"""리뷰 온도 규칙 3개 (SPEC.md 2장)와 이모지 보정 한 개."""

import unicodedata


def to_label(score: float) -> str:
    """score가 0.5 이상이면 "positive", 아니면 "negative"."""
    return "positive" if score >= 0.5 else "negative"


def to_temperature(score: float) -> float:
    """score x 100 을 소수점 첫째 자리까지 반올림."""
    return round(score * 100, 1)


def is_mismatch(rating: int, label: str) -> bool:
    """별점 4~5인데 negative, 또는 별점 1~2인데 positive이면 True. 별점 3은 항상 False."""
    return (rating >= 4 and label == "negative") or (rating <= 2 and label == "positive")


def _is_emoji(ch: str) -> bool:
    """그림 글자(이모지)인지 본다."""
    return ord(ch) >= 0x1F000 or unicodedata.category(ch) == "So"


def calm_score(score: float, text: str) -> float:
    """이모지가 글자보다 많은 리뷰는 AI가 잘 읽지 못한다. 점수를 중립(0.5) 쪽으로 절반 당긴다.

    글자(한글·영문·숫자) 수 대비 이모지 수가 2 이상이면 보정한다. 아니면 그대로 둔다.
    """
    letters = sum(1 for ch in text if ch.isalnum())
    emojis = sum(1 for ch in text if _is_emoji(ch))
    ratio = emojis / letters
    if ratio >= 2:
        return round(0.5 + (score - 0.5) / 2, 4)
    return score


# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
