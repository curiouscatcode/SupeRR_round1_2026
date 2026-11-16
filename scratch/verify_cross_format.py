import pandas as pd
import numpy as np

# Load batting deliveries
df_bat = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')

# Separate IPL and T20I
# Delivery has format in match metadata or delivery level? Let's check columns
print("Batting delivery columns:", df_bat.columns.tolist()[:20])

# Let's inspect match metadata
meta = pd.read_csv('outputs/metadata_audit.csv')
print("Metadata columns:", meta.columns.tolist())
