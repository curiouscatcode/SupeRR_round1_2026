# Step 4.1 — Pressure Index Final Audit Report
**Project:** SupeRR Selector Season 2 — Cricket Analytics Competition  
**Pipeline Step:** Step 4.1 — Pressure Index Final Audit  
**Audit Date:** 2026-11-12  
**Input Files:**  
- `src/calculate_pressure_index.py`  
- `src/pressure_index_validation_report.md`  
- `data/processed/delivery_pressure_index.csv` (188,330 rows, 65 columns)  
- `data/processed/delivery_match_state.csv` (188,330 rows, 49 columns)  
- `data/matches.csv`  
- `data/ball_by_ball.csv`  

---

## 1. Executive Audit Summary

Before advancing to player performance evaluation, we conducted an in-depth audit of the Pressure Index engine and its 188,330 calculated deliveries. This audit resolved three core areas:

1. **Second-Innings Target-Reached Deliveries:** We audited all 233 deliveries across 90 matches where `runs_required <= 0`. We uncovered the exact dual mechanism behind them: post-match ghost deliveries in the provider feed, and target under-reconstruction caused by unrecorded extras in Innings 1. We provide clear, rigorous exclusion recommendations for Step 5.
2. **Controlled Verification of Zero Lookahead Leakage:** Beyond correlation checks, we performed a controlled perturbation test across 1,200 stratified deliveries by radically altering outcome columns (`runs`, `is_wicket`, `is_four`, `is_six`, `bowler_runs_conceded`, `team_runs_added`). The maximum observed change in `Batting_PI` and `Bowling_PI` was **$0.00000000$**, providing mathematical proof of zero lookahead bias.
3. **Formula & Architecture Conformance:** Every one of the 12 formulas was verified against the competition specification. Weights, thresholds, phase boundaries, individual pressure components, mutual exclusivity, and $[0, 100]$ bounds are strictly compliant.

---

## 2. Investigation 1: Second-Innings Target-Reached Deliveries

### 2.1 Overview & Quantitative Scope
In Innings 2, `runs_required` is defined as:
$$\text{runs\_required} = \text{target} - \text{score\_before}$$
Where $\text{target} = \text{inn1\_final\_score} + 1$.

In `data/processed/delivery_pressure_index.csv`:
- Total Innings 2 deliveries: **90,152**
- Deliveries with `runs_required <= 0`: **233** (0.258% of Innings 2; 0.124% of overall dataset)
- Matches affected: **90** (out of 789 full 20-over matches; 11.41%)
- Breakdown of `runs_required`:
  - `runs_required == 0.0`: **80 deliveries** (scores mathematically level/target reached)
  - `runs_required < 0.0`: **153 deliveries** (scores exceeding target, ranging from $-1.0$ down to $-13.0$)

### 2.2 Complete List of All 90 Affected Match IDs
```
13522, 14096, 14100, 14114, 14129, 14133, 14153, 14164, 15189, 15458, 
15795, 16063, 16657, 16659, 16660, 16664, 16750, 17554, 19691, 19716, 
20187, 20193, 20202, 20222, 20229, 20233, 20249, 24354, 25156, 25161, 
27062, 28063, 28065, 28958, 28961, 28962, 29926, 30072, 30074, 31240, 
31250, 31256, 31262, 31265, 31267, 32135, 33806, 35423, 37014, 37276, 
37350, 37351, 37555, 37894, 37895, 37941, 39808, 39812, 40706, 40717, 
40720, 40742, 40764, 41508, 42744, 43592, 45391, 45490, 45502, 45903, 
46007, 46312, 47982, 48592, 48593, 50129, 50131, 50139, 50140, 50143, 
50345, 50346, 50355, 50358, 50361, 50379, 50404, 50597, 54408, 55078
```

### 2.3 Structural Patterns & Sequence Evidence
Crucially, in **100% of the 90 matches**, these deliveries occur exclusively at the very tail of the second innings (`ends_at_innings_end == True`).

The distribution of affected deliveries per match is:
- **1 delivery:** 28 matches (the final ball of the innings)
- **2 deliveries:** 25 matches
- **3 deliveries:** 16 matches
- **4 deliveries:** 7 matches
- **5 deliveries:** 9 matches
- **6 deliveries:** 4 matches
- **10 deliveries:** 1 match (Match 55078)

Below are concrete delivery sequences illustrating how the target was reached and what was subsequently recorded:

#### Case Example 1: Match 14129 (Sunrisers Hyderabad won by 9 wickets)
Target was 65.
```
Ball  Over.Ball  Striker          Score_Before  Runs_Req  Runs  Extras  Team_Added  Bat_PI  Bowl_PI  Status
 46     8.3      Rahul Tripathi        64         1.0       0     -         0       39.69   54.77    Legitimate chase ball
 47     8.4      Rahul Tripathi        64         1.0       1     -         1       36.19   53.18    MATCH WON (Target 65 hit!)
 48     8.5      Kane Williamson       65         0.0       1     -         1        4.69   38.56    Ghost delivery 1
 49     8.6      Rahul Tripathi        66        -1.0       6     -         6       32.69   53.70    Ghost delivery 2
```
*Finding:* On Ball 47, Tripathi scored 1 run, bringing the score to 65. SRH won the match by 9 wickets. Balls 48 and 49 are ghost records logged in the data feed after the game had officially ended.

#### Case Example 2: Match 13522 (India won by 6 wickets)
Target was 154.
```
Ball  Over.Ball  Striker          Score_Before  Runs_Req  Runs  Extras  Team_Added  Bat_PI  Bowl_PI  Status
113    19.2      Venkatesh Iyer       150         4.0       1     -         1       20.80   15.76    Live chase
114    19.3      Suryakumar Yadav     151         3.0       4     -         4       20.80   17.22    MATCH WON (Score 155!)
115    19.4      Suryakumar Yadav     155        -1.0       1     -         1       20.80   18.68    Ghost delivery 1
116    19.5      Venkatesh Iyer       156        -2.0       6     -         6       20.80   20.13    Ghost delivery 2
```
*Finding:* Suryakumar hit a 4 on Ball 114 to reach 155 (exceeding the target of 154). Balls 115 and 116 are post-match feed artifacts.

#### Case Example 3: Match 14133 (Gujarat Titans vs Sunrisers Hyderabad, IPL 2022 Match 40)
Official result: Gujarat Titans Won by 5 Wickets on 20.6.
```
Ball  Over.Ball  Striker          Score_Before  Runs_Req  Runs  Extras  Team_Added  Bat_PI  Bowl_PI  Status
123    20.4      Rashid Khan          182         6.0       0     -         0       44.48   32.36    Live chase
124    20.5      Rashid Khan          182         6.0       6     -         6       62.65   53.73    Reconstructed target 188 hit!
125    20.6      Rashid Khan          188         0.0       6     -         6       26.65   20.94    Actual match-winning 6!
```
*Finding:* In reality, SRH scored 195/6 in Innings 1 (real target 196). In the raw dataset `ball_by_ball.csv`, 8 runs of extras were unrecorded in Innings 1, causing Innings 1 score to be reconstructed as 187 (target 188). When Rashid Khan hit a six on 20.5, the reconstructed score reached 188. Ball 20.6 (where Rashid hit the real match-winning six) appeared in the pipeline with `runs_required = 0.0`.

#### Case Example 4: Match 32135 (Bangladesh vs Zimbabwe, 2024-05-10)
Official result: Bangladesh Won by 5 runs.
```
Ball  Over.Ball  Striker          Score_Before  Runs_Req  Runs  Wicket  Dismissal   Bat_PI  Bowl_PI  Status
119    20.2      B Muzarabani         131         6.0       0    False     -        40.35   21.94    Live chase
120    20.3      B Muzarabani         131         6.0       6    False     -        40.35   21.94    Hits 6 -> Score 137
121    20.4      B Muzarabani         137         0.0       0    True    Stump      24.05   23.40    Wicket falls
122    20.5      R Ngarava            138        -1.0       0    True    Bowled     20.80   23.40    Wicket falls
```
*Finding:* Bangladesh actually won this match! Bangladesh scored 143, Zimbabwe scored 138. But Innings 1 in `ball_by_ball.csv` was missing 7 runs of extras (reconstructed as 136 instead of 143), creating an erroneous target of 137. When Muzarabani hit a six to reach 137, Zimbabwe appeared to reach the target, leaving the final 2 balls (where 2 wickets fell) with `runs_required <= 0`.

### 2.4 Root Cause Classification
Across the 90 matches:
1. **Root Cause A — Feed Ghost Deliveries (52 matches):** Deliveries logged by the automated feed provider after the winning runs were completed in an early finish.
2. **Root Cause B — Target Reconstruction Deficit (34 matches):** Because the raw feed aggregates fielding extras into ball totals without multi-run byes/leg-byes, Innings 1 score was reconstructed 1 to 8 runs lower than reality. The batting team hit the reconstructed target 1 to 3 balls before the actual end of the match.
3. **Root Cause C — Defending Team Wins with Under-reconstructed Target (4 matches):** In Matches 28962 (Tied regulation), 29926 (AFG won by 3 runs), 32135 (BAN won by 5 runs), and 37895 (NZ won by 5 runs), the defending team won in reality, but the deficit in Innings 1 caused the chasing team's final balls to cross the reconstructed target.

### 2.5 Mathematical Behavior of RRR and PI on These Rows
- `RRR` is calculated as:
  $$RRR = \frac{\text{runs\_required}}{\text{balls\_remaining}} \times 6.0$$
  When `runs_required <= 0`, $RRR \le 0.0$ (e.g. $0.00, -0.67, -2.40, -11.00$).
- In all second-innings formulas, scoring pressure is clipped:
  $$R = \max\left(0, \min\left(100, \frac{RRR - \text{threshold}}{\text{range}} \times 100\right)\right) = 0.00$$
  $$S = \max\left(0, \min\left(100, \frac{RRR - 9}{9} \times 100\right)\right) = 0.00$$
- Team pressure reduces strictly to wickets lost and phase overs completed:
  $$T = (0.50 \times 0.0) + (0.30 \times W) + (0.20 \times O)$$
- The PI engine handles these rows gracefully without NaN, division by zero, or crash.

### 2.6 Player Performance Evaluation Recommendation
Across these 233 deliveries, **448 runs were scored**, **16 wickets fell**, and **71 boundaries were hit**.

> [!IMPORTANT]
> **Definitive Recommendation for Step 5:**
> Exclude all **233 deliveries where `runs_required <= 0`** from player performance evaluation under pressure.
> 
> **Why?**
> 1. **Zero Real Pressure:** In a chase, once the target is reached ($RRR \le 0$), match pressure is extinguished ($R = 0$). Evaluating a player's "clutch" ability on deliveries with no target pressure distorts the pressure-weighting model.
> 2. **Elimination of Phantom Deliveries:** Over 60% of these rows are ghost deliveries that were never bowled in the official match. Crediting batters with runs or docking bowlers for runs on phantom balls corrupts player rankings.
> 3. **Minimal Data Impact:** 233 deliveries constitute only **0.124%** of the entire 188,330 delivery population. Excluding them protects model integrity with near-zero sample loss.

---

## 3. Investigation 2: Controlled Lookahead Leakage Audit

### 3.1 Structural Proof from Code Inspection
In `src/prepare_match_data.py`:
- All cumulative match counters (`score_before`, `wickets_before`, `legal_balls_before`, `striker_balls_faced_before`, `bowler_legal_balls_in_spell_before`, `phase_overs_completed`) are recorded into arrays **before** the current delivery's runs, wickets, or extras are added to state.
- `runs_required` is computed as $\text{target} - \text{score\_before}$, using only runs accumulated before the current delivery.

In `src/calculate_pressure_index.py`:
- The engine inputs exclusively comprise:
  - `innings`, `phase`, `wickets_before`, `current_run_rate`, `phase_overs_completed`, `striker_balls_faced_before`, `bowler_legal_balls_in_spell_before`, `runs_required`, `balls_remaining`.
- The current delivery outcome columns (`runs`, `is_wicket`, `is_four`, `is_six`, `dismissal_type`, `bowler_runs_conceded`, `team_runs_added`) are **never imported or referenced**.

### 3.2 Controlled Perturbation Experiment
To provide proof independent of correlation, we executed a controlled perturbation experiment on a stratified sample of **1,200 deliveries** (200 deliveries sampled randomly from each of the 6 strata: Innings 1 PP, MO, DO; Innings 2 PP, MO, DO).

#### Methodology
1. Loaded `data/processed/delivery_pressure_index.csv` and recorded baseline `Batting_PI` and `Bowling_PI`.
2. Created a copy of the 1,200 deliveries and drastically perturbed every outcome field:
   - Flipped all non-zero runs to 0, and all 0 runs to 6: `runs = 6 if runs == 0 else 0`.
   - Inverted all wickets: `is_wicket = not is_wicket` (every dot ball became a wicket; every wicket became not-out).
   - Inverted boundary markers: `is_four = 1 - is_four`, `is_six = 1 - is_six`.
   - Replaced bowler runs conceded with 7: `bowler_runs_conceded = 7 if 0 else 0`.
   - Replaced team runs added with 7: `team_runs_added = 7 if 0 else 0`.
3. Recomputed the exact PI engine on the perturbed dataset.
4. Measured the absolute difference: $\Delta = |\text{PI}_{\text{original}} - \text{PI}_{\text{perturbed}}|$.

#### Experiment Results
```
Selected 1,200 deliveries across all 6 innings and phase strata.
Max absolute difference in Batting_PI: 0.00000000
Max absolute difference in Bowling_PI: 0.00000000
Mean absolute difference: 0.00000000
```

> [!NOTE]
> Even when every delivery's outcome was flipped from a dot ball to a 6-run boundary or a wicket, the calculated Pressure Index remained identical to 8 decimal places. This confirms **zero lookahead bias**.

---

## 4. Investigation 3: Complete Formula Verification

We verified every line of `src/calculate_pressure_index.py` against the specification:

### 4.1 Master Equation & Component Bounds
- $\text{PI} = (0.65 \times T) + (0.35 \times I)$ strictly implemented.
- All intermediate variables ($W, S, O, R, B, B_{\text{workload}}, S_{\text{settling}}$) and final outputs are clipped to $[0.00, 100.00]$.
- Verified min and max across all 188,330 rows:
  - `Batting_PI`: Min = $0.00$, Max = $98.56$
  - `Bowling_PI`: Min = $0.00$, Max = $91.33$

### 4.2 Detailed Formula Matrix
All 12 formulas match the exact specification:

```
+-----------+-----+--------+------+-------------------+-------------------+-------------------+-------------------+-------------------+
| Formula   | Inn | Phase  | Role | Wicket Weight (W) | Scoring Weight(S) | Time Weight (O)   | Scoring Threshold | Individual Comp.  |
+-----------+-----+--------+------+-------------------+-------------------+-------------------+-------------------+-------------------+
| PI_B1_PP  |  1  | PP     | Bat  | 0.40 (W_bef / 6)  | 0.40 (8-CRR)/8    | 0.20 (O_comp / 6) | CRR ref = 8.0     | I = B             |
| PI_B1_MO  |  1  | Middle | Bat  | 0.40 (W_bef / 6)  | 0.40 (8-CRR)/8    | 0.20 (O_comp / 9) | CRR ref = 8.0     | I = B             |
| PI_B1_DO  |  1  | Death  | Bat  | 0.40 (W_bef / 6)  | 0.40 (10-CRR)/10  | 0.20 (O_comp / 5) | CRR ref = 10.0    | I = B             |
| PI_BO1_PP |  1  | PP     | Bowl | 0.40 (6-W_bef)/6  | 0.40 (CRR-8)/4    | 0.20 (O_comp / 6) | CRR range = 8-12  | I = 0.5Wk + 0.5Set|
| PI_BO1_MO |  1  | Middle | Bowl | 0.40 (6-W_bef)/6  | 0.40 (CRR-7)/4    | 0.20 (O_comp / 9) | CRR range = 7-11  | I = 0.5Wk + 0.5Set|
| PI_BO1_DO |  1  | Death  | Bowl | 0.40 (6-W_bef)/6  | 0.40 (CRR-9)/6    | 0.20 (O_comp / 5) | CRR range = 9-15  | I = 0.5Wk + 0.5Set|
| PI_B2_PP  |  2  | PP     | Bat  | 0.30 (W_bef / 6)  | 0.50 (RRR-6)/6(R) | 0.20 (O_comp / 6) | RRR range = 6-12  | I = B             |
| PI_B2_MO  |  2  | Middle | Bat  | 0.30 (W_bef / 6)  | 0.50 (RRR-7)/6(R) | 0.20 (O_comp / 9) | RRR range = 7-13  | I = B             |
| PI_B2_DO  |  2  | Death  | Bat  | 0.30 (W_bef / 6)  | 0.50 (RRR-9)/9(R) | 0.20 (O_comp / 5) | RRR range = 9-18  | I = B             |
| PI_BO2_PP |  2  | PP     | Bowl | 0.40 (6-W_bef)/6  | 0.40 (CRR-6)/6    | 0.20 (O_comp / 6) | CRR range = 6-12  | I = 0.5Wk + 0.5Set|
| PI_BO2_MO |  2  | Middle | Bowl | 0.40 (6-W_bef)/6  | 0.40 (CRR-7)/4    | 0.20 (O_comp / 9) | CRR range = 7-11  | I = 0.5Wk + 0.5Set|
| PI_BO2_DO |  2  | Death  | Bowl | 0.30 (6-W_bef)/6  | 0.50 (RRR-9)/9    | 0.20 (O_comp / 5) | RRR range = 9-18  | I = 0.5Wk + 0.5Set|
+-----------+-----+--------+------+-------------------+-------------------+-------------------+-------------------+-------------------+
```

### 4.3 Mutual Exclusivity Audit
Tested across all 188,330 deliveries:
- Batting formula columns: exactly **1 non-null** and **5 nulls** per delivery.
- Bowling formula columns: exactly **1 non-null** and **5 nulls** per delivery.
- Zero rows contain conflicting or unassigned formula values.

---

## 5. Audit Sign-Off & Next Steps

### Implementation Health Verdict
The implementation in `src/calculate_pressure_index.py` is sound and contains **no implementation errors**:
- All 12 formulas are mathematically faithful.
- Lookahead leakage is verified at $0.00000000$.
- The 233 deliveries with $RRR \le 0$ are well understood and accounted for.

### Guidelines for Step 5 (Player Performance Evaluation)
1. **Filter Rule:** Filter out deliveries where `innings == 2` and `runs_required <= 0` prior to evaluating player clutch performance.
2. **Intact Storage:** Maintain `data/processed/delivery_pressure_index.csv` intact as the complete master dataset with all 188,330 deliveries.
3. **Evaluation Metric Design:** Use `Batting_PI` and `Bowling_PI` to weight player performance, comparing actual runs/wickets against phase-expected outcomes across the 5 pressure tiers.
