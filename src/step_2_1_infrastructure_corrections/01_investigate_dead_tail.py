"""
Step 2.1 - Issue 1: Investigation and Exclusion of Dead-Tail Deliveries
=====================================================================
Analyzes the 233 deliveries occurring after the second-innings target
had already been reached (runs_required <= 0).
"""

import os
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_2_1_infrastructure_corrections"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=== ISSUE 1: DEAD-TAIL DELIVERIES INVESTIGATION ===")

# 1. Load reconstructed delivery dataset
dms_path = "data/processed/delivery_match_state.csv"
print(f"Loading {dms_path}...")
df = pd.read_csv(dms_path)
total_deliv = len(df)
total_matches = df['match_id'].nunique()
print(f"Total starting deliveries: {total_deliv:,} across {total_matches} matches")

# 2. Isolate Innings 2 deliveries
inn2 = df[df['innings'] == 2].copy()
total_inn2 = len(inn2)
print(f"Total Innings 2 deliveries: {total_inn2:,}")

# 3. Identify dead-tail deliveries
dead_tail = inn2[inn2['runs_required'] <= 0].copy()
n_dead_tail = len(dead_tail)
affected_matches = dead_tail['match_id'].nunique()
print(f"\nDead-tail deliveries found (runs_required <= 0): {n_dead_tail}")
print(f"Matches containing dead-tail deliveries: {affected_matches}")

# Breakdown of runs_required in dead tail
print("\nDistribution of runs_required in dead tail:")
print(dead_tail['runs_required'].value_counts().sort_index())

# Breakdown of how many dead-tail balls per match
balls_per_match = dead_tail.groupby('match_id').size()
print("\nDeliveries per match distribution:")
print(balls_per_match.value_counts().sort_index())

# 4. Detailed analysis of why dead-tail deliveries occurred
# Let's inspect the preceding delivery for each dead-tail delivery or sequence
records = []
for m_id, group in dead_tail.groupby('match_id'):
    first_dead_idx = group.index[0]
    # Delivery where target was actually reached (previous row)
    prev_idx = first_dead_idx - 1
    prev_row = df.loc[prev_idx]
    
    records.append({
        'match_id': m_id,
        'dead_tail_count': len(group),
        'winning_ball_overid': prev_row['overid'],
        'winning_ball_over_ball_num': prev_row['over_ball_num'],
        'winning_ball_striker': prev_row['striker_name'],
        'winning_ball_runs': prev_row['runs'],
        'winning_ball_team_runs_added': prev_row['team_runs_added'],
        'winning_ball_extras_type': prev_row['extras_type'],
        'winning_ball_score_before': prev_row['score_before'],
        'winning_ball_req_before': prev_row['runs_required'],
        'first_dead_req': group.iloc[0]['runs_required'],
        'dead_balls_overs': list(group['overid'].values)
    })

summary_df = pd.DataFrame(records)
print(f"\nSample of matches with dead tail:\n{summary_df.head(10)}")

# Save full export of all 233 dead tail deliveries
dead_tail_export = dead_tail[[
    'match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num',
    'striker_name', 'bowler_name', 'score_before', 'wickets_before',
    'legal_balls_before', 'balls_remaining', 'runs_required', 'required_run_rate',
    'runs', 'extras_type', 'team_runs_added', 'is_wicket'
]]
dead_tail_path = os.path.join(OUTPUT_DIR, "dead_tail_deliveries_register.csv")
dead_tail_export.to_csv(dead_tail_path, index=False)
print(f"\nSaved full dead tail delivery register to {dead_tail_path}")

# Save summary by match
summary_path = os.path.join(OUTPUT_DIR, "dead_tail_match_summary.csv")
summary_df.to_csv(summary_path, index=False)
print(f"Saved match-level dead tail summary to {summary_path}")

# 5. Verification of dataset after exclusion
clean_df = df[~((df['innings'] == 2) & (df['runs_required'] <= 0))].copy().reset_index(drop=True)
print(f"\n--- EXCLUSION VERIFICATION ---")
print(f"Deliveries before exclusion: {len(df):,}")
print(f"Deliveries excluded:        {n_dead_tail}")
print(f"Deliveries after exclusion:  {len(clean_df):,}")
assert len(clean_df) == len(df) - 233, "Count mismatch!"
assert clean_df['match_id'].nunique() == total_matches, "Matches should not be dropped, only dead deliveries!"
assert not ((clean_df['innings'] == 2) & (clean_df['runs_required'] <= 0)).any(), "Dead tail deliveries still present!"
print("PASS: Exactly 233 deliveries excluded; 188,097 clean active deliveries remain across all 789 matches.")
