import os
import sys
import gc
import re
import pandas as pd
import pymupdf

def build_pdf_with_user_updates():
    print("=" * 80)
    print("COMPILING PDF WITH USER UPDATES")
    print("=" * 80)

    # 1. Load Authoritative Step 7.4 CSVs
    bat_csv_path = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv'
    bowl_csv_path = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv'

    df_bat = pd.read_csv(bat_csv_path).head(10)
    df_bowl = pd.read_csv(bowl_csv_path).head(10)

    # Build HTML Top 10 Tables (Exact Booktabs Formatting from build_step10_4_restoration.py)
    def make_html_table(df, discipline):
        rows = []
        for _, r in df.iterrows():
            rank = f"#{int(r['Rank'])}"
            player = r['Player']
            team = r['Team/format'].replace('(IPL & T20I)', '(IPL/T20I)')
            shrunk = f"<strong>{r['Shrunk score']:+.4f}</strong>"
            raw = f"{r['Raw score']:+.4f}"
            balls = f"{int(r['Raw opportunities'])}"
            ess = f"{r['Kish ESS']:.1f}"
            ci = r['95% CI'].replace('[', '[+').replace(', ', ', +').replace('+-', '-')
            
            row_html = f"<tr><td>{rank}</td><td>{player}</td><td>{team}</td><td>{shrunk}</td><td>{raw}</td><td>{balls}</td><td>{ess}</td><td>{ci}</td></tr>"
            rows.append(row_html)
            
        table_html = "<table>\n<tr>\n    <th>Rank</th><th>Player Name</th><th>Team / Franchise</th><th>Shrunk Score</th><th>Raw Score</th><th>Balls</th><th>Kish ESS</th><th>95% Bootstrap CI</th>\n</tr>\n" + "\n".join(rows) + "\n</table>"
        return table_html

    html_bat_table = make_html_table(df_bat, "Batting")
    html_bowl_table = make_html_table(df_bowl, "Bowling")

    # Read base script text to reuse CSS and template structure
    with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
        orig_script = f.read()

    # Extract CSS
    css_start = orig_script.find('<style>')
    css_end = orig_script.find('</style>') + 8
    base_css = orig_script[css_start:css_end]

    # Enhanced CSS with tldr-box and image styling
    enhanced_css = base_css.replace('</style>', """
.tldr-box {
    background: #f7fafc;
    border-left: 3pt solid #2b6cb0;
    border-top: 0.5pt solid #e2e8f0;
    border-right: 0.5pt solid #e2e8f0;
    border-bottom: 0.5pt solid #e2e8f0;
    border-radius: 2pt;
    padding: 3pt 6pt;
    margin-bottom: 4pt;
}
.tldr-title {
    font-size: 8.2pt;
    font-weight: bold;
    color: #1a365d;
    margin-bottom: 2pt;
}
.tldr-box ul {
    margin: 0;
    padding-left: 11pt;
}
.tldr-box li {
    font-size: 6.9pt;
    line-height: 1.20;
    margin-bottom: 1.5pt;
    color: #2d3748;
}
.figure-container {
    text-align: center;
    margin-top: 2pt;
    margin-bottom: 3pt;
}
.figure-container img {
    height: 228pt;
    width: auto;
    border: 0.5pt solid #cbd5e0;
}
.figure-caption {
    font-size: 7.0pt;
    font-style: italic;
    color: #718096;
    margin-top: 1pt;
    margin-bottom: 2pt;
}
</style>""")

    # Extract HTML body from orig_script
    html_start = orig_script.find('<!DOCTYPE html>')
    html_end = orig_script.find('</body>') + 7
    full_html = orig_script[html_start:html_end]

    # Split into 12 pages
    pages = full_html.split('<div class="page-break"></div>')
    assert len(pages) == 12, f"Expected 12 pages, got {len(pages)}"

    # -------------------------------------------------------------
    # PAGE 1 UPDATES: Author & TL;DR Box
    # -------------------------------------------------------------
    p1 = pages[0]
    p1 = p1.replace('Antigravity Autonomous Analytics &amp; Audit Team', 'Amit N Suthar')
    p1 = p1.replace('Antigravity Autonomous Analytics & Audit Team', 'Amit N Suthar')

    tldr_html = """
<div class="tldr-box">
    <div class="tldr-title">Executive TL;DR &mdash; Framework, Formulas, Findings &amp; Limitations at a Glance</div>
    <ul>
        <li><strong>a. Our Methodology:</strong> Evaluates 186,780 deliveries across IPL and T20Is (2022&ndash;2026) against an empirical 36-cell situational baseline (Phase &times; Wickets &times; Target &times; Format). Decomposes acute pressure from low-stakes accumulation and applies Empirical Bayes shrinkage (<i>K</i><sub>bat</sub> = 600, <i>K</i><sub>bowl</sub> = 500) based on Kish ESS to reduce small-sample instability through shrinkage.</li>
        <li><strong>b. Our Formula &amp; Meaning:</strong> Delivery pressure is the geometric mean of difficulty and consequence: <i>P</i>(<i>S<sub>t</sub></i>) = &radic;(<i>T</i> &times; <i>L</i><sub>norm</sub>) &isin; [0, 100]. Player reliability (PWSVA for batting, SBVA for bowling) measures situation-adjusted runs and dismissals added above state expectancy, shrunk toward replacement level. True pressure requires <i>both</i> high difficulty and high consequence.</li>
        <li><strong>c. Key Results:</strong> <strong>Vaibhav Sooryavanshi</strong> ranks #1 in batting (+0.3487 shrunk, raw +0.7614) via explosive clutch boundary hitting; <strong>Suryakumar Yadav</strong> (#2, +0.2819) and <strong>Abhishek Sharma</strong> (#3, +0.2703) lead sustained high-volume reliability. <strong>Rashid Khan</strong> (#1, +0.1756 shrunk) and <strong>Jasprit Bumrah</strong> (#2, +0.1541 shrunk) demonstrate strong pressure-weighted performance, including positive death-over results.</li>
        <li><strong>d. Flaws &amp; Limitations:</strong> Striker run-outs are attributed to the striker while non-striker run-outs are treated as team state; unobserved environmental factors (pitch wear, evening dew, boundary asymmetries) are not explicitly in the state vector; and match phases are discretized into 3 discrete bins rather than a continuous 2D surface.</li>
        <li><strong>e. Conclusion:</strong> Objective pre-delivery pressure gating combined with Empirical Bayes shrinkage addresses several limitations of conventional cricket metrics, establishing robust, auditable rankings that prioritize high-stakes repeatability over volume padding.</li>
    </ul>
</div>
"""
    meta_box_end = p1.find('</div>\n\n<h2 class="section-header">Section 1')
    if meta_box_end != -1:
        p1 = p1[:meta_box_end + 6] + tldr_html + p1[meta_box_end + 6:]
    else:
        meta_box_end = p1.find('</div>\n<h2 class="section-header">Section 1')
        p1 = p1[:meta_box_end + 6] + tldr_html + p1[meta_box_end + 6:]

    p1 = p1.replace(
        "Across 186,780 deliveries spanning 2022&ndash;2026:\n</p>\n<ul>\n    <li>Exactly <strong>297 batters</strong> and <strong>292 bowlers</strong> met the sustained pressure eligibility threshold (<i>N</i>(<i>P</i> &ge; 50) &ge; 50).</li>\n    <li><strong>Top Batting Performer:</strong> <strong>Vaibhav Sooryavanshi</strong> ranks #1 (+0.3487 shrunk PWSVA), exhibiting extraordinary boundary hitting in high-pressure opportunities (raw +0.7614, Kish ESS = 506.9, retaining 45.8% of raw performance under rigorous shrinkage).</li>\n    <li><strong>Consistently Elite Batting Volume:</strong> <strong>Suryakumar Yadav</strong> ranks #2 (+0.2819 shrunk PWSVA, raw +0.3558, 2,638 balls, Kish ESS = 2,287.2) and <strong>Abhishek Sharma</strong> ranks #3 (+0.2703 shrunk PWSVA, raw +0.3547, 2,195 balls, Kish ESS = 1,923.3), maintaining elite positive value added across massive sample sizes.</li>\n    <li><strong>Top Bowling Performer:</strong> <strong>Rashid Khan</strong> ranks #1 (+0.1756 shrunk SBVA, raw +0.2147, 2,648 balls, Kish ESS = 2,245.9), followed closely by <strong>Jasprit Bumrah</strong> at #2 (+0.1541 shrunk SBVA, raw +0.2103, 1,606 balls, Kish ESS = 1,369.7) and <strong>Sunil Narine</strong> at #3 (+0.1442 shrunk SBVA, raw +0.2020, 1,464 balls, Kish ESS = 1,246.3).</li>\n</ul>",
        "Across 186,780 deliveries spanning 2022&ndash;2026, exactly <strong>297 batters</strong> and <strong>292 bowlers</strong> met the sustained pressure eligibility threshold (<i>N</i>(<i>P</i> &ge; 50) &ge; 50). Leaderboards are headed by <strong>Vaibhav Sooryavanshi</strong> (+0.3487 shrunk PWSVA) in batting and <strong>Rashid Khan</strong> (+0.1756 shrunk SBVA) in bowling, followed by high-volume masters <strong>Suryakumar Yadav</strong> (+0.2819) and <strong>Jasprit Bumrah</strong> (+0.1541)."
    )

    pages[0] = p1

    # -------------------------------------------------------------
    # PAGE 2: Tables insertion
    # -------------------------------------------------------------
    p2 = pages[1]
    p2 = p2.replace('__HTML_BAT_TABLE__', html_bat_table)
    p2 = p2.replace('__HTML_BOWL_TABLE__', html_bowl_table)
    pages[1] = p2

    # -------------------------------------------------------------
    # PAGE 4: Visual Reference Top 20 Rankings Images
    # -------------------------------------------------------------
    p4 = pages[3]
    p4 = p4.replace(
        '<img src="outputs/step_7_empirical_calibration/step_7_4_final_rankings/top10_batting_reliability.png" alt="Top 20 Batters" style="max-height: 290pt;">',
        '<img src="outputs/step_8_eda/figures/fig01_batting_top20_rankings.png" alt="Top 20 Batters" style="height: 228pt; width: auto;">'
    )
    p4 = p4.replace(
        '<img src="outputs/step_7_empirical_calibration/step_7_4_final_rankings/top10_bowling_reliability.png" alt="Top 20 Bowlers" style="max-height: 290pt;">',
        '<img src="outputs/step_8_eda/figures/fig02_bowling_top20_rankings.png" alt="Top 20 Bowlers" style="height: 228pt; width: auto;">'
    )
    pages[3] = p4

    # -------------------------------------------------------------
    # PAGE 8: Visual Reference Shrinkage Funnels Images (FIXED PATHS)
    # -------------------------------------------------------------
    p8 = pages[7]
    p8 = p8.replace(
        '<img src="outputs/step_7_empirical_calibration/step_7_3_shrinkage_pressure_calibration/batting_shrinkage_funnel.png" alt="Batting Shrinkage Funnel" style="max-height: 290pt;">',
        '<img src="outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png" alt="Batting Shrinkage Funnel" style="height: 228pt; width: auto;">'
    )
    p8 = p8.replace(
        '<img src="outputs/step_7_empirical_calibration/step_7_3_shrinkage_pressure_calibration/bowling_shrinkage_funnel.png" alt="Bowling Shrinkage Funnel" style="max-height: 290pt;">',
        '<img src="outputs/step_8_eda/figures/fig04_bowling_score_vs_sample_size.png" alt="Bowling Shrinkage Funnel" style="height: 228pt; width: auto;">'
    )
    pages[7] = p8

    # -------------------------------------------------------------
    # PAGE 11: Visual Reference Phase Heatmaps Images (FIXED PATHS)
    # -------------------------------------------------------------
    p11 = pages[10]
    p11 = p11.replace(
        '<img src="outputs/step_8_eda/figures/fig_7_batting_phase_heatmap.png" alt="Batting Phase Heatmap" style="max-height: 290pt;">',
        '<img src="outputs/step_8_eda/figures/fig10_batting_phase_heatmap.png" alt="Batting Phase Heatmap" style="height: 228pt; width: auto;">'
    )
    p11 = p11.replace(
        '<img src="outputs/step_8_eda/figures/fig_8_bowling_phase_heatmap.png" alt="Bowling Phase Heatmap" style="max-height: 290pt;">',
        '<img src="outputs/step_8_eda/figures/fig11_bowling_phase_heatmap.png" alt="Bowling Phase Heatmap" style="height: 228pt; width: auto;">'
    )
    pages[10] = p11

    # -------------------------------------------------------------
    # PAGE 12: Section 9 on New Lines & Footer Author Update
    # -------------------------------------------------------------
    p12 = pages[11]
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

    p12 = p12.replace(old_sec9, new_sec9)
    p12 = p12.replace('Antigravity Autonomous Audit Team', 'Amit N Suthar')
    pages[11] = p12

    # Rejoin pages into final HTML
    updated_html_body = '<div class="page-break"></div>'.join(pages)
    
    # Replace CSS in document
    full_compiled_html = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n<title>SupeRR Selector 2.0 &mdash; Methodology Report</title>\n{enhanced_css}\n</head>\n{updated_html_body}"

    # Render with PyMuPDF Story
    raw_pdf_path = 'scratch/raw_candidate_updated.pdf'
    final_pdf_path = 'scratch/step_10_user_candidate_final.pdf'

    for p in [raw_pdf_path, final_pdf_path]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except:
                pass

    archive = pymupdf.Archive('.')
    writer = pymupdf.DocumentWriter(raw_pdf_path)
    story = pymupdf.Story(html=full_compiled_html, archive=archive)

    def rectfn(rect_num, filled):
        mediabox = pymupdf.paper_rect('letter')
        rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
        return mediabox, rect, pymupdf.Identity

    story.write(writer, rectfn)
    writer.close()

    # Post-process: Add running headers & footers
    doc = pymupdf.open(raw_pdf_path)
    total_pages = len(doc)
    print(f"Candidate PDF generated with {total_pages} pages.")
    assert total_pages == 12, f"Target page count is 12, got {total_pages}"

    for pno in range(total_pages):
        page = doc[pno]
        if pno > 0:
            page.insert_text(
                (40, 24),
                "SupeRR Selector 2.0 — Official Methodology Report",
                fontsize=7.5,
                color=(0.35, 0.4, 0.45)
            )
        page.insert_text(
            (40, page.rect.height - 20),
            "Confidential — Prepared for SupeRR Selector Round 1 · Author: Amit N Suthar",
            fontsize=7.5,
            color=(0.5, 0.5, 0.5)
        )
        page_str = f"Page {pno + 1} of {total_pages}"
        tw = pymupdf.get_text_length(page_str, fontname="helv", fontsize=7.5)
        page.insert_text(
            (page.rect.width - 40 - tw, page.rect.height - 20),
            page_str,
            fontsize=7.5,
            color=(0.3, 0.3, 0.3)
        )

    doc.save(final_pdf_path, deflate=True, garbage=4)
    doc.close()
    del doc
    del writer
    gc.collect()

    try:
        if os.path.exists(raw_pdf_path):
            os.remove(raw_pdf_path)
    except:
        pass

    print(f"Successfully generated candidate PDF: {final_pdf_path} (Pages: {total_pages}, Size: {os.path.getsize(final_pdf_path)} bytes).")
    return final_pdf_path

if __name__ == '__main__':
    build_pdf_with_user_updates()
