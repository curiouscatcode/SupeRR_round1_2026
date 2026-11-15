import pandas as pd

matches = pd.read_csv('data/matches.csv')
dms = pd.read_csv('data/processed/delivery_match_state.csv')

inn2_last = dms[dms['innings'] == 2].groupby('match_id').last().reset_index()
inn2_last['final_score_inn2'] = inn2_last['score_before'] + inn2_last['team_runs_added']

inn1_last = dms[dms['innings'] == 1].groupby('match_id').last().reset_index()
inn1_last['final_score_inn1'] = inn1_last['score_before'] + inn1_last['team_runs_added']

check_df = inn2_last.merge(inn1_last[['match_id', 'final_score_inn1']], on='match_id')
check_df = check_df.merge(matches[['match_id', 'win_team_id', 'result']], on='match_id')

check_df['inn2_won'] = check_df['final_score_inn2'] > check_df['final_score_inn1']
check_df['inn1_won'] = check_df['final_score_inn1'] > check_df['final_score_inn2']
check_df['tie'] = check_df['final_score_inn1'] == check_df['final_score_inn2']

print('Matches where Innings 2 scored more runs:', check_df['inn2_won'].sum())
print('Matches where Innings 1 scored more runs:', check_df['inn1_won'].sum())
print('Ties (regular 20 overs):', check_df['tie'].sum())

inn2_bat_team = check_df['batting_team_id']
inn1_bat_team = check_df['bowling_team_id']

mismatch_inn2 = check_df[check_df['inn2_won'] & (check_df['win_team_id'] != inn2_bat_team)]
print('Mismatches where inn2 scored more but win_team_id != inn2 batting team:', len(mismatch_inn2))

mismatch_inn1 = check_df[check_df['inn1_won'] & (check_df['win_team_id'] != inn1_bat_team)]
print('Mismatches where inn1 scored more but win_team_id != inn1 batting team:', len(mismatch_inn1))

ties = check_df[check_df['tie']]
print('Tied matches count:', len(ties))
for idx, r in ties.iterrows():
    print(f"Match {r['match_id']}: {r['result']} | Win team: {r['win_team_id']}")
