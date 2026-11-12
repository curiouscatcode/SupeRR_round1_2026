import pandas as pd
import numpy as np

bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

K_bowl = 50.0
mu_econ = (bowler_df['high_runs_conceded'].sum() / bowler_df['high_legal_balls'].sum()) * 6.0  # 9.06
mu_wk_pct = (bowler_df['high_wickets'].sum() / bowler_df['high_legal_balls'].sum()) * 100.0   # 4.82%
mu_dot = (bowler_df['high_dot_balls'].sum() / bowler_df['high_legal_balls'].sum()) * 100.0   # 39.39%
mu_bnd = (bowler_df['high_boundaries_conceded'].sum() / bowler_df['high_legal_balls'].sum()) * 100.0 # 21.64%

# Filter qualified
bo = bowler_df[bowler_df['high_legal_balls'] >= 60].copy()

lambda_bo = bo['high_legal_balls'] / (bo['high_legal_balls'] + K_bowl)
bo['econ_bayes'] = lambda_bo * bo['high_economy_rate'] + (1.0 - lambda_bo) * mu_econ
bo['wk_pct_obs'] = (bo['high_wickets'] / bo['high_legal_balls']) * 100.0
bo['wk_pct_bayes'] = lambda_bo * bo['wk_pct_obs'] + (1.0 - lambda_bo) * mu_wk_pct
bo['dot_bayes'] = lambda_bo * bo['high_dot_pct'] + (1.0 - lambda_bo) * mu_dot
bo['bnd_bayes'] = lambda_bo * bo['high_boundary_pct'] + (1.0 - lambda_bo) * mu_bnd

# Low/mod baseline shrinkage
lambda_bo_low = bo['low_mod_legal_balls'] / (bo['low_mod_legal_balls'] + K_bowl)
mu_econ_low = (bowler_df['low_mod_runs_conceded'].sum() / bowler_df['low_mod_legal_balls'].sum()) * 6.0
bo['econ_low_bayes'] = lambda_bo_low * bo['low_mod_economy_rate'] + (1.0 - lambda_bo_low) * mu_econ_low
bo['diff_econ_bayes'] = bo['econ_bayes'] - bo['econ_low_bayes']

print("Qualified Bowlers (N >= 60 legal balls):", len(bo))
print("\nTop 10 Bowlers by Bayesian Economy Rate under Pressure (lowest):")
print(bo[['player_name', 'high_legal_balls', 'high_economy_rate', 'econ_bayes', 'wk_pct_bayes', 'dot_bayes', 'diff_econ_bayes']].sort_values('econ_bayes').head(10).to_string(index=False))

print("\nTop 10 Bowlers by Bayesian Wicket % under Pressure (highest):")
print(bo[['player_name', 'high_legal_balls', 'high_wickets', 'wk_pct_obs', 'wk_pct_bayes', 'econ_bayes']].sort_values('wk_pct_bayes', ascending=False).head(10).to_string(index=False))
