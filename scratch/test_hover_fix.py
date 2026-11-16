import plotly.graph_objects as go
import pandas as pd
import os

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector - Copy"
df = pd.read_csv(os.path.join(BASE_DIR, 'outputs', 'step_10_methodology_report', 'dashboard_batting_metrics.csv')).head(10)

# Option A: hovermode='x unified'
fig_unified = go.Figure()
fig_unified.add_trace(go.Bar(
    name='Normal / Routine (P < 50)',
    x=df['Player'],
    y=df['SVA_P_lt_50'],
    marker_color='#64748B',
    text=[f"{v:+.3f}" for v in df['SVA_P_lt_50']],
    textposition='auto',
    textfont=dict(size=11, color='#FFFFFF')
))
fig_unified.add_trace(go.Bar(
    name='High Pressure (P ≥ 50)',
    x=df['Player'],
    y=df['SVA_P_ge_50'],
    marker_color='#EA1B86',
    text=[f"{v:+.3f}" for v in df['SVA_P_ge_50']],
    textposition='auto',
    textfont=dict(size=11, color='#FFFFFF')
))
fig_unified.update_layout(
    barmode='group',
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,23,42,0.6)',
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='#0F172A',
        font_color='#FFFFFF',
        font_size=12,
        bordercolor='#475569'
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color='#F8FAFC', size=12)
    )
)
fig_unified.write_html('scratch/test_unified_hover.html')
print("Generated scratch/test_unified_hover.html")

# Option B: Explicit hovertemplate with custom colored label & clean extra
fig_custom = go.Figure()
fig_custom.add_trace(go.Bar(
    name='Normal / Routine (P < 50)',
    x=df['Player'],
    y=df['SVA_P_lt_50'],
    marker_color='#64748B',
    text=[f"{v:+.3f}" for v in df['SVA_P_lt_50']],
    textposition='auto',
    textfont=dict(size=11, color='#FFFFFF'),
    hoverlabel=dict(bgcolor='#1E293B', font_color='#FFFFFF', font_size=12),
    hovertemplate="<b>%{x}</b><br><span style='color:#94A3B8'>Normal / Routine (P < 50):</span> <b style='color:#FFFFFF'>%{y:+.4f} SVA</b><extra></extra>"
))
fig_custom.add_trace(go.Bar(
    name='High Pressure (P ≥ 50)',
    x=df['Player'],
    y=df['SVA_P_ge_50'],
    marker_color='#EA1B86',
    text=[f"{v:+.3f}" for v in df['SVA_P_ge_50']],
    textposition='auto',
    textfont=dict(size=11, color='#FFFFFF'),
    hoverlabel=dict(bgcolor='#1E293B', font_color='#FFFFFF', font_size=12),
    hovertemplate="<b>%{x}</b><br><span style='color:#F472B6'>High Pressure (P ≥ 50):</span> <b style='color:#FFFFFF'>%{y:+.4f} SVA</b><extra></extra>"
))
fig_custom.update_layout(
    barmode='group',
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,23,42,0.6)',
    hoverlabel=dict(
        bgcolor='#0F172A',
        font_color='#FFFFFF',
        font_size=12,
        bordercolor='#475569'
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color='#F8FAFC', size=12)
    )
)
fig_custom.write_html('scratch/test_custom_hover.html')
print("Generated scratch/test_custom_hover.html")
