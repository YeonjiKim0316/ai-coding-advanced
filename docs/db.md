# DB 구조

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](../LICENSE.md)

현재 DB는 분석 기록 파일 하나입니다. `data/sample_logs.db`(읽기 전용 원본)입니다. 고쳐 보는 앱 DB `data/app.db`는 서버를 한 번 켜면 생깁니다.

## analysis_logs

분석 기록 한 줄이 리뷰 한 건입니다. 가상 데이터입니다.

| 열 | 타입 | 뜻 |
|---|---|---|
| `id` | INTEGER, 기본키 | 번호 (자동으로 늘어남) |
| `created_at` | TEXT | 분석한 시각 (`2026-10-12T08:44:46` 꼴 글자) |
| `rating` | INTEGER | 별점 1~5 |
| `text_length` | INTEGER | 리뷰 글자 수 |
| `label` | TEXT | `positive` 또는 `negative` |
| `score` | REAL | AI 점수 0~1 |
| `temperature` | INTEGER | 리뷰 온도 0~100 (정수) |
| `mismatch` | INTEGER | 별점과 내용이 반대인가 (1 = 그렇다, 0 = 아니다) |
| `review_text` | TEXT | 리뷰 글 |

- 판매자 열이 없습니다. 누구의 리뷰인지 알 수 없습니다.
- 인덱스가 없습니다.
