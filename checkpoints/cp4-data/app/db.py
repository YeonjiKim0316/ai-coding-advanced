"""저장용 DB (data/app.db). 시작할 때 migrations/*.sql 을 순서대로 실행하고 샘플 판매자를 넣는다.

- DB 파일 위치: 환경변수 APP_DB_PATH, 없으면 data/app.db (git에 올리지 않는다)
- 이미 실행한 마이그레이션 파일은 schema_migrations 표에 적어 두고 다시 실행하지 않는다.
"""

import os
import sqlite3
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "migrations"
DEFAULT_DB = ROOT / "data" / "app.db"
SEED_SELLERS = ["하루상점A", "하루상점B"]

_lock = threading.Lock()
_ready: set[str] = set()


def app_db_path() -> str:
    """저장 DB 파일 경로. 테스트는 APP_DB_PATH 로 임시 파일을 가리킨다."""
    return os.getenv("APP_DB_PATH") or str(DEFAULT_DB)


def connect(path: str) -> sqlite3.Connection:
    """연결을 연다. 열 이름으로 값을 꺼낼 수 있고, 외래키(ON DELETE CASCADE)를 켠다."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_migrations(conn: sqlite3.Connection) -> list[str]:
    """아직 실행하지 않은 migrations/*.sql 을 이름순으로 실행하고, 실행한 파일 이름을 돌려준다."""
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY)")
    done = {row[0] for row in conn.execute("SELECT filename FROM schema_migrations")}
    applied = []
    for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if sql_file.name in done:
            continue
        conn.executescript(sql_file.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_migrations (filename) VALUES (?)", (sql_file.name,))
        conn.commit()
        applied.append(sql_file.name)
    return applied


def seed_sellers(conn: sqlite3.Connection) -> None:
    """샘플 판매자 A·B 를 넣는다. 이미 있으면 그대로 둔다."""
    for name in SEED_SELLERS:
        conn.execute("INSERT OR IGNORE INTO sellers (name) VALUES (?)", (name,))
    conn.commit()


def init_db(path: str) -> None:
    """DB 파일을 만들고(폴더 포함) 마이그레이션과 시드를 실행한다. 같은 경로는 한 번만 한다."""
    with _lock:
        if path in _ready and Path(path).exists():
            return
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        conn = connect(path)
        try:
            run_migrations(conn)
            seed_sellers(conn)
        finally:
            conn.close()
        _ready.add(path)

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
