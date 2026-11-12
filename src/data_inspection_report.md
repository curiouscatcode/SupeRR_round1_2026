# SupeRR Selector 2.0 — Comprehensive Data Inspection Report
**Competition:** SupeRR Selector Season 2 — Identify the Most Reliable Players Under Pressure  **Inspection Date:** November 2026  **Author / Agent:** Antigravity Pair Programming System  **Status:** Audit Complete — Ready for Feature Engineering & Pressure Index Calculation
---
## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [File Inventory & High-Level Metrics](#2-file-inventory--high-level-metrics)
3. [Detailed File-by-File Profiling](#3-detailed-file-by-file-profiling)
   - [3.1 competitions.csv](#31-competitionscsv)
   - [3.2 teams.csv](#32-teamscsv)
   - [3.3 matches.csv](#33-matchescsv)
   - [3.4 playing_eleven.csv](#34-playing_elevencsv)
   - [3.5 competition_team_player_mapping.csv](#35-competition_team_player_mappingcsv)
   - [3.6 ball_by_ball.csv](#36-ball_by_ballcsv)
4. [Relational Integrity & Entity Connectivity](#4-relational-integrity--entity-connectivity)
5. [Deep Dive: Runs, Extras, and Column Encoding Semantics](#5-deep-dive-runs-extras-and-column-encoding-semantics)
6. [Over & Ball Sequencing Analysis](#6-over--ball-sequencing-analysis)
7. [Data Quality Issues, Anomalies & Suspicious Records](#7-data-quality-issues-anomalies--suspicious-records)
8. [Pre-Requisites & Recommendations for Pressure Index Calculation](#8-pre-requisites--recommendations-for-pressure-index-calculation)
---
## 1. Executive Summary
This document provides a complete audit of the six data files supplied for Round 1 of the **SupeRR Selector Season 2** competition. The objective is to establish ground truth about schema definitions, relationships, value encodings, edge cases, and data hygiene before constructing any situational Pressure Index or player ranking model.

**Key High-Level Takeaways:**
- **Total Scale:** 200,999 ball-by-ball deliveries spanning 883 matches across 141 competitions (IPL and T20Is) from January 2022 to November 2026.
- **Integrity:** Zero duplicate rows across all 6 files. Primary and foreign key integrity between competitions, teams, matches, and players is extraordinarily high (>99.8%).
- **Critical Schema Decoding (`extras1_runs`):** `extras1_runs` is **NOT** a count of runs! It is an integer categorical code representing `extras_type` (1=Overstep, 2=wide, 3=legbyes, 4=byes, 5=other, 6=Normal ball, 7=Penalty). Relying on this column as runs will severely corrupt bowling and batting figures.
- **Batting vs. Extra Runs (`runs`):** The `runs` column exclusively captures runs scored off the bat. It is 0 for wides, byes, and leg-byes.
- **Illegal Delivery Run Misplacement (`extras_2_runs`):** In 36 deliveries (beamers and oversteps), runs scored off the delivery were logged in `extras_2_runs` instead of `runs`.
- **Sequencing:** `overid` starts strictly from **1** (values 1 through 20; 1 for Super Overs). Both `innings_ball_num` and `over_ball_num` start at **1** and increment strictly by **1.0** without gaps or duplicates, counting every physical delivery (including illegal deliveries).
- **Squad vs. Playing XI:** `playing_eleven.csv` contains entire squad rosters (28,381 rows). 8,667 rows represent bench players (`is_played == False`), which accounts for ~30.5% missing values in `batting_order`, `is_captain`, and `is_wk`.
- **Abandoned Matches:** 16 matches in `matches.csv` have no deliveries in `ball_by_ball.csv`, all of which were abandoned without a ball bowled.
---
## 2. File Inventory & High-Level Metrics
All six files in `data/` are comma-separated tabular files (`.csv`) that can be opened directly in Microsoft Excel, Python pandas, or SQL engines.

| File Name | File Size (MB) | Rows | Columns | Duplicate Rows | Entity Grain / Primary Key |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `ball_by_ball.csv` | 39.17 | 200,999 | 33 | 0 | `match_id`, `innings`, `innings_ball_num` |
| `competition_team_player_mapping.csv` | 0.44 | 6,413 | 6 | 0 | `comp_id`, `team_id`, `player_id` |
| `competitions.csv` | 0.01 | 141 | 4 | 0 | `comp_id` |
| `matches.csv` | 0.12 | 883 | 22 | 0 | `match_id` |
| `playing_eleven.csv` | 0.92 | 28,381 | 9 | 0 | `match_id`, `team_id`, `player_id` |
| `teams.csv` | 0.01 | 353 | 3 | 0 | `comp_id`, `team_id` |

---
## 3. Detailed File-by-File Profiling
### 3.1 `ball_by_ball.csv`
- **Row count:** 200,999
- **Column count:** 33
- **Duplicate rows:** 0

#### Column Dictionary & Missing Value Analysis
| # | Column Name | Data Type | Non-Null Count | Null Count | Null % | Sample Value |
| :-: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `match_id` | `int64` | 200,999 | 0 | 0.00% | 13511 |
| 2 | `innings` | `int64` | 200,999 | 0 | 0.00% | 1 |
| 3 | `overid` | `int64` | 200,999 | 0 | 0.00% | 1 |
| 4 | `over_ball_num` | `int64` | 200,999 | 0 | 0.00% | 1 |
| 5 | `innings_ball_num` | `int64` | 200,999 | 0 | 0.00% | 1 |
| 6 | `batting_team_id` | `int64` | 200,999 | 0 | 0.00% | 22 |
| 7 | `bowling_team_id` | `int64` | 200,999 | 0 | 0.00% | 28 |
| 8 | `striker_id` | `int64` | 200,999 | 0 | 0.00% | 1187 |
| 9 | `striker_name` | `str` | 200,999 | 0 | 0.00% | Jason Roy |
| 10 | `non_striker_id` | `int64` | 200,999 | 0 | 0.00% | 6273 |
| 11 | `non_striker_name` | `str` | 200,999 | 0 | 0.00% | Tom Banton |
| 12 | `bowler_id` | `int64` | 200,999 | 0 | 0.00% | 1772 |
| 13 | `bowler_name` | `str` | 200,999 | 0 | 0.00% | Sheldon Cottrell |
| 14 | `batting_type` | `str` | 200,999 | 0 | 0.00% | RHB |
| 15 | `bowling_type` | `str` | 200,999 | 0 | 0.00% | Left-arm fast-medium |
| 16 | `batting_order` | `int64` | 200,999 | 0 | 0.00% | 1 |
| 17 | `runs` | `int64` | 200,999 | 0 | 0.00% | 0 |
| 18 | `is_four` | `bool` | 200,999 | 0 | 0.00% | False |
| 19 | `is_six` | `bool` | 200,999 | 0 | 0.00% | False |
| 20 | `is_wicket` | `bool` | 200,999 | 0 | 0.00% | False |
| 21 | `dismissal_type_id` | `float64` | 10,881 | 190,118 | 94.59% | 1.0 |
| 22 | `dismissal_type` | `str` | 10,881 | 190,118 | 94.59% | Bowled |
| 23 | `dismissed_player_id` | `float64` | 10,892 | 190,107 | 94.58% | 1187.0 |
| 24 | `extras_type` | `str` | 11,832 | 189,167 | 94.11% | wide |
| 25 | `extras1_runs` | `int64` | 200,999 | 0 | 0.00% | 6 |
| 26 | `extras_2_runs` | `int64` | 200,999 | 0 | 0.00% | 0 |
| 27 | `pace_or_spin` | `str` | 200,999 | 0 | 0.00% | Pace |
| 28 | `bowl_speed` | `float64` | 200,999 | 0 | 0.00% | 0.0 |
| 29 | `stroke` | `str` | 194,841 | 6,158 | 3.06% | Cover Drive |
| 30 | `delivery_style` | `str` | 200,608 | 391 | 0.19% | Inswing |
| 31 | `over_or_around` | `str` | 200,592 | 407 | 0.20% | Over |
| 32 | `on_or_off` | `str` | 200,999 | 0 | 0.00% | Off-side |
| 33 | `delivery_ist_time` | `str` | 200,999 | 0 | 0.00% | 2022-01-23 00:00:00 UTC |

#### Five Sample Rows
> *Note: For high-dimensional datasets like `matches.csv` and `ball_by_ball.csv`, selected core columns are shown below for visual clarity. The complete columns are documented in the schema above.*

|   match_id |   innings |   overid |   over_ball_num | striker_name   | bowler_name      |   runs |   extras_type |   extras1_runs |   extras_2_runs | is_wicket   |
|-----------:|----------:|---------:|----------------:|:---------------|:-----------------|-------:|--------------:|---------------:|----------------:|:------------|
|      13511 |         1 |        1 |               1 | Jason Roy      | Sheldon Cottrell |      0 |           nan |              6 |               0 | False       |
|      13511 |         1 |        1 |               2 | Jason Roy      | Sheldon Cottrell |      0 |           nan |              6 |               0 | False       |
|      13511 |         1 |        1 |               3 | Jason Roy      | Sheldon Cottrell |      0 |           nan |              6 |               0 | False       |
|      13511 |         1 |        1 |               4 | Jason Roy      | Sheldon Cottrell |      0 |           nan |              6 |               0 | False       |
|      13511 |         1 |        1 |               5 | Jason Roy      | Sheldon Cottrell |      6 |           nan |              6 |               0 | False       |

### 3.2 `competition_team_player_mapping.csv`
- **Row count:** 6,413
- **Column count:** 6
- **Duplicate rows:** 0

#### Column Dictionary & Missing Value Analysis
| # | Column Name | Data Type | Non-Null Count | Null Count | Null % | Sample Value |
| :-: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `comp_id` | `int64` | 6,413 | 0 | 0.00% | 1331 |
| 2 | `comp_name` | `str` | 6,413 | 0 | 0.00% | England in West Indies T20I... |
| 3 | `team_id` | `int64` | 6,413 | 0 | 0.00% | 22 |
| 4 | `team_name` | `str` | 6,413 | 0 | 0.00% | England |
| 5 | `player_id` | `int64` | 6,413 | 0 | 0.00% | 478 |
| 6 | `player_name` | `str` | 6,413 | 0 | 0.00% | Eoin Morgan |

#### Five Sample Rows
|   comp_id | comp_name                               |   team_id | team_name   |   player_id | player_name   |
|----------:|:----------------------------------------|----------:|:------------|------------:|:--------------|
|      1331 | England in West Indies T20I Series 2022 |        22 | England     |         478 | Eoin Morgan   |
|      1331 | England in West Indies T20I Series 2022 |        22 | England     |         479 | Adil Rashid   |
|      1331 | England in West Indies T20I Series 2022 |        22 | England     |         722 | Liam Dawson   |
|      1331 | England in West Indies T20I Series 2022 |        22 | England     |         786 | Chris Jordan  |
|      1331 | England in West Indies T20I Series 2022 |        22 | England     |        1187 | Jason Roy     |

### 3.3 `competitions.csv`
- **Row count:** 141
- **Column count:** 4
- **Duplicate rows:** 0

#### Column Dictionary & Missing Value Analysis
| # | Column Name | Data Type | Non-Null Count | Null Count | Null % | Sample Value |
| :-: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `comp_id` | `int64` | 141 | 0 | 0.00% | 3395 |
| 2 | `comp_name` | `str` | 141 | 0 | 0.00% | South Africa in New Zealand... |
| 3 | `match_format` | `str` | 141 | 0 | 0.00% | T20I |
| 4 | `season` | `str` | 141 | 0 | 0.00% | 2026 |

#### Five Sample Rows
|   comp_id | comp_name                                    | match_format   |   season |
|----------:|:---------------------------------------------|:---------------|---------:|
|      3395 | South Africa in New Zealand T20I Series 2026 | T20I           |     2026 |
|      3405 | Afghanistan v Sri Lanka T20I Series 2026     | T20I           |     2026 |
|      3465 | India in Zimbabwe T20I Series 2026           | T20I           |     2026 |
|      3568 | Bangladesh in Zimbabwe T20I Series 2026      | T20I           |     2026 |
|      3482 | Australia in Bangladesh T20I Series 2026     | T20I           |     2026 |

### 3.4 `matches.csv`
- **Row count:** 883
- **Column count:** 22
- **Duplicate rows:** 0

#### Column Dictionary & Missing Value Analysis
| # | Column Name | Data Type | Non-Null Count | Null Count | Null % | Sample Value |
| :-: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `match_id` | `int64` | 883 | 0 | 0.00% | 13511 |
| 2 | `comp_id` | `int64` | 883 | 0 | 0.00% | 1331 |
| 3 | `match_number` | `int64` | 883 | 0 | 0.00% | 1 |
| 4 | `match_date` | `str` | 883 | 0 | 0.00% | 2022-01-22 |
| 5 | `stage` | `str` | 883 | 0 | 0.00% | League |
| 6 | `venue_id` | `int64` | 883 | 0 | 0.00% | 54 |
| 7 | `venue_country` | `str` | 883 | 0 | 0.00% | West Indies |
| 8 | `home_team_id` | `int64` | 883 | 0 | 0.00% | 28 |
| 9 | `home_team` | `str` | 883 | 0 | 0.00% | West Indies |
| 10 | `away_team_id` | `int64` | 883 | 0 | 0.00% | 22 |
| 11 | `away_team` | `str` | 883 | 0 | 0.00% | England |
| 12 | `home_team_captain_id` | `float64` | 839 | 44 | 4.98% | 494.0 |
| 13 | `away_team_captain_id` | `float64` | 838 | 45 | 5.10% | 478.0 |
| 14 | `toss_win_team_id` | `float64` | 868 | 15 | 1.70% | 28.0 |
| 15 | `toss_opted` | `str` | 868 | 15 | 1.70% | Fielding |
| 16 | `man_of_the_match` | `int64` | 883 | 0 | 0.00% | 0 |
| 17 | `first_inn_revised_overs` | `float64` | 25 | 858 | 97.17% | 114.0 |
| 18 | `second_inn_revised_overs` | `float64` | 25 | 858 | 97.17% | 114.0 |
| 19 | `revised_target` | `float64` | 23 | 860 | 97.40% | 143.0 |
| 20 | `knock_out` | `int64` | 883 | 0 | 0.00% | 0 |
| 21 | `win_team_id` | `float64` | 842 | 41 | 4.64% | 28.0 |
| 22 | `result` | `str` | 883 | 0 | 0.00% | West Indies Won by 9 Wickets |

#### Five Sample Rows
> *Note: For high-dimensional datasets like `matches.csv` and `ball_by_ball.csv`, selected core columns are shown below for visual clarity. The complete columns are documented in the schema above.*

|   match_id |   comp_id | match_date   | home_team   | away_team   | toss_opted   | result                       |   win_team_id |
|-----------:|----------:|:-------------|:------------|:------------|:-------------|:-----------------------------|--------------:|
|      13511 |      1331 | 2022-01-22   | West Indies | England     | Fielding     | West Indies Won by 9 Wickets |            28 |
|      13512 |      1331 | 2022-01-23   | West Indies | England     | Fielding     | England Won by 1 Run         |            22 |
|      13513 |      1331 | 2022-01-26   | West Indies | England     | Fielding     | West Indies Won by 20 runs   |            28 |
|      13514 |      1331 | 2022-01-29   | West Indies | England     | Fielding     | England Won by 34 runs       |            22 |
|      13515 |      1331 | 2022-01-30   | West Indies | England     | Batting      | West Indies Won by 17 runs   |            28 |

### 3.5 `playing_eleven.csv`
- **Row count:** 28,381
- **Column count:** 9
- **Duplicate rows:** 0

#### Column Dictionary & Missing Value Analysis
| # | Column Name | Data Type | Non-Null Count | Null Count | Null % | Sample Value |
| :-: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `match_id` | `int64` | 28,381 | 0 | 0.00% | 13511 |
| 2 | `team_id` | `int64` | 28,381 | 0 | 0.00% | 22 |
| 3 | `player_id` | `int64` | 28,381 | 0 | 0.00% | 1187 |
| 4 | `batting_order` | `float64` | 19,703 | 8,678 | 30.58% | 1.0 |
| 5 | `is_played` | `bool` | 28,381 | 0 | 0.00% | True |
| 6 | `is_captain` | `object` | 19,714 | 8,667 | 30.54% | False |
| 7 | `is_wk` | `object` | 19,714 | 8,667 | 30.54% | False |
| 8 | `is_impact` | `int64` | 28,381 | 0 | 0.00% | 0 |
| 9 | `is_impact_off` | `int64` | 28,381 | 0 | 0.00% | 0 |

#### Five Sample Rows
|   match_id |   team_id |   player_id |   batting_order | is_played   | is_captain   | is_wk   |   is_impact |   is_impact_off |
|-----------:|----------:|------------:|----------------:|:------------|:-------------|:--------|------------:|----------------:|
|      13511 |        22 |        1187 |               1 | True        | False        | False   |           0 |               0 |
|      13511 |        22 |        6273 |               2 | True        | False        | False   |           0 |               0 |
|      13511 |        22 |        1210 |               3 | True        | False        | False   |           0 |               0 |
|      13511 |        22 |        1596 |               4 | True        | False        | False   |           0 |               0 |
|      13511 |        22 |         478 |               5 | True        | False        | False   |           0 |               0 |

### 3.6 `teams.csv`
- **Row count:** 353
- **Column count:** 3
- **Duplicate rows:** 0

#### Column Dictionary & Missing Value Analysis
| # | Column Name | Data Type | Non-Null Count | Null Count | Null % | Sample Value |
| :-: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `comp_id` | `int64` | 353 | 0 | 0.00% | 1331 |
| 2 | `team_id` | `int64` | 353 | 0 | 0.00% | 22 |
| 3 | `team_name` | `str` | 353 | 0 | 0.00% | England |

#### Five Sample Rows
|   comp_id |   team_id | team_name   |
|----------:|----------:|:------------|
|      1331 |        22 | England     |
|      1331 |        28 | West Indies |
|      1335 |        18 | India       |
|      1335 |        28 | West Indies |
|      1345 |        20 | Australia   |

---
## 4. Relational Integrity & Entity Connectivity
To determine whether the datasets can be joined cleanly to compute match-contextual metrics, we verified all foreign key relationships.

### 4.1 `comp_id` Connectivity
- `competitions.csv`: **141** unique competition IDs.
- `matches.csv`: **138** unique competition IDs. (All 138 exist in `competitions.csv`; 3 competitions in the master catalog had zero scheduled matches).
- `teams.csv`: **141** unique competition IDs (100% match).
- `competition_team_player_mapping.csv`: **140** unique competition IDs (100% match).
- **Verdict:** `comp_id` provides a **100% consistent link** across all tournament metadata.

### 4.2 `match_id` Connectivity
- `matches.csv`: **883** unique matches.
- `playing_eleven.csv`: **880** unique matches. Exactly 3 matches are missing playing XI data, all of which are matches abandoned before toss.
- `ball_by_ball.csv`: **867** unique matches. All 867 match IDs exist in `matches.csv`.
- **Matches without Ball-by-Ball Records:** Exactly **16 matches** in `matches.csv` have zero records in `ball_by_ball.csv`. Every single one of these 16 matches had `result == 'Match Abandoned'` (rain/washout prior to ball 1).
- **Verdict:** `match_id` provides an **unbroken join** between match conditions and delivery-level data.

### 4.3 `team_id` Connectivity
- Across all six datasets, there are exactly **38 unique teams**.
- Every team appearing in `matches.csv` (home/away), `playing_eleven.csv`, `competition_team_player_mapping.csv`, and `ball_by_ball.csv` (batting/bowling) has a corresponding record in `teams.csv`.
- **Verdict:** Referential integrity for teams is **100.0%**.

### 4.4 `player_id` Connectivity
- `competition_team_player_mapping.csv`: **1,217** registered players.
- `playing_eleven.csv`: **1,082** players.
- `ball_by_ball.csv`: **959** active players (batters, bowlers, non-strikers, dismissed players).
- **100% Master Mapping Coverage:** Every single player appearing in `ball_by_ball.csv` and `playing_eleven.csv` is mapped in `competition_team_player_mapping.csv`.
- **Playing XI Discrepancy (2 Players):** Exactly **2 players** (`player_id` 36153 and 39444) participate in `ball_by_ball.csv` in the *Mens T20 Emerging Teams Asia Cup 2024* (matches 37087, 37092, 37095) but were omitted from `playing_eleven.csv` for those specific matches.
- **Verdict:** Player identification is robust. Joins for player names, roles, and profiles must use `competition_team_player_mapping.csv` as the primary dimension table.

---
## 5. Deep Dive: Runs, Extras, and Column Encoding Semantics
One of the most critical aspects of cricket analytics is correctly computing runs, boundaries, and bowler economy. Our inspection revealed essential discoveries about what `runs`, `extras_type`, `extras1_runs`, and `extras_2_runs` actually represent.

### 5.1 The `extras1_runs` Column: Categorical ID, NOT Runs!
At first glance, a column named `extras1_runs` would appear to store the numeric runs awarded for an extra. **However, empirical cross-tabulation proves conclusively that `extras1_runs` is a 1-to-1 numeric surrogate key for `extras_type`:**

| extras_type   |   1 |    2 |    3 |   4 |   5 |      6 |   7 |
|:--------------|----:|-----:|-----:|----:|----:|-------:|----:|
| None (Normal) |   0 |    0 |    0 |   0 |   0 | 189167 |   0 |
| Overstep      | 576 |    0 |    0 |   0 |   0 |      0 |   0 |
| Penalty       |   0 |    0 |    0 |   0 |   0 |      0 |   1 |
| byes          |   0 |    0 |    0 | 529 |   0 |      0 |   0 |
| legbyes       |   0 |    0 | 2748 |   0 |   0 |      0 |   0 |
| other         |   0 |    0 |    0 |   0 | 264 |      0 |   0 |
| wide          |   0 | 7714 |    0 |   0 |   0 |      0 |   0 |

**Encoding Key:**
- `1` = `Overstep` (No-Ball due to front-foot overstepping)
- `2` = `wide`
- `3` = `legbyes`
- `4` = `byes`
- `5` = `other` (No-Ball due to height/beamer or fielding restriction)
- `6` = `None` (Standard delivery without extras)
- `7` = `Penalty` (Penalty runs awarded)

> [!CAUTION]
> **Do NOT sum `extras1_runs`!** If an analyst calculates `total_runs = runs + extras1_runs`, every normal dot ball will mistakenly add **6 runs**, completely corrupting the analysis!

### 5.2 The `runs` Column: Batting Runs Only
- Distribution of `runs`: `0`: 79,387 | `1`: 72,267 | `2`: 12,547 | `3`: 656 | `4`: 23,303 | `5`: 25 | `6`: 12,814.
- On `wide` deliveries (7,714 balls): `runs` is **0 in 100% of cases**.
- On `byes` deliveries (529 balls): `runs` is **0 in 100% of cases**.
- On `legbyes` deliveries (2,748 balls): `runs` is **0 in 2,747 cases** (and 1 in a single clerical outlier).
- On `Overstep` and `other` (No-Balls): `runs` records the runs scored off the bat (0, 1, 2, 3, 4, 6).
- **Conclusion:** `runs` represents **runs scored off the bat by the striker**.

### 5.3 The `extras_2_runs` Column: Overflow for Illegal Delivery Runs
- In 200,963 deliveries (99.98%), `extras_2_runs` is `0`.
- In exactly **36 deliveries**, `extras_2_runs` is non-zero (20 rows with `1`, 16 rows with `4`).
- Detailed inspection of these 36 deliveries reveals that in all 36 cases, `runs == 0` while the delivery style was a `Beamer`, `Full Toss`, or `Overstep`, and the batsman played a stroke (e.g. Pull Shot, UpperCut, Leg Glance).
- **Conclusion:** In these 36 specific instances, the runs scored off the illegal delivery were logged in `extras_2_runs` rather than `runs`.

### 5.4 Standardized Formula for Total Delivery Runs & Bowler Economy
To ensure accurate pressure calculations and bowler/batter statistics:
1. **Batter Runs:** `runs + (extras_2_runs if extras_type in ['Overstep', 'other'] else 0)`
2. **Extra Runs on Delivery:**
   - If `extras_type == 'wide'`: `1` (plus any running extras)
   - If `extras_type in ['Overstep', 'other']`: `1` (the no-ball penalty)
   - If `extras_type == 'byes'`: byes conceded
   - If `extras_type == 'legbyes'`: leg-byes conceded
3. **Bowler Runs Conceded:** Batter runs + Wide extras + No-ball extras (byes and leg-byes do NOT count against the bowler).

---
## 6. Over & Ball Sequencing Analysis
Understanding delivery ordering is paramount for calculating balls remaining, required run rate, death-over pressure, and win probability.

### 6.1 `overid` Analysis
- **Starting Value:** Starts strictly from **1** (not 0).
- **Maximum Value:** **20** (representing the 20th over).
- **Super Overs:** In innings 3 and 4 (Super Overs), `overid` is always `1`.
- **Indexing Convention:** `overid` is **1-based** (Over 1 covers traditional cricket overs 0.1 to 0.6; Over 20 covers 19.1 to 19.6).

### 6.2 `innings_ball_num` Analysis
- **Starting Value:** Starts at **1** in **100% of innings** across all matches.
- **Sequence Regularity:** Increments by strictly **+1.0** on every delivery without any gaps (`diff == 1.0` in 199,275 intra-innings steps).
- **Zero Duplicates:** Exactly 0 duplicate `(match_id, innings, innings_ball_num)` tuples exist.
- **Physical Delivery Counter:** Counts **every physical delivery**, including wides and no-balls. Maximum recorded is 136 deliveries in an innings (due to 16 extras bowled).

### 6.3 `over_ball_num` Analysis
- **Starting Value:** Starts at **1** for every over in every innings.
- **Sequence Regularity:** Increments by strictly **+1.0** delivery by delivery within each over.
- **Physical Delivery Counter within Over:** Does **not** reset or freeze on illegal deliveries. For example, if ball 4 is a wide, the wide is recorded as `over_ball_num = 4`, and the next delivery is recorded as `over_ball_num = 5`.
- **Over Length Distribution:**
  - 6 deliveries: 25,081 overs (standard clean overs)
  - 7 deliveries: 5,346 overs (1 extra)
  - 8 deliveries: 1,085 overs (2 extras)
  - 9 deliveries: 222 overs
  - 10 deliveries: 42 overs
  - 11 deliveries: 13 overs
  - 13 deliveries: 2 overs (maximum recorded in an over)
  - 1 to 5 deliveries: 559 overs (overs cut short by all-out or target reached)

---
## 7. Data Quality Issues, Anomalies & Suspicious Records
Our audit identified several anomalies and telemetry inconsistencies. None of the original files were modified; these issues must be handled via data-cleaning pipelines in `src/`.

### 7.1 Delivery Speed (`bowl_speed`) Outliers & Missing Values
- **Unrecorded Speeds (0.0 km/h):** **77,861** deliveries (38.74%) have speed `0.0` where radar tracking was absent or unlogged.
- **Negative Speed:** Exactly 1 delivery has `bowl_speed == -1.0` (Axar Patel, Match 14108, Innings 2, Over 9, Ball 1).
- **Extreme Supersonic Speeds:** **20 deliveries** have recorded speeds exceeding 165 km/h, reaching up to **1456.1 km/h** (e.g. Khaleel Ahmed 1456.1 km/h, Kagiso Rabada 1339.6 km/h, Mitchell Starc 1246.0 km/h). These are decimal shift errors where `145.6` was saved as `1456.1`.
- **Implausibly Low Speeds:** Pacemen recorded bowling at 1.32 km/h (Sam Curran) or 6.31 km/h (Josh Hazlewood).
- **Recommendation:** Do not use `bowl_speed` as a primary raw feature for pressure models without imputing or normalizing decimal placement errors.

### 7.2 Wicket & Dismissal Inconsistencies
- **Categorical Typo:** `dismissal_type` has two separate spellings for obstructing the field: `Obstracting the field` (2 rows) and `Obstructing the field` (1 row). Standardize to `Obstructing the field`.
- **Ghost Dismissals on Non-Wicket Deliveries:** Exactly **12 rows** have `is_wicket == False` and `dismissal_type == NaN`, but `dismissed_player_id` is populated with a player ID. These appear to be overturned dismissals via DRS review where the player ID was not wiped.
- **Missing Dismissed Player on Retire Out:** In Match 40709 (Innings 2, Over 20, Ball 5), `is_wicket == True` and `dismissal_type == 'Retire Out'`, but `dismissed_player_id` is NaN.

### 7.3 Boundary Flag Discrepancies
- **Fours without Boundary Flag:** **20 rows** have `runs == 4` but `is_four == False`. These correspond to 4 runs taken by running between wickets or overthrows.
- **Sixes without Boundary Flag:** **3 rows** have `runs == 6` but `is_six == False`.
- **Recommendation:** For boundary percentage metrics, rely on `is_four` and `is_six` rather than assuming every 4 or 6 was a boundary rope hit.

### 7.4 Squad Roster Semantics in `playing_eleven.csv`
- `playing_eleven.csv` contains 28,381 rows across 880 matches.
- Exactly **8,667 rows** have `is_played == False` (substitutes/squad members).
- All {anomalies['bench_null_bo']:,} bench rows have null `batting_order`, `is_captain`, and `is_wk`.
- **Recommendation:** Always filter by `is_played == True` when analyzing the active playing XI.

### 7.5 Incomplete Matches & Null Match Winners
- **41 matches** in `matches.csv` have null `win_team_id`:
  - `No Result`: 21 matches
  - `Match Abandoned`: 19 matches
  - `Match Tied`: 1 matches
- One match (Match 18532, NZ vs IND, 2022-11-22) ended in a DLS Par Score Tie without Super Over.
- **15 matches** have null toss information because they were abandoned prior to the toss.

---
## 8. Pre-Requisites & Recommendations for Pressure Index Calculation
Before formulating the situational Pressure Index or computing player rankings, the following data pipeline standards must be enforced:

1. **Legal Delivery Identification:** Define a boolean column `is_legal_ball = ~extras_type.isin(['wide', 'Overstep', 'other'])` to accurately compute balls faced by batters and legal overs completed by bowlers.
2. **Batter Runs & Strike Rate:** Use `runs` (plus `extras_2_runs` on no-balls). Divide by total legal balls faced (plus no-balls, excluding wides).
3. **Bowler Economy & Runs Conceded:** Calculate bowler runs as `runs + (1 if extras_type in ['wide', 'Overstep', 'other'] else 0) + extras_2_runs`. Exclude byes and legbyes.
4. **Match State Tracking (Innings 2 Chase Pressure):** Compute cumulative target runs, cumulative runs scored, balls remaining (from 120 minus legal balls), wickets fallen, and instantaneous Required Run Rate (RRR) vs Current Run Rate (CRR).
5. **Match State Tracking (Innings 1 Death Overs Pressure):** Track wickets remaining, stage of innings (Powerplay: overs 1-6, Middle: 7-15, Death: 16-20), and projected team par score.
6. **Standardize Dismissal Categories:** Standardize `Obstracting the field` to `Obstructing the field`, and filter out ghost dismissed player IDs where `is_wicket == False`.
7. **Speed Normalization:** Cap or normalize speeds where `bowl_speed > 165` by dividing by 10 if using delivery velocity in bowling pressure models.

---
*Report generated by Antigravity Data Inspection Module.*  
