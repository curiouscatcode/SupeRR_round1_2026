"""
Step 16.6.1: Script 03 - Deep Investigation of Demoted Deliveries (Candidate 2)
==============================================================================
Audits the deliveries classified as High Pressure by Control (Z_PI > 1.0)
but DEMOTED to Low Pressure by Candidate 2 (Z_2 <= 1.0):

1. Characterizes demoted deliveries vs retained deliveries across:
   - Win probability before delivery (wp_before)
   - Match competitiveness buckets (Blowout WP < 5% or > 95%, Competitive WP 20-80%)
   - Innings & Phase distribution
   - Batting position distribution (Positions 1-11)
   - Wickets lost, Balls remaining, Required Run Rate
   - Striker balls faced before delivery
   - Expected delivery leverage distribution

2. Searches for FALSE NEGATIVES (genuinely difficult, important situations demoted):
   - Quantifies how many demoted balls occurred in competitive games (WP in [20%, 80%])
   - Inspects edge cases where high required rate or 1st innings crisis was downscaled
   - Extracts specific delivery case studies with full match context.

Outputs:
- outputs/step_16_6_1_independent_audit/demoted_deliveries_investigation.csv
- outputs/step_16_6_1_independent_audit/demoted_competitive_deliveries_sample.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_6_1_independent_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STEP_16_6_DIR = Path("outputs/step_16_6_leverage_integration")
PROCESSED_DIR = Path("data/processed")


def main():
    print("=== Step 16.6.1 Script 03: Investigate Demoted Deliveries ===")
    t0 = time.time()

    # Load master classified deliveries
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading master delivery dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # Load striker_balls_faced_before from delivery_match_state
    dms_path = PROCESSED_DIR / "delivery_match_state.csv"
    dms = pd.read_csv(dms_path, usecols=['match_id', 'innings', 'overid', 'innings_ball_num',
                                         'striker_balls_faced_before'])
    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    df = df.merge(dms, on=merge_keys, how='left')

    bat_mask = df['is_batter_ball_faced'] == 1
    bat_df = df[bat_mask].copy()

    # Define classification cohorts explicitly
    ctrl_hp = (bat_df['hp_cand0_bat'] == True)
    c2_hp = (bat_df['hp_cand2_bat'] == True)

    bat_df['cohort'] = 'Neither'
    bat_df.loc[ctrl_hp & c2_hp, 'cohort'] = 'Retained_HP'
    bat_df.loc[ctrl_hp & ~c2_hp, 'cohort'] = 'Demoted_from_HP'
    bat_df.loc[~ctrl_hp & c2_hp, 'cohort'] = 'Promoted_to_HP'
    bat_df.loc[~ctrl_hp & ~c2_hp, 'cohort'] = 'Common_Low'

    cohort_counts = bat_df['cohort'].value_counts()
    print("\nBatting Delivery Cohorts (Control vs Candidate 2):")
    for ch, cnt in cohort_counts.items():
        print(f"  {ch:18s}: {cnt:6d} ({cnt/len(bat_df)*100:.2f}%)")

    # Win probability buckets
    def wp_bucket(wp):
        if pd.isna(wp):
            return 'Unknown'
        if wp < 0.05 or wp > 0.95:
            return '1. Blowout (WP < 5% or > 95%)'
        elif wp < 0.20 or wp > 0.80:
            return '2. One-Sided (WP 5-20% or 80-95%)'
        elif wp < 0.40 or wp > 0.60:
            return '3. Competitive (WP 20-40% or 60-80%)'
        else:
            return '4. Parity/Clutch (WP 40-60%)'

    bat_df['wp_bucket'] = bat_df['wp_before'].apply(wp_bucket)

    # 1. Comparison of Demoted vs Retained vs Promoted Deliveries
    cohorts_to_compare = ['Retained_HP', 'Demoted_from_HP', 'Promoted_to_HP']
    comparison_metrics = []

    for ch in cohorts_to_compare:
        sub = bat_df[bat_df['cohort'] == ch]
        sub_inn2 = sub[sub['innings'] == 2]

        # Lower order and top order shares
        top_share = (sub['batting_order'].isin([1, 2, 3])).mean() * 100.0
        mid_share = (sub['batting_order'].isin([4, 5, 6])).mean() * 100.0
        low_share = (sub['batting_order'].isin([7, 8, 9, 10, 11])).mean() * 100.0

        # Phase shares
        pp_share = (sub['phase'] == 'PP').mean() * 100.0
        mid_phase_share = (sub['phase'] == 'Middle').mean() * 100.0
        death_share = (sub['phase'] == 'Death').mean() * 100.0

        # Blowout share (WP < 5% or > 95%)
        blowout_share = (sub['wp_bucket'] == '1. Blowout (WP < 5% or > 95%)').mean() * 100.0
        comp_share = (sub['wp_bucket'].isin(['3. Competitive (WP 20-40% or 60-80%)', '4. Parity/Clutch (WP 40-60%)'])).mean() * 100.0

        comparison_metrics.append({
            'cohort': ch,
            'count': len(sub),
            'pct_of_total_batting': round(len(sub) / len(bat_df) * 100.0, 2),
            'mean_leverage_pct': round(sub['expected_leverage_pct'].mean(), 3),
            'median_leverage_pct': round(sub['expected_leverage_pct'].median(), 3),
            'p25_leverage_pct': round(sub['expected_leverage_pct'].quantile(0.25), 3),
            'p75_leverage_pct': round(sub['expected_leverage_pct'].quantile(0.75), 3),
            'mean_pi': round(sub['Batting_PI'].mean(), 2),
            'mean_z_pi': round(sub['batting_z_score'].mean(), 3),
            'mean_z_cand2': round(sub['z_cand2_bat'].mean(), 3),
            'mean_wickets_lost': round(sub['wickets_before'].mean(), 2),
            'mean_balls_faced': round(sub['striker_balls_faced_before'].mean(), 1),
            'mean_rrr_inn2': round(sub_inn2['required_run_rate'].mean(), 2) if len(sub_inn2) > 0 else np.nan,
            'pct_innings_2': round((sub['innings'] == 2).mean() * 100.0, 2),
            'pct_top_order_1_3': round(top_share, 2),
            'pct_middle_order_4_6': round(mid_share, 2),
            'pct_lower_order_7_11': round(low_share, 2),
            'pct_powerplay': round(pp_share, 2),
            'pct_middle_phase': round(mid_phase_share, 2),
            'pct_death': round(death_share, 2),
            'pct_blowout_game_state': round(blowout_share, 2),
            'pct_competitive_game_state': round(comp_share, 2)
        })

    df_comp = pd.DataFrame(comparison_metrics)
    comp_csv = OUTPUT_DIR / "demoted_deliveries_investigation.csv"
    df_comp.to_csv(comp_csv, index=False)
    print(f"\nSaved demoted deliveries investigation table to {comp_csv}")
    print("\nSummary Characteristics across Cohorts:")
    print(df_comp[['cohort', 'count', 'mean_leverage_pct', 'mean_pi', 'mean_z_pi', 'mean_z_cand2',
                   'pct_lower_order_7_11', 'pct_blowout_game_state', 'pct_competitive_game_state']].to_string())

    # 2. Detailed Breakdown of Demoted Deliveries by WP Bucket and Innings
    demoted = bat_df[bat_df['cohort'] == 'Demoted_from_HP']
    print(f"\n--- Demoted Deliveries Breakdown (n = {len(demoted):,}) ---")
    wp_demoted = demoted.groupby('wp_bucket').agg(
        count=('Batting_PI', 'count'),
        mean_lev=('expected_leverage_pct', 'mean'),
        mean_pi=('Batting_PI', 'mean'),
        mean_z_pi=('batting_z_score', 'mean'),
        mean_z2=('z_cand2_bat', 'mean'),
        mean_wickets=('wickets_before', 'mean'),
        pct_lower_order=('batting_order', lambda s: (s >= 7).mean() * 100.0)
    ).reset_index()
    wp_demoted['pct_of_demoted'] = (wp_demoted['count'] / len(demoted)) * 100.0
    print(wp_demoted[['wp_bucket', 'count', 'pct_of_demoted', 'mean_lev', 'mean_pi', 'mean_z_pi', 'mean_z2', 'pct_lower_order']].to_string())

    # 3. Investigation of Potential False Negatives: Demoted Balls in Competitive States
    comp_demoted = demoted[demoted['wp_bucket'].isin([
        '3. Competitive (WP 20-40% or 60-80%)',
        '4. Parity/Clutch (WP 40-60%)'
    ])]
    n_comp_demoted = len(comp_demoted)
    pct_comp_demoted = (n_comp_demoted / len(demoted)) * 100.0
    print(f"\nPotential False Negatives: Demoted balls in Competitive/Parity states: {n_comp_demoted:,} ({pct_comp_demoted:.2f}% of demoted balls)")

    # Why were these competitive balls demoted?
    # Inspect their Z_PI and Z_Lev
    print("Why were competitive balls demoted? Z_PI vs Z_Lev distribution:")
    print(f"  Mean Z_PI: {comp_demoted['batting_z_score'].mean():.3f} (Min: {comp_demoted['batting_z_score'].min():.3f}, Max: {comp_demoted['batting_z_score'].max():.3f})")
    print(f"  Mean Z_Lev: {comp_demoted['lev_z_score_bat'].mean():.3f} (Min: {comp_demoted['lev_z_score_bat'].min():.3f}, Max: {comp_demoted['lev_z_score_bat'].max():.3f})")
    print(f"  Mean Z_2: {comp_demoted['z_cand2_bat'].mean():.3f}")

    # Notice that many had Z_PI just barely above 1.0 (e.g. 1.01-1.10) and slight negative Z_Lev!
    barely_hp = (comp_demoted['batting_z_score'] <= 1.15).mean() * 100.0
    print(f"  Deliveries with borderline Z_PI (1.00 < Z_PI <= 1.15): {barely_hp:.2f}%")

    # Sample representative case studies from demoted competitive deliveries
    sample_cols = [
        'match_id', 'innings', 'overid', 'innings_ball_num', 'striker_name', 'bowler_name',
        'batting_order', 'phase', 'score_before', 'wickets_before', 'balls_remaining',
        'runs_required', 'required_run_rate', 'wp_before', 'Batting_PI', 'expected_leverage_pct',
        'batting_z_score', 'lev_z_score_bat', 'z_cand2_bat'
    ]
    sample_df = comp_demoted[sample_cols].head(30)
    sample_csv = OUTPUT_DIR / "demoted_competitive_deliveries_sample.csv"
    sample_df.to_csv(sample_csv, index=False)
    print(f"Saved representative competitive demoted deliveries sample to {sample_csv}")

    print(f"\nTotal time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
