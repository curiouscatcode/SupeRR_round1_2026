"""
Investigation D — Impact on Player Rankings Across Audit Models
===============================================================

This script evaluates the downstream impact of the audited flaws by recalculating
player performance evaluations and Bayesian reliability rankings across 5 models:
  0. Model 0: Baseline (Official Step 6.2 Model)
  1. Model 1: Innings Workload Alternative (min(100, innings_balls/24 * 100))
  2. Model 2: Phase-Relative Top 20% Alternative (80th percentile cutoff per phase)
  3. Model 3: Alternative Second-Innings Powerplay Weights (Variant 1: T = 0.65R + 0.20W + 0.15O)
  4. Model 4: Combined Experimental Alternative (Innings Workload + Phase-Relative + Alt 2nd Innings PP)

Integrity Rules Preserved:
- Strict Bayesian shrinkage with K = 50.0.
- Exact empirical population priors calculated dynamically for each model.
- Identical sub-score normalizations and 40/25/20/15 composite weights.
- Identical Tier 1 (N >= 60) and Tier 2 (40 <= N < 60) qualification rules.
- Original datasets and official rankings remain completely untouched.

Outputs:
- outputs/pressure_index_audit/07_ranking_correlation_matrix.png
- outputs/pressure_index_audit/08_rank_movement_comparison.png
- outputs/pressure_index_audit/experimental_rankings_comparison_batters.csv
- outputs/pressure_index_audit/experimental_rankings_comparison_bowlers.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/pressure_index_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

K = 50.0
BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']


def calculate_spearman_corr(series_a: pd.Series, series_b: pd.Series) -> float:
    """Compute Spearman rank correlation using Pearson correlation of ranks."""
    valid_mask = series_a.notna() & series_b.notna()
    if valid_mask.sum() < 2:
        return np.nan
    rank_a = series_a[valid_mask].rank()
    rank_b = series_b[valid_mask].rank()
    return rank_a.corr(rank_b)


def evaluate_and_rank_batters(df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    """Aggregate batter performance under a specified high pressure definition and compute BRS."""
    bf_df = df[df['is_batter_ball_faced'] == 1].copy()

    bf_df['is_bnd'] = (bf_df['is_four'] | bf_df['is_six']).astype(int)
    bf_df['is_dot'] = (bf_df['runs'] == 0).astype(int)
    bf_df['is_out'] = (bf_df['is_wicket'] & (bf_df['dismissed_player_id'] == bf_df['striker_id'])).astype(int)

    is_hp = bf_df[hp_col]

    bf_df['runs_high'] = np.where(is_hp, bf_df['runs'], 0)
    bf_df['bf_high'] = np.where(is_hp, 1, 0)
    bf_df['out_high'] = np.where(is_hp, bf_df['is_out'], 0)
    bf_df['bnd_high'] = np.where(is_hp, bf_df['is_bnd'], 0)
    bf_df['dot_high'] = np.where(is_hp, bf_df['is_dot'], 0)

    bf_df['runs_low'] = np.where(~is_hp, bf_df['runs'], 0)
    bf_df['bf_low'] = np.where(~is_hp, 1, 0)

    # Aggregate by batter
    b_agg = bf_df.groupby(['striker_id', 'striker_name']).agg(
        total_bf=('is_batter_ball_faced', 'count'),
        high_runs=('runs_high', 'sum'),
        high_balls_faced=('bf_high', 'sum'),
        high_dismissals=('out_high', 'sum'),
        high_boundaries=('bnd_high', 'sum'),
        high_dot_balls=('dot_high', 'sum'),
        low_mod_runs=('runs_low', 'sum'),
        low_mod_balls_faced=('bf_low', 'sum')
    ).reset_index().rename(columns={'striker_id': 'player_id', 'striker_name': 'player_name'})

    # Empirical population priors
    sum_bf_h = b_agg['high_balls_faced'].sum()
    sum_bf_l = b_agg['low_mod_balls_faced'].sum()

    mu_sr_h = (b_agg['high_runs'].sum() / sum_bf_h) * 100.0 if sum_bf_h > 0 else 114.0475
    mu_out_h = (b_agg['high_dismissals'].sum() / sum_bf_h) * 100.0 if sum_bf_h > 0 else 7.0859
    mu_bnd_h = (b_agg['high_boundaries'].sum() / sum_bf_h) * 100.0 if sum_bf_h > 0 else 14.1504
    mu_dot_h = (b_agg['high_dot_balls'].sum() / sum_bf_h) * 100.0 if sum_bf_h > 0 else 44.8431
    mu_sr_l = (b_agg['low_mod_runs'].sum() / sum_bf_l) * 100.0 if sum_bf_l > 0 else 143.5157

    # Bayesian Credibility
    lam_h = b_agg['high_balls_faced'] / (b_agg['high_balls_faced'] + K)
    lam_l = b_agg['low_mod_balls_faced'] / (b_agg['low_mod_balls_faced'] + K)

    sr_obs = np.where(b_agg['high_balls_faced'] > 0, (b_agg['high_runs'] / b_agg['high_balls_faced']) * 100.0, mu_sr_h)
    out_obs = np.where(b_agg['high_balls_faced'] > 0, (b_agg['high_dismissals'] / b_agg['high_balls_faced']) * 100.0, mu_out_h)
    bnd_obs = np.where(b_agg['high_balls_faced'] > 0, (b_agg['high_boundaries'] / b_agg['high_balls_faced']) * 100.0, mu_bnd_h)
    dot_obs = np.where(b_agg['high_balls_faced'] > 0, (b_agg['high_dot_balls'] / b_agg['high_balls_faced']) * 100.0, mu_dot_h)
    sr_low_obs = np.where(b_agg['low_mod_balls_faced'] > 0, (b_agg['low_mod_runs'] / b_agg['low_mod_balls_faced']) * 100.0, mu_sr_l)

    sr_star = lam_h * sr_obs + (1.0 - lam_h) * mu_sr_h
    out_star = lam_h * out_obs + (1.0 - lam_h) * mu_out_h
    surv_star = 100.0 - out_star
    bnd_star = lam_h * bnd_obs + (1.0 - lam_h) * mu_bnd_h
    dot_star = lam_h * dot_obs + (1.0 - lam_h) * mu_dot_h
    exec_star = bnd_star - 0.5 * dot_star

    sr_low_star = lam_l * sr_low_obs + (1.0 - lam_l) * mu_sr_l
    diff_sr_star = sr_star - sr_low_star

    score_sr = np.clip((sr_star - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    score_surv = np.clip((surv_star - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    score_exec = np.clip((exec_star + 20.0) / 25.0 * 100.0, 0.0, 100.0)
    score_diff = np.clip((diff_sr_star + 60.0) / 80.0 * 100.0, 0.0, 100.0)

    brs = 0.40 * score_sr + 0.25 * score_surv + 0.20 * score_exec + 0.15 * score_diff

    b_agg[f'brs_{model_name}'] = np.round(brs, 2)
    b_agg[f'hp_balls_{model_name}'] = b_agg['high_balls_faced']

    # Tier assignment
    t1_mask = b_agg[f'hp_balls_{model_name}'] >= 60
    t2_mask = (b_agg[f'hp_balls_{model_name}'] >= 40) & ~t1_mask

    b_agg[f'tier_{model_name}'] = 'Below Threshold'
    b_agg.loc[t1_mask, f'tier_{model_name}'] = 'Tier 1'
    b_agg.loc[t2_mask, f'tier_{model_name}'] = 'Tier 2'

    b_agg[f'rank_{model_name}'] = np.nan
    b_agg.loc[t1_mask, f'rank_{model_name}'] = b_agg.loc[t1_mask, f'brs_{model_name}'].rank(ascending=False, method='min').astype(int)

    return b_agg[['player_id', 'player_name', f'hp_balls_{model_name}', f'brs_{model_name}', f'tier_{model_name}', f'rank_{model_name}']]


def evaluate_and_rank_bowlers(df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    """Aggregate bowler performance under a specified high pressure definition and compute BoRS."""
    lb_df = df[df['is_legal_ball'] == 1].copy()

    is_bowler_wk = (lb_df['is_wicket'] == 1) & (lb_df['dismissal_type'].isin(BOWLER_WICKET_TYPES))
    lb_df['is_wk_int'] = is_bowler_wk.astype(int)
    lb_df['is_dot'] = (lb_df['bowler_runs_conceded'] == 0).astype(int)

    is_hp = lb_df[hp_col]

    lb_df['rc_high'] = np.where(is_hp, lb_df['bowler_runs_conceded'], 0)
    lb_df['lb_high'] = np.where(is_hp, 1, 0)
    lb_df['wk_high'] = np.where(is_hp, lb_df['is_wk_int'], 0)
    lb_df['dot_high'] = np.where(is_hp, lb_df['is_dot'], 0)

    lb_df['rc_low'] = np.where(~is_hp, lb_df['bowler_runs_conceded'], 0)
    lb_df['lb_low'] = np.where(~is_hp, 1, 0)

    bo_agg = lb_df.groupby(['bowler_id', 'bowler_name']).agg(
        total_lb=('is_legal_ball', 'count'),
        high_runs_conceded=('rc_high', 'sum'),
        high_legal_balls=('lb_high', 'sum'),
        high_wickets=('wk_high', 'sum'),
        high_dot_balls=('dot_high', 'sum'),
        low_mod_runs_conceded=('rc_low', 'sum'),
        low_mod_legal_balls=('lb_low', 'sum')
    ).reset_index().rename(columns={'bowler_id': 'player_id', 'bowler_name': 'player_name'})

    sum_lb_h = bo_agg['high_legal_balls'].sum()
    sum_lb_l = bo_agg['low_mod_legal_balls'].sum()

    mu_econ_h = (bo_agg['high_runs_conceded'].sum() / sum_lb_h) * 6.0 if sum_lb_h > 0 else 9.0579
    mu_wk_h = (bo_agg['high_wickets'].sum() / sum_lb_h) * 100.0 if sum_lb_h > 0 else 4.8179
    mu_dot_h = (bo_agg['high_dot_balls'].sum() / sum_lb_h) * 100.0 if sum_lb_h > 0 else 39.3885
    mu_econ_l = (bo_agg['low_mod_runs_conceded'].sum() / sum_lb_l) * 6.0 if sum_lb_l > 0 else 8.6426

    lam_h = bo_agg['high_legal_balls'] / (bo_agg['high_legal_balls'] + K)
    lam_l = bo_agg['low_mod_legal_balls'] / (bo_agg['low_mod_legal_balls'] + K)

    econ_obs = np.where(bo_agg['high_legal_balls'] > 0, (bo_agg['high_runs_conceded'] / bo_agg['high_legal_balls']) * 6.0, mu_econ_h)
    wk_obs = np.where(bo_agg['high_legal_balls'] > 0, (bo_agg['high_wickets'] / bo_agg['high_legal_balls']) * 100.0, mu_wk_h)
    dot_obs = np.where(bo_agg['high_legal_balls'] > 0, (bo_agg['high_dot_balls'] / bo_agg['high_legal_balls']) * 100.0, mu_dot_h)
    econ_low_obs = np.where(bo_agg['low_mod_legal_balls'] > 0, (bo_agg['low_mod_runs_conceded'] / bo_agg['low_mod_legal_balls']) * 6.0, mu_econ_l)

    econ_star = lam_h * econ_obs + (1.0 - lam_h) * mu_econ_h
    wk_star = lam_h * wk_obs + (1.0 - lam_h) * mu_wk_h
    dot_star = lam_h * dot_obs + (1.0 - lam_h) * mu_dot_h
    econ_low_star = lam_l * econ_low_obs + (1.0 - lam_l) * mu_econ_l
    diff_econ_star = econ_low_star - econ_star

    score_econ = np.clip((12.00 - econ_star) / 6.00 * 100.0, 0.0, 100.0)
    score_wk = np.clip((wk_star - 1.50) / 7.50 * 100.0, 0.0, 100.0)
    score_dot = np.clip((dot_star - 25.0) / 25.0 * 100.0, 0.0, 100.0)
    score_diff = np.clip((diff_econ_star + 3.00) / 5.00 * 100.0, 0.0, 100.0)

    bors = 0.40 * score_econ + 0.25 * score_wk + 0.20 * score_dot + 0.15 * score_diff

    bo_agg[f'bors_{model_name}'] = np.round(bors, 2)
    bo_agg[f'hp_balls_{model_name}'] = bo_agg['high_legal_balls']

    t1_mask = bo_agg[f'hp_balls_{model_name}'] >= 60
    t2_mask = (bo_agg[f'hp_balls_{model_name}'] >= 40) & ~t1_mask

    bo_agg[f'tier_{model_name}'] = 'Below Threshold'
    bo_agg.loc[t1_mask, f'tier_{model_name}'] = 'Tier 1'
    bo_agg.loc[t2_mask, f'tier_{model_name}'] = 'Tier 2'

    bo_agg[f'rank_{model_name}'] = np.nan
    bo_agg.loc[t1_mask, f'rank_{model_name}'] = bo_agg.loc[t1_mask, f'bors_{model_name}'].rank(ascending=False, method='min').astype(int)

    return bo_agg[['player_id', 'player_name', f'hp_balls_{model_name}', f'bors_{model_name}', f'tier_{model_name}', f'rank_{model_name}']]


def run_ranking_impact_audit():
    print("Loading delivery_pressure_index.csv...")
    df = pd.read_csv(DATA_DIR / "delivery_pressure_index.csv")
    total_deliveries = len(df)
    print(f"Total deliveries: {total_deliveries:,}")

    # 1. Prepare Columns for the 5 Models
    print("Preparing delivery columns for all 5 audit models...")

    # A. Model 0: Baseline
    df['hp_bat_m0'] = df['Batting_PI'] > 60.0
    df['hp_bowl_m0'] = df['Bowling_PI'] > 60.0

    # B. Model 1: Innings Workload for Bowlers
    cum_legal = df.groupby(['match_id', 'innings', 'bowler_id'])['is_legal_ball'].cumsum() - df['is_legal_ball']
    df['b_workload_innings'] = np.clip((cum_legal / 24.0) * 100.0, 0.0, 100.0)
    df['b_workload_spell'] = np.clip((df['bowler_legal_balls_in_spell_before'] / 12.0) * 100.0, 0.0, 100.0)
    delta_workload = df['b_workload_innings'] - df['b_workload_spell']
    df['bowling_pi_m1'] = np.clip(df['Bowling_PI'] + 0.175 * delta_workload, 0.0, 100.0)

    df['hp_bat_m1'] = df['hp_bat_m0']  # Batters unaffected by bowler workload
    df['hp_bowl_m1'] = df['bowling_pi_m1'] > 60.0

    # C. Model 2: Phase-Relative Top 20%
    p80_bat = {}
    p80_bowl = {}
    for ph in ['PP', 'Middle', 'Death']:
        sub = df[df['phase'] == ph]
        p80_bat[ph] = np.percentile(sub['Batting_PI'].dropna(), 80)
        p80_bowl[ph] = np.percentile(sub['Bowling_PI'].dropna(), 80)

    df['bat_p80_thresh'] = df['phase'].map(p80_bat)
    df['bowl_p80_thresh'] = df['phase'].map(p80_bowl)

    df['hp_bat_m2'] = df['Batting_PI'] > df['bat_p80_thresh']
    df['hp_bowl_m2'] = df['Bowling_PI'] > df['bowl_p80_thresh']

    # D. Model 3: Alternative 2nd Innings PP Weights for Batters
    # Variant 1: T = 0.65*R + 0.20*W + 0.15*O, PI = 0.75*T + 0.25*I
    is_inn2_pp = (df['innings'] == 2) & (df['phase'] == 'PP')
    r_act = np.clip(((df['required_run_rate'] - 6.0) / 6.0) * 100.0, 0.0, 100.0)
    w_act = np.clip((df['wickets_before'] / 6.0) * 100.0, 0.0, 100.0)
    o_act = np.clip((df['phase_overs_completed'] / 6.0) * 100.0, 0.0, 100.0)
    i_act = np.clip(((10.0 - df['striker_balls_faced_before']) / 10.0) * 100.0, 0.0, 100.0)

    t_v1 = 0.65 * r_act + 0.20 * w_act + 0.15 * o_act
    pi_b2_pp_v1 = 0.75 * t_v1 + 0.25 * i_act

    df['batting_pi_m3'] = df['Batting_PI']
    df.loc[is_inn2_pp, 'batting_pi_m3'] = pi_b2_pp_v1[is_inn2_pp]

    df['hp_bat_m3'] = df['batting_pi_m3'] > 60.0
    df['hp_bowl_m3'] = df['hp_bowl_m0'] # Bowlers unaffected

    # E. Model 4: Combined Experimental Alternative
    # Uses batting_pi_m3 for batters, bowling_pi_m1 for bowlers, and applies phase-relative top 20% to both!
    p80_bat_m4 = {}
    p80_bowl_m4 = {}
    for ph in ['PP', 'Middle', 'Death']:
        sub = df[df['phase'] == ph]
        p80_bat_m4[ph] = np.percentile(sub['batting_pi_m3'].dropna(), 80)
        p80_bowl_m4[ph] = np.percentile(sub['bowling_pi_m1'].dropna(), 80)

    df['hp_bat_m4'] = df['batting_pi_m3'] > df['phase'].map(p80_bat_m4)
    df['hp_bowl_m4'] = df['bowling_pi_m1'] > df['phase'].map(p80_bowl_m4)

    # 2. Evaluate Rankings Across All Models
    model_keys = ['m0', 'm1', 'm2', 'm3', 'm4']
    model_names = {
        'm0': 'Baseline (Step 6.2)',
        'm1': 'Innings Workload',
        'm2': 'Phase-Relative (Top 20%)',
        'm3': 'Alt 2nd Inn PP',
        'm4': 'Combined Model'
    }

    print("\nCalculating Batter Rankings across all 5 models...")
    bat_dfs = []
    for k in model_keys:
        b_res = evaluate_and_rank_batters(df, f'hp_bat_{k}', k)
        bat_dfs.append(b_res)

    bat_merged = bat_dfs[0]
    for b_sub in bat_dfs[1:]:
        bat_merged = bat_merged.merge(b_sub.drop(columns=['player_name']), on='player_id', how='left')

    print("Calculating Bowler Rankings across all 5 models...")
    bowl_dfs = []
    for k in model_keys:
        bo_res = evaluate_and_rank_bowlers(df, f'hp_bowl_{k}', k)
        bowl_dfs.append(bo_res)

    bowl_merged = bowl_dfs[0]
    for bo_sub in bowl_dfs[1:]:
        bowl_merged = bowl_merged.merge(bo_sub.drop(columns=['player_name']), on='player_id', how='left')

    # Save CSVs
    bat_merged.to_csv(OUTPUT_DIR / "experimental_rankings_comparison_batters.csv", index=False)
    bowl_merged.to_csv(OUTPUT_DIR / "experimental_rankings_comparison_bowlers.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'experimental_rankings_comparison_batters.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'experimental_rankings_comparison_bowlers.csv'}")

    # 3. Analyze Correlations, Top 10 Overlap, and Tier 1 Turnover
    print("\n" + "="*70)
    print("BATTER RANKING SENSITIVITY SUMMARY (VS BASELINE M0)")
    print("="*70)

    bat_t1_base_ids = set(bat_merged[bat_merged['tier_m0'] == 'Tier 1']['player_id'])
    bat_top10_base_ids = set(bat_merged[bat_merged['rank_m0'] <= 10]['player_id'])

    for k in ['m1', 'm2', 'm3', 'm4']:
        # Spearman correlation on BRS across all players
        rho_all = calculate_spearman_corr(bat_merged['brs_m0'], bat_merged[f'brs_{k}'])
        
        # Spearman correlation on ranks for players qualified in BOTH models
        both_t1 = (bat_merged['tier_m0'] == 'Tier 1') & (bat_merged[f'tier_{k}'] == 'Tier 1')
        rho_t1 = calculate_spearman_corr(bat_merged.loc[both_t1, 'rank_m0'], bat_merged.loc[both_t1, f'rank_{k}'])

        # Top 10 Overlap
        top10_k_ids = set(bat_merged[bat_merged[f'rank_{k}'] <= 10]['player_id'])
        top10_overlap = len(bat_top10_base_ids.intersection(top10_k_ids))
        jaccard = top10_overlap / len(bat_top10_base_ids.union(top10_k_ids))

        # Tier 1 Count and Turnover
        t1_k_ids = set(bat_merged[bat_merged[f'tier_{k}'] == 'Tier 1']['player_id'])
        new_entrants = len(t1_k_ids - bat_t1_base_ids)
        dropouts = len(bat_t1_base_ids - t1_k_ids)

        print(f"\n{model_names[k]} (vs Baseline):")
        print(f"  Spearman rho (All Players BRS):  {rho_all:.4f}")
        print(f"  Spearman rho (Tier 1 Ranks):     {rho_t1:.4f}")
        print(f"  Top 10 Overlap:                  {top10_overlap}/10 (Jaccard: {jaccard:.2f})")
        print(f"  Tier 1 Qualified Count:          {len(t1_k_ids)} (Baseline: {len(bat_t1_base_ids)})")
        print(f"  Tier 1 Turnover:                 +{new_entrants} new, -{dropouts} dropped")

    print("\n" + "="*70)
    print("BOWLER RANKING SENSITIVITY SUMMARY (VS BASELINE M0)")
    print("="*70)

    bowl_t1_base_ids = set(bowl_merged[bowl_merged['tier_m0'] == 'Tier 1']['player_id'])
    bowl_top10_base_ids = set(bowl_merged[bowl_merged['rank_m0'] <= 10]['player_id'])

    for k in ['m1', 'm2', 'm3', 'm4']:
        rho_all = calculate_spearman_corr(bowl_merged['bors_m0'], bowl_merged[f'bors_{k}'])
        both_t1 = (bowl_merged['tier_m0'] == 'Tier 1') & (bowl_merged[f'tier_{k}'] == 'Tier 1')
        rho_t1 = calculate_spearman_corr(bowl_merged.loc[both_t1, 'rank_m0'], bowl_merged.loc[both_t1, f'rank_{k}'])

        top10_k_ids = set(bowl_merged[bowl_merged[f'rank_{k}'] <= 10]['player_id'])
        top10_overlap = len(bowl_top10_base_ids.intersection(top10_k_ids))
        jaccard = top10_overlap / len(bowl_top10_base_ids.union(top10_k_ids))

        t1_k_ids = set(bowl_merged[bowl_merged[f'tier_{k}'] == 'Tier 1']['player_id'])
        new_entrants = len(t1_k_ids - bowl_t1_base_ids)
        dropouts = len(bowl_t1_base_ids - t1_k_ids)

        print(f"\n{model_names[k]} (vs Baseline):")
        print(f"  Spearman rho (All Players BoRS): {rho_all:.4f}")
        print(f"  Spearman rho (Tier 1 Ranks):     {rho_t1:.4f}")
        print(f"  Top 10 Overlap:                  {top10_overlap}/10 (Jaccard: {jaccard:.2f})")
        print(f"  Tier 1 Qualified Count:          {len(t1_k_ids)} (Baseline: {len(bowl_t1_base_ids)})")
        print(f"  Tier 1 Turnover:                 +{new_entrants} new, -{dropouts} dropped")

    # 4. Generate Figure 7: Correlation Matrix Heatmap
    print("\nGenerating Figure 7: Correlation Heatmap Across Models...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Batters BRS correlation matrix (Pearson of ranks is mathematically identical to Spearman)
    bat_score_cols = [f'brs_{k}' for k in model_keys]
    bat_corr = bat_merged[bat_score_cols].rank().corr()
    bat_corr.columns = [model_names[k] for k in model_keys]
    bat_corr.index = [model_names[k] for k in model_keys]

    sns.heatmap(bat_corr, annot=True, fmt='.3f', cmap='Blues', vmin=0.85, vmax=1.0, ax=axes[0],
                cbar_kws={'label': 'Spearman Rank Correlation (rho)'})
    axes[0].set_title("A. Batter Reliability Score (BRS) Cross-Model Correlation", fontsize=12, fontweight='bold', pad=10)

    # Bowlers BoRS correlation matrix
    bowl_score_cols = [f'bors_{k}' for k in model_keys]
    bowl_corr = bowl_merged[bowl_score_cols].rank().corr()
    bowl_corr.columns = [model_names[k] for k in model_keys]
    bowl_corr.index = [model_names[k] for k in model_keys]

    sns.heatmap(bowl_corr, annot=True, fmt='.3f', cmap='Oranges', vmin=0.85, vmax=1.0, ax=axes[1],
                cbar_kws={'label': 'Spearman Rank Correlation (rho)'})
    axes[1].set_title("B. Bowler Reliability Score (BoRS) Cross-Model Correlation", fontsize=12, fontweight='bold', pad=10)

    plt.tight_layout()
    fig_path7 = OUTPUT_DIR / "07_ranking_correlation_matrix.png"
    plt.savefig(fig_path7, dpi=300)
    plt.close()
    print(f"Saved: {fig_path7}")

    # 5. Generate Figure 8: Rank Movement Bump / Slope Chart
    print("\nGenerating Figure 8: Top 10 Rank Movement Comparison...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Top 10 Batters in Baseline
    top10_batters = bat_merged[bat_merged['rank_m0'] <= 10].sort_values(by='rank_m0')
    
    # Plotting slopes for Top 10 Batters
    x_points = [0, 1, 2, 3, 4]
    x_labels = ['Baseline', 'Innings Wkld', 'Phase-Rel', 'Alt PP', 'Combined']
    
    for _, row in top10_batters.iterrows():
        ranks = [row[f'rank_{k}'] for k in model_keys]
        p_name = row['player_name']
        axes[0].plot(x_points, ranks, marker='o', lw=2.2, label=f"#{int(row['rank_m0'])} {p_name}")
        axes[0].text(4.05, ranks[4] if pd.notna(ranks[4]) else 25, f"{p_name} (#{int(ranks[4]) if pd.notna(ranks[4]) else 'NQ'})", 
                     va='center', fontsize=8, fontweight='bold')

    axes[0].set_xticks(x_points)
    axes[0].set_xticklabels(x_labels, fontweight='bold')
    axes[0].set_ylabel("Tier 1 Rank (Lower is Better)", fontsize=11, fontweight='bold')
    axes[0].set_title("A. Top 10 Batters: Rank Movement Across Audit Models", fontsize=13, fontweight='bold', pad=10)
    axes[0].invert_yaxis()
    axes[0].set_ylim(25, 0.5)
    axes[0].legend(loc='lower left', frameon=True, fontsize=8)

    # Top 10 Bowlers in Baseline
    top10_bowlers = bowl_merged[bowl_merged['rank_m0'] <= 10].sort_values(by='rank_m0')

    for _, row in top10_bowlers.iterrows():
        ranks = [row[f'rank_{k}'] for k in model_keys]
        p_name = row['player_name']
        axes[1].plot(x_points, ranks, marker='s', lw=2.2, label=f"#{int(row['rank_m0'])} {p_name}")
        axes[1].text(4.05, ranks[4] if pd.notna(ranks[4]) else 25, f"{p_name} (#{int(ranks[4]) if pd.notna(ranks[4]) else 'NQ'})", 
                     va='center', fontsize=8, fontweight='bold')

    axes[1].set_xticks(x_points)
    axes[1].set_xticklabels(x_labels, fontweight='bold')
    axes[1].set_ylabel("Tier 1 Rank (Lower is Better)", fontsize=11, fontweight='bold')
    axes[1].set_title("B. Top 10 Bowlers: Rank Movement Across Audit Models", fontsize=13, fontweight='bold', pad=10)
    axes[1].invert_yaxis()
    axes[1].set_ylim(25, 0.5)
    axes[1].legend(loc='lower left', frameon=True, fontsize=8)

    plt.tight_layout()
    fig_path8 = OUTPUT_DIR / "08_rank_movement_comparison.png"
    plt.savefig(fig_path8, dpi=300)
    plt.close()
    print(f"Saved: {fig_path8}")


if __name__ == "__main__":
    run_ranking_impact_audit()
