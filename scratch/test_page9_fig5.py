import pymupdf

with open('scratch/test_complete_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract CSS
css_start = text.find('<style>')
css_end = text.find('</style>') + 8
css = text[css_start:css_end]

pages = text.split('<div class="page-break"></div>')
p9_html = pages[8]

print("Original P9 HTML contains score_distributions.png:", "score_distributions.png" in p9_html)

for img_candidate in [
    'outputs/step_8_eda/figures/fig13_population_score_distributions.png',
    'outputs/step_7_empirical_calibration/step_7_4_final_rankings/score_distributions.png'
]:
    print(f"\n--- Testing {img_candidate} ---")
    for height_pt in [180, 190, 200, 210, 220]:
        test_p9 = p9_html.replace(
            '<img src="outputs/step_8_eda/figures/score_distributions.png" alt="Score Distributions" style="height: 200pt; width: auto;">',
            f'<img src="{img_candidate}" alt="Score Distributions" style="height: {height_pt}pt; width: auto;">'
        )
        
        test_html = f"<!DOCTYPE html><html><head>{css}</head><body>{test_p9}</body></html>"
        raw_path = f"scratch/test_p9_{height_pt}.pdf"
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
        print(f"Height {height_pt}pt: total pages={total_p}, images={len(imgs)}, last block ends at y1={last_y:.1f}")
        doc.close()
