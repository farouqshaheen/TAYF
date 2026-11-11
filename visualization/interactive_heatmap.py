"""
طيف — TAYF
خريطة التغطية التفاعلية 2D و 3D — Interactive Plotly Heatmap
"""
import plotly.graph_objects as go
import numpy as np
from simulation.wireless_link import received_power_dbm

def create_interactive_heatmap(params, suspect: str = "طبيعي", incident_t: float = 0.0) -> go.Figure:
    """
    تولد خريطة حرارية تفاعلية ملونة للرادار اللاسلكي
    """
    size = 45
    max_km = params.dist_km * 3.5
    xs = np.linspace(-max_km, max_km, size)
    ys = np.linspace(-max_km, max_km, size)
    XX, YY = np.meshgrid(xs, ys)
    dist = np.sqrt(XX**2 + YY**2)
    dist = np.clip(dist, 0.001, None)

    # حساب FSPL
    pl = 32.44 + 20 * np.log10(params.freq_mhz) + 20 * np.log10(dist)
    rx = received_power_dbm(params.tx_power_dbm, params.tx_gain_dbi, params.rx_gain_dbi, pl)

    rng = np.random.default_rng(99)

    if suspect == "الغايب" and incident_t > 0:
        rx -= incident_t * 18
    elif suspect == "الشبح" and incident_t > 0:
        rx += rng.normal(0, incident_t * 7, rx.shape)
    elif suspect == "المرتجف" and incident_t > 0:
        rx += rng.normal(0, 8, rx.shape)
    elif suspect == "الظل" and incident_t > 0:
        shadow_col = int(size * incident_t * 0.75)
        rx[:, :shadow_col] -= incident_t * 22

    fig = go.Figure(data=go.Heatmap(
        z=rx,
        x=xs * 1000, # تحويل لمتر
        y=ys * 1000,
        colorscale="RdYlGn",
        zmin=-105, zmax=-45,
        colorbar=dict(title="RSSI (dBm)", tickfont=dict(color="#c5c6c7")),
        hovertemplate="الموقع: (%{x:.0f}m, %{y:.0f}m)<br>قوة الإشارة: %{z:.1f} dBm<extra></extra>"
    ))

    # موقع برج الإرسال في المنتصف
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode="markers+text",
        marker=dict(symbol="star", size=16, color="#ffffff", line=dict(color="#000", width=1.5)),
        text=["📡 برج الإرسال"],
        textposition="top center",
        textfont=dict(color="#ffffff", size=12, family="Tajawal"),
        name="المرسل"
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0c10",
        plot_bgcolor="#11141a",
        height=450,
        title=dict(text=f"🌡️ مسح التغطية اللاسلكية ({suspect} — شدة الحادث: {incident_t:.0%})", font=dict(family="Tajawal", size=14)),
        xaxis=dict(title="البعد السيني (متر)", gridcolor="#1f2833"),
        yaxis=dict(title="البعد الصادي (متر)", gridcolor="#1f2833"),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig

