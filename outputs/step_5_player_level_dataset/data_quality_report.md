# Step 5 — Data Quality & Integrity Report

**Artifact Target:** `outputs/step_5_player_level_dataset/`  
**Datasets Audited:**  
- `batting_pressure_deliveries.parquet` (and `.csv`)  
- `bowling_pressure_deliveries.parquet` (and `.csv`)  
- `player_mapping_audit.csv`  
**Reference Pipelines:** `outputs/step_4_pressure_pipeline/delivery_pressure_v3.parquet`, `clean_cohort_deliveries.parquet`, `data/ball_by_ball.csv`  
**Date:** November 2026  
**Data Quality Verdict:** **CERTIFIED — ALL 9 INTEGRITY CHECKS PASSED (100% RECONCILED)**

---

## 1. Executive Summary & Quality Scorecard

This data quality report provides an exhaustive audit of the Step 5 player-level delivery datasets. Step 5 constructed two dedicated delivery-level datasets linking individual batting and bowling performances to the approved Step 4.3 pressure measurements (`delivery_pressure_v3.parquet`).

The audit confirms that all 186,780 deliveries across 782 matches map 1-to-1 to their approved pressure observations, maintain strict striker vs. non-striker attribution, preserve exact bowler vs. fielding wicket separation, and reconcile completely against historical match totals.

### Data Quality Scorecard

| Check # | Validation Focus | Required Invariant | Observed Measurement | Result |
| :---: | :--- | :--- | :--- | :---: |
| **1** | Batting Pressure Validity | 186,780 valid rows, 0 null/inf, bounded in $[0, 100]$ | 186,780 rows, 0 null, 0 inf, range: $[0.00, 99.98]$ | **PASS** |
| **2** | Bowling Pressure Validity | 186,780 valid rows, 0 null/inf, bounded in $[0, 100]$ | 186,780 rows, 0 null, 0 inf, range: $[0.00, 99.88]$ | **PASS** |
| **3** | Player Metadata Coverage | 100% player IDs mapped to competition & playing-11 | 883 of 883 players mapped ($100.0\%$), 0 unmapped | **PASS** |
| **4** | Duplicate Record Check | Zero duplicate `(match_id, innings, ball)` records | 0 duplicate delivery keys in batting or bowling | **PASS** |
| **5** | Match/Innings Alignment | Keys bit-for-bit identical with Step 4.3 Parquet | $100.0\%$ bit-for-bit key alignment | **PASS** |
| **6** | Cohort Exclusions Maintained | 0 rows from DLS, shortened, or dead-tail matches | 0 excluded match rows, 0 dead-tail deliveries | **PASS** |
| **7** | Bit-for-Bit Pressure Identity | Pressure, $T$, $L_{\text{norm}}$, $L$, $\text{WP}$ identical to v3 | Max absolute deviation: $0.00 \times 10^0$ | **PASS** |
| **8** | Source Data Reconciliation | Exact match on runs, wickets, extras, legal balls | All metrics match cohort and match totals | **PASS** |
| **9** | Missing Value Audit | All NaNs documented; 0 unexpected null values | All nulls categorized; 1 source anomaly documented | **PASS** |

---

## 2. Source-to-Output Column Lineage & Mapping

Every field in the Step 5 player-level datasets has a deterministic lineage traced back to `delivery_pressure_v3.parquet`, `clean_cohort_deliveries.parquet`, and raw match records:

### 2.1 Batting Pressure Deliveries Lineage

| Output Column | Source Origin | Data Type | Transformation & Validation Logic |
| :--- | :--- | :---: | :--- |
| `match_id` | `v3['match_id']` | `int64` | Primary match key (782 pure 20-over matches). |
| `innings` | `v3['innings']` | `int64` | Innings sequence (1 = Batting 1st, 2 = Chasing). |
| `overid` | `v3['overid']` | `int64` | 1-indexed over number (1 to 20). |
| `over_ball_num` | `v3['over_ball_num']` | `int64` | Sequence of ball within over (1 to 11 including re-bowled balls). |
| `innings_ball_num` | `v3['innings_ball_num']` | `int64` | Cumulative delivery counter within innings (1 to 130). |
| `batting_team_id` | `v3['batting_team_id']` | `int64` | ID of batting team. |
| `bowling_team_id` | `v3['bowling_team_id']` | `int64` | ID of bowling team. |
| `striker_id` | `v3['striker_id']` | `int64` | Facing batter ID (recipient of batting pressure). |
| `striker_name` | `v3['striker_name']` | `str` | Facing batter name. |
| `non_striker_id` | `v3['non_striker_id']` | `int64` | Non-facing batter ID. |
| `non_striker_name` | `v3['non_striker_name']` | `str` | Non-facing batter name. |
| `bowler_id` | `v3['bowler_id']` | `int64` | Opposing bowler ID. |
| `bowler_name` | `v3['bowler_name']` | `str` | Opposing bowler name. |
| `phase` | `v3['phase']` | `str` | Match segment: `'PP'`, `'Middle'`, `'Death'`. |
| `score_before` | `v3['score_before']` | `int64` | Cumulative team score at $t^-$. |
| `wickets_before` | `v3['wickets_before']` | `int64` | Wickets lost at $t^-$ ($W_t \in [0, 9]$). |
| `W_t` | `v3['W_t']` | `int64` | Standardized wickets lost before ball. |
| `W_rem` | `v3['W_rem']` | `int64` | Wickets in hand ($10 - W_t \in [1, 10]$). |
| `legal_balls_before`| `v3['legal_balls_before']`| `int64` | Legal deliveries bowled prior to delivery ($L_t \in [0, 119]$). |
| `balls_remaining` | `v3['balls_remaining']` | `int64` | Legal deliveries remaining ($120 - L_t \in [1, 120]$). |
| `current_run_rate` | `v3['current_run_rate']` | `float64` | Observed team CRR at $t^-$. |
| `runs_required` | `v3['runs_required']` | `float64` | Runs required to win (Innings 2 only; NaN in Innings 1). |
| `required_run_rate`| `v3['required_run_rate']`| `float64` | Required run rate per 6 balls (Innings 2 only). |
| `striker_balls_faced_before` | `cohort['striker_balls_faced_before']` | `int64` | Batter's cumulative balls faced in innings prior to this ball. |
| `venue_id` | `cohort['venue_id']` | `int64` | Match venue ID. |
| `pressure_batting` | `v3['pressure_batting']`| `float64` | **Approved Step 4.3 Batting Pressure** ($P = \sqrt{T_{\text{bat}} \times L_{\text{norm}}}$). |
| `task_difficulty_bat`| `v3['task_difficulty_bat']`| `float64` | Batting Task Difficulty ($T_{\text{B1}}$ or $T_{\text{B2}}$). |
| `normalized_consequence_L` | `v3['normalized_consequence_L']` | `float64` | ECDF-normalized expected match consequence ($L_{\text{norm}} \in [0, 100]$). |
| `raw_consequence_L` | `v3['raw_consequence_L']` | `float64` | Unnormalized expected match swing ($L_1$ or $L_2$). |
| `pre_delivery_wp` | `v3['pre_delivery_wp']` | `float64` | Win probability at $t^-$. |
| `batter_runs` | `v3['runs']` | `int64` | Runs credited strictly to striker off bat (0, 1, 2, 3, 4, 6). |
| `team_runs_added` | `cohort['team_runs_added']` | `int64` | Total runs added to team score on delivery. |
| `is_four` | `v3['is_four']` | `bool` | True if boundary four off bat. |
| `is_six` | `v3['is_six']` | `bool` | True if boundary six off bat. |
| `is_boundary` | `is_four \| is_six` | `bool` | True if boundary four or six off bat. |
| `is_legal_ball` | `v3['is_legal_ball']` | `bool` | True if legal delivery (False for wide/no-ball). |
| `is_batter_ball_faced` | `cohort['is_batter_ball_faced']` | `bool` | True for all balls faced except wide (official BF). |
| `is_dot_ball_faced`| `is_bf & (runs == 0)`| `bool` | True if batter faced ball and scored 0 runs. |
| `extras_type` | `cohort['extras_type']` | `str/NaN` | `'wide'`, `'Overstep'`, `'byes'`, `'legbyes'`, `'other'`, or NaN. |
| `extras1_runs` | `cohort['extras1_runs']` | `int64` | Penalty or primary extra runs. |
| `extras_2_runs` | `cohort['extras_2_runs']` | `int64` | Ancillary extra runs (e.g. overthrows). |
| `is_wicket` | `cohort['is_wicket']` | `bool` | True if a dismissal occurred on this delivery. |
| `dismissal_type` | `cohort['dismissal_type']` | `str/NaN` | Specific dismissal method. |
| `dismissal_type_id`| `cohort['dismissal_type_id']`| `float64` | Numeric dismissal ID. |
| `dismissed_player_id` | `cohort['dismissed_player_id']` | `float64` | ID of dismissed player. |
| `is_striker_dismissed` | `is_w & (d_pid == s_id)` | `bool` | **True strictly when the striker is dismissed.** |
| `is_non_striker_dismissed` | `is_w & (d_pid == ns_id)` | `bool` | **True strictly when the non-striker is dismissed.** |

---

### 2.2 Bowling Pressure Deliveries Lineage

| Output Column | Source Origin | Data Type | Transformation & Validation Logic |
| :--- | :--- | :---: | :--- |
| `match_id` | `v3['match_id']` | `int64` | Primary match key. |
| `innings` | `v3['innings']` | `int64` | Innings sequence. |
| `overid` | `v3['overid']` | `int64` | 1-indexed over number. |
| `over_ball_num` | `v3['over_ball_num']` | `int64` | Ball number within over. |
| `innings_ball_num` | `v3['innings_ball_num']` | `int64` | Ball number within innings. |
| `bowling_team_id` | `v3['bowling_team_id']` | `int64` | ID of bowling team. |
| `batting_team_id` | `v3['batting_team_id']` | `int64` | ID of batting team. |
| `bowler_id` | `v3['bowler_id']` | `int64` | Delivering bowler ID. |
| `bowler_name` | `v3['bowler_name']` | `str` | Delivering bowler name. |
| `striker_id` | `v3['striker_id']` | `int64` | Opposing striker ID. |
| `striker_name` | `v3['striker_name']` | `str` | Opposing striker name. |
| `non_striker_id` | `v3['non_striker_id']` | `int64` | Opposing non-striker ID. |
| `non_striker_name` | `v3['non_striker_name']` | `str` | Opposing non-striker name. |
| `phase` | `v3['phase']` | `str` | Match segment (`PP`, `Middle`, `Death`). |
| `score_before` | `v3['score_before']` | `int64` | Cumulative team score at $t^-$. |
| `wickets_before` | `v3['wickets_before']` | `int64` | Opponent wickets lost at $t^-$. |
| `W_t` | `v3['W_t']` | `int64` | Opponent wickets lost. |
| `W_rem` | `v3['W_rem']` | `int64` | Opponent wickets in hand ($10 - W_t$). |
| `legal_balls_before`| `v3['legal_balls_before']`| `int64` | Legal deliveries bowled prior to delivery. |
| `balls_remaining` | `v3['balls_remaining']` | `int64` | Legal deliveries remaining. |
| `current_run_rate` | `v3['current_run_rate']` | `float64` | Conceded CRR at $t^-$. |
| `runs_required` | `v3['runs_required']` | `float64` | Opponent target remaining (Innings 2 only). |
| `required_run_rate`| `v3['required_run_rate']`| `float64` | Opponent RRR (Innings 2 only). |
| `bowler_legal_balls_in_spell_before` | `cohort['bowler_legal_balls_in_spell_before']` | `int64` | Bowler's spell count prior to this delivery. |
| `venue_id` | `cohort['venue_id']` | `int64` | Match venue ID. |
| `pressure_bowling` | `v3['pressure_bowling']`| `float64` | **Approved Step 4.3 Bowling Pressure** ($P = \sqrt{T_{\text{bowl}} \times L_{\text{norm}}}$). |
| `task_difficulty_bowl`| `v3['task_difficulty_bowl']`| `float64` | Bowling Task Difficulty ($T_{\text{BO1}}$ or $T_{\text{BO2}}$). |
| `normalized_consequence_L` | `v3['normalized_consequence_L']` | `float64` | ECDF-normalized expected match consequence. |
| `raw_consequence_L` | `v3['raw_consequence_L']` | `float64` | Raw expected match consequence. |
| `pre_delivery_wp` | `v3['pre_delivery_wp']` | `float64` | Win probability at $t^-$. |
| `bowler_runs_conceded` | `cohort['bowler_runs_conceded']` | `int64` | **Runs debited to bowler** (`runs` + penalty; byes/leg-byes excluded). |
| `team_runs_added` | `cohort['team_runs_added']` | `int64` | Total runs added to team score on delivery. |
| `is_bowler_wicket` | `is_w & dismissal in BOWLER_WKT` | `bool` | **True strictly for standard bowler dismissals.** |
| `is_other_dismissal`| `is_w & dismissal not in BOWLER_WKT`| `bool` | **True for run-outs, retire outs, field obstruction.** |
| `is_wicket` | `cohort['is_wicket']` | `bool` | True if a dismissal occurred on this delivery. |
| `dismissal_type` | `cohort['dismissal_type']` | `str/NaN` | Specific dismissal method. |
| `dismissal_type_id`| `cohort['dismissal_type_id']`| `float64` | Numeric dismissal ID. |
| `dismissed_player_id` | `cohort['dismissed_player_id']` | `float64` | ID of dismissed player. |
| `is_bowler_dot_ball`| `bowler_rc == 0` | `bool` | True if bowler conceded 0 runs on delivery. |
| `is_boundary_conceded` | `is_four \| is_six` | `bool` | True if boundary four or six conceded off bat. |
| `is_four_conceded` | `v3['is_four']` | `bool` | Boundary four conceded. |
| `is_six_conceded` | `v3['is_six']` | `bool` | Boundary six conceded. |
| `is_legal_ball` | `v3['is_legal_ball']` | `bool` | True if legal delivery (increments spell count). |
| `extras_type` | `cohort['extras_type']` | `str/NaN` | Specific extras classification. |
| `extras1_runs` | `cohort['extras1_runs']` | `int64` | Extras 1 runs. |
| `extras_2_runs` | `cohort['extras_2_runs']` | `int64` | Extras 2 runs. |
| `is_wide` | `extras_type == 'wide'` | `bool` | True if delivery was a wide. |
| `is_no_ball` | `extras_type in ['Overstep', 'other']` | `bool` | True if delivery was a no-ball. |
| `is_bye` | `extras_type == 'byes'` | `bool` | True if delivery resulted in byes. |
| `is_leg_bye` | `extras_type == 'legbyes'` | `bool` | True if delivery resulted in leg-byes. |

---

## 3. Row Counts & Stratified Delivery Breakdown

The cohort delivery counts across both datasets are identical and match the certified pure 20-over cohort:

| Stratum / Segment | Total Deliveries | Legal Deliveries | Wides | No-Balls | Byes / Leg-Byes | Deliveries with Wickets |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cohort Overall** | **186,780** | **178,798** | **7,190** | **792** | **3,020** | **10,020** |
| **Innings 1 (Defending)** | 97,443 | 93,243 | 3,799 | 401 | 1,595 | 5,178 |
| **Innings 2 (Chasing)** | 89,337 | 85,555 | 3,391 | 391 | 1,425 | 4,842 |
| **Powerplay (Overs 1–6)** | 56,878 | 54,420 | 2,192 | 266 | 934 | 2,752 |
| **Middle (Overs 7–16)** | 85,417 | 81,777 | 3,283 | 357 | 1,353 | 4,228 |
| **Death (Overs 17–20)** | 44,485 | 42,601 | 1,715 | 169 | 733 | 3,040 |

---

## 4. Unique Player & Match Coverage

### 4.1 Player Participation Counts
- **Total Unique Players in Dataset:** **`883`**
- **Unique Strikers (faced deliveries):** **`816`**
- **Unique Bowlers (bowled deliveries):** **`589`**
- **Unique Non-Strikers:** **`798`**
- **Players Appearing as Striker & Bowler (All-Rounders):** **`522`**
- **Players Appearing Solely as Specialist Batters (Never Bowled):** **`294`**
- **Players Appearing Solely as Bowlers (Never Batted):** **`67`**
- **Non-Strikers who Never Faced a Ball or Bowled:** **`0`**

### 4.2 Metadata Coverage Verification
Across all 883 unique players:
- **Found in `competition_team_player_mapping.csv`:** **`883 / 883 (100.0%)`**
- **Found in `playing_eleven.csv`:** **`883 / 883 (100.0%)`**
- **Unmapped Player IDs:** **`0`**
- **Discrepant Player Names Across Sources:** **`0`**

### 4.3 Match Coverage
- **Total Unique Matches:** **`782`**
- **Total Unique Competitions Represented:** **`138`**
- **All matches are certified pure 20-over matches** (4 DLS and 3 shortened matches completely excluded).

---

## 5. Missing-Value Audit

A comprehensive missing-value scan was performed across all columns in both datasets.

### 5.1 Systemic and Expected Missing Values

| Column Name | Missing Count | % Missing | Context & Justification |
| :--- | :---: | :---: | :--- |
| `runs_required` | 97,443 | 52.17% | **Expected.** First innings has no target or runs required. Missing in exactly all 97,443 Innings 1 rows. |
| `required_run_rate` | 97,443 | 52.17% | **Expected.** First innings has no RRR. Missing in exactly all 97,443 Innings 1 rows. |
| `extras_type` | 175,778 | 94.11% | **Expected.** Normal deliveries without extras have `NaN` extras type. Exactly 11,002 deliveries had extras. |
| `dismissal_type` | 176,760 | 94.64% | **Expected.** Deliveries without dismissals have `NaN`. Exactly 10,020 deliveries had dismissals. |
| `dismissal_type_id` | 176,760 | 94.64% | **Expected.** Exactly matches `dismissal_type`. |
| `dismissed_player_id`| 176,761 | 94.64% | **Expected.** Missing on 176,760 non-wicket balls + **1 source anomaly** documented below. |

### 5.2 Non-Systemic Source Anomaly: Match 40709, Delivery 19.5
- **Match ID:** `40709` | **Innings:** `2` | **Over:** `19.5` (Row 119890)
- **Dismissal Type:** `Retire Out`
- **Dismissed Player ID:** `NaN`
- **Source Inspection:** In `ball_by_ball.csv`, this delivery records `is_wicket = 1` and `dismissal_type = 'Retire Out'`, but `dismissed_player_id` was recorded as empty (`NaN`) by the original match scorers.
- **Handling in Step 5:**
  - Neither striker nor non-striker was arbitrarily assigned as out (`is_striker_dismissed = False`, `is_non_striker_dismissed = False`).
  - The delivery is correctly flagged as `is_wicket = True` and `is_other_dismissal = True`.
  - The source limitation is documented rather than silently imputed.

### 5.3 Unexpected Missing Values
- **Pressure fields (`pressure_batting`, `pressure_bowling`):** **`0 nulls`**
- **State fields (`score_before`, `wickets_before`, `legal_balls_before`):** **`0 nulls`**
- **Player identifiers (`striker_id`, `bowler_id`):** **`0 nulls`**
- **Performance outcomes (`batter_runs`, `bowler_runs_conceded`):** **`0 nulls`**

---

## 6. Duplicate Checks

The unique composite key for delivery identification is:
$$\text{Delivery Key} = (\text{match\_id}, \text{innings}, \text{overid}, \text{over\_ball\_num}, \text{innings\_ball\_num})$$

- **Duplicate delivery keys in `batting_pressure_deliveries`:** **`0`**
- **Duplicate delivery keys in `bowling_pressure_deliveries`:** **`0`**
- **Duplicate player entries in `player_mapping_audit.csv`:** **`0`**

Every single row represents a unique, non-overlapping physical delivery event.

---

## 7. Reconciliation with Historical Source Data

All performance metrics reconcile completely across the original `ball_by_ball.csv`, the Step 4 `clean_cohort_deliveries.parquet`, and the Step 5 outputs:

| Metric Category | Batting Dataset | Bowling Dataset | Cohort Dataset | Discrepancy |
| :--- | :---: | :---: | :---: | :---: |
| **Total Deliveries** | 186,780 | 186,780 | 186,780 | **0** |
| **Total Legal Balls** | 178,798 | 178,798 | 178,798 | **0** |
| **Total Batter Runs** | 250,992 | N/A | 250,992 | **0** |
| **Total Bowler Runs Conceded** | N/A | 258,974 | 258,974 | **0** |
| **Total Team Runs Added** | 262,072 | 262,072 | 262,072 | **0** |
| **Total Boundary Fours** | 21,683 | 21,683 | 21,683 | **0** |
| **Total Boundary Sixes** | 11,815 | 11,815 | 11,815 | **0** |
| **Total Delivery Wickets** | 10,020 | 10,020 | 10,020 | **0** |
| **Striker Dismissals** | 9,768 | N/A | 9,768 | **0** |
| **Non-Striker Dismissals** | 251 | N/A | 251 | **0** |
| **Bowler-Credited Wickets** | N/A | 9,463 | 9,463 | **0** |
| **Other Dismissals (Run Outs, etc.)** | N/A | 557 | 557 | **0** |
| **Official Balls Faced by Batters** | 179,590 | N/A | 179,590 | **0** |
| **Bowler Dot Balls Conceded** | N/A | 66,047 | 66,047 | **0** |

### Mathematical Reconciliation of Runs
The total team runs across 186,780 deliveries ($262,072$) reconciles via:
$$\text{Team Runs Added} = \text{Batter Runs} + \text{Extras} = 250,992 + 11,080 = \mathbf{262,072}$$
$$\text{Team Runs Added} = \text{Bowler Runs Conceded} + \text{Byes/Legbyes} = 258,974 + 3,098 = \mathbf{262,072}$$

---

## 8. Exclusions and Unresolved Source Limitations

### 8.1 Permanently Excluded Data (Strictly Maintained)
1. **Dead-Tail Deliveries (233 rows):**
   - Excluded in Step 4.0 because `runs_required <= 0` in Innings 2 represents dead game state after the chase has concluded. None reappear in Step 5.
2. **Four Mid-Match DLS Matches (821 deliveries):**
   - Matches `20182`, `23674`, `24822`, `28334` suffered mid-innings weather interruptions resulting in shortened chase targets. Completely excluded.
3. **Three Pre-Match Shortened Matches (496 deliveries):**
   - Matches `15795`, `31278`, `48514` were scheduled for fewer than 20 overs per side. Completely excluded.

### 8.2 Documented Source Limitations
1. **Match 40709 Delivery 19.5 Missing Dismissal ID:**
   - Raw source records a `Retire Out` without specifying which player retired out. Preserved as `is_wicket = True`, with striker and non-striker outs set to `False` to avoid unsupported imputation.
2. **Target Deficit Matches (38 matches):**
   - 38 matches in historical records have official second-innings targets that differ slightly from the first-innings score total due to legacy scorecard adjustments. As verified in Step 2.2, all pre-delivery chasing metrics use the official scoreboard `runs_required` and `required_run_rate` without retroactive tampering.

---

## 9. Final Quality Certification

The Step 5 player-level datasets achieve **100% data integrity, full source reconciliation, zero missing pressure observations, and strict attribution isolation**.

$$\mathbf{DATA \; QUALITY \; STATUS: \quad CERTIFIED \; PASS}$$
*The dataset is completely approved and ready for Step 6 Player Reliability Methodology Design.*
