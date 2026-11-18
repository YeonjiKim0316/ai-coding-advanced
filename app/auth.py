"""비밀번호 해시(pbkdf2)와 로그인 토큰(hmac 서명). 표준 라이브러리만 쓴다.

- SECRET_KEY 는 환경변수(.env 또는 Render 환경변수)에서만 읽는다. 코드에 적지 않는다.
- 토큰 모양: <판매자번호.만료시각을 base64url 로 바꾼 글>.<hmac-sha256 서명>
"""

import base64
import hashlib
import hmac
import os
import secrets
import time

TOKEN_TTL = 12 * 3600  # 토큰이 살아 있는 초
DEFAULT_ITERATIONS = 100_000


def get_secret() -> bytes:
    """서명 키를 환경변수 SECRET_KEY 에서 읽는다. 없으면 RuntimeError."""
    key = os.getenv("SECRET_KEY", "")
    if not key:
        raise RuntimeError("SECRET_KEY 환경변수가 없습니다 (.env 또는 Render 환경변수에 넣습니다)")
    return key.encode("utf-8")


def hash_password(password: str, salt: bytes | None = None) -> str:
    """pbkdf2_sha256$반복수$소금$해시 꼴 글자로 바꾼다."""
    iterations = int(os.getenv("PBKDF2_ITERATIONS", DEFAULT_ITERATIONS))
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    """비밀번호가 저장된 해시와 같은지 본다. 해시가 없거나 깨져 있으면 False."""
    try:
        scheme, iterations, salt_hex, digest_hex = (stored or "").split("$")
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)


def _sign(payload: str) -> str:
    return hmac.new(get_secret(), payload.encode("ascii"), hashlib.sha256).hexdigest()


def make_token(seller_id: int, ttl: int = TOKEN_TTL, now: float | None = None) -> str:
    """판매자 번호와 만료 시각을 담고 SECRET_KEY 로 서명한 토큰을 만든다."""
    expires = int((time.time() if now is None else now) + ttl)
    payload = base64.urlsafe_b64encode(f"{seller_id}.{expires}".encode("ascii")).decode("ascii")
    return f"{payload}.{_sign(payload)}"


def read_token(token: str, now: float | None = None) -> int | None:
    """서명이 맞고 만료 전이면 판매자 번호를, 아니면 None 을 돌려준다."""
    try:
        payload, signature = token.split(".")
        if not hmac.compare_digest(_sign(payload), signature):
            return None
        seller_id, expires = base64.urlsafe_b64decode(payload.encode("ascii")).decode("ascii").split(".")
        if (time.time() if now is None else now) >= int(expires):
            return None
        return int(seller_id)
    except (ValueError, UnicodeError):
        return None

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
