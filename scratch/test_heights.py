import pymupdf

def test_height(max_h):
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
body {{ font-family: sans-serif; margin: 0; padding: 0; }}
.figure-container {{ text-align: center; margin-top: 2pt; margin-bottom: 2pt; }}
.figure-container img {{ max-height: {max_h}pt; width: auto; max-width: 95%; border: 0.5pt solid #cbd5e0; }}
.figure-caption {{ font-size: 7.0pt; font-style: italic; color: #718096; margin-top: 1pt; margin-bottom: 2pt; }}
.section-header {{ font-size: 11pt; color: #1a365d; margin-top: 0; margin-bottom: 3pt; }}
</style>
</head>
<body>
<h2 class="section-header">Visual Reference &mdash; Empirical Bayes Shrinkage Funnels</h2>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png" alt="Batting Shrinkage Funnel">
    <div class="figure-caption">Figure 3: Batting Empirical Bayes Shrinkage Funnel (K = 600).</div>
</div>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig04_bowling_score_vs_sample_size.png" alt="Bowling Shrinkage Funnel">
    <div class="figure-caption">Figure 4: Bowling Empirical Bayes Shrinkage Funnel (K = 500).</div>
</div>
</body>
</html>"""

    archive = pymupdf.Archive('.')
    raw_path = f'scratch/test_h_{max_h}.pdf'
    writer = pymupdf.DocumentWriter(raw_path)
    story = pymupdf.Story(html=html, archive=archive)
    def rectfn(rect_num, filled):
        mediabox = pymupdf.paper_rect('letter')
        rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
        return mediabox, rect, pymupdf.Identity
    story.write(writer, rectfn)
    writer.close()
    doc = pymupdf.open(raw_path)
    print(f'max_height={max_h}pt -> total pages={len(doc)}')

for h in [280, 260, 250, 240, 230, 220]:
    test_height(h)
