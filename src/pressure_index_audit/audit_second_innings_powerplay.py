"""
Investigation C — Second-Innings Powerplay Scoreboard Pressure Audit
====================================================================

This script investigates whether the existing PI_B2_PP formula:
    T = (0.50 * R) + (0.30 * W) + (0.20 * O)
    PI = (0.65 * T) + (0.35 * I)
understates pressure on top-order batters in steep chases (e.g. chasing 200+ at 0/0),
and whether settled batters (striker_bf >= 10, I = 0) are trapped below 60.0 even at RRR > 12.

It tests controlled simulation scenarios and evaluates experimental alternatives on
all 28,883 historical second-innings Powerplay deliveries.

Outputs:
- outputs/pressure_index_audit/05_chase_scenario_pressure_curves.png
- outputs/pressure_index_audit/06_pp_chase_actual_deliveries_scatter.png
- outputs/pressure_index_audit/second_innings_pp_scenarios.csv
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


def calc_pi_b2_pp(target, wickets, over_completed, striker_bf, 
                   w_r=0.50, w_w=0.30, w_o=0.20, alpha=0.65):
    """Calculate PI_B2_PP for arbitrary parameters."""
    balls_rem = 120 - int(over_completed * 6)
    rrr = (target / balls_rem) * 6.0
    r = np.clip((rrr - 6.0) / 6.0 * 100.0, 0.0, 100.0)
    w = np.clip((wickets / 6.0) * 100.0, 0.0, 100.0)
    o = np.clip((over_completed / 6.0) * 100.0, 0.0, 100.0)
    t = w_r * r + w_w * w + w_o * o
    i = np.clip((10.0 - striker_bf) / 10.0 * 100.0, 0.0, 100.0)
    pi = alpha * t + (1.0 - alpha) * i
    return rrr, r, w, o, t, i, pi


def run_second_innings_pp_audit():
    print("Running Controlled Second-Innings Powerplay Simulations...")

    # 1. Grid of Scenarios
    targets = [120, 140, 160, 180, 200, 220, 240]
    wicket_states = [0, 1, 2, 3, 4]
    overs = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    settling_states = [0, 5, 10] # balls faced (I = 100, 50, 0)

    records = []
    for tgt in targets:
        for wk in wicket_states:
            for ov in overs:
                for bf in settling_states:
                    # Baseline: T = 0.50*R + 0.30*W + 0.20*O, PI = 0.65*T + 0.35*I
                    rrr, r, w, o, t_base, i, pi_base = calc_pi_b2_pp(tgt, wk, ov, bf, 0.50, 0.30, 0.20, 0.65)
                    
                    # Variant 1 (Target Dominance): T = 0.65*R + 0.20*W + 0.15*O, PI = 0.75*T + 0.25*I
                    _, _, _, _, t_v1, _, pi_v1 = calc_pi_b2_pp(tgt, wk, ov, bf, 0.65, 0.20, 0.15, 0.75)
                    
                    # Variant 2 (Scoreboard Dominance): T = 0.70*R + 0.15*W + 0.15*O, PI = 0.70*T + 0.30*I
                    _, _, _, _, t_v2, _, pi_v2 = calc_pi_b2_pp(tgt, wk, ov, bf, 0.70, 0.15, 0.15, 0.70)

                    # Variant 3 (Balanced Scoreboard): T = 0.60*R + 0.25*W + 0.15*O, PI = 0.70*T + 0.30*I
                    _, _, _, _, t_v3, _, pi_v3 = calc_pi_b2_pp(tgt, wk, ov, bf, 0.60, 0.25, 0.15, 0.70)

                    records.append({
                        'target': tgt,
                        'wickets': wk,
                        'over_completed': ov,
                        'striker_bf': bf,
                        'settling_i': i,
                        'rrr': round(rrr, 2),
                        'r_score': round(r, 1),
                        'w_score': round(w, 1),
                        'o_score': round(o, 1),
                        'pi_baseline': round(pi_base, 2),
                        'pi_variant1': round(pi_v1, 2),
                        'pi_variant2': round(pi_v2, 2),
                        'pi_variant3': round(pi_v3, 2)
                    })

    sim_df = pd.DataFrame(records)
    sim_df.to_csv(OUTPUT_DIR / "second_innings_pp_scenarios.csv", index=False)
    print(f"Saved simulation scenarios to: {OUTPUT_DIR / 'second_innings_pp_scenarios.csv'}")

    # Inspect Key Scenarios
    print("\n" + "="*70)
    print("CRITICAL SCENARIO COMPARISON: BALL 0.1 (0/0 AT START OF INNINGS)")
    print("="*70)
    ball_0_1 = sim_df[(sim_df['over_completed'] == 0.0) & (sim_df['wickets'] == 0) & (sim_df['striker_bf'] == 0)]
    print(ball_0_1[['target', 'rrr', 'r_score', 'pi_baseline', 'pi_variant1', 'pi_variant2', 'pi_variant3']].to_string(index=False))

    print("\n" + "="*70)
    print("CRITICAL SCENARIO: SETTLED BATTER (10+ BALLS FACED, I = 0) AT 0/0")
    print("="*70)
    settled_0_0 = sim_df[(sim_df['over_completed'] == 0.0) & (sim_df['wickets'] == 0) & (sim_df['striker_bf'] == 10)]
    print(settled_0_0[['target', 'rrr', 'r_score', 'pi_baseline', 'pi_variant1', 'pi_variant2', 'pi_variant3']].to_string(index=False))

    print("\n" + "="*70)
    print("CRITICAL SCENARIO: OVER 4.0, CHASING 200, 2 WICKETS DOWN, SETTLED BATTER")
    print("="*70)
    chase_200_mid = sim_df[(sim_df['target'] == 200) & (sim_df['wickets'] == 2) & 
                           (sim_df['over_completed'] == 4.0) & (sim_df['striker_bf'] == 10)]
    print(chase_200_mid[['target', 'wickets', 'over_completed', 'rrr', 'pi_baseline', 'pi_variant1', 'pi_variant2', 'pi_variant3']].to_string(index=False))

    # 2. Historical Second-Innings Powerplay Deliveries Audit
    print("\nAuditing Historical Second-Innings Powerplay Deliveries...")
    df = pd.read_csv(DATA_DIR / "delivery_pressure_index.csv")
    inn2_pp = df[(df['innings'] == 2) & (df['phase'] == 'PP')].copy()
    n_inn2_pp = len(inn2_pp)
    print(f"Total Innings 2 Powerplay Deliveries: {n_inn2_pp:,}")

    # Compute Variant 1 on actual deliveries
    r_act = np.clip(((inn2_pp['required_run_rate'] - 6.0) / 6.0) * 100.0, 0.0, 100.0)
    w_act = np.clip((inn2_pp['wickets_before'] / 6.0) * 100.0, 0.0, 100.0)
    o_act = np.clip((inn2_pp['phase_overs_completed'] / 6.0) * 100.0, 0.0, 100.0)
    i_act = np.clip(((10.0 - inn2_pp['striker_balls_faced_before']) / 10.0) * 100.0, 0.0, 100.0)
    
    t_v1_act = 0.65 * r_act + 0.20 * w_act + 0.15 * o_act
    inn2_pp['PI_B2_PP_V1'] = 0.75 * t_v1_act + 0.25 * i_act

    # Steep Chases Analysis (RRR >= 10.0)
    steep_mask = inn2_pp['required_run_rate'] >= 10.0
    n_steep = steep_mask.sum()
    steep_low_base = (steep_mask & (inn2_pp['Batting_PI'] <= 60.0)).sum()
    steep_low_v1 = (steep_mask & (inn2_pp['PI_B2_PP_V1'] <= 60.0)).sum()

    print(f"\nSteep Chases (RRR >= 10.0): {n_steep:,} deliveries")
    print(f"  Baseline Classified as Low/Mod (PI <= 60.0): {steep_low_base:,} ({steep_low_base/n_steep*100:.1f}%)")
    print(f"  Variant 1 Classified as Low/Mod (PI <= 60.0): {steep_low_v1:,} ({steep_low_v1/n_steep*100:.1f}%)")

    # Modest Chases Analysis (RRR <= 7.0)
    modest_mask = inn2_pp['required_run_rate'] <= 7.0
    n_modest = modest_mask.sum()
    modest_high_base = (modest_mask & (inn2_pp['Batting_PI'] > 60.0)).sum()
    modest_high_v1 = (modest_mask & (inn2_pp['PI_B2_PP_V1'] > 60.0)).sum()

    print(f"\nModest Chases (RRR <= 7.0): {n_modest:,} deliveries")
    print(f"  Baseline Classified as High (PI > 60.0): {modest_high_base:,} ({modest_high_base/n_modest*100:.1f}%)")
    print(f"  Variant 1 Classified as High (PI > 60.0): {modest_high_v1:,} ({modest_high_v1/n_modest*100:.1f}%)")

    # Overall High Pressure Deliveries in Innings 2 PP
    hp_base = (inn2_pp['Batting_PI'] > 60.0).sum()
    hp_v1 = (inn2_pp['PI_B2_PP_V1'] > 60.0).sum()
    print(f"\nOverall Innings 2 PP High Pressure Deliveries:")
    print(f"  Baseline:  {hp_base:,} ({hp_base/n_inn2_pp*100:.1f}%)")
    print(f"  Variant 1: {hp_v1:,} ({hp_v1/n_inn2_pp*100:.1f}%)")

    # 3. Generate Figure 5: Controlled Scenario Curves
    print("\nGenerating Figure 5: Controlled Scenario Curves...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Subplot A: Ball 0.1 Opening delivery vs. Target for different formulas
    tgt_range = np.linspace(100, 240, 50)
    base_curve = [calc_pi_b2_pp(tg, 0, 0, 0, 0.50, 0.30, 0.20, 0.65)[6] for tg in tgt_range]
    v1_curve = [calc_pi_b2_pp(tg, 0, 0, 0, 0.65, 0.20, 0.15, 0.75)[6] for tg in tgt_range]
    v2_curve = [calc_pi_b2_pp(tg, 0, 0, 0, 0.70, 0.15, 0.15, 0.70)[6] for tg in tgt_range]
    settled_base = [calc_pi_b2_pp(tg, 0, 0, 10, 0.50, 0.30, 0.20, 0.65)[6] for tg in tgt_range]
    settled_v1 = [calc_pi_b2_pp(tg, 0, 0, 10, 0.65, 0.20, 0.15, 0.75)[6] for tg in tgt_range]

    axes[0].plot(tgt_range, base_curve, color='#e74c3c', lw=2.2, label='Baseline (Ball 0.1, Unsettled I=100)')
    axes[0].plot(tgt_range, v1_curve, color='#2980b9', lw=2.2, label='Variant 1 (Ball 0.1, Unsettled I=100)')
    axes[0].plot(tgt_range, settled_base, color='#e74c3c', linestyle='--', lw=2.0, label='Baseline (Settled Batter I=0)')
    axes[0].plot(tgt_range, settled_v1, color='#2980b9', linestyle='--', lw=2.0, label='Variant 1 (Settled Batter I=0)')

    axes[0].axhline(60.0, color='black', linestyle=':', lw=1.5, label='High Pressure Cutoff (60.0)')
    axes[0].axvline(180, color='gray', linestyle='-.', alpha=0.6, label='T20 Par Target (180)')
    axes[0].set_title("A. Target vs. Pressure Index at Over 0.1 (0/0)", fontsize=13, fontweight='bold', pad=10)
    axes[0].set_xlabel("Target Score", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("Pressure Index (PI)", fontsize=11, fontweight='bold')
    axes[0].set_ylim(0, 100)
    axes[0].legend(loc='upper left', frameon=True, fontsize=9)

    # Subplot B: Effect of Wickets at Over 3.0 (Target 180, Settled Batter)
    wk_range = [0, 1, 2, 3, 4]
    base_wk = [calc_pi_b2_pp(180, w, 3.0, 10, 0.50, 0.30, 0.20, 0.65)[6] for w in wk_range]
    v1_wk = [calc_pi_b2_pp(180, w, 3.0, 10, 0.65, 0.20, 0.15, 0.75)[6] for w in wk_range]
    v2_wk = [calc_pi_b2_pp(180, w, 3.0, 10, 0.70, 0.15, 0.15, 0.70)[6] for w in wk_range]

    axes[1].plot(wk_range, base_wk, 'o-', color='#e74c3c', lw=2.2, label='Baseline (w_W=0.30)')
    axes[1].plot(wk_range, v1_wk, 's-', color='#2980b9', lw=2.2, label='Variant 1 (w_W=0.20)')
    axes[1].plot(wk_range, v2_wk, '^-', color='#27ae60', lw=2.2, label='Variant 2 (w_W=0.15)')

    axes[1].axhline(60.0, color='black', linestyle=':', lw=1.5, label='High Pressure Cutoff (60.0)')
    axes[1].set_title("B. Wickets Lost vs. PI (Over 3.0, Target 180, Settled)", fontsize=13, fontweight='bold', pad=10)
    axes[1].set_xlabel("Wickets Down", fontsize=11, fontweight='bold')
    axes[1].set_ylabel("Pressure Index (PI)", fontsize=11, fontweight='bold')
    axes[1].set_ylim(20, 75)
    axes[1].set_xticks(wk_range)
    axes[1].legend(loc='upper left', frameon=True, fontsize=9)

    plt.tight_layout()
    fig_path5 = OUTPUT_DIR / "05_chase_scenario_pressure_curves.png"
    plt.savefig(fig_path5, dpi=300)
    plt.close()
    print(f"Saved: {fig_path5}")

    # 4. Generate Figure 6: Actual Deliveries Scatter
    print("\nGenerating Figure 6: Historical Deliveries Scatter...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    sample_inn2 = inn2_pp.sample(n=4000, random_state=42)

    # Subplot A: Baseline RRR vs PI
    sc1 = axes[0].scatter(sample_inn2['required_run_rate'], sample_inn2['Batting_PI'], 
                          c=sample_inn2['wickets_before'], cmap='viridis', alpha=0.5, s=18)
    cbar1 = plt.colorbar(sc1, ax=axes[0])
    cbar1.set_label('Wickets Lost Before', fontweight='bold')
    axes[0].axhline(60.0, color='red', linestyle='--', lw=1.5, label='Cutoff (60.0)')
    axes[0].axvline(10.0, color='black', linestyle=':', lw=1.5, label='Steep Chase (RRR >= 10)')
    axes[0].set_title("A. Baseline PI_B2_PP vs. RRR (Historical Deliveries)", fontsize=12, fontweight='bold', pad=10)
    axes[0].set_xlabel("Required Run Rate (RRR)", fontsize=10, fontweight='bold')
    axes[0].set_ylabel("Batting PI", fontsize=10, fontweight='bold')
    axes[0].set_xlim(2, 20)
    axes[0].set_ylim(0, 100)
    axes[0].legend(loc='lower right', frameon=True, fontsize=9)

    # Subplot B: Variant 1 RRR vs PI
    sc2 = axes[1].scatter(sample_inn2['required_run_rate'], sample_inn2['PI_B2_PP_V1'], 
                          c=sample_inn2['wickets_before'], cmap='viridis', alpha=0.5, s=18)
    cbar2 = plt.colorbar(sc2, ax=axes[1])
    cbar2.set_label('Wickets Lost Before', fontweight='bold')
    axes[1].axhline(60.0, color='red', linestyle='--', lw=1.5, label='Cutoff (60.0)')
    axes[1].axvline(10.0, color='black', linestyle=':', lw=1.5, label='Steep Chase (RRR >= 10)')
    axes[1].set_title("B. Variant 1 PI_B2_PP vs. RRR (Historical Deliveries)", fontsize=12, fontweight='bold', pad=10)
    axes[1].set_xlabel("Required Run Rate (RRR)", fontsize=10, fontweight='bold')
    axes[1].set_ylabel("Batting PI (Variant 1)", fontsize=10, fontweight='bold')
    axes[1].set_xlim(2, 20)
    axes[1].set_ylim(0, 100)
    axes[1].legend(loc='lower right', frameon=True, fontsize=9)

    plt.tight_layout()
    fig_path6 = OUTPUT_DIR / "06_pp_chase_actual_deliveries_scatter.png"
    plt.savefig(fig_path6, dpi=300)
    plt.close()
    print(f"Saved: {fig_path6}")


if __name__ == "__main__":
    run_second_innings_pp_audit()
