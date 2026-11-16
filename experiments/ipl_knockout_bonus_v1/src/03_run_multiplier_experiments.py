"""
Experiment: IPL Knockout Bonus (v1) - Stage 3: Multiplier Experiments
====================================================================
Script: 03_run_multiplier_experiments.py
Purpose: Execute isolated multiplier experiments (1.10x, 1.20x, 1.25x),
         recalculating batting and bowling reliability scores, Kish ESS,
         shrinkage, and rankings across all qualified players.
         Generate comparative analytics, zero-knockout invariance audits,
         figures, and detailed CSV/JSON artifacts.
"""

import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# Output Directory Setup
# ------------------------------------------------------------------------------
BASE_DIR = "experiments/ipl_knockout_bonus_v1"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
COMP_DIR = os.path.join(OUTPUT_DIR, "comparisons")
FIG_DIR = os.path.join(COMP_DIR, "figures")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

for m_str in ["multiplier_1_10", "multiplier_1_20", "multiplier_1_25"]:
    os.makedirs(os.path.join(OUTPUT_DIR, m_str), exist_ok=True)
os.makedirs(COMP_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
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
        primary_team = grp[team_col].value_counts().index[0]
        team_context = f"{primary_team} ({fmt_str})"
        records[pid] = {
            'player_name': name,
            'primary_team': primary_team,
            'formats': fmt_str,
            'team_format': team_context
        }
    return records

def compute_spearman(r1, r2):
    # Pearson correlation on ranks is identical to Spearman
    return float(np.corrcoef(r1, r2)[0, 1])

# ------------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------------
def main():
    t_start = time.time()
    print("================================================================================")
    print("EXPERIMENT: IPL KNOCKOUT BONUS (v1) - RUNNING 1.10x, 1.20x, 1.25x EVALUATION")
    print("================================================================================")

    # 1. 19 Audited Knockout Match IDs
    ko_match_ids = set([
        15187, 15188, 15189, 15190, # 2022
        21583, 21584, 21585,        # 2023 (21586 excluded upstream)
        31289, 31290, 31291, 31292, # 2024
        40764, 40765, 40766, 40767, # 2025
        50942, 50943, 50944, 50945  # 2026
    ])

    # 2. Load Frozen Data & Baselines
    print("\n[Stage 1] Loading frozen datasets and models...")
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
    
    # 36-cell tensor
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
    
    for df in [bat, bowl]:
        is_inn2_non_term = (df['innings'] == 2) & (df['W_rem'] > 1)
        df['lambda_eff'] = df['lambda_wkt'].copy()
        df.loc[is_inn2_non_term, 'lambda_eff'] = np.minimum(df.loc[is_inn2_non_term, 'lambda_wkt'], df.loc[is_inn2_non_term, 'runs_required'])
        
    # Delivery values
    bat_faced = bat[bat['is_batter_ball_faced'] == True].copy()
    bat_faced['v_bat'] = (bat_faced['batter_runs'] - bat_faced['exp_runs']) - bat_faced['lambda_eff'] * (bat_faced['is_striker_dismissed'].astype(float) - bat_faced['exp_striker_dismissal'])
    
    is_leg = bowl['is_legal_ball'] == True
    bowl['v_bowl'] = np.zeros(len(bowl))
    bowl.loc[is_leg, 'v_bowl'] = (bowl.loc[is_leg, 'exp_runs_conceded'] - bowl.loc[is_leg, 'bowler_runs_conceded']) + bowl.loc[is_leg, 'lambda_eff'] * (bowl.loc[is_leg, 'is_bowler_wicket'].astype(float) - bowl.loc[is_leg, 'exp_bowler_wicket'])
    bowl.loc[~is_leg, 'v_bowl'] = - bowl.loc[~is_leg, 'bowler_runs_conceded'] + bowl.loc[~is_leg, 'lambda_eff'] * bowl.loc[~is_leg, 'is_bowler_wicket'].astype(float)

    # 3. Identify Knockout Deliveries
    bat_faced['is_knockout'] = bat_faced['match_id'].isin(ko_match_ids)
    bowl['is_knockout'] = bowl['match_id'].isin(ko_match_ids)

    # 4. Enforce Exact Step 6.2 / Step 7.4 Qualification
    bat_p50 = bat_faced[bat_faced['pressure_batting'] >= 50.0]
    bat_p50_counts = bat_p50.groupby('striker_id').size()
    qual_bat_ids = sorted(bat_p50_counts[bat_p50_counts >= 50].index.tolist())
    
    bowl_leg = bowl[bowl['is_legal_ball'] == True]
    bowl_p50 = bowl_leg[bowl_leg['pressure_bowling'] >= 50.0]
    bowl_p50_counts = bowl_p50.groupby('bowler_id').size()
    qual_bowl_ids = sorted(bowl_p50_counts[bowl_p50_counts >= 50].index.tolist())
    
    assert len(qual_bat_ids) == 297
    assert len(qual_bowl_ids) == 292

    bat_meta = get_player_metadata(bat_faced, 'striker_id', 'striker_name', 'team_name', 'format')
    bowl_meta = get_player_metadata(bowl, 'bowler_id', 'bowler_name', 'team_name', 'format')

    # Calculate Knockout Activity Stats per Player
    bat_ko_stats = bat_faced[bat_faced['is_knockout']].groupby('striker_id').agg(
        ko_balls_faced=('v_bat', 'count'),
        ko_matches=('match_id', 'nunique'),
        ko_p50=('pressure_batting', lambda s: (s >= 50).sum()),
        ko_v_sum=('v_bat', 'sum'),
        ko_v_mean=('v_bat', 'mean')
    )
    bowl_ko_stats = bowl[bowl['is_knockout']].groupby('bowler_id').agg(
        ko_legal_balls=('is_legal_ball', lambda s: (s == True).sum()),
        ko_matches=('match_id', 'nunique'),
        ko_p50=('pressure_bowling', lambda s: (s >= 50).sum()),
        ko_v_sum=('v_bowl', 'sum'),
        ko_v_mean=('v_bowl', 'mean')
    )

    # Load Baseline 1.00x Rankings
    bat_base_df = pd.read_csv(os.path.join(OUTPUT_DIR, "baseline", "baseline_batting_recalculated.csv")).set_index('striker_id')
    bowl_base_df = pd.read_csv(os.path.join(OUTPUT_DIR, "baseline", "baseline_bowling_recalculated.csv")).set_index('bowler_id')

    # --------------------------------------------------------------------------
    # 5. Run Recalculations for Multipliers: 1.10x, 1.20x, 1.25x
    # --------------------------------------------------------------------------
    multipliers = [1.10, 1.20, 1.25]
    bat_results = {1.00: bat_base_df}
    bowl_results = {1.00: bowl_base_df}

    for mult in multipliers:
        m_str = f"multiplier_{f'{mult:.2f}'.replace('.', '_')}"
        print(f"\n[Stage 2] Recalculating scores for Knockout Multiplier {mult:.2f}x ({m_str})...")
        
        # --- Batting Recalculation ---
        # Weights: (P / 50) * mult if knockout else (P / 50) * 1.00
        mult_factors_bat = np.where(bat_faced['is_knockout'], mult, 1.00)
        bat_faced['w_m'] = (bat_faced['pressure_batting'] / 50.0) * mult_factors_bat
        bat_faced['wv_m'] = bat_faced['v_bat'] * bat_faced['w_m']
        
        b_agg = bat_faced.groupby('striker_id').agg(
            n_raw=('v_bat', 'count'),
            sum_w=('w_m', 'sum'),
            sum_w2=('w_m', lambda x: (x**2).sum()),
            sum_wv=('wv_m', 'sum')
        )
        b_agg['n_p50'] = b_agg.index.map(bat_p50_counts).fillna(0).astype(int)
        b_agg['n_eff'] = (b_agg['sum_w']**2) / b_agg['sum_w2']
        b_agg['raw_score'] = b_agg['sum_wv'] / b_agg['sum_w']
        b_agg['shrunk_score'] = (b_agg['n_eff'] / (b_agg['n_eff'] + 600.0)) * b_agg['raw_score']
        
        b_df = b_agg.loc[qual_bat_ids].copy()
        b_df['player_name'] = [bat_meta[pid]['player_name'] for pid in b_df.index]
        b_df['team_format'] = [bat_meta[pid]['team_format'] for pid in b_df.index]
        b_df = b_df.sort_values('shrunk_score', ascending=False)
        b_df['rank'] = np.arange(1, len(b_df) + 1)
        
        # Save rankings
        tag = f"{mult:.2f}".replace('.', '_')
        csv_bat_path = os.path.join(OUTPUT_DIR, m_str, f"batting_rankings_{tag}.csv")
        b_df.reset_index().to_csv(csv_bat_path, index=False)
        bat_results[mult] = b_df
        print(f"  -> Batting {mult:.2f}x: Saved {len(b_df)} players to {csv_bat_path}")

        # --- Bowling Recalculation ---
        mult_factors_bowl = np.where(bowl['is_knockout'], mult, 1.00)
        bowl['w_m'] = (bowl['pressure_bowling'] / 50.0) * mult_factors_bowl
        bowl['wv_m'] = bowl['v_bowl'] * bowl['w_m']
        
        bowl_leg_m = bowl[bowl['is_legal_ball'] == True]
        bw_leg_agg = bowl_leg_m.groupby('bowler_id').agg(
            n_leg=('w_m', 'count'),
            sum_w_leg=('w_m', 'sum'),
            sum_w2_leg=('w_m', lambda x: (x**2).sum())
        )
        bw_tot_agg = bowl.groupby('bowler_id').agg(
            n_raw=('w_m', 'count'),
            sum_wv_tot=('wv_m', 'sum')
        )
        bw_agg = bw_leg_agg.join(bw_tot_agg)
        bw_agg['n_p50'] = bw_agg.index.map(bowl_p50_counts).fillna(0).astype(int)
        bw_agg['n_eff'] = (bw_agg['sum_w_leg']**2) / bw_agg['sum_w2_leg']
        bw_agg['raw_score'] = bw_agg['sum_wv_tot'] / bw_agg['sum_w_leg']
        bw_agg['shrunk_score'] = (bw_agg['n_eff'] / (bw_agg['n_eff'] + 500.0)) * bw_agg['raw_score']
        
        bw_df = bw_agg.loc[qual_bowl_ids].copy()
        bw_df['player_name'] = [bowl_meta[pid]['player_name'] for pid in bw_df.index]
        bw_df['team_format'] = [bowl_meta[pid]['team_format'] for pid in bw_df.index]
        bw_df = bw_df.sort_values('shrunk_score', ascending=False)
        bw_df['rank'] = np.arange(1, len(bw_df) + 1)
        
        # Save rankings
        csv_bowl_path = os.path.join(OUTPUT_DIR, m_str, f"bowling_rankings_{tag}.csv")
        bw_df.reset_index().to_csv(csv_bowl_path, index=False)
        bowl_results[mult] = bw_df
        print(f"  -> Bowling {mult:.2f}x: Saved {len(bw_df)} players to {csv_bowl_path}")

    # --------------------------------------------------------------------------
    # 6. Comparative Analytics & Safeguard Audits
    # --------------------------------------------------------------------------
    print("\n[Stage 3] Generating comparative matrices and auditing safeguards...")

    # A. Build Master Comparison Tables
    # Batting comparison
    bat_comp_rows = []
    for pid in qual_bat_ids:
        p_name = bat_meta[pid]['player_name']
        team_fmt = bat_meta[pid]['team_format']
        
        # Knockout stats
        ko_m = bat_ko_stats.loc[pid, 'ko_matches'] if pid in bat_ko_stats.index else 0
        ko_balls = bat_ko_stats.loc[pid, 'ko_balls_faced'] if pid in bat_ko_stats.index else 0
        ko_p50 = bat_ko_stats.loc[pid, 'ko_p50'] if pid in bat_ko_stats.index else 0
        ko_vmean = bat_ko_stats.loc[pid, 'ko_v_mean'] if pid in bat_ko_stats.index else 0.0
        
        r0 = bat_results[1.00].loc[pid]
        r10 = bat_results[1.10].loc[pid]
        r20 = bat_results[1.20].loc[pid]
        r25 = bat_results[1.25].loc[pid]
        
        bat_comp_rows.append({
            'striker_id': pid,
            'player_name': p_name,
            'team_format': team_fmt,
            'ko_matches': int(ko_m),
            'ko_balls_faced': int(ko_balls),
            'ko_p50_opps': int(ko_p50),
            'ko_mean_value_added': float(ko_vmean),
            'rank_base': int(r0['rank']),
            'shrunk_base': float(r0['shrunk_score']),
            'raw_base': float(r0['raw_score']),
            'ess_base': float(r0['n_eff']),
            'rank_1_10': int(r10['rank']),
            'shrunk_1_10': float(r10['shrunk_score']),
            'delta_rank_1_10': int(r0['rank'] - r10['rank']),
            'delta_score_1_10': float(r10['shrunk_score'] - r0['shrunk_score']),
            'rank_1_20': int(r20['rank']),
            'shrunk_1_20': float(r20['shrunk_score']),
            'delta_rank_1_20': int(r0['rank'] - r20['rank']),
            'delta_score_1_20': float(r20['shrunk_score'] - r0['shrunk_score']),
            'delta_ess_1_20': float(r20['n_eff'] - r0['n_eff']),
            'rank_1_25': int(r25['rank']),
            'shrunk_1_25': float(r25['shrunk_score']),
            'delta_rank_1_25': int(r0['rank'] - r25['rank']),
            'delta_score_1_25': float(r25['shrunk_score'] - r0['shrunk_score']),
        })
    df_bat_comp = pd.DataFrame(bat_comp_rows).sort_values(by='rank_base').reset_index(drop=True)
    df_bat_comp.to_csv(os.path.join(COMP_DIR, "batting_multipliers_comparison.csv"), index=False)
    print(f"Saved batting comparison to {os.path.join(COMP_DIR, 'batting_multipliers_comparison.csv')}")

    # Bowling comparison
    bowl_comp_rows = []
    for pid in qual_bowl_ids:
        p_name = bowl_meta[pid]['player_name']
        team_fmt = bowl_meta[pid]['team_format']
        
        ko_m = bowl_ko_stats.loc[pid, 'ko_matches'] if pid in bowl_ko_stats.index else 0
        ko_balls = bowl_ko_stats.loc[pid, 'ko_legal_balls'] if pid in bowl_ko_stats.index else 0
        ko_p50 = bowl_ko_stats.loc[pid, 'ko_p50'] if pid in bowl_ko_stats.index else 0
        ko_vmean = bowl_ko_stats.loc[pid, 'ko_v_mean'] if pid in bowl_ko_stats.index else 0.0
        
        r0 = bowl_results[1.00].loc[pid]
        r10 = bowl_results[1.10].loc[pid]
        r20 = bowl_results[1.20].loc[pid]
        r25 = bowl_results[1.25].loc[pid]
        
        bowl_comp_rows.append({
            'bowler_id': pid,
            'player_name': p_name,
            'team_format': team_fmt,
            'ko_matches': int(ko_m),
            'ko_legal_balls': int(ko_balls),
            'ko_p50_opps': int(ko_p50),
            'ko_mean_value_added': float(ko_vmean),
            'rank_base': int(r0['rank']),
            'shrunk_base': float(r0['shrunk_score']),
            'raw_base': float(r0['raw_score']),
            'ess_base': float(r0['n_eff']),
            'rank_1_10': int(r10['rank']),
            'shrunk_1_10': float(r10['shrunk_score']),
            'delta_rank_1_10': int(r0['rank'] - r10['rank']),
            'delta_score_1_10': float(r10['shrunk_score'] - r0['shrunk_score']),
            'rank_1_20': int(r20['rank']),
            'shrunk_1_20': float(r20['shrunk_score']),
            'delta_rank_1_20': int(r0['rank'] - r20['rank']),
            'delta_score_1_20': float(r20['shrunk_score'] - r0['shrunk_score']),
            'delta_ess_1_20': float(r20['n_eff'] - r0['n_eff']),
            'rank_1_25': int(r25['rank']),
            'shrunk_1_25': float(r25['shrunk_score']),
            'delta_rank_1_25': int(r0['rank'] - r25['rank']),
            'delta_score_1_25': float(r25['shrunk_score'] - r0['shrunk_score']),
        })
    df_bowl_comp = pd.DataFrame(bowl_comp_rows).sort_values(by='rank_base').reset_index(drop=True)
    df_bowl_comp.to_csv(os.path.join(COMP_DIR, "bowling_multipliers_comparison.csv"), index=False)
    print(f"Saved bowling comparison to {os.path.join(COMP_DIR, 'bowling_multipliers_comparison.csv')}")

    # B. Zero-Knockout Invariance Audit
    bat_zero_ko = df_bat_comp[df_bat_comp['ko_balls_faced'] == 0]
    bowl_zero_ko = df_bowl_comp[df_bowl_comp['ko_legal_balls'] == 0]
    
    bat_zero_score_diff = bat_zero_ko['delta_score_1_20'].abs().max()
    bowl_zero_score_diff = bowl_zero_ko['delta_score_1_20'].abs().max()
    
    zero_ko_audit = {
        'batting_zero_ko_count': len(bat_zero_ko),
        'batting_zero_ko_max_score_delta': float(bat_zero_score_diff),
        'bowling_zero_ko_count': len(bowl_zero_ko),
        'bowling_zero_ko_max_score_delta': float(bowl_zero_score_diff),
        'status': 'VERIFIED_ZERO_IMPACT' if max(bat_zero_score_diff, bowl_zero_score_diff) < 1e-15 else 'VIOLATION'
    }
    with open(os.path.join(COMP_DIR, "zero_knockout_invariance_audit.json"), "w") as f:
        json.dump(zero_ko_audit, f, indent=2)
    print(f"\nZero-KO Invariance Audit: Batters Max Delta = {bat_zero_score_diff:.2e}, Bowlers Max Delta = {bowl_zero_score_diff:.2e} -> {zero_ko_audit['status']}")

    # C. Spearman Correlations & Top 10 Retention
    sensitivity = {
        'batting': {},
        'bowling': {}
    }
    
    for m in [1.10, 1.20, 1.25]:
        m_tag = f"{m:.2f}".replace('.', '_')
        # Batting
        spearman_bat = compute_spearman(df_bat_comp['rank_base'], df_bat_comp[f'rank_{m_tag}'])
        top10_base_bat = set(df_bat_comp[df_bat_comp['rank_base'] <= 10]['striker_id'])
        top10_exp_bat = set(df_bat_comp[df_bat_comp[f'rank_{m_tag}'] <= 10]['striker_id'])
        retention_bat = len(top10_base_bat.intersection(top10_exp_bat)) / 10.0
        
        # Bowling
        spearman_bowl = compute_spearman(df_bowl_comp['rank_base'], df_bowl_comp[f'rank_{m_tag}'])
        top10_base_bowl = set(df_bowl_comp[df_bowl_comp['rank_base'] <= 10]['bowler_id'])
        top10_exp_bowl = set(df_bowl_comp[df_bowl_comp[f'rank_{m_tag}'] <= 10]['bowler_id'])
        retention_bowl = len(top10_base_bowl.intersection(top10_exp_bowl)) / 10.0
        
        sensitivity['batting'][f"{m:.2f}x"] = {
            'spearman_correlation': spearman_bat,
            'top10_retention_pct': retention_bat * 100.0,
            'max_positive_rank_change': int(df_bat_comp[f'delta_rank_{m_tag}'].max()),
            'max_negative_rank_change': int(df_bat_comp[f'delta_rank_{m_tag}'].min()),
            'mean_abs_score_change': float(df_bat_comp[f'delta_score_{m_tag}'].abs().mean())
        }
        sensitivity['bowling'][f"{m:.2f}x"] = {
            'spearman_correlation': spearman_bowl,
            'top10_retention_pct': retention_bowl * 100.0,
            'max_positive_rank_change': int(df_bowl_comp[f'delta_rank_{m_tag}'].max()),
            'max_negative_rank_change': int(df_bowl_comp[f'delta_rank_{m_tag}'].min()),
            'mean_abs_score_change': float(df_bowl_comp[f'delta_score_{m_tag}'].abs().mean())
        }

    with open(os.path.join(COMP_DIR, "sensitivity_metrics.json"), "w") as f:
        json.dump(sensitivity, f, indent=2)
    print("Saved sensitivity metrics to JSON")

    # D. Top 10 Movement Register (Specifically for 1.20x)
    top10_movement = []
    
    # Batting Top 10 Comparison
    top10_bat_base = df_bat_comp[df_bat_comp['rank_base'] <= 10].sort_values(by='rank_base')
    top10_bat_20 = df_bat_comp[df_bat_comp['rank_1_20'] <= 10].sort_values(by='rank_1_20')
    
    # Bowling Top 10 Comparison
    top10_bowl_base = df_bowl_comp[df_bowl_comp['rank_base'] <= 10].sort_values(by='rank_base')
    top10_bowl_20 = df_bowl_comp[df_bowl_comp['rank_1_20'] <= 10].sort_values(by='rank_1_20')

    # Save largest rank movers
    bat_largest_climbers = df_bat_comp.sort_values(by='delta_rank_1_20', ascending=False).head(10)
    bat_largest_fallers = df_bat_comp.sort_values(by='delta_rank_1_20', ascending=True).head(10)
    bowl_largest_climbers = df_bowl_comp.sort_values(by='delta_rank_1_20', ascending=False).head(10)
    bowl_largest_fallers = df_bowl_comp.sort_values(by='delta_rank_1_20', ascending=True).head(10)

    # --------------------------------------------------------------------------
    # 7. Generate Publication Figures (300 DPI)
    # --------------------------------------------------------------------------
    print("\n[Stage 4] Generating publication-quality figures...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['figure.dpi'] = 300

    # Fig 1: Batting Rank Changes (1.20x vs Baseline)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    # Highlight players with KO appearances vs without
    ko_mask_b = df_bat_comp['ko_balls_faced'] > 0
    ax.scatter(df_bat_comp.loc[~ko_mask_b, 'rank_base'], df_bat_comp.loc[~ko_mask_b, 'delta_rank_1_20'],
               color='#94a3b8', alpha=0.5, s=25, label='Zero KO Deliveries (N=206)')
    ax.scatter(df_bat_comp.loc[ko_mask_b, 'rank_base'], df_bat_comp.loc[ko_mask_b, 'delta_rank_1_20'],
               color='#e11d48', s=50, edgecolor='#0f172a', linewidth=0.8, label='With KO Deliveries (N=91)')
    
    # Annotate Top 10 and largest movers
    for _, r in pd.concat([df_bat_comp.head(10), bat_largest_climbers.head(5)]).drop_duplicates().iterrows():
        if abs(r['delta_rank_1_20']) > 0 or r['rank_base'] <= 5:
            ax.annotate(f"{r['player_name']} (Δ{r['delta_rank_1_20']:+d})",
                        (r['rank_base'], r['delta_rank_1_20']),
                        xytext=(r['rank_base'] + 4, r['delta_rank_1_20'] + 0.3),
                        fontsize=7.5, fontweight='bold', color='#1e293b')
            
    ax.axhline(0, color='black', linestyle='--', linewidth=1.0)
    ax.set_title("Batting Rank Movement under 1.20x Knockout Multiplier (N=297)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Baseline Rank (1 to 297)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Rank Change (Positive = Climbed, Negative = Dropped)", fontsize=11, fontweight='bold')
    ax.legend(frameon=True, loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig01_batting_rank_changes_1_20.png"), dpi=300)
    plt.close()

    # Fig 2: Bowling Rank Changes (1.20x vs Baseline)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ko_mask_bw = df_bowl_comp['ko_legal_balls'] > 0
    ax.scatter(df_bowl_comp.loc[~ko_mask_bw, 'rank_base'], df_bowl_comp.loc[~ko_mask_bw, 'delta_rank_1_20'],
               color='#94a3b8', alpha=0.5, s=25, label='Zero KO Deliveries (N=210)')
    ax.scatter(df_bowl_comp.loc[ko_mask_bw, 'rank_base'], df_bowl_comp.loc[ko_mask_bw, 'delta_rank_1_20'],
               color='#16a34a', s=50, edgecolor='#0f172a', linewidth=0.8, label='With KO Deliveries (N=82)')
    
    for _, r in pd.concat([df_bowl_comp.head(10), bowl_largest_climbers.head(5)]).drop_duplicates().iterrows():
        if abs(r['delta_rank_1_20']) > 0 or r['rank_base'] <= 5:
            ax.annotate(f"{r['player_name']} (Δ{r['delta_rank_1_20']:+d})",
                        (r['rank_base'], r['delta_rank_1_20']),
                        xytext=(r['rank_base'] + 4, r['delta_rank_1_20'] + 0.3),
                        fontsize=7.5, fontweight='bold', color='#1e293b')
            
    ax.axhline(0, color='black', linestyle='--', linewidth=1.0)
    ax.set_title("Bowling Rank Movement under 1.20x Knockout Multiplier (N=292)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Baseline Rank (1 to 292)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Rank Change (Positive = Climbed, Negative = Dropped)", fontsize=11, fontweight='bold')
    ax.legend(frameon=True, loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig02_bowling_rank_changes_1_20.png"), dpi=300)
    plt.close()

    # Fig 3: Sensitivity across 1.10x, 1.20x, 1.25x
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    m_labels = ['1.10x', '1.20x', '1.25x']
    spear_b = [sensitivity['batting'][m]['spearman_correlation'] for m in m_labels]
    spear_bw = [sensitivity['bowling'][m]['spearman_correlation'] for m in m_labels]
    
    ax1.plot(m_labels, spear_b, marker='o', color='#e11d48', linewidth=2, label='Batting (PWSVA)')
    ax1.plot(m_labels, spear_bw, marker='s', color='#16a34a', linewidth=2, label='Bowling (SBVA)')
    ax1.set_ylim(0.990, 1.0005)
    ax1.set_title("Spearman Rank Correlation vs. Baseline", fontsize=11, fontweight='bold')
    ax1.set_ylabel("Spearman Correlation (rho)", fontsize=10, fontweight='bold')
    ax1.legend(frameon=True)
    
    ret_b = [sensitivity['batting'][m]['top10_retention_pct'] for m in m_labels]
    ret_bw = [sensitivity['bowling'][m]['top10_retention_pct'] for m in m_labels]
    
    ax2.plot(m_labels, ret_b, marker='o', color='#e11d48', linewidth=2, label='Batting Top 10 Retention')
    ax2.plot(m_labels, ret_bw, marker='s', color='#16a34a', linewidth=2, label='Bowling Top 10 Retention')
    ax2.set_ylim(85, 105)
    ax2.set_title("Top 10 Retention Rate (%)", fontsize=11, fontweight='bold')
    ax2.set_ylabel("Retention Percentage (%)", fontsize=10, fontweight='bold')
    ax2.legend(frameon=True)

    plt.suptitle("Sensitivity and Robustness Across Multiplier Regimes", fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig03_spearman_and_top10_retention.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # Fig 4: Knockout Exposure vs Rank Delta
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    ko_bat = df_bat_comp[df_bat_comp['ko_balls_faced'] > 0]
    ax1.scatter(ko_bat['ko_balls_faced'], ko_bat['delta_rank_1_20'], color='#e11d48', s=60, edgecolor='#0f172a', alpha=0.8)
    for _, r in ko_bat[ko_bat['delta_rank_1_20'].abs() >= 2].iterrows():
        ax1.annotate(r['player_name'], (r['ko_balls_faced'], r['delta_rank_1_20']),
                     xytext=(r['ko_balls_faced'] + 2, r['delta_rank_1_20'] + 0.1),
                     fontsize=8, fontweight='bold')
    ax1.axhline(0, color='gray', linestyle='--')
    ax1.set_title("Batting: KO Balls Faced vs. Rank Delta (1.20x)", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Knockout Balls Faced", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Rank Change (Delta Rank)", fontsize=10, fontweight='bold')

    ko_bowl = df_bowl_comp[df_bowl_comp['ko_legal_balls'] > 0]
    ax2.scatter(ko_bowl['ko_legal_balls'], ko_bowl['delta_rank_1_20'], color='#16a34a', s=60, edgecolor='#0f172a', alpha=0.8)
    for _, r in ko_bowl[ko_bowl['delta_rank_1_20'].abs() >= 2].iterrows():
        ax2.annotate(r['player_name'], (r['ko_legal_balls'], r['delta_rank_1_20']),
                     xytext=(r['ko_legal_balls'] + 2, r['delta_rank_1_20'] + 0.1),
                     fontsize=8, fontweight='bold')
    ax2.axhline(0, color='gray', linestyle='--')
    ax2.set_title("Bowling: KO Legal Balls vs. Rank Delta (1.20x)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Knockout Legal Balls Bowled", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Rank Change (Delta Rank)", fontsize=10, fontweight='bold')

    plt.suptitle("Knockout Exposure vs. Rank Disruption (1.20x Multiplier)", fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig04_knockout_exposure_vs_rank_delta.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print("Saved all publication figures to figures/")
    print(f"Total script execution time: {time.time() - t_start:.2f}s")

if __name__ == '__main__':
    main()
