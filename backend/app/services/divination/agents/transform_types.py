"""
Transform Types - 四化分析数据类型

包含：
- TransformStar: 四化星曜
- PalaceTransform: 宫位四化
- TransformPathStep: 飞化路径步骤
- TransformPath: 飞化路径
- TransformPathAnalysis: 飞化路径分析结果
- TransformAnalysis: 四化分析结果
- CycleStage: 成住坏空单个阶段
- CycleAnalysis: 成住坏空四化周期分析结果

注意：Enums 和 constants 请使用 transform_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .transform_constants import (
    TransformType,
    TransformPathType,
    TransformCycleType,
)


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
    kong: CycleStage = None  # 空 - 化忌
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
