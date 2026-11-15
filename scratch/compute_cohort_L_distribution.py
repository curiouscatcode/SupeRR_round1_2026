import sys
import numpy as np
import pandas as pd

# Load cohort deliveries sample to compute empirical distribution of L1 and L2
dms = pd.read_csv('data/processed/delivery_match_state.csv')
tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
dms_clean = dms[~tail_mask].copy()

dls_matches = [20182, 23674, 24822, 28334]
shortened_matches = [15795, 31278, 48514]
exclude_matches = set(dls_matches + shortened_matches)
cohort = dms_clean[~dms_clean['match_id'].isin(exclude_matches)].copy()

# Table 4.1 outcome probabilities with mapped phase strings
P_outcomes = {
    ('PP', 1):     [0.495, 0.262, 0.051, 0.004, 0.118, 0.027, 0.038, 0.030, 0.005],
    ('Middle', 1): [0.352, 0.418, 0.076, 0.006, 0.082, 0.039, 0.046, 0.028, 0.004],
    ('Death', 1):  [0.285, 0.362, 0.098, 0.008, 0.115, 0.082, 0.085, 0.045, 0.006],
    ('PP', 2):     [0.482, 0.271, 0.053, 0.004, 0.121, 0.029, 0.039, 0.032, 0.005],
    ('Middle', 2): [0.348, 0.422, 0.078, 0.006, 0.080, 0.038, 0.048, 0.027, 0.004],
    ('Death', 2):  [0.272, 0.355, 0.102, 0.009, 0.118, 0.088, 0.090, 0.044, 0.006]
}

m2 = np.array([10.64945328, 7.28832399, 0.53806056, 36.14262992])
s2 = np.array([5.64303828, 2.29557336, 0.27565899, 51.96257609])
beta2 = np.array([-0.30921282, -4.11298484, 2.62772346, -1.41554536, 2.77936401])

m1 = np.array([-0.13415434, 7.34230268, 0.49562548, 4.1809563, 0.91562358])
s1 = np.array([0.6484944, 2.15270287, 0.2890039, 3.01059097, 0.28754828])
beta1 = np.array([0.02864037, 0.54254208, 0.4582331, 0.65580652, 0.27098835, 0.01420976])

def wp2(runs_req, balls_rem, wk_lost):
    if balls_rem <= 0:
        return 1.0 if runs_req <= 0 else 0.0
    if runs_req <= 0:
        return 1.0
    if wk_lost >= 10:
        return 0.0
    wk_rem = 10.0 - wk_lost
    rrr = np.clip((runs_req / max(1.0, balls_rem)) * 6.0, 0, 36)
    b_norm = balls_rem / 120.0
    rrr_x_wk = rrr * (10.0 - wk_rem)
    raw = np.array([1.0, rrr, wk_rem, b_norm, rrr_x_wk])
    norm = raw.copy()
    norm[1:] = (raw[1:] - m2) / s2
    z = norm @ beta2
    return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

def wp1(score, legal_balls, wk_lost, par=162.4):
    wk_rem = 10.0 - wk_lost
    b_bowled = legal_balls / 120.0
    par_to_date = par * b_bowled
    score_diff_par = (score - par_to_date) / 30.0
    crr = (score / max(1.0, legal_balls)) * 6.0
    crr_rel_par = crr / (par / 20.0)
    balls_rem = (120.0 - legal_balls) / 120.0
    res_interaction = wk_rem * balls_rem
    raw = np.array([1.0, score_diff_par, wk_rem, b_bowled, res_interaction, crr_rel_par])
    norm = raw.copy()
    norm[1:] = (raw[1:] - m1) / s1
    z = norm @ beta1
    return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

outcomes = [
    (0, 0, 1), # Dot
    (1, 0, 1), # 1
    (2, 0, 1), # 2
    (3, 0, 1), # 3
    (4, 0, 1), # 4
    (6, 0, 1), # 6
    (0, 1, 1), # Wicket
    (1, 0, 0), # Wide
    (1, 0, 0)  # No-ball
]

def calc_L_inn2(runs_req, balls_rem, wk_lost, phase):
    probs = P_outcomes.get((phase, 2), P_outcomes[('Middle', 2)])
    wp_curr = wp2(runs_req, balls_rem, wk_lost)
    exp_swing = 0.0
    for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
        wp_next = wp2(runs_req - r_add, balls_rem - b_add, wk_lost + w_add)
        exp_swing += p_o * abs(wp_next - wp_curr)
    return wp_curr, exp_swing

def calc_L_inn1(score, legal_balls, wk_lost, par, phase):
    probs = P_outcomes.get((phase, 1), P_outcomes[('Middle', 1)])
    wp_curr = wp1(score, legal_balls, wk_lost, par)
    exp_swing = 0.0
    for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
        wp_next = wp1(score + r_add, legal_balls + b_add, wk_lost + w_add, par)
        exp_swing += p_o * abs(wp_next - wp_curr)
    return wp_curr, exp_swing

sample_inn1 = cohort[cohort['innings'] == 1].sample(5000, random_state=42)
sample_inn2 = cohort[cohort['innings'] == 2].sample(5000, random_state=42)

l1_vals = [calc_L_inn1(r['score_before'], r['legal_balls_before'], r['wickets_before'], 162.4, r['phase'])[1] for _, r in sample_inn1.iterrows()]
l2_vals = [calc_L_inn2(r['runs_required'], r['balls_remaining'], r['wickets_before'], r['phase'])[1] for _, r in sample_inn2.iterrows()]

l1_arr = np.array(l1_vals)
l2_arr = np.array(l2_vals)

print("--- INNINGS 1 RAW L DISTRIBUTION (5,000 deliveries) ---")
print(f"Mean:   {np.mean(l1_arr):.5f}")
print(f"Std:    {np.std(l1_arr):.5f}")
print(f"p1:     {np.percentile(l1_arr, 1):.5f}")
print(f"p5:     {np.percentile(l1_arr, 5):.5f}")
print(f"p50:    {np.percentile(l1_arr, 50):.5f}")
print(f"p95:    {np.percentile(l1_arr, 95):.5f}")
print(f"p99:    {np.percentile(l1_arr, 99):.5f}")
print(f"p99.5:  {np.percentile(l1_arr, 99.5):.5f}")

print("\n--- INNINGS 2 RAW L DISTRIBUTION (5,000 deliveries) ---")
print(f"Mean:   {np.mean(l2_arr):.5f}")
print(f"Std:    {np.std(l2_arr):.5f}")
print(f"p1:     {np.percentile(l2_arr, 1):.5f}")
print(f"p5:     {np.percentile(l2_arr, 5):.5f}")
print(f"p50:    {np.percentile(l2_arr, 50):.5f}")
print(f"p95:    {np.percentile(l2_arr, 95):.5f}")
print(f"p99:    {np.percentile(l2_arr, 99):.5f}")
print(f"p99.5:  {np.percentile(l2_arr, 99.5):.5f}")

# Now let's normalize the 10 scenarios!
l1_min = np.percentile(l1_arr, 1)
l1_max = np.percentile(l1_arr, 99.5)
l2_min = np.percentile(l2_arr, 1)
l2_max = np.percentile(l2_arr, 99.5)

print(f"\nNormalization bounds: L1 in [{l1_min:.5f}, {l1_max:.5f}], L2 in [{l2_min:.5f}, {l2_max:.5f}]")
