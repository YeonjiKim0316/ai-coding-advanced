"""저장된 리뷰 API 테스트 (로그인 없는 단계). 가짜 AI + 임시 DB."""

import pytest


def post_review(client, seller_id=1, text="배송도 빠르고 좋아요", rating=5):
    return client.post("/v1/reviews", json={"seller_id": seller_id, "text": text, "rating": rating})


def test_create_review_analyzes_and_saves(make_client):
    # Given: 점수 0.8 을 돌려주는 가짜 AI
    client = make_client(0.8)
    # When: 판매자 1의 리뷰를 저장한다
    r = post_review(client)
    # Then: 201 과 분석 결과, 빈 메모, 판매자 번호가 돌아온다
    body = r.json()
    assert r.status_code == 201
    assert (body["label"], body["temperature"], body["mismatch"], body["memo"]) == ("positive", 80.0, False, "")
    assert body["seller_id"] == 1 and body["id"] >= 1


def test_create_review_seller_missing(make_client):
    # Given: 없는 판매자 99
    # When: 저장한다
    r = post_review(make_client(0.8), seller_id=99)
    # Then: 404
    assert r.status_code == 404


def test_create_review_validation(make_client):
    # Given: 공백뿐인 글과 별점 6
    client = make_client(0.8)
    # When/Then: 둘 다 422
    assert post_review(client, text="   ").status_code == 422
    assert post_review(client, rating=6).status_code == 422


def test_create_review_ai_down(broken_client):
    # Given: 고장 난 AI
    # When: 저장한다
    r = post_review(broken_client)
    # Then: 503, 저장되지 않는다
    assert r.status_code == 503
    assert broken_client.get("/v1/reviews?seller_id=1").json()["total"] == 0


def test_list_reviews_by_seller_newest_first(make_client):
    # Given: 판매자 1에 두 건, 판매자 2에 한 건
    client = make_client(0.8)
    first = post_review(client, text="첫째").json()["id"]
    second = post_review(client, text="둘째").json()["id"]
    post_review(client, seller_id=2, text="남의 것")
    # When: 판매자 1의 목록을 읽는다
    body = client.get("/v1/reviews?seller_id=1").json()
    # Then: 2건이고 최근 것(둘째)이 먼저다. 판매자 2의 것은 없다
    assert body["total"] == 2
    assert [i["id"] for i in body["items"]] == [second, first]


def test_list_reviews_needs_seller_id_and_pages(make_client):
    # Given: 리뷰 세 건
    client = make_client(0.8)
    for n in range(3):
        post_review(client, text=f"리뷰 {n}")
    # When/Then: seller_id 가 없으면 422, size=2 의 2쪽은 1건
    assert client.get("/v1/reviews").status_code == 422
    body = client.get("/v1/reviews?seller_id=1&page=2&size=2").json()
    assert len(body["items"]) == 1
    assert client.get("/v1/reviews?seller_id=1&page=99999999999999999999").json()["items"] == []


def test_patch_memo(make_client):
    # Given: 저장된 리뷰 하나
    client = make_client(0.8)
    rid = post_review(client).json()["id"]
    # When: 메모를 바꾼다
    r = client.patch(f"/v1/reviews/{rid}", json={"memo": "확인함"})
    # Then: 200 과 새 메모. 목록에서도 같다
    assert r.status_code == 200 and r.json()["memo"] == "확인함"
    assert client.get("/v1/reviews?seller_id=1").json()["items"][0]["memo"] == "확인함"


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_missing_review_is_404(make_client, method):
    # Given: 없는 리뷰 번호
    client = make_client(0.8)
    # When: 고치거나 지운다
    kwargs = {"json": {"memo": "x"}} if method == "patch" else {}
    r = getattr(client, method)("/v1/reviews/999", **kwargs)
    # Then: 404
    assert r.status_code == 404


def test_patch_memo_too_long(make_client):
    # Given: 저장된 리뷰 하나
    client = make_client(0.8)
    rid = post_review(client).json()["id"]
    # When: 201자 메모를 보낸다
    r = client.patch(f"/v1/reviews/{rid}", json={"memo": "가" * 201})
    # Then: 422
    assert r.status_code == 422


def test_delete_review(make_client):
    # Given: 저장된 리뷰 하나
    client = make_client(0.8)
    rid = post_review(client).json()["id"]
    # When: 지운다
    r = client.delete(f"/v1/reviews/{rid}")
    # Then: 204 이고 목록에서 사라진다
    assert r.status_code == 204
    assert client.get("/v1/reviews?seller_id=1").json()["total"] == 0


def test_no_login_needed_in_this_step(make_client):
    # Given: 로그인(토큰) 없이 보낸다
    client = make_client(0.8)
    rid = post_review(client, seller_id=1).json()["id"]
    # When: 판매자 2 자리에서 판매자 1의 리뷰 메모를 고친다
    r = client.patch(f"/v1/reviews/{rid}", json={"memo": "남이 고침"})
    # Then: 막히지 않고 고쳐진다 (이 단계의 알려진 구멍 — 다음 단계에서 막는다)
    assert r.status_code == 200

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
