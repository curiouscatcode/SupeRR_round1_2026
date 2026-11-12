import pandas as pd
import numpy as np

batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

# Test shrinkage for batters
pop_sr = (batter_df['high_runs'].sum() / batter_df['high_balls_faced'].sum()) * 100
pop_out_pct = (batter_df['high_dismissals'].sum() / batter_df['high_balls_faced'].sum()) * 100
pop_bnd_pct = (batter_df['high_boundaries'].sum() / batter_df['high_balls_faced'].sum()) * 100
pop_dot_pct = (batter_df['high_dot_balls'].sum() / batter_df['high_balls_faced'].sum()) * 100

print(f"Batter High-Pressure Priors:")
print(f"  SR: {pop_sr:.2f}")
print(f"  Out%: {pop_out_pct:.2f}%")
print(f"  Bnd%: {pop_bnd_pct:.2f}%")
print(f"  Dot%: {pop_dot_pct:.2f}%")

# Bowler priors
pop_econ = (bowler_df['high_runs_conceded'].sum() / bowler_df['high_legal_balls'].sum()) * 6
pop_wk_pct = (bowler_df['high_wickets'].sum() / bowler_df['high_legal_balls'].sum()) * 100
pop_bowl_bnd_pct = (bowler_df['high_boundaries_conceded'].sum() / bowler_df['high_legal_balls'].sum()) * 100
pop_bowl_dot_pct = (bowler_df['high_dot_balls'].sum() / bowler_df['high_legal_balls'].sum()) * 100

print(f"\nBowler High-Pressure Priors:")
print(f"  Economy: {pop_econ:.2f}")
print(f"  Wicket%: {pop_wk_pct:.2f}%")
print(f"  Bnd Conceded%: {pop_bowl_bnd_pct:.2f}%")
print(f"  Dot%: {pop_bowl_dot_pct:.2f}%")
