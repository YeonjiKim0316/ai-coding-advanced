"""아주 작은 .env 읽기. KEY=VALUE 줄만 읽는다. 이미 정해진 환경변수는 덮어쓰지 않는다."""

import os
from pathlib import Path


def load_env(path: str | Path = ".env") -> int:
    """파일이 있으면 환경변수에 넣고, 새로 넣은 개수를 돌려준다. 없으면 0."""
    file = Path(path)
    if not file.is_file():
        return 0
    added = 0
    for line in file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value
            added += 1
    return added

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
