# Investigation 7: Match-to-Match Consistency

## Executive Summary

A foundational question in player reliability evaluation is whether high-ranking players demonstrate **consistent dependability across multiple matches** or whether their aggregate scores are inflated by a few exceptional, high-leverage performances.

This investigation calculated match-level delivery distributions, distinct match counts, match-to-match standard deviations, and top-match reliance across all 116 Tier 1 batters and 113 Tier 1 bowlers.

### Major Findings:
1. **The 'Outlier Dependency' Flaw in Aggregate Ranking:**
   - Because the official v2.0 ranking formula evaluates pooled aggregate numbers (total runs, total balls, total wickets), it cannot distinguish a player who contributes reliably in 80% of matches from a player who explodes in 2 matches and is ineffective in the rest.
   - **Shubham Dubey (#4 Batter):** Qualified with 55 high-pressure balls across only 14 matches. Over **53.1% of his entire high-pressure run total** came from just **two matches** (31.6% in a single match).
   - **Simarjeet Singh (#9 Bowler):** Qualified with 60 high-pressure balls across only **9 matches**. Over **75.0% of his wickets** came in just **two matches** (50.0% in a single match).
   - **Keshav Maharaj (#2 Bowler):** Over **57.1% of his wickets** came in just two matches across 12 games.
   - **Tim Southee (#1 Bowler):** Over **57.1% of his wickets** came in two matches across 19 games.
2. **Truly Consistent High-Sample Anchors:**
   - In contrast, players with high match counts exhibit low outlier dependence:
   - **MS Dhoni (#1 Batter):** 38 matches, Top 1 match = 9.4%, Top 2 matches = 18.5%. Demonstrates genuine repeated clutch execution.
   - **Rinku Singh (#8 Batter):** 45 matches, Top 1 match = 12.4%, Top 2 matches = 23.1%.
   - **Jasprit Bumrah (#24 Bowler):** 31 matches, median economy = 6.00 rpo, std = 4.5 rpo. Highly stable match-to-match containment.
   - **Wanindu Hasaranga (#7 Bowler):** 34 matches, Top 1 match = 14.3%, Top 2 matches = 28.6%.
3. **Match Exposure Disparity:**
   - Tier 1 players range from as few as 8 matches to as many as 56 matches under high pressure. Aggregating them without a minimum match count threshold amplifies small-sample volatility.

---

## 1. Top 10 Batters Match Consistency

| Rank | Player | BRS | High Balls | Matches | Balls/Match | Median SR | SR Std | Top 1 Match % | Top 2 Matches % |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| #1 | **Mahendra Singh Dhoni** | 95.05 | 194 | 38 | 4.5 | 137.5 | 146.1 | 9.4% | 18.5% |
| #2 | **Shashank Singh** | 84.04 | 135 | 21 | 5.0 | 100.0 | 103.8 | 16.5% | 28.6% |
| #3 | **Shivam Dube** | 82.97 | 160 | 38 | 3.7 | 150.0 | 126.8 | 13.3% | 20.6% |
| #4 | **Shubham Dubey** | 80.82 | 69 | 14 | 3.9 | 100.0 | 123.8 | 31.6% | 53.1% |
| #5 | **Cameron Green** | 80.70 | 78 | 26 | 3.0 | 100.0 | 105.5 | 15.0% | 24.4% |
| #6 | **Vijay Shankar** | 78.02 | 65 | 12 | 4.8 | 129.2 | 71.7 | 20.0% | 36.7% |
| #7 | **Jitesh Sharma** | 77.01 | 97 | 29 | 2.8 | 100.0 | 131.3 | 14.1% | 24.2% |
| #8 | **Rinku Singh** | 75.49 | 177 | 45 | 3.6 | 100.0 | 108.5 | 12.4% | 23.1% |
| #9 | **George Dockrell** | 75.38 | 100 | 28 | 3.0 | 100.0 | 147.7 | 27.4% | 40.2% |
| #10 | **Patrick Cummins** | 74.77 | 131 | 31 | 3.5 | 100.0 | 139.8 | 14.9% | 25.1% |

---

## 2. Top 10 Bowlers Match Consistency

| Rank | Player | BoRS | High Balls | Matches | Balls/Match | Median Econ | Econ Std | Top 1 Match % | Top 2 Matches % |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| #1 | **Tim Southee** | 90.69 | 64 | 19 | 3.4 | 2.0 | 4.9 | 28.6% | 57.1% |
| #2 | **Keshav Maharaj** | 79.94 | 78 | 12 | 6.5 | 5.1 | 4.5 | 28.6% | 57.1% |
| #3 | **Haris Rauf** | 78.84 | 106 | 19 | 5.5 | 6.0 | 5.2 | 22.2% | 33.3% |
| #4 | **Mark Adair** | 74.70 | 71 | 17 | 4.2 | 4.5 | 3.5 | 33.3% | 66.7% |
| #5 | **Shoriful Islam** | 74.01 | 61 | 16 | 3.8 | 4.9 | 6.2 | 20.0% | 40.0% |
| #6 | **Harshit Rana** | 72.85 | 158 | 30 | 5.2 | 7.1 | 5.7 | 9.1% | 18.2% |
| #7 | **Wanindu Hasaranga** | 70.04 | 198 | 34 | 5.7 | 6.0 | 4.1 | 14.3% | 28.6% |
| #8 | **Trent Boult** | 69.72 | 180 | 45 | 3.9 | 4.5 | 5.5 | 25.0% | 37.5% |
| #9 | **Simarjeet Singh** | 69.40 | 60 | 9 | 6.7 | 8.7 | 5.9 | 50.0% | 75.0% |
| #10 | **Lungi Ngidi** | 68.89 | 110 | 25 | 4.4 | 6.0 | 5.9 | 14.3% | 28.6% |

| #24 | **Jasprit Bumrah** | 59.29 | 168 | 31 | 5.4 | 6.0 | 4.5 | 20.0% | 40.0% |

---

## 3. Analytical Answers on Match Consistency

1. **Do aggregate rankings hide inconsistent players?**
   - **Yes, significantly.** Players like Shubham Dubey (53.1% in 2 games) and Simarjeet Singh (75.0% in 2 games) achieved elite Tier 1 rankings based on a handful of high-leverage spikes, masking severe unreliability across other matches.
2. **How does match-to-match consistency differ from average performance?**
   - Average performance answers *'What was the pooled output?'* Consistency answers *'How dependable was the player across discrete match opportunities?'*
   - A team choosing a player for a playoff final needs high probability of acceptable execution, not a high aggregate boosted by a blowout win months earlier.
3. **Recommended Methodological Correction for v3.0:**
   - Introduce a dual qualification criterion: e.g. **60 high-pressure balls AND minimum 15 distinct high-pressure matches**.
   - Introduce a **Consistency Factor** or match-level median penalty that downweights players whose top 2 matches constitute $>40\%$ of total value.

---
*(Report generated automatically by Step 11 Investigation 7)*