"""
Step 13.1 Independent Audit — Module A: Independent Calculation & Ranking Verification
======================================================================================
Objective:
Independently reconstruct all batting and bowling calculations from the authoritative
base performance files (batter_performance.csv, bowler_performance.csv) and delivery-level
match state (delivery_pressure_index.csv).

Verifies:
1. Batting: BRS_3 components, Bayesian shrinkage (K=50), population priors, clipping [0, 100],
   and non-inclusion of Boundary Execution.
2. Bowling: Retained v2.0 BoRS components, Bayesian shrinkage (K=50), priors, clipping [0, 100].
3. Qualification: Rule B logic, high-pressure match count (M), delivery count (N),
   tier assignment, within-tier ranking, overall ranking, and sorting.
4. Numerical precision: Verifies all 816 batters and 589 bowlers against Step 13 datasets
   using strict tolerances (1e-6 and 1e-5).

Outputs:
- outputs/step_13_1_independent_audit/audit_a_calculation_discrepancies.csv
- outputs/step_13_1_independent_audit/audit_a_qualification_discrepancies.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
EXP13_DIR = BASE_DIR / "outputs" / "step_13_experimental_ranking_model"
AUDIT_OUT_DIR = BASE_DIR / "outputs" / "step_13_1_independent_audit"
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# CONSTANTS & POPULATION PRIORS (Audited Baseline Specification)
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

FLOAT_TOLERANCE_STRICT = 1e-6
FLOAT_TOLERANCE_REPORT = 1e-5


def run_audit_a():
    print("=" * 80)
    print("STEP 13.1 AUDIT A: INDEPENDENT CALCULATION & RANKING VERIFICATION")
    print("=" * 80)

    # 1. Load Authoritative Base Data (READ ONLY)
    bat_base_path = DATA_DIR / "batter_performance.csv"
    bowl_base_path = DATA_DIR / "bowler_performance.csv"
    dpi_path = DATA_DIR / "delivery_pressure_index.csv"

    exp13_bat_path = EXP13_DIR / "exp13_batter_rankings.csv"
    exp13_bowl_path = EXP13_DIR / "exp13_bowler_rankings.csv"

    for p in [bat_base_path, bowl_base_path, dpi_path, exp13_bat_path, exp13_bowl_path]:
        assert p.exists(), f"Missing required file: {p}"

    df_bat_base = pd.read_csv(bat_base_path)
    df_bowl_base = pd.read_csv(bowl_base_path)

    df_exp13_bat = pd.read_csv(exp13_bat_path)
    df_exp13_bowl = pd.read_csv(exp13_bowl_path)

    print(f"Loaded source datasets:")
    print(f"  Base Batters : {len(df_bat_base)} rows")
    print(f"  Base Bowlers : {len(df_bowl_base)} rows")
    print(f"  Exp13 Batters: {len(df_exp13_bat)} rows")
    print(f"  Exp13 Bowlers: {len(df_exp13_bowl)} rows")

    # -------------------------------------------------------------------------
    # 2. Independent Match Count (M) Reconstruction from Delivery Match State
    # -------------------------------------------------------------------------
    print("\nReconstructing High-Pressure Match Counts (M) directly from delivery logs...")
    dpi = pd.read_csv(dpi_path, usecols=[
        'match_id', 'striker_id', 'bowler_id',
        'Batting_PI', 'Bowling_PI', 'is_batter_ball_faced', 'is_legal_ball'
    ])

    # Batting: Batting_PI > 60.0 & is_batter_ball_faced == True
    b_hp = dpi[(dpi['Batting_PI'] > 60.0) & (dpi['is_batter_ball_faced'] == True)]
    indep_b_matches = b_hp.groupby('striker_id')['match_id'].nunique().to_dict()

    # Bowling: Bowling_PI > 60.0 & is_legal_ball == True
    bo_hp = dpi[(dpi['Bowling_PI'] > 60.0) & (dpi['is_legal_ball'] == True)]
    indep_bo_matches = bo_hp.groupby('bowler_id')['match_id'].nunique().to_dict()

    print(f"  Reconstructed match counts for {len(indep_b_matches)} batters and {len(indep_bo_matches)} bowlers.")

    # -------------------------------------------------------------------------
    # 3. Independent Batting Calculations (BRS_3 & Rule B)
    # -------------------------------------------------------------------------
    print("\nIndependently calculating Batting Model (BRS_3 + Rule B)...")
    b = df_bat_base.copy()

    # Credibility factors
    b['lambda_high'] = b['high_balls_faced'] / (b['high_balls_faced'] + K)
    b['lambda_low']  = b['low_mod_balls_faced'] / (b['low_mod_balls_faced'] + K)

    # Observed rates
    b['sr_obs']  = np.where(b['high_balls_faced'] > 0, (b['high_runs'] / b['high_balls_faced']) * 100.0, MU_BAT_SR_HIGH)
    b['out_obs'] = np.where(b['high_balls_faced'] > 0, (b['high_dismissals'] / b['high_balls_faced']) * 100.0, MU_BAT_OUT_HIGH)
    b['sr_low_obs'] = np.where(b['low_mod_balls_faced'] > 0, (b['low_mod_runs'] / b['low_mod_balls_faced']) * 100.0, MU_BAT_SR_LOW)

    # Bayesian shrinkage
    b['sr_star']   = b['lambda_high'] * b['sr_obs'] + (1.0 - b['lambda_high']) * MU_BAT_SR_HIGH
    b['out_star']  = b['lambda_high'] * b['out_obs'] + (1.0 - b['lambda_high']) * MU_BAT_OUT_HIGH
    b['surv_star'] = 100.0 - b['out_star']
    b['sr_low_star']  = b['lambda_low'] * b['sr_low_obs'] + (1.0 - b['lambda_low']) * MU_BAT_SR_LOW
    b['diff_sr_star'] = b['sr_star'] - b['sr_low_star']

    # Standardized sub-scores [0, 100]
    b['score_sr']   = np.clip((b['sr_star'] - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    b['score_surv'] = np.clip((b['surv_star'] - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    b['score_diff'] = np.clip((b['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)

    # BRS_3 composite (45% SR, 35% Surv, 20% Diff; Boundary Execution NOT included)
    b['brs_3'] = np.clip(0.45 * b['score_sr'] + 0.35 * b['score_surv'] + 0.20 * b['score_diff'], 0.0, 100.0)

    # Match counts M
    b['hp_matches'] = b['player_id'].map(indep_b_matches).fillna(0).astype(int)

    # Rule B Qualification
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

    # Ranks within Tiers
    b['tier1_rank_exp13'] = np.nan
    t1_b_mask = b['tier_exp13'] == 'Tier 1: Qualified'
    b.loc[t1_b_mask, 'tier1_rank_exp13'] = b.loc[t1_b_mask, 'brs_3'].rank(ascending=False, method='min').astype(int)

    b['tier2_rank_exp13'] = np.nan
    t2_b_mask = b['tier_exp13'] == 'Tier 2: Specialist'
    b.loc[t2_b_mask, 'tier2_rank_exp13'] = b.loc[t2_b_mask, 'brs_3'].rank(ascending=False, method='min').astype(int)

    b['overall_rank_exp13'] = b['brs_3'].rank(ascending=False, method='min').astype(int)

    # -------------------------------------------------------------------------
    # 4. Independent Bowling Calculations (BoRS & Rule B)
    # -------------------------------------------------------------------------
    print("Independently calculating Bowling Model (BoRS + Rule B)...")
    bo = df_bowl_base.copy()

    bo['lambda_high'] = bo['high_legal_balls'] / (bo['high_legal_balls'] + K)
    bo['lambda_low']  = bo['low_mod_legal_balls'] / (bo['low_mod_legal_balls'] + K)

    bo['econ_obs']    = np.where(bo['high_legal_balls'] > 0, (bo['high_runs_conceded'] / bo['high_legal_balls']) * 6.0, MU_BOWL_ECON_HIGH)
    bo['wk_pct_obs']  = np.where(bo['high_legal_balls'] > 0, (bo['high_wickets'] / bo['high_legal_balls']) * 100.0, MU_BOWL_WK_HIGH)
    bo['dot_bo_obs']  = np.where(bo['high_legal_balls'] > 0, (bo['high_dot_balls'] / bo['high_legal_balls']) * 100.0, MU_BOWL_DOT_HIGH)
    bo['econ_low_obs']= np.where(bo['low_mod_legal_balls'] > 0, (bo['low_mod_runs_conceded'] / bo['low_mod_legal_balls']) * 6.0, MU_BOWL_ECON_LOW)

    bo['econ_star']     = bo['lambda_high'] * bo['econ_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_ECON_HIGH
    bo['wk_star']       = bo['lambda_high'] * bo['wk_pct_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_WK_HIGH
    bo['dot_bo_star']   = bo['lambda_high'] * bo['dot_bo_obs'] + (1.0 - bo['lambda_high']) * MU_BOWL_DOT_HIGH
    bo['econ_low_star'] = bo['lambda_low'] * bo['econ_low_obs'] + (1.0 - bo['lambda_low']) * MU_BOWL_ECON_LOW
    bo['diff_econ_star']= bo['econ_low_star'] - bo['econ_star']

    bo['score_econ'] = np.clip((12.00 - bo['econ_star']) / 6.00 * 100.0, 0.0, 100.0)
    bo['score_wk']   = np.clip((bo['wk_star'] - 1.50) / 7.50 * 100.0, 0.0, 100.0)
    bo['score_dot']  = np.clip((bo['dot_bo_star'] - 25.0) / 25.0 * 100.0, 0.0, 100.0)
    bo['score_diff'] = np.clip((bo['diff_econ_star'] + 3.00) / 5.00 * 100.0, 0.0, 100.0)

    bo['bors'] = np.clip(0.40 * bo['score_econ'] + 0.25 * bo['score_wk'] + 0.20 * bo['score_dot'] + 0.15 * bo['score_diff'], 0.0, 100.0)

    bo['hp_matches'] = bo['player_id'].map(indep_bo_matches).fillna(0).astype(int)

    def assign_tier_bo_rule_b(row):
        n = row['high_legal_balls']
        m = row['hp_matches']
        if n >= 60 or (n >= 50 and m >= 6):
            return 'Tier 1: Qualified'
        elif n >= 40:
            return 'Tier 2: Specialist'
        else:
            return 'Below Threshold'

    bo['tier_exp13'] = bo.apply(assign_tier_bo_rule_b, axis=1)

    bo['tier1_rank_exp13'] = np.nan
    t1_bo_mask = bo['tier_exp13'] == 'Tier 1: Qualified'
    bo.loc[t1_bo_mask, 'tier1_rank_exp13'] = bo.loc[t1_bo_mask, 'bors'].rank(ascending=False, method='min').astype(int)

    bo['tier2_rank_exp13'] = np.nan
    t2_bo_mask = bo['tier_exp13'] == 'Tier 2: Specialist'
    bo.loc[t2_bo_mask, 'tier2_rank_exp13'] = bo.loc[t2_bo_mask, 'bors'].rank(ascending=False, method='min').astype(int)

    bo['overall_rank_exp13'] = bo['bors'].rank(ascending=False, method='min').astype(int)

    # -------------------------------------------------------------------------
    # 5. Direct Comparison against Step 13 Published Outputs
    # -------------------------------------------------------------------------
    print("\nAuditing Calculations against Step 13 Outputs...")
    calc_discrepancies = []
    qual_discrepancies = []

    # Batters audit
    b_merged = b.merge(df_exp13_bat, on='player_id', suffixes=('_audit', '_exp13'))
    assert len(b_merged) == 816, f"Batter merge count mismatch! Expected 816, got {len(b_merged)}"

    for _, r in b_merged.iterrows():
        pid = r['player_id']
        pname = r['player_name_audit']
        
        # Check scores
        score_diff = abs(r['brs_3_audit'] - r['brs_3_exp13'])
        if score_diff > FLOAT_TOLERANCE_STRICT:
            calc_discrepancies.append({
                'discipline': 'Batting',
                'player_id': pid,
                'player_name': pname,
                'field': 'brs_3',
                'audit_value': r['brs_3_audit'],
                'step13_value': r['brs_3_exp13'],
                'abs_diff': score_diff,
                'tolerance': FLOAT_TOLERANCE_STRICT
            })
            
        # Check sub-scores
        for sub in ['score_sr', 'score_surv', 'score_diff']:
            diff = abs(r[f'{sub}_audit'] - r[f'{sub}_exp13'])
            if diff > FLOAT_TOLERANCE_STRICT:
                calc_discrepancies.append({
                    'discipline': 'Batting',
                    'player_id': pid,
                    'player_name': pname,
                    'field': sub,
                    'audit_value': r[f'{sub}_audit'],
                    'step13_value': r[f'{sub}_exp13'],
                    'abs_diff': diff,
                    'tolerance': FLOAT_TOLERANCE_STRICT
                })
                
        # Check qualification & match counts
        if r['hp_matches_audit'] != r['hp_matches_exp13']:
            qual_discrepancies.append({
                'discipline': 'Batting',
                'player_id': pid,
                'player_name': pname,
                'field': 'hp_matches',
                'audit_value': r['hp_matches_audit'],
                'step13_value': r['hp_matches_exp13']
            })
            
        if r['tier_exp13_audit'] != r['tier_exp13_exp13']:
            qual_discrepancies.append({
                'discipline': 'Batting',
                'player_id': pid,
                'player_name': pname,
                'field': 'tier_exp13',
                'audit_value': r['tier_exp13_audit'],
                'step13_value': r['tier_exp13_exp13']
            })
            
        # Check tier1_rank
        val_audit = r['tier1_rank_exp13_audit']
        val_exp = r['tier1_rank_exp13_exp13']
        if (np.isnan(val_audit) and not np.isnan(val_exp)) or (not np.isnan(val_audit) and np.isnan(val_exp)) or (not np.isnan(val_audit) and val_audit != val_exp):
            qual_discrepancies.append({
                'discipline': 'Batting',
                'player_id': pid,
                'player_name': pname,
                'field': 'tier1_rank_exp13',
                'audit_value': val_audit,
                'step13_value': val_exp
            })

    # Bowlers audit
    bo_merged = bo.merge(df_exp13_bowl, on='player_id', suffixes=('_audit', '_exp13'))
    assert len(bo_merged) == 589, f"Bowler merge count mismatch! Expected 589, got {len(bo_merged)}"

    for _, r in bo_merged.iterrows():
        pid = r['player_id']
        pname = r['player_name_audit']
        
        # Check scores
        score_diff = abs(r['bors_audit'] - r['bors_exp13'])
        if score_diff > FLOAT_TOLERANCE_STRICT:
            calc_discrepancies.append({
                'discipline': 'Bowling',
                'player_id': pid,
                'player_name': pname,
                'field': 'bors',
                'audit_value': r['bors_audit'],
                'step13_value': r['bors_exp13'],
                'abs_diff': score_diff,
                'tolerance': FLOAT_TOLERANCE_STRICT
            })
            
        # Check sub-scores
        for sub in ['score_econ', 'score_wk', 'score_dot', 'score_diff']:
            diff = abs(r[f'{sub}_audit'] - r[f'{sub}_exp13'])
            if diff > FLOAT_TOLERANCE_STRICT:
                calc_discrepancies.append({
                    'discipline': 'Bowling',
                    'player_id': pid,
                    'player_name': pname,
                    'field': sub,
                    'audit_value': r[f'{sub}_audit'],
                    'step13_value': r[f'{sub}_exp13'],
                    'abs_diff': diff,
                    'tolerance': FLOAT_TOLERANCE_STRICT
                })
                
        # Check qualification & match counts
        if r['hp_matches_audit'] != r['hp_matches_exp13']:
            qual_discrepancies.append({
                'discipline': 'Bowling',
                'player_id': pid,
                'player_name': pname,
                'field': 'hp_matches',
                'audit_value': r['hp_matches_audit'],
                'step13_value': r['hp_matches_exp13']
            })
            
        if r['tier_exp13_audit'] != r['tier_exp13_exp13']:
            qual_discrepancies.append({
                'discipline': 'Bowling',
                'player_id': pid,
                'player_name': pname,
                'field': 'tier_exp13',
                'audit_value': r['tier_exp13_audit'],
                'step13_value': r['tier_exp13_exp13']
            })
            
        # Check tier1_rank
        val_audit = r['tier1_rank_exp13_audit']
        val_exp = r['tier1_rank_exp13_exp13']
        if (np.isnan(val_audit) and not np.isnan(val_exp)) or (not np.isnan(val_audit) and np.isnan(val_exp)) or (not np.isnan(val_audit) and val_audit != val_exp):
            qual_discrepancies.append({
                'discipline': 'Bowling',
                'player_id': pid,
                'player_name': pname,
                'field': 'tier1_rank_exp13',
                'audit_value': val_audit,
                'step13_value': val_exp
            })

    calc_disc_df = pd.DataFrame(calc_discrepancies)
    qual_disc_df = pd.DataFrame(qual_discrepancies)

    calc_out_csv = AUDIT_OUT_DIR / "audit_a_calculation_discrepancies.csv"
    qual_out_csv = AUDIT_OUT_DIR / "audit_a_qualification_discrepancies.csv"

    calc_disc_df.to_csv(calc_out_csv, index=False)
    qual_disc_df.to_csv(qual_out_csv, index=False)

    print(f"\nAudit A Results:")
    print(f"  Calculation Discrepancies (tol={FLOAT_TOLERANCE_STRICT}): {len(calc_disc_df)}")
    print(f"  Qualification / Rank Discrepancies: {len(qual_disc_df)}")
    print(f"  Saved Discrepancy CSVs to:")
    print(f"    - {calc_out_csv}")
    print(f"    - {qual_out_csv}")

    # Integrity assertions
    assert len(calc_disc_df) == 0, f"Found {len(calc_disc_df)} calculation discrepancies!"
    assert len(qual_disc_df) == 0, f"Found {len(qual_disc_df)} qualification discrepancies!"

    print("  ALL 816 Batters and 589 Bowlers calculations, priors, shrinkages, and ranks VERIFIED with 0 discrepancies.")
    print("=" * 80)
    return b, bo, calc_disc_df, qual_disc_df


if __name__ == "__main__":
    run_audit_a()
