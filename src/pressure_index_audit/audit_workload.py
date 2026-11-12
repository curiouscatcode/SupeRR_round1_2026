"""
Investigation A — Bowler Workload Loophole Audit
=================================================

This script investigates whether the existing bowler workload formula:
    B_workload = min(100, (bowler_legal_balls_in_spell_before / 12) * 100)
disproportionately inflates Death-phase pressure, misrepresents spell vs innings workload,
or assigns maximum workload to bowlers who have only bowled 2 overs.

It evaluates the experimental alternative:
    B_workload_innings = min(100, (innings_legal_balls_before / 24) * 100)

Outputs:
- outputs/pressure_index_audit/01_workload_distribution_by_phase.png
- outputs/pressure_index_audit/02_spell_vs_innings_workload_scatter.png
- outputs/pressure_index_audit/workload_bowler_impact.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/pressure_index_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_workload_audit():
    print("Loading delivery_pressure_index.csv...")
    df = pd.read_csv(DATA_DIR / "delivery_pressure_index.csv")
    total_deliveries = len(df)
    print(f"Total deliveries loaded: {total_deliveries:,}")

    # 1. Compute cumulative innings legal balls bowled before each delivery
    print("Computing cumulative innings legal balls per bowler...")
    cum_legal = df.groupby(['match_id', 'innings', 'bowler_id'])['is_legal_ball'].cumsum() - df['is_legal_ball']
    df['innings_bowler_legal_before'] = cum_legal

    # 2. Existing Spell Workload vs Experimental Innings Workload
    df['b_workload_spell'] = np.clip((df['bowler_legal_balls_in_spell_before'] / 12.0) * 100.0, 0.0, 100.0)
    df['b_workload_innings'] = np.clip((df['innings_bowler_legal_before'] / 24.0) * 100.0, 0.0, 100.0)
    df['delta_workload'] = df['b_workload_innings'] - df['b_workload_spell']

    # 3. Bowling PI Impact
    # Since PI_BO = 0.65 * T + 0.35 * (0.50 * B_workload + 0.50 * S_settling)
    # Delta Bowling PI = 0.35 * 0.50 * (b_workload_innings - b_workload_spell) = 0.175 * delta_workload
    df['delta_bowling_pi'] = 0.175 * df['delta_workload']
    df['bowling_pi_exp_workload'] = np.clip(df['Bowling_PI'] + df['delta_bowling_pi'], 0.0, 100.0)

    # 4. Statistical Analysis
    print("\n" + "="*70)
    print("INVESTIGATION A: BOWLER WORKLOAD STATISTICAL SUMMARY")
    print("="*70)

    spell_100_count = (df['b_workload_spell'] == 100.0).sum()
    innings_100_count = (df['b_workload_innings'] == 100.0).sum()

    print(f"Deliveries with Spell Workload == 100.0%:   {spell_100_count:7,} ({spell_100_count/total_deliveries*100:5.2f}%)")
    print(f"Deliveries with Innings Workload == 100.0%: {innings_100_count:7,} ({innings_100_count/total_deliveries*100:5.2f}%)")
    print(f"Overall Mean Spell Workload:   {df['b_workload_spell'].mean():.2f}%")
    print(f"Overall Mean Innings Workload: {df['b_workload_innings'].mean():.2f}%")

    print("\nPhase Breakdown:")
    phase_stats = []
    for ph in ['PP', 'Middle', 'Death']:
        sub = df[df['phase'] == ph]
        n_del = len(sub)
        s_100 = (sub['b_workload_spell'] == 100.0).sum()
        i_100 = (sub['b_workload_innings'] == 100.0).sum()
        s_mean = sub['b_workload_spell'].mean()
        i_mean = sub['b_workload_innings'].mean()
        pi_curr_mean = sub['Bowling_PI'].mean()
        pi_exp_mean = sub['bowling_pi_exp_workload'].mean()
        
        # Classification shift
        curr_hp = sub['Bowling_PI'] > 60.0
        exp_hp = sub['bowling_pi_exp_workload'] > 60.0
        gained_hp = (~curr_hp & exp_hp).sum()
        lost_hp = (curr_hp & ~exp_hp).sum()

        phase_stats.append({
            'Phase': ph,
            'Deliveries': n_del,
            'Spell_100_Count': s_100,
            'Spell_100_Pct': round(s_100 / n_del * 100, 2),
            'Innings_100_Count': i_100,
            'Innings_100_Pct': round(i_100 / n_del * 100, 2),
            'Spell_Mean_Workload': round(s_mean, 2),
            'Innings_Mean_Workload': round(i_mean, 2),
            'Curr_Bowling_PI_Mean': round(pi_curr_mean, 2),
            'Exp_Bowling_PI_Mean': round(pi_exp_mean, 2),
            'Curr_HP_Pct': round(curr_hp.mean() * 100, 2),
            'Exp_HP_Pct': round(exp_hp.mean() * 100, 2),
            'Gained_HP_Balls': gained_hp,
            'Lost_HP_Balls': lost_hp
        })
        print(f"  Phase {ph:6s} | Spell Mean: {s_mean:5.2f}% | Innings Mean: {i_mean:5.2f}% | "
              f"Spell 100%: {s_100:5,} ({s_100/n_del*100:4.1f}%) | "
              f"Bowling PI: {pi_curr_mean:.2f} -> {pi_exp_mean:.2f} | "
              f"HP Balls: {curr_hp.sum():,} -> {exp_hp.sum():,}")

    phase_summary_df = pd.DataFrame(phase_stats)

    # 5. Bowler-Level Analysis
    print("\nAggregating Bowler-Level Impact...")
    # Consider bowlers with at least 100 legal balls
    legal_df = df[df['is_legal_ball'] == 1].copy()
    
    b_group = legal_df.groupby(['bowler_id', 'bowler_name']).agg(
        total_legal_balls=('is_legal_ball', 'count'),
        curr_high_balls=('Bowling_PI', lambda s: (s > 60.0).sum()),
        exp_high_balls=('bowling_pi_exp_workload', lambda s: (s > 60.0).sum()),
        curr_mean_pi=('Bowling_PI', 'mean'),
        exp_mean_pi=('bowling_pi_exp_workload', 'mean'),
        mean_spell_workload=('b_workload_spell', 'mean'),
        mean_innings_workload=('b_workload_innings', 'mean'),
        death_balls=('phase', lambda s: (s == 'Death').sum()),
        death_pct=('phase', lambda s: (s == 'Death').mean() * 100.0)
    ).reset_index()

    b_group['delta_high_balls'] = b_group['exp_high_balls'] - b_group['curr_high_balls']
    b_group['delta_mean_pi'] = np.round(b_group['exp_mean_pi'] - b_group['curr_mean_pi'], 2)
    b_group['curr_mean_pi'] = np.round(b_group['curr_mean_pi'], 2)
    b_group['exp_mean_pi'] = np.round(b_group['exp_mean_pi'], 2)
    b_group['mean_spell_workload'] = np.round(b_group['mean_spell_workload'], 2)
    b_group['mean_innings_workload'] = np.round(b_group['mean_innings_workload'], 2)
    b_group['death_pct'] = np.round(b_group['death_pct'], 1)

    # Sort by delta_high_balls descending
    b_group_sorted = b_group.sort_values(by='delta_high_balls', ascending=False)
    b_group_sorted.to_csv(OUTPUT_DIR / "workload_bowler_impact.csv", index=False)
    print(f"Saved bowler workload impact to: {OUTPUT_DIR / 'workload_bowler_impact.csv'}")

    print("\nTop 5 Bowlers Gaining High-Pressure Balls (Death Specialists):")
    print(b_group_sorted[['bowler_name', 'total_legal_balls', 'death_balls', 'death_pct', 
                          'curr_high_balls', 'exp_high_balls', 'delta_high_balls', 'delta_mean_pi']].head(5).to_string(index=False))

    print("\nTop 5 Bowlers Losing High-Pressure Balls (Powerplay Specialists):")
    print(b_group_sorted[['bowler_name', 'total_legal_balls', 'death_balls', 'death_pct', 
                          'curr_high_balls', 'exp_high_balls', 'delta_high_balls', 'delta_mean_pi']].tail(5).to_string(index=False))

    # 6. Generate Figures
    print("\nGenerating Figure 1: Workload Distribution by Phase...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Subplot A: Boxplot comparison by phase
    plot_data = pd.melt(df[['phase', 'b_workload_spell', 'b_workload_innings']], 
                        id_vars=['phase'], 
                        value_vars=['b_workload_spell', 'b_workload_innings'],
                        var_name='Model', value_name='Workload')
    plot_data['Model'] = plot_data['Model'].map({
        'b_workload_spell': 'Baseline (Spell Workload / 12)',
        'b_workload_innings': 'Experimental (Innings Workload / 24)'
    })

    palette = {'Baseline (Spell Workload / 12)': '#e74c3c', 'Experimental (Innings Workload / 24)': '#2980b9'}
    sns.boxplot(data=plot_data, x='phase', y='Workload', hue='Model', 
                order=['PP', 'Middle', 'Death'], palette=palette, ax=axes[0], showmeans=True,
                meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black"})
    axes[0].set_title("A. Bowler Workload Distribution Across Match Phases", fontsize=13, fontweight='bold', pad=10)
    axes[0].set_xlabel("Match Phase", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("Workload Score [0 - 100]", fontsize=11, fontweight='bold')
    axes[0].legend(loc='upper left', frameon=True)

    # Annotate mean values on boxplot
    for i, ph in enumerate(['PP', 'Middle', 'Death']):
        s_m = phase_summary_df.loc[phase_summary_df['Phase'] == ph, 'Spell_Mean_Workload'].values[0]
        i_m = phase_summary_df.loc[phase_summary_df['Phase'] == ph, 'Innings_Mean_Workload'].values[0]
        axes[0].text(i - 0.2, s_m + 3, f"{s_m:.1f}%", color='#c0392b', fontweight='bold', ha='center', fontsize=9)
        axes[0].text(i + 0.2, i_m + 3, f"{i_m:.1f}%", color='#1f618d', fontweight='bold', ha='center', fontsize=9)

    # Subplot B: Workload == 100% saturation rate
    bar_df = phase_summary_df[['Phase', 'Spell_100_Pct', 'Innings_100_Pct']].melt(
        id_vars=['Phase'], var_name='Metric', value_name='Percentage'
    )
    bar_df['Metric'] = bar_df['Metric'].map({
        'Spell_100_Pct': 'Spell Workload == 100% (Cap Reached)',
        'Innings_100_Pct': 'Innings Workload == 100% (Cap Reached)'
    })

    sns.barplot(data=bar_df, x='Phase', y='Percentage', hue='Metric', 
                palette={'Spell Workload == 100% (Cap Reached)': '#e74c3c', 
                         'Innings Workload == 100% (Cap Reached)': '#2980b9'}, 
                ax=axes[1])
    axes[1].set_title("B. Artificial Saturation: Deliveries Capped at 100% Workload", fontsize=13, fontweight='bold', pad=10)
    axes[1].set_xlabel("Match Phase", fontsize=11, fontweight='bold')
    axes[1].set_ylabel("Percentage of Deliveries (%)", fontsize=11, fontweight='bold')
    axes[1].set_ylim(0, 15)
    axes[1].legend(loc='upper right', frameon=True)

    for p in axes[1].patches:
        h = p.get_height()
        if h > 0:
            axes[1].annotate(f"{h:.2f}%", (p.get_x() + p.get_width() / 2., h + 0.3),
                             ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    fig_path1 = OUTPUT_DIR / "01_workload_distribution_by_phase.png"
    plt.savefig(fig_path1, dpi=300)
    plt.close()
    print(f"Saved: {fig_path1}")

    # 7. Generate Figure 2: Spell vs Innings Workload Scatter
    print("\nGenerating Figure 2: Spell vs Innings Workload Scatter & Phase Shift...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Sample 5,000 deliveries for scatter visualization
    sample_df = df.sample(n=5000, random_state=42)

    # Scatter of Spell vs Innings Workload
    phase_colors = {'PP': '#2ecc71', 'Middle': '#f39c12', 'Death': '#e74c3c'}
    for ph, col in phase_colors.items():
        sub_s = sample_df[sample_df['phase'] == ph]
        axes[0].scatter(sub_s['b_workload_spell'], sub_s['b_workload_innings'], 
                        c=col, alpha=0.35, s=20, label=f"{ph} Deliveries")

    axes[0].plot([0, 100], [0, 100], 'k--', lw=1.5, label='Equal Line (Y=X)')
    axes[0].axvline(100, color='red', linestyle=':', alpha=0.7, label='Spell Workload Cap (12 balls)')
    axes[0].set_title("A. Spell Workload vs. Innings Workload per Delivery", fontsize=13, fontweight='bold', pad=10)
    axes[0].set_xlabel("Existing Spell Workload [min(100, balls/12 * 100)]", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("Experimental Innings Workload [min(100, balls/24 * 100)]", fontsize=11, fontweight='bold')
    axes[0].legend(loc='upper left', frameon=True, fontsize=9)

    # Subplot B: Density / Shift in Bowling PI
    sns.kdeplot(data=df, x='Bowling_PI', hue='phase', hue_order=['PP', 'Middle', 'Death'],
                palette=phase_colors, common_norm=False, fill=True, alpha=0.15, ax=axes[1], linestyle='--', label='Baseline')
    sns.kdeplot(data=df, x='bowling_pi_exp_workload', hue='phase', hue_order=['PP', 'Middle', 'Death'],
                palette=phase_colors, common_norm=False, fill=False, linewidth=2.0, ax=axes[1])
    
    axes[1].axvline(60.0, color='black', linestyle='-', lw=1.5, label='High Pressure Cutoff (60.0)')
    axes[1].set_title("B. Bowling PI Distribution Shift: Baseline (Dashed) vs. Innings Workload (Solid)", 
                      fontsize=13, fontweight='bold', pad=10)
    axes[1].set_xlabel("Bowling Pressure Index (PI)", fontsize=11, fontweight='bold')
    axes[1].set_ylabel("Density", fontsize=11, fontweight='bold')
    axes[1].set_xlim(0, 100)

    # Custom legend for axes[1]
    from matplotlib.lines import Line2D
    custom_lines = [
        Line2D([0], [0], color='black', linestyle='--', lw=1.5, label='Baseline Bowling PI'),
        Line2D([0], [0], color='black', linestyle='-', lw=2.0, label='Innings Workload Bowling PI'),
        Line2D([0], [0], color='#2ecc71', lw=2.0, label='PP'),
        Line2D([0], [0], color='#f39c12', lw=2.0, label='Middle'),
        Line2D([0], [0], color='#e74c3c', lw=2.0, label='Death'),
        Line2D([0], [0], color='black', linestyle=':', lw=1.5, label='Threshold 60.0')
    ]
    axes[1].legend(handles=custom_lines, loc='upper right', frameon=True, fontsize=9)

    plt.tight_layout()
    fig_path2 = OUTPUT_DIR / "02_spell_vs_innings_workload_scatter.png"
    plt.savefig(fig_path2, dpi=300)
    plt.close()
    print(f"Saved: {fig_path2}")

    return phase_summary_df, b_group_sorted


if __name__ == "__main__":
    run_workload_audit()
