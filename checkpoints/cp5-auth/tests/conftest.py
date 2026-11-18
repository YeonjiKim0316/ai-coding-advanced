"""강사 제공 테스트 도구: 가짜 AI 부품을 끼운 TestClient (모델·네트워크 필요 없음)."""

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient

from app.deps import get_predict
from app.main import app


@pytest.fixture(autouse=True)
def temp_app_db(tmp_path, monkeypatch) -> None:
    """모든 테스트는 임시 저장 DB와 테스트용 키를 쓴다. data/app.db 와 진짜 키는 건드리지 않는다."""
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-for-pytest-only")  # 테스트용 키 (진짜 키가 아님)
    monkeypatch.setenv("PBKDF2_ITERATIONS", "1000")  # 테스트를 빠르게


@pytest.fixture
def make_client() -> Iterator[Callable[[float], TestClient]]:
    """`make_client(0.8)` -> 어떤 리뷰든 점수 0.8을 돌려주는 가짜 AI가 연결된 클라이언트."""

    def _make(score: float) -> TestClient:
        def fake_predict(texts: list[str]) -> list[float]:
            return [score] * len(texts)

        app.dependency_overrides[get_predict] = lambda: fake_predict
        return TestClient(app)

    yield _make
    app.dependency_overrides.clear()


@pytest.fixture
def broken_client() -> Iterator[TestClient]:
    """AI 부품이 고장 난 클라이언트 (predict가 항상 에러) — 503 확인용."""

    def broken_predict(texts: list[str]) -> list[float]:
        raise RuntimeError("model down")

    app.dependency_overrides[get_predict] = lambda: broken_predict
    yield TestClient(app)
    app.dependency_overrides.clear()


PASSWORDS = {"하루상점A": "haru-a-1234", "하루상점B": "haru-b-1234"}


@pytest.fixture
def login():
    """`login(client, "하루상점A")` -> Authorization 헤더(dict). 수업용 시드 비밀번호로 로그인한다."""

    def _login(client: TestClient, name: str = "하루상점A") -> dict[str, str]:
        r = client.post("/v1/login", json={"name": name, "password": PASSWORDS[name]})
        assert r.status_code == 200
        return {"Authorization": f"Bearer {r.json()['token']}"}

    return _login


# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
