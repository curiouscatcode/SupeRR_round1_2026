"""
Step 16.5: Script 03 - Player-Level WPA Reliability Investigation (Section 6)
=============================================================================
Investigates player-level Win Probability Added (WPA) reliability, expected leverage faced,
performance over expectation, and match-to-match consistency.

Performs:
1. Batting Player Reliability:
   - Total balls faced, HP balls faced, HP exposure rate.
   - Total matches, HP matches.
   - HP Signed WPA (sum and mean per ball), Total Signed WPA.
   - HP Absolute WPA (sum and mean).
   - Average expected leverage faced (HP and overall).
   - Match-to-match consistency: std dev of match WPA, % positive matches.
   - Tier assignment (Step 15 Rule B criteria: Tier 1 >= 60 or (>=50 & M>=6); Tier 2 >= 40).
2. Bowling Player Reliability:
   - Bowler legal balls, HP legal balls, Bowler HP Signed WPA (-wpa), Absolute WPA.
   - Average expected leverage faced.
   - Match-to-match consistency.
   - Tier assignment.
3. Summary Comparison of Consistency Metrics.

Outputs:
- outputs/step_16_5_wpa_investigation/player_batting_wpa_reliability.csv
- outputs/step_16_5_wpa_investigation/player_bowling_wpa_reliability.csv
- outputs/step_16_5_wpa_investigation/player_consistency_summary.csv
"""

import os
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_5_wpa_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def assign_tier(n_hp, m_hp):
    if n_hp >= 60 or (n_hp >= 50 and m_hp >= 6):
        return 'Tier 1'
    elif n_hp >= 40:
        return 'Tier 2'
    else:
        return 'Low Sample (<40)'


def main():
    print("=== Step 16.5 Script 03: Player-Level WPA Reliability Analysis ===")
    t0 = time.time()

    # Load master delivery dataset
    parquet_path = OUTPUT_DIR / "delivery_wpa_leverage.parquet"
    print(f"Loading {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # -------------------------------------------------------------
    # 1. BATTING PLAYER RELIABILITY
    # -------------------------------------------------------------
    print("Computing Batting Player Reliability metrics...")
    bat_df = df[df['is_batter_ball_faced'] == 1].copy()

    # Match-level aggregates per batter
    match_bat = bat_df.groupby(['striker_id', 'match_id']).agg(
        match_wpa=('wpa', 'sum'),
        match_balls=('wpa', 'count'),
        match_hp_balls=('is_high_pressure_bat', 'sum'),
        match_hp_wpa=('wpa', lambda x: x[bat_df.loc[x.index, 'is_high_pressure_bat']].sum())
    ).reset_index()

    # Aggregate across matches
    consistency_bat = match_bat.groupby('striker_id').agg(
        matches_played=('match_id', 'count'),
        match_wpa_std=('match_wpa', 'std'),
        match_wpa_iqr=('match_wpa', lambda x: x.quantile(0.75) - x.quantile(0.25)),
        pct_positive_matches=('match_wpa', lambda x: (x > 0).mean() * 100.0)
    ).reset_index()

    # Aggregate full delivery-level stats per batter
    bat_player_total = bat_df.groupby(['striker_id', 'striker_name']).agg(
        total_balls_faced=('wpa', 'count'),
        total_signed_wpa=('wpa', 'sum'),
        mean_overall_leverage=('expected_leverage_pct', 'mean')
    ).reset_index()

    # Aggregate HP delivery-level stats per batter
    bat_hp_df = bat_df[bat_df['is_high_pressure_bat']]
    bat_player_hp = bat_hp_df.groupby('striker_id').agg(
        hp_balls_faced=('wpa', 'count'),
        hp_matches=('match_id', 'nunique'),
        hp_signed_wpa=('wpa', 'sum'),
        hp_mean_wpa_per_ball=('wpa', 'mean'),
        hp_absolute_wpa=('absolute_wpa', 'sum'),
        hp_mean_absolute_wpa=('absolute_wpa', 'mean'),
        hp_mean_expected_leverage=('expected_leverage_pct', 'mean')
    ).reset_index()

    # Merge
    bat_summary = bat_player_total.merge(bat_player_hp, on='striker_id', how='left')
    bat_summary['hp_balls_faced'] = bat_summary['hp_balls_faced'].fillna(0).astype(int)
    bat_summary['hp_matches'] = bat_summary['hp_matches'].fillna(0).astype(int)
    bat_summary['hp_signed_wpa'] = bat_summary['hp_signed_wpa'].fillna(0.0)
    bat_summary['hp_absolute_wpa'] = bat_summary['hp_absolute_wpa'].fillna(0.0)

    bat_summary['hp_exposure_pct'] = (bat_summary['hp_balls_faced'] / bat_summary['total_balls_faced']) * 100.0
    bat_summary['tier'] = bat_summary.apply(lambda r: assign_tier(r['hp_balls_faced'], r['hp_matches']), axis=1)

    # Merge match consistency
    bat_summary = bat_summary.merge(consistency_bat, on='striker_id', how='left')

    # Convert WPA to percentages for display
    bat_summary['total_signed_wpa_pct'] = bat_summary['total_signed_wpa'] * 100.0
    bat_summary['hp_signed_wpa_pct'] = bat_summary['hp_signed_wpa'] * 100.0
    bat_summary['hp_absolute_wpa_pct'] = bat_summary['hp_absolute_wpa'] * 100.0
    bat_summary['match_wpa_std_pct'] = bat_summary['match_wpa_std'] * 100.0
    bat_summary['match_wpa_iqr_pct'] = bat_summary['match_wpa_iqr'] * 100.0

    # Performance relative to expected impact (WPA / Leverage ratio)
    bat_summary['hp_wpa_to_leverage_ratio'] = np.where(
        bat_summary['hp_mean_expected_leverage'] > 0,
        (bat_summary['hp_mean_wpa_per_ball'] * 100.0) / bat_summary['hp_mean_expected_leverage'],
        np.nan
    )

    # Reorder columns
    bat_cols = [
        'striker_id', 'striker_name', 'tier', 'total_balls_faced', 'hp_balls_faced', 'hp_exposure_pct',
        'matches_played', 'hp_matches', 'hp_signed_wpa_pct', 'hp_mean_wpa_per_ball', 'hp_absolute_wpa_pct',
        'hp_mean_expected_leverage', 'hp_wpa_to_leverage_ratio', 'total_signed_wpa_pct',
        'match_wpa_std_pct', 'match_wpa_iqr_pct', 'pct_positive_matches'
    ]
    bat_summary = bat_summary[bat_cols].sort_values(['tier', 'hp_signed_wpa_pct'], ascending=[True, False]).round(3)

    bat_csv = OUTPUT_DIR / "player_batting_wpa_reliability.csv"
    bat_summary.to_csv(bat_csv, index=False)
    print(f"Saved Batting Player Reliability to {bat_csv} (Total batters = {len(bat_summary):,})")

    # -------------------------------------------------------------
    # 2. BOWLING PLAYER RELIABILITY
    # -------------------------------------------------------------
    print("\nComputing Bowling Player Reliability metrics...")
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    # Match-level aggregates per bowler
    match_bowl = bowl_df.groupby(['bowler_id', 'match_id']).agg(
        match_bwpa=('bowler_wpa', 'sum'),
        match_balls=('bowler_wpa', 'count'),
        match_hp_balls=('is_high_pressure_bowl', 'sum')
    ).reset_index()

    consistency_bowl = match_bowl.groupby('bowler_id').agg(
        matches_bowled=('match_id', 'count'),
        match_bwpa_std=('match_bwpa', 'std'),
        match_bwpa_iqr=('match_bwpa', lambda x: x.quantile(0.75) - x.quantile(0.25)),
        pct_positive_matches=('match_bwpa', lambda x: (x > 0).mean() * 100.0)
    ).reset_index()

    # Total legal deliveries
    bowl_player_total = bowl_df.groupby(['bowler_id', 'bowler_name']).agg(
        total_legal_balls=('bowler_wpa', 'count'),
        total_signed_bwpa=('bowler_wpa', 'sum'),
        mean_overall_leverage=('expected_leverage_pct', 'mean')
    ).reset_index()

    # HP legal deliveries
    bowl_hp_df = bowl_df[bowl_df['is_high_pressure_bowl']]
    bowl_player_hp = bowl_hp_df.groupby('bowler_id').agg(
        hp_legal_balls=('bowler_wpa', 'count'),
        hp_matches=('match_id', 'nunique'),
        hp_signed_bwpa=('bowler_wpa', 'sum'),
        hp_mean_bwpa_per_ball=('bowler_wpa', 'mean'),
        hp_absolute_bwpa=('absolute_wpa', 'sum'),
        hp_mean_absolute_bwpa=('absolute_wpa', 'mean'),
        hp_mean_expected_leverage=('expected_leverage_pct', 'mean')
    ).reset_index()

    # Merge
    bowl_summary = bowl_player_total.merge(bowl_player_hp, on='bowler_id', how='left')
    bowl_summary['hp_legal_balls'] = bowl_summary['hp_legal_balls'].fillna(0).astype(int)
    bowl_summary['hp_matches'] = bowl_summary['hp_matches'].fillna(0).astype(int)
    bowl_summary['hp_signed_bwpa'] = bowl_summary['hp_signed_bwpa'].fillna(0.0)
    bowl_summary['hp_absolute_bwpa'] = bowl_summary['hp_absolute_bwpa'].fillna(0.0)

    bowl_summary['hp_exposure_pct'] = (bowl_summary['hp_legal_balls'] / bowl_summary['total_legal_balls']) * 100.0
    bowl_summary['tier'] = bowl_summary.apply(lambda r: assign_tier(r['hp_legal_balls'], r['hp_matches']), axis=1)

    bowl_summary = bowl_summary.merge(consistency_bowl, on='bowler_id', how='left')

    bowl_summary['total_signed_bwpa_pct'] = bowl_summary['total_signed_bwpa'] * 100.0
    bowl_summary['hp_signed_bwpa_pct'] = bowl_summary['hp_signed_bwpa'] * 100.0
    bowl_summary['hp_absolute_bwpa_pct'] = bowl_summary['hp_absolute_bwpa'] * 100.0
    bowl_summary['match_bwpa_std_pct'] = bowl_summary['match_bwpa_std'] * 100.0
    bowl_summary['match_bwpa_iqr_pct'] = bowl_summary['match_bwpa_iqr'] * 100.0

    bowl_summary['hp_bwpa_to_leverage_ratio'] = np.where(
        bowl_summary['hp_mean_expected_leverage'] > 0,
        (bowl_summary['hp_mean_bwpa_per_ball'] * 100.0) / bowl_summary['hp_mean_expected_leverage'],
        np.nan
    )

    bowl_cols = [
        'bowler_id', 'bowler_name', 'tier', 'total_legal_balls', 'hp_legal_balls', 'hp_exposure_pct',
        'matches_bowled', 'hp_matches', 'hp_signed_bwpa_pct', 'hp_mean_bwpa_per_ball', 'hp_absolute_bwpa_pct',
        'hp_mean_expected_leverage', 'hp_bwpa_to_leverage_ratio', 'total_signed_bwpa_pct',
        'match_bwpa_std_pct', 'match_bwpa_iqr_pct', 'pct_positive_matches'
    ]
    bowl_summary = bowl_summary[bowl_cols].sort_values(['tier', 'hp_signed_bwpa_pct'], ascending=[True, False]).round(3)

    bowl_csv = OUTPUT_DIR / "player_bowling_wpa_reliability.csv"
    bowl_summary.to_csv(bowl_csv, index=False)
    print(f"Saved Bowling Player Reliability to {bowl_csv} (Total bowlers = {len(bowl_summary):,})")

    # -------------------------------------------------------------
    # 3. CONSISTENCY & TIER SUMMARY TABLE
    # -------------------------------------------------------------
    print("\nGenerating Player Consistency Summary...")
    tier_summary_rows = []

    for category, p_df, id_col, name_col, wpa_col, lev_col in [
        ('Batting', bat_summary, 'striker_id', 'striker_name', 'hp_signed_wpa_pct', 'hp_mean_expected_leverage'),
        ('Bowling', bowl_summary, 'bowler_id', 'bowler_name', 'hp_signed_bwpa_pct', 'hp_mean_expected_leverage')
    ]:
        for t_name in ['Tier 1', 'Tier 2', 'Low Sample (<40)']:
            sub = p_df[p_df['tier'] == t_name]
            if len(sub) == 0: continue
            tier_summary_rows.append({
                'discipline': category,
                'tier': t_name,
                'player_count': len(sub),
                'mean_hp_deliveries': round(sub['hp_balls_faced'].mean() if category == 'Batting' else sub['hp_legal_balls'].mean(), 1),
                'mean_hp_signed_wpa_pct': round(sub[wpa_col].mean(), 2),
                'median_hp_signed_wpa_pct': round(sub[wpa_col].median(), 2),
                'mean_hp_leverage_faced': round(sub[lev_col].mean(), 2),
                'mean_match_wpa_std_pct': round(sub['match_wpa_std_pct'].mean() if category == 'Batting' else sub['match_bwpa_std_pct'].mean(), 2),
                'mean_pct_positive_matches': round(sub['pct_positive_matches'].mean(), 1)
            })

    tier_sum_df = pd.DataFrame(tier_summary_rows)
    tier_sum_csv = OUTPUT_DIR / "player_consistency_summary.csv"
    tier_sum_df.to_csv(tier_sum_csv, index=False)
    print(f"Saved Consistency Summary to {tier_sum_csv}")

    print(f"\nStep 03 completed in {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
