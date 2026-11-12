import sys
sys.path.append('src')
import numpy as np
import pandas as pd
from evaluate_player_performance import evaluate_batters, evaluate_bowlers, FLAGGED_TARGET_UNDERSTATED_MATCHES

# 1. Load data
batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

print(f"Loaded {len(batter_df)} batters and {len(bowler_df)} bowlers.")

# Constants from ranking_model_design.md
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

def calculate_batter_rankings(df):
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
    b['sr_star']    = b['lambda_high'] * b['sr_obs'] + (1.0 - b['lambda_high']) * MU_BAT_SR_HIGH
    b['out_star']   = b['lambda_high'] * b['out_obs'] + (1.0 - b['lambda_high']) * MU_BAT_OUT_HIGH
    b['surv_star']  = 100.0 - b['out_star']
    b['bnd_star']   = b['lambda_high'] * b['bnd_obs'] + (1.0 - b['lambda_high']) * MU_BAT_BND_HIGH
    b['dot_star']   = b['lambda_high'] * b['dot_obs'] + (1.0 - b['lambda_high']) * MU_BAT_DOT_HIGH
    b['exec_star']  = b['bnd_star'] - 0.5 * b['dot_star']
    
    b['sr_low_star']   = b['lambda_low'] * b['sr_low_obs'] + (1.0 - b['lambda_low']) * MU_BAT_SR_LOW
    b['diff_sr_star']  = b['sr_star'] - b['sr_low_star']
    
    # Standardized sub-scores
    b['score_sr']   = np.clip((b['sr_star'] - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    b['score_surv'] = np.clip((b['surv_star'] - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    b['score_exec'] = np.clip((b['exec_star'] + 20.0) / 25.0 * 100.0, 0.0, 100.0)
    b['score_diff'] = np.clip((b['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)
    
    # Composite BRS
    b['brs'] = (0.40 * b['score_sr'] + 
                0.25 * b['score_surv'] + 
                0.20 * b['score_exec'] + 
                0.15 * b['score_diff'])
    
    # Qualification tier
    def assign_tier(bf):
        if bf >= 60:
            return 'Tier 1: Qualified'
        elif bf >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'
            
    b['tier'] = b['high_balls_faced'].apply(assign_tier)
    
    # Ranks
    b['tier1_rank'] = np.nan
    t1_mask = b['tier'] == 'Tier 1: Qualified'
    b.loc[t1_mask, 'tier1_rank'] = b.loc[t1_mask, 'brs'].rank(ascending=False, method='min').astype(int)
    
    b['tier2_rank'] = np.nan
    t2_mask = b['tier'] == 'Tier 2: Specialist'
    b.loc[t2_mask, 'tier2_rank'] = b.loc[t2_mask, 'brs'].rank(ascending=False, method='min').astype(int)
    
    return b

def calculate_bowler_rankings(df):
    bo = df.copy()
    
    # Credibility factors
    bo['lambda_high'] = bo['high_legal_balls'] / (bo['high_legal_balls'] + K)
    bo['lambda_low']  = bo['low_mod_legal_balls'] / (bo['low_mod_legal_balls'] + K)
    
    # Observed rates
    bo['econ_obs']   = np.where(bo['high_legal_balls'] > 0, (bo['high_runs_conceded'] / bo['high_legal_balls']) * 6.0, MU_BOWL_ECON_HIGH)
    bo['wk_obs']     = np.where(bo['high_legal_balls'] > 0, (bo['high_wickets'] / bo['high_legal_balls']) * 100.0, MU_BOWL_WK_HIGH)
    bo['dot_bo_obs'] = np.where(bo['high_legal_balls'] > 0, (bo['high_dot_balls'] / bo['high_legal_balls']) * 100.0, MU_BOWL_DOT_HIGH)
    bo['econ_low_obs']= np.where(bo['low_mod_legal_balls'] > 0, (bo['low_mod_runs_conceded'] / bo['low_mod_legal_balls']) * 6.0, MU_BOWL_ECON_LOW)
    
    # Bayesian estimates
    bo['econ_star']    = bo['lambda_high'] * bo['econ_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_ECON_HIGH
    bo['wk_star']      = bo['lambda_high'] * bo['wk_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_WK_HIGH
    bo['dot_bo_star']  = bo['lambda_high'] * bo['dot_bo_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_DOT_HIGH
    bo['econ_low_star']= bo['lambda_low'] * bo['econ_low_obs'] + (1.0 - bo['lambda_low']) * MU_BOWL_ECON_LOW
    bo['diff_econ_star']= bo['econ_low_star'] - bo['econ_star']
    
    # Standardized sub-scores
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
    
    # Ranks
    bo['tier1_rank'] = np.nan
    t1_mask = bo['tier'] == 'Tier 1: Qualified'
    bo.loc[t1_mask, 'tier1_rank'] = bo.loc[t1_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    
    bo['tier2_rank'] = np.nan
    t2_mask = bo['tier'] == 'Tier 2: Specialist'
    bo.loc[t2_mask, 'tier2_rank'] = bo.loc[t2_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    
    return bo

b_ranked = calculate_batter_rankings(batter_df)
bo_ranked = calculate_bowler_rankings(bowler_df)

print("\n=== TOP 10 BATTERS (TIER 1) ===")
t1_bat = b_ranked[b_ranked['tier'] == 'Tier 1: Qualified'].sort_values('tier1_rank').head(10)
for idx, r in t1_bat.iterrows():
    print(f"Rank {int(r['tier1_rank']):2d}: {r['player_name']:22s} | BF={r['high_balls_faced']:3.0f} | SR*={r['sr_star']:6.2f} | Surv*={r['surv_star']:5.2f}% | Delta={r['diff_sr_star']:+6.2f} | BRS={r['brs']:6.2f}")

print("\n=== TOP 10 BOWLERS (TIER 1) ===")
t1_bowl = bo_ranked[bo_ranked['tier'] == 'Tier 1: Qualified'].sort_values('tier1_rank').head(10)
for idx, r in t1_bowl.iterrows():
    print(f"Rank {int(r['tier1_rank']):2d}: {r['player_name']:22s} | LB={r['high_legal_balls']:3.0f} | Econ*={r['econ_star']:5.2f} | Wk*={r['wk_star']:4.2f}% | Dot*={r['dot_bo_star']:5.2f}% | Delta={r['diff_econ_star']:+5.2f} | BoRS={r['bors']:6.2f}")
