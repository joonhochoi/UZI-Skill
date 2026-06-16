# 한국 주식(K) 지원 추가를 위한 필요 데이터 명세

> 본 문서는 UZI-Skill에 한국 주식 시장(K) 지원을 추가하기 위해
> 각 차원(dimension)별로 **어떤 데이터가 필요한지**를 상세히 정리한 것입니다.
>
> `skills/deep-analysis/scripts/lib/data_source_registry.py`에 `"K"` 마켓 타입을
> 새 DataSource로 등록할 때, 각 URL이 반환해야 하는 값의 의미와 형식을 이해하는 데 사용하세요.

---

## 📋 전체 차원 개요 (22차원)

| 키 | 한글명 | 가중치 | 유형 | K 지원 난이도 |
|---|---|---|---|---|
| `0_basic` | 기본 정보 | — | 메타데이터 | ★☆☆ (쉬움) |
| `1_financials` | 재무제표 | 5 | 정량 | ★★☆ (보통) |
| `2_kline` | K선 기술분석 | 4 | 정량 | ★☆☆ (쉬움) |
| `3_macro` | 거시환경 | 3 | 정성 | ★☆☆ (쉬움) |
| `4_peers` | 동종 비교 | 4 | 정량 | ★★☆ (보통) |
| `5_chain` | 공급망 | 4 | 정량 | ★★☆ (보통) |
| `6_research` | 증권사 리포트 | 3 | 정량 | ★★★ (어려움) |
| `7_industry` | 업종 경기 | 4 | 정성 | ★☆☆ (쉬움) |
| `8_materials` | 원자재 | 3 | 정성 | ★☆☆ (쉬움) |
| `9_futures` | 선물 연계 | 2 | 정성 | ★☆☆ (쉬움) |
| `10_valuation` | 밸류에이션 분위 | 5 | 정량 | ★★☆ (보통) |
| `11_governance` | 지배구조 | 4 | 정량 | ★★☆ (보통) |
| `12_capital_flow` | 자금 흐름 | 4 | 정량 | ★★★ (어려움) |
| `13_policy` | 정책/규제 | 3 | 정성 | ★☆☆ (쉬움) |
| `14_moat` | 해자 | 3 | 정량 | ★☆☆ (쉬움) |
| `15_events` | 이벤트/공시 | 4 | 정성 | ★★☆ (보통) |
| `16_lhb` | 용호방 | 4 | 정량 | ★★★ (한국無) |
| `17_sentiment` | 투자심리 | 3 | 정량 | ★★☆ (보통) |
| `18_trap` | 살돈판 탐지 | 5 | 안전 | ★☆☆ (쉬움) |
| `19_contests` | 실전대회 | 4 | 정량 | ★★☆ (보통) |
| `6_fund_holders` | 펀드 보유 | — | 보너스 | ★★☆ (보통) |

---

## 🔍 차원별 상세 필요 데이터

### 0_basic — 기본 정보 (★☆☆)

**목적**: 종목 신원 확인 카드. 모든 후속 차원이 이 정보에 의존함. **점수 없음** (메타데이터).

**필수 필드**:

| 필드명 | 타입 | 설명 | 한국 소스 예시 |
|---|---|---|---|
| `name` | str | 종목명 (예: "삼성전자") | 네이버금융, KRX, Yahoo Finance |
| `price` | float | 현재가 (원화) | 네이버금융, KRX |
| `code` | str | 종목코드 (예: "005930") | KRX |
| `industry` | str | 업종분류 (예: "반도체") | KRX 업종분류, 네이버금융 |
| `market_cap` | str | 시가총액 (예: "450조원" 또는 "4500000억") | KRX, 네이버금융 |
| `pe_ttm` | float | PER (Trailing) | 네이버금융, Yahoo Finance |
| `pb` | float | PBR | 네이버금융, Yahoo Finance |
| `eps` | float | EPS (주당순이익) | 네이버금융, Dart |
| `actual_controller` | str | 실제 지배주주 / 최대주주 | Dart (대주주 현황) |
| `listed_date` | str | 상장일 (예: "1975-06-11") | KRX, 네이버금융 |
| `full_name` | str | 정식 회사명 (예: "삼성전자주식회사") | KRX, Dart |
| `change_pct` | float | 전일대비 등락률 (%) | 네이버금융, KRX |
| `currency` | str | 통화 ("KRW") | — (하드코딩 가능) |

**선택 필드**:
| 필드명 | 타입 | 설명 |
|---|---|---|
| `total_shares` | float | 총 발행주식수 |
| `circulating_cap` | str | 유통 시가총액 |
| `chairman` | str | 대표이사 |
| `staff_num` | float | 직원 수 |

**한국 소스 추천**:
- **주 소스**: Yahoo Finance (`005930.KS`), 네이버금융 (`https://finance.naver.com/item/main.nhn?code=005930`)
- **대체 소스**: KRX 정보데이터시스템 (`http://data.krx.co.kr/`), Dart 전자공시 (`https://dart.fss.or.kr/`)
- **브라우저 소스**: 네이버금융 종목분석 페이지 (Playwright)

---

### 1_financials — 재무제표 (★★☆)

**목적**: 핵심 재무 건전성 — ROE, 마진, 매출성장률, 부채비율. **가중치 5 (최상)**.

**점수 로직**: 기본 5점. ROE≥15% +2, ROE≥10% +1, ROE<5% -2. 순이익률≥15% +1. 매출성장률≥20% +1. 부채비율≥60% -1.

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `roe` | str | 최신 ROE (예: `"18.7%"`) | 점수 산정, 6개 특성 파생 |
| `roe_history` | list[float] | 최근 5년 연간 ROE 리스트 (예: `[12.3, 14.1, 15.8, 16.2, 18.7]`) | ROE 추세, 5년 평균/최소/달성률 |
| `net_margin` | str 또는 float | 순이익률 (예: `"15.2%"`) | 점수 산정, 마진 품질 |
| `gross_margin` | str 또는 float | 매출총이익률 | 성장파/테크리더파 규칙 |
| `revenue_growth` | str | 최근 매출성장률 YoY (예: `"+12.5%"`) | 점수 산정 |
| `revenue_history` | list[float] | 최근 5년 연간 매출액 (억원 단위) (예: `[2300000, 2500000, ...]`) | 매출성장률 CAGR 계산 |
| `net_profit_history` | list[float] | 최근 5년 연간 순이익 (억원 단위) | 순이익 성장률, 연속 흑자 |
| `financial_health` | dict | 재무 건전성 하위 딕셔너리 | |
| `financial_health.debt_ratio` | float | 부채비율 (%) | 점수 산정, 버핏/멍거/클라만 규칙 |
| `financial_health.current_ratio` | float | 유동비율 | 그레이엄 규칙 |
| `financial_health.fcf_margin` | float | 잉여현금흐름률 (%) | FCF 양수 판정 |
| `financial_health.roic` | float | ROIC (%) | 덩샤오펑 규칙 |
| `financial_health.net_margin_pct` | float | 순이익률 (%) (수치형) | 듀퐁 분해 |
| `dupont` | dict | 듀퐁 분해 | |
| `dupont.net_margin_pct` | float | 순이익률 | 듀퐁 ROE 재구성 |
| `dupont.asset_turnover` | float | 자산회전율 | 듀퐁 ROE 재구성 |
| `dupont.equity_multiplier` | float | 자기자본승수 | 듀퐁 ROE 재구성, 레버리지 품질 |
| `dupont.roe_reconstructed_pct` | float | 듀퐁 재구성 ROE | ROE 품질 검증 |
| `dupont.roe_quality` | str | ROE 품질 (`"margin_driven"` / `"leverage_driven"`) | 가치파 규칙 |
| `dividend_years` | list[str] | 배당 연도 리스트 | 연속 배당 연수 |
| `dividend_amounts` | list[float] | 배당금 리스트 | 5년 총배당 |
| `dividend_yields` | list[float] | 배당수익률 리스트 | 배당주 판정 |
| `eps` | float | EPS (주당순이익) | 컨센서스 대비 |
| `fcf` | str | 잉여현금흐름 (예: `"+1.2조"`) | FCF 표시 |

**선택 필드**:
| 필드명 | 타입 | 설명 |
|---|---|---|
| `financial_years` | list[str] | 재무연도 레이블 (예: `["2021", "2022", ...]`) |
| `gross_margin_history` | list[float] | 매출총이익률 추세 |
| `net_margin_history` | list[float] | 순이익률 추세 |
| `bps` | float | BPS (주당순자산) |
| `profit_growth` | str | 순이익성장률 (홍콩주용) |

**한국 소스 추천**:
- **주 소스**: Dart 전자공시 (사업보고서/분기보고서 재무제표), Yahoo Finance (`005930.KS`)
- **대체 소스**: 네이버금융 종목분석 재무제표 탭, KRX
- **브라우저 소스**: 네이버금융 재무제표 페이지 (Playwright)

---

### 2_kline — K선 기술분석 (★☆☆)

**목적**: 가격 차트 분석 — Wyckoff 단계, 이평선 정렬, MACD, RSI, 낙폭. **가중치 4**.

**점수 로직**: 기본 5점. Stage 2 +2, Stage 1 +1, Stage 3/4 -2. 이평선 다두정렬 +1. 최대낙폭 ≤-30% -1.

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `stage` | str | Wyckoff 단계 (`"Stage 1"` / `"Stage 2"` / `"Stage 3"` / `"Stage 4"`) | 점수 산정, ~30개 투자자 규칙 |
| `ma_align` | str | 이평선 정렬 (`"多头"`=다두 / `"空头"`=공두 / `"交叉"`=교차) | 점수 산정, 기술파 규칙 |
| `macd` | str | MACD 상태 (`"金叉"` / `"死叉"` / `"水上金叉"` 등) | 기술파 규칙 |
| `rsi` | str 또는 float | RSI 값 (예: `"55.2"`) | 기술파 규칙 |
| `kline_stats` | dict | K선 통계 | |
| `kline_stats.max_drawdown` | str | 최대 낙폭 (예: `"-25%"`) | 점수 산정, 우드/막스 규칙 |
| `kline_stats.ytd_return` | str | 연초대비 수익률 (예: `"+15.3%"`) | 미네르비니/사이먼스 규칙 |
| `kline_stats.volatility` | str | 변동성 (예: `"28.5%"`) | 간/주사오싱 규칙 |
| `indicators` | dict | 기술지표 하위 딕셔너리 | |
| `indicators.ma5` | float | 5일 이평선 | 이평선 계산 |
| `indicators.ma20` | float | 20일 이평선 | 이평선 계산 |
| `indicators.ma60` | float | 60일 이평선 | 이평선 계산 |
| `indicators.ma120` | float | 120일 이평선 | 이평선 계산 |
| `indicators.ma200` | float | 200일 이평선 | Asness 규칙 |
| `indicators.ma_bull_alignment` | bool | 이평선 다두정렬 여부 | 기술파 규칙 |
| `indicators.macd_dif` | float | MACD DIF | MACD 계산 |
| `indicators.macd_dea` | float | MACD DEA | MACD 계산 |
| `indicators.macd_hist` | float | MACD 히스토그램 | MACD 계산 |
| `indicators.macd_golden_cross` | bool | MACD 골든크로스 여부 | 기술파 규칙 |
| `indicators.rsi_14` | float | RSI 14 | RSI 계산 |
| `indicators.kdj_k` | float | KDJ K값 | KDJ 지표 |
| `indicators.kdj_d` | float | KDJ D값 | KDJ 지표 |
| `indicators.kdj_j` | float | KDJ J값 | KDJ 지표 |
| `indicators.obv` | float | OBV (On-Balance Volume) | OBV 추세 |
| `indicators.obv_trend_up` | bool | OBV 상승추세 여부 | 기술파 규칙 |
| `indicators.williams_r` | float | Williams %R | 기술파 규칙 |
| `indicators.year_high` | float | 52주 최고가 | 고점 대비 위치 |
| `indicators.year_low` | float | 52주 최저가 | 저점 대비 위치 |
| `indicators.pct_from_year_high` | float | 52주 고점 대비 % | 구하이쩌왕 규칙 |
| `indicators.vol_5_vs_20` | float | 5일 vs 20일 거래량 비율 | 거래량 분석 |
| `candles_60d` | list[dict] | 60일 캔들 데이터 (시가/고가/저가/종가/거래량) | 차트 렌더링, Stage 판정 |
| `close_60d` | list[float] | 60일 종가 리스트 | 이평선/지표 계산 |
| `kline_count` | int | K선 데이터 개수 | 데이터 품질 |

**선택 필드**:
| 필드명 | 타입 | 설명 |
|---|---|---|
| `chip_distribution` | dict | 매물대 분포 (한국은 개념 다를 수 있음) |
| `chip_distribution.profit_ratio` | float | 수익률 비율 |
| `chip_distribution.avg_cost` | float | 평균 매입단가 |
| `chip_distribution.concentration_70` | float | 70% 매물 집중도 |
| `chip_distribution.concentration_90` | float | 90% 매물 집중도 |

**한국 소스 추천**:
- **주 소스**: Yahoo Finance (`005930.KS`), 네이버금융 시세 API
- **대체 소스**: KRX 정보데이터시스템, 한국거래소
- **지표 계산**: Python으로 직접 계산 (pandas-ta 라이브러리로 MACD/RSI/KDJ/OBV/Williams%R 모두 계산 가능)

---

### 3_macro — 거시환경 (★☆☆)

**목적**: 거시경제 맥락 — 금리 사이클, 환율, 지정학 리스크, 원자재 동향. **가중치 3**. **정성 차원** (agent 심층 분석 필요). 기본 점수: 6.

**필수 필드**:

| 필드명 | 타입 | 설명 |
|---|---|---|
| `rate_cycle` | str | 금리 사이클 위치 (예: `"한국은행 2026 기준금리 3.25% 유지"`) |
| `fx_trend` | str | 환율 동향 (예: `"원/달러 1350원대, 원화 약세"`) |
| `geo_risk` | str | 지정학 리스크 (예: `"북한 리스크, 미중 갈등 영향"`) |
| `commodity` | str | 원자재 동향 (예: `"반도체 업황 회복기"`) |
| `industry_macro_impact` | str | 해당 업종 거시 영향 |
| `web_search_snippets` | dict | 웹 검색 스니펫 (DDGS 검색 결과) |

**한국 소스 추천**:
- **주 소스**: DDGS 웹 검색 (`한국은행 기준금리 2026`, `한국 GDP 성장률`, `원달러 환율`)
- **대체 소스**: 한국은행 (`https://www.bok.or.kr/`), 통계청 (`https://kostat.go.kr/`)
- **브라우저 소스**: 네이버금융 뉴스, 한국경제

---

### 4_peers — 동종 비교 (★★☆)

**목적**: 경쟁 구도 — 동종 기업 테이블, 업종 내 순위, 상대 밸류에이션. **가중치 4**.

**점수 로직**: 기본 5점. peer_table 데이터 있으면 7점. 자사 PER < 동종 평균 PER × 0.9 → +1. 자사 PER > 동종 평균 PER × 1.2 → -1.

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `peer_table` | list[dict] | 동종 기업 리스트 | 점수 산정, 동종 PER 비교 |
| `peer_table[].name` | str | 기업명 | 표시 |
| `peer_table[].code` | str | 종목코드 | 식별 |
| `peer_table[].pe` | float | PER | 동종 평균 PER 계산 |
| `peer_table[].pb` | float | PBR | 동종 비교 |
| `peer_table[].roe` | float | ROE | 동종 비교 |
| `peer_table[].revenue_growth` | float | 매출성장률 | 동종 비교 |
| `peer_table[].is_self` | bool | 자기 자신 여부 | 자사 제외 평균 계산 |
| `rank` | str | 업종 내 순위 (예: `"3위/15개"`) | 로버트슨/거스트너 규칙 |
| `industry` | str | 업종명 | 업종 확인 |

**한국 소스 추천**:
- **주 소스**: 네이버금융 업종별 종목 (같은 업종 내 PER/PBR/ROE 비교), KRX 섹터 분류
- **대체 소스**: Dart (동종 업종 기업 리스트), Yahoo Finance
- **브라우저 소스**: 네이버금융 종목비교 페이지 (Playwright)

---

### 5_chain — 공급망 (★★☆)

**목적**: 산업 체인 위치 — 사업부문 구성, 상류/하류, 고객 집중도. **가중치 4**.

**점수 로직**: 사업부문 breakdown 있으면 6점, 없으면 5점.

**필수 필드**:

| 필드명 | 타입 | 설명 |
|---|---|---|
| `main_business_breakdown` | list[dict] | 사업부문별 매출 비중 (상위 6개) |
| `main_business_breakdown[].name` | str | 사업부문명 (예: `"반도체"`, `"가전"`) |
| `main_business_breakdown[].value` | float | 매출 비중 (%) |
| `upstream` | str | 상류 공급망 (예: `"웨이퍼, 실리콘"`) |
| `downstream` | str | 하류 수요처 (예: `"스마트폰 제조사, 데이터센터"`) |
| `client_concentration` | str | 고객 집중도 (예: `"상위 5개사 45%"`) |
| `products` | str | 주요 제품 설명 |

**선택 필드**:
| 필드명 | 타입 | 설명 |
|---|---|---|
| `supplier_concentration` | str | 공급사 집중도 |
| `main_business_raw` | list[dict] | 원시 사업부문 데이터 (최대 50행) |

**한국 소스 추천**:
- **주 소스**: Dart 사업보고서 (사업의 내용 섹션), 네이버금융 기업개요
- **대체 소스**: DDGS 웹 검색 (`"삼성전자 공급망"`, `"SK하이닉스 매출 구성"`)
- **브라우저 소스**: 네이버금융 기업분석 페이지 (Playwright)

---

### 6_research — 증권사 리포트 (★★★)

**목적**: 매도측 애널리스트 커버리지 — 리포트 수, 컨센서스 등급, 목표가. **가중치 3**.

**점수 로직**: 5 + min(3, coverage // 5). 매수 등급 ≥10개 +1.

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `report_count` | int | 최근 리포트 수 | 점수 산정 |
| `coverage` | str | 커버리지 기관 수 (예: `"15개"`) | 점수 산정 |
| `coverage_count` | int | 커버리지 기관 수 (수치) | 특성 추출 |
| `rating` | str | 등급 분포 (예: `"매수 12 / 중립 3"`) | 표시 |
| `rating_distribution` | dict | 등급별 개수 (예: `{"매수": 12, "중립": 3}`) | 매수 비율 계산 |
| `buy_rating_pct` | float | 매수 등급 비율 (%) | 피셔/린치 규칙 |
| `target_price_avg` | float | 평균 목표가 (원화) | 업사이드 계산 |
| `target_avg` | str | 평균 목표가 표시용 (예: `"85,000원"`) | 표시 |
| `consensus_eps_2026` | float | 컨센서스 EPS (2026년) | 컨센서스 PER |
| `consensus_pe_2026` | float | 컨센서스 PER (2026년) | 밸류에이션 |
| `consensus_eps_2027` | float | 컨센서스 EPS (2027년) | 장기 전망 |
| `upside` | str | 목표가 괴리율 (예: `"+25.3%"`) | 소로스/펑류 규칙 |
| `recent_reports` | list[dict] | 최근 리포트 목록 | |
| `recent_reports[].date` | str | 발행일 | 표시 |
| `recent_reports[].title` | str | 리포트 제목 | 표시 |
| `recent_reports[].broker` | str | 증권사명 | 표시 |
| `recent_reports[].rating` | str | 등급 | 표시 |
| `recent_reports[].eps_2026` | float | EPS 전망치 | 표시 |
| `recent_reports[].pe_2026` | float | PER 전망치 | 표시 |
| `brokers` | list[str] | 커버 증권사 리스트 | 표시 |

**한국 소스 추천**:
- **주 소스**: Dart (증권사 발행 리포트는 아니지만 실적 전망 가능), 네이버금융 종목분석 컨센서스
- **대체 소스**: 에프앤가이드 (`https://www.fnguide.com/`) — 한국 증권사 컨센서스 표준, FNGuide API
- **브라우저 소스**: 네이버금융 애널리스트 의견 페이지 (Playwright)
- **⚠️ 어려움**: 한국은 중국처럼 akshare로 무료 증권사 리포트 데이터를 한 번에 가져오기 어려움. FNGuide는 유료 API. 대안으로 네이버금융 컨센서스 페이지를 Playwright로 스크래핑하거나, DDGS 웹 검색으로 대체 가능.

---

### 7_industry — 업종 경기 (★☆☆)

**목적**: 업종 건전성 — 성장률, TAM, 침투율, 업종 평균 PER/PBR. **가중치 4**. **정성 차원**. 기본 점수: 7.

**필수 필드**:

| 필드명 | 타입 | 설명 | 특성 사용처 |
|---|---|---|---|
| `industry` | str | 업종명 | 업종 식별 |
| `growth` | str | 업종 성장률 (예: `"+15%/년"`) | 우드/Serenity 규칙 |
| `tam` | str | 총유효시장 (예: `"500조원"`) | 안드레센/차마스 규칙 |
| `penetration` | str | 시장 침투율 (예: `"35%"`) | 표시 |
| `lifecycle` | str | 업종 수명주기 (`"성장기"` / `"성숙기"` / `"쇠퇴기"`) | 성장/쇠퇴 판정 |
| `industry_pe_weighted` | float | 업종 가중평균 PER | 업종 PER 비교 |
| `industry_pe_median` | float | 업종 중간값 PER | 업종 PER 비교 |
| `total_companies` | int | 업종 내 상장사 수 | 시장 점유율 계산 |
| `total_mcap_yi` | float | 업종 총 시가총액 (억원) | 시장 점유율 계산 |
| `note` | str | 비고 | 추가 정보 |

**한국 소스 추천**:
- **주 소스**: KRX 업종분류 + 업종별 통계, 네이버금융 업종별 PER/PBR
- **대체 소스**: 통계청 산업통계, 한국은행 산업별 GDP
- **브라우저 소스**: 네이버금융 업종별 종목 페이지 (Playwright)

---

### 8_materials — 원자재 (★☆☆)

**목적**: 투입 비용 분석 — 핵심 원자재, 가격 동향, 비용 비중. **가중치 3**. **정성 차원**. 기본 점수: 6.

**필수 필드**:

| 필드명 | 타입 | 설명 |
|---|---|---|
| `core_material` | str | 핵심 원자재 (예: `"반도체 웨이퍼 / 희토류"`) |
| `price_trend` | str | 가격 동향 (예: `"12개월 평균 +5.2%"`) |
| `price_history_12m` | list[float] | 12개월 가격 이력 (월별) |
| `materials_detail` | list[dict] | 원자재 상세 |
| `materials_detail[].name` | str | 원자재명 |
| `materials_detail[].code` | str | 선물 코드 |
| `materials_detail[].latest_price` | float | 최신 가격 |
| `materials_detail[].trend_pct_12m` | float | 12개월 추세 (%) |
| `materials_detail[].trend_label` | str | 추세 레이블 |
| `cost_share` | str | 원가 비중 (예: `"원자재가 매출원가의 60%"`) |
| `import_dep` | str | 수입 의존도 |

**한국 소스 추천**:
- **주 소스**: DDGS 웹 검색 (`"삼성전자 원자재 가격"`, `"반도체 웨이퍼 가격 동향"`)
- **대체 소스**: 한국자원정보서비스 (`https://www.kores.net/`), 관세청 수출입 데이터
- **브라우저 소스**: 네이버금융 뉴스

---

### 9_futures — 선물 연계 (★☆☆)

**목적**: 원자재 선물 노출 — 연계 선물 계약, 가격 동향, 헤지 영향. **가중치 2 (최하)**. **정성 차원**. 기본 점수: 5.

**필수 필드**:

| 필드명 | 타입 | 설명 |
|---|---|---|
| `linked_contract` | str | 연계 선물 계약명 (예: `"COMEX 금 선물"`) |
| `contract_code` | str | 선물 코드 |
| `latest_price` | float | 최신 가격 |
| `contract_trend` | str | 계약 가격 동향 (예: `"60일 +12.3%"`) |
| `price_history_60d` | list[float] | 60일 가격 이력 |
| `note` | str | 비고 (연계 계약 없을 시 사유) |

**한국 소스 추천**:
- **주 소스**: Yahoo Finance (국제 선물), Investing.com
- **대체 소스**: KRX 파생상품시장 (한국거래소 선물)
- **브라우저 소스**: 네이버금융 선물/원자재

---

### 10_valuation — 밸류에이션 분위 (★★☆)

**목적**: 역사적 밸류에이션 맥락 — PER/PBR/PSR 5년 분위, 배당수익률, DCF. **가중치 5 (최상)**.

**점수 로직**: PER 분위 < 30 → 9, < 50 → 7, < 70 → 5, < 85 → 3, ≥ 85 → 2.

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `pe` | str | 현재 PER (예: `"15.2"`) | 점수 산정 |
| `pb` | str | 현재 PBR (예: `"1.8"`) | 그레이엄 규칙 |
| `pe_quantile` | str | PER 5년 분위 (예: `"5년 72분위"`) | 점수 산정, ~8개 투자자 규칙 |
| `pb_quantile` | str | PBR 5년 분위 (예: `"5년 45분위"`) | 표시 |
| `industry_pe` | float | 업종 평균 PER | 업종 대비 PER |
| `pe_history` | list[float] | 5년 PER 이력 (월별 또는 분기별) | 분위 계산 |
| `dcf` | str | DCF 내재가치 표시용 (예: `"450조원"`) | 안전마진 계산 |
| `dcf_simple` | dict | DCF 계산 상세 | |
| `dcf_simple.intrinsic_value_total` | float | 총 내재가치 (원화) | 안전마진 계산 |
| `dcf_simple.pv_fcfs` | float | 예측 FCF 현재가치 합 | DCF 표시 |
| `dcf_simple.pv_terminal` | float | 종료가치 현재가치 | DCF 표시 |
| `dcf_simple.assumptions` | dict | DCF 가정 (WACC, 성장률 등) | DCF 표시 |
| `dcf_sensitivity` | dict | DCF 민감도 분석 | |
| `dcf_sensitivity.waccs` | list[float] | WACC 범위 | 민감도 표 |
| `dcf_sensitivity.growths` | list[float] | 성장률 범위 | 민감도 표 |
| `dcf_sensitivity.values` | list[list[float]] | 5×5 민감도 매트릭스 | 민감도 히트맵 |
| `dcf_sensitivity.current_price` | float | 현재가 | 비교 기준 |
| `dividend_yield` | str | 배당수익률 (예: `"2.1%"`) | 달리오 규칙 |

**한국 소스 추천**:
- **주 소스**: Yahoo Finance (5년 PER/PBR 이력), 네이버금융 (PER/PBR 차트)
- **대체 소스**: KRX (과거 PER/PBR 데이터)
- **DCF 계산**: Python으로 직접 계산 (WACC, FCF 예측, 종료가치). 한국 기준 무위험수익률=국고채 3년 금리 (~3.0%), ERP=5-6%, 세율=법인세율 (22% 수준), 종료성장률 g=2.0%.

---

### 11_governance — 지배구조 (★★☆)

**목적**: 기업 지배구조 — 실제 지배주주, 주식 담보, 내부자 거래, 대표이사 교체. **가중치 4**.

**점수 로직**: 기본 6점. 담보 없음 +1. 내부자 거래 있음 +1.

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `pledge` | list[dict] | 주식 담보 기록 | 점수 산정, 돤융핑 규칙 |
| `pledge[].质押比例` | float | 담보 비율 (%) | 담보 위험 판정 |
| `insider_trades_1y` | list[dict] | 최근 1년 내부자 거래 | 점수 산정 |
| `insider_trades_1y[].date` | str | 거래일 | 표시 |
| `insider_trades_1y[].name` | str | 거래자 | 표시 |
| `insider_trades_1y[].change` | str | 변동 (매수/매도) | 방향성 |
| `insider_trades_1y[].amount` | str | 거래량 | 규모 |
| `qualitative_search` | list[str] | 정성 검색 쿼리 (관련자 거래/위반/스톡옵션) | agent 분석용 |

**한국 소스 추천**:
- **주 소스**: Dart (최대주주 현황, 임원 보유주식, 담보 설정 내역)
- **대체 소스**: KRX (지배구조 보고서), 금융감독원 전자공시
- **브라우저 소스**: 네이버금융 지분현황 페이지 (Playwright)

---

### 12_capital_flow — 자금 흐름 (★★★)

**목적**: 기관 자금 흐름 — 외국인/기관 순매수, 신용잔고, 주주 수 추이, 대량매매, 보호예수 해제. **가중치 4**.

**점수 로직**: 기본 5점. 5일 주력 순유입 > 0 +2, < 0 -1. 보호예수 해제 없음 +1.

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `main_fund_flow_20d` | list[dict] | 20일 주력 자금 흐름 | 점수 산정 |
| `main_fund_flow_20d[].主力净流入-净额` | float | 주력 순유입 금액 (원화) | 5일 합계 계산 |
| `main_5d` | str | 5일 요약 (예: `"+1,200억"`) | 표시 |
| `main_20d` | str | 20일 요약 | 표시 |
| `holder_count_history` | list[dict] | 주주 수 추이 | 주주 집중도 |
| `holder_count_history[].holders` | int | 주주 수 | 집중/분산 판정 |
| `holders_trend` | str | 주주 수 추세 (`"집중"` / `"분산"`) | 특성 추출 |
| `margin_recent` | list[dict] | 신용거래 최근 데이터 | 신용 추세 |
| `margin_trend` | str | 신용 추세 | 표시 |
| `unlock_schedule` | list[dict] | 보호예수 해제 일정 | 점수 산정 |
| `unlock_schedule[].date` | str | 해제일 | 표시 |
| `unlock_schedule[].amount` | str | 해제 물량 | 리스크 평가 |
| `block_trades_recent` | list[dict] | 대량매매 (블록딜) 최근 기록 | 리스크 평가 |
| `institutional_history` | dict | 기관 보유 추이 (분기별) | |
| `institutional_history.quarters` | list[str] | 분기 레이블 | 표시 |
| `institutional_history.fund` | list[float] | 펀드 보유 비중 (%) | 기관 신뢰 |
| `institutional_history.qfii` | list[float] | 외국인 보유 비중 (%) | 외국인 신뢰 |

**한국 소스 추천**:
- **주 소스**: KRX (외국인/기관 순매수, 신용잔고), 네이버금융 (외국인/기관 매매동향)
- **대체 소스**: Dart (주주현황, 보호예수), 금융감독원
- **브라우저 소스**: 네이버금융 투자자별 매매동향 페이지 (Playwright)
- **⚠️ 어려움**: 중국의 "북향자금"(沪港通/深港通) 개념이 한국에는 없음. 대신 외국인 순매수, 기관 순매수, 개인 순매수로 대체. "용호방" 개념도 한국에는 없으므로 `16_lhb` 차원은 skip 처리.

---

### 13_policy — 정책/규제 (★☆☆)

**목적**: 정부 정책 영향 — 정책 방향, 보조금, 규제, 반독점. **가중치 3**. **정성 차원**. 기본 점수: 6.

**필수 필드**:

| 필드명 | 타입 | 설명 | 특성 사용처 |
|---|---|---|---|
| `policy_dir` | str | 정책 방향 (`"긍정적"` / `"중립"` / `"긴축"` / `"—"`) | Serenity 규칙 |
| `subsidy` | str | 보조금 정보 | 표시 |
| `monitoring` | str | 규제 감시 | 표시 |
| `anti_trust` | str | 반독점 이슈 | 표시 |
| `snippets` | dict | 웹 검색 스니펫 | agent 분석용 |
| `year` | str | 기준 연도 | 표시 |
| `industry` | str | 대상 업종 | 업종 확인 |

**한국 소스 추천**:
- **주 소스**: DDGS 웹 검색 (`"한국 반도체 산업 정책 2026"`, `"금융위원회 규제"`)
- **대체 소스**: 기획재정부, 산업통상자원부, 금융위원회, 공정거래위원회
- **브라우저 소스**: 네이버금융 뉴스

---

### 14_moat — 해자 (★☆☆)

**목적**: 경쟁우위 평가 — 무형자산, 전환비용, 네트워크효과, 규모우위 (Morningstar 4요소). **가중치 3**. 기본 점수: 6.

**필수 필드**:

| 필드명 | 타입 | 설명 | 특성 사용처 |
|---|---|---|---|
| `scores` | dict | 4요소 점수 | |
| `scores.intangible` | float | 무형자산 점수 (0-10) (브랜드/특허/라이선스) | 버핏/피셔/멍거/장쿤 규칙 |
| `scores.switching` | float | 전환비용 점수 (0-10) | 버핏/Serenity 규칙 |
| `scores.network` | float | 네트워크효과 점수 (0-10) | 틸 규칙 |
| `scores.scale` | float | 규모우위 점수 (0-10) | 버핏/틸 규칙 |
| `intangible` | str | 무형자산 설명 스니펫 | 표시 |
| `switching` | str | 전환비용 설명 스니펫 | 표시 |
| `network` | str | 네트워크효과 설명 스니펫 | 표시 |
| `scale` | str | 규모우위 설명 스니펫 | 표시 |
| `rd_summary` | str | R&D 요약 | 젠슨황 규칙 |
| `web_search_snippets` | dict | 웹 검색 스니펫 (5개 쿼리) | agent 분석용 |

**한국 소스 추천**:
- **주 소스**: DDGS 웹 검색 (`"삼성전자 경쟁우위"`, `"SK하이닉스 해자"`, `"한국 기업 브랜드 가치"`)
- **대체 소스**: Dart 사업보고서 (사업의 내용, 경쟁우위 요소)
- **브라우저 소스**: 네이버금융 기업분석

---

### 15_events — 이벤트/공시 (★★☆)

**목적**: 기업 이벤트와 촉매 — 이벤트 타임라인, 최근 뉴스, 공시, 경고. **가중치 4**. **정성 차원**.

**점수 로직**: 5 + min(3, len(news) // 10).

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `event_timeline` | list[str] | 이벤트 타임라인 (`"날짜 · 제목"` 형식) | 이벤트 수, 촉매 판정 |
| `recent_news` | list[dict] | 최근 뉴스 | 점수 산정 |
| `recent_news[].date` | str | 날짜 | 표시 |
| `recent_news[].title` | str | 제목 | 촉매 키워드 매칭 |
| `recent_news[].type` | str | 유형 | 분류 |
| `recent_news[].source` | str | 출처 | 신뢰도 |
| `recent_notices` | list[dict] | 최근 공시 | |
| `recent_notices[].date` | str | 공시일 | 표시 |
| `recent_notices[].title` | str | 공시 제목 | 표시 |
| `recent_notices[].url` | str | 공시 URL | 원문 링크 |
| `recent_notices[].type` | str | 공시 유형 | 분류 |
| `disclosures_count` | int | 공시 건수 | 데이터 품질 |
| `news_count` | int | 뉴스 건수 | 데이터 품질 |
| `catalyst` | list[dict] | 향후 촉매 | |
| `catalyst[].date` | str | 예정일 | 표시 |
| `catalyst[].event` | str | 이벤트명 | 표시 |
| `catalyst[].impact` | str | 영향도 (`"높음"` / `"중간"` / `"낮음"`) | 표시 |
| `warnings` | list[str] | 리스크 경고 | agent 분석용 |

**한국 소스 추천**:
- **주 소스**: Dart 전자공시 (최근 공시 목록), 네이버금융 뉴스
- **대체 소스**: DDGS 웹 검색 (`"삼성전자 뉴스"`, `"SK하이닉스 공시"`), 한국경제, 매일경제
- **브라우저 소스**: 네이버금융 종목뉴스 페이지 (Playwright)

---

### 16_lhb — 용호방 (★★★ → 한국은 skip)

**목적**: A주 상한가 매매 분석 — 용호방 출현 횟수, 유자(游资) 좌석 매칭. **가중치 4**. **A주 전용**.

**⚠️ 한국 시장에는 용호방(龙虎榜) 개념이 없습니다.** 한국은 가격제한폭(±30%)이 있고 상한가/하한가 종목 리스트는 있지만, 중국식 용호방(매수/매도 상위 5개 증권사 지점 공개) 제도는 없습니다.

**한국 대응 방안**:
- `16_lhb` 차원은 한국 종목 분석 시 **skip 처리** (빈 데이터 반환, `_data_gaps.json`에 명시)
- 대체 가능한 한국 유사 데이터:
  - KRX 상한가/하한가 종목 리스트
  - 거래원별 매매동향 (증권사별 매수/매도 상위)
  - 네이버금융 거래원 데이터

**필수 필드 (참고용)**:

| 필드명 | 타입 | 설명 |
|---|---|---|
| `lhb_count_30d` | int | 30일 용호방 출현 횟수 |
| `lhb_records` | list[dict] | 용호방 상세 기록 |
| `matched_youzi` | list[str] | 매칭된 유자 좌석명 |
| `inst_vs_youzi` | dict | 기관 vs 유자 자금 비교 |
| `sector_lhb_top50` | list[dict] | 섹터 용호방 상위 50 |

---

### 17_sentiment — 투자심리 (★★☆)

**목적**: 개인 투자자 심리 — 커뮤니티 반응, 감정 온도계, 긍정 비율, 소셜 핫트렌드. **가중치 3**.

**점수 로직**: 6 + min(2, len(rank_history) // 10).

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `thermometer_value` | int | 감정 온도계 (0-100) | 템플턴/막스/유자 규칙 |
| `positive_pct` | str | 긍정 비율 (예: `"65%"`) | 감정 방향 |
| `sentiment_label` | str | 감정 레이블 (`"낙관"` / `"중립"` / `"비관"`) | 감정 분류 |
| `platform_snippets` | dict | 플랫폼별 토론 스니펫 | agent 분석용 |
| `platform_hits` | dict | 플랫폼별 언급 수 | 감정 열도 |
| `total_mentions` | int | 총 언급 수 | 데이터 품질 |
| `hot_trend_mentions` | dict | 소셜 핫트렌드 언급 | |
| `hot_trend_mentions.stock_name` | str | 종목명 | 식별 |
| `hot_trend_mentions.platforms_ok` | int | 정상 작동 플랫폼 수 | 데이터 품질 |
| `hot_trend_mentions.total_hits` | int | 총 적중 수 | 감정 열도 |
| `hot_trend_mentions.by_platform_count` | dict | 플랫폼별 적중 수 | 플랫폼 분포 |
| `hot_trend_mentions.mentions` | dict | 플랫폼별 언급 상세 | 표시 |
| `news_multi_source` | dict | 멀티소스 뉴스 | 뉴스 감정 |
| `news_sources_ok` | int | 정상 뉴스 소스 수 | 데이터 품질 |
| `news_total_hits` | int | 총 뉴스 적중 수 | 뉴스 밀도 |

**한국 소스 추천**:
- **주 소스**: DDGS 웹 검색 (`"삼성전자 종목토론"`, `"005930 주식"`), 네이버금융 종목토론실
- **대체 소스**: 네이버 증권 토론방, 다음 금융, 한국거래소 커뮤니티
- **소셜 핫트렌드**: 네이버 실시간 검색어, 다음 실시간 이슈, 유튜브 증권 채널
- **브라우저 소스**: 네이버금융 종목토론실 (Playwright)

---

### 18_trap — 살돈판 탐지 (★☆☆)

**목적**: **안전 차원** — 8개 살돈판(작전주) 신호 스캔, 위험 등급 및 권고. **가중치 5 (최상)**. **역점수**: 신호 많을수록 낮은 점수.

**점수 로직**: 기본 9 (안전). Agent가 발견 신호에 따라 override.

**필수 필드**:

| 필드명 | 타입 | 설명 | 특성 사용처 |
|---|---|---|---|
| `trap_level` | str | 위험 등급 (`"🟢안전"` / `"🟡주의"` / `"🟠경계"` / `"🔴매우의심"`) | 멍거/펑류 규칙 |
| `trap_score` | int | 위험 점수 (1-9, 높을수록 안전) | 표시 |
| `signals_hit` | str | 적중 신호 (예: `"2/8"`) | 표시 |
| `signals_hit_count` | int | 적중 신호 수 | 특성 추출 |
| `signals_hit_detail` | list[dict] | 적중 신호 상세 | |
| `signals_hit_detail[].id` | str | 신호 ID | 식별 |
| `signals_hit_detail[].name` | str | 신호명 (예: `"급등 후 횡보"`) | 표시 |
| `signals_hit_detail[].evidence_kws` | str | 증거 키워드 | 표시 |
| `signals_hit_detail[].severity` | str | 심각도 | 표시 |
| `recommendation` | str | 안전 권고 | 표시 |
| `evidence_count` | int | 증거 수 | 데이터 품질 |
| `snippets` | dict | 8개 신호별 검색 스니펫 | agent 분석용 |

**한국 소스 추천**:
- **주 소스**: DDGS 웹 검색 (8개 신호별 쿼리: `"삼성전자 작전주"`, `"005930 주가조작"`, `"한국 주식 사기"` 등)
- **대체 소스**: 금융감독원 불공정거래 공시, 네이버 증권 토론방
- **브라우저 소스**: 네이버금융 종목토론실 (Playwright)

---

### 19_contests — 실전대회 (★★☆)

**목적**: 소셜 트레이딩 신호 — 설구(雪球) 포트폴리오 보유, 고수익 포트폴리오 수, 커뮤니티 언급. **가중치 4**.

**점수 로직**: 5 + min(3, xq_total // 5) + min(2, high_return).

**필수 필드**:

| 필드명 | 타입 | 설명 | 점수/특성 사용처 |
|---|---|---|---|
| `summary` | dict | 요약 | |
| `summary.xueqiu_cubes_total` | int | 총 포트폴리오 보유 수 | 점수 산정 |
| `summary.high_return_cubes` | int | 고수익 포트폴리오 수 (>50%) | 점수 산정 |
| `summary.xueqiu_login_required` | bool | 로그인 필요 여부 | 데이터 품질 |
| `summary.xueqiu_source` | str | 데이터 소스 | 신뢰도 |
| `xueqiu_cubes` | list[dict] | 포트폴리오 상세 | |
| `xueqiu_cubes[].name` | str | 포트폴리오명 | 표시 |
| `xueqiu_cubes[].owner` | str | 운용자 | 표시 |
| `xueqiu_cubes[].daily_gain` | float | 일간 수익률 | 표시 |
| `xueqiu_cubes[].monthly_gain` | float | 월간 수익률 | 표시 |
| `xueqiu_cubes[].total_gain` | float | 누적 수익률 | 고수익 판정 |
| `xueqiu_cubes[].annualized_gain_rate` | float | 연환산 수익률 | 등급 판정 |
| `tgb_mentions` | list[dict] | 타오구바 언급 | |
| `tgb_mentions[].title` | str | 게시글 제목 | 표시 |
| `tgb_mentions[].url` | str | 게시글 URL | 원문 링크 |
| `ths_simu` | list[dict] | 퉁화순 모의투자 | |
| `dpswang` | list[dict] | 대판수왕 선물대회 | |
| `fallback_queries` | list[str] | 폴백 검색 쿼리 | agent 분석용 |

**한국 소스 추천**:
- **주 소스**: DDGS 웹 검색 (`"삼성전자 포트폴리오"`, `"한국 주식 대회"`), 네이버 증권 인기 포트폴리오
- **대체 소스**: 한국거래소 모의투자대회, 네이버 증권 포트폴리오 공유
- **⚠️ 설구(雪球)는 중국 전용**: 한국에는 설구 같은 통합 소셜 트레이딩 플랫폼이 없음. 대안으로 네이버 증권 관심종목/포트폴리오 데이터, 또는 DDGS 웹 검색으로 대체.

---

### 6_fund_holders — 펀드 보유 (★★☆)

**목적**: "펀드매니저 숙제 베끼기" — 어떤 공모펀드가 이 종목을 보유 중인지, 펀드매니저 5년 성과. **보너스 차원** (핵심 22차원 외).

**필수 필드** (top-level `raw_data.fund_managers`):

| 필드명 | 타입 | 설명 |
|---|---|---|
| `fund_managers` | list[dict] | 펀드매니저 리스트 |
| `fund_managers[].name` | str | 펀드매니저명 |
| `fund_managers[].fund_name` | str | 펀드명 |
| `fund_managers[].fund_code` | str | 펀드코드 |
| `fund_managers[].position_pct` | float | 보유 비중 (%) |
| `fund_managers[].rank_in_fund` | int | 펀드 내 순위 |
| `fund_managers[].holding_quarters` | int | 보유 분기 수 |
| `fund_managers[].position_trend` | str | 보유 추세 |
| `fund_managers[].return_5y` | float | 5년 수익률 (%) |
| `fund_managers[].annualized_5y` | float | 5년 연환산 수익률 (%) |
| `fund_managers[].max_drawdown` | float | 최대 낙폭 (%) |
| `fund_managers[].sharpe` | float | 샤프 비율 |
| `fund_managers[].peer_rank_pct` | float | 동종 순위 백분위 |
| `fund_managers[].nav_history` | list[float] | NAV 이력 |
| `fund_managers[]._row_type` | str | `"full"` 또는 `"lite"` |
| `total_funds_holding` | int | 총 보유 펀드 수 |
| `active_funds_count` | int | 액티브 펀드 수 |
| `full_stats_count` | int | 완전 통계 펀드 수 |

**한국 소스 추천**:
- **주 소스**: Dart (펀드 보유 현황), 네이버금융 (펀드 포트폴리오), 한국펀드평가
- **대체 소스**: 에프앤가이드 펀드 데이터, 제로인 펀드닥터
- **브라우저 소스**: 네이버금융 펀드 페이지 (Playwright)

---

## 📊 특성 추출 요약 (stock_features.py → 108개 특성)

`stock_features.py`는 위 raw_data를 정규화하여 108개 표준 특성을 생성합니다.
이 특성들은 66명 심사위원의 242개 규칙 평가에 직접 사용됩니다.

**가장 중요한 raw_data 필드 (영향도 순)**:

| Raw 필드 | 파생 특성 수 | 영향 받는 투자자 규칙 수 |
|---|---|---|
| `1_financials.roe_history` | 6개 | ~8명 |
| `1_financials.revenue_history` | 3개 | ~9명 |
| `2_kline.stage` | 2개 | ~30명 |
| `10_valuation.pe_quantile` | 1개 | ~8명 |
| `14_moat.scores.*` | 6개 | ~12명 |
| `0_basic.industry` | 1개 | ~20명 (문자열 매칭) |
| `0_basic.market_cap` | 1개 | ~2명 + 유자 범위 체크 |
| `0_basic.pe_ttm` | 1개 | ~15명 |
| `1_financials.debt_ratio` | 1개 | ~8명 |
| `1_financials.net_margin` | 1개 | ~7명 |

---

## 🔧 수정 필요 포인트 요약

### 1. `data_source_registry.py` 수정 사항

- `DataSource.markets` 튜플에 `"K"` 추가
- 한국 데이터 소스 신규 등록 (Tier 1/2/3)
- 예시:
```python
DataSource(
    "naver_finance", "네이버금융",
    "https://finance.naver.com/item/main.nhn?code=005930",
    ("K",),
    ("0_basic", "1_financials", "2_kline", "10_valuation"),
    1, "http", "known_good",
    "한국 주식 기본 정보 / 재무제표 / PER/PBR / 차트 데이터"
),
DataSource(
    "dart", "Dart 전자공시",
    "https://dart.fss.or.kr/",
    ("K",),
    ("1_financials", "11_governance", "15_events"),
    1, "http", "known_good",
    "한국 상장사 공시 / 재무제표 / 지배구조 / 주요사항보고서"
),
DataSource(
    "krx", "한국거래소",
    "http://data.krx.co.kr/",
    ("K",),
    ("0_basic", "2_kline", "4_peers", "7_industry", "12_capital_flow"),
    1, "http", "known_good",
    "KRX 정보데이터시스템 · 업종분류 / 외국인/기관 매매 / 시가총액"
),
DataSource(
    "yahoo_finance_kr", "Yahoo Finance 한국",
    "https://finance.yahoo.com/quote/005930.KS",
    ("K",),
    ("0_basic", "1_financials", "2_kline", "10_valuation"),
    1, "http", "known_good",
    "한국주식 Yahoo Finance · PER/PBR/재무제표/K선 · 티커: 005930.KS"
),
```

### 2. `market_router.py` 수정 사항

- `parse_ticker()`에 한국 종목 코드 인식 추가 (예: `"005930.KS"`, `"005930"`, `"삼성전자"`)
- `classify_security_type()`에 한국 ETF/ETN 등 인식
- `market` 판정 로직에 `"K"` 추가

### 3. Fetcher 스크립트 수정 사항

각 `fetch_*.py`에 한국(K) 브랜치 추가 필요:

| Fetcher | K 지원 난이도 | 비고 |
|---|---|---|
| `fetch_basic.py` | ★☆☆ | Yahoo Finance `.KS` 또는 네이버금융 스크래핑 |
| `fetch_financials.py` | ★★☆ | Yahoo Finance 재무제표 또는 Dart API |
| `fetch_kline.py` | ★☆☆ | Yahoo Finance 히스토리컬 데이터 |
| `fetch_valuation.py` | ★★☆ | Yahoo Finance + 자체 DCF 계산 |
| `fetch_peers.py` | ★★☆ | KRX 업종분류 + 네이버금융 동종목록 |
| `fetch_chain.py` | ★★☆ | Dart 사업보고서 + DDGS 웹 검색 |
| `fetch_research.py` | ★★★ | FNGuide 유료 API 또는 네이버금융 Playwright |
| `fetch_industry.py` | ★☆☆ | DDGS 웹 검색 + KRX 업종통계 |
| `fetch_moat.py` | ★☆☆ | DDGS 웹 검색 |
| `fetch_governance.py` | ★★☆ | Dart 공시 |
| `fetch_macro.py` | ★☆☆ | DDGS 웹 검색 |
| `fetch_futures.py` | ★☆☆ | Yahoo Finance 선물 |
| `fetch_capital_flow.py` | ★★★ | KRX 외국인/기관 데이터 |
| `fetch_policy.py` | ★☆☆ | DDGS 웹 검색 |
| `fetch_events.py` | ★★☆ | Dart 공시 + DDGS 뉴스 |
| `fetch_lhb.py` | — | **skip 처리** (한국에 용호방 없음) |
| `fetch_sentiment.py` | ★★☆ | DDGS + 네이버 증권 토론방 |
| `fetch_trap_signals.py` | ★☆☆ | DDGS 웹 검색 |
| `fetch_contests.py` | ★★☆ | DDGS + 네이버 증권 포트폴리오 |
| `fetch_fund_holders.py` | ★★☆ | Dart 펀드 보유 + 네이버금융 |

### 4. `investor_evaluator.py` 수정 사항

- `reality_check()`에 한국 시장(`"K"`) 추가
- 유자(游资) 그룹(F)은 한국 종목에서 자동 skip (중국 A주만 함)
- 중국 특화 규칙(용호방, 북향자금 등)은 한국 종목에서 비활성화
- 한국 시장 특성에 맞는 규칙 조정 (예: PER 밴드, 변동성 범위)

### 5. `score_fns.py` 수정 사항

- `16_lhb` 차원은 한국 종목에서 기본 점수 5로 처리 (skip)
- `12_capital_flow`의 북향자금(northbound) 필드는 한국에서 외국인 순매수로 대체

### 6. `self_review.py` 수정 사항

- 한국 종목에 대한 검증 규칙 추가 (예: KRW 통화 확인, 한국 업종분류 유효성)
- `16_lhb` 차원 누락을 한국 종목에서는 critical이 아닌 info로 처리

---

## 🌐 한국 데이터 소스 URL 후보

| 소스명 | URL | 접근 방식 | 제공 데이터 |
|---|---|---|---|
| **네이버금융** | `https://finance.naver.com/item/main.nhn?code={code}` | HTTP 스크래핑 / Playwright | 기본정보, PER/PBR, 재무제표, 차트, 뉴스, 토론방 |
| **Yahoo Finance KR** | `https://finance.yahoo.com/quote/{code}.KS` | HTTP / yfinance 라이브러리 | 기본정보, 재무제표, K선, PER/PBR 이력 |
| **Dart 전자공시** | `https://dart.fss.or.kr/` | HTTP / OpenAPI | 사업보고서, 재무제표, 공시, 지배구조 |
| **KRX 정보데이터** | `http://data.krx.co.kr/` | HTTP (JSON/CSV) | 시가총액, 업종분류, 외국인/기관 매매, PER/PBR |
| **한국은행** | `https://www.bok.or.kr/` | HTTP | 기준금리, GDP, 물가, 거시지표 |
| **통계청** | `https://kostat.go.kr/` | HTTP | 산업통계, GDP, 인구 |
| **에프앤가이드** | `https://www.fnguide.com/` | HTTP (유료 API) | 컨센서스, 증권사 리포트, 펀드 데이터 |
| **금융감독원** | `https://www.fss.or.kr/` | HTTP | 불공정거래, 규제, 공시 |
| **한국거래소** | `https://www.krx.co.kr/` | HTTP | 상장종목, 시장통계, 파생상품 |

---

## ⚠️ 한국 시장 특이사항

1. **용호방(龙虎榜) 없음**: `16_lhb` 차원은 한국 종목에서 skip. 대신 거래원별 매매동향으로 대체 가능하나, 중국식 일일 상위 5개 증권사 지점 공개 제도는 한국에 없음.

2. **북향자금(北向资金) 없음**: `12_capital_flow`의 northbound 개념은 중국의 沪港通/深港通 특유 제도. 한국은 외국인 순매수, 기관 순매수로 대체.

3. **설구(雪球) 없음**: `19_contests`의 xueqiu_cubes는 중국 전용 소셜 트레이딩 플랫폼. 한국은 네이버 증권 포트폴리오, 카카오 증권 등으로 대체 가능하나 데이터 접근성이 낮음.

4. **PER/PBR 밴드 차이**: 한국 시장의 PER/PBR 분위 범위가 중국과 다름. 한국은 일반적으로 PER 8-15배가 정상 범위, 중국은 15-40배가 흔함. `10_valuation` 점수 로직의 분위 임계값 조정 필요 가능성.

5. **통화**: 모든 금액 데이터는 **원화(KRW)** 단위로 통일. 시가총액은 "조원" 또는 "억원" 단위 사용.

6. **티커 형식**: 한국 종목 코드는 6자리 숫자 (예: `005930`). Yahoo Finance는 `.KS` 접미사 (예: `005930.KS`), `.KQ` for KOSDAQ.

7. **업종분류**: KRX 업종분류 체계 (WICS, FICS) 사용. 중국의 申万/证监会 분류와 다르므로 `7_industry`의 `INDUSTRY_ESTIMATES` 하드코딩 테이블을 한국 업종에 맞게 확장 필요.

8. **세율/무위험수익률**: DCF 계산 시 한국 기준 적용 — 무위험수익률=국고채 3년 (~3.0%), ERP=5-6%, 법인세율=22% (2026년 기준), 종료성장률 g=2.0%.

---

# 🆕 [보완] 네이버 증권 신페이지(stock.naver.com) 비공식 JSON API — 실측 조사 결과

> 작성일: 2026-06-16 · 실제 `curl` 호출로 응답을 검증함 (종목: 삼성전자 005930).
>
> **핵심 결론**: 네이버 증권은 몇 달 전 `finance.naver.com`(구 HTML 페이지) → `stock.naver.com`(SPA + JSON API)로 개편되었습니다.
> 신페이지는 **HTML 스크래핑이 필요 없는 깔끔한 JSON API**를 제공하며, 22차원 중 **대부분(0/1/2/6_research/10/12/15)을 무료·무인증·단일 HTTP GET으로 충당**할 수 있습니다.
> 따라서 기존 `need_info_type.md`의 "네이버금융 Playwright 스크래핑" 권장은 **신 API 직접 호출로 전면 대체**하는 것을 권장합니다.
> 특히 `6_research`(증권사 리포트)는 원래 ★★★(FNGuide 유료)로 평가됐지만, **신 API가 증권사 리포트 + 목표주가를 무료로 제공**하므로 ★★☆로 하향됩니다.

## 📡 API 호스트 3종

| 호스트 | 용도 | 인증 | 비고 |
|---|---|---|---|
| `https://m.stock.naver.com/api/...` | 모바일 SPA 백엔드 · **주력 소스** | 없음 | `Referer: https://m.stock.naver.com/` 헤더 권장(없어도 대체로 동작), User-Agent 필요 |
| `https://api.stock.naver.com/...` | 데스크톱/차트 백엔드 | 없음 | 차트(K선) 전용으로 주로 사용. 일부 경로는 `StockConflict` 반환 → m. 호스트 우선 |
| `https://ac.stock.naver.com/ac` | 자동완성 검색 (이름→코드) | 없음 | 한글 종목명 → 코드 해석에 사용 |

**공통 호출 규약**:
- 메서드: `GET`
- 헤더: `User-Agent: Mozilla/5.0 ...` (필수) + `Referer: https://m.stock.naver.com/` (권장)
- `{code}`: 6자리 종목코드 (예: `005930`). KOSPI/KOSDAQ 동일 경로, 거래소 구분은 응답의 `stockExchangeType`로 판별.
- 응답: JSON. 단, **유효하지 않은 경로는 200 OK + HTML 에러 페이지**(`<!doctype html>... Npay 증권`)를 반환하므로, 호출부에서 `Content-Type` 또는 첫 글자(`[`/`{`)로 JSON 여부를 검증해야 함.

## 🔑 검증 완료된 엔드포인트 → 차원 매핑

### ① `GET /api/stock/{code}/integration` → `0_basic`, `10_valuation`, `12_capital_flow`
종목 통합 스냅샷. **한 번의 호출로 가장 많은 필드를 채움.**
```jsonc
{
  "stockName": "삼성전자", "itemCode": "005930", "reutersCode": "005930",
  "totalInfos": [   // key/value 쌍 배열
    {"code":"lastClosePrice","key":"전일","value":"337,000"},
    {"code":"marketValue","key":"시총","value":"1,990조 6,579억"},
    {"code":"foreignRate","key":"외인소진율","value":"47.60%"},
    {"code":"highPriceOf52Weeks","key":"52주 최고","value":"377,000"},
    {"code":"lowPriceOf52Weeks","key":"52주 최저","value":"57,400"},
    {"code":"per","key":"PER","value":"27.52배","valueDesc":"2026.03."},
    {"code":"eps","key":"EPS","value":"12,372원"},
    {"code":"cnsPer","key":"추정PER","value":"7.77배"},   // ← 컨센서스 추정 PER (6_research에도 사용)
    {"code":"cnsEps","key":"추정EPS","value":"43,833원"},
    {"code":"pbr","key":"PBR","value":"4.74배"},
    {"code":"bps","key":"BPS","value":"71,907원"},
    {"code":"dividendYieldRatio","key":"배당수익률","value":"0.49%"},
    {"code":"dividend","key":"주당배당금","value":"1,668원"}
  ],
  "dealTrendInfos": [   // ← 일별 외국인/기관/개인 순매수 (12_capital_flow 핵심)
    {"bizdate":"20260615","foreignerPureBuyQuant":"-1,828,940","foreignerHoldRatio":"47.60%",
     "organPureBuyQuant":"+531,697","individualPureBuyQuant":"+1,306,068","closePrice":"337,000"}
  ]
}
```
→ **충당 필드**: `name`, `code`, `market_cap`, `pe_ttm`(PER), `pb`(PBR), `eps`, `bps`, `dividend_yield`, `52주 고/저`, `외인소진율`, `consensus_eps/pe`(추정), 일별 투자자별 순매수.

### ② `GET /api/stock/{code}/basic` → `0_basic` (실시간 시세 + 거래소 구분)
```jsonc
{
  "stockName":"삼성전자","closePrice":"341,250","fluctuationsRatio":"1.26",
  "marketStatus":"OPEN","localTradedAt":"2026-06-16T13:51:21+09:00",
  "stockExchangeType":{"code":"KS","nameKor":"코스피","nameEng":"KOSPI","nationCode":"KOR"},
  "stockExchangeName":"KOSPI",
  "imageCharts": { /* 차트 PNG URL 모음 */ }
}
```
→ **충당 필드**: `price`, `change_pct`(fluctuationsRatio), `currency`(KOR→KRW 하드코딩), **거래소 판별**(`stockExchangeType.code`: `KS`=코스피→`.KS`, `KQ`=코스닥→`.KQ`).

### ③ `GET /api/stock/{code}/finance/annual` · `GET .../finance/quarter` → `1_financials`
연간/분기 재무제표. 행(매출액/영업이익/당기순이익/영업이익률/...) × 열(기간) 매트릭스 구조. `trTitleList`의 `isConsensus:"Y"`는 컨센서스 추정치(미래 기간)를 의미.
```jsonc
{
  "financeInfo": {
    "trTitleList": [
      {"isConsensus":"N","title":"2023.12.","key":"202312"},
      {"isConsensus":"N","title":"2024.12.","key":"202412"},
      {"isConsensus":"N","title":"2025.12.","key":"202512"},
      {"isConsensus":"Y","title":"2026.12.","key":"202612"}   // ← 컨센서스 예상
    ],
    "rowList": [
      {"title":"매출액",   "columns":{"202312":{"value":"2,589,355"}, "202412":{"value":"3,008,709"}, ...}},
      {"title":"영업이익", "columns":{...}},
      {"title":"당기순이익","columns":{...}},
      {"title":"영업이익률","columns":{...}}
      // 실제로는 ROE / 부채비율 / EPS / BPS / 배당 등 더 많은 행 포함(전체 응답에서 파싱)
    ]
  }
}
```
> ⚠️ 단위: 금액은 **억원**(예: `2,589,355` = 258조 9,355억). 콤마 제거 후 float 변환 필요.
> → **충당 필드**: `revenue_history`, `net_profit_history`, `roe_history`, `net_margin`, `gross_margin`, `debt_ratio`, `revenue_growth`(파생 계산), 그리고 **컨센서스 미래 예상치**(6_research의 `consensus_eps_2026/2027`).

### ④ `GET /api/stock/{code}/trend` → `12_capital_flow`
일별 외국인/기관/개인 순매수 + 외국인 보유율 시계열. (②의 `dealTrendInfos`와 동일 스키마이나 더 긴 기간 제공.)
→ **충당 필드**: `main_fund_flow_20d`(외국인+기관을 "주력"으로 간주), `foreignerHoldRatio` 추이, `institutional_history`.

### ⑤ `GET /api/stock/{code}/price?pageSize={n}&page=1` → `2_kline`
일별 OHLCV 시세 (페이지네이션). `closePrice`/`openPrice`/`highPrice`/`lowPrice`는 **콤마 포함 문자열**, `accumulatedTradingVolume`은 정수.
```jsonc
[{"localTradedAt":"2026-06-16","closePrice":"340,500","openPrice":"348,000",
  "highPrice":"352,500","lowPrice":"332,500","accumulatedTradingVolume":24873287,
  "fluctuationsRatio":"1.04"}, ...]
```

### ⑥ `GET https://api.stock.naver.com/chart/domestic/item/{code}/day?startDateTime=YYYYMMDD&endDateTime=YYYYMMDD` → `2_kline` (대량 차트)
**K선 지표 계산에 최적** — float OHLCV + 외국인 보유율을 한 번에 대량 반환. (period: `day`/`week`/`month`)
```jsonc
[{"localDate":"20260102","closePrice":128500.0,"openPrice":120200.0,"highPrice":128500.0,
  "lowPrice":120200.0,"accumulatedTradingVolume":30463279,"foreignRetentionRate":52.37}, ...]
```
→ **충당**: `candles_60d`, `close_60d`. MA/MACD/RSI/KDJ/OBV/Williams%R는 pandas로 직접 계산.

### ⑦ `GET /api/news/stock/{code}?pageSize={n}&page=1` → `15_events`, `17_sentiment`
종목 관련 뉴스 (언론사/제목/본문 미리보기/원문 URL/사진).
```jsonc
[{"items":[{"officeName":"이데일리","datetime":"202606161349","title":"코스피, ...",
  "body":"...","mobileNewsUrl":"https://n.news.naver.com/mnews/article/018/0006307479"}]}]
```

### ⑧ `GET /api/research/stock/{code}?pageSize={n}&page=1` → `6_research` ⭐ **난이도 대폭 하향**
증권사 종목분석 리포트 목록. **목표주가/투자의견이 미리보기 텍스트에 포함**되며, 증권사명·작성일·조회수 제공.
```jsonc
[{"researchCategory":"종목분석","itemCode":"005930","researchId":93538,
  "title":"풀스텍 내재화의 우위","brokerName":"미래에셋증권","writeDate":"2026-06-15",
  "readCount":"18402","previewContent":"...투자의견 '매수' 및 목표주가를 55만원으로 유지한다..."}]
```
> → **충당 필드**: `report_count`, `recent_reports[]`(date/title/broker), `coverage`(고유 증권사 수 집계).
> 단, `target_price_avg`/`rating_distribution`은 `previewContent` 텍스트에서 정규식/LLM 추출 필요(구조화 필드 아님). `integration`의 `cnsPer`/`cnsEps`로 컨센서스 보조.

### ⑨ `GET https://ac.stock.naver.com/ac?q={한글명}&target=stock&st=111` → 이름→코드 해석 ⭐
중국어명 해석(`resolve_chinese_name`)의 한국어 대응. 한글 종목명 → 코드/거래소 매핑.
```jsonc
{"query":"삼성","items":[
  {"code":"005930","name":"삼성전자","typeCode":"KOSPI","typeName":"코스피",
   "url":"/domestic/stock/005930/total","nationCode":"KOR","category":"stock"},
  {"code":"009150","name":"삼성전기","typeCode":"KOSPI", ...}
]}
```
→ `market_router` / `data_sources.resolve_korean_name()`에 직접 사용. KOSPI/KOSDAQ 구분(`typeCode`)도 함께 획득.

## ❌ 유효하지 않은 것으로 확인된 경로 (HTML 에러 반환)
다음 경로들은 200 OK + HTML 에러 페이지를 반환 → **사용 불가, 호출부에서 걸러야 함**:
`/integration`(api.stock 호스트 · `StockConflict`), `/consensus`, `/total`, `/finance/consensus`, `/stockInfo`, `/financeSummary`, `/industryCompare`, `/sameIndustry`, `/estimate`, `/analysis`, `/industry`.

## 🧭 차원별 신 API 커버리지 요약

| 차원 | 신 API로 충당 가능? | 사용 엔드포인트 | 보조 소스 |
|---|---|---|---|
| `0_basic` | ✅ 거의 완전 | `integration` + `basic` | 실제 지배주주는 DART 필요 |
| `1_financials` | ✅ 대부분 | `finance/annual` + `finance/quarter` | ROIC/듀퐁 일부는 파생 계산, DART 보강 |
| `2_kline` | ✅ 완전 | `chart/domestic/item/{code}/day` | 지표는 pandas 자체 계산 |
| `4_peers` | ⚠️ 부분 | (전용 API 미발견) | KRX 업종분류 + 종목별 `integration` 루프 |
| `6_research` | ✅ 대부분 | `research/stock/{code}` + `integration.cnsPer/cnsEps` | 목표가는 텍스트 추출 |
| `10_valuation` | ✅ 현재값 | `integration`(PER/PBR/배당/EPS/BPS) | 5년 분위는 `chart`로 PER 시계열 자체 계산 |
| `11_governance` | ❌ | (신 API 없음) | **DART 필수** (최대주주/임원/담보) |
| `12_capital_flow` | ✅ 한국 핵심 | `trend` + `integration.dealTrendInfos` | 신용잔고/보호예수는 KRX/DART |
| `15_events` | ✅ 뉴스 | `news/stock/{code}` | 공시 원문은 DART |
| `17_sentiment` | ⚠️ 부분 | `news/stock/{code}` + 종목토론실(별도) | DDGS 보조 |
| 이름 해석 | ✅ | `ac.stock.naver.com/ac` | — |

## 🔧 기존 `need_info_type.md` 권장 사항 대비 변경점

1. **6_research 난이도 ★★★ → ★★☆**: FNGuide 유료 API 불필요. 네이버 `research/stock` 무료 API로 증권사 리포트 + 목표주가(텍스트) 확보.
2. **Playwright 의존 제거**: 기본정보/재무/시세/뉴스/리포트 전부 HTTP JSON으로 가능. Playwright는 종목토론실(17_sentiment) 정도만 후순위로 남김.
3. **차트 지표**: 네이버 `chart` API의 float OHLCV가 Yahoo `.KS`보다 한국 시장 데이터 정합성이 좋음(거래정지/우선주/외국인보유율 포함). **2_kline 주 소스를 Yahoo → 네이버 chart로 변경 권장.**
4. **DART는 여전히 필수**: `11_governance`(지배구조), 공시 원문, 정밀 재무(연결/별도 구분, 현금흐름표 세부)는 네이버 API에 없음 → DART OpenAPI 병행 필수.

