"""
Marriage Types - 姻缘配对数据类型

包含：
- CompatibilityLevel: 配对等级枚举
- CompatibilityDimension: 配对维度
- CompatibilityResult: 姻缘配对结果

注意：常量定义请使用 marriage_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class CompatibilityLevel(Enum):
    """配对等级"""
    PERFECT = "完美姻缘"      # 90-100
    EXCELLENT = "天作之合"     # 80-89
    GOOD = "良缘佳配"         # 70-79
    AVERAGE = "中规中矩"      # 50-69
    FAIR = "需要努力"         # 30-49
    CHALLENGING = "磨合期"     # 0-29


@dataclass
class CompatibilityDimension:
    """配对维度"""
    dimension: str              # "性格契合" / "财运互补" / "事业助力" / "感情甜蜜" / "健康同步"
    score: float               # 维度分数 0-100
    level: str                 # 等级
    analysis: str              # 分析理由
    positive_factors: List[str] = field(default_factory=list)
    negative_factors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dimension": self.dimension,
            "score": self.score,
            "level": self.level,
            "analysis": self.analysis,
            "positive_factors": self.positive_factors,
            "negative_factors": self.negative_factors,
        }


@dataclass
class CompatibilityResult:
    """姻缘配对结果"""
    service_type: str = "marriage_compatibility"
    person_a_name: str = "甲方"
    person_b_name: str = "乙方"
    overall_score: float = 0.0                    # 综合配对指数 0-100
    overall_level: str = ""                      # 等级
    dimensions: List[CompatibilityDimension] = field(default_factory=list)
    compatibility_highlights: List[str] = field(default_factory=list)  # 亮点
    compatibility_warnings: List[str] = field(default_factory=list)     # 警示
    best_timing: str = ""                        # 最佳时机
    suggestions: List[str] = field(default_factory=list)
    overall_analysis: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "service_type": self.service_type,
            "person_a_name": self.person_a_name,
            "person_b_name": self.person_b_name,
            "overall_score": self.overall_score,
            "overall_level": self.overall_level,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "compatibility_highlights": self.compatibility_highlights,
            "compatibility_warnings": self.compatibility_warnings,
            "best_timing": self.best_timing,
            "suggestions": self.suggestions,
            "overall_analysis": self.overall_analysis,
            "confidence": self.confidence,
        }
