"""
Step 16.6.1: Script 06 - Independent Player Ranking Reconciliation
===================================================================
Independently calculates and reconciles BRS3 and BoRS player rankings for:
  - Control (Candidate 0)
  - Candidate 2 (Multiplicative Gating, m=0.50)
  - Candidate 1A (Additive 70/30)

Detailed Checks:
1. Exact Tier 1 and Tier 2 qualification counts and sample sizes.
2. Spearman rho and Pearson r correlations.
3. Detailed Top 20 player-by-player movement diagnostics:
   - Number of HP balls in Control vs Cand 2
   - Number of demoted and promoted balls per player
   - Strike rate / economy rate in demoted balls vs retained balls
   - Determining whether ranking movements reflect genuine performance corrections
     (e.g., stripping garbage-time inflation) or artificial delivery churn.

Outputs:
- outputs/step_16_6_1_independent_audit/player_ranking_reconciliation.csv
- outputs/step_16_6_1_independent_audit/batter_rank_movement_diagnostics.csv
- outputs/step_16_6_1_independent_audit/bowler_rank_movement_diagnostics.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_6_1_independent_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STEP_16_6_DIR = Path("outputs/step_16_6_leverage_integration")
PROCESSED_DIR = Path("data/processed")

K = 50.0
BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']


def calculate_brs3(bat_df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    df = bat_df.copy()
    df['is_out'] = (df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])).astype(int)

    df['runs_hp'] = np.where(df[hp_col] == True, df['runs'], 0)
    df['bf_hp'] = np.where(df[hp_col] == True, 1, 0)
    df['out_hp'] = np.where(df[hp_col] == True, df['is_out'], 0)

    df['runs_low'] = np.where(df[hp_col] != True, df['runs'], 0)
    df['bf_low'] = np.where(df[hp_col] != True, 1, 0)

    agg = df.groupby('striker_id').agg(
        player_name=('striker_name', 'first'),
        bf_hp=('bf_hp', 'sum'),
        runs_hp=('runs_hp', 'sum'),
        out_hp=('out_hp', 'sum'),
        bf_low=('bf_low', 'sum'),
        runs_low=('runs_low', 'sum')
    ).reset_index()

    hp_matches = df[df[hp_col] == True].groupby('striker_id')['match_id'].nunique().to_dict()
    agg['hp_matches'] = agg['striker_id'].map(hp_matches).fillna(0).astype(int)

    tot_bf_hp = agg['bf_hp'].sum()
    tot_runs_hp = agg['runs_hp'].sum()
    tot_out_hp = agg['out_hp'].sum()
    tot_bf_low = agg['bf_low'].sum()
    tot_runs_low = agg['runs_low'].sum()

    mu_sr_hp = (tot_runs_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 114.0
    mu_out_hp = (tot_out_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 7.0
    mu_sr_low = (tot_runs_low / tot_bf_low) * 100.0 if tot_bf_low > 0 else 140.0

    agg['lambda_hp'] = agg['bf_hp'] / (agg['bf_hp'] + K)
    agg['lambda_low'] = agg['bf_low'] / (agg['bf_low'] + K)

    agg['sr_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['runs_hp'] / agg['bf_hp']) * 100.0, mu_sr_hp)
    agg['out_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['out_hp'] / agg['bf_hp']) * 100.0, mu_out_hp)
    agg['sr_obs_low'] = np.where(agg['bf_low'] > 0, (agg['runs_low'] / agg['bf_low']) * 100.0, mu_sr_low)

    agg['sr_star'] = agg['lambda_hp'] * agg['sr_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_sr_hp
    agg['out_star'] = agg['lambda_hp'] * agg['out_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_out_hp
    agg['surv_star'] = 100.0 - agg['out_star']
    agg['sr_low_star'] = agg['lambda_low'] * agg['sr_obs_low'] + (1.0 - agg['lambda_low']) * mu_sr_low
    agg['diff_sr_star'] = agg['sr_star'] - agg['sr_low_star']

    agg['score_sr'] = np.clip((agg['sr_star'] - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    agg['score_surv'] = np.clip((agg['surv_star'] - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    agg['score_diff'] = np.clip((agg['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)

    agg['brs3'] = np.round(np.clip(0.45 * agg['score_sr'] + 0.35 * agg['score_surv'] + 0.20 * agg['score_diff'], 0.0, 100.0), 2)

    t1_mask = (agg['bf_hp'] >= 60) | ((agg['bf_hp'] >= 50) & (agg['hp_matches'] >= 6))
    t2_mask = (agg['bf_hp'] >= 40) & ~t1_mask

    agg['tier'] = 'Excluded'
    agg.loc[t2_mask, 'tier'] = 'Tier 2'
    agg.loc[t1_mask, 'tier'] = 'Tier 1'

    agg['tier1_rank'] = np.nan
    agg.loc[t1_mask, 'tier1_rank'] = agg.loc[t1_mask, 'brs3'].rank(ascending=False, method='min').astype(int)
    agg['model'] = model_name
    return agg


def calculate_bors(bowl_df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    df = bowl_df.copy()
    df['is_bowler_wicket'] = (df['is_wicket'] & df['dismissal_type'].isin(BOWLER_WICKET_TYPES)).astype(int)
    df['is_bowler_dot'] = (df['bowler_runs_conceded'] == 0).astype(int)

    df['rc_hp'] = np.where(df[hp_col] == True, df['bowler_runs_conceded'], 0)
    df['lb_hp'] = np.where(df[hp_col] == True, 1, 0)
    df['wk_hp'] = np.where(df[hp_col] == True, df['is_bowler_wicket'], 0)
    df['dot_hp'] = np.where(df[hp_col] == True, df['is_bowler_dot'], 0)

    df['rc_low'] = np.where(df[hp_col] != True, df['bowler_runs_conceded'], 0)
    df['lb_low'] = np.where(df[hp_col] != True, 1, 0)

    agg = df.groupby('bowler_id').agg(
        player_name=('bowler_name', 'first'),
        lb_hp=('lb_hp', 'sum'),
        rc_hp=('rc_hp', 'sum'),
        wk_hp=('wk_hp', 'sum'),
        dot_hp=('dot_hp', 'sum'),
        lb_low=('lb_low', 'sum'),
        rc_low=('rc_low', 'sum')
    ).reset_index()

    hp_matches = df[df[hp_col] == True].groupby('bowler_id')['match_id'].nunique().to_dict()
    agg['hp_matches'] = agg['bowler_id'].map(hp_matches).fillna(0).astype(int)

    tot_hp_balls = agg['lb_hp'].sum()
    tot_hp_rc = agg['rc_hp'].sum()
    tot_hp_wk = agg['wk_hp'].sum()
    tot_hp_dot = agg['dot_hp'].sum()
    tot_low_balls = agg['lb_low'].sum()
    tot_low_rc = agg['rc_low'].sum()

    mu_econ_hp = (tot_hp_rc / tot_hp_balls) * 6.0 if tot_hp_balls > 0 else 8.5
    mu_wk_hp = (tot_hp_wk / tot_hp_balls) * 100.0 if tot_hp_balls > 0 else 5.0
    mu_dot_hp = (tot_hp_dot / tot_hp_balls) * 100.0 if tot_hp_balls > 0 else 35.0
    mu_econ_low = (tot_low_rc / tot_low_balls) * 6.0 if tot_low_balls > 0 else 7.8

    agg['lambda_hp'] = agg['lb_hp'] / (agg['lb_hp'] + K)
    agg['lambda_low'] = agg['lb_low'] / (agg['lb_low'] + K)

    agg['econ_obs'] = np.where(agg['lb_hp'] > 0, (agg['rc_hp'] / agg['lb_hp']) * 6.0, mu_econ_hp)
    agg['wk_pct_obs'] = np.where(agg['lb_hp'] > 0, (agg['wk_hp'] / agg['lb_hp']) * 100.0, mu_wk_hp)
    agg['dot_pct_obs'] = np.where(agg['lb_hp'] > 0, (agg['dot_hp'] / agg['lb_hp']) * 100.0, mu_dot_hp)
    agg['econ_low_obs'] = np.where(agg['lb_low'] > 0, (agg['rc_low'] / agg['lb_low']) * 6.0, mu_econ_low)

    agg['econ_star'] = agg['lambda_hp'] * agg['econ_obs'] + (1.0 - agg['lambda_hp']) * mu_econ_hp
    agg['wk_star'] = agg['lambda_hp'] * agg['wk_pct_obs'] + (1.0 - agg['lambda_hp']) * mu_wk_hp
    agg['dot_star'] = agg['lambda_hp'] * agg['dot_pct_obs'] + (1.0 - agg['lambda_hp']) * mu_dot_hp
    agg['econ_low_star'] = agg['lambda_low'] * agg['econ_low_obs'] + (1.0 - agg['lambda_low']) * mu_econ_low
    agg['diff_econ_star'] = agg['econ_low_star'] - agg['econ_star']

    agg['score_econ'] = np.clip((12.0 - agg['econ_star']) / 6.0 * 100.0, 0.0, 100.0)
    agg['score_wk'] = np.clip((agg['wk_star'] - 1.5) / 7.5 * 100.0, 0.0, 100.0)
    agg['score_dot'] = np.clip((agg['dot_star'] - 25.0) / 25.0 * 100.0, 0.0, 100.0)
    agg['score_diff'] = np.clip((agg['diff_econ_star'] + 3.0) / 5.0 * 100.0, 0.0, 100.0)

    agg['bors'] = np.round(np.clip(
        0.40 * agg['score_econ'] + 0.25 * agg['score_wk'] + 0.20 * agg['score_dot'] + 0.15 * agg['score_diff'],
        0.0, 100.0), 2)

    t1_mask = (agg['lb_hp'] >= 60) | ((agg['lb_hp'] >= 50) & (agg['hp_matches'] >= 6))
    t2_mask = (agg['lb_hp'] >= 40) & ~t1_mask

    agg['tier'] = 'Excluded'
    agg.loc[t2_mask, 'tier'] = 'Tier 2'
    agg.loc[t1_mask, 'tier'] = 'Tier 1'

    agg['tier1_rank'] = np.nan
    agg.loc[t1_mask, 'tier1_rank'] = agg.loc[t1_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    agg['model'] = model_name
    return agg


def main():
    print("=== Step 16.6.1 Script 06: Independent Player Ranking Reconciliation ===")
    t0 = time.time()

    # Load master dataset
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading master delivery dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # Load match state for runs, wickets, dismissal types
    dms_path = PROCESSED_DIR / "delivery_match_state.csv"
    dms_cols = ['match_id', 'innings', 'overid', 'innings_ball_num',
                'runs', 'is_wicket', 'dismissed_player_id', 'dismissal_type', 'bowler_runs_conceded']
    dms_df = pd.read_csv(dms_path, usecols=dms_cols)

    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    df = df.drop(columns=['runs', 'is_wicket', 'dismissed_player_id', 'dismissal_type', 'bowler_runs_conceded'], errors='ignore')
    df = df.merge(dms_df, on=merge_keys, how='left')

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    # Calculate Rankings for Control, Cand 1A, and Cand 2
    print("\nCalculating Batting BRS3 Rankings...")
    bat_ctrl = calculate_brs3(bat_df, 'hp_cand0_bat', 'Control')
    bat_1a = calculate_brs3(bat_df, 'hp_cand1a_bat', 'Cand 1A')
    bat_c2 = calculate_brs3(bat_df, 'hp_cand2_bat', 'Cand 2')

    print("Calculating Bowling BoRS Rankings...")
    bowl_ctrl = calculate_bors(bowl_df, 'hp_cand0_bowl', 'Control')
    bowl_1a = calculate_bors(bowl_df, 'hp_cand1a_bowl', 'Cand 1A')
    bowl_c2 = calculate_bors(bowl_df, 'hp_cand2_bowl', 'Cand 2')

    # 1. Reconciliation Summary Table
    reconciliation_rows = []
    models = [
        ('Candidate 0 (Control)', bat_ctrl, bowl_ctrl),
        ('Candidate 1A (Additive 70/30)', bat_1a, bowl_1a),
        ('Candidate 2 (Multiplicative Gated)', bat_c2, bowl_c2)
    ]

    ctrl_t1_bat = bat_ctrl[bat_ctrl['tier'] == 'Tier 1'].set_index('striker_id')
    ctrl_t1_bowl = bowl_ctrl[bowl_ctrl['tier'] == 'Tier 1'].set_index('bowler_id')
    ctrl_top10_bat_ids = set(ctrl_t1_bat.nsmallest(10, 'tier1_rank').index)
    ctrl_top10_bowl_ids = set(ctrl_t1_bowl.nsmallest(10, 'tier1_rank').index)

    for m_name, b_df, bw_df in models:
        t1_b = b_df[b_df['tier'] == 'Tier 1'].set_index('striker_id')
        t2_b = (b_df['tier'] == 'Tier 2').sum()
        t1_bw = bw_df[bw_df['tier'] == 'Tier 1'].set_index('bowler_id')
        t2_bw = (bw_df['tier'] == 'Tier 2').sum()

        common_b = t1_b.index.intersection(ctrl_t1_bat.index)
        s1_b = ctrl_t1_bat.loc[common_b, 'brs3']
        s2_b = t1_b.loc[common_b, 'brs3']
        rho_b = s1_b.rank().corr(s2_b.rank())
        r_b = s1_b.corr(s2_b)

        common_bw = t1_bw.index.intersection(ctrl_t1_bowl.index)
        s1_bw = ctrl_t1_bowl.loc[common_bw, 'bors']
        s2_bw = t1_bw.loc[common_bw, 'bors']
        rho_bw = s1_bw.rank().corr(s2_bw.rank())
        r_bw = s1_bw.corr(s2_bw)

        top10_b_overlap = len(set(t1_b.nsmallest(10, 'tier1_rank').index).intersection(ctrl_top10_bat_ids))
        top10_bw_overlap = len(set(t1_bw.nsmallest(10, 'tier1_rank').index).intersection(ctrl_top10_bowl_ids))

        reconciliation_rows.append({
            'model_name': m_name,
            'batting_t1_qualified': len(t1_b),
            'batting_t2_qualified': t2_b,
            'batting_spearman_rho': round(rho_b, 4) if not np.isnan(rho_b) else 1.0,
            'batting_pearson_r': round(r_b, 4) if not np.isnan(r_b) else 1.0,
            'batting_top10_overlap': top10_b_overlap,
            'bowling_t1_qualified': len(t1_bw),
            'bowling_t2_qualified': t2_bw,
            'bowling_spearman_rho': round(rho_bw, 4) if not np.isnan(rho_bw) else 1.0,
            'bowling_pearson_r': round(r_bw, 4) if not np.isnan(r_bw) else 1.0,
            'bowling_top10_overlap': top10_bw_overlap
        })

    df_recon = pd.DataFrame(reconciliation_rows)
    recon_csv = OUTPUT_DIR / "player_ranking_reconciliation.csv"
    df_recon.to_csv(recon_csv, index=False)
    print(f"\nSaved player ranking reconciliation summary to {recon_csv}")
    print(df_recon.to_string())

    # 2. Detailed Movement Diagnostics for Batting Top 20
    print("\n--- Diagnostic Audit: Top 20 Control Batters Movement in Candidate 2 ---")
    bat_comp = ctrl_t1_bat.nsmallest(20, 'tier1_rank')[['player_name', 'tier1_rank', 'brs3', 'bf_hp', 'sr_star', 'surv_star', 'diff_sr_star']].copy()
    bat_comp.columns = ['player_name', 'rank_ctrl', 'brs3_ctrl', 'bf_ctrl', 'sr_ctrl', 'surv_ctrl', 'diff_ctrl']

    c2_t1_bat = bat_c2.set_index('striker_id')
    bat_comp['rank_c2'] = bat_comp.index.map(c2_t1_bat['tier1_rank'])
    bat_comp['brs3_c2'] = bat_comp.index.map(c2_t1_bat['brs3'])
    bat_comp['bf_c2'] = bat_comp.index.map(c2_t1_bat['bf_hp'])
    bat_comp['tier_c2'] = bat_comp.index.map(c2_t1_bat['tier'])
    bat_comp['rank_change'] = bat_comp['rank_ctrl'] - bat_comp['rank_c2']

    # For each batter, compute demoted balls count and performance in demoted balls
    movement_diagnostics = []
    for s_id, row in bat_comp.iterrows():
        p_balls = bat_df[bat_df['striker_id'] == s_id]
        ctrl_balls = p_balls[p_balls['hp_cand0_bat'] == True]
        c2_balls = p_balls[p_balls['hp_cand2_bat'] == True]
        demoted_balls = p_balls[(p_balls['hp_cand0_bat'] == True) & (p_balls['hp_cand2_bat'] != True)]
        promoted_balls = p_balls[(p_balls['hp_cand0_bat'] != True) & (p_balls['hp_cand2_bat'] == True)]

        n_demoted = len(demoted_balls)
        n_promoted = len(promoted_balls)

        sr_demoted = (demoted_balls['runs'].sum() / n_demoted * 100.0) if n_demoted > 0 else np.nan
        sr_retained = (c2_balls['runs'].sum() / len(c2_balls) * 100.0) if len(c2_balls) > 0 else np.nan
        m_lev_demoted = demoted_balls['expected_leverage_pct'].mean() if n_demoted > 0 else np.nan

        movement_diagnostics.append({
            'striker_id': s_id,
            'player_name': row['player_name'],
            'rank_ctrl': row['rank_ctrl'],
            'rank_c2': row['rank_c2'],
            'tier_c2': row['tier_c2'],
            'rank_shift': row['rank_change'],
            'brs3_ctrl': row['brs3_ctrl'],
            'brs3_c2': row['brs3_c2'],
            'bf_ctrl': row['bf_ctrl'],
            'bf_c2': row['bf_c2'],
            'balls_demoted': n_demoted,
            'balls_promoted': n_promoted,
            'sr_in_demoted_balls': round(sr_demoted, 1) if pd.notna(sr_demoted) else np.nan,
            'sr_in_c2_hp_balls': round(sr_retained, 1) if pd.notna(sr_retained) else np.nan,
            'mean_lev_demoted_balls': round(m_lev_demoted, 2) if pd.notna(m_lev_demoted) else np.nan
        })

    df_bat_diag = pd.DataFrame(movement_diagnostics)
    bat_diag_csv = OUTPUT_DIR / "batter_rank_movement_diagnostics.csv"
    df_bat_diag.to_csv(bat_diag_csv, index=False)
    print(f"Saved batter movement diagnostics to {bat_diag_csv}")
    print(df_bat_diag[['player_name', 'rank_ctrl', 'rank_c2', 'tier_c2', 'brs3_ctrl', 'brs3_c2', 'bf_ctrl', 'bf_c2', 'balls_demoted', 'sr_in_demoted_balls']].to_string())

    # 3. Detailed Movement Diagnostics for Bowling Top 20
    print("\n--- Diagnostic Audit: Top 20 Control Bowlers Movement in Candidate 2 ---")
    bowl_comp = ctrl_t1_bowl.nsmallest(20, 'tier1_rank')[['player_name', 'tier1_rank', 'bors', 'lb_hp', 'econ_star', 'wk_star']].copy()
    bowl_comp.columns = ['player_name', 'rank_ctrl', 'bors_ctrl', 'lb_ctrl', 'econ_ctrl', 'wk_ctrl']

    c2_t1_bowl = bowl_c2.set_index('bowler_id')
    bowl_comp['rank_c2'] = bowl_comp.index.map(c2_t1_bowl['tier1_rank'])
    bowl_comp['bors_c2'] = bowl_comp.index.map(c2_t1_bowl['bors'])
    bowl_comp['lb_c2'] = bowl_comp.index.map(c2_t1_bowl['lb_hp'])
    bowl_comp['tier_c2'] = bowl_comp.index.map(c2_t1_bowl['tier'])
    bowl_comp['rank_change'] = bowl_comp['rank_ctrl'] - bowl_comp['rank_c2']

    bowl_movement_diagnostics = []
    for b_id, row in bowl_comp.iterrows():
        p_balls = bowl_df[bowl_df['bowler_id'] == b_id]
        ctrl_balls = p_balls[p_balls['hp_cand0_bowl'] == True]
        c2_balls = p_balls[p_balls['hp_cand2_bowl'] == True]
        demoted_balls = p_balls[(p_balls['hp_cand0_bowl'] == True) & (p_balls['hp_cand2_bowl'] != True)]
        promoted_balls = p_balls[(p_balls['hp_cand0_bowl'] != True) & (p_balls['hp_cand2_bowl'] == True)]

        n_demoted = len(demoted_balls)
        n_promoted = len(promoted_balls)

        econ_demoted = (demoted_balls['bowler_runs_conceded'].sum() / n_demoted * 6.0) if n_demoted > 0 else np.nan
        econ_retained = (c2_balls['bowler_runs_conceded'].sum() / len(c2_balls) * 6.0) if len(c2_balls) > 0 else np.nan
        m_lev_demoted = demoted_balls['expected_leverage_pct'].mean() if n_demoted > 0 else np.nan

        bowl_movement_diagnostics.append({
            'bowler_id': b_id,
            'player_name': row['player_name'],
            'rank_ctrl': row['rank_ctrl'],
            'rank_c2': row['rank_c2'],
            'tier_c2': row['tier_c2'],
            'rank_shift': row['rank_change'],
            'bors_ctrl': row['bors_ctrl'],
            'bors_c2': row['bors_c2'],
            'lb_ctrl': row['lb_ctrl'],
            'lb_c2': row['lb_c2'],
            'balls_demoted': n_demoted,
            'balls_promoted': n_promoted,
            'econ_in_demoted_balls': round(econ_demoted, 2) if pd.notna(econ_demoted) else np.nan,
            'econ_in_c2_hp_balls': round(econ_retained, 2) if pd.notna(econ_retained) else np.nan,
            'mean_lev_demoted_balls': round(m_lev_demoted, 2) if pd.notna(m_lev_demoted) else np.nan
        })

    df_bowl_diag = pd.DataFrame(bowl_movement_diagnostics)
    bowl_diag_csv = OUTPUT_DIR / "bowler_rank_movement_diagnostics.csv"
    df_bowl_diag.to_csv(bowl_diag_csv, index=False)
    print(f"Saved bowler movement diagnostics to {bowl_diag_csv}")
    print(df_bowl_diag[['player_name', 'rank_ctrl', 'rank_c2', 'tier_c2', 'bors_ctrl', 'bors_c2', 'lb_ctrl', 'lb_c2', 'balls_demoted']].to_string())

    print(f"\nTotal time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
