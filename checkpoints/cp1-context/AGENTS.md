# AGENTS.md — 리뷰 온도계

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](LICENSE.md)

하루마켓 판매자가 리뷰를 붙여 넣으면 긍정·부정, 온도(0~100℃), 별점 불일치를 알려 주는 FastAPI 서버입니다.

## 실행·테스트 명령

- 서버: `.venv\Scripts\python -m uvicorn app.main:app --reload` (macOS `.venv/bin/python`)
- 테스트: `.venv\Scripts\python -m pytest -q` (macOS `.venv/bin/python -m pytest -q`)

## 꼭 지킬 규칙

1. 기준 문서(`SPEC.md`, `DASHBOARD.md`, `SPEC_COUPON_OFFICIAL.md`)의 이름과 숫자는 바꾸지 않습니다.
2. 테스트의 기대값을 바꿔서 통과시키지 않습니다. 테스트는 `tests/`에 둡니다.
3. 테스트는 Given–When–Then 주석을 답니다.
4. 새 패키지는 먼저 묻습니다.
5. 리뷰 원문, API 키, 비밀번호를 밖으로 보내지 않습니다.
6. `data/sample_logs.db`는 읽기만 합니다. 고쳐 보는 것은 `data/dev.db`에서만 합니다.
7. 삭제나 DB 변경(DELETE, DROP, UPDATE)은 실행할 문장을 먼저 보여 주고 "승인"을 기다립니다.
8. 애매하면 만들기 전에 먼저 질문합니다.
9. "승인" 전에는 커밋하지 않습니다.
10. 답은 쉬운 말로 짧게 합니다.

## 허락 없이 고치지 않는 곳

- `SPEC.md`, `DASHBOARD.md`, `SPEC_COUPON_OFFICIAL.md`, `REQUEST.md`, `tests/`, `static/`
- `app/sentiment.py`, `app/deps.py`, `app/schemas.py`, `models/`, `.codex/`
- `app/dashboard.py`는 `QUERIES`와 `TITLES`만 고칩니다.

## 자주 틀리는 곳

- 점수 0.5는 positive, 0.4999는 negative입니다. 별점 3은 불일치가 아닙니다.
- `score`는 소수점 넷째 자리, `temperature`는 첫째 자리까지 반올림합니다.
- 테스트는 가짜 AI(`tests/conftest.py`)를 씁니다. 모델을 직접 부르지 않습니다.

## 자세한 문서

- 구조: [docs/architecture.md](docs/architecture.md) · 명령: [docs/commands.md](docs/commands.md) · DB: [docs/db.md](docs/db.md)
- 막혔을 때: [docs/troubleshooting.md](docs/troubleshooting.md) · 낱말: [docs/glossary.md](docs/glossary.md)
- 인수인계: [HANDOVER.md](HANDOVER.md)

## 끝났을 때 보고

- 테스트 결과 한 줄, 바뀐 파일 목록, 커밋 메시지 한 줄을 알립니다.
- 허락 없이 고치면 안 되는 파일을 바꿨다면 커밋을 제안하지 말고 먼저 알립니다.
