import numpy as np
import pandas as pd

def sigmoid(z, k=1.0):
    return 100.0 / (1.0 + np.exp(-k * np.clip(z, -20, 20)))

# Load cohort empirical wicket stats
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
    mu = mu_w_dict.get(L_t, 3.5)
    sig = sigma_w_dict.get(L_t, 1.5)
    return mu, max(0.50, sig)

print("=== PART 3: TASK DIFFICULTY MODEL AUDIT ===")

# Model 1: T_B1
def calc_T_B1(score, L_t, W_t, par=162.4):
    R_par = par / 20.0
    B_rem = max(1, 120 - L_t)
    RAR = max(0.0, (par - score) / (B_rem / 6.0))
    rate_stress = (RAR - R_par) / R_par
    
    if L_t == 0:
        w_stress = 0.0
    else:
        mu_w, sig_w = get_w_stats(L_t)
        w_stress = (W_t - mu_w) / sig_w
        
    Z = 0.60 * rate_stress + 0.40 * w_stress
    return Z, sigmoid(Z, k=1.2)

# Model 2: T_B2
def calc_T_B2(rrr, W_t):
    z_rrr = (rrr - 8.10) / 3.00
    z_w = (W_t - 3.50) / 2.00
    z_inter = (rrr * W_t - 28.0) / 25.0
    Z = 0.55 * z_rrr + 0.25 * z_w + 0.20 * z_inter
    return Z, sigmoid(Z, k=1.0)

# Model 3: T_BO1
def calc_T_BO1(crr, L_t, W_t, phase, par=162.4):
    R_par = par / 20.0
    if L_t == 0:
        crr_stress = 0.0
        w_stress = 0.0
    else:
        crr_stress = (crr - R_par) / R_par
        mu_w, sig_w = get_w_stats(L_t)
        # Batting wickets in hand: (10 - W_t) vs expected (10 - mu_w)
        # (10 - W_t) - (10 - mu_w) = mu_w - W_t
        w_stress = (mu_w - W_t) / sig_w
        
    field_factor = 0.50 if phase in ['PP', 'Powerplay', 'Death'] else 0.00
    Z = 0.50 * crr_stress + 0.35 * w_stress + 0.15 * field_factor
    return Z, sigmoid(Z, k=1.1)

# Model 4: T_BO2
def calc_T_BO2(rrr, L_t, W_t):
    rrr_stress = (8.10 - rrr) / 3.00
    mu_w, sig_w = get_w_stats(L_t)
    w_stress = (mu_w - W_t) / sig_w
    Z = 0.60 * rrr_stress + 0.40 * w_stress
    return Z, sigmoid(Z, k=1.0)

# Test Neutral Conditions:
print("\n--- NEUTRAL CONDITIONS CHECK (Target = 50.0) ---")
z_b1_n, t_b1_n = calc_T_B1(score=0, L_t=0, W_t=0)
print(f"T_B1 Ball 0.1 (0/0, Par 162.4): Z = {z_b1_n:.4f}, T = {t_b1_n:.2f}")

z_b2_n, t_b2_n = calc_T_B2(rrr=8.10, W_t=3.50)
print(f"T_B2 Median (RRR=8.1, W_t=3.5): Z = {z_b2_n:.4f}, T = {t_b2_n:.2f}")

z_bo1_n, t_bo1_n = calc_T_BO1(crr=8.12, L_t=60, W_t=3, phase='Middle')
print(f"T_BO1 Middle over 10 (CRR=Par, W_t=3): Z = {z_bo1_n:.4f}, T = {t_bo1_n:.2f}")

z_bo2_n, t_bo2_n = calc_T_BO2(rrr=8.10, L_t=60, W_t=3)
print(f"T_BO2 Middle over 10 (RRR=8.1, W_t=3): Z = {z_bo2_n:.4f}, T = {t_bo2_n:.2f}")

# Test Boundary & Extreme Conditions:
print("\n--- EXTREME CONDITIONS CHECK ---")
# Extreme Batting Crisis: 15/4 at 3.0 ov (L_t=18)
z_b1_crit, t_b1_crit = calc_T_B1(score=15, L_t=18, W_t=4)
print(f"T_B1 Severe Collapse (15/4 at 3.0 ov): Z = {z_b1_crit:.4f}, T = {t_b1_crit:.2f}")

# Batting Dominance: 120/0 at 10.0 ov (L_t=60)
z_b1_dom, t_b1_dom = calc_T_B1(score=120, L_t=60, W_t=0)
print(f"T_B1 Total Dominance (120/0 at 10.0 ov): Z = {z_b1_dom:.4f}, T = {t_b1_dom:.2f}")

# Impossible Chase: RRR=36.0, W_t=9
z_b2_imp, t_b2_imp = calc_T_B2(rrr=36.0, W_t=9)
print(f"T_B2 Impossible Chase (RRR=36, 9 down): Z = {z_b2_imp:.4f}, T = {t_b2_imp:.2f}")

# Trivial Chase: RRR=0.5, W_t=1
z_b2_triv, t_b2_triv = calc_T_B2(rrr=0.5, W_t=1)
print(f"T_B2 Trivial Chase (RRR=0.5, 1 down): Z = {z_b2_triv:.4f}, T = {t_b2_triv:.2f}")

# Bowling Under Fire: CRR=12.0 at ov 6 (L_t=36), 0 down
z_bo1_fire, t_bo1_fire = calc_T_BO1(crr=12.0, L_t=36, W_t=0, phase='PP')
print(f"T_BO1 Bowling Under Fire (72/0 after PP): Z = {z_bo1_fire:.4f}, T = {t_bo1_fire:.2f}")

# Bowling Dominant: Opponent 25/5 at ov 6 (L_t=36)
z_bo1_dom, t_bo1_dom = calc_T_BO1(crr=4.17, L_t=36, W_t=5, phase='PP')
print(f"T_BO1 Bowling Dominance (25/5 after PP): Z = {z_bo1_dom:.4f}, T = {t_bo1_dom:.2f}")
