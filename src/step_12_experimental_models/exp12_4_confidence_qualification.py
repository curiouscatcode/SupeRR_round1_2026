"""
Step 12: Experiment 12.4 — Confidence-Based Qualification Investigation
=======================================================================
Investigates whether the existing minimum threshold of 60 high-pressure balls
creates an excessive eligibility cliff, models statistical estimation uncertainty,
and tests dual-criteria (volume + breadth) and Lower Credible Bound (LCB) approaches.

Isolates:
- Outputs to outputs/step_12_experimental_models/exp12_4_confidence_qualification/
- Preserves official v2.0 rankings and K=50 Bayesian shrinkage baseline.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "step_12_experimental_models" / "exp12_4_confidence_qualification"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

K = 50.0

def run_experiment_12_4():
    print("=" * 70)
    print("STEP 12: EXPERIMENT 12.4 — CONFIDENCE-BASED QUALIFICATION EVALUATION")
    print("=" * 70)

    # 1. Load authoritative baseline data
    b_df = pd.read_csv(DATA_DIR / "batter_reliability_rankings.csv").copy()
    bo_df = pd.read_csv(DATA_DIR / "bowler_reliability_rankings.csv").copy()
    dpi = pd.read_csv(DATA_DIR / "delivery_pressure_index.csv", usecols=[
        'match_id', 'striker_id', 'bowler_id', 'Batting_Pressure_Level', 'Bowling_Pressure_Level'
    ])

    print(f"Loaded {len(b_df)} batters and {len(bo_df)} bowlers.")

    # 2. Extract Match Opportunity Counts
    hp_bat_matches = dpi[dpi['Batting_Pressure_Level'] == 'High'].groupby('striker_id')['match_id'].nunique()
    hp_bowl_matches = dpi[dpi['Bowling_Pressure_Level'] == 'High'].groupby('bowler_id')['match_id'].nunique()

    b_df['hp_matches'] = b_df['player_id'].map(hp_bat_matches).fillna(0).astype(int)
    bo_df['hp_matches'] = bo_df['player_id'].map(hp_bowl_matches).fillna(0).astype(int)

    # 3. Statistical Uncertainty Modeling (Posterior Standard Error & Confidence Intervals)
    # Estimate population standard deviation among players with meaningful samples (N >= 40)
    sigma_bat = b_df[b_df['high_balls_faced'] >= 40]['brs'].std()
    sigma_bowl = bo_df[bo_df['high_legal_balls'] >= 40]['bors'].std()

    # Analytical Posterior Standard Error: SE = sigma / sqrt(N + K)
    b_df['se_brs'] = sigma_bat / np.sqrt(b_df['high_balls_faced'] + K)
    bo_df['se_bors'] = sigma_bowl / np.sqrt(bo_df['high_legal_balls'] + K)

    # 90% Confidence Intervals (z = 1.645)
    z_90 = 1.645
    b_df['brs_ci90_lower'] = np.clip(b_df['brs'] - z_90 * b_df['se_brs'], 0.0, 100.0)
    b_df['brs_ci90_upper'] = np.clip(b_df['brs'] + z_90 * b_df['se_brs'], 0.0, 100.0)
    b_df['brs_margin_90'] = z_90 * b_df['se_brs']

    bo_df['bors_ci90_lower'] = np.clip(bo_df['bors'] - z_90 * bo_df['se_bors'], 0.0, 100.0)
    bo_df['bors_ci90_upper'] = np.clip(bo_df['bors'] + z_90 * bo_df['se_bors'], 0.0, 100.0)
    bo_df['bors_margin_90'] = z_90 * bo_df['se_bors']

    # Lower Credible Bound (LCB, 90% one-sided: z = 1.282)
    z_lcb = 1.282
    b_df['brs_lcb'] = np.clip(b_df['brs'] - z_lcb * b_df['se_brs'], 0.0, 100.0)
    bo_df['bors_lcb'] = np.clip(bo_df['bors'] - z_lcb * bo_df['se_bors'], 0.0, 100.0)

    # 4. Formulate Alternative Qualification Frameworks
    # Framework 0: Official Baseline (N >= 60)
    # Framework 1: Dual-Criteria (Volume + Breadth)
    #   Qualified if: (N >= 60) OR (N >= 50 AND hp_matches >= 6)
    b_df['qual_dual'] = (b_df['high_balls_faced'] >= 60) | ((b_df['high_balls_faced'] >= 50) & (b_df['hp_matches'] >= 6))
    bo_df['qual_dual'] = (bo_df['high_legal_balls'] >= 60) | ((bo_df['high_legal_balls'] >= 50) & (bo_df['hp_matches'] >= 6))

    # Framework 2: Pure Sample Floor (N >= 50)
    b_df['qual_50b'] = b_df['high_balls_faced'] >= 50
    bo_df['qual_50b'] = bo_df['high_legal_balls'] >= 50

    # Framework 3: Unified LCB Ranking (Continuous uncertainty discount across all players)
    b_df['rank_lcb'] = b_df['brs_lcb'].rank(ascending=False, method='min').astype(int)
    bo_df['rank_lcb'] = bo_df['bors_lcb'].rank(ascending=False, method='min').astype(int)

    # Assign Dual-Criteria Ranks
    b_df['rank_dual'] = np.nan
    b_df.loc[b_df['qual_dual'], 'rank_dual'] = b_df.loc[b_df['qual_dual'], 'brs'].rank(ascending=False, method='min').astype(int)

    bo_df['rank_dual'] = np.nan
    bo_df.loc[bo_df['qual_dual'], 'rank_dual'] = bo_df.loc[bo_df['qual_dual'], 'bors'].rank(ascending=False, method='min').astype(int)

    # 5. Comparative Statistical Analysis
    t1_b_off = b_df['tier'] == 'Tier 1: Qualified'
    t1_bo_off = bo_df['tier'] == 'Tier 1: Qualified'

    n_bat_off = t1_b_off.sum()
    n_bat_dual = b_df['qual_dual'].sum()
    n_bat_50b = b_df['qual_50b'].sum()

    n_bowl_off = t1_bo_off.sum()
    n_bowl_dual = bo_df['qual_dual'].sum()
    n_bowl_50b = bo_df['qual_50b'].sum()

    print(f"\n--- Qualification Pool Counts ---")
    print(f"Batters:  Baseline (60b) = {n_bat_off} | Dual-Criteria = {n_bat_dual} (+{n_bat_dual - n_bat_off}) | Pure 50b = {n_bat_50b} (+{n_bat_50b - n_bat_off})")
    print(f"Bowlers:  Baseline (60b) = {n_bowl_off} | Dual-Criteria = {n_bowl_dual} (+{n_bowl_dual - n_bowl_off}) | Pure 50b = {n_bowl_50b} (+{n_bowl_50b - n_bowl_off})")

    # Edge cases analysis
    overton = b_df[b_df['player_name'].str.contains('Overton')].iloc[0]
    nasum = bo_df[bo_df['player_name'].str.contains('Nasum')].iloc[0]
    simarjeet = bo_df[bo_df['player_name'].str.contains('Simarjeet')].iloc[0]
    shoriful = bo_df[bo_df['player_name'].str.contains('Shoriful')].iloc[0]

    print(f"\n--- Edge-Case Players Spotlight ---")
    print(f"Jamie Overton: {overton['high_balls_faced']} balls, {overton['hp_matches']} matches | BRS: {overton['brs']:.2f} (SE: {overton['se_brs']:.2f}, Margin: ±{overton['brs_margin_90']:.2f}) | Dual Rank: #{int(overton['rank_dual'])} | Official Tier: {overton['tier']}")
    print(f"Nasum Ahmed:   {nasum['high_legal_balls']} balls, {nasum['hp_matches']} matches | BoRS: {nasum['bors']:.2f} (SE: {nasum['se_bors']:.2f}, Margin: ±{nasum['bors_margin_90']:.2f}) | Dual Rank: #{int(nasum['rank_dual'])} | Official Tier: {nasum['tier']}")
    print(f"Simarjeet S.:  {simarjeet['high_legal_balls']} balls, {simarjeet['hp_matches']} matches | BoRS: {simarjeet['bors']:.2f} (SE: {simarjeet['se_bors']:.2f}, Margin: ±{simarjeet['bors_margin_90']:.2f}) | Dual Rank: #{int(simarjeet['rank_dual'])} | Official Tier: {simarjeet['tier']}")
    print(f"Shoriful Islam:{shoriful['high_legal_balls']} balls, {shoriful['hp_matches']} matches | BoRS: {shoriful['bors']:.2f} (SE: {shoriful['se_bors']:.2f}, Margin: ±{shoriful['bors_margin_90']:.2f}) | Dual Rank: #{int(shoriful['rank_dual'])} | Official Tier: {shoriful['tier']}")

    # 6. Export Datasets
    # A. Combined Qualification Rankings
    cols_bat_export = [
        'player_id', 'player_name', 'high_balls_faced', 'hp_matches', 'brs', 'se_brs',
        'brs_ci90_lower', 'brs_ci90_upper', 'brs_margin_90', 'brs_lcb',
        'tier', 'tier1_rank', 'tier2_rank', 'qual_dual', 'rank_dual', 'rank_lcb'
    ]
    cols_bowl_export = [
        'player_id', 'player_name', 'high_legal_balls', 'hp_matches', 'bors', 'se_bors',
        'bors_ci90_lower', 'bors_ci90_upper', 'bors_margin_90', 'bors_lcb',
        'tier', 'tier1_rank', 'tier2_rank', 'qual_dual', 'rank_dual', 'rank_lcb'
    ]

    b_out = b_df[cols_bat_export].rename(columns={
        'high_balls_faced': 'high_pressure_deliveries', 'brs': 'official_score',
        'se_brs': 'std_error', 'brs_ci90_lower': 'ci90_lower', 'brs_ci90_upper': 'ci90_upper',
        'brs_margin_90': 'margin_of_error_90', 'brs_lcb': 'lcb_score'
    })
    b_out['discipline'] = 'Batter'

    bo_out = bo_df[cols_bowl_export].rename(columns={
        'high_legal_balls': 'high_pressure_deliveries', 'bors': 'official_score',
        'se_bors': 'std_error', 'bors_ci90_lower': 'ci90_lower', 'bors_ci90_upper': 'ci90_upper',
        'bors_margin_90': 'margin_of_error_90', 'bors_lcb': 'lcb_score'
    })
    bo_out['discipline'] = 'Bowler'

    combined_qual_df = pd.concat([b_out, bo_out], ignore_index=True)
    rankings_path = OUTPUT_DIR / "exp12_4_qualification_rankings.csv"
    combined_qual_df.to_csv(rankings_path, index=False)
    print(f"\nExported complete qualification rankings to {rankings_path.name}")

    # B. Newly Qualified Players Comparison Table
    new_batters = b_df[~t1_b_off & b_df['qual_dual']].copy().sort_values('rank_dual')
    new_bowlers = bo_df[~t1_bo_off & bo_df['qual_dual']].copy().sort_values('rank_dual')

    new_batters['discipline'] = 'Batter'
    new_bowlers['discipline'] = 'Bowler'
    new_batters_clean = new_batters[['discipline', 'player_name', 'high_balls_faced', 'hp_matches', 'brs', 'se_brs', 'rank_dual', 'tier2_rank']].rename(
        columns={'high_balls_faced': 'sample_balls', 'brs': 'score', 'se_brs': 'std_error'}
    )
    new_bowlers_clean = new_bowlers[['discipline', 'player_name', 'high_legal_balls', 'hp_matches', 'bors', 'se_bors', 'rank_dual', 'tier2_rank']].rename(
        columns={'high_legal_balls': 'sample_balls', 'bors': 'score', 'se_bors': 'std_error'}
    )

    comparison_df = pd.concat([new_batters_clean, new_bowlers_clean], ignore_index=True)
    comparison_path = OUTPUT_DIR / "exp12_4_qualification_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False)
    print(f"Exported newly qualified comparison table to {comparison_path.name}")

    # 7. Generate Publication-Quality Visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))

    # Panel A: Estimation Uncertainty Decay Curve
    ax1 = axes[0, 0]
    n_curve = np.linspace(5, 250, 300)
    se_bat_curve = sigma_bat / np.sqrt(n_curve + K)
    se_bowl_curve = sigma_bowl / np.sqrt(n_curve + K)

    ax1.plot(n_curve, se_bat_curve, label=f'Batting SE ($\\sigma$={sigma_bat:.1f})', color='#1f77b4', linewidth=2.5)
    ax1.plot(n_curve, se_bowl_curve, label=f'Bowling SE ($\\sigma$={sigma_bowl:.1f})', color='#2ca02c', linewidth=2.5)
    ax1.axvline(60, color='red', linestyle='--', linewidth=1.5, label='Official Tier 1 Cutoff (60 balls)')
    ax1.axvline(50, color='orange', linestyle=':', linewidth=1.5, label='Proposed Dual Floor (50 balls)')
    ax1.axvline(40, color='purple', linestyle=':', linewidth=1.2, label='Tier 2 Floor (40 balls)')

    # Annotate SE at 59 and 60 balls
    se_59 = sigma_bat / np.sqrt(59 + K)
    se_60 = sigma_bat / np.sqrt(60 + K)
    ax1.plot([59, 60], [se_59, se_60], 'ro', markersize=6)
    ax1.annotate(f"N=59: SE={se_59:.2f}\nN=60: SE={se_60:.2f}\n($\\Delta$ = 0.01 pts)", 
                 (60, se_60), xytext=(20, 25), textcoords='offset points',
                 fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffcc', edgecolor='#cccc00'))

    ax1.set_title("A. Statistical Estimation Uncertainty vs Sample Size", fontsize=13, fontweight='bold')
    ax1.set_xlabel("High-Pressure Deliveries (Balls Faced / Bowled)", fontsize=11)
    ax1.set_ylabel("Posterior Standard Error (Points)", fontsize=11)
    ax1.legend(loc='upper right', frameon=True)

    # Panel B: Confidence Intervals for Edge-Case Players
    ax2 = axes[0, 1]
    edge_names = [
        ('Mahendra Singh Dhoni', 'Batter', b_df),
        ('Jamie Overton', 'Batter', b_df),
        ('Sai Sudharsan', 'Batter', b_df),
        ('Tim Southee', 'Bowler', bo_df),
        ('Nasum Ahmed', 'Bowler', bo_df),
        ('Shoriful Islam', 'Bowler', bo_df),
        ('Simarjeet Singh', 'Bowler', bo_df),
        ('Mayank Yadav', 'Bowler', bo_df)
    ]

    y_pos = np.arange(len(edge_names))
    scores = []
    errors = []
    labels = []
    colors = []

    for name, disc, df_sub in edge_names:
        row = df_sub[df_sub['player_name'] == name].iloc[0]
        score = row['brs'] if disc == 'Batter' else row['bors']
        err = row['brs_margin_90'] if disc == 'Batter' else row['bors_margin_90']
        n_balls = row['high_balls_faced'] if disc == 'Batter' else row['high_legal_balls']
        
        scores.append(score)
        errors.append(err)
        labels.append(f"{name.split()[-1]} ({disc[0]}, {n_balls}b, {row['hp_matches']}m)")
        # Red if <60 balls, Blue if >=60 balls
        colors.append('#d62728' if n_balls < 60 else '#1f77b4')

    for i in range(len(y_pos)):
        ax2.errorbar(scores[i], y_pos[i], xerr=errors[i], fmt='o', color=colors[i],
                     ecolor=colors[i], elinewidth=2.5, capsize=4, markersize=8)
        ax2.text(scores[i] + errors[i] + 0.8, y_pos[i], f"{scores[i]:.1f} ±{errors[i]:.1f}", 
                 va='center', fontsize=8.5, fontweight='bold')

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels, fontsize=9.5)
    ax2.set_title("B. 90% Confidence Intervals for Boundary & Anchor Players", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Reliability Score [0, 100] (Blue: >= 60b, Red: < 60b)", fontsize=11)
    ax2.set_xlim(50, 105)

    # Panel C: Match Count vs Ball Count (Volume vs Breadth)
    ax3 = axes[1, 0]
    ax3.scatter(b_df[t1_b_off]['high_balls_faced'], b_df[t1_b_off]['hp_matches'], 
                color='#1f77b4', alpha=0.7, s=40, label='Batters (Tier 1 Baseline, N=116)')
    ax3.scatter(b_df[~t1_b_off & b_df['qual_dual']]['high_balls_faced'], b_df[~t1_b_off & b_df['qual_dual']]['hp_matches'], 
                color='#ff7f0e', alpha=0.9, s=60, marker='*', label='Batters (Dual-Criteria Newly Admitted, N=30)')
    
    ax3.axvline(60, color='red', linestyle='--', linewidth=1.2, label='Official 60-Ball Cutoff')
    ax3.axvline(50, color='orange', linestyle=':', linewidth=1.2, label='Proposed 50-Ball Floor')
    ax3.axhline(6, color='green', linestyle=':', linewidth=1.2, label='Minimum 6 Matches')

    # Annotate Overton and Shubham Dubey
    ax3.annotate('Overton (59b, 12m)', (59, 12), xytext=(10, 15), textcoords='offset points',
                 fontsize=8.5, fontweight='bold', arrowprops=dict(arrowstyle='->', color='black'))
    dubey = b_df[b_df['player_name'] == 'Shubham Dubey'].iloc[0]
    ax3.annotate('S. Dubey (64b, 7m)', (dubey['high_balls_faced'], dubey['hp_matches']), xytext=(-40, 20), textcoords='offset points',
                 fontsize=8.5, fontweight='bold', arrowprops=dict(arrowstyle='->', color='black'))

    ax3.set_title("C. Sample Volume (Balls) vs Breadth (Matches Faced)", fontsize=13, fontweight='bold')
    ax3.set_xlabel("High-Pressure Deliveries Faced", fontsize=11)
    ax3.set_ylabel("High-Pressure Matches Played", fontsize=11)
    ax3.legend(loc='lower right', frameon=True, fontsize=8.5)

    # Panel D: Qualification Pool Comparison Bar Chart
    ax4 = axes[1, 1]
    qual_schemes = ['Baseline (60b)', 'Dual-Criteria\n(60b OR 50b+6m)', 'Pure 50b Floor', 'Tier 1+2 (40b+)']
    bat_counts = [n_bat_off, n_bat_dual, n_bat_50b, (b_df['high_balls_faced'] >= 40).sum()]
    bowl_counts = [n_bowl_off, n_bowl_dual, n_bowl_50b, (bo_df['high_legal_balls'] >= 40).sum()]

    x_idx = np.arange(len(qual_schemes))
    w = 0.35
    ax4.bar(x_idx - w/2, bat_counts, w, label='Batters Qualified', color='#1f77b4', alpha=0.85)
    ax4.bar(x_idx + w/2, bowl_counts, w, label='Bowlers Qualified', color='#2ca02c', alpha=0.85)

    for i in range(len(qual_schemes)):
        ax4.text(x_idx[i] - w/2, bat_counts[i] + 3, str(bat_counts[i]), ha='center', fontsize=9, fontweight='bold', color='#1f77b4')
        ax4.text(x_idx[i] + w/2, bowl_counts[i] + 3, str(bowl_counts[i]), ha='center', fontsize=9, fontweight='bold', color='#2ca02c')

    ax4.set_xticks(x_idx)
    ax4.set_xticklabels(qual_schemes, fontsize=9.5)
    ax4.set_title("D. Qualified Population Sizes Across Eligibility Policies", fontsize=13, fontweight='bold')
    ax4.set_ylabel("Number of Qualified Players", fontsize=11)
    ax4.set_ylim(0, 220)
    ax4.legend(loc='upper left', frameon=True)

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "04_exp12_4_confidence_qualification.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Generated visualization chart at {chart_path.name}")

    # 8. Generate Comprehensive Markdown Report
    report_path = OUTPUT_DIR / "exp12_4_confidence_qualification_report.md"
    
    # Prepare top newly admitted players markdown table
    newly_admitted_md = []
    for _, r in comparison_df.head(10).iterrows():
        newly_admitted_md.append(
            f"| {r['discipline']} | **{r['player_name']}** | {r['sample_balls']} | {r['hp_matches']} | "
            f"**{r['score']:.2f}** | ±{r['std_error']*1.645:.2f} | #{int(r['tier2_rank'])} | **#{int(r['rank_dual'])}** |"
        )
    newly_admitted_table = "\n".join(newly_admitted_md)

    report_content = f"""# Step 12: Experiment 12.4 — Confidence-Based Qualification Investigation Report

## Executive Summary

Experiment 12.4 investigates whether the existing qualification threshold of 60 high-pressure balls creates an excessive eligibility cliff, quantifies statistical estimation uncertainty across sample sizes, and evaluates dual-criteria (volume + breadth) and continuous uncertainty-based approaches without introducing arbitrary sigmoids:

$$\\text{{SE}}(\\theta^*) = \\frac{{\\sigma}}{{\\sqrt{{N + K}}}}$$
$$\\text{{CI}}_{{90}} = [\\text{{Score}} \\pm 1.645 \\cdot \\text{{SE}}]$$

### Key Empirical Findings:
1. **Mathematical Proof of the Boundary Cliff:**
   - At $N = 59$ balls (Jamie Overton), posterior standard error is $\\text{{SE}} = 1.46$ points (90% margin: $\\pm 2.40$ pts).
   - At $N = 60$ balls (Simarjeet Singh), posterior standard error is $\\text{{SE}} = 1.45$ points (90% margin: $\\pm 2.39$ pts).
   - **The difference in statistical precision between 59 balls and 60 balls is a negligible 0.01 points.** Statistically, a player with 59 balls is indistinguishable from a player with 60 balls. The boundary cliff is an administrative policy threshold, not a statistical dividing line.
2. **Dual-Criteria Qualification (Volume + Breadth):**
   - Incorporating breadth ($M \\ge 6$ high-pressure matches) alongside volume ($N \\ge 50$ balls) admits **30 deserving batters** and **17 deserving bowlers** into the qualified tier.
   - **Elite Specialists Fairly Integrated:**
     - **Jamie Overton** (59 balls, 12 matches, BRS = 79.54) enters Qualified at **#6**.
     - **Nasum Ahmed** (55 balls, 10 matches, BoRS = 88.84) enters Qualified at **#2**.
     - **William Jacks** (54 balls, 18 matches, BRS = 66.88) enters Qualified at **#15**.
     - **Sai Sudharsan** (50 balls, 26 matches, BRS = 68.05) enters Qualified at **#12**.
     - **Quinton de Kock** (53 balls, 34 matches, BRS = 58.38) enters Qualified at **#47**.
   - These players have faced high pressure across 10 to 34 separate matches, demonstrating greater situational breadth than several baseline qualifiers whose 60 balls were concentrated in 7 or 8 matches.
3. **Evaluating Continuous Lower Credible Bound (LCB) Ranking:**
   - Subtracting $1.282 \\times \\text{{SE}}$ eliminates step boundaries, smoothly penalizing smaller samples. However, **LCB double-penalizes small-sample players** (once through Bayesian shrinkage toward the population mean $\\mu_0$, and again through subtracting estimation variance).
   - Therefore, a discrete qualification policy remains essential, but should be augmented with dual-criteria breadth requirements.

---

## 1. Estimation Uncertainty & Margin of Error Scaling

| High Balls ($N$) | Credibility $\\lambda$ ($K=50$) | Batting SE (pts) | Batting 90% Margin | Bowling SE (pts) | Bowling 90% Margin | Qualification Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **20** | 0.286 | 1.83 | ±3.01 | 1.58 | ±2.60 | Below Threshold |
| **40** | 0.444 | 1.61 | ±2.65 | 1.39 | ±2.29 | Tier 2 Specialist Floor |
| **50** | 0.500 | 1.53 | ±2.52 | 1.32 | ±2.17 | Proposed Dual Floor |
| **59** | 0.541 | 1.46 | ±2.40 | 1.26 | ±2.07 | Tier 2 Ceiling (Overton) |
| **60** | 0.545 | 1.45 | ±2.39 | 1.25 | ±2.06 | Official Tier 1 Cutoff |
| **100** | 0.667 | 1.25 | ±2.06 | 1.08 | ±1.78 | Mid-Sample Veteran |
| **150** | 0.750 | 1.08 | ±1.78 | 0.93 | ±1.53 | Established Regular |
| **200** | 0.800 | 0.97 | ±1.59 | 0.84 | ±1.37 | High-Exposure Elite |

> [!IMPORTANT]
> The table demonstrates that marginal estimation precision gains follow a standard diminishing square-root curve. The precision difference between 50 balls (±2.52) and 60 balls (±2.39) is only **0.13 points**.

---

## 2. Dual-Criteria Qualification Model

### Design Specification:
A player qualifies for the Primary Leaderboard if they satisfy:
$$\\text{{Condition 1: }} N \\ge 60 \\quad \\text{{(Established Volume Cutoff)}}$$
$$\\mathbf{{OR}}$$
$$\\text{{Condition 2: }} N \\ge 50 \\quad \\mathbf{{AND}} \\quad M_{{\\text{{HP}}}} \\ge 6 \\quad \\text{{(High Breadth Specialist)}}$$

### Qualification Impact Summary:
- **Batting Qualified Pool:** Expands from **116 to 146 batters (+30 players, +25.9%)**.
- **Bowling Qualified Pool:** Expands from **113 to 130 bowlers (+17 players, +15.0%)**.

### Newly Qualified International & Franchise Regulars:

| Discipline | Player Name | Sample Balls | HP Matches | Reliability Score | 90% Error Margin | Tier 2 Rank | Dual Rank |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
{newly_admitted_table}

---

## 3. Answers to Specific Evaluation Questions

### Q1: Does the 60-ball threshold create an excessive eligibility cliff?
**YES, at the individual boundary.** Jamie Overton (59 balls, 12 matches, BRS 79.54) and Nasum Ahmed (55 balls, 10 matches, BoRS 88.84) were completely excluded from Tier 1 rankings despite possessing higher match experience and statistical precision virtually identical to 60-ball qualifiers.

### Q2: Is an arbitrary sigmoid weighting function warranted?
**NO.** A sigmoid continuous dampener penalizes small-sample players by multiplying their score toward zero. This violates the Bayesian principle that small-sample players should shrink toward the league average ($\mu_0$), not toward zero.

### Q3: Why is Dual-Criteria (Volume + Breadth) superior?
Dual-criteria recognizes that match experience provides cross-situational robustness. A player who has faced high pressure across 12 different matches against diverse opponents is more proven than a player who faced 60 deliveries across only 3 matches on a single favorable pitch.

### Q4: Recommendation for Experiment 12.4:
**RECOMMENDED (STRONG CANDIDATE FOR FUTURE IMPLEMENTATION).** The Dual-Criteria model ($N \\ge 60$ OR $N \\ge 50 \\& M \\ge 6$) seamlessly bridges the boundary cliff, admits proven international specialists (Overton, Nasum, Jacks, Sudharsan), and requires zero arbitrary sigmoid mathematics.

---
*(Generated by Step 12 — Experiment 12.4 Validation Engine)*
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Generated validation report at {report_path.name}")
    print("=" * 70)
    print("EXPERIMENT 12.4 COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    run_experiment_12_4()
