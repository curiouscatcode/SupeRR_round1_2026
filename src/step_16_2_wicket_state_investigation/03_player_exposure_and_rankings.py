"""
Step 16.2: Wicket-State Investigation - Script 03
Player Exposure, Qualification & Experimental BRS3 Rankings
============================================================
Calculates and compares player-level impacts:
1. High-pressure delivery counts across all 816 batters for:
   - Control: Approved Step 16 (Phase x Innings Standard Z > 1.0)
   - Experiment 1: 5-Group Wicket-State Scheme (Z > 1.0)
   - Experiment 2: Consolidated 3-Group Wicket-State Scheme (Z > 1.0)
2. Rule B Qualification:
   - Tier 1: N >= 60 OR (N >= 50 AND M >= 6)
   - Tier 2: N >= 40 (and not Tier 1)
   - Excluded: N < 40
3. Experimental BRS3 Rankings:
   - BRS3 = 0.45 * Score_SR + 0.35 * Score_Surv + 0.20 * Score_Diff
   - Bayesian shrinkage K = 50.
   - Evaluates Tier 1 rank movements and Top 10 shifts.

Exports:
- outputs/step_16_2_wicket_state_investigation/player_exposure_and_qualification_comparison.csv
- outputs/step_16_2_wicket_state_investigation/experimental_brs3_rankings_comparison.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_2_wicket_state_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

K = 50.0


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


def compute_group_zscores(df: pd.DataFrame, group_cols: list, val_col: str, fallback_cols: list, min_n: int = 50):
    counts = df.groupby(group_cols)[val_col].transform('count')
    means = df.groupby(group_cols)[val_col].transform('mean')
    stds = df.groupby(group_cols)[val_col].transform('std')

    fb_means = df.groupby(fallback_cols)[val_col].transform('mean')
    fb_stds = df.groupby(fallback_cols)[val_col].transform('std')

    use_fb = (counts < min_n) | stds.isnull() | (stds < 1e-6)
    final_means = np.where(use_fb, fb_means, means)
    final_stds = np.where(use_fb, fb_stds, stds)
    return (df[val_col] - final_means) / final_stds


def calculate_brs3_rankings(bat_df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    """Computes player-level BRS3 scores and rankings for qualified Tier 1 players."""
    # Indicator columns
    bat_df['is_out'] = (bat_df['is_wicket'] & (bat_df['dismissed_player_id'] == bat_df['striker_id'])).astype(int)
    
    bat_df['runs_hp'] = np.where(bat_df[hp_col], bat_df['runs'], 0)
    bat_df['bf_hp'] = np.where(bat_df[hp_col], 1, 0)
    bat_df['out_hp'] = np.where(bat_df[hp_col], bat_df['is_out'], 0)

    bat_df['runs_low'] = np.where(~bat_df[hp_col], bat_df['runs'], 0)
    bat_df['bf_low'] = np.where(~bat_df[hp_col], 1, 0)

    # Aggregate by striker
    agg = bat_df.groupby('striker_id').agg(
        player_name=('striker_name', 'first'),
        bf_hp=('bf_hp', 'sum'),
        runs_hp=('runs_hp', 'sum'),
        out_hp=('out_hp', 'sum'),
        bf_low=('bf_low', 'sum'),
        runs_low=('runs_low', 'sum')
    ).reset_index()

    # Match counts under HP
    hp_matches = (
        bat_df[bat_df[hp_col]]
        .groupby('striker_id')['match_id']
        .nunique()
        .to_dict()
    )
    agg['hp_matches'] = agg['striker_id'].map(hp_matches).fillna(0).astype(int)

    # Population prior rates
    tot_bf_hp = agg['bf_hp'].sum()
    tot_runs_hp = agg['runs_hp'].sum()
    tot_out_hp = agg['out_hp'].sum()
    tot_bf_low = agg['bf_low'].sum()
    tot_runs_low = agg['runs_low'].sum()

    mu_sr_hp = (tot_runs_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 114.0
    mu_out_hp = (tot_out_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 7.0
    mu_sr_low = (tot_runs_low / tot_bf_low) * 100.0 if tot_bf_low > 0 else 140.0

    # Credibility factors
    agg['lambda_hp'] = agg['bf_hp'] / (agg['bf_hp'] + K)
    agg['lambda_low'] = agg['bf_low'] / (agg['bf_low'] + K)

    # Observed rates
    agg['sr_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['runs_hp'] / agg['bf_hp']) * 100.0, mu_sr_hp)
    agg['out_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['out_hp'] / agg['bf_hp']) * 100.0, mu_out_hp)
    agg['sr_obs_low'] = np.where(agg['bf_low'] > 0, (agg['runs_low'] / agg['bf_low']) * 100.0, mu_sr_low)

    # Bayesian shrinkage
    agg['sr_star'] = agg['lambda_hp'] * agg['sr_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_sr_hp
    agg['out_star'] = agg['lambda_hp'] * agg['out_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_out_hp
    agg['surv_star'] = 100.0 - agg['out_star']
    agg['sr_low_star'] = agg['lambda_low'] * agg['sr_obs_low'] + (1.0 - agg['lambda_low']) * mu_sr_low
    agg['diff_sr_star'] = agg['sr_star'] - agg['sr_low_star']

    # Sub-scores [0, 100]
    agg['score_sr'] = np.clip((agg['sr_star'] - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    agg['score_surv'] = np.clip((agg['surv_star'] - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    agg['score_diff'] = np.clip((agg['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)

    # Composite BRS3
    agg['brs3'] = 0.45 * agg['score_sr'] + 0.35 * agg['score_surv'] + 0.20 * agg['score_diff']
    agg['brs3'] = np.round(np.clip(agg['brs3'], 0.0, 100.0), 2)

    # Rule B Tier Assignment
    # Tier 1: N >= 60 OR (N >= 50 AND M >= 6)
    # Tier 2: N >= 40 and not Tier 1
    # Excluded: N < 40
    t1_mask = (agg['bf_hp'] >= 60) | ((agg['bf_hp'] >= 50) & (agg['hp_matches'] >= 6))
    t2_mask = (agg['bf_hp'] >= 40) & ~t1_mask
    
    agg['tier'] = 'Excluded'
    agg.loc[t2_mask, 'tier'] = 'Tier 2'
    agg.loc[t1_mask, 'tier'] = 'Tier 1'

    # Rank within Tier 1
    agg['tier1_rank'] = np.nan
    agg.loc[t1_mask, 'tier1_rank'] = agg.loc[t1_mask, 'brs3'].rank(ascending=False, method='min').astype(int)

    agg['model'] = model_name
    return agg


def main():
    print("=== Step 16.2 Script 03: Player Exposure, Qualification & Rankings ===")

    # 1. Load active cleaned dataset
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    df = raw_df[~tail_mask].copy()

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()

    bat_df['w_grp_5'] = bat_df['wickets_before'].apply(get_w_grp_5)
    bat_df['w_grp_3'] = bat_df['wickets_before'].apply(get_w_grp_3)

    # Compute Z-Scores for all 3 models
    ctrl_means = bat_df.groupby(['innings', 'phase'])['Batting_PI'].transform('mean')
    ctrl_stds = bat_df.groupby(['innings', 'phase'])['Batting_PI'].transform('std')
    bat_df['hp_control'] = (bat_df['Batting_PI'] - ctrl_means) / ctrl_stds > 1.0

    bat_df['hp_exp1_5grp'] = compute_group_zscores(bat_df, ['innings', 'phase', 'w_grp_5'], 'Batting_PI', ['innings', 'phase'], min_n=50) > 1.0
    bat_df['hp_exp2_3grp'] = compute_group_zscores(bat_df, ['innings', 'phase', 'w_grp_3'], 'Batting_PI', ['innings', 'phase'], min_n=50) > 1.0

    # 2. Compute BRS3 Rankings for each model
    print("\nComputing BRS3 rankings for Control (Step 16)...")
    res_ctrl = calculate_brs3_rankings(bat_df.copy(), 'hp_control', 'Control (Step 16)')

    print("Computing BRS3 rankings for Exp 1 (5-Group Wicket State)...")
    res_exp1 = calculate_brs3_rankings(bat_df.copy(), 'hp_exp1_5grp', 'Exp 1 (5-Group)')

    print("Computing BRS3 rankings for Exp 2 (3-Group Wicket State)...")
    res_exp2 = calculate_brs3_rankings(bat_df.copy(), 'hp_exp2_3grp', 'Exp 2 (3-Group)')

    # 3. Qualification Summary
    qual_summary = []
    for r_df, name in [(res_ctrl, 'Control (Step 16)'), (res_exp1, 'Exp 1 (5-Group)'), (res_exp2, 'Exp 2 (3-Group)')]:
        t1 = (r_df['tier'] == 'Tier 1').sum()
        t2 = (r_df['tier'] == 'Tier 2').sum()
        exc = (r_df['tier'] == 'Excluded').sum()
        tot_q = t1 + t2
        p1 = (r_df['bf_hp'] >= 60).sum()
        p2 = ((r_df['bf_hp'] >= 50) & (r_df['bf_hp'] < 60) & (r_df['hp_matches'] >= 6)).sum()

        qual_summary.append({
            'model': name,
            'total_batters': len(r_df),
            'pathway1_n60': p1,
            'pathway2_n50_m6': p2,
            'tier1_rule_b': t1,
            'tier2': t2,
            'total_qualified_n40': tot_q,
            'excluded_n_less_40': exc,
            'mean_sample_tier1': round(r_df.loc[r_df['tier'] == 'Tier 1', 'bf_hp'].mean(), 1),
            'median_sample_tier1': round(r_df.loc[r_df['tier'] == 'Tier 1', 'bf_hp'].median(), 1)
        })

    qual_comp_df = pd.DataFrame(qual_summary)
    out_q_path = OUTPUT_DIR / "player_exposure_and_qualification_comparison.csv"
    qual_comp_df.to_csv(out_q_path, index=False)
    print(f"\nSaved qualification comparison to {out_q_path}")
    print(qual_comp_df[['model', 'tier1_rule_b', 'tier2', 'total_qualified_n40', 'excluded_n_less_40', 'mean_sample_tier1']])

    # 4. Compare Rankings and Rank Movements
    # Merge Control and Exp 1 rankings
    rank_comp = res_ctrl[['striker_id', 'player_name', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
        columns={'tier': 'tier_ctrl', 'tier1_rank': 'rank_ctrl', 'brs3': 'brs3_ctrl', 'bf_hp': 'n_ctrl'}
    )
    rank_comp = rank_comp.merge(
        res_exp1[['striker_id', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
            columns={'tier': 'tier_exp1', 'tier1_rank': 'rank_exp1', 'brs3': 'brs3_exp1', 'bf_hp': 'n_exp1'}
        ),
        on='striker_id', how='left'
    )
    rank_comp = rank_comp.merge(
        res_exp2[['striker_id', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
            columns={'tier': 'tier_exp2', 'tier1_rank': 'rank_exp2', 'brs3': 'brs3_exp2', 'bf_hp': 'n_exp2'}
        ),
        on='striker_id', how='left'
    )

    rank_comp['rank_change_exp1_minus_ctrl'] = rank_comp['rank_exp1'] - rank_comp['rank_ctrl']
    rank_comp['rank_change_exp2_minus_ctrl'] = rank_comp['rank_exp2'] - rank_comp['rank_ctrl']
    rank_comp['n_change_exp1_minus_ctrl'] = rank_comp['n_exp1'] - rank_comp['n_ctrl']

    out_r_path = OUTPUT_DIR / "experimental_brs3_rankings_comparison.csv"
    rank_comp.to_csv(out_r_path, index=False)
    print(f"Saved rankings comparison to {out_r_path}")

    # Inspect Control Top 10 vs Exp 1 Top 10
    print("\n--- Control Top 10 Batters (Step 16 Approach B Z > 1.0) ---")
    top10_ctrl = rank_comp[rank_comp['rank_ctrl'] <= 10].sort_values('rank_ctrl')
    print(top10_ctrl[['rank_ctrl', 'player_name', 'brs3_ctrl', 'n_ctrl', 'rank_exp1', 'brs3_exp1', 'n_exp1', 'rank_change_exp1_minus_ctrl']])

    print("\n--- Exp 1 Top 10 Batters (5-Group Wicket State Z > 1.0) ---")
    top10_exp1 = rank_comp[rank_comp['rank_exp1'] <= 10].sort_values('rank_exp1')
    print(top10_exp1[['rank_exp1', 'player_name', 'brs3_exp1', 'n_exp1', 'rank_ctrl', 'brs3_ctrl', 'n_ctrl']])


if __name__ == "__main__":
    main()
