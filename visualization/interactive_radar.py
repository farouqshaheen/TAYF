"""
طيف — TAYF
بصمة التوقيع الجنائي الرادارية التفاعلية — Interactive Plotly Radar
"""
import plotly.graph_objects as go

def create_interactive_radar(metrics_dict: dict, suspect_name: str = "مجهول") -> go.Figure:
    categories = [
        "انخفاض القوة 🌑",
        "انهيار SNR 👻",
        "الارتجاف ⚡",
        "التدهور التدريجي 🌫️",
        "فقدان الحزم 📦"
    ]
    
    values = [
        min(1.0, max(0.0, metrics_dict.get("power_drop", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("snr_drop", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("fluctuation", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("drift", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("packet_loss", 0.0))),
    ]
    # إغلاق مضلع الرادار
    values.append(values[0])
    cat_closed = categories + [categories[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=cat_closed,
        fill="toself",
        fillcolor="rgba(255, 23, 68, 0.35)",
        line=dict(color="#ff1744", width=3),
        marker=dict(size=8, color="#ffffff"),
        name="بصمة الإشارة الحالية",
        hovertemplate="المؤشر: %{theta}<br>الشدة الجنائية: %{r:.2f}<extra></extra>"
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#090d16",
        polar=dict(
            bgcolor="#050b14",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#162032", tickfont=dict(color="#64748b")),
            angularaxis=dict(gridcolor="#162032", tickfont=dict(family="Tajawal", size=11, color="#00f0ff"))
        ),
        showlegend=False,
        height=400,
        margin=dict(l=35, r=35, t=45, b=30),
        title=dict(text=f"🕸️ بصمة التوقيع الجنائي للإشارة ({suspect_name})", font=dict(family="Tajawal", size=14, color="#00f0ff"))
    )

    return fig
