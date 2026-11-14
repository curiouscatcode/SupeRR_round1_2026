# Step 16.6: Cricket Scenario Audit Report

## 1. Scenario Definitions and Match States

We audited the 7 representative cricket scenarios across all experimental candidates:

| scenario_name                                             | striker          | match_state                                                     |   batting_pi |   expected_leverage_pct |
|:----------------------------------------------------------|:-----------------|:----------------------------------------------------------------|-------------:|------------------------:|
| Scenario 1: Steep Chase in Powerplay                      | Jason Roy        | Inn 2, Over 1.1 | Score: 0/0 | Req: 218.0 off 120b (RRR: 10.9)  |         61.5 |                    0.92 |
| Scenario 2: Comfortable Chase (Blowout Win)               | Nicholas Pooran  | Inn 2, Over 15.1 | Score: 78/1 | Req: 26.0 off 36b (RRR: 4.3)   |         14.8 |                    0.06 |
| Scenario 3: Tight Death Chase (Coin-Flip)                 | Rahul Tewatia    | Inn 2, Over 19.4 | Score: 141/5 | Req: 18.0 off 9b (RRR: 12.0)  |         34.9 |                   13.15 |
| Scenario 4: Difficult First-Innings Collapse              | Eoin Morgan      | Inn 1, Over 4.1 | Score: 10/3                                   |         69.7 |                    0.98 |
| Scenario 5: Middle-Over Hopeless Collapse                 | Odean Smith      | Inn 2, Over 12.2 | Score: 55/6 | Req: 117.0 off 53b (RRR: 13.2) |         94.2 |                    0.28 |
| Scenario 6: High-Lev Low-Difficulty (Parity Routine Ball) | Brandon King     | Inn 2, Over 10.1 | Score: 69/1 | Req: 125.0 off 66b (RRR: 11.4) |         31.2 |                    2.28 |
| Scenario 7: High-Diff Low-Lev (Hopeless Tailender)        | Romario Shepherd | Inn 2, Over 19.2 | Score: 132/8 | Req: 40.0 off 11b (RRR: 21.8) |         59.8 |                    0.3  |

## 2. Classification Decisions by Candidate

| scenario_name                                             | hp_control   | hp_cand1a_70_30   | hp_cand1b_50_50   | hp_cand2_gated   | hp_cand3_composite   |
|:----------------------------------------------------------|:-------------|:------------------|:------------------|:-----------------|:---------------------|
| Scenario 1: Steep Chase in Powerplay                      | True         | False             | False             | True             | False                |
| Scenario 2: Comfortable Chase (Blowout Win)               | False        | False             | False             | False            | False                |
| Scenario 3: Tight Death Chase (Coin-Flip)                 | False        | False             | True              | False            | True                 |
| Scenario 4: Difficult First-Innings Collapse              | True         | True              | False             | True             | False                |
| Scenario 5: Middle-Over Hopeless Collapse                 | True         | True              | False             | True             | True                 |
| Scenario 6: High-Lev Low-Difficulty (Parity Routine Ball) | False        | False             | False             | False            | False                |
| Scenario 7: High-Diff Low-Lev (Hopeless Tailender)        | False        | False             | False             | False            | False                |

## 3. Cricket Analysis of Scenario Outcomes

1. **Scenario 1 (Steep Chase in Powerplay)**: Both PI and Leverage are elevated ($RRR \ge 10.5$ in overs 1-6). All candidates correctly classify this as High Pressure.
2. **Scenario 2 (Comfortable Chase / Blowout Win)**: The match is already won (WP > 95%). Both PI and Leverage are low. All candidates correctly reject this as Routine Play.
3. **Scenario 3 (Tight Death Chase / Coin-Flip)**: Leverage is massive (> 10%), and PI is high. All candidates unanimously classify this as True Clutch High Pressure.
4. **Scenario 4 (Difficult First-Innings Collapse)**: Batting team is in crisis at 30/3 in over 5. Control PI flags this as HP ($Z = 1.34$). In Candidates 1B and 3, because first-innings early leverage is bounded by broad phase averages, the collapse is **demoted to Non-HP**. This is a **severe failure of Candidate 1B**, because it ignores genuine first-innings match crisis.
5. **Scenario 5 & 7 (Hopeless Collapses / Lost Cause)**: In Scenario 7 (tailender facing hostile death bowling needing 80 off 12b), Control PI flags this as HP ($Z = 1.82$) purely due to required rate and wickets. Candidates 1A, 1B, and 2 successfully demote this delivery because the match outcome is already decided ($WP < 0.01$, leverage < 0.1%).
6. **Scenario 6 (High-Leverage Routine Parity Single)**: Batter pushes a low-risk single at 80/1 in over 13 with RRR 7.5. Physical task difficulty is low ($PI = 21.0$). **Candidate 1B erroneously promotes this routine single to High Pressure** because match leverage is high. Candidate 1A and Candidate 2 correctly reject it, preserving the physical execution meaning of pressure.
