import pandas as pd
import numpy as np

def compute_distributions_and_samples():
    batters = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv')
    bowlers = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv')
    
    # -------------------------------------------------------------
    # 1. BATTING SCORE DISTRIBUTION
    # -------------------------------------------------------------
    b_records = []
    tiers = ['Full Population', 'Tier 1: Qualified', 'Tier 2: Specialist', 'Below Threshold']
    
    for t in tiers:
        if t == 'Full Population':
            subset = batters['brs_3']
            sub_df = batters
        else:
            subset = batters[batters['tier_exp13'] == t]['brs_3']
            sub_df = batters[batters['tier_exp13'] == t]
            
        q25, q75 = subset.quantile(0.25), subset.quantile(0.75)
        iqr = q75 - q25
        
        # consecutive rank gaps
        sorted_scores = subset.sort_values(ascending=False).values
        gaps = np.diff(sorted_scores) * -1 if len(sorted_scores) > 1 else np.array([0])
        
        b_records.append({
            'group': t,
            'count': len(subset),
            'mean_score': np.round(subset.mean(), 2),
            'std_score': np.round(subset.std(), 2),
            'median_score': np.round(subset.median(), 2),
            'q25': np.round(q25, 2),
            'q75': np.round(q75, 2),
            'iqr': np.round(iqr, 2),
            'min_score': np.round(subset.min(), 2),
            'max_score': np.round(subset.max(), 2),
            'skewness': np.round(subset.skew(), 3),
            'kurtosis': np.round(subset.kurt(), 3),
            'mean_rank_gap': np.round(np.mean(gaps), 3) if len(gaps) > 0 else 0,
            'median_rank_gap': np.round(np.median(gaps), 3) if len(gaps) > 0 else 0,
            'max_rank_gap': np.round(np.max(gaps), 3) if len(gaps) > 0 else 0
        })
        
    b_dist_df = pd.DataFrame(b_records)
    b_dist_df.to_csv('outputs/step_15_1_final_results_eda/batting_score_distribution.csv', index=False)
    print("Saved batting_score_distribution.csv")
    
    # -------------------------------------------------------------
    # 2. BOWLING SCORE DISTRIBUTION
    # -------------------------------------------------------------
    bo_records = []
    for t in tiers:
        if t == 'Full Population':
            subset = bowlers['bors']
            sub_df = bowlers
        else:
            subset = bowlers[bowlers['tier_exp13'] == t]['bors']
            sub_df = bowlers[bowlers['tier_exp13'] == t]
            
        q25, q75 = subset.quantile(0.25), subset.quantile(0.75)
        iqr = q75 - q25
        
        sorted_scores = subset.sort_values(ascending=False).values
        gaps = np.diff(sorted_scores) * -1 if len(sorted_scores) > 1 else np.array([0])
        
        bo_records.append({
            'group': t,
            'count': len(subset),
            'mean_score': np.round(subset.mean(), 2),
            'std_score': np.round(subset.std(), 2),
            'median_score': np.round(subset.median(), 2),
            'q25': np.round(q25, 2),
            'q75': np.round(q75, 2),
            'iqr': np.round(iqr, 2),
            'min_score': np.round(subset.min(), 2),
            'max_score': np.round(subset.max(), 2),
            'skewness': np.round(subset.skew(), 3),
            'kurtosis': np.round(subset.kurt(), 3),
            'mean_rank_gap': np.round(np.mean(gaps), 3) if len(gaps) > 0 else 0,
            'median_rank_gap': np.round(np.median(gaps), 3) if len(gaps) > 0 else 0,
            'max_rank_gap': np.round(np.max(gaps), 3) if len(gaps) > 0 else 0
        })
        
    bo_dist_df = pd.DataFrame(bo_records)
    bo_dist_df.to_csv('outputs/step_15_1_final_results_eda/bowling_score_distribution.csv', index=False)
    print("Saved bowling_score_distribution.csv")
    
    # -------------------------------------------------------------
    # 3. BATTING SAMPLE ANALYSIS
    # -------------------------------------------------------------
    b_sample_records = []
    for t in tiers:
        if t == 'Full Population':
            sub = batters
        else:
            sub = batters[batters['tier_exp13'] == t]
            
        r_n_score = sub['high_balls_faced'].corr(sub['brs_3']) if len(sub) > 2 else 0
        r_m_score = sub['hp_matches'].corr(sub['brs_3']) if len(sub) > 2 else 0
        
        b_sample_records.append({
            'group': t,
            'player_count': len(sub),
            'mean_hp_balls': np.round(sub['high_balls_faced'].mean(), 1),
            'median_hp_balls': np.round(sub['high_balls_faced'].median(), 1),
            'min_hp_balls': sub['high_balls_faced'].min(),
            'max_hp_balls': sub['high_balls_faced'].max(),
            'mean_hp_matches': np.round(sub['hp_matches'].mean(), 1),
            'median_hp_matches': np.round(sub['hp_matches'].median(), 1),
            'min_hp_matches': sub['hp_matches'].min(),
            'max_hp_matches': sub['hp_matches'].max(),
            'corr_balls_vs_score': np.round(r_n_score, 3),
            'corr_matches_vs_score': np.round(r_m_score, 3)
        })
        
    b_sample_df = pd.DataFrame(b_sample_records)
    b_sample_df.to_csv('outputs/step_15_1_final_results_eda/batting_sample_analysis.csv', index=False)
    print("Saved batting_sample_analysis.csv")

    # -------------------------------------------------------------
    # 4. BOWLING SAMPLE ANALYSIS
    # -------------------------------------------------------------
    bo_sample_records = []
    for t in tiers:
        if t == 'Full Population':
            sub = bowlers
        else:
            sub = bowlers[bowlers['tier_exp13'] == t]
            
        r_n_score = sub['high_legal_balls'].corr(sub['bors']) if len(sub) > 2 else 0
        r_m_score = sub['hp_matches'].corr(sub['bors']) if len(sub) > 2 else 0
        
        bo_sample_records.append({
            'group': t,
            'player_count': len(sub),
            'mean_hp_balls': np.round(sub['high_legal_balls'].mean(), 1),
            'median_hp_balls': np.round(sub['high_legal_balls'].median(), 1),
            'min_hp_balls': sub['high_legal_balls'].min(),
            'max_hp_balls': sub['high_legal_balls'].max(),
            'mean_hp_matches': np.round(sub['hp_matches'].mean(), 1),
            'median_hp_matches': np.round(sub['hp_matches'].median(), 1),
            'min_hp_matches': sub['hp_matches'].min(),
            'max_hp_matches': sub['hp_matches'].max(),
            'corr_balls_vs_score': np.round(r_n_score, 3),
            'corr_matches_vs_score': np.round(r_m_score, 3)
        })
        
    bo_sample_df = pd.DataFrame(bo_sample_records)
    bo_sample_df.to_csv('outputs/step_15_1_final_results_eda/bowling_sample_analysis.csv', index=False)
    print("Saved bowling_sample_analysis.csv")

if __name__ == '__main__':
    compute_distributions_and_samples()
