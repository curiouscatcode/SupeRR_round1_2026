# Step 16.6 — Expected Leverage Integration into Pressure Index: Final Report

**Date:** November 14, 2026  
**Status:** Completed & Audited  
**Deliverable Type:** Empirical Investigation, Methodology Comparison & Strategic Recommendation  
**Dataset Scope:** 188,097 Clean Active Deliveries across 789 T20 Matches  
**Outputs Directory:** [outputs/step_16_6_leverage_integration/](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration)

---

## 1. Executive Summary

### 1.1 Objective & Context
Step 16.6 investigates whether incorporating **Expected Delivery Leverage** (derived from the pre-delivery Win Probability model developed in Step 16.5 and audited in Step 16.5.1) improves the existing **Pressure Index (PI)** and the phase-relative Z-score classification established in Step 16.

The central research hypothesis was:  
*Can combining situational task difficulty (how hard the situation is for the player) with match consequence (how much the delivery affects the final match outcome) eliminate false-positive pressure in lost causes, correct top-order vs. lower-order capture imbalances, and enhance player clutch evaluation without distorting the established project framework?*

### 1.2 Candidate Classification Matrix
Five distinct methodologies were implemented, standardized, and evaluated side-by-side across all 188,097 clean deliveries:

| Candidate | Mathematical Formulation | Batting HP Capture | Bowling HP Capture | Batting Rank $ho$ vs Control | Bowling Rank $ho$ vs Control | Final Assessment |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Candidate 0 (Control)** | Frozen Step 16 Phase $	imes$ Innings PI ($Z_{\text{PI}} > 1.0$) | 18.09% (32,708) | 17.52% (31,550) | 1.0000 | 1.0000 | **RETAINED (Baseline)** |
| **Candidate 1A (Additive 70/30)** | $Z_{1\text{A}} = \text{Std}(0.70 Z_{\text{PI}} + 0.30 Z_{\text{Lev}}) > 1.0$ | 16.40% (29,655) | 16.15% (29,083) | 0.7631 | 0.7637 | **Promising (Secondary)** |
| **Candidate 1B (Additive 50/50)** | $Z_{1\text{B}} = \text{Std}(0.50 Z_{\text{PI}} + 0.50 Z_{\text{Lev}}) > 1.0$ | 12.77% (23,102) | 13.41% (24,148) | 0.4890 | 0.5464 | **REJECTED (Destructive)** |
| **Candidate 2 (Multiplicative Gated)** | $Z_{2} = \text{Std}(Z_{\text{PI}} \cdot [1.0 + 0.50 \tanh(Z_{\text{Lev}})]) > 1.0$ | 17.52% (31,681) | 15.92% (28,655) | 0.7919 | 0.8226 | **Most Defensible Formulation** |
| **Candidate 3 (Convex Composite)** | $Z_{3} = \text{Std}(\text{Dual Elevation Composite}) > 1.0$ | 13.36% (24,157) | 13.67% (24,606) | 0.5406 | 0.5765 | **REJECTED (Destructive)** |

### 1.3 Key Empirical Findings
1. **Leverage Does NOT Solve Top-Order Batting Under-Capture:**  
   Across all candidates, top-order (positions 1–3) High Pressure (HP) capture remains virtually locked: **7.06% in Control**, **6.22% in 1A**, **6.83% in 1B**, **7.22% in 2**, and **7.04% in 3**. In early overs, win probability is anchored near 50%, and expected delivery leverage is bounded (mean ~1.3%). Normalizing leverage within phase preserves this low capture.
2. **Leverage Successfully Filters Lost Causes and Garbage Time:**  
   In Control, lower-order batters (positions 7–11) captured 52.36% HP balls, often in dead-rubber blowouts (e.g., 50/7 in over 13). Candidates 1A and 2 reduce lower-order capture to 43.78% and 47.02%, systematically demoting 6,436–8,658 deliveries whose mean leverage was only 0.66%–0.68% ($WP < 3\%$ or $> 97\%$).
3. **Equal Weighting (50/50 & Convex) Breaks Cricket Realities:**  
   Candidate 1B and Candidate 3 fail catastrophically: they disqualify over 55 qualified batters from Tier 1, crush rank stability ($\rho < 0.55$), and demote genuine 1st-innings crises (e.g. 30/3 in PP over 5) to Low Pressure because early 1st-innings leverage is mathematically low.
4. **Candidate 2 is the Best Formulation If Leverage Is Integrated:**  
   By treating situational task difficulty as the primary signal and match consequence as an adaptive gating multiplier, Candidate 2 achieves the highest rank stability ($\rho = 0.792$ bat, $\rho = 0.823$ bowl), preserves 204 Tier 1 batters (vs 206 Control), filters blowout deliveries, and correctly flags genuine 1st-innings collapses.
5. **Definitive Strategic Recommendation:**  
   **Retain Candidate 0 (Control Step 16 Phase $	imes$ Innings PI) for Round 1 player evaluation.** Leverage and Pressure Index represent fundamentally orthogonal dimensions: PI measures *how hard the task is for the player*, while Leverage measures *how much the match equity hinges on the delivery*. Conflating them dilutes both signals and fails to address top-order position exposure. Expected Leverage should be preserved as an independent, complementary dimension in Round 2.

---

## 2. Audit of Expected Leverage Input & Baseline Characteristics

### 2.1 Pre-Delivery Purity & Leakage Audit
The Expected Delivery Leverage metric ($L_t$) was audited across all 188,097 clean deliveries to verify complete independence from delivery outcomes:
- **Feature Set:** Inputs to $L_t$ consist exclusively of pre-delivery match state: innings, balls remaining, runs required (or current score), wickets lost, target, current run rate, required run rate, and phase transition probability matrices.
- **Outcome Isolation:** Neither delivery runs, extras, wicket events, dismissed player identities, nor post-delivery win probability changes ($WPA_t$) are used in calculating $L_t$.
- **Temporal Integrity:** Fully causal; zero forward-looking leakage.

### 2.2 Correlation Analysis: Multicollinearity Disproven
A common theoretical question is whether Expected Leverage merely duplicates the existing Pressure Index. Empirical correlation analysis demonstrates that they are virtually orthogonal:

| Metric Pair | Correlation Coefficient ($r$) | R-squared ($r^2$) | Interpretation |
| :--- | :---: | :---: | :--- |
| Expected Leverage vs. Raw Batting PI | $+0.0167$ | $0.0003$ | Completely Orthogonal |
| Expected Leverage vs. Batting PI Z-score | $-0.0522$ | $0.0027$ | Independent Signals |
| Expected Leverage vs. Raw Bowling PI | $-0.0582$ | $0.0034$ | Completely Orthogonal |
| Expected Leverage vs. Bowling PI Z-score | $-0.0601$ | $0.0036$ | Independent Signals |
| Expected Leverage vs. Required Run Rate | $+0.0934$ | $0.0087$ | Low Correlation |
| Expected Leverage vs. Wickets Lost | $-0.0784$ | $0.0061$ | Slight Negative (Blowout Dampening) |

The near-zero correlation ($r \approx -0.05$) proves that Expected Delivery Leverage captures an entirely distinct facet of the match environment. Pressure Index captures **immediate task difficulty**, while Leverage captures **match outcome sensitivity**.

### 2.3 Leverage Distribution Across 12 Phase $	imes$ Innings Strata
The full population distribution of Expected Delivery Leverage exhibits a right-skewed profile:
- **Full Population:** Mean = $1.341\%$, Median = $1.145\%$, IQR = $0.644\%$, Min = $0.000\%$, Max = $15.820\%$.

```
Phase x Innings Leverage Breakdown (Mean / Median / IQR):
- Innings 1 Powerplay:  Mean = 1.362%, Median = 1.258%, IQR = 0.404%
- Innings 1 Middle:     Mean = 0.903%, Median = 0.812%, IQR = 0.456%
- Innings 1 Death:      Mean = 1.139%, Median = 0.985%, IQR = 0.697%
- Innings 2 Powerplay:  Mean = 1.442%, Median = 1.348%, IQR = 0.518%
- Innings 2 Middle:     Mean = 1.332%, Median = 1.157%, IQR = 0.771%
- Innings 2 Death:      Mean = 2.536%, Median = 2.124%, IQR = 2.592%
```

Innings 2 Death overs exhibit nearly double the average delivery leverage ($2.54\%$) of any other phase, driven by close finishes where every ball shifts win probability by $5\%\text{--}15\%$.

---

## 3. Mathematical Methodology of Experimental Candidates

All candidates were normalized using the frozen Step 16 Phase $	imes$ Innings baseline methodology to preserve apples-to-apples comparability.

### 3.1 Candidate 0: Control Baseline
$$Z_{\text{PI}} = \frac{\text{PI} - \mu_{\text{PI}}(\text{phase}, \text{innings})}{\sigma_{\text{PI}}(\text{phase}, \text{innings})}$$
- **Classification:** High Pressure if $Z_{\text{PI}} > 1.00$.

### 3.2 Candidate 1A: Additive 70/30 (Task Difficulty Primary)
$$S_{1\text{A}} = 0.70 \cdot Z_{\text{PI}} + 0.30 \cdot Z_{\text{Lev}}$$
$$Z_{1\text{A}} = \frac{S_{1\text{A}} - \mu(S_{1\text{A}})}{\sigma(S_{1\text{A}})}$$
- **Rationale:** Preserves situational task difficulty as the dominant 70% signal while using 30% match consequence to break ties and downweight irrelevant balls.
- **Classification:** High Pressure if $Z_{1\text{A}} > 1.00$.

### 3.3 Candidate 1B: Additive 50/50 (Equal Weighting)
$$S_{1\text{B}} = 0.50 \cdot Z_{\text{PI}} + 0.50 \cdot Z_{\text{Lev}}$$
$$Z_{1\text{B}} = \frac{S_{1\text{B}} - \mu(S_{1\text{B}})}{\sigma(S_{1\text{B}})}$$
- **Rationale:** Treats the physical difficulty of the delivery and its match importance as equal co-determinants of pressure.
- **Classification:** High Pressure if $Z_{1\text{B}} > 1.00$.

### 3.4 Candidate 2: Multiplicative Gated Interaction
$$G(Z_{\text{Lev}}) = 1.0 + 0.50 \cdot \tanh(Z_{\text{Lev}})$$
$$S_{2} = Z_{\text{PI}} \cdot G(Z_{\text{Lev}})$$
$$Z_{2} = \frac{S_{2} - \mu(S_{2})}{\sigma(S_{2})}$$
- **Rationale:** Pressure cannot exist without task difficulty. High leverage in an easy situation (e.g. singles at 5 RRR) does not create pressure. However, low leverage ($Z_{\text{Lev}} < -1.5$, blowout) should damp task difficulty, while high leverage ($Z_{\text{Lev}} > 2.0$, tight chase) should amplify it. The bounded $\tanh$ multiplier smoothly scales between $0.50\times$ and $1.50\times$.
- **Classification:** High Pressure if $Z_{2} > 1.00$.

### 3.5 Candidate 3: Convex Composite (Dual-Elevation Model)
$$S_{3} = \sqrt{\max(0, Z_{\text{PI}})^2 + \max(0, Z_{\text{Lev}})^2} - \sqrt{\max(0, -Z_{\text{PI}})^2 + \max(0, -Z_{\text{Lev}})^2}$$
$$Z_{3} = \frac{S_{3} - \mu(S_{3})}{\sigma(S_{3})}$$
- **Rationale:** Requires non-linear elevation in both task difficulty and consequence to achieve elite pressure status, penalizing deliveries that are strong in only one attribute.
- **Classification:** High Pressure if $Z_{3} > 1.00$.

---

## 4. Comprehensive Comparative Analysis

### 4.1 Batting Order Position Analysis (Positions 1–11)
A primary project goal was investigating whether leverage resolves the severe disparity between top-order (7.06% HP capture) and lower-order (52.36% HP capture) batting deliveries.

| Batting Order | Role Group | Balls Faced | Mean PI | Mean Lev | Control HP % | Cand 1A HP % | Cand 1B HP % | Cand 2 HP % | Cand 3 HP % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | Top Order | 30,762 | 24.6 | 1.37% | 6.99% | 6.40% | 7.70% | 7.15% | 7.81% |
| **2** | Top Order | 31,253 | 25.1 | 1.29% | 5.19% | 4.81% | 5.50% | 5.97% | 5.71% |
| **3** | Top Order | 28,053 | 29.0 | 1.24% | 9.20% | 7.60% | 7.37% | 8.68% | 7.66% |
| **4** | Middle Order | 26,905 | 33.7 | 1.29% | 13.73% | 13.80% | 13.07% | 14.15% | 13.06% |
| **5** | Middle Order | 21,701 | 40.0 | 1.38% | 20.52% | 21.17% | 18.27% | 21.44% | 18.32% |
| **6** | Middle Order | 16,281 | 46.3 | 1.50% | 28.58% | 27.11% | 21.33% | 27.92% | 21.68% |
| **7** | Lower Order | 11,713 | 53.8 | 1.47% | 41.00% | 34.62% | 22.12% | 36.75% | 23.44% |
| **8** | Lower Order | 6,787 | 61.6 | 1.44% | 54.34% | 45.06% | 24.66% | 48.75% | 27.60% |
| **9** | Lower Order | 4,020 | 66.6 | 1.19% | 62.36% | 50.47% | 21.69% | 54.88% | 26.79% |
| **10** | Lower Order | 2,346 | 71.4 | 1.08% | 70.46% | 58.61% | 22.21% | 63.81% | 28.90% |
| **11** | Lower Order | 1,015 | 78.8 | 1.16% | 88.67% | 80.10% | 32.81% | 84.04% | 41.97% |
| **Summary 1–3** | **Top Order** | **90,068** | **26.1** | **1.30%** | **7.06%** | **6.22%** | **6.83%** | **7.22%** | **7.04%** |
| **Summary 4–6** | **Middle Order**| **64,887** | **39.0** | **1.37%** | **19.73%** | **19.60%** | **16.88%** | **20.04%** | **16.98%** |
| **Summary 7–11**| **Lower Order**| **25,881** | **60.4** | **1.37%** | **52.36%** | **43.78%** | **23.15%** | **47.02%** | **26.27%** |

#### Crucial Insights on Position Capture:
1. **Top-Order Stagnation:** Integrating leverage **fails to elevate top-order capture**. Across all 4 experimental candidates, top-order capture stays pinned between 6.22% and 7.22%. As proven in Step 16.4.1, top-order under-capture is caused by batter balls faced and the low situational intensity of opening overs, which leverage cannot artificially inflate.
2. **Lower-Order Dampening:** Candidate 1A successfully trims lower-order capture from 52.36% to 43.78%, while Candidate 2 reduces it to 47.02%. The demotions occur almost exclusively in dead matches where tailenders bat out meaningless deliveries.
3. **Over-Suppression in 1B & 3:** Candidate 1B (23.15%) and Candidate 3 (26.27%) over-correct, cutting lower-order HP capture in half. This strips out legitimate death-overs finishes where tailenders are under intense pressure to score.

### 4.2 Phase & Innings Balance
The distribution of HP deliveries across the 6 phase $	imes$ innings segments reveals major operational divergence:

```
Batting High-Pressure Capture Rate (%):
Segment           Control    Cand 1A    Cand 1B    Cand 2     Cand 3
Innings 1 PP      19.28%     14.56%      9.74%     15.28%     10.61%
Innings 1 Mid     18.18%     18.35%     15.49%     17.96%     15.27%
Innings 1 Death   19.72%     17.67%     12.86%     18.37%     13.02%
Innings 2 PP      16.66%     13.37%     11.42%     17.70%     11.90%
Innings 2 Mid     17.03%     16.80%     14.71%     17.38%     15.95%
Innings 2 Death   18.60%     16.97%      8.41%     19.09%      9.70%
```

- In Control, every phase captures ~16%–19% HP balls due to phase-relative normalization.
- Candidates 1B and 3 collapse Innings 1 PP capture to under 10% and Innings 2 Death to 8.41%, heavily distorting phase representation.
- Candidate 2 preserves balanced representation: PP (15.3%–17.7%), Middle (17.4%–18.0%), and Death (18.4%–19.1%).

### 4.3 Bowling Phase Representation
Bowling HP capture across phases remains well-calibrated under Candidate 2 and 1A, but collapses under 1B and 3:

| Bowling Phase | Total Deliveries | Control HP % | Cand 1A HP % | Cand 1B HP % | Cand 2 HP % | Cand 3 HP % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay** | 56,796 | 18.01% (10,231) | 17.32% (9,838) | 15.14% (8,600) | 15.50% (8,803) | 16.03% (9,106) |
| **Middle Overs** | 83,786 | 17.28% (14,475) | 15.60% (13,071) | 13.89% (11,637) | 15.69% (13,144) | 14.01% (11,742) |
| **Death Overs** | 39,459 | 17.34% (6,844) | 15.65% (6,174) | 9.91% (3,911) | 17.00% (6,708) | 9.52% (3,758) |

Under Candidates 1B and 3, Death over bowling HP capture plunges from 17.34% to 9.52%–9.91%, arbitrarily punishing death bowlers whose deliveries occur in moderate-equity situations.

### 4.4 Promotion and Demotion Anatomy
Analyzing the exact balls that changed classification between Control and Candidates 1A / 2 confirms the underlying mechanics:

- **Promoted Deliveries (New HP Balls in Cand 1A, n=5,605):**
  - Mean Expected Leverage: **$3.28\%$** (vs full population mean of $1.34\%$).
  - Mean Batting PI: $49.2$ ($Z_{\text{PI}} = 0.69$).
  - Mean Wickets Lost: $2.89$.
  - 62.1% occur in Innings 2 (tight run chases).
  - 30.7% occur in Top Order (positions 1–3).
  - *Profile:* High-stakes deliveries in competitive run-chases where the raw required rate was not extreme, but the game was on the line.
- **Demoted Deliveries (Dropped from HP in Cand 1A, n=8,658):**
  - Mean Expected Leverage: **$0.68\%$** (extremely low match consequence).
  - Mean Batting PI: $59.5$ ($Z_{\text{PI}} = 1.26$).
  - Mean Wickets Lost: $3.85$.
  - 34.5% occur in Lower Order (positions 7–11).
  - *Profile:* Dead-rubber situations, lost-cause chases (e.g. chasing 180 at 70/8), where raw PI was high due to high RRR or early balls faced, but win probability was virtually $0\%$.

---

## 5. Revisit of Original Project Flaws

Step 16 identified four structural flaws in pressure classification. We assess how leverage integration impacts each:

### 5.1 Finisher Bias
- **Status:** **Partially Mitigated.**
- In Control, finishers and tailenders accumulated disproportionate HP deliveries (52.36% for positions 7–11). Candidates 1A and 2 trim this to 43.78%–47.02% by removing low-leverage tailender garbage time. However, finishers in genuine close finishes rightly retain high pressure.

### 5.2 Death-Bowler Bias
- **Status:** **Resolved in Step 16 Phase Normalization; Unchanged by Leverage.**
- Step 16 phase-relative Z-scores already equalized Death over capture (~17.3%). Candidates 1A and 2 maintain this balance (~15.7%–17.0%). Candidates 1B and 3 over-penalize death overs (collapsing to ~9.7%), introducing an anti-death-bowler distortion.

### 5.3 Top-Order Wicket Pressure Under-Capture
- **Status:** **UNRESOLVED by Leverage.**
- The expectation that Win Probability leverage would automatically recognize top-order pressure when early wickets fall proved empirically false. In early overs, win probability curves remain relatively flat because teams have 80–100 balls to recover. Consequently, early collapse deliveries have leverage of only ~1.5%–2.5%, insufficient to elevate top-order capture from ~7%.

### 5.4 Bowling Workload Loophole
- **Status:** **Unaffected.**
- Bowling workload volume is governed by the $K=50$ Bayesian shrinkage prior and Rule B (50 HP balls minimum), which remain completely frozen.

---

## 6. Audit of 7 Representative Cricket Scenarios

We tested all five candidates against seven archetypal cricket scenarios extracted directly from the 188,097-ball dataset:

| # | Scenario Description | Control ($Z_0$) | Cand 1A ($Z_{1\text{A}}$) | Cand 1B ($Z_{1\text{B}}$) | Cand 2 ($Z_2$) | Cand 3 ($Z_3$) |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **PP Parity:** Innings 1, Over 2.1, Score 12/0, PI=21.2, Lev=1.42% | Low ($-0.63$) | Low ($-0.39$) | Low ($-0.17$) | Low ($-0.63$) | Low ($-0.22$) |
| **2** | **1st Innings Collapse:** Innings 1, Over 4.3, Score 30/3, PI=45.8, Lev=1.12% | **HIGH ($1.17$)** | Low ($0.88$) | Low ($0.51$) | **HIGH ($1.05$)** | Low ($0.53$) |
| **3** | **Middle-Overs Squeeze:** Innings 2, Over 12.0, RRR=10.5, 4 down, PI=48.2, Lev=2.15% | **HIGH ($1.03$)** | **HIGH ($1.18$)** | **HIGH ($1.12$)** | **HIGH ($1.15$)** | **HIGH ($1.11$)** |
| **4** | **Death Overs Thriller:** Innings 2, Over 19.2, Need 8 off 4, PI=58.4, Lev=5.84% | **HIGH ($1.06$)** | **HIGH ($1.89$)** | **HIGH ($2.43$)** | **HIGH ($1.78$)** | **HIGH ($2.39$)** |
| **5** | **Dead Rubber Blowout:** Innings 2, Over 13.0, Score 50/7, Need 130 off 42, PI=52.1, Lev=0.12% | **HIGH ($1.13$)** | Low ($0.66$) | Low ($0.11$) | Low ($0.54$) | Low ($0.12$) |
| **6** | **Middle Parity Single:** Innings 1, Over 11.2, Score 82/2, PI=26.4, Lev=0.91% | Low ($-0.12$) | Low ($-0.15$) | Low ($-0.14$) | Low ($-0.12$) | Low ($-0.16$) |
| **7** | **Steep Chase Pressure:** Innings 2, Over 16.0, Need 48 off 24, PI=52.3, Lev=3.10% | **HIGH ($1.19$)** | **HIGH ($1.45$)** | **HIGH ($1.43$)** | **HIGH ($1.48$)** | **HIGH ($1.42$)** |

### Critical Takeaways from Scenario Audit:
1. **The Failure of Candidates 1B and 3 on Scenario 2:**  
   In Scenario 2 (First Innings Collapse at 30/3 in Over 5), an incoming batter faces enormous situational difficulty. Control correctly classifies this as High Pressure ($Z = 1.17$). Candidate 2 also preserves it ($Z = 1.05$). However, Candidates 1B ($Z = 0.51$) and 3 ($Z = 0.53$) **demote this crisis to Low Pressure** because delivery leverage in early 1st innings is historically low. This proves that equal weighting of leverage is fatal to cricket intuition.
2. **The Success of Candidate 2 on Scenario 5:**  
   In Scenario 5 (Dead Rubber Blowout at 50/7 in Over 13), the match is completely over ($WP < 0.1\%$). Control mistakenly flagged this as High Pressure ($Z = 1.13$) due to high RRR and wickets fallen. Candidate 2 correctly demotes it to Low Pressure ($Z = 0.54$).
3. **Amplification in Close Finishes (Scenario 4 & 7):**  
   In genuine thrillers (Scenario 4, need 8 off 4), Candidate 2 elevates the pressure score from $Z = 1.06$ to $Z = 1.78$, reflecting true match tension.

---

## 7. Player Ranking Impact on BRS3 and BoRS

Using the frozen BRS3, BoRS, Bayesian $K=50$, and Rule B qualification criteria, player rankings were recalculated across all candidates to evaluate stability:

### 7.1 Global Ranking Stability Metrics
| Evaluation Metric | Candidate 0 (Control) | Candidate 1A (Additive 70/30) | Candidate 1B (Additive 50/50) | Candidate 2 (Gated Multiplier) | Candidate 3 (Convex Composite) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Batting Tier 1 Qualified Players** | **206** | 189 | 148 | **204** | 155 |
| **Batting Spearman Rank Correlation ($\rho$)** | **1.0000** | 0.7631 | 0.4890 | **0.7919** | 0.5406 |
| **Batting Score Pearson ($r$)** | **1.0000** | 0.7728 | 0.4997 | **0.8014** | 0.5501 |
| **Batting Top 10 Overlap with Control** | **10 / 10** | 5 / 10 | 2 / 10 | **5 / 10** | 3 / 10 |
| **Bowling Tier 1 Qualified Players** | **174** | 162 | 143 | **160** | 142 |
| **Bowling Spearman Rank Correlation ($\rho$)** | **1.0000** | 0.7637 | 0.5464 | **0.8226** | 0.5765 |
| **Bowling Score Pearson ($r$)** | **1.0000** | 0.7904 | 0.5670 | **0.8345** | 0.6087 |
| **Bowling Top 10 Overlap with Control** | **10 / 10** | 6 / 10 | 5 / 10 | **6 / 10** | 5 / 10 |

### 7.2 Movement Among Control Top 10 Batters
| Control Rank | Player Name | Control BRS3 | Cand 1A Rank (Score) | Cand 1B Rank (Score) | Cand 2 Rank (Score) | Cand 3 Rank (Score) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | Patrick Cummins | 79.09 | #16 (65.67) | #58 (58.99) | #13 (68.49) | #66 (58.82) |
| **2** | Shashank Singh | 75.52 | #12 (66.49) | #40 (62.99) | #7 (72.18) | #12 (72.07) |
| **3** | Jitesh Sharma | 74.89 | #2 (74.12) | #16 (70.22) | #6 (72.50) | #28 (65.66) |
| **4** | Vijay Shankar | 74.04 | #32 (61.57) | #91 (53.58) | #115 (49.60) | #58 (60.57) |
| **5** | Cameron Green | 72.64 | #4 (72.89) | #37 (63.39) | #5 (72.51) | #8 (75.93) |
| **6** | Jamie Overton | 72.62 | #6 (71.31) | Unqualified (60.24) | #3 (73.56) | Unqualified (73.17) |
| **7** | Angkrish Raghuvanshi | 72.01 | Unqualified (62.59) | Unqualified (54.53) | #35 (60.85) | Unqualified (57.87) |
| **8** | William Jacks | 71.51 | #1 (77.06) | #4 (75.95) | #9 (71.53) | #6 (78.30) |
| **9** | Suryakumar Yadav | 71.15 | #10 (69.63) | #1 (86.97) | #12 (68.53) | #1 (88.00) |
| **10** | Nicholas Pooran | 70.65 | #19 (65.22) | #64 (58.73) | #14 (66.71) | #45 (62.46) |

### 7.3 Movement Among Control Top 10 Bowlers
| Control Rank | Player Name | Control BoRS | Cand 1A Rank (Score) | Cand 1B Rank (Score) | Cand 2 Rank (Score) | Cand 3 Rank (Score) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | Nasum Ahmed | 84.04 | #4 (82.71) | #11 (77.35) | #2 (87.11) | #11 (74.35) |
| **2** | Brad Evans | 81.31 | #12 (70.90) | Unqualified (71.71) | #16 (69.04) | Unqualified (76.89) |
| **3** | Haris Rauf | 77.40 | #11 (71.09) | #20 (72.39) | #9 (73.32) | #16 (71.93) |
| **4** | Mark Wood | 77.10 | #3 (85.51) | Unqualified (88.34) | #1 (88.37) | Unqualified (87.45) |
| **5** | Tim Southee | 75.82 | #1 (86.94) | #1 (95.27) | #5 (79.16) | #1 (94.84) |
| **6** | Keshav Maharaj | 75.39 | #32 (65.60) | #64 (56.67) | #23 (66.50) | #37 (64.43) |
| **7** | Junaid Siddique | 74.80 | #9 (73.05) | #8 (77.99) | #18 (68.71) | #5 (80.39) |
| **8** | Shoriful Islam | 74.32 | #5 (78.31) | #3 (83.73) | #8 (74.33) | #9 (77.86) |
| **9** | Mark Adair | 73.97 | #26 (67.21) | #6 (80.03) | #24 (66.06) | #7 (78.74) |
| **10** | Harshit Rana | 72.37 | #2 (86.27) | #2 (88.74) | #3 (82.55) | #2 (84.75) |

### 7.4 Key Ranking Observations
1. **Severe Sample Attrition under 1B and 3:** Candidate 1B eliminates 58 qualified batters and 31 bowlers from Tier 1; Candidate 3 eliminates 51 batters and 32 bowlers. Players like Jamie Overton, Angkrish Raghuvanshi, Brad Evans, and Mark Wood fail the 50-ball HP qualification threshold solely due to the collapse in HP deliveries.
2. **Robust Stability of Candidate 2:** Candidate 2 preserves 204 of 206 Tier 1 batters and maintains $\rho = 0.792$ (batting) and $\rho = 0.823$ (bowling). Established clutch performers like Cameron Green (#5), Jitesh Sharma (#6), Shashank Singh (#7), and William Jacks (#9) remain solidly in the top 10.
3. **The Case of Vijay Shankar:** Vijay Shankar drops from #4 (Control) to #115 (Candidate 2). Inspection reveals that Shankar accumulated high PI in several runaway chases where match leverage was below 0.3%. When those lost-cause balls are filtered, his high-pressure sample shrinks and his clutch differential adjusts.

---

## 8. Final Recommendation & Strategic Guidance

### 8.1 Definitive Answer to the Central Question
**Should Expected Delivery Leverage be integrated into the Pressure Index for Round 1 player evaluation?**

**Answer: NO.**  
While integrating Expected Delivery Leverage (specifically via Candidate 2) successfully purges lost-cause blowouts and garbage-time stats, **it does not solve the fundamental top-order wicket pressure challenge**, and it conflates two conceptually distinct cricket phenomena.

### 8.2 Strategic Rationale
1. **Orthogonality of Difficulty vs Consequence:**  
   - **Task Difficulty (PI):** Measures the tactical and environmental resistance faced by the player (e.g. required run rate, balls faced, field restrictions, pitch phase).  
   - **Match Consequence (Leverage / WPA):** Measures the sensitivity of the team's final win probability to the outcome of that ball.  
   Blending them into a single index compromises the purity of both signals. A top-order batter navigating a hostile spell at 20/2 in the 4th over is under enormous tactical difficulty, regardless of whether a win probability model assigns low immediate delivery leverage due to 96 balls remaining.
2. **Top-Order Under-Capture Is Not a Leverage Problem:**  
   Step 16.6 proves that leverage cannot elevate top-order capture from 7% to parity. As demonstrated in Step 16.4.1, top-order capture is driven by batter balls faced and phase baseline distributions. Solving it requires adjustments to the Situational Intensity formula or baseline definitions, not win probability.
3. **Integrity of Frozen Round 1 Baseline:**  
   The Step 16 Phase $	imes$ Innings normalized Pressure Index (Control / Candidate 0) provides a robust, fully audited, and stable baseline for Round 1. Changing the core PI definition at this stage would invalidate extensive validation work and introduce sample qualification instability.

### 8.3 Recommended Roadmap for Round 2
1. **Retain Candidate 0 (Step 16 Control) for Round 1 Rankings:**  
   Maintain the frozen BRS3, BoRS, Bayesian $K=50$, Rule B, and Step 16 Phase $	imes$ Innings PI Z-score.
2. **Preserve Candidate 2 (Multiplicative Gating) as the Approved Bridge Formulation:**  
   If project leadership ultimately mandates leverage integration in future iterations, **Candidate 2 is the only mathematically and empirically viable candidate**. Candidates 1A, 1B, and 3 must remain permanently rejected.
3. **Deploy Expected Leverage as an Independent Dimension in Round 2:**  
   Rather than fusing PI and Leverage into a single metric, evaluate players on a two-dimensional grid:
   - **X-Axis:** Performance under High Task Difficulty (PI Z > 1.0).
   - **Y-Axis:** Performance under High Match Consequence (Expected Leverage Z > 1.0 or Top Quartile Leverage).  
   This preserves analytical transparency and allows talent scouts to distinguish "Difficult Situation Masters" from "High-Stakes Finishers".

---

## 9. Deliverables Directory & Artifact Links

All datasets, scripts, models, and publication figures are stored in the project workspace with zero external modification:

### 9.1 Publication Figures (Visual Artifacts)
- **Figure 1 — Batting Position Capture Comparison:**  
  [fig1_hp_capture_by_batting_position.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/fig1_hp_capture_by_batting_position.png)  
  *Illustrates HP capture rates across batting positions 1–11, highlighting the lower-order dampening achieved by Candidates 1A and 2.*
- **Figure 2 — Phase Representation by Candidate:**  
  [fig2_phase_representation_by_candidate.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/fig2_phase_representation_by_candidate.png)  
  *Compares phase-by-innings HP capture percentages, demonstrating the collapse of 1B and 3 and the stability of Candidate 2.*
- **Figure 3 — Cricket Scenario Z-Score Profiles:**  
  [fig3_cricket_scenario_comparison.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/fig3_cricket_scenario_comparison.png)  
  *Visualizes candidate behavior across the 7 archetypal match scenarios, highlighting the preservation of Scenario 2 and demotion of Scenario 5.*
- **Figure 4 — Player Ranking Stability Scatterplots:**  
  [fig4_ranking_scatter_control_vs_candidates.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/fig4_ranking_scatter_control_vs_candidates.png)  
  *Displays Spearman rank correlation scatterplots for batting and bowling, showing high fidelity in Candidate 2 vs severe distortion in 1B.*

### 9.2 Data Artifacts & Comparative CSVs
- **Classified Deliveries (188,097 balls):**  
  [delivery_candidates_classified.parquet](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/delivery_candidates_classified.parquet)
- **Candidate Summary Metrics:**  
  [candidates_summary_metrics.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/candidates_summary_metrics.csv)
- **Batting Position Comparison Table:**  
  [batting_position_candidate_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/batting_position_candidate_comparison.csv)
- **Phase & Innings Breakdown:**  
  [phase_innings_candidate_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/phase_innings_candidate_comparison.csv)
- **Bowling Phase Breakdown:**  
  [bowling_phase_candidate_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/bowling_phase_candidate_comparison.csv)
- **Promotion & Demotion Characteristics:**  
  [promotion_demotion_characteristics.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/promotion_demotion_characteristics.csv)
- **Scenario Audit Log:**  
  [scenario_classification_audit.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/scenario_classification_audit.csv)
- **Player Ranking Correlation Summary:**  
  [player_ranking_correlation_summary.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/player_ranking_correlation_summary.csv)
- **Batting Candidate Rankings Comparison:**  
  [batting_candidate_rankings_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/batting_candidate_rankings_comparison.csv)
- **Bowling Candidate Rankings Comparison:**  
  [bowling_candidate_rankings_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/bowling_candidate_rankings_comparison.csv)
- **Top 10 Movement Audit:**  
  [top10_movement_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/top10_movement_comparison.csv)
- **Input Audit & Correlation Analysis:**  
  [leverage_input_audit.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/leverage_input_audit.csv)  
  [leverage_vs_pi_components_correlation.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_leverage_integration/leverage_vs_pi_components_correlation.csv)

### 9.3 Source Code Pipeline
- `src/step_16_6_leverage_integration/01_audit_leverage_and_baseline.py`
- `src/step_16_6_leverage_integration/02_develop_experimental_candidates.py`
- `src/step_16_6_leverage_integration/03_evaluate_phase_innings_position_bias.py`
- `src/step_16_6_leverage_integration/04_audit_cricket_scenarios.py`
- `src/step_16_6_leverage_integration/05_player_ranking_impact.py`
- `src/step_16_6_leverage_integration/06_generate_visualizations.py`
- `src/step_16_6_leverage_integration/07_synthesis_and_final_report.py`
