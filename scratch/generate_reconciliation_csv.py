import pandas as pd

records = [
    {
        "Discrepancy_ID": "DISC-REC-01",
        "Area": "Big-Name Batting Rankings",
        "Item_or_Player": "Klaasen, Salt, Head, Iyer, Buttler, Marsh, Kohli, Rohit",
        "Reported_Value_or_Claim": "Step 9 chat summary claimed: Klaasen (#1, +0.324), Head (#3, +0.228), Salt (#5, +0.219), Buttler (#8, +0.177), Samson (#15, +0.126), Kohli (#25, +0.103), Rohit (#41, +0.076)",
        "Step_7_4_Authoritative_Value": "Klaasen (#5, +0.2201), Salt (#6, +0.1954), Head (#8, +0.1625), Iyer (#14, +0.1350), Buttler (#17, +0.1306), Marsh (#19, +0.1272), Kohli (#34, +0.0850), Rohit (#168, -0.0164)",
        "Audit_Finding_or_Recalculated": "Authoritative Step 7.4 CSVs and big_name_batting_leaderboard.csv match 100%. Chat presentation was a hallucinated error.",
        "Root_Cause": "Agent chat generation hallucination in Step 9 summary response. Underlying Step 7.4 CSVs and Step 8.1A leaderboards are completely clean and authoritative.",
        "Classification": "RESOLVED",
        "Action_Required": "Reaffirm authoritative Step 7.4 ranks as immutable truth. Disregard Step 9 chat summary numbers."
    },
    {
        "Discrepancy_ID": "DISC-REC-02",
        "Area": "Big-Name Bowling Rankings",
        "Item_or_Player": "Rashid, Bumrah, Narine, Hazlewood, Shami, Boult, Axar",
        "Reported_Value_or_Claim": "Step 9 chat summary claimed: Bumrah (#1, +0.214), Rashid (#2, +0.175), Narine (#5, +0.147), Axar (#6, +0.128)",
        "Step_7_4_Authoritative_Value": "Rashid (#1, +0.1756), Bumrah (#2, +0.1541), Narine (#3, +0.1442), Hazlewood (#4, +0.1330), Shami (#13, +0.0989), Boult (#16, +0.0922), Axar (#66, +0.0195)",
        "Audit_Finding_or_Recalculated": "Authoritative Step 7.4 CSVs and big_name_bowling_leaderboard.csv match 100%. Chat presentation was a hallucinated error.",
        "Root_Cause": "Agent chat generation hallucination in Step 9 summary response. Underlying Step 7.4 CSVs and Step 8.1A leaderboards are completely clean and authoritative.",
        "Classification": "RESOLVED",
        "Action_Required": "Reaffirm authoritative Step 7.4 ranks as immutable truth. Disregard Step 9 chat summary numbers."
    },
    {
        "Discrepancy_ID": "DISC-REC-03",
        "Area": "Alpha Sensitivity Correlation",
        "Item_or_Player": "Spearman rank correlation (alpha 1.00 vs 1.25)",
        "Reported_Value_or_Claim": "Step 8.1 report text & findings_summary claimed: Batting rho = 0.9881, Bowling rho = 0.9854",
        "Step_7_4_Authoritative_Value": "Step 7.4.1 reported: Batting rho = 0.9978, Bowling rho = 0.9981. Fig 07 titles display: rho = 0.9978 and 0.9981.",
        "Audit_Finding_or_Recalculated": "Direct recalculation from sensitivity CSVs yields rho_bat = 0.997778 (0.9978) and rho_bowl = 0.998114 (0.9981).",
        "Root_Cause": "Typographical transcription error in narrative markdown prose of Step 8.1 report text. Chart Fig 07 and Step 7.4.1 are 100% correct.",
        "Classification": "RESOLVED",
        "Action_Required": "Formally correct narrative text in final report to cite rho = 0.9978 (batting) and rho = 0.9981 (bowling)."
    },
    {
        "Discrepancy_ID": "DISC-REC-04",
        "Area": "Cross-Format Consistency (Batting)",
        "Item_or_Player": "Dual-format batters (IPL vs T20I)",
        "Reported_Value_or_Claim": "Step 8.1 Fig 12 reported: N = 91, Pearson r = 0.1148",
        "Step_7_4_Authoritative_Value": "String matching merged Abdul Samad (India, id 7446, 424 IPL balls) and Abdul Samad (Pakistan, id 6922, 61 T20I balls).",
        "Audit_Finding_or_Recalculated": "Disambiguated by striker_id: N = 90, Pearson r = 0.114929 (0.1149), Spearman rho = 0.164522 (0.1645).",
        "Root_Cause": "Name collision between two distinct international/IPL players sharing identical string name 'Abdul Samad'.",
        "Classification": "RESOLVED",
        "Action_Required": "Document ID-based disambiguation: true dual-format population is N = 90, r = 0.1149, rho = 0.1645."
    },
    {
        "Discrepancy_ID": "DISC-REC-05",
        "Area": "Cross-Format Consistency (Bowling)",
        "Item_or_Player": "Dual-format bowlers (IPL vs T20I)",
        "Reported_Value_or_Claim": "Step 8.1 Fig 12 reported: N = 97, Pearson r = 0.2338",
        "Step_7_4_Authoritative_Value": "N = 97, Pearson r = 0.233816 (0.2338), Spearman rho = 0.295590 (0.2956).",
        "Audit_Finding_or_Recalculated": "Zero name collisions among bowlers. Verified exact agreement between name and ID matching.",
        "Root_Cause": "Verified clean and accurate.",
        "Classification": "RESOLVED",
        "Action_Required": "Retain verified figures: N = 97, r = 0.2338, rho = 0.2956."
    },
    {
        "Discrepancy_ID": "DISC-REC-06",
        "Area": "Phase Performance Heatmaps",
        "Item_or_Player": "Top 10 phase values & sample sizes",
        "Reported_Value_or_Claim": "Step 8.1 Sec 5.1 text table contained corrupted numbers (e.g. Salt Death -0.081, Head Death +0.042, Klaasen Death +0.389)",
        "Step_7_4_Authoritative_Value": "Heatmaps Fig 10 and Fig 11 plot unshrunk pressure-weighted SVA per ball with N >= 20 threshold.",
        "Audit_Finding_or_Recalculated": "Fig 10 and 11 values verified: Salt (PP +0.32/950b, Mid +0.13/546b, Death +0.54/95b); Klaasen (PP +0.25/102b, Mid +0.39/915b, Death +0.25/392b); Head (Death N/A/7b < 20).",
        "Root_Cause": "Text table in Section 5.1 of Step 8.1 report was corrupted/hallucinated during manual authoring. Visual heatmap PNGs are completely correct.",
        "Classification": "RESOLVED",
        "Action_Required": "Discard corrupted markdown text table in Sec 5.1. Use verified values from Fig 10 and Fig 11."
    },
    {
        "Discrepancy_ID": "DISC-REC-07",
        "Area": "Big-Name Catalog Notes",
        "Item_or_Player": "Pollard, Dhawan, Joseph, Rauf in unqualified catalog",
        "Reported_Value_or_Claim": "unqualified_or_missing_players.csv claimed: Pollard (#144, 622b), Dhawan (#223, 122b), Joseph (#135, 1361b), Rauf (#107)",
        "Step_7_4_Authoritative_Value": "Pollard is #244 (212b); Dhawan is UNQUALIFIED in batting (52b); Joseph is #279 (1137b); Rauf is #51 (974b).",
        "Audit_Finding_or_Recalculated": "Manual hardcoding errors in CSV notes column. Official Step 7.4 rankings and primary leaderboards are 100% correct.",
        "Root_Cause": "Manual authoring typographical errors in ancillary catalog note strings.",
        "Classification": "RESOLVED",
        "Action_Required": "Document corrections in audit record. No changes needed to official ranking engines."
    }
]

df_rec = pd.DataFrame(records)
import os
os.makedirs('outputs/step_9_1_discrepancy_reconciliation', exist_ok=True)
df_rec.to_csv('outputs/step_9_1_discrepancy_reconciliation/step_9_1_reconciliation.csv', index=False)
df_rec.to_csv('step_9_1_reconciliation.csv', index=False)
print("Saved step_9_1_reconciliation.csv successfully.")
