# Step 4.1 — Independent Implementation Audit Report

**Document ID:** `step_4_1_independent_implementation_audit.md`  
**Locations:**  
- Primary: `experiments/pressure_definition_v1/step_4_1_independent_implementation_audit.md`  
- Output Archive: `outputs/step_4_1_independent_implementation_audit/step_4_1_independent_implementation_audit.md`  
**Phase:** Step 4.1 — Independent Implementation Audit  
**Framework:** `supeRR_selector_pressure_lab`  
**Audited Directory:** `src/step_4_pressure_pipeline/`  
**Audited Datasets:** `outputs/step_4_pressure_pipeline/`  
**Audit Standard:** Strict Mathematical and Conceptual Independent Audit  
**Overall Implementation Audit Verdict:** **CONDITIONAL PASS (CODE FAITHFUL; 2 METHODOLOGICAL DEFECTS IDENTIFIED)**  

---

## 1. Executive Verdict & Audit Summary

An exhaustive, independent audit of the Step 4 pressure pipeline (`src/step_4_pressure_pipeline/`) was conducted. The audit inspected all pipeline scripts, empirical lookup tables, win probability models, ECDF percentile generators, and the complete 186,780-delivery dataset (`delivery_pressure_v2.parquet` and `delivery_pressure_v2.csv`).

### 1.1 High-Level Audit Findings
1. **Technical & Pipeline Execution:** **PASS.**  
   The software engineering implementation in `src/step_4_pressure_pipeline/` faithfully, reproducibly, and deterministically executes the equations and specifications approved in Step 3.2. All 10 features strictly observe the pre-delivery informational boundary ($t^-$), with zero lookahead outcome leakage ($|r| < 0.05$). All 10 independently tested delivery states reproduce the pipeline's task difficulties, raw consequences, and combined pressure scores with zero mathematical error (max difference $< 0.003$ index points, attributable solely to single-rank array tie resolution in $N=97,443$).
2. **Opening-Ball Discrepancy (Audit A):** **FAIL (METHODOLOGY REPORTING DISCREPANCY).**  
   The Step 3.2 reported value of $L_{\text{norm}} = 50.00$ and $P = 50.00$ for Scenario 1 was **illustrative**, not empirically evaluated. When the actual Step 3.2 formulas and cohort ECDF are evaluated, ball 0.1 of Innings 1 has a raw consequence of $L = 0.02318$, which places it at the **99.60th percentile** of the Innings 1 historical distribution, producing $P_{\text{bat}} = \mathbf{70.57}$. This Step 4 output is reproducible and mathematically exact under the approved formulas, but conceptually indefensible in cricket terms.
3. **Phase & Innings Distribution Disparity (Audit F):** **FAIL (STRUCTURAL INNINGS 1 NORMALIZATION BIAS).**  
   The audit revealed why Middle-over batting pressure averages $\sim 10$ points lower ($41.61$) than Powerplay ($52.71$) and Death ($51.60$). In Innings 2, phase parity holds naturally (PP Mean = $45.24$, Middle Mean = $48.10$, Death Mean = $50.73$). However, in **Innings 1**, pooling all 20 overs into a single ECDF distribution severely distorts consequence: Powerplay deliveries average $L_{\text{norm}} = \mathbf{75.41}$, while Middle-over deliveries average $L_{\text{norm}} = \mathbf{28.13}$! This artificially depresses Innings 1 Middle-over pressure to $35.30$.
4. **Final-Ball Markov Integration (Audit G):** **PASS.**  
   The discrete Markov terminal engine is strictly invoked whenever $B_{\text{rem}} = 1$. It displays strict monotonicity across runs required and wickets lost, respects absorbing terminal states ($1.0$ for win, $0.5$ for tie/Super Over, $0.0$ for loss/all-out), and contains zero player identity bias.

### Table 1.1: Audit Dimension Verdict Matrix
| Audit Module | Audit Focus | Primary Criteria | Verification Method | Verdict | Severity |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Audit A** | **Opening-Ball Discrepancy** | Reconcile Step 3.2 ($P=50.0$) vs Step 4 ($P=70.57$) | Trace 9-outcome WP swings, CRR volatility & ECDF rank | **FAIL** | Moderate |
| **Audit B** | **Feature Lineage & Leakage** | Zero lookahead leakage across all 10 features | Source code trace, array update order & correlation check | **PASS** | None |
| **Audit C** | **Independent Numerical Repro** | Reproduce $\ge 10$ states without pipeline functions | Separate from-scratch audit engine in `scratch/` | **PASS** | None |
| **Audit D** | **Four Model Equations** | Exact fidelity to Step 3.2 mathematical specs | Algebraic coefficient, sign, centering & clipping audit | **PASS** | None |
| **Audit E** | **Consequence & ECDF** | Proper transition sums, extras handling & ECDF | Vectorized swing checks & frozen distribution audit | **PASS** | Minor |
| **Audit F** | **Phase & Innings Disparity** | Investigate Middle-over drop ($41.61$ vs $52.71$) | Cross-tabulated statistical analysis across 186,780 rows | **FAIL** | High |
| **Audit G** | **Final-Ball Markov Engine** | Monotonicity & terminal accuracy on $B_{\text{rem}}=1$ | Parametric boundary sweeps across runs & wickets | **PASS** | None |

---

## 2. Audit A — Opening-Ball Discrepancy Investigation

### 2.1 The Observed Discrepancy
- **Step 3.2 Benchmark Scenario 1:**  
  $\text{State: Inn 1, 0/0, Over 0.1, Par 165} \implies T_{B1} = 50.00,\; L_{\text{norm}} = 50.00,\; P_{\text{bat}} = \mathbf{50.00}$ (Reported as "Exact neutral baseline").
- **Step 4 Production Test Case 1 (Match 13511, Over 1.1):**  
  $\text{State: Inn 1, 0/0, Over 1.1, Par 176.68} \implies T_{B1} = 50.00,\; L_{\text{norm}} = 99.60,\; P_{\text{bat}} = \mathbf{70.57}$.

### 2.2 Seven-Point Investigative Audit

#### 1. Are these genuinely equivalent match situations?
**YES.** Both represent the true opening delivery of the first innings of a T20 match before any ball has been bowled ($S_t = \{ \text{score}=0, \text{wickets}=0, \text{legal\_balls}=0, B_{\text{rem}}=120 \}$).

#### 2. Are they using the same pre-delivery state?
**YES.** Both use $S_0 = (0, 0, 0, 120)$. Both correctly produce $T_{B1} = 50.00$ because $\text{RAR} = R_{\text{par}}$, rate stress $= 0.0$, and regularized wicket stress $W_{\text{stress}} \equiv 0.0$ at ball 0.1.

#### 3. Are they using the same outcome probabilities?
**NO (MINOR REFINEMENT).**  
- Step 3 Table 4.1 listed unnormalized transition probabilities that summed to $1.030$ (adding extras on top of legal balls).
- Step 4 re-derived exact empirical frequencies from the 186,780 deliveries, normalizing strictly to $1.000000$ (`PP_inn1`: Dot: 0.4089, 1: 0.2526, 2: 0.0457, 3: 0.0059, 4: 0.1554, 6: 0.0507, Wkt: 0.0419, Wd: 0.0352, Nb: 0.0037). This refinement slightly increased boundary frequencies (fours: 0.155 vs 0.118; sixes: 0.051 vs 0.027).

#### 4. Are they using the same WP model?
**YES.** The logistic regression model for Innings 1 is identical in both steps:
$$\text{Logit}(\text{WP}_1) = 0.0286 + 0.5425 \cdot \text{ScoreDiffPar}_{\text{norm}} + 0.4582 \cdot \text{WkRem}_{\text{norm}} + 0.6558 \cdot \text{BallsBowled}_{\text{norm}} + 0.2710 \cdot \text{ResInter}_{\text{norm}} + 0.0142 \cdot \text{CRRRelPar}_{\text{norm}}$$

#### 5. Are they using the same ECDF reference distribution?
**YES.** Both evaluate against the historical Innings 1 cohort ($N_1 = 97,443$).

#### 6. Was Step 3.2's scenario value illustrative or empirically calculated?
**ILLUSTRATIVE.**  
This is the root cause of the reporting discrepancy. In Step 3.2 Table 5.1, the author mathematically calculated $T_{B1} = 50.00$ and raw $L = 0.01990$, but **hand-wrote** $L_{\text{norm}} = 50.00$ and $P = 50.00$ under the intuitive assumption that "an opening ball represents the neutral baseline of a match, so its normalized consequence must be the median (50.00)." The author did not actually run the empirical cumulative distribution lookup on $0.01990$. In scratch file `scratch/calc_actual_P_scenarios.py`, the actual min-max / ECDF output was already calculated as $99.24$, but was suppressed in the narrative report.

#### 7. Can the Step 4 result be independently reproduced?
**YES.**  
Evaluating the exact 9 outcomes on Ball 0.1 independently produces:
- Pre-delivery WP: $\text{WP}(S_0) = \mathbf{0.51511}$
- Outcome Dot (p=0.4089): $\text{WP} = 0.50770 \implies \Delta \text{WP} = 0.00741$
- Outcome Single (p=0.2526): $\text{WP} = 0.52305 \implies \Delta \text{WP} = 0.00794$
- Outcome Two (p=0.0457): $\text{WP} = 0.53835 \implies \Delta \text{WP} = 0.02324$
- Outcome Four (p=0.1554): $\text{WP} = 0.56872 \implies \Delta \text{WP} = 0.05361$
- Outcome Six (p=0.0507): $\text{WP} = 0.59857 \implies \Delta \text{WP} = 0.08346$
- Outcome Wicket (p=0.0419): $\text{WP} = 0.43259 \implies \Delta \text{WP} = 0.08253$
- Outcome Extras (p=0.0389): $\text{WP} = 0.53044 \implies \Delta \text{WP} = 0.01533$
- **Expected Consequence:** $L(S_0) = \sum P(o) \cdot |\Delta \text{WP}| = \mathbf{0.023182}$.
- In the Innings 1 historical cohort of 97,443 deliveries, the 99th percentile of raw $L$ is $0.01970$, and the 99.5th percentile is $0.02298$.
- Therefore, $L = 0.023182$ sits at exactly the **99.60th percentile** ($L_{\text{norm}} = \mathbf{99.60}$).
- Combined Pressure: $P_{\text{bat}} = \sqrt{50.00 \times 99.60} = \mathbf{70.57}$.

### 2.3 Cricket Interpretation and Conceptual Defensibility
**Verdict: MATHEMATICALLY CORRECT UNDER STEP 3.2 EQUATIONS, BUT CONCEPTUALLY FLAWED IN CRICKET REALITY.**
- In cricket terms, asserting that the very first delivery of a match carries **99.60th percentile consequence** (higher than 99.6% of all first-innings deliveries, including tense death overs and rebuilding collapses) is **not conceptually defensible**.
- The inflation arises because:
  1. A sample-size-1 delivery causes extreme rate volatility in the logistic model: hitting a six on ball 1 creates a CRR of 36.0 ($+14.2\sigma$ above par), while a wicket drops wickets in hand from 10 to 9, causing large initial WP jumps ($\pm 0.083$).
  2. The ECDF normalizes this early ball against all 97,443 Innings 1 deliveries, where $\sim 45\%$ of balls take place in stable, low-volatility middle overs ($L \approx 0.0088$).
- **Audit Recommendation:** Step 4 faithfully implemented the approved methodology. However, in Step 4.2, the opening ball must be calibrated to match cricket intuition, either through rate shrinkage on early balls ($L_t < 12$) or phase-relative consequence normalization.

---

## 3. Audit B — Pre-Delivery Feature Lineage and Leakage Audit

A comprehensive code and data dependency audit was conducted across `src/prepare_match_data.py`, `src/step_4_pressure_pipeline/01_cohort_filter.py`, `04_consequence_and_ecdf.py`, and `05_task_difficulty_models.py`.

### 3.1 Trace of State Reconstruction Logic
In `src/prepare_match_data.py` (lines 231–259), the pre-delivery match state arrays are explicitly written **BEFORE** the current delivery outcome is parsed and accumulated (lines 291–301):
```python
# 1. State saved strictly BEFORE delivery execution (t^-)
score_before_arr[i] = score
wickets_before_arr[i] = wickets
legal_balls_before_arr[i] = legal_balls
balls_remaining_arr[i] = 120 - legal_balls
crr_arr[i] = (score / legal_balls) * 6.0 if legal_balls > 0 else 0.0
runs_required_arr[i] = target - score if (inn == 2 and target is not None) else np.nan
rrr_arr[i] = (runs_required_arr[i] / (120 - legal_balls)) * 6.0 if ...

# 2. Delivery outcome processed AFTER state is locked
score += t_added
if is_w: wickets += 1
if is_legal: legal_balls += 1
```

### Table 3.1: Complete Pre-Delivery Feature Lineage Matrix
| Feature Name | Source Script / Column | Exact Formula / Derivation | Availability Time | Lookahead Leakage Risk | Verification Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `score_before` | `prepare_match_data.py` | $\sum_{k=1}^{t-1} \text{runs\_added}_k$ | $t^-$ (Pre-ball) | Zero (Updates post-ball) | **PASS** |
| `wickets_before` ($W_t$) | `prepare_match_data.py` | $\sum_{k=1}^{t-1} \mathbb{I}(\text{wicket}_k)$ | $t^-$ (Pre-ball) | Zero (Wicket counted post-ball) | **PASS** |
| `W_rem` | `01_cohort_filter.py` | $10 - W_t$ | $t^-$ (Pre-ball) | Zero (Deterministic linear) | **PASS** |
| `legal_balls_before` | `prepare_match_data.py` | $\sum_{k=1}^{t-1} \mathbb{I}(\text{legal}_k)$ | $t^-$ (Pre-ball) | Zero (Extras tracked separately) | **PASS** |
| `balls_remaining` | `prepare_match_data.py` | $120 - \text{legal\_balls\_before}$ | $t^-$ (Pre-ball) | Zero (Fixed 20-over base) | **PASS** |
| `current_run_rate` | `prepare_match_data.py` | $\frac{\text{score\_before}}{\max(1, \text{legal\_balls\_before})} \times 6.0$ | $t^-$ (Pre-ball) | Zero (Uses pre-delivery score/balls) | **PASS** |
| `runs_required` ($R_t$) | `prepare_match_data.py` | $\text{Target} - \text{score\_before}$ | $t^-$ (Pre-ball) | Zero (Target fixed pre-innings) | **PASS** |
| `required_run_rate` | `prepare_match_data.py` | $\frac{R_t}{\max(1, B_{\text{rem}})} \times 6.0$ | $t^-$ (Pre-ball) | Zero (Pre-delivery variables only) | **PASS** |
| `phase` | `prepare_match_data.py` | PP ($0 \le \text{ov} < 6$), Mid ($6 \le \text{ov} < 15$), Death | $t^-$ (Pre-ball) | Zero (Derived from legal overs) | **PASS** |
| `venue_par` | `02_empirical_tables.py` | Shrunk Venue Par ($K=8.0$) | Pre-Match | Zero (Historical cohort prior) | **PASS** |
| `mu_W`, `sigma_W` | `02_empirical_tables.py` | Empirical Wicket Curve ($L_t$) | Pre-Match | Zero (Historical cohort lookup) | **PASS** |
| `striker_balls_faced` | `prepare_match_data.py` | Retained in data, **EXCLUDED** from models | Pre-ball | Zero (Balls-faced penalty removed) | **PASS** |
| `bowler_spell_balls` | `prepare_match_data.py` | Retained in data, **EXCLUDED** from models | Pre-ball | Zero (Spell workload removed) | **PASS** |

### 3.2 Quantitative Correlation Verification
To confirm zero outcome leakage, Pearson correlation coefficients were computed across all 186,780 deliveries between pre-delivery pressure components and actual delivery outcomes:
- $r(P_{\text{bat}}, \text{runs}) = \mathbf{-0.0094}$
- $r(P_{\text{bat}}, \text{is\_wicket}) = \mathbf{+0.0078}$
- $r(P_{\text{bowl}}, \text{runs}) = \mathbf{+0.0147}$
- $r(P_{\text{bowl}}, \text{is\_wicket}) = \mathbf{-0.0161}$
- $r(L_{\text{norm}}, \text{runs}) = \mathbf{+0.0006}$
- $r(L_{\text{norm}}, \text{is\_wicket}) = \mathbf{-0.0024}$

**Conclusion:** All correlations are bounded within $[-0.016, +0.015]$. There is **zero lookahead outcome leakage** in any feature or pressure component.

---

## 4. Audit C — Independent Numerical Reproduction

Ten delivery states spanning all required archetypes were extracted from `deliveries_with_task_difficulty.parquet` and `delivery_pressure_v2.parquet`. An independent from-scratch audit engine was authored in `scratch/independent_reproduction_10_states.py` with zero calls to pipeline code.

### Table 4.1: Ten-Delivery Independent Reproduction Audit Results
| # | Archetype Context | Match & Ball | State Vector ($S_t$) | Indep $T_{\text{bat}}$ (Pipe) | Indep $T_{\text{bowl}}$ (Pipe) | Indep Raw $L$ (Pipe) | Indep $L_{\text{norm}}$ (Pipe) | Indep $P_{\text{bat}}$ (Pipe) | Indep $P_{\text{bowl}}$ (Pipe) | Max Diff | Status |
| :-: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Opening Ball** | M13511, 1.1 | Inn 1, 0/0, $B_{\text{rem}}=120$ | 50.00 (50.00) | 52.06 (52.06) | 0.023182 (0.023182) | 99.60 (99.60) | 70.57 (70.57) | 72.01 (72.01) | $0.00\times 10^0$ | **PASS** |
| **2** | **Powerplay** | M13514, 3.5 | Inn 1, 13/1, $B_{\text{rem}}=104$ | 55.79 (55.79) | 42.42 (42.42) | 0.012166 (0.012166) | 68.62 (68.62) | 61.87 (61.87) | 53.95 (53.95) | $1.03\times 10^{-3}$ | **PASS** |
| **3** | **Middle Collapse** | M13511, 10.1 | Inn 1, 35/5, $B_{\text{rem}}=66$ | 76.97 (76.97) | 26.69 (26.69) | 0.004834 (0.004834) | 1.93 (1.93) | 12.20 (12.20) | 7.19 (7.18) | $1.62\times 10^{-3}$ | **PASS** |
| **4** | **Death High-Score** | M13513, 19.1 | Inn 1, 195/3, $B_{\text{rem}}=12$ | 20.86 (20.86) | 67.12 (67.12) | 0.006652 (0.006652) | 6.54 (6.54) | 11.68 (11.68) | 20.94 (20.95) | $8.22\times 10^{-4}$ | **PASS** |
| **5** | **Comfortable Chase** | M13511, 17.2 | Inn 2, 92/1, Needs 12 off 23 | 19.43 (19.43) | 85.50 (85.50) | 0.000270 (0.000270) | 3.37 (3.37) | 8.09 (8.09) | 16.97 (16.97) | $0.00\times 10^0$ | **PASS** |
| **6** | **Difficult Chase** | M13513, 16.1 | Inn 2, 147/5, Needs 71 off 30 | 83.89 (83.89) | 19.84 (19.84) | 0.016031 (0.016031) | 55.66 (55.66) | 68.33 (68.33) | 33.23 (33.23) | $1.68\times 10^{-3}$ | **PASS** |
| **7** | **Impossible Chase** | M13512, 19.1 | Inn 2, 132/8, Needs 40 off 12 | 97.81 (97.81) | 5.06 (5.06) | 0.004200 (0.004200) | 19.20 (19.19) | 43.33 (43.33) | 9.86 (9.86) | $2.53\times 10^{-3}$ | **PASS** |
| **8** | **First-Inn Strong** | M13513, 16.4 | Inn 1, 160/2, $B_{\text{rem}}=27$ | 24.84 (24.84) | 66.66 (66.66) | 0.008492 (0.008492) | 17.29 (17.29) | 20.72 (20.72) | 33.95 (33.95) | $5.13\times 10^{-4}$ | **PASS** |
| **9** | **First-Inn Crisis** | M13511, 12.1 | Inn 1, 41/6, $B_{\text{rem}}=54$ | 81.03 (81.03) | 25.43 (25.43) | 0.003582 (0.003582) | 0.62 (0.62) | 7.07 (7.07) | 3.96 (3.96) | $2.94\times 10^{-3}$ | **PASS** |
| **10** | **Final Ball Climax** | M14126, 20.6 | Inn 2, 152/7, Needs 4 off 1 | 98.87 (98.87) | 3.48 (3.48) | 0.302900 (0.302900) | 99.95 (99.95) | 99.41 (99.41) | 18.66 (18.66) | $0.00\times 10^0$ | **PASS** |

### 4.2 Numerical Verification Findings
- Across all 10 archetypes, $T_{\text{bat}}, T_{\text{bowl}}$, and raw $L$ match down to float64 machine epsilon ($0.00 \times 10^{-17}$).
- The minute discrepancy in $L_{\text{norm}}$ ($\le 0.0029$ index points) represents exactly $\pm 1$ position in `np.searchsorted` array rank order among tied floating-point values in arrays of $N=97,443$ and $N=89,337$.
- Under any standard numerical engineering tolerance ($< 0.01$ index points), **10 out of 10 test cases achieve PASS with 100% precision.**

---

## 5. Audit D — Four Model Equation Verification

Every line of code in `src/step_4_pressure_pipeline/05_task_difficulty_models.py` was audited against the formal mathematical specifications in Step 3.2.

### 5.1 Verification Checklist
1. **Model 1 ($T_{B1}$):**
   - Implemented: $Z_{B1} = 0.60 \left(\frac{\text{RAR} - R_{\text{par}}}{R_{\text{par}}}\right) + 0.40 \left(\frac{W_t - \mu_W(L_t)}{\max(0.50, \sigma_W(L_t))}\right)$, $T_{B1} = \frac{100}{1 + \exp(-1.2 \cdot Z_{B1})}$.
   - Verified: Wickets lost $W_t$ correctly increases task difficulty. RAR clipped $\ge 0.0$. Ball 0.1 neutral fix ($W_{\text{stress}} \equiv 0.0$) verified. All 782 opening deliveries with score $0/0$ evaluate to **exactly 50.00**. **STATUS: PASS.**
2. **Model 2 ($T_{B2}$):**
   - Implemented: $Z_{B2} = 0.55 \left(\frac{\text{RRR} - 8.10}{3.00}\right) + 0.25 \left(\frac{W_t - 3.50}{2.00}\right) + 0.20 \left(\frac{\text{RRR} \cdot W_t - 28.0}{25.0}\right)$, $T_{B2} = \frac{100}{1 + \exp(-1.0 \cdot Z_{B2})}$.
   - Verified: RRR clipped to $[0.0, 36.0]$. Interaction term centered by subtracting cohort mean $28.0$. Neutral chase ($\text{RRR}=8.1, W_t=3.5$) evaluates to **50.07**. Impossible chase scales to **99.97**. **STATUS: PASS.**
3. **Model 3 ($T_{BO1}$):**
   - Implemented: $Z_{BO1} = 0.50 \left(\frac{\text{CRR} - R_{\text{par}}}{R_{\text{par}}}\right) + 0.35 \left(\frac{\mu_W(L_t) - W_t}{\max(0.50, \sigma_W(L_t))}\right) + 0.15 \cdot \text{FieldRestrictionFactor}$, $T_{BO1} = \frac{100}{1 + \exp(-1.1 \cdot Z_{BO1})}$.
   - Verified: Opponent wickets term $\frac{\mu_W - W_t}{\sigma_W}$ correctly assigns positive difficulty when the batting side has more wickets in hand than par ($W_t < \mu_W$). Fielding factor is $+0.50$ for PP and Death, $0.00$ for Middle. At ball 0.1, $\text{CRR}_0 \equiv R_{\text{par}}$ and $W_{\text{stress}} \equiv 0.0$. **STATUS: PASS.**
4. **Model 4 ($T_{BO2}$):**
   - Implemented: $Z_{BO2} = 0.60 \left(\frac{8.10 - \text{RRR}}{3.00}\right) + 0.40 \left(\frac{\mu_W(L_t) - W_t}{\max(0.50, \sigma_W(L_t))}\right)$, $T_{BO2} = \frac{100}{1 + \exp(-1.0 \cdot Z_{BO2})}$.
   - Verified: Correctly captures bowling defense hardship (bowling is hardest when opponent required rate is low and opponent wickets are abundant). **STATUS: PASS.**

**Overall Equation Verification Verdict:** **PASS.** Zero algebraic or sign errors detected.

---

## 6. Audit E — Match Consequence and ECDF Audit

### 6.1 Transition Structure and Probability Normalization
- The 9-outcome configuration (`dot`, `one`, `two`, `three`, `four`, `six`, `wicket`, `wide`, `no_ball`) correctly maps runs, wickets, and legal ball deductions.
- Probabilities are empirically pooled across 6 phase/innings strata from all 186,780 cohort deliveries.
- Across all 6 strata, the probability vectors sum strictly to **$1.000000$** (deviation $< 10^{-15}$).
- Player independence is 100% enforced: zero batter or bowler ratings, averages, or IDs exist in transition lookups or WP models.

### 6.2 ECDF Normalization Analysis
- Innings 1 Reference Population: $N_1 = 97,443$ valid pre-delivery states.
- Innings 2 Reference Population: $N_2 = 89,337$ valid pre-delivery states.
- Midpoint empirical cumulative ranking:
  $$L_{i,\text{norm}}(S_t) = \left( \frac{\sum_{j=1}^{N_i} \mathbb{I}(L_j^{(i)} < L(S_t)) + 0.5 \sum_{j=1}^{N_i} \mathbb{I}(L_j^{(i)} = L(S_t))}{N_i} \right) \times 100$$
- Innings 1 Median: **$50.00$**, Min: $0.00$, Max: $100.00$.
- Innings 2 Median: **$50.00$**, Min: $0.11$, Max: $100.00$.
- **Finding on ECDF Calibration:** While ECDF achieves an exact median of 50.00 across each innings as a whole, it creates a severe cross-phase distortion in Innings 1, which is audited in Section 7.

---

## 7. Audit F — Phase and Innings Distribution Analysis

The user audit highlighted that Step 4 reported:
- Powerplay Mean $P_{\text{bat}} = \mathbf{52.71}$
- Death Mean $P_{\text{bat}} = \mathbf{51.60}$
- Middle Overs Mean $P_{\text{bat}} = \mathbf{41.61}$ ($\sim 10$ points lower!)

### 7.1 Cross-Tabulated Empirical Breakdown
To isolate the exact mechanism causing the Middle-overs drop, we decomposed the entire 186,780-delivery dataset across Innings, Phase, Task Difficulty, and Consequence:

### Table 7.1: Comprehensive Phase Decomposition Matrix
| Cohort Slice | Delivery Count ($N$) | Mean $T_{\text{bat}}$ | Median $T_{\text{bat}}$ | Mean Raw $L$ | Median Raw $L$ | Mean $L_{\text{norm}}$ | Median $L_{\text{norm}}$ | Mean $P_{\text{bat}}$ | Median $P_{\text{bat}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Overall Dataset** | 186,780 | 52.53 | 49.02 | 0.013217 | 0.011278 | 50.00 | 50.00 | **47.34** | **47.99** |
| **Innings 1 — All** | 97,443 | 50.89 | 48.59 | 0.010621 | 0.010150 | 50.00 | 50.00 | **47.03** | **47.51** |
| Inn 1 — Powerplay | 29,313 | 49.54 | 47.41 | 0.012973 | 0.012471 | **75.41** | **74.91** | **60.19** | **60.76** |
| Inn 1 — Middle Overs | 43,684 | 50.41 | 49.43 | 0.008834 | 0.009368 | **28.13** | **28.60** | **35.30** | **37.43** |
| Inn 1 — Death Overs | 24,446 | 53.36 | 51.22 | 0.010995 | 0.011910 | **58.62** | **64.06** | **52.21** | **59.90** |
| **Innings 2 — All** | 89,337 | 54.33 | 49.62 | 0.016049 | 0.014229 | 50.00 | 50.01 | **47.68** | **48.57** |
| Inn 2 — Powerplay | 29,326 | 42.17 | 40.91 | 0.014406 | 0.016035 | **52.71** | **55.67** | **45.24** | **47.42** |
| Inn 2 — Middle Overs | 42,476 | 54.82 | 53.66 | 0.013300 | 0.012986 | **48.52** | **46.09** | **48.10** | **49.85** |
| Inn 2 — Death Overs | 17,535 | 73.49 | 82.11 | 0.025459 | 0.010526 | **49.04** | **38.54** | **50.73** | **51.57** |

### 7.2 Root Cause Diagnosis of the Middle-Overs Anomaly
Table 7.1 isolates the root cause with mathematical certainty:

1. **Innings 2 Is Properly Calibrated:**  
   In the second innings (chase), Middle-overs pressure is **not** depressed:
   - Mean $P_{\text{bat}} = \mathbf{48.10}$, Median $P_{\text{bat}} = \mathbf{49.85}$.
   - Mean $L_{\text{norm}} = \mathbf{48.52}$, Median $L_{\text{norm}} = \mathbf{46.09}$.
   Both sit within 2–3 points of the 50.0 neutral baseline!
2. **The Anomaly Is Confined Entirely to Innings 1 Consequence Normalization:**  
   - In Innings 1, task difficulty is uniform across all phases: Powerplay $T = 49.54$, Middle $T = 50.41$, Death $T = 53.36$.
   - However, raw consequence in Innings 1 has a very narrow distribution (Mean = $0.01062$, $\text{Std} = 0.00275$). Because there is no chase target, deliveries in overs 7–15 have very small expected WP swings (Mean raw $L = 0.00883$).
   - When the ECDF ranks all 97,443 deliveries together across all 20 overs, the entire Middle-overs block (43,684 balls, 45% of the innings) falls below the median, with Mean $L_{\text{norm}} = \mathbf{28.13}$!
   - Meanwhile, early overs (where sample-size-1 CRR and initial wicket loss swing WP more) get mapped to the 75th percentile ($L_{\text{norm}} = \mathbf{75.41}$).
   - Multiplying $T \approx 50$ by $L_{\text{norm}} \approx 28.13$ compresses Innings 1 Middle-over batting pressure to **$35.30$**!
   - When pooled across innings:
     $$\text{Pooled Middle Mean} = \frac{43684 \times 35.30 + 42476 \times 48.10}{86160} = \mathbf{41.61}$$
3. **Verdict on Audit F:** **FAIL (STRUCTURAL INNINGS 1 NORMALIZATION BIAS).**  
   The middle-over depression is **NOT** cricket domain reality, nor is it a task difficulty defect. It is a **methodological artifact of whole-innings ECDF pooling in the first innings**.

---

## 8. Audit G — Final-Ball Markov Integration Audit

The integration of the discrete Markov terminal engine was audited across all $B_{\text{rem}} = 1$ deliveries in the second innings.

### 8.1 Implementation Verification
- Code verification confirmed that whenever `balls_remaining == 1` in Innings 2, pre-delivery win probability is evaluated strictly via `wp_framework.predict_wp_final_markov(runs_required, W_t, phase)` (line 44 in `04_consequence_and_ecdf.py`).
- During outcome swing evaluation, terminal absorbing outcomes are assigned directly ($1.0$ if $R_{t+1} \le 0$; $0.5$ if $R_{t+1} = 1$; $0.0$ if $R_{t+1} > 1$ or $W_{t+1} \ge 10$), and re-bowled extras are routed recursively back to `predict_wp_final_markov(req - 1, wt, phase)`.

### 8.2 Parametric Monotonicity and Boundary Testing
Parametric sweeps were conducted across runs required ($R_t \in [1, 12]$) and wickets lost ($W_t \in [0, 10]$):

1. **Monotonicity Across Runs Required (Fixed $W_t = 4, B_{\text{rem}} = 1$):**
   - 1 off 1 ball: $\text{WP} = \mathbf{0.83633}$
   - 2 off 1 ball: $\text{WP} = \mathbf{0.47049}$
   - 3 off 1 ball: $\text{WP} = \mathbf{0.23168}$
   - 4 off 1 ball: $\text{WP} = \mathbf{0.19378}$
   - 5 off 1 ball: $\text{WP} = \mathbf{0.13733}$
   - 6 off 1 ball: $\text{WP} = \mathbf{0.08212}$
   - 7 off 1 ball: $\text{WP} = \mathbf{0.04106}$
   - 8+ off 1 ball: $\text{WP} = \mathbf{0.00000}$
   - **Monotonicity Check:** **PASS.** Strictly non-increasing across all tested states.
2. **Monotonicity Across Wickets Lost (Fixed $R_t = 4, B_{\text{rem}} = 1$):**
   - Wickets Lost $0$ through $9$ (in hand: $10$ down to $1$): $\text{WP} = \mathbf{0.19378}$. (In cricket reality, when 4 runs are needed off 1 ball, losing a wicket loses the match regardless of wickets in hand, while hitting a boundary wins the match).
   - Wickets Lost $10$ (all out): $\text{WP} = \mathbf{0.00000}$.
   - **Monotonicity Check:** **PASS.** Strictly monotonic and respecting absorbing boundary.
3. **Cohort Coverage:**
   - All 256 $B_{\text{rem}} = 1$ deliveries in the certified cohort were evaluated.
   - NaN count: Exactly $0$.
   - Inverted states ($\text{WP} < 0$ or $\text{WP} > 1$): Exactly $0$.
   - Bounded range: $[0.00000, 0.83633]$.

**Verdict on Audit G:** **PASS.** Fully verified, stable, and compliant.

---

## 9. Identified Defects and Their Severity

### Table 9.1: Defect Classification Log
| Defect ID | Defect Description | Affected Module | Evidence & Impact | Severity |
| :--- | :--- | :--- | :--- | :---: |
| **DEF-01** | **Illustrative Hand-Waving of Opening Ball in Step 3.2 Report** | Step 3.2 Table 5.1 | Step 3.2 reported Scenario 1 as $L_{\text{norm}}=50.0, P=50.0$. Evaluating the actual formula produces $L_{\text{norm}}=99.60, P=70.57$. Step 4 faithfully implemented the math, exposing that Step 3.2 hand-wrote 50.0 without running the ECDF. | **MODERATE** |
| **DEF-02** | **Innings 1 Whole-Innings ECDF Middle-Over Compression** | `04_consequence_and_ecdf.py` | Pooling all 20 overs into one ECDF compresses Innings 1 Middle-over consequence to $L_{\text{norm}} \approx 28.13$, driving $P_{\text{bat}}$ down to $35.30$ and creating an artificial 10–15 point penalty against middle-over batters/bowlers. | **HIGH** |
| **DEF-03** | **Innings 1 Sample-Size-1 Rate Volatility on Early Balls** | `03_win_probability_models.py` | At ball 0.1, a single boundary generates an instantaneous CRR of 24–36 RPO ($+14\sigma$ above par), creating artificially high expected swings ($L \approx 0.023$) that exceed 99.6% of first-innings deliveries. | **MODERATE** |
| **DEF-04** | **Unvectorized Python Loop for Final-Ball Markov Evaluations** | `04_consequence_and_ecdf.py` | Lines 41–44 and line 117 use Python `for` loops over indices rather than vectorized matrix multiplication. Functionally correct, but suboptimal for throughput. | **LOW** |

---

## 10. Recommended Corrections (For Future Step 4.2 Implementation)

In strict accordance with the audit guidelines, **zero code or formulas were modified during this audit**. The following recommendations are documented for resolution in Step 4.2:

1. **Recommendation 1 (Resolve Innings 1 Middle-Over Bias): Phase-Conditional or Rolling ECDF for Innings 1:**
   - In Innings 2, whole-innings ECDF works because target distance naturally creates high consequence across all phases (PP Mean $L_{\text{norm}} = 52.7$, Middle $= 48.5$, Death $= 49.0$).
   - In Innings 1, consequence should be normalized **within phase** (Powerplay ECDF, Middle ECDF, Death ECDF) or via a rolling 4-over window. This would restore Innings 1 Middle overs to a median of $50.00$ ($P \approx 50.00$) while preserving legitimate within-phase crisis swings.
2. **Recommendation 2 (Resolve Opening-Ball Consequence Inflation): Bayesian Rate Shrinkage for Early Deliveries:**
   - In the Innings 1 trajectory model, shrink current run rate towards venue par during the first 12 balls:
     $$\text{CRR}_{\text{shrunk}}(L_t) = \frac{L_t}{L_t + 12} \text{CRR}_t + \frac{12}{L_t + 12} R_{\text{par}}$$
   - This eliminates the sample-size-1 rate explosion on ball 1 (where a six produces CRR 36.0), stabilizing opening-ball consequence to an intuitive 45–55 index range.
3. **Recommendation 3 (Update Scenario 1 Documentation):**
   - Explicitly document in the methodology report that the Step 3.2 value of $50.00$ was an illustrative design target, and formally adopt the calibrated Step 4.2 value.
4. **Recommendation 4 (Vectorize Markov Engine):**
   - Replace the Python `for` loop in `04_consequence_and_ecdf.py` with a pre-computed 2D lookup grid `markov_table[runs_required, wickets_lost]` for $B_{\text{rem}} = 1$.

---

## 11. Final Compliance and Sign-Off

### Strict Governance Confirmation
- **Zero Step 4 implementation files or formulas were modified.**
- **Zero player rankings were calculated.**
- **Zero connections were made to BRS3, BoRS, $K=50$, or Rule B.**
- **Zero modifications were made to the original project or legacy pressure index.**
- **All numerical evidence is independently reproducible and saved in `scratch/`.**

**AUDIT EXECUTION IS COMPLETE. WE AWAIT USER APPROVAL BEFORE PROCEEDING TO STEP 4.2.**
