# Investigation 2 — Bowling Containment Methodology Resolution

## Executive Verdict: **RESOLVED WITH QUALIFICATIONS — PROVISIONALLY RETAIN OFFICIAL V2.0 PENDING MULTI-OBJECTIVE OPTIMIZATION**

---

## 1. Core Findings & Answers to Mandatory Questions

### Question 1: How much unique information do Dot Rate and Boundary Concession provide beyond Economy?
- **Finding:** **SUBSTANTIAL LINEAR REDUNDANCY (92.89% OVERLAP).**
- In Tier 1 ($N=113$), Boundary Concession Rate explains **79.88%** of Economy variance ($r = +0.8938$).
- Dot Ball Rate explains **20.94%** of Economy variance ($r = -0.4576$).
- A joint linear regression confirms that Boundary % and Dot % explain **92.89% of Economy Rate variance**.
- Economy is virtually a direct consequence of boundary suppression and dot-ball accumulation.
- The only unmeasured variance is **Running Balls % (1s, 2s, 3s)**, which averages 39.4% and absorbs the covariance between dots and boundaries on the multinomial simplex.

### Question 2: Does adding containment alongside Economy double-count run restriction?
- **Finding:** **YES — CREATES HEAVY COMPRESSION OF WICKETS.**
- The correlation between `Score_Econ` and `Score_Contain` is **$r = 0.8902$** ($R^2 = 79.24%$).
- In Step 12.2 (40% Econ + 30% Contain), nominal run-restriction weight is **70.0%**.
- Effective covariance decomposition reveals that run prevention commands **74.52% of total model variance**, compressing Wickets to just **10.12%**.
- In Step 12.5 Recalibrated (35% Econ + 25% Contain), run prevention commands **62.37%**, restoring Wickets to **15.71%**.

### Question 3: Does Economy's relationship with Dots and Boundaries change across match phases?
- **Finding:** **YES, BUT JOINT R² REMAINS > 90% ACROSS ALL PHASES.**
| Match Phase | Bowlers Analyzed | r(Econ, Bnd%) | r(Econ, Dot%) | r(Dot%, Bnd%) | Joint R² Explained |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Powerplay** | 290 | +0.9408 | -0.7012 | -0.5039 | **95.43%** |
| **Middle Overs** | 379 | +0.9186 | -0.5874 | -0.3182 | **94.07%** |
| **Death Overs** | 242 | +0.9250 | -0.5037 | -0.2504 | **93.45%** |

- In the Powerplay, boundaries are severely penalized due to field restrictions ($r = +0.89$).
- In Death overs, boundary prevention is paramount ($r = +0.88$), while dot balls become harder to produce.
- In all phases, joint $R^2$ exceeds $90\%$, confirming that containment metrics do not decouple from Economy across phases.

### Question 4: Does containment reward genuine control, or simply duplicate Economy?
- **Finding:** **REWARDS EVENT CONTROL AT THE MARGIN, BUT INTRODUCES SYSTEMIC BIAS.**
- Containment successfully elevates bowlers who suffocate batting line-ups through relentless pressure (Bumrah $+10$, Theekshana $+3$).
- However, because it heavily penalizes boundary concession, it treats a bowler who takes 3 wickets while conceding 2 boundaries far worse than a bowler who takes 0 wickets and concedes 1 boundary.

### Question 6 & 7: Wicket-taking representation and penalty on expensive strike bowlers
- **Finding:** **EXPENSIVE STRIKE BOWLERS DROP CATASTROPHICALLY.**
- Under Step 12.2, Expensive Strike Bowlers drop an average of **-18.0 ranks** (Mukesh Choudhary -30, Jacob Duffy -20, Gerald Coetzee -18).
- In T20 matches, taking wickets in overs 18–20 terminates an innings and ends chases. Compressing wickets to 15% (or 20% in 12.5) undervalues game-breaking breakthroughs.

---

## 2. Official v2.0 Top 10 Bowlers Under All Three Models

| Official Rank | Player Name | Balls | Official v2.0 BoRS | Exp 12.2 BoRS | Exp 12.2 Rank | Delta 12.2 | Recal 12.5 BoRS | Recal 12.5 Rank | Delta 12.5 | Bowler Archetype |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | Tim Southee | 64 | 90.69 | 88.18 | 1 | +0 | 88.75 | 1 | +0 | Elite Complete Bowler |
| **2** | Keshav Maharaj | 78 | 79.94 | 77.84 | 3 | -1 | 78.65 | 2 | +0 | Elite Complete Bowler |
| **3** | Haris Rauf | 106 | 78.84 | 76.98 | 4 | -1 | 77.62 | 3 | +0 | Elite Complete Bowler |
| **4** | Mark Adair | 71 | 74.70 | 78.78 | 2 | +2 | 77.25 | 4 | +0 | Balanced / Middle tier |
| **5** | Shoriful Islam | 61 | 74.01 | 71.06 | 6 | -1 | 70.98 | 6 | -1 | Elite Complete Bowler |
| **6** | Harshit Rana | 158 | 72.85 | 69.73 | 7 | -1 | 70.61 | 7 | -1 | Balanced / Middle tier |
| **7** | Wanindu Hasaranga | 198 | 70.04 | 72.16 | 5 | +2 | 71.64 | 5 | +2 | Elite Complete Bowler |
| **8** | Trent Boult | 180 | 69.72 | 67.79 | 10 | -2 | 66.56 | 9 | -1 | Balanced / Middle tier |
| **9** | Simarjeet Singh | 60 | 69.40 | 64.81 | 12 | -3 | 66.28 | 10 | -1 | Balanced / Middle tier |
| **10** | Lungi Ngidi | 110 | 68.89 | 68.45 | 8 | +2 | 68.40 | 8 | +2 | Balanced / Middle tier |

**Verified Top 10 Overlap:**
- Official v2.0 vs Exp 12.2: **9 / 10 (90.0%)** (Theekshana enters #9; Simarjeet exits).
- Official v2.0 vs Recal 12.5: **9 / 10 (90.0%)** (Theekshana enters #9; Simarjeet exits).

---

## 3. Final Recommendation for Investigation 2

### Final Recommendation: **PROVISIONALLY RETAIN OFFICIAL V2.0**
- **Why Containment Cannot Proceed Without Further Optimization:**
  1. *Severe Collinearity:* `Score_Econ` and `Score_Contain` share $79.24\%$ variance, artificially concentrating $70\%$ model weight on run restriction.
  2. *Wicket Suppression:* Direct wickets are compressed from $35\%$ nominal down to $15\%$ (Exp 12.2) or $20\%$ (Recal 12.5). In T20 cricket, breakthroughs break partnerships and prevent death-overs carnage.
  3. *Unresolved Weight Calibration:* There is currently no objective empirical loss function to justify whether Containment should be 20%, 25%, or 30%.
- **Candidate Engine Path:** If containment is incorporated in a future v3.0 engine, it must be formulated as a non-linear residual index or calibrated via win-probability contribution rather than arbitrary additive weighting.
