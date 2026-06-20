"""Dimension 18 · 杀猪盘检测 — 真实 web search 扫描 8 信号."""
from __future__ import annotations

import json
import sys

from lib import data_sources as ds
from lib.market_router import parse_ticker
from lib.web_search import search


SIGNALS = [
    {
        "id": 1, "name": "大量低质量账号同时推荐",
        "queries": ["{name} 强烈推荐 必涨", "{name} 内部消息 暴涨"],
        "positive_kws": ["必涨", "强烈推荐", "内部", "稳赚"],
    },
    {
        "id": 2, "name": "推荐话术模板化",
        "queries": ["{name} 主力建仓完毕 即将爆发", "{name} 翻倍 目标价"],
        "positive_kws": ["即将爆发", "主力建仓完毕", "翻倍", "目标翻倍"],
    },
    {
        "id": 3, "name": "付费社群/VIP直播间引流",
        "queries": ["{name} 股票 微信群", "{name} 老师 带单 VIP 直播间"],
        "positive_kws": ["微信群", "VIP 直播", "老师带", "收费群", "加入群聊"],
    },
    {
        "id": 4, "name": "基本面与热度脱节",
        "queries": ["{name} 业绩亏损 推荐 暴涨", "{name} ST 推荐 拉升"],
        "positive_kws": ["亏损但推荐", "ST", "垃圾股 推荐"],
    },
    {
        "id": 5, "name": "K线异常配合",
        "queries": ["{name} 异动 操纵 拉升"],
        "positive_kws": ["异动", "操纵", "快速拉升", "直线拉升"],
    },
    {
        "id": 6, "name": "老师/股神人设推广",
        "queries": ["{name} 老师 股神 跟单", "{name} 实盘 老师"],
        "positive_kws": ["老师", "股神", "跟单", "操盘手"],
    },
    {
        "id": 7, "name": "跨平台联动推广",
        "queries": ["小红书 {name} 股票 推荐", "抖音 {name} 股票"],
        "positive_kws": ["小红书", "抖音", "快手", "B站 推荐"],
    },
    {
        "id": 8, "name": "虚假研报/伪造消息",
        "queries": ["{name} 虚假研报 谣言", "{name} 辟谣 澄清"],
        "positive_kws": ["虚假", "谣言", "澄清", "辟谣", "伪造"],
    },
]

# 한국(K) 작전주 맥락 8신호 — 리딩방/유튜브/텔레그램/관리종목 등
SIGNALS_KO = [
    {"id": 1, "name": "저질 계정 대량 동시 추천",
     "queries": ["{name} 강력추천 급등 확실", "{name} 내부정보 폭등"],
     "positive_kws": ["강력추천", "급등", "내부정보", "확실수익", "대박"]},
    {"id": 2, "name": "추천 멘트 정형화",
     "queries": ["{name} 세력 매집완료 급등임박", "{name} 두배 목표가"],
     "positive_kws": ["급등임박", "매집완료", "두배", "목표 두배"]},
    {"id": 3, "name": "유료 리딩방/VIP 유인",
     "queries": ["{name} 주식 리딩방 단톡방", "{name} 선생님 종목추천 VIP"],
     "positive_kws": ["리딩방", "단톡방", "VIP", "유료방", "선생님"]},
    {"id": 4, "name": "펀더멘털과 인기 괴리",
     "queries": ["{name} 적자 추천 급등", "{name} 관리종목 추천 급등"],
     "positive_kws": ["적자", "관리종목", "상장폐지", "거래정지 추천"]},
    {"id": 5, "name": "비정상 주가 패턴",
     "queries": ["{name} 이상급등 작전 주가조작"],
     "positive_kws": ["이상급등", "작전", "주가조작", "수직상승"]},
    {"id": 6, "name": "주식고수 인설 마케팅",
     "queries": ["{name} 주식고수 따라하기 리딩", "{name} 실전 선생님 수익인증"],
     "positive_kws": ["주식고수", "따라하기", "실전 리딩", "수익인증"]},
    {"id": 7, "name": "크로스플랫폼 홍보",
     "queries": ["유튜브 {name} 주식 추천", "텔레그램 {name} 주식 오픈채팅"],
     "positive_kws": ["유튜브", "텔레그램", "오픈채팅", "카페 추천"]},
    {"id": 8, "name": "허위 리포트/가짜뉴스",
     "queries": ["{name} 허위 정보 루머", "{name} 해명 정정공시"],
     "positive_kws": ["허위", "루머", "정정", "해명", "가짜"]},
]


def main(ticker_or_name: str) -> dict:
    try:
        from lib.i18n import get_language
        ko = (get_language() == "ko")
    except Exception:
        ko = False
    # If ticker, resolve to name
    name = ticker_or_name
    if ticker_or_name.replace(".", "").replace("SZ", "").replace("SH", "").isdigit():
        try:
            ti = parse_ticker(ticker_or_name)
            basic = ds.fetch_basic(ti)
            name = basic.get("name") or ti.code
        except Exception:
            pass

    hit_signals = []
    all_snippets = {}
    for sig in (SIGNALS_KO if ko else SIGNALS):
        combined_bodies = []
        for q_template in sig["queries"][:1]:  # 1 query per signal to save search calls
            q = q_template.format(name=name)
            res = search(q, max_results=3)
            valid = [r for r in res if "error" not in r]
            combined_bodies.extend(r.get("body", "") for r in valid)
            all_snippets.setdefault(f"signal_{sig['id']}", []).extend(
                {"title": r.get("title", "")[:80], "body": r.get("body", "")[:180], "url": r.get("url", "")}
                for r in valid[:2]
            )

        combined_text = " ".join(combined_bodies)
        hits = [kw for kw in sig["positive_kws"] if kw in combined_text]
        if len(hits) >= 2:
            hit_signals.append({
                "id": sig["id"],
                "name": sig["name"],
                "evidence_kws": hits[:3],
                "severity": "high" if len(hits) >= 3 else "medium",
            })

    n_hits = len(hit_signals)
    if n_hits <= 1:
        level = "🟢 안전" if ko else "🟢 安全"
        score = 9
        recommendation = "데이터 정상 · 뚜렷한 작전/홍보 흔적 없음." if ko else "数据正常，未发现明显推广痕迹。"
    elif n_hits <= 3:
        level = "🟡 주의" if ko else "🟡 注意"
        score = 7
        recommendation = (f"홍보/작전 신호 {n_hits}개 발견 · 정보 출처 확인 권고."
                          if ko else f"发现 {n_hits} 个推广信号，建议核实信息源。")
    elif n_hits <= 5:
        level = "🟠 경계" if ko else "🟠 警惕"
        score = 4
        recommendation = (f"홍보/작전 신호 {n_hits}개 발견 · 신중 접근 강력 권고."
                          if ko else f"发现 {n_hits} 个推广信号，强烈建议谨慎。")
    else:
        level = "🔴 매우 의심" if ko else "🔴 高度可疑"
        score = 1
        recommendation = (f"홍보/작전 신호 {n_hits}개 발견 · 회피 강력 권고 · 작전주 의심."
                          if ko else f"发现 {n_hits} 个推广信号，强烈建议回避。疑似杀猪盘特征。")

    return {
        "ticker": ticker_or_name,
        "data": {
            "trap_level": level,
            "trap_score": score,
            "signals_hit": f"{n_hits}/8",
            "signals_hit_count": n_hits,
            "signals_hit_detail": hit_signals,
            "recommendation": recommendation,
            "evidence_count": sum(len(s.get("evidence_kws", [])) for s in hit_signals),
            "high_risk_kw": ", ".join(s["name"] for s in hit_signals[:3]) if hit_signals else ("미발견" if ko else "未发现"),
            "snippets": all_snippets,
        },
        "source": "web_search:ddgs + 8-signal keyword scan",
        "fallback": False,
    }


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1] if len(sys.argv) > 1 else "002273.SZ"), ensure_ascii=False, indent=2, default=str))
