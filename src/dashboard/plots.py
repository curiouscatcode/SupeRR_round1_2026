"""
src/dashboard/plots.py
Plotly visualization helpers for SupeRR Selector 2.0 Streamlit dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

COLOR_PRIMARY = "#3B82F6"   # Electric Blue
COLOR_ACCENT = "#EC4899"    # Magenta / Crimson
COLOR_SUCCESS = "#10B981"   # Emerald Green
COLOR_WARNING = "#F59E0B"   # Amber
COLOR_BG_DARK = "#1E293B"   # Slate 800
COLOR_CARD = "#0F172A"      # Slate 900
COLOR_TEXT = "#F8FAFC"      # Off white

def create_top10_bar(df: pd.DataFrame, discipline: str):
    """Horizontal bar chart for Top 10 with 95% CIs and Kish ESS labels."""
    df_sorted = df.head(10).iloc[::-1].copy()
    
    # Parse CIs
    ci_lowers, ci_uppers = [], []
    for ci_str in df_sorted['95% CI']:
        try:
            parts = ci_str.strip('[]').split(',')
            ci_lowers.append(float(parts[0]))
            ci_uppers.append(float(parts[1]))
        except:
            ci_lowers.append(0.0)
            ci_uppers.append(0.0)
            
    df_sorted['ci_lower'] = ci_lowers
    df_sorted['ci_upper'] = ci_uppers
    df_sorted['err_minus'] = df_sorted['Shrunk score'] - df_sorted['ci_lower']
    df_sorted['err_plus'] = df_sorted['ci_upper'] - df_sorted['Shrunk score']

    color = '#2563EB' if discipline.lower() == 'batting' else '#D97706'

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted['Player'],
        x=df_sorted['Shrunk score'],
        orientation='h',
        marker=dict(
            color=df_sorted['Shrunk score'],
            colorscale='Blues' if discipline.lower() == 'batting' else 'YlOrBr',
            line=dict(color='white', width=1)
        ),
        error_x=dict(
            type='data',
            symmetric=False,
            array=df_sorted['err_plus'],
            arrayminus=df_sorted['err_minus'],
            color='#E2E8F0',
            thickness=2,
            width=5
        ),
        text=[f"#{r['Rank']}  {r['Shrunk score']:.4f} (ESS: {r['Kish ESS']:.0f})" for _, r in df_sorted.iterrows()],
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(color='white', size=12, family='sans-serif'),
        hovertemplate="<b>%{y}</b><br>Shrunk Score: %{x:.4f}<br>95% CI: [%{customdata[0]:.4f}, %{customdata[1]:.4f}]<br>Kish ESS: %{customdata[2]:.1f}<extra></extra>",
        customdata=df_sorted[['ci_lower', 'ci_upper', 'Kish ESS']]
    ))

    fig.update_layout(
        title=f"<b>Official Top 10 {discipline.capitalize()} Pressure Leaderboard</b><br><span style='font-size:12px; color:#94A3B8'>Shrunk Score (PWSVA / SBVA) with 95% Bootstrap CIs & Kish Effective Sample Size</span>",
        xaxis_title="Empirical Bayes Shrunk Score (Runs / Out Above Replacement)",
        yaxis_title="",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.6)',
        margin=dict(l=20, r=30, t=60, b=40),
        height=450,
        xaxis=dict(showgrid=True, gridcolor='#334155'),
        yaxis=dict(tickfont=dict(size=13, color='#F8FAFC', family='sans-serif'))
    )
    return fig

def create_pressure_lift_chart(df: pd.DataFrame, discipline: str):
    """Grouped bar chart comparing SVA under P >= 50 vs P < 50 for Top 10."""
    top10 = df.head(10).copy()

    fig = go.Figure()
    
    # Normal situation bar (P < 50)
    fig.add_trace(go.Bar(
        name='Normal / Routine (P < 50)',
        x=top10['Player'],
        y=top10['SVA_P_lt_50'],
        marker_color='#64748B',
        text=[f"{v:+.3f}" for v in top10['SVA_P_lt_50']],
        textposition='auto',
        textfont=dict(size=11)
    ))

    # Pressure situation bar (P >= 50)
    bar_color = '#38BDF8' if discipline.lower() == 'batting' else '#F59E0B'
    fig.add_trace(go.Bar(
        name='High Pressure (P ≥ 50)',
        x=top10['Player'],
        y=top10['SVA_P_ge_50'],
        marker_color=bar_color,
        text=[f"{v:+.3f}" for v in top10['SVA_P_ge_50']],
        textposition='auto',
        textfont=dict(size=11, color='white')
    ))

    fig.update_layout(
        title=f"<b>Individual Elevation Under Pressure: Normal (P < 50) vs. High Pressure (P ≥ 50)</b><br><span style='font-size:12px; color:#94A3B8'>Top 10 {discipline.capitalize()}: Quantifying Individual Performance Relative to Normal Baseline</span>",
        barmode='group',
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.6)',
        margin=dict(l=20, r=20, t=60, b=40),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickangle=-25, tickfont=dict(size=11)),
        yaxis=dict(title="Score Value Added (SVA) per Opportunity", showgrid=True, gridcolor='#334155')
    )
    return fig

def create_lift_waterfall(df: pd.DataFrame, discipline: str):
    """Bar chart ranking players purely by Pressure Lift Delta."""
    top10 = df.head(10).sort_values('Pressure_Lift', ascending=True).copy()

    colors = ['#10B981' if x >= 0 else '#EF4444' for x in top10['Pressure_Lift']]

    fig = go.Figure(go.Bar(
        x=top10['Pressure_Lift'],
        y=top10['Player'],
        orientation='h',
        marker_color=colors,
        text=[f"{x:+.4f}" for x in top10['Pressure_Lift']],
        textposition='outside',
        textfont=dict(color='white', size=11)
    ))

    fig.update_layout(
        title=f"<b>Net Pressure Lift (Δ = SVA_{{P ≥ 50}} - SVA_{{P < 50}})</b><br><span style='font-size:12px; color:#94A3B8'>Elite {discipline.capitalize()} Elevation above Own Routine Baseline</span>",
        xaxis_title="Pressure Lift Δ (Positive = Elevates under Pressure)",
        yaxis_title="",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.6)',
        margin=dict(l=20, r=40, t=60, b=40),
        height=380,
        xaxis=dict(showgrid=True, gridcolor='#334155'),
        yaxis=dict(tickfont=dict(size=12))
    )
    return fig

def create_pressure_distribution_pie(player_row: pd.Series):
    """Donut chart showing player's delivery exposure across 4 pressure bands."""
    labels = ['Low (P < 30)', 'Moderate (30 ≤ P < 50)', 'High (50 ≤ P < 75)', 'Crucible (P ≥ 75)']
    values = [player_row['N_Low'], player_row['N_Mid'], player_row['N_High'], player_row['N_Climax']]
    colors = ['#64748B', '#0284C7', '#F59E0B', '#EF4444']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors),
        textinfo='label+percent',
        insidetextorientation='radial',
        hoverinfo='label+value+percent'
    )])

    fig.update_layout(
        title=f"<b>Pressure Exposure Profile</b><br><span style='font-size:11px; color:#94A3B8'>{player_row['Player']} (Total: {sum(values)} balls)</span>",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=20),
        height=300,
        showlegend=False
    )
    return fig

def create_phase_bar(player_row: pd.Series):
    """Bar chart for Powerplay, Middle, and Death SVA performance."""
    phases = ['Powerplay (Overs 1-6)', 'Middle (Overs 7-15)', 'Death (Overs 16-20)']
    sva_vals = [player_row['SVA_PP'], player_row['SVA_Middle'], player_row['SVA_Death']]
    colors = ['#38BDF8', '#818CF8', '#F43F5E']

    fig = go.Figure(go.Bar(
        x=phases,
        y=sva_vals,
        marker_color=colors,
        text=[f"{v:+.3f}" for v in sva_vals],
        textposition='outside',
        textfont=dict(color='white', size=12)
    ))

    fig.update_layout(
        title=f"<b>Tactical Phase SVA Breakdown</b><br><span style='font-size:11px; color:#94A3B8'>{player_row['Player']}</span>",
        xaxis_title="",
        yaxis_title="SVA / Ball",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.6)',
        margin=dict(l=20, r=20, t=50, b=30),
        height=300,
        yaxis=dict(showgrid=True, gridcolor='#334155')
    )
    return fig

def create_player_radar(p1: pd.Series, p2: pd.Series, discipline: str):
    """Radar chart comparing two players across standardized dimensions."""
    categories = [
        'Shrunk Score',
        'Pressure Lift (Δ)',
        'Death Phase SVA',
        'PP Phase SVA',
        'Middle Phase SVA',
        'Sample Robustness (ESS)'
    ]

    # Standardize values for 0-100 radar comparison
    def get_radar_vector(p):
        v1 = max(0, min(100, (p['Shrunk score'] / 0.40) * 100))
        v2 = max(0, min(100, (p['Pressure_Lift'] + 0.10) / 0.35 * 100))
        v3 = max(0, min(100, (p['SVA_Death'] + 0.20) / 0.80 * 100))
        v4 = max(0, min(100, (p['SVA_PP'] + 0.20) / 0.80 * 100))
        v5 = max(0, min(100, (p['SVA_Middle'] + 0.20) / 0.80 * 100))
        v6 = max(0, min(100, (p['Kish ESS'] / 2500) * 100))
        return [v1, v2, v3, v4, v5, v6]

    v1 = get_radar_vector(p1)
    v2 = get_radar_vector(p2)
    
    # Close polygon
    categories_closed = categories + [categories[0]]
    v1_closed = v1 + [v1[0]]
    v2_closed = v2 + [v2[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=v1_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.35)',
        line=dict(color='#3B82F6', width=2),
        name=f"{p1['Player']} (#{p1['Rank']})"
    ))

    fig.add_trace(go.Scatterpolar(
        r=v2_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(236, 72, 153, 0.35)',
        line=dict(color='#EC4899', width=2),
        name=f"{p2['Player']} (#{p2['Rank']})"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='#475569', gridcolor='#334155'),
            angularaxis=dict(tickfont=dict(size=11, color='#E2E8F0'))
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
        title=f"<b>Head-to-Head Radar Comparison (Standardized Scale)</b>"
    )
    return fig

def create_gauge(value: float, title: str, min_val=0, max_val=100, color='#3B82F6'):
    """Speedometer gauge chart for pressure and task difficulty."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 14, 'color': '#E2E8F0'}},
        number={'font': {'size': 24, 'color': '#FFFFFF'}, 'valueformat': '.1f'},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': '#64748B'},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': 'rgba(30,41,59,0.8)',
            'borderwidth': 1,
            'bordercolor': '#475569',
            'steps': [
                {'range': [0, 30], 'color': 'rgba(100, 116, 139, 0.3)'},
                {'range': [30, 50], 'color': 'rgba(2, 132, 199, 0.3)'},
                {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
            ]
        }
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=15, r=15, t=35, b=15),
        height=170
    )
    return fig
