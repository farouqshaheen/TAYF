"""
طيف — TAYF
خريطة التغطية الحرارية — 2D signal strength map
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from simulation.wireless_link import fspl_db, received_power_dbm


BG = "#0a0a0a"


def _make_grid(params, suspect: str, incident_t: float = 0.0) -> np.ndarray:
    """
    يبني شبكة 60×60 من قيم RSSI (dBm)
    incident_t: 0=أساسي .. 1=ذروة الحادث
    """
    size    = 60
    max_km  = params.dist_km * 4
    xs      = np.linspace(-max_km, max_km, size)
    ys      = np.linspace(-max_km, max_km, size)
    XX, YY  = np.meshgrid(xs, ys)
    dist    = np.sqrt(XX**2 + YY**2)
    dist    = np.clip(dist, 0.001, None)

    # خسارة أساسية
    pl = 32.44 + 20*np.log10(params.freq_mhz) + 20*np.log10(dist)
    rx = received_power_dbm(params.tx_power_dbm,
                            params.tx_gain_dbi,
                            params.rx_gain_dbi,
                            pl)

    rng = np.random.default_rng(99)

    if suspect == "الغايب" and incident_t > 0:
        # الأحمر يزحف للداخل (تقليص منطقة التغطية)
        rx -= incident_t * 15

    elif suspect == "الشبح" and incident_t > 0:
        # ضوضاء عشوائية على كل الخريطة
        rx += rng.normal(0, incident_t * 8, rx.shape)

    elif suspect == "المرتجف" and incident_t > 0:
        # وميض (تذبذب سريع)
        rx += rng.normal(0, 10, rx.shape)

    elif suspect == "الظل" and incident_t > 0:
        # ظل يزحف من الجانب الأيسر
        shadow_col = int(size * incident_t * 0.8)
        rx[:, :shadow_col] -= incident_t * 20

    return rx


def plot_heatmap(params, suspect: str = "طبيعي",
                 incident_t: float = 0.0) -> plt.Figure:
    """
    يرسم خريطة التغطية الحرارية
    incident_t: 0=طبيعي .. 1=ذروة الحادث
    """
    grid = _make_grid(params, suspect, incident_t)

    fig, ax = plt.subplots(figsize=(6, 5), facecolor=BG)
    ax.set_facecolor(BG)

    cmap = plt.cm.RdYlGn   # أحمر=ضعيف، أصفر=متوسط، أخضر=قوي
    vmin, vmax = -110, -40

    im = ax.imshow(grid, cmap=cmap, vmin=vmin, vmax=vmax,
                   origin="lower", interpolation="bilinear",
                   extent=[-1, 1, -1, 1])

    # نقطة المرسل
    ax.scatter([0], [0], color="white", s=120, zorder=5,
               marker="*", label="المرسل")
    ax.set_title("🌡️ خريطة التغطية الحرارية",
                 color="#e0e0e0", fontsize=12, fontweight="bold")
    ax.tick_params(colors="#e0e0e0")
    ax.spines[:].set_color("#222")

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("RSSI (dBm)", color="#e0e0e0")
    cbar.ax.yaxis.set_tick_params(color="#e0e0e0")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#e0e0e0")

    if suspect != "طبيعي" and incident_t > 0.1:
        from simulation.scenarios import SUSPECTS
        info = SUSPECTS.get(suspect, {})
        emoji = info.get("emoji", "")
        ax.set_xlabel(f"{emoji} {suspect} — شدة الحادث: {incident_t:.0%}",
                      color="#ff6060", fontsize=9)
    return fig

