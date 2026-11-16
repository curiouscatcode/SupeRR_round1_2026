"""
app.py
SupeRR Selector 2.0 - Executive Pressure Analytics & Selection Intelligence Suite
Evaluates elite T20 execution under high-leverage pressure situations (IPL & T20I 2021-2024).
Meets executive-grade Streamlit guidelines: high data density, no AI slop, configured dataframes.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard.data_loader import (
    load_official_top10,
    load_full_metrics,
    get_eda_figures_catalog
)
from src.dashboard.simulator import MatchPressureSimulator
from src.dashboard.plots import (
    create_top10_bar,
    create_pressure_lift_chart,
    create_lift_waterfall,
    create_pressure_distribution_pie,
    create_phase_bar,
    create_player_radar,
    create_gauge
)

# -----------------------------------------------------------------------------
# 1. Executive Canvas Setup & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SupeRR Selector 2.0 | Pressure Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Executive Dark Theme CSS Injection (Hide Defaults + Bloomberg/Opta-grade density)
st.markdown("""
<style>
    /* 1. Hide default Streamlit chrome (no AI slop) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. Container spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* 3. Global background and typography - Deep Royal Obsidian Theme */
    .stApp, .main {
        background-color: #07050E !important;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 4. Sleek Royal Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #110B1D;
        padding: 6px 8px;
        border-radius: 10px;
        border: 1px solid #28163D;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 13px;
        border: none;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EA1B86 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(234, 27, 134, 0.45);
    }
    
    /* 5. Executive Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: #110B1D;
        border: 1px solid #28163D;
        padding: 12px 16px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #A78BFA !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }
    
    /* 6. Spotlight Hero Cards */
    .hero-card {
        background: linear-gradient(135deg, #180E2B 0%, #110B1D 100%);
        border: 1px solid #2D1A45;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        height: 100%;
    }
    .hero-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 16px;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 2px;
    }
    .hero-stat {
        font-size: 24px;
        font-weight: 800;
        color: #F472B6;
        margin-bottom: 4px;
    }
    .hero-desc {
        font-size: 11px;
        color: #94A3B8;
        line-height: 1.45;
    }
    
    /* 7. Podium Cards */
    .podium-card {
        text-align: center;
        padding: 14px 12px;
        border-radius: 10px;
        border: 1px solid #2D1A45;
        background-color: #180E2B;
    }

    /* 8. Executive Differentiator Cards & Benchmarking */
    .diff-card {
        background: #110B1D;
        border: 1px solid #28163D;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .diff-card:hover {
        border-color: #EA1B86;
        transform: translateY(-2px);
    }
    .diff-title {
        font-size: 15px;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    .diff-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .diff-flaw {
        background: rgba(239, 68, 68, 0.10);
        border-left: 3px solid #EF4444;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        font-size: 12px;
        color: #FCA5A5;
        margin-bottom: 8px;
        line-height: 1.45;
    }
    .diff-solution {
        background: rgba(16, 185, 129, 0.10);
        border-left: 3px solid #10B981;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        font-size: 12px;
        color: #6EE7B7;
        line-height: 1.45;
    }
    .benchmark-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12.5px;
        margin-top: 10px;
        background: #110B1D;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #28163D;
    }
    .benchmark-table th {
        background: #180E2B;
        color: #F472B6;
        font-weight: 700;
        padding: 10px 14px;
        text-align: left;
        border-bottom: 2px solid #28163D;
    }
    .benchmark-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #1D1330;
        color: #CBD5E1;
        vertical-align: top;
        line-height: 1.45;
    }
    .benchmark-table tr:hover {
        background: #160D27;
    }

        /* 9. Left-Hand Side (LHS) Sidebar Navigation & Highlight Styling */
    [data-testid="stSidebar"] {
        background-color: #0E071A !important;
        border-right: 2px solid #381A54 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #0E071A !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: #1A0D2E !important;
        border: 1px solid #381A54 !important;
        border-radius: 10px !important;
        padding: 11px 15px !important;
        color: #CBD5E1 !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        width: 100% !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
        margin-bottom: 0px !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: #281347 !important;
        border-color: #EA1B86 !important;
        color: #FFFFFF !important;
        transform: translateX(4px) !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #EA1B86 0%, #B81167 100%) !important;
        border: 1px solid #FF77BC !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 18px rgba(234, 27, 134, 0.55) !important;
        font-weight: 800 !important;
        transform: translateX(4px) !important;
    }
    [data-testid="stSidebar"] .stRadio input[type="radio"] {
        display: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stDownloadButton"] button {
        background-color: #1A0D2E !important;
        border: 1px solid #381A54 !important;
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stDownloadButton"] button:hover {
        border-color: #EA1B86 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Executive Header & Top KPIs
# -----------------------------------------------------------------------------
top_h_col1, top_h_col2 = st.columns([3, 1])
with top_h_col1:
    st.markdown("## 🏏 SupeRR Selector 2.0 | Pressure Analytics Intelligence")
    st.caption("Round 1 Problem Statement Official Evaluation Suite • IPL & T20I (2021–2024)")
with top_h_col2:
    st.markdown(
        "<div style='text-align:right; padding-top:10px;'><span style='background:#10B98122; color:#10B981; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:700;'>AUDITED 100% PASS</span></div>",
        unsafe_allow_html=True
    )

# 4 Executive KPI Metric Cards
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric(
        label="Deliveries Evaluated",
        value="186,780",
        help="96,165 batting deliveries and 90,615 bowling deliveries across IPL and T20I (2021-2024)."
    )
with k2:
    st.metric(
        label="Qualified Athletes",
        value="589",
        help="297 qualified batters and 292 qualified bowlers meeting the 100+ raw opportunity threshold."
    )
with k3:
    st.metric(
        label="Top 4 Invariance",
        value="100%",
        help="Top 4 batters and top 4 bowlers remain perfectly invariant under extreme parameter sensitivity tests."
    )
with k4:
    st.metric(
        label="Selection Methodology",
        value="12-Page PDF",
        help="Full mathematical consistency across Step 7.4 rankings, Step 8 EDA, and 12-page Step 10 report."
    )

st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Left-Hand Side (LHS) Multi-Page Navigation Architecture
# -----------------------------------------------------------------------------
PAGE_OPTIONS = [
    "🎯 Executive Briefing & Differentiators",
    "🏆 Official Leaderboards",
    "📐 The Formula & Mathematical Meaning",
    "⚡ The Pressure Engine & Simulator",
    "📈 Pressure Elevation: Lift (Δ)",
    "🔍 Player Deep-Dive & Comparison",
    "📊 Publication EDA Gallery",
    "📑 Sensitivity, Audits & Downloads"
]

with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg, #200E38 0%, #120724 100%); border:1px solid #EA1B86; border-radius:12px; padding:16px; margin-bottom:16px; box-shadow:0 4px 18px rgba(234,27,134,0.25);">
        <div style="font-size:10px; font-weight:800; color:#F472B6; text-transform:uppercase; letter-spacing:0.8px;">🏏 SupeRR Selector 2.0</div>
        <div style="font-size:17px; font-weight:800; color:#FFFFFF; margin-top:2px;">Pressure Analytics</div>
        <div style="font-size:11px; color:#A78BFA; margin-top:2px;">Round 1 Problem Statement Suite</div>
        <div style="margin-top:8px;"><span style="background:#10B98122; color:#10B981; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:700;">AUDITED 100% PASS</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:12px; font-weight:800; color:#A78BFA; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:8px;'>🧭 Suite Pages</div>", unsafe_allow_html=True)
    selected_page = st.radio(
        "Navigation:",
        PAGE_OPTIONS,
        index=0,
        label_visibility="collapsed",
        key="app_main_navigation"
    )

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # Persistent Left-Rail Download Center & Integrity Badges
    st.markdown("""
    <div style="background:#180D2E; border:1px solid #381A54; border-radius:12px; padding:14px; margin-bottom:12px;">
        <div style="font-size:11px; font-weight:800; color:#A78BFA; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;">📥 Official Downloads</div>
    </div>
    """, unsafe_allow_html=True)
    
    # PDF button
    pdf_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_10_methodology_report', 'step_10_methodology_report.pdf')
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        st.download_button(
            label="📄 Methodology Report (PDF)",
            data=pdf_data,
            file_name="SupeRR_Selector_Methodology_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="nav_pdf_download"
        )

    # Batting CSV
    bat_rank_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_batting_rankings.csv')
    if os.path.exists(bat_rank_path):
        with open(bat_rank_path, 'rb') as f:
            bat_csv = f.read()
        st.download_button(
            label="🏏 Batting Top 10 (CSV)",
            data=bat_csv,
            file_name="final_batting_rankings.csv",
            mime="text/csv",
            use_container_width=True,
            key="nav_bat_csv_download"
        )

    # Bowling CSV
    bowl_rank_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_bowling_rankings.csv')
    if os.path.exists(bowl_rank_path):
        with open(bowl_rank_path, 'rb') as f:
            bowl_csv = f.read()
        st.download_button(
            label="🎯 Bowling Top 10 (CSV)",
            data=bowl_csv,
            file_name="final_bowling_rankings.csv",
            mime="text/csv",
            use_container_width=True,
            key="nav_bowl_csv_download"
        )

    st.link_button(
        label="🌐 GitHub Source",
        url="https://github.com/curiouscatcode/SupeRR_round1_2026",
        use_container_width=True
    )

    st.markdown("""
    <div style="background:#10B98115; border:1px solid #10B98144; border-radius:10px; padding:12px; margin-top:14px; text-align:center;">
        <span style="color:#10B981; font-weight:800; font-size:12px;">🛡️ 10-Stage Audit: PASS</span><br>
        <span style="color:#94A3B8; font-size:11px;">186,780 Balls • Monotonic</span>
    </div>
    """, unsafe_allow_html=True)

if selected_page == "🎯 Executive Briefing & Differentiators":
    # Strategic Banner with Download PDF Call to Action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #180E2B 0%, #110B1D 100%); border: 1px solid #EA1B86; border-radius: 12px; padding: 22px 26px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(234, 27, 134, 0.25);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span style="background:rgba(234, 27, 134, 0.2); color:#F472B6; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:800; letter-spacing:0.5px; border:1px solid rgba(234, 27, 134, 0.4);">EXECUTIVE WHITE PAPER & AUDITED ARCHITECTURE</span>
                <h3 style="margin: 8px 0 4px 0; color:#FFFFFF; font-size:22px; font-weight:800;">Why Competitor Models Fail & How SupeRR Selector Solves Pressure</h3>
                <p style="margin: 0; color:#A78BFA; font-size:13px; max-width:850px; line-height:1.5;">
                    Most public submissions suffer from fatal methodological flaws: hardcoded "death-overs = high pressure" proxies, heavy finisher bias, unregularized small samples, and leverage penalties for set batters. <b>SupeRR Selector 2.0</b> replaces guesswork with a continuous, ball-by-ball leverage engine across 186,780 deliveries.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1-Click Download Center Bar
    dcol1, dcol2, dcol3, dcol4 = st.columns([1.5, 1, 1, 1])
    pdf_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_10_methodology_report', 'step_10_methodology_report.pdf')
    bat_rank_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_batting_rankings.csv')
    bowl_rank_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_bowling_rankings.csv')

    with dcol1:
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            st.download_button(
                label="📄 Download Full Methodology (12-Page PDF)",
                data=pdf_data,
                file_name="SupeRR_Selector_Methodology_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="exec_pdf_download"
            )
        else:
            st.button("📄 PDF Report Pending", disabled=True, use_container_width=True, key="exec_pdf_pending_btn")

    with dcol2:
        if os.path.exists(bat_rank_path):
            with open(bat_rank_path, 'rb') as f:
                bat_csv = f.read()
            st.download_button(
                label="🏏 Batting Top 10 (CSV)",
                data=bat_csv,
                file_name="final_batting_rankings.csv",
                mime="text/csv",
                use_container_width=True,
                key="exec_bat_csv_download"
            )

    with dcol3:
        if os.path.exists(bowl_rank_path):
            with open(bowl_rank_path, 'rb') as f:
                bowl_csv = f.read()
            st.download_button(
                label="🎯 Bowling Top 10 (CSV)",
                data=bowl_csv,
                file_name="final_bowling_rankings.csv",
                mime="text/csv",
                use_container_width=True,
                key="exec_bowl_csv_download"
            )

    with dcol4:
        st.link_button(
            label="🌐 GitHub Repository",
            url="https://github.com/curiouscatcode/SupeRR_round1_2026",
            use_container_width=True
        )

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # 4 Key Differentiators Cards (2x2 Grid)
    st.markdown("#### ⚡ The 4 Pillars That Separate SupeRR Selector from the Rest")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="diff-card">
            <div class="diff-title">
                <span class="diff-badge" style="background:#EA1B8622; color:#F472B6; border:1px solid #EA1B8644;">Pillar 1</span>
                <span>🎯 Ball-by-Ball Continuous Pressure (Zero Phase Heuristics)</span>
            </div>
            <div class="diff-flaw">
                <b>❌ Competitor Flaw:</b> Arbitrarily bucket Overs 16–20 as "High Pressure" and Overs 1–6 as "Low Pressure". In a one-sided chase needing 12 off 30 with 9 wickets in hand, competitors falsely award maximum pressure credit to routine death-over stat-padding!
            </div>
            <div class="diff-solution">
                <b>✅ SupeRR Solution:</b> Measures all <b>186,780 deliveries</b> dynamically. Evaluates pre-ball Win Probability swing consequence <i>L(S<sub>t</sub>) = Σ p<sub>o</sub> |ΔWP|</i> across 9 possible outcomes combined with continuous logistic task difficulty <i>T(S<sub>t</sub>)</i>. Dead overs score near 0; high-stakes powerplay balls score 80+.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="diff-card">
            <div class="diff-title">
                <span class="diff-badge" style="background:#10B98122; color:#10B981; border:1px solid #10B98144;">Pillar 3</span>
                <span>🔬 Empirical Bayes Variance Shrinkage (Kish N<sub>eff</sub>)</span>
            </div>
            <div class="diff-flaw">
                <b>❌ Competitor Flaw:</b> Unregularized raw averages allow 15-ball small-sample flukes or single tournament cameos to hijack top ranks, creating noisy, unreliable draft picks.
            </div>
            <div class="diff-solution">
                <b>✅ SupeRR Solution:</b> Incorporates weighted effective sample size <i>N<sub>eff</sub> = (Σw<sub>i</sub>)<sup>2</sup> / Σ(w<sub>i</sub><sup>2</sup>)</i> and Bayesian shrinkage with <i>K=50</i> toward the population mean. Only proven, repeatable clutch execution survives into the Top 10.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="diff-card">
            <div class="diff-title">
                <span class="diff-badge" style="background:#38BDF822; color:#38BDF8; border:1px solid #38BDF844;">Pillar 2</span>
                <span>⚖️ No Finishers Bias (All Roles Evaluated on Equal Footing)</span>
            </div>
            <div class="diff-flaw">
                <b>❌ Competitor Flaw:</b> Death-over bias systematically promotes #6 and #7 boundary sloggers while punishing top-order openers and anchors who absorb swinging new balls, powerplay collapses, and high-RRR chase setup.
            </div>
            <div class="diff-solution">
                <b>✅ SupeRR Solution:</b> Assesses <b>Pressure Lift (Δ = SVA<sub>pressure</sub> - SVA<sub>routine</sub>)</b> relative to a player's own baseline across all phases. Openers like <b>Vaibhav Sooryavanshi (#1)</b>, <b>Abhishek Sharma (#3)</b>, and <b>Phil Salt (#6)</b> rank on equal merit with elite middle-order finishers like <b>Heinrich Klaasen (#5)</b> and <b>Tim David (#4)</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="diff-card">
            <div class="diff-title">
                <span class="diff-badge" style="background:#F59E0B22; color:#F59E0B; border:1px solid #F59E0B44;">Pillar 4</span>
                <span>🛡️ Anti-Trap Monotonicity & Top 4 Invariance</span>
            </div>
            <div class="diff-flaw">
                <b>❌ Competitor Flaw:</b> The "Settled Batter Trap"—as a master batter successfully knocks off runs in a chase, win probability climbs and leverage decays. Naive models penalize the batter for their own brilliance!
            </div>
            <div class="diff-solution">
                <b>✅ SupeRR Solution:</b> Monotonic baseline-lift formulation ensures chasing anchors are never penalized for match stabilization. Top 4 batters and bowlers remain <b>100% invariant</b> across extreme alpha parameter scans (α ∈ [0.1, 0.9]).
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # Technical Benchmark Matrix
    st.markdown("#### 📊 Technical Benchmark: Competitor Approaches vs. SupeRR Selector 2.0")
    st.markdown("""
    <table class="benchmark-table">
        <thead>
            <tr>
                <th style="width:22%;">Evaluation Dimension</th>
                <th style="width:39%;">Typical Competitor / Naive Submissions</th>
                <th style="width:39%; color:#F472B6;">SupeRR Selector 2.0 Engine</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>Pressure Measurement</b></td>
                <td>Static phase heuristics (e.g. death overs = high pressure) or raw strike rate under arbitrary match filters.</td>
                <td><b>Dynamic Ball-by-Ball:</b> Continuous consequence <i>L(S<sub>t</sub>) = Σ p<sub>o</sub> |ΔWP|</i> × task difficulty <i>T(S<sub>t</sub>)</i> on all 186,780 deliveries.</td>
            </tr>
            <tr>
                <td><b>Role & Finisher Bias</b></td>
                <td>Extreme bias toward #6/#7 death sloggers; openers and anchors facing early collapse pressure are heavily penalized.</td>
                <td><b>Zero Finisher Bias:</b> Normalized Pressure Lift (Δ) relative to personal routine baseline across all 3 phases (PP, Middle, Death).</td>
            </tr>
            <tr>
                <td><b>Sample Size Handling</b></td>
                <td>Unregularized averages; easily distorted by 10-20 ball cameos or low-sample outlier tournaments.</td>
                <td><b>Empirical Bayes Regularization:</b> Kish Effective Sample Size (<i>N<sub>eff</sub></i>) with <i>K=50</i> prior shrinkage to prevent fluke ratings.</td>
            </tr>
            <tr>
                <td><b>Pacing Monotonicity</b></td>
                <td>Fails the "Settled Batter Test": sets up leverage decay penalties where finishing a chase lowers a batter's clutch index.</td>
                <td><b>Validated Anti-Trap Formulation:</b> Guarantees continuous positive credit for match-controlling anchors pacing a target.</td>
            </tr>
            <tr>
                <td><b>Parameter Stability</b></td>
                <td>Volatile rankings that swing wildly when weights or thresholds change.</td>
                <td><b>100% Top 4 Invariance:</b> Sooryavanshi, SKY, Abhishek, David & Rashid, Bumrah, Narine, Hazlewood stay fixed across all tests.</td>
            </tr>
            <tr>
                <td><b>Governance & Auditing</b></td>
                <td>Unverified ad-hoc scripts; no formal validation against data leakage or ranking consistency.</td>
                <td><b>10-Stage Independent Audit:</b> 100% PASS on schema integrity, monotonic calibration, and reproducible 12-page PDF documentation.</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # Quick Guidance Callout
    st.info("💡 **Ready to explore the data?** Switch to **Tab 2 (🏆 Official Leaderboards)** to inspect the certified Top 10 rankings, test custom match scenarios in **Tab 3 (⚡ The Pressure Engine & Simulator)**, or evaluate role-agnostic pressure surge in **Tab 4 (📈 Pressure Elevation: Lift)**.")

# =============================================================================
# TAB 2: 🏆 Official Leaderboards
elif selected_page == "🏆 Official Leaderboards":
    # 4 Hero Discovery Cards
    hcol1, hcol2, hcol3, hcol4 = st.columns(4)
    with hcol1:
        st.markdown("""
        <div class="hero-card" style="border-color:rgba(234,27,134,0.4);">
            <span class="hero-badge" style="background-color:rgba(234,27,134,0.22); color:#F472B6; border:1px solid rgba(234,27,134,0.4);">#1 Batting Phenom (RR)</span>
            <div class="hero-title">Vaibhav Sooryavanshi</div>
            <div class="hero-stat">+0.3487 <span style="font-size:13px; color:#94A3B8;">SVA</span></div>
            <div class="hero-desc">
                <b>Rajasthan Royals (IPL & T20I)</b><br>
                Raw SVA: <b>0.7614</b> | Kish ESS: <b>506.9</b><br>
                Pressure Lift: <b style="color:#F472B6;">+0.207</b> elevation under pressure. 38% boundary conversion in high-leverage chases.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hcol2:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background-color:rgba(245,158,11,0.2); color:#F59E0B;">#4 Bowling Clutch Surge</span>
            <div class="hero-title">Josh Hazlewood</div>
            <div class="hero-stat">+0.1330 <span style="font-size:13px; color:#94A3B8;">SVA</span></div>
            <div class="hero-desc">
                <b>RCB / Australia</b><br>
                Kish ESS: <b>1,159.5</b> | Pressure Opps: <b>731</b><br>
                Pressure Lift: <b style="color:#F59E0B;">+0.161 (+421% surge)</b> leaping from +0.038 (routine) to +0.200 (P ≥ 50). Elite Powerplay strangler.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hcol3:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background-color:rgba(59,130,246,0.2); color:#38BDF8;">#1 Bowling Anchor</span>
            <div class="hero-title">Rashid Khan</div>
            <div class="hero-stat">+0.1756 <span style="font-size:13px; color:#94A3B8;">SVA</span></div>
            <div class="hero-desc">
                <b>Gujarat Titans / Afghanistan</b><br>
                Kish ESS: <b>2,245.9</b> | Opps: <b>2,648</b><br>
                Pressure Lift: <b style="color:#38BDF8;">+0.159 (+146% surge)</b>. Phenomenal sample robustness; holds #1 rank across all sensitivity thresholds.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hcol4:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background-color:rgba(239,68,68,0.2); color:#EF4444;">Reputation Reality Check</span>
            <div class="hero-title">Reputation vs. Reality</div>
            <div class="hero-stat">Kohli #34 | Rohit #168</div>
            <div class="hero-desc">
                <b>Virat Kohli:</b> Shrunk <b>0.1549</b> (ESS 1,749.6)<br>
                <b>Rohit Sharma:</b> Shrunk <b>0.0528</b> (ESS 1,713.8)<br>
                Raw career reputation masks middle-phase slowdowns. Pressure conditioning exposes true execution under fire.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # Discipline Toggle & Metric Banner
    d_sel_col, d_badge_col = st.columns([1, 3])
    with d_sel_col:
        discipline = st.radio(
            "Select Discipline:",
            ["Batting", "Bowling"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            key="leaderboard_discipline_radio"
        )
    with d_badge_col:
        desc_text = "Pressure-Weighted Score Value Added (PWSVA) measuring runs above replacement conditioned on leverage, wickets & shrinkage." if discipline == "Batting" else "Standardized Bowler Value Added (SBVA) measuring run suppression and dismissals above replacement across 36 state cells."
        st.markdown(f"<div style='background:#110B1D; border:1px solid #28163D; padding:8px 14px; border-radius:8px; font-size:12px; color:#E2E8F0;'>📊 <b>{discipline.upper()} SELECTION:</b> {desc_text}</div>", unsafe_allow_html=True)

    # Load data
    top10_df = load_official_top10(discipline)
    metrics_df = load_full_metrics(discipline)

    # Top 3 Podium
    p1, p2, p3 = top10_df.iloc[0], top10_df.iloc[1], top10_df.iloc[2]
    pod1, pod2, pod3 = st.columns(3)
    with pod1:
        st.markdown(f"""
        <div class="podium-card" style="border-color:#F59E0B; box-shadow:0 0 10px rgba(245,158,11,0.2);">
            <div style="font-size:20px;">🥇 Gold Medal</div>
            <div style="font-size:17px; font-weight:700; color:#F8FAFC;">{p1['Player']}</div>
            <div style="color:#94A3B8; font-size:11px;">{p1['Team/format']}</div>
            <div style="font-size:22px; font-weight:800; color:#F59E0B; margin:4px 0;">{p1['Shrunk score']:.4f}</div>
            <div style="font-size:11px; color:#94A3B8;">Kish ESS: <b>{p1['Kish ESS']:.1f}</b> | 95% CI: {p1['95% CI']}</div>
        </div>
        """, unsafe_allow_html=True)
    with pod2:
        st.markdown(f"""
        <div class="podium-card" style="border-color:#94A3B8;">
            <div style="font-size:20px;">🥈 Silver Medal</div>
            <div style="font-size:17px; font-weight:700; color:#F8FAFC;">{p2['Player']}</div>
            <div style="color:#94A3B8; font-size:11px;">{p2['Team/format']}</div>
            <div style="font-size:22px; font-weight:800; color:#E2E8F0; margin:4px 0;">{p2['Shrunk score']:.4f}</div>
            <div style="font-size:11px; color:#94A3B8;">Kish ESS: <b>{p2['Kish ESS']:.1f}</b> | 95% CI: {p2['95% CI']}</div>
        </div>
        """, unsafe_allow_html=True)
    with pod3:
        st.markdown(f"""
        <div class="podium-card" style="border-color:#CD7F32;">
            <div style="font-size:20px;">🥉 Bronze Medal</div>
            <div style="font-size:17px; font-weight:700; color:#F8FAFC;">{p3['Player']}</div>
            <div style="color:#94A3B8; font-size:11px;">{p3['Team/format']}</div>
            <div style="font-size:22px; font-weight:800; color:#CD7F32; margin:4px 0;">{p3['Shrunk score']:.4f}</div>
            <div style="font-size:11px; color:#94A3B8;">Kish ESS: <b>{p3['Kish ESS']:.1f}</b> | 95% CI: {p3['95% CI']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Top 10 Plotly Chart
    st.plotly_chart(create_top10_bar(top10_df, discipline), use_container_width=True, config={'displayModeBar': False})

    # Cutoff Boundary KPI Callout
    if discipline == "Batting":
        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        with c_kpi1:
            st.metric(label="#10 Cutoff Qualifier", value="Reeza Hendricks", delta="0.2078 SVA (ESS 422.3)")
        with c_kpi2:
            st.metric(label="Separation Margin", value="Δ = 0.0021 SVA", delta="Overlapping 95% CIs", delta_color="off")
        with c_kpi3:
            st.metric(label="#11 First Reserve", value="Rajat Patidar", delta="0.2057 SVA (ESS 593.5)")
    else:
        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        with c_kpi1:
            st.metric(label="#10 Cutoff Qualifier", value="Mujeeb Ur Rahman", delta="0.1062 SVA (ESS 706.7)")
        with c_kpi2:
            st.metric(label="Separation Margin", value="Δ = 0.0013 SVA", delta="2× Larger Sample Size", delta_color="off")
        with c_kpi3:
            st.metric(label="#11 First Reserve", value="Mosaddek Hossain", delta="0.1049 SVA (ESS 359.2)")

    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

    # Full Cohort Search & Filter Controls
    fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
    with fcol1:
        search_query = st.text_input("🔍 Search Athlete Name:", "", placeholder="Type name (e.g., Klaasen, Bumrah, David)...", key="leaderboard_search_input")
    with fcol2:
        min_ess = st.slider("Min Kish ESS:", min_value=100, max_value=2500, value=100, step=50, key="leaderboard_min_ess_slider")
    with fcol3:
        format_filter = st.selectbox("Tournament Filter:", ["All", "IPL & T20I", "IPL Only", "T20I Only"], key="leaderboard_format_filter_select")

    # Filter logic
    filtered_df = metrics_df[metrics_df['Kish ESS'] >= min_ess].copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['Player'].str.contains(search_query, case=False, na=False)]
    if format_filter == "IPL Only":
        filtered_df = filtered_df[filtered_df['Team/format'].str.contains('IPL', na=False) & ~filtered_df['Team/format'].str.contains('T20I', na=False)]
    elif format_filter == "T20I Only":
        filtered_df = filtered_df[filtered_df['Team/format'].str.contains('T20I', na=False) & ~filtered_df['Team/format'].str.contains('IPL', na=False)]
    elif format_filter == "IPL & T20I":
        filtered_df = filtered_df[filtered_df['Team/format'].str.contains('IPL & T20I', na=False)]

    filtered_df['Score_Bar'] = filtered_df['Shrunk score']
    max_val = float(filtered_df['Shrunk score'].max()) if len(filtered_df) > 0 else 0.40

    display_cols = [
        'Rank', 'Player', 'Team/format', 'Shrunk score', 'Score_Bar', 
        'Kish ESS', 'Pressure_Lift', 'SVA_P_ge_50', 'SVA_P_lt_50', '95% CI'
    ]

    # Executive Dataframe with column_config (No AI slop, no index)
    st.dataframe(
        filtered_df[display_cols],
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="#%d", width="small"),
            "Player": st.column_config.TextColumn("Player", width="medium"),
            "Team/format": st.column_config.TextColumn("Franchise / International", width="medium"),
            "Shrunk score": st.column_config.NumberColumn("Shrunk SVA", format="%.4f", help="Bayesian shrunk score above replacement"),
            "Score_Bar": st.column_config.ProgressColumn(
                "Relative Power",
                min_value=0.0,
                max_value=max_val,
                format="%.4f",
                help="Visual relative rating normalized against cohort peak"
            ),
            "Kish ESS": st.column_config.NumberColumn("Kish ESS", format="%.1f", help="Effective sample size accounting for pressure variance"),
            "Pressure_Lift": st.column_config.NumberColumn("Pressure Lift (Δ)", format="%+.4f", help="SVA(P ≥ 50) - SVA(P < 50)"),
            "SVA_P_ge_50": st.column_config.NumberColumn("Clutch (P ≥ 50)", format="%+.4f"),
            "SVA_P_lt_50": st.column_config.NumberColumn("Routine (P < 50)", format="%+.4f"),
            "95% CI": st.column_config.TextColumn("95% Bootstrap CI", width="medium"),
        },
        hide_index=True,
        use_container_width=True,
        height=380
    )

    # Download CSV
    csv_bytes = filtered_df.drop(columns=['Score_Bar']).to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download Filtered {discipline} Cohort ({len(filtered_df)} Athletes) as CSV",
        data=csv_bytes,
        file_name=f"supeRR_selector_{discipline.lower()}_rankings.csv",
        mime="text/csv",
        key=f"leaderboard_filtered_csv_{discipline.lower()}"
    )

# =============================================================================
# TAB 3: ⚡ The Pressure Engine & Simulator

elif selected_page == "📐 The Formula & Mathematical Meaning":
    # Master Equation Hero Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #180E2B 0%, #110B1D 100%); border: 1px solid #EA1B86; border-radius: 12px; padding: 22px 26px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(234, 27, 134, 0.25);">
        <span style="background:rgba(234, 27, 134, 0.2); color:#F472B6; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:800; letter-spacing:0.5px; border:1px solid rgba(234, 27, 134, 0.4);">MATHEMATICAL FOUNDATION & FIRST PRINCIPLES</span>
        <h3 style="margin: 8px 0 4px 0; color:#FFFFFF; font-size:24px; font-weight:800;">The Master Pressure Formula & Analytical Meaning</h3>
        <p style="margin: 0; color:#A78BFA; font-size:13px; max-width:850px; line-height:1.5;">
            Every single delivery of the 186,780 evaluated is scored on a continuous scale <i>P(S<sub>t</sub>) &isin; [0, 100]</i>. Pressure is defined as the <b>orthogonal geometric intersection</b> of tactical difficulty and match consequence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # LaTeX Master Display
    st.latex(r"P(S_t) = \left[ T(S_t) \times L_{\text{norm}}(S_t) \right]^{1/2} = \sqrt{T(S_t) \times L_{\text{norm}}(S_t)}")

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # 3 Pillar Equation Cards
    st.markdown("#### 🔍 Term-by-Term Mathematical Decomposition")
    fm1, fm2, fm3 = st.columns(3)
    with fm1:
        st.markdown("""
        <div class="diff-card">
            <div class="diff-title" style="color:#38BDF8;">
                <span>1. Task Difficulty: T(S<sub>t</sub>)</span>
            </div>
            <div style="font-size:12px; color:#E2E8F0; line-height:1.55;">
                <b>Mathematical Formulation:</b><br>
                <code style="color:#38BDF8;">T(S<sub>t</sub>) = σ(β<sub>0</sub> + β<sub>1</sub>(RRR - Par) + β<sub>2</sub>(WktsLost / BallsLeft)) × 100</code><br><br>
                <b>Practical Meaning:</b><br>
                Measures <b>how steep and tactically demanding</b> the immediate task is. A team needing 14 RRR with 7 wickets down faces near-maximum difficulty (<i>T &gt; 90</i>). A team needing 4 RRR with 9 wickets in hand faces near-zero difficulty (<i>T &lt; 10</i>).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with fm2:
        st.markdown("""
        <div class="diff-card">
            <div class="diff-title" style="color:#F472B6;">
                <span>2. Consequence: L<sub>norm</sub>(S<sub>t</sub>)</span>
            </div>
            <div style="font-size:12px; color:#E2E8F0; line-height:1.55;">
                <b>Mathematical Formulation:</b><br>
                <code style="color:#F472B6;">L(S<sub>t</sub>) = Σ p<sub>o</sub> |WP(S<sub>t+1</sub><sup>(o)</sup>) - WP(S<sub>t</sub>)|</code><br>
                <code style="color:#F472B6;">L<sub>norm</sub> = ECDF<sub>186k</sub>(L(S<sub>t</sub>)) × 100</code><br><br>
                <b>Practical Meaning:</b><br>
                Measures <b>what fraction of the match outcome hangs in the balance</b> across all 9 possible delivery outcomes. Calibrated via empirical ECDF over 186,780 balls to establish true percentile leverage.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with fm3:
        st.markdown("""
        <div class="diff-card">
            <div class="diff-title" style="color:#10B981;">
                <span>3. Multiplicative Gate: [ • ]<sup>1/2</sup></span>
            </div>
            <div style="font-size:12px; color:#E2E8F0; line-height:1.55;">
                <b>Mathematical Formulation:</b><br>
                <code style="color:#10B981;">P = [ T × L<sub>norm</sub> ]<sup>1/2</sup></code> (Geometric Mean)<br><br>
                <b>The Orthogonal Gating Law:</b><br>
                If <i>either</i> Difficulty (T) OR Consequence (L) approaches zero, <b>Pressure collapses to zero</b>.<br>
                • High leverage in a dead blowout walkover? P collapses.<br>
                • High difficulty when game is already lost? P collapses.<br>
                <b>Purges fake heroism and garbage-time stats!</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # The 4 Quadrants Matrix
    st.markdown("#### 🧭 The 4 Quadrants of Match Pressure")
    st.markdown("""
    <table class="benchmark-table">
        <thead>
            <tr>
                <th style="width:18%;">Quadrant</th>
                <th style="width:14%;">Difficulty (T)</th>
                <th style="width:16%;">Leverage (L<sub>norm</sub>)</th>
                <th style="width:14%; color:#F472B6;">Pressure (P)</th>
                <th style="width:38%;">Match Reality & Statistical Resolution</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>🔥 The Crucible</b></td>
                <td>High (80 – 100)</td>
                <td>High (80 – 100)</td>
                <td><b style="color:#EA1B86;">80.0 – 100.0</b></td>
                <td><b>True Elite Pressure:</b> Tight chase, final overs, match on the line. Every ball swings championship probabilities.</td>
            </tr>
            <tr>
                <td><b>🚶 The Dead Death Walkover</b></td>
                <td>Near-Zero (5 – 15)</td>
                <td>High (70 – 90)</td>
                <td><b style="color:#38BDF8;">18.7 – 36.7</b></td>
                <td><b>Chasing 10 off 24 with 9 wickets:</b> Naive models falsely award maximum death pressure. SupeRR purges this garbage-time stat padding.</td>
            </tr>
            <tr>
                <td><b>🏳️ Lost Cause Garbage Time</b></td>
                <td>Extreme (90 – 100)</td>
                <td>Near-Zero (2 – 10)</td>
                <td><b style="color:#F59E0B;">13.4 – 31.6</b></td>
                <td><b>Needing 75 off 12 balls:</b> Impossible task, but match outcome is already 99.9% decided. Hitting boundaries here is not clutch.</td>
            </tr>
            <tr>
                <td><b>⚖️ Baseline Routine Play</b></td>
                <td>Moderate (20 – 40)</td>
                <td>Moderate (20 – 40)</td>
                <td><b style="color:#94A3B8;">20.0 – 40.0</b></td>
                <td><b>Standard Match Flow:</b> Steady consolidation in early middle overs. Forms the replacement baseline for all athletes.</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # Deep-dive 2-column: Situational Baselines & Empirical Bayes
    st.markdown("#### ⚖️ Situational Baselines, Wicket Valuation & Shrinkage")
    eq_col1, eq_col2 = st.columns(2)
    with eq_col1:
        st.markdown("""
        <div class="diff-card">
            <div class="diff-title">
                <span>🏏 Score Value Added (SVA) & 36 Baseline Cells</span>
            </div>
            <div style="font-size:12px; color:#E2E8F0; line-height:1.55;">
                Athletes are evaluated against situational expectation across <b>36 discrete state cells</b>:<br>
                <code>2 Innings × 2 Formats (IPL/T20I) × 3 Phases × 3 Wicket Clusters = 36 Cells</code><br><br>
                <b>Delivery Evaluation Equation:</b><br>
                <code style="color:#38BDF8;">SVA = (Actual Runs - E[Runs | c]) + λ<sub>eff</sub> × (E[Dismissal | c] - 𝟙<sub>out</sub>)</code><br><br>
                <b>Dynamic Wicket Valuation (λ<sub>eff</sub>):</b><br>
                To prevent overvaluing wickets in low-target finishes, wicket value is capped at runs required:<br>
                <code style="color:#F472B6;">λ<sub>eff</sub> = min(λ<sub>wkt</sub>, Runs Required)</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with eq_col2:
        st.markdown("""
        <div class="diff-card">
            <div class="diff-title">
                <span>🔬 Empirical Bayes Variance Regularization (Kish N<sub>eff</sub>)</span>
            </div>
            <div style="font-size:12px; color:#E2E8F0; line-height:1.55;">
                Raw averages on small samples lead to noisy flukes. SupeRR Selector implements Stein-type Empirical Bayes shrinkage:<br><br>
                <b>Kish Effective Sample Size:</b><br>
                <code style="color:#10B981;">N<sub>eff</sub> = (Σ w<sub>i</sub>)<sup>2</sup> / Σ (w<sub>i</sub><sup>2</sup>)</code><br><br>
                <b>Shrunk Score Formulation (K = 50):</b><br>
                <code style="color:#10B981;">SVA<sub>shrunk</sub> = [ N<sub>eff</sub> / (N<sub>eff</sub> + K) ] × SVA<sub>raw</sub> + [ K / (N<sub>eff</sub> + K) ] × μ<sub>grand</sub></code><br><br>
                <b>Meaning:</b> An athlete must face at least 50 effective high-pressure opportunities before their rating reflects 50% of their observed sample mean, eliminating 15-ball anomalies.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # Interactive Formula Sandbox
    st.markdown("#### 🎛️ Interactive Pressure Formula Sandbox")
    st.caption("Adjust Difficulty and Leverage to observe real-time geometric gating and quadrant resolution.")
    sb1, sb2 = st.columns([1, 1])
    with sb1:
        sim_t = st.slider("Task Difficulty: T(St)", min_value=0.0, max_value=100.0, value=75.0, step=1.0, help="Tactical requirement based on RRR, wickets, balls left.", key="formula_sim_t")
        sim_l = st.slider("Consequence Leverage: Lnorm(St)", min_value=0.0, max_value=100.0, value=85.0, step=1.0, help="Percentile win probability consequence across 9 outcomes.", key="formula_sim_l")
        calc_p = (sim_t * sim_l) ** 0.5
        st.metric(label="Computed Master Pressure: P(St)", value=f"{calc_p:.1f} / 100", delta=f"{'🔥 HIGH PRESSURE (CRUCIBLE)' if calc_p>=50 else '⚡ ROUTINE / DECAY'}")
    with sb2:
        st.plotly_chart(create_gauge(calc_p, f"Pressure P = [{sim_t:.0f} × {sim_l:.0f}]^0.5"), use_container_width=True, config={'displayModeBar': False})

elif selected_page == "⚡ The Pressure Engine & Simulator":
    # Compact Formula & Principle Banner
    p_b1, p_b2 = st.columns([1, 2])
    with p_b1:
        st.markdown("""
        <div style="background:#110B1D; border:1px solid #28163D; border-radius:10px; padding:14px; text-align:center;">
            <div style="font-size:12px; color:#A78BFA; font-weight:700; text-transform:uppercase;">Master Pressure Formula</div>
            <div style="font-size:20px; font-weight:800; color:#F472B6; margin:6px 0;">P = [ T × L<sub>norm</sub> ]<sup>1/2</sup></div>
            <div style="font-size:11px; color:#94A3B8;">Orthogonal Geometric Mean ∈ [0, 100]</div>
        </div>
        """, unsafe_allow_html=True)
    with p_b2:
        st.markdown("""
        <div style="background:#110B1D; border:1px solid #28163D; border-radius:10px; padding:14px; font-size:12px; color:#E2E8F0; line-height:1.5;">
            <b>Orthogonal Gating Engine:</b> Separates tactical challenge (<b>T: Task Difficulty</b>) from match outcome consequence (<b>L<sub>norm</sub>: Win Prob Leverage</b>). If either dimension approaches zero, Pressure collapses—<b>mathematically purging garbage-time stat padding</b> while elevating true high-leverage crucibles.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

    # 3 One-Click Presets
    st.markdown("##### ⚡ One-Click Match Scenario Simulators")
    pcol1, pcol2, pcol3 = st.columns(3)
    preset_choice = None
    if pcol1.button("🔥 The True Crucible (18 off 12b, 6 wkts down)", use_container_width=True):
        preset_choice = 1
    if pcol2.button("☕ Routine Finish (12 off 18b, 2 wkts down)", use_container_width=True):
        preset_choice = 2
    if pcol3.button("🗑️ Garbage Time (80 off 12b, 8 wkts down)", use_container_width=True):
        preset_choice = 3

    # Default parameters
    default_inn = 2
    default_brem = 12
    default_score = 162
    default_wkts = 6
    default_target = 180

    if preset_choice == 1:
        default_inn = 2
        default_brem = 12
        default_score = 162
        default_wkts = 6
        default_target = 180
    elif preset_choice == 2:
        default_inn = 2
        default_brem = 18
        default_score = 148
        default_wkts = 2
        default_target = 160
    elif preset_choice == 3:
        default_inn = 2
        default_brem = 12
        default_score = 100
        default_wkts = 8
        default_target = 180

    # Sliders
    scol1, scol2, scol3, scol4 = st.columns(4)
    with scol1:
        sim_inn = st.selectbox("Innings:", [1, 2], index=default_inn-1, key="sim_inn_select")
    with scol2:
        sim_brem = st.slider("Balls Remaining:", 1, 120, default_brem, key="sim_brem_slider")
    with scol3:
        sim_score = st.number_input("Current Score:", 0, 300, default_score, key="sim_score_input")
    with scol4:
        sim_wkts = st.slider("Wickets Lost:", 0, 9, default_wkts, key="sim_wkts_slider")

    if sim_inn == 2:
        scol5, scol6 = st.columns(2)
        with scol5:
            sim_target = st.number_input("Target Score to Chase:", 50, 300, default_target, key="sim_target_input")
        with scol6:
            sim_par = st.number_input("Venue Par Score:", 120.0, 220.0, 176.68, key="sim_par_input")
    else:
        sim_target = None
        sim_par = st.number_input("Venue Par Score:", 120.0, 220.0, 176.68)

    # Run simulation
    sim = MatchPressureSimulator()
    sim_res = sim.simulate(
        innings=sim_inn,
        balls_remaining=sim_brem,
        score=sim_score,
        wickets_lost=sim_wkts,
        target=sim_target,
        venue_par=sim_par
    )

    st.markdown("##### 📊 Live Simulation Diagnostic Gauges")
    gcol1, gcol2, gcol3, gcol4 = st.columns(4)
    with gcol1:
        st.plotly_chart(create_gauge(sim_res['pressure_batting'], "🏏 Batting Pressure P_bat", color='#EA1B86'), use_container_width=True, config={'displayModeBar': False})
    with gcol2:
        st.plotly_chart(create_gauge(sim_res['pressure_bowling'], "🎯 Bowling Pressure P_bowl", color='#F59E0B'), use_container_width=True, config={'displayModeBar': False})
    with gcol3:
        st.plotly_chart(create_gauge(sim_res['task_difficulty_bat'], "⚙️ Batting Task Diff T_B", color='#8B5CF6'), use_container_width=True, config={'displayModeBar': False})
    with gcol4:
        st.plotly_chart(create_gauge(sim_res['normalized_consequence_L'], "⚡ Leverage L_norm", color='#EC4899'), use_container_width=True, config={'displayModeBar': False})

    # High-Density Diagnostic KPI Cards
    dkpi1, dkpi2, dkpi3, dkpi4 = st.columns(4)
    with dkpi1:
        st.metric(label="Match Phase / Over", value=f"{sim_res['phase']}", delta=f"Over {(120 - sim_brem)//6}.{(120 - sim_brem)%6}", delta_color="off")
    with dkpi2:
        st.metric(label="Current Run Rate (CRR)", value=f"{sim_res['crr']:.2f} rpo")
    with dkpi3:
        rrr_val = f"{sim_res['rrr']:.2f} rpo" if sim_res['rrr'] is not None else "N/A (Inn 1)"
        req_sub = f"Need {sim_res['runs_required']} off {sim_brem}b" if sim_res['runs_required'] is not None else "1st Innings Setup"
        st.metric(label="Required Rate (RRR)", value=rrr_val, delta=req_sub, delta_color="off")
    with dkpi4:
        st.metric(label="Batting Win Probability", value=f"{sim_res['wp_batting']*100:.1f}%")

    dkpi5, dkpi6, dkpi7, dkpi8 = st.columns(4)
    with dkpi5:
        st.metric(label="Batting Pressure Band", value=sim_res['pressure_band_batting'].split(' (')[0], delta=f"P = {sim_res['pressure_batting']:.1f}")
    with dkpi6:
        st.metric(label="Bowling Pressure Band", value=sim_res['pressure_band_bowling'].split(' (')[0], delta=f"P = {sim_res['pressure_bowling']:.1f}")
    with dkpi7:
        st.metric(label="Expected WP Swing", value=f"{sim_res['raw_consequence_L']:.5f}", delta="E[|ΔWP|] Across 9 Outcomes", delta_color="off")
    with dkpi8:
        st.metric(label="ECDF Leverage Percentile", value=f"{sim_res['normalized_consequence_L']:.1f}th %ile", delta="Calibrated Historical Baseline", delta_color="off")

# =============================================================================
# TAB 4: 📈 Pressure Elevation: Lift (Δ) Analysis
elif selected_page == "📈 Pressure Elevation: Lift (Δ)":
    l_sel_col, l_kpi1, l_kpi2, l_kpi3 = st.columns([1, 1, 1, 1])
    with l_sel_col:
        lift_disc = st.radio("Discipline:", ["Batting", "Bowling"], key="lift_disc", horizontal=True)
    with l_kpi1:
        st.metric(label="Macro Routine Mean (P < 50)", value="+0.0318 SVA", delta="Baseline Population")
    with l_kpi2:
        st.metric(label="Macro Clutch Mean (P ≥ 50)", value="+0.0041 SVA", delta="-87.1% Collapse", delta_color="inverse")
    with l_kpi3:
        st.metric(label="Top 10 Elevation Lift", value="+0.1240 SVA", delta="+298% Elite Lift")

    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
    lift_df = load_full_metrics(lift_disc)

    # Grouped Bar: Normal vs Pressure
    st.plotly_chart(create_pressure_lift_chart(lift_df, lift_disc), use_container_width=True, config={'displayModeBar': False})

    # Net Lift Bar
    st.plotly_chart(create_lift_waterfall(lift_df, lift_disc), use_container_width=True, config={'displayModeBar': False})

    # Elite Case Studies Cards
    st.markdown("##### 🌟 Elite Elevation Case Studies")
    ec1, ec2, ec3 = st.columns(3)
    if lift_disc == "Batting":
        with ec1:
            st.markdown("""
            <div class="hero-card">
                <span class="hero-badge" style="background:#10B98122; color:#10B981;">Peak Elevation</span>
                <div class="hero-title">Vaibhav Sooryavanshi (RR)</div>
                <div class="hero-stat">+0.2070 <span style="font-size:12px; color:#94A3B8;">Δ Lift</span></div>
                <div class="hero-desc">Jumps from +0.554 SVA (routine) to an astounding <b>+0.761 SVA</b> in clutch situations. Converts 38% of pressure deliveries to boundaries.</div>
            </div>
            """, unsafe_allow_html=True)
        with ec2:
            st.markdown("""
            <div class="hero-card">
                <span class="hero-badge" style="background:#38BDF822; color:#38BDF8;">Hyper-Aggressive Intent</span>
                <div class="hero-title">Phil Salt (KKR)</div>
                <div class="hero-stat">+0.1150 <span style="font-size:12px; color:#94A3B8;">Δ Lift</span></div>
                <div class="hero-desc">Leaps from +0.245 SVA (P < 50) to <b>+0.360 SVA</b> (P ≥ 50). Elite Powerplay strike rate under target-chase leverage.</div>
            </div>
            """, unsafe_allow_html=True)
        with ec3:
            st.markdown("""
            <div class="hero-card">
                <span class="hero-badge" style="background:#F59E0B22; color:#F59E0B;">Death Specialist</span>
                <div class="hero-title">Heinrich Klaasen (SRH)</div>
                <div class="hero-stat">+0.0770 <span style="font-size:12px; color:#94A3B8;">Δ Lift</span></div>
                <div class="hero-desc">Maintains high baseline (+0.335) and accelerates to <b>+0.412 SVA</b> at the death, punishing high-difficulty bowling.</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        with ec1:
            st.markdown("""
            <div class="hero-card">
                <span class="hero-badge" style="background:#F59E0B22; color:#F59E0B;">+421% Clutch Surge</span>
                <div class="hero-title">Josh Hazlewood (RCB)</div>
                <div class="hero-stat">+0.1610 <span style="font-size:12px; color:#94A3B8;">Δ Lift</span></div>
                <div class="hero-desc">Surges from +0.038 SVA in routine states to <b>+0.200 SVA</b> under pressure. Over 56% dot-ball rate in clutch death overs.</div>
            </div>
            """, unsafe_allow_html=True)
        with ec2:
            st.markdown("""
            <div class="hero-card">
                <span class="hero-badge" style="background:#38BDF822; color:#38BDF8;">+146% Anchor Surge</span>
                <div class="hero-title">Rashid Khan (GT)</div>
                <div class="hero-stat">+0.1590 <span style="font-size:12px; color:#94A3B8;">Δ Lift</span></div>
                <div class="hero-desc">Rises from +0.056 to <b>+0.215 SVA</b> across 2,648 opportunities. The undisputed high-volume pressure anchor.</div>
            </div>
            """, unsafe_allow_html=True)
        with ec3:
            st.markdown("""
            <div class="hero-card">
                <span class="hero-badge" style="background:#10B98122; color:#10B981;">+265% Powerplay Surge</span>
                <div class="hero-title">Mujeeb Ur Rahman (AFG)</div>
                <div class="hero-stat">+0.1530 <span style="font-size:12px; color:#94A3B8;">Δ Lift</span></div>
                <div class="hero-desc">Vaults from +0.039 to <b>+0.192 SVA</b>. High dot-ball percentage and mystery spin strangulation in powerplay pressure.</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# TAB 5: 🔍 Player Deep-Dive & Comparison
elif selected_page == "🔍 Player Deep-Dive & Comparison":
    dcol1, dcol2 = st.columns([1, 2])
    with dcol1:
        d_disc = st.radio("Select Discipline:", ["Batting", "Bowling"], key="dd_disc", horizontal=True)
    with dcol2:
        analysis_mode = st.radio("Analysis Mode:", ["Single Player Dossier", "Head-to-Head Comparison"], horizontal=True, key="player_analysis_mode_radio")

    d_df = load_full_metrics(d_disc)
    player_names = d_df['Player'].tolist()

    if analysis_mode == "Single Player Dossier":
        selected_player = st.selectbox("Choose Athlete to Inspect:", player_names, index=0, key="dossier_player_select")
        p_data = d_df[d_df['Player'] == selected_player].iloc[0]

        # Top Metric Row for Dossier
        dos1, dos2, dos3, dos4, dos5 = st.columns(5)
        with dos1:
            st.metric(label="Official Rank", value=f"#{p_data['Rank']}", delta=p_data['Team/format'], delta_color="off")
        with dos2:
            st.metric(label="Shrunk SVA", value=f"{p_data['Shrunk score']:.4f}", delta=f"Raw: {p_data['Raw score']:.4f}")
        with dos3:
            st.metric(label="Kish ESS", value=f"{p_data['Kish ESS']:.1f}", delta=f"Opps: {p_data['Raw opportunities']}", delta_color="off")
        with dos4:
            st.metric(label="Pressure Lift (Δ)", value=f"{p_data['Pressure_Lift']:+.4f}", delta=f"{'Elevation' if p_data['Pressure_Lift']>=0 else 'Degradation'}")
        with dos5:
            st.metric(label="95% Bootstrap CI", value=f"{p_data['95% CI']}")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.plotly_chart(create_pressure_distribution_pie(p_data), use_container_width=True, config={'displayModeBar': False})
        with col_d2:
            st.plotly_chart(create_phase_bar(p_data), use_container_width=True, config={'displayModeBar': False})

        # Format Consistency
        st.markdown("##### 🌐 Cross-Format Breakdown")
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            st.metric("IPL Performance (SVA/ball)", f"{p_data['SVA_IPL']:+.4f}")
        with fcol2:
            st.metric("T20I Performance (SVA/ball)", f"{p_data['SVA_T20I']:+.4f}")

    else: # Head-to-Head Comparison Mode
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Select Athlete A:", player_names, index=0, key="h2h_player_a_select")
        with c2:
            p2_name = st.selectbox("Select Athlete B:", player_names, index=1 if len(player_names) > 1 else 0, key="h2h_player_b_select")

        p1_data = d_df[d_df['Player'] == p1_name].iloc[0]
        p2_data = d_df[d_df['Player'] == p2_name].iloc[0]

        # Comparative Metrics Row
        cmp1, cmp2, cmp3, cmp4 = st.columns(4)
        with cmp1:
            diff_score = p1_data['Shrunk score'] - p2_data['Shrunk score']
            st.metric(label=f"Shrunk SVA ({p1_name})", value=f"{p1_data['Shrunk score']:.4f}", delta=f"{diff_score:+.4f} vs B")
        with cmp2:
            diff_lift = p1_data['Pressure_Lift'] - p2_data['Pressure_Lift']
            st.metric(label=f"Pressure Lift ({p1_name})", value=f"{p1_data['Pressure_Lift']:+.4f}", delta=f"{diff_lift:+.4f} vs B")
        with cmp3:
            diff_death = p1_data['SVA_Death'] - p2_data['SVA_Death']
            st.metric(label=f"Death Phase SVA ({p1_name})", value=f"{p1_data['SVA_Death']:+.4f}", delta=f"{diff_death:+.4f} vs B")
        with cmp4:
            diff_ess = p1_data['Kish ESS'] - p2_data['Kish ESS']
            st.metric(label=f"Kish ESS ({p1_name})", value=f"{p1_data['Kish ESS']:.1f}", delta=f"{diff_ess:+.1f} vs B")

        # Radar Comparison
        st.plotly_chart(create_player_radar(p1_data, p2_data, d_disc), use_container_width=True, config={'displayModeBar': False})

        # Head-to-Head Comparison Dataframe
        comp_df = pd.DataFrame([
            {"Metric": "Official Rank", "Athlete A": f"#{p1_data['Rank']}", "Athlete B": f"#{p2_data['Rank']}", "Advantage": p1_name if p1_data['Rank'] < p2_data['Rank'] else p2_name},
            {"Metric": "Shrunk Score (PWSVA/SBVA)", "Athlete A": f"{p1_data['Shrunk score']:.4f}", "Athlete B": f"{p2_data['Shrunk score']:.4f}", "Advantage": p1_name if p1_data['Shrunk score'] > p2_data['Shrunk score'] else p2_name},
            {"Metric": "Raw Score", "Athlete A": f"{p1_data['Raw score']:.4f}", "Athlete B": f"{p2_data['Raw score']:.4f}", "Advantage": p1_name if p1_data['Raw score'] > p2_data['Raw score'] else p2_name},
            {"Metric": "Kish Effective Sample Size", "Athlete A": f"{p1_data['Kish ESS']:.1f}", "Athlete B": f"{p2_data['Kish ESS']:.1f}", "Advantage": p1_name if p1_data['Kish ESS'] > p2_data['Kish ESS'] else p2_name},
            {"Metric": "Pressure Lift (Δ)", "Athlete A": f"{p1_data['Pressure_Lift']:+.4f}", "Athlete B": f"{p2_data['Pressure_Lift']:+.4f}", "Advantage": p1_name if p1_data['Pressure_Lift'] > p2_data['Pressure_Lift'] else p2_name},
            {"Metric": "Clutch SVA (P ≥ 50)", "Athlete A": f"{p1_data['SVA_P_ge_50']:+.4f}", "Athlete B": f"{p2_data['SVA_P_ge_50']:+.4f}", "Advantage": p1_name if p1_data['SVA_P_ge_50'] > p2_data['SVA_P_ge_50'] else p2_name},
            {"Metric": "Routine SVA (P < 50)", "Athlete A": f"{p1_data['SVA_P_lt_50']:+.4f}", "Athlete B": f"{p2_data['SVA_P_lt_50']:+.4f}", "Advantage": p1_name if p1_data['SVA_P_lt_50'] > p2_data['SVA_P_lt_50'] else p2_name},
            {"Metric": "Death Phase SVA", "Athlete A": f"{p1_data['SVA_Death']:+.4f}", "Athlete B": f"{p2_data['SVA_Death']:+.4f}", "Advantage": p1_name if p1_data['SVA_Death'] > p2_data['SVA_Death'] else p2_name},
            {"Metric": "Powerplay Phase SVA", "Athlete A": f"{p1_data['SVA_PP']:+.4f}", "Athlete B": f"{p2_data['SVA_PP']:+.4f}", "Advantage": p1_name if p1_data['SVA_PP'] > p2_data['SVA_PP'] else p2_name},
        ])

        st.dataframe(
            comp_df,
            column_config={
                "Metric": st.column_config.TextColumn("Evaluation Dimension", width="medium"),
                "Athlete A": st.column_config.TextColumn(f"{p1_name} (#{p1_data['Rank']})", width="medium"),
                "Athlete B": st.column_config.TextColumn(f"{p2_name} (#{p2_data['Rank']})", width="medium"),
                "Advantage": st.column_config.TextColumn("Executive Edge", width="medium"),
            },
            hide_index=True,
            use_container_width=True
        )

# =============================================================================
# TAB 6: 📊 Publication EDA Gallery
elif selected_page == "📊 Publication EDA Gallery":
    figs = get_eda_figures_catalog()
    categories = list(dict.fromkeys([f['category'] for f in figs]))

    sub_tabs = st.tabs([f"📂 {cat}" for cat in categories])

    for i, cat in enumerate(categories):
        with sub_tabs[i]:
            cat_figs = [f for f in figs if f['category'] == cat]
            for f in cat_figs:
                st.markdown(f"##### {f['title']}")
                st.caption(f['desc'])
                if os.path.exists(f['file']):
                    st.image(f['file'], use_container_width=True)
                else:
                    st.error(f"Image not found at {f['file']}")
                st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# =============================================================================
# TAB 7: 📑 Sensitivity, Audits & Official Downloads
elif selected_page == "📑 Sensitivity, Audits & Downloads":
    st.markdown("##### 🧪 Alpha Stability (α = 1.00 vs 1.25) & Knockout Sensitivity")
    # 4 Executive KPI Metric Cards for Sensitivity
    sk1, sk2, sk3, sk4 = st.columns(4)
    with sk1:
        st.metric(label="Top 4 Core Invariance", value="100%", delta="Identical across α=1.00 & 1.25")
    with sk2:
        st.metric(label="Top 10 Cohort Retention", value="10/10", delta="Zero Exclusions")
    with sk3:
        st.metric(label="Playoff Weighting Test", value="Varun #17 ➔ #5", delta="KKR 2024 Title Run")
    with sk4:
        st.metric(label="Official Decision", value="Unbiased Baseline", delta="Tournament Weights Rejected")

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # 2 Comparison Modules
    scol1, scol2 = st.columns(2)
    with scol1:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background:#38BDF822; color:#38BDF8;">Alpha Stability (α = 1.00 vs 1.25)</span>
            <div class="hero-title">Rigorous Rank Stability</div>
            <div class="hero-desc">
                Super-linear weighting (α = 1.25) was evaluated to exponentially penalize routine deliveries.<br><br>
                • <b>Top 4 Batters & Bowlers 100% Invariant:</b> Sooryavanshi, SKY, Abhishek, David; Rashid, Bumrah, Narine, Hazlewood retain exact top ranks.<br>
                • <b>100% Top 10 Overlap:</b> Exactly the same 10 players qualify with only minor adjacent rank swaps (#5 Klaasen and #6 Pooran swap; #8 Head and #9 Salt swap).
            </div>
        </div>
        """, unsafe_allow_html=True)
    with scol2:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background:#F59E0B22; color:#F59E0B;">19 Knockout Matches Evaluated</span>
            <div class="hero-title">Playoff Leverage Multipliers</div>
            <div class="hero-desc">
                Tested scaling leverage across all 19 IPL playoffs and T20I ICC knockout matches by <b>1.10× to 1.25×</b>.<br><br>
                • <b>Varun Chakravarthy Jump:</b> Leaped from #17 to #5 (displacing baseline #5 Wanindu Hasaranga to #6).<br>
                • <b>Executive Decision:</b> Rejected tournament-stage inflation for the official leaderboard to preserve impartial mathematical rigor and avoid small-sample knockout bias.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    st.markdown("##### Figure 7: Alpha Parameter Sensitivity Bump Chart")
    fig7_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_8_eda', 'figures', 'fig07_alpha_sensitivity_slope.png')
    if os.path.exists(fig7_path):
        st.image(fig7_path, use_container_width=True)

    st.markdown("<hr style='border-color:#28163D; margin: 24px 0;'>", unsafe_allow_html=True)

    # 4 Pipeline Stages in 4 Clean Cards
    st.markdown("##### 🏗️ 4-Stage Selection Architecture")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background:#38BDF822; color:#38BDF8;">Stage 1</span>
            <div class="hero-title">Win Probability & Consequence</div>
            <div class="hero-desc">Pre-delivery logistic regression estimating WP(S<sub>t</sub>). Expected consequence L = Σ p<sub>o</sub> |ΔWP| normalized via empirical ECDF into L<sub>norm</sub> ∈ [0, 100].</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background:#818CF822; color:#818CF8;">Stage 2</span>
            <div class="hero-title">Task Difficulty & Gating</div>
            <div class="hero-desc">Standardized RRR, CRR vs par, and empirical wicket stress curves yielding T(S<sub>t</sub>) ∈ [0, 100]. Master Pressure P = [T × L<sub>norm</sub>]<sup>1/2</sup>.</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background:#F43F5E22; color:#F43F5E;">Stage 3</span>
            <div class="hero-title">Situational Baselines</div>
            <div class="hero-desc">36 state cells (Innings × Format × Phase × Wicket Cluster) with dynamic wicket values λ<sub>eff</sub> = min(λ<sub>wkt</sub>, Runs Required).</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background:#10B98122; color:#10B981;">Stage 4</span>
            <div class="hero-title">Empirical Bayes Shrinkage</div>
            <div class="hero-desc">Kish ESS ESS<sub>j</sub> = (Σw<sub>i</sub>)<sup>2</sup> / Σ(w<sub>i</sub><sup>2</sup>) controlling sample variance; Empirical Bayes shrinkage toward grand mean.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # Official Verification Badges
    st.markdown("##### 🛡️ Official Verification Audits")
    a1, a2 = st.columns(2)
    with a1:
        st.markdown("""
        <div style="background:#10B98115; border:1px solid #10B98144; border-radius:8px; padding:12px;">
            <b style="color:#10B981;">✅ Step 10.3 Final Verification Audit: 100% PASS</b><br>
            <span style="font-size:12px; color:#94A3B8;">Monotonic rank ordering verified across all 297 batters and 292 bowlers. Exact 8-column schema preserved. Zero data leakage.</span>
        </div>
        """, unsafe_allow_html=True)
    with a2:
        st.markdown("""
        <div style="background:#10B98115; border:1px solid #10B98144; border-radius:8px; padding:12px;">
            <b style="color:#10B981;">✅ Step 10.4 Pressure Equation & Formula Audit: 100% PASS</b><br>
            <span style="font-size:12px; color:#94A3B8;">Exponential formula P(S<sub>t</sub>) = [T(S<sub>t</sub>) × L<sub>norm</sub>(S<sub>t</sub>)]<sup>1/2</sup> verified across code, markdown, and 12-page PDF.</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # Download Center
    st.markdown("##### 📥 Official Download Center")
    d1, d2, d3 = st.columns(3)
    pdf_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_10_methodology_report', 'step_10_methodology_report.pdf')
    with d1:
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            st.download_button(
                label="📄 Download Audited Report (12-Page PDF)",
                data=pdf_data,
                file_name="SupeRR_Selector_Methodology_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="audit_pdf_download"
            )

    bat_rank_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_batting_rankings.csv')
    with d2:
        if os.path.exists(bat_rank_path):
            with open(bat_rank_path, 'rb') as f:
                bat_csv = f.read()
            st.download_button(
                label="🏏 Download Batting Top 10 (CSV)",
                data=bat_csv,
                file_name="final_batting_rankings.csv",
                mime="text/csv",
                use_container_width=True,
                key="audit_bat_csv_download"
            )

    bowl_rank_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', 'final_bowling_rankings.csv')
    with d3:
        if os.path.exists(bowl_rank_path):
            with open(bowl_rank_path, 'rb') as f:
                bowl_csv = f.read()
            st.download_button(
                label="🎯 Download Bowling Top 10 (CSV)",
                data=bowl_csv,
                file_name="final_bowling_rankings.csv",
                mime="text/csv",
                use_container_width=True,
                key="audit_bowl_csv_download"
            )
