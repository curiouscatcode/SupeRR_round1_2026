"""
Step 16.1: Independent Audit - Script 02
Audit Batting Role Bias, Bowling Phase Bias, and Innings Normalization
======================================================================
Investigates:
1. Batting Role Bias:
   - Validates Top Order (1-3), Middle Order (4-6), Lower Order (7-11)
   - Checks data integrity for batting_order (missing values, order 12)
   - Audits capture rates, shares, and Representation Index under PI > 60 vs Z > 1.0
   - Evaluates whether role improvements are genuine or mechanical
2. Bowling Phase Bias:
   - Audits phase capture rates and phase shares across PP, Middle, Death
   - Confirms whether death-bowler bias is resolved
3. Innings Normalization Investigation:
   - Evaluates Approach A (Phase-only: pooling innings) vs Approach B (Phase x Innings)
   - Tests 5 concrete delivery-level match scenarios from actual match data
   - Analyzes whether Approach B inappropriately discounts genuine chasing pressure
   - Assesses the preservation of PI components (RRR, CRR, wickets)

Exports:
- outputs/step_16_1_independent_audit/batting_role_bias_audit.csv
- outputs/step_16_1_independent_audit/bowling_phase_bias_audit.csv
- outputs/step_16_1_independent_audit/innings_normalization_audit.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
AUDIT_OUT_DIR = Path("outputs/step_16_1_independent_audit")
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_zscores(df: pd.DataFrame, group_cols: list, val_col: str, prefix: str):
    grouped = df.groupby(group_cols)[val_col]
    means = grouped.transform('mean')
    stds = grouped.transform('std')
    df[f'{prefix}_mean'] = means
    df[f'{prefix}_std'] = stds
    df[f'{prefix}_z'] = (df[val_col] - means) / stds
    return df


def main():
    print("=== Step 16.1 Audit Script 02: Biases & Innings Normalization ===")

    # 1. Load active cleaned dataset
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    df = raw_df[~tail_mask].copy()

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    total_bat_balls = len(bat_df)
    total_bowl_balls = len(bowl_df)

    # -------------------------------------------------------------
    # 2. Batting Role Bias Audit
    # -------------------------------------------------------------
    print("\nAuditing Batting Role Bias...")
    print("Batting order value counts:\n", bat_df['batting_order'].value_counts().sort_index())
    
    # Check nulls or unexpected values
    n_order_null = bat_df['batting_order'].isnull().sum()
    n_order_12 = (bat_df['batting_order'] == 12).sum()
    print(f"Batting order nulls: {n_order_null}, Batting order == 12 count: {n_order_12}")

    def assign_role(order):
        if order in [1, 2, 3]:
            return 'Top Order (1-3)'
        elif order in [4, 5, 6]:
            return 'Middle Order (4-6)'
        elif order >= 7:
            return 'Lower Order (7-11)'
        return 'Unknown'

    bat_df['role'] = bat_df['batting_order'].apply(assign_role)

    # Z-scores for Batting
    bat_df = compute_zscores(bat_df, ['phase'], 'Batting_PI', 'appA')
    bat_df = compute_zscores(bat_df, ['innings', 'phase'], 'Batting_PI', 'appB')

    bat_df['hp_base'] = bat_df['Batting_PI'] > 60.0
    bat_df['hp_appA'] = bat_df['appA_z'] > 1.0
    bat_df['hp_appB'] = bat_df['appB_z'] > 1.0

    roles = ['Top Order (1-3)', 'Middle Order (4-6)', 'Lower Order (7-11)']
    role_audit_rows = []

    models = [
        ('Baseline (PI > 60.0)', 'hp_base'),
        ('Approach A (Phase-only Z > 1.0)', 'hp_appA'),
        ('Approach B (Phase x Innings Z > 1.0)', 'hp_appB')
    ]

    for model_label, col_mask in models:
        total_hp = bat_df[col_mask].sum()
        for r in roles:
            sub = bat_df[bat_df['role'] == r]
            r_total = len(sub)
            r_hp = sub[col_mask].sum()
            
            natural_share = round((r_total / total_bat_balls) * 100.0, 2)
            capture_rate = round((r_hp / r_total) * 100.0, 2)
            hp_share = round((r_hp / total_hp) * 100.0, 2) if total_hp > 0 else 0.0
            rep_index = round(hp_share / natural_share, 3) if natural_share > 0 else 0.0

            role_audit_rows.append({
                'model': model_label,
                'batting_role': r,
                'total_balls_faced': r_total,
                'natural_share_pct': natural_share,
                'hp_balls_faced': r_hp,
                'within_role_capture_pct': capture_rate,
                'hp_balls_share_pct': hp_share,
                'representation_index': rep_index
            })

    role_audit_df = pd.DataFrame(role_audit_rows)
    out_r_path = AUDIT_OUT_DIR / "batting_role_bias_audit.csv"
    role_audit_df.to_csv(out_r_path, index=False)
    print(f"Saved batting role bias audit to {out_r_path}")
    print(role_audit_df[['model', 'batting_role', 'hp_balls_faced', 'within_role_capture_pct', 'hp_balls_share_pct', 'representation_index']])

    # -------------------------------------------------------------
    # 3. Bowling Phase Bias Audit
    # -------------------------------------------------------------
    print("\nAuditing Bowling Phase Bias...")
    bowl_df = compute_zscores(bowl_df, ['phase'], 'Bowling_PI', 'appA')
    bowl_df = compute_zscores(bowl_df, ['innings', 'phase'], 'Bowling_PI', 'appB')

    bowl_df['hp_base'] = bowl_df['Bowling_PI'] > 60.0
    bowl_df['hp_appA'] = bowl_df['appA_z'] > 1.0
    bowl_df['hp_appB'] = bowl_df['appB_z'] > 1.0

    phases = ['PP', 'Middle', 'Death']
    phase_audit_rows = []

    bowl_models = [
        ('Baseline (PI > 60.0)', 'hp_base'),
        ('Approach A (Phase-only Z > 1.0)', 'hp_appA'),
        ('Approach B (Phase x Innings Z > 1.0)', 'hp_appB')
    ]

    for model_label, col_mask in bowl_models:
        total_hp = bowl_df[col_mask].sum()
        for ph in phases:
            sub = bowl_df[bowl_df['phase'] == ph]
            ph_total = len(sub)
            ph_hp = sub[col_mask].sum()
            
            natural_share = round((ph_total / total_bowl_balls) * 100.0, 2)
            capture_rate = round((ph_hp / ph_total) * 100.0, 2)
            hp_share = round((ph_hp / total_hp) * 100.0, 2) if total_hp > 0 else 0.0
            rep_index = round(hp_share / natural_share, 3) if natural_share > 0 else 0.0

            phase_audit_rows.append({
                'model': model_label,
                'phase': ph,
                'total_legal_balls': ph_total,
                'natural_share_pct': natural_share,
                'hp_legal_balls': ph_hp,
                'phase_capture_pct': capture_rate,
                'hp_balls_share_pct': hp_share,
                'representation_index': rep_index
            })

    phase_audit_df = pd.DataFrame(phase_audit_rows)
    out_p_path = AUDIT_OUT_DIR / "bowling_phase_bias_audit.csv"
    phase_audit_df.to_csv(out_p_path, index=False)
    print(f"Saved bowling phase bias audit to {out_p_path}")
    print(phase_audit_df[['model', 'phase', 'hp_legal_balls', 'phase_capture_pct', 'hp_balls_share_pct', 'representation_index']])

    # -------------------------------------------------------------
    # 4. Critical Investigation: Innings Normalization
    # -------------------------------------------------------------
    print("\nAuditing Innings Normalization (Approach A vs Approach B)...")

    # Overall Innings Split Comparison
    print("Innings Share Comparison:")
    for m_label, m_col in models:
        inn1_share = (bat_df[m_col] & (bat_df['innings'] == 1)).sum() / bat_df[m_col].sum() * 100.0
        inn2_share = (bat_df[m_col] & (bat_df['innings'] == 2)).sum() / bat_df[m_col].sum() * 100.0
        print(f"  {m_label}: Inn 1 = {inn1_share:.2f}%, Inn 2 = {inn2_share:.2f}%")

    # Select representative actual deliveries across the 5 canonical scenarios
    scenarios = [
        {
            'scenario_name': '1. Difficult Chase in Powerplay (RRR >= 10.0, 2+ Wickets Down)',
            'filter_desc': 'Inn 2, PP, RRR >= 10, Wickets >= 2',
            'query': (bat_df['innings'] == 2) & (bat_df['phase'] == 'PP') & (bat_df['required_run_rate'] >= 10.0) & (bat_df['wickets_before'] >= 2)
        },
        {
            'scenario_name': '2. Comfortable Chase in Powerplay (RRR <= 6.5, <= 1 Wicket Down)',
            'filter_desc': 'Inn 2, PP, RRR <= 6.5, Wickets <= 1',
            'query': (bat_df['innings'] == 2) & (bat_df['phase'] == 'PP') & (bat_df['required_run_rate'] <= 6.5) & (bat_df['wickets_before'] <= 1)
        },
        {
            'scenario_name': '3. Steep Chase in Middle Overs (RRR >= 12.0)',
            'filter_desc': 'Inn 2, Middle, RRR >= 12.0',
            'query': (bat_df['innings'] == 2) & (bat_df['phase'] == 'Middle') & (bat_df['required_run_rate'] >= 12.0)
        },
        {
            'scenario_name': '4. Comfortable First Innings in Death Overs (Score >= 160, Wickets <= 2)',
            'filter_desc': 'Inn 1, Death, Score >= 160, Wickets <= 2',
            'query': (bat_df['innings'] == 1) & (bat_df['phase'] == 'Death') & (bat_df['score_before'] >= 160) & (bat_df['wickets_before'] <= 2)
        },
        {
            'scenario_name': '5. High-Pressure First Innings under Scoreboard Crisis (Wickets >= 5, CRR <= 6.5)',
            'filter_desc': 'Inn 1, Middle/Death, Wickets >= 5, CRR <= 6.5',
            'query': (bat_df['innings'] == 1) & (bat_df['phase'].isin(['Middle', 'Death'])) & (bat_df['wickets_before'] >= 5) & (bat_df['current_run_rate'] <= 6.5)
        }
    ]

    scenario_audit_rows = []

    for sc in scenarios:
        sub = bat_df[sc['query']]
        n_sc = len(sub)
        
        n_hp_base = sub['hp_base'].sum()
        pct_hp_base = (n_hp_base / n_sc) * 100.0 if n_sc > 0 else 0.0

        n_hp_appA = sub['hp_appA'].sum()
        pct_hp_appA = (n_hp_appA / n_sc) * 100.0 if n_sc > 0 else 0.0

        n_hp_appB = sub['hp_appB'].sum()
        pct_hp_appB = (n_hp_appB / n_sc) * 100.0 if n_sc > 0 else 0.0

        # Mean PI and Z-scores
        mean_pi = sub['Batting_PI'].mean()
        mean_z_a = sub['appA_z'].mean()
        mean_z_b = sub['appB_z'].mean()

        # Get representative single delivery example
        rep_ex = sub.iloc[0] if n_sc > 0 else None
        ex_summary = (
            f"Match {rep_ex['match_id']} Inn {rep_ex['innings']} Over {rep_ex['overid']}.{rep_ex['innings_ball_num'] % 6}: "
            f"W={int(rep_ex['wickets_before'])}, Score={int(rep_ex['score_before'])}, "
            f"RRR={rep_ex['required_run_rate']:.1f} (CRR={rep_ex['current_run_rate']:.1f}), "
            f"PI={rep_ex['Batting_PI']:.1f} -> AppA_Z={rep_ex['appA_z']:.2f} (HP={bool(rep_ex['hp_appA'])}), "
            f"AppB_Z={rep_ex['appB_z']:.2f} (HP={bool(rep_ex['hp_appB'])})"
        ) if rep_ex is not None else ""

        scenario_audit_rows.append({
            'scenario_name': sc['scenario_name'],
            'filter_description': sc['filter_desc'],
            'delivery_count': n_sc,
            'mean_batting_pi': round(mean_pi, 2),
            'baseline_hp_count': n_hp_base,
            'baseline_capture_pct': round(pct_hp_base, 2),
            'appA_hp_count': n_hp_appA,
            'appA_capture_pct': round(pct_hp_appA, 2),
            'appB_hp_count': n_hp_appB,
            'appB_capture_pct': round(pct_hp_appB, 2),
            'capture_pct_diff_B_minus_A': round(pct_hp_appB - pct_hp_appA, 2),
            'mean_appA_z': round(mean_z_a, 2),
            'mean_appB_z': round(mean_z_b, 2),
            'representative_example': ex_summary
        })

    scenario_audit_df = pd.DataFrame(scenario_audit_rows)
    out_s_path = AUDIT_OUT_DIR / "innings_normalization_audit.csv"
    scenario_audit_df.to_csv(out_s_path, index=False)
    print(f"Saved innings normalization audit to {out_s_path}")
    print("\nInnings Normalization Scenario Comparison:")
    for _, row in scenario_audit_df.iterrows():
        print(f"Scenario: {row['scenario_name']}")
        print(f"  Count: {row['delivery_count']:,} | Mean PI: {row['mean_batting_pi']}")
        print(f"  Capture % -> Baseline: {row['baseline_capture_pct']}% | App A: {row['appA_capture_pct']}% | App B: {row['appB_capture_pct']}%")
        print(f"  Representative Example: {row['representative_example']}\n")


if __name__ == "__main__":
    main()
