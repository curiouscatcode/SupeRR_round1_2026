import sys
import os
import importlib.util
import json
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_4_pressure_pipeline"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Clean module loading using SourceFileLoader
spec = importlib.util.spec_from_file_location(
    "wp_models", 
    os.path.join("src", "step_4_pressure_pipeline", "03_win_probability_models.py")
)
wp_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wp_mod)
WinProbabilityFramework = wp_mod.WinProbabilityFramework

OUTCOMES_CONFIG = [
    ('dot',     0, 0, 1),
    ('one',     1, 0, 1),
    ('two',     2, 0, 1),
    ('three',   3, 0, 1),
    ('four',    4, 0, 1),
    ('six',     6, 0, 1),
    ('wicket',  0, 1, 1),
    ('wide',    1, 0, 0),
    ('no_ball', 1, 0, 0)
]

def compute_consequence_and_ecdf():
    cohort_path = os.path.join(OUTPUT_DIR, "clean_cohort_deliveries.parquet")
    print(f"Loading clean cohort from {cohort_path}...")
    df = pd.read_parquet(cohort_path)
    
    wp_framework = WinProbabilityFramework(load_saved=True)
    
    # -------------------------------------------------------------
    # 1. Vectorized Pre-Delivery Win Probability
    # -------------------------------------------------------------
    print("Computing pre-delivery Win Probability WP(S_t)...")
    
    inn2_mask = (df['innings'] == 2).values
    final_ball_mask = inn2_mask & (df['balls_remaining'] == 1).values
    penult_ball_mask = inn2_mask & (df['balls_remaining'] > 1).values
    
    wp_arr = np.zeros(len(df), dtype=float)
    
    # Innings 2 penultimate balls (logistic)
    req2 = df.loc[penult_ball_mask, 'runs_required'].values
    brem2 = df.loc[penult_ball_mask, 'balls_remaining'].values
    wt2 = df.loc[penult_ball_mask, 'W_t'].values
    wk_rem2 = 10.0 - wt2
    rrr2 = np.clip((req2 / np.maximum(1.0, brem2)) * 6.0, 0.0, 36.0)
    bnorm2 = brem2 / 120.0
    rrr_x_wk2 = rrr2 * (10.0 - wk_rem2)
    
    X2 = np.column_stack([np.ones(len(req2)), rrr2, wk_rem2, bnorm2, rrr_x_wk2])
    X2_norm = (X2[:, 1:] - wp_framework.m2) / wp_framework.s2
    z2 = np.column_stack([np.ones(len(req2)), X2_norm]) @ wp_framework.beta2
    wp_arr[penult_ball_mask] = 1.0 / (1.0 + np.exp(-np.clip(z2, -20, 20)))
    
    # Innings 2 final balls (Markov engine)
    for idx in df[final_ball_mask].index:
        row = df.loc[idx]
        wp_arr[idx] = wp_framework.predict_wp_final_markov(row['runs_required'], row['W_t'], row['phase'])
        
    # Innings 1 Logistic
    inn1_mask = (df['innings'] == 1).values
    score1 = df.loc[inn1_mask, 'score_before'].values
    lballs1 = df.loc[inn1_mask, 'legal_balls_before'].values
    wt1 = df.loc[inn1_mask, 'W_t'].values
    wk_rem1 = 10.0 - wt1
    vpar1 = df.loc[inn1_mask, 'venue_id'].astype(str).map(wp_framework.venue_par_dict).fillna(176.68).values
    
    bbowled1 = lballs1 / 120.0
    par_to_date1 = vpar1 * bbowled1
    score_diff_par1 = (score1 - par_to_date1) / 30.0
    
    # Bayesian CRR shrinkage with M=18 approved engineering convention
    M_shrinkage = 18.0
    rpar1 = vpar1 / 20.0
    crr_shrunk1 = (score1 + M_shrinkage * (rpar1 / 6.0)) / (lballs1 + M_shrinkage) * 6.0
    crr_rel_par1 = crr_shrunk1 / rpar1
    
    balls_rem1 = (120.0 - lballs1) / 120.0
    res_inter1 = wk_rem1 * balls_rem1
    
    X1 = np.column_stack([np.ones(len(score1)), score_diff_par1, wk_rem1, bbowled1, res_inter1, crr_rel_par1])
    X1_norm = (X1[:, 1:] - wp_framework.m1) / wp_framework.s1
    z1 = np.column_stack([np.ones(len(score1)), X1_norm]) @ wp_framework.beta1
    wp_arr[inn1_mask] = 1.0 / (1.0 + np.exp(-np.clip(z1, -20, 20)))
    
    df['pre_delivery_wp'] = wp_arr
    print("Pre-delivery WP computed. Mean Inn 1 WP = {:.4f}, Mean Inn 2 WP = {:.4f}".format(
        df.loc[inn1_mask, 'pre_delivery_wp'].mean(),
        df.loc[inn2_mask, 'pre_delivery_wp'].mean()
    ))
    
    # -------------------------------------------------------------
    # 2. Vectorized Expected Match Consequence L(S_t)
    # -------------------------------------------------------------
    print("\nComputing expected absolute Match Consequence L(S_t)...")
    raw_L = np.zeros(len(df), dtype=float)
    
    strata_keys = df['phase'] + "_inn" + df['innings'].astype(str)
    
    for stratum, p_list in wp_framework.transitions.items():
        st_mask = (strata_keys == stratum).values
        if not np.any(st_mask):
            continue
            
        st_indices = np.where(st_mask)[0]
        st_df = df.iloc[st_indices]
        curr_wp = st_df['pre_delivery_wp'].values
        inn = st_df['innings'].iloc[0]
        
        cum_swing = np.zeros(len(st_indices), dtype=float)
        
        for p_o, (_, r_add, w_add, b_add) in zip(p_list, OUTCOMES_CONFIG):
            if inn == 2:
                req_next = st_df['runs_required'].values - r_add
                brem_next = st_df['balls_remaining'].values - b_add
                wt_next = st_df['W_t'].values + w_add
                
                wp_next = np.zeros(len(st_indices), dtype=float)
                
                term_win = (req_next <= 0)
                term_loss = (wt_next >= 10) | ((brem_next <= 0) & (req_next > 1))
                term_tie = ((brem_next <= 0) & (req_next == 1))
                
                wp_next[term_win] = 1.0
                wp_next[term_loss] = 0.0
                wp_next[term_tie] = 0.50
                
                active_mask = ~term_win & ~term_loss & ~term_tie
                
                active_final = active_mask & (brem_next == 1)
                for rel_idx in np.where(active_final)[0]:
                    wp_next[rel_idx] = wp_framework.predict_wp_final_markov(req_next[rel_idx], wt_next[rel_idx], st_df['phase'].iloc[rel_idx])
                    
                active_norm = active_mask & (brem_next > 1)
                if np.any(active_norm):
                    r_act = req_next[active_norm]
                    b_act = brem_next[active_norm]
                    w_act = wt_next[active_norm]
                    wk_rem_act = 10.0 - w_act
                    rrr_act = np.clip((r_act / b_act) * 6.0, 0.0, 36.0)
                    bnorm_act = b_act / 120.0
                    rrr_x_wk_act = rrr_act * (10.0 - wk_rem_act)
                    
                    X2_act = np.column_stack([np.ones(len(r_act)), rrr_act, wk_rem_act, bnorm_act, rrr_x_wk_act])
                    X2_act_norm = (X2_act[:, 1:] - wp_framework.m2) / wp_framework.s2
                    z2_act = np.column_stack([np.ones(len(r_act)), X2_act_norm]) @ wp_framework.beta2
                    wp_next[active_norm] = 1.0 / (1.0 + np.exp(-np.clip(z2_act, -20, 20)))
                    
            else: # Innings 1
                score_next = st_df['score_before'].values + r_add
                lballs_next = st_df['legal_balls_before'].values + b_add
                wt_next = st_df['W_t'].values + w_add
                vpar = st_df['venue_id'].astype(str).map(wp_framework.venue_par_dict).fillna(176.68).values
                
                wk_rem_next = 10.0 - wt_next
                bbowled_next = lballs_next / 120.0
                par_to_date_next = vpar * bbowled_next
                score_diff_par_next = (score_next - par_to_date_next) / 30.0
                
                # Bayesian CRR shrinkage with M=18 approved engineering convention
                rpar_next = vpar / 20.0
                crr_shrunk_next = (score_next + 18.0 * (rpar_next / 6.0)) / (lballs_next + 18.0) * 6.0
                crr_rel_par_next = crr_shrunk_next / rpar_next
                
                balls_rem_next = (120.0 - lballs_next) / 120.0
                res_inter_next = wk_rem_next * balls_rem_next
                
                X1_next = np.column_stack([np.ones(len(score_next)), score_diff_par_next, wk_rem_next, bbowled_next, res_inter_next, crr_rel_par_next])
                X1_next_norm = (X1_next[:, 1:] - wp_framework.m1) / wp_framework.s1
                z1_next = np.column_stack([np.ones(len(score_next)), X1_next_norm]) @ wp_framework.beta1
                wp_next = 1.0 / (1.0 + np.exp(-np.clip(z1_next, -20, 20)))
                
            cum_swing += p_o * np.abs(wp_next - curr_wp)
            
        raw_L[st_indices] = cum_swing
        
    df['raw_consequence_L'] = raw_L
    print(f"Computed raw consequence. Mean L1: {df.loc[inn1_mask, 'raw_consequence_L'].mean():.5f}, Mean L2: {df.loc[inn2_mask, 'raw_consequence_L'].mean():.5f}")

    # -------------------------------------------------------------
    # 3. Innings-Specific ECDF Normalization
    # -------------------------------------------------------------
    print("\n--- Computing Innings-Specific ECDF Normalization ---")
    l_norm_arr = np.zeros(len(df), dtype=float)
    
    # Innings 1 ECDF
    l1_vals = df.loc[inn1_mask, 'raw_consequence_L'].values
    l1_sorted = np.sort(l1_vals)
    n1 = len(l1_sorted)
    r_left1 = np.searchsorted(l1_sorted, l1_vals, side='left')
    r_right1 = np.searchsorted(l1_sorted, l1_vals, side='right')
    l_norm_arr[inn1_mask] = ((r_left1 + r_right1) / (2.0 * n1)) * 100.0
    
    # Innings 2 ECDF
    l2_vals = df.loc[inn2_mask, 'raw_consequence_L'].values
    l2_sorted = np.sort(l2_vals)
    n2 = len(l2_sorted)
    r_left2 = np.searchsorted(l2_sorted, l2_vals, side='left')
    r_right2 = np.searchsorted(l2_sorted, l2_vals, side='right')
    l_norm_arr[inn2_mask] = ((r_left2 + r_right2) / (2.0 * n2)) * 100.0
    
    df['normalized_consequence_L'] = l_norm_arr
    print("ECDF normalization complete.")
    print("  Innings 1 L_norm: min={:.2f}, median={:.2f}, max={:.2f}".format(
        df.loc[inn1_mask, 'normalized_consequence_L'].min(),
        df.loc[inn1_mask, 'normalized_consequence_L'].median(),
        df.loc[inn1_mask, 'normalized_consequence_L'].max()
    ))
    print("  Innings 2 L_norm: min={:.2f}, median={:.2f}, max={:.2f}".format(
        df.loc[inn2_mask, 'normalized_consequence_L'].min(),
        df.loc[inn2_mask, 'normalized_consequence_L'].median(),
        df.loc[inn2_mask, 'normalized_consequence_L'].max()
    ))

    # Freeze empirical ECDF percentiles for testing and player evaluation
    ecdf_summary = {
        'inn1_percentiles': {int(p): float(np.percentile(l1_sorted, p)) for p in range(0, 101, 5)},
        'inn2_percentiles': {int(p): float(np.percentile(l2_sorted, p)) for p in range(0, 101, 5)}
    }
    with open(os.path.join(OUTPUT_DIR, "frozen_ecdf_distributions.json"), 'w', encoding='utf-8') as f:
        json.dump(ecdf_summary, f, indent=2)

    out_parquet = os.path.join(OUTPUT_DIR, "deliveries_with_consequence.parquet")
    df.to_parquet(out_parquet, index=False)
    print(f"Saved deliveries with consequence to {out_parquet}")
    return df

if __name__ == '__main__':
    compute_consequence_and_ecdf()
