import numpy as np
import pandas as pd

# 1. First let's check empirical wicket curve mu_W(L_t) and sigma_W(L_t)
dms = pd.read_csv('data/processed/delivery_match_state.csv')
tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
dms_clean = dms[~tail_mask].copy()

dls_matches = [20182, 23674, 24822, 28334]
shortened_matches = [15795, 31278, 48514]
exclude_matches = set(dls_matches + shortened_matches)
cohort = dms_clean[~dms_clean['match_id'].isin(exclude_matches)].copy()

# Group by legal_balls_before to see empirical mean and std of wickets_before
w_stats = cohort.groupby('legal_balls_before')['wickets_before'].agg(['mean', 'std']).reset_index()
print("Wicket stats sample at key points (0, 16, 48, 90, 96, 108, 114):")
for b in [0, 16, 42, 48, 90, 96, 108, 114]:
    row = w_stats[w_stats['legal_balls_before'] == b]
    if len(row) > 0:
        print(f"Ball {b:3d}: mean = {row['mean'].values[0]:.2f}, std = {row['std'].values[0]:.2f}")

# Now let's check the formula from Section 3.1:
# mu_W(L_t) = 10 * (1 - (1 - L_t/120)^0.65)
print("\nAnalytical formula mu_W(L_t) = 10 * (1 - (1 - L_t/120)^0.65):")
for b in [0, 16, 42, 48, 90, 96, 108, 114]:
    formula_mu = 10.0 * (1.0 - (1.0 - b/120.0)**0.65)
    print(f"Ball {b:3d}: formula_mu = {formula_mu:.2f}")
