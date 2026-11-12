import pandas as pd
import numpy as np

batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

# Batter Priors
K_bat = 50.0
mu_sr = (batter_df['high_runs'].sum() / batter_df['high_balls_faced'].sum()) * 100.0  # 114.05
mu_out = (batter_df['high_dismissals'].sum() / batter_df['high_balls_faced'].sum()) * 100.0  # 7.09
mu_bnd = (batter_df['high_boundaries'].sum() / batter_df['high_balls_faced'].sum()) * 100.0  # 14.15
mu_dot = (batter_df['high_dot_balls'].sum() / batter_df['high_balls_faced'].sum()) * 100.0  # 44.84
mu_diff_sr = -18.39  # mean diff for qualified

# Filter qualified
b = batter_df[batter_df['high_balls_faced'] >= 60].copy()

# Bayesian adjustments
lambda_b = b['high_balls_faced'] / (b['high_balls_faced'] + K_bat)
b['sr_bayes'] = lambda_b * b['high_strike_rate'] + (1.0 - lambda_b) * mu_sr
b['out_bayes'] = lambda_b * b['high_dismissal_pct'] + (1.0 - lambda_b) * mu_out
b['bnd_bayes'] = lambda_b * b['high_boundary_pct'] + (1.0 - lambda_b) * mu_bnd
b['dot_bayes'] = lambda_b * b['high_dot_pct'] + (1.0 - lambda_b) * mu_dot

# Baseline low_mod SR shrinkage (with N_low_mod)
lambda_b_low = b['low_mod_balls_faced'] / (b['low_mod_balls_faced'] + K_bat)
mu_sr_low = (batter_df['low_mod_runs'].sum() / batter_df['low_mod_balls_faced'].sum()) * 100.0
b['sr_low_bayes'] = lambda_b_low * b['low_mod_strike_rate'] + (1.0 - lambda_b_low) * mu_sr_low
b['diff_sr_bayes'] = b['sr_bayes'] - b['sr_low_bayes']

print("Qualified Batters (N >= 60 balls faced):", len(b))
print("Top 10 Batters by Bayesian Strike Rate under Pressure:")
print(b[['player_name', 'high_balls_faced', 'high_strike_rate', 'sr_bayes', 'high_dismissal_pct', 'diff_sr_bayes']].sort_values('sr_bayes', ascending=False).head(10).to_string(index=False))
