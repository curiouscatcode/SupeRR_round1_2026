"""
Step 16.7: Script 05 - Generate Diagnostic Visualizations
=========================================================
Generates four high-resolution publication figures for Step 16.7:

1. fig1_balls_faced_decay_curves.png:
   - Mathematical decay profile of Situational Intensity across balls faced (0-35).
   - Contrasts the 10-ball linear cliff in Control with the smooth exponential decay of Cand 1.
2. fig2_hp_capture_by_position.png:
   - HP capture rates across Batting Orders 1 to 11 for all candidates.
3. fig3_archetypal_scenarios_comparison.png:
   - Comparative performance across key cricket scenarios (Set Batters in Crisis, 1st Inn PP Collapse, Blowouts).
4. fig4_player_ranking_stability_scatter.png:
   - Scatter plots of Control BRS3 vs Candidates 1, 2, and 4, highlighting Pat Cummins, Nicholas Pooran, and Heinrich Klaasen.
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs/step_16_7_situational_intensity_redesign")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def set_plot_style():
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['figure.titlesize'] = 14
    plt.rcParams['figure.titleweight'] = 'bold'


def plot_decay_curves():
    bf = np.linspace(0, 35, 200)
    # Control: Linear cliff
    i_ctrl = np.clip(((10.0 - bf) / 10.0) * 100.0, 0.0, 100.0)
    # Candidate 1: Smooth Exponential with Floor
    i_cand1 = 25.0 + 75.0 * np.exp(-bf / 10.0)

    # Load actual mean I from dataset
    bf_csv = OUTPUT_DIR / "balls_faced_decay_profile.csv"
    df_bf = pd.read_csv(bf_csv)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.5), dpi=300)

    # 1. Theoretical Curves
    ax1.plot(bf, i_ctrl, label='Control (10-Ball Linear Cliff)', color='#d62728', lw=2.5)
    ax1.plot(bf, i_cand1, label='Candidate 1 (Smooth Exponential Decay with Floor)', color='#1f77b4', lw=2.5)
    ax1.axvline(10.0, color='black', linestyle='--', alpha=0.6, label='Control Cliff Boundary (bf = 10)')
    ax1.axhline(25.0, color='#1f77b4', linestyle=':', alpha=0.7, label='Cand 1 Asymptotic Floor (25 pts)')
    ax1.fill_between(bf, 0, i_ctrl, color='#d62728', alpha=0.1)
    ax1.set_title("Theoretical Situational Intensity (I) Decay Curves")
    ax1.set_xlabel("Striker Balls Faced Before Delivery (bf)")
    ax1.set_ylabel("Situational Intensity Score (0-100)")
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # 2. Empirical Impact on High-Pressure Capture in Clean Population
    ax2.plot(df_bf['bf_bin'], df_bf['hp_capture_pct'], marker='o', color='#d62728', lw=2.5, label='Control High-Pressure Capture %')
    ax2.plot(df_bf['bf_bin'], df_bf['mean_intensity'], marker='s', color='#7f7f7f', linestyle='--', alpha=0.6, label='Mean Intensity I (Control)')
    ax2.axvline(10.0, color='black', linestyle='--', alpha=0.6)
    ax2.set_title("Empirical Collapse in High-Pressure Capture (180,839 Balls)")
    ax2.set_xlabel("Striker Balls Faced Before Delivery (bf)")
    ax2.set_ylabel("High-Pressure Capture (%)")
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.suptitle("Figure 1: Mathematical Structure & Empirical Impact of the Balls-Faced Cliff", y=1.02)
    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig1_balls_faced_decay_curves.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def plot_position_capture():
    pos_csv = OUTPUT_DIR / "bias_and_position_comparison.csv"
    if not pos_csv.exists():
        return
    df = pd.read_csv(pos_csv)
    # Filter individual batting orders 1 to 11
    df_orders = df[df['batting_order'].str.isdigit()].copy()
    df_orders['batting_order'] = df_orders['batting_order'].astype(int)

    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    x = np.arange(1, 12)
    w = 0.16

    ax.bar(x - 2*w, df_orders['Cand_0_HP_pct'], width=w, label='Control (Linear Cliff)', color='#d62728', alpha=0.85)
    ax.bar(x - w, df_orders['Cand_1_HP_pct'], width=w, label='Cand 1 (Smooth Decay)', color='#1f77b4', alpha=0.85)
    ax.bar(x, df_orders['Cand_2_HP_pct'], width=w, label='Cand 2 (Match-Stakes Context)', color='#ff7f0e', alpha=0.85)
    ax.bar(x + w, df_orders['Cand_3_HP_pct'], width=w, label='Cand 3 (Leverage & Crisis)', color='#2ca02c', alpha=0.85)
    ax.bar(x + 2*w, df_orders['Cand_4_HP_pct'], width=w, label='Cand 4 (Pure Task Difficulty)', color='#9467bd', alpha=0.85)

    ax.set_title("High-Pressure Capture Rate by Batting Order Position (1 to 11)")
    ax.set_xlabel("Batting Order Position")
    ax.set_ylabel("High-Pressure Capture (%)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pos {p}" for p in x])
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig2_hp_capture_by_position.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def plot_scenarios():
    scen_csv = OUTPUT_DIR / "scenario_testing_audit.csv"
    if not scen_csv.exists():
        return
    df = pd.read_csv(scen_csv)

    # Focus on critical scenarios: Collapses, Set Batters in Crisis, Blowouts, Death Finishes
    key_scenarios = [
        '6. 1st Inn PP Collapse',
        '10. Set Batters in Crisis',
        '8. Hopeless Chase / Blowout',
        '9. Middle-Over Squeeze',
        '7. Competitive Death Finish'
    ]
    sub = df[df['scenario_name'].isin(key_scenarios)].copy()

    fig, ax = plt.subplots(figsize=(14, 6), dpi=300)

    x = np.arange(len(sub))
    w = 0.16

    ax.bar(x - 2*w, sub['Cand_0_HP_pct'], width=w, label='Control', color='#d62728', alpha=0.85)
    ax.bar(x - w, sub['Cand_1_HP_pct'], width=w, label='Cand 1 (Smooth Decay)', color='#1f77b4', alpha=0.85)
    ax.bar(x, sub['Cand_2_HP_pct'], width=w, label='Cand 2 (Match-Stakes)', color='#ff7f0e', alpha=0.85)
    ax.bar(x + w, sub['Cand_3_HP_pct'], width=w, label='Cand 3 (Lev & Crisis)', color='#2ca02c', alpha=0.85)
    ax.bar(x + 2*w, sub['Cand_4_HP_pct'], width=w, label='Cand 4 (Pure Task Diff)', color='#9467bd', alpha=0.85)

    ax.set_title("Model Comparison on Key Archetypal Cricket Scenarios")
    ax.set_xlabel("Scenario")
    ax.set_ylabel("High-Pressure Capture (%)")
    ax.set_xticks(x)
    ax.set_xticklabels([s.split('. ')[1] for s in sub['scenario_name']], rotation=15, ha='right')
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig3_archetypal_scenarios_comparison.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def plot_ranking_scatter():
    bat_csv = OUTPUT_DIR / "batting_candidate_rankings_comparison.csv"
    if not bat_csv.exists():
        return
    df = pd.read_csv(bat_csv)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)

    # Filter players who are qualified in both
    t1_1 = df[df['tier_ctrl'].isin(['Tier 1', 'Tier 2']) & df['tier_1'].isin(['Tier 1', 'Tier 2'])]
    t1_2 = df[df['tier_ctrl'].isin(['Tier 1', 'Tier 2']) & df['tier_2'].isin(['Tier 1', 'Tier 2'])]
    t1_4 = df[df['tier_ctrl'].isin(['Tier 1', 'Tier 2']) & df['tier_4'].isin(['Tier 1', 'Tier 2'])]

    # 1. Cand 1 vs Control
    ax1.scatter(t1_1['brs3_ctrl'], t1_1['brs3_1'], alpha=0.6, color='#1f77b4', s=25)
    ax1.plot([0, 100], [0, 100], color='black', linestyle='--', alpha=0.5)
    ax1.set_title("Candidate 1 (Smooth Decay) vs Control [Rho = 0.8094]")
    ax1.set_xlabel("Control BRS3")
    ax1.set_ylabel("Candidate 1 BRS3")
    ax1.grid(True, alpha=0.3)

    # 2. Cand 2 vs Control
    ax2.scatter(t1_2['brs3_ctrl'], t1_2['brs3_2'], alpha=0.6, color='#ff7f0e', s=25)
    ax2.plot([0, 100], [0, 100], color='black', linestyle='--', alpha=0.5)
    ax2.set_title("Candidate 2 (Match-Stakes) vs Control [Rho = 0.6185]")
    ax2.set_xlabel("Control BRS3")
    ax2.set_ylabel("Candidate 2 BRS3")
    ax2.grid(True, alpha=0.3)

    # 3. Cand 4 vs Control
    ax3.scatter(t1_4['brs3_ctrl'], t1_4['brs3_4'], alpha=0.6, color='#9467bd', s=25)
    ax3.plot([0, 100], [0, 100], color='black', linestyle='--', alpha=0.5)
    ax3.set_title("Candidate 4 (Pure Task Diff) vs Control [Rho = 0.5808]")
    ax3.set_xlabel("Control BRS3")
    ax3.set_ylabel("Candidate 4 BRS3")
    ax3.grid(True, alpha=0.3)

    # Annotate Pat Cummins on all three
    cummins = df[df['player_name'] == 'Patrick Cummins'].iloc[0]
    ax1.annotate("Pat Cummins\n(#1 -> #35)", (cummins['brs3_ctrl'], cummins['brs3_1']),
                 xytext=(cummins['brs3_ctrl']-20, cummins['brs3_1']+10),
                 arrowprops=dict(facecolor='darkred', arrowstyle='->', lw=1.5), fontsize=8, weight='bold', color='darkred')
    ax2.annotate("Pat Cummins\n(#1 -> #83)", (cummins['brs3_ctrl'], cummins['brs3_2']),
                 xytext=(cummins['brs3_ctrl']-20, cummins['brs3_2']+10),
                 arrowprops=dict(facecolor='darkred', arrowstyle='->', lw=1.5), fontsize=8, weight='bold', color='darkred')
    ax3.annotate("Pat Cummins\n(#1 -> #96)", (cummins['brs3_ctrl'], cummins['brs3_4']),
                 xytext=(cummins['brs3_ctrl']-20, cummins['brs3_4']+10),
                 arrowprops=dict(facecolor='darkred', arrowstyle='->', lw=1.5), fontsize=8, weight='bold', color='darkred')

    plt.suptitle("Figure 4: BRS3 Score Correlation & Correction of Finisher Inflation", y=1.02)
    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig4_player_ranking_stability_scatter.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def main():
    print("=== Step 16.7 Script 05: Generate Visualizations ===")
    t0 = time.time()
    set_plot_style()
    plot_decay_curves()
    plot_position_capture()
    plot_scenarios()
    plot_ranking_scatter()
    print(f"All visualizations successfully generated in {time.time() - t0:.2f}s.")


if __name__ == "__main__":
    main()
