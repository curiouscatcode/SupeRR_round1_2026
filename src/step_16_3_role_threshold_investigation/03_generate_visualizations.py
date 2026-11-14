"""
Step 16.3: Investigation Script 03
Visualization Generation for Experiments 1, 2, and 3
=====================================================
Generates high-resolution figures:
- fig1_exp1_top_order_sensitivity.png
- fig2_exp2_death_threshold_sensitivity.png
- fig3_bowling_role_bors_distribution.png
- fig4_bowling_role_component_tradeoffs.png

Outputs saved to outputs/step_16_3_role_threshold_investigation/
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = Path("outputs/step_16_3_role_threshold_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set clean aesthetic style
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.titlesize'] = 14


def generate_fig1_exp1(role_df, rank_df):
    """Fig 1: Experiment 1 Top-Order Threshold Sensitivity."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Within-role capture rate across models for Top Order vs Others
    exp1_roles = role_df[role_df['experiment_family'].isin(['Control', 'Exp 1'])].copy()
    model_order = ['Control (Step 16)', 'Exp 1A (Top Z > 0.75)', 'Exp 1B (Top Z > 0.50)']
    model_labels = ['Control\n(Z > 1.00)', 'Exp 1A\n(Top Z > 0.75)', 'Exp 1B\n(Top Z > 0.50)']

    palette = {'Top Order (1-3)': '#2b5c8f', 'Middle Order (4-6)': '#d95f02', 'Lower Order (7-11)': '#7570b3'}

    sns.barplot(
        data=exp1_roles,
        x='model',
        y='within_role_capture_pct',
        hue='batting_role',
        order=model_order,
        palette=palette,
        ax=axes[0]
    )
    axes[0].set_xticks(np.arange(len(model_labels)))
    axes[0].set_xticklabels(model_labels)
    axes[0].set_title('Batting Role Capture Rate Across Thresholds')
    axes[0].set_xlabel('Model Configuration')
    axes[0].set_ylabel('Within-Role Capture Rate (%)')
    axes[0].legend(title='Batting Role', loc='upper left')

    # Annotate Top Order bars
    for p in axes[0].patches:
        height = p.get_height()
        if height > 0 and p.get_x() < 0.2 or (0.7 < p.get_x() < 1.1) or (1.7 < p.get_x() < 2.1):
            axes[0].annotate(f'{height:.1f}%',
                             (p.get_x() + p.get_width() / 2., height),
                             ha='center', va='bottom',
                             fontsize=9, xytext=(0, 3),
                             textcoords='offset points')

    # Right: Tier 1 Qualification count comparison
    qual_data = pd.DataFrame({
        'Model': model_labels,
        'Tier 1 Qualified': [206, 221, 234],
        'Tier 2 Specialist': [35, 38, 35],
        'Total Qualified': [241, 259, 269]
    })
    x = np.arange(len(model_labels))
    width = 0.35

    axes[1].bar(x - width/2, qual_data['Tier 1 Qualified'], width, label='Tier 1 Qualified', color='#1b9e77')
    axes[1].bar(x + width/2, qual_data['Tier 2 Specialist'], width, label='Tier 2 Specialist', color='#e7298a')

    axes[1].set_xticks(x)
    axes[1].set_xticks(np.arange(len(model_labels)))
    axes[1].set_xticklabels(model_labels)
    axes[1].set_title('Player Qualification Volume Under Exp 1')
    axes[1].set_xlabel('Model Configuration')
    axes[1].set_ylabel('Number of Batters')
    axes[1].legend(loc='upper left')

    for i in x:
        axes[1].annotate(f"{qual_data['Tier 1 Qualified'][i]}", (i - width/2, qual_data['Tier 1 Qualified'][i] + 3), ha='center', fontsize=9)
        axes[1].annotate(f"{qual_data['Tier 2 Specialist'][i]}", (i + width/2, qual_data['Tier 2 Specialist'][i] + 3), ha='center', fontsize=9)

    plt.suptitle('Figure 1: Experiment 1 — Top-Order Threshold Sensitivity & Qualification Impact', fontsize=13, weight='bold')
    plt.tight_layout()
    out_path = OUTPUT_DIR / "fig1_exp1_top_order_sensitivity.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Fig 1 to {out_path}")


def generate_fig2_exp2(phase_df):
    """Fig 2: Experiment 2 Death-Over Threshold Sensitivity."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    exp2_phases = phase_df[phase_df['experiment_family'].isin(['Control', 'Exp 2'])].copy()
    model_order = ['Control (Step 16)', 'Exp 2A (Death Z > 1.25)', 'Exp 2B (Death Z > 1.50)']
    model_labels = ['Control\n(Death Z > 1.00)', 'Exp 2A\n(Death Z > 1.25)', 'Exp 2B\n(Death Z > 1.50)']

    palette = {'PP': '#386cb0', 'Middle': '#fdb462', 'Death': '#e41a1c'}

    # Left: Phase Capture Rate across Exp 2
    sns.barplot(
        data=exp2_phases,
        x='model',
        y='phase_capture_pct',
        hue='phase',
        order=model_order,
        palette=palette,
        ax=axes[0]
    )
    axes[0].set_xticks(np.arange(len(model_labels)))
    axes[0].set_xticklabels(model_labels)
    axes[0].set_title('Phase Delivery Capture Rate Across Exp 2')
    axes[0].set_xlabel('Model Configuration')
    axes[0].set_ylabel('Phase Capture Rate (%)')
    axes[0].legend(title='Match Phase', loc='upper right')

    for p in axes[0].patches:
        height = p.get_height()
        if height > 0:
            axes[0].annotate(f'{height:.1f}%',
                             (p.get_x() + p.get_width() / 2., height),
                             ha='center', va='bottom',
                             fontsize=8, xytext=(0, 2),
                             textcoords='offset points')

    # Right: Phase Representation Index
    sns.barplot(
        data=exp2_phases,
        x='model',
        y='representation_index',
        hue='phase',
        order=model_order,
        palette=palette,
        ax=axes[1]
    )
    axes[1].axhline(1.0, color='gray', linestyle='--', linewidth=1.2, label='Perfect Phase Parity (1.00)')
    axes[1].set_xticks(np.arange(len(model_labels)))
    axes[1].set_xticklabels(model_labels)
    axes[1].set_title('Phase Representation Index Across Exp 2')
    axes[1].set_xlabel('Model Configuration')
    axes[1].set_ylabel('Representation Index (HP Share / Natural Share)')
    axes[1].legend(title='Match Phase', loc='upper right')

    for p in axes[1].patches:
        height = p.get_height()
        if height > 0:
            axes[1].annotate(f'{height:.2f}',
                             (p.get_x() + p.get_width() / 2., height),
                             ha='center', va='bottom',
                             fontsize=8, xytext=(0, 2),
                             textcoords='offset points')

    plt.suptitle('Figure 2: Experiment 2 — Death-Over Threshold Sensitivity & Phase Balance Distortion', fontsize=13, weight='bold')
    plt.tight_layout()
    out_path = OUTPUT_DIR / "fig2_exp2_death_threshold_sensitivity.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Fig 2 to {out_path}")


def generate_fig3_bowling_role(bias_df, diag_df):
    """Fig 3: Bowling Role BoRS Distribution and Qualification."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    t1_bowlers = diag_df[diag_df['tier'] == 'Tier 1'].copy()
    role_order = ['Powerplay Specialist', 'Middle Overs Specialist', 'Death Overs Specialist', 'Multi-Phase Bowler']
    role_short = ['Powerplay\nSpecialist', 'Middle Overs\nSpecialist', 'Death Overs\nSpecialist', 'Multi-Phase\nBowler']

    role_colors = {
        'Powerplay Specialist': '#1f77b4',
        'Middle Overs Specialist': '#ff7f0e',
        'Death Overs Specialist': '#d62728',
        'Multi-Phase Bowler': '#2ca02c'
    }

    # Left: Boxplot of BoRS for Tier 1 Bowlers by Role
    sns.boxplot(
        data=t1_bowlers,
        x='role',
        y='bors',
        hue='role',
        order=role_order,
        palette=role_colors,
        legend=False,
        ax=axes[0],
        width=0.5,
        boxprops=dict(alpha=0.8)
    )
    sns.stripplot(
        data=t1_bowlers,
        x='role',
        y='bors',
        order=role_order,
        color='black',
        alpha=0.4,
        size=4,
        jitter=0.2,
        ax=axes[0]
    )
    axes[0].set_xticks(np.arange(len(role_short)))
    axes[0].set_xticklabels(role_short)
    axes[0].set_title('BoRS Distribution by Bowling Role (Tier 1 Bowlers)')
    axes[0].set_xlabel('Bowling Role')
    axes[0].set_ylabel('Bowling Reliability Score (BoRS)')

    # Right: Qualification Volume and Top-End Representation
    x = np.arange(len(role_order))
    width = 0.25

    t1_counts = bias_df.set_index('role').loc[role_order, 'tier1_bowlers'].values
    top25_counts = bias_df.set_index('role').loc[role_order, 'top25_bowlers'].values
    top10_counts = bias_df.set_index('role').loc[role_order, 'top10_bowlers'].values

    axes[1].bar(x - width, t1_counts, width, label='Tier 1 Total', color='#4daf4a')
    axes[1].bar(x, top25_counts, width, label='Top 25', color='#377eb8')
    axes[1].bar(x + width, top10_counts, width, label='Top 10', color='#e41a1c')

    axes[1].set_xticks(x)
    axes[1].set_xticklabels(role_short)
    axes[1].set_title('Role Representation Across Tier 1 and Leaderboards')
    axes[1].set_xlabel('Bowling Role')
    axes[1].set_ylabel('Number of Bowlers')
    axes[1].legend(loc='upper right')

    for i in x:
        axes[1].annotate(f"{t1_counts[i]}", (i - width, t1_counts[i] + 1), ha='center', fontsize=9)
        axes[1].annotate(f"{top25_counts[i]}", (i, top25_counts[i] + 1), ha='center', fontsize=9)
        axes[1].annotate(f"{top10_counts[i]}", (i + width, top10_counts[i] + 1), ha='center', fontsize=9)

    plt.suptitle('Figure 3: Experiment 3 — Bowling Role Performance & Leaderboard Distribution', fontsize=13, weight='bold')
    plt.tight_layout()
    out_path = OUTPUT_DIR / "fig3_bowling_role_bors_distribution.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Fig 3 to {out_path}")


def generate_fig4_component_tradeoffs(bias_df):
    """Fig 4: BoRS Component Trade-offs Across Bowling Roles."""
    fig, ax = plt.subplots(figsize=(10, 6))

    role_order = ['Powerplay Specialist', 'Middle Overs Specialist', 'Death Overs Specialist', 'Multi-Phase Bowler']
    role_short = ['Powerplay Specialist', 'Middle Overs Specialist', 'Death Overs Specialist', 'Multi-Phase Bowler']

    sub_df = bias_df.set_index('role').loc[role_order]

    x = np.arange(len(role_order))
    width = 0.2

    c_econ = sub_df['mean_score_econ'].values
    c_wk = sub_df['mean_score_wk'].values
    c_dot = sub_df['mean_score_dot'].values
    c_diff = sub_df['mean_score_diff'].values

    b1 = ax.bar(x - 1.5*width, c_econ, width, label='Score Econ (40% Weight)', color='#2b83ba')
    b2 = ax.bar(x - 0.5*width, c_wk, width, label='Score Wicket (25% Weight)', color='#d7191c')
    b3 = ax.bar(x + 0.5*width, c_dot, width, label='Score Dot-Ball (20% Weight)', color='#abdda4')
    b4 = ax.bar(x + 1.5*width, c_diff, width, label='Score Clutch Diff (15% Weight)', color='#fdae61')

    ax.set_xticks(x)
    ax.set_xticklabels(role_short, fontsize=10)
    ax.set_title('BoRS Component Score Trade-Offs by Bowling Role (Tier 1)', fontsize=12)
    ax.set_xlabel('Bowling Role')
    ax.set_ylabel('Mean Standardized Score [0, 100]')
    ax.set_ylim(0, 80)
    ax.legend(loc='upper right', frameon=True)

    for bars in [b1, b2, b3, b4]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        (bar.get_x() + bar.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=8, xytext=(0, 2),
                        textcoords='offset points')

    plt.suptitle('Figure 4: BoRS Formula Weight Dynamics Across Bowling Roles', fontsize=13, weight='bold')
    plt.tight_layout()
    out_path = OUTPUT_DIR / "fig4_bowling_role_component_tradeoffs.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Fig 4 to {out_path}")


def main():
    print("=== Step 16.3 Script 03: Generating Publication Figures ===")
    role_df = pd.read_csv(OUTPUT_DIR / "batting_role_threshold_exposure.csv")
    phase_df = pd.read_csv(OUTPUT_DIR / "batting_phase_threshold_exposure.csv")
    rank_df = pd.read_csv(OUTPUT_DIR / "exp1_exp2_brs3_rankings_comparison.csv")
    bias_df = pd.read_csv(OUTPUT_DIR / "bowling_role_bias_summary.csv")
    diag_df = pd.read_csv(OUTPUT_DIR / "bowling_player_diagnostics_and_rankings.csv")

    generate_fig1_exp1(role_df, rank_df)
    generate_fig2_exp2(phase_df)
    generate_fig3_bowling_role(bias_df, diag_df)
    generate_fig4_component_tradeoffs(bias_df)
    print("All 4 figures generated successfully.")


if __name__ == "__main__":
    main()
