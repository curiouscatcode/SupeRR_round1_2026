import numpy as np
import pandas as pd

# Let's test predict_wp2 across grids of (runs_required, balls_remaining, wk_rem)
# Using the exact function and normalization from 01_build_wp_framework.py

dms = pd.read_csv('data/processed/delivery_match_state.csv')
tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
df = dms[~tail_mask].copy().reset_index(drop=True)

matches = pd.read_csv('data/matches.csv')
df = df.merge(matches[['match_id', 'win_team_id']], on='match_id', how='left')
df['bat_win'] = (df['batting_team_id'] == df['win_team_id']).astype(float)

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

def predict_wp2(req, rem, wk):
    req = np.maximum(0.0, np.array(req, dtype=float))
    rem = np.maximum(0.0, np.array(rem, dtype=float))
    wk = np.maximum(0.0, np.minimum(10.0, np.array(wk, dtype=float)))

    rc = np.where(rem > 0, (req / np.maximum(1.0, rem)) * 6.0, 36.0)
    rc = np.clip(rc, 0.0, 36.0)
    bn = rem / 120.0
    interaction = rc * (10.0 - wk)

    x_raw = np.column_stack([np.ones(len(req)), rc, wk, bn, interaction])
    x_norm = x_raw.copy()
    x_norm[:, 1:] = (x_raw[:, 1:] - m2) / s2

    logistic_p = 1.0 / (1.0 + np.exp(-np.clip(x_norm @ beta2, -20, 20)))

    wp_final = np.where(req <= 0, 1.0,
               np.where(wk <= 0, 0.0,
               np.where(rem <= 0, 0.0, logistic_p)))
    return wp_final

# Test Monotonicity:
# 1. As runs_required increases (holding balls_rem=30, wk_rem=6 constant):
reqs = [10, 20, 30, 40, 50, 60, 70, 80]
wps_req = predict_wp2(reqs, [30]*len(reqs), [6]*len(reqs))
print("Test 1: WP vs Runs Required (30 balls rem, 6 wkts in hand):")
for r, wp in zip(reqs, wps_req):
    print(f"  Req {r:2d} (RRR {r/5:4.1f}): WP = {wp*100:5.1f}%")

# Check if strictly decreasing:
is_decreasing_r = all(wps_req[i] >= wps_req[i+1] for i in range(len(wps_req)-1))
print(f"  Strictly decreasing with runs required: {is_decreasing_r}")

# 2. As wickets remaining decreases (holding req=40, balls_rem=30 constant):
wks = [9, 8, 7, 6, 5, 4, 3, 2, 1]
wps_wk = predict_wp2([40]*len(wks), [30]*len(wks), wks)
print("\nTest 2: WP vs Wickets Remaining (Req 40 off 30 balls):")
for w, wp in zip(wks, wps_wk):
    print(f"  Wkts in hand {w}: WP = {wp*100:5.1f}%")

is_decreasing_w = all(wps_wk[i] >= wps_wk[i+1] for i in range(len(wps_wk)-1))
print(f"  Strictly decreasing with wickets lost: {is_decreasing_w}")

# 3. Sparse / Extreme States:
print("\nTest 3: Sparse / Boundary States:")
extreme_states = [
    ("Super tense: 2 req off 1 ball, 5 wkts", 2, 1, 5),
    ("Six to win: 6 req off 1 ball, 5 wkts", 6, 1, 5),
    ("Four to win: 4 req off 1 ball, 5 wkts", 4, 1, 5),
    ("Impossible: 30 req off 6 balls, 1 wkt", 30, 6, 1),
    ("Very tough: 15 req off 6 balls, 2 wkts", 15, 6, 2),
    ("Comfortable: 5 req off 12 balls, 8 wkts", 5, 12, 8),
    ("Over 1 Ball 1: 180 req off 120 balls, 10 wkts", 180, 120, 10),
    ("Over 1 Ball 1: 140 req off 120 balls, 10 wkts", 140, 120, 10),
    ("Over 1 Ball 1: 220 req off 120 balls, 10 wkts", 220, 120, 10),
]
for desc, r, b, w in extreme_states:
    wp = predict_wp2([r], [b], [w])[0]
    print(f"  {desc:45s}: WP = {wp*100:5.2f}%")
