"""
TransformAgent - 四化分析智能体

分析十天干四化在十二宫位的飞化情况

模块化结构：
- transform_constants.py: 常量定义（enums、四化映射表、解释词典）
- transform_types.py: 类型定义（dataclasses）
"""

import json
import os
from typing import Dict, List, Any, Optional

# Import from modular components
from .transform_constants import (
    TransformType,
    TransformCycleType,
    TransformInteraction,
    TransformPathType,
    HEAVENLY_STEM_TRANSFORMS,
    TRANSFORM_INTERPRETATIONS,
    INTERACTION_INTERPRETATIONS,
    CYCLE_INTERPRETATIONS,
)
from .transform_types import (
    TransformStar,
    PalaceTransform,
    TransformPathStep,
    TransformPath,
    TransformPathAnalysis,
    TransformAnalysis,
    CycleStage,
    CycleAnalysis,
)
from .cache_decorator import cached_chart_analysis


def load_transform_rules() -> Dict[str, Dict[str, str]]:
    """
    从规则文件加载四化规则

    Returns:
        四化规则字典，格式: {"甲": {"禄": "廉贞", "权": "破军", ...}, ...}
    """
    rules_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "..",
        "data_source", "mlx", "data", "rules", "transformations"
    )

    # 首先尝试加载十天干四化映射表
    heavenly_stems_path = os.path.join(rules_path, "heavenly_stems.json")
    if os.path.exists(heavenly_stems_path):
        try:
            with open(heavenly_stems_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "heavenly_stems" in data:
                    return data["heavenly_stems"]
        except Exception:
            pass

    # 如果规则目录存在，尝试加载其他JSON文件
    if os.path.exists(rules_path):
        for filename in os.listdir(rules_path):
            if filename.endswith(".json") and filename != "index.json":
                filepath = os.path.join(rules_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # 检查是否是四化映射格式
                        if isinstance(data, dict):
                            first_key = next(iter(data.keys()), None)
                            if first_key in ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]:
                                return data
                except Exception:
                    pass

    # 返回默认规则
    return HEAVENLY_STEM_TRANSFORMS


# 全局四化规则缓存
_TRANSFORM_RULES_CACHE: Dict[str, Dict[str, str]] = None


def get_transform_rules() -> Dict[str, Dict[str, str]]:
    """
    获取四化规则（带缓存）

    Returns:
        四化规则字典
    """
    global _TRANSFORM_RULES_CACHE
    if _TRANSFORM_RULES_CACHE is None:
        _TRANSFORM_RULES_CACHE = load_transform_rules()
    return _TRANSFORM_RULES_CACHE


class TransformAgent:
    """
    四化分析智能体

    分析十天干四化在十二宫位的飞化情况，
    追踪禄权科忌四化分布，分析四化交互关系
    """

    def __init__(self, chart_data: Any = None):
        """
        初始化四化分析智能体

        Args:
            chart_data: 命盘数据，包含宫位星曜信息
        """
        self.chart = chart_data
        self.transform_rules = get_transform_rules()

    def get_transformations(self, heavenly_stem: str) -> Dict[str, str]:
        """
        获取指定天干的四化星曜

        Args:
            heavenly_stem: 天干 (甲乙丙丁戊己庚辛壬癸)

        Returns:
            四化星曜字典 {"禄": star, "权": star, "科": star, "忌": star}

        Raises:
            ValueError: 天干无效时
        """
        if heavenly_stem not in self.transform_rules:
            valid_stems = list(self.transform_rules.keys())
            raise ValueError(
                f"无效的天干: {heavenly_stem}。有效值为: {', '.join(valid_stems)}"
            )

        return self.transform_rules[heavenly_stem].copy()

    def is_valid_heavenly_stem(self, stem: str) -> bool:
        """检查是否为有效天干"""
        return stem in self.transform_rules

    def analyze_transformations(self, year_stem: str, palace_stars: Dict[str, Any] = None) -> TransformAnalysis:
        """
        分析四化飞化

        Args:
            year_stem: 出生年干
            palace_stars: 宫位星曜数据，格式: {宫位名: [星曜列表]}

        Returns:
            四化分析结果
        """
        if not self.is_valid_heavenly_stem(year_stem):
            raise ValueError(f"无效的天干: {year_stem}")

        # 获取四化星曜
        transforms = self.get_transformations(year_stem)

        # 构建TransformStar对象
        transform_stars: List[TransformStar] = []
        palace_transforms: Dict[str, PalaceTransform] = {}

        for transform_type, star_name in transforms.items():
            transform_enum = TransformType(f"化{transform_type}")
            ts = TransformStar(transform_type=transform_enum, star_name=star_name)
            transform_stars.append(ts)

            # 如果有宫位数据，查找四化星所在的宫位
            if palace_stars:
                for palace_name, stars in palace_stars.items():
                    if star_name in stars:
                        if palace_name not in palace_transforms:
                            palace_transforms[palace_name] = PalaceTransform(palace_name=palace_name)
                        ts_copy = TransformStar(
                            transform_type=transform_enum,
                            star_name=star_name,
                            palace=palace_name
                        )
                        palace_transforms[palace_name].transforms.append(ts_copy)

        # 分析四化交互
        interactions = self._analyze_interactions(transform_stars, palace_stars)

        # 生成解释
        interpretation = self._generate_interpretation(year_stem, transform_stars, palace_stars, interactions)

        return TransformAnalysis(
            year_stem=year_stem,
            transforms=transform_stars,
            palace_transforms=palace_transforms,
            interactions=interactions,
            interpretation=interpretation
        )

    def _analyze_interactions(self, transforms: List[TransformStar],
                               palace_stars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """分析四化交互关系"""
        interactions = []

        transform_types = {t.transform_type for t in transforms}

        # 检查存在的交互组合
        has_lu = TransformType.HUA_LU in transform_types
        has_quan = TransformType.HUA_QUAN in transform_types
        has_ke = TransformType.HUA_KE in transform_types
        has_ji = TransformType.HUA_JI in transform_types

        if has_lu and has_quan and has_ke and has_ji:
            interactions.append({
                "type": TransformInteraction.LU_QUAN_KE_JI.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.LU_QUAN_KE_JI]
            })
        elif has_lu and has_quan and has_ke:
            interactions.append({
                "type": TransformInteraction.LU_QUAN_KE.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.LU_QUAN_KE]
            })
        elif has_lu and has_quan:
            interactions.append({
                "type": TransformInteraction.LU_QUAN.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.LU_QUAN]
            })
        elif has_lu and has_ke:
            interactions.append({
                "type": TransformInteraction.LU_KE.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.LU_KE]
            })
        elif has_quan and has_ke:
            interactions.append({
                "type": TransformInteraction.QUAN_KE.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.QUAN_KE]
            })

        if has_lu and has_ji:
            interactions.append({
                "type": TransformInteraction.LU_JI.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.LU_JI]
            })
        if has_quan and has_ji:
            interactions.append({
                "type": TransformInteraction.QUAN_JI.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.QUAN_JI]
            })
        if has_ke and has_ji:
            interactions.append({
                "type": TransformInteraction.KE_JI.value,
                "interpretation": INTERACTION_INTERPRETATIONS[TransformInteraction.KE_JI]
            })

        return interactions

    def _generate_interpretation(self, year_stem: str,
                                 transforms: List[TransformStar],
                                 palace_stars: Dict[str, Any],
                                 interactions: List[Dict[str, Any]]) -> str:
        """生成四化解释"""
        lines = []

        lines.append(f"【{year_stem}年干四化分析】")
        lines.append("")

        # 四化星曜
        lines.append("一、四化星曜分布")
        for t in transforms:
            star = t.star_name
            transform_type = t.transform_type.value

            # 获取该四化的解释
            if transform_type in TRANSFORM_INTERPRETATIONS:
                interpretation = TRANSFORM_INTERPRETATIONS[transform_type].get(star, "")
                if interpretation:
                    lines.append(f"  {transform_type}{star}: {interpretation}")

        lines.append("")

        # 宫位分析
        if palace_stars:
            lines.append("二、四化星曜落宫")
            for t in transforms:
                star = t.star_name
                for palace_name, stars in palace_stars.items():
                    if star in stars:
                        lines.append(f"  {star}位于{palace_name}")

            lines.append("")

        # 交互分析
        if interactions:
            lines.append("三、四化交互关系")
            for interaction in interactions:
                lines.append(f"  {interaction['type']}: {interaction['interpretation']}")

            lines.append("")

        # 总结
        lines.append("四、总体评价")
        if any(i["type"] == TransformInteraction.LU_QUAN_KE.value for i in interactions):
            lines.append("  三奇嘉会，名利双收，整体格局为吉。")
        elif any(i["type"] == TransformInteraction.LU_JI.value for i in interactions):
            lines.append("  禄忌对冲格局，财禄有损耗，须注意先成后败。")
        else:
            lines.append("  格局配置一般，须根据具体星曜组合论断。")

        return "\n".join(lines)

    def get_transform_by_stem(self, stem: str, transform_type: str) -> Optional[str]:
        """
        获取特定天干特定四化的星曜

        Args:
            stem: 天干
            transform_type: 四化类型 (禄/权/科/忌)

        Returns:
            星曜名称或None
        """
        if not self.is_valid_heavenly_stem(stem):
            return None

        transforms = self.transform_rules[stem]
        return transforms.get(transform_type)

    def analyze_transform_paths(
        self,
        palace_stars: Dict[str, List[str]],
        start_palace: Optional[str] = None,
        path_type: Optional[TransformPathType] = None
    ) -> TransformPathAnalysis:
        """
        分析飞化路径

        飞化类型：
        - 禄转忌：本宫化禄→忌入某宫
        - 忌转忌：本宫化忌→忌入某宫，再从该宫化忌
        - 追禄：忌入某宫后，该宫再化禄（同星曜）
        - 追权：忌入某宫后，该宫再化权（同星曜）
        - 追忌：禄入某宫后，该宫再化忌（非必同星曜）

        Args:
            palace_stars: 宫位星曜数据，格式: {宫位名: [星曜列表]}
            start_palace: 起始宫位（可选，不指定则分析所有宫位）
            path_type: 飞化类型（可选，不指定则分析所有类型）

        Returns:
            飞化路径分析结果
        """
        # 获取年干信息
        year_stem = ""
        if self.chart and isinstance(self.chart, dict):
            year_stem = self.chart.get("year_stem", "")

        chart_data = {
            "year_stem": year_stem,
            "palace_stars": palace_stars
        }

        return analyze_transform_path(chart_data, start_palace, path_type)

    def analyze_transform_cycle(self, palace_stars: Dict[str, List[str]] = None) -> CycleAnalysis:
        """
        分析成住坏空四化周期

        成住坏空是佛学宇宙观中的四劫，对应紫微斗数四化：
        - 成 → 化禄（缘起）
        - 住 → 化权（持续）
        - 坏 → 化科（衰减）
        - 空 → 化忌（结束）

        Args:
            palace_stars: 宫位星曜数据，格式: {宫位名: [星曜列表]}

        Returns:
            成住坏空周期分析结果
        """
        # 获取年干信息
        year_stem = ""
        if self.chart and isinstance(self.chart, dict):
            year_stem = self.chart.get("year_stem", "")

        chart_data = {
            "year_stem": year_stem,
            "palace_stars": palace_stars if palace_stars else {}
        }

        return analyze_transform_cycle(chart_data)


def get_transform(year_stem: str) -> TransformAnalysis:
    """
    快捷函数：获取指定年干的四化分析

    Args:
        year_stem: 出生年干

    Returns:
        四化分析结果
    """
    agent = TransformAgent()
    return agent.analyze_transformations(year_stem)


# ============ 飞化路径分析 ============

# 十二宫位名称（按顺序）
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "交友宫",
    "官禄宫", "田宅宫", "福德宫", "父母宫"
]

# 宫位四化解释
TRANSFORM_PATH_INTERPRETATIONS: Dict[TransformPathType, str] = {
    TransformPathType.LU_ZHUAN_JI: "禄转忌：禄是因、忌是果。化禄入某宫后，该宫再化忌飞入目标宫，代表从得到转为付出或收获转为遗憾。",
    TransformPathType.JI_ZHUAN_JI: "忌转忌：连续的忌，深入因果。代表持续的责任、负担或纠缠。",
    TransformPathType.ZHUI_LU: "追禄：禄随忌走（需同星曜）。加倍之得或加倍之损取决于禄忌组合。",
    TransformPathType.ZHUI_QUAN: "追权：权随忌走（同星曜）。代表在责任中追求权力或成就。",
    TransformPathType.ZHUI_JI: "追忌：忌随禄走（非必同星曜）。代表在收获后承担额外责任或付出。",
    TransformPathType.JI_ZHUAN_JI_2: "二度转忌：忌转忌后再转忌，代表更深层次的因果纠缠。",
    TransformPathType.JI_ZHUAN_JI_3: "三度转忌：三连续的忌，代表极重的因果负担。"
}


def _build_palace_transform_map(
    palace_stars: Dict[str, List[str]],
    transform_rules: Dict[str, Dict[str, str]],
    year_stem: str
) -> Dict[str, PalaceTransform]:
    """
    构建宫位四化映射表

    Args:
        palace_stars: 宫位星曜数据，格式: {宫位名: [星曜列表]}
        transform_rules: 四化规则
        year_stem: 年干（用于筛选特定年份的四化）

    Returns:
        宫位四化映射字典
    """
    palace_transform_map: Dict[str, PalaceTransform] = {}

    # 获取该年干的四化星
    year_transforms = transform_rules.get(year_stem, {})

    # 遍历所有宫位，查找哪些星曜在哪些宫位产生了四化
    for palace_name, stars in palace_stars.items():
        palace_transform = PalaceTransform(palace_name=palace_name)
        for star in stars:
            # 只检查这个星曜是否是该年干的四化星
            for transform_type_key, transform_star in year_transforms.items():
                if transform_star == star:
                    # 找到了匹配的星曜
                    if transform_type_key == "禄":
                        palace_transform.transforms.append(
                            TransformStar(TransformType.HUA_LU, star, palace_name)
                        )
                    elif transform_type_key == "权":
                        palace_transform.transforms.append(
                            TransformStar(TransformType.HUA_QUAN, star, palace_name)
                        )
                    elif transform_type_key == "科":
                        palace_transform.transforms.append(
                            TransformStar(TransformType.HUA_KE, star, palace_name)
                        )
                    elif transform_type_key == "忌":
                        palace_transform.transforms.append(
                            TransformStar(TransformType.HUA_JI, star, palace_name)
                        )
                    break  # 只匹配一次，避免同一星曜被多次添加
        if palace_transform.transforms:
            palace_transform_map[palace_name] = palace_transform

    return palace_transform_map


def _find_transform_star_palace(
    palace_transform_map: Dict[str, PalaceTransform],
    star_name: str
) -> Optional[str]:
    """查找特定星曜所在的宫位"""
    for palace_name, pt in palace_transform_map.items():
        for t in pt.transforms:
            if t.star_name == star_name:
                return palace_name
    return None


def _get_star_transform_type(
    transform_rules: Dict[str, Dict[str, str]],
    star_name: str
) -> Optional[TransformType]:
    """获取星曜的四化类型"""
    for stem, transforms in transform_rules.items():
        for transform_type_key, transform_star in transforms.items():
            if transform_star == star_name:
                if transform_type_key == "禄":
                    return TransformType.HUA_LU
                elif transform_type_key == "权":
                    return TransformType.HUA_QUAN
                elif transform_type_key == "科":
                    return TransformType.HUA_KE
                elif transform_type_key == "忌":
                    return TransformType.HUA_JI
    return None


def _interpret_lu_zhuan_ji(path: TransformPath) -> str:
    """解释禄转忌路径"""
    start = path.start_palace
    end = path.end_palace
    steps = path.steps
    if len(steps) >= 2:
        lu_star = steps[0].star_name
        ji_star = steps[1].star_name
        return f"本宫{start}化{lu_star}禄，禄入{end}后，{end}再化{ji_star}忌飞入目标宫。禄是福缘，忌是付出，此为因果转化。忌挟禄入第二宫，第二宫得禄气。"
    return f"{start}禄转忌路径"


def _interpret_ji_zhuan_ji(path: TransformPath) -> str:
    """解释忌转忌路径"""
    start = path.start_palace
    end = path.end_palace
    steps = path.steps
    seq_count = path.sequence_count
    if seq_count == 1:
        return f"本宫{start}化忌，忌入{end}。连续化忌，深入因果。"
    elif seq_count == 2:
        return f"{start}忌转忌，二度连续化忌。因果纠缠加深。"
    else:
        return f"{start}三忌转忌，因果极重，事多阻碍。"


def _interpret_zhui_lu(path: TransformPath, is_same_star: bool) -> str:
    """解释追禄路径"""
    steps = path.steps
    if len(steps) >= 2:
        ji_star = steps[0].star_name if steps else ""
        lu_star = steps[1].star_name if len(steps) > 1 else ""
        if is_same_star:
            return f"忌入某宫后，该宫再化{lu_star}禄（与{ji_star}同星曜），形成禄忌成双忌（加倍之损）。禄随忌走，得失并至。"
        else:
            return f"忌入某宫后，该宫再化{lu_star}禄（非同星曜），星曜不同象义各异。"
    return "追禄路径"


def _interpret_zhui_quan(path: TransformPath, is_same_star: bool) -> str:
    """解释追权路径"""
    steps = path.steps
    if len(steps) >= 2:
        ji_star = steps[0].star_name if steps else ""
        quan_star = steps[1].star_name if len(steps) > 1 else ""
        if is_same_star:
            return f"忌入某宫后，该宫再化{quan_star}权（与{ji_star}同星曜）。权随忌走，在责任中追求权力与成就。"
        else:
            return f"忌入某宫后，该宫再化{quan_star}权（非同星曜）。"
    return "追权路径"


def _interpret_zhui_ji(path: TransformPath, is_same_star: bool) -> str:
    """解释追忌路径"""
    steps = path.steps
    if len(steps) >= 2:
        lu_star = steps[0].star_name if steps else ""
        ji_star = steps[1].star_name if len(steps) > 1 else ""
        if is_same_star:
            return f"禄入某宫后，该宫再化{ji_star}忌（与{lu_star}同星曜），形成禄忌成双禄（加倍之得）。忌随禄走，收获与责任并存。"
        else:
            return f"禄入某宫后，该宫再化{ji_star}忌（非同星曜）。星曜不同，得失有别。"
    return "追忌路径"


def analyze_transform_path(
    chart_data: Dict[str, Any],
    start_palace: Optional[str] = None,
    transform_type: Optional[TransformPathType] = None
) -> TransformPathAnalysis:
    """
    分析飞化路径

    飞化类型：
    - 禄转忌：本宫化禄→忌入某宫
    - 忌转忌：本宫化忌→忌入某宫，再从该宫化忌
    - 追禄：忌入某宫后，该宫再化禄（同星曜）
    - 追权：忌入某宫后，该宫再化权（同星曜）
    - 追忌：禄入某宫后，该宫再化忌（非必同星曜）

    Args:
        chart_data: 命盘数据，包含：
            - year_stem: 出生年干
            - palace_stars: 宫位星曜数据，格式: {宫位名: [星曜列表]}
        start_palace: 起始宫位（可选，不指定则分析所有宫位）
        transform_type: 飞化类型（可选，不指定则分析所有类型）

    Returns:
        飞化路径分析结果
    """
    year_stem = chart_data.get("year_stem", "")
    palace_stars = chart_data.get("palace_stars", {})

    if not year_stem:
        return TransformPathAnalysis(year_stem=year_stem, summary="缺少年干信息")

    # 获取四化规则
    transform_rules = get_transform_rules()

    # 构建宫位四化映射表
    palace_transform_map = _build_palace_transform_map(palace_stars, transform_rules, year_stem)

    # 获取该年干的四化星
    transforms = transform_rules.get(year_stem, {})
    year_lu_star = transforms.get("禄", "")
    year_quan_star = transforms.get("权", "")
    year_ke_star = transforms.get("科", "")
    year_ji_star = transforms.get("忌", "")

    all_paths: List[TransformPath] = []
    lu_zhuan_ji_paths: List[TransformPath] = []
    ji_zhuan_ji_paths: List[TransformPath] = []
    zhui_lu_paths: List[TransformPath] = []
    zhui_quan_paths: List[TransformPath] = []
    zhui_ji_paths: List[TransformPath] = []

    # 分析禄转忌：本宫化禄→忌入某宫
    if year_lu_star and (transform_type is None or transform_type == TransformPathType.LU_ZHUAN_JI):
        # 找到化禄的宫位
        lu_palace = _find_transform_star_palace(palace_transform_map, year_lu_star)
        if lu_palace:
            # 该禄宫是否还有忌
            if lu_palace in palace_transform_map:
                lu_pt = palace_transform_map[lu_palace]
                if lu_pt.has_transform(TransformType.HUA_JI):
                    ji_star_transform = lu_pt.get_transform(TransformType.HUA_JI)
                    if ji_star_transform:
                        # 构建禄转忌路径
                        path = TransformPath(
                            path_type=TransformPathType.LU_ZHUAN_JI,
                            start_palace=lu_palace,
                            steps=[
                                TransformPathStep(
                                    from_palace=lu_palace,
                                    to_palace=lu_palace,
                                    transform_type=TransformType.HUA_LU,
                                    star_name=year_lu_star,
                                    description=f"{lu_palace}化{year_lu_star}禄"
                                ),
                                TransformPathStep(
                                    from_palace=lu_palace,
                                    to_palace="目标宫位",
                                    transform_type=TransformType.HUA_JI,
                                    star_name=ji_star_transform.star_name,
                                    description=f"{lu_palace}再化{ji_star_transform.star_name}忌"
                                )
                            ],
                            interpretation=_interpret_lu_zhuan_ji
                        )
                        all_paths.append(path)
                        lu_zhuan_ji_paths.append(path)

    # 分析忌转忌：本宫化忌→忌入某宫，再从该宫化忌
    if year_ji_star and (transform_type is None or transform_type == TransformPathType.JI_ZHUAN_JI):
        # 找到化忌的宫位
        ji_palace = _find_transform_star_palace(palace_transform_map, year_ji_star)
        if ji_palace:
            # 查找该忌宫化忌入的宫位
            if ji_palace in palace_transform_map:
                ji_pt = palace_transform_map[ji_palace]
                if ji_pt.has_transform(TransformType.HUA_JI):
                    # 二度转忌
                    ji2_star_transform = ji_pt.get_transform(TransformType.HUA_JI)
                    if ji2_star_transform:
                        path = TransformPath(
                            path_type=TransformPathType.JI_ZHUAN_JI,
                            start_palace=ji_palace,
                            steps=[
                                TransformPathStep(
                                    from_palace=ji_palace,
                                    to_palace="目标宫位",
                                    transform_type=TransformType.HUA_JI,
                                    star_name=year_ji_star,
                                    description=f"{ji_palace}化{year_ji_star}忌"
                                ),
                                TransformPathStep(
                                    from_palace=ji_palace,
                                    to_palace="第二目标宫位",
                                    transform_type=TransformType.HUA_JI,
                                    star_name=ji2_star_transform.star_name,
                                    description=f"{ji_palace}再化{ji2_star_transform.star_name}忌"
                                )
                            ],
                            sequence_count=2,
                            interpretation=_interpret_ji_zhuan_ji
                        )
                        all_paths.append(path)
                        ji_zhuan_ji_paths.append(path)

    # 分析追禄：忌入某宫后，该宫再化禄（同星曜）
    if year_ji_star and (transform_type is None or transform_type == TransformPathType.ZHUI_LU):
        # 查找化忌的宫位
        ji_palace = _find_transform_star_palace(palace_transform_map, year_ji_star)
        if ji_palace:
            # 该宫是否有禄（同星曜检查）
            if ji_palace in palace_transform_map:
                ji_pt = palace_transform_map[ji_palace]
                if ji_pt.has_transform(TransformType.HUA_LU):
                    lu_star_transform = ji_pt.get_transform(TransformType.HUA_LU)
                    if lu_star_transform:
                        is_same = lu_star_transform.star_name == year_ji_star
                        path = TransformPath(
                            path_type=TransformPathType.ZHUI_LU,
                            start_palace=ji_palace,
                            steps=[
                                TransformPathStep(
                                    from_palace=ji_palace,
                                    to_palace=ji_palace,
                                    transform_type=TransformType.HUA_JI,
                                    star_name=year_ji_star,
                                    is_same_star=True,
                                    description=f"{ji_palace}化{year_ji_star}忌"
                                ),
                                TransformPathStep(
                                    from_palace=ji_palace,
                                    to_palace=ji_palace,
                                    transform_type=TransformType.HUA_LU,
                                    star_name=lu_star_transform.star_name,
                                    is_same_star=is_same,
                                    description=f"{ji_palace}再化{lu_star_transform.star_name}禄"
                                )
                            ],
                            interpretation=lambda p: _interpret_zhui_lu(p, is_same)
                        )
                        all_paths.append(path)
                        zhui_lu_paths.append(path)

    # 分析追权：忌入某宫后，该宫再化权（同星曜）
    if year_ji_star and (transform_type is None or transform_type == TransformPathType.ZHUI_QUAN):
        ji_palace = _find_transform_star_palace(palace_transform_map, year_ji_star)
        if ji_palace:
            if ji_palace in palace_transform_map:
                ji_pt = palace_transform_map[ji_palace]
                if ji_pt.has_transform(TransformType.HUA_QUAN):
                    quan_star_transform = ji_pt.get_transform(TransformType.HUA_QUAN)
                    if quan_star_transform:
                        is_same = quan_star_transform.star_name == year_ji_star
                        path = TransformPath(
                            path_type=TransformPathType.ZHUI_QUAN,
                            start_palace=ji_palace,
                            steps=[
                                TransformPathStep(
                                    from_palace=ji_palace,
                                    to_palace=ji_palace,
                                    transform_type=TransformType.HUA_JI,
                                    star_name=year_ji_star,
                                    is_same_star=True,
                                    description=f"{ji_palace}化{year_ji_star}忌"
                                ),
                                TransformPathStep(
                                    from_palace=ji_palace,
                                    to_palace=ji_palace,
                                    transform_type=TransformType.HUA_QUAN,
                                    star_name=quan_star_transform.star_name,
                                    is_same_star=is_same,
                                    description=f"{ji_palace}再化{quan_star_transform.star_name}权"
                                )
                            ],
                            interpretation=lambda p: _interpret_zhui_quan(p, is_same)
                        )
                        all_paths.append(path)
                        zhui_quan_paths.append(path)

    # 分析追忌：禄入某宫后，该宫再化忌（非必同星曜）
    if year_lu_star and (transform_type is None or transform_type == TransformPathType.ZHUI_JI):
        lu_palace = _find_transform_star_palace(palace_transform_map, year_lu_star)
        if lu_palace:
            if lu_palace in palace_transform_map:
                lu_pt = palace_transform_map[lu_palace]
                if lu_pt.has_transform(TransformType.HUA_JI):
                    ji_star_transform = lu_pt.get_transform(TransformType.HUA_JI)
                    if ji_star_transform:
                        is_same = ji_star_transform.star_name == year_lu_star
                        path = TransformPath(
                            path_type=TransformPathType.ZHUI_JI,
                            start_palace=lu_palace,
                            steps=[
                                TransformPathStep(
                                    from_palace=lu_palace,
                                    to_palace=lu_palace,
                                    transform_type=TransformType.HUA_LU,
                                    star_name=year_lu_star,
                                    is_same_star=True,
                                    description=f"{lu_palace}化{year_lu_star}禄"
                                ),
                                TransformPathStep(
                                    from_palace=lu_palace,
                                    to_palace=lu_palace,
                                    transform_type=TransformType.HUA_JI,
                                    star_name=ji_star_transform.star_name,
                                    is_same_star=is_same,
                                    description=f"{lu_palace}再化{ji_star_transform.star_name}忌"
                                )
                            ],
                            interpretation=lambda p: _interpret_zhui_ji(p, is_same)
                        )
                        all_paths.append(path)
                        zhui_ji_paths.append(path)

    # 生成总结
    summary_parts = []
    if lu_zhuan_ji_paths:
        summary_parts.append(f"发现{len(lu_zhuan_ji_paths)}条禄转忌路径")
    if ji_zhuan_ji_paths:
        summary_parts.append(f"发现{len(ji_zhuan_ji_paths)}条忌转忌路径")
    if zhui_lu_paths:
        summary_parts.append(f"发现{len(zhui_lu_paths)}条追禄路径")
    if zhui_quan_paths:
        summary_parts.append(f"发现{len(zhui_quan_paths)}条追权路径")
    if zhui_ji_paths:
        summary_parts.append(f"发现{len(zhui_ji_paths)}条追忌路径")

    summary = f"{year_stem}年干四化飞化路径分析。{'；'.join(summary_parts) if summary_parts else '未发现明显的飞化路径。'}"

    return TransformPathAnalysis(
        year_stem=year_stem,
        paths=all_paths,
        lu_zhuan_ji_paths=lu_zhuan_ji_paths,
        ji_zhuan_ji_paths=ji_zhuan_ji_paths,
        zhui_lu_paths=zhui_lu_paths,
        zhui_quan_paths=zhui_quan_paths,
        zhui_ji_paths=zhui_ji_paths,
        summary=summary
    )


def generate_transform_path_diagram(
    analysis: TransformPathAnalysis,
    include_interpretation: bool = True
) -> str:
    """
    生成飞化路径图

    Args:
        analysis: 飞化路径分析结果
        include_interpretation: 是否包含解释

    Returns:
        飞化路径图的文本表示
    """
    lines = []
    lines.append(f"【{analysis.year_stem}年干飞化路径图】")
    lines.append("")
    lines.append("=" * 50)

    if not analysis.paths:
        lines.append("未发现飞化路径")
        return "\n".join(lines)

    # 禄转忌
    if analysis.lu_zhuan_ji_paths:
        lines.append("【禄转忌】禄是因，忌是果")
        for i, path in enumerate(analysis.lu_zhuan_ji_paths, 1):
            lines.append(f"  {i}. {path.steps[0].description}")
            lines.append(f"     → {path.steps[1].description}")
            if include_interpretation and path.interpretation:
                interpret = path.interpretation(path) if callable(path.interpretation) else path.interpretation
                lines.append(f"     解释: {interpret}")
        lines.append("")

    # 忌转忌
    if analysis.ji_zhuan_ji_paths:
        lines.append("【忌转忌】连续化忌，深入因果")
        for i, path in enumerate(analysis.ji_zhuan_ji_paths, 1):
            for step in path.steps:
                lines.append(f"  {i}. {step.description}")
                lines.append("     ↓")
            if include_interpretation:
                interpret = path.interpretation(path) if callable(path.interpretation) else path.interpretation
                lines.append(f"     解释: {interpret}")
        lines.append("")

    # 追禄
    if analysis.zhui_lu_paths:
        lines.append("【追禄】禄随忌走（同星曜）")
        for i, path in enumerate(analysis.zhui_lu_paths, 1):
            lines.append(f"  {i}. {path.steps[0].description}")
            lines.append(f"     → {path.steps[1].description}")
            if include_interpretation:
                interpret = path.interpretation(path) if callable(path.interpretation) else path.interpretation
                lines.append(f"     解释: {interpret}")
        lines.append("")

    # 追权
    if analysis.zhui_quan_paths:
        lines.append("【追权】权随忌走（同星曜）")
        for i, path in enumerate(analysis.zhui_quan_paths, 1):
            lines.append(f"  {i}. {path.steps[0].description}")
            lines.append(f"     → {path.steps[1].description}")
            if include_interpretation:
                interpret = path.interpretation(path) if callable(path.interpretation) else path.interpretation
                lines.append(f"     解释: {interpret}")
        lines.append("")

    # 追忌
    if analysis.zhui_ji_paths:
        lines.append("【追忌】忌随禄走（非必同星曜）")
        for i, path in enumerate(analysis.zhui_ji_paths, 1):
            lines.append(f"  {i}. {path.steps[0].description}")
            lines.append(f"     → {path.steps[1].description}")
            if include_interpretation:
                interpret = path.interpretation(path) if callable(path.interpretation) else path.interpretation
                lines.append(f"     解释: {interpret}")
        lines.append("")

    lines.append("=" * 50)
    lines.append("")
    lines.append(f"总结: {analysis.summary}")

    return "\n".join(lines)


# ============ 成住坏空四化周期分析 ============

def _determine_strength(palaces: List[str], palace_stars: Dict[str, List[str]]) -> str:
    """
    判断成住坏空各阶段的强弱

    根据落入宫位的数量和重要性判断强弱
    """
    if not palaces:
        return "弱"

    # 命宫、官禄宫、财帛宫为强宫
    strong_palaces = {"命宫", "官禄宫", "财帛宫"}
    # 迁移宫、交友宫、夫妻宫为中宫
    medium_palaces = {"迁移宫", "交友宫", "夫妻宫"}

    strong_count = sum(1 for p in palaces if p in strong_palaces)
    medium_count = sum(1 for p in palaces if p in medium_palaces)

    if strong_count >= 2:
        return "强"
    elif strong_count == 1 and medium_count >= 1:
        return "强"
    elif medium_count >= 2:
        return "中"
    elif medium_count == 1 and palaces:
        return "中"
    else:
        return "弱"


def _build_cycle_stage(
    cycle_type: TransformCycleType,
    transform_type: TransformType,
    palace_stars: Dict[str, List[str]],
    year_transforms: Dict[str, str]
) -> CycleStage:
    """
    构建单个成住坏空阶段

    Args:
        cycle_type: 周期类型
        transform_type: 对应四化类型
        palace_stars: 宫位星曜数据
        year_transforms: 年干四化

    Returns:
        CycleStage对象
    """
    # 获取该四化对应的星曜
    transform_star = year_transforms.get(
        "禄" if transform_type == TransformType.HUA_LU else
        "权" if transform_type == TransformType.HUA_QUAN else
        "科" if transform_type == TransformType.HUA_KE else "忌"
    , "")

    # 查找该星曜落入的宫位
    palaces: List[str] = []
    stars: List[str] = []

    if transform_star and palace_stars:
        for palace_name, star_list in palace_stars.items():
            if transform_star in star_list:
                palaces.append(palace_name)
                if transform_star not in stars:
                    stars.append(transform_star)

    # 判断强弱
    strength = _determine_strength(palaces, palace_stars)

    # 获取解释
    cycle_info = CYCLE_INTERPRETATIONS.get(cycle_type, {})
    transform_interpretation = ""

    if transform_star in TRANSFORM_INTERPRETATIONS.get(transform_type.value, {}):
        transform_interpretation = TRANSFORM_INTERPRETATIONS[transform_type.value][transform_star]

    interpretation = f"{cycle_info.get('description', '')} {transform_interpretation}"

    return CycleStage(
        cycle_type=cycle_type,
        transform_type=transform_type,
        palaces=palaces,
        stars=stars,
        strength=strength,
        interpretation=interpretation
    )


def _determine_balance(cheng: CycleStage, zhu: CycleStage, huai: CycleStage, kong: CycleStage) -> tuple:
    """
    判断成住坏空四阶段的平衡性

    Returns:
        (dominant_cycle, weakest_cycle, balance_description)
    """
    strength_order = {"强": 3, "中": 2, "弱": 1}

    cycles = [
        (TransformCycleType.CHENG, cheng),
        (TransformCycleType.ZHU, zhu),
        (TransformCycleType.HUAI, huai),
        (TransformCycleType.KONG, kong)
    ]

    # 计算各阶段得分
    scores = []
    for cycle_type, stage in cycles:
        if stage is None:
            scores.append((cycle_type, 0))
        else:
            score = strength_order.get(stage.strength, 1) + (len(stage.palaces) * 0.5)
            scores.append((cycle_type, score))

    # 排序
    scores.sort(key=lambda x: x[1], reverse=True)

    dominant = scores[0][0] if scores[0][1] > 0 else None
    weakest = scores[-1][0] if scores[-1][1] == 0 else None

    # 判断平衡性
    strong_count = sum(1 for _, s in scores if s >= 3)
    if strong_count >= 3:
        balance = "均衡"
    elif strong_count == 2:
        balance = "偏向"
    else:
        balance = "失衡"

    return dominant, weakest, balance


def _generate_cycle_overall_interpretation(
    year_stem: str,
    cheng: CycleStage,
    zhu: CycleStage,
    huai: CycleStage,
    kong: CycleStage,
    dominant: TransformCycleType,
    weakest: TransformCycleType,
    balance: str
) -> str:
    """生成成住坏空总体解释"""
    lines = []

    lines.append(f"【{year_stem}年干成住坏空四化周期分析】")
    lines.append("")

    lines.append("一、四化周期分布")
    for stage in [cheng, zhu, huai, kong]:
        if stage:
            cycle_name = stage.cycle_type.value
            transform_name = stage.transform_type.value
            strength = stage.strength
            palaces_str = "、".join(stage.palaces) if stage.palaces else "无"
            stars_str = "、".join(stage.stars) if stage.stars else "无"

            lines.append(f"  {cycle_name}（{transform_name}）：强度{strength}，落{palaces_str}，星曜{stars_str}")

    lines.append("")
    lines.append("二、周期特征")

    # 分析各阶段特点
    if cheng and cheng.strength == "强":
        lines.append("  成（化禄）强：福德聚集，缘起旺盛，早年运势佳，有意外收获的可能")

    if zhu and zhu.strength == "强":
        lines.append("  住（化权）强：权力欲强，事业心重，中年期成就突出，有掌控欲")

    if huai and huai.strength == "强":
        lines.append("  坏（化科）强：名声关注，学术运势佳，但有衰减之象，体面与是非并存")

    if kong and kong.strength == "强":
        lines.append("  空（化忌）强：阻碍较多，周期末尾或晚年有重大转变，须注意人际关系")

    # 分析最弱
    if weakest:
        weakest_info = CYCLE_INTERPRETATIONS.get(weakest, {})
        lines.append(f"  最弱为{weakest.value}（{weakest_info.get('meaning', '')}），该方面运势需加强关注")

    lines.append("")
    lines.append("三、总体评价")

    # 平衡性评价
    if balance == "均衡":
        lines.append("  四化周期分布均衡，命运走势平稳，各阶段皆有发力之时")
    elif balance == "偏向":
        lines.append(f"  四化周期分布偏向{dominant.value if dominant else '某'}阶段，命运有明确重点")
    else:
        lines.append("  四化周期分布失衡，命运起伏较大，需注意调配")

    # 综合评价
    if dominant == TransformCycleType.CHENG:
        lines.append("  主导周期为成，早年运势佳，宜把握机遇积累福德")
    elif dominant == TransformCycleType.ZHU:
        lines.append("  主导周期为住，中年强势，宜积极进取成就事业")
    elif dominant == TransformCycleType.HUAI:
        lines.append("  主导周期为坏，学术名声为重，宜守成持稳")
    elif dominant == TransformCycleType.KONG:
        lines.append("  主导周期为空，周期转换期，宜沉淀准备新一轮周期")

    return "\n".join(lines)


def analyze_transform_cycle(chart_data: Dict[str, Any]) -> CycleAnalysis:
    """
    分析成住坏空四化周期

    成住坏空是佛学宇宙观中的四劫，对应紫微斗数四化：
    - 成 → 化禄（缘起）
    - 住 → 化权（持续）
    - 坏 → 化科（衰减）
    - 空 → 化忌（结束）

    Args:
        chart_data: 命盘数据，包含：
            - year_stem: 出生年干
            - palace_stars: 宫位星曜数据，格式: {宫位名: [星曜列表]}

    Returns:
        成住坏空周期分析结果
    """
    year_stem = chart_data.get("year_stem", "")
    palace_stars = chart_data.get("palace_stars", {})

    if not year_stem:
        return CycleAnalysis(year_stem=year_stem, overall_interpretation="缺少年干信息")

    # 获取四化规则
    transform_rules = get_transform_rules()
    year_transforms = transform_rules.get(year_stem, {})

    # 构建四个阶段
    cheng = _build_cycle_stage(
        TransformCycleType.CHENG,
        TransformType.HUA_LU,
        palace_stars,
        year_transforms
    )

    zhu = _build_cycle_stage(
        TransformCycleType.ZHU,
        TransformType.HUA_QUAN,
        palace_stars,
        year_transforms
    )

    huai = _build_cycle_stage(
        TransformCycleType.HUAI,
        TransformType.HUA_KE,
        palace_stars,
        year_transforms
    )

    kong = _build_cycle_stage(
        TransformCycleType.KONG,
        TransformType.HUA_JI,
        palace_stars,
        year_transforms
    )

    # 判断平衡性
    dominant, weakest, balance = _determine_balance(cheng, zhu, huai, kong)

    # 生成总体解释
    overall_interpretation = _generate_cycle_overall_interpretation(
        year_stem, cheng, zhu, huai, kong, dominant, weakest, balance
    )

    return CycleAnalysis(
        year_stem=year_stem,
        cheng=cheng,
        zhu=zhu,
        huai=huai,
        kong=kong,
        dominant_cycle=dominant,
        weakest_cycle=weakest,
        cycle_balance=balance,
        overall_interpretation=overall_interpretation
    )


def generate_cycle_diagram(analysis: CycleAnalysis) -> str:
    """
    生成成住坏空周期分析图

    Args:
        analysis: 周期分析结果

    Returns:
        周期分析图的文本表示
    """
    return analysis.overall_interpretation


# ============ LLM增强分析 ============

class LLMTransformAnalyzer:
    """四化分析LLM增强器"""

    def __init__(self, chart_data: Any = None):
        self.chart = chart_data

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度四化分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import TRANSFORM_SYSTEM_PROMPT, build_transform_user_prompt

        # 构建提示词
        user_prompt = build_transform_user_prompt(self.chart, question)

        messages = [
            {"role": "system", "content": TRANSFORM_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature, cache=False)

        return result

    def analyze_with_llm_sync(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """同步版本的LLM分析"""
        import asyncio
        return asyncio.run(self.analyze_with_llm(question, temperature))

    async def generate_text_report(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """生成文本格式的LLM分析报告"""
        from .llm_prompts import format_analysis_as_text
        result = await self.analyze_with_llm(question, temperature)
        return format_analysis_as_text(result)


async def llm_analyze_transforms(
    chart_data: Any,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用LLM分析命盘四化

    Args:
        chart_data: 命盘数据
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLMTransformAnalyzer(chart_data)
    return await analyzer.analyze_with_llm(question)


@cached_chart_analysis("transforms", ttl=3600)
def llm_analyze_transforms_sync(
    chart_data: Any,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """同步版本的LLM四化分析"""
    import asyncio
    return asyncio.run(llm_analyze_transforms(chart_data, question))
