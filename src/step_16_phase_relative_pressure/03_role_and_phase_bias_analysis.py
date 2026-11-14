"""
Step 16: Phase-Relative Pressure Classification - Script 03
Role & Phase Bias Reduction Analysis
============================================================
Investigates whether phase-relative Z-score classification reduces:
1. Batting Finisher Bias:
   - Evaluates Top Order (1-3), Middle Order (4-6), Lower Order (7-11)
   - Measures within-role capture rate (% of role's deliveries that are HP)
   - Measures share of all HP deliveries by role
2. Bowling Death / Powerplay Imbalance:
   - Evaluates Powerplay, Middle, and Death overs
   - Measures phase capture rate (% of phase's own deliveries that are HP)
   - Measures phase share (% of total HP deliveries)

Compares Baseline PI > 60.0 against candidate Z-score thresholds across:
- Approach A (Phase-only standard & robust Z)
- Approach B (Phase x Innings standard & robust Z)

Exports:
- outputs/step_16_phase_relative_pressure/batting_role_exposure_analysis.csv
- outputs/step_16_phase_relative_pressure/bowling_phase_exposure_analysis.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path("data")
PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_phase_relative_pressure")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_zscores(df: pd.DataFrame, group_cols: list, value_col: str, prefix: str):
    """Computes standard and robust Z-scores grouped by group_cols."""
    grouped = df.groupby(group_cols)[value_col]
    means = grouped.transform('mean')
    stds = grouped.transform('std')
    stds_safe = np.where(stds > 1e-6, stds, np.nan)
    df[f'{prefix}_z_std'] = (df[value_col] - means) / stds_safe

    medians = grouped.transform('median')
    def get_mad(s):
        med = s.median()
        return 1.4826 * (s - med).abs().median()
    mads = grouped.transform(get_mad)
    mads_safe = np.where(mads > 1e-6, mads, np.nan)
    df[f'{prefix}_z_robust'] = (df[value_col] - medians) / mads_safe
    return df


def main():
    print("--- Step 16: Role & Phase Bias Reduction Analysis ---")

    # 1. Load delivery data
    df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    
    # 2. Exclude Innings 2 deliveries where runs_required <= 0
    clean_mask = ~((df['innings'] == 2) & (df['runs_required'] <= 0))
    df = df[clean_mask].copy()

    # 3. Batting dataset (balls faced)
    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    
    # Define Batting Roles
    def get_batting_role(order):
        if order in [1, 2, 3]:
            return 'Top Order (1-3)'
        elif order in [4, 5, 6]:
            return 'Middle Order (4-6)'
        else:
            return 'Lower Order (7-11)'

    bat_df['batting_role'] = bat_df['batting_order'].apply(get_batting_role)

    # Compute Z-scores for Batting
    bat_df = compute_zscores(bat_df, ['phase'], 'Batting_PI', 'appA')
    bat_df = compute_zscores(bat_df, ['innings', 'phase'], 'Batting_PI', 'appB')

    # 4. Bowling dataset (legal balls)
    bowl_df = df[df['is_legal_ball'] == 1].copy()
    bowl_df = compute_zscores(bowl_df, ['phase'], 'Bowling_PI', 'appA')
    bowl_df = compute_zscores(bowl_df, ['innings', 'phase'], 'Bowling_PI', 'appB')

    # Total counts
    total_bat_by_role = bat_df['batting_role'].value_counts().to_dict()
    total_bowl_by_phase = bowl_df['phase'].value_counts().to_dict()

    print("Total Batting Balls by Role:", total_bat_by_role)
    print("Total Bowling Balls by Phase:", total_bowl_by_phase)

    # 5. Build Batting Role Exposure Table
    batting_models = [
        ('Baseline', 'PI > 60.0', bat_df['Batting_PI'] > 60.0),
        # Approach A Standard Z
        ('Approach A (Phase-only)', 'Z > 0.0', bat_df['appA_z_std'] > 0.0),
        ('Approach A (Phase-only)', 'Z > 0.5', bat_df['appA_z_std'] > 0.5),
        ('Approach A (Phase-only)', 'Z > 1.0', bat_df['appA_z_std'] > 1.0),
        ('Approach A (Phase-only)', 'Z > 1.5', bat_df['appA_z_std'] > 1.5),
        # Approach A Robust Z
        ('Approach A (Phase-only)', 'Z_robust > 0.0', bat_df['appA_z_robust'] > 0.0),
        ('Approach A (Phase-only)', 'Z_robust > 0.5', bat_df['appA_z_robust'] > 0.5),
        ('Approach A (Phase-only)', 'Z_robust > 1.0', bat_df['appA_z_robust'] > 1.0),
        ('Approach A (Phase-only)', 'Z_robust > 1.5', bat_df['appA_z_robust'] > 1.5),
        # Approach B Standard Z
        ('Approach B (Phase x Innings)', 'Z > 0.0', bat_df['appB_z_std'] > 0.0),
        ('Approach B (Phase x Innings)', 'Z > 0.5', bat_df['appB_z_std'] > 0.5),
        ('Approach B (Phase x Innings)', 'Z > 1.0', bat_df['appB_z_std'] > 1.0),
        ('Approach B (Phase x Innings)', 'Z > 1.5', bat_df['appB_z_std'] > 1.5),
        # Approach B Robust Z
        ('Approach B (Phase x Innings)', 'Z_robust > 0.0', bat_df['appB_z_robust'] > 0.0),
        ('Approach B (Phase x Innings)', 'Z_robust > 0.5', bat_df['appB_z_robust'] > 0.5),
        ('Approach B (Phase x Innings)', 'Z_robust > 1.0', bat_df['appB_z_robust'] > 1.0),
        ('Approach B (Phase x Innings)', 'Z_robust > 1.5', bat_df['appB_z_robust'] > 1.5),
    ]

    bat_role_rows = []
    roles = ['Top Order (1-3)', 'Middle Order (4-6)', 'Lower Order (7-11)']

    for approach, thresh_label, mask in batting_models:
        total_hp_balls = mask.sum()
        for r in roles:
            r_total_balls = total_bat_by_role[r]
            r_hp_mask = mask & (bat_df['batting_role'] == r)
            r_hp_balls = r_hp_mask.sum()
            
            # Capture rate: % of this role's balls that are classified as HP
            capture_rate = round((r_hp_balls / r_total_balls) * 100.0, 2)
            # Share: % of all HP balls that belong to this role
            hp_share = round((r_hp_balls / total_hp_balls) * 100.0, 2) if total_hp_balls > 0 else 0.0
            
            # Natural share of this role in the overall dataset
            natural_share = round((r_total_balls / len(bat_df)) * 100.0, 2)
            # Representation index: hp_share / natural_share
            rep_index = round(hp_share / natural_share, 3) if natural_share > 0 else 0.0

            bat_role_rows.append({
                'grouping_approach': approach,
                'threshold_name': thresh_label,
                'batting_role': r,
                'total_deliveries_in_role': r_total_balls,
                'natural_share_pct': natural_share,
                'hp_deliveries': r_hp_balls,
                'role_capture_rate_pct': capture_rate,
                'total_hp_deliveries_model': total_hp_balls,
                'hp_deliveries_share_pct': hp_share,
                'representation_index': rep_index
            })

    bat_role_df = pd.DataFrame(bat_role_rows)
    bat_role_csv = OUTPUT_DIR / "batting_role_exposure_analysis.csv"
    bat_role_df.to_csv(bat_role_csv, index=False)
    print(f"Saved batting role exposure analysis to {bat_role_csv}")

    # 6. Build Bowling Phase Exposure Table
    bowling_models = [
        ('Baseline', 'PI > 60.0', bowl_df['Bowling_PI'] > 60.0),
        # Approach A Standard Z
        ('Approach A (Phase-only)', 'Z > 0.0', bowl_df['appA_z_std'] > 0.0),
        ('Approach A (Phase-only)', 'Z > 0.5', bowl_df['appA_z_std'] > 0.5),
        ('Approach A (Phase-only)', 'Z > 1.0', bowl_df['appA_z_std'] > 1.0),
        ('Approach A (Phase-only)', 'Z > 1.5', bowl_df['appA_z_std'] > 1.5),
        # Approach A Robust Z
        ('Approach A (Phase-only)', 'Z_robust > 0.0', bowl_df['appA_z_robust'] > 0.0),
        ('Approach A (Phase-only)', 'Z_robust > 0.5', bowl_df['appA_z_robust'] > 0.5),
        ('Approach A (Phase-only)', 'Z_robust > 1.0', bowl_df['appA_z_robust'] > 1.0),
        ('Approach A (Phase-only)', 'Z_robust > 1.5', bowl_df['appA_z_robust'] > 1.5),
        # Approach B Standard Z
        ('Approach B (Phase x Innings)', 'Z > 0.0', bowl_df['appB_z_std'] > 0.0),
        ('Approach B (Phase x Innings)', 'Z > 0.5', bowl_df['appB_z_std'] > 0.5),
        ('Approach B (Phase x Innings)', 'Z > 1.0', bowl_df['appB_z_std'] > 1.0),
        ('Approach B (Phase x Innings)', 'Z > 1.5', bowl_df['appB_z_std'] > 1.5),
        # Approach B Robust Z
        ('Approach B (Phase x Innings)', 'Z_robust > 0.0', bowl_df['appB_z_robust'] > 0.0),
        ('Approach B (Phase x Innings)', 'Z_robust > 0.5', bowl_df['appB_z_robust'] > 0.5),
        ('Approach B (Phase x Innings)', 'Z_robust > 1.0', bowl_df['appB_z_robust'] > 1.0),
        ('Approach B (Phase x Innings)', 'Z_robust > 1.5', bowl_df['appB_z_robust'] > 1.5),
    ]

    bowl_phase_rows = []
    phases = ['PP', 'Middle', 'Death']

    for approach, thresh_label, mask in bowling_models:
        total_hp_balls = mask.sum()
        for ph in phases:
            ph_total_balls = total_bowl_by_phase[ph]
            ph_hp_mask = mask & (bowl_df['phase'] == ph)
            ph_hp_balls = ph_hp_mask.sum()
            
            # Capture rate: % of this phase's legal balls classified as HP
            capture_rate = round((ph_hp_balls / ph_total_balls) * 100.0, 2)
            # Share: % of all HP legal balls that belong to this phase
            hp_share = round((ph_hp_balls / total_hp_balls) * 100.0, 2) if total_hp_balls > 0 else 0.0
            
            natural_share = round((ph_total_balls / len(bowl_df)) * 100.0, 2)
            rep_index = round(hp_share / natural_share, 3) if natural_share > 0 else 0.0

            bowl_phase_rows.append({
                'grouping_approach': approach,
                'threshold_name': thresh_label,
                'phase': ph,
                'total_deliveries_in_phase': ph_total_balls,
                'natural_share_pct': natural_share,
                'hp_deliveries': ph_hp_balls,
                'phase_capture_rate_pct': capture_rate,
                'total_hp_deliveries_model': total_hp_balls,
                'hp_deliveries_share_pct': hp_share,
                'representation_index': rep_index
            })

    bowl_phase_df = pd.DataFrame(bowl_phase_rows)
    bowl_phase_csv = OUTPUT_DIR / "bowling_phase_exposure_analysis.csv"
    bowl_phase_df.to_csv(bowl_phase_csv, index=False)
    print(f"Saved bowling phase exposure analysis to {bowl_phase_csv}")


if __name__ == "__main__":
    main()
