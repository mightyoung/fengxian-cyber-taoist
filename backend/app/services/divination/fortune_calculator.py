"""
运势分数计算模块

根据命盘数据计算各维度运势分数，包括：
- 事业、财运、感情、健康、人际五个维度
- 月度运势趋势

评分算法基于：
- 四化星曜强度（化禄/化权/化科/化忌）
- 宫位星曜庙旺陷等级
- 格局吉凶判断
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============ 维度权重配置 ============
DIMENSION_WEIGHTS = {
    "career": 0.25,       # 事业
    "wealth": 0.25,       # 财运
    "relationship": 0.20,  # 感情
    "health": 0.15,       # 健康
    "social": 0.15,       # 人际
}

# 维度与宫位索引映射 (基于十二宫顺序)
# 0-命宫, 1-兄弟, 2-夫妻, 3-子女, 4-财帛, 5-疾厄, 6-迁移, 7-交友, 8-事业, 9-田宅, 10-福得, 11-父母
DIMENSION_PALACE_INDEX = {
    "career": 8,          # 事业 → 官禄宫
    "wealth": 4,          # 财运 → 财帛宫
    "relationship": 2,     # 感情 → 夫妻宫
    "health": 5,          # 健康 → 疾厄宫
    "social": 7,          # 人际 → 交友宫
}

# 中文宫位名称映射
PALACE_INDEX_TO_NAME = {
    0: "命宫", 1: "兄弟宫", 2: "夫妻宫", 3: "子女宫",
    4: "财帛宫", 5: "疾厄宫", 6: "迁移宫", 7: "交友宫",
    8: "官禄宫", 9: "田宅宫", 10: "福德宫", 11: "父母宫"
}

# 维度与宫位名称映射
DIMENSION_PALACE_MAPPING = {
    "career": "官禄宫",       # 事业
    "wealth": "财帛宫",       # 财运
    "relationship": "夫妻宫",  # 感情
    "health": "疾厄宫",       # 健康
    "social": "交友宫",       # 人际
}

# 星曜等级分数
STAR_LEVEL_SCORES = {
    "庙": 1.0,   # 最吉利
    "旺": 0.8,   # 次吉
    "平": 0.5,   # 中等
    "陷": 0.2,   # 凶
}

# 四化强度系数
TRANSFORM_INTENSITY = {
    "化禄": 1.0,   # 化禄最强
    "化权": 0.9,   # 化权次强
    "化科": 0.7,   # 化科中等
    "化忌": -0.8,  # 化忌为负
}

# 主星基础分
MAIN_STAR_BASE_SCORE = {
    # 北斗
    "紫微": 0.9,
    "天机": 0.75,
    "太阳": 0.8,
    "武曲": 0.85,
    "天同": 0.7,
    "廉贞": 0.8,
    # 南斗
    "天府": 0.9,
    "太阴": 0.8,
    "贪狼": 0.85,
    "巨门": 0.7,
    "天相": 0.8,
    "天梁": 0.8,
    # 中天
    "七杀": 0.85,
    "破军": 0.8,
}

# 辅星吉凶
AUXILIARY_STAR_JUDGMENT = {
    # 吉利辅星
    "左辅": 0.6, "右弼": 0.6,
    "文昌": 0.5, "文曲": 0.5,
    "天魁": 0.7, "天钺": 0.7,
    "禄存": 0.8, "天马": 0.6,
    # 煞星
    "擎羊": -0.5, "陀罗": -0.4,
    "火星": -0.5, "铃星": -0.4,
    "地空": -0.4, "地劫": -0.5,
}

# 格局分数
PATTERN_SCORES = {
    "吉格": 1.0,
    "中格": 0.5,
    "凶格": -0.5,
}


class FortuneLevel(Enum):
    """运势等级"""
    EXCELLENT = "极佳"     # 85-100
    GOOD = "良好"          # 70-84
    AVERAGE = "中等"       # 50-69
    FAIR = "一般"          # 30-49
    POOR = "较差"          # 0-29


@dataclass
class DimensionScore:
    """维度分数"""
    dimension: str
    score: float
    level: str
    factors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "score": round(self.score, 2),
            "level": self.level,
            "factors": self.factors
        }


@dataclass
class FortuneScore:
    """
    运势分数对象

    包含总分数和各维度分数
    """
    overall_score: float
    overall_level: str
    career_score: float
    wealth_score: float
    relationship_score: float
    health_score: float
    social_score: float
    dimension_scores: Dict[str, DimensionScore] = field(default_factory=dict)
    monthly_scores: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "overall_score": round(self.overall_score, 2),
            "overall_level": self.overall_level,
            "dimensions": {
                "career": {"score": round(self.career_score, 2)},
                "wealth": {"score": round(self.wealth_score, 2)},
                "relationship": {"score": round(self.relationship_score, 2)},
                "health": {"score": round(self.health_score, 2)},
                "social": {"score": round(self.social_score, 2)},
            },
            "dimension_details": {
                k: v.to_dict() for k, v in self.dimension_scores.items()
            },
            "monthly_scores": self.monthly_scores
        }


@dataclass
class FortuneResult:
    """运势计算结果（兼容旧版）"""
    overall_score: float
    overall_level: str
    dimension_scores: Dict[str, DimensionScore]
    risk_index: float
    opportunity_index: float
    monthly_scores: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 2),
            "overall_level": self.overall_level,
            "dimension_scores": {
                k: v.to_dict() for k, v in self.dimension_scores.items()
            },
            "risk_index": round(self.risk_index, 2),
            "opportunity_index": round(self.opportunity_index, 2),
            "monthly_scores": self.monthly_scores
        }


class FortuneCalculator:
    """
    运势分数计算器

    根据命盘数据计算综合运势分数和各维度分数

    支持两种输入格式：
    1. gong_wei_12 + ming_gong 格式（推荐）
    2. palaces 字典格式（兼容旧版）
    """

    def __init__(
        self,
        chart: Optional[Dict[str, Any]] = None,
        target_year: int = 2026,
        gong_wei_12: Optional[List[Dict[str, Any]]] = None,
        ming_gong: Optional[Dict[str, Any]] = None
    ):
        """
        初始化运势计算器

        Args:
            chart: 命盘数据字典（推荐使用）
            target_year: 目标预测年份
            gong_wei_12: 十二宫数据列表（备用格式）
            ming_gong: 命宫数据（备用格式）
        """
        self.target_year = target_year

        # 优先使用 chart 参数
        if chart is not None:
            self.chart = chart
            self.gong_wei_12 = self._convert_chart_to_gongwei12(chart)
            self.ming_gong = chart.get("ming_gong", {})
            self.palaces = chart.get("palaces", {})
        elif gong_wei_12 is not None:
            # 备用格式
            self.gong_wei_12 = gong_wei_12
            self.ming_gong = ming_gong or {}
            self.chart = {}
            self.palaces = {}
        else:
            raise ValueError("必须提供 chart 或 gong_wei_12 参数")

        self.transforms = self.chart.get("transforms", {}) if self.chart else {}
        self.patterns = self.chart.get("patterns", []) if self.chart else []

    def _convert_chart_to_gongwei12(self, chart: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将旧格式 chart 转换为 gong_wei_12 格式"""
        palaces = chart.get("palaces", {})
        gong_wei_12 = []

        for idx, name in PALACE_INDEX_TO_NAME.items():
            palace_data = palaces.get(name, {})
            gong_wei_12.append({
                "index": idx,
                "name": name,
                **palace_data
            })

        return gong_wei_12

    def _get_palace_by_index(self, index: int) -> Dict[str, Any]:
        """根据索引获取宫位数据"""
        if self.gong_wei_12 and 0 <= index < len(self.gong_wei_12):
            return self.gong_wei_12[index]
        return {}

    def calculate_dimension_scores(self) -> Dict[str, DimensionScore]:
        """
        计算各维度分数

        Returns:
            各维度分数字典
        """
        dimension_scores = {}

        for dim_key, palace_idx in DIMENSION_PALACE_INDEX.items():
            # 获取对应宫位数据
            palace_data = self._get_palace_by_index(palace_idx)
            score, factors = self._calculate_palace_score(palace_data, dim_key)
            level = self._score_to_level(score)

            dimension_scores[dim_key] = DimensionScore(
                dimension=dim_key,
                score=score,
                level=level,
                factors=factors
            )

        return dimension_scores

    def _calculate_palace_score(
        self,
        palace_data: Dict[str, Any],
        dimension: str
    ) -> tuple[float, List[Dict[str, Any]]]:
        """
        计算单个宫位的分数

        Args:
            palace_data: 宫位数据
            dimension: 维度名称

        Returns:
            (分数, 影响因素列表)
        """
        factors = []
        total_score = 0.0
        weight_sum = 0.0

        # 1. 主星分数 - 支持多种字段名
        main_star = palace_data.get("main_star", palace_data.get("zhu_star", ""))
        if main_star:
            main_star_score = MAIN_STAR_BASE_SCORE.get(main_star, 0.5)
            stars = palace_data.get("stars", palace_data.get("star_list", []))
            level = self._get_star_level(stars, main_star)
            level_modifier = STAR_LEVEL_SCORES.get(level, 0.5)
            score = main_star_score * level_modifier
            total_score += score * 0.5  # 主星权重50%
            weight_sum += 0.5
            factors.append({
                "type": "main_star",
                "name": main_star,
                "score": round(score, 2),
                "level": level
            })

        # 2. 四化影响 - 支持多种字段名
        transforms = palace_data.get("transforms", palace_data.get("si_hua", {}))
        for transform_type, star_name in transforms.items():
            if transform_type in TRANSFORM_INTENSITY:
                intensity = TRANSFORM_INTENSITY[transform_type]
                factor_score = intensity * 0.3  # 四化权重30%
                total_score += factor_score
                weight_sum += 0.3 * (1 if intensity > 0 else 0.5)  # 化忌权重减半
                factors.append({
                    "type": "transform",
                    "transform": transform_type,
                    "star": star_name,
                    "score": round(factor_score, 2)
                })

        # 3. 辅星影响
        auxiliary_stars = palace_data.get("auxiliary_stars", palace_data.get("fu_xing", []))
        if isinstance(auxiliary_stars, list):
            for star in auxiliary_stars:
                if isinstance(star, str):
                    star_judgment = AUXILIARY_STAR_JUDGMENT.get(star, 0)
                    star_name = star
                else:
                    star_judgment = AUXILIARY_STAR_JUDGMENT.get(star.get("name", ""), 0)
                    star_name = star.get("name", "")
                total_score += star_judgment * 0.1
                weight_sum += 0.1
                if star_judgment != 0:
                    factors.append({
                        "type": "auxiliary",
                        "name": star_name,
                        "score": round(star_judgment * 0.1, 2)
                    })

        # 4. 煞星影响
        malefic_stars = palace_data.get("malefic_stars", palace_data.get("sha_xing", []))
        if isinstance(malefic_stars, list):
            for star in malefic_stars:
                if isinstance(star, str):
                    star_judgment = AUXILIARY_STAR_JUDGMENT.get(star, -0.3)
                    star_name = star
                else:
                    star_judgment = AUXILIARY_STAR_JUDGMENT.get(star.get("name", ""), -0.3)
                    star_name = star.get("name", "")
                total_score += star_judgment * 0.1
                weight_sum += 0.1
                factors.append({
                    "type": "malefic",
                    "name": star_name,
                    "score": round(star_judgment * 0.1, 2)
                })

        # 5. 格局加成
        palace_patterns = self._get_palace_patterns(dimension)
        for pattern in palace_patterns:
            pattern_type = pattern.get("type", "中格")
            pattern_score = PATTERN_SCORES.get(pattern_type, 0.5) * 0.1
            total_score += pattern_score
            weight_sum += 0.1
            factors.append({
                "type": "pattern",
                "name": pattern.get("name", ""),
                "pattern_type": pattern_type,
                "score": round(pattern_score, 2)
            })

        # 归一化分数到0-100
        if weight_sum > 0:
            normalized_score = (total_score / weight_sum) * 50 + 50
        else:
            normalized_score = 50.0

        # 限制在0-100范围
        normalized_score = max(0, min(100, normalized_score))

        return normalized_score, factors

    def _get_star_level(self, stars: List[Dict], target_star: str) -> str:
        """获取星曜等级"""
        for star in stars:
            if star.get("name") == target_star:
                return star.get("brightness", star.get("level", "平"))
        return "平"

    def _get_palace_patterns(self, dimension: str) -> List[Dict]:
        """获取与维度相关的格局"""
        palace_idx = DIMENSION_PALACE_INDEX.get(dimension, -1)
        palace_name = PALACE_INDEX_TO_NAME.get(palace_idx, "")
        related_patterns = []

        for pattern in self.patterns:
            if pattern.get("palace") == palace_name or pattern.get("palace_index") == palace_idx:
                related_patterns.append(pattern)

        return related_patterns

    def calculate_fortune_score(self) -> float:
        """
        计算综合运势分数

        FORTUNE_SCORE = Σ(维度分数 × 权重) / Σ权重

        Returns:
            综合运势分数 (0-100)
        """
        dimension_scores = self.calculate_dimension_scores()

        weighted_sum = 0.0
        weight_sum = 0.0

        for dim_key, weight in DIMENSION_WEIGHTS.items():
            score = dimension_scores[dim_key].score
            weighted_sum += score * weight
            weight_sum += weight

        if weight_sum > 0:
            return weighted_sum / weight_sum

        return 50.0

    def calculate_risk_index(self) -> float:
        """
        计算风险指数

        RISK_INDEX = (化忌数 × 化忌强度) + Σ(凶格数 × 凶格强度)

        Returns:
            风险指数 (0-100, 越高风险越大)
        """
        risk_score = 0.0

        # 1. 化忌影响
        hua_ji_count = 0
        hua_ji_intensity = 0.0
        for palace in self.gong_wei_12:
            transforms = palace.get("transforms", palace.get("si_hua", {}))
            if "化忌" in transforms:
                hua_ji_count += 1
                stars = palace.get("stars", [])
                hua_ji_star = transforms["化忌"]
                level = self._get_star_level(stars, hua_ji_star)
                hua_ji_intensity += STAR_LEVEL_SCORES.get(level, 0.5)

        risk_score += hua_ji_count * hua_ji_intensity * 10

        # 2. 凶格影响
        xiong_ge_count = sum(1 for p in self.patterns if p.get("type") == "凶格")
        risk_score += xiong_ge_count * 15

        # 3. 煞星影响
        malefic_count = 0
        for palace in self.gong_wei_12:
            malefic_stars = palace.get("malefic_stars", palace.get("sha_xing", []))
            malefic_count += len(malefic_stars) if isinstance(malefic_stars, list) else 0

        risk_score += malefic_count * 5

        # 归一化到0-100
        return min(100, max(0, risk_score))

    def calculate_opportunity_index(self) -> float:
        """
        计算机遇指数

        OPPORTUNITY_INDEX = (化禄数 × 禄强度) + Σ(吉格数 × 吉格强度)

        Returns:
            机遇指数 (0-100, 越高机遇越大)
        """
        opportunity_score = 0.0

        # 1. 化禄影响
        hua_lu_count = 0
        hua_lu_intensity = 0.0
        for palace in self.gong_wei_12:
            transforms = palace.get("transforms", palace.get("si_hua", {}))
            if "化禄" in transforms:
                hua_lu_count += 1
                stars = palace.get("stars", [])
                hua_lu_star = transforms["化禄"]
                level = self._get_star_level(stars, hua_lu_star)
                hua_lu_intensity += STAR_LEVEL_SCORES.get(level, 0.5)

        opportunity_score += hua_lu_count * hua_lu_intensity * 10

        # 2. 化权影响
        hua_quan_count = sum(
            1 for palace in self.gong_wei_12
            if "化权" in palace.get("transforms", palace.get("si_hua", {}))
        )
        opportunity_score += hua_quan_count * 8

        # 3. 化科影响
        hua_ke_count = sum(
            1 for palace in self.gong_wei_12
            if "化科" in palace.get("transforms", palace.get("si_hua", {}))
        )
        opportunity_score += hua_ke_count * 5

        # 4. 吉格影响
        ji_ge_count = sum(1 for p in self.patterns if p.get("type") == "吉格")
        opportunity_score += ji_ge_count * 12

        # 5. 吉利辅星影响
        lucky_stars = ["左辅", "右弼", "天魁", "天钺", "禄存"]
        lucky_star_count = 0
        for palace in self.gong_wei_12:
            auxiliary_stars = palace.get("auxiliary_stars", palace.get("fu_xing", []))
            if isinstance(auxiliary_stars, list):
                for star in auxiliary_stars:
                    star_name = star if isinstance(star, str) else star.get("name", "")
                    if star_name in lucky_stars:
                        lucky_star_count += 1

        opportunity_score += lucky_star_count * 3

        # 归一化到0-100
        return min(100, max(0, opportunity_score))

    def get_monthly_scores(self) -> List[Dict[str, Any]]:
        """
        计算月度运势趋势

        基于大运和流年信息估算月度运势波动

        Returns:
            月度运势列表
        """
        monthly_scores = []
        base_score = self.calculate_fortune_score()
        risk_index = self.calculate_risk_index()
        opportunity_index = self.calculate_opportunity_index()

        # 月度运势波动因子
        # 简化模型：基于流年四化产生周期性波动
        year_transforms = self._get_year_transforms()
        month_names = [
            "正月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "冬月", "腊月"
        ]

        for i, month_name in enumerate(month_names):
            # 基础波动：±10分
            import math
            base_fluctuation = math.sin((i + 1) * math.pi / 6) * 10

            # 流年四化影响
            transform_bonus = self._calculate_month_transform_bonus(
                year_transforms, i + 1
            )

            # 计算月度分数
            month_score = base_score + base_fluctuation + transform_bonus
            month_score = max(0, min(100, month_score))

            monthly_scores.append({
                "month": i + 1,
                "month_name": month_name,
                "score": round(month_score, 2),
                "level": self._score_to_level(month_score)
            })

        return monthly_scores

    def _get_year_transforms(self) -> List[Dict[str, str]]:
        """获取流年四化信息"""
        transforms_data = self.transforms.get("transforms", [])
        return transforms_data

    def _calculate_month_transform_bonus(
        self,
        year_transforms: List[Dict],
        month: int
    ) -> float:
        """计算月度四化加成"""
        bonus = 0.0

        # 简化模型：各月份对不同四化的敏感度
        sensitivity = {
            1: {"化禄": 1.0, "化权": 0.5, "化科": 0.5, "化忌": -0.5},
            2: {"化禄": 0.8, "化权": 0.7, "化科": 0.6, "化忌": -0.6},
            3: {"化禄": 0.6, "化权": 0.9, "化科": 0.7, "化忌": -0.7},
            4: {"化禄": 0.5, "化权": 1.0, "化科": 0.8, "化忌": -0.8},
            5: {"化禄": 0.7, "化权": 0.8, "化科": 0.9, "化忌": -0.7},
            6: {"化禄": 0.9, "化权": 0.6, "化科": 1.0, "化忌": -0.6},
            7: {"化禄": 1.0, "化权": 0.5, "化科": 0.9, "化忌": -0.5},
            8: {"化禄": 0.8, "化权": 0.7, "化科": 0.8, "化忌": -0.6},
            9: {"化禄": 0.6, "化权": 0.9, "化科": 0.7, "化忌": -0.7},
            10: {"化禄": 0.5, "化权": 1.0, "化科": 0.6, "化忌": -0.8},
            11: {"化禄": 0.7, "化权": 0.8, "化科": 0.5, "化忌": -0.7},
            12: {"化禄": 0.9, "化权": 0.6, "化科": 0.5, "化忌": -0.5},
        }

        month_sens = sensitivity.get(month, sensitivity[1])

        for transform in year_transforms:
            transform_type = transform.get("transform_type", "")
            if transform_type in month_sens:
                intensity = TRANSFORM_INTENSITY.get(transform_type, 0)
                bonus += intensity * month_sens[transform_type] * 3

        return bonus

    def _score_to_level(self, score: float) -> str:
        """将分数转换为等级"""
        if score >= 85:
            return FortuneLevel.EXCELLENT.value
        elif score >= 70:
            return FortuneLevel.GOOD.value
        elif score >= 50:
            return FortuneLevel.AVERAGE.value
        elif score >= 30:
            return FortuneLevel.FAIR.value
        else:
            return FortuneLevel.POOR.value

    def calculate_full(self) -> FortuneScore:
        """
        计算完整的运势报告

        Returns:
            完整的运势计算结果 (FortuneScore 对象)
        """
        dimension_scores = self.calculate_dimension_scores()
        overall_score = self.calculate_fortune_score()
        monthly_scores = self.get_monthly_scores()

        return FortuneScore(
            overall_score=overall_score,
            overall_level=self._score_to_level(overall_score),
            career_score=dimension_scores.get("career", DimensionScore("career", 50, "", [])).score,
            wealth_score=dimension_scores.get("wealth", DimensionScore("wealth", 50, "", [])).score,
            relationship_score=dimension_scores.get("relationship", DimensionScore("relationship", 50, "", [])).score,
            health_score=dimension_scores.get("health", DimensionScore("health", 50, "", [])).score,
            social_score=dimension_scores.get("social", DimensionScore("social", 50, "", [])).score,
            dimension_scores=dimension_scores,
            monthly_scores=monthly_scores
        )

    def calibrate_with_cases(self, similar_cases: List[Dict]) -> float:
        """
        使用相似案例数据校准分数

        Args:
            similar_cases: 相似命盘案例列表

        Returns:
            校准后的调整因子
        """
        if not similar_cases:
            return 1.0

        # 计算案例的平均运势
        total_score = 0.0
        for case in similar_cases:
            # 从案例中提取运势分数或置信度
            confidence = case.get("confidence", case.get("relevance", 0.5))
            total_score += confidence

        avg_confidence = total_score / len(similar_cases) if similar_cases else 0.5

        # 调整因子：基于案例相似度
        calibration_factor = 0.9 + (avg_confidence * 0.2)  # 0.9-1.1

        return calibration_factor


def calculate_fortune(
    gong_wei_12: Optional[List[Dict[str, Any]]] = None,
    ming_gong: Optional[Dict[str, Any]] = None,
    chart: Optional[Dict[str, Any]] = None,
    target_year: int = 2026
) -> Dict[str, Any]:
    """
    便捷函数：计算运势

    Args:
        gong_wei_12: 十二宫数据列表
        ming_gong: 命宫数据
        chart: 命盘数据字典（兼容旧格式）
        target_year: 目标年份

    Returns:
        运势计算结果字典
    """
    calculator = FortuneCalculator(
        gong_wei_12=gong_wei_12,
        ming_gong=ming_gong,
        chart=chart,
        target_year=target_year
    )
    result = calculator.calculate_full()
    return result.to_dict()
