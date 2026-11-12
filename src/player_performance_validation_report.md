# Player Performance Evaluation Under Pressure — Validation Report
**Project:** SupeRR Selector Season 2 — Cricket Analytics Competition  
**Pipeline Step:** Step 5 — Player Performance Evaluation Under Pressure  
**Audit Date:** 2026-11-12  
**Input Datasets:**  
- `data/processed/delivery_pressure_index.csv` (188,330 rows, 65 columns)  
- `data/processed/delivery_match_state.csv` (188,330 rows, 49 columns)  
- `data/matches.csv`  
**Output Datasets:**  
- `data/processed/batter_performance.csv` (816 players, 87 columns)  
- `data/processed/bowler_performance.csv` (589 players, 90 columns)  
**Execution Script:** `src/evaluate_player_performance.py`  

---

## 1. Executive Summary & Audit Overview

Step 5 builds the empirical performance evaluation layer of the SupeRR Selector 2.0 system. It evaluates how each batter and bowler performs across different match contexts, strictly bifurcating each player's career deliveries into **Low / Moderate Pressure** ($\text{PI} \le 60.0$) and **High / Very High Pressure** ($\text{PI} > 60.0$), while also computing granular phase-wise performance across the Powerplay, Middle Overs, and Death Overs.

### Key Audit Highlights
1. **Strict Data Sanitation:** All 233 second-innings target-reached / ghost deliveries (`runs_required <= 0`) identified in Step 4.1 were cleanly excluded. All evaluations were conducted on the 188,097 active, live-match deliveries.
2. **First-Innings & Flagged Match Retention:** 100% of first-innings deliveries were retained. Live second-innings deliveries from the 38 flagged deficit matches were retained while preserving the audit flag `is_target_understated = True` (4,177 clean deliveries).
3. **Exact Mathematical Conservation:**
   - Total Batter Runs: Exactly **252,658 runs** conserved ($226,053$ low/mod $+$ $26,605$ high).
   - Total Balls Faced: Exactly **180,839 balls** conserved ($157,511$ low/mod $+$ $23,328$ high).
   - Total Bowler Runs Conceded: Exactly **260,714 runs** conserved ($230,696$ low/mod $+$ $30,018$ high).
   - Total Bowler Legal Balls: Exactly **180,041 balls** conserved ($160,157$ low/mod $+$ $19,884$ high).
   - Total Bowler Wickets: Exactly **9,542 wickets** conserved ($8,584$ low/mod $+$ $958$ high).
4. **Wicket Attribution Precision:** Bowler wickets were strictly restricted to Bowled, Caught, LBW, Stumped, and Hit Wicket. All 561 non-bowler wickets (RunOut, Retire Out, Obstructing Field) were cleanly excluded from bowler credit.
5. **Zero Duplicate Players:** Output datasets contain exactly **816 unique batters** and **589 unique bowlers**, with 1-to-1 mapping between player IDs and names.

---

## 2. Methodology & Pressure Classification

### 2.1 Pressure Bimodality Rule
In accordance with competition rules:
- **Low / Moderate Pressure:** $\text{PI} \le 60.00$ (representing Very Low, Low, and Moderate match leverage).
- **High / Very High Pressure:** $\text{PI} > 60.00$ (representing High and Very High match leverage).

This binary partition guarantees mathematical completeness: every delivery belongs to exactly one category, ensuring that player totals equal the sum of their low/moderate and high pressure components without unclassified leakage.

### 2.2 Excluded Deliveries
- **233 Second-Innings Deliveries (`innings == 2` & `runs_required <= 0`):** Excluded prior to aggregation. These deliveries occurred after matches were mathematically won or represented automated feed ghost logs.
- Total deliveries evaluated: **188,097 deliveries** across 789 standard 20-over matches.

### 2.3 Sensitivity Tracking (`is_target_understated`)
In the 38 matches identified in Step 4.2 with first-innings reconstruction deficits, live second-innings deliveries were retained and tagged with `is_target_understated = True`. The total balls faced and legal balls bowled under this condition are preserved in the player tables as `target_understated_balls_faced` and `target_understated_legal_balls`.

---

## 3. Batter Performance Evaluation Framework

### 3.1 Metric Definitions (Batter)
All batting metrics are computed on **batter balls faced** (`is_batter_ball_faced == True`, excluding wides, including no-balls) and **batter runs** (`runs`), not team runs or extras:
- **Strike Rate:** $(\text{Runs} / \text{Balls Faced}) \times 100$
- **Boundary Percentage:** $(\text{Boundaries} / \text{Balls Faced}) \times 100$, where $\text{Boundaries} = \text{Fours} + \text{Sixes}$
- **Dot-Ball Percentage:** $(\text{Dot Balls} / \text{Balls Faced}) \times 100$, where $\text{Dot Ball} = (\text{Runs} == 0)$
- **Dismissals:** Count of dismissals suffered by the batter while on strike (`dismissed_player_id == striker_id`)
- **Dismissal Percentage (Out %):** $(\text{Dismissals} / \text{Balls Faced}) \times 100$
- **Batting Average:** $\text{Runs} / \text{Dismissals}$ (or Runs if 0 dismissals)
- **Pressure Differential ($\Delta$):** Metric under High Pressure minus Metric under Low/Moderate Pressure (e.g., `strike_rate_delta = high_strike_rate - low_mod_strike_rate`)

### 3.2 Top 10 Batters Overall (by Total Runs)
```
+------------------+---------+------------+-------------+---------+-----------+------------+---------+------------+----------+
| Player Name      | Matches | Total Runs | Balls Faced | Overall | High Runs | High Balls | High SR | Low/Mod SR | SR Delta |
+------------------+---------+------------+-------------+---------+-----------+------------+---------+------------+----------+
| Suryakumar Yadav |   133   |    4415    |    2653     | 166.42  |    209    |    152     | 137.50  |   168.17   |  -30.67  |
| Jos Buttler      |   115   |    4166    |    2675     | 155.74  |    111    |     80     | 138.75  |   156.26   |  -17.51  |
| Abhishek Sharma  |   125   |    4091    |    2195     | 186.38  |     81    |     76     | 106.58  |   189.24   |  -82.66  |
| Shubman Gill     |   107   |    3901    |    2606     | 149.69  |     37    |     29     | 127.59  |   149.94   |  -22.35  |
| Virat Kohli      |    89   |    3555    |    2445     | 145.40  |     56    |     47     | 119.15  |   145.91   |  -26.76  |
| Ishan Kishan     |   118   |    3480    |    2385     | 145.91  |     86    |     74     | 116.22  |   146.86   |  -30.64  |
| Sanju Samson     |   120   |    3415    |    2208     | 154.66  |     93    |     91     | 102.20  |   156.92   |  -54.72  |
| N Tilak Varma    |   117   |    3399    |    2356     | 144.27  |    254    |    196     | 129.59  |   145.60   |  -16.01  |
| Nicholas Pooran  |   111   |    2977    |    1894     | 157.18  |    242    |    163     | 148.47  |   158.00   |   -9.53  |
| Lokesh Rahul     |    72   |    2821    |    1994     | 141.47  |     40    |     41     |  97.56  |   142.40   |  -44.84  |
+------------------+---------+------------+-------------+---------+-----------+------------+---------+------------+----------+
```

### 3.3 Top 10 Batters by High-Pressure Volume (Min. 50 Balls Faced)
```
+----------------------+------------+-------------+---------+------------+-----------+---------+------------+----------+
| Player Name          | High Runs  | High Balls  | High SR | Boundary % | Dot Ball% | Out %   | Low/Mod SR | SR Delta |
+----------------------+------------+-------------+---------+------------+-----------+---------+------------+----------+
| Axar Patel           |    401     |     321     | 124.92  |   14.33%   |   35.83%  |  6.85%  |   142.66   |  -17.74  |
| Rashid Khan          |    380     |     265     | 143.40  |   18.49%   |   42.64%  |  7.55%  |   164.60   |  -21.20  |
| Rovman Powell        |    349     |     275     | 126.91  |   16.36%   |   44.73%  |  4.73%  |   149.68   |  -22.77  |
| MS Dhoni             |    331     |     194     | 170.62  |   25.26%   |   32.99%  |  4.12%  |   135.85   |  +34.77  |
| Jason Holder         |    328     |     224     | 146.43  |   16.96%   |   35.71%  |  7.59%  |   138.12   |   +8.31  |
| Romario Shepherd     |    315     |     254     | 124.02  |   15.75%   |   44.49%  |  4.72%  |   174.82   |  -50.80  |
| Rinku Singh          |    259     |     177     | 146.33  |   19.21%   |   38.42%  |  2.82%  |   152.30   |   -5.97  |
| N Tilak Varma        |    254     |     196     | 129.59  |   16.84%   |   38.78%  |  3.57%  |   145.60   |  -16.01  |
| Shimron Hetmyer      |    250     |     204     | 122.55  |   16.18%   |   45.10%  |  2.94%  |   156.14   |  -33.59  |
| Shivam Dube          |    249     |     160     | 155.62  |   20.62%   |   31.25%  |  2.50%  |   153.70   |   +1.92  |
+----------------------+------------+-------------+---------+------------+-----------+---------+------------+----------+
```

> [!NOTE]
> **Elite Pressure Findings (Batting):**
> - **MS Dhoni** exhibits extraordinary clutch acceleration: Strike Rate leaps from **$135.85$** under low/moderate pressure to **$170.62$** under high pressure ($+34.77$ delta), striking boundaries on **$25.26\%$** of high-pressure deliveries with only 8 dismissals in 194 balls.
> - **Rinku Singh** demonstrates extreme reliability: High pressure SR of **$146.33$** with an ultra-low dismissal rate of **$2.82\%$** (dismissed only 5 times in 177 high-pressure balls).
> - **Shivam Dube** maintains higher strike power under pressure: SR increases from **$153.70$** to **$155.62$** ($+1.92$ delta), with a **$2.50\%$** dismissal rate.

---

## 4. Bowler Performance Evaluation Framework

### 4.1 Metric Definitions (Bowler)
All bowling metrics are computed using pre-validated legal balls (`is_legal_ball`) and bowler runs conceded (`bowler_runs_conceded`):
- **Economy Rate:** $(\text{Runs Conceded} / \text{Legal Balls}) \times 6.0$
- **Wickets:** Wickets attributed strictly to the bowler (`dismissal_type.isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])`)
- **Bowling Average:** $\text{Runs Conceded} / \text{Wickets}$
- **Bowling Strike Rate:** $\text{Legal Balls} / \text{Wickets}$
- **Dot-Ball Percentage:** $(\text{Dot Deliveries} / \text{Legal Balls}) \times 100$, where Dot Delivery $= (\text{Runs Conceded} == 0)$
- **Boundary Percentage:** $(\text{Boundaries Conceded} / \text{Legal Balls}) \times 100$, where Boundaries Conceded $= \text{Fours} + \text{Sixes}$
- **Economy Differential ($\Delta$):** `high_economy_rate - low_mod_economy_rate` (negative delta indicates bowler becomes more economical under pressure).

### 4.2 Top 10 Bowlers Overall (by Total Wickets)
```
+--------------------+---------+---------+-------------+---------+----------+------------+---------+------------+----------+
| Player Name        | Matches | Wickets | Legal Balls | Economy | Average  | High Wkts  | High LB | High Econ  | Low Econ | Econ Del |
+--------------------+---------+---------+-------------+---------+----------+------------+---------+------------+----------+
| Arshdeep Singh     |   143   |   187   |    3132     |  9.10   |  23.82   |     21     |   427   |    9.40    |   9.05   |  +0.35   |
| Rashid Khan        |   118   |   149   |    2672     |  7.37   |  22.25   |     15     |   254   |    7.91    |   7.32   |  +0.59   |
| Varun Chakravarthy |    94   |   134   |    2099     |  7.96   |  21.94   |     10     |   267   |    9.71    |   7.71   |  +2.00   |
| Wanindu Hasaranga  |    87   |   129   |    1950     |  7.79   |  20.21   |     13     |   198   |    6.82    |   7.90   |  -1.08   |
| Yuzvendra Chahal   |    96   |   122   |    2114     |  8.63   |  25.43   |      9     |   186   |    9.26    |   8.57   |  +0.69   |
| Ravi Bishnoi       |   106   |   119   |    2285     |  8.30   |  26.96   |     19     |   231   |    9.06    |   8.22   |  +0.84   |
| Kuldeep Yadav      |    87   |   117   |    1884     |  7.96   |  21.97   |     10     |   172   |    8.48    |   7.91   |  +0.57   |
| Axar Patel         |   132   |   116   |    2610     |  7.87   |  29.98   |     20     |   303   |    7.66    |   7.90   |  -0.24   |
| Bhuvneshwar Kumar  |    99   |   113   |    2177     |  8.24   |  26.47   |      6     |   299   |    8.67    |   8.18   |  +0.49   |
| Jason Holder       |    87   |   108   |    1914     |  8.93   |  26.06   |     14     |   180   |    8.93    |   8.93   |   0.00   |
+--------------------+---------+---------+-------------+---------+----------+------------+---------+------------+----------+
```

### 4.3 Top 10 Bowlers by High-Pressure Wickets (Min. 100 Legal Balls)
```
+-------------------+-----------+------------+-----------+------------+------------+-----------+
| Player Name       | High Wkts | High Balls | High Econ | High Dot % | Low/Mod Ec | Econ Del  |
+-------------------+-----------+------------+-----------+------------+------------+-----------+
| Arshdeep Singh    |    21     |    427     |   9.40    |   44.26%   |    9.05    |   +0.35   |
| Axar Patel        |    20     |    303     |   7.66    |   35.97%   |    7.90    |   -0.24   |
| Mohammed Siraj    |    20     |    330     |   8.82    |   47.88%   |    8.73    |   +0.09   |
| Ravi Bishnoi      |    19     |    231     |   9.06    |   38.10%   |    8.22    |   +0.84   |
| Jofra Archer      |    18     |    259     |   9.61    |   44.40%   |    8.76    |   +0.85   |
| Rashid Khan       |    15     |    254     |   7.91    |   36.22%   |    7.32    |   +0.59   |
| Jason Holder      |    14     |    180     |   8.93    |   37.78%   |    8.93    |    0.00   |
| Wanindu Hasaranga |    13     |    198     |   6.82    |   39.90%   |    7.90    |   -1.08   |
| Kagiso Rabada     |    13     |    279     |   8.99    |   48.39%   |    9.31    |   -0.32   |
| Jacob Duffy       |    13     |    127     |  10.02    |   42.52%   |    8.48    |   +1.54   |
+-------------------+-----------+------------+-----------+------------+------------+-----------+
```

> [!NOTE]
> **Elite Pressure Findings (Bowling):**
> - **Wanindu Hasaranga** tightens up under pressure: Economy drops from **$7.90$** in low/moderate pressure to **$6.82$** in high pressure ($-1.08$ delta), claiming 13 wickets across 198 high-pressure balls.
> - **Axar Patel** shows exceptional dual all-round value: With the ball, his economy improves to **$7.66$** (20 high-pressure wickets); with the bat, he leads all players in high-pressure runs (401 runs).
> - **Kagiso Rabada** improves economy from **$9.31$** to **$8.99$** with an extraordinary **$48.39\%$** dot-ball rate under peak pressure.
> - **Mohammed Siraj** claims 20 wickets under high pressure with an elite **$47.88\%$** dot-ball rate.

---

## 5. The 6 Exhaustive Validation Checks (Part 7 Audit)

### Check 1: Conservation of Batter Runs and Balls Faced
```python
assert eval_batter_runs == source_batter_runs  # 252,658 == 252,658
assert (low_runs + high_runs) == source_batter_runs  # 226,053 + 26,605 == 252,658
assert eval_balls_faced == source_balls_faced  # 180,839 == 180,839
assert (low_bf + high_bf) == source_balls_faced  # 157,511 + 23,328 == 180,839
```
*Result:* **PASS.** Total runs and balls faced match source data to the exact unit across all 816 batters.

### Check 2: Conservation of Bowler Runs Conceded and Legal Balls
```python
assert eval_bowler_rc == source_bowler_rc  # 260,714 == 260,714
assert (low_rc + high_rc) == source_bowler_rc  # 230,696 + 30,018 == 260,714
assert eval_legal_balls == source_legal_balls  # 180,041 == 180,041
assert (low_lb + high_lb) == source_legal_balls  # 160,157 + 19,884 == 180,041
```
*Result:* **PASS.** Total runs conceded and legal balls bowled match source data exactly across all 589 bowlers.

### Check 3: Bowler Wicket Attribution Precision
Total dismissals in the clean dataset: **10,103**.
- Bowler wickets (`Caught`, `Bowled`, `LBW`, `Stump`, `Hit Wicket`): **9,542 wickets** (94.45%).
- Non-bowler wickets (`RunOut` = 554, `Retire Out` = 5, `Obstructing Field` = 2): **561 wickets** (5.55%).
```python
assert eval_bowler_wickets == source_bowler_wickets  # 9,542 == 9,542
assert (low_wk + high_wk) == source_bowler_wickets  # 8,584 + 958 == 9,542
```
*Result:* **PASS.** Zero run-outs or non-bowler wickets were credited to bowlers.

### Check 4: Zero Duplicate Player Records
- `batters_df['player_id'].nunique() == len(batters_df) == 816`
- `bowlers_df['player_id'].nunique() == len(bowlers_df) == 589`
*Result:* **PASS.** Every player appears exactly once in each respective table.

### Check 5: Zero Excluded Deliveries Included
- Source rows before cleaning: 188,330
- Excluded second-innings tail rows (`runs_required <= 0`): 233
- Evaluated clean rows: 188,097
*Result:* **PASS.** All 233 target-reached/ghost deliveries were filtered prior to aggregation.

### Check 6: Target-Understated Flags Preserved
The 4,177 live second-innings deliveries in the 38 flagged matches are tracked in the player tables as `target_understated_balls_faced` and `target_understated_legal_balls`.
*Result:* **PASS.**

---

## 6. Preparation for Step 6: Ranking Models & Bayesian Shrinkage

The performance metrics generated in Step 5 provide the foundation for Step 6:
1. **Sample Size Variation:** Player high-pressure opportunities vary widely (e.g. Axar Patel faced 321 high-pressure balls; Shubman Gill faced 29). Step 6 will apply **Bayesian shrinkage / Empirical Bayes weighting** towards league baselines to avoid small-sample distortion.
2. **Phase Normalization:** Powerplay, Middle, and Death overs have inherently different baseline run rates (e.g. Death Over SR is naturally higher). Normalizing by phase will ensure middle-order and top-order players are evaluated equitably.
3. **Dual Metric Balancing:** For batters, balancing Strike Rate against Dismissal Rate under pressure; for bowlers, balancing Economy Rate against Wicket Strike Rate under pressure.
