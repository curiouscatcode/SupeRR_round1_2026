import pandas as pd
import numpy as np

def compute_comparisons_and_phases():
    batters = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv')
    bowlers = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv')
    b_comp = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_batter_comparison.csv')
    bo_comp = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_bowler_comparison.csv')
    
    # -------------------------------------------------------------
    # 1. ORIGINAL VS CANDIDATE BATTING
    # -------------------------------------------------------------
    # Merge official and exp13 metrics
    b_comp_clean = b_comp[[
        'player_id', 'player_name', 'high_balls_faced', 'hp_matches',
        'brs_official', 'tier_official', 'tier1_rank_official', 'overall_rank_official',
        'brs_3', 'tier_exp13', 'tier1_rank_exp13', 'overall_rank_exp13',
        'score_sr', 'score_surv', 'score_exec', 'score_diff'
    ]].copy()
    
    b_comp_clean['score_delta'] = np.round(b_comp_clean['brs_3'] - b_comp_clean['brs_official'], 2)
    b_comp_clean['overall_rank_delta'] = b_comp_clean['overall_rank_official'] - b_comp_clean['overall_rank_exp13']
    b_comp_clean['tier1_rank_delta'] = b_comp_clean['tier1_rank_official'] - b_comp_clean['tier1_rank_exp13']
    
    # Tier transition type
    def get_tier_transition(row):
        t_old = str(row['tier_official'])
        t_new = str(row['tier_exp13'])
        if t_old == t_new:
            return f"Retained {t_new}"
        return f"{t_old} -> {t_new}"
    
    b_comp_clean['tier_transition'] = b_comp_clean.apply(get_tier_transition, axis=1)
    b_comp_clean.to_csv('outputs/step_15_1_final_results_eda/original_vs_candidate_batting.csv', index=False)
    print("Saved original_vs_candidate_batting.csv")

    # -------------------------------------------------------------
    # 2. ORIGINAL VS CANDIDATE BOWLING
    # -------------------------------------------------------------
    bo_comp_clean = bo_comp[[
        'player_id', 'player_name', 'high_legal_balls', 'hp_matches',
        'bors_official', 'tier_official', 'tier1_rank_official', 'overall_rank_official',
        'bors_exp13', 'tier_exp13', 'tier1_rank_exp13', 'overall_rank_exp13',
        'score_econ', 'score_wk', 'score_dot', 'score_diff'
    ]].copy()
    bo_comp_clean.rename(columns={'bors_exp13': 'bors'}, inplace=True)
    
    bo_comp_clean['score_delta'] = np.round(bo_comp_clean['bors'] - bo_comp_clean['bors_official'], 2)
    bo_comp_clean['overall_rank_delta'] = bo_comp_clean['overall_rank_official'] - bo_comp_clean['overall_rank_exp13']
    bo_comp_clean['tier1_rank_delta'] = bo_comp_clean['tier1_rank_official'] - bo_comp_clean['tier1_rank_exp13']
    bo_comp_clean['tier_transition'] = bo_comp_clean.apply(get_tier_transition, axis=1)
    bo_comp_clean.to_csv('outputs/step_15_1_final_results_eda/original_vs_candidate_bowling.csv', index=False)
    print("Saved original_vs_candidate_bowling.csv")

    # -------------------------------------------------------------
    # 3. PHASE-WISE ANALYSIS
    # -------------------------------------------------------------
    # Batters phase metrics
    phase_records = []
    
    # Batting phase exposure
    t1_b = batters[batters['tier_exp13'] == 'Tier 1: Qualified'].copy()
    t1_b['pct_hp_pp'] = np.round(t1_b['bf_pp_high'] / t1_b['high_balls_faced'] * 100, 1)
    t1_b['pct_hp_mo'] = np.round(t1_b['bf_mo_high'] / t1_b['high_balls_faced'] * 100, 1)
    t1_b['pct_hp_do'] = np.round(t1_b['bf_do_high'] / t1_b['high_balls_faced'] * 100, 1)
    
    # Bowlers phase exposure
    t1_bo = bowlers[bowlers['tier_exp13'] == 'Tier 1: Qualified'].copy()
    t1_bo['pct_hp_pp'] = np.round(t1_bo['lb_pp_high'] / t1_bo['high_legal_balls'] * 100, 1)
    t1_bo['pct_hp_mo'] = np.round(t1_bo['lb_mo_high'] / t1_bo['high_legal_balls'] * 100, 1)
    t1_bo['pct_hp_do'] = np.round(t1_bo['lb_do_high'] / t1_bo['high_legal_balls'] * 100, 1)
    
    # Summary of phase distribution across Tier 1
    phase_summary = [
        {
            'discipline': 'Batting (Tier 1, N=146)',
            'phase': 'Powerplay (Overs 1-6)',
            'mean_hp_deliveries': np.round(t1_b['bf_pp_high'].mean(), 1),
            'median_hp_deliveries': np.round(t1_b['bf_pp_high'].median(), 1),
            'mean_share_pct': np.round(t1_b['pct_hp_pp'].mean(), 1),
            'median_share_pct': np.round(t1_b['pct_hp_pp'].median(), 1),
            'corr_share_with_score': np.round(t1_b['pct_hp_pp'].corr(t1_b['brs_3']), 3)
        },
        {
            'discipline': 'Batting (Tier 1, N=146)',
            'phase': 'Middle Overs (Overs 7-15)',
            'mean_hp_deliveries': np.round(t1_b['bf_mo_high'].mean(), 1),
            'median_hp_deliveries': np.round(t1_b['bf_mo_high'].median(), 1),
            'mean_share_pct': np.round(t1_b['pct_hp_mo'].mean(), 1),
            'median_share_pct': np.round(t1_b['pct_hp_mo'].median(), 1),
            'corr_share_with_score': np.round(t1_b['pct_hp_mo'].corr(t1_b['brs_3']), 3)
        },
        {
            'discipline': 'Batting (Tier 1, N=146)',
            'phase': 'Death Overs (Overs 16-20)',
            'mean_hp_deliveries': np.round(t1_b['bf_do_high'].mean(), 1),
            'median_hp_deliveries': np.round(t1_b['bf_do_high'].median(), 1),
            'mean_share_pct': np.round(t1_b['pct_hp_do'].mean(), 1),
            'median_share_pct': np.round(t1_b['pct_hp_do'].median(), 1),
            'corr_share_with_score': np.round(t1_b['pct_hp_do'].corr(t1_b['brs_3']), 3)
        },
        {
            'discipline': 'Bowling (Tier 1, N=130)',
            'phase': 'Powerplay (Overs 1-6)',
            'mean_hp_deliveries': np.round(t1_bo['lb_pp_high'].mean(), 1),
            'median_hp_deliveries': np.round(t1_bo['lb_pp_high'].median(), 1),
            'mean_share_pct': np.round(t1_bo['pct_hp_pp'].mean(), 1),
            'median_share_pct': np.round(t1_bo['pct_hp_pp'].median(), 1),
            'corr_share_with_score': np.round(t1_bo['pct_hp_pp'].corr(t1_bo['bors']), 3)
        },
        {
            'discipline': 'Bowling (Tier 1, N=130)',
            'phase': 'Middle Overs (Overs 7-15)',
            'mean_hp_deliveries': np.round(t1_bo['lb_mo_high'].mean(), 1),
            'median_hp_deliveries': np.round(t1_bo['lb_mo_high'].median(), 1),
            'mean_share_pct': np.round(t1_bo['pct_hp_mo'].mean(), 1),
            'median_share_pct': np.round(t1_bo['pct_hp_mo'].median(), 1),
            'corr_share_with_score': np.round(t1_bo['pct_hp_mo'].corr(t1_bo['bors']), 3)
        },
        {
            'discipline': 'Bowling (Tier 1, N=130)',
            'phase': 'Death Overs (Overs 16-20)',
            'mean_hp_deliveries': np.round(t1_bo['lb_do_high'].mean(), 1),
            'median_hp_deliveries': np.round(t1_bo['lb_do_high'].median(), 1),
            'mean_share_pct': np.round(t1_bo['pct_hp_do'].mean(), 1),
            'median_share_pct': np.round(t1_bo['pct_hp_do'].median(), 1),
            'corr_share_with_score': np.round(t1_bo['pct_hp_do'].corr(t1_bo['bors']), 3)
        }
    ]
    pd.DataFrame(phase_summary).to_csv('outputs/step_15_1_final_results_eda/phase_wise_analysis.csv', index=False)
    print("Saved phase_wise_analysis.csv")

    # -------------------------------------------------------------
    # 4. OUTLIERS AND ANOMALIES
    # -------------------------------------------------------------
    anomalies = []
    
    # 4a. Batting: High Score + Low Sample in Tier 1
    low_sample_high_score_b = t1_b[(t1_b['high_balls_faced'] < 65) & (t1_b['brs_3'] >= 75.0)]
    for _, r in low_sample_high_score_b.iterrows():
        anomalies.append({
            'discipline': 'Batting',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'tier': r['tier_exp13'],
            'tier_rank': r['tier1_rank_exp13'],
            'score': np.round(r['brs_3'], 2),
            'sample_deliveries': int(r['high_balls_faced']),
            'matches': int(r['hp_matches']),
            'anomaly_category': 'High Score with Boundary Sample (N in 50-65)',
            'details': f"BRS3={r['brs_3']:.2f}, N={int(r['high_balls_faced'])}, M={int(r['hp_matches'])}, SR*={r['sr_star']:.1f}, Diff*={r['diff_sr_star']:+.1f}"
        })

    # 4b. Bowling: High Score + Low Sample in Tier 1
    low_sample_high_score_bo = t1_bo[(t1_bo['high_legal_balls'] < 65) & (t1_bo['bors'] >= 75.0)]
    for _, r in low_sample_high_score_bo.iterrows():
        anomalies.append({
            'discipline': 'Bowling',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'tier': r['tier_exp13'],
            'tier_rank': r['tier1_rank_exp13'],
            'score': np.round(r['bors'], 2),
            'sample_deliveries': int(r['high_legal_balls']),
            'matches': int(r['hp_matches']),
            'anomaly_category': 'High Score with Boundary Sample (N in 50-65)',
            'details': f"BoRS={r['bors']:.2f}, N={int(r['high_legal_balls'])}, M={int(r['hp_matches'])}, Econ*={r['econ_star']:.2f}, Dot*={r['dot_bo_star']:.1f}%"
        })

    # 4c. Batting: Extreme Component Conflicts
    # High SR (> 145) but poor survival (Score_Surv < 45)
    conf_b1 = t1_b[(t1_b['sr_star'] >= 140.0) & (t1_b['score_surv'] < 50.0)]
    for _, r in conf_b1.iterrows():
        anomalies.append({
            'discipline': 'Batting',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'tier': r['tier_exp13'],
            'tier_rank': r['tier1_rank_exp13'],
            'score': np.round(r['brs_3'], 2),
            'sample_deliveries': int(r['high_balls_faced']),
            'matches': int(r['hp_matches']),
            'anomaly_category': 'High Aggression / Vulnerable Survival Conflict',
            'details': f"SR*={r['sr_star']:.1f} (Score {r['score_sr']:.1f}) but Out*={r['out_star']:.1f}% (Score {r['score_surv']:.1f})"
        })

    # High Survival (> 80 score) but low SR (< 115)
    conf_b2 = t1_b[(t1_b['score_surv'] >= 75.0) & (t1_b['sr_star'] < 112.0)]
    for _, r in conf_b2.iterrows():
        anomalies.append({
            'discipline': 'Batting',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'tier': r['tier_exp13'],
            'tier_rank': r['tier1_rank_exp13'],
            'score': np.round(r['brs_3'], 2),
            'sample_deliveries': int(r['high_balls_faced']),
            'matches': int(r['hp_matches']),
            'anomaly_category': 'Ultra Anchor / Sub-Par Acceleration Conflict',
            'details': f"Out*={r['out_star']:.1f}% (Score {r['score_surv']:.1f}) but SR*={r['sr_star']:.1f} (Score {r['score_sr']:.1f})"
        })

    # 4d. Bowling: Extreme Component Conflicts
    # Elite Economy (< 7.5) but Low Wickets (< 4.0%)
    conf_bo1 = t1_bo[(t1_bo['econ_star'] <= 7.50) & (t1_bo['wk_star'] < 4.50)]
    for _, r in conf_bo1.iterrows():
        anomalies.append({
            'discipline': 'Bowling',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'tier': r['tier_exp13'],
            'tier_rank': r['tier1_rank_exp13'],
            'score': np.round(r['bors'], 2),
            'sample_deliveries': int(r['high_legal_balls']),
            'matches': int(r['hp_matches']),
            'anomaly_category': 'Elite Economy / Low Wicket Strike Conflict',
            'details': f"Econ*={r['econ_star']:.2f} (Score {r['score_econ']:.1f}) but Wk*={r['wk_star']:.1f}% (Score {r['score_wk']:.1f})"
        })

    # High Wickets (> 7.5%) but Expensive Economy (> 9.0)
    conf_bo2 = t1_bo[(t1_bo['wk_star'] >= 7.00) & (t1_bo['econ_star'] >= 9.00)]
    for _, r in conf_bo2.iterrows():
        anomalies.append({
            'discipline': 'Bowling',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'tier': r['tier_exp13'],
            'tier_rank': r['tier1_rank_exp13'],
            'score': np.round(r['bors'], 2),
            'sample_deliveries': int(r['high_legal_balls']),
            'matches': int(r['hp_matches']),
            'anomaly_category': 'Wicket-Taker / Expensive Economy Conflict',
            'details': f"Wk*={r['wk_star']:.1f}% (Score {r['score_wk']:.1f}) but Econ*={r['econ_star']:.2f} (Score {r['score_econ']:.1f})"
        })

    pd.DataFrame(anomalies).to_csv('outputs/step_15_1_final_results_eda/outliers_and_anomalies.csv', index=False)
    print("Saved outliers_and_anomalies.csv")

if __name__ == '__main__':
    compute_comparisons_and_phases()
