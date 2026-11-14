# Audit Investigation 3: Bayesian K Value & Shrinkage Validation

## Executive Summary

Step 11 asserted that the official prior weight $K=50$ 'excessively shrinks' player metrics toward the population prior, proposing theoretical values of $K_{\text{bat}} \approx 38.2$ and $K_{\text{bow}} \approx 29.0$.

### Critical Audit Findings:
1. **Derivation Audit: The Step 11 Proposed Values Were Stylized Assumptions, Not Fitted Optimizations:**
   - Step 11 did **not** optimize an objective function or perform machine learning / cross-validation.
   - It applied a standard textbook normal-normal shrinkage formula $K = \sigma^2_{\text{within}} / \tau^2_{\text{between}}$ using **stylized assumed constants** (e.g., within-player variance $\sigma^2 \approx 1.85$, talent spread $\tau \approx 0.22$).
   - **Zero held-out predictive validation** was performed in Step 11 to evaluate whether $K=38.2$ or $K=29.0$ actually forecasts future player performance better than $K=50$.
2. **Time-Aware Chronological Validation Results (2022–2024 Train vs 2024–2026 Test):**
   - When evaluated across 789 matches on independent subsequent performances:
   - **Batters (N=83 common qualifiers):** Raw unadjusted strike rate ($K=0$) produces massive prediction error (RMSE = 41.02). Bayesian shrinkage drops RMSE to 34.00 at $K=38$, 33.59 at $K=50$, and 33.10 at $K=100$. The error curve is virtually flat between $K=38$ and $K=75$.
   - **Bowlers (N=92 common qualifiers):** Raw economy ($K=0$) has RMSE = 2.51. Shrinkage reduces error to 2.15 at $K=29$, **2.10 at $K=50$**, and 2.06 at $K=100$.
3. **Empirical Verdict: $K=50$ is Statistically Defensible and Outperforms Lower K:**
   - In out-of-sample forecasting, $K=50$ achieves **lower RMSE and MAE than the proposed $K=29$ and $K=38$**.
   - Because high-pressure sample sizes in T20 are small and noisy, stronger shrinkage provides necessary regularization against short-term volatility.
   - Step 11's claim that $K=50$ was a 'methodological flaw' is **refuted by empirical predictive validation**.

---

## 1. Out-of-Sample Predictive Performance Across K Values

| Discipline | Metric | K Value | Sample N | Out-of-Sample RMSE | Out-of-Sample MAE | Correlation with Future Perf | Assessment |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| Batting | Strike Rate | **0** | 83 | **41.02** | **32.54** | 0.2350 | Alternative |
| Batting | Strike Rate | **20** | 83 | **35.39** | **28.66** | 0.2387 | Alternative |
| Batting | Strike Rate | **29** | 83 | **34.52** | **28.04** | 0.2393 | Alternative |
| Batting | Strike Rate | **30** | 83 | **34.45** | **27.99** | 0.2393 | Alternative |
| Batting | Strike Rate | **38** | 83 | **34.00** | **27.69** | 0.2395 | Proposed Step 11 |
| Batting | Strike Rate | **50** | 83 | **33.59** | **27.34** | 0.2395 | Baseline |
| Batting | Strike Rate | **75** | 83 | **33.21** | **26.89** | 0.2390 | Alternative |
| Batting | Strike Rate | **100** | 83 | **33.10** | **26.65** | 0.2384 | Alternative |
| Bowling | Economy Rate | **0** | 92 | **2.51** | **2.02** | 0.1783 | Alternative |
| Bowling | Economy Rate | **20** | 92 | **2.20** | **1.78** | 0.2006 | Alternative |
| Bowling | Economy Rate | **29** | 92 | **2.15** | **1.74** | 0.2037 | Proposed Step 11 |
| Bowling | Economy Rate | **30** | 92 | **2.15** | **1.73** | 0.2040 | Alternative |
| Bowling | Economy Rate | **38** | 92 | **2.12** | **1.71** | 0.2054 | Alternative |
| Bowling | Economy Rate | **50** | 92 | **2.10** | **1.67** | 0.2063 | Baseline |
| Bowling | Economy Rate | **75** | 92 | **2.07** | **1.65** | 0.2064 | Alternative |
| Bowling | Economy Rate | **100** | 92 | **2.06** | **1.63** | 0.2055 | Alternative |

---

## 2. Answers to Specific Audit Questions

1. **What objective function was optimized in Step 11?**
   - **None.** No likelihood or loss function was minimized. The values were calculated from stylized closed-form ratios.
2. **Was held-out validation performed?**
   - **No.** Step 11 evaluated rank stability internally on the training set, risking overfitting to sample noise.
3. **Is $K=50$ appropriate?**
   - **Yes.** In chronological train/test splits, $K=50$ beats $K=29$ and $K=38$ in both RMSE and MAE for bowlers and batters.
4. **What is the genuine weakness of the Bayesian implementation?**
   - The weakness is **not the shrinkage weight $K$**; it is the **prior mean $\mu$**.
   - The prior mean was calculated over all 188,097 balls (including tail-enders and part-time bowlers), pulling regular clutch performers toward an artificially weak baseline.

---
*(Report generated automatically by Step 11.2 Independent Audit - Investigation 3)*