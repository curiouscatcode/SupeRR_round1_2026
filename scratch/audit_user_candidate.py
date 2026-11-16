import pymupdf
import re

pdf_path = 'scratch/step_10_user_candidate_final.pdf'
doc = pymupdf.open(pdf_path)

print("=" * 80)
print(f"AUDITING CANDIDATE PDF: {pdf_path}")
print("=" * 80)
print(f"Total Page Count: {len(doc)} (Expected: 12)")
assert len(doc) == 12, f"Expected 12 pages, got {len(doc)}"

# Check images per page
total_images = 0
for i, page in enumerate(doc):
    imgs = page.get_images()
    total_images += len(imgs)
    text = page.get_text()
    has_bracket_image = '[image]' in text.lower()
    print(f"Page {i+1:2d}: {len(imgs)} images, text length = {len(text):4d}, contains '[image]': {has_bracket_image}")
    assert not has_bracket_image, f"Page {i+1} still contains fallback '[image]' text!"

print(f"\nTotal Embedded Images across PDF: {total_images}")

# Check Page 1: Author & TL;DR Box
p1_text = doc[0].get_text()
print("\n--- Page 1 Checks ---")
assert "Amit N Suthar" in p1_text, "Author 'Amit N Suthar' missing from Page 1!"
print("  [OK] Author 'Amit N Suthar' present on Page 1.")
assert "Executive TL;DR" in p1_text or "TL;DR" in p1_text, "TL;DR title missing from Page 1!"
print("  [OK] Executive TL;DR title present on Page 1.")

for pt in ["a. Our Methodology", "b. Our Formula", "c. Key Results", "d. Flaws & Limitations", "e. Conclusion"]:
    assert pt in p1_text, f"TL;DR point '{pt}' missing from Page 1!"
    print(f"  [OK] TL;DR point '{pt}' verified.")

# Check Page 2: 20 Table Rows
p2 = doc[1]
p2_blocks = p2.get_text('blocks')
p2_rows = [b[4].strip().split('\n') for b in p2_blocks if b[4].strip().startswith('#')]
print(f"\n--- Page 2 Checks ---")
print(f"Extracted {len(p2_rows)} leaderboard rows on Page 2 (Expected 20).")
assert len(p2_rows) == 20, f"Expected 20 row blocks on Page 2, got {len(p2_rows)}"
assert p2_rows[0][1].strip() == "Vaibhav Sooryavanshi"
assert p2_rows[10][1].strip() == "Rashid Khan"
print("  [OK] Leaderboard rows for Vaibhav Sooryavanshi (#1 Bat) and Rashid Khan (#1 Bowl) verified.")

# Check Page 12: Marquee Stars and Section 9
p12 = doc[11]
p12_blocks = p12.get_text('blocks')
p12_text = p12.get_text()

print("\n--- Page 12 Checks ---")
marquee_rows = [b[4].strip().split('\n') for b in p12_blocks if ('Batting' in b[4] or 'Bowling' in b[4]) and ('#' in b[4])]
print(f"Extracted {len(marquee_rows)} marquee star rows on Page 12 (Expected 15).")
assert len(marquee_rows) == 15, f"Expected 15 marquee rows on Page 12, got {len(marquee_rows)}"
print("  [OK] 15 Marquee Star rows verified on Page 12.")

# Check Section 9 lines
print("\nChecking Section 9 points on separate lines:")
lines = p12_text.splitlines()
pt1_found = False
pt2_found = False
pt3_found = False

for l in lines:
    if l.strip().startswith("1. Striker Run-Out Attribution:"):
        pt1_found = True
        print(f"  [OK] Point 1 line: {l.strip()[:60]}...")
    elif l.strip().startswith("2. Residual Environmental Variance:"):
        pt2_found = True
        print(f"  [OK] Point 2 line: {l.strip()[:60]}...")
    elif l.strip().startswith("3. Discrete Empirical Baseline:"):
        pt3_found = True
        print(f"  [OK] Point 3 line: {l.strip()[:60]}...")

assert pt1_found and pt2_found and pt3_found, "Points 1, 2, 3 not found on distinct lines in Section 9!"

print("\n" + "=" * 80)
print("ALL AUDIT CHECKS PASSED ON CANDIDATE PDF!")
print("=" * 80)
