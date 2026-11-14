"""
Step 16.1: Independent Audit - Script 03
Threshold Sensitivity, Rule B Qualification & Historical Consistency
====================================================================
Audits:
1. Threshold Sensitivity:
   - Evaluates a fine grid of Z cutoffs: [0.0, 0.5, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5]
   - Assesses empirical delivery capture %, Tier 1 Rule B counts, and sample depth.
   - Evaluates whether Z > 1.0 is an arbitrary selection or a natural inflection point.
2. Rule B Qualification Counts:
   - Independently recalculates Rule B qualification for Batters and Bowlers:
     * Tier 1 Pathway 1: N >= 60
     * Tier 1 Pathway 2: N >= 50 and M >= 6 (and N < 60)
     * Total Tier 1 (Rule B)
     * Tier 2: N >= 40 and not Tier 1
     * Total Qualified: N >= 40
     * Excluded: N < 40
   - Verifies exact match with Step 16 claims (206 batters, 174 bowlers).
3. Historical Consistency & Temporal Stability:
   - Investigates parameter stability across seasons (2022-2024 vs 2025-2026).
   - Audits prospective vs retrospective data leakage risks.

Exports:
- outputs/step_16_1_independent_audit/threshold_sensitivity_audit.csv
- outputs/step_16_1_independent_audit/qualification_count_audit.csv
- outputs/step_16_1_independent_audit/historical_consistency_audit.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path("data")
PROCESSED_DIR = Path("data/processed")
AUDIT_OUT_DIR = Path("outputs/step_16_1_independent_audit")
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_zscores(df: pd.DataFrame, group_cols: list, val_col: str):
    grouped = df.groupby(group_cols)[val_col]
    means = grouped.transform('mean')
    stds = grouped.transform('std')
    return (df[val_col] - means) / stds


def evaluate_rule_b(df_hp: pd.DataFrame, all_player_ids: np.ndarray, id_col: str, match_col: str):
    """Independently calculates Rule B qualification pathways."""
    # Player-level HP counts
    p_stats = df_hp.groupby(id_col).agg(
        n_balls=('phase', 'count'),
        n_matches=(match_col, 'nunique')
    ).reset_index()

    # Merge with full player list
    full_df = pd.DataFrame({id_col: all_player_ids}).merge(p_stats, on=id_col, how='left')
    full_df['n_balls'] = full_df['n_balls'].fillna(0).astype(int)
    full_df['n_matches'] = full_df['n_matches'].fillna(0).astype(int)

    # Pathway 1: N >= 60
    p1_mask = full_df['n_balls'] >= 60
    # Pathway 2: N in [50, 59] and M >= 6
    p2_mask = (full_df['n_balls'] >= 50) & (full_df['n_balls'] < 60) & (full_df['n_matches'] >= 6)
    
    tier1_mask = p1_mask | p2_mask
    tier2_mask = (full_df['n_balls'] >= 40) & ~tier1_mask
    excluded_mask = full_df['n_balls'] < 40

    return {
        'total_players_in_population': len(full_df),
        'pathway1_n60': int(p1_mask.sum()),
        'pathway2_n50_m6': int(p2_mask.sum()),
        'total_tier1_rule_b': int(tier1_mask.sum()),
        'tier2_count': int(tier2_mask.sum()),
        'total_qualified_n40': int((tier1_mask | tier2_mask).sum()),
        'excluded_count': int(excluded_mask.sum())
    }


def main():
    print("=== Step 16.1 Audit Script 03: Sensitivity, Qualification & Consistency ===")

    # 1. Load active cleaned dataset
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    df = raw_df[~tail_mask].copy()

    # Add match date and season for temporal audit
    matches = pd.read_csv(DATA_DIR / "matches.csv")
    comps = pd.read_csv(DATA_DIR / "competitions.csv")
    m = matches.merge(comps[['comp_id', 'season', 'comp_name', 'match_format']], on='comp_id', how='left')
    df = df.merge(m[['match_id', 'season', 'match_date', 'comp_name', 'match_format']], on='match_id', how='left')

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    all_batters = bat_df['striker_id'].unique()
    all_bowlers = bowl_df['bowler_id'].unique()
    print(f"Total Unique Batters: {len(all_batters)}, Total Unique Bowlers: {len(all_bowlers)}")

    # Compute Approach B Z-scores
    bat_df['z_b'] = compute_zscores(bat_df, ['innings', 'phase'], 'Batting_PI')
    bowl_df['z_b'] = compute_zscores(bowl_df, ['innings', 'phase'], 'Bowling_PI')

    # -------------------------------------------------------------
    # 2. Rule B Qualification Counts Audit
    # -------------------------------------------------------------
    print("\nAuditing Rule B Qualification Counts for Proposed Model (App B Z > 1.0)...")
    bat_hp_z1 = bat_df[bat_df['z_b'] > 1.0]
    bowl_hp_z1 = bowl_df[bowl_df['z_b'] > 1.0]

    bat_qual = evaluate_rule_b(bat_hp_z1, all_batters, 'striker_id', 'match_id')
    bowl_qual = evaluate_rule_b(bowl_hp_z1, all_bowlers, 'bowler_id', 'match_id')

    # Also evaluate Baseline PI > 60 for direct comparison
    bat_hp_base = bat_df[bat_df['Batting_PI'] > 60.0]
    bowl_hp_base = bowl_df[bowl_df['Bowling_PI'] > 60.0]
    bat_qual_base = evaluate_rule_b(bat_hp_base, all_batters, 'striker_id', 'match_id')
    bowl_qual_base = evaluate_rule_b(bowl_hp_base, all_bowlers, 'bowler_id', 'match_id')

    qual_rows = [
        {'discipline': 'Batting', 'model': 'Baseline (PI > 60.0)', **bat_qual_base, 'step16_reported_t1': 146, 't1_diff': bat_qual_base['total_tier1_rule_b'] - 146},
        {'discipline': 'Batting', 'model': 'Proposed (App B Z > 1.0)', **bat_qual, 'step16_reported_t1': 206, 't1_diff': bat_qual['total_tier1_rule_b'] - 206},
        {'discipline': 'Bowling', 'model': 'Baseline (PI > 60.0)', **bowl_qual_base, 'step16_reported_t1': 130, 't1_diff': bowl_qual_base['total_tier1_rule_b'] - 130},
        {'discipline': 'Bowling', 'model': 'Proposed (App B Z > 1.0)', **bowl_qual, 'step16_reported_t1': 174, 't1_diff': bowl_qual['total_tier1_rule_b'] - 174},
    ]

    qual_df = pd.DataFrame(qual_rows)
    out_q_path = AUDIT_OUT_DIR / "qualification_count_audit.csv"
    qual_df.to_csv(out_q_path, index=False)
    print(f"Saved qualification count audit to {out_q_path}")
    print(qual_df[['discipline', 'model', 'pathway1_n60', 'pathway2_n50_m6', 'total_tier1_rule_b', 'tier2_count', 'total_qualified_n40', 'step16_reported_t1', 't1_diff']])

    # -------------------------------------------------------------
    # 3. Fine Grid Threshold Sensitivity Audit
    # -------------------------------------------------------------
    print("\nAuditing Fine Grid Threshold Sensitivity...")
    z_grid = [0.0, 0.5, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5]
    sens_rows = []

    for z_cut in z_grid:
        # Batting
        sub_bat = bat_df[bat_df['z_b'] > z_cut]
        bat_res = evaluate_rule_b(sub_bat, all_batters, 'striker_id', 'match_id')
        bat_capture_pct = (len(sub_bat) / len(bat_df)) * 100.0
        
        # Bowling
        sub_bowl = bowl_df[bowl_df['z_b'] > z_cut]
        bowl_res = evaluate_rule_b(sub_bowl, all_bowlers, 'bowler_id', 'match_id')
        bowl_capture_pct = (len(sub_bowl) / len(bowl_df)) * 100.0

        sens_rows.append({
            'z_threshold': z_cut,
            'batting_hp_deliveries': len(sub_bat),
            'batting_capture_pct': round(bat_capture_pct, 2),
            'batting_tier1_rule_b': bat_res['total_tier1_rule_b'],
            'batting_tier2': bat_res['tier2_count'],
            'batting_total_qualified': bat_res['total_qualified_n40'],
            'bowling_hp_deliveries': len(sub_bowl),
            'bowling_capture_pct': round(bowl_capture_pct, 2),
            'bowling_tier1_rule_b': bowl_res['total_tier1_rule_b'],
            'bowling_tier2': bowl_res['tier2_count'],
            'bowling_total_qualified': bowl_res['total_qualified_n40'],
        })

    sens_df = pd.DataFrame(sens_rows)
    out_sens_path = AUDIT_OUT_DIR / "threshold_sensitivity_audit.csv"
    sens_df.to_csv(out_sens_path, index=False)
    print(f"Saved threshold sensitivity audit to {out_sens_path}")
    print(sens_df)

    # -------------------------------------------------------------
    # 4. Historical Consistency & Temporal Parameter Audit
    # -------------------------------------------------------------
    print("\nAuditing Historical Consistency & Temporal Stability...")
    # Check seasons in dataset
    print("Deliveries by Season:\n", df['season'].value_counts().sort_index())

    # Split into 2022-2024 (Early Era, 3 seasons) vs 2025-2026 (Recent Era, 2 seasons)
    df['season_year'] = df['season'].astype(str).str[:4].astype(int)
    early_mask = df['season_year'].isin([2022, 2023, 2024])
    recent_mask = df['season_year'].isin([2025, 2026])

    early_bat = df[early_mask & (df['is_batter_ball_faced'] == 1)]
    recent_bat = df[recent_mask & (df['is_batter_ball_faced'] == 1)]

    early_bowl = df[early_mask & (df['is_legal_ball'] == 1)]
    recent_bowl = df[recent_mask & (df['is_legal_ball'] == 1)]

    temporal_rows = []
    phases = ['PP', 'Middle', 'Death']

    for disc, (full_s, early_s, recent_s), pi_col in [
        ('Batting', (bat_df, early_bat, recent_bat), 'Batting_PI'),
        ('Bowling', (bowl_df, early_bowl, recent_bowl), 'Bowling_PI')
    ]:
        for inn in [1, 2]:
            for ph in phases:
                m_full = (full_s['innings'] == inn) & (full_s['phase'] == ph)
                m_early = (early_s['innings'] == inn) & (early_s['phase'] == ph)
                m_recent = (recent_s['innings'] == inn) & (recent_s['phase'] == ph)

                mean_full = full_s.loc[m_full, pi_col].mean()
                std_full = full_s.loc[m_full, pi_col].std()

                mean_early = early_s.loc[m_early, pi_col].mean()
                std_early = early_s.loc[m_early, pi_col].std()

                mean_recent = recent_s.loc[m_recent, pi_col].mean()
                std_recent = recent_s.loc[m_recent, pi_col].std()

                diff_mean = mean_recent - mean_early
                diff_std = std_recent - std_early

                temporal_rows.append({
                    'discipline': disc,
                    'innings': inn,
                    'phase': ph,
                    'full_mean': round(mean_full, 4),
                    'full_std': round(std_full, 4),
                    'early_2022_2024_mean': round(mean_early, 4),
                    'early_2022_2024_std': round(std_early, 4),
                    'recent_2025_2026_mean': round(mean_recent, 4),
                    'recent_2025_2026_std': round(std_recent, 4),
                    'mean_drift_recent_minus_early': round(diff_mean, 4),
                    'std_drift_recent_minus_early': round(diff_std, 4),
                    'stability_status': 'STABLE' if abs(diff_mean) < 3.0 and abs(diff_std) < 2.0 else 'MODERATE_DRIFT'
                })

    temporal_df = pd.DataFrame(temporal_rows)
    out_t_path = AUDIT_OUT_DIR / "historical_consistency_audit.csv"
    temporal_df.to_csv(out_t_path, index=False)
    print(f"Saved historical consistency audit to {out_t_path}")
    print(temporal_df[['discipline', 'innings', 'phase', 'full_mean', 'early_2022_2024_mean', 'recent_2025_2026_mean', 'mean_drift_recent_minus_early', 'stability_status']])


if __name__ == "__main__":
    main()
