# Investigation 4: Shrinkage Parameter (K) Sensitivity Audit Report

**Module:** Step 14.1 — Independent Audit of Step 14 Findings  
**Date:** November 13, 2026  
**Audit Target:** Step 14 Investigation E, Bayesian Shrinkage Sensitivity ($K \in [30, 70]$)  
**Status:** **AUDIT COMPLETED — CRITICAL SCRIPT BUG DISCOVERED & RESOLVED**  

---

## 1. Executive Summary & Root Cause Resolution

Investigation 4 investigated the glaring inconsistency in Step 14 where:
- Table 2 reported a severe drop in Batting Spearman correlation for $K=30–70$ down to **$\rho = 0.8627–0.8821$** (with Top 10 overlap collapsing to 6/10).
- Bowling Spearman correlation remained rock-solid at **$\rho = 0.9968–0.9980$**.
- In the Executive Summary and text, the author simultaneously claimed *'rank correlations of $\rho \ge 0.988$ for Batters'*, creating a blatant internal contradiction.

### Key Audit Breakthrough:
1. **Discovery of Code Bugs in `inv_e_ranking_robustness.py`:**
   - In Step 14's script, the recalculation of $K=30$ and $K=70$ used **completely incorrect priors and completely different normalization formulas** than the actual production model:
     - Used $\mu_{\text{SR}} = 129.8436$ instead of true Step 13 prior $\mu = 114.0475$.
     - Used decimal fraction $\mu_{\text{out}} = 0.06313$ instead of true percentage prior $\mu = 7.0859\%$, resulting in severe clipping distortion.
     - Normalized SR via $(SR - 60)/160$ instead of Step 13's $(SR - 80)/80$.
     - Normalized Survival via $(1 - out/0.15)$ instead of Step 13's $(surv - 85)/12.5$.
   - These recalculated scores were then compared against the baseline ranks from the **real** formula. The correlation drop to $\rho \approx 0.86–0.88$ was entirely an artifact of formula mismatch, not Bayesian shrinkage sensitivity!
2. **Corrected Mathematical Sensitivity Results:**
   - When the recalculation is executed using the **true Step 13 specifications**, batting rankings are in fact **extraordinarily stable**:
     - **Tier 1 Batters ($N=146$):** $K=30 \implies \rho = \mathbf{0.9984}$ (Top 10: **10/10**); $K=70 \implies \rho = \mathbf{0.9989}$ (Top 10: **10/10**).
     - **Full Batting Population ($N=816$):** $K=30 \implies \rho = \mathbf{0.9949}$; $K=70 \implies \rho = \mathbf{0.9971}$.
     - **Tier 1 Bowlers ($N=130$):** $K=30 \implies \rho = \mathbf{0.9986}$ (Top 10: **9/10**); $K=70 \implies \rho = \mathbf{0.9989}$ (Top 10: **10/10**).
     - **Full Bowling Population ($N=589$):** $K=30 \implies \rho = \mathbf{0.9972}$; $K=70 \implies \rho = \mathbf{0.9984}$.
3. **Resolution of Internal Contradiction:**
   - The internal contradiction is fully resolved: the text author's assertion that batting was stable ($\\rho \ge 0.988$) was conceptually correct for the true model, but directly contradicted the buggy script output that was inserted into Table 2.

---

## 2. Corrected Numerical Table (True Step 13 Model)

| Role | Population Evaluated | Shrinkage Parameter ($K$) | Spearman Correlation ($\rho$) | Top 10 Overlap | Top 10 Jaccard Index | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Batter** | **Tier 1 Qualifiers ($N=146$)** | $K = 30$ | **0.9984** | **10/10** | **1.000** | Corrected True Formula |
| **Batter** | **Tier 1 Qualifiers ($N=146$)** | $K = 50$ (Baseline) | **1.0000** | **10/10** | **1.000** | Baseline Production |
| **Batter** | **Tier 1 Qualifiers ($N=146$)** | $K = 70$ | **0.9989** | **10/10** | **1.000** | Corrected True Formula |
| **Batter** | **Full Population ($N=816$)** | $K = 30$ | **0.9949** | **10/10** | **1.000** | Corrected True Formula |
| **Batter** | **Full Population ($N=816$)** | $K = 70$ | **0.9971** | **10/10** | **1.000** | Corrected True Formula |
| **Bowler** | **Tier 1 Qualifiers ($N=130$)** | $K = 30$ | **0.9986** | **9/10** | **0.818** | Corrected True Formula |
| **Bowler** | **Tier 1 Qualifiers ($N=130$)** | $K = 50$ (Baseline) | **1.0000** | **10/10** | **1.000** | Baseline Production |
| **Bowler** | **Tier 1 Qualifiers ($N=130$)** | $K = 70$ | **0.9989** | **10/10** | **1.000** | Corrected True Formula |
| **Bowler** | **Full Population ($N=589$)** | $K = 30$ | **0.9972** | **10/10** | **1.000** | Corrected True Formula |
| **Bowler** | **Full Population ($N=589$)** | $K = 70$ | **0.9984** | **10/10** | **1.000** | Corrected True Formula |

---

## 3. Discrepancy Table for Shrinkage Audit

| Discrepancy ID | Item | Step 14 Claim | Verified Reality | Severity | Classification |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **DISC-12** | Bug in inv_e Script | Recalculated K sensitivity using arbitrary priors and bounds. | Used wrong priors (129.8 vs 114.0) and normalizations; caused artificial drop to $\rho = 0.8627$. | **High** | Critical Script Bug |
| **DISC-13** | Text vs. Table Contradiction | Text claimed $\rho \ge 0.988$; Table 2 showed $\rho = 0.8627$. | Direct internal contradiction in report; corrected true value is $\rho = 0.9984$. | **High** | Internal Report Contradiction |
| **DISC-14** | Population Scope | Claimed full population sensitivity across all 816 and 589 players. | Script only computed sensitivity on Tier 1 subsets ($N=146$ and $N=130$). | **Medium** | Scope Inaccuracy |

---

## 4. Final Recommendation for Investigation 4

- **Methodological Confirmation:** The actual Step 13 ranking model is **exceptionally robust to Bayesian shrinkage parameter choices** across $K \in [30, 70]$ (Spearman $\rho > 0.994$ across all 816 batters and 589 bowlers).
- **Replace Erroneous Sensitivity Table:** Update Table 2 in all project documentation with the corrected values from `audit_recalculated_k_sensitivity.csv`.