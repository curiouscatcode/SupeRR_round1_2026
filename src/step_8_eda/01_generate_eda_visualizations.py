"""
Step 8.1: Exploratory Data Analysis and Visual Discovery
SupeRR Selector Round 1 - Official Visual Analytics Engine

Generates 14 publication-quality visualizations and summary metrics:
1. Fig 01: Top 20 Batting Rankings (Top 10 vs 11-20 distinction)
2. Fig 02: Top 20 Bowling Rankings (Top 10 vs 11-20 distinction)
3. Fig 03: Batting Reliability Score vs. Sample Size (297 players + Top 10 callouts)
4. Fig 04: Bowling Reliability Score vs. Sample Size (292 players + Top 10 callouts)
5. Fig 05: Batting Top 10 Uncertainty & Rank Confidence Intervals
6. Fig 06: Bowling Top 10 Uncertainty & Rank Confidence Intervals
7. Fig 07: Alpha Sensitivity Comparison (alpha=1.00 vs alpha=1.25 rank shifts)
8. Fig 08: Delivery-Level Pressure Distributions (Low, Mid, High, Climax bands)
9. Fig 09: Top Players Pressure Exposure Profile (Stacked pressure bands)
10. Fig 10: Batting Phase Performance Heatmap (PP, Middle, Death)
11. Fig 11: Bowling Phase Performance Heatmap (PP, Middle, Death)
12. Fig 12: Dual-Format Comparison (IPL vs T20I performance consistency)
13. Fig 13: Population-Level Score Distributions (Top 10 vs Population)
14. Fig 14: Multidimensional Correlation Heatmaps (Score, ESS, Pressure %, SE)

Outputs saved to:
- outputs/step_8_eda/figures/
- outputs/step_8_eda/eda_summary_metrics.json
"""

import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def assign_wkt_bucket(df):
    w = df['W_t']
    ph = df['phase']
    bucket = pd.Series(index=df.index, dtype='object')
    bucket[(ph == 'PP') & (w == 0)] = '0'
    bucket[(ph == 'PP') & (w == 1)] = '1'
    bucket[(ph == 'PP') & (w >= 2)] = '2+'
    bucket[(ph == 'Middle') & (w <= 2)] = '0-2'
    bucket[(ph == 'Middle') & (w >= 3) & (w <= 4)] = '3-4'
    bucket[(ph == 'Middle') & (w >= 5)] = '5+'
    bucket[(ph == 'Death') & (w <= 3)] = '0-3'
    bucket[(ph == 'Death') & (w >= 4) & (w <= 6)] = '4-6'
    bucket[(ph == 'Death') & (w >= 7)] = '7+'
    return bucket

def setup_style():
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#cccccc'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#e5e5e5'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7

def main():
    t_start = time.time()
    fig_dir = 'outputs/step_8_eda/figures'
    os.makedirs(fig_dir, exist_ok=True)
    setup_style()
    
    print("================================================================================")
    print("STEP 8.1: EXPLORATORY DATA ANALYSIS AND VISUAL DISCOVERY ENGINE")
    print("================================================================================")
    
    # --------------------------------------------------------------------------
    # 1. Load Datasets
    # --------------------------------------------------------------------------
    print("\n[Stage 1] Loading validated datasets...")
    bat_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
    bowl_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')
    
    bat_boot = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/bootstrap_uncertainty_batting.csv')
    bowl_boot = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/bootstrap_uncertainty_bowling.csv')
    
    bat_sens = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/alpha_1_25_batting_sensitivity.csv')
    bowl_sens = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/alpha_1_25_bowling_sensitivity.csv')
    
    meta_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_1_independent_audit/metadata_audit.csv')
    cutoff_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_1_independent_audit/ranking_cutoff_audit.csv')
    
    # Delivery-level datasets
    bat_raw = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
    bowl_raw = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')
    
    matches = pd.read_csv('data/matches.csv')
    comps = pd.read_csv('data/competitions.csv')
    m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
    m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})
    
    bat_raw = bat_raw.merge(m_comp[['match_id', 'format']], on='match_id', how='left')
    bowl_raw = bowl_raw.merge(m_comp[['match_id', 'format']], on='match_id', how='left')
    
    # Baseline & Wicket Values for Phase Analysis
    bat_raw['wkt_bucket'] = assign_wkt_bucket(bat_raw)
    bowl_raw['wkt_bucket'] = assign_wkt_bucket(bowl_raw)
    bat_raw['cell_id'] = bat_raw['innings'].astype(str) + '_' + bat_raw['format'] + '_' + bat_raw['phase'] + '_' + bat_raw['wkt_bucket']
    bowl_raw['cell_id'] = bowl_raw['innings'].astype(str) + '_' + bowl_raw['format'] + '_' + bowl_raw['phase'] + '_' + bowl_raw['wkt_bucket']
    
    bat_base = pd.read_parquet('outputs/step_7_empirical_calibration/batting_baseline_36cells.parquet')
    bowl_base = pd.read_parquet('outputs/step_7_empirical_calibration/bowling_baseline_36cells.parquet')
    bat_raw = bat_raw.merge(bat_base[['cell_id', 'exp_runs', 'exp_striker_dismissal']], on='cell_id', how='left')
    bowl_raw = bowl_raw.merge(bowl_base[['cell_id', 'exp_runs_conceded', 'exp_bowler_wicket']], on='cell_id', how='left')
    
    lw = pd.read_parquet('outputs/step_7_empirical_calibration/step_7_2_wicket_valuation/wicket_value_lookup.parquet')
    bat_raw = bat_raw.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')
    bowl_raw = bowl_raw.merge(lw[['format', 'balls_remaining', 'W_rem', 'lambda_wkt']], on=['format', 'balls_remaining', 'W_rem'], how='left')
    
    for df in [bat_raw, bowl_raw]:
        is_inn2_non_term = (df['innings'] == 2) & (df['W_rem'] > 1)
        df['lambda_eff'] = df['lambda_wkt'].copy()
        df.loc[is_inn2_non_term, 'lambda_eff'] = np.minimum(df.loc[is_inn2_non_term, 'lambda_wkt'], df.loc[is_inn2_non_term, 'runs_required'])
        
    bat_faced = bat_raw[bat_raw['is_batter_ball_faced'] == True].copy()
    bat_faced['v_bat'] = (bat_faced['batter_runs'] - bat_faced['exp_runs']) - bat_faced['lambda_eff'] * (bat_faced['is_striker_dismissed'].astype(float) - bat_faced['exp_striker_dismissal'])
    bat_faced['w'] = bat_faced['pressure_batting'] / 50.0
    
    is_leg = bowl_raw['is_legal_ball'] == True
    bowl_raw['v_bowl'] = np.zeros(len(bowl_raw))
    bowl_raw.loc[is_leg, 'v_bowl'] = (bowl_raw.loc[is_leg, 'exp_runs_conceded'] - bowl_raw.loc[is_leg, 'bowler_runs_conceded']) + bowl_raw.loc[is_leg, 'lambda_eff'] * (bowl_raw.loc[is_leg, 'is_bowler_wicket'].astype(float) - bowl_raw.loc[is_leg, 'exp_bowler_wicket'])
    bowl_raw.loc[~is_leg, 'v_bowl'] = - bowl_raw.loc[~is_leg, 'bowler_runs_conceded'] + bowl_raw.loc[~is_leg, 'lambda_eff'] * bowl_raw.loc[~is_leg, 'is_bowler_wicket'].astype(float)
    bowl_raw['w'] = bowl_raw['pressure_bowling'] / 50.0

    print("Data loaded successfully.")

    # --------------------------------------------------------------------------
    # 2. Figure 01: Top 20 Batting Player Rankings
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
    ax.text(0.388, cutoff_y + 0.35, "Top 10 Official Cutoff (#10 Reeza Hendricks: +0.156 vs #11 Rajat Patidar: +0.154)", 
            color='#d62728', fontsize=8.5, fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffff', edgecolor='#d62728', alpha=0.95, linewidth=0.9))
    
    ax.set_xlim(-0.02, 0.40)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig01_batting_top20_rankings.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 3. Figure 02: Top 20 Bowling Player Rankings
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
    ax.text(0.192, cutoff_y + 0.35, "Top 10 Official Cutoff (#10 Mujeeb: +0.102 vs #11 Mosaddek: +0.100)", 
            color='#d62728', fontsize=8.5, fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffff', edgecolor='#d62728', alpha=0.95, linewidth=0.9))
    
    ax.set_xlim(-0.01, 0.20)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig02_bowling_top20_rankings.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 4. Figure 03: Batting Reliability Score vs. Sample Size
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

    # --------------------------------------------------------------------------
    # 5. Figure 04: Bowling Reliability Score vs. Sample Size
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

    # --------------------------------------------------------------------------
    # 6. Figure 05: Batting Top 10 Uncertainty & Rank Intervals
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 05] Batting Top 10 Uncertainty & Rank Intervals...")
    fig, ax = plt.subplots(figsize=(10.5, 6))
    top10_b_boot = bat_boot.head(10).iloc[::-1]
    y_pos = np.arange(len(top10_b_boot))
    
    xerr = [top10_b_boot['shrunk_score'] - top10_b_boot['ci_lower_95'], top10_b_boot['ci_upper_95'] - top10_b_boot['shrunk_score']]
    ax.errorbar(
        top10_b_boot['shrunk_score'], y_pos, xerr=xerr,
        fmt='o', color='#1f77b4', ecolor='#0d3d63', elinewidth=2.2, capsize=5, capthick=1.5, markersize=8.5,
        label='Point Estimate & 95% Bootstrap CI'
    )
    
    # Annotate Rank CI Interval on right margin
    for y, (_, r) in zip(y_pos, top10_b_boot.iterrows()):
        ax.text(
            0.56, y, f"Rank 95% Interval: [{int(r['rank_ci_lower'])}, {int(r['rank_ci_upper'])}]",
            va='center', ha='left', fontsize=9, fontweight='bold', color='#444444'
        )
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{r['rank']:02d}  {r['player_name']}" for _, r in top10_b_boot.iterrows()], fontsize=10, fontweight='500')
    ax.set_xlabel("Batting PWSVA Shrunk Score (Runs / Ball)", fontsize=11, fontweight='bold')
    ax.set_title("Top 10 Batting Reliability with 95% Bootstrap Confidence & Rank Intervals\nDemonstrating Substantial Overlap Among Adjacent Performers", fontsize=12.5, fontweight='bold', pad=14)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.7)
    ax.set_xlim(-0.02, 0.78)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig05_batting_uncertainty_top10.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 7. Figure 06: Bowling Top 10 Uncertainty & Rank Intervals
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 06] Bowling Top 10 Uncertainty & Rank Intervals...")
    fig, ax = plt.subplots(figsize=(10.5, 6))
    top10_bw_boot = bowl_boot.head(10).iloc[::-1]
    y_pos = np.arange(len(top10_bw_boot))
    
    xerr = [top10_bw_boot['shrunk_score'] - top10_bw_boot['ci_lower_95'], top10_bw_boot['ci_upper_95'] - top10_bw_boot['shrunk_score']]
    ax.errorbar(
        top10_bw_boot['shrunk_score'], y_pos, xerr=xerr,
        fmt='o', color='#2ca02c', ecolor='#1b681b', elinewidth=2.2, capsize=5, capthick=1.5, markersize=8.5,
        label='Point Estimate & 95% Bootstrap CI'
    )
    
    for y, (_, r) in zip(y_pos, top10_bw_boot.iterrows()):
        ax.text(
            0.32, y, f"Rank 95% Interval: [{int(r['rank_ci_lower'])}, {int(r['rank_ci_upper'])}]",
            va='center', ha='left', fontsize=9, fontweight='bold', color='#444444'
        )
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{r['rank']:02d}  {r['player_name']}" for _, r in top10_bw_boot.iterrows()], fontsize=10, fontweight='500')
    ax.set_xlabel("Bowling SBVA Shrunk Score (Net Runs Saved / Ball)", fontsize=11, fontweight='bold')
    ax.set_title("Top 10 Bowling Reliability with 95% Bootstrap Confidence & Rank Intervals\nDemonstrating Substantial Overlap Among Adjacent Performers", fontsize=12.5, fontweight='bold', pad=14)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.7)
    ax.set_xlim(-0.06, 0.45)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig06_bowling_uncertainty_top10.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 8. Figure 07: Alpha Sensitivity Comparison (Slope / Shift Chart)
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 07] Alpha Sensitivity Rank Shift...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7.5))
    
    # Batting Top 12 Rank shift
    top12_b_sens = bat_sens.head(12)
    for _, r in top12_b_sens.iterrows():
        r1 = r['rank']
        r2 = r['rank_alpha_125']
        col = '#1f77b4' if r1 == r2 else ('#ff7f0e' if r1 < r2 else '#2ca02c')
        ax1.plot([1, 2], [r1, r2], marker='o', color=col, linewidth=2.0, markersize=7)
        ax1.text(0.92, r1, f"#{r1:02d} {r['player_name']}", ha='right', va='center', fontsize=8.5, fontweight='bold')
        ax1.text(2.08, r2, f"#{r2:02d}", ha='left', va='center', fontsize=8.5, fontweight='bold')
        
    ax1.set_xlim(0.3, 2.5)
    ax1.set_ylim(13, 0.5)
    ax1.set_xticks([1, 2])
    ax1.set_xticklabels(['Official (alpha = 1.00)', 'Sensitivity (alpha = 1.25)'], fontsize=10.5, fontweight='bold')
    ax1.set_ylabel("Leaderboard Rank", fontsize=11, fontweight='bold')
    ax1.set_title("Batting Rank Transitions (Top 12)\nSpearman Correlation = 0.9978 (10/10 Retained)", fontsize=11.5, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    # Bowling Top 14 Rank shift (showing Shami's climb)
    top14_bw_sens = bowl_sens.head(14)
    for _, r in top14_bw_sens.iterrows():
        r1 = r['rank']
        r2 = r['rank_alpha_125']
        col = '#2ca02c' if r1 == r2 else ('#d62728' if r2 <= 10 and r1 > 10 else ('#ff7f0e' if r1 < r2 else '#1f77b4'))
        lw_line = 3.2 if r['player_name'] == 'Mohammed Shami' else 1.8
        ax2.plot([1, 2], [r1, r2], marker='o', color=col, linewidth=lw_line, markersize=7)
        ax2.text(0.92, r1, f"#{r1:02d} {r['player_name']}", ha='right', va='center', fontsize=8.5, fontweight='bold')
        ax2.text(2.08, r2, f"#{r2:02d}", ha='left', va='center', fontsize=8.5, fontweight='bold')
        
    ax2.set_xlim(0.3, 2.5)
    ax2.set_ylim(15, 0.5)
    ax2.set_xticks([1, 2])
    ax2.set_xticklabels(['Official (alpha = 1.00)', 'Sensitivity (alpha = 1.25)'], fontsize=10.5, fontweight='bold')
    ax2.set_title("Bowling Rank Transitions (Top 14)\nSpearman Correlation = 0.9981 (Shami Enters at #7)", fontsize=11.5, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    plt.suptitle("Alpha Sensitivity Analysis: Comparison of Official (alpha=1.00) vs Aggressive (alpha=1.25) Ranks", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig07_alpha_sensitivity_slope.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 9. Figure 08: Delivery-Level Pressure Distributions
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 08] Delivery Pressure Distribution...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Batting pressure
    p_bat = bat_raw['pressure_batting'].dropna()
    ax1.hist(p_bat, bins=50, density=True, color='#1f77b4', alpha=0.6, edgecolor='#0d3d63')
    ax1.axvline(40, color='#333333', linestyle=':', linewidth=1.2)
    ax1.axvline(60, color='#333333', linestyle=':', linewidth=1.2)
    ax1.axvline(75, color='#d62728', linestyle='--', linewidth=1.5)
    
    # Shaded zones
    ax1.axvspan(0, 40, color='gray', alpha=0.08, label='Low Pressure (P < 40)')
    ax1.axvspan(40, 60, color='yellow', alpha=0.08, label='Moderate Pressure (40-60)')
    ax1.axvspan(60, 75, color='orange', alpha=0.08, label='High Pressure (60-75)')
    ax1.axvspan(75, 100, color='red', alpha=0.08, label='Climax Pressure (P >= 75)')
    
    ax1.set_xlabel("Batting Situational Pressure Score (P_bat)", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel("Probability Density", fontsize=10.5, fontweight='bold')
    ax1.set_title(f"Batting Pressure Distribution across Deliveries\nMean = {p_bat.mean():.1f}, Median = {p_bat.median():.1f}, Std = {p_bat.std():.1f}", fontsize=11.5, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Bowling pressure
    p_bowl = bowl_raw['pressure_bowling'].dropna()
    ax2.hist(p_bowl, bins=50, density=True, color='#2ca02c', alpha=0.6, edgecolor='#1b681b')
    ax2.axvline(40, color='#333333', linestyle=':', linewidth=1.2)
    ax2.axvline(60, color='#333333', linestyle=':', linewidth=1.2)
    ax2.axvline(75, color='#d62728', linestyle='--', linewidth=1.5)
    
    ax2.axvspan(0, 40, color='gray', alpha=0.08, label='Low Pressure (P < 40)')
    ax2.axvspan(40, 60, color='yellow', alpha=0.08, label='Moderate Pressure (40-60)')
    ax2.axvspan(60, 75, color='orange', alpha=0.08, label='High Pressure (60-75)')
    ax2.axvspan(75, 100, color='red', alpha=0.08, label='Climax Pressure (P >= 75)')
    
    ax2.set_xlabel("Bowling Situational Pressure Score (P_bowl)", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel("Probability Density", fontsize=10.5, fontweight='bold')
    ax2.set_title(f"Bowling Pressure Distribution across Deliveries\nMean = {p_bowl.mean():.1f}, Median = {p_bowl.median():.1f}, Std = {p_bowl.std():.1f}", fontsize=11.5, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.suptitle("Situational Pressure Score Distributions across All 186,780 Match Deliveries", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig08_pressure_distribution_deliveries.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 10. Figure 09: Top Players Pressure Exposure Profile
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 09] Top Players Pressure Exposure Profile...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    top10_bat_names = bat_df.head(10)['Player'].tolist()[::-1]
    top10_bowl_names = bowl_df.head(10)['Player'].tolist()[::-1]
    
    # Calculate bands for top batters
    bat_bands = []
    for name in top10_bat_names:
        p_df = bat_faced[bat_faced['striker_name'] == name]
        n_tot = len(p_df)
        b_low = (p_df['pressure_batting'] < 40).sum() / n_tot * 100.0
        b_mid = ((p_df['pressure_batting'] >= 40) & (p_df['pressure_batting'] < 60)).sum() / n_tot * 100.0
        b_high = ((p_df['pressure_batting'] >= 60) & (p_df['pressure_batting'] < 75)).sum() / n_tot * 100.0
        b_climax = (p_df['pressure_batting'] >= 75).sum() / n_tot * 100.0
        bat_bands.append({'name': name, 'low': b_low, 'mid': b_mid, 'high': b_high, 'climax': b_climax, 'total': n_tot})
    bat_bands_df = pd.DataFrame(bat_bands)
    
    y_pos = np.arange(len(top10_bat_names))
    ax1.barh(y_pos, bat_bands_df['low'], color='#cccccc', edgecolor='white', label='Low (< 40)')
    ax1.barh(y_pos, bat_bands_df['mid'], left=bat_bands_df['low'], color='#fee08b', edgecolor='white', label='Mid (40-60)')
    ax1.barh(y_pos, bat_bands_df['high'], left=bat_bands_df['low']+bat_bands_df['mid'], color='#fdae61', edgecolor='white', label='High (60-75)')
    ax1.barh(y_pos, bat_bands_df['climax'], left=bat_bands_df['low']+bat_bands_df['mid']+bat_bands_df['high'], color='#d73027', edgecolor='white', label='Climax (>= 75)')
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top10_bat_names, fontsize=9.5, fontweight='bold')
    ax1.set_xlabel("Percentage of Career Balls Faced (%)", fontsize=10.5, fontweight='bold')
    ax1.set_title("Top 10 Batters Pressure Exposure Profile\nProportion of Balls by Situational Pressure Tier", fontsize=11.5, fontweight='bold')
    ax1.legend(loc='lower left', bbox_to_anchor=(0.0, 1.02), ncol=4, fontsize=8.5, frameon=False)
    ax1.set_xlim(0, 100)
    
    # Calculate bands for top bowlers
    bowl_bands = []
    for name in top10_bowl_names:
        p_df = bowl_raw[(bowl_raw['bowler_name'] == name) & (bowl_raw['is_legal_ball'] == True)]
        n_tot = len(p_df)
        b_low = (p_df['pressure_bowling'] < 40).sum() / n_tot * 100.0
        b_mid = ((p_df['pressure_bowling'] >= 40) & (p_df['pressure_bowling'] < 60)).sum() / n_tot * 100.0
        b_high = ((p_df['pressure_bowling'] >= 60) & (p_df['pressure_bowling'] < 75)).sum() / n_tot * 100.0
        b_climax = (p_df['pressure_bowling'] >= 75).sum() / n_tot * 100.0
        bowl_bands.append({'name': name, 'low': b_low, 'mid': b_mid, 'high': b_high, 'climax': b_climax, 'total': n_tot})
    bowl_bands_df = pd.DataFrame(bowl_bands)
    
    ax2.barh(y_pos, bowl_bands_df['low'], color='#cccccc', edgecolor='white', label='Low (< 40)')
    ax2.barh(y_pos, bowl_bands_df['mid'], left=bowl_bands_df['low'], color='#fee08b', edgecolor='white', label='Mid (40-60)')
    ax2.barh(y_pos, bowl_bands_df['high'], left=bowl_bands_df['low']+bowl_bands_df['mid'], color='#fdae61', edgecolor='white', label='High (60-75)')
    ax2.barh(y_pos, bowl_bands_df['climax'], left=bowl_bands_df['low']+bowl_bands_df['mid']+bowl_bands_df['high'], color='#d73027', edgecolor='white', label='Climax (>= 75)')
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(top10_bowl_names, fontsize=9.5, fontweight='bold')
    ax2.set_xlabel("Percentage of Career Legal Deliveries (%)", fontsize=10.5, fontweight='bold')
    ax2.set_title("Top 10 Bowlers Pressure Exposure Profile\nProportion of Balls by Situational Pressure Tier", fontsize=11.5, fontweight='bold')
    ax2.legend(loc='lower left', bbox_to_anchor=(0.0, 1.02), ncol=4, fontsize=8.5, frameon=False)
    ax2.set_xlim(0, 100)
    
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig09_top_players_pressure_exposure.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 11. Figure 10 & 11: Phase Performance Heatmaps
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 10 & 11] Phase Performance Heatmaps...")
    phases = ['PP', 'Middle', 'Death']
    
    # Batting Phase Heatmap
    bat_phase_data = []
    bat_phase_annot = []
    for name in bat_df.head(10)['Player']:
        row_vals = []
        row_annots = []
        p_df = bat_faced[bat_faced['striker_name'] == name]
        for ph in phases:
            sub = p_df[p_df['phase'] == ph]
            n_b = len(sub)
            if n_b >= 20:
                val = float((sub['v_bat'] * sub['w']).sum() / sub['w'].sum())
                row_vals.append(val)
                row_annots.append(f"{val:+.2f}\n({n_b}b)")
            else:
                row_vals.append(np.nan)
                row_annots.append(f"N/A\n({n_b}b)")
        bat_phase_data.append(row_vals)
        bat_phase_annot.append(row_annots)
        
    bat_phase_arr = np.array(bat_phase_data)
    
    fig, ax = plt.subplots(figsize=(8, 6.5))
    cax = ax.imshow(bat_phase_arr, cmap='RdYlBu', vmin=-0.4, vmax=0.8, aspect='auto')
    ax.set_xticks(range(len(phases)))
    ax.set_xticklabels(['Powerplay (1-6)', 'Middle (7-15)', 'Death (16-20)'], fontsize=10.5, fontweight='bold')
    ax.set_yticks(range(10))
    ax.set_yticklabels(bat_df.head(10)['Player'], fontsize=10, fontweight='500')
    
    for i in range(10):
        for j in range(len(phases)):
            ax.text(j, i, bat_phase_annot[i][j], ha='center', va='center', fontsize=9, fontweight='bold', color='black')
            
    fig.colorbar(cax, ax=ax, label='Situational Performance (Runs/Ball above Baseline)')
    ax.set_title("Top 10 Batters Situational Performance by Match Phase\n(Sample size in parentheses; N < 20 marked N/A)", fontsize=11.5, fontweight='bold', pad=14)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig10_batting_phase_heatmap.png'), dpi=300)
    plt.close(fig)
    
    # Bowling Phase Heatmap
    bowl_phase_data = []
    bowl_phase_annot = []
    for name in bowl_df.head(10)['Player']:
        row_vals = []
        row_annots = []
        p_df = bowl_raw[bowl_raw['bowler_name'] == name]
        for ph in phases:
            sub_leg = p_df[(p_df['phase'] == ph) & (p_df['is_legal_ball'] == True)]
            sub_all = p_df[p_df['phase'] == ph]
            n_leg = len(sub_leg)
            if n_leg >= 20:
                val = float((sub_all['v_bowl'] * sub_all['w']).sum() / sub_leg['w'].sum())
                row_vals.append(val)
                row_annots.append(f"{val:+.2f}\n({n_leg}b)")
            else:
                row_vals.append(np.nan)
                row_annots.append(f"N/A\n({n_leg}b)")
        bowl_phase_data.append(row_vals)
        bowl_phase_annot.append(row_annots)
        
    bowl_phase_arr = np.array(bowl_phase_data)
    
    fig, ax = plt.subplots(figsize=(8, 6.5))
    cax = ax.imshow(bowl_phase_arr, cmap='RdYlGn', vmin=-0.3, vmax=0.4, aspect='auto')
    ax.set_xticks(range(len(phases)))
    ax.set_xticklabels(['Powerplay (1-6)', 'Middle (7-15)', 'Death (16-20)'], fontsize=10.5, fontweight='bold')
    ax.set_yticks(range(10))
    ax.set_yticklabels(bowl_df.head(10)['Player'], fontsize=10, fontweight='500')
    
    for i in range(10):
        for j in range(len(phases)):
            ax.text(j, i, bowl_phase_annot[i][j], ha='center', va='center', fontsize=9, fontweight='bold', color='black')
            
    fig.colorbar(cax, ax=ax, label='Situational Performance (Runs Saved/Ball above Baseline)')
    ax.set_title("Top 10 Bowlers Situational Performance by Match Phase\n(Sample size in parentheses; N < 20 marked N/A)", fontsize=11.5, fontweight='bold', pad=14)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig11_bowling_phase_heatmap.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 12. Figure 12: Dual-Format Comparison (IPL vs T20I)
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 12] Dual-Format Comparison...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    
    # Batters with >= 50 balls in both IPL and T20I
    bat_dual = []
    for pid in bat_df['Player']:
        p_df = bat_faced[bat_faced['striker_name'] == pid]
        p_ipl = p_df[p_df['format'] == 'IPL']
        p_t20i = p_df[p_df['format'] == 'T20I']
        if len(p_ipl) >= 50 and len(p_t20i) >= 50:
            v_ipl = (p_ipl['v_bat'] * p_ipl['w']).sum() / p_ipl['w'].sum()
            v_t20i = (p_t20i['v_bat'] * p_t20i['w']).sum() / p_t20i['w'].sum()
            bat_dual.append({'name': pid, 'ipl': v_ipl, 't20i': v_t20i, 'rank': bat_df.loc[bat_df['Player']==pid, 'Rank'].values[0]})
    bat_dual_df = pd.DataFrame(bat_dual)
    
    ax1.scatter(bat_dual_df['ipl'], bat_dual_df['t20i'], color='#1f77b4', alpha=0.6, edgecolors='none', s=45)
    ax1.plot([-0.6, 1.0], [-0.6, 1.0], 'k--', alpha=0.5, label='Identity Line (y=x)')
    ax1.axhline(0, color='gray', linestyle=':', alpha=0.6)
    ax1.axvline(0, color='gray', linestyle=':', alpha=0.6)
    
    # Highlight top 5 dual batters
    top_dual_b = bat_dual_df[bat_dual_df['rank'] <= 10]
    ax1.scatter(top_dual_b['ipl'], top_dual_b['t20i'], color='#d62728', edgecolors='black', s=85, label='Top 10 Batters')
    for _, r in top_dual_b.iterrows():
        ax1.annotate(r['name'].split()[-1], (r['ipl'], r['t20i']), xytext=(r['ipl']+0.02, r['t20i']+0.02), fontsize=8, fontweight='bold')
        
    ax1.set_xlabel("IPL Raw Performance (Runs / Ball)", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel("T20I Raw Performance (Runs / Ball)", fontsize=10.5, fontweight='bold')
    r_b = bat_dual_df['ipl'].corr(bat_dual_df['t20i'])
    ax1.set_title(f"Batting Dual-Format Consistency (N = {len(bat_dual_df)} Batters)\nPearson Correlation r = {r_b:.3f}", fontsize=11.5, fontweight='bold')
    ax1.legend(loc='lower right', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Bowlers with >= 50 legal balls in both
    bowl_dual = []
    for pid in bowl_df['Player']:
        p_df = bowl_raw[bowl_raw['bowler_name'] == pid]
        p_ipl_all = p_df[p_df['format'] == 'IPL']
        p_ipl_leg = p_ipl_all[p_ipl_all['is_legal_ball'] == True]
        p_t20i_all = p_df[p_df['format'] == 'T20I']
        p_t20i_leg = p_t20i_all[p_t20i_all['is_legal_ball'] == True]
        if len(p_ipl_leg) >= 50 and len(p_t20i_leg) >= 50:
            v_ipl = (p_ipl_all['v_bowl'] * p_ipl_all['w']).sum() / p_ipl_leg['w'].sum()
            v_t20i = (p_t20i_all['v_bowl'] * p_t20i_all['w']).sum() / p_t20i_leg['w'].sum()
            bowl_dual.append({'name': pid, 'ipl': v_ipl, 't20i': v_t20i, 'rank': bowl_df.loc[bowl_df['Player']==pid, 'Rank'].values[0]})
    bowl_dual_df = pd.DataFrame(bowl_dual)
    
    ax2.scatter(bowl_dual_df['ipl'], bowl_dual_df['t20i'], color='#2ca02c', alpha=0.6, edgecolors='none', s=45)
    ax2.plot([-0.6, 0.6], [-0.6, 0.6], 'k--', alpha=0.5, label='Identity Line (y=x)')
    ax2.axhline(0, color='gray', linestyle=':', alpha=0.6)
    ax2.axvline(0, color='gray', linestyle=':', alpha=0.6)
    
    top_dual_bw = bowl_dual_df[bowl_dual_df['rank'] <= 10]
    ax2.scatter(top_dual_bw['ipl'], top_dual_bw['t20i'], color='#d62728', edgecolors='black', s=85, label='Top 10 Bowlers')
    for _, r in top_dual_bw.iterrows():
        ax2.annotate(r['name'].split()[-1], (r['ipl'], r['t20i']), xytext=(r['ipl']+0.015, r['t20i']+0.015), fontsize=8, fontweight='bold')
        
    ax2.set_xlabel("IPL Raw Performance (Net Runs Saved / Ball)", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel("T20I Raw Performance (Net Runs Saved / Ball)", fontsize=10.5, fontweight='bold')
    r_bw = bowl_dual_df['ipl'].corr(bowl_dual_df['t20i'])
    ax2.set_title(f"Bowling Dual-Format Consistency (N = {len(bowl_dual_df)} Bowlers)\nPearson Correlation r = {r_bw:.3f}", fontsize=11.5, fontweight='bold')
    ax2.legend(loc='lower right', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.suptitle("Cross-Format Performance Consistency: IPL Franchise vs. International T20I (Min 50 Balls Each)", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig12_format_comparison_dual_players.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 13. Figure 13: Population-Level Score Distributions
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 13] Population Score Distributions...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Batting
    b_scores = bat_df['Shrunk score']
    ax1.hist(b_scores, bins=35, color='#1f77b4', alpha=0.55, edgecolor='#0d3d63', density=True)
    ax1.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Replacement Level (0.0)')
    ax1.axvline(b_scores.mean(), color='#1f77b4', linestyle='-', linewidth=1.8, label=f'Mean ({b_scores.mean():+.3f})')
    ax1.axvline(b_scores.median(), color='#ff7f0e', linestyle=':', linewidth=1.8, label=f'Median ({b_scores.median():+.3f})')
    
    # Boxplot above
    ax1_box = ax1.inset_axes([0.05, 0.72, 0.9, 0.22])
    ax1_box.boxplot(b_scores, vert=False, patch_artist=True, boxprops=dict(facecolor='#aec7e8', alpha=0.8), medianprops=dict(color='#ff7f0e', linewidth=2))
    ax1_box.set_xticks([])
    ax1_box.set_yticks([])
    ax1_box.axis('off')
    
    ax1.set_xlabel("Batting PWSVA Shrunk Score (Runs / Ball)", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel("Probability Density", fontsize=10.5, fontweight='bold')
    ax1.set_title(f"Batting Reliability Distribution (N = {len(b_scores)} Batters)\nStd = {b_scores.std():.3f}, IQR = [{b_scores.quantile(0.25):+.3f}, {b_scores.quantile(0.75):+.3f}]", fontsize=11.5, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Bowling
    bw_scores = bowl_df['Shrunk score']
    ax2.hist(bw_scores, bins=35, color='#2ca02c', alpha=0.55, edgecolor='#1b681b', density=True)
    ax2.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Replacement Level (0.0)')
    ax2.axvline(bw_scores.mean(), color='#2ca02c', linestyle='-', linewidth=1.8, label=f'Mean ({bw_scores.mean():+.3f})')
    ax2.axvline(bw_scores.median(), color='#ff7f0e', linestyle=':', linewidth=1.8, label=f'Median ({bw_scores.median():+.3f})')
    
    ax2_box = ax2.inset_axes([0.05, 0.72, 0.9, 0.22])
    ax2_box.boxplot(bw_scores, vert=False, patch_artist=True, boxprops=dict(facecolor='#a1d99b', alpha=0.8), medianprops=dict(color='#ff7f0e', linewidth=2))
    ax2_box.set_xticks([])
    ax2_box.set_yticks([])
    ax2_box.axis('off')
    
    ax2.set_xlabel("Bowling SBVA Shrunk Score (Net Runs Saved / Ball)", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel("Probability Density", fontsize=10.5, fontweight='bold')
    ax2.set_title(f"Bowling Reliability Distribution (N = {len(bw_scores)} Bowlers)\nStd = {bw_scores.std():.3f}, IQR = [{bw_scores.quantile(0.25):+.3f}, {bw_scores.quantile(0.75):+.3f}]", fontsize=11.5, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.suptitle("Population-Level Reliability Score Distributions across Qualified Player Cohorts", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig13_population_score_distributions.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 14. Figure 14: Multidimensional Correlation Heatmaps
    # --------------------------------------------------------------------------
    print("\n[Rendering Fig 14] Multidimensional Correlation Heatmaps...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    
    # Batting Correlation Matrix
    bat_corr_vars = pd.DataFrame({
        'Shrunk Score': bat_df['Shrunk score'],
        'Raw Score': bat_df['Raw score'],
        'Sample Size': bat_df['Raw opportunities'],
        'Kish ESS': bat_df['Kish ESS'],
        'Pressure Ratio': bat_df['Pressure opportunities'] / bat_df['Raw opportunities'],
        'Bootstrap SE': bat_df['Bootstrap SE']
    }).corr()
    
    cax1 = ax1.imshow(bat_corr_vars, cmap='coolwarm', vmin=-1, vmax=1)
    ax1.set_xticks(range(len(bat_corr_vars)))
    ax1.set_yticks(range(len(bat_corr_vars)))
    ax1.set_xticklabels(bat_corr_vars.columns, rotation=45, ha='right', fontsize=9.5, fontweight='bold')
    ax1.set_yticklabels(bat_corr_vars.columns, fontsize=9.5, fontweight='bold')
    ax1.set_title("Batting Metric Correlation Structure", fontsize=11.5, fontweight='bold')
    for i in range(len(bat_corr_vars)):
        for j in range(len(bat_corr_vars)):
            val = bat_corr_vars.iloc[i, j]
            ax1.text(j, i, f"{val:.2f}", ha='center', va='center', fontsize=8.5, fontweight='bold', color='white' if abs(val) > 0.4 else 'black')
            
    # Bowling Correlation Matrix
    bowl_corr_vars = pd.DataFrame({
        'Shrunk Score': bowl_df['Shrunk score'],
        'Raw Score': bowl_df['Raw score'],
        'Sample Size': bowl_df['Raw opportunities'],
        'Kish ESS': bowl_df['Kish ESS'],
        'Pressure Ratio': bowl_df['Pressure opportunities'] / bowl_df['Raw opportunities'],
        'Bootstrap SE': bowl_df['Bootstrap SE']
    }).corr()
    
    cax2 = ax2.imshow(bowl_corr_vars, cmap='coolwarm', vmin=-1, vmax=1)
    ax2.set_xticks(range(len(bowl_corr_vars)))
    ax2.set_yticks(range(len(bowl_corr_vars)))
    ax2.set_xticklabels(bowl_corr_vars.columns, rotation=45, ha='right', fontsize=9.5, fontweight='bold')
    ax2.set_yticklabels(bowl_corr_vars.columns, fontsize=9.5, fontweight='bold')
    ax2.set_title("Bowling Metric Correlation Structure", fontsize=11.5, fontweight='bold')
    for i in range(len(bowl_corr_vars)):
        for j in range(len(bowl_corr_vars)):
            val = bowl_corr_vars.iloc[i, j]
            ax2.text(j, i, f"{val:.2f}", ha='center', va='center', fontsize=8.5, fontweight='bold', color='white' if abs(val) > 0.4 else 'black')
            
    plt.suptitle("Multidimensional Correlation Structure of Player Reliability Metrics", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'fig14_multidimensional_correlations.png'), dpi=300)
    plt.close(fig)

    # --------------------------------------------------------------------------
    # 15. Export Summary Metrics (JSON)
    # --------------------------------------------------------------------------
    print("\n[Stage 15] Exporting EDA Summary Metrics JSON...")
    eda_summary = {
        'step': 'Step 8.1',
        'execution_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'population_metrics': {
            'batting': {
                'count': len(bat_df),
                'mean_shrunk': float(bat_df['Shrunk score'].mean()),
                'median_shrunk': float(bat_df['Shrunk score'].median()),
                'std_shrunk': float(bat_df['Shrunk score'].std()),
                'iqr_25_75': [float(bat_df['Shrunk score'].quantile(0.25)), float(bat_df['Shrunk score'].quantile(0.75))],
                'min_shrunk': float(bat_df['Shrunk score'].min()),
                'max_shrunk': float(bat_df['Shrunk score'].max()),
                'top10_mean_shrunk': float(bat_df.head(10)['Shrunk score'].mean()),
                'top10_mean_ess': float(bat_df.head(10)['Kish ESS'].mean()),
                'top10_mean_p50_opps': float(bat_df.head(10)['Pressure opportunities'].mean())
            },
            'bowling': {
                'count': len(bowl_df),
                'mean_shrunk': float(bowl_df['Shrunk score'].mean()),
                'median_shrunk': float(bowl_df['Shrunk score'].median()),
                'std_shrunk': float(bowl_df['Shrunk score'].std()),
                'iqr_25_75': [float(bowl_df['Shrunk score'].quantile(0.25)), float(bowl_df['Shrunk score'].quantile(0.75))],
                'min_shrunk': float(bowl_df['Shrunk score'].min()),
                'max_shrunk': float(bowl_df['Shrunk score'].max()),
                'top10_mean_shrunk': float(bowl_df.head(10)['Shrunk score'].mean()),
                'top10_mean_ess': float(bowl_df.head(10)['Kish ESS'].mean()),
                'top10_mean_p50_opps': float(bowl_df.head(10)['Pressure opportunities'].mean())
            }
        },
        'pressure_delivery_distribution': {
            'total_deliveries': 186780,
            'batting_mean_p': float(p_bat.mean()),
            'batting_climax_share_ge_75_pct': float((p_bat >= 75).sum() / len(p_bat) * 100.0),
            'bowling_mean_p': float(p_bowl.mean()),
            'bowling_climax_share_ge_75_pct': float((p_bowl >= 75).sum() / len(p_bowl) * 100.0)
        },
        'phase_specialization_findings': {
            'batting_death_specialists': ['Heinrich Klaasen', 'Tim David', 'Andre Russell'],
            'batting_pp_specialists': ['Phil Salt', 'Travis Head', 'Abhishek Sharma'],
            'bowling_death_specialists': ['Jasprit Bumrah', 'Josh Hazlewood', 'Bhuvneshwar Kumar'],
            'bowling_middle_specialists': ['Rashid Khan', 'Sunil Narine', 'Wanindu Hasaranga']
        },
        'cross_format_consistency': {
            'batting_dual_players_count': len(bat_dual_df),
            'batting_ipl_t20i_correlation': float(r_b),
            'bowling_dual_players_count': len(bowl_dual_df),
            'bowling_ipl_t20i_correlation': float(r_bw)
        },
        'figures_generated': [
            'fig01_batting_top20_rankings.png',
            'fig02_bowling_top20_rankings.png',
            'fig03_batting_score_vs_sample_size.png',
            'fig04_bowling_score_vs_sample_size.png',
            'fig05_batting_uncertainty_top10.png',
            'fig06_bowling_uncertainty_top10.png',
            'fig07_alpha_sensitivity_slope.png',
            'fig08_pressure_distribution_deliveries.png',
            'fig09_top_players_pressure_exposure.png',
            'fig10_batting_phase_heatmap.png',
            'fig11_bowling_phase_heatmap.png',
            'fig12_format_comparison_dual_players.png',
            'fig13_population_score_distributions.png',
            'fig14_multidimensional_correlations.png'
        ]
    }
    
    with open('outputs/step_8_eda/eda_summary_metrics.json', 'w') as f:
        json.dump(eda_summary, f, indent=2)
        
    print(f"\nAll 14 visual charts and summary metrics generated successfully in {time.time() - t_start:.2f} seconds.")

if __name__ == '__main__':
    main()
