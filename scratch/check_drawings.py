import fitz

doc = fitz.open('outputs/step_10_methodology_report/step_10_methodology_report.pdf')
page = doc[3] # page 4
drawings = page.get_drawings()
c = 0
for d in drawings:
    fill = d.get('fill')
    if fill and abs(fill[0] - 0.9215) < 0.01:
        print(f"Drawing {c}: rect={d.get('rect')}, items={d.get('items')}")
        c += 1
