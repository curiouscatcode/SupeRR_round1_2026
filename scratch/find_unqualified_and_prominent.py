import pandas as pd

bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bowl_del = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

bat_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bowl_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

# Batters
bat_faced = bat_del[bat_del['is_batter_ball_faced'] == 1]
bat_stats = bat_faced.groupby(['striker_id', 'striker_name']).agg(
    total_balls=('match_id', 'count'),
    pressure_balls=('pressure_batting', lambda s: (s >= 50).sum())
).reset_index()

bat_unqual = bat_stats[bat_stats['pressure_balls'] < 50].sort_values(by='total_balls', ascending=False)
print("=== Top Unqualified Batters by Total Balls Faced ===")
for _, r in bat_unqual.head(25).iterrows():
    print(f"ID: {r['striker_id']} | Name: {r['striker_name']} | Total Balls: {r['total_balls']} | Pressure Balls (P>=50): {r['pressure_balls']}")

# Bowlers
bowl_legal = bowl_del[bowl_del['is_legal_ball'] == 1]
bowl_stats = bowl_legal.groupby(['bowler_id', 'bowler_name']).agg(
    total_balls=('match_id', 'count'),
    pressure_balls=('pressure_bowling', lambda s: (s >= 50).sum())
).reset_index()

bowl_unqual = bowl_stats[bowl_stats['pressure_balls'] < 50].sort_values(by='total_balls', ascending=False)
print("\n=== Top Unqualified Bowlers by Total Legal Balls Bowled ===")
for _, r in bowl_unqual.head(25).iterrows():
    print(f"ID: {r['bowler_id']} | Name: {r['bowler_name']} | Total Balls: {r['total_balls']} | Pressure Balls (P>=50): {r['pressure_balls']}")
