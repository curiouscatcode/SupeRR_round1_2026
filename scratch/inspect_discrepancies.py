import pandas as pd

matches = pd.read_csv('data/matches.csv')
dms = pd.read_csv('data/processed/delivery_match_state.csv')

inn2_last = dms[dms['innings'] == 2].groupby('match_id').last().reset_index()
inn2_last['final_score_inn2'] = inn2_last['score_before'] + inn2_last['team_runs_added']

inn1_last = dms[dms['innings'] == 1].groupby('match_id').last().reset_index()
inn1_last['final_score_inn1'] = inn1_last['score_before'] + inn1_last['team_runs_added']

check_df = inn2_last.merge(inn1_last[['match_id', 'final_score_inn1']], on='match_id')
check_df = check_df.merge(matches[['match_id', 'win_team_id', 'result', 'home_team_id', 'away_team_id']], on='match_id')

# Note: inn2_last['batting_team_id'] is the team batting in innings 2.
# inn2_last['bowling_team_id'] is the team batting in innings 1.
check_df['inn1_batting_team_id'] = inn2_last['bowling_team_id']
check_df['inn2_batting_team_id'] = inn2_last['batting_team_id']

check_df['inn2_scored_more'] = check_df['final_score_inn2'] > check_df['final_score_inn1']
check_df['inn1_scored_more'] = check_df['final_score_inn1'] > check_df['final_score_inn2']
check_df['scores_equal'] = check_df['final_score_inn1'] == check_df['final_score_inn2']

print(f"Inn 2 scored more: {check_df['inn2_scored_more'].sum()}")
print(f"Inn 1 scored more: {check_df['inn1_scored_more'].sum()}")
print(f"Scores equal: {check_df['scores_equal'].sum()}")

# Check if win_team_id matches the team that scored more
inn2_wins = check_df[check_df['win_team_id'] == check_df['inn2_batting_team_id']]
inn1_wins = check_df[check_df['win_team_id'] == check_df['inn1_batting_team_id']]
print(f"Matches where Innings 2 batting team officially won: {len(inn2_wins)}")
print(f"Matches where Innings 1 batting team officially won: {len(inn1_wins)}")

# Check discrepancies
discrepancies = check_df[
    ((check_df['inn2_scored_more']) & (check_df['win_team_id'] != check_df['inn2_batting_team_id'])) |
    ((check_df['inn1_scored_more']) & (check_df['win_team_id'] != check_df['inn1_batting_team_id']))
]
print(f"Total winner vs score discrepancies: {len(discrepancies)}")
print("Sample discrepancies:")
print(discrepancies[['match_id', 'final_score_inn1', 'final_score_inn2', 'result', 'win_team_id', 'inn1_batting_team_id', 'inn2_batting_team_id']].head(10))
