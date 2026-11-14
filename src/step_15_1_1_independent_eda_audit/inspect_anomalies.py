import pandas as pd

df = pd.read_csv('outputs/step_15_1_final_results_eda/outliers_and_anomalies.csv')
print(f"Total flagged: {len(df)}")
for idx, r in df.iterrows():
    print(f"{idx+1}. [{r['discipline']}] {r['player_name']} (T{r['tier']} #{r['tier_rank']}) - {r['anomaly_category']}: {r['details']}")
