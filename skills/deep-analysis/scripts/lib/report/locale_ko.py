"""한국어 리포트 후처리 (K 전용) · Phase 6.

D8 원칙: 기존 중국어 렌더러는 건드리지 않는다. K 종목 리포트일 때만, 생성된
standalone HTML 문자열에 통화/단위/주요 UI 라벨을 한국어로 치환한다.
- 통화: ¥ → ₩ (가격은 천단위 콤마 + 불필요한 .0 제거)
- 단위: 万亿 → 조, 亿 → 억
- 차원 제목 / 판정어 등 핵심 UI 라벨: 중→한 사전 치환 (긴 키 우선)

평가위원 개별 코멘트 등 자연어 문장은 후처리 대상이 아니다(오치환 위험).
그쪽 한국어화는 심층 경로의 language_instruction("ko") + 규칙 라벨 한글화(후속)에서.
"""
from __future__ import annotations

import re

# 중→한 라벨 사전. **긴 키가 먼저 치환되도록** 적용 시 길이 내림차순 정렬한다.
# (예: '估值分位' 가 '估值'+'分位' 로 쪼개져 오치환되는 것 방지)
_ZH_TO_KO: dict[str, str] = {
    # ─ 차원 제목 (22 dims) ─
    "估值分位": "밸류에이션 분위",
    "估值": "밸류에이션",
    "财报": "재무",
    "资金面": "수급",
    "治理": "지배구조",
    "事件": "이벤트",
    "龙虎榜": "용호방(한국 미적용)",
    "护城河": "해자",
    "同行对比": "동종 비교",
    "同行": "동종",
    "宏观": "거시",
    "行业": "업종",
    "产业链": "공급망",
    "原材料": "원자재",
    "期货关联": "선물 연계",
    "政策": "정책",
    "舆情": "투자심리",
    "实盘大赛": "실전대회",
    "研报": "증권사 리포트",
    "公募持仓": "펀드 보유",
    # ─ 판정어 / 점수 라벨 ─
    "综合评分": "종합점수",
    "谨慎": "신중",
    "看多": "매수 우위",
    "看空": "매도 우위",
    "中性": "중립",
    "派": "파",
    # ─ 재무/수급 단어 ─
    "主力": "주력",
    "净流入": "순유입",
    "净流出": "순유출",
    "解禁": "보호예수 해제",
    "总市值": "시가총액",
    "自由现金流": "잉여현금흐름",
    "近 30 天上榜": "최근 30일 거래원 상위",
    "识别游资": "식별 세력",
    "行业均值": "업종 평균",
    # ─ 판정/액션 (평가위원 코멘트에 자주 쓰이는 안전 명사·판정어) ─
    "综合评分": "종합점수",
    "引擎评分": "엔진점수",
    "目标价": "목표가",
    "买入": "매수",
    "卖出": "매도",
    "增持": "비중확대",
    "减持": "비중축소",
    "持有": "보유",
    "强烈": "강력",
    "建议": "권고",
    "风险": "리스크",
    "看好": "긍정적",
    "看淡": "부정적",
    "上涨": "상승",
    "下跌": "하락",
    "评分": "점수",
    # ─ 투자심리 라벨 ─
    "乐观": "낙관",
    "悲观": "비관",
    "中性": "중립",
    "热度": "열기",
    "情绪": "심리",
    "条结果": "건",
    "位大V提及": "명 인플루언서 언급",
    # ─ 빈 데이터 / 상태 ─
    "综合": "종합",
    "暂无数据": "데이터 없음",
    "暂无": "데이터 없음",
    "无数据": "데이터 없음",
    "需定性评估": "정성 평가 필요",
    "数据缺失": "데이터 누락",
    # ─ 중국 플랫폼명 (한국 종목 리포트에 노출 시) ─
    "雪球": "설구(중국)",
    "股吧": "주식게시판",
    "知乎": "지식인",
    "微博": "웨이보",
}


def _localize_currency(html: str) -> str:
    """¥123456.0 → ₩123,456 · ¥1,234 → ₩1,234. 기호만 남는 경우도 ₩."""
    def _repl(m: re.Match) -> str:
        num = m.group(1)
        # 불필요한 .0 제거
        if num.endswith(".0"):
            num = num[:-2]
        # 콤마가 없고 정수면 천단위 콤마 추가
        if "," not in num and num.lstrip("-").isdigit():
            num = f"{int(num):,}"
        return f"₩{num}"

    html = re.sub(r"¥\s*(-?[\d,]+(?:\.\d+)?)", _repl, html)
    return html.replace("¥", "₩")


def _localize_units(html: str) -> str:
    return html.replace("万亿", "조").replace("亿", "억")


def _localize_labels(html: str) -> str:
    for zh in sorted(_ZH_TO_KO, key=len, reverse=True):
        html = html.replace(zh, _ZH_TO_KO[zh])
    return html


# 평가위원 코멘트 템플릿의 미치환 f-string 잔재. 예: {pe_ttm:.0f} {roe:.1f} {ev_to_revenue:.1f}
# (근본 원인은 investor_criteria 템플릿 변수명 ↔ features 키명 불일치 · upstream 전체 이슈)
_RE_UNRENDERED = re.compile(r"\{[a-z_]+:[.,0-9a-z%x]+\}")


def _strip_unrendered(html: str) -> str:
    """미치환 f-string 변수({word:.Nf} 형태)를 — 로 치환. format spec(콜론+포맷)이 있는
    소문자 변수만 대상이라 CSS/JS 중괄호({ return 1; })는 건드리지 않는다."""
    return _RE_UNRENDERED.sub("—", html)


def localize_ko(html: str) -> str:
    """K 리포트 HTML 한국어 후처리 (통화 → 단위 → 라벨 순)."""
    if not html:
        return html
    html = _localize_currency(html)
    html = _localize_units(html)
    html = _localize_labels(html)
    html = _strip_unrendered(html)
    return html
