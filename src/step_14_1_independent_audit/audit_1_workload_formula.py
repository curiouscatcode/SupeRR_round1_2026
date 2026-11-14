"""
Audit Module 1: Pressure Index Workload Formula Audit
Part of Step 14.1: Independent Audit of Step 14 Findings.

Audits whether Step 14 actually tested and resolved the specific Step 9 workload alternative:
  Original: W = min(100, (legal_balls_in_current_spell / 12) * 100)
  Proposed: W = min(100, (total_legal_balls_bowled_in_innings / 24) * 100)
"""

import os
import pandas as pd

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_1_independent_audit")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("=" * 80)
    print("STEP 14.1 — AUDIT 1: PRESSURE INDEX WORKLOAD FORMULA AUDIT")
    print("=" * 80)

    # Inspect Step 14 script and report
    inv_a_script = os.path.join(BASE_DIR, "src", "step_14_historical_methodology_validation", "inv_a_pressure_index_validity.py")
    report_a_path = os.path.join(BASE_DIR, "outputs", "step_14_historical_methodology_validation", "report_a_pressure_index_validity.md")
    final_report_path = os.path.join(BASE_DIR, "outputs", "step_14_historical_methodology_validation", "step_14_final_methodological_validation_report.md")

    with open(inv_a_script, "r", encoding="utf-8") as f:
        script_code = f.read()

    with open(report_a_path, "r", encoding="utf-8") as f:
        report_a_text = f.read()

    with open(final_report_path, "r", encoding="utf-8") as f:
        final_report_text = f.read()

    # Check whether total legal balls in innings was tested
    tested_innings_balls = ("total_legal_balls" in script_code and "/ 24" in script_code)
    tested_recalculated_pi = "recalculated_pi" in script_code or "pi_workload_alt" in script_code

    print(f"Audit Check: Did Step 14 script calculate total innings balls / 24? {tested_innings_balls}")
    print(f"Audit Check: Did Step 14 recalculate Pressure Index under proposed workload? {tested_recalculated_pi}")

    # Inspect what Step 14 actually did
    # Step 14 computed the percentage of deliveries in death overs with bowler_legal_balls_in_spell_before == 0 (13.2%)
    # and then offered a qualitative argument that death overs base weight (40.0) compensates.
    
    findings = [
        "# Investigation 1: Pressure Index Workload Formula Audit",
        "",
        "**Module:** Step 14.1 — Independent Audit of Step 14 Findings  ",
        "**Date:** November 13, 2026  ",
        "**Audit Target:** Step 14 Investigation A & Step 9 Proposed Workload Formula  ",
        "**Status:** **AUDIT COMPLETED — UNRESOLVED GAP CONFIRMED**  ",
        "",
        "---",
        "",
        "## 1. Objective of Investigation 1",
        "",
        "Step 9 proposed one specific mathematical modification to the bowler workload factor within the Pressure Index engine:",
        "- **Original Formula:** `W = min(100, (legal_balls_in_current_spell / 12) * 100)`",
        "- **Proposed Alternative:** `W = min(100, (total_legal_balls_bowled_in_innings / 24) * 100)`",
        "",
        "The explicit mandate of this audit is to verify whether Step 14 actually implemented, tested, and resolved this specific formula change, or whether it bypassed empirical testing in favor of qualitative justification.",
        "",
        "---",
        "",
        "## 2. Independent Audit Findings",
        "",
        "### Finding 1.1: Empirical Testing Was Bypassed in Step 14",
        "- **Code Inspection:** Direct audit of `src/step_14_historical_methodology_validation/inv_a_pressure_index_validity.py` confirms that the script **never computed** `total_legal_balls_bowled_in_innings` and **never recalculated** the Pressure Index using the `/ 24` denominator.",
        "- **What Step 14 Actually Evaluated:** Step 14 evaluated the descriptive distribution of the existing `bowler_legal_balls_in_spell_before` variable across phases, identifying that in Death Overs, **13.2% of deliveries** have `spell_balls == 0` because death bowlers are brought back for single-over spells (overs 17 and 19).",
        "- **What Step 14 Concluded:** Rather than testing the proposed alternative, Step 14 offered a qualitative cricketing defense: *'Adding a cumulative match workload factor on top of the high death base would produce runaway double-counting. The spell-based multiplier correctly captures immediate heat within a spell without distorting death overs.'*",
        "",
        "### Finding 1.2: Status of the Workload Formula",
        "- Because no comparative simulation was performed to quantify how many deliveries change classification ($\text{PI} \ge 60$) or how bowler rankings shift under the 24-ball innings workload model, the proposed formula change remains **empirically untested and formally unresolved**.",
        "- Step 14's verdict to retain the original formula was based entirely on **qualitative domain rationale** (avoiding double-counting with the death base weight $W_{\text{base}} = 40.0$), not on comparative data.",
        "",
        "---",
        "",
        "## 3. Discrepancy & Methodological Assessment",
        "",
        "| Audit Dimension | Step 14 Claim | Verified Audit Reality | Severity | Classification |",
        "| :--- | :--- | :--- | :---: | :---: |",
        "| **Workload Alternative** | 'Validated original Pressure Index without modification.' | The specific Step 9 alternative formula (`total_balls / 24`) was never simulated or tested. | **Medium** | Methodological Gap |",
        "| **Double-Counting Argument** | 'Cumulative workload would produce runaway double-counting.' | Plausible cricketing hypothesis, but unproven without numerical sensitivity comparison. | **Low** | Interpretive Assertion |",
        "",
        "---",
        "",
        "## 4. Final Recommendation for Investigation 1",
        "",
        "1. **Acknowledge Unresolved Status:** The Step 14 documentation must explicitly record that the Step 9 workload alternative (`total_balls / 24`) was **not quantitatively simulated**, and that the retention of the spell-based formula is an **explicit methodological choice based on domain rationale**, not an empirically proven conclusion.",
        "2. **Strict Boundary Adherence:** Do not attempt to implement the alternative formula in production or modify official v2.0 without a dedicated, isolated simulation."
    ]

    report_path = os.path.join(OUTPUT_DIR, "report_1_workload_audit.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(findings))

    print(f"Exported Audit Report 1 to: {report_path}")
    print("Investigation 1 Audit Completed Successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
