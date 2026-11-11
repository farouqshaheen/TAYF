"""Smooth, readable 2D/3D propagation maps for the TAYF wireless lab."""

import numpy as np
import plotly.graph_objects as go

from simulation.wireless_link import received_power_dbm

FONT = "IBM Plex Sans Arabic, sans-serif"
INK = "#e7edf5"
MUTED = "#91a2b8"
GRID = "rgba(129,157,180,.2)"
PALETTE = [
    [0.0, "#16283a"],
    [0.22, "#1b5264"],
    [0.48, "#2a8991"],
    [0.72, "#52e0d1"],
    [0.88, "#ffbd69"],
    [1.0, "#ff6f7d"],
]


def create_rich_heatmap(
    params,
    suspect: str = "طبيعي",
    incident_t: float = 0.0,
    view_mode: str = "2D",
    metric: str = "RSSI",
) -> go.Figure:
    """Create an interactive spatial field without pixel-noise artifacts.

    metric is either RSSI (received power) or SNR (signal-to-noise ratio).
    Interference therefore lowers the SNR layer without falsely lowering RSSI.
    """
    incident_t = float(np.clip(incident_t, 0.0, 1.0))
    size = 56
    max_km = max(float(params.dist_km) * 3.2, 0.04)
    xs = np.linspace(-max_km, max_km, size)
    ys = np.linspace(-max_km, max_km, size)
    XX, YY = np.meshgrid(xs, ys)
    dist_km = np.clip(np.sqrt(XX**2 + YY**2), 0.002, None)
    dist_m = dist_km * 1000.0

    path_loss = 32.44 + 20 * np.log10(params.freq_mhz) + 20 * np.log10(dist_km)
    rssi = received_power_dbm(
        params.tx_power_dbm,
        params.tx_gain_dbi,
        params.rx_gain_dbi,
        path_loss,
    )

    # Spatially structured effects are deterministic and smooth, unlike pixel-wise random noise.
    if suspect == "الغايب" and incident_t:
        rssi -= incident_t * 18.0
    elif suspect == "المرتجف" and incident_t:
        wavelength_m = 300.0 / max(float(params.freq_mhz), 1.0)
        multipath = np.sin(2 * np.pi * dist_m / max(wavelength_m, 0.03))
        cross_path = np.cos(2 * np.pi * XX * 1000.0 / max(1.7 * wavelength_m, 0.05))
        rssi += incident_t * 5.5 * multipath * cross_path
    elif suspect == "الظل" and incident_t:
        x_m = XX * 1000.0
        shadow_edge = max_km * 1000.0 * (0.15 + 0.45 * incident_t)
        shadow_width = max(max_km * 1000.0 * 0.12, 4.0)
        shadow_mask = 0.5 * (1.0 + np.tanh((x_m - shadow_edge) / shadow_width))
        rssi -= incident_t * 22.0 * shadow_mask

    if metric.upper() == "SNR":
        values = rssi - float(params.noise_dbm)
        if suspect == "الشبح":
            values -= incident_t * (12.0 + 15.0 * incident_t)
        elif suspect == "الغايب":
            values -= incident_t * 18.0
        values = np.clip(values, -10.0, 60.0)
        colorbar_title = "SNR · dB"
        z_title = "جودة الرابط · SNR (dB)"
        hover_label = "SNR"
        bound_min, bound_max = -10.0, 60.0
    else:
        values = rssi
        if suspect == "الشبح":
            # Interference degrades quality, not received signal strength.
            pass
        colorbar_title = "RSSI · dBm"
        z_title = "قوة الإشارة · RSSI (dBm)"
        hover_label = "RSSI"
        bound_min, bound_max = -120.0, -20.0

    # Stretch colors to the observed field (with robust percentile clipping) so
    # small changes remain visible without allowing one outlier to dominate.
    observed_min, observed_max = np.nanpercentile(values, [3, 97])
    color_pad = max(float(observed_max - observed_min) * 0.08, 1.0)
    zmin = max(bound_min, float(observed_min) - color_pad)
    zmax = min(bound_max, float(observed_max) + color_pad)
    if zmax - zmin < 2.0:
        center = (zmax + zmin) / 2.0
        zmin, zmax = center - 1.0, center + 1.0

    x_meters = xs * 1000.0
    y_meters = ys * 1000.0
    mode_3d = "3D" in view_mode
    title_metric = "جودة الرابط SNR" if metric.upper() == "SNR" else "قوة الإشارة RSSI"
    title = f"{title_metric} حول المرسل · {suspect} · شدة {incident_t:.0%}"

    if mode_3d:
        fig = go.Figure(
            data=[
                go.Surface(
                    z=values,
                    x=x_meters,
                    y=y_meters,
                    colorscale=PALETTE,
                    cmin=zmin,
                    cmax=zmax,
                    colorbar=dict(title=colorbar_title, tickfont=dict(color=MUTED), thickness=15),
                    lighting=dict(ambient=0.68, diffuse=0.75, specular=0.18, roughness=0.8),
                    contours=dict(
                        z=dict(show=True, usecolormap=True, project_z=True, highlightcolor="#ffffff", width=1),
                    ),
                    hovertemplate="الموقع: (%{x:.0f}, %{y:.0f}) m<br>" + hover_label + ": %{z:.1f}<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            title=dict(text=title, x=0.98, xanchor="right", font=dict(family=FONT, size=14, color=INK)),
            scene=dict(
                bgcolor="#0b1520",
                xaxis=dict(title="X · متر", backgroundcolor="#0b1520", gridcolor=GRID, color=MUTED),
                yaxis=dict(title="Y · متر", backgroundcolor="#0b1520", gridcolor=GRID, color=MUTED),
                zaxis=dict(title=z_title, backgroundcolor="#0b1520", gridcolor=GRID, color=MUTED, range=[zmin, zmax]),
                camera=dict(eye=dict(x=1.55, y=1.55, z=1.1)),
                aspectmode="manual",
                aspectratio=dict(x=1.25, y=1.25, z=0.72),
            ),
            height=540,
            margin=dict(l=8, r=8, t=54, b=8),
        )
    else:
        fig = go.Figure(
            data=[
                go.Heatmap(
                    z=values,
                    x=x_meters,
                    y=y_meters,
                    colorscale=PALETTE,
                    zmin=zmin,
                    zmax=zmax,
                    zsmooth="best",
                    colorbar=dict(title=colorbar_title, tickfont=dict(color=MUTED), thickness=15),
                    hovertemplate="الموقع: (%{x:.0f}, %{y:.0f}) m<br>" + hover_label + ": %{z:.1f}<extra></extra>",
                ),
                go.Scatter(
                    x=[0],
                    y=[0],
                    mode="markers+text",
                    marker=dict(symbol="circle", size=13, color="#f7fbff", line=dict(color="#52e0d1", width=3)),
                    text=["المرسل"],
                    textposition="top center",
                    textfont=dict(color=INK, size=11, family=FONT),
                    name="موقع المرسل",
                    hovertemplate="نقطة الإرسال<extra></extra>",
                ),
            ]
        )
        fig.update_layout(
            title=dict(text=title, x=0.98, xanchor="right", font=dict(family=FONT, size=14, color=INK)),
            xaxis=dict(title="X · متر", gridcolor=GRID, zeroline=False, scaleanchor="y", scaleratio=1),
            yaxis=dict(title="Y · متر", gridcolor=GRID, zeroline=False),
            height=500,
            margin=dict(l=12, r=12, t=55, b=15),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1520",
        font=dict(family=FONT, color=INK, size=11),
        hoverlabel=dict(bgcolor="#102131", bordercolor="#355066", font=dict(family=FONT, color=INK)),
    )
    return fig
