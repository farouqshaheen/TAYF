"""
طيف — TAYF
مولّد السلاسل الزمنية — قبل الحادث وبعده
"""
import numpy as np
import pandas as pd
from simulation.scenarios import LinkParams, SuspectName, apply_suspect
from simulation.wireless_link import fspl_db, received_power_dbm, snr_db, packet_loss_from_snr


BASELINE_STEPS = 20
INCIDENT_STEPS = 30


def generate_baseline(params: LinkParams, rng: np.random.Generator) -> list[dict]:
    """يولّد فترة الخط الأساسي الطبيعي"""
    rows = []
    pl = fspl_db(params.freq_mhz, params.dist_km)
    for i in range(BASELINE_STEPS):
        fluct = rng.normal(0, 0.8)
        rx = received_power_dbm(
            params.tx_power_dbm, params.tx_gain_dbi,
            params.rx_gain_dbi, pl
        ) + fluct
        noise = params.noise_dbm + rng.normal(0, 0.3)
        snr = snr_db(rx, noise)
        rows.append({
            "step":            i,
            "phase":           "أساسي",
            "suspect":         "طبيعي",
            "distance_km":     params.dist_km,
            "tx_power_dbm":    params.tx_power_dbm,
            "path_loss_db":    round(pl, 2),
            "extra_loss_db":   0.0,
            "rx_power_dbm":    round(rx, 2),
            "noise_power_dbm": round(noise, 2),
            "snr_db":          round(snr, 2),
            "rssi_dbm":        round(rx, 2),
            "packet_loss_pct": round(packet_loss_from_snr(snr), 2),
        })
    return rows


def generate_incident(
    params: LinkParams,
    suspect: SuspectName,
    rng: np.random.Generator,
    severity: float = 1.0,
) -> list[dict]:
    """يولّد فترة الحادث"""
    rows = []
    for i in range(INCIDENT_STEPS):
        data = apply_suspect(params, suspect, rng, i, INCIDENT_STEPS, severity=severity)
        data.update({
            "step":    BASELINE_STEPS + i,
            "phase":   "حادث",
            "suspect": suspect,
        })
        rows.append(data)
    return rows


def run_simulation(
    suspect: SuspectName,
    params: LinkParams | None = None,
    seed: int = 42,
    severity: float = 1.0,
) -> pd.DataFrame:
    """
    يشغّل المحاكاة الكاملة ويرجع DataFrame
    suspect: "الغايب" | "الشبح" | "المرتجف" | "الظل"
    """
    if params is None:
        params = LinkParams()
    rng = np.random.default_rng(seed)

    baseline = generate_baseline(params, rng)
    incident = generate_incident(params, suspect, rng, severity=severity)

    df = pd.DataFrame(baseline + incident)
    df["timestamp_s"] = df["step"]   # ثانية واحدة لكل خطوة
    return df
