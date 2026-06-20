# 한국 주식(K) 시장 지원 — 세부 개발 계획서

> 작성일: 2026-06-16 · 대상 저장소: UZI-Skill (주식 22차원 심층 분석 plugin)
> 선행 문서: [need_info_type.md](need_info_type.md)(차원별 필요 데이터 + 네이버 신 API 실측) · [AGENTS_KR.md](AGENTS_KR.md)(저장소 레이아웃)
>
> **목표**: 기존 A주(중국 본토)/H주(홍콩)/U주(미국) 3개 시장에 **K(한국 KOSPI/KOSDAQ)** 를 1급 시장으로 추가하여,
> `python run.py 005930` / `python run.py 삼성전자` 로 22차원 분석 리포트를 생성할 수 있게 한다.

---

## 0. 핵심 설계 결정 (먼저 읽을 것)

| # | 결정 | 근거 |
|---|---|---|
| D1 | 시장 토큰은 **`"K"`** 로 통일 (parse_ticker 반환), 풀티커 접미사는 `.KS`(코스피)/`.KQ`(코스닥) | 기존 A/H/U 패턴과 일관. Yahoo 접미사 관례와도 일치 |
| D1-1 | **접미사 없는 순수 6자리 = K 우선** (구 A주 기본값에서 변경). A주 명시는 **`.A` 접미사**(`600519.A`→A, 거래소는 `_a_share_suffix`로 추론) | 사용자 확정(2026-06-16) · 한국 시장 1급 제품화. ✅ **Phase 1 구현 완료** |
| D8 | 리포트 출력 **언어 기본값 = 한국어**. 단 **한국어 출력부를 별도 모듈/분기로 신설**하고 기존 중국어 출력부는 **건드리지 않음** (upstream 병합 용이) | 사용자 확정(2026-06-16) |
| D9 | **DART API 키 확보됨** → `.env`의 `DART_APIKEY` 사용, `11_governance`/공시/정밀재무 정식 연동 (graceful skip은 키 누락 폴백으로만) | 사용자 확정(2026-06-16) |
| D2 | 주 데이터 소스는 **네이버 증권 신 JSON API** (`m.stock.naver.com/api`, `api.stock.naver.com/chart`, `ac.stock.naver.com/ac`). akshare/yfinance는 **보조**로만 | 무료·무인증·구조화 JSON. need_info_type.md 보완 섹션에서 실측 검증 완료 |
| D2-1 | `11_governance`(지배구조) + 공시 원문 + 정밀 재무는 **DART OpenAPI** 병행 (API 키 필요, `.env`의 `DART_APIKEY`) | 네이버 API에 최대주주/임원/담보 없음 |
| D3 | 신 API 호출/파싱을 **`lib/kr_data_sources.py`** 단일 모듈로 격리 (HK의 `hk_data_sources.py` 패턴 그대로) | 격리 → 회귀 위험 0, 테스트 용이 |
| D4 | 중국 전용 차원은 **graceful skip**: `16_lhb`(용호방), `19_contests`(설구) 비활성. `12_capital_flow`의 북향자금 → 외국인/기관 순매수로 의미 재매핑 | 한국에 해당 제도 없음 |
| D5 | 66 심사위원 중 **F조(游资, 23명)는 K 종목에서 자동 skip** — 코드 수정 거의 불필요(기존 `market_match` 로직이 처리) | `investor_knowledge.MARKET_SCOPE`에서 F조 scope="A". K는 "A"에 매칭 안 되므로 자동 제외 |
| D6 | 통화는 **KRW(₩)**, 금액 단위는 **억원/조원**. 리포트 렌더러의 `¥`/`元` 하드코딩을 시장별 심볼로 분기 | 한국 사용자 가독성 |
| D7 | **파이프라인(pipeline/) 경로를 1급으로 지원**, legacy(stage1/stage2)는 best-effort | run.py 기본값이 pipeline (v3.0.0) |

### ⚠️ 발견된 기존 버그/주의 (작업 중 함께 처리)
- `stock_features.py:390-397` — market을 ticker 접미사로 추론하는데 `.KS`/`.KQ`가 없어 한국 종목이 **`"US"`로 오판**됨. → K 분기 추가 필수.
- `investor_knowledge.market_match`는 market 값으로 `"A"/"HK"/"US"`를 기대(주석)하지만 `parse_ticker`/`TickerInfo`는 `"A"/"H"/"U"`를 사용. `stock_features`가 `"HK"/"US"`로 정규화해 features에 넣음. **K 추가 시 이 매핑(`H`↔`HK`, `U`↔`US`)을 명시적으로 정리**하고 K는 `features["market"]="K"`, scope 비교도 `"K"`로 일관되게.

---

## 1. 영향 받는 컴포넌트 지도 (현 아키텍처 기준)

데이터 흐름: `run.py` → `pipeline.run.run_pipeline` → `pipeline.collect.collect`(22 fetcher 웨이브 실행) → 각 `fetch_*.py` → `lib/data_sources.py`(market 분기) → `pipeline.score`/`synthesize` → `assemble_report` → HTML.
병렬로 `stock_features.extract_features` → `investor_evaluator.evaluate`(66 심사위원 × reality_check).

| 레이어 | 파일 | K 작업 |
|---|---|---|
| 티커 파싱 | `lib/market_router.py` | `parse_ticker`에 K 인식, `is_korean_name`, `classify_security_type` K 분기 |
| 시장 분기 | `lib/data_sources.py` | `fetch_basic`/`fetch_kline`/`fetch_financials`/`_fetch_*_impl`에 `ti.market=="K"` 분기 |
| **신규 소스 모듈** | `lib/kr_data_sources.py` (신규) | 네이버 신 API + DART 래퍼 (HK 모듈 패턴) |
| 소스 레지스트리 | `lib/data_source_registry.py` | K DataSource 등록, `DataSource` docstring의 market 주석 갱신 |
| 22 fetcher | `fetch_*.py` ×22 | 대부분 data_sources 위임 → 자동. 직접 akshare 호출하는 것만 K 분기 |
| 파이프라인 | `lib/pipeline/fetchers/registry.py` | fetcher별 `markets` 튜플에 K, K skip 차원 처리 |
| 점수 | `lib/pipeline/score_fns.py` | `16_lhb`/`12_capital_flow` K 분기 |
| 특성 | `lib/stock_features.py` | market 추론 K 분기(버그 수정), 통화/단위 |
| 심사위원 | `lib/investor_knowledge.py` | MARKET_SCOPE 정리(K), reality_check K |
| 자가검증 | `lib/self_review.py` | K 검증 규칙(KRW/업종/lhb skip을 info로) |
| 리포트 | `lib/report/*`, `lib/pipeline/renderer/*`, `assets/report-template.html` | 통화 심볼 ₩, 라벨 한글화 |
| 업종 추정 | `lib/industry_mapping.py` | KRX(WICS/FICS) 업종 → 내부 매핑 테이블 |
| DCF 파라미터 | `fetch_valuation.py` / `compute_*` | 한국 무위험수익률/세율/ERP |

---

## 2. Phase별 구현 로드맵

> 각 Phase는 독립 PR로 머지 가능하도록 설계. Phase 1~4 완료 시 **lite depth 리포트**가 한국 종목으로 생성됨(MVP). Phase 5~7은 완성도/심층.

### Phase 1 · 티커 파싱 & 시장 식별 (★ 기반) — ✅ **완료 (2026-06-16, TDD)**

**파일**: `lib/market_router.py` · **테스트**: `tests/test_kr_market_router.py` (14) + `tests/test_no_regressions.py` 마이그레이션(4)

구현된 내용:
1. 정규식 추가: `_RE_KR_FULL = r"^(\d{6})\.(KS|KQ)$"`, `_RE_A_DOTA = r"^(\d{6})\.A$"`. `Market` Literal에 `"K"` 추가.
2. **6자리 충돌 해소 (확정 방침 D1-1)**: 명시 접미사 우선순위 → `.KS`/`.KQ`=K, `.SZ`/`.SH`/`.BJ`=A, `.A`=A(거래소 `_a_share_suffix` 추론). **접미사 없는 순수 6자리 = K**, full은 best-effort `.KS`(실제 거래소는 fetch 단계 확정).
3. `parse_ticker` 분기 순서: KR_FULL → A_FULL → A_DOTA → 순수6자리(K) → HK → US → 한자명(A 폴백).
4. `is_korean_name(raw)` 추가 — 한글 음절(U+AC00–U+D7A3) 판정. `is_chinese_name`(CJK U+4E00–U+9FFF)과 범위 비중첩이라 '삼성전자'는 한국명으로만 잡힘.
5. `classify_security_type`: 변경 없음(순수 함수, 중국 코드체계). `fetch_basic`이 `market=="A"`일 때만 호출하므로 K는 자동 "stock". 한국 ETF/ETN은 후순위.
6. **회귀 처리**: 순수 6자리→A를 단언하던 `test_no_regressions.py`의 parser 테스트 4개를 `.A` 접미사로 마이그레이션(구 계약→신 계약). LHB 테스트는 `_fetch_lhb_impl`이 market 무관하게 `ti.code`만 써서 영향 없음.

**검증 결과**: 신규 K 테스트 14 + 마이그레이션 parser 5 = **19 passed**. 전체 스위트 실패 수는 변경 전후 동일(51, 전부 pandas/akshare 미설치 환경 이슈) → **내 변경이 유발한 신규 실패 0**.

> **Phase 1에서 의도적으로 미룬 것**:
> - `run.py --market {A,H,U,K}` 강제 플래그 → 라우팅(resolve_korean_name)이 없는 현 시점엔 dead code. **Phase 3**에서 한글명 resolve와 함께 추가.
> - 네이버 `ac` 자동완성 기반 코드 존재 검증/승격 → **Phase 3**(resolve_korean_name)에서.

---

### Phase 2 · 네이버 신 API + DART 소스 모듈 (★★ 핵심) — ✅ **완료 (2026-06-16, TDD)**

**구현 결과**:
- 신규 `lib/env_loader.py` — 단독 실행/pytest 시 `.env` 로드 (`load_dotenv_from`/`load_dotenv_once`). 테스트 5.
- 신규 `lib/kr_data_sources.py` — 네이버 신 API + DART 래퍼. 네트워크는 `_raw_get` 한 곳으로 격리, `_get_json` 이 HTML 에러페이지(200+`<!doctype>`) 거름.
  - 네이버 파서 9 + fetch 9: `parse_integration`(0_basic/10_valuation/12), `parse_basic`(거래소 KS/KQ·통화), `parse_finance`(1_financials 매트릭스→시계열+컨센서스), `parse_trend`, `parse_research`(+목표가 텍스트 추출), `parse_news`, `parse_price_history`, `parse_chart`, `parse_search`(이름→코드).
  - DART 파서 5 + fetch 6: `parse_dart_finance`(account_id 매칭·원→억원), `parse_dart_shareholders`, `parse_dart_executives`, `parse_dart_disclosures`, `parse_corp_code_xml` + `dart_corp_code_map`(zip 캐시)/`dart_financials`/`dart_major_shareholders`/`dart_executives`/`dart_disclosures`.
  - 숫자/단위 헬퍼: `_parse_kr_number`("27.52배"→27.52), `_parse_market_cap_to_eok`("2,005조 2,736억"→20052736), `_dart_won_to_eok`(원→억원), `_extract_target_price`("55만원"→550000).
- fixture 15개: `tests/fixtures/kr/` (네이버 11 + DART 4).
- 테스트: 네이버 23 + DART 8 + env_loader 5 = **36 GREEN**. 라이브 검증(naver_basic/integration/search, dart corp_code/재무/최대주주/임원) 통과.
- `.env.example` 에 `DART_APIKEY` 추가.

**검증**: K 테스트 전체 50개 통과(router 14 + env 5 + naver 23 + dart 8). 전체 스위트 사전 실패 3건은 환경(akshare/provider) 이슈로 변경 전후 동일 → 신규 실패 0.

> **Phase 2에서 의도적으로 미룬 것 (Phase 3에서)**:
> - `lib/cache.py` `cached()` 래핑(TTL) — 현재 corp_map 만 메모리 캐시. fetch 함수 캐시는 data_sources 배선 시 일괄.
> - `naver_basic_combined`(integration+basic 병합, A주 스키마 정규화) — `_fetch_basic_kr` 에서 조합.

---

#### (참고) 원래 Phase 2 설계 메모

**신규 파일**: `lib/kr_data_sources.py` (HK 모듈 패턴: 함수마다 dict/list 반환, 절대 raise 안 함, `_err` 키에 에러 기록)

핵심 함수 (need_info_type.md 보완 섹션의 엔드포인트 매핑 그대로 구현):

```python
_BASE_M = "https://m.stock.naver.com/api/stock"
_BASE_CHART = "https://api.stock.naver.com/chart/domestic/item"
_BASE_AC = "https://ac.stock.naver.com/ac"
_HEADERS = {"User-Agent": "Mozilla/5.0 ...", "Referer": "https://m.stock.naver.com/"}

def _get_json(url) -> Any | None:
    """GET + JSON 검증. 응답이 HTML 에러페이지면 None 반환 (첫 비공백 문자가 '['/'{' 인지 확인)."""

def naver_integration(code6) -> dict          # 0_basic + 10_valuation + 12_capital_flow(dealTrendInfos)
def naver_basic(code6) -> dict                 # price/거래소구분(KS/KQ)
def naver_finance(code6, period="annual") -> dict   # 1_financials (annual/quarter)
def naver_trend(code6) -> list                 # 12_capital_flow 외국인/기관/개인
def naver_price_history(code6, size=120) -> list    # 2_kline (페이지)
def naver_chart_ohlcv(code6, start, end, period="day") -> list  # 2_kline 대량(float)
def naver_news(code6, size=30) -> list         # 15_events / 17_sentiment
def naver_research(code6, size=30) -> list     # 6_research (리포트+목표가 텍스트)
def naver_search(name) -> list                 # 이름→코드 (ac 자동완성)

def naver_basic_combined(code6) -> dict        # integration+basic 병합 + A주 스키마로 정규화(HK fetch_hk_basic_combined 패턴)
```

**정규화 책임** (중요): 네이버 응답 → 내부 raw_data 스키마 변환을 이 모듈에서 완결.
- `totalInfos` 배열(key/value) → 평탄 dict로 (`per`→`pe_ttm`, `pbr`→`pb`, `eps`/`bps`/`dividendYieldRatio` 등).
- 콤마 제거 + "배"/"원"/"%"/"조"/"억" 단위 파싱 헬퍼 (`_parse_kr_number`, `_parse_market_cap`).
- `finance` 매트릭스(rowList×columns) → `revenue_history`/`net_profit_history`/`roe_history` 시계열 list (연도 오름차순 정렬, `isConsensus:"Y"` 미래열은 컨센서스로 분리).
- `dealTrendInfos`/`trend` → `main_fund_flow_20d`(외국인+기관 합을 "주력 순유입"으로 매핑).

**DART 래퍼** (`kr_data_sources.py` 내 또는 `lib/dart_api.py` 분리):
```python
def dart_major_shareholders(corp_code) -> dict   # 11_governance 최대주주
def dart_executives(corp_code) -> dict           # 임원 현황
def dart_disclosures(corp_code, days=90) -> list # 15_events 공시 원문
def dart_corp_code_map() -> dict                 # 종목코드→DART corp_code (최초 1회 zip 다운로드 캐시)
```
- DART는 `corp_code`(8자리)를 쓰므로 종목코드(6자리)→corp_code 매핑 테이블 캐시 필요 (`corpCode.xml` zip, TTL 주 단위).
- `DART_APIKEY` 미설정 시 graceful skip (11_governance는 빈 데이터 + `_data_gaps`에 기록).

**캐시**: 모든 함수 `lib/cache.py`의 `cached()` 래핑. TTL — 시세/integration=REALTIME, finance/research=QUARTERLY(24h), DART corp map=주 단위.

**테스트**: `tests/test_kr_data_sources.py` — 실제 네트워크는 mock(저장한 JSON fixture), 파싱/정규화 단위 테스트. 단위 변환(억원, 콤마, "배") 경계값 테스트.

---

### Phase 3 · data_sources 시장 분기 배선 (★★) — ✅ **완료 (2026-06-16, TDD)**

**구현 결과**:
- `lib/data_sources.py` K 분기: `fetch_basic`→`_fetch_basic_kr`(naver_basic_combined·거래소 확정), `_fetch_kline_impl`→`_kline_kr_chain`(네이버 chart→A주 동일 중국어 키 스키마라 fetch_kline.py 재사용), `_fetch_financials_impl`(naver_finance annual+quarter), `_fetch_news_impl`(naver_news), `fetch_research_reports`→`_fetch_research_impl_kr`(naver_research).
- `resolve_korean_name_rich`/`resolve_korean_name`(naver_search 기반, KOSPI→.KS·KOSDAQ→.KQ, 정확일치/단일후보 auto-resolve) + 테스트 5.
- `kr_data_sources.merge_basic`/`naver_basic_combined`/`_format_market_cap_kr` + 테스트 2.
- `fetch_basic.py` main 에 `is_korean_name` 분기(한글명→resolve_korean_name_rich), source 라벨 `naver:K`.
- `run.py --market {A,H,U,K}` 플래그(순수 6자리에 .A/.KS/.HK 강제).
- **E2E 검증**: `005930`→K(네이버, 삼성전자 343,000·PER 27.72), `삼성전자`→resolve→005930.KS, `에코프로비엠`→247540.KQ(KOSDAQ), `600519.A`→A주 회귀 정상. 라이브 kline 110행/financials 시계열/research 30개·평균목표가 415,000원 동작.

**검증**: K 테스트 57 + parser 회귀 5 = 62 GREEN. (테스트 러너는 RTK 요약이 한글 mojibake로 "No tests collected" 오보 → hermes venv pytest 직접 사용으로 우회.)

> **Phase 3에서 의도적으로 미룬 것 (Phase 4에서)**: fetcher 스크립트(fetch_kline/financials/research/events 등)의 K 출력 shape 정합(차원 스키마화). 현재 data_sources 는 K 네이티브 출력을 반환, fetcher 가 dimension 스키마로 변환하는 것은 Phase 4.

---

#### (참고) 원래 Phase 3 설계 메모

**파일**: `lib/data_sources.py`

1. `fetch_basic` (L299):
   ```python
   if ti.market == "K":
       return cached(ti.full, f"basic__{ti.code}", lambda: _fetch_basic_kr(ti), ttl=TTL_REALTIME)
   ```
   `_fetch_basic_kr(ti)` 신규 — `kr_data_sources.naver_basic_combined(ti.code)` 호출.
2. `_fetch_kline_impl` (L861): `ti.market=="K"` → `naver_chart_ohlcv` → 내부 캔들 스키마 변환.
3. `_fetch_financials_impl` (L1197): K 분기 → `naver_finance(annual)+(quarter)` 병합. (akshare/yf K 미지원이므로 네이버 전담.)
4. `_fetch_news_impl` (L1285): K → `naver_news`.
5. `_fetch_research_impl` (L1344): K → `naver_research`.
6. `_fetch_north_impl`/`_fetch_hot_impl` 등 A주 전용 함수: K는 빈 반환(현재 `ti.market != "A"` early-return이라 이미 안전, 확인만).
7. `resolve_chinese_name_rich` 옆에 `resolve_korean_name(name)` 추가 → `naver_search` 사용.
8. `_fetch_price_tencent_qt` 류 시세 폴백은 K 미지원 → 네이버가 주 소스이므로 불필요.

**fetch_basic.py** (L43 `main`): 한글명 분기 추가
```python
if is_korean_name(user_input):
    r = ds.resolve_korean_name(user_input)
    ...  # 중국어명 처리와 대칭
```

---

### Phase 4 · 22 fetcher K 대응 + 파이프라인 배선 (★★) — 🟡 **lite 완료 (2026-06-16, TDD+E2E)**

**구현 결과 (lite 코어 + capital_flow)**:
- `kr_data_sources.py` 차원 shape 순수 함수 4 + 테스트 5: `to_financials_dim`, `to_capital_flow_dim`(외국인+기관→주력순유입, 北向 개념 대체), `to_events_dim`(news+DART공시), `to_governance_dim`(DART 최대주주+임원, pledge=[]). akshare 무관이라 hermes pytest 가능.
- fetcher K 분기(얇게 호출): `fetch_financials._fetch_kr`, `fetch_events`(naver_news + dart_disclosures), `fetch_governance`(DART), `fetch_capital_flow`(naver_trend). `fetch_lhb` 는 `market != "A"` 로 이미 자동 skip(K `_note`). `fetch_kline`/`fetch_valuation` 은 Phase 3 data_sources 분기로 무수정 동작.
- `dart_disclosures` 기본 `bgn_de`=최근 90일 (DART 기간 미지정 시 빈 반환 회피).
- **E2E**: `python run.py 005930 --depth lite --no-browser` → `reports/005930.KS_20260616/full-report-standalone.html` (698KB) 생성. critical=0. 리포트에 삼성전자·PER 27.72·ROE 10.85·매출 시계열·최대주주 삼성생명·임원 한종희 모두 채워짐. **F조(游资) 자동 skip 동작**(49 skip, 1派看多/6派看空).

**검증**: K 테스트 62 GREEN (router 14 + env 5 + naver 25 + dart 8 + resolve 5 + dims 5).

> **Phase 4에서 남은 것 (후속)**:
> - 정성/저빈도 차원 fetcher K 정밀화: `fetch_peers`(KRX 동종목), `fetch_research`(naver_research dict shape), `fetch_industry/macro/policy/moat/materials/futures/sentiment/trap/contests/chain/fund_holders` — 현재 빈/웹검색 fallback 으로 graceful(리포트는 생성). Phase 7 에서 충실화.
> - **통화 표시 ¥→₩** (리포트에 ¥ 20개 잔존) → Phase 6.
> - **DCF 한국 파라미터**(무위험 3.0%/ERP 5.5%/세율 22%) → 현재 valuation pe/pb 정확, dcf 값은 중국 파라미터 → Phase 5/6.
> - medium/deep depth 전체 차원 E2E.

---

#### (참고) 원래 Phase 4 설계 메모

대부분 fetcher는 `data_sources`에 위임하므로 Phase 3로 자동 충족. **직접 처리 필요한 것만**:

대부분 fetcher는 `data_sources`에 위임하므로 Phase 3로 자동 충족. **직접 처리 필요한 것만**:

| fetcher | K 처리 |
|---|---|
| `fetch_basic` | Phase 3 (한글명 resolve) ✅ |
| `fetch_financials` | Phase 3 위임 ✅ |
| `fetch_kline` | Phase 3 위임 ✅ |
| `fetch_valuation` | K 분기: 현재 PER/PBR=integration, **5년 PER 분위는 chart로 PER 시계열 자체 계산**, DCF는 한국 파라미터(아래) |
| `fetch_research` | Phase 3 위임 ✅, 목표가는 previewContent 텍스트 추출(정규식 `목표주가.*?([\d,]+)원`) |
| `fetch_capital_flow` | K 분기: `naver_trend` → 외국인/기관 순매수. 북향자금 필드 비움 |
| `fetch_events` | K 분기: `naver_news` + `dart_disclosures` |
| `fetch_governance` | K 분기: `dart_major_shareholders`+`dart_executives` (DART 키 없으면 skip) |
| `fetch_peers` | K 분기: KRX 업종분류로 동종목 코드 → 각 `integration` 루프 (Phase 5로 미뤄도 됨, 1차는 빈 peer_table 허용) |
| `fetch_industry` | K 분기: DDGS 웹검색 + 업종 PER(네이버 업종 페이지 후순위) |
| `fetch_macro`/`fetch_policy`/`fetch_moat`/`fetch_materials`/`fetch_futures` | 정성 차원 — DDGS 웹검색 한국어 쿼리로 전환(need_info_type.md 차원별 "한국 소스 추천" 참고). 코드 변경 최소 |
| `fetch_sentiment` | K 분기: `naver_news` + DDGS. 종목토론실 Playwright는 후순위 |
| `fetch_trap_signals` | DDGS 한국어 8신호 쿼리 |
| `fetch_lhb` | **K skip** — 빈 `{lhb_count_30d:0, _skipped:"no_lhb_in_kr"}` 반환 |
| `fetch_contests` | **K skip** — 설구 없음. 빈 반환 |
| `fetch_fund_holders` | K: DART 펀드 보유 후순위. 1차 빈 반환 허용 |

**파이프라인** `lib/pipeline/fetchers/registry.py`:
- 각 `_make_adapter`의 `markets` 튜플에 `"K"` 추가 (전 차원).
- K에서 skip할 `16_lhb`/`19_contests`는 `markets`에서 K 제외하거나, fetcher가 빈 결과+quality=`missing`(critical 아님) 반환하도록.
- `collect.py`는 market을 모르고 dim_key만 보고 전부 실행하므로, **fetcher 내부에서 market 판별 후 skip**하는 방식이 안전(레지스트리 구조 변경 최소화).

**DCF 한국 파라미터** (`fetch_valuation.py` 또는 `compute_deep_methods.py`):
```python
KR_DCF = {"risk_free": 0.030,  # 국고채 3년
          "erp": 0.055, "tax_rate": 0.22, "terminal_g": 0.020}
```
market에 따라 파라미터 선택 분기.

---

### Phase 5 · 특성 추출 · 심사위원 · 점수 K 정합 (★★) — ✅ **완료 (2026-06-16, TDD)**

**구현 결과**:
- `stock_features.py` **버그 수정**: market 추론에 `.KS`/`.KQ`→`"K"` 추가(기존엔 한국 종목이 `"US"`로 오판 → 미국 시장 룰 적용되던 문제). `market_cap_yi` 는 K basic 이 제공하는 수치를 우선 사용(한국 "조/억" 문자열 파싱 불가 회피). 테스트 4.
- `investor_knowledge.py`: `market_match` docstring 에 K 명시. **F조(游资) 23명은 scope='A' 라 K 자동 skip**, 글로벌 그룹(scope='all')은 K 평가 — 기존 로직으로 동작(코드 변경 0), 특성화 테스트 5로 고정.
- `score_fns.py` 확인: `10_valuation` 은 자기 5년 PER 분위 기반이라 **시장 중립**(절대 임계 없음 → K 완화 불필요), `16_lhb` 는 lhb_count 기본 0 → **자동 5점 중립**(K skip), `11_governance`/`12_capital_flow` K 데이터로 동작. `15_events` 뉴스 카운트용 `news` 별칭을 `to_events_dim` 에 추가.
- `self_review.py`: K 에서 critical=0(HK 전용 체크는 `market!="H"` early-return, 16_lhb 누락도 비-critical) → 수정 불필요.

**검증**: K 단위 테스트 71 GREEN. lite 재실행 시 리포트 `market: K` 정확 반영(이전엔 US 오판), 종합점수 47.8/100, F조 skip, critical=0.

> **Phase 5에서 Phase 6으로 미룬 것**: DCF 한국 파라미터(무위험 3.0%/ERP 5.5%/세율 22%/g 2.0%) — 통화 표시(₩) 한글화와 함께 처리.

---

#### (참고) 원래 Phase 5 설계 메모

1. **`lib/stock_features.py` L390-397** (버그 수정 포함):
   ```python
   if ticker_str.endswith((".SZ", ".SH", ".BJ")):
       f["market"] = "A"
   elif ticker_str.endswith(".HK"):
       f["market"] = "HK"
   elif ticker_str.endswith((".KS", ".KQ")):
       f["market"] = "K"
   else:
       f["market"] = "US"
   ```
   - 시가총액 파싱 `market_cap_yi`(L96)의 `"亿"` 제거 로직 → 한국 "조원"/"억원" 파싱 추가(억원 단위 통일).

2. **`lib/investor_knowledge.py`**:
   - `MARKET_SCOPE` 주석을 `"A"/"HK"/"US"/"K"`로 갱신. F조 23명은 scope `"A"` 유지 → K 자동 skip(원하는 동작, 추가 코드 0).
   - `market_match`: K 종목은 scope="all" 투자자만 통과. (가치/성장/기술/퀀트/매크로 = 한국 적용 OK.)
   - `reality_check`: market 인자에 "K" 들어와도 동작하도록 확인(현재 문자열 비교라 안전). 필요 시 한국 특화 known_holdings는 후순위.

3. **`lib/pipeline/score_fns.py`**:
   - `16_lhb`: market=="K"이면 기본 점수 5(중립) 고정, 신호 평가 skip.
   - `12_capital_flow`: K는 "주력 순유입"을 외국인+기관 순매수 합으로 해석(데이터가 이미 그렇게 들어옴). 북향자금 분기 무시.
   - PER/PBR 분위 임계값: 한국 밴드가 중국보다 낮음(PER 정상 8~15). `10_valuation` 분위 계산은 자기 5년 분위 기반이라 시장 무관하게 동작 → 절대 임계 하드코딩이 있으면 K 완화.

4. **`lib/self_review.py`**:
   - HK 전용 체크(L166/L194 `market != "H"`)와 대칭으로 K 가드 추가하거나 무시.
   - `16_lhb` 누락을 K에서는 critical→info로.
   - KRW 통화/한국 업종분류 유효성 체크 추가(선택).

---

### Phase 6 · 리포트 렌더링 한글화/통화 (★) — ✅ **완료 (2026-06-16, TDD, D8)**

**구현 결과 (D8: 기존 중국어 렌더러 0 수정 · K 전용 후처리 모듈)**:
- 신규 `lib/report/locale_ko.py` — K 리포트 HTML 후처리: 통화 `¥→₩`(천단위 콤마 + `.0` 제거), 단위 `万亿→조`/`亿→억`, 차원 제목·판정어·액션어 중→한 사전(긴 키 우선). 테스트 9.
- `run.py` 단일 배선: standalone/full-report 생성 후 `ti.market=="K"` 면 `localize_ko` 적용 (렌더러 비침습).
- `lib/i18n.py`: `SUPPORTED_LANGS` 에 `"ko"` + `language_instruction("ko")` (심층 경로 agent 코멘트 한국어). `run.py` 가 K 종목이면 `UZI_LANG=ko` 자동 설정(명시 시 우선).
- `fetch_valuation.py`: **DCF 한국 파라미터** — WACC 8.5%(무위험 국고채3년~3.0% + ERP~5.5%), 종료성장 2.0%, 민감도 WACC [6~10]/성장 [4~10].

**E2E 검증**: lite 재생성 리포트 — `¥` 0개→`₩` 20개(`₩343,000` 콤마), `亿` 0개→`억`, 밸류에이션/재무/지배구조/용호방(한국 미적용) 라벨, 액션어(매수 48·매도 58·목표가·리스크) 한글화. K 단위 테스트 80 GREEN.

> **남은 중국어 (후속)**: 평가위원 **개별 코멘트의 긴 자연어 문장**(규칙 기반 생성). 단어 후처리로는 한계 → (a) 심층(deep) 경로는 `language_instruction("ko")` 로 agent 가 한국어 생성, (b) lite 규칙 코멘트 한글화는 synthesize/persona 로직의 한글 출력부 신설(별도 작업, Phase 7+).

---

#### (참고) 원래 Phase 6 설계 메모 — **한국어 기본값 (D8)**

> **원칙 (D8)**: 한국어 출력부를 **별도 모듈/분기로 신설**한다. 기존 중국어 출력 코드는 **수정 최소화**(이상적으로 무수정)하여 upstream 원본 업데이트 시 **병합 충돌을 피한다**. 즉 "중국어 문자열을 한국어로 치환"이 아니라 "K 시장일 때 별도 한국어 렌더 경로를 탄다".

**파일**: `lib/report/*`, `lib/pipeline/renderer/*`, `assets/report-template.html`, 신규 `lib/report/locale_ko.py`

1. **언어 디스패치**: 출력 언어 기본값을 한국어로. `UZI_LANG=ko`를 K 시장에서 자동 설정(또는 market→lang 매핑). `i18n.py` `SUPPORTED_LANGS`에 `"ko"` 추가 + `language_instruction("ko")`.
2. **별도 한국어 라벨/문구 사전**: 신규 `lib/report/locale_ko.py`(또는 `assets/i18n/ko.json`)에 차원 라벨/섹션 제목/판정 문구를 모아둠. 렌더러는 `market=="K"`(또는 lang=="ko")일 때 이 사전을 lookup, 아니면 기존 중국어 경로 그대로 → **기존 중국어 분기 비침습**.
3. **통화/단위**: 헬퍼 `currency_symbol(market)` → `{"A":"¥","H":"HK$","U":"$","K":"₩"}`, 단위 `{"A":"亿/万亿","K":"억/조"}`. 하드코딩 `¥`/`元`(스크립트 6곳, `grep -rl "¥\|元" lib/report lib/pipeline/renderer`)은 **K 경로에서만** 헬퍼 경유, A 경로는 손대지 않음.
4. **템플릿**: `report-template.html`은 placeholder 기반이면 데이터 주입 단계에서 한국어가 들어가므로 무수정 가능. 정적 중국어 텍스트가 있으면 K 전용 변수 슬롯 추가.
5. 16_lhb/19_contests 카드: K에서 "해당 없음(한국 시장 미적용)" 배지로 렌더 또는 숨김.
6. **심사위원 코멘트 언어**: 심층 경로(role-play)에서 `language_instruction("ko")`로 한국어 코멘트 출력. F조 자동 skip은 Phase 5에서 처리됨.

---

### 🔎 medium/deep E2E 점검 결과 (2026-06-17)

lite 이후 medium(22차원 전체)·deep(sonnet subagent 66 평가위원 role-play) E2E 를 돌려 점검.

**deep 경로 동작 확인**: sonnet subagent 가 `panel.json`/`raw_data.json` 읽고 `agent_analysis.json`
작성(42 활성 + 24 skip, 19차원 한국어 코멘트) → stage2 재조립 → 한국어 deep 리포트(707KB) 생성 성공.

**점검 중 보완 완료**:
- 🐞 **[핵심 버그] 평가위원 market "US" 오판** — `extract_features` 가 raw ticker 접미사로 market 추론하는데
  pipeline raw ticker 는 접미사 없는 `005930` → US 로 오판되어 평가위원이 미국 시장 룰 적용
  (F조 skip 사유 "不看US市场"). `raw['market']`(="K") 우선 사용으로 수정. pipeline/run.py 의
  market 화이트리스트에도 "K" 추가. → 이제 thorp 등 US 전용 평가위원도 K 를 올바르게 skip.
- 🐞 **17_sentiment 中 플랫폼 → "비관" 오표시** — 雪球/股吧/知乎 0 hits 로 thermometer 0·"悲观".
  K 분기로 한국 플랫폼(naver/youtube/news/community) 쿼리 + 감정 단어 0개면 "中性(중립)" 처리.
- 🌐 **번역 보강** — locale_ko 에 감정 라벨/중국 플랫폼명/빈데이터/액션어 추가, 미치환 f-string 잔재 정리.

**Phase 7 / 후속 이슈로 기록 (미보완)**:
- **industry 이름 미수집** — K basic 에 업종명 없음(`industry='综合'` fallback, 13곳). 단
  네이버 integration 에 `industryCode`(278) + `industryCompareInfo`(동종 6종목), DART `induty_code`(264)가
  이미 있음 → ① KSIC/네이버 코드→업종명 매핑, ② `industryCompareInfo` 로 **4_peers** 채우기,
  ③ `consensusInfo.priceTargetMean/recommMean` 로 **6_research** 목표가(구조화) 보강.
- **6_fund_holders K** — DART 펀드보유, 현재 "A-share only" skip.
- **웹검색 쿼리 추가 한국어화** — fetch_macro/policy/moat/trap 일부 쿼리.
- **investor_criteria 템플릿/features 키명 불일치**(`{pe_ttm}`↔`pe`, `{roe}`↔`roe_latest`, `{ev_to_revenue}` 등 없음)
  — **K 전용 아님(전체 시장 영향, upstream)**. 현재 K 리포트는 후처리로 잔재만 가림. 근본 수정은 별도.
- KRW 재무 단위(억원) 표기 명시.

---

### 🌐 평가위원/리포트 한글화 작업 + 회고 (2026-06-17)

medium/deep 점검에서 드러난 "리포트 본문 중국어"(평가위원 대화창·섹션 제목·라벨)를 한국어화.

**완료 (커밋 `41a7795`, `2c51b6d`)**:
- `investor_personas.py`: `PERSONAS_KO`(66명 대사) + `get_comment` lang 분기 (sonnet subagent)
- `investor_criteria.py` + `investor_evaluator.py`: `KO_MSGS`(242 rule 메시지) + headline/rationale lang 분기 (sonnet subagent)
- `lib/report/locale_ko.py`: 후처리 사전 ~59 → 1024개 (섹션 제목/UI 라벨/판정 서술) (sonnet subagent)
- D8 준수: 기존 중국어 무수정 · 모두 `UZI_LANG=ko` 별도 출력부. 미설정 시 회귀 보존.
- 효과: 가시 중국어 **1349 → 301 조각 (총출현 80.7%↓)**. 평가위원 대화창·섹션 제목 한국어.

**⚠️ 회고 — LLM 대량 번역의 한계 (다음에 개선할 점)**:
- 증상: 번역 산출물에 **중국어+한국어 혼용**이 다수 섞여 들어감. LLM 번역은 분량/컨텍스트가 커지면
  타깃 언어를 벗어나(환각성) 원문 일부를 그대로 남기거나 혼용하는 경향이 있다.
- 우리가 한 대응(반성점): 혼용/누락을 **locale_ko 후처리 사전으로 재치환**해 땜질 → 사전이 1024개로
  비대해지고, 리포트가 바뀔 때마다 새 혼용이 생겨 **사전을 계속 늘려야 하는 구조적 부담**이 됨.
- 교훈/개선안:
  1. LLM 번역 위임 시 **"출력에 CJK 한자 0개"를 자동 검증**(`grep -P '[\x{4e00}-\x{9fff}]'`)하고,
     실패하면 **재번역 루프**를 subagent 작업 정의에 포함시켰어야 함. (이번엔 키 누락/길이만 검증)
  2. 후처리 사전은 **고정 UI 라벨**에 한정하고, 자연어(대사/서술)는 **소스 ko 출력부에서 끝까지 한글로**
     완성(혼용 0 검증)하는 게 유지보수상 맞다. 후처리로 자연어 혼용을 메우면 무한히 늘어난다.
  3. 남은 ~301 중국어(조사 `为/该/与`, criteria `{'name':..,'msg':..}` JSON 혼합, 일부 한자 이름)는
     후처리로는 오치환 위험이 커 유보. 근본 해결은 **소스(personas/criteria) 재번역 + CJK=0 검증**.

→ **후속 과제**: personas/criteria ko 출력부를 CJK=0 기준으로 재검수(혼용 제거) + 검증 스크립트 추가.

---

### Phase 7 · 업종 매핑 · peers · 마감 (★) — 🟡 **대부분 완료 (2026-06-17, TDD, 커밋 `d649024`)**

**완료**:
1. ✅ **업종명** — `lib/industry_mapping.py`(KSIC 매핑 테이블) 대신, 네이버 `stocks/industry/{code}.groupInfo.name` 으로 직접 lookup(예 278→"반도체와반도체장비"). `parse_integration` 에 `industry_code`/`industry_compare`/`consensus_*` 추가, `naver_basic_combined` 가 업종명까지 채움 → `0_basic.industry` 정상화(综合 fallback 해소).
2. ✅ **4_peers** — `to_peers_dim` + `fetch_peers` K 분기: `integration.industryCompareInfo`(동종) → peer_table. (단위 불명으로 시총 순위는 미산출 · PER/PBR 보강은 후속.)
3. ✅ **6_research** — `consensusInfo.priceTargetMean/recommMean` → `to_research_dim`(목표가 컨센서스 우선) + `fetch_research` K 분기.
4. ✅ **registry** — `data_source_registry.py` 에 K 소스 9개 등록 + `markets` 주석 "K".

**추가 처리 완료 (2026-06-17 · 커밋 후속)**:
- ✅ **문서**: `AGENTS_KR.md`/`README_KR.md`/`CLAUDE_KR.md` 에 K 사용법 섹션 추가(SKILL.md 는 중국어 원본이라 보존).
- ✅ **평가위원 이름 한글화**: `locale_ko` 가 `investor_db.INVESTORS` 의 중국어명→영문명을 자동 매핑(en 보유 ~42명) + 음차 보강(바핏 등). agent_analysis 표기 잔존(伯利/查诺斯)도 음차 추가. → 활성 평가위원 한자명 0.
- ✅ **4_peers PER/PBR 보강**: `fetch_peers` K 가 동종(industryCompareInfo)별 `naver_integration` 추가 호출로 PER/PBR 채움(삼성 28.0·SK하이닉스 24.4 등) + 동종 **중간값** PER(소부장 고PER 이상치 robust).
- ✅ **6_fund_holders K**: graceful skip 확정(한국 공모펀드 보유는 무료 API 미제공 · 유료 에프앤가이드/제로인) + `_note` 한국 안내. DART 대량보유(majorstock 5%+)는 11_governance 보강 후보로 기록.

**2차 후속 처리 완료 (2026-06-20)**:
- ✅ **peer 시총 순위 복원** — `industryCompareInfo.marketValue` 단위 = **백만원**(= market_cap_yi 억원 × 100) 확정. `to_peers_dim` 이 /100 으로 억원 통일 후 정렬 → 삼성전자 반도체 시총 1위/7개 산출.
- ✅ **게이지(F조) 24명 한국어 음차** — `locale_ko` 에 별명 음차 매핑 추가(주식바다 해적왕/장맹주/자오라오거 등), 값 CJK=0.
- ✅ **CJK=0 재검수** — KO_MSGS/NAME_KO 한자 잔존 0 확인. PERSONAS_KO 게이지 14명의 원문 한자 괄호병기('잠금 보유(锁仓)')는 `get_comment` ko 경로에서 정규식 제거 → CJK=0.
- ✅ **DART 대량보유(majorstock 5%+) → 11_governance** — `parse_dart_majorstock`/`dart_major_holders` + `to_governance_dim(major_holders=...)`. 삼성물산 19.7%(최신 보고) 표시.
- ✅ **정성 쿼리 — macro/policy** — `fetch_macro`/`fetch_policy` 에 K 분기: 한국은행 기준금리·원달러 환율·K칩스법 등 한국 거시/정책 쿼리(중국 권위도메인 회피).

**3차 후속 처리 완료 (2026-06-20)**:
- ✅ **정성 쿼리 industry/moat/trap K 분기** — `fetch_industry._dynamic_industry_overview`(업황/시장규모/사이클 + 일반 search, 중국 권위도메인 회피), `fetch_moat`(특허/전환비용/네트워크/점유율/R&D 한국어 + `{name} 주식` 앵커), `fetch_trap_signals`(한국 작전주 맥락 `SIGNALS_KO` 8신호 — 리딩방/유튜브/텔레그램/관리종목 + level/권고문 ko). 모두 UZI_LANG=ko 분기, 비K 중국어 보존.

**계속할 것 (추후)**:
- **6_fund_holders 공모펀드 보유** — 무료 API 부재. 에프앤가이드/제로인 유료 연동 시 fund_managers 스키마 충족 가능(현재 graceful skip + DART 대량보유로 일부 보완).
- **agent_analysis 런타임 CJK 가드** — deep role-play 산출물(agent가 쓴 표기)에 한자 혼용 가능 → 렌더 전 CJK 가드 또는 작업 정의에 CJK=0 명시.
- **trap/moat 휴리스틱 키워드 한국어 매칭** — `fetch_trap_signals.SIGNALS_KO.positive_kws`(완료) 외, `fetch_moat` 의 `pos_kws`("龙头/第一") 등 점수 휴리스틱은 아직 중국어 → K 결과 매칭 부정확(snippet 은 한국어 제공, agent 가 dim_commentary 작성).
- **industry TAM/growth 휴리스틱** — `fetch_industry` 의 "亿元/XX亿" 추출 정규식이 중국 단위 기반 → 한국(조원/억원) 추출 보강 필요(쿼리·snippet 은 한국어).

---

## 3. 신규/수정 파일 요약

**신규**:
- `lib/kr_data_sources.py` — 네이버 신 API + DART 래퍼 (Phase 2)
- `lib/dart_api.py` — (선택 분리) DART OpenAPI 클라이언트
- `tests/test_kr_market_router.py`, `tests/test_kr_data_sources.py`, `tests/test_kr_end_to_end.py`

**수정** (라인은 현재 기준, 작업 시 재확인):
- `lib/market_router.py` (Phase 1)
- `lib/data_sources.py` — fetch_basic/kline/financials/news/research/resolve (Phase 3)
- `fetch_basic.py`, `fetch_valuation.py`, `fetch_capital_flow.py`, `fetch_events.py`, `fetch_governance.py`, `fetch_lhb.py`, `fetch_contests.py`, `fetch_peers.py` (Phase 4)
- `lib/pipeline/fetchers/registry.py` (Phase 4)
- `lib/stock_features.py` L390-397 (Phase 5, 버그 수정)
- `lib/investor_knowledge.py`, `lib/pipeline/score_fns.py`, `lib/self_review.py` (Phase 5)
- `lib/report/*`, `lib/pipeline/renderer/*`, `assets/report-template.html`, `lib/i18n.py` (Phase 6)
- `lib/industry_mapping.py`, `lib/data_source_registry.py` (Phase 7)
- `run.py` — `--market` 인자 (Phase 1)
- `.env.example` — `DART_APIKEY` 추가 (Phase 2)

---

## 4. 테스트 전략

| 레벨 | 내용 |
|---|---|
| 단위 | 네이버 응답 파싱(콤마/억원/조원/"배"/% 변환), finance 매트릭스→시계열, ac 검색→코드 |
| 분기 | `parse_ticker` K 인식, `stock_features` market="K", `market_match` F조 skip |
| 통합 | mock 네트워크로 005930 stage1→raw_data.json 22차원 채움, score/synthesize 무오류 |
| E2E (수동) | `python run.py 005930.KS --depth lite --no-browser` → HTML 생성 확인. `삼성전자` 한글명, `247540.KQ`(코스닥) |
| 회귀 | 기존 A/H/U 332 pytest 전부 통과(시장 분기가 기존 경로 무손상) |

**Fixture**: 실제 네이버/DART 응답 JSON을 `tests/fixtures/kr/`에 저장(integration/basic/finance/trend/research/news/ac). 네트워크 의존 제거.

---

## 5. 리스크 & 완화

| 리스크 | 영향 | 완화 |
|---|---|---|
| 네이버 비공식 API 스키마 변경/차단 | 데이터 수집 실패 | 모듈 격리(kr_data_sources)로 수정 범위 국소화. UA/Referer 헤더, 캐시, 차원별 graceful 빈 반환 |
| 6자리 코드 A주↔K주 충돌 | 오라우팅 | **확정**: 순수 6자리=K 우선, A주는 `.A` 명시. 명시 접미사(.KS/.KQ/.SZ/.SH/.BJ/.A)가 항상 최우선. ✅ Phase 1 구현+테스트 완료 |
| 순수 6자리 K 전환으로 기존 A주 CLI 흐름 일시 단절 | Phase 1~3 사이 `python run.py 600519`가 K로 라우팅(미구현) | 과도기 한정. A주는 `600519.A`/`600519.SH`로 동작. Phase 3에서 K fetch 완성 시 해소. 회귀 테스트는 `.A`로 의도 표현 |
| HTML 에러페이지 200 OK 반환 | 파서 크래시 | `_get_json`에서 첫 문자 검증, 실패 시 None |
| DART 키 부재 | 11_governance 공백 | graceful skip + `_data_gaps` 기록(분석은 진행) |
| 목표주가가 비구조화 텍스트 | 컨센서스 부정확 | 1차 정규식, 부정확 시 integration.cnsPer/cnsEps 보조. 심층 경로는 LLM 추출 |
| PER 밴드 차이로 밸류 점수 왜곡 | 평가 편향 | 자기 5년 분위 기반 유지(시장 무관). 절대 임계만 K 완화 |
| 66 심사위원 중 한국 비친화 | 코멘트 어색 | F조 자동 skip. 나머지 글로벌 프레임워크는 한국 적용 가능. 한국 특화 페르소나는 향후 확장 |

---

## 6. 마일스톤

1. **M1 (MVP, Phase 1-4)**: `python run.py 005930.KS --depth lite` 로 핵심 7~10차원(basic/financials/kline/valuation/capital_flow/events/research) 채운 리포트 생성. F조 자동 skip. → **데모 가능**.
2. **M2 (완성, Phase 5-6)**: 22차원 graceful 충당, 심사위원/점수/자가검증 K 정합, 통화·라벨 한글화.
3. **M3 (심화, Phase 7+)**: peers/industry/governance(DART)/fund_holders 충실화, 한국 특화 심사위원/페르소나 확장, 종목토론실 sentiment.

---

## 7. 다음 작업 (착수 순서)

1. ✅ **Phase 1 — market_router K 인식 + 테스트 (완료, 2026-06-16)**
2. **Phase 2 (다음)** — `lib/kr_data_sources.py` 네이버 신 API + DART 래퍼 + fixture 테스트 (가장 큰 덩어리). DART 키는 `.env`의 `DART_APIKEY` 사용.
3. Phase 3 — data_sources 배선 + `fetch_basic` 한글명 resolve + `run.py --market` → `python fetch_basic.py 005930.KS` 단독 동작 확인
4. Phase 4 — 전 fetcher + 파이프라인 → lite 리포트 E2E
5. 이후 Phase 5(특성/심사위원/점수) → Phase 6(한국어 출력, D8) → Phase 7(peers/industry/governance) 순차

> **사용자 결정 확정(2026-06-16)**:
> - DART API 키 → **발급 완료** (`.env`에 `DART_APIKEY` 설정 필요).
> - 순수 6자리 기본 시장 → **K 우선** (A주는 `.A` 명시). ✅ Phase 1 반영.
> - 리포트 출력 언어 → **한국어 기본**, 한국어 출력부 별도 구성·중국어부 비침습(D8).
