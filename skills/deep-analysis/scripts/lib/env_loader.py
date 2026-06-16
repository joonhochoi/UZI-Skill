"""lib 레벨 .env 로더 · Phase 2 (한국 시장 K).

`run.py._load_dotenv` 는 run.py 진입 시에만 실행된다. kr_data_sources / DART
클라이언트를 단독 실행(pytest, `python -m lib.kr_data_sources`)할 때도 `.env` 의
`DART_APIKEY` 등이 잡히도록, 어디서 import 하든 `.env` 를 한 번 로드한다.

시맨틱은 `run.py._load_dotenv` 와 동일하게 유지:
- 기존 os.environ 값은 절대 덮어쓰지 않음 (셸 export 가 항상 우선)
- 주석(#) / 빈 줄 / `=` 없는 줄 무시
- 값 양끝의 따옴표(' 또는 ") 1겹 제거
"""
from __future__ import annotations

import os
from pathlib import Path


def load_dotenv_from(path) -> int:
    """`path` 의 KEY=VALUE 줄을 os.environ 에 주입 (덮어쓰기 없음). 로드한 개수 반환."""
    path = Path(path)
    if not path.exists():
        return 0
    loaded = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = val
            loaded += 1
    return loaded


_LOADED = False


def load_dotenv_once() -> None:
    """이 파일에서 위로 올라가며 가장 가까운 `.env` 를 찾아 한 번만 로드 (idempotent).

    repo-root layout(skills/deep-analysis/scripts/lib/) 과 Hermes skill-dir layout
    모두에서, 상위 경로를 훑어 `.env` 가 있는 첫 디렉토리를 채택한다.
    """
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    here = Path(__file__).resolve()
    for parent in here.parents:
        env = parent / ".env"
        if env.exists():
            load_dotenv_from(env)
            return
