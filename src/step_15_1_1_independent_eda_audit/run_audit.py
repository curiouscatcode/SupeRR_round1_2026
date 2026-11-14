import pandas as pd
import numpy as np

def audit():
    print("=== STARTING INDEPENDENT AUDIT OF STEP 15.1 EDA ===")
    
    # Load primary Step 13 files
    batters_path = 'outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv'
    bowlers_path = 'outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv'
    b_comp_path = 'outputs/step_13_experimental_ranking_model/exp13_batter_comparison.csv'
    bo_comp_path = 'outputs/step_13_experimental_ranking_model/exp13_bowler_comparison.csv'
    
    batters = pd.read_csv(batters_path)
    bowlers = pd.read_csv(bowlers_path)
    
    # -------------------------------------------------------------
    # 1. POPULATION AND QUALIFICATION COUNTS
    # -------------------------------------------------------------
    print("\n--- 1. Population & Qualification Counts ---")
    print(f"Total Batters: {len(batters)}")
    print(f"Total Bowlers: {len(bowlers)}")
    
    b_tier_counts = batters['tier_exp13'].value_counts()
    bo_tier_counts = bowlers['tier_exp13'].value_counts()
    print("Batter Tiers:\n", b_tier_counts)
    print("Bowler Tiers:\n", bo_tier_counts)
    
    # Rule B breakdown
    t1_b = batters[batters['tier_exp13'] == 'Tier 1: Qualified']
    t1_bo = bowlers[bowlers['tier_exp13'] == 'Tier 1: Qualified']
    
    b_base = len(t1_b[t1_b['high_balls_faced'] >= 60])
    b_hb = len(t1_b[(t1_b['high_balls_faced'] >= 50) & (t1_b['high_balls_faced'] < 60) & (t1_b['hp_matches'] >= 6)])
    
    bo_base = len(t1_bo[t1_bo['high_legal_balls'] >= 60])
    bo_hb = len(t1_bo[(t1_bo['high_legal_balls'] >= 50) & (t1_bo['high_legal_balls'] < 60) & (t1_bo['hp_matches'] >= 6)])
    
    print(f"Batters Tier 1: Baseline N>=60: {b_base}, Rule B High-Breadth (50-59 & M>=6): {b_hb}, Total T1: {b_base + b_hb}")
    print(f"Bowlers Tier 1: Baseline N>=60: {bo_base}, Rule B High-Breadth (50-59 & M>=6): {bo_hb}, Total T1: {bo_base + bo_hb}")
    
    # -------------------------------------------------------------
    # 2. SCORE GAPS RECALCULATION
    # -------------------------------------------------------------
    print("\n--- 2. Score Gaps Recalculation ---")
    t1_b_sorted = t1_b.sort_values('tier1_rank_exp13').reset_index(drop=True)
    t1_bo_sorted = t1_bo.sort_values('tier1_rank_exp13').reset_index(drop=True)
    
    dhoni_score = t1_b_sorted.loc[0, 'brs_3']
    dube_score = t1_b_sorted.loc[1, 'brs_3']
    gap_dhoni_dube = dhoni_score - dube_score
    print(f"Dhoni ({dhoni_score:.4f}) vs Dube ({dube_score:.4f}) gap: {gap_dhoni_dube:.4f} (Reported: 11.20)")
    
    southee_score = t1_bo_sorted.loc[0, 'bors']
    nasum_score = t1_bo_sorted.loc[1, 'bors']
    maharaj_score = t1_bo_sorted.loc[2, 'bors']
    gap_southee_nasum = southee_score - nasum_score
    gap_nasum_maharaj = nasum_score - maharaj_score
    gap_top2_maharaj = min(southee_score, nasum_score) - maharaj_score
    print(f"Southee ({southee_score:.4f}) vs Nasum ({nasum_score:.4f}) gap: {gap_southee_nasum:.4f} (Reported: 1.85)")
    print(f"Nasum ({nasum_score:.4f}) vs Maharaj ({maharaj_score:.4f}) gap: {gap_nasum_maharaj:.4f} (Reported: 8.90)")
    
    # Batting ranks 20 to 80 gaps
    # Ranks 20 to 80 in t1_b_sorted: indices 19 to 79 (inclusive)
    ranks_20_80_scores = t1_b_sorted.loc[19:79, 'brs_3'].values
    gaps_20_80 = np.diff(ranks_20_80_scores) * -1
    print(f"Batting Ranks 20-80 consecutive gaps: mean={np.mean(gaps_20_80):.4f}, median={np.median(gaps_20_80):.4f}, min={np.min(gaps_20_80):.4f}, max={np.max(gaps_20_80):.4f} (Reported median: 0.18)")

    # -------------------------------------------------------------
    # 3. RULE B ENTRANTS AND MATCH COVERAGE
    # -------------------------------------------------------------
    print("\n--- 3. Rule B Entrant Counts and Match Coverage ---")
    hb_batters = t1_b[(t1_b['high_balls_faced'] >= 50) & (t1_b['high_balls_faced'] < 60) & (t1_b['hp_matches'] >= 6)]
    hb_bowlers = t1_bo[(t1_bo['high_legal_balls'] >= 50) & (t1_bo['high_legal_balls'] < 60) & (t1_bo['hp_matches'] >= 6)]
    
    print(f"Rule B Batters count: {len(hb_batters)}")
    print(f"Batters mean matches: {hb_batters['hp_matches'].mean():.2f}, median: {hb_batters['hp_matches'].median():.2f}, min: {hb_batters['hp_matches'].min()}, max: {hb_batters['hp_matches'].max()}")
    
    print(f"Rule B Bowlers count: {len(hb_bowlers)}")
    print(f"Bowlers mean matches: {hb_bowlers['hp_matches'].mean():.2f}, median: {hb_bowlers['hp_matches'].median():.2f}, min: {hb_bowlers['hp_matches'].min()}, max: {hb_bowlers['hp_matches'].max()}")
    
    # Combined mean matches
    all_hb_matches = pd.concat([hb_batters['hp_matches'], hb_bowlers['hp_matches']])
    print(f"Combined mean matches across all 47 Rule B qualifiers: {all_hb_matches.mean():.2f}")
    
    # Also check: what about boundary zone N in [50, 59]? Did anyone have M < 6?
    b_50_59_all = batters[(batters['high_balls_faced'] >= 50) & (batters['high_balls_faced'] < 60)]
    bo_50_59_all = bowlers[(bowlers['high_legal_balls'] >= 50) & (bowlers['high_legal_balls'] < 60)]
    print(f"Batters with N in [50, 59]: Total={len(b_50_59_all)}, Qualified (M>=6)={len(hb_batters)}, Disqualified (M<6)={len(b_50_59_all) - len(hb_batters)}")
    print(f"Bowlers with N in [50, 59]: Total={len(bo_50_59_all)}, Qualified (M>=6)={len(hb_bowlers)}, Disqualified (M<6)={len(bo_50_59_all) - len(hb_bowlers)}")

    # -------------------------------------------------------------
    # 4. COMPONENT CORRELATIONS
    # -------------------------------------------------------------
    print("\n--- 4. Component Correlations ---")
    corr_b_sr = t1_b['score_sr'].corr(t1_b['brs_3'])
    corr_b_surv = t1_b['score_surv'].corr(t1_b['brs_3'])
    corr_b_diff = t1_b['score_diff'].corr(t1_b['brs_3'])
    print(f"Batting Tier 1 correlations with BRS3:")
    print(f"  score_sr (wt 0.45): {corr_b_sr:.4f} (Reported: +0.909)")
    print(f"  score_surv (wt 0.35): {corr_b_surv:.4f} (Reported: +0.713)")
    print(f"  score_diff (wt 0.20): {corr_b_diff:.4f} (Reported: +0.671)")
    
    corr_bo_econ = t1_bo['score_econ'].corr(t1_bo['bors'])
    corr_bo_wk = t1_bo['score_wk'].corr(t1_bo['bors'])
    corr_bo_dot = t1_bo['score_dot'].corr(t1_bo['bors'])
    corr_bo_diff = t1_bo['score_diff'].corr(t1_bo['bors'])
    print(f"Bowling Tier 1 correlations with BoRS:")
    print(f"  score_econ (wt 0.40): {corr_bo_econ:.4f} (Reported: +0.822)")
    print(f"  score_wk (wt 0.25): {corr_bo_wk:.4f} (Reported: +0.636)")
    print(f"  score_dot (wt 0.20): {corr_bo_dot:.4f} (Reported: +0.727)")
    print(f"  score_diff (wt 0.15): {corr_bo_diff:.4f} (Reported: +0.694)")

    # -------------------------------------------------------------
    # 5. PHASE FINDINGS AUDIT
    # -------------------------------------------------------------
    print("\n--- 5. Phase Findings Audit ---")
    # Bowling Powerplay share
    # Method A: Player-level unweighted mean of % PP balls
    t1_bo = t1_bo.copy()
    t1_bo['pct_pp'] = (t1_bo['lb_pp_high'] / t1_bo['high_legal_balls']) * 100
    print(f"Bowling Tier 1 (N=130): Unweighted player-level mean of PP %: {t1_bo['pct_pp'].mean():.2f}% (Reported: 59.1%)")
    print(f"Bowling Tier 1 (N=130): Median of PP %: {t1_bo['pct_pp'].median():.2f}% (Reported: 67.6%)")
    
    # Method B: Aggregate delivery-level weighted share across all Tier 1 bowlers
    total_pp_balls_t1 = t1_bo['lb_pp_high'].sum()
    total_hp_balls_t1 = t1_bo['high_legal_balls'].sum()
    pct_agg_pp_t1 = (total_pp_balls_t1 / total_hp_balls_t1) * 100
    print(f"Bowling Tier 1 (N=130): Aggregate delivery-level PP share: {total_pp_balls_t1} / {total_hp_balls_t1} = {pct_agg_pp_t1:.2f}%")
    
    # Method C: Across ALL 589 bowlers
    total_pp_balls_all = bowlers['lb_pp_high'].sum()
    total_hp_balls_all = bowlers['high_legal_balls'].sum()
    pct_agg_pp_all = (total_pp_balls_all / total_hp_balls_all) * 100
    print(f"Bowling Full Population (N=589): Aggregate delivery-level PP share: {total_pp_balls_all} / {total_hp_balls_all} = {pct_agg_pp_all:.2f}%")

    # Batting Death Over exposure and correlation
    t1_b = t1_b.copy()
    t1_b['pct_do'] = (t1_b['bf_do_high'] / t1_b['high_balls_faced']) * 100
    corr_do_brs3 = t1_b['pct_do'].corr(t1_b['brs_3'])
    print(f"Batting Tier 1 (N=146): Unweighted player-level mean of Death %: {t1_b['pct_do'].mean():.2f}% (Reported: 38.2%)")
    print(f"Batting Tier 1 (N=146): Correlation of pct_do with BRS3: {corr_do_brs3:.4f} (Reported: -0.435)")
    
    total_do_balls_t1_b = t1_b['bf_do_high'].sum()
    total_hp_balls_t1_b = t1_b['high_balls_faced'].sum()
    pct_agg_do_t1_b = (total_do_balls_t1_b / total_hp_balls_t1_b) * 100
    print(f"Batting Tier 1 (N=146): Aggregate delivery-level Death share: {total_do_balls_t1_b} / {total_hp_balls_t1_b} = {pct_agg_do_t1_b:.2f}%")

    # -------------------------------------------------------------
    # 6. CLUTCH DIFFERENTIALS VERIFICATION
    # -------------------------------------------------------------
    print("\n--- 6. Clutch Differentials Verification ---")
    jo_b = batters[batters['player_id'] == 2382].iloc[0]
    print(f"Jamie Overton Batting:")
    print(f"  Observed High SR: {jo_b['high_strike_rate']:.2f}")
    print(f"  Observed Low/Mod SR: {jo_b['low_mod_strike_rate']:.2f}")
    print(f"  Raw SR Delta (Obs High - Obs Low): {jo_b['strike_rate_delta']:.2f} (Reported: +50.95)")
    print(f"  Regularized High SR (sr_star): {jo_b['sr_star']:.4f}")
    print(f"  Regularized Low SR (sr_low_star): {jo_b['sr_low_star']:.4f}")
    print(f"  Regularized Differential (diff_sr_star): {jo_b['diff_sr_star']:.4f} (Reported: +16.05)")

    southee_bo = bowlers[bowlers['player_id'] == 278].iloc[0]
    print(f"\nTim Southee Bowling:")
    print(f"  Observed High Econ: {southee_bo['high_economy_rate']:.2f}")
    print(f"  Observed Low/Mod Econ: {southee_bo['low_mod_economy_rate']:.2f}")
    print(f"  Raw Econ Delta (Low - High): {southee_bo['low_mod_economy_rate'] - southee_bo['high_economy_rate']:.2f} (Reported economy gain: +3.87)")
    print(f"  Regularized High Econ (econ_star): {southee_bo['econ_star']:.4f}")
    print(f"  Regularized Low Econ (econ_low_star): {southee_bo['econ_low_star']:.4f}")
    print(f"  Regularized Differential (diff_econ_star): {southee_bo['diff_econ_star']:.4f} (Reported: +1.73)")

if __name__ == '__main__':
    audit()
