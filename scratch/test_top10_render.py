import pandas as pd
import plotly.graph_objects as go
import os

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector - Copy"

def test_top10(discipline):
    path = os.path.join(BASE_DIR, 'outputs', 'step_7_empirical_calibration', 'step_7_4_final_rankings', f'final_{discipline}_rankings.csv')
    df = pd.read_csv(path)
    df_sorted = df.head(10).iloc[::-1].copy()
    
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

    if discipline.lower() == 'batting':
        colorscale = [
            [0.0, '#FDA4AF'],   # Soft rose pink (Rank 10)
            [0.35, '#FB7185'],  # Rose 400
            [0.65, '#EA1B86'],  # RR Royal Pink
            [1.0, '#831843']    # Deep Royal Crimson (Rank 1)
        ]
    else:
        colorscale = [
            [0.0, '#FDE68A'],   # Soft warm gold (Rank 10)
            [0.35, '#F59E0B'],  # Amber 500
            [0.65, '#D97706'],  # Rich Bronze Gold
            [1.0, '#78350F']    # Deep Royal Amber (Rank 1)
        ]

    s_min = df_sorted['Shrunk score'].min()
    s_max = df_sorted['Shrunk score'].max()
    norms = (df_sorted['Shrunk score'] - s_min) / (s_max - s_min + 1e-9)
    text_colors = ['#0F172A' if n < 0.48 else '#FFFFFF' for n in norms]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted['Player'],
        x=df_sorted['Shrunk score'],
        orientation='h',
        marker=dict(
            color=df_sorted['Shrunk score'],
            colorscale=colorscale,
            line=dict(color='#334155', width=1)
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
        text=[f"<b>#{r['Rank']}  {r['Shrunk score']:.4f} (ESS: {r['Kish ESS']:.0f})</b>" for _, r in df_sorted.iterrows()],
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(color=text_colors, size=12, family='system-ui, -apple-system, sans-serif'),
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
    
    out_html = f"scratch/test_{discipline}_bar.html"
    fig.write_html(out_html)
    print(f"Generated {out_html}")

test_top10('batting')
test_top10('bowling')
