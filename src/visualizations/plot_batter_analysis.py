"""
Part B — Batter Analysis Visualizations
=======================================
Generates:
1. outputs/visualizations/06_batter_strike_rate_comparison.png
2. outputs/visualizations/07_batter_survival_rate_comparison.png
3. outputs/visualizations/08_batter_boundary_dot_comparison.png
4. outputs/visualizations/09_top10_batters_brs.png
5. outputs/visualizations/10_top10_batter_components.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = Path("outputs/visualizations")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
b_rank = pd.read_csv("data/processed/batter_reliability_rankings.csv")
t1_bat = b_rank[b_rank['tier'] == 'Tier 1: Qualified'].sort_values('tier1_rank').copy()
print(f"Loaded {len(b_rank)} batters ({len(t1_bat)} Tier 1 Qualified).")


# =========================================================================
# CHART 6: HIGH-PRESSURE VS LOW/MOD STRIKE RATE COMPARISON
# =========================================================================
def plot_batter_strike_rate_comparison():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    
    # Qualified batters scatter
    x = t1_bat['low_mod_strike_rate']
    y = t1_bat['high_strike_rate']
    sizes = t1_bat['high_balls_faced'] * 1.5
    diff = t1_bat['high_strike_rate'] - t1_bat['low_mod_strike_rate']
    
    scatter = ax.scatter(x, y, s=sizes, c=diff, cmap='coolwarm', 
                         edgecolors='black', linewidths=0.6, alpha=0.85, zorder=3)
    
    cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label('Raw Strike Rate Delta (High - Low/Mod)', fontsize=10, fontweight='bold')
    
    # Parity Line (y = x)
    lims = [70, 220]
    ax.plot(lims, lims, color='#7f8c8d', linestyle='--', linewidth=1.5, zorder=2, label='Parity Line (No Change under Pressure)')
    
    # Population Baselines
    ax.axvline(143.52, color='#2980b9', linestyle=':', linewidth=1.8, label='League Low/Mod Prior (143.52)')
    ax.axhline(114.05, color='#c0392b', linestyle=':', linewidth=1.8, label='League High-Pressure Prior (114.05)')
    
    # Highlight and label Top 10 Batters
    top10 = t1_bat.head(10)
    for _, r in top10.iterrows():
        offset_y = 4 if r['player_name'] not in ['Shivam Dube', 'Cameron Green'] else -5
        ax.annotate(r['player_name'].split()[-1] if 'Dhoni' not in r['player_name'] else 'MS Dhoni',
                    (r['low_mod_strike_rate'], r['high_strike_rate']),
                    textcoords="offset points", xytext=(0, offset_y), ha='center',
                    fontsize=8.5, fontweight='bold', color='#1b2631',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='#fcf3cf', edgecolor='#f39c12', alpha=0.9))
                    
    ax.set_title("Batting Strike Rate: High-Pressure vs Low/Moderate-Pressure (Tier 1: N >= 60 BF)\n"
                 "League drop: -29.5 points | Point size proportional to High-Pressure Balls Faced", 
                 fontsize=11.5, fontweight='bold', pad=12)
    ax.set_xlabel("Low / Moderate-Pressure Strike Rate (PI <= 60.0)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel("High-Pressure Strike Rate (PI >= 61.0)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_xlim(80, 200)
    ax.set_ylim(60, 220)
    ax.legend(loc='lower right', fontsize=9, frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "06_batter_strike_rate_comparison.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 7: HIGH-PRESSURE VS LOW/MOD SURVIVAL RATE COMPARISON
# =========================================================================
def plot_batter_survival_rate_comparison():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    
    # Survival rate = 100 - dismissal_pct
    low_surv = 100.0 - t1_bat['low_mod_dismissal_pct']
    high_surv = 100.0 - t1_bat['high_dismissal_pct']
    sizes = t1_bat['high_balls_faced'] * 1.5
    
    scatter = ax.scatter(low_surv, high_surv, s=sizes, color='#27ae60', 
                         edgecolors='black', linewidths=0.6, alpha=0.8, zorder=3,
                         label='Tier 1 Batters (N >= 60 BF)')
                         
    # Parity Line
    lims = [75, 100]
    ax.plot(lims, lims, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity Line (No Survival Change)')
    
    # League Means
    ax.axvline(94.80, color='#2980b9', linestyle=':', linewidth=1.8, label='League Low/Mod Survival (94.80%)')
    ax.axhline(92.91, color='#c0392b', linestyle=':', linewidth=1.8, label='League High-Pressure Survival (92.91%)')
    
    # Highlight Top 10 Batters
    top10 = t1_bat.head(10)
    for _, r in top10.iterrows():
        r_low_s = 100.0 - r['low_mod_dismissal_pct']
        r_high_s = 100.0 - r['high_dismissal_pct']
        ax.annotate(r['player_name'].split()[-1] if 'Dhoni' not in r['player_name'] else 'MS Dhoni',
                    (r_low_s, r_high_s), textcoords="offset points", xytext=(0, 4), ha='center',
                    fontsize=8.5, fontweight='bold', color='#145a32',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='#d4efdf', edgecolor='#27ae60', alpha=0.9))
                    
    ax.set_title("Wicket Survival Rate: High-Pressure vs Low/Moderate-Pressure\n"
                 "Survival Rate = 100% - Dismissal% | League drop: -1.89 percentage points under pressure", 
                 fontsize=11.5, fontweight='bold', pad=12)
    ax.set_xlabel("Low/Moderate-Pressure Survival Rate (%)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel("High-Pressure Survival Rate (%)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_xlim(88, 99)
    ax.set_ylim(80, 100)
    ax.legend(loc='lower left', fontsize=9, frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "07_batter_survival_rate_comparison.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 8: BOUNDARY % AND DOT BALL % COMPARISON
# =========================================================================
def plot_batter_boundary_dot_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    top10 = t1_bat.head(10).copy()
    y_pos = np.arange(len(top10))
    names = [r['player_name'].replace(' ', '\n', 1) for _, r in top10.iterrows()]
    
    # 1. Boundary %
    w = 0.38
    ax1.barh(y_pos - w/2, top10['low_mod_boundary_pct'], height=w, color='#85c1e9', label='Low/Mod Pressure (Prior = 19.4%)')
    ax1.barh(y_pos + w/2, top10['high_boundary_pct'], height=w, color='#e74c3c', label='High Pressure (Prior = 14.2%)')
    ax1.axvline(14.15, color='#78281f', linestyle=':', label='HP League Prior (14.2%)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top10['player_name'], fontsize=9, fontweight='bold')
    ax1.invert_yaxis()
    ax1.set_xlabel("Boundary Percentage (%)", fontsize=11, fontweight='bold')
    ax1.set_title("Boundary % under Pressure (Top 10 Batters)\n(Elite finishers maintain 20%+ boundaries)", fontsize=11.5, fontweight='bold', pad=10)
    ax1.legend(loc='lower right', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 2. Dot Ball %
    ax2.barh(y_pos - w/2, top10['low_mod_dot_pct'], height=w, color='#a3e4d7', label='Low/Mod Pressure (Prior = 35.8%)')
    ax2.barh(y_pos + w/2, top10['high_dot_pct'], height=w, color='#d35400', label='High Pressure (Prior = 44.8%)')
    ax2.axvline(44.84, color='#6e2c00', linestyle=':', label='HP League Prior (44.8%)')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([]) # Hide labels on right plot
    ax2.invert_yaxis()
    ax2.set_xlabel("Dot Ball Percentage (%)", fontsize=11, fontweight='bold')
    ax2.set_title("Dot Ball % under Pressure (Top 10 Batters)\n(Lower is better: strike rotation mitigates pressure)", fontsize=11.5, fontweight='bold', pad=10)
    ax2.legend(loc='lower right', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "08_batter_boundary_dot_comparison.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 9: TOP 10 BATTERS RANKED BY BRS
# =========================================================================
def plot_top10_batters_brs():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    
    top10 = t1_bat.head(10).iloc[::-1].copy() # Invert so #1 is at top
    y_pos = np.arange(len(top10))
    
    # Horizontal Bars with gradient-style coloring
    colors = plt.cm.viridis(np.linspace(0.85, 0.25, len(top10)))
    bars = ax.barh(y_pos, top10['brs'], color=colors, edgecolor='black', height=0.65, zorder=3)
    
    # Annotations on each bar
    for idx, (bar, (_, r)) in enumerate(zip(bars, top10.iterrows())):
        width = bar.get_width()
        label_text = f" BRS: {r['brs']:.2f}  |  BF: {int(r['high_balls_faced'])}b  |  Obs SR: {r['high_strike_rate']:.1f}  |  Bayes SR: {r['sr_star']:.1f}  |  ΔSR: {r['diff_sr_star']:+.1f}"
        ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, label_text,
                va='center', ha='left', fontsize=8.5, fontweight='bold', color='#1b2631')
                
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{int(r['tier1_rank'])}  {r['player_name']}" for _, r in top10.iterrows()],
                       fontsize=10.5, fontweight='bold')
    ax.set_xlim(0, 115)
    ax.set_xlabel("Batter Reliability Score (BRS, 0–100 Scale)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_title("Top 10 Most Reliable Batters Under Pressure (Tier 1: N >= 60 Balls Faced)\n"
                 "Ranked by Composite BRS (40% Strike Rate + 25% Survival + 20% Net Execution + 15% Clutch Differential)", 
                 fontsize=12, fontweight='bold', pad=15)
    ax.axvline(80.0, color='#b03a2e', linestyle='--', linewidth=1.5, label='Elite Benchmark (BRS >= 80.0)')
    ax.legend(loc='lower right', fontsize=9.5)
    ax.grid(True, linestyle='--', alpha=0.5, zorder=0)
    
    out_path = OUT_DIR / "09_top10_batters_brs.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 10: TOP 10 BATTERS FOUR-COMPONENT BREAKDOWN
# =========================================================================
def plot_top10_batter_components():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    
    top10 = t1_bat.head(10).copy()
    names = [f"#{int(r['tier1_rank'])}\n" + r['player_name'].replace(' ', '\n', 1) for _, r in top10.iterrows()]
    x = np.arange(len(top10))
    width = 0.20
    
    # 4 Components
    c_sr   = ax.bar(x - 1.5*width, top10['score_sr'],   width, label='Strike Rate Score (40%)',   color='#2980b9', edgecolor='black', linewidth=0.5)
    c_surv = ax.bar(x - 0.5*width, top10['score_surv'], width, label='Survival Score (25%)',      color='#27ae60', edgecolor='black', linewidth=0.5)
    c_exec = ax.bar(x + 0.5*width, top10['score_exec'], width, label='Net Execution Score (20%)', color='#e67e22', edgecolor='black', linewidth=0.5)
    c_diff = ax.bar(x + 1.5*width, top10['score_diff'], width, label='Clutch Delta Score (15%)',  color='#8e44ad', edgecolor='black', linewidth=0.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.set_ylabel("Standardized Sub-Score (0–100 Scale)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_title("Component Score Breakdown for Top 10 Batters Under Pressure\n"
                 "Shows the specific tactical strengths driving each batter's high reliability rating", 
                 fontsize=12, fontweight='bold', pad=15)
    ax.axhline(50.0, color='#7f8c8d', linestyle=':', label='League Standard Baseline (50.0)')
    ax.legend(loc='upper right', fontsize=9.5, frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "10_top10_batter_components.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


if __name__ == '__main__':
    plot_batter_strike_rate_comparison()
    plot_batter_survival_rate_comparison()
    plot_batter_boundary_dot_comparison()
    plot_top10_batters_brs()
    plot_top10_batter_components()
