import pandas as pd
import numpy as np

df = pd.read_parquet('outputs/step_4_pressure_pipeline/clean_cohort_deliveries.parquet')

# Let's inspect how outcomes are classified in the raw delivery data:
# runs, is_four, is_six, is_wicket, extras_type
# Legal ball vs wide vs no-ball:
def classify_outcome(row):
    ex = str(row['extras_type']).lower()
    if 'wide' in ex:
        return 'wide'
    if 'no ball' in ex or 'noball' in ex or 'no_ball' in ex:
        return 'no_ball'
    if row['is_wicket'] == 1:
        return 'wicket'
    r = row['runs']
    if r == 0:
        return 'dot'
    elif r == 1:
        return 'one'
    elif r == 2:
        return 'two'
    elif r == 3:
        return 'three'
    elif r == 4 or row['is_four'] == 1:
        return 'four'
    elif r == 6 or row['is_six'] == 1:
        return 'six'
    else:
        return 'other'

df['outcome_cat'] = df.apply(classify_outcome, axis=1)

print("Outcome categories value counts:")
print(df['outcome_cat'].value_counts())

# Group by (phase, innings)
categories = ['dot', 'one', 'two', 'three', 'four', 'six', 'wicket', 'wide', 'no_ball']

for inn in [1, 2]:
    for ph in ['PP', 'Middle', 'Death']:
        sub = df[(df['innings'] == inn) & (df['phase'] == ph)]
        total = len(sub)
        counts = sub['outcome_cat'].value_counts()
        probs = [counts.get(c, 0) / total for c in categories]
        print(f"\nStratum {ph}_inn{inn} (N={total}):")
        for c, p in zip(categories, probs):
            print(f"  {c:8s}: {p:.4f} (count={counts.get(c, 0)})")
        print(f"  SUM = {sum(probs):.5f}")
