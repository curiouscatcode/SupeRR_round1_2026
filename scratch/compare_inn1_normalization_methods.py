import sys
sys.path.append('.')
import math
import pandas as pd
import numpy as np

# Load deliveries
df = pd.read_parquet('outputs/step_4_pressure_pipeline/deliveries_with_task_difficulty.parquet')
inn1 = df[df['innings'] == 1].copy()

# Load shrunk raw L from fast test
import importlib
mod = importlib.import_module('scratch.test_combined_reconciliations_fast')
inn1['raw_L_shrunk'] = mod.inn1_df['raw_L_shrunk']

raw_L = inn1['raw_L_shrunk'].values
t_bat = inn1['task_difficulty_bat'].values
phases = inn1['phase'].values
overs = inn1['overid'].values

# Method 1: Current Whole ECDF on Shrunk L
sorted_w = np.sort(raw_L)
nw = len(sorted_w)
l_whole = ((np.searchsorted(sorted_w, raw_L, side='left') + np.searchsorted(sorted_w, raw_L, side='right')) / (2.0 * nw)) * 100.0

# Method 2: Hybrid Blend (50% Whole-Innings ECDF + 50% Phase-Conditional ECDF)
# Blends macro match consequence with within-phase relative leverage
phase_refs = {ph: np.sort(inn1[inn1['phase'] == ph]['raw_L_shrunk'].values) for ph in ['PP', 'Middle', 'Death']}
l_phase = np.zeros(len(inn1))
for ph in ['PP', 'Middle', 'Death']:
    m = (phases == ph)
    arr = phase_refs[ph]
    l_phase[m] = ((np.searchsorted(arr, raw_L[m], side='left') + np.searchsorted(arr, raw_L[m], side='right')) / (2.0 * len(arr))) * 100.0

l_hybrid_50 = 0.50 * l_whole + 0.50 * l_phase

# Method 3: Rolling Window ECDF (Radius = 3 overs, i.e., 7-over window)
l_rolling_3 = np.zeros(len(inn1))
for ov in range(1, 21):
    m_ov = (overs == ov)
    ref_mask = (overs >= max(1, ov - 3)) & (overs <= min(20, ov + 3))
    ref_arr = np.sort(raw_L[ref_mask])
    l_rolling_3[m_ov] = ((np.searchsorted(ref_arr, raw_L[m_ov], side='left') + np.searchsorted(ref_arr, raw_L[m_ov], side='right')) / (2.0 * len(ref_arr))) * 100.0

# Method 4: Standardized Z-Score Sigmoid on Raw L
# Since raw L is approximately normal in Innings 1, Z = (L - mean) / std, then Sigmoid
mu_L = np.mean(raw_L)
std_L = np.std(raw_L)
z_L = (raw_L - mu_L) / std_L
# Sigmoid mapping centered at 50, k=1.0
l_sigmoid = 100.0 / (1.0 + np.exp(-1.0 * z_L))

methods = [
    ('1. Whole ECDF (Shrunk M=18)', l_whole),
    ('2. Strict Phase ECDF', l_phase),
    ('3. Hybrid 50/50 (Whole + Phase)', l_hybrid_50),
    ('4. Rolling 7-Over ECDF', l_rolling_3),
    ('5. Standardized Sigmoid', l_sigmoid)
]

print("=== INNINGS 1 NORMALIZATION METHODS COMPARISON ===")
print("Method                      | Phase  | Mean L_norm | Med L_norm | Mean P_bat | Med P_bat | Ov6->7 Jump")
print("-" * 95)

for name, l_arr in methods:
    p_bat_arr = np.sqrt(t_bat * l_arr)
    # ov 6 to 7 jump
    ov6_l = l_arr[overs == 6].mean()
    ov7_l = l_arr[overs == 7].mean()
    jump = ov7_l - ov6_l
    for ph in ['PP', 'Middle', 'Death']:
        mask = (phases == ph)
        print(f"{name:27s} | {ph:6s} |   {l_arr[mask].mean():5.2f}    |   {np.median(l_arr[mask]):5.2f}   |   {p_bat_arr[mask].mean():5.2f}   |   {np.median(p_bat_arr[mask]):5.2f}   | {jump:+6.2f} (ph={ph})")
    print("-" * 95)

# Also check Scenario S02 (Collapse: 15/3 at 2.4 ov, sc=15, wt=3, lb=16, t=80.64, raw_L=0.01025)
raw_L_s02 = 0.01025
t_s02 = 80.64
print("\n--- PERFORMANCE ON EARLY COLLAPSE SCENARIO S02 (15/3, 2.4 ov, T=80.64) ---")
# evaluate S02 under each method
rk_w = ((np.searchsorted(sorted_w, raw_L_s02, side='left') + np.searchsorted(sorted_w, raw_L_s02, side='right')) / (2.0 * nw)) * 100.0
rk_p = ((np.searchsorted(phase_refs['PP'], raw_L_s02, side='left') + np.searchsorted(phase_refs['PP'], raw_L_s02, side='right')) / (2.0 * len(phase_refs['PP']))) * 100.0
rk_hyb = 0.5 * rk_w + 0.5 * rk_p
ref_roll = np.sort(raw_L[(overs >= 1) & (overs <= 6)])
rk_roll = ((np.searchsorted(ref_roll, raw_L_s02, side='left') + np.searchsorted(ref_roll, raw_L_s02, side='right')) / (2.0 * len(ref_roll))) * 100.0
rk_sig = 100.0 / (1.0 + np.exp(-1.0 * (raw_L_s02 - mu_L) / std_L))

print(f"1. Whole ECDF:         L_norm = {rk_w:5.2f} -> P_bat = {math.sqrt(t_s02 * rk_w):5.2f}")
print(f"2. Strict Phase ECDF:   L_norm = {rk_p:5.2f} -> P_bat = {math.sqrt(t_s02 * rk_p):5.2f}  <-- COLLAPSE DESTROYED!")
print(f"3. Hybrid 50/50:        L_norm = {rk_hyb:5.2f} -> P_bat = {math.sqrt(t_s02 * rk_hyb):5.2f}")
print(f"4. Rolling 7-Over ECDF: L_norm = {rk_roll:5.2f} -> P_bat = {math.sqrt(t_s02 * rk_roll):5.2f}")
print(f"5. Standardized Sigmoid:L_norm = {rk_sig:5.2f} -> P_bat = {math.sqrt(t_s02 * rk_sig):5.2f}")
