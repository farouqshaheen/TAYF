"""
طيف — TAYF
ميزان الجريمة التفاعلي — Interactive Plotly BER Curve
إمكانية تحريك نقطة SNR بالماوس ورؤية تدهور حزم البيانات لحظياً
"""
import plotly.graph_objects as go
import numpy as np
from scipy.special import erfc

def qpsk_ber(snr_db_array: np.ndarray) -> np.ndarray:
    snr_lin = 10.0 ** (snr_db_array / 10.0)
    return 0.5 * erfc(np.sqrt(snr_lin))

def create_interactive_ber(current_snr: float, baseline_snr: float = 25.0) -> go.Figure:
    snr_range = np.linspace(-5, 25, 250)
    ber_vals = qpsk_ber(snr_range)

    curr_ber = float(qpsk_ber(np.array([current_snr]))[0])
    base_ber = float(qpsk_ber(np.array([baseline_snr]))[0])

    fig = go.Figure()

    # المنحنى النظري الأساسي
    fig.add_trace(go.Scatter(
        x=snr_range, y=ber_vals,
        mode="lines",
        name="منحنى QPSK النظري التنبؤي",
        line=dict(color="#00f0ff", width=3),
        hovertemplate="SNR: %{x:.1f} dB<br>احتمالية الخطأ BER: %{y:.2e}<extra></extra>"
    ))

    # النقطة الطبيعية قبل الحادث
    fig.add_trace(go.Scatter(
        x=[baseline_snr], y=[base_ber],
        mode="markers+text",
        name="طبيعي (قبل الحادث)",
        text=["🟢 نقطة الاستقرار"],
        textposition="top right",
        textfont=dict(color="#00e676", family="Tajawal", size=12),
        marker=dict(size=14, color="#00e676", symbol="circle", line=dict(color="#fff", width=2)),
        hovertemplate="الوضع المستقر:<br>SNR: %{x:.1f} dB<br>BER: %{y:.2e}<extra></extra>"
    ))

    # نقطة مسرح الجريمة الحالية
    fig.add_trace(go.Scatter(
        x=[current_snr], y=[curr_ber],
        mode="markers+text",
        name="الوضع الحالي (مسرح الجريمة)",
        text=["🔴 أنت هنا!"],
        textposition="bottom left",
        textfont=dict(color="#ff1744", family="Tajawal", size=13),
        marker=dict(size=18, color="#ff1744", symbol="x", line=dict(color="#fff", width=3)),
        hovertemplate="الموقع المتضرر:<br>SNR: %{x:.1f} dB<br>BER: %{y:.2e}<extra></extra>"
    ))

    # خط عتبة الجودة الحرجة 10^-3
    fig.add_hline(
        y=1e-3, line_dash="dash", line_color="#ff9100", line_width=1.5,
        annotation_text="عتبة سقوط المكالمات والصوت (10⁻³)",
        annotation_position="bottom right",
        annotation_font=dict(color="#ff9100", family="Tajawal", size=10)
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#090d16",
        plot_bgcolor="#050b14",
        height=450,
        title=dict(text="📈 ميزان الجريمة التفاعلي — موضع الاتصال على منحنى BER", font=dict(family="Tajawal", size=15, color="#00f0ff")),
        xaxis=dict(title="نسبة الإشارة إلى الضوضاء SNR (dB)", gridcolor="#162032"),
        yaxis=dict(title="معدل أخطاء البت BER (لوغاريتمي)", type="log", range=[-6, 0], gridcolor="#162032"),
        margin=dict(l=20, r=20, t=55, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig
