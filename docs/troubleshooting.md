# 막혔을 때

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](../LICENSE.md)

| 증상 | 이렇게 합니다 |
|---|---|
| `python`이 없다고 나오거나 Microsoft Store가 열립니다 | 터미널에서 `py --version`을 쳐 봅니다. 버전이 나오면 `python` 대신 `py`로 `py -m venv .venv`를 칩니다. (macOS는 `python3 --version`) |
| 패키지 설치에서 빨간 줄이 나오며 실패합니다 | 빨간 줄을 복사해 AI에게 붙여 넣고 물어봅니다. 단, 비밀번호나 키가 섞여 있지 않은지 먼저 봅니다. |
| 서버를 켰는데 8000번 포트를 이미 쓰고 있다고 나옵니다 | 서버가 켜진 터미널이 하나 더 있는지 찾아 `Ctrl+C`로 끕니다. 그다음 다시 켭니다. |
| `Activate.ps1`이나 "실행 정책" 오류가 나옵니다 | 가상환경을 켜는(activate) 명령은 치지 않아도 됩니다. `.venv\Scripts\python -m ...` 꼴로 칩니다. |
| 화면에 503 또는 "AI 부품이 아직 준비 중"이 나옵니다 | 모델을 불러오는 중이거나, `models/` 파일이 없어 내려받는 중입니다. 잠시 뒤 다시 누릅니다. |
| 테스트 창에 테스트가 안 보입니다 | 명령 팔레트(`Ctrl+Shift+P`, macOS는 `Cmd+Shift+P`)에서 `Python: Select Interpreter`를 고르고 `.venv`를 선택합니다. |
| `npx`가 안 됩니다 | Node.js가 있는지 `node --version`으로 봅니다. 없으면 설치한 뒤 터미널을 닫았다가 다시 엽니다. |
| MCP 도구가 안 보입니다 | Codex에서 `/mcp`를 쳐 서버 목록을 봅니다. 폴더를 신뢰했는지도 확인합니다. |
| AI가 고치면 안 되는 파일을 바꿨습니다 | `git restore <파일>`로 되돌립니다. 되돌리기 전에 바뀐 내용을 `git diff <파일>`로 봅니다. |
| 커밋할 때 "Please tell me who you are"가 나옵니다 | `git config --global user.name "내 이름"`과 `git config --global user.email "내 메일"`을 칩니다. |

그래도 안 되면 무엇을 했는지 적어 손을 듭니다.
