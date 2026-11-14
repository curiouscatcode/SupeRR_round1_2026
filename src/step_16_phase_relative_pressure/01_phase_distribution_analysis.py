"""
Step 16: Phase-Relative Pressure Classification - Script 01
Phase Distribution Analysis
============================================================
Calculates distribution statistics for Batting PI and Bowling PI across:
- Overall dataset
- Match phases (PP, Middle, Death) combined across innings (Approach A)
- Match phases by innings (Approach B: PP Inn 1/2, Middle Inn 1/2, Death Inn 1/2)
- Competition splits (IPL vs T20I) for stability check (Approach C)

Exports:
- outputs/step_16_phase_relative_pressure/phase_distribution_statistics.csv
- outputs/step_16_phase_relative_pressure/innings_phase_distribution_comparison.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path("data")
PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_phase_relative_pressure")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_distribution_stats(series: pd.Series, group_name: str, metric_name: str) -> dict:
    """Calculate comprehensive distribution statistics for a numeric Series."""
    clean_s = series.dropna()
    n = len(clean_s)
    if n == 0:
        return {}
    
    mean_val = clean_s.mean()
    std_val = clean_s.std(ddof=1)
    median_val = clean_s.median()
    mad_val = 1.4826 * (clean_s - median_val).abs().median()
    min_val = clean_s.min()
    max_val = clean_s.max()
    p25 = clean_s.quantile(0.25)
    p50 = median_val
    p75 = clean_s.quantile(0.75)
    p90 = clean_s.quantile(0.90)
    p95 = clean_s.quantile(0.95)
    iqr = p75 - p25
    skew_val = clean_s.skew()
    kurt_val = clean_s.kurtosis()

    return {
        'group': group_name,
        'metric': metric_name,
        'count': n,
        'mean': round(mean_val, 4),
        'std': round(std_val, 4),
        'median': round(median_val, 4),
        'mad': round(mad_val, 4),
        'min': round(min_val, 4),
        'p25': round(p25, 4),
        'p50': round(p50, 4),
        'p75': round(p75, 4),
        'p90': round(p90, 4),
        'p95': round(p95, 4),
        'max': round(max_val, 4),
        'iqr': round(iqr, 4),
        'skewness': round(skew_val, 4),
        'kurtosis': round(kurt_val, 4)
    }


def main():
    print("--- Step 16: Phase Distribution Analysis ---")
    
    # 1. Load delivery data
    delivery_path = PROCESSED_DIR / "delivery_pressure_index.csv"
    print(f"Loading delivery data from {delivery_path}...")
    df = pd.read_csv(delivery_path)
    total_raw = len(df)
    print(f"Loaded {total_raw:,} raw deliveries.")

    # 2. Exclude Innings 2 deliveries where runs_required <= 0
    is_target_reached_tail = (df['innings'] == 2) & (df['runs_required'] <= 0)
    n_excluded = is_target_reached_tail.sum()
    print(f"Excluding {n_excluded} second-innings deliveries with runs_required <= 0...")
    assert n_excluded == 233, f"Expected 233 excluded deliveries, got {n_excluded}"
    df = df[~is_target_reached_tail].copy()
    print(f"Active dataset: {len(df):,} deliveries.")

    # 3. Attach competition metadata (IPL vs T20I)
    matches = pd.read_csv(DATA_DIR / "matches.csv")
    comps = pd.read_csv(DATA_DIR / "competitions.csv")
    m = matches.merge(comps, on='comp_id', how='left')

    def get_cat(row):
        name = str(row['comp_name'])
        fmt = str(row['match_format'])
        if 'IPL' in name:
            return 'IPL'
        elif fmt == 'T20I':
            return 'T20I'
        return 'Other T20'

    m['competition_category'] = m.apply(get_cat, axis=1)
    df = df.merge(m[['match_id', 'competition_category']], on='match_id', how='left')
    print("Deliveries by competition category:\n", df['competition_category'].value_counts())

    # 4. Filter for legitimate Batting and Bowling deliveries
    # Batting deliveries: is_batter_ball_faced == 1 (excludes wides)
    # Bowling deliveries: is_legal_ball == 1 (excludes wides and no-balls)
    batting_mask = df['is_batter_ball_faced'] == 1
    bowling_mask = df['is_legal_ball'] == 1

    print(f"Batting balls faced: {batting_mask.sum():,}")
    print(f"Bowling legal balls: {bowling_mask.sum():,}")

    # 5. Compute Distribution Statistics across multiple groupings
    # We will compute both on all active deliveries and specifically on balls faced / legal balls
    # In official SupeRR selector evaluations:
    # Batting metrics are computed on balls faced; Bowling metrics on legal balls.
    # We also inspect all deliveries to observe full index behavior.

    stats_list = []

    # Overall dataset
    stats_list.append(calculate_distribution_stats(df.loc[batting_mask, 'Batting_PI'], 'Overall (Batting BF)', 'Batting_PI'))
    stats_list.append(calculate_distribution_stats(df.loc[bowling_mask, 'Bowling_PI'], 'Overall (Bowling LB)', 'Bowling_PI'))
    stats_list.append(calculate_distribution_stats(df['Batting_PI'], 'Overall (All Deliveries)', 'Batting_PI'))
    stats_list.append(calculate_distribution_stats(df['Bowling_PI'], 'Overall (All Deliveries)', 'Bowling_PI'))

    # Approach A: Phase-only (PP, Middle, Death) combined across innings
    phases = ['PP', 'Middle', 'Death']
    for ph in phases:
        ph_mask = df['phase'] == ph
        stats_list.append(calculate_distribution_stats(df.loc[ph_mask & batting_mask, 'Batting_PI'], f'Phase_{ph} (Batting BF)', 'Batting_PI'))
        stats_list.append(calculate_distribution_stats(df.loc[ph_mask & bowling_mask, 'Bowling_PI'], f'Phase_{ph} (Bowling LB)', 'Bowling_PI'))
        stats_list.append(calculate_distribution_stats(df.loc[ph_mask, 'Batting_PI'], f'Phase_{ph} (All Deliveries)', 'Batting_PI'))
        stats_list.append(calculate_distribution_stats(df.loc[ph_mask, 'Bowling_PI'], f'Phase_{ph} (All Deliveries)', 'Bowling_PI'))

    # Approach B: Phase x Innings
    for inn in [1, 2]:
        inn_mask = df['innings'] == inn
        for ph in phases:
            group_mask = inn_mask & (df['phase'] == ph)
            stats_list.append(calculate_distribution_stats(df.loc[group_mask & batting_mask, 'Batting_PI'], f'Inn{inn}_{ph} (Batting BF)', 'Batting_PI'))
            stats_list.append(calculate_distribution_stats(df.loc[group_mask & bowling_mask, 'Bowling_PI'], f'Inn{inn}_{ph} (Bowling LB)', 'Bowling_PI'))
            stats_list.append(calculate_distribution_stats(df.loc[group_mask, 'Batting_PI'], f'Inn{inn}_{ph} (All Deliveries)', 'Batting_PI'))
            stats_list.append(calculate_distribution_stats(df.loc[group_mask, 'Bowling_PI'], f'Inn{inn}_{ph} (All Deliveries)', 'Bowling_PI'))

    # Approach C: Phase x Competition (IPL vs T20I)
    for comp in ['IPL', 'T20I']:
        comp_mask = df['competition_category'] == comp
        for ph in phases:
            group_mask = comp_mask & (df['phase'] == ph)
            stats_list.append(calculate_distribution_stats(df.loc[group_mask & batting_mask, 'Batting_PI'], f'{comp}_{ph} (Batting BF)', 'Batting_PI'))
            stats_list.append(calculate_distribution_stats(df.loc[group_mask & bowling_mask, 'Bowling_PI'], f'{comp}_{ph} (Bowling LB)', 'Bowling_PI'))

    # Convert to DataFrame and save
    stats_df = pd.DataFrame(stats_list)
    out_csv = OUTPUT_DIR / "phase_distribution_statistics.csv"
    stats_df.to_csv(out_csv, index=False)
    print(f"Saved phase distribution statistics to {out_csv}")

    # 6. Generate innings_phase_distribution_comparison.csv
    # Direct side-by-side comparison of Innings 1 vs Innings 2 across phases
    comparison_rows = []
    for metric, ball_mask, ball_name in [('Batting_PI', batting_mask, 'Batting BF'), ('Bowling_PI', bowling_mask, 'Bowling LB')]:
        for ph in phases:
            inn1_vals = df.loc[(df['innings'] == 1) & (df['phase'] == ph) & ball_mask, metric]
            inn2_vals = df.loc[(df['innings'] == 2) & (df['phase'] == ph) & ball_mask, metric]
            
            mean1 = inn1_vals.mean()
            mean2 = inn2_vals.mean()
            std1 = inn1_vals.std(ddof=1)
            std2 = inn2_vals.std(ddof=1)
            med1 = inn1_vals.median()
            med2 = inn2_vals.median()
            mad1 = 1.4826 * (inn1_vals - med1).abs().median()
            mad2 = 1.4826 * (inn2_vals - med2).abs().median()
            
            # Pooled standard deviation & Cohen's d
            n1 = len(inn1_vals)
            n2 = len(inn2_vals)
            pooled_std = np.sqrt(((n1 - 1) * (std1**2) + (n2 - 1) * (std2**2)) / (n1 + n2 - 2))
            cohens_d = (mean2 - mean1) / pooled_std if pooled_std > 0 else 0.0
            
            comparison_rows.append({
                'metric': metric,
                'population': ball_name,
                'phase': ph,
                'inn1_count': n1,
                'inn1_mean': round(mean1, 4),
                'inn1_median': round(med1, 4),
                'inn1_std': round(std1, 4),
                'inn1_mad': round(mad1, 4),
                'inn2_count': n2,
                'inn2_mean': round(mean2, 4),
                'inn2_median': round(med2, 4),
                'inn2_std': round(std2, 4),
                'inn2_mad': round(mad2, 4),
                'mean_difference_inn2_minus_inn1': round(mean2 - mean1, 4),
                'median_difference_inn2_minus_inn1': round(med2 - med1, 4),
                'std_ratio_inn2_to_inn1': round(std2 / std1, 4) if std1 > 0 else np.nan,
                'cohens_d': round(cohens_d, 4),
                'effect_size_magnitude': 'Negligible' if abs(cohens_d) < 0.2 else ('Small' if abs(cohens_d) < 0.5 else ('Medium' if abs(cohens_d) < 0.8 else 'Large'))
            })

    comp_df = pd.DataFrame(comparison_rows)
    comp_csv = OUTPUT_DIR / "innings_phase_distribution_comparison.csv"
    comp_df.to_csv(comp_csv, index=False)
    print(f"Saved innings phase distribution comparison to {comp_csv}")
    print("\nInnings Comparison Preview:")
    print(comp_df[['metric', 'phase', 'inn1_mean', 'inn2_mean', 'mean_difference_inn2_minus_inn1', 'cohens_d', 'effect_size_magnitude']])


if __name__ == "__main__":
    main()
