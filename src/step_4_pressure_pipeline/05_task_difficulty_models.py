"""
Step 4 - Module 5: Task Difficulty Engine (T_B1, T_B2, T_BO1, T_BO2)
===================================================================
Implements the exact Step 3.2 equations for:
1. Batting Innings 1 (T_B1): Required Acceleration Rate vs Par, Empirical Wicket Stress
2. Batting Innings 2 (T_B2): Standardized RRR, Wicket Scarcity, Centered Interaction
3. Bowling Innings 1 (T_BO1): Conceded CRR vs Par, Opponent Wickets in Hand, Fielding Factor
4. Bowling Innings 2 (T_BO2): Opponent Chase Comfort (inverted RRR), Opponent Wickets in Hand
"""

import os
import json
import pandas as pd
import numpy as np

OUTPUT_DIR = "outputs/step_4_pressure_pipeline"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compute_task_difficulty():
    deliveries_path = os.path.join(OUTPUT_DIR, "deliveries_with_consequence.parquet")
    print(f"Loading deliveries from {deliveries_path}...")
    df = pd.read_parquet(deliveries_path)
    
    # Load empirical tables
    with open(os.path.join(OUTPUT_DIR, "empirical_venue_par.json"), 'r', encoding='utf-8') as f:
        venue_par_dict = json.load(f)
    global_par = venue_par_dict.get('GLOBAL_DEFAULT', 176.68)
    
    w_stats_df = pd.read_csv(os.path.join(OUTPUT_DIR, "empirical_wicket_curve.csv"))
    mu_w_dict = dict(zip(w_stats_df['legal_balls_before'], w_stats_df['mean']))
    sig_w_dict = dict(zip(w_stats_df['legal_balls_before'], w_stats_df['regularized_std']))
    
    # Vectorized lookups for mu_w and sigma_w
    lballs = df['legal_balls_before'].values
    mu_w_vec = np.array([mu_w_dict.get(b, 3.5) for b in lballs], dtype=float)
    sig_w_vec = np.array([sig_w_dict.get(b, 1.5) for b in lballs], dtype=float)
    
    # Venue par vector
    vpar_vec = df['venue_id'].astype(str).map(venue_par_dict).fillna(global_par).values
    rpar_vec = vpar_vec / 20.0
    
    inn1_mask = (df['innings'] == 1).values
    inn2_mask = (df['innings'] == 2).values
    
    t_bat = np.zeros(len(df), dtype=float)
    t_bowl = np.zeros(len(df), dtype=float)
    
    # -------------------------------------------------------------
    # 1. Batting Innings 1 (T_B1)
    # -------------------------------------------------------------
    score1 = df.loc[inn1_mask, 'score_before'].values
    lballs1 = df.loc[inn1_mask, 'legal_balls_before'].values
    wt1 = df.loc[inn1_mask, 'W_t'].values
    vpar1 = vpar_vec[inn1_mask]
    rpar1 = rpar_vec[inn1_mask]
    brem1 = np.maximum(1.0, 120.0 - lballs1)
    
    # RAR clipped >= 0
    rar1 = np.maximum(0.0, (vpar1 - score1) / (brem1 / 6.0))
    rate_stress1 = (rar1 - rpar1) / rpar1
    
    # Wicket stress with ball 0.1 neutral fix
    mu1 = mu_w_vec[inn1_mask]
    sig1 = sig_w_vec[inn1_mask]
    w_stress1 = np.where(lballs1 == 0, 0.0, (wt1 - mu1) / sig1)
    
    z_b1 = 0.60 * rate_stress1 + 0.40 * w_stress1
    t_b1 = 100.0 / (1.0 + np.exp(-1.2 * np.clip(z_b1, -20.0, 20.0)))
    t_bat[inn1_mask] = t_b1
    
    # -------------------------------------------------------------
    # 2. Batting Innings 2 (T_B2)
    # -------------------------------------------------------------
    req2 = df.loc[inn2_mask, 'runs_required'].values
    brem2 = np.maximum(1.0, df.loc[inn2_mask, 'balls_remaining'].values)
    wt2 = df.loc[inn2_mask, 'W_t'].values
    rrr2 = np.clip((req2 / brem2) * 6.0, 0.0, 36.0)
    
    z_rrr2 = (rrr2 - 8.10) / 3.00
    z_w2 = (wt2 - 3.50) / 2.00
    # Centered interaction term
    z_inter2 = (rrr2 * wt2 - 28.0) / 25.0
    
    z_b2 = 0.55 * z_rrr2 + 0.25 * z_w2 + 0.20 * z_inter2
    t_b2 = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_b2, -20.0, 20.0)))
    t_bat[inn2_mask] = t_b2
    
    # -------------------------------------------------------------
    # 3. Bowling Innings 1 (T_BO1)
    # -------------------------------------------------------------
    crr1 = np.where(lballs1 == 0, rpar1, (score1 / np.maximum(1.0, lballs1)) * 6.0)
    crr_stress1 = (crr1 - rpar1) / rpar1
    
    # Opponent wickets in hand: (10 - W_t) vs (10 - mu_w) = mu_w - W_t
    w_opp_stress1 = np.where(lballs1 == 0, 0.0, (mu1 - wt1) / sig1)
    
    # Field restriction factor: PP and Death = +0.50, Middle = 0.00
    phase1 = df.loc[inn1_mask, 'phase'].values
    field_factor1 = np.where(np.isin(phase1, ['PP', 'Death']), 0.50, 0.00)
    
    z_bo1 = 0.50 * crr_stress1 + 0.35 * w_opp_stress1 + 0.15 * field_factor1
    t_bo1 = 100.0 / (1.0 + np.exp(-1.1 * np.clip(z_bo1, -20.0, 20.0)))
    t_bowl[inn1_mask] = t_bo1
    
    # -------------------------------------------------------------
    # 4. Bowling Innings 2 (T_BO2)
    # -------------------------------------------------------------
    rrr_stress2 = (8.10 - rrr2) / 3.00
    mu2 = mu_w_vec[inn2_mask]
    sig2 = sig_w_vec[inn2_mask]
    w_opp_stress2 = (mu2 - wt2) / sig2
    
    z_bo2 = 0.60 * rrr_stress2 + 0.40 * w_opp_stress2
    t_bo2 = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_bo2, -20.0, 20.0)))
    t_bowl[inn2_mask] = t_bo2
    
    df['task_difficulty_bat'] = t_bat
    df['task_difficulty_bowl'] = t_bowl
    
    print("\n--- Task Difficulty Summary ---")
    print("Batting Task Difficulty:")
    print("  Inn 1 T_B1:  mean={:.2f}, median={:.2f}, min={:.2f}, max={:.2f}".format(
        df.loc[inn1_mask, 'task_difficulty_bat'].mean(),
        df.loc[inn1_mask, 'task_difficulty_bat'].median(),
        df.loc[inn1_mask, 'task_difficulty_bat'].min(),
        df.loc[inn1_mask, 'task_difficulty_bat'].max()
    ))
    print("  Inn 2 T_B2:  mean={:.2f}, median={:.2f}, min={:.2f}, max={:.2f}".format(
        df.loc[inn2_mask, 'task_difficulty_bat'].mean(),
        df.loc[inn2_mask, 'task_difficulty_bat'].median(),
        df.loc[inn2_mask, 'task_difficulty_bat'].min(),
        df.loc[inn2_mask, 'task_difficulty_bat'].max()
    ))
    print("\nBowling Task Difficulty:")
    print("  Inn 1 T_BO1: mean={:.2f}, median={:.2f}, min={:.2f}, max={:.2f}".format(
        df.loc[inn1_mask, 'task_difficulty_bowl'].mean(),
        df.loc[inn1_mask, 'task_difficulty_bowl'].median(),
        df.loc[inn1_mask, 'task_difficulty_bowl'].min(),
        df.loc[inn1_mask, 'task_difficulty_bowl'].max()
    ))
    print("  Inn 2 T_BO2: mean={:.2f}, median={:.2f}, min={:.2f}, max={:.2f}".format(
        df.loc[inn2_mask, 'task_difficulty_bowl'].mean(),
        df.loc[inn2_mask, 'task_difficulty_bowl'].median(),
        df.loc[inn2_mask, 'task_difficulty_bowl'].min(),
        df.loc[inn2_mask, 'task_difficulty_bowl'].max()
    ))
    
    out_parquet = os.path.join(OUTPUT_DIR, "deliveries_with_task_difficulty.parquet")
    df.to_parquet(out_parquet, index=False)
    print(f"\nSaved deliveries with task difficulty to {out_parquet}")
    return df

if __name__ == '__main__':
    compute_task_difficulty()
