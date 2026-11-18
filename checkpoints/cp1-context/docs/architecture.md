# 구조

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](../LICENSE.md)

## 요청이 지나가는 길

화면이나 요청 -> 입력 검사(`app/schemas.py`) -> AI 점수(`app/sentiment.py`의 `predict`) -> 이모지 보정과 규칙(`app/analysis.py`, `app/thermo.py`) -> 응답

## 파일 역할

| 파일 | 하는 일 |
|---|---|
| `app/main.py` | API 주소(엔드포인트)를 모아 둡니다. 화면(`static/`)을 `/`에 연결합니다. |
| `app/schemas.py` | 요청과 응답의 모양. 규칙에 맞지 않으면 422입니다. |
| `app/thermo.py` | 리뷰 온도 규칙 세 개(`to_label`, `to_temperature`, `is_mismatch`)와 이모지 보정(`calm_score`). |
| `app/analysis.py` | 글 -> AI 점수 -> 보정 -> 규칙으로 이어지는 흐름. |
| `app/coupon.py` | 쿠폰을 줄지 정하는 규칙. |
| `app/dashboard.py` | 대시보드 카드의 SQL(`QUERIES`)과 제목(`TITLES`). DB는 읽기 전용으로 엽니다. |
| `app/deps.py` | 라우터가 받는 부품(분류기, DB 경로). 테스트에서 가짜로 바꿔 끼웁니다. |
| `app/sentiment.py` | AI 모델을 불러와 점수를 냅니다. `models/`를 먼저 보고 없으면 내려받습니다. |
| `static/` | 화면 파일과 샘플 리뷰. |

## 쿠폰 규칙 요약

- negative이면 사과 쿠폰 3000원, positive이고 글이 30자 이상이면 감사 쿠폰 1000원입니다.
- 코드는 `HARU-APL-` 또는 `HARU-THX-` 뒤에 리뷰 번호 대문자를 붙입니다.
- 자세한 것은 `SPEC_COUPON_OFFICIAL.md`.

## 앞 담당자 메모

- 별점 3은 불일치로 보지 않기로 정했습니다. 0.5는 긍정입니다.
- 이모지가 글자보다 많은 리뷰는 점수를 중립(0.5) 쪽으로 절반 당깁니다.
- 처음 모델은 서버가 켜질 때마다 내려받았지만, 지금은 `models/`를 먼저 봅니다.
