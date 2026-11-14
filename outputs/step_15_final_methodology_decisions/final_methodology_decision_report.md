# Step 15 — Final Methodology Decision Report
**SupeRR Selector — Round 1 Player Reliability Ranking Methodology Freeze**

**Status:** Final Decision Record & Formal Methodology Freeze  
**Author:** Antigravity (Methodology Governance & Evaluation Team)  
**Date:** November 13, 2026  
**Audited Target:** Final Candidate Model for SupeRR Selector Round 1  
**Scope:** Full population evaluation across 188,330 deliveries, 816 batters, and 589 bowlers (IPL & T20I data 2022–2026)  

---

## 1. Executive Summary & Purpose of Step 15

The purpose of **Step 15** is to formally make, document, and freeze the final methodology decisions for the **SupeRR Selector Round 1** player reliability ranking model.

Over Steps 1 through 14.2.1, the evaluation framework underwent rigorous scrutiny:
- **Steps 1–6:** Baseline match reconstruction, Pressure Index calculation, player performance accounting, and official v2.0 rankings.
- **Steps 7–8:** Exploratory data analysis, phase analysis, and visual diagnostics.
- **Steps 9–10:** Experimental Pressure Index audits and independent validation.
- **Steps 11–11.2:** Deep ranking methodology investigation and independent verification.
- **Steps 12–12.6:** Four experimental model investigations (batting formula, bowling containment, Bayesian priors, and qualification rules) and resolution of outstanding issues.
- **Steps 13–13.1:** Experimental model integration (BRS3 batting, BoRS bowling, $K=50$, Rule B) and independent integration audit.
- **Steps 14–14.1:** Historical methodology validation across time, format, and sample splits, including bug remediation in sensitivity scripts.
- **Steps 14.2–14.2.1:** Implementation, full-population impact analysis, and independent audit of the proposed cumulative-innings workload formula.

This document represents the **definitive methodology freeze** for Round 1. It consolidates empirical audit findings, formalizes practical governance choices, documents explicit boundaries, and details the rationale for every selected and rejected component.

### Strict Governance Boundaries Observed
1. **No Source Code Modifications:** No Python source files were altered during Step 15.
2. **Audited Baseline Untouched:** Official production data (`data/processed/*`) and baseline files remain completely preserved.
3. **No Ranking Recalculations:** Step 15 freezes and documents the methodology without regenerating or modifying rankings.
4. **No New Hypotheses or Experiments:** No arbitrary formulas, alternative weights, or unvalidated thresholds were introduced.

---

## 2. The Final Candidate Methodology at a Glance

The final candidate model frozen for SupeRR Selector Round 1 consists of seven integrated specifications:

```
                               ┌─────────────────────────────────────────────────────────────┐
                               │             SupeRR Selector Round 1 Architecture            │
                               └──────────────────────────────┬──────────────────────────────┘
                                                              │
                     ┌────────────────────────────────────────┴────────────────────────────────────────┐
                     ▼                                                                                 ▼
     ┌───────────────────────────────┐                                                 ┌───────────────────────────────┐
     │    Pressure Index Engine      │                                                 │     Reliability Scoring       │
     ├───────────────────────────────┤                                                 ├───────────────────────────────┤
     │ • Original v2.0 12-Factor PI  │                                                 │ • Batting: BRS3 (3-Component) │
     │ • Phase-specific sub-formulas │                                                 │   45% SR, 35% Surv, 20% Diff  │
     │ • Spell-based workload (/12)  │                                                 │ • Bowling: BoRS (4-Component) │
     │ • Threshold: Strictly PI > 60 │                                                 │   40% Econ, 25% Wk, 20% Dot,  │
     └───────────────────────────────┘                                                 │   15% Clutch Diff             │
                                                                                       └───────────────┬───────────────┘
                                                                                                       │
                     ┌─────────────────────────────────────────────────────────────────────────────────┴───────────────┐
                     ▼                                                                                                 ▼
     ┌───────────────────────────────┐                                                                 ┌───────────────────────────────┐
     │    Bayesian Regularization    │                                                                 │     Qualification Policy      │
     ├───────────────────────────────┤                                                                 ├───────────────────────────────┤
     │ • Constant shrinkage K = 50.0 │                                                                 │ • Rule B Dual-Threshold:      │
     │ • Format-calibrated global    │                                                                 │   Tier 1: N >= 60 OR          │
     │   empirical priors (mu)       │                                                                 │          (N >= 50 & M >= 6)   │
     │ • Linear shrinkage lambda     │                                                                 │ • Tier 2: N >= 40 (not in T1) │
     │   lambda = N / (N + 50)       │                                                                 │ • Below Threshold: N < 40     │
     └───────────────────────────────┘                                                                 └───────────────────────────────┘
```

| Component | Final Specification | Source / Precedent | Mathematical Definition |
| :--- | :--- | :--- | :--- |
| **1. Pressure Index (PI)** | Original v2.0 Model | Step 4 / Audited Baseline | 12-factor phase-specific engine; $I_{\text{match}} \times I_{\text{chase}} \times I_{\text{phase}} \times I_{\text{bowler}}$, bounded $[0, 100]$ |
| **2. Bowler Workload** | Spell-Based Workload | Step 4 Baseline | $W_{\text{spell}} = \min\left(100, \frac{\text{legal\_balls\_in\_spell\_before}}{12} \times 100\right)$ |
| **3. Batting Formula** | BRS3 (Three-Component) | Step 12.1 / Step 12.6 / Step 13 | $\text{BRS}_3 = 0.45 \times \text{Score\_SR} + 0.35 \times \text{Score\_Surv} + 0.20 \times \text{Score\_Diff}$ |
| **4. Bowling Formula** | BoRS (Official v2.0) | Step 6 Baseline / Step 12.6 | $\text{BoRS} = 0.40 \times \text{Score\_Econ} + 0.25 \times \text{Score\_Wk} + 0.20 \times \text{Score\_Dot} + 0.15 \times \text{Score\_Diff}$ |
| **5. Bayesian Shrinkage** | Constant $K = 50.0$ | Step 5 / Step 6 / Step 14.1 | $\lambda = \frac{N}{N + 50.0}$; $\text{Metric}^* = \lambda \times \text{Observed} + (1 - \lambda) \times \mu_{\text{global}}$ |
| **6. Qualification Policy**| Rule B Dual-Threshold | Step 12.4 / Step 12.6 / Step 13 | Tier 1: $N \ge 60 \text{ OR } (N \ge 50 \text{ AND } M \ge 6)$; Tier 2: $N \ge 40$; Excluded: $N < 40$ |
| **7. Operational Threshold**| Strictly $\text{PI} > 60.0$ | Step 4–14.2.1 Standard | High Pressure: $\text{PI} > 60.0$; Low / Moderate Pressure: $\text{PI} \le 60.0$ |
| **8. Population Scope** | Full Population First | Step 8 / Step 13 / Step 14 | All 816 batters and 589 bowlers evaluated; Top 10 identified post-qualification |
| **9. Model Purpose** | Historical Measurement | Step 14 / Step 14.1 Charter | Retrospective measurement of observed reliability; **no predictive claims** |

---

## 3. Decision-by-Decision Deep Dive

### Decision 1: Pressure Index (PI) Core Engine & Bowler Workload
- **Final Choice:** Retain the original v2.0 Pressure Index formula, including the original spell-based bowler workload calculation ($W_{\text{spell}}$). Reject the experimental cumulative-innings workload formula ($W_{\text{innings}}$).
- **Alternatives Investigated:**
  1. *Cumulative Innings Workload ($W_{\text{innings}} = \min(100, N_{\text{cum}} / 24 \times 100)$):* Proposed in Step 9 and evaluated in Steps 14.1, 14.2, and 14.2.1.
  2. *Re-weighted 12-Factor Engines:* Evaluated in Steps 9–10 with varied phase weights.
- **Why the Final Choice Was Made:**
  - *Mathematical & Statistical Evidence:* In Step 14.2 and audited in Step 14.2.1, implementing cumulative innings workload altered 177,745 deliveries (94.38%). Rather than cleanly isolating fatigue, dividing cumulative legal balls by 24 acted as an aggressive **phase-confounding proxy** ($r > 0.85$ collinearity with innings progression).
  - *Severe Powerplay Deflation:* In opening overs, bowlers bowling consecutive spells had workload progression cut in half ($25\%$ in Over 2, $50\%$ in Over 3). This deflated Powerplay Bowling PI by an average of **$-2.84$ points**, demoting 3,160 deliveries out of high pressure and reducing total Powerplay high-pressure balls from 12,115 to 9,238.
  - *Unintended Death Overs Inflation:* In late overs, any bowler completing their quota received $W \approx 75\%–100\%$, driving Death Overs PI up by **$+6.77$ points** (median $+8.75$ points). In one-sided or blowout run-chases where the required run rate was dead, bowlers bowling overs 18–20 received an unearned $+7.50$ to $+10.00$ pressure bonus.
  - *Ranking Destabilization:* The full-population bowling score correlation collapsed to **$r = 0.7884$**, and rank correlation dropped to **$\rho = 0.7167$**.
  - *Qualification Injustices:* The deflation of Powerplay pressure stripped high-pressure sample from 15 proven bowlers, disqualifying them from Tier 1 under Rule B. This included elite performers such as **Nasum Ahmed** (Baseline Rank 2 in Tier 1; high balls dropped from 55 to 44), **Junaid Siddique** (Baseline Rank 5; 50 to 45), **Shoriful Islam** (Baseline Rank 7; 61 to 49), and **Simarjeet Singh** (Baseline Rank 11; 60 to 44).
  - *Top 10 Overturn:* 50% of the baseline Top 10 bowlers were replaced (Jaccard similarity = 0.333).
- **Documented Limitations & Uncertainties:**
  - *The Spell-Reset Artifact:* Code inspection in Step 14.2.1 (`src/prepare_match_data.py`, lines 209–225) confirmed that when a bowler rests for 2 or more overs (`ov > last_ov + 2`), their active spell counter resets to zero (`W_spell = 0%`). When a bowler returns for Over 18 or 19 after a middle-overs break, the model treats them as having zero fatigue on that initial delivery.
  - *Future Roadmap (v3.0):* This limitation should not be solved by a blunt $N/24$ linear counter. Instead, future releases should explore an **exponential spell-decay model** ($W = W_{\text{spell}} + \alpha W_{\text{prior}}$ with $\alpha \approx 0.30$) or a rest-interval decay function that preserves Powerplay intensity while retaining inter-spell physical memory.

---

### Decision 2: Batting Reliability Score (BRS) — BRS3 Selection
- **Final Choice:** Adopt the three-component BRS3 formula:
  $$\text{BRS}_3 = 0.45 \times \text{Score\_SR} + 0.35 \times \text{Score\_Surv} + 0.20 \times \text{Score\_Diff}$$
- **Alternatives Investigated:**
  1. *Official v2.0 Four-Component BRS:* $0.35 \times \text{Score\_SR} + 0.30 \times \text{Score\_Surv} + 0.20 \times \text{Score\_Bnd} + 0.15 \times \text{Score\_Diff}$.
  2. *Equal-Weighted Model:* $0.25$ on all four components.
  3. *Survival-First Models:* $0.40$ Survival, $0.30$ Strike Rate, $0.20$ Boundary, $0.10$ Differential.
- **Why the Final Choice Was Made:**
  - *Collinearity Audit:* In Step 11.2 and Step 12.1, rigorous statistical auditing proved that high-pressure Strike Rate and Boundary Execution are almost perfectly collinear:
    $$\text{Pearson } r = 0.963, \quad \text{Spearman } \rho = 0.948, \quad \text{Variance Inflation Factor (VIF)} > 14.0$$
  - *Elimination of Double-Counting:* In T20 cricket under pressure, high strike rates are predominantly achieved through boundaries. Including both Strike Rate (35%) and Boundary Execution (20%) meant that 55% of the official v2.0 score was driven by boundary hitting. Removing Boundary Execution eliminates this redundant artifact.
  - *Balance of Core Dimensions:* BRS3 concentrates evaluation on three mathematically distinct dimensions:
    1. *Scoring Acceleration:* Regularized Strike Rate under high pressure (45%).
    2. *Wicket Preservation:* Regularized Dismissal Rate under high pressure (35%).
    3. *Clutch Differential:* Difference between high-pressure and low/moderate pressure scoring rates (20%).
  - *Ranking Stability:* Step 12.5 and 13.1 confirmed that BRS3 correlates strongly with the baseline ($r = 0.985, \rho = 0.981$) while elevating genuine clutch accumulators and eliminating double-penalty distortions on non-boundary scoring.
- **Explicit Methodological Caveat (Mandatory Boundary):**
  - **The selection of BRS3 does NOT prove that Boundary Execution contains zero independent information, nor does it prove that BRS3 is objectively superior across every conceivable match situation.**
  - In specific tactical scenarios (e.g. boundary-count tiebreakers, super overs, or defending tight boundary ropes), boundary frequency carries tactical significance. BRS3 is selected as a defensible, parsimonious model that avoids variance inflation from extreme multicollinearity, not as an absolute cricketing truth.

---

### Decision 3: Bowling Reliability Score (BoRS) — Retain Official v2.0
- **Final Choice:** Retain the official v2.0 four-component BoRS formula:
  $$\text{BoRS} = 0.40 \times \text{Score\_Econ} + 0.25 \times \text{Score\_Wk} + 0.20 \times \text{Score\_Dot} + 0.15 \times \text{Score\_Diff}$$
- **Alternatives Investigated:**
  1. *Experimental Containment-Weighted Formula:* Evaluated in Step 12.2, 12.5, and 12.6, which incorporated boundary suppression (boundary % conceded) and weighted dot balls more heavily.
- **Why the Final Choice Was Made:**
  - *Audit of Containment Multicollinearity:* In Step 12.5, independent auditing proved that high-pressure Bowling Economy Rate and Boundary Suppression are severely collinear ($r > 0.90$). Introducing boundary suppression duplicated economy rate without introducing novel signal.
  - *Preservation of Wicket-Taking Premium:* The experimental containment formula reduced the weight of wickets taken under pressure from 25% down to 15%. In high-pressure T20 cricket, taking a wicket is the single most effective way to terminate batting momentum and reset required run rates. Diluting wicket-taking rewarded defensive bowlers who bowled defensively without threatening the opposition.
  - *Proven Balance:* The v2.0 BoRS balances run prevention (40% Economy), breakthrough capability (25% Wickets), delivery control (20% Dot Balls), and situational composure (15% Clutch Differential).
- **Documented Limitations & Uncertainties:**
  - Component weights ($40/25/20/15$) represent an expert-calibrated tactical balance rather than an automated regression output against match outcome probabilities.
  - The Clutch Differential component ($15\%$) exhibits higher variance for bowlers whose sample of low/moderate pressure deliveries is small or skewed by garbage-time bowling.

---

### Decision 4: Regularization — Constant Bayesian Shrinkage ($K = 50.0$)
- **Final Choice:** Retain constant global Bayesian shrinkage with hyperparameter $K = 50.0$ legal deliveries across all batting, bowling, and phase components:
  $$\lambda = \frac{N}{N + 50.0}, \quad \text{Score}^* = \lambda \cdot \text{Observed} + (1 - \lambda) \cdot \mu_{\text{global}}$$
- **Alternatives Investigated:**
  1. *Variable $K$ Schemes:* $K=30$ for small samples, $K=75$ for high-variance components.
  2. *Empirical Bayes Hierarchical Priors:* Player-type priors (pace vs. spin, top-order vs. finisher).
  3. *Unregularized Raw Rates:* Ranking purely on sample means.
- **Why the Final Choice Was Made:**
  - *Format Alignment:* In T20 cricket, 50 legal deliveries represents approximately 8.2 overs. For a bowler, this is equivalent to bowling out their maximum allocation across two full matches entirely in high pressure. For a batter, it represents facing over 8 full overs of intense pressure.
  - *Smooth Contraction:* At $N = 50$, $\lambda = 0.50$, giving equal weight to observed performance and the population prior ($\mu$). Players with small samples ($N < 30$) are contracted heavily toward the mean, preventing small-sample outliers (e.g. a bowler taking 2 wickets in 6 balls having an astronomical unregularized score) from corrupting the rankings.
  - *Historical Robustness Verified:* In Step 14.1, sensitivity audits across historical halves (2022–2023 vs 2024–2026), format splits (IPL vs T20I), and sample bootstrap resamples verified that $K = 50.0$ delivers exceptional ranking stability ($\rho = 0.9984–0.9989$).
- **Distinction of Decision Nature:**
  - **$K = 50.0$ is a practical policy choice calibrated to the scale of T20 cricket, not a statistically proven unique global optimum.** A choice of $K = 45$ or $K = 55$ would produce comparable rankings. It is retained because it performs robustly and prevents speculative hyperparameter churning.

---

### Decision 5: Player Qualification Policy — Rule B
- **Final Choice:** Adopt the dual-threshold **Rule B** for player tier assignment:
  - **Tier 1 (Qualified):**
    $$N \ge 60 \quad \text{OR} \quad (N \ge 50 \quad \text{AND} \quad M \ge 6)$$
  - **Tier 2 (Specialist / Secondary):**
    $$N \ge 40 \quad \text{and does not qualify for Tier 1}$$
  - **Below Threshold (Excluded):**
    $$N < 40$$
  *(Where $N$ = high-pressure deliveries under $\text{PI} > 60.0$, and $M$ = distinct matches with high-pressure deliveries under $\text{PI} > 60.0$.)*
- **Alternatives Investigated:**
  1. *Official v2.0 Single Cutoff:* Tier 1 ($N \ge 60$), Tier 2 ($N \ge 30$), Below ($N < 30$).
  2. *Strict Volume Rule A:* Tier 1 ($N \ge 75$), Tier 2 ($N \ge 50$).
  3. *Phase-Specific Qualification:* Separate volume thresholds for PP, Middle, and Death.
- **Why the Final Choice Was Made:**
  - *Mitigating Sample Concentration Artifacts:* Step 11.2 and Step 12.4 demonstrated that a single cutoff of $N \ge 60$ suffered from an asymmetrical vulnerability: a player could accumulate 60 balls across only 2 or 3 extreme matches, qualifying for Tier 1 despite having no multi-match consistency.
  - *Recognizing Multi-Match Clutch Consistency:* Conversely, players who faced 50 to 59 intense deliveries spread across 6, 8, or 10 distinct matches were arbitrarily disqualified under v2.0. Rule B's secondary condition ($N \ge 50 \text{ AND } M \ge 6$) appropriately rewards multi-match breadth.
  - *Defensible Specialist Tier:* Raising the Tier 2 floor from 30 to 40 deliveries eliminates volatile low-sample noise while preserving high-leverage specialists (e.g. death-over hitters or opening swing bowlers who bowl only 1 over per match under pressure).
- **Explicit Methodological Caveat (Mandatory Boundary):**
  - **Rule B is a practical governance policy choice, not a mathematically proven natural threshold.** The boundary numbers (60, 50, 6, 40) are pragmatic cutoffs selected to balance sample reliability against player inclusion. They reflect sound cricketing governance, not an underlying physical discontinuity in player performance.

---

### Decision 6: High-Pressure Operational Classification — Strictly `PI > 60.0`
- **Final Choice:** Maintain the strict operational definition of High Pressure as:
  $$\text{High Pressure:} \quad \text{PI} > 60.0 \quad \Big(\text{and } \text{Low / Moderate Pressure:} \quad \text{PI} \le 60.0\Big)$$
- **Alternatives Investigated:**
  1. *Boundary-Inclusive Standard:* $\text{PI} \ge 60.0$.
  2. *Three-Tier Segmentation:* Low ($\text{PI} < 40$), Moderate ($40 \le \text{PI} \le 70$), High ($\text{PI} > 70$).
- **Why the Final Choice Was Made:**
  - *Audit Reconciliation from Step 14.2.1:* Step 14.2.1 revealed that Step 14.2's executive summary inadvertently cited figures from the boundary-inclusive standard ($\text{PI} \ge 60.0$, 4,881 promoted, 5,657 demoted) rather than the canonical standard ($\text{PI} > 60.0$, 4,867 promoted, 5,636 demoted).
  - *Exact Boundary Counts:* In the baseline delivery dataset, exactly **38 deliveries** have $\text{Bowling\_PI} == 60.0$. In the experimental dataset, exactly **31 deliveries** sit at $60.0$.
  - *Project Consistency:* Throughout Steps 4 through 14, every production script and performance accounting module strictly implemented `df['PI'] > 60.0`. Modifying this to $\ge 60.0$ would introduce unnecessary drift and alter historical counts.
- **Documented Nature:**
  - An operational standard maintained strictly for reproducibility and project consistency.

---

### Decision 7: Full-Population Evaluation Scope
- **Final Choice:** Evaluate and rank the **full population of 816 batters and 589 bowlers**, and then apply qualification filters to identify the Top 10 batters and Top 10 bowlers.
- **Alternatives Investigated:**
  1. *Pre-Filtering Pools:* Evaluating only pre-selected elite players or international stars.
  2. *Roster-Fitted Heuristics:* Adjusting formula weights to force specific popular players into the Top 10.
- **Why the Final Choice Was Made:**
  - *Prevention of Truncation Bias:* A valid ranking system cannot evaluate candidates in a vacuum. Calculating global Bayesian empirical priors ($\mu_{\text{SR}} = 114.05, \mu_{\text{Econ}} = 9.06$) requires complete, untruncated population distributions across all 188,097 clean match deliveries.
  - *Objective Integrity:* The Top 10 must emerge organically from the mathematics of the model across the entire population, rather than designing the model backwards to produce a pre-ordained Top 10 list.
- **Documented Nature:**
  - A foundational methodological principle.

---

### Decision 8: Retrospective Historical Measurement vs. Predictive Modeling
- **Final Choice:** The SupeRR Selector model is strictly defined as a **retrospective historical reliability measurement system**.
- **Alternatives Investigated:**
  1. *Predictive Machine Learning Models:* Forecasting future performance, win probability added, or expected auction value.
- **Why the Final Choice Was Made:**
  - *Project Charter:* The project's explicit objective is to evaluate how reliably players performed under pressure in historical IPL and T20I matches from 2022 to 2026.
  - *Epistemological Boundary:* Historical performance under pressure does not constitute an econometric forecast of future performance. Future performance is mediated by aging, team composition, venue changes, batting orders, and tactical counter-strategies.
- **Documented Boundary:**
  - **No predictive claims are made. The rankings reflect audited historical achievement under pressure, not future performance projections.**

---

## 4. Categorization Matrix: Audit-Supported vs. Practical Policy Decisions

To maintain scientific integrity, the table below explicitly distinguishes decisions supported by empirical audit evidence from pragmatic governance choices:

| Component | Final Decision | Decision Nature | Underlying Rationale & Justification |
| :--- | :--- | :--- | :--- |
| **Pressure Index Workload** | Retain Original v2.0 Spell-Based Workload | **Methodological Decision Supported by Audit Evidence** | Step 14.2 & 14.2.1 empirical proof: cumulative formula causes severe phase-confounding ($r > 0.85$), deflates Powerplay PI ($-2.84$), inflates Death PI ($+6.77$), collapses bowling rank correlation ($r=0.7884$), and unfairly disqualifies 15 Tier 1 bowlers. |
| **Batting Formula (BRS3)** | Remove Boundary Execution; Adopt 3-Component | **Methodological Simplification Supported by Collinearity Audit** | Step 11.2 & 12.1 proof: extreme collinearity between SR and Boundary Execution ($r = 0.963, \text{VIF} > 14.0$). Eliminates redundant double-counting of boundaries. *Caveat: Does not prove boundaries contain zero independent signal in all tactical settings.* |
| **Bowling Formula (BoRS)** | Retain Original v2.0 Four-Component Formula | **Methodological Decision Supported by Audit Evidence** | Step 12.5 & 12.6 proof: containment model was redundant with economy ($r > 0.90$) and diluted wicket-taking. v2.0 BoRS preserves essential balance of economy, strike capability, control, and clutch differential. |
| **Bayesian Shrinkage ($K$)** | Retain Constant $K = 50.0$ Deliveries | **Practical Policy Choice Calibrated to T20 Format** | Format-calibrated heuristic (approx 8.2 overs). Smoothly contracts small samples without penalizing medium samples. Proven stable in Step 14.1 ($\rho = 0.9984–0.9989$). Reasonable and robust, but not a statistically proven unique global optimum. |
| **Qualification (Rule B)** | Tier 1: $N \ge 60 \text{ OR } (N \ge 50 \text{ AND } M \ge 6)$ | **Practical Policy Choice** | Solves sample concentration vulnerability of single 60-ball cutoff while recognizing multi-match consistency. Pragmatic governance thresholds, not natural mathematical cutoffs. |
| **Operational Threshold** | Strictly $\text{PI} > 60.0$ | **Operational Standard for Consistency** | Maintained throughout Steps 4–14. Clarifies Step 14.2 text ambiguity; 38 baseline boundary balls at $\text{PI} == 60.0$ belong to moderate pressure. |
| **Population Scope** | Evaluate Full Population (816 B, 589 Bo) | **Fundamental Methodological Principle** | Prevents truncation selection bias and ensures valid empirical population priors. Top 10 emerges organically. |
| **Model Scope** | Retrospective Measurement Only | **Foundational Governance Boundary** | Strict historical measurement across 2022–2026 data. Prohibits unsupported predictive forecasting claims. |

---

## 5. Frozen Candidate Roster Summary

Applying the frozen final candidate methodology (Step 13 integration baseline: BRS3, BoRS, $K=50$, Rule B, v2.0 PI, $\text{PI} > 60.0$) yields the following verified final candidate Top 10 rosters:

### Final Candidate Top 10 Batters (BRS3 + Rule B Qualification)

| Rank | Player Name | BRS3 Score | High Balls Faced ($N$) | High Matches ($M$) | Reg. Strike Rate ($\text{SR}^*$) | Reg. Dismissal % ($\text{Out}^*$) | Clutch Diff ($\text{Diff}^*$) | Qualification Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Mahendra Singh Dhoni** | **93.21** | 194 | 38 | 159.03 | 4.73% | +21.96 | Baseline Volume ($N \ge 60$) |
| **2** | **Shivam Dube** | **82.01** | 160 | 39 | 145.73 | 3.59% | -7.61 | Baseline Volume ($N \ge 60$) |
| **3** | **Shashank Singh** | **81.39** | 135 | 24 | 152.45 | 5.16% | -7.67 | Baseline Volume ($N \ge 60$) |
| **4** | **Cameron Green** | **80.85** | 78 | 26 | 143.77 | 3.55% | -8.34 | Baseline Volume ($N \ge 60$) |
| **5** | **Shubham Dubey** | **80.02** | 69 | 15 | 146.24 | 5.50% | +4.63 | Baseline Volume ($N \ge 60$) |
| **6** | **Vijay Shankar** | **78.79** | 65 | 14 | 133.93 | 3.08% | +0.31 | Baseline Volume ($N \ge 60$) |
| **7** | **Jamie Overton** | **78.19** | 59 | 14 | 144.98 | 6.92% | +16.05 | Rule B High-Breadth ($N=59, M=14$) |
| **8** | **Rinku Singh** | **76.60** | 177 | 46 | 139.22 | 3.76% | -12.69 | Baseline Volume ($N \ge 60$) |
| **9** | **George Dockrell** | **76.06** | 100 | 29 | 134.68 | 4.36% | +2.06 | Baseline Volume ($N \ge 60$) |
| **10** | **Jitesh Sharma** | **75.83** | 97 | 29 | 145.59 | 5.81% | -7.17 | Baseline Volume ($N \ge 60$) |

### Final Candidate Top 10 Bowlers (v2.0 BoRS + Rule B Qualification)

| Rank | Player Name | BoRS Score | High Legal Balls ($N$) | High Matches ($M$) | Reg. Economy ($\text{Econ}^*$) | Reg. Wicket % ($\text{Wk}^*$) | Reg. Dot % ($\text{Dot}^*$) | Clutch Diff ($\text{Diff}^*$) | Qualification Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Tim Southee** | **90.69** | 64 | 19 | 6.87 | 8.25% | 49.73% | +1.73 | Baseline Volume ($N \ge 60$) |
| **2** | **Nasum Ahmed** | **88.84** | 55 | 10 | 6.43 | 7.06% | 52.09% | +1.39 | Rule B High-Breadth ($N=55, M=10$) |
| **3** | **Keshav Maharaj** | **79.94** | 78 | 12 | 7.34 | 7.35% | 45.07% | +1.43 | Baseline Volume ($N \ge 60$) |
| **4** | **Haris Rauf** | **78.84** | 106 | 19 | 7.52 | 7.31% | 45.96% | +1.27 | Baseline Volume ($N \ge 60$) |
| **5** | **Junaid Siddique** | **74.78** | 50 | 12 | 8.37 | 8.41% | 46.69% | +0.40 | Rule B High-Breadth ($N=50, M=12$) |
| **6** | **Mark Adair** | **74.70** | 71 | 17 | 6.87 | 4.47% | 45.20% | +1.81 | Baseline Volume ($N \ge 60$) |
| **7** | **Shoriful Islam** | **74.01** | 61 | 16 | 7.81 | 6.67% | 47.47% | +0.62 | Baseline Volume ($N \ge 60$) |
| **8** | **Harshit Rana** | **72.85** | 158 | 30 | 8.15 | 5.97% | 47.93% | +1.65 | Baseline Volume ($N \ge 60$) |
| **9** | **Wanindu Hasaranga** | **70.04** | 198 | 34 | 7.27 | 6.21% | 39.80% | +0.65 | Baseline Volume ($N \ge 60$) |
| **10** | **Trent Boult** | **69.72** | 180 | 45 | 7.84 | 4.96% | 49.43% | +0.63 | Baseline Volume ($N \ge 60$) |

*(Note: Nasum Ahmed and Junaid Siddique properly qualify for Tier 1 under Rule B's high-breadth criterion [$N \ge 50, M \ge 6$], avoiding the sample concentration issues of single cutoffs while preserving verified multi-match clutch performers.)*

---

### 5.1 Player Role Classification Policy & All-Rounder Dual Eligibility Audit

A critical methodological question arose regarding the appearance of **Jamie Overton** (`player_id = 2382`) at **Rank 7** in the Tier 1 Batting Top 10. Overton is conventionally classified as a bowling all-rounder. An independent role classification audit was conducted to verify project intent, mathematical validity, and eligibility rules.

#### 1. Player Role Metadata in Source Tracking Data
- In the tracking dataset (`data/ball_by_ball.csv` and `data/playing_eleven.csv`), players do not possess an arbitrary administrative text tag such as "Specialist Batter" or "Pure Bowler".
- Jamie Overton's recorded player profile across the 2022–2026 dataset (England in T20Is; Chennai Super Kings in IPL 2025–2026):
  - **Batting Profile:** Right-hand batter. Batted in 18 matches, faced 150 total deliveries (143 balls faced), scored 202 runs. In official playing XIs (`playing_eleven.csv`), he was deployed in the lower order: position #7 (16 times), position #8 (16 times), position #6 (1 time), and position #9 (1 time).
  - **Bowling Profile:** Right-arm fast pace bowler. Bowled in 26 matches, delivering 479 total balls (454 legal deliveries), capturing 33 wickets at an economy of 8.43.
- **Cricketing Summary:** Jamie Overton is unequivocally a **fast-bowling all-rounder / lower-order power-hitter**.

#### 2. Batting Leaderboard Scope: Full Population vs. Specialist Batters
- **The Batting Leaderboard is explicitly intended to evaluate all eligible players who bat under pressure, not merely specialist top-order batters.**
- Throughout Steps 1–15, the project charter defines the scope as evaluating the full population of 816 batters who faced at least one delivery.
- Introducing a subjective post-hoc filter (e.g. "exclude players who bat below position 6" or "exclude players who bowl more than 10 overs") would introduce severe selection bias and violate objective modeling standards.
- In modern T20 cricket, lower-order hitters face the most acute pressure in the match: the death overs (overs 16–20) and tight run chases where $\text{PI} > 60.0$ naturally concentrates. Restricting the batting board to top-order anchors would systematically penalize the very players tasked with finishing high-pressure games.

#### 3. Intentional Dual Eligibility for All-Rounders
- **All-rounders are intentionally eligible for both batting and bowling leaderboards.**
- The model evaluates *execution skill under pressure*, not roster designations. If an all-rounder meets the volume and match qualification criteria in batting, they are ranked as a batter. If they meet the criteria in bowling, they are ranked as a bowler.
- Project-wide cross-evaluation of prominent all-rounders confirms symmetrical and consistent application:
  - **Wanindu Hasaranga:** Qualifies for Tier 1 in both disciplines (Batting: Rank 137, $N=146, \text{BRS}_3=32.48$; Bowling: Rank 9, $N=198, \text{BoRS}=70.04$).
  - **Mark Adair:** Qualifies for Tier 1 in both disciplines (Batting: Rank 44, $N=117, \text{BRS}_3=61.72$; Bowling: Rank 6, $N=71, \text{BoRS}=74.70$).
  - **Cameron Green:** Qualifies for Tier 1 in Batting (Rank 4, $N=78, \text{BRS}_3=80.85$) and Tier 2 in Bowling (Rank 12, $N=49, \text{BoRS}=36.76$).
  - **Shivam Dube:** Qualifies for Tier 1 in Batting (Rank 2, $N=160, \text{BRS}_3=82.01$) and Below Threshold in Bowling ($N=26 < 40$).
  - **Vijay Shankar:** Qualifies for Tier 1 in Batting (Rank 6, $N=65, \text{BRS}_3=78.79$) and Below Threshold in Bowling ($N=0 < 40$).
  - **George Dockrell:** Qualifies for Tier 1 in Batting (Rank 9, $N=100, \text{BRS}_3=76.06$) and Below Threshold in Bowling ($N=0 < 40$).
  - **Jamie Overton:** Qualifies for Tier 1 in Batting (Rank 7, $N=59, \text{BRS}_3=78.19$) and Below Threshold in Bowling ($N=28 < 40$).

#### 4. Verification of Jamie Overton's Batting Eligibility, Sample Size, Score, and Rank
Direct inspection of `outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv` yields:
- **Sample Size:** High-pressure balls faced $N = 59$; high-pressure matches $M = 14$.
- **Rule B Qualification:** Satisfies Tier 1 via the multi-match breadth condition ($N \ge 50 \text{ AND } M \ge 6$). His 59 balls were not accumulated in 1–2 outlier games, but distributed across 14 high-leverage fixtures for England and CSK against elite opposition (India, Australia, RCB, GT, SRH, RR, MI).
- **Observed Metrics ($\text{PI} > 60.0$):** 101 runs, 4 dismissals, raw strike rate $171.19$, batting average $25.25$, boundary rate $23.73\%$ (9 fours, 5 sixes).
- **Low/Moderate Comparison ($\text{PI} \le 60.0$):** 101 runs off 84 balls, 8 dismissals, raw strike rate $120.24$. Raw clutch delta: $+50.95$ SR points.
- **Bayesian Regularization ($K = 50.0$):**
  - $\lambda_{\text{high}} = 59 / (59 + 50) = 0.5413$
  - Regularized SR: $\text{SR}^* = 144.98 \implies \text{Score\_SR} = 81.22$
  - Regularized Dismissal %: $\text{Out}^* = 6.92\% \implies \text{Score\_Surv} = 64.64$
  - Regularized Clutch Delta: $\text{Diff}^* = +16.05 \implies \text{Score\_Diff} = 95.07$
- **BRS3 Calculation:**
  $$\text{BRS}_3 = 0.45(81.22) + 0.35(64.64) + 0.20(95.07) = 36.55 + 22.62 + 19.01 = \mathbf{78.19}$$
- **Final Ranks:** **Tier 1 Rank 7** (Rank 10 overall across all 816 batters).

#### 5. Retention Decision
- **Jamie Overton is legitimately and definitively retained at Rank 7 in the final Tier 1 Batting Top 10.**
- Removing a player who fully satisfies the mathematical qualification rules because of an external squad role label would violate objective empirical governance.
- If selectors were to arbitrarily remove bowling all-rounders from batting rankings, they would logically have to remove Cameron Green (#4), Shivam Dube (#2), Vijay Shankar (#6), and George Dockrell (#9), decimating the empirical integrity of the model.

#### 6. Tactical Interpretation Guidelines for Selectors
- **Reliability vs. Roster Architecture:** The SupeRR Selector leaderboard ranks *clutch execution reliability*, not an eleven-player lineup.
- When assembling a balanced team, selectors require opening batters, anchor players, wicketkeepers, and specialist bowlers.
- The high presence of finishers and all-rounders in the Batting Top 10 reflects an empirical truth of T20 cricket: **the most acute pressure occurs in the death overs**, where aggressive striking with low dismissal rates is paramount.
- Jamie Overton's ranking does not imply he should bat at #3; it scientifically validates that when deployed in high-pressure situations, he delivers elite closing reliability, making him an exceptionally valuable lower-order weapon.

---

## 6. Unresolved Issues, Limitations & Roadmap for Future Iterations (v3.0)

While the final candidate methodology is methodologically sound and frozen for Round 1, the following known limitations and architectural opportunities are documented for future development:

1. **Spell-Reset Discontinuity in Workload:**
   - *Issue:* In the retained v2.0 formula, a bowler who rests for 2 or more overs (`ov > last_ov + 2`) resets their spell counter to zero.
   - *v3.0 Roadmap:* Implement an **exponential spell-decay model** (e.g. $W_{t} = W_{\text{spell}} + \beta \cdot W_{\text{prior}} \cdot e^{-\Delta t / \tau}$) that preserves intra-innings physical fatigue without inflating late-innings death overs.
2. **Binary Threshold Step-Function at $\text{PI} = 60.0$:**
   - *Issue:* Deliveries at $\text{PI} = 59.9$ are categorized as moderate pressure, while deliveries at $\text{PI} = 60.1$ are categorized as high pressure.
   - *v3.0 Roadmap:* Explore **continuous pressure weighting**, where deliveries contribute to player reliability scores proportional to their continuous $\text{PI} / 100$ value rather than via a binary step-function.
3. **Clutch Differential Variance in Small Samples:**
   - *Issue:* The clutch differential component compares regularized performance under $\text{PI} > 60$ versus $\text{PI} \le 60$. For players whose low-pressure sample is small or unrepresentative, the differential can introduce noise.
   - *v3.0 Roadmap:* Investigate joint bivariate shrinkage on high and low pressure rates simultaneously.
4. **Context-Adjusted Venue & Pitch Normalization:**
   - *Issue:* All deliveries are currently normalized against global empirical priors without adjusting for boundary dimensions or extreme ground scoring rates (e.g. Chinnaswamy vs. Chepauk).
   - *v3.0 Roadmap:* Introduce empirical Bayes venue adjustments in future iterations.

---

## 7. Final Verification Checklist

- [x] **Pressure Index:** Original v2.0 model retained; spell-based workload ($/12$) frozen; experimental cumulative formula rejected.
- [x] **Batting Reliability Score:** BRS3 formula ($45\%$ SR, $35\%$ Surv, $20\%$ Diff) frozen; boundary execution removed.
- [x] **Bowling Reliability Score:** Original v2.0 BoRS ($40\%$ Econ, $25\%$ Wk, $20\%$ Dot, $15\%$ Diff) frozen; containment rejected.
- [x] **Bayesian Shrinkage:** $K = 50.0$ legal deliveries retained across all components.
- [x] **Qualification Policy:** Rule B dual threshold ($N \ge 60 \text{ OR } [N \ge 50 \text{ AND } M \ge 6]$; Tier 2: $N \ge 40$) frozen.
- [x] **Operational Threshold:** Strictly $\text{PI} > 60.0$ used consistently throughout documentation.
- [x] **Population Scope:** Full population (816 batters, 589 bowlers) evaluated; Top 10 identified post-qualification.
- [x] **Epistemological Boundary:** Retrospective historical reliability measurement strictly declared; no predictive claims.
- [x] **Source Integrity:** No Python source files, production datasets, or previous step outputs modified.

---
*Decision record compiled and frozen autonomously by Antigravity under Step 15 methodology governance protocols.*
