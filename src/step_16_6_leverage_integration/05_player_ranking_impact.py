"""
Step 16.6: Script 05 - Player Ranking Impact (BRS3 & BoRS)
=========================================================
Evaluates the secondary impact of each experimental PI candidate on player rankings:
1. Batting: BRS3 formula (45% SR, 35% Survival, 20% Clutch Differential), K = 50.0, Rule B.
2. Bowling: BoRS formula (40% Econ, 25% Wicket, 20% Dot, 15% Econ Differential), K = 50.0, Rule B.
3. Compares Candidate 0 (Control) against Candidates 1A, 1B, 2, and 3:
   - Tier 1 qualification counts and sample sizes
   - Spearman rank correlation against Control
   - Top 10 changes and rank movements
   - Who gains/loses qualifying deliveries across roles

Outputs:
- outputs/step_16_6_leverage_integration/player_ranking_correlation_summary.csv
- outputs/step_16_6_leverage_integration/batting_candidate_rankings_comparison.csv
- outputs/step_16_6_leverage_integration/bowling_candidate_rankings_comparison.csv
- outputs/step_16_6_leverage_integration/top10_movement_comparison.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_6_leverage_integration")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR = Path("data/processed")

K = 50.0
BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']


def calculate_brs3(bat_df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    """Computes player-level BRS3 scores and rankings for all batters."""
    df = bat_df.copy()
    df['is_out'] = (df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])).astype(int)

    df['runs_hp'] = np.where(df[hp_col], df['runs'], 0)
    df['bf_hp'] = np.where(df[hp_col], 1, 0)
    df['out_hp'] = np.where(df[hp_col], df['is_out'], 0)

    df['runs_low'] = np.where(~df[hp_col], df['runs'], 0)
    df['bf_low'] = np.where(~df[hp_col], 1, 0)

    agg = df.groupby('striker_id').agg(
        player_name=('striker_name', 'first'),
        bf_hp=('bf_hp', 'sum'),
        runs_hp=('runs_hp', 'sum'),
        out_hp=('out_hp', 'sum'),
        bf_low=('bf_low', 'sum'),
        runs_low=('runs_low', 'sum')
    ).reset_index()

    hp_matches = df[df[hp_col]].groupby('striker_id')['match_id'].nunique().to_dict()
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

    # Rule B Qualification
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
    """Computes player-level BoRS scores and rankings for all bowlers."""
    df = bowl_df.copy()
    df['is_bowler_wicket'] = (df['is_wicket'] & df['dismissal_type'].isin(BOWLER_WICKET_TYPES)).astype(int)
    df['is_bowler_dot'] = (df['bowler_runs_conceded'] == 0).astype(int)

    df['rc_hp'] = np.where(df[hp_col], df['bowler_runs_conceded'], 0)
    df['lb_hp'] = np.where(df[hp_col], 1, 0)
    df['wk_hp'] = np.where(df[hp_col], df['is_bowler_wicket'], 0)
    df['dot_hp'] = np.where(df[hp_col], df['is_bowler_dot'], 0)

    df['rc_low'] = np.where(~df[hp_col], df['bowler_runs_conceded'], 0)
    df['lb_low'] = np.where(~df[hp_col], 1, 0)

    agg = df.groupby('bowler_id').agg(
        player_name=('bowler_name', 'first'),
        lb_hp=('lb_hp', 'sum'),
        rc_hp=('rc_hp', 'sum'),
        wk_hp=('wk_hp', 'sum'),
        dot_hp=('dot_hp', 'sum'),
        lb_low=('lb_low', 'sum'),
        rc_low=('rc_low', 'sum')
    ).reset_index()

    hp_matches = df[df[hp_col]].groupby('bowler_id')['match_id'].nunique().to_dict()
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

    # Rule B Qualification
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
    print("=== Step 16.6 Script 05: Player Ranking Impact Analysis ===")
    t0 = time.time()

    parquet_path = OUTPUT_DIR / "delivery_candidates_classified.parquet"
    print(f"Loading candidate deliveries dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # Need dismissed_player_id, runs, is_wicket, and bowler_runs_conceded from data/processed
    dms = pd.read_csv(PROCESSED_DIR / "delivery_match_state.csv",
                      usecols=['match_id', 'innings', 'overid', 'innings_ball_num',
                               'runs', 'is_wicket', 'dismissed_player_id', 'dismissal_type', 'bowler_runs_conceded'])
    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    # Drop existing duplicates before merge
    df = df.drop(columns=['runs', 'is_wicket', 'dismissed_player_id', 'dismissal_type', 'bowler_runs_conceded'], errors='ignore')
    df = df.merge(dms[merge_keys + ['runs', 'is_wicket', 'dismissed_player_id', 'dismissal_type', 'bowler_runs_conceded']], on=merge_keys, how='left')

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    candidates = [
        ('Candidate 0 (Control)', 'hp_cand0_bat', 'hp_cand0_bowl'),
        ('Candidate 1A (Additive 70/30)', 'hp_cand1a_bat', 'hp_cand1a_bowl'),
        ('Candidate 1B (Additive 50/50)', 'hp_cand1b_bat', 'hp_cand1b_bowl'),
        ('Candidate 2 (Multiplicative Gated)', 'hp_cand2_bat', 'hp_cand2_bowl'),
        ('Candidate 3 (Convex Composite)', 'hp_cand3_bat', 'hp_cand3_bowl')
    ]

    bat_rankings = {}
    bowl_rankings = {}

    print("\nComputing Batting and Bowling Rankings across all 5 candidates...")
    for c_name, hp_bat_col, hp_bowl_col in candidates:
        print(f"  Calculating {c_name}...")
        bat_rankings[c_name] = calculate_brs3(bat_df, hp_bat_col, c_name)
        bowl_rankings[c_name] = calculate_bors(bowl_df, hp_bowl_col, c_name)

    # 1. BATTING RANKINGS COMPARISON TABLE
    print("\nAssembling Batting Rankings Comparison...")
    ctrl_bat = bat_rankings['Candidate 0 (Control)']
    bat_comp = ctrl_bat[['striker_id', 'player_name', 'tier', 'tier1_rank', 'brs3', 'bf_hp', 'hp_matches']].rename(
        columns={'tier': 'tier_ctrl', 'tier1_rank': 'rank_ctrl', 'brs3': 'brs3_ctrl', 'bf_hp': 'n_ctrl', 'hp_matches': 'm_ctrl'}
    )

    for c_name, _, _ in candidates[1:]:
        c_short = c_name.split(' ')[1]  # 1A, 1B, 2, 3
        sub_r = bat_rankings[c_name][['striker_id', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
            columns={'tier': f'tier_{c_short}', 'tier1_rank': f'rank_{c_short}', 'brs3': f'brs3_{c_short}', 'bf_hp': f'n_{c_short}'}
        )
        bat_comp = bat_comp.merge(sub_r, on='striker_id', how='left')

    out_bat_csv = OUTPUT_DIR / "batting_candidate_rankings_comparison.csv"
    bat_comp.to_csv(out_bat_csv, index=False)
    print(f"Saved batting rankings comparison to {out_bat_csv}")

    # 2. BOWLING RANKINGS COMPARISON TABLE
    print("\nAssembling Bowling Rankings Comparison...")
    ctrl_bowl = bowl_rankings['Candidate 0 (Control)']
    bowl_comp = ctrl_bowl[['bowler_id', 'player_name', 'tier', 'tier1_rank', 'bors', 'lb_hp', 'hp_matches']].rename(
        columns={'tier': 'tier_ctrl', 'tier1_rank': 'rank_ctrl', 'bors': 'bors_ctrl', 'lb_hp': 'n_ctrl', 'hp_matches': 'm_ctrl'}
    )

    for c_name, _, _ in candidates[1:]:
        c_short = c_name.split(' ')[1]
        sub_r = bowl_rankings[c_name][['bowler_id', 'tier', 'tier1_rank', 'bors', 'lb_hp']].rename(
            columns={'tier': f'tier_{c_short}', 'tier1_rank': f'rank_{c_short}', 'bors': f'bors_{c_short}', 'lb_hp': f'n_{c_short}'}
        )
        bowl_comp = bowl_comp.merge(sub_r, on='bowler_id', how='left')

    out_bowl_csv = OUTPUT_DIR / "bowling_candidate_rankings_comparison.csv"
    bowl_comp.to_csv(out_bowl_csv, index=False)
    print(f"Saved bowling rankings comparison to {out_bowl_csv}")

    # 3. CORRELATION & QUALIFICATION SUMMARY
    print("\nComputing Ranking Correlations and Stability Metrics against Control...")
    corr_summary_rows = []

    # Common qualified Tier 1 players in Control
    ctrl_t1_bat_ids = set(ctrl_bat[ctrl_bat['tier'] == 'Tier 1']['striker_id'])
    ctrl_t1_bowl_ids = set(ctrl_bowl[ctrl_bowl['tier'] == 'Tier 1']['bowler_id'])

    for c_name, _, _ in candidates:
        r_bat = bat_rankings[c_name]
        r_bowl = bowl_rankings[c_name]

        t1_bat = (r_bat['tier'] == 'Tier 1').sum()
        t2_bat = (r_bat['tier'] == 'Tier 2').sum()
        t1_bowl = (r_bowl['tier'] == 'Tier 1').sum()
        t2_bowl = (r_bowl['tier'] == 'Tier 2').sum()

        # Batting Rank correlations on common Tier 1 players
        comm_bat = r_bat[r_bat['striker_id'].isin(ctrl_t1_bat_ids) & (r_bat['tier'] == 'Tier 1')]
        ctrl_matched_bat = ctrl_bat[ctrl_bat['striker_id'].isin(comm_bat['striker_id'])].set_index('striker_id').loc[comm_bat['striker_id']]

        sp_bat_rho = np.corrcoef(comm_bat['tier1_rank'].rank(), ctrl_matched_bat['tier1_rank'].rank())[0, 1] if len(comm_bat) > 2 else np.nan
        pr_bat_r = np.corrcoef(comm_bat['brs3'], ctrl_matched_bat['brs3'])[0, 1] if len(comm_bat) > 2 else np.nan

        # Bowling Rank correlations on common Tier 1 players
        comm_bowl = r_bowl[r_bowl['bowler_id'].isin(ctrl_t1_bowl_ids) & (r_bowl['tier'] == 'Tier 1')]
        ctrl_matched_bowl = ctrl_bowl[ctrl_bowl['bowler_id'].isin(comm_bowl['bowler_id'])].set_index('bowler_id').loc[comm_bowl['bowler_id']]

        sp_bowl_rho = np.corrcoef(comm_bowl['tier1_rank'].rank(), ctrl_matched_bowl['tier1_rank'].rank())[0, 1] if len(comm_bowl) > 2 else np.nan
        pr_bowl_r = np.corrcoef(comm_bowl['bors'], ctrl_matched_bowl['bors'])[0, 1] if len(comm_bowl) > 2 else np.nan

        # Top 10 overlap
        top10_ctrl_bat = set(ctrl_bat[ctrl_bat['tier1_rank'] <= 10]['striker_id'])
        top10_cand_bat = set(r_bat[r_bat['tier1_rank'] <= 10]['striker_id'])
        top10_bat_overlap = len(top10_ctrl_bat.intersection(top10_cand_bat))

        top10_ctrl_bowl = set(ctrl_bowl[ctrl_bowl['tier1_rank'] <= 10]['bowler_id'])
        top10_cand_bowl = set(r_bowl[r_bowl['tier1_rank'] <= 10]['bowler_id'])
        top10_bowl_overlap = len(top10_ctrl_bowl.intersection(top10_cand_bowl))

        corr_summary_rows.append({
            'candidate': c_name,
            'batting_tier1_qualified': t1_bat,
            'batting_tier2_qualified': t2_bat,
            'batting_spearman_rho_vs_control': round(sp_bat_rho, 4) if pd.notna(sp_bat_rho) else 1.0000,
            'batting_score_pearson_r': round(pr_bat_r, 4) if pd.notna(pr_bat_r) else 1.0000,
            'batting_top10_overlap_count': top10_bat_overlap,
            'bowling_tier1_qualified': t1_bowl,
            'bowling_tier2_qualified': t2_bowl,
            'bowling_spearman_rho_vs_control': round(sp_bowl_rho, 4) if pd.notna(sp_bowl_rho) else 1.0000,
            'bowling_score_pearson_r': round(pr_bowl_r, 4) if pd.notna(pr_bowl_r) else 1.0000,
            'bowling_top10_overlap_count': top10_bowl_overlap
        })

    df_corr_summary = pd.DataFrame(corr_summary_rows)
    out_corr_csv = OUTPUT_DIR / "player_ranking_correlation_summary.csv"
    df_corr_summary.to_csv(out_corr_csv, index=False)
    print("\nRanking Correlation & Qualification Summary:")
    print(df_corr_summary.to_string())

    # 4. TOP 10 MOVEMENT COMPARISON TABLE
    print("\n--- Top 10 Batters Movement ---")
    top10_ctrl_bat_df = bat_comp[bat_comp['rank_ctrl'] <= 10].sort_values('rank_ctrl')
    print(top10_ctrl_bat_df[['rank_ctrl', 'player_name', 'brs3_ctrl', 'rank_1A', 'brs3_1A', 'rank_1B', 'brs3_1B', 'rank_2', 'brs3_2']].to_string())

    print("\n--- Top 10 Bowlers Movement ---")
    top10_ctrl_bowl_df = bowl_comp[bowl_comp['rank_ctrl'] <= 10].sort_values('rank_ctrl')
    print(top10_ctrl_bowl_df[['rank_ctrl', 'player_name', 'bors_ctrl', 'rank_1A', 'bors_1A', 'rank_1B', 'bors_1B', 'rank_2', 'bors_2']].to_string())

    # Save Top 10 Movement CSV
    top10_bat_rows = top10_ctrl_bat_df[['rank_ctrl', 'player_name', 'brs3_ctrl', 'rank_1A', 'brs3_1A', 'rank_1B', 'brs3_1B', 'rank_2', 'brs3_2', 'rank_3', 'brs3_3']].copy()
    top10_bat_rows['discipline'] = 'Batting'

    top10_bowl_rows = top10_ctrl_bowl_df[['rank_ctrl', 'player_name', 'bors_ctrl', 'rank_1A', 'bors_1A', 'rank_1B', 'bors_1B', 'rank_2', 'bors_2', 'rank_3', 'bors_3']].copy()
    top10_bowl_rows = top10_bowl_rows.rename(columns={'bors_ctrl': 'score_ctrl', 'bors_1A': 'score_1A', 'bors_1B': 'score_1B', 'bors_2': 'score_2', 'bors_3': 'score_3'})
    top10_bat_rows = top10_bat_rows.rename(columns={'brs3_ctrl': 'score_ctrl', 'brs3_1A': 'score_1A', 'brs3_1B': 'score_1B', 'brs3_2': 'score_2', 'brs3_3': 'score_3'})

    top10_all = pd.concat([top10_bat_rows, top10_bowl_rows], ignore_index=True)
    out_top10_csv = OUTPUT_DIR / "top10_movement_comparison.csv"
    top10_all.to_csv(out_top10_csv, index=False)
    print(f"Saved Top 10 movement comparison to {out_top10_csv}")

    print(f"\nExecution completed in {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
