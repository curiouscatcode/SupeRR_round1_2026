import json
import math
import numpy as np
import pandas as pd

# Load empirical tables
with open('outputs/step_4_pressure_pipeline/empirical_venue_par.json', 'r') as f:
    venue_par_dict = json.load(f)

wkt_df = pd.read_csv('outputs/step_4_pressure_pipeline/empirical_wicket_curve.csv')
mu_w_dict = dict(zip(wkt_df['legal_balls_before'], wkt_df['mean']))
sig_w_dict = dict(zip(wkt_df['legal_balls_before'], wkt_df['regularized_std']))

with open('outputs/step_4_pressure_pipeline/outcome_transition_probabilities.json', 'r') as f:
    trans_dict = json.load(f)

with open('outputs/step_4_pressure_pipeline/wp_model_inn1.json', 'r') as f:
    m1_dict = json.load(f)
m1_means = np.array(m1_dict['means'])
m1_stds = np.array(m1_dict['stds'])
m1_betas = np.array(m1_dict['coefficients'])

with open('outputs/step_4_pressure_pipeline/wp_model_inn2.json', 'r') as f:
    m2_dict = json.load(f)
m2_means = np.array(m2_dict['means'])
m2_stds = np.array(m2_dict['stds'])
m2_betas = np.array(m2_dict['coefficients'])

# Load clean parquet for true ECDF rank
cohort_df = pd.read_parquet('outputs/step_4_pressure_pipeline/deliveries_with_consequence.parquet')
l1_sorted = np.sort(cohort_df[cohort_df['innings'] == 1]['raw_consequence_L'].values)
l2_sorted = np.sort(cohort_df[cohort_df['innings'] == 2]['raw_consequence_L'].values)
n1 = len(l1_sorted)
n2 = len(l2_sorted)

def sigmoid(z, k):
    return 100.0 / (1.0 + math.exp(-k * max(-20.0, min(20.0, z))))

def calc_wp1_independent(score, legal_balls, wk_lost, par):
    wk_rem = 10.0 - wk_lost
    b_bowled = legal_balls / 120.0
    par_to_date = par * b_bowled
    score_diff_par = (score - par_to_date) / 30.0
    crr = (score / max(1.0, legal_balls)) * 6.0
    crr_rel_par = crr / (par / 20.0)
    balls_rem = (120.0 - legal_balls) / 120.0
    res_interaction = wk_rem * balls_rem
    
    raw = np.array([score_diff_par, wk_rem, b_bowled, res_interaction, crr_rel_par])
    norm = (raw - m1_means) / m1_stds
    z = m1_betas[0] + np.dot(norm, m1_betas[1:])
    return 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, z))))

def calc_markov_wp_independent(runs_req, wk_lost, trans_probs):
    # Terminal recurrence for B_rem = 1
    if runs_req <= 0:
        return 1.0
    if wk_lost >= 10:
        return 0.0
        
    p_dot, p_1, p_2, p_3, p_4, p_6, p_wkt, p_wide, p_nb = trans_probs
    
    legal_outcomes = [
        (p_dot, 0, 0),
        (p_1, 1, 0),
        (p_2, 2, 0),
        (p_3, 3, 0),
        (p_4, 4, 0),
        (p_6, 6, 0),
        (p_wkt, 0, 1)
    ]
    exp_wp_legal = 0.0
    for p_o, r_add, w_add in legal_outcomes:
        new_req = runs_req - r_add
        new_wkts = wk_lost + w_add
        if new_wkts >= 10:
            term = 0.0
        elif new_req <= 0:
            term = 1.0
        elif new_req == 1:
            term = 0.50
        else:
            term = 0.0
        exp_wp_legal += p_o * term
        
    p_extras = p_wide + p_nb
    if runs_req <= 1:
        wp_extra = 0.50
    elif runs_req == 2:
        wp_extra = p_1 + p_2 + p_3 + p_4 + p_6 + 0.5 * p_dot
    elif runs_req == 3:
        wp_extra = 0.5 * p_2 + p_3 + p_4 + p_6
    elif runs_req == 4:
        wp_extra = 0.5 * p_3 + p_4 + p_6
    else:
        wp_extra = 0.0
    wp_final = exp_wp_legal + p_extras * (1.0 if runs_req <= 1 else 0.5 if runs_req == 2 else 0.0)
    return float(np.clip(wp_final, 0.0, 1.0))

def calc_wp2_independent(runs_req, balls_rem, wk_lost, phase, trans_probs):
    if wk_lost >= 10:
        return 0.0
    if runs_req <= 0:
        return 1.0
    if balls_rem <= 0:
        return 0.50 if runs_req == 1 else 0.0
        
    if balls_rem == 1:
        return calc_markov_wp_independent(runs_req, wk_lost, trans_probs)
        
    wk_rem = 10.0 - wk_lost
    rrr = max(0.0, min(36.0, (runs_req / max(1.0, balls_rem)) * 6.0))
    b_norm = balls_rem / 120.0
    rrr_x_wk = rrr * (10.0 - wk_rem)
    
    raw = np.array([rrr, wk_rem, b_norm, rrr_x_wk])
    norm = (raw - m2_means) / m2_stds
    z = m2_betas[0] + np.dot(norm, m2_betas[1:])
    return 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, z))))

outcomes_list = [
    (0, 0, 1), # Dot
    (1, 0, 1), # 1
    (2, 0, 1), # 2
    (3, 0, 1), # 3
    (4, 0, 1), # 4
    (6, 0, 1), # 6
    (0, 1, 1), # Wicket
    (1, 0, 0), # Wide
    (1, 0, 0)  # No-ball
]

def calc_raw_L_independent(row, venue_par):
    inn = row['innings']
    phase = row['phase']
    key = f"{phase}_inn{inn}"
    probs = trans_dict[key]
    
    if inn == 1:
        sc = row['score_before']
        lb = row['legal_balls_before']
        wt = row['W_t']
        wp_curr = calc_wp1_independent(sc, lb, wt, venue_par)
        exp_swing = 0.0
        for p_o, (r_add, w_add, b_add) in zip(probs, outcomes_list):
            wp_next = calc_wp1_independent(sc + r_add, lb + b_add, wt + w_add, venue_par)
            exp_swing += p_o * abs(wp_next - wp_curr)
        return wp_curr, exp_swing
    else:
        req = row['runs_required']
        brem = row['balls_remaining']
        wt = row['W_t']
        wp_curr = calc_wp2_independent(req, brem, wt, phase, probs)
        exp_swing = 0.0
        for p_o, (r_add, w_add, b_add) in zip(probs, outcomes_list):
            next_brem = brem - b_add
            next_req = req - r_add
            next_wt = wt + w_add
            # next phase
            next_ov = (120 - next_brem) // 6 + 1
            next_ph = 'PP' if next_ov <= 6 else ('Middle' if next_ov <= 15 else 'Death')
            next_probs = trans_dict[f"{next_ph}_inn2"]
            wp_next = calc_wp2_independent(next_req, next_brem, next_wt, next_ph, next_probs)
            exp_swing += p_o * abs(wp_next - wp_curr)
        return wp_curr, exp_swing

def calc_ecdf_norm_independent(raw_L, inn):
    arr = l1_sorted if inn == 1 else l2_sorted
    n = n1 if inn == 1 else n2
    r_left = np.searchsorted(arr, raw_L, side='left')
    r_right = np.searchsorted(arr, raw_L, side='right')
    return ((r_left + r_right) / (2.0 * n)) * 100.0

def calc_task_difficulty_independent(row, venue_par):
    inn = row['innings']
    wt = row['W_t']
    lb = row['legal_balls_before']
    brem = row['balls_remaining']
    mu_w = mu_w_dict.get(lb, 3.5)
    sigma_adj = sig_w_dict.get(lb, 1.5)
    
    if inn == 1:
        # T_B1
        r_par = venue_par / 20.0
        rar = max(0.0, (venue_par - row['score_before']) / (max(1, brem) / 6.0))
        w_stress = 0.0 if lb == 0 else (wt - mu_w) / sigma_adj
        z_b1 = 0.60 * ((rar - r_par) / r_par) + 0.40 * w_stress
        t_bat = sigmoid(z_b1, 1.2)
        
        # T_BO1
        crr = r_par if lb == 0 else (row['score_before'] / lb) * 6.0
        fielding = 0.50 if row['phase'] in ['PP', 'Death'] else 0.0
        w_stress_bowl = 0.0 if lb == 0 else (mu_w - wt) / sigma_adj
        z_bo1 = 0.50 * ((crr - r_par) / r_par) + 0.35 * w_stress_bowl + 0.15 * fielding
        t_bowl = sigmoid(z_bo1, 1.1)
        return t_bat, t_bowl
    else:
        # T_B2
        rrr = max(0.0, min(36.0, (row['runs_required'] / max(1, brem)) * 6.0))
        z_b2 = 0.55 * ((rrr - 8.10) / 3.00) + 0.25 * ((wt - 3.50) / 2.00) + 0.20 * ((rrr * wt - 28.0) / 25.0)
        t_bat = sigmoid(z_b2, 1.0)
        
        # T_BO2
        w_stress_bowl2 = (mu_w - wt) / sigma_adj
        z_bo2 = 0.60 * ((8.10 - rrr) / 3.00) + 0.40 * w_stress_bowl2
        t_bowl = sigmoid(z_bo2, 1.0)
        return t_bat, t_bowl

# Load 10 states
states_df = pd.read_parquet('outputs/step_4_pressure_pipeline/deliveries_with_task_difficulty.parquet')
final_df = pd.read_parquet('outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet')
states_df['pressure_batting'] = final_df['pressure_batting']
states_df['pressure_bowling'] = final_df['pressure_bowling']

# Archetype indices:
chosen_indices = [
    states_df[(states_df['innings'] == 1) & (states_df['legal_balls_before'] == 0) & (states_df['score_before'] == 0)].index[0],
    states_df[(states_df['innings'] == 1) & (states_df['overid'] == 3) & (states_df['wickets_before'] == 1)].index[10],
    states_df[(states_df['innings'] == 1) & (states_df['overid'] == 10) & (states_df['wickets_before'] >= 5)].index[0],
    states_df[(states_df['innings'] == 1) & (states_df['overid'] == 19) & (states_df['score_before'] >= 170)].index[0],
    states_df[(states_df['innings'] == 2) & (states_df['overid'] >= 14) & (states_df['runs_required'] <= 15) & (states_df['wickets_before'] <= 3)].index[0],
    states_df[(states_df['innings'] == 2) & (states_df['overid'] == 16) & (states_df['required_run_rate'] >= 13) & (states_df['wickets_before'] >= 4) & (states_df['wickets_before'] <= 6)].index[0],
    states_df[(states_df['innings'] == 2) & (states_df['overid'] == 19) & (states_df['runs_required'] >= 40)].index[0],
    states_df[(states_df['innings'] == 1) & (states_df['overid'] == 16) & (states_df['score_before'] >= 160) & (states_df['wickets_before'] <= 2)].index[0],
    states_df[(states_df['innings'] == 1) & (states_df['overid'] == 12) & (states_df['score_before'] <= 60) & (states_df['wickets_before'] >= 5)].index[0],
    states_df[(states_df['innings'] == 2) & (states_df['balls_remaining'] == 1) & (states_df['runs_required'] <= 6) & (states_df['runs_required'] > 0)].index[0]
]

labels = [
    '1. Opening ball (Inn 1, 0.1)',
    '2. Powerplay (Inn 1, ov 3, 1 down)',
    '3. Middle collapse (Inn 1, ov 10, 5 down)',
    '4. Death situation (Inn 1, ov 19, 170+)',
    '5. Comfortable chase (Inn 2, ov 15, req<=15)',
    '6. Difficult chase (Inn 2, ov 16, RRR 13+)',
    '7. Impossible chase (Inn 2, ov 19, req 40+)',
    '8. First-inn high-scoring (Inn 1, ov 16, 160/2)',
    '9. First-inn low-scoring (Inn 1, ov 12, 60/5+)',
    '10. Final ball nail-biter (Inn 2, B_rem=1, req<=6)'
]

results = []
print("=== INDEPENDENT NUMERICAL REPRODUCTION FOR 10 STATES ===")
for idx, label in zip(chosen_indices, labels):
    row = states_df.loc[idx]
    v_id = str(row['venue_id'])
    v_par = venue_par_dict.get(v_id, venue_par_dict.get('GLOBAL_DEFAULT', 176.68))
    
    t_bat_calc, t_bowl_calc = calc_task_difficulty_independent(row, v_par)
    wp_curr_calc, raw_L_calc = calc_raw_L_independent(row, v_par)
    l_norm_calc = calc_ecdf_norm_independent(raw_L_calc, row['innings'])
    p_bat_calc = math.sqrt(t_bat_calc * l_norm_calc)
    p_bowl_calc = math.sqrt(t_bowl_calc * l_norm_calc)
    
    # Parquet values
    t_bat_pq = row['task_difficulty_bat']
    t_bowl_pq = row['task_difficulty_bowl']
    raw_L_pq = row['raw_consequence_L']
    l_norm_pq = row['normalized_consequence_L']
    p_bat_pq = row['pressure_batting']
    p_bowl_pq = row['pressure_bowling']
    
    diff_t_bat = abs(t_bat_calc - t_bat_pq)
    diff_t_bowl = abs(t_bowl_calc - t_bowl_pq)
    diff_raw_L = abs(raw_L_calc - raw_L_pq)
    diff_l_norm = abs(l_norm_calc - l_norm_pq)
    diff_p_bat = abs(p_bat_calc - p_bat_pq)
    diff_p_bowl = abs(p_bowl_calc - p_bowl_pq)
    
    max_diff = max(diff_t_bat, diff_t_bowl, diff_raw_L, diff_l_norm, diff_p_bat, diff_p_bowl)
    status = "PASS" if max_diff < 1e-4 else "FAIL"
    
    print(f"\n[{label}] (Match {row['match_id']} | Inn {row['innings']} | Ov {row['overid']}.{row['over_ball_num']})")
    print(f"  T_bat:  Indep={t_bat_calc:6.2f} | Pipeline={t_bat_pq:6.2f} | Diff={diff_t_bat:.2e}")
    print(f"  T_bowl: Indep={t_bowl_calc:6.2f} | Pipeline={t_bowl_pq:6.2f} | Diff={diff_t_bowl:.2e}")
    print(f"  Raw L:  Indep={raw_L_calc:.6f} | Pipeline={raw_L_pq:.6f} | Diff={diff_raw_L:.2e}")
    print(f"  L_norm: Indep={l_norm_calc:6.2f} | Pipeline={l_norm_pq:6.2f} | Diff={diff_l_norm:.2e}")
    print(f"  P_bat:  Indep={p_bat_calc:6.2f} | Pipeline={p_bat_pq:6.2f} | Diff={diff_p_bat:.2e}")
    print(f"  P_bowl: Indep={p_bowl_calc:6.2f} | Pipeline={p_bowl_pq:6.2f} | Diff={diff_p_bowl:.2e}")
    print(f"  Status: {status} (Max Diff = {max_diff:.2e})")
    
    results.append({
        'label': label,
        'match_id': int(row['match_id']),
        'innings': int(row['innings']),
        'over_ball': f"{row['overid']}.{row['over_ball_num']}",
        'score_before': int(row['score_before']),
        'wickets_before': int(row['wickets_before']),
        'balls_remaining': int(row['balls_remaining']),
        'runs_required': float(row['runs_required']) if pd.notna(row['runs_required']) else np.nan,
        't_bat_indep': t_bat_calc, 't_bat_pq': t_bat_pq,
        't_bowl_indep': t_bowl_calc, 't_bowl_pq': t_bowl_pq,
        'raw_L_indep': raw_L_calc, 'raw_L_pq': raw_L_pq,
        'l_norm_indep': l_norm_calc, 'l_norm_pq': l_norm_pq,
        'p_bat_indep': p_bat_calc, 'p_bat_pq': p_bat_pq,
        'p_bowl_indep': p_bowl_calc, 'p_bowl_pq': p_bowl_pq,
        'max_diff': max_diff,
        'status': status
    })

res_df = pd.DataFrame(results)
res_df.to_csv('scratch/independent_reproduction_results.csv', index=False)
print("\n=== SUMMARY OF 10-DELIVERY INDEPENDENT REPRODUCTION ===")
print(f"Total Tested: {len(results)}")
print(f"Total Passed: {sum(r['status'] == 'PASS' for r in results)}")
print(f"Max Absolute Error Across All Variables: {res_df['max_diff'].max():.2e}")
