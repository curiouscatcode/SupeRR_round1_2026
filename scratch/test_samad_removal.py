import pandas as pd
import numpy as np

# Load datasets as in 01_generate_eda_visualizations.py
matches = pd.read_csv('data/matches.csv')
comps = pd.read_csv('data/competitions.csv')
m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})

bat_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bat_raw = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bat_raw = bat_raw.merge(m_comp[['match_id', 'format']], on='match_id', how='left')

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
bat_raw['cell_id'] = bat_raw['innings'].astype(str) + '_' + bat_raw['format'] + '_' + bat_raw['phase'] + '_' + bat_raw['wkt_bucket']

bat_base = pd.read_parquet('outputs/step_7_empirical_calibration/batting_baseline_36cells.parquet')
bat_raw = bat_raw.merge(bat_base[['cell_id', 'exp_runs', 'exp_striker_dismissal']], on='cell_id', how='left')

lw = pd.read_parquet('outputs/step_7_empirical_calibration/step_7_2_wicket_valuation/wicket_value_lookup.parquet')
bat_raw = bat_raw.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')

is_inn2_non_term = (bat_raw['innings'] == 2) & (bat_raw['W_rem'] > 1)
bat_raw['lambda_eff'] = bat_raw['lambda_wkt'].copy()
bat_raw.loc[is_inn2_non_term, 'lambda_eff'] = np.minimum(bat_raw.loc[is_inn2_non_term, 'lambda_wkt'], bat_raw.loc[is_inn2_non_term, 'runs_required'])

bat_faced = bat_raw[bat_raw['is_batter_ball_faced'] == True].copy()
bat_faced['v_bat'] = (bat_faced['batter_runs'] - bat_faced['exp_runs']) - bat_faced['lambda_eff'] * (bat_faced['is_striker_dismissed'].astype(float) - bat_faced['exp_striker_dismissal'])
bat_faced['w'] = bat_faced['pressure_batting'] / 50.0

# Name-based loop as in original script:
bat_dual = []
for pid in bat_df['Player']:
    p_df = bat_faced[bat_faced['striker_name'] == pid]
    p_ipl = p_df[p_df['format'] == 'IPL']
    p_t20i = p_df[p_df['format'] == 'T20I']
    if len(p_ipl) >= 50 and len(p_t20i) >= 50:
        v_ipl = (p_ipl['v_bat'] * p_ipl['w']).sum() / p_ipl['w'].sum()
        v_t20i = (p_t20i['v_bat'] * p_t20i['w']).sum() / p_t20i['w'].sum()
        bat_dual.append({'name': pid, 'ipl': v_ipl, 't20i': v_t20i, 'rank': bat_df.loc[bat_df['Player']==pid, 'Rank'].values[0]})

df_name = pd.DataFrame(bat_dual)
print("ORIGINAL NAME-BASED LOOP:")
print(f"N = {len(df_name)}")
r_orig = df_name['ipl'].corr(df_name['t20i'])
print(f"Pearson r = {r_orig:.6f} (reported as {r_orig:.4f})")
spearman_orig = df_name['ipl'].rank().corr(df_name['t20i'].rank())
print(f"Spearman rho = {spearman_orig:.6f} (reported as {spearman_orig:.4f})")

# Now remove Abdul Samad (the collision)
df_no_samad = df_name[df_name['name'] != 'Abdul Samad']
print("\nAFTER REMOVING THE ABDUL SAMAD NAME COLLISION:")
print(f"N = {len(df_no_samad)}")
r_corr = df_no_samad['ipl'].corr(df_no_samad['t20i'])
spearman_corr = df_no_samad['ipl'].rank().corr(df_no_samad['t20i'].rank())
print(f"Pearson r = {r_corr:.6f} (rounded 4 dec: {r_corr:.4f})")
print(f"Spearman rho = {spearman_corr:.6f} (rounded 4 dec: {spearman_corr:.4f})")
