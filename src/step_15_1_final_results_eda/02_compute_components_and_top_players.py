import pandas as pd
import numpy as np

def compute_components_and_top_players():
    batters = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv')
    bowlers = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv')
    
    t1_batters = batters[batters['tier_exp13'] == 'Tier 1: Qualified'].copy()
    t1_bowlers = bowlers[bowlers['tier_exp13'] == 'Tier 1: Qualified'].copy()
    
    # -------------------------------------------------------------
    # 1. BATTING COMPONENT ANALYSIS
    # -------------------------------------------------------------
    # Component statistics in Tier 1
    comps_b = ['score_sr', 'score_surv', 'score_diff', 'sr_star', 'out_star', 'diff_sr_star', 'brs_3']
    b_comp_summary = []
    
    for c in comps_b:
        s_all = batters[c]
        s_t1 = t1_batters[c]
        b_comp_summary.append({
            'metric': c,
            'full_mean': np.round(s_all.mean(), 2),
            'full_std': np.round(s_all.std(), 2),
            't1_mean': np.round(s_t1.mean(), 2),
            't1_std': np.round(s_t1.std(), 2),
            't1_median': np.round(s_t1.median(), 2),
            't1_min': np.round(s_t1.min(), 2),
            't1_max': np.round(s_t1.max(), 2),
            'corr_with_brs3_full': np.round(batters[c].corr(batters['brs_3']), 3),
            'corr_with_brs3_t1': np.round(t1_batters[c].corr(t1_batters['brs_3']), 3)
        })
    b_comp_df = pd.DataFrame(b_comp_summary)
    b_comp_df.to_csv('outputs/step_15_1_final_results_eda/batting_component_analysis.csv', index=False)
    print("Saved batting_component_analysis.csv")

    # -------------------------------------------------------------
    # 2. BOWLING COMPONENT ANALYSIS
    # -------------------------------------------------------------
    comps_bo = ['score_econ', 'score_wk', 'score_dot', 'score_diff', 'econ_star', 'wk_star', 'dot_bo_star', 'diff_econ_star', 'bors']
    bo_comp_summary = []
    
    for c in comps_bo:
        s_all = bowlers[c]
        s_t1 = t1_bowlers[c]
        bo_comp_summary.append({
            'metric': c,
            'full_mean': np.round(s_all.mean(), 2),
            'full_std': np.round(s_all.std(), 2),
            't1_mean': np.round(s_t1.mean(), 2),
            't1_std': np.round(s_t1.std(), 2),
            't1_median': np.round(s_t1.median(), 2),
            't1_min': np.round(s_t1.min(), 2),
            't1_max': np.round(s_t1.max(), 2),
            'corr_with_bors_full': np.round(bowlers[c].corr(bowlers['bors']), 3),
            'corr_with_bors_t1': np.round(t1_bowlers[c].corr(t1_bowlers['bors']), 3)
        })
    bo_comp_df = pd.DataFrame(bo_comp_summary)
    bo_comp_df.to_csv('outputs/step_15_1_final_results_eda/bowling_component_analysis.csv', index=False)
    print("Saved bowling_component_analysis.csv")

    # -------------------------------------------------------------
    # 3. TOP 10, TOP 20, TOP 50 BATTERS
    # -------------------------------------------------------------
    t1_batters_sorted = t1_batters.sort_values('tier1_rank_exp13').copy()
    top50_b = t1_batters_sorted.head(50).copy()
    
    # add cohort label
    top50_b['cohort'] = np.where(top50_b['tier1_rank_exp13'] <= 10, 'Top 10',
                        np.where(top50_b['tier1_rank_exp13'] <= 20, 'Top 11-20', 'Top 21-50'))
    
    cols_top_b = [
        'tier1_rank_exp13', 'cohort', 'player_id', 'player_name', 'brs_3',
        'high_balls_faced', 'hp_matches', 'score_sr', 'score_surv', 'score_diff',
        'sr_star', 'out_star', 'diff_sr_star', 'qualification_reason',
        'matches_played', 'strike_rate', 'high_strike_rate', 'high_batting_avg'
    ]
    top50_b[cols_top_b].to_csv('outputs/step_15_1_final_results_eda/batting_top10_top20_top50.csv', index=False)
    print("Saved batting_top10_top20_top50.csv")

    # -------------------------------------------------------------
    # 4. TOP 10, TOP 20, TOP 50 BOWLERS
    # -------------------------------------------------------------
    t1_bowlers_sorted = t1_bowlers.sort_values('tier1_rank_exp13').copy()
    top50_bo = t1_bowlers_sorted.head(50).copy()
    
    top50_bo['cohort'] = np.where(top50_bo['tier1_rank_exp13'] <= 10, 'Top 10',
                         np.where(top50_bo['tier1_rank_exp13'] <= 20, 'Top 11-20', 'Top 21-50'))
    
    cols_top_bo = [
        'tier1_rank_exp13', 'cohort', 'player_id', 'player_name', 'bors',
        'high_legal_balls', 'hp_matches', 'score_econ', 'score_wk', 'score_dot', 'score_diff',
        'econ_star', 'wk_star', 'dot_bo_star', 'diff_econ_star', 'qualification_reason',
        'matches_bowled', 'economy_rate', 'high_economy_rate', 'high_bowling_avg'
    ]
    top50_bo[cols_top_bo].to_csv('outputs/step_15_1_final_results_eda/bowling_top10_top20_top50.csv', index=False)
    print("Saved bowling_top10_top20_top50.csv")

if __name__ == '__main__':
    compute_components_and_top_players()
