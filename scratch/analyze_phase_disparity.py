import pandas as pd
import numpy as np

df = pd.read_parquet('outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet')

metrics = ['pressure_batting', 'pressure_bowling', 'task_difficulty_bat', 'task_difficulty_bowl', 'normalized_consequence_L', 'raw_consequence_L']

def summarize(series):
    return {
        'N': len(series),
        'Mean': series.mean(),
        'Std': series.std(),
        'p10': np.percentile(series, 10),
        'p25': np.percentile(series, 25),
        'p50': np.percentile(series, 50),
        'p75': np.percentile(series, 75),
        'p90': np.percentile(series, 90)
    }

print("==========================================================================================")
print("PHASE AND INNINGS PRESSURE DISTRIBUTION AUDIT")
print("==========================================================================================")

groups = [
    ('Overall', df),
    ('Innings 1 All', df[df['innings'] == 1]),
    ('Innings 1 Powerplay', df[(df['innings'] == 1) & (df['phase'] == 'PP')]),
    ('Innings 1 Middle', df[(df['innings'] == 1) & (df['phase'] == 'Middle')]),
    ('Innings 1 Death', df[(df['innings'] == 1) & (df['phase'] == 'Death')]),
    ('Innings 2 All', df[df['innings'] == 2]),
    ('Innings 2 Powerplay', df[(df['innings'] == 2) & (df['phase'] == 'PP')]),
    ('Innings 2 Middle', df[(df['innings'] == 2) & (df['phase'] == 'Middle')]),
    ('Innings 2 Death', df[(df['innings'] == 2) & (df['phase'] == 'Death')]),
]

summary_rows = []
for name, sub in groups:
    for m in metrics:
        s = summarize(sub[m])
        s['Group'] = name
        s['Metric'] = m
        summary_rows.append(s)

sum_df = pd.DataFrame(summary_rows)
sum_df = sum_df[['Group', 'Metric', 'N', 'Mean', 'Std', 'p10', 'p25', 'p50', 'p75', 'p90']]

# Print Batting Pressure
print("\n--- BATTING PRESSURE (P_bat) DISTRIBUTION ---")
pbat_df = sum_df[sum_df['Metric'] == 'pressure_batting']
print(pbat_df.to_string(index=False))

# Print Bowling Pressure
print("\n--- BOWLING PRESSURE (P_bowl) DISTRIBUTION ---")
pbowl_df = sum_df[sum_df['Metric'] == 'pressure_bowling']
print(pbowl_df.to_string(index=False))

# Print Task Difficulty Batting
print("\n--- TASK DIFFICULTY BATTING (T_bat) DISTRIBUTION ---")
tbat_df = sum_df[sum_df['Metric'] == 'task_difficulty_bat']
print(tbat_df.to_string(index=False))

# Print Task Difficulty Bowling
print("\n--- TASK DIFFICULTY BOWLING (T_bowl) DISTRIBUTION ---")
tbowl_df = sum_df[sum_df['Metric'] == 'task_difficulty_bowl']
print(tbowl_df.to_string(index=False))

# Print Normalized Consequence L_norm
print("\n--- NORMALIZED CONSEQUENCE (L_norm) DISTRIBUTION ---")
lnorm_df = sum_df[sum_df['Metric'] == 'normalized_consequence_L']
print(lnorm_df.to_string(index=False))

# Print Raw Consequence raw_L
print("\n--- RAW CONSEQUENCE (raw_L) DISTRIBUTION ---")
rawL_df = sum_df[sum_df['Metric'] == 'raw_consequence_L']
print(rawL_df.to_string(index=False))

sum_df.to_csv('scratch/phase_distribution_summary.csv', index=False)
