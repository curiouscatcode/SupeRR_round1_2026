import pandas as pd

bat_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bowl_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bowl_del = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

# Check players of interest
names_to_check = [
    'Mahendra Singh Dhoni', 'David Warner', 'Ben Stokes', 'Kane Williamson',
    'Patrick Cummins', 'Faf du Plessis', 'Glenn Maxwell', 'Andre Russell',
    'Sunil Narine', 'Dinesh Karthik', 'Shikhar Dhawan', 'Jonny Bairstow',
    'Moeen Ali', 'Marcus Stoinis', 'Quinton de Kock', 'David Miller',
    'Nicholas Pooran', 'Shimron Hetmyer', 'Rinku Singh', 'Shivam Dube',
    'Yuzvendra Chahal', 'Harshal Patel', 'Anrich Nortje', 'Lockie Ferguson',
    'Adam Zampa', 'Tabraiz Shamsi', 'Ishant Sharma', 'Deepak Chahar',
    'Shardul Thakur', 'Washington Sundar'
]

print("=== ADDITIONAL PROMINENT PLAYERS STATUS ===")
for name in names_to_check:
    in_bat_elig = bat_elig[bat_elig['Player'] == name]
    in_bowl_elig = bowl_elig[bowl_elig['Player'] == name]
    
    bat_rank = in_bat_elig['Rank'].values[0] if len(in_bat_elig) > 0 else None
    bowl_rank = in_bowl_elig['Rank'].values[0] if len(in_bowl_elig) > 0 else None
    
    # Check raw if not eligible
    raw_bat_balls = len(bat_del[(bat_del['striker_name'] == name) & (bat_del['is_batter_ball_faced'] == 1)])
    raw_bat_p50 = len(bat_del[(bat_del['striker_name'] == name) & (bat_del['is_batter_ball_faced'] == 1) & (bat_del['pressure_batting'] >= 50)])
    
    raw_bowl_balls = len(bowl_del[(bowl_del['bowler_name'] == name) & (bowl_del['is_legal_ball'] == 1)])
    raw_bowl_p50 = len(bowl_del[(bowl_del['bowler_name'] == name) & (bowl_del['is_legal_ball'] == 1) & (bowl_del['pressure_bowling'] >= 50)])
    
    print(f"{name:25s} | Bat Rank: {str(bat_rank):4s} (P>=50: {raw_bat_p50}/{raw_bat_balls}) | Bowl Rank: {str(bowl_rank):4s} (P>=50: {raw_bowl_p50}/{raw_bowl_balls})")
