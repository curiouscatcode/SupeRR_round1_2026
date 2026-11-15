"""
Comprehensive Infrastructure Audit Script for Step 2
=====================================================
Audits:
1. Match-state reconstruction (789 core matches, 188,330 deliveries)
2. First-innings state variables & predictability
3. Second-innings state variables, target tracking, dead tail, DLS/interrupted matches
4. Win Probability framework (inputs, coefficients, Brier scores, calibration, sparse states)
5. Expected match consequence feasibility & strictly pre-delivery guarantees
6. Data availability, gaps, and structural limitations
"""

import os
import sys
import numpy as np
import pandas as pd

# Set paths
DATA_DIR = "data"
PROCESSED_DIR = "data/processed"
WPA_DIR = "outputs/step_16_5_wpa_investigation"

print("--- 1. LOADING DATASETS ---")
matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
comps = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
dms = pd.read_csv(os.path.join(PROCESSED_DIR, "delivery_match_state.csv"))
dpi = pd.read_csv(os.path.join(PROCESSED_DIR, "delivery_pressure_index.csv"))

print(f"Total raw matches: {len(matches)}")
print(f"Total processed deliveries in delivery_match_state: {len(dms):,}")
print(f"Unique matches in delivery_match_state: {dms['match_id'].nunique()}")

# -------------------------------------------------------------------------
# AUDIT 1: MATCH-STATE RECONSTRUCTION
# -------------------------------------------------------------------------
print("\n--- AUDIT 1: MATCH-STATE RECONSTRUCTION ---")

# Verify score_before continuity:
# For each ball, score_after = score_before + team_runs_added
# Next ball score_before should equal previous ball's score_before + team_runs_added
dms['calc_next_score'] = dms['score_before'] + dms['team_runs_added']
dms['next_score_before'] = dms.groupby(['match_id', 'innings'])['score_before'].shift(-1)
score_discrepancies = dms[dms['next_score_before'].notna() & (dms['calc_next_score'] != dms['next_score_before'])]
print(f"Score continuity discrepancies: {len(score_discrepancies)}")

# Verify wickets_before continuity:
dms['calc_next_wickets'] = dms['wickets_before'] + dms['is_wicket']
dms['next_wickets_before'] = dms.groupby(['match_id', 'innings'])['wickets_before'].shift(-1)
wicket_discrepancies = dms[dms['next_wickets_before'].notna() & (dms['calc_next_wickets'] != dms['next_wickets_before'])]
print(f"Wicket continuity discrepancies: {len(wicket_discrepancies)}")

# Verify legal_balls_before continuity:
dms['calc_next_legal'] = dms['legal_balls_before'] + dms['is_legal_ball'].astype(int)
dms['next_legal_before'] = dms.groupby(['match_id', 'innings'])['legal_balls_before'].shift(-1)
legal_discrepancies = dms[dms['next_legal_before'].notna() & (dms['calc_next_legal'] != dms['next_legal_before'])]
print(f"Legal balls continuity discrepancies: {len(legal_discrepancies)}")

# Verify balls_remaining = 120 - legal_balls_before
balls_rem_check = (dms['balls_remaining'] == (120 - dms['legal_balls_before'])).all()
print(f"balls_remaining == (120 - legal_balls_before) for all rows: {balls_rem_check}")

# Check minimum and maximum of balls_remaining
print(f"balls_remaining range: [{dms['balls_remaining'].min()}, {dms['balls_remaining'].max()}]")
neg_balls_rem = dms[dms['balls_remaining'] < 0]
print(f"Deliveries with negative balls_remaining (< 0): {len(neg_balls_rem)}")

# Current run rate (CRR) check
# CRR = (score_before / legal_balls_before) * 6.0 when legal_balls_before > 0 else 0.0
calc_crr = np.where(dms['legal_balls_before'] > 0, np.round((dms['score_before'] / dms['legal_balls_before']) * 6.0, 2), 0.0)
crr_diff = np.abs(dms['current_run_rate'] - calc_crr)
print(f"Max CRR difference from formula: {crr_diff.max():.4f}")

# Phase mapping check
pp_check = dms[dms['phase'] == 'PP']['overid'].between(1, 6).all()
mid_check = dms[dms['phase'] == 'Middle']['overid'].between(7, 15).all()
death_check = dms[dms['phase'] == 'Death']['overid'].between(16, 20).all()
print(f"Phase mappings valid: PP={pp_check}, Middle={mid_check}, Death={death_check}")

# Phase overs completed check
# PP: overid - 1
# Middle: overid - 7
# Death: overid - 16
calc_phase_comp = np.where(dms['phase'] == 'PP', dms['overid'] - 1,
                  np.where(dms['phase'] == 'Middle', dms['overid'] - 7, dms['overid'] - 16))
phase_comp_diff = (dms['phase_overs_completed'] != calc_phase_comp).sum()
print(f"Phase overs completed discrepancies: {phase_comp_diff}")

# Check striker_balls_faced_before
# Does it start at 0?
first_bat_bf = dms.groupby(['match_id', 'innings', 'striker_id'])['striker_balls_faced_before'].first()
print(f"All batter appearances start at striker_balls_faced_before == 0: {(first_bat_bf == 0).all()}")

# Check bowler_legal_balls_in_spell_before
first_bowl_balls = dms.groupby(['match_id', 'innings', 'bowler_id'])['bowler_legal_balls_in_spell_before'].first()
print(f"All bowler appearances start at bowler_legal_balls_in_spell_before == 0: {(first_bowl_balls == 0).all()}")

# -------------------------------------------------------------------------
# AUDIT 2: FIRST-INNINGS STATE
# -------------------------------------------------------------------------
print("\n--- AUDIT 2: FIRST-INNINGS STATE ---")
inn1 = dms[dms['innings'] == 1].copy()
print(f"Total Innings 1 deliveries: {len(inn1):,}")
print(f"Innings 1 runs_required all NaN: {inn1['runs_required'].isna().all()}")
print(f"Innings 1 required_run_rate all NaN: {inn1['required_run_rate'].isna().all()}")

# First innings final scores distribution across 789 matches
inn1_last = inn1.groupby('match_id').last()
inn1_totals = inn1_last['score_before'] + inn1_last['team_runs_added']
print(f"Innings 1 Final Score: Mean={inn1_totals.mean():.2f}, Std={inn1_totals.std():.2f}, Min={inn1_totals.min()}, Max={inn1_totals.max()}")
print(f"Innings 1 Wickets Lost at end: Mean={(inn1_last['wickets_before'] + inn1_last['is_wicket']).mean():.2f}")

# Check correlations of 1st inn in-progress metrics with final score at various overs
for target_over in [6, 10, 15, 18]:
    ov_data = inn1[inn1['overid'] == target_over].groupby('match_id').last()
    ov_data['final_score'] = inn1_totals.loc[ov_data.index]
    r_score = np.corrcoef(ov_data['score_before'], ov_data['final_score'])[0, 1]
    r_wk = np.corrcoef(ov_data['wickets_before'], ov_data['final_score'])[0, 1]
    r_crr = np.corrcoef(ov_data['current_run_rate'], ov_data['final_score'])[0, 1]
    print(f"Over {target_over} end: r(score, final)={r_score:.3f}, r(wickets, final)={r_wk:.3f}, r(crr, final)={r_crr:.3f}")

# -------------------------------------------------------------------------
# AUDIT 3: SECOND-INNINGS STATE & CHASE DYNAMICS
# -------------------------------------------------------------------------
print("\n--- AUDIT 3: SECOND-INNINGS STATE & TARGET TRACKING ---")
inn2 = dms[dms['innings'] == 2].copy()
print(f"Total Innings 2 deliveries: {len(inn2):,}")

# Check target calculation: target should equal inn1_total + 1
# Let's verify for all 789 matches:
inn2_first = inn2.groupby('match_id').first()
first_req = inn2_first['runs_required']
target_match_check = (first_req == (inn1_totals.loc[inn2_first.index] + 1)).all()
print(f"Target initialized to inn1_final_score + 1 for all matches: {target_match_check}")

# Check runs_required continuity:
# Next ball runs_required = current runs_required - team_runs_added
inn2['calc_next_req'] = inn2['runs_required'] - inn2['team_runs_added']
inn2['next_req'] = inn2.groupby('match_id')['runs_required'].shift(-1)
req_discrepancies = inn2[inn2['next_req'].notna() & (inn2['calc_next_req'] != inn2['next_req'])]
print(f"runs_required continuity discrepancies: {len(req_discrepancies)}")

# Check dead tail deliveries in Innings 2: runs_required <= 0
dead_tail = inn2[inn2['runs_required'] <= 0]
print(f"Deliveries with runs_required <= 0 (target already reached): {len(dead_tail)}")
print(f"Number of matches containing dead tail deliveries: {dead_tail['match_id'].nunique()}")
print("Dead tail sample rows:")
print(dead_tail[['match_id', 'overid', 'over_ball_num', 'score_before', 'runs_required', 'balls_remaining', 'team_runs_added']].head(5))

# Check deliveries with balls_remaining <= 0 in Innings 2
inn2_zero_balls = inn2[inn2['balls_remaining'] <= 0]
print(f"Deliveries with balls_remaining <= 0 in Innings 2: {len(inn2_zero_balls)}")

# Check RRR formula and edge cases
# RRR = (runs_required / balls_remaining) * 6.0
# When balls_remaining == 0 or runs_required <= 0:
print(f"Innings 2 RRR NaN count: {inn2['required_run_rate'].isna().sum()}")
print(f"Innings 2 RRR range: [{inn2['required_run_rate'].min()}, {inn2['required_run_rate'].max()}]")
print(f"Innings 2 RRR <= 0 count: {(inn2['required_run_rate'] <= 0).sum()}")

# -------------------------------------------------------------------------
# AUDIT 3.1: DLS AND INTERRUPTED MATCH HANDLING IN RAW DATA
# -------------------------------------------------------------------------
print("\n--- AUDIT 3.1: DLS AND INTERRUPTED MATCHES IN RAW DATA ---")
m = matches.merge(comps, on='comp_id', how='left')
def classify_category(row):
    name = str(row['comp_name'])
    fmt = str(row['match_format'])
    if 'IPL' in name: return 'IPL'
    elif fmt == 'T20I': return 'T20I'
    else: return 'Other T20'
m['category'] = m.apply(classify_category, axis=1)

print(f"Total matches in matches.csv: {len(m)}")
print(f"IPL & T20I matches: {len(m[m['category'].isin(['IPL', 'T20I'])])}")

rev_inn1 = m['first_inn_revised_overs'].notna().sum()
rev_inn2 = m['second_inn_revised_overs'].notna().sum()
rev_target = m['revised_target'].notna().sum()
no_res = m['result'].isin(['No Result', 'Match Abandoned']).sum()
print(f"Matches with revised 1st inn overs: {rev_inn1}")
print(f"Matches with revised 2nd inn overs: {rev_inn2}")
print(f"Matches with revised target: {rev_target}")
print(f"No result / Abandoned matches: {no_res}")

excluded_matches = m[
    (m['category'].isin(['IPL', 'T20I'])) &
    (m['first_inn_revised_overs'].notna() | m['second_inn_revised_overs'].notna() | m['revised_target'].notna() | m['result'].isin(['No Result', 'Match Abandoned']))
]
print(f"Total IPL/T20I matches excluded due to rain/shortened/DLS/abandoned: {len(excluded_matches)}")
print("Breakdown of excluded IPL/T20I matches:")
print(excluded_matches[['match_id', 'comp_name', 'match_date', 'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target', 'result']].head(10))

# -------------------------------------------------------------------------
# AUDIT 4: WIN PROBABILITY IMPLEMENTATION AUDIT
# -------------------------------------------------------------------------
print("\n--- AUDIT 4: WIN PROBABILITY FRAMEWORK AUDIT ---")
wpa_parquet = os.path.join(WPA_DIR, "delivery_wpa_leverage.parquet")
if os.path.exists(wpa_parquet):
    df_wpa = pd.read_parquet(wpa_parquet)
    print(f"Loaded delivery_wpa_leverage.parquet: {len(df_wpa):,} rows")
    print(f"Columns: {list(df_wpa.columns)}")
    
    # Check wp_before range
    print(f"wp_before range: [{df_wpa['wp_before'].min():.4f}, {df_wpa['wp_before'].max():.4f}]")
    print(f"wp_after range:  [{df_wpa['wp_after'].min():.4f}, {df_wpa['wp_after'].max():.4f}]")
    print(f"Nulls in wp_before: {df_wpa['wp_before'].isna().sum()}")
    print(f"Nulls in wp_after:  {df_wpa['wp_after'].isna().sum()}")
    print(f"Nulls in expected_leverage_pct: {df_wpa['expected_leverage_pct'].isna().sum()}")
    print(f"Mean Expected Leverage: {df_wpa['expected_leverage_pct'].mean():.3f}%")
    print(f"Median Expected Leverage: {df_wpa['expected_leverage_pct'].median():.3f}%")
else:
    print("delivery_wpa_leverage.parquet not found!")

# Outcome probability matrix check
outcome_csv = os.path.join(WPA_DIR, "situation_outcome_probabilities.csv")
if os.path.exists(outcome_csv):
    out_prob = pd.read_csv(outcome_csv)
    print("\nSituation-dependent Outcome Probabilities:")
    print(out_prob)

print("\n--- SCRIPT COMPLETED SUCCESSFULLY ---")
