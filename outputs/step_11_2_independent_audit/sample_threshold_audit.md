# Audit Investigation 6: Sample Threshold & Boundary Cliff Revalidation

## Executive Summary

Step 11 concluded that the 60-ball qualification threshold creates an artificial cliff that penalizes high-performing specialists who fall 1–5 balls short of Tier 1, while admitting borderline qualifiers.

### Independent Audit Conclusions:
1. **Edge-Case Figures are 100% Verified:**
   - **Jamie Overton:** Exactly **59 high-pressure balls**, $\text{BRS} = 79.54$. Barred from Tier 1 by 1 single ball; would rank **#6 in Tier 1** under a 50-ball cutoff.
   - **Nasum Ahmed:** Exactly **55 high-pressure legal balls**, $\text{BoRS} = 88.84$. Barred from Tier 1; would rank **#2 in Tier 1** under a 50-ball cutoff.
   - **Simarjeet Singh:** Exactly **60 balls**, $\text{BoRS} = 69.40$, officially ranked **#9 in Tier 1** on the exact boundary ball.
   - **Shoriful Islam:** Exactly **61 balls**, $\text{BoRS} = 74.01$, officially ranked **#5 in Tier 1**; dropping 4 flagged deliveries drops him to 57 balls, ejecting him into Tier 2.
2. **Statistical Uncertainty vs Eligibility Policy:**
   - From a purely statistical perspective, the estimation uncertainty of a player with 59 balls ($\text{SE} = 17.7$ pts) is indistinguishable from that of a player with 60 balls ($\text{SE} = 17.6$ pts).
   - However, any competition ranking requires an **eligibility policy boundary** to prevent unconstrained small-sample noise from polluting official podiums.
   - The official v2.0 design already addressed this by creating **Tier 2 (Specialist Cohort, 40–59 balls)**. Overton and Nasum were **not deleted**; they are ranked #2 and #1 in Tier 2.
3. **Should a Continuous Sigmoid Weighting Function Replace the Cutoff?**
   - While a continuous sigmoid function $W(N) = \frac{1}{1 + e^{-(N-50)/12}}$ smooths the step boundary, it introduces an arbitrary mathematical discount that shrinks small-sample players toward zero rather than shrinking them to the population mean (which Bayesian shrinkage already does).
   - **Recommendation:** Retain the 60-ball threshold as an eligibility filter, but improve presentation by publishing unified leaderboards with transparent sample-size confidence intervals rather than hard tier walls.

---

## 1. Population Inflow and Outflow Across Thresholds

| Threshold (Balls) | Batters Qualified | Batters Delta vs 60b | Batters % Population | Bowlers Qualified | Bowlers Delta vs 60b | Bowlers % Population | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **40** | 188 | +72 | 23.0% | 149 | +36 | 25.3% | Expanded Tier 1 |
| **50** | 146 | +30 | 17.9% | 132 | +19 | 22.4% | Expanded Tier 1 |
| **60** | 116 | +0 | 14.2% | 113 | +0 | 19.2% | Baseline |
| **70** | 94 | -22 | 11.5% | 96 | -17 | 16.3% | Contracted Tier 1 |
| **80** | 81 | -35 | 9.9% | 83 | -30 | 14.1% | Contracted Tier 1 |

---
*(Report generated automatically by Step 11.2 Independent Audit - Investigation 6)*