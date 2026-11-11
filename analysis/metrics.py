"""
طيف — TAYF
حساب مؤشرات المقارنة بين الأساسي والحادث
"""
import pandas as pd
import numpy as np


def compute_stats(series: pd.Series) -> dict:
    """إحصاء أساسي لسلسلة رقمية"""
    return {
        "mean":  round(float(series.mean()), 3),
        "std":   round(float(series.std()), 3),
        "min":   round(float(series.min()), 3),
        "max":   round(float(series.max()), 3),
    }


def compare_phases(df: pd.DataFrame) -> dict:
    """
    يقارن الخط الأساسي بفترة الحادث لكل مؤشر
    ويرجع dict بالتغييرات المهمة
    """
    base = df[df["phase"] == "أساسي"]
    inc  = df[df["phase"] == "حادث"]

    indicators = ["rssi_dbm", "snr_db", "packet_loss_pct", "noise_power_dbm"]
    result = {}

    for col in indicators:
        b_mean = base[col].mean()
        i_mean = inc[col].mean()
        delta  = i_mean - b_mean
        result[col] = {
            "baseline_mean":  round(b_mean, 2),
            "incident_mean":  round(i_mean, 2),
            "delta":          round(delta, 2),
            "baseline_std":   round(base[col].std(), 2),
            "incident_std":   round(inc[col].std(), 2),
            "std_ratio":      round(inc[col].std() / max(base[col].std(), 0.01), 2),
        }

    # معدل التغيير في RSSI (هل هو تدريجي أم مفاجئ؟)
    inc_rssi = inc["rssi_dbm"].values
    if len(inc_rssi) > 1:
        steps_x = np.arange(len(inc_rssi))
        slope, intercept = np.polyfit(steps_x, inc_rssi, 1)
        # حساب التذبذب الحقيقي الصافي حول خط الاتجاه (Detrended Residual Std)
        trend_line = slope * steps_x + intercept
        residuals = inc_rssi - trend_line
        net_fluct_std = float(np.std(residuals))
    else:
        slope = 0.0
        net_fluct_std = float(inc["rssi_dbm"].std())

    result["rssi_slope"] = round(float(slope), 4)   # dBm لكل خطوة زمنية
    result["net_fluct_std"] = round(net_fluct_std, 3)
    base_std = float(base["rssi_dbm"].std())
    result["fluct_ratio"] = round(net_fluct_std / max(base_std, 0.01), 2)

    return result

