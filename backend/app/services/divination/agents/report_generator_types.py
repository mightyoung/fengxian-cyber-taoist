"""
ReportGenerator Types - Markdown报告生成器数据类型

包含：
- JudgmentType: 判断类型枚举
- DimensionAnalysis: 分维度分析
- CausalChainAnalysis: 因果链推理结果
- CaseBasedAnalysis: 案例推理结果
- MultiAgentAnalysis: 多Agent共识验证结果
- ThreeLayerPredictionReport: 三层融合预测报告
- ReportBundle: 报告集合

注意：常量定义请使用 report_generator_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class JudgmentType(str, Enum):
    """判断类型"""
    JI = "吉"
    PING = "平"
    XIONG = "凶"


@dataclass
class DimensionAnalysis:
    """分维度分析"""
    judgment: str  # 吉/平/凶
    confidence: float  # 0.0-1.0
    reasoning: str  # 推理过程

    def to_dict(self) -> Dict[str, Any]:
        return {
            "judgment": self.judgment,
            "confidence": round(self.confidence, 3),
            "reasoning": self.reasoning
        }


@dataclass
class CausalChainAnalysis:
    """因果链推理结果"""
    severity_level: str  # 潜在/条件/确定/重大
    chain_type: str  # 因果链类型
    key_chains: List[Dict[str, Any]]  # 关键因果链
    explanation: str  # 解释
    confidence: float  # 置信度

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity_level": self.severity_level,
            "chain_type": self.chain_type,
            "key_chains": self.key_chains,
            "explanation": self.explanation,
            "confidence": round(self.confidence, 3)
        }


@dataclass
class CaseBasedAnalysis:
    """案例推理结果"""
    similar_cases: List[Dict[str, Any]]  # 相似命盘案例
    predictions: Dict[str, Dict[str, Any]]  # 各维度预测
    probability_summary: str  # 概率总结
    confidence: float  # 置信度

    def to_dict(self) -> Dict[str, Any]:
        return {
            "similar_cases": self.similar_cases,
            "predictions": self.predictions,
            "probability_summary": self.probability_summary,
            "confidence": round(self.confidence, 3)
        }


@dataclass
class MultiAgentAnalysis:
    """多Agent共识验证结果"""
    agent_views: List[Dict[str, Any]]  # 各Agent观点
    consensus: Optional[Dict[str, Any]]  # 共识结果
    final_judgment: str  # 最终判断
    confidence: float  # 置信度

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "agent_views": self.agent_views,
            "final_judgment": self.final_judgment,
            "confidence": round(self.confidence, 3)
        }
        if self.consensus:
            result["consensus"] = self.consensus
        return result


@dataclass
class ThreeLayerPredictionReport:
    """三层融合预测报告"""
    # 综合判断
    overall_judgment: str  # 吉/平/凶
    overall_confidence: float  # 0.0-1.0

    # 三层分析结果
    causal_chain_result: Optional[CausalChainAnalysis] = None
    case_based_result: Optional[CaseBasedAnalysis] = None
    multi_agent_result: Optional[MultiAgentAnalysis] = None

    # 分维度分析
    dimensions: Dict[str, DimensionAnalysis] = field(default_factory=dict)

    # 因果链解释
    causal_explanation: str = ""

    # 参考案例
    reference_cases: List[Dict[str, Any]] = field(default_factory=list)

    # 趋避建议
    suggestions: List[str] = field(default_factory=list)

    # 元数据
    target_year: int = 0
    chart_id: str = ""
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_judgment": self.overall_judgment,
            "overall_confidence": round(self.overall_confidence, 3),
            "causal_chain_result": self.causal_chain_result.to_dict() if self.causal_chain_result else None,
            "case_based_result": self.case_based_result.to_dict() if self.case_based_result else None,
            "multi_agent_result": self.multi_agent_result.to_dict() if self.multi_agent_result else None,
            "dimensions": {k: v.to_dict() for k, v in self.dimensions.items()},
            "causal_explanation": self.causal_explanation,
            "reference_cases": self.reference_cases,
            "suggestions": self.suggestions,
            "target_year": self.target_year,
            "chart_id": self.chart_id,
            "generated_at": self.generated_at
        }


@dataclass
class ReportBundle:
    """报告集合"""
    main_report: str           # Markdown主报告
    sub_reports: Dict[str, str]  # Markdown分报告 {section: content}
    metadata: Dict[str, Any]     # 报告元数据
    generated_at: str           # 生成时间

    def to_dict(self) -> Dict[str, Any]:
        return {
            "main_report": self.main_report,
            "sub_reports": self.sub_reports,
            "metadata": self.metadata,
            "generated_at": self.generated_at
        }
