import pymupdf

with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract CSS
css_start = text.find('<style>')
css_end = text.find('</style>') + 8
css = text[css_start:css_end]

# Extract Marquee table and Section 9 from Page 12
pages = text.split('<div class="page-break"></div>')
p12_html = pages[11]

idx_sec8 = p12_html.find('<h2 class="section-header">Section 8 &mdash; Placement of Prominent')
idx_sec9 = p12_html.find('<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>')

sec8_html = p12_html[idx_sec8:idx_sec9]
sec9_html = """<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>
<div style="margin-top: 1pt; margin-bottom: 2pt;">
    <p style="margin-bottom: 1.5pt;"><strong>1. Striker Run-Out Attribution:</strong> Striker run-outs are attributed to the striker (<i>W</i><sub>striker</sub> = 1); non-striker run-outs are attributed to team match state.</p>
    <p style="margin-bottom: 1.5pt;"><strong>2. Residual Environmental Variance:</strong> Pitch wear, dew, and ground dimensions are unobserved residual factors; delivery clustering is captured via match-level block bootstrap.</p>
    <p style="margin-bottom: 1.5pt;"><strong>3. Discrete Empirical Baseline:</strong> The 36-cell tensor groups overs and wickets discretely; future iterations will adopt continuous 2D Gaussian processes.</p>
</div>"""

sec10_knockout_html = """<h2 class="section-header">Section 10 &mdash; Experimental Sensitivity: Tournament Knockout Leverage</h2>
<p style="margin-bottom: 1.5pt;">
To test whether tournament stakes warrant super-weighting, an experiment applied multipliers (1.10&times; to 1.25&times;) to delivery pressure (<i>P</i>) across 19 IPL playoff matches (4,445 deliveries) with dynamic Kish ESS and Empirical Bayes re-shrinkage.
</p>
<ul style="margin-top: 1pt; margin-bottom: 2pt;">
    <li><strong>Key Results:</strong> Bowlers in the top tier showed 100% retention (Top 5 invariant: Rashid at 1, Bumrah at 2, Narine at 3, Hazlewood at 4, Varun at 5). Batters in the top tier exhibited 90% retention (Top 7 invariant; Rajat Patidar rose from rank 11 to 8 on 186 playoff balls; Travis Head slipped from rank 8 to 10).</li>
    <li><strong>Conclusion:</strong> The knockout bonus was <strong>rejected</strong> from official rankings due to small-sample volatility (e.g., Mitchell Starc +17 ranks on 42 balls), structural bias against players on non-qualifying teams (71% with zero playoff balls), and redundant double-counting since win-probability swing already prices late-game leverage.</li>
</ul>

<h2 class="section-header">Section 11 &mdash; Conclusion</h2>
<p style="margin-bottom: 2pt;">
The SupeRR Selector framework establishes an uncompromised, reproducible standard for T20 evaluation. By decomposing pressure into Task Difficulty and Win-Probability Consequence, contrasting against an empirical baseline, and applying Empirical Bayes shrinkage, the engine delivers transparent, mathematically robust rankings.
</p>

<div style="margin-top: 4pt; font-size: 7.2pt; color: #718096; text-align: center; border-top: 0.5pt solid #e2e8f0; padding-top: 2pt;">
    Official Methodology Report &middot; SupeRR Selector 2.0 (Round 1) &middot; Amit N Suthar &middot; November 2026
</div>"""

test_p12_combined = f"<!DOCTYPE html><html><head>{css}</head><body>\n{sec8_html}\n{sec9_html}\n{sec10_knockout_html}\n</body></html>"

raw_path = "scratch/test_p12_fit.pdf"
archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter(raw_path)
story = pymupdf.Story(html=test_p12_combined, archive=archive)
def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
    return mediabox, rect, pymupdf.Identity
story.write(writer, rectfn)
writer.close()

doc = pymupdf.open(raw_path)
print("Page 12 combined total pages:", len(doc))
p = doc[0]
blocks = p.get_text('blocks')
print(f"Blocks on Page 12: {len(blocks)}, last block ends at y1={blocks[-1][3]:.1f}")
marquee_rows = [b[4].strip().split('\n') for b in blocks if ('Batting' in b[4] or 'Bowling' in b[4]) and ('#' in b[4])]
print(f"Marquee rows found on Page 12: {len(marquee_rows)}")
assert len(marquee_rows) == 15, f"Expected 15 marquee rows on Page 12, got {len(marquee_rows)}"
for i, r in enumerate(marquee_rows):
    assert len(r) == 8, f"Row {i+1} has {len(r)} elements: {r}"
    print(f"  [OK] Row {i+1}: {r[0]:<18} ({r[1]:<7}) {r[2]:<4} {r[3]}")
doc.close()
print("TEST P12 PASSED PERFECTLY!")
