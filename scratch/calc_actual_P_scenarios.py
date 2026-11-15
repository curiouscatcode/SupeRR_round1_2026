import numpy as np

# Real calculated T and L_norm:
scenarios_real = {
    1: {'name': 'First over of innings (0.1)', 'T': 50.00, 'L': 99.24, 'rep_P': 47.5},
    2: {'name': 'Established batter in crisis', 'T': 83.28, 'L': 21.08, 'rep_P': 80.2},
    3: {'name': 'New batter in collapse', 'T': 76.15, 'L': 37.73, 'rep_P': 81.2},
    4: {'name': 'High-scoring 1st inn death', 'T': 27.64, 'L': 29.88, 'rep_P': 44.6},
    5: {'name': 'Difficult chase, 12 ov left', 'T': 71.30, 'L': 6.26, 'rep_P': 73.6},
    6: {'name': '12 off 6 balls', 'T': 79.94, 'L': 100.00, 'rep_P': 85.7},
    7: {'name': '2 off 30 balls', 'T': 16.90, 'L': 0.22, 'rep_P': 3.2},
    8: {'name': 'Blowout chase (80 off 12)', 'T': 99.99, 'L': 0.00, 'rep_P': 8.9},
    9: {'name': 'Defending small target', 'T': 50.45, 'L': 14.77, 'rep_P': 71.2},
    10: {'name': 'Bowler 1st over at ov 17', 'T': 55.16, 'L': 24.15, 'rep_P': 80.9}
}

print("=== ACTUAL COMBINED PRESSURE RECALCULATION ===")
for s, d in scenarios_real.items():
    actual_P = np.sqrt(d['T'] * d['L'])
    print(f"Scenario {s:2d}: Actual T = {d['T']:5.2f}, Actual L = {d['L']:6.2f} -> Actual P = {actual_P:5.2f} (Reported P: {d['rep_P']:4.1f}, Diff: {actual_P - d['rep_P']:+5.2f})")
