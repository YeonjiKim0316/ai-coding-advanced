"""분석 기록 목록 API 테스트 (verification-plan.md 기준). 임시 DB를 쓴다."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.deps import get_logs_db
from app.main import app

ROWS = 45  # 임시 DB의 줄 수


@pytest.fixture
def logs_client(tmp_path):
    """임시 DB(45줄, id 1~45)를 읽는 클라이언트. 진짜 sample_logs.db 는 쓰지 않는다."""
    db = tmp_path / "logs.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE analysis_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,"
        " rating INTEGER NOT NULL, text_length INTEGER NOT NULL, label TEXT NOT NULL,"
        " score REAL NOT NULL, temperature INTEGER NOT NULL, mismatch INTEGER NOT NULL,"
        " review_text TEXT NOT NULL)"
    )
    for i in range(1, ROWS + 1):
        conn.execute(
            "INSERT INTO analysis_logs (created_at, rating, text_length, label, score, temperature,"
            " mismatch, review_text) VALUES (?, 5, 10, 'positive', 0.9, 90, 0, ?)",
            (f"2026-10-12T08:00:{i:02d}", f"비밀 리뷰 {i}"),
        )
    conn.commit()
    conn.close()
    app.dependency_overrides[get_logs_db] = lambda: str(db)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_default_first_page(logs_client):
    # Given: 45줄이 들어 있는 DB
    # When: 아무 값 없이 목록을 요청한다
    r = logs_client.get("/v1/logs")
    # Then: page 1, size 20, total 45, id 45부터 내려가는 20줄이다
    body = r.json()
    assert r.status_code == 200
    assert (body["page"], body["size"], body["total"]) == (1, 20, ROWS)
    assert [i["id"] for i in body["items"]] == list(range(45, 25, -1))


def test_second_page_continues(logs_client):
    # Given: 45줄이 들어 있는 DB
    # When: page=2, size=20 을 요청한다
    body = logs_client.get("/v1/logs?page=2&size=20").json()
    # Then: id 25부터 6까지 이어진다
    assert [i["id"] for i in body["items"]] == list(range(25, 5, -1))


def test_last_page_is_short(logs_client):
    # Given: 45줄 / 20줄씩 = 3쪽
    # When: 3쪽을 요청한다
    body = logs_client.get("/v1/logs?page=3&size=20").json()
    # Then: 5줄만 있다
    assert [i["id"] for i in body["items"]] == [5, 4, 3, 2, 1]


def test_page_out_of_range_is_empty(logs_client):
    # Given: 3쪽까지만 있는 DB
    # When: 4쪽과 아주 큰 쪽을 요청한다
    r4 = logs_client.get("/v1/logs?page=4&size=20")
    huge = logs_client.get("/v1/logs?page=99999999999999999999&size=20")
    # Then: 200과 빈 목록이다 (total 은 그대로)
    assert r4.status_code == 200 and r4.json()["items"] == []
    assert huge.status_code == 200 and huge.json()["items"] == []
    assert r4.json()["total"] == ROWS


@pytest.mark.parametrize("query", ["page=0", "size=0", "page=-1", "size=abc", "size=101", "order=random"])
def test_bad_query_is_422(logs_client, query):
    # Given: 규칙에 맞지 않는 page 또는 size
    # When: 목록을 요청한다
    r = logs_client.get(f"/v1/logs?{query}")
    # Then: 422 이다
    assert r.status_code == 422


def test_item_shape_has_no_review_text(logs_client):
    # Given: 리뷰 글이 들어 있는 DB
    # When: 한 줄을 꺼낸다
    item = logs_client.get("/v1/logs?size=1").json()["items"][0]
    # Then: 여덟 칸이고 리뷰 글은 없고 mismatch 는 true/false 이다
    assert set(item) == {"id", "created_at", "rating", "label", "score", "temperature", "mismatch", "text_length"}
    assert item["mismatch"] is False
    assert "review_text" not in item


def test_read_only_no_write_method(logs_client):
    # Given: 목록 주소
    # When: POST 로 보낸다
    r = logs_client.post("/v1/logs", json={})
    # Then: 405 (쓰기 길이 없다)
    assert r.status_code == 405

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)


def test_size_limit_is_100(logs_client):
    # Given: 45줄이 들어 있는 DB
    # When: size=100(상한)과 size=101(상한 초과)을 요청한다
    ok = logs_client.get("/v1/logs?size=100")
    over = logs_client.get("/v1/logs?size=101")
    # Then: 100은 200 이고 45줄 전부, 101은 422 이다
    assert ok.status_code == 200 and len(ok.json()["items"]) == ROWS
    assert over.status_code == 422


def test_order_oldest_first(logs_client):
    # Given: 45줄이 들어 있는 DB
    # When: order=oldest 로 요청한다
    body = logs_client.get("/v1/logs?order=oldest&size=5").json()
    # Then: id 1부터 올라간다
    assert [i["id"] for i in body["items"]] == [1, 2, 3, 4, 5]


def test_order_newest_is_default_and_pages_follow_order(logs_client):
    # Given: 45줄이 들어 있는 DB
    # When: order=newest 와 order=oldest 의 2쪽을 요청한다
    newest = logs_client.get("/v1/logs?order=newest&page=2&size=20").json()
    oldest = logs_client.get("/v1/logs?order=oldest&page=2&size=20").json()
    # Then: newest 2쪽은 id 25부터 내려가고, oldest 2쪽은 id 21부터 올라간다
    assert newest["items"][0]["id"] == 25
    assert oldest["items"][0]["id"] == 21
