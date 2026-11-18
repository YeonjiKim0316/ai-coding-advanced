"""FastAPI 앱. 대시보드 데이터는 app/dashboard.py 에서 채웁니다.

실행: uvicorn app.main:app --reload
흐름: 화면/요청 -> 입력 검사(schemas) -> AI 점수(predict) -> 규칙(thermo, coupon) -> 응답
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import analysis, auth, coupon, db, logs, reviews, thermo
from app.envfile import load_env
from app.analysis import Predict, get_score
from app.dashboard import run_dashboard
from app.deps import get_db, get_dashboard_db, get_logs_db, get_predict
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    CouponRequest,
    CouponResponse,
    LogPage,
    LoginRequest,
    LoginResponse,
)

load_env(Path(__file__).resolve().parent.parent / ".env")  # 있으면 읽는다 (SECRET_KEY 등)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버가 켜질 때 SECRET_KEY 가 있는지 보고 저장 DB를 준비한다."""
    auth.get_secret()  # 없으면 여기서 멈춘다
    db.init_db(db.app_db_path())
    yield


app = FastAPI(title="리뷰 온도계 API", version="1.0.0", lifespan=lifespan)
app.include_router(reviews.router)


@app.exception_handler(NotImplementedError)
async def not_implemented(request: Request, exc: NotImplementedError) -> JSONResponse:
    """아직 AI와 함께 만들지 않은 함수를 부르면 501과 함수 이름을 알려 준다."""
    return JSONResponse(status_code=501, content={"detail": f"아직 구현되지 않았습니다: {exc}"})


@app.get("/health")
def health() -> dict[str, str]:
    """서버가 살아 있는지 확인."""
    return {"status": "ok"}


# 없는 판매자와 틀린 비밀번호에 같은 시간이 걸리도록, 없는 판매자에게도 해시 비교를 한 번 한다.
DUMMY_HASH = auth.hash_password("no-such-seller")


@app.post("/v1/login", response_model=LoginResponse)
def login(req: LoginRequest, conn: sqlite3.Connection = Depends(get_db)) -> LoginResponse:
    """판매자 이름과 비밀번호로 로그인한다. 맞으면 토큰을 돌려준다. 아니면 401."""
    seller = conn.execute(
        "SELECT id, name, password_hash FROM sellers WHERE name = ?", (req.name,)
    ).fetchone()
    stored = seller["password_hash"] if seller else DUMMY_HASH
    if not auth.verify_password(req.password, stored) or seller is None:
        raise HTTPException(status_code=401, detail="이름 또는 비밀번호가 맞지 않습니다")
    return LoginResponse(token=auth.make_token(seller["id"]), seller_id=seller["id"], name=seller["name"])


@app.post("/v1/reviews/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, predict: Predict = Depends(get_predict)) -> AnalyzeResponse:
    """1차: 리뷰 한 건 -> 긍정/부정, 온도, 별점 불일치."""
    return AnalyzeResponse(**analysis.analyze_text(predict, req.text, req.rating))


@app.post("/v1/coupons/issue", response_model=CouponResponse)
def issue_coupon(req: CouponRequest, predict: Predict = Depends(get_predict)) -> CouponResponse:
    """3차: 리뷰 -> 쿠폰 (긍정/부정은 서버가 다시 판단). 미발급이어도 200."""
    score = round(get_score(predict, req.text), 4)
    label = thermo.to_label(score)
    return CouponResponse(**coupon.decide_coupon(req.review_id, req.text, label))


@app.get("/v1/dashboard")
def dashboard(db_path: str = Depends(get_dashboard_db)) -> dict[str, dict]:
    """2차: 대시보드 카드마다 결과를 돌려준다. 쿼리는 app/dashboard.py 에서 채운다."""
    return run_dashboard(db_path)


@app.get("/v1/logs", response_model=LogPage)
def list_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order: Literal["newest", "oldest"] = "newest",
    db_path: str = Depends(get_logs_db),
) -> dict:
    """분석 기록 목록: 한 페이지씩. order 로 최근순(기본)과 오래된 순을 고른다."""
    return logs.list_logs(db_path, page, size, order)


# 화면(static/)은 마지막에 "/" 로 연결해야 위의 API 경로가 먼저 잡힌다.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
