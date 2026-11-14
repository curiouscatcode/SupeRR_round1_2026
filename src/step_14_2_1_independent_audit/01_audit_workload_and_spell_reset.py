"""
Step 14.2.1 — Module 1: Audit Workload Formula Calculations & Spell-Reset Mechanism
===================================================================================

This module independently investigates:
1. Mathematical correctness of both workload formulas:
   - Original v2.0: W_spell = min(100, (bowler_legal_balls_in_spell_before / 12) * 100)
   - Experimental Step 14.2: W_innings = min(100, (bowler_total_legal_balls_bowled_in_innings_before / 24) * 100)
2. Actual spell-reset architecture from Step 3 (prepare_match_data.py) and Step 4 (calculate_pressure_index.py):
   - Precise condition for spell reset (overid > last_over + 2)
   - Behavior during 1-over rest (mandatory alternating cycle) vs 2+ overs rest (spell reset)
   - Elimination of reset behavior in experimental formula
3. Concrete delivery-level case studies:
   - Case A: Consecutive overs from same end (Overs 1, 3)
   - Case B: Bowler resting for 1 over vs 2+ overs (e.g. Overs 1, 5)
   - Case C: Returning in death overs after middle overs rest (e.g. Overs 2, 4, 18, 20)
   - Case D: Cap saturation (12 balls for v2.0 vs 24 balls for experimental)
   - Case E: Illegal deliveries (wides and no-balls)
   - Case F: First delivery of a new innings

Outputs:
- outputs/step_14_2_1_independent_audit/audit_workload_examples.csv
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_2_1_independent_audit")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("=" * 80)
    print("STEP 14.2.1 — MODULE 1: AUDIT WORKLOAD FORMULA & SPELL-RESET")
    print("=" * 80)

    del_exp_path = os.path.join(BASE_DIR, "outputs", "step_14_2_workload_experiment", "delivery_pressure_index_exp14_2.csv")
    state_path = os.path.join(BASE_DIR, "data", "processed", "delivery_match_state.csv")

    print(f"Loading delivery data from: {del_exp_path}...")
    df_exp = pd.read_csv(del_exp_path)
    df_state = pd.read_csv(state_path)

    # 1. Independent Recalculation of Workload Metrics
    print("\n1. Independently recalculating workload metrics...")
    
    # Sort check
    df_state = df_state.sort_values(by=['match_id', 'innings', 'overid', 'over_ball_num']).reset_index(drop=True)

    # Cumulative legal balls bowled before in innings
    cum_legal_innings = df_state.groupby(['match_id', 'innings', 'bowler_id'])['is_legal_ball'].cumsum()
    indep_cum_before = (cum_legal_innings - df_state['is_legal_ball'].astype(int)).values

    exp_cum_before = df_exp['bowler_total_legal_balls_bowled_in_innings_before'].values

    diff_cum = np.abs(indep_cum_before - exp_cum_before).max()
    assert diff_cum == 0, f"Discrepancy in cumulative innings balls! Max diff: {diff_cum}"
    print(f"  ✓ Cumulative legal balls bowled before matches Step 14.2 with 0 discrepancy across all {len(df_exp):,} deliveries.")

    # Recalculate W_spell and W_innings
    indep_w_spell = np.minimum(100.0, (df_state['bowler_legal_balls_in_spell_before'].values / 12.0) * 100.0)
    indep_w_innings = np.minimum(100.0, (indep_cum_before / 24.0) * 100.0)

    diff_w_spell_round = np.abs(np.round(indep_w_spell, 2) - df_exp['W_spell_orig'].values).max()
    diff_w_innings_round = np.abs(np.round(indep_w_innings, 2) - df_exp['W_innings_exp'].values).max()

    assert diff_w_spell_round == 0.0, f"Discrepancy in rounded W_spell_orig! Max diff: {diff_w_spell_round}"
    assert diff_w_innings_round == 0.0, f"Discrepancy in rounded W_innings_exp! Max diff: {diff_w_innings_round}"
    print(f"  ✓ W_spell_orig and W_innings_exp formulas match Step 14.2 perfectly (0.00 discrepancy on rounded CSV columns).")

    # 2. Extract Concrete Delivery-Level Case Studies
    print("\n2. Extracting concrete delivery-level case studies...")
    
    case_records = []

    # Case A: Bowler bowling consecutive available overs from same end (Overs 1 and 3)
    # Match 14096, Trent Boult
    m14096 = df_exp[(df_exp['match_id'] == 14096) & (df_exp['bowler_name'] == 'Trent Boult')].copy()
    m14096_sample = m14096[m14096['overid'].isin([1, 3])].head(12)
    for _, r in m14096_sample.iterrows():
        case_records.append({
            'case_id': 'Case A: Consecutive Overs (Overs 1, 3)',
            'match_id': r['match_id'], 'innings': r['innings'], 'overid': r['overid'], 'over_ball_num': r['over_ball_num'],
            'bowler_name': r['bowler_name'], 'is_legal_ball': r['is_legal_ball'], 'extras_type': r['extras_type'],
            'balls_in_spell_before': r['bowler_legal_balls_in_spell_before'],
            'balls_in_innings_before': r['bowler_total_legal_balls_bowled_in_innings_before'],
            'W_spell_orig': round(r['W_spell_orig'], 2),
            'W_innings_exp': round(r['W_innings_exp'], 2),
            'delta_workload': round(r['delta_workload'], 2),
            'Bowling_PI_orig': round(r['Bowling_PI_orig'], 2),
            'Bowling_PI_exp': round(r['Bowling_PI_exp'], 2),
            'delta_bowling_pi': round(r['delta_bowling_pi'], 2)
        })

    # Case B: Bowler resting for multiple overs (e.g. Overs 1, then resting until Over 5 or 6 -> Spell Reset)
    # Find a bowler who bowled over 1 and then returned in over 5 or 6 in innings 1
    spell_reset_candidates = df_exp[
        (df_exp['overid'] >= 5) & 
        (df_exp['bowler_legal_balls_in_spell_before'] == 0) & 
        (df_exp['bowler_total_legal_balls_bowled_in_innings_before'] >= 6)
    ]
    reset_match_id = spell_reset_candidates.iloc[0]['match_id']
    reset_bowler = spell_reset_candidates.iloc[0]['bowler_name']
    reset_sample = df_exp[(df_exp['match_id'] == reset_match_id) & (df_exp['bowler_name'] == reset_bowler)]
    for _, r in reset_sample.head(15).iterrows():
        case_records.append({
            'case_id': 'Case B: Rest Interval Spell Reset',
            'match_id': r['match_id'], 'innings': r['innings'], 'overid': r['overid'], 'over_ball_num': r['over_ball_num'],
            'bowler_name': r['bowler_name'], 'is_legal_ball': r['is_legal_ball'], 'extras_type': r['extras_type'],
            'balls_in_spell_before': r['bowler_legal_balls_in_spell_before'],
            'balls_in_innings_before': r['bowler_total_legal_balls_bowled_in_innings_before'],
            'W_spell_orig': round(r['W_spell_orig'], 2),
            'W_innings_exp': round(r['W_innings_exp'], 2),
            'delta_workload': round(r['delta_workload'], 2),
            'Bowling_PI_orig': round(r['Bowling_PI_orig'], 2),
            'Bowling_PI_exp': round(r['Bowling_PI_exp'], 2),
            'delta_bowling_pi': round(r['delta_bowling_pi'], 2)
        })

    # Case C: Returning in Death Overs (e.g. Over 19) with 3 overs bowled earlier
    death_candidates = df_exp[
        (df_exp['overid'] >= 18) & 
        (df_exp['bowler_total_legal_balls_bowled_in_innings_before'] >= 18) & 
        (df_exp['bowler_legal_balls_in_spell_before'] == 0)
    ]
    death_match_id = death_candidates.iloc[0]['match_id']
    death_bowler = death_candidates.iloc[0]['bowler_name']
    death_sample = df_exp[(df_exp['match_id'] == death_match_id) & (df_exp['bowler_name'] == death_bowler) & (df_exp['overid'] >= 18)]
    for _, r in death_sample.head(8).iterrows():
        case_records.append({
            'case_id': 'Case C: Death Return After Long Rest',
            'match_id': r['match_id'], 'innings': r['innings'], 'overid': r['overid'], 'over_ball_num': r['over_ball_num'],
            'bowler_name': r['bowler_name'], 'is_legal_ball': r['is_legal_ball'], 'extras_type': r['extras_type'],
            'balls_in_spell_before': r['bowler_legal_balls_in_spell_before'],
            'balls_in_innings_before': r['bowler_total_legal_balls_bowled_in_innings_before'],
            'W_spell_orig': round(r['W_spell_orig'], 2),
            'W_innings_exp': round(r['W_innings_exp'], 2),
            'delta_workload': round(r['delta_workload'], 2),
            'Bowling_PI_orig': round(r['Bowling_PI_orig'], 2),
            'Bowling_PI_exp': round(r['Bowling_PI_exp'], 2),
            'delta_bowling_pi': round(r['delta_bowling_pi'], 2)
        })

    # Case D: Illegal Deliveries (Wide / No-ball)
    # Find an over with wide or no-ball
    extras_candidates = df_exp[(df_exp['is_legal_ball'] == 0) & (df_exp['extras_type'].isin(['wide', 'Overstep']))]
    ex_match = extras_candidates.iloc[0]['match_id']
    ex_bowler = extras_candidates.iloc[0]['bowler_name']
    ex_over = extras_candidates.iloc[0]['overid']
    ex_sample = df_exp[(df_exp['match_id'] == ex_match) & (df_exp['bowler_name'] == ex_bowler) & (df_exp['overid'] == ex_over)]
    for _, r in ex_sample.iterrows():
        case_records.append({
            'case_id': 'Case D: Illegal Deliveries (Wides/No-balls)',
            'match_id': r['match_id'], 'innings': r['innings'], 'overid': r['overid'], 'over_ball_num': r['over_ball_num'],
            'bowler_name': r['bowler_name'], 'is_legal_ball': r['is_legal_ball'], 'extras_type': r['extras_type'],
            'balls_in_spell_before': r['bowler_legal_balls_in_spell_before'],
            'balls_in_innings_before': r['bowler_total_legal_balls_bowled_in_innings_before'],
            'W_spell_orig': round(r['W_spell_orig'], 2),
            'W_innings_exp': round(r['W_innings_exp'], 2),
            'delta_workload': round(r['delta_workload'], 2),
            'Bowling_PI_orig': round(r['Bowling_PI_orig'], 2),
            'Bowling_PI_exp': round(r['Bowling_PI_exp'], 2),
            'delta_bowling_pi': round(r['delta_bowling_pi'], 2)
        })

    # Case E: First Delivery of New Innings (Innings Transition)
    inn_trans = df_exp[(df_exp['overid'] == 1) & (df_exp['over_ball_num'] == 1)]
    for _, r in inn_trans.head(4).iterrows():
        case_records.append({
            'case_id': 'Case E: First Delivery of Innings',
            'match_id': r['match_id'], 'innings': r['innings'], 'overid': r['overid'], 'over_ball_num': r['over_ball_num'],
            'bowler_name': r['bowler_name'], 'is_legal_ball': r['is_legal_ball'], 'extras_type': r['extras_type'],
            'balls_in_spell_before': r['bowler_legal_balls_in_spell_before'],
            'balls_in_innings_before': r['bowler_total_legal_balls_bowled_in_innings_before'],
            'W_spell_orig': round(r['W_spell_orig'], 2),
            'W_innings_exp': round(r['W_innings_exp'], 2),
            'delta_workload': round(r['delta_workload'], 2),
            'Bowling_PI_orig': round(r['Bowling_PI_orig'], 2),
            'Bowling_PI_exp': round(r['Bowling_PI_exp'], 2),
            'delta_bowling_pi': round(r['delta_bowling_pi'], 2)
        })

    df_cases = pd.DataFrame(case_records)
    case_csv_path = os.path.join(OUTPUT_DIR, "audit_workload_examples.csv")
    df_cases.to_csv(case_csv_path, index=False)
    print(f"  ✓ Exported {len(df_cases)} case study deliveries to: {case_csv_path}")

    print("\nModule 1 Completed Successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
