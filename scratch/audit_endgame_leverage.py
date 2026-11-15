import numpy as np
import pandas as pd

# Load WPA parquet to inspect real deliveries
df = pd.read_parquet('outputs/step_16_5_wpa_investigation/delivery_wpa_leverage.parquet')

print("--- END-GAME LEVERAGE EXAMPLES IN REAL MATCHES ---")
inn2 = df[df['innings'] == 2]

# Let's inspect tight finishes: 20th over, balls_remaining <= 6, runs_required <= 15
tight = inn2[(inn2['overid'] == 20) & (inn2['runs_required'] <= 15) & (inn2['runs_required'] > 0)].copy()
sample_tight = tight[['match_id', 'over_ball_num', 'balls_remaining', 'runs_required', 'wickets_before', 'wp_before', 'expected_leverage_pct', 'runs', 'is_wicket', 'wpa_pct']].head(15)
print(sample_tight.to_string(index=False))

print("\n--- LEVERAGE SUMMARY BY PHASE AND INNINGS ---")
print(df.groupby(['innings', 'phase'])[['expected_leverage_pct', 'absolute_wpa_pct']].agg(['mean', 'median', 'std', 'max']))
