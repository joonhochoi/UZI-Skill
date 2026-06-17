"""한국(K) 데이터 소스 · 네이버 증권 신 API + DART OpenAPI 래퍼 · Phase 2.

설계 (hk_data_sources.py 패턴 그대로):
- 함수는 dict/list 또는 빈 컨테이너를 반환하고 **절대 raise 하지 않는다**. 에러는 `_err` 키.
- 네트워크는 `_raw_get(url,...) -> (status, text)` 한 곳으로 격리 → 테스트는 이걸 monkeypatch.
- 응답 → 내부 raw_data 스키마 정규화를 **이 모듈에서 완결**(콤마/억원/조/"배"/% 파싱).
- 네이버 신 API는 유효하지 않은 경로에 대해 200 OK + HTML 에러페이지를 주므로
  `_get_json` 이 첫 비공백 문자가 '[' / '{' 인지 확인해 HTML 을 걸러낸다.

엔드포인트 (need_info_type.md 보완 섹션 참고, 2026-06-16 실측):
- m.stock.naver.com/api/stock/{code}/integration  → 0_basic + 10_valuation + 12_capital_flow
-                                /basic            → 시세 + 거래소(KS/KQ) + 통화
-                                /finance/annual|quarter → 1_financials (다음 단계)
-                                /trend            → 12_capital_flow (외국인/기관/개인)
-                                /price            → 2_kline (일별, 콤마 문자열)
- api.stock.naver.com/chart/domestic/item/{code}/day → 2_kline (float OHLCV 대량)
- m.stock.naver.com/api/news/stock/{code}       → 15_events / 17_sentiment
- m.stock.naver.com/api/research/stock/{code}   → 6_research (증권사 리포트 + 목표가)
- ac.stock.naver.com/ac                          → 이름→코드 검색
"""
from __future__ import annotations

import io
import json
import os
import re
import urllib.parse
import zipfile
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - requests 는 akshare 의존이라 보통 존재
    requests = None


# ═══════════════════════════════════════════════════════════════
# 네트워크 (격리 · 테스트는 _raw_get 을 monkeypatch)
# ═══════════════════════════════════════════════════════════════
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
_HEADERS = {"User-Agent": _UA, "Referer": "https://m.stock.naver.com/"}

_BASE_M = "https://m.stock.naver.com/api/stock"
_BASE_CHART = "https://api.stock.naver.com/chart/domestic/item"
_BASE_NEWS = "https://m.stock.naver.com/api/news/stock"
_BASE_RESEARCH = "https://m.stock.naver.com/api/research/stock"
_BASE_AC = "https://ac.stock.naver.com/ac"


def _raw_get(url: str, headers: dict | None = None, timeout: int = 15) -> tuple[int | None, str]:
    """단일 네트워크 진입점. (status_code, text) 반환. 실패 시 (None, "")."""
    if requests is None:
        return (None, "")
    try:
        r = requests.get(url, headers=headers or _HEADERS, timeout=timeout)
        return (r.status_code, r.text or "")
    except Exception:
        return (None, "")


def _get_json(url: str, headers: dict | None = None, timeout: int = 15) -> Any | None:
    """GET + JSON 검증. 네이버는 잘못된 경로에 200+HTML 을 주므로 첫 문자로 거른다."""
    status, text = _raw_get(url, headers, timeout)
    if status != 200 or not text:
        return None
    t = text.lstrip()
    if not t or t[0] not in "[{":
        return None
    try:
        return json.loads(t)
    except (ValueError, json.JSONDecodeError):
        return None


# ═══════════════════════════════════════════════════════════════
# 숫자/단위 파싱 헬퍼 (순수 함수)
# ═══════════════════════════════════════════════════════════════
def _parse_kr_number(s: Any) -> float | None:
    """'27.52배' → 27.52 · '1,668원' → 1668 · '0.49%' → 0.49 · '+531,697' → 531697.

    '-' 단독 / 빈값 / None → None. 부호(+/-)는 유지.
    """
    if s is None:
        return None
    t = str(s).strip()
    if not t or t == "-":
        return None
    t = (t.replace(",", "").replace("배", "").replace("원", "")
          .replace("%", "").replace(" ", ""))
    try:
        return float(t)
    except ValueError:
        return None


def _parse_market_cap_to_eok(s: Any) -> float | None:
    """'2,005조 2,736억' → 20,052,736 (억원 단위 · 기존 market_cap_yi=亿 시맨틱)."""
    if s is None:
        return None
    t = str(s).strip()
    if not t or t == "-":
        return None
    t = t.replace(",", "").replace(" ", "")
    jo = re.search(r"([\d.]+)조", t)
    eok = re.search(r"([\d.]+)억", t)
    if jo or eok:
        total = 0.0
        if jo:
            total += float(jo.group(1)) * 10000
        if eok:
            total += float(eok.group(1))
        return total
    # 단위 표기가 없으면 순수 숫자(이미 억원으로 가정)
    try:
        return float(t)
    except ValueError:
        return None


def _extract_target_price(text: str | None) -> float | None:
    """리포트 미리보기 텍스트에서 목표주가 추출. '55만원' → 550000 · '550,000원' → 550000."""
    if not text:
        return None
    m = re.search(r"목표주가[^0-9]{0,6}([\d,]+)\s*만\s*원", text)
    if m:
        return float(m.group(1).replace(",", "")) * 10000
    m = re.search(r"목표주가[^0-9]{0,6}([\d,]+)\s*원", text)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


def _norm_deal_trend_row(r: dict) -> dict:
    """integration.dealTrendInfos / trend 의 한 행을 정규화 (외국인/기관/개인 순매수)."""
    return {
        "date": r.get("bizdate"),
        "foreign_net": _parse_kr_number(r.get("foreignerPureBuyQuant")),
        "org_net": _parse_kr_number(r.get("organPureBuyQuant")),
        "individual_net": _parse_kr_number(r.get("individualPureBuyQuant")),
        "foreign_hold_ratio": _parse_kr_number(r.get("foreignerHoldRatio")),
        "close": _parse_kr_number(r.get("closePrice")),
    }


# ═══════════════════════════════════════════════════════════════
# 네이버 응답 파서 (순수 함수 · fixture 로 단위 테스트)
# ═══════════════════════════════════════════════════════════════
def parse_integration(raw: dict) -> dict:
    """integration → 0_basic + 10_valuation + 컨센서스 + 투자자별 순매수."""
    out: dict[str, Any] = {}
    if not isinstance(raw, dict):
        return out
    out["name"] = raw.get("stockName")
    out["code"] = raw.get("itemCode")
    ti = {x.get("code"): x.get("value") for x in (raw.get("totalInfos") or [])}
    out["pe_ttm"] = _parse_kr_number(ti.get("per"))
    out["pb"] = _parse_kr_number(ti.get("pbr"))
    out["eps"] = _parse_kr_number(ti.get("eps"))
    out["bps"] = _parse_kr_number(ti.get("bps"))
    out["dividend_yield"] = _parse_kr_number(ti.get("dividendYieldRatio"))
    out["dividend_per_share"] = _parse_kr_number(ti.get("dividend"))
    out["consensus_pe"] = _parse_kr_number(ti.get("cnsPer"))
    out["consensus_eps"] = _parse_kr_number(ti.get("cnsEps"))
    out["market_cap_yi"] = _parse_market_cap_to_eok(ti.get("marketValue"))
    out["foreign_hold_ratio"] = _parse_kr_number(ti.get("foreignRate"))
    out["year_high_52w"] = _parse_kr_number(ti.get("highPriceOf52Weeks"))
    out["year_low_52w"] = _parse_kr_number(ti.get("lowPriceOf52Weeks"))
    out["deal_trend"] = [_norm_deal_trend_row(r) for r in (raw.get("dealTrendInfos") or [])]
    # 컨센서스 (목표주가 평균 / 투자의견 평균)
    ci = raw.get("consensusInfo") or {}
    out["consensus_price_target"] = _parse_kr_number(ci.get("priceTargetMean"))
    out["consensus_recomm"] = _parse_kr_number(ci.get("recommMean"))
    # 업종/동종 (industryCode → 업종명 lookup, industryCompareInfo → peers)
    out["industry_code"] = raw.get("industryCode")
    out["industry_compare"] = [{
        "name": x.get("stockName"),
        "code": x.get("itemCode"),
        "market_cap_raw": _parse_kr_number(x.get("marketValue")),
    } for x in (raw.get("industryCompareInfo") or []) if isinstance(x, dict)]
    return out


def parse_basic(raw: dict) -> dict:
    """basic → 시세 + 거래소(KS/KQ) + 통화. 순수 6자리 K 의 실제 거래소를 여기서 확정."""
    out: dict[str, Any] = {}
    if not isinstance(raw, dict):
        return out
    out["name"] = raw.get("stockName")
    out["code"] = raw.get("itemCode")
    out["price"] = _parse_kr_number(raw.get("closePrice"))
    out["change_pct"] = _parse_kr_number(raw.get("fluctuationsRatio"))
    ex = raw.get("stockExchangeType") or {}
    code = ex.get("code")  # "KS" | "KQ"
    out["exchange"] = code
    out["exchange_name"] = raw.get("stockExchangeName") or ex.get("nameKor")
    out["market_suffix"] = ".KS" if code == "KS" else ".KQ" if code == "KQ" else ""
    out["currency"] = "KRW" if ex.get("nationCode") == "KOR" else None
    out["market_status"] = raw.get("marketStatus")
    return out


def parse_trend(raw: list) -> list[dict]:
    """trend → 일별 외국인/기관/개인 순매수 (12_capital_flow)."""
    if not isinstance(raw, list):
        return []
    return [_norm_deal_trend_row(r) for r in raw]


def parse_research(raw: list) -> dict:
    """research → 6_research. 목표가는 previewContent 에서 추출 (구조화 필드 아님)."""
    out: dict[str, Any] = {"report_count": 0, "coverage_count": 0, "recent_reports": [], "target_price_avg": None}
    if not isinstance(raw, list):
        return out
    brokers: set[str] = set()
    reports: list[dict] = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        broker = r.get("brokerName")
        if broker:
            brokers.add(broker)
        reports.append({
            "date": r.get("writeDate"),
            "title": r.get("title"),
            "broker": broker,
            "target_price": _extract_target_price(r.get("previewContent")),
            "read_count": _parse_kr_number(r.get("readCount")),
        })
    out["report_count"] = len(reports)
    out["coverage_count"] = len(brokers)
    out["recent_reports"] = reports
    tps = [x["target_price"] for x in reports if x["target_price"]]
    out["target_price_avg"] = round(sum(tps) / len(tps), 1) if tps else None
    return out


def parse_news(raw: list) -> list[dict]:
    """news → 15_events / 17_sentiment. 응답은 [{items:[...]}, ...] 중첩 구조."""
    out: list[dict] = []
    if not isinstance(raw, list):
        return out
    for block in raw:
        if not isinstance(block, dict):
            continue
        items = block.get("items")
        if items is None and block.get("title"):
            items = [block]
        for it in (items or []):
            out.append({
                "date": it.get("datetime"),
                "title": it.get("titleFull") or it.get("title"),
                "source": it.get("officeName"),
                "url": it.get("mobileNewsUrl") or "",
                "summary": it.get("body", ""),
            })
    return out


def parse_price_history(raw: list) -> list[dict]:
    """price → 일별 OHLCV (콤마 문자열을 숫자로). 2_kline."""
    out: list[dict] = []
    if not isinstance(raw, list):
        return out
    for r in raw:
        if not isinstance(r, dict):
            continue
        out.append({
            "date": r.get("localTradedAt"),
            "open": _parse_kr_number(r.get("openPrice")),
            "high": _parse_kr_number(r.get("highPrice")),
            "low": _parse_kr_number(r.get("lowPrice")),
            "close": _parse_kr_number(r.get("closePrice")),
            "volume": _parse_kr_number(r.get("accumulatedTradingVolume")),
        })
    return out


def parse_chart(raw: list) -> list[dict]:
    """chart/domestic → float OHLCV + 외국인보유율 (대량). 2_kline 지표 계산용 주 소스."""
    out: list[dict] = []
    if not isinstance(raw, list):
        return out
    for r in raw:
        if not isinstance(r, dict):
            continue
        try:
            out.append({
                "date": str(r.get("localDate")),
                "open": float(r.get("openPrice")),
                "high": float(r.get("highPrice")),
                "low": float(r.get("lowPrice")),
                "close": float(r.get("closePrice")),
                "volume": float(r.get("accumulatedTradingVolume") or 0),
                "foreign_hold_ratio": r.get("foreignRetentionRate"),
            })
        except (TypeError, ValueError):
            continue
    return out


# finance rowList 의 한국어 title → 내부 필드명
_FIN_FIELD_MAP = {
    "매출액": "revenue",
    "영업이익": "operating_profit",
    "당기순이익": "net_profit",
    "지배주주순이익": "net_profit_owner",
    "영업이익률": "operating_margin",
    "순이익률": "net_margin",
    "ROE": "roe",
    "부채비율": "debt_ratio",
    "당좌비율": "quick_ratio",
    "유보율": "reserve_ratio",
    "EPS": "eps",
    "BPS": "bps",
    "PER": "per",
    "PBR": "pbr",
    "주당배당금": "dps",
}


def _finance_period_label(key: str, period_type: str) -> str:
    """'202312' → annual:'2023' · quarter:'2023Q4'."""
    key = str(key or "")
    if period_type == "annual":
        return key[:4]
    y, mm = key[:4], key[4:6]
    q = {"03": "Q1", "06": "Q2", "09": "Q3", "12": "Q4"}.get(mm, mm)
    return f"{y}{q}"


def parse_finance(raw: dict, period_type: str = "annual") -> dict:
    """finance/annual|quarter 매트릭스(rowList×columns) → 시계열 (1_financials).

    - 확정 기간(isConsensus != 'Y')만 *_history 시계열로 (연/분기 오름차순).
    - 컨센서스 기간(Y)은 out['consensus'][기간라벨][필드] 로 분리.
    - 금액 단위는 억원(네이버 원본), 비율은 %.
    """
    out: dict[str, Any] = {
        "period_type": period_type, "periods": [], "consensus_periods": [],
        "series": {}, "consensus": {},
    }
    if not isinstance(raw, dict):
        return out
    fi = raw.get("financeInfo") or {}
    tr = fi.get("trTitleList") or []
    confirmed = sorted([t for t in tr if t.get("isConsensus") != "Y"], key=lambda t: str(t.get("key")))
    consensus = sorted([t for t in tr if t.get("isConsensus") == "Y"], key=lambda t: str(t.get("key")))
    conf_keys = [t.get("key") for t in confirmed]
    out["periods"] = [_finance_period_label(t.get("key"), period_type) for t in confirmed]
    out["consensus_periods"] = [_finance_period_label(t.get("key"), period_type) for t in consensus]

    rows = {r.get("title"): (r.get("columns") or {}) for r in (fi.get("rowList") or [])}
    for title, field in _FIN_FIELD_MAP.items():
        cols = rows.get(title)
        if not cols:
            continue
        out["series"][field] = [_parse_kr_number((cols.get(k) or {}).get("value")) for k in conf_keys]
        for t in consensus:
            plabel = _finance_period_label(t.get("key"), period_type)
            val = _parse_kr_number((cols.get(t.get("key")) or {}).get("value"))
            out["consensus"].setdefault(plabel, {})[field] = val

    s = out["series"]
    out["revenue_history"] = s.get("revenue", [])
    out["net_profit_history"] = s.get("net_profit", [])
    out["operating_profit_history"] = s.get("operating_profit", [])
    out["roe_history"] = s.get("roe", [])
    out["net_margin_history"] = s.get("net_margin", [])

    def _latest(field: str) -> float | None:
        vals = [v for v in s.get(field, []) if v is not None]
        return vals[-1] if vals else None

    out["roe"] = _latest("roe")
    out["net_margin"] = _latest("net_margin")
    out["operating_margin"] = _latest("operating_margin")
    out["debt_ratio"] = _latest("debt_ratio")
    out["eps"] = _latest("eps")
    out["bps"] = _latest("bps")
    out["dps"] = _latest("dps")

    rev = [v for v in s.get("revenue", []) if v is not None]
    if len(rev) >= 2 and rev[-2]:
        out["revenue_growth_pct"] = round((rev[-1] - rev[-2]) / rev[-2] * 100, 2)
    return out


def parse_search(raw: dict) -> list[dict]:
    """ac 자동완성 → 이름→코드 후보. 한국(KOR) stock 만."""
    out: list[dict] = []
    if not isinstance(raw, dict):
        return out
    for it in (raw.get("items") or []):
        if not isinstance(it, dict):
            continue
        if it.get("nationCode") != "KOR":
            continue
        if it.get("category") not in (None, "stock"):
            continue
        tc = it.get("typeCode", "") or ""
        exchange = "KOSPI" if "KOSPI" in tc else "KOSDAQ" if "KOSDAQ" in tc else tc
        out.append({
            "code": it.get("code"),
            "name": it.get("name"),
            "market": "K",
            "exchange": exchange,
        })
    return out


# ═══════════════════════════════════════════════════════════════
# 네이버 fetch 함수 (네트워크 + 파서 조합 · 절대 raise 안 함)
# ═══════════════════════════════════════════════════════════════
def naver_integration(code6: str) -> dict:
    raw = _get_json(f"{_BASE_M}/{code6}/integration")
    return parse_integration(raw) if raw else {}


def naver_basic(code6: str) -> dict:
    raw = _get_json(f"{_BASE_M}/{code6}/basic")
    return parse_basic(raw) if raw else {}


def _format_market_cap_kr(yi: float | None) -> str | None:
    """억원 수치 → 한국식 표시 ('20052736' → '2,005조')."""
    if yi is None:
        return None
    if yi >= 10000:
        jo = yi / 10000
        return f"{jo:,.0f}조" if jo >= 100 else f"{jo:,.1f}조"
    return f"{yi:,.0f}억"


def merge_basic(inte: dict, basic: dict) -> dict:
    """integration + basic → 0_basic 스키마 (순수 조합). 거래소/통화는 basic 우선."""
    out: dict[str, Any] = {"market": "K"}
    for k, v in (inte or {}).items():
        if v is not None:
            out[k] = v
    for k in ("name", "price", "change_pct", "exchange", "market_suffix",
              "currency", "exchange_name", "market_status", "code"):
        v = (basic or {}).get(k)
        if v is not None:
            out[k] = v
    if out.get("market_cap_yi") is not None:
        out["market_cap"] = _format_market_cap_kr(out["market_cap_yi"])
    return out


def parse_industry_name(raw: dict) -> str | None:
    """stocks/industry/{code} 응답의 groupInfo.name (업종명)."""
    if not isinstance(raw, dict):
        return None
    g = raw.get("groupInfo") or {}
    return g.get("name")


def naver_industry_name(industry_code) -> str | None:
    """업종코드 → 업종명. (예: 278 → '반도체와반도체장비')"""
    if not industry_code:
        return None
    raw = _get_json(f"{_BASE_M}s/industry/{industry_code}?page=1&pageSize=1")
    return parse_industry_name(raw) if raw else None


def naver_basic_combined(code6: str) -> dict:
    """integration + basic 네트워크 조합 → 0_basic dict. 절대 raise 안 함.

    업종코드가 있으면 업종명까지 lookup 해 industry 필드를 채운다(综合 fallback 방지).
    """
    out = merge_basic(naver_integration(code6), naver_basic(code6))
    ic = out.get("industry_code")
    if ic and not out.get("industry"):
        nm = naver_industry_name(ic)
        if nm:
            out["industry"] = nm
    return out


def naver_trend(code6: str) -> list[dict]:
    raw = _get_json(f"{_BASE_M}/{code6}/trend")
    return parse_trend(raw) if raw else []


def naver_finance(code6: str, period: str = "annual") -> dict:
    """period: 'annual' | 'quarter'."""
    raw = _get_json(f"{_BASE_M}/{code6}/finance/{period}")
    return parse_finance(raw, period_type=period) if raw else {}


def naver_price_history(code6: str, size: int = 120) -> list[dict]:
    raw = _get_json(f"{_BASE_M}/{code6}/price?pageSize={size}&page=1")
    return parse_price_history(raw) if raw else []


def naver_chart_ohlcv(code6: str, start: str, end: str, period: str = "day") -> list[dict]:
    raw = _get_json(f"{_BASE_CHART}/{code6}/{period}?startDateTime={start}&endDateTime={end}")
    return parse_chart(raw) if raw else []


def naver_news(code6: str, size: int = 30) -> list[dict]:
    raw = _get_json(f"{_BASE_NEWS}/{code6}?pageSize={size}&page=1")
    return parse_news(raw) if raw else []


def naver_research(code6: str, size: int = 30) -> dict:
    raw = _get_json(f"{_BASE_RESEARCH}/{code6}?pageSize={size}&page=1")
    return parse_research(raw) if raw else {}


def naver_search(name: str) -> list[dict]:
    q = urllib.parse.quote(name)
    raw = _get_json(f"{_BASE_AC}?q={q}&target=stock&st=111")
    return parse_search(raw) if raw else []


# ═══════════════════════════════════════════════════════════════
# DART OpenAPI · 지배구조 / 정밀재무 / 공시 (네이버 신 API 미커버 영역)
# ═══════════════════════════════════════════════════════════════
_DART_BASE = "https://opendart.fss.or.kr/api"

# fnlttSinglAcntAll 의 표준 account_id → 내부 필드 (account_nm 보다 견고)
_DART_ACCT = {
    "ifrs-full_Revenue": "revenue",
    "dart_OperatingIncomeLoss": "operating_profit",
    "ifrs-full_ProfitLoss": "net_profit",
    "ifrs-full_Assets": "total_assets",
    "ifrs-full_Liabilities": "total_liabilities",
    "ifrs-full_Equity": "total_equity",
}


def _dart_won_to_eok(s: Any) -> float | None:
    """DART 금액(원, 콤마 가능) → 억원. '300870903000000' → 3008709.03."""
    v = _parse_kr_number(s)
    return round(v / 1e8, 2) if v is not None else None


def _dart_key() -> str:
    """DART 인증키. lib 레벨 .env 로더로 단독 실행/pytest 에서도 잡히게."""
    try:
        from .env_loader import load_dotenv_once
        load_dotenv_once()
    except Exception:
        pass
    return os.environ.get("DART_APIKEY", "")


# ─── DART 응답 파서 (순수 · fixture 테스트) ──────────────────────────
def parse_dart_finance(raw: dict) -> dict:
    """fnlttSinglAcntAll → 핵심 계정(억원) + 3개년 시계열 + 파생비율.

    account_id 로 매칭(IS/BS 우선, CIS 중복은 skip). thstrm/frmtrm/bfefrmtrm =
    당기/전기/전전기.
    """
    out: dict[str, Any] = {"status": None, "accounts": {}}
    if not isinstance(raw, dict):
        return out
    out["status"] = raw.get("status")
    accounts: dict[str, dict] = {}
    for r in raw.get("list", []):
        if not isinstance(r, dict):
            continue
        field = _DART_ACCT.get(r.get("account_id"))
        if not field or field in accounts:
            continue
        if r.get("sj_div") not in ("IS", "BS", "CIS"):
            continue
        accounts[field] = {
            "current": _dart_won_to_eok(r.get("thstrm_amount")),
            "prev": _dart_won_to_eok(r.get("frmtrm_amount")),
            "prev2": _dart_won_to_eok(r.get("bfefrmtrm_amount")),
        }
    out["accounts"] = accounts

    def _cur(f: str) -> float | None:
        return (accounts.get(f) or {}).get("current")

    for f in ("revenue", "operating_profit", "net_profit",
              "total_assets", "total_liabilities", "total_equity"):
        out[f] = _cur(f)

    if out["total_equity"] and out["total_liabilities"] is not None:
        out["debt_ratio"] = round(out["total_liabilities"] / out["total_equity"] * 100, 2)
    if out["revenue"] and out["net_profit"] is not None:
        out["net_margin"] = round(out["net_profit"] / out["revenue"] * 100, 2)
    return out


def parse_dart_shareholders(raw: dict) -> list[dict]:
    """hyslrSttus → 최대주주 및 특수관계인 [{name, relation, shares, ratio}]."""
    out: list[dict] = []
    if not isinstance(raw, dict):
        return out
    for r in raw.get("list", []):
        if not isinstance(r, dict):
            continue
        out.append({
            "name": r.get("nm"),
            "relation": r.get("relate"),
            "shares": _parse_kr_number(r.get("bsis_posesn_stock_co")),
            "ratio": _parse_kr_number(r.get("bsis_posesn_stock_qota_rt")),
        })
    return out


def parse_dart_executives(raw: dict) -> list[dict]:
    """exctvSttus → 임원 현황 [{name, position, job, birth}]."""
    out: list[dict] = []
    if not isinstance(raw, dict):
        return out
    for r in raw.get("list", []):
        if not isinstance(r, dict):
            continue
        out.append({
            "name": r.get("nm"),
            "position": r.get("ofcps"),
            "job": (r.get("chrg_job") or "").strip(),
            "birth": r.get("birth_ym"),
        })
    return out


def parse_dart_disclosures(raw: dict) -> list[dict]:
    """list → 공시 [{date, title, rcept_no, filer, url}]."""
    out: list[dict] = []
    if not isinstance(raw, dict):
        return out
    for r in raw.get("list", []):
        if not isinstance(r, dict):
            continue
        rno = r.get("rcept_no")
        out.append({
            "date": r.get("rcept_dt"),
            "title": (r.get("report_nm") or "").strip(),
            "rcept_no": rno,
            "filer": r.get("flr_nm"),
            "url": f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rno}" if rno else "",
        })
    return out


def parse_corp_code_xml(xml_text: str) -> dict[str, str]:
    """corpCode.xml → {stock_code: corp_code} (상장사만 · 빈 stock_code 제외)."""
    import xml.etree.ElementTree as ET
    mapping: dict[str, str] = {}
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return mapping
    for e in root.iter("list"):
        sc = (e.findtext("stock_code") or "").strip()
        cc = (e.findtext("corp_code") or "").strip()
        if sc and cc:
            mapping[sc] = cc
    return mapping


# ─── DART fetch 함수 (네트워크 · 키 필요 · 절대 raise 안 함) ─────────
_CORP_MAP_CACHE: dict[str, str] | None = None


def dart_corp_code_map(force: bool = False) -> dict[str, str]:
    """corpCode.xml(zip) 다운로드 → {종목코드: corp_code}. 메모리 캐시.

    키 없거나 네트워크 실패 시 빈 dict (graceful). zip ~3.5MB / xml ~30MB.
    """
    global _CORP_MAP_CACHE
    if _CORP_MAP_CACHE is not None and not force:
        return _CORP_MAP_CACHE
    key = _dart_key()
    if not key or requests is None:
        _CORP_MAP_CACHE = {}
        return _CORP_MAP_CACHE
    try:
        r = requests.get(f"{_DART_BASE}/corpCode.xml", params={"crtfc_key": key}, timeout=30)
        if r.status_code != 200 or not r.content:
            _CORP_MAP_CACHE = {}
            return _CORP_MAP_CACHE
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            name = next((n for n in zf.namelist() if n.lower().endswith(".xml")), None)
            xml_text = zf.read(name).decode("utf-8") if name else ""
        _CORP_MAP_CACHE = parse_corp_code_xml(xml_text)
    except Exception:
        _CORP_MAP_CACHE = {}
    return _CORP_MAP_CACHE


def dart_corp_code(stock_code6: str) -> str | None:
    """6자리 종목코드 → 8자리 corp_code (없으면 None)."""
    return dart_corp_code_map().get(stock_code6)


def _dart_get(endpoint: str, params: dict) -> dict | None:
    key = _dart_key()
    if not key or requests is None:
        return None
    try:
        p = {"crtfc_key": key, **params}
        r = requests.get(f"{_DART_BASE}/{endpoint}", params=p, timeout=20)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def dart_financials(corp_code: str, year: str | int, reprt_code: str = "11011",
                    fs_div: str = "CFS") -> dict:
    raw = _dart_get("fnlttSinglAcntAll.json", {
        "corp_code": corp_code, "bsns_year": str(year),
        "reprt_code": reprt_code, "fs_div": fs_div,
    })
    return parse_dart_finance(raw) if raw else {}


def dart_major_shareholders(corp_code: str, year: str | int, reprt_code: str = "11011") -> list[dict]:
    raw = _dart_get("hyslrSttus.json", {
        "corp_code": corp_code, "bsns_year": str(year), "reprt_code": reprt_code,
    })
    return parse_dart_shareholders(raw) if raw else []


def dart_executives(corp_code: str, year: str | int, reprt_code: str = "11011") -> list[dict]:
    raw = _dart_get("exctvSttus.json", {
        "corp_code": corp_code, "bsns_year": str(year), "reprt_code": reprt_code,
    })
    return parse_dart_executives(raw) if raw else []


def dart_disclosures(corp_code: str, bgn_de: str | None = None, count: int = 30) -> list[dict]:
    if not bgn_de:
        from datetime import datetime, timedelta
        bgn_de = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
    params: dict[str, Any] = {"corp_code": corp_code, "bgn_de": bgn_de, "page_count": count}
    raw = _dart_get("list.json", params)
    return parse_dart_disclosures(raw) if raw else []


# ═══════════════════════════════════════════════════════════════
# 차원(dimension) shape 변환 · Phase 4 (순수 함수 · fetcher 가 얇게 호출)
# 리포트 viz / score_fns 가 기대하는 키로 정규화 출력을 매핑한다.
# ═══════════════════════════════════════════════════════════════
def _pct(v: float | None) -> str | None:
    return f"{v}%" if v is not None else None


def to_financials_dim(annual: dict) -> dict:
    """parse_finance(annual) → 1_financials 차원 스키마."""
    annual = annual or {}
    s = annual.get("series", {}) or {}
    _clean = lambda xs: [v for v in (xs or []) if v is not None]
    rg = annual.get("revenue_growth_pct")
    out: dict[str, Any] = {
        "roe": _pct(annual.get("roe")),
        "net_margin": _pct(annual.get("net_margin")),
        "roe_history": _clean(s.get("roe")),
        "revenue_history": _clean(s.get("revenue")),
        "net_profit_history": _clean(s.get("net_profit")),
        "net_margin_history": _clean(s.get("net_margin")),
        "financial_years": annual.get("periods", []),
        "eps": annual.get("eps"),
        "bps": annual.get("bps"),
        "revenue_growth": (f"+{rg}%" if rg is not None and rg >= 0
                           else (f"{rg}%" if rg is not None else None)),
        "financial_health": {
            "debt_ratio": annual.get("debt_ratio"),
            "net_margin_pct": annual.get("net_margin"),
        },
        "consensus": annual.get("consensus", {}),
    }
    return out


def to_capital_flow_dim(trend: list) -> dict:
    """parse_trend → 12_capital_flow. 외국인+기관을 '주력 순유입'으로 매핑.

    A주 score_fns 가 읽는 키('主力净流入-净额')에 맞춰 외국인+기관 순매수 합을 넣는다.
    """
    trend = trend or []
    flow: list[dict] = []
    for r in trend:
        f = r.get("foreign_net") or 0
        o = r.get("org_net") or 0
        flow.append({
            "date": r.get("date"),
            "主力净流入-净额": (f + o),         # 외국인+기관 = 주력
            "foreign_net": r.get("foreign_net"),
            "org_net": r.get("org_net"),
            "individual_net": r.get("individual_net"),
        })
    latest_ratio = None
    for r in trend:
        if r.get("foreign_hold_ratio") is not None:
            latest_ratio = r["foreign_hold_ratio"]
            break
    return {
        "main_fund_flow_20d": flow[:20],
        "foreign_hold_ratio_latest": latest_ratio,
        "northbound": {},  # 한국엔 북향자금 개념 없음 (외국인 순매수로 대체)
    }


def to_events_dim(news: list, disclosures: list) -> dict:
    """parse_news + dart_disclosures → 15_events 차원 스키마."""
    news = news or []
    disclosures = disclosures or []
    recent_news = [{
        "date": n.get("date"), "title": n.get("title"),
        "type": "news", "source": n.get("source"),
    } for n in news]
    recent_notices = [{
        "date": d.get("date"), "title": d.get("title"),
        "url": d.get("url"), "type": "disclosure",
    } for d in disclosures]
    timeline = [f"{d.get('date')} · {d.get('title')}" for d in disclosures[:10]]
    return {
        "event_timeline": timeline,
        "recent_news": recent_news,
        "news": recent_news,            # score_fns/A주 호환 별칭 (15_events 뉴스 카운트)
        "recent_notices": recent_notices,
        "news_count": len(recent_news),
        "disclosures_count": len(recent_notices),
        "catalyst": [],
        "warnings": [],
    }


def to_research_dim(research: dict, consensus_target: float | None = None,
                    consensus_recomm: float | None = None) -> dict:
    """parse_research(리포트 목록) + integration 컨센서스 → 6_research 차원.

    목표주가는 컨센서스(integration.consensusInfo)가 더 정확하므로 우선,
    없으면 parse_research 의 previewContent 텍스트 추출값(target_price_avg)을 유지.
    """
    out = dict(research or {})
    if consensus_target:
        out["target_price_avg"] = consensus_target
    out["consensus_recomm"] = consensus_recomm
    return out


def to_peers_dim(industry_compare: list, self_code: str, self_name: str,
                 self_mcap_raw: float | None = None, industry: str | None = None) -> dict:
    """integration.industry_compare(동종) + 자기자신 → 4_peers 차원 스키마.

    네이버 동종 비교는 PER/PBR 미제공 → 시가총액 기준 순위 위주(pe/pb=None).
    """
    peers: list[dict] = [{
        "name": self_name, "code": self_code, "market_cap_raw": self_mcap_raw,
        "is_self": True, "pe": None, "pb": None, "roe": None,
    }]
    for c in (industry_compare or []):
        if not isinstance(c, dict) or c.get("code") == self_code:
            continue
        peers.append({
            "name": c.get("name"), "code": c.get("code"),
            "market_cap_raw": c.get("market_cap_raw"),
            "is_self": False, "pe": None, "pb": None, "roe": None,
        })
    # NOTE: industryCompareInfo.marketValue 단위가 integration.market_cap(억원)과
    # 일치하지 않아(스케일 불명) 시총 정렬/순위는 오정보 위험 → 네이버 원본 순서 유지,
    # rank 미산출. PER/PBR 비교가 필요하면 각 peer integration 추가 호출(후속).
    return {
        "peer_table": peers,
        "peer_count": len(peers),
        "industry": industry,
        "rank": None,
    }


def to_governance_dim(shareholders: list, executives: list) -> dict:
    """dart 최대주주 + 임원 → 11_governance 차원 스키마.

    한국엔 중국식 주식 질권(质押) 일일 공개 제도가 없으므로 pledge=[] (점수 로직 호환).
    """
    shareholders = shareholders or []
    executives = executives or []
    controller = None
    top_ratio = None
    for s in shareholders:
        if s.get("relation") and "본인" in str(s.get("relation")):
            controller = s.get("name")
            top_ratio = s.get("ratio")
            break
    if controller is None and shareholders:
        controller = shareholders[0].get("name")
        top_ratio = shareholders[0].get("ratio")
    return {
        "actual_controller": controller,
        "top_shareholder_ratio": top_ratio,
        "shareholders": shareholders[:10],
        "executives": executives[:15],
        "executives_count": len(executives),
        "pledge": [],
        "insider_trades_1y": [],
        "qualitative_search": [],
    }
