import pandas as pd

df_bat_74 = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
df_bowl_74 = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

df_bn_bat = pd.read_csv('outputs/step_8_eda/big_name_player_analysis/big_name_batting_leaderboard.csv')
df_bn_bowl = pd.read_csv('outputs/step_8_eda/big_name_player_analysis/big_name_bowling_leaderboard.csv')

print("=== RECONCILING BIG-NAME BATTING ===")
for _, r in df_bn_bat.iterrows():
    p_name = r['Dataset Name']
    bn_rank = r['Overall Rank']
    bn_shrunk = r['Shrunk PWSVA']
    bn_raw = r['Raw PWSVA']
    
    m74 = df_bat_74[df_bat_74['Player'] == p_name]
    if not m74.empty:
        r74 = m74.iloc[0]
        rank_74 = r74['Rank']
        shrunk_74 = r74['Shrunk score']
        raw_74 = r74['Raw score']
        match = (bn_rank == rank_74) and (abs(bn_shrunk - shrunk_74) < 1e-5)
        print(f"{p_name}: BN Rank={bn_rank}, Step 7.4 Rank={rank_74} | Match={match} | Shrunk={shrunk_74:.4f}")
    else:
        print(f"NOT FOUND in Step 7.4: {p_name}")

print("\n=== RECONCILING BIG-NAME BOWLING ===")
for _, r in df_bn_bowl.iterrows():
    p_name = r['Dataset Name']
    bn_rank = r['Overall Rank']
    bn_shrunk = r['Shrunk SBVA']
    bn_raw = r['Raw SBVA']
    
    m74 = df_bowl_74[df_bowl_74['Player'] == p_name]
    if not m74.empty:
        r74 = m74.iloc[0]
        rank_74 = r74['Rank']
        shrunk_74 = r74['Shrunk score']
        raw_74 = r74['Raw score']
        match = (bn_rank == rank_74) and (abs(bn_shrunk - shrunk_74) < 1e-5)
        print(f"{p_name}: BN Rank={bn_rank}, Step 7.4 Rank={rank_74} | Match={match} | Shrunk={shrunk_74:.4f}")
    else:
        print(f"NOT FOUND in Step 7.4: {p_name}")
