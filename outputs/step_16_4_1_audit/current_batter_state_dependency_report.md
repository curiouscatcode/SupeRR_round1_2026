# Current-Batter-State Dependency Audit (Part A)

**Audit Date:** 2026-11-14  
**Auditor:** Independent Analytics Auditor  
**Focus:** Clarifying 'Player-Blind' vs 'Batter-State Independence' in Pressure Index  

---

## 1. Executive Summary: What 'Player-Blind' Actually Means

In Step 16.4, it was claimed that the Pressure Index is '100% player-blind' based on controlled mutation tests that shuffled player IDs and career records. However, this definition conflated **identity/quality independence** with **current-batter-state independence**.

The audit definitively establishes:
1. **Identity & Quality Independence (VERIFIED):** PI does NOT know the batter's name, ID, historical strike rate, career average, or designated batting order. Replacing Virat Kohli with Jasprit Bumrah does not change PI.
2. **Current-Batter-State Dependence (CONFIRMED):** Batting PI directly and heavily depends on `striker_balls_faced_before`. It is NOT purely a match-level state variable. At the exact same delivery in a match, two batters at the crease will have radically different PI values if one is newly arrived and the other is set.
3. **Magnitude of the Effect:** Holding every match-state variable constant (innings, phase, score, wickets, required run rate), changing `striker_balls_faced_before` from 0 to 10 decreases Batting PI by exactly **35.00 points**.
4. **Systematic Position Bias:** Because lower-order batters enter late and rarely face more than 10 balls, **76.8% of lower-order balls** receive positive Situational Intensity ($I > 0$). In contrast, **56.5% of top-order balls** are faced when fully set ($I = 0$).

---

## 2. Mathematical Trace of Situational Intensity

In `src/calculate_pressure_index.py`, the batter's Individual Pressure $I$ (designated $B$) is calculated as:
$$B = \text{clip}\left(\frac{10.0 - \text{striker\_balls\_faced\_before}}{10.0} \times 100.0, 0.0, 100.0\right)$$

Every batting delivery in the dataset uses the master formula:
$$\text{Batting\_PI} = 0.65 \times T + 0.35 \times I$$

Because $I = B$, the partial derivative of PI with respect to Individual Pressure is constant:
$$\frac{\partial \text{PI}}{\partial I} = 0.35$$

For every ball a batter faces between ball 0 and ball 10:
- $B$ decreases by $10.0$ percentage points.
- Batting PI decreases by $0.35 \times 10.0 = \mathbf{3.50\text{ PI points}}$ per delivery.
- Beyond 10 balls faced, $B = 0.0$, and the batter receives zero individual pressure contribution.

### Sensitivity Table (Holding Match State Constant)

| Balls Faced ($BF$) | Individual Pressure ($I$) | Added PI Points ($0.35 \times I$) | Total PI at $T=20$ (Calm) | Total PI at $T=50$ (Moderate) | Total PI at $T=80$ (Crisis) | Drop from Ball 0 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 100.0 | +35.00 | 48.00 | 67.50 | 87.00 | -0.00 |
| 1 | 90.0 | +31.50 | 44.50 | 64.00 | 83.50 | -3.50 |
| 2 | 80.0 | +28.00 | 41.00 | 60.50 | 80.00 | -7.00 |
| 3 | 70.0 | +24.50 | 37.50 | 57.00 | 76.50 | -10.50 |
| 4 | 60.0 | +21.00 | 34.00 | 53.50 | 73.00 | -14.00 |
| 5 | 50.0 | +17.50 | 30.50 | 50.00 | 69.50 | -17.50 |
| 6 | 40.0 | +14.00 | 27.00 | 46.50 | 66.00 | -21.00 |
| 7 | 30.0 | +10.50 | 23.50 | 43.00 | 62.50 | -24.50 |
| 8 | 20.0 | +7.00 | 20.00 | 39.50 | 59.00 | -28.00 |
| 9 | 10.0 | +3.50 | 16.50 | 36.00 | 55.50 | -31.50 |
| 10 | 0.0 | +0.00 | 13.00 | 32.50 | 52.00 | -35.00 |
| 11 | 0.0 | +0.00 | 13.00 | 32.50 | 52.00 | -35.00 |
| 12 | 0.0 | +0.00 | 13.00 | 32.50 | 52.00 | -35.00 |

---

## 3. Four Questions from the User Prompt

### 1. Does current batter balls faced directly affect PI?
**YES.** It directly sets Situational Intensity $I$, which constitutes 35% of the total Batting Pressure Index.

### 2. How much does PI change when balls faced changes while every other match-state variable stays constant?
**Exactly 35.00 PI points.** A batter facing their 1st ball ($BF = 0$) has a PI that is $35.00$ points higher than an identical batter in the exact same match situation who has faced 10 or more balls ($BF \ge 10$).

### 3. Is this variable measuring match pressure, individual batting exposure, or both?
**It measures individual batting exposure (settling vulnerability), NOT match pressure.**  
Match pressure is external and shared: the required run rate, the phase of the game, and the wickets remaining apply equally to the team. `striker_balls_faced_before` is an internal, individual attribute of the batter at the crease. Conflating individual settling with match pressure means two batters facing consecutive deliveries in the same over experience vastly different 'pressure' simply because one walked out two minutes earlier.

### 4. Does it systematically classify newly arrived batters as being under greater pressure?
**YES.** Every single batter entering the crease is automatically assigned $I = 100.0$ on their first ball, elevating their PI by $35.00$ points. Because top-order batters face their early balls when $T$ is low (overs 1–2, 0 wickets down), their PI rises from $\approx 15$ to $\approx 50$. Because lower-order batters face their early balls when $T$ is already high ($W \ge 6$), their PI rises from $\approx 55$ to $\approx 90$, causing $82.2\%$ of their early balls to exceed $Z > 1.00$.

---

## 4. Empirical Breakdown by Arrival State Across 180,839 Balls

| Role | Arrival State | Deliveries | % of Role Balls | HP Capture Rate ($Z > 1$) | Mean PI | Mean $I$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Top Order (1-3) | Ball 0 (Cold Arrival) | 4,722 | 5.2% | **52.58%** | 52.24 | 100.00 |
| Top Order (1-3) | Balls 1-4 (Early Settling) | 17,156 | 19.0% | **20.77%** | 42.23 | 75.54 |
| Top Order (1-3) | Balls 5-9 (Late Settling) | 17,264 | 19.2% | **1.44%** | 27.60 | 30.98 |
| Top Order (1-3) | Balls 10+ (Fully Set) | 50,926 | 56.5% | **0.12%** | 17.79 | 0.00 |
| Middle Order (4-6) | Ball 0 (Cold Arrival) | 4,338 | 6.7% | **76.44%** | 60.66 | 100.00 |
| Middle Order (4-6) | Balls 1-4 (Early Settling) | 15,531 | 23.9% | **49.58%** | 52.58 | 75.63 |
| Middle Order (4-6) | Balls 5-9 (Late Settling) | 14,963 | 23.1% | **10.37%** | 37.79 | 31.31 |
| Middle Order (4-6) | Balls 10+ (Fully Set) | 30,055 | 46.3% | **0.78%** | 29.36 | 0.00 |
| Lower Order (7-11) | Ball 0 (Cold Arrival) | 3,670 | 14.2% | **90.08%** | 76.72 | 100.00 |
| Lower Order (7-11) | Balls 1-4 (Early Settling) | 9,783 | 37.8% | **79.23%** | 69.07 | 76.94 |
| Lower Order (7-11) | Balls 5-9 (Late Settling) | 6,425 | 24.8% | **32.68%** | 54.03 | 32.69 |
| Lower Order (7-11) | Balls 10+ (Fully Set) | 6,006 | 23.2% | **6.59%** | 43.08 | 0.00 |

---

## 5. Audit Conclusion on Player-Blind Terminology

> **Audit Verdict:**  
> The statement in Step 16.4 that PI is '100% player-blind' is **scientifically imprecise and rejected**.  
> The correct description is:  
> - PI is **identity-invariant** and **quality-invariant** (blind to player name, ID, and career history).  
> - PI is **strongly state-dependent on the individual batter** via `striker_balls_faced_before`, which accounts for up to 35.00 points of the index.  
> - This current-batter-state dependence directly and systematically inflates the measured pressure of newly arrived batters and systematically biases high-pressure capture toward batting positions that face short innings.
