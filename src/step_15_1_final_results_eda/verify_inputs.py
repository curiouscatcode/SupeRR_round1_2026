import pandas as pd
import numpy as np

def verify():
    batters_path = 'outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv'
    bowlers_path = 'outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv'
    
    batters = pd.read_csv(batters_path)
    bowlers = pd.read_csv(bowlers_path)
    
    print("=== INPUT DATA VERIFICATION ===")
    print(f"Batter file: {batters_path} (rows: {len(batters)}, unique players: {batters['player_id'].nunique()})")
    print(f"Bowler file: {bowlers_path} (rows: {len(bowlers)}, unique players: {bowlers['player_id'].nunique()})")
    
    assert len(batters) == 816, f"Expected 816 batters, got {len(batters)}"
    assert len(bowlers) == 589, f"Expected 589 bowlers, got {len(bowlers)}"
    
    # Tier breakdown
    print("\n--- Batter Tiers ---")
    b_tiers = batters['tier_exp13'].value_counts()
    print(b_tiers)
    
    print("\n--- Bowler Tiers ---")
    bo_tiers = bowlers['tier_exp13'].value_counts()
    print(bo_tiers)
    
    # Formula check BRS3
    # BRS3 = 0.45 * score_sr + 0.35 * score_surv + 0.20 * score_diff
    brs3_calc = 0.45 * batters['score_sr'] + 0.35 * batters['score_surv'] + 0.20 * batters['score_diff']
    max_brs3_diff = np.max(np.abs(brs3_calc - batters['brs_3']))
    print(f"\nMax diff between calculated BRS3 and brs_3 column: {max_brs3_diff:.8f}")
    assert max_brs3_diff < 1e-5, "BRS3 formula mismatch!"
    
    # Formula check BoRS
    # BoRS = 0.40 * score_econ + 0.25 * score_wk + 0.20 * score_dot + 0.15 * score_diff
    bors_calc = 0.40 * bowlers['score_econ'] + 0.25 * bowlers['score_wk'] + 0.20 * bowlers['score_dot'] + 0.15 * bowlers['score_diff']
    max_bors_diff = np.max(np.abs(bors_calc - bowlers['bors']))
    print(f"Max diff between calculated BoRS and bors column: {max_bors_diff:.8f}")
    assert max_bors_diff < 1e-5, "BoRS formula mismatch!"
    
    # Check Rule B qualification
    # Batters
    t1_cond_b = (batters['high_balls_faced'] >= 60) | ((batters['high_balls_faced'] >= 50) & (batters['hp_matches'] >= 6))
    t2_cond_b = (~t1_cond_b) & (batters['high_balls_faced'] >= 40)
    below_cond_b = batters['high_balls_faced'] < 40
    
    assert (batters.loc[t1_cond_b, 'tier_exp13'] == 'Tier 1: Qualified').all()
    assert (batters.loc[t2_cond_b, 'tier_exp13'] == 'Tier 2: Specialist').all()
    assert (batters.loc[below_cond_b, 'tier_exp13'] == 'Below Threshold').all()
    print("Batter Rule B tier assignments: 100% verified.")
    
    # Bowlers
    t1_cond_bo = (bowlers['high_legal_balls'] >= 60) | ((bowlers['high_legal_balls'] >= 50) & (bowlers['hp_matches'] >= 6))
    t2_cond_bo = (~t1_cond_bo) & (bowlers['high_legal_balls'] >= 40)
    below_cond_bo = bowlers['high_legal_balls'] < 40
    
    assert (bowlers.loc[t1_cond_bo, 'tier_exp13'] == 'Tier 1: Qualified').all()
    assert (bowlers.loc[t2_cond_bo, 'tier_exp13'] == 'Tier 2: Specialist').all()
    assert (bowlers.loc[below_cond_bo, 'tier_exp13'] == 'Below Threshold').all()
    print("Bowler Rule B tier assignments: 100% verified.")
    
    # Check Jamie Overton
    jo_b = batters[batters['player_id'] == 2382].iloc[0]
    jo_bo = bowlers[bowlers['player_id'] == 2382].iloc[0]
    print(f"\nJamie Overton Batting: Tier='{jo_b['tier_exp13']}', Tier 1 Rank={jo_b['tier1_rank_exp13']}, BRS3={jo_b['brs_3']:.2f}, N={jo_b['high_balls_faced']}, M={jo_b['hp_matches']}")
    print(f"Jamie Overton Bowling: Tier='{jo_bo['tier_exp13']}', Overall Rank={jo_bo['overall_rank_exp13']}, BoRS={jo_bo['bors']:.2f}, N={jo_bo['high_legal_balls']}, M={jo_bo['hp_matches']}")
    
    # Check Top 10 Batters & Bowlers
    print("\n--- Verified Top 10 Batters ---")
    t1_b_top10 = batters[batters['tier_exp13'] == 'Tier 1: Qualified'].sort_values('tier1_rank_exp13').head(10)
    for idx, r in t1_b_top10.iterrows():
        print(f"Rank {int(r['tier1_rank_exp13'])}: {r['player_name']} (BRS3={r['brs_3']:.2f}, N={int(r['high_balls_faced'])}, M={int(r['hp_matches'])})")

    print("\n--- Verified Top 10 Bowlers ---")
    t1_bo_top10 = bowlers[bowlers['tier_exp13'] == 'Tier 1: Qualified'].sort_values('tier1_rank_exp13').head(10)
    for idx, r in t1_bo_top10.iterrows():
        print(f"Rank {int(r['tier1_rank_exp13'])}: {r['player_name']} (BoRS={r['bors']:.2f}, N={int(r['high_legal_balls'])}, M={int(r['hp_matches'])})")

if __name__ == '__main__':
    verify()
