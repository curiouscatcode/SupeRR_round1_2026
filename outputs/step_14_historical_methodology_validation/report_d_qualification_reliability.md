# Investigation D: Qualification & Sample Reliability (Rule B Audit)

**Module:** Step 14 — Independent Historical Methodology Validation  
**Date:** November 13, 2026  
**Status:** Completed  
**Artifact Link:** [04_qualification_rule_b_boundary_clustering.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_14_historical_methodology_validation/04_qualification_rule_b_boundary_clustering.png)  
**Data Source:** [exp14_qualification_boundary_analysis.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_14_historical_methodology_validation/exp14_qualification_boundary_analysis.csv)  

---

## 1. Executive Summary & Core Verdict

Investigation D independently audited the mathematical defensibility, sample efficiency, and boundary behavior of **Rule B Qualification**:
- **Tier 1:** $N \ge 60 \text{ OR } (N \ge 50 \text{ AND } M \ge 6)$
- **Tier 2:** $N < 60$ not qualifying for Tier 1, but with $N \ge 40$.

### Key Findings:
1. **Volume vs. Breadth Balance:**
   - **Batters (N=816):** 116 qualify via Direct Volume ($N \ge 60$) and 30 qualify via Dual Constraint ($N \in [50, 59], M \ge 6$), totaling **146 Tier 1 Batters**.
   - **Bowlers (N=589):** 113 qualify via Direct Volume ($N \ge 60$) and 17 qualify via Dual Constraint ($N \in [50, 59], M \ge 6$), totaling **130 Tier 1 Bowlers**.
   - **Near-Misses:** Exactly **0 batters** and **2 bowlers** fall in the $N \in [50, 59], M < 6$ boundary window: **Yash Punja** ($N=54, M=5$) and **Auqib Nabi** ($N=51, M=5$).

2. **Boundary Defensibility (Yash Punja & Auqib Nabi):**
   - Auqib Nabi bowled 51 high-pressure balls across 5 matches, but **47.3% (26 deliveries) occurred in a single match (ID: 50376)**, while another match had only 1 delivery.
   - Yash Punja bowled 54 high-pressure balls across 5 matches, with **33.9% (19 deliveries) in a single match (ID: 50373)**.
   - In contrast, Dual-Constraint qualifiers ($M \ge 6$) have an average top-1 match concentration of **22.4% for bowlers** and **24.1% for batters**.
   - The $M \ge 6$ boundary is methodologically defensible: it acts as a robust filter against single-match tournament outliers.

3. **Intraclass Correlation (ICC) & Effective Sample Size ($N_{\text{eff}}$):**
   - Deliveries within the same match share common context (pitch condition, opponent strength, dew, game flow).
   - At an intraclass correlation of $\text{ICC} = 0.10$ (standard for leverage/scoring metrics):
     - A Dual Qualifier at the boundary ($N=50, M=6$) has an average deliveries per match $\bar{m} = 8.33$, yielding $\text{DEFF} = 1.73$ and **$N_{\text{eff}} = 28.9$**.
     - Auqib Nabi ($N=51, M=5$) has $\bar{m} = 10.2$, yielding $\text{DEFF} = 1.92$ and **$N_{\text{eff}} = 26.6$**.
     - Yash Punja ($N=54, M=5$) has $\bar{m} = 10.8$, yielding $\text{DEFF} = 1.98$ and **$N_{\text{eff}} = 27.3$**.
   - **Crucial Mathematical Insight:** Dual-constraint qualifiers with lower nominal $N$ actually possess a **higher effective sample size** than the near-misses due to lower match clustering! The dual constraint is mathematically superior to an unconstrained volume cutoff.

4. **Bayesian Shrinkage Mitigation:**
   - Under the Bayesian shrinkage prior ($K=50$), a player with $N=50$ receives a $50.0\%$ weight on their observed performance and $50.0\%$ weight on the global population mean.
   - This prevents borderline qualifiers from artificially inflating ratings based on noisy data.

5. **Role Equity:**
   - Batters face higher delivery variance per innings than bowlers (who have a hard ceiling of 24 balls per match).
   - Rule B expands the batter pool by $+25.9\%$ (from 116 to 146) and the bowler pool by $+15.0\%$ (from 113 to 130), restoring proportional representation without sacrificing statistical rigor.

**Verdict on Qualification:** **RETAIN RULE B QUALIFICATION AS PRODUCTION STANDARD.**

---

## 2. Full Population Qualification Cohort Distribution

| Cohort | Batter Count | % of Batters | Bowler Count | % of Bowlers | Methodological Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **T1 Direct ($N \ge 60$)** | 116 | 14.2% | 113 | 19.2% | Full sample confidence; $\lambda \ge 0.545$. |
| **T1 Dual ($50 \le N < 60, M \ge 6$)** | 30 | 3.7% | 17 | 2.9% | Verified breadth; low match clustering ($N_{\text{eff}} \ge 28.5$). |
| **T1 Near-Miss ($50 \le N < 60, M < 6$)** | 0 | 0.0% | 2 | 0.3% | High clustering (Auqib Nabi 47.3% in 1 match); appropriately routed to Tier 2. |
| **Tier 2 Specialist ($40 \le N < 50$ or Near-Miss)** | 42 | 5.1% | 19 | 3.2% | Published with sample caveats; heavy prior shrinkage ($\lambda \in [0.44, 0.52]$). |
| **Unranked ($N < 40$)** | 628 | 77.0% | 440 | 74.7% | Insufficient sample; ratings dominated by global prior ($\lambda < 0.44$). |
| **Total Population** | **816** | **100.0%** | **589** | **100.0%** | Complete historical registry. |

---

## 3. Boundary Near-Miss Audits: Yash Punja vs. Auqib Nabi

| Player Name | Role | Deliveries ($N$) | Matches ($M$) | Deliveries/Match ($\bar{m}$) | Top-1 Match Share (%) | $N_{\text{eff}}$ ($\text{ICC}=0.10$) | Score | Assigned Tier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Auqib Nabi** | Bowler | 51 | 5 | 10.20 | **47.3%** | 26.56 | 35.79 | **Tier 2 (Rank 13)** |
| **Yash Punja** | Bowler | 54 | 5 | 10.80 | **33.9%** | 27.27 | 51.56 | **Tier 2 (Rank 5)** |
| **Mean Dual Qualifiers** | Bowler | 54.1 | 7.9 | 6.85 | **22.4%** | **34.12** | 50.84 | **Tier 1 (Qualified)** |

> [!IMPORTANT]
> **Why the Exclusion from Tier 1 is Methodologically Justified:**
> Auqib Nabi's high-pressure sample was heavily concentrated in Match 50376 (26 balls out of 51 legal balls). Placing him in Tier 1 would make his ranking overwhelmingly a reflection of a single match against a single opponent under specific ground conditions. Requiring $M \ge 6$ ensures multi-opponent, multi-condition reliability.

---

## 4. Final Recommendation for Investigation D

- **Conclusion:** **RETAIN Rule B Qualification ($N \ge 60 \lor [N \ge 50 \land M \ge 6]$ for Tier 1; $N \ge 40$ for Tier 2).**
- **Statistical Justification:** Maximizes information efficiency while strictly guarding against single-match leverage bias via the empirical $M \ge 6$ constraint and Bayesian shrinkage ($K=50$).