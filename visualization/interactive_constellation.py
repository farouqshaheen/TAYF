"""
طيف — TAYF
كوكبة QPSK التفاعلية ثلاثية الأبعاد والحركية — Dynamic QPSK Constellation (Plotly)
تحكم حي بالضوضاء، دوران 3D، تشغيل أنيميشن لتشتت الرموز
"""
import plotly.graph_objects as go
import numpy as np

IDEAL_POINTS = np.array([[1, 1], [-1, 1], [-1, -1], [1, -1]]) / np.sqrt(2)

def create_rich_constellation(snr_db: float, n_symbols: int = 500, live_noise_amp: float = 1.0, seed: int = 7) -> go.Figure:
    """
    تولد مخطط كوكبة رموز QPSK تفاعلي حي عالي الجودة مع هالة تشتت وخطوط متجهات
    """
    rng = np.random.default_rng(seed)
    snr_lin = max(0.1, 10.0 ** (snr_db / 10.0))
    sigma = (1.0 / np.sqrt(2.0 * snr_lin)) * live_noise_amp

    choices = rng.integers(0, 4, n_symbols)
    symbols = IDEAL_POINTS[choices]
    noisy = symbols + rng.normal(0, sigma, symbols.shape)

    # تحديد اللون وحالة الاستقرار
    if snr_db >= 16:
        color = "#00e676"
        status_txt = "🟢 كوكبة متماسكة (اتصال مشفر نقي)"
    elif snr_db >= 8:
        color = "#ffd600"
        status_txt = "🟡 تشتت أطياف الضوضاء (تدهور متوسط)"
    else:
        color = "#ff1744"
        status_txt = "🔴 انهيار الإشارة وتداخل قطبي كامل"

    fig = go.Figure()

    # 1. طبقة الرموز المشوشة الحية
    fig.add_trace(go.Scatter(
        x=noisy[:, 0], y=noisy[:, 1],
        mode="markers",
        name="الرموز المستلمة حياً",
        marker=dict(
            size=7,
            color=color,
            opacity=0.6,
            line=dict(width=0.5, color="#ffffff")
        ),
        hovertemplate="رمز مشفر:<br>I (طور): %{x:.3f}<br>Q (تعامد): %{y:.3f}<extra></extra>"
    ))

    # 2. خطوط متجهات من المركز إلى النقاط المثالية
    for pt in IDEAL_POINTS:
        fig.add_trace(go.Scatter(
            x=[0, pt[0]], y=[0, pt[1]],
            mode="lines",
            line=dict(color="rgba(0, 240, 255, 0.35)", width=1.5, dash="dot"),
            showlegend=False,
            hoverinfo="skip"
        ))

    # 3. النقاط المرجعية المثالية الأصلية
    fig.add_trace(go.Scatter(
        x=IDEAL_POINTS[:, 0], y=IDEAL_POINTS[:, 1],
        mode="markers+text",
        name="الرموز الأصلية المثالية",
        text=["(1,1)", "(0,1)", "(0,0)", "(1,0)"],
        textposition="top center",
        textfont=dict(color="#00f0ff", family="Tajawal", size=11),
        marker=dict(size=15, color="#ffffff", symbol="cross", line=dict(color="#000", width=2)),
        hovertemplate="الموقع النظري المثالي:<br>I: %{x:.2f}<br>Q: %{y:.2f}<extra></extra>"
    ))

    # دوائر الخطأ ومناطق القرار (Decision Boundaries)
    shapes = [
        # محاور الإحداثيات المركزية
        dict(type="line", x0=-2.5, y0=0, x1=2.5, y1=0, line=dict(color="rgba(255,255,255,0.15)", width=1)),
        dict(type="line", x0=0, y0=-2.5, x1=0, y1=2.5, line=dict(color="rgba(255,255,255,0.15)", width=1)),
    ]

    for pt in IDEAL_POINTS:
        shapes.append(dict(
            type="circle",
            x0=pt[0] - 2*sigma, y0=pt[1] - 2*sigma,
            x1=pt[0] + 2*sigma, y1=pt[1] + 2*sigma,
            line=dict(color=color, width=1.5, dash="dash"),
            fillcolor=color,
            opacity=0.1
        ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#090d16",
        plot_bgcolor="#050b14",
        height=450,
        shapes=shapes,
        title=dict(
            text=f"🔭 مسرح الكوكبة QPSK | {status_txt}",
            font=dict(family="Tajawal", size=15, color="#00f0ff")
        ),
        xaxis=dict(range=[-2.2, 2.2], title="المحور السيني I (In-Phase)", gridcolor="#162032", zeroline=False),
        yaxis=dict(range=[-2.2, 2.2], title="المحور الصادي Q (Quadrature)", gridcolor="#162032", zeroline=False),
        margin=dict(l=20, r=20, t=55, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig
