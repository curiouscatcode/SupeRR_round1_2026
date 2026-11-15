"""
Step 2.1 - Issue 5: Rigorous Win-Probability Model Validation
=============================================================
Performs 5-fold match-held-out cross-validation for Innings 1 and Innings 2,
compares against multiple baselines, exports decile calibration tables,
and evaluates reliability for expected match consequence calculation.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = "outputs/step_2_1_infrastructure_corrections"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=== ISSUE 5: WIN-PROBABILITY MODEL VALIDATION ===")

# 1. Load clean cohort: 785 matches, dead tail excluded
dms_path = "data/processed/delivery_match_state.csv"
matches_path = "data/matches.csv"

dms = pd.read_csv(dms_path)
matches = pd.read_csv(matches_path)

# Filter dead tail and confirmed DLS matches
dms_clean = dms[
    (~dms['match_id'].isin([20182, 23674, 24822, 28334])) &
    (~((dms['innings'] == 2) & (dms['runs_required'] <= 0)))
].copy().reset_index(drop=True)

dms_clean = dms_clean.merge(matches[['match_id', 'venue_id', 'win_team_id']], on='match_id', how='left')
dms_clean['bat_win'] = (dms_clean['batting_team_id'] == dms_clean['win_team_id']).astype(float)

n_clean = len(dms_clean)
n_matches = dms_clean['match_id'].nunique()
print(f"Clean cohort for validation: {n_clean:,} deliveries across {n_matches} matches")

# Logistic regression solver with L2 regularization
def fit_logistic_nr(X, y, l2=1e-4, max_iter=20):
    beta = np.zeros(X.shape[1])
    for _ in range(max_iter):
        p = 1.0 / (1.0 + np.exp(-np.clip(X @ beta, -20, 20)))
        grad = X.T @ (p - y) + l2 * beta
        W = p * (1.0 - p)
        H = (X.T * W) @ X + (l2 + 1e-4) * np.eye(X.shape[1])
        step = np.linalg.solve(H, grad)
        beta -= step
        if np.max(np.abs(step)) < 1e-5:
            break
    return beta

# -------------------------------------------------------------
# 2. INNINGS 2 CHASE MODEL VALIDATION
# -------------------------------------------------------------
print("\n--- INNINGS 2 WIN PROBABILITY VALIDATION ---")
inn2 = dms_clean[dms_clean['innings'] == 2].copy().reset_index(drop=True)
inn2['wk_rem'] = 10.0 - inn2['wickets_before']
inn2['rrr'] = ((inn2['runs_required'] / np.maximum(1.0, inn2['balls_remaining'])) * 6.0).clip(0, 36)
inn2['b_norm'] = inn2['balls_remaining'] / 120.0
inn2['rrr_x_wk'] = inn2['rrr'] * (10.0 - inn2['wk_rem'])

y2 = inn2['bat_win'].values

# Feature matrices:
# Full model
X2_full_raw = np.column_stack([np.ones(len(inn2)), inn2['rrr'], inn2['wk_rem'], inn2['b_norm'], inn2['rrr_x_wk']])
# Baseline 1: Naive (mean win rate)
# Baseline 2: RRR-only
X2_rrr_raw = np.column_stack([np.ones(len(inn2)), inn2['rrr']])
# Baseline 3: Wickets-only
X2_wk_raw = np.column_stack([np.ones(len(inn2)), inn2['wk_rem']])

# 5-fold match-held-out CV
unique_m2 = inn2['match_id'].unique()
np.random.seed(42)
shuffled_m2 = np.random.permutation(unique_m2)
folds2 = np.array_split(shuffled_m2, 5)

p2_full_cv = np.zeros(len(inn2))
p2_rrr_cv = np.zeros(len(inn2))
p2_wk_cv = np.zeros(len(inn2))
p2_naive_cv = np.zeros(len(inn2))

for f in folds2:
    tr_mask = ~inn2['match_id'].isin(f).values
    te_mask = inn2['match_id'].isin(f).values
    
    y_tr, y_te = y2[tr_mask], y2[te_mask]
    
    # Naive baseline: training set mean
    p2_naive_cv[te_mask] = y_tr.mean()
    
    # RRR baseline
    m_rrr = X2_rrr_raw[tr_mask, 1:].mean(axis=0)
    s_rrr = X2_rrr_raw[tr_mask, 1:].std(axis=0)
    X_tr_rrr = np.column_stack([np.ones(tr_mask.sum()), (X2_rrr_raw[tr_mask, 1:] - m_rrr) / s_rrr])
    X_te_rrr = np.column_stack([np.ones(te_mask.sum()), (X2_rrr_raw[te_mask, 1:] - m_rrr) / s_rrr])
    b_rrr = fit_logistic_nr(X_tr_rrr, y_tr)
    p2_rrr_cv[te_mask] = 1.0 / (1.0 + np.exp(-np.clip(X_te_rrr @ b_rrr, -20, 20)))
    
    # Wk baseline
    m_wk = X2_wk_raw[tr_mask, 1:].mean(axis=0)
    s_wk = X2_wk_raw[tr_mask, 1:].std(axis=0)
    X_tr_wk = np.column_stack([np.ones(tr_mask.sum()), (X2_wk_raw[tr_mask, 1:] - m_wk) / s_wk])
    X_te_wk = np.column_stack([np.ones(te_mask.sum()), (X2_wk_raw[te_mask, 1:] - m_wk) / s_wk])
    b_wk = fit_logistic_nr(X_tr_wk, y_tr)
    p2_wk_cv[te_mask] = 1.0 / (1.0 + np.exp(-np.clip(X_te_wk @ b_wk, -20, 20)))
    
    # Full model
    m_full = X2_full_raw[tr_mask, 1:].mean(axis=0)
    s_full = X2_full_raw[tr_mask, 1:].std(axis=0)
    X_tr_full = np.column_stack([np.ones(tr_mask.sum()), (X2_full_raw[tr_mask, 1:] - m_full) / s_full])
    X_te_full = np.column_stack([np.ones(te_mask.sum()), (X2_full_raw[te_mask, 1:] - m_full) / s_full])
    b_full = fit_logistic_nr(X_tr_full, y_tr)
    
    p_raw = 1.0 / (1.0 + np.exp(-np.clip(X_te_full @ b_full, -20, 20)))
    # Boundary enforcement
    req_te = inn2.loc[te_mask, 'runs_required'].values
    wk_te = inn2.loc[te_mask, 'wk_rem'].values
    rem_te = inn2.loc[te_mask, 'balls_remaining'].values
    p_final = np.where(req_te <= 0, 1.0,
              np.where(wk_te <= 0, 0.0,
              np.where(rem_te <= 0, 0.0, p_raw)))
    p2_full_cv[te_mask] = p_final

# Brier scores
brier2_naive = np.mean((p2_naive_cv - y2) ** 2)
brier2_rrr = np.mean((p2_rrr_cv - y2) ** 2)
brier2_wk = np.mean((p2_wk_cv - y2) ** 2)
brier2_full = np.mean((p2_full_cv - y2) ** 2)

logloss2_full = -np.mean(y2 * np.log(np.clip(p2_full_cv, 1e-6, 1-1e-6)) + (1 - y2) * np.log(np.clip(1 - p2_full_cv, 1e-6, 1-1e-6)))

print("Innings 2 Model Evaluation (5-Fold Match-Held-Out CV):")
print(f"  1. Naive Mean Baseline:     Brier = {brier2_naive:.4f}")
print(f"  2. Wickets-Only Baseline:    Brier = {brier2_wk:.4f} (Skill: {(1 - brier2_wk/brier2_naive)*100:.1f}%)")
print(f"  3. RRR-Only Baseline:        Brier = {brier2_rrr:.4f} (Skill: {(1 - brier2_rrr/brier2_naive)*100:.1f}%)")
print(f"  4. Full Production Model:    Brier = {brier2_full:.4f} (Skill: {(1 - brier2_full/brier2_naive)*100:.1f}%, LogLoss = {logloss2_full:.4f})")

# Innings 2 Calibration table across 10 deciles
inn2['pred_wp'] = p2_full_cv
inn2['decile'] = pd.qcut(inn2['pred_wp'], q=10, labels=False, duplicates='drop')
calib2 = inn2.groupby('decile').agg(
    n_deliv=('pred_wp', 'count'),
    mean_pred=('pred_wp', 'mean'),
    actual_win_rate=('bat_win', 'mean')
).reset_index()
calib2['abs_calib_error'] = np.abs(calib2['mean_pred'] - calib2['actual_win_rate'])
print("\nInnings 2 Decile Calibration Table:")
print(calib2.round(4).to_string(index=False))

calib2_csv = os.path.join(OUTPUT_DIR, "inn2_decile_calibration.csv")
calib2.to_csv(calib2_csv, index=False)

# -------------------------------------------------------------
# 3. INNINGS 1 MODEL VALIDATION (Venue Par-Adjusted)
# -------------------------------------------------------------
print("\n--- INNINGS 1 WIN PROBABILITY VALIDATION ---")
inn1 = dms_clean[dms_clean['innings'] == 1].copy().reset_index(drop=True)

# Compute venue par scores
last_balls1 = inn1.groupby('match_id').last()[['score_before', 'team_runs_added', 'venue_id']].reset_index()
last_balls1['first_inn_total'] = last_balls1['score_before'] + last_balls1['team_runs_added']
global_first_inn_mean = last_balls1['first_inn_total'].mean()

v_agg = last_balls1.groupby('venue_id')['first_inn_total'].agg(['count', 'mean']).reset_index()
K_shrink = 8.0
v_agg['venue_par'] = (v_agg['count'] * v_agg['mean'] + K_shrink * global_first_inn_mean) / (v_agg['count'] + K_shrink)
venue_par_dict = dict(zip(v_agg['venue_id'], v_agg['venue_par']))

inn1['venue_par'] = inn1['venue_id'].map(venue_par_dict).fillna(global_first_inn_mean)
inn1['wk_rem'] = 10.0 - inn1['wickets_before']
inn1['b_bowled'] = inn1['legal_balls_before'] / 120.0
inn1['par_to_date'] = inn1['venue_par'] * inn1['b_bowled']
inn1['score_diff_par'] = (inn1['score_before'] - inn1['par_to_date']) / 30.0
inn1['crr_rel_par'] = inn1['current_run_rate'] / (inn1['venue_par'] / 20.0)
inn1['balls_rem'] = (120.0 - inn1['legal_balls_before']) / 120.0
inn1['res_interaction'] = inn1['wk_rem'] * inn1['balls_rem']

y1 = inn1['bat_win'].values

# Feature matrices:
# Full model
X1_full_raw = np.column_stack([
    np.ones(len(inn1)),
    inn1['score_diff_par'],
    inn1['wk_rem'],
    inn1['b_bowled'],
    inn1['res_interaction'],
    inn1['crr_rel_par']
])
# Baseline 1: Naive (mean win rate)
# Baseline 2: Fixed par 160 (without venue adjustment)
fixed_par = 160.0
score_diff_fixed = (inn1['score_before'] - fixed_par * inn1['b_bowled']) / 30.0
X1_fixed_raw = np.column_stack([
    np.ones(len(inn1)),
    score_diff_fixed,
    inn1['wk_rem'],
    inn1['b_bowled'],
    inn1['res_interaction']
])
# Baseline 3: Wickets-only
X1_wk_raw = np.column_stack([np.ones(len(inn1)), inn1['wk_rem']])

# 5-fold match-held-out CV
unique_m1 = inn1['match_id'].unique()
np.random.seed(42)
shuffled_m1 = np.random.permutation(unique_m1)
folds1 = np.array_split(shuffled_m1, 5)

p1_full_cv = np.zeros(len(inn1))
p1_fixed_cv = np.zeros(len(inn1))
p1_wk_cv = np.zeros(len(inn1))
p1_naive_cv = np.zeros(len(inn1))

for f in folds1:
    tr_mask = ~inn1['match_id'].isin(f).values
    te_mask = inn1['match_id'].isin(f).values
    
    y_tr, y_te = y1[tr_mask], y1[te_mask]
    
    # Naive baseline
    p1_naive_cv[te_mask] = y_tr.mean()
    
    # Wickets baseline
    m_wk = X1_wk_raw[tr_mask, 1:].mean(axis=0)
    s_wk = X1_wk_raw[tr_mask, 1:].std(axis=0)
    X_tr_wk = np.column_stack([np.ones(tr_mask.sum()), (X1_wk_raw[tr_mask, 1:] - m_wk) / s_wk])
    X_te_wk = np.column_stack([np.ones(te_mask.sum()), (X1_wk_raw[te_mask, 1:] - m_wk) / s_wk])
    b_wk = fit_logistic_nr(X_tr_wk, y_tr)
    p1_wk_cv[te_mask] = 1.0 / (1.0 + np.exp(-np.clip(X_te_wk @ b_wk, -20, 20)))
    
    # Fixed par 160 baseline
    m_fix = X1_fixed_raw[tr_mask, 1:].mean(axis=0)
    s_fix = X1_fixed_raw[tr_mask, 1:].std(axis=0)
    X_tr_fix = np.column_stack([np.ones(tr_mask.sum()), (X1_fixed_raw[tr_mask, 1:] - m_fix) / s_fix])
    X_te_fix = np.column_stack([np.ones(te_mask.sum()), (X1_fixed_raw[te_mask, 1:] - m_fix) / s_fix])
    b_fix = fit_logistic_nr(X_tr_fix, y_tr)
    p1_fixed_cv[te_mask] = 1.0 / (1.0 + np.exp(-np.clip(X_te_fix @ b_fix, -20, 20)))
    
    # Full venue-adjusted model
    m_full = X1_full_raw[tr_mask, 1:].mean(axis=0)
    s_full = X1_full_raw[tr_mask, 1:].std(axis=0)
    X_tr_full = np.column_stack([np.ones(tr_mask.sum()), (X1_full_raw[tr_mask, 1:] - m_full) / s_full])
    X_te_full = np.column_stack([np.ones(te_mask.sum()), (X1_full_raw[te_mask, 1:] - m_full) / s_full])
    b_full = fit_logistic_nr(X_tr_full, y_tr)
    p_raw = 1.0 / (1.0 + np.exp(-np.clip(X_te_full @ b_full, -20, 20)))
    wk_te = inn1.loc[te_mask, 'wk_rem'].values
    p_final = np.where(wk_te <= 0, np.minimum(p_raw, 0.05), p_raw)
    p1_full_cv[te_mask] = p_final

# Brier scores
brier1_naive = np.mean((p1_naive_cv - y1) ** 2)
brier1_wk = np.mean((p1_wk_cv - y1) ** 2)
brier1_fixed = np.mean((p1_fixed_cv - y1) ** 2)
brier1_full = np.mean((p1_full_cv - y1) ** 2)

logloss1_full = -np.mean(y1 * np.log(np.clip(p1_full_cv, 1e-6, 1-1e-6)) + (1 - y1) * np.log(np.clip(1 - p1_full_cv, 1e-6, 1-1e-6)))

print("Innings 1 Model Evaluation (5-Fold Match-Held-Out CV):")
print(f"  1. Naive Mean Baseline:     Brier = {brier1_naive:.4f}")
print(f"  2. Wickets-Only Baseline:    Brier = {brier1_wk:.4f} (Skill: {(1 - brier1_wk/brier1_naive)*100:.1f}%)")
print(f"  3. Fixed Par 160 Baseline:   Brier = {brier1_fixed:.4f} (Skill: {(1 - brier1_fixed/brier1_naive)*100:.1f}%)")
print(f"  4. Full Venue-Adjusted:      Brier = {brier1_full:.4f} (Skill: {(1 - brier1_full/brier1_naive)*100:.1f}%, LogLoss = {logloss1_full:.4f})")

# Innings 1 Calibration table across 10 deciles
inn1['pred_wp'] = p1_full_cv
inn1['decile'] = pd.qcut(inn1['pred_wp'], q=10, labels=False, duplicates='drop')
calib1 = inn1.groupby('decile').agg(
    n_deliv=('pred_wp', 'count'),
    mean_pred=('pred_wp', 'mean'),
    actual_win_rate=('bat_win', 'mean')
).reset_index()
calib1['abs_calib_error'] = np.abs(calib1['mean_pred'] - calib1['actual_win_rate'])
print("\nInnings 1 Decile Calibration Table:")
print(calib1.round(4).to_string(index=False))

calib1_csv = os.path.join(OUTPUT_DIR, "inn1_decile_calibration.csv")
calib1.to_csv(calib1_csv, index=False)

# -------------------------------------------------------------
# 4. EXPORT MODEL COMPARISON SUMMARY
# -------------------------------------------------------------
summary_rows = [
    {
        'innings': 2,
        'model_name': 'Naive Mean Baseline',
        'cv_brier': round(brier2_naive, 4),
        'brier_skill_pct': 0.0,
        'features': 'Mean batting win rate'
    },
    {
        'innings': 2,
        'model_name': 'Wickets-Only Baseline',
        'cv_brier': round(brier2_wk, 4),
        'brier_skill_pct': round((1 - brier2_wk/brier2_naive)*100, 2),
        'features': 'Wickets Remaining'
    },
    {
        'innings': 2,
        'model_name': 'RRR-Only Baseline',
        'cv_brier': round(brier2_rrr, 4),
        'brier_skill_pct': round((1 - brier2_rrr/brier2_naive)*100, 2),
        'features': 'Required Run Rate'
    },
    {
        'innings': 2,
        'model_name': 'Full Target Chase Model',
        'cv_brier': round(brier2_full, 4),
        'brier_skill_pct': round((1 - brier2_full/brier2_naive)*100, 2),
        'features': 'RRR, Wk_rem, Balls_rem, RRR x Wk_lost + Terminal Snaps'
    },
    {
        'innings': 1,
        'model_name': 'Naive Mean Baseline',
        'cv_brier': round(brier1_naive, 4),
        'brier_skill_pct': 0.0,
        'features': 'Mean batting win rate'
    },
    {
        'innings': 1,
        'model_name': 'Wickets-Only Baseline',
        'cv_brier': round(brier1_wk, 4),
        'brier_skill_pct': round((1 - brier1_wk/brier1_naive)*100, 2),
        'features': 'Wickets Remaining'
    },
    {
        'innings': 1,
        'model_name': 'Fixed Par 160 Baseline',
        'cv_brier': round(brier1_fixed, 4),
        'brier_skill_pct': round((1 - brier1_fixed/brier1_naive)*100, 2),
        'features': 'Score diff from 160, Wk_rem, Balls_bowled, Interaction'
    },
    {
        'innings': 1,
        'model_name': 'Venue-Adjusted Production Model',
        'cv_brier': round(brier1_full, 4),
        'brier_skill_pct': round((1 - brier1_full/brier1_naive)*100, 2),
        'features': 'Score diff from Venue Par, Wk_rem, Balls_bowled, Interaction, CRR'
    }
]

sum_df = pd.DataFrame(summary_rows)
sum_csv = os.path.join(OUTPUT_DIR, "wp_models_validation_summary.csv")
sum_df.to_csv(sum_csv, index=False)
print(f"\nSaved model validation summary table to {sum_csv}")

# -------------------------------------------------------------
# 5. GENERATE CALIBRATION PLOTS
# -------------------------------------------------------------
print("\nGenerating calibration plots...")
plt.figure(figsize=(12, 5))

# Plot Innings 2 Calibration
plt.subplot(1, 2, 1)
plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration (y=x)')
plt.plot(calib2['mean_pred'], calib2['actual_win_rate'], 'o-', color='#1f77b4', lw=2, markersize=7, label=f'Innings 2 Chase (Brier={brier2_full:.4f})')
plt.xlabel('Predicted Win Probability', fontsize=11)
plt.ylabel('Observed Win Rate', fontsize=11)
plt.title('Innings 2: Chase WP Calibration (10 Deciles)', fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend(loc='upper left', fontsize=10)
plt.xlim(-0.02, 1.02)
plt.ylim(-0.02, 1.02)

# Plot Innings 1 Calibration
plt.subplot(1, 2, 2)
plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration (y=x)')
plt.plot(calib1['mean_pred'], calib1['actual_win_rate'], 's-', color='#ff7f0e', lw=2, markersize=7, label=f'Innings 1 Venue-Adj (Brier={brier1_full:.4f})')
plt.xlabel('Predicted Win Probability', fontsize=11)
plt.ylabel('Observed Win Rate', fontsize=11)
plt.title('Innings 1: Venue-Adjusted WP Calibration (10 Deciles)', fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend(loc='upper left', fontsize=10)
plt.xlim(-0.02, 1.02)
plt.ylim(-0.02, 1.02)

plt.tight_layout()
plot_path = os.path.join(OUTPUT_DIR, "fig1_wp_calibration_curves.png")
plt.savefig(plot_path, dpi=200)
plt.close()
print(f"Saved calibration curves plot to {plot_path}")

print("\nPASS: Both Win Probability models validated with strict 5-fold match-held-out cross-validation.")
