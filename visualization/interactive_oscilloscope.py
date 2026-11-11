"""
طيف — TAYF
راسم الذبذبات التفاعلي والمتحرك — Interactive Plotly Oscilloscope
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_interactive_heartbeat(df: pd.DataFrame, current_step: int | None = None) -> go.Figure:
    """
    ينشئ راسم ذبذبات تفاعلي بالكامل باللون النيون السيبراني الداكن
    current_step: إذا تم تمريره، يرسم حتى هذه اللحظة فقط لعمل حركة وتدفق زمني حي
    """
    if current_step is not None:
        sub_df = df.iloc[:current_step + 1]
    else:
        sub_df = df

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("📡 قوة الإشارة المستقبَلة RSSI (dBm)", "⚡ نسبة الإشارة إلى الضوضاء SNR (dB)")
    )

    t = sub_df["timestamp_s"]
    rssi = sub_df["rssi_dbm"]
    snr = sub_df["snr_db"]
    phase = sub_df["phase"]

    # 1. رسم خط RSSI
    fig.add_trace(
        go.Scatter(
            x=t, y=rssi,
            mode="lines+markers",
            name="RSSI (dBm)",
            line=dict(color="#00e676", width=2.5),
            marker=dict(size=4, color="#00e676"),
            hovertemplate="الوقت: %{x} ثانية<br>RSSI: %{y:.2f} dBm<extra></extra>"
        ),
        row=1, col=1
    )

    # 2. رسم خط SNR
    fig.add_trace(
        go.Scatter(
            x=t, y=snr,
            mode="lines+markers",
            name="SNR (dB)",
            line=dict(color="#ffd600", width=2.5),
            marker=dict(size=4, color="#ffd600"),
            hovertemplate="الوقت: %{x} ثانية<br>SNR: %{y:.2f} dB<extra></extra>"
        ),
        row=2, col=1
    )

    # إضافة خط لحظة وقوع الحادث عند الثانية 20
    if len(sub_df) > 20:
        fig.add_vline(x=20, line_width=2, line_dash="dash", line_color="#ff1744", row="all", col=1)
        fig.add_annotation(
            x=20, y=rssi.max() if len(rssi) > 0 else 0,
            text="🚨 بدء الحادث (مسرح الجريمة)",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#ff1744",
            font=dict(color="#ffffff", size=11, family="Tajawal"),
            bgcolor="#1a0808",
            bordercolor="#ff1744",
            row=1, col=1
        )

    # خط عتبة الجودة لـ SNR عند 10 dB
    fig.add_hline(y=10, line_width=1.5, line_dash="dot", line_color="#ff9100", row=2, col=1)

    # تصميم الشاشة السيبرانية الداكنة (ECG Cyber Monitor)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0c10",
        plot_bgcolor="#11141a",
        height=480,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Tajawal", color="#c5c6c7")
    )

    fig.update_xaxes(
        showgrid=True, gridwidth=0.5, gridcolor="#1f2833",
        title_text="الوقت بالثواني", row=2, col=1
    )
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="#1f2833", row=1, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="#1f2833", row=2, col=1)

    return fig

