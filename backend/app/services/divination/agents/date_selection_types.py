"""
Date Selection Types - 择日分析数据类型

包含：
- DailyOption: 每日选项
- DateSelectionResult: 择日分析结果

注意：常量定义请使用 date_selection_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple


@dataclass
class DailyOption:
    """每日选项"""
    rank: int
    solar_date: str              # 阳历: "2026-09-15"
    lunar_date: str             # 农历: "八月初五"
    tiangan: str                 # 日柱天干: "甲子"
    dizhi: str                   # 日柱地支: "子"
    score: float                # 综合分数 0-100
    level: str                  # 等级
    is_auspicious: bool         # 是否为吉日
    suitable_for: List[str]      # 适合做的事
    avoid: List[str]             # 需要避免的事
    key_factors: List[str]       # 关键因素
    best_time_window: str        # 最佳时段: "上午9-11时"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rank": self.rank,
            "solar_date": self.solar_date,
            "lunar_date": self.lunar_date,
            "tiangan": self.tiangan,
            "dizhi": self.dizhi,
            "score": self.score,
            "level": self.level,
            "is_auspicious": self.is_auspicious,
            "suitable_for": self.suitable_for,
            "avoid": self.avoid,
            "key_factors": self.key_factors,
            "best_time_window": self.best_time_window,
            "warnings": self.warnings,
        }


@dataclass
class DateSelectionResult:
    """择日分析结果"""
    service_type: str = "date_selection"
    date_type: str = ""               # 吉日类型: "结婚嫁娶"
    target_palaces: List[str] = field(default_factory=list)   # 关联宫位
    daily_options: List[DailyOption] = field(default_factory=list)
    best_dates: List[DailyOption] = field(default_factory=list)  # Top 3
    analysis_summary: str = ""
    confidence: float = 0.0
    date_range: Tuple[str, str] = ("", "")  # (开始, 结束)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "service_type": self.service_type,
            "date_type": self.date_type,
            "target_palaces": self.target_palaces,
            "daily_options": [opt.to_dict() for opt in self.daily_options],
            "best_dates": [opt.to_dict() for opt in self.best_dates],
            "analysis_summary": self.analysis_summary,
            "confidence": self.confidence,
            "date_range": list(self.date_range),
        }
