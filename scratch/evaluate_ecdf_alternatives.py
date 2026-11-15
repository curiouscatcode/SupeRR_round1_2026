import pandas as pd
import numpy as np

# Load deliveries
df = pd.read_parquet('outputs/step_4_pressure_pipeline/deliveries_with_task_difficulty.parquet')
final_df = pd.read_parquet('outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet')
df['pressure_batting'] = final_df['pressure_batting']
df['pressure_bowling'] = final_df['pressure_bowling']

inn1 = df[df['innings'] == 1].copy()
inn2 = df[df['innings'] == 2].copy()

print("=== INVESTIGATION A: EVALUATING ECDF NORMALIZATION ALTERNATIVES ===")
print(f"Innings 1 Total Deliveries: {len(inn1)}")
print(f"Innings 2 Total Deliveries: {len(inn2)}")

# -------------------------------------------------------------------------
# Alternative 1: Baseline Whole-Innings ECDF (Current)
# -------------------------------------------------------------------------
# Already computed in df['normalized_consequence_L']

# -------------------------------------------------------------------------
# Alternative 2: Strict Phase-Conditional ECDF
# -------------------------------------------------------------------------
# Slices: PP (ov 1-6), Middle (ov 7-15), Death (ov 16-20)
def calc_phase_ecdf(sub_df):
    l_norm = np.zeros(len(sub_df), dtype=float)
    for ph in ['PP', 'Middle', 'Death']:
        mask = (sub_df['phase'] == ph).values
        vals = sub_df.loc[mask, 'raw_consequence_L'].values
        sorted_vals = np.sort(vals)
        n = len(sorted_vals)
        r_l = np.searchsorted(sorted_vals, vals, side='left')
        r_r = np.searchsorted(sorted_vals, vals, side='right')
        l_norm[mask] = ((r_l + r_r) / (2.0 * n)) * 100.0
    return l_norm

inn1['L_norm_phase'] = calc_phase_ecdf(inn1)
inn2['L_norm_phase'] = calc_phase_ecdf(inn2)

# -------------------------------------------------------------------------
# Alternative 3: Rolling Window ECDF (Window = +/- 2 overs, i.e., 5 overs total)
# -------------------------------------------------------------------------
# For over o in [1, 20], reference pool is deliveries in [max(1, o-2), min(20, o+2)]
def calc_rolling_ecdf(sub_df, window_radius=2):
    l_norm = np.zeros(len(sub_df), dtype=float)
    overs = sub_df['overid'].values
    vals = sub_df['raw_consequence_L'].values
    for ov in range(1, 21):
        mask_ov = (overs == ov)
        if not np.any(mask_ov):
            continue
        # reference pool
        min_ov = max(1, ov - window_radius)
        max_ov = min(20, ov + window_radius)
        ref_mask = (overs >= min_ov) & (overs <= max_ov)
        ref_vals = vals[ref_mask]
        sorted_ref = np.sort(ref_vals)
        n_ref = len(sorted_ref)
        
        ov_vals = vals[mask_ov]
        r_l = np.searchsorted(sorted_ref, ov_vals, side='left')
        r_r = np.searchsorted(sorted_ref, ov_vals, side='right')
        l_norm[mask_ov] = ((r_l + r_r) / (2.0 * n_ref)) * 100.0
    return l_norm

inn1['L_norm_rolling'] = calc_rolling_ecdf(inn1, window_radius=2)
inn2['L_norm_rolling'] = calc_rolling_ecdf(inn2, window_radius=2)

# -------------------------------------------------------------------------
# Alternative 4: Phase-Conditional with Boundary Smoothing (Interpolation on ov 6-7 and 15-16)
# -------------------------------------------------------------------------
# Smooth transition: 
# Over 6: 75% PP ECDF + 25% Mid ECDF
# Over 7: 25% PP ECDF + 75% Mid ECDF
# Over 15: 75% Mid ECDF + 25% Death ECDF
# Over 16: 25% Mid ECDF + 75% Death ECDF
def calc_smoothed_phase_ecdf(sub_df):
    # Precompute all 3 phase reference sorted arrays
    refs = {}
    for ph in ['PP', 'Middle', 'Death']:
        refs[ph] = np.sort(sub_df[sub_df['phase'] == ph]['raw_consequence_L'].values)
        
    def rank_in(arr, v):
        rl = np.searchsorted(arr, v, side='left')
        rr = np.searchsorted(arr, v, side='right')
        return ((rl + rr) / (2.0 * len(arr))) * 100.0

    l_norm = np.zeros(len(sub_df), dtype=float)
    overs = sub_df['overid'].values
    vals = sub_df['raw_consequence_L'].values
    
    for i in range(len(sub_df)):
        ov = overs[i]
        v = vals[i]
        if ov < 6:
            l_norm[i] = rank_in(refs['PP'], v)
        elif ov == 6:
            l_norm[i] = 0.75 * rank_in(refs['PP'], v) + 0.25 * rank_in(refs['Middle'], v)
        elif ov == 7:
            l_norm[i] = 0.25 * rank_in(refs['PP'], v) + 0.75 * rank_in(refs['Middle'], v)
        elif 8 <= ov < 15:
            l_norm[i] = rank_in(refs['Middle'], v)
        elif ov == 15:
            l_norm[i] = 0.75 * rank_in(refs['Middle'], v) + 0.25 * rank_in(refs['Death'], v)
        elif ov == 16:
            l_norm[i] = 0.25 * rank_in(refs['Middle'], v) + 0.75 * rank_in(refs['Death'], v)
        else:
            l_norm[i] = rank_in(refs['Death'], v)
    return l_norm

inn1['L_norm_smooth'] = calc_smoothed_phase_ecdf(inn1)
inn2['L_norm_smooth'] = calc_smoothed_phase_ecdf(inn2)

# Summarize Innings 1 Consequence and Resulting P_bat
print("\n--- INNINGS 1: CONSEQUENCE (L_norm) BY PHASE ACROSS ALTERNATIVES ---")
for ph in ['PP', 'Middle', 'Death']:
    sub = inn1[inn1['phase'] == ph]
    print(f"Phase {ph:7s} (N={len(sub):5d}):")
    print(f"  Alt 1 (Whole-Innings): Mean={sub['normalized_consequence_L'].mean():.2f}, Med={sub['normalized_consequence_L'].median():.2f}")
    print(f"  Alt 2 (Strict Phase):   Mean={sub['L_norm_phase'].mean():.2f}, Med={sub['L_norm_phase'].median():.2f}")
    print(f"  Alt 3 (Rolling 5-ov):   Mean={sub['L_norm_rolling'].mean():.2f}, Med={sub['L_norm_rolling'].median():.2f}")
    print(f"  Alt 4 (Smoothed Phase): Mean={sub['L_norm_smooth'].mean():.2f}, Med={sub['L_norm_smooth'].median():.2f}")

# Compute Resulting Batting Pressure for Innings 1
for alt, col in [('Alt 1 (Whole)', 'normalized_consequence_L'), ('Alt 2 (Phase)', 'L_norm_phase'), ('Alt 3 (Rolling)', 'L_norm_rolling'), ('Alt 4 (Smooth)', 'L_norm_smooth')]:
    inn1[f'P_bat_{alt}'] = np.sqrt(inn1['task_difficulty_bat'] * inn1[col])

print("\n--- INNINGS 1: BATTING PRESSURE (P_bat) BY PHASE ACROSS ALTERNATIVES ---")
for ph in ['PP', 'Middle', 'Death']:
    sub = inn1[inn1['phase'] == ph]
    print(f"Phase {ph:7s} (N={len(sub):5d}):")
    print(f"  Alt 1 (Whole-Innings): Mean={sub['P_bat_Alt 1 (Whole)'].mean():.2f}, Med={sub['P_bat_Alt 1 (Whole)'].median():.2f}")
    print(f"  Alt 2 (Strict Phase):   Mean={sub['P_bat_Alt 2 (Phase)'].mean():.2f}, Med={sub['P_bat_Alt 2 (Phase)'].median():.2f}")
    print(f"  Alt 3 (Rolling 5-ov):   Mean={sub['P_bat_Alt 3 (Rolling)'].mean():.2f}, Med={sub['P_bat_Alt 3 (Rolling)'].median():.2f}")
    print(f"  Alt 4 (Smoothed Phase): Mean={sub['P_bat_Alt 4 (Smooth)'].mean():.2f}, Med={sub['P_bat_Alt 4 (Smooth)'].median():.2f}")

# Check Boundary Discontinuity between Over 6 (ball 5.6) and Over 7 (ball 6.1)
print("\n--- BOUNDARY CONTINUITY: OVER 6 vs OVER 7 (INNINGS 1) ---")
ov6 = inn1[inn1['overid'] == 6]
ov7 = inn1[inn1['overid'] == 7]
print(f"Over 6 Mean L_norm: Alt1={ov6['normalized_consequence_L'].mean():.2f} | Alt2={ov6['L_norm_phase'].mean():.2f} | Alt3={ov6['L_norm_rolling'].mean():.2f} | Alt4={ov6['L_norm_smooth'].mean():.2f}")
print(f"Over 7 Mean L_norm: Alt1={ov7['normalized_consequence_L'].mean():.2f} | Alt2={ov7['L_norm_phase'].mean():.2f} | Alt3={ov7['L_norm_rolling'].mean():.2f} | Alt4={ov7['L_norm_smooth'].mean():.2f}")
print(f"Step Jump (Ov7 - Ov6):")
print(f"  Alt 1: {ov7['normalized_consequence_L'].mean() - ov6['normalized_consequence_L'].mean():+.2f}")
print(f"  Alt 2: {ov7['L_norm_phase'].mean() - ov6['L_norm_phase'].mean():+.2f}")
print(f"  Alt 3: {ov7['L_norm_rolling'].mean() - ov6['L_norm_rolling'].mean():+.2f}")
print(f"  Alt 4: {ov7['L_norm_smooth'].mean() - ov6['L_norm_smooth'].mean():+.2f}")

# Check Innings 2 to see if Innings 2 needs any change
print("\n--- INNINGS 2: COMPARISON OF ALT 1 vs ALT 2 ---")
for ph in ['PP', 'Middle', 'Death']:
    sub = inn2[inn2['phase'] == ph]
    p_alt1 = np.sqrt(sub['task_difficulty_bat'] * sub['normalized_consequence_L'])
    p_alt2 = np.sqrt(sub['task_difficulty_bat'] * sub['L_norm_phase'])
    print(f"Phase {ph:7s} (N={len(sub):5d}):")
    print(f"  Alt 1 (Whole-Innings): Mean P_bat={p_alt1.mean():.2f}, Median P_bat={p_alt1.median():.2f} | Mean L_norm={sub['normalized_consequence_L'].mean():.2f}")
    print(f"  Alt 2 (Strict Phase):   Mean P_bat={p_alt2.mean():.2f}, Median P_bat={p_alt2.median():.2f} | Mean L_norm={sub['L_norm_phase'].mean():.2f}")
