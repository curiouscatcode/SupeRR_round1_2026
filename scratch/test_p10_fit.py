import pymupdf

with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract Page 10 and 7.4 HTML
# Let's inspect Page 10 HTML in build_step10_4_restoration.py
pages = text.split('<div class="page-break"></div>')
p10_html = pages[9]
p12_html = pages[11]

# Find 7.4 in p12
idx_74 = p12_html.find('<h3 class="subsection-header">7.4 Cross-Format Descriptive Associations</h3>')
idx_sec8 = p12_html.find('<h2 class="section-header">Section 8 &mdash; Placement of Prominent')
sec_74_html = p12_html[idx_74:idx_sec8]

# Test putting 7.4 on Page 10
p10_combined = p10_html + "\n" + sec_74_html

css_start = text.find('<style>')
css_end = text.find('</style>') + 8
css = text[css_start:css_end]

test_html = f"<!DOCTYPE html><html><head>{css}</head><body>{p10_combined}</body></html>"

raw_path = "scratch/test_p10_combined.pdf"
archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter(raw_path)
story = pymupdf.Story(html=test_html, archive=archive)
def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
    return mediabox, rect, pymupdf.Identity
story.write(writer, rectfn)
writer.close()

doc = pymupdf.open(raw_path)
print("Page 10 combined total pages:", len(doc))
p = doc[0]
blocks = p.get_text('blocks')
print(f"Blocks on Page 10: {len(blocks)}, last block ends at y1={blocks[-1][3]:.1f}")
doc.close()
