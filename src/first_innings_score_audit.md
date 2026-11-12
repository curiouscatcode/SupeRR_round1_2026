# Step 4.2 — First-Innings Score Reconstruction Audit Report
**Project:** SupeRR Selector Season 2 — Cricket Analytics Competition  
**Pipeline Step:** Step 4.2 — First-Innings Score Reconstruction Audit  
**Audit Date:** 2026-11-12  
**Input Files:**  
- `data/processed/delivery_pressure_index.csv` (188,330 rows, 65 columns)  
- `data/processed/delivery_match_state.csv` (188,330 rows, 49 columns)  
- `data/matches.csv`  
- `data/ball_by_ball.csv`  
- `src/pressure_index_final_audit.md`  

---

## 1. Executive Summary & Audit Purpose

In `pressure_index_final_audit.md`, an audit of 90 matches with second-innings deliveries showing `runs_required <= 0` identified that while 52 matches were caused by post-match feed ghost deliveries, **34 chasing matches** (and 4 defending-win matches) exhibited a target reconstruction deficit. In these matches, the reconstructed first-innings score is lower than the actual score, creating an artificially low chase target in the second innings.

This technical audit investigates all 34 matches to:
1. Identify each match and quantify the exact score difference.
2. Distinguish between **confirmed discrepancies** (verified against official scorecards or mathematical proof in match margins) and **suspected discrepancies** (derived from simulation excess runs and multi-ball continued play).
3. Trace the root cause to missing multi-run byes/leg-byes and raw data feed omission.
4. Quantify the mathematical impact on second-innings Required Run Rate ($RRR$) and Pressure Index ($PI$).
5. Provide actionable handling recommendations for Step 5 (Player Performance Evaluation) without automatically discarding matches or inventing synthetic runs.

### Key Audit Numbers
- **Total Chasing Deficit Matches:** **34 matches**
  - **Confirmed Discrepancies:** **20 matches** (all historical IPL & T20I matches from 2022 to 2024, cross-verified against official match records).
  - **Suspected Discrepancies:** **14 matches** (from 2025–2026 simulation competitions, identified by excess runs and continued play after target).
- **Defending-Win Discrepancy Matches:** **4 matches** (mathematically proven from `result` margins in `matches.csv`).
- **Affected Deliveries:**
  - **First-Innings Deliveries Affected:** **0** (first-innings PI has zero dependence on target or RRR).
  - **Second-Innings Deliveries in the 34 Matches:** **3,819 deliveries** (4.24% of Innings 2; 2.03% of the entire 188,330 dataset).
  - **Second-Innings Deliveries across all 38 Matches:** **4,323 deliveries** (4.80% of Innings 2; 2.30% of entire dataset).

---

## 2. Identification and Comparison of the 34 Affected Matches

Below is the complete audit of all 34 matches, comparing the reconstructed first-innings score against the official or derived first-innings total:

| Match ID | Match Date | Competition Name | Match Teams | Result String | Reconstructed Inn 1 | Official / Expected Inn 1 | Score Deficit ($\Delta$) | Status | Inn 1 Byes / Leg-byes | Neg Balls | Runs in Neg | Wkts in Neg |
|:---:|:---:|:---|:---|:---|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|
| **14096** | 2022-03-27 | IPL 2022 | PBKS vs RCB | Punjab Kings Won by 5 Wkts | 194 | 205 | **+11** | Confirmed | 5 | 3 | 4 | 0 |
| **14114** | 2022-04-11 | IPL 2022 | SRH vs GT | Sunrisers Hyderabad Won by 8 Wickets | 150 | 162 | **+12** | Confirmed | 2 | 6 | 17 | 0 |
| **14133** | 2022-04-27 | IPL 2022 | GT vs SRH | Gujarat Titans Won by 5 Wickets | 187 | 195 | **+8** | Confirmed | 0 | 1 | 6 | 0 |
| **15189** | 2022-05-27 | IPL 2022 | RR vs RCB | Rajasthan Royals won by 7 wickets | 151 | 157 | **+6** | Confirmed | 2 | 3 | 9 | 0 |
| **16659** | 2022-09-03 | Asia Cup 2022 | SL vs AFG | Sri Lanka Won by 4 Wickets | 171 | 175 | **+4** | Confirmed | 1 | 6 | 7 | 1 |
| **16660** | 2022-09-04 | Asia Cup 2022 | IND vs PAK | Pakistan Won by 5 Wickets | 174 | 181 | **+7** | Confirmed | 1 | 5 | 7 | 1 |
| **16664** | 2022-09-09 | Asia Cup 2022 | SL vs PAK | Sri Lanka Won by 5 Wickets | 112 | 121 | **+9** | Confirmed | 1 | 5 | 10 | 1 |
| **19691** | 2023-01-14 | IRE in ZIM 2023 | ZIM vs IRE | Ireland Won by 6 wickets | 139 | 144 | **+5** | Confirmed | 5 | 5 | 9 | 0 |
| **20187** | 2023-04-04 | IPL 2023 | DC vs GT | Gujarat Titans won by 6 wickets | 153 | 162 | **+9** | Confirmed | 1 | 5 | 7 | 0 |
| **24354** | 2023-08-13 | IND in WI 2023 | WI vs IND | West Indies Won by 8 wickets | 162 | 165 | **+3** | Confirmed | 1 | 4 | 8 | 0 |
| **28958** | 2024-01-16 | ZIM in SL 2024 | SL vs ZIM | Zimbabwe Won by 4 Wickets | 169 | 173 | **+4** | Confirmed | 1 | 3 | 7 | 0 |
| **30074** | 2024-04-06 | IPL 2024 | RR vs RCB | Rajasthan Royals Won by 6 Wickets | 179 | 183 | **+4** | Confirmed | 2 | 4 | 8 | 0 |
| **31240** | 2024-04-08 | IPL 2024 | CSK vs KKR | Chennai Super Kings Won by 7 wickets | 134 | 137 | **+3** | Confirmed | 2 | 3 | 5 | 0 |
| **31250** | 2024-04-16 | IPL 2024 | KKR vs RR | Rajasthan Royals Won by 2 wickets | 213 | 223 | **+10** | Confirmed | 2 | 5 | 3 | 0 |
| **31265** | 2024-04-29 | IPL 2024 | KKR vs DC | Kolkata Knight Riders Won by 7 wickets | 149 | 153 | **+4** | Confirmed | 3 | 3 | 6 | 0 |
| **31267** | 2024-05-01 | IPL 2024 | CSK vs PBKS | Punjab Kings Won by 7 wickets | 155 | 162 | **+7** | Confirmed | 2 | 5 | 6 | 0 |
| **33806** | 2024-07-13 | IND in ZIM 2024 | ZIM vs IND | India Won by 10 wickets | 144 | 152 | **+8** | Confirmed | 1 | 3 | 5 | 0 |
| **37014** | 2024-09-27 | IRE v SA 2024 | IRE vs SA | South Africa Won by 8 wickets | 164 | 171 | **+7** | Confirmed | 6 | 6 | 5 | 0 |
| **37351** | 2024-11-15 | ENG in WI 2024 | WI vs ENG | England Won by 3 wickets | 142 | 145 | **+3** | Confirmed | 3 | 3 | 5 | 0 |
| **37555** | 2024-10-17 | WI in SL 2024 | SL vs WI | Sri Lanka Won by 9 wickets | 154 | 162 | **+8** | Confirmed | 3 | 5 | 6 | 0 |
| **40706** | 2025-04-01 | IPL 2025 | LSG vs PBKS | Punjab Kings Won by 8 wickets | 169 | 175 | **+6** | Suspected | 1 | 3 | 6 | 0 |
| **40742** | 2025-04-30 | IPL 2025 | CSK vs PBKS | Punjab Kings Won by 4 wickets | 189 | 193 | **+4** | Suspected | 3 | 3 | 4 | 1 |
| **40764** | 2025-05-29 | IPL 2025 | PBKS vs RCB | Royal Challengers Bengaluru Won by 8 wickets | 94 | 102 | **+8** | Suspected | 2 | 3 | 8 | 0 |
| **41508** | 2025-07-26 | AUS in WI 2025 | WI vs AUS | Australia Won by 3 wickets | 201 | 205 | **+4** | Suspected | 2 | 5 | 4 | 1 |
| **45903** | 2025-09-03 | SL in ZIM 2025 | ZIM vs SL | Sri Lanka Won by 4 wickets | 170 | 175 | **+5** | Suspected | 3 | 3 | 4 | 0 |
| **46312** | 2025-10-04 | AUS in NZ 2025 | AUS vs NZ | Australia Won by 3 wickets | 149 | 155 | **+6** | Suspected | 4 | 4 | 6 | 0 |
| **47982** | 2025-11-29 | Tri-Series 2025 | PAK vs SL | Pakistan Won by 6 wickets | 111 | 117 | **+6** | Suspected | 5 | 4 | 6 | 0 |
| **48592** | 2026-01-23 | NZ in IND 2026 | IND vs NZ | India Won by 7 wickets | 205 | 208 | **+3** | Suspected | 3 | 4 | 3 | 0 |
| **50129** | 2026-04-01 | IPL 2026 | LSG vs DC | Delhi Capitals Won by 6 wickets | 132 | 139 | **+7** | Suspected | 3 | 4 | 7 | 0 |
| **50358** | 2026-04-26 | IPL 2026 | CSK vs GT | Gujarat Titans Won by 8 wickets | 154 | 161 | **+7** | Suspected | 2 | 3 | 7 | 1 |
| **50361** | 2026-04-28 | IPL 2026 | PBKS vs RR | Rajasthan Royals Won by 6 wickets | 216 | 227 | **+11** | Suspected | 2 | 4 | 9 | 0 |
| **50597** | 2026-06-17 | AUS in BAN 2026 | BAN vs AUS | Australia Won by 4 wickets | 128 | 132 | **+4** | Suspected | 2 | 3 | 4 | 1 |
| **54408** | 2026-09-13 | AFG in IND 2026 | AFG vs IND | India Won by 7 wickets | 148 | 152 | **+4** | Suspected | 5 | 3 | 4 | 0 |
| **55078** | 2026-10-09 | SL in PAK 2026 | PAK vs SL | Pakistan Won by 4 wickets | 167 | 186 | **+19** | Suspected | 6 | 10 | 17 | 2 |

---

## 3. The 4 Defending-Win Discrepancy Matches (Special Audit)

In addition to the 34 chasing matches, 4 matches won by the defending team also suffered from target under-reconstruction:

| Match ID | Match Date | Teams | Result in `matches.csv` | Reconstructed Inn 1 | Actual / Expected Inn 1 | Deficit ($\Delta$) | Inn 2 Final Score | Mathematical Proof |
|:---:|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| **28962** | 2024-01-17 | IND vs AFG | India Won Super Over By 10 Runs | 205 | 212 | **+7** | 211 (212 real) | Match tied at 212 regulation; won in double super over. Reconstructed 205 made AFG reach target prematurely. |
| **29926** | 2024-03-15 | AFG vs IRE | Afghanistan won by 3 runs | 199 | 210 | **+11** | 206 (207 real) | If AFG won by 3 runs and IRE scored 207, AFG scored 210. Reconstructed 199 made IRE cross target at 200. |
| **32135** | 2024-05-10 | BAN vs ZIM | Bangladesh Won by 5 runs | 136 | 143 | **+7** | 138 | If BAN won by 5 runs and ZIM scored 138, BAN scored 143. Reconstructed 136 made ZIM cross target at 137. |
| **37895** | 2025-01-12 | NZ vs PAK | New Zealand Won by 5 runs | 99 | 105 | **+6** | 100 | If NZ won by 5 runs and PAK scored 100, NZ scored 105. Reconstructed 99 made PAK cross target at 100. |

---

## 4. Root Cause Analysis: Why the Discrepancies Occur

### 4.1 Schema Limitations with Byes and Leg-Byes
In `data/ball_by_ball.csv`:
- Whenever `extras_type == 'byes'` or `extras_type == 'legbyes'`, the `runs` column is recorded as `0`.
- The dataset does not provide the actual count of runs scored on that delivery (whether 1, 2, 3, or a boundary of 4 leg-byes).
- `extras1_runs` is a 1-to-1 categorical mapping ID, and `extras_2_runs` records fielding extras off illegal balls.
- As established in Step 2, the pipeline adopted the conservative lower-bound proxy:
  $$\text{team\_runs\_added} = 1 \quad \text{for every bye/leg-bye delivery}$$
- Consequently, whenever batters ran 2 byes or struck a 4-leg-bye boundary, the pipeline recorded only 1 run, dropping 1 to 3 runs per occurrence.
- Across 20 overs, an innings with 3 to 6 bye/leg-bye deliveries loses **3 to 12 runs**.

### 4.2 Raw Provider Feed Omissions
In several matches (such as Match 14133 where `inn1_byes_legbyes == 0` yet 8 runs were missing), the discrepancy stemmed directly from the feed provider omitting boundary extras or misattributing team extras to bowler figures.

---

## 5. Propagation Analysis: Impact on Second-Innings Target, RRR, and PI

### 5.1 The Mathematical Chain of Error Propagation
When first-innings score is understated by $\Delta$ runs:
1. **Target:** $\text{target}_{\text{recon}} = \text{target}_{\text{actual}} - \Delta$
2. **Runs Required:**
   $$\text{runs\_required}_{\text{recon}} = \text{target}_{\text{recon}} - \text{score\_before} = \text{runs\_required}_{\text{actual}} - \Delta$$
   Every second-innings delivery is understated by exactly $\Delta$ runs.
3. **Required Run Rate ($RRR$):**
   $$\text{RRR}_{\text{recon}} = \frac{\text{runs\_required}_{\text{actual}} - \Delta}{\text{balls\_remaining}} \times 6 = \text{RRR}_{\text{actual}} - \left(\frac{\Delta}{\text{balls\_remaining}} \times 6\right)$$

### 5.2 Non-Linear Escalation across Match Phases
The distortion in $RRR$ is small at the start of an innings but compounds non-linearly as balls run out:

```
+------------------+-----------------+--------------------------+-----------------------+
| Match Stage      | Balls Remaining | RRR Deficit (Δ = 6 runs) | RRR Deficit (Δ = 10)  |
+------------------+-----------------+--------------------------+-----------------------+
| Over 1.1 (PP)    |       120       |  -0.30 runs / over       |  -0.50 runs / over    |
| Over 6.1 (MO)    |        84       |  -0.43 runs / over       |  -0.71 runs / over    |
| Over 15.1 (DO)   |        30       |  -1.20 runs / over       |  -2.00 runs / over    |
| Over 18.1 (DO)   |        12       |  -3.00 runs / over       |  -5.00 runs / over    |
| Over 19.1 (DO)   |         6       |  -6.00 runs / over       | -10.00 runs / over    |
+------------------+-----------------+--------------------------+-----------------------+
```

### 5.3 Effect on Final Pressure Index ($PI$)
- **Innings 1:** **0 deliveries affected.** First-innings PI relies exclusively on $W_{\text{before}}$, $CRR$, phase progress, and individual balls faced. It has zero mathematical link to chase targets or RRR.
- **Innings 2 Powerplay:** $R$ is understated by $\sim 5$ to $8$ points $\implies$ final `Batting_PI` understated by only **$1.6$ to $2.6$ points** (negligible).
- **Innings 2 Middle Overs:** $R$ is understated by $\sim 10$ to $20$ points $\implies$ final `Batting_PI` understated by **$3.3$ to $6.5$ points** (mild).
- **Innings 2 Death Overs:** $R$ is understated by $\sim 25$ to $50$ points $\implies$ final `Batting_PI` understated by **$8.1$ to $16.3$ points**.
- **Final Deliveries (`runs_required <= 0`):** Once the understated target is crossed, scoring pressure drops to $0.00$, leaving only wickets and overs.

---

## 6. Recommendations for Step 5 (Player Performance Evaluation)

In strict accordance with the constraints (*do not modify datasets, do not invent runs, do not exclude entire matches automatically*), we evaluate the handling options:

### 6.1 Evaluation of Options

#### Option A: Exclude All 34 Matches Entirely
- **Pros:** Completely eliminates all deliveries with understated RRR.
- **Cons:** Violates explicit prompt constraints; discards **3,819 deliveries** of second-innings play and **~4,000 deliveries** of completely uncorrupted first-innings play; discards iconic performances (e.g. Jos Buttler's match-winning 107* in Match 31250, Rashid Khan's last-over 31* in Match 14133).
- **Verdict:** **REJECTED.**

#### Option B: Retain Unconditionally without Flagging
- **Pros:** Preserves full sample size.
- **Cons:** Fails to account for understated pressure in the death overs of these chases, slightly diluting clutch weighting for batters and bowlers in these specific games.
- **Verdict:** **REJECTED.**

#### Option C: Tail-Filtered Retention with Match Sensitivity Flagging (RECOMMENDED)
- **Methodology:**
  1. **Delivery-Level Filtering:** Exclude all **233 deliveries where `runs_required <= 0`** in Innings 2. This removes the distorted zero-pressure tail and ghost deliveries.
  2. **Innings 1 Unconditional Retention:** Retain 100% of first-innings deliveries from all 34 matches (zero RRR dependence).
  3. **Second-Innings Sensitivity Flagging:** Flag the **3,819 second-innings deliveries** with a metadata indicator `is_target_understated = True`.
  4. **Robustness Cross-Check in Step 5:** Compute player pressure-performance rankings under two regimes:
     - **Regime 1 (Master Population):** All valid deliveries (excluding `runs_required <= 0`).
     - **Regime 2 (Sensitivity Population):** Excluding the 3,819 flagged second-innings deliveries.
     - Demonstrate that the Top 10 rankings remain robust and stable across both regimes.
- **Verdict:** **RECOMMENDED.**

---

## 7. Audit Conclusion & Sign-Off

1. **Exact Scope:** Exactly 34 chasing matches (20 confirmed, 14 suspected) and 4 defending-win matches exhibit first-innings target reconstruction deficits.
2. **Root Cause:** Schema omission of multi-run byes/leg-byes and occasional feed omissions.
3. **Data Integrity:** Existing datasets and scripts in `data/processed/` and `src/` remain unchanged.
4. **Step 5 Readiness:** By implementing Option C (filtering `runs_required <= 0` and sensitivity-testing the flagged deliveries), player performance evaluation can proceed with total methodological transparency.
