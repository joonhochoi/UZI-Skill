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


# ─── 사업보고서 '사업의 내용' → 밸류체인(5_chain) ────────────────────
def test_parse_dart_business():
    from lib.kr_data_sources import parse_dart_business
    xml = (
        "II. 사업의 내용 ... 1. 사업의 개요 ... 2. 주요 제품 및 서비스 "
        "<TABLE><TR><TD>사업부문</TD><TD>매출유형</TD><TD>품목</TD>"
        "<TD>구체적용도</TD><TD>주요상표등</TD><TD>매출액(비율)</TD></TR>"
        "<TR><TD>반도체 부문</TD><TD>제품 외</TD><TD>DRAM, NAND Flash 등</TD>"
        "<TD>산업용 전자기기</TD><TD>SK하이닉스</TD><TD>97,146,675(100%)</TD></TR>"
        "<TR><TD>합계</TD><TD>97,146,675(100%)</TD></TR></TABLE>"
        " ... 3. 원재료 및 생산설비 "
        "<TABLE><TR><TD>사업부문</TD><TD>매입유형</TD><TD>품목</TD>"
        "<TD>구체적용도</TD><TD>투입액</TD><TD>비율</TD></TR>"
        "<TR><TD>반도체</TD><TD>원재료</TD><TD>WAFER</TD><TD>Fab</TD>"
        "<TD>1,024,285</TD><TD>7%</TD></TR>"
        "<TR><TD>Substrate</TD><TD>Package</TD><TD>418,856</TD><TD>3%</TD></TR></TABLE>"
    )
    r = parse_dart_business(xml)
    assert r["products"] == "DRAM, NAND Flash 등"
    assert "산업용 전자기기" in r["downstream"]
    assert "WAFER" in r["upstream"]
    assert "Substrate" in r["upstream"]
    assert "Fab" not in r["upstream"]          # 용도어 제외
    assert "Package" not in r["upstream"]
    assert any("반도체" in b for b in r["main_business_breakdown"])


def test_parse_dart_business_empty_safe():
    from lib.kr_data_sources import parse_dart_business
    out = parse_dart_business("")
    assert out["products"] == "—" and out["main_business_breakdown"] == []
    assert out["client_concentration"] == "—"
    assert out["supplier_concentration"] == "—"


# ─── 5_chain 고객/공급사 집중도 (IFRS 8 주요 고객 + 매입처 서술) ─────────
def test_dart_client_concentration_quantified():
    """IFRS 8 '10%+ 단일 고객' 공시 → 당기 금액만 백만원→조원 환산."""
    from lib.kr_data_sources import _dart_client_concentration
    xml = (
        "주요 고객에 대한 정보 당기 중 단일 외부고객으로부터의 매출액이 "
        "연결회사 전체 매출액의 10%를 상회하는 고객 (가)로부터 발생한 매출액은 "
        "23,260,076백만원이며, 전기 중 단일 외부고객으로부터의 매출액이 연결회사 "
        "전체 매출액의 10%를 상회하는 고객 (가)로부터 발생한 매출액은 10,902,817백만원입니다."
    )
    out = _dart_client_concentration(xml)
    assert "10%" in out
    assert "가" in out
    assert "₩23.3조" in out          # 23,260,076 백만원 → 23.26조 (당기)
    assert "10,902,817" not in out   # 전기 금액은 제외


def test_dart_client_concentration_none_when_absent():
    from lib.kr_data_sources import _dart_client_concentration
    assert _dart_client_concentration("아무 관련 없는 본문 텍스트") == "—"


def test_dart_supplier_concentration_descriptive():
    from lib.kr_data_sources import _dart_supplier_concentration
    xml = (
        "주요 원재료의 매입처 및 원재료 공급시장과 공급의 안정성 "
        "당사는 일본, 한국, 독일, 미국 등에 생산시설을 보유한 업계의 주요 공급사로부터 "
        "반도체 공정의 원자재인 300mm 웨이퍼 완제품을 공급받고 있습니다. 웨이퍼 가격은 ..."
    )
    out = _dart_supplier_concentration(xml)
    assert "당사는" in out
    assert "공급사" in out
    assert "..." not in out          # 헤더/꼬리 잡설 제외, 첫 문장만


def test_parse_dart_business_includes_concentration():
    from lib.kr_data_sources import parse_dart_business
    xml = (
        "II. 사업의 내용 "
        "주요 고객에 대한 정보 당기 중 단일 외부고객으로부터의 매출액이 전체 매출액의 "
        "10%를 상회하는 고객 (가)로부터 발생한 매출액은 23,260,076백만원입니다. "
        "나. 주요 원재료의 매입처 당사는 한국, 일본 공급사로부터 웨이퍼를 공급받고 있습니다."
    )
    r = parse_dart_business(xml)
    assert "가" in r["client_concentration"]
    assert "공급사" in r["supplier_concentration"]
