"""작은 .env 읽기 테스트."""

import os

from app.envfile import load_env


def test_load_env_reads_lines(tmp_path, monkeypatch):
    # Given: 주석, 빈 줄, 따옴표가 섞인 .env
    monkeypatch.delenv("DEMO_A", raising=False)
    monkeypatch.delenv("DEMO_B", raising=False)
    f = tmp_path / ".env"
    f.write_text("# 주석\n\nDEMO_A=값1\nDEMO_B = \"값 2\"\n줄바꿈만\n", encoding="utf-8")
    # When: 읽는다
    added = load_env(f)
    # Then: 두 개가 들어간다
    assert added == 2 and os.environ["DEMO_A"] == "값1" and os.environ["DEMO_B"] == "값 2"
    monkeypatch.delenv("DEMO_A")
    monkeypatch.delenv("DEMO_B")


def test_load_env_does_not_override(tmp_path, monkeypatch):
    # Given: 이미 정해진 환경변수와 같은 이름이 .env 에 있다
    monkeypatch.setenv("DEMO_C", "원래값")
    f = tmp_path / ".env"
    f.write_text("DEMO_C=덮어쓰기\n", encoding="utf-8")
    # When: 읽는다
    added = load_env(f)
    # Then: 원래값이 남는다
    assert added == 0 and os.environ["DEMO_C"] == "원래값"


def test_load_env_missing_file(tmp_path):
    # Given: 없는 파일
    # When/Then: 오류 없이 0
    assert load_env(tmp_path / "nope.env") == 0

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
