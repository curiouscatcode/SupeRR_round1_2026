# Matched-Context Batting-Position Pressure Audit Report (Investigation B)

**Audit Date:** 2026-11-13  
**Auditor:** Independent Analytics Agent (Step 16.4)  
**Dataset Population:** 180,839 batting balls faced across 789 matches  
**Status:** Completed & Validated  

---

## 1. Executive Summary & Core Findings

This investigation determines whether the large observed disparity in high-pressure delivery capture between Top-Order batters ($7.06\%$) and Lower-Order batters ($52.36\%$) persists after controlling for the actual cricket situation.

Deliveries are matched into discrete cells defined by:
$$\text{Match State Cell} = (\text{Innings}, \text{Match Phase}, \text{Wickets Lost Before Delivery})$$

### Core Findings
1. **Structural Lack of Common Support for Calm Situations:**
   - Lower-order batters (positions 7–11) **literally never bat** when 0, 1, 2, or 3 wickets are down. Across the entire dataset, there are exactly **0 deliveries** faced by lower-order batters with $\le 3$ wickets lost.
   - Conversely, **$84.5\%$ of all top-order deliveries** occur when $\le 2$ wickets are down.
   - Therefore, the raw capture gap ($45.30$ percentage points) is heavily driven by **selection into crisis situations**: lower-order batters only enter the field when their team has suffered a severe loss of wickets.
2. **Analysis on Common Support (19 Viable Cells):**
   - There are **19 viable match-state cells** with shared support (where both Top Order and Lower Order have $\ge 10$ deliveries). All 19 cells occur at **$\text{wickets\_before} \ge 4$** in Middle and Death overs.
   - When weighted by the common reference distribution across these 19 shared cells:
     * **Top Order Standardized Capture Rate:** **$2.80\%$** ($95\%$ CI: $[1.49\%, 4.03\%]$)
     * **Middle Order Standardized Capture Rate:** **$13.93\%$**
     * **Lower Order Standardized Capture Rate:** **$47.47\%$** ($95\%$ CI: $[43.45\%, 58.28\%]$)
     * **Matched-Context Difference:** **$+44.67$ percentage points** ($95\%$ CI: $[40.41\%, 55.69\%]$)
3. **The Root Driver of the Remaining Difference:**
   - In identical match-state cells (e.g., Innings 1, Death, 5 wickets down), **Tactical Pressure ($T$) is virtually identical**:
     * Top Order Mean $T$: **$46.74$**
     * Lower Order Mean $T$: **$47.85$**
   - However, **Situational Intensity ($I$) differs massively**:
     * Top Order Mean $I$: **$0.50$** (mean balls faced before: $43.6$ balls — fully set)
     * Lower Order Mean $I$: **$47.54$** (mean balls faced before: $7.3$ balls — newly arrived)
   - Because $\text{PI} = 0.65 T + 0.35 I$, the lower-order batter receives an automatic **$+16.5$ to $+17.5$ point boost** in PI from the "getting set" component ($I$). In Death overs, where the Z-score threshold requires high absolute PI, only newly arrived batters (high $I$) cross the $Z > 1.00$ threshold.

---

## 2. Unadjusted vs Matched-Context Comparison Table

| Batting Group | Total Deliveries | Unadjusted Capture % | Matched-Context Capture % | Clustered Bootstrap 95% CI | Mean $T$ (Tactical) | Mean $I$ (Situational) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Top Order (1–3)** | 90,068 | **7.06%** | **2.80%** | $[1.49\%, 4.03\%]$ | 28.74 | 25.57 |
| **Middle Order (4–6)** | 64,887 | **19.73%** | **13.93%** | — | 41.52 | 32.01 |
| **Lower Order (7–11)** | 25,884 | **52.36%** | **47.47%** | $[43.45\%, 58.28\%]$ | 55.43 | 51.37 |
| **Difference (Lower - Top)** | — | **+45.30 pp** | **+44.67 pp** | **[40.41 pp, 55.69 pp]** | **+26.69** | **+25.80** |

```
Artifacts:
outputs/step_16_4_pi_validation_audit/matched_context_batting_position_audit.csv
outputs/step_16_4_pi_validation_audit/matched_context_cells_detailed.csv
```

---

## 3. Individual Batting Position Progression (Positions 1 to 11)

| Batting Order | Role Category | Total Deliveries | Unadjusted HP % | Matched-Context HP % | Mean PI | Mean $T$ (Tactical) | Mean $I$ (Situational) | Mean Balls Faced Before |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | Top Order | 36,013 | **6.40%** | 2.51% | 25.30 | 27.67 | 25.32 | 15.0 |
| **2** | Top Order | 30,307 | **7.25%** | 2.94% | 26.27 | 28.79 | 26.06 | 14.6 |
| **3** | Top Order | 23,748 | **7.81%** | 3.12% | 27.22 | 30.31 | 25.32 | 15.1 |
| **4** | Middle Order | 27,272 | **13.06%** | 8.84% | 32.74 | 34.62 | 29.24 | 12.8 |
| **5** | Middle Order | 21,399 | **20.89%** | 15.12% | 40.06 | 43.14 | 34.33 | 10.3 |
| **6** | Middle Order | 16,216 | **29.41%** | 21.05% | 47.92 | 50.98 | 33.61 | 9.4 |
| **7** | Lower Order | 11,489 | **44.02%** | 37.89% | 56.45 | 53.64 | 47.96 | 7.2 |
| **8** | Lower Order | 6,804 | **56.55%** | 52.18% | 61.94 | 55.43 | 53.94 | 5.6 |
| **9** | Lower Order | 4,007 | **61.94%** | 58.12% | 64.92 | 57.12 | 54.49 | 5.3 |
| **10** | Lower Order | 2,246 | **63.54%** | 60.44% | 66.02 | 58.01 | 55.45 | 5.0 |
| **11** | Lower Order | 1,338 | **64.57%** | 62.15% | 66.84 | 58.62 | 55.82 | 4.8 |

```
Artifact:
outputs/step_16_4_pi_validation_audit/matched_context_by_position_1_to_11.csv
```

---

## 4. Analytical Interpretation

### Why does the gap remain after matching on Phase and Wickets?
1. **The Role of Situational Intensity ($I$):**
   Within identical match-state cells, Tactical Pressure ($T$) is identical across batting positions. The remaining gap of $+44.67$ percentage points is almost entirely explained by **Situational Intensity ($I$)**:
   - Top-order batters surviving to the late overs have batted 40+ balls ($I \approx 0$).
   - Lower-order batters enter cold ($I \approx 50\text{--}100$).
   - A newly arrived batter facing a ball at 140/6 in Over 18 is modeled by PI as experiencing substantially higher personal pressure than an opener who has scored 80 runs off 55 balls and is in full flow.
2. **Cricket Reality:**
   In cricket, an opener who is well-set ("in the groove") possesses complete eye-in, confidence, and momentum. A number 8 walking out with 2 overs left and wickets tumbling faces extreme immediate psychological pressure to hit from ball one without any settling period.
3. **Is it Bias or Legitimate Cricket Measurement?**
   The formula is player-blind (Investigation A). The difference is partly situational (lower order only bats in collapses) and partly structural to the definition of $I$ (new batters face higher immediate settling intensity).
   Investigation C breaks down the exact percentage contribution of each component.
