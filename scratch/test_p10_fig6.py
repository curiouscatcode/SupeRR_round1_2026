import pymupdf

with open('scratch/test_complete_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract CSS
css_start = text.find('<style>')
css_end = text.find('</style>') + 8
css = text[css_start:css_end]

pages = text.split('<div class="page-break"></div>')
p10_html = pages[9]

fig6_html = """
<div class="figure-container" style="margin-top: 4pt; margin-bottom: 2pt;">
    <img src="outputs/step_8_eda/figures/fig07_alpha_sensitivity_slope.png" alt="Alpha Sensitivity Slopegraph" style="height: 175pt; width: auto;">
    <div class="figure-caption">Figure 6: Sensitivity of Player Rankings to Super-Linear Pressure Weighting (&alpha; = 1.00 vs. 1.25 Across Qualified Cohorts).</div>
</div>
"""

# Let's test inserting Figure 6 after 7.2, or after 7.4
# Test 1: After 7.4 (bottom of Page 10)
p10_combined = p10_html + "\n" + fig6_html

for h in [150, 160, 170, 175, 180, 190, 200]:
    test_p10 = p10_combined.replace('height: 175pt', f'height: {h}pt')
    test_html = f"<!DOCTYPE html><html><head>{css}</head><body>{test_p10}</body></html>"
    raw_path = f"scratch/test_p10_fig6_{h}.pdf"
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
    total_p = len(doc)
    p0 = doc[0]
    blocks = p0.get_text('blocks')
    imgs = p0.get_images()
    last_y = blocks[-1][3] if blocks else 0
    print(f"Height {h}pt: total pages={total_p}, images={len(imgs)}, last block ends at y1={last_y:.1f}")
    doc.close()
