# Step 14.2 — Module 4: Ranking Impact & Evaluation Report

**Module:** Step 14.2 — Experimental Workload Formula Implementation and Impact Analysis  
**Date:** November 13, 2026  
**Audit Artifact:** [02_ranking_impact_and_shifts.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_14_2_workload_experiment/02_ranking_impact_and_shifts.png)
**Comparison Dataset:** [exp14_2_ranking_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_14_2_workload_experiment/exp14_2_ranking_comparison.csv)

---

## 1. Executive Summary

This report evaluates the full-population ranking impact of replacing current-spell workload with cumulative innings workload across all **816 batters** and **589 bowlers**.

### Key Findings:
1. **Batting Invariance Confirmed:** Batting rankings are **100% mathematically and empirically invariant** ($r = 1.0000, \rho = 1.0000$, 0 batters with score deltas). The 12-factor Pressure Index strictly isolates bowler workload inside $I_{\text{bowler}}$, which enters only the 6 bowling sub-formulas (`PI_BO`). `Batting_PI` does not depend on bowler workload.
2. **Moderate Bowling Global Correlation:** Across all 589 bowlers:
   - Score Pearson Correlation: **$r = 0.7884$**
   - Overall Rank Spearman Correlation: **$\rho = 0.7167$**
   - This indicates that changing bowler workload from spell-based to innings-based is **not a minor perturbation**, but a structural intervention that alters bowling reliability scores and ranks substantially across the population.
3. **Tier 1 Qualified Population Shifts:**
   - Baseline Tier 1 Qualifiers: **130 bowlers**
   - Experimental Tier 1 Qualifiers: **119 bowlers** (Net change: -11 bowlers)
   - **115 bowlers** remained in Tier 1 across both models (88.5% stability).
   - **4 bowlers entered Tier 1:** Matthew Humphreys, etc. (whose death overs balls were elevated into high pressure).
   - **15 bowlers exited Tier 1:** Including Nasum Ahmed (55 -> 44 balls), Junaid Siddique (50 -> 45 balls), Shoriful Islam (61 -> 49 balls), and Simarjeet Singh (60 -> 44 balls) who relied heavily on Powerplay spell balls where pressure dropped below 60.0.
4. **Top 10 Bowlers Roster Stability:**
   - **Top 10 Overlap:** **5 out of 10 bowlers retained (50.0% overlap, Jaccard = 0.333)**.
   - **Entrants to Top 10:** Azmatullah Omarzai, Jofra Archer, Matthew Humphreys, Mukesh Choudhary, Ravichandran Ashwin.
   - **Exits from Top 10:** Junaid Siddique, Nasum Ahmed, Shoriful Islam, Trent Boult, Wanindu Hasaranga.

---

## 2. Top 10 Bowlers Comparison Table

| Exp Rank | Player Name | Exp BoRS | Base Rank | Base BoRS | Score Delta | High Balls (Base -> Exp) | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Tim Southee** | 92.97 | 1 | 90.69 | +2.28 | 64 -> 73 | Retained Top 10 |
| **2** | **Mark Adair** | 86.66 | 6 | 74.70 | +11.96 | 71 -> 62 | Retained Top 10 |
| **3** | **Keshav Maharaj** | 77.91 | 3 | 79.94 | -2.03 | 78 -> 64 | Retained Top 10 |
| **4** | **Mukesh Choudhary** | 76.64 | 22 | 61.26 | +15.38 | 88 -> 81 | **New Entrant** |
| **5** | **Haris Rauf** | 75.38 | 4 | 78.84 | -3.46 | 106 -> 94 | Retained Top 10 |
| **6** | **Ravichandran Ashwin** | 74.63 | 18 | 62.40 | +12.22 | 130 -> 123 | **New Entrant** |
| **7** | **Harshit Rana** | 74.29 | 8 | 72.85 | +1.44 | 158 -> 149 | Retained Top 10 |
| **8** | **Matthew Humphreys** | 74.25 | T2 / Unranked | 48.12 | +26.14 | 41 -> 52 | **New Entrant** |
| **9** | **Jofra Archer** | 68.08 | 51 | 55.09 | +12.99 | 259 -> 246 | **New Entrant** |
| **10** | **Azmatullah Omarzai** | 67.92 | 29 | 59.09 | +8.84 | 122 -> 96 | **New Entrant** |

---

## 3. Largest Movers Among Tier 1 Bowlers

| Player Name | Baseline Rank | Exp Rank | Rank Delta | BoRS Base | BoRS Exp | High Balls Base $\to$ Exp | Explanatory Factor |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Yash Dayal** | 111 | 19 | **+92** | 38.81 | 62.61 | 110 $\to$ 119 | Death-over overs reclassified as high pressure; wickets under pressure jumped from 5 to 9. |
| **Shadab Khan** | 116 | 28 | **+88** | 35.99 | 59.47 | 67 $\to$ 60 | Middle-over spell workload rebalancing improved economy relative to pressure prior. |
| **Krunal Pandya** | 81 | 15 | **+66** | 46.13 | 63.28 | 154 $\to$ 128 | Middle-over containment under cumulative workload rewarded. |
| **Noor Ahmad** | 82 | 17 | **+65** | 46.09 | 62.89 | 177 $\to$ 161 | Middle overs wrist-spin economy under cumulative workload elevated BoRS. |
| **Reece Topley** | 30 | 95 | **-65** | 59.05 | 39.54 | 73 $\to$ 91 | Death overs additions with high runs conceded degraded high economy. |
| **Mohit Sharma** | 17 | 84 | **-67** | 63.58 | 44.82 | 79 $\to$ 66 | Death specialist losing clean low-scoring death overs; high economy rose from 7.52 to 9.73. |
| **Trent Boult** | 10 | 38 | **-28** | 69.72 | 57.12 | 180 $\to$ 194 | Powerplay balls deflated, death balls inflated; high economy jumped from 7.50 to 8.32. |
| **Wanindu Hasaranga** | 9 | 27 | **-18** | 70.04 | 59.75 | 198 $\to$ 155 | High pressure middle-overs sample reduced; score differential dropped. |
| **Simarjeet Singh** | 11 | Exit (T2) | **Disqualified** | 69.40 | 48.57 | 60 $\to$ 44 | Powerplay deflation dropped high balls from 60 to 44 (below Rule B threshold). |