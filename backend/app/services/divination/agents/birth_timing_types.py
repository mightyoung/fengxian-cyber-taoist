"""
Birth Timing Types - 剖腹产良辰吉日数据类型

包含：
- BirthTimingOption: 时辰选项
- BirthTimingResult: 剖腹产分析结果

注意：常量定义请使用 birth_timing_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class BirthTimingOption:
    """时辰选项"""
    rank: int
    date: str                    # 格式: "2026-09-15"
    lunar_date: str              # 格式: "农历八月初五"
    hour: str                    # 格式: "午时" 或 "11:00-13:00"
    chart_summary: Dict[str, Any]  # 命盘摘要
    score: float                # 综合分数 0-100
    level: str                  # 等级: 极佳/良好/中等/一般/较差
    strengths: List[str]        # 优势列表
    weaknesses: List[str]        # 劣势列表
    reasons: List[str]          # 推荐理由
    warnings: List[str]         # 注意事项

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "rank": self.rank,
            "date": self.date,
            "lunar_date": self.lunar_date,
            "hour": self.hour,
            "chart_summary": self.chart_summary,
            "score": round(self.score, 2),
            "level": self.level,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "reasons": self.reasons,
            "warnings": self.warnings,
        }


@dataclass
class BirthTimingResult:
    """剖腹产分析结果"""
    service_type: str = "birth_timing"
    mother_chart: Dict[str, Any] = field(default_factory=dict)  # 母亲命盘
    father_chart: Dict[str, Any] = field(default_factory=dict)   # 父亲命盘
    options: List[BirthTimingOption] = field(default_factory=list)
    best_option: Optional[BirthTimingOption] = None
    analysis_summary: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "service_type": self.service_type,
            "mother_chart": self.mother_chart,
            "father_chart": self.father_chart,
            "options": [opt.to_dict() for opt in self.options],
            "best_option": self.best_option.to_dict() if self.best_option else None,
            "analysis_summary": self.analysis_summary,
            "confidence": round(self.confidence, 2),
        }
