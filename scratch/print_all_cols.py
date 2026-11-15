import pandas as pd
bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
print("All batting columns:", bat_del.columns.tolist())
