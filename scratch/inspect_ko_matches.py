import pandas as pd

matches = pd.read_csv('data/matches.csv')
competitions = pd.read_csv('data/competitions.csv')
match_meta = matches.merge(competitions, on='comp_id', how='left')

active_ipl = match_meta[match_meta['comp_name'].str.contains('IPL', case=False, na=False)]
ko_candidates = active_ipl[(active_ipl['knock_out'] == 1) | (active_ipl['stage'] != 'League')]

cols_to_show = ['match_id', 'comp_id', 'comp_name', 'season', 'match_number', 'match_date', 'stage', 'knock_out', 'home_team', 'away_team', 'win_team_id', 'result']
print(ko_candidates[cols_to_show].to_string())

# Also check all non-active IPL matches in matches.csv (e.g. why 20 in matches.csv, but 19 in active?)
non_active_ipl_ko = match_meta[(match_meta['comp_name'].str.contains('IPL', case=False, na=False)) & ((match_meta['knock_out'] == 1) | (match_meta['stage'] != 'League'))]
print("\n=== ALL IPL KO matches in metadata (total 20?) ===")
print(non_active_ipl_ko[cols_to_show].to_string())
