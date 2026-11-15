"""
Step 7.1: Empirical Baseline Construction and Validation

This script constructs and validates the frozen 36-cell situational baseline models
for Batting (PWSVA) and Bowling (SBVA):
    Tensor: Innings (1, 2) x Format (IPL, T20I) x Phase (PP, Middle, Death) x Wickets Bucket (3 tiers)

Eligible delivery subsets:
    - Batting: is_batter_ball_faced == True (179,590 deliveries)
    - Bowling: is_legal_ball == True (178,798 deliveries)

Validation:
    - 5-Fold Stratified Match-Held-Out Cross-Validation (zero within-match leakage)
    - Out-of-sample RMSE, MAE, Mean Bias, Brier Score, Log Loss
    - Cell parameter stability across folds
    - Format comparisons (IPL vs T20I)
    - Boundary and extreme state behavior

Outputs:
    - outputs/step_7_empirical_calibration/batting_baseline_36cells.parquet & .csv
    - outputs/step_7_empirical_calibration/bowling_baseline_36cells.parquet & .csv
    - outputs/step_7_empirical_calibration/cell_diagnostics_batting.csv
    - outputs/step_7_empirical_calibration/cell_diagnostics_bowling.csv
    - outputs/step_7_empirical_calibration/match_cv_validation_results.csv
    - outputs/step_7_empirical_calibration/baseline_quality_summary.json
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
    """
    Assign phase-specific wicket state bucket:
    PP (overs 1-6): '0' (0 down), '1' (1 down), '2+' (2+ down)
    Middle (overs 7-16): '0-2' (0-2 down), '3-4' (3-4 down), '5+' (5+ down)
    Death (overs 17-20): '0-3' (0-3 down), '4-6' (4-6 down), '7+' (7+ down)
    """
    w = df['W_t']
    ph = df['phase']
    bucket = pd.Series(index=df.index, dtype='object')
    
    # PP
    bucket[(ph == 'PP') & (w == 0)] = '0'
    bucket[(ph == 'PP') & (w == 1)] = '1'
    bucket[(ph == 'PP') & (w >= 2)] = '2+'
    
    # Middle
    bucket[(ph == 'Middle') & (w <= 2)] = '0-2'
    bucket[(ph == 'Middle') & (w >= 3) & (w <= 4)] = '3-4'
    bucket[(ph == 'Middle') & (w >= 5)] = '5+'
    
    # Death
    bucket[(ph == 'Death') & (w <= 3)] = '0-3'
    bucket[(ph == 'Death') & (w >= 4) & (w <= 6)] = '4-6'
    bucket[(ph == 'Death') & (w >= 7)] = '7+'
    
    return bucket

def load_data():
    print("Loading frozen Step 5 datasets and match metadata...")
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
    
    # Unique cell id
    cell_id_func = lambda df: (
        df['innings'].astype(str) + '_' + 
        df['format'] + '_' + 
        df['phase'] + '_' + 
        df['wkt_bucket']
    )
    bat['cell_id'] = cell_id_func(bat)
    bowl['cell_id'] = cell_id_func(bowl)
    
    print(f"Loaded {len(bat)} batting rows ({bat['is_batter_ball_faced'].sum()} balls faced)")
    print(f"Loaded {len(bowl)} bowling rows ({bowl['is_legal_ball'].sum()} legal deliveries)")
    print(f"Unique matches: {bat['match_id'].nunique()} ({bat['format'].value_counts().to_dict()})")
    return bat, bowl, m_comp

def build_cohort_baselines(bat, bowl):
    print("\n--- Constructing Full-Cohort 36-Cell Baselines ---")
    
    # Filter to eligible domains
    bat_faced = bat[bat['is_batter_ball_faced'] == True].copy()
    bowl_legal = bowl[bowl['is_legal_ball'] == True].copy()
    
    # Grouping columns
    grp_cols = ['innings', 'format', 'phase', 'wkt_bucket', 'cell_id']
    
    # Batting baseline
    bat_agg = bat_faced.groupby(grp_cols, observed=False).agg(
        n_deliveries=('batter_runs', 'count'),
        exp_runs=('batter_runs', 'mean'),
        var_runs=('batter_runs', 'var'),
        exp_striker_dismissal=('is_striker_dismissed', 'mean'),
        var_striker_dismissal=('is_striker_dismissed', 'var'),
        boundary_rate=('is_boundary', 'mean'),
        dot_rate=('is_dot_ball_faced', 'mean')
    ).reset_index()
    
    bat_agg['se_runs'] = np.sqrt(bat_agg['var_runs'] / bat_agg['n_deliveries'])
    bat_agg['se_striker_dismissal'] = np.sqrt(bat_agg['var_striker_dismissal'] / bat_agg['n_deliveries'])
    
    # Bowling baseline
    bowl_agg = bowl_legal.groupby(grp_cols, observed=False).agg(
        n_deliveries=('bowler_runs_conceded', 'count'),
        exp_runs_conceded=('bowler_runs_conceded', 'mean'),
        var_runs_conceded=('bowler_runs_conceded', 'var'),
        exp_bowler_wicket=('is_bowler_wicket', 'mean'),
        var_bowler_wicket=('is_bowler_wicket', 'var'),
        boundary_conceded_rate=('is_boundary_conceded', 'mean'),
        dot_bowled_rate=('is_bowler_dot_ball', 'mean')
    ).reset_index()
    
    bowl_agg['se_runs_conceded'] = np.sqrt(bowl_agg['var_runs_conceded'] / bowl_agg['n_deliveries'])
    bowl_agg['se_bowler_wicket'] = np.sqrt(bowl_agg['var_bowler_wicket'] / bowl_agg['n_deliveries'])
    
    print(f"Batting baseline generated: {len(bat_agg)} cells. Min N = {bat_agg['n_deliveries'].min()}, Max N = {bat_agg['n_deliveries'].max()}")
    print(f"Bowling baseline generated: {len(bowl_agg)} cells. Min N = {bowl_agg['n_deliveries'].min()}, Max N = {bowl_agg['n_deliveries'].max()}")
    
    return bat_agg, bowl_agg

def run_match_held_out_validation(bat, bowl, m_comp):
    print("\n--- Running 5-Fold Stratified Match-Held-Out Cross-Validation ---")
    
    # Eligible data
    bat_faced = bat[bat['is_batter_ball_faced'] == True].copy()
    bowl_legal = bowl[bowl['is_legal_ball'] == True].copy()
    
    # Unique matches and their formats
    unique_matches = bat_faced[['match_id', 'format']].drop_duplicates().sort_values('match_id').reset_index(drop=True)
    
    # Pure numpy stratified 5-fold match assignment
    rng = np.random.RandomState(42)
    unique_matches['fold'] = -1
    for fmt in ['IPL', 'T20I']:
        fmt_indices = unique_matches[unique_matches['format'] == fmt].index.values.copy()
        rng.shuffle(fmt_indices)
        fold_splits = np.array_split(fmt_indices, 5)
        for fold_idx, split_idx in enumerate(fold_splits):
            unique_matches.loc[split_idx, 'fold'] = fold_idx + 1
        
    print("Match distribution across folds:")
    print(unique_matches.groupby(['fold', 'format']).size().unstack())
    
    bat_faced = bat_faced.merge(unique_matches[['match_id', 'fold']], on='match_id', how='left')
    bowl_legal = bowl_legal.merge(unique_matches[['match_id', 'fold']], on='match_id', how='left')
    
    cv_records = []
    cell_stability_records = []
    
    grp_cols = ['innings', 'format', 'phase', 'wkt_bucket', 'cell_id']
    
    for fold in range(1, 6):
        # Split
        bat_train = bat_faced[bat_faced['fold'] != fold]
        bat_test = bat_faced[bat_faced['fold'] == fold]
        
        bowl_train = bowl_legal[bowl_legal['fold'] != fold]
        bowl_test = bowl_legal[bowl_legal['fold'] == fold]
        
        # Fit baselines on training matches
        bat_base = bat_train.groupby(grp_cols, observed=False).agg(
            train_exp_runs=('batter_runs', 'mean'),
            train_exp_wkt=('is_striker_dismissed', 'mean')
        ).reset_index()
        
        bowl_base = bowl_train.groupby(grp_cols, observed=False).agg(
            train_exp_runs=('bowler_runs_conceded', 'mean'),
            train_exp_wkt=('is_bowler_wicket', 'mean')
        ).reset_index()
        
        # Track cell parameter stability
        for _, row in bat_base.iterrows():
            cell_stability_records.append({
                'discipline': 'batting',
                'fold': fold,
                'cell_id': row['cell_id'],
                'exp_runs': row['train_exp_runs'],
                'exp_wkt': row['train_exp_wkt']
            })
            
        for _, row in bowl_base.iterrows():
            cell_stability_records.append({
                'discipline': 'bowling',
                'fold': fold,
                'cell_id': row['cell_id'],
                'exp_runs': row['train_exp_runs'],
                'exp_wkt': row['train_exp_wkt']
            })
            
        # Predict on test matches
        bat_pred = bat_test.merge(bat_base, on=grp_cols, how='left')
        bowl_pred = bowl_test.merge(bowl_base, on=grp_cols, how='left')
        
        # Batting evaluation
        bat_runs_actual = bat_pred['batter_runs'].values
        bat_runs_pred = bat_pred['train_exp_runs'].values
        bat_wkt_actual = bat_pred['is_striker_dismissed'].astype(float).values
        bat_wkt_pred = bat_pred['train_exp_wkt'].values
        
        bat_run_rmse = compute_rmse(bat_runs_actual, bat_runs_pred)
        bat_run_mae = compute_mae(bat_runs_actual, bat_runs_pred)
        bat_run_bias = compute_bias(bat_runs_actual, bat_runs_pred)
        
        bat_wkt_brier = compute_brier(bat_wkt_actual, bat_wkt_pred)
        bat_wkt_logloss = compute_logloss(bat_wkt_actual, bat_wkt_pred)
        bat_wkt_bias = compute_bias(bat_wkt_actual, bat_wkt_pred)
        
        # Bowling evaluation
        bowl_runs_actual = bowl_pred['bowler_runs_conceded'].values
        bowl_runs_pred = bowl_pred['train_exp_runs'].values
        bowl_wkt_actual = bowl_pred['is_bowler_wicket'].astype(float).values
        bowl_wkt_pred = bowl_pred['train_exp_wkt'].values
        
        bowl_run_rmse = compute_rmse(bowl_runs_actual, bowl_runs_pred)
        bowl_run_mae = compute_mae(bowl_runs_actual, bowl_runs_pred)
        bowl_run_bias = compute_bias(bowl_runs_actual, bowl_runs_pred)
        
        bowl_wkt_brier = compute_brier(bowl_wkt_actual, bowl_wkt_pred)
        bowl_wkt_logloss = compute_logloss(bowl_wkt_actual, bowl_wkt_pred)
        bowl_wkt_bias = compute_bias(bowl_wkt_actual, bowl_wkt_pred)
        
        cv_records.append({
            'fold': fold,
            'test_matches': len(bat_test['match_id'].unique()),
            'bat_test_deliveries': len(bat_test),
            'bowl_test_deliveries': len(bowl_test),
            'bat_run_rmse': bat_run_rmse,
            'bat_run_mae': bat_run_mae,
            'bat_run_bias': bat_run_bias,
            'bat_wkt_brier': bat_wkt_brier,
            'bat_wkt_logloss': bat_wkt_logloss,
            'bat_wkt_bias': bat_wkt_bias,
            'bowl_run_rmse': bowl_run_rmse,
            'bowl_run_mae': bowl_run_mae,
            'bowl_run_bias': bowl_run_bias,
            'bowl_wkt_brier': bowl_wkt_brier,
            'bowl_wkt_logloss': bowl_wkt_logloss,
            'bowl_wkt_bias': bowl_wkt_bias
        })
        
        print(f"Fold {fold} Complete | Bat Run RMSE: {bat_run_rmse:.4f}, Bias: {bat_run_bias:+.5f} | Bowl Run RMSE: {bowl_run_rmse:.4f}, Bias: {bowl_run_bias:+.5f}")
        
    cv_df = pd.DataFrame(cv_records)
    stability_df = pd.DataFrame(cell_stability_records)
    return cv_df, stability_df

def compute_quality_diagnostics(bat_base, bowl_base, stability_df):
    print("\n--- Computing Baseline Quality & Parameter Stability Diagnostics ---")
    
    # 1. Format comparison (IPL vs T20I) across phases
    format_comp_bat = bat_base.groupby(['format', 'phase'])[['exp_runs', 'exp_striker_dismissal']].mean().unstack()
    format_comp_bowl = bowl_base.groupby(['format', 'phase'])[['exp_runs_conceded', 'exp_bowler_wicket']].mean().unstack()
    
    # 2. Phase & Wicket bucket progression
    bat_pvt_runs = bat_base.pivot_table(index=['innings', 'format', 'phase'], columns='wkt_bucket', values='exp_runs')
    bat_pvt_wkt = bat_base.pivot_table(index=['innings', 'format', 'phase'], columns='wkt_bucket', values='exp_striker_dismissal')
    
    # 3. Fold stability across cells
    # Calculate standard deviation and max range of cell expectations across the 5 folds
    stab_bat = stability_df[stability_df['discipline'] == 'batting'].groupby('cell_id').agg(
        mean_exp_runs=('exp_runs', 'mean'),
        std_exp_runs=('exp_runs', 'std'),
        max_run_dev=('exp_runs', lambda x: x.max() - x.min()),
        mean_exp_wkt=('exp_wkt', 'mean'),
        std_exp_wkt=('exp_wkt', 'std'),
        max_wkt_dev=('exp_wkt', lambda x: x.max() - x.min())
    ).reset_index()
    
    stab_bowl = stability_df[stability_df['discipline'] == 'bowling'].groupby('cell_id').agg(
        mean_exp_runs=('exp_runs', 'mean'),
        std_exp_runs=('exp_runs', 'std'),
        max_run_dev=('exp_runs', lambda x: x.max() - x.min()),
        mean_exp_wkt=('exp_wkt', 'mean'),
        std_exp_wkt=('exp_wkt', 'std'),
        max_wkt_dev=('exp_wkt', lambda x: x.max() - x.min())
    ).reset_index()
    
    print("Format comparison - Batting Expected Runs (RPO equivalent):")
    print((format_comp_bat['exp_runs'] * 6).round(2))
    
    print("\nFold Stability Summary - Batting Max Cell Shift across 5 folds:")
    print(f"Max Run Deviation across folds: {stab_bat['max_run_dev'].max():.4f} runs/ball (median = {stab_bat['max_run_dev'].median():.4f})")
    print(f"Max Wkt Deviation across folds: {stab_bat['max_wkt_dev'].max():.4f} outs/ball (median = {stab_bat['max_wkt_dev'].median():.4f})")
    
    print("\nFold Stability Summary - Bowling Max Cell Shift across 5 folds:")
    print(f"Max Run Deviation across folds: {stab_bowl['max_run_dev'].max():.4f} runs/ball (median = {stab_bowl['max_run_dev'].median():.4f})")
    print(f"Max Wkt Deviation across folds: {stab_bowl['max_wkt_dev'].max():.4f} wkts/ball (median = {stab_bowl['max_wkt_dev'].median():.4f})")
    
    return {
        'format_bat': format_comp_bat,
        'format_bowl': format_comp_bowl,
        'stab_bat': stab_bat,
        'stab_bowl': stab_bowl,
        'bat_pvt_runs': bat_pvt_runs,
        'bat_pvt_wkt': bat_pvt_wkt
    }

def main():
    out_dir = 'outputs/step_7_empirical_calibration'
    os.makedirs(out_dir, exist_ok=True)
    
    bat, bowl, m_comp = load_data()
    bat_base, bowl_base = build_cohort_baselines(bat, bowl)
    cv_df, stability_df = run_match_held_out_validation(bat, bowl, m_comp)
    diagnostics = compute_quality_diagnostics(bat_base, bowl_base, stability_df)
    
    # Save artifacts
    print("\nSaving baseline artifacts and diagnostic reports...")
    bat_base.to_parquet(os.path.join(out_dir, 'batting_baseline_36cells.parquet'), index=False)
    bat_base.to_csv(os.path.join(out_dir, 'batting_baseline_36cells.csv'), index=False)
    
    bowl_base.to_parquet(os.path.join(out_dir, 'bowling_baseline_36cells.parquet'), index=False)
    bowl_base.to_csv(os.path.join(out_dir, 'bowling_baseline_36cells.csv'), index=False)
    
    # Merge cell diagnostics with fold stability
    cell_diag_bat = bat_base.merge(diagnostics['stab_bat'], on='cell_id', how='left')
    cell_diag_bowl = bowl_base.merge(diagnostics['stab_bowl'], on='cell_id', how='left')
    
    cell_diag_bat.to_csv(os.path.join(out_dir, 'cell_diagnostics_batting.csv'), index=False)
    cell_diag_bowl.to_csv(os.path.join(out_dir, 'cell_diagnostics_bowling.csv'), index=False)
    cv_df.to_csv(os.path.join(out_dir, 'match_cv_validation_results.csv'), index=False)
    
    # Summary json
    summary = {
        'cohort_matches': bat['match_id'].nunique(),
        'ipl_matches': int(bat[bat['format'] == 'IPL']['match_id'].nunique()),
        't20i_matches': int(bat[bat['format'] == 'T20I']['match_id'].nunique()),
        'batting_balls_faced': int(bat['is_batter_ball_faced'].sum()),
        'bowling_legal_balls': int(bowl['is_legal_ball'].sum()),
        'total_cells': len(bat_base),
        'min_cell_samples_bat': int(bat_base['n_deliveries'].min()),
        'max_cell_samples_bat': int(bat_base['n_deliveries'].max()),
        'median_cell_samples_bat': float(bat_base['n_deliveries'].median()),
        'min_cell_samples_bowl': int(bowl_base['n_deliveries'].min()),
        'max_cell_samples_bowl': int(bowl_base['n_deliveries'].max()),
        'median_cell_samples_bowl': float(bowl_base['n_deliveries'].median()),
        'mean_cv_bat_run_rmse': float(cv_df['bat_run_rmse'].mean()),
        'mean_cv_bat_run_bias': float(cv_df['bat_run_bias'].mean()),
        'mean_cv_bat_wkt_brier': float(cv_df['bat_wkt_brier'].mean()),
        'mean_cv_bat_wkt_bias': float(cv_df['bat_wkt_bias'].mean()),
        'mean_cv_bowl_run_rmse': float(cv_df['bowl_run_rmse'].mean()),
        'mean_cv_bowl_run_bias': float(cv_df['bowl_run_bias'].mean()),
        'mean_cv_bowl_wkt_brier': float(cv_df['bowl_wkt_brier'].mean()),
        'mean_cv_bowl_wkt_bias': float(cv_df['bowl_wkt_bias'].mean())
    }
    with open(os.path.join(out_dir, 'baseline_quality_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"\nAll baseline artifacts successfully generated and saved to {out_dir}/")

if __name__ == '__main__':
    main()
