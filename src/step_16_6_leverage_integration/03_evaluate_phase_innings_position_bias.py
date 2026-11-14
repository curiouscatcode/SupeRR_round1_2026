"""
Step 16.6: Script 03 - Comparative Evaluation across Phases, Innings, Positions, and Roles
========================================================================================
Compares Candidate 0 (Control) against Candidates 1A, 1B, 2, and 3 across:
1. Phase (Powerplay, Middle, Death)
2. Innings (Innings 1 vs Innings 2)
3. Batting Position (1 to 11, and Top Order 1-3 vs Middle 4-6 vs Lower 7-11)
4. Bowling Phase Exposure & Specialization
5. Promotion & Demotion Diagnostics:
   - Characterize deliveries promoted into High Pressure by leverage
   - Characterize deliveries demoted out of High Pressure by leverage
6. Evaluation against Original Project Flaws:
   - Does leverage fix top-order batting under-capture (7% in control)?
   - Does leverage reduce lower-order finisher/tailender bias (52% in control)?
   - Does leverage reduce death-bowler bias?

Outputs:
- outputs/step_16_6_leverage_integration/phase_innings_candidate_comparison.csv
- outputs/step_16_6_leverage_integration/batting_position_candidate_comparison.csv
- outputs/step_16_6_leverage_integration/bowling_phase_candidate_comparison.csv
- outputs/step_16_6_leverage_integration/promotion_demotion_characteristics.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_6_leverage_integration")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=== Step 16.6 Script 03: Evaluate Phase, Innings, Position & Role Biases ===")
    t0 = time.time()

    parquet_path = OUTPUT_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading classified candidates dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    print(f"Loaded {len(df):,} deliveries.")

    bat_mask = df['is_batter_ball_faced'] == 1
    bowl_mask = df['is_legal_ball'] == 1
    bat_df = df[bat_mask].copy()
    bowl_df = df[bowl_mask].copy()

    cand_bat_cols = [
        ('Control (Candidate 0)', 'hp_cand0_bat'),
        ('Additive 70/30 (Candidate 1A)', 'hp_cand1a_bat'),
        ('Additive 50/50 (Candidate 1B)', 'hp_cand1b_bat'),
        ('Multiplicative Gated (Candidate 2)', 'hp_cand2_bat'),
        ('Convex Composite (Candidate 3)', 'hp_cand3_bat')
    ]

    cand_bowl_cols = [
        ('Control (Candidate 0)', 'hp_cand0_bowl'),
        ('Additive 70/30 (Candidate 1A)', 'hp_cand1a_bowl'),
        ('Additive 50/50 (Candidate 1B)', 'hp_cand1b_bowl'),
        ('Multiplicative Gated (Candidate 2)', 'hp_cand2_bowl'),
        ('Convex Composite (Candidate 3)', 'hp_cand3_bowl')
    ]

    # -------------------------------------------------------------
    # 1. PHASE & INNINGS COMPARISON
    # -------------------------------------------------------------
    print("\n--- 1. Evaluating Phase & Innings HP Capture ---")
    phase_inn_rows = []

    # Batting
    for inn in [1, 2]:
        for ph in ['PP', 'Middle', 'Death']:
            sub = bat_df[(bat_df['innings'] == inn) & (bat_df['phase'] == ph)]
            n_tot = len(sub)
            row = {
                'discipline': 'Batting',
                'innings': inn,
                'phase': ph,
                'total_deliveries': n_tot,
                'mean_leverage': round(sub['expected_leverage_pct'].mean(), 2),
                'mean_pi': round(sub['Batting_PI'].mean(), 1)
            }
            for c_name, c_col in cand_bat_cols:
                n_hp = sub[c_col].sum()
                pct_hp = (n_hp / n_tot) * 100.0
                row[f"{c_name} HP Count"] = n_hp
                row[f"{c_name} HP %"] = round(pct_hp, 2)
            phase_inn_rows.append(row)

    # Bowling
    for inn in [1, 2]:
        for ph in ['PP', 'Middle', 'Death']:
            sub = bowl_df[(bowl_df['innings'] == inn) & (bowl_df['phase'] == ph)]
            n_tot = len(sub)
            row = {
                'discipline': 'Bowling',
                'innings': inn,
                'phase': ph,
                'total_deliveries': n_tot,
                'mean_leverage': round(sub['expected_leverage_pct'].mean(), 2),
                'mean_pi': round(sub['Bowling_PI'].mean(), 1)
            }
            for c_name, c_col in cand_bowl_cols:
                n_hp = sub[c_col].sum()
                pct_hp = (n_hp / n_tot) * 100.0
                row[f"{c_name} HP Count"] = n_hp
                row[f"{c_name} HP %"] = round(pct_hp, 2)
            phase_inn_rows.append(row)

    df_phase_inn = pd.DataFrame(phase_inn_rows)
    df_phase_inn.to_csv(OUTPUT_DIR / "phase_innings_candidate_comparison.csv", index=False)
    print("Saved Phase & Innings comparison to phase_innings_candidate_comparison.csv")

    # -------------------------------------------------------------
    # 2. BATTING POSITION COMPARISON (Positions 1 to 11)
    # -------------------------------------------------------------
    print("\n--- 2. Evaluating Batting Position HP Capture (Positions 1 to 11) ---")
    pos_rows = []

    for pos in range(1, 12):
        sub = bat_df[bat_df['batting_order'] == pos]
        n_tot = len(sub)
        role = 'Top Order (1-3)' if pos <= 3 else ('Middle Order (4-6)' if pos <= 6 else 'Lower Order (7-11)')
        row = {
            'batting_order': pos,
            'role': role,
            'total_balls_faced': n_tot,
            'mean_leverage': round(sub['expected_leverage_pct'].mean(), 2),
            'mean_pi': round(sub['Batting_PI'].mean(), 1)
        }
        for c_name, c_col in cand_bat_cols:
            n_hp = sub[c_col].sum()
            pct_hp = (n_hp / n_tot) * 100.0
            row[f"{c_name} HP %"] = round(pct_hp, 2)
        pos_rows.append(row)

    # Add Summary Rows for Top Order, Middle Order, Lower Order
    for r_name, r_orders in [('Top Order (1-3)', [1, 2, 3]), ('Middle Order (4-6)', [4, 5, 6]), ('Lower Order (7-11)', list(range(7, 12)))]:
        sub = bat_df[bat_df['batting_order'].isin(r_orders)]
        n_tot = len(sub)
        row = {
            'batting_order': 'Summary',
            'role': r_name,
            'total_balls_faced': n_tot,
            'mean_leverage': round(sub['expected_leverage_pct'].mean(), 2),
            'mean_pi': round(sub['Batting_PI'].mean(), 1)
        }
        for c_name, c_col in cand_bat_cols:
            n_hp = sub[c_col].sum()
            pct_hp = (n_hp / n_tot) * 100.0
            row[f"{c_name} HP %"] = round(pct_hp, 2)
        pos_rows.append(row)

    df_pos = pd.DataFrame(pos_rows)
    df_pos.to_csv(OUTPUT_DIR / "batting_position_candidate_comparison.csv", index=False)
    print("\nBatting Positions 1-11 & Role Summary:")
    print(df_pos[['batting_order', 'role', 'total_balls_faced', 'mean_leverage', 'Control (Candidate 0) HP %',
                  'Additive 70/30 (Candidate 1A) HP %', 'Additive 50/50 (Candidate 1B) HP %',
                  'Multiplicative Gated (Candidate 2) HP %', 'Convex Composite (Candidate 3) HP %']].to_string())

    # -------------------------------------------------------------
    # 3. BOWLING PHASE COMPARISON
    # -------------------------------------------------------------
    print("\n--- 3. Evaluating Bowling Phase HP Capture ---")
    bowl_phase_rows = []
    for ph in ['PP', 'Middle', 'Death']:
        sub = bowl_df[bowl_df['phase'] == ph]
        n_tot = len(sub)
        row = {
            'bowling_phase': ph,
            'total_legal_balls': n_tot,
            'mean_leverage': round(sub['expected_leverage_pct'].mean(), 2),
            'mean_pi': round(sub['Bowling_PI'].mean(), 1)
        }
        for c_name, c_col in cand_bowl_cols:
            n_hp = sub[c_col].sum()
            pct_hp = (n_hp / n_tot) * 100.0
            row[f"{c_name} HP %"] = round(pct_hp, 2)
            row[f"{c_name} HP Count"] = n_hp
        bowl_phase_rows.append(row)

    df_bowl_phase = pd.DataFrame(bowl_phase_rows)
    df_bowl_phase.to_csv(OUTPUT_DIR / "bowling_phase_candidate_comparison.csv", index=False)
    print(df_bowl_phase[['bowling_phase', 'total_legal_balls', 'mean_leverage',
                         'Control (Candidate 0) HP %', 'Additive 70/30 (Candidate 1A) HP %',
                         'Multiplicative Gated (Candidate 2) HP %']].to_string())

    # -------------------------------------------------------------
    # 4. PROMOTION & DEMOTION CHARACTERISTICS
    # -------------------------------------------------------------
    print("\n--- 4. Diagnosing Promoted vs Demoted Deliveries (Candidate 1A vs Control) ---")
    # For Batting:
    # Promoted: not in Control HP, but in Cand 1A HP
    # Demoted: in Control HP, but not in Cand 1A HP
    # Retained: in both
    # Unchanged Non-HP: in neither
    bat_ctrl = bat_df['hp_cand0_bat']
    bat_1a = bat_df['hp_cand1a_bat']

    promoted_1a = bat_df[~bat_ctrl & bat_1a]
    demoted_1a = bat_df[bat_ctrl & ~bat_1a]
    retained_1a = bat_df[bat_ctrl & bat_1a]
    unaffected_1a = bat_df[~bat_ctrl & ~bat_1a]

    # For Candidate 2:
    bat_2 = bat_df['hp_cand2_bat']
    promoted_2 = bat_df[~bat_ctrl & bat_2]
    demoted_2 = bat_df[bat_ctrl & ~bat_2]
    retained_2 = bat_df[bat_ctrl & bat_2]

    diag_rows = [
        {
            'candidate': 'Candidate 1A (Additive 70/30)',
            'group': 'Promoted Deliveries (New HP)',
            'count': len(promoted_1a),
            'pct_of_candidate_hp': round(len(promoted_1a) / len(bat_1a[bat_1a]) * 100, 1),
            'mean_leverage': round(promoted_1a['expected_leverage_pct'].mean(), 2),
            'mean_batting_pi': round(promoted_1a['Batting_PI'].mean(), 1),
            'mean_z_pi': round(promoted_1a['batting_z_score'].mean(), 2),
            'mean_wickets_lost': round(promoted_1a['wickets_before'].mean(), 2),
            'pct_top_order_1_3': round((promoted_1a['batting_order'] <= 3).mean() * 100, 1),
            'pct_lower_order_7_11': round((promoted_1a['batting_order'] >= 7).mean() * 100, 1),
            'pct_powerplay': round((promoted_1a['phase'] == 'PP').mean() * 100, 1),
            'pct_death': round((promoted_1a['phase'] == 'Death').mean() * 100, 1),
            'pct_innings_2': round((promoted_1a['innings'] == 2).mean() * 100, 1)
        },
        {
            'candidate': 'Candidate 1A (Additive 70/30)',
            'group': 'Demoted Deliveries (Dropped from HP)',
            'count': len(demoted_1a),
            'pct_of_candidate_hp': round(len(demoted_1a) / len(bat_ctrl[bat_ctrl]) * 100, 1),
            'mean_leverage': round(demoted_1a['expected_leverage_pct'].mean(), 2),
            'mean_batting_pi': round(demoted_1a['Batting_PI'].mean(), 1),
            'mean_z_pi': round(demoted_1a['batting_z_score'].mean(), 2),
            'mean_wickets_lost': round(demoted_1a['wickets_before'].mean(), 2),
            'pct_top_order_1_3': round((demoted_1a['batting_order'] <= 3).mean() * 100, 1),
            'pct_lower_order_7_11': round((demoted_1a['batting_order'] >= 7).mean() * 100, 1),
            'pct_powerplay': round((demoted_1a['phase'] == 'PP').mean() * 100, 1),
            'pct_death': round((demoted_1a['phase'] == 'Death').mean() * 100, 1),
            'pct_innings_2': round((demoted_1a['innings'] == 2).mean() * 100, 1)
        },
        {
            'candidate': 'Candidate 1A (Additive 70/30)',
            'group': 'Retained Deliveries (Common Core)',
            'count': len(retained_1a),
            'pct_of_candidate_hp': round(len(retained_1a) / len(bat_1a[bat_1a]) * 100, 1),
            'mean_leverage': round(retained_1a['expected_leverage_pct'].mean(), 2),
            'mean_batting_pi': round(retained_1a['Batting_PI'].mean(), 1),
            'mean_z_pi': round(retained_1a['batting_z_score'].mean(), 2),
            'mean_wickets_lost': round(retained_1a['wickets_before'].mean(), 2),
            'pct_top_order_1_3': round((retained_1a['batting_order'] <= 3).mean() * 100, 1),
            'pct_lower_order_7_11': round((retained_1a['batting_order'] >= 7).mean() * 100, 1),
            'pct_powerplay': round((retained_1a['phase'] == 'PP').mean() * 100, 1),
            'pct_death': round((retained_1a['phase'] == 'Death').mean() * 100, 1),
            'pct_innings_2': round((retained_1a['innings'] == 2).mean() * 100, 1)
        },
        {
            'candidate': 'Candidate 2 (Multiplicative Gated)',
            'group': 'Promoted Deliveries (New HP)',
            'count': len(promoted_2),
            'pct_of_candidate_hp': round(len(promoted_2) / len(bat_2[bat_2]) * 100, 1),
            'mean_leverage': round(promoted_2['expected_leverage_pct'].mean(), 2),
            'mean_batting_pi': round(promoted_2['Batting_PI'].mean(), 1),
            'mean_z_pi': round(promoted_2['batting_z_score'].mean(), 2),
            'mean_wickets_lost': round(promoted_2['wickets_before'].mean(), 2),
            'pct_top_order_1_3': round((promoted_2['batting_order'] <= 3).mean() * 100, 1),
            'pct_lower_order_7_11': round((promoted_2['batting_order'] >= 7).mean() * 100, 1),
            'pct_powerplay': round((promoted_2['phase'] == 'PP').mean() * 100, 1),
            'pct_death': round((promoted_2['phase'] == 'Death').mean() * 100, 1),
            'pct_innings_2': round((promoted_2['innings'] == 2).mean() * 100, 1)
        },
        {
            'candidate': 'Candidate 2 (Multiplicative Gated)',
            'group': 'Demoted Deliveries (Dropped from HP)',
            'count': len(demoted_2),
            'pct_of_candidate_hp': round(len(demoted_2) / len(bat_ctrl[bat_ctrl]) * 100, 1),
            'mean_leverage': round(demoted_2['expected_leverage_pct'].mean(), 2),
            'mean_batting_pi': round(demoted_2['Batting_PI'].mean(), 1),
            'mean_z_pi': round(demoted_2['batting_z_score'].mean(), 2),
            'mean_wickets_lost': round(demoted_2['wickets_before'].mean(), 2),
            'pct_top_order_1_3': round((demoted_2['batting_order'] <= 3).mean() * 100, 1),
            'pct_lower_order_7_11': round((demoted_2['batting_order'] >= 7).mean() * 100, 1),
            'pct_powerplay': round((demoted_2['phase'] == 'PP').mean() * 100, 1),
            'pct_death': round((demoted_2['phase'] == 'Death').mean() * 100, 1),
            'pct_innings_2': round((demoted_2['innings'] == 2).mean() * 100, 1)
        }
    ]

    df_diag = pd.DataFrame(diag_rows)
    df_diag.to_csv(OUTPUT_DIR / "promotion_demotion_characteristics.csv", index=False)
    print("\nPromotion & Demotion Characteristics Table:")
    print(df_diag[['candidate', 'group', 'count', 'mean_leverage', 'mean_batting_pi', 'pct_top_order_1_3', 'pct_lower_order_7_11', 'pct_powerplay', 'pct_death']].to_string())

    print(f"\nExecution completed in {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
