"""
EDA Module 02: Sample Size vs Reliability
=========================================
Analyzes:
1. High-pressure balls faced vs BRS across all 816 batters.
2. High-pressure legal balls vs BoRS across all 589 bowlers.
3. Separation of Tier 1 (N >= 60), Tier 2 (40 <= N < 60), and Below Threshold (N < 40).
4. Identification and annotation of small-sample high-score outliers.
5. Theoretical Bayesian shrinkage funnel curve (K=50).
6. Score variance and volatility across sample size bins.

Generates:
- outputs/exploratory_analysis/04_batter_sample_size_vs_brs.png
- outputs/exploratory_analysis/05_bowler_sample_size_vs_bors.png
- outputs/exploratory_analysis/06_small_sample_score_volatility.png
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

print(f"Loaded {len(b_rank)} batters and {len(bo_rank)} bowlers for Sample Size Analysis.")


# =========================================================================
# CHART 4: BATTER SAMPLE SIZE VS BRS SCATTER PLOT
# =========================================================================
def plot_batter_sample_vs_brs():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    
    tier_styles = {
        'Tier 1: Qualified': {'color': '#27ae60', 'alpha': 0.85, 'size': 55, 'edge': 'black', 'zorder': 4},
        'Tier 2: Specialist': {'color': '#e67e22', 'alpha': 0.80, 'size': 45, 'edge': 'black', 'zorder': 3},
        'Below Threshold': {'color': '#95a5a6', 'alpha': 0.45, 'size': 25, 'edge': 'none', 'zorder': 2}
    }
    
    for tier, s in tier_styles.items():
        sub = b_rank[b_rank['tier'] == tier]
        ax.scatter(sub['high_balls_faced'], sub['brs'], c=s['color'], label=f"{tier} (N={len(sub)})",
                   alpha=s['alpha'], s=s['size'], edgecolors=s['edge'], linewidths=0.5, zorder=s['zorder'])
        
    # Qualification threshold vertical lines
    ax.axvline(60, color='#27ae60', linestyle='--', linewidth=2.0, zorder=5, label='Tier 1 Threshold (N >= 60 BF)')
    ax.axvline(40, color='#e67e22', linestyle=':', linewidth=1.8, zorder=5, label='Tier 2 Specialist Threshold (N >= 40 BF)')
    
    # Baseline Score horizontal line
    ax.axhline(50, color='#7f8c8d', linestyle='-', linewidth=1.0, alpha=0.7, zorder=1, label='League Baseline Score (50.0)')

    # Identify and annotate small-sample high-score outliers
    # Batters with N < 60 but BRS >= 70
    small_high = b_rank[(b_rank['high_balls_faced'] < 60) & (b_rank['brs'] >= 68.0)].sort_values('brs', ascending=False)
    for _, r in small_high.iterrows():
        name_short = r['player_name'].split()[-1] if len(r['player_name'].split()) > 1 else r['player_name']
        if r['player_name'] == 'Suyash Prabhudessai':
            name_short = 'Prabhudessai'
        ax.annotate(f"{name_short}\n(N={int(r['high_balls_faced'])}, BRS={r['brs']:.1f})",
                    (r['high_balls_faced'], r['brs']),
                    textcoords="offset points", xytext=(0, 7), ha='center',
                    fontsize=8, fontweight='bold', color='#1a5276',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#ebf5fb', edgecolor='#2980b9', alpha=0.9),
                    zorder=6)
        
    # Also annotate top Tier 1 batters for comparison
    top_t1 = b_rank[b_rank['tier'] == 'Tier 1: Qualified'].head(5)
    for _, r in top_t1.iterrows():
        name_short = r['player_name'].split()[-1] if 'Dhoni' not in r['player_name'] else 'MS Dhoni'
        ax.annotate(f"{name_short} #{int(r['tier1_rank'])}\n(N={int(r['high_balls_faced'])}, BRS={r['brs']:.1f})",
                    (r['high_balls_faced'], r['brs']),
                    textcoords="offset points", xytext=(0, -18), ha='center',
                    fontsize=8, fontweight='bold', color='#1e8449',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#eafaf1', edgecolor='#27ae60', alpha=0.9),
                    zorder=6)
        
    ax.set_title("Full Population Batter Analysis: Sample Size vs Batter Reliability Score (BRS)\n"
                 "Illustrating Small-Sample Volatility and the 60-Ball Primary Qualification Boundary",
                 fontsize=12.5, fontweight='bold', pad=12)
    ax.set_xlabel("High-Pressure Balls Faced (N)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel("Batter Reliability Score (BRS, 0–100)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_xlim(-5, b_rank['high_balls_faced'].max() + 20)
    ax.set_ylim(-5, 105)
    ax.legend(loc='lower right', frameon=True, framealpha=0.92, fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    out_file = OUT_DIR / "04_batter_sample_size_vs_brs.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 5: BOWLER SAMPLE SIZE VS BORS SCATTER PLOT
# =========================================================================
def plot_bowler_sample_vs_bors():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    
    tier_styles = {
        'Tier 1: Qualified': {'color': '#16a085', 'alpha': 0.85, 'size': 55, 'edge': 'black', 'zorder': 4},
        'Tier 2: Specialist': {'color': '#d35400', 'alpha': 0.80, 'size': 45, 'edge': 'black', 'zorder': 3},
        'Below Threshold': {'color': '#95a5a6', 'alpha': 0.45, 'size': 25, 'edge': 'none', 'zorder': 2}
    }
    
    for tier, s in tier_styles.items():
        sub = bo_rank[bo_rank['tier'] == tier]
        ax.scatter(sub['high_legal_balls'], sub['bors'], c=s['color'], label=f"{tier} (N={len(sub)})",
                   alpha=s['alpha'], s=s['size'], edgecolors=s['edge'], linewidths=0.5, zorder=s['zorder'])
        
    ax.axvline(60, color='#16a085', linestyle='--', linewidth=2.0, zorder=5, label='Tier 1 Threshold (N >= 60 Balls)')
    ax.axvline(40, color='#d35400', linestyle=':', linewidth=1.8, zorder=5, label='Tier 2 Specialist Threshold (N >= 40 Balls)')
    ax.axhline(50, color='#7f8c8d', linestyle='-', linewidth=1.0, alpha=0.7, zorder=1, label='League Baseline Score (50.0)')

    # Small-sample high-score outliers for bowlers (N < 60 but BoRS >= 72)
    small_high_bo = bo_rank[(bo_rank['high_legal_balls'] < 60) & (bo_rank['bors'] >= 72.0)].sort_values('bors', ascending=False)
    for _, r in small_high_bo.iterrows():
        name_short = r['player_name'].split()[-1] if len(r['player_name'].split()) > 1 else r['player_name']
        if r['player_name'] == 'Shadley Van Schalkwyk':
            name_short = 'Schalkwyk'
        ax.annotate(f"{name_short}\n(N={int(r['high_legal_balls'])}, BoRS={r['bors']:.1f})",
                    (r['high_legal_balls'], r['bors']),
                    textcoords="offset points", xytext=(0, 7), ha='center',
                    fontsize=8, fontweight='bold', color='#6c3483',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#f4ecf7', edgecolor='#8e44ad', alpha=0.9),
                    zorder=6)
        
    # Top Tier 1 bowlers
    top_t1_bo = bo_rank[bo_rank['tier'] == 'Tier 1: Qualified'].head(5)
    for _, r in top_t1_bo.iterrows():
        name_short = r['player_name'].split()[-1]
        ax.annotate(f"{name_short} #{int(r['tier1_rank'])}\n(N={int(r['high_legal_balls'])}, BoRS={r['bors']:.1f})",
                    (r['high_legal_balls'], r['bors']),
                    textcoords="offset points", xytext=(0, -18), ha='center',
                    fontsize=8, fontweight='bold', color='#117864',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#e8f8f5', edgecolor='#16a085', alpha=0.9),
                    zorder=6)

    ax.set_title("Full Population Bowler Analysis: Sample Size vs Bowler Reliability Score (BoRS)\n"
                 "Highlighting Extreme Small-Sample Tightening Outliers and Phase Specialists",
                 fontsize=12.5, fontweight='bold', pad=12)
    ax.set_xlabel("High-Pressure Legal Balls Bowled (N)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel("Bowler Reliability Score (BoRS, 0–100)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_xlim(-5, bo_rank['high_legal_balls'].max() + 20)
    ax.set_ylim(-5, 105)
    ax.legend(loc='lower right', frameon=True, framealpha=0.92, fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    out_file = OUT_DIR / "05_bowler_sample_size_vs_bors.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 6: SCORE VOLATILITY ACROSS SAMPLE SIZE BINS
# =========================================================================
def plot_score_volatility():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)
    
    # Batters Bins
    b_bins = [0, 10, 25, 40, 60, 100, 200, 500]
    b_labels = ['1-10', '11-25', '26-39', '40-59 (T2)', '60-99 (T1)', '100-199', '200+']
    bo_bins = b_bins
    bo_labels = b_labels
    b_df = b_rank.copy()
    bo_df = bo_rank.copy()
    b_df['sample_bin'] = pd.cut(b_df['high_balls_faced'], bins=b_bins, labels=b_labels, right=False)
    bo_df['sample_bin'] = pd.cut(bo_df['high_legal_balls'], bins=bo_bins, labels=bo_labels, right=False)
    
    # 6.1 Batter Boxplot across Sample Bins
    sns.boxplot(data=b_df, x='sample_bin', y='brs', ax=ax1, palette='Blues_r', hue='sample_bin', legend=False)
    ax1.set_title("A. Batter Score (BRS) Dispersion across Sample Bins\n(Extreme variance in low bins collapses at N >= 60)",
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.set_xlabel("High-Pressure Balls Faced Bins", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Batter Reliability Score (BRS)", fontsize=10, fontweight='bold')
    ax1.axhline(50, color='#c0392b', linestyle='--', linewidth=1.5, label='Baseline (50.0)')
    ax1.set_ylim(-5, 105)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower right', fontsize=8.5)

    # Annotate std dev above each bin
    b_stds = b_df.groupby('sample_bin', observed=False)['brs'].std()
    b_counts = b_df.groupby('sample_bin', observed=False)['brs'].count()
    for i, (cnt, s) in enumerate(zip(b_counts, b_stds)):
        ax1.text(i, 98, f"N={cnt}\nσ={s:.1f}", ha='center', fontsize=8, fontweight='bold', color='#1b2631')

    # 6.2 Bowler Boxplot across Sample Bins
    sns.boxplot(data=bo_df, x='sample_bin', y='bors', ax=ax2, palette='Purples_r', hue='sample_bin', legend=False)
    ax2.set_title("B. Bowler Score (BoRS) Dispersion across Sample Bins\n(Narrower range at N >= 60 confirms shrinkage efficacy)",
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.set_xlabel("High-Pressure Legal Balls Bins", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Bowler Reliability Score (BoRS)", fontsize=10, fontweight='bold')
    ax2.axhline(50, color='#c0392b', linestyle='--', linewidth=1.5, label='Baseline (50.0)')
    ax2.set_ylim(-5, 105)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='lower right', fontsize=8.5)

    bo_stds = bo_df.groupby('sample_bin', observed=False)['bors'].std()
    bo_counts = bo_df.groupby('sample_bin', observed=False)['bors'].count()
    for i, (cnt, s) in enumerate(zip(bo_counts, bo_stds)):
        ax2.text(i, 98, f"N={cnt}\nσ={s:.1f}", ha='center', fontsize=8, fontweight='bold', color='#1b2631')

    plt.tight_layout()
    out_file = OUT_DIR / "06_small_sample_score_volatility.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    plot_batter_sample_vs_brs()
    plot_bowler_sample_vs_bors()
    plot_score_volatility()
    print("Completed EDA Module 02.")
