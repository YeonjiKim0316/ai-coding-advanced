# DB 구조

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](../LICENSE.md)

현재 DB는 분석 기록 파일 하나입니다. `data/sample_logs.db`(읽기 전용 원본)와 그 사본 `data/dev.db`가 같은 구조입니다.

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

- 이 표는 읽기 전용 샘플입니다. 판매자 열이 없어서 누구의 리뷰인지 알 수 없습니다.

## 저장용 DB (`data/app.db`, git에 올리지 않음)

서버가 켜질 때 `migrations/*.sql`을 이름순으로 실행하고, 샘플 판매자 A·B를 넣습니다(`app/db.py`).
테스트는 `APP_DB_PATH`로 임시 파일을 씁니다.

| 표 | 열 | 메모 |
|---|---|---|
| `sellers` | `id`, `name`(겹치지 않음), `created_at`, `password_hash` | 샘플 판매자 `하루상점A`, `하루상점B`. 비밀번호는 pbkdf2 해시로만 저장합니다. |
| `reviews` | `id`, `seller_id`(sellers.id), `text`, `rating`, `label`, `score`, `temperature`, `mismatch`, `memo`, `created_at` | 판매자 1 : 리뷰 N. 판매자를 지우면 리뷰도 지워집니다(CASCADE). |

- 인덱스 `idx_reviews_seller_created`: `reviews(seller_id, created_at)` — "내 리뷰를 최근 것부터" 조회용입니다.
- API: `POST /v1/login`, `POST /v1/reviews`(분석 후 저장), `GET /v1/reviews`, `PATCH /v1/reviews/{id}`(메모), `DELETE /v1/reviews/{id}`. 리뷰 API는 로그인(Bearer 토큰)이 필요합니다.
- 마이그레이션: `001_sellers_reviews.sql`, `002_seller_password.sql`
