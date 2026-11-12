import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')
defending = [28962, 29926, 32135, 37895]
chasing = df[~df['match_id'].isin(defending)].copy()

# Search for conditions that produce exactly 34 matches
for c_neg in range(1, 6):
    for r_neg in range(0, 15):
        cond = (chasing['count_neg'] >= c_neg) & (chasing['runs_in_neg'] >= r_neg)
        if cond.sum() == 34:
            print(f"Condition: count_neg >= {c_neg} and runs_in_neg >= {r_neg} -> 34 matches!")
            
for c_neg in range(1, 6):
    for r_neg in range(0, 15):
        cond = (chasing['count_neg'] > c_neg) & (chasing['runs_in_neg'] >= r_neg)
        if cond.sum() == 34:
            print(f"Condition: count_neg > {c_neg} and runs_in_neg >= {r_neg} -> 34 matches!")

# What about excess_runs?
for er in range(1, 15):
    if (chasing['inn2_recon'] - chasing['target_recon'] >= er).sum() == 34:
        print(f"Condition: excess_runs >= {er} -> 34 matches!")

# What about count_neg >= 3 and ... ?
print("count_neg >= 3 count:", (chasing['count_neg'] >= 3).sum()) # 37
for r in range(1, 10):
    if ((chasing['count_neg'] >= 3) & (chasing['runs_in_neg'] >= r)).sum() == 34:
        print(f"Condition: count_neg >= 3 and runs_in_neg >= {r} -> 34 matches!")
