"""Deterministic educational guidance for the TAYF lab mentor."""


def mentor_guidance(
    phase: str,
    rssi_delta: float,
    snr_delta: float,
    rssi_std_ratio: float,
    hint_level: int = 0,
) -> str:
    """Return a short, evidence-based Arabic prompt without revealing a verdict."""
    level = max(0, min(2, int(hint_level)))

    if phase != "حادث":
        prompts = [
            "خلّينا نثبت خط الأساس أولاً: سجّل RSSI وSNR قبل الحادث، ثم حرّك المؤشر إلى بداية التغيّر وقارن القراءات.",
            "تلميح: لا تعتمد على قراءة واحدة. متوسط المرحلة الأساسية هو مرجعنا لمعرفة ما الذي تغيّر فعلاً.",
            "الخطوة التالية: تقدّم بالمؤشر حتى بداية الحادث، ثم قارن فرق RSSI وSNR في لوحة الحالة.",
        ]
        return prompts[level]

    if abs(rssi_delta) < 3.0 and snr_delta <= -5.0:
        observation = (
            f"SNR انخفض {abs(snr_delta):.1f} dB بينما بقي RSSI قريباً من مستواه "
            f"(التغيّر {rssi_delta:+.1f} dB). قارن بين قوة الإشارة وجودة الرابط قبل أن تستنتج السبب."
        )
    elif rssi_delta <= -6.0:
        observation = (
            f"RSSI انخفض {abs(rssi_delta):.1f} dB في المتوسط. افحص تغيّر القدرة المستقبلة "
            "وقارنه بخريطة التغطية، ثم لاحظ أثره على SNR."
        )
    elif rssi_std_ratio >= 1.8:
        observation = (
            f"تشتّت RSSI صار أكبر بنحو {rssi_std_ratio:.1f} مرة من خط الأساس. "
            "راقب شكل التذبذب عبر الزمن بدلاً من التركيز على متوسط واحد."
        )
    else:
        observation = (
            f"التغيّر المتوسط هو {rssi_delta:+.1f} dB في RSSI و{snr_delta:+.1f} dB في SNR. "
            "قارن المقياسين قبل الانتقال إلى تفسير السبب."
        )

    prompts = [
        observation,
        "تلميح: افتح خريطة التغطية وبدّل بين RSSI وSNR. اسأل نفسك: هل تغيّرت القدرة المستقبلة، أم تدهورت جودة الرابط فقط؟",
        "الخطوة التالية: افحص كوكبة QPSK ومنحنى BER، ثم اربط تدهور الجودة بالتغيّر الذي رأيته في RSSI وSNR.",
    ]
    return prompts[level]
