"""
案例匹配引擎
基于多维度相似度算法，从案例库中匹配最相似的历史案例

使用 Pydantic 模型定义输入输出，复用 case_loader.py 中的案例数据
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from pydantic import BaseModel, Field
from pydantic import field_validator

from .case_loader import get_case_loader, DaxianCaseLoader
from .case_models import DaxianCase

# 配置日志
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic 输入输出模型
# ============================================================================

class ChartInput(BaseModel):
    """命盘输入模型"""
    birth_year_gan: Optional[str] = Field(None, description="年干 (甲/乙/丙/丁...)")
    wuxing_bureau: Optional[str] = Field(None, description="五行局 (水二局/木三局...)")
    main_stars: List[str] = Field(default_factory=list, description="主星列表")
    transforms: Dict[str, str] = Field(default_factory=dict, description="四化分布 {星名: 化禄/化权/化科/化忌}")
    patterns: List[str] = Field(default_factory=list, description="格局列表")
    palaces: Dict[str, str] = Field(default_factory=dict, description="宫位主星 {宫位: 主星}")
    dadian_number: Optional[int] = Field(None, ge=1, le=10, description="大限序号 (1-10)")
    dadian_palace: Optional[str] = Field(None, description="大限宫位")
    zodiac_type: Optional[str] = Field(None, description="命盘类型 (阳男阴女顺行等)")

    class Config:
        json_schema_extra = {
            "example": {
                "birth_year_gan": "甲",
                "wuxing_bureau": "木三局",
                "main_stars": ["紫微", "天机", "太阳"],
                "transforms": {"廉贞": "化禄", "紫微": "化权"},
                "patterns": ["紫微斗数"],
                "palaces": {"命宫": "天机", "财帛宫": "武曲"},
                "dadian_number": 5,
                "dadian_palace": "子女宫",
                "zodiac_type": "阳男阴女顺行"
            }
        }


class DimensionScores(BaseModel):
    """各维度相似度分数"""
    year_gan: float = Field(..., ge=0, le=1, description="年干相似度")
    wuxing_bureau: float = Field(..., ge=0, le=1, description="五行局相似度")
    main_stars: float = Field(..., ge=0, le=1, description="主星组合相似度")
    transforms: float = Field(..., ge=0, le=1, description="四化分布相似度")
    palace_strength: float = Field(..., ge=0, le=1, description="宫位强弱相似度")


class SimilarCase(BaseModel):
    """相似案例输出模型"""
    case_id: str = Field(..., description="案例ID")
    case_name: str = Field(..., description="案例名称")
    case_type: str = Field(..., description="案例类型")
    similarity_score: float = Field(..., ge=0, le=1, description="总相似度")
    dimension_scores: DimensionScores = Field(..., description="各维度分数")
    interpretation: str = Field("", description="解读文本")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    source: str = Field("", description="来源")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "case_id": self.case_id,
            "case_name": self.case_name,
            "case_type": self.case_type,
            "similarity_score": round(self.similarity_score, 4),
            "dimension_scores": self.dimension_scores.model_dump(),
            "interpretation": self.interpretation,
            "keywords": self.keywords,
            "source": self.source
        }


class MatchResult(BaseModel):
    """匹配结果输出模型"""
    total_cases: int = Field(..., description="案例库总数")
    matched_count: int = Field(..., description="匹配到的案例数")
    top_cases: List[SimilarCase] = Field(..., description="最相似的案例列表")
    average_score: float = Field(..., ge=0, le=1, description="平均相似度")


# ============================================================================
# 命盘特征类
# ============================================================================

class ChartFeatures:
    """命盘特征提取"""

    def __init__(
        self,
        birth_year_gan: Optional[str] = None,
        wuxing_bureau: Optional[str] = None,
        main_stars: Optional[List[str]] = None,
        transforms: Optional[Dict[str, str]] = None,
        patterns: Optional[List[str]] = None,
        palaces: Optional[Dict[str, str]] = None,
        dadian_number: Optional[int] = None,
        dadian_palace: Optional[str] = None,
        zodiac_type: Optional[str] = None
    ):
        self.birth_year_gan = birth_year_gan
        self.wuxing_bureau = wuxing_bureau
        self.main_stars = main_stars or []
        self.transforms = transforms or {}
        self.patterns = patterns or []
        self.palaces = palaces or {}
        self.dadian_number = dadian_number
        self.dadian_palace = dadian_palace
        self.zodiac_type = zodiac_type

    @classmethod
    def from_chart_input(cls, chart: ChartInput) -> "ChartFeatures":
        """从 ChartInput 创建"""
        return cls(
            birth_year_gan=chart.birth_year_gan,
            wuxing_bureau=chart.wuxing_bureau,
            main_stars=chart.main_stars,
            transforms=chart.transforms,
            patterns=chart.patterns,
            palaces=chart.palaces,
            dadian_number=chart.dadian_number,
            dadian_palace=chart.dadian_palace,
            zodiac_type=chart.zodiac_type
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChartFeatures":
        """从字典创建"""
        return cls(
            birth_year_gan=data.get("birth_year_gan"),
            wuxing_bureau=data.get("wuxing_bureau"),
            main_stars=data.get("main_stars", []),
            transforms=data.get("transforms", {}),
            patterns=data.get("patterns", []),
            palaces=data.get("palaces", {}),
            dadian_number=data.get("dadian_number"),
            dadian_palace=data.get("dadian_palace"),
            zodiac_type=data.get("zodiac_type")
        )


# ============================================================================
# 案例匹配器
# ============================================================================

class CaseMatcher:
    """案例匹配器

    多维度相似度算法权重:
    - 年干 (10%)
    - 五行局 (10%)
    - 主星组合 (25%)
    - 四化分布 (30%)
    - 宫位强弱 (25%)
    """

    # 相似度权重配置
    WEIGHTS = {
        "year_gan": 0.10,       # 年干
        "wuxing_bureau": 0.10,  # 五行局
        "main_stars": 0.25,     # 主星组合
        "transforms": 0.30,     # 四化分布
        "palace_strength": 0.25 # 宫位强弱
    }

    # 天干列表及五行属性
    YEAR_GAN_LIST = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    # 天干五行映射
    GAN_WUXING = {
        "甲": "木", "乙": "木",
        "丙": "火", "丁": "火",
        "戊": "土", "己": "土",
        "庚": "金", "辛": "金",
        "壬": "水", "癸": "水"
    }

    # 五行局映射
    WUXING_BUREAU_MAP = {
        "水二局": "水",
        "木三局": "木",
        "金四局": "金",
        "土五局": "土",
        "火六局": "火"
    }

    # 宫位列表
    PALACE_LIST = [
        "命宫", "兄弟宫", "夫妻宫", "子女宫",
        "财帛宫", "疾厄宫", "迁移宫", "奴仆宫",
        "官禄宫", "田宅宫", "福德宫", "父母宫"
    ]

    def __init__(self):
        """初始化案例匹配器"""
        self._case_loader: Optional[DaxianCaseLoader] = None
        self._load_cases()

    def _load_cases(self) -> None:
        """加载案例库"""
        try:
            self._case_loader = get_case_loader()
            logger.info(f"案例加载器初始化完成，共 {self._case_loader.total_cases} 条案例")
        except Exception as e:
            logger.error(f"加载案例库失败: {e}")
            self._case_loader = None

    @property
    def case_loader(self) -> Optional[DaxianCaseLoader]:
        """获取案例加载器"""
        return self._case_loader

    @property
    def total_cases(self) -> int:
        """获取案例总数"""
        if self._case_loader:
            return self._case_loader.total_cases
        return 0

    def extract_features(self, chart_data: Dict[str, Any]) -> ChartFeatures:
        """从命盘数据提取特征

        Args:
            chart_data: 命盘数据字典或 ChartInput 对象

        Returns:
            ChartFeatures: 命盘特征对象
        """
        if isinstance(chart_data, ChartInput):
            return ChartFeatures.from_chart_input(chart_data)
        return ChartFeatures.from_dict(chart_data)

    def _calculate_year_gan_similarity(
        self, source: ChartFeatures, target: DaxianCase
    ) -> float:
        """计算年干相似度

        Args:
            source: 源命盘特征
            target: 目标案例

        Returns:
            相似度分数 0-1
        """
        if not source.birth_year_gan:
            return 0.5

        case_gan = target.input.birth_year_gan
        if not case_gan:
            return 0.5

        # 完全匹配
        if source.birth_year_gan == case_gan:
            return 1.0

        # 同五行属性
        source_wuxing = self.GAN_WUXING.get(source.birth_year_gan, "")
        case_wuxing = self.GAN_WUXING.get(case_gan, "")
        if source_wuxing and source_wuxing == case_wuxing:
            return 0.7

        return 0.3

    def _calculate_wuxing_bureau_similarity(
        self, source: ChartFeatures, target: DaxianCase
    ) -> float:
        """计算五行局相似度

        Args:
            source: 源命盘特征
            target: 目标案例

        Returns:
            相似度分数 0-1
        """
        if not source.wuxing_bureau:
            return 0.5

        case_bureau = target.input.wuxing_bureau
        if not case_bureau:
            return 0.5

        # 完全匹配
        if source.wuxing_bureau == case_bureau:
            return 1.0

        # 同五行
        source_element = self.WUXING_BUREAU_MAP.get(source.wuxing_bureau, "")
        case_element = self.WUXING_BUREAU_MAP.get(case_bureau, "")
        if source_element and source_element == case_element:
            return 0.7

        return 0.3

    def _calculate_star_similarity(
        self, source: ChartFeatures, target: DaxianCase
    ) -> float:
        """计算主星组合相似度 (Jaccard)

        Args:
            source: 源命盘特征
            target: 目标案例

        Returns:
            相似度分数 0-1
        """
        if not source.main_stars:
            return 0.5

        # 从案例中提取主星
        case_stars = target.input.main_stars or target.input.stars or []
        if not case_stars:
            return 0.5

        # Jaccard相似度
        source_set = set(source.main_stars)
        case_set = set(case_stars)

        intersection = len(source_set & case_set)
        union = len(source_set | case_set)

        return intersection / union if union > 0 else 0.5

    def _calculate_transform_similarity(
        self, source: ChartFeatures, target: DaxianCase
    ) -> float:
        """计算四化分布相似度

        Args:
            source: 源命盘特征
            target: 目标案例

        Returns:
            相似度分数 0-1
        """
        if not source.transforms:
            return 0.5

        case_transform = target.input.transform or target.input.transform_1
        if not case_transform:
            return 0.5

        # 检查源命盘是否包含此四化
        source_transform_values = list(source.transforms.values())
        if case_transform in source_transform_values:
            return 1.0

        return 0.3

    def _calculate_palace_similarity(
        self, source: ChartFeatures, target: DaxianCase
    ) -> float:
        """计算宫位强弱相似度

        Args:
            source: 源命盘特征
            target: 目标案例

        Returns:
            相似度分数 0-1
        """
        case_palace = target.input.palace

        # 检查大限宫位匹配
        if source.dadian_palace and case_palace:
            if source.dadian_palace == case_palace:
                return 1.0
            # 检查三方四正关系
            if self._is_san_he_sifang(source.dadian_palace, case_palace):
                return 0.7

        # 检查命宫主星匹配
        source_ming_star = source.palaces.get("命宫")
        if source_ming_star:
            # 从案例中提取命宫主星
            case_ming_star = None
            if source.palaces:
                # 尝试从 target 的数据结构中获取
                case_input = target.input
                if hasattr(case_input, 'main_star') and case_input.main_star:
                    case_ming_star = case_input.main_star

            if case_ming_star == source_ming_star:
                return 0.8

        return 0.5

    def _is_san_he_sifang(self, palace1: str, palace2: str) -> bool:
        """判断两宫是否构成三合四方关系

        Args:
            palace1: 宫位1
            palace2: 宫位2

        Returns:
            是否为三合四方关系
        """
        if palace1 == palace2:
            return True

        san_he_map = {
            "命宫": ["财帛宫", "官禄宫", "迁移宫"],
            "财帛宫": ["命宫", "官禄宫", "迁移宫"],
            "官禄宫": ["命宫", "财帛宫", "迁移宫"],
            "迁移宫": ["命宫", "财帛宫", "官禄宫"],
        }

        if palace1 in san_he_map:
            return palace2 in san_he_map[palace1]

        return False

    def similarity_score(
        self, chart1: ChartFeatures, chart2: ChartFeatures
    ) -> Tuple[float, DimensionScores]:
        """计算两个命盘的相似度

        Args:
            chart1: 命盘1特征
            chart2: 命盘2特征

        Returns:
            (总相似度, 各维度分数)
        """
        # 转换为模拟的案例格式用于复用计算逻辑
        mock_case_1 = DaxianCase(
            case_id="chart1",
            agent="",
            type="",
            name="",
            input=chart1,  # type: ignore
            output=None,  # type: ignore
            source=""
        )

        mock_case_2 = DaxianCase(
            case_id="chart2",
            agent="",
            type="",
            name="",
            input=chart2,  # type: ignore
            output=None,  # type: ignore
            source=""
        )

        # 计算各维度相似度
        year_gan_score = self._calc_year_gan_between_charts(chart1, chart2)
        wuxing_bureau_score = self._calc_wuxing_bureau_between_charts(chart1, chart2)
        star_score = self._calc_stars_between_charts(chart1, chart2)
        transform_score = self._calc_transforms_between_charts(chart1, chart2)
        palace_score = self._calc_palace_between_charts(chart1, chart2)

        dimension_scores = DimensionScores(
            year_gan=year_gan_score,
            wuxing_bureau=wuxing_bureau_score,
            main_stars=star_score,
            transforms=transform_score,
            palace_strength=palace_score
        )

        # 加权计算总相似度
        total_score = (
            year_gan_score * self.WEIGHTS["year_gan"] +
            wuxing_bureau_score * self.WEIGHTS["wuxing_bureau"] +
            star_score * self.WEIGHTS["main_stars"] +
            transform_score * self.WEIGHTS["transforms"] +
            palace_score * self.WEIGHTS["palace_strength"]
        )

        return total_score, dimension_scores

    def _calc_year_gan_between_charts(self, c1: ChartFeatures, c2: ChartFeatures) -> float:
        """计算两命盘间的年干相似度"""
        if not c1.birth_year_gan or not c2.birth_year_gan:
            return 0.5
        if c1.birth_year_gan == c2.birth_year_gan:
            return 1.0
        if self.GAN_WUXING.get(c1.birth_year_gan) == self.GAN_WUXING.get(c2.birth_year_gan):
            return 0.7
        return 0.3

    def _calc_wuxing_bureau_between_charts(self, c1: ChartFeatures, c2: ChartFeatures) -> float:
        """计算两命盘间的五行局相似度"""
        if not c1.wuxing_bureau or not c2.wuxing_bureau:
            return 0.5
        if c1.wuxing_bureau == c2.wuxing_bureau:
            return 1.0
        if self.WUXING_BUREAU_MAP.get(c1.wuxing_bureau) == self.WUXING_BUREAU_MAP.get(c2.wuxing_bureau):
            return 0.7
        return 0.3

    def _calc_stars_between_charts(self, c1: ChartFeatures, c2: ChartFeatures) -> float:
        """计算两命盘间的主星相似度"""
        if not c1.main_stars or not c2.main_stars:
            return 0.5
        s1, s2 = set(c1.main_stars), set(c2.main_stars)
        intersection = len(s1 & s2)
        union = len(s1 | s2)
        return intersection / union if union > 0 else 0.5

    def _calc_transforms_between_charts(self, c1: ChartFeatures, c2: ChartFeatures) -> float:
        """计算两命盘间的四化相似度"""
        if not c1.transforms and not c2.transforms:
            return 0.5
        vals1, vals2 = set(c1.transforms.values()), set(c2.transforms.values())
        intersection = len(vals1 & vals2)
        union = len(vals1 | vals2)
        return intersection / union if union > 0 else 0.5

    def _calc_palace_between_charts(self, c1: ChartFeatures, c2: ChartFeatures) -> float:
        """计算两命盘间的宫位相似度"""
        if c1.dadian_palace and c2.dadian_palace:
            if c1.dadian_palace == c2.dadian_palace:
                return 1.0
            if self._is_san_he_sifang(c1.dadian_palace, c2.dadian_palace):
                return 0.7
        return 0.5

    def calculate_similarity(
        self, source: ChartFeatures, target: DaxianCase
    ) -> Tuple[float, DimensionScores]:
        """计算单案例相似度

        Args:
            source: 源命盘特征
            target: 目标案例 (DaxianCase)

        Returns:
            (总相似度, 各维度分数)
        """
        year_gan_score = self._calculate_year_gan_similarity(source, target)
        wuxing_bureau_score = self._calculate_wuxing_bureau_similarity(source, target)
        star_score = self._calculate_star_similarity(source, target)
        transform_score = self._calculate_transform_similarity(source, target)
        palace_score = self._calculate_palace_similarity(source, target)

        dimension_scores = DimensionScores(
            year_gan=year_gan_score,
            wuxing_bureau=wuxing_bureau_score,
            main_stars=star_score,
            transforms=transform_score,
            palace_strength=palace_score
        )

        # 加权计算总相似度
        total_score = (
            year_gan_score * self.WEIGHTS["year_gan"] +
            wuxing_bureau_score * self.WEIGHTS["wuxing_bureau"] +
            star_score * self.WEIGHTS["main_stars"] +
            transform_score * self.WEIGHTS["transforms"] +
            palace_score * self.WEIGHTS["palace_strength"]
        )

        return total_score, dimension_scores

    def find_similar_cases(
        self, input_chart: ChartInput, limit: int = 5
    ) -> MatchResult:
        """查找相似案例

        Args:
            input_chart: 输入命盘 (ChartInput Pydantic模型)
            limit: 返回数量限制

        Returns:
            MatchResult: 匹配结果 (Pydantic模型)
        """
        features = ChartFeatures.from_chart_input(input_chart)
        logger.info(
            f"提取命盘特征: 年干={features.birth_year_gan}, "
            f"五行局={features.wuxing_bureau}, 主星={features.main_stars[:3]}..."
        )

        all_results: List[SimilarCase] = []

        if self._case_loader is None:
            logger.warning("案例加载器未初始化")
            return MatchResult(
                total_cases=0,
                matched_count=0,
                top_cases=[],
                average_score=0.0
            )

        cases = self._case_loader.get_all_cases()
        total_cases = len(cases)

        for case in cases:
            try:
                score, dimension_scores = self.calculate_similarity(features, case)

                result = SimilarCase(
                    case_id=case.case_id,
                    case_name=case.name,
                    case_type=case.type,
                    similarity_score=score,
                    dimension_scores=dimension_scores,
                    interpretation=case.output.interpretation,
                    keywords=case.output.keywords,
                    source=case.source
                )
                all_results.append(result)
            except Exception as e:
                logger.warning(f"计算案例 {case.case_id} 相似度失败: {e}")
                continue

        # 按相似度降序排序
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)

        # 返回Top-N
        top_cases = all_results[:limit]
        matched_count = len(all_results)

        average_score = (
            sum(r.similarity_score for r in all_results) / matched_count
            if matched_count > 0 else 0.0
        )

        return MatchResult(
            total_cases=total_cases,
            matched_count=matched_count,
            top_cases=top_cases,
            average_score=round(average_score, 4)
        )

    def generate_case_context(
        self, similar_cases: List[SimilarCase]
    ) -> str:
        """生成案例上下文用于LLM

        Args:
            similar_cases: 相似案例列表

        Returns:
            格式化的上下文文本
        """
        if not similar_cases:
            return "未找到相似案例"

        context_parts = ["## 相似历史案例参考\n"]

        for i, case in enumerate(similar_cases, 1):
            context_parts.append(f"### 案例 {i}: {case.case_name}")
            context_parts.append(f"- 相似度: {case.similarity_score:.1%}")
            context_parts.append(f"- 类型: {case.case_type}")
            context_parts.append(f"- 维度分数: 年干={case.dimension_scores.year_gan:.2f}, "
                               f"五行局={case.dimension_scores.wuxing_bureau:.2f}, "
                               f"主星={case.dimension_scores.main_stars:.2f}, "
                               f"四化={case.dimension_scores.transforms:.2f}, "
                               f"宫位={case.dimension_scores.palace_strength:.2f}")
            context_parts.append(f"- 解读: {case.interpretation}")
            context_parts.append(f"- 关键词: {', '.join(case.keywords)}")
            context_parts.append(f"- 来源: {case.source}")
            context_parts.append("")

        return "\n".join(context_parts)


# ============================================================================
# 全局单例和快捷函数
# ============================================================================

_matcher: Optional[CaseMatcher] = None


def get_case_matcher() -> CaseMatcher:
    """获取案例匹配器实例"""
    global _matcher
    if _matcher is None:
        _matcher = CaseMatcher()
    return _matcher


def find_similar_cases(
    chart_data: Dict[str, Any], limit: int = 5
) -> Dict[str, Any]:
    """快捷函数：查找相似案例

    Args:
        chart_data: 命盘数据字典
        limit: 返回数量限制

    Returns:
        匹配结果字典
    """
    input_chart = ChartInput(**chart_data)
    matcher = get_case_matcher()
    result = matcher.find_similar_cases(input_chart, limit)
    return result.model_dump()


def similarity_score(
    chart1_data: Dict[str, Any], chart2_data: Dict[str, Any]
) -> Dict[str, Any]:
    """快捷函数：计算两个命盘的相似度

    Args:
        chart1_data: 命盘1数据字典
        chart2_data: 命盘2数据字典

    Returns:
        相似度结果字典
    """
    chart1 = ChartFeatures.from_dict(chart1_data)
    chart2 = ChartFeatures.from_dict(chart2_data)

    matcher = get_case_matcher()
    score, dimension_scores = matcher.similarity_score(chart1, chart2)

    return {
        "similarity_score": round(score, 4),
        "dimension_scores": dimension_scores.model_dump()
    }


def generate_case_context(
    similar_cases: List[Dict[str, Any]]
) -> str:
    """快捷函数：生成案例上下文

    Args:
        similar_cases: 相似案例列表

    Returns:
        上下文文本
    """
    matcher = get_case_matcher()
    cases = [SimilarCase(**c) for c in similar_cases]
    return matcher.generate_case_context(cases)
