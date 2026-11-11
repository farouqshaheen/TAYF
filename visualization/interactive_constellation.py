"""
طيف — TAYF
كوكبة QPSK التفاعلية — Interactive Plotly Constellation
"""
import plotly.graph_objects as go
import numpy as np

IDEAL_POINTS = np.array([[1, 1], [-1, 1], [-1, -1], [1, -1]]) / np.sqrt(2)

def create_interactive_constellation(snr_db: float, n_symbols: int = 400, seed: int = 7) -> go.Figure:
    """
    يرسم مخطط كوكبة تفاعلي بالكامل، يظهر نقاط الرموز المشوشة والمثالية
    مع إمكانية التقريب (Zoom) والتحويم (Hover)
    """
    rng = np.random.default_rng(seed)
    snr_lin = 10.0 ** (snr_db / 10.0)
    sigma = 1.0 / np.sqrt(2.0 * snr_lin)

    choices = rng.integers(0, 4, n_symbols)
    symbols = IDEAL_POINTS[choices]
    noisy = symbols + rng.normal(0, sigma, symbols.shape)

    if snr_db >= 15:
        color = "#00e676"
        status = "إشارة سليمة ومحكمة ✅"
    elif snr_db >= 8:
        color = "#ffd600"
        status = "تشتت طفيف ⚠️"
    else:
        color = "#ff1744"
        status = "انهيار وتشوه كارثي 🔴"

    fig = go.Figure()

    # الرموز المستلمة (مع الضوضاء)
    fig.add_trace(
        go.Scatter(
            x=noisy[:, 0], y=noisy[:, 1],
            mode="markers",
            name="الرموز المستلمة",
            marker=dict(size=6, color=color, opacity=0.55),
            hovertemplate="I: %{x:.2f}<br>Q: %{y:.2f}<extra></extra>"
        )
    )

    # النقاط المرجعية المثالية
    fig.add_trace(
        go.Scatter(
            x=IDEAL_POINTS[:, 0], y=IDEAL_POINTS[:, 1],
            mode="markers",
            name="الرموز الأصلية المثالية",
            marker=dict(size=14, color="#ffffff", symbol="cross", line=dict(width=2, color="#000")),
            hovertemplate="الرمز المثالي<br>I: %{x:.2f}<br>Q: %{y:.2f}<extra></extra>"
        )
    )

    # دوائر توضح مدى تشتت الخطأ
    shapes = []
    for pt in IDEAL_POINTS:
        shapes.append(dict(
            type="circle",
            xref="x", yref="y",
            x0=pt[0] - 2*sigma, y0=pt[1] - 2*sigma,
            x1=pt[0] + 2*sigma, y1=pt[1] + 2*sigma,
            line_color=color,
            line_width=1.5,
            opacity=0.4
        ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0c10",
        plot_bgcolor="#11141a",
        height=400,
        width=420,
        shapes=shapes,
        title=dict(text=f"🔭 كوكبة QPSK ({status})", font=dict(family="Tajawal", size=14)),
        xaxis=dict(range=[-2.2, 2.2], zeroline=True, zerolinecolor="#333", gridcolor="#1f2833", title="I (In-phase)"),
        yaxis=dict(range=[-2.2, 2.2], zeroline=True, zerolinecolor="#333", gridcolor="#1f2833", title="Q (Quadrature)"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

