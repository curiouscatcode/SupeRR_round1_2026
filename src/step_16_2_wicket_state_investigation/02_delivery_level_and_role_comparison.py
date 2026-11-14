"""
Step 16.2: Wicket-State Investigation - Script 02
Delivery-Level, Role Bias & Situational Integrity Comparison
============================================================
Compares three batting classification models:
1. Control: Approved Step 16 (Phase x Innings Standard Z > 1.0)
2. Experiment 1: 5-Group Wicket-State Scheme (Z > 1.0)
   (with explicit fallback to Phase x Innings if cell count < 50)
3. Experiment 2: Consolidated 3-Group Wicket-State Scheme (Z > 1.0)
   (Low: 0-1 wkts, Moderate: 2-4 wkts, High: 5+ wkts)

Audits:
- Batting Role Capture: Top Order (1-3), Middle Order (4-6), Lower Order (7-11)
  * HP deliveries, Within-role capture %, Share of all HP balls, Representation Index.
- Situational Diagnostic Checks:
  * False Positive Audit: Routine Deliveries (0 wickets lost & healthy CRR/low RRR)
    classified as "high pressure".
  * False Negative Audit: Crisis Deliveries (6+ wickets lost)
    classified as "not high pressure".
- Phase & Innings Distribution Balance.

Exports:
- outputs/step_16_2_wicket_state_investigation/batting_role_capture_comparison.csv
- outputs/step_16_2_wicket_state_investigation/phase_innings_capture_comparison.csv
- outputs/step_16_2_wicket_state_investigation/delivery_level_wicket_state_comparison.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_2_wicket_state_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_w_grp_5(w):
    if w in [0, 1]: return '0-1 Wkts'
    elif w in [2, 3]: return '2-3 Wkts'
    elif w in [4, 5]: return '4-5 Wkts'
    elif w in [6, 7]: return '6-7 Wkts'
    elif w >= 8: return '8-10 Wkts'
    return 'Unknown'


def get_w_grp_3(w):
    if w in [0, 1]: return 'Low (0-1 Wkts)'
    elif w in [2, 3, 4]: return 'Moderate (2-4 Wkts)'
    elif w >= 5: return 'High (5+ Wkts)'
    return 'Unknown'


def get_role(order):
    if order in [1, 2, 3]: return 'Top Order (1-3)'
    elif order in [4, 5, 6]: return 'Middle Order (4-6)'
    else: return 'Lower Order (7-11)'


def compute_group_zscores(df: pd.DataFrame, group_cols: list, val_col: str, fallback_cols: list, min_n: int = 50):
    """
    Computes standard Z-scores grouped by group_cols.
    If a cell has count < min_n, falls back to grouping by fallback_cols.
    """
    counts = df.groupby(group_cols)[val_col].transform('count')
    means = df.groupby(group_cols)[val_col].transform('mean')
    stds = df.groupby(group_cols)[val_col].transform('std')

    fb_means = df.groupby(fallback_cols)[val_col].transform('mean')
    fb_stds = df.groupby(fallback_cols)[val_col].transform('std')

    use_fb = (counts < min_n) | stds.isnull() | (stds < 1e-6)
    final_means = np.where(use_fb, fb_means, means)
    final_stds = np.where(use_fb, fb_stds, stds)
    
    z = (df[val_col] - final_means) / final_stds
    return z, final_means, final_stds, use_fb


def main():
    print("=== Step 16.2 Script 02: Delivery-Level & Role Comparison ===")

    # 1. Load active cleaned dataset
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    df = raw_df[~tail_mask].copy()

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    total_balls = len(bat_df)
    print(f"Total Batting Balls: {total_balls:,}")

    bat_df['role'] = bat_df['batting_order'].apply(get_role)
    bat_df['w_grp_5'] = bat_df['wickets_before'].apply(get_w_grp_5)
    bat_df['w_grp_3'] = bat_df['wickets_before'].apply(get_w_grp_3)

    # 2. Compute Z-Scores for all 3 models
    # Model 1: Control (Step 16 Phase x Innings)
    ctrl_means = bat_df.groupby(['innings', 'phase'])['Batting_PI'].transform('mean')
    ctrl_stds = bat_df.groupby(['innings', 'phase'])['Batting_PI'].transform('std')
    bat_df['z_control'] = (bat_df['Batting_PI'] - ctrl_means) / ctrl_stds
    bat_df['hp_control'] = bat_df['z_control'] > 1.0

    # Model 2: Experiment 1 (5-Group Wicket Scheme)
    z_exp1, m_exp1, s_exp1, fb_exp1 = compute_group_zscores(
        bat_df, ['innings', 'phase', 'w_grp_5'], 'Batting_PI', ['innings', 'phase'], min_n=50
    )
    bat_df['z_exp1_5grp'] = z_exp1
    bat_df['hp_exp1_5grp'] = bat_df['z_exp1_5grp'] > 1.0
    bat_df['fb_exp1_5grp'] = fb_exp1

    # Model 3: Experiment 2 (Consolidated 3-Group Wicket Scheme)
    z_exp2, m_exp2, s_exp2, fb_exp2 = compute_group_zscores(
        bat_df, ['innings', 'phase', 'w_grp_3'], 'Batting_PI', ['innings', 'phase'], min_n=50
    )
    bat_df['z_exp2_3grp'] = z_exp2
    bat_df['hp_exp2_3grp'] = bat_df['z_exp2_3grp'] > 1.0

    models = [
        ('Control (Step 16 Phase x Innings)', 'hp_control'),
        ('Exp 1 (5-Group Wicket State)', 'hp_exp1_5grp'),
        ('Exp 2 (3-Group Wicket State)', 'hp_exp2_3grp')
    ]

    # 3. Batting Role Capture Comparison
    print("\n--- Batting Role Capture Comparison ---")
    roles = ['Top Order (1-3)', 'Middle Order (4-6)', 'Lower Order (7-11)']
    role_rows = []

    for model_name, hp_col in models:
        total_hp = bat_df[hp_col].sum()
        for r in roles:
            sub = bat_df[bat_df['role'] == r]
            r_total = len(sub)
            r_hp = sub[hp_col].sum()

            natural_share = round((r_total / total_balls) * 100.0, 2)
            capture_rate = round((r_hp / r_total) * 100.0, 2)
            hp_share = round((r_hp / total_hp) * 100.0, 2) if total_hp > 0 else 0.0
            rep_index = round(hp_share / natural_share, 3) if natural_share > 0 else 0.0

            role_rows.append({
                'model': model_name,
                'batting_role': r,
                'total_deliveries': r_total,
                'natural_share_pct': natural_share,
                'hp_deliveries': r_hp,
                'within_role_capture_pct': capture_rate,
                'total_hp_deliveries_model': total_hp,
                'hp_deliveries_share_pct': hp_share,
                'representation_index': rep_index
            })

    role_df = pd.DataFrame(role_rows)
    out_role_path = OUTPUT_DIR / "batting_role_capture_comparison.csv"
    role_df.to_csv(out_role_path, index=False)
    print(role_df[['model', 'batting_role', 'hp_deliveries', 'within_role_capture_pct', 'hp_deliveries_share_pct', 'representation_index']])

    # 4. Phase and Innings Distribution Comparison
    print("\n--- Phase and Innings Distribution Comparison ---")
    phase_inn_rows = []
    phases = ['PP', 'Middle', 'Death']

    for model_name, hp_col in models:
        total_hp = bat_df[hp_col].sum()
        
        # Phases
        for ph in phases:
            sub = bat_df[bat_df['phase'] == ph]
            ph_total = len(sub)
            ph_hp = sub[hp_col].sum()
            phase_inn_rows.append({
                'model': model_name,
                'dimension': 'Phase',
                'group': ph,
                'total_deliveries': ph_total,
                'hp_deliveries': ph_hp,
                'capture_rate_pct': round((ph_hp / ph_total) * 100.0, 2),
                'hp_share_pct': round((ph_hp / total_hp) * 100.0, 2)
            })
            
        # Innings
        for inn in [1, 2]:
            sub = bat_df[bat_df['innings'] == inn]
            inn_total = len(sub)
            inn_hp = sub[hp_col].sum()
            phase_inn_rows.append({
                'model': model_name,
                'dimension': 'Innings',
                'group': f'Innings {inn}',
                'total_deliveries': inn_total,
                'hp_deliveries': inn_hp,
                'capture_rate_pct': round((inn_hp / inn_total) * 100.0, 2),
                'hp_share_pct': round((inn_hp / total_hp) * 100.0, 2)
            })

    pi_df = pd.DataFrame(phase_inn_rows)
    out_pi_path = OUTPUT_DIR / "phase_innings_capture_comparison.csv"
    pi_df.to_csv(out_pi_path, index=False)
    print(f"Saved phase and innings capture comparison to {out_pi_path}")

    # 5. Situational Integrity Diagnostics (False Positives & False Negatives)
    print("\n--- Situational Integrity Diagnostics ---")
    # Routine Deliveries: 0 wickets down and comfortable situation
    # Inn 1: Wkts==0 and CRR >= 8.5
    # Inn 2: Wkts==0 and RRR <= 6.5
    routine_mask = (
        ((bat_df['innings'] == 1) & (bat_df['wickets_before'] == 0) & (bat_df['current_run_rate'] >= 8.5)) |
        ((bat_df['innings'] == 2) & (bat_df['wickets_before'] == 0) & (bat_df['required_run_rate'] <= 6.5))
    )
    n_routine = routine_mask.sum()

    # Crisis Deliveries: 6+ wickets down
    crisis_mask = bat_df['wickets_before'] >= 6
    n_crisis = crisis_mask.sum()

    print(f"Total Routine Deliveries (0 wkts, healthy run rate): {n_routine:,}")
    print(f"Total Crisis Deliveries (6+ wickets lost): {n_crisis:,}")

    print("\nFalse Positive Rate (Routine Deliveries misclassified as High Pressure):")
    for m_name, m_col in models:
        fp_count = (routine_mask & bat_df[m_col]).sum()
        fp_rate = (fp_count / n_routine) * 100.0
        print(f"  {m_name}: {fp_count:,} / {n_routine:,} ({fp_rate:.2f}%)")

    print("\nFalse Negative Rate (Crisis Deliveries misclassified as NOT High Pressure):")
    for m_name, m_col in models:
        fn_count = (crisis_mask & ~bat_df[m_col]).sum()
        fn_rate = (fn_count / n_crisis) * 100.0
        print(f"  {m_name}: {fn_count:,} / {n_crisis:,} ({fn_rate:.2f}%)")

    # 6. Delivery-Level Comparison Sample
    sample_cols = [
        'match_id', 'innings', 'overid', 'innings_ball_num', 'phase', 'batting_order', 'role',
        'striker_id', 'striker_name', 'score_before', 'wickets_before', 'current_run_rate',
        'required_run_rate', 'Batting_PI', 'z_control', 'hp_control', 'z_exp1_5grp', 'hp_exp1_5grp',
        'z_exp2_3grp', 'hp_exp2_3grp'
    ]
    # Sample contrasting deliveries:
    # 1. Routine 0-wicket delivery that becomes HP under Exp 1
    # 2. Collapse delivery (6+ wkts) that loses HP under Exp 1
    # 3. Early collapse top-order delivery
    case1 = bat_df[routine_mask & ~bat_df['hp_control'] & bat_df['hp_exp1_5grp']].head(20)
    case2 = bat_df[crisis_mask & bat_df['hp_control'] & ~bat_df['hp_exp1_5grp']].head(20)
    case3 = bat_df[(bat_df['role'] == 'Top Order (1-3)') & (bat_df['wickets_before'] >= 2) & bat_df['hp_control']].head(20)
    case4 = bat_df.head(40)

    sample_all = pd.concat([case1, case2, case3, case4]).drop_duplicates().head(100)
    out_sample_path = OUTPUT_DIR / "delivery_level_wicket_state_comparison.csv"
    sample_all[sample_cols].to_csv(out_sample_path, index=False)
    print(f"Saved delivery-level comparison sample to {out_sample_path}")


if __name__ == "__main__":
    main()
