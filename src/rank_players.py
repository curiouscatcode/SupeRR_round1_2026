"""
SupeRR Selector 2.0: Player Reliability Ranking Engine
======================================================

This script implements the exact finalized model specified in:
`src/ranking_model_design.md`

Outputs:
1. data/processed/batter_reliability_rankings.csv
2. data/processed/bowler_reliability_rankings.csv
3. data/processed/phase_specialist_rankings.csv

Validation:
- Recalculates worked examples for Dhoni and Hasaranga.
- Runs dual-regime sensitivity analysis with and without the 4,177 flagged deliveries.
- Performs rigorous assertions on bounds [0, 100], nulls, and duplicate IDs.
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd

# Add src to path for imports
sys.path.append(str(Path(__file__).resolve().parent))
from evaluate_player_performance import evaluate_batters, evaluate_bowlers, FLAGGED_TARGET_UNDERSTATED_MATCHES

# -------------------------------------------------------------------------
# CONSTANTS & POPULATION PRIORS (from src/ranking_model_design.md)
# -------------------------------------------------------------------------
K = 50.0

# Batting Priors
MU_BAT_SR_HIGH   = 114.0475
MU_BAT_OUT_HIGH  = 7.0859
MU_BAT_BND_HIGH  = 14.1504
MU_BAT_DOT_HIGH  = 44.8431
MU_BAT_SR_LOW    = 143.5157

# Bowling Priors
MU_BOWL_ECON_HIGH = 9.0579
MU_BOWL_WK_HIGH   = 4.8179
MU_BOWL_DOT_HIGH  = 39.3885
MU_BOWL_ECON_LOW  = 8.6426

# Phase Priors
MU_BAT_SR_PP = 108.0109
MU_BAT_SR_MO = 106.2190
MU_BAT_SR_DO = 125.3967

MU_BOWL_ECON_PP = 9.3445
MU_BOWL_WK_PP   = 4.3929
MU_BOWL_ECON_MO = 8.8232
MU_BOWL_WK_MO   = 4.5874
MU_BOWL_ECON_DO = 7.7592
MU_BOWL_WK_DO   = 9.9296


def calculate_batter_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Batter Reliability Score (BRS) and tier rankings."""
    b = df.copy()
    
    # Credibility factors
    b['lambda_high'] = b['high_balls_faced'] / (b['high_balls_faced'] + K)
    b['lambda_low']  = b['low_mod_balls_faced'] / (b['low_mod_balls_faced'] + K)
    
    # Observed rates
    b['sr_obs']  = np.where(b['high_balls_faced'] > 0, (b['high_runs'] / b['high_balls_faced']) * 100.0, MU_BAT_SR_HIGH)
    b['out_obs'] = np.where(b['high_balls_faced'] > 0, (b['high_dismissals'] / b['high_balls_faced']) * 100.0, MU_BAT_OUT_HIGH)
    b['bnd_obs'] = np.where(b['high_balls_faced'] > 0, (b['high_boundaries'] / b['high_balls_faced']) * 100.0, MU_BAT_BND_HIGH)
    b['dot_obs'] = np.where(b['high_balls_faced'] > 0, (b['high_dot_balls'] / b['high_balls_faced']) * 100.0, MU_BAT_DOT_HIGH)
    b['sr_low_obs'] = np.where(b['low_mod_balls_faced'] > 0, (b['low_mod_runs'] / b['low_mod_balls_faced']) * 100.0, MU_BAT_SR_LOW)
    
    # Bayesian estimates
    b['sr_star']   = b['lambda_high'] * b['sr_obs'] + (1.0 - b['lambda_high']) * MU_BAT_SR_HIGH
    b['out_star']  = b['lambda_high'] * b['out_obs'] + (1.0 - b['lambda_high']) * MU_BAT_OUT_HIGH
    b['surv_star'] = 100.0 - b['out_star']
    b['bnd_star']  = b['lambda_high'] * b['bnd_obs'] + (1.0 - b['lambda_high']) * MU_BAT_BND_HIGH
    b['dot_star']  = b['lambda_high'] * b['dot_obs'] + (1.0 - b['lambda_high']) * MU_BAT_DOT_HIGH
    b['exec_star'] = b['bnd_star'] - 0.5 * b['dot_star']
    
    b['sr_low_star']  = b['lambda_low'] * b['sr_low_obs'] + (1.0 - b['lambda_low']) * MU_BAT_SR_LOW
    b['diff_sr_star'] = b['sr_star'] - b['sr_low_star']
    
    # Standardized sub-scores [0, 100]
    b['score_sr']   = np.clip((b['sr_star'] - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    b['score_surv'] = np.clip((b['surv_star'] - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    b['score_exec'] = np.clip((b['exec_star'] + 20.0) / 25.0 * 100.0, 0.0, 100.0)
    b['score_diff'] = np.clip((b['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)
    
    # Composite BRS
    b['brs'] = (0.40 * b['score_sr'] + 
                0.25 * b['score_surv'] + 
                0.20 * b['score_exec'] + 
                0.15 * b['score_diff'])
    
    # Assign qualification tiers
    def assign_tier(bf):
        if bf >= 60:
            return 'Tier 1: Qualified'
        elif bf >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'
            
    b['tier'] = b['high_balls_faced'].apply(assign_tier)
    
    # Assign Ranks within Tiers (1-based, descending by BRS)
    b['tier1_rank'] = np.nan
    t1_mask = b['tier'] == 'Tier 1: Qualified'
    b.loc[t1_mask, 'tier1_rank'] = b.loc[t1_mask, 'brs'].rank(ascending=False, method='min').astype(int)
    
    b['tier2_rank'] = np.nan
    t2_mask = b['tier'] == 'Tier 2: Specialist'
    b.loc[t2_mask, 'tier2_rank'] = b.loc[t2_mask, 'brs'].rank(ascending=False, method='min').astype(int)
    
    # Sort order: Tier 1 ranks, then Tier 2 ranks, then remaining by balls faced
    b = b.sort_values(by=['tier', 'tier1_rank', 'tier2_rank', 'high_balls_faced'], 
                      ascending=[True, True, True, False]).reset_index(drop=True)
    return b


def calculate_bowler_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Bowler Reliability Score (BoRS) and tier rankings."""
    bo = df.copy()
    
    # Credibility factors
    bo['lambda_high'] = bo['high_legal_balls'] / (bo['high_legal_balls'] + K)
    bo['lambda_low']  = bo['low_mod_legal_balls'] / (bo['low_mod_legal_balls'] + K)
    
    # Observed rates
    bo['econ_obs']    = np.where(bo['high_legal_balls'] > 0, (bo['high_runs_conceded'] / bo['high_legal_balls']) * 6.0, MU_BOWL_ECON_HIGH)
    bo['wk_pct_obs']  = np.where(bo['high_legal_balls'] > 0, (bo['high_wickets'] / bo['high_legal_balls']) * 100.0, MU_BOWL_WK_HIGH)
    bo['dot_bo_obs']  = np.where(bo['high_legal_balls'] > 0, (bo['high_dot_balls'] / bo['high_legal_balls']) * 100.0, MU_BOWL_DOT_HIGH)
    bo['econ_low_obs']= np.where(bo['low_mod_legal_balls'] > 0, (bo['low_mod_runs_conceded'] / bo['low_mod_legal_balls']) * 6.0, MU_BOWL_ECON_LOW)
    
    # Bayesian estimates
    bo['econ_star']    = bo['lambda_high'] * bo['econ_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_ECON_HIGH
    bo['wk_star']      = bo['lambda_high'] * bo['wk_pct_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_WK_HIGH
    bo['dot_bo_star']  = bo['lambda_high'] * bo['dot_bo_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_DOT_HIGH
    bo['econ_low_star']= bo['lambda_low'] * bo['econ_low_obs'] + (1.0 - bo['lambda_low']) * MU_BOWL_ECON_LOW
    bo['diff_econ_star']= bo['econ_low_star'] - bo['econ_star']
    
    # Standardized sub-scores [0, 100]
    bo['score_econ'] = np.clip((12.00 - bo['econ_star']) / 6.00 * 100.0, 0.0, 100.0)
    bo['score_wk']   = np.clip((bo['wk_star'] - 1.50) / 7.50 * 100.0, 0.0, 100.0)
    bo['score_dot']  = np.clip((bo['dot_bo_star'] - 25.0) / 25.0 * 100.0, 0.0, 100.0)
    bo['score_diff'] = np.clip((bo['diff_econ_star'] + 3.00) / 5.00 * 100.0, 0.0, 100.0)
    
    # Composite BoRS
    bo['bors'] = (0.40 * bo['score_econ'] + 
                  0.25 * bo['score_wk'] + 
                  0.20 * bo['score_dot'] + 
                  0.15 * bo['score_diff'])
    
    # Qualification tier
    def assign_tier(lb):
        if lb >= 60:
            return 'Tier 1: Qualified'
        elif lb >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'
            
    bo['tier'] = bo['high_legal_balls'].apply(assign_tier)
    
    # Assign Ranks within Tiers (1-based, descending by BoRS)
    bo['tier1_rank'] = np.nan
    t1_mask = bo['tier'] == 'Tier 1: Qualified'
    bo.loc[t1_mask, 'tier1_rank'] = bo.loc[t1_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    
    bo['tier2_rank'] = np.nan
    t2_mask = bo['tier'] == 'Tier 2: Specialist'
    bo.loc[t2_mask, 'tier2_rank'] = bo.loc[t2_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    
    # Sort order
    bo = bo.sort_values(by=['tier', 'tier1_rank', 'tier2_rank', 'high_legal_balls'], 
                        ascending=[True, True, True, False]).reset_index(drop=True)
    return bo


def calculate_phase_specialists(b_df: pd.DataFrame, bo_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate rankings for phase specialists across PP, MO, and DO."""
    phase_records = []
    
    # 1. Batters - Powerplay (N >= 25)
    b_pp = b_df[b_df['bf_pp_high'] >= 25].copy()
    lam_b_pp = b_pp['bf_pp_high'] / (b_pp['bf_pp_high'] + K)
    b_pp['sr_star'] = lam_b_pp * b_pp['pp_high_strike_rate'] + (1 - lam_b_pp) * MU_BAT_SR_PP
    b_pp = b_pp.sort_values('sr_star', ascending=False).reset_index(drop=True)
    for rnk, (_, row) in enumerate(b_pp.iterrows(), start=1):
        phase_records.append({
            'category': 'Batter_Powerplay',
            'phase': 'Powerplay (Overs 1-6)',
            'role': 'Batter',
            'rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['bf_pp_high'],
            'observed_metric': row['pp_high_strike_rate'],
            'metric_label': 'Strike Rate',
            'bayesian_metric': np.round(row['sr_star'], 2),
            'phase_prior': np.round(MU_BAT_SR_PP, 2)
        })

    # 2. Batters - Middle Overs (N >= 30)
    b_mo = b_df[b_df['bf_mo_high'] >= 30].copy()
    lam_b_mo = b_mo['bf_mo_high'] / (b_mo['bf_mo_high'] + K)
    b_mo['sr_star'] = lam_b_mo * b_mo['mo_high_strike_rate'] + (1 - lam_b_mo) * MU_BAT_SR_MO
    b_mo = b_mo.sort_values('sr_star', ascending=False).reset_index(drop=True)
    for rnk, (_, row) in enumerate(b_mo.iterrows(), start=1):
        phase_records.append({
            'category': 'Batter_MiddleOvers',
            'phase': 'Middle Overs (Overs 7-15)',
            'role': 'Batter',
            'rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['bf_mo_high'],
            'observed_metric': row['mo_high_strike_rate'],
            'metric_label': 'Strike Rate',
            'bayesian_metric': np.round(row['sr_star'], 2),
            'phase_prior': np.round(MU_BAT_SR_MO, 2)
        })

    # 3. Batters - Death Overs (N >= 30)
    b_do = b_df[b_df['bf_do_high'] >= 30].copy()
    lam_b_do = b_do['bf_do_high'] / (b_do['bf_do_high'] + K)
    b_do['sr_star'] = lam_b_do * b_do['do_high_strike_rate'] + (1 - lam_b_do) * MU_BAT_SR_DO
    b_do = b_do.sort_values('sr_star', ascending=False).reset_index(drop=True)
    for rnk, (_, row) in enumerate(b_do.iterrows(), start=1):
        phase_records.append({
            'category': 'Batter_DeathOvers',
            'phase': 'Death Overs (Overs 16-20)',
            'role': 'Batter',
            'rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['bf_do_high'],
            'observed_metric': row['do_high_strike_rate'],
            'metric_label': 'Strike Rate',
            'bayesian_metric': np.round(row['sr_star'], 2),
            'phase_prior': np.round(MU_BAT_SR_DO, 2)
        })

    # 4. Bowlers - Powerplay (N >= 30)
    bo_pp = bo_df[bo_df['lb_pp_high'] >= 30].copy()
    lam_bo_pp = bo_pp['lb_pp_high'] / (bo_pp['lb_pp_high'] + K)
    bo_pp['econ_star'] = lam_bo_pp * bo_pp['pp_high_economy_rate'] + (1 - lam_bo_pp) * MU_BOWL_ECON_PP
    bo_pp = bo_pp.sort_values('econ_star', ascending=True).reset_index(drop=True)
    for rnk, (_, row) in enumerate(bo_pp.iterrows(), start=1):
        phase_records.append({
            'category': 'Bowler_Powerplay',
            'phase': 'Powerplay (Overs 1-6)',
            'role': 'Bowler',
            'rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['lb_pp_high'],
            'observed_metric': row['pp_high_economy_rate'],
            'metric_label': 'Economy Rate',
            'bayesian_metric': np.round(row['econ_star'], 2),
            'phase_prior': np.round(MU_BOWL_ECON_PP, 2)
        })

    # 5. Bowlers - Middle Overs (N >= 25)
    bo_mo = bo_df[bo_df['lb_mo_high'] >= 25].copy()
    lam_bo_mo = bo_mo['lb_mo_high'] / (bo_mo['lb_mo_high'] + K)
    bo_mo['econ_star'] = lam_bo_mo * bo_mo['mo_high_economy_rate'] + (1 - lam_bo_mo) * MU_BOWL_ECON_MO
    bo_mo = bo_mo.sort_values('econ_star', ascending=True).reset_index(drop=True)
    for rnk, (_, row) in enumerate(bo_mo.iterrows(), start=1):
        phase_records.append({
            'category': 'Bowler_MiddleOvers',
            'phase': 'Middle Overs (Overs 7-15)',
            'role': 'Bowler',
            'rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['lb_mo_high'],
            'observed_metric': row['mo_high_economy_rate'],
            'metric_label': 'Economy Rate',
            'bayesian_metric': np.round(row['econ_star'], 2),
            'phase_prior': np.round(MU_BOWL_ECON_MO, 2)
        })

    # 6. Bowlers - Death Overs (N >= 15)
    bo_do = bo_df[bo_df['lb_do_high'] >= 15].copy()
    lam_bo_do = bo_do['lb_do_high'] / (bo_do['lb_do_high'] + K)
    bo_do['econ_star'] = lam_bo_do * bo_do['do_high_economy_rate'] + (1 - lam_bo_do) * MU_BOWL_ECON_DO
    bo_do = bo_do.sort_values('econ_star', ascending=True).reset_index(drop=True)
    for rnk, (_, row) in enumerate(bo_do.iterrows(), start=1):
        phase_records.append({
            'category': 'Bowler_DeathOvers',
            'phase': 'Death Overs (Overs 16-20)',
            'role': 'Bowler',
            'rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['lb_do_high'],
            'observed_metric': row['do_high_economy_rate'],
            'metric_label': 'Economy Rate',
            'bayesian_metric': np.round(row['econ_star'], 2),
            'phase_prior': np.round(MU_BOWL_ECON_DO, 2)
        })

    return pd.DataFrame(phase_records)


def run_ranking_pipeline():
    print("=================================================================")
    print("STEP 6.2 — RUNNING PLAYER RELIABILITY RANKING ENGINE")
    print("=================================================================")
    
    # 1. Load Primary Evaluated Performance Datasets
    batters_path = Path("data/processed/batter_performance.csv")
    bowlers_path = Path("data/processed/bowler_performance.csv")
    p_df_path    = Path("data/processed/delivery_pressure_index.csv")
    
    assert batters_path.exists(), f"Missing {batters_path}"
    assert bowlers_path.exists(), f"Missing {bowlers_path}"
    assert p_df_path.exists(), f"Missing {p_df_path}"
    
    batter_df = pd.read_csv(batters_path)
    bowler_df = pd.read_csv(bowlers_path)
    
    print(f"Loaded {len(batter_df)} batters and {len(bowler_df)} bowlers from Step 5 outputs.")
    
    # 2. Calculate Primary Rankings
    print("\nCalculating Primary Player Reliability Rankings...")
    b_ranked = calculate_batter_rankings(batter_df)
    bo_ranked = calculate_bowler_rankings(bowler_df)
    
    # 3. Calculate Phase Specialist Rankings
    print("Calculating Phase Specialist Rankings...")
    phase_ranked = calculate_phase_specialists(batter_df, bowler_df)
    
    # 4. Rigorous Integrity Assertions
    print("\nRunning Model Validation & Integrity Assertions...")
    
    # Check nulls in composite scores
    assert b_ranked['brs'].isnull().sum() == 0, "Null values found in BRS!"
    assert bo_ranked['bors'].isnull().sum() == 0, "Null values found in BoRS!"
    
    # Check bounds [0, 100]
    assert (b_ranked['brs'] >= 0.0).all() and (b_ranked['brs'] <= 100.0).all(), "BRS outside [0, 100]!"
    assert (bo_ranked['bors'] >= 0.0).all() and (bo_ranked['bors'] <= 100.0).all(), "BoRS outside [0, 100]!"
    
    # Check duplicate player IDs
    assert b_ranked['player_id'].duplicated().sum() == 0, "Duplicate player_id in batter rankings!"
    assert bo_ranked['player_id'].duplicated().sum() == 0, "Duplicate player_id in bowler rankings!"
    
    # Check sample counts in tiers
    num_t1_bat = (b_ranked['tier'] == 'Tier 1: Qualified').sum()
    num_t2_bat = (b_ranked['tier'] == 'Tier 2: Specialist').sum()
    num_t1_bo  = (bo_ranked['tier'] == 'Tier 1: Qualified').sum()
    num_t2_bo  = (bo_ranked['tier'] == 'Tier 2: Specialist').sum()
    
    print(f"Batters: Tier 1 Qualified = {num_t1_bat}, Tier 2 Specialist = {num_t2_bat}, Below = {len(b_ranked)-num_t1_bat-num_t2_bat}")
    print(f"Bowlers: Tier 1 Qualified = {num_t1_bo}, Tier 2 Specialist = {num_t2_bo}, Below = {len(bo_ranked)-num_t1_bo-num_t2_bo}")
    
    assert num_t1_bat == 116, f"Expected 116 Tier 1 batters, got {num_t1_bat}"
    assert num_t2_bat == 72, f"Expected 72 Tier 2 batters, got {num_t2_bat}"
    assert num_t1_bo == 113, f"Expected 113 Tier 1 bowlers, got {num_t1_bo}"
    assert num_t2_bo == 36, f"Expected 36 Tier 2 bowlers, got {num_t2_bo}"
    
    # 5. Recalculate Worked Examples Verification
    dhoni = b_ranked[b_ranked['player_name'] == 'Mahendra Singh Dhoni'].iloc[0]
    hasaranga = bo_ranked[bo_ranked['player_name'] == 'Wanindu Hasaranga'].iloc[0]
    
    print(f"\nRecalculated Worked Example 1 — MS Dhoni:")
    print(f"  BF: {dhoni['high_balls_faced']}, SR*: {dhoni['sr_star']:.2f}, Surv*: {dhoni['surv_star']:.2f}%, Exec*: {dhoni['exec_star']:.2f}, Delta*: {dhoni['diff_sr_star']:+.2f}")
    print(f"  Component Scores: SR={dhoni['score_sr']:.2f}, Surv={dhoni['score_surv']:.2f}, Exec={dhoni['score_exec']:.2f}, Diff={dhoni['score_diff']:.2f}")
    print(f"  Composite BRS: {dhoni['brs']:.4f} (Expected: 95.0516) -> Rank: #{int(dhoni['tier1_rank'])}")
    assert abs(dhoni['brs'] - 95.0516) < 0.01, f"Dhoni BRS mismatch: got {dhoni['brs']}"
    
    print(f"\nRecalculated Worked Example 2 — Wanindu Hasaranga:")
    print(f"  LB: {hasaranga['high_legal_balls']}, Econ*: {hasaranga['econ_star']:.2f}, Wk*: {hasaranga['wk_star']:.2f}%, Dot*: {hasaranga['dot_bo_star']:.2f}%, Delta*: {hasaranga['diff_econ_star']:+.2f}")
    print(f"  Component Scores: Econ={hasaranga['score_econ']:.2f}, Wk={hasaranga['score_wk']:.2f}, Dot={hasaranga['score_dot']:.2f}, Diff={hasaranga['score_diff']:.2f}")
    print(f"  Composite BoRS: {hasaranga['bors']:.4f} (Expected: 70.0350) -> Rank: #{int(hasaranga['tier1_rank'])}")
    assert abs(hasaranga['bors'] - 70.0350) < 0.01, f"Hasaranga BoRS mismatch: got {hasaranga['bors']}"
    
    # 6. Sensitivity Analysis (Without 4,177 Flagged Deliveries)
    print("\nRunning Sensitivity Analysis (Excluding 4,177 flagged target-understated deliveries)...")
    p_df = pd.read_csv(p_df_path)
    is_target_reached_tail = (p_df['innings'] == 2) & (p_df['runs_required'] <= 0)
    clean_df = p_df[~is_target_reached_tail].copy()
    clean_df['is_target_understated'] = (clean_df['innings'] == 2) & clean_df['match_id'].isin(FLAGGED_TARGET_UNDERSTATED_MATCHES)
    
    num_flagged = clean_df['is_target_understated'].sum()
    print(f"Reconciled flagged deliveries to exclude: {num_flagged:,}")
    assert num_flagged == 4177, f"Expected 4177 flagged deliveries, got {num_flagged}"
    
    clean_no_tu = clean_df[~clean_df['is_target_understated']].copy()
    b_sens_eval = evaluate_batters(clean_no_tu)
    bo_sens_eval = evaluate_bowlers(clean_no_tu)
    
    b_sens = calculate_batter_rankings(b_sens_eval)
    bo_sens = calculate_bowler_rankings(bo_sens_eval)
    
    # Sensitivity Top 10 Overlap
    top10_b_base = b_ranked[b_ranked['tier'] == 'Tier 1: Qualified'].head(10)['player_name'].tolist()
    top10_b_sens = b_sens[b_sens['tier'] == 'Tier 1: Qualified'].head(10)['player_name'].tolist()
    overlap_b = len(set(top10_b_base).intersection(set(top10_b_sens)))
    
    top10_bo_base = bo_ranked[bo_ranked['tier'] == 'Tier 1: Qualified'].head(10)['player_name'].tolist()
    top10_bo_sens = bo_sens[bo_sens['tier'] == 'Tier 1: Qualified'].head(10)['player_name'].tolist()
    overlap_bo = len(set(top10_bo_base).intersection(set(top10_bo_sens)))
    
    # Spearman rank correlations
    merged_b = pd.merge(b_ranked[b_ranked['tier'] == 'Tier 1: Qualified'][['player_id', 'tier1_rank']],
                        b_sens[b_sens['tier'] == 'Tier 1: Qualified'][['player_id', 'tier1_rank']],
                        on='player_id', suffixes=('_base', '_sens'))
    rho_b = merged_b['tier1_rank_base'].corr(merged_b['tier1_rank_sens'])
    
    merged_bo = pd.merge(bo_ranked[bo_ranked['tier'] == 'Tier 1: Qualified'][['player_id', 'tier1_rank']],
                         bo_sens[bo_sens['tier'] == 'Tier 1: Qualified'][['player_id', 'tier1_rank']],
                         on='player_id', suffixes=('_base', '_sens'))
    rho_bo = merged_bo['tier1_rank_base'].corr(merged_bo['tier1_rank_sens'])
    
    print(f"\nSensitivity Results:")
    print(f"  Batter Top-10 Overlap: {overlap_b}/10 ({overlap_b*10}%) | Spearman Rho (N={len(merged_b)}): {rho_b:.4f}")
    print(f"  Bowler Top-10 Overlap: {overlap_bo}/10 ({overlap_bo*10}%) | Spearman Rho (N={len(merged_bo)}): {rho_bo:.4f}")
    
    assert overlap_b >= 9, "Batter Top-10 overlap below 90%!"
    assert overlap_bo >= 9, "Bowler Top-10 overlap below 90%!"
    assert rho_b >= 0.95, "Batter Spearman rho below 0.95!"
    assert rho_bo >= 0.95, "Bowler Spearman rho below 0.95!"
    
    # 7. Format and Save Artifacts
    print("\nSaving Output CSV Artifacts...")
    
    # Round numerical columns for presentation
    round_cols_bat = ['sr_obs', 'out_obs', 'bnd_obs', 'dot_obs', 'sr_low_obs',
                      'sr_star', 'out_star', 'surv_star', 'bnd_star', 'dot_star', 'exec_star',
                      'sr_low_star', 'diff_sr_star', 'score_sr', 'score_surv', 'score_exec', 'score_diff', 'brs']
    for c in round_cols_bat:
        b_ranked[c] = b_ranked[c].round(2)
        
    round_cols_bowl = ['econ_obs', 'wk_pct_obs', 'dot_bo_obs', 'econ_low_obs',
                       'econ_star', 'wk_star', 'dot_bo_star', 'econ_low_star', 'diff_econ_star',
                       'score_econ', 'score_wk', 'score_dot', 'score_diff', 'bors']
    for c in round_cols_bowl:
        bo_ranked[c] = bo_ranked[c].round(2)
        
    out_b_path = Path("data/processed/batter_reliability_rankings.csv")
    out_bo_path = Path("data/processed/bowler_reliability_rankings.csv")
    out_phase_path = Path("data/processed/phase_specialist_rankings.csv")
    
    b_ranked.to_csv(out_b_path, index=False)
    bo_ranked.to_csv(out_bo_path, index=False)
    phase_ranked.to_csv(out_phase_path, index=False)
    
    print(f"Saved: {out_b_path} ({len(b_ranked)} rows)")
    print(f"Saved: {out_bo_path} ({len(bo_ranked)} rows)")
    print(f"Saved: {out_phase_path} ({len(phase_ranked)} rows)")
    
    print("\n=================================================================")
    print("STEP 6.2 COMPLETED SUCCESSFULLY!")
    print("=================================================================")


if __name__ == '__main__':
    run_ranking_pipeline()
