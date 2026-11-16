import pandas as pd
import numpy as np

# Load datasets as in 01_generate_eda_visualizations.py
matches = pd.read_csv('data/matches.csv')
comps = pd.read_csv('data/competitions.csv')
m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})

bowl_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')
bowl_raw = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')
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

bowl_raw['wkt_bucket'] = assign_wkt_bucket(bowl_raw)
bowl_raw['cell_id'] = bowl_raw['innings'].astype(str) + '_' + bowl_raw['format'] + '_' + bowl_raw['phase'] + '_' + bowl_raw['wkt_bucket']

bowl_base = pd.read_parquet('outputs/step_7_empirical_calibration/bowling_baseline_36cells.parquet')
bowl_raw = bowl_raw.merge(bowl_base[['cell_id', 'exp_runs_conceded', 'exp_bowler_wicket']], on='cell_id', how='left')

lw = pd.read_parquet('outputs/step_7_empirical_calibration/step_7_2_wicket_valuation/wicket_value_lookup.parquet')
bowl_raw = bowl_raw.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')

is_inn2_non_term = (bowl_raw['innings'] == 2) & (bowl_raw['W_rem'] > 1)
bowl_raw['lambda_eff'] = bowl_raw['lambda_wkt'].copy()
bowl_raw.loc[is_inn2_non_term, 'lambda_eff'] = np.minimum(bowl_raw.loc[is_inn2_non_term, 'lambda_wkt'], bowl_raw.loc[is_inn2_non_term, 'runs_required'])

is_leg = bowl_raw['is_legal_ball'] == True
bowl_raw['v_bowl'] = np.zeros(len(bowl_raw))
bowl_raw.loc[is_leg, 'v_bowl'] = (bowl_raw.loc[is_leg, 'exp_runs_conceded'] - bowl_raw.loc[is_leg, 'bowler_runs_conceded']) + bowl_raw.loc[is_leg, 'lambda_eff'] * (bowl_raw.loc[is_leg, 'is_bowler_wicket'].astype(float) - bowl_raw.loc[is_leg, 'exp_bowler_wicket'])
bowl_raw.loc[~is_leg, 'v_bowl'] = - bowl_raw.loc[~is_leg, 'bowler_runs_conceded'] + bowl_raw.loc[~is_leg, 'lambda_eff'] * bowl_raw.loc[~is_leg, 'is_bowler_wicket'].astype(float)
bowl_raw['w'] = bowl_raw['pressure_bowling'] / 50.0

# 1. Name-based loop
bowl_dual_name = []
for pid in bowl_df['Player']:
    p_df = bowl_raw[bowl_raw['bowler_name'] == pid]
    p_ipl_all = p_df[p_df['format'] == 'IPL']
    p_ipl_leg = p_ipl_all[p_ipl_all['is_legal_ball'] == True]
    p_t20i_all = p_df[p_df['format'] == 'T20I']
    p_t20i_leg = p_t20i_all[p_t20i_all['is_legal_ball'] == True]
    if len(p_ipl_leg) >= 50 and len(p_t20i_leg) >= 50:
        v_ipl = (p_ipl_all['v_bowl'] * p_ipl_all['w']).sum() / p_ipl_leg['w'].sum()
        v_t20i = (p_t20i_all['v_bowl'] * p_t20i_all['w']).sum() / p_t20i_leg['w'].sum()
        bowl_dual_name.append({'name': pid, 'ipl': v_ipl, 't20i': v_t20i, 'rank': bowl_df.loc[bowl_df['Player']==pid, 'Rank'].values[0]})

df_bowl_name = pd.DataFrame(bowl_dual_name)
print("BOWLING NAME-BASED LOOP:")
print(f"N = {len(df_bowl_name)}")
r_bw = df_bowl_name['ipl'].corr(df_bowl_name['t20i'])
spearman_bw = df_bowl_name['ipl'].rank().corr(df_bowl_name['t20i'].rank())
print(f"Pearson r = {r_bw:.6f} (reported as {r_bw:.4f})")
print(f"Spearman rho = {spearman_bw:.6f} (reported as {spearman_bw:.4f})")

# Check if any bowler names map to multiple IDs in bowl_raw
name_to_ids = bowl_raw.groupby('bowler_name')['bowler_id'].nunique()
mult_ids = name_to_ids[name_to_ids > 1]
print("Bowler names with multiple IDs:", mult_ids)
