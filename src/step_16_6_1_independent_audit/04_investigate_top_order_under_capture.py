"""
Step 16.6.1: Script 04 - Top-Order Under-Capture Investigation
=============================================================
Investigates why Expected Leverage integration (Candidate 2) fails to elevate
Top-Order (positions 1-3) High Pressure capture, leaving it locked at ~7.2%.

Deconstructs the 90,068 Top-Order deliveries across:
1. Innings 1 vs Innings 2.
2. Wickets lost at delivery time (0, 1, 2, 3+).
3. Striker balls faced before delivery (0-5, 6-10, 11-20, 21-35, 36+).
4. Required run rate in Innings 2 (<8, 8-10, 10-12, >12).
5. Leverage distribution (Z_Lev < 0, 0 <= Z_Lev < 1, Z_Lev >= 1).
6. Mathematical constraint analysis of Candidate 2:
   - S_2 = Z_PI * [1 + 0.5 * tanh(Z_Lev)]
   - Since g(Z_Lev) > 0 always, S_2 has the exact same sign as Z_PI.
   - Deliveries with Z_PI <= 0 can NEVER be promoted to High Pressure,
     no matter how high the leverage is!

Outputs:
- outputs/step_16_6_1_independent_audit/top_order_capture_investigation.csv
- outputs/step_16_6_1_independent_audit/top_order_strata_breakdown.csv
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
    print("=== Step 16.6.1 Script 04: Top-Order Under-Capture Investigation ===")
    t0 = time.time()

    # Load master classified deliveries
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading master delivery dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # Load striker_balls_faced_before and match state
    dms_path = PROCESSED_DIR / "delivery_match_state.csv"
    dms = pd.read_csv(dms_path, usecols=['match_id', 'innings', 'overid', 'innings_ball_num',
                                         'striker_balls_faced_before'])
    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    df = df.merge(dms, on=merge_keys, how='left')

    bat_mask = df['is_batter_ball_faced'] == 1
    top_mask = bat_mask & df['batting_order'].isin([1, 2, 3])
    top_df = df[top_mask].copy()
    n_top = len(top_df)
    print(f"Loaded {n_top:,} Top-Order (positions 1-3) deliveries.")

    # Boolean flags
    top_df['hp_ctrl'] = (top_df['hp_cand0_bat'] == True)
    top_df['hp_c2'] = (top_df['hp_cand2_bat'] == True)
    top_df['hp_c1a'] = (top_df['hp_cand1a_bat'] == True)

    # 1. Mathematical Constraint Audit: Sign of Z_PI
    pos_z_pi = (top_df['batting_z_score'] > 0).mean() * 100.0
    high_lev_top = (top_df['lev_z_score_bat'] > 1.0).mean() * 100.0
    both_pos = ((top_df['batting_z_score'] > 0) & (top_df['lev_z_score_bat'] > 1.0)).mean() * 100.0
    neg_pi_high_lev = ((top_df['batting_z_score'] <= 0) & (top_df['lev_z_score_bat'] > 1.0)).mean() * 100.0

    print("\n--- 1. Mathematical Sign Constraint in Top-Order Deliveries ---")
    print(f"  Top-Order deliveries with Z_PI > 0: {pos_z_pi:.2f}% ({(top_df['batting_z_score'] > 0).sum():,} balls)")
    print(f"  Top-Order deliveries with Z_PI <= 0: {100.0 - pos_z_pi:.2f}% ({(top_df['batting_z_score'] <= 0).sum():,} balls)")
    print(f"  Top-Order deliveries with Z_Lev > 1.0: {high_lev_top:.2f}% ({(top_df['lev_z_score_bat'] > 1.0).sum():,} balls)")
    print(f"  High Leverage (Z_Lev > 1.0) but Negative Z_PI (Z_PI <= 0): {neg_pi_high_lev:.2f}% ({((top_df['batting_z_score'] <= 0) & (top_df['lev_z_score_bat'] > 1.0)).sum():,} balls)")
    print(f"  >> In Candidate 2, because g(Z_Lev) > 0, ALL {((top_df['batting_z_score'] <= 0) & (top_df['lev_z_score_bat'] > 1.0)).sum():,} high-leverage deliveries remain mathematically negative (S_2 <= 0) and CAN NEVER BE PROMOTED TO HIGH PRESSURE!")

    # 2. Deconstruction by Match Dimensions
    def categorize_top_order(row):
        # Innings
        inn = f"Inn {row['innings']}"
        # Wickets
        w = row['wickets_before']
        w_cat = '0 wkts' if w == 0 else ('1 wkt' if w == 1 else ('2 wkts' if w == 2 else '3+ wkts'))
        # Balls faced
        bf = row['striker_balls_faced_before']
        bf_cat = '0-5 bf' if bf <= 5 else ('6-15 bf' if bf <= 15 else ('16-30 bf' if bf <= 30 else '31+ bf'))
        return inn, w_cat, bf_cat

    top_df['inn_cat'] = top_df['innings'].apply(lambda x: f"Innings {x}")
    top_df['wkt_cat'] = top_df['wickets_before'].apply(lambda w: '0 wickets' if w == 0 else ('1 wicket' if w == 1 else ('2 wickets' if w == 2 else '3+ wickets')))
    top_df['bf_cat'] = top_df['striker_balls_faced_before'].apply(lambda bf: '1. 0-5 balls' if bf <= 5 else ('2. 6-15 balls' if bf <= 15 else ('3. 16-30 balls' if bf <= 30 else '4. 31+ balls')))

    # Analysis across Strata
    strata_analyses = [
        ('Innings', 'inn_cat'),
        ('Wickets Lost', 'wkt_cat'),
        ('Striker Balls Faced', 'bf_cat'),
        ('Match Phase', 'phase')
    ]

    breakdown_rows = []
    for dim_name, col_name in strata_analyses:
        grp = top_df.groupby(col_name)
        for cat_val, sub in grp:
            n_sub = len(sub)
            ctrl_hp_pct = sub['hp_ctrl'].mean() * 100.0
            c2_hp_pct = sub['hp_c2'].mean() * 100.0
            c1a_hp_pct = sub['hp_c1a'].mean() * 100.0
            m_lev = sub['expected_leverage_pct'].mean()
            m_pi = sub['Batting_PI'].mean()
            m_z_pi = sub['batting_z_score'].mean()
            m_z_lev = sub['lev_z_score_bat'].mean()
            pct_pos_pi = (sub['batting_z_score'] > 0).mean() * 100.0
            pct_high_lev = (sub['lev_z_score_bat'] > 1.0).mean() * 100.0

            breakdown_rows.append({
                'dimension': dim_name,
                'category': str(cat_val),
                'total_balls': n_sub,
                'pct_of_top_order': round(n_sub / n_top * 100.0, 2),
                'mean_pi': round(m_pi, 2),
                'mean_z_pi': round(m_z_pi, 3),
                'mean_leverage_pct': round(m_lev, 3),
                'mean_z_lev': round(m_z_lev, 3),
                'pct_z_pi_positive': round(pct_pos_pi, 2),
                'pct_high_leverage': round(pct_high_lev, 2),
                'control_hp_pct': round(ctrl_hp_pct, 2),
                'cand2_hp_pct': round(c2_hp_pct, 2),
                'cand1a_hp_pct': round(c1a_hp_pct, 2)
            })

    df_breakdown = pd.DataFrame(breakdown_rows)
    breakdown_csv = OUTPUT_DIR / "top_order_capture_investigation.csv"
    df_breakdown.to_csv(breakdown_csv, index=False)
    print(f"\nSaved top-order breakdown to {breakdown_csv}")
    print("\nTop-Order Capture Breakdown across Dimensions:")
    print(df_breakdown[['dimension', 'category', 'total_balls', 'mean_pi', 'mean_z_pi', 'mean_leverage_pct',
                        'pct_z_pi_positive', 'control_hp_pct', 'cand2_hp_pct']].to_string())

    # 3. Two-way cross-tab: Wickets Lost x Balls Faced in Top Order
    crosstab = top_df.groupby(['wkt_cat', 'bf_cat']).agg(
        count=('Batting_PI', 'count'),
        mean_pi=('Batting_PI', 'mean'),
        mean_lev=('expected_leverage_pct', 'mean'),
        mean_z_pi=('batting_z_score', 'mean'),
        ctrl_hp_pct=('hp_ctrl', lambda s: s.mean() * 100.0),
        c2_hp_pct=('hp_c2', lambda s: s.mean() * 100.0)
    ).reset_index()
    crosstab_csv = OUTPUT_DIR / "top_order_strata_breakdown.csv"
    crosstab.to_csv(crosstab_csv, index=False)
    print(f"\nSaved two-way cross-tab to {crosstab_csv}")
    print("\nTwo-Way Cross-Tab (Wickets Lost x Balls Faced in Top Order):")
    print(crosstab[['wkt_cat', 'bf_cat', 'count', 'mean_pi', 'mean_lev', 'ctrl_hp_pct', 'c2_hp_pct']].to_string())

    print(f"\nTotal time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
