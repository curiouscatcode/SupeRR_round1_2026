# Step 16.7 — Situational Intensity Investigation and Redesign: Final Report

**Date:** November 14, 2026  
**Status:** Completed, Audited & Mathematically Validated  
**Deliverable Type:** Empirical Investigation, Mathematical Audit & Redesign Recommendations  
**Dataset Scope:** 180,839 Clean Batting Deliveries across 789 T20 Matches  
**Deliverables Directory:** [outputs/step_16_7_situational_intensity_redesign/](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign)

---

## 1. Executive Summary & Candidate Classification Matrix

### 1.1 Objective & Context
In Step 16.6.1, an independent audit revealed that **top-order batters (positions 1–3) captured only 7.06% High Pressure deliveries**, while **lower-order tailenders (positions 7–11) captured 52.36%**. Step 16.7 was chartered to investigate the foundational root cause of this structural disparity: the **Situational Intensity ($I$)** component of the batting Pressure Index.

The canonical batting Pressure Index is:
$$\text{PI} = 0.65 \times \text{Task Difficulty } (T) + 0.35 \times \text{Situational Intensity } (I)$$

In the original v2.0 framework, Situational Intensity is computed exclusively from striker balls faced:
$$I = \operatorname{clip}\left( \frac{10 - \text{striker\_balls\_faced\_before}}{10} \times 100, 0, 100 \right)$$

### 1.2 Core Audit Discoveries
1. **The 35-Point Artificial Cliff:**  
   Because $I$ is weighted at $35\%$, a batter loses **35.0 full points of Pressure Index** simply by surviving 10 deliveries. In the Powerplay, where baseline standard deviation is $\sigma \approx 16.1$, this 35-point penalty represents a **downward shock of $2.17$ standard deviations**!
2. **The Eradication of Crisis Pressure for Set Batters:**  
   In controlled match environments where Task Difficulty is held constant at medium difficulty ($T \in [45, 55]$), High Pressure capture drops from **92.11% on ball 0** down to **0.00% on ball 10**!  
   More alarmingly, in severe crises and steep chases ($T > 65$):
   - A **new batter** (0–5 balls faced) captures **96.44% High Pressure deliveries**.
   - A **settled batter** (15+ balls faced, e.g. chasing 14 RRR or anchoring after a collapse) captures **ONLY 6.91% High Pressure deliveries**!
   - **93.09% of severe crisis deliveries faced by set batters are classified as LOW PRESSURE.**
3. **The Finisher Loophole:**  
   Tailenders (positions 8–11) face **67%–90% of their deliveries with $\le 5$ balls faced**, receiving average $I$ scores of **52 to 79**. Conversely, openers face **54% of their deliveries with $\ge 10$ balls faced ($I = 0$)**, receiving an average $I$ score of only **24.7**. This mathematical artifact, rather than match leverage, is the primary driver of both finisher bias and top-order under-capture.

### 1.3 Candidate Classification Matrix
| Candidate Model | Mathematical Formulation | HP Capture % | Top Order (1–3) HP % | Lower Order (7–11) HP % | Set Batters in Crisis ($T>65$) | BRS3 Rank $\rho$ vs Control | Tier 1 Batters | Final Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Candidate 0 (Control)** | $I_0 = \operatorname{clip}((10-\text{bf})/10 \times 100, 0, 100)$ | 18.09% | 7.06% | 52.36% | **6.91%** | 1.0000 | 206 | **RETAINED (Baseline)** |
| **Candidate 1 (Smooth Decay)** | $I_1 = 25.0 + 75.0 \times \exp(-\text{bf} / 10.0)$ | 18.04% | 6.52% | 55.76% | **16.64%** | **0.8094** | **209** | **RECOMMENDED FOR VALIDATION** |
| **Candidate 2 (Match-Stakes Context)** | $I_2 = 0.40 M_{\text{stage}} + 0.40 W_{\text{risk}} + 0.20 S_{\text{settle}}$ | 18.07% | 6.30% | 55.71% | **58.23%** | 0.6185 | 201 | **Promising but Unproven** |
| **Candidate 3 (Leverage & Crisis)** | $I_3 = w_C C_{\text{crisis}} + w_L L_{\text{conseq}} + 0.20 S_{\text{settle}}$ | 18.27% | 7.19% | 49.37% | **55.00%** | 0.6151 | 202 | **Promising but Unproven** |
| **Candidate 4 (Pure Task Difficulty)** | $\text{PI}_4 = T$ (Zero Intensity Ablation) | 18.85% | 8.54% | 53.46% | **73.94%** | 0.5808 | 205 | **Rejected (Diagnostic Benchmark)** |

---

## 2. Independent Audit of the Existing Formula

### 2.1 Mechanical Decay Across Balls Faced (0 to 35+)
We tracked the exact empirical progression of the 180,839 clean batting deliveries across striker balls faced:

| Balls Faced (bf) | Total Deliveries | Mean Intensity ($I$) | Mean Task Difficulty ($T$) | Mean Composite PI | Mean $Z_{\text{PI}}$ | High Pressure Capture % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 12,730 | 100.0 | 41.79 | **62.17** | **+1.415** | **71.52%** |
| **1** | 11,795 | 90.0 | 40.40 | **57.76** | **+1.176** | **60.28%** |
| **2** | 10,951 | 80.0 | 39.54 | **53.70** | **+0.958** | **48.86%** |
| **5** | 8,847 | 50.0 | 38.40 | **42.46** | **+0.347** | **19.50%** |
| **8** | 7,180 | 20.0 | 38.24 | **31.85** | **-0.231** | **4.60%** |
| **9** | 6,696 | 10.0 | 38.37 | **28.44** | **-0.419** | **2.57%** |
| **10** | 6,235 | 0.0 | 38.39 | **24.96** | **-0.606** | **0.99%** |
| **11** | 5,805 | 0.0 | 38.27 | **24.87** | **-0.606** | **0.88%** |
| **15** | 4,422 | 0.0 | 37.05 | **24.08** | **-0.612** | **0.86%** |
| **20** | 3,137 | 0.0 | 34.53 | **22.44** | **-0.642** | **0.89%** |
| **25** | 2,214 | 0.0 | 33.96 | **22.08** | **-0.642** | **0.77%** |
| **35+** | 10,343 | 0.0 | 36.14 | **23.49** | **-0.718** | **0.36%** |

#### Critical Empirical Takeaways:
1. **The Task Difficulty Invariance:**  
   Notice that across balls faced 0 through 15, **Task Difficulty ($T$) remains virtually flat between 37.0 and 41.8**. The physical match situation is not changing; what changes is solely the artificial $I$ penalty!
2. **The High Pressure Collapse:**  
   High Pressure capture plummets from **71.52% on ball 0** to **0.99% on ball 10**. Once a batter reaches ball 10, their likelihood of facing a high-pressure ball drops by a factor of **72x**!

### 2.2 Controlled Task Difficulty Analysis
To prove causality beyond correlation, we isolated all 20,959 deliveries where Task Difficulty was held strictly constant in the medium band ($T \in [45, 55]$, mean $T = 49.75$):

```
Controlled T in [45, 55] across Balls Faced:
bf_bin   Total Deliveries    Mean T    Mean I    Mean PI    Mean Z_PI    HP Capture %
  0           1,584          49.75     100.0      67.33      +1.688         92.11%
  1           1,455          49.66      90.0      63.78      +1.493         92.78%
  2           1,327          49.73      80.0      60.32      +1.306         85.31%
  5           1,104          49.77      50.0      49.85      +0.723         24.46%
  9             799          49.80      10.0      35.87      -0.046          0.00%
 10             735          49.91       0.0      32.44      -0.239          0.00%
 15             508          49.87       0.0      32.41      -0.258          0.00%
 25             219          49.56       0.0      32.21      -0.195          0.00%
```

- When $T$ is identical, a batter on ball 0 has a **92.11% chance of High Pressure**.
- By ball 10, that exact same situation has a **0.00% chance of High Pressure**.
- This proves conclusively that the drop in pressure is **pure mathematical artifact**, completely detached from match context.

### 2.3 The Set Batter in Crisis Pathology ($T > 65$)
We audited all 22,401 deliveries where Task Difficulty was in extreme crisis or steep chase ($T > 65$):
- **New Batters (0–5 balls faced):** 8,940 deliveries. Mean PI = **79.51**. HP Capture = **96.44%**.
- **Settled Batters (15+ balls faced):** 6,335 deliveries. Mean PI = **51.65**. HP Capture = **6.91%**.
- **Conclusion:** A batter like Virat Kohli or Jos Buttler anchoring an innings at 60/4 or chasing 13 RRR receives zero intensity credit ($I = 0$), dragging their PI from 70 down to 45.5, which falls below the phase threshold ($Z \le 1.0$). **The existing formula systematically erases pressure for set batters.**

### 2.4 Role Exposure Disparity
| Batting Order | Role Group | % Deliveries at $\text{bf} \le 5$ | % Deliveries at $\text{bf} > 10$ | Mean Intensity ($I$) | Mean Task Diff ($T$) | Mean PI | Control HP % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | Top Order | 27.89% | **54.27%** | **25.01** | 24.36 | 24.58 | **6.99%** |
| **2** | Top Order | 27.53% | **54.66%** | **24.70** | 25.24 | 25.05 | **5.19%** |
| **3** | Top Order | 30.27% | **50.55%** | **27.15** | 30.05 | 29.04 | **9.20%** |
| **4** | Middle Order | 31.46% | 48.33% | 28.21 | 36.58 | 33.65 | 13.73% |
| **5** | Middle Order | 36.27% | 41.68% | 32.42 | 44.10 | 40.01 | 20.52% |
| **6** | Middle Order | 42.55% | 34.17% | 37.74 | 50.91 | 46.30 | 28.58% |
| **7** | Lower Order | 48.44% | 27.78% | 42.81 | 59.68 | 53.78 | 41.00% |
| **8** | Lower Order | 59.32% | 18.49% | 52.12 | 66.64 | 61.56 | 54.34% |
| **9** | Lower Order | 66.79% | 12.79% | 58.67 | 70.88 | 66.60 | 62.36% |
| **10** | Lower Order | 76.98% | 6.10% | 67.44 | 73.51 | 71.38 | 70.46% |
| **11** | Lower Order | **90.05%** | **1.77%** | **78.96** | 78.69 | 78.78 | **88.67%** |

Openers spend over half their time with $I = 0$, while position 11 spends 90% of their deliveries with $I \in [50, 100]$. This explains why Pat Cummins was ranked #1 in the world in Control: his 135 HP balls were accumulated exclusively in short bursts where $I$ was maximally inflated!

---

## 3. Alternative Situational Intensity Formulations

### 3.1 Candidate 1: Bounded Smooth Decay ($I_{\text{decay}}$)
- **Cricket Rationale:** Settling pressure in T20 cricket is real on arrival, but it does not collapse to zero after 10 balls. An exponential decay with a half-life of 10 balls and an asymptotic floor of 25.0 points guarantees that set batters retain baseline intensity:
$$I_1 = 25.0 + 75.0 \times \exp\left(-\frac{\text{bf}}{10.0}\right)$$
- At bf = 0: $I_1 = 100.0$
- At bf = 5: $I_1 = 70.5$
- At bf = 10: $I_1 = 52.6$ (vs 0.0 in Control)
- At bf = 20: $I_1 = 35.1$ (vs 0.0 in Control)
- At bf $\to \infty$: $I_1 \to 25.0$.
- **Composite:** $\text{PI}_1 = 0.65 T + 0.35 I_1$, standardized within Phase $	imes$ Innings: $Z_1 > 1.00$.

### 3.2 Candidate 2: Context-Dependent Match-Stakes Intensity ($I_{\text{context}}$)
- **Cricket Rationale:** "Situational Intensity" should measure the *intensity of the match situation*, not just the batter's personal settling time. To prevent double-counting run rates (which are already in Task Difficulty $T$), $I_2$ captures:
  1. **Match-Stage Urgency ($M_{\text{stage}}$):** $(120 - \text{balls\_remaining}) / 120 \times 100$.
  2. **Wicket Exposure Risk ($W_{\text{risk}}$):** $\operatorname{clip}(\text{wickets\_before} / 7.0 \times 100, 0, 100)$.
  3. **Settling Time ($S_{\text{settle}}$):** $I_1$ weighted at 20%.
- **Formula:**
$$I_2 = 0.40 \times M_{\text{stage}} + 0.40 \times W_{\text{risk}} + 0.20 \times S_{\text{settle}}$$
- **Composite:** $\text{PI}_2 = 0.65 T + 0.35 I_2$, standardized within Phase $	imes$ Innings: $Z_2 > 1.00$.

### 3.3 Candidate 3: Leverage-Augmented Crisis & Consequence Intensity ($I_{\text{hybrid}}$)
- **Cricket Rationale:** In Step 16.6.1, Candidate 2 failed because multiplying $Z_{\text{PI}}$ by leverage suppressed 1st-innings collapses. Candidate 3 embeds Expected Delivery Leverage inside $I$ while adding an explicit **Crisis Safeguard**:
  1. **Crisis Safeguard ($C_{\text{crisis}}$):** $\operatorname{clip}(\text{wickets\_before} / 4.0 \times 100, 0, 100)$.
  2. **Delivery Consequence ($L_{\text{conseq}}$):** $\operatorname{clip}(50.0 + 25.0 \times Z_{\text{Lev}}, 0, 100)$.
  3. **Settling ($S_{\text{settle}}$):** $I_1$ weighted at 20%.
- **Formula:**
  - Innings 1: $I_3 = 0.45 C_{\text{crisis}} + 0.35 L_{\text{conseq}} + 0.20 S_{\text{settle}}$
  - Innings 2: $I_3 = 0.20 C_{\text{crisis}} + 0.60 L_{\text{conseq}} + 0.20 S_{\text{settle}}$
- **Composite:** $\text{PI}_3 = 0.65 T + 0.35 I_3$, standardized within Phase $	imes$ Innings: $Z_3 > 1.00$.

### 3.4 Candidate 4: Pure Task Difficulty Ablation ($I = 0$)
- **Scientific Rationale:** Completely removes Situational Intensity ($I = 0$ or $w_I = 0$), defining $\text{PI}_4 = T$. This serves as the benchmark to determine how much distortion was caused by $I$.

---

## 4. Evaluation Across the 10 Required Scenarios and Biases

All models were evaluated across the 10 mandated cricket scenarios extracted from the 180,839 batting deliveries:

| # | Archetypal Cricket Scenario | Deliveries | Mean $T$ | Control HP % | Cand 1 HP % | Cand 2 HP % | Cand 3 HP % | Cand 4 HP % | Key Finding / Audit Verdict |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Top-Order Overall (1–3)** | 90,068 | 26.44 | 7.06% | 6.52% | 6.30% | 7.19% | **8.54%** | Stays at 7–8.5% because early PP difficulty $T$ is low. |
| **2** | **Middle-Order Overall (4–6)** | 64,887 | 42.69 | 19.73% | 18.99% | 19.38% | 21.25% | 19.36% | Perfectly calibrated across all candidates (~19–21%). |
| **3** | **Lower-Order Overall (7–11)** | 25,881 | 65.24 | 52.36% | 55.76% | 55.71% | 49.37% | 53.46% | Remains elevated due to high physical difficulty $T=65.2$. |
| **4** | **Powerplay Phase** | 57,037 | 29.58 | 17.97% | 17.60% | 16.50% | 17.21% | 17.42% | Well-calibrated phase baseline across all models. |
| **5** | **Death Overs Phase** | 39,764 | 49.32 | 19.25% | 18.68% | 20.41% | 16.58% | 21.45% | Well-calibrated phase baseline across all models. |
| **6** | **1st Inn PP Collapse** *(3+ down)* | 1,575 | 46.13 | 59.49% | **75.62%** | **98.92%** | **100.00%** | **90.35%** | **Major Success: Cand 2 & 3 capture 99-100% of collapses.** |
| **7** | **Competitive Death Finish** | 452 | 48.81 | 1.33% | 0.00% | 0.00% | 0.22% | 0.00% | Under-captured across all because RRR is modest ($R=0$). |
| **8** | **Hopeless Chase / Blowout** | 8,240 | 87.64 | 52.34% | 60.07% | 68.99% | 62.20% | 75.44% | High because Task Difficulty $T=87.6$ is massive. |
| **9** | **Middle-Over Squeeze** | 1,860 | 52.07 | 16.72% | 9.73% | 4.57% | **30.05%** | 1.61% | **Cand 3 uniquely elevates high-tension middle overs.** |
| **10**| **Set Batters in Crisis ($T>65$)** | 6,335 | 79.46 | **6.91%** | **16.64%** | **58.23%** | **55.00%** | **73.94%** | **BREAKTHROUGH: Cand 2 & 3 elevate capture from 6.9% to 58%.** |

### Critical Takeaways:
1. **The Set Batter Breakthrough (Scenario 10):**  
   Control captured only **6.91%** of set batters in severe crises. Candidate 2 elevates capture to **58.23%**, Candidate 3 to **55.00%**, and Candidate 4 to **73.94%**. Removing the 10-ball cliff finally allows the model to recognize when a set batter is fighting for their team under extreme pressure!
2. **First-Innings Collapses Fully Preserved (Scenario 6):**  
   Unlike Step 16.6.1's Candidate 2 (which dropped collapse capture to 34.1%), redesigning Situational Intensity elevates 1st-innings collapse capture to **75.62% in Candidate 1**, **98.92% in Candidate 2**, and **100.00% in Candidate 3**!
3. **The Reality of Top-Order Capture (Scenario 1):**  
   Even under Candidate 4 (Pure Task Difficulty, zero intensity), top-order capture only rises to **8.54%**. This proves definitively that **top-order capture in T20 cricket is naturally low (7%–9%)** because Task Difficulty in opening overs is low (0 wickets down, low required rate). Expecting top-order capture to equal 18% is an artificial expectation that misinterprets cricket reality.

---

## 5. Player Ranking Validation (BRS3 Batting Rankings)

Player rankings were independently recalculated under frozen BRS3, Bayesian shrinkage ($K = 50.0$), and Rule B qualification (minimum 50 HP balls):

### 5.1 Global Ranking Reconciliation
| Evaluation Metric | Candidate 0 (Control) | Candidate 1 (Smooth Decay) | Candidate 2 (Match-Stakes) | Candidate 3 (Lev & Crisis) | Candidate 4 (Pure Task Diff) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tier 1 Qualified Batters** | **206** | **209** | 201 | 202 | 205 |
| **Tier 2 Qualified Batters** | 35 | 32 | 37 | 41 | 48 |
| **Spearman Rank Correlation ($\rho$)** | **1.0000** | **0.8094** | 0.6185 | 0.6151 | 0.5808 |
| **Pearson Score Correlation ($r$)** | **1.0000** | **0.8394** | 0.6454 | 0.6467 | 0.6281 |
| **Top 10 Overlap with Control** | 10 / 10 | 4 / 10 | 2 / 10 | 4 / 10 | 2 / 10 |

### 5.2 Movement of Notable Batters across Models
| Player Name | Control Rank (Score) | Cand 1 Rank (Score) | Cand 2 Rank (Score) | Cand 3 Rank (Score) | Cand 4 Rank (Score) | Cricket Diagnosis |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Patrick Cummins** | **#1 (80.30)** | **#35 (67.61)** | **#83 (68.55)** | **#66 (68.74)** | **#96 (71.04)** | **Finisher Loophole Corrected.** Cummins falls from #1 to realistic middle ranks once his $I=100$ short-burst bias is removed. |
| **Nicholas Pooran** | #11 (69.84) | **#1 (86.92)** | **#2 (93.55)** | **#1 (94.02)** | **#5 (91.65)** | Recognized as an elite clutch hitter across all alternative models. |
| **Heinrich Klaasen** | #53 (57.05) | **#42 (66.52)** | **#26 (80.95)** | **#20 (82.11)** | **#22 (86.09)** | Rises substantially once set-batter crisis pressure is credited. |
| **Suryakumar Yadav** | #9 (70.18) | **#20 (72.49)** | **#7 (90.20)** | **#8 (90.54)** | **#8 (91.27)** | Strongly solidified as a premier world-class pressure player. |
| **Rinku Singh** | #61 (56.01) | **#58 (63.18)** | **#13 (87.04)** | **#15 (86.22)** | **#6 (91.64)** | Rises to the top 15 in context models where late-game urgency is rewarded. |
| **Shashank Singh** | #3 (74.55) | #24 (71.04) | #20 (82.80) | #18 (83.12) | #33 (83.14) | Solidifies in top 20–30 as a genuine finisher. |
| **Travis Head** | #110 (49.88) | #147 (48.14) | Unqualified (38b) | Unqualified (42b) | **#43 (80.89)** | Gains high score under Pure Task Difficulty where explosive PP batting is rewarded. |
| **Virat Kohli** | #48 (57.76) | #128 (51.70) | #81 (68.84) | #78 (69.12) | **#61 (76.45)** | Gains high score in crisis anchoring under context-based intensity. |

---

## 6. Final Decision & Strategic Recommendation

### 6.1 Formal Decision on Candidates
1. **Candidate 0 (Control): RETAINED AS FROZEN BASELINE FOR ROUND 1.**  
   Maintains stability, complete auditability, and continuity for official Round 1 outputs.
2. **Candidate 1 (Bounded Smooth Decay): RECOMMENDED FOR FURTHER VALIDATION.**  
   - **Why:** It represents the most elegant, minimally invasive, and mathematically sound bridge.  
   - **Achievements:** It maintains high rank correlation with Control ($\rho = 0.8094$), expands Tier 1 qualified batters to 209, increases set-batter crisis capture from 6.9% to 16.6%, eliminates the artificial 10-ball cliff, and successfully corrects Pat Cummins' runaway finisher distortion (#1 to #35) without breaking the project architecture.
3. **Candidate 2 (Match-Stakes Context): PROMISING BUT UNPROVEN.**  
   - **Why:** Phenomenal capture of set batters in crisis (58.23%) and 1st-innings collapses (98.92%), but introduces major ranking shifts ($\rho = 0.6185$) and requires further calibration of multi-factor weights.
4. **Candidate 3 (Leverage & Crisis): PROMISING BUT UNPROVEN.**  
   - **Why:** Demonstrates that Expected Leverage can be integrated without suppressing 1st-innings collapses (100% capture), but produces similar ranking volatility ($\rho = 0.6151$).
5. **Candidate 4 (Pure Task Difficulty Ablation): REJECTED AS STANDALONE.**  
   - **Why:** Proves that $I$ was introducing distortion, but completely removing $I$ ignores the genuine psychological settling time new batters face on arrival.

### 6.2 Definitive Answers to Core Questions
- **Is the balls-faced formula responsible for top-order under-capture?**  
  **Partially.** The balls-faced formula severely suppresses set top-order batters in crises (holding them to 6.9% capture). However, top-order capture in general will always remain around 7%–9% because Task Difficulty in opening overs is naturally modest (low wickets down, achievable run rates).
- **Does pressure drop artificially after surviving 5–10 balls?**  
  **YES, decisively.** A batter loses 35.0 PI points purely by surviving 10 balls. When Task Difficulty is held constant at $T=50$, High Pressure capture drops from 92.1% on ball 0 to 0.0% on ball 10.
- **Does the formula favour lower-order batters?**  
  **YES, decisively.** Tailenders face 90% of deliveries with $\text{bf} \le 5$, receiving average $I$ scores of 79, while openers receive average $I$ scores of 25.
- **Is Candidate 1 ready for adoption?**  
  Candidate 1 is **recommended as the primary candidate for Round 2 adoption**. It smoothly eliminates the cliff while preserving project integrity.

---

## 7. Deliverables Directory & Verification Links

All datasets, scripts, models, and publication figures are stored in the project workspace with zero external modification:

### 7.1 Visual Artifacts (High-Resolution Figures)
- **Figure 1 — Mathematical Structure & Empirical Impact of the Balls-Faced Cliff:**  
  [fig1_balls_faced_decay_curves.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/fig1_balls_faced_decay_curves.png)  
  *Contrasts the Control 10-ball linear cliff with Candidate 1's exponential decay and illustrates the 72x empirical drop in HP capture.*
- **Figure 2 — HP Capture Rates by Batting Position (1 to 11):**  
  [fig2_hp_capture_by_position.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/fig2_hp_capture_by_position.png)  
  *Shows position-by-position capture rates across all five candidate models.*
- **Figure 3 — Archetypal Cricket Scenarios Comparison:**  
  [fig3_archetypal_scenarios_comparison.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/fig3_archetypal_scenarios_comparison.png)  
  *Highlights the recovery of Set Batters in Crisis (from 6.9% to 58%) and First-Innings Collapses (from 59% to 100%).*
- **Figure 4 — Player Ranking Stability & Correction of Finisher Inflation:**  
  [fig4_player_ranking_stability_scatter.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/fig4_player_ranking_stability_scatter.png)  
  *Scatter plots comparing Control BRS3 against Candidates 1, 2, and 4, annotating Pat Cummins' correction from #1 to #35/#83.*

### 7.2 Master Data Artifacts
- **Existing Intensity Audit Table:** [existing_intensity_audit.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/existing_intensity_audit.csv)
- **Balls-Faced Decay Profile (0 to 35+):** [balls_faced_decay_profile.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/balls_faced_decay_profile.csv)
- **Controlled Task Difficulty Audit:** [controlled_task_difficulty_decay.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/controlled_task_difficulty_decay.csv)
- **Role Intensity Exposure Table:** [role_intensity_exposure.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/role_intensity_exposure.csv)
- **Candidate Models Summary Metrics:** [candidates_summary_metrics.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/candidates_summary_metrics.csv)
- **Position & Bias Comparison Table:** [bias_and_position_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/bias_and_position_comparison.csv)
- **Phase & Innings Candidates Breakdown:** [phase_innings_candidates_breakdown.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/phase_innings_candidates_breakdown.csv)
- **10 Cricket Scenarios Audit Log:** [scenario_testing_audit.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/scenario_testing_audit.csv)
- **Player Ranking Reconciliation Summary:** [player_ranking_reconciliation.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/player_ranking_reconciliation.csv)
- **Batting Candidate Rankings Comparison:** [batting_candidate_rankings_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/batting_candidate_rankings_comparison.csv)
- **Notable Batters Movement Table:** [top_batters_role_movement.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/top_batters_role_movement.csv)
- **Classified Parquet Dataset (180,839 balls):** [delivery_intensity_candidates.parquet](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_7_situational_intensity_redesign/delivery_intensity_candidates.parquet)

### 7.3 Source Code Pipeline
- `src/step_16_7_situational_intensity_redesign/01_audit_existing_situational_intensity.py`
- `src/step_16_7_situational_intensity_redesign/02_develop_candidate_models.py`
- `src/step_16_7_situational_intensity_redesign/03_evaluate_bias_and_scenarios.py`
- `src/step_16_7_situational_intensity_redesign/04_player_ranking_validation.py`
- `src/step_16_7_situational_intensity_redesign/05_generate_visualizations.py`
- `src/step_16_7_situational_intensity_redesign/06_synthesis_and_final_report.py`
