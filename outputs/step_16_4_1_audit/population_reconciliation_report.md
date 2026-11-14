# Population Reconciliation Audit (Part D)

**Audit Date:** 2026-11-14  
**Auditor:** Independent Analytics Auditor  
**Scope:** Full Reconciliation of 188,097 Clean Deliveries vs 180,839 Batting Balls Faced  

---

## 1. Executive Summary & Exact Numerical Accounting

The project baseline consists of three primary delivery counts across the 789 core matches:
1. **188,097 Clean Active Deliveries:** All legitimate match deliveries after removing 233 dead tail deliveries.
2. **180,839 Active Batting Balls Faced:** Deliveries credited to the batter as a ball faced under cricket scoring laws.
3. **180,041 Active Bowling Legal Balls:** Deliveries credited to the bowler as a legal ball incrementing the over.

### Reconciliation Breakdown:
$$188,097 \text{ (Clean Deliveries)} - 7,258 \text{ (Wides)} = \mathbf{180,839\text{ (Batting Balls Faced)}}$$
$$188,097 \text{ (Clean Deliveries)} - 7,258 \text{ (Wides)} - 798 \text{ (No-Balls)} = \mathbf{180,041\text{ (Bowling Legal Balls)}}$$

Every single delivery in the difference between 188,097 and 180,839 is verified to be **100% WIDES** (`extras_type == 'wide'`). Exactly zero legal balls or no-balls were dropped.

---

## 2. Master Reconciliation Table

| Stage | Population Name | Deliveries Count | Delta from Clean | Definition & Governing Cricket Rule | Analytical Function |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1. | **Raw Reconstructed Deliveries** | 188,330 | 0 | Full 789 core 20-over matches (IPL & T20I, 2022-2026) | Database ingestion baseline |
| 2. | **Excluded Dead Tail Deliveries** | 233 | -233 | Innings 2 balls after target reached (runs_required <= 0) | Match already won; no valid tactical pressure |
| 3. | **Clean Active Deliveries Population** | 188,097 | -233 | Step 16 Baseline Clean Deliveries | Master denominator for all match-level delivery state |
| 4. | **Excluded Non-Batting Balls (Wides)** | 7,258 | -7,258 | Wides (extras_type == wide, exactly 7,258 balls) | Cannot be faced by batter under Law 22 (no shot played) |
| 5. | **Active Batting Balls Faced** | 180,839 | -7,258 | is_batter_ball_faced == True (Legal balls + No-balls) | Denominator for all batting stats (BRS3, SR, Survival, Batting PI) |
| 6. | **Excluded Illegal Bowling Balls (Wides + No-Balls)** | 8,056 | -8,056 | 7,258 wides + 544 Overstep no-balls + 254 other no-balls | Illegal deliveries that must be re-bowled |
| 7. | **Active Bowling Legal Balls Bowled** | 180,041 | -8,056 | is_legal_ball == True (Increments over counter) | Denominator for all bowling stats (BoRS, Economy, Dot%, Bowling PI) |

---

## 3. Breakdown of the 7,258 Wides Across Phases and Innings

| Innings | Powerplay (PP) | Middle Overs | Death Overs | Total Wides |
| :---: | :---: | :---: | :---: | :---: |
| Innings 1 | 1,049 (27.3%) | 1,398 (36.4%) | 1,391 (36.2%) | **3,838** |
| Innings 2 | 1,093 (32.0%) | 1,367 (40.0%) | 960 (28.1%) | **3,420** |
| **Total** | **2,142 (29.5%)** | **2,765 (38.1%)** | **2,351 (32.4%)** | **7,258 (100.0%)** |

---

## 4. Denominator Integrity and Verification

1. **Batting Statistics Denominator:**  
   - Under MCC Law 22 and official ICC T20 playing conditions, wides do not count as balls faced by the batter. Including wides in batting denominator would artificially deflate batter Strike Rate and distort balls-faced sample sizes.  
   - No-balls (Overstep / other, 798 balls) ARE credited as balls faced by the batter because the batter can score off them.  
   - Therefore, **180,839** is the exact, correct denominator for all batting performance, BRS3, and batting pressure analyses.

2. **Bowling Statistics Denominator:**  
   - Under MCC Law 21 and 22, neither wides nor no-balls count as legal balls toward the 6-ball over. Both must be re-bowled.  
   - Therefore, **180,041** is the exact, correct denominator for bowler overs bowled, economy rate, and dot-ball percentage.

3. **Audit Verification:** All prior scripts in Step 16 and Step 16.4 correctly filtered by `is_batter_ball_faced == 1` for batting analyses and `is_legal_ball == 1` for bowling analyses. The denominators are rigorously separated and mathematically reconciled.
