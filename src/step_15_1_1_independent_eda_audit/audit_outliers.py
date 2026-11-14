import pandas as pd

def audit_24_outliers():
    anom = pd.read_csv('outputs/step_15_1_final_results_eda/outliers_and_anomalies.csv')
    batters = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv')
    bowlers = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv')
    
    audit_results = []
    
    for idx, r in anom.iterrows():
        disc = r['discipline']
        pid = r['player_id']
        name = r['player_name']
        rep_rank = r['tier_rank']
        rep_score = r['score']
        rep_n = r['sample_deliveries']
        rep_m = r['matches']
        cat = r['anomaly_category']
        
        if disc == 'Batting':
            src = batters[batters['player_id'] == pid].iloc[0]
            true_rank = src['tier1_rank_exp13']
            true_score = round(src['brs_3'], 2)
            true_n = src['high_balls_faced']
            true_m = src['hp_matches']
            is_match = (rep_rank == true_rank) and (rep_score == true_score) and (rep_n == true_n) and (rep_m == true_m)
        else:
            src = bowlers[bowlers['player_id'] == pid].iloc[0]
            true_rank = src['tier1_rank_exp13']
            true_score = round(src['bors'], 2)
            true_n = src['high_legal_balls']
            true_m = src['hp_matches']
            is_match = (rep_rank == true_rank) and (rep_score == true_score) and (rep_n == true_n) and (rep_m == true_m)
            
        audit_results.append({
            'index': idx + 1,
            'discipline': disc,
            'player_name': name,
            'player_id': pid,
            'category': cat,
            'reported_rank': rep_rank,
            'actual_rank': true_rank,
            'reported_score': rep_score,
            'actual_score': true_score,
            'reported_n': rep_n,
            'actual_n': true_n,
            'reported_m': rep_m,
            'actual_m': true_m,
            'data_verified': is_match
        })
        
    df_out = pd.DataFrame(audit_results)
    df_out.to_csv('outputs/step_15_1_1_independent_eda_audit/outliers_audit_verification.csv', index=False)
    print("Saved outliers_audit_verification.csv")
    print("All 24 outliers data match check:", df_out['data_verified'].all())
    if not df_out['data_verified'].all():
        print(df_out[~df_out['data_verified']])

if __name__ == '__main__':
    audit_24_outliers()
