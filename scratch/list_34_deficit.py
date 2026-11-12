import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')
comps = pd.read_csv('data/competitions.csv')
m = df.merge(comps, on='comp_id')

defending = [28962, 29926, 32135, 37895]

# The 34 chasing deficit matches:
# We have the 33 chasing matches with count_neg >= 3 and runs_in_neg > 2, plus Match 14133!
c33 = (m['count_neg'] >= 3) & (m['runs_in_neg'] > 2) & (~m['match_id'].isin(defending))
m34 = m[c33 | (m['match_id'] == 14133)].copy().sort_values('match_id').reset_index(drop=True)

print(f"Total matches in m34: {len(m34)}")
print("34 Match IDs:")
print(m34['match_id'].tolist())

cols = ['match_id', 'match_date', 'comp_name', 'home_team', 'away_team', 'result', 'inn1_recon', 'inn2_recon', 'target_recon', 'count_neg', 'runs_in_neg', 'wickets_in_neg', 'inn1_lb', 'inn1_b']
print("\nTable of the 34 matches:")
print(m34[cols].to_string(index=False))

m34.to_csv('scratch/the_34_matches.csv', index=False)
