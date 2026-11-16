from src.dashboard.simulator import MatchPressureSimulator
sim = MatchPressureSimulator()

scenarios = [
    ('Over 0.0 (0/1)', 120, 0, 1),
    ('Over 6.0 (60/2)', 84, 60, 2),
    ('Over 12.0 (130/3)', 48, 130, 3),
    ('Over 16.0 (188/4)', 24, 188, 4),
    ('Over 18.0 (220/5)', 12, 220, 5),
    ('Over 19.0 (236/5)', 6, 236, 5),
    ('Over 19.0 (230/7)', 6, 230, 7)
]

print(f"{'Scenario':<20} | {'Score':<8} | {'RRR':<6} | {'WP%':<6} | {'T_B':<6} | {'L_norm':<7} | {'P_bat':<6} | Band")
print("-" * 90)
for name, brem, sc, wt in scenarios:
    r = sim.simulate(2, brem, sc, wt, target=248)
    print(f"{name:<20} | {sc}/{wt:<6} | {r['rrr']:<6.1f} | {r['wp_batting']*100:<6.1f} | {r['task_difficulty_bat']:6.1f} | {r['normalized_consequence_L']:7.1f} | {r['pressure_batting']:6.1f} | {r['pressure_band_batting']}")
