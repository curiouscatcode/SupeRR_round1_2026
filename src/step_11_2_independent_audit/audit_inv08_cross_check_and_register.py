"""
src/step_11_2_independent_audit/audit_inv08_cross_check_and_register.py
Step 11.2 Independent Audit - Investigation 8: Cross-Check & Discrepancy Register

Compiles the comprehensive cross-check of all Step 11 investigation claims against independent
calculations, and outputs the official discrepancy register CSV.
"""

import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "step_11_2_independent_audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_investigation():
    print("=" * 80)
    print("AUDIT INVESTIGATION 8: CROSS-CHECK & DISCREPANCY REGISTER")
    print("=" * 80)
    
    register_records = [
        {
            'Claim': "Bumrah high-pressure legal balls, runs, wickets, wicket rate",
            'Step_11_Value': "168 legal balls, 194 runs, 5 wickets, 2.98% wicket rate, Econ 6.93",
            'Independently_Calculated_Value': "168 legal balls, 194 runs, 5 wickets, 2.9762% (2.98%) wicket rate, Econ 6.9286 (6.93)",
            'Status': "Confirmed",
            'Explanation': "Verified directly from delivery_pressure_index.csv where Bowling_PI > 60.0. All 5 wickets are bowler-credited (2 bowled, 3 caught; 0 run outs)."
        },
        {
            'Claim': "Step 8 EDA Bumrah metrics (3 wickets, 1.79% wicket rate, Econ 6.89, Rank #14)",
            'Step_11_Value': "Acknowledged discrepancy between Step 8 (1.79%, 3 wickets) and Step 11 (2.98%, 5 wickets)",
            'Independently_Calculated_Value': "Step 8 had an editorial narrative error in eda_07_outliers_and_anomalies.py (hardcoded VULN-01 dictionary). Innings 1 wickets (3) / 168 balls = 1.79%; High tier runs (193) / 168 balls * 6 = 6.89 rpo.",
            'Status': "Confirmed",
            'Explanation': "Authoritative truth is 5 wickets, 168 balls, 2.98%, 6.93 rpo, Rank #24. Step 8 EDA contained an unverified manual dictionary entry."
        },
        {
            'Claim': "Batting Strike Rate and Boundary Execution correlation",
            'Step_11_Value': "r = 0.9628 in Tier 1",
            'Independently_Calculated_Value': "r = 0.9628 in Tier 1 (N=116), r = 0.9638 across All Batters (N=816), r = 0.9636 in Tier 2 (N=72)",
            'Status': "Confirmed",
            'Explanation': "Fully confirmed across all population subsets. Linear regression yields R^2 = 0.9270, leaving only 7.30% independent residual variance."
        },
        {
            'Claim': "Combined scoring speed contribution to BRS variance",
            'Step_11_Value': "68.07% of total variance (SR 45.65% + Exec 22.42%)",
            'Independently_Calculated_Value': "68.07% under marginal covariance decomposition (w_i * Cov(X_i, S) / Var(S)). Unique variances account for only 40.58%; shared cross-covariance accounts for 59.42%.",
            'Status': "Confirmed with qualification",
            'Explanation': "The 68.07% figure is mathematically correct under portfolio marginal covariance decomposition, but shared covariance (21.85% between SR and Exec alone) is allocated proportionally to formula weights."
        },
        {
            'Claim': "Empirical Bayes optimal shrinkage parameters (K_bat = 38.2, K_bow = 29.0)",
            'Step_11_Value': "K_bat = 38.2, K_bow = 29.0; claimed K=50 is excessive shrinkage",
            'Independently_Calculated_Value': "In time-aware out-of-sample validation (473 train matches vs 316 test matches), K=50 outperforms K=38 and K=29 in RMSE (33.59 vs 34.00 bat; 2.10 vs 2.15 bow) and MAE (27.34 vs 27.69 bat; 1.67 vs 1.74 bow).",
            'Status': "Incorrect",
            'Explanation': "Step 11 proposed values were stylized textbook ratios based on assumed constants without predictive validation. Empirical forecasting proves K=50 provides necessary regularization against noise."
        },
        {
            'Claim': "Shubham Dubey and Simarjeet Singh outlier dependence",
            'Step_11_Value': "Dubey: 53.1% runs in 2 matches; Simarjeet: 75.0% wickets in 2 matches",
            'Independently_Calculated_Value': "Dubey: exactly 53.06% in 2 matches; Simarjeet: exactly 75.00% in 2 matches. However, distinct match count strongly correlates with concentration (r = -0.707 bat, r = -0.568 bow).",
            'Status': "Confirmed with qualification",
            'Explanation': "The concentration figures are exact, but are mathematically driven by low match counts (Dubey 14 matches, Simarjeet 9 matches) rather than unique player inconsistency. Peer groups with similar match counts show identical concentration."
        },
        {
            'Claim': "MS Dhoni phase exposure and strike rates",
            'Step_11_Value': "78.4% death balls, Death SR = 197.37, Middle SR = 65.79, Overall SR = 170.62",
            'Independently_Calculated_Value': "152 of 194 balls (78.35%), Death SR = 197.37, Middle SR = 65.79, Overall SR = 170.62",
            'Status': "Confirmed",
            'Explanation': "100% numerically verified. Dhoni's middle-overs Z-score is -1.42, while death-overs Z-score is +1.27. Pooling unweighted deliveries allows death-overs dominance to swamp middle-overs accumulation."
        },
        {
            'Claim': "Target reconstruction sensitivity rank correlations",
            'Step_11_Value': "Spearman rho = 0.9945 (batters), rho = 0.9852 (bowlers)",
            'Independently_Calculated_Value': "Spearman rho = 0.9945 across 116 common Tier 1 batters; rho = 0.9852 across 111 common Tier 1 bowlers",
            'Status': "Confirmed",
            'Explanation': "Verified on common Tier 1 players. Shoriful Islam (61 to 59 balls) dropped below 60 balls and was ejected to Tier 2."
        },
        {
            'Claim': "Jamie Overton and Nasum Ahmed threshold cliff impact",
            'Step_11_Value': "Overton: 59 balls, BRS 79.54 (potential #6); Nasum: 55 balls, BoRS 88.84 (potential #2)",
            'Independently_Calculated_Value': "Overton: 59 balls, BRS 79.54 (would rank #6 under cutoff 50); Nasum: 55 balls, BoRS 88.84 (would rank #2 under cutoff 50)",
            'Status': "Confirmed",
            'Explanation': "Verified by re-ranking under a 50-ball threshold. Demonstrates the discontinuity inherent in knife-edge qualification cutoffs."
        },
        {
            'Claim': "Bowling variance decomposition fidelity to nominal weights",
            'Step_11_Value': "Econ 39.88%, Wk 23.11%, Dot 21.80%, Diff 15.21%",
            'Independently_Calculated_Value': "Econ 39.88%, Wk 23.11%, Dot 21.80%, Diff 15.21%",
            'Status': "Confirmed",
            'Explanation': "Verified via covariance matrix multiplication in Tier 1. Bowling components are orthogonal and variance contributions match nominal design weights."
        },
        {
            'Claim': "Phase standardization should be adopted for overall rankings",
            'Step_11_Value': "Proposed phase-standardized z-scores for overall v3.0 model",
            'Independently_Calculated_Value': "Phase standardization drops Dhoni from #1 to #21, converting an absolute clutch finishing metric into a role-relative versatility score.",
            'Status': "Confirmed with qualification",
            'Explanation': "Phase standardization conflates specialist roles with generalist versatility. In T20 cricket, death-overs finishing is objectively higher leverage. Phase-specific rankings are preferable to distorting the overall leaderboard."
        },
        {
            'Claim': "Sigmoidal continuous confidence weighting should replace cutoffs",
            'Step_11_Value': "Recommended continuous sigmoid function W(N) = 1 / (1 + exp(-(N-50)/12))",
            'Independently_Calculated_Value': "A sigmoid multiplier arbitrarily discounts small-sample players toward zero rather than shrinking them to the population mean (which Bayesian shrinkage already does).",
            'Status': "Confirmed with qualification",
            'Explanation': "Replacing hard cliffs is desirable, but continuous confidence intervals or published tier boundaries are statistically superior to multiplying scores by a sigmoid curve."
        }
    ]
    
    df_register = pd.DataFrame(register_records)
    csv_out = OUTPUT_DIR / "step_11_discrepancy_register.csv"
    df_register.to_csv(csv_out, index=False)
    print(f"Generated discrepancy register with {len(df_register)} audited claims.")
    print(f"Saved discrepancy register to: {csv_out}")
    
    # Summary of Register
    print("\n--- Summary of Register Statuses ---")
    print(df_register['Status'].value_counts())

if __name__ == "__main__":
    run_investigation()
