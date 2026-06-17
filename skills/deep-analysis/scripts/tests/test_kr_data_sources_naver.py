"""kr_data_sources · 네이버 신 API 파서 (Phase 2).

순수 파싱/정규화 함수를 fixture(tests/fixtures/kr/) 기반으로 검증한다.
네트워크는 _raw_get(url,...) 을 monkeypatch 하여 격리 — 실제 호출 없음.

fixture ground-truth (삼성전자 005930, 2026-06-16 수집):
- PER 27.72배 / PBR 4.77배 / EPS 12,372원 / BPS 71,907원
- 추정PER 7.83배 / 추정EPS 43,833원 / 배당수익률 0.49% / 주당배당 1,668원
- 시총 "2,005조 2,736억" → 20,052,736 억원
- 거래소: 005930=KS(코스피), 247540=KQ(코스닥)
- research[0]: brokerName 있음 · previewContent "목표주가를 55만원으로" → 550,000원
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
FX = Path(__file__).resolve().parent / "fixtures" / "kr"


def _load(name):
    return json.loads((FX / name).read_text(encoding="utf-8"))


# ─── 숫자/단위 파싱 헬퍼 ─────────────────────────────────────────────
def test_parse_kr_number_variants():
    from lib.kr_data_sources import _parse_kr_number
    assert _parse_kr_number("27.52배") == 27.52
    assert _parse_kr_number("1,668원") == 1668.0
    assert _parse_kr_number("0.49%") == 0.49
    assert _parse_kr_number("12,372") == 12372.0
    assert _parse_kr_number("-1,828,940") == -1828940.0
    assert _parse_kr_number("+531,697") == 531697.0
    assert _parse_kr_number("-") is None
    assert _parse_kr_number("") is None
    assert _parse_kr_number(None) is None


def test_parse_market_cap_to_eok():
    """억원 단위로 정규화 (기존 market_cap_yi=亿 시맨틱과 맞춤)."""
    from lib.kr_data_sources import _parse_market_cap_to_eok
    assert _parse_market_cap_to_eok("2,005조 2,736억") == 20052736.0
    assert _parse_market_cap_to_eok("4,500억") == 4500.0
    assert _parse_market_cap_to_eok("3조") == 30000.0
    assert _parse_market_cap_to_eok("-") is None


# ─── _get_json · HTML 에러페이지 거부 ────────────────────────────────
def test_get_json_rejects_html_error_page(monkeypatch):
    import lib.kr_data_sources as kr
    monkeypatch.setattr(kr, "_raw_get", lambda *a, **k: (200, "<!doctype html><html>Npay</html>"))
    assert kr._get_json("https://x") is None


def test_get_json_parses_valid_json(monkeypatch):
    import lib.kr_data_sources as kr
    monkeypatch.setattr(kr, "_raw_get", lambda *a, **k: (200, '{"a": 1}'))
    assert kr._get_json("https://x") == {"a": 1}
    monkeypatch.setattr(kr, "_raw_get", lambda *a, **k: (200, '[1, 2]'))
    assert kr._get_json("https://x") == [1, 2]


def test_get_json_returns_none_on_non_200(monkeypatch):
    import lib.kr_data_sources as kr
    monkeypatch.setattr(kr, "_raw_get", lambda *a, **k: (404, '{"a":1}'))
    assert kr._get_json("https://x") is None


# ─── parse_integration → 0_basic + 10_valuation + cns + deal_trend ──
def test_parse_integration_core_fields():
    from lib.kr_data_sources import parse_integration
    out = parse_integration(_load("naver_integration_005930.json"))
    assert out["name"] == "삼성전자"
    assert out["code"] == "005930"
    assert out["pe_ttm"] == 27.72
    assert out["pb"] == 4.77
    assert out["eps"] == 12372.0
    assert out["bps"] == 71907.0
    assert out["dividend_yield"] == 0.49
    assert out["market_cap_yi"] == 20052736.0
    assert out["foreign_hold_ratio"] == 47.60


def test_parse_integration_consensus_fields():
    from lib.kr_data_sources import parse_integration
    out = parse_integration(_load("naver_integration_005930.json"))
    assert out["consensus_pe"] == 7.83
    assert out["consensus_eps"] == 43833.0


def test_parse_integration_deal_trend_present():
    from lib.kr_data_sources import parse_integration
    out = parse_integration(_load("naver_integration_005930.json"))
    dt = out["deal_trend"]
    assert isinstance(dt, list) and len(dt) > 0
    row0 = dt[0]
    assert row0["date"] == "20260615"
    assert row0["foreign_net"] == -1828940.0
    assert row0["org_net"] == 531697.0
    assert row0["individual_net"] == 1306068.0


# ─── parse_basic · 거래소 구분 + 통화 ────────────────────────────────
def test_parse_basic_kospi():
    from lib.kr_data_sources import parse_basic
    out = parse_basic(_load("naver_basic_005930.json"))
    assert out["exchange"] == "KS"
    assert out["market_suffix"] == ".KS"
    assert out["currency"] == "KRW"
    assert out["price"] == 343000.0
    assert out["name"] == "삼성전자"


def test_parse_basic_kosdaq():
    from lib.kr_data_sources import parse_basic
    out = parse_basic(_load("naver_basic_247540_kosdaq.json"))
    assert out["exchange"] == "KQ"
    assert out["market_suffix"] == ".KQ"


# ─── parse_research · 6_research + 목표가 추출 ───────────────────────
def test_parse_research_basic_shape():
    from lib.kr_data_sources import parse_research
    out = parse_research(_load("naver_research_005930.json"))
    assert out["report_count"] >= 1
    assert out["coverage_count"] >= 1     # 고유 증권사 수
    r0 = out["recent_reports"][0]
    assert r0["broker"]
    assert r0["date"]
    assert r0["title"]


def test_parse_research_extracts_target_price_from_preview():
    """previewContent '목표주가를 55만원으로' → 550,000원 추출."""
    from lib.kr_data_sources import _extract_target_price
    assert _extract_target_price("투자의견 매수, 목표주가를 55만원으로 유지") == 550000.0
    assert _extract_target_price("목표주가 550,000원 제시") == 550000.0
    assert _extract_target_price("특이사항 없음") is None


# ─── parse_trend → 12_capital_flow ──────────────────────────────────
def test_parse_trend_maps_investors():
    from lib.kr_data_sources import parse_trend
    rows = parse_trend(_load("naver_trend_005930.json"))
    assert isinstance(rows, list) and len(rows) > 0
    assert rows[0]["date"] == "20260615"
    assert "foreign_net" in rows[0] and "org_net" in rows[0] and "individual_net" in rows[0]


# ─── parse_news → 15_events ─────────────────────────────────────────
def test_parse_news_shape():
    from lib.kr_data_sources import parse_news
    news = parse_news(_load("naver_news_005930.json"))
    assert isinstance(news, list) and len(news) > 0
    n0 = news[0]
    assert n0["title"]
    assert n0["source"]
    assert n0["url"].startswith("http")


# ─── parse_price_history / parse_chart → 2_kline ────────────────────
def test_parse_price_history_ohlcv():
    from lib.kr_data_sources import parse_price_history
    candles = parse_price_history(_load("naver_price_005930.json"))
    assert len(candles) > 0
    c0 = candles[0]
    for k in ("date", "open", "high", "low", "close", "volume"):
        assert k in c0
    assert c0["close"] > 0


def test_parse_chart_ohlcv_float():
    from lib.kr_data_sources import parse_chart
    candles = parse_chart(_load("naver_chart_day_005930.json"))
    assert len(candles) > 0
    c0 = candles[0]
    assert isinstance(c0["close"], float)
    assert c0["high"] >= c0["low"]


# ─── parse_search → 이름→코드 ───────────────────────────────────────
def test_parse_search_name_to_code():
    from lib.kr_data_sources import parse_search
    cands = parse_search(_load("naver_ac_samsung.json"))
    assert len(cands) > 0
    top = cands[0]
    assert top["code"] == "005930"
    assert top["name"] == "삼성전자"
    assert top["market"] == "K"
    assert top["exchange"] in ("KOSPI", "KOSDAQ")


# ─── parse_finance → 1_financials (매트릭스 → 시계열) ────────────────
def test_parse_finance_annual_periods_split_confirmed_vs_consensus():
    from lib.kr_data_sources import parse_finance
    out = parse_finance(_load("naver_finance_annual_005930.json"), period_type="annual")
    assert out["periods"] == ["2023", "2024", "2025"]
    assert out["consensus_periods"] == ["2026"]


def test_parse_finance_annual_revenue_series_chronological():
    from lib.kr_data_sources import parse_finance
    out = parse_finance(_load("naver_finance_annual_005930.json"), period_type="annual")
    rev = out["revenue_history"]
    assert len(rev) == 3                 # 확정 3개년만 (컨센서스 제외)
    assert rev[-1] == 3336059.0          # 2025 (억원)


def test_parse_finance_annual_latest_ratios():
    from lib.kr_data_sources import parse_finance
    out = parse_finance(_load("naver_finance_annual_005930.json"), period_type="annual")
    assert out["roe"] == 10.85           # 2025 ROE(%)
    assert out["debt_ratio"] == 29.94
    assert out["eps"] == 6564.0
    assert len(out["roe_history"]) == 3


def test_parse_finance_annual_consensus_block():
    from lib.kr_data_sources import parse_finance
    out = parse_finance(_load("naver_finance_annual_005930.json"), period_type="annual")
    c = out["consensus"]["2026"]
    assert c["revenue"] == 6932502.0
    assert c["eps"] == 43833.0
    assert c["roe"] == 52.18


def test_parse_finance_annual_revenue_growth_yoy():
    from lib.kr_data_sources import parse_finance
    out = parse_finance(_load("naver_finance_annual_005930.json"), period_type="annual")
    # (3336059 - 3008709) / 3008709 * 100 ≈ 10.88
    assert out["revenue_growth_pct"] == 10.88


def test_parse_finance_quarter_labels():
    from lib.kr_data_sources import parse_finance
    out = parse_finance(_load("naver_finance_quarter_005930.json"), period_type="quarter")
    assert all(("Q" in p) for p in out["periods"])
    assert len(out["periods"]) >= 4


# ─── merge_basic · integration + basic → 0_basic 스키마 ─────────────
def test_merge_basic_combines_integration_and_basic():
    from lib.kr_data_sources import merge_basic, parse_integration, parse_basic
    inte = parse_integration(_load("naver_integration_005930.json"))
    basic = parse_basic(_load("naver_basic_005930.json"))
    out = merge_basic(inte, basic)
    assert out["name"] == "삼성전자"
    assert out["price"] == 343000.0          # basic 실시간가
    assert out["pe_ttm"] == 27.72            # integration
    assert out["pb"] == 4.77
    assert out["market_cap_yi"] == 20052736.0
    assert out["exchange"] == "KS"
    assert out["market_suffix"] == ".KS"
    assert out["currency"] == "KRW"
    assert out["market"] == "K"
    assert out["market_cap"].endswith("조")   # 표시 문자열


def test_merge_basic_handles_empty_inputs():
    from lib.kr_data_sources import merge_basic
    out = merge_basic({}, {})
    assert out["market"] == "K"               # 빈 입력도 raise 안 함


# ─── industry 업종명 + peers (Phase 7) ──────────────────────────────
def test_parse_integration_industry_code_and_compare():
    from lib.kr_data_sources import parse_integration
    out = parse_integration(_load("naver_integration_005930.json"))
    assert str(out["industry_code"]) == "278"
    comp = out["industry_compare"]
    assert len(comp) >= 1
    assert comp[0]["name"] == "SK하이닉스"
    assert comp[0]["code"] == "000660"
    assert comp[0]["market_cap_raw"] == 1697657033.0


def test_parse_industry_name():
    from lib.kr_data_sources import parse_industry_name
    name = parse_industry_name(_load("naver_industry_278.json"))
    assert name == "반도체와반도체장비"
