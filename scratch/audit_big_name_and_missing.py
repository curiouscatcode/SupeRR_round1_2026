import os
import pandas as pd
import numpy as np

bn_bat = pd.read_csv('outputs/step_8_eda/big_name_player_analysis/big_name_batting_leaderboard.csv')
bn_bowl = pd.read_csv('outputs/step_8_eda/big_name_player_analysis/big_name_bowling_leaderboard.csv')
unqual = pd.read_csv('outputs/step_8_eda/big_name_player_analysis/unqualified_or_missing_players.csv')

bat_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bowl_elig = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bowl_del = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

print("--- 1. AUDITING BIG-NAME BATTING LEADERBOARD (17 PLAYERS) ---")
bat_discrepancies = []
for _, r in bn_bat.iterrows():
    pname = r['Dataset Name']
    match = bat_elig[bat_elig['Player'] == pname]
    if len(match) == 0:
        bat_discrepancies.append((pname, 'Not found in all_eligible_batting_players.csv'))
    else:
        m = match.iloc[0]
        rank_diff = r['Overall Rank'] - m['Rank']
        score_diff = abs(r['Shrunk PWSVA'] - m['Shrunk score'])
        ess_diff = abs(r['Kish ESS'] - m['Kish ESS'])
        if rank_diff != 0 or score_diff > 1e-6 or ess_diff > 1e-4:
            bat_discrepancies.append((pname, f"Rank diff={rank_diff}, Score diff={score_diff:.2e}"))
        else:
            print(f"VERIFIED: #{int(r['Overall Rank']):03d} {r['Requested Name']:18s} | Shrunk={r['Shrunk PWSVA']:+.4f} | Balls={int(r['Balls Faced'])}")

print(f"Batting Discrepancies count: {len(bat_discrepancies)}")

print("\n--- 2. AUDITING BIG-NAME BOWLING LEADERBOARD (11 PLAYERS) ---")
bowl_discrepancies = []
for _, r in bn_bowl.iterrows():
    pname = r['Dataset Name']
    match = bowl_elig[bowl_elig['Player'] == pname]
    if len(match) == 0:
        bowl_discrepancies.append((pname, 'Not found in all_eligible_bowling_players.csv'))
    else:
        m = match.iloc[0]
        rank_diff = r['Overall Rank'] - m['Rank']
        score_diff = abs(r['Shrunk SBVA'] - m['Shrunk score'])
        ess_diff = abs(r['Kish ESS'] - m['Kish ESS'])
        if rank_diff != 0 or score_diff > 1e-6 or ess_diff > 1e-4:
            bowl_discrepancies.append((pname, f"Rank diff={rank_diff}, Score diff={score_diff:.2e}"))
        else:
            print(f"VERIFIED: #{int(r['Overall Rank']):03d} {r['Requested Name']:18s} | Shrunk={r['Shrunk SBVA']:+.4f} | Balls={int(r['Legal Balls'])}")

print(f"Bowling Discrepancies count: {len(bowl_discrepancies)}")

print("\n--- 3. AUDITING UNQUALIFIED / MISSING PLAYERS ---")
# Specifically check Ben Stokes, Steve Smith, Shan Masood, Kieron Pollard
targets = ['Ben Stokes', 'Steve Smith', 'Shan Masood', 'Kieron Pollard']
for t in targets:
    r = unqual[unqual['Player Name'] == t].iloc[0]
    print(f"\nPlayer: {t}")
    print(f"  Reported Status: {r['Status']}")
    print(f"  Reported Reason: {r['Reason']}")
    
    # Check batting deliveries in raw dataset
    b_sub = bat_del[bat_del['striker_name'] == t]
    b_faced = b_sub[b_sub['is_batter_ball_faced'] == True]
    b_p50 = b_faced[b_faced['pressure_batting'] >= 50.0]
    
    # Check bowling deliveries in raw dataset
    bw_sub = bowl_del[bowl_del['bowler_name'] == t]
    bw_leg = bw_sub[bw_sub['is_legal_ball'] == True]
    bw_p50 = bw_leg[bw_leg['pressure_bowling'] >= 50.0]
    
    print(f"  Actual Batting Faced: {len(b_faced)}, P>=50: {len(b_p50)} (Reported: {r['Batting Balls Faced']}, {r['Batting P>=50 Opps']})")
    print(f"  Actual Bowling Legal: {len(bw_leg)}, P>=50: {len(bw_p50)} (Reported: {r['Bowling Legal Balls']}, {r['Bowling P>=50 Opps']})")
