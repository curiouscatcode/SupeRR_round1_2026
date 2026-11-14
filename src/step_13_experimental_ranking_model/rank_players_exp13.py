"""
Step 13: Integrated Experimental Ranking Model Pipeline
=======================================================
Implements the integrated experimental player reliability ranking system
based on the verified findings of Step 12.6:

1. Batting:
   - BRS_3 formula: 0.45 * Score_SR + 0.35 * Score_Surv + 0.20 * Score_Diff
   - Boundary execution component removed.
   - Preserves all official component scaling, bounds, priors, and shrinkage (K=50).

2. Bowling:
   - Official v2.0 BoRS formula retained: 0.40 * Score_Econ + 0.25 * Score_Wk + 0.20 * Score_Dot + 0.15 * Score_Diff
   - Containment formula NOT added.
   - Preserves all official component scaling, bounds, priors, and shrinkage (K=50).

3. Qualification:
   - Rule B applied to both Batting and Bowling:
     * Tier 1: N >= 60 OR (N >= 50 AND M >= 6)
     * Tier 2: N < 60 not in Tier 1, but N >= 40
     * Below Threshold: N < 40
     (N = high-pressure deliveries, M = distinct matches with high-pressure opportunities)

4. Phase Specialists:
   - Evaluated under existing phase methodology across PP, MO, and DO.
   - Annotated with both official tier and experimental Rule B tier status.

Authoritative source files used (READ-ONLY):
- data/processed/batter_performance.csv
- data/processed/bowler_performance.csv
- data/processed/delivery_pressure_index.csv
- data/processed/batter_reliability_rankings.csv (for official baseline comparison)
- data/processed/bowler_reliability_rankings.csv (for official baseline comparison)
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs" / "step_13_experimental_ranking_model"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# CONSTANTS & POPULATION PRIORS (Identical to Official v2.0 Specification)
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


def extract_high_pressure_matches(dpi_path: Path):
    """
    Extract distinct high-pressure match counts (M) for all batters and bowlers.
    - Batting: Batting_PI > 60.0 AND is_batter_ball_faced
    - Bowling: Bowling_PI > 60.0 AND is_legal_ball
    """
    print(f"Loading delivery-level pressure data from: {dpi_path.name}...")
    dpi = pd.read_csv(dpi_path, usecols=[
        'match_id', 'striker_id', 'bowler_id',
        'Batting_PI', 'Bowling_PI', 'is_batter_ball_faced', 'is_legal_ball'
    ])
    
    b_hp = dpi[(dpi['Batting_PI'] > 60.0) & (dpi['is_batter_ball_faced'] == True)]
    bo_hp = dpi[(dpi['Bowling_PI'] > 60.0) & (dpi['is_legal_ball'] == True)]
    
    b_matches = b_hp.groupby('striker_id')['match_id'].nunique().to_dict()
    bo_matches = bo_hp.groupby('bowler_id')['match_id'].nunique().to_dict()
    
    print(f"  Extracted high-pressure match counts for {len(b_matches)} batters and {len(bo_matches)} bowlers.")
    return b_matches, bo_matches


def calculate_exp13_batter_rankings(df: pd.DataFrame, hp_matches: dict) -> pd.DataFrame:
    """
    Calculate Integrated Experimental Batting Rankings (BRS_3 + Rule B).
    BRS_3 = 0.45 * Score_SR + 0.35 * Score_Surv + 0.20 * Score_Diff
    """
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
    b['score_exec'] = np.clip((b['exec_star'] + 20.0) / 25.0 * 100.0, 0.0, 100.0)  # Preserved for reference/audit
    b['score_diff'] = np.clip((b['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)
    
    # Composite BRS_3 (Experimental 3-Component Formula)
    b['brs_3'] = (0.45 * b['score_sr'] + 
                  0.35 * b['score_surv'] + 
                  0.20 * b['score_diff'])
    b['brs_3'] = np.clip(b['brs_3'], 0.0, 100.0)
    
    # Also calculate official BRS_4 for side-by-side verification
    b['brs_official'] = (0.40 * b['score_sr'] + 
                         0.25 * b['score_surv'] + 
                         0.20 * b['score_exec'] + 
                         0.15 * b['score_diff'])
    b['brs_official'] = np.clip(b['brs_official'], 0.0, 100.0)
    
    # Match count M
    b['hp_matches'] = b['player_id'].map(hp_matches).fillna(0).astype(int)
    
    # Qualification Tiers: Rule B
    # Tier 1: N >= 60 OR (N >= 50 AND M >= 6)
    # Tier 2: N < 60 not in Tier 1, but N >= 40
    # Below Threshold: N < 40
    def assign_tier_rule_b(row):
        n = row['high_balls_faced']
        m = row['hp_matches']
        if n >= 60 or (n >= 50 and m >= 6):
            return 'Tier 1: Qualified'
        elif n >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'
            
    b['tier_exp13'] = b.apply(assign_tier_rule_b, axis=1)
    
    # Official baseline tier for comparison
    def assign_tier_official(row):
        n = row['high_balls_faced']
        if n >= 60:
            return 'Tier 1: Qualified'
        elif n >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'
    b['tier_official'] = b.apply(assign_tier_official, axis=1)
    
    # Qualification reason tag
    def get_qual_reason(row):
        n = row['high_balls_faced']
        m = row['hp_matches']
        if n >= 60:
            return 'Baseline Volume (N>=60)'
        elif n >= 50 and m >= 6:
            return f'Rule B High-Breadth (N={n}, M={m})'
        elif n >= 40:
            return f'Specialist Sample (N={n})'
        else:
            return f'Below Threshold (N={n})'
    b['qualification_reason'] = b.apply(get_qual_reason, axis=1)

    # Assign Ranks within Tiers for Exp 13 (1-based, descending by brs_3)
    b['tier1_rank_exp13'] = np.nan
    t1_mask = b['tier_exp13'] == 'Tier 1: Qualified'
    b.loc[t1_mask, 'tier1_rank_exp13'] = b.loc[t1_mask, 'brs_3'].rank(ascending=False, method='min').astype(int)
    
    b['tier2_rank_exp13'] = np.nan
    t2_mask = b['tier_exp13'] == 'Tier 2: Specialist'
    b.loc[t2_mask, 'tier2_rank_exp13'] = b.loc[t2_mask, 'brs_3'].rank(ascending=False, method='min').astype(int)

    # Full population overall rank by brs_3
    b['overall_rank_exp13'] = b['brs_3'].rank(ascending=False, method='min').astype(int)
    
    # Sort order: Tier 1 ranks, then Tier 2 ranks, then remaining by balls faced
    b = b.sort_values(by=['tier_exp13', 'tier1_rank_exp13', 'tier2_rank_exp13', 'high_balls_faced'], 
                      ascending=[True, True, True, False]).reset_index(drop=True)
    return b


def calculate_exp13_bowler_rankings(df: pd.DataFrame, hp_matches: dict) -> pd.DataFrame:
    """
    Calculate Integrated Experimental Bowling Rankings (Official BoRS + Rule B).
    BoRS = 0.40 * Score_Econ + 0.25 * Score_Wk + 0.20 * Score_Dot + 0.15 * Score_Diff
    """
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
    
    # Composite BoRS (Official formula retained)
    bo['bors'] = (0.40 * bo['score_econ'] + 
                  0.25 * bo['score_wk'] + 
                  0.20 * bo['score_dot'] + 
                  0.15 * bo['score_diff'])
    bo['bors'] = np.clip(bo['bors'], 0.0, 100.0)
    
    # Match count M
    bo['hp_matches'] = bo['player_id'].map(hp_matches).fillna(0).astype(int)
    
    # Qualification Tiers: Rule B
    # Tier 1: N >= 60 OR (N >= 50 AND M >= 6)
    # Tier 2: N < 60 not in Tier 1, but N >= 40
    # Below Threshold: N < 40
    def assign_tier_rule_b(row):
        n = row['high_legal_balls']
        m = row['hp_matches']
        if n >= 60 or (n >= 50 and m >= 6):
            return 'Tier 1: Qualified'
        elif n >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'
            
    bo['tier_exp13'] = bo.apply(assign_tier_rule_b, axis=1)
    
    # Official baseline tier for comparison
    def assign_tier_official(row):
        n = row['high_legal_balls']
        if n >= 60:
            return 'Tier 1: Qualified'
        elif n >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'
    bo['tier_official'] = bo.apply(assign_tier_official, axis=1)
    
    # Qualification reason tag
    def get_qual_reason(row):
        n = row['high_legal_balls']
        m = row['hp_matches']
        if n >= 60:
            return 'Baseline Volume (N>=60)'
        elif n >= 50 and m >= 6:
            return f'Rule B High-Breadth (N={n}, M={m})'
        elif n >= 40:
            return f'Specialist Sample (N={n})'
        else:
            return f'Below Threshold (N={n})'
    bo['qualification_reason'] = bo.apply(get_qual_reason, axis=1)
    
    # Assign Ranks within Tiers for Exp 13 (1-based, descending by bors)
    bo['tier1_rank_exp13'] = np.nan
    t1_mask = bo['tier_exp13'] == 'Tier 1: Qualified'
    bo.loc[t1_mask, 'tier1_rank_exp13'] = bo.loc[t1_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    
    bo['tier2_rank_exp13'] = np.nan
    t2_mask = bo['tier_exp13'] == 'Tier 2: Specialist'
    bo.loc[t2_mask, 'tier2_rank_exp13'] = bo.loc[t2_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    
    # Full population overall rank by bors
    bo['overall_rank_exp13'] = bo['bors'].rank(ascending=False, method='min').astype(int)
    
    # Sort order
    bo = bo.sort_values(by=['tier_exp13', 'tier1_rank_exp13', 'tier2_rank_exp13', 'high_legal_balls'], 
                        ascending=[True, True, True, False]).reset_index(drop=True)
    return bo


def calculate_exp13_phase_specialists(b_ranked: pd.DataFrame, bo_ranked: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate phase specialist rankings under existing phase methodology,
    annotating each specialist with their official and Exp 13 qualification tiers.
    """
    phase_records = []
    
    # 1. Batters - Powerplay (N >= 25)
    b_pp = b_ranked[b_ranked['bf_pp_high'] >= 25].copy()
    lam_b_pp = b_pp['bf_pp_high'] / (b_pp['bf_pp_high'] + K)
    b_pp['sr_star'] = lam_b_pp * b_pp['pp_high_strike_rate'] + (1 - lam_b_pp) * MU_BAT_SR_PP
    b_pp = b_pp.sort_values('sr_star', ascending=False).reset_index(drop=True)
    for rnk, (_, row) in enumerate(b_pp.iterrows(), start=1):
        phase_records.append({
            'category': 'Batter_Powerplay',
            'phase': 'Powerplay (Overs 1-6)',
            'role': 'Batter',
            'phase_rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['bf_pp_high'],
            'total_high_deliveries': row['high_balls_faced'],
            'hp_matches': row['hp_matches'],
            'observed_metric': row['pp_high_strike_rate'],
            'metric_label': 'Strike Rate',
            'bayesian_metric': np.round(row['sr_star'], 2),
            'phase_prior': np.round(MU_BAT_SR_PP, 2),
            'tier_official': row['tier_official'],
            'tier_exp13': row['tier_exp13'],
            'tier1_rank_exp13': row['tier1_rank_exp13']
        })

    # 2. Batters - Middle Overs (N >= 30)
    b_mo = b_ranked[b_ranked['bf_mo_high'] >= 30].copy()
    lam_b_mo = b_mo['bf_mo_high'] / (b_mo['bf_mo_high'] + K)
    b_mo['sr_star'] = lam_b_mo * b_mo['mo_high_strike_rate'] + (1 - lam_b_mo) * MU_BAT_SR_MO
    b_mo = b_mo.sort_values('sr_star', ascending=False).reset_index(drop=True)
    for rnk, (_, row) in enumerate(b_mo.iterrows(), start=1):
        phase_records.append({
            'category': 'Batter_MiddleOvers',
            'phase': 'Middle Overs (Overs 7-15)',
            'role': 'Batter',
            'phase_rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['bf_mo_high'],
            'total_high_deliveries': row['high_balls_faced'],
            'hp_matches': row['hp_matches'],
            'observed_metric': row['mo_high_strike_rate'],
            'metric_label': 'Strike Rate',
            'bayesian_metric': np.round(row['sr_star'], 2),
            'phase_prior': np.round(MU_BAT_SR_MO, 2),
            'tier_official': row['tier_official'],
            'tier_exp13': row['tier_exp13'],
            'tier1_rank_exp13': row['tier1_rank_exp13']
        })

    # 3. Batters - Death Overs (N >= 30)
    b_do = b_ranked[b_ranked['bf_do_high'] >= 30].copy()
    lam_b_do = b_do['bf_do_high'] / (b_do['bf_do_high'] + K)
    b_do['sr_star'] = lam_b_do * b_do['do_high_strike_rate'] + (1 - lam_b_do) * MU_BAT_SR_DO
    b_do = b_do.sort_values('sr_star', ascending=False).reset_index(drop=True)
    for rnk, (_, row) in enumerate(b_do.iterrows(), start=1):
        phase_records.append({
            'category': 'Batter_DeathOvers',
            'phase': 'Death Overs (Overs 16-20)',
            'role': 'Batter',
            'phase_rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['bf_do_high'],
            'total_high_deliveries': row['high_balls_faced'],
            'hp_matches': row['hp_matches'],
            'observed_metric': row['do_high_strike_rate'],
            'metric_label': 'Strike Rate',
            'bayesian_metric': np.round(row['sr_star'], 2),
            'phase_prior': np.round(MU_BAT_SR_DO, 2),
            'tier_official': row['tier_official'],
            'tier_exp13': row['tier_exp13'],
            'tier1_rank_exp13': row['tier1_rank_exp13']
        })

    # 4. Bowlers - Powerplay (N >= 30)
    bo_pp = bo_ranked[bo_ranked['lb_pp_high'] >= 30].copy()
    lam_bo_pp = bo_pp['lb_pp_high'] / (bo_pp['lb_pp_high'] + K)
    bo_pp['econ_star'] = lam_bo_pp * bo_pp['pp_high_economy_rate'] + (1 - lam_bo_pp) * MU_BOWL_ECON_PP
    bo_pp = bo_pp.sort_values('econ_star', ascending=True).reset_index(drop=True)
    for rnk, (_, row) in enumerate(bo_pp.iterrows(), start=1):
        phase_records.append({
            'category': 'Bowler_Powerplay',
            'phase': 'Powerplay (Overs 1-6)',
            'role': 'Bowler',
            'phase_rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['lb_pp_high'],
            'total_high_deliveries': row['high_legal_balls'],
            'hp_matches': row['hp_matches'],
            'observed_metric': row['pp_high_economy_rate'],
            'metric_label': 'Economy Rate',
            'bayesian_metric': np.round(row['econ_star'], 2),
            'phase_prior': np.round(MU_BOWL_ECON_PP, 2),
            'tier_official': row['tier_official'],
            'tier_exp13': row['tier_exp13'],
            'tier1_rank_exp13': row['tier1_rank_exp13']
        })

    # 5. Bowlers - Middle Overs (N >= 25)
    bo_mo = bo_ranked[bo_ranked['lb_mo_high'] >= 25].copy()
    lam_bo_mo = bo_mo['lb_mo_high'] / (bo_mo['lb_mo_high'] + K)
    bo_mo['econ_star'] = lam_bo_mo * bo_mo['mo_high_economy_rate'] + (1 - lam_bo_mo) * MU_BOWL_ECON_MO
    bo_mo = bo_mo.sort_values('econ_star', ascending=True).reset_index(drop=True)
    for rnk, (_, row) in enumerate(bo_mo.iterrows(), start=1):
        phase_records.append({
            'category': 'Bowler_MiddleOvers',
            'phase': 'Middle Overs (Overs 7-15)',
            'role': 'Bowler',
            'phase_rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['lb_mo_high'],
            'total_high_deliveries': row['high_legal_balls'],
            'hp_matches': row['hp_matches'],
            'observed_metric': row['mo_high_economy_rate'],
            'metric_label': 'Economy Rate',
            'bayesian_metric': np.round(row['econ_star'], 2),
            'phase_prior': np.round(MU_BOWL_ECON_MO, 2),
            'tier_official': row['tier_official'],
            'tier_exp13': row['tier_exp13'],
            'tier1_rank_exp13': row['tier1_rank_exp13']
        })

    # 6. Bowlers - Death Overs (N >= 15)
    bo_do = bo_ranked[bo_ranked['lb_do_high'] >= 15].copy()
    lam_bo_do = bo_do['lb_do_high'] / (bo_do['lb_do_high'] + K)
    bo_do['econ_star'] = lam_bo_do * bo_do['do_high_economy_rate'] + (1 - lam_bo_do) * MU_BOWL_ECON_DO
    bo_do = bo_do.sort_values('econ_star', ascending=True).reset_index(drop=True)
    for rnk, (_, row) in enumerate(bo_do.iterrows(), start=1):
        phase_records.append({
            'category': 'Bowler_DeathOvers',
            'phase': 'Death Overs (Overs 16-20)',
            'role': 'Bowler',
            'phase_rank': rnk,
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'sample_deliveries': row['lb_do_high'],
            'total_high_deliveries': row['high_legal_balls'],
            'hp_matches': row['hp_matches'],
            'observed_metric': row['do_high_economy_rate'],
            'metric_label': 'Economy Rate',
            'bayesian_metric': np.round(row['econ_star'], 2),
            'phase_prior': np.round(MU_BOWL_ECON_DO, 2),
            'tier_official': row['tier_official'],
            'tier_exp13': row['tier_exp13'],
            'tier1_rank_exp13': row['tier1_rank_exp13']
        })

    return pd.DataFrame(phase_records)


def run_exp13_pipeline():
    print("=" * 80)
    print("STEP 13: INTEGRATED EXPERIMENTAL RANKING MODEL PIPELINE")
    print("=" * 80)
    
    # 1. Load Source Datasets
    batters_path = DATA_DIR / "batter_performance.csv"
    bowlers_path = DATA_DIR / "bowler_performance.csv"
    dpi_path     = DATA_DIR / "delivery_pressure_index.csv"
    
    assert batters_path.exists(), f"Missing: {batters_path}"
    assert bowlers_path.exists(), f"Missing: {bowlers_path}"
    assert dpi_path.exists(), f"Missing: {dpi_path}"
    
    batter_df = pd.read_csv(batters_path)
    bowler_df = pd.read_csv(bowlers_path)
    print(f"Loaded {len(batter_df)} batters and {len(bowler_df)} bowlers from base performance data.")
    
    # 2. Extract Match Counts M
    hp_matches_bat, hp_matches_bowl = extract_high_pressure_matches(dpi_path)
    
    # 3. Calculate Experimental Rankings
    print("\nCalculating Integrated Experimental Batting Rankings (BRS_3 + Rule B)...")
    exp13_bat = calculate_exp13_batter_rankings(batter_df, hp_matches_bat)
    
    print("Calculating Integrated Experimental Bowling Rankings (BoRS + Rule B)...")
    exp13_bowl = calculate_exp13_bowler_rankings(bowler_df, hp_matches_bowl)
    
    # 4. Calculate Phase Specialist Rankings using base performance data (preserving exact stable-sort input order)
    print("Calculating Integrated Phase Specialist Rankings...")
    # Add tier annotations to batter_df and bowler_df for phase specialist tagging
    b_tier_map = exp13_bat.set_index('player_id')[['tier_official', 'tier_exp13', 'tier1_rank_exp13', 'hp_matches']].to_dict('index')
    bo_tier_map = exp13_bowl.set_index('player_id')[['tier_official', 'tier_exp13', 'tier1_rank_exp13', 'hp_matches']].to_dict('index')
    
    b_for_phase = batter_df.copy()
    b_for_phase['tier_official'] = b_for_phase['player_id'].map(lambda pid: b_tier_map[pid]['tier_official'])
    b_for_phase['tier_exp13'] = b_for_phase['player_id'].map(lambda pid: b_tier_map[pid]['tier_exp13'])
    b_for_phase['tier1_rank_exp13'] = b_for_phase['player_id'].map(lambda pid: b_tier_map[pid]['tier1_rank_exp13'])
    b_for_phase['hp_matches'] = b_for_phase['player_id'].map(lambda pid: b_tier_map[pid]['hp_matches'])
    
    bo_for_phase = bowler_df.copy()
    bo_for_phase['tier_official'] = bo_for_phase['player_id'].map(lambda pid: bo_tier_map[pid]['tier_official'])
    bo_for_phase['tier_exp13'] = bo_for_phase['player_id'].map(lambda pid: bo_tier_map[pid]['tier_exp13'])
    bo_for_phase['tier1_rank_exp13'] = bo_for_phase['player_id'].map(lambda pid: bo_tier_map[pid]['tier1_rank_exp13'])
    bo_for_phase['hp_matches'] = bo_for_phase['player_id'].map(lambda pid: bo_tier_map[pid]['hp_matches'])
    
    exp13_phase = calculate_exp13_phase_specialists(b_for_phase, bo_for_phase)
    
    # 5. Integrity & Quality Assertions
    print("\nRunning Rigorous Integrity Assertions...")
    
    # Check total populations
    assert len(exp13_bat) == 816, f"Expected 816 batters, got {len(exp13_bat)}"
    assert len(exp13_bowl) == 589, f"Expected 589 bowlers, got {len(exp13_bowl)}"
    assert len(exp13_phase) == 453, f"Expected 453 phase entries, got {len(exp13_phase)}"
    
    # Check score bounds [0, 100] and no nulls
    assert (exp13_bat['brs_3'] >= 0.0).all() and (exp13_bat['brs_3'] <= 100.0).all(), "BRS_3 score outside [0, 100]!"
    assert (exp13_bowl['bors'] >= 0.0).all() and (exp13_bowl['bors'] <= 100.0).all(), "BoRS score outside [0, 100]!"
    assert exp13_bat['brs_3'].isnull().sum() == 0, "Null found in BRS_3!"
    assert exp13_bowl['bors'].isnull().sum() == 0, "Null found in BoRS!"
    
    # Check no duplicate player IDs
    assert exp13_bat['player_id'].duplicated().sum() == 0, "Duplicate player_id in batters!"
    assert exp13_bowl['player_id'].duplicated().sum() == 0, "Duplicate player_id in bowlers!"
    
    # Check Tier counts under Rule B
    t1_b_count = (exp13_bat['tier_exp13'] == 'Tier 1: Qualified').sum()
    t2_b_count = (exp13_bat['tier_exp13'] == 'Tier 2: Specialist').sum()
    ex_b_count = (exp13_bat['tier_exp13'] == 'Below Threshold').sum()
    assert t1_b_count == 146, f"Expected 146 Tier 1 batters, got {t1_b_count}"
    assert t2_b_count == 42, f"Expected 42 Tier 2 batters, got {t2_b_count}"
    assert ex_b_count == 628, f"Expected 628 Excluded batters, got {ex_b_count}"
    
    t1_bo_count = (exp13_bowl['tier_exp13'] == 'Tier 1: Qualified').sum()
    t2_bo_count = (exp13_bowl['tier_exp13'] == 'Tier 2: Specialist').sum()
    ex_bo_count = (exp13_bowl['tier_exp13'] == 'Below Threshold').sum()
    assert t1_bo_count == 130, f"Expected 130 Tier 1 bowlers, got {t1_bo_count}"
    assert t2_bo_count == 19, f"Expected 19 Tier 2 bowlers, got {t2_bo_count}"
    assert ex_bo_count == 440, f"Expected 440 Excluded bowlers, got {ex_bo_count}"
    
    # Check consecutive ranks in Tier 1
    t1_b_ranks = exp13_bat.loc[exp13_bat['tier_exp13'] == 'Tier 1: Qualified', 'tier1_rank_exp13'].sort_values().values
    assert t1_b_ranks[0] == 1 and t1_b_ranks[-1] == 146, f"Tier 1 batter ranks not 1-146! (min={t1_b_ranks[0]}, max={t1_b_ranks[-1]})"
    
    t1_bo_ranks = exp13_bowl.loc[exp13_bowl['tier_exp13'] == 'Tier 1: Qualified', 'tier1_rank_exp13'].sort_values().values
    assert t1_bo_ranks[0] == 1 and t1_bo_ranks[-1] == 130, f"Tier 1 bowler ranks not 1-130! (min={t1_bo_ranks[0]}, max={t1_bo_ranks[-1]})"
    
    print("  ALL 10 Integrity and Structure Assertions PASSED successfully.")
    
    # 6. Export Datasets
    bat_out_csv = OUTPUT_DIR / "exp13_batter_rankings.csv"
    bowl_out_csv = OUTPUT_DIR / "exp13_bowler_rankings.csv"
    phase_out_csv = OUTPUT_DIR / "exp13_phase_specialist_rankings.csv"
    
    exp13_bat.to_csv(bat_out_csv, index=False)
    exp13_bowl.to_csv(bowl_out_csv, index=False)
    exp13_phase.to_csv(phase_out_csv, index=False)
    
    print(f"\nExported Experimental Datasets:")
    print(f"  1. Batters  : {bat_out_csv} ({len(exp13_bat)} rows)")
    print(f"  2. Bowlers  : {bowl_out_csv} ({len(exp13_bowl)} rows)")
    print(f"  3. Phases   : {phase_out_csv} ({len(exp13_phase)} rows)")
    
    print("\nSummary of Step 13 Tier Structure:")
    print(f"  Batters : Tier 1 = {t1_b_count} (+30 vs official 116), Tier 2 = {t2_b_count} (-30 vs official 72), Below = {ex_b_count}")
    print(f"  Bowlers : Tier 1 = {t1_bo_count} (+17 vs official 113), Tier 2 = {t2_bo_count} (-17 vs official 36), Below = {ex_bo_count}")
    print("=" * 80)
    return exp13_bat, exp13_bowl, exp13_phase


if __name__ == "__main__":
    run_exp13_pipeline()
