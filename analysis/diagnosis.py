"""
طيف — TAYF
محرك الحكم — يرتب المشتبه فيهم بناءً على الأدلة
"""
from analysis.evidence import extract_evidence
import pandas as pd

WEIGHTS = {"strength": [1, 2, 3]}   # strength 1=خفيف, 2=متوسط, 3=قوي


def rank_suspects(df: pd.DataFrame) -> dict:
    """
    يرجع:
      {
        "evidence": [...],
        "scores": {"الغايب": x, "الشبح": y, ...},
        "verdict": "اسم المتهم",
        "confidence": 0-100,
        "runner_up": [(name, score), ...],
      }
    """
    evidence = extract_evidence(df)

    scores = {"الغايب": 0.0, "الشبح": 0.0, "المرتجف": 0.0, "الظل": 0.0}

    for e in evidence:
        suspect = e["supports"]
        if suspect in scores:
            scores[suspect] += e["strength"]

    total = sum(scores.values()) or 1
    pct   = {k: round(v / total * 100) for k, v in scores.items()}

    # ترتيب تنازلي
    ranked = sorted(pct.items(), key=lambda x: x[1], reverse=True)
    verdict = ranked[0][0]

    # درجة الثقة: نسبة المتصدر من المجموع
    confidence = ranked[0][1]

    return {
        "evidence":   evidence,
        "scores":     scores,
        "pct":        pct,
        "ranked":     ranked,
        "verdict":    verdict,
        "confidence": confidence,
    }

