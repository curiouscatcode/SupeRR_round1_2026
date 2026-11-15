"""
Step 4 - Module 1: Cohort Filter and State Invariant Enforcement
================================================================
Extracts and filters the certified pure 20-over cohort:
- Starting rows: 188,330 deliveries across 789 matches
- Excludes 233 dead-tail deliveries (runs_required <= 0 in Innings 2)
- Excludes 4 confirmed mid-match DLS matches (20182, 23674, 24822, 28334; 821 deliveries)
- Excludes 3 pre-match shortened matches (15795, 31278, 48514; 496 non-dead-tail deliveries)
- Final verified cohort: 186,780 deliveries across 782 matches (97,443 Inn 1; 89,337 Inn 2)
"""

import os
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_4_pressure_pipeline"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_filter_cohort():
    dms_path = "data/processed/delivery_match_state.csv"
    matches_path = "data/matches.csv"
    
    print("Loading delivery_match_state.csv and matches.csv...")
    dms = pd.read_csv(dms_path)
    matches = pd.read_csv(matches_path)
    
    start_rows = len(dms)
    start_matches = dms['match_id'].nunique()
    print(f"Starting raw data: {start_rows} deliveries across {start_matches} matches.")
    
    # 1. Exclusion: Dead-tail deliveries
    dead_tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
    dead_tail_count = dead_tail_mask.sum()
    dms_clean = dms[~dead_tail_mask].copy()
    print(f"[-] Excluded {dead_tail_count} dead-tail deliveries.")
    
    # 2. Exclusion: 4 confirmed DLS matches
    dls_matches = [20182, 23674, 24822, 28334]
    dls_mask = dms_clean['match_id'].isin(dls_matches)
    dls_count = dls_mask.sum()
    dms_clean = dms_clean[~dls_mask].copy()
    print(f"[-] Excluded {dls_count} deliveries from 4 DLS matches.")
    
    # 3. Exclusion: 3 pre-match shortened matches
    shortened_matches = [15795, 31278, 48514]
    short_mask = dms_clean['match_id'].isin(shortened_matches)
    short_count = short_mask.sum()
    dms_clean = dms_clean[~short_mask].copy()
    print(f"[-] Excluded {short_count} deliveries from 3 pre-match shortened matches.")
    
    # Verify exact cohort invariants
    final_rows = len(dms_clean)
    final_matches = dms_clean['match_id'].nunique()
    inn1_rows = len(dms_clean[dms_clean['innings'] == 1])
    inn2_rows = len(dms_clean[dms_clean['innings'] == 2])
    
    print("\n--- Cohort Reconciliation Check ---")
    print(f"Final deliveries: {final_rows} (Expected: 186,780)")
    print(f"Final matches:    {final_matches} (Expected: 782)")
    print(f"Innings 1 rows:   {inn1_rows} (Expected: 97,443)")
    print(f"Innings 2 rows:   {inn2_rows} (Expected: 89,337)")
    
    assert final_rows == 186780, f"Cohort delivery mismatch: {final_rows} != 186780"
    assert final_matches == 782, f"Cohort match mismatch: {final_matches} != 782"
    assert inn1_rows == 97443, f"Innings 1 row mismatch: {inn1_rows} != 97443"
    assert inn2_rows == 89337, f"Innings 2 row mismatch: {inn2_rows} != 89337"
    print(">>> All cohort boundary assertions PASSED successfully.")
    
    # Merge match-level metadata
    match_cols = ['match_id', 'venue_id', 'win_team_id', 'home_team_id', 'away_team_id', 'toss_win_team_id', 'toss_opted']
    dms_clean = dms_clean.merge(matches[match_cols], on='match_id', how='left')
    
    # Pre-delivery win target label
    dms_clean['bat_win'] = (dms_clean['batting_team_id'] == dms_clean['win_team_id']).astype(float)
    
    # Standardize phase strings to ('PP', 'Middle', 'Death')
    phase_mapping = {
        'PP': 'PP',
        'Powerplay': 'PP',
        'powerplay': 'PP',
        'Middle': 'Middle',
        'middle': 'Middle',
        'Death': 'Death',
        'death': 'Death'
    }
    dms_clean['phase'] = dms_clean['phase'].map(phase_mapping).fillna('Middle')
    
    # Standardize wicket convention
    # W_t is wickets lost before the delivery [0, 9]
    # W_rem is wickets in hand [1, 10]
    dms_clean['W_t'] = dms_clean['wickets_before'].astype(int)
    dms_clean['W_rem'] = 10 - dms_clean['W_t']
    
    out_parquet = os.path.join(OUTPUT_DIR, "clean_cohort_deliveries.parquet")
    dms_clean.to_parquet(out_parquet, index=False)
    print(f"Saved clean cohort dataset to {out_parquet}")
    return dms_clean

if __name__ == '__main__':
    load_and_filter_cohort()
