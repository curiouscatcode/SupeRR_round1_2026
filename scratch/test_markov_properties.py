import sys
sys.path.append('.')
import importlib
import numpy as np
import pandas as pd

mod3 = importlib.import_module('src.step_4_pressure_pipeline.03_win_probability_models')
wp = mod3.WinProbabilityFramework(load_saved=True)

print("=== AUDIT G: FINAL-BALL MARKOV ENGINE VERIFICATION ===")

# 1. Monotonicity across runs required (R_t from 1 to 12) for fixed W_t = 4
print("\n--- Monotonicity Across Runs Required (W_t = 4, B_rem = 1) ---")
prev_p = 1.1
monotonic_runs = True
for req in range(1, 13):
    p = wp.predict_wp_final_markov(req, 4, 'Death')
    is_mono = (p <= prev_p + 1e-9)
    if not is_mono:
        monotonic_runs = False
    print(f"Req = {req:2d} off 1 ball | WP = {p:.5f} | Monotonic: {is_mono}")
    prev_p = p

print(f"Runs monotonicity verdict: {'PASS' if monotonic_runs else 'FAIL'}")

# 2. Monotonicity across wickets lost (W_t from 0 to 10) for fixed runs required
print("\n--- Monotonicity Across Wickets Lost (Req = 4 off 1 ball) ---")
prev_p = 1.1
monotonic_wkts = True
for wt in range(0, 11):
    p = wp.predict_wp_final_markov(4, wt, 'Death')
    is_mono = (p <= prev_p + 1e-9)
    if not is_mono:
        monotonic_wkts = False
    print(f"Wkts Lost = {wt:2d} (in hand: {10-wt:2d}) | WP = {p:.5f} | Monotonic: {is_mono}")
    prev_p = p

print(f"Wickets monotonicity verdict: {'PASS' if monotonic_wkts else 'FAIL'}")

# 3. Check terminal absorbing properties
print("\n--- Terminal Absorbing Properties ---")
print("R_t <= 0 (Req 0):", wp.predict_wp_final_markov(0, 5, 'Death'), "Expected: 1.0")
print("R_t <= 0 (Req -1):", wp.predict_wp_final_markov(-1, 5, 'Death'), "Expected: 1.0")
print("W_t >= 10 (W_t 10):", wp.predict_wp_final_markov(4, 10, 'Death'), "Expected: 0.0")
print("W_t >= 10 (W_t 11):", wp.predict_wp_final_markov(4, 11, 'Death'), "Expected: 0.0")

# 4. Check all 256 B_rem = 1 deliveries in the actual dataset
df = pd.read_parquet('outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet')
final_deliveries = df[(df['innings'] == 2) & (df['balls_remaining'] == 1)]
print(f"\nTotal B_rem = 1 deliveries in cohort: {len(final_deliveries)}")
print("Pre-delivery WP summary:")
print(final_deliveries['pre_delivery_wp'].describe())
print("NaN count:", final_deliveries['pre_delivery_wp'].isna().sum())
print("Min WP:", final_deliveries['pre_delivery_wp'].min())
print("Max WP:", final_deliveries['pre_delivery_wp'].max())
print("Any inverted (WP < 0 or WP > 1):", ((final_deliveries['pre_delivery_wp'] < 0) | (final_deliveries['pre_delivery_wp'] > 1)).any())
