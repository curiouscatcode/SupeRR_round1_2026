import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Ensure output directories exist
out_dir = "outputs/step_8_eda/big_name_player_analysis"
fig_dir = os.path.join(out_dir, "figures")
os.makedirs(fig_dir, exist_ok=True)

# -------------------------------------------------------------
# 1. LOAD FROZEN DATASETS
# -------------------------------------------------------------
bat_elig = pd.read_csv("outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv")
bowl_elig = pd.read_csv("outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv")

bat_boot = pd.read_csv("outputs/step_7_empirical_calibration/step_7_4_final_rankings/bootstrap_uncertainty_batting.csv")
bowl_boot = pd.read_csv("outputs/step_7_empirical_calibration/step_7_4_final_rankings/bootstrap_uncertainty_bowling.csv")

bat_del = pd.read_parquet("outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet")
bowl_del = pd.read_parquet("outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet")

# Merge bootstrap rank CIs with eligible player tables
bat_merged = bat_elig.merge(
    bat_boot[['player_name', 'rank_median', 'rank_ci_lower', 'rank_ci_upper']],
    left_on='Player', right_on='player_name', how='left'
).drop(columns=['player_name'])

bowl_merged = bowl_elig.merge(
    bowl_boot[['player_name', 'rank_median', 'rank_ci_lower', 'rank_ci_upper']],
    left_on='Player', right_on='player_name', how='left'
).drop(columns=['player_name'])

# -------------------------------------------------------------
# 2. DEFINE REQUESTED PLAYER MAPPINGS
# -------------------------------------------------------------
# Batters to investigate
requested_batters_map = {
    'Shubman Gill': 'Shubman Gill',
    'Rohit Sharma': 'Rohit Sharma',
    'Shreyas Iyer': 'Shreyas Iyer',
    'Virat Kohli': 'Virat Kohli',
    'Devdutt Padikkal': 'Devdutt Padikkal',
    'Rishabh Pant': 'Rishabh Pant',
    'Mitchell Marsh': 'Mitchell Marsh',
    'Babar Azam': 'Babar Azam',
    'Mohammad Rizwan': 'Mohammad Rizwan',
    'Sanju Samson': 'Sanju Samson',
    'KL Rahul': 'Lokesh Rahul',
    'Hardik Pandya': 'Hardik Pandya',
    'Ravindra Jadeja': 'Ravindra Jadeja',
    'Pathum Nissanka': 'Pathum Nissanka',
    'Jos Buttler': 'Jos Buttler',
    'Harry Brook': 'Harry Brook',
    'Sam Curran': 'Sam Curran'
}

# Bowlers to investigate
requested_bowlers_map = {
    'Kagiso Rabada': 'Kagiso Rabada',
    'Mitchell Starc': 'Mitchell Starc',
    'Shaheen Shah Afridi': 'Shaheen Afridi',
    'Trent Boult': 'Trent Boult',
    'Mohammed Siraj': 'Mohammed Siraj',
    'Mohammed Shami': 'Mohammed Shami',
    'Arshdeep Singh': 'Arshdeep Singh',
    'Axar Patel': 'Axar Patel',
    'Ravindra Jadeja': 'Ravindra Jadeja',
    'Sam Curran': 'Sam Curran',
    'Mitchell Santner': 'Mitchell Santner'
}

# -------------------------------------------------------------
# 3. BUILD BIG-NAME LEADERBOARDS
# -------------------------------------------------------------
bat_records = []
for display_name, dataset_name in requested_batters_map.items():
    match = bat_merged[bat_merged['Player'] == dataset_name]
    if len(match) > 0:
        r = match.iloc[0]
        bat_records.append({
            'Requested Name': display_name,
            'Dataset Name': dataset_name,
            'Overall Rank': int(r['Rank']),
            'Shrunk PWSVA': float(r['Shrunk score']),
            'Raw PWSVA': float(r['Raw score']),
            'Balls Faced': int(r['Raw opportunities']),
            'Kish ESS': float(r['Kish ESS']),
            'Pressure Opps (P>=50)': int(r['Pressure opportunities']),
            'Bootstrap SE': float(r['Bootstrap SE']),
            '95% Score CI': str(r['95% CI']),
            'Median Bootstrap Rank': float(r['rank_median']),
            '95% Rank CI': f"[{int(r['rank_ci_lower'])}, {int(r['rank_ci_upper'])}]",
            'Alpha 1.25 Rank': int(r['Alpha 1.25 rank']),
            'Team / Format': str(r['Team/format'])
        })

df_bigname_bat = pd.DataFrame(bat_records).sort_values(by='Overall Rank').reset_index(drop=True)
df_bigname_bat.to_csv(os.path.join(out_dir, "big_name_batting_leaderboard.csv"), index=False)
print(f"Generated big_name_batting_leaderboard.csv ({len(df_bigname_bat)} players)")

bowl_records = []
for display_name, dataset_name in requested_bowlers_map.items():
    match = bowl_merged[bowl_merged['Player'] == dataset_name]
    if len(match) > 0:
        r = match.iloc[0]
        bowl_records.append({
            'Requested Name': display_name,
            'Dataset Name': dataset_name,
            'Overall Rank': int(r['Rank']),
            'Shrunk SBVA': float(r['Shrunk score']),
            'Raw SBVA': float(r['Raw score']),
            'Legal Balls': int(r['Raw opportunities']),
            'Kish ESS': float(r['Kish ESS']),
            'Pressure Opps (P>=50)': int(r['Pressure opportunities']),
            'Bootstrap SE': float(r['Bootstrap SE']),
            '95% Score CI': str(r['95% CI']),
            'Median Bootstrap Rank': float(r['rank_median']),
            '95% Rank CI': f"[{int(r['rank_ci_lower'])}, {int(r['rank_ci_upper'])}]",
            'Alpha 1.25 Rank': int(r['Alpha 1.25 rank']),
            'Team / Format': str(r['Team/format'])
        })

df_bigname_bowl = pd.DataFrame(bowl_records).sort_values(by='Overall Rank').reset_index(drop=True)
df_bigname_bowl.to_csv(os.path.join(out_dir, "big_name_bowling_leaderboard.csv"), index=False)
print(f"Generated big_name_bowling_leaderboard.csv ({len(df_bigname_bowl)} players)")

# -------------------------------------------------------------
# 4. UNQUALIFIED OR MISSING PLAYERS CATALOG
# -------------------------------------------------------------
unqualified_list = [
    {
        'Player Name': 'Ben Stokes',
        'Status': 'Unqualified in both disciplines',
        'Reason': 'Failed qualification threshold N(P>=50) >= 50 in both batting and bowling.',
        'Batting Balls Faced': 34,
        'Batting P>=50 Opps': 12,
        'Bowling Legal Balls': 30,
        'Bowling P>=50 Opps': 24,
        'Dataset Presence': 'Present in 2021-2024 tracking data, but limited appearances due to injuries/workload'
    },
    {
        'Player Name': 'Steve Smith',
        'Status': 'Completely Absent from Dataset',
        'Reason': 'Zero deliveries faced or bowled in the competition dataset period (2021-2024 IPL & select T20I matches).',
        'Batting Balls Faced': 0,
        'Batting P>=50 Opps': 0,
        'Bowling Legal Balls': 0,
        'Bowling P>=50 Opps': 0,
        'Dataset Presence': 'Absent (did not play eligible T20 tournament matches in window)'
    },
    {
        'Player Name': 'Shan Masood',
        'Status': 'Unqualified in Batting (Agonizing Near-Miss)',
        'Reason': 'Accumulated 176 balls faced, but only 47 were at P>=50 (missed qualification threshold by exactly 3 balls).',
        'Batting Balls Faced': 176,
        'Batting P>=50 Opps': 47,
        'Bowling Legal Balls': 0,
        'Bowling P>=50 Opps': 0,
        'Dataset Presence': 'Present in Pakistan T20I matches'
    },
    {
        'Player Name': 'Kieron Pollard',
        'Status': 'Unqualified in Bowling (Near-Miss)',
        'Reason': 'Bowled 185 legal balls, but only 45 were at P>=50 (missed bowling qualification by exactly 5 balls). Retired from IPL after 2022.',
        'Batting Balls Faced': 622,
        'Batting P>=50 Opps': 275, # Note: Pollard qualified in batting! Rank 144
        'Bowling Legal Balls': 185,
        'Bowling P>=50 Opps': 45,
        'Dataset Presence': 'Qualified as Batter (#144); Unqualified as Bowler'
    },
    {
        'Player Name': 'Alzarri Joseph',
        'Status': 'Unqualified in Batting (Near-Miss)',
        'Reason': 'Faced 130 balls, but exactly 49 were at P>=50 (missed batting qualification by 1 ball). Qualified in bowling (Rank 135).',
        'Batting Balls Faced': 130,
        'Batting P>=50 Opps': 49,
        'Bowling Legal Balls': 1361,
        'Bowling P>=50 Opps': 704,
        'Dataset Presence': 'Qualified as Bowler (#135); Unqualified as Batter'
    },
    {
        'Player Name': 'Rishi Dhawan',
        'Status': 'Unqualified in Bowling (Near-Miss)',
        'Reason': 'Bowled 168 legal balls, but exactly 49 were at P>=50 (missed bowling qualification by 1 ball).',
        'Batting Balls Faced': 122,
        'Batting P>=50 Opps': 55, # Qualified in batting! Rank 223
        'Bowling Legal Balls': 168,
        'Bowling P>=50 Opps': 49,
        'Dataset Presence': 'Qualified as Batter (#223); Unqualified as Bowler'
    },
    {
        'Player Name': 'Mosaddek Hossain',
        'Status': 'Unqualified in Batting (Near-Miss)',
        'Reason': 'Faced 113 balls, with 47 at P>=50 (missed batting qualification by 3 balls). Highly prominent in bowling (Rank 11).',
        'Batting Balls Faced': 113,
        'Batting P>=50 Opps': 47,
        'Bowling Legal Balls': 159,
        'Bowling P>=50 Opps': 50,
        'Dataset Presence': 'Qualified as Bowler (#11); Unqualified as Batter'
    },
    {
        'Player Name': 'Haris Rauf',
        'Status': 'Unqualified in Batting',
        'Reason': 'Tailender batter: faced 103 balls, 38 at P>=50. Qualified in bowling (Rank 107).',
        'Batting Balls Faced': 103,
        'Batting P>=50 Opps': 38,
        'Bowling Legal Balls': 1483,
        'Bowling P>=50 Opps': 770,
        'Dataset Presence': 'Qualified as Bowler (#107); Unqualified as Batter'
    },
    {
        'Player Name': 'Gerald Coetzee',
        'Status': 'Unqualified in Batting',
        'Reason': 'Faced 97 balls, 40 at P>=50. Qualified in bowling (Rank 220).',
        'Batting Balls Faced': 97,
        'Batting P>=50 Opps': 40,
        'Bowling Legal Balls': 616,
        'Bowling P>=50 Opps': 328,
        'Dataset Presence': 'Qualified as Bowler (#220); Unqualified as Batter'
    },
    {
        'Player Name': 'Rachin Ravindra',
        'Status': 'Unqualified in Bowling',
        'Reason': 'Part-time bowler: bowled 132 legal balls, only 19 at P>=50. Qualified in batting (Rank 133).',
        'Batting Balls Faced': 585,
        'Batting P>=50 Opps': 267,
        'Bowling Legal Balls': 132,
        'Bowling P>=50 Opps': 19,
        'Dataset Presence': 'Qualified as Batter (#133); Unqualified as Bowler'
    },
    {
        'Player Name': 'Glenn Phillips',
        'Status': 'Unqualified in Bowling',
        'Reason': 'Part-time bowler: bowled 111 legal balls, 37 at P>=50. Qualified in batting (Rank 24).',
        'Batting Balls Faced': 1051,
        'Batting P>=50 Opps': 329,
        'Bowling Legal Balls': 111,
        'Bowling P>=50 Opps': 37,
        'Dataset Presence': 'Qualified as Batter (#24); Unqualified as Bowler'
    }
]
df_unqualified = pd.DataFrame(unqualified_list)
df_unqualified.to_csv(os.path.join(out_dir, "unqualified_or_missing_players.csv"), index=False)
print(f"Generated unqualified_or_missing_players.csv ({len(df_unqualified)} players)")

# -------------------------------------------------------------
# 5. ADDITIONAL PROMINENT PLAYERS CATALOG
# -------------------------------------------------------------
additional_names = [
    ('Mahendra Singh Dhoni', 'Batting', 93, 'Wicketkeeper Finisher'),
    ('David Warner', 'Batting', 40, 'Top-Order Anchor'),
    ('Kane Williamson', 'Batting', 286, 'Accumulator / Anchor'),
    ('Patrick Cummins', 'Batting', 77, 'Lower-Order Finisher'),
    ('Patrick Cummins', 'Bowling', 175, 'Pace Enforcer / Captain'),
    ('Faf du Plessis', 'Batting', 114, 'Top-Order Explosive Batter'),
    ('Glenn Maxwell', 'Batting', 46, 'Middle-Overs Aggressor'),
    ('Glenn Maxwell', 'Bowling', 121, 'Off-Spin Containment'),
    ('Andre Russell', 'Batting', 9, 'Clutch Death Finisher (Top 10)'),
    ('Andre Russell', 'Bowling', 270, 'Death Yorker / Heavy Ball'),
    ('Sunil Narine', 'Batting', 275, 'Pinch-Hitter / Opener'),
    ('Sunil Narine', 'Bowling', 3, 'Choke Spin Benchmark (Top 10)'),
    ('Dinesh Karthik', 'Batting', 13, 'Death Finisher Specialist'),
    ('Shikhar Dhawan', 'Batting', 243, 'Top-Order Anchor'),
    ('Jonny Bairstow', 'Batting', 43, 'Powerplay Destroyer'),
    ('Moeen Ali', 'Batting', 141, 'Floating All-Rounder'),
    ('Moeen Ali', 'Bowling', 48, 'Off-Spin Choke'),
    ('Marcus Stoinis', 'Batting', 73, 'Finisher / Anchor'),
    ('Marcus Stoinis', 'Bowling', 241, 'Medium-Pace Seamer'),
    ('Quinton de Kock', 'Batting', 184, 'Wicketkeeper Opener'),
    ('David Miller', 'Batting', 78, 'Middle-Order Finisher'),
    ('Nicholas Pooran', 'Batting', 22, 'Aggressive Middle Finisher'),
    ('Shimron Hetmyer', 'Batting', 65, 'Middle-Order Slugger'),
    ('Rinku Singh', 'Batting', 25, 'Clutch Death Chase Finisher'),
    ('Shivam Dube', 'Batting', 39, 'Middle-Overs Spin Destroyer'),
    ('Shivam Dube', 'Bowling', 273, 'Medium-Pace Seamer'),
    ('Yuzvendra Chahal', 'Bowling', 120, 'Attacking Leg-Spinner'),
    ('Harshal Patel', 'Bowling', 237, 'Death Yorker / Slower Ball Specialist'),
    ('Anrich Nortje', 'Bowling', 289, 'Express Pace Enforcer'),
    ('Lockie Ferguson', 'Bowling', 110, 'Express Pace Seamer'),
    ('Adam Zampa', 'Bowling', 101, 'Attacking Leg-Spinner'),
    ('Tabraiz Shamsi', 'Bowling', 274, 'Wrist-Spin Specialist'),
    ('Ishant Sharma', 'Bowling', 116, 'Powerplay Hit-the-Deck Pacer'),
    ('Deepak Chahar', 'Bowling', 64, 'Powerplay Swing Specialist'),
    ('Shardul Thakur', 'Batting', 283, 'Lower-Order Pinch Hitter'),
    ('Shardul Thakur', 'Bowling', 288, 'Partnership-Breaker Seamer'),
    ('Washington Sundar', 'Batting', 60, 'Middle-Order Anchor'),
    ('Washington Sundar', 'Bowling', 108, 'Powerplay Off-Spinner')
]

add_records = []
for p_name, role_cat, rnk, archetype in additional_names:
    if role_cat == 'Batting':
        m = bat_merged[bat_merged['Player'] == p_name]
        if len(m) > 0:
            row = m.iloc[0]
            add_records.append({
                'Player Name': p_name,
                'Discipline': 'Batting',
                'Overall Rank': int(row['Rank']),
                'Shrunk Score': float(row['Shrunk score']),
                'Raw Score': float(row['Raw score']),
                'Opportunities': int(row['Raw opportunities']),
                'Kish ESS': float(row['Kish ESS']),
                'Pressure Opps (P>=50)': int(row['Pressure opportunities']),
                '95% CI': str(row['95% CI']),
                'Archetype / Tactical Role': archetype,
                'Team / Format': str(row['Team/format'])
            })
    else:
        m = bowl_merged[bowl_merged['Player'] == p_name]
        if len(m) > 0:
            row = m.iloc[0]
            add_records.append({
                'Player Name': p_name,
                'Discipline': 'Bowling',
                'Overall Rank': int(row['Rank']),
                'Shrunk Score': float(row['Shrunk score']),
                'Raw Score': float(row['Raw score']),
                'Opportunities': int(row['Raw opportunities']),
                'Kish ESS': float(row['Kish ESS']),
                'Pressure Opps (P>=50)': int(row['Pressure opportunities']),
                '95% CI': str(row['95% CI']),
                'Archetype / Tactical Role': archetype,
                'Team / Format': str(row['Team/format'])
            })

df_additional = pd.DataFrame(add_records).sort_values(by=['Discipline', 'Overall Rank']).reset_index(drop=True)
df_additional.to_csv(os.path.join(out_dir, "additional_prominent_players.csv"), index=False)
print(f"Generated additional_prominent_players.csv ({len(df_additional)} records)")

# -------------------------------------------------------------
# 6. VISUALIZATIONS GENERATION (300 DPI)
# -------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

# -------------------------------------------------------------
# FIG 1: FULL POPULATION BATTING RANKS (297 BATTERS)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
ranks = bat_merged['Rank'].values
scores = bat_merged['Shrunk score'].values

# Neutral scatter for all batters
ax.scatter(ranks, scores, color='#cbd5e1', s=25, alpha=0.7, label='Eligible Batters (N=297)', zorder=2)

# Top 10 Highlight
top10_bat = bat_merged[bat_merged['Rank'] <= 10]
ax.scatter(top10_bat['Rank'], top10_bat['Shrunk score'], color='#0284c7', s=70, edgecolor='#0f172a', linewidth=1.2, label='Top 10 Batters (Frozen)', zorder=4)

# Big-Name Highlight
bigname_bat_matches = bat_merged[bat_merged['Player'].isin(requested_batters_map.values())]
ax.scatter(bigname_bat_matches['Rank'], bigname_bat_matches['Shrunk score'], color='#e11d48', s=90, marker='D', edgecolor='#0f172a', linewidth=1.2, label='Requested Big-Name Batters', zorder=5)

# Annotate requested big names
for _, r in bigname_bat_matches.iterrows():
    p_name = [k for k, v in requested_batters_map.items() if v == r['Player']][0]
    rnk = int(r['Rank'])
    sc = r['Shrunk score']
    # Select offset based on position to avoid clutter
    if rnk <= 20:
        y_off = 0.02
        x_off = 3
    elif rnk <= 50:
        y_off = 0.015 if rnk % 2 == 0 else -0.02
        x_off = 4
    elif rnk <= 150:
        y_off = 0.015 if rnk % 2 == 0 else -0.02
        x_off = 4
    else:
        y_off = -0.025 if rnk > 200 else 0.015
        x_off = 4
    ax.annotate(
        f"{p_name} (#{rnk}, {sc:+.3f})",
        xy=(rnk, sc),
        xytext=(rnk + x_off, sc + y_off),
        fontsize=8,
        fontweight='bold',
        color='#9f1239',
        arrowprops=dict(arrowstyle="->", color='#e11d48', lw=0.8, alpha=0.8),
        zorder=6
    )

ax.axhline(0.0, color='#64748b', linestyle='--', linewidth=1.0, alpha=0.8, label='Situational Baseline (0.0)')
ax.set_title("Full Population Batting Reliability: Big-Name Player Rank Positions (N=297)", fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel("Overall Batting Reliability Rank (1 to 297)", fontsize=11, fontweight='bold')
ax.set_ylabel("Shrunk PWSVA Score (Runs / Ball Above Baseline)", fontsize=11, fontweight='bold')
ax.set_xlim(-5, 305)
ax.set_ylim(-0.20, 0.40)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right', fontsize=10)
plt.tight_layout()
fig_path1 = os.path.join(fig_dir, "fig_bigname_01_batting_full_population_ranks.png")
plt.savefig(fig_path1, dpi=300)
plt.close()
print("Saved fig_bigname_01_batting_full_population_ranks.png")

# -------------------------------------------------------------
# FIG 2: FULL POPULATION BOWLING RANKS (292 BOWLERS)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
ranks_b = bowl_merged['Rank'].values
scores_b = bowl_merged['Shrunk score'].values

# Neutral scatter for all bowlers
ax.scatter(ranks_b, scores_b, color='#cbd5e1', s=25, alpha=0.7, label='Eligible Bowlers (N=292)', zorder=2)

# Top 10 Highlight
top10_bowl = bowl_merged[bowl_merged['Rank'] <= 10]
ax.scatter(top10_bowl['Rank'], top10_bowl['Shrunk score'], color='#16a34a', s=70, edgecolor='#0f172a', linewidth=1.2, label='Top 10 Bowlers (Frozen)', zorder=4)

# Big-Name Highlight
bigname_bowl_matches = bowl_merged[bowl_merged['Player'].isin(requested_bowlers_map.values())]
ax.scatter(bigname_bowl_matches['Rank'], bigname_bowl_matches['Shrunk score'], color='#7c3aed', s=90, marker='D', edgecolor='#0f172a', linewidth=1.2, label='Requested Big-Name Bowlers', zorder=5)

# Annotate requested big names
for _, r in bigname_bowl_matches.iterrows():
    p_name = [k for k, v in requested_bowlers_map.items() if v == r['Player']][0]
    rnk = int(r['Rank'])
    sc = r['Shrunk score']
    y_off = 0.018 if rnk % 2 == 0 else -0.022
    x_off = 4
    if rnk > 200:
        y_off = -0.02
        x_off = -45
    ax.annotate(
        f"{p_name} (#{rnk}, {sc:+.3f})",
        xy=(rnk, sc),
        xytext=(rnk + x_off, sc + y_off),
        fontsize=8,
        fontweight='bold',
        color='#5b21b6',
        arrowprops=dict(arrowstyle="->", color='#7c3aed', lw=0.8, alpha=0.8),
        zorder=6
    )

ax.axhline(0.0, color='#64748b', linestyle='--', linewidth=1.0, alpha=0.8, label='Situational Baseline (0.0)')
ax.set_title("Full Population Bowling Reliability: Big-Name Player Rank Positions (N=292)", fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel("Overall Bowling Reliability Rank (1 to 292)", fontsize=11, fontweight='bold')
ax.set_ylabel("Shrunk SBVA Score (Runs Saved / Ball Relative to Baseline)", fontsize=11, fontweight='bold')
ax.set_xlim(-5, 300)
ax.set_ylim(-0.30, 0.22)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right', fontsize=10)
plt.tight_layout()
fig_path2 = os.path.join(fig_dir, "fig_bigname_02_bowling_full_population_ranks.png")
plt.savefig(fig_path2, dpi=300)
plt.close()
print("Saved fig_bigname_02_bowling_full_population_ranks.png")

# -------------------------------------------------------------
# FIG 3: BIG-NAME BATTING LEADERBOARD (BAR CHART WITH RAW MARKERS)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
df_plot_bat = df_bigname_bat.sort_values(by='Overall Rank', ascending=False).reset_index(drop=True)
y_pos = np.arange(len(df_plot_bat))

colors = ['#1e40af' if sc > 0.10 else '#3b82f6' if sc > 0.0 else '#ef4444' for sc in df_plot_bat['Shrunk PWSVA']]
bars = ax.barh(y_pos, df_plot_bat['Shrunk PWSVA'], color=colors, alpha=0.85, height=0.65, label='Shrunk PWSVA Score', zorder=3)

# Add raw score ghost markers
ax.scatter(df_plot_bat['Raw PWSVA'], y_pos, color='#0f172a', marker='|', s=140, linewidths=2.5, label='Raw PWSVA Score', zorder=5)

ax.axvline(0.0, color='#475569', linestyle='--', linewidth=1.0)
ax.set_yticks(y_pos)
y_labels = [f"#{r['Overall Rank']} {r['Requested Name']}" for _, r in df_plot_bat.iterrows()]
ax.set_yticklabels(y_labels, fontsize=10, fontweight='bold')

# Score value labels
for i, r in df_plot_bat.iterrows():
    shrunk_val = r['Shrunk PWSVA']
    raw_val = r['Raw PWSVA']
    x_text = shrunk_val + 0.008 if shrunk_val >= 0 else shrunk_val - 0.035
    ax.text(x_text, i, f"{shrunk_val:+.3f} (raw {raw_val:+.3f})", va='center', fontsize=8.5, fontweight='bold', color='#1e293b')

ax.set_xlabel("PWSVA Score (Runs / Ball Above Baseline)", fontsize=11, fontweight='bold')
ax.set_title("Big-Name Batting Reliability Leaderboard (Requested Players, N=17)", fontsize=13, fontweight='bold', pad=12)
ax.set_xlim(-0.15, 0.25)
ax.legend(frameon=True, facecolor='white', loc='lower right', fontsize=10)
plt.tight_layout()
fig_path3 = os.path.join(fig_dir, "fig_bigname_03_batting_leaderboard_bars.png")
plt.savefig(fig_path3, dpi=300)
plt.close()
print("Saved fig_bigname_03_batting_leaderboard_bars.png")

# -------------------------------------------------------------
# FIG 4: BIG-NAME BOWLING LEADERBOARD (BAR CHART WITH RAW MARKERS)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
df_plot_bowl = df_bigname_bowl.sort_values(by='Overall Rank', ascending=False).reset_index(drop=True)
y_pos_b = np.arange(len(df_plot_bowl))

colors_b = ['#15803d' if sc > 0.08 else '#22c55e' if sc > 0.0 else '#ef4444' for sc in df_plot_bowl['Shrunk SBVA']]
bars_b = ax.barh(y_pos_b, df_plot_bowl['Shrunk SBVA'], color=colors_b, alpha=0.85, height=0.65, label='Shrunk SBVA Score', zorder=3)

# Add raw score ghost markers
ax.scatter(df_plot_bowl['Raw SBVA'], y_pos_b, color='#0f172a', marker='|', s=140, linewidths=2.5, label='Raw SBVA Score', zorder=5)

ax.axvline(0.0, color='#475569', linestyle='--', linewidth=1.0)
ax.set_yticks(y_pos_b)
y_labels_b = [f"#{r['Overall Rank']} {r['Requested Name']}" for _, r in df_plot_bowl.iterrows()]
ax.set_yticklabels(y_labels_b, fontsize=10, fontweight='bold')

# Score value labels
for i, r in df_plot_bowl.iterrows():
    shrunk_val = r['Shrunk SBVA']
    raw_val = r['Raw SBVA']
    x_text = shrunk_val + 0.008 if shrunk_val >= 0 else shrunk_val - 0.045
    ax.text(x_text, i, f"{shrunk_val:+.3f} (raw {raw_val:+.3f})", va='center', fontsize=8.5, fontweight='bold', color='#1e293b')

ax.set_xlabel("SBVA Score (Runs Saved / Ball Relative to Baseline)", fontsize=11, fontweight='bold')
ax.set_title("Big-Name Bowling Reliability Leaderboard (Requested Players, N=11)", fontsize=13, fontweight='bold', pad=12)
ax.set_xlim(-0.28, 0.20)
ax.legend(frameon=True, facecolor='white', loc='lower right', fontsize=10)
plt.tight_layout()
fig_path4 = os.path.join(fig_dir, "fig_bigname_04_bowling_leaderboard_bars.png")
plt.savefig(fig_path4, dpi=300)
plt.close()
print("Saved fig_bigname_04_bowling_leaderboard_bars.png")

# -------------------------------------------------------------
# FIG 5: BATTING SCORE UNCERTAINTY (FOREST PLOT 95% CIs)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
df_ci_bat = df_bigname_bat.sort_values(by='Overall Rank', ascending=False).reset_index(drop=True)
y_pos = np.arange(len(df_ci_bat))

# Parse 95% CI strings
ci_lowers = []
ci_uppers = []
for _, r in df_ci_bat.iterrows():
    parts = r['95% Score CI'].replace('[', '').replace(']', '').split(',')
    ci_lowers.append(float(parts[0]))
    ci_uppers.append(float(parts[1]))

ci_lowers = np.array(ci_lowers)
ci_uppers = np.array(ci_uppers)
shrunk_vals = df_ci_bat['Shrunk PWSVA'].values
xerr_low = shrunk_vals - ci_lowers
xerr_high = ci_uppers - shrunk_vals

ax.errorbar(shrunk_vals, y_pos, xerr=[xerr_low, xerr_high], fmt='o', color='#1e3a8a', ecolor='#3b82f6', elinewidth=2, capsize=4, capthick=1.5, markersize=7, label='95% Bootstrap Confidence Interval', zorder=4)

ax.axvline(0.0, color='#ef4444', linestyle='--', linewidth=1.2, label='Baseline Replacement Level (0.0)')
ax.set_yticks(y_pos)
ax.set_yticklabels([f"#{r['Overall Rank']} {r['Requested Name']} (Rank CI: {r['95% Rank CI']})" for _, r in df_ci_bat.iterrows()], fontsize=9, fontweight='bold')
ax.set_xlabel("Shrunk PWSVA Score with 95% Bootstrap Confidence Bounds", fontsize=11, fontweight='bold')
ax.set_title("Batting Uncertainty & Estimation Variance for Big-Name Players", fontsize=13, fontweight='bold', pad=12)
ax.legend(frameon=True, facecolor='white', loc='lower right', fontsize=10)
plt.tight_layout()
fig_path5 = os.path.join(fig_dir, "fig_bigname_05_batting_score_uncertainty.png")
plt.savefig(fig_path5, dpi=300)
plt.close()
print("Saved fig_bigname_05_batting_score_uncertainty.png")

# -------------------------------------------------------------
# FIG 6: BOWLING SCORE UNCERTAINTY (FOREST PLOT 95% CIs)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
df_ci_bowl = df_bigname_bowl.sort_values(by='Overall Rank', ascending=False).reset_index(drop=True)
y_pos_b = np.arange(len(df_ci_bowl))

ci_lowers_b = []
ci_uppers_b = []
for _, r in df_ci_bowl.iterrows():
    parts = r['95% Score CI'].replace('[', '').replace(']', '').split(',')
    ci_lowers_b.append(float(parts[0]))
    ci_uppers_b.append(float(parts[1]))

ci_lowers_b = np.array(ci_lowers_b)
ci_uppers_b = np.array(ci_uppers_b)
shrunk_vals_b = df_ci_bowl['Shrunk SBVA'].values
xerr_low_b = shrunk_vals_b - ci_lowers_b
xerr_high_b = ci_uppers_b - shrunk_vals_b

ax.errorbar(shrunk_vals_b, y_pos_b, xerr=[xerr_low_b, xerr_high_b], fmt='s', color='#14532d', ecolor='#22c55e', elinewidth=2, capsize=4, capthick=1.5, markersize=7, label='95% Bootstrap Confidence Interval', zorder=4)

ax.axvline(0.0, color='#ef4444', linestyle='--', linewidth=1.2, label='Baseline Replacement Level (0.0)')
ax.set_yticks(y_pos_b)
ax.set_yticklabels([f"#{r['Overall Rank']} {r['Requested Name']} (Rank CI: {r['95% Rank CI']})" for _, r in df_ci_bowl.iterrows()], fontsize=9, fontweight='bold')
ax.set_xlabel("Shrunk SBVA Score with 95% Bootstrap Confidence Bounds", fontsize=11, fontweight='bold')
ax.set_title("Bowling Uncertainty & Estimation Variance for Big-Name Players", fontsize=13, fontweight='bold', pad=12)
ax.legend(frameon=True, facecolor='white', loc='lower right', fontsize=10)
plt.tight_layout()
fig_path6 = os.path.join(fig_dir, "fig_bigname_06_bowling_score_uncertainty.png")
plt.savefig(fig_path6, dpi=300)
plt.close()
print("Saved fig_bigname_06_bowling_score_uncertainty.png")

# -------------------------------------------------------------
# FIG 7: RAW VS SHRUNK COMPARISON (DUAL PANEL)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

# Batting Raw vs Shrunk
ax1.scatter(df_bigname_bat['Raw PWSVA'], df_bigname_bat['Shrunk PWSVA'], color='#2563eb', s=80, edgecolor='#1e293b', zorder=4)
min_b = min(df_bigname_bat['Raw PWSVA'].min(), df_bigname_bat['Shrunk PWSVA'].min()) - 0.03
max_b = max(df_bigname_bat['Raw PWSVA'].max(), df_bigname_bat['Shrunk PWSVA'].max()) + 0.03
ax1.plot([min_b, max_b], [min_b, max_b], 'k--', alpha=0.5, label='No Shrinkage (y = x)')
ax1.axhline(0, color='gray', linestyle=':', alpha=0.6)
ax1.axvline(0, color='gray', linestyle=':', alpha=0.6)

for _, r in df_bigname_bat.iterrows():
    ax1.annotate(r['Requested Name'], (r['Raw PWSVA'], r['Shrunk PWSVA']),
                 xytext=(r['Raw PWSVA'] + 0.005, r['Shrunk PWSVA'] - 0.008),
                 fontsize=8, fontweight='bold', color='#1e3a8a')

ax1.set_title("Batting: Raw vs. Shrunk Score (K_bat = 600)", fontsize=12, fontweight='bold')
ax1.set_xlabel("Raw PWSVA Score", fontsize=10, fontweight='bold')
ax1.set_ylabel("Shrunk PWSVA Score", fontsize=10, fontweight='bold')
ax1.legend(loc='upper left', frameon=True)

# Bowling Raw vs Shrunk
ax2.scatter(df_bigname_bowl['Raw SBVA'], df_bigname_bowl['Shrunk SBVA'], color='#16a34a', s=80, edgecolor='#1e293b', zorder=4)
min_bw = min(df_bigname_bowl['Raw SBVA'].min(), df_bigname_bowl['Shrunk SBVA'].min()) - 0.03
max_bw = max(df_bigname_bowl['Raw SBVA'].max(), df_bigname_bowl['Shrunk SBVA'].max()) + 0.03
ax2.plot([min_bw, max_bw], [min_bw, max_bw], 'k--', alpha=0.5, label='No Shrinkage (y = x)')
ax2.axhline(0, color='gray', linestyle=':', alpha=0.6)
ax2.axvline(0, color='gray', linestyle=':', alpha=0.6)

for _, r in df_bigname_bowl.iterrows():
    ax2.annotate(r['Requested Name'], (r['Raw SBVA'], r['Shrunk SBVA']),
                 xytext=(r['Raw SBVA'] + 0.005, r['Shrunk SBVA'] - 0.008),
                 fontsize=8, fontweight='bold', color='#14532d')

ax2.set_title("Bowling: Raw vs. Shrunk Score (K_bowl = 500)", fontsize=12, fontweight='bold')
ax2.set_xlabel("Raw SBVA Score", fontsize=10, fontweight='bold')
ax2.set_ylabel("Shrunk SBVA Score", fontsize=10, fontweight='bold')
ax2.legend(loc='upper left', frameon=True)

plt.suptitle("Impact of Empirical Bayes Regularization on Big-Name Players", fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig_path7 = os.path.join(fig_dir, "fig_bigname_07_raw_vs_shrunk_comparison.png")
plt.savefig(fig_path7, dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig_bigname_07_raw_vs_shrunk_comparison.png")

# -------------------------------------------------------------
# FIG 8: DUAL-DISCIPLINE ALL-ROUNDERS SCATTER PLOT
# -------------------------------------------------------------
# Identify players qualified in both batting and bowling
allrounders = [
    ('Ravindra Jadeja', 121, 45),
    ('Mitchell Marsh', 19, 60),
    ('Hardik Pandya', 130, 284),
    ('Sam Curran', 189, 286),
    ('Axar Patel', 95, 66),
    ('Mitchell Santner', 221, 37),
    ('Patrick Cummins', 77, 175),
    ('Glenn Maxwell', 46, 121),
    ('Andre Russell', 9, 270),
    ('Sunil Narine', 275, 3),
    ('Moeen Ali', 141, 48),
    ('Marcus Stoinis', 73, 241),
    ('Shivam Dube', 39, 273),
    ('Shardul Thakur', 283, 288),
    ('Washington Sundar', 60, 108)
]

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

# Calculate percentiles (lower rank = higher percentile)
# Total batters = 297, Total bowlers = 292
ar_names = [a[0] for a in allrounders]
bat_ranks = [a[1] for a in allrounders]
bowl_ranks = [a[2] for a in allrounders]

bat_pct = [(1.0 - (r - 1) / 297.0) * 100 for r in bat_ranks]
bowl_pct = [(1.0 - (r - 1) / 292.0) * 100 for r in bowl_ranks]

scatter = ax.scatter(bat_pct, bowl_pct, color='#0284c7', s=100, edgecolor='#0f172a', linewidth=1.2, zorder=4)

ax.axhline(50, color='#94a3b8', linestyle='--', alpha=0.7)
ax.axvline(50, color='#94a3b8', linestyle='--', alpha=0.7)

# Quadrant labels
ax.text(75, 75, "ELITE DUAL THREAT\n(Top 50% Both)", fontsize=11, fontweight='bold', color='#15803d', ha='center', va='center', alpha=0.3)
ax.text(25, 75, "BOWLING SPECIALIST\n(Below Median Batting)", fontsize=11, fontweight='bold', color='#6b21a8', ha='center', va='center', alpha=0.3)
ax.text(75, 25, "BATTING SPECIALIST\n(Below Median Bowling)", fontsize=11, fontweight='bold', color='#1e40af', ha='center', va='center', alpha=0.3)
ax.text(25, 25, "SUB-MEDIAN BOTH\n(Relies on Volume)", fontsize=11, fontweight='bold', color='#b91c1c', ha='center', va='center', alpha=0.3)

for name, bp, bwp, br, bwr in zip(ar_names, bat_pct, bowl_pct, bat_ranks, bowl_ranks):
    ax.annotate(
        f"{name}\n(Bat #{br}, Bowl #{bwr})",
        (bp, bwp),
        xytext=(bp + 1.5, bwp + 1.5),
        fontsize=8,
        fontweight='bold',
        color='#0f172a'
    )

ax.set_title("Dual-Discipline Reliability Percentiles: Prominent All-Rounders", fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel("Batting Reliability Percentile (0 = Worst, 100 = Best)", fontsize=11, fontweight='bold')
ax.set_ylabel("Bowling Reliability Percentile (0 = Worst, 100 = Best)", fontsize=11, fontweight='bold')
ax.set_xlim(-5, 105)
ax.set_ylim(-5, 105)
plt.tight_layout()
fig_path8 = os.path.join(fig_dir, "fig_bigname_08_dual_discipline_allrounders.png")
plt.savefig(fig_path8, dpi=300)
plt.close()
print("Saved fig_bigname_08_dual_discipline_allrounders.png")

print("\nAll visualizations generated successfully in outputs/step_8_eda/big_name_player_analysis/figures/")
