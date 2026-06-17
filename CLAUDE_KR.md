# UZI-Skill · Claude Code 컨텍스트

> 본 파일은 Claude Code가 자동으로 읽어 프로젝트 컨텍스트를 제공합니다.
> (원문: [CLAUDE.md](CLAUDE.md) — 본 파일은 한글 번역본이며, 정본은 CLAUDE.md입니다.)

## 이게 뭔가요

주식 심층 분석 plugin입니다. 사용자가 "XXX 분석해줘"라고 말하면, 자동으로 `deep-analysis` skill을 트리거해야 합니다.

## 핵심 스킬

| Skill | 트리거 조건 | 설명 |
|---|---|---|
| `deep-analysis` | 사용자가 "분석/리서치/밸류에이션/DCF/살 만한가" 등을 언급 | 22차원 데이터 + 66명 심사위원 + Bloomberg식 리포트 |
| `investor-panel` | 사용자가 "심사위원만/대가들은 어떻게 보나"를 요청 | 투자자 패널만 단독 실행 |
| `lhb-analyzer` | 사용자가 "용호방/유자/증권사 지점"을 언급 | 용호방(龙虎榜) 전문 분석 |
| `trap-detector` | 사용자가 "작전주/문제 없나/안전한가"를 언급 | 살돈판(작전주) 탐지 |

## 워크플로 · 깊이 2단계 (v2.10.6)

**빠른 경로(기본값)**: 사용자가 "분석/봐줘"라고 하면 우선 CLI 직접 실행을 사용합니다.
```
python3 run.py <ticker> --depth lite --no-browser   # 30-60초
# 또는
python3 run.py <ticker> --depth medium --no-browser # 2-4분, 기본 완성도
```
v2.10.4부터 CLI 직접 실행 시 `agent_analysis.json`이 없으면 자동으로 warning으로 강등되고, 그래도 HTML 리포트는 출력됩니다. **66명 심사위원 role-play는 필요 없습니다.**

**심층 경로**: 사용자가 명시적으로 DCF / IC memo(투자위원회 메모) / 신규 커버리지 / 투자위원회 비망록 등 심층 산출물을 요구할 때만 2단계 방식을 사용합니다.
1. `stage1()` — 스크립트가 데이터 수집 + 규칙 엔진 골격 점수 산출
2. **당신(Claude)이 개입** — `panel.json`을 읽고, 66명 심사위원을 role-play하여 `agent_analysis.json` 작성
3. `stage2()` — 당신의 분석을 자동 병합하여 리포트 생성

상세 플로는 `AGENTS.md` / `skills/deep-analysis/SKILL.md` 참고.

## 중요 파일

- `AGENTS.md` — 전체 agent 지침 (한글판: `AGENTS_KR.md`)
- `skills/deep-analysis/SKILL.md` — 심층 분석 워크플로
- `skills/deep-analysis/scripts/run_real_test.py` — 메인 엔진
- `commands/analyze-stock.md` — `/analyze-stock` 명령어

---

## 📎 한국 주식(K) 시장 지원 작업 컨텍스트

본 저장소는 현재 **한국(KOSPI/KOSDAQ) 시장 지원 추가** 작업이 진행 중입니다.

- 필요 데이터 명세: `need_info_type.md` (22차원별 한국 데이터 소스 매핑 + 네이버 신 API 분석)
- 세부 개발 계획서: `new_dev_plan.md` (Phase별 구현 로드맵)
- 데이터 소스 핵심: 네이버 증권 신페이지 비공식 JSON API (`m.stock.naver.com/api`, `api.stock.naver.com`, `ac.stock.naver.com`) + DART OpenAPI + KRX

한국 종목 작업 시에는 위 두 문서를 먼저 읽으세요.

### 한국 종목 사용법

```bash
python run.py 005930 --depth lite --no-browser     # 순수 6자리 = K 우선 (삼성전자)
python run.py 삼성전자 --depth medium --no-browser  # 한글명 → 네이버 ac 자동완성 resolve
python run.py 247540.KQ --no-browser               # 코스닥 명시
python run.py 600519.A --no-browser                # A주(중국)는 .A 접미사 명시
```

- **시장 라우팅**: 접미사 없는 6자리 → **K(한국) 우선**. A주는 `.A`, 코스피 `.KS`, 코스닥 `.KQ`. (`run.py --market {A,H,U,K}` 강제 가능)
- **출력 언어**: K 종목은 `UZI_LANG=ko` 자동. 평가위원 코멘트·라벨·통화(₩) 한국어. (D8: 중국어 출력부는 별도 ko 출력부로만 보존)
- **DART**: `.env` 에 `DART_APIKEY`(opendart.fss.or.kr 40자리) 필요 — 지배구조/공시/정밀재무.
- **K 미적용 차원**: `16_lhb`(용호방)·`19_contests`(설구) skip, F조(游资) 평가위원 자동 skip.
- **테스트**: RTK 가 pytest 출력을 한글 mojibake로 오보하므로, K 테스트는 hermes venv pytest(`AppData/Local/hermes/hermes-agent/venv/Scripts/pytest.exe`) 직접 호출로 확인.

> 진행 현황·발견·회고는 `new_dev_plan.md` 참조 (Phase 1~7 + medium/deep E2E 점검 + 한글화 회고).
