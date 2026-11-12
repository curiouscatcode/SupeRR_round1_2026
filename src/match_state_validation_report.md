# SupeRR Selector 2.0 — Match State Reconstruction Validation Report
**Phase:** Step 3 Match State Reconstruction  
**Date:** November 2026  
**Processed Dataset:** `data/processed/delivery_match_state.csv`  
**Pipeline Script:** `src/prepare_match_data.py`  
---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Match Selection & Cohort Verification](#2-match-selection--cohort-verification)
3. [Reconstructed State Schema & Column Definitions](#3-reconstructed-state-schema--column-definitions)
4. [Detailed Validation on Benchmark Matches](#4-detailed-validation-on-benchmark-matches)
   - [4.1 Match 13511: First Innings Powerplay & Death Overs](#41-match-13511-first-innings-powerplay--death-overs)
   - [4.2 Match 13511: Second Innings Chase Dynamics & Target Tracking](#42-match-13511-second-innings-chase-dynamics--target-tracking)
   - [4.3 Match 14098: Multi-Bowler Over & Spell Continuity](#43-match-14098-multi-bowler-over--spell-continuity)
   - [4.4 Match 31254: Overstep No-Ball with 4 Byes (`extras_2_runs`)](#44-match-31254-overstep-no-ball-with-4-byes-extras_2_runs)
5. [Spell Tracking Architecture](#5-spell-tracking-architecture)
6. [Data Hygiene & Flagged Anomalies](#6-data-hygiene--flagged-anomalies)
7. [Pipeline Guarantees & Non-Leakage Proof](#7-pipeline-guarantees--non-leakage-proof)
---

## 1. Executive Summary
The Match State Reconstruction pipeline successfully processes **188,330 deliveries** across all **789 full 20-over completed matches** (1,578 regular innings) from the 2022–2026 IPL and T20I seasons. For every single delivery, the pipeline accurately computes the exact match situation immediately **BEFORE** the ball is bowled, preventing any future or current delivery outcome from leaking into the pre-delivery feature space.

**Core Deliverables Completed:**
- `src/prepare_match_data.py`: Standalone, end-to-end Python pipeline script.
- `data/processed/delivery_match_state.csv`: Reconstructed dataset preserving all 33 original delivery attributes and adding 16 reconstructed match context columns.
- `src/match_state_validation_report.md`: Formal verification report.

## 2. Match Selection & Cohort Verification
The match cohort strictly implements the filtering criteria established in Phase 2:

| Metric | Count | Validation Status |
| :--- | :---: | :--- |
| **Core Completed Matches** | **789** | Exactly matches Phase 2 validation count (789). |
| — IPL Matches (2022–2026) | **357** | 357 completed 20-over IPL matches. |
| — T20I Matches (2022–2026) | **432** | 432 completed 20-over T20I matches. |
| **Total Regular Innings** | **1,578** | Exactly 789 Innings 1 and 789 Innings 2. |
| **Excluded Matches** | **94** | 30 Other T20, 24 DLS Shortened, 24 No Result, 16 Abandoned. |
| **Excluded Super Overs** | **12 innings** | Innings 3 & 4 (6 matches) kept separate from regular innings. |

## 3. Reconstructed State Schema & Column Definitions

| Column Name | Type | Description | Sample Value |
| :--- | :---: | :--- | :---: |
| `score_before` | `int32` | Total team runs scored before this delivery | `0`, `45`, `162` |
| `wickets_before` | `int32` | Total wickets lost by batting team before this delivery | `0`, `2`, `7` |
| `legal_balls_before` | `int32` | Total legal deliveries bowled in the innings so far | `0`, `36`, `114` |
| `balls_remaining` | `int32` | Total legal deliveries remaining in the 20-over innings ($120 - \text{legal balls}$) | `120`, `84`, `6` |
| `current_run_rate` | `float64` | Current Run Rate ($(\text{score} / \text{legal balls}) \times 6.0$; 0.0 at ball 0) | `7.50`, `9.20` |
| `runs_required` | `float64` | Runs required to win (Innings 2 only; `NaN` in Innings 1) | `104.0`, `15.0` |
| `required_run_rate` | `float64` | Required Run Rate ($(\text{req} / \text{balls rem}) \times 6.0$; Innings 2 only) | `8.45`, `12.50` |
| `striker_balls_faced_before` | `int32` | Balls faced by current striker in this innings before this delivery | `0`, `14`, `42` |
| `bowler_legal_balls_in_spell_before`| `int32` | Legal balls bowled by current bowler in active spell before this ball | `0`, `5`, `18` |
| `phase` | `string` | Match phase: `'PP'` (overs 1-6), `'Middle'` (7-15), `'Death'` (16-20) | `'PP'`, `'Death'` |
| `phase_overs_completed` | `int32` | Number of completed overs within the current phase | `0` to `8` |
| `is_legal_ball` | `bool` | True if delivery is legal; False if wide, overstep, or other | `True`, `False` |
| `is_batter_ball_faced` | `bool` | True if delivery counts as batter ball faced (all except wide) | `True`, `False` |
| `bowler_runs_conceded` | `int32` | Runs debited to bowler on this ball (`runs` + 1 if wide/no-ball) | `0`, `1`, `4`, `6` |
| `team_runs_added` | `int32` | Runs added to team total on this ball | `0`, `1`, `4`, `5` |
| `is_anomalous_extra` | `bool` | Flag for the single anomalous leg-bye row where `runs > 0` | `False` (1 `True`) |

## 4. Detailed Validation on Benchmark Matches

### 4.1 Match 13511: First Innings Powerplay & Death Overs
England innings vs West Indies (January 22, 2022). England scored 103 all out in 19.4 overs.

|   overid |   over_ball_num | striker_name   | bowler_name      |   score_before |   wickets_before |   legal_balls_before |   current_run_rate |   striker_balls_faced_before | phase   |   phase_overs_completed |   team_runs_added |
|---------:|----------------:|:---------------|:-----------------|---------------:|-----------------:|---------------------:|-------------------:|-----------------------------:|:--------|------------------------:|------------------:|
|        1 |               1 | Jason Roy      | Sheldon Cottrell |              0 |                0 |                    0 |               0    |                            0 | PP      |                       0 |                 0 |
|        1 |               2 | Jason Roy      | Sheldon Cottrell |              0 |                0 |                    1 |               0    |                            1 | PP      |                       0 |                 0 |
|        1 |               3 | Jason Roy      | Sheldon Cottrell |              0 |                0 |                    2 |               0    |                            2 | PP      |                       0 |                 0 |
|        1 |               4 | Jason Roy      | Sheldon Cottrell |              0 |                0 |                    3 |               0    |                            3 | PP      |                       0 |                 0 |
|        1 |               5 | Jason Roy      | Sheldon Cottrell |              0 |                0 |                    4 |               0    |                            4 | PP      |                       0 |                 6 |
|        1 |               6 | Jason Roy      | Sheldon Cottrell |              6 |                0 |                    5 |               7.2  |                            5 | PP      |                       0 |                 0 |
|        2 |               1 | Tom Banton     | Jason Holder     |              6 |                1 |                    6 |               6    |                            0 | PP      |                       1 |                 0 |
|        2 |               2 | Tom Banton     | Jason Holder     |              6 |                1 |                    7 |               5.14 |                            1 | PP      |                       1 |                 0 |

- **Verification:** At Over 1 Ball 1, `score_before = 0`, `wickets_before = 0`, `legal_balls_before = 0`, `crr = 0.0`. Jason Roy hits a 6 on Ball 5; on Ball 6, `score_before` is 6 and `crr` updates to 7.20. Roy is out on Ball 6; at Over 2 Ball 1, `wickets_before` correctly reflects 1.

### 4.2 Match 13511: Second Innings Chase Dynamics & Target Tracking
West Indies target: **104 runs**. West Indies won by 9 wickets in 17.1 overs.

|   overid |   over_ball_num | striker_name   |   score_before |   runs_required |   balls_remaining |   required_run_rate |   current_run_rate |   team_runs_added |
|---------:|----------------:|:---------------|---------------:|----------------:|------------------:|--------------------:|-------------------:|------------------:|
|        1 |               1 | Brandon King   |              0 |             104 |               120 |                5.2  |                  0 |                 0 |
|        1 |               2 | Brandon King   |              0 |             104 |               119 |                5.24 |                  0 |                 4 |
|        1 |               3 | Brandon King   |              4 |             100 |               118 |                5.08 |                 12 |                 0 |
|        1 |               4 | Brandon King   |              4 |             100 |               117 |                5.13 |                  8 |                 0 |
|        1 |               5 | Brandon King   |              4 |             100 |               116 |                5.17 |                  6 |                 1 |
|        1 |               6 | Shai Hope      |              5 |              99 |               115 |                5.17 |                  6 |                 1 |

- **Verification:** Target correctly initialized to 104 ($103 + 1$). At Ball 1: `runs_required = 104`, `balls_remaining = 120`, `rrr = 5.20`. After King hits a four on Ball 2, Ball 3 correctly shows `runs_required = 100`, `balls_remaining = 118`, `rrr = 5.08`.

### 4.3 Match 14098: Multi-Bowler Over & Spell Continuity
In Match 14098 (SRH vs RR, Over 20), Nathan Coulter-Nile bowled a no-ball and got injured; Riyan Parag bowled the remaining 6 deliveries.

|   over_ball_num | striker_name      | bowler_name         |   bowler_legal_balls_in_spell_before | is_legal_ball   |   team_runs_added |
|----------------:|:------------------|:--------------------|-------------------------------------:|:----------------|------------------:|
|               1 | Bhuvneshwar Kumar | Nathan Coulter Nile |                                    0 | False           |                 1 |
|               2 | Bhuvneshwar Kumar | Riyan Parag         |                                    0 | True            |                 1 |
|               3 | Aiden Markram     | Riyan Parag         |                                    1 | True            |                 1 |
|               4 | Bhuvneshwar Kumar | Riyan Parag         |                                    2 | True            |                 1 |
|               5 | Aiden Markram     | Riyan Parag         |                                    3 | True            |                 4 |
|               6 | Aiden Markram     | Riyan Parag         |                                    4 | True            |                 6 |
|               7 | Aiden Markram     | Riyan Parag         |                                    5 | True            |                 1 |

- **Verification:** Coulter-Nile had 0 legal balls in spell before. On Ball 2, Parag begins his spell with 0 legal balls in spell before, incrementing cleanly to 5 on Ball 7.

### 4.4 Match 31254: Overstep No-Ball with 4 Byes (`extras_2_runs`)
In Match 31254 (KKR vs RCB, Over 17 Ball 3), Yash Dayal overstepped and conceded 4 boundary byes.

| striker_name   | bowler_name   |   runs | extras_type   |   extras_2_runs |   bowler_runs_conceded |   team_runs_added | is_legal_ball   | is_batter_ball_faced   |
|:---------------|:--------------|-------:|:--------------|----------------:|-----------------------:|------------------:|:----------------|:-----------------------|
| Andre Russell  | Yash Dayal    |      0 | Overstep      |               4 |                      1 |                 5 | False           | True                   |

- **Verification:** `runs = 0` (Russell credited with 0), `extras_2_runs = 4` (not added to batter or bowler), `bowler_runs_conceded = 1` (no-ball penalty only), `team_runs_added = 5` (1 no-ball + 4 byes), `is_legal_ball = False` (does not increment legal balls), `is_batter_ball_faced = True` (Russell faced the no-ball).

## 5. Spell Tracking Architecture
In 20-over cricket, alternate overs from the same end constitute a continuous spell (e.g. Overs 1, 3, 5). Our algorithm tracks the last over bowled by each bowler:

- **Same Spell Condition:** If $\text{overid} \le \text{last\_over} + 2$, the bowler is continuing consecutive available overs from that end. The spell counter continues accumulating.
- **New Spell Condition:** If $\text{overid} > \text{last\_over} + 2$, another bowler was introduced from that end, meaning the bowler was taken off. When the bowler returns, `bowler_legal_balls_in_spell_before` resets to **0**.

## 6. Data Hygiene & Flagged Anomalies
- **Anomalous Leg-bye Row Flagged:** Exactly 1 row in the entire dataset (Row 113,765, Match 37099, Innings 2, Over 14, Ball 6) has `extras_type == 'legbyes'` and `runs == 1`. The pipeline marks `is_anomalous_extra = True`, records `team_runs_added = 1` under the proxy rule, and credits 0 to batter and bowler.
- **Zero Negative or Impossible Values:** `score_before >= 0`, `0 <= wickets_before <= 10`, `0 <= legal_balls_before <= 121`, `balls_remaining >= 0`.

## 7. Pipeline Guarantees & Non-Leakage Proof
Every single reconstructed feature satisfies the strict temporal boundary condition:

$$\text{Feature}_{t} = f(\text{Delivery}_{1}, \text{Delivery}_{2}, \dots, \text{Delivery}_{t-1})$$

No attribute of $\text{Delivery}_{t}$ (runs scored, extra conceded, or wicket taken) is present in $\text{Feature}_{t}$. This guarantees that when machine learning models or situational Pressure Indices are evaluated at delivery $t$, they only possess the exact information available to the batter, bowler, and captain on the field at that precise moment.

---
*Match state reconstruction pipeline certified for SupeRR Selector Season 2.*  
