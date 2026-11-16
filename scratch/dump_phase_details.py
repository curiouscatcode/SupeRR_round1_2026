import pandas as pd
import numpy as np

# Load datasets as in 01_generate_eda_visualizations.py
matches = pd.read_csv('data/matches.csv')
comps = pd.read_csv('data/competitions.csv')
m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})

bat_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bowl_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

bat_raw = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bowl_raw = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

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
bat_faced['w'] = bat_faced['pressure_batting'] / 50.0

is_leg = bowl_raw['is_legal_ball'] == True
bowl_raw['v_bowl'] = np.zeros(len(bowl_raw))
bowl_raw.loc[is_leg, 'v_bowl'] = (bowl_raw.loc[is_leg, 'exp_runs_conceded'] - bowl_raw.loc[is_leg, 'bowler_runs_conceded']) + bowl_raw.loc[is_leg, 'lambda_eff'] * (bowl_raw.loc[is_leg, 'is_bowler_wicket'].astype(float) - bowl_raw.loc[is_leg, 'exp_bowler_wicket'])
bowl_raw.loc[~is_leg, 'v_bowl'] = - bowl_raw.loc[~is_leg, 'bowler_runs_conceded'] + bowl_raw.loc[~is_leg, 'lambda_eff'] * bowl_raw.loc[~is_leg, 'is_bowler_wicket'].astype(float)
bowl_raw['w'] = bowl_raw['pressure_bowling'] / 50.0

phases = ['PP', 'Middle', 'Death']

print("=== TOP 10 BATTING PHASE DETAILS ===")
for name in bat_df.head(10)['Player']:
    p_df = bat_faced[bat_faced['striker_name'] == name]
    print(f"\n{name}:")
    for ph in phases:
        sub = p_df[p_df['phase'] == ph]
        n_b = len(sub)
        if n_b >= 20:
            val = float((sub['v_bat'] * sub['w']).sum() / sub['w'].sum())
            print(f"  {ph:6s}: val={val:+.4f} ({val:+.2f}), n={n_b} balls")
        else:
            print(f"  {ph:6s}: val=N/A, n={n_b} balls (BELOW 20)")

print("\n=== TOP 10 BOWLING PHASE DETAILS ===")
for name in bowl_df.head(10)['Player']:
    p_df = bowl_raw[bowl_raw['bowler_name'] == name]
    print(f"\n{name}:")
    for ph in phases:
        sub_leg = p_df[(p_df['phase'] == ph) & (p_df['is_legal_ball'] == True)]
        sub_all = p_df[p_df['phase'] == ph]
        n_leg = len(sub_leg)
        if n_leg >= 20:
            val = float((sub_all['v_bowl'] * sub_all['w']).sum() / sub_leg['w'].sum())
            print(f"  {ph:6s}: val={val:+.4f} ({val:+.2f}), n={n_leg} balls")
        else:
            print(f"  {ph:6s}: val=N/A, n={n_leg} balls (BELOW 20)")
