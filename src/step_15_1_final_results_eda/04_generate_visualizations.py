import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set consistent styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

batters = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv')
bowlers = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv')
b_comp = pd.read_csv('outputs/step_15_1_final_results_eda/original_vs_candidate_batting.csv')
bo_comp = pd.read_csv('outputs/step_15_1_final_results_eda/original_vs_candidate_bowling.csv')

t1_b = batters[batters['tier_exp13'] == 'Tier 1: Qualified'].sort_values('tier1_rank_exp13')
t1_bo = bowlers[bowlers['tier_exp13'] == 'Tier 1: Qualified'].sort_values('tier1_rank_exp13')

# -------------------------------------------------------------------------
# Figure 1: Score Distributions by Tier
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Batting
sns.boxplot(data=batters, x='tier_exp13', y='brs_3', ax=axes[0], palette='Blues', order=['Tier 1: Qualified', 'Tier 2: Specialist', 'Below Threshold'])
axes[0].set_title('Batting Score (BRS3) Distribution by Tier (N=816)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Qualification Tier (Rule B)', fontsize=11)
axes[0].set_ylabel('BRS3 Score', fontsize=11)
axes[0].set_ylim(0, 105)

# Bowler
sns.boxplot(data=bowlers, x='tier_exp13', y='bors', ax=axes[1], palette='Greens', order=['Tier 1: Qualified', 'Tier 2: Specialist', 'Below Threshold'])
axes[1].set_title('Bowling Score (BoRS) Distribution by Tier (N=589)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Qualification Tier (Rule B)', fontsize=11)
axes[1].set_ylabel('BoRS Score', fontsize=11)
axes[1].set_ylim(0, 105)

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/01_score_distributions_by_tier.png')
plt.close()
print("Saved 01_score_distributions_by_tier.png")

# -------------------------------------------------------------------------
# Figure 2: Rank vs Score and Gaps
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Batting Tier 1 Rank vs Score
axes[0].plot(t1_b['tier1_rank_exp13'], t1_b['brs_3'], marker='o', markersize=4, color='#1f77b4', linestyle='-', linewidth=1.5)
axes[0].axvline(10, color='red', linestyle='--', alpha=0.7, label='Top 10 Cutoff')
axes[0].axvline(20, color='orange', linestyle='--', alpha=0.7, label='Top 20 Cutoff')
# Annotate Dhoni
axes[0].annotate('MS Dhoni (93.21)\n[Gap to #2: 11.20 pts]', xy=(1, 93.21), xytext=(8, 90),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6), fontsize=9, fontweight='bold')
# Annotate Overton
axes[0].annotate('Jamie Overton (#7, 78.19)', xy=(7, 78.19), xytext=(12, 82),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6), fontsize=9)
axes[0].set_title('Tier 1 Batting: Rank vs BRS3 Score (N=146)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Tier 1 Rank', fontsize=11)
axes[0].set_ylabel('BRS3 Score', fontsize=11)
axes[0].legend(loc='lower left')

# Bowling Tier 1 Rank vs Score
axes[1].plot(t1_bo['tier1_rank_exp13'], t1_bo['bors'], marker='s', markersize=4, color='#2ca02c', linestyle='-', linewidth=1.5)
axes[1].axvline(10, color='red', linestyle='--', alpha=0.7, label='Top 10 Cutoff')
axes[1].axvline(20, color='orange', linestyle='--', alpha=0.7, label='Top 20 Cutoff')
axes[1].annotate('Tim Southee (#1, 90.69)\nNasum Ahmed (#2, 88.84)\n[Gap to #3: 8.90 pts]', xy=(1, 90.69), xytext=(10, 88),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6), fontsize=9, fontweight='bold')
axes[1].set_title('Tier 1 Bowling: Rank vs BoRS Score (N=130)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Tier 1 Rank', fontsize=11)
axes[1].set_ylabel('BoRS Score', fontsize=11)
axes[1].legend(loc='lower left')

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/02_rank_vs_score_and_gaps.png')
plt.close()
print("Saved 02_rank_vs_score_and_gaps.png")

# -------------------------------------------------------------------------
# Figure 3: Sample Size vs Score
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

sns.scatterplot(data=batters, x='high_balls_faced', y='brs_3', hue='tier_exp13', palette='tab10', alpha=0.7, ax=axes[0])
axes[0].axvline(60, color='grey', linestyle=':', label='N=60 (Baseline)')
axes[0].axvline(50, color='blue', linestyle=':', label='N=50 (Rule B Breadth)')
axes[0].axvline(40, color='purple', linestyle=':', label='N=40 (Tier 2 Floor)')
axes[0].set_title('Batting: High Pressure Balls Faced vs BRS3 (N=816)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('High Pressure Balls Faced (PI > 60.0)', fontsize=11)
axes[0].set_ylabel('BRS3 Score', fontsize=11)
axes[0].legend(loc='upper right', fontsize=8)

sns.scatterplot(data=bowlers, x='high_legal_balls', y='bors', hue='tier_exp13', palette='tab10', alpha=0.7, ax=axes[1])
axes[1].axvline(60, color='grey', linestyle=':', label='N=60 (Baseline)')
axes[1].axvline(50, color='blue', linestyle=':', label='N=50 (Rule B Breadth)')
axes[1].axvline(40, color='purple', linestyle=':', label='N=40 (Tier 2 Floor)')
axes[1].set_title('Bowling: High Pressure Legal Balls vs BoRS (N=589)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('High Pressure Legal Balls (PI > 60.0)', fontsize=11)
axes[1].set_ylabel('BoRS Score', fontsize=11)
axes[1].legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/03_sample_size_vs_score.png')
plt.close()
print("Saved 03_sample_size_vs_score.png")

# -------------------------------------------------------------------------
# Figure 4: Rule B Qualification Pathways (N vs M)
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Batters
sns.scatterplot(data=batters, x='high_balls_faced', y='hp_matches', hue='tier_exp13', palette='tab10', alpha=0.7, ax=axes[0])
axes[0].axvline(60, color='black', linestyle='--', alpha=0.5)
axes[0].axhline(6, color='black', linestyle='--', alpha=0.5)
axes[0].axvline(50, color='blue', linestyle=':', alpha=0.5)
# Highlight Jamie Overton
axes[0].scatter([59], [14], color='red', s=80, zorder=5, label='Jamie Overton (N=59, M=14)')
axes[0].set_title('Batting: High Balls vs Matches (Rule B Pathways)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('High Pressure Balls Faced', fontsize=11)
axes[0].set_ylabel('High Pressure Matches', fontsize=11)
axes[0].legend(loc='lower right', fontsize=8)

# Bowlers
sns.scatterplot(data=bowlers, x='high_legal_balls', y='hp_matches', hue='tier_exp13', palette='tab10', alpha=0.7, ax=axes[1])
axes[1].axvline(60, color='black', linestyle='--', alpha=0.5)
axes[1].axhline(6, color='black', linestyle='--', alpha=0.5)
axes[1].axvline(50, color='blue', linestyle=':', alpha=0.5)
# Highlight Nasum Ahmed & Junaid Siddique
axes[1].scatter([55], [10], color='red', s=80, zorder=5, label='Nasum Ahmed (N=55, M=10)')
axes[1].scatter([50], [12], color='purple', s=80, zorder=5, label='Junaid Siddique (N=50, M=12)')
axes[1].set_title('Bowling: High Legal Balls vs Matches (Rule B Pathways)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('High Pressure Legal Balls', fontsize=11)
axes[1].set_ylabel('High Pressure Matches', fontsize=11)
axes[1].legend(loc='lower right', fontsize=8)

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/04_rule_b_qualification_pathways.png')
plt.close()
print("Saved 04_rule_b_qualification_pathways.png")

# -------------------------------------------------------------------------
# Figure 5: Component Correlations Heatmap
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

b_corr = t1_b[['score_sr', 'score_surv', 'score_diff', 'brs_3']].rename(columns={
    'score_sr': 'Score_SR (45%)',
    'score_surv': 'Score_Surv (35%)',
    'score_diff': 'Score_Diff (20%)',
    'brs_3': 'Final BRS3'
}).corr()

sns.heatmap(b_corr, annot=True, fmt='.2f', cmap='Blues', vmin=-0.2, vmax=1.0, ax=axes[0], cbar=False)
axes[0].set_title('Batting Component Correlations (Tier 1, N=146)', fontsize=12, fontweight='bold')

bo_corr = t1_bo[['score_econ', 'score_wk', 'score_dot', 'score_diff', 'bors']].rename(columns={
    'score_econ': 'Score_Econ (40%)',
    'score_wk': 'Score_Wk (25%)',
    'score_dot': 'Score_Dot (20%)',
    'score_diff': 'Score_Diff (15%)',
    'bors': 'Final BoRS'
}).corr()

sns.heatmap(bo_corr, annot=True, fmt='.2f', cmap='Greens', vmin=-0.2, vmax=1.0, ax=axes[1], cbar=False)
axes[1].set_title('Bowling Component Correlations (Tier 1, N=130)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/05_component_correlations_and_weights.png')
plt.close()
print("Saved 05_component_correlations_and_weights.png")

# -------------------------------------------------------------------------
# Figure 6: Top 20 Batters Component Breakdown
# -------------------------------------------------------------------------
top20_b = t1_b.head(20).sort_values('tier1_rank_exp13', ascending=False)
fig, ax = plt.subplots(figsize=(12, 8))

y_pos = np.arange(len(top20_b))
c_sr = top20_b['score_sr'] * 0.45
c_surv = top20_b['score_surv'] * 0.35
c_diff = top20_b['score_diff'] * 0.20

ax.barh(y_pos, c_sr, color='#1f77b4', label='Strike Rate Contribution (45%)')
ax.barh(y_pos, c_surv, left=c_sr, color='#2ca02c', label='Survival Contribution (35%)')
ax.barh(y_pos, c_diff, left=c_sr+c_surv, color='#ff7f0e', label='Clutch Diff Contribution (20%)')

labels = [f"#{int(r['tier1_rank_exp13'])} {r['player_name']} ({r['brs_3']:.1f})" for _, r in top20_b.iterrows()]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=9)
ax.set_xlabel('BRS3 Composite Score', fontsize=11)
ax.set_title('Top 20 Tier 1 Batters: Component Score Composition', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=9)
ax.set_xlim(0, 100)

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/06_top20_batters_breakdown.png')
plt.close()
print("Saved 06_top20_batters_breakdown.png")

# -------------------------------------------------------------------------
# Figure 7: Top 20 Bowlers Component Breakdown
# -------------------------------------------------------------------------
top20_bo = t1_bo.head(20).sort_values('tier1_rank_exp13', ascending=False)
fig, ax = plt.subplots(figsize=(12, 8))

y_pos_bo = np.arange(len(top20_bo))
c_econ = top20_bo['score_econ'] * 0.40
c_wk = top20_bo['score_wk'] * 0.25
c_dot = top20_bo['score_dot'] * 0.20
c_diff_bo = top20_bo['score_diff'] * 0.15

ax.barh(y_pos_bo, c_econ, color='#2ca02c', label='Economy (40%)')
ax.barh(y_pos_bo, c_wk, left=c_econ, color='#d62728', label='Wicket Rate (25%)')
ax.barh(y_pos_bo, c_dot, left=c_econ+c_wk, color='#1f77b4', label='Dot-Ball Rate (20%)')
ax.barh(y_pos_bo, c_diff_bo, left=c_econ+c_wk+c_dot, color='#9467bd', label='Clutch Diff (15%)')

labels_bo = [f"#{int(r['tier1_rank_exp13'])} {r['player_name']} ({r['bors']:.1f})" for _, r in top20_bo.iterrows()]
ax.set_yticks(y_pos_bo)
ax.set_yticklabels(labels_bo, fontsize=9)
ax.set_xlabel('BoRS Composite Score', fontsize=11)
ax.set_title('Top 20 Tier 1 Bowlers: Component Score Composition', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=9)
ax.set_xlim(0, 100)

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/07_top20_bowlers_breakdown.png')
plt.close()
print("Saved 07_top20_bowlers_breakdown.png")

# -------------------------------------------------------------------------
# Figure 8: Phase Exposure for Top 20 Batters & Bowlers
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# Batters Phase Breakdown
top20_b_fwd = t1_b.head(20).sort_values('tier1_rank_exp13', ascending=False)
p_pp_b = top20_b_fwd['bf_pp_high'] / top20_b_fwd['high_balls_faced'] * 100
p_mo_b = top20_b_fwd['bf_mo_high'] / top20_b_fwd['high_balls_faced'] * 100
p_do_b = top20_b_fwd['bf_do_high'] / top20_b_fwd['high_balls_faced'] * 100

y_b = np.arange(len(top20_b_fwd))
axes[0].barh(y_b, p_pp_b, color='#3498db', label='Powerplay (1-6)')
axes[0].barh(y_b, p_mo_b, left=p_pp_b, color='#f1c40f', label='Middle (7-15)')
axes[0].barh(y_b, p_do_b, left=p_pp_b+p_mo_b, color='#e74c3c', label='Death (16-20)')
axes[0].set_yticks(y_b)
axes[0].set_yticklabels([f"#{int(r['tier1_rank_exp13'])} {r['player_name']}" for _, r in top20_b_fwd.iterrows()], fontsize=8)
axes[0].set_title('Top 20 Batters: High-Pressure Phase Exposure (%)', fontsize=11, fontweight='bold')
axes[0].set_xlabel('% of High Pressure Deliveries Faced', fontsize=10)
axes[0].legend(loc='lower right', fontsize=8)
axes[0].set_xlim(0, 100)

# Bowlers Phase Breakdown
top20_bo_fwd = t1_bo.head(20).sort_values('tier1_rank_exp13', ascending=False)
p_pp_bo = top20_bo_fwd['lb_pp_high'] / top20_bo_fwd['high_legal_balls'] * 100
p_mo_bo = top20_bo_fwd['lb_mo_high'] / top20_bo_fwd['high_legal_balls'] * 100
p_do_bo = top20_bo_fwd['lb_do_high'] / top20_bo_fwd['high_legal_balls'] * 100

y_bo = np.arange(len(top20_bo_fwd))
axes[1].barh(y_bo, p_pp_bo, color='#3498db', label='Powerplay (1-6)')
axes[1].barh(y_bo, p_mo_bo, left=p_pp_bo, color='#f1c40f', label='Middle (7-15)')
axes[1].barh(y_bo, p_do_bo, left=p_pp_bo+p_mo_bo, color='#e74c3c', label='Death (16-20)')
axes[1].set_yticks(y_bo)
axes[1].set_yticklabels([f"#{int(r['tier1_rank_exp13'])} {r['player_name']}" for _, r in top20_bo_fwd.iterrows()], fontsize=8)
axes[1].set_title('Top 20 Bowlers: High-Pressure Phase Exposure (%)', fontsize=11, fontweight='bold')
axes[1].set_xlabel('% of High Pressure Legal Balls Bowled', fontsize=10)
axes[1].legend(loc='lower right', fontsize=8)
axes[1].set_xlim(0, 100)

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/08_phase_exposure_and_death_bias.png')
plt.close()
print("Saved 08_phase_exposure_and_death_bias.png")

# -------------------------------------------------------------------------
# Figure 9: Original v2.0 vs Candidate Rank Transitions
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Batters
axes[0].scatter(b_comp['overall_rank_official'], b_comp['overall_rank_exp13'], alpha=0.5, color='#1f77b4', s=20)
axes[0].plot([1, 816], [1, 816], color='red', linestyle='--', label='1:1 Line (No Change)')
axes[0].set_title('Batting: Official v2.0 vs Candidate Overall Rank (N=816)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Official v2.0 Overall Rank', fontsize=11)
axes[0].set_ylabel('Candidate Step 13 Overall Rank', fontsize=11)
axes[0].legend(loc='upper left')

# Bowlers
axes[1].scatter(bo_comp['overall_rank_official'], bo_comp['overall_rank_exp13'], alpha=0.5, color='#2ca02c', s=20)
axes[1].plot([1, 589], [1, 589], color='red', linestyle='--', label='1:1 Line (Formula Identical)')
axes[1].set_title('Bowling: Official v2.0 vs Candidate Overall Rank (N=589)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Official v2.0 Overall Rank', fontsize=11)
axes[1].set_ylabel('Candidate Step 13 Overall Rank', fontsize=11)
axes[1].legend(loc='upper left')

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/09_original_v2_vs_candidate_transitions.png')
plt.close()
print("Saved 09_original_v2_vs_candidate_transitions.png")

# -------------------------------------------------------------------------
# Figure 10: Clutch Regime Deltas and Outliers
# -------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Batting SR Low vs High
axes[0].scatter(t1_b['low_mod_strike_rate'], t1_b['high_strike_rate'], color='#1f77b4', alpha=0.6, s=35)
axes[0].plot([80, 200], [80, 200], color='red', linestyle='--', label='Zero Delta (High SR = Low SR)')
# Annotate extreme delta
axes[0].annotate('Jamie Overton (+50.95 delta)', xy=(120.2, 171.2), xytext=(90, 185),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5), fontsize=8, fontweight='bold')
axes[0].annotate('MS Dhoni (+36.0 delta)', xy=(135.0, 171.0), xytext=(145, 180),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5), fontsize=8, fontweight='bold')
axes[0].set_title('Tier 1 Batters: Low/Mod SR vs High-Pressure SR', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Observed Strike Rate (Low/Mod Pressure: PI <= 60)', fontsize=11)
axes[0].set_ylabel('Observed Strike Rate (High Pressure: PI > 60)', fontsize=11)
axes[0].legend(loc='lower right')

# Bowling Economy Low vs High
axes[1].scatter(t1_bo['low_mod_economy_rate'], t1_bo['high_economy_rate'], color='#2ca02c', alpha=0.6, s=35)
axes[1].plot([5, 12], [5, 12], color='red', linestyle='--', label='Zero Delta (High Econ = Low Econ)')
axes[1].annotate('Tim Southee (+3.87 economy gain under pressure)', xy=(10.7, 6.8), xytext=(8.0, 5.5),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5), fontsize=8, fontweight='bold')
axes[1].annotate('Nasum Ahmed (+2.53 economy gain)', xy=(8.4, 5.9), xytext=(6.0, 7.5),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5), fontsize=8, fontweight='bold')
axes[1].set_title('Tier 1 Bowlers: Low/Mod Econ vs High-Pressure Econ', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Observed Economy (Low/Mod Pressure: PI <= 60)', fontsize=11)
axes[1].set_ylabel('Observed Economy (High Pressure: PI > 60)', fontsize=11)
axes[1].legend(loc='lower right')

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/10_clutch_regime_deltas_and_outliers.png')
plt.close()
print("Saved 10_clutch_regime_deltas_and_outliers.png")

# -------------------------------------------------------------------------
# Figure 11: All-Rounder Dual Profile Matrix
# -------------------------------------------------------------------------
all_rounders = [
    (8, 'MS Dhoni'),
    (4755, 'Shivam Dube'),
    (2756, 'Shashank Singh'),
    (5939, 'Cameron Green'),
    (25139, 'Shubham Dubey'),
    (2877, 'Vijay Shankar'),
    (2382, 'Jamie Overton'),
    (4708, 'Rinku Singh'),
    (1101, 'George Dockrell'),
    (3916, 'Jitesh Sharma'),
    (4900, 'Wanindu Hasaranga'),
    (5379, 'Mark Adair')
]

ar_rows = []
for pid, name in all_rounders:
    b_r = batters[batters['player_id'] == pid]
    bo_r = bowlers[bowlers['player_id'] == pid]
    b_s = b_r['brs_3'].values[0] if len(b_r) else 0
    bo_s = bo_r['bors'].values[0] if len(bo_r) else 0
    b_t = b_r['tier_exp13'].values[0] if len(b_r) else 'None'
    bo_t = bo_r['tier_exp13'].values[0] if len(bo_r) else 'None'
    ar_rows.append({'name': name, 'brs_3': b_s, 'bors': bo_s, 'bat_tier': b_t, 'bowl_tier': bo_t})

ar_df = pd.DataFrame(ar_rows)

fig, ax = plt.subplots(figsize=(10, 7))
sns.scatterplot(data=ar_df, x='brs_3', y='bors', s=120, color='darkorange', ax=ax)
for _, r in ar_df.iterrows():
    ax.annotate(r['name'], xy=(r['brs_3'], r['bors']), xytext=(r['brs_3']+0.8, r['bors']+0.8), fontsize=9, fontweight='bold')

ax.axvline(50, color='grey', linestyle=':', alpha=0.5)
ax.axhline(50, color='grey', linestyle=':', alpha=0.5)
ax.set_title('All-Rounder & Key Player Dual Profile Matrix (BRS3 vs BoRS)', fontsize=12, fontweight='bold')
ax.set_xlabel('Batting Reliability Score (BRS3)', fontsize=11)
ax.set_ylabel('Bowling Reliability Score (BoRS)', fontsize=11)
ax.set_xlim(25, 100)
ax.set_ylim(25, 95)

plt.tight_layout()
plt.savefig('outputs/step_15_1_final_results_eda/11_all_rounder_dual_profile_matrix.png')
plt.close()
print("Saved 11_all_rounder_dual_profile_matrix.png")
