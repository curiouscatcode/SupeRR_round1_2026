import pandas as pd
import numpy as np

batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

print("="*60)
print("BATTER HIGH-PRESSURE DISTRIBUTIONS (N = 816)")
print("="*60)
print(batter_df['high_balls_faced'].describe(percentiles=[0.25, 0.5, 0.75, 0.8, 0.85, 0.9, 0.95]))

thresholds = [10, 20, 30, 40, 50, 60, 75, 80, 100, 120, 150]
print("\nBatter counts above thresholds (high_balls_faced):")
for t in thresholds:
    cnt = (batter_df['high_balls_faced'] >= t).sum()
    print(f"  >= {t:3d} balls: {cnt:3d} batters ({cnt/len(batter_df)*100:.1f}%)")

print("\n" + "="*60)
print("BOWLER HIGH-PRESSURE DISTRIBUTIONS (N = 589)")
print("="*60)
print(bowler_df['high_legal_balls'].describe(percentiles=[0.25, 0.5, 0.75, 0.8, 0.85, 0.9, 0.95]))

print("\nBowler counts above thresholds (high_legal_balls):")
for t in thresholds:
    cnt = (bowler_df['high_legal_balls'] >= t).sum()
    print(f"  >= {t:3d} balls: {cnt:3d} bowlers ({cnt/len(bowler_df)*100:.1f}%)")

print("\n" + "="*60)
print("PHASE-WISE HIGH-PRESSURE DISTRIBUTIONS")
print("="*60)
print("Batter Phase Balls Faced:")
print(f"  PP: total = {batter_df['bf_pp_high'].sum()}, players > 0: {(batter_df['bf_pp_high'] > 0).sum()}, players >= 20: {(batter_df['bf_pp_high'] >= 20).sum()}, players >= 30: {(batter_df['bf_pp_high'] >= 30).sum()}")
print(f"  MO: total = {batter_df['bf_mo_high'].sum()}, players > 0: {(batter_df['bf_mo_high'] > 0).sum()}, players >= 20: {(batter_df['bf_mo_high'] >= 20).sum()}, players >= 30: {(batter_df['bf_mo_high'] >= 30).sum()}")
print(f"  DO: total = {batter_df['bf_do_high'].sum()}, players > 0: {(batter_df['bf_do_high'] > 0).sum()}, players >= 20: {(batter_df['bf_do_high'] >= 20).sum()}, players >= 30: {(batter_df['bf_do_high'] >= 30).sum()}")

print("\nBowler Phase Legal Balls:")
print(f"  PP: total = {bowler_df['lb_pp_high'].sum()}, players > 0: {(bowler_df['lb_pp_high'] > 0).sum()}, players >= 20: {(bowler_df['lb_pp_high'] >= 20).sum()}, players >= 30: {(bowler_df['lb_pp_high'] >= 30).sum()}")
print(f"  MO: total = {bowler_df['lb_mo_high'].sum()}, players > 0: {(bowler_df['lb_mo_high'] > 0).sum()}, players >= 20: {(bowler_df['lb_mo_high'] >= 20).sum()}, players >= 30: {(bowler_df['lb_mo_high'] >= 30).sum()}")
print(f"  DO: total = {bowler_df['lb_do_high'].sum()}, players > 0: {(bowler_df['lb_do_high'] > 0).sum()}, players >= 20: {(bowler_df['lb_do_high'] >= 20).sum()}, players >= 30: {(bowler_df['lb_do_high'] >= 30).sum()}")

# Aggregates across all high-pressure deliveries
total_bat_hp_runs = batter_df['high_runs'].sum()
total_bat_hp_bf = batter_df['high_balls_faced'].sum()
total_bat_hp_fours = batter_df['high_fours'].sum()
total_bat_hp_sixes = batter_df['high_sixes'].sum()
total_bat_hp_dots = batter_df['high_dot_balls'].sum()
total_bat_hp_outs = batter_df['high_dismissals'].sum()

print("\n" + "="*60)
print("POPULATION HIGH-PRESSURE AGGREGATES (BATTERS)")
print("="*60)
pop_sr = (total_bat_hp_runs / total_bat_hp_bf) * 100
pop_bnd_pct = ((total_bat_hp_fours + total_bat_hp_sixes) / total_bat_hp_bf) * 100
pop_dot_pct = (total_bat_hp_dots / total_bat_hp_bf) * 100
pop_out_pct = (total_bat_hp_outs / total_bat_hp_bf) * 100
print(f"Total HP Balls Faced: {total_bat_hp_bf}")
print(f"Population Strike Rate: {pop_sr:.2f}")
print(f"Population Boundary %: {pop_bnd_pct:.2f}%")
print(f"Population Dot %: {pop_dot_pct:.2f}%")
print(f"Population Dismissal %: {pop_out_pct:.2f}% (Average balls per dismissal: {total_bat_hp_bf / total_bat_hp_outs:.2f})")

total_bowl_hp_rc = bowler_df['high_runs_conceded'].sum()
total_bowl_hp_lb = bowler_df['high_legal_balls'].sum()
total_bowl_hp_dots = bowler_df['high_dot_balls'].sum()
total_bowl_hp_bnd = bowler_df['high_boundaries_conceded'].sum()
total_bowl_hp_wk = bowler_df['high_wickets'].sum()

print("\n" + "="*60)
print("POPULATION HIGH-PRESSURE AGGREGATES (BOWLERS)")
print("="*60)
pop_econ = (total_bowl_hp_rc / total_bowl_hp_lb) * 6
pop_bowl_dot_pct = (total_bowl_hp_dots / total_bowl_hp_lb) * 100
pop_bowl_bnd_pct = (total_bowl_hp_bnd / total_bowl_hp_lb) * 100
pop_bowl_sr = total_bowl_hp_lb / total_bowl_hp_wk if total_bowl_hp_wk > 0 else np.nan
print(f"Total HP Legal Balls: {total_bowl_hp_lb}")
print(f"Population Economy Rate: {pop_econ:.2f}")
print(f"Population Bowling Dot %: {pop_bowl_dot_pct:.2f}%")
print(f"Population Boundary Conceded %: {pop_bowl_bnd_pct:.2f}%")
print(f"Population Wicket Strike Rate: {pop_bowl_sr:.2f} balls/wicket")
