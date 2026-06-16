"""stock_features · 한국(K) 시장 특성 추출 (Phase 5).

기존 버그: market 을 ticker 접미사로 추론하는데 .KS/.KQ 가 없어 한국 종목이
'US' 로 오판됨 → reality_check 가 미국 시장 룰을 적용. 본 Phase 에서 수정.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def _raw(ticker, basic=None):
    return {"ticker": ticker, "dimensions": {"0_basic": {"data": basic or {}}}}


def test_market_inferred_as_k_for_kospi_kosdaq():
    from lib.stock_features import extract_features
    assert extract_features(_raw("005930.KS"), {})["market"] == "K"
    assert extract_features(_raw("247540.KQ"), {})["market"] == "K"


def test_market_regression_a_hk_us_unaffected():
    from lib.stock_features import extract_features
    assert extract_features(_raw("600519.SH"), {})["market"] == "A"
    assert extract_features(_raw("000858.SZ"), {})["market"] == "A"
    assert extract_features(_raw("00700.HK"), {})["market"] == "HK"
    assert extract_features(_raw("AAPL"), {})["market"] == "US"


def test_market_cap_yi_from_korean_field():
    """K basic 은 market_cap_yi(억원) 수치를 직접 제공 → 그대로 사용."""
    from lib.stock_features import extract_features
    f = extract_features(_raw("005930.KS", {"market_cap_yi": 20052736.0, "market_cap": "2,005조"}), {})
    assert f["market_cap_yi"] == 20052736.0


def test_market_cap_yi_a_share_still_parses_string():
    """A주는 market_cap 문자열('4500亿')에서 파싱 (회귀)."""
    from lib.stock_features import extract_features
    f = extract_features(_raw("600519.SH", {"market_cap": "4500亿"}), {})
    assert f["market_cap_yi"] == 4500.0


def test_raw_market_takes_priority_over_ticker_suffix():
    """pipeline raw 의 ticker 는 접미사 없는 '005930' 이라, raw['market'] 를 우선해야 한다.

    버그: extract_features 가 ticker 접미사로만 추론 → '005930'이 US 로 오판되어
    평가위원이 미국 시장 룰로 평가하던 문제 (deep E2E 에서 발견).
    raw['market'] 는 parse_ticker 시장코드(A/H/U/K) → 내부 표기(A/HK/US/K)로 매핑.
    """
    from lib.stock_features import extract_features
    raw = {"ticker": "005930", "market": "K", "dimensions": {"0_basic": {"data": {}}}}
    assert extract_features(raw, {})["market"] == "K"
    raw_h = {"ticker": "00700", "market": "H", "dimensions": {"0_basic": {"data": {}}}}
    assert extract_features(raw_h, {})["market"] == "HK"
    raw_u = {"ticker": "AAPL", "market": "U", "dimensions": {"0_basic": {"data": {}}}}
    assert extract_features(raw_u, {})["market"] == "US"
    raw_a = {"ticker": "600519", "market": "A", "dimensions": {"0_basic": {"data": {}}}}
    assert extract_features(raw_a, {})["market"] == "A"
