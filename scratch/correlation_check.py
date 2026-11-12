import pandas as pd
import numpy as np

batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

# Let's inspect qualified batters (>= 50 balls faced)
b50 = batter_df[batter_df['high_balls_faced'] >= 50].copy()
b50['clutch_sr_diff'] = b50['high_strike_rate'] - b50['low_mod_strike_rate']

bat_cols = ['high_strike_rate', 'high_boundary_pct', 'high_dot_pct', 'high_dismissal_pct', 'clutch_sr_diff']
print("BATTER METRIC CORRELATION MATRIX (N >= 50 HP balls, count = len(b50)):")
print(b50[bat_cols].corr().round(3))

# Bowlers (>= 50 legal balls)
bo50 = bowler_df[bowler_df['high_legal_balls'] >= 50].copy()
bo50['high_wicket_pct'] = (bo50['high_wickets'] / bo50['high_legal_balls']) * 100
bo50['clutch_econ_diff'] = bo50['high_economy_rate'] - bo50['low_mod_economy_rate']

bowl_cols = ['high_economy_rate', 'high_wicket_pct', 'high_dot_pct', 'high_boundary_pct', 'clutch_econ_diff']
print("\nBOWLER METRIC CORRELATION MATRIX (N >= 50 HP legal balls, count = len(bo50)):")
print(bo50[bowl_cols].corr().round(3))
