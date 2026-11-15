"""
Step 2.1 - Issue 3: Investigation of Multi-Run Extras and Score Discrepancies
=============================================================================
Forensic investigation of the 104 matches where reconstructed second-innings
totals fall 1-4+ runs short of the chase target.
"""

import os
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_2_1_infrastructure_corrections"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=== ISSUE 3: MULTI-RUN EXTRAS AND SCORE DISCREPANCY INVESTIGATION ===")

# 1. Load data
bbb_path = "data/ball_by_ball.csv"
matches_path = "data/matches.csv"
comps_path = "data/competitions.csv"
dms_path = "data/processed/delivery_match_state.csv"

print("Loading datasets...")
bbb = pd.read_csv(bbb_path, low_memory=False)
matches = pd.read_csv(matches_path)
comps = pd.read_csv(comps_path)
dms = pd.read_csv(dms_path)

m_all = matches.merge(comps, on='comp_id', how='left')

# Exclude dead tail and 4 confirmed DLS matches from analysis
clean_cohort_mids = set(dms['match_id'].unique()) - {20182, 23674, 24822, 28334}

# 2. Inspect representations of extras in ball_by_ball.csv
print("\n--- Raw Data Extras Field Analysis in ball_by_ball.csv ---")
extras_summary = bbb[bbb['extras_type'].notna()].groupby(
    ['extras_type', 'extras1_runs', 'runs', 'extras_2_runs', 'is_four', 'is_six'],
    dropna=False
).size().reset_index(name='count')

print("All unique combinations of extras fields in raw ball_by_ball.csv:")
print(extras_summary.to_string(index=False))

# Check extras1_runs unique values across entire dataset
print("\nUnique values of extras1_runs by extras_type:")
print(bbb[['extras_type', 'extras1_runs']].drop_duplicates())

# 3. Can missing runs be recovered from any other column?
print("\n--- Investigating Potential Source Fields for Missing Runs ---")
other_cols = [c for c in bbb.columns if c not in ['match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num', 'batting_team_id', 'bowling_team_id', 'striker_id', 'striker_name', 'bowler_id', 'bowler_name', 'runs', 'extras_type', 'extras1_runs', 'extras_2_runs']]
print("Checking other available columns in ball_by_ball.csv:", other_cols)

# Check if stroke, bowl_speed, or delivery_style contain extra runs info
byes_legbyes = bbb[bbb['extras_type'].isin(['byes', 'legbyes'])]
print(f"Total byes/legbyes deliveries in raw data: {len(byes_legbyes):,}")
print("Sample of byes/legbyes rows across other fields:")
print(byes_legbyes[['extras_type', 'runs', 'extras1_runs', 'extras_2_runs', 'stroke', 'pace_or_spin']].head(10))

# 4. Detailed audit of the 104 affected matches
print("\n--- Auditing the 104 Matches Finishing Short in Ball-by-Ball ---")

# Reconstruct 2nd innings totals for clean cohort
inn2_deliv = dms[
    (dms['match_id'].isin(clean_cohort_mids)) &
    (dms['innings'] == 2) &
    (~((dms['innings'] == 2) & (dms['runs_required'] <= 0)))
]

inn2_last = inn2_deliv.groupby('match_id').last().reset_index()
inn2_last['score2_reconstructed'] = inn2_last['score_before'] + inn2_last['team_runs_added']
inn2_last['last_runs_req'] = inn2_last['runs_required'] - inn2_last['team_runs_added']
inn2_last['last_legal_balls'] = inn2_last['legal_balls_before'] + inn2_last['is_legal_ball'].astype(int)
inn2_last['last_wickets'] = inn2_last['wickets_before'] + inn2_last['is_wicket'].astype(int)

# Innings 1 totals
inn1_last = dms[
    (dms['match_id'].isin(clean_cohort_mids)) &
    (dms['innings'] == 1)
].groupby('match_id').last().reset_index()
inn1_last['score1_total'] = inn1_last['score_before'] + inn1_last['team_runs_added']

chase_audit = inn2_last.merge(inn1_last[['match_id', 'score1_total']], on='match_id')
chase_audit = chase_audit.merge(m_all[['match_id', 'comp_name', 'match_date', 'result', 'win_team_id']], on='match_id')

chase_audit['target'] = chase_audit['score1_total'] + 1
chase_audit['deficit'] = chase_audit['target'] - chase_audit['score2_reconstructed']
chase_audit['inn2_won_official'] = (chase_audit['win_team_id'] == chase_audit['batting_team_id'])

# Matches where inn2 team won officially but finished short of target in reconstructed score
deficit_matches = chase_audit[chase_audit['inn2_won_official'] & (chase_audit['deficit'] > 0)].copy()
deficit_matches = deficit_matches.sort_values(by='deficit', ascending=False).reset_index(drop=True)

print(f"Total chasing winner matches finishing short: {len(deficit_matches)}")
print("\nDistribution of deficit (runs short of target):")
print(deficit_matches['deficit'].value_counts().sort_index())

# Check how many of these matches also had premature innings (balls < 120 and wkts < 10)
deficit_matches['balls_rem_at_end'] = 120 - deficit_matches['last_legal_balls']
print(f"Mean balls remaining when match ended: {deficit_matches['balls_rem_at_end'].mean():.1f} balls")
print(f"Mean wickets remaining when match ended: {(10 - deficit_matches['last_wickets']).mean():.1f} wickets")

# Save detailed register of all deficit matches
export_cols = [
    'match_id', 'comp_name', 'match_date', 'result',
    'score1_total', 'target', 'score2_reconstructed', 'deficit',
    'last_legal_balls', 'balls_rem_at_end', 'last_wickets'
]
deficit_path = os.path.join(OUTPUT_DIR, "extras_deficit_104_matches.csv")
deficit_matches[export_cols].to_csv(deficit_path, index=False)
print(f"\nSaved deficit matches register to {deficit_path}")

# Print sample case studies
print("\n--- Detailed Case Studies of Deficit Matches ---")
sample_cases = [13511, 14094, 14097, 31273]
for mid in sample_cases:
    row = deficit_matches[deficit_matches['match_id'] == mid]
    if len(row) > 0:
        r = row.iloc[0]
        print(f"Match {mid} ({r['comp_name']}, {r['match_date']}):")
        print(f"  Result: '{r['result']}'")
        print(f"  Target: {r['target']} | Reconstructed Score: {r['score2_reconstructed']} (Deficit: {r['deficit']} runs)")
        print(f"  Final State: {10 - r['last_wickets']} wickets in hand, {r['balls_rem_at_end']} balls remaining")
