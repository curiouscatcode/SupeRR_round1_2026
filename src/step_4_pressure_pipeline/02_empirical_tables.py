"""
Step 4 - Module 2: Pre-computed Empirical Reference Tables
==========================================================
Computes and freezes the empirical reference tables across the 782-match cohort:
1. Empirical Bayes Venue Par (K = 8.0 shrinkage)
2. Regularized Empirical Wicket Progression Tables (mu_W, sigma_W with floor 0.50)
3. Player-Independent Outcome Transition Probabilities (6 strata, verified sum = 1.0)
"""

import os
import json
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_4_pressure_pipeline"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_empirical_tables():
    cohort_path = os.path.join(OUTPUT_DIR, "clean_cohort_deliveries.parquet")
    df = pd.read_parquet(cohort_path)
    
    # -------------------------------------------------------------
    # 1. Empirical Bayes Venue Par Calculation
    # -------------------------------------------------------------
    print("--- 1. Computing Empirical Bayes Venue Par (K=8.0) ---")
    inn1 = df[df['innings'] == 1].copy()
    
    last_balls = inn1.groupby('match_id').last()[['score_before', 'team_runs_added', 'venue_id']].reset_index()
    last_balls['first_inn_total'] = last_balls['score_before'] + last_balls['team_runs_added']
    global_par = float(last_balls['first_inn_total'].mean())
    print(f"Global first innings mean total across 782 matches: {global_par:.2f} runs")
    
    v_agg = last_balls.groupby('venue_id')['first_inn_total'].agg(['count', 'mean']).reset_index()
    K_shrink = 8.0
    v_agg['venue_par'] = (v_agg['count'] * v_agg['mean'] + K_shrink * global_par) / (v_agg['count'] + K_shrink)
    
    venue_par_dict = {int(k): float(v) for k, v in zip(v_agg['venue_id'], v_agg['venue_par'])}
    venue_par_dict['GLOBAL_DEFAULT'] = float(global_par)
    
    venue_par_json = os.path.join(OUTPUT_DIR, "empirical_venue_par.json")
    with open(venue_par_json, 'w', encoding='utf-8') as f:
        json.dump(venue_par_dict, f, indent=2)
    print(f"Saved venue par table ({len(venue_par_dict)-1} venues) to {venue_par_json}")
    
    # -------------------------------------------------------------
    # 2. Regularized Empirical Wicket Progression Tables
    # -------------------------------------------------------------
    print("\n--- 2. Computing Regularized Empirical Wicket Progression ---")
    w_stats = df.groupby('legal_balls_before')['W_t'].agg(['count', 'mean', 'std']).reset_index()
    w_stats['std'] = w_stats['std'].fillna(0.0)
    w_stats['regularized_std'] = w_stats['std'].clip(lower=0.50)
    
    # Ensure ball 0.1 (legal_balls_before = 0) has exact neutral values
    w_stats.loc[w_stats['legal_balls_before'] == 0, 'mean'] = 0.0
    w_stats.loc[w_stats['legal_balls_before'] == 0, 'regularized_std'] = 0.50
    
    wicket_table_csv = os.path.join(OUTPUT_DIR, "empirical_wicket_curve.csv")
    w_stats.to_csv(wicket_table_csv, index=False)
    print(f"Saved regularized wicket progression table (balls 0-119) to {wicket_table_csv}")
    print(f"  Ball   0: mu_W = {w_stats.loc[w_stats['legal_balls_before']==0, 'mean'].values[0]:.2f}, reg_sigma = {w_stats.loc[w_stats['legal_balls_before']==0, 'regularized_std'].values[0]:.2f}")
    print(f"  Ball  60: mu_W = {w_stats.loc[w_stats['legal_balls_before']==60, 'mean'].values[0]:.2f}, reg_sigma = {w_stats.loc[w_stats['legal_balls_before']==60, 'regularized_std'].values[0]:.2f}")
    print(f"  Ball 114: mu_W = {w_stats.loc[w_stats['legal_balls_before']==114, 'mean'].values[0]:.2f}, reg_sigma = {w_stats.loc[w_stats['legal_balls_before']==114, 'regularized_std'].values[0]:.2f}")
    
    # -------------------------------------------------------------
    # 3. Player-Independent Outcome Transition Probabilities
    # -------------------------------------------------------------
    print("\n--- 3. Deriving Player-Independent Empirical Outcome Transitions ---")
    def classify_outcome_exact(row):
        ex = str(row['extras_type']).lower()
        if 'wide' in ex:
            return 'wide'
        if 'overstep' in ex or 'no ball' in ex or 'noball' in ex:
            return 'no_ball'
        if row['is_wicket'] == 1:
            return 'wicket'
        r = row['runs']
        if r == 0:
            return 'dot'
        elif r == 1:
            return 'one'
        elif r == 2:
            return 'two'
        elif r == 3:
            return 'three'
        elif r == 4 or row['is_four'] == 1:
            return 'four'
        elif r == 6 or row['is_six'] == 1:
            return 'six'
        else:
            return 'one'

    df['outcome_cat'] = df.apply(classify_outcome_exact, axis=1)
    categories = ['dot', 'one', 'two', 'three', 'four', 'six', 'wicket', 'wide', 'no_ball']

    empirical_transitions = {}
    for inn in [1, 2]:
        for ph in ['PP', 'Middle', 'Death']:
            sub = df[(df['innings'] == inn) & (df['phase'] == ph)]
            total = len(sub)
            counts = sub['outcome_cat'].value_counts()
            probs = [float(counts.get(c, 0) / total) for c in categories]
            p_arr = np.array(probs)
            p_arr = p_arr / p_arr.sum()
            key = f"{ph}_inn{inn}"
            empirical_transitions[key] = [round(float(x), 6) for x in p_arr]
            # Exact sum invariant
            diff = 1.0 - sum(empirical_transitions[key])
            empirical_transitions[key][0] += diff
            
            total_p = round(float(sum(empirical_transitions[key])), 6)
            print(f"Stratum {key:12s}: N={total:5d}, sum = {total_p:.6f}")
            assert abs(total_p - 1.0) < 1e-6, f"Probabilities do not sum to 1 in {key}"
            
    transitions_json = os.path.join(OUTPUT_DIR, "outcome_transition_probabilities.json")
    with open(transitions_json, 'w', encoding='utf-8') as f:
        json.dump(empirical_transitions, f, indent=2)
    print(f"Saved outcome transition probabilities to {transitions_json}")
    
    return venue_par_dict, w_stats, empirical_transitions

if __name__ == '__main__':
    generate_empirical_tables()
