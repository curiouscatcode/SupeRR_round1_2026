import pandas as pd

dms = pd.read_csv('data/processed/delivery_match_state.csv')
m14097 = dms[dms['match_id'] == 14097]

inn1 = m14097[m14097['innings'] == 1]
inn2 = m14097[m14097['innings'] == 2]

print("Inn 1 total rows:", len(inn1))
last1 = inn1.iloc[-1]
score1 = last1['score_before'] + last1['team_runs_added']
print(f"Inn 1 score: {score1} ({last1['wickets_before'] + last1['is_wicket']} wkts in {last1['legal_balls_before'] + int(last1['is_legal_ball'])} balls)")

print("Inn 2 total rows:", len(inn2))
last2 = inn2.iloc[-1]
score2 = last2['score_before'] + last2['team_runs_added']
print(f"Inn 2 score: {score2} ({last2['wickets_before'] + last2['is_wicket']} wkts in {last2['legal_balls_before'] + int(last2['is_legal_ball'])} balls)")

first2 = inn2.iloc[0]
print(f"Inn 2 ball 1 runs_required: {first2['runs_required']}")
print("Inn 2 last 5 deliveries:")
print(inn2.tail(5)[['overid', 'over_ball_num', 'striker_name', 'score_before', 'runs_required', 'runs', 'team_runs_added']])
