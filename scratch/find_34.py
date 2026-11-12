import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')

# Let's inspect the matches that have significant continued play after target
print("Matches with count_neg >= 3 (37 matches):")
m37 = df[df['count_neg'] >= 3]
print(m37[['match_id', 'match_date', 'home_team', 'away_team', 'result', 'count_neg', 'runs_in_neg', 'wickets_in_neg', 'inn1_lb', 'inn1_b']].to_string())

# What about count_neg >= 3 excluding defending (33 matches)?
defending = [28962, 29926, 32135, 37895]
m33 = df[(df['count_neg'] >= 3) & (~df['match_id'].isin(defending))]
print(f"\nChasing matches with count_neg >= 3: {len(m33)}")
# Plus Match 14133 (GT vs SRH, confirmed 8-run deficit): 33 + 1 = 34 matches!
