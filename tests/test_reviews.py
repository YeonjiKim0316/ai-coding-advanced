"""저장된 리뷰 API 테스트 (로그인 필요). 가짜 AI + 임시 DB."""

import pytest


def post_review(client, headers, text="배송도 빠르고 좋아요", rating=5):
    return client.post("/v1/reviews", json={"text": text, "rating": rating}, headers=headers)


def test_create_review_analyzes_and_saves(make_client, login):
    # Given: 점수 0.8 을 돌려주는 가짜 AI, 로그인한 판매자 A
    client = make_client(0.8)
    a = login(client, "하루상점A")
    # When: 리뷰를 저장한다
    r = post_review(client, a)
    # Then: 201, 분석 결과, 빈 메모, 판매자 A(1)의 것
    body = r.json()
    assert r.status_code == 201
    assert (body["label"], body["temperature"], body["mismatch"], body["memo"]) == ("positive", 80.0, False, "")
    assert body["seller_id"] == 1


def test_create_review_validation(make_client, login):
    # Given: 로그인한 판매자
    client = make_client(0.8)
    a = login(client)
    # When/Then: 공백뿐인 글과 별점 6은 422
    assert post_review(client, a, text="   ").status_code == 422
    assert post_review(client, a, rating=6).status_code == 422


def test_create_review_ai_down(broken_client, login):
    # Given: 고장 난 AI
    a = login(broken_client)
    # When: 저장한다
    r = post_review(broken_client, a)
    # Then: 503, 저장되지 않는다
    assert r.status_code == 503
    assert broken_client.get("/v1/reviews", headers=a).json()["total"] == 0


def test_list_shows_only_my_reviews_newest_first(make_client, login):
    # Given: A 에 두 건, B 에 한 건
    client = make_client(0.8)
    a, b = login(client, "하루상점A"), login(client, "하루상점B")
    first = post_review(client, a, text="첫째").json()["id"]
    second = post_review(client, a, text="둘째").json()["id"]
    post_review(client, b, text="B의 것")
    # When: A 의 목록을 읽는다
    body = client.get("/v1/reviews", headers=a).json()
    # Then: 2건이고 최근 것(둘째)이 먼저다. B 의 것은 없다
    assert body["total"] == 2
    assert [i["id"] for i in body["items"]] == [second, first]


def test_list_pages(make_client, login):
    # Given: 리뷰 세 건
    client = make_client(0.8)
    a = login(client)
    for n in range(3):
        post_review(client, a, text=f"리뷰 {n}")
    # When/Then: size=2 의 2쪽은 1건, 아주 큰 쪽은 빈 목록
    assert len(client.get("/v1/reviews?page=2&size=2", headers=a).json()["items"]) == 1
    assert client.get("/v1/reviews?page=99999999999999999999", headers=a).json()["items"] == []


def test_patch_memo(make_client, login):
    # Given: A 의 리뷰 하나
    client = make_client(0.8)
    a = login(client)
    rid = post_review(client, a).json()["id"]
    # When: 메모를 바꾼다
    r = client.patch(f"/v1/reviews/{rid}", json={"memo": "확인함"}, headers=a)
    # Then: 200 과 새 메모. 목록에서도 같다
    assert r.status_code == 200 and r.json()["memo"] == "확인함"
    assert client.get("/v1/reviews", headers=a).json()["items"][0]["memo"] == "확인함"


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_missing_review_is_404(make_client, login, method):
    # Given: 없는 리뷰 번호
    client = make_client(0.8)
    a = login(client)
    # When: 고치거나 지운다
    kwargs = {"json": {"memo": "x"}} if method == "patch" else {}
    r = getattr(client, method)("/v1/reviews/999", headers=a, **kwargs)
    # Then: 404
    assert r.status_code == 404


def test_patch_memo_too_long(make_client, login):
    # Given: A 의 리뷰 하나
    client = make_client(0.8)
    a = login(client)
    rid = post_review(client, a).json()["id"]
    # When: 201자 메모를 보낸다
    r = client.patch(f"/v1/reviews/{rid}", json={"memo": "가" * 201}, headers=a)
    # Then: 422
    assert r.status_code == 422


def test_delete_review(make_client, login):
    # Given: A 의 리뷰 하나
    client = make_client(0.8)
    a = login(client)
    rid = post_review(client, a).json()["id"]
    # When: 지운다
    r = client.delete(f"/v1/reviews/{rid}", headers=a)
    # Then: 204 이고 목록에서 사라진다
    assert r.status_code == 204
    assert client.get("/v1/reviews", headers=a).json()["total"] == 0


# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
