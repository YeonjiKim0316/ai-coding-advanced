# 명령 모음

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](../LICENSE.md)

Windows PowerShell 먼저, 그다음 macOS입니다. 가상환경을 켜는(activate) 명령은 치지 않습니다.

## 처음 한 번

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 서버

```powershell
.venv\Scripts\python -m uvicorn app.main:app --reload
```

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

- 화면: `http://localhost:8000`, API 설명서: `http://localhost:8000/docs`
- 끌 때는 `Ctrl+C`. 8000번 포트가 이미 쓰이고 있다고 나오면 다른 터미널의 서버를 끕니다.

## 테스트

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m pytest tests\test_thermo.py -q
```

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest tests/test_thermo.py -q
```

- 테스트는 `tests/` 폴더에 둡니다. 이름은 `test_`로 시작합니다.
- 테스트는 모델도 네트워크도 필요하지 않습니다. 가짜 AI를 끼웁니다.
