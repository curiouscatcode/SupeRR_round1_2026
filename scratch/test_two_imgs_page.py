import pymupdf

def test_page(p_name, img1_path, cap1, img2_path, cap2, h_pt=230):
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
body {{ font-family: sans-serif; margin: 0; padding: 0; }}
.figure-container {{ text-align: center; margin-top: 2pt; margin-bottom: 2pt; }}
.figure-container img {{ height: {h_pt}pt; width: auto; border: 0.5pt solid #cbd5e0; }}
.figure-caption {{ font-size: 7.2pt; font-style: italic; color: #718096; margin-top: 1pt; margin-bottom: 2pt; }}
.section-header {{ font-size: 11pt; color: #1a365d; margin-top: 0; margin-bottom: 3pt; }}
</style>
</head>
<body>
<h2 class="section-header">{p_name}</h2>
<div class="figure-container">
    <img src="{img1_path}" alt="Image 1">
    <div class="figure-caption">{cap1}</div>
</div>
<div class="figure-container">
    <img src="{img2_path}" alt="Image 2">
    <div class="figure-caption">{cap2}</div>
</div>
</body>
</html>"""

    raw_path = f"scratch/test_{p_name.replace(' ', '_')}.pdf"
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
    print(f"{p_name}: total pages = {len(doc)}, images on p1 = {len(doc[0].get_images())}")
    for b in doc[0].get_text('blocks'):
        print(f"  y0={b[1]:.1f}, y1={b[3]:.1f}: {b[4][:55]!r}")
    doc.close()

test_page("Page_8_Shrinkage", 
          "outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png",
          "Figure 3: Batting Empirical Bayes Shrinkage Funnel showing convergence of raw PWSVA toward population baseline (K = 600).",
          "outputs/step_8_eda/figures/fig04_bowling_score_vs_sample_size.png",
          "Figure 4: Bowling Empirical Bayes Shrinkage Funnel showing convergence of raw SBVA toward population baseline (K = 500).",
          h_pt=230)

test_page("Page_11_Heatmaps",
          "outputs/step_8_eda/figures/fig10_batting_phase_heatmap.png",
          "Figure 7: Batting Phase Performance Heatmap (Powerplay vs. Middle vs. Death Value Added per Ball).",
          "outputs/step_8_eda/figures/fig11_bowling_phase_heatmap.png",
          "Figure 8: Bowling Phase Performance Heatmap (Powerplay vs. Middle vs. Death Net Runs Saved per Ball).",
          h_pt=230)
