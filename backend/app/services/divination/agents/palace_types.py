"""
Palace Types - 宫位分析数据类型

包含：
- PalaceStrengthLevel: 宫位强弱等级枚举
- PalaceScore: 宫位评分详情
- PalaceAnalysisResult: 单个宫位分析结果
- PalaceAnalysis: 宫位分析结果
- PalaceConnectionResult: 多宫位串联分析结果
- MultiPalaceConnectionAnalysis: 多宫位串联分析汇总
- EmptyPalaceAnalysis: 空宫分析结果

注意：常量定义请使用 palace_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class PalaceStrengthLevel(str, Enum):
    """宫位强弱等级"""
    STRONG = "强"    # 70-100分
    MEDIUM = "中"    # 40-69分
    WEAK = "弱"      # 0-39分


@dataclass
class PalaceScore:
    """宫位评分详情"""
    palace_name: str
    total_score: int
    strength_level: str

    # 各维度得分
    master_star_score: int = 0
    auxiliary_star_score: int = 0
    sha_star_deduction: int = 0
    transform_bonus_score: int = 0
    palace_environment_score: int = 0

    # 加权调整
    weighted_score: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palace_name": self.palace_name,
            "total_score": self.total_score,
            "strength_level": self.strength_level,
            "master_star_score": self.master_star_score,
            "auxiliary_star_score": self.auxiliary_star_score,
            "sha_star_deduction": self.sha_star_deduction,
            "transform_bonus_score": self.transform_bonus_score,
            "palace_environment_score": self.palace_environment_score,
            "weighted_score": self.weighted_score,
        }


@dataclass
class PalaceAnalysisResult:
    """单个宫位分析结果"""
    palace_name: str
    branch: str
    tiangan: str
    score: PalaceScore
    stars_in_palace: List[Dict[str, Any]]
    focal_point: str
    interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palace_name": self.palace_name,
            "branch": self.branch,
            "tiangan": self.tiangan,
            "score": self.score.to_dict() if self.score else None,
            "stars_in_palace": self.stars_in_palace,
            "focal_point": self.focal_point,
            "interpretation": self.interpretation,
        }


@dataclass
class PalaceAnalysis:
    """宫位分析结果"""
    palace_results: List[PalaceAnalysisResult] = field(default_factory=list)
    strongest_palace: str = ""
    weakest_palace: str = ""
    key_palaces: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palace_results": [r.to_dict() for r in self.palace_results],
            "strongest_palace": self.strongest_palace,
            "weakest_palace": self.weakest_palace,
            "key_palaces": self.key_palaces,
        }


@dataclass
class PalaceConnectionResult:
    """多宫位串联分析结果"""
    topic: str
    connected_palaces: List[str]
    palace_scores: Dict[str, int]
    strongest_in_chain: str
    weakest_in_chain: str
    overall_score: int
    connection_analysis: str
    detailed_interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "connected_palaces": self.connected_palaces,
            "palace_scores": self.palace_scores,
            "strongest_in_chain": self.strongest_in_chain,
            "weakest_in_chain": self.weakest_in_chain,
            "overall_score": self.overall_score,
            "connection_analysis": self.connection_analysis,
            "detailed_interpretation": self.detailed_interpretation,
        }


@dataclass
class MultiPalaceConnectionAnalysis:
    """多宫位串联分析汇总"""
    topic: str
    connection_result: PalaceConnectionResult
    chain_summary: str
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "connection_result": self.connection_result.to_dict(),
            "chain_summary": self.chain_summary,
            "recommendations": self.recommendations,
        }


@dataclass
class EmptyPalaceAnalysis:
    """空宫分析结果"""
    palace_name: str
    is_empty: bool
    opposite_palace: str
    opposite_stars: List[Dict[str, Any]]
    projection_strength: str  # 强/中/弱
    projection_analysis: str
    influence_description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palace_name": self.palace_name,
            "is_empty": self.is_empty,
            "opposite_palace": self.opposite_palace,
            "opposite_stars": self.opposite_stars,
            "projection_strength": self.projection_strength,
            "projection_analysis": self.projection_analysis,
            "influence_description": self.influence_description,
        }
