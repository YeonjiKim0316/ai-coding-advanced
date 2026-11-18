-- 판매자(sellers) 1 : 리뷰(reviews) N
-- 판매자를 지우면 그 판매자의 리뷰도 함께 지워진다(ON DELETE CASCADE).

CREATE TABLE sellers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL REFERENCES sellers(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    label TEXT NOT NULL CHECK (label IN ('positive', 'negative')),
    score REAL NOT NULL,
    temperature REAL NOT NULL,
    mismatch INTEGER NOT NULL CHECK (mismatch IN (0, 1)),
    memo TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

-- 자주 쓰는 조회: 내 리뷰를 최근 것부터
CREATE INDEX idx_reviews_seller_created ON reviews (seller_id, created_at);

-- © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
