"""
Part C — Bowler Analysis Visualizations
=======================================
Generates:
1. outputs/visualizations/11_bowler_economy_comparison.png
2. outputs/visualizations/12_bowler_wicket_rate_comparison.png
3. outputs/visualizations/13_bowler_dot_boundary_comparison.png
4. outputs/visualizations/14_top10_bowlers_bors.png
5. outputs/visualizations/15_top10_bowler_components.png
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
bo_rank = pd.read_csv("data/processed/bowler_reliability_rankings.csv")
t1_bowl = bo_rank[bo_rank['tier'] == 'Tier 1: Qualified'].sort_values('tier1_rank').copy()
print(f"Loaded {len(bo_rank)} bowlers ({len(t1_bowl)} Tier 1 Qualified).")


# =========================================================================
# CHART 11: HIGH-PRESSURE VS LOW/MOD ECONOMY RATE COMPARISON
# =========================================================================
def plot_bowler_economy_comparison():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    
    # Qualified bowlers scatter
    x = t1_bowl['low_mod_economy_rate']
    y = t1_bowl['high_economy_rate']
    sizes = t1_bowl['high_legal_balls'] * 1.5
    diff = t1_bowl['low_mod_economy_rate'] - t1_bowl['high_economy_rate'] # positive = tighter under pressure
    
    scatter = ax.scatter(x, y, s=sizes, c=diff, cmap='coolwarm_r', 
                         edgecolors='black', linewidths=0.6, alpha=0.85, zorder=3)
    
    cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label('Raw Economy Tightening (Low/Mod Econ - High Econ)', fontsize=10, fontweight='bold')
    
    # Parity Line (y = x)
    lims = [4.5, 15.5]
    ax.plot(lims, lims, color='#7f8c8d', linestyle='--', linewidth=1.5, zorder=2, 
            label='Parity Line (No Change under Pressure)')
    
    # Population Baselines
    ax.axvline(8.64, color='#2980b9', linestyle=':', linewidth=1.8, label='League Low/Mod Prior (8.64)')
    ax.axhline(9.06, color='#c0392b', linestyle=':', linewidth=1.8, label='League High-Pressure Prior (9.06)')
    
    # Favorable region shading (below parity line: high econ < low econ)
    ax.fill_between(lims, [4.5, 4.5], lims, color='#d4efdf', alpha=0.15, label='Clutch Zone (Tighter under Pressure)')
    
    # Highlight and label Top 10 Bowlers
    top10 = t1_bowl.head(10)
    for _, r in top10.iterrows():
        offset_y = 5 if r['player_name'] not in ['Trent Boult', 'Haris Rauf'] else -7
        ax.annotate(r['player_name'].split()[-1],
                    (r['low_mod_economy_rate'], r['high_economy_rate']),
                    textcoords="offset points", xytext=(0, offset_y), ha='center',
                    fontsize=8.5, fontweight='bold', color='#1b2631',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='#fcf3cf', edgecolor='#f39c12', alpha=0.9))
                    
    ax.set_title("Bowling Economy Rate: High-Pressure vs Low/Moderate-Pressure (Tier 1: N >= 60 LB)\n"
                 "Lower is better | Points below parity line indicate tighter economy under pressure", 
                 fontsize=11.5, fontweight='bold', pad=12)
    ax.set_xlabel("Low / Moderate-Pressure Economy Rate (Runs per Over)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel("High-Pressure Economy Rate (Runs per Over)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_xlim(5.0, 12.0)
    ax.set_ylim(4.5, 15.0)
    ax.legend(loc='upper left', fontsize=9, frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "11_bowler_economy_comparison.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 12: HIGH-PRESSURE VS LOW/MOD WICKET RATE COMPARISON
# =========================================================================
def plot_bowler_wicket_rate_comparison():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    
    # Wicket rate = (wickets / legal balls) * 100
    low_wk = (t1_bowl['low_mod_wickets'] / t1_bowl['low_mod_legal_balls']) * 100.0
    high_wk = (t1_bowl['high_wickets'] / t1_bowl['high_legal_balls']) * 100.0
    sizes = t1_bowl['high_legal_balls'] * 1.5
    
    scatter = ax.scatter(low_wk, high_wk, s=sizes, color='#8e44ad', 
                         edgecolors='black', linewidths=0.6, alpha=0.8, zorder=3,
                         label='Tier 1 Bowlers (N >= 60 LB)')
                         
    # Parity Line
    lims = [0, 15]
    ax.plot(lims, lims, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity Line (No Change)')
    
    # League Means
    ax.axvline(5.36, color='#2980b9', linestyle=':', linewidth=1.8, label='League Low/Mod Prior (5.36%)')
    ax.axhline(4.82, color='#c0392b', linestyle=':', linewidth=1.8, label='League High-Pressure Prior (4.82%)')
    
    # Highlight Top 10 Bowlers
    top10 = t1_bowl.head(10)
    for _, r in top10.iterrows():
        r_low_wk = (r['low_mod_wickets'] / r['low_mod_legal_balls']) * 100.0
        r_high_wk = (r['high_wickets'] / r['high_legal_balls']) * 100.0
        ax.annotate(r['player_name'].split()[-1],
                    (r_low_wk, r_high_wk), textcoords="offset points", xytext=(0, 4), ha='center',
                    fontsize=8.5, fontweight='bold', color='#4a235a',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='#ebdef0', edgecolor='#8e44ad', alpha=0.9))
                    
    ax.set_title("Breakthrough Wicket Rate: High-Pressure vs Low/Moderate-Pressure\n"
                 "Wicket Rate = (Wickets / Legal Balls) * 100 | Higher is better (Breakthrough Capability)", 
                 fontsize=11.5, fontweight='bold', pad=12)
    ax.set_xlabel("Low/Moderate-Pressure Wicket Rate (%)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel("High-Pressure Wicket Rate (%)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_xlim(1.0, 10.0)
    ax.set_ylim(0.0, 14.0)
    ax.legend(loc='upper left', fontsize=9, frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "12_bowler_wicket_rate_comparison.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 13: DOT BALL % AND BOUNDARY CONCEDED % COMPARISON
# =========================================================================
def plot_bowler_dot_boundary_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    top10 = t1_bowl.head(10).copy()
    y_pos = np.arange(len(top10))
    w = 0.38
    
    # 1. Dot Ball % (Higher is better)
    ax1.barh(y_pos - w/2, top10['low_mod_dot_pct'], height=w, color='#aed6f1', label='Low/Mod Pressure (Prior = 36.7%)')
    ax1.barh(y_pos + w/2, top10['high_dot_pct'], height=w, color='#2980b9', label='High Pressure (Prior = 39.4%)')
    ax1.axvline(39.39, color='#1b4f72', linestyle=':', label='HP League Prior (39.4%)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top10['player_name'], fontsize=9, fontweight='bold')
    ax1.invert_yaxis()
    ax1.set_xlabel("Bowling Dot Ball Percentage (%)", fontsize=11, fontweight='bold')
    ax1.set_title("Dot Ball % under Pressure (Top 10 Bowlers)\n(Higher is better: builds compounding pressure)", fontsize=11.5, fontweight='bold', pad=10)
    ax1.legend(loc='lower right', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 2. Boundary Conceded % (Lower is better)
    ax2.barh(y_pos - w/2, top10['low_mod_boundary_pct'], height=w, color='#f5b7b1', label='Low/Mod Pressure (Prior = 18.5%)')
    ax2.barh(y_pos + w/2, top10['high_boundary_pct'], height=w, color='#c0392b', label='High Pressure (Prior = 21.6%)')
    ax2.axvline(21.64, color='#78281f', linestyle=':', label='HP League Prior (21.6%)')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([]) # Hide labels on right plot
    ax2.invert_yaxis()
    ax2.set_xlabel("Boundary Conceded Percentage (%)", fontsize=11, fontweight='bold')
    ax2.set_title("Boundary Conceded % under Pressure (Top 10 Bowlers)\n(Lower is better: restricts leakage under pressure)", fontsize=11.5, fontweight='bold', pad=10)
    ax2.legend(loc='lower right', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "13_bowler_dot_boundary_comparison.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 14: TOP 10 BOWLERS RANKED BY BORS
# =========================================================================
def plot_top10_bowlers_bors():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    
    top10 = t1_bowl.head(10).iloc[::-1].copy() # Invert so #1 is at top
    y_pos = np.arange(len(top10))
    
    # Horizontal Bars
    colors = plt.cm.magma(np.linspace(0.80, 0.30, len(top10)))
    bars = ax.barh(y_pos, top10['bors'], color=colors, edgecolor='black', height=0.65, zorder=3)
    
    # Annotations on each bar
    for idx, (bar, (_, r)) in enumerate(zip(bars, top10.iterrows())):
        width = bar.get_width()
        label_text = f" BoRS: {r['bors']:.2f}  |  LB: {int(r['high_legal_balls'])}b  |  Obs Econ: {r['high_economy_rate']:.2f}  |  Bayes Econ: {r['econ_star']:.2f}  |  Wk%: {r['wk_star']:.1f}%"
        ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, label_text,
                va='center', ha='left', fontsize=8.5, fontweight='bold', color='#1b2631')
                
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{int(r['tier1_rank'])}  {r['player_name']}" for _, r in top10.iterrows()],
                       fontsize=10.5, fontweight='bold')
    ax.set_xlim(0, 115)
    ax.set_xlabel("Bowler Reliability Score (BoRS, 0–100 Scale)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_title("Top 10 Most Reliable Bowlers Under Pressure (Tier 1: N >= 60 Legal Balls Bowled)\n"
                 "Ranked by Composite BoRS (40% Economy Rate + 25% Wicket Rate + 20% Dot Ball % + 15% Clutch Tightening)", 
                 fontsize=12, fontweight='bold', pad=15)
    ax.axvline(70.0, color='#b03a2e', linestyle='--', linewidth=1.5, label='Elite Benchmark (BoRS >= 70.0)')
    ax.legend(loc='lower right', fontsize=9.5)
    ax.grid(True, linestyle='--', alpha=0.5, zorder=0)
    
    out_path = OUT_DIR / "14_top10_bowlers_bors.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 15: TOP 10 BOWLERS FOUR-COMPONENT BREAKDOWN
# =========================================================================
def plot_top10_bowler_components():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    
    top10 = t1_bowl.head(10).copy()
    names = [f"#{int(r['tier1_rank'])}\n" + r['player_name'].replace(' ', '\n', 1) for _, r in top10.iterrows()]
    x = np.arange(len(top10))
    width = 0.20
    
    # 4 Components
    c_econ = ax.bar(x - 1.5*width, top10['score_econ'], width, label='Economy Score (40%, Inverted)',  color='#2980b9', edgecolor='black', linewidth=0.5)
    c_wk   = ax.bar(x - 0.5*width, top10['score_wk'],   width, label='Wicket Breakthrough Score (25%)', color='#c0392b', edgecolor='black', linewidth=0.5)
    c_dot  = ax.bar(x + 0.5*width, top10['score_dot'],  width, label='Dot Ball Control Score (20%)',    color='#16a085', edgecolor='black', linewidth=0.5)
    c_diff = ax.bar(x + 1.5*width, top10['score_diff'], width, label='Clutch Tightening Score (15%)',   color='#8e44ad', edgecolor='black', linewidth=0.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9, fontweight='bold')
    ax.set_ylim(0, 115)
    ax.set_ylabel("Standardized Sub-Score (0–100 Scale)", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_title("Component Score Breakdown for Top 10 Bowlers Under Pressure\n"
                 "Shows the specific tactical strengths driving each bowler's high reliability rating", 
                 fontsize=12, fontweight='bold', pad=15)
    ax.axhline(50.0, color='#7f8c8d', linestyle=':', label='League Standard Baseline (50.0)')
    ax.legend(loc='upper right', fontsize=9.5, frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "15_top10_bowler_components.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


if __name__ == '__main__':
    plot_bowler_economy_comparison()
    plot_bowler_wicket_rate_comparison()
    plot_bowler_dot_boundary_comparison()
    plot_top10_bowlers_bors()
    plot_top10_bowler_components()
