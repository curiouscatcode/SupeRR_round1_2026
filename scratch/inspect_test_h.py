import pymupdf

doc = pymupdf.open('scratch/test_h_220.pdf')
print("Total pages:", len(doc))
for i, p in enumerate(doc):
    print(f"--- Page {i+1} ---")
    print("Images:", len(p.get_images()))
    for b in p.get_text('blocks'):
        print(f"  y0={b[1]:.1f}, y1={b[3]:.1f}: {b[4][:50]!r}")
