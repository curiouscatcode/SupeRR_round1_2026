# Audit Investigation 4: Match-Level Consistency & Opportunity Validation

## Executive Summary

Step 11 concluded that high aggregate reliability scores conceal significant match-to-match fragility, highlighting that **53.1% of Shubham Dubey's runs** and **75.0% of Simarjeet Singh's wickets** were concentrated in just two matches, proposing that such players are 'outlier-dependent'.

### Independent Audit Conclusions:
1. **Numerical Verification:** Both figures are **100% numerically verified**. Shubham Dubey scored 52 of his 98 high-pressure runs in 2 matches (53.06%). Simarjeet Singh took 3 of his 4 high-pressure wickets in 2 matches (75.00%).
2. **Statistical Audit: High Concentration is Mathematically Inevitable for Low Match Counts:**
   - Across all Tier 1 batters, distinct match count correlates strongly and negatively with Top-2 run concentration (**$r = -0.7074$**). Across bowlers, the correlation is **$r = -0.5680$**.
   - If a player only plays 10 matches, their Top 2 matches represent 20% of their career opportunities. If a player plays 40 matches, the Top 2 matches represent only 5%.
   - **Dubey's Peer Group:** Among Tier 1 batters with 10–18 matches, the mean Top 2 share is **41.7%** (median 40.5%). Dubey's 53.1% is completely standard for a 14-match player, not an erratic anomaly.
   - **Simarjeet's Peer Group:** In T20 bowling under high pressure, wickets are discrete Poisson events with low base rates (~5%). When a bowler takes only 4 wickets across 9 matches (2 in match 1, 1 in match 2, 1 in match 3), any two matches will mathematically account for at least $3/4 = 75.0\%$ of their total wickets! Among bowlers with $\le 14$ matches, the median Top-2 wicket share is **66.7%**.
3. **The True Underlying Weakness:**
   - The root cause is **not player inconsistency**, but **match-level sample truncation**.
   - The 60-ball qualification threshold allows players with as few as **7 to 9 matches** into Tier 1.
   - The correct remedy is **not an arbitrary consistency penalty**, but introducing a **dual qualification threshold** (e.g. minimum 60 balls faced **AND** minimum 15 distinct match opportunities).

---

## 1. Top 10 Batters Match Opportunity & Dispersion Audit

| Rank | Player | BRS | High Balls | Matches | Meaningful (>=5b) | Balls/Match | Median SR | Mean SR | Std SR | IQR SR | Top 2 Share |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| #1 | **Mahendra Singh Dhoni** | 95.05 | 171 | 38 | 14 | 4.5 | 137.5 | 166.8 | 146.1 | 174.3 | **18.5%** |
| #2 | **Shashank Singh** | 84.04 | 105 | 21 | 11 | 5.0 | 100.0 | 152.4 | 103.8 | 155.8 | **28.6%** |
| #3 | **Shivam Dube** | 82.97 | 140 | 38 | 14 | 3.7 | 150.0 | 154.1 | 126.8 | 119.2 | **20.6%** |
| #4 | **Shubham Dubey** | 80.82 | 55 | 14 | 6 | 3.9 | 100.0 | 140.3 | 123.8 | 157.5 | **53.1%** |
| #5 | **Cameron Green** | 80.70 | 77 | 26 | 5 | 3.0 | 100.0 | 163.4 | 105.5 | 100.0 | **24.4%** |
| #6 | **Vijay Shankar** | 78.02 | 57 | 12 | 7 | 4.8 | 129.2 | 144.7 | 71.7 | 92.9 | **36.7%** |
| #7 | **Jitesh Sharma** | 77.01 | 82 | 29 | 6 | 2.8 | 100.0 | 136.7 | 131.3 | 133.3 | **24.2%** |
| #8 | **Rinku Singh** | 75.49 | 164 | 45 | 12 | 3.6 | 100.0 | 123.8 | 108.5 | 107.1 | **23.1%** |
| #9 | **George Dockrell** | 75.38 | 83 | 28 | 4 | 3.0 | 100.0 | 136.9 | 147.7 | 200.0 | **40.2%** |
| #10 | **Patrick Cummins** | 74.77 | 109 | 31 | 8 | 3.5 | 100.0 | 145.4 | 139.8 | 158.3 | **25.1%** |

---

## 2. Top 10 Bowlers Match Opportunity & Dispersion Audit

| Rank | Player | BoRS | High Balls | Matches | Meaningful (>=6b) | Balls/Match | Median Econ | Mean Econ | Std Econ | IQR Econ | Top 2 Share |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| #1 | **Tim Southee** | 90.69 | 64 | 19 | 3 | 3.4 | 2.0 | 3.7 | 4.9 | 6.0 | **57.1%** |
| #2 | **Keshav Maharaj** | 79.94 | 78 | 12 | 5 | 6.5 | 5.1 | 6.1 | 4.5 | 6.8 | **57.1%** |
| #3 | **Haris Rauf** | 78.84 | 105 | 19 | 8 | 5.5 | 6.0 | 7.2 | 5.2 | 5.0 | **33.3%** |
| #4 | **Mark Adair** | 74.70 | 71 | 17 | 3 | 4.2 | 4.5 | 3.8 | 3.5 | 6.0 | **66.7%** |
| #5 | **Shoriful Islam** | 74.01 | 61 | 16 | 6 | 3.8 | 4.9 | 5.6 | 6.2 | 7.8 | **40.0%** |
| #6 | **Harshit Rana** | 72.85 | 157 | 30 | 12 | 5.2 | 7.1 | 7.1 | 5.7 | 6.8 | **18.2%** |
| #7 | **Wanindu Hasaranga** | 70.04 | 192 | 34 | 15 | 5.7 | 6.0 | 6.1 | 4.1 | 4.9 | **28.6%** |
| #8 | **Trent Boult** | 69.72 | 177 | 45 | 10 | 3.9 | 4.5 | 5.7 | 5.5 | 8.0 | **37.5%** |
| #9 | **Simarjeet Singh** | 69.40 | 60 | 9 | 4 | 6.7 | 8.7 | 8.9 | 5.9 | 7.6 | **75.0%** |
| #10 | **Lungi Ngidi** | 68.89 | 111 | 25 | 6 | 4.4 | 6.0 | 6.4 | 5.9 | 5.0 | **28.6%** |

| #24 | **Jasprit Bumrah** | 59.29 | 167 | 31 | 12 | 5.4 | 6.0 | 5.6 | 4.5 | 5.8 | **40.0%** |

---

## 3. Methodological Assessment: Should a Consistency Penalty Be Introduced?

### Verdict: **NO to Penalties; YES to Opportunity Eligibility Filters**
1. **Penalizing Top-Heavy Output Punishes Clutch Match-Winning:** In tournament T20 cricket, winning two high-pressure matches single-handedly is immensely valuable. Introducing an arbitrary penalty that discounts a player's best matches creates perverse statistical incentives.
2. **The Clean Solution:** Require players to demonstrate repeated exposure by adding a minimum match threshold (e.g., $M \ge 15$). This naturally prevents small-sample outliers like Simarjeet Singh (9 matches) from entering Tier 1 without distorting the scoring mechanics.

---
*(Report generated automatically by Step 11.2 Independent Audit - Investigation 4)*