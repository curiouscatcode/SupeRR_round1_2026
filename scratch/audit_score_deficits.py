import pandas as pd

matches = pd.read_csv('data/matches.csv')
dms = pd.read_csv('data/processed/delivery_match_state.csv')

inn2_last = dms[dms['innings'] == 2].groupby('match_id').last().reset_index()
inn2_last['final_score_inn2'] = inn2_last['score_before'] + inn2_last['team_runs_added']
inn2_last['last_runs_req'] = inn2_last['runs_required'] - inn2_last['team_runs_added']

inn1_last = dms[dms['innings'] == 1].groupby('match_id').last().reset_index()
inn1_last['final_score_inn1'] = inn1_last['score_before'] + inn1_last['team_runs_added']

check_df = inn2_last.merge(inn1_last[['match_id', 'final_score_inn1']], on='match_id')
check_df = check_df.merge(matches[['match_id', 'win_team_id', 'result']], on='match_id')

check_df['inn1_batting_team_id'] = inn2_last['bowling_team_id']
check_df['inn2_batting_team_id'] = inn2_last['batting_team_id']

# Cases where inn2 team won officially, but their ball-by-ball score <= inn1 score:
inn2_won_official = check_df['win_team_id'] == check_df['inn2_batting_team_id']
inn2_score_deficit = check_df[inn2_won_official & (check_df['final_score_inn2'] <= check_df['final_score_inn1'])]

print(f"Matches where Innings 2 team won officially, but BBB score <= Innings 1 score: {len(inn2_score_deficit)}")
print(f"Deficit (inn1_score + 1 - inn2_score) distribution:")
inn2_score_deficit['runs_short'] = (inn2_score_deficit['final_score_inn1'] + 1) - inn2_score_deficit['final_score_inn2']
print(inn2_score_deficit['runs_short'].value_counts().sort_index())

print("\nSample matches where Inn 2 won officially but finished runs short in BBB:")
print(inn2_score_deficit[['match_id', 'final_score_inn1', 'final_score_inn2', 'runs_short', 'last_runs_req', 'result']].head(10))
