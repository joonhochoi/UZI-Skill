# 한국 주식(K) 지원 추가 — 변경 작업 전수 기록

> 이 문서는 원래 **중국 A주 / 홍콩(H) / 미국(U)** 만 지원하던 분석 파이프라인에
> **한국(K, 코스피·코스닥)** 을 추가하면서 한 모든 변경을 **코드 단위**로 정리한다.
> "원래 코드가 요구하던 값 → K에서는 어떤 URL/소스에서 어떤 파일을 받아 → 그중 어떤 값을
> 어떻게 가공해 사용했는가" 를 차원별 테이블로 남겨, 추후 오류 추적·보완의 기준점으로 삼는다.
>
> 작성 기준 커밋: `e35e7c4` (feat/korea-market-support). 작업 커밋 범위: `1f849f1`(Phase1) ~ `e35e7c4`(Phase8).

---

## 0. 핵심 설계 원칙

### D8 — 중국어 출력부 비침습 (가장 중요)
기존 A/H/U(중국어) 코드 경로는 **바이트 단위로 보존**한다. 한국어는 항상 **별도 분기/출력부**로 추가한다.
- 게이트: `ti.market == "K"` (데이터 단계) 또는 `get_language() == "ko"` (렌더 단계).
- `UZI_LANG` 미설정 시 `get_language()` 기본값은 `"zh"` → 비K 경로는 기존과 동일하게 동작.
- 원본(upstream) 코드가 갱신돼도 병합이 쉽도록, 기존 dict/함수를 수정하지 않고 `_KO` 접미사 병렬 dict를 신설.

### 티커 라우팅 (lib/market_router.py)
| 입력 | 시장 | 비고 |
|---|---|---|
| 순수 6자리 `005930` | **K 우선** | 구 A주 기본값에서 변경 |
| `005930.KS` / `247540.KQ` | K | 코스피/코스닥 명시 |
| `600519.A` | A | A주는 `.A` 명시 필요 (`_a_share_suffix`로 SZ/SH/BJ 추론) |
| `600519.SH` / `00700.HK` 등 | A/H/U | 명시 접미사가 항상 최우선 |

- `Market = Literal["A", "H", "U", "K"]` (L12)
- `_RE_KR_FULL = ^(\d{6})\.(KS|KQ)$`, `_RE_A_DOTA = ^(\d{6})\.A$`
- `is_korean_name()` — 가-힣(U+AC00–U+D7A3) 포함 시 한글명으로 판단(이름→코드 해석 분기).

### 시장 추론 버그 수정 (lib/stock_features.py L393-407)
파이프라인 raw ticker는 `005930`처럼 접미사가 없어, 접미사 기반 추론 시 US로 오판하는 버그가 있었다.
→ `raw["market"]`(parse_ticker가 박아둔 A/H/U/K)를 **우선** 사용하도록 수정.
```python
_MKT_MAP = {"A":"A","H":"HK","U":"US","K":"K","HK":"HK","US":"US"}
_rm = raw.get("market")
if _rm in _MKT_MAP: f["market"] = _MKT_MAP[_rm]   # 우선
else: ...접미사 fallback
```

---

## 1. 데이터 소스 카탈로그

### 1-A. 네이버 증권 신 API (인증 불필요, lib/kr_data_sources.py)
헤더: `User-Agent`(모바일) + `Referer: https://m.stock.naver.com/`.
네트워크는 `_raw_get(url) -> (status, text)` 한 곳으로 격리(테스트는 이걸 monkeypatch). 잘못된 경로는 200 + HTML 에러페이지를 반환하므로 `_get_json`에서 첫 문자 `[`/`{` 검증 후 None.

| 베이스 상수 | URL | 받는 내용 | 쓰는 차원 |
|---|---|---|---|
| `_BASE_M` | `m.stock.naver.com/api/stock/{code}/integration` | totalInfos(현재가/PER/PBR/시총/EPS), industryCompareInfo(동종), 컨센서스 목표가·투자의견 | 0_basic, 4_peers, 6_research, 10_valuation |
| `_BASE_M` | `…/{code}/basic` | 거래소 타입, 종목 부가정보 | 0_basic 보조 |
| `_BASE_M` | `…/{code}/finance/annual` `…/quarter` | rowList(매출/순이익/ROE/부채비율/**PER/PBR** 연·분기 시계열) | 1_financials, 10_valuation(분위) |
| `_BASE_M` | `…/{code}/trend` | 외국인·기관 일별 순매수(거래원) | 12_capital_flow |
| `_BASE_M` | `…/{code}/price?pageSize=…` | 일별 시세(보조) | 2_kline 보조 |
| `_BASE_M` | `m.stock.naver.com/api/stocks/industry/{industryCode}` | groupInfo.name(업종명) + 구성 종목 | 7_industry, 4_peers |
| `_BASE_CHART` | `api.stock.naver.com/chart/domestic/item/{code}/day` | OHLCV(float 대량) | 2_kline |
| `_BASE_NEWS` | `m.stock.naver.com/api/news/stock/{code}` | 종목 뉴스 | 15_events, 17_sentiment |
| `_BASE_RESEARCH` | `m.stock.naver.com/api/research/stock/{code}` | 증권사 리포트(제목/증권사/목표가) | 6_research |
| `_BASE_AC` | `ac.stock.naver.com/ac?q={name}&target=stock` | 이름→코드 자동완성 | 종목명 해석 |

### 1-B. DART OpenAPI (DART_APIKEY 필요 · .env, gitignore)
키 로딩: `lib/env_loader.py`(`load_dotenv_once`) → `_dart_key()`. 키 없으면 모든 DART 함수는 graceful({}/[]/"" 반환).

| 엔드포인트 | 받는 내용 | 쓰는 차원 | 래퍼 함수 |
|---|---|---|---|
| `corpCode.xml` (zip) | 종목코드(6) → 고유 corp_code(8) 매핑 | 전 DART 진입 | `dart_corp_code_map` / `dart_corp_code` |
| `fnlttSinglAcntAll.json` | 단일회사 전체 재무제표 | (재무 보조) | `dart_financials` |
| `hyslrSttus.json` | 최대주주 현황 | 11_governance | `dart_major_shareholders` |
| `exctvSttus.json` | 임원 현황 | 11_governance | `dart_executives` |
| `majorstock.json` | 대량보유(5%+) 상황 | 11_governance | `dart_major_holders` |
| `list.json` | 공시 목록 / 정기보고서(사업보고서) | 15_events, 5_chain | `dart_disclosures` / `dart_latest_business_rcept` |
| `document.xml` (zip) | 사업보고서 본문(메인 xml, ~8MB) | 5_chain | `dart_document_main_xml` |

---

## 2. 22차원 변경 테이블 (핵심)

각 행: **원래(A주)가 요구/사용하던 값 → K 소스(URL) → 받는 값 → 추출·가공 → 결과 필드**.
라우팅은 `lib/data_sources.py`(공통 진입) 또는 각 `fetch_*.py`의 `ti.market == "K"` 분기에서 분기한다.

### 0_basic — 종목 기본정보
- **원래**: akshare `stock_individual_info_em` 등(종목명/시총/PER/업종)
- **K 분기**: `data_sources.fetch_basic` L308 → `naver_basic_combined(code)`
- **소스**: `…/integration` + `…/basic` + 업종 lookup(`…/stocks/industry/{code}`)
- **받는 값**: 종목명, 현재가, 시총("2,005조 2,736억" 문자열), PER_ttm, PBR, EPS, 컨센서스 PER/EPS/목표가, 업종코드
- **가공**: `_parse_market_cap_to_eok("2,005조 2,736억") → 20,052,736`(억원, `market_cap_yi`) · 업종코드→업종명 lookup
- **결과 필드**: name, price, market_cap(₩표시), market_cap_yi, pe_ttm, pb, eps, industry, market="K", currency="KRW"

### 1_financials — 재무
- **원래**: akshare 재무 시계열
- **K 분기**: `fetch_financials` → `data_sources` L1234 → `naver_finance(code,"annual"/"quarter")` → `to_financials_dim`
- **소스**: `…/finance/annual` `…/finance/quarter`
- **받는 값**: rowList 매트릭스(항목×기간) — 매출/영업이익/순이익/ROE/순이익률/부채비율
- **가공**: `parse_finance` 가 매트릭스를 연도별 시계열로 전치, 3년 추출(`roe_history`/`revenue_history`/`net_profit_history`), `revenue_growth` 계산
- **결과 필드**: roe, net_margin, roe_history[3], revenue_history[3], net_profit_history[3], financial_years, financial_health.debt_ratio

### 2_kline — 캔들
- **원래**: akshare kline(qfq)
- **K 분기**: `fetch_kline` → `data_sources` L894 → `naver_chart_ohlcv(code, start, end, "day")`
- **소스**: `api.stock.naver.com/chart/domestic/item/{code}/day`
- **받는 값**: 일별 OHLCV(float)
- **가공**: `parse_chart` 정규화 → 표준 캔들 dict 리스트
- **결과 필드**: 표준 OHLCV(이후 기술지표·stage 계산은 공통 로직 재사용)

### 3_macro — 거시환경
- **원래**: `search_trusted`로 중국 거시(인민은행/위안화/중미관계) 검색
- **K 분기**: `fetch_macro` `get_language()=="ko"` → **한국어 쿼리**(한국은행 기준금리/원달러 환율/미국 연준/지정학 리스크 북한/원자재 반도체 소재) + 일반 `search`
- **소스**: 웹검색(ddgs, region=kr-ko)
- **가공**: snippet 수집(자유 텍스트). 정량 휴리스틱은 score_fns autofill(한국어)이 보조
- **결과 필드**: rate_cycle/us_rate/fx_trend/geo_risk/commodity/industry_macro snippet

### 4_peers — 동종 비교
- **원래**: akshare 동종 종목
- **K 분기**: `fetch_peers` K → `naver_integration`(industryCompareInfo) + 각 peer `naver_integration`로 PER/PBR enrich → `to_peers_dim`
- **소스**: `…/integration` (industryCompareInfo)
- **받는 값**: 동종 종목명/코드/시총(marketValue, **백만원**), 각 종목 PER/PBR
- **가공**: ① 시총 단위 통일 — `marketValue(백만원) ÷ 100 → 억원`(self의 market_cap_yi와 동일 시맨틱) · ② 시총 정렬 후 순위 산출(삼성전자 반도체 1위) · ③ **PER 이상치 필터 `0 < pe ≤ 150`**(적자·극단 고PER 제외 → 평균 왜곡 방지)
- **결과 필드**: peer_table[{name,code,market_cap_yi,pe,pb,is_self}], rank, peer_median_pe, peer_avg_pe

### 5_chain — 밸류체인(상·하류) [Phase8]
- **원래**: 同花顺 `stock_zyjs_ths`(중국 주영업무 소개) → 上游/下游 추정
- **K 분기**: `fetch_chain` K → `dart_business(code)` → DART 사업보고서 본문 파싱
- **소스**: `list.json`(최신 **사업보고서** rcept_no) → `document.xml`(zip, 메인 본문 ~8MB) → "II. 사업의 내용"
- **받는 값**: 주요제품 표(사업부문|매출유형|품목|구체적용도|매출액(비율)), 원재료 표(…|품목|구체적용도|투입액|비율)
- **가공**: `parse_dart_business` — 본문(목차 아닌 마지막 매치) 슬라이스 후 `<TABLE>/<TR>/<TD>` 파싱. products=품목, downstream=구체적용도, main_business_breakdown=사업부문:매출액(비율), upstream=원재료 영문 품목(용도어 Fab/Package/Module 제외)
- **결과 필드(SK하이닉스 실측)**: products="DRAM, NAND Flash 등", upstream="WAFER, Substrate, PCB", downstream="산업용 전자기기", main_business_breakdown=["반도체 부문: 97,146,675(100%)"]
- **미구현**: client/supplier_concentration("—", 매출처/매입처 집중도 표 후속)

### 6_research — 증권사 리서치
- **원래**: akshare 증권사 리포트/평점
- **K 분기**: `fetch_research` K → `naver_research` + `naver_integration`(컨센서스) → `to_research_dim`
- **소스**: `…/research/stock/{code}` + `…/integration`
- **받는 값**: 리포트(제목/증권사/목표가), 컨센서스 목표가·투자의견(cnsPer 등)
- **가공**: `_extract_rating`(네이버는 평점 필드 부재 → 텍스트 추출), `buy_rating_pct`, `target_avg`(컨센서스 우선, ₩콤마). 렌더 호환 위해 `coverage_count`/`coverage`, `rating` 별칭 양쪽 채움
- **결과 필드**: report_count, coverage_count/coverage, target_price_avg/target_avg, rating_distribution, buy_rating_pct, consensus_recomm

### 6_fund_holders — 공모펀드 보유 [graceful]
- **원래**: akshare 공모펀드 보유(중국 명성 매니저)
- **K**: **무료 API 부재** → graceful skip. `fetch_fund_holders` `_note`(한국어) + 렌더(`render_fund_managers`/`FundRenderer`)에서 **"한국 시장 · 공모펀드 보유 현황은 무료 API 미제공으로 미지원 (DART 5%+ 대량보유는 거버넌스 항목 참고)"** 명시 표기
- **대안**: DART majorstock(5%+ 대량보유)이 11_governance에 일부 반영

### 7_industry — 업종 분석
- **원래**: `search_trusted`(중국 권위 도메인) + 하드코딩 업종 TAM(¥…亿)
- **K 분기**: `fetch_industry` ko → **한국어 쿼리**(업황/시장규모/사이클) + 일반 `search`(중국 권위 도메인 회피) + `naver_industry_name`(업종명)
- **소스**: `…/stocks/industry/{code}` + 웹검색(kr-ko)
- **가공**: 한국어 정규식 — growth `성장률 X%`, TAM `X조원·X억원→₩`, penetration `침투율 X%`, lifecycle `성장기/성숙기/쇠퇴기/업황 호조`(中 단위 `亿`/`生命周期` 의존 제거)
- **결과 필드**: 업종명, growth_heuristic, tam_heuristic(₩), penetration_heuristic, lifecycle_heuristic

### 8_materials — 원자재
- **원래**: akshare commodity + autofill
- **K**: 전용 분기 없음. score_fns autofill(`_autofill_qualitative_via_mx`)이 **한국어 쿼리**("{name} 주요 원자재 원가 구조 핵심 소재")로 ddgs 보충. (반도체 종목엔 약한 차원)

### 9_futures — 연관 선물 [graceful]
- **원래**: akshare 선물 + `INDUSTRY_FUTURES`(중국 업종→선물 매핑)
- **K**: 중국 업종 매핑이라 K 업종은 매칭 0 → graceful. `fetch_futures` ko → "직접 연관 선물 상품 없음" + "{industry} 업종은 선물시장과 강하게 연관된 상품이 없음"

### 10_valuation — 밸류에이션 [Phase7+]
- **원래**: akshare baidu `stock_zh_valuation_baidu`(PE 5년) + cninfo 업종 PE
- **K 분기**: `fetch_valuation` K(4곳) → `naver_integration`(현재 PER/PBR) + `naver_pe_pb_series`(시계열) + 간이 DCF
- **소스**: `…/integration` + `…/finance/annual|quarter`(PER/PBR rowList)
- **받는 값**: 현재 PER_ttm/PBR, PER/PBR 연·분기 시계열(양수만)
- **가공**: ① 분위 — `현재값 < 시계열` 비율 백분위(SK PER 26.7→89분위·고평가) · ② 라벨 "최근 PER N분위"(中 "5 年 N 分位" → K) · ③ DCF — WACC 8.5%·터미널 2.0%(A주 10%/3%와 다름), 표시 `₩…조`(中 `¥…亿` → K)
- **결과 필드**: pe, pe_quantile("최근 PER N분위"), pb_quantile, dcf("₩864.7조"), dcf_simple, dcf_sensitivity
- **미연결**: industry_pe(업종 PE 평균, A주는 cninfo)

### 11_governance — 지배구조 [DART]
- **원래**: akshare 거버넌스(최대주주/임원/질권)
- **K 분기**: `fetch_governance` K → `dart_corp_code` → `dart_major_shareholders` + `dart_executives` + `dart_major_holders` → `to_governance_dim`
- **소스**: DART `hyslrSttus` + `exctvSttus` + `majorstock`
- **받는 값**: 최대주주(이름/지분/주식수), 임원(이름/직위/담당), 대량보유 5%+(보고자별 최신 지분)
- **가공**: `parse_dart_*`. 한국은 질권(pledge) 공개 제도가 달라 `pledge=[]`(점수 로직 호환)
- **결과 필드**: actual_controller, top_shareholder_ratio, shareholders[], executives_count, major_holders[], pledge=[]

### 12_capital_flow — 자금 흐름
- **원래**: akshare 주력 순유입/북향자금(중국 특유)
- **K 분기**: `fetch_capital_flow` → `naver_trend` → `to_capital_flow_dim`
- **소스**: `…/{code}/trend` (거래원 일별)
- **받는 값**: 외국인·기관 일별 순매수
- **가공**: **외국인+기관 → "주력(主力)" 으로 매핑**(중국 主力净流入 자리에), 20일 시계열, 외국인 보유율
- **결과 필드**: main_fund_flow_20d, foreign_hold_ratio_latest

### 13_policy — 정책·규제
- **원래**: `search_trusted`(중국 国家政策/监管)
- **K 분기**: `fetch_policy` ko → **한국어 쿼리**(정부정책 지원 육성 / 보조금 세제 K칩스법 / 규제 감독 / 공정거래위원회 담합)
- **소스**: 웹검색(kr-ko, search_trusted는 ko에서 일반 search로 우회)

### 14_moat — 해자
- **원래**: `search_trusted` + 중국어 `pos_kws`(龙头/第一/垄断)
- **K 분기**: `fetch_moat` ko → **한국어 쿼리**(`{name} 주식` 앵커) + **한국어 점수 키워드**(특허/핵심기술/독점/락인/장기계약/플랫폼/생태계/1위/점유율)
- **소스**: 웹검색(kr-ko)

### 15_events — 이벤트·공시
- **원래**: akshare 뉴스 + 공시
- **K 분기**: `fetch_events` K → `naver_news` + DART `dart_disclosures` → `to_events_dim`
- **소스**: `…/news/stock/{code}` + DART `list.json`
- **받는 값**: 종목 뉴스, 정기/수시 공시(제목/접수번호/URL)
- **가공**: `parse_news`, `parse_dart_disclosures`(trailing space 제거, rcept_no→URL)
- **결과 필드**: news_count, recent_news[], disclosures_count, recent_notices[]

### 16_lhb — 거래대금 상위(龙虎榜) [graceful]
- **원래**: akshare 龙虎榜(중국 A주 전용 제도)
- **K**: `fetch_lhb` `ti.market != "A"` → graceful. K는 "거래대금 상위 매매주체 공시는 중국 A주 전용 제도 · 한국 시장 미지원"

### 17_sentiment — 여론·심리
- **원래**: 중국 플랫폼(雪球/股吧/知乎/小红书) + 중국어 키워드(看好/涨停/利好)
- **K 분기**: `fetch_sentiment` K → **한국 플랫폼**(네이버 금융 종목토론, 네이버 블로그, 유튜브, 디시/fmkorea, 전문가 의견) + **한국어 키워드**(호재/강세/상한가/매수 vs 악재/하락/손절/하한가)
- **소스**: 웹검색(kr-ko) site:finance.naver.com 등
- **가공**: 긍/부정 단어 카운트 → positive_pct, 감정 단어 0개면 "中性"(오'비관' 방지)

### 18_trap — 작전주/리스크 탐지
- **원래**: 중국 杀猪盘 8신호(必涨/老师带单/VIP直播)
- **K 분기**: `fetch_trap_signals` ko → **`SIGNALS_KO` 8신호**(리딩방/단톡방, 유튜브/텔레그램 오픈채팅, 관리종목/상장폐지, 작전 주가조작, 주식고수 수익인증, 허위 리포트) + ko level(🟢안전~🔴매우 의심)·권고문
- **소스**: 웹검색(kr-ko)

### 19_contests — 실전대회 [graceful]
- **원래**: 중국 실전투자대회(雪球 cubes/淘股吧 实盘大赛)
- **K**: `fetch_contests` K → graceful 미지원. "한국 시장은 중국 실전투자대회(실전 포트폴리오 랭킹) 데이터를 지원하지 않습니다"

---

## 3. 데이터 가공·단위 변환 규칙 (lib/kr_data_sources.py)

| 함수 | 입력 → 출력 | 용도 |
|---|---|---|
| `_parse_kr_number` | "1,234.5"/"−"/"%" 등 정제 → float\|None | 모든 네이버 숫자 |
| `_parse_market_cap_to_eok` | "2,005조 2,736억" → 20,052,736 (**억원**) | 시총(`market_cap_yi`, 중국 `亿` 시맨틱 호환) |
| `_dart_won_to_eok` | "300870903000000"(원) → 3,008,709.03 (**억원**, ÷1e8) | DART 재무 금액 |
| `_format_market_cap_kr` | 억원 → "X조 Y억"(₩표시) | 시총 표시 |
| `to_peers_dim` 내부 | `marketValue(백만원) ÷ 100` → 억원 | peer 시총 단위 통일(순위 정확성) |
| `_extract_target_price` / `_extract_rating` | 리포트 텍스트 → 목표가/평점 | 네이버 비정형 평점 |

**핵심 단위 시맨틱**: 중국 `亿`(1e8) ↔ 한국 `억원`(1e8) 은 같은 자릿수라 `market_cap_yi` 필드를 그대로 재사용. 표시만 `localize_ko`가 `亿→억`, `¥→₩`, `万亿→조` 후처리.

---

## 4. 정성 차원 검색 인프라 (lib/web_search.py)

중국 검색 노이즈(K 종목 리포트에 中 발改委 정책·中 기사가 섞이는 문제)를 근본 차단. 모두 `get_language()=="ko"` 게이트.

| 변경 | 내용 |
|---|---|
| region | `search()` K 모드 시 ddgs region `cn-zh`→**`kr-ko`** + region별 캐시 키 분리 |
| `_drop_cjk_heavy` | 결과 중 **한글 없고 한자 dominant**(중국어 기사)를 drop (한국 기사·영문은 보존, 전부 drop 시 원본 유지) |
| `search_trusted` ko 가드 | K는 중국 권위 도메인 `site:` 필터를 쓰지 않고 일반 `search`(한국어 쿼리)로 우회 |
| autofill (score_fns `_autofill_qualitative_via_mx`) | 6개 정성차원 보충 query 템플릿을 **한국어화** + **MX(중국 妙想 API) K 비활성**(ddgs만 사용) |

---

## 5. 출력 한국어화 (D8 별도 출력부)

`UZI_LANG=ko`(K 종목 자동 설정) 시 적용. 데이터 단계는 ko 분기, 최종 HTML은 `localize_ko` 후처리.

| 위치 | 내용 |
|---|---|
| `lib/report/locale_ko.py` `_ZH_TO_KO` (**1,249 항목**) | 중→한 라벨 사전(길이 내림차순 치환). 통화 `¥→₩`, 단위 `亿→억`/`万亿→조`, UI 라벨, 면책조항, 미치환 f-string `{var:.0f}`→"—" |
| `lib/investor_personas.py` `PERSONAS_KO`(66) | 평가위원 페르소나 대사 한국어 병렬부. `get_comment` lang 분기 + 괄호 한자 병기 strip |
| `lib/investor_criteria.py` `KO_MSGS`/`NAME_KO` | 규칙 메시지·규칙 이름 한국어 매핑 |
| `lib/investor_profile.py` `PROFILES_KO`(28)+`GROUP_DEFAULT_KO`(9) | 평가위원 투자철학(time_horizon/position_sizing/what_would_change_my_mind) |
| `lib/report/dim_viz.py` `_viz_valuation`/`_viz_research` | 밸류 게이지·PE밴드 범례, 리서치 도넛(매수/중립/매도) ko |
| `lib/report/special_cards.py` | 평가위원 패널 집계(看多→매수 등), `render_fund_managers` K 미지원 표기 |
| `lib/pipeline/score_fns.py` | 평가위원 verdict/skip, punchline/risks, Bull-Bear 토론, 시나리오 rationale, 밸류 label/reasons ko |
| `lib/pipeline/renderer/*` (research/chain/fund) | 섹션 라벨 ko |
| `lib/report/compute_friendly.py` `compute_exit_triggers` | 청산 신호 ko(동적 가격 `₩{ma60:,.0f}`) |

**회고(중요 교훈)**: 초기 LLM 대량 번역은 길이/맥락 증가 시 언어 타깃을 벗어나 한중 혼용을 남겼다. 이후 모든 위임 번역에 **CJK=0 자동 검증**(`[一-鿿]` 카운트 0 확인·재시도)을 강제. 동적 자연어를 후처리 사전으로 메우는 방식은 무한 확장되므로 지양하고, 생성 소스를 ko 분기하는 것이 정답.

---

## 6. 시장별 graceful (A주 전용 차원의 K 처리)

| 차원 | 이유 | K 처리 |
|---|---|---|
| 6_fund_holders | 무료 API 부재 | "무료 API 미제공 미지원" 명시 |
| 9_futures | 중국 업종→선물 매핑 | "직접 연관 선물 없음" |
| 16_lhb | 龙虎榜 = 중국 A주 전용 제도 | "중국 A주 전용 · 한국 미지원" |
| 19_contests | 중국 실전대회 | "중국 실전투자대회 미지원" |
| F조 게이지(游资 24명) | `MARKET_SCOPE` scope="A" | reality_check가 K 종목에서 자동 skip |

---

## 7. 테스트 (tests/, hermes pytest 또는 bash python 3.14)

- `tests/test_kr_*.py` — market_router, env_loader, naver 파서, DART 파서, dim 변환, features, investor, locale, **parse_pe_pb_series**(밸류 분위), **parse_dart_business**(5_chain)
- `tests/fixtures/kr/` — 실제 네이버/DART 응답 JSON(네트워크 의존 제거). DART 키는 fixture에 절대 미포함
- **환경 주의**: hermes venv(3.11)는 akshare/pandas 없음 → akshare import하는 fetch_* 테스트는 baseline 실패(내 변경 무관). `institutional.py`는 3.11 f-string 비호환. 순수 파서/locale 테스트는 GREEN
- **RTK 프록시 주의**: 한국어 mojibake로 pytest 출력이 "No tests collected"로 깨짐 → hermes `pytest.exe` 직접 실행

---

## 8. 실행 방법

```bash
python run.py 005930 --depth medium --no-browser   # 코스피(자동 K, UZI_LANG=ko)
python run.py 000660 --depth deep   --no-browser    # 코스닥은 .KQ, 또는 6자리
python run.py 삼성전자 ...                            # 한글명 → naver_search 해석
```
- K 종목은 `UZI_LANG=ko` 자동 설정 + 종료 단계 `localize_ko` 후처리.
- `--no-resume` 강제 재추출(없으면 `.cache/{ticker}/raw_data.json` 재사용).

---

## 9. 알려진 한계 / 후속 과제

| 항목 | 상태 |
|---|---|
| industry_pe(업종 PE 평균) | K 소스 미연결(A주는 cninfo). 네이버 동종/업종 집계로 보강 여지 |
| 5_chain 고객/공급사 집중도 | DART 매출처/매입처 집중도 표 파싱 후속(제품/원재료/매출비중은 완료) |
| 6_fund_holders 실데이터 | 에프앤가이드/제로인 유료 연동 시 가능(현재 graceful) |
| 밸류 분위 정밀도 | 네이버 finance는 연·분기 ~10포인트(일별 5년 밴드 아님). 근사 |
| agent_analysis 런타임 CJK 가드 | deep role-play 산출물 한자 혼용 가능 → 렌더 전 가드 미적용 |
| 잔여 단일 한자(~56) | 차트/disclaimer 조사·단위·인명 단편. 매핑 시 오치환 위험으로 보류 |

---

## 10. 변경 파일 인덱스 (커밋 `1f849f1`~`e35e7c4`)

- **라우팅/추론**: `lib/market_router.py`, `lib/stock_features.py`, `lib/pipeline/run.py`(market whitelist에 K)
- **데이터 소스**: `lib/kr_data_sources.py`(신설·최대), `lib/data_sources.py`(K 라우팅), `lib/env_loader.py`, `lib/data_source_registry.py`(9 K DataSource 등록)
- **fetcher**: fetch_basic/financials/kline/valuation/capital_flow/governance/events/research/peers/industry/chain/macro/policy/moat/sentiment/trap_signals/futures/lhb/contests/fund_holders
- **검색 인프라**: `lib/web_search.py`, `lib/pipeline/score_fns.py`(autofill)
- **한국어화**: `lib/report/locale_ko.py`, `lib/report/dim_viz.py`, `lib/report/special_cards.py`, `lib/report/compute_friendly.py`, `lib/pipeline/renderer/{research,chain,fund}.py`, `lib/investor_personas.py`, `lib/investor_criteria.py`, `lib/investor_profile.py`, `lib/investor_evaluator.py`
- **설정/문서**: `.env`(DART_APIKEY, gitignore), `run.py`(--market, UZI_LANG=ko auto), `CLAUDE_KR.md`/`AGENTS_KR.md`/`README_KR.md`, `need_info_type.md`(네이버 API 명세), `new_dev_plan.md`(Phase 로드맵 + 1~8차 후속)
- **테스트**: `tests/test_kr_*.py`, `tests/fixtures/kr/`
