"""저장 DB 테스트: 마이그레이션, 시드, 인덱스, 외래키. 임시 DB만 쓴다."""

import sqlite3

import pytest

from app import db


@pytest.fixture
def conn(tmp_path):
    """마이그레이션까지 끝낸 임시 DB 연결."""
    path = str(tmp_path / "t.db")
    db.init_db(path)
    c = db.connect(path)
    yield c
    c.close()


def test_migrations_create_tables(conn):
    # Given: init_db 를 끝낸 DB
    # When: 표 이름을 읽는다
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    # Then: sellers, reviews, 기록용 표가 있다
    assert {"sellers", "reviews", "schema_migrations"} <= tables


def test_index_on_seller_and_created_at(conn):
    # Given: init_db 를 끝낸 DB
    # When: reviews 의 인덱스 열을 읽는다
    cols = [r[2] for r in conn.execute("PRAGMA index_info(idx_reviews_seller_created)")]
    # Then: (seller_id, created_at) 순서다
    assert cols == ["seller_id", "created_at"]


def test_seed_has_two_sellers(conn):
    # Given: init_db 를 끝낸 DB
    # When: 판매자를 읽는다
    names = [r[0] for r in conn.execute("SELECT name FROM sellers ORDER BY id")]
    # Then: A, B 두 곳이다
    assert names == ["하루상점A", "하루상점B"]


def test_init_is_repeatable(tmp_path):
    # Given: 이미 준비한 DB
    path = str(tmp_path / "again.db")
    db.init_db(path)
    c = db.connect(path)
    # When: 마이그레이션과 시드를 한 번 더 실행한다
    applied = db.run_migrations(c)
    db.seed_sellers(c)
    # Then: 새로 실행한 파일이 없고 판매자는 여전히 2명이다
    assert applied == []
    assert c.execute("SELECT COUNT(*) FROM sellers").fetchone()[0] == 2
    c.close()


def test_delete_seller_deletes_reviews(conn):
    # Given: 판매자 1의 리뷰 하나
    conn.execute(
        "INSERT INTO reviews (seller_id, text, rating, label, score, temperature, mismatch, created_at)"
        " VALUES (1, 'a', 5, 'positive', 0.9, 90, 0, '2026-10-12T00:00:00')"
    )
    # When: 판매자 1을 지운다
    conn.execute("DELETE FROM sellers WHERE id = 1")
    # Then: 그 리뷰도 함께 사라진다 (ON DELETE CASCADE)
    assert conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 0


def test_review_needs_existing_seller(conn):
    # Given: 없는 판매자 번호 99
    # When/Then: 리뷰를 넣으면 외래키 오류가 난다
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO reviews (seller_id, text, rating, label, score, temperature, mismatch, created_at)"
            " VALUES (99, 'a', 5, 'positive', 0.9, 90, 0, '2026-10-12T00:00:00')"
        )


def test_app_db_path_uses_env(monkeypatch, tmp_path):
    # Given: APP_DB_PATH 를 임시 파일로 정했다
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "x.db"))
    # When: 경로를 묻는다
    # Then: 그 값이다 (기본값 data/app.db 가 아니다)
    assert db.app_db_path() == str(tmp_path / "x.db")

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
