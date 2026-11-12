import pandas as pd
import numpy as np

batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

# Filter batters with at least some balls
print("=== BATTER ANALYSIS ===")
b_filt = batter_df[batter_df['high_balls_faced'] >= 40].copy()
print(f"Batters with >= 40 HP balls: {len(b_filt)}")

# Check correlations of key candidate metrics for batters
b_filt['clutch_sr_diff'] = b_filt['high_strike_rate'] - b_filt['low_mod_strike_rate']
b_filt['clutch_bnd_diff'] = b_filt['high_boundary_pct'] - b_filt['low_mod_boundary_pct']
b_filt['clutch_dot_diff'] = b_filt['high_dot_pct'] - b_filt['low_mod_dot_pct']
b_filt['clutch_out_diff'] = b_filt['high_dismissal_pct'] - b_filt['low_mod_dismissal_pct']

print("\nSummary stats for Batters (>= 40 HP balls):")
for col in ['high_strike_rate', 'high_boundary_pct', 'high_dot_pct', 'high_dismissal_pct', 'clutch_sr_diff']:
    s = b_filt[col]
    print(f"  {col:20s}: Mean={s.mean():6.2f}, Std={s.std():6.2f}, Median={s.median():6.2f}, Min={s.min():6.2f}, Max={s.max():6.2f}")

print("\n=== BOWLER ANALYSIS ===")
bo_filt = bowler_df[bowler_df['high_legal_balls'] >= 40].copy()
print(f"Bowlers with >= 40 HP legal balls: {len(bo_filt)}")

bo_filt['clutch_econ_diff'] = bo_filt['high_economy_rate'] - bo_filt['low_mod_economy_rate']
bo_filt['clutch_dot_diff'] = bo_filt['high_dot_pct'] - bo_filt['low_mod_dot_pct']
bo_filt['clutch_bnd_diff'] = bo_filt['high_boundary_pct'] - bo_filt['low_mod_boundary_pct']

print("\nSummary stats for Bowlers (>= 40 HP legal balls):")
for col in ['high_economy_rate', 'high_dot_pct', 'high_boundary_pct', 'high_strike_rate', 'clutch_econ_diff']:
    s = bo_filt[col]
    print(f"  {col:20s}: Mean={s.mean():6.2f}, Std={s.std():6.2f}, Median={s.median():6.2f}, Min={s.min():6.2f}, Max={s.max():6.2f}")

print("\n=== TARGET UNDERSTATED SENSITIVITY CHECK ===")
print("Batters with target understated balls faced:")
b_tu = batter_df[batter_df['target_understated_balls_faced'] > 0]
print(f"  Total batters with TU balls: {len(b_tu)}")
print(f"  Max TU balls faced by any batter: {b_tu['target_understated_balls_faced'].max()}")
print(f"  Mean TU balls faced among affected: {b_tu['target_understated_balls_faced'].mean():.2f}")

bo_tu = bowler_df[bowler_df['target_understated_legal_balls'] > 0]
print("Bowlers with target understated legal balls:")
print(f"  Total bowlers with TU legal balls: {len(bo_tu)}")
print(f"  Max TU legal balls by any bowler: {bo_tu['target_understated_legal_balls'].max()}")
print(f"  Mean TU legal balls among affected: {bo_tu['target_understated_legal_balls'].mean():.2f}")
