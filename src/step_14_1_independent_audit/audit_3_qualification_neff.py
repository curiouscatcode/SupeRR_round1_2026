"""
Audit Module 3: Qualification (Rule B) & Effective Sample Size Audit
Part of Step 14.1: Independent Audit of Step 14 Findings.

Audits:
  1. Delivery counts and match counts across all players.
  2. Reconciliation of the Auqib Nabi discrepancy (N=51 vs 55 deliveries).
  3. Recalculation of match concentration figures.
  4. Audit of ICC assumptions (assumed vs empirically established).
  5. Recalculation of effective sample sizes under ICC = 0.02, 0.10, 0.15 with Kish's unequal-cluster formula.
  6. Practical policy defensibility of Rule B.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_1_independent_audit")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("=" * 80)
    print("STEP 14.1 — AUDIT 3: QUALIFICATION (RULE B) & EFFECTIVE SAMPLE SIZE AUDIT")
    print("=" * 80)

    # 1. Load Data
    del_path = os.path.join(BASE_DIR, "data", "processed", "delivery_pressure_index.csv")
    bowl_path = os.path.join(BASE_DIR, "outputs", "step_13_experimental_ranking_model", "exp13_bowler_rankings.csv")
    bat_path = os.path.join(BASE_DIR, "outputs", "step_13_experimental_ranking_model", "exp13_batter_rankings.csv")

    df_del = pd.read_csv(del_path)
    df_w = pd.read_csv(bowl_path)
    df_b = pd.read_csv(bat_path)

    # 2. Reconcile Auqib Nabi Discrepancy
    print("Reconciling Auqib Nabi High-Pressure Deliveries:")
    nabi_all = df_del[(df_del['bowler_name'].str.contains('Auqib Nabi', case=False, na=False)) & (df_del['Bowling_PI'] >= 60)]
    nabi_legal = nabi_all[nabi_all['is_legal_ball'] == True]

    print(f"  Total High-Pressure Deliveries (inc extras): {len(nabi_all)}")
    print(f"  Total High-Pressure Legal Balls: {len(nabi_legal)}")
    print(f"  Official high_legal_balls in exp13_bowler_rankings: {df_w[df_w['player_name'] == 'Auqib Nabi']['high_legal_balls'].values[0]}")

    nabi_match_all = nabi_all.groupby('match_id').size()
    nabi_match_legal = nabi_legal.groupby('match_id').size()

    print("\n  Auqib Nabi Breakdown by Match:")
    for m_id in nabi_match_all.index:
        tot = nabi_match_all.loc[m_id]
        leg = nabi_match_legal.get(m_id, 0)
        ext = tot - leg
        print(f"    Match {m_id}: Total={tot}, Legal={leg}, Extras={ext}")

    max_all = nabi_match_all.max()
    max_leg = nabi_match_legal.max()
    pct_all = (max_all / len(nabi_all)) * 100.0
    pct_leg = (max_leg / len(nabi_legal)) * 100.0

    print(f"\n  Top-1 Match Share (Total Deliveries): {max_all}/{len(nabi_all)} = {pct_all:.2f}%")
    print(f"  Top-1 Match Share (Legal Deliveries): {max_leg}/{len(nabi_legal)} = {pct_leg:.2f}%")

    # 3. Yash Punja Reconciliation
    punja_all = df_del[(df_del['bowler_name'].str.contains('Punja', case=False, na=False)) & (df_del['Bowling_PI'] >= 60)]
    punja_legal = punja_all[punja_all['is_legal_ball'] == True]
    punja_match_all = punja_all.groupby('match_id').size()
    punja_match_legal = punja_legal.groupby('match_id').size()
    pct_punja_all = (punja_match_all.max() / len(punja_all)) * 100.0
    pct_punja_leg = (punja_match_legal.max() / len(punja_legal)) * 100.0

    print(f"\n  Yash Punja Top-1 Match Share (Total Deliveries): {punja_match_all.max()}/{len(punja_all)} = {pct_punja_all:.2f}%")
    print(f"  Yash Punja Top-1 Match Share (Legal Deliveries): {punja_match_legal.max()}/{len(punja_legal)} = {pct_punja_leg:.2f}%")

    # 4. Effective Sample Size & Design Effect Calculations under Varying ICC
    print("\nAuditing Effective Sample Size (N_eff) Formulations...")
    # Kish's unequal cluster formula: m_star = sum(m_i^2) / sum(m_i)
    def calc_clustered_neff(cluster_sizes, icc):
        n = sum(cluster_sizes)
        if len(cluster_sizes) == 0 or n == 0:
            return 0.0, 1.0, 0.0
        m_bar = n / len(cluster_sizes)
        m_star = sum(x**2 for x in cluster_sizes) / n
        deff_simplified = 1.0 + (m_bar - 1.0) * icc
        deff_kish = 1.0 + (m_star - 1.0) * icc
        neff_simplified = n / deff_simplified
        neff_kish = n / deff_kish
        return m_bar, m_star, deff_simplified, deff_kish, neff_simplified, neff_kish

    nabi_clusters = list(nabi_match_legal.values)
    punja_clusters = list(punja_match_legal.values)

    print("\nAuqib Nabi (Legal Balls N=51, M=5):")
    for icc in [0.02, 0.05, 0.10, 0.15]:
        m_bar, m_star, d_s, d_k, n_s, n_k = calc_clustered_neff(nabi_clusters, icc)
        print(f"  ICC={icc:.2f}: Simplified DEFF={d_s:.3f} (Neff={n_s:.1f}) | Kish DEFF={d_k:.3f} (Neff={n_k:.1f})")

    print("\nYash Punja (Legal Balls N=54, M=5):")
    for icc in [0.02, 0.05, 0.10, 0.15]:
        m_bar, m_star, d_s, d_k, n_s, n_k = calc_clustered_neff(punja_clusters, icc)
        print(f"  ICC={icc:.2f}: Simplified DEFF={d_s:.3f} (Neff={n_s:.1f}) | Kish DEFF={d_k:.3f} (Neff={n_k:.1f})")

    # Dual Qualifiers comparison at boundary (e.g. N=50, M=6)
    dual_boundary_even = [8, 8, 8, 8, 9, 9]  # fairly dispersed
    print("\nHypothetical Dual Qualifier Boundary (N=50, M=6, balanced):")
    for icc in [0.02, 0.05, 0.10, 0.15]:
        m_bar, m_star, d_s, d_k, n_s, n_k = calc_clustered_neff(dual_boundary_even, icc)
        print(f"  ICC={icc:.2f}: Simplified DEFF={d_s:.3f} (Neff={n_s:.1f}) | Kish DEFF={d_k:.3f} (Neff={n_k:.1f})")

    # 5. Build Investigation 3 Report
    report_lines = [
        "# Investigation 3: Qualification (Rule B) & Effective Sample Size Audit Report",
        "",
        "**Module:** Step 14.1 — Independent Audit of Step 14 Findings  ",
        "**Date:** November 13, 2026  ",
        "**Audit Target:** Step 14 Investigation D, Rule B Qualification & Effective Sample Size Claims  ",
        "**Status:** **AUDIT COMPLETED — DISCREPANCIES RECONCILED & STATISTICAL CLAIMS QUALIFIED**  ",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        "Investigation 3 independently audited the qualification mechanics, boundary player statistics, match-level concentration, and effective sample size ($N_{\\text{eff}}$) arguments under **Rule B Qualification**:",
        "- **Tier 1:** $N \\ge 60 \\text{ OR } (N \\ge 50 \\text{ AND } M \\ge 6)$",
        "- **Tier 2:** $N < 60$ not qualifying for Tier 1, but with $N \\ge 40$.",
        "",
        "### Key Audit Conclusions:",
        "1. **Reconciliation of the Auqib Nabi Discrepancy:**",
        "   - In Step 14, Auqib Nabi was cited as $N=51$ in the qualification summary table, but reported as having $26 / 55$ deliveries ($47.3\\%$) in Match 50376 in the match concentration section.",
        "   - **Root Cause Identified:** The official dataset tracks **legal balls** ($N=51$, excluding extras), whereas `inv_d_qualification_reliability.py` queried `delivery_pressure_index.csv` without filtering `is_legal_ball == True`, capturing 4 extras (2 wides in Match 50356, 2 wides/no-balls in Match 50376).",
        "   - **Reconciled Reality:** In Match 50376, Auqib Nabi bowled **24 legal balls out of 51 legal balls ($47.06\\%$)** and 26 total deliveries out of 55 ($47.27\\%$). The concentration finding holds true regardless of definition, but the distinction between legal deliveries and total deliveries must be documented.",
        "2. **Audit of Effective Sample Size ($N_{\\text{eff}}$) Claims:**",
        "   - Step 14 asserted that dual-constraint qualifiers possess an empirically proven higher effective sample size than near-misses.",
        "   - **Audit Finding:** Step 14 did not empirically estimate the intraclass correlation ($\\text{ICC}$) from variance-component models; it **assumed** $\\text{ICC} = 0.10$ as an illustrative scenario.",
        "   - At lower, realistic delivery-level correlation levels ($\\text{ICC} = 0.02$), the effective sample size difference shrinks significantly: Auqib Nabi has $N_{\\text{eff}} = 43.1$, compared to $N_{\\text{eff}} = 43.6$ for a dual qualifier at $N=50, M=6$.",
        "   - Therefore, describing the effective sample size argument as *'empirical mathematical proof'* was an unsupported overstatement. It is an illustrative statistical model.",
        "3. **Kish's Unequal Cluster Size Formula:**",
        "   - Step 14 used the simplified design effect formula $\\text{DEFF} = 1 + (\\bar{m} - 1) \\cdot \\text{ICC}$ with average cluster size $\\bar{m} = N/M = 10.20$.",
        "   - When cluster sizes vary wildly (e.g. Auqib Nabi's legal balls per match: $[7, 9, 10, 24, 1]$), Kish's exact design effect uses $m^* = \\sum m_i^2 / \\sum m_i = 15.82$.",
        "   - Under Kish's exact formula at $\\text{ICC} = 0.10$, Auqib Nabi's true $\\text{DEFF} = 2.482$, yielding an even lower effective sample size of **$N_{\\text{eff}} = 20.55$** (compared to $26.6$ reported in Step 14). Step 14 actually understated his concentration penalty.",
        "4. **Defensibility of Rule B as Practical Policy:**",
        "   - Independently of whether $\\text{ICC} = 0.02$ or $0.10$, **Rule B is an entirely defensible practical qualification policy**.",
        "   - Requiring $M \\ge 6$ ensures multi-opponent, multi-venue breadth and prevents a single anomalous spell from dictating a player's core reliability rating.",
        "",
        "---",
        "",
        "## 2. Reconciled Boundary Player Table",
        "",
        "| Player Name | Metric Type | High-Pressure Deliveries ($N$) | Matches ($M$) | Top Match Deliveries | Top Match Share (%) | $N_{\\text{eff}}$ ($\\text{ICC}=0.02$) | $N_{\\text{eff}}$ ($\\text{ICC}=0.10$) | Assigned Tier |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
        "| **Auqib Nabi** | Legal Balls | **51** | **5** | 24 | **47.06%** | 39.4 (Kish) | **20.6 (Kish)** | **Tier 2 (Rank 13)** |",
        "| **Auqib Nabi** | Total Balls (inc Extras) | 55 | 5 | 26 | 47.27% | 41.5 (Kish) | 21.3 (Kish) | Tier 2 (Rank 13) |",
        "| **Yash Punja** | Legal Balls | **54** | **5** | 19 | **35.19%** | 44.5 (Kish) | **26.4 (Kish)** | **Tier 2 (Rank 5)** |",
        "| **Yash Punja** | Total Balls (inc Extras) | 56 | 5 | 19 | 33.93% | 46.8 (Kish) | 28.6 (Kish) | Tier 2 (Rank 5) |",
        "| **Dual Qualifier Boundary** | Legal Balls (Hypothetical) | **50** | **6** | 9 | **18.00%** | **43.6 (Kish)** | **28.7 (Kish)** | **Tier 1 Qualified** |",
        "",
        "---",
        "",
        "## 3. Discrepancy Table for Qualification Audit",
        "",
        "| Discrepancy ID | Item | Step 14 Claim | Verified Reality | Severity | Classification |",
        "| :---: | :--- | :--- | :--- | :---: | :---: |",
        "| **DISC-09** | Nabi Delivery Denominator | 26/55 balls ($47.3\\%$) in concentration vs $N=51$ in tier tables. | $N=51$ is legal balls; 55 includes 4 extras. Legal concentration is 24/51 ($47.06\\%$). | **Low** | Factual Reconciliation |",
        "| **DISC-10** | Status of ICC Parameter | 'Rigorous ICC analysis proved mathematical superiority.' | ICC = 0.10 was an assumed parameter, not empirically estimated from random-effects models. | **Medium** | Statistical Overstatement |",
        "| **DISC-11** | Clustered Design Effect | Applied simplified $\\bar{m}$ formula instead of Kish's unequal cluster formula. | Kish formula yields $m^* = 15.82$ for Nabi, reducing $N_{\\text{eff}}$ from $26.6$ to $20.55$ at $\\text{ICC}=0.10$. | **Low** | Mathematical Precision |",
        "",
        "---",
        "",
        "## 4. Final Recommendation for Investigation 3",
        "",
        "- **Retain Rule B as Practical Qualification Policy:** The policy is pragmatic, sensible, and defensible.",
        "- **Reframe Statistical Justification:** Reframe the effective sample size argument as a illustrative statistical model under assumed clustering, rather than an *'empirical mathematical proof'*."
    ]

    report_path = os.path.join(OUTPUT_DIR, "report_3_qualification_neff_audit.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Exported Audit Report 3 to: {report_path}")
    print("Investigation 3 Audit Completed Successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
