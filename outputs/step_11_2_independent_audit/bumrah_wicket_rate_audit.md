# Audit Investigation 1: Jasprit Bumrah Wicket Rate Reconciliation

## Executive Summary & Discrepancy Resolution

An apparent discrepancy was identified between previous project documentation:
- **Step 8 Exploratory Data Analysis (EDA):** Reported 168 high-pressure legal balls, 3 wickets, wicket rate of **1.79%**, economy of 6.89, and rank #14.
- **Step 11 Investigation:** Reported 168 high-pressure legal balls, 5 wickets, wicket rate of **2.98%**, economy of 6.93, and rank #24.

### Definitively Established Facts from Authoritative Source Data:
1. **The Step 11 figures are 100% numerically correct and verified.**
2. **Exact High-Pressure Deliveries:** Jasprit Bumrah bowled **177 total deliveries** where `Bowling_PI > 60.0`. Of these, **168 were legal balls** (9 extras: 7 wides, 2 no-balls).
3. **Exact High-Pressure Runs Conceded:** Exactly **194 runs** (yielding an economy rate of $194 / 168 \times 6 = \mathbf{6.93}$ rpo).
4. **Exact High-Pressure Dismissals:** Exactly **5 dismissals** occurred. **All 5 dismissals are bowler-credited** (2 Bowled, 3 Caught; 0 run outs).
5. **Exact High-Pressure Wicket Rate:** $\mathbf{2.98\%}$ ($5 / 168 = 2.976\%$, exactly matching Step 11).
6. **Root Cause of the 1.79% Discrepancy:** In Step 8 (`src/exploratory_analysis/eda_07_outliers_and_anomalies.py`, lines 215–230), the author **hardcoded an unverified narrative dictionary** (`VULN-01`) stating `'Econ 6.89, Wickets 3 (Wk% 1.79%), Dots 50.0%', Tier 1 Rank #14`. This erroneous figure arose because:
   - Bumrah took exactly **3 wickets in Innings 1** (and 2 in Innings 2). Dividing Innings 1 wickets (3) by total legal balls (168) yields $3 / 168 = \mathbf{1.7857\% \approx 1.79\%}$.
   - Bumrah conceded **193 runs** in `Bowling_Pressure_Level == 'High'` (excluding the 1 run in `Very High`). Dividing 193 by 168 yields $193 / 168 \times 6 = \mathbf{6.89}$ rpo.
   - This was an **editorial narrative error** in Step 8, completely refuted by the underlying CSV datasets.

---

## 1. Independent Recalculation Audit Checklist

| Audit Item | Value | Authoritative Source Verification | Status |
| :--- | :---: | :--- | :---: |
| **High-Pressure Legal Balls** | **168** | `delivery_pressure_index.csv` (177 deliveries - 9 extras) | **CONFIRMED** |
| **High-Pressure Wickets** | **5** | All 5 bowler-credited (`is_wicket==1 & dismissal_type in BOWLER_WICKET_TYPES`) | **CONFIRMED** |
| **Wicket Rate Denominator** | **Legal Balls (168)** | $5 / 168 \times 100 = 2.976\%$ | **CONFIRMED** |
| **Runs Conceded** | **194** | `bowler_runs_conceded` sum for `Bowling_PI > 60.0` | **CONFIRMED** |
| **Economy Rate** | **6.93** | $(194 / 168) \times 6 = 6.9286$ rpo | **CONFIRMED** |
| **Dot Balls Bowled** | **73** | $73 / 168 = 43.45\%$ | **CONFIRMED** |
| **Non-Bowler Dismissals** | **0** | Zero run-outs or non-bowler dismissals occurred on Bumrah's balls | **CONFIRMED** |
| **Post-Target Deliveries** | **Excluded** | Standard tail filter applied in Step 6.2 pipeline | **CONFIRMED** |
| **Pressure Definition** | **Bowling_PI > 60.0** | Includes both High (60-80) and Very High (>80) tiers | **CONFIRMED** |
| **Official Baseline Model** | **Model 0 (v2.0)** | BoRS = 59.29, Official Tier 1 Rank = #24 | **CONFIRMED** |

---

## 2. Complete Roster of High-Pressure Dismissals Bowled by Bumrah

| Match ID | Innings | Over | Batter Dismissed | Dismissal Type | Bowler Credited? | Bowling PI | Pressure Tier |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| 24822 | 1 | 1.2 | **Andrew Balbirnie** | Bowled | **YES** | 69.21 | High |
| 31273 | 1 | 6.5 | **Abhishek Sharma** | Caught | **YES** | 62.53 | High |
| 40722 | 2 | 13.4 | **Axar Patel** | Caught | **YES** | 60.79 | High |
| 41978 | 2 | 18.6 | **Ben Dwarshuis** | Bowled | **YES** | 60.74 | High |
| 48594 | 1 | 10.1 | **Rachin Ravindra** | Caught | **YES** | 64.25 | High |

---

## 3. Detailed Component Comparison: Bumrah vs Top 10 Bowlers

| Rank | Player | High Balls | Obs Econ | Obs Wk % | Score Econ (0.40) | Score Wk (0.25) | Score Dot (0.20) | Score Diff (0.15) | BoRS |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| #1 | Tim Southee | 64 | 5.16 | 10.94% | 85.54 | 90.05 | 98.93 | 94.53 | 90.69 |
| #2 | Keshav Maharaj | 78 | 6.23 | 8.97% | 77.75 | 78.01 | 80.29 | 88.52 | 79.94 |
| #3 | Haris Rauf | 106 | 6.79 | 8.49% | 74.69 | 77.51 | 83.83 | 85.45 | 78.84 |
| #4 | Mark Adair | 71 | 5.32 | 4.23% | 85.55 | 39.60 | 80.81 | 96.12 | 74.70 |
| #5 | Shoriful Islam | 61 | 6.79 | 8.20% | 69.84 | 69.00 | 89.89 | 72.35 | 74.01 |
| #6 | Harshit Rana | 158 | 7.86 | 6.33% | 64.19 | 59.54 | 91.72 | 92.94 | 72.85 |
| #7 | Wanindu Hasaranga | 198 | 6.82 | 6.57% | 78.84 | 62.84 | 59.18 | 73.03 | 70.04 |
| #8 | Trent Boult | 180 | 7.50 | 5.00% | 69.36 | 46.14 | 97.73 | 72.68 | 69.72 |
| #9 | Simarjeet Singh | 60 | 8.00 | 6.67% | 58.65 | 57.68 | 87.98 | 92.83 | 69.40 |
| #10 | Lungi Ngidi | 110 | 7.31 | 5.45% | 69.07 | 50.07 | 79.24 | 86.00 | 68.89 |
| #24 | **Jasprit Bumrah** | 168 | 6.93 | 2.98% | 76.38 | 25.31 | 70.08 | 55.96 | **59.29** |

### Why Bumrah Trails Rank #10 Lungi Ngidi by 9.60 Points:
- **Economy Component:** Bumrah gains **+2.92 points** ($0.40 \times (76.38 - 69.07)$).
- **Wicket Component:** Bumrah loses **-6.19 points** ($0.25 \times (25.31 - 50.07)$).
- **Clutch Differential Component:** Bumrah loses **-4.51 points** ($0.15 \times (55.96 - 86.00)$).
- **Dot Ball Component:** Bumrah loses **-1.83 points** ($0.20 \times (70.08 - 79.24)$).
- **Net Difference:** $+2.92 - 6.19 - 4.51 - 1.83 = \mathbf{-9.60}$ points.

---
*(Report generated automatically by Step 11.2 Independent Audit - Investigation 1)*