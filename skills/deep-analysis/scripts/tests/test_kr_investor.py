"""investor_knowledge · 한국(K) 시장 심사위원 필터 (Phase 5).

F조(游资)는 打板/龙虎榜/T+1 방법론이라 A주 전용 → K 자동 skip.
나머지 그룹(가치/성장/기술/퀀트/매크로 등 scope='all')은 K 평가 가능.
코드 변경 없이 기존 market_match 로직으로 동작 — 회귀 방지 특성화 테스트.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def test_market_match_f_group_excludes_korea():
    from lib.investor_knowledge import market_match
    # F조 游资 (scope 'A') → K 제외
    for fid in ("zhang_mz", "zhao_lg", "chengdu", "ghzw"):
        assert market_match(fid, "K") is False, f"{fid} 는 K 에서 skip 되어야"


def test_market_match_global_groups_include_korea():
    from lib.investor_knowledge import market_match
    # 글로벌 프레임워크 (scope 'all') → K 평가
    for gid in ("buffett", "munger", "lynch", "simons", "wood", "duan", "serenity"):
        assert market_match(gid, "K") is True, f"{gid} 는 K 평가 가능해야"


def test_reality_check_skips_f_group_on_korea():
    from lib.investor_knowledge import reality_check
    rc = reality_check("zhang_mz", "K", "005930", "삼성전자", "반도체")
    assert rc["should_evaluate"] is False
    assert rc["skip_reason"]


def test_reality_check_allows_global_on_korea():
    from lib.investor_knowledge import reality_check
    rc = reality_check("buffett", "K", "005930", "삼성전자", "반도체")
    assert rc["should_evaluate"] is True


def test_market_match_a_share_f_group_still_works():
    """회귀: F조는 A주에서는 여전히 평가."""
    from lib.investor_knowledge import market_match
    assert market_match("zhang_mz", "A") is True
