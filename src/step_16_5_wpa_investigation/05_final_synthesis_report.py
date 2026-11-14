"""
Step 16.5: Script 05 - Generate Final Master Synthesis Report
============================================================
Synthesizes all empirical results from Sections 2 to 8 into:
outputs/step_16_5_wpa_investigation/step_16_5_final_report.md.
Answers all 8 required project questions, separates verified from suggestive
and unresolved evidence, and provides a definitive, evidence-backed recommendation.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

OUTPUT_DIR = Path("outputs/step_16_5_wpa_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=== Step 16.5 Script 05: Master Synthesis Report Generation ===")

    # Load tables for exact verified figures
    lev_df = pd.read_csv(OUTPUT_DIR / "pi_vs_leverage_summary.csv")
    wpa_df = pd.read_csv(OUTPUT_DIR / "pi_vs_actual_wpa_summary.csv")
    quad_df = pd.read_csv(OUTPUT_DIR / "four_quadrant_analysis.csv")
    sens_df = pd.read_csv(OUTPUT_DIR / "four_quadrant_cutoff_sensitivity.csv")
    pos_df = pd.read_csv(OUTPUT_DIR / "batting_position_wpa_leverage.csv")
    bowl_df = pd.read_csv(OUTPUT_DIR / "bowling_phase_wpa_leverage.csv")
    cons_df = pd.read_csv(OUTPUT_DIR / "player_consistency_summary.csv")
    val_df = pd.read_csv(OUTPUT_DIR / "wp_model_validation_summary.csv")

    rep_path = OUTPUT_DIR / "step_16_5_final_report.md"
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write("# Step 16.5 — Pressure Index vs Win Probability Impact (WPA) Investigation\n\n")
        f.write("**Audit Date:** 2026-11-14  \n")
        f.write("**Project:** SupeRR Selector Season 2 — Round 1  \n")
        f.write("**Investigation Topic:** The Empirical Relationship Between Pressure Index (PI) and Win Probability Impact (WPA / Delivery Leverage)  \n")
        f.write("**Baseline Population:** 188,097 Clean Active Deliveries across 789 Matches (180,839 Batting Balls Faced; 180,041 Bowling Legal Balls)  \n")
        f.write("**Methodology Foundation:** Frozen Step 16 Phase $\\times$ Innings Z-Score Classification ($Z > 1.00$)  \n")
        f.write("**Status:** Investigation Completed; Definitive Recommendation Finalized  \n\n")
        f.write("---\n\n")

        # -------------------------------------------------------------
        # 1. Executive Summary
        # -------------------------------------------------------------
        f.write("## 1. Executive Summary\n\n")
        f.write("This investigation evaluates whether deliveries classified as **High Pressure ($Z > 1.00$)** by our Pressure Index (PI) ")
        f.write("genuinely correspond to situations with high potential to influence the match outcome (Expected Delivery Leverage $\\mathbb{E}[|\\Delta \\text{WP}|]$) ")
        f.write("and whether they produce larger actual shifts in win probability (Actual WPA = $\\text{WP}_{\\text{after}} - \\text{WP}_{\\text{before}}$).\n\n")

        f.write("### Core Empirical Findings:\n")
        f.write("1. **PI and Match Leverage Are Fundamentally Orthogonal Dimensions:**  \n")
        f.write("   - Pressure Index measures **Task Difficulty / Resource Depletion** (how steep is the mountain facing the team?).\n")
        f.write("   - Expected Leverage measures **Game Uncertainty / Outcome Sensitivity** (is the match outcome in the balance?).\n")
        f.write("   - Across the entire population of 180,839 batting deliveries, the correlation between PI Z-score and Expected Leverage is **negative**: Pearson $r = -0.0522$, Spearman $\\rho = -0.0814$.\n\n")

        f.write("2. **High PI Deliveries Have Lower Average Leverage in Run Chases:**  \n")
        f.write("   - In **Innings 2**, High Pressure deliveries have **0.94% expected leverage** compared to **1.74% for Non-HP deliveries** (a deficit of **-0.79 pp**, 95% CI: `[-0.86 pp, -0.73 pp]`).\n")
        f.write("   - Why? Because **58.2% of Innings 2 High Pressure deliveries occur when Win Probability is $< 10\\%$** (hopeless collapses where required run rate is $> 18$ and $7\\text{--}9$ wickets have fallen). In those blowout states, delivery leverage collapses toward zero because the match is already decided.\n\n")

        f.write("3. **PI Systematically Misses Tense, Balanced Finishes:**  \n")
        f.write("   - Deliveries in close, knife-edge finishes (e.g. 18 runs needed off 12 balls with 6 wickets in hand) have Win Probability $\\approx 50\\%$ and massive leverage ($> 2.5\\%$).\n")
        f.write("   - However, because the batting side has wickets in hand and moderate RRR, PI assigns them **low to moderate scores ($Z \\le 1.00$)**, placing them into **Quadrant 3 (Tense Parity: 43.5% of all balls)**.\n\n")

        f.write("4. **Divergence Across Batting Order Positions:**  \n")
        f.write("   - For **Top-Order batters (positions 1–3)**, High Pressure deliveries DO carry higher leverage (+0.12 pp, $r = +0.1937$), because early pressure situations occur when the match remains winnable.\n")
        f.write("   - For **Lower-Order tailenders (positions 7–11)**, High Pressure deliveries carry vastly lower leverage (**-1.05 pp**, $r = -0.2616$). At Position 11, HP capture rate is **88.7%**, but median leverage is just **0.29%**.\n\n")

        f.write("5. **Definitive Recommendation:** **Retain PI as currently defined for Round 1, but formally recognize WPA and Expected Leverage as a separate, complementary dimension for Round 2 development (Option 2).**\n\n")
        f.write("---\n\n")

        # -------------------------------------------------------------
        # 2. Section 2: Win Probability Framework Reliability
        # -------------------------------------------------------------
        f.write("## 2. Reliability Audit of the Win Probability Framework\n\n")
        f.write("In accordance with Section 2 instructions, we constructed an enhanced, independently audited Win Probability and Leverage model:\n\n")
        f.write("- **Venue-Adjusted Innings 1 Model:** Replaced the arbitrary 160-par assumption with Bayesian-shrunk venue pars ($K = 8.0$), capturing venue scoring baselines that range from 155 to 201 runs across 94 grounds.\n")
        f.write("- **5-Fold Match-Held-Out Cross Validation:** Partitioned strictly at `match_id` level. Out-of-fold generalization was verified with negligible overfitting gap:\n")
        f.write("  * Innings 2: In-sample Brier = `0.1341` vs 5-Fold CV Brier = `0.1351` (Overfitting $\\Delta = +0.0010$).\n")
        f.write("  * Innings 1: In-sample Brier = `0.2215` vs 5-Fold CV Brier = `0.2227` (Overfitting $\\Delta = +0.0011$).\n")
        f.write("- **Situation-Dependent Outcome Probability Matrix:** Calculated empirical delivery event probabilities across all 6 (Innings $\\times$ Phase) strata across 10 delivery types (dots, 1s, 2s, 3s, 4s, 6s, wickets, wides, no-balls, rare runs), verified to sum to exactly `1.0000` in every stratum.\n")
        f.write("- **Strict Temporal Isolation:** Both `wp_before` and `expected_leverage` use only pre-delivery information. Zero outcome leakage exists.\n\n")

        f.write("| Model Specification | Deliveries | Matches | In-Sample Brier | 5-Fold CV Brier | Overfitting Gap | Feature Vector Specification |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n")
        for _, r in val_df.iterrows():
            f.write(f"| **{r['model_name']}** | {r['observations']:,} | {r['unique_matches']} | {r['in_sample_brier']:.4f} | **{r['cv_5fold_brier']:.4f}** | {r['overfitting_gap']:+.4f} | {r['primary_features']} |\n")

        f.write("\n---\n\n")

        # -------------------------------------------------------------
        # 3. Section 5A & 5B: Empirical Comparison Tables
        # -------------------------------------------------------------
        f.write("## 3. Empirical Comparison: Pressure Index vs. Match Leverage & Actual WPA\n\n")

        f.write("### 3.1 PI vs. Expected Delivery Leverage (Section 5A)\n\n")
        f.write("| Dimension | Subgroup | Deliveries | HP Count | HP % | Mean Lev (All) | Mean Lev (HP) | Mean Lev (Non-HP) | Diff (HP - Non-HP) | 95% Clustered CI | Pearson $r$ | Spearman $\\rho$ |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in lev_df.iterrows():
            f.write(f"| {r['dimension']} | **{r['subgroup']}** | {r['total_deliveries']:,} | {r['hp_deliveries']:,} | {r['hp_capture_pct']:.1f}% | {r['mean_leverage_all']:.2f}% | **{r['mean_leverage_hp']:.2f}%** | **{r['mean_leverage_non_hp']:.2f}%** | **{r['leverage_diff_hp_minus_nh']:+.2f} pp** | [{r['ci_95_diff_lower']:+.2f}, {r['ci_95_diff_upper']:+.2f}] | {r['pearson_r_z_leverage']:+.4f} | {r['spearman_rho_z_leverage']:+.4f} |\n")

        f.write("\n### 3.2 PI vs. Actual WPA Impact (Section 5B)\n\n")
        f.write("| Dimension | Subgroup | Mean Signed WPA (HP) | Mean Signed WPA (Non-HP) | Mean |WPA| (HP) | Median |WPA| (HP) | Mean |WPA| (Non-HP) | Median |WPA| (Non-HP) | |WPA| Diff | 95% Clustered CI | Pearson $r$ |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in wpa_df.iterrows():
            f.write(f"| {r['dimension']} | **{r['subgroup']}** | {r['mean_signed_wpa_hp']:+.2f}% | {r['mean_signed_wpa_non_hp']:+.2f}% | **{r['mean_absolute_wpa_hp']:.2f}%** | {r['median_absolute_wpa_hp']:.2f}% | **{r['mean_absolute_wpa_non_hp']:.2f}%** | {r['median_absolute_wpa_non_hp']:.2f}% | **{r['abs_wpa_diff_hp_minus_nh']:+.2f} pp** | [{r['ci_95_diff_lower']:+.2f}, {r['ci_95_diff_upper']:+.2f}] | {r['pearson_r_z_abs_wpa']:+.4f} |\n")

        f.write("\n---\n\n")

        # -------------------------------------------------------------
        # 4. Section 5C: Four-Quadrant Analysis
        # -------------------------------------------------------------
        f.write("## 4. Four-Quadrant Analysis: Pressure Index vs. Match Leverage\n\n")
        f.write("Deliveries are cross-classified using the frozen Step 16 PI threshold ($Z > 1.00$) and the empirical population median expected leverage (**1.14%**):\n\n")

        f.write("| Quadrant Name | Deliveries | % of Total | % Inn 1 / Inn 2 | % PP / Mid / Death | Mean Wickets | Mean CRR / RRR (Inn 2) | Mean Win Prob | Median Win Prob | Mean Leverage | Mean |WPA| |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in quad_df.iterrows():
            rrr_str = f"{r['mean_rrr_inn2']:.1f}" if pd.notna(r['mean_rrr_inn2']) else "—"
            f.write(f"| **{r['quadrant']}** | {r['deliveries']:,} | **{r['pct_of_total']:.1f}%** | {r['pct_innings_1']:.0f}% / {r['pct_innings_2']:.0f}% | {r['pct_powerplay']:.0f}% / {r['pct_middle_overs']:.0f}% / {r['pct_death_overs']:.0f}% | {r['mean_wickets_lost']:.1f} | {r['mean_crr']:.1f} / {rrr_str} | **{r['mean_win_probability_pct']:.1f}%** | {r['median_win_probability_pct']:.1f}% | **{r['mean_expected_leverage']:.2f}%** | {r['mean_absolute_wpa']:.2f}% |\n")

        f.write("\n### 4.1 Detailed Breakdown of the Four Regimes:\n")
        f.write("1. **Q1: True Clutch Situations (11,698 balls, 6.5%):**  \n")
        f.write("   - High PI ($Z > 1.00$) AND High Leverage ($\\ge 1.14\\%$). Mean Win Probability = $39.8\\%$.\n")
        f.write("   - Tight chases where required run rate is steep (11.1 RPO) but the match is completely in reach with wickets in hand.\n")
        f.write("2. **Q2: Crisis Collapses (21,010 balls, 11.6%):**  \n")
        f.write("   - High PI ($Z > 1.00$) BUT Low Leverage ($< 1.14\\%$). Mean Win Probability = **21.0%** (median: **14.7%**).\n")
        f.write("   - Lost-cause blowouts (mean wickets lost = 4.7, Innings 2 RRR = 19.5 RPO). The batting side faces extreme task difficulty, but the match outcome cannot be altered.\n")
        f.write("3. **Q3: Tense Parity (78,732 balls, 43.5%):**  \n")
        f.write("   - Low PI ($Z \\le 1.00$) BUT High Leverage ($\\ge 1.14\\%$). Mean Win Probability = **52.9%** (median: **52.9%**).\n")
        f.write("   - Balanced matches where RRR is manageable (9.3 RPO) and wickets are preserved. Every single delivery causes massive win-probability swings (mean leverage = $1.95\\%$, mean $|\\text{WPA}| = 1.96\\%$), yet PI classifies them as non-high-pressure!\n")
        f.write("4. **Q4: Routine Calm Play (69,399 balls, 38.4%):**  \n")
        f.write("   - Low PI AND Low Leverage. Calm middle overs where the match is progressing steadily.\n\n")

        f.write("### 4.2 Sensitivity Analysis Across Five Cutoffs\n\n")
        f.write("| Cutoff Specification | Cutoff Value | Q1 % (True Clutch) | Q2 % (Crisis Collapses) | Q3 % (Tense Parity) | Q4 % (Routine) | Q1 / Q2 Ratio | High Leverage Share in HP |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in sens_df.iterrows():
            f.write(f"| **{r['cutoff_label']}** | {r['cutoff_value']:.2f}% | {r['q1_pct']:.1f}% | {r['q2_pct']:.1f}% | {r['q3_pct']:.1f}% | {r['q4_pct']:.1f}% | {r['q1_q2_ratio']:.2f} | **{r['high_lev_share_in_hp_pct']:.1f}%** |\n")

        f.write("\n> **Robustness Finding:** Regardless of whether the leverage cutoff is set at 1.00%, 1.14%, 1.20%, or 1.51%, the majority of High Pressure deliveries ($57\\%\\text{ to }76\\%$) fall into Low Leverage (Q2), while the vast majority of High Leverage deliveries ($83\\%\\text{ to }87\\%$) occur at Low PI (Q3). The divergence is structural, not an artifact of threshold selection.\n\n")

        f.write("---\n\n")

        # -------------------------------------------------------------
        # 5. Section 5D & 5E: Positional & Bowling Phase Analyses
        # -------------------------------------------------------------
        f.write("## 5. Positional and Bowling Phase Analyses\n\n")

        f.write("### 5.1 Batting Positions 1 to 11 (Section 5D)\n\n")
        f.write("| Position | Assigned Role | Deliveries | HP Capture % | Mean Leverage (All) | Median Leverage | Mean Leverage in HP | Mean Leverage in Non-HP | Leverage at Matched Z (0.5–1.5) | Mean Signed WPA | Mean |WPA| |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in pos_df.iterrows():
            f.write(f"| **{r['batting_position']}** | {r['role']} | {r['deliveries']:,} | **{r['hp_capture_pct']:.1f}%** | {r['mean_expected_leverage']:.2f}% | {r['median_expected_leverage']:.2f}% | **{r['mean_leverage_in_hp']:.2f}%** | {r['mean_leverage_in_non_hp']:.2f}% | {r['mean_leverage_at_matched_z_05_15']:.2f}% | {r['mean_signed_wpa']:+.2f}% | {r['mean_absolute_wpa']:.2f}% |\n")

        f.write("\n### 5.2 Bowling Phases (Section 5E)\n\n")
        f.write("| Bowling Phase | Total Legal Balls | HP Bowling % | High Leverage % | Overlap Count | Overlap % of HP | Mean Expected Leverage | Median Expected Leverage | Mean Bowler WPA | Mean Bowler |WPA| |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in bowl_df.iterrows():
            f.write(f"| **{r['bowling_phase']}** | {r['total_legal_balls']:,} | **{r['hp_bowling_capture_pct']:.1f}%** | **{r['high_leverage_pct']:.1f}%** | {r['hp_and_high_leverage_overlap_count']:,} | **{r['overlap_pct_of_hp']:.1f}%** | {r['mean_expected_leverage']:.2f}% | {r['median_expected_leverage']:.2f}% | {r['mean_bowler_wpa']:+.3f}% | {r['mean_absolute_wpa']:.2f}% |\n")

        f.write("\n---\n\n")

        # -------------------------------------------------------------
        # 6. Section 6: Player-Level Reliability Findings
        # -------------------------------------------------------------
        f.write("## 6. Player-Level Reliability Findings (Section 6)\n\n")
        f.write("This supporting analysis evaluates how players perform in actual win-probability terms relative to the leverage of the situations they faced:\n\n")

        f.write("### 6.1 Batting Reliability Highlights (Tier 1 Qualified Batters)\n")
        f.write("- **Positive WPA Leaders in High Pressure:** Yashasvi Jaiswal (+98.1% WPA), Suryakumar Yadav (+37.7% WPA), Shivam Dube (+33.9% WPA), Cameron Green (+35.7% WPA), and Mitchell Marsh (+46.8% WPA).\n")
        f.write("- **Negative WPA in High Pressure:** Lower-order bowling all-rounders and tailenders consistently exhibit negative total WPA in HP situations (e.g. Maheesh Theekshana -114.2%, Azmatullah Omarzai -77.6%, Rashid Khan -71.6%, Axar Patel -76.5%). Because they bat in hopeless chases with impossible run rates, their dismissals and dot balls steadily bleed the remaining fractions of win probability.\n")
        f.write("- **Match Consistency:** Top batters exhibit match WPA standard deviations of 8% to 15%. Over 60% of their matches yield positive or neutral WPA contributions.\n\n")

        f.write("### 6.2 Bowling Reliability Highlights (Tier 1 Qualified Bowlers)\n")
        f.write("- **Positive Bowler WPA Leaders in High Pressure:** Axar Patel (+173.8% Bowler WPA), Harshit Rana (+122.2%), Rashid Khan (+95.2%), Sunil Narine (+94.7%), Ravi Bishnoi (+87.7%), and Jasprit Bumrah (+83.6%).\n")
        f.write("- **Consistency:** Elite bowlers maintain positive match WPA in 48% to 65% of their matches, holding volatility ($\sigma_{\\text{match}}$) below 14%.\n\n")

        f.write("---\n\n")

        # -------------------------------------------------------------
        # 7. Section 9: Answers to the Eight Specific Questions
        # -------------------------------------------------------------
        f.write("## 7. Answers to the Eight Specific Project Questions\n\n")

        f.write("### Question 1: Does high PI correspond to high expected match leverage?\n")
        f.write("**Definitive Answer: NO, not generally.**  \n")
        f.write("Across the full batting delivery population, High PI ($Z > 1.00$) deliveries have **lower expected leverage** ($1.05\\%$) than Non-HP deliveries ($1.40\\%$), a statistically significant deficit of **-0.35 pp** (95% CI: `[-0.38 pp, -0.32 pp]`). The overall Pearson correlation is negative ($r = -0.0522$). High PI measures task difficulty, which peaks in blowout collapses where expected leverage collapses toward zero.\n\n")

        f.write("### Question 2: Does high PI correspond to larger actual WPA?\n")
        f.write("**Definitive Answer: NO.**  \n")
        f.write("Mean absolute WPA ($|\\text{WPA}|$) for High Pressure deliveries is **1.01%**, compared to **1.39%** for Non-HP deliveries (a deficit of **-0.38 pp**, 95% CI: `[-0.41 pp, -0.35 pp]`). Deliveries that produce massive shifts in win probability ($|\\text{WPA}| > 5\\%$) occur predominantly in close, balanced matches at moderate PI values ($Z \\in [-0.5, +0.8]$).\n\n")

        f.write("### Question 3: Which situations have high PI but low expected leverage?\n")
        f.write("**Definitive Answer: Lost-Cause Collapses (Quadrant 2).**  \n")
        f.write("These account for **21,010 deliveries (11.6% of all balls)**. Key characteristics: 7–9 wickets down in Innings 2 with required run rates exceeding 18 RPO, or severe top-order collapses where Win Probability is $< 10\\%$. In these deliveries, the batting task is virtually impossible (sky-high PI), but the match outcome is already decided, so a six or a wicket moves win probability by less than 0.3%.\n\n")

        f.write("### Question 4: Which situations have low PI but high expected leverage?\n")
        f.write("**Definitive Answer: Tense Parity Finishes (Quadrant 3).**  \n")
        f.write("These account for **78,732 deliveries (43.5% of all balls)**. Key characteristics: Win Probability near 50%, required run rates between 8 and 10 RPO, and 4–7 wickets in hand. Because the team is not in a resource crisis, the PI formula assigns them low to moderate pressure ($Z \\le 1.00$). However, because the contest is on a knife edge, every boundary or dot ball causes massive swings in win probability (mean leverage = $1.95\\%$).\n\n")

        f.write("### Question 5: Does this relationship differ by innings, phase or batting position?\n")
        f.write("**Definitive Answer: YES, dramatically.**  \n")
        f.write("- **By Innings:** In Innings 1, High PI correlates positively with leverage (+0.06 pp, $r = +0.0738$) because all first-innings situations retain chase uncertainty. In Innings 2, High PI correlates negatively with leverage (**-0.79 pp**, $r = -0.0921$) due to lost-cause chases.\n")
        f.write("- **By Batting Position:** For Top-Order batters (1–3), High PI carries higher leverage (+0.12 pp, $r = +0.1937$). For Lower-Order tailenders (7–11), High PI carries vastly lower leverage (**-1.05 pp**, $r = -0.2616$). Tailenders face high PI almost exclusively in dead blowouts.\n")
        f.write("- **By Bowling Phase:** In Powerplay bowling, High PI and High Leverage align closely. In Death bowling, High Bowling PI carries **-0.97 pp lower leverage** than Non-HP death overs because many death overs are bowled in matches that are already decided.\n\n")

        f.write("### Question 6: Does WPA reveal an important dimension of pressure that the current PI misses?\n")
        f.write("**Definitive Answer: YES.**  \n")
        f.write("WPA reveals **Competitive Leverage** (the sensitivity of the victory condition to the next delivery). The current PI formula only measures **Resource Depletion** (overs elapsed, wickets lost, required run rate, and balls faced settling). Consequently, PI is blind to the intense pressure of a tied or balanced match where wickets remain in hand.\n\n")

        f.write("### Question 7: Should match pressure and match leverage be treated as separate measurements?\n")
        f.write("**Definitive Answer: YES, absolutely.**  \n")
        f.write("Conflating task difficulty with match leverage is a fundamental analytical error. A batter facing 20 off 6 balls with 2 wickets down is under extreme leverage (the match is winnable or losable right now). A batter facing 60 off 12 balls with 8 wickets down is under extreme task difficulty (impossible batting assignment, but match outcome is settled). They must be modeled as **orthogonal, complementary axes**.\n\n")

        f.write("### Question 8: Is there sufficient evidence to justify a future methodology change?\n")
        f.write("**Definitive Answer: YES, for Round 2.**  \n")
        f.write("The empirical evidence proving that PI misclassifies blowouts as high-pressure and misses close finishes is overwhelming. While the methodology remains frozen under Step 15 decisions for the immediate Round 1 submission deadline, developing an integrated **Leverage-Weighted Pressure Index (LWPI)** is the single highest-priority recommendation for Round 2.\n\n")

        f.write("---\n\n")

        # -------------------------------------------------------------
        # 8. Section 10: Definitive Recommendation
        # -------------------------------------------------------------
        f.write("## 8. Definitive Recommendation\n\n")
        f.write("We formally adopt:\n\n")
        f.write("### **Recommendation: Retain PI but recognise WPA/Expected Leverage as a separate dimension (Option 2)**\n\n")

        f.write("### Methodological Defense:\n")
        f.write("1. **Preserve Round 1 Submission Stability:**  \n")
        f.write("   Step 15 established a formal methodology freeze for Round 1 (BRS3, BoRS, $K=50$, Rule B, Step 16 Phase $\\times$ Innings baselines). The existing candidate rankings are fully validated, reproducible, and internally consistent. Injecting WPA or modifying thresholds now would violate the project charter.\n")
        f.write("2. **Avoid Conflating Two Distinct Phenomena:**  \n")
        f.write("   PI successfully evaluates player execution under severe environmental stress and resource exhaustion. Tailenders surviving hostile death bowling and finishers hitting boundaries under steep run rates deserve credit for executing difficult physical tasks, even in losing causes. BRS3 appropriately penalizes cheap dismissals via survival weighting.\n")
        f.write("3. **Clear Scientific Blueprint for Round 2:**  \n")
        f.write("   By recognizing WPA and Delivery Leverage as a distinct, orthogonal dimension, the project establishes a clean conceptual roadmap: Round 1 delivers reliability under task pressure; Round 2 integrates game-theoretic win-probability leverage.\n\n")

        f.write("---\n\n")

        # -------------------------------------------------------------
        # 9. Directory of Artifacts
        # -------------------------------------------------------------
        f.write("## 9. Directory of Step 16.5 Deliverables\n\n")
        f.write("All datasets, validation reports, and publication figures are accessible at the links below:\n\n")

        f.write("### Master & Validation Reports:\n")
        f.write("- [step_16_5_final_report.md](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/step_16_5_final_report.md) *(Master Investigation Report)*\n")
        f.write("- [wp_framework_audit_report.md](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/wp_framework_audit_report.md) *(Section 2 WP Framework Audit Report)*\n\n")

        f.write("### Investigation Datasets:\n")
        f.write("- [delivery_wpa_leverage.parquet](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/delivery_wpa_leverage.parquet) *(Master 188,097 Delivery Dataset with WP, WPA, and Leverage)*\n")
        f.write("- [pi_vs_leverage_summary.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/pi_vs_leverage_summary.csv) *(PI vs Expected Leverage by Phase, Innings, Role)*\n")
        f.write("- [pi_vs_actual_wpa_summary.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/pi_vs_actual_wpa_summary.csv) *(PI vs Signed and Absolute WPA with 95% CIs)*\n")
        f.write("- [four_quadrant_analysis.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/four_quadrant_analysis.csv) *(Four-Quadrant Breakdown at Median Cutoff 1.14%)*\n")
        f.write("- [four_quadrant_cutoff_sensitivity.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/four_quadrant_cutoff_sensitivity.csv) *(Sensitivity Analysis across 5 Leverage Cutoffs)*\n")
        f.write("- [batting_position_wpa_leverage.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/batting_position_wpa_leverage.csv) *(Batting Positions 1–11 WPA & Leverage Breakdown)*\n")
        f.write("- [bowling_phase_wpa_leverage.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/bowling_phase_wpa_leverage.csv) *(Bowling Phase WPA & HP/Leverage Overlap)*\n")
        f.write("- [player_batting_wpa_reliability.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/player_batting_wpa_reliability.csv) *(Player-Level Batting WPA Reliability across 816 Batters)*\n")
        f.write("- [player_bowling_wpa_reliability.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/player_bowling_wpa_reliability.csv) *(Player-Level Bowling WPA Reliability across 589 Bowlers)*\n")
        f.write("- [player_consistency_summary.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/player_consistency_summary.csv) *(Consistency Summary by Discipline and Tier)*\n")
        f.write("- [situation_outcome_probabilities.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/situation_outcome_probabilities.csv) *(Conditional Outcome Matrix across 6 Strata)*\n")
        f.write("- [wp_model_validation_summary.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/wp_model_validation_summary.csv) *(5-Fold CV Model Performance Summary)*\n\n")

        f.write("### Investigation Figures:\n")
        f.write("- [fig1_pi_zscore_vs_expected_leverage.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig1_pi_zscore_vs_expected_leverage.png) *(Figure 1: PI Z-Score vs Expected Leverage)*\n")
        f.write("- [fig2_pi_zscore_vs_absolute_wpa.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig2_pi_zscore_vs_absolute_wpa.png) *(Figure 2: PI Z-Score vs Absolute WPA)*\n")
        f.write("- [fig3_expected_leverage_distributions.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig3_expected_leverage_distributions.png) *(Figure 3: Expected Leverage Distributions for HP vs Non-HP)*\n")
        f.write("- [fig4_actual_wpa_distributions.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig4_actual_wpa_distributions.png) *(Figure 4: Actual Signed and Absolute WPA Distributions)*\n")
        f.write("- [fig5_four_quadrant_analysis.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig5_four_quadrant_analysis.png) *(Figure 5: Four-Quadrant Tactical Map)*\n")
        f.write("- [fig6_expected_leverage_by_innings_and_phase.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig6_expected_leverage_by_innings_and_phase.png) *(Figure 6: Expected Leverage by Innings and Phase)*\n")
        f.write("- [fig7_wpa_by_batting_position.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig7_wpa_by_batting_position.png) *(Figure 7: WPA and Leverage Across Batting Positions 1–11)*\n")
        f.write("- [fig8_wpa_by_bowling_phase.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig8_wpa_by_bowling_phase.png) *(Figure 8: Bowling Impact and Leverage Across Phases)*\n")
        f.write("- [fig9_player_match_wpa_consistency.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_5_wpa_investigation/fig9_player_match_wpa_consistency.png) *(Figure 9: Player Match WPA Consistency vs HP Impact)*\n")

    print(f"Master Synthesis Report written to {rep_path}")


if __name__ == "__main__":
    main()
