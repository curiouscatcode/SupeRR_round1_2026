"""
EDA Module 07: Outlier Investigation & Methodology Vulnerability Audits
=======================================================================
Analyzes:
1. Multidimensional anomaly detection for batters and bowlers.
2. Generates comprehensive CSV anomaly tables:
   - outputs/exploratory_analysis/flagged_batters_anomalies.csv
   - outputs/exploratory_analysis/flagged_bowlers_anomalies.csv
   - outputs/exploratory_analysis/small_sample_high_score_players.csv
   - outputs/exploratory_analysis/conflicting_metrics_players.csv
   - outputs/exploratory_analysis/methodology_vulnerabilities_cases.csv
3. Deep-dive into 5 critical methodology vulnerabilities:
   - The Bumrah Paradox (containment suppressing wickets)
   - The 60-Ball Threshold Cliff (Overton at 59 balls vs 60-ball qualifiers)
   - Narine Rank Collapse (high SR vs high dot/dismissal tension)
   - Dhoni Phase Inversion (Rank 2 Death vs Rank 86 Middle)
   - Constant Prior Distortion Across Non-Homogeneous Roles

Generates:
- outputs/exploratory_analysis/18_anomaly_multidimensional_clusters.png
- outputs/exploratory_analysis/19_methodology_vulnerabilities_showcase.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = Path("outputs/exploratory_analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
b_rank = pd.read_csv("data/processed/batter_reliability_rankings.csv")
bo_rank = pd.read_csv("data/processed/bowler_reliability_rankings.csv")
p_spec = pd.read_csv("data/processed/phase_specialist_rankings.csv")

print(f"Loaded {len(b_rank)} batters and {len(bo_rank)} bowlers for Anomaly Analysis.")


# =========================================================================
# 1. GENERATE ANOMALY CSV FILES
# =========================================================================
def generate_anomaly_csvs():
    # -------------------------------------------------------------
    # 1.1 Flagged Batters Anomalies CSV
    # -------------------------------------------------------------
    flagged_batters = []
    
    # Anomaly A: Extreme Raw SR on small sample
    sub_a = b_rank[(b_rank['high_balls_faced'] < 30) & (b_rank['sr_obs'] >= 220.0)].copy()
    for _, r in sub_a.iterrows():
        flagged_batters.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_balls': r['high_balls_faced'], 'raw_metric': f"SR {r['sr_obs']:.1f}",
            'bayesian_metric': f"SR* {r['sr_star']:.1f}", 'score': r['brs'],
            'anomaly_category': 'Small-Sample Extreme Strike Rate',
            'cricketing_review_note': 'Explosive cameo on very low sample (<30 balls); heavily regressed by prior.'
        })
        
    # Anomaly B: Zero Dismissals on substantial sample (N >= 30)
    sub_b = b_rank[(b_rank['high_balls_faced'] >= 30) & (b_rank['high_dismissals'] == 0)].copy()
    for _, r in sub_b.iterrows():
        flagged_batters.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_balls': r['high_balls_faced'], 'raw_metric': "0 Dismissals (100% Surv)",
            'bayesian_metric': f"Surv* {r['surv_star']:.1f}%", 'score': r['brs'],
            'anomaly_category': 'Zero Dismissal Outlier',
            'cricketing_review_note': f"Faced {int(r['high_balls_faced'])} high-pressure deliveries without being dismissed; maxes out Score Surv."
        })

    # Anomaly C: Extreme Dot Ball Rate but High Strike Rate (All-or-Nothing)
    sub_c = b_rank[(b_rank['high_balls_faced'] >= 30) & (b_rank['high_boundary_pct'] >= 20.0) & (b_rank['high_dot_pct'] >= 45.0)].copy()
    for _, r in sub_c.iterrows():
        flagged_batters.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_balls': r['high_balls_faced'], 'raw_metric': f"Bnd {r['high_boundary_pct']:.1f}%, Dot {r['high_dot_pct']:.1f}%",
            'bayesian_metric': f"Net Exec {r['score_exec']:.1f}", 'score': r['brs'],
            'anomaly_category': 'All-or-Nothing Boundary-Dependent Batter',
            'cricketing_review_note': 'High boundary rate masked by heavy dot-ball accumulation; severe vulnerability if boundaries dried up.'
        })

    # Anomaly D: Extreme Negative Clutch Delta (Collapse under pressure, N >= 40)
    sub_d = b_rank[(b_rank['high_balls_faced'] >= 40) & (b_rank['strike_rate_delta'] <= -40.0)].copy()
    for _, r in sub_d.iterrows():
        flagged_batters.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_balls': r['high_balls_faced'], 'raw_metric': f"ΔSR {r['strike_rate_delta']:.1f}",
            'bayesian_metric': f"Diff* {r['diff_sr_star']:.1f}", 'score': r['brs'],
            'anomaly_category': 'Severe Clutch Scoring Collapse',
            'cricketing_review_note': f"Scoring velocity drops by > 40 points in high-pressure regime compared to low/mod pressure."
        })

    df_flagged_bat = pd.DataFrame(flagged_batters).drop_duplicates(subset=['player_id', 'anomaly_category'])
    out_b_csv = OUT_DIR / "flagged_batters_anomalies.csv"
    df_flagged_bat.to_csv(out_b_csv, index=False)
    print(f"Generated: {out_b_csv} ({len(df_flagged_bat)} flagged entries)")

    # -------------------------------------------------------------
    # 1.2 Flagged Bowlers Anomalies CSV
    # -------------------------------------------------------------
    flagged_bowlers = []
    
    # Anomaly A: Expensive Strike Bowlers (Econ >= 10.5, Wk >= 5, N >= 30)
    sub_bo_a = bo_rank[(bo_rank['high_legal_balls'] >= 30) & (bo_rank['high_economy_rate'] >= 10.5) & (bo_rank['high_wickets'] >= 5)].copy()
    for _, r in sub_bo_a.iterrows():
        flagged_bowlers.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_legal_balls': r['high_legal_balls'], 'raw_metric': f"Econ {r['high_economy_rate']:.1f}, Wk {int(r['high_wickets'])}",
            'bayesian_metric': f"Econ* {r['econ_star']:.1f}, Wk* {r['wk_star']:.1f}%", 'score': r['bors'],
            'anomaly_category': 'Expensive Strike Bowler (Trade-off)',
            'cricketing_review_note': 'High breakthrough capability achieved at the expense of run-leakage (Econ >= 10.5).'
        })

    # Anomaly B: Restrictive Non-Wicket Takers (Econ <= 7.2, Wk <= 2, N >= 40)
    sub_bo_b = bo_rank[(bo_rank['high_legal_balls'] >= 40) & (bo_rank['high_economy_rate'] <= 7.5) & (bo_rank['high_wickets'] <= 2)].copy()
    for _, r in sub_bo_b.iterrows():
        flagged_bowlers.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_legal_balls': r['high_legal_balls'], 'raw_metric': f"Econ {r['high_economy_rate']:.1f}, Wk {int(r['high_wickets'])}",
            'bayesian_metric': f"Econ* {r['econ_star']:.1f}, Wk* {r['wk_star']:.1f}%", 'score': r['bors'],
            'anomaly_category': 'Restrictive Shield (Zero/Low Wickets)',
            'cricketing_review_note': 'Exceptional containment under pressure, but takes very few wickets; penalised in Score Wk.'
        })

    # Anomaly C: High Dot % but High Economy (Boundary Leakage Masked by Dots)
    sub_bo_c = bo_rank[(bo_rank['high_legal_balls'] >= 30) & (bo_rank['high_dot_pct'] >= 45.0) & (bo_rank['high_economy_rate'] >= 9.5)].copy()
    for _, r in sub_bo_c.iterrows():
        flagged_bowlers.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_legal_balls': r['high_legal_balls'], 'raw_metric': f"Dot {r['high_dot_pct']:.1f}%, Econ {r['high_economy_rate']:.1f}",
            'bayesian_metric': f"Score Dot {r['score_dot']:.1f}, Score Econ {r['score_econ']:.1f}", 'score': r['bors'],
            'anomaly_category': 'High Dot Rate with Severe Boundary Bleed',
            'cricketing_review_note': 'Bowls many dot balls but non-dot deliveries are heavily punished for boundaries.'
        })

    # Anomaly D: Extreme Economy Leakage under Pressure (ΔEcon <= -2.5 RPO, N >= 40)
    bo_rank_copy = bo_rank.copy()
    bo_rank_copy['tightening'] = bo_rank_copy['low_mod_economy_rate'] - bo_rank_copy['high_economy_rate']
    sub_bo_d = bo_rank_copy[(bo_rank_copy['high_legal_balls'] >= 40) & (bo_rank_copy['tightening'] <= -2.5)].copy()
    for _, r in sub_bo_d.iterrows():
        flagged_bowlers.append({
            'player_id': r['player_id'], 'player_name': r['player_name'], 'tier': r['tier'],
            'high_legal_balls': r['high_legal_balls'], 'raw_metric': f"ΔEcon {r['tightening']:.2f} RPO",
            'bayesian_metric': f"Diff* {r['diff_econ_star']:.2f}", 'score': r['bors'],
            'anomaly_category': 'Severe Pressure Economy Bleeder',
            'cricketing_review_note': 'Economy deteriorates by > 2.5 RPO in high-pressure scenarios compared to low-pressure play.'
        })

    df_flagged_bo = pd.DataFrame(flagged_bowlers).drop_duplicates(subset=['player_id', 'anomaly_category'])
    out_bo_csv = OUT_DIR / "flagged_bowlers_anomalies.csv"
    df_flagged_bo.to_csv(out_bo_csv, index=False)
    print(f"Generated: {out_bo_csv} ({len(df_flagged_bo)} flagged entries)")

    # -------------------------------------------------------------
    # 1.3 Small Sample High Score Players (N < 60 but Score >= 65.0)
    # -------------------------------------------------------------
    small_high_bat = b_rank[(b_rank['high_balls_faced'] < 60) & (b_rank['brs'] >= 65.0)].copy()
    small_high_bat['role'] = 'Batter'
    small_high_bat['sample_deliveries'] = small_high_bat['high_balls_faced']
    small_high_bat['reliability_score'] = small_high_bat['brs']
    small_high_bat['raw_core_metric'] = small_high_bat['sr_obs'].apply(lambda v: f"SR {v:.1f}")
    small_high_bat['bayesian_core_metric'] = small_high_bat['sr_star'].apply(lambda v: f"SR* {v:.1f}")

    small_high_bowl = bo_rank[(bo_rank['high_legal_balls'] < 60) & (bo_rank['bors'] >= 65.0)].copy()
    small_high_bowl['role'] = 'Bowler'
    small_high_bowl['sample_deliveries'] = small_high_bowl['high_legal_balls']
    small_high_bowl['reliability_score'] = small_high_bowl['bors']
    small_high_bowl['raw_core_metric'] = small_high_bowl['econ_obs'].apply(lambda v: f"Econ {v:.1f}")
    small_high_bowl['bayesian_core_metric'] = small_high_bowl['econ_star'].apply(lambda v: f"Econ* {v:.1f}")

    cols_small = ['role', 'player_id', 'player_name', 'tier', 'sample_deliveries', 
                  'reliability_score', 'raw_core_metric', 'bayesian_core_metric']
    df_small = pd.concat([small_high_bat[cols_small], small_high_bowl[cols_small]]).sort_values('reliability_score', ascending=False)
    out_small_csv = OUT_DIR / "small_sample_high_score_players.csv"
    df_small.to_csv(out_small_csv, index=False)
    print(f"Generated: {out_small_csv} ({len(df_small)} small-sample high-score players)")

    # -------------------------------------------------------------
    # 1.4 Conflicting Metrics Players CSV
    # -------------------------------------------------------------
    # Combine all-or-nothing batters, expensive strike bowlers, and restrictive shield bowlers
    conflicts = []
    for _, r in df_flagged_bat[df_flagged_bat['anomaly_category'].str.contains('All-or-Nothing')].iterrows():
        conflicts.append({
            'role': 'Batter', 'player_name': r['player_name'], 'tier': r['tier'],
            'sample_deliveries': r['high_balls'], 'conflict_type': 'High Boundary % vs High Dot Ball %',
            'metrics_evidence': r['raw_metric'], 'score': r['score']
        })
    for _, r in df_flagged_bo[df_flagged_bo['anomaly_category'].str.contains('Expensive Strike')].iterrows():
        conflicts.append({
            'role': 'Bowler', 'player_name': r['player_name'], 'tier': r['tier'],
            'sample_deliveries': r['high_legal_balls'], 'conflict_type': 'High Wickets vs Leaked Economy (Econ >= 10.5)',
            'metrics_evidence': r['raw_metric'], 'score': r['score']
        })
    for _, r in df_flagged_bo[df_flagged_bo['anomaly_category'].str.contains('Restrictive Shield')].iterrows():
        conflicts.append({
            'role': 'Bowler', 'player_name': r['player_name'], 'tier': r['tier'],
            'sample_deliveries': r['high_legal_balls'], 'conflict_type': 'Elite Economy vs Minimal Wickets (Wk <= 2)',
            'metrics_evidence': r['raw_metric'], 'score': r['score']
        })
    df_conflicts = pd.DataFrame(conflicts).sort_values('score', ascending=False)
    out_conflicts_csv = OUT_DIR / "conflicting_metrics_players.csv"
    df_conflicts.to_csv(out_conflicts_csv, index=False)
    print(f"Generated: {out_conflicts_csv} ({len(df_conflicts)} conflicting metrics players)")

    # -------------------------------------------------------------
    # 1.5 Methodology Vulnerabilities Cases CSV
    # -------------------------------------------------------------
    vulnerabilities = [
        {
            'case_id': 'VULN-01',
            'case_name': 'The Bumrah Paradox (Containment Wicket Suppression)',
            'affected_player': 'Jasprit Bumrah',
            'player_role': 'Bowler',
            'sample_deliveries': 168,
            'observed_metrics': 'Econ 6.89, Wickets 3 (Wk% 1.79%), Dots 50.0%',
            'ranking_outcome': 'Tier 1 Rank #14 (BoRS 68.64)',
            'methodological_root_cause': (
                'Because batters play Bumrah with extreme risk-aversion (leaving/defending), '
                'his high-pressure wicket rate is artificially depressed (1.79% vs 6.21% league prior). '
                'Score Wk drops to 45.42, preventing him from reaching the Top 5 despite a masterclass 6.89 economy.'
            ),
            'recommended_remedy': 'Introduce a composite pressure-conceded index that rewards dot-ball containment over raw wickets when economy is elite.'
        },
        {
            'case_id': 'VULN-02',
            'case_name': 'The 60-Ball Hard Threshold Boundary Cliff',
            'affected_player': 'Jamie Overton',
            'player_role': 'Batter',
            'sample_deliveries': 59,
            'observed_metrics': 'SR 228.81, Surv 96.61%, BRS 79.54',
            'ranking_outcome': 'Tier 2 Specialist Rank #2 (Strictly Excluded from Tier 1)',
            'methodological_root_cause': (
                'Overton faced exactly 59 high-pressure deliveries—1 ball short of the 60-ball Tier 1 threshold. '
                'His 79.54 BRS would place him #1 overall in Tier 1 ahead of Heinrich Klaasen (78.33), '
                'yet he is barred from the primary competition podium by a single delivery.'
            ),
            'recommended_remedy': 'Implement a continuous sigmoidal confidence weight rather than a binary knife-edge cutoff.'
        },
        {
            'case_id': 'VULN-03',
            'case_name': 'Sunil Narine Strike Rate Collapse Under Multi-Component Tension',
            'affected_player': 'Sunil Narine',
            'player_role': 'Batter',
            'sample_deliveries': 62,
            'observed_metrics': 'Raw SR 174.19 (Rank #15 Raw), BRS 53.15 (Rank #85)',
            'ranking_outcome': 'Tier 1 Rank #85 (-52 Rank Movement)',
            'methodological_root_cause': (
                'Narine strikes at 174.19 in high pressure, but has a 12.9% dismissal rate and 53.2% dot rate. '
                'His Score Surv drops to 46.50 and Score Exec drops to 39.80, causing a catastrophic 52-place rank plunge.'
            ),
            'recommended_remedy': 'Distinguish between opening pinch-hitters whose job is early risk-taking versus traditional anchors.'
        },
        {
            'case_id': 'VULN-04',
            'case_name': 'MS Dhoni Extreme Phase-Dependent Reliability Inversion',
            'affected_player': 'Mahendra Singh Dhoni',
            'player_role': 'Batter',
            'sample_deliveries': 85,
            'observed_metrics': 'Death SR 222.0 (Rank #2 Death), Middle SR 102.5 (Rank #86 Middle)',
            'ranking_outcome': 'Tier 1 Rank #25 (BRS 65.51)',
            'methodological_root_cause': (
                'Dhoni is an immortal death-overs finisher (#2 overall behind Rinku Singh), but bats very conservatively '
                'in the middle overs. Because BRS pools all phases together, his mediocre middle-overs SR drags down '
                'his overall standing, obscuring his true match-winning capability.'
            ),
            'recommended_remedy': 'Weight phase reliability by player batting position or evaluate role specialists within their active phases.'
        },
        {
            'case_id': 'VULN-05',
            'case_name': 'First-Innings Target Under-Reconstruction Distortion',
            'affected_player': 'Chasing Batters in 38 Flagged Matches',
            'player_role': 'Chasing Batters',
            'sample_deliveries': 4177,
            'observed_metrics': 'Targets reconstructed 1 to 8 runs lower due to unrecorded extras',
            'ranking_outcome': 'Subtly Understated RRR and PI in Chases',
            'methodological_root_cause': (
                'In 38 matches, target reconstruction deficit caused required run rates to be slightly underestimated, '
                'falsely classifying ~150 deliveries as moderate pressure instead of high pressure.'
            ),
            'recommended_remedy': 'Sensitivity analysis confirms high rank stability (rho > 0.998), but official scores should be ingested.'
        }
    ]
    df_vuln = pd.DataFrame(vulnerabilities)
    out_vuln_csv = OUT_DIR / "methodology_vulnerabilities_cases.csv"
    df_vuln.to_csv(out_vuln_csv, index=False)
    print(f"Generated: {out_vuln_csv} (5 in-depth case studies)")


# =========================================================================
# CHART 18: ANOMALY MULTIDIMENSIONAL CLUSTERS
# =========================================================================
def plot_anomaly_multidimensional_clusters():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300)
    
    # 18.1 Batter Anomaly Clusters (SR vs Dot% colored by Dismissal%)
    b_plot = b_rank[b_rank['high_balls_faced'] >= 15].copy()
    sc1 = ax1.scatter(b_plot['high_dot_pct'], b_plot['high_strike_rate'],
                      c=b_plot['high_dismissal_pct'], cmap='coolwarm', s=b_plot['high_balls_faced']*0.7,
                      edgecolors='black', linewidths=0.4, alpha=0.85)
    cbar1 = plt.colorbar(sc1, ax=ax1, pad=0.02)
    cbar1.set_label('Dismissal % (High Pressure)', fontsize=9.5, fontweight='bold')
    
    ax1.axvline(45.0, color='#7f8c8d', linestyle=':', label='High Dot Cutoff (45%)')
    ax1.axhline(150.0, color='#7f8c8d', linestyle=':', label='High SR Cutoff (150)')

    # Shaded Anomaly Region: All-or-Nothing Batters (Top-Right: High SR + High Dots)
    ax1.axvspan(45.0, 75.0, ymin=0.5, ymax=1.0, color='#fadbd8', alpha=0.25, label='Anomaly Zone: All-or-Nothing')
    
    # Annotate key outliers
    annot_b = ['Sunil Narine', 'Glenn Maxwell', 'Heinrich Klaasen', 'Mahendra Singh Dhoni', 'Jos Buttler']
    for _, r in b_plot[b_plot['player_name'].isin(annot_b)].iterrows():
        lbl = 'MS Dhoni' if 'Dhoni' in r['player_name'] else r['player_name'].split()[-1]
        ax1.annotate(f"{lbl}\n(SR {r['high_strike_rate']:.0f}, Dot {r['high_dot_pct']:.0f}%)",
                     (r['high_dot_pct'], r['high_strike_rate']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#fcf3cf', edgecolor='#f39c12', alpha=0.9))

    ax1.set_title("A. Batter Anomaly Map: Strike Rate vs Dot Ball %\n(Identifying All-or-Nothing Finishers vs Steady Anchors)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax1.set_xlabel("High-Pressure Dot Ball %", fontsize=10, fontweight='bold')
    ax1.set_ylabel("High-Pressure Strike Rate", fontsize=10, fontweight='bold')
    ax1.set_xlim(15, 75)
    ax1.set_ylim(40, 260)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=8.5, frameon=True)

    # 18.2 Bowler Anomaly Clusters (Economy vs Wicket Rate colored by Dot%)
    bo_plot = bo_rank[bo_rank['high_legal_balls'] >= 15].copy()
    bo_plot['wk_pct'] = (bo_plot['high_wickets'] / bo_plot['high_legal_balls']) * 100.0
    sc2 = ax2.scatter(bo_plot['high_economy_rate'], bo_plot['wk_pct'],
                      c=bo_plot['high_dot_pct'], cmap='viridis', s=bo_plot['high_legal_balls']*0.7,
                      edgecolors='black', linewidths=0.4, alpha=0.85)
    cbar2 = plt.colorbar(sc2, ax=ax2, pad=0.02)
    cbar2.set_label('Dot Ball % (High Pressure)', fontsize=9.5, fontweight='bold')

    ax2.axvline(10.0, color='#7f8c8d', linestyle=':', label='Expensive Cutoff (10.0 RPO)')
    ax2.axhline(6.21, color='#c0392b', linestyle='--', label='League Wk Prior (6.21%)')

    # Shaded Anomaly Region: Expensive Strike Bowlers (Top-Right)
    ax2.axvspan(10.0, 16.0, ymin=0.4, ymax=1.0, color='#fef9e7', alpha=0.35, label='Anomaly Zone: Expensive Strike')

    annot_bo = ['Jasprit Bumrah', 'Gerald Coetzee', 'Rashid Khan', 'Arshdeep Singh', 'Harshal Patel']
    for _, r in bo_plot[bo_plot['player_name'].isin(annot_bo)].iterrows():
        ax2.annotate(f"{r['player_name'].split()[-1]}\n(Econ {r['high_economy_rate']:.1f}, Wk {r['wk_pct']:.1f}%)",
                     (r['high_economy_rate'], r['wk_pct']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='#e8f8f5', edgecolor='#16a085', alpha=0.9))

    ax2.set_title("B. Bowler Anomaly Map: Economy Rate vs Breakthrough Wicket %\n(Contrasting Containment Shields like Bumrah vs Strike Weapons like Coetzee)", 
                  fontsize=11.5, fontweight='bold', pad=10)
    ax2.set_xlabel("High-Pressure Economy Rate (RPO)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("High-Pressure Breakthrough Wicket %", fontsize=10, fontweight='bold')
    ax2.set_xlim(4.0, 16.0)
    ax2.set_ylim(-1.0, 25.0)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=8.5, frameon=True)

    plt.suptitle("Multidimensional Outlier Detection & Anomaly Clustering\n"
                 "Revealing Statistical Inconsistencies and Role Trade-offs Across the Player Population",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "18_anomaly_multidimensional_clusters.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


# =========================================================================
# CHART 19: METHODOLOGY VULNERABILITIES SHOWCASE
# =========================================================================
def plot_methodology_vulnerabilities_showcase():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    
    # 19.1 Vulnerability 1: The Bumrah Paradox (Score Wk vs Score Econ)
    t1_bo = bo_rank[bo_rank['tier'] == 'Tier 1: Qualified'].copy()
    ax1.scatter(t1_bo['score_econ'], t1_bo['score_wk'], color='#bdc3c7', s=45, alpha=0.7)
    bumrah = t1_bo[t1_bo['player_name'] == 'Jasprit Bumrah'].iloc[0]
    ax1.scatter(bumrah['score_econ'], bumrah['score_wk'], color='#c0392b', s=160, edgecolors='black', linewidths=1.5, zorder=5)
    ax1.annotate("JASPRIT BUMRAH (#14)\nScore Econ: 79.7 (Elite!)\nScore Wk: 45.4 (Penalised!)",
                 (bumrah['score_econ'], bumrah['score_wk']),
                 textcoords="offset points", xytext=(-80, -35), fontsize=9, fontweight='bold', color='#c0392b',
                 bbox=dict(boxstyle='round,pad=0.25', facecolor='#fadbd8', edgecolor='#c0392b', alpha=0.95))
    ax1.axvline(50, color='#7f8c8d', linestyle=':', alpha=0.6)
    ax1.axhline(50, color='#7f8c8d', linestyle=':', alpha=0.6)
    ax1.set_title("Vulnerability 1: The Bumrah Paradox (Containment Penalty)\n"
                  "Batters play defensively -> 0 wickets -> Wk Score drops -> Rank slips to #14", 
                  fontsize=11, fontweight='bold', pad=10)
    ax1.set_xlabel("Economy Component Score (Score Econ)", fontsize=9.5, fontweight='bold')
    ax1.set_ylabel("Wicket Component Score (Score Wk)", fontsize=9.5, fontweight='bold')
    ax1.set_xlim(20, 100)
    ax1.set_ylim(20, 100)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 19.2 Vulnerability 2: The 60-Ball Hard Threshold Cliff (Jamie Overton Case)
    cliff_players = b_rank[(b_rank['high_balls_faced'] >= 45) & (b_rank['high_balls_faced'] <= 75)].sort_values('high_balls_faced')
    colors_cliff = ['#e67e22' if r['high_balls_faced'] < 60 else '#27ae60' for _, r in cliff_players.iterrows()]
    ax2.barh(cliff_players['player_name'], cliff_players['high_balls_faced'], color=colors_cliff, edgecolor='black', alpha=0.85)
    ax2.axvline(60, color='#c0392b', linestyle='--', linewidth=2, label='Binary Tier 1 Threshold (60 Balls)')
    
    # Highlight Overton
    ax2.annotate("JAMIE OVERTON (59 Balls)\nBRS = 79.54 (#1 if in Tier 1!)\nBarred from Tier 1 by 1 single ball!",
                 (59, 'Jamie Overton'),
                 textcoords="offset points", xytext=(-170, -10), fontsize=8.5, fontweight='bold', color='#c0392b',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='#fef9e7', edgecolor='#e67e22', alpha=0.95))
    ax2.set_title("Vulnerability 2: The 60-Ball Hard Boundary Cliff\n"
                  "Jamie Overton (59 Balls) has higher BRS than Klaasen (78.33), yet excluded from Tier 1", 
                  fontsize=11, fontweight='bold', pad=10)
    ax2.set_xlabel("High-Pressure Balls Faced", fontsize=9.5, fontweight='bold')
    ax2.set_xlim(35, 80)
    ax2.legend(loc='lower right', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # 19.3 Vulnerability 3: Sunil Narine Rank Collapse (-52 Places)
    narine_comps = ['Raw SR Rank\n(#15)', 'Score SR\n(75.5)', 'Score Surv\n(46.5)', 'Score Exec\n(39.8)', 'Score Diff\n(54.4)', 'Final BRS Rank\n(#85)']
    narine_vals = [15, 75.5, 46.5, 39.8, 54.4, 85]
    colors_n = ['#2980b9', '#27ae60', '#e74c3c', '#c0392b', '#f39c12', '#78281f']
    ax3.bar(narine_comps, narine_vals, color=colors_n, edgecolor='black', alpha=0.85, width=0.55)
    for i, v in enumerate(narine_vals):
        ax3.text(i, v + 2, f"{v:.1f}", ha='center', fontsize=9, fontweight='bold')
    ax3.set_title("Vulnerability 3: Sunil Narine's Rank Collapse (-52 Ranks)\n"
                  "Multi-component tension: Raw SR 174.2 crushed by high dismissals (12.9%) and dots (53.2%)", 
                  fontsize=11, fontweight='bold', pad=10)
    ax3.set_ylabel("Value / Score / Rank", fontsize=9.5, fontweight='bold')
    ax3.set_ylim(0, 100)
    ax3.grid(True, linestyle='--', alpha=0.5)

    # 19.4 Vulnerability 4: MS Dhoni Phase Pooling Inversion
    dhoni_phases = ['Powerplay\n(N=4 BF)', 'Middle Overs\n(N=28 BF)', 'Death Overs\n(N=53 BF)', 'Overall High-P\n(N=85 BF)']
    dhoni_sr = [75.0, 102.5, 222.0, 175.3] # High-P SR
    dhoni_ranks = ['N/A (<30)', 'Rank #86 (Middle)', 'Rank #2 (Death!)', 'Tier 1 Rank #25']
    bars4 = ax4.bar(dhoni_phases, dhoni_sr, color=['#95a5a6', '#3498db', '#e74c3c', '#f39c12'], edgecolor='black', width=0.55)
    for i, (bar, rk) in enumerate(zip(bars4, dhoni_ranks)):
        h = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, h + 5, f"SR: {h:.1f}\n{rk}", ha='center', fontsize=8.5, fontweight='bold')
    ax4.axhline(114.05, color='#7f8c8d', linestyle=':', label='League High-P Prior (114.05)')
    ax4.set_title("Vulnerability 4: MS Dhoni's Phase Pooling Dilution\n"
                  "Death-Overs Maestro (#2 in Death) diluted to #25 overall due to conservative Middle-Overs play", 
                  fontsize=11, fontweight='bold', pad=10)
    ax4.set_ylabel("High-Pressure Strike Rate", fontsize=9.5, fontweight='bold')
    ax4.set_ylim(0, 260)
    ax4.legend(loc='upper left', fontsize=8.5)
    ax4.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("Systemic Methodology Vulnerability Showcase: 4 Critical Edge Cases\n"
                 "Demonstrating How Mathematical Assumptions Influence Player Evaluations in Real-World Scenarios",
                 fontsize=13.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    out_file = OUT_DIR / "19_methodology_vulnerabilities_showcase.png"
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    generate_anomaly_csvs()
    plot_anomaly_multidimensional_clusters()
    plot_methodology_vulnerabilities_showcase()
    print("Completed EDA Module 07.")
