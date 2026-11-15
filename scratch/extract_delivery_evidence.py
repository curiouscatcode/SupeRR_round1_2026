import pandas as pd
import numpy as np

dms = pd.read_csv('data/processed/delivery_match_state.csv')
df_wpa = pd.read_parquet('outputs/step_16_5_wpa_investigation/delivery_wpa_leverage.parquet')

# 1. Normal Powerplay Ball 1: Match 13511 Inn 1 Over 1 Ball 1
deliv1 = dms[(dms['match_id'] == 13511) & (dms['innings'] == 1) & (dms['overid'] == 1) & (dms['over_ball_num'] == 1)].iloc[0]
print("--- 1. OVER 1 BALL 1 (Match 13511 Inn 1) ---")
cols_to_print = ['match_id', 'innings', 'overid', 'over_ball_num', 'striker_name', 'bowler_name', 'score_before', 'wickets_before', 'legal_balls_before', 'balls_remaining', 'current_run_rate', 'runs_required', 'required_run_rate', 'striker_balls_faced_before', 'bowler_legal_balls_in_spell_before', 'phase', 'phase_overs_completed', 'team_runs_added', 'is_legal_ball', 'is_wicket']
print(deliv1[cols_to_print].to_dict())

# 2. Phase Boundary: Match 13511 Inn 1 Over 6 Ball 6 vs Over 7 Ball 1
print("\n--- 2. PHASE BOUNDARY PP -> MIDDLE (Match 13511 Inn 1) ---")
deliv_pp_end = dms[(dms['match_id'] == 13511) & (dms['innings'] == 1) & (dms['overid'] == 6) & (dms['over_ball_num'] == 6)].iloc[0]
deliv_mid_start = dms[(dms['match_id'] == 13511) & (dms['innings'] == 1) & (dms['overid'] == 7) & (dms['over_ball_num'] == 1)].iloc[0]
print("PP End (Over 6 Ball 6):", deliv_pp_end[['overid', 'over_ball_num', 'score_before', 'legal_balls_before', 'phase', 'phase_overs_completed']].to_dict())
print("Mid Start (Over 7 Ball 1):", deliv_mid_start[['overid', 'over_ball_num', 'score_before', 'legal_balls_before', 'phase', 'phase_overs_completed']].to_dict())

# 3. Phase Boundary Middle -> Death: Match 13511 Inn 1 Over 15 Ball 6 vs Over 16 Ball 1
print("\n--- 3. PHASE BOUNDARY MIDDLE -> DEATH (Match 13511 Inn 1) ---")
deliv_mid_end = dms[(dms['match_id'] == 13511) & (dms['innings'] == 1) & (dms['overid'] == 15) & (dms['over_ball_num'] == 6)].iloc[0]
deliv_death_start = dms[(dms['match_id'] == 13511) & (dms['innings'] == 1) & (dms['overid'] == 16) & (dms['over_ball_num'] == 1)].iloc[0]
print("Mid End (Over 15 Ball 6):", deliv_mid_end[['overid', 'over_ball_num', 'score_before', 'legal_balls_before', 'phase', 'phase_overs_completed']].to_dict())
print("Death Start (Over 16 Ball 1):", deliv_death_start[['overid', 'over_ball_num', 'score_before', 'legal_balls_before', 'phase', 'phase_overs_completed']].to_dict())

# 4. Extra: Wide in Innings 2: Match 13522 Inn 2 Over 1 Ball 1
print("\n--- 4. EXTRA: WIDE DELIVERY (Match 13522 Inn 2 Over 1 Ball 1) ---")
deliv_wide = dms[(dms['match_id'] == 13522) & (dms['innings'] == 2) & (dms['extras_type'] == 'wide')].iloc[0]
print(deliv_wide[['match_id', 'overid', 'over_ball_num', 'score_before', 'legal_balls_before', 'balls_remaining', 'runs_required', 'required_run_rate', 'extras_type', 'team_runs_added', 'is_legal_ball']].to_dict())

# 5. Extra: No-Ball with 4 Byes: Match 31254 Inn 1 Over 17 Ball 3
print("\n--- 5. EXTRA: NO-BALL WITH 4 BYES (Match 31254 Inn 1 Over 17 Ball 3) ---")
deliv_nb = dms[(dms['match_id'] == 31254) & (dms['innings'] == 1) & (dms['overid'] == 17) & (dms['over_ball_num'] == 3)].iloc[0]
print(deliv_nb[['match_id', 'striker_name', 'bowler_name', 'runs', 'extras_type', 'extras_2_runs', 'bowler_runs_conceded', 'team_runs_added', 'is_legal_ball', 'is_batter_ball_faced', 'score_before', 'legal_balls_before']].to_dict())

# 6. Wicket Delivery: Match 13511 Inn 1 Over 1 Ball 6 (Roy out)
print("\n--- 6. WICKET DELIVERY (Match 13511 Inn 1 Over 1 Ball 6 & Over 2 Ball 1) ---")
deliv_w1 = dms[(dms['match_id'] == 13511) & (dms['innings'] == 1) & (dms['overid'] == 1) & (dms['over_ball_num'] == 6)].iloc[0]
deliv_w2 = dms[(dms['match_id'] == 13511) & (dms['innings'] == 1) & (dms['overid'] == 2) & (dms['over_ball_num'] == 1)].iloc[0]
print("Wicket Ball (Over 1 Ball 6):", deliv_w1[['overid', 'over_ball_num', 'striker_name', 'is_wicket', 'wickets_before', 'team_runs_added']].to_dict())
print("Next Ball (Over 2 Ball 1):", deliv_w2[['overid', 'over_ball_num', 'striker_name', 'wickets_before']].to_dict())

# 7. Multi-bowler over / spell continuity: Match 14098 Inn 2 Over 20 Balls 1 and 2
print("\n--- 7. MULTI-BOWLER OVER / SPELL CONTINUITY (Match 14098 Inn 2 Over 20) ---")
deliv_sp1 = dms[(dms['match_id'] == 14098) & (dms['innings'] == 2) & (dms['overid'] == 20) & (dms['over_ball_num'] == 1)].iloc[0]
deliv_sp2 = dms[(dms['match_id'] == 14098) & (dms['innings'] == 2) & (dms['overid'] == 20) & (dms['over_ball_num'] == 2)].iloc[0]
print("Ball 1 (Coulter-Nile):", deliv_sp1[['bowler_name', 'bowler_legal_balls_in_spell_before', 'is_legal_ball', 'extras_type']].to_dict())
print("Ball 2 (Parag):", deliv_sp2[['bowler_name', 'bowler_legal_balls_in_spell_before', 'is_legal_ball']].to_dict())

# 8. Dead tail delivery: Match 13522 Inn 2 Over 19 Ball 4
print("\n--- 8. DEAD TAIL DELIVERY (Match 13522 Inn 2 Over 19 Ball 4) ---")
deliv_tail = dms[(dms['match_id'] == 13522) & (dms['innings'] == 2) & (dms['overid'] == 19) & (dms['over_ball_num'] == 4)].iloc[0]
print(deliv_tail[['match_id', 'overid', 'over_ball_num', 'score_before', 'runs_required', 'balls_remaining', 'required_run_rate', 'team_runs_added']].to_dict())

# 9. DLS match leak: Match 24822 Inn 2 Over 7 Ball 1
print("\n--- 9. DLS MATCH LEAK (Match 24822 Inn 2 Over 7 Ball 1) ---")
deliv_dls = dms[(dms['match_id'] == 24822) & (dms['innings'] == 2)].iloc[-1]
print(deliv_dls[['match_id', 'overid', 'over_ball_num', 'score_before', 'wickets_before', 'legal_balls_before', 'balls_remaining', 'runs_required', 'required_run_rate']].to_dict())

# 10. WP and Expected Leverage in Climax: Match 13616 Inn 2 Over 20 Balls 1, 2, 3
print("\n--- 10. CLIMAX WP & EXPECTED LEVERAGE (Match 13616 Inn 2 Over 20) ---")
m13616 = df_wpa[(df_wpa['match_id'] == 13616) & (df_wpa['innings'] == 2) & (df_wpa['overid'] == 20)].head(3)
for idx, r in m13616.iterrows():
    print(dict(r[['over_ball_num', 'balls_remaining', 'runs_required', 'wickets_before', 'wp_before', 'expected_leverage_pct', 'runs', 'wpa_pct']]))
