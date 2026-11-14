"""
Step 16.6: Script 06 - Generate Publication-Grade Visualizations
==============================================================
Generates visual evidence for Step 16.6 Report:
1. fig1_hp_capture_by_batting_position.png:
   - HP Capture % across Batting Positions 1 to 11 (Control vs Candidates).
   - Demonstrates that top-order capture remains ~7%, while lower-order drops from 52% to 44% (1A) / 23% (1B).
2. fig2_phase_representation_by_candidate.png:
   - High-Pressure Phase Representation across Candidates (PP, Middle, Death).
3. fig3_cricket_scenario_comparison.png:
   - Heatmap / matrix comparing the 7 representative cricket scenarios across all candidates.
4. fig4_ranking_scatter_control_vs_candidates.png:
   - Scatter plots of Player Scores (BRS3 and BoRS): Control vs Candidate 1A and Candidate 2.

Outputs:
- outputs/step_16_6_leverage_integration/fig1_hp_capture_by_batting_position.png
- outputs/step_16_6_leverage_integration/fig2_phase_representation_by_candidate.png
- outputs/step_16_6_leverage_integration/fig3_cricket_scenario_comparison.png
- outputs/step_16_6_leverage_integration/fig4_ranking_scatter_control_vs_candidates.png
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs/step_16_6_leverage_integration")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#eeeeee'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7


def main():
    print("=== Step 16.6 Script 06: Generate Visualizations ===")
    t0 = time.time()

    # Load data
    pos_df = pd.read_csv(OUTPUT_DIR / "batting_position_candidate_comparison.csv")
    phase_df = pd.read_csv(OUTPUT_DIR / "phase_innings_candidate_comparison.csv")
    sc_df = pd.read_csv(OUTPUT_DIR / "scenario_classification_audit.csv")
    bat_comp = pd.read_csv(OUTPUT_DIR / "batting_candidate_rankings_comparison.csv")
    bowl_comp = pd.read_csv(OUTPUT_DIR / "bowling_candidate_rankings_comparison.csv")

    # -------------------------------------------------------------
    # Figure 1: Batting Position HP Capture %
    # -------------------------------------------------------------
    print("Generating Figure 1: Batting Position HP Capture %...")
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    # Filter positions 1 to 11
    pos11 = pos_df[pos_df['batting_order'] != 'Summary'].copy()
    pos11['pos_num'] = pos11['batting_order'].astype(int)
    pos11 = pos11.sort_values('pos_num')

    x = pos11['pos_num'].values
    w = 0.17

    ax.bar(x - 2*w, pos11['Control (Candidate 0) HP %'], w, label='Control (Original PI Z > 1.0)', color='#34495e', edgecolor='#2c3e50')
    ax.bar(x - w, pos11['Additive 70/30 (Candidate 1A) HP %'], w, label='Candidate 1A (Additive 70/30)', color='#3498db', edgecolor='#2980b9')
    ax.bar(x, pos11['Multiplicative Gated (Candidate 2) HP %'], w, label='Candidate 2 (Gated Interaction)', color='#2ecc71', edgecolor='#27ae60')
    ax.bar(x + w, pos11['Additive 50/50 (Candidate 1B) HP %'], w, label='Candidate 1B (Additive 50/50)', color='#e67e22', edgecolor='#d35400')
    ax.bar(x + 2*w, pos11['Convex Composite (Candidate 3) HP %'], w, label='Candidate 3 (Convex Composite)', color='#9b59b6', edgecolor='#8e44ad')

    ax.set_title("Figure 1: High-Pressure Delivery Capture Rate Across Batting Positions 1–11\n(Control vs Experimental Expected Leverage Integration Candidates)", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Batting Order Position (1 = Opener to 11 = Number 11)", fontsize=10)
    ax.set_ylabel("% of Deliveries Classified as High Pressure", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pos {p}" for p in x], fontsize=9)
    ax.set_ylim(0, 95)
    ax.grid(True, axis='y')
    ax.legend(loc='upper left', frameon=True, fontsize=8.5)

    # Annotation box
    textstr = "\n".join((
        r"$\mathbf{Key\ Position\ Findings:}$",
        r"$\bullet\ \mathrm{Top\ Order\ (1\text{-}3):}\ \mathrm{Capture\ remains\ flat\ at\ \sim 6\text{-}7\%}$",
        r"$\ \ \mathrm{across\ all\ candidates\ (leverage\ does\ not\ fix\ top\text{-}order\ bias).}$",
        r"$\bullet\ \mathrm{Lower\ Order\ (7\text{-}11):}\ \mathrm{Capture\ drops\ from\ 52.4\%\ (Control)}$",
        r"$\ \ \mathrm{to\ 43.8\%\ (1A)\ and\ 23.2\%\ (1B)\ by\ filtering\ blowouts.}$"
    ))
    props = dict(boxstyle='round,pad=0.5', facecolor='#ffffff', edgecolor='#bdc3c7', alpha=0.95)
    ax.text(0.48, 0.95, textstr, transform=ax.transAxes, fontsize=8.5, verticalalignment='top', bbox=props)

    plt.tight_layout()
    fig1_path = OUTPUT_DIR / "fig1_hp_capture_by_batting_position.png"
    plt.savefig(fig1_path)
    plt.close()
    print(f"Saved Figure 1 to {fig1_path}")

    # -------------------------------------------------------------
    # Figure 2: Phase Representation Comparison
    # -------------------------------------------------------------
    print("Generating Figure 2: Phase Representation Comparison...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # Batting Phase Share
    bat_phase = phase_df[phase_df['discipline'] == 'Batting'].groupby('phase')[
        ['Control (Candidate 0) HP Count', 'Additive 70/30 (Candidate 1A) HP Count',
         'Multiplicative Gated (Candidate 2) HP Count', 'Additive 50/50 (Candidate 1B) HP Count']
    ].sum().loc[['PP', 'Middle', 'Death']]

    bat_phase_pct = bat_phase.div(bat_phase.sum(axis=0), axis=1) * 100.0

    x_p = np.arange(3)
    w_p = 0.20
    phases = ['Powerplay', 'Middle Overs', 'Death Overs']

    ax1.bar(x_p - 1.5*w_p, bat_phase_pct['Control (Candidate 0) HP Count'], w_p, label='Control (Z_PI > 1.0)', color='#34495e')
    ax1.bar(x_p - 0.5*w_p, bat_phase_pct['Additive 70/30 (Candidate 1A) HP Count'], w_p, label='Cand 1A (70/30)', color='#3498db')
    ax1.bar(x_p + 0.5*w_p, bat_phase_pct['Multiplicative Gated (Candidate 2) HP Count'], w_p, label='Cand 2 (Gated)', color='#2ecc71')
    ax1.bar(x_p + 1.5*w_p, bat_phase_pct['Additive 50/50 (Candidate 1B) HP Count'], w_p, label='Cand 1B (50/50)', color='#e67e22')

    ax1.set_title("Batting HP Phase Representation Share (%)", fontsize=11, fontweight='bold')
    ax1.set_xticks(x_p)
    ax1.set_xticklabels(phases, fontsize=9)
    ax1.set_ylabel("% Share of All HP Batting Balls", fontsize=10)
    ax1.set_ylim(0, 60)
    ax1.grid(True, axis='y')
    ax1.legend(loc='upper right', frameon=True, fontsize=8)

    # Bowling Phase Share
    bowl_phase = phase_df[phase_df['discipline'] == 'Bowling'].groupby('phase')[
        ['Control (Candidate 0) HP Count', 'Additive 70/30 (Candidate 1A) HP Count',
         'Multiplicative Gated (Candidate 2) HP Count', 'Additive 50/50 (Candidate 1B) HP Count']
    ].sum().loc[['PP', 'Middle', 'Death']]

    bowl_phase_pct = bowl_phase.div(bowl_phase.sum(axis=0), axis=1) * 100.0

    ax2.bar(x_p - 1.5*w_p, bowl_phase_pct['Control (Candidate 0) HP Count'], w_p, label='Control (Z_PI > 1.0)', color='#34495e')
    ax2.bar(x_p - 0.5*w_p, bowl_phase_pct['Additive 70/30 (Candidate 1A) HP Count'], w_p, label='Cand 1A (70/30)', color='#3498db')
    ax2.bar(x_p + 0.5*w_p, bowl_phase_pct['Multiplicative Gated (Candidate 2) HP Count'], w_p, label='Cand 2 (Gated)', color='#2ecc71')
    ax2.bar(x_p + 1.5*w_p, bowl_phase_pct['Additive 50/50 (Candidate 1B) HP Count'], w_p, label='Cand 1B (50/50)', color='#e67e22')

    ax2.set_title("Bowling HP Phase Representation Share (%)", fontsize=11, fontweight='bold')
    ax2.set_xticks(x_p)
    ax2.set_xticklabels(phases, fontsize=9)
    ax2.set_ylabel("% Share of All HP Bowling Balls", fontsize=10)
    ax2.set_ylim(0, 60)
    ax2.grid(True, axis='y')
    ax2.legend(loc='upper right', frameon=True, fontsize=8)

    plt.suptitle("Figure 2: Step 16.6 — Phase Representation across Experimental PI Candidates", fontsize=12, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig2_path = OUTPUT_DIR / "fig2_phase_representation_by_candidate.png"
    plt.savefig(fig2_path)
    plt.close()
    print(f"Saved Figure 2 to {fig2_path}")

    # -------------------------------------------------------------
    # Figure 3: Scenario Classification Heatmap
    # -------------------------------------------------------------
    print("Generating Figure 3: Scenario Classification Heatmap...")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)

    cand_cols = ['hp_control', 'hp_cand1a_70_30', 'hp_cand1b_50_50', 'hp_cand2_gated', 'hp_cand3_composite']
    cand_labels = ['Control\n(Z_PI > 1.0)', 'Cand 1A\n(Add 70/30)', 'Cand 1B\n(Add 50/50)', 'Cand 2\n(Gated)', 'Cand 3\n(Composite)']

    scenario_short_names = [
        '1: Steep Chase PP',
        '2: Easy Chase (Win)',
        '3: Tight Death Chase',
        '4: Inn 1 Collapse (30/3)',
        '5: Hopeless Mid Collapse',
        '6: Routine Parity Ball',
        '7: Hopeless Tailender'
    ]

    mat = sc_df[cand_cols].values.astype(int)

    cmap = plt.cm.colors.ListedColormap(['#ecf0f1', '#27ae60'])
    im = ax.imshow(mat, cmap=cmap, aspect='auto')

    ax.set_xticks(np.arange(len(cand_labels)))
    ax.set_xticklabels(cand_labels, fontsize=9)
    ax.set_yticks(np.arange(len(scenario_short_names)))
    ax.set_yticklabels(scenario_short_names, fontsize=9, fontweight='bold')

    for i in range(len(scenario_short_names)):
        for j in range(len(cand_labels)):
            val = mat[i, j]
            label = "HP" if val == 1 else "NON-HP"
            color = "#ffffff" if val == 1 else "#7f8c8d"
            ax.text(j, i, label, ha='center', va='center', fontsize=9, fontweight='bold', color=color)

    ax.set_title("Figure 3: Cricket Scenario Classification Audit\n(Green = Classified as High Pressure; Grey = Classified as Non-HP)", fontsize=11, fontweight='bold', pad=12)

    plt.tight_layout()
    fig3_path = OUTPUT_DIR / "fig3_cricket_scenario_comparison.png"
    plt.savefig(fig3_path)
    plt.close()
    print(f"Saved Figure 3 to {fig3_path}")

    # -------------------------------------------------------------
    # Figure 4: Player Score Scatter (Control vs Candidates)
    # -------------------------------------------------------------
    print("Generating Figure 4: Player Ranking Scatter Comparison...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # Batting: Control BRS3 vs Cand 1A BRS3
    t1_bat = bat_comp[(bat_comp['tier_ctrl'] == 'Tier 1') & (bat_comp['tier_1A'] == 'Tier 1')].copy()
    ax1.scatter(t1_bat['brs3_ctrl'], t1_bat['brs3_1A'], color='#3498db', alpha=0.7, s=30, edgecolors='#2980b9', label='Common Tier 1 Batters (N=189)')
    ax1.plot([40, 85], [40, 85], color='#e74c3c', linestyle='--', linewidth=1.5, label='Identity (y = x)')
    ax1.set_title("Batting: Control BRS3 vs Candidate 1A BRS3\n(Spearman rho = 0.7631, Pearson r = 0.7728)", fontsize=10, fontweight='bold')
    ax1.set_xlabel("Control BRS3 Score (Step 16 Baseline)", fontsize=9)
    ax1.set_ylabel("Candidate 1A (Additive 70/30) BRS3 Score", fontsize=9)
    ax1.grid(True)
    ax1.legend(loc='upper left', frameon=True, fontsize=8.5)

    # Bowling: Control BoRS vs Cand 2 BoRS
    t1_bowl = bowl_comp[(bowl_comp['tier_ctrl'] == 'Tier 1') & (bowl_comp['tier_2'] == 'Tier 1')].copy()
    ax2.scatter(t1_bowl['bors_ctrl'], t1_bowl['bors_2'], color='#2ecc71', alpha=0.7, s=30, edgecolors='#27ae60', label='Common Tier 1 Bowlers (N=160)')
    ax2.plot([45, 90], [45, 90], color='#e74c3c', linestyle='--', linewidth=1.5, label='Identity (y = x)')
    ax2.set_title("Bowling: Control BoRS vs Candidate 2 BoRS\n(Spearman rho = 0.8226, Pearson r = 0.8345)", fontsize=10, fontweight='bold')
    ax2.set_xlabel("Control BoRS Score (Step 16 Baseline)", fontsize=9)
    ax2.set_ylabel("Candidate 2 (Multiplicative Gated) BoRS Score", fontsize=9)
    ax2.grid(True)
    ax2.legend(loc='upper left', frameon=True, fontsize=8.5)

    plt.suptitle("Figure 4: Step 16.6 — Player Reliability Score Sensitivity across Candidates", fontsize=12, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig4_path = OUTPUT_DIR / "fig4_ranking_scatter_control_vs_candidates.png"
    plt.savefig(fig4_path)
    plt.close()
    print(f"Saved Figure 4 to {fig4_path}")

    print(f"Visualizations successfully generated in {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
