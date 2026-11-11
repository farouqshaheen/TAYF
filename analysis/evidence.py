"""
طيف — TAYF
استخراج الأدلة من المقارنة وتحويلها لجمل مفهومة
"""
from analysis.metrics import compare_phases
import pandas as pd


def extract_evidence(df: pd.DataFrame) -> list[dict]:
    """
    يرجع قائمة أدلة، كل دليل:
      { "text": نص الدليل, "supports": المشتبه فيه, "strength": 0-3 }
    """
    stats = compare_phases(df)
    evidence = []

    rssi_delta    = stats["rssi_dbm"]["delta"]
    snr_delta     = stats["snr_db"]["delta"]
    snr_inc_mean  = stats["snr_db"]["incident_mean"]
    fluct_r       = stats["fluct_ratio"]
    pl_pct_delta  = stats["packet_loss_pct"]["delta"]
    noise_delta   = stats["noise_power_dbm"]["delta"]
    slope         = stats["rssi_slope"]

    # --- دليل 1: انخفاض تدريجي مستمر (الظل - Slow Fading / Shadowing) ---
    if slope < -0.2:
        strength = 3 if slope < -0.4 else 2
        evidence.append({
            "text":     f"الإشارة تتلاشى تدريجياً وببطء ({slope:.2f} dBm/ثانية)",
            "supports": "الظل",
            "strength": strength,
            "emoji":    "🌫️",
        })

    # --- دليل 2: انخفاض في متوسط الإشارة الكلي ---
    if rssi_delta < -6:
        # إذا كان هناك انحدار تدريجي واضح فهو الظل، وإلا فهو انتقال مفاجئ أو مسافة (الغايب)
        if slope >= -0.2:
            strength = 3 if rssi_delta < -12 else 2
            evidence.append({
                "text":     f"متوسط الإشارة انخفض بشدة بمقدار {abs(rssi_delta):.1f} dBm",
                "supports": "الغايب",
                "strength": strength,
                "emoji":    "🌑",
            })
    elif rssi_delta < -2 and slope >= -0.2:
        evidence.append({
            "text":     f"الإشارة انخفضت قليلاً ({abs(rssi_delta):.1f} dBm)",
            "supports": "الغايب",
            "strength": 1,
            "emoji":    "🌑",
        })

    # --- دليل 3: وقوع SNR مع ثبات الإشارة (الشبح - Interference) ---
    if snr_delta < -5 and abs(rssi_delta) < 4:
        strength = 3 if snr_delta < -10 else 2
        evidence.append({
            "text":     f"انهيار في SNR بمقدار {abs(snr_delta):.1f} dB مع بقاء الإشارة الأصلية قوية",
            "supports": "الشبح",
            "strength": strength,
            "emoji":    "👻",
        })

    # --- دليل 4: ضوضاء ارتفعت بشكل غير معتاد ---
    if noise_delta > 6:
        evidence.append({
            "text":     f"مستوى ضوضاء القناة ارتفع بمقدار {noise_delta:.1f} dB",
            "supports": "الشبح",
            "strength": 2,
            "emoji":    "👻",
        })

    # --- دليل 5: تذبذب سريع وارتجاف صريح (المرتجف - Fast Fading) ---
    # استخدام التذبذب الصافي حول المسار
    if fluct_r > 3.0:
        strength = 3 if fluct_r > 5.0 else 2
        evidence.append({
            "text":     f"الإشارة ترتجف بعنف — التذبذب اللحظي ارتفع ×{fluct_r:.1f}",
            "supports": "المرتجف",
            "strength": strength,
            "emoji":    "⚡",
        })

    # --- دليل 6: فقدان الحزم ارتفع ---
    if pl_pct_delta > 10:
        strength = 2 if pl_pct_delta > 25 else 1
        evidence.append({
            "text":     f"معدل فقدان الحزم ارتفع {pl_pct_delta:.1f}%",
            "supports":  "الشبح" if abs(rssi_delta) < 4 else "الغايب",
            "strength": strength,
            "emoji":    "📦",
        })

    if not evidence:
        evidence.append({
            "text":     "لا توجد أدلة على حادث — الرابط طبيعي",
            "supports": "طبيعي",
            "strength": 0,
            "emoji":    "✅",
        })

    return evidence

