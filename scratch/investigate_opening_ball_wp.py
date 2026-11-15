import json
import numpy as np
import pandas as pd

with open('outputs/step_4_pressure_pipeline/wp_model_inn1.json') as f:
    d = json.load(f)
m = np.array(d['means'])
s = np.array(d['stds'])
beta = np.array(d['coefficients'])
feat_names = d['feature_names'][1:]

print("=== INNINGS 1 WP MODEL FEATURE WEIGHTS & SCALING ===")
for name, mean, std, b in zip(feat_names, m, s, beta[1:]):
    print(f"{name:22s}: Mean={mean:+.4f}, Std={std:.4f}, Coeff={b:+.4f}, Effective Weight (Coeff/Std)={b/std:+.4f}")

# Let's inspect the exact shift for each outcome on Ball 0.1
def calc_z(score, legal_balls, wk_lost, par=176.68, crr_override=None):
    wk_rem = 10.0 - wk_lost
    b_bowled = legal_balls / 120.0
    par_to_date = par * b_bowled
    score_diff_par = (score - par_to_date) / 30.0
    if crr_override is not None:
        crr = crr_override
    else:
        crr = (score / max(1.0, legal_balls)) * 6.0
    crr_rel_par = crr / (par / 20.0)
    balls_rem = (120.0 - legal_balls) / 120.0
    res_interaction = wk_rem * balls_rem
    raw = np.array([score_diff_par, wk_rem, b_bowled, res_interaction, crr_rel_par])
    norm = (raw - m) / s
    z = beta[0] + norm @ beta[1:]
    p = 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))
    return p, z, raw, norm

outcomes = [
    ('Dot (0)', 0, 0, 1),
    ('Single (1)', 1, 0, 1),
    ('Two (2)', 2, 0, 1),
    ('Three (3)', 3, 0, 1),
    ('Four (4)', 4, 0, 1),
    ('Six (6)', 6, 0, 1),
    ('Wicket', 0, 1, 1),
    ('Wide', 1, 0, 0),
    ('No-ball', 1, 0, 0)
]

with open('outputs/step_4_pressure_pipeline/outcome_transition_probabilities.json') as f:
    probs = json.load(f)['PP_inn1']

print("\n--- BALL 0.1 DECOMPOSITION WITH EXISTING CRR ---")
p0, z0, r0, n0 = calc_z(0, 0, 0)
print(f"Pre-delivery WP(S_0) = {p0:.5f} (z_0 = {z0:.4f})")

exp_swing_total = 0.0
for (name, r_add, w_add, b_add), p_o in zip(outcomes, probs):
    p_next, z_next, r_next, n_next = calc_z(r_add, b_add, w_add)
    swing = abs(p_next - p0)
    exp_swing_total += p_o * swing
    z_diff = z_next - z0
    # breakdown of z_diff by feature
    z_contribs = (n_next - n0) * beta[1:]
    print(f"{name:12s} (p={p_o:.4f}): WP={p_next:.4f}, Swing={swing:.5f} | z_diff={z_diff:+.4f} [ScoreDiff={z_contribs[0]:+.4f}, WkRem={z_contribs[1]:+.4f}, BBowled={z_contribs[2]:+.4f}, ResInt={z_contribs[3]:+.4f}, CRR={z_contribs[4]:+.4f}]")

print(f"\nTotal Expected Consequence L(S_0) = {exp_swing_total:.6f}")
