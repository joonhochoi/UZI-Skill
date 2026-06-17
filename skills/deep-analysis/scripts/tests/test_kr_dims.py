"""kr_data_sources · 차원(dimension) shape 변환 (Phase 4).

네이버/DART 정규화 출력 → 리포트 viz 가 기대하는 차원 스키마로 변환하는
순수 함수들. fetcher(fetch_financials/events/governance)는 이들을 얇게 호출.
akshare 무관 → hermes pytest 로 단위 테스트 가능.
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


# ─── 1_financials ───────────────────────────────────────────────────
def test_to_financials_dim():
    from lib.kr_data_sources import parse_finance, to_financials_dim
    ann = parse_finance(_load("naver_finance_annual_005930.json"), "annual")
    dim = to_financials_dim(ann)
    assert dim["roe"] == "10.85%"
    assert dim["net_margin"] == "13.55%"
    assert dim["roe_history"] == [4.15, 9.03, 10.85]
    assert dim["revenue_history"] == [2589355.0, 3008709.0, 3336059.0]
    assert dim["net_profit_history"][-1] > 0
    assert dim["financial_years"] == ["2023", "2024", "2025"]
    assert dim["revenue_growth"] == "+10.88%"
    assert dim["financial_health"]["debt_ratio"] == 29.94


def test_to_financials_dim_empty_safe():
    from lib.kr_data_sources import to_financials_dim
    dim = to_financials_dim({})
    assert isinstance(dim, dict)
    assert dim.get("roe_history") == []


# ─── 12_capital_flow ────────────────────────────────────────────────
def test_to_capital_flow_dim():
    from lib.kr_data_sources import parse_trend, to_capital_flow_dim
    rows = parse_trend(_load("naver_trend_005930.json"))
    dim = to_capital_flow_dim(rows)
    # 외국인+기관을 "주력"으로 매핑
    assert "main_fund_flow_20d" in dim
    assert len(dim["main_fund_flow_20d"]) > 0
    assert "主力净流入-净额" in dim["main_fund_flow_20d"][0]
    assert "foreign_hold_ratio_latest" in dim


# ─── 15_events ──────────────────────────────────────────────────────
def test_to_events_dim():
    from lib.kr_data_sources import parse_news, to_events_dim
    news = parse_news(_load("naver_news_005930.json"))
    disclosures = [
        {"date": "20260608", "title": "최대주주등소유주식변동신고서",
         "rcept_no": "20260608800918", "url": "http://dart...", "filer": "삼성전자"},
    ]
    dim = to_events_dim(news, disclosures)
    assert dim["news_count"] >= 1
    assert len(dim["recent_news"]) >= 1
    assert dim["recent_news"][0]["title"]
    assert dim["disclosures_count"] == 1
    assert len(dim["recent_notices"]) == 1
    assert dim["recent_notices"][0]["title"] == "최대주주등소유주식변동신고서"


# ─── 11_governance ──────────────────────────────────────────────────
def test_to_governance_dim():
    from lib.kr_data_sources import (parse_dart_shareholders, parse_dart_executives,
                                     to_governance_dim)
    sh = parse_dart_shareholders(_load("dart_major_shareholders_005930.json"))
    ex = parse_dart_executives(_load("dart_executives_005930.json"))
    dim = to_governance_dim(sh, ex)
    assert dim["actual_controller"]            # 최대주주 본인 이름
    assert dim["top_shareholder_ratio"] == 8.51
    assert len(dim["shareholders"]) >= 1
    assert dim["executives_count"] >= 9
    # 한국엔 질권(pledge) 공개 제도 다름 → 빈 리스트 (점수 로직 호환)
    assert dim["pledge"] == []


# ─── 4_peers (Phase 7) ──────────────────────────────────────────────
def test_to_peers_dim():
    from lib.kr_data_sources import parse_integration, to_peers_dim
    inte = parse_integration(_load("naver_integration_005930.json"))
    dim = to_peers_dim(inte["industry_compare"], self_code="005930",
                       self_name="삼성전자", self_mcap_raw=20052736.0,
                       industry="반도체와반도체장비")
    pt = dim["peer_table"]
    assert len(pt) >= 2
    # 자기 자신 포함 + is_self 플래그
    selfrow = [p for p in pt if p.get("is_self")]
    assert len(selfrow) == 1 and selfrow[0]["code"] == "005930"
    # 동종 종목 포함
    assert any(p["name"] == "SK하이닉스" for p in pt)
    assert dim["industry"] == "반도체와반도체장비"


# ─── 6_research consensus (Phase 7) ─────────────────────────────────
def test_parse_integration_consensus():
    from lib.kr_data_sources import parse_integration
    out = parse_integration(_load("naver_integration_005930.json"))
    assert out["consensus_price_target"] == 443750.0
    assert out["consensus_recomm"] == 4.04


def test_to_research_dim_consensus_target_priority():
    from lib.kr_data_sources import parse_research, to_research_dim
    res = parse_research(_load("naver_research_005930.json"))
    dim = to_research_dim(res, consensus_target=443750.0, consensus_recomm=4.04)
    assert dim["report_count"] >= 1
    assert dim["target_price_avg"] == 443750.0     # consensus 우선
    assert dim["consensus_recomm"] == 4.04
