# Independent Win-Probability & Leverage Audit (Part C)

**Audit Date:** 2026-11-14  
**Auditor:** Independent Analytics Auditor  
**Scope:** Technical Verification of Step 16.4's WP Model & Leverage Benchmark  

---

## 1. Technical Audit Findings on the 7 Specific Requirements

### 1. Training and Evaluation Separation by Match
- **Audit Finding:** In Step 16.4 Script 04, the models were trained **in-sample** across all deliveries without a train/test split or cross-validation.  
- **Independent Verification:** We performed a 5-fold match-level grouped cross-validation (GroupKFold on `match_id`). The results confirm that overfitting was negligible:
  * Innings 2: In-sample Brier = `0.1342` vs Out-of-fold CV Brier = `0.1352` (Delta = `0.0010`).
  * Innings 1: In-sample Brier = `0.2227` vs Out-of-fold CV Brier = `0.2240` (Delta = `0.0013`).
- **Conclusion:** Although methodologically in-sample, the low dimensionality ($4\text{--}5$ parameters on $>85,000$ balls) prevented overfitting.

### 2. Pre-Delivery Feature Verification (Zero Post-Delivery Leakage)
- **Audit Finding: VERIFIED.** All input features (`runs_required`, `balls_remaining`, `wickets_before`, `score_before`, `legal_balls_before`, `current_run_rate`) are strictly evaluated immediately prior to the ball being bowled. No delivery outcomes (`runs`, `is_wicket`, extras) leak into the feature space.

### 3. Appropriate Handling of Innings 1 and Innings 2
- **Audit Finding: VERIFIED with Caveat.**  
  * Innings 2 explicitly models target chase dynamics with interaction ($RRR \times \text{Wickets Remaining}$).  
  * Innings 1 assumes a fixed par score of 160. Because pitch par varies from 130 to 210, Innings 1 WP has higher intrinsic noise (Brier score 0.224 vs 0.135 in Innings 2). Both are monotonic and appropriate for baseline leverage benchmarking.

### 4. Model Calibration Verification
- **Audit Finding: VERIFIED.**  
  * Innings 2 is exceptionally calibrated across all 10 deciles (mean absolute calibration gap = `0.007` or 0.7 percentage points).
  * Innings 1 is well-calibrated (mean absolute calibration gap = `0.021` or 2.1 percentage points).
  * See full decile breakdown in `outputs/step_16_4_1_audit/wp_calibration_table.csv`.

### 5. Expected Leverage Calculation Over Next-Delivery Outcomes
- **Audit Finding: VERIFIED.** Leverage is calculated strictly as $\mathbb{E}[|\Delta \text{WP}|] = \sum_k P(O_k) \cdot |\text{WP}(S_{t+1}(O_k)) - \text{WP}(S_t)|$ over empirical outcome frequencies (dots, 1s, 2s, 4s, 6s, wickets, extras) summing to 1.0000.

### 6. Exclusion of Actual Delivery Outcome
- **Audit Finding: VERIFIED.** The actual result of delivery $t$ is completely excluded from $\mathbb{E}[|\Delta \text{WP}|]$.

### 7. Representativeness of the 5,000-Delivery Sample CSV
- **Audit Finding: DEFECT IDENTIFIED in Artifact Export.**  
  * The file `match_leverage_validation_data.csv` was generated via `bat_df.head(5000)`.  
  * It contains deliveries from only **22 matches out of 789** (the earliest chronological matches).
  * Mean leverage in that sample is **1.50%** compared to **1.34%** in the full population.
  * Lower-order share in that sample is **11.98%** compared to **14.31%** in the full population.
  * **Crucial Clarification:** However, the summary statistics in `leverage_summary_by_subgroup.csv` WERE correctly computed on the entire 180,839 population. The flaw was restricted to the exported sample CSV file.

---

## 2. Why Overall High-Pressure Deliveries Have Lower Estimated Leverage

In Step 16.4, High Pressure deliveries had lower leverage than Non-HP deliveries (1.07% vs 1.41%). Step 16.4 dismissed this as a conceptual distinction between 'task difficulty' and 'game leverage'.

Our audit provides the **exact empirical and mathematical proof** of why this happens:

### 1. Mathematical Structure of Leverage
For any standard logistic win probability model $P(W) = \frac{1}{1 + e^{-\eta}}$, the marginal swing (derivative) is:
$$\frac{\partial P(W)}{\partial \eta} = P(W) \cdot (1 - P(W))$$
This function is strictly concave and symmetric, reaching its global maximum at **$P(W) = 0.50$** (value = $0.25$).  
When $P(W) = 0.05$ (hopeless game) or $P(W) = 0.95$ (blowout win), $P(W)(1 - P(W)) = 0.0475$—**over 5.2 times smaller**!

### 2. Empirical Distribution of Win Probability in High Pressure Deliveries
- In Innings 2, **58.2% of all High Pressure deliveries have Win Probability $< 10\%$**!
- The mean Win Probability of Innings 2 High Pressure deliveries is only **12.6%** (median: **7.1%**).
- In contrast, Non-HP deliveries in Innings 2 have a mean Win Probability of **54.7%** (median: **57.1%**), with **32.3%** of balls occurring in close games ($WP \in [0.30, 0.70]$).

### 3. The Core Mechanism of Mismatch
1. **High Leverage requires Balance:** A delivery swings the match when either team can win ($WP \approx 50\%$). In balanced games, required run rates are reasonable (7–10 RPO) and wickets remain in hand. Therefore, the Pressure Index formula gives them **LOW to MODERATE PI**, classifying them as $Z \le 1.00$!
2. **High PI requires Crisis:** The PI formula requires extreme required run rates (14–22 RPO) and heavy wicket depletion ($W \ge 7$). In professional T20 cricket, teams in this state have almost certainly **already lost** ($WP < 8\%$). In those blowout states, a six or a wicket changes the outcome by less than $0.3\%$.

> **Audit Verdict:**  
> The lower leverage of High Pressure deliveries is **not a modeling error**, but an **intrinsic limitation of the Pressure Index formula**.  
> The Pressure Index is fundamentally a **Crisis / Resource Depletion Index**, not a **Competitive Tension Index**. It systematically overweights lost-cause collapses where match outcome is settled, and systematically misses tense, knife-edge finishes where wickets are in hand.
