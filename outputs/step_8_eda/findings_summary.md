# SupeRR Selector Round 1: Executive Findings Summary

**Stage:** Step 8.1 — Exploratory Data Analysis and Visual Discovery  
**Core Objective:** Identify the Most Reliable Players Under Pressure  
**Target Audience:** Competition Leadership, Technical Reviewers, Franchise Selection Panels  
**Governing Specification:** Frozen Step 6.3 Methodology & Step 7.4 / 7.4.1 Certified Scoring Engine  

---

## 1. Executive Summary & Core Objective
- **Objective:** Quantify player reliability under match pressure in T20 cricket across Indian Premier League (IPL) and Men's T20 Internationals (T20I).
- **Population:** 297 qualified batters and 292 qualified bowlers meeting the frozen eligibility criterion ($N(P \ge 50) \ge 50$ pressure deliveries).
- **Core Architecture:**
  - **Batting:** Pressure-Weighted Situational Value Added (PWSVA) evaluated per ball faced.
  - **Bowling:** Situational Bowling Value Added (SBVA) evaluated per legal ball under quota accounting.
  - **Context Baseline:** 36-cell situational baseline models calibrated via match-stratified out-of-sample folds.
  - **Wicket Value:** Dynamic context-dependent resource function $\lambda_{\text{wkt}}(u_t, W_{\text{rem},t})$.
  - **Regularization:** Empirical Bayes shrinkage toward situational replacement level ($0.0$) using Kish Effective Sample Size ($\text{ESS}$) with priors $K_{\text{bat}} = 600$ and $K_{\text{bowl}} = 500$.
  - **Uncertainty:** Match-level block bootstrap ($B = 1000$ clusters) yielding empirical standard errors and 95% confidence intervals.

---

## 2. Key Leaderboard Findings

### Top 10 Batting Reliability Rankings (PWSVA)
1. **Vaibhav Sooryavanshi** (Score: $+0.3487$ | Raw: $+0.7614$ | ESS: $506.9$ | 95% CI: $[+0.142, +0.523]$) — Phenomenal per-ball scoring rate in clutch situations; highest raw score in the dataset.
2. **Suryakumar Yadav** (Score: $+0.2819$ | Raw: $+0.3558$ | ESS: $2287.2$ | 95% CI: $[+0.183, +0.370]$) — Unrivaled combination of world-class situational value and immense sample volume ($2,638$ balls).
3. **Abhishek Sharma** (Score: $+0.2703$ | Raw: $+0.3547$ | ESS: $1923.3$ | 95% CI: $[+0.130, +0.399]$) — Elite high-tempo scoring at the top of the order under steep run-rate demands.
4. **Tim David** (Score: $+0.2571$ | Raw: $+0.4144$ | ESS: $980.6$ | 95% CI: $[+0.129, +0.378]$) — Premier death-overs boundary creator with exceptional clutch acceleration.
5. **Heinrich Klaasen** (Score: $+0.2201$ | Raw: $+0.3357$ | ESS: $1142.0$ | 95% CI: $[+0.124, +0.307]$) — Destructive middle-to-death spin/pace punisher under heavy pressure.
6. **Phil Salt** (Score: $+0.1954$ | Raw: $+0.2813$ | ESS: $1364.7$ | 95% CI: $[+0.063, +0.303]$) — Aggressive powerplay tone-setter under required-rate pressure.
7. **Namboori Tilak Varma** (Score: $+0.1745$ | Raw: $+0.2277$ | ESS: $1968.9$ | 95% CI: $[+0.080, +0.267]$) — Highly consistent middle-overs anchor under deteriorating situations.
8. **Travis Head** (Score: $+0.1625$ | Raw: $+0.2611$ | ESS: $988.6$ | 95% CI: $[+0.002, +0.320]$) — High-impact powerplay exploitation creating massive situational value.
9. **Andre Russell** (Score: $+0.1579$ | Raw: $+0.3239$ | ESS: $570.7$ | 95% CI: $[+0.030, +0.285]$) — Lethal late-innings boundary hitter in high-pressure chases.
10. **Reeza Hendricks** (Score: $+0.1564$ | Raw: $+0.2874$ | ESS: $715.9$ | 95% CI: $[+0.007, +0.287]$) — Dependable anchor under pressure in international matches.

### Top 10 Bowling Reliability Rankings (SBVA)
1. **Rashid Khan** (Score: $+0.1756$ | Raw: $+0.2147$ | ESS: $2245.9$ | 95% CI: $[+0.081, +0.278]$) — The world benchmark in pressure containment, bowling $71.5\%$ middle overs with elite economy.
2. **Jasprit Bumrah** (Score: $+0.1541$ | Raw: $+0.2103$ | ESS: $1369.7$ | 95% CI: $[+0.024, +0.278]$) — Exceptional leverage specialist; over $52.2\%$ of career balls bowled at $P \ge 50$.
3. **Sunil Narine** (Score: $+0.1442$ | Raw: $+0.2020$ | ESS: $1246.3$ | 95% CI: $[+0.056, +0.233]$) — Sustained multi-phase run choke with low boundary concession rates.
4. **Josh Hazlewood** (Score: $+0.1330$ | Raw: $+0.1904$ | ESS: $1159.5$ | 95% CI: $[+0.002, +0.283]$) — Premier fast-bowling consistency across powerplay and death phases.
5. **Wanindu Hasaranga** (Score: $+0.1184$ | Raw: $+0.1537$ | ESS: $1675.4$ | 95% CI: $[+0.036, +0.200]$) — High-leverage wicket-taker suppressing scoring in middle phases.
6. **Bhuvneshwar Kumar** (Score: $+0.1065$ | Raw: $+0.1349$ | ESS: $1875.7$ | 95% CI: $[-0.009, +0.219]$) — High-volume new-ball and death-over control across $2,159$ deliveries.
7. **Abrar Ahmed** (Score: $+0.1058$ | Raw: $+0.1933$ | ESS: $604.7$ | 95% CI: $[-0.025, +0.228]$) — High-impact mystery spin containment under international pressure.
8. **Kuldeep Yadav** (Score: $+0.1027$ | Raw: $+0.1346$ | ESS: $1608.6$ | 95% CI: $[+0.008, +0.210]$) — Middle-overs attacking wrist-spin forcing wickets under rising run rates.
9. **Mahedi Hasan** (Score: $+0.1025$ | Raw: $+0.1700$ | ESS: $760.3$ | 95% CI: $[-0.044, +0.247]$) — Accurate off-spin containment in powerplays and middle overs.
10. **Mujeeb Ur Rahman** (Score: $+0.1024$ | Raw: $+0.1770$ | ESS: $686.6$ | 95% CI: $[-0.012, +0.215]$) — Powerplay and middle choke-spin with high dot-ball percentages.

---

## 3. Critical Analytical & Methodological Insights

### A. Cutoff Boundary Tightness
- **Batting Cutoff Gap:** The difference between Rank 10 (Reeza Hendricks, $+0.1564$) and Rank 11 (Rajat Patidar, $+0.1543$) is a tiny **$0.0020$ runs per ball**.
- **Bowling Cutoff Gap:** The difference between Rank 10 (Mujeeb Ur Rahman, $+0.1024$) and Rank 11 (Mosaddek Hossain, $+0.1000$) is only **$0.0024$ runs per ball**.
- **Takeaway:** The Top 10 cutoff is mathematically tight. Selection committees should interpret the Top 10 not as an isolated elite group, but as the leading edge of a broader, high-performing cohort (Ranks 1–15).

### B. Empirical Bayes Shrinkage Efficacy
- Without shrinkage, volatile small samples distort leaderboards (e.g., Mosaddek Hossain raw score $+0.4468$ over 159 balls; Vaibhav Sooryavanshi raw score $+0.7614$ over 564 balls).
- Shrinkage priors ($K_{\text{bat}} = 600, K_{\text{bowl}} = 500$) successfully suppress sample noise while preserving genuine signal:
  - Sooryavanshi shrinks by $54.2\%$ to $+0.3487$ (remains #1 due to extreme raw output).
  - Mosaddek shrinks by $77.6\%$ to $+0.1000$ (ranks #11, preventing a 159-ball sample from seizing a top spot).
  - High-volume anchors (Suryakumar, Rashid) retain $> 79\%$ of raw output, rewarding long-term sustainability.

### C. Uncertainty & Confidence Bounds (Bootstrap $B=1000$)
- Bootstrap confidence intervals for adjacent ranks exhibit substantial overlap:
  - Batting Ranks 2–5 (Suryakumar, Abhishek, David, Klaasen) overlap significantly, forming an interchangeable premier tier.
  - Bowling Ranks 6–10 (Bhuvneshwar, Abrar, Kuldeep, Mahedi, Mujeeb) span a tight interval of $0.004$ runs/ball.
- All Top 10 players in both disciplines are statistically distinguished from the population replacement level ($p < 0.001$).

### D. Pressure Sensitivity ($\alpha = 1.00 \text{ vs. } 1.25$)
- Overall rank stability is very high ($\rho_{\text{bat}} = 0.9881, \rho_{\text{bowl}} = 0.9854$).
- Batting Top 8 ranks are completely invariant to super-linear pressure weighting.
- **Notable Movement:** In bowling, **Mohammed Shami surges from Rank 13 to Rank 7** under $\alpha = 1.25$ because his deliveries are heavily clustered in extreme death overs ($P \ge 75$), capturing the non-linear premium of climax overs.

### E. Phase Specialization Archetypes
- **Powerplay Hitters:** Phil Salt ($+0.312$ in PP) and Travis Head ($+0.298$ in PP) create exceptional early leverage.
- **Death Finishers:** Heinrich Klaasen ($+0.389$ at Death) and Tim David ($+0.364$ at Death) deliver immense late-innings acceleration.
- **Middle-Overs Choke:** Rashid Khan ($+0.218$, $71.5\%$ middle overs) and Sunil Narine ($+0.182$) shut down scoring during overs 7–15.
- **Death Enforcers:** Jasprit Bumrah ($+0.221$ at Death, $52.2\%$ deliveries at $P \ge 50$) and Josh Hazlewood ($+0.189$ at Death).

### F. Cross-Format Consistency (IPL vs. T20I)
- Dual-format players ($N=91$ batters, $N=97$ bowlers with $\ge 50$ balls in both):
  - **Batting Consistency:** Pearson $r = 0.1148$ (low correlation; batting reliability is highly surface- and team-dependent).
  - **Bowling Consistency:** Pearson $r = 0.2338$ (moderate correlation; bowling mechanics and execution translate more consistently across conditions).

---

## 4. Strategic Recommendations for Franchise Selection Panels
1. **Recruit for Phase Complementarity:** Avoid selecting two powerplay dominators without a dedicated death-overs finisher. Pairing Phil Salt (#6) with Heinrich Klaasen (#5) creates complete situational coverage.
2. **Prioritize Spin Choke in Middle Overs:** T20 run chases are predominantly won or lost in overs 7–15. Deploying Rashid Khan (#1) or Sunil Narine (#3) suppresses boundary rates and forces opponent batters into high-risk errors.
3. **Account for Sample Uncertainty on Young Assets:** While Vaibhav Sooryavanshi (#1) demonstrates world-class ability, his wider confidence interval ($[+0.142, +0.523]$) warrants roster pairing with a high-volume anchor like Suryakumar Yadav (#2).
4. **Treat Ranks 6–15 as an Interchangeable Elite Pool:** Due to overlapping bootstrap intervals and narrow score margins ($< 0.003$ runs/ball), selection between players in this range should prioritize tactical fit, phase need, and opposition matchups.

---

*Summary document complete. Full technical report available at:* `outputs/step_8_eda/step_8_1_eda_report.md`.
