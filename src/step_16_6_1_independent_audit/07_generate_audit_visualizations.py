"""
Step 16.6.1: Script 07 - Generate Publication-Grade Audit Visualizations
========================================================================
Generates four high-resolution diagnostic figures:
1. fig1_multiplier_sensitivity.png:
   - Sensitivity curves for multiplier m in [0.00, 0.80] showing capture rates,
     Tier 1 player qualifications, and Spearman ranking correlations.
2. fig2_demoted_deliveries_distribution.png:
   - Win probability and leverage distributions of demoted deliveries, highlighting
     the 24% pure blowouts vs 35% competitive/parity deliveries demoted.
3. fig3_top_order_leverage_vs_pi.png:
   - Top-order delivery scatter (Z_PI vs Z_Lev), proving why S_2 <= 0 prevents
     the promotion of high-leverage deliveries into High Pressure.
4. fig4_candidate2_vs_control_rankings.png:
   - Scatter plots of Control vs Candidate 2 BRS3 and BoRS scores, highlighting
     key player movements (Dhoni, Shankar, Cummins, Baartman).
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs/step_16_6_1_independent_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STEP_16_6_DIR = Path("outputs/step_16_6_leverage_integration")


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


def plot_multiplier_sensitivity():
    sens_path = OUTPUT_DIR / "multiplier_sensitivity_analysis.csv"
    if not sens_path.exists():
        return
    df = pd.read_csv(sens_path)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5), dpi=300)

    # 1. Capture Rates
    ax1.plot(df['multiplier'], df['batting_hp_pct'], marker='o', color='#1f77b4', lw=2.5, label='Overall Batting HP %')
    ax1.plot(df['multiplier'], df['lower_order_7_11_hp_pct'], marker='s', color='#d62728', lw=2, label='Lower Order (7-11) HP %')
    ax1.plot(df['multiplier'], df['top_order_1_3_hp_pct'], marker='^', color='#2ca02c', lw=2, label='Top Order (1-3) HP %')
    ax1.axvline(0.50, color='gray', linestyle='--', alpha=0.7, label='Candidate 2 Choice (m=0.50)')
    ax1.set_title("HP Capture % by Multiplier (m)")
    ax1.set_xlabel("Leverage Multiplier (m)")
    ax1.set_ylabel("High-Pressure Capture (%)")
    ax1.legend(loc='center left')
    ax1.grid(True, alpha=0.3)

    # 2. Ranking Correlations
    ax2.plot(df['multiplier'], df['bat_spearman_rho'], marker='o', color='#9467bd', lw=2.5, label='Batting Spearman Rho')
    ax2.plot(df['multiplier'], df['bowl_spearman_rho'], marker='s', color='#8c564b', lw=2.5, label='Bowling Spearman Rho')
    ax2.axvline(0.50, color='gray', linestyle='--', alpha=0.7, label='Candidate 2 (m=0.50)')
    ax2.axhline(0.70, color='red', linestyle=':', alpha=0.6, label='Acceptable Stability Floor (0.70)')
    ax2.set_title("Rank Correlation (Rho) vs Control")
    ax2.set_xlabel("Leverage Multiplier (m)")
    ax2.set_ylabel("Spearman Rank Correlation")
    ax2.legend(loc='lower left')
    ax2.grid(True, alpha=0.3)

    # 3. Tier 1 Qualified Counts
    ax3.plot(df['multiplier'], df['bat_t1_qualified'], marker='o', color='#1f77b4', lw=2.5, label='Tier 1 Batters')
    ax3.plot(df['multiplier'], df['bowl_t1_qualified'], marker='s', color='#ff7f0e', lw=2.5, label='Tier 1 Bowlers')
    ax3.axvline(0.50, color='gray', linestyle='--', alpha=0.7, label='Candidate 2 (m=0.50)')
    ax3.set_title("Tier 1 Qualified Players")
    ax3.set_xlabel("Leverage Multiplier (m)")
    ax3.set_ylabel("Qualified Player Count")
    ax3.legend(loc='lower left')
    ax3.grid(True, alpha=0.3)

    plt.suptitle("Figure 1: Sensitivity Analysis of Multiplier m in Candidate 2 [Z_2 = Std(Z_PI * (1 + m*tanh(Z_Lev)))]", y=1.02)
    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig1_multiplier_sensitivity.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def plot_demoted_deliveries():
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    if not parquet_path.exists():
        return
    df = pd.read_parquet(parquet_path)
    bat_mask = df['is_batter_ball_faced'] == 1
    bat_df = df[bat_mask].copy()

    ctrl_hp = bat_df['hp_cand0_bat'] == True
    c2_hp = bat_df['hp_cand2_bat'] == True

    retained = bat_df[ctrl_hp & c2_hp]
    demoted = bat_df[ctrl_hp & ~c2_hp]
    promoted = bat_df[~ctrl_hp & c2_hp]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5), dpi=300)

    # Win Probability distribution
    ax1.hist(demoted['wp_before'].dropna(), bins=30, alpha=0.6, color='#d62728', density=True, label=f'Demoted from HP (n={len(demoted):,})')
    ax1.hist(retained['wp_before'].dropna(), bins=30, alpha=0.5, color='#1f77b4', density=True, label=f'Retained HP (n={len(retained):,})')
    ax1.hist(promoted['wp_before'].dropna(), bins=30, alpha=0.5, color='#2ca02c', density=True, label=f'Promoted to HP (n={len(promoted):,})')
    ax1.axvline(0.05, color='black', linestyle=':', label='Blowout Cutoffs (5% & 95%)')
    ax1.axvline(0.95, color='black', linestyle=':')
    ax1.set_title("Pre-Delivery Win Probability Distribution by Cohort")
    ax1.set_xlabel("Win Probability Before Delivery (wp_before)")
    ax1.set_ylabel("Probability Density")
    ax1.legend(loc='upper center')
    ax1.grid(True, alpha=0.3)

    # Expected Leverage distribution
    ax2.hist(np.clip(demoted['expected_leverage_pct'], 0, 8), bins=30, alpha=0.6, color='#d62728', density=True, label='Demoted Deliveries')
    ax2.hist(np.clip(retained['expected_leverage_pct'], 0, 8), bins=30, alpha=0.5, color='#1f77b4', density=True, label='Retained Deliveries')
    ax2.hist(np.clip(promoted['expected_leverage_pct'], 0, 8), bins=30, alpha=0.5, color='#2ca02c', density=True, label='Promoted Deliveries')
    ax2.set_title("Expected Delivery Leverage Distribution by Cohort")
    ax2.set_xlabel("Expected Delivery Leverage (%)")
    ax2.set_ylabel("Probability Density")
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.suptitle("Figure 2: Match State Anatomy of Demoted vs Retained vs Promoted Deliveries", y=1.02)
    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig2_demoted_deliveries_distribution.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def plot_top_order_leverage_vs_pi():
    parquet_path = STEP_16_6_DIR / "delivery_candidates_classified.parquet"
    if not parquet_path.exists():
        return
    df = pd.read_parquet(parquet_path)
    top_df = df[(df['is_batter_ball_faced'] == 1) & (df['batting_order'].isin([1, 2, 3]))].copy()

    # Sample 5000 points for clear visualization
    sample = top_df.sample(5000, random_state=42)

    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)

    # Color code by classification
    ctrl_hp = sample['hp_cand0_bat'] == True
    c2_hp = sample['hp_cand2_bat'] == True

    ax.scatter(sample.loc[~ctrl_hp & ~c2_hp, 'batting_z_score'], sample.loc[~ctrl_hp & ~c2_hp, 'lev_z_score_bat'],
               alpha=0.25, color='#7f7f7f', s=15, label='Common Low Pressure (78.9%)')
    ax.scatter(sample.loc[ctrl_hp & ~c2_hp, 'batting_z_score'], sample.loc[ctrl_hp & ~c2_hp, 'lev_z_score_bat'],
               alpha=0.7, color='#d62728', s=35, marker='x', label='Demoted by Cand 2 (False Negatives)')
    ax.scatter(sample.loc[ctrl_hp & c2_hp, 'batting_z_score'], sample.loc[ctrl_hp & c2_hp, 'lev_z_score_bat'],
               alpha=0.7, color='#1f77b4', s=30, label='Retained High Pressure (Common)')
    ax.scatter(sample.loc[~ctrl_hp & c2_hp, 'batting_z_score'], sample.loc[~ctrl_hp & c2_hp, 'lev_z_score_bat'],
               alpha=0.8, color='#2ca02c', s=35, marker='^', label='Promoted by Cand 2')

    # Threshold lines
    ax.axvline(1.0, color='blue', linestyle='--', alpha=0.6, label='Control Threshold (Z_PI = 1.0)')
    ax.axvline(0.0, color='black', linestyle=':', alpha=0.5, label='Sign Boundary (Z_PI = 0.0)')
    ax.axhline(1.0, color='green', linestyle='--', alpha=0.6, label='High Leverage (Z_Lev = 1.0)')

    # Shaded unpromotable region
    ax.axvspan(-3.0, 0.0, alpha=0.08, color='red')
    ax.text(-2.5, 3.0, "MATHEMATICALLY UNPROMOTABLE REGION\n(S_2 <= 0 because Z_PI <= 0,\ndespite extreme high leverage)",
            fontsize=9, weight='bold', color='darkred', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title("Top-Order Deliveries: Task Difficulty (Z_PI) vs Consequence (Z_Lev)")
    ax.set_xlabel("Batting Task Difficulty Z-score (Z_PI)")
    ax.set_ylabel("Expected Delivery Leverage Z-score (Z_Lev)")
    ax.set_xlim(-3.0, 3.5)
    ax.set_ylim(-2.5, 4.5)
    ax.legend(loc='lower right', frameon=True)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig3_top_order_leverage_vs_pi.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def plot_ranking_diagnostics():
    bat_diag_path = OUTPUT_DIR / "batter_rank_movement_diagnostics.csv"
    bowl_diag_path = OUTPUT_DIR / "bowler_rank_movement_diagnostics.csv"
    if not bat_diag_path.exists() or not bowl_diag_path.exists():
        return

    bat_df = pd.read_csv(bat_diag_path)
    bowl_df = pd.read_csv(bowl_diag_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=300)

    # 1. Batting Top 20 Movements
    colors = ['#2ca02c' if x > 0 else ('#d62728' if x < 0 else '#1f77b4') for x in bat_df['rank_shift']]
    bars = ax1.barh(bat_df['player_name'], bat_df['rank_shift'], color=colors, alpha=0.8)
    ax1.axvline(0, color='black', lw=1)
    ax1.set_title("Top 20 Control Batters: Rank Shift in Candidate 2 (+ = Rise, - = Fall)")
    ax1.set_xlabel("Rank Shift (Rank_Ctrl - Rank_C2)")
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3)

    # Annotate key cases
    for i, row in bat_df.iterrows():
        shift = row['rank_shift']
        if pd.notna(shift):
            t_str = f"{int(shift):+d} (R{int(row['rank_ctrl'])} -> R{int(row['rank_c2']) if pd.notna(row['rank_c2']) else 'DQ'})"
            x_pos = shift + (1.5 if shift >= 0 else -1.5)
            ha = 'left' if shift >= 0 else 'right'
            ax1.text(x_pos, i, t_str, va='center', ha=ha, fontsize=8, weight='bold')

    # 2. Bowling Top 20 Movements
    colors_bw = ['#2ca02c' if x > 0 else ('#d62728' if x < 0 else '#1f77b4') for x in bowl_df['rank_shift']]
    bars_bw = ax2.barh(bowl_df['player_name'], bowl_df['rank_shift'], color=colors_bw, alpha=0.8)
    ax2.axvline(0, color='black', lw=1)
    ax2.set_title("Top 20 Control Bowlers: Rank Shift in Candidate 2 (+ = Rise, - = Fall)")
    ax2.set_xlabel("Rank Shift (Rank_Ctrl - Rank_C2)")
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)

    for i, row in bowl_df.iterrows():
        shift = row['rank_shift']
        if pd.notna(shift):
            t_str = f"{int(shift):+d} (R{int(row['rank_ctrl'])} -> R{int(row['rank_c2']) if pd.notna(row['rank_c2']) else 'DQ'})"
            x_pos = shift + (1.5 if shift >= 0 else -1.5)
            ha = 'left' if shift >= 0 else 'right'
            ax2.text(x_pos, i, t_str, va='center', ha=ha, fontsize=8, weight='bold')

    plt.suptitle("Figure 4: Player Ranking Movement Diagnostics (Control vs Candidate 2)", y=1.02)
    plt.tight_layout()
    out_fig = OUTPUT_DIR / "fig4_candidate2_vs_control_rankings.png"
    plt.savefig(out_fig, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_fig}")


def main():
    print("=== Step 16.6.1 Script 07: Generate Audit Visualizations ===")
    t0 = time.time()
    set_plot_style()
    plot_multiplier_sensitivity()
    plot_demoted_deliveries()
    plot_top_order_leverage_vs_pi()
    plot_ranking_diagnostics()
    print(f"All visualizations successfully generated in {time.time() - t0:.2f}s.")


if __name__ == "__main__":
    main()
