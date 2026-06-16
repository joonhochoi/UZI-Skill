<div align="center">

# 유자(UZI) Skills

*"66명의 투자 거장이 당신의 차트를 봐줍니다. 버핏, 자오라오거, 구하이쩌왕이 드디어 한 테이블에 앉았습니다."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.com/product/claude-code)
[![Dimensions](https://img.shields.io/badge/Dimensions-22-brightgreen)]()
[![Investors](https://img.shields.io/badge/Investors-66-orange)]()
[![Methods](https://img.shields.io/badge/Institutional%20Methods-22-red)]()
[![Self-Review](https://img.shields.io/badge/Self--Review-13%20checks-blueviolet)](skills/deep-analysis/scripts/lib/self_review.py)

A주 / 홍콩주 / 미주 · 종목 심층 분석 엔진 · **66인 심사단 × 9대 유파 × 22차원 데이터 × 22종 기관 메서드** · 최신 **v3.9.0**: 신규 심사위원 「구하이쩌왕」—— 타오구바 10년 실전 (8951건 교차 확인 + 5069건 발언) 증류, 33만→3000만 실제 곡선으로 규칙 정립 · 전체 이력은 [업데이트 로그](#-업데이트-로그) 참조

[설치](#설치) · [사용법](#사용법) · [3단계 깊이](#-3단계-분석-깊이v2103-추가) · [Hermes 🆕](INSTALL-HERMES.md) · [심사단](#-66인-심사단) · [Serenity 🆕](#-i그룹--serenity--ai-포지션-병목-헌터) · [기관 메서드](#-22종-기관급-메서드) · [자체 점검 gate](#-기계-자체-점검-gatev29-부터) · [리포트 스크린샷](#-리포트는-어떻게-생겼나) · [FAQ](#-faq) · [테스트 교류](#-테스트-교류) · [Contributors](CONTRIBUTORS.md)

**한국어** | [中文](README.md) | [English](README_EN.md)

</div>

---

## 🚀 30초 시작하기

**어떤 agent든 한 마디 던지면 · 설치 후 바로 사용 가능**. 자세한 설치법은 [설치](#설치) 참조.

| 사용 중인 agent | 이렇게 말하세요 |
|---|---|
| **Claude Code** | `/plugin marketplace add wbh604/UZI-Skill` 그 다음 `/plugin install stock-deep-analyzer@uzi-skill` |
| **Codex / OpenAI CLI** | "https://raw.githubusercontent.com/wbh604/UZI-Skill/main/.codex/INSTALL.md 에 따라 UZI-Skill 설치하고, 600519 분석해줘" |
| **Cursor** | `/add-plugin stock-deep-analyzer` |
| **Gemini CLI** | `gemini extensions install https://github.com/wbh604/UZI-Skill` |
| **Hermes** | ⚠️ `hermes skills install`이 현재 [Skills Guard 오탐](https://github.com/NousResearch/hermes-agent/issues/1006)으로 차단됨 · 원클릭 스크립트로 우회: `curl -fsSL https://raw.githubusercontent.com/wbh604/UZI-Skill/main/install-hermes.sh \| bash` · 자세한 내용은 [INSTALL-HERMES.md](INSTALL-HERMES.md) |
| **OpenClaw / 랍스터** | "https://github.com/wbh604/UZI-Skill 이 주식 분석 스킬 설치해줘" |
| **CLI 직접 사용** | `git clone https://github.com/wbh604/UZI-Skill.git && cd UZI-Skill && pip install -r requirements.txt && python run.py 贵州茅台` |

설치 후 가장 자주 쓰는 4가지 명령어 (어떤 agent에서든 바로 말하기):

```
/stock-deep-analyzer:analyze-stock 贵州茅台    ← 완전 22차원 × 66 심사위원 분석 (5-8분)
/stock-deep-analyzer:quick-scan 002217         ← 30초 속성 판단
/stock-deep-analyzer:scan-trap 002217          ← 살돈판(杀猪盘) 점검
/stock-deep-analyzer:dcf 600519                ← DCF 밸류에이션 특화
```

> 💡 **현재 최신 안정판 v3.8.1** · 전체 이력은 [업데이트 로그](#-업데이트-로그) 참조:
> - **66인 심사단 · 9대 유파** (v3.7 신규 a16z Andreessen / Naval / 젠슨 황 / 머스크 / 고릉 장레이 / Burry / Chanos 등 13인 + 독립 I그룹 Serenity AI 포지션 헌터) · 242개 정량 규칙
> - **Serenity 엄밀화** (v3.8): 8개 페널티 팩터 + 3단계 증거 계층 ("정점 양산 있음"≈90점 vs "테마만"≈60점) + 공급망 8계층 분류
> - **Tier-1 5대 메서드** (v3.8): `/ai-readiness` `/earnings-preview` `/model-update` `/returns` `/rebalance`
> - **다종목 비교 & 포트폴리오** (v3.6): `--versus` 2-4종목 횡적 대결 · `--portfolio` CSV 포트폴리오 건강도 · 다크 모드 + sticky TOC + 용어 툴팁
> - **유파 시각 고정** (v3.5): `--school A-I` 한 유파의 판단만 보기 · 리포트에 SCHOOL LOCK 배너
> - **아키텍처**: v3.0 pipeline 기본 메인 · 632 tests 전부 통과 · v2.x API 100% 하위 호환 (`UZI_LEGACY=1`로 구경로 복귀)
>
> **Hermes 사용자**: `hermes skills install`이 상위 Skills Guard에 의해 오탐됨 · 원클릭 스크립트로 설치: `curl -fsSL https://raw.githubusercontent.com/wbh604/UZI-Skill/main/install-hermes.sh | bash` · 자세한 내용은 [INSTALL-HERMES.md](INSTALL-HERMES.md).

---

## 💬 그룹 채팅 없음! 왜 교류 그룹도 별 내용 없는데 차단당하는지 모르겠지만...

그룹 만들면 차단당합니다. 의견 있으신 분은 직접 추가해주세요. 플러그인 자체나 다른 재미있는 프로젝트, 퀀트에 대해서만, 개별 종목은 이야기하지 않습니다.

<p align="center">
  <img src="docs/screenshots/8501bb4280cc56c809c0a19619e49c82.jpg" width="300" alt="그룹 만들면 차단당합니다. 의견 있으신 분은 직접 추가해주세요. 플러그인 자체나 다른 재미있는 프로젝트, 퀀트에 대해서만, 개별 종목은 이야기하지 않습니다." />
</p>

> 추가 인원이 많으니, 용건을 꼭 메모해주세요. 그래야 무슨 문제인지 알 수 있습니다..

---

## 감사 인사
AI 배우려면 L站!
[Linux.do](https://linux.do/) 커뮤니티 지원에 감사드립니다.

## 이게 뭔가요

한 마디로: 종목 하나 입력하면, Claude가 당신의 개인 애널리스트가 되어, 22개 차원의 데이터를 돌리고, 17종 월스트리트 분석 모델을 적용하고, 51명의 완전히 다른 투자 스타일을 가진 거장들이 각자 점수를 매긴 후, 600KB짜리 Bloomberg 스타일 리포트를 뱉어냅니다.

```
/stock-deep-analyzer:analyze-stock 国盾量子
```

5-8분 후에 당신이 얻는 것:
- **HTML 리포트** — 브라우저로 바로 열 수 있고, 자체 포함형, 오프라인에서도 볼 수 있음
- **모멘츠 세로 이미지** — 1080×1920, 바로 공유
- **단체 채팅 전황 보고** — 1920×1080
- **한 문단 요약** — 복사 붙여넣기로 단체방에 바로 공유

## 왜 만들었나

예전에 종목 하나 보는 과정: 동방재부에서 기본면 → 퉁화순에서 K선 → 설구에서 대V 발언 스크롤 → 리포트 시스템에서 매도 측 관점 찾기 → Excel로 DCF 계산 → 결과는 사도 손실.

이 작업들은 본질적으로 "정보 수집 → 다각도 분석 → 결론 도출"인데, AI에게 전부 맡기면 안 될까?

시중에 있는 것들을 둘러봤더니, 세 문단짜리 쓸데없는 말을 출력하는 GPT 래퍼거나, 사용할 수 없는 기관 터미널이었습니다. Anthropic이 [financial-services-plugins](https://github.com/anthropics/financial-services-plugins)를 냈는데, 방법론은 좋지만(DCF / Comps / LBO 같은 것들), 완전히 미주 시각 + 전부 유료 데이터 소스였습니다.

그래서 직접 만들었습니다. **전부 무료 데이터 소스, API key 제로, A주 바로 실행 가능.**

---

## 설치

어떤 agent를 쓰든, **그냥 한 마디 던지면 됩니다**:

### Claude Code

```
/plugin marketplace add wbh604/UZI-Skill
/plugin install stock-deep-analyzer@uzi-skill
```

설치 후 `/stock-deep-analyzer:analyze-stock 贵州茅台` 라고 말하세요.

> ⚠️ **반드시 `stock-deep-analyzer:` 네임스페이스 접두사 필수**
>
> Claude Code에 plugin 설치 후, 모든 skill/command는 `stock-deep-analyzer:`로 시작합니다.
> 일부 환경에서는 짧은 이름(`/analyze-stock`)이 자동으로 해석되지 않을 수 있습니다——안전하게 항상 전체 이름을 사용하세요:
>
> - `/stock-deep-analyzer:analyze-stock <ticker>`
> - `/stock-deep-analyzer:quick-scan <ticker>`
> - `/stock-deep-analyzer:scan-trap <ticker>`
> - `/stock-deep-analyzer:dcf <ticker>`
> - `/stock-deep-analyzer:ic-memo <ticker>`
> - `/stock-deep-analyzer:investor-panel <ticker>`
> - `/stock-deep-analyzer:trap-detector <ticker>`
> - `/stock-deep-analyzer:deep-analysis <ticker>`
> - 등 총 14개
>
> Cursor / Gemini CLI / Codex도 동일: **항상 `/stock-deep-analyzer:<cmd>` 전체 이름 사용**,
> 짧은 이름 해석 실패 방지.

### Codex

Codex에게 직접 말하세요:

> https://raw.githubusercontent.com/wbh604/UZI-Skill/main/.codex/INSTALL.md 의 안내에 따라 UZI-Skill을 설치하고, 贵州茅台 심층 분석해줘.

### OpenClaw / 랍스터

랍스터에게 말하세요:

> https://github.com/wbh604/UZI-Skill 이 주식 분석 스킬 설치해주고, 설치 후 贵州茅台 분석해줘.

### Cursor

```
/add-plugin stock-deep-analyzer
```

그런 다음 "贵州茅台 분석해줘" 라고 말하세요.

### Gemini CLI

```bash
gemini extensions install https://github.com/wbh604/UZI-Skill
```

### OpenCode

OpenCode에게 말하세요:

> https://raw.githubusercontent.com/wbh604/UZI-Skill/main/.opencode/INSTALL.md 에 따라 설치하고 贵州茅台 분석해줘.

### Windsurf / Devin / 기타 Agent

이 문장을 던지세요:

> https://github.com/wbh604/UZI-Skill 클론하고, AGENTS.md 읽어서 사용법 파악한 다음, 贵州茅台 심층 분석해줘.

### 📱 컴퓨터 앞에 없을 때?

어떤 agent에게든 말하세요:

> 贵州茅台 분석해줘, 원격 모드로, 휴대폰에서 볼 수 있는 공개 링크 생성해줘.

agent가 자동으로 `--remote`로 Cloudflare Tunnel을 시작해서, `https://xxx.trycloudflare.com` 링크를 줍니다.

---

## 사용법

### 완전 심층 분석 (5-8분)

```
/stock-deep-analyzer:analyze-stock 水晶光电
/stock-deep-analyzer:analyze-stock 002273
/stock-deep-analyzer:analyze-stock 00700.HK
/stock-deep-analyzer:analyze-stock AAPL
```

### 특화 명령어

> 모두 `/stock-deep-analyzer:` 접두사를 붙여야 실행이 보장됩니다.

| 명령어 | 하는 일 |
|---|---|
| `/stock-deep-analyzer:dcf 600519` | DCF 밸류에이션 · WACC + 5×5 민감도 테이블 |
| `/stock-deep-analyzer:comps 002273` | 동종 비교 · PE/PB 분위 분석 |
| `/stock-deep-analyzer:lbo 600519` | LBO 테스트 · PE 바이어가 얼마나 IRR 벌 수 있는지 |
| `/stock-deep-analyzer:initiate 002273` | 기관 최초 커버리지 리포트 · JPM/GS 형식 |
| `/stock-deep-analyzer:ic-memo 002273` | 투자위원회 메모 · 3개 시나리오 수익 |
| `/stock-deep-analyzer:earnings 002273` | 실적 해석 · beat/miss 감지 |
| `/stock-deep-analyzer:catalysts 002273` | 촉매 캘린더 · 향후 60일 |
| `/stock-deep-analyzer:thesis 002273` | 투자 로직 추적 · 5개 기둥 모니터링 |
| `/stock-deep-analyzer:screen 002273` | 5종 퀀트 스크리닝 · value/growth/quality |
| `/stock-deep-analyzer:dd 002273` | 실사 체크리스트 · 5개 워크플로우 21항목 |
| `/stock-deep-analyzer:quick-scan 002273` | 30초 속성 판단 |
| `/stock-deep-analyzer:panel-only 600519` | 66 심사위원 투표만 보기 |
| `/stock-deep-analyzer:scan-trap 002273` | 살돈판 점검 |
| `/stock-deep-analyzer:segmental-model 300308` | 사업부별 매출 bottom-up 모델링 · 3 시나리오 × 3년 projection · DCF 역교차 검증 |
| `/stock-deep-analyzer:ai-readiness 002273` | 🆕 v3.8 · 단일 종목 AI 준비도/포지션 평가 · 3단계 gate → Go/Wait + 등급 |
| `/stock-deep-analyzer:earnings-preview 002273` | 🆕 v3.8 · 실적 **발표 전** 프리뷰 · 컨센서스 + Bull/Base/Bear + 내재 변동성 |
| `/stock-deep-analyzer:model-update 002273` | 🆕 v3.8 · 신규 실적/가이던스 증분 업데이트 모델 · 가정 delta → DCF/thesis 영향 |
| `/stock-deep-analyzer:returns` | 🆕 v3.8 · 포트폴리오 수익 귀속 · 보유/업종별 분해 + Top 기여/발목 |
| `/stock-deep-analyzer:rebalance` | 🆕 v3.8 · 보유종목별 리밸런싱 · 드리프트 + 거래 목록 + A주 인지세/수수료 회전 비용 |

### CLI 직접 실행 고급 활용법 (git clone 사용자)

```bash
python run.py 600519.SH --depth lite --no-browser   # 30-60초 빠른 모드
python run.py 300394.SZ --school I                  # Serenity 포지션 시각만 보기 (A-I 9파 중 선택)
python run.py --versus 茅台 五粮液 002594.SZ         # 2-4종목 횡적 대결 · ★WIN 하이라이트
python run.py --portfolio holdings.csv             # CSV 포트폴리오 · 가중 점수 + 건강도
python run.py 600519.SH --output-dir /tmp/out      # SaaS 통합 · index.html + meta.json
```

---

## 🎯 점수 보정 (v2.11)

사용자 피드백 "마오타이 47점", "65점 넘은 적 없음"—— 진단 결과 두 곳의 공식이 지나치게 엄격, v2.11 보정:

| 변경 | 구 (v2.9.1) | 신 (v2.11) | 영향 |
|---|---|---|---|
| **verdict 임계값** | 85/70/55/40 | **80/65/50/35** | 85 이상(「집중 매수 가치」구간 공석)인 종목이 없었음, 5점 하향으로 백마/진짜 강세주가 「기다릴 만함」구간 진입 가능 |
| **consensus neutral 가중치** | 0.5 (반가중) | **0.6** | (v2.11 보정 시 51 심사위원) 가치파+유자 35인이 보수적 편향, neutral 가중치 0.5로 백마 consensus 37에 불과, 0.6이 「함정은 아니지만 마음에 드는 건 아님」의 실제 의미에 더 가까움 |

공식 (불변): `overall = fund_score × 0.6 + consensus × 0.4`

전형적 백마 (예: 마오타이) 예상:
- v2.9.1: `fund=62 consensus=45 → overall 55 → 관망 우선`
- v2.11: `fund=62 consensus=50 → overall 57 → 관망 우선` (하지만 「기다릴 만함」경계에 더 가까워, 백마 랠리 시작 시 65 진입 용이)

두 구간 합산 영향 ~5-8점. **진짜 함정은 여전히 < 35 → 회피**, 점수 식별력은 오히려 상승.

진단 필드 `panel.json::consensus_formula.version = "v2.11 · (bullish + 0.6*neutral) / active"` 감사 가능.

회귀 테스트: `tests/test_v2_11_scoring_calibration.py` 8개 케이스.

전체 보정 기록은 [BUGS-LOG.md v2.11.0 섹션](docs/BUGS-LOG.md#v2110-2026-04-18--评分校准--用户反馈驱动) 참조.

---

## 🎚️ 3단계 분석 깊이 (v2.10.3 추가)

사용자가 직접 분석 강도를 선택——빠른 생각 / 보통 / 깊이 파기:

```bash
python run.py 600519 --depth lite     # ⚡ 속성 판단 모드 (1-2분)
python run.py 600519                   # 📊 표준 분석 (5-8분) · 기본값
python run.py 600519 --depth deep      # 🔬 심층 연구 (15-20분)
```

또는 환경 변수로:

```bash
export UZI_DEPTH=lite       # 또는 medium / deep
python run.py 600519
```

### 3단계 차이一览

| 차원 | ⚡ **lite** 속성 판단 | 📊 **medium** 표준 | 🔬 **deep** 기관급 |
|---|---|---|---|
| **예상 소요 시간** | 1-2분 | 5-8분 | 15-20분 |
| **fetcher 차원** | 핵심 7차원 | 전체 22차원 | 전체 22차원 + 강화 fallback |
| **심사위원 수** | 10인 대표 | 66인 완전 | 66인 + **Bull-Bear 구조화 토론** |
| **기관 메서드** | DCF만 | 전체 17종 | 전체 17종 + **Segmental Build-Up** |
| **ddgs 정성 쿼리** | **전부 skip** (토큰 절약) | 필요시 · 예산 30회 | 전부 실행 · 예산 60회 |
| **fund_holders** | Top 5 완전 실적 | Top 20 완전 + 나머지 목록 | Top 100 완전 |
| **자체 점검 gate** | critical block | critical block · warning은 ack 가능 | 양쪽 모두 block |
| **Playwright 폴백** (v2.13.1) | ❌ 완전 비활성화 | opt-in · `UZI_PLAYWRIGHT_ENABLE=1` · **6차원** (4_peers/8_materials/15_events/17_sentiment/7_industry/14_moat) | ✅ 기본 활성화 · **10차원** (medium 6 + 3_macro/13_policy/18_trap/19_contests) · 최초 y/n 상호작용으로 Chromium 설치 |
| **토큰 소비 (Codex)** | 가장 적음 | 중간 | 최대 |
| **적용 시나리오** | 슬쩍 보기 / 상사가 갑자기 물어봄 / ETF 구성종목 사전 판단 | 일상 심층 분석 · 리포트 작성 | 투자위원회 메모 · 포지션 구축 전 깊이 파기 |

### 자동 강등 전략

- **최초 설치** / `.cache/_global` 비어있음 → 자동 lite 전환 (최초 콜드 스타트 시간 절약)
- **네트워크 사전 점검 3+ 도메인 불통** → 자동 lite 전환 (멈춤 방지)
- 수동 `--depth`는 항상 자동 판단을 덮어씀

### 실전 선택

| 질문 | 추천 단계 |
|---|---|
| "이 종목 살 수 있는지 좀 봐줘" | `medium` (기본값) |
| "15분 안에 결론 줘" | `lite` |
| "내일 상사가 투자위원회에서 볼 거야" | `deep` (Bull-Bear 토론 + bottom-up segmental 포함) |
| "ETF 코드 입력했어 (시스템이 구성종목 선택 제안)" | `lite` (구성종목 빠른 사전 판단) |
| "Codex 환경 / 최초 설치" | 신경 쓸 필요 없음 · 자동 lite |

### 명령어 매핑 (암시적 단계)

| 명령어 | 암시적 단계 |
|---|---|
| `/stock-deep-analyzer:quick-scan 600519` | lite |
| `/stock-deep-analyzer:panel-only 600519` | lite |
| `/stock-deep-analyzer:analyze-stock 600519` | medium (기본값) |
| `/stock-deep-analyzer:ic-memo 600519` | deep |
| `/stock-deep-analyzer:initiate 600519` | deep |

---

## 🎭 66인 심사단

템플릿 멘트가 아닙니다. 각 인물은 자신만의 **정량 규칙 세트**(총 236개)를 가지며, 제시하는 조언은 반드시 구체적으로 어떤 규칙에 적중했는지 인용해야 합니다.
v3.7.0부터 신규 **13인의 신진 테크 거물** + 독립 **I그룹 Serenity (AI 포지션/병목 헌터)** 추가; v3.9.0에 10년 실전 교차 확인에서 증류한 **구하이쩌왕** 추가, 9대 유파 커버:

| 그룹 | 스타일 | 인원 | 대표 인물 |
|---|---|---|---|
| A | 클래식 가치 | 6 | 버핏 · 그레이엄 · 멍거 · 피셔 · 템플턴 · 클라만 |
| B | 성장 투자 | 9 | 린치 · 우드 · 틸 · **Andreessen (a16z)** · **Gurley (Benchmark)** · **Naval** · **Gerstner (Altimeter)** · **Chamath** |
| C | 매크로 헤지 | 7 | 소로스 · 달리오 · 하워드 막스 · 드러켄밀러 · 로버트슨 · **Burry (빅쇼트)** · **Chanos (숏 헌터)** |
| D | 기술 트렌드 | 4 | 리버모어 · 미네르비니 · 다바스 · 간 |
| E | 중국 가치투자 | 7 | 돤융핑 · 장쿤 · 주사오싱 · 셰즈위 · 펑류 · 덩샤오펑 · **장레이 (고릉)** |
| F | A주 유자 | 24 | 장멍주 · 자오라오거 · 차오구양자 · **구하이쩌왕 🆕** (타오구바 10년 실전 증류) · 베이징차오자 … |
| G | 퀀트 시스템 | 4 | 사이먼스 · 소프 · 데이비드 쇼 · **Asness (AQR)** |
| H | 테크 리더파 🆕 | 4 | **젠슨 황 (NVIDIA)** · **머스크 (Tesla)** · **Sam Altman (OpenAI)** · **Saylor (MSTR)** |
| I | AI 포지션/병목 헌터 🆕 | 1 | **Serenity (@aleabitoreddit)** |

> v3.7.0 (2026-06) 신규 13인은 굵게 표시. **H그룹**은 자신의 산업 체인 시각을 가진 테크 CEO; **I그룹 Serenity**는 단독 특별 심사위원 (아래 참조).

**예시**:

> **버핏**이 수정광전에 62점 · 중립
> "관망: 해자 27/40 가시적; 그러나 ROE 5년 최저 6.7%, 달성률 0/5"
> ✅ 부채비율 30% 보수적 · ❌ ROE 5년 최저 6.7%

> **젠슨 황**이 어떤 CPO 광모듈 주에 100점 · 매수
> "AI 컴퓨팅 체인 위에 있음 · 데이터센터 Capex 직접 수혜 · 매출총이익률 ≥50% 가격 결정력 강함——이것은 광속 무어의 법칙의 수혜자."
> ✅ AI 컴퓨팅 수요 강한 연관 · ✅ CUDA/생태계 바인딩 깊음

> **클라만**이 수정광전에 0점 · 매도
> "매도 핵심: 30% 안전마진 없음"

---

## 🧠 I그룹 · Serenity · AI 포지션/병목 헌터

> **중량급 캐릭터**: 2026년 X(트위터)에서 폭발적 인기를 얻은 해외 개인 투자자 [@aleabitoreddit](https://x.com/aleabitoreddit).
> 단독 그룹, 단독 점수——그녀의 투자법은 극도로 집중적이고 극도로 반컨센서스이며, 어떤 기관 거장과도 다릅니다.

### 그녀는 누구인가

- 자술 배경: **전 AI 연구 과학자 · Nature 논문 저자 · 전 RISC-V 재단 멤버 · 반도체/광통신 엔지니어**
- 2D 아바타, 익명, 얼굴 비공개, 강의 판매 안 함, 따라하기 유도 안 함, 연구 **전부 무료 공개**, X 팔로워 30만+
- 대표 전투: 약 1년 앞서 InP 인화인듐 기판 병목주 **$AXTI ($12 → $70+, 최고 $115–140)** 적중, 2026 Q1 IntelliEPI CEO가 공개적으로 "InP 부족이 전체 AI 인프라의 병목"이라고 인정

> ⚠️ 신원과 수익은 모두 **자술/미디어 전언, 제3자 감사 미실시**, 각 출처의 숫자는 서로 모순됨. 본 프로젝트는 그녀의 **방법론**만을 하나의 분석 시각으로 증류한 것이며, 실제 전적을 인정하는 것은 아님. 자세한 내용은 [`docs/serenity-research-dossier.md`](docs/serenity-research-dossier.md) (전체 20+ 출처 항목별 아카이브) 참조.

### UZI-Skill 내에서의 역할

그녀의 **「AI 산업 체인 병목/초크포인트 이론(Chokepoint Theory)」**을 정량화 가능한 심사위원으로 만듦——
**AI 리더를 사지 않음** (엔비디아 같은 이미 충분히 가격 반영된 종목), 대신 공급망을 따라 상류로 분해하여, "전 세계가 우회할 수 없고, 공급이 가장 바닥나기 쉬운" 2, 3선 상류 소형주를 찾아, 시장이 가격에 반영하기 전에 매복.

```
리더가 사들여짐 → 공급망 따라 상류로 분해 → 가장 대체하기 어려운环节 찾기 → 그 环节에서 공급이 가장 타이트한 소형주 찾기 → 사전 매복
```

**핵심 점수 로직 「포지션이 태도를 결정」**——밸류에이션 싼지, 성장 빠른지 안 보고, 오직 하나의 변수만 봄: **이 회사의 제품이 현재 AI 웨이브에서 남의 목을 조르고 있는가**.

| 판정 | 태도 |
|---|---|
| 조르고 있음 (대체 불가 + 공급 병목 + 가격 미반영) | 🟢 **매수 / 집중 매수 가능** |
| AI 체인 위에 있지만 포지션이 단단하지 않음 (대체 가능 / 생산능력 충분) | ⚖️ 중립 · 검증 대기 |
| 포지션 못 잡음 / 그냥 컨셉에 편승 / AI 체인에 없음 | 🔴 **바로 skip** (백주, 은행 해자 만점도 0점) |

어떤环节이 "포지션 포인트"인지 판단하는 세 가지: ① **대체 어려움** (공급업체/소재/공정 교체에 얼마나 걸리는지, 길수록 좋음 → `14_moat` 전환 비용) ② **공급 타이트** (생산능력이 AI 수요 곡선을 따라잡을 수 있는지, 못 따라잡을수록 좋음 → `7_industry`) ③ **가격 미반영** (시장이 여전히 "사이클주/구반도체/틈새 소재"라는 옛 내러티브로 보고 있음 → `5_chain` + `15_events`).

### Serenity 시각만 단독 실행하는 법

```bash
python run.py 300394.SZ --school I       # Serenity의 "포지션 잡았는지" 판단만 보기
python run.py NVDA --school H             # H그룹 테크 리더파만 보기 (젠슨 황/Musk/Altman/Saylor)
```

> 방법론 6단계법 + alpha 5차원은 [`skills/deep-analysis/references/fin-methods/serenity-bottleneck.md`](skills/deep-analysis/references/fin-methods/serenity-bottleneck.md) 참조;
> 어조 라이브러리 + 점수 규칙은 [`skills/investor-panel/references/group-i-serenity.md`](skills/investor-panel/references/group-i-serenity.md) 참조.

---

## 📐 22종 기관급 메서드

[anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins)에서 방법론을 이식, A주 파라미터에 맞게 조정 (rf=2.5% / ERP=6% / 세율 25% / 종료가치 g=2.5%). 1차 17종 + v3.8.0 Tier-1 추가 5종 (`/ai-readiness` `/earnings-preview` `/model-update` `/returns` `/rebalance` · [특화 명령어](#특화-명령어) 참조):

**밸류에이션 모델링**
- DCF (WACC 분해 + 2단계 FCF + Gordon Growth 종료가치 + 5×5 민감도 히트맵)
- Comps 동종 비교 (PE / PB / EV-EBITDA 분위 + 내재 목표가)
- 3표 예측 (5년 IS / BS / CF 연동)
- Quick LBO (PE 펀드 시각 IRR 교차 검증)
- M&A 증액/희석 모델

**연구 워크플로우**
- 최초 커버리지 리포트 (JPM/GS/MS 형식 · 등급 + 목표가 + 논점 + 리스크)
- 실적 beat/miss 해석
- 촉매 캘린더 (실제 이벤트 추출 + 미래 사전 배치 + 영향 등급)
- 투자 로직 추적 (5개 기둥 건강도)
- 모닝 브리프 · 퀀트 스크리닝 · 업종 개요

**심층 의사결정**
- IC 투자위원회 메모 (8개 섹션 · Bull/Base/Bear 3개 시나리오)
- Porter 5 Forces + BCG 매트릭스
- DD 실사 체크리스트 (5개 워크플로우 21항목 · 자동 완료 상태 표시)
- 단위 경제학 · 가치 창조 계획 · 포트폴리오 리밸런싱

---

## 📸 리포트는 어떻게 생겼나

> 아래 스크린샷은 모두 수정광전 (002273.SZ)의 실제 분석 결과입니다.

### 종합 점수 + 핵심 결론

<img src="docs/screenshots/hero-score.png" width="700" />

### 다공 대분기 · The Great Divide

피셔 100점 vs 클라만 96점, 3라운드 상호 공방, 매 라운드 구체적 숫자 인용.

<img src="docs/screenshots/great-divide.png" width="700" />

### 65인 심사단 · 심판석

각 인물 하나의 등——녹색 매수, 적색 매도, 회색 중립.

<img src="docs/screenshots/jury-seats.png" width="700" />

### 채팅방 모드

심사위원들이 자신의 언어 스타일로 발언, 적중한 구체적 규칙 인용.

<img src="docs/screenshots/chat-room.png" width="700" />

### DCF 밸류에이션 · 5×5 민감도 히트맵

WACC 6.96% · 내재가치 ¥20.73 · 안전마진 -28.6%, 색상은 진녹색(저평가)에서 진적색(고평가)까지.

<img src="docs/screenshots/dcf-model.png" width="700" />

### IC 투자위원회 메모 · 3개 시나리오 수익

Bull ¥26.95 / Base ¥20.73 / Bear ¥14.51, 각 시나리오에 확률과 가정 포함.

<img src="docs/screenshots/ic-memo.png" width="700" />

### 22차원 심층 카드

각 차원에 독립 시각화——K선 캔들 차트 / PE Band / 레이더 차트 / 공급망 흐름도 / 온도계 / 도넛 차트.

<img src="docs/screenshots/deep-scan.png" width="700" />

### 모멘츠 세로 이미지 · 원클릭 공유

<img src="docs/screenshots/share-card.png" width="300" />

---

## 🔧 데이터 소스

전부 무료, API key 제로:

| 데이터 | 주 소스 | 예비 |
|---|---|---|
| 실시간 시세 / PE / 시총 | 동방재부 push2 | 설구 → 텐센트 → 시나 → 바이두 |
| 재무제표 이력 | akshare | 설구 f10 |
| K선 / 기술 지표 | akshare | yfinance |
| 용호방 / 북향 / 양융 | akshare | 동재 |
| 리포트 / 공시 | 쥐차오 cninfo + akshare | 퉁화순 |
| 홍콩주 | akshare hk | yfinance |
| 미주 | yfinance | akshare us |
| 매크로 / 정책 / 여론 / 살돈판 | DuckDuckGo web search | — |
| **소셜 핫 리스트** (v2.12 추가) | **웨이보 / 즈후 / 바이두 / 더우인 / 토우티아오 / B스테이션 · 각 플랫폼 공식 JSON API** | 5분 파일 캐시 · 단일 플랫폼 실패가 다른 플랫폼에 영향 없음 |

다층 fallback 체인 — 한 소스가 죽으면 자동으로 다음으로 전환.

### 📱 6개 플랫폼 소셜 핫 리스트 (v2.12 추가)

개인 투자자 감정과 살돈판 테마는 종종 더우인/샤오홍슈/웨이보에서 먼저 발효되며, DuckDuckGo는 스캔하지 못함. v2.12부터 `17_sentiment` 차원이 자동 조회:

- **웨이보 핫서치** · `weibo.com/ajax/side/hotSearch` 수집 · 50개 실시간 핫서치
- **즈후 핫 리스트** · `zhihu.com/api/v3/feed/topstory/hot-list-web` 수집 · 50개
- **바이두 핫서치** · `top.baidu.com/api/board` 수집 · 실시간 리스트
- **더우인 핫 포인트** · `douyin.com/aweme/v1/web/hot/search/list/` 수집 · 검색 핫 포인트
- **토우티아오 핫 리스트** · `toutiao.com/hot-event/hot-board/` 수집 · 핫 이벤트
- **B스테이션 핫서치** · `s.search.bilibili.com/main/hotword` 수집 · 전역 핫서치

종목명 (약칭 포함, 예: "贵州茅台"→"贵州"/"茅台")이 핫 리스트 제목에 적중 → 감정 열도에计入 + 구체적 항목 기록.

데이터 구조: synthesis의 `17_sentiment.data.hot_trend_mentions`:
```json
{
  "stock_name": "贵州茅台",
  "platforms_ok": 6,
  "total_hits": 3,
  "by_platform_count": {"weibo": 2, "zhihu": 1, ...},
  "mentions": { "weibo": [{"rank":3, "title":"茅台 1499 회귀", ...}], ... }
}
```

> 감사: 본 모듈 설계는 [run-bigpig/jcp](https://github.com/run-bigpig/jcp) (구채판 AI)의 `hottrend` 서비스 구현을 참조했습니다.

### 🔑 선택 사항: 동방재부 먀오샹 Skills API (v2.3 추가)

2026년 `push2.eastmoney.com`이 본토 네트워크에서 자주 안티크롤링 차단됨. 만약
`MX_APIKEY`를 설정하면, UZI-Skill이 우선적으로 공식 NLP API를 사용:

- **중문명 교정**: "北部港湾" → 자동으로 "北部湾港(000582.SZ)" 식별
- **시세 스냅샷**: push2를 우회하여 직접 최신가/시총/PE/PB/업종 획득

설정:
```bash
cp .env.example .env
# .env 편집하여 MX_APIKEY 입력 (무료 신청: https://dl.dfcfs.com/m/itc4)
```

키 없을 시 전부 XueQiu/akshare 체인으로 폴백, 기존 사용자 제로 인지.

### 🔓 로그인 필요 데이터 소스 (v2.7.1 추가)

일부 데이터 소스가 2026년부터 로그인 인증 추가, UZI-Skill은 기본적으로 **능동적으로 로그인 창을 띄우지 않음** (무인值守 유지).
사용자가 필요에 따라 활성화 가능:

| 데이터 소스 | 차원 | 활성화 방법 | 영향 |
|---|---|---|---|
| **XueQiu cubes_search.json** | `19_contests` 실전 대회 보유 | `export UZI_XQ_LOGIN=1` 그 다음 `python -m lib.xueqiu_browser login` (일회성 브라우저 로그인 팝업) | 미활성화: 리포트 19_contests에 "⚠️ XueQiu 로그인 필요, 0 cube" 표시; 활성화 후 설구 50+ 실전 포트폴리오가 본 주식 보유 중인 것 확인 가능 |

#### XueQiu 로그인 절차

```bash
# 1. 환경 변수 활성화 (일회성, .zshrc에 추가 가능)
export UZI_XQ_LOGIN=1

# 2. 일회성 로그인 (최초 실행 시 헤드 브라우저 팝업, 로그인 후 터미널로 돌아와 엔터)
python -m lib.xueqiu_browser login
# → 브라우저 팝업, 수동 계정/비번 / 위챗 QR 스캔 / SMS 로그인
# → 로그인 성공 후 터미널로 돌아와 엔터, 쿠키 영구화 ~/.uzi-skill/playwright-xueqiu/

# 3. 이후 분석 실행 시 자동 로그인 상태 재사용 (쿠키 보통 ≥ 30일 유효)
python run.py 贵州茅台 --no-browser
# 19_contests 차원에 실제 설구 포트폴리오 수 + 수익률 분포 표시

# 4. run.py 직접 실행 시 활성화하려면 flag 추가
python run.py 贵州茅台 --enable-xueqiu-login
```

#### 로그인 건너뛰기 (기본 동작)

로그인不想? 아무것도 안 하면 됩니다. XueQiu 차원은 명확하게 `⚠️ 로그인 필요, 0 cube`로 표시,
다른 21개 차원은 정상 작동.

#### 상태 조회
```bash
python -m lib.xueqiu_browser status
# 표시: profile dir / 쿠키 존재 여부 / 활성화 여부
```

### 🚨 데이터 갭 처리 방법 (v2.3)

만약 일부 필드를 스크립트가 가져오지 못하면 (네트워크 제한 / 신규주 / 거래정지), pipeline은 **기본값으로 얼버무리지 않음**:

1. `_data_gaps.json` 생성하여 각 갭의 권장 복구 동작 나열 (브라우저 / MX / WebSearch / 추론)
2. Agent가 [HARD-GATE-DATAGAPS](skills/deep-analysis/SKILL.md)에 따라 항목별로 보완 시도
3. 정말 보완 불가 → `agent_analysis.json`에 `data_gap_acknowledged` 명시적 인정
4. HTML 리포트 상단에 주황색 배너 표시 + 관련 필드 "—" 표시 및 취소선

이렇게 하면 항상 "이 주식이 정말 사기에 부적합한지" vs "단지 데이터를 못 가져온 건지" 구분 가능.

### 🌐 네트워크 제한 환경 (v2.4 추가)

UZI-Skill은 본토와 해외 모두에서 실행 가능하지만, 병목이 다르므로 상황에 맞게 대처 권장:

**본토 네트워크 · `pip install` 실패 시 어떻게 하나?**

`run.py`와 `setup.sh`가 자동으로 국내 미러 시도 (칭화 → 알리클라우드 → 중과대),
따라서 일반적인 경우 아무것도 안 해도 됩니다. 수동 지정하려면:

```bash
pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn
```

**Codex / 해외 agent · 데이터 소스 접근 느릴 때 어떻게 하나?**

국내 데이터 소스 (특히 `push2.eastmoney.com`)는 해외에서 접근 시 자주 타임아웃. **강력히 권장
`MX_APIKEY` 설정** (무료 신청 → https://dl.dfcfs.com/m/itc4), 이것은
`mkapi2.dfcfs.com`을 경유하여 국내외 모두 통하며, 동시에 자연스럽게 중문명 교정 능력 보유.

```bash
cp .env.example .env
# .env 편집하여 MX_APIKEY 입력
python run.py 贵州茅台
```

**양쪽 모두 불통**: agent는 `_data_gaps.json` / `_resolve_error.json`을 보존해야 하며,
네트워크 복구 후 바로 `stage2()` 실행으로 이미 수집된 데이터 재사용 가능, 처음부터 다시 할 필요 없음.

자세한 내용은 [AGENTS.md · 네트워크 제한 환경](AGENTS.md)의 시나리오 A/B/C 속성 참조.

---

## 📁 프로젝트 구조 (v3.x 아키텍처)

```
UZI-Skill/
├── run.py                              # ✅ 사용자 진입점 (python run.py <ticker>)
├── AGENTS.md / CLAUDE.md / CODEX.md    # agent 지침 (v3.2 CODEX.md 추가)
├── GEMINI.md                           # Gemini CLI 가이드
├── RELEASE-NOTES.md                    # 전체 버전 로그
├── docs/BUGS-LOG.md                    # 버그 등록 + 재발 방지 체크리스트
├── .claude-plugin/plugin.json          # Claude Code 매니페스트
├── .cursor-plugin/plugin.json          # Cursor 매니페스트
├── gemini-extension.json               # Gemini 매니페스트
├── commands/                           # 20개 slash commands
├── personas/                           # 51개 YAML persona (v2.15.0)
├── skills/
│   ├── deep-analysis/                  # ★ 메인 skill (주식 분석)
│   │   ├── SKILL.md
│   │   ├── references/                 # 방법론 문서
│   │   ├── assets/                     # HTML 템플릿 + 65 아바타 svg
│   │   └── scripts/                    # ← 모든 Python 비즈니스 코드
│   │       ├── run_real_test.py        # 레거시 stage1/stage2 (v3.1 다이어트 735줄)
│   │       ├── assemble_report.py      # HTML 셸 (v3.2 다이어트 587줄)
│   │       ├── fetch_*.py              # 22 fetcher · 독립 CLI로도 사용 가능
│   │       ├── compute_deep_methods.py # 기관 모델링
│   │       ├── tests/                  # 642 pytest
│   │       └── lib/
│   │           ├── pipeline/           # 🆕 v3.0 파이프라인 아키텍처 (기본 경로)
│   │           │   ├── run.py          # run_pipeline 오케스트레이션 진입점
│   │           │   ├── collect.py      # 동시성 collector (22 adapter)
│   │           │   ├── score.py        # scoring 단계 (rrt 순수 함수 호출)
│   │           │   ├── synthesize.py   # stage2 씬 래퍼
│   │           │   ├── score_fns.py    # 🆕 v3.1 · 1228줄 순수 함수
│   │           │   ├── preflight_helpers.py  # 🆕 v3.1 · 네트워크/ticker 사전 점검
│   │           │   ├── fetchers/registry.py  # 22 adapter 팩토리
│   │           │   └── renderer/       # 21개 renderer stub
│   │           ├── tier1/              # 🆕 v3.8 · 5개 Tier-1 메서드 (ai_readiness 등)
│   │           ├── versus_runner.py    # 🆕 v3.6 · --versus 다종목 비교
│   │           ├── portfolio_runner.py # 🆕 v3.6 · --portfolio 포트폴리오 분석
│   │           ├── fund_holdings_runner.py # v3.4 · ETF/LOF 보유 루프
│   │           ├── report/             # 🆕 v3.2 · assemble_report 분할
│   │           │   ├── svg_primitives.py     # 19 svg_* + COLOR_*
│   │           │   ├── dim_viz.py            # 19 _viz_xxx + DIM_VIZ_RENDERERS
│   │           │   ├── institutional.py      # DCF/LBO/IC/catalyst/competitive
│   │           │   ├── panel_cards.py        # 66 심사위원 panel
│   │           │   └── special_cards.py      # fund/insights/school_scores
│   │           ├── investor_criteria.py      # 66인 × 242 규칙
│   │           ├── investor_evaluator.py     # 규칙 엔진
│   │           ├── stock_features.py         # 108 표준화 특성
│   │           ├── playwright_fallback.py    # v2.13 폴백
│   │           ├── self_review.py            # 기계 자체 점검 13 check
│   │           └── ...                       # 기타 lib 모듈
│   ├── investor-panel/                 # 심사단 skill
│   ├── lhb-analyzer/                   # 용호방 skill
│   └── trap-detector/                  # 살돈판 skill
├── requirements.txt
└── LICENSE
```

**v3.2 리팩터링 계층화 하이라이트**:

| 계층 | 파일 | 책임 |
|---|---|---|
| 진입점 | `run.py` | CLI 메인 진입점 · `UZI_LEGACY=1` 구경로 폴백 |
| 파이프라인 | `lib/pipeline/*` | v3.0 메인 · collect / score / synthesize |
| 순수 함수 | `lib/pipeline/score_fns.py` | v3.1 · score_dimensions / generate_panel / generate_synthesis |
| 렌더링 | `lib/report/*` | v3.2 · 5개 서브모듈 · svg / viz / inst / panel / special |
| 레거시 | `run_real_test.py` + `assemble_report.py` | v2.x 하위 호환 레이어 · 모든 이전 함수 re-export |

---

## 🧠 설계 이념

**Agent 주도 분석, 스크립트는 단지 도구.**

전체 프로세스는 두 단계로 나뉨——중간에 agent가 반드시 개입해야 하며, **최종적으로 반드시 자체 점검** (v2.9부터 기계 강제):

```
Stage 1 (스크립트)          → 데이터 수집 + 모델 계산 + 규칙 엔진 스켈레톤 점수
         ⏸️ Agent 개입     → 데이터 읽기 → 65 심사위원 role-play → 판단 작성 → 가정 심사
Stage 2 (스크립트)          → 종합 판단 + 자동 13개 자체 점검 실행 → 리포트 생성
                          ↑ v2.9 핵심: critical 통과 못 하면 → HTML 출력 거부
```

**51명의 심사위원은 공식 돌려서 점수 내는 게 아님**——agent가 진정으로 각 인물의 관점에서 생각해야 함:

- 버핏이 애플 분석 → agent는 이것이 버크셔 해서웨이 1위 보유 종목임을 앎 → override 매수
- 자오라오거가 미주 분석 → agent는 유자가 미주 안 함을 앎 → skip
- 우드가 백주 분석 → agent는 그녀가 파괴적 혁신만 봄을 앎 → "플랫폼에 없음"
- 그레이엄이 PE 33 봄 → 복잡한 추론 불필요 → 매도

각 판단은 규칙 엔진의 기계적 점수를 덮어쓸 수 있지만, 반드시 이유를 제시해야 함.

**3층 평가**: 실제 보유 → 업종 친화도 → 정량 규칙. 진짜 돈이 어떤 공식보다 설득력 있음.

### 🛡 기계 자체 점검 gate (v2.9부터)

과거 `HARD-GATE-FINAL-CHECK`는 "소프트 요구사항"이었음——agent가 건너뛸 수 있고, 잊을 수 있고, 반쯤 할 수 있었음. BUG#R10 (윈알루미늄이 "농부식품가공"으로 분류됨)은 전체 프로세스 다 돌고 리포트 발송 후, 사용자가 업종 분류가 틀렸다는 것을 발견한 사례. **소프트 gate로는 부족, v2.9부터 기계 강제.**

**`lib/self_review.py`** 13개 자동 검사가 모든 역사적 BUG 경험을 커버:

| 심각도 | 잡아내는 것 | 배후 BUG |
|---|---|---|
| 🔴 critical | 업종 충돌 (공업금속→농부식품가공) | BUG#R10 |
| 🔴 critical | 차원 누락 / 빈 data / 플레이스홀더 | wave2 timeout, fetcher 크래시 |
| 🔴 critical | HK kline 0개 / HK 재무제표 빔 | BUG#R7 / R8 |
| 🔴 critical | panel 전부 skip / coverage < 60% | 데이터 재난 |
| 🔴 critical | agent_analysis 누락 / 미review | agent 게으름 |
| 🟡 warning | DCF 전부 0 / 금속주 materials 빔 | v2.8.x coverage gap |
| 🟡 warning | "애플 산업 체인" 조작 근거 raw_data 증거 없음 | 연상 조작 |

**`assemble_report::assemble()` 진입점에서 자동으로 review 실행**, critical > 0 → `raise RuntimeError("⛔ BLOCKED by self-review")`, **물리적으로 리포트 출력 불가**, agent가 수정 완료할 때까지.

```bash
# agent 반복 프로세스
loop:
  python review_stage_output.py <ticker>
  .cache/<ticker>/_review_issues.json 읽기
  각 critical에 대해 suggested_fix 실행
  critical == 0 될 때까지 HTML 출력 안 함
```

매번 새로운 BUG 수정 완료 시, 대응하는 `check_*` 규칙이 self_review에 추가됨, **다음에 동일 유형 문제 발생 시 실행만으로 자동 포착, 더 이상 사용자 피드백에 의존하지 않음**.

---

## ❓ FAQ

**Q: 한 번 실행에 얼마나 걸리나요?**
A: 5-8분, 주로 데이터 수집이 느림 (22개 차원에十几个 API 호출). 순수 계산의 기관 모델링 부분은 < 1초.

**Q: 유료 데이터 소스가 필요한가요?**
A: 필요 없음. 전부 무료 소스 (akshare / yfinance / DuckDuckGo / 쥐차오 / 동방재부 / 설구), API key 제로.

**Q: 홍콩주, 미주 사용 가능한가요?**
A: 가능. `/stock-deep-analyzer:analyze-stock 00700.HK` 또는 `/stock-deep-analyzer:analyze-stock AAPL`.

**Q: 데이터 정확한가요?**
A: 실시간 데이터는 동방재부 / 설구 경유, 재무제표는 쥐차오 / akshare 경유, 동방재부 App에서 보는 것과 동일. 단, web search 품질은 불안정 (DuckDuckGo 중문 검색이 때때로 무관한 결과 반환), 그래서 Claude가 2차 심사 수행.

**Q: 투자 조언으로 사용할 수 있나요?**
A: 불가. 이것은 도구이지 신이 아님, 66명 거장의 의견은 모두 규칙 엔진 시뮬레이션이며, 실제 인물의 관점을 대표하지 않음. 사고 말고는 스스로 결정.

**Q: 이번 리포트 데이터가 신뢰할 수 있는지 어떻게 아나요?**
A: v2.9부터 **강제** 기계 자체 점검. 리포트 생성 전 13개 검사 실행, critical 통과 못 하면 물리적으로 리포트 발송 불가. `.cache/<ticker>/_review_issues.json`에서 이번 실행에 warning이 있는지 볼 수 있으며, 각 항목에 `suggested_fix` 포함. 매번 새로운 BUG 수정 시 대응 검사 추가 → 다음에 동일 유형 문제 자동 포착, 사용자 피드백 불필요.

**Q: 새 버전으로 업그레이드 어떻게 하나요? 자동 알림 오나요?**
A: 옵니다. v2.14.0부터 매번 CLI 또는 agent 세션 시작 시 백그라운드에서 GitHub 최신 release 감지:
- 새 버전 있음 → 3지선다 프롬프트 (예 / 이 버전 건너뛰기 / 아니오) + 변경 요약
- "예" 선택 → 설치 방식에 따라 대응 명령 실행:
  - Claude Code: `/plugin update stock-deep-analyzer`
  - git clone: `cd UZI-Skill && git pull`
  - Hermes: `hermes skills update wbh604/UZI-Skill/skills/deep-analysis`
- "이 버전 건너뛰기" 선택 → 해당 버전 다시 프롬프트 안 함, 다음 새 버전 나올 때만 다시 팝업
- "아니오" 선택 → 다음 시작 시 다시 물음
- 네트워크 느림 / 검사 끄기: `export UZI_NO_UPDATE_CHECK=1` (CI / Codex 환경 권장)
- 캐시 6시간 · 매번 GitHub API 치지 않음

**Q: 이전 리포트에 BUG 있으면 어떻게 하나요?**
A: 2026-04-17 이전에 "공업금속 / 공업모기 / 공업기계" 관련 주식을 실행한 사용자는, cache의 `7_industry` 차원이 틀림 (윈알루미늄이 농부식품가공으로 분류된 그 버그). cache 삭제 후 재실행:
```bash
rm -rf skills/deep-analysis/scripts/.cache/<ticker>/raw_data.json
python run.py <ticker> --no-resume
```

---

## 📋 업데이트 로그

| 버전 | 날짜 | 주요 변경 |
|---|---|---|
| **v3.9.0** | 2026-06-11 | **신규 심사위원 「구하이쩌왕」· 최초로 실제 교차 확인에서 증류된 심사위원 (65→66)** · 데이터 소스: 타오구바 10년 실전 게시글 (2016-02 개설) · 3898장 보유 스크린샷 OCR → **8951건 역추적 교차 확인** + **5069건 발언**. 정량 프로필: 33만→3131만 (~95배/10년) · 보유 중위값 1일/P75 3일 · 동시 3-5종목 · 1위 보유 중위값 51% · 10년 2010종목 테마 로테이션 (훙보/촨넝/런민왕/다중교통). 방법론 증류 (스타일提炼·원문 그대로 전재 아님): 복기 3문(왜 상한가/섹터 지위/대판 지위) · 약세→강세 빠른 판이어야 예상 초과 · 로직 단단한 저위 종목 폭발력 충분 ·格局주=시대의 감정 캐리어(3-5배格局론) · 반복 강조 따라하기 금지. 구현: F그룹 flagship · 6개 데이터 주도 규칙 (임계값은 실제 행동 통계에서 도출) · 대사는 스타일에 맞게 독창 작성 · `docs/ghzw-dossier.md` 증류 아카이브. **원본 교차 확인/스크린샷/발언은 모두 로컬 데이터 ·入库 안 됨.** 실측: 훙보식 요괴주 bullish 100 (그가 실제로 22번 함) · 마오타이 bearish 9.5 · 미주 skip. 10개 신규 회귀 · 총 642 passed |
| **v3.8.1** | 2026-06-09 | **skills 전면 건강검진 · H/I 두 그룹配套层 6곳 보완** · 건강검진 결과 v3.6.3/v3.7.0에서 14인 심사위원 추가 시配套层 업데이트 누락 발견 (전부 자동 강등되어 드러나지 않음): ① 14 심사위원 아바타 SVG 누락 → 리포트 이미지 깨짐 (gen_pixel_avatars 보완 · 총 65) ② `render_school_scores` order=[A..G] → H/I 두 파 점수 영원히 렌더링 안 됨 ③ GROUP_LABELS ×3곳 H/I 누락 → bare 문자 표시 ④ `GROUP_DEFAULT` H/I 누락 → profile 전부 "—" ⑤ `STYLE_GROUP_WEIGHTS` H/I 누락 → v2.7 스타일 가중치 두 그룹에失效 (현재 I는 배당주 0.2/테크성장 1.5) ⑥ 13 신규 심사위원 명시적 MARKET_SCOPE + PERSONAS voice 대사 보완 (이전 그룹챗 전부 generic套话). 문서 동기화 ~35곳 (52→65 심사위원 / 7→9 유파 / 180→236 규칙 / --school A-G→A-I). 10개 신규 건강검진 회귀 · 총 632 passed |
| **v3.8.0** | 2026-06-08 | **Tier-1 5대 메서드 + Serenity 엄밀화 + 기술지표/듀퐁 확장** (참조 `anthropics/financial-services` + `lolifamily/ashare-mcp` + `muxuuu/serenity-skill`). **① Tier-1 5대 메서드** (신규 패키지 `lib/tier1/`): `/ai-readiness` (AI 준비도/포지션 · `ai_chokepoint_score` 재사용) · `/earnings-preview` (실적 전 프리뷰 · Bull/Base/Bear + 내재 변동성) · `/model-update` (증분 업데이트 모델 · 가정 delta + DCF/Comps/thesis에 대한 영향) · `/returns` (포트폴리오 수익 귀속) · `/rebalance` (보유종목별 리밸런싱 + 로컬화 회전 비용, A주 자본이득세 없으므로 TLH 미실시). **② Serenity 엄밀화** (더 이상 매수만 보지 않음): 8개 페널티 팩터 (과대광고 무주문/마이크로캡 유동성/살돈판/거버넌스/사이클/대체 설계/지정학/희석 · 최대 60% 할인) + 3단계 증거 계층 (강 공시 재무제표×1.0 > 중 미디어 매도측×0.85 > 약 내러티브×0.70 · 동일 포지션 "정점 양산 있음"≈90 vs "테마만"≈60) + 공급망 8계층 분류 (소재→...→하류 · 상류일수록 병목 점수 높음). **③ 지표 확장**: DuPont 듀퐁 분해 (ROE 품질 출처 margin_driven/leverage_driven · 가치파용) + KDJ/OBV/Williams%R (K선 카드 신규 보조 지표 배지 · 기술파용). 61개 신규 회귀 테스트 · 총 622 passed |
| **v3.7.1** | 2026-06-04 | **홈페이지 Serenity 소개 보완 + `--school H/I` 개방** · 사용자 피드백 "README가 Serenity를 명확히 쓰지 않음". 수정: (1) 심사단 섹션 재작성 52→65인 · 7→9그룹 완전 테이블 (A–I)· 규칙 180→236; (2) 신규 전용 `## 🧠 I그룹 · Serenity · AI 포지션/병목 헌터` 소개 블록 (그녀는 누구 + 미감사 면책 + Chokepoint Theory 역할 + "포지션이 태도 결정" 점수표 + `--school I/H` 사용법); (3) **버그 수정** · v3.7.0부터 evaluator `SCHOOL_LABELS`에 H/I 포함되었지만 `run.py` argparse `choices`는 여전히 A-G · 문서는 사용 가능하다고 하나 실제 실행 시 오류 · 현재 choices A-I로 확장 + `_SCHOOL_NAMES` 중문명 보완; (4) README/CLAUDE/AGENTS/GEMINI 현재 상태 카운트 52→65 심사위원 동기화 (과거 changelog는 변경 안 함). 533 passed |
| **v3.7.0** | 2026-06-03 | **13인 신진 테크 거물 집단 입단 · 52→65 심사위원** · 사용자 피드백 "심사위원 라이브러리 신진 테크 / AI / VC 시각 커버 부족". 신규 분포: **B 성장파 +5** (Marc Andreessen a16z / Bill Gurley Benchmark / Naval Ravikant AngelList / Brad Gerstner Altimeter / Chamath Palihapitiya Social Capital) · **C 매크로파 +2** 숏 헌터 (Michael Burry Big Short / Jim Chanos Kynikos) · **E 중국 가치투자 +1** (장레이 고릉 · "시간의 친구") · **G 퀀트파 +1** (Cliff Asness AQR 가치×품질×모멘텀 3팩터) · **H AI 포지션/병목 헌터 +4** (젠슨 황 NVIDIA / Musk TSLA / Sam Altman OpenAI / Saylor MSTR). 각 심사위원 ≥4 규칙 (테스트 수호) · `_render_school_lock_banner` THEMES 전파 대표 심사위원 실제 재적 멤버로 업데이트 · H파 배색 보라색 🔗. NVDA 실행 실측 Andreessen/Gerstner/Huang/Altman 전원 100 · 마오타이 실행 실측 Andreessen 38 (industry filter ✓ 백주는 software/AI에 없음) · 장레이 80 (✓ 긴 활주로 리더). 18개 신규 회귀 테스트 · 총 532 passed |
| **v3.6.3** | 2026-06-03 | **중량급 캐릭터 Serenity · AI 포지션/병목 헌터 (신규 52번째 심사위원 · 독립 I그룹)** · X에서 폭발적 인기의 AI 공급망 「목조르기/병목점」 투자자 Serenity ([@aleabitoreddit](https://x.com/aleabitoreddit)) 심사단接入 · 참조 [serenity-alpha skill](https://github.com/haskaomni/serenity-skill/tree/main/serenity-alpha) 방법론 + X 실제 발언 크롤링 어조 라이브러리 구축. **핵심 점수 로직 「포지션이 태도 결정」**: 신규 파생 특성 `ai_chokepoint_score` (AI 체인 적중 × 대체 불가성 × 중소형주 탄력성 × 수요 변곡점) · `SERENITY_RULES` 전부 weight 5 · 제품이 AI 병목에 걸림 (광모듈/CPO/HBM/CoWoS/InP 기판…)+ 상류 대체 불가 + 소형주 → **bullish 집중 매수**; 포지션 못 잡음/AI 체인에 없음 → **bearish 손대지 않음** (백주/은행 해자 만점도 score=0); 체인 위지만 포지션 단단하지 않음 → neutral 검증 대기. 변경 `investor_db`(독립 I그룹)/`investor_criteria`/`investor_evaluator`(`--school I`)/`investor_personas`/`investor_profile`/`stock_features`/`agents/investor-panel.md`/`investor-cards.json`(상단 고정 하이라이트). 신규 `group-i-serenity.md` + `fin-methods/serenity-bottleneck.md` (6단계법 + alpha 5차원 + $AXTI 사례) + `serenity-voice.md` 어조 라이브러리 + `docs/serenity-research-dossier.md` (전체 20개 평가 아카이브). 8개 신규 회귀 + 실측 수정광전(neutral 59) · 총 533 passed |
| **v3.6.2** | 2026-06-03 | **cninfo 페이지 넘김 롱테일 수정 + Hermes 스크립트 pip 탐지** · 두 커뮤니티 이슈 동시 발생. **#68** ([@xy2yp](https://github.com/wbh604/UZI-Skill/issues/68)): `--versus 000958 600406 --depth lite`가 15_events cninfo 공시에서 멈춤 · `0/854 [01:53<6:11:58]` · 근본 원인 `akshare.stock_zh_a_disclosure_report_cninfo` 내부에서 전체 854페이지 다 넘긴 후 반환 · 우리의 `.head(30)`은 사후 절단으로 무용. 수정법: 신규 `_cninfo_direct_api` cninfo `/new/hisAnnouncement/query` HTTP 직통 · `pageSize=30 + pageNum=1 + 15s 하드 타임아웃` · akshare 느린 경로 기본 비활성화 (`UZI_AK_CNINFO_FALLBACK=1` opt-in) · 몇 시간 → ≤15s. **#69** ([@FrankHuy](https://github.com/wbh604/UZI-Skill/issues/69)): Linux + Py3.11에서 설치 스크립트 실행 `pip: command not found` · akshare 설치 불가. 수정법: 스크립트 시작 시 Python 버전 사전 검사 추가 (≥3.10) · pip 5계층 연쇄 탐지 (venv/.venv/pip/pip3/python -m pip) · 완전 실패 시 apt/yum/ensurepip 3세트 명령어 제공 · install 실패 시 미러 소스 + pip 업그레이드 제안. 12개 신규 회귀 · 총 507 passed |
| **v3.6.1** | 2026-05-29 | **Hermes Skills Guard 가양성 우회** · [issue #66](https://github.com/wbh604/UZI-Skill/issues/66) (@zodiacg) 피드백: `hermes skills install`이 `Verdict: DANGEROUS · 168 findings` 보고 · `--force`도 덮어쓰기 불가. 진단: Hermes Skills Guard 패턴 매칭 가양성 · 우리의 `os.environ.get("UZI_DEPTH")` 읽기를 "exfiltration"으로 간주 · `subprocess.run(["brew", "install", "cloudflared"])`를 "privilege_escalation"으로 간주 · HTML 주석을 "injection"으로 간주. Hermes 팀 기지 문제 ([#1006](https://github.com/NousResearch/hermes-agent/issues/1006)/[#7072](https://github.com/NousResearch/hermes-agent/issues/7072))· 공식 builtin skills도 자체 스캐너에 차단됨. 수정법: 신규 `install-hermes.sh` (96줄 · `set -euo pipefail`) · `curl ... \| bash` 원클릭 clone + symlink + venv pip · Hub 설치와 완전 동등하지만 스캔 우회. `INSTALL-HERMES.md` 헤더 재작성 가양성 원인 설명. 11개 신규 회귀 테스트 수호 (script 존재/bash 문법/엄격 모드/4 skill 커버/venv fallback/문서 링크) · 총 495 passed |
| **v3.6.0** | 2026-05-29 | **비주얼/인터랙션 대규모 업그레이드 + 다종목 횡적 비교 + 포트폴리오 분석** · 3 Phase 합본 발표. **Phase A 비주얼**: (1) 다크 모드 토글 (우측 상단 🌙 · `localStorage` 영속화 + `prefers-color-scheme` 자동 초기화) · (2) 좌측 sticky TOC + IntersectionObserver scroll-spy · (3) 대형 점수 count-up 애니메이션 · (4) PE/PB/ROE/DCF/IRR/WACC/EV-EBITDA/LBO/YTD/TTM/PEG/LHB 자동 `.jargon` 래핑 + 플로팅 tooltip · (5) 리포트 하단 QR 코드 (스캔 시 전체 리포트 직통) · 🔒 전부 `createElement + textContent` 안전 DOM · innerHTML 미사용 (XSS 방어). **Phase B `--versus`**: 2-4종목 횡적 비교 · `lib/versus_runner.py` (380줄)· ★ WIN 하이라이트 12개 핵심 지표 · 단일 HTML 자체 포함 · cache 재사용. **Phase C `--portfolio`**: 사용자 CSV 업로드 (ticker/weight/note) · 내결함성 파싱 (header/무header/중영문 열명/0-1 vs 0-100 가중치) · 가중치 자동 정규화 · 출력 순위 + KPI (가중 점수 + 집중도 + 업종 분산) + metadata.json · `lib/portfolio_runner.py` (370줄). Phase D (`--sector` / `--as-of`)는 fetcher date-aware 필요 · v3.7로 유보. 39개 신규 회귀 테스트 · 총 484 passed |
| **v3.5.0** | 2026-05-29 | **단일 유파 시각 고정 (`--school A-G`) + SaaS 통합 (`--output-dir`)** · 커뮤니티 피드백 "F파 유자 시각만 보고 싶음 · 51 심사위원 함께 vote不想". (1) `run.py`에 `--school A/B/C/D/E/F/G` 추가 · 가치/성장/매크로/기술/중국가치투자/유자/퀀트 7选1 · `investor_evaluator.evaluate` 진입점에서 `UZI_SCHOOL` env 검사 · 해당 파 아닌 심사위원은 바로 `_skip_result(reason="사용자가 X파 시각 고정")` 규칙 엔진 미진입. (2) `synthesis.school_lock={group,label}` syn에 인코딩 · `_render_school_lock_banner` 7파 각자 배색 (A=진녹/F=진적/G=청) 리포트 상단에 렌더링 · 공유자가 한눈에 이번에 해당 파만 봤음을 알 수 있게 · 51 심사위원 결론으로 오독 방지. (3) `SKILL.md`에 HARD-GATE 추가 · agent role-play 시 엄격히 해당 파만 role-play · `panel_insights`에 교차 파 비교 작성 금지. (4) 동시에 미리 준비된 `--output-dir DIR` SaaS 통합 파라미터 합병 · `reports/{ticker}_{date}/`를 외부 경로로 복사 + `index.html` / `report.meta.json` 작성하여 Celery worker入库 용. 11개 신규 회귀 테스트 · 총 445 passed |
| **v3.4.5** | 2026-05-12 | **F파 유자 LHB 역조회 + low-confidence 배너** · 커뮤니티 codex agent가 징동팡 (000725) 실행 실측 발견 두 가지: ① F파 23인 전원 skip (시총 2000억 초과 사정거리) · 그러나 LHB 실제로 3-5개 유자 좌석이 상한가 게임 참여 · 심사위원 로직과 데이터 괴리. ② 규칙 엔진 fund_score 37.6이지만 agent 재평가 65/100 · 리포트에 어떤 "score 신뢰 불가" 경고도 없음 · 사용자 오판. 수정법: (1) `_is_youzi_out_of_range`에 LHB 역조회 추가 · features.matched_youzi에 해당 유자 닉네임 포함 시 강제 skip 안 함. (2) `_render_data_gap_banner`에 신규 syn 파라미터 · stock + fund_score<50 + cov<60% → low-confidence 적색 배너 렌더링 · 문안 명확히 agent 재평가 보도록 유도. 10개 신규 회귀 테스트 · 총 407 passed |
| **v3.4.4** | 2026-05-12 | **data quality banner UX 최적화** · 커뮤니티 피드백 두 가지: ① ETF 리포트 "커버리지 17%"가 사용자에게 신뢰도 오판 유발 (실제 ETF는 본래 ROE/PE 개별주 필드 없음) · ② 주황색 배너 위 주황색 글자 (`#f59e0b/#fbbf24`) 가독성 불량. 수정법: (1) 배너가 ETF/LOF/mutual_fund 감지 · `fund-type` 청색조 배너로 전환 · 문안 명확히 "펀드 유형 예상 결손 필드·신뢰도에 영향 없음"+ 보유주 리포트 보도록 유도. (2) CSS 대비 대폭 변경 · title→#92400e 진갈색 · subtitle strong→#7c2d12 + 굵게 800 · chip 문자→#7c2d12 · subtitle 본문→#1f2937 진회색. 11개 신규 CSS + 행동 회귀 테스트 · 총 397 passed |
| **v3.4.3** | 2026-05-12 | **개방형 펀드 분류 수정 + 필드 레벨 fallback gate** · (1) [#60 재심](https://github.com/wbh604/UZI-Skill/issues/60) (@SchrodingerBarbatos) · 사용자 110011 이팡다优输入 → 전환사채로 오판 early-exit. 수정법: `classify_security_type`이 cb 판정 전 `akshare.fund_name_em` 2차 검증 사용 · `mutual_fund` 유형 추가 · run.py + preflight가 fund_holdings_runner로 라우팅 · 005xxx 등 주식 접두사 외 펀드도 식별. (2) [PR #63](https://github.com/wbh604/UZI-Skill/pull/63) (@Wood Letitia · 313+137줄) · 필드 레벨 fallback gate · 소스 레벨 통째 전환으로 name 영원히 결손되는 문제 수정 · 주 소스가 price/PE/PB는 가져왔지만 name이 빔 · 자동으로 tencent_qt → baostock → ak_code_name 호출 보완 · 빈 것만 채우고 덮어쓰지 않음. 386 tests passed |

(출력이 50KB에서 제한되었습니다. 1-797행 표시. offset=798으로 계속 읽으세요.)

---

전체 업데이트 로그는 [RELEASE-NOTES.md](RELEASE-NOTES.md) 참조

---

## 🤝 감사 인사

- [anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) — 기관급 분석 방법론
- [obra/superpowers](https://github.com/obra/superpowers) — 다중 플랫폼 아키텍처 / HARD-GATE / hooks / sub-agent 설계
- [akshare](https://github.com/akfamily/akshare) — A주 데이터 엔진
- [titanwings/colleague-skill](https://github.com/titanwings/colleague-skill) — Skill 아키텍처 참조
- [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) — Pydantic Signal 패턴
- [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) — 다공 토론 루프

---

## ⚠️ 면책 성명

본 도구는 AI 모델이 공개 데이터를 기반으로 분석 리포트를 생성합니다. 모든 점수, 제안, 시뮬레이션 평어는 알고리즘 출력이며, 실제 투자자의 실제 관점을 대표하지 않습니다. **투자 조언을 구성하지 않으며**, 투자에는 리스크가 있으니, 시장 진입 시 신중하시기 바랍니다.

---

## ⭐ Star 이력

실시간 stars: ![GitHub Repo stars](https://img.shields.io/github/stars/wbh604/UZI-Skill?style=social)

<a href="https://star-history.com/#wbh604/uzi-skill&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=wbh604/uzi-skill&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=wbh604/uzi-skill&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=wbh604/uzi-skill&type=Date" />
 </picture>
</a>

> 주: star-history.com 서버 측에 24h 캐시 있음, 급성장 중인 초기 며칠은 차트가滞后될 수 있음 (현재 실제 숫자를 보려면 위의 shields.io 배지 참조, 또는 차트 클릭하여 star-history 공식 사이트 진입 시 새로고침 트리거).

---

<div align="center">

MIT License · Made by FloatFu-true · O.o

</div>
