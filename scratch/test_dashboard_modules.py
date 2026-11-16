import os
import pandas as pd
from src.dashboard.data_loader import load_official_top10, load_full_metrics
from src.dashboard.plots import (
    create_top10_bar,
    create_pressure_lift_chart,
    create_lift_waterfall,
    create_pressure_distribution_pie,
    create_phase_bar,
    create_player_radar,
    create_gauge
)

print("1. Testing data loading...")
bat_top10 = load_official_top10('batting')
bowl_top10 = load_official_top10('bowling')
bat_metrics = load_full_metrics('batting')
bowl_metrics = load_full_metrics('bowling')
print(f"Loaded {len(bat_top10)} bat top10, {len(bowl_top10)} bowl top10, {len(bat_metrics)} bat metrics, {len(bowl_metrics)} bowl metrics.")

print("2. Testing create_top10_bar (Batting & Bowling)...")
fig_bat = create_top10_bar(bat_top10, 'batting')
fig_bowl = create_top10_bar(bowl_top10, 'bowling')
print("Top 10 bar charts created successfully!")

print("3. Testing create_pressure_lift_chart & waterfall...")
fig_lift = create_pressure_lift_chart(bat_metrics, 'batting')
fig_wf = create_lift_waterfall(bat_metrics, 'batting')
print("Lift charts created successfully!")

print("4. Testing player deep-dive charts (pie, phase, radar)...")
row1 = bat_metrics.iloc[0]
row2 = bat_metrics.iloc[1]
fig_pie = create_pressure_distribution_pie(row1)
fig_phase = create_phase_bar(row1)
fig_radar = create_player_radar(row1, row2, 'batting')
print("Deep dive charts created successfully!")

print("5. Testing gauge chart...")
fig_g1 = create_gauge(79.7, "Batting Pressure (P_bat)")
fig_g2 = create_gauge(63.6, "Bowling Pressure (P_bowl)", color="#F59E0B")
print("Gauge charts created successfully!")

print("ALL DASHBOARD MODULE TESTS PASSED WITH 100% SUCCESS!")
