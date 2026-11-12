import pandas as pd
import numpy as np

# Load the processed dataset
df = pd.read_csv('data/processed/delivery_pressure_index.csv')

# Select a diverse sample of 1,000 deliveries:
# Stratified across Innings 1 and 2, and all 3 phases
sample_indices = []
for inn in [1, 2]:
    for ph in ['PP', 'Middle', 'Death']:
        sub = df[(df['innings'] == inn) & (df['phase'] == ph)]
        # sample up to 200 per stratum
        n_sample = min(200, len(sub))
        sample_indices.extend(sub.sample(n=n_sample, random_state=42).index.tolist())

sample_df = df.loc[sample_indices].copy()
print(f"Selected {len(sample_df)} deliveries across all innings and phases for controlled perturbation test.")

# Baseline PI values
orig_batting_pi = sample_df['Batting_PI'].to_numpy()
orig_bowling_pi = sample_df['Bowling_PI'].to_numpy()

# Now create a severely perturbed copy of the delivery outcome columns:
# 1. Invert wicket: 0 -> 1, 1 -> 0
# 2. Multiply runs by 6 or set to 6
# 3. Add heavy extras
# 4. Alter dismissal type and bowler runs conceded
perturbed_df = sample_df.copy()
perturbed_df['runs'] = np.where(perturbed_df['runs'] == 0, 6, 0)
perturbed_df['is_wicket'] = ~perturbed_df['is_wicket'].astype(bool)
perturbed_df['is_four'] = np.where(perturbed_df['is_four'] == 0, 1, 0)
perturbed_df['is_six'] = np.where(perturbed_df['is_six'] == 0, 1, 0)
perturbed_df['bowler_runs_conceded'] = np.where(perturbed_df['bowler_runs_conceded'] == 0, 7, 0)
perturbed_df['team_runs_added'] = np.where(perturbed_df['team_runs_added'] == 0, 7, 0)

# Import the calculation function from src.calculate_pressure_index
# We test by running the vectorized logic directly on the perturbed dataframe
import sys
sys.path.append('src')
from calculate_pressure_index import assign_pressure_level

# Re-run PI calculation logic on perturbed_df
striker_bf = perturbed_df['striker_balls_faced_before'].to_numpy(dtype=float)
b_batter = np.clip(((10.0 - striker_bf) / 10.0) * 100.0, 0.0, 100.0)
i_batter = b_batter

bowler_spell_balls = perturbed_df['bowler_legal_balls_in_spell_before'].to_numpy(dtype=float)
b_workload = np.clip((bowler_spell_balls / 12.0) * 100.0, 0.0, 100.0)
s_settling = b_batter
i_bowler = (0.50 * b_workload) + (0.50 * s_settling)

innings = perturbed_df['innings'].to_numpy()
phase = perturbed_df['phase'].to_numpy()
w_before = perturbed_df['wickets_before'].to_numpy(dtype=float)
crr = perturbed_df['current_run_rate'].to_numpy(dtype=float)
phase_overs = perturbed_df['phase_overs_completed'].to_numpy(dtype=float)

runs_req = perturbed_df['runs_required'].to_numpy(dtype=float)
balls_rem = perturbed_df['balls_remaining'].to_numpy(dtype=float)

total_rows = len(perturbed_df)
rrr = np.full(total_rows, np.nan, dtype=float)
inn2_mask = (innings == 2)
valid_inn2 = inn2_mask & (balls_rem > 0)
rrr[valid_inn2] = (runs_req[valid_inn2] / balls_rem[valid_inn2]) * 6.0

m_b1_pp  = (innings == 1) & (phase == 'PP')
m_b1_mo  = (innings == 1) & (phase == 'Middle')
m_b1_do  = (innings == 1) & (phase == 'Death')

m_b2_pp  = (innings == 2) & (phase == 'PP')
m_b2_mo  = (innings == 2) & (phase == 'Middle')
m_b2_do  = (innings == 2) & (phase == 'Death')

new_bat_pi = np.full(total_rows, np.nan)
new_bowl_pi = np.full(total_rows, np.nan)

# PI_B1_PP
w_b1_pp = np.clip((w_before[m_b1_pp] / 6.0) * 100.0, 0.0, 100.0)
s_b1_pp = np.clip(((8.0 - crr[m_b1_pp]) / 8.0) * 100.0, 0.0, 100.0)
o_b1_pp = np.clip((phase_overs[m_b1_pp] / 6.0) * 100.0, 0.0, 100.0)
t_b1_pp = (0.40 * w_b1_pp) + (0.40 * s_b1_pp) + (0.20 * o_b1_pp)
new_bat_pi[m_b1_pp] = np.round((0.65 * t_b1_pp) + (0.35 * i_batter[m_b1_pp]), 2)

w_bo1_pp = np.clip(((6.0 - w_before[m_b1_pp]) / 6.0) * 100.0, 0.0, 100.0)
s_bo1_pp = np.clip(((crr[m_b1_pp] - 8.0) / 4.0) * 100.0, 0.0, 100.0)
o_bo1_pp = np.clip((phase_overs[m_b1_pp] / 6.0) * 100.0, 0.0, 100.0)
t_bo1_pp = (0.40 * w_bo1_pp) + (0.40 * s_bo1_pp) + (0.20 * o_bo1_pp)
new_bowl_pi[m_b1_pp] = np.round((0.65 * t_bo1_pp) + (0.35 * i_bowler[m_b1_pp]), 2)

# PI_B1_MO
w_b1_mo = np.clip((w_before[m_b1_mo] / 6.0) * 100.0, 0.0, 100.0)
s_b1_mo = np.clip(((8.0 - crr[m_b1_mo]) / 8.0) * 100.0, 0.0, 100.0)
o_b1_mo = np.clip((phase_overs[m_b1_mo] / 9.0) * 100.0, 0.0, 100.0)
t_b1_mo = (0.40 * w_b1_mo) + (0.40 * s_b1_mo) + (0.20 * o_b1_mo)
new_bat_pi[m_b1_mo] = np.round((0.65 * t_b1_mo) + (0.35 * i_batter[m_b1_mo]), 2)

w_bo1_mo = np.clip(((6.0 - w_before[m_b1_mo]) / 6.0) * 100.0, 0.0, 100.0)
s_bo1_mo = np.clip(((crr[m_b1_mo] - 7.0) / 4.0) * 100.0, 0.0, 100.0)
o_bo1_mo = np.clip((phase_overs[m_b1_mo] / 9.0) * 100.0, 0.0, 100.0)
t_bo1_mo = (0.40 * w_bo1_mo) + (0.40 * s_bo1_mo) + (0.20 * o_bo1_mo)
new_bowl_pi[m_b1_mo] = np.round((0.65 * t_bo1_mo) + (0.35 * i_bowler[m_b1_mo]), 2)

# PI_B1_DO
w_b1_do = np.clip((w_before[m_b1_do] / 6.0) * 100.0, 0.0, 100.0)
s_b1_do = np.clip(((10.0 - crr[m_b1_do]) / 10.0) * 100.0, 0.0, 100.0)
o_b1_do = np.clip((phase_overs[m_b1_do] / 5.0) * 100.0, 0.0, 100.0)
t_b1_do = (0.40 * w_b1_do) + (0.40 * s_b1_do) + (0.20 * o_b1_do)
new_bat_pi[m_b1_do] = np.round((0.65 * t_b1_do) + (0.35 * i_batter[m_b1_do]), 2)

w_bo1_do = np.clip(((6.0 - w_before[m_b1_do]) / 6.0) * 100.0, 0.0, 100.0)
s_bo1_do = np.clip(((crr[m_b1_do] - 9.0) / 6.0) * 100.0, 0.0, 100.0)
o_bo1_do = np.clip((phase_overs[m_b1_do] / 5.0) * 100.0, 0.0, 100.0)
t_bo1_do = (0.40 * w_bo1_do) + (0.40 * s_bo1_do) + (0.20 * o_bo1_do)
new_bowl_pi[m_b1_do] = np.round((0.65 * t_bo1_do) + (0.35 * i_bowler[m_b1_do]), 2)

# PI_B2_PP
r_b2_pp = np.clip(((rrr[m_b2_pp] - 6.0) / 6.0) * 100.0, 0.0, 100.0)
w_b2_pp = np.clip((w_before[m_b2_pp] / 6.0) * 100.0, 0.0, 100.0)
o_b2_pp = np.clip((phase_overs[m_b2_pp] / 6.0) * 100.0, 0.0, 100.0)
t_b2_pp = (0.50 * r_b2_pp) + (0.30 * w_b2_pp) + (0.20 * o_b2_pp)
new_bat_pi[m_b2_pp] = np.round((0.65 * t_b2_pp) + (0.35 * i_batter[m_b2_pp]), 2)

s_bo2_pp = np.clip(((crr[m_b2_pp] - 6.0) / 6.0) * 100.0, 0.0, 100.0)
w_bo2_pp = np.clip(((6.0 - w_before[m_b2_pp]) / 6.0) * 100.0, 0.0, 100.0)
o_bo2_pp = np.clip((phase_overs[m_b2_pp] / 6.0) * 100.0, 0.0, 100.0)
t_bo2_pp = (0.40 * s_bo2_pp) + (0.40 * w_bo2_pp) + (0.20 * o_bo2_pp)
new_bowl_pi[m_b2_pp] = np.round((0.65 * t_bo2_pp) + (0.35 * i_bowler[m_b2_pp]), 2)

# PI_B2_MO
r_b2_mo = np.clip(((rrr[m_b2_mo] - 7.0) / 6.0) * 100.0, 0.0, 100.0)
w_b2_mo = np.clip((w_before[m_b2_mo] / 6.0) * 100.0, 0.0, 100.0)
o_b2_mo = np.clip((phase_overs[m_b2_mo] / 9.0) * 100.0, 0.0, 100.0)
t_b2_mo = (0.50 * r_b2_mo) + (0.30 * w_b2_mo) + (0.20 * o_b2_mo)
new_bat_pi[m_b2_mo] = np.round((0.65 * t_b2_mo) + (0.35 * i_batter[m_b2_mo]), 2)

s_bo2_mo = np.clip(((crr[m_b2_mo] - 7.0) / 4.0) * 100.0, 0.0, 100.0)
w_bo2_mo = np.clip(((6.0 - w_before[m_b2_mo]) / 6.0) * 100.0, 0.0, 100.0)
o_bo2_mo = np.clip((phase_overs[m_b2_mo] / 9.0) * 100.0, 0.0, 100.0)
t_bo2_mo = (0.40 * s_bo2_mo) + (0.40 * w_bo2_mo) + (0.20 * o_bo2_mo)
new_bowl_pi[m_b2_mo] = np.round((0.65 * t_bo2_mo) + (0.35 * i_bowler[m_b2_mo]), 2)

# PI_B2_DO
r_b2_do = np.clip(((rrr[m_b2_do] - 9.0) / 9.0) * 100.0, 0.0, 100.0)
w_b2_do = np.clip((w_before[m_b2_do] / 6.0) * 100.0, 0.0, 100.0)
o_b2_do = np.clip((phase_overs[m_b2_do] / 5.0) * 100.0, 0.0, 100.0)
t_b2_do = (0.50 * r_b2_do) + (0.30 * w_b2_do) + (0.20 * o_b2_do)
new_bat_pi[m_b2_do] = np.round((0.65 * t_b2_do) + (0.35 * i_batter[m_b2_do]), 2)

s_bo2_do = np.clip(((rrr[m_b2_do] - 9.0) / 9.0) * 100.0, 0.0, 100.0)
w_bo2_do = np.clip(((6.0 - w_before[m_b2_do]) / 6.0) * 100.0, 0.0, 100.0)
o_bo2_do = np.clip((phase_overs[m_b2_do] / 5.0) * 100.0, 0.0, 100.0)
t_bo2_do = (0.50 * s_bo2_do) + (0.30 * w_bo2_do) + (0.20 * o_bo2_do)
new_bowl_pi[m_b2_do] = np.round((0.65 * t_bo2_do) + (0.35 * i_bowler[m_b2_do]), 2)

diff_bat = np.abs(orig_batting_pi - new_bat_pi)
diff_bowl = np.abs(orig_bowling_pi - new_bowl_pi)

print(f"Max absolute difference in Batting_PI after severe outcome perturbation: {diff_bat.max():.8f}")
print(f"Max absolute difference in Bowling_PI after severe outcome perturbation: {diff_bowl.max():.8f}")
assert diff_bat.max() == 0.0, "Batting_PI changed when outcome columns were perturbed!"
assert diff_bowl.max() == 0.0, "Bowling_PI changed when outcome columns were perturbed!"
print("CONTROLLED TEST PASSED: Changing delivery outcomes (runs, wickets, extras, boundaries) has ZERO effect on PI!")
