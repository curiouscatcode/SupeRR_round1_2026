import pandas as pd

bat_comp = pd.read_csv('experiments/ipl_knockout_bonus_v1/outputs/comparisons/batting_multipliers_comparison.csv')
bowl_comp = pd.read_csv('experiments/ipl_knockout_bonus_v1/outputs/comparisons/bowling_multipliers_comparison.csv')

print("=== BATTING TOP 12 COMPARISON ===")
cols_b = ['rank_base', 'rank_1_10', 'rank_1_20', 'rank_1_25', 'player_name', 'ko_matches', 'ko_balls_faced', 'shrunk_base', 'shrunk_1_20', 'delta_score_1_20']
print(bat_comp[cols_b].head(12).to_string(index=False))

print("\n=== BOWLING TOP 12 COMPARISON ===")
cols_bw = ['rank_base', 'rank_1_10', 'rank_1_20', 'rank_1_25', 'player_name', 'ko_matches', 'ko_legal_balls', 'shrunk_base', 'shrunk_1_20', 'delta_score_1_20']
print(bowl_comp[cols_bw].head(12).to_string(index=False))

print("\n=== BATTING TOP 10 MOVEMENT (1.20x) ===")
# Who entered top 10?
entered_bat = bat_comp[(bat_comp['rank_base'] > 10) & (bat_comp['rank_1_20'] <= 10)]
print("Entered Top 10 Batting:")
print(entered_bat[['player_name', 'rank_base', 'rank_1_20', 'ko_matches', 'ko_balls_faced', 'shrunk_base', 'shrunk_1_20']])

left_bat = bat_comp[(bat_comp['rank_base'] <= 10) & (bat_comp['rank_1_20'] > 10)]
print("\nLeft Top 10 Batting:")
print(left_bat[['player_name', 'rank_base', 'rank_1_20', 'ko_matches', 'ko_balls_faced', 'shrunk_base', 'shrunk_1_20']])

print("\n=== BOWLING TOP 10 MOVEMENT (1.20x) ===")
entered_bowl = bowl_comp[(bowl_comp['rank_base'] > 10) & (bowl_comp['rank_1_20'] <= 10)]
print("Entered Top 10 Bowling:", len(entered_bowl))
left_bowl = bowl_comp[(bowl_comp['rank_base'] <= 10) & (bowl_comp['rank_1_20'] > 10)]
print("Left Top 10 Bowling:", len(left_bowl))

print("\n=== LARGEST BATTING CLIMBERS (1.20x) ===")
print(bat_comp.sort_values(by='delta_rank_1_20', ascending=False)[['player_name', 'rank_base', 'rank_1_20', 'delta_rank_1_20', 'ko_matches', 'ko_balls_faced', 'shrunk_base', 'shrunk_1_20']].head(10).to_string(index=False))

print("\n=== LARGEST BATTING FALLERS (1.20x) ===")
print(bat_comp.sort_values(by='delta_rank_1_20', ascending=True)[['player_name', 'rank_base', 'rank_1_20', 'delta_rank_1_20', 'ko_matches', 'ko_balls_faced', 'shrunk_base', 'shrunk_1_20']].head(10).to_string(index=False))

print("\n=== LARGEST BOWLING CLIMBERS (1.20x) ===")
print(bowl_comp.sort_values(by='delta_rank_1_20', ascending=False)[['player_name', 'rank_base', 'rank_1_20', 'delta_rank_1_20', 'ko_matches', 'ko_legal_balls', 'shrunk_base', 'shrunk_1_20']].head(10).to_string(index=False))

print("\n=== LARGEST BOWLING FALLERS (1.20x) ===")
print(bowl_comp.sort_values(by='delta_rank_1_20', ascending=True)[['player_name', 'rank_base', 'rank_1_20', 'delta_rank_1_20', 'ko_matches', 'ko_legal_balls', 'shrunk_base', 'shrunk_1_20']].head(10).to_string(index=False))
