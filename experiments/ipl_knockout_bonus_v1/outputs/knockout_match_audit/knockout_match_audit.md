# IPL Knockout Match Classification & Delivery Audit

**Experiment:** IPL Knockout Bonus (v1)  
**Stage:** Stage 1 & 2 — Match Audit and Metadata Identification  
**Author:** Antigravity (Google DeepMind Agentic System)  
**Date:** November 15, 2026  
**Governing Rule:** Strict isolation; no modification of baseline rankings or data.  

---

## 1. Executive Audit Summary

- **Total Scheduled IPL Playoff Matches in Metadata:** **20 matches** across 5 seasons (2022 to 2026).
- **Active Knockout Matches in Frozen Dataset:** **19 matches** (100% of full 20-over playoff matches).
- **Excluded Knockout Matches:** Exactly **1 match** (Match `21586`, the IPL 2023 Final: CSK vs GT).
  - *Audit Finding:* Match `21586` was interrupted by rain after Gujarat Titans' innings (214/4) and revised under DLS to a 15-over chase (target 171 in 90 balls). As documented in Step 2.1, Step 2.2, and Step 4, all non-20-over DLS matches were excluded upstream from the pure 20-over dataset to avoid distorting situational baselines.
- **Total Delivery Volume in Active Knockouts:**
  - **Batting Delivery Rows:** `4,445`
  - **Batter Balls Faced:** `4,277`
  - **Batting Pressure Deliveries ($P \ge 50$):** `1,922`
  - **Batting Climax Deliveries ($P \ge 75$):** `211`
  - **Bowling Delivery Rows:** `4,445`
  - **Bowler Legal Balls Bowled:** `4,257`
  - **Bowling Pressure Deliveries ($P \ge 50$):** `1,964`
  - **Bowling Climax Deliveries ($P \ge 75$):** `36`
- **Player Participation in Active Knockouts:**
  - Distinct batters participating in knockouts: `128` (91 of the 297 qualified batters).
  - Distinct bowlers participating in knockouts: `92` (82 of the 292 qualified bowlers).
  - Qualified batters with **ZERO** knockout appearances: `206` (69.4% of qualified population).
  - Qualified bowlers with **ZERO** knockout appearances: `210` (71.9% of qualified population).

---

## 2. Match-by-Match Verification Register

| Match ID | Season | Match # | Date | Metadata Stage | Verified Knockout Stage | Matchup (Home vs Away) | Result | In Dataset? | Faced Balls | Legal Balls | Pressure Balls ($P \ge 50$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `15187` | 2022 | #71 | 2022-05-24 | `Qualifier` | **Qualifier 1** | Gujarat Titans vs Rajasthan Royals | Gujarat Titans Won by 7 Wickets | **YES** | 239 | 237 | Bat: 172 / Bowl: 195 |
| `15188` | 2022 | #72 | 2022-05-25 | `Eliminator` | **Eliminator** | Lucknow Super Giants vs Royal Challengers Bengaluru | Royal Challengers Bengaluru Won by 14 Runs | **YES** | 241 | 240 | Bat: 141 / Bowl: 137 |
| `15189` | 2022 | #73 | 2022-05-27 | `Qualifier` | **Qualifier 2** | Rajasthan Royals vs Royal Challengers Bengaluru | Rajasthan Royals won by 7 wickets | **YES** | 226 | 226 | Bat: 63 / Bowl: 112 |
| `15190` | 2022 | #74 | 2022-05-29 | `Final` | **Final** | Gujarat Titans vs Rajasthan Royals | Gujarat Titans Won by 7 Wickets | **YES** | 229 | 229 | Bat: 67 / Bowl: 135 |
| `21583` | 2023 | #71 | 2023-05-23 | `Qualifier` | **Qualifier 1** | Gujarat Titans vs Chennai Super Kings | Chennai Super Kings Won by 15 runs | **YES** | 242 | 240 | Bat: 168 / Bowl: 143 |
| `21584` | 2023 | #72 | 2023-05-24 | `Eliminator` | **Eliminator** | Lucknow Super Giants vs Mumbai Indians | Mumbai Indians won by 81 runs | **YES** | 219 | 219 | Bat: 136 / Bowl: 109 |
| `21585` | 2023 | #73 | 2023-05-26 | `Qualifier` | **Qualifier 2** | Gujarat Titans vs Mumbai Indians | Gujarat Titans won by 62 runs | **YES** | 233 | 230 | Bat: 66 / Bowl: 59 |
| `21586` | 2023 | #74 | 2023-05-29 | `Final` | **Final** | Chennai Super Kings vs Gujarat Titans | Chennai Super Kings Won by 5 wickets  (DLS method) | *NO (DLS)* | 0 | 0 | N/A |
| `31289` | 2024 | #71 | 2024-05-21 | `Qualifier` | **Qualifier 1** | Kolkata Knight Riders vs Sunrisers Hyderabad | Kolkata Knight Riders Won by 8 wickets | **YES** | 201 | 199 | Bat: 44 / Bowl: 68 |
| `31290` | 2024 | #72 | 2024-05-22 | `Eliminator` | **Eliminator** | Rajasthan Royals vs Royal Challengers Bengaluru | Rajasthan Royals Won by 4 wickets | **YES** | 234 | 234 | Bat: 151 / Bowl: 196 |
| `31291` | 2024 | #73 | 2024-05-24 | `Qualifier` | **Qualifier 2** | Sunrisers Hyderabad vs Rajasthan Royals | Sunrisers Hyderabad Won by 36 runs | **YES** | 241 | 240 | Bat: 174 / Bowl: 133 |
| `31292` | 2024 | #74 | 2024-05-26 | `Final` | **Final** | Kolkata Knight Riders vs Sunrisers Hyderabad | Kolkata Knight Riders Won by 8 wickets | **YES** | 174 | 174 | Bat: 32 / Bowl: 5 |
| `40764` | 2025 | #72 | 2025-05-29 | `Qualifier` | **Qualifier 1** | Punjab Kings vs Royal Challengers Bengaluru | Royal Challengers Bengaluru Won by 8 wickets | **YES** | 143 | 142 | Bat: 36 / Bowl: 22 |
| `40765` | 2025 | #73 | 2025-05-30 | `Eliminator` | **Eliminator** | Gujarat Titans vs Mumbai Indians | Mumbai Indians Won by 20 runs | **YES** | 240 | 240 | Bat: 98 / Bowl: 84 |
| `40766` | 2025 | #74 | 2025-06-01 | `Qualifier` | **Qualifier 2** | Punjab Kings vs Mumbai Indians | Punjab Kings Won by 5 wickets | **YES** | 237 | 234 | Bat: 151 / Bowl: 138 |
| `40767` | 2025 | #75 | 2025-06-03 | `Final` | **Final** | Royal Challengers Bengaluru vs Punjab Kings | Royal Challengers Bengaluru Won by 6 runs | **YES** | 240 | 240 | Bat: 179 / Bowl: 152 |
| `50942` | 2026 | #71 | 2026-05-26 | `Qualifier` | **Qualifier 1** | Royal Challengers Bengaluru vs Gujarat Titans | Royal Challengers Bengaluru Won by 92 runs | **YES** | 240 | 237 | Bat: 43 / Bowl: 38 |
| `50943` | 2026 | #72 | 2026-05-27 | `Eliminator` | **Eliminator** | Sunrisers Hyderabad vs Rajasthan Royals | Rajasthan Royals Won by 47 runs | **YES** | 238 | 236 | Bat: 15 / Bowl: 24 |
| `50944` | 2026 | #73 | 2026-05-29 | `Qualifier` | **Qualifier 2** | Gujarat Titans vs Rajasthan Royals | Gujarat Titans Won by 7 wickets | **YES** | 232 | 232 | Bat: 112 / Bowl: 111 |
| `50945` | 2026 | #74 | 2026-05-31 | `Final` | **Final** | Royal Challengers Bengaluru vs Gujarat Titans | Royal Challengers Bengaluru Won by 5 wickets | **YES** | 228 | 228 | Bat: 74 / Bowl: 103 |

---

## 3. Ambiguity & Missing Stage Detection

1. **Tournament Stage Verification:**
   - In raw `data/matches.csv`, stages are categorized as `'Qualifier'`, `'Eliminator'`, and `'Final'`.
   - In 2022, 2023, 2024, and 2026, the four playoff matches are sequentially numbered #71 (Qualifier 1), #72 (Eliminator), #73 (Qualifier 2), and #74 (Final).
   - In 2025, due to 71 league matches scheduled, the playoff matches are numbered #72 (Qualifier 1: PBKS vs RCB), #73 (Eliminator: GT vs MI), #74 (Qualifier 2: PBKS vs MI), and #75 (Final: RCB vs PBKS).
   - Cross-referencing match dates, participating teams, and winner progression confirms **zero ambiguity** in mapping each match to its true tournament stage.
2. **Knockout Flag Consistency:**
   - In `data/matches.csv`, `knock_out == 1` holds for all 20 playoff matches and `knock_out == 0` holds for all 351 league matches. There are zero metadata classification contradictions.
3. **Upstream Exclusion of Match 21586:**
   - Match `21586` is confirmed as the 2023 Final.
   - Because it was revised under DLS to 15 overs in Innings 2, it was excluded upstream during Step 1/Step 2/Step 4 cohort filtering.
   - Per experiment guidelines, no delivery data are invented or imported from excluded matches. The experiment strictly evaluates deliveries present in the frozen Step 5 datasets.

---

## 4. Methodological Implications for the Multiplier Experiment

1. **Asymmetric Exposure Warning:**
   - Over 69% of qualified batters (206 of 297) and 71% of qualified bowlers (210 of 292) have zero knockout deliveries in the dataset (predominantly international-only players, or players from teams that did not reach playoffs).
   - By mathematical design, players with zero knockout exposure will have an adjusted delivery weight equal to their original delivery weight across all balls. Their raw scores, Kish ESS, and shrunk scores will remain identical to baseline.
2. **Knockout Multiplier Mechanics:**
   - For deliveries where `match_id` is in the 19 audited knockout matches:
     $$w_i^{\text{adj}} = w_i^{\text{orig}} \times M$$
     where $M \in \{1.00, 1.10, 1.20, 1.25\}$.
   - For all other deliveries (IPL league matches and all T20I matches):
     $$w_i^{\text{adj}} = w_i^{\text{orig}} \times 1.00$$
   - Kish Effective Sample Size will be recomputed as:
     $$\text{ESS}_{\text{adj}} = \frac{\left(\sum_{i} w_i^{\text{adj}}\right)^2}{\sum_{i} (w_i^{\text{adj}})^2}$$
   - Shrunk scores will be re-evaluated as:
     $$\text{Score}_{\text{shrunk}}^{\text{adj}} = \text{Score}_{\text{raw}}^{\text{adj}} \times \frac{\text{ESS}_{\text{adj}}}{\text{ESS}_{\text{adj}} + K}$$
     with frozen $K_{\text{bat}} = 600$ and $K_{\text{bowl}} = 500$.

---

## 5. Audit Certification & Sign-off

The 19 active knockout matches and 1 excluded DLS match have been fully audited, cross-verified, and certified.
**Gate Status:** Ready for user review and confirmation before proceeding to score recalculation.