"""
Step 16.7: Script 04 - Player Ranking Validation (BRS3 Batting Rankings)
=======================================================================
Calculates and reconciles player-level BRS3 batting rankings across:
  - Candidate 0 (Control)
  - Candidate 1 (Smooth Decay)
  - Candidate 2 (Match-Stakes Context)
  - Candidate 3 (Leverage & Crisis)
  - Candidate 4 (Pure Task Difficulty Ablation)

Fixed Methodology:
- BRS3 formula: 45% SR*, 35% Survival*, 20% Clutch Differential*
- Bayesian shrinkage K = 50.0
- Rule B qualification: >= 60 HP balls OR (>= 50 HP balls & >= 6 HP matches)
- Clean delivery population: 180,839 batting deliveries

Outputs:
- outputs/step_16_7_situational_intensity_redesign/player_ranking_reconciliation.csv
- outputs/step_16_7_situational_intensity_redesign/batting_candidate_rankings_comparison.csv
- outputs/step_16_7_situational_intensity_redesign/top_batters_role_movement.csv
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_7_situational_intensity_redesign")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR = Path("data/processed")

K = 50.0


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


def main():
    print("=== Step 16.7 Script 04: Player Ranking Validation ===")
    t0 = time.time()

    parquet_path = OUTPUT_DIR / "delivery_intensity_candidates.parquet"
    print(f"Loading candidate dataset from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # Load runs, is_wicket, dismissed_player_id from delivery_match_state
    dms_path = PROCESSED_DIR / "delivery_match_state.csv"
    dms = pd.read_csv(dms_path, usecols=['match_id', 'innings', 'overid', 'innings_ball_num',
                                         'runs', 'is_wicket', 'dismissed_player_id'])
    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    df = df.drop(columns=['runs', 'is_wicket', 'dismissed_player_id'], errors='ignore')
    df = df.merge(dms, on=merge_keys, how='left')

    candidates = [
        ('Candidate 0 (Control)', 'HP_cand0'),
        ('Candidate 1 (Smooth Decay)', 'HP_cand1'),
        ('Candidate 2 (Match-Stakes Context)', 'HP_cand2'),
        ('Candidate 3 (Leverage & Crisis)', 'HP_cand3'),
        ('Candidate 4 (Pure Task Difficulty)', 'HP_cand4')
    ]

    bat_rankings = {}
    print("\nComputing BRS3 rankings across all 5 candidate models...")
    for c_name, hp_col in candidates:
        print(f"  Calculating {c_name}...")
        bat_rankings[c_name] = calculate_brs3(df, hp_col, c_name)

    # 1. Reconciliation Table
    ctrl_t1 = bat_rankings['Candidate 0 (Control)'][bat_rankings['Candidate 0 (Control)']['tier'] == 'Tier 1'].set_index('striker_id')
    ctrl_top10_ids = set(ctrl_t1.nsmallest(10, 'tier1_rank').index)

    reconcile_rows = []
    for c_name, _ in candidates:
        m_df = bat_rankings[c_name]
        t1 = m_df[m_df['tier'] == 'Tier 1'].set_index('striker_id')
        t2_count = (m_df['tier'] == 'Tier 2').sum()

        common_ids = t1.index.intersection(ctrl_t1.index)
        s1 = ctrl_t1.loc[common_ids, 'brs3']
        s2 = t1.loc[common_ids, 'brs3']
        rho = s1.rank().corr(s2.rank())
        r = s1.corr(s2)

        top10_ids = set(t1.nsmallest(10, 'tier1_rank').index)
        top10_overlap = len(top10_ids.intersection(ctrl_top10_ids))

        reconcile_rows.append({
            'candidate': c_name,
            'tier1_qualified_batters': len(t1),
            'tier2_qualified_batters': t2_count,
            'spearman_rho_vs_control': round(rho, 4) if not np.isnan(rho) else 1.0,
            'pearson_r_vs_control': round(r, 4) if not np.isnan(r) else 1.0,
            'top10_overlap_with_control': top10_overlap
        })

    df_recon = pd.DataFrame(reconcile_rows)
    recon_csv = OUTPUT_DIR / "player_ranking_reconciliation.csv"
    df_recon.to_csv(recon_csv, index=False)
    print(f"\nSaved player ranking reconciliation to {recon_csv}")
    print(df_recon.to_string())

    # 2. Assembling Master Batting Comparison Table
    ctrl_full = bat_rankings['Candidate 0 (Control)'][['striker_id', 'player_name', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
        columns={'tier': 'tier_ctrl', 'tier1_rank': 'rank_ctrl', 'brs3': 'brs3_ctrl', 'bf_hp': 'bf_ctrl'}
    )

    for c_name, _ in candidates[1:]:
        short = c_name.split(' ')[1]
        sub = bat_rankings[c_name][['striker_id', 'tier', 'tier1_rank', 'brs3', 'bf_hp']].rename(
            columns={'tier': f'tier_{short}', 'tier1_rank': f'rank_{short}', 'brs3': f'brs3_{short}', 'bf_hp': f'bf_{short}'}
        )
        ctrl_full = ctrl_full.merge(sub, on='striker_id', how='left')

    out_bat_csv = OUTPUT_DIR / "batting_candidate_rankings_comparison.csv"
    ctrl_full.to_csv(out_bat_csv, index=False)
    print(f"Saved batting comparison table to {out_bat_csv}")

    # 3. Top-Order and Notable Player Diagnostics
    print("\n--- Diagnostic Audit: Notable Batters across Candidates ---")
    notable_names = [
        'Travis Head', 'Philip Salt', 'Jos Buttler', 'Virat Kohli', 'Rohit Sharma',
        'Yashasvi Jaiswal', 'Suryakumar Yadav', 'Heinrich Klaasen', 'Nicholas Pooran',
        'Shashank Singh', 'Jitesh Sharma', 'Rinku Singh', 'Andre Russell', 'Patrick Cummins'
    ]
    diag_rows = []
    for name in notable_names:
        p_row = ctrl_full[ctrl_full['player_name'] == name]
        if len(p_row) > 0:
            diag_rows.append(p_row.iloc[0].to_dict())

    df_notable = pd.DataFrame(diag_rows)
    notable_csv = OUTPUT_DIR / "top_batters_role_movement.csv"
    df_notable.to_csv(notable_csv, index=False)
    print(f"Saved notable batters diagnostic table to {notable_csv}")
    cols_to_print = ['player_name', 'rank_ctrl', 'brs3_ctrl', 'bf_ctrl',
                     'rank_1', 'brs3_1', 'bf_1',
                     'rank_2', 'brs3_2', 'bf_2',
                     'rank_4', 'brs3_4', 'bf_4']
    print(df_notable[[c for c in cols_to_print if c in df_notable.columns]].to_string())

    print(f"\nTotal time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
