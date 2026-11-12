import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')

# Exclude the 4 defending wins
defending_mids = [28962, 29926, 32135, 37895]
chasing_df = df[~df['match_id'].isin(defending_mids)].copy()
print(f"Total chasing matches: {len(chasing_df)}")

# Let's inspect different possible classification criteria that partition 86 into 52 and 34:
# Possibility 1: Matches where Innings 1 had byes/leg-byes vs not?
has_extras_inn1 = (chasing_df['inn1_lb'] + chasing_df['inn1_b'] > 0)
print(f"Chasing matches with byes/leg-byes in Inn 1: {has_extras_inn1.sum()} vs without: {(~has_extras_inn1).sum()}")

# Possibility 2: Matches where runs were actually scored during the negative deliveries (runs_in_neg > 0)
has_runs_in_neg = (chasing_df['runs_in_neg'] > 0)
print(f"Chasing matches with runs_in_neg > 0: {has_runs_in_neg.sum()} vs == 0: {(~has_runs_in_neg).sum()}")

# Possibility 3: Matches where negative deliveries occurred in the death overs (Overs 19 or 20) vs earlier
over_num = chasing_df['first_neg_over'].apply(lambda x: int(x.split('.')[0].replace('Over ', '')))
in_death = (over_num >= 19)
print(f"Chasing matches reaching target in death (>=19): {in_death.sum()} vs earlier: {(~in_death).sum()}")

# Possibility 4: Matches where Innings 2 reconstructed score exceeded target by > 0
# i.e., inn2_recon >= target_recon
diff = chasing_df['inn2_recon'] - chasing_df['target_recon']
print(f"Chasing matches where inn2_recon > target_recon: {(diff > 0).sum()}, == 0: {(diff == 0).sum()}")

# Possibility 5: What if count_neg == 1 vs count_neg > 1?
print(f"Chasing matches with count_neg > 1: {(chasing_df['count_neg'] > 1).sum()}, == 1: {(chasing_df['count_neg'] == 1).sum()}")
