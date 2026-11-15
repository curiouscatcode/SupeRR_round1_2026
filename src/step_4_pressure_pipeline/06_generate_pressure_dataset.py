"""
Step 4 - Module 6: Combined Pressure Dataset Generator
======================================================
Combines Task Difficulty and Normalized Consequence into final pressure scores:
  P_batting  = sqrt(task_difficulty_bat  * normalized_consequence_L)
  P_bowling  = sqrt(task_difficulty_bowl * normalized_consequence_L)

Exports final delivery-level dataset to Parquet and CSV in outputs/step_4_pressure_pipeline/
"""

import os
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_4_pressure_pipeline"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pressure_dataset():
    input_parquet = os.path.join(OUTPUT_DIR, "deliveries_with_task_difficulty.parquet")
    print(f"Loading deliveries with task difficulty from {input_parquet}...")
    df = pd.read_parquet(input_parquet)
    
    # Combined Geometric Mean Pressure
    t_bat = df['task_difficulty_bat'].values
    t_bowl = df['task_difficulty_bowl'].values
    l_norm = df['normalized_consequence_L'].values
    
    p_bat = np.sqrt(np.maximum(0.0, t_bat * l_norm))
    p_bowl = np.sqrt(np.maximum(0.0, t_bowl * l_norm))
    
    # Clip strictly to [0.0, 100.0]
    df['pressure_batting'] = np.clip(p_bat, 0.0, 100.0)
    df['pressure_bowling'] = np.clip(p_bowl, 0.0, 100.0)
    
    print("\n--- Combined Pressure Summary ---")
    print("Batting Pressure (P_bat):")
    print("  Overall: Mean={:.2f}, Median={:.2f}, Std={:.2f}, Min={:.2f}, Max={:.2f}".format(
        df['pressure_batting'].mean(), df['pressure_batting'].median(),
        df['pressure_batting'].std(), df['pressure_batting'].min(), df['pressure_batting'].max()
    ))
    for inn in [1, 2]:
        sub = df[df['innings'] == inn]
        print("  Inn {}:   Mean={:.2f}, Median={:.2f}, Min={:.2f}, Max={:.2f}".format(
            inn, sub['pressure_batting'].mean(), sub['pressure_batting'].median(),
            sub['pressure_batting'].min(), sub['pressure_batting'].max()
        ))
        
    print("\nBowling Pressure (P_bowl):")
    print("  Overall: Mean={:.2f}, Median={:.2f}, Std={:.2f}, Min={:.2f}, Max={:.2f}".format(
        df['pressure_bowling'].mean(), df['pressure_bowling'].median(),
        df['pressure_bowling'].std(), df['pressure_bowling'].min(), df['pressure_bowling'].max()
    ))
    for inn in [1, 2]:
        sub = df[df['innings'] == inn]
        print("  Inn {}:   Mean={:.2f}, Median={:.2f}, Min={:.2f}, Max={:.2f}".format(
            inn, sub['pressure_bowling'].mean(), sub['pressure_bowling'].median(),
            sub['pressure_bowling'].min(), sub['pressure_bowling'].max()
        ))
        
    print("\nPressure by Phase (Batting / Bowling):")
    for ph in ['PP', 'Middle', 'Death']:
        sub = df[df['phase'] == ph]
        print("  Phase {:6s} (N={:5d}): P_bat Mean={:.2f} (Med={:.2f}) | P_bowl Mean={:.2f} (Med={:.2f})".format(
            ph, len(sub), sub['pressure_batting'].mean(), sub['pressure_batting'].median(),
            sub['pressure_bowling'].mean(), sub['pressure_bowling'].median()
        ))
        
    # Select clean output columns
    out_cols = [
        'match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num',
        'batting_team_id', 'bowling_team_id',
        'striker_id', 'striker_name', 'non_striker_id', 'non_striker_name',
        'bowler_id', 'bowler_name',
        'phase', 'score_before', 'wickets_before', 'W_t', 'W_rem',
        'legal_balls_before', 'balls_remaining',
        'current_run_rate', 'runs_required', 'required_run_rate',
        'pre_delivery_wp',
        'task_difficulty_bat', 'task_difficulty_bowl',
        'raw_consequence_L', 'normalized_consequence_L',
        'pressure_batting', 'pressure_bowling',
        'runs', 'is_wicket', 'is_four', 'is_six', 'extras_type', 'is_legal_ball'
    ]
    
    clean_output_df = df[out_cols].copy()
    
    # Export to Parquet (v3: Step 4.3 with M=18 Bayesian CRR shrinkage)
    out_parquet = os.path.join(OUTPUT_DIR, "delivery_pressure_v3.parquet")
    clean_output_df.to_parquet(out_parquet, index=False)
    print(f"\nSaved final delivery pressure dataset to {out_parquet}")
    
    # Export to CSV
    out_csv = os.path.join(OUTPUT_DIR, "delivery_pressure_v3.csv")
    print(f"Exporting to CSV ({out_csv})...")
    clean_output_df.to_csv(out_csv, index=False)
    print("CSV export complete.")
    
    # Also archive to Step 4.3 output directory
    archive_dir = "outputs/step_4_3_controlled_implementation"
    os.makedirs(archive_dir, exist_ok=True)
    archive_parquet = os.path.join(archive_dir, "delivery_pressure_v3.parquet")
    clean_output_df.to_parquet(archive_parquet, index=False)
    print(f"Archived dataset to {archive_parquet}")
    
    return clean_output_df

if __name__ == '__main__':
    generate_pressure_dataset()
