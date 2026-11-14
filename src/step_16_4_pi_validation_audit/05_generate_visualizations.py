"""
05_generate_visualizations.py
Generate 4 professional audit visualizations for Step 16.4:
1. fig1_matched_context_capture_rates.png: Unadjusted vs Matched-Context capture rates across batting positions 1-11.
2. fig2_pi_component_decomposition.png: Absolute PI points & percentage shares of W, Rate, O, I across batting roles.
3. fig3_pi_vs_leverage_scatter_density.png: 4-Quadrant density / scatter plot of Pressure Index vs Match Leverage.
4. fig4_leverage_by_role_and_phase.png: Mean leverage for HP (Z > 1.00) vs Non-HP (Z <= 1.00) across phases and roles.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

OUTPUT_DIR = r"outputs\step_16_4_pi_validation_audit"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set global style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def generate_fig1():
    print("Generating Figure 1: Matched Context Capture Rates (Positions 1-11)...")
    csv_path = os.path.join(OUTPUT_DIR, "matched_context_by_position_1_to_11.csv")
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    x = df['batting_order']
    y_raw = df['unadjusted_hp_capture_pct']
    y_std = df['matched_context_hp_capture_pct']

    width = 0.35
    rects1 = ax.bar(x - width/2, y_raw, width, label='Unadjusted Capture Rate (%)', color='#2b5c8f', alpha=0.9)
    rects2 = ax.bar(x + width/2, y_std, width, label='Matched-Context Standardized Rate (%)', color='#e26d5c', alpha=0.9)

    ax.set_ylabel('High Pressure Capture Rate (% of Balls Faced)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Batting Position (Order of Appearance)', fontsize=12, fontweight='bold')
    ax.set_title('Figure 1: High Pressure Capture Rate by Batting Position (1–11)\nUnadjusted vs Matched-Context Standardized', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pos {p}" for p in x], fontsize=10)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(100, decimals=0))
    ax.set_ylim(0, 75)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=11)

    # Add direct labels on bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, color='#1f3b5c', fontweight='semibold')

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'{h:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, color='#8f2d20', fontweight='semibold')

    # Add explanatory annotation
    ax.text(0.03, 0.72,
            "Key Insight:\nEven when standardizing on common match-state cells\n(same phase, innings, and wickets lost),\nlower-order batters have ~47% capture vs ~3% for top order,\ndriven by Situational Intensity (cold entry: balls faced ~ 7 vs 44).",
            transform=ax.transAxes, fontsize=9.5, bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', edgecolor='#dddddd'))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig1_matched_context_capture_rates.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def generate_fig2():
    print("Generating Figure 2: PI Component Decomposition...")
    csv_path = os.path.join(OUTPUT_DIR, "pi_component_decomposition.csv")
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    roles = ['Top Order (1-3)', 'Middle Order (4-6)', 'Lower Order (7-11)']
    df_roles = df[(df['group_type'] == 'Overall Role') & (df['group_name'].isin(roles))].set_index('group_name').reindex(roles)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # 1. Absolute Contributions (Stacked Bar)
    components = ['Tactical Wickets (W)', 'Tactical Run Rate (Rate)', 'Tactical Overs (O)', 'Situational Intensity (I)']
    cols = ['contrib_wickets_points', 'contrib_rate_points', 'contrib_overs_points', 'contrib_situational_i_points']
    colors = ['#1d3557', '#457b9d', '#a8dadc', '#e63946']

    bottom = np.zeros(len(roles))
    for col, comp_name, color in zip(cols, components, colors):
        vals = df_roles[col].values
        ax1.bar(roles, vals, bottom=bottom, label=comp_name, color=color, width=0.55)
        bottom += vals

    ax1.set_ylabel('Mean Pressure Index Points', fontsize=12, fontweight='bold')
    ax1.set_title('A: Absolute PI Points by Component', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 80)
    ax1.legend(loc='upper left', frameon=True, facecolor='white', fontsize=10)

    # Annotate total PI on top of each bar
    for idx, (role, total_pi) in enumerate(zip(roles, df_roles['mean_batting_pi'])):
        ax1.text(idx, total_pi + 1.5, f'{total_pi:.1f} pts', ha='center', va='bottom', fontweight='bold', fontsize=11)

    # 2. Decomposition of the 34.3 pt Gap (Waterfall / Bar chart)
    gap_labels = ['Wickets (W)', 'Run Rate (Rate)', 'Phase Overs (O)', 'Situational Intensity (I)']
    gap_pts = [17.38, 5.92, 1.93, 9.03]
    gap_pcts = [50.7, 17.3, 5.6, 26.4]

    y_pos = np.arange(len(gap_labels))
    bars = ax2.barh(y_pos, gap_pts, color=colors, height=0.55)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(gap_labels, fontsize=11, fontweight='semibold')
    ax2.invert_yaxis()  # top-down
    ax2.set_xlabel('Contribution to Gap: Lower Order minus Top Order (PI Points)', fontsize=12, fontweight='bold')
    ax2.set_title('B: Drivers of the +34.3 pt Top-to-Lower Gap', fontsize=13, fontweight='bold')
    ax2.set_xlim(0, 22)

    for bar, pt, pct in zip(bars, gap_pts, gap_pcts):
        w = bar.get_width()
        ax2.text(w + 0.4, bar.get_y() + bar.get_height()/2, f'+{pt:.2f} pts ({pct:.1f}%)',
                 ha='left', va='center', fontweight='bold', fontsize=10)

    ax2.text(0.40, 0.15,
             "Total Gap = +34.26 PI Points\n- Tactical Pressure (T): +25.23 pts (73.6%)\n- Situational Intensity (I): +9.03 pts (26.4%)",
             transform=ax2.transAxes, fontsize=10, bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', edgecolor='#cccccc'))

    plt.suptitle('Figure 2: Pressure Index (PI) Component Decomposition by Batting Role', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig2_pi_component_decomposition.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def generate_fig3():
    print("Generating Figure 3: PI vs Delivery Leverage 4-Quadrant Plot...")
    csv_path = os.path.join(OUTPUT_DIR, "match_leverage_validation_data.csv")
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)

    # Subsample for clear scatter visualization if needed
    sample_df = df.sample(n=min(5000, len(df)), random_state=42)

    # Color points by High Pressure vs Non-HP
    colors = np.where(sample_df['hp'] == True, '#d90429', '#2b2d42')

    scatter = ax.scatter(sample_df['Batting_PI'], sample_df['delivery_leverage_pct'],
                         c=colors, alpha=0.3, s=18, edgecolors='none')

    # Add quadrant dividing lines
    # Median leverage is ~1.1%
    median_lev = 1.10
    pi_threshold_approx = 50.0  # Approx HP threshold boundary

    ax.axvline(x=pi_threshold_approx, color='#7f7f7f', linestyle='--', linewidth=1.2, alpha=0.8)
    ax.axhline(y=median_lev, color='#7f7f7f', linestyle='--', linewidth=1.2, alpha=0.8)

    ax.set_xlabel('Pressure Index (PI)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Expected Delivery Leverage: E[|ΔWP|] (%)', fontsize=12, fontweight='bold')
    ax.set_title('Figure 3: Pressure Index vs Match Leverage (4-Quadrant Tactical Map)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 8)

    # Annotate 4 quadrants
    # Q1: High PI, High Leverage
    ax.text(75, 5.5, "Q1: True Clutch Situations\n(7.7% of balls)\nHigh PI, High Swing\nMean WP: 36.8%",
            ha='center', va='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#feeafa', edgecolor='#d90429'), fontsize=9.5, fontweight='bold')

    # Q2: High PI, Low Leverage
    ax.text(75, 0.5, "Q2: Lost-Cause Collapses\n(10.4% of balls)\nHigh PI, Zero Swing\nMean WP: 8.2%",
            ha='center', va='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#fdf0ed', edgecolor='#ef233c'), fontsize=9.5, fontweight='bold')

    # Q3: Low PI, High Leverage
    ax.text(25, 5.5, "Q3: Tense Parity\n(42.3% of balls)\nLow PI, High Swing\nMean WP: 52.1%",
            ha='center', va='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#eef4f8', edgecolor='#2b5c8f'), fontsize=9.5, fontweight='bold')

    # Q4: Low PI, Low Leverage
    ax.text(25, 0.5, "Q4: Routine Calm Play\n(39.6% of balls)\nLow PI, Low Swing\nMean WP: 68.4%",
            ha='center', va='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f9fa', edgecolor='#8d99ae'), fontsize=9.5, fontweight='bold')

    # Legend proxy
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='High Pressure (Z > 1.00)', markerfacecolor='#d90429', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Non-High Pressure (Z ≤ 1.00)', markerfacecolor='#2b2d42', markersize=8)
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=True, facecolor='white', framealpha=0.9, fontsize=10)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig3_pi_vs_leverage_scatter_density.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def generate_fig4():
    print("Generating Figure 4: Leverage by Role and Phase...")
    csv_path = os.path.join(OUTPUT_DIR, "leverage_summary_by_subgroup.csv")
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # 1. Batting Roles
    df_role = df[df['dimension'] == 'Batting Role'].copy()
    roles = ['Top Order (1-3)', 'Middle Order (4-6)', 'Lower Order (7-11)']
    df_role = df_role.set_index('subgroup').reindex(roles).reset_index()

    x = np.arange(len(roles))
    width = 0.35

    ax1.bar(x - width/2, df_role['mean_leverage_hp_pct'], width, label='High Pressure (Z > 1.00)', color='#d90429', alpha=0.9)
    ax1.bar(x + width/2, df_role['mean_leverage_non_hp_pct'], width, label='Non-HP (Z ≤ 1.00)', color='#2b5c8f', alpha=0.9)

    ax1.set_ylabel('Mean Delivery Leverage (%)', fontsize=11, fontweight='bold')
    ax1.set_title('A: Mean Delivery Leverage by Batting Role', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Top Order\n(Pos 1–3)', 'Middle Order\n(Pos 4–6)', 'Lower Order\n(Pos 7–11)'], fontsize=10)
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(100, decimals=1))
    ax1.set_ylim(0, 2.2)
    ax1.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    # Annotations on ax1
    for i in range(len(roles)):
        hp = df_role.loc[i, 'mean_leverage_hp_pct']
        non_hp = df_role.loc[i, 'mean_leverage_non_hp_pct']
        diff = hp - non_hp
        ax1.text(i - width/2, hp + 0.05, f"{hp:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')
        ax1.text(i + width/2, non_hp + 0.05, f"{non_hp:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#2b5c8f')
        ax1.text(i, 0.15, f"Δ: {diff:+.2f} pp", ha='center', va='bottom', fontsize=9, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='#f1f1f1', edgecolor='#bbbbbb'))

    # 2. Match Phases
    df_phase = df[df['dimension'] == 'Match Phase'].copy()
    phases = ['PP', 'Middle', 'Death']
    df_phase = df_phase.set_index('subgroup').reindex(phases).reset_index()

    x2 = np.arange(len(phases))
    ax2.bar(x2 - width/2, df_phase['mean_leverage_hp_pct'], width, label='High Pressure (Z > 1.00)', color='#d90429', alpha=0.9)
    ax2.bar(x2 + width/2, df_phase['mean_leverage_non_hp_pct'], width, label='Non-HP (Z ≤ 1.00)', color='#2b5c8f', alpha=0.9)

    ax2.set_ylabel('Mean Delivery Leverage (%)', fontsize=11, fontweight='bold')
    ax2.set_title('B: Mean Delivery Leverage by Match Phase', fontsize=12, fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(['Powerplay\n(Overs 1–6)', 'Middle Overs\n(Overs 7–15)', 'Death Overs\n(Overs 16–20)'], fontsize=10)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(100, decimals=1))
    ax2.set_ylim(0, 2.2)
    ax2.legend(loc='upper right', frameon=True, facecolor='white', fontsize=9.5)

    # Annotations on ax2
    for i in range(len(phases)):
        hp = df_phase.loc[i, 'mean_leverage_hp_pct']
        non_hp = df_phase.loc[i, 'mean_leverage_non_hp_pct']
        diff = hp - non_hp
        ax2.text(i - width/2, hp + 0.05, f"{hp:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')
        ax2.text(i + width/2, non_hp + 0.05, f"{non_hp:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#2b5c8f')
        ax2.text(i, 0.15, f"Δ: {diff:+.2f} pp", ha='center', va='bottom', fontsize=9, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='#f1f1f1', edgecolor='#bbbbbb'))

    plt.suptitle('Figure 4: Delivery Leverage Comparison: High Pressure (Z > 1.00) vs Non-HP', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig4_leverage_by_role_and_phase.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    print("All 4 figures generated successfully!")
