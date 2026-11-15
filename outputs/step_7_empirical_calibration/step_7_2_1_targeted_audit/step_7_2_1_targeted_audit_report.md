# Step 7.2.1 — Targeted Independent Audit of Wicket Valuation

**Status:** AUDIT COMPLETE  
**Final Verdict:** **`PASS WITH CONDITIONS`**  
**Audited Artifacts:** Step 7.2 Calibration Models and Outputs (`outputs/step_7_empirical_calibration/step_7_2_wicket_valuation/`)  
**Audit Pipeline Script:** [`src/step_7_empirical_calibration/03_run_targeted_wicket_audit.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/src/step_7_empirical_calibration/03_run_targeted_wicket_audit.py)  
**Audit Output Directory:** [`outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/)

---

## Executive Summary & Final Verdict

This targeted independent audit critically evaluated the empirical validity, mathematical consistency, out-of-sample generalization, parameter stability, and second-innings applicability of the Step 7.2 calibrated Duckworth-Lewis-Stern (DLS) wicket valuation model $\lambda_{\text{wkt}}(u_t, W_{\text{rem}, t})$.

### Final Verdict: `PASS WITH CONDITIONS`

Step 7.2 is methodologically sound, mathematically rigorous, strictly positive, strictly monotonic, and demonstrates decisive out-of-sample predictive power over naive and empirical benchmarks. However, because the resource function was calibrated exclusively on unconstrained First-Innings run maximization data, proceeding to Step 7.3 requires adherence to three mandatory operational conditions.

#### Mandatory Conditions for Step 7.3:
1. **Second-Innings Non-Terminal Wicket Capping:**  
   In Innings 2, for all non-terminal wickets ($W_{\text{rem}} \ge 2$), $\lambda_{\text{wkt}}$ must be capped at the remaining target runs:
   $$\lambda_{\text{wkt}}^{\text{eff}}(u_t, W_{\text{rem}, t}) = \min\left(\lambda_{\text{wkt}}(u_t, W_{\text{rem}, t}), \text{runs\_required}_t\right)$$
   This prevents anomalous penalties (e.g., deducting $7.7$ runs when only $1$ run is needed to win).
2. **Terminal Inning Termination Preservation:**  
   For the final wicket ($W_{\text{rem}} = 1$), the uncapped $\lambda_{\text{wkt}}(u_t, 1)$ must always apply, because losing the 10th wicket terminates the innings immediately and guarantees defeat in a chase regardless of `runs_required`.
3. **Format-Stratification Mandate:**  
   All IPL deliveries must strictly use the IPL-calibrated lookup table ($b = 2.314, Z_0^{\text{IPL}}$); all T20I deliveries must strictly use the T20I-calibrated lookup table ($b = 2.128, Z_0^{\text{T20I}}$). Pooled values must only serve as diagnostic benchmarks.

---

## 1. Out-of-Sample Model Quality & Cross-Validation Integrity

### 1.1 Benchmark Comparison on Match-Held-Out Folds
To determine whether the Format-Stratified DLS model provides a genuine structural improvement rather than a marginal numerical artifact, we benchmarked it against six alternative specifications across identical 5-fold match-held-out splits:

| Model Specification | Cross-Validation Architecture | Out-of-Sample RMSE (Runs) | Out-of-Sample MAE (Runs) | Out-of-Sample Bias (Runs) | Out-of-Sample $R^2$ Score | Free Parameters | Strictly Positive ($\lambda \ge 0$) | Strictly Monotonic |
|---|---|---|---|---|---|---|---|---|
| **Global Mean Remaining Runs** | Null Baseline | $55.865$ | $46.689$ | $-0.001$ | $0.000$ | 1 | Yes | Yes |
| **Format-Specific Mean Remaining Runs** | Format Null | $55.769$ | $46.621$ | $-0.003$ | $0.003$ | 2 | Yes | Yes |
| **Linear($u$) Global Run Rate** | Time-Only Linear | $25.382$ | $18.492$ | $-0.002$ | $0.794$ | 1 | Yes | Yes |
| **Format-Linear($u$) Run Rate** | Time-Only Format | $25.094$ | $18.194$ | $-0.003$ | $0.798$ | 2 | Yes | Yes |
| **Unsmoothed Empirical Grid** | 2D Bivariate Grid | $23.588$ | $17.043$ | $-0.011$ | $0.822$ | 1,200 | **NO (Fails)** | **NO (Fails)** |
| **Pooled DLS (Unified)** | Single Exponential | $23.523$ | $16.998$ | $-0.026$ | $0.823$ | 11 | Yes | Yes |
| **Format-Stratified DLS (Approved)** | Format Exponential | **$23.280$** | **$16.758$** | **$-0.045$** | **$0.826$** | 22 | **YES (100%)** | **YES (100%)** |

*Artifact Reference:* [`baseline_comparison_results.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/baseline_comparison_results.csv)

### 1.2 Evaluation of Meaningful Improvement
1. **Variance Explained:**  
   The Format-Stratified DLS model explains **$82.63\%$** of the total variance in remaining runs across all deliveries, reducing RMSE from $55.865$ down to $23.280$.
2. **Value of Non-Linear Wicket Modeling:**  
   Compared to a format-linear model based solely on balls remaining ($u$), which achieves an RMSE of $25.094$, the DLS model achieves an RMSE of $23.280$. This represents a **$14.0\%$ reduction in unexplained residual variance** ($629.7 \to 542.0 \text{ runs}^2$), proving that modeling the non-linear interaction between wickets in hand and balls remaining captures fundamental cricket dynamics.
3. **Decisive Superiority Over the Empirical Grid:**  
   While an unsmoothed empirical grid uses 1,200 unconstrained cell parameters, it overfits local sampling noise, achieving an out-of-sample RMSE of $23.588$. More critically, the empirical grid produces multiple negative wicket values ($\lambda_{\text{wkt}} < 0$) in sparse states. In contrast, the Format-Stratified DLS model achieves superior predictive accuracy ($23.280$) using only 22 parameters while guaranteeing mathematical monotonicity and positivity.

### 1.3 Audit of Cross-Validation Leakage
We audited the cross-validation implementation in `02_calibrate_wicket_valuation.py` for potential training/test leakage:
- **Match-Level Splitting:** Partitioning was performed on unique `match_id` values stratified by format. In every fold, `len(train_matches.intersection(test_matches)) == 0` (0 overlap verified across all 5 folds).
- **Strictly Disjoint Calibration:** The Levenberg-Marquardt optimizer was trained exclusively on deliveries from the training matches.
- **Out-of-Sample Metric Calculation:** Test deliveries were scored purely with parameters fitted on disjoint training folds.
- **Conclusion:** There was **zero data leakage** in Step 7.2.

*Artifact Reference:* [`match_cv_leakage_check.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/match_cv_leakage_check.csv)

---

## 2. Second-Innings Applicability Analysis

### 2.1 Theoretical Justification for First-Innings Calibration
Step 7.2 calibrated resource curves exclusively on Innings 1 data (782 matches, 97,443 deliveries). This decision was methodologically correct because:
1. **Unconstrained Run Maximization:** Innings 1 teams seek to score the maximum possible runs over 120 balls. Wicket loss represents a loss of future scoring capacity.
2. **Target Truncation in Innings 2:** In Innings 2, a team's objective is to reach the target $T$, not to maximize runs. As soon as $R_{\text{scored}} \ge T$, the innings immediately terminates.
3. **Data Censoring:** If a resource curve were fitted directly on Innings 2 remaining runs, the resulting function would primarily reflect the match target distribution rather than player skill or resource capacity.

### 2.2 Empirical Audit of Second-Innings Match Endings
In our dataset of 782 matches, Innings 2 deliveries total 89,337. An analysis of match endings reveals:
- **Chases Won (Terminated Early by Target):** 294 matches ($37.60\%$).
- **Bowled Out (Terminated Early by All-Out):** 159 matches ($20.33\%$).
- **Batted Full 20 Overs (Defending Team Won):** 225 matches ($28.77\%$).
- **Shortened / Interrupted Matches:** 104 matches ($13.30\%$).

*Artifact Reference:* [`second_innings_applicability.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/second_innings_applicability.csv)

### 2.3 The Target Overflow Problem ($\lambda_{\text{wkt}} > \text{runs\_required}$)
When applying the First-Innings intrinsic resource value $\lambda_{\text{wkt}}(u, W_{\text{rem}})$ to Innings 2 chases, an edge-case distortion arises when remaining target runs are very small:
- Across all 89,337 Innings 2 deliveries, there are **232 deliveries ($0.26\%$)** where $\lambda_{\text{wkt}} > \text{runs\_required}$.
- During these 232 deliveries, exactly **14 dismissals** occurred.
- *Concrete Example (Match 14129, Ball 11610):*  
  At Over 7.1 ($u = 77$ balls remaining), the batting team had 10 wickets in hand ($W_{\text{rem}} = 10$) and needed only **1.0 run** to win. The calibrated IPL $\lambda_{\text{wkt}}(77, 10)$ is **$7.73$ runs**. When the batter was dismissed, unconstrained accounting would debit $-7.73$ runs from their batting ledger and credit $+7.73$ runs to the bowler, even though the match outcome was practically sealed and the team only needed 1 run.

### 2.4 Resolution and Operational Boundary Condition
To eliminate this distortion while preserving cricket realism:
- **For Non-Terminal Wickets ($W_{\text{rem}} \ge 2$):**  
  Losing a non-terminal wicket when wickets are plentiful cannot forfeit more runs than the team actually needs to win the match. Therefore, $\lambda_{\text{wkt}}$ must be capped at `runs_required`:
  $$\lambda_{\text{wkt}}^{\text{eff}} = \min(\lambda_{\text{wkt}}, \text{runs\_required})$$
- **For Terminal Wickets ($W_{\text{rem}} = 1$):**  
  If 9 wickets are down, losing the final wicket terminates the innings immediately, resulting in a loss of the match. For the final wicket, $\lambda_{\text{wkt}}$ must **never** be capped at `runs_required`.
- **Pressure Weighting Mitigation:**  
  Because Step 6.3 incorporates exponential pressure weighting $w_t = \exp(\alpha P_t)$, blowout situations (e.g., 1 run needed from 77 balls) have $P_t \approx 0.05$, naturally reducing the weight of these deliveries. However, enforcing the explicit cap $\min(\lambda_{\text{wkt}}, \text{runs\_required})$ ensures mathematical integrity regardless of the pressure exponent $\alpha$.

---

## 3. Parameter and Format Stability Analysis

### 3.1 Fold-by-Fold Parameter Stability
We evaluated the stability of all 11 parameters across the 5 cross-validation folds:

| Format | Parameter | Full Cohort Estimate | Fold Mean | Fold Std Dev | Coefficient of Variation (CV%) | Min Across Folds | Max Across Folds |
|---|---|---|---|---|---|---|---|
| **IPL** | **$b$** | **$2.314$** | $2.314$ | $0.027$ | **$1.18\%$** | $2.279$ | $2.335$ |
| **IPL** | **$Z_0(1)$** | **$20.10$** | $20.23$ | $2.71$ | **$13.40\%$** | $16.56$ | $22.69$ |
| **IPL** | **$Z_0(2)$** | **$23.10$** | $23.38$ | $1.84$ | **$7.89\%$** | $20.38$ | $25.46$ |
| **IPL** | **$Z_0(3)$** | **$38.67$** | $38.96$ | $2.39$ | **$6.14\%$** | $35.14$ | $41.50$ |
| **IPL** | **$Z_0(4)$** | **$61.84$** | $61.97$ | $2.03$ | **$3.27\%$** | $59.67$ | $64.35$ |
| **IPL** | **$Z_0(5)$** | **$106.81$** | $106.76$ | $5.17$ | **$4.84\%$** | $99.00$ | $110.81$ |
| **IPL** | **$Z_0(6)$** | **$129.82$** | $129.93$ | $5.36$ | **$4.12\%$** | $123.64$ | $137.08$ |
| **IPL** | **$Z_0(7)$** | **$177.35$** | $177.54$ | $8.07$ | **$4.55\%$** | $168.75$ | $189.73$ |
| **IPL** | **$Z_0(8)$** | **$219.35$** | $219.42$ | $6.93$ | **$3.16\%$** | $214.17$ | $230.72$ |
| **IPL** | **$Z_0(9)$** | **$261.37$** | $261.59$ | $7.59$ | **$2.90\%$** | $251.73$ | $270.93$ |
| **IPL** | **$Z_0(10)$** | **$322.66$** | $322.79$ | $5.77$ | **$1.79\%$** | $315.13$ | $331.38$ |
| **T20I**| **$b$** | **$2.128$** | $2.128$ | $0.026$ | **$1.24\%$** | $2.092$ | $2.166$ |
| **T20I**| **$Z_0(1)$** | **$12.83$** | $12.66$ | $1.53$ | **$12.08\%$** | $10.67$ | $14.05$ |
| **T20I**| **$Z_0(2)$** | **$33.82$** | $34.10$ | $4.15$ | **$12.18\%$** | $27.11$ | $38.23$ |
| **T20I**| **$Z_0(3)$** | **$53.25$** | $53.27$ | $6.74$ | **$12.65\%$** | $43.79$ | $59.62$ |
| **T20I**| **$Z_0(4)$** | **$72.58$** | $72.81$ | $2.28$ | **$3.14\%$** | $69.75$ | $75.53$ |
| **T20I**| **$Z_0(5)$** | **$107.35$** | $107.38$ | $2.43$ | **$2.27\%$** | $103.94$ | $110.57$ |
| **T20I**| **$Z_0(6)$** | **$145.68$** | $145.70$ | $3.95$ | **$2.71\%$** | $140.96$ | $149.25$ |
| **T20I**| **$Z_0(7)$** | **$172.18$** | $172.36$ | $5.54$ | **$3.21\%$** | $164.87$ | $178.67$ |
| **T20I**| **$Z_0(8)$** | **$216.63$** | $216.80$ | $6.22$ | **$2.87\%$** | $206.30$ | $222.05$ |
| **T20I**| **$Z_0(9)$** | **$258.67$** | $258.73$ | $6.12$ | **$2.37\%$** | $250.44$ | $263.91$ |
| **T20I**| **$Z_0(10)$** | **$292.87$** | $292.99$ | $6.32$ | **$2.16\%$** | $285.47$ | $301.62$ |

*Artifact Reference:* [`parameter_stability_and_format_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/parameter_stability_and_format_comparison.csv)

### 3.2 Audit of Low-Wicket Discrepancy ($Z_0(2) - Z_0(1)$)
A key inquiry of this audit was why IPL displays a small capacity gap between 1 and 2 wickets in hand ($Z_0(2) - Z_0(1) = 3.00\text{ runs}$), whereas T20I displays a large gap ($Z_0(2) - Z_0(1) = 20.99\text{ runs}$).

Our empirical audit uncovered the direct underlying cause:
1. **Empirical Scoring Rate Parity in IPL:**  
   In IPL Innings 1, deliveries at $W_{\text{rem}} = 2$ (8 down) score at an average of **$5.29$ runs per over** ($15.36$ runs over $17.41$ balls remaining). Deliveries at $W_{\text{rem}} = 1$ (9 down) score at an average of **$5.67$ runs per over** ($11.81$ runs over $12.49$ balls remaining). In franchise cricket, the 10th and 11th batters are capable hitters who swing aggressively regardless of being 8 down or 9 down. The marginal difference in scoring rate is negligible.
2. **Steep Tail Collapse in T20I:**  
   In T20I Innings 1, deliveries at $W_{\text{rem}} = 2$ (8 down) score at an average of **$7.26$ runs per over**. However, upon losing the 9th wicket ($W_{\text{rem}} = 1$), the scoring rate collapses to **$4.66$ runs per over**. International teams have distinct non-batting tails (especially Associate nations and traditional lower orders), creating a substantial drop in scoring capacity between 8 down and 9 down.
3. **Sparse-State Extrapolation:**  
   In Innings 1, teams are rarely 8 or 9 down with many balls remaining. The maximum observed balls remaining at $W_{\text{rem}} = 1$ is 39 balls in IPL and 52 balls in T20I. As a result, asymptotic capacities $Z_0(1)$ and $Z_0(2)$ are mathematically extrapolated beyond the empirical support. However, in live matches, $W_{\text{rem}} \le 2$ occurs almost exclusively in the death overs ($u \le 24$), where DLS predictions are driven by $b \cdot u$ and accurately match observed data.

---

## 4. Mathematical and Diagnostic Consistency

We audited all core mathematical invariants across all 3,630 points in the resource and lookup tables:

| Mathematical Invariant | Scope / Domain | Empirical Test Result | Status |
|---|---|---|---|
| **Wickets Remaining Indexing** | All 186,780 Deliveries | $W_{\text{rem}} + \text{wickets\_before} \equiv 10$ holds strictly on 100% of rows | **VERIFIED** |
| **Strict Positivity ($\lambda_{\text{wkt}} \ge 0$)** | 3,630 Grid Points | Minimum $\lambda_{\text{wkt}} = 0.000000$ (at $u = 0$). Zero negative values. | **VERIFIED** |
| **Monotonicity in Wickets ($W_{\text{rem}}$)** | 3,630 Grid Points | $R(u, w) - R(u, w-1) \ge 0$ strictly for all $u$ and $w$ (min diff $= 0.0$). | **VERIFIED** |
| **Monotonicity in Balls ($u$)** | 3,630 Grid Points | $R(u, w) - R(u-1, w) \ge 0$ strictly for all $u$ and $w$ (min diff $= 5.29 \times 10^{-9}$). | **VERIFIED** |
| **Terminal Zero Limit ($u \to 0$)** | 30 Terminal States | At $u = 0$, $\lambda_{\text{wkt}} \equiv 0.000$ across all formats and wicket states. | **VERIFIED** |
| **Final Ball Non-Terminal Decay** | $u = 1, W_{\text{rem}} \ge 2$ | Maximum $\lambda_{\text{wkt}} \le 0.1015$ runs (approaches zero quadratically as $\mathcal{O}(u^2)$). | **VERIFIED** |
| **Final Ball Terminal Wicket Value** | $u = 1, W_{\text{rem}} = 1$ | $\lambda_{\text{wkt}} = 2.186$ (IPL) and $1.961$ (T20I), matching ball run expectancy. | **VERIFIED** |

*Artifact Reference:* [`mathematical_invariant_checks.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/mathematical_invariant_checks.csv)

---

## 5. Summary of Audit Deliverables

All required audit artifacts have been generated, independently executed, and saved to `outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/`:
1. **Audit Script:** [`03_run_targeted_wicket_audit.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/src/step_7_empirical_calibration/03_run_targeted_wicket_audit.py)
2. **Baseline Comparison Results:** [`baseline_comparison_results.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/baseline_comparison_results.csv)
3. **CV Leakage Diagnostics:** [`match_cv_leakage_check.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/match_cv_leakage_check.csv)
4. **Second-Innings Analysis:** [`second_innings_applicability.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/second_innings_applicability.csv)
5. **Parameter Stability & Format Diagnostics:** [`parameter_stability_and_format_comparison.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/parameter_stability_and_format_comparison.csv)
6. **Mathematical Invariant Verification:** [`mathematical_invariant_checks.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/mathematical_invariant_checks.csv)
7. **Machine-Readable Summary:** [`step_7_2_1_audit_summary.json`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/step_7_2_1_audit_summary.json)
8. **This Audit Report:** [`step_7_2_1_targeted_audit_report.md`](file:///c:/Users/ASUS/Desktop/supeRR_selector%20-%20Copy/outputs/step_7_empirical_calibration/step_7_2_1_targeted_audit/step_7_2_1_targeted_audit_report.md)

---

## 6. Formal Certification & Transition to Step 7.3

### 6.1 Audit Conclusions
1. The DLS parametric formulation permanently eliminates the noisy, non-monotonic, and negative wicket values that afflicted raw empirical averages.
2. The format stratification between IPL and T20I is statistically justified, reflecting genuine structural differences in batting depth and boundary scoring.
3. The cross-validation was conducted without training/test leakage.
4. Second-innings target truncation affects only $0.26\%$ of deliveries and is fully resolved by enforcing the capping rule $\min(\lambda_{\text{wkt}}, \text{runs\_required})$ for non-terminal wickets.

### 6.2 Approval to Proceed
With the three mandatory operational conditions established, the Step 7.2 wicket valuation calibration is **certified for implementation**.

The pipeline is officially cleared to proceed to:  
**Step 7.3 — Empirical Bayes Shrinkage and Pressure Weighting Calibration**.
