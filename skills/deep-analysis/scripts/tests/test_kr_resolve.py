"""data_sources.resolve_korean_name · 한글 종목명 → TickerInfo (Phase 3).

resolve_chinese_name_rich 의 한국어 대응. naver_search(ac 자동완성)를 monkeypatch
하여 네트워크 없이 라우팅 로직만 검증.

규칙:
- 입력과 이름이 정확히 일치하는 후보가 있으면 auto-resolve.
- 후보가 1개뿐이면 auto-resolve.
- 여러 후보 + 정확 일치 없음 → resolved=None (사용자 확인용 candidates 제공).
- KOSPI → .KS, KOSDAQ → .KQ.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def test_resolve_korean_name_exact_match(monkeypatch):
    import lib.kr_data_sources as kr
    import lib.data_sources as ds
    monkeypatch.setattr(kr, "naver_search",
                        lambda n: [{"code": "005930", "name": "삼성전자", "market": "K", "exchange": "KOSPI"}])
    r = ds.resolve_korean_name_rich("삼성전자")
    assert r["resolved"] is not None
    assert r["resolved"].full == "005930.KS"
    assert r["resolved"].market == "K"
    assert r["resolved"].code == "005930"


def test_resolve_korean_name_kosdaq_suffix(monkeypatch):
    import lib.kr_data_sources as kr
    import lib.data_sources as ds
    monkeypatch.setattr(kr, "naver_search",
                        lambda n: [{"code": "247540", "name": "에코프로비엠", "market": "K", "exchange": "KOSDAQ"}])
    r = ds.resolve_korean_name_rich("에코프로비엠")
    assert r["resolved"].full == "247540.KQ"


def test_resolve_korean_name_ambiguous_no_autoresolve(monkeypatch):
    import lib.kr_data_sources as kr
    import lib.data_sources as ds
    monkeypatch.setattr(kr, "naver_search", lambda n: [
        {"code": "005930", "name": "삼성전자", "exchange": "KOSPI"},
        {"code": "009150", "name": "삼성전기", "exchange": "KOSPI"},
    ])
    r = ds.resolve_korean_name_rich("삼성")
    assert r["resolved"] is None
    assert len(r["candidates"]) == 2


def test_resolve_korean_name_no_hit(monkeypatch):
    import lib.kr_data_sources as kr
    import lib.data_sources as ds
    monkeypatch.setattr(kr, "naver_search", lambda n: [])
    r = ds.resolve_korean_name_rich("없는종목명xyz")
    assert r["resolved"] is None
    assert r["candidates"] == []


def test_resolve_korean_name_thin_wrapper(monkeypatch):
    import lib.kr_data_sources as kr
    import lib.data_sources as ds
    monkeypatch.setattr(kr, "naver_search",
                        lambda n: [{"code": "035720", "name": "카카오", "exchange": "KOSPI"}])
    ti = ds.resolve_korean_name("카카오")
    assert ti is not None
    assert ti.full == "035720.KS"
