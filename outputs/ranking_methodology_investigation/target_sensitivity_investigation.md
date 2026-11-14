# Investigation 8: Target Reconstruction Sensitivity

## Executive Summary

This investigation evaluates the stability of the official player reliability rankings against known target reconstruction issues identified in Step 3 and validated in Step 6.2 and Step 10.

Specifically, we audit the impact of **4,177 clean deliveries** across **38 matches** where the second innings target was understated due to missing historical boundary or extra records.

### Key Audit Conclusions:
1. **Extraordinary Methodological Robustness:**
   - **Batters:** Spearman rank correlation is **$\rho = 0.9945$** across all qualified Tier 1 batters. Top 10 overlap is **10/10 (100%)** and Top 20 overlap is **20/20 (100%)**.
   - **Bowlers:** Spearman rank correlation is **$\rho = 0.9852$**. Top 10 overlap is **9/10 (90%)** and Top 20 overlap is **19/20 (95%)**.
2. **Phase Concentration of Flagged Deliveries:**
   - Middle Overs: **2,081 deliveries (49.8%)**
   - Powerplay: **1,427 deliveries (34.2%)**
   - Death Overs: **669 deliveries (16.0%)**
   - Over **84.0%** of all flagged deliveries are concentrated in the Powerplay and Middle Overs. Death Overs (where high pressure is most intense) are largely untouched.
3. **Disproportionate Exposure by Player Type:**
   - Spinners (Wanindu Hasaranga: 96 balls, Noor Ahmad: 84 balls, Kuldeep Yadav: 84 balls, Theekshana: 72 balls) and top-order anchors (Pathum Nissanka: 215 balls, Jos Buttler: 202 balls) account for the largest exposure to flagged matches.
4. **The Shoriful Islam Threshold Cliff Effect:**
   - The single change in the Bowler Top 10 is **Shoriful Islam** (61 balls in baseline $\rightarrow$ Rank #5). Four of his balls occurred in flagged matches. When excluded, his sample fell to 57 balls, dropping him below the 60-ball cliff into Tier 2. This promoted **Maheesh Theekshana** into Rank #10. The top 4 bowlers (Southee, Maharaj, Rauf, Adair) remained completely invariant.

---

## 1. Distribution of 4,177 Flagged Deliveries

| Phase | Flagged Deliveries | Percentage | Contextual Role |
| :--- | :---: | :---: | :--- |
| **Middle Overs (Overs 7-15)** | 2,081 | 49.82% | Dominated by spin bowling and run accumulation |
| **Powerplay (Overs 1-6)** | 1,427 | 34.16% | Opening pace attacks and field restriction attacks |
| **Death Overs (Overs 16-20)** | 669 | 16.02% | High-leverage end-game finishing |
| **Total Flagged Deliveries** | **4,177** | **100.00%** | **Innings 2 only across 38 matches** |

---

## 2. Sensitivity Correlation and Overlap

| Metric | Batting Model | Bowling Model | Threshold Benchmark | Audit Status |
| :--- | :---: | :---: | :---: | :---: |
| **Spearman Rank Correlation ($\rho$)** | **0.9945** | **0.9852** | $\ge 0.95$ | **PASS** |
| **Top 10 Roster Overlap** | **10/10 (100%)** | **9/10 (90%)** | $\ge 90\%$ | **PASS** |
| **Top 20 Roster Overlap** | **20/20 (100%)** | **19/20 (95%)** | $\ge 90\%$ | **PASS** |

---

## 3. Players Disproportionately Affected

### Top 8 Batters with Flagged Exposure:
| Player | High Pressure Balls | Flagged Deliveries Faced | Flagged Share |
| :--- | :---: | :---: | :---: |
| **Pathum Nissanka** | 49 | 215 | 81.4% |
| **Jos Buttler** | 80 | 202 | 71.6% |
| **Kusal Mendis** | 24 | 123 | 83.7% |
| **Yashasvi Jaiswal** | 63 | 102 | 61.8% |
| **Shubman Gill** | 29 | 98 | 77.2% |
| **Shreyas Iyer** | 83 | 96 | 53.6% |
| **Sai Sudharsan** | 50 | 91 | 64.5% |
| **Sanju Samson** | 91 | 84 | 48.0% |

### Top 8 Bowlers with Flagged Exposure:
| Player | High Pressure Balls | Flagged Legal Balls Bowled | Flagged Share |
| :--- | :---: | :---: | :---: |
| **Wanindu Hasaranga** | 198 | 96 | 32.7% |
| **Noor Ahmad** | 177 | 84 | 32.2% |
| **Kuldeep Yadav** | 172 | 84 | 32.8% |
| **Maheesh Theekshana** | 219 | 72 | 24.7% |
| **Yuzvendra Chahal** | 186 | 72 | 27.9% |
| **Rashid Khan** | 254 | 67 | 20.9% |
| **Arshdeep Singh** | 427 | 66 | 13.4% |
| **Ravi Bishnoi** | 231 | 66 | 22.2% |

---

## 4. Analytical Verdict on Target Sensitivity

1. **Data Integrity Conclusion:**
   - The target reconstruction anomaly in 38 matches does **not** compromise the integrity or validity of the official v2.0 rankings.
   - With rank correlations of $0.9945$ (batters) and $0.9852$ (bowlers), player reliability scores are extraordinarily stable against target noise.
2. **Vulnerability to Threshold Discontinuities:**
   - The only vulnerability exposed by sensitivity analysis is the **hard 60-ball cliff**. Shoriful Islam fell from #5 to Tier 2 solely because 4 deliveries dropped him from 61 to 57 balls.
   - This reinforces Investigation 2's recommendation to replace hard cutoff cliffs with continuous sigmoidal weighting in future iterations.

---
*(Report generated automatically by Step 11 Investigation 8)*