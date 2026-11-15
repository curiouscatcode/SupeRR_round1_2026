import json
import math
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

# Fit Spec B (M=18) on Innings 1 cohort
inn1_df = df[df['innings'] == 1].copy()
inn1_df['venue_par'] = inn1_df['venue_id'].astype(str).map(vpar_dict).fillna(global_par)
inn1_df['r_par'] = inn1_df['venue_par'] / 20.0
inn1_df['wk_rem'] = 10.0 - inn1_df['W_t']
inn1_df['b_bowled'] = inn1_df['legal_balls_before'] / 120.0
inn1_df['par_to_date'] = inn1_df['venue_par'] * inn1_df['b_bowled']
inn1_df['score_diff_par'] = (inn1_df['score_before'] - inn1_df['par_to_date']) / 30.0
inn1_df['balls_rem'] = (120.0 - inn1_df['legal_balls_before']) / 120.0
inn1_df['res_interaction'] = inn1_df['wk_rem'] * inn1_df['balls_rem']

M = 18.0
crr_shrunk = (inn1_df['score_before'] + M * (inn1_df['r_par'] / 6.0)) / (inn1_df['legal_balls_before'] + M) * 6.0
crr_rel_shrunk = crr_shrunk / inn1_df['r_par']
XB = np.column_stack([np.ones(len(inn1_df)), inn1_df['score_diff_par'], inn1_df['wk_rem'], inn1_df['b_bowled'], inn1_df['res_interaction'], crr_rel_shrunk])
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

outcomes = [
    (0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1), (4, 0, 1), (6, 0, 1), (0, 1, 1), (1, 0, 0), (1, 0, 0)
]

def calc_raw_L_shrunk_inn1(sc, lb, wt, par, phase):
    r_p = par / 20.0
    def wp(s_in, b_in, w_in):
        wk_r = 10.0 - w_in
        bb = b_in / 120.0
        sd = (s_in - par * bb) / 30.0
        c = (s_in + M * (r_p / 6.0)) / (b_in + M) * 6.0
        cr = c / r_p
        br = (120.0 - b_in) / 120.0
        ri = wk_r * br
        raw = np.array([sd, wk_r, bb, ri, cr])
        norm = (raw - mB) / sB
        z = betaB[0] + norm @ betaB[1:]
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

    probs = t_dict[f"{phase}_inn1"]
    wp0 = wp(sc, lb, wt)
    exp_sw = 0.0
    for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
        wp1 = wp(sc + r_add, lb + b_add, wt + w_add)
        exp_sw += p_o * abs(wp1 - wp0)
    return wp0, exp_sw

# Compute raw L for full Innings 1 under Shrunk Model
print("Computing full Innings 1 raw L under Shrunk Model...")
raw_L_shrunk = np.zeros(len(inn1_df))
for i in range(len(inn1_df)):
    row = inn1_df.iloc[i]
    _, l_val = calc_raw_L_shrunk_inn1(row['score_before'], row['legal_balls_before'], row['W_t'], row['venue_par'], row['phase'])
    raw_L_shrunk[i] = l_val
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

def rank_phase(val, ph):
    arr = phase_refs[ph]
    return ((np.searchsorted(arr, val, side='left') + np.searchsorted(arr, val, side='right')) / (2.0 * len(arr))) * 100.0

l_phase_list = []
for i in range(len(inn1_df)):
    l_phase_list.append(rank_phase(raw_L_shrunk[i], inn1_df['phase'].iloc[i]))
inn1_df['L_norm_shrunk_phase'] = np.array(l_phase_list)

# 3. Smoothed Phase Conditional Shrunk ECDF
l_smooth_list = []
for i in range(len(inn1_df)):
    ov = inn1_df['overid'].iloc[i]
    v = raw_L_shrunk[i]
    if ov < 6:
        rk = rank_phase(v, 'PP')
    elif ov == 6:
        rk = 0.75 * rank_phase(v, 'PP') + 0.25 * rank_phase(v, 'Middle')
    elif ov == 7:
        rk = 0.25 * rank_phase(v, 'PP') + 0.75 * rank_phase(v, 'Middle')
    elif 8 <= ov < 15:
        rk = rank_phase(v, 'Middle')
    elif ov == 15:
        rk = 0.75 * rank_phase(v, 'Middle') + 0.25 * rank_phase(v, 'Death')
    elif ov == 16:
        rk = 0.25 * rank_phase(v, 'Middle') + 0.75 * rank_phase(v, 'Death')
    else:
        rk = rank_phase(v, 'Death')
    l_smooth_list.append(rk)
inn1_df['L_norm_shrunk_smooth'] = np.array(l_smooth_list)

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
