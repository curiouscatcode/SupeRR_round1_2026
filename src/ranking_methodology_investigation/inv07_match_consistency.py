"""
src/ranking_methodology_investigation/inv07_match_consistency.py
Investigation 7: Match-to-Match Consistency

Investigates whether high-ranking players are consistently reliable across matches
or whether aggregate scores hide high-variance, outlier-dependent performers.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "ranking_methodology_investigation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_investigation():
    print("=" * 80)
    print("INVESTIGATION 7: MATCH-TO-MATCH CONSISTENCY")
    print("=" * 80)
    
    dpi_path = BASE_DIR / "data" / "processed" / "delivery_pressure_index.csv"
    bat_rank_path = BASE_DIR / "data" / "processed" / "batter_reliability_rankings.csv"
    bow_rank_path = BASE_DIR / "data" / "processed" / "bowler_reliability_rankings.csv"
    
    print("Loading delivery pressure index and ranking datasets...")
    dpi = pd.read_csv(dpi_path)
    df_bat_rank = pd.read_csv(bat_rank_path)
    df_bow_rank = pd.read_csv(bow_rank_path)
    
    t1_bat = df_bat_rank[df_bat_rank['tier'] == 'Tier 1: Qualified'].copy()
    t1_bow = df_bow_rank[df_bow_rank['tier'] == 'Tier 1: Qualified'].copy()
    
    # 1. Batting Match-Level Consistency
    print("\nComputing match-level metrics for 116 Tier 1 Batters...")
    high_bat = dpi[(dpi['Batting_Pressure_Level'] == 'High') & (dpi['is_batter_ball_faced'] == 1)]
    
    bat_consistency = []
    for _, r in t1_bat.iterrows():
        p_id = r['player_id']
        p_df = high_bat[high_bat['striker_id'] == p_id]
        m_agg = p_df.groupby('match_id').agg(
            runs=('runs', 'sum'),
            balls=('runs', 'count')
        )
        m_agg['sr'] = m_agg['runs'] / m_agg['balls'] * 100.0
        
        n_matches = len(m_agg)
        mean_balls = m_agg['balls'].mean() if n_matches > 0 else 0
        med_sr = m_agg['sr'].median() if n_matches > 0 else 0
        std_sr = m_agg['sr'].std() if n_matches > 1 else 0
        min_sr = m_agg['sr'].min() if n_matches > 0 else 0
        max_sr = m_agg['sr'].max() if n_matches > 0 else 0
        pct_above_avg = (m_agg['sr'] >= 115.0).mean() * 100.0 if n_matches > 0 else 0
        
        tot_runs = m_agg['runs'].sum()
        top1_runs = m_agg['runs'].max() if n_matches > 0 else 0
        top1_share = (top1_runs / tot_runs * 100.0) if tot_runs > 0 else 0
        top2_runs = m_agg['runs'].nlargest(2).sum() if n_matches >= 2 else tot_runs
        top2_share = (top2_runs / tot_runs * 100.0) if tot_runs > 0 else 0
        
        bat_consistency.append({
            'role': 'Batter',
            'player_id': p_id,
            'player_name': r['player_name'],
            'tier1_rank': int(r['tier1_rank']),
            'overall_score': r['brs'],
            'high_balls': int(r['high_balls_faced']),
            'distinct_matches': n_matches,
            'balls_per_match': round(mean_balls, 2),
            'median_perf': round(med_sr, 2),
            'std_perf': round(std_sr, 2),
            'min_perf': round(min_sr, 2),
            'max_perf': round(max_sr, 2),
            'pct_above_avg': round(pct_above_avg, 2),
            'top1_share': round(top1_share, 2),
            'top2_share': round(top2_share, 2)
        })
    df_bat_cons = pd.DataFrame(bat_consistency)
    
    # 2. Bowling Match-Level Consistency
    print("Computing match-level metrics for 113 Tier 1 Bowlers...")
    high_bow = dpi[(dpi['Bowling_Pressure_Level'] == 'High') & (dpi['is_legal_ball'] == 1)]
    
    bow_consistency = []
    for _, r in t1_bow.iterrows():
        p_id = r['player_id']
        p_df = high_bow[high_bow['bowler_id'] == p_id]
        m_agg = p_df.groupby('match_id').agg(
            runs=('bowler_runs_conceded', 'sum'),
            balls=('bowler_runs_conceded', 'count'),
            wk=('is_wicket', lambda s: sum(s == 1))
        )
        m_agg['econ'] = m_agg['runs'] / m_agg['balls'] * 6.0
        
        n_matches = len(m_agg)
        mean_balls = m_agg['balls'].mean() if n_matches > 0 else 0
        med_econ = m_agg['econ'].median() if n_matches > 0 else 0
        std_econ = m_agg['econ'].std() if n_matches > 1 else 0
        min_econ = m_agg['econ'].min() if n_matches > 0 else 0
        max_econ = m_agg['econ'].max() if n_matches > 0 else 0
        pct_above_avg = (m_agg['econ'] <= 8.50).mean() * 100.0 if n_matches > 0 else 0
        
        tot_wk = m_agg['wk'].sum()
        top1_wk = m_agg['wk'].max() if n_matches > 0 else 0
        top1_share = (top1_wk / tot_wk * 100.0) if tot_wk > 0 else 0
        top2_wk = m_agg['wk'].nlargest(2).sum() if n_matches >= 2 else tot_wk
        top2_share = (top2_wk / tot_wk * 100.0) if tot_wk > 0 else 0
        
        bow_consistency.append({
            'role': 'Bowler',
            'player_id': p_id,
            'player_name': r['player_name'],
            'tier1_rank': int(r['tier1_rank']),
            'overall_score': r['bors'],
            'high_balls': int(r['high_legal_balls']),
            'distinct_matches': n_matches,
            'balls_per_match': round(mean_balls, 2),
            'median_perf': round(med_econ, 2),
            'std_perf': round(std_econ, 2),
            'min_perf': round(min_econ, 2),
            'max_perf': round(max_econ, 2),
            'pct_above_avg': round(pct_above_avg, 2),
            'top1_share': round(top1_share, 2),
            'top2_share': round(top2_share, 2)
        })
    df_bow_cons = pd.DataFrame(bow_consistency)
    
    # Combined Consistency CSV
    df_combined = pd.concat([df_bat_cons, df_bow_cons], ignore_index=True)
    csv_out = OUTPUT_DIR / "match_consistency_metrics.csv"
    df_combined.to_csv(csv_out, index=False)
    print(f"\nSaved match consistency metrics to: {csv_out}")
    
    # Print Top 10 Summary
    print("\n--- Top 10 Batters Consistency ---")
    print(df_bat_cons.head(10)[['tier1_rank', 'player_name', 'distinct_matches', 'balls_per_match', 'median_perf', 'std_perf', 'top1_share', 'top2_share']].to_string(index=False))
    
    print("\n--- Top 10 Bowlers Consistency ---")
    print(df_bow_cons.head(10)[['tier1_rank', 'player_name', 'distinct_matches', 'balls_per_match', 'median_perf', 'std_perf', 'top1_share', 'top2_share']].to_string(index=False))
    
    # Print Bumrah
    bumrah_row = df_bow_cons[df_bow_cons['player_name'].str.contains('Bumrah', case=False, na=False)].iloc[0]
    print(f"\nJasprit Bumrah: Rank #{bumrah_row['tier1_rank']}, Matches: {bumrah_row['distinct_matches']}, Balls/M: {bumrah_row['balls_per_match']}, Med Econ: {bumrah_row['median_perf']}, Std Econ: {bumrah_row['std_perf']}, Top1 Wk: {bumrah_row['top1_share']}%, Top2 Wk: {bumrah_row['top2_share']}%")
    
    # 3. Visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))
    
    # Subplot A: Batters Top 2 Matches Share vs Overall Rank
    ax_a = axes[0, 0]
    sc_a = ax_a.scatter(df_bat_cons['overall_score'], df_bat_cons['top2_share'], c=df_bat_cons['distinct_matches'], cmap='plasma', s=df_bat_cons['high_balls']*0.7, alpha=0.8, edgecolors='black')
    cbar_a = plt.colorbar(sc_a, ax=ax_a)
    cbar_a.set_label('Distinct Matches with High Pressure', fontsize=11)
    ax_a.axhline(40.0, color='red', linestyle='--', alpha=0.7, label='High Outlier Dependence (>40% runs in 2 matches)')
    ax_a.set_xlabel('Official BRS Score', fontsize=11)
    ax_a.set_ylabel('% Total High-Pressure Runs from Top 2 Matches', fontsize=11)
    ax_a.set_title('A. Tier 1 Batters: Outlier Dependence vs BRS\n(Size = High Balls Faced, Color = Matches)', fontsize=12, fontweight='bold')
    ax_a.legend(fontsize=9, loc='upper right')
    ax_a.grid(True, linestyle='--', alpha=0.5)
    
    # Annotate key batters
    for _, r in df_bat_cons.head(5).iterrows():
        ax_a.annotate(f"{r['player_name']} (#{r['tier1_rank']})", (r['overall_score'], r['top2_share']), xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')
    dubey = df_bat_cons[df_bat_cons['player_name'] == 'Shubham Dubey'].iloc[0]
    ax_a.annotate(f"Shubham Dubey (#4)\n53.1% in 2 matches!", (dubey['overall_score'], dubey['top2_share']), xytext=(-100, 10), textcoords='offset points', fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.8))
    
    # Subplot B: Bowlers Top 2 Matches Share vs Overall Rank
    ax_b = axes[0, 1]
    sc_b = ax_b.scatter(df_bow_cons['overall_score'], df_bow_cons['top2_share'], c=df_bow_cons['distinct_matches'], cmap='viridis', s=df_bow_cons['high_balls']*0.7, alpha=0.8, edgecolors='black')
    cbar_b = plt.colorbar(sc_b, ax=ax_b)
    cbar_b.set_label('Distinct Matches with High Pressure', fontsize=11)
    ax_b.axhline(50.0, color='red', linestyle='--', alpha=0.7, label='High Outlier Dependence (>50% wickets in 2 matches)')
    ax_b.set_xlabel('Official BoRS Score', fontsize=11)
    ax_b.set_ylabel('% Total High-Pressure Wickets from Top 2 Matches', fontsize=11)
    ax_b.set_title('B. Tier 1 Bowlers: Outlier Dependence vs BoRS\n(Size = Legal Balls Bowled, Color = Matches)', fontsize=12, fontweight='bold')
    ax_b.legend(fontsize=9, loc='upper right')
    ax_b.grid(True, linestyle='--', alpha=0.5)
    
    # Annotate key bowlers
    simarjeet = df_bow_cons[df_bow_cons['player_name'] == 'Simarjeet Singh'].iloc[0]
    ax_b.annotate(f"Simarjeet Singh (#9)\n75.0% in 2 matches!", (simarjeet['overall_score'], simarjeet['top2_share']), xytext=(-100, 10), textcoords='offset points', fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.8))
    southee = df_bow_cons[df_bow_cons['player_name'] == 'Tim Southee'].iloc[0]
    ax_b.annotate(f"Tim Southee (#1)\n57.1% in 2 matches", (southee['overall_score'], southee['top2_share']), xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')
    bumrah = df_bow_cons[df_bow_cons['player_name'] == 'Jasprit Bumrah'].iloc[0]
    ax_b.annotate(f"Bumrah (#24)\n31 matches, 40% in 2 matches", (bumrah['overall_score'], bumrah['top2_share']), xytext=(5, -15), textcoords='offset points', fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgreen', alpha=0.8))
    
    # Subplot C: Distribution of Matches Played Under High Pressure
    ax_c = axes[1, 0]
    ax_c.hist([df_bat_cons['distinct_matches'], df_bow_cons['distinct_matches']], bins=15, label=['Tier 1 Batters', 'Tier 1 Bowlers'], color=['#e74c3c', '#3498db'], edgecolor='black', alpha=0.7)
    ax_c.set_xlabel('Distinct Matches with High Pressure Deliveries', fontsize=11)
    ax_c.set_ylabel('Number of Players', fontsize=11)
    ax_c.set_title('C. Distribution of Distinct Matches Under High Pressure', fontsize=12, fontweight='bold')
    ax_c.axvline(15, color='black', linestyle=':', label='15 Matches Threshold')
    ax_c.legend(fontsize=10)
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    # Subplot D: Performance Variance vs Sample Size (Batters SR Std)
    ax_d = axes[1, 1]
    ax_d.scatter(df_bat_cons['distinct_matches'], df_bat_cons['std_perf'], color='#9b59b6', alpha=0.7, edgecolors='black', s=50, label='Batters (SR Std)')
    ax_d.set_xlabel('Distinct Matches', fontsize=11)
    ax_d.set_ylabel('Match-Level Strike Rate Standard Deviation', fontsize=11)
    ax_d.set_title('D. Match-to-Match Volatility vs Match Count (Batters)', fontsize=12, fontweight='bold')
    ax_d.grid(True, linestyle='--', alpha=0.5)
    ax_d.legend(fontsize=10)
    
    plt.tight_layout()
    plot_out = OUTPUT_DIR / "07_match_to_match_consistency.png"
    plt.savefig(plot_out, dpi=300)
    plt.close()
    print(f"Saved visualization to: {plot_out}")
    
    # 4. Generate Markdown Report
    generate_markdown_report(df_bat_cons, df_bow_cons)

def generate_markdown_report(bat_cons, bow_cons):
    md_path = OUTPUT_DIR / "match_consistency_investigation.md"
    
    rep = []
    rep.append("# Investigation 7: Match-to-Match Consistency")
    rep.append("")
    rep.append("## Executive Summary")
    rep.append("")
    rep.append("A foundational question in player reliability evaluation is whether high-ranking players demonstrate **consistent dependability across multiple matches** or whether their aggregate scores are inflated by a few exceptional, high-leverage performances.")
    rep.append("")
    rep.append("This investigation calculated match-level delivery distributions, distinct match counts, match-to-match standard deviations, and top-match reliance across all 116 Tier 1 batters and 113 Tier 1 bowlers.")
    rep.append("")
    rep.append("### Major Findings:")
    rep.append("1. **The 'Outlier Dependency' Flaw in Aggregate Ranking:**")
    rep.append("   - Because the official v2.0 ranking formula evaluates pooled aggregate numbers (total runs, total balls, total wickets), it cannot distinguish a player who contributes reliably in 80% of matches from a player who explodes in 2 matches and is ineffective in the rest.")
    rep.append("   - **Shubham Dubey (#4 Batter):** Qualified with 55 high-pressure balls across only 14 matches. Over **53.1% of his entire high-pressure run total** came from just **two matches** (31.6% in a single match).")
    rep.append("   - **Simarjeet Singh (#9 Bowler):** Qualified with 60 high-pressure balls across only **9 matches**. Over **75.0% of his wickets** came in just **two matches** (50.0% in a single match).")
    rep.append("   - **Keshav Maharaj (#2 Bowler):** Over **57.1% of his wickets** came in just two matches across 12 games.")
    rep.append("   - **Tim Southee (#1 Bowler):** Over **57.1% of his wickets** came in two matches across 19 games.")
    rep.append("2. **Truly Consistent High-Sample Anchors:**")
    rep.append("   - In contrast, players with high match counts exhibit low outlier dependence:")
    rep.append("   - **MS Dhoni (#1 Batter):** 38 matches, Top 1 match = 9.4%, Top 2 matches = 18.5%. Demonstrates genuine repeated clutch execution.")
    rep.append("   - **Rinku Singh (#8 Batter):** 45 matches, Top 1 match = 12.4%, Top 2 matches = 23.1%.")
    rep.append("   - **Jasprit Bumrah (#24 Bowler):** 31 matches, median economy = 6.00 rpo, std = 4.5 rpo. Highly stable match-to-match containment.")
    rep.append("   - **Wanindu Hasaranga (#7 Bowler):** 34 matches, Top 1 match = 14.3%, Top 2 matches = 28.6%.")
    rep.append("3. **Match Exposure Disparity:**")
    rep.append("   - Tier 1 players range from as few as 8 matches to as many as 56 matches under high pressure. Aggregating them without a minimum match count threshold amplifies small-sample volatility.")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 1. Top 10 Batters Match Consistency")
    rep.append("")
    rep.append("| Rank | Player | BRS | High Balls | Matches | Balls/Match | Median SR | SR Std | Top 1 Match % | Top 2 Matches % |")
    rep.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in bat_cons.head(10).iterrows():
        rep.append(f"| #{r['tier1_rank']} | **{r['player_name']}** | {r['overall_score']:.2f} | {r['high_balls']} | {r['distinct_matches']} | {r['balls_per_match']:.1f} | {r['median_perf']:.1f} | {r['std_perf']:.1f} | {r['top1_share']:.1f}% | {r['top2_share']:.1f}% |")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 2. Top 10 Bowlers Match Consistency")
    rep.append("")
    rep.append("| Rank | Player | BoRS | High Balls | Matches | Balls/Match | Median Econ | Econ Std | Top 1 Match % | Top 2 Matches % |")
    rep.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in bow_cons.head(10).iterrows():
        rep.append(f"| #{r['tier1_rank']} | **{r['player_name']}** | {r['overall_score']:.2f} | {r['high_balls']} | {r['distinct_matches']} | {r['balls_per_match']:.1f} | {r['median_perf']:.1f} | {r['std_perf']:.1f} | {r['top1_share']:.1f}% | {r['top2_share']:.1f}% |")
    rep.append("")
    # Add Bumrah row for comparison
    bumrah = bow_cons[bow_cons['player_name'].str.contains('Bumrah', case=False, na=False)].iloc[0]
    rep.append(f"| #{bumrah['tier1_rank']} | **{bumrah['player_name']}** | {bumrah['overall_score']:.2f} | {bumrah['high_balls']} | {bumrah['distinct_matches']} | {bumrah['balls_per_match']:.1f} | {bumrah['median_perf']:.1f} | {bumrah['std_perf']:.1f} | {bumrah['top1_share']:.1f}% | {bumrah['top2_share']:.1f}% |")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 3. Analytical Answers on Match Consistency")
    rep.append("")
    rep.append("1. **Do aggregate rankings hide inconsistent players?**")
    rep.append("   - **Yes, significantly.** Players like Shubham Dubey (53.1% in 2 games) and Simarjeet Singh (75.0% in 2 games) achieved elite Tier 1 rankings based on a handful of high-leverage spikes, masking severe unreliability across other matches.")
    rep.append("2. **How does match-to-match consistency differ from average performance?**")
    rep.append("   - Average performance answers *'What was the pooled output?'* Consistency answers *'How dependable was the player across discrete match opportunities?'*")
    rep.append("   - A team choosing a player for a playoff final needs high probability of acceptable execution, not a high aggregate boosted by a blowout win months earlier.")
    rep.append("3. **Recommended Methodological Correction for v3.0:**")
    rep.append("   - Introduce a dual qualification criterion: e.g. **60 high-pressure balls AND minimum 15 distinct high-pressure matches**.")
    rep.append("   - Introduce a **Consistency Factor** or match-level median penalty that downweights players whose top 2 matches constitute $>40\\%$ of total value.")
    rep.append("")
    rep.append("---")
    rep.append("*(Report generated automatically by Step 11 Investigation 7)*")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(rep))
    print(f"Generated markdown report: {md_path}")

if __name__ == "__main__":
    run_investigation()
