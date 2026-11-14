# Step 16.3: Batting Threshold Sensitivity & Bowling Role-Bias Investigation Report

**Investigation Date:** 2026-11-13  
**Project:** SupeRR Selector (Round 1)  
**Status:** Completed & Validated  
**Module Directory:** [src/step_16_3_role_threshold_investigation/](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/step_16_3_role_threshold_investigation/)  
**Outputs Directory:** [outputs/step_16_3_role_threshold_investigation/](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/)  

---

## Executive Summary & Core Decision Matrix

This investigation examines three independent methodological questions arising from the approval of the **Step 16 Phase-Relative Z-Score Pressure Classification** ($Z > 1.00$):

1. **Question 1 (Top-Order Batting):** Should top-order batters (batting positions 1–3) have a lower Z-score threshold ($Z > 0.75$ or $Z > 0.50$ instead of $Z > 1.00$)?
2. **Question 2 (Death-Over Batting):** Should Death-over batting deliveries have a higher Z-score threshold ($Z > 1.25$ or $Z > 1.50$ instead of $Z > 1.00$)?
3. **Question 3 (Bowling Role Bias):** Does the current bowling pressure classification ($Z > 1.00$) or ranking methodology (BoRS) systematically favour particular bowling phases or roles (Powerplay, Middle Overs, Death Overs, or Multi-Phase)?

### Summary Decision Matrix

| Question / Experiment | Candidate Proposals | Empirical Findings | Final Recommendation |
| :--- | :--- | :--- | :--- |
| **Q1: Top-Order Batting Threshold** | Exp 1A: $Z > 0.75$<br>Exp 1B: $Z > 0.50$ | Captures routine 1st-over balls ($0$ wickets down, PI 38–44). Top capture jumps from 7.06% to 15.32%, diluting clutch crisis signal and creating unprincipled role-dependent double standards. | **REJECT (Retain $Z > 1.00$)** |
| **Q2: Death-Over Batting Threshold** | Exp 2A: $Z > 1.25$<br>Exp 2B: $Z > 1.50$ | Destroys phase parity. Death capture rate collapses from 19.25% to 9.26% (Representation Index falls from 1.064 to 0.583). Disqualifies 24 Tier 1 batters, starving genuine clutch finishers. | **REJECT (Retain $Z > 1.00$)** |
| **Q3: Bowling Role Bias** | Test for Death vs PP / Middle Bias | Bowling capture rates are virtually identical across all 4 roles (17.11%–18.34%, Rep Index 0.976–1.047). In BoRS, Death bowlers have 0 in Top 10 due to 60% containment weighting (40% Economy, 20% Dots). | **RETAIN CONTROL (No adjustment needed)** |

> [!IMPORTANT]
> **Methodology Verdict:** All three experimental adjustments are conclusively rejected. The Step 16 Phase $\times$ Innings Standard Z-Score ($Z > 1.00$) is verified as the optimal, mathematically consistent, and domain-defensible classification threshold across both disciplines.

---

## 1. Context, Dataset & Investigation Architecture

All analyses are executed on the clean active dataset of **188,097 deliveries** (excluding the 233 second-innings deliveries where target was already reached):
- **Batting Population:** 180,839 balls faced by 816 batters.
- **Bowling Population:** 180,041 legal deliveries bowled by 589 bowlers.
- **Control Classification:** Step 16 Approach B (grouped by `innings` $\times$ `phase`), Standard Z-score, High Pressure: $Z > 1.00$.
- **Performance Models:** BRS3 for Batting ($45\%$ SR, $35\%$ Survival, $20\%$ Clutch Diff; $K=50.0$), BoRS for Bowling ($40\%$ Economy, $25\%$ Wickets, $20\%$ Dots, $15\%$ Clutch Diff; $K=50.0$), Rule B Qualification (Tier 1: $N \ge 60$ or $N \ge 50, M \ge 6$; Tier 2: $N \ge 40$).

### Core Output Registry

All outputs have been generated and validated:
- [batting_role_threshold_exposure.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/batting_role_threshold_exposure.csv)
- [batting_phase_threshold_exposure.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/batting_phase_threshold_exposure.csv)
- [exp1_top_order_threshold_sensitivity.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/exp1_top_order_threshold_sensitivity.csv)
- [exp2_death_threshold_sensitivity.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/exp2_death_threshold_sensitivity.csv)
- [delivery_level_threshold_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/delivery_level_threshold_comparison.csv)
- [exp1_exp2_brs3_rankings_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/exp1_exp2_brs3_rankings_comparison.csv)
- [bowling_role_phase_exposure.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/bowling_role_phase_exposure.csv)
- [bowling_player_diagnostics_and_rankings.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/bowling_player_diagnostics_and_rankings.csv)
- [bowling_role_bias_summary.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/bowling_role_bias_summary.csv)
- [fig1_exp1_top_order_sensitivity.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig1_exp1_top_order_sensitivity.png)
- [fig2_exp2_death_threshold_sensitivity.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig2_exp2_death_threshold_sensitivity.png)
- [fig3_bowling_role_bors_distribution.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig3_bowling_role_bors_distribution.png)
- [fig4_bowling_role_component_tradeoffs.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig4_bowling_role_component_tradeoffs.png)

---

## 2. Experiment 1: Lower Top-Order Batting Threshold Investigation

### 2.1 Hypothesis & Experimental Design

Top-order batters (positions 1–3) naturally face fewer high-pressure deliveries under a standard $Z > 1.00$ threshold ($7.06\%$ capture rate) than middle-order ($19.73\%$) or lower-order batters ($52.36\%$). Experiment 1 investigates whether lowering the threshold for top-order batters:
- **Exp 1A:** Top-Order (positions 1–3) $Z > 0.75$; Middle/Lower Order (positions 4–11) $Z > 1.00$.
- **Exp 1B:** Top-Order (positions 1–3) $Z > 0.50$; Middle/Lower Order (positions 4–11) $Z > 1.00$.

### 2.2 Numerical Findings & Sensitivity Table

| Model Configuration | Top-Order Total Balls | Top HP Balls | Within-Role Capture % | HP Share % | Rep Index | Tier 1 Qualified | Tier 2 Specialist | Total Qualified |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control ($Z > 1.00$ for all)** | 90,068 | 6,355 | **7.06%** | 19.43% | 0.390 | 206 | 35 | 241 |
| **Exp 1A (Top $Z > 0.75$)** | 90,068 | 9,404 | **10.44%** | 26.30% | 0.528 | 221 (+15) | 38 | 259 (+18) |
| **Exp 1B (Top $Z > 0.50$)** | 90,068 | 13,799 | **15.32%** | 34.37% | 0.690 | 234 (+28) | 35 | 269 (+28) |

```
Figure 1 Visualization:
[fig1_exp1_top_order_sensitivity.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig1_exp1_top_order_sensitivity.png)
```

### 2.3 Qualitative Delivery Audit: The Contamination of "Pressure"

Direct inspection of deliveries that flip from low/moderate ($Z \le 1.00$) to high pressure under Exp 1A and Exp 1B in [delivery_level_threshold_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/delivery_level_threshold_comparison.csv) demonstrates severe conceptual contamination:
- **Delivery 3 (Innings 1, Over 1, Ball 2):** Score: 1/0, $0$ wickets down, $\text{PI} = 41.50$, $Z = 0.731$. Flipped to High Pressure under Exp 1B. This is a completely routine second ball of a standard first innings.
- **Delivery 5 (Innings 2, Over 1, Ball 2):** Score: 1/0, $0$ wickets down, $\text{RRR} = 8.55$, $\text{PI} = 48.81$, $Z = 0.531$. Flipped to High Pressure under Exp 1B. Standard opening chase delivery.
- **Delivery 11 (Innings 1, Over 1, Ball 4):** Score: 2/0, $0$ wickets down, $\text{PI} = 41.00$, $Z = 0.700$. Routine powerplay ball.
- **Delivery 12–13 (Innings 1, Over 1, Balls 5–6):** Score: 2/0, $0$ wickets down, $\text{PI} = 39.20\text{--}40.75$, $Z = 0.588\text{--}0.684$. Routine powerplay balls.

### 2.4 Impact on Leaderboards & Rankings

In [exp1_exp2_brs3_rankings_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/exp1_exp2_brs3_rankings_comparison.csv):
- Lowering the threshold artificially inflates sample sizes by absorbing routine deliveries. For example, **Paul Stirling** jumps from unranked in Tier 1 ($N=43$, Tier 2 under Control) straight into **Rank 2** (BRS3 77.09, $N=76$) under Exp 1B.
- **Brian Bennett** experiences an artificial $+68$ rank jump from Rank 76 (BRS3 53.21, $N=67$) to **Rank 8** (BRS3 70.35, $N=118$).
- Middle-order batters who face genuine crisis deliveries (collapses, steep run chases) are pushed down by openers scoring freely in calm Powerplays.

### 2.5 Theoretical Evaluation & Verdict on Question 1

1. **Pressure Invariance Violation:** Pressure is an objective physical property of the match state (score, overs remaining, wickets lost, required run rate). Setting $Z > 0.50$ for positions 1–3 and $Z > 1.00$ for positions 4–11 implies that the exact same delivery situation is simultaneously "High Pressure" for an opener and "Low Pressure" for a number four. This destroys the mathematical coherence of the Pressure Index.
2. **Dilution of Clutch Signal:** An opener batting at 2/0 in Over 1 is not in a clutch crisis. Capturing these deliveries directly contradicts the project mandate to evaluate reliability under genuine pressure.
3. **Verdict:** **REJECT Experiment 1.** Retain uniform $Z > 1.00$ for all batting positions.

---

## 3. Experiment 2: Higher Death-Over Batting Threshold Investigation

### 3.1 Hypothesis & Experimental Design

Experiment 2 investigates whether raising the threshold for Death-over batting deliveries ($Z > 1.25$ or $Z > 1.50$ instead of $Z > 1.00$) further curtails finisher dominance:
- **Control:** $Z > 1.00$ for all phases.
- **Exp 2A:** Death Phase $Z > 1.25$; PP & Middle $Z > 1.00$.
- **Exp 2B:** Death Phase $Z > 1.50$; PP & Middle $Z > 1.00$.

### 3.2 Numerical Findings & Phase Sensitivity Table

| Model Configuration | Phase | Total Balls | Natural Share % | HP Balls | Phase Capture % | HP Share % | Rep Index | Tier 1 Qualified |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control ($Z > 1.00$)** | Powerplay | 57,037 | 31.54% | 10,250 | 17.97% | 31.34% | **0.994** | **206** |
| | Middle | 84,038 | 46.47% | 14,803 | 17.61% | 45.26% | **0.974** | |
| | Death | 39,764 | 21.99% | 7,655 | 19.25% | 23.40% | **1.064** | |
| **Exp 2A (Death $Z > 1.25$)** | Powerplay | 57,037 | 31.54% | 10,250 | 17.97% | 33.40% | 1.059 | **191 (-15)** |
| | Middle | 84,038 | 46.47% | 14,803 | 17.61% | 48.24% | 1.038 | |
| | Death | 39,764 | 21.99% | 5,632 | **14.16%** | 18.35% | **0.834** | |
| **Exp 2B (Death $Z > 1.50$)** | Powerplay | 57,037 | 31.54% | 10,250 | 17.97% | 35.67% | 1.131 | **182 (-24)** |
| | Middle | 84,038 | 46.47% | 14,803 | 17.61% | 51.52% | 1.109 | |
| | Death | 39,764 | 21.99% | 3,682 | **9.26%** | 12.81% | **0.583** | |

```
Figure 2 Visualization:
[fig2_exp2_death_threshold_sensitivity.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig2_exp2_death_threshold_sensitivity.png)
```

### 3.3 Destruction of Phase Balance & Sample Starvation

1. **Step 16 Already Solved the Finisher Bias:**
   Under the legacy fixed $\text{PI} > 60.0$, Death overs had a Representation Index of **2.02** (accounting for $44.5\%$ of all HP deliveries). Step 16’s phase-relative standard Z-score completely cured this distortion, bringing Death Representation Index to **1.064** (almost perfect parity with natural share $21.99\%$).
2. **Exp 2 Introduces Severe Under-Representation:**
   Raising the Death threshold to $Z > 1.25$ drops the Representation Index to **0.834**, and $Z > 1.50$ crashes it to **0.583**. Death overs become severely under-represented relative to their natural frequency.
3. **Disqualification of Legitimate Finishers:**
   In Exp 2A, **15 Tier 1 batters are disqualified**; in Exp 2B, **24 Tier 1 batters are disqualified**. Elite clutch performers lose legitimate high-pressure deliveries. For example:
   - **Patrick Cummins:** Drops from Rank 1 (BRS3 80.30) to Rank 13 in Exp 2A (67.93) and Rank 21 in Exp 2B (62.41).
   - **Shashank Singh:** Drops from Rank 3 (74.55) to Rank 15 in Exp 2B (65.94).
   - **Jitesh Sharma:** Drops from Rank 4 (74.07) to Rank 17 in Exp 2B (64.44).
4. **Verdict:** **REJECT Experiment 2.** Retain uniform $Z > 1.00$ for Death overs.

---

## 4. Experiment 3: Bowling Role & Phase Exposure and Bias Investigation

### 4.1 Bowling Role Definitions

To evaluate potential bowling biases rigorously, all 589 bowlers in the dataset are classified into four mutually exclusive operational roles based on their career phase allocations:
1. **Powerplay Specialist:** $\text{PP share} \ge 45\%$ and $\text{Death share} < 25\%$ (84 total bowlers; e.g., Deepak Chahar, Umesh Yadav, Mohammed Shami, Trent Boult).
2. **Middle Overs Specialist:** $\text{Middle share} \ge 50\%$ and $\text{Death share} < 25\%$ (250 total bowlers; e.g., Ravindra Jadeja, Ravichandran Ashwin, Sunil Narine, Adil Rashid, Keshav Maharaj).
3. **Death Overs Specialist:** $\text{Death share} \ge 30\%$ and $\text{PP share} < 30\%$ (78 total bowlers; e.g., Dwayne Bravo, Chris Jordan, Harshal Patel, Andre Russell, Mohit Sharma, Matheesha Pathirana).
4. **Multi-Phase Bowler:** Operates across multiple phases without single-phase isolation (177 total bowlers; pace spearheads and multi-phase all-rounders; e.g., Tim Southee, Bhuvneshwar Kumar, Haris Rauf, Mark Wood, Pat Cummins, Jasprit Bumrah).

### 4.2 Bowling Pressure Exposure Across Roles

| Bowling Role | Total Legal Balls | Natural Share % | HP Balls ($Z > 1.00$) | Within-Role Capture % | HP Share % | Rep Index |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay Specialist** | 26,129 | 14.51% | 4,792 | **18.34%** | 15.19% | **1.047** |
| **Middle Overs Specialist** | 69,029 | 38.34% | 12,059 | **17.47%** | 38.22% | **0.997** |
| **Death Overs Specialist** | 14,837 | 8.24% | 2,717 | **18.31%** | 8.61% | **1.045** |
| **Multi-Phase Bowler** | 70,046 | 38.91% | 11,982 | **17.11%** | 37.98% | **0.976** |
| **Total / Overall** | **180,041** | **100.00%** | **31,550** | **17.52%** | **100.00%** | **1.000** |

```
Figure 3 & Figure 4 Visualizations:
[fig3_bowling_role_bors_distribution.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig3_bowling_role_bors_distribution.png)
[fig4_bowling_role_component_tradeoffs.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_3_role_threshold_investigation/fig4_bowling_role_component_tradeoffs.png)
```

> [!NOTE]
> **Key Finding on Pressure Exposure:**  
> The within-role capture rates under Step 16 are virtually identical across all four roles:
> - Powerplay Specialists: $18.34\%$
> - Middle Overs Specialists: $17.47\%$
> - Death Overs Specialists: $18.31\%$
> - Multi-Phase Bowlers: $17.11\%$
> Every role's representation index is within $[0.976, 1.047]$. **There is zero pressure classification bias across bowling roles under Step 16.**

---

### 4.3 Bowling Ranking Outcomes & Leaderboard Representation

Under the approved BoRS formula and Rule B qualification ($K=50.0$), how do the four bowling roles fare?

| Bowling Role | Total Bowlers | Tier 1 Bowlers | Tier 1 Qual Rate % | Tier 1 Share % | Top 10 Bowlers | Top 25 Bowlers | Mean BoRS | Median BoRS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay Specialist** | 84 | 26 | 30.95% | 14.94% | **3** | **4** | **51.96** | 49.49 |
| **Middle Overs Specialist** | 250 | 60 | 24.00% | 34.48% | **1** | **4** | **45.21** | 44.94 |
| **Death Overs Specialist** | 78 | 15 | 19.23% | 8.62% | **0** | **2** | **47.43** | 48.57 |
| **Multi-Phase Bowler** | 177 | 73 | 41.24% | 41.95% | **6** | **15** | **51.54** | 51.27 |
| **Total Population** | **589** | **174** | **29.54%** | **100.00%** | **10** | **25** | **48.87** | **48.81** |

### 4.4 Top 15 Tier 1 Bowlers Under Step 16 Control

| Tier 1 Rank | Player Name | Operational Role | High Legal Balls ($N$) | BoRS | Score Econ (40%) | Score Wicket (25%) | Score Dot (20%) | Score Diff (15%) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Nasum Ahmed** | Powerplay Specialist | 80 | **85.23** | 95.19 | 59.17 | 93.94 | 90.47 |
| **2** | **Brad Evans** | Multi-Phase Bowler | 63 | **82.51** | 79.42 | 94.68 | 62.94 | 96.56 |
| **3** | **Haris Rauf** | Multi-Phase Bowler | 156 | **77.98** | 72.21 | 88.22 | 76.76 | 77.92 |
| **4** | **Mark Wood** | Multi-Phase Bowler | 64 | **77.49** | 67.32 | 100.00 | 82.57 | 60.29 |
| **5** | **Keshav Maharaj** | Middle Overs Specialist | 135 | **76.29** | 72.84 | 86.09 | 68.72 | 79.26 |
| **6** | **Tim Southee** | Multi-Phase Bowler | 90 | **76.03** | 67.68 | 100.00 | 71.52 | 64.40 |
| **7** | **Junaid Siddique** | Multi-Phase Bowler | 62 | **75.57** | 71.20 | 83.80 | 75.11 | 74.08 |
| **8** | **Shoriful Islam** | Powerplay Specialist | 73 | **74.71** | 73.78 | 74.52 | 78.96 | 71.83 |
| **9** | **Mark Adair** | Multi-Phase Bowler | 103 | **74.49** | 77.61 | 73.42 | 70.02 | 73.95 |
| **10** | **Harshit Rana** | Powerplay Specialist | 190 | **73.40** | 66.98 | 67.33 | 81.72 | 89.57 |
| **11** | Abbas Afridi | Multi-Phase Bowler | 67 | 71.74 | 70.72 | 79.37 | 64.21 | 71.75 |
| **12** | Maheesh Theekshana | Multi-Phase Bowler | 307 | 71.10 | 80.32 | 61.12 | 66.98 | 68.65 |
| **13** | Lungi Ngidi | Multi-Phase Bowler | 201 | 71.03 | 65.64 | 79.44 | 67.38 | 76.24 |
| **14** | Ottneil Baartman | Multi-Phase Bowler | 51 | 69.98 | 59.15 | 95.11 | 66.46 | 61.65 |
| **15** | Ravichandran Ashwin | Middle Overs Specialist | 219 | 68.70 | 78.72 | 67.83 | 50.23 | 68.07 |

---

### 4.5 Component Trade-offs & Structural Diagnosis

Why are Death-overs specialists NOT dominating the Bowling Top 10?

#### Mean Component Scores Across Roles (Tier 1 Bowlers)

| Bowling Role | Mean BoRS | Score Econ (40% Weight) | Score Wicket (25% Weight) | Score Dot-Ball (20% Weight) | Score Clutch Diff (15% Weight) | $\text{Econ}^*$ | $\text{Wk}^*$ % | $\text{Dot}^*$ % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Death Overs Specialist** | 47.43 | **44.24** | **59.60** | **36.94** | 49.62 | 9.35 | 5.98% | 34.24% |
| **Middle Overs Specialist** | 45.21 | **51.10** | **46.20** | **31.98** | 45.53 | 8.93 | 4.96% | 32.94% |
| **Multi-Phase Bowler** | 51.54 | **48.35** | **58.73** | **50.98** | 48.81 | 9.10 | 5.94% | 37.75% |
| **Powerplay Specialist** | 51.96 | **50.16** | **49.89** | **60.02** | 49.50 | 8.99 | 5.24% | 40.00% |

#### Structural Diagnosis: The 60% Containment Anchor

1. **Wicket Rate Advantage is Modest (25% Weight):**
   Death specialists do achieve the highest average shrunk wicket rate ($\text{Wk}^* = 5.98\%$, Score Wk = $59.60$). However, Multi-Phase bowlers achieve virtually identical wicket rates ($\text{Wk}^* = 5.94\%$, Score Wk = $58.73$).
2. **Containment Penalty is Heavy (60% Combined Weight):**
   The BoRS formula assigns **40% to Economy** and **20% to Dot-ball rate** (total 60% weight to run prevention and pressure building).
   - Death specialists operate in the highest-scoring phase of T20 cricket. Their average shrunk economy is **9.35** (Score Econ = $44.24$).
   - Their dot-ball rate is only **34.24%** (Score Dot = $36.94$).
   - By contrast, Powerplay specialists achieve a dot-ball rate of **40.00%** (Score Dot = $60.02$) and an economy of **8.99** (Score Econ = $50.16$).
3. **Where Do Elite Death Bowlers Rank?**
   Death specialists who control runs are appropriately rewarded:
   - **Matheesha Pathirana:** Rank 16 (BoRS 68.40; Score Econ 65.82, Score Wk 93.46, Score Dot 52.86).
   - **Mohit Sharma:** Rank 20 (BoRS 65.40; Score Econ 54.79, Score Wk 100.00, Score Dot 38.93).
   - **Obed McCoy:** Rank 36 (BoRS 59.62; Score Econ 50.94, Score Wk 77.44).
   - Conversely, high-economy death bowlers are properly penalized: **Harshal Patel** (Rank 105, BoRS 45.69, Score Econ 37.09) and **Andre Russell** (Rank 168, BoRS 26.83, Score Econ 12.39).
4. **Conclusion on Question 3:**
   The bowling methodology is completely sound. The pressure classification is unbiased across roles (all capture rates $\sim 17.5\%$), and BoRS's 60% containment weighting naturally prevents death-over wicket-takers from dominating while rewarding complete, multi-phase bowlers.

---

## 5. Synthesis & Final Methodology Recommendations

### 5.1 Definitive Answers to the Three Decision Questions

1. **Question 1: Should top-order batters have a lower Z-score threshold?**
   - **Decision: NO (REJECT Exp 1).**
   - **Rationale:** Lowering the threshold to $0.75$ or $0.50$ contaminates the pressure dataset with routine opening deliveries (e.g., Over 1, 0 wickets down, PI 38–42). It violates situational pressure invariance and artificially inflates opener rankings.
2. **Question 2: Should Death-over batting deliveries have a higher Z-score threshold?**
   - **Decision: NO (REJECT Exp 2).**
   - **Rationale:** Step 16 already eliminated the legacy finisher bias (bringing Death representation index from 2.02 to 1.064). Raising the threshold to $1.25$ or $1.50$ over-corrects, starves sample depth, disqualifies 24 Tier 1 batters, and severely under-represents death overs (Rep Index 0.58).
3. **Question 3: Does the bowling pressure classification or ranking favour particular bowling phases or roles?**
   - **Decision: NO (RETAIN Step 16 Control).**
   - **Rationale:** The pressure classification has zero role bias (capture rates are 17.1%–18.3% across all roles). BoRS formula dynamics balance wicket-taking with 60% containment weighting, naturally producing a balanced leaderboard where Multi-Phase pace spearheads (6 in Top 10) and Powerplay specialists (3 in Top 10) thrive, while elite death specialists rank fairly based on economy containment.

### 5.2 Final Methodology Freeze Confirmation

| Parameter / Dimension | Status | Frozen Specification |
| :--- | :--- | :--- |
| **Pressure Index Formula** | Frozen | Original v2.0 formula (Spell-based workload $W_{\text{spell}}$ retained) |
| **Pressure Classification** | Frozen | **Step 16 Approach B:** Separate Phase $\times$ Innings baselines, Standard Z-score, **$Z > 1.00$** for both Batting and Bowling across all phases and roles |
| **Batting Performance Metric** | Frozen | **BRS3:** $45\%$ Strike Rate, $35\%$ Survival, $20\%$ Clutch Differential |
| **Bowling Performance Metric** | Frozen | **BoRS (v2.0):** $40\%$ Economy, $25\%$ Wicket Rate, $20\%$ Dot-Ball Rate, $15\%$ Clutch Diff |
| **Bayesian Shrinkage** | Frozen | $K = 50.0$ across all components |
| **Player Qualification** | Frozen | **Rule B:** Tier 1: $N \ge 60$ OR ($N \ge 50$ AND $M \ge 6$); Tier 2: $N \ge 40$; Excluded: $N < 40$ |
| **Role Eligibility** | Frozen | Universal eligibility across all player roles (specialists and all-rounders eligible in both disciplines) |

---
*Report compiled and verified under strict analytical standards for SupeRR Selector Round 1.*
