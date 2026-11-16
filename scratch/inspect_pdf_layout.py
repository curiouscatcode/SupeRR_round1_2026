import pymupdf

doc = pymupdf.open('outputs/step_10_methodology_report/step_10_methodology_report.pdf')

for i in range(len(doc)):
    page = doc[i]
    print(f"================================ PAGE {i+1} ================================")
    blocks = page.get_text('blocks')
    for b in blocks:
        # print first line of each block
        first_line = b[4].strip().split('\n')[0]
        print(f"  [{b[1]:.1f} - {b[3]:.1f}] {first_line[:80]}")
