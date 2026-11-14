# Match Leverage Validation Report (Investigation D)

**Audit Date:** 2026-11-13  
**Auditor:** Independent Analytics Agent (Step 16.4)  
**Dataset Population:** 180,839 batting deliveries across 789 matches  
**Benchmark:** Calibrated Win Probability (WP) & Expected Delivery Leverage ($\mathbb{E}[|\Delta \text{WP}|]$)  
**Status:** Completed & Validated  

---

## 1. Executive Summary & Core Conceptual Findings

This investigation establishes an independent, objective reference to determine whether deliveries classified as **High Pressure ($Z > 1.00$)** genuinely occur in higher-leverage match situations.

### Core Conceptual Distinction: Task Difficulty vs Game Uncertainty
A fundamental distinction exists between two different concepts of "pressure" in sports analytics:
1. **Pressure Index (Task Difficulty / Crisis Intensity):**
   - Measures the difficulty of the task facing the batter (e.g. required run rate of 16 RPO, 8 wickets lost, early collapse, 0 balls to settle).
   - In cricket, a batter walking out at 40/6 in a run-chase is under extreme crisis pressure (task failure is imminent).
2. **Delivery Leverage (Game Uncertainty / Swing Potential):**
   - Measures the expected shift in win probability caused by the next ball: $\mathbb{E}[|\Delta \text{WP}|]$.
   - Mathematically, leverage is maximized when Win Probability is near **$50\%$** (game in the balance).
   - In a blowout (e.g. when Win Probability is $0.2\%$ because 8 wickets are down and 60 runs are needed off 18 balls), **Leverage is near ZERO** because the game is already decided, even though the batter's task difficulty is at its maximum!

### Key Empirical Findings:
- **Innings 1:** High Pressure ($Z > 1.00$) deliveries **have higher leverage** ($1.13\%$) than non-HP deliveries ($1.02\%$).
- **Top Order:** For top-order batters, High Pressure deliveries **have substantially higher leverage** ($1.61\%$) than non-HP deliveries ($1.33\%$).
- **Innings 2 & Lower Order:** In Innings 2 and for lower-order batters, High Pressure deliveries have *lower* average leverage ($0.99\%$ vs $1.82\%$ for Inn 2; $0.78\%$ vs $1.74\%$ for Lower Order).
  * Why? Because lower-order batters predominantly bat in **lost-cause collapses**: games where the team has already lost $7\text{--}9$ wickets and win probability is under $5\%$. In these deliveries, Task Pressure is at its absolute peak ($Z > 2.0$), but Leverage is tiny.
- **Correlation:** The linear correlation between continuous Batting PI and Leverage is $+0.0174$, and between Z-score and Leverage is $-0.0421$. This near-zero correlation is not an error; it mathematically confirms that PI measures *Task Difficulty*, which peaks in collapses where Leverage collapses to zero.

---

## 2. Subgroup Leverage Comparison Table

| Dimension | Subgroup | Total Deliveries | HP Deliveries ($Z > 1$) | Mean Leverage (All) | Mean Leverage (HP) | Mean Leverage (Non-HP) | Difference (HP - Non-HP) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Overall** | All Deliveries | 180,839 | 32,708 | **1.34%** | **1.07%** | **1.41%** | **-0.33 pp** |
| **Innings** | Innings 1 | 94,340 | 16,339 | **1.04%** | **1.13%** | **1.02%** | **+0.11 pp** |
| | Innings 2 | 86,499 | 16,369 | **1.67%** | **0.99%** | **1.82%** | **-0.82 pp** |
| **Phase** | Powerplay | 57,037 | 10,250 | **1.43%** | **1.36%** | **1.44%** | **-0.08 pp** |
| | Middle Overs | 84,038 | 14,803 | **1.22%** | **0.98%** | **1.27%** | **-0.29 pp** |
| | Death Overs | 39,764 | 7,655 | **1.50%** | **0.86%** | **1.65%** | **-0.79 pp** |
| **Batting Role** | Top Order (1–3) | 90,068 | 6,355 | **1.35%** | **1.61%** | **1.33%** | **+0.28 pp** |
| | Middle Order (4–6) | 64,887 | 12,800 | **1.39%** | **1.12%** | **1.45%** | **-0.34 pp** |
| | Lower Order (7–11) | 25,884 | 13,553 | **1.24%** | **0.78%** | **1.74%** | **-0.96 pp** |

```
Artifacts:
outputs/step_16_4_pi_validation_audit/match_leverage_validation_data.csv
outputs/step_16_4_pi_validation_audit/leverage_summary_by_subgroup.csv
```

---

## 3. Four-Quadrant Contrast Analysis

Cross-classifying deliveries by **Pressure Index (High vs Low)** and **Match Leverage (High vs Low)** reveals four distinct tactical regimes:

```
                  HIGH MATCH LEVERAGE (Game in Balance)
                                |
     Q3: Tense Parity           |      Q1: True Clutch Situations
     (Low PI, High Leverage)    |      (High PI, High Leverage)
     Deliveries: 76,462 (42.3%) |      Deliveries: 13,957 (7.7%)
     Mean Win Prob: 52.1%       |      Mean Win Prob: 36.8%
     Mean PI: 33.4              |      Mean PI: 61.8
     Mean Leverage: 2.32%       |      Mean Leverage: 2.14%
  ------------------------------+-------------------------------
     Q4: Routine Calm Play      |      Q2: Lost-Cause Collapses
     (Low PI, Low Leverage)     |      (High PI, Low Leverage)
     Deliveries: 71,669 (39.6%) |      Deliveries: 18,751 (10.4%)
     Mean Win Prob: 68.4%       |      Mean Win Prob: 8.2%
     Mean PI: 24.1              |      Mean PI: 74.5
     Mean Leverage: 0.44%       |      Mean Leverage: 0.28%
                                |
                  LOW MATCH LEVERAGE (Game Decided)
```

### Detailed Breakdown of the 4 Regimes:
1. **Q1: True Clutch Situations ($7.7\%$, 13,957 balls):**
   - High PI ($Z > 1.00$) AND High Leverage ($\text{WP} \approx 37\%$).
   - Tight second-innings chases with steep run rates (RRR 10–13) but achievable targets with wickets in hand.
   - High task difficulty coincides with high match swing.
2. **Q2: Lost-Cause Collapses ($10.4\%$, 18,751 balls):**
   - High PI ($Z > 1.00$) BUT Low Leverage ($\text{WP} = 8.2\%$).
   - Team has collapsed ($7\text{--}9$ wickets down, RRR $> 18$).
   - Lower-order tailenders batting in games that are already lost. Task difficulty is maximum ($T > 80$), but the match outcome cannot be salvaged.
3. **Q3: Tense Parity ($42.3\%$, 76,462 balls):**
   - Low PI ($Z \le 1.00$) BUT High Leverage ($\text{WP} = 52.1\%$).
   - Close games where run rate requirements are moderate (e.g. 15 required off 12 balls with 6 wickets in hand).
   - Because RRR and wickets lost are not in crisis, PI does not classify them as High Pressure, even though a single boundary or wicket swings the match dramatically.
4. **Q4: Routine Calm Play ($39.6\%$, 71,669 balls):**
   - Low PI AND Low Leverage.
   - Calm, routine overs with match firmly under control (blowout wins or early low-intensity overs).

---

## 4. Assessment of Question 4: Does High PI Correspond to High Leverage?

### Honest Scientific Verdict:
**No, High PI does not consistently correspond to High Delivery Leverage.**
- High PI measures **Task Difficulty / Resource Crisis** (how bad is the situation for the batting side?).
- Leverage measures **Game Uncertainty** (is the match outcome still open?).
- Because cricket matches often become one-sided blowouts before the 20th over, extreme crisis situations (high PI) naturally occur when the team has already lost (zero leverage).
- For Top-Order batters, High PI DOES correlate with higher leverage ($+0.28$ pp) because top-order collapses occur early enough that the match is still winnable.
- For Lower-Order batters, High PI occurs almost exclusively in Q2 (Lost-Cause Collapses), where leverage is near zero.
