import pandas as pd
import numpy as np

for disc in ['batting', 'bowling']:
    path = f'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_{disc}_rankings.csv'
    df = pd.read_csv(path).head(10).iloc[::-1].copy()
    s_min = df['Shrunk score'].min()
    s_max = df['Shrunk score'].max()
    norms = (df['Shrunk score'] - s_min) / (s_max - s_min + 1e-9)
    text_colors = ['#0F172A' if n < 0.48 else '#FFFFFF' for n in norms]
    print(f"=== {disc.upper()} ===")
    for (_, r), col, n in zip(df.iterrows(), text_colors, norms):
        print(f"Rank {int(r['Rank'])}: {r['Player']} (score={r['Shrunk score']:.4f}, norm={n:.2f}) -> text: {col}")
