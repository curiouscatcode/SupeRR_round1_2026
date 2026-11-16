import os
import numpy as np
import pandas as pd

def precompute():
    print("[Precomputing Dashboard Metrics]...")
    os.makedirs('outputs/step_10_methodology_report', exist_ok=True)
    
    # 1. Load delivery datasets
    bat_raw = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
    bowl_raw = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

    matches = pd.read_csv('data/matches.csv')
    comps = pd.read_csv('data/competitions.csv')
    m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
    m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})

    bat_raw = bat_raw.merge(m_comp[['match_id', 'format']], on='match_id', how='left')
    bowl_raw = bowl_raw.merge(m_comp[['match_id', 'format']], on='match_id', how='left')

    def assign_wkt_bucket(df):
        w = df['W_t']
        ph = df['phase']
        bucket = pd.Series(index=df.index, dtype='object')
        bucket[(ph == 'PP') & (w == 0)] = '0'
        bucket[(ph == 'PP') & (w == 1)] = '1'
        bucket[(ph == 'PP') & (w >= 2)] = '2+'
        bucket[(ph == 'Middle') & (w <= 2)] = '0-2'
        bucket[(ph == 'Middle') & (w >= 3) & (w <= 4)] = '3-4'
        bucket[(ph == 'Middle') & (w >= 5)] = '5+'
        bucket[(ph == 'Death') & (w <= 3)] = '0-3'
        bucket[(ph == 'Death') & (w >= 4) & (w <= 6)] = '4-6'
        bucket[(ph == 'Death') & (w >= 7)] = '7+'
        return bucket

    bat_raw['wkt_bucket'] = assign_wkt_bucket(bat_raw)
    bowl_raw['wkt_bucket'] = assign_wkt_bucket(bowl_raw)
    bat_raw['cell_id'] = bat_raw['innings'].astype(str) + '_' + bat_raw['format'] + '_' + bat_raw['phase'] + '_' + bat_raw['wkt_bucket']
    bowl_raw['cell_id'] = bowl_raw['innings'].astype(str) + '_' + bowl_raw['format'] + '_' + bowl_raw['phase'] + '_' + bowl_raw['wkt_bucket']

    bat_base = pd.read_parquet('outputs/step_7_empirical_calibration/batting_baseline_36cells.parquet')
    bowl_base = pd.read_parquet('outputs/step_7_empirical_calibration/bowling_baseline_36cells.parquet')
    bat_raw = bat_raw.merge(bat_base[['cell_id', 'exp_runs', 'exp_striker_dismissal']], on='cell_id', how='left')
    bowl_raw = bowl_raw.merge(bowl_base[['cell_id', 'exp_runs_conceded', 'exp_bowler_wicket']], on='cell_id', how='left')

    lw = pd.read_parquet('outputs/step_7_empirical_calibration/step_7_2_wicket_valuation/wicket_value_lookup.parquet')
    bat_raw = bat_raw.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')
    bowl_raw = bowl_raw.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')

    for df in [bat_raw, bowl_raw]:
        is_inn2_non_term = (df['innings'] == 2) & (df['W_rem'] > 1)
        df['lambda_eff'] = df['lambda_wkt'].copy()
        df.loc[is_inn2_non_term, 'lambda_eff'] = np.minimum(df.loc[is_inn2_non_term, 'lambda_wkt'], df.loc[is_inn2_non_term, 'runs_required'])

    bat_faced = bat_raw[bat_raw['is_batter_ball_faced'] == True].copy()
    bat_faced['v_bat'] = (bat_faced['batter_runs'] - bat_faced['exp_runs']) - bat_faced['lambda_eff'] * (bat_faced['is_striker_dismissed'].astype(float) - bat_faced['exp_striker_dismissal'])

    is_leg = bowl_raw['is_legal_ball'] == True
    bowl_raw['v_bowl'] = np.zeros(len(bowl_raw))
    bowl_raw.loc[is_leg, 'v_bowl'] = (bowl_raw.loc[is_leg, 'exp_runs_conceded'] - bowl_raw.loc[is_leg, 'bowler_runs_conceded']) + bowl_raw.loc[is_leg, 'lambda_eff'] * (bowl_raw.loc[is_leg, 'is_bowler_wicket'].astype(float) - bowl_raw.loc[is_leg, 'exp_bowler_wicket'])
    bowl_raw.loc[~is_leg, 'v_bowl'] = - bowl_raw.loc[~is_leg, 'bowler_runs_conceded'] + bowl_raw.loc[~is_leg, 'lambda_eff'] * bowl_raw.loc[~is_leg, 'is_bowler_wicket'].astype(float)

    # 2. Load qualified player leaderboards
    bat_all = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
    bowl_all = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

    print(f"Aggregating {len(bat_all)} qualified batters...")
    bat_records = []
    for _, r in bat_all.iterrows():
        p_name = r['Player']
        sub = bat_faced[bat_faced['striker_name'] == p_name]
        p_id = sub['striker_id'].iloc[0] if len(sub) > 0 else None
            
        n_total = len(sub)
        sub_hi = sub[sub['pressure_batting'] >= 50]
        sub_lo = sub[sub['pressure_batting'] < 50]
        
        sva_hi = float(sub_hi['v_bat'].mean()) if len(sub_hi) > 0 else 0.0
        sva_lo = float(sub_lo['v_bat'].mean()) if len(sub_lo) > 0 else 0.0
        lift = sva_hi - sva_lo
        
        # Phases
        sva_pp = float(sub[sub['phase'] == 'PP']['v_bat'].mean()) if len(sub[sub['phase'] == 'PP']) > 0 else 0.0
        sva_mid = float(sub[sub['phase'] == 'Middle']['v_bat'].mean()) if len(sub[sub['phase'] == 'Middle']) > 0 else 0.0
        sva_death = float(sub[sub['phase'] == 'Death']['v_bat'].mean()) if len(sub[sub['phase'] == 'Death']) > 0 else 0.0
        
        # Formats
        sva_ipl = float(sub[sub['format'] == 'IPL']['v_bat'].mean()) if len(sub[sub['format'] == 'IPL']) > 0 else 0.0
        sva_t20i = float(sub[sub['format'] == 'T20I']['v_bat'].mean()) if len(sub[sub['format'] == 'T20I']) > 0 else 0.0
        
        # Pressure bands count
        n_low = int((sub['pressure_batting'] < 30).sum())
        n_mid = int(((sub['pressure_batting'] >= 30) & (sub['pressure_batting'] < 50)).sum())
        n_high = int(((sub['pressure_batting'] >= 50) & (sub['pressure_batting'] < 75)).sum())
        n_climax = int((sub['pressure_batting'] >= 75).sum())

        rec = {
            'Discipline': 'Batting',
            'Rank': int(r['Rank']),
            'Player': p_name,
            'Player ID': p_id,
            'Team/format': r['Team/format'],
            'Shrunk score': float(r['Shrunk score']),
            'Raw score': float(r['Raw score']),
            'Raw opportunities': int(r['Raw opportunities']),
            'Kish ESS': float(r['Kish ESS']),
            '95% CI': str(r['95% CI']),
            'SVA_P_ge_50': sva_hi,
            'SVA_P_lt_50': sva_lo,
            'Pressure_Lift': lift,
            'N_Pressure_ge_50': len(sub_hi),
            'N_Pressure_lt_50': len(sub_lo),
            'SVA_PP': sva_pp,
            'SVA_Middle': sva_mid,
            'SVA_Death': sva_death,
            'SVA_IPL': sva_ipl,
            'SVA_T20I': sva_t20i,
            'N_Low': n_low,
            'N_Mid': n_mid,
            'N_High': n_high,
            'N_Climax': n_climax,
        }
        bat_records.append(rec)

    print(f"Aggregating {len(bowl_all)} qualified bowlers...")
    bowl_records = []
    for _, r in bowl_all.iterrows():
        p_name = r['Player']
        sub = bowl_raw[bowl_raw['bowler_name'] == p_name]
        p_id = sub['bowler_id'].iloc[0] if len(sub) > 0 else None
            
        n_total = len(sub)
        sub_hi = sub[sub['pressure_bowling'] >= 50]
        sub_lo = sub[sub['pressure_bowling'] < 50]
        
        sva_hi = float(sub_hi['v_bowl'].mean()) if len(sub_hi) > 0 else 0.0
        sva_lo = float(sub_lo['v_bowl'].mean()) if len(sub_lo) > 0 else 0.0
        lift = sva_hi - sva_lo
        
        # Phases
        sva_pp = float(sub[sub['phase'] == 'PP']['v_bowl'].mean()) if len(sub[sub['phase'] == 'PP']) > 0 else 0.0
        sva_mid = float(sub[sub['phase'] == 'Middle']['v_bowl'].mean()) if len(sub[sub['phase'] == 'Middle']) > 0 else 0.0
        sva_death = float(sub[sub['phase'] == 'Death']['v_bowl'].mean()) if len(sub[sub['phase'] == 'Death']) > 0 else 0.0
        
        # Formats
        sva_ipl = float(sub[sub['format'] == 'IPL']['v_bowl'].mean()) if len(sub[sub['format'] == 'IPL']) > 0 else 0.0
        sva_t20i = float(sub[sub['format'] == 'T20I']['v_bowl'].mean()) if len(sub[sub['format'] == 'T20I']) > 0 else 0.0
        
        # Pressure bands count
        n_low = int((sub['pressure_bowling'] < 30).sum())
        n_mid = int(((sub['pressure_bowling'] >= 30) & (sub['pressure_bowling'] < 50)).sum())
        n_high = int(((sub['pressure_bowling'] >= 50) & (sub['pressure_bowling'] < 75)).sum())
        n_climax = int((sub['pressure_bowling'] >= 75).sum())

        rec = {
            'Discipline': 'Bowling',
            'Rank': int(r['Rank']),
            'Player': p_name,
            'Player ID': p_id,
            'Team/format': r['Team/format'],
            'Shrunk score': float(r['Shrunk score']),
            'Raw score': float(r['Raw score']),
            'Raw opportunities': int(r['Raw opportunities']),
            'Kish ESS': float(r['Kish ESS']),
            '95% CI': str(r['95% CI']),
            'SVA_P_ge_50': sva_hi,
            'SVA_P_lt_50': sva_lo,
            'Pressure_Lift': lift,
            'N_Pressure_ge_50': len(sub_hi),
            'N_Pressure_lt_50': len(sub_lo),
            'SVA_PP': sva_pp,
            'SVA_Middle': sva_mid,
            'SVA_Death': sva_death,
            'SVA_IPL': sva_ipl,
            'SVA_T20I': sva_t20i,
            'N_Low': n_low,
            'N_Mid': n_mid,
            'N_High': n_high,
            'N_Climax': n_climax,
        }
        bowl_records.append(rec)

    df_bat_out = pd.DataFrame(bat_records)
    df_bowl_out = pd.DataFrame(bowl_records)
    
    df_bat_out.to_csv('outputs/step_10_methodology_report/dashboard_batting_metrics.csv', index=False)
    df_bowl_out.to_csv('outputs/step_10_methodology_report/dashboard_bowling_metrics.csv', index=False)
    
    print(f"Successfully saved {len(df_bat_out)} batting and {len(df_bowl_out)} bowling dashboard metrics.")

if __name__ == '__main__':
    precompute()
