"""
ChartVectorizer - 命盘特征向量提取模块

实现55维命盘特征向量提取：
- 主星组合：20维
- 格局特征：10维
- 四化特征：8维
- 宫位强弱：12维
- 五行分布：5维

案例涌现推理 = 数字孪生精神
- 找到历史上相似的命盘案例
- 将命运轨迹时序对齐
- 统计推断预测概率
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import math


# 主星列表（十四正曜）
ZHENGYAO_STARS = [
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",  # 北斗
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁",  # 南斗
    "七杀", "破军"  # 中天
]

# 辅星列表
FUXING_STARS = [
    "左辅", "右弼", "文昌", "文曲",
    "天魁", "天钺", "禄存", "天马",
    "火星", "铃星", "地空", "地劫"
]

# 四化类型
TRANSFORM_TYPES = ["化禄", "化权", "化科", "化忌"]

# 宫位列表
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "交友宫",
    "官禄宫", "田宅宫", "福德宫", "父母宫"
]

# 五行局
WUXING_JU = ["水二局", "木三局", "金四局", "土五局", "火六局"]

# 宫位强度等级（简化版）
PALACE_STRENGTH = {
    "命宫": 5, "财帛宫": 4, "官禄宫": 4,
    "夫妻宫": 3, "迁移宫": 3, "田宅宫": 3,
    "子女宫": 2, "福德宫": 2, "疾厄宫": 2,
    "兄弟宫": 1, "交友宫": 1, "父母宫": 1
}


class ChartFeatureQuality(Enum):
    """特征质量"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ChartFeatures:
    """
    命盘特征向量

    55维特征向量：
    - 主星组合(20维): 14主星 + 6个常见辅星组合
    - 格局特征(10维): 命宫强弱、五行平衡等
    - 四化特征(8维): 四化星分布
    - 宫位强弱(12维): 十二宫强弱分布
    - 五行分布(5维): 五行局分布
    """
    # 主星组合 (20维)
    main_star_vector: List[float] = field(default_factory=list)

    # 格局特征 (10维)
    pattern_vector: List[float] = field(default_factory=list)

    # 四化特征 (8维)
    transform_vector: List[float] = field(default_factory=list)

    # 宫位强弱 (12维)
    palace_strength_vector: List[float] = field(default_factory=list)

    # 五行分布 (5维)
    wuxing_vector: List[float] = field(default_factory=list)

    # 原始命盘数据（用于调试和详细分析）
    raw_data: Dict[str, Any] = field(default_factory=dict)

    # 特征质量
    quality: ChartFeatureQuality = ChartFeatureQuality.MEDIUM

    def __post_init__(self):
        """验证向量维度"""
        if len(self.main_star_vector) != 20:
            self.main_star_vector = [0.0] * 20
        if len(self.pattern_vector) != 10:
            self.pattern_vector = [0.0] * 10
        if len(self.transform_vector) != 8:
            self.transform_vector = [0.0] * 8
        if len(self.palace_strength_vector) != 12:
            self.palace_strength_vector = [0.0] * 12
        if len(self.wuxing_vector) != 5:
            self.wuxing_vector = [0.0] * 5

    def to_vector(self) -> List[float]:
        """
        转换为55维向量

        Returns:
            55维特征向量
        """
        return (
            self.main_star_vector +
            self.pattern_vector +
            self.transform_vector +
            self.palace_strength_vector +
            self.wuxing_vector
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "main_star_vector": self.main_star_vector,
            "pattern_vector": self.pattern_vector,
            "transform_vector": self.transform_vector,
            "palace_strength_vector": self.palace_strength_vector,
            "wuxing_vector": self.wuxing_vector,
            "quality": self.quality.value,
            "feature_count": 55
        }


@dataclass
class LifeEvent:
    """命运事件"""
    age: int                    # 年龄
    year: int                   # 年份
    event_type: str             # 事件类型：财运、事业、感情、健康
    description: str            # 事件描述
    significance: float         # 重要程度 0-1
    palace: str                 # 涉及宫位

    def to_dict(self) -> Dict[str, Any]:
        return {
            "age": self.age,
            "year": self.year,
            "event_type": self.event_type,
            "description": self.description,
            "significance": self.significance,
            "palace": self.palace
        }


@dataclass
class LifeTrajectory:
    """命运轨迹"""
    chart_id: str
    birth_year: int
    events: List[LifeEvent] = field(default_factory=list)

    def get_events_by_age(self, age: int) -> List[LifeEvent]:
        """获取指定年龄的事件"""
        return [e for e in self.events if e.age == age]

    def get_events_by_type(self, event_type: str) -> List[LifeEvent]:
        """获取指定类型的事件"""
        return [e for e in self.events if e.event_type == event_type]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "birth_year": self.birth_year,
            "events": [e.to_dict() for e in self.events]
        }


@dataclass
class ChartCase:
    """命盘案例"""
    case_id: str
    chart_id: str
    features: ChartFeatures
    trajectory: Optional[LifeTrajectory]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "chart_id": self.chart_id,
            "features": self.features.to_dict(),
            "trajectory": self.trajectory.to_dict() if self.trajectory else None,
            "metadata": self.metadata
        }


class ChartVectorizer:
    """
    命盘特征向量提取器

    从完整命盘数据中提取55维特征向量，用于案例检索和相似度计算。

    特征维度：
    - 主星组合(20维): 紫微、天机、太阳、武曲、天同、廉贞、天府、太阴、贪狼、巨门、天相、天梁、七杀、破军 + 6个常见辅星
    - 格局特征(10维): 命宫强弱、三方四正、事业星、财星、桃花星等
    - 四化特征(8维): 化禄、化权、化科、化忌在各宫分布
    - 宫位强弱(12维): 十二宫的强弱评分
    - 五行分布(5维): 水木金土火的分布
    """

    def __init__(self):
        """初始化向量器"""
        self._main_star_weights = self._init_main_star_weights()
        self._palace_element_strength = self._init_palace_element_strength()

    def _init_main_star_weights(self) -> Dict[str, float]:
        """初始化主星权重"""
        return {
            # 十四正曜权重
            "紫微": 1.0, "天机": 0.9, "太阳": 0.9,
            "武曲": 0.85, "天同": 0.8, "廉贞": 0.85,
            "天府": 0.9, "太阴": 0.85, "贪狼": 0.8,
            "巨门": 0.75, "天相": 0.8, "天梁": 0.85,
            "七杀": 0.8, "破军": 0.75,
            # 六颗常见辅星
            "左辅": 0.5, "右弼": 0.5, "文昌": 0.4, "文曲": 0.4,
            "禄存": 0.6, "天马": 0.5
        }

    def _init_palace_element_strength(self) -> Dict[str, Dict[str, float]]:
        """初始化宫位五行强度"""
        return {
            # 宫位: {五行: 强度}
            "命宫": {"木": 0.8, "火": 0.6, "土": 0.5, "金": 0.5, "水": 0.7},
            "财帛宫": {"金": 0.9, "水": 0.7, "木": 0.4, "火": 0.5, "土": 0.6},
            "官禄宫": {"火": 0.9, "木": 0.7, "土": 0.6, "金": 0.5, "水": 0.4},
            "夫妻宫": {"水": 0.8, "金": 0.7, "火": 0.5, "木": 0.6, "土": 0.5},
            "迁移宫": {"木": 0.8, "水": 0.7, "火": 0.6, "土": 0.5, "金": 0.5},
            "田宅宫": {"土": 0.9, "火": 0.6, "金": 0.5, "木": 0.5, "水": 0.6},
            "子女宫": {"木": 0.8, "火": 0.7, "水": 0.6, "金": 0.5, "土": 0.5},
            "福德宫": {"土": 0.8, "金": 0.7, "水": 0.6, "木": 0.5, "火": 0.6},
            "疾厄宫": {"木": 0.8, "水": 0.7, "火": 0.6, "土": 0.5, "金": 0.5},
            "兄弟宫": {"金": 0.8, "土": 0.7, "水": 0.6, "木": 0.5, "火": 0.5},
            "交友宫": {"金": 0.8, "土": 0.7, "水": 0.6, "火": 0.5, "木": 0.5},
            "父母宫": {"火": 0.8, "土": 0.7, "金": 0.6, "水": 0.5, "木": 0.5}
        }

    def extract(self, chart: Dict[str, Any]) -> ChartFeatures:
        """
        从命盘数据提取55维特征向量

        Args:
            chart: 命盘数据，包含 palaces, stars, transforms, birth_info

        Returns:
            ChartFeatures: 命盘特征向量

        Raises:
            ValueError: 当命盘数据格式不正确时
        """
        # 验证必要字段
        if not isinstance(chart, dict):
            raise ValueError("命盘数据必须是字典类型")

        # 提取各维度特征
        main_star_vec = self._extract_main_star_vector(chart)
        pattern_vec = self._extract_pattern_vector(chart)
        transform_vec = self._extract_transform_vector(chart)
        palace_vec = self._extract_palace_strength_vector(chart)
        wuxing_vec = self._extract_wuxing_vector(chart)

        # 计算特征质量
        quality = self._assess_quality(main_star_vec, pattern_vec, transform_vec)

        return ChartFeatures(
            main_star_vector=main_star_vec,
            pattern_vector=pattern_vec,
            transform_vector=transform_vec,
            palace_strength_vector=palace_vec,
            wuxing_vector=wuxing_vec,
            raw_data=chart,
            quality=quality
        )

    def _extract_main_star_vector(self, chart: Dict[str, Any]) -> List[float]:
        """
        提取主星组合向量(20维)

        前14维：十四正曜（紫微、天机、太阳、武曲、天同、廉贞、天府、太阴、贪狼、巨门、天相、天梁、七杀、破军）
        后6维：常见辅星（左辅、右弼、文昌、文曲、禄存、天马）
        """
        vector = [0.0] * 20

        # 获取星曜数据
        stars_data = chart.get("stars", {})
        palaces_data = chart.get("palaces", {})

        # 统计主星出现情况
        star_positions = {}  # star_name -> list of palace names

        # 从palaces中提取星曜
        if isinstance(palaces_data, dict):
            for palace_name, palace_info in palaces_data.items():
                if isinstance(palace_info, dict):
                    stars = palace_info.get("stars", [])
                    for star in stars:
                        if isinstance(star, dict):
                            star_name = star.get("name", "")
                        elif isinstance(star, str):
                            star_name = star
                        else:
                            continue

                        if star_name not in star_positions:
                            star_positions[star_name] = []
                        star_positions[star_name].append(palace_name)
                elif isinstance(palace_info, list):
                    for star in palace_info:
                        if isinstance(star, dict):
                            star_name = star.get("name", "")
                        elif isinstance(star, str):
                            star_name = star
                        else:
                            continue

                        if star_name not in star_positions:
                            star_positions[star_name] = []
                        star_positions[star_name].append(palace_name)

        # 从stars中提取（备用）
        if isinstance(stars_data, dict):
            for palace_name, stars in stars_data.items():
                for star in stars:
                    if isinstance(star, dict):
                        star_name = star.get("name", "")
                    elif isinstance(star, str):
                        star_name = star
                    else:
                        continue

                    if star_name not in star_positions:
                        star_positions[star_name] = []
                    if palace_name not in star_positions[star_name]:
                        star_positions[star_name].append(palace_name)

        # 填充十四正曜 (前14维)
        zhengyao_index = {
            "紫微": 0, "天机": 1, "太阳": 2, "武曲": 3,
            "天同": 4, "廉贞": 5, "天府": 6, "太阴": 7,
            "贪狼": 8, "巨门": 9, "天相": 10, "天梁": 11,
            "七杀": 12, "破军": 13
        }

        for star_name, idx in zhengyao_index.items():
            if star_name in star_positions:
                weight = self._main_star_weights.get(star_name, 0.5)
                count = len(star_positions[star_name])
                vector[idx] = weight * min(count, 3)  # 最多计3次

        # 填充辅星 (后6维)
        fuxing_index = {"左辅": 14, "右弼": 15, "文昌": 16, "文曲": 17, "禄存": 18, "天马": 19}

        for star_name, idx in fuxing_index.items():
            if star_name in star_positions:
                weight = self._main_star_weights.get(star_name, 0.3)
                count = len(star_positions[star_name])
                vector[idx] = weight * min(count, 2)

        # L2归一化
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def _extract_pattern_vector(self, chart: Dict[str, Any]) -> List[float]:
        """
        提取格局特征向量(10维)

        0-2: 命宫强弱 (命宫主星强度、三方四正、辅星)
        3-4: 事业格局
        5-6: 财富格局
        7-8: 感情格局
        9: 五行平衡度
        """
        vector = [0.0] * 10

        birth_info = chart.get("birth_info", {})
        palaces_data = chart.get("palaces", {})

        # 获取命宫信息
        ming_gong_stars = self._get_palace_stars(palaces_data, "命宫")

        # 命宫强弱评估 (0-2)
        vector[0] = self._assess_ming_gong_strength(ming_gong_stars)

        # 三方四正评估 (1)
        sanfang = self._assess_sanfang_sizheng(palaces_data)
        vector[1] = sanfang

        # 辅星拱照评估 (2)
        vector[2] = self._assess_auxiliary_stars(palaces_data, "命宫")

        # 事业格局评估 (3-4)
        career_stars = self._get_palace_stars(palaces_data, "官禄宫")
        vector[3] = self._assess_career_pattern(career_stars)
        vector[4] = self._assess_career_direction(palaces_data)

        # 财富格局评估 (5-6)
        wealth_stars = self._get_palace_stars(palaces_data, "财帛宫")
        vector[5] = self._assess_wealth_pattern(wealth_stars)
        vector[6] = self._assess_wealth_sources(palaces_data)

        # 感情格局评估 (7-8)
        marriage_stars = self._get_palace_stars(palaces_data, "夫妻宫")
        vector[7] = self._assess_marriage_pattern(marriage_stars)
        vector[8] = self._assess_peach_blossom(palaces_data)

        # 五行平衡度 (9)
        vector[9] = self._assess_wuxing_balance(chart)

        return vector

    def _extract_transform_vector(self, chart: Dict[str, Any]) -> List[float]:
        """
        提取四化特征向量(8维)

        0-1: 化禄 (本宫、对宫)
        2-3: 化权 (本宫、对宫)
        4-5: 化科 (本宫、对宫)
        6-7: 化忌 (本宫、对宫)
        """
        vector = [0.0] * 8

        transforms = chart.get("transforms", [])
        palaces_data = chart.get("palaces", {})

        # 统计四化星在各宫分布
        transform_distribution = {
            "化禄": {}, "化权": {}, "化科": {}, "化忌": {}
        }

        for transform in transforms:
            if isinstance(transform, dict):
                transform_type = transform.get("type", "")
                star = transform.get("star", "")
                if transform_type in transform_distribution:
                    transform_distribution[transform_type][star] = True

        # 计算各宫四化强度
        for i, palace_name in enumerate(PALACE_NAMES):
            palace = self._get_palace_data(palaces_data, palace_name)
            if not palace:
                continue

            palace_stars = self._get_palace_stars(palaces_data, palace_name)

            # 检查本宫四化
            for j, transform_type in enumerate(["化禄", "化权", "化科", "化忌"]):
                base_idx = j * 2
                if any(star in transform_distribution[transform_type] for star in palace_stars):
                    vector[base_idx] = 0.8
                # 对宫四化
                opposite_idx = self._get_opposite_palace_idx(i)
                opposite_name = PALACE_NAMES[opposite_idx]
                opposite_stars = self._get_palace_stars(palaces_data, opposite_name)
                if any(star in transform_distribution[transform_type] for star in opposite_stars):
                    vector[base_idx + 1] = 0.6

        # 归一化
        max_val = max(max(vector), 1.0)
        vector = [x / max_val for x in vector]

        return vector

    def _extract_palace_strength_vector(self, chart: Dict[str, Any]) -> List[float]:
        """
        提取宫位强弱向量(12维)

        每个宫位的强弱评分基于：
        - 主星强度
        - 辅星数量
        - 四化影响
        - 三方四正配合
        """
        vector = [0.0] * 12
        palaces_data = chart.get("palaces", {})

        for i, palace_name in enumerate(PALACE_NAMES):
            base_strength = PALACE_STRENGTH.get(palace_name, 1.0)
            palace_stars = self._get_palace_stars(palaces_data, palace_name)

            # 主星加成
            main_star_bonus = 0.0
            for star in palace_stars:
                if star in self._main_star_weights:
                    main_star_bonus += self._main_star_weights[star]

            # 辅星加成
            aux_star_bonus = len([s for s in palace_stars if s in FUXING_STARS]) * 0.1

            # 三方四正加成
            sanfang_bonus = self._calc_sanfang_bonus(palaces_data, palace_name)

            total = base_strength + main_star_bonus * 0.3 + aux_star_bonus + sanfang_bonus
            vector[i] = min(total / 10.0, 1.0)  # 归一化到0-1

        return vector

    def _extract_wuxing_vector(self, chart: Dict[str, Any]) -> List[float]:
        """
        提取五行分布向量(5维)

        水(0)、木(1)、金(2)、土(3)、火(4)
        """
        vector = [0.0] * 5

        # 获取五行局
        wuxing_ju = chart.get("birth_info", {}).get("wuxing_ju", "水二局")

        # 五行局权重映射
        wuxing_weights = {
            "水二局": [0.4, 0.1, 0.1, 0.1, 0.3],
            "木三局": [0.1, 0.4, 0.1, 0.2, 0.2],
            "金四局": [0.1, 0.1, 0.4, 0.2, 0.2],
            "土五局": [0.1, 0.1, 0.2, 0.4, 0.2],
            "火六局": [0.2, 0.2, 0.1, 0.2, 0.3]
        }

        weights = wuxing_weights.get(wuxing_ju, [0.2, 0.2, 0.2, 0.2, 0.2])
        vector = weights[:]

        # 计算十二宫五行分布
        palaces_data = chart.get("palaces", {})
        palace_elements = {
            "子": "水", "丑": "土", "寅": "木", "卯": "木",
            "辰": "土", "巳": "火", "午": "火", "未": "土",
            "申": "金", "酉": "金", "戌": "土", "亥": "水"
        }

        element_counts = {"水": 0, "木": 0, "金": 0, "土": 0, "火": 0}

        for palace_name in PALACE_NAMES:
            palace = self._get_palace_data(palaces_data, palace_name)
            if palace:
                branch = palace.get("branch", "")
                element = palace_elements.get(branch, "土")
                stars = self._get_palace_stars(palaces_data, palace_name)
                element_counts[element] += len(stars)

        # 归一化
        total = sum(element_counts.values())
        if total > 0:
            element_idx = {"水": 0, "木": 1, "金": 2, "土": 3, "火": 4}
            for elem, idx in element_idx.items():
                vector[idx] = (vector[idx] + element_counts[elem] / total) / 2

        # 归一化
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    # ========== 辅助方法 ==========

    def _get_palace_data(self, palaces: Dict[str, Any], palace_name: str) -> Optional[Dict]:
        """获取宫位数据"""
        if isinstance(palaces, dict):
            return palaces.get(palace_name)
        return None

    def _get_palace_stars(self, palaces: Dict[str, Any], palace_name: str) -> List[str]:
        """获取宫位星曜列表"""
        palace = self._get_palace_data(palaces, palace_name)
        if not palace:
            return []

        stars = palace.get("stars", [])
        if isinstance(stars, list):
            return [s.get("name", "") if isinstance(s, dict) else s for s in stars]
        return []

    def _get_opposite_palace_idx(self, idx: int) -> int:
        """获取对宫索引"""
        return (idx + 6) % 12

    def _assess_ming_gong_strength(self, stars: List[str]) -> float:
        """评估命宫强度"""
        if not stars:
            return 0.0

        score = 0.0
        has_zhengyao = any(s in ZHENGYAO_STARS for s in stars)
        has_fuxing = any(s in FUXING_STARS for s in stars)

        if has_zhengyao:
            score += 0.5
        if has_fuxing:
            score += 0.3
        if len(stars) >= 3:
            score += 0.2

        return min(score, 1.0)

    def _assess_sanfang_sizheng(self, palaces: Dict[str, Any]) -> float:
        """评估三方四正"""
        # 命宫的三方四正：命宫、财帛宫、官禄宫、迁移宫
        target_palaces = ["命宫", "财帛宫", "官禄宫", "迁移宫"]
        total_stars = 0

        for palace_name in target_palaces:
            stars = self._get_palace_stars(palaces, palace_name)
            total_stars += len(stars)

        return min(total_stars / 20.0, 1.0)

    def _assess_auxiliary_stars(self, palaces: Dict[str, Any], target_palace: str) -> float:
        """评估辅星拱照"""
        target_idx = PALACE_NAMES.index(target_palace) if target_palace in PALACE_NAMES else 0

        # 左右夹宫
        left_idx = (target_idx - 1) % 12
        right_idx = (target_idx + 1) % 12

        left_stars = self._get_palace_stars(palaces, PALACE_NAMES[left_idx])
        right_stars = self._get_palace_stars(palaces, PALACE_NAMES[right_idx])

        has_left = any(s in ["左辅", "右弼"] for s in left_stars)
        has_right = any(s in ["左辅", "右弼"] for s in right_stars)

        if has_left and has_right:
            return 0.8
        elif has_left or has_right:
            return 0.5
        return 0.2

    def _assess_career_pattern(self, stars: List[str]) -> float:
        """评估事业格局"""
        career_stars = ["太阳", "武曲", "天府", "天梁", "三台", "八座"]
        score = sum(0.2 for s in stars if s in career_stars)
        return min(score, 1.0)

    def _assess_career_direction(self, palaces: Dict[str, Any]) -> float:
        """评估事业方向"""
        # 官禄宫和迁移宫的配合
        career_stars = self._get_palace_stars(palaces, "官禄宫")
        migration_stars = self._get_palace_stars(palaces, "迁移宫")

        combined = set(career_stars) | set(migration_stars)

        if any(s in ["紫微", "天府", "太阳"] for s in combined):
            return 0.8  # 管理类
        elif any(s in ["武曲", "天机", "贪狼"] for s in combined):
            return 0.6  # 财务/商业
        return 0.4

    def _assess_wealth_pattern(self, stars: List[str]) -> float:
        """评估财富格局"""
        wealth_stars = ["武曲", "太阴", "天府", "禄存", "紫微"]
        score = sum(0.25 for s in stars if s in wealth_stars)
        return min(score, 1.0)

    def _assess_wealth_sources(self, palaces: Dict[str, Any]) -> float:
        """评估财富来源"""
        # 财帛宫和田宅宫的配合
        wealth_stars = self._get_palace_stars(palaces, "财帛宫")
        property_stars = self._get_palace_stars(palaces, "田宅宫")

        combined = set(wealth_stars) | set(property_stars)

        if any(s in ["武曲", "太阴"] for s in combined):
            return 0.7  # 正财
        elif any(s in ["贪狼", "火星"] for s in combined):
            return 0.5  # 动财
        return 0.3

    def _assess_marriage_pattern(self, stars: List[str]) -> float:
        """评估感情格局"""
        marriage_stars = ["天同", "太阴", "贪狼", "廉贞", "天府"]
        score = sum(0.25 for s in stars if s in marriage_stars)
        return min(score, 1.0)

    def _assess_peach_blossom(self, palaces: Dict[str, Any]) -> float:
        """评估桃花程度"""
        # 夫妻宫、子女宫、福德宫的综合评估
        target_palaces = ["夫妻宫", "子女宫", "福德宫"]
        peach_stars = ["贪狼", "廉贞", "天相", "文曲", "文昌"]

        total_peach = 0
        for palace_name in target_palaces:
            stars = self._get_palace_stars(palaces, palace_name)
            total_peach += sum(1 for s in stars if s in peach_stars)

        return min(total_peach / 6.0, 1.0)

    def _assess_wuxing_balance(self, chart: Dict[str, Any]) -> float:
        """评估五行平衡度"""
        palaces_data = chart.get("palaces", {})
        palace_elements = {
            "子": "水", "丑": "土", "寅": "木", "卯": "木",
            "辰": "土", "巳": "火", "午": "火", "未": "土",
            "申": "金", "酉": "金", "戌": "土", "亥": "水"
        }

        element_counts = {"水": 0, "木": 0, "金": 0, "土": 0, "火": 0}

        for palace_name in PALACE_NAMES:
            palace = self._get_palace_data(palaces_data, palace_name)
            if palace:
                branch = palace.get("branch", "")
                element = palace_elements.get(branch, "土")
                stars = self._get_palace_stars(palaces_data, palace_name)
                element_counts[element] += len(stars) + 1

        # 计算方差（越平衡方差越小）
        total = sum(element_counts.values())
        if total == 0:
            return 0.5

        avg = total / 5.0
        variance = sum((count - avg) ** 2 for count in element_counts.values()) / 5.0

        # 归一化：方差越小分数越高
        max_variance = (total - avg) ** 2 if total > 5 else avg ** 2 * 4
        balance = 1.0 - (variance / max_variance) if max_variance > 0 else 1.0

        return max(0.0, min(1.0, balance))

    def _calc_sanfang_bonus(self, palaces: Dict[str, Any], palace_name: str) -> float:
        """计算三方四正加成"""
        if palace_name not in PALACE_NAMES:
            return 0.0

        idx = PALACE_NAMES.index(palace_name)

        # 三方：命宫+财帛宫+官禄宫（如果是命宫）或对应的三方宫
        if palace_name == "命宫":
            sanfang_names = ["财帛宫", "官禄宫", "迁移宫"]
        elif palace_name == "财帛宫":
            sanfang_names = ["命宫", "官禄宫", "迁移宫"]
        elif palace_name == "官禄宫":
            sanfang_names = ["命宫", "财帛宫", "迁移宫"]
        elif palace_name == "迁移宫":
            sanfang_names = ["命宫", "财帛宫", "官禄宫"]
        else:
            return 0.0

        bonus = 0.0
        for name in sanfang_names:
            stars = self._get_palace_stars(palaces, name)
            bonus += len(stars) * 0.05

        return min(bonus, 0.3)

    def _assess_quality(
        self,
        main_star_vec: List[float],
        pattern_vec: List[float],
        transform_vec: List[float]
    ) -> ChartFeatureQuality:
        """评估特征质量"""
        # 检查主星覆盖率
        main_star_density = sum(1 for x in main_star_vec[:14] if x > 0) / 14.0

        # 检查格局完整性
        pattern_density = sum(1 for x in pattern_vec if x > 0) / 10.0

        # 检查四化覆盖率
        transform_density = sum(1 for x in transform_vec if x > 0) / 8.0

        if main_star_density >= 0.5 and pattern_density >= 0.4 and transform_density >= 0.3:
            return ChartFeatureQuality.HIGH
        elif main_star_density >= 0.3 and pattern_density >= 0.2:
            return ChartFeatureQuality.MEDIUM
        return ChartFeatureQuality.LOW

    def compute_similarity(
        self,
        features1: ChartFeatures,
        features2: ChartFeatures
    ) -> float:
        """
        计算两个命盘特征的余弦相似度

        Args:
            features1: 第一个命盘特征
            features2: 第二个命盘特征

        Returns:
            float: 相似度得分 (0-1)
        """
        vec1 = features1.to_vector()
        vec2 = features2.to_vector()

        # 余弦相似度
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


# 便捷函数
def extract_chart_features(chart: Dict[str, Any]) -> ChartFeatures:
    """
    从命盘提取特征向量

    Args:
        chart: 命盘数据

    Returns:
        ChartFeatures: 命盘特征向量
    """
    vectorizer = ChartVectorizer()
    return vectorizer.extract(chart)


def compute_chart_similarity(
    chart1: Dict[str, Any],
    chart2: Dict[str, Any]
) -> float:
    """
    计算两个命盘的相似度

    Args:
        chart1: 第一个命盘
        chart2: 第二个命盘

    Returns:
        float: 相似度得分 (0-1)
    """
    vectorizer = ChartVectorizer()
    features1 = vectorizer.extract(chart1)
    features2 = vectorizer.extract(chart2)
    return vectorizer.compute_similarity(features1, features2)
