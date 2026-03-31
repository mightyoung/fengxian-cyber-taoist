"""
因果链常量模块 - 紫微斗数因果分析常量定义

包含：
- 宫位名称和索引
- 四化类型枚举
- 因果链类型枚举
- 年干/宫干四化映射表
- 飞化路线映射表
"""

from typing import Dict, List
from enum import Enum


# 十二宫名称（按固定顺序）
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "交友宫",
    "官禄宫", "田宅宫", "福德宫", "父母宫"
]

# 宫位索引映射
PALACE_INDEX = {name: i for i, name in enumerate(PALACE_NAMES)}


class SeverityLevel(Enum):
    """凶险等级"""
    GOOD = "吉祥"          # 无忌或全禄：吉祥如意
    POTENTIAL = "潜在"      # 单忌：潜在阻碍
    CONDITION = "条件"      # 双忌：有条件阻碍
    BAD = "确定"           # 三忌：确定发生
    CATASTROPHIC = "重大"  # 四忌+：重大灾祸


class TransformType(Enum):
    """四化类型"""
    HUA_LU = "化禄"      # 化禄 - 机会、原因
    HUA_QUAN = "化权"    # 化权 - 权力、成就
    HUA_KE = "化科"      # 化科 - 名誉、科名
    HUA_JI = "化忌"      # 化忌 - 结果、阻碍


class CausalChainType(Enum):
    """因果链类型"""
    LU_ZHUAN_JI = "禄转忌"       # 得而复失
    JI_ZHUAN_JI = "忌转忌"       # 连续阻碍（需同星曜才契缘）
    LU_JI_TONG_GONG = "禄忌同宫"  # 得失参半
    SAN_JI_HUI_JU = "三忌汇聚"   # 大凶之兆（宫位串联，非同宫数量）
    JI_CHONG_MING = "忌冲命宫"   # 命宫受冲
    JI_CHONG_YI = "忌冲迁移"     # 迁移宫受冲
    BEN_GONG_ZI_HUA = "本宫自化"  # 本宫自化禄权科忌
    LU_JI_DUI_CHEN = "禄忌对称"   # 禄忌对称分析
    GUO_BAO_GONG = "果报宫"       # 果报宫分析
    JI_RU_ZI_HUA = "忌入逢自化"   # 忌入逢自化特殊情况
    LIN_GONG_CHONG = "邻宫冲势"   # 邻宫冲势判断
    ZHUI_LU = "追禄"             # 追踪禄的走向
    ZHUI_QUAN = "追权"           # 追踪权的走向
    ZHUI_JI = "追忌"             # 追踪忌的走向
    SAN_FANG_SI_ZHENG = "三方四正"  # 三方四正关系
    PATTERN_RECOGNITION = "格局识别"  # 四大格局识别


# 生年干四化映射表
# 与 transform_decider 保持一致，避免不同分析链条使用不同四化规则。
YEAR_STEM_TRANSFORMS: Dict[str, Dict[TransformType, str]] = {
    "甲": {
        TransformType.HUA_LU: "廉贞",
        TransformType.HUA_QUAN: "破军",
        TransformType.HUA_KE: "太阳",
        TransformType.HUA_JI: "太阴",
    },
    "乙": {
        TransformType.HUA_LU: "天机",
        TransformType.HUA_QUAN: "天梁",
        TransformType.HUA_KE: "文昌",
        TransformType.HUA_JI: "贪狼",
    },
    "丙": {
        TransformType.HUA_LU: "天同",
        TransformType.HUA_QUAN: "天机",
        TransformType.HUA_KE: "天机",
        TransformType.HUA_JI: "天同",
    },
    "丁": {
        TransformType.HUA_LU: "巨门",
        TransformType.HUA_QUAN: "太阳",
        TransformType.HUA_KE: "文曲",
        TransformType.HUA_JI: "天机",
    },
    "戊": {
        TransformType.HUA_LU: "贪狼",
        TransformType.HUA_QUAN: "武曲",
        TransformType.HUA_KE: "天梁",
        TransformType.HUA_JI: "廉贞",
    },
    "己": {
        TransformType.HUA_LU: "太阴",
        TransformType.HUA_QUAN: "巨门",
        TransformType.HUA_KE: "天机",
        TransformType.HUA_JI: "文昌",
    },
    "庚": {
        TransformType.HUA_LU: "天梁",
        TransformType.HUA_QUAN: "紫微",
        TransformType.HUA_KE: "天府",
        TransformType.HUA_JI: "天同",
    },
    "辛": {
        TransformType.HUA_LU: "文昌",
        TransformType.HUA_QUAN: "文曲",
        TransformType.HUA_KE: "天同",
        TransformType.HUA_JI: "天梁",
    },
    "壬": {
        TransformType.HUA_LU: "天同",
        TransformType.HUA_QUAN: "天机",
        TransformType.HUA_KE: "天机",
        TransformType.HUA_JI: "天同",
    },
    "癸": {
        TransformType.HUA_LU: "天机",
        TransformType.HUA_QUAN: "文曲",
        TransformType.HUA_KE: "天同",
        TransformType.HUA_JI: "天机",
    },
}


# 宫干四化映射表（梁若瑜《飞星紫微斗数》自化理论）
# 每个天干在不同宫位时的四化结果
# 注意：这是宫干（不是年干）的四化表，用于计算自化
# 宫干四化与年干四化使用相同的天干规则
PALACE_GAN_TRANSFORMS: Dict[str, Dict[TransformType, str]] = {
    "甲": {
        TransformType.HUA_LU: "廉贞",
        TransformType.HUA_QUAN: "破军",
        TransformType.HUA_KE: "太阳",
        TransformType.HUA_JI: "太阴",
    },
    "乙": {
        TransformType.HUA_LU: "廉贞",
        TransformType.HUA_QUAN: "破军",
        TransformType.HUA_KE: "武曲",
        TransformType.HUA_JI: "太阳",
    },
    "丙": {
        TransformType.HUA_LU: "天同",
        TransformType.HUA_QUAN: "天梁",
        TransformType.HUA_KE: "太阳",
        TransformType.HUA_JI: "天同",
    },
    "丁": {
        TransformType.HUA_LU: "天同",
        TransformType.HUA_QUAN: "天梁",
        TransformType.HUA_KE: "天机",
        TransformType.HUA_JI: "太阴",
    },
    "戊": {
        TransformType.HUA_LU: "贪狼",
        TransformType.HUA_QUAN: "太阴",
        TransformType.HUA_KE: "右弼",
        TransformType.HUA_JI: "天机",
    },
    "己": {
        TransformType.HUA_LU: "武曲",
        TransformType.HUA_QUAN: "贪狼",
        TransformType.HUA_KE: "太阴",
        TransformType.HUA_JI: "武曲",
    },
    "庚": {
        TransformType.HUA_LU: "太阳",
        TransformType.HUA_QUAN: "武曲",
        TransformType.HUA_KE: "天府",
        TransformType.HUA_JI: "太阳",
    },
    "辛": {
        TransformType.HUA_LU: "巨门",
        TransformType.HUA_QUAN: "太阳",
        TransformType.HUA_KE: "天府",
        TransformType.HUA_JI: "巨门",
    },
    "壬": {
        TransformType.HUA_LU: "天梁",
        TransformType.HUA_QUAN: "天机",
        TransformType.HUA_KE: "紫微",
        TransformType.HUA_JI: "天梁",
    },
    "癸": {
        TransformType.HUA_LU: "天机",
        TransformType.HUA_QUAN: "巨门",
        TransformType.HUA_KE: "紫微",
        TransformType.HUA_JI: "天机",
    },
}


# 四化飞化路线（根据《飞星紫微斗数》理论）
# 化禄、化权、化科的飞化路线相同，化忌的飞化路线不同
FLYING_ROUTES: Dict[str, List[str]] = {
    "化禄": ["财帛宫", "官禄宫", "迁移宫", "福德宫", "命宫"],
    "化权": ["财帛宫", "官禄宫", "迁移宫", "福德宫", "命宫"],
    "化科": ["财帛宫", "官禄宫", "迁移宫", "福德宫", "命宫"],
    "化忌": ["对宫", "三合方"],
}


# 三方四正关系映射（王亭之《中州派》紫微斗数）
# 每个宫位的三方（已修正，使用动态计算公式）
# 三方 = (宫位索引+4)%12, (宫位索引+8)%12
# 旧版SANFANG_MAP包含了对宫（错误），现已改用get_sanfang()动态计算
SANFANG_MAP: Dict[str, List[str]] = {
    "命宫": ["财帛宫", "官禄宫"],
    "兄弟宫": ["疾厄宫", "田宅宫"],
    "夫妻宫": ["迁移宫", "福德宫"],
    "子女宫": ["交友宫", "父母宫"],
    "财帛宫": ["官禄宫", "命宫"],
    "疾厄宫": ["田宅宫", "兄弟宫"],
    "迁移宫": ["福德宫", "夫妻宫"],
    "交友宫": ["父母宫", "子女宫"],
    "官禄宫": ["命宫", "财帛宫"],
    "田宅宫": ["兄弟宫", "疾厄宫"],
    "福德宫": ["夫妻宫", "迁移宫"],
    "父母宫": ["子女宫", "交友宫"],
}


# 化忌飞化完整路线（梁若瑜《飞星紫微斗数》）
# 命宫、迁移宫、田宅宫需要特殊处理
JI_FLYING_ROUTE_MING: List[str] = ["财帛宫", "官禄宫", "疾厄宫", "田宅宫", "父母宫"]
JI_FLYING_ROUTE_QIAN: List[str] = ["命宫", "官禄宫", "仆役宫", "田宅宫", "福德宫"]
JI_FLYING_ROUTE_TIAN: List[str] = ["命宫", "兄弟宫", "福德宫", "父母宫", "财帛宫"]


# 飞化路线动态计算表（王亭之《中州派》紫微斗数）
# 根据本宫位动态计算飞化目标
DYNAMIC_FLYING_ROUTES: Dict[str, Dict[str, List[str]]] = {
    "命宫": {
        "化禄": ["财帛宫", "官禄宫", "迁移宫", "福德宫"],
        "化权": ["财帛宫", "官禄宫", "迁移宫", "福德宫"],
        "化科": ["财帛宫", "官禄宫", "迁移宫", "福德宫"],
        "化忌": ["财帛宫", "官禄宫", "疾厄宫", "田宅宫", "父母宫"],
    },
    "兄弟宫": {
        "化禄": ["财帛宫", "官禄宫", "迁移宫"],
        "化权": ["财帛宫", "官禄宫", "迁移宫"],
        "化科": ["财帛宫", "官禄宫", "迁移宫"],
        "化忌": ["命宫", "夫妻宫", "子女宫", "田宅宫", "福德宫"],
    },
    "夫妻宫": {
        "化禄": ["财帛宫", "官禄宫", "迁移宫"],
        "化权": ["财帛宫", "官禄宫", "迁移宫"],
        "化科": ["财帛宫", "官禄宫", "迁移宫"],
        "化忌": ["命宫", "兄弟宫", "子女宫", "父母宫", "福德宫"],
    },
    "子女宫": {
        "化禄": ["财帛宫", "官禄宫", "迁移宫"],
        "化权": ["财帛宫", "官禄宫", "迁移宫"],
        "化科": ["财帛宫", "官禄宫", "迁移宫"],
        "化忌": ["命宫", "兄弟宫", "夫妻宫", "田宅宫", "福德宫"],
    },
    "财帛宫": {
        "化禄": ["命宫", "官禄宫", "迁移宫"],
        "化权": ["命宫", "官禄宫", "迁移宫"],
        "化科": ["命宫", "官禄宫", "迁移宫"],
        "化忌": ["兄弟宫", "夫妻宫", "疾厄宫", "田宅宫", "父母宫"],
    },
    "疾厄宫": {
        "化禄": ["命宫", "兄弟宫", "迁移宫"],
        "化权": ["命宫", "兄弟宫", "迁移宫"],
        "化科": ["命宫", "兄弟宫", "迁移宫"],
        "化忌": ["命宫", "财帛宫", "官禄宫", "田宅宫", "福德宫"],
    },
    "迁移宫": {
        "化禄": ["命宫", "官禄宫", "财帛宫"],
        "化权": ["命宫", "官禄宫", "财帛宫"],
        "化科": ["命宫", "官禄宫", "财帛宫"],
        "化忌": ["命宫", "官禄宫", "仆役宫", "田宅宫", "福德宫"],
    },
    "仆役宫": {
        "化禄": ["命宫", "官禄宫", "迁移宫"],
        "化权": ["命宫", "官禄宫", "迁移宫"],
        "化科": ["命宫", "官禄宫", "迁移宫"],
        "化忌": ["命宫", "迁移宫", "兄弟宫", "田宅宫", "父母宫"],
    },
    "官禄宫": {
        "化禄": ["命宫", "财帛宫", "迁移宫"],
        "化权": ["命宫", "财帛宫", "迁移宫"],
        "化科": ["命宫", "财帛宫", "迁移宫"],
        "化忌": ["命宫", "兄弟宫", "夫妻宫", "田宅宫", "福德宫"],
    },
    "田宅宫": {
        "化禄": ["兄弟宫", "仆役宫", "福德宫"],
        "化权": ["兄弟宫", "仆役宫", "福德宫"],
        "化科": ["兄弟宫", "仆役宫", "福德宫"],
        "化忌": ["命宫", "兄弟宫", "福德宫", "父母宫", "财帛宫"],
    },
    "父母宫": {
        "化禄": ["子女宫", "疾厄宫", "福德宫"],
        "化权": ["子女宫", "疾厄宫", "福德宫"],
        "化科": ["子女宫", "疾厄宫", "福德宫"],
        "化忌": ["命宫", "兄弟宫", "夫妻宫", "田宅宫", "财帛宫"],
    },
    "福德宫": {
        "化禄": ["夫妻宫", "财帛宫", "田宅宫"],
        "化权": ["夫妻宫", "财帛宫", "田宅宫"],
        "化科": ["夫妻宫", "财帛宫", "田宅宫"],
        "化忌": ["命宫", "兄弟宫", "子女宫", "田宅宫", "父母宫"],
    },
}
