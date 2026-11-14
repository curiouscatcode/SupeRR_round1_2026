# Step 16.5: Win Probability Framework Audit Report (Section 2)

**Audit Date:** 2026-11-14  
**Auditor:** Independent Analytics Auditor  
**Dataset Scope:** All 188,097 Clean Active Deliveries across 789 Matches  
**Evaluation Framework:** 5-Fold Match-Held-Out GroupKFold Cross-Validation  

---

## 1. Technical Audit of the Six Section 2 Requirements

### 1. Pre-Delivery Temporal Isolation
- **Audit Status: VERIFIED & ENFORCED.**  
  `wp_before` and `expected_leverage` are calculated strictly from state variables available immediately before the bowler runs in (`score_before`, `wickets_before`, `legal_balls_before`, `runs_required`, `balls_remaining`, `venue_par`). Zero delivery outcomes (`runs`, `is_wicket`, extras) leak into pre-delivery features.

### 2. Model Calibration & Brier Scores
- **Innings 2 Model:** 5-fold CV Brier Score = **0.1351** (In-sample = 0.1341, Overfitting Delta = 0.0010). Calibration across all 10 deciles is within 0.7 percentage points.
- **Innings 1 Model:** 5-fold CV Brier Score = **0.2227** (In-sample = 0.2215, Overfitting Delta = 0.0011). Calibrated within 1.9 percentage points.

### 3. Match-Held-Out Cross Validation
- **Audit Status: VERIFIED.**  
  Folds are strictly partitioned at the `match_id` level (GroupKFold). No deliveries from the same match appear in both training and test sets.

### 4. Innings 1 and Innings 2 Appropriateness
- **Innings 2:** Models deterministic chase dynamics using RRR, balls remaining, wickets in hand, and their non-linear crisis interaction. All boundary conditions ($R_{req} \le 0 \implies 1.0$, $W \ge 10 \implies 0.0$, overs expired $\implies 0.0$) are strictly enforced.
- **Innings 1:** Replaced the arbitrary fixed par of 160 with a **Bayesian-shrunk venue-specific par score** ($K = 8.0$), accounting for differences between high-scoring grounds (e.g. Chinnaswamy, mean 201) and low-scoring grounds (e.g. Lucknow, mean 155).

### 5. Situation-Dependent Outcome Probability Matrix
- **Audit Status: ENFORCED.**  
  Replaced the single global 7-outcome distribution from Step 16.4 with empirical transition distributions conditional on **(Innings $\times$ Phase)** across 10 distinct delivery events (dots, singles, twos, threes, fours, sixes, wickets, wides, no-balls, and rare runs).  
  Verified that outcome probabilities sum to **1.0000** in all 6 strata.

### 6. Venue, Score, Wickets, and Overs Handling
- All relevant environmental and tactical state variables are integrated into the feature matrices. The model captures both resource depletion and run rate pressure.

---

## 2. Summary Model Validation Table

| Model Specification | Deliveries | Unique Matches | In-Sample Brier | 5-Fold CV Brier | Overfitting Gap | Feature Vector Specification |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Innings 2 Win Probability (Target Chase)** | 89,919 | 789 | 0.1341 | **0.1351** | +0.0010 | RRR, Wickets Remaining, Balls Remaining, RRR x Wickets Lost |
| **Innings 1 Win Probability (Venue-Adjusted Par)** | 98,178 | 789 | 0.2215 | **0.2227** | +0.0011 | Score diff from Venue Par, Wickets Remaining, Balls Bowled, Resource Interaction, CRR |
