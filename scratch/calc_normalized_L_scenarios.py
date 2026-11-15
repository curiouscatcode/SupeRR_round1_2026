import numpy as np

l1_min = 0.00283
l1_max = 0.02003
l2_min = 0.00002
l2_max = 0.12201

# Raw L from actual models:
raw_L = {
    1: 0.01990, # S1: Inn 1, 0/0, Over 0.1
    2: 0.02574, # S2: Inn 2, Chasing 175, 110/5 at 15.0 ov (Req=65, B_rem=30)
    3: 0.00932, # S3: Inn 1, 15/3 after 2.4 ov
    4: 0.00797, # S4: Inn 1, 175/2 at 16.0 ov
    5: 0.00766, # S5: Inn 2, Chasing 190, 60/4 at 8.0 ov
    6: 0.21119, # S6: Inn 2, Chasing 180, 168/5 at 19.0 ov (12 off 6)
    7: 0.00029, # S7: Inn 2, Chasing 152, 150/2 at 15.0 ov (2 off 30)
    8: 0.00002, # S8: Inn 2, Chasing 185, 105/8 at 18.0 ov (80 off 12)
    9: 0.01804, # S9: Inn 2, Defending 125, 45/3 at 7.0 ov
    10: 0.02948 # S10: Inn 2, Defending 35 off 24 at 16.0 ov
}

inn_map = {1:1, 2:2, 3:1, 4:1, 5:2, 6:2, 7:2, 8:2, 9:2, 10:2}

print("=== EXACT L_norm CALCULATION FOR 10 SCENARIOS ===")
for s in range(1, 11):
    raw = raw_L[s]
    inn = inn_map[s]
    if inn == 1:
        norm = np.clip((raw - l1_min) / (l1_max - l1_min) * 100.0, 0.0, 100.0)
    else:
        norm = np.clip((raw - l2_min) / (l2_max - l2_min) * 100.0, 0.0, 100.0)
    print(f"Scenario {s:2d} (Inn {inn}): Raw L = {raw:.5f} -> L_norm = {norm:6.2f}")
