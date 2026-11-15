"""
Step 2.1 - Issue 4: Investigation of Final-Ball Win-Probability Behavior
========================================================================
Investigates the breakdown of the continuous RRR logistic regression on the
final ball (balls_remaining == 1) and formulates a principled discrete
terminal-ball treatment based on Markov expectations.
"""

import os
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_2_1_infrastructure_corrections"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=== ISSUE 4: FINAL-BALL WIN-PROBABILITY BEHAVIOR INVESTIGATION ===")

# 1. Load clean active delivery dataset and situation outcome probabilities
dms = pd.read_csv("data/processed/delivery_match_state.csv")
dms_clean = dms[
    (~dms['match_id'].isin([20182, 23674, 24822, 28334])) &
    (~((dms['innings'] == 2) & (dms['runs_required'] <= 0)))
].copy().reset_index(drop=True)

matches = pd.read_csv("data/matches.csv")
dms_clean = dms_clean.merge(matches[['match_id', 'win_team_id']], on='match_id', how='left')
dms_clean['bat_win'] = (dms_clean['batting_team_id'] == dms_clean['win_team_id']).astype(float)

# Fit the standard Innings 2 Logistic Model
inn2 = dms_clean[dms_clean['innings'] == 2].copy()
inn2['wk_rem'] = 10.0 - inn2['wickets_before']
inn2['rrr'] = ((inn2['runs_required'] / np.maximum(1.0, inn2['balls_remaining'])) * 6.0).clip(0, 36)
inn2['b_norm'] = inn2['balls_remaining'] / 120.0
inn2['rrr_x_wk'] = inn2['rrr'] * (10.0 - inn2['wk_rem'])

X2_raw = np.column_stack([
    np.ones(len(inn2)),
    inn2['rrr'].values,
    inn2['wk_rem'].values,
    inn2['b_norm'].values,
    inn2['rrr_x_wk'].values
])
y2 = inn2['bat_win'].values
m2 = X2_raw[:, 1:].mean(axis=0)
s2 = X2_raw[:, 1:].std(axis=0)
X2_norm = X2_raw.copy()
X2_norm[:, 1:] = (X2_raw[:, 1:] - m2) / s2

beta2 = np.zeros(X2_raw.shape[1])
for _ in range(15):
    p = 1.0 / (1.0 + np.exp(-np.clip(X2_norm @ beta2, -20, 20)))
    grad = X2_norm.T @ (p - y2)
    W = p * (1.0 - p)
    H = (X2_norm.T * W) @ X2_norm + 1e-4 * np.eye(X2_raw.shape[1])
    step = np.linalg.solve(H, grad)
    beta2 -= step
    if np.max(np.abs(step)) < 1e-5: break

def predict_wp2_continuous(runs_req_v, balls_rem_v, wk_rem_v):
    """Current continuous RRR logistic model with boundary enforcement."""
    req = np.maximum(0.0, np.array(runs_req_v, dtype=float))
    rem = np.maximum(0.0, np.array(balls_rem_v, dtype=float))
    wk = np.maximum(0.0, np.minimum(10.0, np.array(wk_rem_v, dtype=float)))

    rc = np.where(rem > 0, (req / np.maximum(1.0, rem)) * 6.0, 36.0)
    rc = np.clip(rc, 0.0, 36.0)
    bn = rem / 120.0
    interaction = rc * (10.0 - wk)

    x_raw = np.column_stack([np.ones(len(req)), rc, wk, bn, interaction])
    x_norm = x_raw.copy()
    x_norm[:, 1:] = (x_raw[:, 1:] - m2) / s2

    logistic_p = 1.0 / (1.0 + np.exp(-np.clip(x_norm @ beta2, -20, 20)))

    wp_final = np.where(req <= 0, 1.0,
               np.where(wk <= 0, 0.0,
               np.where(rem <= 0, 0.0, logistic_p)))
    return wp_final

# 2. Extract empirical outcome transition probabilities for Death Phase (Innings 2)
outcome_csv = "outputs/step_16_5_wpa_investigation/situation_outcome_probabilities.csv"
if os.path.exists(outcome_csv):
    out_probs_df = pd.read_csv(outcome_csv)
    death_probs = out_probs_df[(out_probs_df['innings'] == 2) & (out_probs_df['phase'] == 'Death')].iloc[0]
else:
    raise FileNotFoundError("situation_outcome_probabilities.csv not found!")

outcome_defs = {
    'dot':        {'r': 0, 'l': 1, 'w': 0},
    '1':          {'r': 1, 'l': 1, 'w': 0},
    '2':          {'r': 2, 'l': 1, 'w': 0},
    '3':          {'r': 3, 'l': 1, 'w': 0},
    '4':          {'r': 4, 'l': 1, 'w': 0},
    '6':          {'r': 6, 'l': 1, 'w': 0},
    'wicket':     {'r': 0, 'l': 1, 'w': 1},
    'wide':       {'r': 1, 'l': 0, 'w': 0},
    'noball':     {'r': 2, 'l': 0, 'w': 0},
    'other_runs': {'r': 5, 'l': 1, 'w': 0}
}

p_event = {k: float(death_probs[k]) for k in outcome_defs.keys() if k in death_probs}
print("\nInnings 2 Death Phase Empirical Outcome Probabilities:")
for k, v in p_event.items():
    print(f"  {k:12s}: {v*100:6.3f}%")

# 3. Simulate and test all outcomes from identical final-ball pre-delivery states
print("\n--- Testing All Possible Outcomes for Final-Ball States (balls_remaining == 1) ---")

scenarios = [
    ("1 run required (Tie/Win)", 1, 1, 5),
    ("2 runs required", 2, 1, 5),
    ("3 runs required", 3, 1, 5),
    ("4 runs required (Boundary Needed)", 4, 1, 5),
    ("5 runs required", 5, 1, 5),
    ("6 runs required (Six Needed)", 6, 1, 5),
    ("7 runs required (Extra + Boundary Needed)", 7, 1, 5),
]

test_results = []

for desc, req, rem, wk in scenarios:
    wp_continuous_pre = predict_wp2_continuous([req], [rem], [wk])[0]
    
    # Evaluate every discrete outcome
    outcome_evals = {}
    discrete_expected_wp = 0.0
    
    for ev_name, ev_props in outcome_defs.items():
        p_k = p_event.get(ev_name, 0.0)
        post_req = max(0, req - ev_props['r'])
        post_rem = max(0, rem - ev_props['l'])
        post_wk = max(0, wk - ev_props['w'])
        
        # Post-delivery WP
        # Note: If post_rem == 0 and post_req > 0 -> 0.0 (balls expired)
        # If post_req <= 0 -> 1.0 (target reached)
        # If wide/noball: post_rem == 1, post_req = req - r. Ball re-bowled!
        if post_req <= 0:
            post_wp = 1.0
        elif post_wk <= 0 or post_rem <= 0:
            post_wp = 0.0
        else:
            # Ball re-bowled (wide/no-ball)
            post_wp = predict_wp2_continuous([post_req], [post_rem], [post_wk])[0]
            
        outcome_evals[ev_name] = post_wp
        discrete_expected_wp += p_k * post_wp
        
    test_results.append({
        'scenario': desc,
        'req': req,
        'balls_rem': rem,
        'wk_rem': wk,
        'rrr': (req / rem) * 6.0,
        'continuous_wp_pre': wp_continuous_pre,
        'discrete_expected_wp_pre': discrete_expected_wp,
        'wp_if_dot': outcome_evals['dot'],
        'wp_if_one': outcome_evals['1'],
        'wp_if_two': outcome_evals['2'],
        'wp_if_four': outcome_evals['4'],
        'wp_if_six': outcome_evals['6'],
        'wp_if_wicket': outcome_evals['wicket'],
        'wp_if_wide': outcome_evals['wide'],
        'wp_if_noball': outcome_evals['noball']
    })

res_df = pd.DataFrame(test_results)
print("\nFinal-Ball Comparison Table: Continuous vs Discrete Expectation:")
display_cols = ['scenario', 'req', 'rrr', 'continuous_wp_pre', 'discrete_expected_wp_pre', 'wp_if_four', 'wp_if_six', 'wp_if_dot']
print(res_df[display_cols].to_string(index=False))

# 4. Detailed analysis of the divergence
print("\n--- Critical Diagnostic Findings ---")
print("1. When 6 runs are needed off 1 ball:")
print(f"   - Continuous RRR Model predicts:   {res_df.loc[5, 'continuous_wp_pre']*100:.4f}%")
print(f"   - Discrete Markov Model predicts:  {res_df.loc[5, 'discrete_expected_wp_pre']*100:.2f}% (reflects P(six) = {p_event['6']*100:.2f}% + extras)")
print("2. When 4 runs are needed off 1 ball:")
print(f"   - Continuous RRR Model predicts:   {res_df.loc[3, 'continuous_wp_pre']*100:.2f}%")
print(f"   - Discrete Markov Model predicts:  {res_df.loc[3, 'discrete_expected_wp_pre']*100:.2f}% (reflects P(four) + P(six) + extras)")
print("3. When 1 run is needed off 1 ball:")
print(f"   - Continuous RRR Model predicts:   {res_df.loc[0, 'continuous_wp_pre']*100:.2f}%")
print(f"   - Discrete Markov Model predicts:  {res_df.loc[0, 'discrete_expected_wp_pre']*100:.2f}% (sum of all scoring outcomes)")

# Save full results table
csv_out = os.path.join(OUTPUT_DIR, "final_ball_wp_comparison.csv")
res_df.to_csv(csv_out, index=False)
print(f"\nSaved final-ball comparison table to {csv_out}")

# 5. Feasibility of Discrete Final-Ball Treatment in Pre-Delivery State
print("\n--- Mathematical Principles of Discrete Final-Ball Treatment ---")
print("Principle: The terminal state is an absorbingly discrete Markov transition.")
print("For balls_remaining == 1, rather than projecting a continuous RRR (which scales to 36.0),")
print("the pre-delivery WP is the mathematically sound expectation:")
print("  WP_pre(R, 1, W) = Sum_k P(outcome_k | Death, Innings 2) * WP_post(S_{t+1}(k))")
print("This uses ONLY pre-delivery empirical outcome probabilities, requires ZERO arbitrary heuristics,")
print("and aligns pre-delivery WP with the actual Laws of Cricket.")
