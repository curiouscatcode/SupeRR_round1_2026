import pymupdf

with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Find HTML portion
html_start = text.find('<!DOCTYPE html>')
html_end = text.find('</body>') + 7
html_full = text[html_start:html_end]

pages = html_full.split('<div class="page-break"></div>')
p12_html = pages[11]

old_sec9 = """<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>
<p>
1. <strong>Striker Run-Out Attribution:</strong> Striker run-out dismissals are attributed to the striker (<i>W</i><sub>striker</sub> = 1), while non-striker run-outs are attributed to team match state rather than individual batters. 2. <strong>Residual Environmental Variance:</strong> Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance. 3. <strong>Discrete Empirical Baseline:</strong> The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0-3, 4-6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets.
</p>"""

new_sec9 = """<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>
<div style="margin-top: 2pt; margin-bottom: 3pt;">
    <p style="margin-bottom: 2pt;"><strong>1. Striker Run-Out Attribution:</strong> Striker run-out dismissals are attributed to the striker (<i>W</i><sub>striker</sub> = 1), while non-striker run-outs are attributed to team match state rather than individual batters.</p>
    <p style="margin-bottom: 2pt;"><strong>2. Residual Environmental Variance:</strong> Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance.</p>
    <p style="margin-bottom: 2pt;"><strong>3. Discrete Empirical Baseline:</strong> The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0&ndash;3, 4&ndash;6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets.</p>
</div>"""

assert old_sec9 in p12_html
p12_fixed = p12_html.replace(old_sec9, new_sec9)

css_start = text.find('<style>')
css_end = text.find('</style>') + 8
css = text[css_start:css_end]

test_html = f"<!DOCTYPE html><html><head>{css}</head><body>{p12_fixed}</body></html>"

raw_path = "scratch/test_p12_clean.pdf"
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
print("Page 12 clean test: total pages =", len(doc))
p = doc[0]
for b in p.get_text('blocks'):
    print(f"  y0={b[1]:.1f}, y1={b[3]:.1f}: {b[4][:55]!r}")
doc.close()
