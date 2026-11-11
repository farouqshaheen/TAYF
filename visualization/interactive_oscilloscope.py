"""Clear, selectable wireless-link traces for TAYF's investigation dashboard."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

INK = "#e7edf5"
MUTED = "#91a2b8"
GRID = "rgba(129,157,180,.14)"
PANEL = "#0b1520"
CYAN = "#52e0d1"
AMBER = "#ffbd69"
RED = "#ff6f7d"
FONT = "IBM Plex Sans Arabic, sans-serif"


def create_interactive_heartbeat(df: pd.DataFrame, current_step: int | None = None) -> go.Figure:
    """Build a clean two-track time series with incident and cursor overlays."""
    if current_step is None:
        sub_df = df
    else:
        sub_df = df.iloc[: max(0, int(current_step)) + 1]

    if sub_df.empty:
        sub_df = df.iloc[:1]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.13,
        row_heights=[0.52, 0.48],
        subplot_titles=("قوة الإشارة المستقبلة · RSSI", "جودة الرابط · SNR"),
    )

    t = sub_df["timestamp_s"]
    incident_start = float(df.loc[df["phase"] == "حادث", "timestamp_s"].min())
    end_time = float(sub_df["timestamp_s"].max())

    fig.add_trace(
        go.Scatter(
            x=t,
            y=sub_df["rssi_dbm"],
            mode="lines",
            name="RSSI · dBm",
            line=dict(color=CYAN, width=2.7, shape="linear"),
            hovertemplate="الزمن: %{x:.0f} ث<br>RSSI: %{y:.1f} dBm<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=t,
            y=sub_df["snr_db"],
            mode="lines",
            name="SNR · dB",
            line=dict(color=AMBER, width=2.7, shape="linear"),
            hovertemplate="الزمن: %{x:.0f} ث<br>SNR: %{y:.1f} dB<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Mark only the selected sample; avoid the visual clutter of a marker on every sample.
    if current_step is not None and int(current_step) < len(df):
        row = df.iloc[int(current_step)]
        for trace_y, trace_row, color in (
            (row["rssi_dbm"], 1, CYAN),
            (row["snr_db"], 2, AMBER),
        ):
            fig.add_trace(
                go.Scatter(
                    x=[row["timestamp_s"]],
                    y=[trace_y],
                    mode="markers",
                    name="اللحظة المختارة" if trace_row == 1 else None,
                    showlegend=trace_row == 1,
                    marker=dict(size=10, color=color, line=dict(color="#f7fbff", width=2)),
                    hovertemplate="اللحظة المختارة<br>%{x:.0f} ث · %{y:.1f}<extra></extra>",
                ),
                row=trace_row,
                col=1,
            )
        fig.add_vline(
            x=float(row["timestamp_s"]),
            line_width=1,
            line_dash="dot",
            line_color="rgba(231,237,245,.55)",
            row="all",
            col=1,
        )

    if end_time >= incident_start:
        fig.add_vrect(
            x0=incident_start,
            x1=end_time,
            fillcolor="rgba(255,111,125,.07)",
            line_width=0,
            row="all",
            col=1,
        )
    if end_time >= incident_start:
        fig.add_vline(
            x=incident_start,
            line_width=1.5,
            line_dash="dash",
            line_color=RED,
            row="all",
            col=1,
        )
        fig.add_annotation(
            x=incident_start,
            y=1.015,
            xref="x",
            yref="paper",
            text="بداية الحادث",
            showarrow=False,
            xanchor="left",
            font=dict(family=FONT, size=10, color=RED),
            bgcolor="rgba(11,21,32,.92)",
            borderpad=4,
        )

    fig.add_hline(
        y=10,
        line_width=1,
        line_dash="dot",
        line_color="rgba(255,189,105,.72)",
        row=2,
        col=1,
        annotation_text="عتبة SNR = 10 dB",
        annotation_position="bottom right",
        annotation_font=dict(family=FONT, size=9, color=AMBER),
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PANEL,
        height=510,
        margin=dict(l=18, r=22, t=52, b=24),
        font=dict(family=FONT, color=INK, size=11),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#102131", bordercolor="#355066", font=dict(family=FONT, color=INK)),
        showlegend=False,
    )
    fig.update_annotations(font=dict(family=FONT, color=MUTED, size=11))
    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        rangeslider=dict(visible=True, thickness=0.055, bgcolor="#101f2d", bordercolor="#294052"),
        row=2,
        col=1,
        title_text="الزمن المحاكى · ثانية",
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, title_text="dBm", row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, title_text="dB", row=2, col=1)
    return fig
