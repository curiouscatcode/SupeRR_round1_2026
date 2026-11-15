# Step 5 — Implementation Report: Player-Level Pressure Performance Dataset

**Project Target:** `experiments/pressure_definition_v1/`  
**Step:** Step 5 — Player-Level Pressure Performance Dataset  
**Primary Deliverables:**  
- `outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet` (and `.csv`)  
- `outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet` (and `.csv`)  
- `outputs/step_5_player_level_dataset/player_mapping_audit.csv`  
- `outputs/step_5_player_level_dataset/data_quality_report.md`  
- `outputs/step_5_player_level_dataset/validation_results.json`  
**Execution Script:** `src/step_5_player_dataset/build_player_datasets.py`  
**Validation Suite:** `src/step_5_player_dataset/validate_step_5.py`  
**Date:** November 2026  
**Implementation Verdict:** **COMPLETE & FULLY VERIFIED (ALL 9 CHECKS PASSED)**

---

## 1. Executive Summary & Objective Alignment

### 1.1 Objective Alignment
The core objective of the project remains unchanged:
$$\mathbf{Identify \; the \; Most \; Reliable \; Players \; Under \; Pressure}$$

Following the successful implementation (`Step 4.3`) and independent audits (`Step 4.3.1`, `Step 4.3.2`) of the delivery pressure pipeline, **Step 5** provides the vital data engineering bridge linking delivery-level pressure measurements to individual player performance. 

Step 5 is strictly a **data preparation and integrity step**. In accordance with instructions:
- **No reliability formulas were designed.**
- **No player rankings or top-10 lists were generated.**
- **The pressure methodology was not modified.**
- **Zero production code or Step 4 pipeline outputs were altered.**

### 1.2 Summary of Deliverables Produced
Two clean, production-grade player-delivery datasets were constructed in `outputs/step_5_player_level_dataset/`:
1. `batting_pressure_deliveries.parquet` ($186,780$ rows, $9.70$ MB; CSV: $51.81$ MB):
   Connects each facing striker to the batting pressure they experienced, capturing batter runs, boundary production, dismissals, and official balls faced.
2. `bowling_pressure_deliveries.parquet` ($186,780$ rows, $9.76$ MB; CSV: $55.31$ MB):
   Connects each delivering bowler to the bowling pressure they imposed or experienced, capturing bowler runs conceded, bowler-credited wickets, dot balls, boundary concessions, and legal delivery counts.
3. `player_mapping_audit.csv` ($883$ unique players, $292.87$ KB):
   Audits all 883 participating players across competition team rosters and match playing elevens.

---

## 2. Dataset Architecture & Attribution Rules

### 2.1 Striker vs. Non-Striker Attribution Rules
A common failure mode in sports analytics pipelines is incorrectly attributing a delivery's batting performance or dismissal to the non-striker. Step 5 enforces strict attribution boundaries:

1. **Pressure Attribution:**
   - Batting pressure $P_{\text{bat}} = \sqrt{T_{\text{bat}} \times L_{\text{norm}}}$ is experienced by the **facing batter (`striker_id`)** at $t^-$. It is not assigned to the non-striker.
2. **Batter Runs vs. Team Runs:**
   - `batter_runs` records runs scored off the bat by the striker ($0, 1, 2, 3, 4, 6$).
   - `team_runs_added` records the total increment to the team score, including extras. Byes, leg-byes, and wide penalties are not credited to the batter.
3. **Dismissal Attribution:**
   - `is_striker_dismissed`: Evaluated as `True` if and only if `is_wicket == True` AND `dismissed_player_id == striker_id`. Across 186,780 deliveries, exactly **$9,768$** striker dismissals occurred.
   - `is_non_striker_dismissed`: Evaluated as `True` if `is_wicket == True` AND `dismissed_player_id == non_striker_id`. Exactly **$251$** deliveries resulted in the non-striker being run out or retired. The striker is strictly **NOT** marked as dismissed on these balls.
4. **Official Balls Faced:**
   - Wides ($7,190$ deliveries) do not count as a ball faced in batting records (`is_batter_ball_faced = False`). All other deliveries ($179,590$ deliveries, including no-balls faced) have `is_batter_ball_faced = True`.

### 2.2 Bowler vs. Fielding Attribution Rules
Standard cricket scoring conventions dictate that bowlers are only debited for runs and credited for wickets within their control:

1. **Runs Conceded Convention:**
   - `bowler_runs_conceded` debits runs off the bat, wide penalties, and no-ball penalties.
   - Byes ($480$ deliveries) and leg-byes ($2,540$ deliveries) are fielding events and are **NOT** charged to the bowler.
   - Across the cohort, bowlers conceded **$258,974$** runs, compared to total team runs of **$262,072$** (a verified difference of $3,098$ bye/leg-bye runs).
2. **Bowler-Credit Wickets vs. Fielding Dismissals:**
   - `is_bowler_wicket` is credited strictly for standard bowler dismissals: `Caught`, `Bowled`, `LBW`, `Stump`, and `Hit Wicket`. Exactly **$9,463$** wickets belong to the bowler.
   - Non-bowler dismissals (`RunOut`, `Retire Out`, `Obstructing the field`) are flagged separately in `is_other_dismissal`. Exactly **$557$** non-bowler dismissals occurred.
3. **Legal Deliveries:**
   - `is_legal_ball` is `True` for valid deliveries ($178,798$ balls) and `False` for wides ($7,190$) and no-balls ($792$). Only legal deliveries count toward a bowler's completed overs.

---

## 3. Data Dictionary

### 3.1 Batting Pressure Deliveries Schema

| Column Name | Data Type | Nullable | Valid Values / Units | Description |
| :--- | :---: | :---: | :---: | :--- |
| `match_id` | `int64` | No | $[13511, 55088]$ | Primary match identifier (782 matches). |
| `innings` | `int64` | No | $1, 2$ | Innings indicator. |
| `overid` | `int64` | No | $[1, 20]$ | 1-indexed over number. |
| `over_ball_num` | `int64` | No | $[1, 11]$ | Ball number within the over. |
| `innings_ball_num` | `int64` | No | $[1, 130]$ | Sequence delivery counter within innings. |
| `batting_team_id` | `int64` | No | $[1, 50]$ | Team ID of batting side. |
| `bowling_team_id` | `int64` | No | $[1, 50]$ | Team ID of bowling side. |
| `striker_id` | `int64` | No | $[1, 99999]$ | Facing batter player ID (816 unique batters). |
| `striker_name` | `string` | No | Text | Facing batter name. |
| `non_striker_id` | `int64` | No | $[1, 99999]$ | Non-facing batter player ID. |
| `non_striker_name` | `string` | No | Text | Non-facing batter name. |
| `bowler_id` | `int64` | No | $[1, 99999]$ | Bowler player ID. |
| `bowler_name` | `string` | No | Text | Bowler name. |
| `phase` | `string` | No | `'PP'`, `'Middle'`, `'Death'` | Match phase segment. |
| `score_before` | `int64` | No | $[0, 260]$ | Runs scored before delivery. |
| `wickets_before` | `int64` | No | $[0, 9]$ | Wickets lost before delivery. |
| `W_t` | `int64` | No | $[0, 9]$ | Standardized wickets lost before ball. |
| `W_rem` | `int64` | No | $[1, 10]$ | Wickets in hand ($10 - W_t$). |
| `legal_balls_before`| `int64` | No | $[0, 119]$ | Legal balls bowled before delivery. |
| `balls_remaining` | `int64` | No | $[1, 120]$ | Legal balls remaining ($120 - L_t$). |
| `current_run_rate` | `float64` | No | $[0.00, 36.00]$ | Run rate at $t^-$. |
| `runs_required` | `float64` | Yes (Inn 1) | $[1.00, 260.00]$ | Runs required to win (Innings 2 only). |
| `required_run_rate`| `float64` | Yes (Inn 1) | $[0.00, 36.00]$ | Required run rate (Innings 2 only). |
| `striker_balls_faced_before`| `int64`| No | $[0, 75]$ | Cumulative balls faced by striker in innings. |
| `venue_id` | `int64` | No | $[1, 200]$ | Venue identifier. |
| `pressure_batting` | `float64` | No | $[0.00, 99.98]$ | **Approved Step 4.3 Batting Pressure**. |
| `task_difficulty_bat`| `float64`| No | $[0.01, 99.98]$ | Batting Task Difficulty ($T$). |
| `normalized_consequence_L`| `float64`| No | $[0.00, 100.00]$ | Normalized Match Consequence ($L_{\text{norm}}$). |
| `raw_consequence_L`| `float64` | No | $[0.00000, 0.05000]$ | Raw Expected Consequence ($L$). |
| `pre_delivery_wp` | `float64` | No | $[0.0000, 1.0000]$ | Pre-delivery Win Probability. |
| `batter_runs` | `int64` | No | $0, 1, 2, 3, 4, 6$ | Runs scored off bat by striker. |
| `team_runs_added` | `int64` | No | $[0, 7]$ | Total runs added to score on ball. |
| `is_four` | `bool` | No | `True`, `False` | Boundary four hit by striker. |
| `is_six` | `bool` | No | `True`, `False` | Boundary six hit by striker. |
| `is_boundary` | `bool` | No | `True`, `False` | Boundary four or six hit by striker. |
| `is_legal_ball` | `bool` | No | `True`, `False` | True if legal delivery. |
| `is_batter_ball_faced`| `bool` | No | `True`, `False` | True if ball faced (all except wide). |
| `is_dot_ball_faced` | `bool` | No | `True`, `False` | True if ball faced and 0 runs scored. |
| `extras_type` | `string` | Yes | `'wide'`, `'Overstep'`, etc. | Extras category or `NaN`. |
| `extras1_runs` | `int64` | No | $[0, 5]$ | Primary extra runs. |
| `extras_2_runs` | `int64` | No | $[0, 5]$ | Secondary extra runs. |
| `is_wicket` | `bool` | No | `True`, `False` | True if wicket fell on ball. |
| `dismissal_type` | `string` | Yes | `'Caught'`, `'Bowled'`, etc.| Dismissal method or `NaN`. |
| `dismissal_type_id`| `float64` | Yes | $[1.0, 10.0]$ | Numeric dismissal ID. |
| `dismissed_player_id`| `float64`| Yes | $[1.0, 99999.0]$ | Player ID of dismissed batter. |
| `is_striker_dismissed`| `bool` | No | `True`, `False` | **True strictly when striker is dismissed.** |
| `is_non_striker_dismissed`| `bool` | No | `True`, `False` | **True strictly when non-striker is dismissed.** |

---

### 3.2 Bowling Pressure Deliveries Schema

| Column Name | Data Type | Nullable | Valid Values / Units | Description |
| :--- | :---: | :---: | :---: | :--- |
| `match_id` | `int64` | No | $[13511, 55088]$ | Primary match identifier. |
| `innings` | `int64` | No | $1, 2$ | Innings indicator. |
| `overid` | `int64` | No | $[1, 20]$ | 1-indexed over number. |
| `over_ball_num` | `int64` | No | $[1, 11]$ | Ball number within the over. |
| `innings_ball_num` | `int64` | No | $[1, 130]$ | Sequence delivery counter within innings. |
| `bowling_team_id` | `int64` | No | $[1, 50]$ | Team ID of bowling side. |
| `batting_team_id` | `int64` | No | $[1, 50]$ | Team ID of batting side. |
| `bowler_id` | `int64` | No | $[1, 99999]$ | Delivering bowler ID (589 unique bowlers). |
| `bowler_name` | `string` | No | Text | Delivering bowler name. |
| `striker_id` | `int64` | No | $[1, 99999]$ | Facing striker ID. |
| `striker_name` | `string` | No | Text | Facing striker name. |
| `non_striker_id` | `int64` | No | $[1, 99999]$ | Non-striker ID. |
| `non_striker_name` | `string` | No | Text | Non-striker name. |
| `phase` | `string` | No | `'PP'`, `'Middle'`, `'Death'` | Match phase segment. |
| `score_before` | `int64` | No | $[0, 260]$ | Runs scored before delivery. |
| `wickets_before` | `int64` | No | $[0, 9]$ | Opponent wickets lost before delivery. |
| `W_t` | `int64` | No | $[0, 9]$ | Opponent wickets lost. |
| `W_rem` | `int64` | No | $[1, 10]$ | Opponent wickets in hand. |
| `legal_balls_before`| `int64` | No | $[0, 119]$ | Legal balls bowled before delivery. |
| `balls_remaining` | `int64` | No | $[1, 120]$ | Legal balls remaining. |
| `current_run_rate` | `float64` | No | $[0.00, 36.00]$ | Opponent run rate at $t^-$. |
| `runs_required` | `float64` | Yes (Inn 1) | $[1.00, 260.00]$ | Opponent runs required (Innings 2 only). |
| `required_run_rate`| `float64` | Yes (Inn 1) | $[0.00, 36.00]$ | Opponent required run rate (Innings 2 only). |
| `bowler_legal_balls_in_spell_before`| `int64`| No | $[0, 24]$ | Cumulative legal balls bowled by bowler in spell. |
| `venue_id` | `int64` | No | $[1, 200]$ | Venue identifier. |
| `pressure_bowling` | `float64` | No | $[0.00, 99.88]$ | **Approved Step 4.3 Bowling Pressure**. |
| `task_difficulty_bowl`| `float64`| No | $[0.01, 99.98]$ | Bowling Task Difficulty ($T$). |
| `normalized_consequence_L`| `float64`| No | $[0.00, 100.00]$ | Normalized Match Consequence ($L_{\text{norm}}$). |
| `raw_consequence_L`| `float64` | No | $[0.00000, 0.05000]$ | Raw Expected Consequence ($L$). |
| `pre_delivery_wp` | `float64` | No | $[0.0000, 1.0000]$ | Pre-delivery Win Probability. |
| `bowler_runs_conceded`| `int64` | No | $[0, 7]$ | **Runs charged to bowler** (byes/leg-byes excluded). |
| `team_runs_added` | `int64` | No | $[0, 7]$ | Total runs added to score on ball. |
| `is_bowler_wicket`| `bool` | No | `True`, `False` | **True strictly for standard bowler wickets.** |
| `is_other_dismissal`| `bool` | No | `True`, `False` | **True for run-outs, retire outs, obstruction.** |
| `is_wicket` | `bool` | No | `True`, `False` | True if any wicket fell on delivery. |
| `dismissal_type` | `string` | Yes | Text | Dismissal method or `NaN`. |
| `dismissal_type_id`| `float64` | Yes | $[1.0, 10.0]$ | Numeric dismissal ID. |
| `dismissed_player_id`| `float64`| Yes | $[1.0, 99999.0]$ | Dismissed player ID. |
| `is_bowler_dot_ball`| `bool` | No | `True`, `False` | True if bowler conceded 0 runs. |
| `is_boundary_conceded`| `bool` | No | `True`, `False` | Boundary four or six conceded off bat. |
| `is_four_conceded`| `bool` | No | `True`, `False` | Boundary four conceded. |
| `is_six_conceded` | `bool` | No | `True`, `False` | Boundary six conceded. |
| `is_legal_ball` | `bool` | No | `True`, `False` | True if legal delivery. |
| `extras_type` | `string` | Yes | Text | Extras category or `NaN`. |
| `extras1_runs` | `int64` | No | $[0, 5]$ | Primary extra runs. |
| `extras_2_runs` | `int64` | No | $[0, 5]$ | Secondary extra runs. |
| `is_wide` | `bool` | No | `True`, `False` | Delivery was a wide. |
| `is_no_ball` | `bool` | No | `True`, `False` | Delivery was a no-ball. |
| `is_bye` | `bool` | No | `True`, `False` | Delivery resulted in byes. |
| `is_leg_bye` | `bool` | No | `True`, `False` | Delivery resulted in leg-byes. |

---

## 4. Player Mapping Audit Summary

The player mapping audit was generated as `outputs/step_5_player_level_dataset/player_mapping_audit.csv`. It aggregates every player's participation across the entire cohort:

### 4.1 Cohort Player Aggregates
- **Total Unique Participating Players:** **`883`**
- **Mapped in `competition_team_player_mapping.csv`:** **`883 / 883 (100.0%)`**
- **Mapped in `playing_eleven.csv`:** **`883 / 883 (100.0%)`**
- **Discrepancies in Player Names:** **`0`**

### 4.2 Top Participating Batters (by Balls Faced)
*(Illustrative inspection of aggregated totals in `player_mapping_audit.csv`)*

| Player ID | Player Name | Batting Deliveries | Official Balls Faced | Total Runs | Fours | Sixes | Dismissals | Official Strike Rate |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `1407` | Virat Kohli | 2,752 | 2,674 | 3,694 | 338 | 125 | 71 | 138.15 |
| `78` | Shikhar Dhawan | 2,427 | 2,367 | 3,115 | 358 | 66 | 82 | 131.60 |
| `380` | Faf du Plessis | 2,410 | 2,333 | 3,246 | 299 | 128 | 79 | 139.13 |
| `1331` | Jos Buttler | 2,374 | 2,298 | 3,365 | 323 | 161 | 75 | 146.43 |
| `1726` | KL Rahul | 2,362 | 2,298 | 3,091 | 258 | 114 | 64 | 134.51 |
| `43` | David Warner | 2,295 | 2,229 | 3,044 | 309 | 89 | 74 | 136.56 |

### 4.3 Top Participating Bowlers (by Legal Balls Bowled)
*(Illustrative inspection of aggregated totals in `player_mapping_audit.csv`)*

| Player ID | Player Name | Total Deliveries | Legal Deliveries | Runs Conceded | Bowler Wickets | Dot Balls | Official Economy Rate |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `282` | Rashid Khan | 2,746 | 2,683 | 3,251 | 148 | 1,027 | 7.27 |
| `3720` | Harshal Patel | 2,408 | 2,274 | 3,294 | 142 | 818 | 8.69 |
| `244` | Yuzvendra Chahal | 2,378 | 2,323 | 3,165 | 139 | 785 | 8.18 |
| `3715` | Avesh Khan | 2,192 | 2,075 | 3,040 | 108 | 788 | 8.79 |
| `276` | Trent Boult | 2,139 | 2,072 | 2,829 | 108 | 913 | 8.19 |
| `216` | Mohammed Shami | 2,082 | 2,019 | 2,836 | 115 | 874 | 8.43 |

---

## 5. Formal Validation Results

The Step 5 validation suite (`validate_step_5.py`) executed 9 automated checks on the final datasets, saved to `outputs/step_5_player_level_dataset/validation_results.json`:

```json
{
  "verdict": "PASS",
  "checks": {
    "Check 1: Batting Pressure Validity": "PASS",
    "Check 2: Bowling Pressure Validity": "PASS",
    "Check 3: Player Metadata Coverage": "PASS",
    "Check 4: Zero Duplicate Records": "PASS",
    "Check 5: Match & Innings Consistency": "PASS",
    "Check 6: Exclusions Maintained": "PASS",
    "Check 7: Bit-for-Bit Pressure Identity": "PASS",
    "Check 8: Source Reconciliation": "PASS",
    "Check 9: Documented Missing Values": "PASS"
  }
}
```

---

## 6. Readiness Assessment for Step 6

With Step 5 complete and certified:
1. Every delivery in the 186,780 cohort now possesses unambiguous player attribution for both batter and bowler.
2. The pressure values attached to each record are guaranteed bit-for-bit identical to the approved Step 4.3 calculations.
3. Traditional performance indicators (batter runs, official balls faced, bowler runs conceded, legal deliveries, dot balls, bowler wickets) are completely separated from fielding events and extras.
4. The datasets provide the exact foundation required to design and evaluate player reliability formulas under pressure in Step 6.

$$\mathbf{STEP \; 5 \; VERDICT: \quad CERTIFIED \; COMPLETE}$$

---
*Report certified by Antigravity Autonomous Data Architecture Team.*
