import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def setup_style():
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#cccccc'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#e5e5e5'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7

def regenerate_figures():
    fig_dir = 'outputs/step_8_eda/figures'
    os.makedirs(fig_dir, exist_ok=True)
    setup_style()

    print("[Loading datasets for Figures 1-4]...")
    bat_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
    bowl_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

    # --------------------------------------------------------------------------
    # 1. Figure 01: Top 20 Batting Player Rankings
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 01] Top 20 Batting Rankings...")
    fig, ax = plt.subplots(figsize=(11, 7.5))
    top20_b = bat_df.head(20).iloc[::-1]  # Reverse for bottom-to-top display
    y_pos = np.arange(len(top20_b))
    
    colors = ['#1f77b4' if r['Rank'] <= 10 else '#9ecae1' for _, r in top20_b.iterrows()]
    bars = ax.barh(y_pos, top20_b['Shrunk score'], color=colors, edgecolor='#0d3d63', height=0.68, alpha=0.9)
    
    ax.set_yticks(y_pos)
    labels = [f"#{r['Rank']:02d}  {r['Player']}  ({r['Team/format'].split(' (')[0]})" for _, r in top20_b.iterrows()]
    ax.set_yticklabels(labels, fontsize=9.5, fontweight='500')
    ax.set_xlabel("Batting Pressure Reliability Score (PWSVA Shrunk Score, Runs / Ball)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_title("Top 20 Batting Reliability Under Pressure (SupeRR Selector Round 1)\nHighlighting Top 10 vs Ranks 11–20", fontsize=13, fontweight='bold', pad=15)
    
    # Annotate bars
    for bar, (_, r) in zip(bars, top20_b.iterrows()):
        val = r['Shrunk score']
        ax.text(val + 0.006, bar.get_y() + bar.get_height()/2, f"+{val:.3f}", va='center', ha='left', fontsize=8.5, fontweight='bold', color='#111111')
        
    # Cutoff line between rank 10 and 11
    cutoff_y = 9.5
    ax.axhline(cutoff_y, color='#d62728', linestyle='--', linewidth=1.5, alpha=0.8)
    
    # Position cutoff text with white bounding box in empty area on the right, completely clear of bar text
    ax.text(0.388, cutoff_y + 0.35, "Top 10 Official Cutoff (#10 Reeza Hendricks: +0.156 vs #11 Rajat Patidar: +0.154)", 
            color='#d62728', fontsize=8.5, fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffff', edgecolor='#d62728', alpha=0.95, linewidth=0.9))
    
    ax.set_xlim(-0.02, 0.40)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig01_batting_top20_rankings.png'), dpi=300)
    plt.close(fig)
    print("  -> Saved Fig 01 successfully.")

    # --------------------------------------------------------------------------
    # 2. Figure 02: Top 20 Bowling Player Rankings
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 02] Top 20 Bowling Rankings...")
    fig, ax = plt.subplots(figsize=(11, 7.5))
    top20_bw = bowl_df.head(20).iloc[::-1]
    y_pos = np.arange(len(top20_bw))
    
    colors = ['#2ca02c' if r['Rank'] <= 10 else '#a1d99b' for _, r in top20_bw.iterrows()]
    bars = ax.barh(y_pos, top20_bw['Shrunk score'], color=colors, edgecolor='#1b681b', height=0.68, alpha=0.9)
    
    ax.set_yticks(y_pos)
    labels = [f"#{r['Rank']:02d}  {r['Player']}  ({r['Team/format'].split(' (')[0]})" for _, r in top20_bw.iterrows()]
    ax.set_yticklabels(labels, fontsize=9.5, fontweight='500')
    ax.set_xlabel("Bowling Pressure Reliability Score (SBVA Shrunk Score, Net Runs Saved / Ball)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_title("Top 20 Bowling Reliability Under Pressure (SupeRR Selector Round 1)\nHighlighting Top 10 vs Ranks 11–20", fontsize=13, fontweight='bold', pad=15)
    
    for bar, (_, r) in zip(bars, top20_bw.iterrows()):
        val = r['Shrunk score']
        ax.text(val + 0.003, bar.get_y() + bar.get_height()/2, f"+{val:.3f}", va='center', ha='left', fontsize=8.5, fontweight='bold', color='#111111')
        
    cutoff_y = 9.5
    ax.axhline(cutoff_y, color='#d62728', linestyle='--', linewidth=1.5, alpha=0.8)
    
    # Position cutoff text with white bounding box in empty area on the right, completely clear of bar text
    ax.text(0.192, cutoff_y + 0.35, "Top 10 Official Cutoff (#10 Mujeeb: +0.102 vs #11 Mosaddek: +0.100)", 
            color='#d62728', fontsize=8.5, fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffff', edgecolor='#d62728', alpha=0.95, linewidth=0.9))
    
    ax.set_xlim(-0.01, 0.20)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig02_bowling_top20_rankings.png'), dpi=300)
    plt.close(fig)
    print("  -> Saved Fig 02 successfully.")

    # --------------------------------------------------------------------------
    # 3. Figure 03: Batting Reliability Score vs. Sample Size
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 03] Batting Score vs Sample Size...")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    
    # Population scatter
    ax.scatter(bat_df['Raw opportunities'], bat_df['Shrunk score'], color='#aec7e8', alpha=0.65, edgecolors='#1f77b4', s=35, label='All 297 Qualifying Batters')
    
    # Highlight top 10
    top10_b_all = bat_df.head(10)
    ax.scatter(top10_b_all['Raw opportunities'], top10_b_all['Shrunk score'], color='#1f77b4', edgecolors='black', s=95, linewidth=1.2, zorder=5, label='Top 10 Batters')
    
    # Distinct quadrant offsets to guarantee zero overlap between Tim David (#4) and Heinrich Klaasen (#5)
    offsets_bat = {
        1: (50, 0.015),       # Vaibhav: top-right
        2: (-200, 0.018),     # Surya: top-left
        3: (50, 0.015),       # Abhishek: top-right
        4: (-210, 0.024),     # Tim David: top-left (1163b, +0.257) -> moves away from Klaasen
        5: (45, -0.028),      # Heinrich Klaasen: bottom-right (1409b, +0.220) -> moves away from David
    }
    for _, r in top10_b_all.head(5).iterrows():
        rk = int(r['Rank'])
        dx, dy = offsets_bat.get(rk, (40, 0.018))
        ax.annotate(
            f"#{rk} {r['Player']}\n(+{r['Shrunk score']:.3f})",
            (r['Raw opportunities'], r['Shrunk score']),
            xytext=(r['Raw opportunities'] + dx, r['Shrunk score'] + dy),
            fontsize=8.5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.88),
            arrowprops=dict(arrowstyle='->', color='#333333', lw=0.9)
        )
        
    ax.axhline(0, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='Situational Replacement Level (0.0)')
    ax.set_xlabel("Career Balls Faced Under Pressure Consideration (Deliveries)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Batting Reliability Score (PWSVA Shrunk Score, Runs/Ball)", fontsize=11, fontweight='bold')
    ax.set_title("Batting Reliability Under Pressure vs. Sample Size (N = 297 Batters)\nDemonstrating Empirical Bayes Shrinkage across Volume Tiers", fontsize=13, fontweight='bold', pad=14)
    ax.legend(loc='lower right', frameon=True, fontsize=9.5)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig03_batting_score_vs_sample_size.png'), dpi=300)
    plt.close(fig)
    print("  -> Saved Fig 03 successfully.")

    # --------------------------------------------------------------------------
    # 4. Figure 04: Bowling Reliability Score vs. Sample Size
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 04] Bowling Score vs Sample Size...")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    
    ax.scatter(bowl_df['Raw opportunities'], bowl_df['Shrunk score'], color='#a1d99b', alpha=0.65, edgecolors='#2ca02c', s=35, label='All 292 Qualifying Bowlers')
    
    top10_bw_all = bowl_df.head(10)
    ax.scatter(top10_bw_all['Raw opportunities'], top10_bw_all['Shrunk score'], color='#2ca02c', edgecolors='black', s=95, linewidth=1.2, zorder=5, label='Top 10 Bowlers')
    
    # Distinct quadrant offsets to guarantee zero overlap between Josh Hazlewood (#4) and Sunil Narine (#3)
    offsets_bowl = {
        1: (-210, 0.014),     # Rashid: top-left
        2: (50, 0.014),       # Bumrah: top-right
        3: (45, 0.016),       # Sunil Narine: top-right (1464b, +0.144) -> moves away from Hazlewood
        4: (-230, -0.022),    # Josh Hazlewood: bottom-left (1368b, +0.133) -> moves away from Narine
        5: (50, -0.016),      # Wanindu Hasaranga: bottom-right (1932b, +0.118)
    }
    for _, r in top10_bw_all.head(5).iterrows():
        rk = int(r['Rank'])
        dx, dy = offsets_bowl.get(rk, (50, 0.012))
        ax.annotate(
            f"#{rk} {r['Player']}\n(+{r['Shrunk score']:.3f})",
            (r['Raw opportunities'], r['Shrunk score']),
            xytext=(r['Raw opportunities'] + dx, r['Shrunk score'] + dy),
            fontsize=8.5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.88),
            arrowprops=dict(arrowstyle='->', color='#333333', lw=0.9)
        )
        
    ax.axhline(0, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='Situational Replacement Level (0.0)')
    ax.set_xlabel("Career Legal Deliveries Bowled Under Consideration (Balls)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Bowling Reliability Score (SBVA Shrunk Score, Runs Saved/Ball)", fontsize=11, fontweight='bold')
    ax.set_title("Bowling Reliability Under Pressure vs. Sample Size (N = 292 Bowlers)\nDemonstrating Empirical Bayes Shrinkage across Volume Tiers", fontsize=13, fontweight='bold', pad=14)
    ax.legend(loc='lower right', frameon=True, fontsize=9.5)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig04_bowling_score_vs_sample_size.png'), dpi=300)
    plt.close(fig)
    print("  -> Saved Fig 04 successfully.")

if __name__ == '__main__':
    regenerate_figures()
