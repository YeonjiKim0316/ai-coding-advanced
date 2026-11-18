"""요청마다 한 줄 로그를 남기는 미들웨어.

남기는 것: request_id, 방법, 경로, 상태코드, 걸린 시간(ms), seller_id (오류면 오류 이름과 위치)
남기지 않는 것: 토큰, 비밀번호, 리뷰 원문, 쿼리 문자열, 오류 메시지(글 내용이 들어 있을 수 있다)
"""

import logging
import re
import sys
import time
import uuid
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.access")
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,64}$")


def setup_logging() -> None:
    """app.access 로그가 터미널(Render 로그)에 한 줄씩 나오게 한다. 여러 번 불러도 한 번만 붙는다."""
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def error_place(exc: BaseException) -> str:
    """오류가 난 곳(파일 이름:줄)을 돌려준다. 오류 메시지는 쓰지 않는다."""
    tb = exc.__traceback__
    while tb is not None and tb.tb_next is not None:
        tb = tb.tb_next
    if tb is None:
        return "?"
    return f"{Path(tb.tb_frame.f_code.co_filename).name}:{tb.tb_lineno}"


async def access_log(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """request_id 를 정하고, 요청이 끝나면 한 줄을 남긴다. 처리하지 못한 오류는 500 으로 돌려준다."""
    incoming = request.headers.get("x-request-id", "")
    request_id = incoming if REQUEST_ID_PATTERN.match(incoming) else uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    started = time.perf_counter()
    status = 500
    error = ""
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception as exc:  # 처리하지 못한 오류
        error = f" error={type(exc).__name__} at={error_place(exc)}"
        response = JSONResponse(
            status_code=500, content={"detail": "서버 오류가 났습니다", "request_id": request_id}
        )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    seller_id = getattr(request.state, "seller_id", "-")
    logger.info(
        "request_id=%s method=%s path=%s status=%s ms=%s seller_id=%s%s",
        request_id, request.method, request.url.path, status, elapsed_ms, seller_id, error,
    )
    response.headers["X-Request-ID"] = request_id
    return response

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
