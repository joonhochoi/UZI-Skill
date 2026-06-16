"""report.locale_ko · 한국어 후처리 (Phase 6).

D8 원칙: 기존 중국어 렌더러는 0 수정. K 리포트일 때만 생성된 HTML 에
통화/단위/주요 라벨을 한국어로 치환하는 후처리 모듈.
upstream 병합 시 이 모듈만 유지하면 됨.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def test_localize_currency_yen_to_won():
    from lib.report.locale_ko import localize_ko
    out = localize_ko('<span class="price">¥343000.0</span>')
    assert "₩" in out
    assert "¥" not in out


def test_localize_currency_strips_trailing_dot_zero():
    from lib.report.locale_ko import localize_ko
    assert "₩343,000" in localize_ko("¥343000.0")


def test_localize_units_han_to_korean():
    from lib.report.locale_ko import localize_ko
    out = localize_ko("总市值 300亿 · 自由现金流 5万亿")
    assert "억" in out and "亿" not in out
    assert "조" in out and "万亿" not in out


def test_localize_dimension_titles():
    from lib.report.locale_ko import localize_ko
    assert "밸류에이션" in localize_ko("估值")
    assert "재무" in localize_ko("财报")
    assert "지배구조" in localize_ko("治理")


def test_localize_longer_label_first():
    """估值分位 → 밸류에이션 분위 (부분 치환 충돌 방지: 긴 키 우선)."""
    from lib.report.locale_ko import localize_ko
    out = localize_ko("估值分位")
    assert "估" not in out and "值" not in out


def test_localize_verdict_words():
    from lib.report.locale_ko import localize_ko
    out = localize_ko("综合评分 47.8 · 谨慎 · 看多")
    assert "종합" in out
    assert "综合" not in out


def test_localize_idempotent_safe():
    """두 번 적용해도 깨지지 않음."""
    from lib.report.locale_ko import localize_ko
    once = localize_ko("¥100亿 估值")
    twice = localize_ko(once)
    assert "₩" in twice and "억" in twice


def test_localize_action_words():
    from lib.report.locale_ko import localize_ko
    out = localize_ko("建议买入 · 目标价 ¥500000 · 风险可控")
    assert "매수" in out and "目标价" not in out
    assert "리스크" in out


def test_i18n_ko_supported():
    from lib.i18n import language_instruction, SUPPORTED_LANGS
    assert "ko" in SUPPORTED_LANGS
    assert "한국어" in language_instruction("ko")


def test_strip_unrendered_fstrings():
    """평가위원 코멘트 템플릿의 미치환 f-string({pe_ttm:.0f} 등)을 — 로 정리.

    근본 원인은 investor_criteria 템플릿/features 키명 불일치(전체 시장 영향, upstream)
    지만, K 리포트 가시성을 위해 후처리에서 잔재를 가린다.
    """
    from lib.report.locale_ko import localize_ko
    out = localize_ko("PER {pe_ttm:.0f}배 · ROE {roe:.1f}% · {ev_to_revenue:.1f}x")
    assert "{pe_ttm" not in out
    assert "{roe" not in out
    assert "{ev_to_revenue" not in out


def test_strip_unrendered_keeps_normal_braces():
    """정상 텍스트(CSS/JS 중괄호 등)는 건드리지 않는다 — 변수 패턴만 제거."""
    from lib.report.locale_ko import localize_ko
    out = localize_ko("function(){ return 1; }")
    assert "return 1" in out
