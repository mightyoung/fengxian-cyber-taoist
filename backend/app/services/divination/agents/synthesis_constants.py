"""
Synthesis Constants - 综合分析常量定义

包含：
- ConflictType: 冲突类型枚举
- PRIORITY_RULES: 优先级规则
- PALACE_RELATIONS: 宫位关系图
- STAR_CATEGORIES: 星曜分类
- TRANSFORM_INTERACTIONS: 四化相互作用规则
- TRANSFORMABLE_PATTERNS: 可转化凶格规则

注意：Dataclasses 请使用 synthesis_types 模块
"""

from typing import Dict, List
from enum import Enum


class ConflictType(Enum):
    """冲突类型枚举"""
    REAL_CONFLICT = "real_conflict"           # 真正的冲突（性质相反且影响同一事务）
    TRANSFORMABLE = "transformable"            # 可转化类型（某些凶格在特定条件下可解）
    FALSE_POSITIVE = "false_positive"         # 误判（看起来冲突但实际不冲突）
    COMPLEMENTARY = "complementary"           # 互补关系（一方描述细节另一方描述全局）
    NO_CONFLICT = "no_conflict"               # 无冲突


# 优先级规则：主星 > 辅星 > 杂曜
# 时机：运限 > 原局
# 四化：化忌 > 化禄/化权/化科
PRIORITY_RULES = {
    "星曜级别": {
        "正曜": 3,
        "副曜": 2,
        "杂曜": 1
    },
    "四化级别": {
        "化忌": 4,
        "化权": 3,
        "化科": 2,
        "化禄": 2
    },
    "时机": {
        "运限": 2,
        "原局": 1
    }
}

# 宫位关系图：哪些宫位相互影响
PALACE_RELATIONS: Dict[str, Dict[str, List[str]]] = {
    "财帛宫": {"related": ["命宫", "官禄宫", "福德宫"], "opposes": ["田宅宫"]},
    "官禄宫": {"related": ["命宫", "财帛宫", "迁移宫"], "opposes": ["兄弟宫"]},
    "命宫": {"related": ["财帛宫", "官禄宫", "迁移宫"], "opposes": ["福德宫"]},
    "夫妻宫": {"related": ["官禄宫", "迁移宫", "福德宫"], "opposes": ["田宅宫"]},
    "迁移宫": {"related": ["命宫", "官禄宫", "仆役宫"], "opposes": ["命宫"]},
    "福德宫": {"related": ["命宫", "夫妻宫", "田宅宫"], "opposes": ["命宫"]},
}

# 星曜分类：决定优先级
STAR_CATEGORIES: Dict[str, List[str]] = {
    "main_stars": ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"],
    "assistant_stars": ["左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马"],
    "transforming_stars": ["化禄", "化权", "化科", "化忌"],
    "flower_stars": ["红鸾", "天喜", "咸池", "海棠"],
    "sha_stars": ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"],
}

# 四化相互作用的规则
TRANSFORM_INTERACTIONS: Dict[tuple, str] = {
    ("化禄", "化忌"): "相悖",    # 化禄增加vs化忌减少
    ("化权", "化忌"): "相悖",    # 强势vs阻碍
    ("化科", "化忌"): "相悖",    # 名声vs阻碍
    ("化禄", "化权"): "相助",    # 财权双美
    ("化禄", "化科"): "相助",    # 财名双美
    ("化权", "化科"): "相助",    # 权名双美
}

# 可转化凶格规则
TRANSFORMABLE_PATTERNS: List[tuple] = [
    # (凶格特征, 转化条件, 转化结果)
    ("桃花星.*煞星", "有化禄或化权", "桃花煞变桃花贵"),
    ("煞星.*桃花星", "有化科或左辅右弼", "煞星被制化"),
    ("化忌.*破军", "有化禄或禄存", "破财可解"),
    ("空亡.*星曜", "有天乙贵人或天马", "凶中带吉"),
    ("陀罗.*火星", "有天梁或天寿", "擎羊夹忌可解"),
]
