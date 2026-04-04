"""
CaseBasedPredictor Types - 案例推理预测器数据类型

包含：
- ProbabilisticResult: 概率推断结果
- PredictionReport: 预测报告

注意：常量定义请使用 case_based_predictor_constants 模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ProbabilisticResult:
    """
    概率推断结果

    包含预测结果和置信度
    """
    event_type: str                          # 事件类型
    prediction: str                           # 预测描述
    probability: float                       # 概率 (0-1)
    confidence: float                        # 置信度 (0-1)
    similar_cases: List[Dict[str, Any]]      # 相似案例
    reasoning: str                           # 推理过程
    year: int                                # 预测年份

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "prediction": self.prediction,
            "probability": round(self.probability, 3),
            "confidence": round(self.confidence, 3),
            "similar_cases": self.similar_cases,
            "reasoning": self.reasoning,
            "year": self.year
        }


@dataclass
class CasePredictionReport:
    """
    预测报告

    包含多个概率推断结果的汇总
    """
    chart_id: str
    target_year: int
    results: List[ProbabilisticResult]
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "target_year": self.target_year,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
            "metadata": self.metadata
        }
