import sys
sys.path.append('.')
import numpy as np
import pandas as pd
from scratch.calculate_actual_L import calc_L_inn1, calc_L_inn2

def sigmoid(z, k=1.0):
    return 100.0 / (1.0 + np.exp(-k * np.clip(z, -20, 20)))

# Load empirical wicket curves
dms = pd.read_csv('data/processed/delivery_match_state.csv')
tail_mask = (dms['innings'] == 2) & (dms['runs_required'] <= 0)
dms_clean = dms[~tail_mask].copy()
dls_matches = [20182, 23674, 24822, 28334]
shortened_matches = [15795, 31278, 48514]
exclude_matches = set(dls_matches + shortened_matches)
cohort = dms_clean[~dms_clean['match_id'].isin(exclude_matches)].copy()

w_stats = cohort.groupby('legal_balls_before')['wickets_before'].agg(['mean', 'std']).reset_index()
mu_w_dict = dict(zip(w_stats['legal_balls_before'], w_stats['mean']))
sigma_w_dict = dict(zip(w_stats['legal_balls_before'], w_stats['std']))

def get_w_stats(L_t):
    return mu_w_dict.get(L_t, 3.5), max(0.50, sigma_w_dict.get(L_t, 1.5))

scenarios = [
    (1, 'First over 0.1', 1, 0, 0, 0, 120, None, None, 165.0, 'PP', 'B1'),
    (2, 'Established batter crisis', 2, 110, 90, 5, 30, 65, 13.0, None, 'Death', 'B2'),
    (3, 'New batter in collapse', 1, 15, 16, 3, 104, None, None, 170.0, 'PP', 'B1'),
    (4, 'High-scoring 1st inn death', 1, 175, 96, 2, 24, None, None, 180.0, 'Death', 'B1'),
    (5, 'Difficult chase 12 ov left', 2, 60, 48, 4, 72, 130, 10.83, None, 'Middle', 'B2'),
    (6, '12 off 6 balls', 2, 168, 114, 5, 6, 12, 12.0, None, 'Death', 'B2'),
    (7, '2 off 30 balls', 2, 150, 90, 2, 30, 2, 0.40, None, 'Death', 'B2'),
    (8, 'Impossible chase 80 off 12', 2, 105, 108, 8, 12, 80, 40.0, None, 'Death', 'B2'),
    (9, 'Defending small target 125', 2, 45, 42, 3, 78, 81, 6.23, None, 'Middle', 'BO2'),
    (10, 'Bowler 1st over at ov 17', 2, 90, 96, 3, 24, 35, 8.75, None, 'Death', 'BO2')
]

ecdf_L_base = {
    1: 50.0, 2: 89.8, 3: 72.5, 4: 55.2, 5: 68.2,
    6: 99.9, 7: 3.6, 8: 0.8, 9: 73.8, 10: 91.8
}

def evaluate_framework(params):
    scores = {}
    for sc in scenarios:
        sid, name, inn, S_t, L_t, W_t, B_rem, R_t, RRR, Par, phase, mtype = sc
        L_norm = ecdf_L_base[sid]
        
        if mtype == 'B1':
            R_par = Par / 20.0
            RAR = max(0.0, (Par - S_t) / (B_rem / 6.0))
            rate_stress = (RAR - R_par) / R_par
            if L_t == 0:
                w_stress = 0.0
            else:
                mu_w, sig_w = get_w_stats(L_t)
                w_stress = (W_t - mu_w) / sig_w
            Z = params['b1_w_rate'] * rate_stress + params['b1_w_wkt'] * w_stress
            T = sigmoid(Z, k=params['b1_k'])
            
        elif mtype == 'B2':
            z_rrr = (RRR - params['b2_r_bench']) / params['b2_s_rrr']
            z_w = (W_t - 3.50) / 2.00
            z_inter = (RRR * W_t - 28.0) / 25.0
            Z = params['b2_w_rrr'] * z_rrr + params['b2_w_wkt'] * z_w + params['b2_w_int'] * z_inter
            T = sigmoid(Z, k=params['b2_k'])
            
        elif mtype == 'BO2':
            rrr_stress = (params['bo2_r_bench'] - RRR) / params['bo2_s_rrr']
            mu_w, sig_w = get_w_stats(L_t)
            w_stress = (mu_w - W_t) / sig_w
            Z = params['bo2_w_rrr'] * rrr_stress + params['bo2_w_wkt'] * w_stress
            T = sigmoid(Z, k=params['bo2_k'])
            
        P = 100.0 * ((T / 100.0) ** params['comb_alpha']) * ((L_norm / 100.0) ** params['comb_beta'])
        scores[sid] = (T, P)
    return scores

base_params = {
    'b1_w_rate': 0.60, 'b1_w_wkt': 0.40, 'b1_k': 1.2,
    'b2_w_rrr': 0.55, 'b2_w_wkt': 0.25, 'b2_w_int': 0.20, 'b2_k': 1.0, 'b2_r_bench': 8.10, 'b2_s_rrr': 3.0,
    'bo2_w_rrr': 0.60, 'bo2_w_wkt': 0.40, 'bo2_k': 1.0, 'bo2_r_bench': 8.10, 'bo2_s_rrr': 3.0,
    'comb_alpha': 0.50, 'comb_beta': 0.50
}

base_results = evaluate_framework(base_params)

print("=== BASELINE RESULTS ===")
for sid in range(1, 11):
    t, p = base_results[sid]
    print(f"Scenario {sid:2d}: T={t:5.2f}, L={ecdf_L_base[sid]:5.1f}, P={p:5.2f}")

# TEST 1: Combination Exponents: Asymmetric (alpha=0.40, beta=0.60 vs alpha=0.60, beta=0.40)
print("\n--- SENSITIVITY TEST 1: COMBINATION EXPONENTS ---")
p_asym1 = base_params.copy()
p_asym1['comb_alpha'] = 0.40
p_asym1['comb_beta'] = 0.60
res_asym1 = evaluate_framework(p_asym1)

p_asym2 = base_params.copy()
p_asym2['comb_alpha'] = 0.60
p_asym2['comb_beta'] = 0.40
res_asym2 = evaluate_framework(p_asym2)

diffs_asym1 = [res_asym1[s][1] - base_results[s][1] for s in range(1, 11)]
diffs_asym2 = [res_asym2[s][1] - base_results[s][1] for s in range(1, 11)]
print(f"Alpha=0.40, Beta=0.60: Max diff = {np.max(np.abs(diffs_asym1)):.2f}, Mean abs diff = {np.mean(np.abs(diffs_asym1)):.2f}")
print(f"Alpha=0.60, Beta=0.40: Max diff = {np.max(np.abs(diffs_asym2)):.2f}, Mean abs diff = {np.mean(np.abs(diffs_asym2)):.2f}")

# TEST 2: Sigmoid Multipliers k: (k +- 20%)
print("\n--- SENSITIVITY TEST 2: SIGMOID MULTIPLIERS (k +/- 20%) ---")
p_k_high = base_params.copy()
p_k_high['b1_k'] = 1.44
p_k_high['b2_k'] = 1.20
p_k_high['bo2_k'] = 1.20
res_k_high = evaluate_framework(p_k_high)

p_k_low = base_params.copy()
p_k_low['b1_k'] = 0.96
p_k_low['b2_k'] = 0.80
p_k_low['bo2_k'] = 0.80
res_k_low = evaluate_framework(p_k_low)

diffs_kh = [res_k_high[s][1] - base_results[s][1] for s in range(1, 11)]
diffs_kl = [res_k_low[s][1] - base_results[s][1] for s in range(1, 11)]
print(f"k +20%: Max diff = {np.max(np.abs(diffs_kh)):.2f}, Mean abs diff = {np.mean(np.abs(diffs_kh)):.2f}")
print(f"k -20%: Max diff = {np.max(np.abs(diffs_kl)):.2f}, Mean abs diff = {np.mean(np.abs(diffs_kl)):.2f}")

# TEST 3: Component Weights: Wicket vs Rate Emphasis (+- 15%)
print("\n--- SENSITIVITY TEST 3: WICKET EMPHASIS (+15% Wicket Weight) ---")
p_wkt_high = base_params.copy()
p_wkt_high['b1_w_rate'] = 0.45
p_wkt_high['b1_w_wkt'] = 0.55
p_wkt_high['b2_w_rrr'] = 0.45
p_wkt_high['b2_w_wkt'] = 0.35
res_wkt_high = evaluate_framework(p_wkt_high)
diffs_wkt = [res_wkt_high[s][1] - base_results[s][1] for s in range(1, 11)]
print(f"High Wicket Weight: Max diff = {np.max(np.abs(diffs_wkt)):.2f}, Mean abs diff = {np.mean(np.abs(diffs_wkt)):.2f}")

# TEST 4: RRR Reference Benchmark (8.1 vs 8.5 vs 7.8)
print("\n--- SENSITIVITY TEST 4: RRR BENCHMARK (8.5 vs 8.1) ---")
p_r_high = base_params.copy()
p_r_high['b2_r_bench'] = 8.50
p_r_high['bo2_r_bench'] = 8.50
res_r_high = evaluate_framework(p_r_high)
diffs_r = [res_r_high[s][1] - base_results[s][1] for s in range(1, 11)]
print(f"RRR Bench = 8.50: Max diff = {np.max(np.abs(diffs_r)):.2f}, Mean abs diff = {np.mean(np.abs(diffs_r)):.2f}")

# Check ranking order stability across all alternatives:
base_ranks = np.argsort([-base_results[s][1] for s in range(1, 11)])
print("\n--- SCENARIO RANKING ORDER STABILITY ---")
print("Base Order:     ", [s+1 for s in base_ranks])
for name, res in [('Alpha=0.4, Beta=0.6', res_asym1), ('Alpha=0.6, Beta=0.4', res_asym2), ('k +20%', res_k_high), ('k -20%', res_k_low), ('Wicket High', res_wkt_high), ('RRR Bench 8.5', res_r_high)]:
    r_ranks = np.argsort([-res[s][1] for s in range(1, 11)])
    is_identical = list(base_ranks) == list(r_ranks)
    print(f"{name:20s}: {[s+1 for s in r_ranks]} (Identical to Base: {is_identical})")
