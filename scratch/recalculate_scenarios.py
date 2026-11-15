import numpy as np

def sigmoid(z, k=1.0):
    return 100.0 / (1.0 + np.exp(-k * z))

print("=== RECALCULATING SCENARIO TASK DIFFICULTIES FROM SECTION 6 FORMULAS ===")

# Scenario 1: First over of innings (0.1)
# Inn 1, 0/0, Over 0.1, Par 165
# Form: T_B1
# Z_B1 = 0.50 * ((RAR - R_par)/R_par) + 0.30 * ((W_t - mu_W)/sigma_W) + 0.20 * (W_t / (11 - W_t))
# k_B1 = 1.2
# S_0 = 0, B_rem = 120, Par = 165, R_par = 165/20 = 8.25, RAR = 165 / (120/6) = 8.25
# W_t = 0. At L_t = 0: mu_W = 0. What is sigma_W? If regularized to 1.0 (or term is 0)
term1_s1 = 0.50 * (8.25 - 8.25) / 8.25 # 0.0
term2_s1 = 0.30 * 0.0 # 0.0
term3_s1 = 0.20 * (0.0 / 11.0) # 0.0
z_s1 = term1_s1 + term2_s1 + term3_s1
t_s1 = sigmoid(z_s1, k=1.2)
print(f"Scenario 1: Z = {z_s1:.4f}, T = {t_s1:.2f} (Reported: 50.0)")

# Scenario 2: Established batter in crisis
# Inn 2, Chasing 175, 110/5 at 15.0 ov. Needs 65 off 30 (RRR = 13.0). Batter 50*(35).
# Form: T_B2
# Z_B2 = 0.55 * ((RRR - 8.1)/3.0) + 0.25 * ((W_t - 3.5)/2.0) + 0.20 * ((RRR * W_t) / 25.0)
# k_B2 = 1.0
# RRR = 13.0, W_t = 5
term1_s2 = 0.55 * ((13.0 - 8.1) / 3.0) # 0.55 * 1.6333 = 0.8983
term2_s2 = 0.25 * ((5.0 - 3.5) / 2.0)   # 0.25 * 0.75 = 0.1875
term3_s2 = 0.20 * ((13.0 * 5.0) / 25.0) # 0.20 * 2.6 = 0.5200
z_s2 = term1_s2 + term2_s2 + term3_s2
t_s2 = sigmoid(z_s2, k=1.0)
print(f"Scenario 2: Z = {z_s2:.4f}, T = {t_s2:.2f} (Reported: 82.4)")

# Scenario 3: New batter entering in collapse
# Inn 1, 15/3 after 2.4 ov (L_t = 16), Par 170.
# Form: T_B1
# R_par = 170 / 20 = 8.5. S_t = 15, B_rem = 120 - 16 = 104 balls = 17.333 overs.
# RAR = (170 - 15) / (104 / 6) = 155 / 17.333 = 8.9423
# W_t = 3. At L_t = 16: empirical mu_W = 0.69, sigma_W = 0.80 (or formula mu_W = 0.89)
# Let's test with empirical mu_W = 0.69, sigma = 0.80:
term1_s3 = 0.50 * ((8.9423 - 8.5) / 8.5) # 0.50 * 0.0520 = 0.0260
term2_s3 = 0.30 * ((3.0 - 0.69) / 0.80)   # 0.30 * 2.8875 = 0.8663
term3_s3 = 0.20 * (3.0 / (11.0 - 3.0))    # 0.20 * (3/8) = 0.0750
z_s3 = term1_s3 + term2_s3 + term3_s3
t_s3 = sigmoid(z_s3, k=1.2)
print(f"Scenario 3 (empirical mu): Z = {z_s3:.4f}, T = {t_s3:.2f} (Reported: 86.5)")
# With formula mu = 0.89, sigma = 1.0:
term2_s3_form = 0.30 * ((3.0 - 0.89) / 1.0)
z_s3_form = term1_s3 + term2_s3_form + term3_s3
t_s3_form = sigmoid(z_s3_form, k=1.2)
print(f"Scenario 3 (formula mu): Z = {z_s3_form:.4f}, T = {t_s3_form:.2f}")

# Scenario 4: High-scoring 1st innings death
# Inn 1, 175/2 at 16.0 ov (L_t = 96), Par 180.
# R_par = 180 / 20 = 9.0. S_t = 175, B_rem = 24 balls = 4.0 overs.
# RAR = (180 - 175) / 4.0 = 5 / 4.0 = 1.25.
# W_t = 2. At L_t = 96: empirical mu_W = 4.55, sigma_W = 1.84 (formula mu = 6.49)
term1_s4 = 0.50 * ((1.25 - 9.0) / 9.0) # 0.50 * (-0.8611) = -0.4306
term2_s4 = 0.30 * ((2.0 - 4.55) / 1.84) # 0.30 * (-1.3859) = -0.4158
term3_s4 = 0.20 * (2.0 / (11.0 - 2.0))   # 0.20 * (2/9) = 0.0444
z_s4 = term1_s4 + term2_s4 + term3_s4
t_s4 = sigmoid(z_s4, k=1.2)
print(f"Scenario 4: Z = {z_s4:.4f}, T = {t_s4:.2f} (Reported: 38.2)")

# Scenario 5: Difficult chase, many overs left
# Inn 2, Chasing 190, 60/4 after 8.0 ov (L_t = 48). Needs 130 off 72 (RRR = 10.833).
# W_t = 4 (4 wickets lost!).
# Form: T_B2
term1_s5 = 0.55 * ((10.833 - 8.1) / 3.0) # 0.55 * 0.911 = 0.5011
term2_s5 = 0.25 * ((4.0 - 3.5) / 2.0)    # 0.25 * 0.25 = 0.0625
term3_s5 = 0.20 * ((10.833 * 4.0) / 25.0) # 0.20 * 1.7333 = 0.3467
z_s5 = term1_s5 + term2_s5 + term3_s5
t_s5 = sigmoid(z_s5, k=1.0)
print(f"Scenario 5: Z = {z_s5:.4f}, T = {t_s5:.2f} (Reported: 84.1)")

# Scenario 6: 12 runs required from 6 balls
# Inn 2, Chasing 180, 168/5 at 19.0 ov (L_t = 114). Needs 12 off 6 (RRR = 12.0). W_t = 5.
# Form: T_B2
term1_s6 = 0.55 * ((12.0 - 8.1) / 3.0) # 0.55 * 1.30 = 0.7150
term2_s6 = 0.25 * ((5.0 - 3.5) / 2.0)  # 0.25 * 0.75 = 0.1875
term3_s6 = 0.20 * ((12.0 * 5.0) / 25.0) # 0.20 * 2.40 = 0.4800
z_s6 = term1_s6 + term2_s6 + term3_s6
t_s6 = sigmoid(z_s6, k=1.0)
print(f"Scenario 6: Z = {z_s6:.4f}, T = {t_s6:.2f} (Reported: 74.5)")

# Scenario 7: 2 runs required from 30 balls
# Inn 2, Chasing 152, 150/2 at 15.0 ov (L_t = 90). Needs 2 off 30 (RRR = 0.40). W_t = 2.
# Form: T_B2
term1_s7 = 0.55 * ((0.40 - 8.1) / 3.0) # 0.55 * (-2.5667) = -1.4117
term2_s7 = 0.25 * ((2.0 - 3.5) / 2.0)  # 0.25 * (-0.75) = -0.1875
term3_s7 = 0.20 * ((0.40 * 2.0) / 25.0) # 0.20 * 0.032 = 0.0064
z_s7 = term1_s7 + term2_s7 + term3_s7
t_s7 = sigmoid(z_s7, k=1.0)
print(f"Scenario 7: Z = {z_s7:.4f}, T = {t_s7:.2f} (Reported: 2.1)")

# Scenario 8: Impossible chase (Blowout)
# Inn 2, Chasing 185, 105/8 at 18.0 ov (L_t = 108). Needs 80 off 12 (RRR = 40.0). W_t = 8.
# Form: T_B2
term1_s8 = 0.55 * ((40.0 - 8.1) / 3.0) # 0.55 * 10.633 = 5.8483
term2_s8 = 0.25 * ((8.0 - 3.5) / 2.0)  # 0.25 * 2.25 = 0.5625
term3_s8 = 0.20 * ((40.0 * 8.0) / 25.0) # 0.20 * 12.80 = 2.5600
z_s8 = term1_s8 + term2_s8 + term3_s8
t_s8 = sigmoid(z_s8, k=1.0)
print(f"Scenario 8: Z = {z_s8:.4f}, T = {t_s8:.2f} (Reported: 99.2)")

# Scenario 9: Defending small target
# Inn 2, Defending 125, opposition 45/3 at 7.0 ov (L_t = 42). Needs 81 off 78 (RRR = 6.23).
# Bowling Form: T_BO2
# Z_BO2 = 0.60 * ((8.1 - RRR) / 3.0) + 0.40 * ((10 - W_t - mu_Wrem) / sigma_W)
# k_BO2 = 1.0
# RRR = 6.23, W_t = 3 -> 10 - W_t = 7 wickets remaining for batting team.
# At L_t = 42, empirical mu_Wrem = 10 - 1.87 = 8.13, sigma_W = 1.27
term1_s9 = 0.60 * ((8.1 - 6.23) / 3.0) # 0.60 * 0.6233 = 0.3740
term2_s9 = 0.40 * ((7.0 - 8.13) / 1.27) # 0.40 * (-0.8898) = -0.3559
z_s9 = term1_s9 + term2_s9
t_s9 = sigmoid(z_s9, k=1.0)
print(f"Scenario 9: Z = {z_s9:.4f}, T = {t_s9:.2f} (Reported: 68.4)")

# Scenario 10: Bowler entering with 0 prior balls
# Over 16.0 (L_t = 96), defending 35 off 24 (RRR = 8.75). W_t = 3 (7 wkts in hand).
# Bowling Form: T_BO2
# At L_t = 96, empirical mu_Wrem = 10 - 4.55 = 5.45, sigma_W = 1.84
term1_s10 = 0.60 * ((8.1 - 8.75) / 3.0) # 0.60 * (-0.2167) = -0.1300
term2_s10 = 0.40 * ((7.0 - 5.45) / 1.84) # 0.40 * 0.8424 = 0.3370
z_s10 = term1_s10 + term2_s10
t_s10 = sigmoid(z_s10, k=1.0)
print(f"Scenario 10: Z = {z_s10:.4f}, T = {t_s10:.2f} (Reported: 78.0)")
