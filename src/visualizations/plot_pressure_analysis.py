"""
Part A — Pressure Analysis Visualizations
=========================================
Generates:
1. outputs/visualizations/01_batting_pressure_distribution.png
2. outputs/visualizations/02_bowling_pressure_distribution.png
3. outputs/visualizations/03_pressure_by_phase.png
4. outputs/visualizations/04_pressure_by_innings.png
5. outputs/visualizations/05_match_pressure_timelines.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Styling setup
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = Path("outputs/visualizations")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load Data
p_df = pd.read_csv("data/processed/delivery_pressure_index.csv")
# Clean dataset (exclude 233 target reached tail deliveries)
is_target_reached_tail = (p_df['innings'] == 2) & (p_df['runs_required'] <= 0)
clean_df = p_df[~is_target_reached_tail].copy()

print(f"Loaded {len(clean_df):,} clean deliveries for Pressure Analysis.")


# =========================================================================
# CHART 1: BATTING PRESSURE INDEX DISTRIBUTION
# =========================================================================
def plot_batting_pi_distribution():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    bat_pi = clean_df['Batting_PI']
    mean_val = bat_pi.mean()
    median_val = bat_pi.median()
    
    # Qualitative bands background
    bands = [
        (0, 20, '#eaf2f8', 'Very Low (0-20)'),
        (20, 40, '#d4efdf', 'Low (21-40)'),
        (40, 60, '#fef9e7', 'Moderate (41-60)'),
        (60, 80, '#fadbd8', 'High (61-80)'),
        (80, 100, '#f5b7b1', 'Very High (81-100)')
    ]
    for low, high, color, label in bands:
        ax.axvspan(low, high, color=color, alpha=0.45, label=label)
        
    # Histogram
    n, bins, patches = ax.hist(bat_pi, bins=50, density=True, color='#2874a6', 
                               edgecolor='white', alpha=0.85, zorder=3)
    
    # Summary lines
    ax.axvline(mean_val, color='#b03a2e', linestyle='--', linewidth=2, zorder=4, 
               label=f'Mean PI = {mean_val:.2f}')
    ax.axvline(median_val, color='#117a65', linestyle='-', linewidth=2, zorder=4, 
               label=f'Median PI = {median_val:.2f}')
    ax.axvline(60.0, color='#78281f', linestyle=':', linewidth=2.2, zorder=4,
               label='High-Pressure Cutoff (PI > 60.0)')

    # Labels and formatting
    ax.set_title("Distribution of Batting Pressure Index across T20 Deliveries (2022–2026)\n"
                 f"Clean Population: N = {len(clean_df):,} deliveries | High-Pressure Deliveries: {(bat_pi > 60).sum():,} ({(bat_pi > 60).mean()*100:.1f}%)",
                 fontsize=12, pad=15, fontweight='bold', color='#1b2631')
    ax.set_xlabel("Batting Pressure Index (0–100)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_ylabel("Probability Density", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlim(0, 100)
    ax.grid(True, linestyle='--', alpha=0.5, zorder=0)
    ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9)
    
    out_path = OUT_DIR / "01_batting_pressure_distribution.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 2: BOWLING PRESSURE INDEX DISTRIBUTION
# =========================================================================
def plot_bowling_pi_distribution():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    bowl_pi = clean_df['Bowling_PI']
    mean_val = bowl_pi.mean()
    median_val = bowl_pi.median()
    
    # Qualitative bands background
    bands = [
        (0, 20, '#eaf2f8', 'Very Low (0-20)'),
        (20, 40, '#d4efdf', 'Low (21-40)'),
        (40, 60, '#fef9e7', 'Moderate (41-60)'),
        (60, 80, '#fadbd8', 'High (61-80)'),
        (80, 100, '#f5b7b1', 'Very High (81-100)')
    ]
    for low, high, color, label in bands:
        ax.axvspan(low, high, color=color, alpha=0.45, label=label)
        
    # Histogram
    n, bins, patches = ax.hist(bowl_pi, bins=50, density=True, color='#8e44ad', 
                               edgecolor='white', alpha=0.85, zorder=3)
    
    # Summary lines
    ax.axvline(mean_val, color='#b03a2e', linestyle='--', linewidth=2, zorder=4, 
               label=f'Mean PI = {mean_val:.2f}')
    ax.axvline(median_val, color='#117a65', linestyle='-', linewidth=2, zorder=4, 
               label=f'Median PI = {median_val:.2f}')
    ax.axvline(60.0, color='#78281f', linestyle=':', linewidth=2.2, zorder=4,
               label='High-Pressure Cutoff (PI > 60.0)')

    # Labels and formatting
    ax.set_title("Distribution of Bowling Pressure Index across T20 Deliveries (2022–2026)\n"
                 f"Clean Population: N = {len(clean_df):,} deliveries | High-Pressure Deliveries: {(bowl_pi > 60).sum():,} ({(bowl_pi > 60).mean()*100:.1f}%)",
                 fontsize=12, pad=15, fontweight='bold', color='#1b2631')
    ax.set_xlabel("Bowling Pressure Index (0–100)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_ylabel("Probability Density", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlim(0, 100)
    ax.grid(True, linestyle='--', alpha=0.5, zorder=0)
    ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9)
    
    out_path = OUT_DIR / "02_bowling_pressure_distribution.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 3: PRESSURE DISTRIBUTION ACROSS PHASES (PP, MIDDLE, DEATH)
# =========================================================================
def plot_pressure_by_phase():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300, sharey=True)
    
    phases = ['PP', 'Middle', 'Death']
    phase_labels = ['Powerplay\n(Overs 1-6)', 'Middle Overs\n(Overs 7-15)', 'Death Overs\n(Overs 16-20)']
    colors = ['#3caea3', '#f6d55c', '#ed553b']
    
    # 1. Batting PI by Phase
    data_bat = [clean_df[clean_df['phase'] == p]['Batting_PI'].values for p in phases]
    bp1 = ax1.boxplot(data_bat, patch_artist=True, tick_labels=phase_labels, widths=0.55,
                      medianprops=dict(color='black', linewidth=2),
                      boxprops=dict(linewidth=1.2),
                      whiskerprops=dict(linestyle='--', linewidth=1.2),
                      capprops=dict(linewidth=1.2),
                      flierprops=dict(marker='o', markersize=2, alpha=0.2))
    
    for patch, color in zip(bp1['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
        
    # Annotate means
    means_bat = [np.mean(d) for d in data_bat]
    hp_pct_bat = [(d > 60).mean()*100 for d in data_bat]
    for i, (m, hp) in enumerate(zip(means_bat, hp_pct_bat)):
        ax1.text(i + 1, m + 2.5, f"Mean: {m:.1f}\nHP: {hp:.1f}%", 
                 ha='center', fontsize=9.5, fontweight='bold', color='#1a5276',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#cccccc'))
                 
    ax1.set_title("Batting Pressure Index by Match Phase\n(Pressure escalates towards Death Overs)", 
                  fontsize=12, fontweight='bold', pad=12, color='#1b2631')
    ax1.set_ylabel("Pressure Index (0–100)", fontsize=11, fontweight='bold')
    ax1.axhline(60, color='#b03a2e', linestyle=':', label='High-Pressure Cutoff (PI >= 61.0)')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 2. Bowling PI by Phase
    data_bowl = [clean_df[clean_df['phase'] == p]['Bowling_PI'].values for p in phases]
    bp2 = ax2.boxplot(data_bowl, patch_artist=True, tick_labels=phase_labels, widths=0.55,
                      medianprops=dict(color='black', linewidth=2),
                      boxprops=dict(linewidth=1.2),
                      whiskerprops=dict(linestyle='--', linewidth=1.2),
                      capprops=dict(linewidth=1.2),
                      flierprops=dict(marker='o', markersize=2, alpha=0.2))
    
    for patch, color in zip(bp2['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
        
    means_bowl = [np.mean(d) for d in data_bowl]
    hp_pct_bowl = [(d > 60).mean()*100 for d in data_bowl]
    for i, (m, hp) in enumerate(zip(means_bowl, hp_pct_bowl)):
        ax2.text(i + 1, m + 2.5, f"Mean: {m:.1f}\nHP: {hp:.1f}%", 
                 ha='center', fontsize=9.5, fontweight='bold', color='#6c3483',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#cccccc'))
                 
    ax2.set_title("Bowling Pressure Index by Match Phase\n(Bowling pressure peaks in Powerplay with wickets in hand)", 
                  fontsize=12, fontweight='bold', pad=12, color='#1b2631')
    ax2.axhline(60, color='#b03a2e', linestyle=':', label='High-Pressure Cutoff (PI >= 61.0)')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "03_pressure_by_phase.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 4: PRESSURE BY INNINGS (1st vs 2nd INNINGS)
# =========================================================================
def plot_pressure_by_innings():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    inn1 = clean_df[clean_df['innings'] == 1]
    inn2 = clean_df[clean_df['innings'] == 2]
    
    # 1. Batting PI by Innings
    bins = np.linspace(0, 100, 45)
    ax1.hist(inn1['Batting_PI'], bins=bins, density=True, alpha=0.65, color='#2e86c1', 
             label=f"1st Innings (Setting Target)\nMean={inn1['Batting_PI'].mean():.1f}, Med={inn1['Batting_PI'].median():.1f}")
    ax1.hist(inn2['Batting_PI'], bins=bins, density=True, alpha=0.65, color='#e74c3c', 
             label=f"2nd Innings (Chasing Target)\nMean={inn2['Batting_PI'].mean():.1f}, Med={inn2['Batting_PI'].median():.1f}")
    
    ax1.axvline(60, color='black', linestyle=':', linewidth=1.8, label='High-Pressure (PI >= 61.0)')
    ax1.set_title("Batting Pressure: 1st Innings vs 2nd Innings Chases\n(2nd Innings exhibits heavier right tail due to RRR escalations)", 
                  fontsize=11.5, fontweight='bold', pad=12)
    ax1.set_xlabel("Batting Pressure Index", fontsize=11, fontweight='bold')
    ax1.set_ylabel("Probability Density", fontsize=11, fontweight='bold')
    ax1.set_xlim(0, 100)
    ax1.legend(loc='upper right', fontsize=9, frameon=True)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 2. Bowling PI by Innings
    ax2.hist(inn1['Bowling_PI'], bins=bins, density=True, alpha=0.65, color='#17a589', 
             label=f"1st Innings (Bowling First)\nMean={inn1['Bowling_PI'].mean():.1f}, Med={inn1['Bowling_PI'].median():.1f}")
    ax2.hist(inn2['Bowling_PI'], bins=bins, density=True, alpha=0.65, color='#884ea0', 
             label=f"2nd Innings (Defending Target)\nMean={inn2['Bowling_PI'].mean():.1f}, Med={inn2['Bowling_PI'].median():.1f}")
    
    ax2.axvline(60, color='black', linestyle=':', linewidth=1.8, label='High-Pressure (PI >= 61.0)')
    ax2.set_title("Bowling Pressure: 1st Innings vs 2nd Innings Defending\n(Bowling pressure shows higher variance in defending chases)", 
                  fontsize=11.5, fontweight='bold', pad=12)
    ax2.set_xlabel("Bowling Pressure Index", fontsize=11, fontweight='bold')
    ax2.set_ylabel("Probability Density", fontsize=11, fontweight='bold')
    ax2.set_xlim(0, 100)
    ax2.legend(loc='upper right', fontsize=9, frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.5)

    out_path = OUT_DIR / "04_pressure_by_innings.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


# =========================================================================
# CHART 5: MATCH-LEVEL PRESSURE TIMELINES (3 REPRESENTATIVE ARCHETYPES)
# =========================================================================
def plot_match_timelines():
    fig, axes = plt.subplots(3, 1, figsize=(14, 11), dpi=300, sharex=True)
    
    # Archetype 1: Match 14126 (CSK vs MI, 2022-04-21) - Dramatic Last-Ball Chase
    m1 = clean_df[(clean_df['match_id'] == 14126) & (clean_df['innings'] == 2)].copy()
    ax1 = axes[0]
    ax1.plot(m1['legal_balls_before'], m1['Batting_PI'], color='#c0392b', linewidth=2.5, 
             label='Batting PI (CSK Chasing 156)')
    ax1.plot(m1['legal_balls_before'], m1['Bowling_PI'], color='#2980b9', linewidth=2, linestyle='--',
             label='Bowling PI (MI Defending)')
    
    # Highlight dismissals
    w_balls = m1[m1['is_wicket']]['legal_balls_before']
    w_pis = m1[m1['is_wicket']]['Batting_PI']
    ax1.scatter(w_balls, w_pis, color='#900c3f', s=70, marker='X', zorder=5, label='Wicket Fallen')
    
    ax1.axhline(60, color='#7f8c8d', linestyle=':', label='High-Pressure Cutoff')
    ax1.set_title("Archetype 1 — Dramatic Escalating Chase: Match 14126 (MI vs CSK, 2022-04-21)\n"
                  "CSK needed 16 off 4 balls; Dhoni hit 6, 4, 2, 4 off Unadkat to win on final delivery (Batting PI peaked at 92.5)", 
                  fontsize=11, fontweight='bold', pad=8, color='#1b2631')
    ax1.set_ylabel("Pressure Index", fontsize=10, fontweight='bold')
    ax1.set_ylim(0, 100)
    ax1.legend(loc='upper left', fontsize=8.5, frameon=True)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Archetype 2: Match 14153 (CSK vs MI, 2022-05-12) - Early First-Innings Collapse
    m2 = clean_df[(clean_df['match_id'] == 14153) & (clean_df['innings'] == 1)].copy()
    ax2 = axes[1]
    ax2.plot(m2['legal_balls_before'], m2['Batting_PI'], color='#d35400', linewidth=2.5, 
             label='Batting PI (CSK Setting Target)')
    ax2.plot(m2['legal_balls_before'], m2['Bowling_PI'], color='#16a085', linewidth=2, linestyle='--',
             label='Bowling PI (MI Bowling First)')
             
    w_balls2 = m2[m2['is_wicket']]['legal_balls_before']
    w_pis2 = m2[m2['is_wicket']]['Batting_PI']
    ax2.scatter(w_balls2, w_pis2, color='#900c3f', s=70, marker='X', zorder=5, label='Wicket Fallen')
    
    ax2.axhline(60, color='#7f8c8d', linestyle=':', label='High-Pressure Cutoff')
    ax2.set_title("Archetype 2 — Early Top-Order Collapse: Match 14153 (CSK vs MI, 2022-05-12)\n"
                  "CSK collapsed to 16/3 in 1.4 overs and 32/5 in 5.3 overs (Batting PI immediately spiked to 83.2 in Powerplay)", 
                  fontsize=11, fontweight='bold', pad=8, color='#1b2631')
    ax2.set_ylabel("Pressure Index", fontsize=10, fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper right', fontsize=8.5, frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # Archetype 3: Match 14125 (DC vs PBKS, 2022-04-20) - Comfortable One-Sided Chase
    m3 = clean_df[(clean_df['match_id'] == 14125) & (clean_df['innings'] == 2)].copy()
    ax3 = axes[2]
    ax3.plot(m3['legal_balls_before'], m3['Batting_PI'], color='#27ae60', linewidth=2.5, 
             label='Batting PI (DC Chasing 116)')
    ax3.plot(m3['legal_balls_before'], m3['Bowling_PI'], color='#7f8c8d', linewidth=2, linestyle='--',
             label='Bowling PI (PBKS Defending 115)')
             
    w_balls3 = m3[m3['is_wicket']]['legal_balls_before']
    w_pis3 = m3[m3['is_wicket']]['Batting_PI']
    ax3.scatter(w_balls3, w_pis3, color='#900c3f', s=70, marker='X', zorder=5, label='Wicket Fallen')
    
    ax3.axhline(60, color='#7f8c8d', linestyle=':', label='High-Pressure Cutoff')
    ax3.set_title("Archetype 3 — Low-Pressure Comfortable Chase: Match 14125 (DC vs PBKS, 2022-04-20)\n"
                  "DC cruised to 119/1 in 10.3 overs (Batting PI remained flat in 20-35 range throughout the entire chase)", 
                  fontsize=11, fontweight='bold', pad=8, color='#1b2631')
    ax3.set_xlabel("Legal Balls Completed in Innings (0–120)", fontsize=11, fontweight='bold', labelpad=8)
    ax3.set_ylabel("Pressure Index", fontsize=10, fontweight='bold')
    ax3.set_xlim(0, 120)
    ax3.set_ylim(0, 100)
    ax3.legend(loc='upper left', fontsize=8.5, frameon=True)
    ax3.grid(True, linestyle='--', alpha=0.5)
    
    out_path = OUT_DIR / "05_match_pressure_timelines.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


if __name__ == '__main__':
    plot_batting_pi_distribution()
    plot_bowling_pi_distribution()
    plot_pressure_by_phase()
    plot_pressure_by_innings()
    plot_match_timelines()
