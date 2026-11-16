import re
import fitz

with open('scratch/build_step10_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

print("=== FORMULA BOXES IN build_step10_pdf.py ===")
for m in re.finditer(r'<div class="formula-box">.*?</div>', text, re.DOTALL):
    print(m.group(0))
    print('='*40)

print("\n=== SEARCHING FOR BLUE RECTANGLES / DRAWINGS IN PDF ===")
doc = fitz.open('outputs/step_10_methodology_report/step_10_methodology_report.pdf')
for i, page in enumerate(doc):
    drawings = page.get_drawings()
    for d in drawings:
        fill = d.get('fill')
        rect = d.get('rect')
        # Check if fill is blue (B > R and B > G and B > 0.6)
        if fill and len(fill) == 3:
            r, g, b = fill
            if b > 0.6 and b > r + 0.2 and b > g + 0.1:
                print(f"Page {i+1}: Blue drawing fill={fill}, rect={rect}")
                words = page.get_text("words")
                overlap_words = [w[4] for w in words if fitz.Rect(w[:4]).intersects(rect)]
                if overlap_words:
                    print(f"   --> OVERLAPPING WORDS ({len(overlap_words)}): {' '.join(overlap_words[:10])}")
