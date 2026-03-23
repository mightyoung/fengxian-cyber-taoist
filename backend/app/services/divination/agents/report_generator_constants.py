"""
ReportGenerator Constants - Markdown报告生成器常量定义

包含：
- CAUSAL_WEIGHT: 因果链权重
- CASE_BASED_WEIGHT: 案例推理权重
- MULTI_AGENT_WEIGHT: 多Agent共识权重
- CORE_DIMENSIONS: 核心维度列表

注意：Dataclasses 请使用 report_generator_types 模块
"""

from typing import List

# ============ 三层融合预测报告权重 ============

CAUSAL_WEIGHT = 0.40  # 因果链权重 40%
CASE_BASED_WEIGHT = 0.35  # 案例推理权重 35%
MULTI_AGENT_WEIGHT = 0.25  # 多Agent共识权重 25%

# ============ 核心维度列表 ============

CORE_DIMENSIONS: List[str] = ["财富", "事业", "感情", "健康"]

# ============ 报告格式化常量 ============

PALACE_STRENGTH_THRESHOLDS = {
    "strong": 70,
    "medium": 40,
}

STAR_SECTION_TYPES = [
    "main_stars",
    "auxiliary_stars",
    "sha_stars",
    "transform_stars",
]

# 评分等级阈值
SCORE_LEVELS = {
    "strong": "🟢强",
    "medium": "🟡中",
    "weak": "🔴弱",
}
