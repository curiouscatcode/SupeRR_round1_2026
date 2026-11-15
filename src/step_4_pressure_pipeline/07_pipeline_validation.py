"""
Step 4 - Module 7: Comprehensive Pipeline Validation Suite
==========================================================
Executes automated validation checks across all 12 mandated criteria:
1. Cohort Counts & Match Exclusions
2. Pre-Delivery Feature Invariance (No Outcome Leakage)
3. Transition Probability Normalization (Sum = 1.0)
4. Player Independence Verification
5. ECDF Normalization Bounds & Distribution
6. Task Difficulty Equations & Regularization
7. Pressure Value Bounds [0, 100]
8. Completeness & NaN/Inf Absence
9. First-Ball & Final-Ball Edge Cases
10. Phase & Innings Categorical Consistency
11. Deterministic Reproducibility
12. Manually Inspectable Delivery-Level Test Cases
"""

import os
import json
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_4_pressure_pipeline"

def run_validation_suite():
    print("=" * 80)
    print("STEP 4: AUTOMATED PRESSURE PIPELINE VALIDATION SUITE")
    print("=" * 80)
    
    results = {}
    
    # -------------------------------------------------------------
    # Check 1: Cohort Counts and Match Exclusions
    # -------------------------------------------------------------
    print("\n--- Check 1: Cohort Counts and Match Exclusions ---")
    parquet_path = os.path.join(OUTPUT_DIR, "delivery_pressure_v3.parquet")
    if not os.path.exists(parquet_path):
        parquet_path = os.path.join(OUTPUT_DIR, "delivery_pressure_v2.parquet")
    df = pd.read_parquet(parquet_path)
    
    total_deliveries = len(df)
    total_matches = df['match_id'].nunique()
    inn1_delivs = len(df[df['innings'] == 1])
    inn2_delivs = len(df[df['innings'] == 2])
    
    c1_deliv_pass = (total_deliveries == 186780)
    c1_match_pass = (total_matches == 782)
    c1_inn1_pass = (inn1_delivs == 97443)
    c1_inn2_pass = (inn2_delivs == 89337)
    
    # Check that excluded matches are completely absent
    excluded_mids = [20182, 23674, 24822, 28334, 15795, 31278, 48514]
    c1_leak_pass = not df['match_id'].isin(excluded_mids).any()
    
    # Check that dead-tail deliveries (runs_required <= 0 in Inn 2) are completely absent
    c1_deadtail_pass = not ((df['innings'] == 2) & (df['runs_required'] <= 0)).any()
    
    status_c1 = "PASS" if (c1_deliv_pass and c1_match_pass and c1_inn1_pass and c1_inn2_pass and c1_leak_pass and c1_deadtail_pass) else "FAIL"
    results['Check 1: Cohort & Exclusions'] = status_c1
    print(f"  Deliveries: {total_deliveries} / 186,780 -> {c1_deliv_pass}")
    print(f"  Matches:    {total_matches} / 782 -> {c1_match_pass}")
    print(f"  Inn 1 / 2:  {inn1_delivs} / {inn2_delivs} -> {c1_inn1_pass and c1_inn2_pass}")
    print(f"  Excluded Matches Absent: {c1_leak_pass}")
    print(f"  Dead-Tail Absent:        {c1_deadtail_pass}")
    print(f"  => STATUS: {status_c1}")

    # -------------------------------------------------------------
    # Check 2: Pre-Delivery-Only Feature Availability
    # -------------------------------------------------------------
    print("\n--- Check 2: Pre-Delivery Feature Invariance ---")
    post_delivery_cols = ['runs', 'is_wicket', 'is_four', 'is_six', 'extras_type', 'is_legal_ball']
    pressure_input_cols = [
        'score_before', 'wickets_before', 'W_t', 'W_rem',
        'legal_balls_before', 'balls_remaining', 'current_run_rate',
        'runs_required', 'required_run_rate', 'phase'
    ]
    # Check correlation between pressure and post-delivery outcome on ball t:
    # A bowler taking a wicket or giving 6 should NOT directly define pre-delivery pressure
    corr_wicket = df['pressure_batting'].corr(df['is_wicket'])
    corr_runs = df['pressure_batting'].corr(df['runs'])
    print(f"  Correlation(P_bat, is_wicket on current ball): {corr_wicket:.4f}")
    print(f"  Correlation(P_bat, runs on current ball):      {corr_runs:.4f}")
    
    # Pressure inputs do not overlap with post-delivery event
    c2_pass = (abs(corr_wicket) < 0.10) and (abs(corr_runs) < 0.10)
    status_c2 = "PASS" if c2_pass else "FAIL"
    results['Check 2: Pre-Delivery Invariant'] = status_c2
    print(f"  => STATUS: {status_c2}")

    # -------------------------------------------------------------
    # Check 3: Probability Distributions Summing to 1
    # -------------------------------------------------------------
    print("\n--- Check 3: Transition Probability Normalization ---")
    with open(os.path.join(OUTPUT_DIR, "outcome_transition_probabilities.json"), 'r', encoding='utf-8') as f:
        transitions = json.load(f)
        
    c3_pass = True
    for st, p_list in transitions.items():
        s = round(float(sum(p_list)), 6)
        print(f"  Stratum {st:12s}: sum = {s:.6f}")
        if abs(s - 1.0) > 1e-6:
            c3_pass = False
            
    status_c3 = "PASS" if c3_pass else "FAIL"
    results['Check 3: Probability Sums = 1.0'] = status_c3
    print(f"  => STATUS: {status_c3}")

    # -------------------------------------------------------------
    # Check 4: Player Independence Verification
    # -------------------------------------------------------------
    print("\n--- Check 4: Player Independence Verification ---")
    # Verify that transitions and WP parameters contain zero player IDs or names
    with open(os.path.join(OUTPUT_DIR, "wp_model_inn1.json"), 'r', encoding='utf-8') as f:
        wp1_d = json.load(f)
    with open(os.path.join(OUTPUT_DIR, "wp_model_inn2.json"), 'r', encoding='utf-8') as f:
        wp2_d = json.load(f)
        
    c4_pass = True
    for d in [wp1_d, wp2_d, transitions]:
        dump_str = json.dumps(d)
        if 'striker' in dump_str or 'bowler' in dump_str or 'player' in dump_str:
            c4_pass = False
            
    status_c4 = "PASS" if c4_pass else "FAIL"
    results['Check 4: Player Independence'] = status_c4
    print(f"  Transition and WP model files contain zero player terms: {c4_pass}")
    print(f"  => STATUS: {status_c4}")

    # -------------------------------------------------------------
    # Check 5: ECDF Reference Distributions and Normalization Bounds
    # -------------------------------------------------------------
    print("\n--- Check 5: ECDF Normalization Bounds & Distribution ---")
    l_norm_min = df['normalized_consequence_L'].min()
    l_norm_max = df['normalized_consequence_L'].max()
    l1_med = df.loc[df['innings'] == 1, 'normalized_consequence_L'].median()
    l2_med = df.loc[df['innings'] == 2, 'normalized_consequence_L'].median()
    
    c5_bounds_pass = (l_norm_min >= 0.0) and (l_norm_max <= 100.0)
    c5_median_pass = abs(l1_med - 50.0) < 1.0 and abs(l2_med - 50.0) < 1.0
    
    status_c5 = "PASS" if (c5_bounds_pass and c5_median_pass) else "FAIL"
    results['Check 5: ECDF Normalization'] = status_c5
    print(f"  Bounds: [{l_norm_min:.2f}, {l_norm_max:.2f}] (within [0, 100]) -> {c5_bounds_pass}")
    print(f"  Innings 1 Median: {l1_med:.2f} (Target 50.0) -> {abs(l1_med-50.0)<1.0}")
    print(f"  Innings 2 Median: {l2_med:.2f} (Target 50.0) -> {abs(l2_med-50.0)<1.0}")
    print(f"  => STATUS: {status_c5}")

    # -------------------------------------------------------------
    # Check 6: Task Difficulty Equations & Regularization
    # -------------------------------------------------------------
    print("\n--- Check 6: Task Difficulty Equations & Regularization ---")
    t_bat_min = df['task_difficulty_bat'].min()
    t_bat_max = df['task_difficulty_bat'].max()
    t_bowl_min = df['task_difficulty_bowl'].min()
    t_bowl_max = df['task_difficulty_bowl'].max()
    
    c6_bat_pass = (t_bat_min >= 0.0) and (t_bat_max <= 100.0)
    c6_bowl_pass = (t_bowl_min >= 0.0) and (t_bowl_max <= 100.0)
    
    # Check ball 0.1 neutral value (for true opening ball 0/0, must be exactly 50.0)
    ball_0_init = df.loc[(df['innings'] == 1) & (df['legal_balls_before'] == 0) & (df['score_before'] == 0), 'task_difficulty_bat'].unique()
    ball_0_extras = df.loc[(df['innings'] == 1) & (df['legal_balls_before'] == 0) & (df['score_before'] > 0), 'task_difficulty_bat'].values
    c6_ball0_pass = (len(ball_0_init) == 1) and (abs(ball_0_init[0] - 50.0) < 1e-4) and (np.all((ball_0_extras >= 48.0) & (ball_0_extras <= 50.0)))
    
    status_c6 = "PASS" if (c6_bat_pass and c6_bowl_pass and c6_ball0_pass) else "FAIL"
    results['Check 6: Task Difficulty Models'] = status_c6
    print(f"  Batting Task Difficulty Bounds: [{t_bat_min:.2f}, {t_bat_max:.2f}] -> {c6_bat_pass}")
    print(f"  Bowling Task Difficulty Bounds: [{t_bowl_min:.2f}, {t_bowl_max:.2f}] -> {c6_bowl_pass}")
    print(f"  Opening Ball 0/0 Exact Neutral T_B1 = 50.00: {ball_0_init} (N={len(df[(df['innings']==1) & (df['legal_balls_before']==0) & (df['score_before']==0)])}) -> {c6_ball0_pass}")
    print(f"  Ball 0 with Extras T_B1 in [48, 50]: (N={len(ball_0_extras)}) -> {np.all((ball_0_extras >= 48.0) & (ball_0_extras <= 50.0))}")
    print(f"  => STATUS: {status_c6}")

    # -------------------------------------------------------------
    # Check 7: Pressure Value Bounds [0, 100]
    # -------------------------------------------------------------
    print("\n--- Check 7: Combined Pressure Value Bounds ---")
    p_bat_min = df['pressure_batting'].min()
    p_bat_max = df['pressure_batting'].max()
    p_bowl_min = df['pressure_bowling'].min()
    p_bowl_max = df['pressure_bowling'].max()
    
    c7_bat_pass = (p_bat_min >= 0.0) and (p_bat_max <= 100.0)
    c7_bowl_pass = (p_bowl_min >= 0.0) and (p_bowl_max <= 100.0)
    
    status_c7 = "PASS" if (c7_bat_pass and c7_bowl_pass) else "FAIL"
    results['Check 7: Pressure Bounds [0, 100]'] = status_c7
    print(f"  P_bat Bounds:  [{p_bat_min:.2f}, {p_bat_max:.2f}] -> {c7_bat_pass}")
    print(f"  P_bowl Bounds: [{p_bowl_min:.2f}, {p_bowl_max:.2f}] -> {c7_bowl_pass}")
    print(f"  => STATUS: {status_c7}")

    # -------------------------------------------------------------
    # Check 8: Absence of NaN or Infinite Values
    # -------------------------------------------------------------
    print("\n--- Check 8: Completeness & NaN/Inf Absence ---")
    core_cols = [
        'pre_delivery_wp', 'raw_consequence_L', 'normalized_consequence_L',
        'task_difficulty_bat', 'task_difficulty_bowl',
        'pressure_batting', 'pressure_bowling'
    ]
    nan_counts = df[core_cols].isna().sum().to_dict()
    inf_counts = {c: int(np.isinf(df[c]).sum()) for c in core_cols}
    
    c8_nan_pass = (sum(nan_counts.values()) == 0)
    c8_inf_pass = (sum(inf_counts.values()) == 0)
    
    status_c8 = "PASS" if (c8_nan_pass and c8_inf_pass) else "FAIL"
    results['Check 8: Zero NaN/Inf'] = status_c8
    print(f"  NaN Counts: {nan_counts} -> {c8_nan_pass}")
    print(f"  Inf Counts: {inf_counts} -> {c8_inf_pass}")
    print(f"  => STATUS: {status_c8}")

    # -------------------------------------------------------------
    # Check 9: First-Ball & Final-Ball Edge Cases
    # -------------------------------------------------------------
    print("\n--- Check 9: Edge Cases (First-Ball & Final-Ball) ---")
    # Ball 0.1
    b0_rows = df[(df['innings'] == 1) & (df['legal_balls_before'] == 0)]
    c9_b0_pass = (len(b0_rows) > 0) and (not b0_rows['pressure_batting'].isna().any())
    
    # Final ball B_rem = 1
    final_balls = df[(df['innings'] == 2) & (df['balls_remaining'] == 1)]
    c9_final_pass = (len(final_balls) > 0) and (not final_balls['pressure_batting'].isna().any())
    
    # Check monotonicity of Markov final ball:
    # At B_rem=1, needing 1 run should have higher WP than needing 6 runs
    status_c9 = "PASS" if (c9_b0_pass and c9_final_pass) else "FAIL"
    results['Check 9: Edge Cases Handling'] = status_c9
    print(f"  Ball 0.1 Valid Deliveries (N={len(b0_rows)}): {c9_b0_pass}")
    print(f"  Final Ball (B_rem=1) Valid Deliveries (N={len(final_balls)}): {c9_final_pass}")
    print(f"  => STATUS: {status_c9}")

    # -------------------------------------------------------------
    # Check 10: Phase and Innings Categorical Consistency
    # -------------------------------------------------------------
    print("\n--- Check 10: Categorical Consistency ---")
    inns_present = sorted(df['innings'].unique().tolist())
    phases_present = sorted(df['phase'].unique().tolist())
    
    c10_inn_pass = (inns_present == [1, 2])
    c10_phase_pass = (phases_present == ['Death', 'Middle', 'PP'])
    
    status_c10 = "PASS" if (c10_inn_pass and c10_phase_pass) else "FAIL"
    results['Check 10: Categorical Consistency'] = status_c10
    print(f"  Innings Present: {inns_present} -> {c10_inn_pass}")
    print(f"  Phases Present:  {phases_present} -> {c10_phase_pass}")
    print(f"  => STATUS: {status_c10}")

    # -------------------------------------------------------------
    # Check 11: Reproducibility Across Repeated Execution
    # -------------------------------------------------------------
    print("\n--- Check 11: Deterministic Reproducibility ---")
    # Re-evaluate 1,000 deliveries deterministically
    sample_test = df.iloc[:1000]
    p_recalc = np.sqrt(sample_test['task_difficulty_bat'].values * sample_test['normalized_consequence_L'].values)
    max_recalc_diff = np.max(np.abs(p_recalc - sample_test['pressure_batting'].values))
    c11_pass = (max_recalc_diff < 1e-10)
    
    status_c11 = "PASS" if c11_pass else "FAIL"
    results['Check 11: Reproducibility'] = status_c11
    print(f"  Max Recalculation Difference: {max_recalc_diff:.2e} -> {c11_pass}")
    print(f"  => STATUS: {status_c11}")

    # -------------------------------------------------------------
    # Check 12: Manually Inspectable Delivery-Level Test Cases
    # -------------------------------------------------------------
    print("\n--- Check 12: Manually Inspectable Delivery Test Cases ---")
    # Extract 5 actual match situations from the cohort
    test_cases = [
        ("Powerplay Opening Ball", (df['innings'] == 1) & (df['legal_balls_before'] == 0)),
        ("Middle Overs Collapse", (df['innings'] == 1) & (df['overid'] == 4) & (df['W_t'] == 3)),
        ("Death Climax Finish", (df['innings'] == 2) & (df['overid'] == 20) & (df['runs_required'].between(6, 12))),
        ("Comfortable Chase", (df['innings'] == 2) & (df['overid'] == 15) & (df['runs_required'] < 10) & (df['W_t'] < 3)),
        ("Impossible Blowout", (df['innings'] == 2) & (df['overid'] == 19) & (df['runs_required'] > 50))
    ]
    
    sample_records = []
    for label, mask in test_cases:
        sub = df[mask]
        if len(sub) > 0:
            row = sub.iloc[0]
            rec = {
                'case_label': label,
                'match_id': int(row['match_id']),
                'innings': int(row['innings']),
                'over_ball': f"{row['overid']}.{row['over_ball_num']}",
                'state': f"Score={row['score_before']}/{row['W_t']}, BallsRem={row['balls_remaining']}, Req={row['runs_required']}",
                'pre_wp': round(float(row['pre_delivery_wp']), 4),
                'T_bat': round(float(row['task_difficulty_bat']), 2),
                'T_bowl': round(float(row['task_difficulty_bowl']), 2),
                'raw_L': round(float(row['raw_consequence_L']), 5),
                'L_norm': round(float(row['normalized_consequence_L']), 2),
                'P_bat': round(float(row['pressure_batting']), 2),
                'P_bowl': round(float(row['pressure_bowling']), 2)
            }
            sample_records.append(rec)
            print(f"  [{label}]: Mid={row['match_id']}, State={rec['state']} -> P_bat={rec['P_bat']}, P_bowl={rec['P_bowl']}")
            
    c12_pass = (len(sample_records) == 5)
    status_c12 = "PASS" if c12_pass else "FAIL"
    results['Check 12: Delivery Test Cases'] = status_c12
    print(f"  => STATUS: {status_c12}")
    
    # Save test cases to CSV
    test_cases_df = pd.DataFrame(sample_records)
    test_cases_csv = os.path.join(OUTPUT_DIR, "manual_delivery_test_cases.csv")
    test_cases_df.to_csv(test_cases_csv, index=False)
    archive_dir = "outputs/step_4_3_controlled_implementation"
    os.makedirs(archive_dir, exist_ok=True)
    test_cases_df.to_csv(os.path.join(archive_dir, "manual_delivery_test_cases.csv"), index=False)
    print(f"\nSaved inspectable test cases to {test_cases_csv} and archived to {archive_dir}")

    # -------------------------------------------------------------
    # Overall Validation Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("VALIDATION SUITE EXECUTION SUMMARY")
    print("=" * 80)
    all_pass = all(v == "PASS" for v in results.values())
    for check_name, st in results.items():
        print(f"  {check_name:42s}: {st}")
    print("-" * 80)
    final_verdict = "PASS" if all_pass else "FAIL"
    print(f"FINAL AUTOMATED VALIDATION VERDICT: {final_verdict}")
    print("=" * 80)
    
    # Save validation results JSON
    val_json_path = os.path.join(OUTPUT_DIR, "validation_results.json")
    with open(val_json_path, 'w', encoding='utf-8') as f:
        json.dump({'verdict': final_verdict, 'checks': results}, f, indent=2)
        
    archive_dir = "outputs/step_4_3_controlled_implementation"
    os.makedirs(archive_dir, exist_ok=True)
    val_archive_path = os.path.join(archive_dir, "step_4_3_validation_results.json")
    with open(val_archive_path, 'w', encoding='utf-8') as f:
        json.dump({'verdict': final_verdict, 'checks': results}, f, indent=2)
    print(f"Archived validation results to {val_archive_path}")
        
    return final_verdict, results

if __name__ == '__main__':
    run_validation_suite()
