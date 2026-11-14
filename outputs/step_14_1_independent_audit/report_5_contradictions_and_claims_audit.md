# Investigation 5: Contradictions & Unsupported Claims Audit Report

**Module:** Step 14.1 — Independent Audit of Step 14 Findings  
**Date:** November 13, 2026  
**Audit Target:** Step 14 Final Report and Investigation Reports A–E  
**Status:** **AUDIT COMPLETED — 7 CONTRADICTIONS INVENTORIED & RESOLVED**  

---

## 1. Executive Summary

Investigation 5 conducted a line-by-line critical review of all Step 14 markdown reports and empirical datasets to identify incorrect calculations, unsupported claims, mathematical misnomers, and internal contradictions.

### Key Categories of Identified Contradictions:
1. **Factual Errors in Player Ranks:** Falsely placing Virat Kohli at Tier 1 Rank 9 (he is in Tier 2), Heinrich Klaasen at Rank 7 (he is Rank 85), and Nicholas Pooran in the Top 10 (he is Rank 12).
2. **Cohort Count Contradictions:** Presenting three conflicting sets of batting order counts for Tier 1 ($131$ in Report B, $146$ in the Final Report, and the true distribution of $50$ lower-order hitters/all-rounders in the dataset).
3. **Internal Report Contradictions:** Claiming $\rho \ge 0.988$ in prose while Table 2 of the same report displayed $\rho = 0.8627–0.8821$ (resolved by Audit 4 as an underlying script bug).
4. **Statistical Terminology Misnomers:** Describing component pairs with correlations of $r = 0.44$ to $0.58$ as 'orthogonal'.
5. **Overstated Proof Claims:** Declaring an illustrative model based on an assumed $\text{ICC} = 0.10$ to be an 'empirical mathematical proof'.

---

## 2. Detailed Inventory of Contradictions

| ID | Topic | Severity | Step 14 Claim | Verified Reality & Audit Correction |
| :---: | :--- | :---: | :--- | :--- |
| **CONT-01** | Player Ranks | **High** | 'Top Order led by Virat Kohli, Rank 9; Middle led by Klaasen, Rank 7.' | Kohli is Tier 2 ($N=47$). Tier 1 Rank 9 is George Dockrell. Klaasen is Rank 85 in Tier 1. |
| **CONT-02** | Batting Roles | **High** | Final report claimed Top 48, Middle 56, Finishers 42. | Actual dataset has 50 Tailenders/Lower Order, 45 Middle, 37 Finishers, 14 Top Order. |
| **CONT-03** | Sensitivity Text vs Table | **High** | Text claimed $\rho \ge 0.988$; Table showed $\rho = 0.8627$. | Script formula bug caused Table drop. True corrected value is $\rho = 0.9984$. |
| **CONT-04** | 'Orthogonality' Misnomer | **Medium** | Described BoRS bowling components as 'orthogonal'. | Correlations are $r = 0.22$ to $0.58$. Term should be 'low-to-moderate collinearity'. |
| **CONT-05** | Proof vs Assumption | **Medium** | Claimed 'mathematical proof' for dual constraint superiority. | ICC = 0.10 was assumed, not empirically estimated. Reframe as practical breadth policy. |
| **CONT-06** | Threshold Notation | **Low** | Alternated between 'PI > 60' and 'PI >= 60'. | Exact filter is $\text{PI} \ge 60.0$ (13,650 balls). Exactly 20 bat and 38 bowl balls are at 60.0. |
| **CONT-07** | Nabi Ball Count | **Low** | Cited $N=51$ in tables, but 26/55 ($47.3\%$) in concentration. | $N=51$ is legal balls; 55 includes 4 extras. Legal concentration is 24/51 ($47.06\%$). |

---

## 3. Final Recommendation for Investigation 5

- All seven items have been reconciled and logged in the project's permanent audit register.
- By correcting these editorial and numerical contradictions, the core historical reliability methodology remains **fully intact and substantially strengthened**.