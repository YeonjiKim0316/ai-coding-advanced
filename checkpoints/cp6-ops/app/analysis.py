"""리뷰 한 건을 분석하는 흐름 (analyze API와 이후 저장 API가 함께 씁니다).

글 -> AI 점수(predict) -> 이모지 보정(thermo.calm_score) -> 규칙(thermo) -> 결과
"""

from collections.abc import Callable

from fastapi import HTTPException

from app import thermo

Predict = Callable[[list[str]], list[float]]


def get_score(predict: Predict, text: str) -> float:
    """AI 부품에게 점수를 받는다. 실패하면 503."""
    try:
        return predict([text])[0]
    except Exception as exc:
        raise HTTPException(status_code=503, detail="AI 부품이 응답하지 않습니다") from exc


def analyze_text(predict: Predict, text: str, rating: int) -> dict:
    """리뷰 글과 별점 -> {"label", "score", "temperature", "mismatch"}."""
    score = round(thermo.calm_score(get_score(predict, text), text), 4)
    label = thermo.to_label(score)  # 규칙은 app/thermo.py
    return {
        "label": label,
        "score": score,
        "temperature": thermo.to_temperature(score),
        "mismatch": thermo.is_mismatch(rating, label),
    }

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
