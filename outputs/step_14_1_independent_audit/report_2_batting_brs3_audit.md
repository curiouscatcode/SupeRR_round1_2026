# Investigation 2: Batting Metric (BRS3) Audit Report

**Module:** Step 14.1 — Independent Audit of Step 14 Findings  
**Date:** November 13, 2026  
**Audit Target:** Step 14 Investigation B & Batting Reliability ($BRS_3$)  
**Status:** **AUDIT COMPLETED — STATISTICAL CONFIRMATION WITH REPORTING CORRECTIONS**  

---

## 1. Executive Summary

Investigation 2 independently audited the claims made in Step 14 regarding the three-component batting reliability metric:
$$BRS_3 = 0.45 \cdot \text{Score}_{\text{SR}} + 0.35 \cdot \text{Score}_{\text{Surv}} + 0.20 \cdot \text{Score}_{\text{Diff}}$$

### Key Audit Conclusions:
1. **Mathematical Collinearity Verified:** The reported correlation between Strike Rate and Boundary Execution is **numerically verified at $r = 0.9638$ ($R^2 = 92.89\%$)** in Tier 1, and $r = 0.9701$ ($R^2 = 94.11\%$) across all 816 batters. The claim that official v2.0 contained severe multicollinearity is completely substantiated.
2. **Equating High Correlation with Complete Redundancy is an Overstatement:** While $92.89\%$ of Boundary Execution variance is collinear with Strike Rate, the remaining **$7.11\%$ of independent variance** captured explicit boundary-seeking vs. strike-rotation preferences (e.g. 6 singles vs. 1 boundary + 5 dots). Removing Boundary Execution is a defensible simplification, but it discarded this distinct boundary preference rather than proving it mathematically identical.
3. **Reporting Contradictions Regarding Batting Orders:** Step 14 reports contain major numerical contradictions regarding role distributions in Tier 1:
   - `report_b_batting_reliability.md` reported: Top Order = 41, Middle Order = 52, Finishers = 38 (Total = 131, omitting 15 qualifiers).
   - `step_14_final_methodological_validation_report.md` reported: Top Order = 48, Middle Order = 56, Finishers = 42 (Total = 146).
   - Actual Dataset (`exp14_batter_full_population_evaluation.csv`) shows: **Tailenders/Lower Order (8+) = 50, Middle Order (4–5) = 45, Finishers (6–7) = 37, Top Order (1–3) = 14**.
4. **Factual Error Regarding Top Performers:** The Step 14 final report asserted that Top Order was *'Led by Virat Kohli, Rank 9'* and Middle Order was *'Led by Heinrich Klaasen, Rank 7'*. Both statements are **factually false**:
   - **Virat Kohli** faced only $N=47$ high-pressure deliveries and is in **Tier 2 (Rank 9 in Tier 2)**, not Tier 1 Rank 9 (Tier 1 Rank 9 is George Dockrell).
   - **Heinrich Klaasen** is ranked **85th in Tier 1** ($BRS_3 = 50.22$), not 7th (Tier 1 Rank 7 is Jamie Overton).

---

## 2. Mathematical vs. Cricketing Breakdown

| Dimension | Mathematical Finding | Cricketing Interpretation | Audit Status |
| :--- | :--- | :--- | :---: |
| **Collinearity** | $r = 0.9638$ ($R^2 = 92.89\%$) between SR and Exec. | Boundary Execution was effectively an 85% Strike Rate proxy with an extra dot penalty. | **Verified** |
| **Redundancy** | $7.11\%$ of Exec variance is independent of SR. | Discards distinction between boundary-hitters and strike-rotators; acceptable trade-off for simplicity. | **Qualified** |
| **Survival Trade-off** | $r = 0.4297$ between SR and Survival in Tier 1. | Balances aggressive boundary hitters against wicket preservation. | **Verified** |
| **Role Equity** | Finishers average $BRS_3 = 56.8$, Top Order averages $54.3$. | Death hitters gain a small premium reflecting high RRR demands. | **Verified** |

---

## 3. Discrepancy Table for Batting Audit

| Discrepancy ID | Item | Step 14 Claim | Verified Reality | Severity | Classification |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **DISC-05** | Redundancy Scope | 'Removing Boundary Execution preserves all essential information.' | $7.11\%$ of Boundary Execution variance was independent; distinct boundary preference is lost. | **Low** | Statistical Qualification |
| **DISC-06** | Tier 1 Role Counts | Top Order 48, Middle 56, Finishers 42. | Dataset has Tailenders (8+) 50, Middle 45, Finishers 37, Top Order 14. | **High** | Factual Contradiction |
| **DISC-07** | Kohli Tier 1 Rank | 'Top Order led by Virat Kohli, Rank 9.' | Virat Kohli has $N=47$; he is in **Tier 2 (Rank 9)**, not Tier 1. Tier 1 Rank 9 is George Dockrell. | **High** | Factual Error |
| **DISC-08** | Klaasen Tier 1 Rank | 'Middle Order led by Heinrich Klaasen, Rank 7.' | Heinrich Klaasen is **Rank 85 in Tier 1** ($BRS_3 = 50.22$). Tier 1 Rank 7 is Jamie Overton. | **High** | Factual Error |

---

## 4. Final Recommendation for Investigation 2

- **Adopt $BRS_3$ with Explicit Qualifications:** $BRS_3$ is mathematically sound and successfully eliminates severe multicollinearity. Retain it as the production standard.
- **Correct Documentation Errors:** Immediately correct the erroneous player references (Kohli, Klaasen) and role count distributions in all presentation summaries.