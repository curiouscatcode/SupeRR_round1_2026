"""
Investigation B — Phase-Relative Pressure Baselines Audit
=========================================================

This script investigates whether applying an absolute cutoff (PI > 60.0)
systematically disadvantages Powerplay batters and Death bowlers due to
cross-phase baseline distribution differences.

It evaluates the experimental alternative:
    High Pressure = Top 20% (80th percentile cutoff) within each match phase.

Outputs:
- outputs/pressure_index_audit/03_phase_relative_distributions.png
- outputs/pressure_index_audit/04_absolute_vs_relative_classification_matrix.png
- outputs/pressure_index_audit/phase_relative_player_sample_shifts.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/pressure_index_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_phase_relative_audit():
    print("Loading delivery_pressure_index.csv...")
    df = pd.read_csv(DATA_DIR / "delivery_pressure_index.csv")
    total_deliveries = len(df)
    print(f"Total deliveries loaded: {total_deliveries:,}")

    # 1. Compute Empirical Phase 80th Percentiles
    print("\nComputing Phase-Specific 80th Percentiles...")
    p80_bat = {}
    p80_bowl = {}
    phases = ['PP', 'Middle', 'Death']

    for ph in phases:
        sub = df[df['phase'] == ph]
        p80_bat[ph] = np.percentile(sub['Batting_PI'].dropna(), 80)
        p80_bowl[ph] = np.percentile(sub['Bowling_PI'].dropna(), 80)
        print(f"  Phase {ph:6s} | Batting PI 80th %ile: {p80_bat[ph]:.2f} (Mean: {sub['Batting_PI'].mean():.2f}) | "
              f"Bowling PI 80th %ile: {p80_bowl[ph]:.2f} (Mean: {sub['Bowling_PI'].mean():.2f})")

    # 2. Delivery Classifications
    # Baseline
    df['bat_hp_base'] = df['Batting_PI'] > 60.0
    df['bowl_hp_base'] = df['Bowling_PI'] > 60.0

    # Phase-Relative Top 20%
    df['bat_p80_thresh'] = df['phase'].map(p80_bat)
    df['bowl_p80_thresh'] = df['phase'].map(p80_bowl)

    df['bat_hp_rel'] = df['Batting_PI'] > df['bat_p80_thresh']
    df['bowl_hp_rel'] = df['Bowling_PI'] > df['bowl_p80_thresh']

    # 3. Delivery Classification Contingency Matrices
    print("\n" + "="*70)
    print("DELIVERY CLASSIFICATION CONTINGENCY MATRICES")
    print("="*70)

    print("\nBatting Deliveries (Absolute vs. Relative):")
    bat_ct = pd.crosstab(df['bat_hp_base'], df['bat_hp_rel'], 
                         rownames=['Baseline (PI > 60)'], colnames=['Phase-Relative (Top 20%)'])
    print(bat_ct)

    print("\nBowling Deliveries (Absolute vs. Relative):")
    bowl_ct = pd.crosstab(df['bowl_hp_base'], df['bowl_hp_rel'], 
                          rownames=['Baseline (PI > 60)'], colnames=['Phase-Relative (Top 20%)'])
    print(bowl_ct)

    # 4. Phase-wise breakdown
    print("\nPhase-wise High Pressure Delivery Counts:")
    for ph in phases:
        sub = df[df['phase'] == ph]
        n = len(sub)
        b_base = sub['bat_hp_base'].sum()
        b_rel = sub['bat_hp_rel'].sum()
        bo_base = sub['bowl_hp_base'].sum()
        bo_rel = sub['bowl_hp_rel'].sum()
        print(f"  Phase {ph:6s} | Total: {n:6,} | "
              f"Batting HP: {b_base:5,} ({b_base/n*100:4.1f}%) -> {b_rel:5,} ({b_rel/n*100:4.1f}%) | "
              f"Bowling HP: {bo_base:5,} ({bo_base/n*100:4.1f}%) -> {bo_rel:5,} ({bo_rel/n*100:4.1f}%)")

    # 5. Player-Level Sample Size Shifts
    print("\nAggregating Player-Level Sample Size Shifts...")
    
    # Batters (using balls faced)
    bf_df = df[df['is_batter_ball_faced'] == 1].copy()
    bat_shift = bf_df.groupby(['striker_id', 'striker_name']).agg(
        total_bf=('is_batter_ball_faced', 'count'),
        pp_bf=('phase', lambda s: (s == 'PP').sum()),
        mo_bf=('phase', lambda s: (s == 'Middle').sum()),
        do_bf=('phase', lambda s: (s == 'Death').sum()),
        base_hp_bf=('bat_hp_base', 'sum'),
        rel_hp_bf=('bat_hp_rel', 'sum')
    ).reset_index()

    bat_shift['delta_hp_bf'] = bat_shift['rel_hp_bf'] - bat_shift['base_hp_bf']
    bat_shift['pct_change'] = np.round((bat_shift['delta_hp_bf'] / np.maximum(bat_shift['base_hp_bf'], 1)) * 100.0, 1)
    bat_shift['pp_share'] = np.round(bat_shift['pp_bf'] / bat_shift['total_bf'] * 100.0, 1)
    bat_shift['do_share'] = np.round(bat_shift['do_bf'] / bat_shift['total_bf'] * 100.0, 1)

    # Primary role tag
    def tag_role_bat(row):
        if row['pp_share'] >= 45.0:
            return 'Opener / Top Order'
        elif row['do_share'] >= 35.0:
            return 'Finisher / Death'
        else:
            return 'Middle Order'
    bat_shift['role'] = bat_shift.apply(tag_role_bat, axis=1)

    # Bowlers (using legal balls)
    lb_df = df[df['is_legal_ball'] == 1].copy()
    bowl_shift = lb_df.groupby(['bowler_id', 'bowler_name']).agg(
        total_lb=('is_legal_ball', 'count'),
        pp_lb=('phase', lambda s: (s == 'PP').sum()),
        mo_lb=('phase', lambda s: (s == 'Middle').sum()),
        do_lb=('phase', lambda s: (s == 'Death').sum()),
        base_hp_lb=('bowl_hp_base', 'sum'),
        rel_hp_lb=('bowl_hp_rel', 'sum')
    ).reset_index()

    bowl_shift['delta_hp_lb'] = bowl_shift['rel_hp_lb'] - bowl_shift['base_hp_lb']
    bowl_shift['pct_change'] = np.round((bowl_shift['delta_hp_lb'] / np.maximum(bowl_shift['base_hp_lb'], 1)) * 100.0, 1)
    bowl_shift['pp_share'] = np.round(bowl_shift['pp_lb'] / bowl_shift['total_lb'] * 100.0, 1)
    bowl_shift['do_share'] = np.round(bowl_shift['do_lb'] / bowl_shift['total_lb'] * 100.0, 1)

    def tag_role_bowl(row):
        if row['pp_share'] >= 45.0:
            return 'Powerplay Specialist'
        elif row['do_share'] >= 30.0:
            return 'Death Specialist'
        else:
            return 'Middle-Overs Specialist'
    bowl_shift['role'] = bowl_shift.apply(tag_role_bowl, axis=1)

    # Tier 1 Qualification Thresholds (N >= 60)
    print("\n--- Tier 1 Qualification Impact (N >= 60 High Pressure Balls) ---")
    bat_qual_base = (bat_shift['base_hp_bf'] >= 60).sum()
    bat_qual_rel = (bat_shift['rel_hp_bf'] >= 60).sum()
    print(f"Batters qualifying for Tier 1: Baseline = {bat_qual_base} | Phase-Relative = {bat_qual_rel} (Net: {bat_qual_rel - bat_qual_base:+d})")

    bowl_qual_base = (bowl_shift['base_hp_lb'] >= 60).sum()
    bowl_qual_rel = (bowl_shift['rel_hp_lb'] >= 60).sum()
    print(f"Bowlers qualifying for Tier 1: Baseline = {bowl_qual_base} | Phase-Relative = {bowl_qual_rel} (Net: {bowl_qual_rel - bowl_qual_base:+d})")

    # Combine player shifts into a single export CSV
    bat_shift['player_type'] = 'Batter'
    bat_shift.rename(columns={'striker_id': 'player_id', 'striker_name': 'player_name', 
                              'total_bf': 'total_balls', 'base_hp_bf': 'base_hp_balls', 
                              'rel_hp_bf': 'rel_hp_balls', 'delta_hp_bf': 'delta_hp_balls'}, inplace=True)

    bowl_shift['player_type'] = 'Bowler'
    bowl_shift.rename(columns={'bowler_id': 'player_id', 'bowler_name': 'player_name', 
                               'total_lb': 'total_balls', 'base_hp_lb': 'base_hp_balls', 
                               'rel_hp_lb': 'rel_hp_balls', 'delta_hp_lb': 'delta_hp_balls'}, inplace=True)

    combined_shift = pd.concat([bat_shift, bowl_shift], ignore_index=True)
    combined_shift.to_csv(OUTPUT_DIR / "phase_relative_player_sample_shifts.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'phase_relative_player_sample_shifts.csv'}")

    # Print interesting examples
    print("\nTop 5 Batters with Largest HP Ball Gain (Openers):")
    print(bat_shift.sort_values(by='delta_hp_balls', ascending=False)[
        ['player_name', 'role', 'total_balls', 'pp_share', 'base_hp_balls', 'rel_hp_balls', 'delta_hp_balls', 'pct_change']
    ].head(5).to_string(index=False))

    print("\nTop 5 Batters with Largest HP Ball Loss (Death Specialists):")
    print(bat_shift.sort_values(by='delta_hp_balls', ascending=True)[
        ['player_name', 'role', 'total_balls', 'do_share', 'base_hp_balls', 'rel_hp_balls', 'delta_hp_balls', 'pct_change']
    ].head(5).to_string(index=False))

    print("\nTop 5 Bowlers with Largest HP Ball Gain (Death Bowlers):")
    print(bowl_shift.sort_values(by='delta_hp_balls', ascending=False)[
        ['player_name', 'role', 'total_balls', 'do_share', 'base_hp_balls', 'rel_hp_balls', 'delta_hp_balls', 'pct_change']
    ].head(5).to_string(index=False))

    # 6. Generate Figure 3: Distributions & Cutoffs
    print("\nGenerating Figure 3: Phase-Relative Distributions...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    colors = {'PP': '#2ecc71', 'Middle': '#f39c12', 'Death': '#e74c3c'}
    
    # Subplot A: Batting PI
    for ph in phases:
        sub = df[df['phase'] == ph]['Batting_PI'].dropna()
        sns.kdeplot(sub, ax=axes[0], color=colors[ph], lw=2.2, label=f"{ph} (80%ile: {p80_bat[ph]:.1f})")
        axes[0].axvline(p80_bat[ph], color=colors[ph], linestyle='--', lw=1.5)

    axes[0].axvline(60.0, color='black', linestyle='-', lw=2.0, label='Baseline Cutoff (60.0)')
    axes[0].set_title("A. Batting Pressure Index (PI) Distribution by Phase", fontsize=13, fontweight='bold', pad=10)
    axes[0].set_xlabel("Batting Pressure Index", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("Density", fontsize=11, fontweight='bold')
    axes[0].set_xlim(0, 100)
    axes[0].legend(loc='upper right', frameon=True, fontsize=9)

    # Subplot B: Bowling PI
    for ph in phases:
        sub = df[df['phase'] == ph]['Bowling_PI'].dropna()
        sns.kdeplot(sub, ax=axes[1], color=colors[ph], lw=2.2, label=f"{ph} (80%ile: {p80_bowl[ph]:.1f})")
        axes[1].axvline(p80_bowl[ph], color=colors[ph], linestyle='--', lw=1.5)

    axes[1].axvline(60.0, color='black', linestyle='-', lw=2.0, label='Baseline Cutoff (60.0)')
    axes[1].set_title("B. Bowling Pressure Index (PI) Distribution by Phase", fontsize=13, fontweight='bold', pad=10)
    axes[1].set_xlabel("Bowling Pressure Index", fontsize=11, fontweight='bold')
    axes[1].set_ylabel("Density", fontsize=11, fontweight='bold')
    axes[1].set_xlim(0, 100)
    axes[1].legend(loc='upper right', frameon=True, fontsize=9)

    plt.tight_layout()
    fig_path3 = OUTPUT_DIR / "03_phase_relative_distributions.png"
    plt.savefig(fig_path3, dpi=300)
    plt.close()
    print(f"Saved: {fig_path3}")

    # 7. Generate Figure 4: Contingency Heatmaps
    print("\nGenerating Figure 4: Classification Contingency Matrices...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Batting Contingency
    bat_ct_pct = bat_ct / bat_ct.values.sum() * 100.0
    sns.heatmap(bat_ct, annot=True, fmt=',d', cmap='Blues', cbar=False, ax=axes[0], annot_kws={'size': 12, 'weight': 'bold'})
    axes[0].set_title("A. Batting Deliveries: Absolute vs. Relative Classification", fontsize=12, fontweight='bold', pad=10)
    axes[0].set_xlabel("Phase-Relative Top 20% (False = Low, True = High)", fontsize=10, fontweight='bold')
    axes[0].set_ylabel("Baseline Cutoff > 60.0 (False = Low, True = High)", fontsize=10, fontweight='bold')

    # Bowling Contingency
    bowl_ct_pct = bowl_ct / bowl_ct.values.sum() * 100.0
    sns.heatmap(bowl_ct, annot=True, fmt=',d', cmap='Oranges', cbar=False, ax=axes[1], annot_kws={'size': 12, 'weight': 'bold'})
    axes[1].set_title("B. Bowling Deliveries: Absolute vs. Relative Classification", fontsize=12, fontweight='bold', pad=10)
    axes[1].set_xlabel("Phase-Relative Top 20% (False = Low, True = High)", fontsize=10, fontweight='bold')
    axes[1].set_ylabel("Baseline Cutoff > 60.0 (False = Low, True = High)", fontsize=10, fontweight='bold')

    plt.tight_layout()
    fig_path4 = OUTPUT_DIR / "04_absolute_vs_relative_classification_matrix.png"
    plt.savefig(fig_path4, dpi=300)
    plt.close()
    print(f"Saved: {fig_path4}")

    return combined_shift


if __name__ == "__main__":
    run_phase_relative_audit()
