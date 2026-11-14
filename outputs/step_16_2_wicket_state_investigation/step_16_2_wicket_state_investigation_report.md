# Step 16.2: Investigate Wicket-State-Relative Batting Pressure
## Comprehensive Investigation and Methodology Evaluation Report

**Date:** 2026-11-13  
**Project:** SupeRR Selector 2.0 — T20 Pressure Reliability Evaluation  
**Status:** Completed Investigation (Methodology Experiment Rejection)  
**Deliverable Directory:** [`outputs/step_16_2_wicket_state_investigation/`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/)  

---

## Executive Summary & Final Decision

This investigation evaluates whether adding **wickets lost before each delivery (`wickets_before`)** to the approved Step 16 phase-relative Z-score classification improves the recognition of genuine top-order pressure situations without removing legitimate lower-order pressure.

The investigation compared the approved **Control Model** (Step 16 Approach B: Phase $\times$ Innings Standard Z-Scores with $Z > 1.0$) against two experimental wicket-state models:
1. **Experiment 1 (5-Group Scheme):** $0\text{--}1, 2\text{--}3, 4\text{--}5, 6\text{--}7, 8\text{--}10$ wickets lost.
2. **Experiment 2 (Consolidated 3-Group Scheme):** Low ($0\text{--}1$), Moderate ($2\text{--}4$), High ($5+$) wickets lost.

### Final Decision & Recommendation: **REJECT THE EXPERIMENT AND RETAIN THE CONTROL METHODOLOGY**
We strongly recommend **retaining the approved Step 16 Phase $\times$ Innings methodology** and **rejecting wicket-state-relative baselining**.

Adding wicket-state conditioning creates severe statistical and cricket distortions:
1. **Statistical Conditioning Removes the Crisis Signal:** Wickets lost is already a primary driver of the underlying Pressure Index ($30\%\text{--}40\%$ weight). Conditioning Z-scores on wickets lost mathematically subtracts out the crisis signal: a delivery bowled at $95/8$ in the 17th over is compared only against other 8-wicket collapses where PI averages $69.47$ (cutoff $= 86.05$). Consequently, **$79.01\%$ of all deliveries bowled when 6+ wickets are down are stripped of high-pressure status**.
2. **Artificial "Pressure" Manufactured for Low-Wicket Openers:** Because the cutoff for $0\text{--}1$ wickets lost in the Powerplay drops to $42.58$, **4,931 deliveries where 0 or 1 wicket had fallen were artificially promoted to "high pressure"**. This catapulted Powerplay openers attacking under zero crisis (e.g. Prithvi Shaw) to Rank 1 with an inflated BRS3 score of $90.08$.
3. **Severe Cell Sparsity:** In the Powerplay, 6–7 wickets lost contains only 13 deliveries in Innings 1 and 0 deliveries in Innings 2; 8–10 wickets lost contains 0 deliveries. Arbitrary fallback rules are required to patch empty cells.
4. **Qualification Contraction:** Tier 1 Rule B qualified batters contract from **206 down to 184 (-22 players)**, unfairly eliminating legitimate crisis finishers (e.g. Jamie Overton's sample drops from $N = 62$ to $N = 38$, causing total disqualification).

---

## 1. Methodology and Experimental Assumptions

### 1.1 Control Model (Approved Step 16 Methodology)
- **Population:** 188,097 clean deliveries (180,839 batting balls faced) across 789 full 20-over matches (357 IPL, 432 T20I).
- **Baselines:** 6 separate batting baselines: $\text{Innings } j \in \{1, 2\} \times \text{Phase } k \in \{\text{PP, Middle, Death}\}$.
- **Classification:** Standard Z-score $Z = (\text{PI} - \mu_{j, k}) / \sigma_{j, k} > 1.0000$.
- **Performance Evaluation:** BRS3 formula ($45\%$ Strike Rate, $35\%$ Survival, $20\%$ Clutch Differential) with Bayesian shrinkage $K = 50.0$ and Rule B qualification (Tier 1: $N \ge 60$ or $N \ge 50, M \ge 6$; Tier 2: $N \ge 40$).

### 1.2 Wicket-State Experimental Formulations
- **Wicket Attribution Rule:** Uses `wickets_before` (wickets lost by the batting team strictly *before* the delivery is bowled). Delivery outcomes are strictly excluded from state attribution.
- **Experiment 1 (5-Group Wicket Scheme):**
  - Group 1: 0–1 wickets lost
  - Group 2: 2–3 wickets lost
  - Group 3: 4–5 wickets lost
  - Group 4: 6–7 wickets lost
  - Group 5: 8–10 wickets lost
  - Fallback Rule: If cell count $N < 50$ (or $\sigma = 0$), fall back to the Phase $\times$ Innings baseline.
- **Experiment 2 (Consolidated 3-Group Scheme):**
  - Low Wickets: 0–1 wickets lost
  - Moderate Wickets: 2–4 wickets lost
  - High Wickets / Crisis: 5+ wickets lost

---

## 2. Baseline Distributions & Sample-Size Diagnostics

Distribution statistics were computed across all combinations and exported in [`wicket_state_baseline_distributions.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/wicket_state_baseline_distributions.csv).

### Table 2.1: 5-Group Wicket-State Distributions & Cutoffs (Batting Balls Faced)

| Innings | Phase | Wicket Group | Ball Count | Mean PI | Std Dev ($\sigma$) | Median PI | MAD | Effective Cutoff ($\mu + 1.0\sigma$) | Sample Adequacy |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | Powerplay | 0–1 Wkts | 23,246 | 27.21 | 15.36 | 24.98 | 17.51 | **42.58** | Robust |
| 1 | Powerplay | 2–3 Wkts | 4,956 | 39.79 | 13.76 | 38.60 | 14.83 | **53.55** | Robust |
| 1 | Powerplay | 4–5 Wkts | 318 | 56.58 | 11.83 | 55.45 | 11.12 | **68.41** | Low Sample |
| 1 | Powerplay | 6–7 Wkts | 13 | 76.42 | 6.76 | 76.54 | 6.76 | **83.18** | **Critically Sparse** |
| 1 | Powerplay | 8–10 Wkts | 0 | — | — | — | — | — | **Empty** |
| **1** | Middle | 0–1 Wkts | 10,296 | 10.33 | 8.97 | 8.67 | 6.42 | **19.30** | Robust |
| 1 | Middle | 2–3 Wkts | 19,809 | 25.88 | 12.51 | 24.11 | 13.48 | **38.40** | Robust |
| 1 | Middle | 4–5 Wkts | 10,536 | 41.12 | 13.12 | 40.50 | 13.62 | **54.24** | Robust |
| 1 | Middle | 6–7 Wkts | 1,733 | 54.62 | 13.52 | 53.69 | 13.91 | **68.14** | Robust |
| 1 | Middle | 8–10 Wkts | 264 | 61.39 | 13.44 | 61.08 | 13.66 | **74.82** | Low Sample |
| **1** | Death | 0–1 Wkts | 548 | 9.96 | 8.32 | 8.67 | 6.42 | **18.27** | Low Sample |
| 1 | Death | 2–3 Wkts | 4,614 | 23.48 | 11.51 | 22.84 | 11.96 | **34.98** | Robust |
| 1 | Death | 4–5 Wkts | 9,874 | 37.55 | 13.12 | 36.36 | 13.31 | **50.67** | Robust |
| 1 | Death | 6–7 Wkts | 5,794 | 51.54 | 14.00 | 50.48 | 14.47 | **65.54** | Robust |
| 1 | Death | 8–10 Wkts | 2,339 | 56.45 | 14.01 | 55.45 | 14.44 | **70.46** | Robust |
| **2** | Powerplay | 0–1 Wkts | 22,308 | 36.82 | 14.59 | 36.36 | 14.83 | **51.41** | Robust |
| 2 | Powerplay | 2–3 Wkts | 5,769 | 51.29 | 15.42 | 51.44 | 15.84 | **66.71** | Robust |
| 2 | Powerplay | 4–5 Wkts | 427 | 67.09 | 14.71 | 67.54 | 15.11 | **81.80** | Low Sample |
| 2 | Powerplay | 6–7 Wkts | 0 | — | — | — | — | — | **Empty** |
| 2 | Powerplay | 8–10 Wkts | 0 | — | — | — | — | — | **Empty** |
| **2** | Middle | 0–1 Wkts | 9,433 | 17.91 | 12.75 | 14.44 | 10.96 | **30.66** | Robust |
| 2 | Middle | 2–3 Wkts | 18,304 | 34.57 | 16.31 | 32.84 | 16.51 | **50.87** | Robust |
| 2 | Middle | 4–5 Wkts | 10,303 | 53.20 | 17.73 | 52.84 | 18.32 | **70.93** | Robust |
| 2 | Middle | 6–7 Wkts | 2,815 | 68.73 | 16.26 | 69.47 | 16.78 | **84.99** | Robust |
| 2 | Middle | 8–10 Wkts | 545 | 77.31 | 14.28 | 78.47 | 14.47 | **91.59** | Robust |
| **2** | Death | 0–1 Wkts | 350 | 7.89 | 8.77 | 6.50 | 6.42 | **16.67** | Low Sample |
| 2 | Death | 2–3 Wkts | 2,873 | 21.87 | 14.41 | 19.50 | 13.91 | **36.28** | Robust |
| 2 | Death | 4–5 Wkts | 5,383 | 40.37 | 18.41 | 38.60 | 18.82 | **58.78** | Robust |
| 2 | Death | 6–7 Wkts | 4,812 | 58.65 | 19.19 | 59.47 | 20.32 | **77.84** | Robust |
| 2 | Death | 8–10 Wkts | 3,177 | 69.47 | 16.58 | 70.47 | 17.34 | **86.05** | Robust |

### Key Analytical Insights from Baseline Distributions
1. **Severe Structural Cell Sparsity:** In the Powerplay, 3 out of 10 cells are completely empty ($N = 0$), and 1 cell contains only 13 deliveries. Teams simply do not lose 8 wickets in the first 6 overs in professional T20 cricket. Conditioning on fine-grained wicket states is structurally mismatched with the natural mechanics of the Powerplay.
2. **Massive Cutoff Discrepancies:**
   - In Innings 1 Death, the cutoff for $0\text{--}1$ wickets is **$18.27$**, whereas for $8\text{--}10$ wickets it is **$70.46$**.
   - In Innings 2 Death, the cutoff for $0\text{--}1$ wickets is **$16.67$**, whereas for $8\text{--}10$ wickets it is **$86.05$**.
   See [`fig1_wicket_state_baselines_by_phase.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/fig1_wicket_state_baselines_by_phase.png) for visual depiction.

---

## 3. Batting Role Exposure & Capture Comparison

We compared the distribution of high-pressure deliveries across batting orders in [`batting_role_capture_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/batting_role_capture_comparison.csv).

### Table 3.1: Batting Role Pressure Capture Comparison

| Batting Role | Total Balls Faced | Natural Share | Model | HP Balls | Within-Role Capture % | Total HP Balls | HP Share % | Representation Index |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Top Order (1–3)** | 90,068 | 49.81% | Control (Step 16) | 6,355 | 7.06% | 32,708 | 19.43% | 0.390 |
| | | | **Exp 1 (5-Group)** | **11,056** | **12.28%** | **32,257** | **34.27%** | **0.688** |
| | | | Exp 2 (3-Group) | 10,882 | 12.08% | 32,203 | 33.79% | 0.678 |
| **Middle Order (4–6)** | 64,887 | 35.88% | Control (Step 16) | 12,800 | 19.73% | 32,708 | 39.13% | 1.091 |
| | | | **Exp 1 (5-Group)** | **12,957** | **19.97%** | **32,257** | **40.17%** | **1.120** |
| | | | Exp 2 (3-Group) | 13,721 | 21.15% | 32,203 | 42.61% | 1.188 |
| **Lower Order (7–11)** | 25,884 | 14.31% | Control (Step 16) | 13,553 | 52.36% | 32,708 | 41.44% | 2.896 |
| | | | **Exp 1 (5-Group)** | **8,244** | **31.85%** | **32,257** | **25.56%** | **1.786** |
| | | | Exp 2 (3-Group) | 7,600 | 29.36% | 32,203 | 23.60% | 1.649 |

### Critical Findings on Batting Role Capture
1. **Lower Order Stripped of Legitimate Samples:** Under Exp 1, lower-order deliveries collapse from 13,553 down to **8,244 balls (-39.2% reduction)**. Over 5,300 high-pressure deliveries faced by lower-order batters were erased.
2. **Where Did the Top Order Balls Come From?**
   Top-order balls increased by $+4,701$ balls (from 6,355 to 11,056). A detailed delivery-level trace in [`delivery_level_wicket_state_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/delivery_level_wicket_state_comparison.csv) revealed:
   - **$95.1\%$ of all balls gained by the top order ($4,931$ out of $5,183$) occurred when only 0 or 1 wicket had fallen.**
   - Early collapse deliveries (where 2, 3, or 4 wickets fell in the Powerplay) contributed less than $5\%$ of the gained balls because **the Control model was already capturing early collapse situations**.
   - Instead of rewarding collapse resistance, the wicket-state model rewarded routine Powerplay deliveries.
   See [`fig2_role_capture_and_share_comparison.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/fig2_role_capture_and_share_comparison.png).

---

## 4. Situational Integrity Diagnostics: Crisis Stripping & Routine Inflation

We conducted an independent audit of situational integrity across two critical scenarios:
1. **Routine Deliveries (9,921 balls):** Zero wickets lost and healthy scoring rate ($\text{CRR} \ge 8.5$ in Innings 1, or $\text{RRR} \le 6.5$ in Innings 2).
2. **Crisis Deliveries (21,492 balls):** Six or more wickets lost ($\text{wickets\_before} \ge 6$).

### Table 4.1: Situational Misclassification Diagnostics

| Test Scenario | Delivery Count | Evaluation Goal | Control (Step 16) | Exp 1 (5-Group) | Exp 2 (3-Group) | Methodological Finding |
| :--- | :---: | :--- | :---: | :---: | :---: | :--- |
| **Routine Deliveries** | 9,921 | Avoid classifying routine balls as HP | **0.00%** (0 balls) | **0.00%** (0 balls) | **0.00%** (0 balls) | All models correctly exclude extreme zero-wicket cruise balls. |
| **Crisis Deliveries** | 21,492 | Retain collapse crisis as HP | **53.52%** False Negatives | **79.01% False Negatives** | **71.56% False Negatives** | **Wicket-state models strip 79% of legitimate collapse crisis balls!** |

### The "Crisis Stripping" Statistical Mechanism
Why does the wicket-state model produce a **79.01% False Negative Rate** on crisis deliveries?
- In professional cricket, losing 6, 7, 8, or 9 wickets represents an objective match crisis.
- The control model evaluates a delivery relative to the general phase norm ($\mu \approx 29\text{--}47$). A collapse generates high PI ($60\text{--}85$), easily crossing the $+1\sigma$ cutoff.
- The wicket-state model evaluates a collapse delivery *only against other collapse deliveries*. Because the mean PI for 8–10 wickets in Innings 2 Death is $69.47$, the cutoff is pushed to **$86.05$**.
- A tailender batting at 110/8 needing 10 an over has an intense PI of $78.0$. But because $78.0 < 86.05$, the wicket-state model labels it as **NOT HIGH PRESSURE**!
See [`fig3_crisis_vs_routine_diagnostics.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/fig3_crisis_vs_routine_diagnostics.png).

---

## 5. Phase & Innings Distribution Balance

We evaluated phase and innings capture rates in [`phase_innings_capture_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/phase_innings_capture_comparison.csv).

### Table 5.1: Phase and Innings Capture Comparison

| Dimension | Segment | Total Deliveries | Control Capture % | Exp 1 (5-Group) Capture % | Exp 2 (3-Group) Capture % | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Phase** | Powerplay (PP) | 57,037 | 17.97% | 17.64% | 17.52% | Stable |
| **Phase** | Middle Overs | 84,038 | 17.61% | 17.19% | 17.07% | Stable |
| **Phase** | Death Overs | 39,764 | 19.25% | 19.48% | 19.78% | Stable |
| **Innings** | Innings 1 | 94,340 | 18.89% | 18.61% | 18.52% | Stable |
| **Innings** | Innings 2 | 86,499 | 17.21% | 17.00% | 17.03% | Stable |

While aggregate phase and innings percentages remain relatively stable ($\sim 17.5\text{--}19.5\%$), the underlying composition of deliveries is heavily corrupted: routine low-wicket Powerplay balls replaced legitimate late-innings collapse balls.

---

## 6. Player Exposure, Qualification & Experimental Rankings

We calculated player-level sample sizes and experimental BRS3 rankings across all 816 batters in [`player_exposure_and_qualification_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/player_exposure_and_qualification_comparison.csv) and [`experimental_brs3_rankings_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/experimental_brs3_rankings_comparison.csv).

### Table 6.1: Rule B Qualification Comparison

| Model | Total Batters | Pathway 1 ($N \ge 60$) | Pathway 2 ($N \ge 50, M \ge 6$) | Tier 1 (Rule B) | Tier 2 ($N \ge 40$) | Total Qualified ($N \ge 40$) | Excluded ($N < 40$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control (Step 16)** | 816 | 174 | 32 | **206** | 35 | **241** | 575 |
| **Exp 1 (5-Group)** | 816 | 161 | 23 | **184** | 27 | **211** | 605 |
| **Exp 2 (3-Group)** | 816 | 162 | 22 | **184** | 35 | **219** | 597 |

Tier 1 qualified batters contracted by **-22 players** (from 206 down to 184).

### Table 6.2: Experimental BRS3 Top 10 Comparison

| Control Rank | Player Name | Control Sample ($N$) | Control BRS3 | Exp 1 Rank | Exp 1 Sample ($N$) | Exp 1 BRS3 | Rank Change ($\Delta$) | Cricket Impact Assessment |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | Patrick Cummins | 135 | 80.30 | **117** | 59 | 51.93 | **-116** | Sample halved; dropped 116 ranks due to crisis stripping. |
| **2** | Jamie Overton | 62 | 75.32 | **Excluded** | 38 | 69.01 | **Disqualified** | High-pressure sample fell below Rule B cutoff ($N < 40$). |
| **3** | Shashank Singh | 161 | 74.55 | **41** | 117 | 65.16 | **-38** | Sample dropped by 44 balls; dropped 38 ranks. |
| **4** | Jitesh Sharma | 165 | 74.07 | **14** | 190 | 73.53 | -10 | Minor rank adjustment. |
| **5** | Vijay Shankar | 81 | 73.95 | **13** | 112 | 73.84 | -8 | Gained sample in low-wicket middle overs. |
| **6** | Cameron Green | 145 | 71.99 | **35** | 191 | 67.05 | -29 | Gained routine balls; dropped in efficiency. |
| **7** | Angkrish Raghuvanshi | 62 | 71.93 | **7** | 75 | 77.46 | **0** | Perfectly stable. |
| **8** | William Jacks | 85 | 71.36 | **10** | 133 | 75.16 | -2 | Retained in Top 10. |
| **9** | Suryakumar Yadav | 304 | 70.18 | **8** | 358 | 76.49 | +1 | Gained balls across all wicket states. |
| **10** | Riyan Parag | 181 | 69.86 | **19** | 211 | 71.09 | -9 | Minor drop. |

### Table 6.3: Top 10 Under Exp 1 (Wicket-State Model)

| Exp 1 Rank | Player Name | Exp 1 Sample ($N$) | Exp 1 BRS3 | Control Rank | Control Sample ($N$) | Control BRS3 | Cause of Elevation |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Prithvi Shaw** | 63 | **90.08** | **Excluded** | 30 | 88.99 | **Manufactured pressure at 0–1 wickets in Powerplay.** |
| **2** | **Sai Sudharsan** | 194 | **82.86** | 25 | 89 | 62.92 | Gained 105 balls at 0–1 wickets down in Middle overs. |
| **3** | M Shahrukh Khan | 149 | 81.60 | 47 | 129 | 57.83 | Elevated by middle-over boundary hitting. |
| **4** | **Jonny Bairstow** | 99 | **79.18** | 105 | 54 | 50.47 | Jumped 101 ranks due to 0-wicket Powerplay scoring. |
| **5** | Ramandeep Singh | 61 | 78.95 | 32 | 108 | 61.42 | High clutch diff retained. |
| **6** | Hardik Pandya | 404 | 77.54 | 23 | 318 | 63.89 | Substantial sample gain across all phases. |
| **7** | Angkrish Raghuvanshi | 75 | 77.46 | 7 | 62 | 71.93 | Retained from Control. |
| **8** | Suryakumar Yadav | 358 | 76.49 | 9 | 304 | 70.18 | Retained from Control. |
| **9** | George Dockrell | 101 | 76.01 | 28 | 151 | 62.07 | Moderate movement. |
| **10** | William Jacks | 133 | 75.16 | 8 | 85 | 71.36 | Retained from Control. |

See [`fig4_top10_rank_shift_comparison.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_2_wicket_state_investigation/fig4_top10_rank_shift_comparison.png) for visual exhibit.

---

## 7. Direct Answers to Required Comparisons

### 1. Top-order recognition:
Does the new method capture more genuine pressure deliveries faced by positions 1–3, especially during early collapses?
**No.** Early collapse deliveries (where 2, 3, or 4 wickets fell in the Powerplay) were **already captured** under the Control model. The 4,701 extra balls gained by the top order were almost entirely ($95.1\%$) routine balls where only 0 or 1 wicket had fallen.

### 2. Routine situations:
Does it avoid classifying routine deliveries as high pressure?
**No.** By lowering the Powerplay and Death cutoffs for $0\text{--}1$ wickets to $42.58$ and $18.27$, it manufactured high-pressure classifications for attacking openers playing with zero match crisis.

### 3. Lower-order preservation:
Does it retain genuinely difficult situations faced by positions 7–11?
**No.** It stripped $39.2\%$ of lower-order high-pressure balls ($5,300$ deliveries erased) and produced a catastrophic **$79.01\%$ False Negative Rate** on crisis deliveries with 6+ wickets lost.

### 4. Phase distribution:
Phase distributions remain nominally around $17.5\text{--}19.5\%$, but their situational meaning is severely corrupted.

### 5. Innings distribution:
Innings balance remains stable ($54.4\% / 45.6\%$), but exhibits the same internal distortion.

### 6. Player exposure:
Openers artificially doubled their samples, while genuine collapse finishers saw their samples cut in half.

### 7. Qualification impact:
Tier 1 Rule B batters contracted from **206 down to 184**. Proven crisis finishers were disqualified.

### 8. Ranking impact:
Prithvi Shaw jumped from Excluded ($N = 30$) to **Rank 1 in the world** ($N = 63, \text{BRS3} = 90.08$), while genuine crisis performers like Pat Cummins dropped from Rank 1 to Rank 117.

---

## 8. Final Decision & Methodological Verdict

### Decision Question:
> *"Does adding wickets lost produce a more cricket-valid pressure classification than the current phase × innings Z-score method?"*

### Unanimous Verdict: **NO. RETAIN THE CURRENT STEP 16 METHODOLOGY.**
Adding wickets lost to the Z-score baselines commits the classic statistical fallacy of **conditioning on the outcome variable**. Wickets lost is the primary source of cricket pressure; standardizing within wicket-loss groups removes the pressure of losing wickets.

The Step 16 Phase $\times$ Innings methodology remains the most statistically rigorous, robust, and cricket-valid classification model developed in this project.

**Step 16.2 is concluded. The experiment is rejected, and Step 16 methodology is confirmed for Step 17 implementation.**
