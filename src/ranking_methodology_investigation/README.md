# Ranking Methodology Investigation (Step 11)

This module contains the investigative framework and analytical scripts developed for **Step 11 — Deep Ranking Methodology Investigation**.

## 1. Objective

The objective of Step 11 is an adversarial, data-driven audit of the **official v2.0 player reliability ranking methodology** (implemented in Step 6.2 and audited in Step 7–10). Specifically, this investigation determines whether the current mathematical formulas, Bayesian shrinkage parameters, normalization bounds, and tier thresholds genuinely measure player reliability under pressure, or whether they introduce structural biases and distortions.

In strict compliance with project safety rules:
- **No official formulas, production code, or datasets were modified.**
- All investigation scripts are isolated in `src/ranking_methodology_investigation/`.
- All generated reports, CSVs, and visualization charts are stored in `outputs/ranking_methodology_investigation/`.

---

## 2. Directory Structure & Script Inventory

```
src/ranking_methodology_investigation/
├── inv01_bumrah_balance.py       # Investigation 1: Bumrah suppression & bowling metric balance
├── inv02_sample_threshold.py     # Investigation 2: 60-ball sample threshold & cutoff sensitivity
├── inv03_bayesian_shrinkage.py   # Investigation 3: Bayesian shrinkage K=50 & prior representativeness
├── inv04_batting_metrics.py      # Investigation 4: Batting metric collinearity & variance decomposition
├── inv05_bowling_metrics.py      # Investigation 5: Bowling metric tradeoffs (containment vs strike)
├── inv06_phase_specialization.py # Investigation 6: Phase exposure confounding & MS Dhoni reconciliation
├── inv07_match_consistency.py    # Investigation 7: Match-level volatility & outlier dependency
├── inv08_target_sensitivity.py   # Investigation 8: Target reconstruction sensitivity (38 flagged matches)
├── inv09_ranking_robustness.py   # Investigation 9: One-at-a-time controlled sensitivity experiments
├── run_all_investigations.py     # Master runner validating execution and output integrity
└── README.md                     # This documentation file
```

---

## 3. Investigation Summaries & Key Findings

| # | Investigation Name | Script | Key Quantitative Finding | Output Artifacts |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Bumrah Bowling Balance** | `inv01_bumrah_balance.py` | Bumrah ranks #24 (BoRS 59.29). Despite elite economy (6.93 rpo, score 76.38), his 2.98% wicket rate yields a score of 25.31 out of 100, creating an insurmountable 6.19 pt drag vs #10 Ngidi. | `bumrah_component_comparison.csv`<br>`01_bumrah_vs_top10_components.png`<br>`bumrah_bowling_investigation.md` |
| **2** | **Minimum Sample Threshold** | `inv02_sample_threshold.py` | The 60-ball threshold excludes 85.8% of batters and 80.8% of bowlers. Creates a steep cliff where Jamie Overton (59 balls, BRS 79.54, potential #6) and Nasum Ahmed (55 balls, BoRS 88.84, potential #2) are excluded. | `sample_threshold_analysis.csv`<br>`02_sample_threshold_distributions.png`<br>`sample_threshold_investigation.md` |
| **3** | **Bayesian Shrinkage & K=50** | `inv03_bayesian_shrinkage.py` | Global priors include tail-enders and part-timers, pulling qualified regulars downward. Theoretical optimal prior weights are $K_{\text{bat}} \approx 38.2$ and $K_{\text{bow}} \approx 29.0$. While K=50 is slightly conservative, rank correlation across $K \in [20, 100]$ exceeds 0.98. | `bayesian_shrinkage_variations.csv`<br>`03_bayesian_shrinkage_k_curves.png`<br>`bayesian_shrinkage_investigation.md` |
| **4** | **Batting Metric Balance** | `inv04_batting_metrics.py` | Strike Rate and Boundary Execution correlate at $r = 0.9628$. Scoring speed commanding 68.07% of effective BRS variance, severely marginalizing Survival (effective variance 19.80% vs nominal 25%). | `batting_metric_distributions.csv`<br>`04_batting_metric_correlations.png`<br>`batting_metric_investigation.md` |
| **5** | **Bowling Metric Balance** | `inv05_bowling_metrics.py` | Variance contributions match nominal weights well (Econ 39.9%, Wk 23.1%, Dot 21.8%, Diff 15.2%). However, wide wicket score spread (std 18.9) penalizes pure containment bowlers who induce wickets at the other end. | `bowling_metric_distributions.csv`<br>`05_bowling_metric_tradeoffs.png`<br>`bowling_metric_investigation.md` |
| **6** | **Phase Specialization & Dhoni** | `inv06_phase_specialization.py` | **Dhoni Mystery Resolved:** In Middle Overs, Dhoni ranks #86 (SR 65.79); in Death Overs, he ranks #2 (SR 197.37). 78.4% of his high-pressure balls were in Death Overs, inflating his overall SR to 170.62 (#1 overall). Model lacks phase normalization. | `phase_specialization_analysis.csv`<br>`06_phase_specialist_vs_overall.png`<br>`phase_specialization_investigation.md` |
| **7** | **Match-to-Match Consistency** | `inv07_match_consistency.py` | High rankings hide outlier-dependent players. Over 53.1% of Shubham Dubey's (#4 batter) runs and 75.0% of Simarjeet Singh's (#9 bowler) wickets came from just two matches. | `match_consistency_metrics.csv`<br>`07_match_to_match_consistency.png`<br>`match_consistency_investigation.md` |
| **8** | **Target Sensitivity** | `inv08_target_sensitivity.py` | Excluding the 4,177 flagged deliveries from 38 matches yields Spearman $\rho = 0.9945$ (batters) and $0.9852$ (bowlers). Shoriful Islam fell from #5 to Tier 2 because 4 flagged balls dropped him below the 60-ball cliff. | `target_sensitivity_impact.csv`<br>`08_target_sensitivity_distribution.png`<br>`target_sensitivity_investigation.md` |
| **9** | **Overall Ranking Robustness** | `inv09_ranking_robustness.py` | Model is highly robust to weight adjustments ($\rho \ge 0.985$ batters, $\ge 0.965$ bowlers) and K adjustments ($\rho \ge 0.98$). The primary fragility is the qualification cutoff. Removing collinear Boundary Execution preserves ranking with $\rho = 0.9961$. | `ranking_robustness_experiments.csv`<br>`09_ranking_robustness_sensitivity.png`<br>`ranking_robustness_investigation.md` |

---

## 4. Execution & Reproduction

To reproduce all 9 investigations and verify all generated artifacts:

```powershell
python src/ranking_methodology_investigation/run_all_investigations.py
```

All 9 publication-grade charts are rendered at 300 DPI into `outputs/ranking_methodology_investigation/`.
The comprehensive evaluation synthesis answering all 12 mandatory questions is located in:
`outputs/ranking_methodology_investigation/step_11_final_report.md`.
