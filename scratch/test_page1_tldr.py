import pymupdf

def test_p1():
    html = """<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 8.0pt; line-height: 1.25; color: #2d3748; margin: 0; padding: 0; }
.report-title { font-size: 15pt; font-weight: bold; color: #1a365d; margin-bottom: 2pt; line-height: 1.15; }
.report-subtitle { font-size: 9.5pt; font-weight: 500; color: #2b6cb0; margin-bottom: 5pt; }
.meta-box { background: #edf2f7; border: 0.5pt solid #cbd5e0; border-radius: 3pt; padding: 4pt 6pt; font-size: 7.2pt; color: #4a5568; margin-bottom: 5pt; line-height: 1.25; }
.tldr-box { background: #f7fafc; border-left: 3pt solid #2b6cb0; border-top: 0.5pt solid #e2e8f0; border-right: 0.5pt solid #e2e8f0; border-bottom: 0.5pt solid #e2e8f0; border-radius: 2pt; padding: 4pt 6pt; margin-bottom: 5pt; }
.tldr-title { font-size: 8.5pt; font-weight: bold; color: #1a365d; margin-bottom: 3pt; }
.tldr-box ul { margin: 0; padding-left: 12pt; }
.tldr-box li { font-size: 7.2pt; line-height: 1.22; margin-bottom: 2pt; color: #2d3748; }
.section-header { font-size: 10.5pt; font-weight: bold; color: #1a365d; border-bottom: 0.5pt solid #cbd5e0; padding-bottom: 1pt; margin-top: 5pt; margin-bottom: 3pt; }
.subsection-header { font-size: 8.8pt; font-weight: bold; color: #2b6cb0; margin-top: 4pt; margin-bottom: 2pt; }
p { margin-top: 0; margin-bottom: 3pt; text-align: justify; }
ul { margin-top: 0; margin-bottom: 3pt; padding-left: 12pt; }
li { margin-bottom: 1.5pt; line-height: 1.22; }
</style>
</head>
<body>

<div class="report-title">Identifying the Most Reliable T20 Players Under Pressure</div>
<div class="report-subtitle">A Dual-Dimensional Situational Value Framework with Empirical Bayes Shrinkage</div>

<div class="meta-box">
    <strong>Author:</strong> Amit N Suthar &nbsp;|&nbsp; <strong>Competition:</strong> SupeRR Selector Season 2 &mdash; Round 1<br>
    <strong>Dataset Scope:</strong> Ball-by-ball records from Men's T20 Competitions (IPL &amp; T20I, 2022&ndash;2026, <i>N</i> = 186,780 deliveries)<br>
    <strong>Authoritative Source Baseline:</strong> Frozen Step 7.4 Outputs (<code>outputs/step_7_empirical_calibration/step_7_4_final_rankings/</code>)
</div>

<div class="tldr-box">
    <div class="tldr-title">Executive TL;DR &mdash; Framework &amp; Findings at a Glance</div>
    <ul>
        <li><strong>a. Our Methodology:</strong> Evaluates 186,780 deliveries across IPL and T20Is (2022&ndash;2026) against an empirical 36-cell situational baseline (Phase &times; Wickets &times; Target &times; Format). Decomposes acute pressure from low-stakes accumulation and applies Empirical Bayes shrinkage (<i>K</i><sub>bat</sub> = 600, <i>K</i><sub>bowl</sub> = 500) based on Kish ESS to prevent small-sample noise.</li>
        <li><strong>b. Our Formula &amp; Its Meaning:</strong> Pressure is defined pre-delivery (<i>t</i><sup>&minus;</sup>) as the geometric mean of difficulty and consequence: <i>P</i> = &radic;(<i>T</i> &times; <i>L</i><sub>norm</sub>) &isin; [0, 100]. Batting reliability (PWSVA) and bowling reliability (SBVA) measure situation-adjusted runs and dismissals added above state expectancy, shrunk toward replacement level.</li>
        <li><strong>c. Key Results:</strong> <strong>Vaibhav Sooryavanshi</strong> ranks #1 in batting (+0.3487 shrunk, raw +0.7614) via explosive clutch boundary hitting; <strong>Suryakumar Yadav</strong> (#2, +0.2819) and <strong>Abhishek Sharma</strong> (#3, +0.2703) lead high-volume reliability. <strong>Rashid Khan</strong> (#1, +0.1756 shrunk) and <strong>Jasprit Bumrah</strong> (#2, +0.1541 shrunk) dominate bowling through peerless death-over containment and breakthroughs.</li>
        <li><strong>d. Flaws &amp; Limitations:</strong> Striker run-outs are attributed to the striker while non-striker run-outs are treated as team state; unobserved environmental factors (pitch wear, evening dew, ground dimensions) are not explicitly in the state vector; and match phases are discretized into 3 discrete bins rather than a continuous 2D surface.</li>
        <li><strong>e. Conclusion:</strong> Objective pre-delivery pressure gating combined with Empirical Bayes shrinkage solves traditional cricket metric distortions, establishing robust, auditable rankings that prioritize high-stakes repeatability over volume padding.</li>
    </ul>
</div>

<h2 class="section-header">Section 1 &mdash; Executive Summary</h2>
<h3 class="subsection-header">1.1 The Challenge of Pressure Evaluation</h3>
<p>
In elite Twenty20 cricket, traditional evaluation metrics&mdash;such as raw batting strike rate, batting average, and bowling economy rate&mdash;fail to distinguish between low-stakes accumulation and performance delivered under acute match pressure. A boundary hit when requiring 6 runs off 2 balls carries vastly greater athletic and tactical value than a boundary hit in a decided blowout. Conversely, conceding a single boundary in a high-leverage death over does not reflect poor execution if the baseline expectancy in that situation is substantially worse.
</p>
<p>
To identify the <strong>most reliable players under pressure</strong>, we design and implement an end-to-end mathematical framework:
</p>
<ul>
    <li><strong>Objective, Independent Pressure Quantification (<i>P<sub>t</sub></i> &isin; [0, 100]):</strong> Pressure is decoupled from player identity and outcome, defined strictly pre-delivery (<i>t</i><sup>&minus;</sup>) as the geometric mean of <strong>Task Difficulty (<i>T<sub>t</sub></i>)</strong> and <strong>Normalized Match Consequence (<i>L</i><sub>norm</sub>(<i>S<sub>t</sub></i>))</strong>.</li>
    <li><strong>Situational Value Added (SVA):</strong> Every delivery is evaluated against a discrete 36-cell empirical baseline tensor calibrated on 186,780 deliveries, computing runs and dismissals added relative to exact match state expectancy.</li>
    <li><strong>Endgame Wicket Capping:</strong> To eliminate mathematical distortion in late-inning run chases where required runs are low, effective wicket valuations are capped by remaining runs (&lambda;<sub>eff</sub> = min(&lambda;<sub>wkt</sub>, <i>R</i><sub>req</sub>)).</li>
    <li><strong>Quota-Based Bowling Normalization:</strong> Conceded extras (wides and no-balls) are penalized in the numerator, while bowling opportunity rates are normalized strictly over legal deliveries.</li>
    <li><strong>Empirical Bayes Shrinkage toward Zero Replacement Level:</strong> Raw situational averages are regressed based on Kish's Effective Sample Size (<i>N</i><sub>eff</sub>), preventing small-sample noise from dominating official leaderboards (<i>K</i><sub>bat</sub> = 600, <i>K</i><sub>bowl</sub> = 500).</li>
</ul>

<h3 class="subsection-header">1.2 Summary of Findings</h3>
<p>
Across 186,780 deliveries spanning 2022&ndash;2026: Exactly <strong>297 batters</strong> and <strong>292 bowlers</strong> met the sustained pressure eligibility threshold (<i>N</i>(<i>P</i> &ge; 50) &ge; 50). Top performers include <strong>Vaibhav Sooryavanshi</strong> (#1 Batting, +0.3487), <strong>Suryakumar Yadav</strong> (#2 Batting, +0.2819), <strong>Rashid Khan</strong> (#1 Bowling, +0.1756), and <strong>Jasprit Bumrah</strong> (#2 Bowling, +0.1541).
</p>

</body>
</html>
"""

    raw_path = "scratch/test_p1_tldr.pdf"
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
    print(f"Page 1 test: total pages = {len(doc)}")
    p1 = doc[0]
    blocks = p1.get_text('blocks')
    print("Blocks on Page 1:", len(blocks))
    print(f"First block: {blocks[0][4][:40]!r}")
    print(f"Last block: y0={blocks[-1][1]:.1f}, y1={blocks[-1][3]:.1f}: {blocks[-1][4][:60]!r}")
    doc.close()

test_p1()
