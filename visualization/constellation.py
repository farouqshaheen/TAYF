"""
طيف — TAYF
مخطط الكوكبة — بصمة الجريمة (QPSK Constellation)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG = "#0a0a0a"
IDEAL_POINTS = np.array([[1, 1], [-1, 1], [-1, -1], [1, -1]]) / np.sqrt(2)


def plot_constellation(snr_db: float, n_symbols: int = 500,
                       seed: int = 7) -> plt.Figure:
    """
    يرسم كوكبة QPSK مع ضوضاء مناسبة لقيمة SNR
    """
    rng = np.random.default_rng(seed)

    # تحويل SNR من dB لخطي
    snr_lin  = 10 ** (snr_db / 10)
    sigma    = 1 / np.sqrt(2 * snr_lin)   # انحراف الضوضاء

    fig, ax = plt.subplots(figsize=(5, 5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_aspect("equal")
    ax.tick_params(colors="#555")
    ax.spines[:].set_color("#222")
    ax.axhline(0, color="#222", linewidth=0.8)
    ax.axvline(0, color="#222", linewidth=0.8)
    ax.grid(color="#1a1a2e", linewidth=0.5)

    # اللون يعتمد على SNR
    if snr_db >= 15:
        color = "#00e676"   # أخضر — إشارة ممتازة
        label = f"إشارة نظيفة ✅  SNR = {snr_db:.1f} dB"
    elif snr_db >= 8:
        color = "#ffea00"   # أصفر — مقبول
        label = f"إشارة متوسطة ⚠️  SNR = {snr_db:.1f} dB"
    else:
        color = "#ff1744"   # أحمر — كارثة
        label = f"إشارة تالفة 🔴  SNR = {snr_db:.1f} dB"

    # توليد رموز عشوائية مع إضافة ضوضاء
    choices = rng.integers(0, 4, n_symbols)
    symbols = IDEAL_POINTS[choices]
    noisy   = symbols + rng.normal(0, sigma, symbols.shape)

    ax.scatter(noisy[:, 0], noisy[:, 1],
               color=color, alpha=0.4, s=12, linewidths=0)

    # النقاط المثالية
    ax.scatter(IDEAL_POINTS[:, 0], IDEAL_POINTS[:, 1],
               color="white", s=80, zorder=5, marker="+")

    # دوائر الخطأ
    for pt in IDEAL_POINTS:
        circle = plt.Circle(pt, sigma * 2, color=color,
                            fill=False, linewidth=0.8, alpha=0.5)
        ax.add_patch(circle)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_xlabel("I (In-phase)", color="#999", fontsize=9)
    ax.set_ylabel("Q (Quadrature)", color="#999", fontsize=9)
    ax.set_title("🔭 بصمة الجريمة — مخطط الكوكبة QPSK",
                 color="#e0e0e0", fontsize=11, fontweight="bold")
    ax.text(0, -1.85, label, ha="center", color=color, fontsize=9)

    return fig

