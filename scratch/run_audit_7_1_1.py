"""
Step 7.1.1: Targeted Baseline Validation Audit

Investigates four specific issues:
1. Wicket-probability benchmarks (reproduce Brier scores, compare against global and Innings x Format benchmarks).
2. Cell-level out-of-sample errors (run bias and RMSE separately for every cell and fold, check cancellation).
3. Fold parameter stability (identify largest deviations, investigate 1_IPL_Death_7+ cell shift of 0.161 runs/ball).
4. Report accuracy (verify phase scoring progression PP -> Middle -> Death and metric weights).
"""

import os
import json
import numpy as np
import pandas as pd

def compute_rmse(actual, pred):
    return float(np.sqrt(np.mean((actual - pred) ** 2)))

def compute_mae(actual, pred):
    return float(np.mean(np.abs(actual - pred)))

def compute_bias(actual, pred):
    return float(np.mean(pred - actual))

def compute_brier(actual, pred):
    return float(np.mean((actual - pred) ** 2))

def compute_logloss(actual, pred, eps=1e-6):
    p = np.clip(pred, eps, 1.0 - eps)
    return float(-np.mean(actual * np.log(p) + (1.0 - actual) * np.log(1.0 - p)))

def assign_wkt_bucket(df):
    w = df['W_t']
    ph = df['phase']
    bucket = pd.Series(index=df.index, dtype='object')
    bucket[(ph == 'PP') & (w == 0)] = '0'
    bucket[(ph == 'PP') & (w == 1)] = '1'
    bucket[(ph == 'PP') & (w >= 2)] = '2+'
    bucket[(ph == 'Middle') & (w <= 2)] = '0-2'
    bucket[(ph == 'Middle') & (w >= 3) & (w <= 4)] = '3-4'
    bucket[(ph == 'Middle') & (w >= 5)] = '5+'
    bucket[(ph == 'Death') & (w <= 3)] = '0-3'
    bucket[(ph == 'Death') & (w >= 4) & (w <= 6)] = '4-6'
    bucket[(ph == 'Death') & (w >= 7)] = '7+'
    return bucket

# Load data
print("Loading datasets...")
bat = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bowl = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')
matches = pd.read_csv('data/matches.csv')
comps = pd.read_csv('data/competitions.csv')
m_comp = matches.merge(comps, on='comp_id', how='left')[['match_id', 'match_format']]
m_comp['format'] = m_comp['match_format'].map({'T20': 'IPL', 'T20I': 'T20I'})

bat = bat.merge(m_comp[['match_id', 'format']], on='match_id', how='left')
bowl = bowl.merge(m_comp[['match_id', 'format']], on='match_id', how='left')

bat['wkt_bucket'] = assign_wkt_bucket(bat)
bowl['wkt_bucket'] = assign_wkt_bucket(bowl)

cell_id_func = lambda df: df['innings'].astype(str) + '_' + df['format'] + '_' + df['phase'] + '_' + df['wkt_bucket']
bat['cell_id'] = cell_id_func(bat)
bowl['cell_id'] = cell_id_func(bowl)

bat_faced = bat[bat['is_batter_ball_faced'] == True].copy()
bowl_legal = bowl[bowl['is_legal_ball'] == True].copy()

# Folds (exact replication of Step 7.1)
unique_matches = bat_faced[['match_id', 'format']].drop_duplicates().sort_values('match_id').reset_index(drop=True)
rng = np.random.RandomState(42)
unique_matches['fold'] = -1
for fmt in ['IPL', 'T20I']:
    fmt_indices = unique_matches[unique_matches['format'] == fmt].index.values.copy()
    rng.shuffle(fmt_indices)
    fold_splits = np.array_split(fmt_indices, 5)
    for fold_idx, split_idx in enumerate(fold_splits):
        unique_matches.loc[split_idx, 'fold'] = fold_idx + 1

bat_faced = bat_faced.merge(unique_matches[['match_id', 'fold']], on='match_id', how='left')
bowl_legal = bowl_legal.merge(unique_matches[['match_id', 'fold']], on='match_id', how='left')

print("\n=======================================================")
print("=== 1. WICKET PROBABILITY BENCHMARK COMPARISONS ===")
print("=======================================================")

def evaluate_benchmarks(df, target_col, disc_name):
    records = []
    for fold in range(1, 6):
        train = df[df['fold'] != fold]
        test = df[df['fold'] == fold].copy()
        
        # Benchmark 1: Global Training Fold Mean (1 parameter)
        p_global = float(train[target_col].mean())
        test['pred_global'] = p_global
        
        # Benchmark 2: Innings x Format Training Fold Mean (4 cells)
        m2_base = train.groupby(['innings', 'format'])[target_col].mean().reset_index(name='pred_m2')
        test = test.merge(m2_base, on=['innings', 'format'], how='left')
        
        # Model 3: Step 7.1 Full 36-Cell Model
        m3_base = train.groupby(['innings', 'format', 'phase', 'wkt_bucket'])[target_col].mean().reset_index(name='pred_36cell')
        test = test.merge(m3_base, on=['innings', 'format', 'phase', 'wkt_bucket'], how='left')
        
        y_true = test[target_col].astype(float).values
        n_test = len(y_true)
        prev = float(np.mean(y_true))
        
        models = [
            ('Global Mean (1 param)', test['pred_global'].values),
            ('Innings x Format (4 cells)', test['pred_m2'].values),
            ('36-Cell Model (Approved)', test['pred_36cell'].values)
        ]
        
        for m_name, y_pred in models:
            brier = compute_brier(y_true, y_pred)
            logloss = compute_logloss(y_true, y_pred)
            bias = compute_bias(y_true, y_pred)
            
            # Calibration slope & intercept via linear regression y ~ pred
            # Slope = Cov(y, pred) / Var(pred)
            cov_yp = np.cov(y_true, y_pred)[0, 1] if np.var(y_pred) > 0 else 0
            var_p = np.var(y_pred)
            cal_slope = cov_yp / var_p if var_p > 1e-12 else np.nan
            cal_intercept = prev - cal_slope * np.mean(y_pred) if not np.isnan(cal_slope) else prev
            
            records.append({
                'discipline': disc_name,
                'fold': fold,
                'model': m_name,
                'test_deliveries': n_test,
                'prevalence': prev,
                'brier_score': brier,
                'log_loss': logloss,
                'mean_bias': bias,
                'cal_slope': cal_slope,
                'cal_intercept': cal_intercept
            })
            
    return pd.DataFrame(records)

bench_bat = evaluate_benchmarks(bat_faced, 'is_striker_dismissed', 'Batting Dismissal')
bench_bowl = evaluate_benchmarks(bowl_legal, 'is_bowler_wicket', 'Bowling Wicket')
bench_all = pd.concat([bench_bat, bench_bowl], ignore_index=True)

bench_summary = bench_all.groupby(['discipline', 'model']).agg(
    mean_brier=('brier_score', 'mean'),
    std_brier=('brier_score', 'std'),
    mean_logloss=('log_loss', 'mean'),
    mean_bias=('mean_bias', 'mean'),
    mean_cal_slope=('cal_slope', 'mean'),
    mean_cal_intercept=('cal_intercept', 'mean')
).reset_index()

print("\nBenchmark Summary (5-Fold Out-of-Sample Means):")
print(bench_summary.to_string(index=False))

# Relative improvement calculation
for disc in ['Batting Dismissal', 'Bowling Wicket']:
    sub = bench_summary[bench_summary['discipline'] == disc]
    brier_null = sub[sub['model'] == 'Global Mean (1 param)']['mean_brier'].values[0]
    brier_m2 = sub[sub['model'] == 'Innings x Format (4 cells)']['mean_brier'].values[0]
    brier_36 = sub[sub['model'] == '36-Cell Model (Approved)']['mean_brier'].values[0]
    
    brier_skill_score_36 = (brier_null - brier_36) / brier_null * 100
    brier_skill_score_m2 = (brier_null - brier_m2) / brier_null * 100
    print(f"\n{disc} Brier Skill Score relative to Global Mean:")
    print(f"  Innings x Format (4 cells):  {brier_skill_score_m2:.4f}% improvement")
    print(f"  36-Cell Model:               {brier_skill_score_36:.4f}% improvement")


print("\n=======================================================")
print("=== 2. CELL-LEVEL OUT-OF-SAMPLE ERROR ANALYSIS ===")
print("=======================================================")

cell_cv_records = []
for fold in range(1, 6):
    train = bat_faced[bat_faced['fold'] != fold]
    test = bat_faced[bat_faced['fold'] == fold]
    
    m3_base = train.groupby('cell_id').agg(
        pred_runs=('batter_runs', 'mean'),
        pred_wkt=('is_striker_dismissed', 'mean')
    ).reset_index()
    
    test_merged = test.merge(m3_base, on='cell_id', how='left')
    
    for cell_id, g in test_merged.groupby('cell_id'):
        y_r = g['batter_runs'].values
        p_r = g['pred_runs'].values
        y_w = g['is_striker_dismissed'].astype(float).values
        p_w = g['pred_wkt'].values
        
        cell_cv_records.append({
            'fold': fold,
            'cell_id': cell_id,
            'n_test': len(g),
            'actual_runs': float(np.mean(y_r)),
            'pred_runs': float(np.mean(p_r)),
            'run_bias': float(np.mean(p_r - y_r)),
            'run_rmse': float(np.sqrt(np.mean((y_r - p_r)**2))),
            'actual_wkt': float(np.mean(y_w)),
            'pred_wkt': float(np.mean(p_w)),
            'wkt_bias': float(np.mean(p_w - y_w))
        })

cell_cv_df = pd.DataFrame(cell_cv_records)

# Summarize per cell across all 5 folds
cell_summary = cell_cv_df.groupby('cell_id').agg(
    total_test_deliveries=('n_test', 'sum'),
    mean_pred_runs=('pred_runs', 'mean'),
    mean_actual_runs=('actual_runs', 'mean'),
    mean_run_bias=('run_bias', 'mean'),
    std_run_bias=('run_bias', 'std'),
    mean_run_rmse=('run_rmse', 'mean'),
    mean_pred_wkt=('pred_wkt', 'mean'),
    mean_actual_wkt=('actual_wkt', 'mean'),
    mean_wkt_bias=('wkt_bias', 'mean'),
    folds_positive_bias=('run_bias', lambda x: int(np.sum(x > 0))),
    folds_negative_bias=('run_bias', lambda x: int(np.sum(x < 0)))
).reset_index()

print("\nCell-Level Error Distribution Summary across 36 Cells:")
print(f"Mean Cell Run Bias across all cells: {cell_summary['mean_run_bias'].mean():.5f}")
print(f"Median Cell Run Bias: {cell_summary['mean_run_bias'].median():.5f}")
print(f"Min Cell Run Bias: {cell_summary['mean_run_bias'].min():.5f} (most under-predicting)")
print(f"Max Cell Run Bias: {cell_summary['mean_run_bias'].max():.5f} (most over-predicting)")
print(f"Number of cells with consistent positive bias (all 5 folds > 0): {len(cell_summary[cell_summary['folds_positive_bias'] == 5])}")
print(f"Number of cells with consistent negative bias (all 5 folds < 0): {len(cell_summary[cell_summary['folds_negative_bias'] == 5])}")

print("\nTop 5 Cells with Largest Positive Run Bias (Over-predicting):")
print(cell_summary.sort_values('mean_run_bias', ascending=False).head(5)[['cell_id', 'total_test_deliveries', 'mean_pred_runs', 'mean_actual_runs', 'mean_run_bias', 'std_run_bias', 'folds_positive_bias']].to_string(index=False))

print("\nTop 5 Cells with Largest Negative Run Bias (Under-predicting):")
print(cell_summary.sort_values('mean_run_bias', ascending=True).head(5)[['cell_id', 'total_test_deliveries', 'mean_pred_runs', 'mean_actual_runs', 'mean_run_bias', 'std_run_bias', 'folds_negative_bias']].to_string(index=False))

# Check cancellation
weighted_bias = np.sum(cell_summary['mean_run_bias'] * cell_summary['total_test_deliveries']) / np.sum(cell_summary['total_test_deliveries'])
mean_abs_cell_bias = float(np.mean(np.abs(cell_summary['mean_run_bias'])))
weighted_abs_cell_bias = float(np.sum(np.abs(cell_summary['mean_run_bias']) * cell_summary['total_test_deliveries']) / np.sum(cell_summary['total_test_deliveries']))

print(f"\nCancellation Audit:")
print(f"  Weighted Aggregate Run Bias:         {weighted_bias:.6f} runs/ball")
print(f"  Unweighted Mean Absolute Cell Bias:  {mean_abs_cell_bias:.6f} runs/ball")
print(f"  Delivery-Weighted Mean Absolute Bias: {weighted_abs_cell_bias:.6f} runs/ball")


print("\n=======================================================")
print("=== 3. FOLD PARAMETER STABILITY INVESTIGATION ===")
print("=======================================================")

# Read cell diagnostics
diag_bat = pd.read_csv('outputs/step_7_empirical_calibration/cell_diagnostics_batting.csv')
diag_bowl = pd.read_csv('outputs/step_7_empirical_calibration/cell_diagnostics_bowling.csv')

print("\nTop 5 Cells with Largest Parameter Deviation Across 5 Folds (Batting):")
print(diag_bat[['cell_id', 'n_deliveries', 'exp_runs', 'se_runs', 'max_run_dev', 'max_wkt_dev']].sort_values('max_run_dev', ascending=False).head(5).to_string(index=False))

print("\nFull Distribution of max_run_dev (Batting):")
print(f"  Max Shift:    {diag_bat['max_run_dev'].max():.4f} runs/ball")
print(f"  90th Pct:     {diag_bat['max_run_dev'].quantile(0.90):.4f} runs/ball")
print(f"  75th Pct:     {diag_bat['max_run_dev'].quantile(0.75):.4f} runs/ball")
print(f"  Median Shift: {diag_bat['max_run_dev'].median():.4f} runs/ball")
print(f"  25th Pct:     {diag_bat['max_run_dev'].quantile(0.25):.4f} runs/ball")
print(f"  Min Shift:    {diag_bat['max_run_dev'].min():.4f} runs/ball")

# Detailed trace of 1_IPL_Death_7+
target_cell = '1_IPL_Death_7+'
print(f"\nDetailed Fold-by-Fold Inspection for {target_cell}:")
t_records = []
for fold in range(1, 6):
    train = bat_faced[bat_faced['fold'] != fold]
    test = bat_faced[bat_faced['fold'] == fold]
    
    tr_c = train[train['cell_id'] == target_cell]
    te_c = test[test['cell_id'] == target_cell]
    
    t_records.append({
        'fold': fold,
        'train_n': len(tr_c),
        'train_runs': float(tr_c['batter_runs'].mean()),
        'train_var': float(tr_c['batter_runs'].var()),
        'train_se': float(np.sqrt(tr_c['batter_runs'].var() / len(tr_c))),
        'test_n': len(te_c),
        'test_runs': float(te_c['batter_runs'].mean()) if len(te_c) > 0 else np.nan,
        'test_bias': float(tr_c['batter_runs'].mean() - te_c['batter_runs'].mean()) if len(te_c) > 0 else np.nan
    })
t_df = pd.DataFrame(t_records)
print(t_df.to_string(index=False))

# Theoretical sampling bounds for 1_IPL_Death_7+
c_full = bat_faced[bat_faced['cell_id'] == target_cell]
sigma = np.sqrt(c_full['batter_runs'].var())
n_train = len(c_full) * 0.8
theoretical_se_train = sigma / np.sqrt(n_train)
expected_range_5 = 2.326 * theoretical_se_train * np.sqrt(0.2 / 0.8) # fold shift formula
print(f"\nStatistical explanation for {target_cell}:")
print(f"  Total N = {len(c_full)}, SD = {sigma:.3f}, SE = {c_full['batter_runs'].sem():.4f}")
print(f"  Average Training N per fold = {n_train:.0f}, Training SE = {theoretical_se_train:.4f}")
print(f"  Observed Training Mean Range: {t_df['train_runs'].max() - t_df['train_runs'].min():.4f} runs/ball")


print("\n=======================================================")
print("=== 4. REPORT ACCURACY AUDIT (SCORING PROGRESSION) ===")
print("=======================================================")

phase_prog_bat = bat_faced.groupby(['format', 'phase'])['batter_runs'].agg(
    n_balls='count',
    mean_runs='mean'
).reset_index()
phase_prog_bat['rpo'] = phase_prog_bat['mean_runs'] * 6.0

print("Actual Phase Scoring Progression (Batting Balls Faced):")
print(phase_prog_bat.pivot_table(index='format', columns='phase', values='rpo')[['PP', 'Middle', 'Death']].round(2))

# Bowling legal deliveries
phase_prog_bowl = bowl_legal.groupby(['format', 'phase'])['bowler_runs_conceded'].agg(
    n_balls='count',
    mean_runs='mean'
).reset_index()
phase_prog_bowl['rpo'] = phase_prog_bowl['mean_runs'] * 6.0
print("\nActual Phase Scoring Progression (Bowling Legal Deliveries):")
print(phase_prog_bowl.pivot_table(index='format', columns='phase', values='rpo')[['PP', 'Middle', 'Death']].round(2))

print("\n--- AUDIT CALCULATIONS COMPLETE ---")
