import pandas as pd

matches = pd.read_csv('data/matches.csv')
competitions = pd.read_csv('data/competitions.csv')

# Merge match metadata with competition info
match_meta = matches.merge(competitions, on='comp_id', how='left')

# Load our player level deliveries to see what match_ids are actually in our dataset
bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
active_match_ids = set(bat_del['match_id'].unique())

print(f"Total matches in dataset: {len(active_match_ids)}")

active_meta = match_meta[match_meta['match_id'].isin(active_match_ids)]
print(f"Matched active matches in metadata: {len(active_meta)}")

# Breakdown of active matches by competition
print("\n=== Active Competitions in Dataset ===")
comp_counts = active_meta.groupby(['comp_id', 'comp_name', 'season', 'match_format']).agg(
    matches=('match_id', 'count')
).reset_index().sort_values(by='season')

print(comp_counts[comp_counts['comp_name'].str.contains('IPL', case=False, na=False)])

print("\n=== All Stages in Matches Data for IPL ===")
ipl_matches = match_meta[match_meta['comp_name'].str.contains('IPL', case=False, na=False)]
print(ipl_matches['stage'].value_counts(dropna=False))

print("\n=== All Stages in ACTIVE Matches for IPL ===")
active_ipl = active_meta[active_meta['comp_name'].str.contains('IPL', case=False, na=False)]
print(active_ipl['stage'].value_counts(dropna=False))

print("\n=== Check knock_out column in IPL ===")
print(active_ipl['knock_out'].value_counts(dropna=False))

print("\n=== Active IPL Knockout Matches Details ===")
ko_candidates = active_ipl[(active_ipl['knock_out'] == 1) | (active_ipl['stage'] != 'League')]
print(ko_candidates[['match_id', 'comp_id', 'comp_name', 'season', 'match_number', 'match_date', 'stage', 'knock_out', 'home_team', 'away_team', 'result']])
