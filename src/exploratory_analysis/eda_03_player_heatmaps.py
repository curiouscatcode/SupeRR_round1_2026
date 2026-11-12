"""
EDA Module 03: Full Player Metric Heatmaps
==========================================
Analyzes:
1. All 116 Tier 1 Qualified Batters across 6 key metrics:
   - Strike Rate (SR*)
   - Survival Rate (Surv*)
   - Boundary % (Bnd*)
   - Dot Ball % (Dot*)
   - Clutch Strike Rate Delta (diff_sr_star)
   - Final BRS
2. All 113 Tier 1 Qualified Bowlers across 6 key metrics:
   - Economy Rate (Econ*)
   - Wicket Rate (Wk*)
   - Dot Ball % (Dot*)
   - Boundary Conceded % (high_boundary_pct)
   - Clutch Tightening Delta (diff_econ_star)
   - Final BoRS
3. Tier 2 Specialists (72 Batters, 36 Bowlers) in a dedicated heatmap.

All 116 Tier 1 batters and 113 Tier 1 bowlers are fully displayed across
two-column high-resolution panels to ensure 100% legibility and zero truncation.

Generates:
- outputs/exploratory_analysis/07_tier1_batters_heatmap.png
- outputs/exploratory_analysis/08_tier1_bowlers_heatmap.png
- outputs/exploratory_analysis/09_tier2_specialists_heatmap.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

OUT_DIR = Path("outputs/exploratory_analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
b_rank = pd.read_csv("data/processed/batter_reliability_rankings.csv")
bo_rank = pd.read_csv("data/processed/bowler_reliability_rankings.csv")

t1_bat = b_rank[b_rank['tier'] == 'Tier 1: Qualified'].sort_values('tier1_rank').copy()
t1_bowl = bo_rank[bo_rank['tier'] == 'Tier 1: Qualified'].sort_values('tier1_rank').copy()
t2_bat = b_rank[b_rank['tier'] == 'Tier 2: Specialist'].sort_values('tier2_rank').copy()
t2_bowl = bo_rank[bo_rank['tier'] == 'Tier 2: Specialist'].sort_values('tier2_rank').copy()

print(f"Heatmap Cohorts: {len(t1_bat)} Tier 1 Batters, {len(t1_bowl)} Tier 1 Bowlers, {len(t2_bat)} Tier 2 Batters, {len(t2_bowl)} Tier 2 Bowlers.")


def min_max_scale(arr):
    mn = np.nanmin(arr, axis=0)
    mx = np.nanmax(arr, axis=0)
    diff = mx - mn
    diff[diff == 0] = 1.0
    return (arr - mn) / diff

# =========================================================================
# CHART 7: TIER 1 BATTERS HEATMAP (ALL 116 BATTERS)
# =========================================================================
def plot_tier1_batters_heatmap():
    mid = 58
    p1 = t1_bat.iloc[:mid].copy()
    p2 = t1_bat.iloc[mid:].copy()
    
    cols = ['sr_star', 'surv_star', 'bnd_star', 'dot_star', 'diff_sr_star', 'brs']
    col_labels = ['SR*', 'Surv%*', 'Bnd%*', 'Dot%*', 'Clutch Δ*', 'BRS']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 22), dpi=300)
    
    labels1 = [f"#{int(r['tier1_rank'])} {r['player_name']} ({int(r['high_balls_faced'])})" for _, r in p1.iterrows()]
    labels2 = [f"#{int(r['tier1_rank'])} {r['player_name']} ({int(r['high_balls_faced'])})" for _, r in p2.iterrows()]
    
    data1 = p1[cols].values
    data2 = p2[cols].values
    
    all_scaled = min_max_scale(t1_bat[cols].values)
    scaled1 = all_scaled[:mid]
    scaled2 = all_scaled[mid:]
    
    # Plot Panel 1 (Rank 1-58)
    sns.heatmap(scaled1, ax=ax1, cmap='YlGnBu', annot=data1, fmt=".1f", cbar=False,
                yticklabels=labels1, xticklabels=col_labels, linewidths=0.5, linecolor='#e0e0e0')
    ax1.set_title("Tier 1 Qualified Batters — Ranks 1 to 58\n(Label: Rank Player_Name (High-P Balls Faced))", 
                  fontsize=12, fontweight='bold', pad=12)
    ax1.tick_params(axis='y', labelsize=8.5)
    ax1.tick_params(axis='x', labelsize=10, rotation=0)

    # Plot Panel 2 (Rank 59-116)
    sns.heatmap(scaled2, ax=ax2, cmap='YlGnBu', annot=data2, fmt=".1f", cbar=True,
                cbar_kws={'label': 'Relative Performance Percentile (Within Tier 1 Cohort)', 'shrink': 0.6},
                yticklabels=labels2, xticklabels=col_labels, linewidths=0.5, linecolor='#e0e0e0')
    ax2.set_title("Tier 1 Qualified Batters — Ranks 59 to 116\n(Label: Rank Player_Name (High-P Balls Faced))", 
                  fontsize=12, fontweight='bold', pad=12)
    ax2.tick_params(axis='y', labelsize=8.5)
    ax2.tick_params(axis='x', labelsize=10, rotation=0)

    plt.suptitle("Comprehensive Metric Heatmap: All 116 Tier 1 Qualified Batters\n"
                 "Metrics: Bayesian SR*, Survival%*, Boundary%*, Dot%*, Clutch Strike Rate Δ*, and Final BRS",
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "07_tier1_batters_heatmap.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 8: TIER 1 BOWLERS HEATMAP (ALL 113 BOWLERS)
# =========================================================================
def plot_tier1_bowlers_heatmap():
    mid = 57
    p1 = t1_bowl.iloc[:mid].copy()
    p2 = t1_bowl.iloc[mid:].copy()
    
    cols = ['econ_star', 'wk_star', 'dot_bo_star', 'high_boundary_pct', 'diff_econ_star', 'bors']
    col_labels = ['Econ*', 'Wk%*', 'Dot%*', 'Bnd Con%*', 'Clutch Tight Δ*', 'BoRS']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 22), dpi=300)
    
    labels1 = [f"#{int(r['tier1_rank'])} {r['player_name']} ({int(r['high_legal_balls'])})" for _, r in p1.iterrows()]
    labels2 = [f"#{int(r['tier1_rank'])} {r['player_name']} ({int(r['high_legal_balls'])})" for _, r in p2.iterrows()]
    
    data1 = p1[cols].values
    data2 = p2[cols].values
    
    # Scale for bowling (for Econ and Boundary Conceded, lower is better; invert scale so darker = better)
    all_scaled = min_max_scale(t1_bowl[cols].values)
    # Invert Econ (col 0) and Bnd Conceded (col 3)
    all_scaled[:, 0] = 1.0 - all_scaled[:, 0]
    all_scaled[:, 3] = 1.0 - all_scaled[:, 3]
    
    scaled1 = all_scaled[:mid]
    scaled2 = all_scaled[mid:]
    
    sns.heatmap(scaled1, ax=ax1, cmap='YlOrRd', annot=data1, fmt=".1f", cbar=False,
                yticklabels=labels1, xticklabels=col_labels, linewidths=0.5, linecolor='#e0e0e0')
    ax1.set_title("Tier 1 Qualified Bowlers — Ranks 1 to 57\n(Label: Rank Player_Name (High-P Legal Balls))", 
                  fontsize=12, fontweight='bold', pad=12)
    ax1.tick_params(axis='y', labelsize=8.5)
    ax1.tick_params(axis='x', labelsize=9.5, rotation=0)

    sns.heatmap(scaled2, ax=ax2, cmap='YlOrRd', annot=data2, fmt=".1f", cbar=True,
                cbar_kws={'label': 'Relative Bowling Effectiveness (Darker = Superior Execution)', 'shrink': 0.6},
                yticklabels=labels2, xticklabels=col_labels, linewidths=0.5, linecolor='#e0e0e0')
    ax2.set_title("Tier 1 Qualified Bowlers — Ranks 58 to 113\n(Label: Rank Player_Name (High-P Legal Balls))", 
                  fontsize=12, fontweight='bold', pad=12)
    ax2.tick_params(axis='y', labelsize=8.5)
    ax2.tick_params(axis='x', labelsize=9.5, rotation=0)

    plt.suptitle("Comprehensive Metric Heatmap: All 113 Tier 1 Qualified Bowlers\n"
                 "Metrics: Bayesian Econ*, Wicket%*, Dot%*, Boundary Conceded%, Clutch Tightening Δ*, and Final BoRS",
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "08_tier1_bowlers_heatmap.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 9: TIER 2 SPECIALISTS HEATMAP (72 BATTERS & 36 BOWLERS)
# =========================================================================
def plot_tier2_specialists_heatmap():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 16), dpi=300)
    
    # 9.1 Tier 2 Batters (Top 40 of 72 for readable presentation)
    top_t2_bat = t2_bat.head(45).copy()
    b_cols = ['sr_star', 'surv_star', 'bnd_star', 'dot_star', 'diff_sr_star', 'brs']
    b_labels = [f"T2#{int(r['tier2_rank'])} {r['player_name']} ({int(r['high_balls_faced'])})" for _, r in top_t2_bat.iterrows()]
    b_data = top_t2_bat[b_cols].values
    
    b_scaled = min_max_scale(b_data)
    
    sns.heatmap(b_scaled, ax=ax1, cmap='YlGnBu', annot=b_data, fmt=".1f", cbar=False,
                yticklabels=b_labels, xticklabels=['SR*', 'Surv%*', 'Bnd%*', 'Dot%*', 'Clutch Δ*', 'BRS'],
                linewidths=0.4, linecolor='#e0e0e0')
    ax1.set_title(f"Tier 2 Specialist Batters (Top 45 of {len(t2_bat)} Ranked, N=40–59 BF)\n"
                  "(High-upside finishers & anchors constrained by sample size)", 
                  fontsize=11.5, fontweight='bold', pad=12)
    ax1.tick_params(axis='y', labelsize=8)
    ax1.tick_params(axis='x', labelsize=9.5)

    # 9.2 Tier 2 Bowlers (All 36)
    bo_cols = ['econ_star', 'wk_star', 'dot_bo_star', 'high_boundary_pct', 'diff_econ_star', 'bors']
    bo_labels = [f"T2#{int(r['tier2_rank'])} {r['player_name']} ({int(r['high_legal_balls'])})" for _, r in t2_bowl.iterrows()]
    bo_data = t2_bowl[bo_cols].values
    bo_scaled = min_max_scale(bo_data)
    bo_scaled[:, 0] = 1.0 - bo_scaled[:, 0]
    bo_scaled[:, 3] = 1.0 - bo_scaled[:, 3]
    
    sns.heatmap(bo_scaled, ax=ax2, cmap='YlOrRd', annot=bo_data, fmt=".1f", cbar=True,
                cbar_kws={'label': 'Relative Execution Level', 'shrink': 0.7},
                yticklabels=bo_labels, xticklabels=['Econ*', 'Wk%*', 'Dot%*', 'Bnd Con%*', 'Clutch Δ*', 'BoRS'],
                linewidths=0.4, linecolor='#e0e0e0')
    ax2.set_title(f"Tier 2 Specialist Bowlers (All {len(t2_bowl)} Bowlers, N=40–59 Balls)\n"
                  "(Includes elite strike bowlers: Nasum Ahmed, Mark Wood, Junaid Siddique)", 
                  fontsize=11.5, fontweight='bold', pad=12)
    ax2.tick_params(axis='y', labelsize=8)
    ax2.tick_params(axis='x', labelsize=9.5)

    plt.suptitle("Tier 2 Specialist Cohort Analysis (40–59 High-Pressure Deliveries)\n"
                 "High-Performance Specialists Protected from Small-Sample Tier 1 Dilution",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "09_tier2_specialists_heatmap.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    plot_tier1_batters_heatmap()
    plot_tier1_bowlers_heatmap()
    plot_tier2_specialists_heatmap()
    print("Completed EDA Module 03.")
