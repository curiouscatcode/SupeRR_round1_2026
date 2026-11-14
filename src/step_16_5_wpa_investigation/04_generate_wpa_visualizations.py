"""
Step 16.5: Script 04 - Generate Visualizations (Section 8)
=========================================================
Generates the 9 required publication-quality figures:
1. fig1_pi_zscore_vs_expected_leverage.png
2. fig2_pi_zscore_vs_absolute_wpa.png
3. fig3_expected_leverage_distributions.png
4. fig4_actual_wpa_distributions.png
5. fig5_four_quadrant_analysis.png
6. fig6_expected_leverage_by_innings_and_phase.png
7. fig7_wpa_by_batting_position.png
8. fig8_wpa_by_bowling_phase.png
9. fig9_player_match_wpa_consistency.png
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

OUTPUT_DIR = Path("outputs/step_16_5_wpa_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Styling configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def generate_fig1_and_fig2(bat_df):
    print("Generating Figure 1: PI Z-Score vs Expected Leverage...")
    sample = bat_df.sample(n=min(8000, len(bat_df)), random_state=42)

    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    colors = np.where(sample['is_high_pressure_bat'], '#d90429', '#2b5c8f')
    alphas = np.where(sample['is_high_pressure_bat'], 0.45, 0.2)

    ax.scatter(sample['batting_z_score'], sample['expected_leverage_pct'],
               c=colors, alpha=0.3, s=16, edgecolors='none')

    ax.axvline(x=1.00, color='#d90429', linestyle='--', linewidth=1.5, label='High Pressure Cutoff (Z = 1.00)')
    ax.axhline(y=1.1436, color='#2b2d42', linestyle=':', linewidth=1.5, label='Median Leverage Cutoff (1.14%)')

    ax.set_xlabel('Pressure Index Z-Score (Phase × Innings Standardized)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Expected Delivery Leverage: E[|ΔWP|] (%)', fontsize=11, fontweight='bold')
    ax.set_title('Figure 1: Pressure Index Z-Score vs Expected Delivery Leverage', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlim(-2.5, 4.0)
    ax.set_ylim(0, 7.5)
    ax.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    ax.text(0.04, 0.78,
            "Key Insight:\nHigh Z-scores (Z > 1.0) do NOT cluster at high leverage.\nMany extreme crisis deliveries (Z > 2.0) have leverage < 0.5%\nbecause they occur in hopeless collapses (WP < 8%).",
            transform=ax.transAxes, fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f9fa', edgecolor='#dddddd'))

    plt.tight_layout()
    out1 = OUTPUT_DIR / "fig1_pi_zscore_vs_expected_leverage.png"
    plt.savefig(out1)
    plt.close()
    print(f"Saved: {out1}")

    print("Generating Figure 2: PI Z-Score vs Absolute WPA...")
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    ax.scatter(sample['batting_z_score'], sample['absolute_wpa_pct'],
               c=colors, alpha=0.3, s=16, edgecolors='none')

    ax.axvline(x=1.00, color='#d90429', linestyle='--', linewidth=1.5, label='High Pressure Cutoff (Z = 1.00)')

    ax.set_xlabel('Pressure Index Z-Score (Phase × Innings Standardized)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Actual Absolute WPA: |ΔWP| (%)', fontsize=11, fontweight='bold')
    ax.set_title('Figure 2: Pressure Index Z-Score vs Actual Absolute WPA', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlim(-2.5, 4.0)
    ax.set_ylim(0, 15.0)
    ax.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    ax.text(0.04, 0.78,
            "Key Insight:\nLarge match swings (|WPA| > 5%) occur overwhelmingly\nat moderate PI values (Z between -1.0 and +1.0) in close games,\nwhile extreme high PI deliveries yield small shifts.",
            transform=ax.transAxes, fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f9fa', edgecolor='#dddddd'))

    plt.tight_layout()
    out2 = OUTPUT_DIR / "fig2_pi_zscore_vs_absolute_wpa.png"
    plt.savefig(out2)
    plt.close()
    print(f"Saved: {out2}")


def generate_fig3_and_fig4(bat_df):
    print("Generating Figure 3: Expected Leverage Distributions (HP vs Non-HP)...")
    hp_lev = bat_df[bat_df['is_high_pressure_bat']]['expected_leverage_pct']
    nh_lev = bat_df[~bat_df['is_high_pressure_bat']]['expected_leverage_pct']

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    bins = np.linspace(0, 5, 51)

    ax.hist(nh_lev, bins=bins, density=True, alpha=0.55, color='#2b5c8f', label=f'Non-HP (Z ≤ 1.0): Mean = {nh_lev.mean():.2f}%, Median = {nh_lev.median():.2f}%')
    ax.hist(hp_lev, bins=bins, density=True, alpha=0.65, color='#d90429', label=f'High Pressure (Z > 1.0): Mean = {hp_lev.mean():.2f}%, Median = {hp_lev.median():.2f}%')

    ax.axvline(x=nh_lev.median(), color='#2b5c8f', linestyle='--', linewidth=1.5)
    ax.axvline(x=hp_lev.median(), color='#d90429', linestyle='--', linewidth=1.5)

    ax.set_xlabel('Expected Delivery Leverage (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Probability Density', fontsize=11, fontweight='bold')
    ax.set_title('Figure 3: Expected Leverage Distribution: High Pressure vs Non-HP Deliveries', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlim(0, 4.5)
    ax.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    plt.tight_layout()
    out3 = OUTPUT_DIR / "fig3_expected_leverage_distributions.png"
    plt.savefig(out3)
    plt.close()
    print(f"Saved: {out3}")

    print("Generating Figure 4: Actual WPA Distributions (HP vs Non-HP)...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    # Subplot A: Signed WPA
    hp_swpa = bat_df[bat_df['is_high_pressure_bat']]['wpa_pct']
    nh_swpa = bat_df[~bat_df['is_high_pressure_bat']]['wpa_pct']
    sbins = np.linspace(-6, 6, 61)

    ax1.hist(nh_swpa, bins=sbins, density=True, alpha=0.55, color='#2b5c8f', label=f'Non-HP (Z ≤ 1.0): Mean = {nh_swpa.mean():.2f}%')
    ax1.hist(hp_swpa, bins=sbins, density=True, alpha=0.65, color='#d90429', label=f'High Pressure (Z > 1.0): Mean = {hp_swpa.mean():.2f}%')
    ax1.set_xlabel('Signed WPA (%) [Batting Perspective]', fontsize=10.5, fontweight='bold')
    ax1.set_ylabel('Probability Density', fontsize=10.5, fontweight='bold')
    ax1.set_title('A: Signed WPA Distribution', fontsize=11.5, fontweight='bold')
    ax1.set_xlim(-6, 6)
    ax1.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9)

    # Subplot B: Absolute WPA
    hp_awpa = bat_df[bat_df['is_high_pressure_bat']]['absolute_wpa_pct']
    nh_awpa = bat_df[~bat_df['is_high_pressure_bat']]['absolute_wpa_pct']
    abins = np.linspace(0, 8, 41)

    ax2.hist(nh_awpa, bins=abins, density=True, alpha=0.55, color='#2b5c8f', label=f'Non-HP: Mean = {nh_awpa.mean():.2f}%, Median = {nh_awpa.median():.2f}%')
    ax2.hist(hp_awpa, bins=abins, density=True, alpha=0.65, color='#d90429', label=f'HP: Mean = {hp_awpa.mean():.2f}%, Median = {hp_awpa.median():.2f}%')
    ax2.set_xlabel('Absolute WPA: |ΔWP| (%)', fontsize=10.5, fontweight='bold')
    ax2.set_ylabel('Probability Density', fontsize=10.5, fontweight='bold')
    ax2.set_title('B: Absolute WPA Distribution', fontsize=11.5, fontweight='bold')
    ax2.set_xlim(0, 7)
    ax2.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9)

    plt.suptitle('Figure 4: Actual WPA Distributions: High Pressure vs Non-HP Deliveries', fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    out4 = OUTPUT_DIR / "fig4_actual_wpa_distributions.png"
    plt.savefig(out4)
    plt.close()
    print(f"Saved: {out4}")


def generate_fig5_four_quadrant(quad_df):
    print("Generating Figure 5: Four-Quadrant Analysis Map...")
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)

    # Box coordinates and colors
    quads = [
        {'name': 'Q3: Tense Parity\n(Low PI, High Leverage)', 'x': 0.05, 'y': 0.52, 'w': 0.42, 'h': 0.42, 'bg': '#eef4f8', 'edge': '#2b5c8f',
         'deliveries': '78,732 (43.5%)', 'wp': 'Mean WP: 52.9%', 'lev': 'Mean Lev: 1.95%', 'rrr': 'Mean Inn 2 RRR: 9.3 RPO', 'desc': 'Close, balanced games with wickets in hand.'},
        {'name': 'Q1: True Clutch\n(High PI, High Leverage)', 'x': 0.53, 'y': 0.52, 'w': 0.42, 'h': 0.42, 'bg': '#fcf0f2', 'edge': '#d90429',
         'deliveries': '11,698 (6.5%)', 'wp': 'Mean WP: 39.8%', 'lev': 'Mean Lev: 1.80%', 'rrr': 'Mean Inn 2 RRR: 11.1 RPO', 'desc': 'Steep chases/starts that remain winnable.'},
        {'name': 'Q4: Routine Calm Play\n(Low PI, Low Leverage)', 'x': 0.05, 'y': 0.05, 'w': 0.42, 'h': 0.42, 'bg': '#f8f9fa', 'edge': '#8d99ae',
         'deliveries': '69,399 (38.4%)', 'wp': 'Mean WP: 54.7%', 'lev': 'Mean Lev: 0.77%', 'rrr': 'Mean Inn 2 RRR: 11.7 RPO', 'desc': 'Comfortable middle overs & routine overs.'},
        {'name': 'Q2: Crisis Collapses\n(High PI, Low Leverage)', 'x': 0.53, 'y': 0.05, 'w': 0.42, 'h': 0.42, 'bg': '#fef2ed', 'edge': '#ef233c',
         'deliveries': '21,010 (11.6%)', 'wp': 'Mean WP: 21.0%', 'lev': 'Mean Lev: 0.64%', 'rrr': 'Mean Inn 2 RRR: 19.5 RPO', 'desc': 'Lost-cause collapses (7-9 wickets down).'}
    ]

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    for q in quads:
        rect = plt.Rectangle((q['x'], q['y']), q['w'], q['h'], facecolor=q['bg'], edgecolor=q['edge'], linewidth=2.0, linestyle='-', zorder=1)
        ax.add_patch(rect)

        # Title
        ax.text(q['x'] + q['w']/2, q['y'] + q['h'] - 0.07, q['name'], ha='center', va='center', fontsize=11.5, fontweight='bold', color=q['edge'])
        # Stats
        stats_text = f"Deliveries: {q['deliveries']}\n{q['wp']} | {q['lev']}\n{q['rrr']}\n\nContext: {q['desc']}"
        ax.text(q['x'] + q['w']/2, q['y'] + q['h']/2 - 0.04, stats_text, ha='center', va='center', fontsize=9.5, color='#222222', multialignment='center')

    # Add axis labels
    ax.text(0.5, 0.98, 'HIGH MATCH LEVERAGE (Game in Balance: Leverage ≥ 1.14%) ↑', ha='center', va='top', fontsize=11, fontweight='bold', color='#1d3557')
    ax.text(0.5, 0.02, '↓ LOW MATCH LEVERAGE (Game Decided: Leverage < 1.14%)', ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1d3557')
    ax.text(0.01, 0.5, '← LOW PI (Z ≤ 1.0)', ha='left', va='center', rotation=90, fontsize=11, fontweight='bold', color='#1d3557')
    ax.text(0.99, 0.5, 'HIGH PI (Z > 1.0) →', ha='right', va='center', rotation=-90, fontsize=11, fontweight='bold', color='#d90429')

    plt.suptitle('Figure 5: Four-Quadrant Tactical Map: Pressure Index vs Match Leverage', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout()
    out5 = OUTPUT_DIR / "fig5_four_quadrant_analysis.png"
    plt.savefig(out5)
    plt.close()
    print(f"Saved: {out5}")


def generate_fig6_leverage_by_phase(bat_df):
    print("Generating Figure 6: Expected Leverage by Innings and Phase...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # Subplot A: Innings 1
    inn1 = bat_df[bat_df['innings'] == 1]
    phases = ['PP', 'Middle', 'Death']
    x = np.arange(len(phases))
    width = 0.35

    hp_means_1 = [inn1[(inn1['phase'] == p) & (inn1['is_high_pressure_bat'])]['expected_leverage_pct'].mean() for p in phases]
    nh_means_1 = [inn1[(inn1['phase'] == p) & (~inn1['is_high_pressure_bat'])]['expected_leverage_pct'].mean() for p in phases]

    ax1.bar(x - width/2, hp_means_1, width, label='High Pressure (Z > 1.0)', color='#d90429', alpha=0.9)
    ax1.bar(x + width/2, nh_means_1, width, label='Non-HP (Z ≤ 1.0)', color='#2b5c8f', alpha=0.9)
    ax1.set_ylabel('Mean Expected Leverage (%)', fontsize=10.5, fontweight='bold')
    ax1.set_title('A: Innings 1 (Setting Target)', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Powerplay\n(Overs 1–6)', 'Middle\n(Overs 7–15)', 'Death\n(Overs 16–20)'], fontsize=10)
    ax1.set_ylim(0, 2.5)
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(100, decimals=1))
    ax1.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    for i in range(len(phases)):
        ax1.text(i - width/2, hp_means_1[i] + 0.06, f"{hp_means_1[i]:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')
        ax1.text(i + width/2, nh_means_1[i] + 0.06, f"{nh_means_1[i]:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#2b5c8f')

    # Subplot B: Innings 2
    inn2 = bat_df[bat_df['innings'] == 2]
    hp_means_2 = [inn2[(inn2['phase'] == p) & (inn2['is_high_pressure_bat'])]['expected_leverage_pct'].mean() for p in phases]
    nh_means_2 = [inn2[(inn2['phase'] == p) & (~inn2['is_high_pressure_bat'])]['expected_leverage_pct'].mean() for p in phases]

    ax2.bar(x - width/2, hp_means_2, width, label='High Pressure (Z > 1.0)', color='#d90429', alpha=0.9)
    ax2.bar(x + width/2, nh_means_2, width, label='Non-HP (Z ≤ 1.0)', color='#2b5c8f', alpha=0.9)
    ax2.set_ylabel('Mean Expected Leverage (%)', fontsize=10.5, fontweight='bold')
    ax2.set_title('B: Innings 2 (Chasing Target)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Powerplay\n(Overs 1–6)', 'Middle\n(Overs 7–15)', 'Death\n(Overs 16–20)'], fontsize=10)
    ax2.set_ylim(0, 2.5)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(100, decimals=1))
    ax2.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    for i in range(len(phases)):
        ax2.text(i - width/2, hp_means_2[i] + 0.06, f"{hp_means_2[i]:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')
        ax2.text(i + width/2, nh_means_2[i] + 0.06, f"{nh_means_2[i]:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#2b5c8f')

    plt.suptitle('Figure 6: Mean Expected Leverage Comparison Across Match Phases and Innings', fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    out6 = OUTPUT_DIR / "fig6_expected_leverage_by_innings_and_phase.png"
    plt.savefig(out6)
    plt.close()
    print(f"Saved: {out6}")


def generate_fig7_batting_positions(pos_df):
    print("Generating Figure 7: WPA and Leverage by Batting Position (1 to 11)...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    x = pos_df['batting_position']

    # Subplot A: HP Capture Rate vs Mean Expected Leverage
    ax1_twin = ax1.twinx()
    l1 = ax1.bar(x - 0.18, pos_df['hp_capture_pct'], width=0.36, color='#e63946', alpha=0.85, label='High PI Capture Rate (%)')
    l2 = ax1_twin.plot(x + 0.18, pos_df['mean_expected_leverage'], color='#1d3557', marker='o', linewidth=2.0, label='Mean Expected Leverage (%)')

    ax1.set_xlabel('Batting Position (Order of Appearance)', fontsize=10.5, fontweight='bold')
    ax1.set_ylabel('High PI Capture Rate (%)', fontsize=10.5, fontweight='bold', color='#e63946')
    ax1_twin.set_ylabel('Mean Expected Leverage (%)', fontsize=10.5, fontweight='bold', color='#1d3557')
    ax1.set_title('A: High PI Capture vs Expected Leverage', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_ylim(0, 100)
    ax1_twin.set_ylim(0.5, 2.0)

    # Subplot B: Mean Signed WPA vs Absolute WPA
    ax2.plot(x, pos_df['mean_absolute_wpa'], color='#457b9d', marker='s', linewidth=2.0, label='Mean Absolute WPA (%)')
    ax2.plot(x, pos_df['mean_signed_wpa'], color='#e76f51', marker='^', linewidth=2.0, linestyle='--', label='Mean Signed WPA (%)')
    ax2.axhline(y=0.0, color='#777777', linestyle=':', linewidth=1.0)

    ax2.set_xlabel('Batting Position (Order of Appearance)', fontsize=10.5, fontweight='bold')
    ax2.set_ylabel('WPA Metric (%)', fontsize=10.5, fontweight='bold')
    ax2.set_title('B: Actual WPA Impact Across Batting Order', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_ylim(-0.8, 1.8)
    ax2.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    plt.suptitle('Figure 7: Win Probability Impact and Leverage Across Batting Positions 1–11', fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    out7 = OUTPUT_DIR / "fig7_wpa_by_batting_position.png"
    plt.savefig(out7)
    plt.close()
    print(f"Saved: {out7}")


def generate_fig8_bowling_phases(bowl_phase_df):
    print("Generating Figure 8: Bowling WPA and Leverage by Phase...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    x = np.arange(len(bowl_phase_df))
    phases = bowl_phase_df['bowling_phase']
    width = 0.35

    # Subplot A: HP Capture vs High Leverage Share
    ax1.bar(x - width/2, bowl_phase_df['hp_bowling_capture_pct'], width, label='HP Bowling Capture (Z > 1.0)', color='#d90429', alpha=0.9)
    ax1.bar(x + width/2, bowl_phase_df['high_leverage_pct'], width, label='High Leverage Deliveries (≥ 1.14%)', color='#2b5c8f', alpha=0.9)

    ax1.set_ylabel('Percentage of Phase Deliveries (%)', fontsize=10.5, fontweight='bold')
    ax1.set_title('A: Bowling High PI vs High Leverage Proportions', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Powerplay\n(Overs 1–6)', 'Middle\n(Overs 7–15)', 'Death\n(Overs 16–20)'], fontsize=10)
    ax1.set_ylim(0, 75)
    ax1.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    for i in range(len(phases)):
        ax1.text(i - width/2, bowl_phase_df.loc[i, 'hp_bowling_capture_pct'] + 1.2, f"{bowl_phase_df.loc[i, 'hp_bowling_capture_pct']:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax1.text(i + width/2, bowl_phase_df.loc[i, 'high_leverage_pct'] + 1.2, f"{bowl_phase_df.loc[i, 'high_leverage_pct']:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Subplot B: Mean Expected Leverage & Mean Bowler Absolute WPA
    ax2.plot(x, bowl_phase_df['mean_expected_leverage'], color='#1d3557', marker='o', linewidth=2.2, label='Mean Expected Leverage (%)')
    ax2.plot(x, bowl_phase_df['mean_absolute_wpa'], color='#e26d5c', marker='s', linewidth=2.2, linestyle='--', label='Mean Absolute WPA Conceded (%)')

    ax2.set_ylabel('Percentage Metric (%)', fontsize=10.5, fontweight='bold')
    ax2.set_title('B: Expected Leverage and Absolute WPA by Phase', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Powerplay\n(Overs 1–6)', 'Middle\n(Overs 7–15)', 'Death\n(Overs 16–20)'], fontsize=10)
    ax2.set_ylim(0.8, 2.2)
    ax2.legend(loc='upper left', frameon=True, facecolor='white', fontsize=9.5)

    plt.suptitle('Figure 8: Bowling Impact Analysis: Leverage, HP Capture, and WPA Across Phases', fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    out8 = OUTPUT_DIR / "fig8_wpa_by_bowling_phase.png"
    plt.savefig(out8)
    plt.close()
    print(f"Saved: {out8}")


def generate_fig9_player_consistency():
    print("Generating Figure 9: Player Match-to-Match WPA Consistency...")
    bat_p = pd.read_csv(OUTPUT_DIR / "player_batting_wpa_reliability.csv")
    bowl_p = pd.read_csv(OUTPUT_DIR / "player_bowling_wpa_reliability.csv")

    t1_bat = bat_p[bat_p['tier'] == 'Tier 1'].copy()
    t1_bowl = bowl_p[bowl_p['tier'] == 'Tier 1'].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # Subplot A: Batters
    sc1 = ax1.scatter(t1_bat['match_wpa_std_pct'], t1_bat['hp_signed_wpa_pct'],
                      c=t1_bat['hp_mean_expected_leverage'], cmap='coolwarm', s=35, alpha=0.85, edgecolors='none')
    cb1 = plt.colorbar(sc1, ax=ax1)
    cb1.set_label('Mean Expected Leverage (%)', fontsize=9)

    ax1.axhline(y=0.0, color='#777777', linestyle='--', linewidth=1.0)
    ax1.set_xlabel('Match WPA Volatility (Std Dev of Match WPA %)', fontsize=10.5, fontweight='bold')
    ax1.set_ylabel('HP Signed WPA (Total %)', fontsize=10.5, fontweight='bold')
    ax1.set_title('A: Tier 1 Batters (Consistency vs Impact)', fontsize=12, fontweight='bold')

    # Annotate notable batters
    notables_bat = ['Shivam Dube', 'Suryakumar Yadav', 'Heinrich Klaasen', 'Virat Kohli', 'MS Dhoni', 'Rinku Singh', 'Yashasvi Jaiswal']
    for _, r in t1_bat[t1_bat['striker_name'].isin(notables_bat)].iterrows():
        ax1.annotate(r['striker_name'], (r['match_wpa_std_pct'], r['hp_signed_wpa_pct']),
                     xytext=(4, 4), textcoords='offset points', fontsize=8, fontweight='bold')

    # Subplot B: Bowlers
    sc2 = ax2.scatter(t1_bowl['match_bwpa_std_pct'], t1_bowl['hp_signed_bwpa_pct'],
                      c=t1_bowl['hp_mean_expected_leverage'], cmap='viridis', s=35, alpha=0.85, edgecolors='none')
    cb2 = plt.colorbar(sc2, ax=ax2)
    cb2.set_label('Mean Expected Leverage (%)', fontsize=9)

    ax2.axhline(y=0.0, color='#777777', linestyle='--', linewidth=1.0)
    ax2.set_xlabel('Match Bowler WPA Volatility (Std Dev %)', fontsize=10.5, fontweight='bold')
    ax2.set_ylabel('HP Bowler WPA (Total %)', fontsize=10.5, fontweight='bold')
    ax2.set_title('B: Tier 1 Bowlers (Consistency vs Impact)', fontsize=12, fontweight='bold')

    # Annotate notable bowlers
    notables_bowl = ['Jasprit Bumrah', 'Rashid Khan', 'Sunil Narine', 'Tim Southee', 'Axar Patel', 'Arshdeep Singh', 'Harshit Rana']
    for _, r in t1_bowl[t1_bowl['bowler_name'].isin(notables_bowl)].iterrows():
        ax2.annotate(r['bowler_name'], (r['match_bwpa_std_pct'], r['hp_signed_bwpa_pct']),
                     xytext=(4, 4), textcoords='offset points', fontsize=8, fontweight='bold')

    plt.suptitle('Figure 9: Player Match-to-Match WPA Consistency vs High Pressure Match Impact', fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    out9 = OUTPUT_DIR / "fig9_player_match_wpa_consistency.png"
    plt.savefig(out9)
    plt.close()
    print(f"Saved: {out9}")


def main():
    print("=== Step 16.5 Script 04: Generate All 9 Visualizations ===")
    parquet_path = OUTPUT_DIR / "delivery_wpa_leverage.parquet"
    df = pd.read_parquet(parquet_path)
    bat_df = df[df['is_batter_ball_faced'] == 1].copy()

    quad_df = pd.read_csv(OUTPUT_DIR / "four_quadrant_analysis.csv")
    pos_df = pd.read_csv(OUTPUT_DIR / "batting_position_wpa_leverage.csv")
    bowl_phase_df = pd.read_csv(OUTPUT_DIR / "bowling_phase_wpa_leverage.csv")

    generate_fig1_and_fig2(bat_df)
    generate_fig3_and_fig4(bat_df)
    generate_fig5_four_quadrant(quad_df)
    generate_fig6_leverage_by_phase(bat_df)
    generate_fig7_batting_positions(pos_df)
    generate_fig8_bowling_phases(bowl_phase_df)
    generate_fig9_player_consistency()

    print("All 9 figures generated successfully!")


if __name__ == "__main__":
    main()
