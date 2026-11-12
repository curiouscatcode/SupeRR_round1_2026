import pandas as pd

df = pd.read_csv('scratch/detailed_90_matches.csv')

# Let's inspect the match numbers and their characteristics
print(df[['match_id', 'result', 'first_neg_over', 'last_ball_over', 'count_neg', 'inn1_recon', 'inn2_recon', 'inn1_lb', 'inn1_b']].to_string())
