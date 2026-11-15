import pandas as pd
bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
print("Batting columns:", bat_del.columns.tolist()[:20])
bowl_del = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')
print("Bowling columns:", bowl_del.columns.tolist()[:20])
