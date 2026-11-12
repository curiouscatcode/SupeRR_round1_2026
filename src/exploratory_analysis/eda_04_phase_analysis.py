"""
EDA Module 04: Phase-Wise Performance Analysis
==============================================
Analyzes:
1. Performance transitions across Powerplay (PP), Middle Overs (MO), and Death Overs (DO).
2. Phase rank inversions: identifying single-phase specialists vs all-phase masters.
3. Scatter comparisons of High-Pressure Strike Rates (PP vs MO, MO vs DO).
4. Scatter comparisons of High-Pressure Economy Rates (PP vs MO, PP vs DO).
5. Phase specialization profiles for iconic cricket archetypes.

Generates:
- outputs/exploratory_analysis/10_phase_performance_transitions.png
- outputs/exploratory_analysis/11_phase_specialist_disparity.png
- outputs/exploratory_analysis/12_cross_phase_player_profiles.png
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
b_perf = pd.read_csv("data/processed/batter_performance.csv")
bo_perf = pd.read_csv("data/processed/bowler_performance.csv")
p_spec = pd.read_csv("data/processed/phase_specialist_rankings.csv")

print(f"Loaded {len(b_perf)} batters, {len(bo_perf)} bowlers, and {len(p_spec)} phase entries.")


# =========================================================================
# CHART 10: PHASE PERFORMANCE TRANSITIONS (SCATTER PLOTS)
# =========================================================================
def plot_phase_performance_transitions():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12), dpi=300)
    
    # 10.1 Batters: Powerplay vs Middle Overs (bf >= 15 in both)
    b_pp_mo = b_perf[(b_perf['bf_pp_high'] >= 15) & (b_perf['bf_mo_high'] >= 15)].copy()
    diff_b1 = b_pp_mo['mo_high_strike_rate'] - b_pp_mo['pp_high_strike_rate']
    sizes_b1 = (b_pp_mo['bf_pp_high'] + b_pp_mo['bf_mo_high']) * 0.8
    sc1 = ax1.scatter(b_pp_mo['pp_high_strike_rate'], b_pp_mo['mo_high_strike_rate'],
                      s=sizes_b1, c=diff_b1, cmap='coolwarm', edgecolors='black', linewidths=0.6, alpha=0.85)
    lims1 = [50, 210]
    ax1.plot(lims1, lims1, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity (Equal SR)')
    ax1.set_title(f"A. Batting Strike Rate: Powerplay vs Middle Overs (N={len(b_pp_mo)})\n(Red = Faster in Middle; Blue = Faster in Powerplay)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.set_xlabel("Powerplay High-P Strike Rate", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Middle Overs High-P Strike Rate", fontsize=10, fontweight='bold')
    ax1.set_xlim(lims1)
    ax1.set_ylim(lims1)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower right', fontsize=8.5)
    
    # Annotate notable batters
    notable_b1 = ['Travis Head', 'Sunil Narine', 'Suryakumar Yadav', 'Nicholas Pooran', 'Jos Buttler']
    for _, r in b_pp_mo[b_pp_mo['player_name'].isin(notable_b1)].iterrows():
        ax1.annotate(r['player_name'].split()[-1], (r['pp_high_strike_rate'], r['mo_high_strike_rate']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#fcf3cf', edgecolor='#f39c12', alpha=0.85))

    # 10.2 Batters: Middle Overs vs Death Overs (bf >= 15 in both)
    b_mo_do = b_perf[(b_perf['bf_mo_high'] >= 15) & (b_perf['bf_do_high'] >= 15)].copy()
    diff_b2 = b_mo_do['do_high_strike_rate'] - b_mo_do['mo_high_strike_rate']
    sizes_b2 = (b_mo_do['bf_mo_high'] + b_mo_do['bf_do_high']) * 0.7
    sc2 = ax2.scatter(b_mo_do['mo_high_strike_rate'], b_mo_do['do_high_strike_rate'],
                      s=sizes_b2, c=diff_b2, cmap='coolwarm', edgecolors='black', linewidths=0.6, alpha=0.85)
    lims2 = [50, 260]
    ax2.plot(lims2, lims2, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity (Equal SR)')
    ax2.set_title(f"B. Batting Strike Rate: Middle Overs vs Death Overs (N={len(b_mo_do)})\n(Red = Death Acceleration; Blue = Death Deceleration)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.set_xlabel("Middle Overs High-P Strike Rate", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Death Overs High-P Strike Rate", fontsize=10, fontweight='bold')
    ax2.set_xlim(lims2)
    ax2.set_ylim(lims2)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='lower right', fontsize=8.5)

    notable_b2 = ['Mahendra Singh Dhoni', 'Rinku Singh', 'Heinrich Klaasen', 'Tim David', 'Shivam Dube', 'Marcus Stoinis']
    for _, r in b_mo_do[b_mo_do['player_name'].isin(notable_b2)].iterrows():
        name_lbl = 'MS Dhoni' if 'Dhoni' in r['player_name'] else r['player_name'].split()[-1]
        ax2.annotate(name_lbl, (r['mo_high_strike_rate'], r['do_high_strike_rate']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#d5f5e3', edgecolor='#27ae60', alpha=0.85))

    # 10.3 Bowlers: Powerplay vs Middle Overs (lb >= 15 in both)
    bo_pp_mo = bo_perf[(bo_perf['lb_pp_high'] >= 15) & (bo_perf['lb_mo_high'] >= 15)].copy()
    diff_bo1 = bo_pp_mo['pp_high_economy_rate'] - bo_pp_mo['mo_high_economy_rate'] # positive = tighter in Middle
    sizes_bo1 = (bo_pp_mo['lb_pp_high'] + bo_pp_mo['lb_mo_high']) * 0.7
    sc3 = ax3.scatter(bo_pp_mo['pp_high_economy_rate'], bo_pp_mo['mo_high_economy_rate'],
                      s=sizes_bo1, c=diff_bo1, cmap='coolwarm_r', edgecolors='black', linewidths=0.6, alpha=0.85)
    lims3 = [4.0, 14.0]
    ax3.plot(lims3, lims3, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity (Equal Economy)')
    ax3.set_title(f"C. Bowling Economy: Powerplay vs Middle Overs (N={len(bo_pp_mo)})\n(Blue = Tighter in Middle; Red = Tighter in Powerplay)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax3.set_xlabel("Powerplay High-P Economy (RPO)", fontsize=10, fontweight='bold')
    ax3.set_ylabel("Middle Overs High-P Economy (RPO)", fontsize=10, fontweight='bold')
    ax3.set_xlim(lims3)
    ax3.set_ylim(lims3)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(loc='upper left', fontsize=8.5)

    notable_bo1 = ['Jasprit Bumrah', 'Axar Patel', 'Rashid Khan', 'Trent Boult', 'Arshdeep Singh']
    for _, r in bo_pp_mo[bo_pp_mo['player_name'].isin(notable_bo1)].iterrows():
        ax3.annotate(r['player_name'].split()[-1], (r['pp_high_economy_rate'], r['mo_high_economy_rate']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#e8f8f5', edgecolor='#16a085', alpha=0.85))

    # 10.4 Bowlers: Powerplay vs Death Overs (lb >= 15 in both)
    bo_pp_do = bo_perf[(bo_perf['lb_pp_high'] >= 15) & (bo_perf['lb_do_high'] >= 15)].copy()
    diff_bo2 = bo_pp_do['do_high_economy_rate'] - bo_pp_do['pp_high_economy_rate']
    sizes_bo2 = (bo_pp_do['lb_pp_high'] + bo_pp_do['lb_do_high']) * 0.7
    sc4 = ax4.scatter(bo_pp_do['pp_high_economy_rate'], bo_pp_do['do_high_economy_rate'],
                      s=sizes_bo2, c=diff_bo2, cmap='coolwarm', edgecolors='black', linewidths=0.6, alpha=0.85)
    lims4 = [4.0, 16.0]
    ax4.plot(lims4, lims4, color='#7f8c8d', linestyle='--', linewidth=1.5, label='Parity (Equal Economy)')
    ax4.set_title(f"D. Bowling Economy: Powerplay vs Death Overs (N={len(bo_pp_do)})\n(Red = Death Economy Leakage; Blue = Death Containment)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax4.set_xlabel("Powerplay High-P Economy (RPO)", fontsize=10, fontweight='bold')
    ax4.set_ylabel("Death Overs High-P Economy (RPO)", fontsize=10, fontweight='bold')
    ax4.set_xlim(lims4)
    ax4.set_ylim(lims4)
    ax4.grid(True, linestyle='--', alpha=0.5)
    ax4.legend(loc='upper left', fontsize=8.5)

    notable_bo2 = ['Jasprit Bumrah', 'Arshdeep Singh', 'Bhuvneshwar Kumar', 'Mohammad Shami', 'Harshit Rana']
    for _, r in bo_pp_do[bo_pp_do['player_name'].isin(notable_bo2)].iterrows():
        ax4.annotate(r['player_name'].split()[-1], (r['pp_high_economy_rate'], r['do_high_economy_rate']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#fbfcfc', edgecolor='#8e44ad', alpha=0.85))

    plt.suptitle("Cross-Phase Performance Dynamics: Powerplay, Middle, and Death Overs\n"
                 "Visualizing Structural Shifts in High-Pressure Scoring Velocity and Bowling Resistance",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "10_phase_performance_transitions.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 11: PHASE SPECIALIST DISPARITY (RANK INVERSIONS)
# =========================================================================
def plot_phase_specialist_disparity():
    # Pivot phase specialist rankings
    p_wide = p_spec.pivot_table(index=['player_id', 'player_name', 'role'], 
                                columns='phase', values='rank').reset_index()
    
    mo_col = 'Middle Overs (Overs 7-15)'
    do_col = 'Death Overs (Overs 16-20)'
    pp_col = 'Powerplay (Overs 1-6)'
    
    # 1. Death Specialists (Batters with much better Death rank than Middle rank)
    bat_multi = p_wide[(p_wide['role'] == 'Batter') & p_wide[mo_col].notnull() & p_wide[do_col].notnull()].copy()
    bat_multi['rank_diff'] = bat_multi[mo_col] - bat_multi[do_col] # positive = better in death
    top_death_bat = bat_multi.sort_values('rank_diff', ascending=False).head(10)
    top_mo_bat = bat_multi.sort_values('rank_diff', ascending=True).head(10)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=300)
    
    # Dumbbell Chart 1: Batters Death Specialists (Death vs Middle rank)
    y_pos1 = np.arange(len(top_death_bat))
    ax1.hlines(y=y_pos1, xmin=top_death_bat[do_col], xmax=top_death_bat[mo_col], color='#bdc3c7', linewidth=2.5, zorder=1)
    ax1.scatter(top_death_bat[do_col], y_pos1, color='#e74c3c', s=100, zorder=3, label='Death Overs Rank (Higher Quality)')
    ax1.scatter(top_death_bat[mo_col], y_pos1, color='#3498db', s=100, zorder=3, label='Middle Overs Rank')
    
    # Annotate delta
    for i, (_, r) in enumerate(top_death_bat.iterrows()):
        ax1.text((r[do_col] + r[mo_col]) / 2, i + 0.25, f"+{int(r['rank_diff'])} Ranks at Death", 
                 ha='center', fontsize=8, fontweight='bold', color='#c0392b')
        
    ax1.set_yticks(y_pos1)
    ax1.set_yticklabels([r['player_name'] for _, r in top_death_bat.iterrows()], fontsize=9.5, fontweight='bold')
    ax1.set_xlabel("Phase Specialist Rank (1 = Best)", fontsize=10, fontweight='bold')
    ax1.set_title("A. Pure Death-Over Batting Specialists\n(Elite Death Finishers with Mediocre Middle-Over Ranks)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.invert_yaxis()
    ax1.legend(loc='lower right', frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Dumbbell Chart 2: Middle Overs Batting Specialists (Better in Middle than Death)
    y_pos2 = np.arange(len(top_mo_bat))
    ax2.hlines(y=y_pos2, xmin=top_mo_bat[mo_col], xmax=top_mo_bat[do_col], color='#bdc3c7', linewidth=2.5, zorder=1)
    ax2.scatter(top_mo_bat[mo_col], y_pos2, color='#27ae60', s=100, zorder=3, label='Middle Overs Rank (Higher Quality)')
    ax2.scatter(top_mo_bat[do_col], y_pos2, color='#e67e22', s=100, zorder=3, label='Death Overs Rank')

    for i, (_, r) in enumerate(top_mo_bat.iterrows()):
        ax2.text((r[mo_col] + r[do_col]) / 2, i + 0.25, f"+{int(abs(r['rank_diff']))} Ranks in Middle", 
                 ha='center', fontsize=8, fontweight='bold', color='#27ae60')

    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels([r['player_name'] for _, r in top_mo_bat.iterrows()], fontsize=9.5, fontweight='bold')
    ax2.set_xlabel("Phase Specialist Rank (1 = Best)", fontsize=10, fontweight='bold')
    ax2.set_title("B. Middle-Overs Spin Enforcers & Anchors\n(Elite in Middle Overs, but Decline When Pushed to Death)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.invert_yaxis()
    ax2.legend(loc='lower right', frameon=True, fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("Phase Specialization Inversion: Revealing Structural Role Limitations\n"
                 "Contrasting Pure Finishers (MS Dhoni, Rinku Singh) vs Middle-Overs Anchors (Axar Patel, Pat Cummins)",
                 fontsize=13, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "11_phase_specialist_disparity.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 12: CROSS-PHASE PLAYER PROFILES (REPRESENTATIVE ARCHETYPES)
# =========================================================================
def plot_cross_phase_player_profiles():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300)
    
    # Archetype Batters Strike Rate across Phases
    # Select iconic players with presence across PP, MO, DO
    bat_archetypes = {
        'MS Dhoni': '#e67e22',        # Pure Finisher
        'Rinku Singh': '#27ae60',      # Clutch Finisher
        'Suryakumar Yadav': '#2980b9', # Middle-Overs Master
        'Travis Head': '#8e44ad',      # Powerplay Enforcer
        'Virat Kohli': '#c0392b',      # Anchor
        'Heinrich Klaasen': '#d35400'  # Phase Accelerator
    }
    
    phases = ['Powerplay', 'Middle Overs', 'Death Overs']
    x_pos = np.arange(len(phases))
    
    for name, color in bat_archetypes.items():
        row = b_perf[b_perf['player_name'] == name]
        if not row.empty:
            r = row.iloc[0]
            sr_vals = [r['pp_high_strike_rate'], r['mo_high_strike_rate'], r['do_high_strike_rate']]
            # Only plot valid numbers
            sr_clean = [v if pd.notnull(v) and v > 0 else np.nan for v in sr_vals]
            ax1.plot(x_pos, sr_clean, marker='o', linewidth=2.4, markersize=8, color=color, label=f"{name}")
            
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(phases, fontsize=10.5, fontweight='bold')
    ax1.set_ylabel("High-Pressure Strike Rate", fontsize=10.5, fontweight='bold')
    ax1.set_title("A. Batting Archetypes Across Match Phases\n(Demonstrating Extreme Phase Specialization Profiles)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.axhline(114.05, color='#7f8c8d', linestyle=':', label='League High-P Prior (114.05)')
    ax1.legend(loc='upper left', frameon=True, fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Archetype Bowlers Economy across Phases
    bowl_archetypes = {
        'Jasprit Bumrah': '#117864',    # All-Phase Master
        'Bhuvneshwar Kumar': '#2980b9', # Powerplay Specialist
        'Rashid Khan': '#8e44ad',       # Middle-Overs Spin Lock
        'Arshdeep Singh': '#c0392b',    # Death/PP Left-Arm Swing
        'Trent Boult': '#27ae60',       # Powerplay Swing Weapon
        'Andre Russell': '#d35400'      # Death Overs Yorker Weapon
    }
    
    for name, color in bowl_archetypes.items():
        row = bo_perf[bo_perf['player_name'] == name]
        if not row.empty:
            r = row.iloc[0]
            econ_vals = [r['pp_high_economy_rate'], r['mo_high_economy_rate'], r['do_high_economy_rate']]
            econ_clean = [v if pd.notnull(v) and v > 0 else np.nan for v in econ_vals]
            ax2.plot(x_pos, econ_clean, marker='s', linewidth=2.4, markersize=8, color=color, label=f"{name}")

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(phases, fontsize=10.5, fontweight='bold')
    ax2.set_ylabel("High-Pressure Economy Rate (RPO - Lower is Better)", fontsize=10.5, fontweight='bold')
    ax2.set_title("B. Bowling Archetypes Across Match Phases\n(Comparing Multi-Phase Control vs Specialized Spells)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.axhline(9.06, color='#7f8c8d', linestyle=':', label='League High-P Prior (9.06)')
    ax2.legend(loc='upper left', frameon=True, fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("Player Career Architecture: Tracing Role-Specific Execution Across T20 Phases",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "12_cross_phase_player_profiles.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    plot_phase_performance_transitions()
    plot_phase_specialist_disparity()
    plot_cross_phase_player_profiles()
    print("Completed EDA Module 04.")
