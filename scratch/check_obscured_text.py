import fitz

doc = fitz.open('outputs/step_10_methodology_report/step_10_methodology_report.pdf')

for pno in range(len(doc)):
    page = doc[pno]
    drawings = page.get_drawings()
    blue_table_drawings = [
        d for d in drawings 
        if d.get('fill') == (0.10196078568696976, 0.21176470816135406, 0.364705890417099)
    ]
    words = page.get_text('words')
    overlapped = []
    for d in blue_table_drawings:
        r = d['rect']
        for w in words:
            if fitz.Rect(w[:4]).intersects(r):
                overlapped.append(w[4])
    print(f"Page {pno+1}: {len(blue_table_drawings)} blue table drawings. Overlapped words: {len(overlapped)}")
    if overlapped:
        print(f"   Sample overlapped text: {' '.join(overlapped[:20])}")
