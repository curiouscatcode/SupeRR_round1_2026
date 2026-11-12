"""
EDA Module 06: Clutch Regime Shifts (High vs Low/Moderate Pressure)
===================================================================
Analyzes:
1. Full population distributions of performance changes across pressure regimes:
   - Strike rate changes for batters (ΔSR = High SR - Low SR).
   - Survival rate changes (ΔSurv = High Surv - Low Surv).
   - Boundary % and Dot ball % changes for batters.
   - Economy rate tightening for bowlers (ΔEcon = Low Econ - High Econ).
   - Wicket rate changes for bowlers (ΔWk% = High Wk% - Low Wk%).
   - Dot % and Boundary Conceded % changes for bowlers.
2. Identifies players who elevate performance under stress ("Clutch Elevators")
   versus players whose execution degrades ("Pressure Degraders").

Generates:
- outputs/exploratory_analysis/16_batter_clutch_regime_deltas.png
- outputs/exploratory_analysis/17_bowler_clutch_regime_deltas.png
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

print(f"Loaded {len(b_rank)} batters and {len(bo_rank)} bowlers for Clutch Regime Analysis.")


# =========================================================================
# CHART 16: BATTER CLUTCH REGIME DELTAS
# =========================================================================
def plot_batter_clutch_deltas():
    # Filter batters with at least 20 balls faced in both regimes for reliable delta analysis
    b_valid = b_rank[(b_rank['high_balls_faced'] >= 20) & (b_rank['low_mod_balls_faced'] >= 20)].copy()
    b_valid['surv_high'] = 100.0 - b_valid['high_dismissal_pct']
    b_valid['surv_low'] = 100.0 - b_valid['low_mod_dismissal_pct']
    b_valid['surv_delta'] = b_valid['surv_high'] - b_valid['surv_low']
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 11), dpi=300)
    
    # 16.1 Strike Rate Delta Distribution
    sns.histplot(b_valid['strike_rate_delta'], kde=True, ax=ax1, color='#2980b9', bins=30, stat='density', alpha=0.55)
    ax1.axvline(0, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity (0.0 Delta)')
    ax1.axvline(b_valid['strike_rate_delta'].mean(), color='#c0392b', linestyle='-', linewidth=2,
                label=f"Mean Delta ({b_valid['strike_rate_delta'].mean():.1f})")
    ax1.axvline(b_valid['strike_rate_delta'].median(), color='#27ae60', linestyle=':', linewidth=2,
                label=f"Median Delta ({b_valid['strike_rate_delta'].median():.1f})")
    ax1.set_title(f"A. Strike Rate Delta Distribution (N={len(b_valid)} Batters, BF >= 20 in both)\n"
                  f"(High SR - Low/Mod SR: {(b_valid['strike_rate_delta'] < 0).mean()*100:.1f}% of batters suffer a scoring drop)",
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.set_xlabel("Strike Rate Delta (High - Low/Mod)", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Density", fontsize=10, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, fontsize=8.5)

    # 16.2 Strike Rate Delta vs Boundary % Delta
    sc2 = ax2.scatter(b_valid['boundary_pct_delta'], b_valid['strike_rate_delta'],
                      c=b_valid['high_balls_faced'], cmap='viridis', s=40, edgecolors='black', linewidths=0.4, alpha=0.85)
    cbar2 = plt.colorbar(sc2, ax=ax2, pad=0.02)
    cbar2.set_label('High-P Balls Faced', fontsize=9, fontweight='bold')
    ax2.axvline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    ax2.axhline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    
    # Linear fit line
    m2, b2 = np.polyfit(b_valid['boundary_pct_delta'], b_valid['strike_rate_delta'], 1)
    x_vals2 = np.linspace(b_valid['boundary_pct_delta'].min(), b_valid['boundary_pct_delta'].max(), 50)
    ax2.plot(x_vals2, m2*x_vals2 + b2, color='#c0392b', linestyle='-', linewidth=2,
             label=f"Trend (r = {b_valid['boundary_pct_delta'].corr(b_valid['strike_rate_delta']):.2f})")
    ax2.set_title("B. Strike Rate Delta vs Boundary % Delta\n(Boundary rate suppression is the primary driver of SR collapse)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.set_xlabel("Boundary % Delta (High - Low/Mod)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Strike Rate Delta", fontsize=10, fontweight='bold')
    ax2.legend(loc='lower right', frameon=True, fontsize=8.5)

    # 16.3 Strike Rate Delta vs Dot Ball % Delta
    sc3 = ax3.scatter(b_valid['dot_pct_delta'], b_valid['strike_rate_delta'],
                      c=b_valid['high_balls_faced'], cmap='magma', s=40, edgecolors='black', linewidths=0.4, alpha=0.85)
    cbar3 = plt.colorbar(sc3, ax=ax3, pad=0.02)
    cbar3.set_label('High-P Balls Faced', fontsize=9, fontweight='bold')
    ax3.axvline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    ax3.axhline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    m3, b3 = np.polyfit(b_valid['dot_pct_delta'], b_valid['strike_rate_delta'], 1)
    x_vals3 = np.linspace(b_valid['dot_pct_delta'].min(), b_valid['dot_pct_delta'].max(), 50)
    ax3.plot(x_vals3, m3*x_vals3 + b3, color='#c0392b', linestyle='-', linewidth=2,
             label=f"Trend (r = {b_valid['dot_pct_delta'].corr(b_valid['strike_rate_delta']):.2f})")
    ax3.set_title("C. Strike Rate Delta vs Dot Ball % Delta\n(Surge in dot balls strongly compounds scoring decline)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax3.set_xlabel("Dot Ball % Delta (High - Low/Mod)", fontsize=10, fontweight='bold')
    ax3.set_ylabel("Strike Rate Delta", fontsize=10, fontweight='bold')
    ax3.legend(loc='upper right', frameon=True, fontsize=8.5)

    # 16.4 Survival Rate Delta vs Strike Rate Delta (Risk/Reward Quadrant)
    ax4.scatter(b_valid['surv_delta'], b_valid['strike_rate_delta'],
                color='#16a085', s=45, alpha=0.85, edgecolors='black', linewidths=0.4)
    ax4.axvline(0, color='#7f8c8d', linestyle='--', linewidth=1.2)
    ax4.axhline(0, color='#7f8c8d', linestyle='--', linewidth=1.2)
    
    # Quadrant annotations
    ax4.text(12, 45, "CLUTCH MASTERS\n(+SR, +Survival)", fontsize=9, fontweight='bold', color='#27ae60',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#eafaf1', edgecolor='#27ae60', alpha=0.85))
    ax4.text(-12, 45, "EXPLOSIVE SACRIFICE\n(+SR, -Survival)", fontsize=9, fontweight='bold', color='#e67e22',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#fef9e7', edgecolor='#f39c12', alpha=0.85))
    ax4.text(12, -55, "DEFENSIVE ANCHORS\n(-SR, +Survival)", fontsize=9, fontweight='bold', color='#2980b9',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#ebf5fb', edgecolor='#2980b9', alpha=0.85))
    ax4.text(-12, -55, "PRESSURE DEGRADED\n(-SR, -Survival)", fontsize=9, fontweight='bold', color='#c0392b',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#fadbd8', edgecolor='#c0392b', alpha=0.85))

    # Annotate exemplary players
    iconic_b = ['Heinrich Klaasen', 'Mahendra Singh Dhoni', 'Virat Kohli', 'Sunil Narine', 'Glenn Maxwell']
    for _, r in b_valid[b_valid['player_name'].isin(iconic_b)].iterrows():
        lbl = 'MS Dhoni' if 'Dhoni' in r['player_name'] else r['player_name'].split()[-1]
        ax4.annotate(lbl, (r['surv_delta'], r['strike_rate_delta']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#fcf3cf', edgecolor='#f39c12', alpha=0.9))

    ax4.set_title("D. Risk-Reward Trade-off: Survival Delta vs Strike Rate Delta\n(Categorizing Players into 4 Distinct Clutch Archetypes)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax4.set_xlabel("Survival Rate Delta % (High - Low/Mod)", fontsize=10, fontweight='bold')
    ax4.set_ylabel("Strike Rate Delta", fontsize=10, fontweight='bold')
    ax4.set_xlim(-20, 20)
    ax4.set_ylim(-75, 75)
    ax4.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("Batter Execution Shift Across Pressure Regimes (Low/Mod vs High Pressure)\n"
                 "Analyzing Devaluation Drivers: Boundary Shrinkage, Dot Accumulation, and Wicket Fragility",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "16_batter_clutch_regime_deltas.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 17: BOWLER CLUTCH REGIME DELTAS
# =========================================================================
def plot_bowler_clutch_deltas():
    bo_valid = bo_rank[(bo_rank['high_legal_balls'] >= 20) & (bo_rank['low_mod_legal_balls'] >= 20)].copy()
    bo_valid['high_wk_pct'] = (bo_valid['high_wickets'] / bo_valid['high_legal_balls']) * 100.0
    bo_valid['low_wk_pct'] = (bo_valid['low_mod_wickets'] / bo_valid['low_mod_legal_balls']) * 100.0
    bo_valid['wk_delta'] = bo_valid['high_wk_pct'] - bo_valid['low_wk_pct']
    # Economy tightening: positive = lower economy under pressure
    bo_valid['econ_tightening'] = bo_valid['low_mod_economy_rate'] - bo_valid['high_economy_rate']
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 11), dpi=300)
    
    # 17.1 Economy Tightening Distribution
    sns.histplot(bo_valid['econ_tightening'], kde=True, ax=ax1, color='#8e44ad', bins=30, stat='density', alpha=0.55)
    ax1.axvline(0, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity (0.0 Delta)')
    ax1.axvline(bo_valid['econ_tightening'].mean(), color='#c0392b', linestyle='-', linewidth=2,
                label=f"Mean Tightening ({bo_valid['econ_tightening'].mean():.2f} RPO)")
    ax1.axvline(bo_valid['econ_tightening'].median(), color='#27ae60', linestyle=':', linewidth=2,
                label=f"Median Tightening ({bo_valid['econ_tightening'].median():.2f} RPO)")
    ax1.set_title(f"A. Economy Rate Tightening Distribution (N={len(bo_valid)} Bowlers)\n"
                  f"(Low Econ - High Econ: {(bo_valid['econ_tightening'] > 0).mean()*100:.1f}% of bowlers tighten economy)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.set_xlabel("Economy Tightening (RPO, Positive = Superior Under Pressure)", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Density", fontsize=10, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, fontsize=8.5)

    # 17.2 Economy Tightening vs Wicket Rate Delta
    sc2 = ax2.scatter(bo_valid['wk_delta'], bo_valid['econ_tightening'],
                      c=bo_valid['high_legal_balls'], cmap='plasma', s=40, edgecolors='black', linewidths=0.4, alpha=0.85)
    cbar2 = plt.colorbar(sc2, ax=ax2, pad=0.02)
    cbar2.set_label('High-P Legal Balls Bowled', fontsize=9, fontweight='bold')
    ax2.axvline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    ax2.axhline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    
    ax2.text(5, 3.5, "GOLD STANDARD\n(+Wickets, Tighter Econ)", fontsize=9, fontweight='bold', color='#27ae60',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#eafaf1', edgecolor='#27ae60', alpha=0.85))
    ax2.text(-5, 3.5, "RESTRICTIVE SHIELD\n(-Wickets, Tighter Econ)", fontsize=9, fontweight='bold', color='#2980b9',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#ebf5fb', edgecolor='#2980b9', alpha=0.85))
    ax2.text(5, -4.5, "EXPENSIVE STRIKE\n(+Wickets, Leaked Econ)", fontsize=9, fontweight='bold', color='#e67e22',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#fef9e7', edgecolor='#f39c12', alpha=0.85))
    ax2.text(-5, -4.5, "PRESSURE BLEEDER\n(-Wickets, Leaked Econ)", fontsize=9, fontweight='bold', color='#c0392b',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#fadbd8', edgecolor='#c0392b', alpha=0.85))

    iconic_bo = ['Jasprit Bumrah', 'Rashid Khan', 'Gerald Coetzee', 'Harshal Patel', 'Trent Boult']
    for _, r in bo_valid[bo_valid['player_name'].isin(iconic_bo)].iterrows():
        ax2.annotate(r['player_name'].split()[-1], (r['wk_delta'], r['econ_tightening']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#fcf3cf', edgecolor='#f39c12', alpha=0.9))

    ax2.set_title("B. Bowler Clutch Quadrants: Wicket Delta vs Economy Tightening\n"
                  "(Distinguishing Restrictive Anchors from Expensive Strike Bowlers)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.set_xlabel("Wicket Rate Delta % (High - Low/Mod)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Economy Tightening (Low Econ - High Econ)", fontsize=10, fontweight='bold')
    ax2.set_xlim(-10, 15)
    ax2.set_ylim(-6, 6)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # 17.3 Dot Ball % Delta vs Boundary Conceded % Delta
    sc3 = ax3.scatter(bo_valid['boundary_pct_delta'], bo_valid['dot_pct_delta'],
                      c=bo_valid['high_legal_balls'], cmap='coolwarm', s=40, edgecolors='black', linewidths=0.4, alpha=0.85)
    cbar3 = plt.colorbar(sc3, ax=ax3, pad=0.02)
    cbar3.set_label('High-P Legal Balls', fontsize=9, fontweight='bold')
    ax3.axvline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    ax3.axhline(0, color='#7f8c8d', linestyle='--', linewidth=1)
    ax3.set_title("C. Pressure Creation: Dot % Delta vs Boundary Conceded Delta\n(Ideal quadrant: High dots + Suppressed boundaries in top-left)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax3.set_xlabel("Boundary Conceded % Delta (High - Low/Mod)", fontsize=10, fontweight='bold')
    ax3.set_ylabel("Dot Ball % Delta (High - Low/Mod)", fontsize=10, fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.5)

    # 17.4 Tier Comparison of Economy Tightening
    sns.boxplot(data=bo_valid, x='tier', y='econ_tightening', ax=ax4,
                palette=['#16a085', '#d35400', '#95a5a6'], hue='tier', legend=False)
    ax4.axhline(0, color='#c0392b', linestyle='--', linewidth=1.5, label='Parity (0.0 Tightening)')
    ax4.set_title("D. Economy Tightening Comparison Across Tiers\n(Tier 1 demonstrates stable containment; Tier 2 shows high-variance upside)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax4.set_xlabel("")
    ax4.set_ylabel("Economy Tightening (RPO)", fontsize=10, fontweight='bold')
    ax4.set_ylim(-6, 7)
    ax4.grid(True, linestyle='--', alpha=0.5)
    ax4.legend(loc='upper right', fontsize=8.5)

    plt.suptitle("Bowler Execution Shift Across Pressure Regimes (Low/Mod vs High Pressure)\n"
                 "Evaluating Run Containment, Breakthrough Capability, and Resistance Under Match Stress",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "17_bowler_clutch_regime_deltas.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    plot_batter_clutch_deltas()
    plot_bowler_clutch_deltas()
    print("Completed EDA Module 06.")
