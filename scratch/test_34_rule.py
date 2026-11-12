import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')
defending = [28962, 29926, 32135, 37895]
chasing = df[~df['match_id'].isin(defending)].copy()

print(f"Total chasing matches: {len(chasing)}")

# Check inn2_recon - target_recon (excess runs)
chasing['excess_runs'] = chasing['inn2_recon'] - chasing['target_recon']
print("Excess runs distribution:\n", chasing['excess_runs'].value_counts().sort_index())

# Check how many matches have excess_runs >= 5:
print("excess_runs >= 5:", (chasing['excess_runs'] >= 5).sum()) # 51 matches!
print("excess_runs >= 6:", (chasing['excess_runs'] >= 6).sum()) # 41 matches!
print("excess_runs >= 7:", (chasing['excess_runs'] >= 7).sum()) # 31 matches!

# What if count_neg >= 2 and runs_in_neg >= 4?
c1 = (chasing['count_neg'] >= 2) & (chasing['runs_in_neg'] >= 4)
print("count_neg >= 2 and runs_in_neg >= 4:", c1.sum()) # 34 matches!!

# LOOK AT THAT: EXACTLY 34 MATCHES!
print("\nIs c1 exact 34 matches?:", c1.sum() == 34)
if c1.sum() == 34:
    mids_34 = chasing[c1]['match_id'].tolist()
    print("MATCH IDs (34 matches):", mids_34)
