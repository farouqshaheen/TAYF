"""
طيف — TAYF
خريطة الرادار التفاعلية 2D و 3D — Surface & Heatmap (Plotly)
إمكانية التبديل بين خريطة طيفية مسطحة ومجسم ثلاثي الأبعاد 3D لتضاريس الإشارة!
"""
import plotly.graph_objects as go
import numpy as np
from simulation.wireless_link import received_power_dbm

def create_rich_heatmap(params, suspect: str = "طبيعي", incident_t: float = 0.0, view_mode: str = "2D") -> go.Figure:
    """
    تولد خريطة تفاعلية أو مجسم 3D طيفي يمكن تدويره في الفضاء بالماوس
    """
    size = 40
    max_km = params.dist_km * 3.2
    xs = np.linspace(-max_km, max_km, size)
    ys = np.linspace(-max_km, max_km, size)
    XX, YY = np.meshgrid(xs, ys)
    dist = np.sqrt(XX**2 + YY**2)
    dist = np.clip(dist, 0.002, None)

    # حساب FSPL
    pl = 32.44 + 20 * np.log10(params.freq_mhz) + 20 * np.log10(dist)
    rx = received_power_dbm(params.tx_power_dbm, params.tx_gain_dbi, params.rx_gain_dbi, pl)

    rng = np.random.default_rng(99)

    if suspect == "الغايب" and incident_t > 0:
        rx -= incident_t * 18
    elif suspect == "الشبح" and incident_t > 0:
        rx += rng.normal(0, incident_t * 8, rx.shape)
    elif suspect == "المرتجف" and incident_t > 0:
        rx += rng.normal(0, 8.5, rx.shape)
    elif suspect == "الظل" and incident_t > 0:
        shadow_col = int(size * incident_t * 0.75)
        rx[:, :shadow_col] -= incident_t * 24

    x_meters = xs * 1000
    y_meters = ys * 1000

    if view_mode == "3D المجسم الطيفي":
        fig = go.Figure(data=[go.Surface(
            z=rx,
            x=x_meters,
            y=y_meters,
            colorscale="Viridis",
            colorbar=dict(title="RSSI (dBm)", tickfont=dict(color="#00f0ff")),
            hovertemplate="الموقع: (%{x:.0f}m, %{y:.0f}m)<br>القدرة: %{z:.1f} dBm<extra></extra>"
        )])
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#090d16",
            height=500,
            title=dict(text="🌐 مجسم تضاريس الإشارة ثلاثي الأبعاد 3D (قم بتدويره بالماوس)", font=dict(family="Tajawal", size=15, color="#00f0ff")),
            scene=dict(
                xaxis=dict(title="المحور X (متر)", backgroundcolor="#050b14", gridcolor="#162032"),
                yaxis=dict(title="المحور Y (متر)", backgroundcolor="#050b14", gridcolor="#162032"),
                zaxis=dict(title="قوة الإشارة RSSI", backgroundcolor="#050b14", gridcolor="#162032"),
            ),
            margin=dict(l=10, r=10, t=50, b=10)
        )
    else:
        fig = go.Figure(data=go.Heatmap(
            z=rx,
            x=x_meters,
            y=y_meters,
            colorscale="Turbo",
            zmin=-105, zmax=-45,
            colorbar=dict(title="RSSI (dBm)", tickfont=dict(color="#c5c6c7")),
            hovertemplate="الموقع: (%{x:.0f}m, %{y:.0f}m)<br>قوة الإشارة: %{z:.1f} dBm<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode="markers+text",
            marker=dict(symbol="star", size=18, color="#ffffff", line=dict(color="#00f0ff", width=2)),
            text=["📡 برج الإرسال"],
            textposition="top center",
            textfont=dict(color="#ffffff", size=12, family="Tajawal"),
            name="برج الإرسال"
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#090d16",
            plot_bgcolor="#050b14",
            height=460,
            title=dict(text=f"🌡️ مسح التغطية اللاسلكية الراداري 2D ({suspect} — شدة الحادث: {incident_t:.0%})", font=dict(family="Tajawal", size=15, color="#00f0ff")),
            xaxis=dict(title="البعد السيني (متر)", gridcolor="#162032"),
            yaxis=dict(title="البعد الصادي (متر)", gridcolor="#162032"),
            margin=dict(l=20, r=20, t=50, b=20)
        )

    return fig
