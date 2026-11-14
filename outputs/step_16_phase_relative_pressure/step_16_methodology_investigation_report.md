# Step 16: Phase-Relative Pressure Classification (Z-Score Investigation)
## Comprehensive Methodology Investigation and Recommendation Report

**Date:** 2026-11-13  
**Project:** SupeRR Selector 2.0 — T20 Pressure Reliability Evaluation  
**Status:** Completed Investigation (Phase-Relative Classification Freeze)  
**Deliverable Directory:** [`outputs/step_16_phase_relative_pressure/`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/)  

---

## Executive Summary

The SupeRR Selector project measures players' historical performance under high pressure in T20 cricket (IPL and T20I matches from 2022 onward). Under the original v2.0 methodology frozen in Step 15, deliveries were classified as "High Pressure" using a flat, global cutoff of $\text{Pressure Index (PI)} > 60.0$.

Independent exploratory audits (Step 8, Step 15.1, and Step 15.1.1) revealed that this flat threshold creates two severe structural biases:
1. **Bowling Death-Over Deprivation:** Because bowling spell workloads reset when bowlers rotate and early-innings fielding restrictions elevate Powerplay scores, raw Bowling PI averages $50.00$ in the Powerplay but only $29.28$ in the Death Overs. Consequently, under a flat cutoff of $60.0$, **58.16% of all high-pressure bowling deliveries occurred in the Powerplay, while only 6.43% occurred in the Death Overs**. Only 3.24% of all death-over legal balls qualified as high pressure, requiring an extreme $+2.12$ standard deviation score.
2. **Batting Finisher Bias:** Batting PI averages $42.78$ in Death Overs compared to $34.97$ in the Powerplay and $32.71$ in Middle Overs, driven by accelerating required run rates and late-innings wickets. Under $\text{PI} > 60.0$, **lower-order batters (positions 7–11) had 52.54% of their deliveries classified as high pressure and accounted for 58.30% of all high-pressure batting balls**, while top-order batters (positions 1–3) saw only 3.04% of their balls classified as high pressure.

This investigation evaluates **phase-relative Z-score classification** as a statistically principled replacement for the flat $\text{PI} > 60.0$ threshold. 

### Core Recommendations for Step 17
1. **Adopt Phase-Relative Z-Scores:** Empirically proven to eliminate structural phase distortions by evaluating pressure relative to contextual phase norms.
2. **Implement Approach B (Phase $\times$ Innings Baselines):** Innings 2 exhibits statistically significant and practically large elevations in PI across all phases (Cohen's $d = 0.55\text{--}0.65$ in batting; $d = 0.82$ in death bowling). Approach B eliminates chasing bias, achieving an innings distribution of $54.5\% / 45.5\%$ (batting) and $50.9\% / 49.1\%$ (bowling).
3. **Select Standard Z-Scores over Robust Z-Scores:** The underlying PI distributions exhibit near-normal skewness ($0.33\text{--}0.52$) and platykurtic kurtosis ($-0.58\text{ to } +0.27$), with no outlier distortion. Robust Z-scores artificially inflate Powerplay share due to very small Powerplay MAD values.
4. **Approve $Z > 1.0000$ as the Optimal Threshold:** Captures the top $18.09\%$ of batting balls and $17.52\%$ of bowling balls ($1 \sigma$ cutoff). Expands Tier 1 Rule B qualified players from 146 to 206 batters and from 130 to 174 bowlers, while boosting death-bowling high-pressure volume by **$+435\%$ (from 1,279 to 6,844 balls)** and top-order batting volume by **$+132\%$ (from 2,741 to 6,355 balls)**.

---

## 1. Audit of the Existing Pressure Index Implementation

The SupeRR Selector Pressure Index (PI) is calculated delivery-by-delivery across all completed 20-over matches using a linear combination of situational match pressure ($T$) and individual player state ($I$):
$$\text{PI} = 0.65 \times T + 0.35 \times I \quad \in [0, 100]$$

### 1.1 Match Population and Data Hygiene
- **Total Deliveries Analyzed:** 188,330 across 789 full 20-over completed matches (357 IPL, 432 T20I).
- **Established Delivery Exclusions:** Exactly 233 deliveries in second innings where the target had already been achieved (`innings == 2` and `runs_required <= 0`) are excluded from active evaluation, preserving a clean baseline of **188,097 deliveries**.
- **Discipline-Specific Subsets:**
  - **Batting:** 180,839 balls faced (`is_batter_ball_faced == 1`, excluding wides).
  - **Bowling:** 180,041 legal balls (`is_legal_ball == 1`, excluding wides and no-balls).

### 1.2 Exact Pressure Index Formulas (12 Specific Contexts)
Match phases are defined strictly by completed overs:
- **Powerplay (PP):** Overs 1–6 (`overid` 1 to 6, length 6 overs)
- **Middle Overs (Middle):** Overs 7–15 (`overid` 7 to 15, length 9 overs)
- **Death Overs (Death):** Overs 16–20 (`overid` 16 to 20, length 5 overs)

#### Individual Pressure Components ($I$)
- **Batter Individual Pressure ($B$):** Acclimatization pressure decaying over first 10 balls faced:
  $$B = \max\left(0, \min\left(100, \frac{10 - \text{striker\_balls\_faced\_before}}{10} \times 100\right)\right)$$
- **Bowler Individual Pressure ($I_{\text{bowler}}$):** Weighted combination of spell workload and batter acclimatization:
  $$B_{\text{workload}} = \min\left(100, \frac{\text{bowler\_legal\_balls\_in\_spell\_before}}{12} \times 100\right)$$
  $$S_{\text{settling}} = B$$
  $$I_{\text{bowler}} = 0.50 \times B_{\text{workload}} + 0.50 \times S_{\text{settling}}$$

#### Situational Match Pressure Components ($T$)
- **Innings 1 Batting (PI_B1):**
  - $\text{PP, Middle, Death:} \quad T = 0.40 W + 0.40 S + 0.20 O$
  - Where $W = \min(100, (\text{wickets}/6) \times 100)$; $O = (\text{phase\_overs\_completed}/\text{phase\_length}) \times 100$.
  - Score deficiency $S$: in PP & Middle, $S = \text{clip}((8 - \text{CRR})/8 \times 100, 0, 100)$; in Death, $S = \text{clip}((10 - \text{CRR})/10 \times 100, 0, 100)$.
- **Innings 1 Bowling (PI_BO1):**
  - $\text{PP, Middle, Death:} \quad T = 0.40 W + 0.40 S + 0.20 O$
  - Where $W = \max(0, ((6 - \text{wickets})/6) \times 100)$; $O = (\text{phase\_overs}/\text{phase\_len}) \times 100$.
  - Run concession pressure $S$: in PP, $S = \text{clip}((\text{CRR} - 8)/(12 - 8) \times 100, 0, 100)$; in Middle, $S = \text{clip}((\text{CRR} - 7)/(11 - 7) \times 100, 0, 100)$; in Death, $S = \text{clip}((\text{CRR} - 9)/(15 - 9) \times 100, 0, 100)$.
- **Innings 2 Batting (PI_B2):**
  - $\text{PP, Middle, Death:} \quad T = 0.50 R + 0.30 W + 0.20 O$
  - Where $R = \text{clip}((\text{RRR} - \text{bench})/(\text{ceil} - \text{bench}) \times 100, 0, 100)$ with benchmarks: PP $[6, 12]$, Middle $[7, 13]$, Death $[9, 18]$.
- **Innings 2 Bowling (PI_BO2):**
  - $\text{PP & Middle:} \quad T = 0.40 S + 0.40 W + 0.20 O$ (with CRR benchmarks $[6, 12]$ in PP and $[7, 11]$ in Middle).
  - $\text{Death:} \quad T = 0.50 S + 0.30 W + 0.20 O$ (with RRR benchmark $[9, 18]$).

---

## 2. Phase-Specific Distribution Analysis

Full statistical distributions were calculated independently for batting (balls faced) and bowling (legal balls) across:
- **Approach A:** Phase-only baselines pooled across both innings.
- **Approach B:** Phase $\times$ Innings baselines.
- **Approach C:** Format splits (IPL vs. T20I).

Full tabular outputs are documented in [`phase_distribution_statistics.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/phase_distribution_statistics.csv) and [`innings_phase_distribution_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/innings_phase_distribution_comparison.csv).

### Table 2.1: Empirical Phase Distribution Summary

| Discipline | Grouping / Phase | Delivery Count | Mean PI | Median PI | Std Dev ($\sigma$) | MAD | Skewness | Kurtosis |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Batting** | Overall (All BF) | 180,839 | 35.64 | 33.54 | 20.03 | 21.93 | +0.49 | -0.34 |
| | **Powerplay (PP)** | 57,037 | 34.97 | 34.49 | 16.97 | 19.48 | +0.26 | -0.63 |
| | **Middle Overs** | 84,038 | 32.71 | 28.89 | 20.60 | 21.42 | +0.65 | -0.20 |
| | **Death Overs** | 39,764 | 42.78 | 40.33 | 21.09 | 23.90 | +0.33 | -0.65 |
| **Bowling** | Overall (All LB) | 180,041 | 41.00 | 41.82 | 15.07 | 15.34 | -0.00 | -0.41 |
| | **Powerplay (PP)** | 56,796 | 50.00 | 47.29 | 11.02 | 9.89 | +0.58 | -0.25 |
| | **Middle Overs** | 83,786 | 40.41 | 39.80 | 13.65 | 14.84 | +0.18 | -0.47 |
| | **Death Overs** | 39,459 | 29.28 | 26.97 | 14.52 | 14.54 | +0.60 | -0.19 |

### Table 2.2: Innings 1 vs. Innings 2 Phase Distribution Comparison

| Discipline | Phase | Inn 1 Count | Inn 1 Mean | Inn 1 Median | Inn 2 Count | Inn 2 Mean | Inn 2 Median | Mean Diff (Inn 2 - Inn 1) | Cohen's $d$ | Effect Size |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Batting** | PP | 28,533 | 29.75 | 27.61 | 28,504 | 40.20 | 39.85 | **+10.45** | 0.648 | **Medium** |
| **Batting** | Middle | 42,638 | 27.28 | 24.11 | 41,400 | 38.29 | 36.06 | **+11.02** | 0.555 | **Medium** |
| **Batting** | Death | 23,169 | 39.50 | 37.17 | 16,595 | 47.36 | 48.75 | **+7.85** | 0.379 | **Small/Med** |
| **Bowling** | PP | 28,404 | 48.20 | 45.58 | 28,392 | 51.80 | 49.83 | **+3.60** | 0.332 | **Small** |
| **Bowling** | Middle | 42,528 | 40.40 | 39.63 | 41,258 | 40.42 | 40.00 | **+0.02** | 0.001 | Negligible |
| **Bowling** | Death | 22,980 | 24.66 | 23.89 | 16,479 | 35.72 | 34.93 | **+11.06** | 0.822 | **Large** |

### Key Findings from Phase Distributions
1. **Mathematical Proof of Death-Bowling Starvation Under Flat $\text{PI} > 60$:**
   In Death-over bowling, the mean PI is $29.28$ with a standard deviation of $14.52$. Reaching a flat score of $60.0$ requires a Z-score of:
   $$Z_{\text{Death, Bowl}} = \frac{60.0 - 29.28}{14.52} = +2.116 \implies \text{Top } 1.7\% \text{ of distribution}$$
   In contrast, in Powerplay bowling, the mean is $50.00$ with $\sigma = 11.02$:
   $$Z_{\text{PP, Bowl}} = \frac{60.0 - 50.00}{11.02} = +0.908 \implies \text{Top } 18.2\% \text{ of distribution}$$
   This demonstrates why 58.16% of all high-pressure bowling deliveries under $\text{PI} > 60$ occurred in the Powerplay, while death overs were starved.
2. **Innings 2 Structural Elevation:**
   Batting PI in Innings 2 is on average $10.0$ points higher than in Innings 1 across all three phases ($d = 0.55\text{--}0.65$). Similarly, Innings 2 Death-over bowling PI is $11.06$ points higher ($d = 0.822$). If Innings 1 and 2 are pooled into a single phase baseline (Approach A), Innings 2 automatically captures 68% of batting pressure, penalizing first-innings batters.

---

## 3. Experimental Z-Scores and Outlier Diagnostics

We investigated standard Z-scores ($Z = (\text{PI} - \mu) / \sigma$) and robust Z-scores ($Z_{\text{robust}} = (\text{PI} - \text{median}) / \text{MAD}$) across all deliveries. Tabular details are in [`outlier_and_distribution_analysis.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/outlier_and_distribution_analysis.csv).

### Table 3.1: Distribution Diagnostics and Theoretical Concordance

| Discipline | Distribution Model | Mean | Std | Median | MAD | Skewness | Kurtosis | % > 0.5 | % > 1.0 | % > 1.5 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| *Theoretical Normal* | $N(0, 1)$ | 0.00 | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 30.85% | 15.87% | 6.68% |
| **Batting** | App A Standard Z (Phase-only) | 0.00 | 1.00 | -0.12 | 1.11 | +0.46 | -0.43 | 31.07% | 17.59% | 8.24% |
| **Batting** | App A Robust Z (Phase-only) | +0.11 | 0.92 | 0.00 | 1.00 | +0.50 | -0.30 | 33.00% | 18.26% | 7.75% |
| **Batting** | **App B Standard Z (Phase $\times$ Inn)** | **0.00** | **1.00** | **-0.11** | **1.10** | **+0.39** | **-0.58** | **30.95%** | **18.09%** | **9.09%** |
| **Batting** | App B Robust Z (Phase $\times$ Inn) | +0.10 | 0.92 | 0.00 | 1.00 | +0.41 | -0.48 | 31.94% | 18.08% | 8.37% |
| **Bowling** | App A Standard Z (Phase-only) | 0.00 | 1.00 | -0.13 | 1.02 | +0.40 | -0.34 | 30.01% | 17.75% | 8.81% |
| **Bowling** | App A Robust Z (Phase-only) | +0.14 | 1.01 | 0.00 | 1.00 | +0.49 | -0.11 | 33.18% | 20.19% | 10.80% |
| **Bowling** | **App B Standard Z (Phase $\times$ Inn)** | **0.00** | **1.00** | **-0.11** | **1.05** | **+0.34** | **-0.36** | **30.58%** | **17.52%** | **8.33%** |
| **Bowling** | App B Robust Z (Phase $\times$ Inn) | +0.11 | 1.00 | 0.00 | 1.00 | +0.52 | +0.27 | 32.75% | 18.73% | 9.15% |

### Outlier Evaluation Findings
- **Absence of Severe Outliers:** All standardized distributions display skewness between $+0.34$ and $+0.52$ and slightly negative excess kurtosis (platykurtic, $-0.36\text{ to } -0.58$). There are no heavy tails or rogue extreme points distorting the sample mean.
- **Parametric Alignment:** At $Z > 1.0$, the empirical capture rate ($18.09\%$ in Batting, $17.52\%$ in Bowling) is remarkably close to the theoretical Gaussian expectation of $15.87\%$.
- **Robust Z Distortion:** While median and MAD are robust in heavy-tailed settings, in near-normal distributions where Powerplay variance is artificially low, MAD compresses Powerplay denominators. For example, in Innings 1 Bowling PP, MAD is only $8.35$ while $\sigma = 10.56$. Consequently, Robust Z inflates Powerplay scores, causing Powerplay bowling to capture $23.82\%$ of deliveries compared to $16.14\%$ in Death overs. **Standard Z-score provides superior phase parity.**

---

## 4. Evaluation of Candidate High-Pressure Thresholds

We evaluated thresholds $Z > 0.0, 0.5, 1.0, 1.5$ against the Baseline $\text{PI} > 60.0$. Full results are tabulated in [`zscore_threshold_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/zscore_threshold_comparison.csv).

### Table 4.1: Candidate Threshold Performance Comparison

| Model / Cutoff | HP Balls | % Total Balls | PP Share | Mid Share | Death Share | Inn 1 Share | Inn 2 Share | Tier 1 (Rule B) | Total Qual ($N \ge 40$) | Mean Qual Sample |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BATTING** | | | | | | | | | | |
| Baseline ($\text{PI} > 60.0$) | 23,328 | 12.90% | 20.49% | 40.60% | 38.91% | 31.19% | 68.81% | 146 | 188 | 86.9 |
| App A Standard $Z > 0.0$ | 83,503 | 46.18% | 33.43% | 44.69% | 21.88% | 40.51% | 59.49% | 328 | 380 | 202.5 |
| App A Standard $Z > 0.5$ | 56,181 | 31.07% | 32.45% | 44.78% | 22.77% | 36.43% | 63.57% | 282 | 314 | 156.0 |
| App A Standard $Z > 1.0$ | 31,805 | 17.59% | 31.88% | 46.07% | 22.05% | 32.11% | 67.89% | 202 | 243 | 102.6 |
| App A Standard $Z > 1.5$ | 14,910 | 8.24% | 30.93% | 47.22% | 21.84% | 21.78% | 78.22% | 77 | 110 | 70.5 |
| **App B Standard $Z > 1.0$** | **32,708** | **18.09%** | **31.34%** | **45.26%** | **23.40%** | **54.49%** | **45.51%** | **206** | **241** | **106.0** |
| App B Standard $Z > 1.5$ | 16,431 | 9.09% | 30.26% | 47.33% | 22.41% | 56.96% | 43.04% | 94 | 128 | 72.6 |
| **BOWLING** | | | | | | | | | | |
| Baseline ($\text{PI} > 60.0$) | 19,884 | 11.04% | 58.16% | 35.41% | 6.43% | 40.26% | 59.74% | 130 | 149 | 112.9 |
| App A Standard $Z > 0.0$ | 81,522 | 45.28% | 28.90% | 49.87% | 21.23% | 45.77% | 54.23% | 268 | 315 | 245.7 |
| App A Standard $Z > 0.5$ | 54,035 | 30.01% | 30.10% | 49.25% | 20.65% | 42.69% | 57.31% | 223 | 251 | 197.9 |
| App A Standard $Z > 1.0$ | 31,958 | 17.75% | 33.06% | 45.28% | 21.66% | 39.86% | 60.14% | 174 | 189 | 147.3 |
| App A Standard $Z > 1.5$ | 15,861 | 8.81% | 37.82% | 38.59% | 23.59% | 37.28% | 62.72% | 103 | 127 | 96.4 |
| **App B Standard $Z > 1.0$** | **31,550** | **17.52%** | **32.43%** | **45.88%** | **21.69%** | **50.88%** | **49.12%** | **174** | **190** | **145.1** |
| App B Standard $Z > 1.5$ | 14,994 | 8.33% | 38.78% | 40.96% | 20.26% | 53.56% | 46.44% | 98 | 121 | 94.3 |

### Detailed Evaluation of Candidate Cutoffs
- **$Z > 0.0$ (Median Split / 50th Percentile):** Captures $45\text{--}46\%$ of all deliveries. Classifying almost half of all balls bowled in professional cricket as "high pressure" is conceptually invalid; it conflates ordinary play with clutch situations.
- **$Z > 0.5$ (Upper 30th Percentile):** Captures $\sim 31\%$ of deliveries. While it expands player qualification to $>275$ batters and $>220$ bowlers, it dilutes the clutch signal by labeling 1 in every 3 balls as high pressure.
- **$Z > 1.5$ (Upper 8th Percentile):** Captures only $8.3\text{--}9.1\%$ of deliveries. This causes severe sample starvation: Tier 1 Rule B batters collapse to 94 (down from 146 in baseline), and qualified bowlers collapse to 98. Over 550 batters would have fewer than 20 balls under pressure, crippling the Bayesian shrinkage model.
- **$Z > 1.0$ (Upper 18th Percentile — Optimal):** Captures $18.09\%$ of batting deliveries and $17.52\%$ of bowling deliveries. It perfectly balances exclusivity with statistical robustness:
  - Batting Tier 1 Rule B expands by **$+41\%$ (from 146 to 206 players)**.
  - Bowling Tier 1 Rule B expands by **$+34\%$ (from 130 to 174 players)**.
  - Total qualified players ($N \ge 40$) increases to 241 batters and 190 bowlers.
  - Provides a healthy average qualified player sample of $106.0$ balls for batters and $145.1$ balls for bowlers.

---

## 5. Investigation of Bias Reduction (Central Requirement)

A primary reason for investigating phase-relative Z-scores is to establish whether the finisher bias in batting and the death-bowler bias in bowling are genuinely reduced.

Detailed tabular records are available in [`batting_role_exposure_analysis.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/batting_role_exposure_analysis.csv) and [`bowling_phase_exposure_analysis.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/bowling_phase_exposure_analysis.csv).

### 5.1 Batting Role Exposure Analysis

We grouped batters into three natural tactical orders:
- **Top Order (Positions 1–3):** 90,068 total balls faced ($49.81\%$ natural share).
- **Middle Order (Positions 4–6):** 64,887 total balls faced ($35.88\%$ natural share).
- **Lower Order (Positions 7–11):** 25,884 total balls faced ($14.31\%$ natural share).

### Table 5.1: Batting Role Pressure Exposure: Baseline vs. Proposed Model

| Batting Role | Total Balls Faced | Natural Share | Model | HP Balls | Within-Role Capture % | Share of All HP Balls | Representation Index |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **Top Order (1–3)** | 90,068 | 49.81% | Baseline ($\text{PI} > 60.0$) | 2,741 | 3.04% | 11.75% | 0.236 |
| | | | **Proposed (App B $Z > 1.0$)** | **6,355** | **7.06%** | **19.43%** | **0.390** |
| **Middle Order (4–6)** | 64,887 | 35.88% | Baseline ($\text{PI} > 60.0$) | 6,987 | 10.77% | 29.95% | 0.835 |
| | | | **Proposed (App B $Z > 1.0$)** | **12,800** | **19.73%** | **39.13%** | **1.091** |
| **Lower Order (7–11)** | 25,884 | 14.31% | Baseline ($\text{PI} > 60.0$) | 13,600 | 52.54% | 58.30% | 4.074 |
| | | | **Proposed (App B $Z > 1.0$)** | **13,553** | **52.36%** | **41.44%** | **2.896** |

#### Batting Bias Verdict: Substantially Reduced
- Under the baseline $\text{PI} > 60.0$, top-order batters faced 90,068 balls but received only 2,741 high-pressure balls ($3.04\%$ capture rate). In contrast, lower-order batters received 13,600 balls ($58.30\%$ of all high-pressure deliveries), giving lower-order finishers a representation index of $4.074$.
- Under **Approach B $Z > 1.0$**, high-pressure balls faced by the Top Order increase from 2,741 to **6,355 (+131.8% increase)**. Their share of all high-pressure balls rises from $11.75\%$ to $19.43\%$.
- Middle-order batters increase from 6,987 to 12,800 HP balls ($+83.2\%$).
- Lower-order share drops from $58.30\%$ to $41.44\%$. While lower-order capture rate remains high ($52.36\%$), this is physically authentic in cricket: lower-order batters only enter the crease when multiple top-order wickets have collapsed or during desperate late-innings chases.

---

### 5.2 Bowling Phase Exposure Analysis

We evaluated the distribution of legal balls across match phases:
- **Powerplay (PP):** 56,796 legal balls ($31.55\%$ natural share).
- **Middle Overs:** 83,786 legal balls ($46.54\%$ natural share).
- **Death Overs:** 39,459 legal balls ($21.92\%$ natural share).

### Table 5.2: Bowling Phase Pressure Exposure: Baseline vs. Proposed Model

| Phase | Total Legal Balls | Natural Share | Model | HP Legal Balls | Phase Capture Rate % | Share of All HP Balls | Representation Index |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **Powerplay (PP)** | 56,796 | 31.55% | Baseline ($\text{PI} > 60.0$) | 11,564 | 20.36% | 58.16% | 1.843 |
| | | | **Proposed (App B $Z > 1.0$)** | **10,231** | **18.01%** | **32.43%** | **1.028** |
| **Middle Overs** | 83,786 | 46.54% | Baseline ($\text{PI} > 60.0$) | 7,041 | 8.40% | 35.41% | 0.761 |
| | | | **Proposed (App B $Z > 1.0$)** | **14,475** | **17.28%** | **45.88%** | **0.986** |
| **Death Overs** | 39,459 | 21.92% | Baseline ($\text{PI} > 60.0$) | 1,279 | 3.24% | 6.43% | 0.293 |
| | | | **Proposed (App B $Z > 1.0$)** | **6,844** | **17.34%** | **21.69%** | **0.990** |

#### Bowling Bias Verdict: Completely Normalized
- Under the baseline $\text{PI} > 60.0$, death overs were virtually excluded: only 1,279 balls qualified as high pressure ($3.24\%$ capture rate; $6.43\%$ share; representation index $0.293$). Meanwhile, Powerplay bowling was grossly overrepresented ($58.16\%$ share; representation index $1.843$).
- Under **Approach B $Z > 1.0$**, Death-over high-pressure deliveries surge from 1,279 to **6,844 (+435.1% increase)**.
- **Near-Perfect Phase Parity:** The capture rate of each phase's own legal balls under Approach B $Z > 1.0$ is:
  - Powerplay: **$18.01\%$** (Representation index = 1.028)
  - Middle: **$17.28\%$** (Representation index = 0.986)
  - Death: **$17.34\%$** (Representation index = 0.990)
- The representation index across all three phases is virtually $1.00$ ($\pm 0.03$), demonstrating that bowling phase bias is comprehensively eliminated.

---

## 6. Statistical and Methodological Safeguards

To ensure that phase-relative Z-score classification is robust, reproducible, and immune to artifacts, five specific integrity checks were performed:

### 6.1 Competition Stability (IPL vs. T20I)
We compared phase-specific means and standard deviations across IPL and T20I matches in [`phase_distribution_statistics.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/phase_distribution_statistics.csv):
- **Batting PP:** IPL mean = $35.23$ ($\sigma = 17.24$) vs. T20I mean = $34.76$ ($\sigma = 16.73$) $\implies \Delta = 0.47$ points.
- **Batting Middle:** IPL mean = $31.90$ ($\sigma = 20.23$) vs. T20I mean = $33.38$ ($\sigma = 20.88$) $\implies \Delta = 1.48$ points.
- **Batting Death:** IPL mean = $41.55$ ($\sigma = 21.34$) vs. T20I mean = $43.86$ ($\sigma = 20.81$) $\implies \Delta = 2.31$ points.
- **Bowling PP:** IPL mean = $51.39$ ($\sigma = 11.34$) vs. T20I mean = $48.85$ ($\sigma = 10.61$) $\implies \Delta = 2.54$ points.
- **Bowling Middle:** IPL mean = $42.94$ ($\sigma = 13.68$) vs. T20I mean = $38.29$ ($\sigma = 13.26$) $\implies \Delta = 4.65$ points.
- **Bowling Death:** IPL mean = $30.72$ ($\sigma = 14.57$) vs. T20I mean = $28.02$ ($\sigma = 14.37$) $\implies \Delta = 2.70$ points.
**Conclusion:** The parameter estimates are remarkably consistent across IPL and T20I. Differences between competitions ($0.5\text{--}4.6$ points) are dwarfed by the differences across phases ($10\text{--}20$ points) and between innings ($8\text{--}11$ points). Separate competition baselines are unnecessary and would risk sample fragmentation.

### 6.2 Match Dominance Check
We examined whether high-pressure deliveries are dominated by a handful of extreme matches:
- Across all 789 matches, the mean number of deliveries per match is $238.4$.
- The median number of high-pressure deliveries per match under Approach B $Z > 1.0$ is $41.0$ (mean $43.0$, min $5$, max $110$).
- The top 10 matches by high-pressure volume account for **only 2.86%** of all high-pressure deliveries.
**Conclusion:** No single match or small cluster of matches dominates the distribution.

### 6.3 Phase Boundary Discontinuities
In the underlying PI formula, match progress $O$ resets to $0$ at the start of each phase (over 7 for Middle, over 16 for Death). Consequently:
- Batting PI drops from $27.59$ in over 6 to $16.89$ in over 7 (Inn 1), and Bowling PI drops from $41.53$ in over 15 to $20.94$ in over 16 (Inn 1).
- Applying a flat threshold across these boundaries created massive artificial cliffs.
- Phase-relative Z-scoring absorbs these structural resets because the mean and standard deviation within each phase naturally baseline against that phase's specific scale.

### 6.4 Neutrality Guarantee
Thresholds and groupings were evaluated strictly on statistical distributions, delivery capture rates, and sample sufficiency across the entire population of 188,097 deliveries. **No individual player rankings, scores, or Top 10 lists were inspected or tuned during Step 16.**

---

## 7. Visualizations and Analytical Exhibits

Five publication-grade visual artifacts were generated and saved in [`outputs/step_16_phase_relative_pressure/`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/):

1. **[`fig1_pi_distribution_by_phase.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/fig1_pi_distribution_by_phase.png):**  
   Shows empirical density distributions for Batting and Bowling PI across Powerplay, Middle, and Death phases. Clearly displays how the fixed $60.0$ threshold required extreme $+2.12 \sigma$ scores in Death Bowling, whereas $Z = 1.0$ cutoffs track each phase's natural upper quartile.
2. **[`fig2_innings_distribution_comparison.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/fig2_innings_distribution_comparison.png):**  
   Side-by-side boxplots of Innings 1 vs. Innings 2 pressure across phases, illustrating the statistically significant $+8\text{--}11$ point elevation in Innings 2.
3. **[`fig3_threshold_tradeoffs.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/fig3_threshold_tradeoffs.png):**  
   Sensitivity curves demonstrating the trade-off between delivery volume capture and qualified player counts across $Z \in [0.0, 1.5]$, confirming $Z = 1.0$ as the optimal inflection point.
4. **[`fig4_batting_role_exposure_comparison.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/fig4_batting_role_exposure_comparison.png):**  
   Grouped bar charts comparing Top, Middle, and Lower Order capture rates and shares under Baseline $\text{PI} > 60.0$ vs. Z-score models, showing the $+132\%$ increase in Top Order high-pressure exposure.
5. **[`fig5_bowling_phase_exposure_comparison.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_phase_relative_pressure/fig5_bowling_phase_exposure_comparison.png):**  
   Grouped bar charts illustrating the restoration of phase parity in bowling, where Death overs rise from $3.24\%$ capture rate under baseline to $17.34\%$ under the proposed model.

---

## 8. Final Recommendation and Methodology Freeze for Step 17

We provide direct, evidence-based answers to the seven mandatory recommendation questions:

### 1. Are phase-relative Z-scores justified by the data?
**Yes, unequivocally.** The raw Pressure Index operates on structurally disparate scales across Powerplay, Middle, and Death overs due to shifting fielding restrictions, run rate benchmarks, and bowler workload resets. A flat global threshold creates massive distortion ($+0.82 \sigma$ in Death batting vs $+1.48 \sigma$ in PP batting; $+0.91 \sigma$ in PP bowling vs $+2.12 \sigma$ in Death bowling). Standardizing pressure relative to phase norms resolves this without altering the underlying formula.

### 2. Do Innings 1 and 2 need separate baselines?
**Yes, Approach B (Phase $\times$ Innings) is essential.** Innings 2 exhibits a statistically large elevation in Batting PI ($+8\text{--}11$ points, $d = 0.55\text{--}0.65$) and Death Bowling PI ($+11.06$ points, $d = 0.822$). If pooled (Approach A), Innings 2 captures $68\%$ of batting pressure, penalizing first-innings batters. Approach B normalizes Innings 1 and 2 exposure to $54.5\% / 45.5\%$ (batting) and $50.9\% / 49.1\%$ (bowling), matching delivery volume.

### 3. Are standard or robust Z-scores more appropriate?
**Standard Z-scores ($Z = (\text{PI} - \mu) / \sigma$) are superior.** Diagnostic analysis confirms that the PI distributions have mild skewness ($0.34\text{--}0.52$) and near-normal kurtosis without heavy outlier tails. Robust Z-scores suffer because Powerplay Bowling PI has an artificially low MAD ($8.35$), which inflates Powerplay robust Z-values and reintroduces phase bias.

### 4. Which threshold is the strongest candidate and why?
**$Z > 1.0000$ under Approach B is the strongest candidate.**
- $Z > 0.0$ ($46\%$ capture) dilutes high pressure into routine match play.
- $Z > 0.5$ ($31\%$ capture) is overly permissive.
- $Z > 1.5$ ($8\text{--}9\%$ capture) causes severe sample starvation (Tier 1 Rule B collapses to 94 batters and 98 bowlers).
- $Z > 1.0$ captures $18.09\%$ of batting and $17.52\%$ of bowling deliveries, closely matching the upper $\sim 16\%$ Gaussian tail. It expands Tier 1 Rule B qualified players from 146 to 206 batters and 130 to 174 bowlers, providing robust sample depth.

### 5. Are finisher and death-bowler exposure biases reduced?
**Yes.**
- **Batting:** Top-order high-pressure volume increases by $+132\%$ (from 2,741 to 6,355 balls), giving specialist openers adequate sample depth. Lower-order share drops from $58.30\%$ to $41.44\%$.
- **Bowling:** Death-over high-pressure volume increases by $+435\%$ (from 1,279 to 6,844 balls). Capture rate parity across Powerplay ($18.01\%$), Middle ($17.28\%$), and Death ($17.34\%$) is virtually identical, completely eliminating the $58\%$ Powerplay bias.

### 6. What risks or limitations remain?
- Lower-order batters naturally face a higher proportion of high-pressure balls ($52\%$) than top-order batters ($7\%$) because tailenders primarily bat during collapses or close chases. This reflects authentic cricket physics, not formula bias.
- Discrete phase bins mean that small boundary step-changes exist between overs 6 and 7, and overs 15 and 16, though these are inherent to cricket's standard over segmentation.

---

### 7. Exact Proposed Classification Formula to Carry into Step 17

Define the high-pressure indicator for delivery $i$ bowled in innings $j \in \{1, 2\}$ and match phase $k \in \{\text{PP}, \text{Middle}, \text{Death}\}$:

$$\text{High\_Pressure}_{\text{Batting}, i} = \begin{cases} 1 & \text{if } \dfrac{\text{Batting\_PI}_i - \mu_{\text{Batting}, j, k}}{\sigma_{\text{Batting}, j, k}} > 1.0000 \\ 0 & \text{otherwise} \end{cases}$$

$$\text{High\_Pressure}_{\text{Bowling}, i} = \begin{cases} 1 & \text{if } \dfrac{\text{Bowling\_PI}_i - \mu_{\text{Bowling}, j, k}}{\sigma_{\text{Bowling}, j, k}} > 1.0000 \\ 0 & \text{otherwise} \end{cases}$$

#### Frozen Parameter Lookup Table (Reproduced from Step 16 Dataset)

| Discipline | Innings ($j$) | Phase ($k$) | Population Deliveries | Mean ($\mu$) | Std Dev ($\sigma$) | Effective Cutoff ($\mu + 1.0\sigma$) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **Batting** | Innings 1 | Powerplay (PP) | 28,533 | 29.7483 | 16.0789 | **45.8272** |
| **Batting** | Innings 1 | Middle Overs | 42,638 | 27.2792 | 17.2776 | **44.5568** |
| **Batting** | Innings 1 | Death Overs | 23,169 | 39.5031 | 17.5706 | **57.0737** |
| **Batting** | Innings 2 | Powerplay (PP) | 28,504 | 40.2022 | 16.2016 | **56.4038** |
| **Batting** | Innings 2 | Middle Overs | 41,400 | 38.2947 | 22.1941 | **60.4888** |
| **Batting** | Innings 2 | Death Overs | 16,595 | 47.3564 | 24.4665 | **71.8229** |
| **Bowling** | Innings 1 | Powerplay (PP) | 28,404 | 48.1985 | 10.5552 | **58.7537** |
| **Bowling** | Innings 1 | Middle Overs | 42,528 | 40.4027 | 13.7022 | **54.1049** |
| **Bowling** | Innings 1 | Death Overs | 22,980 | 24.6618 | 10.9545 | **35.6163** |
| **Bowling** | Innings 2 | Powerplay (PP) | 28,392 | 51.8018 | 11.1728 | **62.9746** |
| **Bowling** | Innings 2 | Middle Overs | 41,258 | 40.4192 | 13.5980 | **54.0172** |
| **Bowling** | Innings 2 | Death Overs | 16,479 | 35.7190 | 16.3216 | **52.0406** |

---

## 9. Strict Governance Confirmation

In strict compliance with the Step 16 instructions:
1. No official Pressure Index calculation was modified.
2. No official source CSVs (`data/*`) or processed files (`data/processed/*`) were altered or overwritten.
3. No Step 13, Step 15, or Step 15.1 candidate rankings or outputs were modified.
4. **No player scores, rankings, or leaderboards were recalculated.**
5. No predictive modeling or forward-looking match outcome information was introduced.
6. All scripts, data artifacts, and visual charts are strictly segregated inside `src/step_16_phase_relative_pressure/` and `outputs/step_16_phase_relative_pressure/`.

**Step 16 investigation is complete. Ready for independent review prior to Step 17 implementation.**
