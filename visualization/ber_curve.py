"""
طيف — TAYF
ميزان الجريمة — منحنى معدل أخطاء البت (BER Curve) لـ QPSK
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erfc

BG = "#0a0a0a"

def qpsk_ber(snr_db_array: np.ndarray) -> np.ndarray:
    """BER = 0.5 * erfc(sqrt(10^(SNR/10)))"""
    snr_lin = 10.0 ** (snr_db_array / 10.0)
    return 0.5 * erfc(np.sqrt(snr_lin))

def plot_ber_curve(current_snr: float, baseline_snr: float | None = None) -> plt.Figure:
    """
    يرسم منحنى BER النظري ويحدد موقع الإشارة الحالي وقبل الحادث
    """
    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors="#e0e0e0")
    ax.spines[:].set_color("#222")
    ax.grid(color="#1a1a2e", linewidth=0.6, which="both")

    snr_range = np.linspace(-5, 20, 200)
    ber_vals = qpsk_ber(snr_range)

    ax.semilogy(snr_range, ber_vals, color="#00e5ff", linewidth=2, label="منحنى QPSK النظري")

    # النقطة قبل الحادث (Baseline)
    if baseline_snr is not None:
        base_ber = float(qpsk_ber(np.array([baseline_snr]))[0])
        ax.scatter([baseline_snr], [base_ber], color="#00e676", s=100, zorder=5, label=f"قبل الحادث ({baseline_snr:.1f} dB)")
        ax.annotate("طبيعي", (baseline_snr, base_ber), textcoords="offset points", xytext=(-20, 10),
                    color="#00e676", fontweight="bold", fontsize=9)

    # النقطة الحالية (Current / Incident)
    curr_ber = float(qpsk_ber(np.array([current_snr]))[0])
    ax.scatter([current_snr], [curr_ber], color="#ff1744", s=130, zorder=6, label=f"الوضع الحالي ({current_snr:.1f} dB)")
    ax.annotate("أنت هنا 🔴", (current_snr, curr_ber), textcoords="offset points", xytext=(10, 10),
                color="#ff1744", fontweight="bold", fontsize=10)

    # خط العتبة الحرجة
    ax.axhline(1e-3, color="#ff9100", linestyle="--", linewidth=1, alpha=0.7, label="عتبة مقبولة (10⁻³)")

    ax.set_ylim(1e-6, 1)
    ax.set_xlim(-5, 20)
    ax.set_xlabel("نسبة الإشارة إلى الضوضاء SNR (dB)", color="#e0e0e0", fontsize=10)
    ax.set_ylabel("معدل أخطاء البت BER", color="#e0e0e0", fontsize=10)
    ax.set_title("📈 ميزان الجريمة — منحنى BER لـ QPSK", color="#e0e0e0", fontsize=12, fontweight="bold")
    ax.legend(facecolor="#111", labelcolor="#e0e0e0", fontsize=8, loc="upper right")

    return fig

