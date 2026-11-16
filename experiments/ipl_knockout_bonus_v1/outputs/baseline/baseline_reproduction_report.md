# Stage 2: Strict 1.00x Baseline Reproduction Audit

**Experiment:** IPL Knockout Bonus (v1)  
**Stage:** Stage 2 — Isolated Pipeline Baseline Verification  
**Author:** Antigravity (Google DeepMind Agentic System)  
**Date:** November 15, 2026  
**Audit Status:** **PASS** (Zero discrepancies across all 297 batters and 292 bowlers)  

---

## 1. Reproduction Methodology

The isolated experiment engine re-implemented the entire frozen Step 7.4 scoring framework:
1. **Batting:** Value Added $v_{\text{bat}}$ per ball faced evaluated against 36-cell empirical baselines, situational wicket valuation $\lambda_{\text{eff}}$, Kish ESS, and Empirical Bayes shrinkage ($K_{\text{bat}} = 600$).
2. **Bowling:** Value Added $v_{\text{bowl}}$ evaluated under legal-ball quota accounting, 36-cell baselines, situational wicket valuation $\lambda_{\text{eff}}$, Kish ESS, and Empirical Bayes shrinkage ($K_{\text{bowl}} = 500$).
3. **Knockout Multiplier:** Set strictly to $1.00\times$ across all deliveries.

---

## 2. Quantitative Verification Results

| Evaluation Metric | Batting Population ($N=297$) | Bowling Population ($N=292$) | Certification Standard | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Population Count** | 297 | 292 | Exact Match | **PASS** |
| **Maximum Rank Discrepancy** | `0` | `0` | Exactly 0 | **PASS** |
| **Max Shrunk Score $|\Delta|$** | `0.00e+00` | `0.00e+00` | $< 1.0 \times 10^{-12}$ | **PASS** |
| **Max Raw Score $|\Delta|$** | `0.00e+00` | `0.00e+00` | $< 1.0 \times 10^{-12}$ | **PASS** |
| **Max Kish ESS $|\Delta|$** | `0.00e+00` | `0.00e+00` | $< 1.0 \times 10^{-12}$ | **PASS** |
| **Opportunity Counts (Raw/P50)** | 0 mismatches | 0 mismatches | Exact Integer Match | **PASS** |

---

## 3. Top 10 Recalculated vs. Frozen Comparison

### Batting Top 10 Leaderboard
```
Rank Player                    Recalc Shrunk   Frozen Shrunk   Delta        ESS       
--------------------------------------------------------------------------------
1    Vaibhav Sooryavanshi      0.348711        0.348711        0.00e+00     506.9     
2    Suryakumar Yadav          0.281876        0.281876        0.00e+00     2287.2    
3    Abhishek Sharma           0.270324        0.270324        0.00e+00     1923.3    
4    Tim David                 0.257085        0.257085        0.00e+00     980.6     
5    Heinrich Klaasen          0.220103        0.220103        0.00e+00     1142.0    
6    Phil Salt                 0.195396        0.195396        0.00e+00     1364.7    
7    Namboori Tilak Varma      0.174500        0.174500        0.00e+00     1968.9    
8    Travis Head               0.162485        0.162485        0.00e+00     988.6     
9    Andre Russell             0.157881        0.157881        0.00e+00     570.7     
10   Reeza Hendricks           0.156353        0.156353        0.00e+00     715.9     
```

### Bowling Top 10 Leaderboard
```
Rank Player                    Recalc Shrunk   Frozen Shrunk   Delta        ESS       
--------------------------------------------------------------------------------
1    Rashid Khan               0.175625        0.175625        0.00e+00     2245.9    
2    Jasprit Bumrah            0.154096        0.154096        0.00e+00     1369.7    
3    Sunil Narine              0.144171        0.144171        0.00e+00     1246.3    
4    Josh Hazlewood            0.133038        0.133038        0.00e+00     1159.5    
5    Wanindu Hasaranga         0.118358        0.118358        0.00e+00     1675.4    
6    Bhuvneshwar Kumar         0.106504        0.106504        0.00e+00     1875.7    
7    Abrar Ahmed               0.105797        0.105797        0.00e+00     604.7     
8    Kuldeep Yadav             0.102696        0.102696        0.00e+00     1608.6    
9    Mahedi Hasan              0.102540        0.102540        0.00e+00     760.3     
10   Mujeeb Ur Rahman          0.102403        0.102403        0.00e+00     686.6     
```

---

## 4. Certification Sign-off

The isolated recalculation pipeline demonstrates machine-precision reproduction ($|\Delta| < 10^{-15}$) across all 589 player evaluations.
**Conclusion:** The baseline calculation engine in `experiments/ipl_knockout_bonus_v1/` is completely verified and certified for the subsequent multiplier experiments ($1.10\times, 1.20\times, 1.25\times$).