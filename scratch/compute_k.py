import pandas as pd
import numpy as np

batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

# Qualified batters
b = batter_df[batter_df['high_balls_faced'] >= 40].copy()
mu_sr = (batter_df['high_runs'].sum() / batter_df['high_balls_faced'].sum()) * 100

# Sample variance of strike rates
var_total_sr = b['high_strike_rate'].var()
# Approximate binomial/multinomial within variance for 40-80 balls
# On average, runs per ball ~ 1.14, variance of runs per ball ~ 2.4
# var(SR) for N balls = 10000 * var(runs_per_ball) / N
mean_N_b = b['high_balls_faced'].mean()
var_within_sr = 10000 * 2.35 / mean_N_b
var_between_sr = max(1.0, var_total_sr - var_within_sr)
K_sr = var_within_sr / var_between_sr * mean_N_b

print(f"Batter SR: Total Var={var_total_sr:.1f}, Within Var={var_within_sr:.1f}, Between Var={var_between_sr:.1f}")
print(f"Suggested theoretical K for Batter SR: {K_sr:.1f}")

# Bowlers
bo = bowler_df[bowler_df['high_legal_balls'] >= 40].copy()
mu_econ = (bowler_df['high_runs_conceded'].sum() / bowler_df['high_legal_balls'].sum()) * 6
var_total_econ = bo['high_economy_rate'].var()
mean_N_bo = bo['high_legal_balls'].mean()
# variance of runs per ball ~ 2.5
# var(econ) for N balls = 36 * var(runs_per_ball) / N
var_within_econ = 36 * 2.5 / mean_N_bo
var_between_econ = max(0.1, var_total_econ - var_within_econ)
K_econ = var_within_econ / var_between_econ * mean_N_bo

print(f"\nBowler Econ: Total Var={var_total_econ:.2f}, Within Var={var_within_econ:.2f}, Between Var={var_between_econ:.2f}")
print(f"Suggested theoretical K for Bowler Econ: {K_econ:.1f}")
