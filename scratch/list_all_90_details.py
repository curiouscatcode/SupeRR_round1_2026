import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')
comps = pd.read_csv('data/competitions.csv')
m = df.merge(comps, on='comp_id')

print("All 90 matches with their competition and dates:")
cols = ['match_id', 'match_date', 'comp_name', 'home_team', 'away_team', 'result', 'inn1_recon', 'inn2_recon', 'count_neg', 'runs_in_neg', 'wickets_in_neg']
print(m[cols].to_string())
