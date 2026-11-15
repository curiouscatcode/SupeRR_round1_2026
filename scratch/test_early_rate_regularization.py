import json
import numpy as np
import pandas as pd

with open('outputs/step_4_pressure_pipeline/wp_model_inn1.json') as f:
    d = json.load(f)
m = np.array(d['means'])
s = np.array(d['stds'])
beta = np.array(d['coefficients'])

with open('outputs/step_4_pressure_pipeline/outcome_transition_probabilities.json') as f:
    probs = json.load(f)['PP_inn1']

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

def eval_ball_01_consequence(shrinkage_M=0, init_crr_par=False, par=176.68):
    r_par = par / 20.0
    
    def get_crr(score, legal_balls):
        if legal_balls == 0:
            return r_par if init_crr_par else 0.0
        if shrinkage_M == 0:
            return (score / legal_balls) * 6.0
        # Bayesian shrinkage towards venue par
        # Effective balls = legal_balls + M
        # Effective runs = score + M * (r_par / 6.0)
        eff_balls = legal_balls + shrinkage_M
        eff_runs = score + shrinkage_M * (r_par / 6.0)
        return (eff_runs / eff_balls) * 6.0

    def calc_wp(score, legal_balls, wk_lost):
        wk_rem = 10.0 - wk_lost
        b_bowled = legal_balls / 120.0
        par_to_date = par * b_bowled
        score_diff_par = (score - par_to_date) / 30.0
        crr = get_crr(score, legal_balls)
        crr_rel_par = crr / r_par
        balls_rem = (120.0 - legal_balls) / 120.0
        res_interaction = wk_rem * balls_rem
        raw = np.array([score_diff_par, wk_rem, b_bowled, res_interaction, crr_rel_par])
        norm = (raw - m) / s
        z = beta[0] + norm @ beta[1:]
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))

    wp0 = calc_wp(0, 0, 0)
    exp_swing = 0.0
    swings = {}
    for (name, r_add, w_add, b_add), p_o in zip(outcomes, probs):
        wp_next = calc_wp(r_add, b_add, w_add)
        sw = abs(wp_next - wp0)
        exp_swing += p_o * sw
        swings[name] = (wp_next, sw)
    return wp0, exp_swing, swings

print("=== EVALUATION OF EARLY-RATE REGULARIZATION METHODS ON BALL 0.1 ===")
print("Method                                        | WP(S_0) | Raw L(S_0) | Swing(Dot) | Swing(Four) | Swing(Six) | Swing(Wkt)")
print("-" * 110)

configs = [
    ("1. Baseline (M=0, Init CRR=0.0)", 0, False),
    ("2. Init Neutral CRR (M=0, Init CRR=R_par)", 0, True),
    ("3. Bayesian Shrinkage M=6 (1 over)", 6, True),
    ("4. Bayesian Shrinkage M=12 (2 overs)", 12, True),
    ("5. Bayesian Shrinkage M=18 (3 overs)", 18, True),
    ("6. Bayesian Shrinkage M=24 (4 overs)", 24, True),
    ("7. Bayesian Shrinkage M=36 (6 overs / PP)", 36, True),
]

for label, M, init_par in configs:
    wp0, exp_L, swings = eval_ball_01_consequence(shrinkage_M=M, init_crr_par=init_par)
    print(f"{label:45s} | {wp0:.4f}  |  {exp_L:.6f}  |  {swings['Dot (0)'][1]:.5f}   |   {swings['Four (4)'][1]:.5f}   |  {swings['Six (6)'][1]:.5f}   |  {swings['Wicket'][1]:.5f}")
