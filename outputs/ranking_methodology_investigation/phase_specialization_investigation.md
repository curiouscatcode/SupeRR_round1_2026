# Investigation 6: Phase Specialization Versus Overall Reliability

## Executive Summary

This investigation evaluates whether aggregating high-pressure performance across all match phases into a single composite reliability score (BRS for batters, BoRS for bowlers) fairly represents players who specialize in distinct phases (Powerplay, Middle Overs, Death Overs).

### Key Mathematical & Structural Findings:
1. **Phase Exposure Confounding:** Players do not experience equal phase distributions under high pressure. Across Tier 1 batters, Death Overs exposure ranges from 0.0% to 88.5%. Across Tier 1 bowlers, Powerplay exposure ranges from 0.0% to 84.6%.
2. **Resolution of the MS Dhoni Discrepancy:**
   - In official v2.0 rankings, MS Dhoni is **Rank #1 overall** (BRS 95.05).
   - In phase specialist rankings, Dhoni is **Rank #86 in Middle Overs** (observed SR 65.79) but **Rank #2 in Death Overs** (observed SR 197.37).
   - **Root Cause Reconciliation:** Dhoni faced **78.4% (152 of 194 balls)** of his high-pressure deliveries in the Death Overs, where he achieved a staggering strike rate of 197.37. Only 19.6% (38 balls) occurred in Middle Overs. Because the official v2.0 model aggregates across all deliveries without phase-stratified weighting, his massive Death Overs scoring completely dominates his overall record, yielding an aggregate high-pressure strike rate of 170.62.
3. **The Bumrah Powerplay Concentration:**
   - Jasprit Bumrah bowled **73.2% (123 of 168 balls)** of his high-pressure deliveries in the **Powerplay**, where he conceded only 7.07 rpo (Rank #5 among Powerplay specialists).
   - In Death Overs, Bumrah bowled only 9 high-pressure balls across the entire multi-year dataset. Because batters naturally play defensively against Bumrah in the Powerplay (conceding few wickets), his low overall wicket count (5 wickets, 2.98%) is primarily a function of **phase exposure**, not a lack of clutch wicket-taking capability.
4. **Structural Ranking Distortion:** The overall model systematically favors Death Overs finishers in batting (elevated baseline strike rates) and penalizes Powerplay bowlers in bowling (depressed wicket baselines), creating an uneven playing field.

---

## 1. MS Dhoni Discrepancy Reconciliation

Direct recalculation from authoritative datasets (`batter_performance.csv` and `delivery_match_state.csv`):

| Phase | High Balls Faced | High Runs | High Dismissals | Observed SR | Phase Specialist Rank | Bayesian Metric |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay (Overs 1-6)** | 4 (2.1%) | 6 | 0 | 150.00 | Unranked (<15 balls) | — |
| **Middle Overs (Overs 7-15)** | 38 (19.6%) | 25 | 0 | 65.79 | **#86** | 88.76 |
| **Death Overs (Overs 16-20)** | 152 (78.4%) | 300 | 8 | 197.37 | **#2** | 179.55 |
| **Total High Pressure** | **194** | **331** | **8** | **170.62** | **#1 Overall (Tier 1)** | **BRS = 95.05** |

> [!IMPORTANT]
> **Definitive Reconciliation:** Both previous reports were factually correct but described different facets of Dhoni's distribution. In Middle Overs, Dhoni was an extreme accumulator (SR 65.79, 0 dismissals). In Death Overs, he was an explosive finisher (SR 197.37). Because 78.4% of his sample came in Death Overs, his aggregate BRS of 95.05 accurately reflects his high-pressure role as a Death Overs finisher, but misrepresents him if viewed as an all-phase batter.

---

## 2. Jasprit Bumrah Phase Exposure

Direct recalculation for Jasprit Bumrah (`bowler_performance.csv`):

| Phase | High Legal Balls | Runs Conceded | Wickets | Observed Econ | Phase Specialist Rank | Bayesian Econ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay (Overs 1-6)** | 123 (73.2%) | 145 | 2 | 7.07 | **#5** | 7.73 |
| **Middle Overs (Overs 7-15)** | 36 (21.4%) | 47 | 2 | 7.83 | **#24** | 8.41 |
| **Death Overs (Overs 16-20)** | 9 (5.4%) | 2 | 1 | 1.33 | Unranked (<15 balls) | — |
| **Total High Pressure** | **168** | **194** | **5** | **6.93** | **#24 Overall (Tier 1)** | **BoRS = 59.29** |

> [!NOTE]
> Bumrah's low wicket score (25.31) is directly caused by his 73.2% Powerplay exposure. In Powerplay cricket, batting teams aim to survive Bumrah's high-pressure overs, yielding an exceptional 7.07 economy rate but only 2 wickets in 123 balls (1.63%).

---

## 3. Tier 1 Population Phase Exposure Extremes

### A. Extreme Powerplay Batters vs Extreme Death Overs Batters

**Top 5 Powerplay-Heavy Batters (Tier 1):**
| Rank | Player | High Balls | PP % | MO % | DO % | BRS |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| #63 | **Yashasvi Jaiswal** | 63 | 100.0% | 0.0% | 0.0% | 53.11 |
| #94 | **Abhishek Sharma** | 76 | 97.4% | 2.6% | 0.0% | 39.19 |
| #90 | **Sanju Samson** | 91 | 91.2% | 8.8% | 0.0% | 40.33 |
| #41 | **Nitish Rana** | 80 | 87.5% | 11.2% | 1.2% | 59.14 |
| #66 | **Ishan Kishan** | 74 | 83.8% | 16.2% | 0.0% | 51.93 |

**Top 5 Death-Overs-Heavy Batters (Tier 1):**
| Rank | Player | High Balls | PP % | MO % | DO % | BRS |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| #115 | **Dushmantha Chameera** | 86 | 0.0% | 7.0% | 93.0% | 17.72 |
| #108 | **Arshdeep Singh** | 104 | 0.0% | 8.7% | 91.3% | 31.30 |
| #113 | **Ravi Bishnoi** | 77 | 0.0% | 11.7% | 88.3% | 25.64 |
| #76 | **Haris Rauf** | 96 | 0.0% | 13.5% | 86.5% | 48.71 |
| #96 | **Ish Sodhi** | 96 | 0.0% | 13.5% | 86.5% | 37.23 |

### B. Extreme Powerplay Bowlers vs Extreme Death Overs Bowlers

**Top 5 Powerplay-Heavy Bowlers (Tier 1):**
| Rank | Player | High Balls | PP % | MO % | DO % | BoRS |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| #56 | **Deepak Chahar** | 134 | 99.3% | 0.7% | 0.0% | 50.19 |
| #39 | **Nuwan Thushara** | 82 | 97.6% | 0.0% | 2.4% | 56.27 |
| #13 | **Khaleel Ahmed** | 222 | 95.9% | 3.2% | 0.9% | 64.68 |
| #81 | **Xavier Bartlett** | 69 | 95.7% | 2.9% | 1.4% | 44.28 |
| #5 | **Shoriful Islam** | 61 | 95.1% | 4.9% | 0.0% | 74.01 |

**Top 5 Death-Overs-Heavy Bowlers (Tier 1):**
| Rank | Player | High Balls | PP % | MO % | DO % | BoRS |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| #21 | **Matheesha Pathirana** | 86 | 19.8% | 40.7% | 39.5% | 60.37 |
| #14 | **Mohit Sharma** | 79 | 29.1% | 31.6% | 39.2% | 63.58 |
| #107 | **Harshal Patel** | 133 | 36.8% | 30.1% | 33.1% | 32.14 |
| #88 | **Andre Russell** | 89 | 22.5% | 53.9% | 23.6% | 40.63 |
| #42 | **Yash Thakur** | 82 | 61.0% | 15.9% | 23.2% | 56.03 |

---

## 4. Answers to Mandatory Phase Specialization Questions

1. **How different are player performances across phases?**
   - Vastly different. High-pressure strike rates average 111.3 in Powerplay vs 122.9 in Death Overs (with elite finishers exceeding 180). Bowling wicket rates triple from Powerplay (~3.5%) to Death Overs (~9.0%).
2. **Which players are strong specialists but average overall?**
   - *Nasum Ahmed:* #1 Powerplay bowler (economy 4.43), but below threshold overall.
   - *Mohit Sharma:* #1 Death Overs bowler (economy 5.42), but #43 overall.
   - *Ravichandran Ashwin:* #2 Middle Overs bowler (economy 5.83), but #39 overall.
   - *Jasprit Bumrah:* #5 Powerplay bowler (economy 7.07), but #24 overall.
3. **Does overall aggregation hide valuable phase-specific strengths?**
   - Yes, definitively. Aggregating all high-pressure deliveries masks world-class phase execution behind generic composite scores.
4. **Are players being compared fairly when their phase exposure differs?**
   - **No.** An overall metric that compares a 78% Death Overs batter against a 70% Powerplay batter without adjusting for phase baselines introduces systematic role bias.
5. **Does the current phase-specialist ranking provide useful additional information?**
   - Yes, it surfaces phase masters, but it is currently limited to a single Bayesian metric (SR for batters, Economy for bowlers) and lacks composite multi-dimensional scoring.

---
*(Report generated automatically by Step 11 Investigation 6)*