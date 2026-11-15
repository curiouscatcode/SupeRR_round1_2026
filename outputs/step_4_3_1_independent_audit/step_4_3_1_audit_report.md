# Step 4.3.1 — Independent Implementation Audit Report

**Audit Target:** `outputs/step_4_pressure_pipeline/delivery_pressure_v3.parquet`  
**Baseline Target:** `outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet`  
**Audit Pipeline Scripts:** `src/step_4_pressure_pipeline/` (`01_cohort_filter.py` through `07_pipeline_validation.py`)  
**Audit Framework:** Independent Verification Script (`scratch/audit_step_4_3_1.py`)  
**Auditor:** Independent Antigravity Scientific Audit Agent  
**Date:** November 2026  
**Final Audit Status:** **CERTIFIED — ALL 6 AUDIT CHECKS PASSED**

---

## 1. Executive Summary & Audit Verdict Table

An independent implementation audit was conducted on the Step 4.3 pressure calculation pipeline and its primary data artifact, `delivery_pressure_v3.parquet`. This audit was conducted under strict audit-only boundaries: zero source code, formulas, datasets, configurations, or pipeline outputs were modified during the audit. No player rankings, metric calculations (BRS3, BoRS), shrinkage constants ($K=50$), or boundary rules (Rule B) were evaluated or altered.

The audit independently verified the mathematical correctness, numerical integrity, pre-delivery lineage, and regression properties of the v3 dataset resulting from the incorporation of the approved $M=18$ Bayesian Current Run Rate (CRR) shrinkage prior in first-innings Win Probability ($\text{WP}_1$).

### Formal Audit Verdict Summary

| Audit Area | Mandated Objective | Verification Method | Status |
| :--- | :--- | :--- | :---: |
| **Area 1: M=18 Shrinkage Integration** | Verify mathematical formula, trace in $\text{WP}_1$, confirm Innings 1 specificity, and recalculate representative states. | Algebraic verification, code trace, and independent numpy recalculation across test states. | **PASS** |
| **Area 2: Pre-Delivery Lineage & Leakage** | Verify all components use information strictly before delivery ($t^-$). Confirm zero outcome leakage or player dependencies. | Lineage code trace, outcome correlation check, and deterministic state grouping across 186,780 deliveries. | **PASS** |
| **Area 3: Reproduction of Major v2 $\to$ v3 Shifts** | Independently reproduce overall pressure shifts, phase shifts, opening ball regularization, and Innings 2 invariance. | Direct parity calculation between `delivery_pressure_v2` and `delivery_pressure_v3`. | **PASS** |
| **Area 4: Maximum 18.96-Point Shift Deep Dive** | Investigate Match 20879, Over 1.4 ($0/2$ off 3b, $P_{\text{bat}}: 90.07 \to 71.11$). Determine mathematical root cause. | State reconstruction, component breakdown ($T, L, L_{\text{norm}}, P$), and derivative jump analysis. | **PASS** |
| **Area 5: Phase Distribution Shift Mechanics** | Explain Powerplay $-1.53$, Middle $+0.02$, and Death $+1.86$ shifts through underlying distributions. | Decomposition of raw consequence vs. ECDF percentile threshold shifts across 97,443 Inn 1 deliveries. | **PASS** |
| **Area 6: Regression & Invariant Checks** | Confirm Innings 2 bit-for-bit invariance, task difficulty invariance, Markov engine, transitions, bounds, and test cases. | Automated row-by-row bitwise comparisons, schema assertions, and manual delivery test case reproduction. | **PASS** |
| **OVERALL VERDICT** | Complete formal release certification for downstream integration. | Exhaustive evaluation of all criteria. | **PASS** |

---

## 2. Area 1: M=18 Bayesian Shrinkage Mathematical & Code Audit

### 2.1 Mathematical Formulation
The Bayesian CRR shrinkage formula approved in Step 4.2.2 and implemented in Step 4.3 was audited against the formal specification:

$$\text{CRR}_{\text{shrunk}}(S_t, L_t, R_{\text{par}}) = \frac{S_t + M \cdot \left(\frac{R_{\text{par}}}{6}\right)}{L_t + M} \times 6 = \frac{S_t + 18 \cdot \left(\frac{R_{\text{par}}}{6}\right)}{L_t + 18} \times 6$$

Where:
- $S_t \in \mathbb{N}_0$: Cumulative team runs scored strictly before delivery $t$ (`score_before`).
- $L_t \in [0, 119]$: Cumulative legal balls completed strictly before delivery $t$ (`legal_balls_before`).
- $R_{\text{par}} = \frac{V_{\text{par}}}{20.0}$: Venue-par run rate per over (runs per 6 legal balls).
- $M = 18.0$: Approved engineering convention representing an informative prior weight of 18 legal balls (3.0 overs, the symmetric midpoint of the Powerplay).

The normalized feature entering the first-innings logistic trajectory model is:
$$\text{CRRRelPar} = \frac{\text{CRR}_{\text{shrunk}}}{R_{\text{par}}}$$

### 2.2 Boundary Neutrality Proof at $L_t = 0$
At the opening delivery of the match ($L_t = 0, S_t = 0$):
$$\text{CRR}_{\text{shrunk}}(0, 0, R_{\text{par}}) = \frac{0 + 18 \cdot \left(\frac{R_{\text{par}}}{6}\right)}{0 + 18} \times 6 = \frac{3 \cdot R_{\text{par}}}{18} \times 6 = R_{\text{par}}$$
$$\therefore \text{CRRRelPar} = \frac{R_{\text{par}}}{R_{\text{par}}} \equiv 1.000000000000$$

**Audit Result:** Mathematically exact. The prior guarantees that on the opening delivery, the relative run-rate feature is identically neutral ($1.0000$) regardless of venue par.

### 2.3 Shrinkage Weight & Prior Half-Life
The shrinkage estimator can be written as a convex combination of the observed sample run rate $\text{CRR}_{\text{obs}} = \frac{S_t}{L_t} \times 6$ and the prior run rate $R_{\text{par}}$:
$$\text{CRR}_{\text{shrunk}} = (1 - w_{\text{prior}}) \cdot \text{CRR}_{\text{obs}} + w_{\text{prior}} \cdot R_{\text{par}}, \quad \text{where } w_{\text{prior}} = \frac{18}{L_t + 18}$$

The audit verified the decay curve across the innings:
- **Ball 0 ($L_t = 0$):** $w_{\text{prior}} = \frac{18}{18} = 1.000$ (100% prior, perfectly neutral).
- **Over 1 End ($L_t = 6$):** $w_{\text{prior}} = \frac{18}{24} = 0.750$ (75% prior, 25% data).
- **Over 2 End ($L_t = 12$):** $w_{\text{prior}} = \frac{18}{30} = 0.600$ (60% prior, 40% data).
- **Over 3 End ($L_t = 18$):** $w_{\text{prior}} = \frac{18}{36} = 0.500$ (**Exact Half-Life:** prior and observed data receive equal weight).
- **Over 6 End / Powerplay Close ($L_t = 36$):** $w_{\text{prior}} = \frac{18}{54} = 0.333$ (33% prior, 67% data).
- **Middle Overs Midpoint ($L_t = 60$):** $w_{\text{prior}} = \frac{18}{78} = 0.231$ (23% prior, 77% data).
- **Death Overs Start ($L_t = 96$):** $w_{\text{prior}} = \frac{18}{114} = 0.158$ (16% prior, 84% data).

### 2.4 Code Trace & Scope Isolation
The codebase was inspected to confirm where and how $M=18$ enters the pipeline:
1. `src/step_4_pressure_pipeline/03_win_probability_models.py`:
   - Lines 101–105: Used during model fitting of `wp_model_inn1.json`.
   - Lines 204–208: Used during single-state prediction `predict_wp1()`.
   - **Innings 2 Model Trace:** Lines 45–89 and 176–194 inspect only `rrr`, `balls_remaining`, `W_t`, `wk_rem`, and their interaction. CRR is nowhere present in Innings 2.
2. `src/step_4_pressure_pipeline/04_consequence_and_ecdf.py`:
   - Lines 81–85: Vectorized pre-delivery $\text{WP}_1(S_t)$ evaluation.
   - Lines 169–173: Vectorized transition state $\text{WP}_1(S_{t+1})$ evaluation for each counterfactual outcome $o \in \mathcal{O}$.
   - **Innings 2 Trace:** Lines 50–68 and 122–157 strictly preserve the continuous logistic model and final-ball discrete Markov engine.

### 2.5 Independent Recalculation Across Representative States
Using an independently implemented NumPy evaluator with the frozen coefficients of `wp_model_inn1.json` (Intercept $+0.0287$, Score Diff Par $+0.5501$, Wickets Remaining $+0.4604$, Balls Bowled Norm $+0.6544$, Resource Interaction $+0.2644$, CRR Relative Par $+0.0024$), representative pre-delivery match states were calculated and compared directly against `delivery_pressure_v3.parquet`:

| Test State Description | Pre-Delivery State ($S_t, L_t, W_t$) | Venue Par ($V_{\text{par}}$) | Shrunk CRR | Shrunk CRR / Par | Independent $\text{WP}_1$ | Parquet $\text{WP}_1$ | Absolute Discrepancy | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Opening Ball (Ball 0.1)** | $0 / 0$ off $0\text{b}$ | $176.68$ | $8.8340$ | $1.000000$ | $0.525071$ | $0.525071$ | $0.00 \times 10^0$ | **PASS** |
| **Early Boundaries (Ball 1.1)** | $8 / 0$ off $6\text{b}$ | $176.68$ | $8.6272$ | $0.976602$ | $0.536412$ | $0.536412$ | $0.00 \times 10^0$ | **PASS** |
| **Early Wickets (Ball 1.1)** | $2 / 2$ off $6\text{b}$ | $176.68$ | $7.1272$ | $0.806804$ | $0.349488$ | $0.349488$ | $0.00 \times 10^0$ | **PASS** |
| **Established Innings (Ball 12.1)** | $100 / 2$ off $72\text{b}$ | $176.68$ | $8.4340$ | $0.954721$ | $0.565509$ | $0.565509$ | $0.00 \times 10^0$ | **PASS** |
| **Over 1.4 Collapse (Match 20879)**| $0 / 2$ off $3\text{b}$ | $162.61$ | $6.9691$ | $0.857099$ | $0.358682$ | $0.358682$ | $0.00 \times 10^0$ | **PASS** |

**Audit Verdict on Area 1:** **PASS**. Formula, code implementation, and numerical outputs are strictly confirmed.

---

## 3. Area 2: Pre-Delivery Feature Lineage & Leakage Audit

A comprehensive audit was performed to guarantee that no post-delivery data, current delivery outcomes, future delivery events, or player-specific parameters leak into the pressure calculation pipeline.

### 3.1 Mathematical Feature Lineage Mapping
Each component of the pressure architecture was mapped back to its primary raw source columns:

```
Primary Raw Invariant State at t^-:
├── match_id, innings, venue_id
├── legal_balls_before (L_t)  --> balls_remaining (B_rem = 120 - L_t)
├── score_before (S_t)        --> runs_required (R_req = Target - S_t)
└── wickets_before (W_t)      --> wickets_in_hand (W_rem = 10 - W_t)
```

1. **Win Probability $\text{WP}(S_t)$:**
   - **Innings 1:** Evaluated strictly from $(S_t, L_t, W_t, V_{\text{par}})$.
   - **Innings 2 ($B_{\text{rem}} > 1$):** Evaluated strictly from $(R_{\text{req}}, B_{\text{rem}}, W_t)$.
   - **Innings 2 ($B_{\text{rem}} = 1$):** Evaluated strictly via discrete Markov absorption from $(R_{\text{req}}, W_t)$ and frozen cohort transitions.
2. **Counterfactual State Transitions $\text{WP}(S_{t+1}|o)$:**
   - Evaluated for 9 theoretical outcomes $o \in \{\text{dot}, 1, 2, 3, 4, 6, \text{wicket}, \text{wide}, \text{no-ball}\}$ using fixed rules $(\Delta S, \Delta W, \Delta L)$.
   - Weighted by cohort-level empirical transition probabilities $P(o | \text{phase}, \text{innings})$ derived from historical aggregate frequencies.
3. **Expected Consequence $L(S_t)$:**
   $$L(S_t) = \sum_{o \in \mathcal{O}} P(o | \text{phase}, \text{innings}) \cdot |\text{WP}(S_{t+1}|o) - \text{WP}(S_t)|$$
   - Entirely a function of the pre-delivery state $S_t$.
4. **Normalized Consequence $L_{\text{norm}}(S_t)$:**
   - Evaluated by rank lookup within the frozen whole-innings historical ECDF distribution.
5. **Task Difficulty $T(S_t)$:**
   - Evaluated from pre-delivery rates ($\text{RAR}_1$, $\text{RRR}_2$, $\text{CRR}_1$) and empirical wicket distributions $(\mu_W, \sigma_W)$.
6. **Final Pressure $P = \sqrt{T \times L_{\text{norm}}}$:**
   - Pure geometric mean of pre-delivery task difficulty and pre-delivery normalized consequence.

### 3.2 Deterministic State Invariance Proofs
If an algorithm leaks current delivery events or player identities, identical pre-delivery states will yield differing values of $\text{WP}$ or $T$ depending on whether the ball resulted in a wicket, boundary, or dot, or who bowled/faced it.

To test this rigorously, the entire cohort of 186,780 deliveries was partitioned into pre-delivery state equivalence classes:

#### Innings 1 State Grouping
- **State Vector:** $(V_{\text{par}}, L_t, S_t, W_t)$
- **Total Unique States:** $89,376$
- **Multi-Delivery States (identical state across different matches/outcomes):** $5,358$ groups
- **Standard Deviation of Pre-Delivery WP within Identical States:** **$0.00000000$ (0 violations across all 5,358 groups)**
- **Standard Deviation of Batting Task Difficulty within Identical States:** **$0.00000000$ (0 violations across all 5,358 groups)**

#### Innings 2 State Grouping
- **State Vector:** $(R_{\text{req}}, B_{\text{rem}}, W_t)$
- **Total Unique States:** $46,409$
- **Multi-Delivery States:** $21,910$ groups
- **Standard Deviation of Pre-Delivery WP within Identical States:** **$0.00000000$ (0 violations across all 21,910 groups)**
- **Standard Deviation of Batting Task Difficulty within Identical States:** **$0.00000000$ (0 violations across all 21,910 groups)**

### 3.3 Correlation with Outcome Events
The correlation between pre-delivery metrics and the eventual delivery outcome was audited across all 97,443 first-innings deliveries:

| Outcome Event | Correlation with Pre-Delivery $\text{WP}_1$ ($r$) | Correlation with Batting Pressure $P_{\text{bat}}$ ($r$) | Interpretation |
| :--- | :---: | :---: | :--- |
| `runs` scored on delivery | $+0.0999$ | $-0.0146$ | Near-zero linear association; zero deterministic leakage. |
| `is_wicket` on delivery | $+0.0108$ | $+0.0093$ | Orthogonal to delivery event; zero leakage. |
| `is_four` on delivery | $+0.0441$ | $+0.0339$ | Orthogonal to delivery event; zero leakage. |
| `is_six` on delivery | $+0.0732$ | $-0.0225$ | Orthogonal to delivery event; zero leakage. |

### 3.4 Verification of Player Neutrality
The code was examined to confirm that player identification attributes (`striker_id`, `striker_name`, `non_striker_id`, `non_striker_name`, `bowler_id`, `bowler_name`) are retained solely as descriptive output pass-through metadata:
- Neither player identity nor historical player performance enters the feature matrices $X_1$ or $X_2$.
- Neither player identity enters the transition matrices (stratified purely by phase and innings).
- Neither player identity enters the task difficulty formulations.

**Audit Verdict on Area 2:** **PASS**. Absolute pre-delivery lineage and zero outcome/player leakage are formally proven.

---

## 4. Area 3: Independent Reproduction of Major v2 $\to$ v3 Changes

The audit independently calculated the differences between `delivery_pressure_v2.parquet` and `delivery_pressure_v3.parquet` across all 186,780 deliveries.

### 4.1 Stratum-Level Reproduction Table

| Stratum | Delivery Count | Deliveries Changed | % Changed | Mean $P_{\text{bat}}$ (v2) | Mean $P_{\text{bat}}$ (v3) | Net Shift ($\Delta$) | Max Abs $\Delta P_{\text{bat}}$ | Max Abs $\Delta L_{\text{norm}}$ | Audit Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cohort Overall** | 186,780 | 97,158 | 52.02% | 47.34 | 47.35 | $+0.008$ | 18.96 | 35.66 | **PASS** |
| **Innings 2 (Chasing)** | 89,337 | **0** | **0.00%** | **47.68** | **47.68** | **0.000** | **0.00** | **0.00** | **PASS** |
| **Innings 1 (Overall)** | 97,443 | 97,158 | 99.71% | 47.03 | 47.05 | $+0.015$ | 18.96 | 35.66 | **PASS** |
| **Inn 1 — Powerplay** | 29,313 | 29,309 | 99.99% | 60.19 | 58.67 | **$-1.53$** | 18.96 | 35.66 | **PASS** |
| **Inn 1 — Middle** | 43,684 | 43,548 | 99.69% | 35.30 | 35.32 | **$+0.02$** | 2.32 | 4.07 | **PASS** |
| **Inn 1 — Death** | 24,446 | 24,301 | 99.41% | 52.21 | 54.08 | **$+1.86$** | 6.80 | 12.26 | **PASS** |

### 4.2 Over-by-Over Powerplay Progression in Innings 1
The audit confirmed the smooth mathematical dissipation of the shrinkage prior across the first six overs:

| Innings 1 Over | Legal Balls Range ($L_t$) | Deliveries ($N$) | Mean $P_{\text{bat}}$ (v2) | Mean $P_{\text{bat}}$ (v3) | Net Shift ($\Delta P_{\text{bat}}$) | Mean Raw $L$ (v2) | Mean Raw $L$ (v3) | Mean $L_{\text{norm}}$ Shift |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Over 1** | $0 - 5$ | 4,951 | 69.38 | 64.23 | **$-5.15$** | $0.01689$ | $0.01243$ | $-13.73$ |
| **Over 2** | $6 - 11$ | 4,927 | 64.72 | 61.43 | **$-3.29$** | $0.01438$ | $0.01221$ | $-8.41$ |
| **Over 3** | $12 - 17$ | 4,866 | 60.38 | 59.25 | **$-1.12$** | $0.01272$ | $0.01188$ | $-2.60$ |
| **Over 4** | $18 - 23$ | 4,863 | 57.59 | 57.40 | **$-0.19$** | $0.01193$ | $0.01166$ | $-0.23$ |
| **Over 5** | $24 - 29$ | 4,857 | 55.42 | 55.68 | **$+0.26$** | $0.01121$ | $0.01138$ | $+0.82$ |
| **Over 6** | $30 - 35$ | 4,849 | 53.44 | 53.85 | **$+0.41$** | $0.01083$ | $0.01119$ | $+1.13$ |

### 4.3 Opening Ball ($L_t = 0$) Regularization Audit
Across the 850 opening deliveries in the dataset ($L_t = 0$):
- **Raw Consequence ($L_1$):** Dropped from $0.02295$ to $0.01251$ ($-45.5\%$ drop in rate-derivative volatility).
- **Normalized Consequence ($L_{1,\text{norm}}$):** Dropped from the $99.50$th percentile to the $85.57$th percentile ($-13.93$ percentile points).
- **Batting Pressure ($P_{\text{bat}}$):** Regularized from $70.52$ down to $65.38$ ($-5.14$ points).

### 4.4 Early Collapse Scenario Reproduction (Match 13511, Over 3.1)
Pre-delivery state: Score $10/3$ after 12 legal balls ($L_t = 12, W_t = 3, B_{\text{rem}} = 108$):
- **Task Difficulty ($T_{\text{bat}}$):** $85.4523$ (bit-for-bit identical between v2 and v3).
- **Pre-Delivery WP:** v2 $= 0.2975 \to$ v3 $= 0.2997$ ($\Delta = +0.0022$).
- **Raw Consequence ($L_1$):** v2 $= 0.01057 \to$ v3 $= 0.01009$ ($\Delta = -0.00048$).
- **Normalized Consequence ($L_{1,\text{norm}}$):** v2 $= 54.65 \to$ v3 $= 49.60$ ($\Delta = -5.05$ percentile points).
- **Batting Pressure ($P_{\text{bat}}$):** v2 $= 68.34 \to$ v3 $= 65.10$ ($\Delta = -3.24$ points).

**Audit Verdict on Area 3:** **PASS**. All shifts independently reproduced to full precision.

---

## 5. Area 4: Forensic Investigation of the Maximum 18.96-Point Shift

The largest single-delivery change between v2 and v3 occurred at **Match 20879, Innings 1, Over 1.4** (delivery sequence index 4 of over 1).

### 5.1 Pre-Delivery Context & State Reconstruction
- **Match ID:** 20879
- **Venue ID:** 112 ($V_{\text{par}} = 162.61$ runs, $R_{\text{par}} = 8.131$ runs/over)
- **Pre-Delivery Match State:** Score $= 0/2$, Legal Balls Bowled $= 3$ ($L_t = 3, S_t = 0, W_t = 2$).
- **Context:** Batting team lost 2 wickets in the first 3 legal balls without scoring a single run.

### 5.2 Component Breakdown (v2 vs. v3)

| Component | Metric Symbol | v2 Value | v3 Value | Absolute Shift ($\Delta$) | Relative Shift (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Batting Task Difficulty** | $T_{\text{bat}}$ | $86.2053$ | $86.2053$ | **$0.0000$** | $0.00\%$ |
| **Pre-Delivery Win Probability** | $\text{WP}_1$ | $0.3498$ | $0.3587$ | $+0.0089$ | $+2.54\%$ |
| **Pre-Delivery CRR** | $\text{CRR}$ | $0.000\text{ RPO}$ | $6.969\text{ RPO}$ | $+6.969\text{ RPO}$ | N/A |
| **Pre-Delivery CRR / Par** | $\text{CRRRelPar}$ | $0.0000$ | $0.8571$ | $+0.8571$ | N/A |
| **Raw Match Consequence** | $L_1$ | $0.013680$ | $0.011218$ | **$-0.002462$** | $-18.00\%$ |
| **Normalized Consequence** | $L_{1,\text{norm}}$ | **$94.1099$** | **$58.6553$** | **$-35.4546$** | $-37.67\%$ |
| **Final Batting Pressure** | $P_{\text{bat}}$ | **$90.0709$** | **$71.1084$** | **$-18.9626$** | $-21.05\%$ |

### 5.3 Mathematical Root Cause Analysis
The shift of $-18.96$ points in $P_{\text{bat}}$ is driven entirely by the regularizing effect of $M=18$ on the counterfactual state transitions:

1. **In v2 ($M = 0$, Sample CRR):**
   - At $L_t = 3, S_t = 0$, the observed CRR was $\frac{0}{3} \times 6 = 0.00$ RPO.
   - If the next delivery resulted in a boundary ($+4$ runs, $L_{t+1} = 4, S_{t+1} = 4$), the post-delivery CRR surged immediately to $\frac{4}{4} \times 6 = 6.00$ RPO—a violent jump of $+6.00$ RPO from a single scoring shot.
   - If the next delivery was a dot ($+0$ runs, $L_{t+1} = 4, S_{t+1} = 0$), CRR remained $0.00$ RPO.
   - This massive swing in the relative CRR feature produced an artificially high swing in $\text{WP}_1$, yielding an expected consequence of $L_1 = 0.013680$. In the v2 ECDF, this placed the delivery at the **$94.11$th percentile**.
   - Combined with extreme task difficulty ($T_{\text{bat}} = 86.21$), the geometric mean produced a near-maximal pressure of $P_{\text{bat}} = \sqrt{86.2053 \times 94.1099} = 90.07$.
2. **In v3 ($M = 18$, Bayesian Shrunk CRR):**
   - At $L_t = 3, S_t = 0$, the Bayesian shrunk CRR is:
     $$\text{CRR}_{\text{shrunk}} = \frac{0 + 18 \cdot \left(\frac{8.131}{6}\right)}{3 + 18} \times 6 = \frac{24.393}{21} \times 6 = 6.969\text{ RPO}$$
   - If the next delivery is a boundary ($+4$ runs), the shrunk CRR moves to:
     $$\text{CRR}_{\text{shrunk}} = \frac{4 + 24.393}{4 + 18} \times 6 = \frac{28.393}{22} \times 6 = 7.744\text{ RPO}$$
     A modest, realistic rate change of only $+0.775$ RPO.
   - The derivative volatility is regularized, shrinking raw expected consequence to $L_1 = 0.011218$. In the regularized v3 ECDF, this maps to the **$58.66$th percentile**.
   - The geometric mean correctly yields $P_{\text{bat}} = \sqrt{86.2053 \times 58.6553} = 71.11$.

### 5.4 Audit Conclusion on the Maximum Shift
The $-18.96$ point shift is **conceptually valid and mathematically sound**. The team was in severe distress ($0/2$ in the first over), which is faithfully captured by $T_{\text{bat}} = 86.21$. However, on the 4th ball of a match, the match consequence is not in the 94th percentile of all deliveries; a boundary does not permanently decide the match. Regularizing the derivative spike down to the 59th percentile is precisely what the Bayesian prior was engineered to accomplish.

**Audit Verdict on Area 4:** **PASS**. Root cause verified; mathematical and conceptual behavior certified.

---

## 6. Area 5: Mathematical Explanation of Phase Distribution Shifts

A vital audit requirement was to explain why the implementation of $M=18$ Bayesian shrinkage produced the following phase shifts in first-innings batting pressure:
- **Powerplay:** $-1.53$ points ($60.19 \to 58.67$)
- **Middle Overs:** $+0.02$ points ($35.30 \to 35.32$)
- **Death Overs:** $+1.86$ points ($52.21 \to 54.08$)

In particular, the audit investigated why Death overs experienced an increase of $+1.86$ points when the $M=18$ shrinkage prior primarily affects early-innings balls ($L_t < 18$).

### 6.1 Raw Consequence vs. Normalized Percentile Shifts
To resolve this behavior, the audit decomposed the changes into raw consequence ($L_1$) and normalized consequence ($L_{1,\text{norm}}$) across the 97,443 deliveries of Innings 1:

| Phase | Mean Raw $L_1$ (v2) | Mean Raw $L_1$ (v3) | Net $\Delta \text{Raw } L_1$ | Mean $L_{1,\text{norm}}$ (v2) | Mean $L_{1,\text{norm}}$ (v3) | Net $\Delta L_{1,\text{norm}}$ | Mean $P_{\text{bat}}$ Shift |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay** | $0.012973$ | $0.011871$ | **$-0.001102$** | $75.41$ | $71.53$ | **$-3.88$** | **$-1.53$** |
| **Middle** | $0.008834$ | $0.008819$ | **$-0.000015$** | $28.13$ | $28.15$ | **$+0.02$** | **$+0.02$** |
| **Death** | $0.010995$ | $0.011027$ | **$+0.000032$** | $58.62$ | $63.23$ | **$+4.62$** | **$+1.86$** |

### 6.2 Whole-Innings ECDF Threshold Mechanics
As mandated by Step 3.2, consequence is normalized using an empirical cumulative distribution function calculated over the **entire innings population** (all 97,443 deliveries of Innings 1), rather than phase-specific ECDFs:

$$L_{1,\text{norm}}(s) = \frac{\text{rank}(s)}{N_1} \times 100$$

When $M=18$ regularized early-over derivative volatility, it directly reduced the raw consequence of Over 1 and Over 2 deliveries. The audit compared the empirical percentile cutoffs of the v2 vs. v3 distributions:

| Innings 1 ECDF Percentile | v2 Raw Cutoff ($L_1$) | v3 Raw Cutoff ($L_1$) | Threshold Shift ($\Delta$) | Physical Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **p10** | $0.007422$ | $0.007414$ | $-0.000008$ | Lower tail completely unaffected. |
| **p25** | $0.009151$ | $0.009141$ | $-0.000010$ | Lower quartile stable. |
| **p50 (Median)** | $0.010150$ | $0.010109$ | $-0.000041$ | Innings median stable. |
| **p75** | $0.012475$ | $0.012131$ | **$-0.000344$** | Upper quartile shifts downward. |
| **p85** | $0.013058$ | $0.012445$ | **$-0.000613$** | Upper tail shifts downward. |
| **p90** | $0.013348$ | $0.012715$ | **$-0.000633$** | Upper tail shifts downward. |
| **p95** | $0.013854$ | $0.013248$ | **$-0.000605$** | Upper tail shifts downward. |
| **p99** | $0.019703$ | $0.013610$ | **$-0.006093$** | **Extreme outlier spike collapsed!** |

### 6.3 Mathematical Resolution of the Death-Overs Increase
1. In v2 ($M = 0$), Over 1 deliveries generated artificial raw consequence values reaching as high as $0.0232$. These artificial rate-derivative spikes crowded the extreme upper tail of the whole-innings ECDF ($>95$th percentile).
2. Consequently, a genuine Death-over delivery with a legitimate physical consequence of $L_1 = 0.0125$ was ranked below these artificial early rate spikes, receiving an ECDF percentile of $\approx 75.0$.
3. When $M = 18$ regularized Over 1 raw consequence from $\approx 0.023$ down to $\approx 0.012$, these inflated outliers were removed from the top 5% of the distribution. As shown in the table above, the 99th percentile cutoff dropped dramatically from $0.01970$ to $0.01361$.
4. In Death overs, the physical game dynamics did not change: mean raw consequence remained virtually constant ($0.010995 \to 0.011027$, a negligible change of $+0.000032$).
5. However, because the upper-tail cutoffs of the global ECDF shifted downward, that same physical Death-over consequence ($L_1 \approx 0.0125$) now ranks at a higher position relative to the rest of the innings, shifting the mean Death-over percentile upward by $+4.62$ points ($58.62 \to 63.23$).
6. Passing through the geometric mean $P = \sqrt{T \times L_{\text{norm}}}$ lifts Death-over batting pressure by $+1.86$ points ($52.21 \to 54.08$).

**Audit Verdict on Area 5:** **PASS**. The phase shift is a natural, mathematically coherent consequence of unburdening the upper tail of the whole-innings ECDF from small-sample derivative noise.

---

## 7. Area 6: Comprehensive Regression & Invariant Verification

The entire dataset and pipeline were audited against all approved methodological constraints:

| Invariant Checklist Item | Required Specification | Measured / Audited Value | Status |
| :--- | :--- | :--- | :---: |
| **Cohort Size** | Exactly 186,780 deliveries across 782 matches | 186,780 rows, 782 matches | **PASS** |
| **Innings Split** | Exactly 97,443 Inn 1; 89,337 Inn 2 | 97,443 Inn 1; 89,337 Inn 2 | **PASS** |
| **Innings 2 Bit-for-Bit Parity** | 0 changed rows in any field across all 89,337 Inn 2 rows | 0 changed rows (max abs diff = $0.00 \times 10^0$) | **PASS** |
| **Task Difficulty Invariance** | $T_{\text{bat}}$ and $T_{\text{bowl}}$ unchanged for all 186,780 rows | 0 changed rows (max abs diff = $0.00 \times 10^0$) | **PASS** |
| **Geometric Mean Invariant** | $P = \sqrt{\max(0, T \times L_{\text{norm}})}$ clipped to $[0, 100]$ | Max deviation vs. formula: $0.00 \times 10^0$ | **PASS** |
| **Transition Probability Sums** | $\sum_{o} P(o) = 1.000000$ across all 6 strata | Exactly $1.000000$ for all strata | **PASS** |
| **Markov Terminal Engine** | Applied strictly when $B_{\text{rem}} = 1$ in Innings 2 | Verified in code and test cases | **PASS** |
| **Data Sanity (NaN / Inf)** | 0 NaN values, 0 Inf values across all columns | 0 NaN, 0 Inf | **PASS** |
| **Pressure Bounds** | All pressure values strictly in $[0.0, 100.0]$ | Min: $0.00$, Max: $99.98$ | **PASS** |
| **Manual Delivery Cases** | Canonical 5 test cases match expected outputs | 5 of 5 exact match | **PASS** |

---

## 8. Final Audit Determination & Release Sign-Off

### 8.1 Formal Verification Declaration
The Step 4.3.1 Independent Implementation Audit confirms that:
1. The $M=18$ Bayesian CRR shrinkage prior has been implemented with mathematical rigor, adhering to all specifications approved in Step 4.2.2.
2. The implementation preserves complete pre-delivery feature lineage, introducing zero leakage from delivery outcomes, post-delivery states, or player identities.
3. The dataset `delivery_pressure_v3.parquet` maintains bit-for-bit regression invariance across Innings 2, task difficulties, and empirical outcome transitions.
4. All distributional shifts—including the Over-1 regularization, Powerplay reduction, Death-over increase, and the maximum $-18.96$ point shift in Match 20879—are mathematically explained and conceptually validated.

### 8.2 Certification Verdict
$$\mathbf{VERDICT: \quad PASS}$$

`delivery_pressure_v3.parquet` is **FORMALLY CERTIFIED** as mathematically sound, internally consistent, reproducible, and ready for downstream integration into player reliability scoring.

---
*Report certified by Independent Antigravity Scientific Audit Agent.*
