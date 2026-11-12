import pandas as pd

m_df = pd.read_csv('data/matches.csv')
p_df = pd.read_csv('data/processed/delivery_pressure_index.csv')

valid_ids = set(p_df['match_id'].unique())
m_valid = m_df[m_df['match_id'].isin(valid_ids)].copy()

print(f"Total valid matches: {len(m_valid)}")

# Let's find:
# 1. Matches with tight finishes in Innings 2:
# E.g. runs_required reached 1 to 6 in the 20th over
p_inn2_do = p_df[(p_df['innings'] == 2) & (p_df['phase'] == 'Death')].copy()
final_balls = p_inn2_do.groupby('match_id').tail(1)
thrillers = final_balls[(final_balls['runs_required'] >= 0) & (final_balls['runs_required'] <= 6)]
print(f"Thrillers count: {len(thrillers)}")

sample_thrillers = m_valid[m_valid['match_id'].isin(thrillers['match_id'])].head(10)
print("\nSample Thrillers (Close Chases):")
for idx, r in sample_thrillers.iterrows():
    print(f"  ID: {r['match_id']} | Date: {r['match_date']} | {r['home_team']} vs {r['away_team']} | Result: {r['result']}")

# 2. One-sided chases (e.g. won in 12-16 overs with 8-10 wickets in hand):
easy_wins = final_balls[final_balls['over_number'] <= 16]
print("\nSample Comfortable Chases:")
sample_easy = m_valid[m_valid['match_id'].isin(easy_wins['match_id'])].head(5)
for idx, r in sample_easy.iterrows():
    print(f"  ID: {r['match_id']} | Date: {r['match_date']} | {r['home_team']} vs {r['away_team']} | Result: {r['result']}")
