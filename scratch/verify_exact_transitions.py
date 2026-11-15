import pandas as pd
import numpy as np

df = pd.read_parquet('outputs/step_4_pressure_pipeline/clean_cohort_deliveries.parquet')

def classify_outcome_exact(row):
    ex = str(row['extras_type']).lower()
    if 'wide' in ex:
        return 'wide'
    if 'overstep' in ex or 'no ball' in ex or 'noball' in ex:
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
        # any other extras or rare run counts
        return 'one'

df['outcome_cat'] = df.apply(classify_outcome_exact, axis=1)

categories = ['dot', 'one', 'two', 'three', 'four', 'six', 'wicket', 'wide', 'no_ball']

empirical_transitions = {}
for inn in [1, 2]:
    for ph in ['PP', 'Middle', 'Death']:
        sub = df[(df['innings'] == inn) & (df['phase'] == ph)]
        total = len(sub)
        counts = sub['outcome_cat'].value_counts()
        probs = [float(counts.get(c, 0) / total) for c in categories]
        # Normalize to exact 1.0
        p_arr = np.array(probs)
        p_arr = p_arr / p_arr.sum()
        key = f"{ph}_inn{inn}"
        empirical_transitions[key] = [round(float(x), 6) for x in p_arr]
        # fix slight rounding on last element to ensure sum == 1.0
        diff = 1.0 - sum(empirical_transitions[key])
        empirical_transitions[key][0] += diff

print("=== EXACT EMPIRICAL TRANSITION PROBABILITIES (FROM CERTIFIED COHORT) ===")
for k, v in empirical_transitions.items():
    print(f"{k:12s}: sum = {sum(v):.6f}")
    print("  ", [round(x, 4) for x in v])
