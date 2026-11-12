# Pressure Index (PI) Validation Report
**Project:** SupeRR Selector Season 2 — Cricket Analytics Competition  
**Pipeline Step:** Step 4 — Implement the Pressure Index Engine  
**Execution Timestamp:** 2026-11-12  
**Input Dataset:** `data/processed/delivery_match_state.csv` (188,330 rows, 49 columns)  
**Output Dataset:** `data/processed/delivery_pressure_index.csv` (188,330 rows, 65 columns)  
**Engine Script:** `src/calculate_pressure_index.py`  

---

## 1. Executive Summary & Audit Verdict

This document presents the technical audit and validation of the Pressure Index (PI) engine developed for the SupeRR Selector 2.0 competition. The engine evaluates the match-context pressure faced by both the striker (`Batting_PI`) and the bowler (`Bowling_PI`) immediately **before** every delivery across 789 standard 20-over matches (357 IPL, 432 T20I) from 2022 to 2026.

### Key Audit Findings
1. **Formula Fidelity:** All 12 specific phase- and innings-dependent formulas were implemented strictly as specified in the competition problem definition. No formulas were simplified, replaced, or modified.
2. **Mutual Exclusivity:** For every delivery, exactly **one** batting formula column and exactly **one** bowling formula column are populated. The remaining 10 formula columns remain strictly `NaN` / null.
3. **Range Adherence:** Every component ($W, S, O, R, B, B_{\text{workload}}, S_{\text{settling}}$), intermediate score ($T, I$), and final pressure index ($PI$) is strictly bounded within $[0.00, 100.00]$.
4. **Data Integrity & Zero Lookahead:** The output dataset retains all 188,330 rows from `delivery_match_state.csv`. All state variables were reconstructed strictly using pre-delivery information, resulting in near-zero correlations with current ball outcomes (e.g., $r = -0.0015$ with bowler runs conceded, $r = 0.0267$ with wickets).
5. **First-Ball Determinism:** On the first ball of Innings 1, all 789 matches evaluate to the exact theoretical values: `Batting_PI = 61.00` ($\sigma = 0.0$) and `Bowling_PI = 43.50` ($\sigma = 0.0$). On the first ball of Innings 2, bowling pressure is identically constant (`Bowling_PI = 43.50`, $\sigma = 0.0$), while batting pressure varies strictly as a function of target difficulty (ranging from $35.00$ to $67.50$).

---

## 2. Core Architecture & Common Rules

### 2.1 The Master Equation
For every delivery, role, innings, and phase:
$$\text{PI} = (0.65 \times T) + (0.35 \times I)$$

Where:
- $T \in [0, 100]$: Team Contextual Pressure (match situation, phase time, wickets, scoring rate).
- $I \in [0, 100]$: Individual Player Pressure (balls faced / settling-in, workload).

### 2.2 Match Phases
Phases are partitioned by scheduled over numbers, using the pre-existing `phase` and `phase_overs_completed` columns:
- **Powerplay (PP):** Overs 1–6 (6 overs total). `phase_overs_completed` ranges from 0 to 5.
- **Middle Overs (MO):** Overs 7–15 (9 overs total). `phase_overs_completed` ranges from 0 to 8.
- **Death Overs (DO):** Overs 16–20 (5 overs total). `phase_overs_completed` ranges from 0 to 4.

### 2.3 Individual Pressure Formulations

#### Batter Individual Pressure ($I_{\text{batter}}$)
Batters experience peak individual pressure on their first delivery ($100.0$) and settle in over their first 10 balls faced (excluding wides, including no-balls):
$$B = \max\left(0, \min\left(100, \frac{10 - \text{striker\_balls\_faced\_before}}{10} \times 100\right)\right)$$
$$I_{\text{batter}} = B$$

#### Bowler Individual Pressure ($I_{\text{bowler}}$)
Bowler pressure reflects cumulative fatigue/exposure in the current spell balanced against striker settling:
$$B_{\text{workload}} = \min\left(100, \frac{\text{bowler\_legal\_balls\_in\_spell\_before}}{12} \times 100\right)$$
$$S_{\text{settling}} = B = \max\left(0, \min\left(100, \frac{10 - \text{striker\_balls\_faced\_before}}{10} \times 100\right)\right)$$
$$I_{\text{bowler}} = (0.50 \times B_{\text{workload}}) + (0.50 \times S_{\text{settling}})$$

### 2.4 Qualitative Pressure Tiers
Continuous PI values are mapped to 5 standardized qualitative tiers:

| PI Range | Pressure Tier | Interpretation |
|:---:|:---:|:---|
| $[0.00, 20.00]$ | **Very Low** | Low stakes, dominant position, or minimal immediate risk |
| $(20.00, 40.00]$ | **Low** | Manageable tempo, controlled state |
| $(40.00, 60.00]$ | **Moderate** | Par contest, evenly balanced match leverage |
| $(60.00, 80.00]$ | **High** | Escalated jeopardy, tight asking rate, or critical wickets lost |
| $(80.00, 100.00]$ | **Very High** | Extreme crisis, steep required run rate, or imminent collapse |

---

## 3. The 12 Specific Formula Specifications

### 3.1 First-Innings Batters (`innings == 1`)
Wicket pressure measures wickets lost by the batting team ($W = \min(100, (W_{\text{before}} / 6) \times 100)$). Scoring pressure measures deficit below target benchmark run rates.

1. **`PI_B1_PP` (Powerplay):**
   - $W = \min(100, (W_{\text{before}} / 6) \times 100)$
   - $S = \max(0, \min(100, ((8 - CRR) / 8) \times 100))$
   - $O = (O_{\text{comp}} / 6) \times 100$
   - $T = (0.40 \times W) + (0.40 \times S) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times B)$

2. **`PI_B1_MO` (Middle Overs):**
   - $W = \min(100, (W_{\text{before}} / 6) \times 100)$
   - $S = \max(0, \min(100, ((8 - CRR) / 8) \times 100))$
   - $O = (O_{\text{comp}} / 9) \times 100$
   - $T = (0.40 \times W) + (0.40 \times S) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times B)$

3. **`PI_B1_DO` (Death Overs):**
   - $W = \min(100, (W_{\text{before}} / 6) \times 100)$
   - $S = \max(0, \min(100, ((10 - CRR) / 10) \times 100))$
   - $O = (O_{\text{comp}} / 5) \times 100$
   - $T = (0.40 \times W) + (0.40 \times S) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times B)$

### 3.2 First-Innings Bowlers (`innings == 1`)
Bowling wicket pressure is inverted: bowling teams face higher pressure when they have taken fewer wickets ($W = \max(0, ((6 - W_{\text{before}}) / 6) \times 100)$). Scoring pressure measures batting team scoring above defensive thresholds.

4. **`PI_BO1_PP` (Powerplay):**
   - $W = \max(0, ((6 - W_{\text{before}}) / 6) \times 100)$
   - $S = \max(0, \min(100, ((CRR - 8) / (12 - 8)) \times 100))$
   - $O = (O_{\text{comp}} / 6) \times 100$
   - $T = (0.40 \times W) + (0.40 \times S) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times I_{\text{bowler}})$

5. **`PI_BO1_MO` (Middle Overs):**
   - $W = \max(0, ((6 - W_{\text{before}}) / 6) \times 100)$
   - $S = \max(0, \min(100, ((CRR - 7) / (11 - 7)) \times 100))$
   - $O = (O_{\text{comp}} / 9) \times 100$
   - $T = (0.40 \times W) + (0.40 \times S) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times I_{\text{bowler}})$

6. **`PI_BO1_DO` (Death Overs):**
   - $W = \max(0, ((6 - W_{\text{before}}) / 6) \times 100)$
   - $S = \max(0, \min(100, ((CRR - 9) / (15 - 9)) \times 100))$
   - $O = (O_{\text{comp}} / 5) \times 100$
   - $T = (0.40 \times W) + (0.40 \times S) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times I_{\text{bowler}})$

### 3.3 Second-Innings Batters (`innings == 2`)
Batting chase pressure is anchored to Required Run Rate ($RRR = (\text{runs\_required} / \text{balls\_remaining}) \times 6$).

7. **`PI_B2_PP` (Powerplay):**
   - $R = \max(0, \min(100, ((RRR - 6) / (12 - 6)) \times 100))$
   - $W = \min(100, (W_{\text{before}} / 6) \times 100)$
   - $O = (O_{\text{comp}} / 6) \times 100$
   - $T = (0.50 \times R) + (0.30 \times W) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times B)$

8. **`PI_B2_MO` (Middle Overs):**
   - $R = \max(0, \min(100, ((RRR - 7) / (13 - 7)) \times 100))$
   - $W = \min(100, (W_{\text{before}} / 6) \times 100)$
   - $O = (O_{\text{comp}} / 9) \times 100$
   - $T = (0.50 \times R) + (0.30 \times W) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times B)$

9. **`PI_B2_DO` (Death Overs):**
   - $R = \max(0, \min(100, ((RRR - 9) / (18 - 9)) \times 100))$
   - $W = \min(100, (W_{\text{before}} / 6) \times 100)$
   - $O = (O_{\text{comp}} / 5) \times 100$
   - $T = (0.50 \times R) + (0.30 \times W) + (0.20 \times O)$
   - $\text{PI} = (0.65 \times T) + (0.35 \times B)$

### 3.4 Second-Innings Bowlers (`innings == 2`)
In Powerplay and Middle overs, bowler pressure depends on the current scoring rate; in Death overs, bowler scoring pressure depends directly on RRR.

10. **`PI_BO2_PP` (Powerplay):**
    - $S = \max(0, \min(100, ((CRR - 6) / (12 - 6)) \times 100))$
    - $W = \max(0, ((6 - W_{\text{before}}) / 6) \times 100)$
    - $O = (O_{\text{comp}} / 6) \times 100$
    - $T = (0.40 \times S) + (0.40 \times W) + (0.20 \times O)$
    - $\text{PI} = (0.65 \times T) + (0.35 \times I_{\text{bowler}})$

11. **`PI_BO2_MO` (Middle Overs):**
    - $S = \max(0, \min(100, ((CRR - 7) / (11 - 7)) \times 100))$
    - $W = \max(0, ((6 - W_{\text{before}}) / 6) \times 100)$
    - $O = (O_{\text{comp}} / 9) \times 100$
    - $T = (0.40 \times S) + (0.40 \times W) + (0.20 \times O)$
    - $\text{PI} = (0.65 \times T) + (0.35 \times I_{\text{bowler}})$

12. **`PI_BO2_DO` (Death Overs):**
    - $S = \max(0, \min(100, ((RRR - 9) / (18 - 9)) \times 100))$
    - $W = \max(0, ((6 - W_{\text{before}}) / 6) \times 100)$
    - $O = (O_{\text{comp}} / 5) \times 100$
    - $T = (0.50 \times S) + (0.30 \times W) + (0.20 \times O)$
    - $\text{PI} = (0.65 \times T) + (0.35 \times I_{\text{bowler}})$

---

## 4. Worked Numerical Examples

Below is a complete, manual step-by-step worked calculation for each of the 12 formulas. Every example was cross-verified against the programmatic engine.

```
+-----------+-----------------------------------+---------+---------+---------+-----------+
| Formula   | Inputs Context                    | T Score | I Score | Calc PI | Tier      |
+-----------+-----------------------------------+---------+---------+---------+-----------+
| PI_B1_PP  | W_bef=2, CRR=7.0, O_comp=3, BF=4  | 28.3333 | 60.0000 |  39.42  | Low       |
| PI_B1_MO  | W_bef=3, CRR=6.5, O_comp=4, BF=8  | 36.3889 | 20.0000 |  30.65  | Low       |
| PI_B1_DO  | W_bef=5, CRR=8.5, O_comp=3, BF=12 | 51.3333 |  0.0000 |  33.37  | Low       |
| PI_BO1_PP | W_bef=1, CRR=9.5, O_comp=4, SP=6  | 61.6667 | 25.0000 |  48.83  | Moderate  |
| PI_BO1_MO | W_bef=2, CRR=8.2, O_comp=5, SP=12 | 49.7778 | 70.0000 |  56.86  | Moderate  |
| PI_BO1_DO | W_bef=4, CRR=10.5,O_comp=4, SP=18 | 39.3333 | 50.0000 |  43.07  | Moderate  |
| PI_B2_PP  | Req=140, Rem=102, W=1, O=2, BF=5  | 30.2941 | 50.0000 |  37.19  | Low       |
| PI_B2_MO  | Req=80,  Rem=42,  W=4, O=6, BF=2  | 70.2381 | 80.0000 |  73.65  | High      |
| PI_B2_DO  | Req=24,  Rem=12,  W=6, O=3, BF=18 | 58.6667 |  0.0000 |  38.13  | Low       |
| PI_BO2_PP | W_bef=0, CRR=9.0, O_comp=3, SP=4  | 70.0000 | 26.6667 |  54.83  | Moderate  |
| PI_BO2_MO | W_bef=2, CRR=8.5, O_comp=3, SP=8  | 48.3333 | 33.3333 |  43.08  | Moderate  |
| PI_BO2_DO | Req=36,  Rem=18,  W=3, O=2, SP=10 | 39.6667 | 41.6667 |  40.37  | Moderate  |
+-----------+-----------------------------------+---------+---------+---------+-----------+
```

### Detailed Step-by-Step Breakdown

#### 1. `PI_B1_PP` (Innings 1, Powerplay, Batter)
- **Inputs:** `wickets_before` = 2, `current_run_rate` = 7.00, `phase_overs_completed` = 3, `striker_balls_faced_before` = 4.
- $W = (2 / 6) \times 100 = 33.3333$
- $S = ((8.0 - 7.0) / 8.0) \times 100 = 12.5000$
- $O = (3 / 6) \times 100 = 50.0000$
- $T = (0.40 \times 33.3333) + (0.40 \times 12.5000) + (0.20 \times 50.0000) = 13.3333 + 5.0000 + 10.0000 = 28.3333$
- $I = B = ((10 - 4) / 10) \times 100 = 60.0000$
- $PI = (0.65 \times 28.3333) + (0.35 \times 60.0000) = 18.4167 + 21.0000 = \mathbf{39.42}$ (Tier: **Low**)

#### 2. `PI_B1_MO` (Innings 1, Middle Overs, Batter)
- **Inputs:** `wickets_before` = 3, `current_run_rate` = 6.50, `phase_overs_completed` = 4, `striker_balls_faced_before` = 8.
- $W = (3 / 6) \times 100 = 50.0000$
- $S = ((8.0 - 6.5) / 8.0) \times 100 = 18.7500$
- $O = (4 / 9) \times 100 = 44.4444$
- $T = (0.40 \times 50.0000) + (0.40 \times 18.7500) + (0.20 \times 44.4444) = 20.0000 + 7.5000 + 8.8889 = 36.3889$
- $I = B = ((10 - 8) / 10) \times 100 = 20.0000$
- $PI = (0.65 \times 36.3889) + (0.35 \times 20.0000) = 23.6528 + 7.0000 = \mathbf{30.65}$ (Tier: **Low**)

#### 3. `PI_B1_DO` (Innings 1, Death Overs, Batter)
- **Inputs:** `wickets_before` = 5, `current_run_rate` = 8.50, `phase_overs_completed` = 3, `striker_balls_faced_before` = 12.
- $W = (5 / 6) \times 100 = 83.3333$
- $S = ((10.0 - 8.5) / 10.0) \times 100 = 15.0000$
- $O = (3 / 5) \times 100 = 60.0000$
- $T = (0.40 \times 83.3333) + (0.40 \times 15.0000) + (0.20 \times 60.0000) = 33.3333 + 6.0000 + 12.0000 = 51.3333$
- $I = B = \max(0, ((10 - 12)/10) \times 100) = 0.0000$
- $PI = (0.65 \times 51.3333) + (0.35 \times 0.0000) = \mathbf{33.37}$ (Tier: **Low**)

#### 4. `PI_BO1_PP` (Innings 1, Powerplay, Bowler)
- **Inputs:** `wickets_before` = 1, `current_run_rate` = 9.50, `phase_overs_completed` = 4, `bowler_spell_balls` = 6, `striker_balls_faced_before` = 15.
- $W = ((6 - 1) / 6) \times 100 = 83.3333$
- $S = ((9.5 - 8.0) / 4.0) \times 100 = 37.5000$
- $O = (4 / 6) \times 100 = 66.6667$
- $T = (0.40 \times 83.3333) + (0.40 \times 37.5000) + (0.20 \times 66.6667) = 33.3333 + 15.0000 + 13.3333 = 61.6667$
- $B_{\text{workload}} = (6 / 12) \times 100 = 50.0000$; $S_{\text{settling}} = 0.0000$; $I = (0.50 \times 50) + 0 = 25.0000$
- $PI = (0.65 \times 61.6667) + (0.35 \times 25.0000) = 40.0833 + 8.7500 = \mathbf{48.83}$ (Tier: **Moderate**)

#### 5. `PI_BO1_MO` (Innings 1, Middle Overs, Bowler)
- **Inputs:** `wickets_before` = 2, `current_run_rate` = 8.20, `phase_overs_completed` = 5, `bowler_spell_balls` = 12, `striker_balls_faced_before` = 6.
- $W = ((6 - 2) / 6) \times 100 = 66.6667$
- $S = ((8.2 - 7.0) / 4.0) \times 100 = 30.0000$
- $O = (5 / 9) \times 100 = 55.5556$
- $T = (0.40 \times 66.6667) + (0.40 \times 30.0000) + (0.20 \times 55.5556) = 26.6667 + 12.0000 + 11.1111 = 49.7778$
- $B_{\text{workload}} = (12 / 12) \times 100 = 100.0000$; $S_{\text{settling}} = 40.0000$; $I = (0.50 \times 100) + (0.50 \times 40) = 70.0000$
- $PI = (0.65 \times 49.7778) + (0.35 \times 70.0000) = 32.3556 + 24.5000 = \mathbf{56.86}$ (Tier: **Moderate**)

#### 6. `PI_BO1_DO` (Innings 1, Death Overs, Bowler)
- **Inputs:** `wickets_before` = 4, `current_run_rate` = 10.50, `phase_overs_completed` = 4, `bowler_spell_balls` = 18, `striker_balls_faced_before` = 20.
- $W = ((6 - 4) / 6) \times 100 = 33.3333$
- $S = ((10.5 - 9.0) / 6.0) \times 100 = 25.0000$
- $O = (4 / 5) \times 100 = 80.0000$
- $T = (0.40 \times 33.3333) + (0.40 \times 25.0000) + (0.20 \times 80.0000) = 13.3333 + 10.0000 + 16.0000 = 39.3333$
- $B_{\text{workload}} = \min(100, (18 / 12) \times 100) = 100.0000$; $S_{\text{settling}} = 0.0000$; $I = 50.0000$
- $PI = (0.65 \times 39.3333) + (0.35 \times 50.0000) = 25.5667 + 17.5000 = \mathbf{43.07}$ (Tier: **Moderate**)

#### 7. `PI_B2_PP` (Innings 2, Powerplay, Batter)
- **Inputs:** `runs_required` = 140, `balls_remaining` = 102, `wickets_before` = 1, `phase_overs_completed` = 2, `striker_balls_faced_before` = 5.
- $RRR = (140 / 102) \times 6 = 8.2353$
- $R = ((8.2353 - 6.0) / 6.0) \times 100 = 37.2549$
- $W = (1 / 6) \times 100 = 16.6667$
- $O = (2 / 6) \times 100 = 33.3333$
- $T = (0.50 \times 37.2549) + (0.30 \times 16.6667) + (0.20 \times 33.3333) = 18.6275 + 5.0000 + 6.6667 = 30.2941$
- $I = B = ((10 - 5) / 10) \times 100 = 50.0000$
- $PI = (0.65 \times 30.2941) + (0.35 \times 50.0000) = 19.6912 + 17.5000 = \mathbf{37.19}$ (Tier: **Low**)

#### 8. `PI_B2_MO` (Innings 2, Middle Overs, Batter)
- **Inputs:** `runs_required` = 80, `balls_remaining` = 42, `wickets_before` = 4, `phase_overs_completed` = 6, `striker_balls_faced_before` = 2.
- $RRR = (80 / 42) \times 6 = 11.4286$
- $R = ((11.4286 - 7.0) / 6.0) \times 100 = 73.8095$
- $W = (4 / 6) \times 100 = 66.6667$
- $O = (6 / 9) \times 100 = 66.6667$
- $T = (0.50 \times 73.8095) + (0.30 \times 66.6667) + (0.20 \times 66.6667) = 36.9048 + 20.0000 + 13.3333 = 70.2381$
- $I = B = ((10 - 2) / 10) \times 100 = 80.0000$
- $PI = (0.65 \times 70.2381) + (0.35 \times 80.0000) = 45.6548 + 28.0000 = \mathbf{73.65}$ (Tier: **High**)

#### 9. `PI_B2_DO` (Innings 2, Death Overs, Batter)
- **Inputs:** `runs_required` = 24, `balls_remaining` = 12, `wickets_before` = 6, `phase_overs_completed` = 3, `striker_balls_faced_before` = 18.
- $RRR = (24 / 12) \times 6 = 12.0000$
- $R = ((12.0 - 9.0) / 9.0) \times 100 = 33.3333$
- $W = (6 / 6) \times 100 = 100.0000$
- $O = (3 / 5) \times 100 = 60.0000$
- $T = (0.50 \times 33.3333) + (0.30 \times 100.0000) + (0.20 \times 60.0000) = 16.6667 + 30.0000 + 12.0000 = 58.6667$
- $I = B = 0.0000$
- $PI = (0.65 \times 58.6667) + (0.35 \times 0.0000) = \mathbf{38.13}$ (Tier: **Low**)

#### 10. `PI_BO2_PP` (Innings 2, Powerplay, Bowler)
- **Inputs:** `wickets_before` = 0, `current_run_rate` = 9.00, `phase_overs_completed` = 3, `bowler_spell_balls` = 4, `striker_balls_faced_before` = 8.
- $S = ((9.0 - 6.0) / 6.0) \times 100 = 50.0000$
- $W = ((6 - 0) / 6) \times 100 = 100.0000$
- $O = (3 / 6) \times 100 = 50.0000$
- $T = (0.40 \times 50.0000) + (0.40 \times 100.0000) + (0.20 \times 50.0000) = 20.0000 + 40.0000 + 10.0000 = 70.0000$
- $B_{\text{workload}} = (4 / 12) \times 100 = 33.3333$; $S_{\text{settling}} = 20.0000$; $I = (0.50 \times 33.3333) + (0.50 \times 20.0000) = 26.6667$
- $PI = (0.65 \times 70.0000) + (0.35 \times 26.6667) = 45.5000 + 9.3333 = \mathbf{54.83}$ (Tier: **Moderate**)

#### 11. `PI_BO2_MO` (Innings 2, Middle Overs, Bowler)
- **Inputs:** `wickets_before` = 2, `current_run_rate` = 8.50, `phase_overs_completed` = 3, `bowler_spell_balls` = 8, `striker_balls_faced_before` = 14.
- $S = ((8.5 - 7.0) / 4.0) \times 100 = 37.5000$
- $W = ((6 - 2) / 6) \times 100 = 66.6667$
- $O = (3 / 9) \times 100 = 33.3333$
- $T = (0.40 \times 37.5000) + (0.40 \times 66.6667) + (0.20 \times 33.3333) = 15.0000 + 26.6667 + 6.6667 = 48.3333$
- $B_{\text{workload}} = (8 / 12) \times 100 = 66.6667$; $S_{\text{settling}} = 0.0000$; $I = 33.3333$
- $PI = (0.65 \times 48.3333) + (0.35 \times 33.3333) = 31.4167 + 11.6667 = \mathbf{43.08}$ (Tier: **Moderate**)

#### 12. `PI_BO2_DO` (Innings 2, Death Overs, Bowler)
- **Inputs:** `runs_required` = 36, `balls_remaining` = 18, `wickets_before` = 3, `phase_overs_completed` = 2, `bowler_spell_balls` = 10, `striker_balls_faced_before` = 11.
- $RRR = (36 / 18) \times 6 = 12.0000$
- $S = ((12.0 - 9.0) / 9.0) \times 100 = 33.3333$
- $W = ((6 - 3) / 6) \times 100 = 50.0000$
- $O = (2 / 5) \times 100 = 40.0000$
- $T = (0.50 \times 33.3333) + (0.30 \times 50.0000) + (0.20 \times 40.0000) = 16.6667 + 15.0000 + 8.0000 = 39.6667$
- $B_{\text{workload}} = (10 / 12) \times 100 = 83.3333$; $S_{\text{settling}} = 0.0000$; $I = 41.6667$
- $PI = (0.65 \times 39.6667) + (0.35 \times 41.6667) = 25.7833 + 14.5833 = \mathbf{40.37}$ (Tier: **Moderate**)

---

## 5. Real-Match Delivery Examples from the Dataset

Below are 12 actual deliveries extracted directly from `data/processed/delivery_pressure_index.csv` representing each formula in actual competition play:

| Formula | Match ID | Inn | Over.Ball | Striker | Bowler | Score Before | Wkts | CRR | RRR | Batting PI | Bowling PI |
|:---|:---:|:---:|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `PI_B1_PP` | 31283 | 1 | 6.5 | Tom Kohler | Harshal Patel | 38/1 | 1 | 6.71 | — | **19.36** | 38.33 |
| `PI_B1_MO` | 31286 | 1 | 7.6 | Virat Kohli | Ravindra Jadeja | 51/0 | 0 | 7.46 | — | **1.76** | 36.28 |
| `PI_B1_DO` | 31279 | 1 | 19.5 | Riyan Parag | Shardul Thakur | 129/3 | 3 | 6.91 | — | **28.83** | 26.63 |
| `PI_BO1_PP` | 31283 | 1 | 6.5 | Tom Kohler | Harshal Patel | 38/1 | 1 | 6.71 | — | 19.36 | **38.33** |
| `PI_BO1_MO` | 31286 | 1 | 7.6 | Virat Kohli | Ravindra Jadeja | 51/0 | 0 | 7.46 | — | 1.76 | **36.28** |
| `PI_BO1_DO` | 31279 | 1 | 19.5 | Riyan Parag | Shardul Thakur | 129/3 | 3 | 6.91 | — | 28.83 | **26.63** |
| `PI_B2_PP` | 31287 | 2 | 1.1 | Travis Head | Arshdeep Singh | 0/0 | 0 | 0.00 | 10.70 | **60.46** | 43.50 |
| `PI_B2_MO` | 31282 | 2 | 9.6 | Nicholas Pooran | Gulbadin Naib | 85/5 | 5 | 9.62 | 11.10 | **41.37** | 31.54 |
| `PI_B2_DO` | 31254 | 2 | 17.6 | S Prabhudessai | V Chakravarthy | 186/6 | 6 | 11.05 | 11.68 | **31.79** | 28.33 |
| `PI_BO2_PP` | 31287 | 2 | 1.1 | Travis Head | Arshdeep Singh | 0/0 | 0 | 0.00 | 10.70 | 60.46 | **43.50** |
| `PI_BO2_MO` | 31282 | 2 | 9.6 | Nicholas Pooran | Gulbadin Naib | 85/5 | 5 | 9.62 | 11.10 | 41.37 | **31.54** |
| `PI_BO2_DO` | 31254 | 2 | 17.6 | S Prabhudessai | V Chakravarthy | 186/6 | 6 | 11.05 | 11.68 | 31.79 | **28.33** |

---

## 6. Comprehensive Statistical Distributions

### 6.1 Formula-Level Descriptive Statistics

| Formula Column | Deliveries Count | Min | Mean | Median | Max | Std Dev | Active Role |
|:---|---:|:---:|:---:|:---:|:---:|:---:|:---|
| `PI_B1_PP` | 29,582 | 2.17 | 29.84 | 27.83 | 86.71 | 16.10 | Batter (Inn 1, PP) |
| `PI_B1_MO` | 44,036 | 0.00 | 27.22 | 23.98 | 83.25 | 17.25 | Batter (Inn 1, Middle) |
| `PI_B1_DO` | 24,560 | 0.00 | 39.37 | 37.05 | 84.11 | 17.55 | Batter (Inn 1, Death) |
| `PI_BO1_PP` | 29,582 | 19.50 | 48.21 | 45.58 | 91.33 | 10.56 | Bowler (Inn 1, PP) |
| `PI_BO1_MO` | 44,036 | 1.44 | 40.47 | 39.76 | 89.89 | 13.72 | Bowler (Inn 1, Middle) |
| `PI_BO1_DO` | 24,560 | 0.00 | 24.71 | 23.95 | 67.60 | 10.95 | Bowler (Inn 1, Death) |
| `PI_B2_PP` | 29,597 | 2.17 | 40.24 | 39.89 | 94.58 | 16.20 | Batter (Inn 2, PP) |
| `PI_B2_MO` | 42,793 | 0.00 | 38.37 | 36.19 | 98.56 | 22.17 | Batter (Inn 2, Middle) |
| `PI_B2_DO` | 17,762 | 0.00 | 47.20 | 48.62 | 97.40 | 24.42 | Batter (Inn 2, Death) |
| `PI_BO2_PP` | 29,597 | 18.08 | 51.81 | 49.83 | 91.33 | 11.18 | Bowler (Inn 2, PP) |
| `PI_BO2_MO` | 42,793 | 2.89 | 40.45 | 40.04 | 89.89 | 13.60 | Bowler (Inn 2, Middle) |
| `PI_BO2_DO` | 17,762 | 0.00 | 35.62 | 34.72 | 85.05 | 16.28 | Bowler (Inn 2, Death) |

### 6.2 Unified Pressure Index Metrics

| Metric Column | Total Count | Missing / Null | Minimum | Mean | Median | Maximum | Std Dev |
|:---|---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Batting_PI` | 188,330 | 0 | 0.00 | 35.68 | 33.60 | 98.56 | 20.03 |
| `Bowling_PI` | 188,330 | 0 | 0.00 | 40.95 | 41.78 | 91.33 | 15.09 |

### 6.3 Pressure Level Tier Frequencies

#### Batting Pressure Level Distribution
- **Low (20–40]:** 65,779 deliveries (34.93%)
- **Moderate (40–60]:** 49,482 deliveries (26.27%)
- **Very Low [0–20]:** 48,725 deliveries (25.87%)
- **High (60–80]:** 19,978 deliveries (10.61%)
- **Very High (80–100]:** 4,366 deliveries (2.32%)
- *Total:* 188,330 deliveries (100.0%)

#### Bowling Pressure Level Distribution
- **Moderate (40–60]:** 81,672 deliveries (43.37%)
- **Low (20–40]:** 68,242 deliveries (36.24%)
- **High (60–80]:** 20,484 deliveries (10.88%)
- **Very Low [0–20]:** 17,604 deliveries (9.35%)
- **Very High (80–100]:** 328 deliveries (0.17%)
- *Total:* 188,330 deliveries (100.0%)

### 6.4 Cross-Tabulations

#### Phase $\times$ Batting Pressure Level
| Phase | Very Low | Low | Moderate | High | Very High | Total |
|:---|---:|---:|---:|---:|---:|---:|
| **Powerplay (PP)** | 13,561 | 22,546 | 18,069 | 4,744 | 259 | 59,179 |
| **Middle Overs (MO)** | 28,687 | 28,697 | 19,666 | 7,693 | 2,086 | 86,829 |
| **Death Overs (DO)** | 6,477 | 14,536 | 11,747 | 7,541 | 2,021 | 42,322 |
| **Total** | **48,725** | **65,779** | **49,482** | **19,978** | **4,366** | **188,330** |

#### Phase $\times$ Bowling Pressure Level
| Phase | Very Low | Low | Moderate | High | Very High | Total |
|:---|---:|---:|---:|---:|---:|---:|
| **Powerplay (PP)** | 9 | 9,475 | 37,580 | 11,875 | 240 | 59,179 |
| **Middle Overs (MO)** | 5,004 | 38,638 | 35,850 | 7,252 | 85 | 86,829 |
| **Death Overs (DO)** | 12,591 | 20,129 | 8,242 | 1,357 | 3 | 42,322 |
| **Total** | **17,604** | **68,242** | **81,672** | **20,484** | **328** | **188,330** |

#### Innings $\times$ Batting Pressure Level
| Innings | Very Low | Low | Moderate | High | Very High | Total |
|:---|---:|---:|---:|---:|---:|---:|
| **Innings 1** | 31,505 | 37,248 | 21,836 | 7,513 | 76 | 98,178 |
| **Innings 2** | 17,220 | 28,531 | 27,646 | 12,465 | 4,290 | 90,152 |
| **Total** | **48,725** | **65,779** | **49,482** | **19,978** | **4,366** | **188,330** |

> [!NOTE]
> Notice the sharp contrast in extreme pressure: Innings 2 features **4,290** deliveries of "Very High" batting pressure compared to only **76** in Innings 1. This correctly reflects the compounding pressure of chasing steep targets under collapsing wickets.

---

## 7. The 12 Technical Validation Checks (Part G Audit)

### Test 1: Independent Formula Verification
Every one of the 12 formulas was tested in isolation. The output masks strictly segregate:
- Innings 1: 98,178 deliveries (PP: 29,582, MO: 44,036, DO: 24,560)
- Innings 2: 90,152 deliveries (PP: 29,597, MO: 42,793, DO: 17,762)
Each formula acts only within its legitimate mask.

### Test 2: Programmatic vs. Manual Calculation Consistency
All 12 manual worked examples in Section 4 were checked against program outputs. Discrepancies between manual KaTeX/hand computations and vectorized numpy operations were less than $0.01$ (strictly attributable to 2-decimal rounding).

### Test 3 & 4: Full Coverage across Both Innings and All Three Phases
Across the 1,578 completed innings in 789 matches:
- Innings 1: 100% of deliveries have valid `Batting_PI` and `Bowling_PI`.
- Innings 2: 100% of deliveries have valid `Batting_PI` and `Bowling_PI`.
- PP, MO, and DO phases all contain expected delivery volumes and transition seamlessly at overs 7.1 and 16.1.

### Test 5: First Delivery Invariants (Innings 1 & 2 Ball 1)
At Over 1, Ball 1 (`innings_ball_num == 1`):
- **Innings 1 Ball 1 Batting:**
  $W = 0$, $S = 100.0$ ($CRR = 0.0$), $O = 0$, $T = 40.0$, $I = 100.0$ ($BF = 0$).
  $$PI = (0.65 \times 40.0) + (0.35 \times 100.0) = 26.0 + 35.0 = \mathbf{61.00}$$
  *Result:* Exactly $61.00$ across all 789 matches ($\sigma = 0.0$).
- **Innings 1 Ball 1 Bowling:**
  $W = 100.0$ ($W_{\text{before}} = 0$), $S = 0.0$ ($CRR = 0.0 \le 8$), $O = 0$, $T = 40.0$, $I = 50.0$ ($Workload = 0$, $Settling = 100$).
  $$PI = (0.65 \times 40.0) + (0.35 \times 50.0) = 26.0 + 17.5 = \mathbf{43.50}$$
  *Result:* Exactly $43.50$ across all 789 matches ($\sigma = 0.0$).
- **Innings 2 Ball 1 Bowling:**
  Identical initial state: $W = 100.0$, $S = 0.0$, $O = 0$, $T = 40.0$, $I = 50.0$.
  $$PI = \mathbf{43.50}$$
  *Result:* Exactly $43.50$ across all 789 matches ($\sigma = 0.0$).
- **Innings 2 Ball 1 Batting:**
  $W = 0$, $O = 0$, $BF = 0 \implies I = 100.0$.
  $T = 0.50 \times R = 0.50 \times \text{clip}\left(\frac{(\text{Target}/20) - 6}{6} \times 100, 0, 100\right)$.
  *Result:* Range is strictly $[35.00, 67.50]$ with mean $50.57$, varying purely with target magnitude.

### Test 6: Zero and Maximum Boundary Clamping
Tested under boundary conditions:
- Batters with $\ge 10$ balls faced have $B = 0.00$.
- Bowlers with $\ge 12$ spell balls have $B_{\text{workload}} = 100.00$.
- Overs completed at start of phase ($0.0$) yield $O = 0.00$.
- CRR and RRR values far above or below thresholds are smoothly clipped to $0.00$ or $100.00$ without mathematical overflow or invalid values.

### Test 7: RRR and CRR Edge Cases
- **CRR = 0.0 at Ball 1:** Cleanly handled by vectorized clipping:
  - Batter PP scoring pressure: $((8 - 0)/8) \times 100 = 100.0$.
  - Bowler PP scoring pressure: $\max(0, ((0 - 8)/4) \times 100) = 0.0$.
- **Balls Remaining > 0:** `balls_remaining` in Innings 2 is strictly between 1 and 120 (minimum observed is 1). No division by zero can occur.
- **Runs Required $\le$ 0:** In 233 deliveries where the target had already been reached or tied prior to anomalous extra balls in the feed, $RRR \le 0.0$. The scoring component $R$ or $S$ cleanly evaluates to $\max(0, \text{negative}) = 0.00$, keeping team pressure well-behaved.

### Test 8: Missing and Invalid Input Handling
- Innings 1 correctly has `NaN` for `runs_required` and `required_run_rate`, which are not used by any Innings 1 formula.
- The 12 individual formula columns are strictly populated for their target subset and `NaN` elsewhere.
- Unified columns `Batting_PI` and `Bowling_PI` have **zero** nulls across all 188,330 rows.

### Test 9: Strict Score Range Enforcement
```python
assert (df['Batting_PI'] >= 0.0).all() and (df['Batting_PI'] <= 100.0).all()
assert (df['Bowling_PI'] >= 0.0).all() and (df['Bowling_PI'] <= 100.0).all()
```
Both assertions passed with 0 violations.

### Test 10: Formula Selection & Mutual Exclusivity
```python
assert (df[batting_formula_cols].notnull().sum(axis=1) == 1).all()
assert (df[bowling_formula_cols].notnull().sum(axis=1) == 1).all()
```
For every single delivery, exactly one batting formula and one bowling formula are active.

### Test 11: Zero Lookahead Leakage Audit
To ensure that PI reflects pre-delivery context only, we checked correlations with current ball outcome columns:
- Correlation `Batting_PI` with `runs` (batter runs on current ball): $r = -0.0776$
- Correlation `Batting_PI` with `is_wicket`: $r = +0.0267$
- Correlation `Bowling_PI` with `bowler_runs_conceded`: $r = -0.0015$
- Correlation `Bowling_PI` with `is_wicket`: $r = -0.0202$

These near-zero correlations confirm that current ball events do not leak into the pre-delivery Pressure Index.

### Test 12: Dataset Integrity & Row Conservation
- Input row count (`delivery_match_state.csv`): 188,330
- Output row count (`delivery_pressure_index.csv`): 188,330
- Total columns increased from 49 to 65 (+12 formula columns, +2 unified PI columns, +2 categorical level columns).
- Zero rows were dropped, duplicated, or reordered.

---

## 8. Known Caveats, Limitations & Next Steps

1. **Extras Representation Limitation:** As documented in Step 2, byes and leg-byes use a conservative 1-run proxy because the raw feed aggregates fielding extras into ball totals without multi-run byes breakdowns. This minor limitation affects cumulative score reconstruction by $< 0.4\%$ of total runs and has no meaningful distortion on CRR/RRR.
2. **Provisional Parameters:** As noted in the competition brief, all weights ($0.65/0.35$ master split, $0.40/0.40/0.20$ team component weights) and threshold anchors ($8.0$ CRR, $12.0$ RRR, etc.) are provisional specifications designed to measure objective situational pressure rather than subjective player psychology.
3. **No Ranking Leakage:** In accordance with prompt instructions, no player rankings, reliability metrics (Bayesian shrinkage / regressed win probabilities), or machine learning models have been trained or applied in this step.
4. **Readiness for Player Performance Modeling:** The generated dataset `data/processed/delivery_pressure_index.csv` is fully validated, mathematically consistent, and ready for Step 5: Player Performance Evaluation under Pressure.
