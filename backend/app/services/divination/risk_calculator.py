"""
风险/机遇指数计算模块

根据命盘的四化数据和星曜信息计算：
- 风险指数 (0-100)
- 机遇指数 (0-100)

算法基于：
- 四化强度（化禄/化权/化科/化忌）
- 宫位星曜庙旺陷等级
- 格局吉凶判断
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


# ============ 强度系数配置 ============

# 四化强度系数
TRANSFORM_INTENSITY = {
    "化禄": 1.0,   # 化禄最强
    "化权": 0.9,   # 化权次强
    "化科": 0.7,   # 化科中等
    "化忌": -0.8,  # 化忌为负
}

# 化忌权重系数（凶，权重较高）
JI_WEIGHT = 1.2

# 化禄权重系数（吉，权重较高）
LU_WEIGHT = 1.0

# 化权权重系数
QUAN_WEIGHT = 0.8

# 化科权重系数
KE_WEIGHT = 0.6

# 星曜等级分数
STAR_LEVEL_SCORES = {
    "庙": 1.0,   # 最吉利
    "旺": 0.8,   # 次吉
    "平": 0.5,   # 中等
    "陷": 0.2,   # 凶
}

# 煞星列表（增加风险）
MALEFIC_STARS = ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]

# 吉利辅星列表（增加机遇）
LUCKY_STARS = ["左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马"]

# 格局权重
PATTERN_WEIGHTS = {
    "吉格": 15.0,
    "中格": 5.0,
    "凶格": -12.0,
}


@dataclass
class TransformInfo:
    """四化信息"""
    transform_type: str          # 化禄/化权/化科/化忌
    star: str                    # 四化星曜
    palace: str                  # 所在宫位
    intensity: float = 1.0       # 强度系数
    level: str = "平"            # 庙旺陷等级

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transform_type": self.transform_type,
            "star": self.star,
            "palace": self.palace,
            "intensity": self.intensity,
            "level": self.level
        }


@dataclass
class PatternInfo:
    """格局信息"""
    name: str                    # 格局名称
    pattern_type: str            # 吉格/中格/凶格
    palace: str                  # 所在宫位
    weight: float = 0.0          # 权重分数

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pattern_type": self.pattern_type,
            "palace": self.palace,
            "weight": self.weight
        }


@dataclass
class RiskMetrics:
    """风险指标"""
    risk_index: float                          # 风险指数 (0-100)
    hua_ji_count: int                          # 化忌数量
    hua_ji_total_intensity: float              # 化忌总强度
    xiong_ge_count: int                        # 凶格数量
    xiong_ge_total_weight: float               # 凶格总权重
    malefic_count: int                         # 煞星数量
    hua_ji_details: List[TransformInfo] = field(default_factory=list)
    xiong_ge_details: List[PatternInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_index": round(self.risk_index, 2),
            "hua_ji_count": self.hua_ji_count,
            "hua_ji_total_intensity": round(self.hua_ji_total_intensity, 2),
            "xiong_ge_count": self.xiong_ge_count,
            "xiong_ge_total_weight": round(self.xiong_ge_total_weight, 2),
            "malefic_count": self.malefic_count,
            "hua_ji_details": [t.to_dict() for t in self.hua_ji_details],
            "xiong_ge_details": [p.to_dict() for p in self.xiong_ge_details]
        }


@dataclass
class OpportunityMetrics:
    """机遇指标"""
    opportunity_index: float                  # 机遇指数 (0-100)
    hua_lu_count: int                         # 化禄数量
    hua_lu_total_intensity: float             # 化禄总强度
    hua_quan_count: int                        # 化权数量
    hua_ke_count: int                          # 化科数量
    ji_ge_count: int                           # 吉格数量
    ji_ge_total_weight: float                 # 吉格总权重
    lucky_star_count: int                     # 吉利辅星数量
    hua_lu_details: List[TransformInfo] = field(default_factory=list)
    hua_quan_details: List[TransformInfo] = field(default_factory=list)
    hua_ke_details: List[TransformInfo] = field(default_factory=list)
    ji_ge_details: List[PatternInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_index": round(self.opportunity_index, 2),
            "hua_lu_count": self.hua_lu_count,
            "hua_lu_total_intensity": round(self.hua_lu_total_intensity, 2),
            "hua_quan_count": self.hua_quan_count,
            "hua_ke_count": self.hua_ke_count,
            "ji_ge_count": self.ji_ge_count,
            "ji_ge_total_weight": round(self.ji_ge_total_weight, 2),
            "lucky_star_count": self.lucky_star_count,
            "hua_lu_details": [t.to_dict() for t in self.hua_lu_details],
            "hua_quan_details": [t.to_dict() for t in self.hua_quan_details],
            "hua_ke_details": [t.to_dict() for t in self.hua_ke_details],
            "ji_ge_details": [p.to_dict() for p in self.ji_ge_details]
        }


@dataclass
class RiskOpportunityMetrics:
    """风险与机遇综合指标"""
    risk: RiskMetrics
    opportunity: OpportunityMetrics
    risk_opportunity_ratio: float             # 风险机遇比 (风险/机遇)
    balance_level: str                        # 平衡等级

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk": self.risk.to_dict(),
            "opportunity": self.opportunity.to_dict(),
            "risk_opportunity_ratio": round(self.risk_opportunity_ratio, 2),
            "balance_level": self.balance_level
        }


class RiskCalculator:
    """
    风险指数计算器

    风险指数 = (忌数 × 忌强度) + Σ(凶格数 × 凶格强度) + Σ(煞星 × 煞星权重)

    四化强度系数:
    - 化忌: -0.8 (基础强度)
    - 星曜等级: 庙=1.0, 旺=0.8, 平=0.5, 陷=0.2
    """

    def __init__(self, palaces: Dict[str, Any], patterns: Optional[List[Dict]] = None):
        """
        初始化风险计算器

        Args:
            palaces: 宫位数据字典 {宫位名: {transforms: {...}, stars: [...], ...}}
            patterns: 格局列表 [{name, type, palace, ...}, ...]
        """
        self.palaces = palaces
        self.patterns = patterns or []

    def _get_star_level(self, palace_name: str, star_name: str) -> str:
        """获取星曜等级"""
        palace_data = self.palaces.get(palace_name, {})
        stars = palace_data.get("stars", [])

        for star in stars:
            if star.get("name") == star_name:
                return star.get("brightness", star.get("level", "平"))
        return "平"

    def _get_palace_transforms(self, palace_name: str) -> Dict[str, str]:
        """获取宫位的四化信息"""
        palace_data = self.palaces.get(palace_name, {})
        return palace_data.get("transforms", {})

    def _count_malefic_stars(self) -> int:
        """统计煞星数量"""
        count = 0
        for palace_data in self.palaces.values():
            malefic_stars = palace_data.get("malefic_stars", [])
            for star in malefic_stars:
                if star in MALEFIC_STARS:
                    count += 1
        return count

    def calculate_hua_ji_metrics(self) -> tuple[int, float, List[TransformInfo]]:
        """
        计算化忌指标

        Returns:
            (化忌数量, 化忌总强度, 化忌详情列表)
        """
        count = 0
        total_intensity = 0.0
        details = []

        for palace_name, palace_data in self.palaces.items():
            transforms = palace_data.get("transforms", {})
            if "化忌" in transforms:
                count += 1
                hua_ji_star = transforms["化忌"]
                level = self._get_star_level(palace_name, hua_ji_star)
                level_score = STAR_LEVEL_SCORES.get(level, 0.5)
                intensity = TRANSFORM_INTENSITY["化忌"] * level_score
                total_intensity += abs(intensity)

                details.append(TransformInfo(
                    transform_type="化忌",
                    star=hua_ji_star,
                    palace=palace_name,
                    intensity=intensity,
                    level=level
                ))

        return count, total_intensity, details

    def calculate_xiong_ge_metrics(self) -> tuple[int, float, List[PatternInfo]]:
        """
        计算凶格指标

        Returns:
            (凶格数量, 凶格总权重, 凶格详情列表)
        """
        count = 0
        total_weight = 0.0
        details = []

        for pattern in self.patterns:
            pattern_type = pattern.get("type", "中格")
            if pattern_type == "凶格":
                count += 1
                weight = PATTERN_WEIGHTS["凶格"]
                total_weight += abs(weight)

                details.append(PatternInfo(
                    name=pattern.get("name", ""),
                    pattern_type=pattern_type,
                    palace=pattern.get("palace", ""),
                    weight=weight
                ))

        return count, total_weight, details

    def calculate_risk_index(self) -> float:
        """
        计算风险指数

        RISK_INDEX = (忌数 × 忌强度) + Σ(凶格数 × 凶格强度) + Σ(煞星 × 煞星权重)

        Returns:
            风险指数 (0-100, 越高风险越大)
        """
        # 1. 化忌影响
        hua_ji_count, hua_ji_intensity, _ = self.calculate_hua_ji_metrics()
        hua_ji_risk = hua_ji_count * hua_ji_intensity * JI_WEIGHT * 10

        # 2. 凶格影响
        xiong_ge_count, xiong_ge_weight, _ = self.calculate_xiong_ge_metrics()
        xiong_ge_risk = xiong_ge_count * xiong_ge_weight

        # 3. 煞星影响
        malefic_count = self._count_malefic_stars()
        malefic_risk = malefic_count * 5

        # 计算总风险分
        risk_score = hua_ji_risk + xiong_ge_risk + malefic_risk

        # 归一化到 0-100
        return min(100, max(0, risk_score))

    def calculate_metrics(self) -> RiskMetrics:
        """
        计算完整的风险指标

        Returns:
            RiskMetrics 对象
        """
        hua_ji_count, hua_ji_intensity, hua_ji_details = self.calculate_hua_ji_metrics()
        xiong_ge_count, xiong_ge_weight, xiong_ge_details = self.calculate_xiong_ge_metrics()
        malefic_count = self._count_malefic_stars()

        risk_index = self.calculate_risk_index()

        return RiskMetrics(
            risk_index=risk_index,
            hua_ji_count=hua_ji_count,
            hua_ji_total_intensity=hua_ji_intensity,
            xiong_ge_count=xiong_ge_count,
            xiong_ge_total_weight=xiong_ge_weight,
            malefic_count=malefic_count,
            hua_ji_details=hua_ji_details,
            xiong_ge_details=xiong_ge_details
        )


class OpportunityCalculator:
    """
    机遇指数计算器

    机遇指数 = (禄数 × 禄强度) + Σ(吉格数 × 吉格强度) + Σ(化权 × 化权权重) + Σ(化科 × 化科权重) + Σ(吉利辅星)

    四化强度系数:
    - 化禄: 1.0 (最强)
    - 化权: 0.9 (次强)
    - 化科: 0.7 (中等)
    - 星曜等级: 庙=1.0, 旺=0.8, 平=0.5, 陷=0.2
    """

    def __init__(self, palaces: Dict[str, Any], patterns: Optional[List[Dict]] = None):
        """
        初始化机遇计算器

        Args:
            palaces: 宫位数据字典 {宫位名: {transforms: {...}, stars: [...], ...}}
            patterns: 格局列表 [{name, type, palace, ...}, ...]
        """
        self.palaces = palaces
        self.patterns = patterns or []

    def _get_star_level(self, palace_name: str, star_name: str) -> str:
        """获取星曜等级"""
        palace_data = self.palaces.get(palace_name, {})
        stars = palace_data.get("stars", [])

        for star in stars:
            if star.get("name") == star_name:
                return star.get("brightness", star.get("level", "平"))
        return "平"

    def _get_palace_transforms(self, palace_name: str) -> Dict[str, str]:
        """获取宫位的四化信息"""
        palace_data = self.palaces.get(palace_name, {})
        return palace_data.get("transforms", {})

    def _count_lucky_stars(self) -> int:
        """统计吉利辅星数量"""
        count = 0
        for palace_data in self.palaces.values():
            auxiliary_stars = palace_data.get("auxiliary_stars", [])
            for star in auxiliary_stars:
                if star in LUCKY_STARS:
                    count += 1
        return count

    def calculate_hua_lu_metrics(self) -> tuple[int, float, List[TransformInfo]]:
        """
        计算化禄指标

        Returns:
            (化禄数量, 化禄总强度, 化禄详情列表)
        """
        count = 0
        total_intensity = 0.0
        details = []

        for palace_name, palace_data in self.palaces.items():
            transforms = palace_data.get("transforms", {})
            if "化禄" in transforms:
                count += 1
                hua_lu_star = transforms["化禄"]
                level = self._get_star_level(palace_name, hua_lu_star)
                level_score = STAR_LEVEL_SCORES.get(level, 0.5)
                intensity = TRANSFORM_INTENSITY["化禄"] * level_score
                total_intensity += intensity

                details.append(TransformInfo(
                    transform_type="化禄",
                    star=hua_lu_star,
                    palace=palace_name,
                    intensity=intensity,
                    level=level
                ))

        return count, total_intensity, details

    def calculate_hua_quan_metrics(self) -> tuple[int, List[TransformInfo]]:
        """
        计算化权指标

        Returns:
            (化权数量, 化权详情列表)
        """
        count = 0
        details = []

        for palace_name, palace_data in self.palaces.items():
            transforms = palace_data.get("transforms", {})
            if "化权" in transforms:
                count += 1
                hua_quan_star = transforms["化权"]
                level = self._get_star_level(palace_name, hua_quan_star)

                details.append(TransformInfo(
                    transform_type="化权",
                    star=hua_quan_star,
                    palace=palace_name,
                    intensity=TRANSFORM_INTENSITY["化权"],
                    level=level
                ))

        return count, details

    def calculate_hua_ke_metrics(self) -> tuple[int, List[TransformInfo]]:
        """
        计算化科指标

        Returns:
            (化科数量, 化科详情列表)
        """
        count = 0
        details = []

        for palace_name, palace_data in self.palaces.items():
            transforms = palace_data.get("transforms", {})
            if "化科" in transforms:
                count += 1
                hua_ke_star = transforms["化科"]
                level = self._get_star_level(palace_name, hua_ke_star)

                details.append(TransformInfo(
                    transform_type="化科",
                    star=hua_ke_star,
                    palace=palace_name,
                    intensity=TRANSFORM_INTENSITY["化科"],
                    level=level
                ))

        return count, details

    def calculate_ji_ge_metrics(self) -> tuple[int, float, List[PatternInfo]]:
        """
        计算吉格指标

        Returns:
            (吉格数量, 吉格总权重, 吉格详情列表)
        """
        count = 0
        total_weight = 0.0
        details = []

        for pattern in self.patterns:
            pattern_type = pattern.get("type", "中格")
            if pattern_type == "吉格":
                count += 1
                weight = PATTERN_WEIGHTS["吉格"]
                total_weight += weight

                details.append(PatternInfo(
                    name=pattern.get("name", ""),
                    pattern_type=pattern_type,
                    palace=pattern.get("palace", ""),
                    weight=weight
                ))

        return count, total_weight, details

    def calculate_opportunity_index(self) -> float:
        """
        计算机遇指数

        OPPORTUNITY_INDEX = (禄数 × 禄强度) + Σ(化权 × 化权权重) + Σ(化科 × 化科权重) + Σ(吉格数 × 吉格强度)

        Returns:
            机遇指数 (0-100, 越高机遇越大)
        """
        # 1. 化禄影响
        hua_lu_count, hua_lu_intensity, _ = self.calculate_hua_lu_metrics()
        hua_lu_opportunity = hua_lu_count * hua_lu_intensity * LU_WEIGHT * 10

        # 2. 化权影响
        hua_quan_count, _ = self.calculate_hua_quan_metrics()
        hua_quan_opportunity = hua_quan_count * QUAN_WEIGHT * 8

        # 3. 化科影响
        hua_ke_count, _ = self.calculate_hua_ke_metrics()
        hua_ke_opportunity = hua_ke_count * KE_WEIGHT * 5

        # 4. 吉格影响
        ji_ge_count, ji_ge_weight, _ = self.calculate_ji_ge_metrics()
        ji_ge_opportunity = ji_ge_count * ji_ge_weight

        # 5. 吉利辅星影响
        lucky_star_count = self._count_lucky_stars()
        lucky_opportunity = lucky_star_count * 3

        # 计算总机遇分
        opportunity_score = (
            hua_lu_opportunity +
            hua_quan_opportunity +
            hua_ke_opportunity +
            ji_ge_opportunity +
            lucky_opportunity
        )

        # 归一化到 0-100
        return min(100, max(0, opportunity_score))

    def calculate_metrics(self) -> OpportunityMetrics:
        """
        计算完整的机遇指标

        Returns:
            OpportunityMetrics 对象
        """
        hua_lu_count, hua_lu_intensity, hua_lu_details = self.calculate_hua_lu_metrics()
        hua_quan_count, hua_quan_details = self.calculate_hua_quan_metrics()
        hua_ke_count, hua_ke_details = self.calculate_hua_ke_metrics()
        ji_ge_count, ji_ge_weight, ji_ge_details = self.calculate_ji_ge_metrics()
        lucky_star_count = self._count_lucky_stars()

        opportunity_index = self.calculate_opportunity_index()

        return OpportunityMetrics(
            opportunity_index=opportunity_index,
            hua_lu_count=hua_lu_count,
            hua_lu_total_intensity=hua_lu_intensity,
            hua_quan_count=hua_quan_count,
            hua_ke_count=hua_ke_count,
            ji_ge_count=ji_ge_count,
            ji_ge_total_weight=ji_ge_weight,
            lucky_star_count=lucky_star_count,
            hua_lu_details=hua_lu_details,
            hua_quan_details=hua_quan_details,
            hua_ke_details=hua_ke_details,
            ji_ge_details=ji_ge_details
        )


class RiskOpportunityCalculator:
    """
    风险与机遇综合计算器

    同时计算风险指数和机遇指数，并输出综合指标
    """

    def __init__(
        self,
        palaces: Dict[str, Any],
        patterns: Optional[List[Dict]] = None
    ):
        """
        初始化综合计算器

        Args:
            palaces: 宫位数据字典
            patterns: 格局列表
        """
        self.palaces = palaces
        self.patterns = patterns or []
        self.risk_calculator = RiskCalculator(palaces, patterns)
        self.opportunity_calculator = OpportunityCalculator(palaces, patterns)

    def calculate(self) -> RiskOpportunityMetrics:
        """
        计算完整的风险与机遇指标

        Returns:
            RiskOpportunityMetrics 对象
        """
        risk_metrics = self.risk_calculator.calculate_metrics()
        opportunity_metrics = self.opportunity_calculator.calculate_metrics()

        # 计算风险机遇比
        if opportunity_metrics.opportunity_index > 0:
            ratio = risk_metrics.risk_index / opportunity_metrics.opportunity_index
        else:
            ratio = risk_metrics.risk_index  # 机遇为0时，比值等于风险

        # 判断平衡等级
        balance_level = self._get_balance_level(
            risk_metrics.risk_index,
            opportunity_metrics.opportunity_index
        )

        return RiskOpportunityMetrics(
            risk=risk_metrics,
            opportunity=opportunity_metrics,
            risk_opportunity_ratio=ratio,
            balance_level=balance_level
        )

    def _get_balance_level(self, risk_index: float, opportunity_index: float) -> str:
        """
        判断风险与机遇的平衡等级

        Args:
            risk_index: 风险指数
            opportunity_index: 机遇指数

        Returns:
            平衡等级描述
        """
        if opportunity_index >= 70 and risk_index <= 30:
            return "极佳平衡"
        elif opportunity_index >= 50 and risk_index <= 40:
            return "良好平衡"
        elif opportunity_index >= 30 and risk_index <= 50:
            return "一般平衡"
        elif opportunity_index < 30 and risk_index > 50:
            return "高风险低机遇"
        elif opportunity_index > 50 and risk_index > 50:
            return "高风险高机遇"
        elif opportunity_index < 30 and risk_index <= 30:
            return "低风险低机遇"
        else:
            return "待观察"


def calculate_risk_opportunity(
    palaces: Dict[str, Any],
    patterns: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    便捷函数：计算风险与机遇指数

    Args:
        palaces: 宫位数据字典
        patterns: 格局列表

    Returns:
        风险与机遇计算结果字典
    """
    calculator = RiskOpportunityCalculator(palaces, patterns)
    result = calculator.calculate()
    return result.to_dict()


def calculate_risk(
    palaces: Dict[str, Any],
    patterns: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    便捷函数：计算风险指数

    Args:
        palaces: 宫位数据字典
        patterns: 格局列表

    Returns:
        风险计算结果字典
    """
    calculator = RiskCalculator(palaces, patterns)
    result = calculator.calculate_metrics()
    return result.to_dict()


def calculate_opportunity(
    palaces: Dict[str, Any],
    patterns: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    便捷函数：计算机遇指数

    Args:
        palaces: 宫位数据字典
        patterns: 格局列表

    Returns:
        机遇计算结果字典
    """
    calculator = OpportunityCalculator(palaces, patterns)
    result = calculator.calculate_metrics()
    return result.to_dict()
