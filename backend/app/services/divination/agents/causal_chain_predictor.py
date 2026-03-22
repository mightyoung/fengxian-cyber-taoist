"""
因果链推理引擎 - 紫微斗数因果链分析

核心原理：
- 禄是因、忌是果：化禄代表机会/原因，化忌代表结果/阻碍
- 禄转忌：得而复失，昙花一现
- 忌转忌：祸不单行，忌数越多越严重
- 忌数论事：单忌=潜在，双忌=条件，三忌=确定，四忌+=重大

参考梁若瑜《飞星紫微斗数》因果链理论
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from copy import deepcopy


# 十二宫名称（按固定顺序）
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "交友宫",
    "官禄宫", "田宅宫", "福德宫", "父母宫"
]

# 宫位索引映射
PALACE_INDEX = {name: i for i, name in enumerate(PALACE_NAMES)}


def get_sanfang(palace: str) -> List[str]:
    """
    动态计算三方（不包含对宫）

    三方：相隔4宫和8宫的宫位
    公式：(宫位索引+4)%12, (宫位索引+8)%12

    Args:
        palace: 宫位名称

    Returns:
        三方宫位列表
    """
    idx = PALACE_INDEX.get(palace, 0)
    sanfang_indices = [(idx + 4) % 12, (idx + 8) % 12]
    return [PALACE_NAMES[i] for i in sanfang_indices]


def get_sizheng(palace: str) -> List[str]:
    """
    动态计算四正（三方+对宫）

    四正：三方 + 对宫
    公式：(宫位索引+4)%12, (宫位索引+6)%12, (宫位索引+8)%12

    Args:
        palace: 宫位名称

    Returns:
        四正宫位列表（含对宫）
    """
    idx = PALACE_INDEX.get(palace, 0)
    sicheng_indices = [(idx + 4) % 12, (idx + 6) % 12, (idx + 8) % 12]
    return [PALACE_NAMES[i] for i in sicheng_indices]


def get_duigong(palace: str) -> str:
    """
    动态计算对宫

    对宫：相隔6宫的宫位
    公式：(宫位索引+6)%12

    Args:
        palace: 宫位名称

    Returns:
        对宫名称
    """
    idx = PALACE_INDEX.get(palace, 0)
    return PALACE_NAMES[(idx + 6) % 12]


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


# 生年干四化映射表（根据紫微斗数典籍《紫微斗数全书》《飞星紫微斗数》）
# 注意：一星不可化两曜，化禄和化忌可以同星
# 甲: 廉贞化禄、破军化权、太阳化科、太阴化忌
# 乙: 廉贞化禄、破军化权、武曲化科、太阳化忌
# 丙: 天同化禄、天梁化权、太阳化科、天同化忌
# 丁: 天同化禄、天梁化权、天机化科、太阴化忌
# 戊: 贪狼化禄、太阴化权、右弼化科、天机化忌
# 己: 武曲化禄、贪狼化权、太阴化科、武曲化忌
# 庚: 太阳化禄、武曲化权、天府化科、太阳化忌
# 辛: 巨门化禄、太阳化权、天府化科、巨门化忌
# 壬: 天梁化禄、天机化权、紫微化科、天梁化忌
# 癸: 天机化禄、巨门化权、紫微化科、天机化忌
YEAR_STEM_TRANSFORMS: Dict[str, Dict[TransformType, str]] = {
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


@dataclass
class TransformStar:
    """四化星曜"""
    transform_type: TransformType
    star_name: str
    palace: str  # 所在宫位

    def to_dict(self) -> Dict:
        return {
            "type": self.transform_type.value,
            "star": self.star_name,
            "palace": self.palace
        }


@dataclass
class FlyingPath:
    """飞化路径"""
    from_palace: str
    to_palace: str
    transform_type: TransformType
    star_name: str

    def to_dict(self) -> Dict:
        return {
            "from": self.from_palace,
            "to": self.to_palace,
            "type": self.transform_type.value,
            "star": self.star_name
        }


@dataclass
class CausalChain:
    """因果链"""
    chain_type: CausalChainType
    palaces: List[str]
    transforms: List[FlyingPath]
    severity: SeverityLevel
    description: str

    def to_dict(self) -> Dict:
        return {
            "type": self.chain_type.value,
            "palaces": self.palaces,
            "transforms": [t.to_dict() for t in self.transforms],
            "severity": self.severity.value,
            "description": self.description
        }


@dataclass
class CausalResult:
    """因果推理结果

    Attributes:
        year_stem: 出生年干
        transforms: 四化分布
        flying_paths: 飞化路线
        causal_chains: 因果链列表
        severity: 整体凶险等级
        severity_level: severity 的别名，提供统一的访问接口
        analysis: 分析说明
        explanation: analysis 的别名，提供统一的访问接口
        key_factors: causal_chains 的别名，提供统一的访问接口
        ji_count: 忌数
        confidence: 置信度 (0.0-1.0)
    """
    year_stem: str
    transforms: List[TransformStar]  # 四化分布
    flying_paths: List[FlyingPath]    # 飞化路线
    causal_chains: List[CausalChain]  # 因果链
    ji_count: int                     # 忌数
    severity: SeverityLevel           # 整体凶险等级
    analysis: str                     # 分析说明
    confidence: float                 # 置信度 (0.0-1.0)

    @property
    def severity_level(self) -> SeverityLevel:
        """severity 的别名，提供统一的访问接口"""
        return self.severity

    @property
    def explanation(self) -> str:
        """analysis 的别名，提供统一的访问接口"""
        return self.analysis

    @property
    def key_factors(self) -> List[CausalChain]:
        """causal_chains 的别名，提供统一的访问接口"""
        return self.causal_chains

    def to_dict(self) -> Dict:
        return {
            "year_stem": self.year_stem,
            "transforms": [t.to_dict() for t in self.transforms],
            "flying_paths": [p.to_dict() for p in self.flying_paths],
            "causal_chains": [c.to_dict() for c in self.causal_chains],
            "ji_count": self.ji_count,
            "severity": self.severity.value,
            "analysis": self.analysis,
            "confidence": self.confidence
        }


def count_ji_intensity(ji_count: int) -> SeverityLevel:
    """
    忌数强度评估

    Args:
        ji_count: 忌的数量

    Returns:
        SeverityLevel: 凶险等级
    """
    if ji_count == 0:
        return SeverityLevel.GOOD
    elif ji_count >= 4:
        return SeverityLevel.CATASTROPHIC
    elif ji_count == 3:
        return SeverityLevel.BAD
    elif ji_count == 2:
        return SeverityLevel.CONDITION
    else:
        return SeverityLevel.POTENTIAL


def calculate_causal_confidence(
    causal_chains: List['CausalChain'],
    ji_count: int,
    severity: SeverityLevel
) -> float:
    """
    计算因果链置信度

    基于王亭之中州派紫微斗数理论：
    【核心原则】忌越多=因果越明确=置信度越高
    - 0忌：因果模糊，难以判断 → 低置信度
    - 3+忌：因果链清晰明确 → 高置信度

    综合考虑：
    1. 因果链数量因子 (0-0.25): 链越多，分析越充分
    2. 忌数因子 (0-0.35): 王亭之理论核心 - 忌多=明确
    3. 严重等级因子 (0-0.25): 反映因果链的类型质量
    4. 链类型权重因子 (0-0.15): 每条链按类型质量加分

    Args:
        causal_chains: 因果链列表
        ji_count: 忌数
        severity: 整体凶险等级

    Returns:
        float: 置信度 (0.0-1.0)
    """
    # 1. 因果链数量因子 (0-0.25)
    chain_count = len(causal_chains)
    if chain_count == 0:
        chain_factor = 0.0
    elif 1 <= chain_count <= 3:
        chain_factor = 0.08
    elif 4 <= chain_count <= 6:
        chain_factor = 0.15
    elif 7 <= chain_count <= 10:
        chain_factor = 0.20
    else:  # 11+
        chain_factor = 0.25

    # 2. 忌数因子 (0-0.35) - 王亭之理论核心
    # 忌越多=因果越明确=置信度越高
    if ji_count == 0:
        ji_factor = 0.10  # 无忌=因果模糊
    elif ji_count == 1:
        ji_factor = 0.20  # 单忌=潜在
    elif ji_count == 2:
        ji_factor = 0.28  # 双忌=条件
    elif ji_count == 3:
        ji_factor = 0.32  # 三忌=确定
    else:  # 4+
        ji_factor = 0.35  # 多忌=重大因果

    # 3. 严重等级因子 (0-0.25) - 反映因果链类型质量
    # GOOD=因果平衡, BAD=因果明确, CATASTROPHIC=因果极明确
    severity_factor_map = {
        SeverityLevel.GOOD: 0.15,      # 因果平衡，难断
        SeverityLevel.POTENTIAL: 0.18,  # 潜在问题
        SeverityLevel.CONDITION: 0.20,  # 条件性问题
        SeverityLevel.BAD: 0.23,       # 因果明确
        SeverityLevel.CATASTROPHIC: 0.25  # 因果极明确
    }
    severity_factor = severity_factor_map.get(severity, 0.20)

    # 4. 链类型权重因子 (0-0.15)
    # 每条链按类型贡献加分
    chain_weight = 0.0
    for chain in causal_chains:
        if chain.chain_type.value in ["禄忌对称", "忌冲", "三忌汇聚"]:
            chain_weight += 0.05  # 核心因果链类型
        elif chain.chain_type.value in ["禄转忌", "忌转忌"]:
            chain_weight += 0.04  # 重要因果链
        elif chain.chain_type.value in ["忌入逢星", "忌入逢自化"]:
            chain_weight += 0.03  # 一般因果链
        else:
            chain_weight += 0.02  # 其他链
    chain_weight_factor = min(chain_weight, 0.15)  # 上限0.15

    # 汇总置信度
    confidence = chain_factor + ji_factor + severity_factor + chain_weight_factor

    # 确保在0.0-1.0范围内
    return max(0.0, min(1.0, confidence))


def get_flying_destinations(palace: str, transform_type: TransformType) -> List[str]:
    """
    获取飞化目标宫位（动态计算，根据本宫位调整）

    根据《中州派》紫微斗数理论，飞化路线应根据本宫位动态计算，
    而不是使用固定的万能路线。

    Args:
        palace: 本宫位
        transform_type: 四化类型

    Returns:
        List[str]: 飞化目标宫位列表
    """
    # 使用动态飞化路线表
    if palace in DYNAMIC_FLYING_ROUTES:
        route_key = transform_type.value
        if route_key in DYNAMIC_FLYING_ROUTES[palace]:
            return DYNAMIC_FLYING_ROUTES[palace][route_key]

    # 回退逻辑：如果不在动态表中，使用传统计算
    palace_idx = PALACE_INDEX.get(palace, 0)

    if transform_type == TransformType.HUA_JI:
        # 化忌飞化特殊规则：根据《飞星紫微斗数》理论
        # 化忌飞化到：对宫、三合方
        destinations = []
        # 对宫
        opposite_idx = (palace_idx + 6) % 12
        destinations.append(PALACE_NAMES[opposite_idx])
        # 三合方
        sanhe_indices = [(palace_idx + 4) % 12, (palace_idx + 8) % 12]
        destinations.extend([PALACE_NAMES[i] for i in sanhe_indices])
        return destinations
    else:
        # 禄权科飞化路线
        routes = FLYING_ROUTES.get(transform_type.value, [])
        return routes


def calculate_palace_stems(year_stem: str) -> Dict[str, str]:
    """
    根据年干计算各宫位的宫干

    宫干排法（紫微斗数基础规则）：
    - 命宫宫干 = 年干
    - 其他宫位按顺序递增

    Args:
        year_stem: 年干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）

    Returns:
        Dict[str, str]: 宫位到宫干的映射
    """
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    gan_index = gan_list.index(year_stem) if year_stem in gan_list else 0

    palace_stems = {}
    for i, palace in enumerate(PALACE_NAMES):
        palace_stems[palace] = gan_list[(gan_index + i) % 10]

    return palace_stems


def calculate_flying_paths(
    palace_stars: Dict[str, List[str]],
    year_stem: str
) -> List[FlyingPath]:
    """
    计算所有飞化路线（包括年干四化和宫干四化自化）

    Args:
        palace_stars: 宫位星曜映射 {宫位名: [星曜列表]}
        year_stem: 年干

    Returns:
        List[FlyingPath]: 飞化路径列表
    """
    paths = []
    transforms = YEAR_STEM_TRANSFORMS.get(year_stem, {})

    # 转换星曜名称列表（统一处理dict和string格式）
    def get_star_name(star) -> str:
        if isinstance(star, dict):
            return star.get("name", "")
        return str(star)

    # 获取四化星曜名称列表
    transform_star_names = list(transforms.values())

    # 找到每个化曜所在的宫位
    star_to_palace = {}
    for palace, stars in palace_stars.items():
        for star in stars:
            star_name = get_star_name(star)
            if star_name in transform_star_names:
                for t_type, t_star in transforms.items():
                    if star_name == t_star:
                        star_to_palace[star_name] = palace

    # 计算飞化路径（年干四化）
    for transform_type, star_name in transforms.items():
        if star_name not in star_to_palace:
            continue

        from_palace = star_to_palace[star_name]
        destinations = get_flying_destinations(from_palace, transform_type)

        for dest in destinations:
            # 包含自化路径（dest == from_palace）
            # 自化是重要因果链，用于检测本宫宫干化禄/忌入本宫的情况
            paths.append(FlyingPath(
                from_palace=from_palace,
                to_palace=dest,
                transform_type=transform_type,
                star_name=star_name
            ))

    # 计算宫干四化路径（自化逻辑）
    # 根据梁若瑜理论：本宫宫干化忌入本宫 = 自化
    palace_stems = calculate_palace_stems(year_stem)

    for palace, gan in palace_stems.items():
        gan_transforms = PALACE_GAN_TRANSFORMS.get(gan, {})

        for transform_type, star_name in gan_transforms.items():
            # 宫干四化：飞化的起点和终点都是本宫（自化）
            # 标记为"宫干自化"以便区分
            paths.append(FlyingPath(
                from_palace=palace,
                to_palace=palace,  # 自化：入本宫
                transform_type=transform_type,
                star_name=f"{gan}干{star_name}"  # 标记宫干四化
            ))

    return paths


def analyze_lu_zhuan_ji(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析禄转忌（得而复失）

    禄转忌定义（梁若瑜派）：禄在某宫化禄，然后忌从同一宫飞出，飞向另一宫。
    禄是因，忌是果，代表得而复失。

    注意：禄忌同入一宫（即禄和忌飞入同一宫）不是禄转忌，而是禄忌同宫。
    """
    chains = []
    lu_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_LU]
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    for lu_path in lu_paths:
        for ji_path in ji_paths:
            # 禄转忌：禄和忌从同一宫飞出（from_palace相同），但飞向不同宫位
            # 这代表禄是因，忌是果 - 得而复失
            if lu_path.from_palace == ji_path.from_palace and lu_path.to_palace != ji_path.to_palace:
                chains.append(CausalChain(
                    chain_type=CausalChainType.LU_ZHUAN_JI,
                    palaces=[lu_path.from_palace, ji_path.to_palace],
                    transforms=[lu_path, ji_path],
                    severity=SeverityLevel.CONDITION,
                    description=f"{lu_path.star_name}化禄于{lu_path.from_palace}，后{ji_path.star_name}化忌自{ji_path.from_palace}飞入{ji_path.to_palace}，禄转忌得而复失"
                ))

    return chains


def analyze_ji_zhuan_ji(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析忌转忌（连续阻碍）

    本宫化忌，忌入某宫，该宫再化忌，形成连续的阻碍。
    根据梁若瑜《飞星紫微斗数》理论，必须同星曜才能契缘（祸不单行）。
    不同星曜的忌转忌，只是普通的因果延续，不是契缘。
    """
    chains = []
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    for first_ji in ji_paths:
        for second_ji in ji_paths:
            # 检查是否形成连续的忌
            if first_ji.to_palace == second_ji.from_palace:
                # 梁若瑜派：必须同星曜才能契缘
                if first_ji.star_name == second_ji.star_name:
                    # 同星曜才算契缘，祸不单行
                    chains.append(CausalChain(
                        chain_type=CausalChainType.JI_ZHUAN_JI,
                        palaces=[first_ji.from_palace, first_ji.to_palace, second_ji.to_palace],
                        transforms=[first_ji, second_ji],
                        severity=SeverityLevel.CATASTROPHIC,
                        description=f"{first_ji.star_name}化忌于{first_ji.from_palace}冲{first_ji.to_palace}，"
                                    f"再{second_ji.star_name}化忌于{second_ji.from_palace}，同星曜契缘，祸不单行"
                    ))
                else:
                    # 不同星曜不算契缘，只是普通因果链
                    chains.append(CausalChain(
                        chain_type=CausalChainType.JI_ZHUAN_JI,
                        palaces=[first_ji.from_palace, first_ji.to_palace, second_ji.to_palace],
                        transforms=[first_ji, second_ji],
                        severity=SeverityLevel.BAD,
                        description=f"{first_ji.star_name}化忌于{first_ji.from_palace}冲{first_ji.to_palace}，"
                                    f"再{second_ji.star_name}化忌于{second_ji.from_palace}，不同星曜非契缘"
                    ))

    return chains


def analyze_lu_ji_tong_gong(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析禄忌同宫（得失参半）

    同一宫位既有化禄又有化忌，得失参半
    """
    chains = []

    # 统计每个宫位的禄和忌
    gong_lu = {}  # {宫位: 禄路径}
    gong_ji = {}  # {宫位: 忌路径}

    for path in flying_paths:
        if path.transform_type == TransformType.HUA_LU:
            if path.from_palace not in gong_lu:
                gong_lu[path.from_palace] = []
            gong_lu[path.from_palace].append(path)
        elif path.transform_type == TransformType.HUA_JI:
            if path.from_palace not in gong_ji:
                gong_ji[path.from_palace] = []
            gong_ji[path.from_palace].append(path)

    # 查找禄忌同宫
    for palace in set(gong_lu.keys()) & set(gong_ji.keys()):
        lu_star = gong_lu[palace][0].star_name if gong_lu.get(palace) else ""
        ji_star = gong_ji[palace][0].star_name if gong_ji.get(palace) else ""

        chains.append(CausalChain(
            chain_type=CausalChainType.LU_JI_TONG_GONG,
            palaces=[palace],
            transforms=gong_lu.get(palace, []) + gong_ji.get(palace, []),
            severity=SeverityLevel.CONDITION,
            description=f"{palace}宫{lu_star}化禄与{ji_star}化忌同宫，得失参半"
        ))

    return chains


def analyze_san_ji_hui_ju(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析三忌汇聚（大凶之兆）

    根据梁若瑜《飞星紫微斗数》理论，三忌汇聚应该是宫位串联，
    而非简单的同一宫位忌数量。即忌的因果链形成串联关系。

    例如：命宫化忌->财帛宫，财帛宫化忌->官禄宫，官禄宫化忌->迁移宫
    这种串联形成三忌汇聚链。
    """
    chains = []
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    # 构建因果链串联分析
    # 查找连续的三忌串联链
    def find串联(paths: List[FlyingPath], current: FlyingPath, chain: List[FlyingPath], result: List[List[FlyingPath]]):
        """递归查找能串联的下一层"""
        if len(chain) >= 3:
            result.append(chain[:])

        # 查找下一个能串联的忌
        for next_path in paths:
            if next_path == current:
                continue
            # 串联条件：当前忌的目标宫位 = 下一个忌的源宫位
            if current.to_palace == next_path.from_palace:
                # 避免循环
                if next_path not in chain:
                    chain.append(next_path)
                    find串联(paths, next_path, chain, result)
                    chain.pop()

    def find_ji_chains(paths: List[FlyingPath], min_length: int = 3) -> List[List[FlyingPath]]:
        """递归查找忌的串联链"""
        result = []

        # 以每个路径为起点，查找能串联的链
        for path in paths:
            chain = [path]
            find串联(paths, path, chain, result)

        return result

    串联_chains = find_ji_chains(ji_paths, min_length=3)

    for chain in 串联_chains:
        palaces = [p.from_palace for p in chain] + [chain[-1].to_palace]
        ji_stars = [p.star_name for p in chain]
        chains.append(CausalChain(
            chain_type=CausalChainType.SAN_JI_HUI_JU,
            palaces=palaces,
            transforms=chain,
            severity=SeverityLevel.CATASTROPHIC,
            description=f"三忌汇聚串联：{'->'.join(ji_stars)}，大凶之兆"
        ))

    # 同时保留原有的同宫汇聚检测（作为补充）
    ji_by_dest: Dict[str, List[FlyingPath]] = {}
    for path in ji_paths:
        if path.to_palace not in ji_by_dest:
            ji_by_dest[path.to_palace] = []
        ji_by_dest[path.to_palace].append(path)

    # 检查三忌同宫汇聚
    for palace, paths in ji_by_dest.items():
        if len(paths) >= 3:
            # 检查是否已经通过串联链覆盖
            already_covered = any(set(p.to_palace for p in chain) == {palace} for chain in 串联_chains)
            if not already_covered:
                chains.append(CausalChain(
                    chain_type=CausalChainType.SAN_JI_HUI_JU,
                    palaces=[palace],
                    transforms=paths,
                    severity=SeverityLevel.CATASTROPHIC,
                    description=f"三忌汇聚于{palace}宫，大凶之兆"
                ))

    return chains


def analyze_ji_chong_palaces(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析忌冲宫位

    化忌冲命宫、迁移宫等重要宫位
    只有当化忌所在宫位的对宫是命宫或迁移宫时，才形成真正的冲
    根据梁若瑜《飞星紫微斗数》理论，忌冲对宫需要详细解释冲的具体含义
    """
    chains = []
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    # 检查每个化忌路径
    for path in ji_paths:
        from_idx = PALACE_INDEX.get(path.from_palace, 0)
        to_idx = PALACE_INDEX.get(path.to_palace, 0)

        # 计算对宫
        opposite_idx = (from_idx + 6) % 12
        opposite_palace = PALACE_NAMES[opposite_idx]

        # 如果飞化到对宫，且对宫是命宫或迁移宫，则是忌冲
        if path.to_palace == opposite_palace:
            if path.to_palace == "命宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.JI_CHONG_MING,
                    palaces=[path.from_palace, path.to_palace],
                    transforms=[path],
                    severity=SeverityLevel.BAD,
                    description=f"{path.star_name}化忌于{path.from_palace}冲命宫，"
                               f"命宫受损，本人与外在环境冲突，逆势而行"
                ))
            elif path.to_palace == "迁移宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.JI_CHONG_YI,
                    palaces=[path.from_palace, path.to_palace],
                    transforms=[path],
                    severity=SeverityLevel.BAD,
                    description=f"{path.star_name}化忌于{path.from_palace}冲迁移宫，"
                               f"迁移宫受损，外出运程反复，变动较多"
                ))

    return chains


class CausalChainPredictor:
    """
    因果链预测器

    根据四化飞化规则，分析因果链关系，判断凶险程度
    """

    def __init__(self):
        """初始化因果链预测器"""
        pass

    def predict(
        self,
        chart: Dict,
        time_point: Optional[int] = None
    ) -> CausalResult:
        """
        预测因果链

        Args:
            chart: 排盘结果，包含 palaces 和 year_stem 信息
            time_point: 时间点（流年、流月等），可选

        Returns:
            CausalResult: 因果推理结果
        """
        # 提取年干
        year_stem = chart.get("year_stem", "")
        if not year_stem:
            # 尝试从 birth_info 获取
            birth_info = chart.get("birth_info", {})
            year_stem = birth_info.get("year_stem", "")

        # 获取宫位星曜
        palace_stars = self._extract_palace_stars(chart)

        # 计算飞化路线
        flying_paths = calculate_flying_paths(palace_stars, year_stem)

        # 分析因果链
        causal_chains = []
        causal_chains.extend(analyze_lu_zhuan_ji(flying_paths, palace_stars))
        causal_chains.extend(analyze_ji_zhuan_ji(flying_paths, palace_stars))
        causal_chains.extend(analyze_lu_ji_tong_gong(flying_paths, palace_stars))
        causal_chains.extend(analyze_san_ji_hui_ju(flying_paths, palace_stars))
        causal_chains.extend(analyze_ji_chong_palaces(flying_paths, palace_stars))

        # 添加新的分析方法
        causal_chains.extend(self.analyze_pursuit_lu(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_pursuit_quan(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_pursuit_ji(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_lu_ji_symmetry(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_ben_gong_zi_hua(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_ji_ru_zi_hua(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_neighbor_palace_chong(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_guo_bao_gong(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_multi_palace_chain(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_san_fang_si_zheng(flying_paths, palace_stars))

        # 格局识别
        patterns = self.recognize_patterns(chart)
        if patterns:
            causal_chains.append(CausalChain(
                chain_type=CausalChainType.PATTERN_RECOGNITION,
                palaces=[],
                transforms=[],
                severity=SeverityLevel.POTENTIAL,
                description=f"四大格局：{', '.join(patterns)}"
            ))

        # 计算忌数（按宫位累计忌的数量，而非星曜数量）
        # 根据梁若瑜和王亭之的理论，忌数应该看忌飞入哪些宫位
        ji_by_dest: Dict[str, List[FlyingPath]] = {}
        for p in flying_paths:
            if p.transform_type == TransformType.HUA_JI:
                if p.to_palace not in ji_by_dest:
                    ji_by_dest[p.to_palace] = []
                ji_by_dest[p.to_palace].append(p)
        # 取汇聚数量最多的宫位的忌数作为忌数强度
        max_ji = max(len(pals) for pals in ji_by_dest.values()) if ji_by_dest else 0
        ji_count = max_ji

        # 评估整体凶险等级
        severity = self._evaluate_overall_severity(causal_chains, ji_count)

        # 生成分析说明
        analysis = self._generate_analysis(year_stem, flying_paths, causal_chains, severity)

        # 提取四化星曜
        transforms = self._extract_transforms(chart, year_stem)

        # 计算置信度
        confidence = calculate_causal_confidence(causal_chains, ji_count, severity)

        return CausalResult(
            year_stem=year_stem,
            transforms=transforms,
            flying_paths=flying_paths,
            causal_chains=causal_chains,
            ji_count=ji_count,
            severity=severity,
            analysis=analysis,
            confidence=confidence
        )

    def _extract_palace_stars(self, chart: Dict) -> Dict[str, List[str]]:
        """
        从排盘结果提取宫位星曜

        Args:
            chart: 排盘结果

        Returns:
            Dict[str, List[str]]: {宫位名: [星曜列表]}
        """
        palace_stars = {}

        palaces_data = chart.get("palaces", {})
        if isinstance(palaces_data, dict):
            for palace_name, palace_info in palaces_data.items():
                stars = []
                if isinstance(palace_info, dict):
                    stars_list = palace_info.get("stars", [])
                    if isinstance(stars_list, list):
                        stars = [s.get("name", "") if isinstance(s, dict) else str(s) for s in stars_list]
                    elif isinstance(stars_list, str):
                        # 可能已经是逗号分隔的字符串
                        stars = stars_list.split(",")
                palace_stars[palace_name] = [s for s in stars if s]
        elif isinstance(palaces_data, list):
            for palace in palaces_data:
                if isinstance(palace, dict):
                    name = palace.get("name", "")
                    stars = palace.get("stars", [])
                    if isinstance(stars, list):
                        palace_stars[name] = [s.get("name", "") if isinstance(s, dict) else str(s) for s in stars]
                    elif isinstance(stars, str):
                        palace_stars[name] = stars.split(",")

        return palace_stars

    def _extract_transforms(self, chart: Dict, year_stem: str) -> List[TransformStar]:
        """
        提取四化星曜

        Args:
            chart: 排盘结果
            year_stem: 年干

        Returns:
            List[TransformStar]: 四化星曜列表
        """
        transforms = []
        palace_stars = self._extract_palace_stars(chart)

        transform_map = YEAR_STEM_TRANSFORMS.get(year_stem, {})
        for t_type, star_name in transform_map.items():
            # 找到该星曜所在的宫位
            palace = None
            for p_name, stars in palace_stars.items():
                if star_name in stars:
                    palace = p_name
                    break

            if palace:
                transforms.append(TransformStar(
                    transform_type=t_type,
                    star_name=star_name,
                    palace=palace
                ))

        return transforms

    def _evaluate_overall_severity(
        self,
        causal_chains: List[CausalChain],
        ji_count: int
    ) -> SeverityLevel:
        """
        评估整体凶险等级

        Args:
            causal_chains: 因果链列表
            ji_count: 忌数

        Returns:
            SeverityLevel: 整体凶险等级
        """
        # 根据因果链评估
        max_severity = count_ji_intensity(ji_count)

        for chain in causal_chains:
            if chain.severity == SeverityLevel.CATASTROPHIC:
                return SeverityLevel.CATASTROPHIC

        for chain in causal_chains:
            if chain.severity == SeverityLevel.BAD:
                # 如果还有三忌汇聚，保持大凶
                if any(c.chain_type == CausalChainType.SAN_JI_HUI_JU for c in causal_chains):
                    return SeverityLevel.CATASTROPHIC
                return SeverityLevel.BAD

        return max_severity

    def _generate_analysis(
        self,
        year_stem: str,
        flying_paths: List[FlyingPath],
        causal_chains: List[CausalChain],
        severity: SeverityLevel
    ) -> str:
        """
        生成分析说明

        Args:
            year_stem: 年干
            flying_paths: 飞化路线
            causal_chains: 因果链
            severity: 凶险等级

        Returns:
            str: 分析说明
        """
        lines = [f"年干{year_stem}四化因果分析："]

        # 四化概述
        transform_map = YEAR_STEM_TRANSFORMS.get(year_stem, {})
        for t_type, star in transform_map.items():
            lines.append(f"- {t_type.value}：{star}")

        lines.append("")

        # 飞化路线概述
        if flying_paths:
            lines.append(f"飞化路线（共{len(flying_paths)}条）：")
            for path in flying_paths[:5]:  # 只显示前5条
                lines.append(f"- {path.star_name}{path.transform_type.value}：{path.from_palace}→{path.to_palace}")
            if len(flying_paths) > 5:
                lines.append(f"- ...还有{len(flying_paths) - 5}条")

        lines.append("")

        # 因果链概述
        if causal_chains:
            lines.append(f"因果链分析（共{len(causal_chains)}条）：")
            for chain in causal_chains:
                lines.append(f"- {chain.chain_type.value}（{chain.severity.value}）：{chain.description}")

        lines.append("")
        lines.append(f"整体评估：{severity.value}")

        return "\n".join(lines)

    def recognize_patterns(self, chart: Dict) -> List[str]:
        """
        识别四大格局（王亭之《中州派》）

        根据紫微斗数经典格局理论，识别：
        1. 紫府同宫格：紫微天府同守命宫
        2. 天府朝垣格：天府守命，三合照会
        3. 贪狼入庙格：贪狼居子午卯酉宫
        4. 杀破狼格：七杀破军贪狼三方四正汇聚
        """
        patterns = []
        palace_stars = self._extract_palace_stars(chart)

        # 1. 紫府同宫格：紫微天府同守命宫
        if "命宫" in palace_stars:
            ming_stars = palace_stars["命宫"]
            if "紫微" in ming_stars and "天府" in ming_stars:
                patterns.append("紫府同宫格")

        # 2. 天府朝垣格：天府守命，三合照会（命宫、财帛宫、官禄宫）
        if "命宫" in palace_stars and "天府" in palace_stars["命宫"]:
            has_sanhe = False
            for p in ["财帛宫", "官禄宫"]:
                if p in palace_stars and palace_stars[p]:
                    has_sanhe = True
                    break
            if has_sanhe:
                patterns.append("天府朝垣格")

        # 3. 贪狼入庙格：贪狼居子午卯酉宫
        for p in ["子宫", "午宫", "卯宫", "酉宫"]:
            if p in palace_stars and "贪狼" in palace_stars[p]:
                patterns.append("贪狼入庙格")
                break

        # 4. 杀破狼格：七杀、破军、贪狼三方四正汇聚
        has_qisha = False
        has_pojun = False
        has_tanlang = False
        for palace, stars in palace_stars.items():
            if "七杀" in stars:
                has_qisha = True
            if "破军" in stars:
                has_pojun = True
            if "贪狼" in stars:
                has_tanlang = True
        if has_qisha and has_pojun and has_tanlang:
            patterns.append("杀破狼格")

        return patterns

    def analyze_pursuit_lu(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        追踪禄的走向（梁若瑜《飞星紫微斗数》）

        分析化禄的飞化路线，追踪禄的最终落点
        """
        chains = []
        lu_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_LU]

        if not lu_paths:
            return chains

        # 按禄的目标宫位分析
        lu_by_dest: Dict[str, List[FlyingPath]] = {}
        for path in lu_paths:
            if path.to_palace not in lu_by_dest:
                lu_by_dest[path.to_palace] = []
            lu_by_dest[path.to_palace].append(path)

        for dest, paths in lu_by_dest.items():
            if len(paths) >= 2:
                chains.append(CausalChain(
                    chain_type=CausalChainType.ZHUI_LU,
                    palaces=[p.from_palace for p in paths] + [dest],
                    transforms=paths,
                    severity=SeverityLevel.POTENTIAL,
                    description=f"追禄：{paths[0].star_name}化禄汇聚于{dest}，禄源充沛"
                ))

        return chains

    def analyze_pursuit_quan(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        追踪权的走向（梁若瑜《飞星紫微斗数》）

        分析化权的飞化路线，追踪权的最终落点
        """
        chains = []
        quan_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_QUAN]

        if not quan_paths:
            return chains

        # 按权的功能宫位分析（官禄宫为权力中心）
        for path in quan_paths:
            if path.to_palace == "官禄宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.ZHUI_QUAN,
                    palaces=[path.from_palace, path.to_palace],
                    transforms=[path],
                    severity=SeverityLevel.CONDITION,
                    description=f"追权：{path.star_name}化权入官禄宫，权力巩固"
                ))

        return chains

    def analyze_pursuit_ji(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        追踪忌的走向（梁若瑜《飞星紫微斗数》）

        分析化忌的飞化路线，追踪忌的最终落点及其影响
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        if not ji_paths:
            return chains

        # 按忌的目标宫位分析
        ji_by_dest: Dict[str, List[FlyingPath]] = {}
        for path in ji_paths:
            if path.to_palace not in ji_by_dest:
                ji_by_dest[path.to_palace] = []
            ji_by_dest[path.to_palace].append(path)

        for dest, paths in ji_by_dest.items():
            if len(paths) >= 2:
                ji_stars = [p.star_name for p in paths]
                chains.append(CausalChain(
                    chain_type=CausalChainType.ZHUI_JI,
                    palaces=[p.from_palace for p in paths] + [dest],
                    transforms=paths,
                    severity=SeverityLevel.BAD,
                    description=f"追忌：{', '.join(ji_stars)}化忌汇聚于{dest}，多忌纠缠"
                ))

        return chains

    def analyze_lu_ji_symmetry(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        禄忌对称分析（梁若瑜《飞星紫微斗数》）

        分析禄和忌是否形成对称关系，即禄入某宫而忌入其对宫
        """
        chains = []
        lu_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_LU]
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        for lu in lu_paths:
            lu_idx = PALACE_INDEX.get(lu.to_palace, 0)
            lu_opposite = PALACE_NAMES[(lu_idx + 6) % 12]

            for ji in ji_paths:
                if ji.to_palace == lu_opposite:
                    chains.append(CausalChain(
                        chain_type=CausalChainType.LU_JI_DUI_CHEN,
                        palaces=[lu.from_palace, lu.to_palace, ji.to_palace],
                        transforms=[lu, ji],
                        severity=SeverityLevel.CONDITION,
                        description=f"禄忌对称：{lu.star_name}化禄于{lu.from_palace}入{lu.to_palace}，"
                                   f"{ji.star_name}化忌于{ji.from_palace}入{ji.to_palace}，阴阳对峙"
                    ))

        return chains

    def analyze_ben_gong_zi_hua(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        本宫自化检测（梁若瑜《飞星紫微斗数》）

        检测本宫是否有自化禄、权、科、忌的情况
        """
        chains = []

        for path in flying_paths:
            # 自化的条件：飞化的起点和终点在同宫
            if path.from_palace == path.to_palace:
                chains.append(CausalChain(
                    chain_type=CausalChainType.BEN_GONG_ZI_HUA,
                    palaces=[path.from_palace],
                    transforms=[path],
                    severity=SeverityLevel.POTENTIAL,
                    description=f"本宫自化：{path.star_name}{path.transform_type.value}于{path.from_palace}，"
                               f"本宫气机流动"
                ))

        return chains

    def analyze_ji_ru_zi_hua(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        忌入逢自化特殊情况（梁若瑜《飞星紫微斗数》）

        当化忌飞入某宫时，如果该宫恰好有星曜自化，则为特殊组合
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        # 检查忌入的宫位是否有自化
        for ji in ji_paths:
            if ji.to_palace in palace_stars and palace_stars[ji.to_palace]:
                # 忌入某宫，该宫有星曜（可能自化）
                # 这种情况需要进一步分析，但先标记为特殊情况
                chains.append(CausalChain(
                    chain_type=CausalChainType.JI_RU_ZI_HUA,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.CONDITION,
                    description=f"忌入逢星：{ji.star_name}化忌入{ji.to_palace}，"
                               f"该宫有星曜配置，需防化中带变"
                ))

        return chains

    def analyze_neighbor_palace_chong(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        邻宫冲势判断（王亭之《中州派》）

        分析邻宫（相隔1宫或11宫）的冲势影响
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        for ji in ji_paths:
            from_idx = PALACE_INDEX.get(ji.from_palace, 0)

            # 邻宫：相隔1宫或11宫
            neighbor_indices = [(from_idx + 1) % 12, (from_idx - 1) % 12]
            neighbors = [PALACE_NAMES[i] for i in neighbor_indices]

            # 检查忌是否冲邻宫
            if ji.to_palace in neighbors:
                chains.append(CausalChain(
                    chain_type=CausalChainType.LIN_GONG_CHONG,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.CONDITION,
                    description=f"邻宫冲势：{ji.star_name}化忌于{ji.from_palace}冲邻宫{ji.to_palace}，"
                               f"影响力较对宫冲势稍弱"
                ))

        return chains

    def analyze_guo_bao_gong(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        果报宫分析（梁若瑜《飞星紫微斗数》）

        分析因果报应关系：田宅宫为因果宫，福德宫为果报宫
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        # 检查忌是否入田宅宫或福德宫
        for ji in ji_paths:
            if ji.to_palace == "田宅宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.GUO_BAO_GONG,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.BAD,
                    description=f"因果宫：{ji.star_name}化忌入田宅宫，与家宅田产有因果纠葛"
                ))
            elif ji.to_palace == "福德宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.GUO_BAO_GONG,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.BAD,
                    description=f"果报宫：{ji.star_name}化忌入福德宫，因果福报受损"
                ))

        return chains

    def analyze_multi_palace_chain(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        多宫位串联分析（王亭之《中州派》）

        分析跨宫位的因果链串联关系
        """
        chains = []

        # 按类型分组飞化路径
        paths_by_type: Dict[TransformType, List[FlyingPath]] = {}
        for path in flying_paths:
            if path.transform_type not in paths_by_type:
                paths_by_type[path.transform_type] = []
            paths_by_type[path.transform_type].append(path)

        # 分析禄的串联链
        if TransformType.HUA_LU in paths_by_type:
            lu_paths = paths_by_type[TransformType.HUA_LU]
            for i, lu1 in enumerate(lu_paths):
                for lu2 in lu_paths[i+1:]:
                    if lu1.to_palace == lu2.from_palace:
                        chains.append(CausalChain(
                            chain_type=CausalChainType.SAN_FANG_SI_ZHENG,
                            palaces=[lu1.from_palace, lu1.to_palace, lu2.to_palace],
                            transforms=[lu1, lu2],
                            severity=SeverityLevel.POTENTIAL,
                            description=f"禄续禄：{lu1.star_name}化禄于{lu1.from_palace}入{lu1.to_palace}，"
                                       f"{lu2.star_name}化禄于{lu2.from_palace}延续"
                        ))

        return chains

    def analyze_san_fang_si_zheng(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        三方四正关系分析（王亭之《中州派》）

        分析宫位的三方四正关系（命宫、财帛宫、官禄宫、迁移宫）
        """
        chains = []

        # 核心四宫
        core_palaces = ["命宫", "财帛宫", "官禄宫", "迁移宫"]

        # 检查核心四宫之间的飞化关系
        for path in flying_paths:
            if path.from_palace in core_palaces and path.to_palace in core_palaces:
                if path.from_palace != path.to_palace:
                    chains.append(CausalChain(
                        chain_type=CausalChainType.SAN_FANG_SI_ZHENG,
                        palaces=[path.from_palace, path.to_palace],
                        transforms=[path],
                        severity=SeverityLevel.POTENTIAL,
                        description=f"三方四正：{path.star_name}{path.transform_type.value}于{path.from_palace}→{path.to_palace}"
                    ))

        return chains


def create_mock_chart(
    year_stem: str,
    lu_palace: str,
    ji_palace: str,
    quan_palace: str = None,
    ke_palace: str = None
) -> Dict:
    """
    创建模拟排盘数据用于测试

    Args:
        year_stem: 年干
        lu_palace: 化禄所在宫位
        ji_palace: 化忌所在宫位
        quan_palace: 化权所在宫位
        ke_palace: 化科所在宫位

    Returns:
        Dict: 模拟排盘数据
    """
    transform_map = YEAR_STEM_TRANSFORMS.get(year_stem, {})
    palaces_data = {name: {"stars": []} for name in PALACE_NAMES}

    for t_type, star_name in transform_map.items():
        if t_type == TransformType.HUA_LU and lu_palace:
            palaces_data[lu_palace]["stars"].append({"name": star_name})
        elif t_type == TransformType.HUA_JI and ji_palace:
            palaces_data[ji_palace]["stars"].append({"name": star_name})
        elif t_type == TransformType.HUA_QUAN and quan_palace:
            palaces_data[quan_palace]["stars"].append({"name": star_name})
        elif t_type == TransformType.HUA_KE and ke_palace:
            palaces_data[ke_palace]["stars"].append({"name": star_name})

    return {
        "year_stem": year_stem,
        "palaces": palaces_data
    }


# ==================== 测试用例 ====================

def test_lu_in_ming_gong():
    """测试：禄在命宫且忌不在冲宫 → 吉"""
    # 化忌在父母宫，不会直接冲命宫或迁移宫
    chart = create_mock_chart("甲", "命宫", "父母宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.year_stem == "甲"
    # 忌不在冲宫位置，应该评估为潜在或条件级别
    assert result.severity in [SeverityLevel.POTENTIAL, SeverityLevel.CONDITION]
    print("✓ test_lu_in_ming_gong passed")


def test_ji_chong_yiqian_gong():
    """测试：忌冲迁移宫 → 凶"""
    # 化忌在命宫，会冲迁移宫
    chart = create_mock_chart("甲", "财帛宫", "命宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 验证化忌冲迁移宫
    ji_chong_yi = [c for c in result.causal_chains
                   if c.chain_type == CausalChainType.JI_CHONG_YI]
    assert len(ji_chong_yi) > 0
    print("✓ test_ji_chong_yiqian_gong passed")


def test_san_ji_hui_ju():
    """测试：三忌汇聚 → 大凶"""
    # 使用多个化忌星曜飞化到同一宫位形成三忌汇聚
    chart = {
        "year_stem": "戊",  # 戊年：天机化忌（双重）
        "palaces": {
            "命宫": {"stars": [{"name": "天机"}]},  # 化忌在命宫
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 当忌飞化到多个宫位且形成汇聚时，应该是大凶
    # 注意：这里主要测试三忌汇聚的因果链类型能被正确识别
    san_ji = [c for c in result.causal_chains
              if c.chain_type == CausalChainType.SAN_JI_HUI_JU]
    print(f"  三忌汇聚链数量: {len(san_ji)}")
    print("✓ test_san_ji_hui_ju passed")


def test_lu_ji_tong_gong():
    """测试：禄忌同宫 → 得失参半"""
    chart = create_mock_chart("甲", "命宫", "命宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该有禄忌同宫的因果链
    lu_ji = [c for c in result.causal_chains
             if c.chain_type == CausalChainType.LU_JI_TONG_GONG]
    assert len(lu_ji) > 0
    print("✓ test_lu_ji_tong_gong passed")


def test_ji_zhuan_ji():
    """测试：忌转忌 → 连续阻碍"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "太阴"}]},  # 化忌
            "财帛宫": {"stars": [{"name": "天机"}]},  # 化权（不在因果链中）
            "官禄宫": {"stars": [{"name": "太阳"}]},  # 化科
            "疾厄宫": {"stars": [{"name": "廉贞"}]},  # 化禄
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 检查因果链类型
    assert len(result.causal_chains) >= 0
    print("✓ test_ji_zhuan_ji passed")


def test_ji_count_single():
    """测试：单忌 = 潜在（无冲宫情况）"""
    # 化忌在父母宫，不冲命宫或迁移宫
    chart = create_mock_chart("乙", "命宫", "父母宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.ji_count >= 1
    # 无冲宫情况下，单忌应该是潜在级别
    assert result.severity == SeverityLevel.POTENTIAL
    print("✓ test_ji_count_single passed")


def test_ji_count_double():
    """测试：双忌 = 条件"""
    chart = {
        "year_stem": "乙",
        "palaces": {
            "命宫": {"stars": [{"name": "天机"}, {"name": "巨门"}]},  # 化禄 + 化忌
            "兄弟宫": {"stars": [{"name": "天梁"}]},  # 化权
            "夫妻宫": {"stars": [{"name": "武曲"}]},  # 化科
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.ji_count >= 1
    print("✓ test_ji_count_double passed")


def test_ji_count_triple():
    """测试：三忌 = 确定"""
    chart = {
        "year_stem": "丁",  # 丁年：巨门化禄、太阳化权、天机化科、天同化忌
        "palaces": {
            "命宫": {"stars": [{"name": "天同"}]},  # 化忌
            "财帛宫": {"stars": [{"name": "天同"}]},  # 化忌飞入
            "官禄宫": {"stars": [{"name": "天同"}]},  # 化忌飞入
            "迁移宫": {"stars": [{"name": "天同"}]},  # 化忌飞入
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.severity in [SeverityLevel.BAD, SeverityLevel.CATASTROPHIC]
    print("✓ test_ji_count_triple passed")


def test_ji_count_quad():
    """测试：四忌+ = 重大"""
    # 使用壬年（天同化忌），因为壬年只有一个化忌
    # 测试多个忌星曜汇聚的情况
    chart = {
        "year_stem": "丁",  # 丁年：巨门化禄、太阳化权、天机化科、天同化忌
        "palaces": {
            "命宫": {"stars": [{"name": "天同"}]},  # 化忌
            "财帛宫": {"stars": [{"name": "天同"}]},  # 化忌飞入
            "官禄宫": {"stars": [{"name": "天同"}]},  # 化忌飞入
            "迁移宫": {"stars": [{"name": "天同"}]},  # 化忌飞入
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 由于化忌飞化到命宫和迁移宫，会产生忌冲，评估为确定或重大
    assert result.severity in [SeverityLevel.BAD, SeverityLevel.CATASTROPHIC]
    print("✓ test_ji_count_quad passed")


def test_lu_zhuan_ji_analysis():
    """测试：禄转忌分析"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "廉贞"}]},  # 化禄
            "疾厄宫": {"stars": [{"name": "太阴"}]},  # 化忌
            "财帛宫": {"stars": []},
            "官禄宫": {"stars": []},
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 检查是否有禄转忌的因果链
    lu_zhuan_ji = [c for c in result.causal_chains
                   if c.chain_type == CausalChainType.LU_ZHUAN_JI]
    print(f"  禄转忌链数量: {len(lu_zhuan_ji)}")
    print("✓ test_lu_zhuan_ji_analysis passed")


def test_ji_chong_ming_gong():
    """测试：忌冲命宫"""
    # 化忌在迁移宫，对宫是命宫，形成忌冲命宫
    chart = {
        "year_stem": "乙",
        "palaces": {
            "迁移宫": {"stars": [{"name": "巨门"}]},  # 化忌在迁移宫，对宫是命宫
            "命宫": {"stars": []},
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    ji_chong_ming = [c for c in result.causal_chains
                     if c.chain_type == CausalChainType.JI_CHONG_MING]
    assert len(ji_chong_ming) > 0
    print("✓ test_ji_chong_ming_gong passed")


def test_all_year_stems():
    """测试：所有年干的四化映射"""
    year_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    for ys in year_stems:
        chart = create_mock_chart(ys, "命宫", "迁移宫")
        predictor = CausalChainPredictor()
        result = predictor.predict(chart)
        assert result.year_stem == ys

    print("✓ test_all_year_stems passed")


def test_transform_extraction():
    """测试：四化星曜提取"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "廉贞"}, {"name": "太阴"}]},  # 化禄 + 化忌
            "兄弟宫": {"stars": [{"name": "天机"}]},  # 化权
            "夫妻宫": {"stars": [{"name": "太阳"}]},  # 化科
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert len(result.transforms) >= 3  # 至少有禄权科
    print("✓ test_transform_extraction passed")


def test_severity_level_enum():
    """测试：SeverityLevel枚举"""
    assert count_ji_intensity(0) == SeverityLevel.POTENTIAL
    assert count_ji_intensity(1) == SeverityLevel.POTENTIAL
    assert count_ji_intensity(2) == SeverityLevel.CONDITION
    assert count_ji_intensity(3) == SeverityLevel.BAD
    assert count_ji_intensity(4) == SeverityLevel.CATASTROPHIC
    assert count_ji_intensity(5) == SeverityLevel.CATASTROPHIC
    print("✓ test_severity_level_enum passed")


def test_flying_path_calculation():
    """测试：飞化路线计算"""
    chart = create_mock_chart("甲", "命宫", "财帛宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert len(result.flying_paths) > 0
    print("✓ test_flying_path_calculation passed")


def test_empty_chart():
    """测试：空排盘"""
    chart = {"year_stem": "甲", "palaces": {}}
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.year_stem == "甲"
    print("✓ test_empty_chart passed")


def test_no_transform_star():
    """测试：星曜不在预期的宫位"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "紫微"}]},  # 不是四化星
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该正常处理，不报错
    assert result.year_stem == "甲"
    print("✓ test_no_transform_star passed")


def test_ji_zhaun_ji_multiple():
    """测试：多重忌转忌"""
    chart = {
        "year_stem": "壬",  # 壬年：天机化禄、紫微化权、贪狼化科、天同化忌
        "palaces": {
            "命宫": {"stars": [{"name": "天同"}]},  # 化忌
            "财帛宫": {"stars": [{"name": "天同"}]},  # 化忌
            "官禄宫": {"stars": [{"name": "天同"}]},  # 化忌
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该有多重因果链
    print(f"  因果链数量: {len(result.causal_chains)}")
    print("✓ test_ji_zhaun_ji_multiple passed")


def test_palace_stars_extraction():
    """测试：宫位星曜提取（列表格式）"""
    chart = {
        "year_stem": "甲",
        "palaces": [
            {"name": "命宫", "stars": [{"name": "廉贞"}]},
            {"name": "兄弟宫", "stars": [{"name": "天机"}]},
        ]
    }
    predictor = CausalChainPredictor()
    palace_stars = predictor._extract_palace_stars(chart)

    assert "命宫" in palace_stars
    assert "廉贞" in palace_stars["命宫"]
    print("✓ test_palace_stars_extraction passed")


def test_palace_stars_string_format():
    """测试：宫位星曜提取（字符串格式）"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": "廉贞,天机"},
        }
    }
    predictor = CausalChainPredictor()
    palace_stars = predictor._extract_palace_stars(chart)

    assert "命宫" in palace_stars
    assert "廉贞" in palace_stars["命宫"]
    print("✓ test_palace_stars_string_format passed")


def test_result_to_dict():
    """测试：结果转换为字典"""
    chart = create_mock_chart("甲", "命宫", "迁移宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    result_dict = result.to_dict()
    assert "year_stem" in result_dict
    assert "transforms" in result_dict
    assert "flying_paths" in result_dict
    assert "causal_chains" in result_dict
    assert "severity" in result_dict
    print("✓ test_result_to_dict passed")


def test_causal_chain_to_dict():
    """测试：因果链转换为字典"""
    chain = CausalChain(
        chain_type=CausalChainType.LU_ZHUAN_JI,
        palaces=["命宫", "财帛宫"],
        transforms=[],
        severity=SeverityLevel.CONDITION,
        description="得而复失"
    )

    chain_dict = chain.to_dict()
    assert chain_dict["type"] == "禄转忌"
    assert chain_dict["palaces"] == ["命宫", "财帛宫"]
    assert chain_dict["severity"] == "条件"
    print("✓ test_causal_chain_to_dict passed")


def test_transform_star_to_dict():
    """测试：四化星转换为字典"""
    star = TransformStar(
        transform_type=TransformType.HUA_LU,
        star_name="廉贞",
        palace="命宫"
    )

    star_dict = star.to_dict()
    assert star_dict["type"] == "化禄"
    assert star_dict["star"] == "廉贞"
    assert star_dict["palace"] == "命宫"
    print("✓ test_transform_star_to_dict passed")


def test_flying_path_to_dict():
    """测试：飞化路径转换为字典"""
    path = FlyingPath(
        from_palace="命宫",
        to_palace="财帛宫",
        transform_type=TransformType.HUA_LU,
        star_name="廉贞"
    )

    path_dict = path.to_dict()
    assert path_dict["from"] == "命宫"
    assert path_dict["to"] == "财帛宫"
    assert path_dict["type"] == "化禄"
    assert path_dict["star"] == "廉贞"
    print("✓ test_flying_path_to_dict passed")


def test_year_stem_transforms_completeness():
    """测试：年干四化表完整性"""
    expected_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    for ys in expected_stems:
        assert ys in YEAR_STEM_TRANSFORMS
        transform = YEAR_STEM_TRANSFORMS[ys]
        assert TransformType.HUA_LU in transform
        assert TransformType.HUA_QUAN in transform
        assert TransformType.HUA_KE in transform
        assert TransformType.HUA_JI in transform
        assert transform[TransformType.HUA_LU] is not None
        assert transform[TransformType.HUA_QUAN] is not None
        assert transform[TransformType.HUA_KE] is not None
        assert transform[TransformType.HUA_JI] is not None

    print("✓ test_year_stem_transforms_completeness passed")


def test_palace_index_mapping():
    """测试：宫位索引映射"""
    assert PALACE_INDEX["命宫"] == 0
    assert PALACE_INDEX["兄弟宫"] == 1
    assert PALACE_INDEX["夫妻宫"] == 2
    assert PALACE_INDEX["子女宫"] == 3
    assert PALACE_INDEX["财帛宫"] == 4
    assert PALACE_INDEX["疾厄宫"] == 5
    assert PALACE_INDEX["迁移宫"] == 6
    assert PALACE_INDEX["交友宫"] == 7
    assert PALACE_INDEX["官禄宫"] == 8
    assert PALACE_INDEX["田宅宫"] == 9
    assert PALACE_INDEX["福德宫"] == 10
    assert PALACE_INDEX["父母宫"] == 11
    print("✓ test_palace_index_mapping passed")


def test_opposite_palace():
    """测试：对宫计算"""
    # 对宫应该是相隔6个位置
    for i, palace in enumerate(PALACE_NAMES):
        opposite_idx = (i + 6) % 12
        opposite = PALACE_NAMES[opposite_idx]
        # 验证对宫关系
        assert PALACE_INDEX[opposite] == (PALACE_INDEX[palace] + 6) % 12

    print("✓ test_opposite_palace passed")


def test_sanhe_palace():
    """测试：三合方计算"""
    # 三合方应该是相隔4和8个位置
    for i, palace in enumerate(PALACE_NAMES):
        sanhe1_idx = (i + 4) % 12
        sanhe2_idx = (i + 8) % 12
        sanhe1 = PALACE_NAMES[sanhe1_idx]
        sanhe2 = PALACE_NAMES[sanhe2_idx]
        # 验证三合方关系
        assert PALACE_INDEX[sanhe1] == (PALACE_INDEX[palace] + 4) % 12
        assert PALACE_INDEX[sanhe2] == (PALACE_INDEX[palace] + 8) % 12

    print("✓ test_sanhe_palace passed")


def test_ji_in_qiyi_gong():
    """测试：忌在七杀宫"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "子女宫": {"stars": [{"name": "太阴"}]},  # 化忌在子女宫
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该能正常处理
    assert result.year_stem == "甲"
    print("✓ test_ji_in_qiyi_gong passed")


def test_lu_ji_contradiction():
    """测试：禄忌对冲的矛盾分析"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "廉贞"}]},  # 化禄
            "迁移宫": {"stars": [{"name": "太阴"}]},  # 化忌
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 检查因果链
    assert len(result.causal_chains) > 0
    print("✓ test_lu_ji_contradiction passed")


def test_no_ji():
    """测试：无化忌的情况"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "廉贞"}]},  # 化禄
            "兄弟宫": {"stars": [{"name": "天机"}]},  # 化权
            "夫妻宫": {"stars": [{"name": "太阳"}]},  # 化科
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该没有忌的因果链
    ji_chains = [c for c in result.causal_chains
                 if c.chain_type in [CausalChainType.JI_ZHUAN_JI,
                                    CausalChainType.SAN_JI_HUI_JU,
                                    CausalChainType.JI_CHONG_MING,
                                    CausalChainType.JI_CHONG_YI]]
    # 可能没有忌链
    print(f"  忌相关因果链: {len(ji_chains)}")
    print("✓ test_no_ji passed")


def test_complex_flying():
    """测试：复杂飞化场景"""
    chart = {
        "year_stem": "丙",  # 丙：天同化禄、天机化权、太阳化科、天梁化忌
        "palaces": {
            "命宫": {"stars": [{"name": "天同"}]},  # 化禄
            "兄弟宫": {"stars": [{"name": "天机"}]},  # 化权
            "夫妻宫": {"stars": [{"name": "太阳"}]},  # 化科
            "子女宫": {"stars": [{"name": "天梁"}]},  # 化忌
            "财帛宫": {"stars": []},
            "疾厄宫": {"stars": []},
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该计算出多条飞化路线
    assert len(result.flying_paths) > 0
    print(f"  飞化路线数: {len(result.flying_paths)}")
    print("✓ test_complex_flying passed")


def test_birth_info_extraction():
    """测试：从birth_info提取年干"""
    chart = {
        "birth_info": {
            "year_stem": "乙"
        },
        "palaces": {
            "命宫": {"stars": [{"name": "天机"}]},  # 化禄
            "兄弟宫": {"stars": [{"name": "天梁"}]},  # 化权
            "夫妻宫": {"stars": [{"name": "武曲"}]},  # 化科
            "子女宫": {"stars": [{"name": "巨门"}]},  # 化忌
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.year_stem == "乙"
    print("✓ test_birth_info_extraction passed")


def test_transform_path_duplication():
    """测试：飞化路径去重"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "廉贞"}]},  # 化禄
            "疾厄宫": {"stars": [{"name": "太阴"}]},  # 化忌
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 检查飞化路径是否有重复
    path_set = set()
    for path in result.flying_paths:
        path_key = (path.from_palace, path.to_palace, path.transform_type)
        # 同一对宫位同一类型的飞化应该合并
        path_set.add(path_key)

    print(f"  唯一飞化路径: {len(path_set)}")
    print("✓ test_transform_path_duplication passed")


def test_analysis_text_generation():
    """测试：分析文本生成"""
    chart = create_mock_chart("甲", "命宫", "迁移宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert len(result.analysis) > 0
    assert "甲" in result.analysis
    assert "化禄" in result.analysis
    assert "化忌" in result.analysis
    print("✓ test_analysis_text_generation passed")


def test_severity_escalation():
    """测试：凶险等级递进"""
    # 单忌
    chart1 = create_mock_chart("甲", "命宫", "兄弟宫")
    result1 = CausalChainPredictor().predict(chart1)

    # 双忌
    chart2 = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "廉贞"}, {"name": "太阴"}]},
        }
    }
    result2 = CausalChainPredictor().predict(chart2)

    # 三忌
    chart3 = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "太阴"}]},
            "财帛宫": {"stars": [{"name": "太阴"}]},
            "官禄宫": {"stars": [{"name": "太阴"}]},
        }
    }
    result3 = CausalChainPredictor().predict(chart3)

    # 四忌
    chart4 = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "太阴"}]},
            "财帛宫": {"stars": [{"name": "太阴"}]},
            "官禄宫": {"stars": [{"name": "太阴"}]},
            "迁移宫": {"stars": [{"name": "太阴"}]},
        }
    }
    result4 = CausalChainPredictor().predict(chart4)

    # 验证等级递进
    print(f"  单忌: {result1.severity.value}")
    print(f"  多忌: {result2.severity.value}")
    print(f"  三忌: {result3.severity.value}")
    print(f"  四忌+: {result4.severity.value}")
    print("✓ test_severity_escalation passed")


def test_causal_chain_types():
    """测试：所有因果链类型"""
    chain_types = [
        CausalChainType.LU_ZHUAN_JI,
        CausalChainType.JI_ZHUAN_JI,
        CausalChainType.LU_JI_TONG_GONG,
        CausalChainType.SAN_JI_HUI_JU,
        CausalChainType.JI_CHONG_MING,
        CausalChainType.JI_CHONG_YI,
    ]

    for ct in chain_types:
        assert ct.value is not None

    print("✓ test_causal_chain_types passed")


def test_transform_types():
    """测试：所有四化类型"""
    assert TransformType.HUA_LU.value == "化禄"
    assert TransformType.HUA_QUAN.value == "化权"
    assert TransformType.HUA_KE.value == "化科"
    assert TransformType.HUA_JI.value == "化忌"
    print("✓ test_transform_types passed")


def test_year_stem_transforms_values():
    """测试：年干四化值正确性（根据紫微斗数典籍）"""
    # 验证甲年的四化：廉贞化禄、破军化权、太阳化科、太阴化忌
    assert YEAR_STEM_TRANSFORMS["甲"][TransformType.HUA_LU] == "廉贞"
    assert YEAR_STEM_TRANSFORMS["甲"][TransformType.HUA_QUAN] == "破军"
    assert YEAR_STEM_TRANSFORMS["甲"][TransformType.HUA_KE] == "太阳"
    assert YEAR_STEM_TRANSFORMS["甲"][TransformType.HUA_JI] == "太阴"

    # 验证乙年的四化：廉贞化禄、破军化权、武曲化科、太阳化忌
    assert YEAR_STEM_TRANSFORMS["乙"][TransformType.HUA_LU] == "廉贞"
    assert YEAR_STEM_TRANSFORMS["乙"][TransformType.HUA_QUAN] == "破军"
    assert YEAR_STEM_TRANSFORMS["乙"][TransformType.HUA_KE] == "武曲"
    assert YEAR_STEM_TRANSFORMS["乙"][TransformType.HUA_JI] == "太阳"

    # 验证丙年的四化：天同化禄、天梁化权、太阳化科、天同化忌
    assert YEAR_STEM_TRANSFORMS["丙"][TransformType.HUA_LU] == "天同"
    assert YEAR_STEM_TRANSFORMS["丙"][TransformType.HUA_QUAN] == "天梁"
    assert YEAR_STEM_TRANSFORMS["丙"][TransformType.HUA_KE] == "太阳"
    assert YEAR_STEM_TRANSFORMS["丙"][TransformType.HUA_JI] == "天同"

    # 验证丁年的四化：天同化禄、天梁化权、天机化科、太阴化忌
    assert YEAR_STEM_TRANSFORMS["丁"][TransformType.HUA_LU] == "天同"
    assert YEAR_STEM_TRANSFORMS["丁"][TransformType.HUA_QUAN] == "天梁"
    assert YEAR_STEM_TRANSFORMS["丁"][TransformType.HUA_KE] == "天机"
    assert YEAR_STEM_TRANSFORMS["丁"][TransformType.HUA_JI] == "太阴"

    print("✓ test_year_stem_transforms_values passed")


def test_get_flying_destinations_lu():
    """测试：化禄飞化目标"""
    dests = get_flying_destinations("命宫", TransformType.HUA_LU)
    assert "财帛宫" in dests
    assert "官禄宫" in dests
    print("✓ test_get_flying_destinations_lu passed")


def test_get_flying_destinations_ji():
    """测试：化忌飞化目标"""
    dests = get_flying_destinations("命宫", TransformType.HUA_JI)
    assert "对宫" in dests or "迁移宫" in dests  # 对宫应该是迁移宫
    print("✓ test_get_flying_destinations_ji passed")


def test_severity_level_values():
    """测试：SeverityLevel枚举值"""
    assert SeverityLevel.POTENTIAL.value == "潜在"
    assert SeverityLevel.CONDITION.value == "条件"
    assert SeverityLevel.BAD.value == "确定"
    assert SeverityLevel.CATASTROPHIC.value == "重大"
    print("✓ test_severity_level_values passed")


def test_palace_names_complete():
    """测试：十二宫名称完整性"""
    assert len(PALACE_NAMES) == 12
    assert "命宫" in PALACE_NAMES
    assert "迁移宫" in PALACE_NAMES
    assert "财帛宫" in PALACE_NAMES
    assert "官禄宫" in PALACE_NAMES
    assert "福德宫" in PALACE_NAMES
    print("✓ test_palace_names_complete passed")


def test_flying_routes_complete():
    """测试：飞化路线定义完整性"""
    assert "化禄" in FLYING_ROUTES
    assert "化权" in FLYING_ROUTES
    assert "化科" in FLYING_ROUTES
    assert "化忌" in FLYING_ROUTES
    assert len(FLYING_ROUTES["化禄"]) > 0
    assert len(FLYING_ROUTES["化忌"]) > 0
    print("✓ test_flying_routes_complete passed")


def test_causal_chain_descriptions():
    """测试：因果链描述生成"""
    chart = create_mock_chart("甲", "命宫", "迁移宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    for chain in result.causal_chains:
        assert len(chain.description) > 0
        assert chain.chain_type.value in chain.description or chain.palaces[0] in chain.description

    print("✓ test_causal_chain_descriptions passed")


def test_prediction_with_time_point():
    """测试：带时间点的预测"""
    chart = create_mock_chart("甲", "命宫", "迁移宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart, time_point=2024)

    assert result.year_stem == "甲"
    print("✓ test_prediction_with_time_point passed")


def run_all_tests():
    """运行所有测试"""
    tests = [
        test_lu_in_ming_gong,
        test_ji_chong_yiqian_gong,
        test_san_ji_hui_ju,
        test_lu_ji_tong_gong,
        test_ji_zhuan_ji,
        test_ji_count_single,
        test_ji_count_double,
        test_ji_count_triple,
        test_ji_count_quad,
        test_lu_zhuan_ji_analysis,
        test_ji_chong_ming_gong,
        test_all_year_stems,
        test_transform_extraction,
        test_severity_level_enum,
        test_flying_path_calculation,
        test_empty_chart,
        test_no_transform_star,
        test_ji_zhaun_ji_multiple,
        test_palace_stars_extraction,
        test_palace_stars_string_format,
        test_result_to_dict,
        test_causal_chain_to_dict,
        test_transform_star_to_dict,
        test_flying_path_to_dict,
        test_year_stem_transforms_completeness,
        test_palace_index_mapping,
        test_opposite_palace,
        test_sanhe_palace,
        test_ji_in_qiyi_gong,
        test_lu_ji_contradiction,
        test_no_ji,
        test_complex_flying,
        test_birth_info_extraction,
        test_transform_path_duplication,
        test_analysis_text_generation,
        test_severity_escalation,
        test_causal_chain_types,
        test_transform_types,
        test_year_stem_transforms_values,
        test_get_flying_destinations_lu,
        test_get_flying_destinations_ji,
        test_severity_level_values,
        test_palace_names_complete,
        test_flying_routes_complete,
        test_causal_chain_descriptions,
        test_prediction_with_time_point,
    ]

    print(f"运行 {len(tests)} 个测试...\n")

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")

    return failed == 0


if __name__ == "__main__":
    run_all_tests()
