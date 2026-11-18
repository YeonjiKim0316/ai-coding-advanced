# 리뷰 온도계

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](LICENSE.md)

하루마켓(수업용 가상 쇼핑몰) 판매자가 자기 가게 리뷰를 붙여 넣으면, 긍정인지 부정인지 알려 주는 서버입니다.
리뷰가 얼마나 좋은지 0~100℃ '리뷰 온도'로 보여 주고, 별점과 내용이 반대인 리뷰도 찾아 줍니다.

여러분은 이 서비스를 앞 담당자에게서 넘겨받았습니다. 먼저 [HANDOVER.md](HANDOVER.md)를 읽습니다.

## 저장소 받기

1. https://github.com/YeonjiKim0316/ai-coding-advanced 에서 **Use this template** → **Create a new repository**를 누릅니다. 이름은 `ai-coding-advanced`, 공개(Public)로 만듭니다. 내 계정에 내 저장소가 생깁니다.
2. 터미널에서 내 저장소를 받습니다. `<내 아이디>`는 내 GitHub 아이디로 바꿉니다.

Windows PowerShell:

```powershell
cd $HOME\Documents
git clone https://github.com/<내 아이디>/ai-coding-advanced.git
cd ai-coding-advanced
```

macOS:

```bash
cd ~/Documents
git clone https://github.com/<내 아이디>/ai-coding-advanced.git
cd ai-coding-advanced
```

`cd $HOME\Documents`에서 경로가 없다고 나오면 문서 폴더가 OneDrive로 옮겨진 PC입니다. `cd $HOME\OneDrive\Documents`로 바꿉니다.

`checkpoints/` 폴더에는 단계별 완성본이 있습니다. 늦었을 때 비교하거나 따라잡는 데 씁니다.

## 처음 켜기

Python 3.11 ~ 3.13이 필요합니다. `python --version`(macOS `python3 --version`)으로 확인합니다.

터미널에서 저장소 폴더로 들어간 뒤 세 줄을 한 줄씩 칩니다. 가상환경을 켜는(activate) 명령은 치지 않아도 됩니다.

① 가상환경(이 프로젝트만의 파이썬 상자)을 만듭니다 ② 필요한 패키지를 넣습니다(처음에는 오래 걸립니다. 멈춘 듯 보여도 기다립니다) ③ 서버를 켭니다

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload
```

macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --reload
```

터미널에 `Uvicorn running on http://127.0.0.1:8000`이 보이면 켜진 것입니다. 이 터미널은 그대로 둡니다.

- http://localhost:8000 : 리뷰 분석 화면
- http://localhost:8000/dashboard.html : 대시보드 화면
- http://localhost:8000/docs : API 설명서

서버를 끌 때는 터미널에서 `Ctrl+C`를 누릅니다.

## 테스트

서버가 켜진 터미널과는 다른 터미널에서 칩니다.

Windows PowerShell:

```powershell
.venv\Scripts\python -m pytest -q
```

macOS:

```bash
.venv/bin/python -m pytest -q
```

테스트는 모델도 네트워크도 필요하지 않습니다.

## 폴더 안내

- `app/`: 서버 코드
- `static/`: 화면 파일
- `tests/`: 테스트
- `data/`: 분석 기록 샘플(`sample_logs.db`, 읽기 전용 원본)과 그 사본(`dev.db`)
- `docs/`: 상세 문서
- `models/`: AI 모델 파일
- `.agents/skills/`: AI에게 업무 순서를 알려 주는 스킬
- `.codex/config.toml`: 이 저장소 안에서만 쓰는 Codex 설정
- `render.yaml`: 인터넷에 내놓을 때 쓰는 설정

문서 목록: [HANDOVER.md](HANDOVER.md)(인수인계), [AGENTS.md](AGENTS.md)(AI 작업 규칙), [SPEC.md](SPEC.md)(리뷰 온도 명세), [DASHBOARD.md](DASHBOARD.md)(대시보드 명세), [SPEC_COUPON_OFFICIAL.md](SPEC_COUPON_OFFICIAL.md)(쿠폰 명세), [REQUEST.md](REQUEST.md)(옛 요청서)

## 안전 규칙

- API 키·비밀번호·실제 고객 정보는 AI 채팅과 파일에 넣지 않습니다.
- 결제 수단은 어디에도 등록하지 않습니다.
- Codex가 폴더 신뢰를 물으면, 이 저장소만 신뢰합니다.
- `data/sample_logs.db`는 읽기만 합니다. 고쳐 보는 것은 `data/dev.db`에서 합니다.

## 막혔을 때

[docs/troubleshooting.md](docs/troubleshooting.md)에서 증상을 찾습니다. 낱말이 어려우면 [docs/glossary.md](docs/glossary.md)를 봅니다.
