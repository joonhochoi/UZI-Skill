"""kr_data_sources · DART OpenAPI 파서 (Phase 2).

fixture(tests/fixtures/kr/dart_*.json) 기반 순수 파서 검증.
네트워크/키 없이 동작 — DART 응답 파싱/정규화만 테스트.

ground-truth (삼성전자 corp_code 00126380, 2024 사업보고서 11011, CFS):
- 매출액 300,870,903,000,000원 → 3,008,709.03 억원
- 영업이익 32,725,961,000,000원 → 327,259.61 억원
- 최대주주 삼성생명보험㈜ 8.51%, 보통주 508,157,148
- 임원 9명, 한종희 부회장(대표이사)
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


# ─── 원 → 억원 변환 ─────────────────────────────────────────────────
def test_dart_won_to_eok():
    from lib.kr_data_sources import _dart_won_to_eok
    assert _dart_won_to_eok("300870903000000") == 3008709.03
    assert _dart_won_to_eok("1,234,500,000") == 12.35   # 콤마 허용
    assert _dart_won_to_eok("-5000000000000") == -50000.0
    assert _dart_won_to_eok("-") is None
    assert _dart_won_to_eok(None) is None


# ─── 재무 (fnlttSinglAcntAll) ────────────────────────────────────────
def test_parse_dart_finance_core_accounts_in_eok():
    from lib.kr_data_sources import parse_dart_finance
    out = parse_dart_finance(_load("dart_finance_005930.json"))
    assert out["revenue"] == 3008709.03
    assert out["operating_profit"] == 327259.61
    assert out["net_profit"] == 344513.51
    assert out["total_assets"] == 5145319.48
    assert out["total_liabilities"] == 1123398.78
    assert out["total_equity"] == 4021920.70


def test_parse_dart_finance_has_3yr_series():
    from lib.kr_data_sources import parse_dart_finance
    out = parse_dart_finance(_load("dart_finance_005930.json"))
    rev = out["accounts"]["revenue"]
    assert rev["current"] == 3008709.03
    assert rev["prev"] == 2589354.94   # 258,935,494,000,000 / 1e8
    assert rev["prev2"] is not None


def test_parse_dart_finance_derived_ratios():
    from lib.kr_data_sources import parse_dart_finance
    out = parse_dart_finance(_load("dart_finance_005930.json"))
    # 부채비율 = 부채/자본*100 = 1123398.78/4021920.70*100 ≈ 27.93
    assert out["debt_ratio"] == 27.93
    # 순이익률 = 순이익/매출*100 = 344513.51/3008709.03*100 ≈ 11.45
    assert out["net_margin"] == 11.45


# ─── 최대주주 (hyslrSttus) ──────────────────────────────────────────
def test_parse_dart_shareholders():
    from lib.kr_data_sources import parse_dart_shareholders
    out = parse_dart_shareholders(_load("dart_major_shareholders_005930.json"))
    assert len(out) >= 1
    top = out[0]
    assert top["name"] == "삼성생명보험㈜"
    assert top["ratio"] == 8.51
    assert top["shares"] == 508157148.0


# ─── 임원 (exctvSttus) ──────────────────────────────────────────────
def test_parse_dart_executives():
    from lib.kr_data_sources import parse_dart_executives
    out = parse_dart_executives(_load("dart_executives_005930.json"))
    assert len(out) >= 9
    assert out[0]["name"] == "한종희"
    assert out[0]["position"] == "부회장"
    assert "대표이사" in out[0]["job"]


# ─── 공시 (list) ────────────────────────────────────────────────────
def test_parse_dart_disclosures():
    from lib.kr_data_sources import parse_dart_disclosures
    out = parse_dart_disclosures(_load("dart_list_005930.json"))
    assert len(out) >= 1
    d0 = out[0]
    assert d0["date"]
    assert d0["title"] == d0["title"].strip()    # trailing space 제거
    assert d0["rcept_no"] in d0["url"]
    assert d0["url"].startswith("http")


# ─── corpCode.xml 파싱 (종목코드 → corp_code) ───────────────────────
def test_parse_dart_majorstock():
    """대량보유(5%+) 보고 → 고유 보고자별 최신 지분율."""
    from lib.kr_data_sources import parse_dart_majorstock
    out = parse_dart_majorstock(_load("dart_majorstock_005930.json"))
    assert len(out) >= 1
    top = out[0]
    assert top["name"] == "삼성물산"
    assert top["ratio"] == 19.7      # fixture 최신 보고(2026-05-22) 기준
    assert top.get("date")


def test_to_governance_dim_includes_major_holders():
    from lib.kr_data_sources import (parse_dart_shareholders, parse_dart_executives,
                                     parse_dart_majorstock, to_governance_dim)
    sh = parse_dart_shareholders(_load("dart_major_shareholders_005930.json"))
    ex = parse_dart_executives(_load("dart_executives_005930.json"))
    mh = parse_dart_majorstock(_load("dart_majorstock_005930.json"))
    dim = to_governance_dim(sh, ex, major_holders=mh)
    assert len(dim["major_holders"]) >= 1
    assert dim["major_holders"][0]["name"] == "삼성물산"


def test_parse_corp_code_xml_maps_listed_only():
    from lib.kr_data_sources import parse_corp_code_xml
    xml = (
        "<result>"
        "<list><corp_code>00126380</corp_code><corp_name>삼성전자</corp_name>"
        "<stock_code>005930</stock_code><modify_date>20260101</modify_date></list>"
        "<list><corp_code>00999999</corp_code><corp_name>비상장회사</corp_name>"
        "<stock_code> </stock_code><modify_date>20260101</modify_date></list>"
        "<list><corp_code>00164779</corp_code><corp_name>SK하이닉스</corp_name>"
        "<stock_code>000660</stock_code><modify_date>20260101</modify_date></list>"
        "</result>"
    )
    m = parse_corp_code_xml(xml)
    assert m["005930"] == "00126380"
    assert m["000660"] == "00164779"
    assert " " not in m            # 비상장(빈 stock_code) 제외
    assert len(m) == 2
