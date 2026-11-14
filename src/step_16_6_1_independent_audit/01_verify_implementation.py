"""
Step 16.6.1: Script 01 - Verify Implementation and Independent Recalculation
=============================================================================
Audits Step 16.6 implementation:
1. Re-computes Phase x Innings Z-scores for Batting PI and Bowling PI from raw PI values.
2. Re-computes Phase x Innings Z-scores for Expected Delivery Leverage.
3. Re-computes Candidates 0, 1A, 1B, 2, and 3 independently.
4. Compares Phase x Innings standardization vs Global standardization for Candidate 2.
5. Verifies population masks: is_batter_ball_faced (180,839) vs is_legal_ball (180,041).
6. Compares recalculations directly with Step 16.6 outputs to verify exact fidelity.
7. Exports recalculated_candidates_comparison.csv.
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_6_1_independent_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STEP_16_5_DIR = Path("outputs/step_16_5_wpa_investigation")
STEP_16_6_DIR = Path("outputs/step_16_6_leverage_integration")
PROCESSED_DIR = Path("data/processed")


def standardize_series(series):
    s_std = series.std()
    if s_std == 0 or np.isnan(s_std):
        return series - series.mean()
    return (series - series.mean()) / s_std


def main():
    print("=== Step 16.6.1 Script 01: Implementation Verification ===")
    t0 = time.time()

    # 1. Load source datasets
    wpa_parquet = STEP_16_5_DIR / "delivery_wpa_leverage.parquet"
    print(f"Loading base dataset from {wpa_parquet}...")
    df = pd.read_parquet(wpa_parquet)
    n_deliv = len(df)
    print(f"Loaded {n_deliv:,} deliveries.")

    # Load frozen Step 16 delivery pressure index to check raw values
    dpi_path = PROCESSED_DIR / "delivery_pressure_index.csv"
    print(f"Loading raw PI from {dpi_path}...")
    dpi_df = pd.read_csv(dpi_path, usecols=['match_id', 'innings', 'overid', 'innings_ball_num', 'Batting_PI', 'Bowling_PI'])
    
    # Merge raw PI
    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    df = df.merge(dpi_df, on=merge_keys, how='left', suffixes=('', '_raw_check'))

    # Check match of raw PI
    bat_pi_diff = np.nanmax(np.abs(df['Batting_PI'] - df['Batting_PI_raw_check']))
    bowl_pi_diff = np.nanmax(np.abs(df['Bowling_PI'] - df['Bowling_PI_raw_check']))
    print(f"Max absolute difference in raw Batting PI: {bat_pi_diff:.8f}")
    print(f"Max absolute difference in raw Bowling PI: {bowl_pi_diff:.8f}")

    # 2. Verify Population Masks
    bat_mask = df['is_batter_ball_faced'] == 1
    bowl_mask = df['is_legal_ball'] == 1
    print(f"\nPopulation breakdown:")
    print(f"  Total Clean Deliveries: {len(df):,}")
    print(f"  Batting balls faced (bat_mask): {bat_mask.sum():,}")
    print(f"  Bowling legal balls (bowl_mask): {bowl_mask.sum():,}")
    print(f"  Wides (not batter faced): {(df['is_batter_ball_faced'] == 0).sum():,}")
    print(f"  No balls / Extras (not legal ball): {(df['is_legal_ball'] == 0).sum():,}")

    # 3. Independent Recalculation of Phase x Innings Z-scores for PI
    print("\n--- Auditing Step 16 Frozen PI Z-scores ---")
    df['recalc_z_pi_bat'] = np.nan
    bat_grouped_pi = df[bat_mask].groupby(['innings', 'phase'])['Batting_PI']
    df.loc[bat_mask, 'recalc_z_pi_bat'] = (df.loc[bat_mask, 'Batting_PI'] - bat_grouped_pi.transform('mean')) / bat_grouped_pi.transform('std')

    df['recalc_z_pi_bowl'] = np.nan
    bowl_grouped_pi = df[bowl_mask].groupby(['innings', 'phase'])['Bowling_PI']
    df.loc[bowl_mask, 'recalc_z_pi_bowl'] = (df.loc[bowl_mask, 'Bowling_PI'] - bowl_grouped_pi.transform('mean')) / bowl_grouped_pi.transform('std')

    bat_z_diff = np.nanmax(np.abs(df.loc[bat_mask, 'recalc_z_pi_bat'] - df.loc[bat_mask, 'batting_z_score']))
    bowl_z_diff = np.nanmax(np.abs(df.loc[bowl_mask, 'recalc_z_pi_bowl'] - df.loc[bowl_mask, 'bowling_z_score']))
    print(f"Max abs diff in Batting PI Z-score (Recalc vs Step 16): {bat_z_diff:.8e}")
    print(f"Max abs diff in Bowling PI Z-score (Recalc vs Step 16): {bowl_z_diff:.8e}")
    assert bat_z_diff < 1e-5, "Batting PI Z-scores do not match Step 16 baseline!"
    assert bowl_z_diff < 1e-5, "Bowling PI Z-scores do not match Step 16 baseline!"
    print(">> VERIFIED: Step 16 PI Z-scores reproduced with near-zero machine precision difference.")

    # 4. Independent Recalculation of Leverage Z-scores
    print("\n--- Auditing Expected Leverage Z-scores ---")
    df['recalc_z_lev_bat'] = np.nan
    bat_grouped_lev = df[bat_mask].groupby(['innings', 'phase'])['expected_leverage_pct']
    df.loc[bat_mask, 'recalc_z_lev_bat'] = (df.loc[bat_mask, 'expected_leverage_pct'] - bat_grouped_lev.transform('mean')) / bat_grouped_lev.transform('std')

    df['recalc_z_lev_bowl'] = np.nan
    bowl_grouped_lev = df[bowl_mask].groupby(['innings', 'phase'])['expected_leverage_pct']
    df.loc[bowl_mask, 'recalc_z_lev_bowl'] = (df.loc[bowl_mask, 'expected_leverage_pct'] - bowl_grouped_lev.transform('mean')) / bowl_grouped_lev.transform('std')

    # 5. Independent Recalculation of Candidates
    print("\n--- Recalculating Candidates 0, 1A, 1B, 2, and 3 ---")
    z_pi_bat = df.loc[bat_mask, 'recalc_z_pi_bat'].values
    z_lev_bat = df.loc[bat_mask, 'recalc_z_lev_bat'].values
    z_pi_bowl = df.loc[bowl_mask, 'recalc_z_pi_bowl'].values
    z_lev_bowl = df.loc[bowl_mask, 'recalc_z_lev_bowl'].values

    # Candidate 0 (Control)
    df.loc[bat_mask, 'recalc_hp_cand0_bat'] = z_pi_bat > 1.00
    df.loc[bowl_mask, 'recalc_hp_cand0_bowl'] = z_pi_bowl > 1.00

    # Candidate 1A (Additive 70/30)
    raw_1a_bat = 0.70 * z_pi_bat + 0.30 * z_lev_bat
    df.loc[bat_mask, 'recalc_raw_1a_bat'] = raw_1a_bat
    df.loc[bat_mask, 'recalc_z_1a_bat'] = df[bat_mask].groupby(['innings', 'phase'])['recalc_raw_1a_bat'].transform(standardize_series)
    df.loc[bat_mask, 'recalc_hp_cand1a_bat'] = df.loc[bat_mask, 'recalc_z_1a_bat'] > 1.00

    raw_1a_bowl = 0.70 * z_pi_bowl + 0.30 * z_lev_bowl
    df.loc[bowl_mask, 'recalc_raw_1a_bowl'] = raw_1a_bowl
    df.loc[bowl_mask, 'recalc_z_1a_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['recalc_raw_1a_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'recalc_hp_cand1a_bowl'] = df.loc[bowl_mask, 'recalc_z_1a_bowl'] > 1.00

    # Candidate 1B (Additive 50/50)
    raw_1b_bat = 0.50 * z_pi_bat + 0.50 * z_lev_bat
    df.loc[bat_mask, 'recalc_raw_1b_bat'] = raw_1b_bat
    df.loc[bat_mask, 'recalc_z_1b_bat'] = df[bat_mask].groupby(['innings', 'phase'])['recalc_raw_1b_bat'].transform(standardize_series)
    df.loc[bat_mask, 'recalc_hp_cand1b_bat'] = df.loc[bat_mask, 'recalc_z_1b_bat'] > 1.00

    raw_1b_bowl = 0.50 * z_pi_bowl + 0.50 * z_lev_bowl
    df.loc[bowl_mask, 'recalc_raw_1b_bowl'] = raw_1b_bowl
    df.loc[bowl_mask, 'recalc_z_1b_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['recalc_raw_1b_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'recalc_hp_cand1b_bowl'] = df.loc[bowl_mask, 'recalc_z_1b_bowl'] > 1.00

    # Candidate 2 (Multiplicative Gated: Phase x Innings standardized)
    g_lev_bat_50 = 1.0 + 0.50 * np.tanh(z_lev_bat)
    raw_2_bat = z_pi_bat * g_lev_bat_50
    df.loc[bat_mask, 'recalc_raw_2_bat'] = raw_2_bat
    df.loc[bat_mask, 'recalc_z_2_bat'] = df[bat_mask].groupby(['innings', 'phase'])['recalc_raw_2_bat'].transform(standardize_series)
    df.loc[bat_mask, 'recalc_hp_cand2_bat'] = df.loc[bat_mask, 'recalc_z_2_bat'] > 1.00

    g_lev_bowl_50 = 1.0 + 0.50 * np.tanh(z_lev_bowl)
    raw_2_bowl = z_pi_bowl * g_lev_bowl_50
    df.loc[bowl_mask, 'recalc_raw_2_bowl'] = raw_2_bowl
    df.loc[bowl_mask, 'recalc_z_2_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['recalc_raw_2_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'recalc_hp_cand2_bowl'] = df.loc[bowl_mask, 'recalc_z_2_bowl'] > 1.00

    # Alternative Candidate 2: Globally standardized (test standardization scope)
    df.loc[bat_mask, 'recalc_z_2_bat_global'] = standardize_series(pd.Series(raw_2_bat, index=df[bat_mask].index))
    df.loc[bat_mask, 'recalc_hp_cand2_bat_global'] = df.loc[bat_mask, 'recalc_z_2_bat_global'] > 1.00
    df.loc[bowl_mask, 'recalc_z_2_bowl_global'] = standardize_series(pd.Series(raw_2_bowl, index=df[bowl_mask].index))
    df.loc[bowl_mask, 'recalc_hp_cand2_bowl_global'] = df.loc[bowl_mask, 'recalc_z_2_bowl_global'] > 1.00

    # Candidate 3 (Convex Composite)
    pos_mag_bat = np.sqrt(np.maximum(0, z_pi_bat)**2 + np.maximum(0, z_lev_bat)**2)
    neg_mag_bat = np.sqrt(np.maximum(0, -z_pi_bat)**2 + np.maximum(0, -z_lev_bat)**2)
    raw_3_bat = pos_mag_bat - neg_mag_bat
    df.loc[bat_mask, 'recalc_raw_3_bat'] = raw_3_bat
    df.loc[bat_mask, 'recalc_z_3_bat'] = df[bat_mask].groupby(['innings', 'phase'])['recalc_raw_3_bat'].transform(standardize_series)
    df.loc[bat_mask, 'recalc_hp_cand3_bat'] = df.loc[bat_mask, 'recalc_z_3_bat'] > 1.00

    pos_mag_bowl = np.sqrt(np.maximum(0, z_pi_bowl)**2 + np.maximum(0, z_lev_bowl)**2)
    neg_mag_bowl = np.sqrt(np.maximum(0, -z_pi_bowl)**2 + np.maximum(0, -z_lev_bowl)**2)
    raw_3_bowl = pos_mag_bowl - neg_mag_bowl
    df.loc[bowl_mask, 'recalc_raw_3_bowl'] = raw_3_bowl
    df.loc[bowl_mask, 'recalc_z_3_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['recalc_raw_3_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'recalc_hp_cand3_bowl'] = df.loc[bowl_mask, 'recalc_z_3_bowl'] > 1.00

    # 6. Compare with Step 16.6 Parquet Outputs
    step16_6_parquet = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    print(f"\nLoading Step 16.6 classified deliveries from {step16_6_parquet}...")
    s16_6_df = pd.read_parquet(step16_6_parquet)

    checks = [
        ('hp_cand0_bat', 'recalc_hp_cand0_bat', bat_mask),
        ('hp_cand1a_bat', 'recalc_hp_cand1a_bat', bat_mask),
        ('hp_cand1b_bat', 'recalc_hp_cand1b_bat', bat_mask),
        ('hp_cand2_bat', 'recalc_hp_cand2_bat', bat_mask),
        ('hp_cand3_bat', 'recalc_hp_cand3_bat', bat_mask),
        ('hp_cand0_bowl', 'recalc_hp_cand0_bowl', bowl_mask),
        ('hp_cand1a_bowl', 'recalc_hp_cand1a_bowl', bowl_mask),
        ('hp_cand1b_bowl', 'recalc_hp_cand1b_bowl', bowl_mask),
        ('hp_cand2_bowl', 'recalc_hp_cand2_bowl', bowl_mask),
        ('hp_cand3_bowl', 'recalc_hp_cand3_bowl', bowl_mask),
    ]

    print("\n--- Verifying Exact Delivery-Level Concordance ---")
    verification_results = []
    for s16_col, recalc_col, mask in checks:
        s16_vals = s16_6_df.loc[mask, s16_col].values
        recalc_vals = df.loc[mask, recalc_col].values
        mismatches = np.sum(s16_vals != recalc_vals)
        total = mask.sum()
        pct_match = (1.0 - mismatches / total) * 100.0
        print(f"  {s16_col:16s} vs {recalc_col:22s}: Mismatches = {mismatches:5d} / {total:,} ({pct_match:.4f}% match)")
        verification_results.append({
            'candidate_col': s16_col,
            'total_evaluated': total,
            'step_16_6_hp_count': int(s16_vals.sum()),
            'recalculated_hp_count': int(recalc_vals.sum()),
            'mismatch_count': int(mismatches),
            'concordance_pct': round(pct_match, 4)
        })

    # 7. Analyze Global vs Phase x Innings Standardization for Candidate 2
    print("\n--- Candidate 2 Standardization Scope Analysis: Phase x Innings vs Global ---")
    glob_bat_hp = int(df.loc[bat_mask, 'recalc_hp_cand2_bat_global'].sum())
    pxi_bat_hp = int(df.loc[bat_mask, 'recalc_hp_cand2_bat'].sum())
    overlap_bat = int((df.loc[bat_mask, 'recalc_hp_cand2_bat'] & df.loc[bat_mask, 'recalc_hp_cand2_bat_global']).sum())
    print(f"Batting HP Deliveries: Phase x Innings = {pxi_bat_hp:,} ({(pxi_bat_hp/bat_mask.sum())*100:.2f}%), Global = {glob_bat_hp:,} ({(glob_bat_hp/bat_mask.sum())*100:.2f}%)")
    print(f"Batting Overlap: {overlap_bat:,} ({(overlap_bat/pxi_bat_hp)*100:.2f}% of PxI, {(overlap_bat/glob_bat_hp)*100:.2f}% of Global)")

    # Phase breakdown for Global vs PxI
    pxi_phase_dist = df[bat_mask].groupby('phase')['recalc_hp_cand2_bat'].mean() * 100
    glob_phase_dist = df[bat_mask].groupby('phase')['recalc_hp_cand2_bat_global'].mean() * 100
    print("\nBatting HP Capture by Phase (PxI vs Global):")
    for ph in ['PP', 'Middle', 'Death']:
        print(f"  {ph:6s}: PxI = {pxi_phase_dist[ph]:.2f}%, Global = {glob_phase_dist[ph]:.2f}%")

    # 8. Export Comparison Summary
    recalc_csv = OUTPUT_DIR / "recalculated_candidates_comparison.csv"
    pd.DataFrame(verification_results).to_csv(recalc_csv, index=False)
    print(f"\nSaved recalculation verification summary to {recalc_csv}")
    print(f"Total time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
