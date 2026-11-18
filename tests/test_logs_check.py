"""강사 검사 파일: SPEC_LOGS.md(예시 답)대로 목록 API가 만들어졌는지 본다. 진짜 data/sample_logs.db 를 읽는다.

고치지 않습니다. 실행: .venv\\Scripts\\python -m pytest tests/test_logs_check.py -q
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
FIELDS = {"id", "created_at", "rating", "label", "score", "temperature", "mismatch", "text_length"}


def test_first_page_default():
    # Given: 기록 462건이 든 sample_logs.db
    # When: 값 없이 목록을 요청한다
    body = client.get("/v1/logs").json()
    # Then: page 1, size 20, total 462, id 462부터 20줄
    assert (body["page"], body["size"], body["total"]) == (1, 20, 462)
    assert [i["id"] for i in body["items"]] == list(range(462, 442, -1))


def test_page_two_starts_at_442():
    # Given/When: page=2
    body = client.get("/v1/logs?page=2&size=20").json()
    # Then: id 442부터 시작한다
    assert body["items"][0]["id"] == 442


def test_last_page_has_two_rows():
    # Given/When: 462건을 20줄씩 나눈 마지막(24쪽)
    body = client.get("/v1/logs?page=24&size=20").json()
    # Then: 2줄(id 2, 1)
    assert [i["id"] for i in body["items"]] == [2, 1]


def test_page_beyond_is_empty():
    # Given/When: 없는 25쪽
    r = client.get("/v1/logs?page=25&size=20")
    # Then: 200 과 빈 목록
    assert r.status_code == 200 and r.json()["items"] == []


def test_custom_size():
    # Given/When: size=5
    body = client.get("/v1/logs?size=5").json()
    # Then: 5줄이고 size 도 5
    assert len(body["items"]) == 5 and body["size"] == 5


@pytest.mark.parametrize("query", ["page=0", "size=0"])
def test_bad_values_are_422(query):
    # Given/When: 규칙에 맞지 않는 값
    r = client.get(f"/v1/logs?{query}")
    # Then: 422
    assert r.status_code == 422


def test_item_fields():
    # Given/When: 한 줄
    item = client.get("/v1/logs?size=1").json()["items"][0]
    # Then: 정해진 칸만 있고, 리뷰 글은 없고, mismatch 는 true/false
    assert set(item) == FIELDS
    assert isinstance(item["mismatch"], bool)


def test_newest_first_order():
    # Given/When: 첫 페이지
    ids = [i["id"] for i in client.get("/v1/logs?size=50").json()["items"]]
    # Then: id 가 큰 것부터 내려간다
    assert ids == sorted(ids, reverse=True)

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
