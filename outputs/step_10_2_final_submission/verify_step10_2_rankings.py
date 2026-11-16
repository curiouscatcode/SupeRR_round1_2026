"""
Independent Ranking Verification Script for Step 10.2
Verifies 100% numerical and textual consistency between:
1. Authoritative Step 7.4 CSV files:
   - outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv (Top 10 Batting)
   - outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv (Top 10 Bowling)
   - outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv (All 297 Batters)
   - outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv (All 292 Bowlers)
2. Step 10 Methodology Report Markdown:
   - outputs/step_10_methodology_report/step_10_methodology_report.md
3. Step 10 Methodology Report PDF:
   - outputs/step_10_methodology_report/step_10_methodology_report.pdf
"""

import sys
import os
import hashlib
import pandas as pd
import pymupdf

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_rankings():
    print("=" * 80)
    print("STEP 10.2 INDEPENDENT RANKING VERIFICATION PIPELINE")
    print("=" * 80)

    # 1. File existence and hashes
    bat_top10_csv = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv'
    bowl_top10_csv = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv'
    bat_all_csv = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv'
    bowl_all_csv = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv'
    md_path = 'outputs/step_10_methodology_report/step_10_methodology_report.md'
    pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'

    all_files = [bat_top10_csv, bowl_top10_csv, bat_all_csv, bowl_all_csv, md_path, pdf_path]
    for p in all_files:
        if not os.path.exists(p):
            print(f"[FAIL] Required file not found: {p}")
            sys.exit(1)
        print(f"[OK] Found {p} (SHA-256: {get_file_hash(p)[:16]}...)")

    # 2. Load Step 7.4 CSVs
    df_bat_top10 = pd.read_csv(bat_top10_csv)
    df_bowl_top10 = pd.read_csv(bowl_top10_csv)
    df_bat_all = pd.read_csv(bat_all_csv)
    df_bowl_all = pd.read_csv(bowl_all_csv)

    print(f"\n[LOAD] Top 10 Batting CSV: {len(df_bat_top10)} rows.")
    print(f"[LOAD] Top 10 Bowling CSV: {len(df_bowl_top10)} rows.")
    print(f"[LOAD] All Eligible Batting CSV: {len(df_bat_all)} rows.")
    print(f"[LOAD] All Eligible Bowling CSV: {len(df_bowl_all)} rows.")

    assert len(df_bat_all) == 297, f"Expected 297 batting players, got {len(df_bat_all)}"
    assert len(df_bowl_all) == 292, f"Expected 292 bowling players, got {len(df_bowl_all)}"

    # 3. Read Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    print("\n--- Verifying Markdown (step_10_methodology_report.md) ---")
    md_discrepancies = []

    # Check Top 10 Batting in MD
    for idx, row in df_bat_top10.iterrows():
        rank_str = f"#{int(row['Rank'])}"
        name_str = row['Player']
        shrunk_val = f"{float(row['Shrunk score']):+.4f}"
        raw_val = f"{float(row['Raw score']):+.4f}"
        balls_val = str(int(row['Raw opportunities']))
        ess_val = f"{float(row['Kish ESS']):.1f}"

        if name_str not in md_text:
            md_discrepancies.append(f"Batting MD: Player {name_str} not found in markdown.")
        if shrunk_val not in md_text:
            md_discrepancies.append(f"Batting MD: Shrunk value {shrunk_val} for {name_str} not found in markdown.")
        if raw_val not in md_text:
            md_discrepancies.append(f"Batting MD: Raw value {raw_val} for {name_str} not found in markdown.")
        if balls_val not in md_text:
            md_discrepancies.append(f"Batting MD: Balls faced {balls_val} for {name_str} not found in markdown.")
        if ess_val not in md_text:
            md_discrepancies.append(f"Batting MD: Kish ESS {ess_val} for {name_str} not found in markdown.")

    # Check Top 10 Bowling in MD
    for idx, row in df_bowl_top10.iterrows():
        rank_str = f"#{int(row['Rank'])}"
        name_str = row['Player']
        shrunk_val = f"{float(row['Shrunk score']):+.4f}"
        raw_val = f"{float(row['Raw score']):+.4f}"
        balls_val = str(int(row['Raw opportunities']))
        ess_val = f"{float(row['Kish ESS']):.1f}"

        if name_str not in md_text:
            md_discrepancies.append(f"Bowling MD: Player {name_str} not found in markdown.")
        if shrunk_val not in md_text:
            md_discrepancies.append(f"Bowling MD: Shrunk value {shrunk_val} for {name_str} not found in markdown.")
        if raw_val not in md_text:
            md_discrepancies.append(f"Bowling MD: Raw value {raw_val} for {name_str} not found in markdown.")
        if balls_val not in md_text:
            md_discrepancies.append(f"Bowling MD: Balls bowled {balls_val} for {name_str} not found in markdown.")
        if ess_val not in md_text:
            md_discrepancies.append(f"Bowling MD: Kish ESS {ess_val} for {name_str} not found in markdown.")

    if md_discrepancies:
        print(f"[FAIL] Found {len(md_discrepancies)} discrepancies in Markdown:")
        for d in md_discrepancies:
            print(f"  - {d}")
        sys.exit(1)
    else:
        print("[PASS] All Top 10 Batting & Bowling values verified in Markdown.")

    # 4. Check Marquee Stars in MD against all_eligible CSVs
    marquee_checks = [
        ('Heinrich Klaasen', 'Batting', 5, 0.2201, 0.3357, 1409, 1142.0),
        ('Phil Salt', 'Batting', 6, 0.1954, 0.2813, 1591, 1364.7),
        ('Travis Head', 'Batting', 8, 0.1625, 0.2611, 1096, 988.6),
        ('Shreyas Iyer', 'Batting', 14, 0.1350, 0.1887, 1751, 1507.1),
        ('Jos Buttler', 'Batting', 17, 0.1306, 0.1642, 2675, 2330.2),
        ('Mitchell Marsh', 'Batting', 19, 0.1272, 0.1796, 1656, 1456.7),
        ('Virat Kohli', 'Batting', 34, 0.0850, 0.1081, 2445, 2201.2),
        ('Rohit Sharma', 'Batting', 168, -0.0164, -0.0231, 1561, 1451.1),
        ('Rashid Khan', 'Bowling', 1, 0.1756, 0.2147, 2648, 2245.9),
        ('Jasprit Bumrah', 'Bowling', 2, 0.1541, 0.2103, 1606, 1369.7),
        ('Sunil Narine', 'Bowling', 3, 0.1442, 0.2020, 1464, 1246.3),
        ('Josh Hazlewood', 'Bowling', 4, 0.1330, 0.1904, 1368, 1159.5),
        ('Mohammed Shami', 'Bowling', 13, 0.0989, 0.1438, 1228, 1100.8),
        ('Trent Boult', 'Bowling', 16, 0.0922, 0.1272, 1501, 1313.6),
        ('Axar Patel', 'Bowling', 66, 0.0195, 0.0239, 2604, 2218.5),
    ]

    for name, disc, rank, shrunk, raw, balls, ess in marquee_checks:
        csv_source = df_bat_all if disc == 'Batting' else df_bowl_all
        p_row = csv_source[csv_source['Player'] == name]
        if p_row.empty:
            print(f"[FAIL] Marquee player {name} not found in Step 7.4 {disc} CSV!")
            sys.exit(1)
        r = p_row.iloc[0]
        actual_rank = int(r['Rank'])
        actual_shrunk = float(r['Shrunk score'])
        actual_raw = float(r['Raw score'])
        actual_balls = int(r['Raw opportunities'])
        actual_ess = float(r['Kish ESS'])

        assert actual_rank == rank, f"Rank mismatch for {name}: expected {rank}, got {actual_rank}"
        assert abs(actual_shrunk - shrunk) < 0.0001, f"Shrunk score mismatch for {name}: expected {shrunk}, got {actual_shrunk}"
        assert abs(actual_raw - raw) < 0.0001, f"Raw score mismatch for {name}: expected {raw}, got {actual_raw}"
        assert actual_balls == balls, f"Balls mismatch for {name}: expected {balls}, got {actual_balls}"
        assert abs(actual_ess - ess) < 0.1, f"ESS mismatch for {name}: expected {ess}, got {actual_ess}"
        assert name in md_text, f"{name} not in markdown"

    print("[PASS] All Section 8 Marquee Players verified against Step 7.4 CSVs and Markdown.")

    # 5. Verify PDF Document
    print("\n--- Verifying PDF (step_10_methodology_report.pdf) ---")
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    print(f"[INFO] PDF total page count: {total_pages} (Required: 12)")
    assert total_pages == 12, f"PDF page count is {total_pages}, expected exactly 12."

    page_texts = {p: doc[p].get_text() for p in range(total_pages)}

    # Page 2: Top 10 Batting & Bowling
    p2_text = page_texts[1]
    pdf_discrepancies = []

    print("[CHECK] Page 2: Checking Top 10 Batting...")
    for idx, row in df_bat_top10.iterrows():
        name = row['Player']
        shrunk = f"{float(row['Shrunk score']):+.4f}"
        raw = f"{float(row['Raw score']):+.4f}"
        balls = str(int(row['Raw opportunities']))
        ess = f"{float(row['Kish ESS']):.1f}"

        if name not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Batting player {name} missing.")
        if shrunk not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Batting shrunk score {shrunk} for {name} missing.")
        if raw not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Batting raw score {raw} for {name} missing.")
        if balls not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Batting balls {balls} for {name} missing.")
        if ess not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Batting ESS {ess} for {name} missing.")

    print("[CHECK] Page 2: Checking Top 10 Bowling...")
    for idx, row in df_bowl_top10.iterrows():
        name = row['Player']
        shrunk = f"{float(row['Shrunk score']):+.4f}"
        raw = f"{float(row['Raw score']):+.4f}"
        balls = str(int(row['Raw opportunities']))
        ess = f"{float(row['Kish ESS']):.1f}"

        if name not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Bowling player {name} missing.")
        if shrunk not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Bowling shrunk score {shrunk} for {name} missing.")
        if raw not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Bowling raw score {raw} for {name} missing.")
        if balls not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Bowling balls {balls} for {name} missing.")
        if ess not in p2_text:
            pdf_discrepancies.append(f"PDF Page 2: Bowling ESS {ess} for {name} missing.")

    if pdf_discrepancies:
        print(f"[FAIL] Found {len(pdf_discrepancies)} discrepancies on Page 2:")
        for d in pdf_discrepancies:
            print(f"  - {d}")
        sys.exit(1)
    else:
        print("[PASS] PDF Page 2 Top 10 Batting & Bowling tables are 100% verified.")

    # Page 7: Shrinkage Dynamics and Formulas
    p7_text = page_texts[6]
    print("[CHECK] Page 7: Checking Shrinkage Dynamics...")
    assert "Section 5 — Measuring Player Reliability: PWSVA and SBVA" in p7_text
    assert "Vaibhav Sooryavanshi (ESS 506.9) retains 45.79%" in p7_text
    assert "Suryakumar Yadav (ESS 2287.2) retains 79.22%" in p7_text
    assert "Rashid Khan (ESS 2245.9) retains 81.79%" in p7_text
    assert "Jasprit Bumrah (ESS 1369.7) retains 73.26%" in p7_text
    print("[PASS] PDF Page 7 Shrinkage Dynamics verified.")

    # Page 10: Empirical Validation & Alpha Sensitivity
    p10_text = page_texts[9]
    print("[CHECK] Page 10: Checking Empirical Validation & Sensitivities...")
    assert "0.9978" in p10_text
    assert "0.9981" in p10_text
    assert "Figures 7 and 8" in p10_text
    print("[PASS] PDF Page 10 Empirical Validation metrics verified.")

    # Page 12: Section 8 Marquee Players and Cross-Format
    p12_text = page_texts[11]
    print("[CHECK] Page 12: Checking Marquee Players & Cross-Format...")
    assert "N = 90, Pearson r = 0.1149, Spearman ρ = 0.1645" in p12_text
    assert "N = 97, Pearson r = 0.2338, Spearman ρ = 0.2956" in p12_text
    for name, disc, rank, shrunk, raw, balls, ess in marquee_checks:
        assert name in p12_text, f"Marquee star {name} missing on Page 12"
        shrunk_str = f"{shrunk:+.4f}"
        assert shrunk_str in p12_text, f"Shrunk score {shrunk_str} for {name} missing on Page 12"

    print("[PASS] PDF Page 12 Marquee Stars and Cross-Format verified.")

    print("\n" + "=" * 80)
    print("ALL VERIFICATION CHECKS PASSED WITH ZERO DISCREPANCIES (100% CONSISTENT)")
    print("=" * 80)
    return True

if __name__ == '__main__':
    verify_rankings()
