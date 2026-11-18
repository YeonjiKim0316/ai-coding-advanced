"""요청/응답의 모양(스키마). 강사 제공 파일.

여기에 적힌 규칙을 어기는 요청은 FastAPI가 자동으로 422로 거절합니다.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

# 앞뒤 공백을 지운 뒤 길이를 검사하는 글자 타입
Text500 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
Id20 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]


class AnalyzeRequest(BaseModel):
    """1차: 리뷰 분석 요청"""

    text: Text500  # 리뷰 글 (1~500자)
    rating: int = Field(ge=1, le=5)  # 별점 (1~5)


class AnalyzeResponse(BaseModel):
    """1차: 리뷰 분석 결과"""

    label: Literal["positive", "negative"]  # 긍정/부정
    score: float  # AI가 준 '긍정일 확률' (0~1)
    temperature: float  # 리뷰 온도 (0~100)
    mismatch: bool  # 별점과 내용이 반대인가


class CouponRequest(BaseModel):
    """3차: 쿠폰 발급 요청"""

    review_id: Id20  # 리뷰 번호 (1~20자)
    text: Text500  # 리뷰 글 (1~500자)


class CouponResponse(BaseModel):
    """3차: 쿠폰 발급 결과 (미발급이면 issued=False, 나머지는 None)"""

    issued: bool
    coupon_type: Literal["APOLOGY", "THANKS"] | None = None  # 사과 / 감사
    amount: int | None = None  # 쿠폰 금액(원)
    code: str | None = None  # 쿠폰 코드

class LogItem(BaseModel):
    """분석 기록 한 줄 (리뷰 글은 담지 않는다)"""

    id: int
    created_at: str
    rating: int
    label: Literal["positive", "negative"]
    score: float
    temperature: int
    mismatch: bool
    text_length: int


class LogPage(BaseModel):
    """분석 기록 목록 한 페이지"""

    items: list[LogItem]
    page: int
    size: int
    total: int


Memo200 = Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]


class ReviewCreate(BaseModel):
    """리뷰 저장 요청 (분석한 뒤 저장한다). 누구의 리뷰인지는 로그인한 판매자로 정한다."""

    text: Text500
    rating: int = Field(ge=1, le=5)


class MemoUpdate(BaseModel):
    """메모 바꾸기 요청"""

    memo: Memo200


class ReviewOut(BaseModel):
    """저장된 리뷰 한 건"""

    id: int
    seller_id: int
    text: str
    rating: int
    label: Literal["positive", "negative"]
    score: float
    temperature: float
    mismatch: bool
    memo: str
    created_at: str


class ReviewPage(BaseModel):
    """저장된 리뷰 목록 한 페이지"""

    items: list[ReviewOut]
    page: int
    size: int
    total: int


class LoginRequest(BaseModel):
    """로그인 요청"""

    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    password: Annotated[str, StringConstraints(min_length=1, max_length=200)]


class LoginResponse(BaseModel):
    """로그인 결과: 이후 요청에 Authorization: Bearer <token> 으로 보낸다"""

    token: str
    token_type: Literal["bearer"] = "bearer"
    seller_id: int
    name: str


# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
