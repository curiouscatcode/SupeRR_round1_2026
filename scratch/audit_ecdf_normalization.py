import sys
sys.path.append('.')
import numpy as np
import pandas as pd
from scratch.calculate_actual_L import calc_L_inn1, calc_L_inn2

# Load clean 782-match cohort
dms = pd.read_csv('data/processed/delivery_match_state.csv')
tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
dms_clean = dms[~tail_mask].copy()

dls_matches = [20182, 23674, 24822, 28334]
shortened_matches = [15795, 31278, 48514]
exclude_matches = set(dls_matches + shortened_matches)
cohort = dms_clean[~dms_clean['match_id'].isin(exclude_matches)].copy()

print("=== PART 2: ECDF NORMALIZATION AUDIT ===")
print(f"Total cohort deliveries: {len(cohort)}")
print(f"Innings 1 deliveries: {len(cohort[cohort['innings'] == 1])}")
print(f"Innings 2 deliveries: {len(cohort[cohort['innings'] == 2])}")

# Let's compute raw L for a large sample (10,000 per innings) or full cohort
# Let's take 10,000 per innings for high precision
np.random.seed(42)
s1 = cohort[cohort['innings'] == 1].sample(10000, random_state=42)
s2 = cohort[cohort['innings'] == 2].sample(10000, random_state=42)

l1_list = []
for _, r in s1.iterrows():
    _, l = calc_L_inn1(r['score_before'], r['legal_balls_before'], r['wickets_before'], 162.4, r['phase'])
    l1_list.append((r['phase'], r['overid'], l))

l2_list = []
for _, r in s2.iterrows():
    phase = r['phase']
    if str(phase) not in ['PP', 'Middle', 'Death']:
        phase = 'Middle'
    _, l = calc_L_inn2(r['runs_required'], r['balls_remaining'], r['wickets_before'], phase)
    l2_list.append((r['phase'], r['overid'], l))

df_l1 = pd.DataFrame(l1_list, columns=['phase', 'overid', 'raw_L'])
df_l2 = pd.DataFrame(l2_list, columns=['phase', 'overid', 'raw_L'])

# Check distribution across phases for Innings 1 and Innings 2 under ECDF
# ECDF percentile for each observation:
df_l1['ecdf_L'] = df_l1['raw_L'].rank(pct=True) * 100.0
df_l2['ecdf_L'] = df_l2['raw_L'].rank(pct=True) * 100.0

# Linear Min-Max for comparison:
p1_1, p995_1 = np.percentile(df_l1['raw_L'], 1), np.percentile(df_l1['raw_L'], 99.5)
p1_2, p995_2 = np.percentile(df_l2['raw_L'], 1), np.percentile(df_l2['raw_L'], 99.5)

df_l1['minmax_L'] = np.clip((df_l1['raw_L'] - p1_1) / (p995_1 - p1_1) * 100.0, 0, 100)
df_l2['minmax_L'] = np.clip((df_l2['raw_L'] - p1_2) / (p995_2 - p1_2) * 100.0, 0, 100)

print("\n--- INNINGS 1 PHASE COMPARISON: ECDF vs LINEAR MIN-MAX ---")
for ph in ['PP', 'Middle', 'Death']:
    sub = df_l1[df_l1['phase'] == ph]
    print(f"Phase {ph:7s} (N={len(sub)}): ECDF Mean={sub['ecdf_L'].mean():.1f}, Median={sub['ecdf_L'].median():.1f} | MinMax Mean={sub['minmax_L'].mean():.1f}, Median={sub['minmax_L'].median():.1f}")

print("\n--- INNINGS 2 PHASE COMPARISON: ECDF vs LINEAR MIN-MAX ---")
for ph in ['PP', 'Middle', 'Death']:
    sub = df_l2[df_l2['phase'] == ph]
    print(f"Phase {ph:7s} (N={len(sub)}): ECDF Mean={sub['ecdf_L'].mean():.1f}, Median={sub['ecdf_L'].median():.1f} | MinMax Mean={sub['minmax_L'].mean():.1f}, Median={sub['minmax_L'].median():.1f}")

# Check over-by-over median ECDF in Innings 2:
print("\n--- INNINGS 2 OVER-BY-OVER MEDIAN ECDF vs MINMAX ---")
for ov in [1, 5, 8, 12, 15, 17, 19, 20]:
    sub = df_l2[df_l2['overid'] == ov]
    print(f"Over {ov:2d}: ECDF Median = {sub['ecdf_L'].median():.1f} | MinMax Median = {sub['minmax_L'].median():.1f}")
