"""
Multi-Agent Validator Types - 多Agent共识验证数据类型

包含：
- JudgmentType: 判断类型枚举
- AgentView: 标准化Agent观点
- ConsensusResult: 共识检测结果
- Resolution: 分歧解决结果
- FinalConfidence: 综合置信度
- ValidationResult: 验证最终结果

注意：常量定义请使用 multi_agent_validator_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from .multi_agent_validator_constants import ExpertAuthor


class JudgmentType(str, Enum):
    """判断类型"""
    JI = "吉"      # 吉
    PING = "平"    # 平
    XIONG = "凶"   # 凶


@dataclass
class AgentView:
    """标准化Agent观点"""
    agent_name: str           # "StarAgent", "PalaceAgent", etc.
    dimension: str           # "财富", "事业", "感情", "健康"
    judgment: JudgmentType    # 吉 / 平 / 凶
    confidence: float         # 0.0-1.0
    reasoning: str            # 推理过程
    key_factors: List[str]    # 关键因素
    expert_role: Optional[ExpertAuthor] = None  # 专家作者
    validation_results: List[str] = field(default_factory=list)  # 验证结果列表

    def __post_init__(self):
        """验证字段范围"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.judgment not in JudgmentType:
            raise ValueError(f"invalid judgment type: {self.judgment}")


@dataclass
class ConsensusResult:
    """共识检测结果"""
    has_consensus: bool                    # 是否有共识
    agreed_judgment: Optional[JudgmentType]  # 共识判断（无共识时为None）
    agreeing_agents: List[str]              # 达成共识的Agent列表
    consensus_confidence: float             # 共识置信度
    dissenting_views: List[AgentView]       # 分歧观点
    reasoning: str                          # 共识检测推理过程


@dataclass
class Resolution:
    """分歧解决结果"""
    resolved_judgment: JudgmentType        # 最终判断
    weight_scores: Dict[str, float]        # 各判断的加权得分
    deciding_agents: List[str]             # 决定性投票的Agent
    reasoning: str                          # 解决推理过程


@dataclass
class FinalConfidence:
    """综合置信度"""
    causal_confidence: float               # 因果链置信度
    probabilistic_confidence: float         # 案例推理置信度
    multi_agent_confidence: float           # 多Agent共识置信度
    overall_confidence: float               # 综合置信度

    # 权重配置
    CAUSAL_WEIGHT: float = 0.40           # 因果链权重 40%
    PROBABILISTIC_WEIGHT: float = 0.35     # 案例推理权重 35%
    MULTI_AGENT_WEIGHT: float = 0.25       # 多Agent共识权重 25%


@dataclass
class ValidationResult:
    """验证最终结果"""
    dimension: str                          # 分析维度
    final_judgment: JudgmentType           # 最终判断
    final_confidence: FinalConfidence       # 综合置信度
    consensus_result: Optional[ConsensusResult]  # 共识结果（如果有）
    resolution: Optional[Resolution]        # 分歧解决结果（如果有）
    agent_views: List[AgentView]            # 所有Agent观点
    summary: str                            # 结果摘要
