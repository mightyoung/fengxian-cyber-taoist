"""
Timing Core - 运限时间分析核心函数

包含：
- 四化计算函数
- 成住坏空阶段计算
- 四化影响力计算
"""

from typing import Dict

from .timing_constants import HEAVENLY_STEM_TRANSFORMS


def get_yearly_transforms(year_gan: str) -> Dict[str, str]:
    """
    根据流年天干获取四化信息（流年四化）

    流年四化与年干四化的区别：
    - 流年四化：根据当前流年天干决定的四化，每年不同
    - 生年四化（年干四化）：根据出生年天干决定的四化，一生不变

    Args:
        year_gan: 流年天干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）

    Returns:
        四化字典，格式: {化位: 星曜名}，例如: {"禄": "廉贞", "权": "破军", ...}
    """
    if year_gan in HEAVENLY_STEM_TRANSFORMS:
        return HEAVENLY_STEM_TRANSFORMS[year_gan]
    return {}


def get_birth_transforms(birth_gan: str) -> Dict[str, str]:
    """
    根据出生年天干获取四化信息（生年四化/年干四化）

    生年四化是根据出生年的天干来确定的四化，一辈子不变。

    Args:
        birth_gan: 出生年天干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）

    Returns:
        四化字典，格式: {化位: 星曜名}
    """
    if birth_gan in HEAVENLY_STEM_TRANSFORMS:
        return HEAVENLY_STEM_TRANSFORMS[birth_gan]
    return {}


def get_cycle_stage_for_palace(palace: str, age: int, major_fate_year: int) -> str:
    """
    根据年龄和大限年数获取宫位的成住坏空阶段

    Args:
        palace: 宫位名称
        age: 当前年龄
        major_fate_year: 大限第几年 (1-10)

    Returns:
        成/住/坏/空
    """
    # 基础阶段 = (年龄 % 20) // 5  # 0-3对应成住坏空
    # 大限调整 = major_fate_year % 4
    # 综合计算
    base_stage = (age % 20) // 5
    fate_adjust = major_fate_year % 4

    stage_index = (base_stage + fate_adjust) % 4
    stages = ["成", "住", "坏", "空"]
    return stages[stage_index]


def get_transform_cycle_impact(transform_type: str, palace: str) -> Dict[str, str]:
    """
    获取四化对成住坏空的影响

    Args:
        transform_type: 化禄/化权/化科/化忌
        palace: 宫位

    Returns:
        影响描述字典
    """
    cycle_impacts = {
        "化禄": {
            "成": "加速形成，带来机遇",
            "住": "巩固稳定，积累财富",
            "坏": "表面繁华，内在空虚",
            "空": "虚假机遇，难以兑现"
        },
        "化权": {
            "成": "增强控制，快速成长",
            "住": "权力巩固，地位稳固",
            "坏": "权力斗争，是非增多",
            "空": "虚假权威，难以服众"
        },
        "化科": {
            "成": "名声初显，才华展露",
            "住": "名声稳定，贵人扶持",
            "坏": "名声受损，小人作祟",
            "空": "徒有虚名，才华被埋"
        },
        "化忌": {
            "成": "困难初现，根基不稳",
            "住": "持续压力，动力不足",
            "坏": "问题爆发，需要化解",
            "空": "彻底失败，一无所有"
        }
    }
    return cycle_impacts.get(transform_type, {})
