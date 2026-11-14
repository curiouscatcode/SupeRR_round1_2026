# Pressure Index (PI) Input Dependency Audit & Controlled Mutation Report

**Audit Date:** 2026-11-13  
**Auditor:** Independent Analytics Agent (Step 16.4)  
**Dataset Population:** 188,097 clean active deliveries  
**Status:** 100% Verified — Complete Player Invariance Established  

---

## 1. Executive Summary

This audit independently inspects the mathematical formulas, source code implementation (`src/calculate_pressure_index.py` and `src/prepare_match_data.py`), and pre-delivery data dependencies of the Pressure Index (PI) engine.

### Core Verdict
- **Direct Batter Independence:** Neither Batting PI nor Bowling PI directly uses batter identity, career statistics, historical strike rate, career balls faced, batting position, player reputation, or player skill ratings.
- **Indirect Batter Independence:** All input variables represent **objective physical match states** (runs, overs, wickets, required run rate, match phase) or **within-innings situational stay** (`striker_balls_faced_before`). None of these variables proxy or leak individual batter identity.
- **Temporal Integrity & Outcome Leakage:** Every single input variable is reconstructed **strictly BEFORE the delivery is bowled**. Zero post-delivery outcomes (runs scored on delivery, wicket fallen on delivery, extras conceded) are accessible or utilized.
- **Controlled Mutation Validation:** In 6 out of 6 controlled mutation tests, randomly scrambling or mutating batter identities, names, batting positions, and career statistics yielded **exactly 0.000000 difference** in Batting PI and Bowling PI.

---

## 2. Complete Component-by-Component Formula Trace

The unified Pressure Index follows the master linear structure:
$$\text{PI} = 0.65 \times T + 0.35 \times I$$

### 2.1 Tactical Pressure ($T$)

| Formula Code | Sub-Equation for $T$ | Input Variables | Source Columns | Pre-Delivery Available? | Batter Dependent? | Outcome Leakage? |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **PI_B1_PP** | $0.40 W + 0.40 S + 0.20 O$ | `wickets_before`, `current_run_rate`, `phase_overs_completed` | `wickets_before`, `score_before`, `legal_balls_before`, `overid` | YES | **NO** | **NONE** |
| **PI_B1_MO** | $0.40 W + 0.40 S + 0.20 O$ | `wickets_before`, `current_run_rate`, `phase_overs_completed` | `wickets_before`, `score_before`, `legal_balls_before`, `overid` | YES | **NO** | **NONE** |
| **PI_B1_DO** | $0.40 W + 0.40 S + 0.20 O$ | `wickets_before`, `current_run_rate`, `phase_overs_completed` | `wickets_before`, `score_before`, `legal_balls_before`, `overid` | YES | **NO** | **NONE** |
| **PI_BO1_PP** | $0.40 W + 0.40 S + 0.20 O$ | `wickets_before`, `current_run_rate`, `phase_overs_completed` | `wickets_before`, `score_before`, `legal_balls_before`, `overid` | YES | **NO** | **NONE** |
| **PI_BO1_MO** | $0.40 W + 0.40 S + 0.20 O$ | `wickets_before`, `current_run_rate`, `phase_overs_completed` | `wickets_before`, `score_before`, `legal_balls_before`, `overid` | YES | **NO** | **NONE** |
| **PI_BO1_DO** | $0.40 W + 0.40 S + 0.20 O$ | `wickets_before`, `current_run_rate`, `phase_overs_completed` | `wickets_before`, `score_before`, `legal_balls_before`, `overid` | YES | **NO** | **NONE** |
| **PI_B2_PP** | $0.50 R + 0.30 W + 0.20 O$ | `rrr`, `wickets_before`, `phase_overs_completed` | `runs_required`, `balls_remaining`, `wickets_before`, `overid` | YES | **NO** | **NONE** |
| **PI_B2_MO** | $0.50 R + 0.30 W + 0.20 O$ | `rrr`, `wickets_before`, `phase_overs_completed` | `runs_required`, `balls_remaining`, `wickets_before`, `overid` | YES | **NO** | **NONE** |
| **PI_B2_DO** | $0.50 R + 0.30 W + 0.20 O$ | `rrr`, `wickets_before`, `phase_overs_completed` | `runs_required`, `balls_remaining`, `wickets_before`, `overid` | YES | **NO** | **NONE** |
| **PI_BO2_PP** | $0.40 S + 0.40 W + 0.20 O$ | `current_run_rate`, `wickets_before`, `phase_overs_completed` | `score_before`, `legal_balls_before`, `wickets_before`, `overid` | YES | **NO** | **NONE** |
| **PI_BO2_MO** | $0.40 S + 0.40 W + 0.20 O$ | `current_run_rate`, `wickets_before`, `phase_overs_completed` | `score_before`, `legal_balls_before`, `wickets_before`, `overid` | YES | **NO** | **NONE** |
| **PI_BO2_DO** | $0.50 S + 0.30 W + 0.20 O$ | `rrr`, `wickets_before`, `phase_overs_completed` | `runs_required`, `balls_remaining`, `wickets_before`, `overid` | YES | **NO** | **NONE** |

### Detailed Definitions of Tactical Sub-Components:
1. **Wickets Factor ($W$):**
   - Batting: $W = \min(100, (\text{wickets\_before} / 6) \times 100)$ — captures team collapse and loss of batting resources.
   - Bowling: $W = \max(0, ((6 - \text{wickets\_before}) / 6) \times 100)$ — captures bowling jeopardy when the opposition has wickets in hand.
2. **Run Rate Factor ($S$ and $R$):**
   - Innings 1 Batting ($S$): $S = \max(0, \min(100, ((8 - \text{CRR}) / 8) \times 100))$ (or $10$ in Death) — pressure increases when scoring rate lags.
   - Innings 2 Batting ($R$): $R = \max(0, \min(100, ((\text{RRR} - \text{Base}) / \text{Scale}) \times 100))$ — pressure scales directly with Required Run Rate.
   - Bowling Innings 1 ($S$): Pressure increases when CRR accelerates above par.
   - Bowling Innings 2 ($S$): Pressure increases when RRR is low (chasing team in control) or CRR is rapid.
3. **Phase Progression Factor ($O$):**
   - $O = (\text{phase\_overs\_completed} / \text{phase\_length}) \times 100$ — captures tension mounting toward the conclusion of each phase.

---

### 2.2 Situational Intensity ($I$)

| Component | Exact Formula | Input Variables | Source Columns | Pre-Delivery Available? | Batter Dependent? | Outcome Leakage? |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **$I_{\text{batter}}$ (Settling)** | $\max(0, \min(100, ((10 - B_{\text{bf}}) / 10) \times 100))$ | `striker_balls_faced_before` | In-innings counter incremented on balls faced | YES | **NO** | **NONE** |
| **$I_{\text{bowler}}$ (Workload + Settling)** | $0.50 B_{\text{workload}} + 0.50 S_{\text{settling}}$ | `bowler_legal_balls_in_spell_before`, `striker_balls_faced_before` | In-innings spell counter + striker balls faced | YES | **NO** | **NONE** |

#### Critical Examination of `striker_balls_faced_before`:
- Does `striker_balls_faced_before` depend on who the batter is? **NO.**
- It is an anonymous counter initialized to $0$ when a batter enters the crease and incremented by $1$ after each legal or illegal ball faced by the striker in that specific innings.
- It models the well-established cricket concept of "getting set" (vulnerability and psychological pressure during the first 10 balls).
- Whether the striker is an opening specialist with a career strike rate of 150 or a number 11 tailender, the formula executes identically: $B_{\text{bf}} = 0 \implies I = 100.0$; $B_{\text{bf}} \ge 10 \implies I = 0.0$.
- It is completely blind to player identity, career records, and batting position.

---

## 3. Controlled Mutation Test Results

A rigorous controlled mutation test was conducted across all 188,097 clean deliveries. Batter identities, names, batting positions, and career statistics were altered while preserving pre-delivery match context.

| Test ID | Mutation Applied | Target Field Mutated | Max Abs Diff (Batting PI) | Max Abs Diff (Bowling PI) | Result |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **MUT-01** | Random permutation of `striker_id` across all deliveries | `striker_id` | **0.000000** | **0.000000** | **PASSED** |
| **MUT-02** | Inversion of `batting_order` ($12 - \text{order}$) | `batting_order` | **0.000000** | **0.000000** | **PASSED** |
| **MUT-03** | Constant `batting_order` = 11 across all deliveries | `batting_order` | **0.000000** | **0.000000** | **PASSED** |
| **MUT-04** | Uniform constant `striker_name` ("Mutated_Player_X") | `striker_name` | **0.000000** | **0.000000** | **PASSED** |
| **MUT-05** | Injection of synthetic career strike rate metadata | `career_sr` | **0.000000** | **0.000000** | **PASSED** |
| **MUT-06** | Random permutation of `bowler_id` across all deliveries | `bowler_id` | **0.000000** | **0.000000** | **PASSED** |

```
Mutation Test Data Artifact:
outputs/step_16_4_pi_validation_audit/controlled_mutation_test_results.csv
```

---

## 4. Conclusion on Investigation A

The Pressure Index is mathematically and structurally **player-blind**. 
The disparity in high-pressure delivery capture between top-order batters ($7.06\%$) and lower-order batters ($52.36\%$) cannot be caused by any batter-specific input, career metric, batting position tag, or identity variable in the PI engine. 

The cause must therefore reside entirely in the **situational distribution of match states** encountered by different batting positions. This is investigated directly in Investigation B.
