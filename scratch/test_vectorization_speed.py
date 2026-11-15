import numpy as np
import pandas as pd
import time

# Test vectorization of WP and consequence
df = pd.read_parquet('outputs/step_4_pressure_pipeline/clean_cohort_deliveries.parquet')
print(f"Loaded {len(df)} deliveries.")
t0 = time.time()

# Check vectorized speed for 9 outcomes
inn2_mask = (df['innings'] == 2).values
print(f"Innings 2 rows: {inn2_mask.sum()}, Innings 1 rows: {(~inn2_mask).sum()}")
print(f"Elapsed test setup: {time.time() - t0:.2f}s")
