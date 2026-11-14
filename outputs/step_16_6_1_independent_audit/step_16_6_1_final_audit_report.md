# Step 16.6.1 — Independent Audit of Leverage-Integrated Pressure Index

**Date:** November 14, 2026  
**Audit Status:** Complete, Audited & Verified  
**Audit Target:** Step 16.6 Leverage-Integrated Pressure Index (Specifically Candidate 2: Multiplicative Gating)  
**Dataset Population:** 188,097 Clean Active Deliveries across 789 T20 Matches  
**Deliverables Directory:** [outputs/step_16_6_1_independent_audit/](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit)

---

## 1. Executive Summary & Audit Verdict

### 1.1 Objective
This independent audit rigorously evaluates the methodology, mathematical implementation, behavioral edge cases, and player ranking impact of the experimental Pressure Index candidates proposed in Step 16.6, with primary focus on **Candidate 2 (Multiplicative Gating)**:

$$Z_2 = \operatorname{Std}\left( Z_{\text{PI}} \cdot \left[ 1.0 + 0.50 \tanh(Z_{\text{Lev}}) \right] \right)$$

The audit's central objective is to determine whether Candidate 2 represents a **genuine improvement in identifying difficult and match-consequential cricket situations**, or whether it merely shifts the distribution of high-pressure deliveries while introducing new, unaddressed failure modes.

### 1.2 Formal Audit Verdict
**Candidate 2 is formally classified as: PROMISING BUT UNPROVEN (REJECTED FOR ROUND 1 ADOPTION).**

While Candidate 2 is mathematically elegant and successfully purges ~1,556 pure blowout garbage-time deliveries from lower-order tailenders, **it fails as a replacement for the canonical Pressure Index**. Crucially, it introduces severe false negatives in first-innings collapses (cutting capture of 3+ down crises from 59.5% to 34.1%), remains mathematically incapable of solving top-order exposure under-capture, and produces sample-size boundary instability for qualifying players.

### 1.3 Executive Summary Table: Candidate Evaluation Matrix
| Evaluation Dimension | Candidate 0 (Control) | Candidate 1A (Additive 70/30) | Candidate 2 (Multiplicative Gated) | Audit Assessment |
| :--- | :---: | :---: | :---: | :--- |
| **Implementation Concordance** | 100.00% (Baseline) | 100.00% Verified | 100.00% Verified | Fully verified down to machine precision. |
| **Total Batting HP Capture** | 18.09% (32,708) | 16.40% (29,655) | 17.52% (31,681) | Well-calibrated population capture (~17.5%). |
| **Top Order (1–3) HP %** | **7.06%** | **6.22%** | **7.22%** | **Zero material change. Top-order remains trapped.** |
| **Lower Order (7–11) HP %** | **52.36%** | **43.78%** | **47.02%** | **Genuine reduction of 5.34% lower-order false positives.** |
| **1st Innings Collapse Capture** | **59.49%** (937 balls) | **35.30%** (556 balls) | **34.10%** (537 balls) | **CRITICAL FLAW: Cuts crisis capture nearly in half.** |
| **Dead-Rubber Blowout Capture** | **52.34%** (4,313 balls) | **35.30%** (2,909 balls) | **41.77%** (3,442 balls) | **Modest improvement: Trims 871 hopeless chase balls.** |
| **Competitive Death Finish HP %** | **1.33%** (6 balls) | **48.67%** (220 balls) | **18.58%** (84 balls) | **Major improvement over Control in tight finishes.** |
| **Batting Rank Correlation ($\rho$)** | 1.0000 | 0.7638 | 0.7967 | Robust overall rank preservation. |
| **Bowling Rank Correlation ($\rho$)** | 1.0000 | 0.7561 | 0.8148 | Robust overall rank preservation. |
| **Tier 1 Batters Qualified** | **206** | 189 | **204** | Preserves 99% of qualified batter sample. |

---

## 2. Verification of Implementation

### 2.1 Independent Recalculation and Concordance Audit
Every delivery classification was recalculated from source CSVs (`delivery_match_state.csv` and `delivery_pressure_index.csv`) across all 188,097 clean deliveries without importing Step 16.6 intermediate tables as truth.

The audit verified:
1. **Raw Pressure Index Fidelity:** Exact machine-precision match with raw source tables (maximum absolute difference = $0.00000000$).
2. **Frozen Step 16 Z-Scores:** Re-derived from raw Batting_PI and Bowling_PI within the six Phase $	imes$ Innings baselines. Maximum absolute difference vs Step 16 frozen baseline = $0.00000000e+00$.
3. **Delivery Population Masks:**
   - Total clean deliveries: **188,097**
   - Batting population (`is_batter_ball_faced == 1`): **180,839**
   - Bowling population (`is_legal_ball == 1`): **180,041**
   - Wides (not faced by batter): **7,258**
   - No-balls / Extras (not legal bowling balls): **8,056**
4. **Candidate Delivery-Level Concordance:**
   - Candidate 0 Batting: **100.0000% match** (0 mismatches / 180,839)
   - Candidate 1A Batting: **100.0000% match** (0 mismatches / 180,839)
   - Candidate 1B Batting: **100.0000% match** (0 mismatches / 180,839)
   - Candidate 2 Batting: **100.0000% match** (0 mismatches / 180,839)
   - Candidate 3 Batting: **100.0000% match** (0 mismatches / 180,839)
   - Bowling Candidates 0, 1A, 1B, 2, 3: **100.0000% match** (0 mismatches / 180,041)

### 2.2 Standardization Scope: Phase $	imes$ Innings vs. Global
We investigated whether Candidate 2's final standardization was performed within Phase $	imes$ Innings strata or globally across the full population:
- **Phase $	imes$ Innings Standardization (Implemented in Step 16.6):** Yields 31,681 HP batting deliveries (17.52%). Phase capture is evenly spread: PP = 16.49%, Middle = 17.67%, Death = 18.67%.
- **Global Standardization (Alternative):** Yields 30,536 HP deliveries (16.89%). Phase capture drops to 15.67% in PP and 16.97% in Middle, while concentrating in Death (18.45%).
- **Audit Finding:** Standardizing within Phase $	imes$ Innings is **methodologically correct and necessary**. It honors the foundational design principle of Step 16, preventing death overs from re-accumulating structural capture advantages over early overs.

---

## 3. Audit of the 0.50 Multiplier Parameter

In Step 16.6, the multiplier $m = 0.50$ in the gating factor $g_m(Z_{\text{Lev}}) = 1.0 + m \tanh(Z_{\text{Lev}})$ was introduced as an empirical parameter. We conducted an independent sensitivity sweep across $m \in [0.20, 0.35, 0.50, 0.65, 0.80]$ to determine whether $0.50$ is defensible:

### 3.1 Multiplier Sensitivity Sweep Results
| Multiplier ($m$) | Batting HP % | Top Order (1–3) HP % | Lower Order (7–11) HP % | Batting Tier 1 Qualified | Batting Spearman $\rho$ | Bowling Tier 1 Qualified | Bowling Spearman $\rho$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.00 (Control)** | 18.09% | 7.06% | 52.36% | 206 | 1.0000 | 174 | 1.0000 |
| **0.20** | 18.33% | 7.20% | 51.26% | 207 | 0.9413 | 173 | 0.9503 |
| **0.35** | 18.15% | 7.21% | 49.67% | 205 | 0.8695 | 166 | 0.9202 |
| **0.50 (Cand 2)** | **17.52%** | **7.22%** | **47.02%** | **204** | **0.7967** | **160** | **0.8148** |
| **0.65** | 15.78% | 6.73% | 40.95% | 180 | 0.6859 | 152 | 0.7162 |
| **0.80** | 14.13% | 6.67% | 33.63% | 161 | 0.5805 | 148 | 0.6639 |

### 3.2 Audit Findings on Multiplier Defensibility
1. **Inflection Point / "Knee of the Curve":**  
   The parameter $m = 0.50$ is an **optimal upper bound**. At $m \le 0.35$, the dampening effect on lower-order false positives is trivial (capture remains $\ge 49.7\%$). However, as soon as $m > 0.50$, the system experiences severe non-linear degradation:
   - At $m = 0.65$, Tier 1 qualified batters plunge from 204 to 180 (loss of 24 players), and rank correlation breaks below the 0.70 stability threshold ($\rho = 0.6859$).
   - At $m = 0.80$, Tier 1 qualified batters collapse to 161 (loss of 45 players), and correlation disintegrates to $\rho = 0.5805$.
2. **Defensibility Conclusion:**  
   If a multiplicative gating formulation is adopted, **$m = 0.50$ is mathematically defensible**. It maximizes lower-order filtering while preserving 99% of qualified players and maintaining robust rank stability ($\rho \approx 0.80$). Values above $0.50$ are destructive and must be rejected.

---

## 4. Deep Investigation of Lower-Order Demotions

Step 16.6 reported that Candidate 2 reduced lower-order (positions 7–11) HP capture from 52.36% to 47.02%. We isolated and audited all **6,436 deliveries demoted from High Pressure** by Candidate 2 to evaluate whether this improvement is genuine.

### 4.1 Match State Distribution of Demoted Deliveries
| Win Probability Segment | Demoted Balls Count | % of Demoted Deliveries | Mean Leverage | Mean Batting PI | Mean $Z_{\text{PI}}$ | Mean $Z_2$ | % Lower Order (7–11) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Pure Blowouts ($WP < 5\%$ or $> 95\%$)** | **1,556** | **24.18%** | **0.17%** | **65.91** | **1.21** | **0.82** | **52.96%** |
| **2. One-Sided ($WP \in [5, 20)\%$ or $(80, 95]\%$)** | **2,586** | **40.18%** | **0.61%** | **58.90** | **1.27** | **0.82** | **37.24%** |
| **3. Competitive ($WP \in [20, 40)\%$ or $(60, 80]\%$)** | **1,679** | **26.09%** | **0.95%** | **51.16** | **1.26** | **0.84** | **23.70%** |
| **4. Parity/Clutch ($WP \in [40, 60]\%$)** | **615** | **9.56%** | **1.26%** | **47.69** | **1.12** | **0.89** | **0.00%** |
| **Total Demoted Population** | **6,436** | **100.00%** | **0.66%** | **57.50** | **1.23** | **0.83** | **33.95%** |

### 4.2 Audit Verdict on Lower-Order Demotions
1. **The Genuine Improvement (Blowouts):**  
   In 1,556 deliveries (24.18% of demotions), the game was a total blowout ($WP < 5\%$ or $> 95\%$), with mean delivery leverage of only **0.17%**. More than half of these balls were faced by tailenders (positions 7–11) batting in hopeless chases (e.g. 50/7 in over 13 needing 130). Stripping these deliveries is an **unambiguous, verified improvement**.
2. **The Unintended Collateral Damage (Competitive Demotions):**  
   However, **2,294 demoted deliveries (35.64%) occurred in competitive or parity match states ($WP \in [20\%, 80\%]$)**.
   - For these deliveries, mean PI was 50.2 ($Z_{\text{PI}} \approx 1.22$).
   - They were demoted because their delivery leverage was slightly below the phase average ($Z_{\text{Lev}} \approx -0.70$), which depressed the gating multiplier ($g \approx 0.70$), dragging $Z_2$ just below the 1.0 threshold ($Z_2 \approx 0.85$).
   - While 44.2% were borderline deliveries ($Z_{\text{PI}} \le 1.15$), a substantial subset represents legitimate, hard-fought cricket deliveries that were stripped of high pressure status.

---

## 5. Deep Investigation of Top-Order Under-Capture

Step 16.6 observed that top-order (positions 1–3) High Pressure capture remained pinned at ~7.2% across all candidates. This audit investigated the exact mathematical and structural root causes behind this persistent stagnation.

### 5.1 Mathematical Proof of Candidate 2 Sign Constraint
In Candidate 2:
$$S_2 = Z_{\text{PI}} \cdot \left[ 1.0 + 0.50 \tanh(Z_{\text{Lev}}) \right]$$

Since $\tanh(x) \in (-1, 1)$, the gating multiplier $g(Z_{\text{Lev}}) = 1.0 + 0.50 \tanh(Z_{\text{Lev}})$ is **strictly bounded in $(0.50, 1.50)$ and is ALWAYS POSITIVE**.

Consequently:
$$\operatorname{sign}(S_2) \equiv \operatorname{sign}(Z_{\text{PI}})$$

- If $Z_{\text{PI}} \le 0$, then **$S_2 \le 0$ ALWAYS**, regardless of how extreme the delivery leverage is!
- Across the 90,068 Top-Order deliveries:
  - **71.87% (64,730 deliveries) have $Z_{\text{PI}} \le 0$**!
  - 10.60% (9,545 deliveries) have elite leverage ($Z_{\text{Lev}} > 1.0$).
  - **5,948 deliveries have elite leverage ($Z_{\text{Lev}} > 1.0$) BUT negative difficulty ($Z_{\text{PI}} \le 0$)**.
  - **Mathematical Proof:** In Candidate 2, because $g(Z_{\text{Lev}}) > 0$, **not a single one of those 5,948 high-leverage deliveries can ever achieve $S_2 > 0$, making it mathematically impossible for them to be promoted to High Pressure ($Z_2 > 1.0$)!**

### 5.2 The True Driver: Balls Faced Collapse in Situational Intensity
Analyzing top-order deliveries across balls faced (`striker_balls_faced_before`) reveals why $Z_{\text{PI}}$ is overwhelmingly negative:

```
Top-Order Deliveries by Balls Faced:
Striker Balls Faced   Total Balls   Mean PI   Mean Z_PI   Mean Leverage   Control HP %   Cand 2 HP %
1. 0–5 balls           25,676        42.79     +0.493        1.482%          24.06%         24.85%
2. 6–15 balls          29,161        21.59     -0.755        1.314%           0.40%          0.12%
3. 16–30 balls         23,240        16.11     -0.898        1.149%           0.04%          0.06%
4. 31+ balls           11,991        20.92     -0.758        1.199%           0.43%          0.62%
```

- When an opener has faced **$\le 5$ balls**, Situational Intensity is elevated by the "new batter" term, capturing **24.06% HP balls**.
- The moment the opener faces **6 to 15 balls**, Situational Intensity drops dramatically. Mean PI collapses from 42.79 to 21.59 ($Z_{\text{PI}} = -0.755$), and High Pressure capture plunges to **0.40%**!
- From balls 16 to 30, HP capture is **0.04%** (virtually zero).
- **Audit Conclusion:** Top-order under-capture is **100% caused by the internal design of the Situational Intensity formula and the Phase baseline mean**, not by win probability leverage. Attempting to fix top-order under-capture via leverage integration is a fundamental category error.

---

## 6. Audit of Cricket Scenarios and Full-Population Edge Cases

### 6.1 Verification of Step 16.6 Scenarios
All seven Step 16.6 scenarios were traced back to their raw delivery records in the dataset:
- Scenario 1 (Steep Chase PP, 0/0, RRR 10.9): Jason Roy, $PI = 61.54$, $Z_{\text{PI}} = 1.32$, $Z_2 = 1.04$. **Verified HP in both.**
- Scenario 2 (Comfortable Chase, 78/1, RRR 4.3): Nicholas Pooran, $PI = 14.81$, $Z_{\text{PI}} = -1.06$, $Z_2 = -0.62$. **Verified Low in both.**
- Scenario 3 (Tight Death Chase, 141/5, RRR 12.0): Rahul Tewatia, $PI = 34.88$, $Z_{\text{PI}} = -0.51$, $Z_2 = -0.78$. **Verified Low in both.**
- Scenario 4 (1st Innings Collapse, 10/3 in over 4.1): Eoin Morgan, $PI = 69.68$, $Z_{\text{PI}} = 2.48$, $Z_2 = 1.39$. **Verified HP in both.**
- Scenario 5 (Middle Hopeless Collapse, 55/6 in over 12.2): Odean Smith, $PI = 94.22$, $Z_{\text{PI}} = 2.52$, $Z_2 = 1.65$. **Verified HP in both.**
- Scenario 6 (Parity Routine Single, 69/1 in over 10.1): Brandon King, $PI = 31.22$, $Z_{\text{PI}} = -0.32$, $Z_2 = -0.47$. **Verified Low in both.**
- Scenario 7 (Hopeless Tailender, 132/8 in over 19.2): Romario Shepherd, $PI = 59.80$, $Z_{\text{PI}} = 0.51$, $Z_2 = 0.50$. **Verified Low in both.**

### 6.2 Full-Population Systematic Category Audit
To prevent selection bias from hand-picked examples, we executed a full-population query across six critical archetypal categories:

| Archetypal Match Category | Total Deliveries | Mean PI | Mean $Z_{\text{PI}}$ | Mean Leverage | Control HP % | Cand 1A HP % | Cand 2 HP % | Audit Assessment |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Category A: 1st Innings Collapse**<br>*(Inn 1, PP, 3+ wkts down, e.g. 20/3)* | 1,575 | 48.78 | +1.184 | 1.040% | **59.49%** | **35.30%** | **34.10%** | **FATAL FLAW: Cand 2 cuts crisis capture from 59.5% to 34.1%.** |
| **Category B: Lost-Cause Chase**<br>*(Inn 2, Ov 13+, WP < 5%, RRR > 12)* | 8,240 | 70.50 | +1.070 | 0.356% | **52.34%** | **35.30%** | **41.77%** | **Partial success: Trims 871 garbage-time balls.** |
| **Category C: Competitive Death Finish**<br>*(Inn 2, Ov 18+, WP 30-70%, rem <= 12)* | 452 | 44.30 | -0.125 | 14.627% | **1.33%** | **48.67%** | **18.58%** | **Substantial improvement over Control's severe under-capture.** |
| **Category D: Tight Middle Squeeze**<br>*(Inn 2, Ov 10-16, WP 40-60%, RRR 9-12)* | 1,860 | 43.61 | +0.197 | 2.951% | **16.72%** | **36.51%** | **26.34%** | **Meaningful capture increase in high-tension middle overs.** |
| **Category E: High Lev / Low Difficulty**<br>*(Z_Lev > 1.5 but Z_PI < 0)* | 1,333 | 33.62 | -0.298 | 6.872% | **0.00%** | **10.80%** | **0.00%** | **Candidate 2 completely rejects high leverage if difficulty is low.** |
| **Category F: High Difficulty / Low Lev**<br>*(Z_PI > 1.0 but Z_Lev < -1.0)* | 8,584 | 68.17 | +1.754 | 0.435% | **100.00%** | **48.87%** | **56.49%** | **Filters out 43.5% of low-consequence task difficulty.** |

### 6.3 The Case Study of Match 13511: The England 10/3 False Negative
The audit uncovered a definitive false negative demonstrating Candidate 2's vulnerability:
- **Match 13511 (England vs West Indies):**  
  In the 4th over of the Powerplay, England collapsed to **10/3**. James Vince and Eoin Morgan faced hostile bowling from Sheldon Cottrell and Jason Holder.
- **Control Classification:** Batting PI was $54.83\text{--}57.63$ ($Z_{\text{PI}} = 1.56\text{--}1.73$). **Classified as HIGH PRESSURE.**
- **Candidate 2 Behavior:** Delivery leverage was only $0.91\%\text{--}1.03\%$ ($Z_{\text{Lev}} = -1.02\text{--}-1.40$).  
  Why? Because win probability models assign lower delivery leverage when a team's win probability has already collapsed to $24\%$!  
  The gating multiplier collapsed to $0.56\times$, pulling $Z_2$ down to $0.85\text{--}0.90$.
- **Result:** **Candidate 2 demoted Eoin Morgan and James Vince batting at 10/3 in the 4th over to LOW PRESSURE.**  
  Stripping high-pressure status from international batters fighting an early collapse is cricket nonsense.

---

## 7. Independent Player Ranking Reconciliation

Player rankings were independently recalculated under frozen BRS3, BoRS, Bayesian shrinkage ($K = 50$), and Rule B qualification (minimum 50 HP balls).

### 7.1 Global Ranking Reconciliation
| Evaluation Metric | Candidate 0 (Control) | Candidate 1A (Additive 70/30) | Candidate 2 (Multiplicative Gated) |
| :--- | :---: | :---: | :---: |
| **Batting Tier 1 Qualified Players** | **206** | 189 | **204** |
| **Batting Tier 2 Qualified Players** | 35 | 31 | 28 |
| **Batting Spearman Rank Correlation ($\rho$)** | **1.0000** | 0.7638 | **0.7967** |
| **Batting Score Pearson ($r$)** | **1.0000** | 0.7825 | **0.8062** |
| **Batting Top 10 Overlap with Control** | 10 / 10 | 5 / 10 | 5 / 10 |
| **Bowling Tier 1 Qualified Players** | **174** | 162 | **160** |
| **Bowling Tier 2 Qualified Players** | 16 | 20 | 21 |
| **Bowling Spearman Rank Correlation ($\rho$)** | **1.0000** | 0.7561 | **0.8148** |
| **Bowling Score Pearson ($r$)** | **1.0000** | 0.7855 | **0.8310** |
| **Bowling Top 10 Overlap with Control** | 10 / 10 | 6 / 10 | 6 / 10 |

### 7.2 Diagnostic Audit of Key Player Movements

#### 1. Mahendra Singh Dhoni (#18 $\to$ #1 in Batting):
- **Observation:** MS Dhoni rises from Rank 18 (Score 66.98) to **Rank 1 in the world (Score 78.80)**.
- **Audit Diagnosis:** Candidate 2 demoted 39 of Dhoni's HP deliveries. In those 39 demoted balls, **Dhoni's strike rate was only 69.2**! These were hopeless chases where CSK required $>15$ RRR and Dhoni batted conservatively. Stripping those 39 low-leverage balls caused his HP strike rate to surge, vaulting him to #1. This ranking change is **empirically justified**.

#### 2. Vijay Shankar (#5 $\to$ #119 in Batting):
- **Observation:** Vijay Shankar falls from Rank 5 (Score 73.95) to **Rank 119 (Score 47.09)**.
- **Audit Diagnosis:** Shankar accumulated high PI in several runaway games where his strike rate was 188.9. In Candidate 2, he gained 34 balls in competitive chases where his performance was mediocre, diluting his clutch differential. This ranking shift is **empirically justified**.

#### 3. Patrick Cummins (#1 $\to$ #13 in Batting):
- **Observation:** Pat Cummins falls from Rank 1 (Score 80.30) to Rank 13 (Score 67.26).
- **Audit Diagnosis:** Cummins lost 25 deliveries where his strike rate was 220.0 (high-PI slogs in decided games). In competitive situations, his sample size shrunk from 135 to 116 balls.

#### 4. Boundary Disqualification Casualties:
- **Ottneil Baartman (Bowling):** Ranked #14 in Control (Score 69.98, 51 HP balls). In Candidate 2, he lost 21 balls to demotion, leaving him with only 30 HP balls. He was **completely excluded from Tier 1 and Tier 2 rankings**.
- **Sarfaraz Khan (Batting):** Ranked #17 in Control (Score 67.56, 58 HP balls). In Candidate 2, he lost 11 balls, dropping to 49 balls and **missing Tier 1 qualification by a single ball**.

---

## 8. Final Verdict & Answers to Mandated Questions

### Question 1: Is Candidate 2 implemented correctly?
**Answer: YES.**  
The implementation was independently reproduced with **100.0000% concordance** across all 180,839 batting deliveries and 180,041 bowling deliveries. The standardization within Phase $	imes$ Innings was executed with flawless numerical fidelity.

### Question 2: Is the 0.50 multiplier defensible?
**Answer: YES, as an optimal upper bound.**  
Our sensitivity sweep ($m \in [0.20, 0.80]$) proved that $m = 0.50$ is the exact mathematical inflection point. Values below $0.35$ produce negligible dampening, while values above $0.50$ trigger rapid sample collapse, rank correlation breakdown ($\rho < 0.68$), and mass player disqualifications.

### Question 3: Does Candidate 2 genuinely reduce misleading lower-order pressure capture?
**Answer: YES, partially.**  
It successfully purges 1,556 pure blowout deliveries ($WP < 5\%$ or $> 95\%$, mean leverage $0.17\%$) where tailenders accumulated inflated PI scores. However, in severe lost-cause chases (Category B), 41.77% of deliveries still remain classified as High Pressure because their raw difficulty ($PI > 70$) overwhelms the gating multiplier.

### Question 4: Does it preserve genuine first-innings and top-order pressure?
**Answer: NO. This is Candidate 2's primary failure.**  
- **First-Innings Collapses Severely Punished:** In Category A (1st Innings Collapses, 3+ down in PP), Candidate 2 **slashes capture from 59.49% down to 34.10%**, demoting genuine crises (like England 10/3 in Match 13511) to Low Pressure.
- **Top-Order Stagnation:** Due to the mathematical sign constraint ($S_2 \le 0$ when $Z_{\text{PI}} \le 0$), Candidate 2 cannot promote a single one of the 5,948 high-leverage top-order deliveries, leaving top-order capture frozen at 7.22%.

### Question 5: Are its player ranking changes justified?
**Answer: MIXED.**  
While individual adjustments like MS Dhoni (+17 ranks) and Vijay Shankar ($-114$ ranks) correctly strip garbage-time statistics, players on the sample-size boundary (such as Ottneil Baartman and Sarfaraz Khan) suffer arbitrary disqualification, and batters who rebuild in first-innings collapses are unfairly penalized.

### Question 6: Is Candidate 2 better than the original PI overall?
**Answer: NO.**  
While Candidate 2 successfully cures lower-order garbage-time inflation, it does so by introducing an equally severe flaw: **the systematic suppression of first-innings collapses**. It trades finisher bias for first-innings collapse erasure, while completely failing to address top-order exposure under-capture.

---

## 9. Deliverables Directory & Artifact Links

All scripts, datasets, sensitivity logs, and publication figures are stored in isolated workspace directories:

### 9.1 Visual Artifacts (High-Resolution Figures)
- **Figure 1 — Multiplier Sensitivity Sweep:**  
  [fig1_multiplier_sensitivity.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/fig1_multiplier_sensitivity.png)  
  *Traces HP capture rates, Tier 1 player qualifications, and Spearman correlations across $m \in [0.00, 0.80]$.*
- **Figure 2 — Match State Anatomy of Demoted Deliveries:**  
  [fig2_demoted_deliveries_distribution.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/fig2_demoted_deliveries_distribution.png)  
  *Highlights the win probability and leverage profiles of the 24% pure blowouts vs 35% competitive balls demoted.*
- **Figure 3 — Top-Order Mathematical Sign Constraint:**  
  [fig3_top_order_leverage_vs_pi.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/fig3_top_order_leverage_vs_pi.png)  
  *Scatter plot demonstrating why 5,948 high-leverage top-order deliveries remain mathematically trapped in $S_2 \le 0$.*
- **Figure 4 — Player Ranking Movement Diagnostics:**  
  [fig4_candidate2_vs_control_rankings.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/fig4_candidate2_vs_control_rankings.png)  
  *Visualizes rank movements for the top 20 batters and bowlers, highlighting Dhoni's rise and Shankar's decline.*

### 9.2 Independent Audit Datasets
- **Recalculated Concordance Table:**  
  [recalculated_candidates_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/recalculated_candidates_comparison.csv)
- **Multiplier Sensitivity Sweep Data:**  
  [multiplier_sensitivity_analysis.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/multiplier_sensitivity_analysis.csv)  
  [multiplier_position_breakdown.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/multiplier_position_breakdown.csv)
- **Demoted Deliveries Investigation:**  
  [demoted_deliveries_investigation.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/demoted_deliveries_investigation.csv)  
  [demoted_competitive_deliveries_sample.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/demoted_competitive_deliveries_sample.csv)
- **Top-Order Under-Capture Investigation:**  
  [top_order_capture_investigation.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/top_order_capture_investigation.csv)  
  [top_order_strata_breakdown.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/top_order_strata_breakdown.csv)
- **Scenario Recalculation Verification:**  
  [scenario_recalculation_verification.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/scenario_recalculation_verification.csv)
- **Population Categories Audit & Case Studies:**  
  [population_categories_audit.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/population_categories_audit.csv)  
  [category_case_studies.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/category_case_studies.csv)
- **Player Ranking Reconciliation & Diagnostics:**  
  [player_ranking_reconciliation.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/player_ranking_reconciliation.csv)  
  [batter_rank_movement_diagnostics.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/batter_rank_movement_diagnostics.csv)  
  [bowler_rank_movement_diagnostics.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_16_6_1_independent_audit/bowler_rank_movement_diagnostics.csv)

### 9.3 Independent Audit Scripts
- `src/step_16_6_1_independent_audit/01_verify_implementation.py`
- `src/step_16_6_1_independent_audit/02_audit_multiplier_sensitivity.py`
- `src/step_16_6_1_independent_audit/03_investigate_lower_order_demotions.py`
- `src/step_16_6_1_independent_audit/04_investigate_top_order_under_capture.py`
- `src/step_16_6_1_independent_audit/05_audit_scenarios_and_real_deliveries.py`
- `src/step_16_6_1_independent_audit/06_reconcile_player_rankings.py`
- `src/step_16_6_1_independent_audit/07_generate_audit_visualizations.py`
- `src/step_16_6_1_independent_audit/08_synthesis_and_audit_report.py`
