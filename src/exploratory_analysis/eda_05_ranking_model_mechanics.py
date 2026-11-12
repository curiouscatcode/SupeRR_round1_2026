"""
EDA Module 05: Ranking Model Mechanics & Shrinkage Dynamics
===========================================================
Analyzes:
1. Mathematical impact of Empirical Bayes shrinkage (K=50).
2. Compression of raw observable metrics into Bayesian posterior estimates.
3. Component score correlations and multivariate regression influence on BRS/BoRS.
4. Identification of disproportionate feature dominance.
5. Dumbbell charts of extreme rank shifts induced by shrinkage and multi-component weighting.

Generates:
- outputs/exploratory_analysis/13_bayesian_shrinkage_mechanics.png
- outputs/exploratory_analysis/14_component_influence_and_correlations.png
- outputs/exploratory_analysis/15_shrinkage_rank_movements.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = Path("outputs/exploratory_analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
b_rank = pd.read_csv("data/processed/batter_reliability_rankings.csv")
bo_rank = pd.read_csv("data/processed/bowler_reliability_rankings.csv")

t1_bat = b_rank[b_rank['tier'] == 'Tier 1: Qualified'].copy()
t1_bowl = bo_rank[bo_rank['tier'] == 'Tier 1: Qualified'].copy()

print(f"Loaded {len(b_rank)} batters and {len(bo_rank)} bowlers for Model Mechanics Analysis.")


# =========================================================================
# CHART 13: BAYESIAN SHRINKAGE MECHANICS (RAW VS ADJUSTED SCATTER)
# =========================================================================
def plot_bayesian_shrinkage_mechanics():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300)
    
    # 13.1 Batting Strike Rate: Raw vs Bayesian Shrinkage
    # Filter batters with at least 5 balls to avoid infinity/division by zero in raw
    b_valid = b_rank[b_rank['high_balls_faced'] >= 5].copy()
    sc1 = ax1.scatter(b_valid['sr_obs'].clip(0, 300), b_valid['sr_star'],
                      c=b_valid['high_balls_faced'], cmap='viridis', s=35, alpha=0.8,
                      edgecolors='black', linewidths=0.4, zorder=3)
    cbar1 = plt.colorbar(sc1, ax=ax1, pad=0.02)
    cbar1.set_label('High-Pressure Balls Faced (N)', fontsize=9.5, fontweight='bold')
    
    # Parity and Prior lines
    lims1 = [40, 260]
    ax1.plot(lims1, lims1, color='#7f8c8d', linestyle='--', linewidth=1.5, zorder=2, label='Parity Line (No Shrinkage)')
    ax1.axhline(114.05, color='#c0392b', linestyle=':', linewidth=2, zorder=2, label='Batting Prior (114.05)')
    ax1.axvline(114.05, color='#c0392b', linestyle=':', linewidth=1, alpha=0.5, zorder=2)
    
    # Annotate high-shrinkage examples
    small_extreme = b_valid[(b_valid['high_balls_faced'] < 25) & (b_valid['sr_obs'] > 200)].head(3)
    for _, r in small_extreme.iterrows():
        name_short = r['player_name'].split()[-1]
        ax1.annotate(f"{name_short}\n(Raw {r['sr_obs']:.0f} -> {r['sr_star']:.1f})",
                     (min(r['sr_obs'], 290), r['sr_star']),
                     textcoords="offset points", xytext=(-25, 10), fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#fcf3cf', edgecolor='#f39c12', alpha=0.9))

    ax1.set_title("A. Batting Strike Rate Shrinkage: Raw Observed vs Posterior SR*\n"
                  "(Points pulled horizontally toward Prior 114.05; pull is inversely proportional to N)",
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.set_xlabel("Raw Observed High-P Strike Rate (clipped at 300)", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Bayesian Adjusted Strike Rate (SR*)", fontsize=10, fontweight='bold')
    ax1.set_xlim(lims1)
    ax1.set_ylim(80, 185)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower right', fontsize=8.5, frameon=True)

    # 13.2 Bowling Economy: Raw vs Bayesian Shrinkage
    bo_valid = bo_rank[bo_rank['high_legal_balls'] >= 5].copy()
    sc2 = ax2.scatter(bo_valid['econ_obs'].clip(2, 20), bo_valid['econ_star'],
                      c=bo_valid['high_legal_balls'], cmap='plasma', s=35, alpha=0.8,
                      edgecolors='black', linewidths=0.4, zorder=3)
    cbar2 = plt.colorbar(sc2, ax=ax2, pad=0.02)
    cbar2.set_label('High-Pressure Legal Balls Bowled (N)', fontsize=9.5, fontweight='bold')
    
    lims2 = [3.5, 16.5]
    ax2.plot(lims2, lims2, color='#7f8c8d', linestyle='--', linewidth=1.5, zorder=2, label='Parity Line (No Shrinkage)')
    ax2.axhline(9.06, color='#c0392b', linestyle=':', linewidth=2, zorder=2, label='Bowling Prior (9.06 RPO)')
    ax2.axvline(9.06, color='#c0392b', linestyle=':', linewidth=1, alpha=0.5, zorder=2)

    small_extreme_bo = bo_valid[(bo_valid['high_legal_balls'] < 25) & ((bo_valid['econ_obs'] < 5.5) | (bo_valid['econ_obs'] > 14))].head(3)
    for _, r in small_extreme_bo.iterrows():
        name_short = r['player_name'].split()[-1]
        ax2.annotate(f"{name_short}\n(Raw {r['econ_obs']:.1f} -> {r['econ_star']:.1f})",
                     (r['econ_obs'], r['econ_star']),
                     textcoords="offset points", xytext=(10, -5), fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#e8f8f5', edgecolor='#16a085', alpha=0.9))

    ax2.set_title("B. Bowling Economy Shrinkage: Raw Observed vs Posterior Econ*\n"
                  "(Extreme 0.0 or 18.0+ RPO outliers compressed toward Prior 9.06 RPO)",
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.set_xlabel("Raw Observed High-P Economy Rate (RPO)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Bayesian Adjusted Economy Rate (Econ*)", fontsize=10, fontweight='bold')
    ax2.set_xlim(lims2)
    ax2.set_ylim(6.0, 13.0)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper left', fontsize=8.5, frameon=True)

    plt.suptitle("Empirical Bayes Shrinkage Mechanics (K = 50 Deliveries Prior Weight)\n"
                 "Demonstrating How the Pipeline Regulates Small-Sample Noise Across All 1,405 Players",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "13_bayesian_shrinkage_mechanics.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 14: COMPONENT INFLUENCE & CORRELATION ANALYSIS
# =========================================================================
def plot_component_influence():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12), dpi=300)
    
    # 14.1 Batter Component Correlation Matrix
    b_cols = ['score_sr', 'score_surv', 'score_exec', 'score_diff', 'brs']
    b_labels = ['Strike Rate (40%)', 'Survival (25%)', 'Net Exec (20%)', 'Clutch Diff (15%)', 'Final BRS']
    b_corr = t1_bat[b_cols].corr()
    
    sns.heatmap(b_corr, ax=ax1, cmap='Blues', annot=True, fmt=".2f", linewidths=0.8,
                xticklabels=b_labels, yticklabels=b_labels, cbar=False)
    ax1.set_title("A. Batter Component Score Correlations (Tier 1 Qualified)\n"
                  "(Score Exec & Score SR exhibit massive r > 0.90 dominance)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.tick_params(axis='x', rotation=20, labelsize=9)
    ax1.tick_params(axis='y', labelsize=9)

    # 14.2 Bowler Component Correlation Matrix
    bo_cols = ['score_econ', 'score_wk', 'score_dot', 'score_diff', 'bors']
    bo_labels = ['Economy (40%)', 'Wicket Rate (25%)', 'Dot Ball (20%)', 'Clutch Tight (15%)', 'Final BoRS']
    bo_corr = t1_bowl[bo_cols].corr()
    
    sns.heatmap(bo_corr, ax=ax2, cmap='Purples', annot=True, fmt=".2f", linewidths=0.8,
                xticklabels=bo_labels, yticklabels=bo_labels, cbar=False)
    ax2.set_title("B. Bowler Component Score Correlations (Tier 1 Qualified)\n"
                  "(Score Econ exhibits primary r = 0.81 dominance over Wickets r = 0.61)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.tick_params(axis='x', rotation=20, labelsize=9)
    ax2.tick_params(axis='y', labelsize=9)

    # 14.3 Linear Feature Influence (Standardized Beta Coefficients on BRS)
    # Using numpy least squares for standardized regression
    X_b = t1_bat[['score_sr', 'score_surv', 'score_exec', 'score_diff']].values
    y_b = t1_bat['brs'].values
    # Standardize
    X_b_std = (X_b - X_b.mean(axis=0)) / X_b.std(axis=0)
    y_b_std = (y_b - y_b.mean()) / y_b.std()
    beta_b, _, _, _ = np.linalg.lstsq(X_b_std, y_b_std, rcond=None)
    
    comp_names_b = ['Score SR\n(Weight: 40%)', 'Score Surv\n(Weight: 25%)', 'Score Exec\n(Weight: 20%)', 'Score Diff\n(Weight: 15%)']
    colors_b = ['#2980b9', '#27ae60', '#f39c12', '#e74c3c']
    bars1 = ax3.bar(comp_names_b, beta_b, color=colors_b, edgecolor='black', alpha=0.85, width=0.55)
    for bar in bars1:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"β = {yval:.3f}", ha='center', fontsize=9.5, fontweight='bold')
    ax3.set_title("C. Batter Standardized Regression Coefficients (Effective Feature Weight)\n"
                  "Score SR (0.428) and Score Surv (0.323) govern final ranking order", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax3.set_ylabel("Standardized Coefficient (β)", fontsize=10, fontweight='bold')
    ax3.set_ylim(0, 0.55)
    ax3.grid(True, linestyle='--', alpha=0.5)

    # 14.4 Bowler Standardized Beta Coefficients on BoRS
    X_bo = t1_bowl[['score_econ', 'score_wk', 'score_dot', 'score_diff']].values
    y_bo = t1_bowl['bors'].values
    X_bo_std = (X_bo - X_bo.mean(axis=0)) / X_bo.std(axis=0)
    y_bo_std = (y_bo - y_bo.mean()) / y_bo.std()
    beta_bo, _, _, _ = np.linalg.lstsq(X_bo_std, y_bo_std, rcond=None)

    comp_names_bo = ['Score Econ\n(Weight: 40%)', 'Score Wk\n(Weight: 25%)', 'Score Dot\n(Weight: 20%)', 'Score Diff\n(Weight: 15%)']
    colors_bo = ['#8e44ad', '#d35400', '#16a085', '#c0392b']
    bars2 = ax4.bar(comp_names_bo, beta_bo, color=colors_bo, edgecolor='black', alpha=0.85, width=0.55)
    for bar in bars2:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"β = {yval:.3f}", ha='center', fontsize=9.5, fontweight='bold')
    ax4.set_title("D. Bowler Standardized Regression Coefficients (Effective Feature Weight)\n"
                  "Score Econ (0.461) and Score Wk (0.354) form the dual backbone of BoRS", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax4.set_ylabel("Standardized Coefficient (β)", fontsize=10, fontweight='bold')
    ax4.set_ylim(0, 0.55)
    ax4.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("Component Weight Sensitivity & Multi-Collinearity Diagnostic\n"
                 "Evaluating How Specified Weights (40/25/20/15) Translate Into Empirical Ranking Drivers",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "14_component_influence_and_correlations.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 15: RANK SHIFTS FROM RAW METRIC TO FINAL BRS/BORS
# =========================================================================
def plot_shrinkage_rank_movements():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), dpi=300)
    
    # 15.1 Batters: Raw SR Rank vs BRS Rank (Tier 1)
    b_shifts = t1_bat.copy()
    b_shifts['raw_sr_rank'] = b_shifts['sr_obs'].rank(ascending=False, method='min')
    b_shifts['rank_shift'] = b_shifts['raw_sr_rank'] - b_shifts['tier1_rank'] # positive = climbed ranks in BRS
    
    # Top 8 Climbers and Top 8 Fallers
    climbers_b = b_shifts.sort_values('rank_shift', ascending=False).head(8)
    fallers_b = b_shifts.sort_values('rank_shift', ascending=True).head(8)
    combined_b = pd.concat([climbers_b, fallers_b]).sort_values('rank_shift', ascending=True)
    
    y_pos1 = np.arange(len(combined_b))
    colors1 = ['#e74c3c' if s < 0 else '#27ae60' for s in combined_b['rank_shift']]
    
    ax1.hlines(y=y_pos1, xmin=combined_b['raw_sr_rank'], xmax=combined_b['tier1_rank'],
               color=colors1, linewidth=2.5, alpha=0.7, zorder=1)
    ax1.scatter(combined_b['raw_sr_rank'], y_pos1, color='#7f8c8d', s=60, zorder=2, label='Raw Observed SR Rank')
    ax1.scatter(combined_b['tier1_rank'], y_pos1, color=colors1, s=80, zorder=3, label='Final BRS Rank (After Shrinkage & Multi-Component)')
    
    for i, (_, r) in enumerate(combined_b.iterrows()):
        txt = f"+{int(r['rank_shift'])}" if r['rank_shift'] > 0 else f"{int(r['rank_shift'])}"
        x_text = (r['raw_sr_rank'] + r['tier1_rank']) / 2
        ax1.text(x_text, i + 0.28, txt, ha='center', fontsize=8, fontweight='bold', color=colors1[i])
        
    ax1.set_yticks(y_pos1)
    ax1.set_yticklabels([f"{r['player_name']} (N={int(r['high_balls_faced'])})" for _, r in combined_b.iterrows()],
                        fontsize=9, fontweight='bold')
    ax1.set_xlabel("Rank (1 = Best, 116 = Worst)", fontsize=10, fontweight='bold')
    ax1.set_title("A. Batter Rank Shifts: Raw SR Rank vs Final BRS Rank (Tier 1)\n"
                  "(Red = High raw SR dragged down by dismissals/dots; Green = Lifted by anchor survival)", 
                  fontsize=11, fontweight='bold', pad=10)
    ax1.legend(loc='lower right', frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 15.2 Bowlers: Raw Econ Rank vs BoRS Rank (Tier 1)
    bo_shifts = t1_bowl.copy()
    bo_shifts['raw_econ_rank'] = bo_shifts['econ_obs'].rank(ascending=True, method='min') # lower econ = better rank
    bo_shifts['rank_shift'] = bo_shifts['raw_econ_rank'] - bo_shifts['tier1_rank']
    
    climbers_bo = bo_shifts.sort_values('rank_shift', ascending=False).head(8)
    fallers_bo = bo_shifts.sort_values('rank_shift', ascending=True).head(8)
    combined_bo = pd.concat([climbers_bo, fallers_bo]).sort_values('rank_shift', ascending=True)

    y_pos2 = np.arange(len(combined_bo))
    colors2 = ['#e74c3c' if s < 0 else '#27ae60' for s in combined_bo['rank_shift']]

    ax2.hlines(y=y_pos2, xmin=combined_bo['raw_econ_rank'], xmax=combined_bo['tier1_rank'],
               color=colors2, linewidth=2.5, alpha=0.7, zorder=1)
    ax2.scatter(combined_bo['raw_econ_rank'], y_pos2, color='#7f8c8d', s=60, zorder=2, label='Raw Observed Economy Rank')
    ax2.scatter(combined_bo['tier1_rank'], y_pos2, color=colors2, s=80, zorder=3, label='Final BoRS Rank')

    for i, (_, r) in enumerate(combined_bo.iterrows()):
        txt = f"+{int(r['rank_shift'])}" if r['rank_shift'] > 0 else f"{int(r['rank_shift'])}"
        x_text = (r['raw_econ_rank'] + r['tier1_rank']) / 2
        ax2.text(x_text, i + 0.28, txt, ha='center', fontsize=8, fontweight='bold', color=colors2[i])

    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels([f"{r['player_name']} (N={int(r['high_legal_balls'])})" for _, r in combined_bo.iterrows()],
                        fontsize=9, fontweight='bold')
    ax2.set_xlabel("Rank (1 = Best, 113 = Worst)", fontsize=10, fontweight='bold')
    ax2.set_title("B. Bowler Rank Shifts: Raw Economy Rank vs Final BoRS Rank (Tier 1)\n"
                  "(Red = Tight economy penalised for 0 wickets; Green = Lifted by high breakthrough wicket rates)", 
                  fontsize=11, fontweight='bold', pad=10)
    ax2.legend(loc='lower right', frameon=True, fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("Shrinkage & Multi-Component Rank Shifts: Uncovering Divergence Between Raw & Regressed Order",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "15_shrinkage_rank_movements.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    plot_bayesian_shrinkage_mechanics()
    plot_component_influence()
    plot_shrinkage_rank_movements()
    print("Completed EDA Module 05.")
