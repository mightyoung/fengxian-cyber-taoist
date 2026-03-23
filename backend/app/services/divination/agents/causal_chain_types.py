"""
因果链数据类型模块 - 紫微斗数因果分析数据类

包含：
- TransformStar: 四化星曜
- FlyingPath: 飞化路径
- CausalChain: 因果链
- CausalResult: 因果推理结果
"""

from typing import Dict, List
from dataclasses import dataclass

from .causal_chain_constants import TransformType, CausalChainType, SeverityLevel


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
