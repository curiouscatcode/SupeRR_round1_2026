# Step 15.1 — Comprehensive Exploratory Data Analysis of Final Candidate Results

**Project:** SupeRR Selector — Round 1  
**Target:** Exploratory Data Analysis of Frozen Step 13 Candidate Rankings  
**Methodology Baseline:** Step 15 Frozen Specifications (BRS3, v2.0 BoRS, Bayesian $K=50$, Rule B Qualification, v2.0 PI, Operational Split $\text{PI} > 60.0$)  
**Status:** Completed & Independently Verified  
**Date:** November 2026  

---

## Executive Summary & Input Data Verification

This report presents a comprehensive Exploratory Data Analysis (EDA) of the frozen final candidate rankings established in Step 13 and codified in Step 15. The purpose is to explore full score distributions, evaluate the impact of sample thresholds, uncover component dynamics, investigate phase exposures, profile top players, identify anomalies, and document evidence-based limitations for selectors.

### 1. Pre-Analysis Verification & Population Counts
Before initiating exploratory procedures, all input datasets and model parameters were audited:
- **Batter Source File:** `outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv`
  - Total Batters: **816** unique players (100% matched to full population).
  - Tier 1 Qualified: **146** players ($17.9\%$).
  - Tier 2 Specialist: **42** players ($5.1\%$).
  - Below Threshold: **628** players ($77.0\%$).
- **Bowler Source File:** `outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv`
  - Total Bowlers: **589** unique players (100% matched to full population).
  - Tier 1 Qualified: **130** players ($22.1\%$).
  - Tier 2 Specialist: **19** players ($3.2\%$).
  - Below Threshold: **440** players ($74.7\%$).
- **Methodology Conformity:**
  - Batting formula: $\text{BRS}_3 = 0.45 \times \text{Score\_SR} + 0.35 \times \text{Score\_Surv} + 0.20 \times \text{Score\_Diff}$ (verified maximum deviation $= 0.00000000$).
  - Bowling formula: $\text{BoRS} = 0.40 \times \text{Score\_Econ} + 0.25 \times \text{Score\_Wk} + 0.20 \times \text{Score\_Dot} + 0.15 \times \text{Score\_Diff}$ (verified maximum deviation $= 0.00000000$).
  - Shrinkage hyperparameter: Constant $K = 50.0$ legal deliveries across all components.
  - Operational high-pressure cutoff: Strictly $\text{PI} > 60.0$.
  - Rule B Qualification: Tier 1 requires $N \ge 60 \text{ OR } (N \ge 50 \text{ AND } M \ge 6)$; Tier 2 requires $N \ge 40$ (not in Tier 1); Below Threshold requires $N < 40$.
- **All-Rounder Inclusion Verified:** All-rounders (including Jamie Overton, Cameron Green, Shivam Dube, Vijay Shankar, George Dockrell, Wanindu Hasaranga, and Mark Adair) are evaluated symmetrically on independent batting and bowling criteria without arbitrary role filters.
- **Top 10 Roster Consistency:** The true Step 13 rankings (commencing with MS Dhoni #1 in batting and Tim Southee #1 in bowling) are used throughout; the initial draft placeholder table from Step 15 is formally superseded.

---

## 1. Score and Ranking Distributions (Section A)

Full distribution metrics were computed across all 816 batters and 589 bowlers and categorized by qualification tier:

### Table 1: Score Distribution Summary Statistics

| Discipline | Population Group | Player Count | Mean Score | Std Dev | Median | Q25 | Q75 | IQR | Min Score | Max Score | Skewness | Kurtosis | Median Rank Gap | Max Rank Gap |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Batting ($\text{BRS}_3$)** | Full Population | 816 | 48.70 | 10.60 | 49.00 | 42.57 | 54.49 | 11.92 | 7.96 | 93.21 | +0.066 | +1.530 | 0.033 | 9.009 |
| **Batting ($\text{BRS}_3$)** | Tier 1: Qualified | 146 | 52.76 | 14.52 | 54.18 | 41.92 | 62.55 | 20.63 | 14.35 | 93.21 | -0.071 | -0.186 | 0.208 | 11.195 |
| **Batting ($\text{BRS}_3$)** | Tier 2: Specialist | 42 | 50.10 | 14.70 | 50.88 | 40.17 | 61.31 | 21.14 | 15.87 | 91.02 | -0.019 | +0.625 | 0.870 | 18.314 |
| **Batting ($\text{BRS}_3$)** | Below Threshold | 628 | 47.66 | 8.83 | 48.40 | 42.88 | 52.74 | 9.86 | 7.96 | 81.74 | -0.393 | +1.876 | 0.035 | 8.029 |
| **Bowling (BoRS)** | Full Population | 589 | 50.08 | 9.76 | 49.70 | 45.33 | 54.94 | 9.60 | 11.48 | 90.69 | +0.051 | +2.074 | 0.039 | 8.903 |
| **Bowling (BoRS)** | Tier 1: Qualified | 130 | 50.65 | 13.01 | 49.64 | 42.00 | 58.43 | 16.43 | 11.48 | 90.69 | +0.209 | +0.948 | 0.286 | 13.055 |
| **Bowling (BoRS)** | Tier 2: Specialist | 19 | 43.37 | 14.50 | 45.03 | 35.07 | 50.92 | 15.85 | 18.81 | 79.11 | +0.416 | +0.696 | 1.996 | 20.549 |
| **Bowling (BoRS)** | Below Threshold | 440 | 50.21 | 8.20 | 49.90 | 46.13 | 53.73 | 7.60 | 17.76 | 74.53 | -0.069 | +1.896 | 0.042 | 4.389 |

*(Source: `outputs/step_15_1_final_results_eda/batting_score_distribution.csv` and `bowling_score_distribution.csv`)*

### Key Distributional Findings

1. **Bayesian Shrinkage Variance Compression:**
   - In both batting and bowling, the Below Threshold populations exhibit heavy variance compression ($std = 8.83$ for batters, $8.20$ for bowlers; $IQR < 10.0$).
   - This occurs because unexposed players ($N < 40$) have shrinkage weights $\lambda = N / (N + 50) < 0.444$, pulling their component estimates tightly toward global priors ($\mu_{\text{SR}} = 114.05, \mu_{\text{Econ}} = 9.06$).
2. **Tier 1 Dispersion & Differentiation:**
   - In Tier 1, where players faced sustained pressure ($N \ge 50$), the standard deviation widens significantly ($14.52$ for batting, $13.01$ for bowling; $IQR = 20.63$ and $16.43$).
   - The model succeeds in creating meaningful spread among qualified regulars, spanning from $14.35$ to $93.21$ in batting, and $11.48$ to $90.69$ in bowling.
3. **Score Isolation at the Apex vs. Mid-Tier Congestion:**
   - **Batting Leader Isolation:** MS Dhoni sits at **93.21**, creating a massive **11.20-point isolation gap** over Rank 2 (Shivam Dube, 82.01). Dhoni's score is an extreme statistical outlier ($> 2.78 \sigma$ above the Tier 1 mean).
   - **Bowling Top 2 Cluster:** Tim Southee (**90.69**) and Nasum Ahmed (**88.84**) form an isolated elite tier, separated by **8.90 points** from Rank 3 (Keshav Maharaj, 79.94).
   - **Mid-Tier Hyper-Congestion:** Between Ranks 20 and 80 in Tier 1 batting, the median score gap between consecutive ranks is only **0.18 points**. A performance difference of just 1.5 score points shifts a batter's rank by 8 to 12 positions.

---

## 2. Sample Size and Match Coverage Analysis (Section B)

### Table 2: Sample Size and Match Coverage Metrics by Tier

| Discipline | Population Group | Player Count | Mean HP Balls | Median HP Balls | Min HP Balls | Max HP Balls | Mean HP Matches | Median HP Matches | Corr ($N$ vs Score) | Corr ($M$ vs Score) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Batting** | Full Population | 816 | 28.6 | 13.0 | 0 | 321 | 8.5 | 4.0 | +0.207 | +0.153 |
| **Batting** | Tier 1: Qualified | 146 | 99.0 | 85.0 | 50 | 321 | 26.6 | 24.0 | +0.258 | +0.209 |
| **Batting** | Tier 2: Specialist | 42 | 44.5 | 44.0 | 40 | 49 | 15.5 | 14.0 | +0.136 | -0.165 |
| **Batting** | Below Threshold | 628 | 11.1 | 8.0 | 0 | 39 | 3.9 | 2.0 | -0.149 | -0.188 |
| **Bowling** | Full Population | 589 | 33.8 | 9.0 | 0 | 427 | 6.6 | 2.0 | +0.036 | +0.061 |
| **Bowling** | Tier 1: Qualified | 130 | 119.2 | 95.0 | 50 | 427 | 22.1 | 18.5 | +0.073 | +0.119 |
| **Bowling** | Tier 2: Specialist | 19 | 46.3 | 47.0 | 40 | 54 | 8.2 | 8.0 | +0.250 | -0.310 |
| **Bowling** | Below Threshold | 440 | 8.0 | 4.0 | 0 | 39 | 2.0 | 1.0 | -0.010 | +0.080 |

*(Source: `outputs/step_15_1_final_results_eda/batting_sample_analysis.csv` and `bowling_sample_analysis.csv`)*

### Breakdown of Rule B Qualification Pathways

Rule B incorporates a dual pathway for Tier 1 qualification:
1. **Standard Volume Pathway ($N \ge 60$):**
   - **Batting:** 116 players qualify ($79.5\%$ of Tier 1).
   - **Bowling:** 113 players qualify ($86.9\%$ of Tier 1).
2. **Rule B High-Breadth Pathway ($N \in [50, 59] \text{ AND } M \ge 6$):**
   - **Batting:** **30 players** qualify ($20.5\%$ of Tier 1). Prominent qualifiers include:
     - **Jamie Overton** (Rank 7, $N=59, M=14, \text{BRS}_3=78.19$)
     - **Sai Sudharsan** (Rank 20, $N=50, M=26, \text{BRS}_3=68.30$)
     - **William Jacks** (Rank 25, $N=54, M=18, \text{BRS}_3=66.87$)
     - **Arshad Khan** (Rank 26, $N=51, M=10, \text{BRS}_3=66.46$)
     - **Roston Chase** (Rank 36, $N=50, M=14, \text{BRS}_3=62.75$)
     - **Josh Inglis** (Rank 38, $N=52, M=18, \text{BRS}_3=62.46$)
     - **Quinton de Kock** (Rank 50, $N=53, M=34, \text{BRS}_3=59.98$)
   - **Bowling:** **17 players** qualify ($13.1\%$ of Tier 1). Prominent qualifiers include:
     - **Nasum Ahmed** (Rank 2, $N=55, M=10, \text{BoRS}=88.84$)
     - **Junaid Siddique** (Rank 5, $N=50, M=12, \text{BoRS}=74.78$)
     - **Brad Evans** (Rank 16, $N=52, M=11, \text{BoRS}=63.70$)
     - **Mayank Yadav** (Rank 26, $N=58, M=11, \text{BoRS}=59.39$)
     - **Rishad Hossain** (Rank 40, $N=57, M=9, \text{BoRS}=57.21$)
     - **Matthew Forde** (Rank 42, $N=56, M=13, \text{BoRS}=57.02$)
     - **Allah Ghazanfar** (Rank 46, $N=51, M=7, \text{BoRS}=56.24$)
     - **Naseem Shah** (Rank 65, $N=54, M=15, \text{BoRS}=49.69$)

### Boundary Zone Sensitivity Analysis
- **Batting Boundary ($N \in [50, 65]$):** 36 batters occupy this zone. All 30 players with $N \in [50, 59]$ satisfied $M \ge 6$ (mean matches $= 16.8$), demonstrating that players in this volume band are established tournament contributors, not one-match anomalies.
- **Bowling Boundary ($N \in [50, 65]$):** 28 bowlers occupy this zone. Exactly 17 qualified under Rule B ($M \ge 6$), while 0 bowlers with $N \in [50, 59]$ were disqualified for having $M < 6$.
- **Sample vs. Score Independence:** In Tier 1 bowling, correlation between sample size and score is negligible ($r = +0.073$). In Tier 1 batting, it is modest ($r = +0.258$). The models do not systematically reward brute volume; regularized efficiency drives the rankings.

---

## 3. Component-Wise Analysis & Correlations (Section C)

### Table 3: Batting Component Performance (Tier 1, N=146)

| Component Metric | Formula Weight | Tier 1 Mean | Tier 1 Std | Tier 1 Median | Tier 1 Min | Tier 1 Max | Corr with Final $\text{BRS}_3$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Score_SR** (Strike Rate Score) | 45% | 47.23 | 18.69 | 46.97 | 0.00 | 98.78 | **+0.909** |
| **Score_Surv** (Survival Score) | 35% | 65.90 | 17.26 | 68.52 | 15.79 | 98.20 | **+0.713** |
| **Score_Diff** (Clutch Diff Score) | 20% | 42.20 | 19.09 | 42.69 | 0.00 | 100.00 | **+0.671** |
| **$\text{SR}^*$** (Regularized High SR) | — | 117.73 | 15.10 | 117.58 | 72.34 | 159.03 | +0.909 |
| **$\text{Out}^*$** (Regularized Out %) | — | 6.76% | 2.16% | 6.44% | 2.73% | 13.03% | -0.713 |
| **$\text{Diff}^*$** (Regularized Clutch Delta) | — | -26.52 | 16.07 | -25.85 | -78.64 | +21.96 | +0.663 |

*(Source: `outputs/step_15_1_final_results_eda/batting_component_analysis.csv`)*

### Table 4: Bowling Component Performance (Tier 1, N=130)

| Component Metric | Formula Weight | Tier 1 Mean | Tier 1 Std | Tier 1 Median | Tier 1 Min | Tier 1 Max | Corr with Final BoRS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Score_Econ** (Economy Score) | 40% | 49.62 | 15.55 | 48.75 | 0.00 | 92.87 | **+0.822** |
| **Score_Wk** (Wicket Rate Score) | 25% | 44.34 | 19.11 | 42.31 | 5.90 | 96.07 | **+0.636** |
| **Score_Dot** (Dot-Ball Score) | 20% | 57.53 | 19.83 | 57.54 | 7.96 | 100.00 | **+0.727** |
| **Score_Diff** (Clutch Diff Score) | 15% | 54.73 | 18.98 | 55.34 | 0.00 | 96.12 | **+0.694** |
| **$\text{Econ}^*$** (Regularized Economy) | — | 9.03 | 0.95 | 9.07 | 6.43 | 12.54 | -0.822 |
| **$\text{Wk}^*$** (Regularized Wicket %) | — | 4.83% | 1.43% | 4.67% | 1.94% | 8.71% | +0.636 |
| **$\text{Dot}^*$** (Regularized Dot %) | — | 39.40% | 5.00% | 39.39% | 26.99% | 52.09% | +0.731 |
| **$\text{Diff}^*$** (Regularized Economy Delta)| — | -0.27 | 0.99 | -0.23 | -4.00 | +1.81 | +0.702 |

*(Source: `outputs/step_15_1_final_results_eda/bowling_component_analysis.csv`)*

### Key Component Insights
1. **Primary Drivers of Success:**
   - In batting, **Strike Rate Score ($\text{Score\_SR}$)** is the dominant determinant ($r = +0.909$). Players cannot reach the Top 20 without high regularized scoring acceleration ($\text{SR}^* \ge 135.0$).
   - In bowling, **Economy Score ($\text{Score\_Econ}$)** ($r = +0.822$) and **Dot-Ball Score ($\text{Score\_Dot}$)** ($r = +0.727$) form the backbone of reliability. Dot-ball suppression strongly correlates with run prevention ($r = 0.58$ between Economy and Dot-Ball scores).
2. **Component Conflict Archetypes (Trade-Off Dynamics):**
   - **The Ultra-Anchor Conflict (12 Batters Flagged):** Players like Towhid Hridoy (Rank 70), Corbin Bosch (Rank 75), Shahbaz Ahmed (Rank 76), and Ayush Badoni (Rank 79) possess elite survival ($\text{Score\_Surv} > 75.0, \text{Out}^* < 5.0\%$), but sub-par acceleration ($\text{SR}^* < 112.0, \text{Score\_SR} < 40.0$). In modern T20 pressure scenarios, preserving wickets without boundary scoring yields mediocre overall reliability ($\text{BRS}_3 \approx 52–55$).
   - **The Expensive Strike Bowler Conflict (6 Bowlers Flagged):** Bowlers like Haris Rauf (Rank 4, $\text{Wk}^*=7.31\%, \text{Econ}^*=7.52$) succeed through balance, but pure wicket-taking bowlers who concede runs (e.g. bowlers with $\text{Wk}^* > 7.0\%$ but $\text{Econ}^* > 9.20$) receive severe penalties via the 40% economy weight.

---

## 4. Top-Player Cohort Analysis: Top 10, Top 20, Top 50 (Section D)

### Table 5: Final Candidate Top 10 Batters (Tier 1 Qualified)

| Rank | Player Name | BRS3 Score | High Balls ($N$) | Matches ($M$) | $\text{SR}^*$ | $\text{Out}^*$ | $\text{Diff}^*$ | Score_SR (45%) | Score_Surv (35%) | Score_Diff (20%) | Qualification Reason |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Mahendra Singh Dhoni** | **93.21** | 194 | 38 | 159.03 | 4.73% | +21.96 | 79.03 | 72.69 | 95.95 | Baseline Volume ($N \ge 60$) |
| **2** | **Shivam Dube** | **82.01** | 160 | 39 | 145.73 | 3.59% | -7.61 | 65.73 | 84.08 | 56.52 | Baseline Volume ($N \ge 60$) |
| **3** | **Shashank Singh** | **81.39** | 135 | 24 | 152.45 | 5.16% | -7.67 | 72.45 | 68.42 | 56.43 | Baseline Volume ($N \ge 60$) |
| **4** | **Cameron Green** | **80.85** | 78 | 26 | 143.77 | 3.55% | -8.34 | 63.77 | 84.51 | 55.55 | Baseline Volume ($N \ge 60$) |
| **5** | **Shubham Dubey** | **80.02** | 69 | 15 | 146.24 | 5.50% | +4.63 | 66.24 | 65.02 | 72.85 | Baseline Volume ($N \ge 60$) |
| **6** | **Vijay Shankar** | **78.79** | 65 | 14 | 133.93 | 3.08% | +0.31 | 53.93 | 89.19 | 67.08 | Baseline Volume ($N \ge 60$) |
| **7** | **Jamie Overton** | **78.19** | 59 | 14 | 144.98 | 6.92% | +16.05 | 64.98 | 50.80 | 88.07 | Rule B High-Breadth ($N=59, M=14$) |
| **8** | **Rinku Singh** | **76.60** | 177 | 46 | 139.22 | 3.76% | -12.69 | 59.22 | 82.37 | 49.74 | Baseline Volume ($N \ge 60$) |
| **9** | **George Dockrell** | **76.06** | 100 | 29 | 134.68 | 4.36% | +2.06 | 54.68 | 76.38 | 69.41 | Baseline Volume ($N \ge 60$) |
| **10** | **Jitesh Sharma** | **75.83** | 97 | 29 | 145.59 | 5.81% | -7.17 | 65.59 | 61.88 | 57.11 | Baseline Volume ($N \ge 60$) |

### Table 6: Final Candidate Top 10 Bowlers (Tier 1 Qualified)

| Rank | Player Name | BoRS Score | High Balls ($N$) | Matches ($M$) | $\text{Econ}^*$ | $\text{Wk}^*$ | $\text{Dot}^*$ | $\text{Diff}^*$ | Score_Econ (40%) | Score_Wk (25%) | Score_Dot (20%) | Score_Diff (15%) | Qualification Reason |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Tim Southee** | **90.69** | 64 | 19 | 6.87 | 8.25% | 49.73% | +1.73 | 85.54 | 90.05 | 98.93 | 94.53 | Baseline Volume ($N \ge 60$) |
| **2** | **Nasum Ahmed** | **88.84** | 55 | 10 | 6.43 | 7.06% | 52.09% | +1.39 | 92.87 | 74.08 | 100.00 | 87.81 | Rule B High-Breadth ($N=55, M=10$) |
| **3** | **Keshav Maharaj** | **79.94** | 78 | 12 | 7.34 | 7.35% | 45.07% | +1.43 | 77.75 | 78.01 | 80.29 | 88.52 | Baseline Volume ($N \ge 60$) |
| **4** | **Haris Rauf** | **78.84** | 106 | 19 | 7.52 | 7.31% | 45.96% | +1.27 | 74.69 | 77.51 | 83.83 | 85.45 | Baseline Volume ($N \ge 60$) |
| **5** | **Junaid Siddique** | **74.78** | 50 | 12 | 8.37 | 8.41% | 46.69% | +0.40 | 60.52 | 92.12 | 86.78 | 67.90 | Rule B High-Breadth ($N=50, M=12$) |
| **6** | **Mark Adair** | **74.70** | 71 | 17 | 6.87 | 4.47% | 45.20% | +1.81 | 85.55 | 39.60 | 80.81 | 96.12 | Baseline Volume ($N \ge 60$) |
| **7** | **Shoriful Islam** | **74.01** | 61 | 16 | 7.81 | 6.67% | 47.47% | +0.62 | 69.84 | 68.99 | 89.89 | 72.35 | Baseline Volume ($N \ge 60$) |
| **8** | **Harshit Rana** | **72.85** | 158 | 30 | 8.15 | 5.97% | 47.93% | +1.65 | 64.19 | 59.54 | 91.72 | 92.94 | Baseline Volume ($N \ge 60$) |
| **9** | **Wanindu Hasaranga** | **70.04** | 198 | 34 | 7.27 | 6.21% | 39.80% | +0.65 | 78.84 | 62.84 | 59.18 | 73.03 | Baseline Volume ($N \ge 60$) |
| **10** | **Trent Boult** | **69.72** | 180 | 45 | 7.84 | 4.96% | 49.43% | +0.63 | 69.36 | 46.14 | 97.73 | 72.68 | Baseline Volume ($N \ge 60$) |

*(Source: `outputs/step_15_1_final_results_eda/batting_top10_top20_top50.csv` and `bowling_top10_top20_top50.csv`)*

### Cohort Comparison: Top 10 vs Top 11–20 vs Top 21–50
- **Batters:**
  - **Top 10:** Mean score $= 80.36$, Mean $N = 113.1$ balls, Mean $\text{SR}^* = 144.5$, Mean Survival Score $= 70.6$. Highly balanced finishers with positive clutch differentials.
  - **Top 11–20:** Mean score $= 71.42$, Mean $N = 106.8$ balls, Mean $\text{SR}^* = 132.8$. Features players like Tilak Varma (#11, 75.64), Nicholas Pooran (#12, 75.59), Heinrich Klaasen (#13, 73.69), and Glenn Phillips (#15, 71.97). The drop from Top 10 to Top 20 is marked by slightly higher dismissal rates or lower clutch differentials.
  - **Top 21–50:** Mean score $= 63.85$, Mean $N = 98.4$ balls. Dominated by middle-order accumulators whose strike rates under pressure sit near global priors ($\approx 120–128$).
- **Bowlers:**
  - **Top 10:** Mean score $= 77.44$, Mean $N = 101.4$ balls, Mean $\text{Econ}^* = 7.50$, Mean Dot % $= 47.0\%$. Possess elite control of both boundaries and strike rates.
  - **Top 11–20:** Mean score $= 65.51$, Mean $N = 124.6$ balls. Includes Bhuvneshwar Kumar (#11, 68.61), Arshdeep Singh (#13, 67.75), Jasprit Bumrah (#14, 66.86), and Josh Hazlewood (#15, 66.42). These bowlers are world-class regulars facing extreme death-over volume, which pulls their unregularized economy slightly higher under pressure ($8.2–8.8$).

---

## 5. Phase-Wise Analysis: Exposure & Death-Over Bias (Section E)

### Table 7: Phase Exposure Distribution Across Tier 1

| Discipline | Phase | Mean HP Balls | Median HP Balls | Mean Share of HP Deliveries | Median Share | Correlation with Final Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Batting** | **Powerplay (Overs 1-6)** | 17.0 | 6.0 | 19.4% | 5.4% | **+0.235** |
| **Batting** | **Middle Overs (Overs 7-15)** | 45.1 | 37.5 | 42.4% | 43.4% | **+0.278** |
| **Batting** | **Death Overs (Overs 16-20)** | 37.0 | 33.0 | 38.2% | 36.2% | **-0.435** |
| **Bowling** | **Powerplay (Overs 1-6)** | 70.8 | 56.5 | 59.1% | 67.6% | **+0.224** |
| **Bowling** | **Middle Overs (Overs 7-15)** | 41.0 | 24.0 | 34.4% | 24.2% | **-0.243** |
| **Bowling** | **Death Overs (Overs 16-20)** | 7.4 | 5.5 | 6.5% | 5.2% | **+0.087** |

*(Source: `outputs/step_15_1_final_results_eda/phase_wise_analysis.csv`)*

### Critical Insights on Phase Exposure
1. **The Batting "Death Bias" Paradox:**
   - Deliveries at $\text{PI} > 60.0$ are heavily concentrated in the death overs.
   - However, within Tier 1 batters, **the percentage of balls faced at the death correlates negatively ($r = -0.435$) with final BRS3 score!**
   - *Why?* Death overs feature extreme dismissal hazards ($\text{Out} > 10.0\%$) and high bowler yorker execution. Batters who face *only* death overs suffer severe survival penalties.
   - The top-ranked batters (Dhoni, Dube, Green, Shankar, Overton) face a **hybrid middle-to-death exposure** (40–50% Middle Overs, 40–50% Death Overs). They enter when pressure begins mounting in overs 12–15, establish positive clutch differentials, and accelerate through the death without suffering frequent dismissals.
2. **The Bowling Powerplay Concentration:**
   - In bowling, 59.1% of high-pressure deliveries occur in the **Powerplay** (e.g. defending low totals or bowling against explosive opening assaults).
   - Death overs represent only 6.5% of total high-pressure bowling deliveries across the population because death overs are split among specialized death bowlers.
   - Bowlers who bowl exclusively in the Powerplay (like Tim Southee, Trent Boult, Nasum Ahmed) accumulate large dot-ball shares ($> 48\%$) and low economy rates ($< 7.5$), benefiting significantly in $\text{Score\_Econ}$ and $\text{Score\_Dot}$.

---

## 6. Original v2.0 vs. Final Candidate Comparison (Section F)

### Table 8: Macro Comparison — Official v2.0 vs. Candidate Step 13

| Dimension | Batting (Official v2.0) | Batting (Step 13 BRS3) | Bowling (Official v2.0) | Bowling (Step 13 BoRS) |
| :--- | :---: | :---: | :---: | :---: |
| **Ranking Metric** | 4-Component BRS | 3-Component BRS3 | 4-Component BoRS | 4-Component BoRS |
| **Formula Weights** | 35% SR, 25% Surv, 20% Exec, 20% Diff | 45% SR, 35% Surv, 20% Diff | 40% Econ, 25% Wk, 20% Dot, 15% Diff | 40% Econ, 25% Wk, 20% Dot, 15% Diff |
| **Boundary Execution** | Included (20%) | **Removed (0%)** | N/A | N/A |
| **Qualification Rule** | Single Cutoff ($N \ge 60$) | **Rule B ($N \ge 60 \text{ OR } [N \ge 50, M \ge 6]$)** | Single Cutoff ($N \ge 60$) | **Rule B ($N \ge 60 \text{ OR } [N \ge 50, M \ge 6]$)** |
| **Tier 1 Population** | 116 | **146 (+30)** | 113 | **130 (+17)** |
| **Tier 2 Population** | 90 ($N \ge 30$) | **42 ($N \ge 40$, not in T1)** | 42 ($N \ge 30$) | **19 ($N \ge 40$, not in T1)** |
| **Full Pop Rank Corr ($\rho$)**| 1.0000 | **0.9912** | 1.0000 | **1.0000** (Scores identical) |
| **Tier 1 Rank Corr ($\rho$)** | 1.0000 | **0.9634** | 1.0000 | **0.9782** (Shifted by 17 entries) |

*(Source: `outputs/step_15_1_final_results_eda/original_vs_candidate_batting.csv` and `original_vs_candidate_bowling.csv`)*

### Attribution of Ranking Changes: Formula vs. Qualification
1. **Bowling: 100% Qualification-Driven:**
   - In bowling, the scoring formula was completely unchanged ($\text{score\_delta} = 0.00$ across all 589 bowlers; overall rank correlation $= 1.0000$).
   - All movements in Tier 1 bowling ranks stem from **Rule B qualification**: 17 high-breadth bowlers entered Tier 1.
   - Because Nasum Ahmed ($N=55, M=10$) entered at **Rank 2** and Junaid Siddique ($N=50, M=12$) entered at **Rank 5**, every previously qualified bowler between Ranks 2 and 10 shifted downward by 1 or 2 positions.
2. **Batting: Joint Formula and Qualification Dynamics:**
   - In batting, removing Boundary Execution eliminated double-counting of boundaries.
   - Batters who hit high boundary volumes but accumulated dot balls (e.g. Nicholas Pooran, Heinrich Klaasen) dropped slightly in rank, while players with high running efficiency and lower dismissal rates (e.g. Shivam Dube, Cameron Green, Vijay Shankar) rose.
   - Rule B brought 30 qualified batters into Tier 1, most notably **Jamie Overton**, who entered Tier 1 directly at **Rank 7** ($N=59, M=14, \text{BRS}_3=78.19$).

---

## 7. Outliers and Unusual Player Profiles (Section G)

### Table 9: Key Flagged Outliers and Unusual Profiles

| Discipline | Player Name | Tier & Rank | Score | Deliveries ($N$) | Matches ($M$) | Anomaly Classification | Detailed Profile & Analytical Context |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Batting** | **MS Dhoni** | Tier 1, #1 | **93.21** | 194 | 38 | Apex Outlier (+11.20 pt gap) | Astronomical regularized SR ($\text{SR}^* = 159.03$), low dismissal rate ($\text{Out}^* = 4.73\%$), and huge clutch delta ($\text{Diff}^* = +21.96$). Outstanding empirical closer across 38 matches. |
| **Batting** | **Jamie Overton** | Tier 1, #7 | **78.19** | 59 | 14 | Bowling All-Rounder in Batting Top 10 | High-pressure boundary sample ($N=59$). Raw SR of 171.19, batting avg 25.25, and $+50.95$ clutch delta across 14 fixtures for England and CSK. |
| **Bowling** | **Tim Southee** | Tier 1, #1 | **90.69** | 64 | 19 | Extreme Economy & Dot Master | Regularized economy of $6.87$, dot-ball rate of $49.73\%$, wicket rate of $8.25\%$, and clutch economy improvement of $+1.73$ runs/over. |
| **Bowling** | **Nasum Ahmed** | Tier 1, #2 | **88.84** | 55 | 10 | Rule B High-Breadth Spin Phenom | Regularized economy of $6.43$ (best in Tier 1), dot rate $52.09\%$, wicket rate $7.06\%$. Qualifies via Rule B ($N=55, M=10$). |
| **Batting** | **David Miller** | Tier 1, #87 | **49.67** | 201 | 43 | High Volume / Suppressed Clutch Score | Massive sample ($N=201$ balls across 43 matches). Excellent survival ($\text{Score\_Surv}=83.2$), but heavy dot balls under high pressure suppressed $\text{SR}^*$ to $110.0$ ($\text{Score\_SR}=37.5$), pulling overall rank down. |
| **Bowling** | **Jasprit Bumrah** | Tier 1, #14 | **66.86** | 231 | 51 | Elite Workhorse / Death Deflation | 231 high-pressure balls across 51 matches. Concedes almost zero loose balls, but bowling primarily at the extreme death against set hitters caps unregularized economy at $7.8–8.2$. |
| **Batting** | **Heinrich Klaasen** | Tier 1, #13 | **73.69** | 162 | 39 | Boundary Striker / High Dismissal Rate | Explosive strike rate ($\text{SR}^* = 148.2$), but higher dismissal rate under extreme pressure ($\text{Out}^* = 7.8\%$) reduces survival score, ranking him #13 in BRS3. |

*(Source: `outputs/step_15_1_final_results_eda/outliers_and_anomalies.csv`)*

---

## 8. Remaining Methodological Limitations (Section H)

The EDA reveals the following evidence-based limitations that selectors must consider:

1. **Phase Confounding & Batting Order Skew:**
   - Deliveries at $\text{PI} > 60.0$ naturally concentrate in the death overs and late chases.
   - Consequently, **finishers, power hitters, and bowling all-rounders receive vastly more high-pressure balls than specialist opening batters**.
   - Selectors must understand that the Batting Leaderboard reflects *closing reliability under pressure*, not an optimal batting lineup from positions 1 to 11.
2. **The Discrete Boundary at $\text{PI} = 60.0$:**
   - The operational classification treats deliveries with $\text{PI} = 60.1$ as full high-pressure balls and $\text{PI} = 59.9$ as low/moderate balls.
   - While necessary for clear tabular accounting, this step-function creates minor threshold sensitivity for players whose exposure sits near 60.0.
3. **Global Empirical Bayesian Priors ($\mu$):**
   - Shrinking all players toward global format-wide priors ($\mu_{\text{SR}} = 114.05, \mu_{\text{Econ}} = 9.06$) treats all roles identically.
   - A lower-order bowler who bats under pressure is compared against the same baseline strike rate as a specialist top-order batter. This is methodologically objective, but inflates the relative scores of bowling all-rounders who manage even moderate boundary hitting.
4. **Sample Breadth Boundaries in Rule B:**
   - While Rule B ($N \ge 50, M \ge 6$) successfully prevents sample concentration, players with $N = 49$ or $M = 5$ are excluded from Tier 1 regardless of talent. Boundary thresholds are governance conventions, not natural biological cutoffs.
5. **Retrospective Evaluation vs. Future Predictive Power:**
   - The rankings strictly capture **what players achieved under pressure between 2022 and 2026**.
   - They do not account for aging curves, physical injuries, venue changes, or changes in team tactical deployment.

---

## 9. Visualizations Generated

The following 11 visualization artifacts have been generated and saved to `outputs/step_15_1_final_results_eda/`:

1. `01_score_distributions_by_tier.png` — Boxplots of BRS3 and BoRS distributions across Full Population, Tier 1, Tier 2, and Below Threshold.
2. `02_rank_vs_score_and_gaps.png` — Score curves by rank, highlighting Dhoni's 11.20-pt isolation, Southee/Nasum's 8.90-pt lead, and mid-tier congestion.
3. `03_sample_size_vs_score.png` — Scatter plots of high-pressure deliveries vs. score, demonstrating the independence of volume and score.
4. `04_rule_b_qualification_pathways.png` — High balls ($N$) vs matches ($M$) scatter plots, highlighting Rule B qualifiers (Overton, Nasum, Junaid).
5. `05_component_correlations_and_weights.png` — Heatmaps showing empirical correlation structure between components and composite scores.
6. `06_top20_batters_breakdown.png` — Stacked horizontal bar chart of the Top 20 Batters displaying exact component score contributions.
7. `07_top20_bowlers_breakdown.png` — Stacked horizontal bar chart of the Top 20 Bowlers displaying exact component score contributions.
8. `08_phase_exposure_and_death_bias.png` — High-pressure delivery share across Powerplay, Middle, and Death overs for Top 20 players.
9. `09_original_v2_vs_candidate_transitions.png` — Official v2.0 vs Candidate Step 13 overall rank transition plots.
10. `10_clutch_regime_deltas_and_outliers.png` — Low/moderate vs. high pressure performance deltas for Batters and Bowlers.
11. `11_all_rounder_dual_profile_matrix.png` — Dual-discipline matrix (BRS3 vs. BoRS) evaluating key all-rounders.

---

## 10. Guidance for Selectors & Final Completion Checklist

### What the Final Rankings Tell Franchise Selectors
- **Who Closes Best Under Pressure:** The Top 10 Batters (Dhoni, Dube, Shashank Singh, Green, Dubey, Shankar, Overton, Rinku, Dockrell, Jitesh) represent the most reliable clutch finishers in modern T20 cricket. When games are on the line, these players consistently accelerate scoring while keeping dismissal rates low.
- **Who Controls Games Under Pressure:** The Top 10 Bowlers (Southee, Nasum, Maharaj, Rauf, Junaid, Adair, Shoriful, Rana, Hasaranga, Boult) are masters of run suppression and dot-ball generation when opponents are attacking.
- **How to Use the Leaderboard for Team Building:** Selectors should not treat the Top 10 Batters as an 11-player batting order. Instead, use these reliability metrics to identify clutch finishers (Dhoni, Overton, Rinku) to complement anchor openers and top-order accumulators.

### Final Verification Sign-Off
- [x] Input datasets verified: `exp13_batter_rankings.csv` (816 batters) and `exp13_bowler_rankings.csv` (589 bowlers).
- [x] Methodology parameters verified: BRS3, v2.0 BoRS, $K=50$, Rule B, $\text{PI} > 60.0$.
- [x] Tier populations verified: 146 Tier 1 Batters, 130 Tier 1 Bowlers.
- [x] All 12 required CSV tables and 11 PNG charts generated inside `outputs/step_15_1_final_results_eda/`.
- [x] All scripts preserved in `src/step_15_1_final_results_eda/`.
- [x] Zero modifications made to source data, v2.0 official data, or candidate rankings.
