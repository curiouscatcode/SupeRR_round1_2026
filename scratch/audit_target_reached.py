import pandas as pd

df = pd.read_csv('data/processed/delivery_pressure_index.csv')
matches = pd.read_csv('data/matches.csv')

inn2 = df[df['innings'] == 2]
neg_or_zero = inn2[inn2['runs_required'] <= 0]
match_ids = neg_or_zero['match_id'].unique()

print(f"Total affected matches: {len(match_ids)}")
print(f"Total deliveries with runs_required <= 0: {len(neg_or_zero)}")
print(f"Deliveries with runs_required == 0: {(neg_or_zero['runs_required'] == 0).sum()}")
print(f"Deliveries with runs_required < 0: {(neg_or_zero['runs_required'] < 0).sum()}")

print("\nDetailed breakdown of first 6 affected matches:")
cols = [
    'innings_ball_num', 'overid', 'over_ball_num', 'striker_name', 
    'score_before', 'runs_required', 'required_run_rate', 
    'balls_remaining', 'runs', 'extras_type', 'team_runs_added', 
    'Batting_PI', 'Bowling_PI'
]

for mid in match_ids[:6]:
    m_info = matches[matches['match_id'] == mid].iloc[0]
    m_delivs = inn2[inn2['match_id'] == mid]
    first_reached_idx = m_delivs[m_delivs['runs_required'] <= 0].index[0]
    pos = m_delivs.index.get_loc(first_reached_idx)
    start_pos = max(0, pos - 2)
    sample = m_delivs.iloc[start_pos:]
    
    print(f"\n==========================================")
    print(f"Match {mid} | Win: {m_info.get('win_type')} by {m_info.get('win_margin')} | Winner ID: {m_info.get('winner')}")
    print(f"Total deliveries in Inn 2: {len(m_delivs)} | Deliveries where runs_req <= 0: {len(m_delivs[m_delivs['runs_required'] <= 0])}")
    print(sample[cols].to_string(index=False))
