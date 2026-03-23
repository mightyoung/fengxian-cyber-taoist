"""
Timing Types - 运限时间分析数据类型

包含：
- MajorFate: 大限数据类
- YearFate: 流年数据类
- MonthFate: 流月数据类
- DayFate: 流日数据类
- HourFate: 流时数据类
- TimingAnalysis: 时间分析结果
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class FateLevel(str, Enum):
    """运限级别"""
    MAJOR_FATE = "大限"      # 10年大运
    YEAR_FATE = "流年"       # 一年
    MONTH_FATE = "流月"      # 一月
    DAY_FATE = "流日"        # 一日
    HOUR_FATE = "流时"       # 一时辰(2小时)


class LiuYaoCategory(str, Enum):
    """流曜类别"""
    BOSHISHI_SHEN = "博士十二神"
    JIANGSHIQIAN_SHEN = "将前十神"
    SUIQIAN_SHIER_SHEN = "岁前十二神"
    FUZHU_SHAHUA = "辅佐煞化流曜"


class CycleStage(Enum):
    """成住坏空阶段"""
    FORMATION = "成"    # 形成期
    STABLE = "住"      # 稳定期
    DECAY = "坏"       # 衰败期
    EMPTY = "空"       # 空亡期


@dataclass
class MajorFate:
    """大限数据"""
    start_age: int
    end_age: int
    hub_palace: str           # 枢纽宫
    hub_star: str             # 枢纽星
    star_system: str           # 星曜系统
    main_transform: str       # 主导四化
    description: str          # 描述
    keywords: List[str] = field(default_factory=list)


@dataclass
class YearFate:
    """流年数据"""
    year: int
    zodiac: str               # 地支
    gan_zhi: str              # 干支
    tai_sui_palace: str       # 太岁落宫
    tai_sui_relationship: str # 太岁关系
    stars: List[str] = field(default_factory=list)       # 星曜
    liu_yao: Dict[str, str] = field(default_factory=dict)  # 流曜
    description: str = ""


@dataclass
class MonthFate:
    """流月数据"""
    month: int
    zodiac: str
    gan_zhi: str
    tai_sui_palace: str
    stars: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class DayFate:
    """流日数据"""
    day: int
    zodiac: str
    gan_zhi: str
    tai_sui_palace: str
    stars: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class HourFate:
    """流时数据"""
    hour: int
    zodiac: str
    gan_zhi: str
    tai_sui_palace: str
    stars: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class TimingAnalysis:
    """时间分析结果"""
    major_fates: List[MajorFate]                    # 所有大限
    current_major_fate: Optional[MajorFate]          # 当前大限
    year_fates: List[YearFate]                      # 流年列表
    current_year_fate: Optional[YearFate]           # 当前流年
    timing_triggers: List[Dict[str, Any]] = field(default_factory=list)  # 触发因素
    hub_palace_analysis: Dict[str, Any] = field(default_factory=dict)     # 枢纽宫分析
    recommendations: List[str] = field(default_factory=list)               # 建议
    major_fate_table: List[Dict[str, Any]] = field(default_factory=list) # 大限表格
    year_predictions: List[Dict[str, Any]] = field(default_factory=list) # 流年预测
    time_anchors: Dict[str, Any] = field(default_factory=dict)          # 时间锚点

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "major_fates": [
                {
                    "start_age": mf.start_age,
                    "end_age": mf.end_age,
                    "hub_palace": mf.hub_palace,
                    "hub_star": mf.hub_star,
                    "star_system": mf.star_system,
                    "main_transform": mf.main_transform,
                    "description": mf.description,
                    "keywords": mf.keywords
                } for mf in self.major_fates
            ],
            "current_major_fate": {
                "start_age": self.current_major_fate.start_age,
                "end_age": self.current_major_fate.end_age,
                "hub_palace": self.current_major_fate.hub_palace,
                "hub_star": self.current_major_fate.hub_star,
            } if self.current_major_fate else None,
            "year_fates": [
                {
                    "year": yf.year,
                    "zodiac": yf.zodiac,
                    "gan_zhi": yf.gan_zhi,
                    "tai_sui_palace": yf.tai_sui_palace,
                    "tai_sui_relationship": yf.tai_sui_relationship,
                    "stars": yf.stars,
                    "liu_yao": yf.liu_yao,
                    "description": yf.description
                } for yf in self.year_fates
            ],
            "current_year_fate": {
                "year": self.current_year_fate.year,
                "zodiac": self.current_year_fate.zodiac,
                "tai_sui_palace": self.current_year_fate.tai_sui_palace,
            } if self.current_year_fate else None,
            "timing_triggers": self.timing_triggers,
            "hub_palace_analysis": self.hub_palace_analysis,
            "recommendations": self.recommendations,
            "major_fate_table": self.major_fate_table,
            "year_predictions": self.year_predictions,
            "time_anchors": self.time_anchors
        }
