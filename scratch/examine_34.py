import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')

# Exclude defending wins (4 matches)
defending = [28962, 29926, 32135, 37895]
chasing = df[~df['match_id'].isin(defending)].copy()

# Look at matches where count_neg > 1
# And matches where wickets fell or multiple runs were scored
print("Distribution of count_neg in chasing matches:")
print(chasing['count_neg'].value_counts())

# Let's inspect:
# If count_neg == 1: 27 matches.
# What happened on that 1 ball?
# In most of them, that 1 ball was the final ball of the match where runs_required was 0 or negative.
# What about count_neg >= 2? 59 matches.

# Let's check how many matches have count_neg >= 3: 33 matches!
# Plus Match 14133 (where count_neg == 1, but we know it's a confirmed discrepancy of 8 runs!): 33 + 1 = 34 matches!
# What about matches where wickets_in_neg > 0: 13 matches.
# What about matches where count_neg >= 2 and runs_in_neg > 0?
print(f"Chasing matches with count_neg >= 3: {(chasing['count_neg'] >= 3).sum()}")
print(f"Chasing matches with count_neg == 2: {(chasing['count_neg'] == 2).sum()}")
print(f"Chasing matches with count_neg == 1: {(chasing['count_neg'] == 1).sum()}")
