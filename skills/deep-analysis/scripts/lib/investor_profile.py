"""Per-investor authentic decision profile · v2.8.

Each investor fills THREE fields according to their own methodology — NOT a uniform
template. This is the "因地制宜" layer: Buffett's time horizon is "10+ years",
赵老哥's is "T+2"; Buffett's position sizing is "集中前 5 大 70%+", Simons' is
"等权数千只，单票 < 0.5%".

Fields:
    time_horizon:              该投资者自然持仓周期
    position_sizing:           该投资者的仓位/集中度风格
    what_would_change_my_mind: 什么会让他/她**翻盘** — 触发卖出/反向的条件

Design principle:
- 22 个标志性人物各自手写 authentic 内容（覆盖 7 个流派）
- 其余 ~29 人用 GROUP_DEFAULT 按流派 fallback（好过通用默认，但不冒充个人风格）
- 未注册人物回 GENERIC_FALLBACK

Keys follow `id` in lib/investor_db.py.
Sources are real quotes / methodology summaries / published behavior patterns.
"""
from __future__ import annotations


# ═══════════════════════════════════════════════════════════════
# 22 标志性人物 · 每人 authentic 3 字段
# ═══════════════════════════════════════════════════════════════
PROFILES: dict[str, dict[str, str]] = {
    # ────── Group A · 经典价值 ──────
    "buffett": {
        "time_horizon": "10 年以上 / 永远；如果你不愿意持有十年，就不要持有十分钟",
        "position_sizing": "集中持仓，前 5 大通常占 70%+；好机会稀有，要重仓",
        "what_would_change_my_mind": "ROE 连续 2 年跌破 12% · CEO 离职且战略转向 · 发现管理层诚信问题 · 商业模式被颠覆（例如纺织、报纸）",
    },
    "graham": {
        "time_horizon": "2-3 年；达到内在价值或持有 2 年仍跑输市场则卖出",
        "position_sizing": "分散至少 30 只，单票上限 5%，防御型投资者的铁律",
        "what_would_change_my_mind": "PE × PB > 22.5 · 流动比率跌破 2 · 连续两年无盈利 · 股息中断",
    },
    "fisher": {
        "time_horizon": "长期持有 5-15 年，让伟大的公司给你长期复利",
        "position_sizing": "集中 10-20 只，深入了解后重仓；不懂的不碰",
        "what_would_change_my_mind": "15 要点中出现 3 项以上恶化 · 管理层对投资者不坦诚 · 研发投入比突降 · 利润率持续侵蚀",
    },
    "munger": {
        "time_horizon": "终身持有好生意，除非基本面永久性恶化",
        "position_sizing": "极度集中，3-5 只占组合 80%+；反过来想，分散是能力不足的承认",
        "what_would_change_my_mind": "反过来想——'这家最可能怎么死？' 看到 2 个以上答案时就要警觉 · 管理层 incentive 跑偏",
    },
    "klarman": {
        "time_horizon": "灵活，有机会就出手，没机会就拿现金；特殊事件驱动为主",
        "position_sizing": "可以 30-50% 现金等机会；单票 5-10%，特殊情形可更高",
        "what_would_change_my_mind": "安全边际消失（市值接近 NAV）· 催化剂被推迟或取消 · 出现更好的错杀机会",
    },

    # ────── Group B · 成长派 ──────
    "lynch": {
        "time_horizon": "公司故事讲完为止，典型 3-5 年；小盘 fast-grower 可以短些",
        "position_sizing": "30-50 只多样化，按 6 类（稳定/周期/fast/慢/困境/资产）配比",
        "what_would_change_my_mind": "PEG > 2（成长不配估值）· 库存/应收增速超过营收 · 故事不再兑现 · 个人能接触的场景里热度消退",
    },
    "oneill": {
        "time_horizon": "握到 cup-and-handle 失败或 50 日均线破位；典型 3-12 个月",
        "position_sizing": "初仓 25%，突破加仓至 100%；CANSLIM 7 维不达标不开仓",
        "what_would_change_my_mind": "M 大盘转熊 · 跌破买入价 7-8% 无条件止损 · RS 强度跌出前 20% · 季度 EPS 减速",
    },
    "thiel": {
        "time_horizon": "Power law 回报，一笔对的能 cover 所有错的；持有至 IPO/被收购",
        "position_sizing": "极度不分散，单笔可 30%+；先找垄断再谈估值",
        "what_would_change_my_mind": "竞争进入（垄断破） · 网络效应被新技术绕过 · 管理层卖股转向",
    },
    "wood": {
        "time_horizon": "5 年视角看颠覆性技术拐点；短期波动不是卖出理由",
        "position_sizing": "高 β 组合单票可 10%+，接受 50% 回撤换 10x 上行",
        "what_would_change_my_mind": "S-curve 采用率斜率走平 · 监管禁令 · 核心技术被更新范式替代",
    },

    # ────── Group C · 宏观对冲 ──────
    "soros": {
        "time_horizon": "反身性循环一轮，通常数周到数月，随时可翻转",
        "position_sizing": "重仓押一次（sterling 1992 那种），但任何时候都可反向",
        "what_would_change_my_mind": "市场停止验证我的叙事（反身性反转）· 基本面超出错误区间 · 更好的非对称机会出现",
    },
    "dalio": {
        "time_horizon": "All Weather 全天候配置，再平衡周期约 1 年；单次押注几天到几月",
        "position_sizing": "风险平价：每类资产的波动率贡献相等，不看单票",
        "what_would_change_my_mind": "经济周期象限切换（增长↑↓ × 通胀↑↓ 四宫格）· 央行政策拐点 · 长债利率结构破位",
    },
    "druck": {
        "time_horizon": "灵活，从几周到 2 年；对错都要快速反应",
        "position_sizing": "不对的时候只下小注，极度对的时候 all-in；集中非常高",
        "what_would_change_my_mind": "央行立场转向 · 自己的赔率判断被市场证伪 · 发现更大赔率的品种",
    },
    "marks": {
        "time_horizon": "完整的市场周期（通常 5-7 年），周期位置决定进出",
        "position_sizing": "逆向：别人抢时不买，别人弃时买；单票仓位按风险定价调",
        "what_would_change_my_mind": "二阶思维反转（我对多数人的判断变了）· 风险溢价收敛到极值 · 周期钟摆触顶",
    },

    # ────── Group D · 技术趋势 ──────
    "livermore": {
        "time_horizon": "吃完主升浪，通常数周到数月，坐住比交易难",
        "position_sizing": "试仓-验证-加仓-重仓 pyramid；错了立刻止损走人",
        "what_would_change_my_mind": "关键支撑破位 · 领涨股走弱 · 整体市场 tone 改变 · 任何反向信号 '立即 get out'",
    },
    "minervini": {
        "time_horizon": "VCP 突破后 3-6 个月吃主升浪；跌破 20 日立即减仓",
        "position_sizing": "初始 25% 仓位，确认追加至 100%；亏损不超过整仓 2%",
        "what_would_change_my_mind": "跌破 10/20 日均线 · 放量下跌 · 趋势模板 8 条件中 3 项以上失效",
    },

    # ────── Group E · 中国价投 ──────
    "duan": {
        "time_horizon": "10-20 年，好的公司尽可能长；搞懂了就敢重仓",
        "position_sizing": "极度集中：Apple 占他组合大半；敢 all-in 到自己真的懂的",
        "what_would_change_my_mind": "生意的本质变了（不是季度波动）· 管理层 incentive 偏移 · 自己真的不懂了就卖",
    },
    "zhangkun": {
        "time_horizon": "3-5 年中期；白酒、医药、大消费要看够一个周期",
        "position_sizing": "易方达蓝筹前十大长期占 70%+，低换手；好公司等回调",
        "what_would_change_my_mind": "ROE 连续 2 年掉队行业平均 · 估值分位超 90% · 管理层大规模变动",
    },
    "fengliu": {
        "time_horizon": "3-6 个月等错杀修复，弱者体系不预测只应对",
        "position_sizing": "偏均衡，单票不超 10%；用足够差价换取错了也能扛",
        "what_would_change_my_mind": "基本面证伪（订单/产能/客户反馈）· 价格修复完毕 · 发现更大错杀",
    },
    "dengxiaofeng": {
        "time_horizon": "2-4 年跨周期，深度研究周期行业与产业链",
        "position_sizing": "集中产业链龙头，单票 10-20%；周期底部布局、顶部卖",
        "what_would_change_my_mind": "产能周期见顶信号 · 价格下行兑现 · 下游需求证伪",
    },

    # ────── Group F · A 股游资 ──────
    "zhao_lg": {
        "time_horizon": "T+2 到 T+5，吃打板主升；强度退化立即走",
        "position_sizing": "龙头板仓位 10-20%，T+1 根据分歧加减；绝不过周末的不隔夜",
        "what_would_change_my_mind": "板上砸盘 · 龙头断板 · 龙虎榜出现对手方机构 · 量能跟不上",
    },
    "zhang_mz": {
        "time_horizon": "核心大龙 7-15 天，吃到主升末期",
        "position_sizing": "打最强龙头，重仓敢拿；接力中军分仓",
        "what_would_change_my_mind": "题材逻辑证伪 · 大盘系统性风险 · 自己席位被跟风破坏节奏",
    },
    # 注：chengdu（成都帮）是席位集合体非个人，按 quotes-knowledge-base 的
    # 「席位类游资·无个人原话」分类走 Group F fallback，而不是冒充成有 authored 方法论。
    "lasa": {
        "time_horizon": "1-2 天，打首板 / 二板为主",
        "position_sizing": "单票 5-15%，封板率高时加仓；封板力度弱就跑",
        "what_would_change_my_mind": "封板时间推后 · 开板即砸 · 情绪周期从亢奋转分歧",
    },

    # ────── Group G · 量化 ──────
    "simons": {
        "time_horizon": "平均持仓 < 2 天；数秒到数月组合，完全由模型决定",
        "position_sizing": "等权数千只，单票仓位 < 0.5%；风险预算由协方差决定",
        "what_would_change_my_mind": "模型信号 Sharpe 跌破 0.5 · 因子衰减 · 市场结构变化（如交易制度改变）",
    },

    # ────── Group H · AI 卡位/瓶颈猎手 ──────
    "serenity": {
        "time_horizon": "thesis-driven，从信息差到机构 rotation 兑现，典型数月到 1-2 年；瓶颈逻辑不破就拿住",
        "position_sizing": "极度集中 + 约 1.3-1.4x margin，最高信念的卡点敢满仓重押；不在链上的一律 0 仓",
        "what_would_change_my_mind": "卡位被证伪（出现可替代方案 / 新增产能放量）· 供给从紧转松 · 下游 roadmap 绕过该节点 · 估值已反映瓶颈、信息差消失",
    },
    "ghzw": {  # v3.9.0 · 股海贼王 · 数据来自其十年实盘 (8951 笔交割单)
        "time_horizon": "超短接力 T+1 到 T+5（持仓中位 1 天）· 时代级格局票可拿数月看三五倍",
        "position_sizing": "同时 3-5 只 · 第一重仓常打五成 · 闲钱逆回购 · 高位票绝不满仓搞",
        "what_would_change_my_mind": "主线退潮 · 弱转强失败/盘口承接消失 · 大盘系统性风险（自认十年最大弱项 · 赚 15 个点就休息）",
    },

}


# ═══════════════════════════════════════════════════════════════
# Group-level fallback · 未单独注册的投资者按流派走
# ═══════════════════════════════════════════════════════════════
# 每个流派给一份**流派级**但仍足够具体的默认，好过通用默认。
# 落在这里的投资者至少不会用错流派的语境回答问题。
GROUP_DEFAULT: dict[str, dict[str, str]] = {
    "A": {  # 经典价值
        "time_horizon": "3-10 年，等公司兑现内在价值",
        "position_sizing": "集中 10-20 只，重仓高确定性机会",
        "what_would_change_my_mind": "基本面永久性恶化 · 管理层诚信受损 · 安全边际被市场吃掉",
    },
    "B": {  # 成长派
        "time_horizon": "2-5 年，跟随公司成长曲线",
        "position_sizing": "中度集中 20-30 只，成长最猛的票重仓",
        "what_would_change_my_mind": "增长失速 · 估值与成长严重背离（PEG>2）· 护城河被穿",
    },
    "C": {  # 宏观对冲
        "time_horizon": "数周到数月，跟随宏观节奏与流动性窗口",
        "position_sizing": "按赔率分配，对的时候敢重仓，错的时候立即认错",
        "what_would_change_my_mind": "宏观叙事被证伪 · 央行/政策转向 · 赔率变得不利",
    },
    "D": {  # 技术趋势
        "time_horizon": "数周到 3 个月，跟趋势做，破位就走",
        "position_sizing": "Pyramid 加仓，亏损严格控制在单笔 2% 以内",
        "what_would_change_my_mind": "关键均线破位 · 量能背离 · 相对强度掉出前列",
    },
    "E": {  # 中国价投
        "time_horizon": "3-5 年，等好公司给好价格",
        "position_sizing": "偏集中，单票 5-15%；深度研究后重仓",
        "what_would_change_my_mind": "ROE / 净利率掉队行业 · 管理层或核心业务大变 · 估值分位过高",
    },
    "F": {  # A 股游资
        "time_horizon": "T+1 到 T+5 超短线，视盘面决定",
        "position_sizing": "单票 5-20%，强度强时加仓、弱时立即走",
        "what_would_change_my_mind": "板上砸盘 / 断板 · 量能不配合 · 龙虎榜对手方压过自己席位",
    },
    "G": {  # 量化
        "time_horizon": "由模型决定，通常数天到数周",
        "position_sizing": "等权或风险平价分散，单票权重由模型算",
        "what_would_change_my_mind": "因子 IC 衰减 · Sharpe 下降 · 市场微观结构改变",
    },
    # v3.8.1 · 补 H/I（之前缺失 → H/I 评委 profile 落到 GENERIC_FALLBACK 全是 "—"）
    "H": {  # 科技领袖派（黄仁勋/马斯克/Altman/Saylor · 看自家产业链）
        "time_horizon": "5-10 年技术周期，跟随平台迁移（AI/EV/AGI/数字资产）",
        "position_sizing": "极度集中——All in 自己看得最清的产业链节点",
        "what_would_change_my_mind": "技术路线被颠覆 · scaling 失效 · 产业链节点被绕过",
    },
    "I": {  # AI 卡位/瓶颈猎手（Serenity）
        "time_horizon": "6-24 个月，从市场未定价埋伏到瓶颈被公认",
        "position_sizing": "高信念集中重仓 1-3 只卡点小盘，确认错了立即清仓",
        "what_would_change_my_mind": "替代方案量产 · 产能瓶颈解除 · 卡点被市场充分定价",
    },
}


# ═══════════════════════════════════════════════════════════════
# Generic fallback · 不在任何已知流派
# ═══════════════════════════════════════════════════════════════
GENERIC_FALLBACK: dict[str, str] = {
    "time_horizon": "—",
    "position_sizing": "—",
    "what_would_change_my_mind": "—",
}


# ═══════════════════════════════════════════════════════════════
# 한국어 병렬 출력부 (D8 · 기존 中文 PROFILES 비침습 · UZI_LANG=ko 시 사용)
# ═══════════════════════════════════════════════════════════════
PROFILES_KO: dict[str, dict[str, str]] = {
    # ── Group A · 클래식 가치 ──
    "buffett": {
        "time_horizon": "10년 이상 / 영원히; 10년 보유할 생각이 없으면 10분도 보유하지 마라",
        "position_sizing": "집중 보유, 상위 5종목이 보통 70%+; 좋은 기회는 드무니 크게 베팅",
        "what_would_change_my_mind": "ROE 2년 연속 12% 하회 · CEO 사임 및 전략 선회 · 경영진 정직성 문제 발견 · 비즈니스 모델 붕괴(예: 섬유·신문)",
    },
    "graham": {
        "time_horizon": "2~3년; 내재가치 도달 또는 2년 보유해도 시장 하회 시 매도",
        "position_sizing": "최소 30종목 분산, 단일종목 상한 5%, 방어적 투자자의 철칙",
        "what_would_change_my_mind": "PER × PBR > 22.5 · 유동비율 2 하회 · 2년 연속 무이익 · 배당 중단",
    },
    "fisher": {
        "time_horizon": "장기 보유 5~15년, 위대한 기업이 장기 복리를 안겨주게 하라",
        "position_sizing": "집중 10~20종목, 깊이 이해한 뒤 크게 베팅; 모르는 건 손대지 않는다",
        "what_would_change_my_mind": "15개 핵심 포인트 중 3개 이상 악화 · 경영진이 투자자에게 솔직하지 않음 · R&D 투자 비중 급락 · 이익률 지속 잠식",
    },
    "munger": {
        "time_horizon": "좋은 사업은 평생 보유, 펀더멘털이 영구적으로 악화되지 않는 한",
        "position_sizing": "극도로 집중, 3~5종목이 포트폴리오 80%+; 거꾸로 생각하라, 분산은 능력 부족의 인정",
        "what_would_change_my_mind": "거꾸로 생각하라—'이 회사가 가장 망하기 쉬운 경로는?' 답이 2개 이상 보이면 경계 · 경영진 인센티브 어긋남",
    },
    "klarman": {
        "time_horizon": "유연하게, 기회 있으면 출수 없으면 현금 보유; 특수상황 이벤트 드리븐 위주",
        "position_sizing": "30~50% 현금으로 기회 대기 가능; 단일종목 5~10%, 특수상황은 더 높게",
        "what_would_change_my_mind": "안전마진 소멸(시총이 NAV 근접) · 촉매 지연 또는 취소 · 더 좋은 저평가 기회 출현",
    },
    # ── Group B · 성장파 ──
    "lynch": {
        "time_horizon": "기업 스토리가 끝날 때까지, 보통 3~5년; 소형 fast-grower는 더 짧게",
        "position_sizing": "30~50종목 다양화, 6유형(안정/경기순환/고성장/저성장/회생/자산주)으로 배분",
        "what_would_change_my_mind": "PEG > 2(성장이 밸류에이션을 못 받침) · 재고/매출채권 증가율이 매출 초과 · 스토리 미실현 · 일상에서 접하던 인기 소멸",
    },
    "oneill": {
        "time_horizon": "cup-and-handle 실패 또는 50일선 이탈까지; 보통 3~12개월",
        "position_sizing": "초기 25%, 돌파 시 100%까지 추가; CANSLIM 7요소 미달이면 진입 안 함",
        "what_would_change_my_mind": "M 시장 약세 전환 · 매수가 7~8% 하회 시 무조건 손절 · RS 강도 상위 20% 이탈 · 분기 EPS 감속",
    },
    "thiel": {
        "time_horizon": "Power law 수익, 한 번의 정답이 모든 오답을 커버; IPO/피인수까지 보유",
        "position_sizing": "극도로 비분산, 단일 베팅 30%+ 가능; 독점을 먼저 찾고 밸류에이션은 나중",
        "what_would_change_my_mind": "경쟁 진입(독점 붕괴) · 네트워크 효과가 신기술에 우회당함 · 경영진 지분 매도 선회",
    },
    "wood": {
        "time_horizon": "5년 시계로 파괴적 기술 변곡점을 본다; 단기 변동은 매도 이유가 아니다",
        "position_sizing": "고베타 포트폴리오 단일종목 10%+ 가능, 10배 상승 위해 50% 낙폭 감내",
        "what_would_change_my_mind": "S-curve 채택률 기울기 평탄화 · 규제 금지 · 핵심기술이 새 패러다임에 대체",
    },
    # ── Group C · 매크로 헤지 ──
    "soros": {
        "time_horizon": "재귀성 순환 한 사이클, 보통 수주~수개월, 언제든 뒤집힐 수 있다",
        "position_sizing": "한 번에 크게 베팅(1992 파운드화 같은), 그러나 언제든 반대로 돌 수 있다",
        "what_would_change_my_mind": "시장이 내 내러티브 검증을 멈춤(재귀성 반전) · 펀더멘털이 오차범위 초과 · 더 좋은 비대칭 기회 출현",
    },
    "dalio": {
        "time_horizon": "All Weather 전천후 배분, 리밸런싱 주기 약 1년; 단일 베팅은 며칠~몇 달",
        "position_sizing": "리스크 패리티: 각 자산군의 변동성 기여를 균등하게, 단일종목 안 봄",
        "what_would_change_my_mind": "경기 사이클 사분면 전환(성장↑↓ × 인플레↑↓) · 중앙은행 정책 변곡점 · 장기채 금리 구조 이탈",
    },
    "druck": {
        "time_horizon": "유연하게, 수주~2년; 맞든 틀리든 빠르게 반응",
        "position_sizing": "틀릴 땐 소액만, 극도로 맞을 땐 all-in; 집중도 매우 높음",
        "what_would_change_my_mind": "중앙은행 입장 선회 · 자신의 손익비 판단이 시장에서 반증됨 · 더 큰 손익비의 종목 발견",
    },
    "marks": {
        "time_horizon": "완전한 시장 사이클(보통 5~7년), 사이클 위치가 진출입 결정",
        "position_sizing": "역발상: 남들이 살 때 안 사고, 남들이 버릴 때 산다; 단일종목 비중은 리스크 가격 따라 조정",
        "what_would_change_my_mind": "2차적 사고 반전(다수에 대한 내 판단이 바뀜) · 리스크 프리미엄이 극값으로 수렴 · 사이클 진자 정점 도달",
    },
    # ── Group D · 기술 추세 ──
    "livermore": {
        "time_horizon": "주 상승파를 다 먹을 때까지, 보통 수주~수개월, 버티는 게 매매보다 어렵다",
        "position_sizing": "시험매수-검증-추가-집중 피라미드; 틀리면 즉시 손절하고 나간다",
        "what_would_change_my_mind": "핵심 지지선 이탈 · 주도주 약화 · 시장 전체 톤 변화 · 어떤 반대 신호든 '즉시 빠져나간다'",
    },
    "minervini": {
        "time_horizon": "VCP 돌파 후 3~6개월 주 상승파; 20일선 이탈 시 즉시 축소",
        "position_sizing": "초기 25% 비중, 확인 후 100%까지 추가; 손실은 전체의 2% 초과 금지",
        "what_would_change_my_mind": "10/20일선 이탈 · 대량 하락 · 추세 템플릿 8조건 중 3개 이상 실패",
    },
    # ── Group E · 중국 가치투자 ──
    "duan": {
        "time_horizon": "10~20년, 좋은 회사는 최대한 길게; 이해했으면 크게 베팅",
        "position_sizing": "극도로 집중: Apple이 그의 포트폴리오 절반 이상; 진짜 이해한 것엔 all-in",
        "what_would_change_my_mind": "사업의 본질이 변함(분기 변동 아님) · 경영진 인센티브 이탈 · 자신이 정말 이해 못 하게 되면 매도",
    },
    "zhangkun": {
        "time_horizon": "3~5년 중기; 주류·제약·대형소비재는 한 사이클을 충분히 봐야",
        "position_sizing": "이팡다 블루칩 상위10이 장기 70%+, 낮은 회전율; 좋은 회사는 조정을 기다린다",
        "what_would_change_my_mind": "ROE 2년 연속 업종 평균 하회 · 밸류에이션 분위 90% 초과 · 경영진 대규모 변동",
    },
    "fengliu": {
        "time_horizon": "3~6개월 저평가 회복 대기, 약자 체계는 예측하지 않고 대응만",
        "position_sizing": "균형 지향, 단일종목 10% 이하; 충분한 가격차로 틀려도 버틸 수 있게",
        "what_would_change_my_mind": "펀더멘털 반증(주문/생산능력/고객 피드백) · 가격 회복 완료 · 더 큰 저평가 발견",
    },
    "dengxiaofeng": {
        "time_horizon": "2~4년 사이클 횡단, 경기순환 업종과 밸류체인을 깊이 연구",
        "position_sizing": "밸류체인 선두주 집중, 단일종목 10~20%; 사이클 바닥 매집·정점 매도",
        "what_would_change_my_mind": "생산능력 사이클 정점 신호 · 가격 하락 실현 · 전방 수요 반증",
    },
    # ── Group F · A주 단타(游资) ──
    "zhao_lg": {
        "time_horizon": "T+2~T+5, 상한가 주 상승파; 강도 약화 시 즉시 이탈",
        "position_sizing": "주도 섹터 비중 10~20%, T+1에 분기 따라 가감; 주말 넘기는 종목은 절대 오버나이트 안 함",
        "what_would_change_my_mind": "상한가에서 매도 출회 · 주도주 상한가 풀림 · 거래대금 순위에 기관 상대방 출현 · 거래량 미달",
    },
    "zhang_mz": {
        "time_horizon": "핵심 대장주 7~15일, 주 상승 말기까지",
        "position_sizing": "최강 주도주 매매, 크게 베팅; 이어받는 중군은 분산",
        "what_would_change_my_mind": "테마 논리 반증 · 시장 시스템 리스크 · 자기 자리가 추종 매수에 리듬 파괴",
    },
    "lasa": {
        "time_horizon": "1~2일, 첫 상한가/둘째 상한가 위주",
        "position_sizing": "단일종목 5~15%, 상한가 안착률 높을 때 추가; 안착 강도 약하면 이탈",
        "what_would_change_my_mind": "상한가 안착 시간 지연 · 개장 즉시 매도 출회 · 심리 사이클이 흥분에서 분기로 전환",
    },
    # ── Group G · 퀀트 ──
    "simons": {
        "time_horizon": "평균 보유 < 2일; 수초~수개월 조합, 전적으로 모델이 결정",
        "position_sizing": "수천 종목 등가중, 단일종목 비중 < 0.5%; 리스크 예산은 공분산으로 결정",
        "what_would_change_my_mind": "모델 신호 Sharpe 0.5 하회 · 팩터 감쇠 · 시장 구조 변화(예: 거래제도 변경)",
    },
    # ── Group H · AI 길목/병목 헌터 ──
    "serenity": {
        "time_horizon": "thesis-driven, 정보 격차에서 기관 rotation 실현까지, 보통 수개월~1~2년; 병목 논리가 깨지지 않으면 보유",
        "position_sizing": "극도 집중 + 약 1.3~1.4x 마진, 최고 신념의 길목엔 풀베팅; 밸류체인 밖은 일률 0 비중",
        "what_would_change_my_mind": "길목이 반증됨(대체안 출현/신규 생산능력 방출) · 공급이 긴축에서 완화로 · 전방 roadmap이 해당 노드 우회 · 밸류에이션이 병목 반영하고 정보 격차 소멸",
    },
    "ghzw": {
        "time_horizon": "초단기 이어받기 T+1~T+5(보유 중위값 1일) · 시대급 구도주는 수개월 보유해 3~5배 노림",
        "position_sizing": "동시 3~5종목 · 최우선 집중은 보통 50% · 여유자금은 역RP · 고점주는 절대 풀베팅 안 함",
        "what_would_change_my_mind": "주력 라인 퇴조 · 약→강 전환 실패/호가 받침 소멸 · 시장 시스템 리스크(스스로 10년 최대 약점 인정 · 15% 먹으면 휴식)",
    },
}


GROUP_DEFAULT_KO: dict[str, dict[str, str]] = {
    "A": {
        "time_horizon": "3~10년, 회사가 내재가치 실현하길 기다림",
        "position_sizing": "집중 10~20종목, 고확실성 기회에 크게 베팅",
        "what_would_change_my_mind": "펀더멘털 영구 악화 · 경영진 정직성 훼손 · 안전마진이 시장에 잠식",
    },
    "B": {
        "time_horizon": "2~5년, 회사 성장 곡선을 따라",
        "position_sizing": "중간 집중 20~30종목, 가장 강한 성장주 크게",
        "what_would_change_my_mind": "성장 실속 · 밸류에이션과 성장 심각 괴리(PEG>2) · 해자 돌파",
    },
    "C": {
        "time_horizon": "수주~수개월, 거시 리듬과 유동성 창 따라",
        "position_sizing": "손익비 따라 배분, 맞을 땐 크게, 틀릴 땐 즉시 인정",
        "what_would_change_my_mind": "거시 내러티브 반증 · 중앙은행/정책 선회 · 손익비가 불리해짐",
    },
    "D": {
        "time_horizon": "수주~3개월, 추세 따라, 이탈하면 이탈",
        "position_sizing": "피라미드 추가, 손실은 단일 베팅 2% 이내로 엄격 통제",
        "what_would_change_my_mind": "핵심 이평선 이탈 · 거래량 다이버전스 · 상대강도 선두 이탈",
    },
    "E": {
        "time_horizon": "3~5년, 좋은 회사가 좋은 가격 주길 기다림",
        "position_sizing": "집중 지향, 단일종목 5~15%; 깊이 연구 후 크게",
        "what_would_change_my_mind": "ROE/순이익률 업종 하회 · 경영진 또는 핵심사업 대변동 · 밸류에이션 분위 과도",
    },
    "F": {
        "time_horizon": "T+1~T+5 초단기, 호가 보고 결정",
        "position_sizing": "단일종목 5~20%, 강할 때 추가·약할 때 즉시 이탈",
        "what_would_change_my_mind": "상한가 매도 출회/풀림 · 거래량 미동조 · 거래대금 상대방이 자기 자리 압도",
    },
    "G": {
        "time_horizon": "모델이 결정, 보통 수일~수주",
        "position_sizing": "등가중 또는 리스크 패리티 분산, 단일 비중은 모델이 계산",
        "what_would_change_my_mind": "팩터 IC 감쇠 · Sharpe 하락 · 시장 미시구조 변화",
    },
    "H": {
        "time_horizon": "5~10년 기술 사이클, 플랫폼 이전 따라(AI/EV/AGI/디지털자산)",
        "position_sizing": "극도 집중—가장 명확히 보이는 밸류체인 노드에 All in",
        "what_would_change_my_mind": "기술 노선 붕괴 · scaling 실패 · 밸류체인 노드 우회당함",
    },
    "I": {
        "time_horizon": "6~24개월, 시장 미반영 매복에서 병목 공인까지",
        "position_sizing": "고신념 집중 1~3종목 길목 소형주, 틀리면 즉시 청산",
        "what_would_change_my_mind": "대체안 양산 · 생산능력 병목 해소 · 길목이 시장에 충분히 반영됨",
    },
}


GENERIC_FALLBACK_KO: dict[str, str] = {
    "time_horizon": "—",
    "position_sizing": "—",
    "what_would_change_my_mind": "—",
}


def get_profile(investor_id: str, group: str = "") -> dict[str, str]:
    """Return the authentic 3-field profile for one investor.

    Priority:
      1. PROFILES[investor_id] — 22 个标志性人物手写内容
      2. GROUP_DEFAULT[group]  — 流派级 fallback
      3. GENERIC_FALLBACK      — 最后默认

    参数：
      investor_id: e.g. 'buffett' / 'zhao_lg' / 'simons'
      group:       e.g. 'A' / 'F' — 从 investor_db 取，用于 fallback

    返回：
      {'time_horizon': ..., 'position_sizing': ..., 'what_would_change_my_mind': ...}
    """
    # K(한국) · UZI_LANG=ko 면 한국어 프로파일 (D8 · 기존 中文 경로 비침습)
    try:
        from lib.i18n import get_language
        _ko = (get_language() == "ko")
    except Exception:
        _ko = False
    if _ko:
        if investor_id in PROFILES_KO:
            return dict(PROFILES_KO[investor_id])
        if group and group in GROUP_DEFAULT_KO:
            return dict(GROUP_DEFAULT_KO[group])
        return dict(GENERIC_FALLBACK_KO)

    if investor_id in PROFILES:
        return dict(PROFILES[investor_id])
    if group and group in GROUP_DEFAULT:
        return dict(GROUP_DEFAULT[group])
    return dict(GENERIC_FALLBACK)


def stats() -> dict:
    """Coverage report."""
    return {
        "authored_profiles": len(PROFILES),
        "groups_with_defaults": len(GROUP_DEFAULT),
        "authored_ids": sorted(PROFILES.keys()),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(stats(), ensure_ascii=False, indent=2))
    print()
    print("=== Sample profiles ===")
    for inv_id in ("buffett", "zhao_lg", "simons", "lynch", "soros"):
        print(f"\n{inv_id}:")
        print(json.dumps(get_profile(inv_id), ensure_ascii=False, indent=2))
