import pymupdf

tests = [
    ('max_height_220', 'style="max-height: 220pt;"'),
    ('height_220', 'style="height: 220pt;"'),
    ('width_320', 'style="width: 320pt;"'),
    ('height_attr', 'height="220"'),
    ('width_attr', 'width="320"'),
    ('container_w', 'container')
]

for name, syntax in tests:
    if syntax == 'container':
        html = """<!DOCTYPE html><html><head><style>body { margin: 0; } .box { width: 320pt; margin: 0 auto; }</style></head>
<body><div class="box"><img src="outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png" style="width: 100%;"></div></body></html>"""
    else:
        html = f"""<!DOCTYPE html><html><head><style>body {{ margin: 0; }}</style></head>
<body><img src="outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png" {syntax}></body></html>"""

    raw_path = f"scratch/test_{name}.pdf"
    archive = pymupdf.Archive('.')
    writer = pymupdf.DocumentWriter(raw_path)
    story = pymupdf.Story(html=html, archive=archive)
    def rectfn(rect_num, filled):
        mediabox = pymupdf.paper_rect('letter')
        rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
        return mediabox, rect, pymupdf.Identity
    story.write(writer, rectfn)
    writer.close()
    doc = pymupdf.open(raw_path)
    p = doc[0]
    for item in p.get_images(full=True):
        bbox = p.get_image_bbox(item)
        print(f'{name:15s} -> height: {bbox.height:.1f}, width: {bbox.width:.1f}, bbox: {bbox}')
    doc.close()
