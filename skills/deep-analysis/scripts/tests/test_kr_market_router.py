"""한국(K) 시장 티커 파싱 · market_router Phase 1.

설계 결정 (new_dev_plan.md):
- 접미사 없는 순수 6자리 영숫자 코드는 **K 우선** (기존 A주 동작에서 변경)
- A주를 명시하려면 `.A` 접미사 (`600519.A` → A, 거래소는 _a_share_suffix로 추론)
- `.KS`(코스피) / `.KQ`(코스닥) 명시 접미사 → K
- 순수 6자리 K의 full은 best-effort `.KS` (실제 거래소는 fetch 단계에서 확정)
- 한글 종목명은 is_korean_name()으로 판정 (caller가 resolve)

모든 테스트는 순수 함수 단위 · 네트워크 의존 없음.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


# ─── 순수 6자리 → K 우선 (계약 변경의 핵심) ──────────────────────────
def test_bare_6digit_defaults_to_korea():
    """접미사 없는 6자리는 K 시장으로 라우팅된다 (구 A주 기본값에서 변경)."""
    from lib.market_router import parse_ticker
    ti = parse_ticker("005930")
    assert ti.market == "K", f"순수 6자리는 K여야 함, 실제 {ti.market}"
    assert ti.code == "005930"
    assert ti.full == "005930.KS", f"best-effort full은 .KS여야 함, 실제 {ti.full}"


def test_bare_6digit_kosdaq_style_code_still_korea():
    """코스닥 스타일 코드(247540 에코프로비엠)도 접미사 없으면 K."""
    from lib.market_router import parse_ticker
    ti = parse_ticker("247540")
    assert ti.market == "K"


# ─── 명시 접미사 .KS / .KQ → K ───────────────────────────────────────
def test_explicit_kospi_suffix():
    from lib.market_router import parse_ticker
    ti = parse_ticker("005930.KS")
    assert ti.market == "K"
    assert ti.full == "005930.KS"
    assert ti.code == "005930"


def test_explicit_kosdaq_suffix():
    from lib.market_router import parse_ticker
    ti = parse_ticker("247540.KQ")
    assert ti.market == "K"
    assert ti.full == "247540.KQ"
    assert ti.code == "247540"


def test_kr_suffix_case_insensitive():
    from lib.market_router import parse_ticker
    assert parse_ticker("005930.ks").market == "K"
    assert parse_ticker("247540.kq").full == "247540.KQ"


# ─── A주 명시: .A 접미사 → A (거래소는 _a_share_suffix로 추론) ────────
def test_dot_a_suffix_routes_to_ashare_sh():
    """600519.A → A주, 거래소 SH로 정규화."""
    from lib.market_router import parse_ticker
    ti = parse_ticker("600519.A")
    assert ti.market == "A"
    assert ti.full == "600519.SH"
    assert ti.code == "600519"


def test_dot_a_suffix_routes_to_ashare_sz():
    from lib.market_router import parse_ticker
    ti = parse_ticker("000858.A")
    assert ti.market == "A"
    assert ti.full == "000858.SZ"


def test_dot_a_suffix_etf_resolves_exchange_and_code_intact():
    """512400.A → SH ETF. classify_security_type(code)는 순수 함수로 유지."""
    from lib.market_router import parse_ticker, classify_security_type
    ti = parse_ticker("512400.A")
    assert ti.market == "A"
    assert ti.full == "512400.SH"
    assert classify_security_type(ti.code) == "etf"


def test_dot_a_suffix_case_insensitive():
    from lib.market_router import parse_ticker
    assert parse_ticker("600519.a").full == "600519.SH"


# ─── 기존 명시 접미사(.SZ/.SH/.BJ)는 그대로 A 유지 ────────────────────
def test_explicit_chinese_exchange_suffix_unchanged():
    from lib.market_router import parse_ticker
    assert parse_ticker("600519.SH").market == "A"
    assert parse_ticker("002273.SZ").market == "A"
    assert parse_ticker("830799.BJ").market == "A"
    assert parse_ticker("600519.SH").full == "600519.SH"


# ─── 다른 시장(H/U)은 회귀 없이 그대로 ───────────────────────────────
def test_hk_and_us_unaffected():
    from lib.market_router import parse_ticker
    assert parse_ticker("00700.HK").market == "H"
    assert parse_ticker("700").market == "H"        # 3자리 → HK (v2.10.2)
    assert parse_ticker("AAPL").market == "U"
    assert parse_ticker("BRK.B").market == "U"


# ─── 한글 종목명 판정 ────────────────────────────────────────────────
def test_is_korean_name_detects_hangul():
    from lib.market_router import is_korean_name
    assert is_korean_name("삼성전자") is True
    assert is_korean_name("SK하이닉스") is True   # 한글 일부 포함


def test_is_korean_name_false_for_non_hangul():
    from lib.market_router import is_korean_name
    assert is_korean_name("AAPL") is False
    assert is_korean_name("600519") is False
    assert is_korean_name("贵州茅台") is False     # 중국어는 한글 아님


def test_korean_name_is_not_chinese_name():
    """한글명이 is_chinese_name으로 잘못 잡히면 안 됨 (라우팅 분기 충돌 방지)."""
    from lib.market_router import is_chinese_name, is_korean_name
    assert is_korean_name("삼성전자") is True
    assert is_chinese_name("삼성전자") is False
