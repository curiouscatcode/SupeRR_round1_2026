import pandas as pd
import numpy as np

# Load clean cohort
df = pd.read_parquet('outputs/step_4_pressure_pipeline/clean_cohort_deliveries.parquet')
inn1 = df[df['innings'] == 1].copy()

# Load venue par
import json
with open('outputs/step_4_pressure_pipeline/empirical_venue_par.json') as f:
    vpar_dict = json.load(f)
global_par = vpar_dict.get('GLOBAL_DEFAULT', 176.68)
inn1['venue_par'] = inn1['venue_id'].astype(str).map(vpar_dict).fillna(global_par)
inn1['r_par'] = inn1['venue_par'] / 20.0

# Base features
inn1['wk_rem'] = 10.0 - inn1['W_t']
inn1['b_bowled'] = inn1['legal_balls_before'] / 120.0
inn1['par_to_date'] = inn1['venue_par'] * inn1['b_bowled']
inn1['score_diff_par'] = (inn1['score_before'] - inn1['par_to_date']) / 30.0
inn1['balls_rem'] = (120.0 - inn1['legal_balls_before']) / 120.0
inn1['res_interaction'] = inn1['wk_rem'] * inn1['balls_rem']
y1 = inn1['bat_win'].values

# Compare 3 model specifications for Innings 1 WP:
# Spec A: Current Step 4 (Raw CRR / R_par)
# Spec B: Shrunk CRR (M = 18 balls)
# Spec C: Parsimonious Model without CRR (Score Diff Par, Wk Rem, Balls Bowled, Res Interaction)

def fit_logistic(X, y):
    m = X[:, 1:].mean(axis=0)
    s = X[:, 1:].std(axis=0)
    s[s < 1e-6] = 1.0
    X_norm = X.copy()
    X_norm[:, 1:] = (X[:, 1:] - m) / s
    beta = np.zeros(X.shape[1])
    for _ in range(25):
        p = 1.0 / (1.0 + np.exp(-np.clip(X_norm @ beta, -20, 20)))
        grad = X_norm.T @ (p - y)
        W = p * (1.0 - p)
        H = (X_norm.T * W) @ X_norm + 1e-4 * np.eye(X.shape[1])
        step = np.linalg.solve(H, grad)
        beta -= step
        if np.max(np.abs(step)) < 1e-6:
            break
    # compute log-likelihood and AUC
    preds = 1.0 / (1.0 + np.exp(-np.clip(X_norm @ beta, -20, 20)))
    brier = np.mean((preds - y)**2)
    return beta, m, s, preds, brier

# Spec A:
crr_raw = np.where(inn1['legal_balls_before'] == 0, inn1['r_par'], (inn1['score_before'] / np.maximum(1.0, inn1['legal_balls_before'])) * 6.0)
crr_rel_raw = crr_raw / inn1['r_par']
XA = np.column_stack([np.ones(len(inn1)), inn1['score_diff_par'], inn1['wk_rem'], inn1['b_bowled'], inn1['res_interaction'], crr_rel_raw])
betaA, mA, sA, predsA, brierA = fit_logistic(XA, y1)

# Spec B (M=18):
M = 18
crr_shrunk = (inn1['score_before'] + M * (inn1['r_par'] / 6.0)) / (inn1['legal_balls_before'] + M) * 6.0
crr_rel_shrunk = crr_shrunk / inn1['r_par']
XB = np.column_stack([np.ones(len(inn1)), inn1['score_diff_par'], inn1['wk_rem'], inn1['b_bowled'], inn1['res_interaction'], crr_rel_shrunk])
betaB, mB, sB, predsB, brierB = fit_logistic(XB, y1)

# Spec C (No CRR, 4 features):
XC = np.column_stack([np.ones(len(inn1)), inn1['score_diff_par'], inn1['wk_rem'], inn1['b_bowled'], inn1['res_interaction']])
betaC, mC, sC, predsC, brierC = fit_logistic(XC, y1)

print("=== INNINGS 1 WIN PROBABILITY MODEL COMPARISON ===")
print(f"Spec A (Current Step 4 with raw CRR):       Brier Score = {brierA:.5f}")
print(f"Spec B (Bayesian Shrunk CRR M=18):         Brier Score = {brierB:.5f}")
print(f"Spec C (Parsimonious without redundant CRR): Brier Score = {brierC:.5f}")

# Now let's test what expected consequence L is across the 20 overs under Spec A, Spec B, Spec C!
# Load outcome probabilities for Innings 1
with open('outputs/step_4_pressure_pipeline/outcome_transition_probabilities.json') as f:
    t_dict = json.load(f)

outcomes = [
    (0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1), (4, 0, 1), (6, 0, 1), (0, 1, 1), (1, 0, 0), (1, 0, 0)
]

def eval_spec_L(beta, m, s, is_spec_c=False, M_val=0):
    def get_wp(score, lb, wt, par):
        wk_rem = 10.0 - wt
        bb = lb / 120.0
        r_p = par / 20.0
        sd = (score - par * bb) / 30.0
        br = (120.0 - lb) / 120.0
        ri = wk_rem * br
        if is_spec_c:
            raw = np.array([sd, wk_rem, bb, ri])
        else:
            if M_val == 0:
                c = r_p if lb == 0 else (score / max(1.0, lb)) * 6.0
            else:
                c = (score + M_val * (r_p / 6.0)) / (lb + M_val) * 6.0
            cr = c / r_p
            raw = np.array([sd, wk_rem, bb, ri, cr])
        norm = (raw - m) / s
        z = beta[0] + norm @ beta[1:]
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

    # Evaluate on a representative match state across overs 1 to 20
    # Par = 170. At over ov, score = ov * 8.5, wickets = empirical average
    l_list = []
    wkt_curve = pd.read_csv('outputs/step_4_pressure_pipeline/empirical_wicket_curve.csv')
    wkt_map = dict(zip(wkt_curve['legal_balls_before'], wkt_curve['mean']))
    
    for ov in range(0, 20):
        lb = ov * 6
        sc = int(ov * 8.5)
        wt = int(round(wkt_map.get(lb, ov * 0.3)))
        ph = 'PP' if ov < 6 else ('Middle' if ov < 15 else 'Death')
        probs = t_dict[f"{ph}_inn1"]
        wp0 = get_wp(sc, lb, wt, 170.0)
        exp_sw = 0.0
        for p_o, (r_add, w_add, b_add) in zip(probs, outcomes):
            wp1 = get_wp(sc + r_add, lb + b_add, wt + w_add, 170.0)
            exp_sw += p_o * abs(wp1 - wp0)
        l_list.append((ov + 1, ph, wp0, exp_sw))
    return pd.DataFrame(l_list, columns=['Over', 'Phase', 'WP', 'Raw_L'])

dfA = eval_spec_L(betaA, mA, sA, is_spec_c=False, M_val=0)
dfB = eval_spec_L(betaB, mB, sB, is_spec_c=False, M_val=18)
dfC = eval_spec_L(betaC, mC, sC, is_spec_c=True)

comp_df = pd.DataFrame({
    'Over': dfA['Over'],
    'Phase': dfA['Phase'],
    'Raw_L_SpecA (Current)': dfA['Raw_L'],
    'Raw_L_SpecB (Shrunk M=18)': dfB['Raw_L'],
    'Raw_L_SpecC (No CRR)': dfC['Raw_L']
})

print("\n--- TRAJECTORY EXPECTED SWING (Raw L) OVER BY OVER ---")
print(comp_df.to_string(index=False))
