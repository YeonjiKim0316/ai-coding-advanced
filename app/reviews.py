"""저장된 리뷰 API: 분석 후 저장, 목록, 메모 바꾸기, 삭제.

모든 주소는 로그인(Bearer 토큰)이 필요하다(없으면 401). 남의 리뷰를 고치거나 지우면 403.
"""

import sqlite3
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app import analysis
from app.analysis import Predict
from app.deps import current_seller, get_db, get_predict
from app.schemas import MemoUpdate, ReviewCreate, ReviewOut, ReviewPage

router = APIRouter()

COLUMNS = "id, seller_id, text, rating, label, score, temperature, mismatch, memo, created_at"


def to_review(row: sqlite3.Row) -> dict:
    """DB 한 줄 -> 응답 모양 (mismatch 는 true/false)."""
    return dict(row) | {"mismatch": bool(row["mismatch"])}


def get_review_row(conn: sqlite3.Connection, review_id: int) -> sqlite3.Row:
    """리뷰 한 줄을 읽는다. 없으면 404."""
    row = conn.execute(f"SELECT {COLUMNS} FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    return row


def get_own_review_row(conn: sqlite3.Connection, review_id: int, seller: sqlite3.Row) -> sqlite3.Row:
    """내 리뷰 한 줄을 읽는다. 없으면 404, 남의 것이면 403."""
    row = get_review_row(conn, review_id)
    if row["seller_id"] != seller["id"]:
        raise HTTPException(status_code=403, detail="다른 판매자의 리뷰입니다")
    return row


@router.post("/v1/reviews", response_model=ReviewOut, status_code=201)
def create_review(
    req: ReviewCreate,
    seller: sqlite3.Row = Depends(current_seller),
    conn: sqlite3.Connection = Depends(get_db),
    predict: Predict = Depends(get_predict),
) -> dict:
    """로그인한 판매자의 리뷰를 분석한 뒤 저장한다."""
    result = analysis.analyze_text(predict, req.text, req.rating)
    created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    cursor = conn.execute(
        "INSERT INTO reviews (seller_id, text, rating, label, score, temperature, mismatch, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            seller["id"],
            req.text,
            req.rating,
            result["label"],
            result["score"],
            result["temperature"],
            int(result["mismatch"]),
            created_at,
        ),
    )
    conn.commit()
    return to_review(get_review_row(conn, cursor.lastrowid))


@router.get("/v1/reviews", response_model=ReviewPage)
def list_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    seller: sqlite3.Row = Depends(current_seller),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """로그인한 판매자의 리뷰를 최근 것부터 한 페이지씩 돌려준다."""
    seller_id = seller["id"]
    total = conn.execute("SELECT COUNT(*) FROM reviews WHERE seller_id = ?", (seller_id,)).fetchone()[0]
    rows = conn.execute(
        f"SELECT {COLUMNS} FROM reviews WHERE seller_id = ? ORDER BY created_at DESC, id DESC"
        " LIMIT ? OFFSET ?",
        (seller_id, size, min((page - 1) * size, total)),
    ).fetchall()
    return {"items": [to_review(row) for row in rows], "page": page, "size": size, "total": total}


@router.patch("/v1/reviews/{review_id}", response_model=ReviewOut)
def update_memo(
    review_id: int,
    req: MemoUpdate,
    seller: sqlite3.Row = Depends(current_seller),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """내 리뷰의 메모를 바꾼다."""
    get_own_review_row(conn, review_id, seller)
    conn.execute("UPDATE reviews SET memo = ? WHERE id = ?", (req.memo, review_id))
    conn.commit()
    return to_review(get_review_row(conn, review_id))


@router.delete("/v1/reviews/{review_id}", status_code=204)
def delete_review(
    review_id: int,
    seller: sqlite3.Row = Depends(current_seller),
    conn: sqlite3.Connection = Depends(get_db),
) -> Response:
    """내 리뷰를 지운다."""
    get_own_review_row(conn, review_id, seller)
    conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    return Response(status_code=204)

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
