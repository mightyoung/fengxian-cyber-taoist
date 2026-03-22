"""
星曜分析智能体 - StarAgent

负责分析命盘中的星曜组合,生成星曜解读。

职责：
1. 加载星曜属性数据
2. 分析十四正曜、辅星、煞星的状态
3. 计算星曜的庙旺平陷
4. 生成星曜解读
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .llm_prompts import STAR_SYSTEM_PROMPT, build_star_user_prompt
from .siyin_loader import SiyinLoader, get_siyin_interpretation
from ..wuxing_calculator import WuXingJuType

# 宫位顺序
PALACE_ORDER = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "仆役宫",
    "官禄宫", "田宅宫", "父母宫", "福德宫"
]

# 地支到宫位索引的映射
BRANCH_TO_INDEX = {
    "子": 0, "丑": 1, "寅": 2, "卯": 3,
    "辰": 4, "巳": 5, "午": 6, "未": 7,
    "申": 8, "酉": 9, "戌": 10, "亥": 11
}


# ============ 五行局-庙旺平陷判断辅助函数 ============

# 星曜五行属性映射（来自 stars-attributes.json）
STAR_WUXING_MAP = {
    # 十四正曜
    "紫微": "土",
    "天机": "木",
    "太阳": "火",
    "武曲": "金",
    "天同": "水",
    "廉贞": "火",
    "天府": "土",
    "太阴": "水",
    "贪狼": "木",
    "巨门": "水",  # 阴水
    "天相": "水",
    "天梁": "土",
    "七杀": "金",
    "破军": "水",
    # 辅曜
    "左辅": "土",
    "右弼": "水",
    "天魁": "火",
    "天钺": "火",
    # 佐曜
    "文昌": "金",
    "文曲": "水",
    "禄存": "土",
    "天马": "火",
    # 煞星
    "擎羊": "金",
    "陀罗": "土",
    "火星": "火",
    "铃星": "火",
    "地空": "火",
    "地劫": "水",  # 阴水
}

# 五行局与星曜的增强关系
# 格式：{五行局: {星曜: 提升等级}}
# 当星曜五行与五行局相同时，该星曜在判断庙旺平时可提升一级
WUXING_JU_STAR_BOOST = {
    WuXingJuType.WATER_TWO: {
        "太阴": "水性星曜在太阴更旺，太阴落水二局旺上叠旺",
        "天同": "水性星曜，天同与太阴同属水牲，互助有力",
        "天相": "水牲星，天相落水二局更吉",
        "破军": "水性星曜，破军落水二局格局更佳",
    },
    WuXingJuType.WOOD_THREE: {
        "天机": "木性星曜，天机落木三局智慧之星更旺",
        "太阳": "木生火，但太阳为火牲，天机为木牲，相得益彰",
        "天同": "水生木，天同与天机木性互助",
        "贪狼": "木牲星，贪狼落木三局野心与智慧并存",
    },
    WuXingJuType.GOLD_FOUR: {
        "武曲": "金牲星，武曲落金四局财权两旺",
        "天府": "土金相生，天府落金四局更吉",
        "七杀": "金牲星，七杀落金四局威权更显",
    },
    WuXingJuType.EARTH_FIVE: {
        "紫微": "土牲星，紫微落土五局帝王之星更旺",
        "天府": "土牲星，天府土五局财库丰盈",
        "天相": "水牲星，但土能防水，天相落土五局有印星之力",
        "巨门": "土牲星，巨门落土五局能言善辩",
        "天梁": "土牲星，天梁落土五局福荫寿长",
    },
    WuXingJuType.FIRE_SIX: {
        "廉贞": "火牲星，廉贞落火六局清廉正直更旺",
        "七杀": "金牲星，火炼金成器，七杀落火六局威权显赫",
        "太阳": "火牲星，太阳落火六局光辉照世",
        "天梁": "土生金，但天梁与太阳火性有光",
    },
}

# 五行相生相克表
WUXING_RELATIONS = {
    "木": {"生": "火", "克": "土", "被生": "水", "被克": "金"},
    "火": {"生": "土", "克": "金", "被生": "木", "被克": "水"},
    "土": {"生": "金", "克": "水", "被生": "火", "被克": "木"},
    "金": {"生": "水", "克": "木", "被生": "土", "被克": "火"},
    "水": {"生": "木", "克": "火", "被生": "金", "被克": "土"},
}


def get_miao_wang_by_wuxing_ju(
    star: str,
    palace: str,
    wuxing_ju: str
) -> Dict[str, Any]:
    """
    根据星曜、宫位和五行局计算庙旺平陷

    Args:
        star: 星曜名称
        palace: 宫位名称
        wuxing_ju: 五行局（如"水二局"、"木三局"等）

    Returns:
        Dict包含:
            - level: 庙/旺/平/陷
            - base_level: 基于地支判断的基础等级
            - wuxing_adjustment: 五行局调整说明
            - wuxing_influence: 五行局影响描述
    """
    # 解析五行局类型
    wuxing_ju_type = None
    for jut in WuXingJuType:
        if jut.value == wuxing_ju or jut.value.replace("局", "") in wuxing_ju:
            wuxing_ju_type = jut
            break

    if wuxing_ju_type is None:
        return {
            "level": "平",
            "base_level": "平",
            "wuxing_adjustment": 0,
            "wuxing_influence": f"未知五行局: {wuxing_ju}，无法判断五行影响",
        }

    # 获取星曜五行属性
    star_wuxing = STAR_WUXING_MAP.get(star, None)
    if star_wuxing is None:
        return {
            "level": "平",
            "base_level": "平",
            "wuxing_adjustment": 0,
            "wuxing_influence": f"星曜 {star} 五行属性未知，默认为平",
        }

    # 判断五行局增强（与五行局相同则增强）
    wuxing_ju_element = {
        WuXingJuType.WATER_TWO: "水",
        WuXingJuType.WOOD_THREE: "木",
        WuXingJuType.GOLD_FOUR: "金",
        WuXingJuType.EARTH_FIVE: "土",
        WuXingJuType.FIRE_SIX: "火",
    }.get(wuxing_ju_type, "")

    # 计算五行关系
    base_result = {
        "level": "平",
        "base_level": "平",
        "wuxing_adjustment": 0,
        "wuxing_influence": "",
    }

    if star_wuxing == wuxing_ju_element:
        # 星曜五行与五行局相同，获得增强
        base_result["wuxing_adjustment"] = 1
        base_result["wuxing_influence"] = WUXING_JU_STAR_BOOST.get(wuxing_ju_type, {}).get(
            star,
            f"{star}属{star_wuxing}性，与{wuxing_ju}相合，得地而旺"
        )
    else:
        # 检查是否有特定增强关系
        boost_desc = WUXING_JU_STAR_BOOST.get(wuxing_ju_type, {}).get(star, "")
        if boost_desc:
            base_result["wuxing_adjustment"] = 1
            base_result["wuxing_influence"] = boost_desc
        else:
            base_result["wuxing_adjustment"] = 0
            relations = WUXING_RELATIONS.get(star_wuxing, {})
            if wuxing_ju_element == relations.get("被生"):
                base_result["wuxing_influence"] = f"{star}属{star_wuxing}性，{wuxing_ju}生助{star_wuxing}，星曜得地"
            elif wuxing_ju_element == relations.get("生"):
                base_result["wuxing_influence"] = f"{star}属{star_wuxing}性，{wuxing_ju}泄气，星曜稍弱"
            elif wuxing_ju_element == relations.get("克"):
                base_result["wuxing_influence"] = f"{star}属{star_wuxing}性，{wuxing_ju}克制{star_wuxing}，星曜受制"
            elif wuxing_ju_element == relations.get("被克"):
                base_result["wuxing_influence"] = f"{star}属{star_wuxing}性，{star_wuxing}克{wuxing_ju}，星曜有力"
            else:
                base_result["wuxing_influence"] = f"{star}属{star_wuxing}性，{wuxing_ju}与{star_wuxing}无直接生克关系"

    return base_result


def apply_wuxing_adjustment(base_level: str, adjustment: int) -> str:
    """
    根据五行局调整应用等级变化

    Args:
        base_level: 基础等级（庙/旺/平/陷）
        adjustment: 调整值（1=升一级，-1=降一级，0=不变）

    Returns:
        调整后的等级
    """
    level_order = ["陷", "平", "旺", "庙"]
    try:
        base_idx = level_order.index(base_level)
        new_idx = max(0, min(len(level_order) - 1, base_idx + adjustment))
        return level_order[new_idx]
    except ValueError:
        return base_level


class StarLevelType(str, Enum):
    """星曜庙旺平陷等级"""
    MIAO = "庙"   # 庙旺 - 最吉
    WANG = "旺"   # 旺 - 次吉
    PING = "平"   # 平 - 中等
    XIAN = "陷"   # 陷 - 凶


@dataclass
class StarAnalysisResult:
    """单颗星曜分析结果"""
    star_name: str
    palace: str
    level: str
    level_type: str
    category: str
    interpretation: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    wuxing_ju: str = ""  # 五行局
    wuxing_influence: str = ""  # 五行局影响说明
    base_level: str = ""  # 基础等级（地支判断）


@dataclass
class StarAnalysis:
    """星曜分析结果"""
    main_stars: List[StarAnalysisResult] = field(default_factory=list)
    auxiliary_stars: List[StarAnalysisResult] = field(default_factory=list)
    sha_stars: List[StarAnalysisResult] = field(default_factory=list)
    transform_stars: List[StarAnalysisResult] = field(default_factory=list)
    palace_star_summary: Dict[str, List[str]] = field(default_factory=dict)
    total_stars_count: int = 0


class StarAgent:
    """
    星曜分析智能体

    分析命盘中的星曜组合,生成详细的星曜解读。
    """

    def __init__(self, chart_data: Dict[str, Any]):
        """
        初始化星曜分析智能体

        Args:
            chart_data: 命盘数据字典
        """
        self.chart = chart_data
        self.star_attributes = self._load_star_attributes()
        self.palace_attributes = self._load_palace_attributes()
        self.siyin_loader = SiyinLoader()

        # 获取五行局信息
        birth_info = chart_data.get("birth_info", {})
        self.wuxing_ju = birth_info.get("wuxing_ju", birth_info.get("wuxing_ju_name", ""))

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        # 获取项目根目录
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        full_path = os.path.join(project_root, file_path)

        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_star_attributes(self) -> Dict[str, Any]:
        """加载星曜属性数据"""
        try:
            return self._load_json("data_source/mlx/data/knowledge/stars/stars-attributes.json")
        except FileNotFoundError:
            # 如果文件不存在,返回空字典
            return {"stars": {}}

    def _load_palace_attributes(self) -> Dict[str, Any]:
        """加载宫位属性数据"""
        try:
            return self._load_json("data_source/mlx/data/knowledge/palaces/palaces-attributes.json")
        except FileNotFoundError:
            return {"palaces": {}}

    def _get_star_category(self, star_name: str) -> str:
        """获取星曜类别"""
        stars_data = self.star_attributes.get("stars", {})

        # 检查十四正曜
        zhengyao = stars_data.get("十四正曜", {})
        if star_name in zhengyao:
            return "十四正曜"

        # 检查辅曜
        fuyao = stars_data.get("辅曜", {})
        if star_name in fuyao:
            return "辅曜"

        # 检查佐曜
        zuoyao = stars_data.get("佐曜", {})
        if star_name in zuoyao:
            return "佐曜"

        # 检查煞星
        saxing = stars_data.get("煞星", {})
        if star_name in saxing:
            return "煞星"

        # 检查化曜
        hua_yao = stars_data.get("化曜", {})
        if star_name in hua_yao:
            return "化曜"

        return "杂星"

    def _get_star_attributes(self, star_name: str) -> Dict[str, Any]:
        """获取星曜详细属性"""
        stars_data = self.star_attributes.get("stars", {})

        # 按类别查找
        for category in ["十四正曜", "辅曜", "佐曜", "煞星", "化曜"]:
            category_data = stars_data.get(category, {})
            if star_name in category_data:
                return category_data[star_name]

        return {}

    def _get_palace_branch(self, palace_name: str) -> str:
        """获取宫位对应的地支"""
        palace_data = self.palace_attributes.get("palaces", {})
        return palace_data.get(palace_name, {}).get("branch", "")

    def get_star_level(self, star_name: str, palace: str, include_wuxing: bool = True) -> str:
        """
        计算星曜的庙旺平陷等级

        Args:
            star_name: 星曜名称
            palace: 宫位名称
            include_wuxing: 是否考虑五行局调整

        Returns:
            庙/旺/平/陷
        """
        star_attrs = self._get_star_attributes(star_name)
        if not star_attrs:
            return "平"  # 未知星曜默认为平

        # 获取宫位对应的地支
        palace_branch = self._get_palace_branch(palace)

        # 检查庙位
        miao_positions = star_attrs.get("miao_positions", [])
        if palace_branch in miao_positions:
            base_level = "庙"
            return self._apply_wuxing_adjustment(star_name, base_level) if include_wuxing else base_level

        # 检查旺位
        wang_positions = star_attrs.get("wang_positions", [])
        if palace_branch in wang_positions:
            base_level = "旺"
            return self._apply_wuxing_adjustment(star_name, base_level) if include_wuxing else base_level

        # 检查陷位
        xian_positions = star_attrs.get("xian_positions", [])
        if palace_branch in xian_positions:
            base_level = "陷"
            return self._apply_wuxing_adjustment(star_name, base_level) if include_wuxing else base_level

        # 默认为平
        base_level = "平"
        return self._apply_wuxing_adjustment(star_name, base_level) if include_wuxing else base_level

    def _apply_wuxing_adjustment(self, star_name: str, base_level: str) -> str:
        """
        五行局不影响星曜庙旺平陷
        五行局仅决定大限起运年龄，不应影响星曜本身的庙旺平陷等级

        Args:
            star_name: 星曜名称
            base_level: 基础等级

        Returns:
            直接返回基础等级，不做调整
        """
        # 五行局仅决定大限起运年龄，不影响星曜庙旺
        return base_level

    def get_star_level_with_wuxing(self, star_name: str, palace: str) -> Dict[str, Any]:
        """
        获取星曜庙旺平陷详情（含五行局影响）

        Args:
            star_name: 星曜名称
            palace: 宫位名称

        Returns:
            包含完整庙旺平陷信息和五行局影响的字典
        """
        star_attrs = self._get_star_attributes(star_name)
        if not star_attrs:
            return {
                "level": "平",
                "base_level": "平",
                "wuxing_ju": self.wuxing_ju,
                "wuxing_adjustment": 0,
                "wuxing_influence": f"星曜 {star_name} 属性未知"
            }

        # 获取宫位对应的地支
        palace_branch = self._get_palace_branch(palace)

        # 确定基础等级
        miao_positions = star_attrs.get("miao_positions", [])
        if palace_branch in miao_positions:
            base_level = "庙"
        else:
            wang_positions = star_attrs.get("wang_positions", [])
            if palace_branch in wang_positions:
                base_level = "旺"
            else:
                xian_positions = star_attrs.get("xian_positions", [])
                if palace_branch in xian_positions:
                    base_level = "陷"
                else:
                    base_level = "平"

        # 获取五行局调整
        wuxing_result = get_miao_wang_by_wuxing_ju(star_name, palace, self.wuxing_ju)
        adjustment = wuxing_result.get("wuxing_adjustment", 0)

        # 应用调整
        final_level = apply_wuxing_adjustment(base_level, adjustment) if adjustment != 0 else base_level

        return {
            "level": final_level,
            "base_level": base_level,
            "wuxing_ju": self.wuxing_ju,
            "wuxing_adjustment": adjustment,
            "wuxing_influence": wuxing_result.get("wuxing_influence", ""),
            "palace_branch": palace_branch,
        }

    def _generate_star_interpretation(
        self,
        star_name: str,
        palace: str,
        level: str,
        category: str
    ) -> str:
        """生成星曜解读"""
        star_attrs = self._get_star_attributes(star_name)
        palace_attrs = self.palace_attributes.get("palaces", {}).get(palace, {})

        # 获取基础解读
        interpretation_parts = []

        # 添加星曜特性
        characteristics = star_attrs.get("characteristics", [])
        if characteristics:
            interpretation_parts.append(f"星曜特性: {'; '.join(characteristics[:2])}")

        # 添加庙旺平陷解读
        if category == "十四正曜":
            interp_dict = star_attrs.get("interpretation", {})
            level_key = {"庙": "miao", "旺": "wang", "平": "ping", "陷": "xian"}.get(level, "ping")
            level_interp = interp_dict.get(level_key, "")
            if level_interp:
                interpretation_parts.append(level_interp)

        # 添加宫位解读
        palace_focus = palace_attrs.get("focus", "")
        if palace_focus:
            interpretation_parts.append(f"落宫特点: {palace_focus}")

        # 添加强弱判断
        if level == "庙":
            interpretation_parts.append("庙旺: 星曜力量最强,最为吉利")
        elif level == "旺":
            interpretation_parts.append("旺: 星曜力量较强,较为吉利")
        elif level == "陷":
            interpretation_parts.append("陷: 星曜力量最弱,需谨慎应对")
        else:
            interpretation_parts.append("平: 星曜力量中等")

        return "。".join(interpretation_parts) if interpretation_parts else f"{star_name}落在{palace},{level}位"

    def _analyze_single_star(
        self,
        star_data: Dict[str, Any],
        palace: str
    ) -> StarAnalysisResult:
        """分析单颗星曜"""
        star_name = star_data.get("name", "")
        level_str = star_data.get("level", "平")
        category = self._get_star_category(star_name)

        # 获取含五行局影响的完整庙旺平陷信息
        wuxing_detail = self.get_star_level_with_wuxing(star_name, palace)
        calculated_level = wuxing_detail.get("level", "平")
        base_level = wuxing_detail.get("base_level", "平")
        wuxing_influence = wuxing_detail.get("wuxing_influence", "")

        # 获取星曜属性
        star_attrs = self._get_star_attributes(star_name)

        # 生成解读
        interpretation = self._generate_star_interpretation(
            star_name, palace, calculated_level, category
        )

        # 如果有五行局影响，添加到解读中
        if wuxing_influence:
            interpretation = f"{interpretation} [{wuxing_influence}]"

        return StarAnalysisResult(
            star_name=star_name,
            palace=palace,
            level=level_str,  # 原始等级
            level_type=calculated_level,  # 计算后的庙旺平陷
            category=category,
            interpretation=interpretation,
            attributes=star_attrs,
            wuxing_ju=self.wuxing_ju,
            wuxing_influence=wuxing_influence,
            base_level=base_level,
        )

    def _get_co_star_at_palace(self, palace_name: str) -> List[str]:
        """获取指定宫位的所有共星（除了主星外的其他星曜）"""
        palaces_data = self.chart.get("palaces", {})
        palace_data = palaces_data.get(palace_name, {})
        stars = palace_data.get("stars", [])

        co_stars = []
        for star in stars:
            star_name = star.get("name", "")
            if star_name and star.get("type") != "正曜":
                co_stars.append(star_name)
        return co_stars

    def _get_main_star_at_palace(self, palace_name: str) -> Optional[str]:
        """获取指定宫位的主星"""
        palaces_data = self.chart.get("palaces", {})
        palace_data = palaces_data.get(palace_name, {})
        stars = palace_data.get("stars", [])

        for star in stars:
            if star.get("type") == "正曜":
                return star.get("name")
        return None

    def get_siyin_system_for_palace(self, palace_name: str) -> Dict[str, Any]:
        """
        获取指定宫位的六十星系分析

        Args:
            palace_name: 宫位名称

        Returns:
            六十星系分析结果
        """
        main_star = self._get_main_star_at_palace(palace_name)
        if not main_star:
            return {
                "matched": False,
                "reason": "该宫位无主星"
            }

        co_stars = self._get_co_star_at_palace(palace_name)
        palace_branch = self._get_palace_branch(palace_name)

        # 使用六十星系加载器获取分析
        result = get_siyin_interpretation(main_star, co_stars, palace_branch)

        # 添加额外信息
        result["main_star"] = main_star
        result["secondary_stars"] = co_stars
        result["palace"] = palace_name
        result["palace_branch"] = palace_branch

        return result

    def analyze_all_palaces_siyin(self) -> Dict[str, Dict[str, Any]]:
        """
        分析所有宫位的六十星系配置

        Returns:
            包含所有宫位六十星系分析的字典
        """
        results = {}
        for palace_name in PALACE_ORDER:
            siyin_analysis = self.get_siyin_system_for_palace(palace_name)
            if siyin_analysis.get("matched"):
                results[palace_name] = siyin_analysis
        return results

    async def analyze_stars(self) -> StarAnalysis:
        """
        分析命盘中的所有星曜

        Returns:
            StarAnalysis: 星曜分析结果
        """
        stars_data = self.chart.get("stars", {})
        palaces_data = self.chart.get("palaces", {})

        result = StarAnalysis()

        # 分析主星
        main_stars = stars_data.get("main_stars", [])
        for star_data in main_stars:
            star_name = star_data.get("name", "")
            palace = star_data.get("palace", "")
            if palace:
                analysis = self._analyze_single_star(star_data, palace)
                result.main_stars.append(analysis)

        # 分析辅星
        auxiliary_stars = stars_data.get("auxiliary_stars", [])
        for star_data in auxiliary_stars:
            palace = star_data.get("palace", "")
            if palace:
                analysis = self._analyze_single_star(star_data, palace)
                result.auxiliary_stars.append(analysis)

        # 分析煞星
        sha_stars = stars_data.get("sha_stars", [])
        for star_data in sha_stars:
            palace = star_data.get("palace", "")
            if palace:
                analysis = self._analyze_single_star(star_data, palace)
                result.sha_stars.append(analysis)

        # 分析化曜
        transform_stars = stars_data.get("transform_stars", [])
        for star_data in transform_stars:
            palace = star_data.get("palace", "")
            if palace:
                analysis = self._analyze_single_star(star_data, palace)
                result.transform_stars.append(analysis)

        # 构建宫位星曜汇总
        for palace_name in PALACE_ORDER:
            palace_stars = palaces_data.get(palace_name, {}).get("stars", [])
            star_names = [s.get("name", "") for s in palace_stars if s.get("name")]
            if star_names:
                result.palace_star_summary[palace_name] = star_names

        # 计算总星数
        result.total_stars_count = (
            len(result.main_stars) +
            len(result.auxiliary_stars) +
            len(result.sha_stars) +
            len(result.transform_stars)
        )

        return result

    def get_palace_star_summary(self, palace_name: str) -> List[str]:
        """获取指定宫位的星曜列表"""
        palaces_data = self.chart.get("palaces", {})
        palace_data = palaces_data.get(palace_name, {})
        return palace_data.get("stars", [])

    def get_star_by_palace(self, palace_name: str) -> Dict[str, Any]:
        """获取指定宫位的星曜分析"""
        result = {
            "palace": palace_name,
            "wuxing_ju": self.wuxing_ju,
            "main_stars": [],
            "auxiliary_stars": [],
            "sha_stars": [],
            "transform_stars": [],
            "total_stars": 0
        }

        palaces_data = self.chart.get("palaces", {})
        palace_data = palaces_data.get(palace_name, {})
        stars = palace_data.get("stars", [])

        for star in stars:
            star_name = star.get("name", "")
            star_type = star.get("type", "")
            level = star.get("level", "平")

            # 获取含五行局影响的完整信息
            wuxing_detail = self.get_star_level_with_wuxing(star_name, palace_name)
            calculated_level = wuxing_detail.get("level", "平")
            wuxing_influence = wuxing_detail.get("wuxing_influence", "")

            star_info = {
                "name": star_name,
                "original_level": level,
                "calculated_level": calculated_level,
                "base_level": wuxing_detail.get("base_level", ""),
                "wuxing_influence": wuxing_influence,
                "attributes": self._get_star_attributes(star_name)
            }

            if star_type == "正曜":
                result["main_stars"].append(star_info)
            elif star_type == "辅星":
                result["auxiliary_stars"].append(star_info)
            elif star_type == "煞星":
                result["sha_stars"].append(star_info)
            elif star_type == "化曜":
                result["transform_stars"].append(star_info)

        result["total_stars"] = len(stars)
        return result

    def generate_star_report(self) -> str:
        """生成星曜分析报告文本"""
        import asyncio

        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 没有运行中的事件循环，可以安全使用asyncio.run()
            return asyncio.run(self._generate_star_report_async())
        else:
            # 在事件循环中运行，需要创建一个任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, self._generate_star_report_async())
                return future.result()

    async def _generate_star_report_async(self) -> str:
        """异步生成星曜分析报告"""
        analysis = await self.analyze_stars()

        lines = ["=" * 50]
        lines.append("星曜分析报告")
        lines.append("=" * 50)

        # 添加五行局信息
        if self.wuxing_ju:
            lines.append(f"\n五行局: {self.wuxing_ju}")
        lines.append("")

        # 主星分析
        lines.append("\n【十四正曜分析】")
        for star in analysis.main_stars:
            lines.append(f"\n{star.star_name} ({star.palace})")
            lines.append(f"  原始等级: {star.level}")
            lines.append(f"  基础庙旺: {star.base_level}")
            lines.append(f"  五行局调整后: {star.level_type}")
            if star.wuxing_influence:
                lines.append(f"  五行影响: {star.wuxing_influence}")
            lines.append(f"  解读: {star.interpretation}")

        # 辅星分析
        lines.append("\n\n【辅星分析】")
        if analysis.auxiliary_stars:
            for star in analysis.auxiliary_stars:
                wuxing_info = f" | 五行影响: {star.wuxing_influence}" if star.wuxing_influence else ""
                lines.append(f"  {star.star_name} - {star.palace} ({star.level_type}){wuxing_info}")
        else:
            lines.append("  无辅星落入")

        # 煞星分析
        lines.append("\n\n【煞星分析】")
        if analysis.sha_stars:
            for star in analysis.sha_stars:
                wuxing_info = f" | 五行影响: {star.wuxing_influence}" if star.wuxing_influence else ""
                lines.append(f"  {star.star_name} - {star.palace} ({star.level_type}){wuxing_info}")
        else:
            lines.append("  无煞星落入")

        # 化曜分析
        lines.append("\n\n【化曜分析】")
        if analysis.transform_stars:
            for star in analysis.transform_stars:
                lines.append(f"  {star.star_name} - {star.palace}")
        else:
            lines.append("  无化曜落入")

        # 宫位汇总
        lines.append("\n\n【宫位星曜汇总】")
        for palace, stars in analysis.palace_star_summary.items():
            if stars:
                lines.append(f"  {palace}: {', '.join(stars)}")

        lines.append("\n" + "=" * 50)
        lines.append(f"总星曜数: {analysis.total_stars_count}")
        lines.append("=" * 50)

        return "\n".join(lines)


# ============ LLM增强分析 ============

class LLMStarAnalyzer:
    """星曜分析LLM增强器"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度星曜分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        from ....utils.llm_client import LLMClient

        # 构建提示词
        user_prompt = build_star_user_prompt(self.chart, question)

        messages = [
            {"role": "system", "content": STAR_SYSTEM_PROMPT},
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
        """
        生成文本格式的LLM分析报告

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            格式化的文本报告
        """
        result = await self.analyze_with_llm(question, temperature)
        return format_analysis_as_text(result)


async def llm_analyze_stars(
    chart_data: Dict[str, Any],
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用LLM分析命盘星曜

    Args:
        chart_data: 命盘数据
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLMStarAnalyzer(chart_data)
    return await analyzer.analyze_with_llm(question)


def llm_analyze_stars_sync(
    chart_data: Dict[str, Any],
    question: Optional[str] = None
) -> Dict[str, Any]:
    """同步版本的LLM星曜分析"""
    import asyncio
    return asyncio.run(llm_analyze_stars(chart_data, question))


# ============ 便捷函数 ============

async def analyze_chart_stars(chart_data: Dict[str, Any]) -> StarAnalysis:
    """
    分析命盘星曜

    Args:
        chart_data: 命盘数据

    Returns:
        StarAnalysis: 星曜分析结果
    """
    agent = StarAgent(chart_data)
    return await agent.analyze_stars()


def analyze_stars_sync(chart_data: Dict[str, Any]) -> StarAnalysis:
    """同步版本的星曜分析"""
    import asyncio
    return asyncio.run(analyze_chart_stars(chart_data))


if __name__ == "__main__":
    # 测试示例
    import asyncio

    async def main():
        # 模拟命盘数据
        test_chart = {
            "birth_info": {
                "year": 1990,
                "month": 5,
                "day": 15,
                "gender": "male",
                "wuxing_ju": "水二局"
            },
            "palaces": {
                "命宫": {"branch": "子", "tiangan": "甲", "stars": [
                    {"name": "紫微", "type": "正曜", "level": "旺"},
                    {"name": "天机", "type": "正曜", "level": "平"},
                    {"name": "左辅", "type": "辅星", "level": "旺"}
                ]},
                "兄弟宫": {"branch": "丑", "tiangan": "乙", "stars": []},
                "夫妻宫": {"branch": "寅", "tiangan": "丙", "stars": []},
                "子女宫": {"branch": "卯", "tiangan": "丁", "stars": []},
                "财帛宫": {"branch": "辰", "tiangan": "戊", "stars": []},
                "疾厄宫": {"branch": "巳", "tiangan": "己", "stars": []},
                "迁移宫": {"branch": "午", "tiangan": "庚", "stars": []},
                "仆役宫": {"branch": "未", "tiangan": "辛", "stars": []},
                "官禄宫": {"branch": "申", "tiangan": "壬", "stars": []},
                "田宅宫": {"branch": "酉", "tiangan": "癸", "stars": []},
                "父母宫": {"branch": "戌", "tiangan": "甲", "stars": []},
                "福德宫": {"branch": "亥", "tiangan": "乙", "stars": []}
            },
            "stars": {
                "main_stars": [
                    {"name": "紫微", "palace": "命宫", "level": "旺", "type": "正曜"},
                    {"name": "天机", "palace": "命宫", "level": "平", "type": "正曜"},
                    {"name": "太阳", "palace": "财帛宫", "level": "旺", "type": "正曜"},
                    {"name": "武曲", "palace": "田宅宫", "level": "旺", "type": "正曜"},
                    {"name": "天同", "palace": "官禄宫", "level": "庙", "type": "正曜"},
                    {"name": "廉贞", "palace": "福德宫", "level": "旺", "type": "正曜"},
                    {"name": "天府", "palace": "父母宫", "level": "旺", "type": "正曜"},
                    {"name": "太阴", "palace": "兄弟宫", "level": "旺", "type": "正曜"},
                    {"name": "贪狼", "palace": "夫妻宫", "level": "庙", "type": "正曜"},
                    {"name": "巨门", "palace": "迁移宫", "level": "旺", "type": "正曜"},
                    {"name": "天相", "palace": "疾厄宫", "level": "庙", "type": "正曜"},
                    {"name": "天梁", "palace": "子女宫", "level": "旺", "type": "正曜"},
                    {"name": "七杀", "palace": "仆役宫", "level": "旺", "type": "正曜"},
                    {"name": "破军", "palace": "田宅宫", "level": "旺", "type": "正曜"}
                ],
                "auxiliary_stars": [
                    {"name": "左辅", "palace": "命宫", "level": "旺", "type": "辅星"},
                    {"name": "右弼", "palace": "福德宫", "level": "旺", "type": "辅星"},
                    {"name": "文昌", "palace": "官禄宫", "level": "平", "type": "辅星"},
                    {"name": "文曲", "palace": "财帛宫", "level": "平", "type": "辅星"},
                    {"name": "天魁", "palace": "迁移宫", "level": "旺", "type": "辅星"},
                    {"name": "天钺", "palace": "夫妻宫", "level": "旺", "type": "辅星"}
                ],
                "sha_stars": [
                    {"name": "擎羊", "palace": "迁移宫", "level": "陷", "type": "煞星"},
                    {"name": "陀罗", "palace": "疾厄宫", "level": "陷", "type": "煞星"},
                    {"name": "火星", "palace": "田宅宫", "level": "陷", "type": "煞星"},
                    {"name": "地空", "palace": "父母宫", "level": "陷", "type": "煞星"}
                ],
                "transform_stars": [
                    {"name": "化禄", "palace": "财帛宫", "level": "庙", "type": "化曜"},
                    {"name": "化权", "palace": "官禄宫", "level": "旺", "type": "化曜"},
                    {"name": "化忌", "palace": "福德宫", "level": "陷", "type": "化曜"}
                ]
            },
            "transforms": [
                {"type": "禄", "star": "廉贞", "palace": "财帛宫"},
                {"type": "权", "star": "紫微", "palace": "官禄宫"},
                {"type": "科", "star": "文昌", "palace": "父母宫"},
                {"type": "忌", "star": "廉贞", "palace": "福德宫"}
            ]
        }

        agent = StarAgent(test_chart)

        # 测试分析
        print("=== 星曜分析测试 ===\n")

        # 测试获取单个宫位星曜
        palace_analysis = agent.get_star_by_palace("命宫")
        print(f"命宫星曜分析: {palace_analysis}")

        # 测试庙旺平陷计算
        level = agent.get_star_level("紫微", "命宫")
        print(f"\n紫微在命宫的庙旺平陷: {level}")

        level2 = agent.get_star_level("太阳", "疾厄宫")
        print(f"太阳在疾厄宫的庙旺平陷: {level2}")

        # 测试完整分析
        analysis = await agent.analyze_stars()
        print(f"\n主星数量: {len(analysis.main_stars)}")
        print(f"辅星数量: {len(analysis.auxiliary_stars)}")
        print(f"煞星数量: {len(analysis.sha_stars)}")
        print(f"化曜数量: {len(analysis.transform_stars)}")

        # 测试报告生成
        print("\n" + "=" * 50)
        print(agent.generate_star_report())

    asyncio.run(main())
