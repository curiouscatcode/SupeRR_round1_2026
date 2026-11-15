import sys
sys.path.append('.')
import json
import math
import numpy as np
import pandas as pd

# Load empirical tables
with open('outputs/step_4_pressure_pipeline/empirical_venue_par.json') as f:
    vpar_dict = json.load(f)
global_par = vpar_dict.get('GLOBAL_DEFAULT', 176.68)

wkt_curve = pd.read_csv('outputs/step_4_pressure_pipeline/empirical_wicket_curve.csv')
mu_w_map = dict(zip(wkt_curve['legal_balls_before'], wkt_curve['mean']))
sig_w_map = dict(zip(wkt_curve['legal_balls_before'], wkt_curve['regularized_std']))

with open('outputs/step_4_pressure_pipeline/outcome_transition_probabilities.json') as f:
    t_dict = json.load(f)

# Load WP models
with open('outputs/step_4_pressure_pipeline/wp_model_inn1.json') as f:
    d1 = json.load(f)
m1_base = np.array(d1['means'])
s1_base = np.array(d1['stds'])
beta1_base = np.array(d1['coefficients'])

with open('outputs/step_4_pressure_pipeline/wp_model_inn2.json') as f:
    d2 = json.load(f)
m2 = np.array(d2['means'])
s2 = np.array(d2['stds'])
beta2 = np.array(d2['coefficients'])

# Load clean parquet for reference distributions
df_conseq = pd.read_parquet('outputs/step_4_pressure_pipeline/deliveries_with_consequence.parquet')
inn1_conseq = df_conseq[df_conseq['innings'] == 1]
inn2_conseq = df_conseq[df_conseq['innings'] == 2]

# Baseline Whole ECDFs
base_inn1_sorted = np.sort(inn1_conseq['raw_consequence_L'].values)
base_inn2_sorted = np.sort(inn2_conseq['raw_consequence_L'].values)

# Shrunk Model (M=18) reference distributions
import importlib
mod_fast = importlib.import_module('scratch.test_combined_reconciliations_fast')
shrunk_inn1_whole = np.sort(mod_fast.inn1_df['raw_L_shrunk'].values)
shrunk_inn1_pp = np.sort(mod_fast.inn1_df[mod_fast.inn1_df['phase'] == 'PP']['raw_L_shrunk'].values)
shrunk_inn1_mid = np.sort(mod_fast.inn1_df[mod_fast.inn1_df['phase'] == 'Middle']['raw_L_shrunk'].values)
shrunk_inn1_death = np.sort(mod_fast.inn1_df[mod_fast.inn1_df['phase'] == 'Death']['raw_L_shrunk'].values)

# Beta & scalers for Shrunk Model
m1_shrunk = mod_fast.mB
s1_shrunk = mod_fast.sB
beta1_shrunk = mod_fast.betaB

outcomes = [
    (0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1), (4, 0, 1), (6, 0, 1), (0, 1, 1), (1, 0, 0), (1, 0, 0)
]

def rank_ecdf(arr, val):
    rl = np.searchsorted(arr, val, side='left')
    rr = np.searchsorted(arr, val, side='right')
    return ((rl + rr) / (2.0 * len(arr))) * 100.0

def calc_wp2(req, brem, wt, phase='Death'):
    if req <= 0: return 1.0
    if wt >= 10: return 0.0
    if brem <= 0: return 0.50 if req == 1 else 0.0
    if brem == 1:
        # Markov
        probs = t_dict[f"{phase}_inn2"]
        p_dot, p_1, p_2, p_3, p_4, p_6, p_wkt, p_wide, p_nb = probs
        leg = [(p_dot, 0, 0), (p_1, 1, 0), (p_2, 2, 0), (p_3, 3, 0), (p_4, 4, 0), (p_6, 6, 0), (p_wkt, 0, 1)]
        exp_w = sum(p * (1.0 if req - r <= 0 else (0.5 if req - r == 1 else 0.0)) for p, r, w in leg if wt + w < 10)
        p_ex = p_wide + p_nb
        wp_ex = 0.5 if req <= 1 else (0.5 if req == 2 else 0.0)
        return float(np.clip(exp_w + p_ex * wp_ex, 0.0, 1.0))
    rrr = max(0.0, min(36.0, (req / max(1.0, brem)) * 6.0))
    wk_rem = 10.0 - wt
    bnorm = brem / 120.0
    inter = rrr * (10.0 - wk_rem)
    raw = np.array([rrr, wk_rem, bnorm, inter])
    norm = (raw - m2) / s2
    z = beta2[0] + norm @ beta2[1:]
    return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

def calc_conseq_inn2(req, brem, wt, phase):
    probs = t_dict[f"{phase}_inn2"]
    wp0 = calc_wp2(req, brem, wt, phase)
    exp_sw = 0.0
    for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
        next_req = req - r_add
        next_brem = brem - b_add
        next_wt = wt + w_add
        next_ov = (120 - next_brem) // 6 + 1
        next_ph = 'PP' if next_ov <= 6 else ('Middle' if next_ov <= 15 else 'Death')
        wp1 = calc_wp2(next_req, next_brem, next_wt, next_ph)
        exp_sw += p_o * abs(wp1 - wp0)
    return wp0, exp_sw

def calc_task_diff(inn, sc, wt, lb, brem, req, phase, par=170.0):
    mu_w = mu_w_map.get(lb, 3.5)
    sig_w = sig_w_map.get(lb, 1.5)
    if inn == 1:
        r_par = par / 20.0
        rar = max(0.0, (par - sc) / (max(1, brem) / 6.0))
        w_stress = 0.0 if lb == 0 else (wt - mu_w) / sig_w
        z_b1 = 0.60 * ((rar - r_par) / r_par) + 0.40 * w_stress
        t_bat = 100.0 / (1.0 + np.exp(-1.2 * np.clip(z_b1, -20, 20)))
        
        crr = r_par if lb == 0 else (sc / lb) * 6.0
        fielding = 0.50 if phase in ['PP', 'Death'] else 0.0
        w_stress_bowl = 0.0 if lb == 0 else (mu_w - wt) / sig_w
        z_bo1 = 0.50 * ((crr - r_par) / r_par) + 0.35 * w_stress_bowl + 0.15 * fielding
        t_bowl = 100.0 / (1.0 + np.exp(-1.1 * np.clip(z_bo1, -20, 20)))
        return t_bat, t_bowl
    else:
        rrr = max(0.0, min(36.0, (req / max(1, brem)) * 6.0))
        z_b2 = 0.55 * ((rrr - 8.10) / 3.00) + 0.25 * ((wt - 3.50) / 2.00) + 0.20 * ((rrr * wt - 28.0) / 25.0)
        t_bat = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_b2, -20, 20)))
        
        w_stress_bowl2 = (mu_w - wt) / sig_w
        z_bo2 = 0.60 * ((8.10 - rrr) / 3.00) + 0.40 * w_stress_bowl2
        t_bowl = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_bo2, -20, 20)))
        return t_bat, t_bowl

def calc_conseq_inn1_base(sc, lb, wt, par, phase):
    r_par = par / 20.0
    def wp(s_in, b_in, w_in):
        wkr = 10.0 - w_in
        bb = b_in / 120.0
        sd = (s_in - par * bb) / 30.0
        c = (s_in / max(1.0, b_in)) * 6.0
        cr = c / r_par
        br = (120.0 - b_in) / 120.0
        ri = wkr * br
        raw = np.array([sd, wkr, bb, ri, cr])
        norm = (raw - m1_base) / s1_base
        z = beta1_base[0] + norm @ beta1_base[1:]
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

    probs = t_dict[f"{phase}_inn1"]
    wp0 = wp(sc, lb, wt)
    exp_sw = 0.0
    for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
        wp1 = wp(sc + r_add, lb + b_add, wt + w_add)
        exp_sw += p_o * abs(wp1 - wp0)
    return wp0, exp_sw

def calc_conseq_inn1_shrunk(sc, lb, wt, par, phase):
    r_par = par / 20.0
    M_val = 18.0
    def wp(s_in, b_in, w_in):
        wkr = 10.0 - w_in
        bb = b_in / 120.0
        sd = (s_in - par * bb) / 30.0
        c = (s_in + M_val * (r_par / 6.0)) / (b_in + M_val) * 6.0
        cr = c / r_par
        br = (120.0 - b_in) / 120.0
        ri = wkr * br
        raw = np.array([sd, wkr, bb, ri, cr])
        norm = (raw - m1_shrunk) / s1_shrunk
        z = beta1_shrunk[0] + norm @ beta1_shrunk[1:]
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

    probs = t_dict[f"{phase}_inn1"]
    wp0 = wp(sc, lb, wt)
    exp_sw = 0.0
    for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
        wp1 = wp(sc + r_add, lb + b_add, wt + w_add)
        exp_sw += p_o * abs(wp1 - wp0)
    return wp0, exp_sw

# 10 Test Scenarios
scenarios = [
    {
        'id': 'S01', 'name': 'Opening ball at 0/0', 'inn': 1,
        'sc': 0, 'wt': 0, 'lb': 0, 'brem': 120, 'req': None, 'phase': 'PP', 'ov': 1, 'par': 170.0
    },
    {
        'id': 'S01B', 'name': 'Opening ball after fast start (20/0, 1.0 ov)', 'inn': 1,
        'sc': 20, 'wt': 0, 'lb': 6, 'brem': 114, 'req': None, 'phase': 'PP', 'ov': 2, 'par': 170.0
    },
    {
        'id': 'S02', 'name': 'Early-innings collapse (15/3, 2.4 ov)', 'inn': 1,
        'sc': 15, 'wt': 3, 'lb': 16, 'brem': 104, 'req': None, 'phase': 'PP', 'ov': 3, 'par': 170.0
    },
    {
        'id': 'S03', 'name': 'Middle-over collapse (45/5, 10.0 ov)', 'inn': 1,
        'sc': 45, 'wt': 5, 'lb': 60, 'brem': 60, 'req': None, 'phase': 'Middle', 'ov': 11, 'par': 170.0
    },
    {
        'id': 'S04', 'name': 'Comfortable middle situation (85/1, 11.0 ov)', 'inn': 1,
        'sc': 85, 'wt': 1, 'lb': 66, 'brem': 54, 'req': None, 'phase': 'Middle', 'ov': 12, 'par': 170.0
    },
    {
        'id': 'S05', 'name': 'Death acceleration (175/2, 16.0 ov)', 'inn': 1,
        'sc': 175, 'wt': 2, 'lb': 96, 'brem': 24, 'req': None, 'phase': 'Death', 'ov': 17, 'par': 170.0
    },
    {
        'id': 'S06', 'name': 'Difficult chase (110/5, needs 65 off 30, RRR=13.0)', 'inn': 2,
        'sc': 110, 'wt': 5, 'lb': 90, 'brem': 30, 'req': 65, 'phase': 'Death', 'ov': 16, 'par': 175.0
    },
    {
        'id': 'S07', 'name': 'Comfortable chase (150/2, needs 2 off 30)', 'inn': 2,
        'sc': 150, 'wt': 2, 'lb': 90, 'brem': 30, 'req': 2, 'phase': 'Death', 'ov': 16, 'par': 152.0
    },
    {
        'id': 'S08', 'name': 'Impossible chase (105/8, needs 80 off 12, RRR=40.0)', 'inn': 2,
        'sc': 105, 'wt': 8, 'lb': 108, 'brem': 12, 'req': 80, 'phase': 'Death', 'ov': 19, 'par': 185.0
    },
    {
        'id': 'S09', 'name': 'Final ball climax (needs 4 off 1, 7 down)', 'inn': 2,
        'sc': 152, 'wt': 7, 'lb': 119, 'brem': 1, 'req': 4, 'phase': 'Death', 'ov': 20, 'par': 156.0
    }
]

results = []
for scn in scenarios:
    inn = scn['inn']
    t_bat, t_bowl = calc_task_diff(inn, scn['sc'], scn['wt'], scn['lb'], scn['brem'], scn['req'], scn['phase'], scn['par'])
    
    if inn == 1:
        # Base
        _, raw_L_base = calc_conseq_inn1_base(scn['sc'], scn['lb'], scn['wt'], scn['par'], scn['phase'])
        L_norm_base = rank_ecdf(base_inn1_sorted, raw_L_base)
        P_bat_base = math.sqrt(t_bat * L_norm_base)
        
        # Shrunk Whole
        _, raw_L_shrunk = calc_conseq_inn1_shrunk(scn['sc'], scn['lb'], scn['wt'], scn['par'], scn['phase'])
        L_norm_shrunk_whole = rank_ecdf(shrunk_inn1_whole, raw_L_shrunk)
        P_bat_shrunk_whole = math.sqrt(t_bat * L_norm_shrunk_whole)
        
        # Shrunk Phase
        ref_p = shrunk_inn1_pp if scn['phase'] == 'PP' else (shrunk_inn1_mid if scn['phase'] == 'Middle' else shrunk_inn1_death)
        L_norm_shrunk_phase = rank_ecdf(ref_p, raw_L_shrunk)
        P_bat_shrunk_phase = math.sqrt(t_bat * L_norm_shrunk_phase)
        
        # Shrunk Smooth Phase
        rk_p = rank_ecdf(shrunk_inn1_pp, raw_L_shrunk)
        rk_m = rank_ecdf(shrunk_inn1_mid, raw_L_shrunk)
        rk_d = rank_ecdf(shrunk_inn1_death, raw_L_shrunk)
        ov = scn['ov']
        if ov < 6: L_norm_smooth = rk_p
        elif ov == 6: L_norm_smooth = 0.75 * rk_p + 0.25 * rk_m
        elif ov == 7: L_norm_smooth = 0.25 * rk_p + 0.75 * rk_m
        elif 8 <= ov < 15: L_norm_smooth = rk_m
        elif ov == 15: L_norm_smooth = 0.75 * rk_m + 0.25 * rk_d
        elif ov == 16: L_norm_smooth = 0.25 * rk_m + 0.75 * rk_d
        else: L_norm_smooth = rk_d
        P_bat_smooth = math.sqrt(t_bat * L_norm_smooth)
        
    else:
        # Innings 2 (chase target fixed)
        _, raw_L_base = calc_conseq_inn2(scn['req'], scn['brem'], scn['wt'], scn['phase'])
        raw_L_shrunk = raw_L_base
        L_norm_base = rank_ecdf(base_inn2_sorted, raw_L_base)
        P_bat_base = math.sqrt(t_bat * L_norm_base)
        L_norm_shrunk_whole = L_norm_base
        P_bat_shrunk_whole = P_bat_base
        L_norm_shrunk_phase = L_norm_base # In Inn 2, whole-innings is preferred
        P_bat_shrunk_phase = P_bat_base
        L_norm_smooth = L_norm_base
        P_bat_smooth = P_bat_base

    results.append({
        'ID': scn['id'],
        'Name': scn['name'],
        'T_bat': t_bat,
        'L_Base': raw_L_base,
        'Lnorm_Base': L_norm_base,
        'P_Base': P_bat_base,
        'L_Shrunk': raw_L_shrunk,
        'Lnorm_ShrunkWhole': L_norm_shrunk_whole,
        'P_ShrunkWhole': P_bat_shrunk_whole,
        'Lnorm_Smooth': L_norm_smooth,
        'P_Smooth': P_bat_smooth
    })

res_df = pd.DataFrame(results)
print("\n=== COMPREHENSIVE SCENARIO COMPARISON MATRIX ===")
cols_show = ['ID', 'T_bat', 'P_Base', 'P_ShrunkWhole', 'P_Smooth', 'Lnorm_Base', 'Lnorm_Smooth']
print(res_df[cols_show].to_string(index=False))

for _, r in res_df.iterrows():
    print(f"\n[{r['ID']}] {r['Name']}")
    print(f"  T_bat = {r['T_bat']:5.2f}")
    print(f"  Base (Step 4):   Raw L = {r['L_Base']:.5f} -> L_norm = {r['Lnorm_Base']:5.2f} -> P_bat = {r['P_Base']:5.2f}")
    print(f"  Shrunk Whole:    Raw L = {r['L_Shrunk']:.5f} -> L_norm = {r['Lnorm_ShrunkWhole']:5.2f} -> P_bat = {r['P_ShrunkWhole']:5.2f}")
    print(f"  Smoothed Phase:  Raw L = {r['L_Shrunk']:.5f} -> L_norm = {r['Lnorm_Smooth']:5.2f} -> P_bat = {r['P_Smooth']:5.2f}")

res_df.to_csv('scratch/scenario_comparison_matrix.csv', index=False)
