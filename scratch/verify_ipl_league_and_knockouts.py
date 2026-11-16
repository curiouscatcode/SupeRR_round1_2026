import pandas as pd
import numpy as np

matches = pd.read_csv('data/matches.csv')
competitions = pd.read_csv('data/competitions.csv')
match_meta = matches.merge(competitions, on='comp_id', how='left')

ipl_all = match_meta[match_meta['comp_name'].str.contains('IPL', case=False, na=False)].sort_values(by=['season', 'match_date', 'match_number'])

seasons = sorted(ipl_all['season'].unique())

for s in seasons:
    print(f"\n=======================================================")
    print(f"SEASON {s}")
    print(f"=======================================================")
    season_matches = ipl_all[ipl_all['season'] == s]
    league_matches = season_matches[season_matches['stage'] == 'League']
    ko_matches = season_matches[season_matches['stage'] != 'League']
    
    # Calculate points table
    points = {}
    for _, r in league_matches.iterrows():
        t1 = r['home_team']
        t2 = r['away_team']
        if t1 not in points: points[t1] = {'played': 0, 'won': 0, 'points': 0}
        if t2 not in points: points[t2] = {'played': 0, 'won': 0, 'points': 0}
        
        points[t1]['played'] += 1
        points[t2]['played'] += 1
        
        # Check result
        res = str(r['result'])
        win_id = r['win_team_id']
        if pd.notna(win_id):
            if r['home_team_id'] == win_id:
                points[t1]['won'] += 1
                points[t1]['points'] += 2
            elif r['away_team_id'] == win_id:
                points[t2]['won'] += 1
                points[t2]['points'] += 2
            else:
                # Tie/no result
                points[t1]['points'] += 1
                points[t2]['points'] += 1
        else:
            points[t1]['points'] += 1
            points[t2]['points'] += 1

    df_points = pd.DataFrame.from_dict(points, orient='index').sort_values(by=['points', 'won'], ascending=False)
    print("--- Top 5 League Standings (by Points & Wins) ---")
    print(df_points.head(5))
    
    print("\n--- Knockout Matches ---")
    for _, r in ko_matches.iterrows():
        print(f"Match ID: {r['match_id']} | Match #{r['match_number']} | Date: {r['match_date']} | Metadata Stage: {r['stage']} | {r['home_team']} vs {r['away_team']} | Result: {r['result']}")
