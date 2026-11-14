"""
Step 16.1: Independent Audit - Script 01
Verify Twelve Baselines & Z-Score Calculations
============================================================
Independently verifies:
1. Delivery population cleaning (233 excluded where innings==2 & runs_required<=0).
2. All 12 Phase x Innings baseline parameters (Batting: 6, Bowling: 6).
   - Delivery count, Mean, Std Dev, Median, Effective Cutoff (mean + 1.0*std),
     deliveries with Z > 1.0, and empirical capture %.
   - Compares ddof=1 vs ddof=0 conventions.
   - Compares with Step 16 frozen parameters and flags any discrepancy.
3. Delivery-level Z-score calculation and 18% capture claim verification.
   - Overall capture %
   - Phase capture %
   - Innings capture %
   - Group-level capture %

Exports:
- outputs/step_16_1_independent_audit/baseline_verification.csv
- outputs/step_16_1_independent_audit/zscore_calculation_verification.csv
- outputs/step_16_1_independent_audit/threshold_capture_verification.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
STEP16_OUT_DIR = Path("outputs/step_16_phase_relative_pressure")
AUDIT_OUT_DIR = Path("outputs/step_16_1_independent_audit")
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)

# Step 16 reported frozen lookup parameters for exact comparison
STEP16_REPORTED_FROZEN = {
    ('Batting', 1, 'PP'): {'count': 28533, 'mean': 29.7483, 'std': 16.0789, 'cutoff': 45.8272},
    ('Batting', 1, 'Middle'): {'count': 42638, 'mean': 27.2792, 'std': 17.2776, 'cutoff': 44.5568},
    ('Batting', 1, 'Death'): {'count': 23169, 'mean': 39.5031, 'std': 17.5706, 'cutoff': 57.0737},
    ('Batting', 2, 'PP'): {'count': 28504, 'mean': 40.2022, 'std': 16.2016, 'cutoff': 56.4038},
    ('Batting', 2, 'Middle'): {'count': 41400, 'mean': 38.2947, 'std': 22.1941, 'cutoff': 60.4888},
    ('Batting', 2, 'Death'): {'count': 16595, 'mean': 47.3564, 'std': 24.4665, 'cutoff': 71.8229},
    ('Bowling', 1, 'PP'): {'count': 28404, 'mean': 48.1985, 'std': 10.5552, 'cutoff': 58.7537},
    ('Bowling', 1, 'Middle'): {'count': 42528, 'mean': 40.4027, 'std': 13.7022, 'cutoff': 54.1049},
    ('Bowling', 1, 'Death'): {'count': 22980, 'mean': 24.6618, 'std': 10.9545, 'cutoff': 35.6163},
    ('Bowling', 2, 'PP'): {'count': 28392, 'mean': 51.8018, 'std': 11.1728, 'cutoff': 62.9746},
    ('Bowling', 2, 'Middle'): {'count': 41258, 'mean': 40.4192, 'std': 13.5980, 'cutoff': 54.0172},
    ('Bowling', 2, 'Death'): {'count': 16479, 'mean': 35.7190, 'std': 16.3216, 'cutoff': 52.0406},
}


def main():
    print("=== Step 16.1 Audit Script 01: Twelve Baselines & Z-Score Verification ===")

    # 1. Load delivery data
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    total_raw = len(raw_df)
    print(f"Total raw deliveries loaded: {total_raw:,}")

    # 2. Verify data cleaning
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    tail_count = tail_mask.sum()
    print(f"Excluded deliveries where innings==2 & runs_required<=0: {tail_count}")
    assert tail_count == 233, f"Expected exactly 233 excluded deliveries, found {tail_count}"

    df = raw_df[~tail_mask].copy()
    active_deliveries = len(df)
    print(f"Active clean deliveries: {active_deliveries:,}")
    assert active_deliveries == 188097, f"Expected 188,097 active deliveries, found {active_deliveries}"

    # 3. Verify subsets
    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    n_bat = len(bat_df)
    n_bowl = len(bowl_df)
    print(f"Batting balls faced: {n_bat:,} (Expected: 180,839)")
    print(f"Bowling legal balls: {n_bowl:,} (Expected: 180,041)")
    assert n_bat == 180839, f"Batting count mismatch: {n_bat}"
    assert n_bowl == 180041, f"Bowling count mismatch: {n_bowl}"

    # 4. Audit all 12 Baselines
    baseline_audit_rows = []
    phases = ['PP', 'Middle', 'Death']

    for disc, sub_df, pi_col in [('Batting', bat_df, 'Batting_PI'), ('Bowling', bowl_df, 'Bowling_PI')]:
        for inn in [1, 2]:
            for ph in phases:
                group_mask = (sub_df['innings'] == inn) & (sub_df['phase'] == ph)
                vals = sub_df.loc[group_mask, pi_col].dropna()
                
                n_count = len(vals)
                mean_val = vals.mean()
                std_sample = vals.std(ddof=1)
                std_pop = vals.std(ddof=0)
                median_val = vals.median()
                
                cutoff_sample = mean_val + 1.0 * std_sample
                cutoff_pop = mean_val + 1.0 * std_pop
                
                hp_deliveries = (vals > cutoff_sample).sum()
                hp_pct = (hp_deliveries / n_count) * 100.0 if n_count > 0 else 0.0

                # Compare against Step 16 reported values
                rep = STEP16_REPORTED_FROZEN.get((disc, inn, ph), {})
                rep_count = rep.get('count', np.nan)
                rep_mean = rep.get('mean', np.nan)
                rep_std = rep.get('std', np.nan)
                rep_cutoff = rep.get('cutoff', np.nan)

                diff_count = n_count - rep_count
                diff_mean = mean_val - rep_mean
                diff_std = std_sample - rep_std
                diff_cutoff = cutoff_sample - rep_cutoff

                status = 'VERIFIED'
                if abs(diff_count) > 0 or abs(diff_mean) > 1e-4 or abs(diff_std) > 1e-4 or abs(diff_cutoff) > 1e-4:
                    status = 'DISCREPANCY'

                baseline_audit_rows.append({
                    'discipline': disc,
                    'innings': inn,
                    'phase': ph,
                    'audit_count': n_count,
                    'step16_count': rep_count,
                    'count_diff': diff_count,
                    'audit_mean': round(mean_val, 4),
                    'step16_mean': rep_mean,
                    'mean_diff': round(diff_mean, 6),
                    'audit_std_sample_ddof1': round(std_sample, 4),
                    'audit_std_pop_ddof0': round(std_pop, 4),
                    'step16_std': rep_std,
                    'std_diff': round(diff_std, 6),
                    'audit_median': round(median_val, 4),
                    'audit_cutoff': round(cutoff_sample, 4),
                    'step16_cutoff': rep_cutoff,
                    'cutoff_diff': round(diff_cutoff, 6),
                    'hp_deliveries_gt_cutoff': hp_deliveries,
                    'hp_capture_pct': round(hp_pct, 2),
                    'verification_status': status
                })

    baseline_audit_df = pd.DataFrame(baseline_audit_rows)
    out_b_path = AUDIT_OUT_DIR / "baseline_verification.csv"
    baseline_audit_df.to_csv(out_b_path, index=False)
    print(f"Saved baseline verification to {out_b_path}")

    # 5. Calculate and Verify Z-Scores at Delivery Level
    print("\nCalculating delivery-level Z-scores...")
    # Batting Z-scores
    bat_grouped = bat_df.groupby(['innings', 'phase'])['Batting_PI']
    bat_means = bat_grouped.transform('mean')
    bat_stds = bat_grouped.transform('std')
    bat_df['z_score'] = (bat_df['Batting_PI'] - bat_means) / bat_stds
    bat_df['is_hp_z1'] = (bat_df['z_score'] > 1.0).astype(int)

    # Bowling Z-scores
    bowl_grouped = bowl_df.groupby(['innings', 'phase'])['Bowling_PI']
    bowl_means = bowl_grouped.transform('mean')
    bowl_stds = bowl_grouped.transform('std')
    bowl_df['z_score'] = (bowl_df['Bowling_PI'] - bowl_means) / bowl_stds
    bowl_df['is_hp_z1'] = (bowl_df['z_score'] > 1.0).astype(int)

    # Check Total Capture
    total_bat_hp = bat_df['is_hp_z1'].sum()
    pct_bat_hp = (total_bat_hp / n_bat) * 100.0

    total_bowl_hp = bowl_df['is_hp_z1'].sum()
    pct_bowl_hp = (total_bowl_hp / n_bowl) * 100.0

    print(f"\nAudit Batting High Pressure Balls (Z > 1.0): {total_bat_hp:,} / {n_bat:,} ({pct_bat_hp:.2f}%)")
    print(f"  Step 16 Reported Batting: 32,708 (18.09%) -> Diff: {total_bat_hp - 32708}")

    print(f"Audit Bowling High Pressure Balls (Z > 1.0): {total_bowl_hp:,} / {n_bowl:,} ({pct_bowl_hp:.2f}%)")
    print(f"  Step 16 Reported Bowling: 31,550 (17.52%) -> Diff: {total_bowl_hp - 31550}")

    # 6. Verify Capture Rates by Phase and Innings
    capture_audit_rows = []

    # Batting breakdowns
    for ph in phases:
        sub = bat_df[bat_df['phase'] == ph]
        hp_sub = sub['is_hp_z1'].sum()
        pct_sub = (hp_sub / len(sub)) * 100.0
        share_sub = (hp_sub / total_bat_hp) * 100.0
        capture_audit_rows.append({
            'discipline': 'Batting',
            'dimension': 'Phase',
            'group': ph,
            'total_balls': len(sub),
            'hp_balls': hp_sub,
            'capture_rate_pct': round(pct_sub, 2),
            'hp_share_pct': round(share_sub, 2)
        })

    for inn in [1, 2]:
        sub = bat_df[bat_df['innings'] == inn]
        hp_sub = sub['is_hp_z1'].sum()
        pct_sub = (hp_sub / len(sub)) * 100.0
        share_sub = (hp_sub / total_bat_hp) * 100.0
        capture_audit_rows.append({
            'discipline': 'Batting',
            'dimension': 'Innings',
            'group': f'Innings {inn}',
            'total_balls': len(sub),
            'hp_balls': hp_sub,
            'capture_rate_pct': round(pct_sub, 2),
            'hp_share_pct': round(share_sub, 2)
        })

    # Bowling breakdowns
    for ph in phases:
        sub = bowl_df[bowl_df['phase'] == ph]
        hp_sub = sub['is_hp_z1'].sum()
        pct_sub = (hp_sub / len(sub)) * 100.0
        share_sub = (hp_sub / total_bowl_hp) * 100.0
        capture_audit_rows.append({
            'discipline': 'Bowling',
            'dimension': 'Phase',
            'group': ph,
            'total_balls': len(sub),
            'hp_balls': hp_sub,
            'capture_rate_pct': round(pct_sub, 2),
            'hp_share_pct': round(share_sub, 2)
        })

    for inn in [1, 2]:
        sub = bowl_df[bowl_df['innings'] == inn]
        hp_sub = sub['is_hp_z1'].sum()
        pct_sub = (hp_sub / len(sub)) * 100.0
        share_sub = (hp_sub / total_bowl_hp) * 100.0
        capture_audit_rows.append({
            'discipline': 'Bowling',
            'dimension': 'Innings',
            'group': f'Innings {inn}',
            'total_balls': len(sub),
            'hp_balls': hp_sub,
            'capture_rate_pct': round(pct_sub, 2),
            'hp_share_pct': round(share_sub, 2)
        })

    capture_audit_df = pd.DataFrame(capture_audit_rows)
    out_c_path = AUDIT_OUT_DIR / "threshold_capture_verification.csv"
    capture_audit_df.to_csv(out_c_path, index=False)
    print(f"Saved threshold capture verification to {out_c_path}")

    # 7. Export Delivery-level Verification Sample
    # Verify exact traceability: match_id, innings, overid, delivery_ball, PI, z_score, is_hp_z1
    sample_cols = ['match_id', 'innings', 'overid', 'innings_ball_num', 'phase', 'striker_id', 'striker_name', 'Batting_PI', 'z_score', 'is_hp_z1']
    sample_bat = bat_df[sample_cols].head(50).copy()
    sample_bat = sample_bat.rename(columns={'striker_id': 'player_id', 'striker_name': 'player_name', 'Batting_PI': 'PI'})
    sample_bat['discipline'] = 'Batting'

    sample_bowl_cols = ['match_id', 'innings', 'overid', 'innings_ball_num', 'phase', 'bowler_id', 'bowler_name', 'Bowling_PI', 'z_score', 'is_hp_z1']
    sample_bowl = bowl_df[sample_bowl_cols].head(50).copy()
    sample_bowl = sample_bowl.rename(columns={'bowler_id': 'player_id', 'bowler_name': 'player_name', 'Bowling_PI': 'PI'})
    sample_bowl['discipline'] = 'Bowling'

    sample_z = pd.concat([sample_bat, sample_bowl], ignore_index=True)
    out_z_path = AUDIT_OUT_DIR / "zscore_calculation_verification.csv"
    sample_z.to_csv(out_z_path, index=False)
    print(f"Saved zscore calculation verification sample to {out_z_path}")


if __name__ == "__main__":
    main()
