"""
Step 16: Phase-Relative Pressure Classification - Script 02
Z-Score Calculation & Threshold Investigation
============================================================
Calculates standard and robust Z-scores for:
- Approach A: Phase-only baselines (pooled across innings)
- Approach B: Phase x Innings baselines (separate innings baselines)

Evaluates candidate thresholds:
- Z > 0.0
- Z > 0.5
- Z > 1.0
- Z > 1.5
(and robust equivalents Z_robust > 0.0, 0.5, 1.0, 1.5)
against the existing PI > 60.0 baseline.

Calculates:
- Delivery capture volume and percentages
- Phase balance (PP%, Middle%, Death%)
- Innings balance (Inn 1% vs Inn 2%)
- Player qualification counts (Tier 1 Rule B, Rule A, Tier 2, Total N >= 40)
- Player sample distributions (small sample counts < 20, < 10, mean, median, max)
- Outlier and distribution shape diagnostics

Exports:
- outputs/step_16_phase_relative_pressure/zscore_threshold_comparison.csv
- outputs/step_16_phase_relative_pressure/outlier_and_distribution_analysis.csv
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
    """
    Computes standard and robust Z-scores grouped by group_cols.
    Handles zero/near-zero standard deviation safely.
    """
    grouped = df.groupby(group_cols)[value_col]
    
    means = grouped.transform('mean')
    stds = grouped.transform('std')
    # Safe std
    stds_safe = np.where(stds > 1e-6, stds, np.nan)
    z_std = (df[value_col] - means) / stds_safe

    medians = grouped.transform('median')
    
    # Calculate MAD per group: 1.4826 * median(|x - median|)
    def get_mad(s):
        med = s.median()
        return 1.4826 * (s - med).abs().median()
    
    mads = grouped.transform(get_mad)
    mads_safe = np.where(mads > 1e-6, mads, np.nan)
    z_robust = (df[value_col] - medians) / mads_safe

    df[f'{prefix}_z_std'] = z_std
    df[f'{prefix}_z_robust'] = z_robust
    return df


def evaluate_threshold(df_deliveries: pd.DataFrame, condition_mask: pd.Series, 
                       player_id_col: str, match_id_col: str,
                       total_balls: int, discipline: str, threshold_name: str,
                       grouping_approach: str, z_type: str) -> dict:
    """Evaluate a single classification threshold for delivery and player-level statistics."""
    hp_df = df_deliveries[condition_mask]
    n_hp = len(hp_df)
    pct_hp = round((n_hp / total_balls) * 100.0, 2) if total_balls > 0 else 0.0

    # Phase breakdown
    pp_count = (hp_df['phase'] == 'PP').sum()
    mo_count = (hp_df['phase'] == 'Middle').sum()
    do_count = (hp_df['phase'] == 'Death').sum()
    
    pp_pct = round((pp_count / n_hp) * 100.0, 2) if n_hp > 0 else 0.0
    mo_pct = round((mo_count / n_hp) * 100.0, 2) if n_hp > 0 else 0.0
    do_pct = round((do_count / n_hp) * 100.0, 2) if n_hp > 0 else 0.0

    # Innings breakdown
    inn1_count = (hp_df['innings'] == 1).sum()
    inn2_count = (hp_df['innings'] == 2).sum()
    inn1_pct = round((inn1_count / n_hp) * 100.0, 2) if n_hp > 0 else 0.0
    inn2_pct = round((inn2_count / n_hp) * 100.0, 2) if n_hp > 0 else 0.0

    # Player-level aggregation
    # Count balls under HP and distinct matches under HP
    player_stats = hp_df.groupby(player_id_col).agg(
        n_balls=('phase', 'count'),
        n_matches=(match_id_col, 'nunique')
    ).reset_index()

    # Rule B: N >= 60 OR (N >= 50 AND M >= 6)
    tier1_rule_b = ((player_stats['n_balls'] >= 60) | ((player_stats['n_balls'] >= 50) & (player_stats['n_matches'] >= 6))).sum()
    tier1_rule_a = (player_stats['n_balls'] >= 60).sum()
    tier2 = ((player_stats['n_balls'] >= 40) & ~((player_stats['n_balls'] >= 60) | ((player_stats['n_balls'] >= 50) & (player_stats['n_matches'] >= 6)))).sum()
    total_qualified = (player_stats['n_balls'] >= 40).sum()

    # Small sample counts (from entire active player population)
    # Total unique players who participated in this discipline
    all_players = df_deliveries[player_id_col].unique()
    player_stats_full = pd.DataFrame({player_id_col: all_players}).merge(player_stats, on=player_id_col, how='left')
    player_stats_full['n_balls'] = player_stats_full['n_balls'].fillna(0).astype(int)
    
    n_less_20 = (player_stats_full['n_balls'] < 20).sum()
    n_less_10 = (player_stats_full['n_balls'] < 10).sum()
    n_zero = (player_stats_full['n_balls'] == 0).sum()

    # Qualified player sample size distribution
    qual_df = player_stats[player_stats['n_balls'] >= 40]
    mean_qual_sample = round(qual_df['n_balls'].mean(), 1) if len(qual_df) > 0 else 0.0
    median_qual_sample = round(qual_df['n_balls'].median(), 1) if len(qual_df) > 0 else 0.0
    max_sample = player_stats['n_balls'].max() if len(player_stats) > 0 else 0

    return {
        'discipline': discipline,
        'grouping_approach': grouping_approach,
        'z_type': z_type,
        'threshold_name': threshold_name,
        'hp_deliveries': n_hp,
        'hp_delivery_pct': pct_hp,
        'pp_count': pp_count,
        'pp_share_pct': pp_pct,
        'mo_count': mo_count,
        'mo_share_pct': mo_pct,
        'do_count': do_count,
        'do_share_pct': do_pct,
        'inn1_count': inn1_count,
        'inn1_share_pct': inn1_pct,
        'inn2_count': inn2_count,
        'inn2_share_pct': inn2_pct,
        'tier1_rule_b_count': tier1_rule_b,
        'tier1_rule_a_count': tier1_rule_a,
        'tier2_count': tier2,
        'total_qualified_n40': total_qualified,
        'players_n_less_20': n_less_20,
        'players_n_less_10': n_less_10,
        'players_n_zero': n_zero,
        'mean_sample_qualified': mean_qual_sample,
        'median_sample_qualified': median_qual_sample,
        'max_sample_player': max_sample
    }


def main():
    print("--- Step 16: Z-Score Calculation & Threshold Investigation ---")

    # 1. Load delivery data
    df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    
    # 2. Apply cleaning: exclude Innings 2 deliveries where runs_required <= 0
    clean_mask = ~((df['innings'] == 2) & (df['runs_required'] <= 0))
    df = df[clean_mask].copy()
    print(f"Active dataset: {len(df):,} deliveries.")

    # 3. Create subsets for Batting (balls faced) and Bowling (legal balls)
    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    total_bat_balls = len(bat_df)
    total_bowl_balls = len(bowl_df)
    print(f"Total Batting Balls Faced: {total_bat_balls:,}")
    print(f"Total Bowling Legal Balls: {total_bowl_balls:,}")

    # 4. Compute Z-scores for Batting
    # Approach A: Group by ['phase']
    bat_df = compute_zscores(bat_df, ['phase'], 'Batting_PI', 'appA')
    # Approach B: Group by ['innings', 'phase']
    bat_df = compute_zscores(bat_df, ['innings', 'phase'], 'Batting_PI', 'appB')

    # 5. Compute Z-scores for Bowling
    # Approach A: Group by ['phase']
    bowl_df = compute_zscores(bowl_df, ['phase'], 'Bowling_PI', 'appA')
    # Approach B: Group by ['innings', 'phase']
    bowl_df = compute_zscores(bowl_df, ['innings', 'phase'], 'Bowling_PI', 'appB')

    # 6. Evaluate Candidate Thresholds
    threshold_results = []

    # --- BATTING THRESHOLDS ---
    # Baseline: PI > 60.0
    threshold_results.append(evaluate_threshold(
        bat_df, bat_df['Batting_PI'] > 60.0, 'striker_id', 'match_id',
        total_bat_balls, 'Batting', 'PI > 60.0 (Baseline)', 'Baseline', 'None'
    ))

    # Candidate Z thresholds
    z_cutoffs = [0.0, 0.5, 1.0, 1.5]

    for app_code, app_name in [('appA', 'Approach A (Phase-only)'), ('appB', 'Approach B (Phase x Innings)')]:
        # Standard Z
        for z_cut in z_cutoffs:
            threshold_results.append(evaluate_threshold(
                bat_df, bat_df[f'{app_code}_z_std'] > z_cut, 'striker_id', 'match_id',
                total_bat_balls, 'Batting', f'Z > {z_cut}', app_name, 'Standard Z'
            ))
        # Robust Z
        for z_cut in z_cutoffs:
            threshold_results.append(evaluate_threshold(
                bat_df, bat_df[f'{app_code}_z_robust'] > z_cut, 'striker_id', 'match_id',
                total_bat_balls, 'Batting', f'Z_robust > {z_cut}', app_name, 'Robust Z'
            ))

    # --- BOWLING THRESHOLDS ---
    # Baseline: PI > 60.0
    threshold_results.append(evaluate_threshold(
        bowl_df, bowl_df['Bowling_PI'] > 60.0, 'bowler_id', 'match_id',
        total_bowl_balls, 'Bowling', 'PI > 60.0 (Baseline)', 'Baseline', 'None'
    ))

    for app_code, app_name in [('appA', 'Approach A (Phase-only)'), ('appB', 'Approach B (Phase x Innings)')]:
        # Standard Z
        for z_cut in z_cutoffs:
            threshold_results.append(evaluate_threshold(
                bowl_df, bowl_df[f'{app_code}_z_std'] > z_cut, 'bowler_id', 'match_id',
                total_bowl_balls, 'Bowling', f'Z > {z_cut}', app_name, 'Standard Z'
            ))
        # Robust Z
        for z_cut in z_cutoffs:
            threshold_results.append(evaluate_threshold(
                bowl_df, bowl_df[f'{app_code}_z_robust'] > z_cut, 'bowler_id', 'match_id',
                total_bowl_balls, 'Bowling', f'Z_robust > {z_cut}', app_name, 'Robust Z'
            ))

    thresh_df = pd.DataFrame(threshold_results)
    out_thresh_csv = OUTPUT_DIR / "zscore_threshold_comparison.csv"
    thresh_df.to_csv(out_thresh_csv, index=False)
    print(f"Saved threshold comparison to {out_thresh_csv}")

    # 7. Outlier and Distribution Analysis
    # Analyze distribution shape, cutoffs, and extreme values for both approaches
    outlier_rows = []

    def analyze_distribution_diagnostics(series: pd.Series, name: str, discipline: str):
        s = series.dropna()
        p1 = s.quantile(0.01)
        p5 = s.quantile(0.05)
        p25 = s.quantile(0.25)
        p50 = s.median()
        p75 = s.quantile(0.75)
        p95 = s.quantile(0.95)
        p99 = s.quantile(0.99)
        min_v = s.min()
        max_v = s.max()
        mean_v = s.mean()
        std_v = s.std(ddof=1)
        mad_v = 1.4826 * (s - p50).abs().median()
        skew_v = s.skew()
        kurt_v = s.kurtosis()
        
        # Empirical percentiles of specific cutoffs
        pct_z0 = (s > 0.0).mean() * 100.0
        pct_z05 = (s > 0.5).mean() * 100.0
        pct_z10 = (s > 1.0).mean() * 100.0
        pct_z15 = (s > 1.5).mean() * 100.0

        return {
            'discipline': discipline,
            'distribution_name': name,
            'count': len(s),
            'mean': round(mean_v, 4),
            'std': round(std_v, 4),
            'median': round(p50, 4),
            'mad': round(mad_v, 4),
            'skewness': round(skew_v, 4),
            'kurtosis': round(kurt_v, 4),
            'min': round(min_v, 4),
            'p1': round(p1, 4),
            'p5': round(p5, 4),
            'p25': round(p25, 4),
            'p75': round(p75, 4),
            'p95': round(p95, 4),
            'p99': round(p99, 4),
            'max': round(max_v, 4),
            'pct_above_0_0': round(pct_z0, 2),
            'pct_above_0_5': round(pct_z05, 2),
            'pct_above_1_0': round(pct_z10, 2),
            'pct_above_1_5': round(pct_z15, 2),
            'theoretical_normal_pct_z0': 50.00,
            'theoretical_normal_pct_z05': 30.85,
            'theoretical_normal_pct_z10': 15.87,
            'theoretical_normal_pct_z15': 6.68
        }

    # Batting distributions
    outlier_rows.append(analyze_distribution_diagnostics(bat_df['Batting_PI'], 'Raw Batting_PI', 'Batting'))
    outlier_rows.append(analyze_distribution_diagnostics(bat_df['appA_z_std'], 'Approach A Standard Z (Phase-only)', 'Batting'))
    outlier_rows.append(analyze_distribution_diagnostics(bat_df['appA_z_robust'], 'Approach A Robust Z (Phase-only)', 'Batting'))
    outlier_rows.append(analyze_distribution_diagnostics(bat_df['appB_z_std'], 'Approach B Standard Z (Phase x Innings)', 'Batting'))
    outlier_rows.append(analyze_distribution_diagnostics(bat_df['appB_z_robust'], 'Approach B Robust Z (Phase x Innings)', 'Batting'))

    # Bowling distributions
    outlier_rows.append(analyze_distribution_diagnostics(bowl_df['Bowling_PI'], 'Raw Bowling_PI', 'Bowling'))
    outlier_rows.append(analyze_distribution_diagnostics(bowl_df['appA_z_std'], 'Approach A Standard Z (Phase-only)', 'Bowling'))
    outlier_rows.append(analyze_distribution_diagnostics(bowl_df['appA_z_robust'], 'Approach A Robust Z (Phase-only)', 'Bowling'))
    outlier_rows.append(analyze_distribution_diagnostics(bowl_df['appB_z_std'], 'Approach B Standard Z (Phase x Innings)', 'Bowling'))
    outlier_rows.append(analyze_distribution_diagnostics(bowl_df['appB_z_robust'], 'Approach B Robust Z (Phase x Innings)', 'Bowling'))

    outlier_df = pd.DataFrame(outlier_rows)
    out_outlier_csv = OUTPUT_DIR / "outlier_and_distribution_analysis.csv"
    outlier_df.to_csv(out_outlier_csv, index=False)
    print(f"Saved outlier and distribution analysis to {out_outlier_csv}")


if __name__ == "__main__":
    main()
