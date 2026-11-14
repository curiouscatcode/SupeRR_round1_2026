"""
Step 16.6: Script 02 - Develop and Standardize Experimental PI Candidates
========================================================================
Constructs four defensible integration candidates combining Pressure Index (PI)
and Expected Delivery Leverage, all standardized to mean 0, std 1 within
Phase x Innings strata so that threshold Z > 1.0 remains universally calibrated:

1. Candidate 0 (Control):
   - Original Step 16 Phase x Innings PI Z-score (Z_PI)
   - High Pressure: Z_PI > 1.00

2. Candidate 1A (Additive Conservative - 70% PI / 30% Leverage):
   - Combines task difficulty with secondary outcome consequence
   - Raw = 0.70 * Z_PI + 0.30 * Z_Lev
   - Standardized Z_1A > 1.00

3. Candidate 1B (Additive Balanced - 50% PI / 50% Leverage):
   - Co-equal weighting of difficulty and consequence
   - Raw = 0.50 * Z_PI + 0.50 * Z_Lev
   - Standardized Z_1B > 1.00

4. Candidate 2 (Multiplicative / Gated Interaction):
   - Leverage acts as a consequence multiplier on physical task difficulty
   - Gating factor g(Z_Lev) = 1.0 + 0.50 * tanh(Z_Lev) (bounded [0.5, 1.5])
   - Raw = Z_PI * g(Z_Lev)
   - Standardized Z_2 > 1.00

5. Candidate 3 (Bivariate Convex Composite / Dual Focus):
   - Requires simultaneous elevation in both difficulty and consequence
   - Raw = sqrt(max(0, Z_PI)^2 + max(0, Z_Lev)^2) - sqrt(max(0, -Z_PI)^2 + max(0, -Z_Lev)^2)
   - Standardized Z_3 > 1.00

Outputs:
- outputs/step_16_6_leverage_integration/delivery_candidates_classified.parquet
- outputs/step_16_6_leverage_integration/candidates_summary_metrics.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_6_leverage_integration")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STEP_16_5_DIR = Path("outputs/step_16_5_wpa_investigation")


def standardize_series(series):
    s_std = series.std()
    if s_std == 0 or np.isnan(s_std):
        return series - series.mean()
    return (series - series.mean()) / s_std


def main():
    print("=== Step 16.6 Script 02: Develop Experimental PI Candidates ===")
    t0 = time.time()

    parquet_path = STEP_16_5_DIR / "delivery_wpa_leverage.parquet"
    print(f"Loading master delivery dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    n_deliv = len(df)
    print(f"Loaded {n_deliv:,} deliveries.")

    # 1. Compute Phase x Innings Z-scores for Expected Leverage
    print("\nComputing Phase x Innings Z-scores for Expected Delivery Leverage...")
    # Batting Z-scores
    bat_mask = df['is_batter_ball_faced'] == 1
    df['lev_z_score_bat'] = np.nan
    bat_grouped_lev = df[bat_mask].groupby(['innings', 'phase'])['expected_leverage_pct']
    df.loc[bat_mask, 'lev_z_score_bat'] = (df.loc[bat_mask, 'expected_leverage_pct'] - bat_grouped_lev.transform('mean')) / bat_grouped_lev.transform('std')

    # Bowling Z-scores
    bowl_mask = df['is_legal_ball'] == 1
    df['lev_z_score_bowl'] = np.nan
    bowl_grouped_lev = df[bowl_mask].groupby(['innings', 'phase'])['expected_leverage_pct']
    df.loc[bowl_mask, 'lev_z_score_bowl'] = (df.loc[bowl_mask, 'expected_leverage_pct'] - bowl_grouped_lev.transform('mean')) / bowl_grouped_lev.transform('std')

    # 2. Build Experimental Candidates for Batting
    print("\nConstructing Batting Experimental Candidates...")
    z_pi_bat = df.loc[bat_mask, 'batting_z_score'].values
    z_lev_bat = df.loc[bat_mask, 'lev_z_score_bat'].values

    # Candidate 0 (Control)
    df.loc[bat_mask, 'z_cand0_bat'] = z_pi_bat
    df.loc[bat_mask, 'hp_cand0_bat'] = z_pi_bat > 1.00

    # Candidate 1A: Additive 70/30
    raw_1a_bat = 0.70 * z_pi_bat + 0.30 * z_lev_bat
    df.loc[bat_mask, 'raw_1a_bat'] = raw_1a_bat
    # Group-wise standardizing by (innings, phase)
    df['z_cand1a_bat'] = np.nan
    df.loc[bat_mask, 'z_cand1a_bat'] = df[bat_mask].groupby(['innings', 'phase'])['raw_1a_bat'].transform(standardize_series)
    df.loc[bat_mask, 'hp_cand1a_bat'] = df.loc[bat_mask, 'z_cand1a_bat'] > 1.00

    # Candidate 1B: Additive 50/50
    raw_1b_bat = 0.50 * z_pi_bat + 0.50 * z_lev_bat
    df.loc[bat_mask, 'raw_1b_bat'] = raw_1b_bat
    df['z_cand1b_bat'] = np.nan
    df.loc[bat_mask, 'z_cand1b_bat'] = df[bat_mask].groupby(['innings', 'phase'])['raw_1b_bat'].transform(standardize_series)
    df.loc[bat_mask, 'hp_cand1b_bat'] = df.loc[bat_mask, 'z_cand1b_bat'] > 1.00

    # Candidate 2: Multiplicative Gated Interaction
    # g(Z_Lev) = 1.0 + 0.50 * tanh(Z_Lev)
    g_lev_bat = 1.0 + 0.50 * np.tanh(z_lev_bat)
    raw_2_bat = z_pi_bat * g_lev_bat
    df.loc[bat_mask, 'raw_2_bat'] = raw_2_bat
    df['z_cand2_bat'] = np.nan
    df.loc[bat_mask, 'z_cand2_bat'] = df[bat_mask].groupby(['innings', 'phase'])['raw_2_bat'].transform(standardize_series)
    df.loc[bat_mask, 'hp_cand2_bat'] = df.loc[bat_mask, 'z_cand2_bat'] > 1.00

    # Candidate 3: Bivariate Convex Composite
    pos_mag_bat = np.sqrt(np.maximum(0, z_pi_bat)**2 + np.maximum(0, z_lev_bat)**2)
    neg_mag_bat = np.sqrt(np.maximum(0, -z_pi_bat)**2 + np.maximum(0, -z_lev_bat)**2)
    raw_3_bat = pos_mag_bat - neg_mag_bat
    df.loc[bat_mask, 'raw_3_bat'] = raw_3_bat
    df['z_cand3_bat'] = np.nan
    df.loc[bat_mask, 'z_cand3_bat'] = df[bat_mask].groupby(['innings', 'phase'])['raw_3_bat'].transform(standardize_series)
    df.loc[bat_mask, 'hp_cand3_bat'] = df.loc[bat_mask, 'z_cand3_bat'] > 1.00

    # 3. Build Experimental Candidates for Bowling
    print("Constructing Bowling Experimental Candidates...")
    z_pi_bowl = df.loc[bowl_mask, 'bowling_z_score'].values
    z_lev_bowl = df.loc[bowl_mask, 'lev_z_score_bowl'].values

    # Candidate 0 (Control)
    df.loc[bowl_mask, 'z_cand0_bowl'] = z_pi_bowl
    df.loc[bowl_mask, 'hp_cand0_bowl'] = z_pi_bowl > 1.00

    # Candidate 1A: Additive 70/30
    raw_1a_bowl = 0.70 * z_pi_bowl + 0.30 * z_lev_bowl
    df.loc[bowl_mask, 'raw_1a_bowl'] = raw_1a_bowl
    df['z_cand1a_bowl'] = np.nan
    df.loc[bowl_mask, 'z_cand1a_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['raw_1a_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'hp_cand1a_bowl'] = df.loc[bowl_mask, 'z_cand1a_bowl'] > 1.00

    # Candidate 1B: Additive 50/50
    raw_1b_bowl = 0.50 * z_pi_bowl + 0.50 * z_lev_bowl
    df.loc[bowl_mask, 'raw_1b_bowl'] = raw_1b_bowl
    df['z_cand1b_bowl'] = np.nan
    df.loc[bowl_mask, 'z_cand1b_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['raw_1b_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'hp_cand1b_bowl'] = df.loc[bowl_mask, 'z_cand1b_bowl'] > 1.00

    # Candidate 2: Multiplicative Gated Interaction
    g_lev_bowl = 1.0 + 0.50 * np.tanh(z_lev_bowl)
    raw_2_bowl = z_pi_bowl * g_lev_bowl
    df.loc[bowl_mask, 'raw_2_bowl'] = raw_2_bowl
    df['z_cand2_bowl'] = np.nan
    df.loc[bowl_mask, 'z_cand2_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['raw_2_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'hp_cand2_bowl'] = df.loc[bowl_mask, 'z_cand2_bowl'] > 1.00

    # Candidate 3: Bivariate Convex Composite
    pos_mag_bowl = np.sqrt(np.maximum(0, z_pi_bowl)**2 + np.maximum(0, z_lev_bowl)**2)
    neg_mag_bowl = np.sqrt(np.maximum(0, -z_pi_bowl)**2 + np.maximum(0, -z_lev_bowl)**2)
    raw_3_bowl = pos_mag_bowl - neg_mag_bowl
    df.loc[bowl_mask, 'raw_3_bowl'] = raw_3_bowl
    df['z_cand3_bowl'] = np.nan
    df.loc[bowl_mask, 'z_cand3_bowl'] = df[bowl_mask].groupby(['innings', 'phase'])['raw_3_bowl'].transform(standardize_series)
    df.loc[bowl_mask, 'hp_cand3_bowl'] = df.loc[bowl_mask, 'z_cand3_bowl'] > 1.00

    # 4. Generate Candidate Summary Metrics
    print("\nEvaluating Candidate Summary Metrics across Population...")
    summary_rows = []

    candidates = [
        ('Candidate 0 (Control)', 'hp_cand0_bat', 'z_cand0_bat', 'hp_cand0_bowl', 'z_cand0_bowl', 'Frozen Step 16 Phase x Innings Z-score (Z_PI > 1.0)'),
        ('Candidate 1A (Additive 70/30)', 'hp_cand1a_bat', 'z_cand1a_bat', 'hp_cand1a_bowl', 'z_cand1a_bowl', '70% Task Difficulty + 30% Consequence (Standardized Z > 1.0)'),
        ('Candidate 1B (Additive 50/50)', 'hp_cand1b_bat', 'z_cand1b_bat', 'hp_cand1b_bowl', 'z_cand1b_bowl', '50% Task Difficulty + 50% Consequence (Standardized Z > 1.0)'),
        ('Candidate 2 (Multiplicative Gated)', 'hp_cand2_bat', 'z_cand2_bat', 'hp_cand2_bowl', 'z_cand2_bowl', 'Difficulty scaled by tanh(Leverage) Gating factor (Standardized Z > 1.0)'),
        ('Candidate 3 (Convex Composite)', 'hp_cand3_bat', 'z_cand3_bat', 'hp_cand3_bowl', 'z_cand3_bowl', 'Simultaneous Dual-Elevation in Difficulty & Consequence (Standardized Z > 1.0)')
    ]

    for c_name, hp_bat_col, z_bat_col, hp_bowl_col, z_bowl_col, desc in candidates:
        n_bat_hp = int(df.loc[bat_mask, hp_bat_col].sum())
        pct_bat_hp = (n_bat_hp / bat_mask.sum()) * 100.0

        n_bowl_hp = int(df.loc[bowl_mask, hp_bowl_col].sum())
        pct_bowl_hp = (n_bowl_hp / bowl_mask.sum()) * 100.0

        # Mean Expected Leverage within HP deliveries
        m_lev_bat_hp = df.loc[bat_mask & df[hp_bat_col], 'expected_leverage_pct'].mean()
        m_lev_bowl_hp = df.loc[bowl_mask & df[hp_bowl_col], 'expected_leverage_pct'].mean()

        # Mean PI within HP deliveries
        m_pi_bat_hp = df.loc[bat_mask & df[hp_bat_col], 'Batting_PI'].mean()
        m_pi_bowl_hp = df.loc[bowl_mask & df[hp_bowl_col], 'Bowling_PI'].mean()

        # Overlap with Control HP
        ov_bat = (df.loc[bat_mask, 'hp_cand0_bat'] & df.loc[bat_mask, hp_bat_col]).sum()
        ov_bat_pct = (ov_bat / max(1, df.loc[bat_mask, 'hp_cand0_bat'].sum())) * 100.0

        ov_bowl = (df.loc[bowl_mask, 'hp_cand0_bowl'] & df.loc[bowl_mask, hp_bowl_col]).sum()
        ov_bowl_pct = (ov_bowl / max(1, df.loc[bowl_mask, 'hp_cand0_bowl'].sum())) * 100.0

        summary_rows.append({
            'candidate': c_name,
            'description': desc,
            'batting_hp_deliveries': n_bat_hp,
            'batting_hp_capture_pct': round(pct_bat_hp, 2),
            'batting_hp_mean_leverage': round(m_lev_bat_hp, 3),
            'batting_hp_mean_pi': round(m_pi_bat_hp, 2),
            'batting_overlap_with_control_pct': round(ov_bat_pct, 2),
            'bowling_hp_deliveries': n_bowl_hp,
            'bowling_hp_capture_pct': round(pct_bowl_hp, 2),
            'bowling_hp_mean_leverage': round(m_lev_bowl_hp, 3),
            'bowling_hp_mean_pi': round(m_pi_bowl_hp, 2),
            'bowling_overlap_with_control_pct': round(ov_bowl_pct, 2)
        })

    df_cand_summary = pd.DataFrame(summary_rows)
    cand_csv = OUTPUT_DIR / "candidates_summary_metrics.csv"
    df_cand_summary.to_csv(cand_csv, index=False)
    print("\nCandidate Summary Table:")
    print(df_cand_summary[['candidate', 'batting_hp_capture_pct', 'batting_hp_mean_leverage', 'batting_overlap_with_control_pct',
                           'bowling_hp_capture_pct', 'bowling_hp_mean_leverage', 'bowling_overlap_with_control_pct']].to_string())

    # 5. Export Master Candidate Parquet
    export_cols = [
        'match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num',
        'striker_id', 'striker_name', 'bowler_id', 'bowler_name', 'batting_order',
        'phase', 'venue_id', 'is_legal_ball', 'is_batter_ball_faced',
        'score_before', 'wickets_before', 'balls_remaining', 'runs_required', 'required_run_rate', 'current_run_rate',
        'wp_before', 'Batting_PI', 'Bowling_PI', 'expected_leverage_pct', 'wpa_pct', 'absolute_wpa_pct',
        'batting_z_score', 'bowling_z_score', 'lev_z_score_bat', 'lev_z_score_bowl',
        'z_cand0_bat', 'hp_cand0_bat', 'z_cand1a_bat', 'hp_cand1a_bat', 'z_cand1b_bat', 'hp_cand1b_bat',
        'z_cand2_bat', 'hp_cand2_bat', 'z_cand3_bat', 'hp_cand3_bat',
        'z_cand0_bowl', 'hp_cand0_bowl', 'z_cand1a_bowl', 'hp_cand1a_bowl', 'z_cand1b_bowl', 'hp_cand1b_bowl',
        'z_cand2_bowl', 'hp_cand2_bowl', 'z_cand3_bowl', 'hp_cand3_bowl'
    ]

    out_parquet = OUTPUT_DIR / "delivery_candidates_classified.parquet"
    df[export_cols].to_parquet(out_parquet, index=False)
    print(f"\nSaved master candidate classification dataset to {out_parquet}")
    print(f"Total time elapsed: {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
