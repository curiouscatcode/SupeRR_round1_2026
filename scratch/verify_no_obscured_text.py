import pymupdf

doc = pymupdf.open('outputs/step_10_methodology_report/step_10_methodology_report.pdf')

print("=== CHECKING FOR DRAWINGS & ARTIFACTS ACROSS ALL 14 PAGES ===")
total_overlapped_words = 0

for pno in range(len(doc)):
    page = doc[pno]
    drawings = page.get_drawings()
    # Check for any drawing with fill or color that is blue
    blue_drawings = []
    for d in drawings:
        fill = d.get('fill')
        color = d.get('color')
        if fill and len(fill) == 3:
            r, g, b = fill
            if b > 0.4 and (b > r + 0.1 or b > g + 0.1):
                blue_drawings.append(d)
        elif color and len(color) == 3:
            r, g, b = color
            if b > 0.4 and (b > r + 0.1 or b > g + 0.1):
                blue_drawings.append(d)

    words = page.get_text('words')
    overlapped = []
    for d in blue_drawings:
        r = d['rect']
        # if the rect has area > 50 (i.e. not a thin 1pt border)
        if (r.x1 - r.x0) > 10 and (r.y1 - r.y0) > 5:
            for w in words:
                if pymupdf.Rect(w[:4]).intersects(r):
                    overlapped.append(w[4])
    total_overlapped_words += len(overlapped)
    print(f"Page {pno+1}: {len(drawings)} total drawings, {len(blue_drawings)} blue drawings, {len(overlapped)} overlapped words.")
    if overlapped:
        print(f"  WARNING: Overlapped text on Page {pno+1}: {' '.join(overlapped[:15])}")

print(f"\nFinal Verdict: Total overlapped words across entire document = {total_overlapped_words}")
if total_overlapped_words == 0:
    print("SUCCESS: ZERO TEXT IS COVERED OR OBSCURED BY BLUE RECTANGLES!")
