"""
EDA Module 01: Full Population Distributions
============================================
Analyzes:
1. BRS distribution for all 816 batters.
2. BoRS distribution for all 589 bowlers.
3. Raw vs Bayesian-adjusted metric distributions.
4. Tier 1, Tier 2, and Below Threshold comparisons (KDE, Boxplots, Violins).
5. Population clustering and outlier boundaries.

Generates:
- outputs/exploratory_analysis/01_population_distributions_overview.png
- outputs/exploratory_analysis/02_raw_vs_bayesian_distributions.png
- outputs/exploratory_analysis/03_tier_comparisons_boxplots.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Styling setup
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = Path("outputs/exploratory_analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load Data
b_rank = pd.read_csv("data/processed/batter_reliability_rankings.csv")
bo_rank = pd.read_csv("data/processed/bowler_reliability_rankings.csv")

print(f"Loaded {len(b_rank)} batters and {len(bo_rank)} bowlers for Distribution Analysis.")


# =========================================================================
# CHART 1: POPULATION DISTRIBUTIONS OVERVIEW (BRS & BoRS BY TIER)
# =========================================================================
def plot_population_distributions():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 11), dpi=300)
    
    tier_colors = {
        'Tier 1: Qualified': '#27ae60',
        'Tier 2: Specialist': '#e67e22',
        'Below Threshold': '#7f8c8d'
    }
    
    # 1.1 Batter BRS Histogram & KDE by Tier
    for tier, color in tier_colors.items():
        subset = b_rank[b_rank['tier'] == tier]['brs']
        sns.histplot(subset, ax=ax1, color=color, label=f"{tier} (N={len(subset)})", 
                     kde=True, stat="density", bins=25, alpha=0.45, edgecolor=color)
    
    ax1.axvline(b_rank['brs'].mean(), color='#c0392b', linestyle='--', linewidth=1.8,
                label=f"Overall Mean ({b_rank['brs'].mean():.2f})")
    ax1.axvline(b_rank['brs'].median(), color='#2980b9', linestyle=':', linewidth=1.8,
                label=f"Overall Median ({b_rank['brs'].median():.2f})")
    ax1.set_title("A. Batter Reliability Score (BRS) Distribution Across Tiers\n(All 816 Batters)", 
                  fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel("Batter Reliability Score (BRS)", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Probability Density", fontsize=10, fontweight='bold')
    ax1.set_xlim(0, 105)
    ax1.legend(loc='upper right', frameon=True, fontsize=8.5)
    
    # 1.2 Bowler BoRS Histogram & KDE by Tier
    for tier, color in tier_colors.items():
        subset = bo_rank[bo_rank['tier'] == tier]['bors']
        sns.histplot(subset, ax=ax2, color=color, label=f"{tier} (N={len(subset)})", 
                     kde=True, stat="density", bins=25, alpha=0.45, edgecolor=color)
        
    ax2.axvline(bo_rank['bors'].mean(), color='#c0392b', linestyle='--', linewidth=1.8,
                label=f"Overall Mean ({bo_rank['bors'].mean():.2f})")
    ax2.axvline(bo_rank['bors'].median(), color='#2980b9', linestyle=':', linewidth=1.8,
                label=f"Overall Median ({bo_rank['bors'].median():.2f})")
    ax2.set_title("B. Bowler Reliability Score (BoRS) Distribution Across Tiers\n(All 589 Bowlers)", 
                  fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel("Bowler Reliability Score (BoRS)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Probability Density", fontsize=10, fontweight='bold')
    ax2.set_xlim(0, 105)
    ax2.legend(loc='upper right', frameon=True, fontsize=8.5)
    
    # 1.3 Batter Cumulative Density Function (CDF)
    for tier, color in tier_colors.items():
        subset = np.sort(b_rank[b_rank['tier'] == tier]['brs'].dropna())
        y_vals = np.arange(1, len(subset) + 1) / len(subset)
        ax3.plot(subset, y_vals, color=color, linewidth=2, label=tier)
    ax3.set_title("C. Empirical Cumulative Distribution (ECDF) of BRS", fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlabel("Batter Reliability Score (BRS)", fontsize=10, fontweight='bold')
    ax3.set_ylabel("Cumulative Probability", fontsize=10, fontweight='bold')
    ax3.set_xlim(0, 105)
    ax3.legend(loc='lower right', frameon=True, fontsize=9)
    ax3.grid(True, linestyle='--', alpha=0.5)

    # 1.4 Bowler Cumulative Density Function (CDF)
    for tier, color in tier_colors.items():
        subset = np.sort(bo_rank[bo_rank['tier'] == tier]['bors'].dropna())
        y_vals = np.arange(1, len(subset) + 1) / len(subset)
        ax4.plot(subset, y_vals, color=color, linewidth=2, label=tier)
    ax4.set_title("D. Empirical Cumulative Distribution (ECDF) of BoRS", fontsize=12, fontweight='bold', pad=10)
    ax4.set_xlabel("Bowler Reliability Score (BoRS)", fontsize=10, fontweight='bold')
    ax4.set_ylabel("Cumulative Probability", fontsize=10, fontweight='bold')
    ax4.set_xlim(0, 105)
    ax4.legend(loc='lower right', frameon=True, fontsize=9)
    ax4.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    out_file = OUT_DIR / "01_population_distributions_overview.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 2: RAW VS BAYESIAN-ADJUSTED METRIC DISTRIBUTIONS
# =========================================================================
def plot_raw_vs_bayesian():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 11), dpi=300)
    
    # 2.1 Batting Strike Rate (Raw vs Star)
    # Clip extreme raw visual range to 0-300 for readable comparison
    raw_sr = b_rank['sr_obs'].clip(0, 300)
    star_sr = b_rank['sr_star']
    sns.kdeplot(raw_sr, ax=ax1, color='#e74c3c', fill=True, alpha=0.3, label=f"Raw SR (Std={raw_sr.std():.1f})")
    sns.kdeplot(star_sr, ax=ax1, color='#2980b9', fill=True, alpha=0.3, label=f"Bayesian SR* (Std={star_sr.std():.1f})")
    ax1.axvline(114.05, color='#2c3e50', linestyle='--', linewidth=2, label="Prior (114.05)")
    ax1.set_title("A. Batter Strike Rate: Raw vs Bayesian Shrinkage\n(Massive variance compression towards Prior 114.05)", 
                  fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel("High-Pressure Strike Rate", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Density", fontsize=10, fontweight='bold')
    ax1.set_xlim(0, 260)
    ax1.legend(loc='upper right', frameon=True, fontsize=9)
    
    # 2.2 Batting Survival Rate (Raw vs Star)
    raw_surv = (100.0 - b_rank['out_obs']).clip(0, 100)
    star_surv = b_rank['surv_star']
    sns.kdeplot(raw_surv, ax=ax2, color='#e74c3c', fill=True, alpha=0.3, label=f"Raw Survival% (Std={raw_surv.std():.1f})")
    sns.kdeplot(star_surv, ax=ax2, color='#27ae60', fill=True, alpha=0.3, label=f"Bayesian Surv* (Std={star_surv.std():.1f})")
    ax2.axvline(91.70, color='#2c3e50', linestyle='--', linewidth=2, label="Prior (91.70%)")
    ax2.set_title("B. Batter Survival Rate: Raw vs Bayesian Shrinkage\n(Removes 0% and 100% small-sample flukes)", 
                  fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel("High-Pressure Survival Rate (%)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Density", fontsize=10, fontweight='bold')
    ax2.set_xlim(50, 102)
    ax2.legend(loc='upper left', frameon=True, fontsize=9)
    
    # 2.3 Bowling Economy Rate (Raw vs Star)
    raw_econ = bo_rank['econ_obs'].clip(0, 24)
    star_econ = bo_rank['econ_star']
    sns.kdeplot(raw_econ, ax=ax3, color='#8e44ad', fill=True, alpha=0.3, label=f"Raw Econ (Std={raw_econ.std():.1f})")
    sns.kdeplot(star_econ, ax=ax3, color='#16a085', fill=True, alpha=0.3, label=f"Bayesian Econ* (Std={star_econ.std():.1f})")
    ax3.axvline(9.06, color='#2c3e50', linestyle='--', linewidth=2, label="Prior (9.06 RPO)")
    ax3.set_title("C. Bowler Economy Rate: Raw vs Bayesian Shrinkage\n(Eliminates 0.0 and 24.0+ per-over small samples)", 
                  fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlabel("High-Pressure Economy Rate (RPO)", fontsize=10, fontweight='bold')
    ax3.set_ylabel("Density", fontsize=10, fontweight='bold')
    ax3.set_xlim(3, 18)
    ax3.legend(loc='upper right', frameon=True, fontsize=9)
    
    # 2.4 Bowling Wicket Rate (Raw vs Star)
    raw_wk = bo_rank['wk_pct_obs'].clip(0, 50)
    star_wk = bo_rank['wk_star']
    sns.kdeplot(raw_wk, ax=ax4, color='#d35400', fill=True, alpha=0.3, label=f"Raw Wk% (Std={raw_wk.std():.1f})")
    sns.kdeplot(star_wk, ax=ax4, color='#2980b9', fill=True, alpha=0.3, label=f"Bayesian Wk* (Std={star_wk.std():.1f})")
    ax4.axvline(6.21, color='#2c3e50', linestyle='--', linewidth=2, label="Prior (6.21%)")
    ax4.set_title("D. Bowler Wicket Rate: Raw vs Bayesian Shrinkage\n(Pulls 0-wicket bowlers up to ~6.2% league prior)", 
                  fontsize=12, fontweight='bold', pad=10)
    ax4.set_xlabel("High-Pressure Wicket Rate (%)", fontsize=10, fontweight='bold')
    ax4.set_ylabel("Density", fontsize=10, fontweight='bold')
    ax4.set_xlim(0, 25)
    ax4.legend(loc='upper right', frameon=True, fontsize=9)
    
    plt.tight_layout()
    out_file = OUT_DIR / "02_raw_vs_bayesian_distributions.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 3: TIER COMPARISONS BOXPLOTS & VIOLINS ACROSS COMPONENTS
# =========================================================================
def plot_tier_comparisons():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10), dpi=300)
    
    # Batter metrics
    b_order = ['Tier 1: Qualified', 'Tier 2: Specialist', 'Below Threshold']
    b_pal = ['#27ae60', '#e67e22', '#95a5a6']
    
    sns.boxplot(data=b_rank, x='tier', y='brs', hue='tier', order=b_order, palette=b_pal, ax=axes[0, 0], legend=False)
    axes[0, 0].set_title("A. BRS Across Tiers (Batters)", fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel("BRS Score (0-100)", fontsize=9, fontweight='bold')
    axes[0, 0].set_xlabel("")
    
    sns.boxplot(data=b_rank, x='tier', y='score_sr', hue='tier', order=b_order, palette=b_pal, ax=axes[0, 1], legend=False)
    axes[0, 1].set_title("B. Strike Rate Component (Batters)", fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel("Score SR (0-100)", fontsize=9, fontweight='bold')
    axes[0, 1].set_xlabel("")
    
    sns.boxplot(data=b_rank, x='tier', y='score_exec', hue='tier', order=b_order, palette=b_pal, ax=axes[0, 2], legend=False)
    axes[0, 2].set_title("C. Net Execution Component (Batters)", fontsize=11, fontweight='bold')
    axes[0, 2].set_ylabel("Score Exec (0-100)", fontsize=9, fontweight='bold')
    axes[0, 2].set_xlabel("")
    
    # Bowler metrics
    bo_order = ['Tier 1: Qualified', 'Tier 2: Specialist', 'Below Threshold']
    bo_pal = ['#16a085', '#d35400', '#95a5a6']
    
    sns.boxplot(data=bo_rank, x='tier', y='bors', hue='tier', order=bo_order, palette=bo_pal, ax=axes[1, 0], legend=False)
    axes[1, 0].set_title("D. BoRS Across Tiers (Bowlers)", fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel("BoRS Score (0-100)", fontsize=9, fontweight='bold')
    axes[1, 0].set_xlabel("")
    
    sns.boxplot(data=bo_rank, x='tier', y='score_econ', hue='tier', order=bo_order, palette=bo_pal, ax=axes[1, 1], legend=False)
    axes[1, 1].set_title("E. Economy Component (Bowlers)", fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel("Score Econ (0-100)", fontsize=9, fontweight='bold')
    axes[1, 1].set_xlabel("")
    
    sns.boxplot(data=bo_rank, x='tier', y='score_wk', hue='tier', order=bo_order, palette=bo_pal, ax=axes[1, 2], legend=False)
    axes[1, 2].set_title("F. Breakthrough Wicket Component (Bowlers)", fontsize=11, fontweight='bold')
    axes[1, 2].set_ylabel("Score Wk (0-100)", fontsize=9, fontweight='bold')
    axes[1, 2].set_xlabel("")
    
    for ax in axes.flat:
        ax.set_ylim(-5, 105)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.tick_params(axis='x', rotation=15)
        
    plt.tight_layout()
    out_file = OUT_DIR / "03_tier_comparisons_boxplots.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    plot_population_distributions()
    plot_raw_vs_bayesian()
    plot_tier_comparisons()
    print("Completed EDA Module 01.")
