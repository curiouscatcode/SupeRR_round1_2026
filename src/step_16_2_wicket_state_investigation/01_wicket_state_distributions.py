"""
Step 16.2: Wicket-State Investigation - Script 01
Wicket-State Baseline Distribution Analysis
============================================================
Investigates adding wickets lost before each delivery (`wickets_before`)
to the batting pressure classification framework.

Evaluates two candidate grouping schemes:
1. 5-Group Scheme (Proposed in Prompt):
   - 0-1 Wickets Lost
   - 2-3 Wickets Lost
   - 4-5 Wickets Lost
   - 6-7 Wickets Lost
   - 8-10 Wickets Lost
   Identifies empty / sparse cells across Innings x Phase combinations.

2. Consolidated 3-Group Scheme (Defensible Merge):
   - Low Wickets: 0-1 Wkts
   - Moderate Wickets: 2-4 Wkts
   - High Wickets / Crisis: 5+ Wkts
   Ensures robust sample sizes in every phase.

Calculates distribution statistics:
- Delivery count, Mean, Std Dev, Median, MAD, Min, Max, Skewness, Kurtosis.

Exports:
- outputs/step_16_2_wicket_state_investigation/wicket_state_baseline_distributions.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_2_wicket_state_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_w_grp_5(w):
    if w in [0, 1]:
        return '0-1 Wkts'
    elif w in [2, 3]:
        return '2-3 Wkts'
    elif w in [4, 5]:
        return '4-5 Wkts'
    elif w in [6, 7]:
        return '6-7 Wkts'
    elif w >= 8:
        return '8-10 Wkts'
    return 'Unknown'


def get_w_grp_3(w):
    if w in [0, 1]:
        return 'Low (0-1 Wkts)'
    elif w in [2, 3, 4]:
        return 'Moderate (2-4 Wkts)'
    elif w >= 5:
        return 'High (5+ Wkts)'
    return 'Unknown'


def calculate_distribution_stats(series: pd.Series, inn: int, phase: str, scheme: str, grp: str) -> dict:
    clean = series.dropna()
    n = len(clean)
    if n == 0:
        return {
            'scheme': scheme, 'innings': inn, 'phase': phase, 'wicket_group': grp,
            'count': 0, 'mean': np.nan, 'std': np.nan, 'median': np.nan, 'mad': np.nan,
            'min': np.nan, 'max': np.nan, 'skewness': np.nan, 'kurtosis': np.nan,
            'effective_cutoff_z1': np.nan, 'sample_adequacy': 'EMPTY'
        }
    
    mean_val = clean.mean()
    std_val = clean.std(ddof=1) if n > 1 else 0.0
    med_val = clean.median()
    mad_val = 1.4826 * (clean - med_val).abs().median()
    min_val = clean.min()
    max_val = clean.max()
    skew_val = clean.skew() if n > 2 else 0.0
    kurt_val = clean.kurtosis() if n > 3 else 0.0
    cutoff = mean_val + std_val

    # Sample adequacy flag
    if n < 50:
        adequacy = 'CRITICALLY_SPARSE'
    elif n < 500:
        adequacy = 'LOW_SAMPLE'
    else:
        adequacy = 'ROBUST'

    return {
        'scheme': scheme,
        'innings': inn,
        'phase': phase,
        'wicket_group': grp,
        'count': n,
        'mean': round(mean_val, 4),
        'std': round(std_val, 4),
        'median': round(med_val, 4),
        'mad': round(mad_val, 4),
        'min': round(min_val, 4),
        'max': round(max_val, 4),
        'skewness': round(skew_val, 4),
        'kurtosis': round(kurt_val, 4),
        'effective_cutoff_z1': round(cutoff, 4),
        'sample_adequacy': adequacy
    }


def main():
    print("=== Step 16.2 Script 01: Wicket-State Baseline Distribution Analysis ===")

    # 1. Load active cleaned dataset
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    df = raw_df[~tail_mask].copy()

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    print(f"Total Batting Balls Faced: {len(bat_df):,}")

    bat_df['w_grp_5'] = bat_df['wickets_before'].apply(get_w_grp_5)
    bat_df['w_grp_3'] = bat_df['wickets_before'].apply(get_w_grp_3)

    phases = ['PP', 'Middle', 'Death']
    stats_rows = []

    # -------------------------------------------------------------
    # 2. Scheme 1: 5-Group Wicket Scheme
    # -------------------------------------------------------------
    w_groups_5 = ['0-1 Wkts', '2-3 Wkts', '4-5 Wkts', '6-7 Wkts', '8-10 Wkts']
    for inn in [1, 2]:
        for ph in phases:
            for grp in w_groups_5:
                sub = bat_df[(bat_df['innings'] == inn) & (bat_df['phase'] == ph) & (bat_df['w_grp_5'] == grp)]
                stats_rows.append(calculate_distribution_stats(sub['Batting_PI'], inn, ph, '5-Group Scheme', grp))

    # -------------------------------------------------------------
    # 3. Scheme 2: Consolidated 3-Group Scheme
    # -------------------------------------------------------------
    w_groups_3 = ['Low (0-1 Wkts)', 'Moderate (2-4 Wkts)', 'High (5+ Wkts)']
    for inn in [1, 2]:
        for ph in phases:
            for grp in w_groups_3:
                sub = bat_df[(bat_df['innings'] == inn) & (bat_df['phase'] == ph) & (bat_df['w_grp_3'] == grp)]
                stats_rows.append(calculate_distribution_stats(sub['Batting_PI'], inn, ph, '3-Group Scheme', grp))

    stats_df = pd.DataFrame(stats_rows)
    out_path = OUTPUT_DIR / "wicket_state_baseline_distributions.csv"
    stats_df.to_csv(out_path, index=False)
    print(f"Saved wicket-state baseline distributions to {out_path}")

    # Inspect Sparse Cells in 5-Group Scheme
    sparse_5 = stats_df[(stats_df['scheme'] == '5-Group Scheme') & (stats_df['sample_adequacy'].isin(['CRITICALLY_SPARSE', 'EMPTY']))]
    print("\nIdentified Sparse / Empty Cells in 5-Group Scheme:")
    print(sparse_5[['innings', 'phase', 'wicket_group', 'count', 'mean', 'std', 'sample_adequacy']])

    # Compare cutoffs between 0-1 wkts vs 8-10 wkts
    print("\nCutoff Comparison (0-1 Wkts vs 8-10 Wkts across phases):")
    extreme_comp = stats_df[stats_df['wicket_group'].isin(['0-1 Wkts', '8-10 Wkts'])][['innings', 'phase', 'wicket_group', 'count', 'mean', 'std', 'effective_cutoff_z1']]
    print(extreme_comp)


if __name__ == "__main__":
    main()
