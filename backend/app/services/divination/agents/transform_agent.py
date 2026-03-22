"""
四化分析智能体
分析十天干四化在十二宫位的飞化情况
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class TransformType(Enum):
    """四化类型"""
    HUA_LU = "化禄"      # 化禄 - 财禄、享受
    HUA_QUAN = "化权"    # 化权 - 权力、成就
    HUA_KE = "化科"      # 化科 - 科名、名誉
    HUA_JI = "化忌"      # 化忌 - 忌恨、阻碍


class TransformCycleType(Enum):
    """
    成住坏空四周期类型

    佛学宇宙观中的成住坏空四劫，对应紫微斗数四化理论：
    - 成（缘起）→ 化禄：万事万物形成的阶段，代表缘起、开始、福德
    - 住（持续）→ 化权：成熟稳定阶段，代表持续、权力、成就
    - 坏（衰减）→ 化科：开始衰败阶段，代表衰减、科名、名誉受损
    - 空（结束）→ 化忌：归于空无阶段，代表结束、忌恨、阻碍

    参考梁若瑜《飞星紫微斗数》中成住坏空与四化对应理论
    """
    CHENG = "成"     # 缘起 - 化禄
    ZHU = "住"      # 持续 - 化权
    HUAI = "坏"     # 衰减 - 化科
    KONG = "空"     # 结束 - 化忌


class TransformInteraction(Enum):
    """四化交互类型"""
    LU_QUAN_KE_JI = "禄权科忌"  # 完整配置
    LU_QUAN_KE = "禄权科"       # 三奇嘉会
    LU_QUAN = "禄权"            # 权禄组合
    LU_KE = "禄科"              # 禄科组合
    QUAN_KE = "权科"            # 权科组合
    LU_JI = "禄忌"              # 禄忌对冲
    QUAN_JI = "权忌"            # 权忌对冲
    KE_JI = "科忌"              # 科忌对冲


class TransformPathType(Enum):
    """飞化路径类型"""
    # 禄转忌：本宫化禄→忌入某宫
    LU_ZHUAN_JI = "禄转忌"
    # 忌转忌：本宫化忌→忌入某宫，再从该宫化忌
    JI_ZHUAN_JI = "忌转忌"
    # 追禄：忌入某宫后，该宫再化禄（同星曜）
    ZHUI_LU = "追禄"
    # 追权：忌入某宫后，该宫再化权（同星曜）
    ZHUI_QUAN = "追权"
    # 追忌：禄入某宫后，该宫再化忌（非必同星曜）
    ZHUI_JI = "追忌"
    # 二度转忌：忌转忌后再转忌
    JI_ZHUAN_JI_2 = "二度转忌"
    # 三度转忌：忌转忌后再转忌再转忌
    JI_ZHUAN_JI_3 = "三度转忌"


@dataclass
class TransformStar:
    """四化星曜"""
    transform_type: TransformType
    star_name: str
    palace: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "type": self.transform_type.value,
            "star": self.star_name,
            "palace": self.palace
        }


@dataclass
class PalaceTransform:
    """宫位四化"""
    palace_name: str
    transforms: List[TransformStar] = field(default_factory=list)

    def has_transform(self, transform_type: TransformType) -> bool:
        return any(t.transform_type == transform_type for t in self.transforms)

    def get_transform(self, transform_type: TransformType) -> Optional[TransformStar]:
        for t in self.transforms:
            if t.transform_type == transform_type:
                return t
        return None


@dataclass
class TransformPathStep:
    """飞化路径步骤"""
    from_palace: str  # 来源宫位
    to_palace: str    # 目标宫位
    transform_type: TransformType  # 四化类型
    star_name: str    # 星曜名称
    is_same_star: bool = True  # 是否同星曜（追禄、追权要求同星曜）
    description: str = ""  # 步骤描述

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_palace,
            "to": self.to_palace,
            "type": self.transform_type.value,
            "star": self.star_name,
            "same_star": self.is_same_star,
            "description": self.description
        }


@dataclass
class TransformPath:
    """飞化路径"""
    path_type: TransformPathType  # 路径类型
    start_palace: str  # 起始宫位
    steps: List[TransformPathStep] = field(default_factory=list)  # 路径步骤
    interpretation: str = ""  # 路径解释
    sequence_count: int = 1  # 连续化忌次数（用于忌转忌系列）

    @property
    def end_palace(self) -> str:
        """路径终点宫位"""
        if self.steps:
            return self.steps[-1].to_palace
        return self.start_palace

    @property
    def is_double_lu(self) -> bool:
        """是否双禄（加倍之得）"""
        return self.path_type == TransformPathType.ZHUI_LU and len(self.steps) >= 2

    @property
    def is_double_ji(self) -> bool:
        """是否双忌（加倍之损）"""
        return self.path_type == TransformPathType.ZHUI_JI and len(self.steps) >= 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_type": self.path_type.value,
            "start": self.start_palace,
            "end": self.end_palace,
            "steps": [s.to_dict() for s in self.steps],
            "interpretation": self.interpretation,
            "sequence_count": self.sequence_count,
            "is_double_lu": self.is_double_lu,
            "is_double_ji": self.is_double_ji
        }


@dataclass
class TransformPathAnalysis:
    """飞化路径分析结果

    Attributes:
        year_stem: 出生年干
        paths: 所有飞化路径
        lu_zhuan_ji_paths: 禄转忌路径
        ji_zhuan_ji_paths: 忌转忌路径
        zhui_lu_paths: 追禄路径
        zhui_quan_paths: 追权路径
        zhui_ji_paths: 追忌路径
        summary: 分析总结
        all_matched_paths: 统一的访问接口，返回所有路径的字典
    """
    year_stem: str
    paths: List[TransformPath] = field(default_factory=list)
    lu_zhuan_ji_paths: List[TransformPath] = field(default_factory=list)
    ji_zhuan_ji_paths: List[TransformPath] = field(default_factory=list)
    zhui_lu_paths: List[TransformPath] = field(default_factory=list)
    zhui_quan_paths: List[TransformPath] = field(default_factory=list)
    zhui_ji_paths: List[TransformPath] = field(default_factory=list)
    summary: str = ""

    @property
    def all_matched_paths(self) -> Dict[str, List[TransformPath]]:
        """统一的访问接口，返回所有类型的路径字典

        Returns:
            包含所有路径类型的字典
        """
        return {
            "all": self.paths,
            "lu_zhuan_ji": self.lu_zhuan_ji_paths,
            "ji_zhuan_ji": self.ji_zhuan_ji_paths,
            "zhui_lu": self.zhui_lu_paths,
            "zhui_quan": self.zhui_quan_paths,
            "zhui_ji": self.zhui_ji_paths
        }

    def get_paths_by_type(self, path_type: str) -> List[TransformPath]:
        """根据路径类型获取对应的路径列表

        Args:
            path_type: 路径类型 ('lu_zhuan_ji', 'ji_zhuan_ji', 'zhui_lu', 'zhui_quan', 'zhui_ji')

        Returns:
            对应类型的路径列表
        """
        path_map = {
            "lu_zhuan_ji": self.lu_zhuan_ji_paths,
            "ji_zhuan_ji": self.ji_zhuan_ji_paths,
            "zhui_lu": self.zhui_lu_paths,
            "zhui_quan": self.zhui_quan_paths,
            "zhui_ji": self.zhui_ji_paths,
            "all": self.paths
        }
        return path_map.get(path_type, [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year_stem": self.year_stem,
            "all_paths": [p.to_dict() for p in self.paths],
            "lu_zhuan_ji": [p.to_dict() for p in self.lu_zhuan_ji_paths],
            "ji_zhuan_ji": [p.to_dict() for p in self.ji_zhuan_ji_paths],
            "zhui_lu": [p.to_dict() for p in self.zhui_lu_paths],
            "zhui_quan": [p.to_dict() for p in self.zhui_quan_paths],
            "zhui_ji": [p.to_dict() for p in self.zhui_ji_paths],
            "summary": self.summary
        }


@dataclass
class TransformAnalysis:
    """四化分析结果"""
    year_stem: str
    transforms: List[TransformStar] = field(default_factory=list)
    palace_transforms: Dict[str, PalaceTransform] = field(default_factory=dict)
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year_stem": self.year_stem,
            "transforms": [t.to_dict() for t in self.transforms],
            "palace_transforms": {
                palace: pt.transforms
                for palace, pt in self.palace_transforms.items()
                if pt.transforms
            },
            "interactions": self.interactions,
            "interpretation": self.interpretation
        }


@dataclass
class CycleStage:
    """成住坏空单个阶段"""
    cycle_type: TransformCycleType  # 周期类型
    transform_type: TransformType  # 对应四化
    palaces: List[str] = field(default_factory=list)  # 落入宫位
    stars: List[str] = field(default_factory=list)  # 星曜列表
    strength: str = ""  # 强弱：强/中/弱
    interpretation: str = ""  # 解释

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_type": self.cycle_type.value,
            "transform_type": self.transform_type.value,
            "palaces": self.palaces,
            "stars": self.stars,
            "strength": self.strength,
            "interpretation": self.interpretation
        }


@dataclass
class CycleAnalysis:
    """
    成住坏空四化周期分析结果

    成住坏空是佛学宇宙观中的四劫，在紫微斗数中与四化有对应关系：
    - 成（缘起）→ 化禄：代表缘起、开始、福德聚集
    - 住（持续）→ 化权：代表稳定、持续、权力成就
    - 坏（衰减）→ 化科：代表衰减、名誉受损、但仍有科名
    - 空（结束）→ 化忌：代表结束、忌恨、阻碍、重新开始

    分析命盘中四化在十二宫的分布，判断成住坏空四阶段的强弱
    """
    year_stem: str
    cheng: CycleStage = None  # 成 - 化禄
    zhu: CycleStage = None   # 住 - 化权
    huai: CycleStage = None  # 坏 - 化科
    kong: CycleStage = None # 空 - 化忌
    dominant_cycle: TransformCycleType = None  # 主宰周期
    weakest_cycle: TransformCycleType = None   # 最弱周期
    cycle_balance: str = ""  # 周期平衡：均衡/偏向某阶段
    overall_interpretation: str = ""  # 总体解释

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year_stem": self.year_stem,
            "cheng": self.cheng.to_dict() if self.cheng else None,
            "zhu": self.zhu.to_dict() if self.zhu else None,
            "huai": self.huai.to_dict() if self.huai else None,
            "kong": self.kong.to_dict() if self.kong else None,
            "dominant_cycle": self.dominant_cycle.value if self.dominant_cycle else None,
            "weakest_cycle": self.weakest_cycle.value if self.weakest_cycle else None,
            "cycle_balance": self.cycle_balance,
            "overall_interpretation": self.overall_interpretation
        }


# 成住坏空与四化对应关系映射表
CYCLE_TO_TRANSFORM: Dict[TransformCycleType, TransformType] = {
    TransformCycleType.CHENG: TransformType.HUA_LU,   # 成 → 化禄
    TransformCycleType.ZHU: TransformType.HUA_QUAN,   # 住 → 化权
    TransformCycleType.HUAI: TransformType.HUA_KE,   # 坏 → 化科
    TransformCycleType.KONG: TransformType.HUA_JI,   # 空 → 化忌
}

# 成住坏空解释词典
CYCLE_INTERPRETATIONS: Dict[TransformCycleType, Dict[str, str]] = {
    TransformCycleType.CHENG: {
        "name": "成",
        "meaning": "缘起、形成、福德聚集",
        "description": "成是万事万物形成的阶段，代表新的缘起开始。此时福德里程碑已经聚气，有积累和收获的可能。化禄代表财禄、享受、缘起。"
    },
    TransformCycleType.ZHU: {
        "name": "住",
        "meaning": "持续、稳定、权力成就",
        "description": "住是事物成熟稳定的阶段，代表持续性和权力欲。化权代表权力、成就、掌控力，事物进入强势期。"
    },
    TransformCycleType.HUAI: {
        "name": "坏",
        "meaning": "衰减、名誉受损、但有科名",
        "description": "坏是事物开始衰败的阶段，但同时也是名誉和声名的体现。化科代表科名、名誉、学术，虽然衰减但仍有体面。"
    },
    TransformCycleType.KONG: {
        "name": "空",
        "meaning": "结束、忌恨、阻碍、重新开始",
        "description": "空是事物归于空无的阶段，代表结束和阻碍。化忌代表忌恨、阻碍，但也意味着一个周期的结束和新周期的开始。"
    }
}


# 十天干四化映射表 (流年四化/生年四化通用表)
# 格式: {天干: {化位: 星曜名}}
# 流年四化: 根据流年天干查表
# 生年四化: 根据出生年天干查表
#
# 正确四化表（根据紫微斗数典籍《紫微斗数全书》《飞星紫微斗数》）
# 一星不可化两曜（如甲年廉贞不能同时化禄和化忌）
# 化禄和化忌可以同星（如庚年太阳禄忌同宫）
HEAVENLY_STEM_TRANSFORMS: Dict[str, Dict[str, str]] = {
    # 甲: 廉贞化禄、破军化权、太阳化科、太阴化忌
    "甲": {
        "禄": "廉贞",   # 甲年: 廉贞化禄
        "权": "破军",   # 甲年: 破军化权
        "科": "太阳",   # 甲年: 太阳化科
        "忌": "太阴"    # 甲年: 太阴化忌
    },
    # 乙: 廉贞化禄、破军化权、武曲化科、太阳化忌
    "乙": {
        "禄": "廉贞",   # 乙年: 廉贞化禄
        "权": "破军",   # 乙年: 破军化权
        "科": "武曲",   # 乙年: 武曲化科
        "忌": "太阳"    # 乙年: 太阳化忌
    },
    # 丙: 天同化禄、天梁化权、太阳化科、天同化忌
    "丙": {
        "禄": "天同",   # 丙年: 天同化禄
        "权": "天梁",   # 丙年: 天梁化权
        "科": "太阳",   # 丙年: 太阳化科
        "忌": "天同"    # 丙年: 天同化忌
    },
    # 丁: 天同化禄、天梁化权、天机化科、太阴化忌
    "丁": {
        "禄": "天同",   # 丁年: 天同化禄
        "权": "天梁",   # 丁年: 天梁化权
        "科": "天机",   # 丁年: 天机化科
        "忌": "太阴"    # 丁年: 太阴化忌
    },
    # 戊: 贪狼化禄、太阴化权、右弼化科、天机化忌
    "戊": {
        "禄": "贪狼",   # 戊年: 贪狼化禄
        "权": "太阴",   # 戊年: 太阴化权
        "科": "右弼",   # 戊年: 右弼化科
        "忌": "天机"    # 戊年: 天机化忌
    },
    # 己: 武曲化禄、贪狼化权、太阴化科、武曲化忌
    "己": {
        "禄": "武曲",   # 己年: 武曲化禄
        "权": "贪狼",   # 己年: 贪狼化权
        "科": "太阴",   # 己年: 太阴化科
        "忌": "武曲"    # 己年: 武曲化忌
    },
    # 庚: 太阳化禄、武曲化权、天府化科、太阳化忌
    "庚": {
        "禄": "太阳",   # 庚年: 太阳化禄
        "权": "武曲",   # 庚年: 武曲化权
        "科": "天府",   # 庚年: 天府化科
        "忌": "太阳"    # 庚年: 太阳化忌（禄忌同宫）
    },
    # 辛: 巨门化禄、太阳化权、天府化科、巨门化忌
    "辛": {
        "禄": "巨门",   # 辛年: 巨门化禄
        "权": "太阳",   # 辛年: 太阳化权
        "科": "天府",   # 辛年: 天府化科
        "忌": "巨门"    # 辛年: 巨门化忌（禄忌同宫）
    },
    # 壬: 天梁化禄、天机化权、紫微化科、天梁化忌
    "壬": {
        "禄": "天梁",   # 壬年: 天梁化禄
        "权": "天机",   # 壬年: 天机化权
        "科": "紫微",   # 壬年: 紫微化科
        "忌": "天梁"    # 壬年: 天梁化忌（禄忌同宫）
    },
    # 癸: 天机化禄、巨门化权、紫微化科、天机化忌
    "癸": {
        "禄": "天机",   # 癸年: 天机化禄
        "权": "巨门",   # 癸年: 巨门化权
        "科": "紫微",   # 癸年: 紫微化科
        "忌": "天机"    # 癸年: 天机化忌（禄忌同宫）
    }
}

# 四化星曜解释
TRANSFORM_INTERPRETATIONS: Dict[str, Dict[str, str]] = {
    "化禄": {
        "破军": "破军化禄，主开创、变革、消耗与收获并存",
        "廉贞": "廉贞化禄，主清明、忠贞、官非与财禄",
        "太阴": "太阴化禄，主财禄、田宅、母亲与女性",
        "天机": "天机化禄，主智慧、策划、兄弟与变动",
        "天同": "天同化禄，主福禄、享受、休闲与小人",
        "巨门": "巨门化禄，主口才、是非、争执与财禄",
        "贪狼": "贪狼化禄，主欲望、桃花、交际与横发",
        "武曲": "武曲化禄，主财星、刚毅、行动与成就",
        "太阳": "太阳化禄，主名望、父亲、事业与财禄",
        "文昌": "文昌化禄，主功名、考试、文化与升迁",
        "天府": "天府化禄，主库府、统筹、领导与稳定",
        "紫微": "紫微化禄，主帝星、权力、贵气与福禄",
        "禄存": "禄存化禄，主禄存本身，财星入库"
    },
    "化权": {
        "廉贞": "廉贞化权，主权威、刚强、官非与纷争",
        "太阳": "太阳化权，主权力、事业、名望与父亲",
        "天机": "天机化权，主权谋、策划、变动与竞争",
        "天同": "天同化权，主稳定、福气、懒散与固执",
        "贪狼": "贪狼化权，主欲望、权力、桃花与争夺",
        "太阴": "太阴化权，主女主、财权、田宅与隐忍",
        "文曲": "文曲化权，主文才、艺术、名声与权谋",
        "文昌": "文昌化权，主功名、考试、学术与权力",
        "紫微": "紫微化权，主帝权、贵气、领导与独断",
        "文曲": "文曲化权同文昌化权"
    },
    "化科": {
        "太阳": "太阳化科，主名望、贵人、考试与飘浮",
        "武曲": "武曲化科，主功名、财星、刚直与清贵",
        "天机": "天机化科，主智慧、策划、学术与清秀",
        "文昌": "文昌化科，主功名、考试、文化与清贵",
        "文曲": "文曲化科，主才艺、艺术、名声与风流",
        "天府": "天府化科，主贵气、库府、稳定与清福",
        "贪狼": "贪狼化科，主才艺、桃花、交际与虚名",
        "天同": "天同化科，主福气、清闲、懒散与虚名"
    },
    "化忌": {
        "太阴": "太阴化忌，主晦暗、田宅、母亲与女性麻烦",
        "巨门": "巨门化忌，主是非、口舌、争执与隐瞒",
        "天梁": "天梁化忌，主是非、孤寡、贵人与灾难",
        "禄存": "禄存化忌主忌恨、财损、欲望与纠纷",
        "天机": "天机化忌，主变动、策划失败、兄弟与是非",
        "天同": "天同化忌，主阻碍、福禄减少、懒散与拖延",
        "文曲": "文曲化忌，主才艺损失、文凭问题、桃花劫",
        "文昌": "文昌化忌，主功名损失、考试失败、文化是非",
        "贪狼": "贪狼化忌，主欲望受阻、桃花劫、争执与损失"
    }
}

# 四化组合解释
INTERACTION_INTERPRETATIONS: Dict[TransformInteraction, str] = {
    TransformInteraction.LU_QUAN_KE_JI: "禄权科忌四化齐全，命运多变，须看具体组合而定吉凶",
    TransformInteraction.LU_QUAN_KE: "三奇嘉会格，名利双收，贵气十足，考试官运均有利",
    TransformInteraction.LU_QUAN: "禄权组合，有权有禄，权力与财富兼备",
    TransformInteraction.LU_KE: "禄科组合，财禄与名望兼具，富贵兼全",
    TransformInteraction.QUAN_KE: "权科组合，权力与名誉兼备，学术权力皆有",
    TransformInteraction.LU_JI: "禄忌对冲，财禄有损耗，先成后败",
    TransformInteraction.QUAN_JI: "权忌对冲，权力有阻碍，权力纷争",
    TransformInteraction.KE_JI: "科忌对冲，名望有损，考试功名有阻碍"
}


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


def llm_analyze_transforms_sync(
    chart_data: Any,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """同步版本的LLM四化分析"""
    import asyncio
    return asyncio.run(llm_analyze_transforms(chart_data, question))
