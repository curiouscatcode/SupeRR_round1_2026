# Balls-Faced Matched-Context Audit (Part B)

**Audit Date:** 2026-11-14  
**Auditor:** Independent Analytics Auditor  
**Focus:** Controlling for `striker_balls_faced_before` in Matched-Context Analysis  
**Reference Baseline:** Step 16.4 Unadjusted Gap (+45.30 pp) & Matched Gap (+44.67 pp)  

---

## 1. Executive Summary: The Dissolution of the Matched Gap

In Step 16.4, an exact match on $(Inn \times Phase \times Wickets)$ reported a persistent matched gap of **+44.67 percentage points** between Lower Order and Top Order batters. That investigation concluded the gap was an intrinsic cricket reality.

However, when we include `striker_balls_faced_before` as a diagnostic matching variable, an extraordinary transformation occurs:

- **Step 16.4 Matched Gap (without BF matching):** **+44.67 pp** (Top: 2.80%, Lower: 47.47%)
- **Step 16.4.1 Matched Gap (WITH BF matching):** **+0.23 pp** (Top: 2.96%, Lower: 3.19%)
- **95% Clustered Bootstrap CI for Matched Gap:** **[-1.43 pp, 1.78 pp]**
- **Percentage of Step 16.4 Matched Gap Explained by Balls Faced:** **99.5%**!

Over **95% of the matched gap reported in Step 16.4 was not driven by match-state pressure or role-specific courage**; it was mechanically created because top-order batters in the comparison cells were set ($BF \approx 44, I = 0$) while lower-order batters were newly arrived ($BF \approx 7, I \approx 48$)!

---

## 2. Standardized Comparison Table

| Batting Role | Total Population Balls | Unadjusted HP % | Viable Support Balls | Viable Support Unadjusted HP % | Standardized HP % | 95% Clustered Bootstrap CI | Mean PI (Viable) | Mean $I$ (Viable) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Top Order (1-3)** | 90,068 | 7.06% | 2,132 | 2.53% | **2.96%** | [1.65%, 4.37%] | 35.11 | 0.00 |
| **Middle Order (4-6)** | 64,887 | 19.73% | 9,775 | 1.83% | **2.42%** | [1.77%, 3.20%] | 36.39 | 0.00 |
| **Lower Order (7-11)** | 25,884 | 52.36% | 5,765 | 4.54% | **3.19%** | [2.39%, 3.98%] | 42.73 | 0.00 |
| **Lower minus Top Gap** | — | **+45.30 pp** | — | **+2.01 pp** | **+0.23 pp** | **[-1.43 pp, +1.78 pp]** | **+7.62** | **+0.00** |

---

## 3. Analysis of Common Support Across Balls-Faced Ranges

When matching on $(Inn \times Phase \times Wickets \times BF\_bin)$, there are exactly **16 viable cells** where Top, Middle, and Lower order all have $\ge 10$ deliveries.

### Critical Common Support Insight:
1. **All 16 viable cells occur exclusively in the `10+` (fully set) bucket!**
   - Why? Because when wickets lost are high ($W \ge 5$), Top Order batters present in that phase are almost exclusively openers or #3s who have faced $\ge 10$ balls (mean $BF \approx 30\text{--}45$).
   - Conversely, when Top Order batters have $BF < 5$, wickets lost is almost always $0$ or $1$, where Lower Order batters NEVER bat (literally 0 deliveries).
2. **Within the `10+` Common Support Regime:**
   - Top Order, Middle Order, and Lower Order batters all have **$I = 0.00$**.
   - Top Order standardized capture rate is **2.96%**.
   - Middle Order standardized capture rate is **2.42%**.
   - Lower Order standardized capture rate is **3.19%**.
   - The resulting matched gap is only **+0.23 percentage points**!

### What Happens When Batters Are Cold ($BF < 5$)?
Although common support across all three roles does not exist for $BF < 5$ at high wickets, we can evaluate what happens when batters of different roles enter the crease cold:

| Role | Balls Faced Range | Deliveries | HP Capture Rate ($Z > 1$) | Mean PI | Mean $T$ | Mean $I$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Top Order (1-3) | 0–4 (Cold Arrival) | 21,878 | **27.64%** | 44.39 | 24.78 | 80.82 |
| Top Order (1-3) | 5–9 (Settling) | 17,264 | **1.44%** | 27.60 | 25.77 | 30.98 |
| Top Order (1-3) | 10+ (Fully Set) | 50,926 | **0.12%** | 17.79 | 27.37 | 0.00 |
| Middle Order (4-6) | 0–4 (Cold Arrival) | 19,869 | **55.44%** | 54.34 | 40.01 | 80.95 |
| Middle Order (4-6) | 5–9 (Settling) | 14,963 | **10.37%** | 37.79 | 41.29 | 31.31 |
| Middle Order (4-6) | 10+ (Fully Set) | 30,055 | **0.78%** | 29.36 | 45.16 | 0.00 |
| Lower Order (7-11) | 0–4 (Cold Arrival) | 13,453 | **82.19%** | 71.16 | 64.65 | 83.23 |
| Lower Order (7-11) | 5–9 (Settling) | 6,425 | **32.68%** | 54.03 | 65.52 | 32.69 |
| Lower Order (7-11) | 10+ (Fully Set) | 6,006 | **6.59%** | 43.08 | 66.28 | 0.00 |

---

## 4. Key Takeaways for the Audit

1. **The Step 16.4 Claim is Disproven:** Step 16.4 claimed that even under matched conditions, cricket reality dictates that lower-order batters experience a +44.67 pp higher pressure capture rate. That claim was invalid because it failed to control for the fact that top-order batters in the comparison were set ($I = 0$) while lower-order batters were cold ($I > 0$).
2. **Settling Accounts for 95% of the Matched Difference:** When both top-order and lower-order batters are set ($BF \ge 10$), their capture rates under identical match conditions are **2.53% vs 4.54%**—a negligible gap of only **+2.01 pp**.
3. **The Core Mechanism of the Bias:** The Pressure Index creates a powerful interaction between match situation ($T$) and individual balls faced ($I$). Because tailenders face short stints, they are evaluated almost entirely under the $+35.0$ point settling surcharge. Because top-order batters face long stints, over half their balls occur after the settling surcharge has vanished.
