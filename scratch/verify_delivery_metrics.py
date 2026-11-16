import pandas as pd

bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bowl_del = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

# 19 active knockout matches
ko_match_ids = [
    15187, 15188, 15189, 15190, # 2022
    21583, 21584, 21585,        # 2023 (21586 excluded upstream)
    31289, 31290, 31291, 31292, # 2024
    40764, 40765, 40766, 40767, # 2025
    50942, 50943, 50944, 50945  # 2026
]

print("=== Batting Deliveries in Knockouts ===")
bat_ko = bat_del[bat_del['match_id'].isin(ko_match_ids)]
print(f"Total batting delivery rows: {len(bat_ko)}")
bat_ko_faced = bat_ko[bat_ko['is_batter_ball_faced'] == 1]
print(f"Total balls faced by batters: {len(bat_ko_faced)}")
print(f"Batting pressure deliveries (P >= 50): {(bat_ko_faced['pressure_batting'] >= 50).sum()}")
print(f"Batting climax deliveries (P >= 75): {(bat_ko_faced['pressure_batting'] >= 75).sum()}")
print(f"Distinct batters in knockouts: {bat_ko_faced['striker_id'].nunique()}")

print("\n=== Bowling Deliveries in Knockouts ===")
bowl_ko = bowl_del[bowl_del['match_id'].isin(ko_match_ids)]
print(f"Total bowling delivery rows: {len(bowl_ko)}")
bowl_ko_legal = bowl_ko[bowl_ko['is_legal_ball'] == 1]
print(f"Total legal balls bowled: {len(bowl_ko_legal)}")
print(f"Bowling pressure deliveries (P >= 50): {(bowl_ko_legal['pressure_bowling'] >= 50).sum()}")
print(f"Bowling climax deliveries (P >= 75): {(bowl_ko_legal['pressure_bowling'] >= 75).sum()}")
print(f"Distinct bowlers in knockouts: {bowl_ko_legal['bowler_id'].nunique()}")

# Check player overlap with qualified players
bat_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bowl_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

# Load metadata audit for player_id mapping
meta_audit = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_1_independent_audit/metadata_audit.csv')
name_to_id = dict(zip(meta_audit['player_name'], meta_audit['player_id']))

elig_bat_ids = set([name_to_id[name] for name in bat_elig['Player'] if name in name_to_id])
elig_bowl_ids = set([name_to_id[name] for name in bowl_elig['Player'] if name in name_to_id])

batters_with_ko = set(bat_ko_faced['striker_id'].unique())
bowlers_with_ko = set(bowl_ko_legal['bowler_id'].unique())

print(f"\nQualified batters with knockout appearances: {len(batters_with_ko.intersection(elig_bat_ids))} of {len(elig_bat_ids)}")
print(f"Qualified bowlers with knockout appearances: {len(bowlers_with_ko.intersection(elig_bowl_ids))} of {len(elig_bowl_ids)}")

print(f"Qualified batters with ZERO knockout appearances: {len(elig_bat_ids - batters_with_ko)} of {len(elig_bat_ids)}")
print(f"Qualified bowlers with ZERO knockout appearances: {len(elig_bowl_ids - bowlers_with_ko)} of {len(elig_bowl_ids)}")
