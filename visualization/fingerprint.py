"""
طيف — TAYF
بصمة الجريمة الإحصائية — Radar / Spider Chart
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG = "#0a0a0a"

def plot_fingerprint(metrics_dict: dict, suspect_name: str = "مجهول") -> plt.Figure:
    """
    يرسم مخطط رادار (Spider Chart) لبصمة الإشارة الحالية
    metrics_dict: قيم مطبّعة بين 0 و 1 لمؤشرات معينة:
      - انخفاض القوة (Power Drop)
      - انهيار SNR (SNR Drop)
      - التذبذب والارتجاف (Fluctuation / Variance)
      - التدهور التدريجي (Slope / Drift)
      - فقدان الحزم (Packet Loss)
    """
    labels = [
        "انخفاض القوة 🌑",
        "انهيار SNR 👻",
        "الارتجاف ⚡",
        "التدهور التدريجي 🌫️",
        "فقدان الحزم 📦"
    ]
    num_vars = len(labels)

    # حساب الزوايا
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # إغلاق الدائرة

    # القيم المطبّعة
    values = [
        min(1.0, max(0.0, metrics_dict.get("power_drop", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("snr_drop", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("fluctuation", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("drift", 0.0))),
        min(1.0, max(0.0, metrics_dict.get("packet_loss", 0.0))),
    ]
    values += values[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor=BG)
    ax.set_facecolor(BG)

    # إعدادات المحاور
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, color="#e0e0e0", fontsize=9, fontweight="bold")

    ax.set_ylim(0, 1)
    ax.set_rgrids([0.2, 0.4, 0.6, 0.8, 1.0], labels=[])
    ax.grid(color="#333333", linewidth=0.7)
    ax.spines["polar"].set_color("#444")

    # رسم البصمة
    ax.plot(angles, values, color="#ff1744", linewidth=2, linestyle="solid")
    ax.fill(angles, values, color="#ff1744", alpha=0.35)

    ax.set_title(f"🕸️ البصمة الجنائية للإشارة ({suspect_name})", color="#e0e0e0", fontsize=11, fontweight="bold", pad=20)

    return fig

