"""Short Arabic dialogue lines and matching audio assets for TAYF's mentor."""

WELCOME_LINE = "أهلاً بك في مختبر طيف.. افحص تدهور القناة واكتشف مين اللي شوش على اجتماعي اليوم!"
CASE_001_LINE = "كنت عم بحاضر وفجأة الإشارة انهارت.. بدي تقرير كامل على مكتبي مين المشتبه فيه!"

VERDICT_AUDIO = {
    "الشبح": "verdict_ghost.wav",
    "الغايب": "verdict_absent.wav",
    "المرتجف": "verdict_shaky.wav",
    "الظل": "verdict_shadow.wav",
}


def doctor_dialogue(mode: str, verdict: str = "") -> str:
    """Return the mentor's welcome, case briefing, or evidence-board reaction."""
    if mode == "case_001":
        return CASE_001_LINE
    if mode == "verdict":
        suspect = str(verdict).strip() or "المشتبه به"
        return f"أحسنت يا محقق! الأدلة الرياضية لا تكذب.. المتهم هو فعلاً «{suspect}»!"
    return WELCOME_LINE


def doctor_audio_filename(mode: str, verdict: str = "") -> str:
    """Return a bundled voice clip matching the currently displayed dialogue."""
    if mode == "case_001":
        return "case_001.wav"
    if mode == "verdict":
        return VERDICT_AUDIO.get(str(verdict).strip(), "verdict_ghost.wav")
    return "welcome.wav"
