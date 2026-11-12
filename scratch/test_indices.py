import pandas as pd
import numpy as np

batter_df = pd.read_csv('data/processed/batter_performance.csv')
bowler_df = pd.read_csv('data/processed/bowler_performance.csv')

# Qualified sets (N >= 60)
b = batter_df[batter_df['high_balls_faced'] >= 60].copy()
bo = bowler_df[bowler_df['high_legal_balls'] >= 60].copy()

# Priors
K = 50.0

# BATTER PRIORS
mu_bat_sr = (batter_df['high_runs'].sum() / batter_df['high_balls_faced'].sum()) * 100.0
mu_bat_out = (batter_df['high_dismissals'].sum() / batter_df['high_balls_faced'].sum()) * 100.0
mu_bat_bnd = (batter_df['high_boundaries'].sum() / batter_df['high_balls_faced'].sum()) * 100.0
mu_bat_dot = (batter_df['high_dot_balls'].sum() / batter_df['high_balls_faced'].sum()) * 100.0
mu_bat_sr_low = (batter_df['low_mod_runs'].sum() / batter_df['low_mod_balls_faced'].sum()) * 100.0

# Batter shrinkage
lam_b = b['high_balls_faced'] / (b['high_balls_faced'] + K)
lam_b_low = b['low_mod_balls_faced'] / (b['low_mod_balls_faced'] + K)

b['sr_star'] = lam_b * b['high_strike_rate'] + (1 - lam_b) * mu_bat_sr
b['out_star'] = lam_b * b['high_dismissal_pct'] + (1 - lam_b) * mu_bat_out
b['surv_star'] = 100.0 - b['out_star']
b['bnd_star'] = lam_b * b['high_boundary_pct'] + (1 - lam_b) * mu_bat_bnd
b['dot_star'] = lam_b * b['high_dot_pct'] + (1 - lam_b) * mu_bat_dot
b['exec_star'] = b['bnd_star'] - 0.5 * b['dot_star']

b['sr_low_star'] = lam_b_low * b['low_mod_strike_rate'] + (1 - lam_b_low) * mu_bat_sr_low
b['diff_sr_star'] = b['sr_star'] - b['sr_low_star']

# Standardize components to [0, 100] using min-max on 5th and 95th percentiles (winsorized min-max)
def scale_component(series, higher_is_better=True):
    p5 = series.quantile(0.02)
    p95 = series.quantile(0.98)
    if higher_is_better:
        scaled = (series - p5) / (p95 - p5) * 100.0
    else:
        scaled = (p95 - series) / (p95 - p5) * 100.0
    return np.clip(scaled, 0.0, 100.0)

b['score_sr'] = scale_component(b['sr_star'], higher_is_better=True)
b['score_surv'] = scale_component(b['surv_star'], higher_is_better=True)
b['score_exec'] = scale_component(b['exec_star'], higher_is_better=True)
b['score_diff'] = scale_component(b['diff_sr_star'], higher_is_better=True)

b['brs'] = (0.40 * b['score_sr'] + 
            0.25 * b['score_surv'] + 
            0.20 * b['score_exec'] + 
            0.15 * b['score_diff'])

print("=== TOP 15 BATTERS BY BRS (TEST RUN) ===")
print(b[['player_name', 'high_balls_faced', 'high_strike_rate', 'sr_star', 'surv_star', 'diff_sr_star', 'brs']].sort_values('brs', ascending=False).head(15).to_string(index=False))

# BOWLER CALCULATIONS
mu_bo_econ = (bowler_df['high_runs_conceded'].sum() / bowler_df['high_legal_balls'].sum()) * 6.0
mu_bo_wk = (bowler_df['high_wickets'].sum() / bowler_df['high_legal_balls'].sum()) * 100.0
mu_bo_dot = (bowler_df['high_dot_balls'].sum() / bowler_df['high_legal_balls'].sum()) * 100.0
mu_bo_econ_low = (bowler_df['low_mod_runs_conceded'].sum() / bowler_df['low_mod_legal_balls'].sum()) * 6.0

lam_bo = bo['high_legal_balls'] / (bo['high_legal_balls'] + K)
lam_bo_low = bo['low_mod_legal_balls'] / (bo['low_mod_legal_balls'] + K)

bo['econ_star'] = lam_bo * bo['high_economy_rate'] + (1 - lam_bo) * mu_bo_econ
bo['wk_obs'] = (bo['high_wickets'] / bo['high_legal_balls']) * 100.0
bo['wk_star'] = lam_bo * bo['wk_obs'] + (1 - lam_bo) * mu_bo_wk
bo['dot_star'] = lam_bo * bo['high_dot_pct'] + (1 - lam_bo) * mu_bo_dot

bo['econ_low_star'] = lam_bo_low * bo['low_mod_economy_rate'] + (1 - lam_bo_low) * mu_bo_econ_low
bo['diff_econ_star'] = bo['econ_low_star'] - bo['econ_star'] # positive if more economical under pressure

bo['score_econ'] = scale_component(bo['econ_star'], higher_is_better=False)
bo['score_wk'] = scale_component(bo['wk_star'], higher_is_better=True)
bo['score_dot'] = scale_component(bo['dot_star'], higher_is_better=True)
bo['score_diff'] = scale_component(bo['diff_econ_star'], higher_is_better=True)

bo['bors'] = (0.40 * bo['score_econ'] + 
              0.25 * bo['score_wk'] + 
              0.20 * bo['score_dot'] + 
              0.15 * bo['score_diff'])

print("\n=== TOP 15 BOWLERS BY BORS (TEST RUN) ===")
print(bo[['player_name', 'high_legal_balls', 'high_economy_rate', 'econ_star', 'wk_star', 'diff_econ_star', 'bors']].sort_values('bors', ascending=False).head(15).to_string(index=False))
