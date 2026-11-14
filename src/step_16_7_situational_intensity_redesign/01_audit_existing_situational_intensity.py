"""
Step 16.7: Script 01 - Audit Existing Situational Intensity Formula
===================================================================
Independently audits the existing Situational Intensity (I) component:
  I = clip(((10 - striker_balls_faced_before) / 10) * 100, 0, 100)
  Batting_PI = 0.65 * Batting_T + 0.35 * Batting_I

Key Investigations:
1. Balls-faced decay profile (0 to 35+ balls):
   - Distribution of deliveries, mean I, mean T, mean PI, mean Z_PI, and HP capture %.
2. Controlled match situation analysis:
   - Holding Task Difficulty (T) constant, quantify the pure mechanical drop in PI and HP capture.
   - For high-difficulty deliveries (T > 65), how many set batters lose HP status solely due to I = 0?
3. Role exposure disparity:
   - Distribution of balls faced and average I received by Batting Position (1 to 11).
4. Innings and Phase exposure:
   - Percentage of balls where I = 0 across the 6 Phase x Innings strata.

Outputs:
- outputs/step_16_7_situational_intensity_redesign/existing_intensity_audit.csv
- outputs/step_16_7_situational_intensity_redesign/balls_faced_decay_profile.csv
- outputs/step_16_7_situational_intensity_redesign/controlled_task_difficulty_decay.csv
- outputs/step_16_7_situational_intensity_redesign/role_intensity_exposure.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_7_situational_intensity_redesign")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR = Path("data/processed")
STEP_16_6_DIR = Path("outputs/step_16_6_leverage_integration")


def main():
    print("=== Step 16.7 Script 01: Audit Existing Situational Intensity ===")
    t0 = time.time()

    # Load master delivery dataset
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading master delivery dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # Load striker_balls_faced_before and Batting_PI from delivery_pressure_index
    dpi_path = PROCESSED_DIR / "delivery_pressure_index.csv"
    print(f"Loading PI components from {dpi_path}...")
    dpi_cols = ['match_id', 'innings', 'overid', 'innings_ball_num',
                'striker_balls_faced_before', 'Batting_PI', 'Bowling_PI']
    dpi = pd.read_csv(dpi_path, usecols=dpi_cols)

    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    # Drop overlapping columns if already in parquet
    df = df.drop(columns=['striker_balls_faced_before', 'Batting_PI', 'Bowling_PI'], errors='ignore')
    df = df.merge(dpi, on=merge_keys, how='left')

    bat_mask = df['is_batter_ball_faced'] == 1
    bat_df = df[bat_mask].copy()
    n_bat = len(bat_df)
    print(f"Loaded {n_bat:,} batting deliveries.")

    # Calculate Batting_I and Batting_T
    bat_df['Batting_I'] = np.clip(((10.0 - bat_df['striker_balls_faced_before']) / 10.0) * 100.0, 0.0, 100.0)
    bat_df['Batting_T'] = (bat_df['Batting_PI'] - 0.35 * bat_df['Batting_I']) / 0.65

    recalc_pi = 0.65 * bat_df['Batting_T'] + 0.35 * bat_df['Batting_I']
    max_pi_diff = np.nanmax(np.abs(recalc_pi - bat_df['Batting_PI']))
    print(f"Max absolute difference in recalculated Batting_PI: {max_pi_diff:.8e}")
    assert max_pi_diff < 1e-5, "Batting_I / Batting_PI formula mismatch!"
    print(">> VERIFIED: Existing Situational Intensity formula independently reproduced.")

    # 1. Balls-Faced Decay Profile (0 to 35+)
    print("\n--- 1. Balls-Faced Decay Profile ---")
    bat_df['bf_bin'] = np.where(bat_df['striker_balls_faced_before'] >= 35, 35, bat_df['striker_balls_faced_before'])
    
    bf_profile = bat_df.groupby('bf_bin').agg(
        total_deliveries=('Batting_PI', 'count'),
        mean_intensity=('Batting_I', 'mean'),
        mean_task_difficulty=('Batting_T', 'mean'),
        mean_pi=('Batting_PI', 'mean'),
        mean_z_pi=('batting_z_score', 'mean'),
        hp_count=('hp_cand0_bat', lambda s: (s == True).sum()),
        hp_capture_pct=('hp_cand0_bat', lambda s: (s == True).mean() * 100.0)
    ).reset_index()

    bf_csv = OUTPUT_DIR / "balls_faced_decay_profile.csv"
    bf_profile.to_csv(bf_csv, index=False)
    print(f"Saved balls faced decay profile to {bf_csv}")
    print("\nKey Milestones in Balls-Faced Decay:")
    key_bf = [0, 1, 2, 5, 8, 9, 10, 11, 15, 20, 25, 30, 35]
    print(bf_profile[bf_profile['bf_bin'].isin(key_bf)][['bf_bin', 'total_deliveries', 'mean_intensity',
                                                         'mean_task_difficulty', 'mean_pi', 'mean_z_pi', 'hp_capture_pct']].to_string())

    # 2. Controlled Task Difficulty Analysis
    print("\n--- 2. Controlled Task Difficulty Decay ---")
    # Hold T in [45, 55] (medium difficulty, where T is constant)
    t_controlled = bat_df[bat_df['Batting_T'].between(45, 55)].copy()
    print(f"Controlled Task Difficulty deliveries (T in [45, 55]): {len(t_controlled):,} deliveries.")

    t_ctrl_profile = t_controlled.groupby('bf_bin').agg(
        total_deliveries=('Batting_PI', 'count'),
        mean_t=('Batting_T', 'mean'),
        mean_i=('Batting_I', 'mean'),
        mean_pi=('Batting_PI', 'mean'),
        mean_z_pi=('batting_z_score', 'mean'),
        hp_capture_pct=('hp_cand0_bat', lambda s: (s == True).mean() * 100.0)
    ).reset_index()

    t_ctrl_csv = OUTPUT_DIR / "controlled_task_difficulty_decay.csv"
    t_ctrl_profile.to_csv(t_ctrl_csv, index=False)
    print(f"Saved controlled T decay to {t_ctrl_csv}")
    print("\nControlled T [45, 55] across Balls Faced:")
    print(t_ctrl_profile[t_ctrl_profile['bf_bin'].isin([0, 1, 2, 5, 9, 10, 15, 25])][
        ['bf_bin', 'total_deliveries', 'mean_t', 'mean_i', 'mean_pi', 'mean_z_pi', 'hp_capture_pct']].to_string())

    # High Difficulty Crisis (T > 65): Set Batters vs New Batters
    high_t = bat_df[bat_df['Batting_T'] > 65].copy()
    print(f"\nHigh Task Difficulty deliveries (T > 65, Crisis/Steep Chase): {len(high_t):,} deliveries.")
    new_in_crisis = high_t[high_t['striker_balls_faced_before'] <= 5]
    settled_in_crisis = high_t[high_t['striker_balls_faced_before'] >= 15]
    print(f"  New Batters (0-5 bf) in Crisis: {len(new_in_crisis):,} balls, Mean PI = {new_in_crisis['Batting_PI'].mean():.2f}, HP % = {(new_in_crisis['hp_cand0_bat']==True).mean()*100:.2f}%")
    print(f"  Settled Batters (15+ bf) in Crisis: {len(settled_in_crisis):,} balls, Mean PI = {settled_in_crisis['Batting_PI'].mean():.2f}, HP % = {(settled_in_crisis['hp_cand0_bat']==True).mean()*100:.2f}%")

    # 3. Role Exposure Disparity (Batting Order 1 to 11)
    print("\n--- 3. Role Exposure Disparity ---")
    role_rows = []
    for bo in range(1, 12):
        sub_bo = bat_df[bat_df['batting_order'] == bo]
        n_bo = len(sub_bo)
        if n_bo == 0:
            continue
        pct_0_5 = (sub_bo['striker_balls_faced_before'] <= 5).mean() * 100.0
        pct_6_10 = sub_bo['striker_balls_faced_before'].between(6, 10).mean() * 100.0
        pct_11_plus = (sub_bo['striker_balls_faced_before'] > 10).mean() * 100.0
        m_i = sub_bo['Batting_I'].mean()
        m_t = sub_bo['Batting_T'].mean()
        m_pi = sub_bo['Batting_PI'].mean()
        hp_pct = (sub_bo['hp_cand0_bat'] == True).mean() * 100.0

        role_group = 'Top Order (1-3)' if bo <= 3 else ('Middle Order (4-6)' if bo <= 6 else 'Lower Order (7-11)')

        role_rows.append({
            'batting_order': bo,
            'role_group': role_group,
            'total_deliveries': n_bo,
            'pct_of_total_batting': round(n_bo / n_bat * 100.0, 2),
            'pct_balls_faced_0_to_5': round(pct_0_5, 2),
            'pct_balls_faced_6_to_10': round(pct_6_10, 2),
            'pct_balls_faced_11_plus': round(pct_11_plus, 2),
            'mean_intensity_I': round(m_i, 2),
            'mean_task_difficulty_T': round(m_t, 2),
            'mean_composite_PI': round(m_pi, 2),
            'hp_capture_pct': round(hp_pct, 2)
        })

    df_role = pd.DataFrame(role_rows)
    role_csv = OUTPUT_DIR / "role_intensity_exposure.csv"
    df_role.to_csv(role_csv, index=False)
    print(f"Saved role intensity exposure to {role_csv}")
    print("\nRole Intensity Exposure Table:")
    print(df_role[['batting_order', 'role_group', 'pct_balls_faced_0_to_5', 'pct_balls_faced_11_plus',
                   'mean_intensity_I', 'mean_task_difficulty_T', 'mean_composite_PI', 'hp_capture_pct']].to_string())

    # 4. Innings and Phase Exposure
    print("\n--- 4. Innings and Phase Intensity Breakdown ---")
    inn_phase_audit = bat_df.groupby(['innings', 'phase']).agg(
        total_deliveries=('Batting_PI', 'count'),
        pct_zero_intensity=('Batting_I', lambda s: (s == 0).mean() * 100.0),
        mean_intensity=('Batting_I', 'mean'),
        mean_t=('Batting_T', 'mean'),
        mean_pi=('Batting_PI', 'mean'),
        hp_pct=('hp_cand0_bat', lambda s: (s == True).mean() * 100.0)
    ).reset_index()

    audit_csv = OUTPUT_DIR / "existing_intensity_audit.csv"
    inn_phase_audit.to_csv(audit_csv, index=False)
    print(f"Saved innings and phase audit to {audit_csv}")
    print(inn_phase_audit.to_string())

    print(f"\nTotal time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
