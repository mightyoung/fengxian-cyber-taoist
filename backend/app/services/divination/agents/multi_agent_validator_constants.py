"""
Multi-Agent Validator Constants - 多Agent共识验证常量定义

包含：
- ExpertAuthor: 专家作者枚举
- EXPERT_AUTHOR_DESCRIPTIONS: 作者专业领域描述
- AGENT_WEIGHTS: Agent权重配置
- EXPERT_ROLE_WEIGHTS: 专家角色权重
- DEFAULT_AGENT_WEIGHT: 默认Agent权重
- DEFAULT_EXPERT_WEIGHT: 默认专家权重

注意：Enums 和 Dataclasses 请使用 multi_agent_validator_types 模块
"""

from enum import Enum
from typing import Dict


class ExpertAuthor(str, Enum):
    """专家作者定义 - 基于data_source/mlx/resources/md目录下的真实作者"""
    XU_QUAN_REN = "许铨仁"           # 《命理学正解》- 斗数界公认的好老师
    LIANG_RUO_YU = "梁若瑜"           # 《飞星紫微斗数》- 四化能量符号专家
    WANG_TING_ZHI = "王亭之"          # 《中州派紫微斗数深造讲义》- 中州派正统
    ZI_YUN = "紫云"                   # 《紫云论斗数 星曜赋性》- 星曜赋性专家


# 作者专业领域描述
EXPERT_AUTHOR_DESCRIPTIONS: Dict[ExpertAuthor, Dict] = {
    ExpertAuthor.XU_QUAN_REN: {
        "name": "许铨仁",
        "title": "《命理学正解》作者",
        "school": "台湾斗数学派",
        "expertise": [
            "斗数命理学正本清源",
            "宫星象三合一完整解义学",
            "象数平衡学",
            "理则学而非神学"
        ],
        "key_theories": [
            "紫微斗数命理学系哲学/理则学",
            "绝无'改命''改运'之谬论",
            "宫星象三合一解义"
        ]
    },
    ExpertAuthor.LIANG_RUO_YU: {
        "name": "梁若瑜",
        "title": "《飞星紫微斗数》作者",
        "school": "飞星派",
        "expertise": [
            "四化是能量符号",
            "禄转忌、忌转忌分析",
            "多宫位串联释象",
            "理气的逻辑归纳"
        ],
        "key_theories": [
            "禄因忌果",
            "善观禄忌解析问题",
            "追禄/追权/追忌",
            "忌入逢本宫自化禄出"
        ]
    },
    ExpertAuthor.WANG_TING_ZHI: {
        "name": "王亭之",
        "title": "《中州派紫微斗数深造讲义》作者",
        "school": "中州派",
        "expertise": [
            "中州派紫微斗数正统传承",
            "太微赋注解",
            "星曜赋性深化",
            "格局体系"
        ],
        "key_theories": [
            "中州派格局论断",
            "星曜庙旺平陷",
            "宫位三方四正关系"
        ]
    },
    ExpertAuthor.ZI_YUN: {
        "name": "紫云",
        "title": "《紫云论斗数 星曜赋性》作者",
        "school": "星曜派",
        "expertise": [
            "星曜赋性详解（5册）",
            "十四正曜特性",
            "辅星、煞星配置",
            "星曜组合效应"
        ],
        "key_theories": [
            "星曜五行属性",
            "星曜入宫论断",
            "星曜互动关系"
        ]
    }
}


# Agent权重配置：基于专家角色的重要性
# 紫微斗数专家权重最高（专业知识是核心），其他专家辅助验证
AGENT_WEIGHTS: Dict[str, float] = {
    # 技术Agent权重
    "TransformAgent": 1.0,   # 四化分析是核心
    "PatternAgent": 0.8,     # 格局识别重要
    "PalaceAgent": 0.7,     # 宫位分析基础
    "StarAgent": 0.6,       # 星曜分析基础
    # 其他Agent默认权重
    "TimingAgent": 0.5,
    "WealthAgent": 0.5,
    "HealthAgent": 0.5,
    "CareerAgent": 0.5,
    "RelationshipAgent": 0.5,
    "EducationAgent": 0.5,
    "ResolutionAgent": 0.4,
}

# 专家角色权重（专家验证层）
# 基于真实作者的专业领域和影响力
EXPERT_ROLE_WEIGHTS: Dict[ExpertAuthor, float] = {
    ExpertAuthor.XU_QUAN_REN: 1.0,     # 命理学正解派 - 理论根基
    ExpertAuthor.LIANG_RUO_YU: 0.95,   # 飞星派 - 四化能量是核心
    ExpertAuthor.WANG_TING_ZHI: 0.9,    # 中州派 - 正统传承
    ExpertAuthor.ZI_YUN: 0.85,          # 星曜派 - 星曜赋性为基础
}

# 默认权重
DEFAULT_AGENT_WEIGHT: float = 0.5
DEFAULT_EXPERT_WEIGHT: float = 0.5


def get_agent_weight(agent_name: str) -> float:
    """获取Agent权重"""
    return AGENT_WEIGHTS.get(agent_name, DEFAULT_AGENT_WEIGHT)


def get_expert_weight(expert_role: ExpertAuthor) -> float:
    """获取专家角色权重"""
    return EXPERT_ROLE_WEIGHTS.get(expert_role, DEFAULT_EXPERT_WEIGHT)
