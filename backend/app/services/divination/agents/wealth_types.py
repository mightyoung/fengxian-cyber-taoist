"""
Wealth Types - 财运分析数据类型

包含：
- WealthLevel: 财富等级枚举
- PalaceWealthAnalysis: 宫位财富分析
- WealthPattern: 财富格局
- YearlyWealthForecast: 年度财富预测
- WealthReport: 完整财富报告

注意：常量定义请使用 wealth_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class WealthLevel(str, Enum):
    """财富等级"""
    TOP_RICH = "顶级富"      # 90-100
    VERY_RICH = "大富"       # 75-89
    MEDIUM_RICH = "中富"    # 60-74
    SMALL_RICH = "小富"      # 45-59
    NORMAL = "普通"          # 30-44
    POOR = "清贫"            # 0-29


@dataclass
class PalaceWealthAnalysis:
    """宫位财富分析"""
    palace_name: str
    score: int
    strength_level: str
    main_stars: List[str] = field(default_factory=list)
    auxiliary_stars: List[str] = field(default_factory=list)
    sha_stars: List[str] = field(default_factory=list)
    transform_stars: List[str] = field(default_factory=list)
    interpretation: str = ""
    wealth_indicator: str = ""  # 财富 indicator e.g. "正财之星"
    risk_factors: List[str] = field(default_factory=list)
    opportunity_factors: List[str] = field(default_factory=list)


@dataclass
class WealthPattern:
    """财富格局"""
    pattern_name: str
    description: str
    score_bonus: int  # 加分
    characteristics: List[str] = field(default_factory=list)


@dataclass
class YearlyWealthForecast:
    """年度财富预测"""
    year: int
    wealth_score: int
    gan_zhi: str
    tai_sui_palace: str
    advice: str
    opportunity_periods: List[str] = field(default_factory=list)
    risk_periods: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class WealthReport:
    """完整财富报告"""
    total_wealth_score: int
    wealth_level: str
    caibi_palace: PalaceWealthAnalysis
    tianzhai_palace: PalaceWealthAnalysis
    fude_palace: PalaceWealthAnalysis
    guanlu_palace: PalaceWealthAnalysis
    wealth_patterns: List[WealthPattern] = field(default_factory=list)
    advantages: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    yearly_forecast: List[YearlyWealthForecast] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    investment_advice: Dict[str, str] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
