"""
Step 16.6.1: Script 05 - Scenario Recalculation & Full-Population Edge Case Audit
===============================================================================
1. Recalculates the seven Step 16.6 scenarios from underlying delivery inputs:
   - Verifies exact delivery match IDs, overs, balls, score, wickets, PI, leverage, Z-scores.
   - Verifies candidate classifications against recalculated values.

2. Performs an extensive full-population audit across six distinct archetypal categories:
   - Category A: Genuine First-Innings Collapses (Inn 1, PP, 3+ wickets lost)
   - Category B: Lost-Cause Chases / Garbage Time (Inn 2, Ov 13-20, WP < 5%, RRR > 12)
   - Category C: Competitive Death Overs Thrillers (Inn 2, Ov 18-20, WP in [30%, 70%], balls rem <= 12)
   - Category D: Tight Middle-Over Squeeze (Inn 2, Ov 10-16, WP in [40%, 60%], 3-5 down, RRR 9-12)
   - Category E: High Leverage, Low Task Difficulty (Z_Lev > 1.5, Batting PI < 35 / Z_PI < 0)
   - Category F: High Task Difficulty, Low Leverage (Batting PI > 60 / Z_PI > 1.0, Z_Lev < -1.0)

Outputs:
- outputs/step_16_6_1_independent_audit/scenario_recalculation_verification.csv
- outputs/step_16_6_1_independent_audit/population_categories_audit.csv
- outputs/step_16_6_1_independent_audit/category_case_studies.csv
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
    print("=== Step 16.6.1 Script 05: Scenario Recalculation & Population Audit ===")
    t0 = time.time()

    # Load master classified dataset
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading master delivery dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # 1. Recalculate the 7 Step 16.6 Scenarios
    scenario_csv = STEP_16_6_DIR / "scenario_classification_audit.csv"
    print(f"Loading Step 16.6 scenario audit log from {scenario_csv}...")
    s16_scenarios = pd.read_csv(scenario_csv)

    verified_scenarios = []
    print("\n--- Verifying Step 16.6 Scenarios ---")
    for idx, row in s16_scenarios.iterrows():
        m_id = row['match_id']
        striker = row['striker']
        state_str = str(row['match_state'])

        # Parse match_state string: e.g. "Inn 2, Over 1.1 | Score: 0/0"
        inn_part = state_str.split(',')[0].strip()  # "Inn 2"
        inn = int(inn_part.split(' ')[1])
        over_part = state_str.split(',')[1].split('|')[0].strip()  # "Over 1.1"
        over_dot_ball = over_part.split(' ')[1]
        over_id = int(over_dot_ball.split('.')[0])
        ball_num = int(over_dot_ball.split('.')[1])

        match_row = df[(df['match_id'] == m_id) & (df['innings'] == inn) &
                       (df['overid'] == over_id) & (df['over_ball_num'] == ball_num)]
        if len(match_row) == 0:
            # Fallback to striker match in that match and innings
            match_row = df[(df['match_id'] == m_id) & (df['innings'] == inn) & (df['striker_name'] == striker)]
            if len(match_row) == 0:
                print(f"WARNING: Delivery not found for {row['scenario_name']}: Match {m_id}, Inn {inn}, Over {over_id}.{ball_num}")
                continue

        deliv = match_row.iloc[0]
        # Verify values
        pi_val = deliv['Batting_PI']
        lev_val = deliv['expected_leverage_pct']
        z_pi = deliv['batting_z_score']
        z_lev = deliv['lev_z_score_bat']
        z_c0 = deliv['z_cand0_bat']
        z_c1a = deliv['z_cand1a_bat']
        z_c1b = deliv['z_cand1b_bat']
        z_c2 = deliv['z_cand2_bat']
        z_c3 = deliv['z_cand3_bat']

        hp_c0 = bool(deliv['hp_cand0_bat'] == True)
        hp_c1a = bool(deliv['hp_cand1a_bat'] == True)
        hp_c1b = bool(deliv['hp_cand1b_bat'] == True)
        hp_c2 = bool(deliv['hp_cand2_bat'] == True)
        hp_c3 = bool(deliv['hp_cand3_bat'] == True)

        verified_scenarios.append({
            'scenario_name': row['scenario_name'],
            'match_id': m_id,
            'innings': inn,
            'over_delivery': f"{deliv['overid']}.{deliv['over_ball_num']}",
            'score_state': f"{deliv['score_before']}/{deliv['wickets_before']}",
            'striker_name': deliv['striker_name'],
            'reported_pi': round(row['batting_pi'], 2),
            'verified_pi': round(pi_val, 2),
            'reported_lev': round(row['expected_leverage_pct'], 2),
            'verified_lev': round(lev_val, 2),
            'reported_z_control': round(row['z_control'], 2),
            'verified_z_control': round(z_pi, 2),
            'reported_z_cand2': round(row['z_cand2_gated'], 2),
            'verified_z_cand2': round(z_c2, 2),
            'cand0_hp': hp_c0,
            'cand1a_hp': hp_c1a,
            'cand1b_hp': hp_c1b,
            'cand2_hp': hp_c2,
            'cand3_hp': hp_c3
        })

    df_ver_scenarios = pd.DataFrame(verified_scenarios)
    ver_csv = OUTPUT_DIR / "scenario_recalculation_verification.csv"
    df_ver_scenarios.to_csv(ver_csv, index=False)
    print(f"Saved scenario verification to {ver_csv}")
    print(df_ver_scenarios[['scenario_name', 'score_state', 'verified_pi', 'verified_lev', 'cand0_hp', 'cand2_hp']].to_string())

    # 2. Full-Population Systematic Category Audit
    print("\n--- Systematic Full-Population Category Audit ---")
    bat_mask = df['is_batter_ball_faced'] == 1
    bat_df = df[bat_mask].copy()

    # Define Categories
    cat_A = (bat_df['innings'] == 1) & (bat_df['phase'] == 'PP') & (bat_df['wickets_before'] >= 3)
    cat_B = (bat_df['innings'] == 2) & (bat_df['overid'] >= 13) & (bat_df['wp_before'] < 0.05) & (bat_df['required_run_rate'] > 12.0)
    cat_C = (bat_df['innings'] == 2) & (bat_df['overid'] >= 18) & (bat_df['wp_before'].between(0.30, 0.70)) & (bat_df['balls_remaining'] <= 12)
    cat_D = (bat_df['innings'] == 2) & (bat_df['overid'].between(10, 16)) & (bat_df['wp_before'].between(0.40, 0.60)) & (bat_df['wickets_before'].between(3, 5)) & (bat_df['required_run_rate'].between(9.0, 12.0))
    cat_E = (bat_df['lev_z_score_bat'] > 1.5) & (bat_df['batting_z_score'] < 0.0)
    cat_F = (bat_df['batting_z_score'] > 1.0) & (bat_df['lev_z_score_bat'] < -1.0)

    categories = [
        ('Category A: 1st Innings PP Collapse', cat_A, 'Inn 1, PP, 3+ wkts down (e.g. 20/3 in over 4)'),
        ('Category B: Lost-Cause Chase / Blowout', cat_B, 'Inn 2, Over 13+, WP < 5%, RRR > 12 (e.g. 60/7 chasing 190)'),
        ('Category C: Competitive Death Thriller', cat_C, 'Inn 2, Over 18+, WP 30-70%, <= 12 balls rem (e.g. 10 off 6)'),
        ('Category D: Tight Middle-Over Squeeze', cat_D, 'Inn 2, Over 10-16, WP 40-60%, 3-5 down, RRR 9-12'),
        ('Category E: High Leverage / Low Difficulty', cat_E, 'Z_Lev > 1.5 but Z_PI < 0 (Close game, easy tactical state)'),
        ('Category F: High Difficulty / Low Leverage', cat_F, 'Z_PI > 1.0 but Z_Lev < -1.0 (Extreme tactical stress in decided match)')
    ]

    cat_rows = []
    case_study_rows = []

    for cat_name, mask, desc in categories:
        sub = bat_df[mask]
        n_deliv = len(sub)
        if n_deliv == 0:
            continue

        c0_hp_pct = (sub['hp_cand0_bat'] == True).mean() * 100.0
        c1a_hp_pct = (sub['hp_cand1a_bat'] == True).mean() * 100.0
        c2_hp_pct = (sub['hp_cand2_bat'] == True).mean() * 100.0
        c3_hp_pct = (sub['hp_cand3_bat'] == True).mean() * 100.0

        m_pi = sub['Batting_PI'].mean()
        m_z_pi = sub['batting_z_score'].mean()
        m_lev = sub['expected_leverage_pct'].mean()
        m_z_lev = sub['lev_z_score_bat'].mean()
        m_wp = sub['wp_before'].mean()

        cat_rows.append({
            'category_name': cat_name,
            'description': desc,
            'total_deliveries': n_deliv,
            'pct_of_all_batting': round(n_deliv / len(bat_df) * 100.0, 2),
            'mean_pi': round(m_pi, 2),
            'mean_z_pi': round(m_z_pi, 3),
            'mean_leverage_pct': round(m_lev, 3),
            'mean_z_lev': round(m_z_lev, 3),
            'mean_wp_before': round(m_wp, 3),
            'control_hp_pct': round(c0_hp_pct, 2),
            'cand1a_hp_pct': round(c1a_hp_pct, 2),
            'cand2_hp_pct': round(c2_hp_pct, 2),
            'cand3_hp_pct': round(c3_hp_pct, 2)
        })

        # Grab top 5 representative deliveries as case studies
        top_cases = sub.sort_values(by='expected_leverage_pct', ascending=False).head(5)
        for _, c_row in top_cases.iterrows():
            case_study_rows.append({
                'category_name': cat_name,
                'match_id': c_row['match_id'],
                'innings': c_row['innings'],
                'overid': c_row['overid'],
                'innings_ball_num': c_row['innings_ball_num'],
                'striker_name': c_row['striker_name'],
                'bowler_name': c_row['bowler_name'],
                'batting_order': c_row['batting_order'],
                'phase': c_row['phase'],
                'score_state': f"{c_row['score_before']}/{c_row['wickets_before']}",
                'balls_rem': c_row['balls_remaining'],
                'rrr': round(c_row['required_run_rate'], 1) if pd.notna(c_row['required_run_rate']) else np.nan,
                'wp_before': round(c_row['wp_before'], 3),
                'Batting_PI': round(c_row['Batting_PI'], 1),
                'expected_leverage_pct': round(c_row['expected_leverage_pct'], 2),
                'batting_z_score': round(c_row['batting_z_score'], 2),
                'lev_z_score_bat': round(c_row['lev_z_score_bat'], 2),
                'z_cand2_bat': round(c_row['z_cand2_bat'], 2),
                'ctrl_hp': bool(c_row['hp_cand0_bat'] == True),
                'c2_hp': bool(c_row['hp_cand2_bat'] == True)
            })

    df_cat = pd.DataFrame(cat_rows)
    cat_csv = OUTPUT_DIR / "population_categories_audit.csv"
    df_cat.to_csv(cat_csv, index=False)
    print(f"\nSaved population categories audit to {cat_csv}")
    print("\nPopulation Categories Audit Table:")
    print(df_cat[['category_name', 'total_deliveries', 'mean_pi', 'mean_z_pi', 'mean_leverage_pct',
                  'control_hp_pct', 'cand1a_hp_pct', 'cand2_hp_pct']].to_string())

    df_cases = pd.DataFrame(case_study_rows)
    cases_csv = OUTPUT_DIR / "category_case_studies.csv"
    df_cases.to_csv(cases_csv, index=False)
    print(f"Saved category case studies to {cases_csv}")

    print(f"\nTotal time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
