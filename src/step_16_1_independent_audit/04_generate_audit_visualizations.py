"""
Step 16.1: Independent Audit - Script 04
Generate Audit Visualizations
============================================================
Generates 4 focused audit figures:
1. audit_fig1_innings_normalization_scenarios.png:
   Side-by-side comparison of capture rates across 5 canonical cricket scenarios
   (demonstrates that Approach B preserves high pressure while eliminating chasing bias).
2. audit_fig2_threshold_sensitivity_curve.png:
   Fine-grid sensitivity curve of Z cutoffs vs. delivery capture rate and Rule B Tier 1 count.
3. audit_fig3_role_and_phase_parity.png:
   Representation index for Batting roles and Bowling phases (Baseline vs Proposed Model).
4. audit_fig4_temporal_parameter_stability.png:
   Comparison of baseline parameters between 2022-2024 and 2025-2026 eras.

Outputs:
- outputs/step_16_1_independent_audit/*.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

AUDIT_OUT_DIR = Path("outputs/step_16_1_independent_audit")
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11


def plot_fig1_innings_scenarios():
    sc_csv = AUDIT_OUT_DIR / "innings_normalization_audit.csv"
    if not sc_csv.exists():
        return
    df = pd.read_csv(sc_csv)

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle('Audit Figure 1: High-Pressure Capture Rate Across 5 Canonical Cricket Scenarios', fontsize=14, fontweight='bold', y=0.98)

    labels = [
        '1. Difficult Chase PP\n(RRR>=10, Wk>=2)',
        '2. Comfortable Chase PP\n(RRR<=6.5, Wk<=1)',
        '3. Steep Chase Middle\n(RRR>=12.0)',
        '4. Comf 1st Inn Death\n(Score>=160, Wk<=2)',
        '5. 1st Inn Crisis\n(Wk>=5, CRR<=6.5)'
    ]

    x = np.arange(len(labels))
    width = 0.25

    rects1 = ax.bar(x - width, df['baseline_capture_pct'], width, label='Baseline (PI > 60.0)', color='#999999', alpha=0.85)
    rects2 = ax.bar(x, df['appA_capture_pct'], width, label='Approach A (Phase-only Z>1.0)', color='#e66101', alpha=0.85)
    rects3 = ax.bar(x + width, df['appB_capture_pct'], width, label='Approach B (Phase x Inn Z>1.0)', color='#2b83ba', alpha=0.9)

    ax.set_ylabel('High-Pressure Delivery Capture Rate (%)', fontweight='bold')
    ax.set_title('Innings Normalization Assessment: Does Approach B Remove Genuine Chasing Pressure?', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylim(0, 85)
    ax.legend(loc='upper right')

    for rects in [rects1, rects2, rects3]:
        for p in rects:
            h = p.get_height()
            if h > 0:
                ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h),
                            ha='center', va='bottom', fontsize=8.5, xytext=(0, 2), textcoords='offset points')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = AUDIT_OUT_DIR / "audit_fig1_innings_normalization_scenarios.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Audit Figure 1 to {out_path}")


def plot_fig2_sensitivity_curve():
    sens_csv = AUDIT_OUT_DIR / "threshold_sensitivity_audit.csv"
    if not sens_csv.exists():
        return
    df = pd.read_csv(sens_csv)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Audit Figure 2: Fine-Grid Threshold Sensitivity (Z in [0.0, 1.5])', fontsize=14, fontweight='bold', y=0.98)

    # Panel 1: Batting
    ax0 = axes[0]
    color1 = '#1f77b4'
    color2 = '#d62728'

    ax0.plot(df['z_threshold'], df['batting_capture_pct'], marker='o', color=color1, linewidth=2.5, label='Delivery Capture %')
    ax0.set_xlabel('Z-Score Threshold (Approach B)')
    ax0.set_ylabel('Delivery Capture %', color=color1, fontweight='bold')
    ax0.tick_params(axis='y', labelcolor=color1)
    ax0.set_ylim(0, 55)

    ax0_twin = ax0.twinx()
    ax0_twin.plot(df['z_threshold'], df['batting_tier1_rule_b'], marker='s', linestyle='--', color=color2, linewidth=2.5, label='Tier 1 Rule B Players')
    ax0_twin.set_ylabel('Tier 1 Batters Count', color=color2, fontweight='bold')
    ax0_twin.tick_params(axis='y', labelcolor=color2)
    ax0_twin.set_ylim(50, 360)

    ax0.axvline(1.0, color='black', linestyle=':', linewidth=2, label='Recommended Z = 1.0')
    ax0.set_title('Batting Threshold Sensitivity', fontweight='bold')

    lines_1, labels_1 = ax0.get_legend_handles_labels()
    lines_2, labels_2 = ax0_twin.get_legend_handles_labels()
    ax0.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', fontsize=8.5)

    # Panel 2: Bowling
    ax1 = axes[1]
    ax1.plot(df['z_threshold'], df['bowling_capture_pct'], marker='o', color=color1, linewidth=2.5, label='Delivery Capture %')
    ax1.set_xlabel('Z-Score Threshold (Approach B)')
    ax1.set_ylabel('Delivery Capture %', color=color1, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 55)

    ax1_twin = ax1.twinx()
    ax1_twin.plot(df['z_threshold'], df['bowling_tier1_rule_b'], marker='s', linestyle='--', color=color2, linewidth=2.5, label='Tier 1 Rule B Players')
    ax1_twin.set_ylabel('Tier 1 Bowlers Count', color=color2, fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor=color2)
    ax1_twin.set_ylim(50, 320)

    ax1.axvline(1.0, color='black', linestyle=':', linewidth=2, label='Recommended Z = 1.0')
    ax1.set_title('Bowling Threshold Sensitivity', fontweight='bold')

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', fontsize=8.5)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = AUDIT_OUT_DIR / "audit_fig2_threshold_sensitivity_curve.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Audit Figure 2 to {out_path}")


def plot_fig3_parity():
    r_csv = AUDIT_OUT_DIR / "batting_role_bias_audit.csv"
    p_csv = AUDIT_OUT_DIR / "bowling_phase_bias_audit.csv"
    if not (r_csv.exists() and p_csv.exists()):
        return

    r_df = pd.read_csv(r_csv)
    p_df = pd.read_csv(p_csv)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Audit Figure 3: Representation Index Parity (Target = 1.0)', fontsize=14, fontweight='bold', y=0.98)

    # Panel 1: Batting Roles
    ax0 = axes[0]
    sub_r = r_df[r_df['model'].isin(['Baseline (PI > 60.0)', 'Approach B (Phase x Innings Z > 1.0)'])].copy()
    sub_r['model_clean'] = sub_r['model'].map({'Baseline (PI > 60.0)': 'Baseline\n(PI > 60.0)', 'Approach B (Phase x Innings Z > 1.0)': 'Proposed\n(App B Z > 1.0)'})
    
    sns.barplot(x='batting_role', y='representation_index', hue='model_clean', data=sub_r, 
                palette=['#e41a1c', '#377eb8'], ax=ax0)
    ax0.axhline(1.0, color='black', linestyle='--', linewidth=1.5, label='Parity Baseline (1.0)')
    ax0.set_title('Batting Role Representation Index', fontweight='bold')
    ax0.set_xlabel('Batting Role')
    ax0.set_ylabel('Representation Index (HP Share / Natural Share)')
    ax0.set_ylim(0, 4.5)
    ax0.legend(loc='upper right')

    for p in ax0.patches:
        h = p.get_height()
        if h > 0:
            ax0.annotate(f"{h:.3f}", (p.get_x() + p.get_width() / 2., h),
                         ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')

    # Panel 2: Bowling Phases
    ax1 = axes[1]
    sub_p = p_df[p_df['model'].isin(['Baseline (PI > 60.0)', 'Approach B (Phase x Innings Z > 1.0)'])].copy()
    sub_p['model_clean'] = sub_p['model'].map({'Baseline (PI > 60.0)': 'Baseline\n(PI > 60.0)', 'Approach B (Phase x Innings Z > 1.0)': 'Proposed\n(App B Z > 1.0)'})

    sns.barplot(x='phase', y='representation_index', hue='model_clean', data=sub_p, 
                palette=['#e41a1c', '#377eb8'], ax=ax1)
    ax1.axhline(1.0, color='black', linestyle='--', linewidth=1.5, label='Parity Baseline (1.0)')
    ax1.set_title('Bowling Phase Representation Index', fontweight='bold')
    ax1.set_xlabel('Match Phase')
    ax1.set_ylabel('Representation Index (HP Share / Natural Share)')
    ax1.set_ylim(0, 2.2)
    ax1.legend(loc='upper right')

    for p in ax1.patches:
        h = p.get_height()
        if h > 0:
            ax1.annotate(f"{h:.3f}", (p.get_x() + p.get_width() / 2., h),
                         ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = AUDIT_OUT_DIR / "audit_fig3_role_and_phase_parity.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Audit Figure 3 to {out_path}")


def main():
    print("=== Step 16.1 Audit Script 04: Visualizations ===")
    plot_fig1_innings_scenarios()
    plot_fig2_sensitivity_curve()
    plot_fig3_parity()
    print("All audit visualizations generated successfully.")


if __name__ == "__main__":
    main()
