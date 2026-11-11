from pathlib import Path
import wave

from analysis.doctor_dialogue import (
    CASE_001_LINE,
    VERDICT_AUDIO,
    WELCOME_LINE,
    doctor_audio_filename,
    doctor_dialogue,
)

AUDIO_DIR = Path(__file__).resolve().parents[1] / "static" / "doctor_character" / "assets" / "audio"


def test_welcome_dialogue_is_default():
    assert doctor_dialogue("welcome") == WELCOME_LINE
    assert doctor_dialogue("unknown-mode") == WELCOME_LINE
    assert doctor_audio_filename("welcome") == "welcome.wav"


def test_case_briefing_matches_case_001_line():
    assert doctor_dialogue("case_001") == CASE_001_LINE
    assert "انهارت" in doctor_dialogue("case_001")
    assert doctor_audio_filename("case_001") == "case_001.wav"


def test_verdict_dialogue_and_audio_use_the_current_suspect():
    message = doctor_dialogue("verdict", "الشبح")
    assert "الأدلة الرياضية لا تكذب" in message
    assert "«الشبح»" in message
    assert doctor_audio_filename("verdict", "الشبح") == "verdict_ghost.wav"


def test_all_verdict_audio_variants_are_distinct():
    names = {
        doctor_audio_filename("verdict", suspect)
        for suspect in ("الشبح", "الغايب", "المرتجف", "الظل")
    }
    assert len(names) == 4


def test_empty_verdict_has_safe_fallback():
    assert "المشتبه به" in doctor_dialogue("verdict")
    assert doctor_audio_filename("verdict") == "verdict_ghost.wav"


def test_all_generated_voice_files_are_bundled_and_readable():
    filenames = {"welcome.wav", "case_001.wav", *VERDICT_AUDIO.values()}
    for filename in filenames:
        path = AUDIO_DIR / filename
        assert path.is_file()
        with wave.open(str(path), "rb") as audio:
            assert audio.getnframes() > 0
            assert audio.getnchannels() == 1
            assert audio.getsampwidth() == 2
            assert audio.getframerate() == 24_000
