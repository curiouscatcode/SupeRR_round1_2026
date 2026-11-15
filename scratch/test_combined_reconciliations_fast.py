import json
import numpy as np
import pandas as pd

# Load cohort parquet
df = pd.read_parquet('outputs/step_4_pressure_pipeline/deliveries_with_task_difficulty.parquet')
final_df = pd.read_parquet('outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet')
df['pressure_batting'] = final_df['pressure_batting']
df['pressure_bowling'] = final_df['pressure_bowling']

with open('outputs/step_4_pressure_pipeline/empirical_venue_par.json') as f:
    vpar_dict = json.load(f)
global_par = vpar_dict.get('GLOBAL_DEFAULT', 176.68)

with open('outputs/step_4_pressure_pipeline/outcome_transition_probabilities.json') as f:
    t_dict = json.load(f)

inn1_df = df[df['innings'] == 1].copy()
vpar1 = inn1_df['venue_id'].astype(str).map(vpar_dict).fillna(global_par).values
rpar1 = vpar1 / 20.0
score1 = inn1_df['score_before'].values
lballs1 = inn1_df['legal_balls_before'].values
wt1 = inn1_df['W_t'].values
wk_rem1 = 10.0 - wt1
bbowled1 = lballs1 / 120.0
par_to_date1 = vpar1 * bbowled1
score_diff_par1 = (score1 - par_to_date1) / 30.0
balls_rem1 = (120.0 - lballs1) / 120.0
res_inter1 = wk_rem1 * balls_rem1

M = 18.0
crr_shrunk1 = (score1 + M * (rpar1 / 6.0)) / (lballs1 + M) * 6.0
crr_rel_shrunk1 = crr_shrunk1 / rpar1
XB = np.column_stack([np.ones(len(inn1_df)), score_diff_par1, wk_rem1, bbowled1, res_inter1, crr_rel_shrunk1])
y1 = inn1_df['bat_win'].values

mB = XB[:, 1:].mean(axis=0)
sB = XB[:, 1:].std(axis=0)
XB_norm = XB.copy()
XB_norm[:, 1:] = (XB[:, 1:] - mB) / sB
betaB = np.zeros(XB.shape[1])
for _ in range(25):
    p = 1.0 / (1.0 + np.exp(-np.clip(XB_norm @ betaB, -20, 20)))
    grad = XB_norm.T @ (p - y1)
    W = p * (1.0 - p)
    H = (XB_norm.T * W) @ XB_norm + 1e-4 * np.eye(XB.shape[1])
    step = np.linalg.solve(H, grad)
    betaB -= step
    if np.max(np.abs(step)) < 1e-6:
        break

print("Model converged.")

# Pre-delivery WP under Shrunk Model
z1 = XB_norm @ betaB
wp_curr1 = 1.0 / (1.0 + np.exp(-np.clip(z1, -20, 20)))

outcomes = [
    (0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1), (4, 0, 1), (6, 0, 1), (0, 1, 1), (1, 0, 0), (1, 0, 0)
]

# Vectorized computation of expected swing stratum by stratum
raw_L_shrunk = np.zeros(len(inn1_df), dtype=float)
phases = inn1_df['phase'].values

for ph in ['PP', 'Middle', 'Death']:
    ph_mask = (phases == ph)
    if not np.any(ph_mask):
        continue
    probs = t_dict[f"{ph}_inn1"]
    indices = np.where(ph_mask)[0]
    
    sc_sub = score1[indices]
    lb_sub = lballs1[indices]
    wt_sub = wt1[indices]
    vp_sub = vpar1[indices]
    rp_sub = rpar1[indices]
    curr_wp_sub = wp_curr1[indices]
    
    cum_swing = np.zeros(len(indices), dtype=float)
    
    for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
        next_sc = sc_sub + r_add
        next_lb = lb_sub + b_add
        next_wt = wt_sub + w_add
        
        next_wkr = 10.0 - next_wt
        next_bb = next_lb / 120.0
        next_sd = (next_sc - vp_sub * next_bb) / 30.0
        next_br = (120.0 - next_lb) / 120.0
        next_ri = next_wkr * next_br
        next_c = (next_sc + M * (rp_sub / 6.0)) / (next_lb + M) * 6.0
        next_cr = next_c / rp_sub
        
        # Normalize
        norm_sd = (next_sd - mB[0]) / sB[0]
        norm_wkr = (next_wkr - mB[1]) / sB[1]
        norm_bb = (next_bb - mB[2]) / sB[2]
        norm_ri = (next_ri - mB[3]) / sB[3]
        norm_cr = (next_cr - mB[4]) / sB[4]
        
        z_next = betaB[0] + norm_sd * betaB[1] + norm_wkr * betaB[2] + norm_bb * betaB[3] + norm_ri * betaB[4] + norm_cr * betaB[5]
        wp_next = 1.0 / (1.0 + np.exp(-np.clip(z_next, -20, 20)))
        cum_swing += p_o * np.abs(wp_next - curr_wp_sub)
        
    raw_L_shrunk[indices] = cum_swing

print("Vectorized consequence complete.")
inn1_df['raw_L_shrunk'] = raw_L_shrunk

# Compute ECDFs:
# 1. Whole Innings Shrunk ECDF
sorted_whole = np.sort(raw_L_shrunk)
nw = len(sorted_whole)
inn1_df['L_norm_shrunk_whole'] = ((np.searchsorted(sorted_whole, raw_L_shrunk, side='left') + np.searchsorted(sorted_whole, raw_L_shrunk, side='right')) / (2.0 * nw)) * 100.0

# 2. Phase Conditional Shrunk ECDF
phase_refs = {}
for ph in ['PP', 'Middle', 'Death']:
    phase_refs[ph] = np.sort(inn1_df[inn1_df['phase'] == ph]['raw_L_shrunk'].values)

def rank_phase(vals, ph):
    arr = phase_refs[ph]
    n = len(arr)
    rl = np.searchsorted(arr, vals, side='left')
    rr = np.searchsorted(arr, vals, side='right')
    return ((rl + rr) / (2.0 * n)) * 100.0

l_phase_arr = np.zeros(len(inn1_df), dtype=float)
for ph in ['PP', 'Middle', 'Death']:
    mask = (phases == ph)
    l_phase_arr[mask] = rank_phase(raw_L_shrunk[mask], ph)
inn1_df['L_norm_shrunk_phase'] = l_phase_arr

# 3. Smoothed Phase Conditional Shrunk ECDF
# Precalculate rank of each element in each phase ref
rk_pp = rank_phase(raw_L_shrunk, 'PP')
rk_mid = rank_phase(raw_L_shrunk, 'Middle')
rk_death = rank_phase(raw_L_shrunk, 'Death')

overs = inn1_df['overid'].values
l_smooth_arr = np.zeros(len(inn1_df), dtype=float)

for i in range(len(inn1_df)):
    ov = overs[i]
    if ov < 6:
        l_smooth_arr[i] = rk_pp[i]
    elif ov == 6:
        l_smooth_arr[i] = 0.75 * rk_pp[i] + 0.25 * rk_mid[i]
    elif ov == 7:
        l_smooth_arr[i] = 0.25 * rk_pp[i] + 0.75 * rk_mid[i]
    elif 8 <= ov < 15:
        l_smooth_arr[i] = rk_mid[i]
    elif ov == 15:
        l_smooth_arr[i] = 0.75 * rk_mid[i] + 0.25 * rk_death[i]
    elif ov == 16:
        l_smooth_arr[i] = 0.25 * rk_mid[i] + 0.75 * rk_death[i]
    else:
        l_smooth_arr[i] = rk_death[i]

inn1_df['L_norm_shrunk_smooth'] = l_smooth_arr

print("\n--- INNINGS 1 PHASE COMPARISON UNDER SHRUNK MODEL (M=18) ---")
for ph in ['PP', 'Middle', 'Death']:
    sub = inn1_df[inn1_df['phase'] == ph]
    t_m = sub['task_difficulty_bat'].mean()
    l_whole = sub['L_norm_shrunk_whole'].mean()
    p_whole = np.sqrt(sub['task_difficulty_bat'] * sub['L_norm_shrunk_whole']).mean()
    l_phase = sub['L_norm_shrunk_phase'].mean()
    p_phase = np.sqrt(sub['task_difficulty_bat'] * sub['L_norm_shrunk_phase']).mean()
    l_smooth = sub['L_norm_shrunk_smooth'].mean()
    p_smooth = np.sqrt(sub['task_difficulty_bat'] * sub['L_norm_shrunk_smooth']).mean()
    print(f"Phase {ph:7s} (T_bat Mean={t_m:.1f}):")
    print(f"  Whole ECDF:    Mean L_norm={l_whole:5.2f} -> Mean P_bat={p_whole:5.2f}")
    print(f"  Phase ECDF:    Mean L_norm={l_phase:5.2f} -> Mean P_bat={p_phase:5.2f}")
    print(f"  Smooth Phase:  Mean L_norm={l_smooth:5.2f} -> Mean P_bat={p_smooth:5.2f}")

# Check ball 0.1 specifically
b0 = inn1_df[(inn1_df['legal_balls_before'] == 0) & (inn1_df['score_before'] == 0)].iloc[0]
print("\n--- BALL 0.1 VALUES ---")
print(f"Raw L (Baseline M=0):       {b0['raw_consequence_L']:.5f} -> Whole ECDF = {b0['normalized_consequence_L']:.2f} -> P_bat = {b0['pressure_batting']:.2f}")
print(f"Raw L (Shrunk M=18):         {b0['raw_L_shrunk']:.5f}")
print(f"  Under Whole ECDF:         L_norm = {b0['L_norm_shrunk_whole']:.2f} -> P_bat = {np.sqrt(50.0 * b0['L_norm_shrunk_whole']):.2f}")
print(f"  Under Phase ECDF:         L_norm = {b0['L_norm_shrunk_phase']:.2f} -> P_bat = {np.sqrt(50.0 * b0['L_norm_shrunk_phase']):.2f}")
print(f"  Under Smooth Phase ECDF:   L_norm = {b0['L_norm_shrunk_smooth']:.2f} -> P_bat = {np.sqrt(50.0 * b0['L_norm_shrunk_smooth']):.2f}")
