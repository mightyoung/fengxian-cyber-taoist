"""
格局分析智能体
识别紫微斗数命盘中的各种格局
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import json
import os

from .pattern_constants import (
    PALACE_NAMES as CONSTANT_PALACE_NAMES,
    TRANSFORM_TYPES as CONSTANT_TRANSFORM_TYPES,
    MAJOR_STARS as CONSTANT_MAJOR_STARS,
    MODIFIER_STARS as CONSTANT_MODIFIER_STARS,
    SINI_STARS as CONSTANT_SINI_STARS,
    EMPTY_STARS as CONSTANT_EMPTY_STARS,
)
from .pattern_types import PatternCategory, PatternQuality, Pattern, PatternAnalysis
from .cache_decorator import cached_chart_analysis


# 十二宫位名称（完整列表）
PALACE_NAMES = CONSTANT_PALACE_NAMES

# 宫位简称到全称的映射（用于精确匹配）
PALACE_ALIASES: Dict[str, str] = {
    "命": "命宫",
    "兄": "兄弟宫",
    "夫": "夫妻宫",
    "妻": "夫妻宫",
    "子": "子女宫",
    "财": "财帛宫",
    "疾": "疾厄宫",
    "迁": "迁移宫",
    "仆": "仆役宫",
    "友": "仆役宫",
    "官": "官禄宫",
    "禄": "官禄宫",
    "田": "田宅宫",
    "宅": "田宅宫",
    "福": "福德宫",
    "父": "父母宫",
    "母": "父母宫"
}

# 化曜类型（精确匹配）
TRANSFORM_TYPES = CONSTANT_TRANSFORM_TYPES


def parse_transform_star(star: str) -> Optional[Tuple[str, str]]:
    """
    解析化曜，返回 (原星, 化曜类型)
    例如: "廉贞化禄" -> ("廉贞", "化禄")
          "紫微化忌" -> ("紫微", "化忌")
    """
    for transform in TRANSFORM_TYPES:
        if star.endswith(transform):
            base_star = star[:-len(transform)]
            if base_star:
                return (base_star, transform)
    return None


def is_transform_star(star: str) -> bool:
    """判断是否是化曜"""
    return parse_transform_star(star) is not None


def get_transform_type(star: str) -> Optional[str]:
    """获取化曜类型"""
    parsed = parse_transform_star(star)
    return parsed[1] if parsed else None


def get_base_star(star: str) -> Optional[str]:
    """获取化曜的本星"""
    parsed = parse_transform_star(star)
    return parsed[0] if parsed else None


def normalize_palace_name(palace: str) -> Optional[str]:
    """
    规范化宫位名称，返回标准宫位名
    例如: "安命" -> None (不匹配)
          "命宫" -> "命宫"
          "命" -> "命宫"
    """
    # 首先检查是否是完整宫位名
    if palace in PALACE_NAMES:
        return palace
    # 检查是否是简称
    if palace in PALACE_ALIASES:
        return PALACE_ALIASES[palace]
    return None


def is_palace_match(palace_key: str, pattern: str) -> bool:
    """
    检查宫位是否匹配模式
    - 精确匹配: "命宫" 匹配 "命宫"
    - 不匹配: "安命" 不匹配 "命宫"
    - 支持简称: "命" -> "命宫"
    """
    normalized = normalize_palace_name(palace_key)
    if not normalized:
        return False
    # 精确匹配模式
    return pattern in normalized or normalized in pattern


def extract_stars_by_palace(palace_stars: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    """
    提取每个宫位的星曜集合（保留宫位信息）
    返回: {宫位名: {星曜集合}}
    """
    result = {}
    for palace, stars in palace_stars.items():
        palace_set: Set[str] = set()
        for star in stars:
            if isinstance(star, dict):
                star_name = star.get("name", "")
                if star_name:
                    palace_set.add(star_name)
            elif isinstance(star, str):
                palace_set.add(star)
        result[palace] = palace_set
    return result


def extract_all_stars(palace_stars: Dict[str, List[str]]) -> Set[str]:
    """
    提取所有星曜（不区分宫位）
    用于检查星曜是否存在
    """
    all_stars: Set[str] = set()
    for palace, stars in palace_stars.items():
        for star in stars:
            if isinstance(star, dict):
                star_name = star.get("name", "")
                if star_name:
                    all_stars.add(star_name)
            elif isinstance(star, str):
                all_stars.add(star)
    return all_stars


def extract_transform_stars(palace_stars: Dict[str, List[str]]) -> Dict[str, List[Tuple[str, str]]]:
    """
    提取所有化曜，按宫位分类
    返回: {宫位名: [(本星, 化曜类型), ...]}
    """
    result: Dict[str, List[Tuple[str, str]]] = {}
    for palace, stars in palace_stars.items():
        transforms = []
        for star in stars:
            star_str = star if isinstance(star, str) else star.get("name", "")
            if star_str:
                parsed = parse_transform_star(star_str)
                if parsed:
                    transforms.append(parsed)
        if transforms:
            result[palace] = transforms
    return result


def check_stars_in_palace(
    palace_stars_dict: Dict[str, Set[str]],
    palace_pattern: str,
    required_stars: List[str]
) -> bool:
    """
    检查特定宫位是否包含所需星曜
    palace_pattern: 宫位模式（如 "命宫"、"寅申宫"）
    """
    # 规范化宫位模式
    normalized_pattern = normalize_palace_name(palace_pattern)
    if not normalized_pattern:
        # 可能是复合宫位如 "寅申宫"
        normalized_pattern = palace_pattern

    # 遍历所有宫位查找匹配
    for palace, stars in palace_stars_dict.items():
        palace_normalized = normalize_palace_name(palace)
        if not palace_normalized:
            continue

        # 检查宫位是否匹配模式
        is_match = False
        if "至" in palace_pattern or "同" in palace_pattern:
            # 特殊匹配：前后夹命、三方四正等
            is_match = palace_pattern in palace_normalized or palace_normalized in palace_pattern
        elif "宫" in palace_pattern:
            # 精确宫位匹配
            is_match = palace_normalized == palace_pattern or palace_pattern in palace_normalized
        else:
            # 简称匹配
            is_match = palace_pattern in palace_normalized

        if is_match:
            # 检查星曜是否都在该宫位
            if all(star in stars for star in required_stars):
                return True
    return False


def check_transform_in_palace(
    transform_dict: Dict[str, List[Tuple[str, str]]],
    palace_pattern: str,
    required_transforms: List[str]
) -> bool:
    """
    检查特定宫位是否包含所需化曜
    """
    normalized_pattern = normalize_palace_name(palace_pattern)
    if not normalized_pattern:
        normalized_pattern = palace_pattern

    for palace, transforms in transform_dict.items():
        palace_normalized = normalize_palace_name(palace)
        if not palace_normalized:
            continue

        is_match = False
        if "宫" in palace_pattern:
            is_match = palace_normalized == palace_pattern or palace_pattern in palace_normalized
        else:
            is_match = palace_pattern in palace_normalized

        if is_match:
            transform_types = [t[1] for t in transforms]
            if all(t in transform_types for t in required_transforms):
                return True
    return False




# 常用星曜列表（十四正曜）
MAJOR_STARS = CONSTANT_MAJOR_STARS

# 辅星列表
MODIFIER_STARS = CONSTANT_MODIFIER_STARS

# 煞星列表
SINI_STARS = CONSTANT_SINI_STARS

# 空曜列表
EMPTY_STARS = CONSTANT_EMPTY_STARS


def load_pattern_rules() -> Dict[str, Any]:
    """
    从规则文件加载格局规则

    Returns:
        格局规则字典
    """
    rules_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "..",
        "data_source", "mlx", "data", "knowledge", "rules",
        "pattern-rules.json"
    )

    if os.path.exists(rules_path):
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {}


def parse_pattern_category(category: str) -> PatternCategory:
    """解析格局类别"""
    if "吉" in category:
        return PatternCategory.AUSPICIOUS
    elif "凶" in category:
        return PatternCategory.INAUSPICIOUS
    else:
        return PatternCategory.NEUTRAL


def parse_pattern_quality(quality: str) -> PatternQuality:
    """解析格局等级"""
    try:
        return PatternQuality(quality)
    except ValueError:
        return PatternQuality.B


class PatternAgent:
    """
    格局分析智能体

    识别命盘中的各种格局，
    分析格局强弱和完整性
    """

    def __init__(self, chart_data: Any = None):
        """
        初始化格局分析智能体

        Args:
            chart_data: 命盘数据，包含宫位星曜信息
        """
        self.chart = chart_data
        self.pattern_rules = load_pattern_rules()
        self._init_patterns()

    def _init_patterns(self):
        """初始化格局列表"""
        self.patterns: List[Pattern] = []

        if not self.pattern_rules:
            return

        # 加载吉格
        for pattern_data in self.pattern_rules.get("auspicious_patterns", []):
            pattern = Pattern(
                id=pattern_data.get("id", ""),
                name=pattern_data.get("name", ""),
                name_en=pattern_data.get("name_en", ""),
                category=parse_pattern_category(pattern_data.get("category", "吉格")),
                quality=parse_pattern_quality(pattern_data.get("quality", "B")),
                description=pattern_data.get("description", ""),
                source=pattern_data.get("source", ""),
                formation_conditions=pattern_data.get("formation_conditions", {}),
                judgment_rules=pattern_data.get("judgment_rules", {}),
                analysis_points=pattern_data.get("analysis_points", []),
                effects=pattern_data.get("effects", {})
            )
            self.patterns.append(pattern)

        # 加载凶格
        for pattern_data in self.pattern_rules.get("inauspicious_patterns", []):
            pattern = Pattern(
                id=pattern_data.get("id", ""),
                name=pattern_data.get("name", ""),
                name_en=pattern_data.get("name_en", ""),
                category=parse_pattern_category(pattern_data.get("category", "凶格")),
                quality=parse_pattern_quality(pattern_data.get("quality", "B")),
                description=pattern_data.get("description", ""),
                source=pattern_data.get("source", ""),
                formation_conditions=pattern_data.get("formation_conditions", {}),
                judgment_rules=pattern_data.get("judgment_rules", {}),
                analysis_points=pattern_data.get("analysis_points", []),
                effects=pattern_data.get("effects", {})
            )
            self.patterns.append(pattern)

        # 加载中性格
        for pattern_data in self.pattern_rules.get("neutral_patterns", []):
            pattern = Pattern(
                id=pattern_data.get("id", ""),
                name=pattern_data.get("name", ""),
                name_en=pattern_data.get("name_en", ""),
                category=parse_pattern_category(pattern_data.get("category", "中性格")),
                quality=parse_pattern_quality(pattern_data.get("quality", "B")),
                description=pattern_data.get("description", ""),
                source=pattern_data.get("source", ""),
                formation_conditions=pattern_data.get("formation_conditions", {}),
                judgment_rules=pattern_data.get("judgment_rules", {}),
                analysis_points=pattern_data.get("analysis_points", []),
                effects=pattern_data.get("effects", {})
            )
            self.patterns.append(pattern)

    def identify_patterns(self, palace_stars: Dict[str, List[str]],
                          year_stem: str = "") -> List[Pattern]:
        """
        识别命盘中的格局

        Args:
            palace_stars: 宫位星曜数据，格式: {宫位名: [星曜列表]}
            year_stem: 出生年干

        Returns:
            匹配到的格局列表
        """
        matched_patterns: List[Pattern] = []

        for pattern in self.patterns:
            if self._match_pattern(pattern, palace_stars, year_stem):
                matched_patterns.append(pattern)

        return matched_patterns

    def _match_pattern(self, pattern: Pattern, palace_stars: Dict[str, List[str]],
                       year_stem: str) -> bool:
        """
        匹配单个格局

        关键修复：
        1. 格局判断必须考虑宫位（紫微在命宫 vs 紫微在田宅宫是不同格局）
        2. 化曜检测需要精确匹配化禄/化权/化科/化忌
        3. 宫位匹配需要精确（如"命宫"完整匹配，不能匹配"安命"）
        """
        conditions = pattern.formation_conditions
        matched_conditions: List[str] = []
        failed_conditions: List[str] = []

        # ============ 提取宫位星曜数据（保留宫位信息）============
        palace_stars_dict = extract_stars_by_palace(palace_stars)
        all_stars_set = extract_all_stars(palace_stars)
        transform_dict = extract_transform_stars(palace_stars)

        # 获取命宫星曜
        ming_gong_stars = palace_stars_dict.get("命宫", set())

        # ============ 检查主星条件（区分宫位）============
        # 对于需要特定宫位的格局，检查星曜是否在正确宫位
        primary_stars = conditions.get("primary_stars", conditions.get("required_stars", []))
        palace_condition = conditions.get("palace", "")
        location_condition = conditions.get("location", "")

        if primary_stars:
            # 如果有宫位要求，检查星曜是否在指定宫位
            if palace_condition or location_condition:
                # 检查主星是否在指定宫位
                palace_to_check = palace_condition or location_condition
                matched_in_palace = False

                for palace, stars in palace_stars_dict.items():
                    # 精确匹配宫位
                    palace_normalized = normalize_palace_name(palace)
                    location_normalized = normalize_palace_name(palace_to_check)

                    # 检查是否匹配
                    is_match = False
                    if palace_normalized and location_normalized:
                        is_match = palace_normalized == location_normalized
                    elif palace_to_check in palace:
                        is_match = True

                    if is_match:
                        # 检查该宫位是否包含所有主星
                        if all(star in stars for star in primary_stars):
                            matched_in_palace = True
                            matched_conditions.append(
                                f"主星{','.join(primary_stars)}在{ palace}宫"
                            )
                            break

                if not matched_in_palace:
                    failed_conditions.append(
                        f"主星{','.join(primary_stars)}不在{ palace_to_check}宫"
                    )
                    return False
            else:
                # 无宫位要求，只检查星曜是否存在
                primary_matched = all(star in all_stars_set for star in primary_stars)
                if primary_matched:
                    matched_conditions.append(f"主星{','.join(primary_stars)}齐全")
                else:
                    failed_conditions.append(f"主星{','.join(primary_stars)}不全")
                    return False

        # ============ 检查辅星条件 ============
        required_modifiers = conditions.get("required_modifiers", [])
        if required_modifiers:
            # 检查辅星是否存在于任何宫位
            modifier_matched = all(modifier in all_stars_set for modifier in required_modifiers)
            if modifier_matched:
                matched_conditions.append(f"辅星{','.join(required_modifiers)}齐全")
            else:
                failed_conditions.append(f"辅星不全")

        # ============ 检查第二组星曜 ============
        required_stars_2 = conditions.get("required_stars_2", [])
        if required_stars_2:
            star2_matched = any(star in all_stars_set for star in required_stars_2)
            if star2_matched:
                matched_conditions.append(f"有{','.join(required_stars_2)}之一")
            else:
                failed_conditions.append(f"缺少第二组星曜")

        # ============ 检查禁忌星曜 ============
        forbidden = conditions.get("forbidden", [])
        if forbidden:
            for fb in forbidden:
                if fb in all_stars_set:
                    failed_conditions.append(f"有禁忌{fb}")
                    return False

        # ============ 检查化曜条件（精确匹配）============
        required_transforms = conditions.get("required_transforms", [])
        if required_transforms:
            # 精确匹配化禄/化权/化科/化忌
            all_transforms: Set[str] = set()
            for palace, transforms in transform_dict.items():
                for base_star, transform_type in transforms:
                    all_transforms.add(transform_type)

            # 检查是否有所需的化曜
            transforms_found = [t for t in required_transforms if t in all_transforms]

            if transforms_found:
                matched_conditions.append(f"有化曜: {','.join(transforms_found)}")
            else:
                failed_conditions.append(f"缺少化曜: {','.join(required_transforms)}")

            # 额外检查：如果是特定化曜（如"贪狼化禄"），需要检查
            for transform in required_transforms:
                # 处理"星名化禄"格式
                if "化" in transform:
                    for palace, transforms in transform_dict.items():
                        for base_star, transform_type in transforms:
                            # 检查是否匹配 "X化Y" 格式
                            expected = f"{base_star}{transform_type}"
                            if expected == transform:
                                matched_conditions.append(f"{base_star}{transform_type}在{palace}")

        # ============ 检查宫位条件（精确匹配）============
        location = conditions.get("location", "")
        if location:
            location_matched = False
            matched_location = ""

            for palace in palace_stars_dict.keys():
                # 精确匹配宫位名（不是模糊匹配）
                if is_palace_match(palace, location):
                    location_matched = True
                    matched_location = palace
                    break
                # 处理特殊格式如"寅申宫"、"三方四正"等
                if location in palace or palace in location:
                    # 但要排除"安命"匹配"命宫"的情况
                    if normalize_palace_name(palace) is not None:
                        location_matched = True
                        matched_location = palace
                        break

            if location_matched:
                matched_conditions.append(f"位置符合{location}({matched_location})")
            else:
                failed_conditions.append(f"位置不符合{location}")

        # ============ 检查特定宫位（精确匹配）============
        if palace_condition:
            # 精确匹配
            if normalize_palace_name(palace_condition):
                # 使用规范化名称检查
                if any(
                    normalize_palace_name(p) == normalize_palace_name(palace_condition)
                    for p in palace_stars_dict.keys()
                ):
                    matched_conditions.append(f"在{palace_condition}宫")
                else:
                    return False
            else:
                # 非标准宫位（如"寅申宫"格式）
                if any(palace_condition in p for p in palace_stars_dict.keys()):
                    matched_conditions.append(f"在{palace_condition}宫")
                else:
                    return False

        # ============ 检查寅申宫等特殊要求 ============
        palace_requirement = conditions.get("palace_requirement", "")
        if palace_requirement:
            if "寅申宫" in palace_requirement:
                if "寅宫" in palace_stars_dict or "申宫" in palace_stars_dict:
                    matched_conditions.append("符合寅申宫要求")

        # ============ 检查特定结构（如同宫、三方会照等）============
        # 简化处理：检查是否有多颗星在同一宫位
        structures = conditions.get("structures", [])
        if structures:
            for struct in structures:
                if isinstance(struct, dict):
                    # 检查星曜是否同宫
                    struct_stars = struct.get("stars", [])
                    if struct_stars:
                        # 检查这些星是否同宫
                        for palace, stars in palace_stars_dict.items():
                            if all(s in stars for s in struct_stars):
                                matched_conditions.append(
                                    f"{','.join(struct_stars)}在{palace}同宫"
                                )
                                break

        # ============ 最终判定 ============
        # 如果有必须满足的条件但没有匹配成功，返回False
        must_satisfy = pattern.judgment_rules.get("must_satisfy", [])
        if must_satisfy and not matched_conditions:
            return False

        # 更新pattern的匹配状态
        if matched_conditions:
            pattern.matched = True
            pattern.match_details = "; ".join(matched_conditions)
            return True

        return False

    def analyze_patterns(self, palace_stars: Dict[str, List[str]],
                        year_stem: str = "") -> PatternAnalysis:
        """
        分析命盘格局

        Args:
            palace_stars: 宫位星曜数据
            year_stem: 出生年干

        Returns:
            格局分析结果
        """
        # 识别格局
        matched_patterns = self.identify_patterns(palace_stars, year_stem)

        # 分类
        auspicious = [p for p in matched_patterns
                     if p.category == PatternCategory.AUSPICIOUS]
        inauspicious = [p for p in matched_patterns
                       if p.category == PatternCategory.INAUSPICIOUS]
        neutral = [p for p in matched_patterns
                  if p.category == PatternCategory.NEUTRAL]

        # 按质量排序
        auspicious.sort(key=lambda x: self._quality_sort_key(x.quality), reverse=True)
        inauspicious.sort(key=lambda x: self._quality_sort_key(x.quality), reverse=True)

        # 生成解释
        interpretation = self._generate_interpretation(
            matched_patterns, auspicious, inauspicious, neutral
        )

        return PatternAnalysis(
            year_stem=year_stem,
            patterns=matched_patterns,
            auspicious_patterns=auspicious,
            inauspicious_patterns=inauspicious,
            neutral_patterns=neutral,
            interpretation=interpretation
        )

    def _quality_sort_key(self, quality: PatternQuality) -> int:
        """质量排序键"""
        mapping = {
            PatternQuality.A_PLUS: 5,
            PatternQuality.A: 4,
            PatternQuality.B_PLUS: 3,
            PatternQuality.B: 2,
            PatternQuality.C: 1
        }
        return mapping.get(quality, 0)

    def _generate_interpretation(self, patterns: List[Pattern],
                                auspicious: List[Pattern],
                                inauspicious: List[Pattern],
                                neutral: List[Pattern]) -> str:
        """生成格局解释"""
        lines = []

        lines.append("【命盘格局分析】")
        lines.append("")

        # 吉格
        if auspicious:
            lines.append("一、吉格")
            for p in auspicious:
                lines.append(f"  {p.name} ({p.quality.value})")
                lines.append(f"    {p.description}")
                if p.match_details:
                    lines.append(f"    匹配: {p.match_details}")
                if p.analysis_points:
                    lines.append(f"    分析: {p.analysis_points[0]}")
            lines.append("")

        # 凶格
        if inauspicious:
            lines.append("二、凶格")
            for p in inauspicious:
                lines.append(f"  {p.name} ({p.quality.value})")
                lines.append(f"    {p.description}")
                if p.match_details:
                    lines.append(f"    匹配: {p.match_details}")
            lines.append("")

        # 中性格
        if neutral:
            lines.append("三、中性格")
            for p in neutral:
                lines.append(f"  {p.name} ({p.quality.value})")
                lines.append(f"    {p.description}")
            lines.append("")

        # 总结
        lines.append("四、总体评价")
        total = len(patterns)

        if not patterns:
            lines.append("  未发现明显格局，需结合星曜组合综合论断。")
        else:
            lines.append(f"  共发现 {total} 个格局:")

            quality_counts = {"A+": 0, "A": 0, "B": 0, "C": 0}
            for p in patterns:
                q = p.quality.value
                if q in quality_counts:
                    quality_counts[q] += 1

            if quality_counts["A+"] > 0 or quality_counts["A"] > 0:
                lines.append("  格局配置良好，有望获得较大成就。")
            else:
                lines.append("  格局配置中等，需要后天努力弥补。")

            if inauspicious and len(inauspicious) > len(auspicious):
                lines.append("  注意化解凶格带来的负面影响。")
            elif auspicious and len(auspicious) > len(inauspicious):
                lines.append("  吉格占优，整体命运较为顺遂。")

        return "\n".join(lines)

    def get_all_patterns(self) -> List[Pattern]:
        """获取所有格局列表"""
        return self.patterns

    def get_patterns_by_category(self, category: PatternCategory) -> List[Pattern]:
        """获取指定类别的格局"""
        return [p for p in self.patterns if p.category == category]


def analyze_patterns(palace_stars: Dict[str, List[str]],
                    year_stem: str = "") -> PatternAnalysis:
    """
    快捷函数：分析命盘格局

    Args:
        palace_stars: 宫位星曜数据
        year_stem: 出生年干

    Returns:
        格局分析结果
    """
    agent = PatternAgent()
    return agent.analyze_patterns(palace_stars, year_stem)


# ============ LLM增强分析 ============

class LLMPatternAnalyzer:
    """格局分析LLM增强器"""

    def __init__(self, chart_data: Any = None):
        self.chart = chart_data

    def analyze_patterns(self, palace_stars: Dict[str, List[str]], year_stem: str = "") -> PatternAnalysis:
        """
        规则匹配格局分析

        Args:
            palace_stars: 宫位星曜数据
            year_stem: 出生年干

        Returns:
            格局分析结果
        """
        agent = PatternAgent()
        return agent.analyze_patterns(palace_stars, year_stem)

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度格局分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import PATTERN_SYSTEM_PROMPT, build_pattern_user_prompt

        # 构建提示词
        user_prompt = build_pattern_user_prompt(self.chart, question)

        messages = [
            {"role": "system", "content": PATTERN_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature)

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


async def llm_analyze_patterns(
    chart_data: Any,
    palace_stars: Optional[Dict[str, List[str]]] = None,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用LLM分析命盘格局

    Args:
        chart_data: 命盘数据
        palace_stars: 宫位星曜数据（可选，如果提供则进行规则匹配增强）
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLMPatternAnalyzer(chart_data)

    # 如果提供了 palace_stars，先进行规则匹配分析
    if palace_stars:
        year_stem = chart_data.get('birth_info', {}).get('year_gan', '甲')
        rule_based_analysis = analyzer.analyze_patterns(palace_stars, year_stem)
        # 将规则匹配结果添加到 chart_data 中供 LLM 参考
        chart_data = {**chart_data, '_rule_based_patterns': rule_based_analysis.to_dict()}

    return await analyzer.analyze_with_llm(question)


@cached_chart_analysis("patterns", ttl=3600)
def llm_analyze_patterns_sync(
    chart_data: Any,
    palace_stars: Optional[Dict[str, List[str]]] = None,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """同步版本的LLM格局分析

    Args:
        chart_data: 命盘数据
        palace_stars: 宫位星曜数据（可选，如果提供则进行规则匹配增强）
        question: 可选的特定问题
    """
    import asyncio
    return asyncio.run(llm_analyze_patterns(chart_data, palace_stars, question))
