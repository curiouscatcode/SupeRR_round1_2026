# Step 12: Experimental Ranking Model Development — Comprehensive Synthesis Report

## Executive Summary

Step 12 develops, executes, and rigorously validates four independent experimental improvements to the SupeRR Selector player reliability ranking engine. Following the adversarial findings of Step 11 and their independent validation in Step 11.2, this phase evaluates whether principled adjustments to metric composition, bowling containment, Bayesian priors, and qualification criteria improve the identification of clutch T20 performers.

In strict adherence to experimental isolation boundaries:
- The audited production baseline (Model 0 / v2.0) remains 100% untouched.
- All four experiments were executed independently in sequence without combining parameters into a unified model.
- Time-aware chronological predictive validation across 789 matches was utilized to prevent look-ahead bias and information leakage.

### High-Level Summary of Findings & Verdicts

| Experiment | Focus Area | Mathematical Formulation | Macro Rank Stability ($\rho$) | Top 10 Overlap | Out-of-Sample Predictive Impact | Final Verdict & Recommendation |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **12.1 Batting Formula** | Eliminates Strike Rate & Boundary Execution collinearity ($r=0.9628$) | $\text{BRS}_3 = 0.45(\text{SR}) + 0.35(\text{Surv}) + 0.20(\text{Diff})$ | **0.9885** (Tier 1)<br>**0.9818** (All 816) | **10/10 (100%)** | Restores Survival Rate share from 19.8% to 31.7%; eliminates double-reward on boundary sloggers. | **KEEP (Strong Candidate)** |
| **12.2 Bowling Containment** | Recognizes dot-ball pressure and boundary suppression across all bowlers | $\text{BoRS}_{\text{Contain}} = 0.40(\text{Econ}) + 0.15(\text{Wk}) + 0.30(\text{Contain}) + 0.15(\text{Diff})$ | **0.9502** (Tier 1)<br>**0.9634** (All 589) | **9/10 (90%)** | Explains 92.9% of economy variance; naturally elevates Bumrah (+10 ranks to #14) and Theekshana (into Top 10). | **KEEP (Strong Candidate)** |
| **12.3 Cohort Priors** | Evaluates role-specific Bayesian priors (Top vs Middle; Pace vs Spin) | $\theta^* = \lambda \hat{\theta} + (1-\lambda) \mu_{\text{Cohort}}$ with $K=50$ | **0.9996** (Bat)<br>**0.9987** (Bowl) | **10/10 (Bat)**<br>**10/10 (Bowl)** | Out-of-sample RMSE worsens in batting (33.05 $\to$ 33.59) and is identical in bowling (2.06 $\to$ 2.06). | **REJECT** |
| **12.4 Qualification** | Investigates 60-ball boundary cliff & estimation uncertainty | Dual-Criteria: $N \ge 60 \lor (N \ge 50 \land M \ge 6)$ | **0.9942** (Common)<br>Expands T1 | Admits Overton (#6) & Nasum (#2) | Statistical SE at 59b vs 60b differs by only 0.01 pts; dual-criteria admits 30 batters & 17 bowlers with high match breadth. | **KEEP (Strong Candidate)** |

---

## 1. Summary of the Four Experiments

### Experiment 12.1 — Three-Component Batting Formula
- **Objective:** Address the statistical collinearity between Strike Rate and Boundary Execution ($r = 0.9628$ in Tier 1, $r = 0.9638$ across all 816 batters), which caused combined scoring speed to dominate **68.06%** of effective BRS variance and relegated Survival Rate to 19.80%.
- **Formula Tested:**
  $$\text{BRS}_3 = 0.45 \cdot \text{Score}_{\text{SR}} + 0.35 \cdot \text{Score}_{\text{Surv}} + 0.20 \cdot \text{Score}_{\text{Diff}}$$
- **Outputs Created:**
  - Script: [`exp12_1_batting_formula.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/step_12_experimental_models/exp12_1_batting_formula.py)
  - Full Rankings CSV: [`exp12_1_batting_rankings.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_1_batting_formula/exp12_1_batting_rankings.csv)
  - Tier 1 Comparison CSV: [`exp12_1_batting_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_1_batting_formula/exp12_1_batting_comparison.csv)
  - Visual Chart: [`01_exp12_1_batting_formula.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_1_batting_formula/01_exp12_1_batting_formula.png)
  - Validation Report: [`exp12_1_batting_formula_report.md`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_1_batting_formula/exp12_1_batting_formula_report.md)

### Experiment 12.2 — Bowling Containment & Pressure Induction
- **Objective:** Investigate whether the official bowling formula adequately values bowlers who restrict scoring without accumulating raw wickets, and test a generalized containment index without ad-hoc player-specific adjustments.
- **Formula Tested:**
  $$\text{BoRS}_{\text{Contain}} = 0.40 \cdot \text{Score}_{\text{Econ}} + 0.15 \cdot \text{Score}_{\text{Wk}} + 0.30 \cdot \text{Score}_{\text{Contain}} + 0.15 \cdot \text{Score}_{\text{Diff}}$$
  where $\text{Score}_{\text{Contain}} = 0.50 \cdot \text{Score}_{\text{Dot}} + 0.50 \cdot \text{Score}_{\text{Bnd}}$ and $\text{Score}_{\text{Bnd}} = \text{clip}\left(\frac{30.0 - \text{bnd}^*}{20.0} \times 100.0, 0.0, 100.0\right)$.
- **Outputs Created:**
  - Script: [`exp12_2_bowling_containment.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/step_12_experimental_models/exp12_2_bowling_containment.py)
  - Full Rankings CSV: [`exp12_2_bowling_rankings.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_2_bowling_containment/exp12_2_bowling_rankings.csv)
  - Tier 1 Comparison CSV: [`exp12_2_bowling_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_2_bowling_containment/exp12_2_bowling_comparison.csv)
  - Visual Chart: [`02_exp12_2_bowling_containment.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_2_bowling_containment/02_exp12_2_bowling_containment.png)
  - Validation Report: [`exp12_2_bowling_containment_report.md`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_2_bowling_containment/exp12_2_bowling_containment_report.md)

### Experiment 12.3 — Cohort-Specific Bayesian Priors
- **Objective:** Test whether segmenting players into tactical cohorts (Top Order vs Middle Order; Pace vs Spin) improves predictive shrinkage under $K=50$, using a strict chronological split (60% Train / 40% Test across 789 matches).
- **Formulation Tested:**
  $$\theta^*_{\text{Cohort}} = \lambda \cdot \hat{\theta}_{\text{obs}} + (1 - \lambda) \cdot \mu_{\text{Cohort}}, \quad \lambda = \frac{N}{N + 50.0}$$
- **Outputs Created:**
  - Script: [`exp12_3_cohort_priors.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/step_12_experimental_models/exp12_3_cohort_priors.py)
  - Full Rankings CSV: [`exp12_3_cohort_priors_rankings.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_3_cohort_priors/exp12_3_cohort_priors_rankings.csv)
  - Chronological Comparison CSV: [`exp12_3_cohort_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_3_cohort_priors/exp12_3_cohort_comparison.csv)
  - Visual Chart: [`03_exp12_3_cohort_priors.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_3_cohort_priors/03_exp12_3_cohort_priors.png)
  - Validation Report: [`exp12_3_cohort_priors_report.md`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_3_cohort_priors/exp12_3_cohort_priors_report.md)

### Experiment 12.4 — Confidence-Based Qualification & Boundary Cliff
- **Objective:** Quantify statistical estimation uncertainty around the 60-ball boundary, evaluate whether 59-ball players are statistically distinguishable from 60-ball qualifiers, and test a Dual-Criteria (Volume + Breadth) qualification framework.
- **Formulation Tested:**
  $$\text{SE} = \frac{\sigma}{\sqrt{N + 50.0}}, \quad \text{CI}_{90} = [\text{Score} \pm 1.645 \cdot \text{SE}]$$
  $$\text{Dual-Criteria: } \text{Qualifies if } (N \ge 60) \lor (N \ge 50 \land M_{\text{HP}} \ge 6)$$
- **Outputs Created:**
  - Script: [`exp12_4_confidence_qualification.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/step_12_experimental_models/exp12_4_confidence_qualification.py)
  - Complete Qualification CSV: [`exp12_4_qualification_rankings.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_4_confidence_qualification/exp12_4_qualification_rankings.csv)
  - Newly Qualified Comparison CSV: [`exp12_4_qualification_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_4_confidence_qualification/exp12_4_qualification_comparison.csv)
  - Visual Chart: [`04_exp12_4_confidence_qualification.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_4_confidence_qualification/04_exp12_4_confidence_qualification.png)
  - Validation Report: [`exp12_4_confidence_qualification_report.md`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_12_experimental_models/exp12_4_confidence_qualification/exp12_4_confidence_qualification_report.md)

---

## 2. Baseline versus Experimental Comparisons

### A. Batting Reliability Rankings (Experiment 12.1 vs Baseline v2.0)

| Official Rank | Player Name | High Balls | Official BRS (v2.0) | Exp BRS_3 | Score Delta | Exp Rank | Net Shift | Key Factor Driving Shift |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **Mahendra Singh Dhoni** | 94 | **100.00** | **100.00** | +0.00 | **#1** | 0 | Perfect sub-scores across all metrics |
| **#2** | **Shashank Singh** | 77 | **79.13** | **78.78** | -0.35 | **#2** | 0 | Elite SR (163.6) and survival (94.8%) |
| **#3** | **Shivam Dube** | 69 | **76.84** | **77.29** | +0.45 | **#3** | 0 | Elite SR (159.4) and survival (95.7%) |
| **#4** | **Shubham Dubey** | 64 | **75.90** | **75.78** | -0.12 | **#4** | 0 | High clutch diff (+37.8) and solid survival |
| **#5** | **Cameron Green** | 61 | **75.89** | **75.29** | -0.60 | **#5** | 0 | Strong all-round profile |
| **#6** | **Jitesh Sharma** | 69 | **75.47** | **73.57** | -1.90 | **#7** | -1 | Lower survival score (74.2) |
| **#7** | **Patrick Cummins** | 62 | **74.15** | **73.34** | -0.81 | **#8** | -1 | Boundary-reliant scoring profile |
| **#8** | **George Dockrell** | 71 | **73.61** | **75.21** | +1.60 | **#6** | **+2** | Elite survival score (89.5) boosts rank |
| **#9** | **Harmanpreet Singh** | 68 | **72.76** | **72.10** | -0.66 | **#10** | -1 | Moderate survival score (73.2) |
| **#10** | **Rinku Singh** | 66 | **72.63** | **72.60** | -0.03 | **#9** | **+1** | High survival consistency (86.4) |
| *Notable* | **Matthew Wade** | 71 | 64.51 | **68.38** | **+3.87** | **#18** | **+10** | Near-flawless survival score (95.8) |
| *Notable* | **Sunil Narine** | 79 | 53.15 | **48.65** | **-4.50** | **#78** | **-16** | Abysmal survival score (30.4) penalized |
| *Notable* | **Tim David** | 115 | 63.12 | **58.90** | **-4.22** | **#47** | **-15** | High dot rate & low survival penalized |

### B. Bowling Reliability Rankings (Experiment 12.2 vs Baseline v2.0)

| Official Rank | Player Name | Legal Balls | Economy | Official BoRS | Exp BoRS | Score Delta | Exp Rank | Net Shift | Key Factor Driving Shift |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **Tim Southee** | 64 | 5.16 | **90.69** | **88.18** | -2.51 | **#1** | 0 | World-class economy (5.16) & dots (57.8%) |
| **#2** | **Keshav Maharaj** | 78 | 6.23 | **79.94** | **77.84** | -2.10 | **#3** | -1 | Elite control (6.23 rpo, 14.1% boundaries) |
| **#3** | **Haris Rauf** | 106 | 6.79 | **78.84** | **76.98** | -1.86 | **#4** | -1 | Pace, dots (49.1%), and clutch control |
| **#4** | **Mark Adair** | 71 | 5.32 | **74.70** | **78.78** | **+4.08** | **#2** | **+2** | Elite boundary suppression (only 8.5% bnd) |
| **#5** | **Shoriful Islam** | 61 | 6.79 | **74.01** | **71.06** | -2.95 | **#6** | -1 | Excellent dot ball rate (54.1%) |
| **#6** | **Harshit Rana** | 158 | 7.86 | **72.85** | **69.73** | -3.12 | **#7** | -1 | High volume, balanced wicket/dot profile |
| **#7** | **Wanindu Hasaranga** | 198 | 6.82 | **70.04** | **72.16** | **+2.12** | **#5** | **+2** | Heavy volume, 75.8 boundary suppression |
| **#8** | **Trent Boult** | 180 | 7.50 | **69.72** | **67.79** | -1.93 | **#10** | -2 | 97.7 dot score balanced by higher bnd |
| **#9** | **Simarjeet Singh** | 60 | 8.00 | **69.40** | **64.81** | **-4.59** | **#12** | **-3** | Higher boundary concession (19.6%) drops out |
| **#10** | **Lungi Ngidi** | 110 | 7.31 | **68.89** | **68.45** | -0.44 | **#8** | **+2** | Consistent death-phase containment |
| *Spotlight*| **Maheesh Theekshana**| 93 | 6.88 | 66.86 | **67.92** | **+1.06** | **#9** | **+3** | Enters Top 10 via 64.8 boundary suppression |
| *Spotlight*| **Jasprit Bumrah** | 168 | 6.93 | 59.29 | **64.46** | **+5.17** | **#14** | **+10** | **Concedes only 13.1% boundaries (Score 74.7)** |
| *Spotlight*| **Harpreet Brar** | 84 | 6.93 | 56.16 | **61.90** | **+5.74** | **#18** | **+23** | Elite boundary suppression (11.9% bnd) |
| *Spotlight*| **Mukesh Choudhary** | 88 | 9.95 | 61.26 | **51.47** | **-9.79** | **#49** | **-30** | Expensive wicket-taker leaking 29.5% bnd |

---

## 3. Important Findings and Methodological Limitations

### Finding 1: Batting Collinearity is Safely Removable Without Ranking Distortion
- In official v2.0, the collinearity between Strike Rate and Boundary Execution ($r = 0.9628$, $R^2 = 92.7\%$) artificially compressed the variance share of Survival Rate down to **19.80%**, creating an implicit 2.3-to-1 bias in favor of boundary hitters over strike rotators.
- Eliminating Boundary Execution and redistributing weights to $\text{BRS}_3 = 0.45(\text{SR}) + 0.35(\text{Surv}) + 0.20(\text{Diff})$ restores Survival Rate to **31.67%** of effective variance while preserving a near-perfect rank correlation of **$\rho = 0.9885$** across Tier 1.
- All 10 batters in the official Top 10 remain in the Top 10 under $\text{BRS}_3$, proving that this is a clean variance recalibration rather than an erratic disruption.

### Finding 2: Bowling Economy is Functionally Dictated by Boundary Bleeding and Dots
- Across all qualified bowlers, Economy Rate is **92.89%** linearly explained by Boundary Concession Rate ($r = +0.8938$) and Dot Ball Rate ($r = -0.4575$).
- Crucially, **Boundary Concession Rate and Dot Ball Rate are statistically independent ($r = -0.1110$)**. Official v2.0 measured dot balls but omitted boundary suppression. By incorporating Boundary Suppression into a unified Containment Index ($0.50 \times \text{Dots} + 0.50 \times \text{Bnd}$), elite containment bowlers like **Jasprit Bumrah** (+10 ranks to #14), **Maheesh Theekshana** (enters Top 10 at #9), and **Harpreet Brar** (+23 ranks to #18) are naturally rewarded without any player-specific rules.

### Finding 3: Cohort-Specific Priors Suffer from Situation Convergence in T20 Cricket
- Chronological out-of-sample validation on 789 matches proved that cohort-specific priors fail to improve predictive generalization.
- In batting, Top Order and Middle Order priors produced **higher out-of-sample RMSE** ($33.59$ vs $33.05$ for Global). In T20 match chasing, top-order batters who bat under high pressure are almost always batting deep into the middle and death overs, meaning their tactical requirements converge with middle-order finishers.
- In bowling, Pace and Spin training priors differed by only 0.21 rpo (8.42 vs 8.21), producing identical out-of-sample error ($2.06$ RMSE). Segmenting players into cohorts introduces subjective classification boundaries with zero empirical benefit.

### Finding 4: The 60-Ball Threshold is an Administrative Policy, Not a Statistical Boundary
- Analytical modeling of the Bayesian posterior standard error $\text{SE} = \frac{\sigma}{\sqrt{N + 50}}$ demonstrates that the difference in estimation precision between 59 balls and 60 balls is **0.01 points** ($\pm 2.40$ vs $\pm 2.39$ margin of error).
- Barring players like **Jamie Overton** (59 balls, 12 matches, BRS 79.54) and **Nasum Ahmed** (55 balls, 10 matches, BoRS 88.84) from official rankings created a harsh boundary cliff. A Dual-Criteria model ($N \ge 60 \lor (N \ge 50 \land M \ge 6)$) admits 30 proven international batters and 17 bowlers who possess substantial match breadth without relying on arbitrary sigmoid mathematics.

### Limitations & Unintended Consequences:
1. **Match-Opportunity Availability Bias:** Implementing dual criteria based on match count ($M \ge 6$) slightly favors international and IPL regulars who play full seasons over emerging tournament players with short 5-match team campaigns.
2. **Containment vs Tail-Ender Slogging:** Reducing wicket weight from 25% to 15% in bowling containment slightly demotes death-overs strike bowlers who concede runs while cleaning up tail-enders. In tournament knockouts, taking wickets in overs 19-20 still carries distinct value that pure containment metrics do not completely capture.

---

## 4. Evaluative Verdicts: Keep, Reject, or Investigate Further

```mermaid
flowchart TD
    subgraph S12["Step 12 Experimental Candidate Evaluation"]
        E1["Exp 12.1: Batting Formula (BRS_3)"] -->|Collinearity eliminated, rho=0.9885| V1["KEEP (Strong Candidate)"]
        E2["Exp 12.2: Bowling Containment (BoRS_Contain)"] -->|Bumrah #14, Theekshana Top 10, r(Dot,Bnd)=-0.111| V2["KEEP (Strong Candidate)"]
        E3["Exp 12.3: Cohort-Specific Priors"] -->|Out-of-sample RMSE worse, identical in bowling| V3["REJECT"]
        E4["Exp 12.4: Dual-Criteria Qualification"] -->|SE delta 0.01 pts, Overton & Nasum admitted| V4["KEEP (Strong Candidate)"]
    end
    
    style V1 fill:#d4edda,stroke:#28a745,stroke-width:2px;
    style V2 fill:#d4edda,stroke:#28a745,stroke-width:2px;
    style V3 fill:#f8d7da,stroke:#dc3545,stroke-width:2px;
    style V4 fill:#d4edda,stroke:#28a745,stroke-width:2px;
```

### Detailed Decision Log:

1. **Experiment 12.1 (Batting Formula BRS_3): KEEP (STRONG CANDIDATE)**
   - *Rationale:* Eliminates undeniable statistical redundancy ($R^2 = 0.927$), restores Survival Rate to its intended 35% weight, retains 100% of the Top 10 batters, and fairly values anchor-finishers.
2. **Experiment 12.2 (Bowling Containment BoRS_Contain): KEEP (STRONG CANDIDATE)**
   - *Rationale:* Resolves the long-standing limitation where elite economical bowlers (Bumrah, Theekshana, Ashwin, Brar) were penalized for batters playing defensively against them. Solves this across the entire population via an objective, principled boundary suppression metric.
3. **Experiment 12.3 (Cohort-Specific Priors): REJECT**
   - *Rationale:* Empirically refuted by out-of-sample chronological validation. Increases prediction error in batting, provides zero gain in bowling, and introduces subjective classification rules. Global Bayesian shrinkage with $K=50$ is strictly superior.
4. **Experiment 12.4 (Dual-Criteria Qualification): KEEP (STRONG CANDIDATE)**
   - *Rationale:* Bridges the 60-ball boundary cliff with mathematical integrity. Admitting players with $N \ge 50$ balls and $M \ge 6$ matches rewards cross-situational breadth while preserving high standards of proof.

---

## 5. Recommended Candidates for a Future Combined Model (SupeRR Selector 3.0)

While Step 12 strictly forbids implementing a combined model, the empirical findings clearly define the blueprint for a future **v3.0 Production Candidate**:

1. **Batting Core:** Adopt $\text{BRS}_3$ (Strike Rate 0.45, Survival Rate 0.35, Clutch Differential 0.20) under global prior shrinkage ($K=50$).
2. **Bowling Core:** Adopt $\text{BoRS}_{\text{Contain}}$ (Economy 0.40, Wickets 0.15, Containment Index 0.30 [50% Dots + 50% Boundary Suppression], Clutch Differential 0.15) under global prior shrinkage ($K=50$).
3. **Priors:** Maintain unified Global Population Priors ($\mu_0$) with $K=50.0$. Reject cohort segmentation.
4. **Qualification Architecture:** Upgrade official qualification to Dual-Criteria:
   - **Tier 1 (Qualified):** $N \ge 60$ balls OR ($N \ge 50$ balls AND $M_{\text{HP}} \ge 6$ matches).
   - **Tier 2 (Specialist):** Remaining players with $40 \le N < 60$ OR ($N \ge 30$ AND $M_{\text{HP}} \ge 4$).
   - **Transparency:** Surface 90% confidence intervals alongside point estimates on all published leaderboards.

---
*(Authored by SupeRR Selector Research & Development Engine — Step 12)*
