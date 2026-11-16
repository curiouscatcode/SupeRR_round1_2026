import fitz

doc = fitz.open('outputs/step_10_methodology_report/step_10_methodology_report.pdf')

for p_idx, page in enumerate(doc):
    drawings = page.get_drawings()
    unique_fills = set()
    unique_colors = set()
    for d in drawings:
        if d.get('fill'):
            unique_fills.add(tuple(round(x, 3) for x in d.get('fill')))
        if d.get('color'):
            unique_colors.add(tuple(round(x, 3) for x in d.get('color')))
    print(f"Page {p_idx+1}: fills = {unique_fills}, colors = {unique_colors}")
