"""로그 테스트: 한 줄에 필요한 것만 남고, 비밀은 남지 않는다."""

import logging

import pytest

from app import thermo

SECRET_REVIEW = "아주비밀스러운리뷰문장입니다"


@pytest.fixture
def log(caplog):
    """app.access 로그를 INFO 까지 모은다."""
    caplog.set_level(logging.INFO, logger="app.access")
    return caplog


def lines(log):
    return [r.getMessage() for r in log.records if r.name == "app.access"]


def test_one_line_per_request_with_fields(make_client, log):
    # Given: 가짜 AI 클라이언트
    client = make_client(0.8)
    # When: /health 를 한 번 부른다
    client.get("/health")
    # Then: 한 줄이고 request_id, method, path, status, ms, seller_id 가 있다
    [line] = lines(log)
    for key in ("request_id=", "method=GET", "path=/health", "status=200", "ms=", "seller_id=-"):
        assert key in line


def test_response_has_request_id_header(make_client, log):
    # Given/When: 요청 한 번
    r = make_client(0.8).get("/health")
    # Then: 응답 헤더 X-Request-ID 가 로그의 request_id 와 같다
    rid = r.headers["x-request-id"]
    assert f"request_id={rid} " in lines(log)[0]


def test_incoming_request_id_is_reused_only_if_safe(make_client, log):
    # Given: 클라이언트
    client = make_client(0.8)
    # When: 안전한 값과 이상한 값을 보낸다
    ok = client.get("/health", headers={"X-Request-ID": "my-id-123"})
    bad = client.get("/health", headers={"X-Request-ID": "a b;c"})
    # Then: 안전한 값은 그대로, 이상한 값은 새로 만든다
    assert ok.headers["x-request-id"] == "my-id-123"
    assert bad.headers["x-request-id"] != "a b;c" and len(bad.headers["x-request-id"]) == 12


def test_seller_id_is_logged_after_login(make_client, login, log):
    # Given: 로그인한 판매자 A
    client = make_client(0.8)
    a = login(client, "하루상점A")
    log.clear()
    # When: 목록을 읽는다
    client.get("/v1/reviews", headers=a)
    # Then: seller_id=1
    assert "seller_id=1" in lines(log)[0] and "status=200" in lines(log)[0]


def test_401_is_logged_without_seller(make_client, log):
    # Given: 로그인하지 않은 클라이언트
    # When: 목록을 읽는다
    make_client(0.8).get("/v1/reviews")
    # Then: status=401, seller_id=-
    assert "status=401" in lines(log)[0] and "seller_id=-" in lines(log)[0]


def test_logs_never_contain_secrets(make_client, login, log):
    # Given: 비밀번호로 로그인하고 토큰을 얻은 뒤 리뷰를 저장한다
    client = make_client(0.8)
    r = client.post("/v1/login", json={"name": "하루상점A", "password": "haru-a-1234"})
    token = r.json()["token"]
    client.post(
        "/v1/reviews?memo=쿼리비밀",
        json={"text": SECRET_REVIEW, "rating": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post("/v1/reviews/analyze", json={"text": SECRET_REVIEW, "rating": 5})
    # When: 모든 로그 글을 모은다
    everything = log.text
    # Then: 비밀번호, 토큰, 리뷰 글, 쿼리 문자열이 없다
    for secret in ("haru-a-1234", token, token.split(".")[0], SECRET_REVIEW, "쿼리비밀", "test-secret-key"):
        assert secret not in everything


def test_unhandled_error_is_500_with_request_id_and_place(make_client, monkeypatch, log):
    # Given: 계산 중 오류가 나도록 바꿔 둔다 (오류 메시지에는 리뷰 글이 들어 있다)
    def boom(score, text):
        raise ZeroDivisionError(text)

    monkeypatch.setattr(thermo, "calm_score", boom)
    # When: 분석을 요청한다
    r = make_client(0.8).post("/v1/reviews/analyze", json={"text": SECRET_REVIEW, "rating": 5})
    # Then: 500, 응답에 request_id, 로그에 오류 이름과 위치가 있고 메시지(리뷰 글)는 없다
    assert r.status_code == 500
    assert r.json()["request_id"] == r.headers["x-request-id"]
    [line] = lines(log)
    assert "status=500" in line and "error=ZeroDivisionError" in line and "at=test_logging.py:" in line
    assert SECRET_REVIEW not in log.text

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
