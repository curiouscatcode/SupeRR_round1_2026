import pandas as pd
import numpy as np

dms = pd.read_csv('data/processed/delivery_match_state.csv')

# Exclude dead-tail
tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
dms_clean = dms[~tail_mask].copy()

# Exclude 7 matches
dls_matches = [20182, 23674, 24822, 28334]
shortened_matches = [15795, 31278, 48514]
exclude_matches = set(dls_matches + shortened_matches)
cohort = dms_clean[~dms_clean['match_id'].isin(exclude_matches)].copy()

print(f"Cohort deliveries: {len(cohort)}, matches: {cohort['match_id'].nunique()}")
print(f"Innings 1 deliveries: {len(cohort[cohort['innings'] == 1])}")
print(f"Innings 2 deliveries: {len(cohort[cohort['innings'] == 2])}")
