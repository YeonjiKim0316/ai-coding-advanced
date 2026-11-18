"""분석 기록 목록 (SPEC_LOGS.md). data/sample_logs.db 를 읽기 전용으로 읽는다."""

from app.dashboard import open_readonly

COLUMNS = "id, created_at, rating, label, score, temperature, mismatch, text_length"


def list_logs(db_path: str, page: int, size: int, order: str = "newest") -> dict:
    """page(1부터)와 size로 한 페이지를 돌려준다. order=newest 는 id 큰 것부터, oldest 는 작은 것부터."""
    direction = "ASC" if order == "oldest" else "DESC"
    offset = (page - 1) * size
    with open_readonly(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM analysis_logs").fetchone()[0]
        rows = []
        if offset < total:  # 범위를 넘으면 DB에 묻지 않고 빈 목록
            rows = conn.execute(
                f"SELECT {COLUMNS} FROM analysis_logs ORDER BY id {direction} LIMIT ? OFFSET ?",
                (size, offset),
            ).fetchall()
    keys = [c.strip() for c in COLUMNS.split(",")]
    items = [dict(zip(keys, row)) | {"mismatch": bool(row[6])} for row in rows]
    return {"items": items, "page": page, "size": size, "total": total}

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
