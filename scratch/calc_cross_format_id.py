import pandas as pd
import numpy as np

# Load datasets
matches = pd.read_csv('data/matches.csv')
comps = pd.read_csv('data/competitions.csv')
m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})

# Batting
bat_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bat_raw = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bat_raw = bat_raw.merge(m_comp[['match_id', 'format']], on='match_id', how='left')

# Wicket bucket & baseline
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

# 1. Match by striker_id
unique_strikers = bat_faced[['striker_id', 'striker_name']].drop_duplicates()

bat_dual_id = []
for _, row in unique_strikers.iterrows():
    sid = row['striker_id']
    sname = row['striker_name']
    p_df = bat_faced[bat_faced['striker_id'] == sid]
    p_ipl = p_df[p_df['format'] == 'IPL']
    p_t20i = p_df[p_df['format'] == 'T20I']
    if len(p_ipl) >= 50 and len(p_t20i) >= 50:
        v_ipl = (p_ipl['v_bat'] * p_ipl['w']).sum() / p_ipl['w'].sum()
        v_t20i = (p_t20i['v_bat'] * p_t20i['w']).sum() / p_t20i['w'].sum()
        bat_dual_id.append({'id': sid, 'name': sname, 'ipl': v_ipl, 't20i': v_t20i, 'n_ipl': len(p_ipl), 'n_t20i': len(p_t20i)})

df_dual_id = pd.DataFrame(bat_dual_id)
print(f"Batting by ID: N = {len(df_dual_id)}")
r_pearson = df_dual_id['ipl'].corr(df_dual_id['t20i'])
r_spearman = df_dual_id['ipl'].rank().corr(df_dual_id['t20i'].rank())
print(f"Pearson r = {r_pearson:.6f} (rounded 4 dec: {r_pearson:.4f})")
print(f"Spearman rho = {r_spearman:.6f} (rounded 4 dec: {r_spearman:.4f})")

# Check name matching for Abdul Samad
samads = df_dual_id[df_dual_id['name'].str.contains('Abdul Samad', case=False, na=False)]
print("Abdul Samad in dual_id:", samads)

all_samads = bat_faced[bat_faced['striker_name'].str.contains('Abdul Samad', case=False, na=False)][['striker_id', 'striker_name', 'format']].drop_duplicates()
print("All Abdul Samads in bat_faced:\n", all_samads)
for sid in all_samads['striker_id'].unique():
    sub = bat_faced[bat_faced['striker_id'] == sid]
    print(f"Striker {sid} ({sub['striker_name'].iloc[0]}): IPL={len(sub[sub['format']=='IPL'])}, T20I={len(sub[sub['format']=='T20I'])}")
