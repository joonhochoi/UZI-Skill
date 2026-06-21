"""agent_analysis_validator.cjk_audit · K(한국어) deep 산출물 한자 혼용 가드.

deep role-play 산출물에 원문 한자가 섞일 수 있어(new_dev_plan 회고),
렌더 전 한자 개수/위치를 집계해 경고하기 위한 감지 함수. 자동수정은 하지 않음.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def test_cjk_audit_detects_mixed_hanzi():
    from lib.agent_analysis_validator import cjk_audit
    aa = {
        "dim_commentary": {"5_chain": "밸류체인 분석 完成", "1_financials": "재무 양호"},
        "risks": ["리스크 风险 존재"],
    }
    total, hits = cjk_audit(aa)
    assert total == 4   # 完成(2) + 风险(2)
    paths = {h["path"] for h in hits}
    assert "dim_commentary.5_chain" in paths
    assert "risks[0]" in paths


def test_cjk_audit_clean_korean_zero():
    from lib.agent_analysis_validator import cjk_audit
    aa = {"dim_commentary": {"5_chain": "밸류체인 분석 완료"}, "risks": ["리스크 존재"]}
    total, hits = cjk_audit(aa)
    assert total == 0 and hits == []


def test_cjk_audit_empty_safe():
    from lib.agent_analysis_validator import cjk_audit
    assert cjk_audit({}) == (0, [])
    assert cjk_audit(None) == (0, [])
