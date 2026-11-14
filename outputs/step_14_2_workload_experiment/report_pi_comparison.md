# Step 14.2 — Module 2: Pressure Index Comparison & Distribution Report

**Module:** Step 14.2 — Experimental Workload Formula Implementation and Impact Analysis  
**Date:** November 13, 2026  
**Audit Artifact:** [01_workload_and_pi_distributions.png](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_14_2_workload_experiment/01_workload_and_pi_distributions.png)
**Summary Dataset:** [exp14_2_pi_comparison_summary.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/step_14_2_workload_experiment/exp14_2_pi_comparison_summary.csv)

---

## 1. Executive Summary

This report evaluates the empirical delivery-level impact of replacing the current-spell bowler workload formula with the cumulative innings workload formula proposed in Step 9:
- **Original v2.0 Formula:** $W_{\text{spell}} = \min(100, (\text{legal\_balls\_in\_spell} / 12) \cdot 100)$
- **Experimental Formula:** $W_{\text{innings}} = \min(100, (\text{total\_legal\_balls\_in\_innings} / 24) \cdot 100)$

Evaluated across all **188,330 deliveries** in the 2022–2026 IPL/T20I dataset.

### Key Findings:
1. **Magnitude of Change:** Exactly **174,272 deliveries (92.54%)** experience a change in Bowling Pressure Index. The global mean delta is **$+0.69$ points** (Std = $3.59$). Changes range strictly from **$-8.75$ points** to **$+13.13$ points**.
2. **Phase-Specific Divergence:**
   - **Powerplay (PP, 59,179 balls):** Mean delta is **$-1.63$ points** (Max decrease: $-8.75$). In the Powerplay, bowlers in their second over had maximum spell workload ($12/12 = 100$) under v2.0, but only half innings workload ($12/24 = 50$) under the experimental model. Pressure in Powerplay drops noticeably.
   - **Middle Overs (86,829 balls):** Mean delta is **$+0.87$ points** (range $-7.00$ to $+13.13$).
   - **Death Overs (42,322 balls):** Mean delta is **$+3.56$ points** (range $-4.38$ to $+13.13$). In Death overs, death specialists entering a new spell (e.g. over 19) previously had $W = 0.0$; under the experimental formula, they have $W = 75.0$ (18 balls bowled). Their pressure score increases by up to $+13.13$ points.
3. **Pressure Classification Impact ($	ext{PI} \ge 60$):**
   - **Original High-Pressure Deliveries:** 24,364 deliveries (12.94%).
   - **Experimental High-Pressure Deliveries:** 25,603 deliveries (13.59%).
   - **Net Increase:** $+1,239$ deliveries ($+5.09\%$ increase).
   - **Promoted Deliveries (Low/Mod $\to$ High):** 2,427 deliveries promoted (82.1% in Death and Middle overs).
   - **Demoted Deliveries (High $\to$ Low/Mod):** 1,188 deliveries demoted (76.8% in Powerplay and early overs).

---

## 2. Phase-Level Distribution Breakdown

| Phase | Delivery Count | Mean Orig PI | Mean Exp PI | Mean Delta | Std Delta | Min Delta | Max Delta | High Balls Orig ($\ge 60$) | High Balls Exp ($\ge 60$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay (PP)** | 59,179 | 36.63 | 35.00 | **-1.63** | 2.50 | -8.75 | +4.38 | 5,479 (9.26%) | 4,685 (7.92%) |
| **Middle Overs** | 86,829 | 38.64 | 39.51 | **+0.87** | 3.32 | -7.00 | +13.13 | 10,256 (11.81%) | 10,872 (12.52%) |
| **Death Overs** | 42,322 | 47.01 | 50.57 | **+3.56** | 3.98 | -4.38 | +13.13 | 8,629 (20.39%) | 10,046 (23.74%) |
| **Total Population** | **188,330** | **39.89** | **40.58** | **+0.69** | **3.59** | **-8.75** | **+13.13** | **24,364 (12.94%)** | **25,603 (13.59%)** |

---

## 3. Workload Progression Bracket Summary

| Innings Legal Balls | Delivery Count | Mean $W_{\text{spell}}$ | Mean $W_{\text{innings}}$ | Mean Orig PI | Mean Exp PI | Mean Delta PI | Cricketing Context |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Over 1 (0–6 balls)** | 67,882 | 26.5 | 11.4 | 36.42 | 33.78 | **-2.64** | Bowlers in early overs see workload deflated compared to aggressive spell scaling. |
| **Over 2 (7–12 balls)** | 56,864 | 45.4 | 38.7 | 39.40 | 38.23 | **-1.17** | Second over bowlers show modest deflation. |
| **Over 3 (13–18 balls)** | 42,976 | 38.1 | 64.6 | 42.66 | 47.29 | **+4.63** | Workload accumulates significantly as third over is bowled across the innings. |
| **Over 4 (19–24 balls)** | 20,608 | 32.2 | 88.5 | 46.85 | 56.70 | **+9.85** | Final overs (usually death) experience substantial workload escalation ($+9.85$ pts). |