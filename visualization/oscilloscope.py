"""
طيف — TAYF
نبضة القلب — راسم الذبذبات الحي
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

COLORS = {
    "أساسي":   "#00e676",   # أخضر حي
    "حادث":    "#ff1744",   # أحمر كارثة
    "snr":     "#ffea00",   # أصفر
    "bg":      "#0a0a0a",
    "grid":    "#1a1a2e",
    "text":    "#e0e0e0",
}

BASELINE_LINE = 20   # عدد خطوات الأساسي


def plot_heartbeat(df: pd.DataFrame) -> plt.Figure:
    """
    مخطط نبضة القلب المزدوج — RSSI + SNR
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 5), sharex=True,
                                   facecolor=COLORS["bg"])
    fig.subplots_adjust(hspace=0.08)

    for ax in (ax1, ax2):
        ax.set_facecolor(COLORS["bg"])
        ax.tick_params(colors=COLORS["text"])
        ax.spines[:].set_color(COLORS["grid"])
        ax.grid(color=COLORS["grid"], linewidth=0.6)

    t = df["timestamp_s"].values

    # --- RSSI ---
    base_mask  = df["phase"] == "أساسي"
    inc_mask   = df["phase"] == "حادث"
    rssi       = df["rssi_dbm"].values

    ax1.plot(t[base_mask], rssi[base_mask], color=COLORS["أساسي"],
             linewidth=1.8, label="أساسي")
    ax1.plot(t[inc_mask],  rssi[inc_mask],  color=COLORS["حادث"],
             linewidth=1.8, label="حادث")
    ax1.axvline(BASELINE_LINE, color="#ffffff", linestyle="--",
                linewidth=1, alpha=0.5)
    ax1.set_ylabel("RSSI (dBm)", color=COLORS["text"], fontsize=10)
    ax1.legend(facecolor="#111", labelcolor=COLORS["text"], fontsize=8)
    ax1.text(BASELINE_LINE + 0.5, rssi.max() - 1,
             "⚡ بدأ الحادث", color="#ffffff", fontsize=8, alpha=0.8)

    # --- SNR ---
    snr = df["snr_db"].values
    ax2.plot(t[base_mask], snr[base_mask], color=COLORS["snr"], linewidth=1.8)
    ax2.plot(t[inc_mask],  snr[inc_mask],  color=COLORS["حادث"],  linewidth=1.8)
    ax2.axvline(BASELINE_LINE, color="#ffffff", linestyle="--",
                linewidth=1, alpha=0.5)
    ax2.axhline(10, color="#ff6d00", linestyle=":", linewidth=1, alpha=0.7,
                label="عتبة الجودة (10 dB)")
    ax2.set_ylabel("SNR (dB)", color=COLORS["text"], fontsize=10)
    ax2.set_xlabel("الوقت (ثانية)", color=COLORS["text"], fontsize=10)
    ax2.legend(facecolor="#111", labelcolor=COLORS["text"], fontsize=8)

    fig.suptitle("📡 نبضة القلب — راسم الذبذبات",
                 color=COLORS["text"], fontsize=13, fontweight="bold")
    return fig

