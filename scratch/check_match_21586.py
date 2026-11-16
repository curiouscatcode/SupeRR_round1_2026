import pandas as pd

# Check Step 4 cohort filter or step 2.1
# Let's inspect src/step_4_pressure_pipeline/01_cohort_filter.py or check clean_cohort_deliveries.parquet
cohort = pd.read_parquet('outputs/step_4_pressure_pipeline/clean_cohort_deliveries.parquet')
print("Is 21586 in clean_cohort_deliveries?", 21586 in cohort['match_id'].unique())

# Let's inspect src/step_4_pressure_pipeline/01_cohort_filter.py
with open('src/step_4_pressure_pipeline/01_cohort_filter.py') as f:
    text = f.read()
    print("Filter script snippet:")
    print(text[:1500])
