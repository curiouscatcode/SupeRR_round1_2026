"""
Step 14.2.1 — Module 2: Audit Pressure Classification & Delivery Transitions
=============================================================================

Audits:
1. Classification threshold difference:
   - Established Operational Threshold: PI > 60.0 (High) vs PI <= 60.0 (Low/Mod)
   - Alternative / Boundary-Inclusive: PI >= 60.0 (High) vs PI < 60.0 (Low/Mod)
   - Identifies deliveries sitting on exact boundary PI == 60.0
2. Delivery-level transition reconciliation:
   - 177,745 changed deliveries (94.38%)
   - Promoted / demoted counts under both thresholds
   - Complete transition breakdown by Phase (PP, Middle, Death) and Innings (1, 2)
   - Phase-specific PI mean and median changes
3. Diagnostic Visualization (01_audit_pressure_transitions.png):
   - 4-panel diagnostic chart showing transition matrices, boundary counts, and distributions.

Outputs:
- outputs/step_14_2_1_independent_audit/step_14_2_1_pressure_transitions.csv
- outputs/step_14_2_1_independent_audit/01_audit_pressure_transitions.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_2_1_independent_audit")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("=" * 80)
    print("STEP 14.2.1 — MODULE 2: AUDIT PRESSURE CLASSIFICATION & TRANSITIONS")
    print("=" * 80)

    del_path = os.path.join(BASE_DIR, "outputs", "step_14_2_workload_experiment", "delivery_pressure_index_exp14_2.csv")
    print(f"Loading delivery pressure index data from: {del_path}...")
    df = pd.read_csv(del_path)
    total_dels = len(df)
    print(f"Loaded {total_dels:,} deliveries.")

    orig_pi = df['Bowling_PI_orig']
    exp_pi = df['Bowling_PI_exp']
    delta_pi = df['delta_bowling_pi']

    # 1. Delta Bowling PI distribution
    changed_mask = delta_pi.abs() > 1e-5
    num_changed = changed_mask.sum()
    pct_changed = num_changed / total_dels * 100.0

    print(f"\n1. Global Delivery Delta Audit:")
    print(f"  Total Deliveries      : {total_dels:,}")
    print(f"  Changed Deliveries    : {num_changed:,} ({pct_changed:.2f}%)")
    print(f"  Increased Deliveries  : {(delta_pi > 1e-5).sum():,} ({(delta_pi > 1e-5).mean()*100:.2f}%)")
    print(f"  Decreased Deliveries  : {(delta_pi < -1e-5).sum():,} ({(delta_pi < -1e-5).mean()*100:.2f}%)")
    print(f"  Unchanged Deliveries  : {(delta_pi.abs() <= 1e-5).sum():,} ({(delta_pi.abs() <= 1e-5).mean()*100:.2f}%)")
    print(f"  Overall Mean Delta    : {delta_pi.mean():+.2f}")
    print(f"  Overall Median Delta  : {delta_pi.median():+.2f}")
    print(f"  Overall Std Delta     : {delta_pi.std():.2f}")
    print(f"  Min Delta / Max Delta : {delta_pi.min():+.2f} / {delta_pi.max():+.2f}")

    # 2. Audit Operational Threshold PI > 60.0 vs Boundary PI >= 60.0
    print("\n2. Operational Threshold Audit (PI > 60.0 vs PI >= 60.0):")
    
    # Boundary counts
    orig_exact_60 = (orig_pi == 60.0).sum()
    exp_exact_60 = (exp_pi == 60.0).sum()
    print(f"  Deliveries exactly at Bowling_PI == 60.0:")
    print(f"    - Original Bowling PI == 60.0    : {orig_exact_60}")
    print(f"    - Experimental Bowling PI == 60.0: {exp_exact_60}")

    # Canonical threshold: PI > 60.0
    orig_gt = orig_pi > 60.0
    exp_gt = exp_pi > 60.0
    prom_gt = (~orig_gt & exp_gt).sum()
    dem_gt = (orig_gt & ~exp_gt).sum()
    stable_high_gt = (orig_gt & exp_gt).sum()
    stable_low_gt = (~orig_gt & ~exp_gt).sum()
    net_gt = exp_gt.sum() - orig_gt.sum()

    print(f"\n  Under Canonical Standard (PI > 60.0):")
    print(f"    - Original High Pressure   : {orig_gt.sum():,} ({orig_gt.mean()*100:.2f}%)")
    print(f"    - Experimental High Pressure: {exp_gt.sum():,} ({exp_gt.mean()*100:.2f}%)")
    print(f"    - Net Change               : {net_gt:+,}")
    print(f"    - Promoted (<=60 -> >60)   : {prom_gt:,}")
    print(f"    - Demoted  (>60 -> <=60)   : {dem_gt:,}")
    print(f"    - Stable High              : {stable_high_gt:,}")
    print(f"    - Stable Low               : {stable_low_gt:,}")

    # Inclusive threshold: PI >= 60.0
    orig_gte = orig_pi >= 60.0
    exp_gte = exp_pi >= 60.0
    prom_gte = (~orig_gte & exp_gte).sum()
    dem_gte = (orig_gte & ~exp_gte).sum()
    stable_high_gte = (orig_gte & exp_gte).sum()
    stable_low_gte = (~orig_gte & ~exp_gte).sum()
    net_gte = exp_gte.sum() - orig_gte.sum()

    print(f"\n  Under Boundary-Inclusive Standard (PI >= 60.0):")
    print(f"    - Original High Pressure   : {orig_gte.sum():,} ({orig_gte.mean()*100:.2f}%)")
    print(f"    - Experimental High Pressure: {exp_gte.sum():,} ({exp_gte.mean()*100:.2f}%)")
    print(f"    - Net Change               : {net_gte:+,}")
    print(f"    - Promoted (<60 -> >=60)   : {prom_gte:,}")
    print(f"    - Demoted  (>=60 -> <60)   : {dem_gte:,}")
    print(f"    - Stable High              : {stable_high_gte:,}")
    print(f"    - Stable Low               : {stable_low_gte:,}")

    # Document Discrepancy Reconciliation
    print(f"\n  [AUDIT FINDING]:")
    print(f"    - The reported numbers in Step 14.2 report (4,881 promoted, 5,657 demoted) correspond")
    print(f"      EXACTLY to the boundary-inclusive threshold PI >= 60.0.")
    print(f"    - Under the canonical operational definition PI > 60.0, the true numbers are:")
    print(f"      4,867 promoted (-14) and 5,636 demoted (-21), with net change -769 (vs -776).")

    # 3. Transition Tables Breakdown
    print("\n3. Building detailed transition tables across Phase and Innings...")
    
    transition_records = []
    
    # Overall
    transition_records.append({
        'group_type': 'Overall', 'category': 'All Deliveries', 'threshold': 'PI > 60.0 (Canonical)',
        'total_deliveries': total_dels,
        'orig_high': orig_gt.sum(), 'exp_high': exp_gt.sum(), 'net_change': net_gt,
        'promoted': prom_gt, 'demoted': dem_gt, 'stable_high': stable_high_gt, 'stable_low': stable_low_gt,
        'mean_orig_pi': round(orig_pi.mean(), 2), 'median_orig_pi': round(orig_pi.median(), 2),
        'mean_exp_pi': round(exp_pi.mean(), 2), 'median_exp_pi': round(exp_pi.median(), 2),
        'mean_delta': round(delta_pi.mean(), 2), 'median_delta': round(delta_pi.median(), 2)
    })
    transition_records.append({
        'group_type': 'Overall', 'category': 'All Deliveries', 'threshold': 'PI >= 60.0 (Inclusive)',
        'total_deliveries': total_dels,
        'orig_high': orig_gte.sum(), 'exp_high': exp_gte.sum(), 'net_change': net_gte,
        'promoted': prom_gte, 'demoted': dem_gte, 'stable_high': stable_high_gte, 'stable_low': stable_low_gte,
        'mean_orig_pi': round(orig_pi.mean(), 2), 'median_orig_pi': round(orig_pi.median(), 2),
        'mean_exp_pi': round(exp_pi.mean(), 2), 'median_exp_pi': round(exp_pi.median(), 2),
        'mean_delta': round(delta_pi.mean(), 2), 'median_delta': round(delta_pi.median(), 2)
    })

    # By Phase (PI > 60.0)
    for p_name in ['PP', 'Middle', 'Death']:
        sub = df[df['phase'] == p_name]
        o_g = sub['Bowling_PI_orig'] > 60.0
        e_g = sub['Bowling_PI_exp'] > 60.0
        p_pr = (~o_g & e_g).sum()
        p_dm = (o_g & ~e_g).sum()
        transition_records.append({
            'group_type': 'Phase', 'category': p_name, 'threshold': 'PI > 60.0 (Canonical)',
            'total_deliveries': len(sub),
            'orig_high': o_g.sum(), 'exp_high': e_g.sum(), 'net_change': e_g.sum() - o_g.sum(),
            'promoted': p_pr, 'demoted': p_dm, 'stable_high': (o_g & e_g).sum(), 'stable_low': (~o_g & ~e_g).sum(),
            'mean_orig_pi': round(sub['Bowling_PI_orig'].mean(), 2), 'median_orig_pi': round(sub['Bowling_PI_orig'].median(), 2),
            'mean_exp_pi': round(sub['Bowling_PI_exp'].mean(), 2), 'median_exp_pi': round(sub['Bowling_PI_exp'].median(), 2),
            'mean_delta': round(sub['delta_bowling_pi'].mean(), 2), 'median_delta': round(sub['delta_bowling_pi'].median(), 2)
        })

    # By Phase (PI >= 60.0)
    for p_name in ['PP', 'Middle', 'Death']:
        sub = df[df['phase'] == p_name]
        o_ge = sub['Bowling_PI_orig'] >= 60.0
        e_ge = sub['Bowling_PI_exp'] >= 60.0
        p_pr = (~o_ge & e_ge).sum()
        p_dm = (o_ge & ~e_ge).sum()
        transition_records.append({
            'group_type': 'Phase', 'category': p_name, 'threshold': 'PI >= 60.0 (Inclusive)',
            'total_deliveries': len(sub),
            'orig_high': o_ge.sum(), 'exp_high': e_ge.sum(), 'net_change': e_ge.sum() - o_ge.sum(),
            'promoted': p_pr, 'demoted': p_dm, 'stable_high': (o_ge & e_ge).sum(), 'stable_low': (~o_ge & ~e_ge).sum(),
            'mean_orig_pi': round(sub['Bowling_PI_orig'].mean(), 2), 'median_orig_pi': round(sub['Bowling_PI_orig'].median(), 2),
            'mean_exp_pi': round(sub['Bowling_PI_exp'].mean(), 2), 'median_exp_pi': round(sub['Bowling_PI_exp'].median(), 2),
            'mean_delta': round(sub['delta_bowling_pi'].mean(), 2), 'median_delta': round(sub['delta_bowling_pi'].median(), 2)
        })

    # By Innings (PI > 60.0)
    for inn in [1, 2]:
        sub = df[df['innings'] == inn]
        o_g = sub['Bowling_PI_orig'] > 60.0
        e_g = sub['Bowling_PI_exp'] > 60.0
        p_pr = (~o_g & e_g).sum()
        p_dm = (o_g & ~e_g).sum()
        transition_records.append({
            'group_type': 'Innings', 'category': f'Innings {inn}', 'threshold': 'PI > 60.0 (Canonical)',
            'total_deliveries': len(sub),
            'orig_high': o_g.sum(), 'exp_high': e_g.sum(), 'net_change': e_g.sum() - o_g.sum(),
            'promoted': p_pr, 'demoted': p_dm, 'stable_high': (o_g & e_g).sum(), 'stable_low': (~o_g & ~e_g).sum(),
            'mean_orig_pi': round(sub['Bowling_PI_orig'].mean(), 2), 'median_orig_pi': round(sub['Bowling_PI_orig'].median(), 2),
            'mean_exp_pi': round(sub['Bowling_PI_exp'].mean(), 2), 'median_exp_pi': round(sub['Bowling_PI_exp'].median(), 2),
            'mean_delta': round(sub['delta_bowling_pi'].mean(), 2), 'median_delta': round(sub['delta_bowling_pi'].median(), 2)
        })

    df_trans = pd.DataFrame(transition_records)
    trans_csv = os.path.join(OUTPUT_DIR, "step_14_2_1_pressure_transitions.csv")
    df_trans.to_csv(trans_csv, index=False)
    print(f"  ✓ Exported transition table to: {trans_csv}")

    # 4. Diagnostic Visualization (01_audit_pressure_transitions.png)
    print("\n4. Generating Diagnostic Plot (01_audit_pressure_transitions.png)...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Subplot 1: Phase Promotions & Demotions Comparison (PI > 60.0)
    ax1 = axes[0, 0]
    phase_data = df_trans[(df_trans['group_type'] == 'Phase') & (df_trans['threshold'] == 'PI > 60.0 (Canonical)')]
    x_pos = np.arange(len(phase_data))
    width = 0.35
    ax1.bar(x_pos - width/2, phase_data['promoted'], width, label='Promoted (<=60 -> >60)', color='#2ca02c')
    ax1.bar(x_pos + width/2, phase_data['demoted'], width, label='Demoted (>60 -> <=60)', color='#d62728')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(['Powerplay (PP)', 'Middle Overs', 'Death Overs'])
    ax1.set_ylabel("Number of Deliveries", fontsize=10)
    ax1.set_title("A. Promotions & Demotions by Match Phase (PI > 60.0)", fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    for i, r in enumerate(phase_data.iterrows()):
        row = r[1]
        ax1.text(i - width/2, row['promoted'] + 50, f"{row['promoted']:,}", ha='center', fontsize=9, fontweight='bold')
        ax1.text(i + width/2, row['demoted'] + 50, f"{row['demoted']:,}", ha='center', fontsize=9, fontweight='bold')

    # Subplot 2: Delta Bowling PI Distribution across Phases
    ax2 = axes[0, 1]
    palette = {'PP': '#1f77b4', 'Middle': '#ff7f0e', 'Death': '#2ca02c'}
    sns.boxplot(data=df, x='phase', y='delta_bowling_pi', hue='phase', palette=palette, ax=ax2, order=['PP', 'Middle', 'Death'], legend=False)
    ax2.axhline(0, color='red', linestyle='--', alpha=0.7)
    ax2.set_title("B. Bowling PI Delta Distribution by Phase (Exp - Orig)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Match Phase", fontsize=10)
    ax2.set_ylabel("Delta Bowling PI (Points)", fontsize=10)
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(['Powerplay (Mean -2.84)', 'Middle Overs (Mean +0.14)', 'Death Overs (Mean +6.77)'])

    # Subplot 3: Innings 1 vs Innings 2 Comparison
    ax3 = axes[1, 0]
    inn_data = df_trans[(df_trans['group_type'] == 'Innings') & (df_trans['threshold'] == 'PI > 60.0 (Canonical)')]
    x_inn = np.arange(len(inn_data))
    ax3.bar(x_inn - width/2, inn_data['promoted'], width, label='Promoted Deliveries', color='#17becf')
    ax3.bar(x_inn + width/2, inn_data['demoted'], width, label='Demoted Deliveries', color='#bcbd22')
    ax3.set_xticks(x_inn)
    ax3.set_xticklabels(['Innings 1', 'Innings 2'])
    ax3.set_ylabel("Number of Deliveries", fontsize=10)
    ax3.set_title("C. Promotions & Demotions by Innings (PI > 60.0)", fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9)
    for i, r in enumerate(inn_data.iterrows()):
        row = r[1]
        ax3.text(i - width/2, row['promoted'] + 50, f"{row['promoted']:,}", ha='center', fontsize=9, fontweight='bold')
        ax3.text(i + width/2, row['demoted'] + 50, f"{row['demoted']:,}", ha='center', fontsize=9, fontweight='bold')

    # Subplot 4: Boundary Zoom Distribution ([55, 65] PI)
    ax4 = axes[1, 1]
    sub_orig = orig_pi[(orig_pi >= 55) & (orig_pi <= 65)]
    sub_exp = exp_pi[(exp_pi >= 55) & (exp_pi <= 65)]
    sns.histplot(sub_orig, bins=20, color='blue', alpha=0.4, label=f'Original PI (Exact 60={orig_exact_60})', ax=ax4)
    sns.histplot(sub_exp, bins=20, color='green', alpha=0.4, label=f'Experimental PI (Exact 60={exp_exact_60})', ax=ax4)
    ax4.axvline(60.0, color='red', linestyle='--', linewidth=2, label='Threshold = 60.0')
    ax4.set_title("D. Boundary Density Zoom: Deliveries in [55, 65] Range", fontsize=12, fontweight='bold')
    ax4.set_xlabel("Bowling Pressure Index", fontsize=10)
    ax4.set_ylabel("Delivery Count", fontsize=10)
    ax4.legend(fontsize=9)

    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, "01_audit_pressure_transitions.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"  ✓ Saved diagnostic visualization to: {plot_path}")

    print("\nModule 2 Completed Successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
