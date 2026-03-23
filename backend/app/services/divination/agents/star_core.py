"""
Star Core - 星曜分析核心计算函数

包含：
- get_miao_wang_by_wuxing_ju: 根据星曜、宫位和五行局计算庙旺平陷
- apply_wuxing_adjustment: 根据五行局调整应用等级变化

注意：常量请使用 star_constants 模块
"""

from typing import Any, Dict

from .star_constants import (
    STAR_WUXING_MAP,
    WUXING_JU_STAR_BOOST,
    WUXING_RELATIONS,
)
from ..wuxing_calculator import WuXingJuType


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
