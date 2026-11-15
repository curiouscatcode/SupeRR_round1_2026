"""
Step 4.3: Regression Comparison Suite
====================================
Compares delivery_pressure_v3.parquet (M=18 Bayesian CRR shrinkage)
against delivery_pressure_v2.parquet (previous Step 4 baseline).

Generates outputs/step_4_3_controlled_implementation/step_4_3_regression_comparison.csv
"""

import os
import pandas as pd
import numpy as np

v2_path = "outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet"
v3_path = "outputs/step_4_pressure_pipeline/delivery_pressure_v3.parquet"
OUTPUT_DIR = "outputs/step_4_3_controlled_implementation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading v2 (baseline) and v3 (M=18 shrunk)...")
df_v2 = pd.read_parquet(v2_path)
df_v3 = pd.read_parquet(v3_path)

assert len(df_v2) == len(df_v3) == 186780, "Delivery counts do not match!"

# Compute differences (v3 - v2)
diff_p_bat = df_v3["pressure_batting"] - df_v2["pressure_batting"]
diff_p_bowl = df_v3["pressure_bowling"] - df_v2["pressure_bowling"]
diff_raw_L = df_v3["raw_consequence_L"] - df_v2["raw_consequence_L"]
diff_l_norm = df_v3["normalized_consequence_L"] - df_v2["normalized_consequence_L"]
diff_wp = df_v3["pre_delivery_wp"] - df_v2["pre_delivery_wp"]

# -----------------------------------------------------------------------------
# 1. Innings 2 Invariance Check
# -----------------------------------------------------------------------------
inn2_mask = (df_v2["innings"] == 2).values
inn2_p_bat_diff = np.max(np.abs(diff_p_bat[inn2_mask]))
inn2_p_bowl_diff = np.max(np.abs(diff_p_bowl[inn2_mask]))
inn2_raw_L_diff = np.max(np.abs(diff_raw_L[inn2_mask]))
inn2_l_norm_diff = np.max(np.abs(diff_l_norm[inn2_mask]))
inn2_wp_diff = np.max(np.abs(diff_wp[inn2_mask]))

print("\n--- Innings 2 Invariance Verification ---")
print(f"Max abs diff P_bat:   {inn2_p_bat_diff:.2e}")
print(f"Max abs diff P_bowl:  {inn2_p_bowl_diff:.2e}")
print(f"Max abs diff Raw L:   {inn2_raw_L_diff:.2e}")
print(f"Max abs diff L_norm:  {inn2_l_norm_diff:.2e}")
print(f"Max abs diff Pre WP:  {inn2_wp_diff:.2e}")
assert inn2_p_bat_diff < 1e-9, "Innings 2 batting pressure changed unexpectedly!"
assert inn2_p_bowl_diff < 1e-9, "Innings 2 bowling pressure changed unexpectedly!"

# -----------------------------------------------------------------------------
# 2. Stratified Regression Comparisons
# -----------------------------------------------------------------------------
strata = [
    ("Cohort Overall", np.ones(len(df_v2), dtype=bool)),
    ("Innings 2 (Chasing)", inn2_mask),
    ("Innings 1 (Overall)", (df_v2["innings"] == 1).values),
    ("Innings 1 - Powerplay", (df_v2["innings"] == 1) & (df_v2["phase"] == "PP")),
    ("Innings 1 - Middle", (df_v2["innings"] == 1) & (df_v2["phase"] == "Middle")),
    ("Innings 1 - Death", (df_v2["innings"] == 1) & (df_v2["phase"] == "Death")),
]

# Add Over 1 to Over 6 breakdowns for Innings 1
for ov in range(1, 7):
    strata.append((f"Innings 1 - Over {ov}", (df_v2["innings"] == 1) & (df_v2["overid"] == ov)))

reg_rows = []
for label, mask in strata:
    n = int(np.sum(mask))
    dp_b = diff_p_bat[mask]
    dp_bw = diff_p_bowl[mask]
    dl_n = diff_l_norm[mask]
    
    # Values under v2 and v3
    v2_pbat = df_v2.loc[mask, "pressure_batting"]
    v3_pbat = df_v3.loc[mask, "pressure_batting"]
    
    v2_pbowl = df_v2.loc[mask, "pressure_bowling"]
    v3_pbowl = df_v3.loc[mask, "pressure_bowling"]
    
    changed_count = int(np.sum(np.abs(dp_b) > 1e-4))
    
    reg_rows.append({
        "stratum": label,
        "deliveries": n,
        "changed_deliveries": changed_count,
        "pct_changed": round(changed_count / n * 100.0, 2),
        "v2_Pbat_mean": round(float(v2_pbat.mean()), 2),
        "v3_Pbat_mean": round(float(v3_pbat.mean()), 2),
        "mean_diff_Pbat": round(float(dp_b.mean()), 4),
        "median_diff_Pbat": round(float(dp_b.median()), 4),
        "std_diff_Pbat": round(float(dp_b.std()), 4),
        "max_abs_diff_Pbat": round(float(np.max(np.abs(dp_b))), 4),
        "v2_Pbowl_mean": round(float(v2_pbowl.mean()), 2),
        "v3_Pbowl_mean": round(float(v3_pbowl.mean()), 2),
        "mean_diff_Pbowl": round(float(dp_bw.mean()), 4),
        "median_diff_Pbowl": round(float(dp_bw.median()), 4),
        "max_abs_diff_Pbowl": round(float(np.max(np.abs(dp_bw))), 4),
        "mean_diff_Lnorm": round(float(dl_n.mean()), 4),
        "median_diff_Lnorm": round(float(dl_n.median()), 4),
        "max_abs_diff_Lnorm": round(float(np.max(np.abs(dl_n))), 4)
    })

reg_df = pd.DataFrame(reg_rows)
out_csv = os.path.join(OUTPUT_DIR, "step_4_3_regression_comparison.csv")
reg_df.to_csv(out_csv, index=False)
print(f"Saved step_4_3_regression_comparison.csv to {out_csv}")

print("\n--- Stratum Comparison Summary ---")
print(reg_df[["stratum", "deliveries", "v2_Pbat_mean", "v3_Pbat_mean", "mean_diff_Pbat", "max_abs_diff_Pbat"]].to_string())
