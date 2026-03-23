"""
Star Types - 星曜分析数据类型

包含：
- StarLevelType: 星曜庙旺平陷等级枚举
- StarAnalysisResult: 单颗星曜分析结果
- StarAnalysis: 星曜分析结果汇总

注意：常量定义请使用 star_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class StarLevelType(str, Enum):
    """星曜庙旺平陷等级"""
    MIAO = "庙"   # 庙旺 - 最吉
    WANG = "旺"   # 旺 - 次吉
    PING = "平"   # 平 - 中等
    XIAN = "陷"   # 陷 - 凶


@dataclass
class StarAnalysisResult:
    """单颗星曜分析结果"""
    star_name: str
    palace: str
    level: str
    level_type: str
    category: str
    interpretation: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    wuxing_ju: str = ""  # 五行局
    wuxing_influence: str = ""  # 五行局影响说明
    base_level: str = ""  # 基础等级（地支判断）

    def to_dict(self) -> Dict[str, Any]:
        return {
            "star_name": self.star_name,
            "palace": self.palace,
            "level": self.level,
            "level_type": self.level_type,
            "category": self.category,
            "interpretation": self.interpretation,
            "attributes": self.attributes,
            "wuxing_ju": self.wuxing_ju,
            "wuxing_influence": self.wuxing_influence,
            "base_level": self.base_level,
        }


@dataclass
class StarAnalysis:
    """星曜分析结果"""
    main_stars: List[StarAnalysisResult] = field(default_factory=list)
    auxiliary_stars: List[StarAnalysisResult] = field(default_factory=list)
    sha_stars: List[StarAnalysisResult] = field(default_factory=list)
    transform_stars: List[StarAnalysisResult] = field(default_factory=list)
    palace_star_summary: Dict[str, List[str]] = field(default_factory=dict)
    total_stars_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "main_stars": [s.to_dict() for s in self.main_stars],
            "auxiliary_stars": [s.to_dict() for s in self.auxiliary_stars],
            "sha_stars": [s.to_dict() for s in self.sha_stars],
            "transform_stars": [s.to_dict() for s in self.transform_stars],
            "palace_star_summary": self.palace_star_summary,
            "total_stars_count": self.total_stars_count,
        }
