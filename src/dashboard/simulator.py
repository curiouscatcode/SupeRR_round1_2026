"""
src/dashboard/simulator.py
Real-time, exact mathematical simulator for match state pressure calculations.
Directly implements the Step 4 & Step 10 approved equations:
- Logistic Task Difficulty (T_B1, T_B2, T_BO1, T_BO2)
- Win Probability models (WP_inn1, WP_inn2)
- Expected Consequence L via 9-outcome expectations
- Innings-calibrated ECDF lookup -> L_norm
- Orthogonal Geometric Mean: P = sqrt(T * L_norm)
"""

import json
import os
import numpy as np
import pandas as pd

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STEP4_DIR = os.path.join(BASE_DIR, "outputs", "step_4_pressure_pipeline")

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

class MatchPressureSimulator:
    def __init__(self):
        # 1. Load WP model weights
        with open(os.path.join(STEP4_DIR, "wp_model_inn1.json"), 'r', encoding='utf-8') as f:
            inn1_dict = json.load(f)
            self.m1 = np.array(inn1_dict['means'])
            self.s1 = np.array(inn1_dict['stds'])
            self.beta1 = np.array(inn1_dict['coefficients'])

        with open(os.path.join(STEP4_DIR, "wp_model_inn2.json"), 'r', encoding='utf-8') as f:
            inn2_dict = json.load(f)
            self.m2 = np.array(inn2_dict['means'])
            self.s2 = np.array(inn2_dict['stds'])
            self.beta2 = np.array(inn2_dict['coefficients'])

        # 2. Outcome transition probabilities
        with open(os.path.join(STEP4_DIR, "outcome_transition_probabilities.json"), 'r', encoding='utf-8') as f:
            self.transition_probs = json.load(f)

        # 3. Frozen ECDF percentiles
        with open(os.path.join(STEP4_DIR, "frozen_ecdf_distributions.json"), 'r', encoding='utf-8') as f:
            ecdf_data = json.load(f)
            self.ecdf1_pcts = np.array([float(k) for k in ecdf_data['inn1_percentiles'].keys()])
            self.ecdf1_vals = np.array(list(ecdf_data['inn1_percentiles'].values()))
            self.ecdf2_pcts = np.array([float(k) for k in ecdf_data['inn2_percentiles'].keys()])
            self.ecdf2_vals = np.array(list(ecdf_data['inn2_percentiles'].values()))

        # 4. Empirical wicket curves
        w_df = pd.read_csv(os.path.join(STEP4_DIR, "empirical_wicket_curve.csv"))
        self.mu_w_dict = dict(zip(w_df['legal_balls_before'], w_df['mean']))
        self.sig_w_dict = dict(zip(w_df['legal_balls_before'], w_df['regularized_std']))

    def compute_wp_inn1(self, score, lballs, wt, venue_par=176.68):
        lballs_cl = min(120, max(0, lballs))
        wt_cl = min(10, max(0, wt))
        if wt_cl >= 10:
            return 0.0
            
        wk_rem = 10.0 - wt_cl
        b_bowled = lballs_cl / 120.0
        par_to_date = venue_par * b_bowled
        score_diff_par = (score - par_to_date) / 30.0

        rpar = venue_par / 20.0
        crr_shrunk = (score + 18.0 * (rpar / 6.0)) / (lballs_cl + 18.0) * 6.0
        crr_rel_par = crr_shrunk / rpar

        balls_rem = (120.0 - lballs_cl) / 120.0
        res_inter = wk_rem * balls_rem

        raw = np.array([score_diff_par, wk_rem, b_bowled, res_inter, crr_rel_par])
        norm = (raw - self.m1) / self.s1
        x = np.concatenate([[1.0], norm])
        z = np.dot(x, self.beta1)
        return float(1.0 / (1.0 + np.exp(-np.clip(z, -20.0, 20.0))))

    def compute_wp_inn2(self, runs_req, brem, wt):
        wt_cl = min(10, max(0, wt))
        if runs_req <= 0:
            return 1.0
        if wt_cl >= 10 or brem <= 0:
            return 0.0

        wk_rem = 10.0 - wt_cl
        if brem == 1:
            p_bound = 0.055 if wk_rem == 1 else 0.155
            if runs_req > 6:
                return 0.001
            elif runs_req in [5, 6]:
                return 0.50 * p_bound
            elif runs_req in [3, 4]:
                return 1.00 * p_bound
            elif runs_req == 2:
                return 2.50 * p_bound
            else: # 1 run
                return 1.0 - (0.45 * (0.045 if wk_rem == 1 else 0.015))

        rrr = float(np.clip((runs_req / max(1.0, brem)) * 6.0, 0.0, 36.0))
        b_norm = brem / 120.0
        rrr_x_wk = rrr * (10.0 - wk_rem)

        raw = np.array([rrr, wk_rem, b_norm, rrr_x_wk])
        norm = (raw - self.m2) / self.s2
        x = np.concatenate([[1.0], norm])
        z = np.dot(x, self.beta2)
        return float(1.0 / (1.0 + np.exp(-np.clip(z, -20.0, 20.0))))

    def compute_leverage_and_lnorm(self, innings, balls_remaining, score, wickets_lost, runs_required=None, venue_par=176.68):
        lballs = 120 - balls_remaining
        if balls_remaining > 84:
            phase = 'PP'
        elif balls_remaining > 30:
            phase = 'Middle'
        else:
            phase = 'Death'

        key = f"{phase}_inn{innings}"
        p_vec = self.transition_probs.get(key, self.transition_probs['Middle_inn1'])

        if innings == 1:
            curr_wp = self.compute_wp_inn1(score, lballs, wickets_lost, venue_par)
            cum_swing = 0.0
            for p_o, (_, r_add, w_add, b_add) in zip(p_vec, OUTCOMES_CONFIG):
                next_score = score + r_add
                next_lballs = lballs + b_add
                next_wt = wickets_lost + w_add
                wp_next = self.compute_wp_inn1(next_score, next_lballs, next_wt, venue_par)
                cum_swing += p_o * abs(wp_next - curr_wp)
            raw_L = cum_swing
            l_norm = float(np.interp(raw_L, self.ecdf1_vals, self.ecdf1_pcts))
        else:
            curr_wp = self.compute_wp_inn2(runs_required, balls_remaining, wickets_lost)
            cum_swing = 0.0
            for p_o, (_, r_add, w_add, b_add) in zip(p_vec, OUTCOMES_CONFIG):
                next_req = max(0, runs_required - r_add)
                next_brem = max(0, balls_remaining - b_add)
                next_wt = wickets_lost + w_add
                wp_next = self.compute_wp_inn2(next_req, next_brem, next_wt)
                cum_swing += p_o * abs(wp_next - curr_wp)
            raw_L = cum_swing
            l_norm = float(np.interp(raw_L, self.ecdf2_vals, self.ecdf2_pcts))

        return curr_wp, raw_L, float(np.clip(l_norm, 0.0, 100.0)), phase

    def compute_task_difficulty(self, innings, balls_remaining, score, wickets_lost, runs_required=None, venue_par=176.68):
        lballs = 120 - balls_remaining
        mu_w = self.mu_w_dict.get(lballs, 3.5)
        sig_w = self.sig_w_dict.get(lballs, 1.5)
        rpar = venue_par / 20.0

        if balls_remaining > 84:
            phase = 'PP'
        elif balls_remaining > 30:
            phase = 'Middle'
        else:
            phase = 'Death'

        if innings == 1:
            brem = max(1.0, float(balls_remaining))
            rar = max(0.0, (venue_par - score) / (brem / 6.0))
            rate_stress = (rar - rpar) / rpar
            w_stress = 0.0 if lballs == 0 else (wickets_lost - mu_w) / sig_w
            z_b1 = 0.60 * rate_stress + 0.40 * w_stress
            t_bat = 100.0 / (1.0 + np.exp(-1.2 * np.clip(z_b1, -20.0, 20.0)))

            crr1 = rpar if lballs == 0 else (score / max(1.0, lballs)) * 6.0
            crr_stress1 = (crr1 - rpar) / rpar
            w_opp_stress1 = 0.0 if lballs == 0 else (mu_w - wickets_lost) / sig_w
            field_factor1 = 0.50 if phase in ['PP', 'Death'] else 0.00
            z_bo1 = 0.50 * crr_stress1 + 0.35 * w_opp_stress1 + 0.15 * field_factor1
            t_bowl = 100.0 / (1.0 + np.exp(-1.1 * np.clip(z_bo1, -20.0, 20.0)))
        else:
            brem = max(1.0, float(balls_remaining))
            rrr = np.clip((runs_required / brem) * 6.0, 0.0, 36.0)
            z_rrr = (rrr - 8.10) / 3.00
            z_w = (wickets_lost - 3.50) / 2.00
            z_inter = (rrr * wickets_lost - 28.0) / 25.0
            z_b2 = 0.55 * z_rrr + 0.25 * z_w + 0.20 * z_inter
            t_bat = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_b2, -20.0, 20.0)))

            rrr_stress2 = (8.10 - rrr) / 3.00
            w_opp_stress2 = (mu_w - wickets_lost) / sig_w
            z_bo2 = 0.60 * rrr_stress2 + 0.40 * w_opp_stress2
            t_bowl = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_bo2, -20.0, 20.0)))

        return float(np.clip(t_bat, 0.0, 100.0)), float(np.clip(t_bowl, 0.0, 100.0))

    def simulate(self, innings, balls_remaining, score, wickets_lost, target=None, venue_par=176.68):
        runs_req = (target - score) if (innings == 2 and target is not None) else None
        if innings == 2 and runs_req is None:
            runs_req = max(1, 180 - score)

        t_bat, t_bowl = self.compute_task_difficulty(innings, balls_remaining, score, wickets_lost, runs_req, venue_par)
        wp, raw_L, l_norm, phase = self.compute_leverage_and_lnorm(innings, balls_remaining, score, wickets_lost, runs_req, venue_par)

        p_bat = float(np.clip(np.sqrt(t_bat * l_norm), 0.0, 100.0))
        p_bowl = float(np.clip(np.sqrt(t_bowl * l_norm), 0.0, 100.0))

        # Classify pressure band
        if p_bat >= 75.0:
            band_bat = "Crucible / Climax (P ≥ 75)"
        elif p_bat >= 50.0:
            band_bat = "High Pressure (50 ≤ P < 75)"
        elif p_bat >= 30.0:
            band_bat = "Moderate / Par (30 ≤ P < 50)"
        else:
            band_bat = "Low Pressure (P < 30)"

        if p_bowl >= 75.0:
            band_bowl = "Crucible / Climax (P ≥ 75)"
        elif p_bowl >= 50.0:
            band_bowl = "High Pressure (50 ≤ P < 75)"
        elif p_bowl >= 30.0:
            band_bowl = "Moderate / Par (30 ≤ P < 50)"
        else:
            band_bowl = "Low Pressure (P < 30)"

        return {
            'innings': innings,
            'phase': phase,
            'balls_remaining': balls_remaining,
            'score': score,
            'wickets_lost': wickets_lost,
            'runs_required': runs_req,
            'wp_batting': wp,
            'raw_consequence_L': raw_L,
            'normalized_consequence_L': l_norm,
            'task_difficulty_bat': t_bat,
            'task_difficulty_bowl': t_bowl,
            'pressure_batting': p_bat,
            'pressure_bowling': p_bowl,
            'pressure_band_batting': band_bat,
            'pressure_band_bowling': band_bowl,
            'rrr': (runs_req / max(1.0, balls_remaining) * 6.0) if runs_req is not None else None,
            'crr': (score / max(1.0, 120 - balls_remaining) * 6.0)
        }
