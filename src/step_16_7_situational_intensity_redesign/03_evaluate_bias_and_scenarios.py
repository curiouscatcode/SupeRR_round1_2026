"""
Step 16.7: Script 03 - Evaluate Bias and Scenario Tests across All 10 Dimensions
================================================================================
Conducts the mandatory comprehensive bias and scenario evaluation for Candidates 0, 1, 2, 3, and 4:

1. Batting order positions 1 to 11 individually and role groups (Top 1-3, Middle 4-6, Lower 7-11).
2. Phase & Innings representation across the 6 strata.
3. The 10 specific cricket scenarios:
   - Scenario 1: Top-Order Overall (Positions 1-3)
   - Scenario 2: Middle-Order Overall (Positions 4-6)
   - Scenario 3: Lower-Order Overall (Positions 7-11)
   - Scenario 4: Match Phase Balance (PP, Middle, Death)
   - Scenario 5: Innings Balance (Inn 1 vs Inn 2)
   - Scenario 6: First-Innings PP Collapses (Inn 1, PP, 3+ wkts down)
   - Scenario 7: Competitive Death Finishes (Inn 2, Ov 18+, WP 30-70%, <= 12 balls rem)
   - Scenario 8: Hopeless Chases / Pure Blowouts (Inn 2, Ov 13+, WP < 5%, RRR > 12)
   - Scenario 9: Middle-Over Run-Rate Squeeze (Inn 2, Ov 10-16, WP 40-60%, 3-5 down, RRR 9-12)
   - Scenario 10: Set Batters under Crisis (bf >= 15, Task Difficulty T > 65)

Outputs:
- outputs/step_16_7_situational_intensity_redesign/bias_and_position_comparison.csv
- outputs/step_16_7_situational_intensity_redesign/scenario_testing_audit.csv
- outputs/step_16_7_situational_intensity_redesign/phase_innings_candidates_breakdown.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_7_situational_intensity_redesign")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=== Step 16.7 Script 03: Evaluate Bias and Scenarios ===")
    t0 = time.time()

    parquet_path = OUTPUT_DIR / "delivery_intensity_candidates.parquet"
    print(f"Loading candidate dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    n_bat = len(df)
    print(f"Loaded {n_bat:,} deliveries.")

    candidates = [
        ('Candidate 0 (Control)', 'HP_cand0', 'Z_cand0', 'PI_cand0'),
        ('Candidate 1 (Smooth Decay)', 'HP_cand1', 'Z_cand1', 'PI_cand1'),
        ('Candidate 2 (Match-Stakes Context)', 'HP_cand2', 'Z_cand2', 'PI_cand2'),
        ('Candidate 3 (Leverage & Crisis)', 'HP_cand3', 'Z_cand3', 'PI_cand3'),
        ('Candidate 4 (Pure Task Difficulty)', 'HP_cand4', 'Z_cand4', 'PI_cand4')
    ]

    # 1. Batting Order Position Breakdown (Positions 1 to 11)
    print("\n--- 1. Batting Order Position Breakdown ---")
    pos_rows = []
    for bo in range(1, 12):
        sub = df[df['batting_order'] == bo]
        n_sub = len(sub)
        if n_sub == 0:
            continue
        role_grp = 'Top Order (1-3)' if bo <= 3 else ('Middle Order (4-6)' if bo <= 6 else 'Lower Order (7-11)')
        
        row_dict = {
            'batting_order': bo,
            'role_group': role_grp,
            'total_deliveries': n_sub,
            'pct_of_all_batting': round(n_sub / n_bat * 100.0, 2),
            'mean_task_difficulty_T': round(sub['Batting_T'].mean(), 2)
        }
        for c_name, hp_col, z_col, pi_col in candidates:
            short_name = c_name.split(' ')[1]  # 0, 1, 2, 3, 4
            hp_pct = (sub[hp_col] == True).mean() * 100.0
            row_dict[f'Cand_{short_name}_HP_pct'] = round(hp_pct, 2)
        pos_rows.append(row_dict)

    # Role summaries
    for r_name, r_orders in [('Top Order (1-3)', [1, 2, 3]), ('Middle Order (4-6)', [4, 5, 6]), ('Lower Order (7-11)', [7, 8, 9, 10, 11])]:
        sub = df[df['batting_order'].isin(r_orders)]
        row_dict = {
            'batting_order': f"Summary: {r_name}",
            'role_group': r_name,
            'total_deliveries': len(sub),
            'pct_of_all_batting': round(len(sub) / n_bat * 100.0, 2),
            'mean_task_difficulty_T': round(sub['Batting_T'].mean(), 2)
        }
        for c_name, hp_col, z_col, pi_col in candidates:
            short_name = c_name.split(' ')[1]
            hp_pct = (sub[hp_col] == True).mean() * 100.0
            row_dict[f'Cand_{short_name}_HP_pct'] = round(hp_pct, 2)
        pos_rows.append(row_dict)

    df_pos = pd.DataFrame(pos_rows)
    pos_csv = OUTPUT_DIR / "bias_and_position_comparison.csv"
    df_pos.to_csv(pos_csv, index=False)
    print(f"Saved position comparison to {pos_csv}")
    print(df_pos[['batting_order', 'total_deliveries', 'mean_task_difficulty_T',
                  'Cand_0_HP_pct', 'Cand_1_HP_pct', 'Cand_2_HP_pct', 'Cand_3_HP_pct', 'Cand_4_HP_pct']].to_string())

    # 2. Phase and Innings Representation (6 Strata)
    print("\n--- 2. Phase & Innings Breakdown ---")
    strata_rows = []
    for inn in [1, 2]:
        for ph in ['PP', 'Middle', 'Death']:
            sub = df[(df['innings'] == inn) & (df['phase'] == ph)]
            n_sub = len(sub)
            row_dict = {
                'innings': inn,
                'phase': ph,
                'total_deliveries': n_sub,
                'pct_of_all_batting': round(n_sub / n_bat * 100.0, 2),
                'mean_T': round(sub['Batting_T'].mean(), 2)
            }
            for c_name, hp_col, z_col, pi_col in candidates:
                short_name = c_name.split(' ')[1]
                hp_pct = (sub[hp_col] == True).mean() * 100.0
                row_dict[f'Cand_{short_name}_HP_pct'] = round(hp_pct, 2)
            strata_rows.append(row_dict)

    df_strata = pd.DataFrame(strata_rows)
    strata_csv = OUTPUT_DIR / "phase_innings_candidates_breakdown.csv"
    df_strata.to_csv(strata_csv, index=False)
    print(f"Saved phase & innings breakdown to {strata_csv}")
    print(df_strata[['innings', 'phase', 'total_deliveries', 'mean_T',
                     'Cand_0_HP_pct', 'Cand_1_HP_pct', 'Cand_2_HP_pct', 'Cand_3_HP_pct', 'Cand_4_HP_pct']].to_string())

    # 3. The 10 Mandated Scenario Tests
    print("\n--- 3. Testing the 10 Specific Cricket Scenarios ---")
    scenarios = [
        ('1. Top-Order Overall', df['batting_order'].isin([1, 2, 3]), 'Batting positions 1-3 (Openers & #3)'),
        ('2. Middle-Order Overall', df['batting_order'].isin([4, 5, 6]), 'Batting positions 4-6 (Anchors & Finishers)'),
        ('3. Lower-Order Overall', df['batting_order'].isin([7, 8, 9, 10, 11]), 'Batting positions 7-11 (Tailenders)'),
        ('4. Powerplay Phase', df['phase'] == 'PP', 'Overs 1-6 (Field restrictions on)'),
        ('5. Death Overs Phase', df['phase'] == 'Death', 'Overs 16-20 (Closing overs)'),
        ('6. 1st Inn PP Collapse', (df['innings'] == 1) & (df['phase'] == 'PP') & (df['wickets_before'] >= 3), 'Inn 1, PP, 3+ wkts down (e.g. 20/3 in over 4)'),
        ('7. Competitive Death Finish', (df['innings'] == 2) & (df['overid'] >= 18) & (df['wp_before'].between(0.30, 0.70)) & (df['balls_remaining'] <= 12), 'Inn 2, Over 18+, WP 30-70%, <=12b rem (e.g. 10 off 6)'),
        ('8. Hopeless Chase / Blowout', (df['innings'] == 2) & (df['overid'] >= 13) & (df['wp_before'] < 0.05) & (df['required_run_rate'] > 12.0), 'Inn 2, Over 13+, WP < 5%, RRR > 12 (e.g. 60/7 chasing 190)'),
        ('9. Middle-Over Squeeze', (df['innings'] == 2) & (df['overid'].between(10, 16)) & (df['wp_before'].between(0.40, 0.60)) & (df['wickets_before'].between(3, 5)) & (df['required_run_rate'].between(9.0, 12.0)), 'Inn 2, Over 10-16, WP 40-60%, 3-5 down, RRR 9-12'),
        ('10. Set Batters in Crisis', (df['striker_balls_faced_before'] >= 15) & (df['Batting_T'] > 65.0), 'Set batters (bf >= 15) facing severe crisis (T > 65)')
    ]

    scenario_rows = []
    for s_name, mask, desc in scenarios:
        sub = df[mask]
        n_sub = len(sub)
        row_dict = {
            'scenario_name': s_name,
            'description': desc,
            'total_deliveries': n_sub,
            'pct_of_all_batting': round(n_sub / n_bat * 100.0, 2),
            'mean_T': round(sub['Batting_T'].mean(), 2) if n_sub > 0 else np.nan,
            'mean_I_control': round(sub['I_cand0'].mean(), 2) if n_sub > 0 else np.nan
        }
        for c_name, hp_col, z_col, pi_col in candidates:
            short_name = c_name.split(' ')[1]
            hp_pct = (sub[hp_col] == True).mean() * 100.0 if n_sub > 0 else 0.0
            row_dict[f'Cand_{short_name}_HP_pct'] = round(hp_pct, 2)
            row_dict[f'Cand_{short_name}_HP_count'] = int((sub[hp_col] == True).sum()) if n_sub > 0 else 0

        scenario_rows.append(row_dict)

    df_scenarios = pd.DataFrame(scenario_rows)
    scen_csv = OUTPUT_DIR / "scenario_testing_audit.csv"
    df_scenarios.to_csv(scen_csv, index=False)
    print(f"Saved scenario testing audit to {scen_csv}")
    print("\n10 Cricket Scenarios Audit Table:")
    print(df_scenarios[['scenario_name', 'total_deliveries', 'mean_T', 'mean_I_control',
                        'Cand_0_HP_pct', 'Cand_1_HP_pct', 'Cand_2_HP_pct', 'Cand_3_HP_pct', 'Cand_4_HP_pct']].to_string())

    print(f"\nTotal time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
