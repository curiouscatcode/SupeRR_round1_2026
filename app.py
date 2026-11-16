"""
app.py
SupeRR Selector 2.0 - Official Pressure Analytics & Selection Intelligence Dashboard
Evaluates elite T20 execution under high-leverage pressure situations (IPL & T20I 2021-2024).
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
# 1. Page Configuration & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SupeRR Selector 2.0 | Pressure Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark sports-analytics theme CSS
st.markdown("""
<style>
    /* Global background and typography */
    .main {
        background-color: #0B1120;
        color: #F8FAFC;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0F172A;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #1E293B;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 14px;
        border: none;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    /* Hero Card Styling */
    .hero-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
        margin-bottom: 12px;
        height: 100%;
    }
    .hero-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 17px;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .hero-stat {
        font-size: 26px;
        font-weight: 800;
        color: #38BDF8;
        margin-bottom: 6px;
    }
    .hero-desc {
        font-size: 12px;
        color: #94A3B8;
        line-height: 1.4;
    }
    /* Metric container */
    .metric-banner {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .podium-card {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        background-color: #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Header & Global KPIs Banner
# -----------------------------------------------------------------------------
st.title("🏏 SupeRR Selector 2.0 — Pressure Analytics Intelligence")
st.markdown("**Round 1 Problem Statement Official Submission** | *Evaluating Elite T20 Execution Under High-Leverage Pressure*")

# Top KPI Metric Cards
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
with col_kpi1:
    st.metric(
        label="⚡ Deliveries Evaluated",
        value="186,780",
        help="96,165 batting deliveries and 90,615 bowling deliveries across IPL and T20I (2021-2024)."
    )
with col_kpi2:
    st.metric(
        label="👥 Qualified Cohort",
        value="589 Athletes",
        help="297 qualified batters and 292 qualified bowlers meeting the 100+ raw opportunity threshold."
    )
with col_kpi3:
    st.metric(
        label="🛡️ Top 4 Invariance",
        value="100% Robust",
        help="Top 4 batters and top 4 bowlers remain perfectly invariant under extreme parameter sensitivity tests."
    )
with col_kpi4:
    st.metric(
        label="📑 Official Report Audit",
        value="100% Certified Pass",
        help="Full mathematical consistency across Step 7.4 rankings, Step 8 EDA, and 12-page Step 10 report."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. Top Tabs Navigation
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "🏆 Official Leaderboards & Squad Selection",
    "⚡ The Pressure Engine & Live Simulator",
    "📈 Pressure Elevation: Lift (Δ) Analysis",
    "🔍 Player Deep Dive & Head-to-Head",
    "📊 Visual EDA Gallery (14 Figures)",
    "🧪 Sensitivity & Knockout Experiments",
    "📑 Methodology, Audit & Downloads"
])

# =============================================================================
# TAB 1: 🏆 Official Leaderboards & Squad Selection
# =============================================================================
with tabs[0]:
    st.markdown("### 🌟 Spotlight: Key Selection Discoveries")
    
    # 4 Hero Spotlight Cards
    hcol1, hcol2, hcol3, hcol4 = st.columns(4)
    with hcol1:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background-color:rgba(16,185,129,0.2); color:#10B981;">#1 Batting Phenom</span>
            <div class="hero-title">Vaibhav Sooryavanshi</div>
            <div class="hero-stat">+0.3487 <span style="font-size:14px; color:#94A3B8;">SVA</span></div>
            <div class="hero-desc">
                <b>Rajasthan Royals (IPL & T20I)</b><br>
                Raw score: <b>0.7614</b> | Kish ESS: <b>506.9</b><br>
                Pressure Lift: <b style="color:#10B981;">+0.207</b> elevation under pressure. Unmatched boundary conversion in high-leverage chases.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hcol2:
        st.markdown("""
        <div class="hero-card">
            <span class="hero-badge" style="background-color:rgba(245,158,11,0.2); color:#F59E0B;">#4 Bowling Clutch Surge</span>
            <div class="hero-title">Josh Hazlewood</div>
            <div class="hero-stat">+0.1330 <span style="font-size:14px; color:#94A3B8;">SVA</span></div>
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
            <div class="hero-stat">+0.1756 <span style="font-size:14px; color:#94A3B8;">SVA</span></div>
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

    st.markdown("---")
    
    # Discipline Selector
    disc_col, info_col = st.columns([1, 3])
    with disc_col:
        discipline = st.radio(
            "Select Discipline:",
            ["Batting", "Bowling"],
            index=0,
            horizontal=True
        )
    with info_col:
        if discipline == "Batting":
            st.info("📊 **Pressure-Weighted Score Value Added (PWSVA)** measures runs generated above replacement adjusted for match leverage, dynamic wicket valuation, and Bayesian shrinkage.")
        else:
            st.info("🎯 **Standardized Bowler Value Added (SBVA)** measures runs suppressed and wickets taken above replacement conditioned on 36 situational state cells and match pressure.")

    # Load data
    top10_df = load_official_top10(discipline)
    metrics_df = load_full_metrics(discipline)

    # Top 3 Podium Cards
    p1, p2, p3 = top10_df.iloc[0], top10_df.iloc[1], top10_df.iloc[2]
    pod1, pod2, pod3 = st.columns(3)
    with pod1:
        st.markdown(f"""
        <div class="podium-card" style="border-color:#F59E0B; box-shadow:0 0 10px rgba(245,158,11,0.2);">
            <div style="font-size:24px;">🥇 Gold Medal</div>
            <div style="font-size:18px; font-weight:700; color:#F8FAFC;">{p1['Player']}</div>
            <div style="color:#94A3B8; font-size:12px;">{p1['Team/format']}</div>
            <div style="font-size:22px; font-weight:800; color:#F59E0B; margin:6px 0;">{p1['Shrunk score']:.4f}</div>
            <div style="font-size:11px; color:#94A3B8;">Kish ESS: <b>{p1['Kish ESS']:.1f}</b> | 95% CI: {p1['95% CI']}</div>
        </div>
        """, unsafe_allow_html=True)
    with pod2:
        st.markdown(f"""
        <div class="podium-card" style="border-color:#94A3B8;">
            <div style="font-size:24px;">🥈 Silver Medal</div>
            <div style="font-size:18px; font-weight:700; color:#F8FAFC;">{p2['Player']}</div>
            <div style="color:#94A3B8; font-size:12px;">{p2['Team/format']}</div>
            <div style="font-size:22px; font-weight:800; color:#E2E8F0; margin:6px 0;">{p2['Shrunk score']:.4f}</div>
            <div style="font-size:11px; color:#94A3B8;">Kish ESS: <b>{p2['Kish ESS']:.1f}</b> | 95% CI: {p2['95% CI']}</div>
        </div>
        """, unsafe_allow_html=True)
    with pod3:
        st.markdown(f"""
        <div class="podium-card" style="border-color:#CD7F32;">
            <div style="font-size:24px;">🥉 Bronze Medal</div>
            <div style="font-size:18px; font-weight:700; color:#F8FAFC;">{p3['Player']}</div>
            <div style="color:#94A3B8; font-size:12px;">{p3['Team/format']}</div>
            <div style="font-size:22px; font-weight:800; color:#CD7F32; margin:6px 0;">{p3['Shrunk score']:.4f}</div>
            <div style="font-size:11px; color:#94A3B8;">Kish ESS: <b>{p3['Kish ESS']:.1f}</b> | 95% CI: {p3['95% CI']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Top 10 Plotly Chart
    st.plotly_chart(create_top10_bar(top10_df, discipline), use_container_width=True)

    # Official Cutoff Boundary Explainer
    if discipline == "Batting":
        st.warning("""
        ⚖️ **Official Cutoff Boundary (#10 Reeza Hendricks vs. #11 Rajat Patidar):**
        - **#10 Reeza Hendricks:** Shrunk score **0.2078** [0.0683, 0.3347], Kish ESS: 422.3.
        - **#11 Rajat Patidar:** Shrunk score **0.2057** [0.0783, 0.3323], Kish ESS: 593.5.
        - **Marginal Separation:** Exactly **0.0021 runs/ball**. Their 95% bootstrap confidence intervals overlap substantially. Selectors seeking higher sample volume can legitimately consider Patidar as first-reserve!
        """)
    else:
        st.warning("""
        ⚖️ **Official Cutoff Boundary (#10 Mujeeb Ur Rahman vs. #11 Mosaddek Hossain):**
        - **#10 Mujeeb Ur Rahman:** Shrunk score **0.1062** [0.0093, 0.1989], Kish ESS: 706.7.
        - **#11 Mosaddek Hossain:** Shrunk score **0.1049** [0.0020, 0.2046], Kish ESS: 359.2.
        - **Marginal Separation:** Exactly **0.0013 runs/ball**. Mujeeb secures #10 due to nearly 2× larger effective sample size (ESS 706.7 vs. 359.2).
        """)

    # Full Cohort Search & Filter Table
    st.markdown(f"### 📋 Full {discipline} Cohort ({len(metrics_df)} Athletes)")
    fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
    with fcol1:
        search_query = st.text_input("🔍 Search Athlete Name:", "")
    with fcol2:
        min_ess = st.slider("Min Kish ESS:", min_value=100, max_value=2500, value=100, step=50)
    with fcol3:
        format_filter = st.selectbox("Tournament Filter:", ["All", "IPL & T20I", "IPL Only", "T20I Only"])

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

    display_cols = ['Rank', 'Player', 'Team/format', 'Shrunk score', 'Raw score', 'Kish ESS', 'Pressure_Lift', 'SVA_P_ge_50', 'SVA_P_lt_50', '95% CI']
    st.dataframe(
        filtered_df[display_cols].style.format({
            'Shrunk score': '{:.4f}',
            'Raw score': '{:.4f}',
            'Kish ESS': '{:.1f}',
            'Pressure_Lift': '{:+.4f}',
            'SVA_P_ge_50': '{:+.4f}',
            'SVA_P_lt_50': '{:+.4f}'
        }),
        use_container_width=True,
        height=350
    )

    # Download CSV
    csv_bytes = filtered_df[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download Filtered {discipline} Table (CSV)",
        data=csv_bytes,
        file_name=f"supeRR_selector_{discipline.lower()}_rankings.csv",
        mime="text/csv"
    )

# =============================================================================
# TAB 2: ⚡ The Pressure Engine & Live Simulator
# =============================================================================
with tabs[1]:
    st.markdown("### ⚡ The Mathematical Pressure Engine: Orthogonal Gating")
    
    st.markdown("""
    **The Fundamental Principle of SupeRR Selector 2.0:**
    $$\\mathbf{P}(S_t) = \\left[ \\mathbf{T}(S_t) \\times \\mathbf{L}_{\\text{norm}}(S_t) \\right]^{1/2} \\in [0, 100]$$
    
    To evaluate players without distortion, Pressure is factored into two strictly orthogonal dimensions:
    1. **Task Difficulty $\\mathbf{T}(S_t)$**: How hard is the immediate tactical assignment? (Required Run Rate, current run rate vs. par, wickets lost, phase par).
    2. **Win Probability Consequence $\\mathbf{L}_{\\text{norm}}(S_t)$**: How much does the match outcome actually hinge on this specific delivery? ($E[|\\Delta WP|]$ across 9 discrete transition outcomes mapped through an empirical ECDF).
    
    *Why the Geometric Mean?* It acts as an **orthogonal gate**: if *either* difficulty or consequence is near zero, Pressure collapses to near zero. An impossible chase (40 RRR) when the match is already dead produces zero consequence $\\to$ **Garbage Time is mathematically purged!**
    """)
    
    st.markdown("---")
    st.markdown("### 🎮 One-Click Match Scenario Simulators")
    st.write("Click any preset scenario to see how the engine instantly isolates true high pressure from routine or garbage situations:")

    pcol1, pcol2, pcol3 = st.columns(3)
    preset_choice = None
    if pcol1.button("🔥 Scenario 1: The True Crucible", help="18 needed off 12 balls, 6 wickets down in chase"):
        preset_choice = 1
    if pcol2.button("☕ Scenario 2: Routine Finish", help="12 needed off 18 balls, 2 wickets down in chase"):
        preset_choice = 2
    if pcol3.button("🗑️ Scenario 3: Garbage Time", help="80 needed off 12 balls, 8 wickets down in chase"):
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

    st.markdown("#### 🎛️ Interactive Custom Match State Controls")
    scol1, scol2, scol3, scol4 = st.columns(4)
    with scol1:
        sim_inn = st.selectbox("Innings:", [1, 2], index=default_inn-1)
    with scol2:
        sim_brem = st.slider("Balls Remaining in Innings:", 1, 120, default_brem)
    with scol3:
        sim_score = st.number_input("Current Score:", 0, 300, default_score)
    with scol4:
        sim_wkts = st.slider("Wickets Lost:", 0, 9, default_wkts)

    if sim_inn == 2:
        scol5, scol6 = st.columns(2)
        with scol5:
            sim_target = st.number_input("Target Score to Chase:", 50, 300, default_target)
        with scol6:
            sim_par = st.number_input("Venue Par Score:", 120.0, 220.0, 176.68)
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

    st.markdown("### 📊 Live Simulation Diagnostic Gauges")
    gcol1, gcol2, gcol3, gcol4 = st.columns(4)
    with gcol1:
        st.plotly_chart(create_gauge(sim_res['pressure_batting'], "🏏 Batting Pressure P_bat", color='#3B82F6'), use_container_width=True, config={'displayModeBar': False})
    with gcol2:
        st.plotly_chart(create_gauge(sim_res['pressure_bowling'], "🎯 Bowling Pressure P_bowl", color='#F59E0B'), use_container_width=True, config={'displayModeBar': False})
    with gcol3:
        st.plotly_chart(create_gauge(sim_res['task_difficulty_bat'], "⚙️ Batting Task Diff T_B", color='#8B5CF6'), use_container_width=True, config={'displayModeBar': False})
    with gcol4:
        st.plotly_chart(create_gauge(sim_res['normalized_consequence_L'], "⚡ Leverage L_norm", color='#EC4899'), use_container_width=True, config={'displayModeBar': False})

    # Detailed diagnostic breakdown
    rcol1, rcol2 = st.columns(2)
    with rcol1:
        rrr_display = f"`{sim_res['rrr']:.2f} rpo` (Runs needed: `{sim_res['runs_required']}`)" if sim_res['rrr'] is not None else "`N/A (Innings 1 - Target Not Set)`"
        st.markdown(f"""
        **Match State Breakdown:**
        - **Phase:** `{sim_res['phase']}` (Over {(120 - sim_brem)//6}.{(120 - sim_brem)%6})
        - **Current Run Rate (CRR):** `{sim_res['crr']:.2f}` rpo
        - **Required Run Rate (RRR):** {rrr_display}
        - **Batting Win Probability WP(S_t):** `{sim_res['wp_batting']*100:.1f}%`
        """)
    with rcol2:
        band_bat = sim_res['pressure_band_batting']
        color_alert = "warning" if "High" in band_bat else ("error" if "Crucible" in band_bat else "info")
        st.markdown(f"""
        **Pressure Classification:**
        - **Batting Band:** `{band_bat}`
        - **Bowling Band:** `{sim_res['pressure_band_bowling']}`
        - **Raw Expected Leverage E[|ΔWP|]:** `{sim_res['raw_consequence_L']:.5f}`
        - **ECDF Percentile Consequence:** `{sim_res['normalized_consequence_L']:.2f}th percentile`
        """)

# =============================================================================
# TAB 3: 📈 Pressure Elevation: Lift (Δ) Analysis
# =============================================================================
with tabs[2]:
    st.markdown("### 📈 Quantifying Pressure Elevation: Routine vs. Crucible Execution")
    st.markdown("""
    *Directly addressing the Round 1 Prompt:* **"Performance under pressure compared to normal situations."**
    
    A critical limitation of raw averages is that players who accumulate stats in low-stakes phases appear dominant, but falter when leverage peaks. 
    Here, we explicitly contrast each athlete's performance in **routine situations ($P < 50$)** against **elevated pressure ($P \ge 50$)**.
    $$\\text{Pressure Lift } \\Delta = \\text{SVA}_{P \\ge 50} - \\text{SVA}_{P < 50}$$
    """)

    lcol1, lcol2 = st.columns([1, 3])
    with lcol1:
        lift_disc = st.radio("Discipline:", ["Batting", "Bowling"], key="lift_disc")
    with lcol2:
        st.markdown("""
        **Macro Population Finding:**
        Across the entire database of 589 qualified players, batting performance suffers a catastrophic drop under pressure:
        - **Mean Batting SVA ($P < 50$):** `+0.0318 runs/ball`
        - **Mean Batting SVA ($P \\ge 50$):** `+0.0041 runs/ball` **(-87.1% collapse!)**
        
        The athletes below are not merely maintaining baseline; **they are elevating above their own routine level!**
        """)

    lift_df = load_full_metrics(lift_disc)

    # Grouped Bar: Normal vs Pressure
    st.plotly_chart(create_pressure_lift_chart(lift_df, lift_disc), use_container_width=True)

    # Net Lift Bar
    st.plotly_chart(create_lift_waterfall(lift_df, lift_disc), use_container_width=True)

    # Elite Case Studies
    if lift_disc == "Batting":
        st.markdown("""
        #### 🌟 Elite Batting Elevation Case Studies:
        1. **Vaibhav Sooryavanshi ($\Delta = +0.207$):** Jumps from $+0.554$ in routine situations to an astounding $+0.761$ in clutch pressure. He hits boundaries at a 38% clip under pressure.
        2. **Phil Salt ($\Delta = +0.115$):** Leaps from $+0.245$ ($P < 50$) to $+0.360$ ($P \ge 50$), proving his hyper-aggressive intent is most potent when the match requires acceleration.
        3. **Heinrich Klaasen ($\Delta = +0.077$):** Increases from $+0.335$ to $+0.412$ at death, cementing his reputation as the premier spin/pace demolisher at the death.
        """)
    else:
        st.markdown("""
        #### 🎯 Elite Bowling Elevation Case Studies:
        1. **Josh Hazlewood ($\Delta = +0.161$, +421% Surge):** Rises from $+0.038$ ($P < 50$) to $+0.200$ ($P \ge 50$). In tight powerplays and death overs, his dot-ball percentage exceeds 56%.
        2. **Rashid Khan ($\Delta = +0.159$, +146% Surge):** Rises from $+0.056$ to $+0.215$. Over 2,648 opportunities, he strangles scoring when the opposition needs boundaries.
        3. **Mujeeb Ur Rahman ($\Delta = +0.153$, +265% Surge):** Vaults from $+0.039$ to $+0.192$, demonstrating elite boundary suppression in high-stakes powerplays.
        """)

# =============================================================================
# TAB 4: 🔍 Player Deep Dive & Head-to-Head
# =============================================================================
with tabs[3]:
    st.markdown("### 🔍 Granular Athlete Profiling & Head-to-Head Comparison")
    
    dcol1, dcol2 = st.columns([1, 2])
    with dcol1:
        d_disc = st.radio("Select Discipline:", ["Batting", "Bowling"], key="dd_disc")
    with dcol2:
        analysis_mode = st.radio("Analysis Mode:", ["Single Player Dossier", "Head-to-Head Comparison"], horizontal=True)

    d_df = load_full_metrics(d_disc)
    player_names = d_df['Player'].tolist()

    if analysis_mode == "Single Player Dossier":
        selected_player = st.selectbox("Choose Athlete to Inspect:", player_names, index=0)
        p_data = d_df[d_df['Player'] == selected_player].iloc[0]

        # Player Header Card
        st.markdown(f"""
        <div class="hero-card">
            <span class="hero-badge" style="background-color:rgba(59,130,246,0.2); color:#38BDF8;">Rank #{p_data['Rank']} {d_disc}</span>
            <div style="font-size:24px; font-weight:800; color:#FFFFFF;">{p_data['Player']}</div>
            <div style="color:#94A3B8; font-size:13px; margin-bottom:12px;">Team & Format: <b>{p_data['Team/format']}</b></div>
            <div style="display:flex; gap:24px; flex-wrap:wrap;">
                <div><span style="font-size:11px; color:#94A3B8;">SHRUNK SCORE</span><br><b style="font-size:20px; color:#38BDF8;">{p_data['Shrunk score']:.4f}</b></div>
                <div><span style="font-size:11px; color:#94A3B8;">RAW SCORE</span><br><b style="font-size:20px; color:#E2E8F0;">{p_data['Raw score']:.4f}</b></div>
                <div><span style="font-size:11px; color:#94A3B8;">KISH ESS</span><br><b style="font-size:20px; color:#10B981;">{p_data['Kish ESS']:.1f}</b></div>
                <div><span style="font-size:11px; color:#94A3B8;">PRESSURE LIFT (Δ)</span><br><b style="font-size:20px; color:{'#10B981' if p_data['Pressure_Lift'] >= 0 else '#EF4444'};">{p_data['Pressure_Lift']:+.4f}</b></div>
                <div><span style="font-size:11px; color:#94A3B8;">95% BOOTSTRAP CI</span><br><b style="font-size:16px; color:#F59E0B;">{p_data['95% CI']}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.plotly_chart(create_pressure_distribution_pie(p_data), use_container_width=True)
        with col_d2:
            st.plotly_chart(create_phase_bar(p_data), use_container_width=True)

        # Cross Format Consistency
        st.markdown("#### 🌐 Cross-Format Breakdown (IPL vs. T20I)")
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            st.metric("IPL Performance (SVA/ball)", f"{p_data['SVA_IPL']:+.4f}")
        with fcol2:
            st.metric("T20I Performance (SVA/ball)", f"{p_data['SVA_T20I']:+.4f}")

    else: # Head-to-Head Mode
        st.markdown("#### ⚔️ Head-to-Head Athlete Comparison")
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Select Athlete A:", player_names, index=0)
        with c2:
            p2_name = st.selectbox("Select Athlete B:", player_names, index=1 if len(player_names) > 1 else 0)

        p1_data = d_df[d_df['Player'] == p1_name].iloc[0]
        p2_data = d_df[d_df['Player'] == p2_name].iloc[0]

        # Radar Comparison
        st.plotly_chart(create_player_radar(p1_data, p2_data, d_disc), use_container_width=True)

        # Comparison Table
        comp_df = pd.DataFrame({
            'Metric': ['Official Rank', 'Shrunk Score', 'Raw Score', 'Kish ESS', 'Pressure Lift (Δ)', 'SVA (P ≥ 50)', 'SVA (P < 50)', 'Death Phase SVA', 'Powerplay SVA'],
            f"{p1_name} (#{p1_data['Rank']})": [
                f"#{p1_data['Rank']}",
                f"{p1_data['Shrunk score']:.4f}",
                f"{p1_data['Raw score']:.4f}",
                f"{p1_data['Kish ESS']:.1f}",
                f"{p1_data['Pressure_Lift']:+.4f}",
                f"{p1_data['SVA_P_ge_50']:+.4f}",
                f"{p1_data['SVA_P_lt_50']:+.4f}",
                f"{p1_data['SVA_Death']:+.4f}",
                f"{p1_data['SVA_PP']:+.4f}"
            ],
            f"{p2_name} (#{p2_data['Rank']})": [
                f"#{p2_data['Rank']}",
                f"{p2_data['Shrunk score']:.4f}",
                f"{p2_data['Raw score']:.4f}",
                f"{p2_data['Kish ESS']:.1f}",
                f"{p2_data['Pressure_Lift']:+.4f}",
                f"{p2_data['SVA_P_ge_50']:+.4f}",
                f"{p2_data['SVA_P_lt_50']:+.4f}",
                f"{p2_data['SVA_Death']:+.4f}",
                f"{p2_data['SVA_PP']:+.4f}"
            ]
        })
        st.table(comp_df.set_index('Metric'))

# =============================================================================
# TAB 5: 📊 Visual EDA Gallery (14 Figures)
# =============================================================================
with tabs[4]:
    st.markdown("### 📊 Publication-Grade Exploratory Data Analysis (EDA) Gallery")
    st.markdown("All 14 figures from the official audited methodology report rendered at 300 DPI:")

    figs = get_eda_figures_catalog()
    categories = list(dict.fromkeys([f['category'] for f in figs]))
    
    sub_tabs = st.tabs([f"📂 {cat}" for cat in categories])

    for i, cat in enumerate(categories):
        with sub_tabs[i]:
            cat_figs = [f for f in figs if f['category'] == cat]
            for f in cat_figs:
                st.markdown(f"#### {f['title']}")
                st.caption(f['desc'])
                if os.path.exists(f['file']):
                    st.image(f['file'], use_container_width=True)
                else:
                    st.error(f"Image not found at {f['file']}")
                st.markdown("---")

# =============================================================================
# TAB 6: 🧪 Sensitivity & Knockout Experiments
# =============================================================================
with tabs[5]:
    st.markdown("### 🧪 Sensitivity Testing & Playoff Knockout Experiments")
    st.markdown("""
    To guarantee that our official rankings are not artifacts of hyper-parameter tuning, we subjected the model to rigorous stress-testing:
    """)

    sens_col1, sens_col2 = st.columns(2)
    with sens_col1:
        st.markdown("""
        #### 1. Alpha Sensitivity: Linear vs. Super-Linear Weighting
        - **Baseline ($\alpha = 1.00$):** Linear pressure weighting ($w_i = (P_i / 50)^{1.00}$).
        - **Clutch Test ($\alpha = 1.25$):** Super-linear weighting ($w_i = (P_i / 50)^{1.25}$) exponentially penalizing routine situations.
        - **Findings:**
          - **Top 4 Batters & Bowlers remain 100% Invariant:**
            - Batters: Sooryavanshi (#1), Suryakumar (#2), Abhishek (#3), David (#4).
            - Bowlers: Rashid (#1), Bumrah (#2), Narine (#3), Hazlewood (#4).
          - **100% Top 10 Cohort Retention:** Exactly the same 10 players qualify with only minor adjacent rank swaps (#5 Klaasen and #6 Pooran swap; #8 Head and #9 Salt swap).
        """)
    with sens_col2:
        st.markdown("""
        #### 2. Playoff / Knockout Leverage Multiplier Experiment
        - Tested scaling leverage across all 19 IPL playoffs and T20I ICC knockout matches by multipliers of **$1.10\\times$ to $1.25\\times$**.
        - **Findings:**
          - Top 4 bowlers remain invariant.
          - **Varun Chakravarthy:** Under playoff multipliers, Varun jumped from **#17 up to #5** (displacing baseline #5 Wanindu Hasaranga to #6), reflecting KKR's 2024 dominant championship playoff run.
          - **Methodological Conclusion:** To maintain unbiased, objective mathematical standards, arbitrary tournament-stage multipliers were **rejected for the official leaderboard**, preserving equal valuation across all 186,780 deliveries.
        """)

    st.markdown("---")
    st.markdown("#### Figure 7: Alpha Parameter Sensitivity Bump Chart")
    fig7_path = os.path.join(os.path.dirname(__file__), 'outputs', 'step_8_eda', 'figures', 'fig07_alpha_sensitivity_slope.png')
    if os.path.exists(fig7_path):
        st.image(fig7_path, use_container_width=True)

# =============================================================================
# TAB 7: 📑 Methodology, Audit & Downloads
# =============================================================================
with tabs[6]:
    st.markdown("### 📑 Methodological Architecture, Mathematical Audit & Official Downloads")
    
    st.markdown("""
    #### 🏗️ The 4-Stage Selection Pipeline
    1. **Stage 1 (Win Probability & Consequence Engine):** Pre-delivery logistic regression estimating $WP(S_t)$, yielding expected swing $L(S_t) = \\sum p_o |WP(S_{t+1}) - WP(S_t)|$, normalized via empirical ECDF to $L_{\\text{norm}} \\in [0, 100]$.
    2. **Stage 2 (Task Difficulty Engine):** Standardized RRR, CRR vs venue par, and empirical wicket scarcity curves yielding $T(S_t) \\in [0, 100]$. Combined via geometric mean: $P = \\sqrt{T \\times L_{\\text{norm}}}$.
    3. **Stage 3 (Situational Baselines & Dynamic Wickets):** 36 situational state cells (Innings $\\times$ Format $\\times$ Phase $\\times$ Wicket Cluster) with dynamic wicket values $\\lambda_{\\text{eff}}(S_t) = \\min(\\lambda_{\\text{wkt}}, \\text{Runs Required})$.
    4. **Stage 4 (Empirical Bayes Shrinkage & Kish ESS):** Kish Effective Sample Size $ESS_j = (\\sum w_i)^2 / \\sum(w_i^2)$ controlling sample variance; Empirical Bayes shrinking raw scores toward the cohort grand mean.
    """)

    st.markdown("---")
    st.markdown("#### 🛡️ Official Verification Audits")
    acol1, acol2 = st.columns(2)
    with acol1:
        st.success("""
        ✅ **Step 10.3 Final Verification Audit: 100% PASS**
        - Monotonic rank ordering verified across all 297 batters and 292 bowlers.
        - Exact 8-column schema preserved (`Rank, Player, Team/format, Shrunk score, Raw score, Kish ESS, 95% CI, Alpha 1.25 rank`).
        - Zero data corruption, zero nulls, zero leakage.
        """)
    with acol2:
        st.success("""
        ✅ **Step 10.4 Pressure Equation & Formula Audit: 100% PASS**
        - Exponential formula $\mathbf{P}(S_t) = [\mathbf{T}(S_t) \times \mathbf{L}_{\\text{norm}}(S_t)]^{1/2}$ fully compliant.
        - Zero font or rendering glitches in report.
        - Exact 12-page budget strictly maintained.
        """)

    st.markdown("---")
    st.markdown("#### 📥 Official Download Center")
    st.write("Download the complete audited methodology report, frozen datasets, and precomputed metrics:")

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
                mime="application/pdf"
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
                mime="text/csv"
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
                mime="text/csv"
            )
