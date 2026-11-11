"""
طيف — TAYF
الحوادث الأربعة: الغايب، الشبح، المرتجف، الظل
"""
import numpy as np
from dataclasses import dataclass
from typing import Literal

SuspectName = Literal["الغايب", "الشبح", "المرتجف", "الظل", "طبيعي"]

SUSPECTS = {
    "الغايب":   {"en": "path_loss",    "emoji": "🌑", "color": "#555555"},
    "الشبح":    {"en": "interference", "emoji": "👻", "color": "#cc2200"},
    "المرتجف":  {"en": "fast_fading",  "emoji": "⚡", "color": "#ffaa00"},
    "الظل":     {"en": "slow_fading",  "emoji": "🌫️", "color": "#4466aa"},
}


@dataclass
class LinkParams:
    tx_power_dbm: float = 20.0      # قدرة الإرسال
    tx_gain_dbi:  float = 2.0       # كسب هوائي المرسل
    rx_gain_dbi:  float = 2.0       # كسب هوائي المستقبل
    freq_mhz:     float = 2400.0    # التردد (ميغاهرتز)
    dist_km:      float = 0.1       # المسافة (كيلومتر)
    noise_dbm:    float = -95.0     # قدرة الضوضاء الأساسية
    bandwidth_hz: float = 20e6      # عرض النطاق (20 MHz)


def apply_suspect(
    params: LinkParams,
    suspect: SuspectName,
    rng: np.random.Generator,
    step: int,
    total_steps: int,
) -> dict:
    """
    يطبّق تأثير كل مشتبه فيه على معاملات الرابط
    ويرجع dict بالقيم المحسوبة لهذه الخطوة الزمنية.
    """
    from simulation.wireless_link import (
        fspl_db, received_power_dbm, snr_db,
        packet_loss_from_snr
    )

    dist   = params.dist_km
    noise  = params.noise_dbm
    extra  = 0.0           # خسارة إضافية
    fluct  = 0.0           # تذبذب سريع

    t = step / max(total_steps - 1, 1)   # 0..1 يمثل تقدم الحادث

    if suspect == "الغايب":
        # في مسألة ابتعاد المستقبل (Path loss)، غالباً ما يكون هناك انتقال إلى موقع أبعد أو زيادة حادة في المسافة
        # بعد الخط الأساسي، يبتعد المستقبل مباشرة ويبقى بعيداً مع حركة خفيفة
        dist = params.dist_km * (3.5 + 0.5 * t)

    elif suspect == "الشبح":
        # حقن ضوضاء وتداخل تشويش فوري ومتصاعد
        noise = params.noise_dbm + 12.0 + t * 15.0

    elif suspect == "المرتجف":
        # تذبذبات سريعة عشوائية حول المتوسط (Rayleigh / multipath fast fading)
        fluct = rng.normal(0, 6.0)

    elif suspect == "الظل":
        # عائق يمر ببطء تدريجي (Slow fading / shadowing)
        extra = t * 20.0

    # احسب FSPL
    pl = fspl_db(params.freq_mhz, dist)

    # الإشارة المستقبَلة
    rx = received_power_dbm(
        params.tx_power_dbm,
        params.tx_gain_dbi,
        params.rx_gain_dbi,
        pl,
        extra,
    ) + fluct + rng.normal(0, 0.5)   # ضوضاء خلفية خفيفة دايماً

    # SNR
    snr = snr_db(rx, noise)

    # فقدان الحزم
    pl_pct = packet_loss_from_snr(snr)

    return {
        "distance_km":          round(dist, 4),
        "tx_power_dbm":         params.tx_power_dbm,
        "path_loss_db":         round(pl, 2),
        "extra_loss_db":        round(extra, 2),
        "rx_power_dbm":         round(rx, 2),
        "noise_power_dbm":      round(noise, 2),
        "snr_db":               round(snr, 2),
        "rssi_dbm":             round(rx, 2),
        "packet_loss_pct":      round(pl_pct, 2),
    }

