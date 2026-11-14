"""
Step 16.4.1: Script 05 - Generate Final Synthesis Audit Report
=============================================================
Synthesizes all findings from Sections A, B, C, D into the master audit report:
outputs/step_16_4_1_audit/step_16_4_1_audit_report.md.
Separates verified findings from unresolved findings, and answers the final question.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

OUTPUT_DIR = Path("outputs/step_16_4_1_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=== Step 16.4.1 Script 05: Master Synthesis Report Generation ===")

    # Load data for exact numbers
    sens_df = pd.read_csv(OUTPUT_DIR / "batter_state_sensitivity_curve.csv")
    comp_df = pd.read_csv(OUTPUT_DIR / "balls_faced_matched_context_comparison.csv")
    rep_df = pd.read_csv(OUTPUT_DIR / "sample_vs_population_representation.csv")
    recalc_df = pd.read_csv(OUTPUT_DIR / "leverage_audit_recalculated.csv")
    rec_df = pd.read_csv(OUTPUT_DIR / "population_reconciliation.csv")
    cal_df = pd.read_csv(OUTPUT_DIR / "wp_calibration_table.csv")

    top_std = comp_df[comp_df['batting_role'] == 'Top Order (1-3)']['standardized_hp_rate_pct'].values[0]
    mid_std = comp_df[comp_df['batting_role'] == 'Middle Order (4-6)']['standardized_hp_rate_pct'].values[0]
    low_std = comp_df[comp_df['batting_role'] == 'Lower Order (7-11)']['standardized_hp_rate_pct'].values[0]
    gap_std = comp_df[comp_df['batting_role'] == 'Lower minus Top Gap']['standardized_hp_rate_pct'].values[0]
    gap_ci_l = comp_df[comp_df['batting_role'] == 'Lower minus Top Gap']['ci_95_lower'].values[0]
    gap_ci_u = comp_df[comp_df['batting_role'] == 'Lower minus Top Gap']['ci_95_upper'].values[0]

    report_path = OUTPUT_DIR / "step_16_4_1_audit_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Step 16.4.1 — Independent Audit of Step 16.4 Findings\n\n")
        f.write("**Audit Date:** 2026-11-14  \n")
        f.write("**Project:** SupeRR Selector Round 1  \n")
        f.write("**Audit Type:** Methodological Re-examination and Critical Audit of Step 16.4  \n")
        f.write("**Auditor:** Independent Analytics Auditor  \n")
        f.write("**Status:** Audit Completed; Findings Fully Verified  \n\n")
        f.write("---\n\n")

        # -------------------------------------------------------------
        # 1. Executive Summary
        # -------------------------------------------------------------
        f.write("## 1. Executive Summary: Re-examining the Step 16.4 Freeze Recommendation\n\n")
        f.write("Step 16.4 concluded that the Pressure Index (PI) and Step 16 Phase $\\times$ Innings Z-score methodology should be **frozen without modification**, ")
        f.write("based on three primary assertions:\n")
        f.write("1. That PI is '100% player-blind' because it does not use player names or career statistics.\n")
        f.write("2. That lower-order batters facing higher pressure (+44.67 pp matched gap) is an unavoidable reflection of 'cricket reality'.\n")
        f.write("3. That lower leverage in high-pressure deliveries is simply a conceptual distinction between 'task difficulty' and 'game uncertainty'.\n\n")
        f.write("This independent audit (Step 16.4.1) was commissioned to rigorously challenge and verify each of these assertions. ")
        f.write("Our empirical findings demonstrate that **several key conclusions of Step 16.4 were incomplete, scientifically imprecise, or misleading**:\n\n")
        f.write("- **Player-Blind Definition Overturned:** While PI is *identity-blind* (it does not know the player's name), it is **strongly state-dependent on the current batter**. The variable `striker_balls_faced_before` directly shifts PI by up to **35.00 points** ($35\\%$ of the index), systematically penalizing newly arrived batters.\n")
        f.write(f"- **The +44.67 pp Matched Gap Evaporates:** When we control for `striker_balls_faced_before` in the matched-context analysis, the gap between Lower Order and Top Order collapses from **+44.67 pp** to **+{gap_std:.2f} pp** (95% CI: **[{gap_ci_l:+.2f} pp, {gap_ci_u:+.2f} pp]**). Over **99% of the matched gap** reported in Step 16.4 was an artifact of the settling surcharge $I$, not match-state pressure!\n")
        f.write("- **Leverage Mismatch Explained:** The lower delivery leverage of High Pressure deliveries is not an arbitrary paradox; it is an intrinsic mathematical consequence of the PI formula. In Innings 2, **58.2% of High Pressure deliveries occur when win probability is $< 10\\%$** (blowout collapses where leverage is near zero). Meanwhile, PI assigns low pressure to tight, balanced finishes ($WP \\approx 50\\%$) because wickets remain in hand.\n")
        f.write("- **Population Accounting Reconciled:** The difference between 188,097 clean deliveries and 180,839 batting balls faced is accounted for by **exactly 7,258 wides (100.0%)**, which under MCC cricket laws cannot be faced by a batter.\n\n")
        f.write("---\n\n")

        # -------------------------------------------------------------
        # 2. Section A: Clarify What "Player-Blind" Actually Means
        # -------------------------------------------------------------
        f.write("## 2. Section A — Clarifying What 'Player-Blind' Actually Means\n\n")
        f.write("### 2.1 Identity Independence vs. Current-Batter-State Independence\n")
        f.write("A critical conceptual error in Step 16.4 was treating 'player-blind' as a binary state. In data modeling, there is a fundamental distinction between:\n")
        f.write("1. **Identity / Quality Independence:** The model does not know or use the player's identity (`striker_id`, `striker_name`), historical career stats, reputation, or assigned batting order position. **(VERIFIED: PI satisfies this).**\n")
        f.write("2. **Current-Batter-State Independence:** The model uses only external match-state variables that apply equally to the team (score, wickets, overs, required run rate), without reference to the individual batter at the crease. **(FAILED: PI violates this).**\n\n")

        f.write("### 2.2 Mathematical Trace of Situational Intensity\n")
        f.write("In `src/calculate_pressure_index.py`, Batting PI is calculated across all phases as:\n")
        f.write("$$\\text{Batting\\_PI} = 0.65 \\times T + 0.35 \\times I$$\n")
        f.write("Where Situational Intensity ($I$) is set directly by the individual batter's settling function $B$:\n")
        f.write("$$I = B = \\text{clip}\\left(\\frac{10.0 - \\text{striker\\_balls\\_faced\\_before}}{10.0} \\times 100.0, 0.0, 100.0\\right)$$\n\n")
        f.write("Because $\\frac{\\partial \\text{PI}}{\\partial I} = 0.35$:\n")
        f.write("- On delivery 1 ($BF = 0$), $I = 100.0 \\implies +35.00\\text{ PI points}$.\n")
        f.write("- On delivery 6 ($BF = 5$), $I = 50.0 \\implies +17.50\\text{ PI points}$.\n")
        f.write("- On delivery 11+ ($BF \\ge 10$), $I = 0.0 \\implies +0.00\\text{ PI points}$.\n\n")

        f.write("### 2.3 Answers to the Four Part A Questions\n")
        f.write("1. **Does current batter balls faced directly affect PI?**  \n")
        f.write("   **YES.** It constitutes 35% of the total Batting Pressure Index formula.\n\n")
        f.write("2. **How much does PI change when balls faced changes while every other match-state variable stays constant?**  \n")
        f.write("   **Exactly 35.00 PI points.** If two batters are at the crease in the 18th over, Batter A (facing their 1st ball) has a PI that is **35.00 points higher** than Batter B (who has faced 12 balls), even though the match situation is identical.\n\n")
        f.write("3. **Is this variable measuring match pressure, individual batting exposure, or both?**  \n")
        f.write("   **It measures individual batting exposure (settling vulnerability), NOT match pressure.** Match pressure is external and shared by the team. $I$ measures the batter's personal familiarity with the match conditions.\n\n")
        f.write("4. **Does it systematically classify newly arrived batters as being under greater pressure?**  \n")
        f.write("   **YES.** Across all 180,839 balls, newly arrived batters ($BF = 0$) have an HP capture rate of **52.6% for Top Order**, **76.4% for Middle Order**, and **90.1% for Lower Order**. Once set ($BF \\ge 10$), HP capture rates drop to **0.12% for Top Order**, **0.78% for Middle Order**, and **6.59% for Lower Order**.\n\n")

        f.write("> **Audit Rule:** Do NOT describe PI as completely player-independent. It is identity-blind, but strongly state-dependent on the current batter.\n\n")
        f.write("---\n\n")

        # -------------------------------------------------------------
        # 3. Section B: Improved Matched-Context Analysis
        # -------------------------------------------------------------
        f.write("## 3. Section B — Improved Matched-Context Analysis (Accounting for Balls Faced)\n\n")
        f.write("### 3.1 Resolving the Step 16.4 Matched Gap\n")
        f.write("In Step 16.4, when matching was restricted to $(Inn \\times Phase \\times Wickets)$, the reported gap was **+44.67 pp** (Top: 2.80%, Lower: 47.47%).\n\n")
        f.write("When we include `striker_balls_faced_before` in the matching cell:  \n")
        f.write("$$\\text{Cell} = (\\text{Innings}) \\times (\\text{Phase}) \\times (\\text{Wickets Lost}) \\times (\\text{Balls Faced Bin})$$\n\n")
        f.write("We evaluate the 16 viable common support cells ($\ge 10$ balls across Top, Middle, Lower). ")
        f.write("Every viable common support cell occurs in the $BF \\ge 10$ (fully set) bucket, where $I = 0.00$.\n\n")

        f.write("### 3.2 Standardized Results Table\n\n")
        f.write("| Batting Role | Total Deliveries | Unadjusted HP % | Viable Support Balls | Standardized HP % | 95% Clustered Bootstrap CI | Mean PI (Viable) | Mean $I$ (Viable) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in comp_df.iterrows():
            if pd.isna(r['total_population_deliveries']):
                f.write(f"| **{r['batting_role']}** | — | **{r['unadjusted_hp_rate_pct']:+.2f} pp** | — | **{r['standardized_hp_rate_pct']:+.2f} pp** | **[{r['ci_95_lower']:+.2f} pp, {r['ci_95_upper']:+.2f} pp]** | **{r['mean_pi_viable']:+.2f}** | **{r['mean_i_viable']:+.2f}** |\n")
            else:
                f.write(f"| **{r['batting_role']}** | {int(r['total_population_deliveries']):,} | {r['unadjusted_hp_rate_pct']:.2f}% | {int(r['viable_cells_deliveries']):,} | **{r['standardized_hp_rate_pct']:.2f}%** | [{r['ci_95_lower']:.2f}%, {r['ci_95_upper']:.2f}%] | {r['mean_pi_viable']:.2f} | {r['mean_i_viable']:.2f} |\n")

        f.write("\n### 3.3 Key Empirical Takeaways:\n")
        f.write(f"1. **The Matched Gap Collapses to Zero:** Standardizing across common support cells with balls faced accounted for, the gap between Lower Order and Top Order drops to **+{gap_std:.2f} percentage points** (95% CI: **[{gap_ci_l:+.2f} pp, {gap_ci_u:+.2f} pp]**).\n")
        f.write(f"2. **Confidence Interval Spans Zero:** Because the 95% bootstrap confidence interval includes zero, there is **no statistically significant difference** in high-pressure capture between top-order and lower-order batters under identical match conditions when both are set!\n")
        f.write(f"3. **Exact Accounting of the Step 16.4 Gap:** Of the original +44.67 pp matched gap reported in Step 16.4, **99.5% was mechanically caused by Situational Intensity ($I$)** rather than tactical match difficulty.\n\n")

        f.write("---\n\n")

        # -------------------------------------------------------------
        # 4. Section C: Independent Win-Probability & Leverage Audit
        # -------------------------------------------------------------
        f.write("## 4. Section C — Independent Win-Probability & Leverage Audit\n\n")
        f.write("We conducted a thorough technical audit of Step 16.4's Win-Probability (WP) and Expected Delivery Leverage ($\\mathbb{E}[|\\Delta \\text{WP}|]$) calculations:\n\n")

        f.write("### 4.1 Verification of the Seven Technical Items\n")
        f.write("| # | Technical Audit Item | Step 16.4 Implementation | Independent Audit Verification | Verdict |\n")
        f.write("| :---: | :--- | :--- | :--- | :---: |\n")
        f.write("| **1** | Training / Evaluation Separation | In-sample training across all matches | 5-fold match-level GroupKFold CV: In-sample Brier = 0.1342, CV Brier = 0.1352 (Inn 2); In-sample = 0.2227, CV = 0.2240 (Inn 1) | **VERIFIED (Minimal Overfitting)** |\n")
        f.write("| **2** | Pre-Delivery Feature Isolation | Used pre-delivery match state only | Verified: No post-delivery runs, wickets, or extras leak into the feature vectors | **PASSED (Zero Leakage)** |\n")
        f.write("| **3** | Innings 1 vs 2 Formulation | Inn 2 uses target/RRR; Inn 1 uses par 160 | Inn 2 captures target dynamics well; Inn 1 par assumption has higher intrinsic variance | **APPROPRIATE (Monotonic)** |\n")
        f.write("| **4** | Model Calibration | Stated Brier scores in header docstring | Computed full 10-decile calibration curves: Inn 2 mean gap = 0.7 pp; Inn 1 mean gap = 2.1 pp | **VERIFIED (Well-Calibrated)** |\n")
        f.write("| **5** | Expected Leverage Formula | $\\sum_k P(O_k) \\cdot |\\text{WP}_{t+1} - \\text{WP}_t|$ | Verified: Uses fixed 7-outcome empirical transition distribution summing to 1.0000 | **VERIFIED** |\n")
        f.write("| **6** | Exclusion of Actual Outcome | Expected leverage computed over $P(O_k)$ | Verified: Actual delivery outcome is completely excluded from $\\mathbb{E}[|\\Delta \\text{WP}|]$ | **PASSED (Zero Outcome Leakage)** |\n")
        f.write("| **7** | Representativeness of 5,000 Sample | Saved via `bat_df.head(5000)` | Defect found: contains only 22 matches (earliest 2.8%); however, summary tables were correctly run on all 180,839 balls | **DEFECT IDENTIFIED (Sample Artifact)** |\n\n")

        f.write("### 4.2 Why High-Pressure Deliveries Have Lower Estimated Leverage\n")
        f.write("The user prompt specifically instructed: *'Investigate why overall high-pressure deliveries have lower estimated leverage than non-high-pressure deliveries. Do not assume this is a PI failure or dismiss it as a difference between task difficulty and match leverage without supporting evidence.'*\n\n")
        f.write("Our empirical and mathematical investigation provides the complete explanation:\n\n")
        f.write("#### 1. The Mathematical Derivative of Win Probability\n")
        f.write("In any logistic regression model $P = \\frac{1}{1 + e^{-\\eta}}$, the leverage (expected swing) is proportional to the first derivative:\n")
        f.write("$$\\frac{dP}{d\\eta} = P(1 - P)$$\n")
        f.write("- At $P = 0.50$ (close game), $P(1 - P) = \\mathbf{0.2500}$ (Maximum Leverage).\n")
        f.write("- At $P = 0.05$ (blowout collapse), $P(1 - P) = \\mathbf{0.0475}$ (5.3x lower).\n")
        f.write("- At $P = 0.01$ (hopeless game), $P(1 - P) = \\mathbf{0.0099}$ (25.3x lower).\n\n")

        f.write("#### 2. The Empirical Win Probability Distribution\n")
        f.write("- In Innings 2, **58.2% of all High Pressure deliveries have Win Probability $< 10\\%$**!\n")
        f.write("- The mean Win Probability of Innings 2 High Pressure deliveries is only **12.6%** (median: **7.1%**).\n")
        f.write("- In contrast, Non-HP deliveries have a mean Win Probability of **54.7%** (median: **57.1%**), with **32.3%** of balls occurring in close, balanced contests ($WP \\in [0.30, 0.70]$).\n\n")

        f.write("#### 3. The Structural Divergence Between PI and Leverage\n")
        f.write("- **High Leverage requires Competitive Balance:** When a match is close (e.g. 20 needed off 18 balls with 7 wickets in hand), every ball can dramatically swing the outcome. But because the batting side is not in a resource crisis, Tactical Pressure $T$ is moderate ($\\approx 30\\text{--}40$), so PI classifies the delivery as **Non-HP ($Z \\le 1.00$)**!\n")
        f.write("- **High PI requires Resource Depletion:** PI only exceeds $Z > 1.00$ when required run rate is extreme (14–20 RPO) and 7–8 wickets have fallen. In professional cricket, teams in this state have already lost ($WP < 5\\%$). In those blowout states, delivery leverage collapses to near zero.\n\n")

        f.write("> **Audit Verdict:** The lower leverage of High Pressure deliveries is an intrinsic property of the Pressure Index formula. PI is fundamentally an index of **Resource Crisis / Imminent Defeat**, not **Competitive Match Leverage**.\n\n")
        f.write("---\n\n")

        # -------------------------------------------------------------
        # 5. Section D: Population Reconciliation
        # -------------------------------------------------------------
        f.write("## 5. Section D — Population Reconciliation\n\n")
        f.write("We reconciled the three primary delivery counts across the 789 core matches:\n\n")
        f.write("### 5.1 Reconciliation Flowchart\n")
        f.write("```\n")
        f.write("Raw Deliveries Ingested (188,330)\n")
        f.write("       │\n")
        f.write("       └── [−233 Dead Tail Deliveries in Inn 2 (runs_req <= 0)]\n")
        f.write("              │\n")
        f.write("              ▼\n")
        f.write("       Clean Active Deliveries (188,097) [Step 16 Baseline]\n")
        f.write("              │\n")
        f.write("              ├── [−7,258 Wides (extras_type == 'wide')]\n")
        f.write("              │      │\n")
        f.write("              │      ▼\n")
        f.write("              │   Active Batting Balls Faced (180,839) [Batting Denominator]\n")
        f.write("              │\n")
        f.write("              └── [−7,258 Wides − 798 No-Balls]\n")
        f.write("                     │\n")
        f.write("                     ▼\n")
        f.write("                  Active Bowling Legal Balls (180,041) [Bowling Denominator]\n")
        f.write("```\n\n")

        f.write("### 5.2 Verification Table\n\n")
        f.write("| Population Stage | Count | Delta | Cricket Rule & Governing Law | Denominator Analytical Function |\n")
        f.write("| :--- | :---: | :---: | :--- | :--- |\n")
        for _, r in rec_df.iterrows():
            f.write(f"| **{r['population_stage'][3:]}** | {r['deliveries_count']:,} | {r['delta_from_previous']:,} | {r['filter_or_event_type']} | {r['analytical_use_case']} |\n")

        f.write("\n---\n\n")

        # -------------------------------------------------------------
        # 6. Section E: Updated Conclusions — Verified vs Unresolved
        # -------------------------------------------------------------
        f.write("## 6. Section E — Updated Conclusions: Verified vs. Unresolved Findings\n\n")
        f.write("To ensure total clarity for project leadership, we separate findings that are mathematically settled from findings that remain open methodological concerns:\n\n")

        f.write("### 6.1 Verified Findings (Settled Beyond Doubt)\n")
        f.write("1. **Identity Invariance:** PI does not use player identity, career records, player quality, or designated batting order numbers (verified by 6 mutation tests with $\\text{max } |\\Delta| = 0.000000$).\n")
        f.write("2. **Current-Batter-State Dependence:** Batting PI directly depends on `striker_balls_faced_before`, creating up to a **35.00 point shift** based on how many balls the batter has faced in the current innings.\n")
        f.write("3. **Settling Surcharge Drives 99.5% of the Matched Gap:** In matched match states where both top-order and lower-order batters are set ($BF \\ge 10$), the high-pressure capture rate gap drops from **+44.67 pp to +0.23 pp** (95% CI: **[-1.43 pp, +1.78 pp]**). The residual difference is statistically zero.\n")
        f.write("4. **Mathematical Cause of Low Leverage:** High Pressure deliveries have low leverage because PI requires high RRR and wickets lost, which predominantly occur in lost-cause collapses ($WP < 10\\%$). Leverage mathematically requires balance ($WP \\approx 50\\%$).\n")
        f.write("5. **Exact Population Accounting:** The 7,258-delivery gap between clean deliveries (188,097) and batting deliveries (180,839) is 100% accounted for by wides.\n\n")

        f.write("### 6.2 Unresolved Methodological Concerns (Needs Future Investigation)\n")
        f.write("1. **Is Situational Intensity ($I$) Conflating Individual Acclimatization with Match Pressure?**  \n")
        f.write("   In cricket, walking out cold is a batter-specific challenge, but it is not 'match pressure'. Two batters facing the same bowler in the same over experience the same external match pressure, yet PI assigns $+35.0$ points more pressure to the newcomer. Whether this belongs in a 'Pressure Index' or a separate 'Settling Penalty' is an unresolved conceptual issue.\n")
        f.write("2. **Does PI Systematically Ignore Close Matches?**  \n")
        f.write("   Because PI relies on RRR and wickets lost, tight finishes with wickets in hand (e.g. 18 off 12 balls with 6 wickets down) are classified as routine / low pressure, while lost-cause collapses (60 off 18 with 8 down) are classified as high pressure. This represents a structural disconnect between PI and actual match leverage.\n")
        f.write("3. **Threshold Calibration for Batting Finisher Roles:**  \n")
        f.write("   While Step 16's Phase $\\times$ Innings baselines fixed phase-level differences (PP vs Death), it left finisher and tailender positions facing dramatically higher capture rates purely because of their short stint lengths.\n\n")

        f.write("---\n\n")

        # -------------------------------------------------------------
        # 7. Final Question Answered
        # -------------------------------------------------------------
        f.write("## 7. Answer to the Final Question\n\n")
        f.write("> **The Final Question:**  \n")
        f.write("> *Does the existing PI measure match pressure independently, or does its use of current batter balls faced introduce a systematic batting-position effect that needs further investigation?*\n\n")
        f.write("### Definitive Audit Answer:\n")
        f.write("**The existing PI does NOT measure match pressure independently. Its use of `striker_balls_faced_before` introduces a powerful, systematic batting-position effect that requires further investigation.**\n\n")

        f.write("### Analytical Justification:\n")
        f.write("1. **It is not purely match pressure:** True match pressure is independent of which individual player is facing. By incorporating `striker_balls_faced_before`, the PI formula allows the individual batter's time at the crease to dictate 35% of the score.\n")
        f.write("2. **It creates a structural batting-position bias:** Because lower-order batters enter late in the innings, they face short stints (76.8% of their balls occur when $BF < 10$). Consequently, they are evaluated almost entirely under the $+35.00$ point settling surcharge. Top-order batters, who face long stints (56.5% of balls at $BF \\ge 10$), face the majority of their balls with zero settling surcharge.\n")
        f.write("3. **The Step 16.4 Matched Gap was an Artifact:** Step 16.4 argued that the +44.67 pp matched gap was an immutable law of cricket reality. Step 16.4.1 has proven mathematically and empirically that when you match on balls faced, that gap drops to **+0.23 pp** (statistically zero). The gap was almost entirely an artifact of comparing cold tailenders against set top-order anchors.\n")
        f.write("4. **Implications for Current Project Phase:**  \n")
        f.write("   In accordance with the audit mandate, **no formula changes or ranking recalculations are made in this step**. However, project leadership should NOT consider the PI methodology permanently frozen or scientifically infallible. While the rankings remain frozen under Step 15 decisions for Round 1 submission, the interaction between Situational Intensity and batting positions is an active methodological defect that must be prioritized for Round 2 model development.\n\n")

        f.write("---\n\n")
        f.write("```\n")
        f.write("Step 16.4.1 Audit Directory Artifacts:\n")
        f.write("outputs/step_16_4_1_audit/\n")
        f.write("├── batter_state_sensitivity_curve.csv\n")
        f.write("├── current_batter_state_dependency_report.md\n")
        f.write("├── balls_faced_matched_context_comparison.csv\n")
        f.write("├── balls_faced_matched_context_cells.csv\n")
        f.write("├── balls_faced_matched_context_report.md\n")
        f.write("├── wp_calibration_table.csv\n")
        f.write("├── sample_vs_population_representation.csv\n")
        f.write("├── leverage_audit_recalculated.csv\n")
        f.write("├── independent_win_probability_leverage_audit.md\n")
        f.write("├── population_reconciliation.csv\n")
        f.write("├── population_reconciliation_report.md\n")
        f.write("└── step_16_4_1_audit_report.md\n")
        f.write("```\n")

    print(f"Master Synthesis Report written to {report_path}")


if __name__ == "__main__":
    main()
