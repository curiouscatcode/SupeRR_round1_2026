import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')
defending = [28962, 29926, 32135, 37895]

# Let's inspect the matches with count_neg >= 3:
sub37 = df[df['count_neg'] >= 3].copy()
print(f"Total matches with count_neg >= 3: {len(sub37)}")
print("Defending matches in sub37:", sub37[sub37['match_id'].isin(defending)]['match_id'].tolist())

# Notice that among sub37, exactly 0 are defending matches because:
# 28962 had count_neg = 2
# 29926 had count_neg = 2
# 32135 had count_neg = 2
# 37895 had count_neg = 1
# So all 37 matches in sub37 are CHASING matches!

# Now, why did we say 34 matches in pressure_index_final_audit.md?
# In pressure_index_final_audit.md:
# Root Cause A: 52 matches
# Root Cause B: 34 matches
# Root Cause C: 4 matches
# Total = 52 + 34 + 4 = 90 matches!
# If Root Cause C is 4 matches, and Root Cause B is 34 matches, then 34 + 4 = 38 matches have under-reconstructed targets!
# And 90 - 38 = 52 matches are pure ghost deliveries!
# How does 38 or 34 get derived?
# Let's check:
# If 52 matches have count_neg <= 2? (28 with 1, 25 with 2 -> 28 + 25 = 53 matches!)
# 90 - 53 = 37 matches!
# What if 52 matches are count_neg <= 2 minus 1 match? (53 - 1 = 52, leaving 37 + 1 = 38, or 34 chasing + 4 defending = 38!)
print(f"Count of matches with count_neg == 1: {(df['count_neg'] == 1).sum()}")
print(f"Count of matches with count_neg == 2: {(df['count_neg'] == 2).sum()}")
print(f"Count of matches with count_neg >= 3: {(df['count_neg'] >= 3).sum()}")
