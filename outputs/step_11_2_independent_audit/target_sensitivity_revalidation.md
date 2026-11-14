# Audit Investigation 7: Target Sensitivity & Shoriful Islam Revalidation

## Executive Summary

Step 11 concluded that the player reliability ranking model is extraordinarily robust to target reconstruction issues in the 38 flagged matches (4,177 deliveries), reporting Spearman rank correlations of **0.9945 (batters)** and **0.9852 (bowlers)**.

### Independent Audit Conclusions:
1. **Correlations Fully Confirmed:**
   - **Batters:** Spearman $\rho = \mathbf{0.9945}$ across all common Tier 1 batters ($N=116$). Top 10 overlap is **10/10 (100%)**.
   - **Bowlers:** Spearman $\rho = \mathbf{0.9852}$ across all common Tier 1 bowlers ($N=111$). Top 10 overlap is **9/10 (90%)**.
2. **Treatment of the Player Population:**
   - The correlation calculation in Step 11 was computed across **common players who remained in Tier 1 in both regimes**.
   - In batting, all 116 baseline Tier 1 batters remained in Tier 1 in the sensitivity regime ($N=116$).
   - In bowling, 111 of the 113 baseline Tier 1 bowlers remained in Tier 1 ($N=111$). Two bowlers dropped below 60 balls: **Shoriful Islam** (61 balls $\rightarrow$ 57 balls) and **Josh Little** (61 balls $\rightarrow$ 58 balls).
3. **How a High Correlation Coexists with Discrete Tier Ejections:**
   - Spearman correlation is a measure of rank order preservation among continuous scores. For the 111 common bowlers, relative ranks shifted by only $\pm 1$ position on average.
   - However, the qualification boundary is a **discontinuous Heaviside step function** ($I(N \ge 60)$).
   - Shoriful Islam was not displaced by lower performance; his underlying performance actually improved slightly in the clean subset (BoRS $74.01 \rightarrow 74.22$). He was excluded entirely because the step function ejected him into Tier 2.
   - This proves that high overall rank correlation does **not** prove absence of threshold sensitivity for individual players on the boundary.

---
*(Report generated automatically by Step 11.2 Independent Audit - Investigation 7)*