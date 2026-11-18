---
name: review-branch
description: 브랜치 하나의 변경을 main과 비교해 리뷰한다. "$review-branch feat-reviews"처럼 스킬 이름 뒤에 브랜치 이름을 적는다. 지적만 하고 파일은 고치지 않는다.
---

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](../../../LICENSE.md)

# 브랜치 리뷰

## 대상 정하기

1. 사람이 스킬 이름 뒤에 적은 글을 브랜치 이름으로 씁니다. 예: `$review-branch feat-reviews` → `feat-reviews`.
2. 아무것도 적지 않았으면 지금 브랜치를 씁니다(`git branch --show-current`). 지금 브랜치가 main이면 어떤 브랜치를 볼지 먼저 묻습니다.
3. 그런 브랜치가 없으면 `git branch` 목록을 보여 주고 묻습니다.

## 순서

1. `git diff main...<브랜치> --stat`으로 바뀐 파일을 봅니다.
2. `git diff main...<브랜치>`로 바뀐 내용을 읽습니다.
3. `AGENTS.md`와 관련 스펙(SPEC로 시작하는 파일, DASHBOARD.md)을 기준으로 봅니다.
4. 테스트를 돌립니다: `python -m pytest -q` (Windows는 `.venv\Scripts\python -m pytest -q`).

## 보고 모양

결과 한 줄(테스트 결과 포함)을 먼저 쓰고, 지적은 표로 최대 7줄입니다.

| 번호 | 파일 | 무엇이 문제인가 | 꼭 고침 / 고치면 좋음 / 질문 |
|---|---|---|---|

## 하지 말 것

- 파일을 고치지 않습니다. 고칠 번호는 사람이 고릅니다.
- 커밋, 합치기, push를 하지 않습니다.
