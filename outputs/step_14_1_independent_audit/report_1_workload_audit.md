# Investigation 1: Pressure Index Workload Formula Audit

**Module:** Step 14.1 — Independent Audit of Step 14 Findings  
**Date:** November 13, 2026  
**Audit Target:** Step 14 Investigation A & Step 9 Proposed Workload Formula  
**Status:** **AUDIT COMPLETED — UNRESOLVED GAP CONFIRMED**  

---

## 1. Objective of Investigation 1

Step 9 proposed one specific mathematical modification to the bowler workload factor within the Pressure Index engine:
- **Original Formula:** `W = min(100, (legal_balls_in_current_spell / 12) * 100)`
- **Proposed Alternative:** `W = min(100, (total_legal_balls_bowled_in_innings / 24) * 100)`

The explicit mandate of this audit is to verify whether Step 14 actually implemented, tested, and resolved this specific formula change, or whether it bypassed empirical testing in favor of qualitative justification.

---

## 2. Independent Audit Findings

### Finding 1.1: Empirical Testing Was Bypassed in Step 14
- **Code Inspection:** Direct audit of `src/step_14_historical_methodology_validation/inv_a_pressure_index_validity.py` confirms that the script **never computed** `total_legal_balls_bowled_in_innings` and **never recalculated** the Pressure Index using the `/ 24` denominator.
- **What Step 14 Actually Evaluated:** Step 14 evaluated the descriptive distribution of the existing `bowler_legal_balls_in_spell_before` variable across phases, identifying that in Death Overs, **13.2% of deliveries** have `spell_balls == 0` because death bowlers are brought back for single-over spells (overs 17 and 19).
- **What Step 14 Concluded:** Rather than testing the proposed alternative, Step 14 offered a qualitative cricketing defense: *'Adding a cumulative match workload factor on top of the high death base would produce runaway double-counting. The spell-based multiplier correctly captures immediate heat within a spell without distorting death overs.'*

### Finding 1.2: Status of the Workload Formula
- Because no comparative simulation was performed to quantify how many deliveries change classification ($	ext{PI} \ge 60$) or how bowler rankings shift under the 24-ball innings workload model, the proposed formula change remains **empirically untested and formally unresolved**.
- Step 14's verdict to retain the original formula was based entirely on **qualitative domain rationale** (avoiding double-counting with the death base weight $W_{	ext{base}} = 40.0$), not on comparative data.

---

## 3. Discrepancy & Methodological Assessment

| Audit Dimension | Step 14 Claim | Verified Audit Reality | Severity | Classification |
| :--- | :--- | :--- | :---: | :---: |
| **Workload Alternative** | 'Validated original Pressure Index without modification.' | The specific Step 9 alternative formula (`total_balls / 24`) was never simulated or tested. | **Medium** | Methodological Gap |
| **Double-Counting Argument** | 'Cumulative workload would produce runaway double-counting.' | Plausible cricketing hypothesis, but unproven without numerical sensitivity comparison. | **Low** | Interpretive Assertion |

---

## 4. Final Recommendation for Investigation 1

1. **Acknowledge Unresolved Status:** The Step 14 documentation must explicitly record that the Step 9 workload alternative (`total_balls / 24`) was **not quantitatively simulated**, and that the retention of the spell-based formula is an **explicit methodological choice based on domain rationale**, not an empirically proven conclusion.
2. **Strict Boundary Adherence:** Do not attempt to implement the alternative formula in production or modify official v2.0 without a dedicated, isolated simulation.