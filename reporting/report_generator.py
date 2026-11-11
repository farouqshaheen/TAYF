"""
طيف — TAYF
مولّد ملف القضية الجنائية وتصدير البيانات
"""
import pandas as pd
import datetime

def generate_case_summary_text(df: pd.DataFrame, verdict_info: dict) -> str:
    """
    يولّد وثيقة رسمية بلهجة أمنية جنائية لملف القضية
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    verdict = verdict_info.get("verdict", "غير محدد")
    confidence = verdict_info.get("confidence", 0)

    base = df[df["phase"] == "أساسي"]
    inc = df[df["phase"] == "حادث"]

    lines = [
        "===========================================================",
        "               المملكة الأردنية الهاشمية                    ",
        "         مختبر التحقيق الجنائي الرقمي واللاسلكي             ",
        "             ملف قضية فحص إشارة شبكة طيف                    ",
        "===========================================================",
        f"تاريخ وتوقيت التحقيق: {now_str}",
        "القضية: انقطاع غامض وتدهور بجودة الاتصال اللاسلكي",
        "الموقع المفترض: مكتب د. محمد رسمي موسى — جامعة الزرقاء",
        "-----------------------------------------------------------",
        "البيانات الأولية المرصودة:",
        f"• متوسط قوة الإشارة (قبل الحادث): {base['rssi_dbm'].mean():.2f} dBm",
        f"• متوسط قوة الإشارة (أثناء الحادث): {inc['rssi_dbm'].mean():.2f} dBm (فرق: {inc['rssi_dbm'].mean() - base['rssi_dbm'].mean():.2f} dBm)",
        f"• متوسط نسبة SNR: {base['snr_db'].mean():.2f} dB ➔ {inc['snr_db'].mean():.2f} dB",
        f"• معدل فقدان الحزم: {base['packet_loss_pct'].mean():.1f}% ➔ {inc['packet_loss_pct'].mean():.1f}%",
        "-----------------------------------------------------------",
        "الأدلة الجنائية المكتشفة في مسرح الترددات:",
    ]

    for ev in verdict_info.get("evidence", []):
        lines.append(f"  {ev.get('emoji', '📌')} {ev.get('text', '')} ➔ يشير للمشتبه: {ev.get('supports', '')}")

    lines.extend([
        "-----------------------------------------------------------",
        "قرار المحقق والتقرير النهائي:",
        f"المتهم الأول بإعدام الاتصال: 【 {verdict} 】",
        f"نسبة اليقين والقرائن: {confidence}%",
        "",
        "ترتيب قائمة المشتبه بهم:",
    ])

    for suspect, score in verdict_info.get("ranked", []):
        bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        lines.append(f"• {suspect:<12} : {bar} ({score}%)")

    lines.extend([
        "===========================================================",
        "تنبيه علمي: النتائج مستندة لنماذج انتشار المحاكاة الفيزيائية,",
        "وليست دليلاً على اختراق سيبراني خارجي متعمد بالضرورة.",
        "تم تصدير التقرير بواسطة محرك طيف (TAYF Forensics).",
        "==========================================================="
    ])

    return "\n".join(lines)


def export_dataframe_csv(df: pd.DataFrame) -> str:
    """تصدير السجل الزمني كـ CSV string"""
    return df.to_csv(index=False)

