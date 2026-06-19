"""Dimension 11 · 治理 (实控人/质押/管理层增减持/关联交易)."""
import json
import sys

import akshare as ak  # type: ignore
from lib.market_router import parse_ticker


def main(ticker: str) -> dict:
    ti = parse_ticker(ticker)
    if ti.market == "K":
        # K · DART 최대주주 + 임원 → 11_governance
        try:
            from lib.kr_data_sources import (dart_corp_code, dart_major_shareholders,
                                             dart_executives, dart_major_holders,
                                             to_governance_dim)
            cc = dart_corp_code(ti.code)
            sh, ex, mh = [], [], []
            if cc:
                # 직전 사업연도 기준 (2024 사업보고서 11011)
                sh = dart_major_shareholders(cc, 2024)
                ex = dart_executives(cc, 2024)
                mh = dart_major_holders(cc)
            data = to_governance_dim(sh, ex, major_holders=mh)
            return {
                "ticker": ti.full, "data": data,
                "source": "dart:hyslrSttus + exctvSttus",
                "fallback": not bool(sh or ex),
            }
        except Exception as e:
            return {
                "ticker": ti.full,
                "data": {"_err": f"{type(e).__name__}: {str(e)[:120]}", "pledge": [],
                         "insider_trades_1y": [], "qualitative_search": []},
                "source": "dart", "fallback": True,
            }
    pledges: list = []
    insider: list = []
    try:
        if ti.market == "A":
            try:
                df_pledge = ak.stock_gpzy_pledge_ratio_em()
                if df_pledge is not None:
                    row = df_pledge[df_pledge["股票代码"] == ti.code]
                    pledges = row.to_dict("records")
            except Exception:
                pass
            try:
                df_in = ak.stock_ggcg_em(symbol="近一年")
                if df_in is not None:
                    row = df_in[df_in["股票代码"] == ti.code]
                    insider = row.head(20).to_dict("records")
            except Exception:
                pass
    except Exception as e:
        return {"data": {"error": str(e)}, "source": "akshare", "fallback": True}
    return {
        "ticker": ti.full,
        "data": {
            "pledge": pledges,
            "insider_trades_1y": insider,
            "qualitative_search": [f"{ti.full} 关联交易 违规 处罚", f"{ti.full} 股权激励"],
        },
        "source": "akshare:stock_gpzy_pledge_ratio_em + stock_ggcg_em",
        "fallback": False,
    }


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1] if len(sys.argv) > 1 else "002273.SZ"), ensure_ascii=False, indent=2, default=str))
