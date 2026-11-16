import os
import re

with open('scratch/build_step10_4_original.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Author
text = text.replace('Antigravity Autonomous Analytics &amp; Audit Team', 'Amit N Suthar')
text = text.replace('Antigravity Autonomous Analytics & Audit Team', 'Amit N Suthar')

# 2. Add TL;DR Box on Page 1
tldr_box = """<div class="tldr-box">
    <div class="tldr-title">Executive TL;DR &mdash; Framework, Formulas, Findings &amp; Limitations at a Glance</div>
    <ul>
        <li><strong>a. Our Methodology:</strong> Evaluates 186,780 deliveries across IPL and T20Is (2022&ndash;2026) against an empirical 36-cell situational baseline (Phase &times; Wickets &times; Target &times; Format). Decomposes acute pressure from low-stakes accumulation and applies Empirical Bayes shrinkage (<i>K</i><sub>bat</sub> = 600, <i>K</i><sub>bowl</sub> = 500) based on Kish ESS to reduce small-sample instability through shrinkage.</li>
        <li><strong>b. Our Formula &amp; Meaning:</strong> Delivery pressure is the geometric mean of difficulty and consequence: <i>P</i>(<i>S<sub>t</sub></i>) = &radic;(<i>T</i> &times; <i>L</i><sub>norm</sub>) &isin; [0, 100]. Player reliability (PWSVA for batting, SBVA for bowling) measures situation-adjusted runs and dismissals added above state expectancy, shrunk toward replacement level. True pressure requires <i>both</i> high difficulty and high consequence.</li>
        <li><strong>c. Key Results:</strong> <strong>Vaibhav Sooryavanshi</strong> ranks #1 in batting (+0.3487 shrunk, raw +0.7614) via explosive clutch boundary hitting; <strong>Suryakumar Yadav</strong> (#2, +0.2819) and <strong>Abhishek Sharma</strong> (#3, +0.2703) lead sustained high-volume reliability. <strong>Rashid Khan</strong> (#1, +0.1756 shrunk) and <strong>Jasprit Bumrah</strong> (#2, +0.1541 shrunk) lead bowling reliability, demonstrating strong pressure-weighted performance, including positive death-over results.</li>
        <li><strong>d. Flaws &amp; Limitations:</strong> Striker run-outs are attributed to the striker while non-striker run-outs are treated as team state; unobserved environmental factors (pitch wear, evening dew, boundary asymmetries) are not explicitly in the state vector; and match phases are discretized into 3 discrete bins rather than a continuous 2D surface.</li>
        <li><strong>e. Conclusion:</strong> Objective pre-delivery pressure gating combined with Empirical Bayes shrinkage addresses several limitations of conventional cricket metrics, establishing robust, auditable rankings that prioritize high-stakes repeatability over volume padding.</li>
    </ul>
</div>"""

meta_end = text.find('</div>\n\n<h2 class="section-header">Section 1')
if meta_end != -1:
    text = text[:meta_end + 6] + '\n' + tldr_box + text[meta_end + 6:]
else:
    meta_end = text.find('</div>\n<h2 class="section-header">Section 1')
    text = text[:meta_end + 6] + '\n' + tldr_box + text[meta_end + 6:]

# Trim Section 1.2 slightly on Page 1 so everything fits comfortably on Page 1
sec12_old = """Across 186,780 deliveries spanning 2022&ndash;2026:
</p>
<ul>
    <li>Exactly <strong>297 batters</strong> and <strong>292 bowlers</strong> met the sustained pressure eligibility threshold (<i>N</i>(<i>P</i> &ge; 50) &ge; 50).</li>
    <li><strong>Top Batting Performer:</strong> <strong>Vaibhav Sooryavanshi</strong> ranks #1 (+0.3487 shrunk PWSVA), exhibiting extraordinary boundary hitting in high-pressure opportunities (raw +0.7614, Kish ESS = 506.9, retaining 45.8% of raw performance under rigorous shrinkage).</li>
    <li><strong>Consistently Elite Batting Volume:</strong> <strong>Suryakumar Yadav</strong> ranks #2 (+0.2819 shrunk PWSVA, raw +0.3558, 2,638 balls, Kish ESS = 2,287.2) and <strong>Abhishek Sharma</strong> ranks #3 (+0.2703 shrunk PWSVA, raw +0.3547, 2,195 balls, Kish ESS = 1,923.3), maintaining elite positive value added across massive sample sizes.</li>
    <li><strong>Top Bowling Performer:</strong> <strong>Rashid Khan</strong> ranks #1 (+0.1756 shrunk SBVA, raw +0.2147, 2,648 balls, Kish ESS = 2,245.9), followed closely by <strong>Jasprit Bumrah</strong> at #2 (+0.1541 shrunk SBVA, raw +0.2103, 1,606 balls, Kish ESS = 1,369.7) and <strong>Sunil Narine</strong> at #3 (+0.1442 shrunk SBVA, raw +0.2020, 1,464 balls, Kish ESS = 1,246.3).</li>
</ul>"""

sec12_new = """Across 186,780 deliveries spanning 2022&ndash;2026, exactly <strong>297 batters</strong> and <strong>292 bowlers</strong> met the sustained pressure eligibility threshold (<i>N</i>(<i>P</i> &ge; 50) &ge; 50). Leaderboards are headed by <strong>Vaibhav Sooryavanshi</strong> (+0.3487 shrunk PWSVA) in batting and <strong>Rashid Khan</strong> (+0.1756 shrunk SBVA) in bowling, followed by high-volume masters <strong>Suryakumar Yadav</strong> (+0.2819) and <strong>Jasprit Bumrah</strong> (+0.1541).</p>"""

text = text.replace(sec12_old, sec12_new)

# 3. Enhanced CSS for tldr-box and figure styling
text = text.replace('</style>', """
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
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4pt;
    margin-bottom: 6pt;
    font-size: 7.8pt;
    page-break-inside: avoid;
}
th {
    border-top: 1.2pt solid #1a365d;
    border-bottom: 1.2pt solid #1a365d;
    background-color: transparent;
    color: #1a365d;
    text-align: left;
    padding: 3.5pt 4pt;
    font-weight: bold;
}
td {
    border-bottom: 0.5pt solid #e2e8f0;
    padding: 3.2pt 4pt;
    color: #2d3748;
}
</style>""")

# 4. Fix Images on Page 4, Page 8, Page 11
text = text.replace(
    '<img src="outputs/step_7_empirical_calibration/step_7_4_final_rankings/top10_batting_reliability.png" alt="Top 20 Batters" style="max-height: 290pt;">',
    '<img src="outputs/step_8_eda/figures/fig01_batting_top20_rankings.png" alt="Top 20 Batters" style="height: 228pt; width: auto;">'
)
text = text.replace(
    '<img src="outputs/step_7_empirical_calibration/step_7_4_final_rankings/top10_bowling_reliability.png" alt="Top 20 Bowlers" style="max-height: 290pt;">',
    '<img src="outputs/step_8_eda/figures/fig02_bowling_top20_rankings.png" alt="Top 20 Bowlers" style="height: 228pt; width: auto;">'
)

# Page 8
text = text.replace(
    '<img src="outputs/step_7_empirical_calibration/step_7_3_shrinkage_pressure_calibration/batting_shrinkage_funnel.png" alt="Batting Shrinkage Funnel" style="max-height: 290pt;">',
    '<img src="outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png" alt="Batting Shrinkage Funnel" style="height: 228pt; width: auto;">'
)
text = text.replace(
    '<img src="outputs/step_7_empirical_calibration/step_7_3_shrinkage_pressure_calibration/bowling_shrinkage_funnel.png" alt="Bowling Shrinkage Funnel" style="max-height: 290pt;">',
    '<img src="outputs/step_8_eda/figures/fig04_bowling_score_vs_sample_size.png" alt="Bowling Shrinkage Funnel" style="height: 228pt; width: auto;">'
)

# Page 11
text = text.replace(
    '<img src="outputs/step_8_eda/figures/fig_7_batting_phase_heatmap.png" alt="Batting Phase Heatmap" style="max-height: 290pt;">',
    '<img src="outputs/step_8_eda/figures/fig10_batting_phase_heatmap.png" alt="Batting Phase Heatmap" style="height: 228pt; width: auto;">'
)
text = text.replace(
    '<img src="outputs/step_8_eda/figures/fig_8_bowling_phase_heatmap.png" alt="Bowling Phase Heatmap" style="max-height: 290pt;">',
    '<img src="outputs/step_8_eda/figures/fig11_bowling_phase_heatmap.png" alt="Bowling Phase Heatmap" style="height: 228pt; width: auto;">'
)

# 5. Fix Section 9 formatting on new lines
sec9_old = """<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>
<p>
1. <strong>Striker Run-Out Attribution:</strong> Striker run-out dismissals are attributed to the striker (<i>W</i><sub>striker</sub> = 1), while non-striker run-outs are attributed to team match state rather than individual batters. 2. <strong>Residual Environmental Variance:</strong> Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance. 3. <strong>Discrete Empirical Baseline:</strong> The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0-3, 4-6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets.
</p>"""

sec9_new = """<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>
<div style="margin-top: 2pt; margin-bottom: 3pt;">
    <p style="margin-bottom: 2pt;"><strong>1. Striker Run-Out Attribution:</strong> Striker run-out dismissals are attributed to the striker (<i>W</i><sub>striker</sub> = 1), while non-striker run-outs are attributed to team match state rather than individual batters.</p>
    <p style="margin-bottom: 2pt;"><strong>2. Residual Environmental Variance:</strong> Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance.</p>
    <p style="margin-bottom: 2pt;"><strong>3. Discrete Empirical Baseline:</strong> The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0&ndash;3, 4&ndash;6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets.</p>
</div>"""

text = text.replace(sec9_old, sec9_new)

# 6. Clean Table function
func_old = """    # 3. Build HTML Top 10 Tables (Booktabs Border Styling)
    html_bat_table = \"\"\"<table class=\"report-table\">"""

# Replace make_html_table implementation if needed
text = re.sub(
    r'# 3\. Build HTML Top 10 Tables.*?(?=html_bat_table = make_html_table)',
    '''# 3. Build HTML Top 10 Tables (Booktabs Border Styling)
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
            
        table_html = "<table>\\n<tr>\\n    <th>Rank</th><th>Player Name</th><th>Team / Franchise</th><th>Shrunk Score</th><th>Raw Score</th><th>Balls</th><th>Kish ESS</th><th>95% Bootstrap CI</th>\\n</tr>\\n" + "\\n".join(rows) + "\\n</table>"
        return table_html

    ''',
    text,
    flags=re.DOTALL
)

# 7. Destination PDF paths
text = text.replace(
    "pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'",
    "pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'"
)
text = text.replace(
    'raw_pdf_path = "scratch/step_10_4_candidate.pdf"',
    'raw_pdf_path = "scratch/raw_candidate_final.pdf"'
)

# Footer running text
text = text.replace(
    '"Confidential — Prepared for SupeRR Selector Round 1 Competition Judges"',
    '"Confidential — Prepared for SupeRR Selector Round 1 · Author: Amit N Suthar"'
)

# Do not overwrite markdown in build script
text = text.replace(
    "with open(md_out_path, 'w', encoding='utf-8') as f:\n        f.write(full_markdown_text)",
    "# Preserving markdown as edited"
)

with open('scratch/build_step10_4_restoration.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved clean scratch/build_step10_4_restoration.py.")
