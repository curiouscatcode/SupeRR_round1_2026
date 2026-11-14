# Investigation 4 — Ranking Consistency & Top 10 Discrepancy Resolution

## Executive Verdict: **RESOLVED — PREVIOUS NARRATIVE CLAIM INCORRECT (TRANSCRIPTION ERROR IDENTIFIED)**

---

## 1. Discrepancy Root Cause Analysis

### The Reported Inconsistency:
- In Step 12.5, Section 2.2 of `step_12_5_final_audit_report.md` presented a narrative table claiming the Tier 1 Top 3 batters were **Heinrich Klaasen, Suryakumar Yadav, and Nicholas Pooran**.
- In Section 3.2, it presented a table claiming the Tier 1 Top 3 bowlers were **Mohsin Khan, Sunil Narine, and Matheesha Pathirana**.
- However, authoritative project records from Step 6.2 establish that the official Tier 1 Top 3 begins with **MS Dhoni, Shashank Singh, and Shivam Dube** (Batting), and **Tim Southee, Keshav Maharaj, and Haris Rauf** (Bowling).

### Forensic Cause of the Discrepancy:
1. **Code vs Narrative Divergence:**
   - The Python code in Step 12 (`exp12_1_batting_formula.py`) and Step 12.5 (`audit_12_1_batting_formula.py`) **computed the exact correct mathematical results** from `data/processed/batter_reliability_rankings.csv`.
   - The reported Spearman rank correlations ($\rho = 0.9818$ across 816 batters; $\rho = 0.9885$ across Tier 1) and the Top 10 overlap ($10/10$ in batting, $9/10$ in bowling) were mathematically verified from the source code.
2. **Manual Synthesis Error in Markdown Report:**
   - When the agent authored `step_12_5_final_audit_report.md`, instead of inserting the output of `t1_df.sort_values('tier1_rank').head(10)`, the author manually transcribed a synthetic table of marquee T20 names (Klaasen, Suryakumar, Pooran, Miller, Maxwell... and Mohsin Khan, Narine, Pathirana...).
   - Searching the entire repository confirms that the synthetic score numbers ($75.98$, $75.05$, $72.80$) **never existed in any computed CSV file**; they appeared solely in the markdown narrative.
3. **Resolution:**
   - This audit formally repudiates the synthetic narrative table.
   - The true underlying data, rankings, and mathematical correlations are completely reconciled and verified below.

---

## 2. Authoritative Reconciliation Table

| Comparison                                      | Official source                                | Experimental source                                                                          | Population                               | Eligibility rule                         | Verified Top 10 overlap   | Verified Official Top 3                          | Verified Exp Top 3                               | Status                                                   |
|:------------------------------------------------|:-----------------------------------------------|:---------------------------------------------------------------------------------------------|:-----------------------------------------|:-----------------------------------------|:--------------------------|:-------------------------------------------------|:-------------------------------------------------|:---------------------------------------------------------|
| Batting Formula (Exp 12.1 vs Official v2.0)     | data/processed/batter_reliability_rankings.csv | outputs/step_12_experimental_models/exp12_1_batting_formula/exp12_1_batting_rankings.csv     | Full Population (N=816) / Tier 1 (N=116) | N >= 60 high-pressure balls faced        | 10/10 (100.0%)            | 1. MS Dhoni, 2. Shashank Singh, 3. Shivam Dube   | 1. MS Dhoni, 2. Shivam Dube, 3. Shashank Singh   | RESOLVED (Previous Report Contained Transcription Error) |
| Bowling Containment (Exp 12.2 vs Official v2.0) | data/processed/bowler_reliability_rankings.csv | outputs/step_12_experimental_models/exp12_2_bowling_containment/exp12_2_bowling_rankings.csv | Full Population (N=589) / Tier 1 (N=113) | N >= 60 high-pressure legal balls bowled | 9/10 (90.0%)              | 1. Tim Southee, 2. Keshav Maharaj, 3. Haris Rauf | 1. Tim Southee, 2. Mark Adair, 3. Keshav Maharaj | RESOLVED (Previous Report Contained Transcription Error) |

---

## 3. Authoritative Tier 1 Top 10 Batters (Official v2.0 vs Experimental BRS_3)

| Official Rank | Player Name | High Balls | Official BRS | Exp BRS_3 | Exp Rank | Rank Delta | Notes |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | Mahendra Singh Dhoni | 194 | 95.05 | 93.20 | 1 | +0 | Retained in Top 10 |
| **2** | Shashank Singh | 135 | 84.04 | 81.39 | 3 | -1 | Retained in Top 10 |
| **3** | Shivam Dube | 160 | 82.97 | 82.01 | 2 | +1 | Retained in Top 10 |
| **4** | Shubham Dubey | 69 | 80.82 | 80.02 | 5 | -1 | Retained in Top 10 |
| **5** | Cameron Green | 78 | 80.70 | 80.85 | 4 | +1 | Retained in Top 10 |
| **6** | Vijay Shankar | 65 | 78.02 | 78.79 | 6 | +0 | Retained in Top 10 |
| **7** | Jitesh Sharma | 97 | 77.01 | 75.83 | 9 | -2 | Retained in Top 10 |
| **8** | Rinku Singh | 177 | 75.49 | 76.60 | 7 | +1 | Retained in Top 10 |
| **9** | George Dockrell | 100 | 75.38 | 76.06 | 8 | +1 | Retained in Top 10 |
| **10** | Patrick Cummins | 131 | 74.77 | 72.85 | 10 | +0 | Retained in Top 10 |

**Verified Top 10 Overlap:** Exactly **10 / 10 (100.0%)**.
- Order under Official v2.0: Dhoni, Shashank Singh, Shivam Dube, Shubham Dubey, Cameron Green, Vijay Shankar, Jitesh Sharma, Rinku Singh, George Dockrell, Patrick Cummins.
- Order under Exp BRS_3: Dhoni, Shivam Dube, Shashank Singh, Cameron Green, Shubham Dubey, Vijay Shankar, Rinku Singh, George Dockrell, Jitesh Sharma, Patrick Cummins.
- Shivam Dube climbs to #2 (higher survival rate $94.4\%$); Shashank Singh moves to #3 ($92.6\%$ survival).

---

## 4. Authoritative Tier 1 Top 10 Bowlers (Official v2.0 vs Experimental BoRS_Contain)

| Official Rank | Player Name | High Balls | Official BoRS | Exp BoRS | Exp Rank | Rank Delta | Movement Summary |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | Tim Southee | 64 | 90.69 | 88.18 | 1 | +0 | Retained |
| **2** | Keshav Maharaj | 78 | 79.94 | 77.84 | 3 | -1 | Retained |
| **3** | Haris Rauf | 106 | 78.84 | 76.98 | 4 | -1 | Retained |
| **4** | Mark Adair | 71 | 74.70 | 78.78 | 2 | +2 | Retained |
| **5** | Shoriful Islam | 61 | 74.01 | 71.06 | 6 | -1 | Retained |
| **6** | Harshit Rana | 158 | 72.85 | 69.73 | 7 | -1 | Retained |
| **7** | Wanindu Hasaranga | 198 | 70.04 | 72.16 | 5 | +2 | Retained |
| **8** | Trent Boult | 180 | 69.72 | 67.79 | 10 | -2 | Retained |
| **9** | Simarjeet Singh | 60 | 69.40 | 64.81 | 12 | -3 | Exits Top 10 (#12) |
| **10** | Lungi Ngidi | 110 | 68.89 | 68.45 | 8 | +2 | Retained |

**Verified Top 10 Overlap:** Exactly **9 / 10 (90.0%)**.
- **Player Entering Top 10:** Maheesh Theekshana (Official #12 $\to$ Exp #9; Economy $6.82$, $11.8\%$ boundaries).
- **Player Exiting Top 10:** Simarjeet Singh (Official #9 $\to$ Exp #12; higher boundary concession).

---

## 5. Final Mathematical Certification

1. **Full-Population Batting Stability ($N=816$):**
   - Spearman rank correlation: **$\rho = 0.9818$**.
   - Pearson score correlation: **$r = 0.9859$**.
2. **Full-Population Bowling Stability ($N=589$):**
   - Spearman rank correlation: **$\rho = 0.9634$**.
   - Pearson score correlation: **$r = 0.9712$**.
3. **Top 10 Consistency:**
   - With identical population filtering (Tier 1 Qualified, $N \ge 60$ balls), the code produces 10/10 overlap in batting and 9/10 overlap in bowling.
   - The previous narrative discrepancy is completely explained, documented, and corrected.
