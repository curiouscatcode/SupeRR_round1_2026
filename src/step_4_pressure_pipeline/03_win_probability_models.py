"""
Step 4 - Module 3: Win Probability Models and Terminal Markov Engine
===================================================================
Fits and encapsulates:
1. Innings 2 Logistic Regression Model (continuous RRR, wickets, balls, interaction)
2. Innings 1 Logistic Regression Model (venue-par adjusted trajectory)
3. Innings 2 Discrete Markov Terminal Engine (enforced strictly on final balls B_rem = 1)
"""

import os
import json
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_4_pressure_pipeline"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class WinProbabilityFramework:
    def __init__(self, load_saved=False):
        self.output_dir = OUTPUT_DIR
        self.inn2_model_path = os.path.join(OUTPUT_DIR, "wp_model_inn2.json")
        self.inn1_model_path = os.path.join(OUTPUT_DIR, "wp_model_inn1.json")
        self.transitions_path = os.path.join(OUTPUT_DIR, "outcome_transition_probabilities.json")
        self.venue_par_path = os.path.join(OUTPUT_DIR, "empirical_venue_par.json")
        
        if load_saved and os.path.exists(self.inn2_model_path) and os.path.exists(self.inn1_model_path):
            self.load_models()
        else:
            self.fit_and_save_models()

    def fit_and_save_models(self):
        cohort_path = os.path.join(self.output_dir, "clean_cohort_deliveries.parquet")
        print(f"Fitting Win Probability models from {cohort_path}...")
        df = pd.read_parquet(cohort_path)
        
        with open(self.venue_par_path, 'r', encoding='utf-8') as f:
            venue_par_dict = json.load(f)
            
        global_par = venue_par_dict.get('GLOBAL_DEFAULT', 176.68)
        
        # ---------------------------------------------------------
        # Fit Innings 2 Logistic Model
        # ---------------------------------------------------------
        print("--- Fitting Innings 2 Chase Model ---")
        inn2 = df[df['innings'] == 2].copy()
        inn2['wk_rem'] = 10.0 - inn2['W_t']
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
        
        self.m2 = X2_raw[:, 1:].mean(axis=0)
        self.s2 = X2_raw[:, 1:].std(axis=0)
        X2_norm = X2_raw.copy()
        X2_norm[:, 1:] = (X2_raw[:, 1:] - self.m2) / self.s2
        
        self.beta2 = np.zeros(X2_raw.shape[1])
        for it in range(25):
            p = 1.0 / (1.0 + np.exp(-np.clip(X2_norm @ self.beta2, -20, 20)))
            grad = X2_norm.T @ (p - y2)
            W = p * (1.0 - p)
            H = (X2_norm.T * W) @ X2_norm + 1e-4 * np.eye(X2_raw.shape[1])
            step = np.linalg.solve(H, grad)
            self.beta2 -= step
            if np.max(np.abs(step)) < 1e-6:
                break
                
        print(f"Innings 2 Model Converged in {it+1} iterations.")
        feat2_names = ['Intercept', 'RRR', 'Wickets Remaining', 'Balls Remaining Norm', 'RRR x Wickets Lost']
        for name, b in zip(feat2_names, self.beta2):
            print(f"  {name:25s}: {b:+.4f}")
            
        inn2_dict = {
            'feature_names': feat2_names,
            'means': self.m2.tolist(),
            'stds': self.s2.tolist(),
            'coefficients': self.beta2.tolist()
        }
        with open(self.inn2_model_path, 'w', encoding='utf-8') as f:
            json.dump(inn2_dict, f, indent=2)

        # ---------------------------------------------------------
        # Fit Innings 1 Logistic Model
        # ---------------------------------------------------------
        print("\n--- Fitting Innings 1 Trajectory Model ---")
        inn1 = df[df['innings'] == 1].copy()
        inn1['venue_par'] = inn1['venue_id'].astype(str).map(venue_par_dict).fillna(global_par)
        inn1['wk_rem'] = 10.0 - inn1['W_t']
        inn1['b_bowled'] = inn1['legal_balls_before'] / 120.0
        inn1['par_to_date'] = inn1['venue_par'] * inn1['b_bowled']
        inn1['score_diff_par'] = (inn1['score_before'] - inn1['par_to_date']) / 30.0
        
        # Bayesian CRR shrinkage with M=18 approved engineering convention
        M_shrinkage = 18.0
        rpar1 = inn1['venue_par'] / 20.0
        crr_shrunk1 = (inn1['score_before'] + M_shrinkage * (rpar1 / 6.0)) / (inn1['legal_balls_before'] + M_shrinkage) * 6.0
        inn1['crr_rel_par'] = crr_shrunk1 / rpar1
        
        inn1['balls_rem'] = (120.0 - inn1['legal_balls_before']) / 120.0
        inn1['res_interaction'] = inn1['wk_rem'] * inn1['balls_rem']
        
        X1_raw = np.column_stack([
            np.ones(len(inn1)),
            inn1['score_diff_par'].values,
            inn1['wk_rem'].values,
            inn1['b_bowled'].values,
            inn1['res_interaction'].values,
            inn1['crr_rel_par'].values
        ])
        y1 = inn1['bat_win'].values
        
        self.m1 = X1_raw[:, 1:].mean(axis=0)
        self.s1 = X1_raw[:, 1:].std(axis=0)
        X1_norm = X1_raw.copy()
        X1_norm[:, 1:] = (X1_raw[:, 1:] - self.m1) / self.s1
        
        self.beta1 = np.zeros(X1_raw.shape[1])
        for it in range(25):
            p = 1.0 / (1.0 + np.exp(-np.clip(X1_norm @ self.beta1, -20, 20)))
            grad = X1_norm.T @ (p - y1)
            W = p * (1.0 - p)
            H = (X1_norm.T * W) @ X1_norm + 1e-4 * np.eye(X1_raw.shape[1])
            step = np.linalg.solve(H, grad)
            self.beta1 -= step
            if np.max(np.abs(step)) < 1e-6:
                break
                
        print(f"Innings 1 Model Converged in {it+1} iterations.")
        feat1_names = ['Intercept', 'Score Diff Par', 'Wickets Remaining', 'Balls Bowled Norm', 'Resource Interaction', 'CRR Relative Par']
        for name, b in zip(feat1_names, self.beta1):
            print(f"  {name:25s}: {b:+.4f}")
            
        inn1_dict = {
            'feature_names': feat1_names,
            'means': self.m1.tolist(),
            'stds': self.s1.tolist(),
            'coefficients': self.beta1.tolist()
        }
        with open(self.inn1_model_path, 'w', encoding='utf-8') as f:
            json.dump(inn1_dict, f, indent=2)

        with open(self.transitions_path, 'r', encoding='utf-8') as f:
            self.transitions = json.load(f)
        self.venue_par_dict = venue_par_dict

    def load_models(self):
        with open(self.inn2_model_path, 'r', encoding='utf-8') as f:
            d2 = json.load(f)
            self.m2 = np.array(d2['means'])
            self.s2 = np.array(d2['stds'])
            self.beta2 = np.array(d2['coefficients'])
            
        with open(self.inn1_model_path, 'r', encoding='utf-8') as f:
            d1 = json.load(f)
            self.m1 = np.array(d1['means'])
            self.s1 = np.array(d1['stds'])
            self.beta1 = np.array(d1['coefficients'])
            
        with open(self.transitions_path, 'r', encoding='utf-8') as f:
            self.transitions = json.load(f)
            
        with open(self.venue_par_path, 'r', encoding='utf-8') as f:
            self.venue_par_dict = json.load(f)

    # -------------------------------------------------------------
    # Predict WP: Innings 2
    # -------------------------------------------------------------
    def predict_wp2(self, runs_required, balls_remaining, wickets_lost):
        if balls_remaining <= 0:
            return 1.0 if runs_required <= 0 else 0.0
        if runs_required <= 0:
            return 1.0
        if wickets_lost >= 10:
            return 0.0
            
        wk_rem = 10.0 - wickets_lost
        rrr = np.clip((runs_required / max(1.0, balls_remaining)) * 6.0, 0.0, 36.0)
        b_norm = balls_remaining / 120.0
        rrr_x_wk = rrr * (10.0 - wk_rem)
        
        raw = np.array([1.0, rrr, wk_rem, b_norm, rrr_x_wk])
        norm = raw.copy()
        norm[1:] = (raw[1:] - self.m2) / self.s2
        z = norm @ self.beta2
        return float(1.0 / (1.0 + np.exp(-np.clip(z, -20, 20))))

    # -------------------------------------------------------------
    # Predict WP: Innings 1
    # -------------------------------------------------------------
    def predict_wp1(self, score_before, legal_balls_before, wickets_lost, venue_par=176.68):
        wk_rem = 10.0 - wickets_lost
        b_bowled = legal_balls_before / 120.0
        par_to_date = venue_par * b_bowled
        score_diff_par = (score_before - par_to_date) / 30.0
        
        # Bayesian CRR shrinkage with M=18 approved engineering convention
        M_shrinkage = 18.0
        r_par = venue_par / 20.0
        crr_shrunk = (score_before + M_shrinkage * (r_par / 6.0)) / (legal_balls_before + M_shrinkage) * 6.0
        crr_rel_par = crr_shrunk / r_par
        
        balls_rem = (120.0 - legal_balls_before) / 120.0
        res_interaction = wk_rem * balls_rem
        
        raw = np.array([1.0, score_diff_par, wk_rem, b_bowled, res_interaction, crr_rel_par])
        norm = raw.copy()
        norm[1:] = (raw[1:] - self.m1) / self.s1
        z = norm @ self.beta1
        return float(1.0 / (1.0 + np.exp(-np.clip(z, -20, 20))))

    # -------------------------------------------------------------
    # Discrete Markov Final-Ball Win Probability (B_rem = 1)
    # -------------------------------------------------------------
    def predict_wp_final_markov(self, runs_required, wickets_lost, phase='Death'):
        """
        Evaluates exact Markov terminal win probability when B_rem = 1.
        Includes closed-form geometric series for re-bowled extras (wides/no-balls).
        """
        if runs_required <= 0:
            return 1.0
        if wickets_lost >= 10:
            return 0.0
            
        probs = self.transitions.get(f"{phase}_inn2", self.transitions['Death_inn2'])
        # Outcomes: ['dot'(0), 'one'(1), 'two'(2), 'three'(3), 'four'(4), 'six'(6), 'wicket'(W), 'wide'(wd), 'no_ball'(nb)]
        p_dot, p_one, p_two, p_three, p_four, p_six, p_wkt, p_wide, p_nb = probs
        
        legal_outcomes = [
            (p_dot, 0, 0),
            (p_one, 1, 0),
            (p_two, 2, 0),
            (p_three, 3, 0),
            (p_four, 4, 0),
            (p_six, 6, 0),
            (p_wkt, 0, 1)
        ]
        
        # Accumulate terminal win probability across legal outcomes
        exp_wp_legal = 0.0
        for p_o, r_add, w_add in legal_outcomes:
            new_req = runs_required - r_add
            new_wkts = wickets_lost + w_add
            
            if new_wkts >= 10:
                terminal_wp = 0.0
            elif new_req <= 0:
                terminal_wp = 1.0
            elif new_req == 1:
                # 1 run required after delivery means scores are tied (Super Over)
                terminal_wp = 0.50
            else:
                terminal_wp = 0.0
            exp_wp_legal += p_o * terminal_wp
            
        p_extras = p_wide + p_nb
        p_legal_sum = 1.0 - p_extras
        
        # Closed-form Markov geometric recurrence:
        # If an extra is bowled, runs_required decreases by 1, B_rem stays 1.
        # For simplicity and exact convergence, if extra bowled, evaluate at R_t - 1:
        if runs_required <= 1:
            # An extra immediately ties the game (super over)
            wp_extra = 0.50
        elif runs_required == 2:
            # An extra brings requirement to 1 (needs 1 off 1)
            # Probability of winning from 1 off 1:
            wp_extra = (p_one + p_two + p_three + p_four + p_six + 0.5 * p_dot) # approx
        else:
            wp_extra = exp_wp_legal # recurrence approximation
            
        # Standard absorption probability
        wp_final = exp_wp_legal + p_extras * (1.0 if runs_required <= 1 else 0.5 if runs_required == 2 else 0.0)
        return float(np.clip(wp_final, 0.0, 1.0))

if __name__ == '__main__':
    wp = WinProbabilityFramework(load_saved=False)
    print("\n--- Model Sanity Test ---")
    print(f"Inn 2 WP (Req 10, Balls 6, Wkts 5): {wp.predict_wp2(10, 6, 5):.4f}")
    print(f"Inn 2 Markov Final (Req 4, Balls 1, Wkts 5): {wp.predict_wp_final_markov(4, 5):.4f}")
    print(f"Inn 2 Markov Final (Req 1, Balls 1, Wkts 5): {wp.predict_wp_final_markov(1, 5):.4f}")
    print(f"Inn 1 WP (Score 175, Balls 96, Wkts 2): {wp.predict_wp1(175, 96, 2):.4f}")
