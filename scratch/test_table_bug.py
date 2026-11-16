import pymupdf

def test_config(name, html_table):
    test_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
@page {{ size: letter; margin: 40pt; }}
body {{ font-family: sans-serif; font-size: 10pt; }}
.figure-container {{ text-align: center; margin: 8pt 0; }}
img.figure-img {{ max-width: 440pt; max-height: 270pt; }}
</style>
</head>
<body>
<h1>Test Title</h1>
{html_table}

<div class="figure-container" style="page-break-before: always;">
    <img src="outputs/step_8_eda/figures/fig01_batting_top20_rankings.png" class="figure-img">
    <p>Figure 1</p>
</div>
</body>
</html>
"""
    archive = pymupdf.Archive('.')
    out_pdf = f'scratch/test_{name}.pdf'
    writer = pymupdf.DocumentWriter(out_pdf)
    story = pymupdf.Story(html=test_html, archive=archive)

    def rectfn(rect_num, filled):
        mediabox = pymupdf.paper_rect('letter')
        rect = pymupdf.Rect(40, 45, mediabox.width - 40, mediabox.height - 45)
        return mediabox, rect, pymupdf.Identity

    story.write(writer, rectfn)
    writer.close()

    doc = pymupdf.open(out_pdf)
    p2 = doc[1]
    blue_drawings = [d for d in p2.get_drawings() if d.get('fill') == (0.10196078568696976, 0.21176470816135406, 0.364705890417099)]
    print(f"Option '{name}': P2 total drawings = {len(p2.get_drawings())}, blue drawings = {len(blue_drawings)}")

# Option 1: standard table with th background-color
test_config("standard_th", """
<table style="width: 100%; border-collapse: collapse;">
<tr><th style="background-color: #1a365d; color: white;">Col 1</th><th style="background-color: #1a365d; color: white;">Col 2</th></tr>
<tr><td>A</td><td>B</td></tr>
</table>
""")

# Option 2: table with thead / tbody
test_config("thead_tbody", """
<table style="width: 100%; border-collapse: collapse;">
<thead>
<tr><th style="background-color: #1a365d; color: white;">Col 1</th><th style="background-color: #1a365d; color: white;">Col 2</th></tr>
</thead>
<tbody>
<tr><td>A</td><td>B</td></tr>
</tbody>
</table>
""")

# Option 3: table without background-color on th/td (using borders and text color)
test_config("no_bg", """
<table style="width: 100%; border-collapse: collapse; border-top: 2pt solid #1a365d; border-bottom: 2pt solid #1a365d;">
<tr><th style="color: #1a365d; border-bottom: 1pt solid #1a365d; padding: 4pt;">Col 1</th><th style="color: #1a365d; border-bottom: 1pt solid #1a365d; padding: 4pt;">Col 2</th></tr>
<tr><td style="padding: 4pt; border-bottom: 0.5pt solid #ccc;">A</td><td style="padding: 4pt; border-bottom: 0.5pt solid #ccc;">B</td></tr>
</table>
""")

# Option 4: table inside div with overflow hidden or display table
test_config("div_table", """
<div style="display: block; width: 100%;">
<table style="width: 100%; border-collapse: collapse;">
<tr><th style="background-color: #1a365d; color: white;">Col 1</th><th style="background-color: #1a365d; color: white;">Col 2</th></tr>
<tr><td>A</td><td>B</td></tr>
</table>
</div>
""")
