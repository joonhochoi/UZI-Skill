"""lib/env_loader · .env 로더 (Phase 2).

run.py 의 _load_dotenv 는 run.py 를 거칠 때만 실행되므로, kr_data_sources / DART
클라이언트를 단독 실행(pytest, python -m)할 때 DART_APIKEY 가 잡히지 않는다.
lib 레벨 로더로 어디서 import 해도 .env 가 한 번 로드되게 한다.

시맨틱은 run.py._load_dotenv 와 동일:
- 기존 os.environ 값을 덮어쓰지 않음 (셸 export 가 항상 우선)
- 주석(#)/빈 줄/= 없는 줄 무시
- 따옴표 제거
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def test_load_dotenv_from_sets_missing_var(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("KR_ENV_TEST_A=bar123\n", encoding="utf-8")
    monkeypatch.delenv("KR_ENV_TEST_A", raising=False)
    from lib.env_loader import load_dotenv_from
    n = load_dotenv_from(env)
    assert os.environ["KR_ENV_TEST_A"] == "bar123"
    assert n == 1


def test_load_dotenv_from_does_not_override_existing(tmp_path, monkeypatch):
    """셸 환경변수가 .env 파일 값보다 우선 (run.py 와 동일 시맨틱)."""
    env = tmp_path / ".env"
    env.write_text("KR_ENV_TEST_B=fromfile\n", encoding="utf-8")
    monkeypatch.setenv("KR_ENV_TEST_B", "fromshell")
    from lib.env_loader import load_dotenv_from
    load_dotenv_from(env)
    assert os.environ["KR_ENV_TEST_B"] == "fromshell"


def test_load_dotenv_from_ignores_comments_blanks_and_quotes(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        "# 주석\n"
        "\n"
        "KR_ENV_TEST_C='quoted'\n"
        "no_equals_line\n"
        'KR_ENV_TEST_D="dq"\n',
        encoding="utf-8",
    )
    for k in ("KR_ENV_TEST_C", "KR_ENV_TEST_D"):
        monkeypatch.delenv(k, raising=False)
    from lib.env_loader import load_dotenv_from
    load_dotenv_from(env)
    assert os.environ["KR_ENV_TEST_C"] == "quoted"
    assert os.environ["KR_ENV_TEST_D"] == "dq"


def test_load_dotenv_from_missing_file_returns_zero(tmp_path):
    from lib.env_loader import load_dotenv_from
    assert load_dotenv_from(tmp_path / "nope.env") == 0


def test_load_dotenv_once_is_idempotent(monkeypatch):
    """load_dotenv_once 는 두 번 불러도 한 번만 실제 로드 (플래그 캐시)."""
    import lib.env_loader as el
    monkeypatch.setattr(el, "_LOADED", False, raising=False)
    calls = {"n": 0}
    monkeypatch.setattr(el, "load_dotenv_from", lambda p: calls.__setitem__("n", calls["n"] + 1))
    el.load_dotenv_once()
    el.load_dotenv_once()
    assert calls["n"] <= 1, "두 번째 호출은 no-op 이어야 함"
