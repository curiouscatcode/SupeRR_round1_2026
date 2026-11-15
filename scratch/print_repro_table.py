import pandas as pd
df = pd.read_csv('scratch/independent_reproduction_results.csv')
print("=== INDEPENDENT REPRODUCTION RESULTS TABLE ===")
for _, r in df.iterrows():
    print(f"{r['label']:45s} | MaxDiff={r['max_diff']:.2e} | P_bat={r['p_bat_indep']:5.2f} (pipe={r['p_bat_pq']:5.2f}) | P_bowl={r['p_bowl_indep']:5.2f} (pipe={r['p_bowl_pq']:5.2f})")
print(f"Overall max error: {df['max_diff'].max():.4e}")
print(f"Number with error < 0.01 points: {sum(df['max_diff'] < 0.01)} / 10")
