# Step 14.2.1 — Independent Audit of Experimental Workload Formula

## Overview
This package conducts an independent audit of **Step 14.2: Experimental Workload Formula Implementation and Impact Analysis**. It evaluates whether Step 14.2's mathematical implementations, classification shifts, player eligibility changes, ranking impacts, and conclusions are numerically and methodologically sound.

## Strict Boundaries
- Official v2.0 code and production datasets (`data/processed/*`) are untouched.
- Step 14.2 implementation scripts and outputs (`src/step_14_2*`, `outputs/step_14_2*`) are untouched and treated strictly as audit targets.
- No new ranking formulas or alternative workload formulas were introduced.
- All code and artifacts are strictly isolated in `src/step_14_2_1_independent_audit/` and `outputs/step_14_2_1_independent_audit/`.

## Directory Structure
```
src/step_14_2_1_independent_audit/
├── 01_audit_workload_and_spell_reset.py                # Module 1: Formula calculations & spell reset
├── 02_audit_pressure_classification_and_transitions.py # Module 2: Classification threshold & transition audit
├── 03_audit_performance_and_accounting_consistency.py # Module 3: 233 exclusion filter & accounting totals
├── 04_audit_eligibility_and_rankings.py               # Module 4: Rule B eligibility & ranking reconciliation
├── 05_generate_audit_report_and_register.py           # Module 5: Discrepancy register & final report
├── run_step_14_2_1_audit.py                           # Master pipeline runner
└── README.md                                          # Package documentation

outputs/step_14_2_1_independent_audit/
├── audit_workload_examples.csv                        # Concrete delivery case studies
├── step_14_2_1_pressure_transitions.csv               # Full phase & innings transition reconciliations
├── 01_audit_pressure_transitions.png                  # 4-panel diagnostic plot (transitions & boundary zoom)
├── step_14_2_1_accounting_audit.csv                   # Delivery and performance accounting audit
├── step_14_2_1_eligibility_audit.csv                  # Rule B qualification shifts for all 589 bowlers
├── step_14_2_1_ranking_reconciliation.csv             # Full-population bowling ranking comparison
├── 02_audit_ranking_reconciliation.png                # 4-panel diagnostic plot (ranking & Rule B space)
├── step_14_2_1_discrepancy_register.csv               # Complete register of all audit findings
└── step_14_2_1_independent_audit_report.md            # Final consolidated audit report
```

## Running the Complete Audit
To run the full independent audit pipeline from end to end:
```bash
python src/step_14_2_1_independent_audit/run_step_14_2_1_audit.py
```
Total runtime is approximately 10 to 15 seconds.
