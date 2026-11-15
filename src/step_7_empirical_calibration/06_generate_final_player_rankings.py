"""
Step 7.4: Final Player Reliability Scoring and Ranking Engine
SupeRR Selector Round 1 - Official Implementation

This script implements:
1. Strict Step 6.2 Player Eligibility:
   - Batting: N(P_bat >= 50) >= 50 balls faced (297 qualifying batters)
   - Bowling: N_leg(P_bowl >= 50) >= 50 legal balls bowled (292 qualifying bowlers)
2. Final Batting Reliability Scoring:
   - Frozen PWSVA formula with situation-dependent wicket valuation (lambda_eff)
   - Step 7.2.1 conditions: Innings 2 non-terminal wickets capped at runs_required,
     terminal wicket uncapped, format-stratified DLS curves.
   - Pressure weighting: w(P) = (P / 50)^1.00
   - Kish Effective Sample Size: N_eff = (sum w)^2 / sum (w^2)
   - Empirical Bayes Shrinkage: K_bat = 600
3. Final Bowling Reliability Scoring:
   - Frozen SBVA formula with legal-quota accounting:
     numerator accumulates all deliveries (legal + extras),
     denominator and Kish ESS accumulate legal deliveries.
   - Pressure weighting: w(P) = (P / 50)^1.00
   - Empirical Bayes Shrinkage: K_bowl = 500
4. Match-Level Block Bootstrap Uncertainty (B = 1,000):
   - Resampling 782 matches with replacement (fixed seed 42)
   - Shrunk score SE, 95% CI, presence count, and rank distribution intervals
5. Alpha Sensitivity Analysis (alpha = 1.25):
   - Sensitivity rankings, Spearman correlations, rank transitions
6. Automated Quality Checks & Delivery-Level Independent Spot Checks:
   - Verification against underlying delivery rows for 3 batters and 3 bowlers
7. Deliverables Generation:
   - CSV rankings, JSON summary, PNG figures

Output Directory: outputs/step_7_empirical_calibration/step_7_4_final_rankings/
"""

import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def assign_wkt_bucket(df):
    w = df['W_t']
    ph = df['phase']
    bucket = pd.Series(index=df.index, dtype='object')
    bucket[(ph == 'PP') & (w == 0)] = '0'
    bucket[(ph == 'PP') & (w == 1)] = '1'
    bucket[(ph == 'PP') & (w >= 2)] = '2+'
    bucket[(ph == 'Middle') & (w <= 2)] = '0-2'
    bucket[(ph == 'Middle') & (w >= 3) & (w <= 4)] = '3-4'
    bucket[(ph == 'Middle') & (w >= 5)] = '5+'
    bucket[(ph == 'Death') & (w <= 3)] = '0-3'
    bucket[(ph == 'Death') & (w >= 4) & (w <= 6)] = '4-6'
    bucket[(ph == 'Death') & (w >= 7)] = '7+'
    return bucket

def get_player_metadata(df, id_col, name_col, team_col, format_col):
    records = {}
    for pid, grp in df.groupby(id_col):
        name = grp[name_col].iloc[0]
        fmts = sorted(grp[format_col].dropna().unique())
        fmt_str = ' & '.join(fmts)
        # Primary team is the team where player had most appearances/balls
        primary_team = grp[team_col].value_counts().index[0]
        team_context = f"{primary_team} ({fmt_str})"
        records[pid] = {
            'player_name': name,
            'primary_team': primary_team,
            'formats': fmt_str,
            'team_format': team_context
        }
    return records

def main():
    t_start = time.time()
    out_dir = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings'
    os.makedirs(out_dir, exist_ok=True)
    
    print("================================================================================")
    print("STEP 7.4: FINAL PLAYER RELIABILITY SCORING AND RANKING ENGINE")
    print("================================================================================")
    
    # --------------------------------------------------------------------------
    # 1. Load Frozen Datasets & Baselines
    # --------------------------------------------------------------------------
    print("\n[Stage 1] Loading frozen datasets, baselines, and lookup tables...")
    bat = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
    bowl = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')
    
    matches = pd.read_csv('data/matches.csv')
    comps = pd.read_csv('data/competitions.csv')
    teams = pd.read_csv('data/teams.csv')
    
    m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
    m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})
    
    bat = bat.merge(m_comp[['match_id', 'format']], on='match_id', how='left')
    bowl = bowl.merge(m_comp[['match_id', 'format']], on='match_id', how='left')
    
    team_map = teams[['team_id', 'team_name']].drop_duplicates().set_index('team_id')['team_name'].to_dict()
    bat['team_name'] = bat['batting_team_id'].map(team_map)
    bowl['team_name'] = bowl['bowling_team_id'].map(team_map)
    
    # 36-cell tensor assignment
    bat['wkt_bucket'] = assign_wkt_bucket(bat)
    bowl['wkt_bucket'] = assign_wkt_bucket(bowl)
    bat['cell_id'] = bat['innings'].astype(str) + '_' + bat['format'] + '_' + bat['phase'] + '_' + bat['wkt_bucket']
    bowl['cell_id'] = bowl['innings'].astype(str) + '_' + bowl['format'] + '_' + bowl['phase'] + '_' + bowl['wkt_bucket']
    
    bat_base = pd.read_parquet('outputs/step_7_empirical_calibration/batting_baseline_36cells.parquet')
    bowl_base = pd.read_parquet('outputs/step_7_empirical_calibration/bowling_baseline_36cells.parquet')
    bat = bat.merge(bat_base[['cell_id', 'exp_runs', 'exp_striker_dismissal']], on='cell_id', how='left')
    bowl = bowl.merge(bowl_base[['cell_id', 'exp_runs_conceded', 'exp_bowler_wicket']], on='cell_id', how='left')
    
    # Wicket valuation lookup table
    lw = pd.read_parquet('outputs/step_7_empirical_calibration/step_7_2_wicket_valuation/wicket_value_lookup.parquet')
    bat = bat.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')
    bowl = bowl.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')
    
    # Step 7.2.1 Conditions:
    # 1. Innings 2 non-terminal wickets capped at runs_required
    # 2. Terminal wicket (W_rem == 1) retains uncapped lambda_wkt
    # 3. Format-stratified parameter sets
    for df in [bat, bowl]:
        is_inn2_non_term = (df['innings'] == 2) & (df['W_rem'] > 1)
        df['lambda_eff'] = df['lambda_wkt'].copy()
        df.loc[is_inn2_non_term, 'lambda_eff'] = np.minimum(df.loc[is_inn2_non_term, 'lambda_wkt'], df.loc[is_inn2_non_term, 'runs_required'])
        
    # Calculate delivery-level Value-Added:
    # Batting: strictly is_batter_ball_faced == True
    bat_faced = bat[bat['is_batter_ball_faced'] == True].copy()
    bat_faced['v_bat'] = (bat_faced['batter_runs'] - bat_faced['exp_runs']) - bat_faced['lambda_eff'] * (bat_faced['is_striker_dismissed'].astype(float) - bat_faced['exp_striker_dismissal'])
    
    # Bowling: quota accounting via legal balls
    is_leg = bowl['is_legal_ball'] == True
    bowl['v_bowl'] = np.zeros(len(bowl))
    bowl.loc[is_leg, 'v_bowl'] = (bowl.loc[is_leg, 'exp_runs_conceded'] - bowl.loc[is_leg, 'bowler_runs_conceded']) + bowl.loc[is_leg, 'lambda_eff'] * (bowl.loc[is_leg, 'is_bowler_wicket'].astype(float) - bowl.loc[is_leg, 'exp_bowler_wicket'])
    bowl.loc[~is_leg, 'v_bowl'] = - bowl.loc[~is_leg, 'bowler_runs_conceded'] + bowl.loc[~is_leg, 'lambda_eff'] * bowl.loc[~is_leg, 'is_bowler_wicket'].astype(float)
    
    print(f"Loaded {len(bat_faced)} batting balls faced and {len(bowl)} bowling deliveries across 782 matches.")

    # --------------------------------------------------------------------------
    # 2. Strict Player Eligibility Verification (Step 6.2 Standard)
    # --------------------------------------------------------------------------
    print("\n[Stage 2] Enforcing strict Step 6.2 Player Eligibility...")
    
    # Batting: N(P_bat >= 50) >= 50 balls faced
    bat_p50 = bat_faced[bat_faced['pressure_batting'] >= 50.0]
    bat_p50_counts = bat_p50.groupby('striker_id').size()
    qual_bat_ids = sorted(bat_p50_counts[bat_p50_counts >= 50].index.tolist())
    print(f"Batting: {len(qual_bat_ids)} qualifying batters (Expected: 297).")
    assert len(qual_bat_ids) == 297, f"Batting qualifying count mismatch: got {len(qual_bat_ids)}, expected 297"
    
    # Bowling: N_leg(P_bowl >= 50) >= 50 legal balls bowled
    bowl_leg = bowl[bowl['is_legal_ball'] == True]
    bowl_p50 = bowl_leg[bowl_leg['pressure_bowling'] >= 50.0]
    bowl_p50_counts = bowl_p50.groupby('bowler_id').size()
    qual_bowl_ids = sorted(bowl_p50_counts[bowl_p50_counts >= 50].index.tolist())
    print(f"Bowling: {len(qual_bowl_ids)} qualifying bowlers (Expected: 292).")
    assert len(qual_bowl_ids) == 292, f"Bowling qualifying count mismatch: got {len(qual_bowl_ids)}, expected 292"
    
    # Player metadata
    bat_meta = get_player_metadata(bat_faced, 'striker_id', 'striker_name', 'team_name', 'format')
    bowl_meta = get_player_metadata(bowl, 'bowler_id', 'bowler_name', 'team_name', 'format')

    # --------------------------------------------------------------------------
    # 3. Calculate Final Batting Scores (Official alpha = 1.00, K = 600)
    # --------------------------------------------------------------------------
    print("\n[Stage 3] Calculating Final Batting Scores (PWSVA, alpha=1.00, K_bat=600)...")
    bat_faced['w_100'] = bat_faced['pressure_batting'] / 50.0
    bat_faced['wv_100'] = bat_faced['v_bat'] * bat_faced['w_100']
    
    bat_agg = bat_faced.groupby('striker_id').agg(
        n_raw=('v_bat', 'count'),
        sum_w=('w_100', 'sum'),
        sum_w2=('w_100', lambda x: (x**2).sum()),
        sum_wv=('wv_100', 'sum')
    )
    bat_agg['n_p50'] = bat_agg.index.map(bat_p50_counts).fillna(0).astype(int)
    bat_agg['n_eff'] = (bat_agg['sum_w']**2) / bat_agg['sum_w2']
    bat_agg['raw_score'] = bat_agg['sum_wv'] / bat_agg['sum_w']
    bat_agg['shrunk_score'] = (bat_agg['n_eff'] / (bat_agg['n_eff'] + 600.0)) * bat_agg['raw_score']
    
    # Filter to eligible batters
    bat_df = bat_agg.loc[qual_bat_ids].copy()
    bat_df['player_name'] = [bat_meta[pid]['player_name'] for pid in bat_df.index]
    bat_df['team_format'] = [bat_meta[pid]['team_format'] for pid in bat_df.index]
    bat_df['primary_team'] = [bat_meta[pid]['primary_team'] for pid in bat_df.index]
    bat_df['formats'] = [bat_meta[pid]['formats'] for pid in bat_df.index]
    
    # Sort descending by shrunk score
    bat_df = bat_df.sort_values('shrunk_score', ascending=False).reset_index()
    bat_df['rank'] = np.arange(1, len(bat_df) + 1)
    
    print(f"Top 5 Batters by PWSVA:\n{bat_df[['rank', 'player_name', 'team_format', 'shrunk_score', 'raw_score', 'n_raw', 'n_eff', 'n_p50']].head(5).to_string(index=False)}")

    # --------------------------------------------------------------------------
    # 4. Calculate Final Bowling Scores (Official alpha = 1.00, K = 500)
    # --------------------------------------------------------------------------
    print("\n[Stage 4] Calculating Final Bowling Scores (SBVA, alpha=1.00, K_bowl=500)...")
    bowl['w_100'] = bowl['pressure_bowling'] / 50.0
    bowl['wv_100'] = bowl['v_bowl'] * bowl['w_100']
    
    bowl_leg = bowl[bowl['is_legal_ball'] == True]
    bowl_leg_agg = bowl_leg.groupby('bowler_id').agg(
        n_leg=('w_100', 'count'),
        sum_w_leg=('w_100', 'sum'),
        sum_w2_leg=('w_100', lambda x: (x**2).sum())
    )
    bowl_tot_agg = bowl.groupby('bowler_id').agg(
        n_raw=('w_100', 'count'),
        sum_wv_tot=('wv_100', 'sum')
    )
    bowl_agg = bowl_leg_agg.join(bowl_tot_agg)
    bowl_agg['n_p50'] = bowl_agg.index.map(bowl_p50_counts).fillna(0).astype(int)
    bowl_agg['n_eff'] = (bowl_agg['sum_w_leg']**2) / bowl_agg['sum_w2_leg']
    bowl_agg['raw_score'] = bowl_agg['sum_wv_tot'] / bowl_agg['sum_w_leg']
    bowl_agg['shrunk_score'] = (bowl_agg['n_eff'] / (bowl_agg['n_eff'] + 500.0)) * bowl_agg['raw_score']
    
    # Filter to eligible bowlers
    bowl_df = bowl_agg.loc[qual_bowl_ids].copy()
    bowl_df['player_name'] = [bowl_meta[pid]['player_name'] for pid in bowl_df.index]
    bowl_df['team_format'] = [bowl_meta[pid]['team_format'] for pid in bowl_df.index]
    bowl_df['primary_team'] = [bowl_meta[pid]['primary_team'] for pid in bowl_df.index]
    bowl_df['formats'] = [bowl_meta[pid]['formats'] for pid in bowl_df.index]
    
    # Sort descending by shrunk score
    bowl_df = bowl_df.sort_values('shrunk_score', ascending=False).reset_index()
    bowl_df['rank'] = np.arange(1, len(bowl_df) + 1)
    
    print(f"Top 5 Bowlers by SBVA:\n{bowl_df[['rank', 'player_name', 'team_format', 'shrunk_score', 'raw_score', 'n_leg', 'n_eff', 'n_p50']].head(5).to_string(index=False)}")

    # --------------------------------------------------------------------------
    # 5. Match-Level Block Bootstrap Uncertainty Analysis (B = 1,000)
    # --------------------------------------------------------------------------
    print("\n[Stage 5] Running Match-Level Block Bootstrap Uncertainty (B=1,000 resamples)...")
    B_REPS = 1000
    all_match_ids = np.sort(bat['match_id'].unique())
    n_matches = len(all_match_ids)
    m_idx_map = {m: idx for idx, m in enumerate(all_match_ids)}
    
    # Pre-aggregate match-level stats for fast resampling
    bat_faced['m_idx'] = bat_faced['match_id'].map(m_idx_map)
    bowl['m_idx'] = bowl['match_id'].map(m_idx_map)
    
    bat_match_agg = bat_faced.groupby(['m_idx', 'striker_id']).agg(
        sw=('w_100', 'sum'),
        sw2=('w_100', lambda x: (x**2).sum()),
        swv=('wv_100', 'sum')
    ).reset_index()
    
    bowl_match_leg = bowl[bowl['is_legal_ball'] == True].groupby(['m_idx', 'bowler_id']).agg(
        sw_leg=('w_100', 'sum'),
        sw2_leg=('w_100', lambda x: (x**2).sum())
    ).reset_index()
    bowl_match_tot = bowl.groupby(['m_idx', 'bowler_id']).agg(
        swv_tot=('wv_100', 'sum')
    ).reset_index()
    bowl_match_agg = bowl_match_leg.merge(bowl_match_tot, on=['m_idx', 'bowler_id'], how='outer').fillna(0.0)
    
    bat_by_m = {m_idx: grp[['striker_id', 'sw', 'sw2', 'swv']].values for m_idx, grp in bat_match_agg.groupby('m_idx')}
    bowl_by_m = {m_idx: grp[['bowler_id', 'sw_leg', 'sw2_leg', 'swv_tot']].values for m_idx, grp in bowl_match_agg.groupby('m_idx')}
    
    bat_id_to_idx = {pid: i for i, pid in enumerate(qual_bat_ids)}
    bowl_id_to_idx = {pid: i for i, pid in enumerate(qual_bowl_ids)}
    
    n_qual_bat = len(qual_bat_ids)
    n_qual_bowl = len(qual_bowl_ids)
    
    bat_boot_scores = np.zeros((B_REPS, n_qual_bat))
    bowl_boot_scores = np.zeros((B_REPS, n_qual_bowl))
    bat_boot_ranks = np.zeros((B_REPS, n_qual_bat), dtype=int)
    bowl_boot_ranks = np.zeros((B_REPS, n_qual_bowl), dtype=int)
    bat_present_counts = np.zeros(n_qual_bat, dtype=int)
    bowl_present_counts = np.zeros(n_qual_bowl, dtype=int)
    
    # Reproducible seed
    rng_boot = np.random.RandomState(42)
    
    print("Simulating 1,000 bootstrap draws...")
    for b in range(B_REPS):
        sample_matches = rng_boot.choice(n_matches, size=n_matches, replace=True)
        m_counts = pd.Series(sample_matches).value_counts()
        
        # Batting
        sw_b = np.zeros(n_qual_bat)
        sw2_b = np.zeros(n_qual_bat)
        swv_b = np.zeros(n_qual_bat)
        
        for m_idx, cnt in m_counts.items():
            if m_idx in bat_by_m:
                dat = bat_by_m[m_idx]
                for row in dat:
                    pid = int(row[0])
                    if pid in bat_id_to_idx:
                        idx = bat_id_to_idx[pid]
                        sw_b[idx] += row[1] * cnt
                        sw2_b[idx] += row[2] * cnt
                        swv_b[idx] += row[3] * cnt
                        
        valid_b = sw_b > 0
        bat_present_counts += valid_b.astype(int)
        
        neff_b = np.zeros(n_qual_bat)
        raw_b = np.zeros(n_qual_bat)
        neff_b[valid_b] = (sw_b[valid_b]**2) / np.maximum(sw2_b[valid_b], 1e-6)
        raw_b[valid_b] = swv_b[valid_b] / sw_b[valid_b]
        shrunk_b = np.zeros(n_qual_bat)
        shrunk_b[valid_b] = (neff_b[valid_b] / (neff_b[valid_b] + 600.0)) * raw_b[valid_b]
        bat_boot_scores[b, :] = shrunk_b
        
        # Calculate ranks in replicate (1 = highest score)
        # scipy rankdata equivalent: descending order
        order_b = np.argsort(-shrunk_b)
        ranks_b = np.empty_like(order_b)
        ranks_b[order_b] = np.arange(1, n_qual_bat + 1)
        bat_boot_ranks[b, :] = ranks_b
        
        # Bowling
        sw_bw = np.zeros(n_qual_bowl)
        sw2_bw = np.zeros(n_qual_bowl)
        swv_bw = np.zeros(n_qual_bowl)
        
        for m_idx, cnt in m_counts.items():
            if m_idx in bowl_by_m:
                dat = bowl_by_m[m_idx]
                for row in dat:
                    pid = int(row[0])
                    if pid in bowl_id_to_idx:
                        idx = bowl_id_to_idx[pid]
                        sw_bw[idx] += row[1] * cnt
                        sw2_bw[idx] += row[2] * cnt
                        swv_bw[idx] += row[3] * cnt
                        
        valid_bw = sw_bw > 0
        bowl_present_counts += valid_bw.astype(int)
        
        neff_bw = np.zeros(n_qual_bowl)
        raw_bw = np.zeros(n_qual_bowl)
        neff_bw[valid_bw] = (sw_bw[valid_bw]**2) / np.maximum(sw2_bw[valid_bw], 1e-6)
        raw_bw[valid_bw] = swv_bw[valid_bw] / sw_bw[valid_bw]
        shrunk_bw = np.zeros(n_qual_bowl)
        shrunk_bw[valid_bw] = (neff_bw[valid_bw] / (neff_bw[valid_bw] + 500.0)) * raw_bw[valid_bw]
        bowl_boot_scores[b, :] = shrunk_bw
        
        order_bw = np.argsort(-shrunk_bw)
        ranks_bw = np.empty_like(order_bw)
        ranks_bw[order_bw] = np.arange(1, n_qual_bowl + 1)
        bowl_boot_ranks[b, :] = ranks_bw

    # Compute bootstrap summary statistics for Batting
    bat_boot_se = np.std(bat_boot_scores, axis=0, ddof=1)
    bat_ci_lower = np.percentile(bat_boot_scores, 2.5, axis=0)
    bat_ci_upper = np.percentile(bat_boot_scores, 97.5, axis=0)
    bat_rank_med = np.median(bat_boot_ranks, axis=0)
    bat_rank_p025 = np.percentile(bat_boot_ranks, 2.5, axis=0)
    bat_rank_p975 = np.percentile(bat_boot_ranks, 97.5, axis=0)
    
    bat_boot_df = pd.DataFrame({
        'striker_id': qual_bat_ids,
        'bootstrap_se': bat_boot_se,
        'ci_lower_95': bat_ci_lower,
        'ci_upper_95': bat_ci_upper,
        'presence_count_1000': bat_present_counts,
        'presence_pct': bat_present_counts / B_REPS * 100.0,
        'rank_median': bat_rank_med,
        'rank_ci_lower': bat_rank_p025,
        'rank_ci_upper': bat_rank_p975
    })
    
    # Compute bootstrap summary statistics for Bowling
    bowl_boot_se = np.std(bowl_boot_scores, axis=0, ddof=1)
    bowl_ci_lower = np.percentile(bowl_boot_scores, 2.5, axis=0)
    bowl_ci_upper = np.percentile(bowl_boot_scores, 97.5, axis=0)
    bowl_rank_med = np.median(bowl_boot_ranks, axis=0)
    bowl_rank_p025 = np.percentile(bowl_boot_ranks, 2.5, axis=0)
    bowl_rank_p975 = np.percentile(bowl_boot_ranks, 97.5, axis=0)
    
    bowl_boot_df = pd.DataFrame({
        'bowler_id': qual_bowl_ids,
        'bootstrap_se': bowl_boot_se,
        'ci_lower_95': bowl_ci_lower,
        'ci_upper_95': bowl_ci_upper,
        'presence_count_1000': bowl_present_counts,
        'presence_pct': bowl_present_counts / B_REPS * 100.0,
        'rank_median': bowl_rank_med,
        'rank_ci_lower': bowl_rank_p025,
        'rank_ci_upper': bowl_rank_p975
    })
    
    # Merge bootstrap metrics into main player tables
    bat_df = bat_df.merge(bat_boot_df, on='striker_id', how='left')
    bowl_df = bowl_df.merge(bowl_boot_df, on='bowler_id', how='left')
    
    print("Bootstrap uncertainty calculation complete.")

    # --------------------------------------------------------------------------
    # 6. Alpha Sensitivity Analysis (alpha = 1.25)
    # --------------------------------------------------------------------------
    print("\n[Stage 6] Running Alpha Sensitivity Analysis (alpha = 1.25 vs alpha = 1.00)...")
    
    # Batting alpha = 1.25
    bat_faced['w_125'] = (bat_faced['pressure_batting'] / 50.0) ** 1.25
    bat_faced['wv_125'] = bat_faced['v_bat'] * bat_faced['w_125']
    bat_sens_agg = bat_faced.groupby('striker_id').agg(
        sum_w=('w_125', 'sum'),
        sum_w2=('w_125', lambda x: (x**2).sum()),
        sum_wv=('wv_125', 'sum')
    )
    bat_sens_agg['n_eff_125'] = (bat_sens_agg['sum_w']**2) / bat_sens_agg['sum_w2']
    bat_sens_agg['raw_score_125'] = bat_sens_agg['sum_wv'] / bat_sens_agg['sum_w']
    bat_sens_agg['shrunk_score_125'] = (bat_sens_agg['n_eff_125'] / (bat_sens_agg['n_eff_125'] + 600.0)) * bat_sens_agg['raw_score_125']
    
    bat_sens_df = bat_sens_agg.loc[qual_bat_ids].copy().reset_index()
    bat_sens_df['player_name'] = [bat_meta[pid]['player_name'] for pid in bat_sens_df['striker_id']]
    bat_sens_df['team_format'] = [bat_meta[pid]['team_format'] for pid in bat_sens_df['striker_id']]
    bat_sens_df = bat_sens_df.sort_values('shrunk_score_125', ascending=False).reset_index(drop=True)
    bat_sens_df['rank_alpha_125'] = np.arange(1, len(bat_sens_df) + 1)
    
    # Bowling alpha = 1.25
    bowl['w_125'] = (bowl['pressure_bowling'] / 50.0) ** 1.25
    bowl['wv_125'] = bowl['v_bowl'] * bowl['w_125']
    bowl_sens_leg = bowl[bowl['is_legal_ball'] == True].groupby('bowler_id').agg(
        sum_w_leg=('w_125', 'sum'),
        sum_w2_leg=('w_125', lambda x: (x**2).sum())
    )
    bowl_sens_tot = bowl.groupby('bowler_id').agg(
        sum_wv_tot=('wv_125', 'sum')
    )
    bowl_sens_agg = bowl_sens_leg.join(bowl_sens_tot)
    bowl_sens_agg['n_eff_125'] = (bowl_sens_agg['sum_w_leg']**2) / bowl_sens_agg['sum_w2_leg']
    bowl_sens_agg['raw_score_125'] = bowl_sens_agg['sum_wv_tot'] / bowl_sens_agg['sum_w_leg']
    bowl_sens_agg['shrunk_score_125'] = (bowl_sens_agg['n_eff_125'] / (bowl_sens_agg['n_eff_125'] + 500.0)) * bowl_sens_agg['raw_score_125']
    
    bowl_sens_df = bowl_sens_agg.loc[qual_bowl_ids].copy().reset_index()
    bowl_sens_df['player_name'] = [bowl_meta[pid]['player_name'] for pid in bowl_sens_df['bowler_id']]
    bowl_sens_df['team_format'] = [bowl_meta[pid]['team_format'] for pid in bowl_sens_df['bowler_id']]
    bowl_sens_df = bowl_sens_df.sort_values('shrunk_score_125', ascending=False).reset_index(drop=True)
    bowl_sens_df['rank_alpha_125'] = np.arange(1, len(bowl_sens_df) + 1)
    
    # Merge sensitivity ranks into main tables
    bat_df = bat_df.merge(bat_sens_df[['striker_id', 'rank_alpha_125', 'shrunk_score_125', 'n_eff_125']], on='striker_id', how='left')
    bowl_df = bowl_df.merge(bowl_sens_df[['bowler_id', 'rank_alpha_125', 'shrunk_score_125', 'n_eff_125']], on='bowler_id', how='left')
    
    bat_df['rank_delta_alpha'] = bat_df['rank'] - bat_df['rank_alpha_125']
    bowl_df['rank_delta_alpha'] = bowl_df['rank'] - bowl_df['rank_alpha_125']
    
    # Calculate Spearman rank correlations (Pearson corr of integer ranks)
    spearman_bat = float(bat_df['rank'].corr(bat_df['rank_alpha_125']))
    spearman_bowl = float(bowl_df['rank'].corr(bowl_df['rank_alpha_125']))
    
    print(f"Alpha Sensitivity Spearman Rank Correlation: Batting = {spearman_bat:.4f}, Bowling = {spearman_bowl:.4f}")

    # --------------------------------------------------------------------------
    # 7. Quality Checks & Delivery-Level Independent Spot Checks
    # --------------------------------------------------------------------------
    print("\n[Stage 7] Performing Independent Delivery-Level Spot Checks...")
    spot_check_records = []
    
    # Check 3 batters: Rank 1, Rank 15, Rank 150
    sample_bat_ids = [bat_df.iloc[0]['striker_id'], bat_df.iloc[14]['striker_id'], bat_df.iloc[149]['striker_id']]
    for pid in sample_bat_ids:
        row_table = bat_df[bat_df['striker_id'] == pid].iloc[0]
        p_raw = bat_faced[bat_faced['striker_id'] == pid]
        
        calc_n_raw = len(p_raw)
        calc_n_p50 = (p_raw['pressure_batting'] >= 50.0).sum()
        w = p_raw['pressure_batting'] / 50.0
        calc_sw = w.sum()
        calc_sw2 = (w**2).sum()
        calc_neff = (calc_sw**2) / calc_sw2
        calc_swv = (p_raw['v_bat'] * w).sum()
        calc_raw = calc_swv / calc_sw
        calc_shrunk = (calc_neff / (calc_neff + 600.0)) * calc_raw
        
        diff_shrunk = abs(calc_shrunk - row_table['shrunk_score'])
        diff_neff = abs(calc_neff - row_table['n_eff'])
        
        assert diff_shrunk < 1e-9, f"Batting spot check failed for {row_table['player_name']} (shrunk score diff {diff_shrunk})"
        assert diff_neff < 1e-9, f"Batting spot check failed for {row_table['player_name']} (N_eff diff {diff_neff})"
        
        spot_check_records.append({
            'discipline': 'Batting',
            'player_id': int(pid),
            'player_name': row_table['player_name'],
            'official_rank': int(row_table['rank']),
            'table_shrunk': float(row_table['shrunk_score']),
            'recomputed_shrunk': float(calc_shrunk),
            'shrunk_abs_diff': float(diff_shrunk),
            'table_neff': float(row_table['n_eff']),
            'recomputed_neff': float(calc_neff),
            'status': 'PASS'
        })
        print(f"Spot Check Batting: {row_table['player_name']} (Rank {row_table['rank']}) -> Diff: {diff_shrunk:.2e} [PASS]")
        
    # Check 3 bowlers: Rank 1, Rank 15, Rank 150
    sample_bowl_ids = [bowl_df.iloc[0]['bowler_id'], bowl_df.iloc[14]['bowler_id'], bowl_df.iloc[149]['bowler_id']]
    for pid in sample_bowl_ids:
        row_table = bowl_df[bowl_df['bowler_id'] == pid].iloc[0]
        p_raw_all = bowl[bowl['bowler_id'] == pid]
        p_raw_leg = p_raw_all[p_raw_all['is_legal_ball'] == True]
        
        calc_n_raw = len(p_raw_all)
        calc_n_leg = len(p_raw_leg)
        calc_n_p50 = (p_raw_leg['pressure_bowling'] >= 50.0).sum()
        
        w_leg = p_raw_leg['pressure_bowling'] / 50.0
        w_all = p_raw_all['pressure_bowling'] / 50.0
        
        calc_sw_leg = w_leg.sum()
        calc_sw2_leg = (w_leg**2).sum()
        calc_neff = (calc_sw_leg**2) / calc_sw2_leg
        calc_swv_tot = (p_raw_all['v_bowl'] * w_all).sum()
        calc_raw = calc_swv_tot / calc_sw_leg
        calc_shrunk = (calc_neff / (calc_neff + 500.0)) * calc_raw
        
        diff_shrunk = abs(calc_shrunk - row_table['shrunk_score'])
        diff_neff = abs(calc_neff - row_table['n_eff'])
        
        assert diff_shrunk < 1e-9, f"Bowling spot check failed for {row_table['player_name']} (shrunk score diff {diff_shrunk})"
        assert diff_neff < 1e-9, f"Bowling spot check failed for {row_table['player_name']} (N_eff diff {diff_neff})"
        
        spot_check_records.append({
            'discipline': 'Bowling',
            'player_id': int(pid),
            'player_name': row_table['player_name'],
            'official_rank': int(row_table['rank']),
            'table_shrunk': float(row_table['shrunk_score']),
            'recomputed_shrunk': float(calc_shrunk),
            'shrunk_abs_diff': float(diff_shrunk),
            'table_neff': float(row_table['n_eff']),
            'recomputed_neff': float(calc_neff),
            'status': 'PASS'
        })
        print(f"Spot Check Bowling: {row_table['player_name']} (Rank {row_table['rank']}) -> Diff: {diff_shrunk:.2e} [PASS]")

    # --------------------------------------------------------------------------
    # 8. Save Final CSV Deliverables
    # --------------------------------------------------------------------------
    print("\n[Stage 8] Exporting Final Data Tables and Deliverables...")
    
    # Format CI strings for final presentation tables
    bat_df['ci_95_str'] = bat_df.apply(lambda r: f"[{r['ci_lower_95']:.4f}, {r['ci_upper_95']:.4f}]", axis=1)
    bowl_df['ci_95_str'] = bowl_df.apply(lambda r: f"[{r['ci_lower_95']:.4f}, {r['ci_upper_95']:.4f}]", axis=1)
    bat_df['rank_ci_str'] = bat_df.apply(lambda r: f"[{int(r['rank_ci_lower'])}, {int(r['rank_ci_upper'])}]", axis=1)
    bowl_df['rank_ci_str'] = bowl_df.apply(lambda r: f"[{int(r['rank_ci_lower'])}, {int(r['rank_ci_upper'])}]", axis=1)
    
    # Required columns for final presentation
    bat_final_cols = [
        'rank', 'player_name', 'team_format', 'shrunk_score', 'raw_score',
        'n_raw', 'n_eff', 'n_p50', 'bootstrap_se', 'ci_95_str', 'rank_alpha_125'
    ]
    bat_final_rename = {
        'rank': 'Rank',
        'player_name': 'Player',
        'team_format': 'Team/format',
        'shrunk_score': 'Shrunk score',
        'raw_score': 'Raw score',
        'n_raw': 'Raw opportunities',
        'n_eff': 'Kish ESS',
        'n_p50': 'Pressure opportunities',
        'bootstrap_se': 'Bootstrap SE',
        'ci_95_str': '95% CI',
        'rank_alpha_125': 'Alpha 1.25 rank'
    }
    
    bowl_final_cols = [
        'rank', 'player_name', 'team_format', 'shrunk_score', 'raw_score',
        'n_leg', 'n_eff', 'n_p50', 'bootstrap_se', 'ci_95_str', 'rank_alpha_125'
    ]
    bowl_final_rename = {
        'rank': 'Rank',
        'player_name': 'Player',
        'team_format': 'Team/format',
        'shrunk_score': 'Shrunk score',
        'raw_score': 'Raw score',
        'n_leg': 'Raw opportunities',
        'n_eff': 'Kish ESS',
        'n_p50': 'Pressure opportunities',
        'bootstrap_se': 'Bootstrap SE',
        'ci_95_str': '95% CI',
        'rank_alpha_125': 'Alpha 1.25 rank'
    }
    
    # 1. final_batting_rankings.csv (Top 10)
    top10_bat = bat_df.head(10)[bat_final_cols].rename(columns=bat_final_rename)
    top10_bat.to_csv(os.path.join(out_dir, 'final_batting_rankings.csv'), index=False)
    
    # 2. final_bowling_rankings.csv (Top 10)
    top10_bowl = bowl_df.head(10)[bowl_final_cols].rename(columns=bowl_final_rename)
    top10_bowl.to_csv(os.path.join(out_dir, 'final_bowling_rankings.csv'), index=False)
    
    # 3. all_eligible_batting_players.csv (All 297)
    all_bat = bat_df[bat_final_cols].rename(columns=bat_final_rename)
    all_bat.to_csv(os.path.join(out_dir, 'all_eligible_batting_players.csv'), index=False)
    
    # 4. all_eligible_bowling_players.csv (All 292)
    all_bowl = bowl_df[bowl_final_cols].rename(columns=bowl_final_rename)
    all_bowl.to_csv(os.path.join(out_dir, 'all_eligible_bowling_players.csv'), index=False)
    
    # 5. alpha_1_25_batting_sensitivity.csv
    bat_sens_out = bat_df[['rank', 'player_name', 'team_format', 'shrunk_score', 'rank_alpha_125', 'shrunk_score_125', 'rank_delta_alpha']]
    bat_sens_out.to_csv(os.path.join(out_dir, 'alpha_1_25_batting_sensitivity.csv'), index=False)
    
    # 6. alpha_1_25_bowling_sensitivity.csv
    bowl_sens_out = bowl_df[['rank', 'player_name', 'team_format', 'shrunk_score', 'rank_alpha_125', 'shrunk_score_125', 'rank_delta_alpha']]
    bowl_sens_out.to_csv(os.path.join(out_dir, 'alpha_1_25_bowling_sensitivity.csv'), index=False)
    
    # 7. bootstrap_uncertainty_batting.csv
    bat_boot_out = bat_df[['rank', 'player_name', 'shrunk_score', 'bootstrap_se', 'ci_lower_95', 'ci_upper_95', 'presence_count_1000', 'rank_median', 'rank_ci_lower', 'rank_ci_upper']]
    bat_boot_out.to_csv(os.path.join(out_dir, 'bootstrap_uncertainty_batting.csv'), index=False)
    
    # 8. bootstrap_uncertainty_bowling.csv
    bowl_boot_out = bowl_df[['rank', 'player_name', 'shrunk_score', 'bootstrap_se', 'ci_lower_95', 'ci_upper_95', 'presence_count_1000', 'rank_median', 'rank_ci_lower', 'rank_ci_upper']]
    bowl_boot_out.to_csv(os.path.join(out_dir, 'bootstrap_uncertainty_bowling.csv'), index=False)
    
    print("All CSV tables successfully written.")

    # --------------------------------------------------------------------------
    # 9. Generate Visualizations
    # --------------------------------------------------------------------------
    print("\n[Stage 9] Rendering Visualization Figures...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # Figure 1: Top 10 Batting Reliability with 95% Bootstrap CI
    fig, ax = plt.subplots(figsize=(10, 6))
    top10_b = bat_df.head(10).iloc[::-1]  # reverse for horizontal plot
    y_pos = np.arange(len(top10_b))
    
    ax.errorbar(
        top10_b['shrunk_score'], y_pos,
        xerr=[top10_b['shrunk_score'] - top10_b['ci_lower_95'], top10_b['ci_upper_95'] - top10_b['shrunk_score']],
        fmt='o', color='#1f77b4', ecolor='#aec7e8', elinewidth=2.5, capsize=5, capthick=1.5, markersize=8
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{r['rank']} {r['player_name']} ({r['primary_team']})" for _, r in top10_b.iterrows()], fontsize=10)
    ax.set_xlabel("Batting Pressure Reliability (PWSVA Shrunk Score, Runs/Ball)", fontsize=11, fontweight='bold')
    ax.set_title("Top 10 Batting Reliability Under Pressure (with 95% Bootstrap CIs)", fontsize=13, fontweight='bold', pad=12)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.7)
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'top10_batting_reliability.png'), dpi=300)
    plt.close(fig)
    
    # Figure 2: Top 10 Bowling Reliability with 95% Bootstrap CI
    fig, ax = plt.subplots(figsize=(10, 6))
    top10_bw = bowl_df.head(10).iloc[::-1]
    y_pos = np.arange(len(top10_bw))
    
    ax.errorbar(
        top10_bw['shrunk_score'], y_pos,
        xerr=[top10_bw['shrunk_score'] - top10_bw['ci_lower_95'], top10_bw['ci_upper_95'] - top10_bw['shrunk_score']],
        fmt='o', color='#2ca02c', ecolor='#98df8a', elinewidth=2.5, capsize=5, capthick=1.5, markersize=8
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{r['rank']} {r['player_name']} ({r['primary_team']})" for _, r in top10_bw.iterrows()], fontsize=10)
    ax.set_xlabel("Bowling Pressure Reliability (SBVA Shrunk Score, Runs Saved/Ball)", fontsize=11, fontweight='bold')
    ax.set_title("Top 10 Bowling Reliability Under Pressure (with 95% Bootstrap CIs)", fontsize=13, fontweight='bold', pad=12)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.7)
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'top10_bowling_reliability.png'), dpi=300)
    plt.close(fig)
    
    # Figure 3: Full Score Distributions
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.hist(bat_df['shrunk_score'], bins=30, color='#1f77b4', alpha=0.7, edgecolor='black')
    ax1.axvline(0, color='red', linestyle='--', linewidth=1.5)
    ax1.set_title(f"Batting Reliability Distribution (N={len(bat_df)})", fontsize=12, fontweight='bold')
    ax1.set_xlabel("PWSVA Shrunk Score", fontsize=10)
    ax1.set_ylabel("Number of Batters", fontsize=10)
    
    ax2.hist(bowl_df['shrunk_score'], bins=30, color='#2ca02c', alpha=0.7, edgecolor='black')
    ax2.axvline(0, color='red', linestyle='--', linewidth=1.5)
    ax2.set_title(f"Bowling Reliability Distribution (N={len(bowl_df)})", fontsize=12, fontweight='bold')
    ax2.set_xlabel("SBVA Shrunk Score", fontsize=10)
    ax2.set_ylabel("Number of Bowlers", fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'score_distributions.png'), dpi=300)
    plt.close(fig)
    
    # Figure 4: Alpha Sensitivity Scatter (alpha=1.00 vs alpha=1.25)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.scatter(bat_df['shrunk_score'], bat_df['shrunk_score_125'], color='#1f77b4', alpha=0.6, edgecolors='none', s=35)
    ax1.plot([-0.25, 0.45], [-0.25, 0.45], 'k--', alpha=0.6, label='Identity (y=x)')
    ax1.set_title(f"Batting Scores: alpha=1.00 vs alpha=1.25 (r_s = {spearman_bat:.4f})", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Shrunk Score (alpha = 1.00)", fontsize=10)
    ax1.set_ylabel("Shrunk Score (alpha = 1.25)", fontsize=10)
    ax1.legend(loc='lower right')
    
    ax2.scatter(bowl_df['shrunk_score'], bowl_df['shrunk_score_125'], color='#2ca02c', alpha=0.6, edgecolors='none', s=35)
    ax2.plot([-0.30, 0.35], [-0.30, 0.35], 'k--', alpha=0.6, label='Identity (y=x)')
    ax2.set_title(f"Bowling Scores: alpha=1.00 vs alpha=1.25 (r_s = {spearman_bowl:.4f})", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Shrunk Score (alpha = 1.00)", fontsize=10)
    ax2.set_ylabel("Shrunk Score (alpha = 1.25)", fontsize=10)
    ax2.legend(loc='lower right')
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'alpha_sensitivity_scatter.png'), dpi=300)
    plt.close(fig)
    
    print("Visualization figures successfully generated and saved.")

    # --------------------------------------------------------------------------
    # 10. Machine-Readable Validation Summary (JSON)
    # --------------------------------------------------------------------------
    validation_summary = {
        'step': 'Step 7.4',
        'verdict': 'PASS',
        'execution_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'population_counts': {
            'qualifying_batters': len(bat_df),
            'qualifying_bowlers': len(bowl_df),
            'eligibility_rule_batting': 'N(P_bat >= 50) >= 50 balls faced',
            'eligibility_rule_bowling': 'N_leg(P_bowl >= 50) >= 50 legal balls bowled'
        },
        'frozen_parameters': {
            'K_bat': 600,
            'K_bowl': 500,
            'alpha_official': 1.00,
            'alpha_sensitivity': 1.25,
            'bootstrap_replicates': B_REPS,
            'bootstrap_seed': 42
        },
        'top10_batting_summary': [
            {
                'rank': int(r['Rank']),
                'player': r['Player'],
                'team_format': r['Team/format'],
                'shrunk_score': float(r['Shrunk score']),
                'raw_score': float(r['Raw score']),
                'kish_ess': float(r['Kish ESS']),
                'ci_95': r['95% CI'],
                'alpha_125_rank': int(r['Alpha 1.25 rank'])
            }
            for _, r in top10_bat.iterrows()
        ],
        'top10_bowling_summary': [
            {
                'rank': int(r['Rank']),
                'player': r['Player'],
                'team_format': r['Team/format'],
                'shrunk_score': float(r['Shrunk score']),
                'raw_score': float(r['Raw score']),
                'kish_ess': float(r['Kish ESS']),
                'ci_95': r['95% CI'],
                'alpha_125_rank': int(r['Alpha 1.25 rank'])
            }
            for _, r in top10_bowl.iterrows()
        ],
        'alpha_sensitivity_summary': {
            'spearman_batting': float(spearman_bat),
            'spearman_bowling': float(spearman_bowl),
            'batting_top10_overlap': len(set(bat_df.head(10)['striker_id']).intersection(set(bat_sens_df.head(10)['striker_id']))),
            'bowling_top10_overlap': len(set(bowl_df.head(10)['bowler_id']).intersection(set(bowl_sens_df.head(10)['bowler_id'])))
        },
        'spot_checks': spot_check_records
    }
    
    with open(os.path.join(out_dir, 'ranking_validation_results.json'), 'w') as f:
        json.dump(validation_summary, f, indent=2)
        
    print(f"\nStep 7.4 Execution Completed in {time.time() - t_start:.2f} seconds.")

if __name__ == '__main__':
    main()
