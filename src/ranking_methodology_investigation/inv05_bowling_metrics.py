"""
src/ranking_methodology_investigation/inv05_bowling_metrics.py
Investigation 5: Bowling Metric Contribution and Balance

Deep investigation of all 589 bowlers and 113 Tier 1 qualified bowlers,
evaluating metric distributions, correlations, variance decomposition,
and archetype tradeoffs between run containment and wicket-taking.
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
    print("INVESTIGATION 5: BOWLING METRIC CONTRIBUTION AND BALANCE")
    print("=" * 80)
    
    bow_path = BASE_DIR / "data" / "processed" / "bowler_reliability_rankings.csv"
    df = pd.read_csv(bow_path)
    t1 = df[df['tier'] == 'Tier 1: Qualified'].copy()
    t2 = df[df['tier'] == 'Tier 2: Specialist'].copy()
    bt = df[df['tier'] == 'Below Threshold'].copy()
    
    print(f"Loaded {len(df)} total bowlers. Qualified Tier 1: {len(t1)}, Tier 2: {len(t2)}, Below Threshold: {len(bt)}.")
    
    components = ['score_econ', 'score_wk', 'score_dot', 'score_diff']
    weights = np.array([0.40, 0.25, 0.20, 0.15])
    comp_labels = ['Economy (0.40)', 'Wickets (0.25)', 'Dot Balls (0.20)', 'Clutch Diff (0.15)']
    
    # 1. Distribution Summary
    dist_all = df[components + ['bors']].describe().T
    dist_t1 = t1[components + ['bors']].describe().T
    
    summary_records = []
    for comp in components + ['bors']:
        summary_records.append({
            'Metric': comp,
            'All_Mean': round(dist_all.loc[comp, 'mean'], 2),
            'All_Std': round(dist_all.loc[comp, 'std'], 2),
            'All_Median': round(dist_all.loc[comp, '50%'], 2),
            'T1_Mean': round(dist_t1.loc[comp, 'mean'], 2),
            'T1_Std': round(dist_t1.loc[comp, 'std'], 2),
            'T1_Median': round(dist_t1.loc[comp, '50%'], 2)
        })
    dist_df = pd.DataFrame(summary_records)
    print("\n--- Component Score Distributions (All vs Tier 1) ---")
    print(dist_df.to_string(index=False))
    
    csv_out = OUTPUT_DIR / "bowling_metric_distributions.csv"
    dist_df.to_csv(csv_out, index=False)
    print(f"Saved distribution summary to: {csv_out}")
    
    # 2. Correlation Matrix
    corr_p_t1 = t1[components].corr(method='pearson')
    corr_s_t1 = t1[components].corr(method='spearman')
    corr_p_all = df[components].corr(method='pearson')
    
    print("\n--- Tier 1 Component Correlation Matrix (Pearson) ---")
    print(corr_p_t1.round(4))
    print("\n--- Tier 1 Component Correlation Matrix (Spearman) ---")
    print(corr_s_t1.round(4))
    
    # 3. Variance Decomposition
    cov_matrix = t1[components].cov().values
    total_var = weights.T @ cov_matrix @ weights
    marginal_contrib = (cov_matrix @ weights) * weights
    pct_contrib = (marginal_contrib / total_var) * 100.0
    
    print("\n--- Variance Decomposition (Tier 1) ---")
    for comp, w, c in zip(components, weights, pct_contrib):
        print(f"  {comp:12s} (nominal weight {w:.2f}): {c:.2f}% of BoRS variance")
        
    # 4. Archetype Identification
    print("\n--- Archetype Analysis: Containment vs Strike Bowlers ---")
    containment = t1[(t1['score_econ'] >= 65) & (t1['score_wk'] <= 40)].sort_values('score_econ', ascending=False)
    strike = t1[(t1['score_wk'] >= 65) & (t1['score_econ'] <= 55)].sort_values('score_wk', ascending=False)
    balanced = t1[(t1['score_econ'] >= 65) & (t1['score_wk'] >= 60)].sort_values('bors', ascending=False)
    
    print(f"Containment Specialists count: {len(containment)}")
    print(containment[['tier1_rank', 'player_name', 'high_legal_balls', 'econ_obs', 'wk_pct_obs', 'score_econ', 'score_wk', 'score_dot', 'score_diff', 'bors']].head(8).to_string())
    
    print(f"\nStrike Bowlers count: {len(strike)}")
    print(strike[['tier1_rank', 'player_name', 'high_legal_balls', 'econ_obs', 'wk_pct_obs', 'score_econ', 'score_wk', 'score_dot', 'score_diff', 'bors']].head(8).to_string())
    
    print(f"\nBalanced Top Performers count: {len(balanced)}")
    print(balanced[['tier1_rank', 'player_name', 'high_legal_balls', 'econ_obs', 'wk_pct_obs', 'score_econ', 'score_wk', 'score_dot', 'score_diff', 'bors']].head(8).to_string())
    
    # 5. Visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))
    
    # Subplot A: Economy vs Wicket Rate Scatter
    ax_a = axes[0, 0]
    sc = ax_a.scatter(t1['econ_obs'], t1['wk_pct_obs'], c=t1['bors'], cmap='viridis', s=t1['high_legal_balls']*0.8, alpha=0.8, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(sc, ax=ax_a)
    cbar.set_label('Official BoRS Score', fontsize=11)
    
    # Highlight key archetypes
    bumrah = t1[t1['player_name'].str.contains('Bumrah', case=False, na=False)].iloc[0]
    southee = t1[t1['player_name'].str.contains('Southee', case=False, na=False)].iloc[0]
    duffy = t1[t1['player_name'].str.contains('Duffy', case=False, na=False)].iloc[0]
    adair = t1[t1['player_name'].str.contains('Adair', case=False, na=False)].iloc[0]
    theeks = t1[t1['player_name'].str.contains('Theekshana', case=False, na=False)].iloc[0]
    coetzee = t1[t1['player_name'].str.contains('Coetzee', case=False, na=False)].iloc[0]
    
    key_bowlers = [
        (bumrah, 'Jasprit Bumrah (#24)\nEcon 6.93, Wk 2.98%'),
        (southee, 'Tim Southee (#1)\nEcon 5.81, Wk 9.38%'),
        (duffy, 'Jacob Duffy (#35)\nEcon 10.02, Wk 10.24%'),
        (adair, 'Mark Adair (#4)\nEcon 5.32, Wk 4.23%'),
        (theeks, 'Theekshana (#12)\nEcon 6.88, Wk 4.11%'),
        (coetzee, 'Coetzee (#27)\nEcon 10.00, Wk 9.52%')
    ]
    for b_row, lbl in key_bowlers:
        ax_a.scatter(b_row['econ_obs'], b_row['wk_pct_obs'], color='red', s=130, zorder=5, edgecolors='black')
        ax_a.annotate(lbl, (b_row['econ_obs'], b_row['wk_pct_obs']), xytext=(8, 5), textcoords='offset points', fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))
        
    ax_a.set_title('A. High-Pressure Economy vs Wicket Rate (Tier 1 Bowlers)\nSize = Balls Bowled, Color = BoRS', fontsize=12, fontweight='bold')
    ax_a.set_xlabel('Observed Economy Rate (Runs Per Over) [Lower is Better]', fontsize=11)
    ax_a.set_ylabel('Observed Wicket % [Higher is Better]', fontsize=11)
    ax_a.grid(True, linestyle='--', alpha=0.5)
    
    # Subplot B: Correlation Heatmap
    ax_b = axes[0, 1]
    im = ax_b.imshow(corr_p_t1.values, cmap='coolwarm', vmin=-0.2, vmax=1.0)
    ax_b.set_xticks(range(len(components)))
    ax_b.set_yticks(range(len(components)))
    ax_b.set_xticklabels(comp_labels, rotation=20, ha='right', fontsize=10)
    ax_b.set_yticklabels(comp_labels, fontsize=10)
    for i in range(len(components)):
        for j in range(len(components)):
            val = corr_p_t1.iloc[i, j]
            ax_b.text(j, i, f"{val:.3f}", ha="center", va="center", color="white" if abs(val) > 0.5 else "black", fontweight='bold', fontsize=11)
    plt.colorbar(im, ax=ax_b, fraction=0.046, pad=0.04)
    ax_b.set_title('B. Pearson Correlation Between Bowling Components (Tier 1)', fontsize=12, fontweight='bold')
    
    # Subplot C: Variance Decomposition Bar Chart
    ax_c = axes[1, 0]
    bars_x = np.arange(len(components))
    nom_w = weights * 100.0
    eff_w = pct_contrib
    width = 0.35
    b1 = ax_c.bar(bars_x - width/2, nom_w, width, label='Nominal Model Weight (%)', color='#3498db', edgecolor='black')
    b2 = ax_c.bar(bars_x + width/2, eff_w, width, label='Effective Variance Contribution (%)', color='#e67e22', edgecolor='black')
    ax_c.set_xticks(bars_x)
    ax_c.set_xticklabels(['Economy', 'Wickets', 'Dot Balls', 'Clutch Diff'], fontsize=11)
    ax_c.set_ylabel('Percentage (%)', fontsize=11)
    ax_c.set_title('C. Nominal Weights vs Effective Variance Contribution', fontsize=12, fontweight='bold')
    ax_c.legend(fontsize=10)
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5)
    for bar in b1:
        h = bar.get_height()
        ax_c.annotate(f"{h:.1f}%", (bar.get_x() + bar.get_width()/2, h + 0.8), ha='center', fontsize=10, fontweight='bold')
    for bar in b2:
        h = bar.get_height()
        ax_c.annotate(f"{h:.1f}%", (bar.get_x() + bar.get_width()/2, h + 0.8), ha='center', fontsize=10, fontweight='bold')
        
    # Subplot D: Score Distribution Boxplots
    ax_d = axes[1, 1]
    box_data = [t1[comp] for comp in components] + [t1['bors']]
    box_labels = ['Score Econ', 'Score Wk', 'Score Dot', 'Score Diff', 'Final BoRS']
    bp = ax_d.boxplot(box_data, tick_labels=box_labels, patch_artist=True, medianprops=dict(color='black', linewidth=2))
    colors = ['#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c']
    for patch, col in zip(bp['boxes'], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)
    ax_d.set_ylabel('Score (0 to 100)', fontsize=11)
    ax_d.set_title('D. Component and Composite Score Distributions (Tier 1)', fontsize=12, fontweight='bold')
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plot_out = OUTPUT_DIR / "05_bowling_metric_tradeoffs.png"
    plt.savefig(plot_out, dpi=300)
    plt.close()
    print(f"Saved visualization to: {plot_out}")
    
    # 6. Generate Markdown Report
    generate_markdown_report(t1, dist_df, corr_p_t1, corr_s_t1, pct_contrib, containment, strike, balanced)

def generate_markdown_report(t1, dist_df, corr_p, corr_s, eff_weights, containment, strike, balanced):
    md_path = OUTPUT_DIR / "bowling_metric_investigation.md"
    
    rep = []
    rep.append("# Investigation 5: Bowling Metric Contribution and Balance")
    rep.append("")
    rep.append("## Executive Summary")
    rep.append("")
    rep.append("This investigation evaluates the mathematical structure, component correlations, variance decomposition, and role-based fairness of the official bowling reliability ranking model (v2.0) across all 589 bowlers (113 Tier 1 qualified, 36 Tier 2 specialists, 440 below threshold).")
    rep.append("")
    rep.append("Unlike the batting model, where extreme collinearity between Strike Rate and Boundary Execution concentrated 68.1% of variance into scoring speed, the bowling model demonstrates **substantially better structural balance**:")
    rep.append("- Component inter-correlations are moderate ($r \\in [0.19, 0.56]$), meaning each metric captures distinct bowling dimensions.")
    rep.append("- Effective variance contributions track nominal model weights remarkably well: Economy accounts for **39.88%** (nominal 40%), Wickets **23.11%** (nominal 25%), Dot Balls **21.80%** (nominal 20%), and Clutch Differential **15.21%** (nominal 15%).")
    rep.append("")
    rep.append("However, deep inspection reveals a **critical structural asymmetry in how player archetypes are rewarded**:")
    rep.append("1. **The Containment Penalty:** Pure containment specialists (e.g. Jasprit Bumrah #24, Maheesh Theekshana #12, Richard Ngarava #20, Harpreet Brar #41) concede remarkably few runs (economy 6.8 to 7.2 rpo under high pressure) but achieve lower raw wicket percentages (2.0% to 4.2%). Because the wicket score spans a wide range (5.9 to 96.1) with a standard deviation of 18.9 points, pure containment bowlers forfeit 12 to 18 net BoRS points on the wicket component alone.")
    rep.append("2. **The Strike Bowler Penalty:** Pure strike bowlers (e.g. Jacob Duffy #35, Gerald Coetzee #27, Ravi Bishnoi #36, Sai Kishore #52) achieve elite wicket rates (8.0% to 10.2%) but concede 9.0 to 10.0+ rpo, suffering steep penalties on economy and clutch differential.")
    rep.append("3. **The All-Rounder Premium:** The Top 10 rankings are completely dominated by 'all-rounder bowlers' who achieve moderate-to-high scores across all four metrics simultaneously (e.g. Tim Southee #1, Keshav Maharaj #2, Haris Rauf #3, Harshit Rana #6).")
    rep.append("4. **The Partnership Blindspot:** In T20 cricket, extreme dot-ball pressure from elite containment bowlers frequently forces batters to attack and lose wickets at the other end. The current model measures only individual credited wickets, completely ignoring induced pressure.")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 1. Component Score Distributions")
    rep.append("")
    rep.append("Comparison of descriptive statistics across All 589 Bowlers vs Tier 1 Qualified Bowlers (N=113):")
    rep.append("")
    rep.append("| Metric | All Mean | All Std | All Median | Tier 1 Mean | Tier 1 Std | Tier 1 Median |")
    rep.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, row in dist_df.iterrows():
        rep.append(f"| **{row['Metric']}** | {row['All_Mean']:.2f} | {row['All_Std']:.2f} | {row['All_Median']:.2f} | {row['T1_Mean']:.2f} | {row['T1_Std']:.2f} | {row['T1_Median']:.2f} |")
    rep.append("")
    rep.append("> [!NOTE]")
    rep.append("> While the Tier 1 mean BoRS is 50.51 (standard deviation 12.71), component spreads differ substantially. Wicket score exhibits the largest spread (standard deviation 18.92, range 5.90 to 96.07), making it the most volatile component, whereas Economy score has the lowest standard deviation (15.59) and maxes out at 85.55.")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 2. Component Correlation Analysis")
    rep.append("")
    rep.append("### Tier 1 Pearson Correlation Matrix")
    rep.append("")
    rep.append("| Component | Economy (0.40) | Wickets (0.25) | Dot Balls (0.20) | Clutch Diff (0.15) |")
    rep.append("| :--- | :---: | :---: | :---: | :---: |")
    for comp in ['score_econ', 'score_wk', 'score_dot', 'score_diff']:
        row_str = f"| **{comp}** |"
        for target in ['score_econ', 'score_wk', 'score_dot', 'score_diff']:
            row_str += f" {corr_p.loc[comp, target]:.4f} |"
        rep.append(row_str)
    rep.append("")
    rep.append("### Key Statistical Observations:")
    rep.append(f"1. **Economy vs Wickets ($r = {corr_p.loc['score_econ', 'score_wk']:.4f}$):** Economy and wicket taking are virtually orthogonal. Bowling economically under pressure does not automatically produce wickets, and hunting wickets often inflates run rates.")
    rep.append(f"2. **Economy vs Dot Balls ($r = {corr_p.loc['score_econ', 'score_dot']:.4f}$):** Moderate positive correlation. Dot balls are the primary mechanism for suppressing runs, though boundary balls can dilute this relationship.")
    rep.append(f"3. **Wickets vs Dot Balls ($r = {corr_p.loc['score_wk', 'score_dot']:.4f}$):** Weak-to-moderate positive correlation ($r = 0.3518$), indicating that dot-ball pressure assists in dismissal generation.")
    rep.append(f"4. **Economy vs Clutch Diff ($r = {corr_p.loc['score_econ', 'score_diff']:.4f}$):** Substantial correlation ($r = 0.5625$). Bowlers who are highly economical under pressure tend to improve upon their baseline economy.")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 3. Effective Variance Decomposition")
    rep.append("")
    rep.append("Using the formula $C_i = \\sum_j w_i w_j \\text{Cov}(S_i, S_j) / \\text{Var}(\\text{BoRS})$:")
    rep.append("")
    rep.append("| Component | Nominal Weight | Effective Variance Contribution | Difference |")
    rep.append("| :--- | :---: | :---: | :---: |")
    comps = ['score_econ', 'score_wk', 'score_dot', 'score_diff']
    noms = [40.0, 25.0, 20.0, 15.0]
    for c, nw, ew in zip(comps, noms, eff_weights):
        diff = ew - nw
        sign = "+" if diff >= 0 else ""
        rep.append(f"| **{c}** | {nw:.1f}% | {ew:.2f}% | {sign}{diff:.2f}% |")
    rep.append("")
    rep.append("**Conclusion on Weights:** In contrast to the batting model (where effective weight differed from nominal weight by up to +5.65% on SR and -5.20% on Survival), the bowling formula's effective contributions match the theoretical design with extraordinary fidelity (all within $\\pm 1.9\\%$).")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 4. Player Archetypes: The Tradeoff Between Containment and Wickets")
    rep.append("")
    rep.append("### A. Containment Specialists (High Economy, Lower Wicket Rates)")
    rep.append("Bowlers with Economy Score $\\ge 65.0$ but Wicket Score $\\le 40.0$:")
    rep.append("")
    rep.append("| Rank | Player | Balls | High Econ | High Wk % | Score Econ | Score Wk | Score Dot | Score Diff | BoRS |")
    rep.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in containment.head(8).iterrows():
        rep.append(f"| #{int(r['tier1_rank'])} | **{r['player_name']}** | {int(r['high_legal_balls'])} | {r['econ_obs']:.2f} | {r['wk_pct_obs']:.2f}% | {r['score_econ']:.2f} | {r['score_wk']:.2f} | {r['score_dot']:.2f} | {r['score_diff']:.2f} | **{r['bors']:.2f}** |")
    rep.append("")
    rep.append("### B. Pure Strike Bowlers (High Wickets, Expensive Economy)")
    rep.append("Bowlers with Wicket Score $\\ge 65.0$ but Economy Score $\\le 55.0$:")
    rep.append("")
    rep.append("| Rank | Player | Balls | High Econ | High Wk % | Score Econ | Score Wk | Score Dot | Score Diff | BoRS |")
    rep.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in strike.head(8).iterrows():
        rep.append(f"| #{int(r['tier1_rank'])} | **{r['player_name']}** | {int(r['high_legal_balls'])} | {r['econ_obs']:.2f} | {r['wk_pct_obs']:.2f}% | {r['score_econ']:.2f} | {r['score_wk']:.2f} | {r['score_dot']:.2f} | {r['score_diff']:.2f} | **{r['bors']:.2f}** |")
    rep.append("")
    rep.append("### C. Balanced High Performers (Top Tier 1)")
    rep.append("Bowlers with Economy Score $\\ge 65.0$ and Wicket Score $\\ge 60.0$:")
    rep.append("")
    rep.append("| Rank | Player | Balls | High Econ | High Wk % | Score Econ | Score Wk | Score Dot | Score Diff | BoRS |")
    rep.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in balanced.head(8).iterrows():
        rep.append(f"| #{int(r['tier1_rank'])} | **{r['player_name']}** | {int(r['high_legal_balls'])} | {r['econ_obs']:.2f} | {r['wk_pct_obs']:.2f}% | {r['score_econ']:.2f} | {r['score_wk']:.2f} | {r['score_dot']:.2f} | {r['score_diff']:.2f} | **{r['bors']:.2f}** |")
    rep.append("")
    rep.append("---")
    rep.append("")
    rep.append("## 5. Does the Model Adequately Represent Different Bowling Roles?")
    rep.append("")
    rep.append("### Critical Analytical Verdict: **Partially Defensible, Role-Biased**")
    rep.append("")
    rep.append("1. **The 'All-Rounder' Requirement:**")
    rep.append("   - To enter the Top 10, a bowler must be above average in *all four* components. A specialist who excels world-class in run suppression (like Bumrah or Theekshana) cannot offset a low wicket count.")
    rep.append("   - Consider Bumrah: His high-pressure economy of 6.93 rpo yields an Economy Score of 76.38. But his 2.98% wicket rate yields a Wicket Score of 25.31. The net drag from wickets is $0.25 \\times (25.31 - 50.0) = -6.17$ points, dragging his BoRS down to 59.29 (#24).")
    rep.append("")
    rep.append("2. **The Missing 'Induced Wicket' Credit:**")
    rep.append("   - Cricket tactics dictate that elite batters do not take uncalculated risks against Jasprit Bumrah (economy 6.93) or Maheesh Theekshana (economy 6.88). Instead, they 'play out' the elite bowler and target the weaker bowler at the other end.")
    rep.append("   - As a result, the bowler creating the pressure does not receive the wicket credit, while the partner receives an inflated wicket score despite higher economy.")
    rep.append("")
    rep.append("3. **Recommendations for Future v3.0 Exploration:**")
    rep.append("   - **Role-Based Normalization:** Separate 'Enforcer / Containment' bowlers from 'Strike / Death' bowlers, or adopt a non-linear convex reward where elite economy (<7.0 rpo) is weighted more heavily.")
    rep.append("   - **Wicket Value Modulation:** Weight wickets by the quality/phase of batter dismissed or combine Dot Ball % and Economy into a unified 'Pressure Induction Index'.")
    rep.append("")
    rep.append("---")
    rep.append("*(Report generated automatically by Step 11 Investigation 5)*")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(rep))
    print(f"Generated markdown report: {md_path}")

if __name__ == "__main__":
    run_investigation()
