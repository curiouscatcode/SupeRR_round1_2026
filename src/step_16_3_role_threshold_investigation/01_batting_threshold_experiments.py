"""
Step 16.3: Investigation Script 01
Batting Threshold Experiments (Exp 1: Top-Order & Exp 2: Death-Over)
=====================================================================
Evaluates two independent batting threshold modifications against Control:

Control: Approved Step 16 (Phase x Innings Standard Z > 1.00 for all)

Experiment 1: Lower Top-Order Batting Threshold
- Exp 1A: Top Order (pos 1-3) Z > 0.75; others (pos 4-11) Z > 1.00
- Exp 1B: Top Order (pos 1-3) Z > 0.50; others (pos 4-11) Z > 1.00

Experiment 2: Increase Death-Over Batting Threshold
- Exp 2A: Death phase Z > 1.25; PP & Middle Z > 1.00
- Exp 2B: Death phase Z > 1.50; PP & Middle Z > 1.00

Exports:
- outputs/step_16_3_role_threshold_investigation/exp1_top_order_threshold_sensitivity.csv
- outputs/step_16_3_role_threshold_investigation/exp2_death_threshold_sensitivity.csv
- outputs/step_16_3_role_threshold_investigation/batting_role_threshold_exposure.csv
- outputs/step_16_3_role_threshold_investigation/batting_phase_threshold_exposure.csv
- outputs/step_16_3_role_threshold_investigation/delivery_level_threshold_comparison.csv
- outputs/step_16_3_role_threshold_investigation/exp1_exp2_brs3_rankings_comparison.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_3_role_threshold_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

K = 50.0


def get_role(order):
    if order in [1, 2, 3]: return 'Top Order (1-3)'
    elif order in [4, 5, 6]: return 'Middle Order (4-6)'
    else: return 'Lower Order (7-11)'


def calculate_brs3(bat_df: pd.DataFrame, hp_mask: pd.Series, model_name: str) -> pd.DataFrame:
    """Computes BRS3 scores and rankings for Tier 1 batters under a specific HP mask."""
    df = bat_df.copy()
    df['is_out'] = (df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])).astype(int)

    df['runs_hp'] = np.where(hp_mask, df['runs'], 0)
    df['bf_hp'] = np.where(hp_mask, 1, 0)
    df['out_hp'] = np.where(hp_mask, df['is_out'], 0)

    df['runs_low'] = np.where(~hp_mask, df['runs'], 0)
    df['bf_low'] = np.where(~hp_mask, 1, 0)

    agg = df.groupby('striker_id').agg(
        player_name=('striker_name', 'first'),
        bf_hp=('bf_hp', 'sum'),
        runs_hp=('runs_hp', 'sum'),
        out_hp=('out_hp', 'sum'),
        bf_low=('bf_low', 'sum'),
        runs_low=('runs_low', 'sum')
    ).reset_index()

    hp_matches = df[hp_mask].groupby('striker_id')['match_id'].nunique().to_dict()
    agg['hp_matches'] = agg['striker_id'].map(hp_matches).fillna(0).astype(int)

    tot_bf_hp = agg['bf_hp'].sum()
    tot_runs_hp = agg['runs_hp'].sum()
    tot_out_hp = agg['out_hp'].sum()
    tot_bf_low = agg['bf_low'].sum()
    tot_runs_low = agg['runs_low'].sum()

    mu_sr_hp = (tot_runs_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 114.0
    mu_out_hp = (tot_out_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 7.0
    mu_sr_low = (tot_runs_low / tot_bf_low) * 100.0 if tot_bf_low > 0 else 140.0

    agg['lambda_hp'] = agg['bf_hp'] / (agg['bf_hp'] + K)
    agg['lambda_low'] = agg['bf_low'] / (agg['bf_low'] + K)

    agg['sr_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['runs_hp'] / agg['bf_hp']) * 100.0, mu_sr_hp)
    agg['out_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['out_hp'] / agg['bf_hp']) * 100.0, mu_out_hp)
    agg['sr_obs_low'] = np.where(agg['bf_low'] > 0, (agg['runs_low'] / agg['bf_low']) * 100.0, mu_sr_low)

    agg['sr_star'] = agg['lambda_hp'] * agg['sr_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_sr_hp
    agg['out_star'] = agg['lambda_hp'] * agg['out_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_out_hp
    agg['surv_star'] = 100.0 - agg['out_star']
    agg['sr_low_star'] = agg['lambda_low'] * agg['sr_obs_low'] + (1.0 - agg['lambda_low']) * mu_sr_low
    agg['diff_sr_star'] = agg['sr_star'] - agg['sr_low_star']

    agg['score_sr'] = np.clip((agg['sr_star'] - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    agg['score_surv'] = np.clip((agg['surv_star'] - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    agg['score_diff'] = np.clip((agg['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)

    agg['brs3'] = np.round(np.clip(0.45 * agg['score_sr'] + 0.35 * agg['score_surv'] + 0.20 * agg['score_diff'], 0.0, 100.0), 2)

    t1_mask = (agg['bf_hp'] >= 60) | ((agg['bf_hp'] >= 50) & (agg['hp_matches'] >= 6))
    t2_mask = (agg['bf_hp'] >= 40) & ~t1_mask
    
    agg['tier'] = 'Excluded'
    agg.loc[t2_mask, 'tier'] = 'Tier 2'
    agg.loc[t1_mask, 'tier'] = 'Tier 1'

    agg['tier1_rank'] = np.nan
    agg.loc[t1_mask, 'tier1_rank'] = agg.loc[t1_mask, 'brs3'].rank(ascending=False, method='min').astype(int)
    agg['model'] = model_name
    return agg


def main():
    print("=== Step 16.3 Script 01: Batting Threshold Sensitivity Experiments ===")

    # 1. Load active cleaned dataset
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    df = raw_df[~tail_mask].copy()

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    total_balls = len(bat_df)
    print(f"Total Batting Balls Faced: {total_balls:,}")

    bat_df['role'] = bat_df['batting_order'].apply(get_role)

    # Compute Approach B Standard Z-score
    grouped = bat_df.groupby(['innings', 'phase'])['Batting_PI']
    means = grouped.transform('mean')
    stds = grouped.transform('std')
    bat_df['z_score'] = (bat_df['Batting_PI'] - means) / stds

    # Define Threshold Conditions
    is_top = bat_df['role'] == 'Top Order (1-3)'
    is_death = bat_df['phase'] == 'Death'

    # Control: Z > 1.00 for all
    bat_df['hp_ctrl'] = bat_df['z_score'] > 1.00

    # Experiment 1A: Top Order Z > 0.75, Others Z > 1.00
    bat_df['hp_exp1a'] = np.where(is_top, bat_df['z_score'] > 0.75, bat_df['z_score'] > 1.00)

    # Experiment 1B: Top Order Z > 0.50, Others Z > 1.00
    bat_df['hp_exp1b'] = np.where(is_top, bat_df['z_score'] > 0.50, bat_df['z_score'] > 1.00)

    # Experiment 2A: Death Phase Z > 1.25, PP/Middle Z > 1.00
    bat_df['hp_exp2a'] = np.where(is_death, bat_df['z_score'] > 1.25, bat_df['z_score'] > 1.00)

    # Experiment 2B: Death Phase Z > 1.50, PP/Middle Z > 1.00
    bat_df['hp_exp2b'] = np.where(is_death, bat_df['z_score'] > 1.50, bat_df['z_score'] > 1.00)

    models = [
        ('Control (Step 16)', bat_df['hp_ctrl'], 'Control'),
        ('Exp 1A (Top Z > 0.75)', bat_df['hp_exp1a'], 'Exp 1'),
        ('Exp 1B (Top Z > 0.50)', bat_df['hp_exp1b'], 'Exp 1'),
        ('Exp 2A (Death Z > 1.25)', bat_df['hp_exp2a'], 'Exp 2'),
        ('Exp 2B (Death Z > 1.50)', bat_df['hp_exp2b'], 'Exp 2')
    ]

    # -------------------------------------------------------------
    # 2. Batting Role Threshold Exposure Comparison
    # -------------------------------------------------------------
    roles = ['Top Order (1-3)', 'Middle Order (4-6)', 'Lower Order (7-11)']
    role_rows = []

    for model_name, mask, exp_type in models:
        total_hp = mask.sum()
        for r in roles:
            sub = bat_df[bat_df['role'] == r]
            r_total = len(sub)
            r_hp = (sub['role'] == r) & mask[sub.index]
            r_hp_count = r_hp.sum()

            natural_share = round((r_total / total_balls) * 100.0, 2)
            capture_rate = round((r_hp_count / r_total) * 100.0, 2)
            hp_share = round((r_hp_count / total_hp) * 100.0, 2) if total_hp > 0 else 0.0
            rep_index = round(hp_share / natural_share, 3) if natural_share > 0 else 0.0

            role_rows.append({
                'experiment_family': exp_type,
                'model': model_name,
                'batting_role': r,
                'total_balls_faced': r_total,
                'natural_share_pct': natural_share,
                'hp_balls_faced': r_hp_count,
                'within_role_capture_pct': capture_rate,
                'total_hp_balls_model': total_hp,
                'hp_share_pct': hp_share,
                'representation_index': rep_index
            })

    role_df = pd.DataFrame(role_rows)
    out_role_path = OUTPUT_DIR / "batting_role_threshold_exposure.csv"
    role_df.to_csv(out_role_path, index=False)
    print(f"Saved batting role exposure to {out_role_path}")

    # -------------------------------------------------------------
    # 3. Batting Phase Threshold Exposure Comparison
    # -------------------------------------------------------------
    phases = ['PP', 'Middle', 'Death']
    phase_rows = []

    for model_name, mask, exp_type in models:
        total_hp = mask.sum()
        for ph in phases:
            sub = bat_df[bat_df['phase'] == ph]
            ph_total = len(sub)
            ph_hp_count = mask[sub.index].sum()

            natural_share = round((ph_total / total_balls) * 100.0, 2)
            capture_rate = round((ph_hp_count / ph_total) * 100.0, 2)
            hp_share = round((ph_hp_count / total_hp) * 100.0, 2) if total_hp > 0 else 0.0
            rep_index = round(hp_share / natural_share, 3) if natural_share > 0 else 0.0

            phase_rows.append({
                'experiment_family': exp_type,
                'model': model_name,
                'phase': ph,
                'total_balls': ph_total,
                'natural_share_pct': natural_share,
                'hp_balls': ph_hp_count,
                'phase_capture_pct': capture_rate,
                'total_hp_balls_model': total_hp,
                'hp_share_pct': hp_share,
                'representation_index': rep_index
            })

    phase_df = pd.DataFrame(phase_rows)
    out_phase_path = OUTPUT_DIR / "batting_phase_threshold_exposure.csv"
    phase_df.to_csv(out_phase_path, index=False)
    print(f"Saved batting phase exposure to {out_phase_path}")

    # -------------------------------------------------------------
    # 4. Sensitivity Tables for Exp 1 and Exp 2
    # -------------------------------------------------------------
    # Exp 1 Table
    exp1_df = role_df[role_df['experiment_family'].isin(['Control', 'Exp 1'])].copy()
    out_exp1_path = OUTPUT_DIR / "exp1_top_order_threshold_sensitivity.csv"
    exp1_df.to_csv(out_exp1_path, index=False)

    # Exp 2 Table
    exp2_df = phase_df[phase_df['experiment_family'].isin(['Control', 'Exp 2'])].copy()
    out_exp2_path = OUTPUT_DIR / "exp2_death_threshold_sensitivity.csv"
    exp2_df.to_csv(out_exp2_path, index=False)

    # -------------------------------------------------------------
    # 5. Compute BRS3 Rankings Across Models
    # -------------------------------------------------------------
    print("\nCalculating BRS3 rankings for Control and Experiments...")
    rank_ctrl = calculate_brs3(bat_df, bat_df['hp_ctrl'], 'Control')
    rank_exp1a = calculate_brs3(bat_df, bat_df['hp_exp1a'], 'Exp 1A')
    rank_exp1b = calculate_brs3(bat_df, bat_df['hp_exp1b'], 'Exp 1B')
    rank_exp2a = calculate_brs3(bat_df, bat_df['hp_exp2a'], 'Exp 2A')
    rank_exp2b = calculate_brs3(bat_df, bat_df['hp_exp2b'], 'Exp 2B')

    # Merge rankings
    rank_merged = rank_ctrl[['striker_id', 'player_name', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
        columns={'tier': 'tier_ctrl', 'tier1_rank': 'rank_ctrl', 'brs3': 'brs3_ctrl', 'bf_hp': 'n_ctrl'}
    )
    for r_obj, pfx in [(rank_exp1a, 'exp1a'), (rank_exp1b, 'exp1b'), (rank_exp2a, 'exp2a'), (rank_exp2b, 'exp2b')]:
        sub_r = r_obj[['striker_id', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
            columns={'tier': f'tier_{pfx}', 'tier1_rank': f'rank_{pfx}', 'brs3': f'brs3_{pfx}', 'bf_hp': f'n_{pfx}'}
        )
        rank_merged = rank_merged.merge(sub_r, on='striker_id', how='left')

    out_rank_path = OUTPUT_DIR / "exp1_exp2_brs3_rankings_comparison.csv"
    rank_merged.to_csv(out_rank_path, index=False)
    print(f"Saved rankings comparison to {out_rank_path}")

    # -------------------------------------------------------------
    # 6. Delivery-Level Classification Comparison Sample
    # -------------------------------------------------------------
    sample_cols = [
        'match_id', 'innings', 'overid', 'innings_ball_num', 'phase', 'batting_order', 'role',
        'striker_id', 'striker_name', 'score_before', 'wickets_before', 'current_run_rate',
        'required_run_rate', 'Batting_PI', 'z_score', 'hp_ctrl', 'hp_exp1a', 'hp_exp1b', 'hp_exp2a', 'hp_exp2b'
    ]
    # Sample contrasting deliveries:
    # Top-order balls that flip to HP under Exp 1A/1B
    flip_top = bat_df[~bat_df['hp_ctrl'] & bat_df['hp_exp1b']].head(30)
    # Death balls that lose HP under Exp 2A/2B
    flip_death = bat_df[bat_df['hp_ctrl'] & ~bat_df['hp_exp2b']].head(30)
    # Control HP sample
    ctrl_sample = bat_df[bat_df['hp_ctrl']].head(40)

    dl_sample = pd.concat([flip_top, flip_death, ctrl_sample]).drop_duplicates().head(100)
    out_dl_path = OUTPUT_DIR / "delivery_level_threshold_comparison.csv"
    dl_sample[sample_cols].to_csv(out_dl_path, index=False)
    print(f"Saved delivery-level comparison sample to {out_dl_path}")

    # Qualification counts summary
    print("\nQualification Summary (Tier 1 Rule B):")
    for r_obj, label in [(rank_ctrl, 'Control'), (rank_exp1a, 'Exp 1A (Top Z>0.75)'), (rank_exp1b, 'Exp 1B (Top Z>0.50)'), (rank_exp2a, 'Exp 2A (Death Z>1.25)'), (rank_exp2b, 'Exp 2B (Death Z>1.50)')]:
        t1 = (r_obj['tier'] == 'Tier 1').sum()
        t2 = (r_obj['tier'] == 'Tier 2').sum()
        print(f"  {label}: Tier 1 = {t1}, Tier 2 = {t2}, Total Qual = {t1 + t2}")


if __name__ == "__main__":
    main()
