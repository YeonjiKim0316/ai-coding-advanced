"""심어 둔 오류의 재현·고침 테스트: 글자가 하나도 없는 리뷰(이모지만, 기호만)에서 500 이 났다.

원인: thermo.calm_score 가 이모지 수를 글자 수로 나누는데, 글자 수가 0이면 나누기 오류(ZeroDivisionError).
"""

import pytest

from app import thermo


@pytest.mark.parametrize("text", ["😀😀😀", "👍", "...", "!!!", "😀 ... 😀"])
def test_no_letters_does_not_crash(make_client, text):
    # Given: 글자(한글·영문·숫자)가 하나도 없는 리뷰, 점수 0.8 을 주는 가짜 AI
    client = make_client(0.8)
    # When: 분석을 요청한다
    r = client.post("/v1/reviews/analyze", json={"text": text, "rating": 5})
    # Then: 500 이 아니라 200 이다
    assert r.status_code == 200


def test_emoji_only_is_pulled_to_neutral(make_client):
    # Given: 이모지만 있는 리뷰 (글자 0, 이모지 3), 가짜 AI 점수 0.8
    # When: 분석한다
    body = make_client(0.8).post("/v1/reviews/analyze", json={"text": "😀😀😀", "rating": 5}).json()
    # Then: 점수가 중립(0.5) 쪽으로 절반 당겨진다: 0.5 + (0.8 - 0.5) / 2 = 0.65
    assert body["score"] == 0.65 and body["temperature"] == 65.0


def test_symbols_only_is_left_alone(make_client):
    # Given: 기호만 있는 리뷰 (이모지 0)
    # When: 분석한다
    body = make_client(0.8).post("/v1/reviews/analyze", json={"text": "...", "rating": 5}).json()
    # Then: 점수는 그대로 0.8
    assert body["score"] == 0.8


def test_emoji_only_review_can_be_saved(make_client, login):
    # Given: 로그인한 판매자
    client = make_client(0.8)
    a = login(client)
    # When: 이모지만 있는 리뷰를 저장한다
    r = client.post("/v1/reviews", json={"text": "👍👍", "rating": 4}, headers=a)
    # Then: 201
    assert r.status_code == 201


@pytest.mark.parametrize(
    "text, expected",
    [
        ("좋아요", 0.8),  # 이모지 0
        ("좋아 😀😀😀", 0.8),  # 글자 2, 이모지 3: 비율 1.5 (보정 안 함)
        ("좋아 😀😀😀😀", 0.65),  # 글자 2, 이모지 4: 비율 2.0 (보정)
        ("😀", 0.65),  # 글자 0
        ("", 0.8),  # 빈 글
    ],
)
def test_calm_score_boundary(text, expected):
    # Given: 점수 0.8 과 글
    # When: 보정한다
    result = thermo.calm_score(0.8, text)
    # Then: 비율 2 이상일 때만 중립 쪽으로 당긴다
    assert result == expected

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
