# Audit Investigation 2: Batting Metric Collinearity & Variance Validation

## Executive Summary

Step 11 reported that Strike Rate and Boundary Execution correlate at $r = 0.9628$, and claimed that combined scoring speed dominates **68.07%** of the effective variance in the Batting Reliability Score (BRS), thereby marginalizing Survival Rate.

### Independent Audit Conclusions:
1. **Collinearity is Fully Confirmed Across All Subpopulations:** The Pearson correlation between Strike Rate and Boundary Execution is **$r = 0.9628$ in Tier 1**, **$r = 0.9638$ across all 816 batters**, and $r = 0.9636$ in Tier 2. The relationship is extraordinarily robust and invariant.
2. **The 68.07% Variance Claim is Confirmed but Requires Methodological Qualification:**
   - In marginal covariance decomposition (where total portfolio variance is partitioned via $w_i \text{Cov}(X_i, S) / \text{Var}(S)$), Strike Rate accounts for **45.65%** and Boundary Execution accounts for **22.42%**, summing to exactly **68.07%**.
   - However, **59.42% of total BRS variance is shared cross-covariance**, and the mutual covariance between Strike Rate and Boundary Execution alone represents **21.85% of the entire BRS variance**.
   - Because BRS is linearly composed of these components, regressing BRS on its components is an identity, and assigning shared covariance to individual components depends on the chosen attribution convention.
3. **Boundary Execution Contains Only 7.30% Independent Residual Information:** $R^2 = 0.9270$, meaning 92.7% of Boundary Execution is statistically redundant with Strike Rate.
4. **Cricketing Evaluation of Boundary Execution:** While statistically collinear, Boundary Execution captures whether runs are scored via boundaries vs non-boundary strike rotation. However, because both components reward boundaries simultaneously, the official model imposes an unintentional double reward on boundary hitters at the expense of anchors.

---

## 1. Inter-Component Correlation Matrices

### Tier 1 Qualified Batters (N=116)

| Component | Strike Rate (0.40) | Survival Rate (0.25) | Boundary Exec (0.20) | Clutch Diff (0.15) |
| :--- | :---: | :---: | :---: | :---: |
| **score_sr** | 1.0000 | 0.4722 | 0.9628 | 0.5544 |
| **score_surv** | 0.4722 | 1.0000 | 0.5133 | 0.2430 |
| **score_exec** | 0.9628 | 0.5133 | 1.0000 | 0.5549 |
| **score_diff** | 0.5544 | 0.2430 | 0.5549 | 1.0000 |

---

## 2. Decomposition of Total BRS Variance

Total Tier 1 BRS Variance is $\text{Var}(\text{BRS}) = 233.66$. Decomposing into unique vs shared terms:

| Component | Nominal Formula Weight | Component Variance $\sigma^2$ | Unique Variance Share ($w_i^2 \sigma_i^2 / \text{Var}$) | Marginal Covariance Share ($w_i \text{Cov}(X_i, S) / \text{Var}$) | Difference vs Nominal |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **score_sr** | 40.0% | 338.48 | **23.18%** | **45.65%** | +5.65% |
| **score_surv** | 25.0% | 313.90 | **8.40%** | **19.80%** | -5.20% |
| **score_exec** | 20.0% | 324.58 | **5.56%** | **22.42%** | +2.42% |
| **score_diff** | 15.0% | 357.91 | **3.45%** | **12.14%** | -2.86% |

> [!IMPORTANT]
> **Statistical Insight on Shared Covariance:** The sum of unique variances across all 4 components is only **40.58%**. The remaining **59.42%** of BRS variance is shared cross-covariance, dominated by the massive covariance between Strike Rate and Boundary Execution (21.85%). The marginal covariance method splits this shared covariance between the two metrics, producing the 68.07% total.

---

## 3. Does Boundary Execution Contribute Meaningful Information Beyond Strike Rate?

Regressing Boundary Execution on Strike Rate ($Y = \beta X + \epsilon$):
- **$R^2 = 0.9270$ (92.70%)**
- **Independent Residual Variance:** **7.30%**

### Cricketing Interpretation:
1. The 7.3% residual represents batters who score via extreme boundary-or-dot distributions vs strike rotators.
2. However, in T20 match chasing, an innings of 20 runs off 10 balls with (2 sixes, 1 four, 7 dots) provides essentially the same scoreline as 20 runs off 10 balls with (1 four, 8 twos). The official model, by including Boundary Execution as an independent 20% component, double-rewards the boundary hitter while penalizing the strike rotator.
3. Therefore, while Boundary Execution is not 'wrong', it is statistically redundant and structurally biases the model toward boom-or-bust power hitters.

---
*(Report generated automatically by Step 11.2 Independent Audit - Investigation 2)*