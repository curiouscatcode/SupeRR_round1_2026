"""
Step 16: Phase-Relative Pressure Classification - Script 04
Generate Comparative Visualizations
============================================================
Generates 5 publication-quality figures comparing original PI > 60.0
with experimental Z-score classifications:

1. fig1_pi_distribution_by_phase.png:
   Histograms/KDE showing Batting and Bowling PI distribution by phase
   with phase means, medians, and fixed 60 threshold vs Z=1.0 cutoffs.

2. fig2_innings_distribution_comparison.png:
   Side-by-side box/violin plots comparing Innings 1 vs Innings 2
   distributions across Powerplay, Middle, and Death phases.

3. fig3_threshold_tradeoffs.png:
   Dual-axis line charts illustrating the trade-off between
   delivery capture percentage and qualified player sample depth.

4. fig4_batting_role_exposure_comparison.png:
   Grouped bar charts comparing batting role exposure (Top, Middle, Lower)
   under Baseline PI > 60.0 vs Z-score thresholds.

5. fig5_bowling_phase_exposure_comparison.png:
   Grouped bar charts comparing bowling phase capture rates and phase shares
   under Baseline PI > 60.0 vs Z-score thresholds.

Outputs:
- outputs/step_16_phase_relative_pressure/*.png
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_phase_relative_pressure")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Styling configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11


def plot_fig1_distributions(df: pd.DataFrame):
    """Figure 1: PI Distributions by Phase with Cutoff Lines."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharey='row')
    fig.suptitle('Figure 1: Pressure Index (PI) Empirical Distributions by Match Phase', fontsize=15, fontweight='bold', y=0.98)

    phases = ['PP', 'Middle', 'Death']
    phase_titles = ['Powerplay (Overs 1–6)', 'Middle Overs (Overs 7–15)', 'Death Overs (Overs 16–20)']
    colors_bat = ['#1f77b4', '#2ca02c', '#d62728']
    colors_bowl = ['#9467bd', '#8c564b', '#e377c2']

    bat_df = df[df['is_batter_ball_faced'] == 1]
    bowl_df = df[df['is_legal_ball'] == 1]

    # Row 0: Batting PI
    for idx, (ph, title, col) in enumerate(zip(phases, phase_titles, colors_bat)):
        ax = axes[0, idx]
        data = bat_df.loc[bat_df['phase'] == ph, 'Batting_PI']
        mean_v = data.mean()
        std_v = data.std()
        z1_cutoff = mean_v + std_v

        sns.histplot(data, bins=40, kde=True, ax=ax, color=col, alpha=0.4, stat='density')
        ax.axvline(60.0, color='black', linestyle='--', linewidth=2, label='Flat Threshold (PI = 60.0)')
        ax.axvline(mean_v, color='blue', linestyle=':', linewidth=1.8, label=f'Mean ({mean_v:.1f})')
        ax.axvline(z1_cutoff, color='red', linestyle='-', linewidth=2, label=f'Z = 1.0 Cutoff ({z1_cutoff:.1f})')

        ax.set_title(f'Batting: {title}', fontweight='bold')
        ax.set_xlabel('Batting PI')
        ax.set_ylabel('Density' if idx == 0 else '')
        ax.set_xlim(0, 100)
        ax.legend(loc='upper right', fontsize=8.5)

    # Row 1: Bowling PI
    for idx, (ph, title, col) in enumerate(zip(phases, phase_titles, colors_bowl)):
        ax = axes[1, idx]
        data = bowl_df.loc[bowl_df['phase'] == ph, 'Bowling_PI']
        mean_v = data.mean()
        std_v = data.std()
        z1_cutoff = mean_v + std_v

        sns.histplot(data, bins=40, kde=True, ax=ax, color=col, alpha=0.4, stat='density')
        ax.axvline(60.0, color='black', linestyle='--', linewidth=2, label='Flat Threshold (PI = 60.0)')
        ax.axvline(mean_v, color='blue', linestyle=':', linewidth=1.8, label=f'Mean ({mean_v:.1f})')
        ax.axvline(z1_cutoff, color='red', linestyle='-', linewidth=2, label=f'Z = 1.0 Cutoff ({z1_cutoff:.1f})')

        ax.set_title(f'Bowling: {title}', fontweight='bold')
        ax.set_xlabel('Bowling PI')
        ax.set_ylabel('Density' if idx == 0 else '')
        ax.set_xlim(0, 100)
        ax.legend(loc='upper right', fontsize=8.5)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = OUTPUT_DIR / "fig1_pi_distribution_by_phase.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Figure 1 to {out_path}")


def plot_fig2_innings_comparison(df: pd.DataFrame):
    """Figure 2: Innings 1 vs Innings 2 Comparison across Phases."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Figure 2: Innings 1 vs. Innings 2 Pressure Distributions across Match Phases', fontsize=14, fontweight='bold', y=0.98)

    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    # Batting Boxplot
    ax0 = axes[0]
    sns.boxplot(x='phase', y='Batting_PI', hue='innings', data=bat_df, 
                order=['PP', 'Middle', 'Death'], palette=['#4575b4', '#d73027'], ax=ax0, showmeans=True,
                meanprops={"marker":"o", "markerfacecolor":"yellow", "markeredgecolor":"black", "markersize":"7"})
    ax0.axhline(60.0, color='black', linestyle='--', linewidth=1.5, label='Fixed PI = 60.0')
    ax0.set_title('Batting PI: Innings 1 vs Innings 2', fontweight='bold')
    ax0.set_xlabel('Match Phase')
    ax0.set_ylabel('Batting PI')
    ax0.set_ylim(0, 100)
    ax0.legend(title='Innings', loc='upper left')

    # Bowling Boxplot
    ax1 = axes[1]
    sns.boxplot(x='phase', y='Bowling_PI', hue='innings', data=bowl_df, 
                order=['PP', 'Middle', 'Death'], palette=['#4575b4', '#d73027'], ax=ax1, showmeans=True,
                meanprops={"marker":"o", "markerfacecolor":"yellow", "markeredgecolor":"black", "markersize":"7"})
    ax1.axhline(60.0, color='black', linestyle='--', linewidth=1.5, label='Fixed PI = 60.0')
    ax1.set_title('Bowling PI: Innings 1 vs Innings 2', fontweight='bold')
    ax1.set_xlabel('Match Phase')
    ax1.set_ylabel('Bowling PI')
    ax1.set_ylim(0, 100)
    ax1.legend(title='Innings', loc='upper left')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = OUTPUT_DIR / "fig2_innings_distribution_comparison.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Figure 2 to {out_path}")


def plot_fig3_threshold_tradeoffs():
    """Figure 3: Threshold Tradeoffs (Delivery Volume vs Qualified Players)."""
    thresh_csv = OUTPUT_DIR / "zscore_threshold_comparison.csv"
    if not thresh_csv.exists():
        return
    df = pd.read_csv(thresh_csv)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Figure 3: Candidate Threshold Trade-offs: Delivery Capture % vs. Qualified Player Count', fontsize=14, fontweight='bold', y=0.98)

    models_to_plot = [
        ('Batting', axes[0]),
        ('Bowling', axes[1])
    ]

    for disc, ax in models_to_plot:
        sub = df[(df['discipline'] == disc) & (df['grouping_approach'] == 'Approach B (Phase x Innings)') & (df['z_type'] == 'Standard Z')].copy()
        sub['z_val'] = [0.0, 0.5, 1.0, 1.5]

        # Add Baseline reference
        base_row = df[(df['discipline'] == disc) & (df['threshold_name'] == 'PI > 60.0 (Baseline)')].iloc[0]

        color1 = '#1f77b4'
        color2 = '#d62728'

        ax.plot(sub['z_val'], sub['hp_delivery_pct'], marker='o', linewidth=2.5, color=color1, label='HP Delivery % of Total')
        ax.set_xlabel('Standard Z-Score Cutoff (Approach B)')
        ax.set_ylabel('HP Delivery Capture Rate (%)', color=color1, fontweight='bold')
        ax.tick_params(axis='y', labelcolor=color1)
        ax.set_ylim(0, 55)

        ax2 = ax.twinx()
        ax2.plot(sub['z_val'], sub['tier1_rule_b_count'], marker='s', linewidth=2.5, linestyle='--', color=color2, label='Tier 1 (Rule B) Qualified Players')
        ax2.set_ylabel('Tier 1 Qualified Player Count', color=color2, fontweight='bold')
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.set_ylim(0, 360)

        # Baseline horizontal reference markers
        ax.axhline(base_row['hp_delivery_pct'], color=color1, linestyle=':', alpha=0.7, label=f'Baseline Delivery % ({base_row["hp_delivery_pct"]}%)')
        ax2.axhline(base_row['tier1_rule_b_count'], color=color2, linestyle=':', alpha=0.7, label=f'Baseline Tier 1 Count ({base_row["tier1_rule_b_count"]})')

        ax.set_title(f'{disc}: Sensitivity Curve across Z Thresholds', fontweight='bold')
        
        # Combined legend
        lines_1, labels_1 = ax.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', fontsize=8.5)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = OUTPUT_DIR / "fig3_threshold_tradeoffs.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Figure 3 to {out_path}")


def plot_fig4_batting_role_exposure():
    """Figure 4: Batting Role Exposure across Models."""
    role_csv = OUTPUT_DIR / "batting_role_exposure_analysis.csv"
    if not role_csv.exists():
        return
    df = pd.read_csv(role_csv)

    # Filter to selected representative models
    sel_models = [
        ('Baseline\n(PI > 60.0)', 'PI > 60.0', 'Baseline'),
        ('App A (Phase-only)\nZ > 1.0', 'Z > 1.0', 'Approach A (Phase-only)'),
        ('App B (Phase x Inn)\nZ > 1.0', 'Z > 1.0', 'Approach B (Phase x Innings)'),
        ('App B (Phase x Inn)\nZ_rob > 1.0', 'Z_robust > 1.0', 'Approach B (Phase x Innings)')
    ]

    filtered_rows = []
    for label, thresh, app in sel_models:
        sub = df[(df['threshold_name'] == thresh) & (df['grouping_approach'] == app)].copy()
        sub['model_label'] = label
        filtered_rows.append(sub)
    plot_df = pd.concat(filtered_rows)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Figure 4: Batting Role Pressure Exposure: Baseline PI > 60.0 vs. Z-Score Models', fontsize=14, fontweight='bold', y=0.98)

    # Panel 1: Capture Rate (% of each role's deliveries that are HP)
    ax0 = axes[0]
    sns.barplot(x='model_label', y='role_capture_rate_pct', hue='batting_role', data=plot_df, 
                palette=['#1f77b4', '#2ca02c', '#d62728'], ax=ax0)
    ax0.set_title('Within-Role High-Pressure Capture Rate (%)', fontweight='bold')
    ax0.set_xlabel('Pressure Classification Model')
    ax0.set_ylabel('% of Role Balls Classified as HP')
    ax0.set_ylim(0, 60)
    ax0.legend(title='Batting Role', loc='upper right')
    for p in ax0.patches:
        height = p.get_height()
        if height > 0:
            ax0.annotate(f"{height:.1f}%", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8.5, xytext=(0, 2), textcoords='offset points')

    # Panel 2: Share of all HP deliveries (% of total HP balls belonging to each role)
    ax1 = axes[1]
    sns.barplot(x='model_label', y='hp_deliveries_share_pct', hue='batting_role', data=plot_df, 
                palette=['#1f77b4', '#2ca02c', '#d62728'], ax=ax1)
    ax1.set_title('Share of Total High-Pressure Deliveries (%)', fontweight='bold')
    ax1.set_xlabel('Pressure Classification Model')
    ax1.set_ylabel('% of All HP Balls')
    ax1.set_ylim(0, 65)
    ax1.legend(title='Batting Role', loc='upper right')
    for p in ax1.patches:
        height = p.get_height()
        if height > 0:
            ax1.annotate(f"{height:.1f}%", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8.5, xytext=(0, 2), textcoords='offset points')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = OUTPUT_DIR / "fig4_batting_role_exposure_comparison.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Figure 4 to {out_path}")


def plot_fig5_bowling_phase_exposure():
    """Figure 5: Bowling Phase Exposure across Models."""
    phase_csv = OUTPUT_DIR / "bowling_phase_exposure_analysis.csv"
    if not phase_csv.exists():
        return
    df = pd.read_csv(phase_csv)

    sel_models = [
        ('Baseline\n(PI > 60.0)', 'PI > 60.0', 'Baseline'),
        ('App A (Phase-only)\nZ > 1.0', 'Z > 1.0', 'Approach A (Phase-only)'),
        ('App B (Phase x Inn)\nZ > 1.0', 'Z > 1.0', 'Approach B (Phase x Innings)'),
        ('App B (Phase x Inn)\nZ_rob > 1.0', 'Z_robust > 1.0', 'Approach B (Phase x Innings)')
    ]

    filtered_rows = []
    for label, thresh, app in sel_models:
        sub = df[(df['threshold_name'] == thresh) & (df['grouping_approach'] == app)].copy()
        sub['model_label'] = label
        filtered_rows.append(sub)
    plot_df = pd.concat(filtered_rows)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Figure 5: Bowling Phase Pressure Exposure: Baseline PI > 60.0 vs. Z-Score Models', fontsize=14, fontweight='bold', y=0.98)

    # Panel 1: Capture Rate (% of phase legal balls classified as HP)
    ax0 = axes[0]
    sns.barplot(x='model_label', y='phase_capture_rate_pct', hue='phase', data=plot_df, 
                palette=['#9467bd', '#8c564b', '#e377c2'], ax=ax0)
    ax0.set_title('Phase High-Pressure Capture Rate (%)', fontweight='bold')
    ax0.set_xlabel('Pressure Classification Model')
    ax0.set_ylabel('% of Phase Legal Balls Classified as HP')
    ax0.set_ylim(0, 30)
    ax0.legend(title='Match Phase', loc='upper right')
    for p in ax0.patches:
        height = p.get_height()
        if height > 0:
            ax0.annotate(f"{height:.1f}%", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8.5, xytext=(0, 2), textcoords='offset points')

    # Panel 2: Share of all HP deliveries (% of total HP balls belonging to each phase)
    ax1 = axes[1]
    sns.barplot(x='model_label', y='hp_deliveries_share_pct', hue='phase', data=plot_df, 
                palette=['#9467bd', '#8c564b', '#e377c2'], ax=ax1)
    ax1.set_title('Share of Total High-Pressure Deliveries (%)', fontweight='bold')
    ax1.set_xlabel('Pressure Classification Model')
    ax1.set_ylabel('% of All HP Balls')
    ax1.set_ylim(0, 65)
    ax1.legend(title='Match Phase', loc='upper right')
    for p in ax1.patches:
        height = p.get_height()
        if height > 0:
            ax1.annotate(f"{height:.1f}%", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8.5, xytext=(0, 2), textcoords='offset points')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = OUTPUT_DIR / "fig5_bowling_phase_exposure_comparison.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Figure 5 to {out_path}")


def main():
    print("--- Step 16: Generating Comparative Visualizations ---")
    df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    clean_mask = ~((df['innings'] == 2) & (df['runs_required'] <= 0))
    df = df[clean_mask].copy()

    plot_fig1_distributions(df)
    plot_fig2_innings_comparison(df)
    plot_fig3_threshold_tradeoffs()
    plot_fig4_batting_role_exposure()
    plot_fig5_bowling_phase_exposure()
    print("All visualizations generated successfully.")


if __name__ == "__main__":
    main()
