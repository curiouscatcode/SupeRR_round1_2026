
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

# Folds
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

print('=== 1. WICKET PROBABILITY BENCHMARK COMPARISONS ===')

def evaluate_models(df, target_col, name):
    results = []
    for fold in range(1, 6):
        train = df[df['fold'] != fold]
        test = df[df['fold'] == fold].copy()
        
        # Model 1: Global Mean
        p_global = train[target_col].mean()
        test['pred_m1'] = p_global
        
        # Model 2: Innings x Format (4 cells)
        m2_base = train.groupby(['innings', 'format'])[target_col].mean().reset_index(name='pred_m2')
        test = test.merge(m2_base, on=['innings', 'format'], how='left')
        
        # Model 3: 36 Cells
        m3_base = train.groupby(['innings', 'format', 'phase', 'wkt_bucket'])[target_col].mean().reset_index(name='pred_m3')
        test = test.merge(m3_base, on=['innings', 'format', 'phase', 'wkt_bucket'], how='left')
        
        y_true = test[target_col].astype(float).values
        
        for m_name, pred_col in [('Global Mean (1 cell)', 'pred_m1'), ('Innings x Format (4 cells)', 'pred_m2'), ('36-Cell Baseline', 'pred_m3')]:
            y_pred = test[pred_col].values
            brier = compute_brier(y_true, y_pred)
            logloss = compute_logloss(y_true, y_pred)
            bias = compute_bias(y_true, y_pred)
            results.append({
                'discipline': name,
                'fold': fold,
                'model': m_name,
                'brier': brier,
                'logloss': logloss,
                'bias': bias,
                'prevalence': float(np.mean(y_true))
            })
    return pd.DataFrame(results)

bat_bench = evaluate_models(bat_faced, 'is_striker_dismissed', 'Batting Dismissal')
bowl_bench = evaluate_models(bowl_legal, 'is_bowler_wicket', 'Bowling Wicket')

all_bench = pd.concat([bat_bench, bowl_bench])
bench_summary = all_bench.groupby(['discipline', 'model'])[['brier', 'logloss', 'bias', 'prevalence']].mean().reset_index()
print(bench_summary.to_string(index=False))

with open('scratch/bench_summary.txt', 'w') as f:
    f.write(bench_summary.to_string(index=False))
