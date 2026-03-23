"""
Pattern Types - 格局分析数据类型

包含：
- PatternCategory: 格局类别枚举
- PatternQuality: 格局等级枚举
- Pattern: 格局数据结构
- PatternAnalysis: 格局分析结果

注意：常量定义请使用 pattern_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class PatternCategory(Enum):
    """格局类别"""
    AUSPICIOUS = "吉格"     # 吉格
    INAUSPICIOUS = "凶格"   # 凶格
    NEUTRAL = "中性格"      # 中性格


class PatternQuality(Enum):
    """格局等级"""
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C = "C"


@dataclass
class Pattern:
    """格局"""
    id: str
    name: str
    name_en: str
    category: PatternCategory
    quality: PatternQuality
    description: str
    source: str
    formation_conditions: Dict[str, Any] = field(default_factory=dict)
    judgment_rules: Dict[str, Any] = field(default_factory=dict)
    analysis_points: List[str] = field(default_factory=list)
    effects: Dict[str, str] = field(default_factory=dict)
    matched: bool = False
    match_details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "category": self.category.value,
            "quality": self.quality.value,
            "description": self.description,
            "source": self.source,
            "matched": self.matched,
            "match_details": self.match_details,
            "effects": self.effects
        }


@dataclass
class PatternAnalysis:
    """格局分析结果

    Attributes:
        year_stem: 出生年干
        patterns: 所有格局列表
        matched_patterns: 已匹配的格局（只读属性）
        auspicious_patterns: 吉格列表
        inauspicious_patterns: 凶格列表
        neutral_patterns: 中性格列表
        interpretation: 格局解释
    """
    year_stem: str
    patterns: List[Pattern] = field(default_factory=list)
    auspicious_patterns: List[Pattern] = field(default_factory=list)
    inauspicious_patterns: List[Pattern] = field(default_factory=list)
    neutral_patterns: List[Pattern] = field(default_factory=list)
    interpretation: str = ""

    @property
    def matched_patterns(self) -> List[Pattern]:
        """已匹配的格局列表（只返回 matched=True 的格局）"""
        return [p for p in self.patterns if p.matched]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year_stem": self.year_stem,
            "matched_patterns": [p.to_dict() for p in self.patterns if p.matched],
            "auspicious_count": len(self.auspicious_patterns),
            "auspicious_patterns": [p.to_dict() for p in self.auspicious_patterns],
            "inauspicious_count": len(self.inauspicious_patterns),
            "inauspicious_patterns": [p.to_dict() for p in self.inauspicious_patterns],
            "neutral_count": len(self.neutral_patterns),
            "neutral_patterns": [p.to_dict() for p in self.neutral_patterns],
            "interpretation": self.interpretation
        }
