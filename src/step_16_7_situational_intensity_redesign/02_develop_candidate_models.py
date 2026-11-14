"""
Step 16.7: Script 02 - Develop and Standardize Situational Intensity Candidate Models
=====================================================================================
Constructs four principled experimental alternatives for Situational Intensity (I),
alongside Candidate 0 (Control) and Candidate 4 (Pure Task Difficulty Ablation):

1. Candidate 0 (Control - Baseline):
   - I_0 = clip(((10 - bf) / 10) * 100, 0, 100)
   - PI_0 = 0.65 * T + 0.35 * I_0

2. Candidate 1 (Bounded Smooth Decay):
   - Replaces the hard 10-ball cliff with a smooth exponential decay with floor:
     I_1 = 25.0 + 75.0 * exp(-bf / 10.0)
   - PI_1 = 0.65 * T + 0.35 * I_1

3. Candidate 2 (Context-Dependent Match-Stakes Intensity):
   - Balances Match Stage Urgency, Wicket Exposure Risk, and Smooth Settling:
     M_stage = clip(((120 - balls_remaining) / 120) * 100, 0, 100)
     W_risk  = clip((wickets_before / 7.0) * 100, 0, 100)
     S_settle = 25.0 + 75.0 * exp(-bf / 10.0)
     I_2 = 0.40 * M_stage + 0.40 * W_risk + 0.20 * S_settle
   - PI_2 = 0.65 * T + 0.35 * I_2

4. Candidate 3 (Leverage-Augmented Crisis & Consequence Intensity):
   - Integrates Expected Delivery Leverage without suppressing 1st-innings collapses:
     C_crisis = clip((wickets_before / 4.0) * 100, 0, 100)
     L_conseq = clip(50.0 + 25.0 * Z_Lev, 0, 100)
     S_settle = 25.0 + 75.0 * exp(-bf / 10.0)
     Inn 1: I_3 = 0.45 * C_crisis + 0.35 * L_conseq + 0.20 * S_settle
     Inn 2: I_3 = 0.20 * C_crisis + 0.60 * L_conseq + 0.20 * S_settle
   - PI_3 = 0.65 * T + 0.35 * I_3

5. Candidate 4 (Pure Task Difficulty Ablation - Zero Intensity):
   - PI_4 = T (Removes I entirely to isolate environmental task difficulty)

All candidates standardized within Phase x Innings baselines, High Pressure: Z > 1.00.

Outputs:
- outputs/step_16_7_situational_intensity_redesign/delivery_intensity_candidates.parquet
- outputs/step_16_7_situational_intensity_redesign/candidates_summary_metrics.csv
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


def standardize_series(series):
    s_std = series.std()
    if s_std == 0 or np.isnan(s_std):
        return series - series.mean()
    return (series - series.mean()) / s_std


def main():
    print("=== Step 16.7 Script 02: Develop Situational Intensity Candidates ===")
    t0 = time.time()

    # Load master classified parquet
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading master delivery dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # Load match state for balls_remaining, wickets_before, striker_balls_faced_before
    dms_path = PROCESSED_DIR / "delivery_match_state.csv"
    print(f"Loading match state from {dms_path}...")
    dms_cols = ['match_id', 'innings', 'overid', 'innings_ball_num',
                'striker_balls_faced_before', 'balls_remaining', 'wickets_before']
    dms = pd.read_csv(dms_path, usecols=dms_cols)

    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    df = df.drop(columns=['striker_balls_faced_before', 'balls_remaining', 'wickets_before'], errors='ignore')
    df = df.merge(dms, on=merge_keys, how='left')

    bat_mask = df['is_batter_ball_faced'] == 1
    bat_df = df[bat_mask].copy()
    n_bat = len(bat_df)
    print(f"Loaded {n_bat:,} batting deliveries.")

    # 1. Base Variables
    bf = bat_df['striker_balls_faced_before'].to_numpy(dtype=float)
    balls_rem = bat_df['balls_remaining'].to_numpy(dtype=float)
    w_before = bat_df['wickets_before'].to_numpy(dtype=float)
    innings = bat_df['innings'].to_numpy()
    phase = bat_df['phase'].to_numpy()
    z_lev = bat_df['lev_z_score_bat'].to_numpy(dtype=float)

    # Task Difficulty (T)
    # Recover exact T: T = (Batting_PI - 0.35 * I_0) / 0.65
    i_0 = np.clip(((10.0 - bf) / 10.0) * 100.0, 0.0, 100.0)
    t_diff = (bat_df['Batting_PI'].to_numpy(dtype=float) - 0.35 * i_0) / 0.65
    bat_df['Batting_T'] = t_diff

    # 2. Build Alternative Situational Intensity Formulations
    print("\nComputing Candidate Situational Intensity (I) Formulations...")

    # Candidate 0 (Control)
    bat_df['I_cand0'] = i_0
    bat_df['PI_cand0'] = bat_df['Batting_PI']
    bat_df['Z_cand0'] = bat_df['batting_z_score']
    bat_df['HP_cand0'] = bat_df['Z_cand0'] > 1.00

    # Candidate 1: Bounded Smooth Decay
    # I_1 = 25.0 + 75.0 * exp(-bf / 10.0)
    i_1 = 25.0 + 75.0 * np.exp(-bf / 10.0)
    bat_df['I_cand1'] = i_1
    pi_1 = 0.65 * t_diff + 0.35 * i_1
    bat_df['PI_cand1'] = pi_1
    bat_df['Z_cand1'] = bat_df.groupby(['innings', 'phase'])['PI_cand1'].transform(standardize_series)
    bat_df['HP_cand1'] = bat_df['Z_cand1'] > 1.00

    # Candidate 2: Context-Dependent Match-Stakes Intensity
    # M_stage = clip(((120 - balls_remaining) / 120) * 100, 0, 100)
    # W_risk  = clip((wickets_before / 7.0) * 100, 0, 100)
    # S_settle = 25.0 + 75.0 * exp(-bf / 10.0)
    # I_2 = 0.40 * M_stage + 0.40 * W_risk + 0.20 * S_settle
    m_stage = np.clip(((120.0 - balls_rem) / 120.0) * 100.0, 0.0, 100.0)
    w_risk = np.clip((w_before / 7.0) * 100.0, 0.0, 100.0)
    s_settle = i_1
    i_2 = 0.40 * m_stage + 0.40 * w_risk + 0.20 * s_settle
    bat_df['I_cand2'] = i_2
    pi_2 = 0.65 * t_diff + 0.35 * i_2
    bat_df['PI_cand2'] = pi_2
    bat_df['Z_cand2'] = bat_df.groupby(['innings', 'phase'])['PI_cand2'].transform(standardize_series)
    bat_df['HP_cand2'] = bat_df['Z_cand2'] > 1.00

    # Candidate 3: Leverage-Augmented Crisis & Consequence Intensity
    # C_crisis = clip((wickets_before / 4.0) * 100, 0, 100)
    # L_conseq = clip(50.0 + 25.0 * Z_Lev, 0, 100)
    # Inn 1: I_3 = 0.45 * C_crisis + 0.35 * L_conseq + 0.20 * S_settle
    # Inn 2: I_3 = 0.20 * C_crisis + 0.60 * L_conseq + 0.20 * S_settle
    c_crisis = np.clip((w_before / 4.0) * 100.0, 0.0, 100.0)
    l_conseq = np.clip(50.0 + 25.0 * z_lev, 0.0, 100.0)
    inn1_mask = (innings == 1)
    i_3 = np.where(
        inn1_mask,
        0.45 * c_crisis + 0.35 * l_conseq + 0.20 * s_settle,
        0.20 * c_crisis + 0.60 * l_conseq + 0.20 * s_settle
    )
    bat_df['I_cand3'] = i_3
    pi_3 = 0.65 * t_diff + 0.35 * i_3
    bat_df['PI_cand3'] = pi_3
    bat_df['Z_cand3'] = bat_df.groupby(['innings', 'phase'])['PI_cand3'].transform(standardize_series)
    bat_df['HP_cand3'] = bat_df['Z_cand3'] > 1.00

    # Candidate 4: Pure Task Difficulty Ablation (Zero Situational Intensity)
    # PI_4 = T
    bat_df['I_cand4'] = 0.0
    bat_df['PI_cand4'] = t_diff
    bat_df['Z_cand4'] = bat_df.groupby(['innings', 'phase'])['PI_cand4'].transform(standardize_series)
    bat_df['HP_cand4'] = bat_df['Z_cand4'] > 1.00

    # 3. Export Summary Metrics Table
    print("\n--- Summary Metrics of Candidate Models ---")
    candidates = [
        ('Candidate 0 (Control)', 'PI_cand0', 'Z_cand0', 'HP_cand0', 'I_cand0', 'Original 10-ball linear cliff (I = (10-bf)/10*100)'),
        ('Candidate 1 (Smooth Decay)', 'PI_cand1', 'Z_cand1', 'HP_cand1', 'I_cand1', 'Exponential decay with 25-pt floor (I = 25 + 75*exp(-bf/10))'),
        ('Candidate 2 (Match-Stakes Context)', 'PI_cand2', 'Z_cand2', 'HP_cand2', 'I_cand2', '40% Stage Urgency + 40% Wicket Risk + 20% Settling'),
        ('Candidate 3 (Leverage & Crisis)', 'PI_cand3', 'Z_cand3', 'HP_cand3', 'I_cand3', 'Crisis Safeguard + Scaled Delivery Leverage + Settling'),
        ('Candidate 4 (Pure Task Difficulty)', 'PI_cand4', 'Z_cand4', 'HP_cand4', 'I_cand4', 'Zero Intensity Ablation (PI = T)')
    ]

    summary_rows = []
    top_mask = bat_df['batting_order'].isin([1, 2, 3])
    mid_mask = bat_df['batting_order'].isin([4, 5, 6])
    low_mask = bat_df['batting_order'].isin([7, 8, 9, 10, 11])

    for c_name, pi_col, z_col, hp_col, i_col, desc in candidates:
        hp_s = (bat_df[hp_col] == True)
        n_hp = int(hp_s.sum())
        pct_hp = n_hp / n_bat * 100.0
        m_pi = bat_df[pi_col].mean()
        m_i = bat_df[i_col].mean()
        
        top_hp_pct = (bat_df.loc[top_mask, hp_col] == True).mean() * 100.0
        mid_hp_pct = (bat_df.loc[mid_mask, hp_col] == True).mean() * 100.0
        low_hp_pct = (bat_df.loc[low_mask, hp_col] == True).mean() * 100.0

        # Overlap with Control HP
        ov_ctrl = (bat_df['HP_cand0'] & hp_s).sum()
        ov_pct = (ov_ctrl / bat_df['HP_cand0'].sum()) * 100.0

        summary_rows.append({
            'candidate': c_name,
            'description': desc,
            'total_hp_deliveries': n_hp,
            'hp_capture_pct': round(pct_hp, 2),
            'mean_intensity_I': round(m_i, 2),
            'mean_pi': round(m_pi, 2),
            'top_order_1_3_hp_pct': round(top_hp_pct, 2),
            'middle_order_4_6_hp_pct': round(mid_hp_pct, 2),
            'lower_order_7_11_hp_pct': round(low_hp_pct, 2),
            'overlap_with_control_pct': round(ov_pct, 2)
        })

    df_summary = pd.DataFrame(summary_rows)
    cand_csv = OUTPUT_DIR / "candidates_summary_metrics.csv"
    df_summary.to_csv(cand_csv, index=False)
    print(f"Saved candidate summary metrics to {cand_csv}")
    print(df_summary[['candidate', 'hp_capture_pct', 'top_order_1_3_hp_pct', 'middle_order_4_6_hp_pct',
                      'lower_order_7_11_hp_pct', 'overlap_with_control_pct']].to_string())

    # 4. Save Master Classified Parquet
    out_parquet = OUTPUT_DIR / "delivery_intensity_candidates.parquet"
    export_cols = [
        'match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num',
        'striker_id', 'striker_name', 'bowler_id', 'bowler_name', 'batting_order',
        'phase', 'is_legal_ball', 'is_batter_ball_faced',
        'score_before', 'wickets_before', 'balls_remaining', 'runs_required', 'required_run_rate', 'current_run_rate',
        'striker_balls_faced_before', 'wp_before', 'expected_leverage_pct', 'lev_z_score_bat',
        'Batting_T', 'I_cand0', 'PI_cand0', 'Z_cand0', 'HP_cand0',
        'I_cand1', 'PI_cand1', 'Z_cand1', 'HP_cand1',
        'I_cand2', 'PI_cand2', 'Z_cand2', 'HP_cand2',
        'I_cand3', 'PI_cand3', 'Z_cand3', 'HP_cand3',
        'I_cand4', 'PI_cand4', 'Z_cand4', 'HP_cand4'
    ]
    bat_df[export_cols].to_parquet(out_parquet, index=False)
    print(f"\nSaved master candidate delivery parquet to {out_parquet}")
    print(f"Total time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
