import sys
sys.path.append('.')
import json
import math
import numpy as np
import pandas as pd

# Load empirical tables
with open('outputs/step_4_pressure_pipeline/empirical_venue_par.json') as f:
    vpar_dict = json.load(f)
global_par = vpar_dict.get('GLOBAL_DEFAULT', 176.68)

with open('outputs/step_4_pressure_pipeline/outcome_transition_probabilities.json') as f:
    t_dict = json.load(f)

# Load clean deliveries
df = pd.read_parquet('outputs/step_4_pressure_pipeline/deliveries_with_task_difficulty.parquet')
final_df = pd.read_parquet('outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet')
df['pressure_batting'] = final_df['pressure_batting']
df['pressure_bowling'] = final_df['pressure_bowling']

# -------------------------------------------------------------------------
# Table 1: Early-Rate Shrinkage Parameter Sweep (M = 0, 6, 12, 18, 24, 36)
# -------------------------------------------------------------------------
from scratch.test_early_rate_regularization import eval_ball_01_consequence

sweep_results = []
for M_val in [0, 6, 12, 18, 24, 36]:
    init_p = (M_val > 0)
    wp0, exp_L, swings = eval_ball_01_consequence(shrinkage_M=M_val, init_crr_par=init_p)
    sweep_results.append({
        'Prior_Strength_M': M_val,
        'Overs_Equivalent': M_val / 6.0,
        'WP_Pre_Delivery': wp0,
        'Raw_L_Ball_01': exp_L,
        'Swing_Dot': swings['Dot (0)'][1],
        'Swing_Single': swings['Single (1)'][1],
        'Swing_Four': swings['Four (4)'][1],
        'Swing_Six': swings['Six (6)'][1],
        'Swing_Wicket': swings['Wicket'][1]
    })

sweep_df = pd.DataFrame(sweep_results)
sweep_df.to_csv('scratch/early_rate_shrinkage_sweep.csv', index=False)
print("Saved early_rate_shrinkage_sweep.csv")

# -------------------------------------------------------------------------
# Table 2: Phase Distribution Comparison Across Alternatives
# -------------------------------------------------------------------------
import importlib
mod_fast = importlib.import_module('scratch.test_combined_reconciliations_fast')
inn1_df = mod_fast.inn1_df

phase_dist_results = []
for ph in ['PP', 'Middle', 'Death']:
    sub = inn1_df[inn1_df['phase'] == ph]
    n = len(sub)
    t_mean = sub['task_difficulty_bat'].mean()
    t_med = sub['task_difficulty_bat'].median()
    
    # Alt 1: Baseline Whole ECDF (M=0)
    p_base = sub['pressure_batting']
    l_base = sub['normalized_consequence_L']
    
    # Alt 2: Shrunk Whole ECDF (M=18)
    p_shrunk_w = np.sqrt(sub['task_difficulty_bat'] * sub['L_norm_shrunk_whole'])
    l_shrunk_w = sub['L_norm_shrunk_whole']
    
    # Alt 3: Strict Phase ECDF (M=18)
    p_phase = np.sqrt(sub['task_difficulty_bat'] * sub['L_norm_shrunk_phase'])
    l_phase = sub['L_norm_shrunk_phase']
    
    # Alt 4: Smoothed Phase ECDF (M=18)
    p_smooth = np.sqrt(sub['task_difficulty_bat'] * sub['L_norm_shrunk_smooth'])
    l_smooth = sub['L_norm_shrunk_smooth']
    
    phase_dist_results.append({
        'Phase': ph, 'N': n,
        'T_bat_Mean': t_mean, 'T_bat_Med': t_med,
        'Base_Lnorm_Mean': l_base.mean(), 'Base_Lnorm_Med': l_base.median(),
        'Base_Pbat_Mean': p_base.mean(), 'Base_Pbat_Med': p_base.median(),
        'ShrunkWhole_Lnorm_Mean': l_shrunk_w.mean(), 'ShrunkWhole_Lnorm_Med': l_shrunk_w.median(),
        'ShrunkWhole_Pbat_Mean': p_shrunk_w.mean(), 'ShrunkWhole_Pbat_Med': p_shrunk_w.median(),
        'PhaseECDF_Lnorm_Mean': l_phase.mean(), 'PhaseECDF_Lnorm_Med': l_phase.median(),
        'PhaseECDF_Pbat_Mean': p_phase.mean(), 'PhaseECDF_Pbat_Med': p_phase.median(),
        'SmoothECDF_Lnorm_Mean': l_smooth.mean(), 'SmoothECDF_Lnorm_Med': l_smooth.median(),
        'SmoothECDF_Pbat_Mean': p_smooth.mean(), 'SmoothECDF_Pbat_Med': p_smooth.median()
    })

pdist_df = pd.DataFrame(phase_dist_results)
pdist_df.to_csv('scratch/phase_distribution_comparison.csv', index=False)
print("Saved phase_distribution_comparison.csv")

# -------------------------------------------------------------------------
# Table 3: Scenario Comparison Table
# -------------------------------------------------------------------------
scen_df = pd.read_csv('scratch/scenario_comparison_matrix.csv')
scen_df.to_csv('scratch/scenario_comparison_table.csv', index=False)
print("Saved scenario_comparison_table.csv")
print("All Step 4.2 evidence tables successfully generated.")
