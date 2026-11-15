import pandas as pd
import numpy as np

# Load datasets
dms = pd.read_csv('data/processed/delivery_match_state.csv')
bbb = pd.read_csv('data/ball_by_ball.csv', low_memory=False)
matches = pd.read_csv('data/matches.csv')

print("=== RAW DATASET COUNTS ===")
print(f"delivery_match_state.csv rows: {len(dms)}, unique match_ids: {dms['match_id'].nunique()}")
print(f"ball_by_ball.csv rows:         {len(bbb)}, unique match_ids: {bbb['match_id'].nunique()}")
print(f"matches.csv rows:              {len(matches)}, unique match_ids: {matches['match_id'].nunique()}")

# Matches in dms vs bbb vs matches
dms_mids = set(dms['match_id'].unique())
bbb_mids = set(bbb['match_id'].unique())
matches_mids = set(matches['match_id'].unique())
print(f"Match IDs in dms: {len(dms_mids)}")
print(f"Match IDs in bbb: {len(bbb_mids)}")
print(f"Match IDs in matches: {len(matches_mids)}")

# Check target matches
dls_matches = [20182, 23674, 24822, 28334]
shortened_matches = [15795, 31278, 48514]

print("\n=== MATCH LEVEL COUNTS IN DMS VS BBB ===")
print("DLS Matches:")
for m in dls_matches:
    c_dms = len(dms[dms['match_id'] == m])
    c_bbb = len(bbb[bbb['match_id'] == m])
    print(f"  Match {m}: dms={c_dms}, bbb={c_bbb}")

print("Shortened Matches:")
for m in shortened_matches:
    c_dms = len(dms[dms['match_id'] == m])
    c_bbb = len(bbb[bbb['match_id'] == m])
    print(f"  Match {m}: dms={c_dms}, bbb={c_bbb}")

# Check where 183, 204, 255 could have come from:
# Let's check legal balls or total balls or something else
print("\n=== INVESTIGATING WHERE 183, 204, 255 CAME FROM ===")
for m in shortened_matches:
    sub_dms = dms[dms['match_id'] == m]
    sub_bbb = bbb[bbb['match_id'] == m]
    print(f"Match {m}:")
    print(f"  dms total rows: {len(sub_dms)}")
    print(f"  dms legal balls: {sub_dms['is_legal_ball'].sum()}")
    print(f"  bbb total rows: {len(sub_bbb)}")

# Check dead tail deliveries in dms
dead_tail = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
print(f"\nDead tail deliveries in dms: {dead_tail.sum()} across {dms.loc[dead_tail, 'match_id'].nunique()} matches")

# Check overlap of dead tail with the 7 excluded matches
print(f"Dead tail in DLS matches: {dms.loc[dead_tail & dms['match_id'].isin(dls_matches), 'match_id'].value_counts().to_dict()}")
print(f"Dead tail in Shortened matches: {dms.loc[dead_tail & dms['match_id'].isin(shortened_matches), 'match_id'].value_counts().to_dict()}")

# Now calculate the exact combinations of exclusions:
# Method A: Strictly on dms
# 1. Total rows: 188330
# 2. Exclude dead tail: -233 -> 188097
# 3. Exclude 4 DLS matches:
dls_rows_in_clean = len(dms[~dead_tail & dms['match_id'].isin(dls_matches)])
print(f"\nDLS rows after dead tail: {dls_rows_in_clean}")
# 4. Exclude 3 Shortened matches:
short_rows_in_clean = len(dms[~dead_tail & ~dms['match_id'].isin(dls_matches) & dms['match_id'].isin(shortened_matches)])
print(f"Shortened rows after dead tail and DLS: {short_rows_in_clean}")

cohort_dms = dms[~dead_tail & ~dms['match_id'].isin(dls_matches) & ~dms['match_id'].isin(shortened_matches)]
print(f"Final cohort size: {len(cohort_dms)} deliveries across {cohort_dms['match_id'].nunique()} matches")
