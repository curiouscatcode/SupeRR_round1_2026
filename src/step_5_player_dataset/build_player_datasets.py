"""
Step 5 - Module 1: Build Player-Level Batting & Bowling Pressure Datasets
========================================================================
Constructs clean player-delivery performance datasets linked to Step 4.3 pressure:
1. batting_pressure_deliveries.parquet & .csv
2. bowling_pressure_deliveries.parquet & .csv
3. player_mapping_audit.csv

Guarantees:
- Exact 1-to-1 mapping with delivery_pressure_v3.parquet (186,780 deliveries).
- Strict striker vs non-striker attribution (batter runs, boundaries, striker outs).
- Strict bowler vs fielding attribution (bowler runs conceded, bowler wickets vs run outs).
- Exact pressure preservation from v3 (pressure_batting, pressure_bowling, T, L_norm, L, WP).
"""

import os
import json
import numpy as np
import pandas as pd

OUTPUT_DIR = "outputs/step_5_player_level_dataset"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
OTHER_DISMISSAL_TYPES = ['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field']

def build_datasets():
    print("=" * 80)
    print("STEP 5: BUILDING PLAYER-LEVEL PRESSURE PERFORMANCE DATASETS")
    print("=" * 80)

    v3_path = "outputs/step_4_pressure_pipeline/delivery_pressure_v3.parquet"
    cohort_path = "outputs/step_4_pressure_pipeline/clean_cohort_deliveries.parquet"
    mapping_path = "data/competition_team_player_mapping.csv"
    p11_path = "data/playing_eleven.csv"
    matches_path = "data/matches.csv"

    print(f"Loading {v3_path}...")
    df_v3 = pd.read_parquet(v3_path)
    print(f"Loading {cohort_path}...")
    df_cohort = pd.read_parquet(cohort_path)

    assert len(df_v3) == 186780, f"Expected 186,780 rows in v3, found {len(df_v3)}"
    assert len(df_cohort) == 186780, f"Expected 186,780 rows in cohort, found {len(df_cohort)}"

    # Verify key alignment
    key_cols = ['match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num']
    assert (df_v3[key_cols] == df_cohort[key_cols]).all().all(), "Keys are not aligned between v3 and cohort!"
    print("Key alignment verified bit-for-bit across all 186,780 deliveries.")

    # -------------------------------------------------------------
    # 1. CONSTRUCT BATTING PRESSURE DELIVERIES
    # -------------------------------------------------------------
    print("\n--- 1. Constructing Batting Pressure Deliveries ---")
    bat_df = pd.DataFrame()
    
    # Sequence & Match Keys
    for col in key_cols:
        bat_df[col] = df_v3[col]
        
    # Team IDs
    bat_df['batting_team_id'] = df_v3['batting_team_id']
    bat_df['bowling_team_id'] = df_v3['bowling_team_id']
    
    # Players
    bat_df['striker_id'] = df_v3['striker_id']
    bat_df['striker_name'] = df_v3['striker_name']
    bat_df['non_striker_id'] = df_v3['non_striker_id']
    bat_df['non_striker_name'] = df_v3['non_striker_name']
    bat_df['bowler_id'] = df_v3['bowler_id']
    bat_df['bowler_name'] = df_v3['bowler_name']
    
    # Pre-delivery match state at t^-
    bat_df['phase'] = df_v3['phase']
    bat_df['score_before'] = df_v3['score_before']
    bat_df['wickets_before'] = df_v3['wickets_before']
    bat_df['W_t'] = df_v3['W_t']
    bat_df['W_rem'] = df_v3['W_rem']
    bat_df['legal_balls_before'] = df_v3['legal_balls_before']
    bat_df['balls_remaining'] = df_v3['balls_remaining']
    bat_df['current_run_rate'] = df_v3['current_run_rate']
    bat_df['runs_required'] = df_v3['runs_required']
    bat_df['required_run_rate'] = df_v3['required_run_rate']
    bat_df['striker_balls_faced_before'] = df_cohort['striker_balls_faced_before']
    bat_df['venue_id'] = df_cohort['venue_id']
    
    # Step 4.3 Approved Pressure Measurements (Attributed to Striker)
    bat_df['pressure_batting'] = df_v3['pressure_batting']
    bat_df['task_difficulty_bat'] = df_v3['task_difficulty_bat']
    bat_df['normalized_consequence_L'] = df_v3['normalized_consequence_L']
    bat_df['raw_consequence_L'] = df_v3['raw_consequence_L']
    bat_df['pre_delivery_wp'] = df_v3['pre_delivery_wp']
    
    # Batting Performance Outcomes (Attributed strictly to Striker)
    bat_df['batter_runs'] = df_v3['runs']
    bat_df['team_runs_added'] = df_cohort['team_runs_added']
    bat_df['is_four'] = df_v3['is_four'].astype(bool)
    bat_df['is_six'] = df_v3['is_six'].astype(bool)
    bat_df['is_boundary'] = (bat_df['is_four'] | bat_df['is_six'])
    
    # Ball Faced Indicators
    bat_df['is_legal_ball'] = df_v3['is_legal_ball'].astype(bool)
    bat_df['is_batter_ball_faced'] = df_cohort['is_batter_ball_faced'].astype(bool)
    bat_df['is_dot_ball_faced'] = bat_df['is_batter_ball_faced'] & (bat_df['batter_runs'] == 0)
    
    # Extras
    bat_df['extras_type'] = df_cohort['extras_type']
    bat_df['extras1_runs'] = df_cohort['extras1_runs'].fillna(0).astype(int)
    bat_df['extras_2_runs'] = df_cohort['extras_2_runs'].fillna(0).astype(int)
    
    # Dismissal Information
    bat_df['is_wicket'] = df_cohort['is_wicket'].astype(bool)
    bat_df['dismissal_type'] = df_cohort['dismissal_type']
    bat_df['dismissal_type_id'] = df_cohort['dismissal_type_id']
    bat_df['dismissed_player_id'] = df_cohort['dismissed_player_id']
    
    # Strict Striker vs Non-Striker Out Attribution
    bat_df['is_striker_dismissed'] = bat_df['is_wicket'] & (df_cohort['dismissed_player_id'] == bat_df['striker_id'])
    bat_df['is_non_striker_dismissed'] = bat_df['is_wicket'] & (df_cohort['dismissed_player_id'] == bat_df['non_striker_id'])

    print(f"Batting dataset rows: {len(bat_df):,}")
    print(f"  Striker dismissals:     {bat_df['is_striker_dismissed'].sum():,}")
    print(f"  Non-striker dismissals: {bat_df['is_non_striker_dismissed'].sum():,}")
    print(f"  Balls faced (official): {bat_df['is_batter_ball_faced'].sum():,}")
    print(f"  Total batter runs:      {bat_df['batter_runs'].sum():,}")
    print(f"  Total team runs:        {bat_df['team_runs_added'].sum():,}")

    # -------------------------------------------------------------
    # 2. CONSTRUCT BOWLING PRESSURE DELIVERIES
    # -------------------------------------------------------------
    print("\n--- 2. Constructing Bowling Pressure Deliveries ---")
    bowl_df = pd.DataFrame()
    
    # Sequence & Match Keys
    for col in key_cols:
        bowl_df[col] = df_v3[col]
        
    # Team IDs
    bowl_df['bowling_team_id'] = df_v3['bowling_team_id']
    bowl_df['batting_team_id'] = df_v3['batting_team_id']
    
    # Players
    bowl_df['bowler_id'] = df_v3['bowler_id']
    bowl_df['bowler_name'] = df_v3['bowler_name']
    bowl_df['striker_id'] = df_v3['striker_id']
    bowl_df['striker_name'] = df_v3['striker_name']
    bowl_df['non_striker_id'] = df_v3['non_striker_id']
    bowl_df['non_striker_name'] = df_v3['non_striker_name']
    
    # Pre-delivery match state at t^-
    bowl_df['phase'] = df_v3['phase']
    bowl_df['score_before'] = df_v3['score_before']
    bowl_df['wickets_before'] = df_v3['wickets_before']
    bowl_df['W_t'] = df_v3['W_t']
    bowl_df['W_rem'] = df_v3['W_rem']
    bowl_df['legal_balls_before'] = df_v3['legal_balls_before']
    bowl_df['balls_remaining'] = df_v3['balls_remaining']
    bowl_df['current_run_rate'] = df_v3['current_run_rate']
    bowl_df['runs_required'] = df_v3['runs_required']
    bowl_df['required_run_rate'] = df_v3['required_run_rate']
    bowl_df['bowler_legal_balls_in_spell_before'] = df_cohort['bowler_legal_balls_in_spell_before']
    bowl_df['venue_id'] = df_cohort['venue_id']
    
    # Step 4.3 Approved Pressure Measurements (Attributed to Bowler)
    bowl_df['pressure_bowling'] = df_v3['pressure_bowling']
    bowl_df['task_difficulty_bowl'] = df_v3['task_difficulty_bowl']
    bowl_df['normalized_consequence_L'] = df_v3['normalized_consequence_L']
    bowl_df['raw_consequence_L'] = df_v3['raw_consequence_L']
    bowl_df['pre_delivery_wp'] = df_v3['pre_delivery_wp']
    
    # Bowling Performance Outcomes
    bowl_df['bowler_runs_conceded'] = df_cohort['bowler_runs_conceded']
    bowl_df['team_runs_added'] = df_cohort['team_runs_added']
    
    # Bowler-Credit Wickets vs Other Dismissals
    bowl_df['is_wicket'] = df_cohort['is_wicket'].astype(bool)
    bowl_df['dismissal_type'] = df_cohort['dismissal_type']
    bowl_df['dismissal_type_id'] = df_cohort['dismissal_type_id']
    bowl_df['dismissed_player_id'] = df_cohort['dismissed_player_id']
    
    bowl_df['is_bowler_wicket'] = bowl_df['is_wicket'] & df_cohort['dismissal_type'].isin(BOWLER_WICKET_TYPES)
    bowl_df['is_other_dismissal'] = bowl_df['is_wicket'] & ~df_cohort['dismissal_type'].isin(BOWLER_WICKET_TYPES)
    
    # Dot & Boundary Conceded Indicators
    bowl_df['is_bowler_dot_ball'] = (bowl_df['bowler_runs_conceded'] == 0)
    bowl_df['is_four_conceded'] = df_v3['is_four'].astype(bool)
    bowl_df['is_six_conceded'] = df_v3['is_six'].astype(bool)
    bowl_df['is_boundary_conceded'] = (bowl_df['is_four_conceded'] | bowl_df['is_six_conceded'])
    
    # Delivery Classification & Extras
    bowl_df['is_legal_ball'] = df_v3['is_legal_ball'].astype(bool)
    bowl_df['extras_type'] = df_cohort['extras_type']
    bowl_df['extras1_runs'] = df_cohort['extras1_runs'].fillna(0).astype(int)
    bowl_df['extras_2_runs'] = df_cohort['extras_2_runs'].fillna(0).astype(int)
    
    bowl_df['is_wide'] = (bowl_df['extras_type'] == 'wide')
    bowl_df['is_no_ball'] = bowl_df['extras_type'].isin(['Overstep', 'other'])
    bowl_df['is_bye'] = (bowl_df['extras_type'] == 'byes')
    bowl_df['is_leg_bye'] = (bowl_df['extras_type'] == 'legbyes')

    print(f"Bowling dataset rows: {len(bowl_df):,}")
    print(f"  Bowler-credited wickets: {bowl_df['is_bowler_wicket'].sum():,}")
    print(f"  Other dismissals:        {bowl_df['is_other_dismissal'].sum():,}")
    print(f"  Legal deliveries:        {bowl_df['is_legal_ball'].sum():,}")
    print(f"  Bowler runs conceded:    {bowl_df['bowler_runs_conceded'].sum():,}")
    print(f"  Bowler dot balls:        {bowl_df['is_bowler_dot_ball'].sum():,}")

    # -------------------------------------------------------------
    # 3. EXPORT PARQUET AND CSV
    # -------------------------------------------------------------
    print("\n--- 3. Exporting Datasets ---")
    bat_parquet = os.path.join(OUTPUT_DIR, "batting_pressure_deliveries.parquet")
    bat_csv = os.path.join(OUTPUT_DIR, "batting_pressure_deliveries.csv")
    bowl_parquet = os.path.join(OUTPUT_DIR, "bowling_pressure_deliveries.parquet")
    bowl_csv = os.path.join(OUTPUT_DIR, "bowling_pressure_deliveries.csv")
    
    print(f"Saving {bat_parquet}...")
    bat_df.to_parquet(bat_parquet, index=False)
    print(f"Saving {bat_csv}...")
    bat_df.to_csv(bat_csv, index=False)
    
    print(f"Saving {bowl_parquet}...")
    bowl_df.to_parquet(bowl_parquet, index=False)
    print(f"Saving {bowl_csv}...")
    bowl_df.to_csv(bowl_csv, index=False)
    print("Dataset exports completed successfully.")

    # -------------------------------------------------------------
    # 4. PLAYER MAPPING AUDIT
    # -------------------------------------------------------------
    print("\n--- 4. Generating Player Mapping Audit ---")
    mapping = pd.read_csv(mapping_path)
    p11 = pd.read_csv(p11_path)
    matches = pd.read_csv(matches_path)
    
    # Collect all unique players in the 186,780 deliveries
    strikers_agg = bat_df.groupby('striker_id').agg({
        'striker_name': 'first',
        'innings_ball_num': 'count',
        'is_batter_ball_faced': 'sum',
        'batter_runs': 'sum',
        'is_four': 'sum',
        'is_six': 'sum',
        'is_striker_dismissed': 'sum',
        'match_id': 'nunique'
    }).reset_index().rename(columns={
        'striker_id': 'player_id',
        'striker_name': 'player_name',
        'innings_ball_num': 'batting_deliveries',
        'is_batter_ball_faced': 'official_balls_faced',
        'batter_runs': 'total_batter_runs',
        'is_four': 'total_fours',
        'is_six': 'total_sixes',
        'is_striker_dismissed': 'total_outs',
        'match_id': 'batting_matches'
    })
    
    bowlers_agg = bowl_df.groupby('bowler_id').agg({
        'bowler_name': 'first',
        'innings_ball_num': 'count',
        'is_legal_ball': 'sum',
        'bowler_runs_conceded': 'sum',
        'is_bowler_wicket': 'sum',
        'is_bowler_dot_ball': 'sum',
        'match_id': 'nunique'
    }).reset_index().rename(columns={
        'bowler_id': 'player_id',
        'bowler_name': 'player_name',
        'innings_ball_num': 'bowling_deliveries',
        'is_legal_ball': 'official_legal_balls',
        'bowler_runs_conceded': 'total_runs_conceded',
        'is_bowler_wicket': 'total_bowler_wickets',
        'is_bowler_dot_ball': 'total_dot_balls_bowled',
        'match_id': 'bowling_matches'
    })
    
    # Non-strikers unique
    ns_unique = set(bat_df['non_striker_id'].unique())
    
    # Full set of players
    all_player_ids = sorted(list(set(strikers_agg['player_id']) | set(bowlers_agg['player_id']) | ns_unique))
    
    # Player master dictionary
    id_to_name = {}
    for pid, name in zip(bat_df['striker_id'], bat_df['striker_name']): id_to_name[pid] = name
    for pid, name in zip(bowl_df['bowler_id'], bowl_df['bowler_name']): id_to_name[pid] = name
    for pid, name in zip(bat_df['non_striker_id'], bat_df['non_striker_name']): id_to_name[pid] = name
    
    map_pids = set(mapping['player_id'].unique())
    p11_pids = set(p11['player_id'].unique())
    
    # Build metadata lookup: team names and competitions
    p_teams = mapping.groupby('player_id')['team_name'].unique().to_dict()
    p_comps = mapping.groupby('player_id')['comp_name'].unique().to_dict()
    
    # Matches played across playing eleven
    p11_matches = p11[p11['is_played'] == True].groupby('player_id')['match_id'].nunique().to_dict()
    
    audit_rows = []
    for pid in all_player_ids:
        s_row = strikers_agg[strikers_agg['player_id'] == pid]
        b_row = bowlers_agg[bowlers_agg['player_id'] == pid]
        
        is_striker = len(s_row) > 0
        is_bowler = len(b_row) > 0
        is_non_striker = pid in ns_unique
        
        b_del = int(s_row['batting_deliveries'].values[0]) if is_striker else 0
        b_bf = int(s_row['official_balls_faced'].values[0]) if is_striker else 0
        b_runs = int(s_row['total_batter_runs'].values[0]) if is_striker else 0
        b_fours = int(s_row['total_fours'].values[0]) if is_striker else 0
        b_sixes = int(s_row['total_sixes'].values[0]) if is_striker else 0
        b_outs = int(s_row['total_outs'].values[0]) if is_striker else 0
        
        bw_del = int(b_row['bowling_deliveries'].values[0]) if is_bowler else 0
        bw_lb = int(b_row['official_legal_balls'].values[0]) if is_bowler else 0
        bw_rc = int(b_row['total_runs_conceded'].values[0]) if is_bowler else 0
        bw_wk = int(b_row['total_bowler_wickets'].values[0]) if is_bowler else 0
        bw_dots = int(b_row['total_dot_balls_bowled'].values[0]) if is_bowler else 0
        
        in_map = pid in map_pids
        in_p11 = pid in p11_pids
        
        t_list = "; ".join(sorted(p_teams.get(pid, [])))
        c_list = "; ".join(sorted(p_comps.get(pid, [])))
        p11_m = p11_matches.get(pid, 0)
        
        audit_rows.append({
            'player_id': pid,
            'player_name': id_to_name[pid],
            'is_striker': is_striker,
            'is_bowler': is_bowler,
            'is_non_striker': is_non_striker,
            'batting_deliveries': b_del,
            'official_balls_faced': b_bf,
            'total_batter_runs': b_runs,
            'total_fours': b_fours,
            'total_sixes': b_sixes,
            'total_outs': b_outs,
            'bowling_deliveries': bw_del,
            'official_legal_balls': bw_lb,
            'total_runs_conceded': bw_rc,
            'total_bowler_wickets': bw_wk,
            'total_dot_balls_bowled': bw_dots,
            'in_competition_mapping': in_map,
            'in_playing_eleven': in_p11,
            'matches_in_playing_eleven': p11_m,
            'teams': t_list,
            'competitions': c_list
        })
        
    audit_df = pd.DataFrame(audit_rows)
    audit_csv = os.path.join(OUTPUT_DIR, "player_mapping_audit.csv")
    audit_df.to_csv(audit_csv, index=False)
    print(f"Saved player mapping audit ({len(audit_df):,} players) to {audit_csv}")
    
    return bat_df, bowl_df, audit_df

if __name__ == '__main__':
    build_datasets()
