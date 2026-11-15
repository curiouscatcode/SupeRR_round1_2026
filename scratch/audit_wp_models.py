import numpy as np
import pandas as pd

# Load and prepare data as in 01_build_wp_framework.py
dms = pd.read_csv('data/processed/delivery_match_state.csv')
tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
df = dms[~tail_mask].copy().reset_index(drop=True)

matches = pd.read_csv('data/matches.csv')
match_cols = ['match_id', 'venue_id', 'win_team_id', 'home_team_id', 'away_team_id', 'toss_win_team_id', 'toss_opted']
df = df.merge(matches[match_cols], on='match_id', how='left')
df['bat_win'] = (df['batting_team_id'] == df['win_team_id']).astype(float)

# INNINGS 2
inn2 = df[df['innings'] == 2].copy()
inn2['wk_rem'] = 10.0 - inn2['wickets_before']
inn2['rrr'] = ((inn2['runs_required'] / np.maximum(1.0, inn2['balls_remaining'])) * 6.0).clip(0, 36)
inn2['b_norm'] = inn2['balls_remaining'] / 120.0
inn2['rrr_x_wk'] = inn2['rrr'] * (10.0 - inn2['wk_rem'])

X2_raw = np.column_stack([
    np.ones(len(inn2)),
    inn2['rrr'].values,
    inn2['wk_rem'].values,
    inn2['b_norm'].values,
    inn2['rrr_x_wk'].values
])
y2 = inn2['bat_win'].values
m2 = X2_raw[:, 1:].mean(axis=0)
s2 = X2_raw[:, 1:].std(axis=0)
X2_norm = X2_raw.copy()
X2_norm[:, 1:] = (X2_raw[:, 1:] - m2) / s2

beta2 = np.zeros(X2_raw.shape[1])
for _ in range(15):
    p = 1.0 / (1.0 + np.exp(-np.clip(X2_norm @ beta2, -20, 20)))
    grad = X2_norm.T @ (p - y2)
    W = p * (1.0 - p)
    H = (X2_norm.T * W) @ X2_norm + 1e-4 * np.eye(X2_raw.shape[1])
    step = np.linalg.solve(H, grad)
    beta2 -= step
    if np.max(np.abs(step)) < 1e-5: break

print("--- INNINGS 2 MODEL COEFFICIENTS (Normalized Features) ---")
feat2_names = ['Intercept', 'RRR', 'Wickets Remaining', 'Balls Remaining (Norm)', 'RRR x Wickets Lost']
for name, b in zip(feat2_names, beta2):
    print(f"  {name:25s}: {b:+.4f}")

# INNINGS 1
inn1 = df[df['innings'] == 1].copy()
last_balls = inn1.groupby('match_id').last()[['score_before', 'team_runs_added', 'venue_id']].reset_index()
last_balls['first_inn_total'] = last_balls['score_before'] + last_balls['team_runs_added']
global_first_inn_mean = last_balls['first_inn_total'].mean()

v_agg = last_balls.groupby('venue_id')['first_inn_total'].agg(['count', 'mean']).reset_index()
K_shrink = 8.0
v_agg['venue_par'] = (v_agg['count'] * v_agg['mean'] + K_shrink * global_first_inn_mean) / (v_agg['count'] + K_shrink)
venue_par_dict = dict(zip(v_agg['venue_id'], v_agg['venue_par']))

inn1['venue_par'] = inn1['venue_id'].map(venue_par_dict).fillna(global_first_inn_mean)
inn1['wk_rem'] = 10.0 - inn1['wickets_before']
inn1['b_bowled'] = inn1['legal_balls_before'] / 120.0
inn1['par_to_date'] = inn1['venue_par'] * inn1['b_bowled']
inn1['score_diff_par'] = (inn1['score_before'] - inn1['par_to_date']) / 30.0
inn1['crr_rel_par'] = inn1['current_run_rate'] / (inn1['venue_par'] / 20.0)
inn1['balls_rem'] = (120.0 - inn1['legal_balls_before']) / 120.0
inn1['res_interaction'] = inn1['wk_rem'] * inn1['balls_rem']

X1_raw = np.column_stack([
    np.ones(len(inn1)),
    inn1['score_diff_par'].values,
    inn1['wk_rem'].values,
    inn1['b_bowled'].values,
    inn1['res_interaction'].values,
    inn1['crr_rel_par'].values
])
y1 = inn1['bat_win'].values
m1 = X1_raw[:, 1:].mean(axis=0)
s1 = X1_raw[:, 1:].std(axis=0)
X1_norm = X1_raw.copy()
X1_norm[:, 1:] = (X1_raw[:, 1:] - m1) / s1

beta1 = np.zeros(X1_raw.shape[1])
for _ in range(15):
    p = 1.0 / (1.0 + np.exp(-np.clip(X1_norm @ beta1, -20, 20)))
    grad = X1_norm.T @ (p - y1)
    W = p * (1.0 - p)
    H = (X1_norm.T * W) @ X1_norm + 1e-4 * np.eye(X1_raw.shape[1])
    step = np.linalg.solve(H, grad)
    beta1 -= step
    if np.max(np.abs(step)) < 1e-5: break

print("\n--- INNINGS 1 MODEL COEFFICIENTS (Normalized Features) ---")
feat1_names = ['Intercept', 'Score Diff from Par', 'Wickets Remaining', 'Balls Bowled (Norm)', 'Resource Interaction', 'CRR Relative to Par']
for name, b in zip(feat1_names, beta1):
    print(f"  {name:25s}: {b:+.4f}")
