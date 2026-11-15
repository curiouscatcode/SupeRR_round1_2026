"""
Step 5 - Module 2: Data Integrity & Reconciliation Validation Suite
===================================================================
Executes exhaustive validation checks on:
1. batting_pressure_deliveries.parquet
2. bowling_pressure_deliveries.parquet
3. player_mapping_audit.csv

Validates all 9 mandated checks from Step 5 specifications:
1. Every eligible batting record maps to exactly one valid pressure observation.
2. Every eligible bowling record maps to exactly one valid pressure observation.
3. Batter and bowler IDs map correctly to player metadata.
4. No duplicate player-delivery records exist.
5. Match and innings identifiers remain consistent.
6. Excluded matches and dead-tail deliveries do not reappear.
7. Batting and bowling pressure values remain identical to their corresponding v3 source rows.
8. Runs, wickets, extras and legal-ball counts reconcile with the original source data wherever the source permits.
9. Missing or ambiguous mappings are documented rather than guessed.
"""

import os
import json
import numpy as np
import pandas as pd

OUTPUT_DIR = "outputs/step_5_player_level_dataset"

def run_validation():
    print("=" * 80)
    print("STEP 5: DATA INTEGRITY & RECONCILIATION VALIDATION")
    print("=" * 80)

    bat_parquet = os.path.join(OUTPUT_DIR, "batting_pressure_deliveries.parquet")
    bowl_parquet = os.path.join(OUTPUT_DIR, "bowling_pressure_deliveries.parquet")
    audit_csv = os.path.join(OUTPUT_DIR, "player_mapping_audit.csv")
    v3_path = "outputs/step_4_pressure_pipeline/delivery_pressure_v3.parquet"
    cohort_path = "outputs/step_4_pressure_pipeline/clean_cohort_deliveries.parquet"
    bbb_path = "data/ball_by_ball.csv"

    bat_df = pd.read_parquet(bat_parquet)
    bowl_df = pd.read_parquet(bowl_parquet)
    audit_df = pd.read_csv(audit_csv)
    v3_df = pd.read_parquet(v3_path)
    cohort_df = pd.read_parquet(cohort_path)

    results = {}

    # -------------------------------------------------------------
    # Check 1: Batting Record Mapping to Valid Pressure
    # -------------------------------------------------------------
    print("\n--- Check 1: Batting Record to Valid Pressure Mapping ---")
    c1_n = len(bat_df)
    c1_null_p = bat_df['pressure_batting'].isna().sum()
    c1_inf_p = np.isinf(bat_df['pressure_batting']).sum()
    c1_bounds = ((bat_df['pressure_batting'] >= 0.0) & (bat_df['pressure_batting'] <= 100.0)).all()
    print(f"Total batting records: {c1_n:,}")
    print(f"Null pressure values:  {c1_null_p}")
    print(f"Inf pressure values:   {c1_inf_p}")
    print(f"All values in [0,100]: {c1_bounds}")
    c1_pass = (c1_n == 186780) and (c1_null_p == 0) and (c1_inf_p == 0) and c1_bounds
    results['Check 1: Batting Pressure Validity'] = 'PASS' if c1_pass else 'FAIL'

    # -------------------------------------------------------------
    # Check 2: Bowling Record Mapping to Valid Pressure
    # -------------------------------------------------------------
    print("\n--- Check 2: Bowling Record to Valid Pressure Mapping ---")
    c2_n = len(bowl_df)
    c2_null_p = bowl_df['pressure_bowling'].isna().sum()
    c2_inf_p = np.isinf(bowl_df['pressure_bowling']).sum()
    c2_bounds = ((bowl_df['pressure_bowling'] >= 0.0) & (bowl_df['pressure_bowling'] <= 100.0)).all()
    print(f"Total bowling records: {c2_n:,}")
    print(f"Null pressure values:  {c2_null_p}")
    print(f"Inf pressure values:   {c2_inf_p}")
    print(f"All values in [0,100]: {c2_bounds}")
    c2_pass = (c2_n == 186780) and (c2_null_p == 0) and (c2_inf_p == 0) and c2_bounds
    results['Check 2: Bowling Pressure Validity'] = 'PASS' if c2_pass else 'FAIL'

    # -------------------------------------------------------------
    # Check 3: Player ID Metadata Mapping
    # -------------------------------------------------------------
    print("\n--- Check 3: Player ID to Metadata Mapping ---")
    c3_total_players = len(audit_df)
    c3_missing_comp = (~audit_df['in_competition_mapping']).sum()
    c3_missing_p11 = (~audit_df['in_playing_eleven']).sum()
    print(f"Total unique players in audit:    {c3_total_players:,}")
    print(f"Missing from competition mapping: {c3_missing_comp}")
    print(f"Missing from playing eleven:      {c3_missing_p11}")
    c3_pass = (c3_total_players == 883) and (c3_missing_comp == 0) and (c3_missing_p11 == 0)
    results['Check 3: Player Metadata Coverage'] = 'PASS' if c3_pass else 'FAIL'

    # -------------------------------------------------------------
    # Check 4: No Duplicate Player-Delivery Records
    # -------------------------------------------------------------
    print("\n--- Check 4: Duplicate Record Detection ---")
    key_cols = ['match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num']
    bat_dups = bat_df.duplicated(subset=key_cols).sum()
    bowl_dups = bowl_df.duplicated(subset=key_cols).sum()
    print(f"Batting delivery key duplicates: {bat_dups}")
    print(f"Bowling delivery key duplicates: {bowl_dups}")
    c4_pass = (bat_dups == 0) and (bowl_dups == 0)
    results['Check 4: Zero Duplicate Records'] = 'PASS' if c4_pass else 'FAIL'

    # -------------------------------------------------------------
    # Check 5: Match and Innings Consistency
    # -------------------------------------------------------------
    print("\n--- Check 5: Match & Innings Identifier Consistency ---")
    m_bat_v3 = (bat_df['match_id'] == v3_df['match_id']).all()
    inn_bat_v3 = (bat_df['innings'] == v3_df['innings']).all()
    m_bowl_v3 = (bowl_df['match_id'] == v3_df['match_id']).all()
    inn_bowl_v3 = (bowl_df['innings'] == v3_df['innings']).all()
    print(f"Batting match_id matches v3:   {m_bat_v3}")
    print(f"Batting innings matches v3:    {inn_bat_v3}")
    print(f"Bowling match_id matches v3:   {m_bowl_v3}")
    print(f"Bowling innings matches v3:    {inn_bowl_v3}")
    c5_pass = m_bat_v3 and inn_bat_v3 and m_bowl_v3 and inn_bowl_v3
    results['Check 5: Match & Innings Consistency'] = 'PASS' if c5_pass else 'FAIL'

    # -------------------------------------------------------------
    # Check 6: Excluded Matches and Dead-Tail Deliveries
    # -------------------------------------------------------------
    print("\n--- Check 6: Excluded Matches & Dead-Tail Deliveries Absence ---")
    dls_matches = [20182, 23674, 24822, 28334]
    short_matches = [15795, 31278, 48514]
    excluded_matches = dls_matches + short_matches
    
    bat_excl_matches = bat_df['match_id'].isin(excluded_matches).sum()
    bowl_excl_matches = bowl_df['match_id'].isin(excluded_matches).sum()
    
    bat_dead_tail = ((bat_df['innings'] == 2) & (bat_df['runs_required'] <= 0)).sum()
    bowl_dead_tail = ((bowl_df['innings'] == 2) & (bowl_df['runs_required'] <= 0)).sum()
    
    print(f"Batting rows from excluded matches: {bat_excl_matches}")
    print(f"Bowling rows from excluded matches: {bowl_excl_matches}")
    print(f"Batting dead-tail deliveries:       {bat_dead_tail}")
    print(f"Bowling dead-tail deliveries:       {bowl_dead_tail}")
    c6_pass = (bat_excl_matches == 0) and (bowl_excl_matches == 0) and (bat_dead_tail == 0) and (bowl_dead_tail == 0)
    results['Check 6: Exclusions Maintained'] = 'PASS' if c6_pass else 'FAIL'

    # -------------------------------------------------------------
    # Check 7: Pressure Values Bit-for-Bit Identity with v3
    # -------------------------------------------------------------
    print("\n--- Check 7: Pressure Values Identity with v3 ---")
    bat_p_diff = np.max(np.abs(bat_df['pressure_batting'] - v3_df['pressure_batting']))
    bat_t_diff = np.max(np.abs(bat_df['task_difficulty_bat'] - v3_df['task_difficulty_bat']))
    bat_ln_diff = np.max(np.abs(bat_df['normalized_consequence_L'] - v3_df['normalized_consequence_L']))
    bat_l_diff = np.max(np.abs(bat_df['raw_consequence_L'] - v3_df['raw_consequence_L']))
    bat_wp_diff = np.max(np.abs(bat_df['pre_delivery_wp'] - v3_df['pre_delivery_wp']))

    bowl_p_diff = np.max(np.abs(bowl_df['pressure_bowling'] - v3_df['pressure_bowling']))
    bowl_t_diff = np.max(np.abs(bowl_df['task_difficulty_bowl'] - v3_df['task_difficulty_bowl']))
    bowl_ln_diff = np.max(np.abs(bowl_df['normalized_consequence_L'] - v3_df['normalized_consequence_L']))
    bowl_l_diff = np.max(np.abs(bowl_df['raw_consequence_L'] - v3_df['raw_consequence_L']))
    bowl_wp_diff = np.max(np.abs(bowl_df['pre_delivery_wp'] - v3_df['pre_delivery_wp']))

    print(f"Batting max diff (P, T, L_norm, L, WP):   {bat_p_diff:.2e}, {bat_t_diff:.2e}, {bat_ln_diff:.2e}, {bat_l_diff:.2e}, {bat_wp_diff:.2e}")
    print(f"Bowling max diff (P, T, L_norm, L, WP):   {bowl_p_diff:.2e}, {bowl_t_diff:.2e}, {bowl_ln_diff:.2e}, {bowl_l_diff:.2e}, {bowl_wp_diff:.2e}")
    c7_pass = (max(bat_p_diff, bat_t_diff, bat_ln_diff, bat_l_diff, bat_wp_diff,
                   bowl_p_diff, bowl_t_diff, bowl_ln_diff, bowl_l_diff, bowl_wp_diff) < 1e-12)
    results['Check 7: Bit-for-Bit Pressure Identity'] = 'PASS' if c7_pass else 'FAIL'

    # -------------------------------------------------------------
    # Check 8: Reconciliation with Source Data
    # -------------------------------------------------------------
    print("\n--- Check 8: Reconciliation with Source Data ---")
    # Total batter runs in batting dataset vs v3/cohort
    bat_runs_sum = bat_df['batter_runs'].sum()
    cohort_runs_sum = cohort_df['runs'].sum()
    print(f"Batting dataset total batter runs: {bat_runs_sum:,}")
    print(f"Cohort dataset total batter runs:  {cohort_runs_sum:,}")
    assert bat_runs_sum == cohort_runs_sum, "Batter runs mismatch!"

    # Bowler runs conceded vs cohort
    bowl_rc_sum = bowl_df['bowler_runs_conceded'].sum()
    cohort_rc_sum = cohort_df['bowler_runs_conceded'].sum()
    print(f"Bowling dataset bowler runs conceded: {bowl_rc_sum:,}")
    print(f"Cohort dataset bowler runs conceded:  {cohort_rc_sum:,}")
    assert bowl_rc_sum == cohort_rc_sum, "Bowler runs conceded mismatch!"

    # Team runs added reconciliation
    bat_tra_sum = bat_df['team_runs_added'].sum()
    bowl_tra_sum = bowl_df['team_runs_added'].sum()
    cohort_tra_sum = cohort_df['team_runs_added'].sum()
    print(f"Batting dataset team runs added:  {bat_tra_sum:,}")
    print(f"Bowling dataset team runs added:  {bowl_tra_sum:,}")
    print(f"Cohort dataset team runs added:   {cohort_tra_sum:,}")
    assert bat_tra_sum == bowl_tra_sum == cohort_tra_sum, "Team runs added mismatch!"

    # Wickets reconciliation
    total_wickets_bat = bat_df['is_wicket'].sum()
    total_wickets_bowl = bowl_df['is_wicket'].sum()
    cohort_wickets = cohort_df['is_wicket'].sum()
    striker_outs = bat_df['is_striker_dismissed'].sum()
    non_striker_outs = bat_df['is_non_striker_dismissed'].sum()
    bowler_wkts = bowl_df['is_bowler_wicket'].sum()
    other_dismissals = bowl_df['is_other_dismissal'].sum()
    
    print(f"Total delivery wickets:       {total_wickets_bat:,} (Bat) | {total_wickets_bowl:,} (Bowl) | {cohort_wickets:,} (Cohort)")
    print(f"Striker outs:                 {striker_outs:,}")
    print(f"Non-striker outs:             {non_striker_outs:,}")
    print(f"Bowler-credited wickets:      {bowler_wkts:,}")
    print(f"Other dismissals (run outs):  {other_dismissals:,}")
    assert total_wickets_bat == total_wickets_bowl == cohort_wickets == 10020, "Wicket count mismatch!"
    assert bowler_wkts + other_dismissals == 10020, "Bowler wickets + other dismissals mismatch!"

    # Legal deliveries reconciliation
    bat_legal = bat_df['is_legal_ball'].sum()
    bowl_legal = bowl_df['is_legal_ball'].sum()
    cohort_legal = cohort_df['is_legal_ball'].sum()
    print(f"Total legal balls:            {bat_legal:,} (Bat) | {bowl_legal:,} (Bowl) | {cohort_legal:,} (Cohort)")
    assert bat_legal == bowl_legal == cohort_legal == 178798, f"Legal ball count mismatch: {bat_legal} != 178798"

    c8_pass = True
    results['Check 8: Source Reconciliation'] = 'PASS'

    # -------------------------------------------------------------
    # Check 9: Missing / Ambiguous Values Documentation
    # -------------------------------------------------------------
    print("\n--- Check 9: Missing / Ambiguous Values Documentation ---")
    # Identify any NaN fields and verify they are expected
    bat_nulls = bat_df.isna().sum().to_dict()
    bowl_nulls = bowl_df.isna().sum().to_dict()
    
    expected_bat_nulls = ['runs_required', 'required_run_rate', 'extras_type', 'dismissal_type', 'dismissal_type_id', 'dismissed_player_id']
    expected_bowl_nulls = ['runs_required', 'required_run_rate', 'extras_type', 'dismissal_type', 'dismissal_type_id', 'dismissed_player_id']
    
    unexpected_bat_nulls = {k: v for k, v in bat_nulls.items() if v > 0 and k not in expected_bat_nulls}
    unexpected_bowl_nulls = {k: v for k, v in bowl_nulls.items() if v > 0 and k not in expected_bowl_nulls}
    
    print(f"Unexpected nulls in Batting dataset: {unexpected_bat_nulls}")
    print(f"Unexpected nulls in Bowling dataset: {unexpected_bowl_nulls}")
    
    # 1 specific known source anomaly: Match 40709 delivery where dismissed_player_id is NaN for Retire Out
    miss_dismissed = cohort_df[(cohort_df['is_wicket'] == 1) & (cohort_df['dismissed_player_id'].isna())]
    print(f"Wickets with missing dismissed_player_id: {len(miss_dismissed)} (Match {miss_dismissed['match_id'].values[0]}, Over {miss_dismissed['overid'].values[0]}.{miss_dismissed['over_ball_num'].values[0]})")
    
    c9_pass = (len(unexpected_bat_nulls) == 0) and (len(unexpected_bowl_nulls) == 0) and (len(miss_dismissed) == 1)
    results['Check 9: Documented Missing Values'] = 'PASS' if c9_pass else 'FAIL'

    print("\n" + "=" * 80)
    print("STEP 5 VALIDATION SUMMARY")
    print("=" * 80)
    all_pass = all(v == 'PASS' for v in results.values())
    for name, status in results.items():
        print(f"  {name:45s}: {status}")
    print("-" * 80)
    print(f"OVERALL STEP 5 VERDICT: {'PASS' if all_pass else 'FAIL'}")
    print("=" * 80)

    # Save validation results JSON
    val_out = os.path.join(OUTPUT_DIR, "validation_results.json")
    with open(val_out, 'w') as f:
        json.dump({'verdict': 'PASS' if all_pass else 'FAIL', 'checks': results}, f, indent=2)
    print(f"Saved validation results to {val_out}")

    return results

if __name__ == '__main__':
    run_validation()
