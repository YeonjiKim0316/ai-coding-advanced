"""로그인과 권한 테스트: 인증(누구인가)과 인가(이 리뷰를 고쳐도 되나)."""

import time

import pytest

from app import auth


# ---- 비밀번호 해시 ----
def test_hash_is_not_plain_and_verifies():
    # Given: 비밀번호 하나
    # When: 해시를 만든다
    stored = auth.hash_password("haru-a-1234")
    # Then: 원문이 들어 있지 않고, 맞는 비밀번호만 통과한다
    assert "haru-a-1234" not in stored and stored.startswith("pbkdf2_sha256$")
    assert auth.verify_password("haru-a-1234", stored) is True
    assert auth.verify_password("틀린 값", stored) is False


@pytest.mark.parametrize("stored", [None, "", "abc", "md5$1$00$00", "pbkdf2_sha256$x$zz$zz"])
def test_verify_rejects_broken_hash(stored):
    # Given: 없거나 깨진 해시
    # When/Then: 어떤 비밀번호도 통과하지 못한다
    assert auth.verify_password("x", stored) is False


def test_default_iterations_are_strong(monkeypatch):
    # Given: 반복 수를 따로 정하지 않았다
    monkeypatch.delenv("PBKDF2_ITERATIONS")
    # When: 해시를 만든다
    stored = auth.hash_password("x")
    # Then: 반복 수가 100000 이상이다
    assert int(stored.split("$")[1]) >= 100_000


# ---- 토큰 ----
def test_token_roundtrip():
    # Given: 판매자 7 의 토큰
    token = auth.make_token(7)
    # When/Then: 읽으면 7
    assert auth.read_token(token) == 7


def test_token_tampered_or_wrong_key_is_rejected(monkeypatch):
    # Given: 판매자 1 의 토큰
    token = auth.make_token(1)
    payload, signature = token.split(".")
    # When/Then: 글을 바꾸거나 서명을 바꾸거나 다른 키로 읽으면 None
    other = auth.make_token(2).split(".")[0]
    assert auth.read_token(f"{other}.{signature}") is None
    assert auth.read_token(f"{payload}.{'0' * len(signature)}") is None
    monkeypatch.setenv("SECRET_KEY", "another-key")
    assert auth.read_token(token) is None


def test_token_expires():
    # Given: 10초짜리 토큰
    now = time.time()
    token = auth.make_token(1, ttl=10, now=now)
    # When/Then: 9초 뒤에는 되고, 10초 뒤에는 안 된다
    assert auth.read_token(token, now=now + 9) == 1
    assert auth.read_token(token, now=now + 10) is None


@pytest.mark.parametrize("token", ["", "abc", "a.b", "a.b.c"])
def test_garbage_token_is_none(token):
    # Given: 모양이 틀린 글
    # When/Then: 오류 없이 None
    assert auth.read_token(token) is None


def test_missing_secret_key_raises(monkeypatch):
    # Given: SECRET_KEY 가 없다
    monkeypatch.delenv("SECRET_KEY")
    # When/Then: 키를 읽으려 하면 RuntimeError (조용히 빈 키로 서명하지 않는다)
    with pytest.raises(RuntimeError):
        auth.get_secret()


# ---- 로그인 ----
def test_login_ok(make_client):
    # Given: 시드 판매자 A
    # When: 맞는 비밀번호로 로그인한다
    r = make_client(0.5).post("/v1/login", json={"name": "하루상점A", "password": "haru-a-1234"})
    # Then: 200 과 토큰, 판매자 번호
    body = r.json()
    assert r.status_code == 200 and body["token_type"] == "bearer"
    assert body["seller_id"] == 1 and auth.read_token(body["token"]) == 1


@pytest.mark.parametrize(
    "name, password", [("하루상점A", "틀림"), ("하루상점A", "haru-b-1234"), ("없는상점", "haru-a-1234")]
)
def test_login_fail_is_401_with_same_message(make_client, name, password):
    # Given: 틀린 비밀번호 또는 없는 판매자
    # When: 로그인한다
    r = make_client(0.5).post("/v1/login", json={"name": name, "password": password})
    # Then: 401 이고 어느 쪽이 틀렸는지 알려 주지 않는다
    assert r.status_code == 401
    assert r.json()["detail"] == "이름 또는 비밀번호가 맞지 않습니다"


def test_login_response_never_has_password_hash(make_client):
    # Given/When: 로그인
    r = make_client(0.5).post("/v1/login", json={"name": "하루상점A", "password": "haru-a-1234"})
    # Then: 응답 글에 해시도 비밀번호도 없다
    assert "pbkdf2" not in r.text and "haru-a-1234" not in r.text


def test_seeded_passwords_are_hashed_in_db(make_client):
    # Given: 시드를 끝낸 DB
    import sqlite3
    import os

    make_client(0.5).post("/v1/login", json={"name": "하루상점A", "password": "haru-a-1234"})
    conn = sqlite3.connect(os.environ["APP_DB_PATH"])
    # When: 저장된 값을 읽는다
    stored = conn.execute("SELECT password_hash FROM sellers WHERE name = ?", ("하루상점A",)).fetchone()[0]
    # Then: 원문이 아니라 pbkdf2 해시다
    assert stored.startswith("pbkdf2_sha256$") and "haru-a-1234" not in stored


# ---- 인증: 토큰이 없거나 틀리면 401 ----
@pytest.mark.parametrize(
    "method, path",
    [("get", "/v1/reviews"), ("post", "/v1/reviews"), ("patch", "/v1/reviews/1"), ("delete", "/v1/reviews/1")],
)
def test_no_token_is_401(make_client, method, path):
    # Given: 로그인하지 않은 클라이언트
    client = make_client(0.5)
    kwargs = {"json": {"text": "좋아요", "rating": 5, "memo": "x"}} if method in ("post", "patch") else {}
    # When: 리뷰 API 를 부른다
    r = getattr(client, method)(path, **kwargs)
    # Then: 401, 다시 로그인하라는 헤더
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("header", ["Bearer garbage", "Bearer a.b", "Basic abc", "Bearer"])
def test_bad_token_is_401(make_client, header):
    # Given: 틀린 Authorization 헤더
    # When: 목록을 부른다
    r = make_client(0.5).get("/v1/reviews", headers={"Authorization": header})
    # Then: 401
    assert r.status_code == 401


def test_token_for_deleted_seller_is_401(make_client):
    # Given: 존재하지 않는 판매자 99 의 (서명은 맞는) 토큰
    token = auth.make_token(99)
    # When: 목록을 부른다
    r = make_client(0.5).get("/v1/reviews", headers={"Authorization": f"Bearer {token}"})
    # Then: 401
    assert r.status_code == 401


# ---- 인가: 남의 리뷰는 403 ----
def test_other_sellers_review_is_403(make_client, login):
    # Given: A 의 리뷰 하나, 로그인한 B
    client = make_client(0.8)
    a, b = login(client, "하루상점A"), login(client, "하루상점B")
    rid = client.post("/v1/reviews", json={"text": "A의 리뷰", "rating": 5}, headers=a).json()["id"]
    # When: A 의 토큰이 아니라 B 의 토큰으로 고치고 지운다
    patch = client.patch(f"/v1/reviews/{rid}", json={"memo": "남이 고침"}, headers=b)
    delete = client.delete(f"/v1/reviews/{rid}", headers=b)
    # Then: 둘 다 403 이고 리뷰는 그대로다
    assert patch.status_code == 403 and delete.status_code == 403
    mine = client.get("/v1/reviews", headers=a).json()["items"]
    assert len(mine) == 1 and mine[0]["memo"] == ""


def test_seller_id_in_body_is_ignored(make_client, login):
    # Given: 로그인한 B
    client = make_client(0.8)
    b = login(client, "하루상점B")
    # When: 본문에 seller_id=1 (A) 을 몰래 넣어 저장한다
    r = client.post("/v1/reviews", json={"text": "좋아요", "rating": 5, "seller_id": 1}, headers=b)
    # Then: 로그인한 B(2)의 리뷰로 저장된다
    assert r.status_code == 201 and r.json()["seller_id"] == 2


def test_analyze_and_logs_stay_public(make_client):
    # Given: 로그인하지 않은 클라이언트
    client = make_client(0.8)
    # When/Then: 분석(저장하지 않음)과 /health 는 로그인 없이 된다
    assert client.post("/v1/reviews/analyze", json={"text": "좋아요", "rating": 5}).status_code == 200
    assert client.get("/health").status_code == 200

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
