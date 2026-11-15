"""
Step 2.2 - Investigation 1: Pre-Match Shortened Matches
======================================================
Investigates Match 15795, Match 31278, Match 48514 and scans for any other
shortened matches in the 785 clean cohort.
"""

import os
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_2_2_remaining_validation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=== INVESTIGATION 1: PRE-MATCH SHORTENED MATCHES ===")

# 1. Load data
dms_path = "data/processed/delivery_match_state.csv"
matches_path = "data/matches.csv"
comps_path = "data/competitions.csv"
bbb_path = "data/ball_by_ball.csv"

dms = pd.read_csv(dms_path)
matches = pd.read_csv(matches_path)
comps = pd.read_csv(comps_path)
bbb = pd.read_csv(bbb_path, low_memory=False)

m_all = matches.merge(comps, on='comp_id', how='left')

# Exclude dead tail and 4 confirmed DLS matches
excluded_dls = [20182, 23674, 24822, 28334]
cohort_785_mids = set(dms['match_id'].unique()) - set(excluded_dls)

print(f"Cohort size: {len(cohort_785_mids)} matches")

target_matches = [15795, 31278, 48514]

# 2. Detailed audit of the three target matches
audit_records = []

for mid in target_matches:
    m_meta = m_all[m_all['match_id'] == mid].iloc[0]
    m_dms = dms[dms['match_id'] == mid]
    
    inn1 = m_dms[m_dms['innings'] == 1]
    inn2 = m_dms[m_dms['innings'] == 2]
    
    inn1_max_over = inn1['overid'].max()
    inn1_legal = inn1['is_legal_ball'].sum()
    inn1_wkts = inn1['wickets_before'].iloc[-1] + inn1['is_wicket'].iloc[-1]
    inn1_score = inn1['score_before'].iloc[-1] + inn1['team_runs_added'].iloc[-1]
    
    inn2_max_over = inn2['overid'].max()
    inn2_legal = inn2['is_legal_ball'].sum()
    inn2_wkts = inn2['wickets_before'].iloc[-1] + inn2['is_wicket'].iloc[-1]
    inn2_score = inn2['score_before'].iloc[-1] + inn2['team_runs_added'].iloc[-1]
    
    # Check balls_remaining at start and end of Innings 1 in prepare_match_data
    inn1_start_rem = inn1['balls_remaining'].iloc[0]
    inn1_end_rem = inn1['balls_remaining'].iloc[-1]
    
    # Check balls_remaining and RRR at start of Innings 2 in prepare_match_data
    inn2_start_rem = inn2['balls_remaining'].iloc[0]
    inn2_start_rrr = inn2['required_run_rate'].iloc[0]
    inn2_req = inn2['runs_required'].iloc[0]
    
    # Scheduled overs calculation
    if mid == 15795:
        sched_overs = 12
        sched_balls = 72
        shortened_type = "Pre-toss rain delay (reduced to 12 overs/side)"
    elif mid == 31278:
        sched_overs = 16
        sched_balls = 96
        shortened_type = "Pre-toss rain delay (reduced to 16 overs/side)"
    elif mid == 48514:
        sched_overs = 12
        sched_balls = 72
        shortened_type = "Pre-toss rain delay (reduced to 12 overs/side)"
        
    true_initial_rrr = round((inn2_req / sched_balls) * 6.0, 2)
    pipeline_initial_rrr = inn2_start_rrr
    
    # Phase distribution in pipeline
    phases_present_inn1 = list(inn1['phase'].unique())
    phases_present_inn2 = list(inn2['phase'].unique())
    
    rec = {
        'match_id': mid,
        'competition': m_meta['comp_name'],
        'match_date': m_meta['match_date'],
        'teams': f"{m_meta['home_team']} vs {m_meta['away_team']}",
        'result_string': m_meta['result'],
        'shortened_type': shortened_type,
        'scheduled_overs': sched_overs,
        'scheduled_balls': sched_balls,
        'inn1_actual_overs': f"{inn1_max_over}.0 ({inn1_legal} balls)",
        'inn1_score_wkts': f"{inn1_score}/{inn1_wkts}",
        'inn2_actual_overs': f"{inn2_max_over}.{inn2_legal % 6} ({inn2_legal} balls)",
        'inn2_score_wkts': f"{inn2_score}/{inn2_wkts}",
        'pipeline_inn1_start_rem': inn1_start_rem,
        'pipeline_inn1_end_rem': inn1_end_rem,
        'pipeline_inn2_start_rem': inn2_start_rem,
        'true_target': inn1_score + 1,
        'pipeline_req': inn2_req,
        'pipeline_initial_rrr': pipeline_initial_rrr,
        'true_initial_rrr': true_initial_rrr,
        'rrr_understatement': round(true_initial_rrr - pipeline_initial_rrr, 2),
        'inn1_phases_present': phases_present_inn1,
        'inn2_phases_present': phases_present_inn2,
        'has_death_overs': ('Death' in phases_present_inn1) or ('Death' in phases_present_inn2),
    }
    audit_records.append(rec)

audit_df = pd.DataFrame(audit_records)
print("\nDetailed Investigation Summary of the Three Matches:")
print(audit_df[['match_id', 'competition', 'scheduled_overs', 'pipeline_inn1_end_rem', 'pipeline_initial_rrr', 'true_initial_rrr', 'rrr_understatement', 'has_death_overs']].to_string(index=False))

audit_csv = os.path.join(OUTPUT_DIR, "pre_match_shortened_investigation.csv")
audit_df.to_csv(audit_csv, index=False)
print(f"\nSaved detailed shortened match audit to {audit_csv}")

# 3. Comprehensive scan across all other 782 matches in cohort_785_mids
print("\n--- Scanning Remaining 782 Matches for Any Other Shortened Games ---")

suspicious_matches = []
for mid in cohort_785_mids - set(target_matches):
    m_deliv = dms[dms['match_id'] == mid]
    inn1 = m_deliv[m_deliv['innings'] == 1]
    inn2 = m_deliv[m_deliv['innings'] == 2]
    
    if len(inn1) == 0 or len(inn2) == 0:
        continue
        
    l1 = inn1['is_legal_ball'].sum()
    w1 = inn1['wickets_before'].iloc[-1] + inn1['is_wicket'].iloc[-1]
    max_ov1 = inn1['overid'].max()
    
    l2 = inn2['is_legal_ball'].sum()
    w2 = inn2['wickets_before'].iloc[-1] + inn2['is_wicket'].iloc[-1]
    max_ov2 = inn2['overid'].max()
    
    # Check if Innings 1 terminated before 20 overs without 10 wickets
    # Full 20 overs means either max_ov1 == 20 (and legal balls >= 118) OR wickets == 10
    if max_ov1 < 20 and w1 < 10:
        suspicious_matches.append((mid, 'Inn1 premature', max_ov1, l1, w1))
        
    # Check if Innings 2 reached scheduled over limit < 20 without target reached and without 10 wkts
    last_req = inn2['runs_required'].iloc[-1] - inn2['team_runs_added'].iloc[-1]
    if max_ov2 < 20 and w2 < 10 and last_req > 0 and max_ov1 < 20:
        suspicious_matches.append((mid, 'Inn2 premature', max_ov2, l2, w2))

print(f"Other matches with premature Innings 1 (< 20 overs with < 10 wickets): {len(suspicious_matches)}")
if len(suspicious_matches) > 0:
    for item in suspicious_matches:
        print(item)
else:
    print("Zero other shortened matches exist in the remaining 782 matches. All other matches had full 20 overs in Innings 1 (or 10 wickets).")

# 4. Impact on pressure features
print("\n--- Impact Analysis on Pipeline Features ---")
print("1. Balls Remaining: Assumes 120 balls. For 12-over games, ball 72 is treated as ball 72/120 (48 balls remaining!).")
print("2. Phase Mapping: Overs 1-6 = PP, 7-15 = Middle, 16-20 = Death.")
print("   - In a 12-over game, Death phase is NEVER reached (all overs 7-12 are classified as Middle).")
print("   - In a 16-over game, only over 16 is classified as Death (1 over instead of 4-5 overs).")
print("3. Required Run Rate: Understated by 3.63 RRR (15795), 1.97 RRR (31278), and 3.83 RRR (48514).")
print("4. Bowler/Batter Phase Context: Distorts phase specialist stats and PI calculations.")
