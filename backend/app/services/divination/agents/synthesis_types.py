"""
Synthesis Types - 综合分析数据类型

包含：
- AnalysisPriority: 分析优先级枚举
- AgentResult: 各agent的分析结果
- StarAnalysis: 星曜分析结果（简化版）
- PalaceAnalysis: 宫位分析结果（简化版）
- PatternAnalysis: 格局分析结果
- TransformAnalysis: 四化分析结果
- TimingAnalysis: 时机分析结果（简化版）
- SynthesisReport: 综合报告

注意：常量定义请使用 synthesis_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class AnalysisPriority(str, Enum):
    """分析优先级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class AgentResult:
    """各agent的分析结果"""
    agent_name: str          # agent名称
    content: str            # 分析内容
    priority: AnalysisPriority = AnalysisPriority.MEDIUM
    confidence: float = 0.8  # 置信度 0-1
    conflicts_with: List[str] = field(default_factory=list)  # 与哪些agent有冲突

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "content": self.content,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "conflicts_with": self.conflicts_with,
        }


@dataclass
class StarAnalysis:
    """星曜分析结果（简化版）"""
    main_stars: List[str] = field(default_factory=list)           # 主星
    assistant_stars: List[str] = field(default_factory=list)       # 辅星
    marginal_stars: List[str] = field(default_factory=list)        # 杂曜
    transforming_stars: List[str] = field(default_factory=list)   # 四化星
    key_observations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "main_stars": self.main_stars,
            "assistant_stars": self.assistant_stars,
            "marginal_stars": self.marginal_stars,
            "transforming_stars": self.transforming_stars,
            "key_observations": self.key_observations,
            "summary": self.summary,
        }


@dataclass
class PalaceAnalysis:
    """宫位分析结果（简化版）"""
    palace_strengths: Dict[str, float] = field(default_factory=dict)  # 宫位强弱
    key_palaces: Dict[str, str] = field(default_factory=dict)  # 关键宫位
    observations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palace_strengths": self.palace_strengths,
            "key_palaces": self.key_palaces,
            "observations": self.observations,
            "summary": self.summary,
        }


@dataclass
class PatternAnalysis:
    """格局分析结果"""
    major_patterns: List[str] = field(default_factory=list)
    minor_patterns: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "major_patterns": self.major_patterns,
            "minor_patterns": self.minor_patterns,
            "observations": self.observations,
            "summary": self.summary,
        }


@dataclass
class TransformAnalysis:
    """四化分析结果"""
    original_transforms: Dict[str, str] = field(default_factory=dict)  # 原局四化
    current_transforms: Dict[str, str] = field(default_factory=dict)  # 运限四化
    observations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_transforms": self.original_transforms,
            "current_transforms": self.current_transforms,
            "observations": self.observations,
            "summary": self.summary,
        }


@dataclass
class TimingAnalysis:
    """时机分析结果（简化版）"""
    current_period: str = ""
    year_fate: str = ""
    key_timing: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_period": self.current_period,
            "year_fate": self.year_fate,
            "key_timing": self.key_timing,
            "observations": self.observations,
            "summary": self.summary,
        }


@dataclass
class SynthesisReport:
    """综合报告"""
    # 基础信息
    chart_overview: str = ""
    birth_info: Dict[str, Any] = field(default_factory=dict)

    # 各维度分析
    star_analysis: StarAnalysis = field(default_factory=lambda: StarAnalysis())
    palace_analysis: PalaceAnalysis = field(default_factory=lambda: PalaceAnalysis())
    pattern_analysis: PatternAnalysis = field(default_factory=lambda: PatternAnalysis())
    transform_analysis: TransformAnalysis = field(default_factory=lambda: TransformAnalysis())
    timing_analysis: TimingAnalysis = field(default_factory=lambda: TimingAnalysis())

    # 综合结论
    overall_assessment: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # 冲突解决
    conflict_resolutions: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chart_overview": self.chart_overview,
            "birth_info": self.birth_info,
            "star_analysis": self.star_analysis.to_dict(),
            "palace_analysis": self.palace_analysis.to_dict(),
            "pattern_analysis": self.pattern_analysis.to_dict(),
            "transform_analysis": self.transform_analysis.to_dict(),
            "timing_analysis": self.timing_analysis.to_dict(),
            "overall_assessment": self.overall_assessment,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "conflict_resolutions": self.conflict_resolutions
        }
