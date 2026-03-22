"""
MetaphysicsValidator - 命理-社会交叉验证器

对比命理预测与社会模拟结果，计算一致性评分并校准置信度。

依赖:
- scenarios.py: MetaphysicsScenario
- platforms/trend_tracker.py: EmergenceResult
- social_interaction.py: SocialEvent, InteractionMetrics
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from app.services.divination.metaphysics_swarm.scenarios import MetaphysicsScenario, ScenarioType
from app.services.divination.metaphysics_swarm.platforms.trend_tracker import EmergenceResult
from app.services.divination.metaphysics_swarm.social_interaction import InteractionMetrics


# ============ 社会验证因子映射 ============

SOCIAL_VALIDATION_FACTOR = {
    "高度共识": 1.2,    # consensus > 0.85
    "中度共识": 1.0,    # 0.6 < consensus <= 0.85
    "低度共识": 0.85,   # 0.4 < consensus <= 0.6
    "存在分歧": 0.7,    # 0.2 < consensus <= 0.4
    "严重矛盾": 0.5,    # consensus <= 0.2
}


# ============ 预测方向映射 ============

DIRECTION_MAPPING = {
    "大吉": {"positive": 0.9, "negative": 0.1, "neutral": 0.0},
    "吉": {"positive": 0.7, "negative": 0.1, "neutral": 0.2},
    "平": {"positive": 0.3, "negative": 0.3, "neutral": 0.4},
    "凶": {"positive": 0.1, "negative": 0.7, "neutral": 0.2},
    "大凶": {"positive": 0.0, "negative": 0.9, "neutral": 0.1},
}


# ============ 话题类别映射 ============

TOPIC_CATEGORY_MAP = {
    "事业发展方向": "事业",
    "财务投资策略": "财运",
    "人际关系处理": "感情",
    "健康生活方式": "健康",
    "学业进修计划": "学业",
    "家庭责任分担": "感情",
    "退休养老安排": "财运",
    "创业创新机遇": "事业",
    "社会责任担当": "事业",
    "心理健康维护": "健康",
}


# ============ 数据模型 ============

@dataclass
class PalaceAnalysis:
    """宫位分析"""
    palace_name: str
    main_stars: List[str] = field(default_factory=list)
    auxiliary_stars: List[str] = field(default_factory=list)
    transform_stars: List[str] = field(default_factory=list)
    analysis: str = ""
    score: float = 0.5  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palace_name": self.palace_name,
            "main_stars": self.main_stars,
            "auxiliary_stars": self.auxiliary_stars,
            "transform_stars": self.transform_stars,
            "analysis": self.analysis,
            "score": round(self.score, 3),
        }


@dataclass
class Prediction:
    """单条预测"""
    prediction_id: str
    category: str  # 事业/财运/感情/健康/学业
    content: str
    direction: str  # "上升" / "下降" / "平稳" / "波动"
    intensity: float  # 0-1
    timing: Optional[str] = None  # 时间节点描述
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "category": self.category,
            "content": self.content,
            "direction": self.direction,
            "intensity": round(self.intensity, 3),
            "timing": self.timing,
            "confidence": round(self.confidence, 3),
        }


@dataclass
class MetaphysicsPrediction:
    """命理预测结果"""
    chart_id: str
    target_year: int

    # 四化预测
    transforms: Dict[str, List[str]] = field(default_factory=dict)  # {宫位: [四化列表]}

    # 宫位分析
    palace_analysis: Dict[str, PalaceAnalysis] = field(default_factory=dict)  # {宫位: 分析}

    # 预测结论
    predictions: List[Prediction] = field(default_factory=list)

    # 置信度
    original_confidence: float = 0.5

    # 维度分数
    dimension_scores: Dict[str, float] = field(default_factory=dict)  # {维度: 分数}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "target_year": self.target_year,
            "transforms": self.transforms,
            "palace_analysis": {k: v.to_dict() for k, v in self.palace_analysis.items()},
            "predictions": [p.to_dict() for p in self.predictions],
            "original_confidence": round(self.original_confidence, 3),
            "dimension_scores": {k: round(v, 3) for k, v in self.dimension_scores.items()},
        }


@dataclass
class PlatformMetrics:
    """平台指标"""
    platform_name: str
    post_count: int = 0
    engagement_rate: float = 0.0
    sentiment_avg: float = 0.0
    top_topics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform_name": self.platform_name,
            "post_count": self.post_count,
            "engagement_rate": round(self.engagement_rate, 3),
            "sentiment_avg": round(self.sentiment_avg, 3),
            "top_topics": self.top_topics,
        }


@dataclass
class SocialSimulationResult:
    """社交模拟结果"""
    simulation_id: str

    # 共识度
    consensus_score: float  # 0-1

    # 互动密度
    interaction_density: float  # 0-1

    # 情感趋势
    sentiment_trend: str  # "上升" / "下降" / "平稳"
    sentiment_magnitude: float  # 变化幅度

    # 热门话题
    trending_topics: List[str] = field(default_factory=list)

    # 涌现结果
    emergence: EmergenceResult = field(default_factory=EmergenceResult)

    # 平台数据
    platform_metrics: Dict[str, PlatformMetrics] = field(default_factory=dict)

    # 互动指标
    interaction_metrics: InteractionMetrics = field(default_factory=InteractionMetrics)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "consensus_score": round(self.consensus_score, 3),
            "interaction_density": round(self.interaction_density, 3),
            "sentiment_trend": self.sentiment_trend,
            "sentiment_magnitude": round(self.sentiment_magnitude, 3),
            "trending_topics": self.trending_topics,
            "emergence": self.emergence.to_dict() if self.emergence else {},
            "platform_metrics": {k: v.to_dict() for k, v in self.platform_metrics.items()},
            "interaction_metrics": {
                "total_events": self.interaction_metrics.total_events,
                "consensus_score": round(self.interaction_metrics.consensus_score, 3),
                "average_sentiment": round(self.interaction_metrics.average_sentiment, 3),
            },
        }


@dataclass
class Contradiction:
    """矛盾点"""
    contradiction_id: str
    type: str  # "direction" / "timing" / "intensity"
    metaphysics_claim: str
    social_claim: str
    severity: float  # 0-1
    resolution: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contradiction_id": self.contradiction_id,
            "type": self.type,
            "metaphysics_claim": self.metaphysics_claim,
            "social_claim": self.social_claim,
            "severity": round(self.severity, 3),
            "resolution": self.resolution,
        }


@dataclass
class ValidationResult:
    """验证结果"""
    timestamp: datetime = field(default_factory=datetime.now)

    # 一致性评分
    consistency_score: float = 0.0  # 0-1

    # 社会验证因子
    social_validation_factor: float = 1.0  # 0.5-1.2

    # 校准后的置信度
    calibrated_confidence: float = 0.5

    # 矛盾点
    contradictions: List[Contradiction] = field(default_factory=list)

    # 验证详情
    validation_details: Dict[str, Any] = field(default_factory=dict)

    # 验证结论
    conclusion: str = ""  # "高度一致" / "基本一致" / "存在分歧" / "矛盾"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "consistency_score": round(self.consistency_score, 3),
            "social_validation_factor": round(self.social_validation_factor, 3),
            "calibrated_confidence": round(self.calibrated_confidence, 3),
            "contradictions": [c.to_dict() for c in self.contradictions],
            "validation_details": self.validation_details,
            "conclusion": self.conclusion,
        }


# ============ 验证器实现 ============

class MetaphysicsValidator:
    """
    命理-社会交叉验证器

    对比命理预测与社会模拟结果，计算一致性评分并校准置信度。
    """

    def __init__(self):
        """初始化验证器"""
        self.validation_history: List[ValidationResult] = []

    def validate(
        self,
        metaphysics_prediction: MetaphysicsPrediction,
        social_simulation: SocialSimulationResult,
        chart_data: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        对比命理预测与社会模拟结果

        Args:
            metaphysics_prediction: 命理预测结果（四化、宫位分析等）
            social_simulation: 社交模拟结果（共识、趋势、涌现等）
            chart_data: 原始命盘数据

        Returns:
            ValidationResult: 验证结果
        """
        validation_id = str(uuid.uuid4())[:8]

        # 1. 计算各维度一致性评分
        direction_score = self.validate_direction(
            metaphysics_prediction, social_simulation
        )
        timing_score = self.validate_timing(
            metaphysics_prediction, social_simulation
        )
        intensity_score = self.validate_intensity(
            metaphysics_prediction, social_simulation
        )

        # 2. 计算总体一致性评分
        consistency_score = self.calculate_consistency_score(
            metaphysics_result=metaphysics_prediction.to_dict(),
            social_result=social_simulation.to_dict(),
        )

        # 3. 确定社会验证因子
        social_validation_factor = self._get_social_validation_factor(
            social_simulation.consensus_score
        )

        # 4. 识别矛盾点
        contradictions = self.identify_contradictions(
            metaphysics_prediction.to_dict(),
            social_simulation.to_dict(),
        )

        # 5. 校准置信度
        calibrated_confidence = self.calibrate_confidence(
            original_confidence=metaphysics_prediction.original_confidence,
            social_validation_factor=social_validation_factor,
            contradictions=contradictions,
        )

        # 6. 生成验证结论
        conclusion = self._generate_conclusion(consistency_score, contradictions)

        # 7. 构建验证结果
        validation_result = ValidationResult(
            timestamp=datetime.now(),
            consistency_score=consistency_score,
            social_validation_factor=social_validation_factor,
            calibrated_confidence=calibrated_confidence,
            contradictions=contradictions,
            validation_details={
                "direction_score": direction_score,
                "timing_score": timing_score,
                "intensity_score": intensity_score,
                "consensus_level": social_simulation.consensus_score,
                "sentiment_trend": social_simulation.sentiment_trend,
                "emergence_insights": social_simulation.emergence.key_insights
                    if social_simulation.emergence else [],
            },
            conclusion=conclusion,
        )

        # 保存历史记录
        self.validation_history.append(validation_result)

        return validation_result

    def calculate_consistency_score(
        self,
        metaphysics_result: Dict[str, Any],
        social_result: Dict[str, Any],
    ) -> float:
        """
        计算一致性评分 (0-1)

        综合考虑预测方向、强度、时间节点与社交模拟结果的匹配度。

        Args:
            metaphysics_result: 命理预测结果字典
            social_result: 社会模拟结果字典

        Returns:
            一致性评分 0-1
        """
        scores: List[float] = []

        # 1. 预测方向一致性
        predictions = metaphysics_result.get("predictions", [])
        social_sentiment = social_result.get("sentiment_trend", "平稳")

        direction_matches = 0
        for pred in predictions:
            direction = pred.get("direction", "")
            expected_sentiment = self._direction_to_sentiment(direction)

            if expected_sentiment == "上升" and social_sentiment == "上升":
                direction_matches += 1
            elif expected_sentiment == "下降" and social_sentiment == "下降":
                direction_matches += 1
            elif expected_sentiment == "平稳" and social_sentiment == "平稳":
                direction_matches += 1
            elif direction in ["波动", "震荡"]:
                direction_matches += 0.5  # 波动预测较为模糊

        if predictions:
            direction_score = direction_matches / len(predictions)
            scores.append(direction_score)

        # 2. 强度一致性
        predictions_intensity = [p.get("intensity", 0.5) for p in predictions]
        if predictions_intensity:
            avg_intensity = sum(predictions_intensity) / len(predictions_intensity)
            consensus = social_result.get("consensus_score", 0.5)

            # 高强度预测应该与高共识相关
            intensity_consistency = 1.0 - abs(avg_intensity - consensus)
            scores.append(max(0.0, intensity_consistency))

        # 3. 宫位与话题一致性
        palace_analysis = metaphysics_result.get("palace_analysis", {})
        trending_topics = social_result.get("trending_topics", [])

        palace_topic_matches = 0
        palace_topic_total = 0

        for palace_name, analysis in palace_analysis.items():
            if isinstance(analysis, dict):
                palace_topics = analysis.get("transform_stars", [])
            else:
                continue

            for palace_topic in palace_topics:
                for trending_topic in trending_topics:
                    if self._topics_related(palace_topic, trending_topic):
                        palace_topic_matches += 1
                    palace_topic_total += 1

        if palace_topic_total > 0:
            palace_topic_score = palace_topic_matches / palace_topic_total
            scores.append(palace_topic_score)

        # 4. 情感趋势一致性
        emergence = social_result.get("emergence", {})
        if emergence:
            emergence_sentiment = emergence.get("overall_sentiment", 0.0)
            sentiment_trend = emergence.get("sentiment_trend", "平稳")

            # 基于预测方向推断的情感预期
            positive_predictions = sum(
                1 for p in predictions if p.get("direction") in ["上升", "大吉"]
            )
            negative_predictions = sum(
                1 for p in predictions if p.get("direction") in ["下降", "大凶"]
            )

            if positive_predictions > negative_predictions:
                expected_sentiment = 0.3
            elif negative_predictions > positive_predictions:
                expected_sentiment = -0.3
            else:
                expected_sentiment = 0.0

            sentiment_score = 1.0 - abs(emergence_sentiment - expected_sentiment) / 2
            scores.append(max(0.0, sentiment_score))

        # 计算最终评分
        if not scores:
            return 0.5

        return sum(scores) / len(scores)

    def calibrate_confidence(
        self,
        original_confidence: float,
        social_validation_factor: float,
        contradictions: Optional[List[Contradiction]] = None,
    ) -> float:
        """
        校准置信度

        最终置信度 = 原始置信度 × 验证因子 - 矛盾惩罚
        矛盾惩罚 = 矛盾数量 × 0.05 × 矛盾严重度

        Args:
            original_confidence: 原始置信度
            social_validation_factor: 社会验证因子
            contradictions: 矛盾列表

        Returns:
            校准后的置信度
        """
        # 计算矛盾惩罚
        contradiction_penalty = 0.0
        if contradictions:
            contradiction_penalty = sum(c.severity for c in contradictions) * 0.05

        # 校准公式
        calibrated = original_confidence * social_validation_factor - contradiction_penalty

        # 限制在 0.1-0.95 范围内
        return max(0.1, min(0.95, calibrated))

    def identify_contradictions(
        self,
        metaphysics_result: Dict[str, Any],
        social_result: Dict[str, Any],
    ) -> List[Contradiction]:
        """
        识别矛盾点

        Args:
            metaphysics_result: 命理结果字典
            social_result: 社会结果字典

        Returns:
            矛盾点列表
        """
        contradictions: List[Contradiction] = []

        predictions = metaphysics_result.get("predictions", [])
        social_sentiment = social_result.get("sentiment_trend", "平稳")
        emergence = social_result.get("emergence", {})

        for i, pred in enumerate(predictions):
            pred_id = pred.get("prediction_id", f"pred_{i}")
            direction = pred.get("direction", "")
            content = pred.get("content", "")
            intensity = pred.get("intensity", 0.5)

            # 方向矛盾
            expected_sentiment = self._direction_to_sentiment(direction)

            direction_contradiction = False
            social_direction = social_sentiment

            if expected_sentiment == "上升" and social_direction == "下降":
                direction_contradiction = True
                severity = 0.8
            elif expected_sentiment == "下降" and social_direction == "上升":
                direction_contradiction = True
                severity = 0.8
            elif direction == "大吉" and social_direction == "下降":
                direction_contradiction = True
                severity = 0.9
            elif direction == "大凶" and social_direction == "上升":
                direction_contradiction = True
                severity = 0.9

            if direction_contradiction:
                contradiction = Contradiction(
                    contradiction_id=f"contradiction_{pred_id}_direction",
                    type="direction",
                    metaphysics_claim=f"命理预测'{content}'方向为{direction}",
                    social_claim=f"社会模拟显示情感趋势{social_direction}",
                    severity=severity,
                    resolution=self._suggest_resolution(
                        direction, social_sentiment, "direction"
                    ),
                )
                contradictions.append(contradiction)

            # 强度矛盾
            if emergence:
                emergence_sentiment = emergence.get("overall_sentiment", 0.0)
                sentiment_direction = (
                    "positive"
                    if emergence_sentiment > 0.2
                    else "negative" if emergence_sentiment < -0.2 else "neutral"
                )

                # 检查强度不匹配
                if intensity > 0.7 and sentiment_direction == "negative":
                    contradiction = Contradiction(
                        contradiction_id=f"contradiction_{pred_id}_intensity",
                        type="intensity",
                        metaphysics_claim=f"命理预测'{content}'强度较高(intensity={intensity:.2f})",
                        social_claim=f"社会模拟显示负面情感(sentiment={emergence_sentiment:.2f})",
                        severity=0.6,
                        resolution=self._suggest_resolution(
                            direction, sentiment_direction, "intensity"
                        ),
                    )
                    contradictions.append(contradiction)

        # 共识度与预测一致性矛盾
        consensus = social_result.get("consensus_score", 0.5)
        if consensus < 0.3 and len(predictions) > 3:
            # 低共识但有多条预测，可能存在内部矛盾
            contradiction = Contradiction(
                contradiction_id="contradiction_low_consensus",
                type="direction",
                metaphysics_claim=f"命理预测包含{len(predictions)}条预测",
                social_claim=f"社会模拟共识度较低(consensus={consensus:.2f})",
                severity=0.5,
                resolution="建议检查各预测之间是否存在内在一致性",
            )
            contradictions.append(contradiction)

        return contradictions

    def validate_direction(
        self,
        metaphysics_prediction: MetaphysicsPrediction,
        social_simulation: SocialSimulationResult,
    ) -> float:
        """
        验证预测方向是否与社会反馈一致

        Args:
            metaphysics_prediction: 命理预测
            social_simulation: 社会模拟结果

        Returns:
            方向一致性评分 0-1
        """
        if not metaphysics_prediction.predictions:
            return 0.5

        matches = 0
        total = len(metaphysics_prediction.predictions)

        social_trend = social_simulation.sentiment_trend

        for pred in metaphysics_prediction.predictions:
            direction = pred.direction
            expected_trend = self._direction_to_sentiment(direction)

            if expected_trend == social_trend:
                matches += 1
            elif direction in ["波动", "震荡"]:
                # 波动预测较为灵活，更容易匹配
                matches += 0.5

        return matches / total if total > 0 else 0.5

    def validate_timing(
        self,
        metaphysics_prediction: MetaphysicsPrediction,
        social_simulation: SocialSimulationResult,
    ) -> float:
        """
        验证时间节点是否匹配

        Args:
            metaphysics_prediction: 命理预测
            social_simulation: 社会模拟结果

        Returns:
            时间一致性评分 0-1
        """
        # 简化实现：检查是否有时间相关的预测
        timed_predictions = [p for p in metaphysics_prediction.predictions if p.timing]

        if not timed_predictions:
            return 0.5  # 无时间预测，返回中等分

        # 检查互动密度是否与预测的时间节点匹配
        interaction_density = social_simulation.interaction_density

        # 高互动密度可能对应命理中的"变动"时期
        timing_matches = 0
        for pred in timed_predictions:
            timing = pred.timing or ""

            if "变动" in timing or "转折" in timing:
                if interaction_density > 0.6:
                    timing_matches += 1
            elif "平稳" in timing or "稳定" in timing:
                if 0.3 <= interaction_density <= 0.7:
                    timing_matches += 1
            else:
                timing_matches += 0.5  # 模糊时间预测

        return timing_matches / len(timed_predictions)

    def validate_intensity(
        self,
        metaphysics_prediction: MetaphysicsPrediction,
        social_simulation: SocialSimulationResult,
    ) -> float:
        """
        验证预测强度是否与社会反应匹配

        Args:
            metaphysics_prediction: 命理预测
            social_simulation: 社会模拟结果

        Returns:
            强度一致性评分 0-1
        """
        if not metaphysics_prediction.predictions:
            return 0.5

        # 获取社交模拟的情感指标
        emergence = social_simulation.emergence
        if not emergence:
            return 0.5

        overall_sentiment = emergence.overall_sentiment
        sentiment_magnitude = abs(overall_sentiment)

        matches = 0
        total = len(metaphysics_prediction.predictions)

        for pred in metaphysics_prediction.predictions:
            intensity = pred.intensity
            direction = pred.direction

            # 归一化强度到 0-1
            expected_sentiment = self._intensity_to_sentiment(intensity, direction)

            # 计算差异
            sentiment_diff = abs(overall_sentiment - expected_sentiment)

            if sentiment_diff < 0.2:
                matches += 1
            elif sentiment_diff < 0.4:
                matches += 0.5

        return matches / total if total > 0 else 0.5

    def generate_validation_report(
        self,
        validation_result: ValidationResult,
    ) -> str:
        """
        生成验证报告

        Args:
            validation_result: 验证结果

        Returns:
            格式化的验证报告字符串
        """
        lines = [
            "=" * 60,
            "命理-社会交叉验证报告",
            "=" * 60,
            "",
            f"验证时间: {validation_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 一致性评估",
            "-" * 40,
            f"一致性评分: {validation_result.consistency_score:.2%}",
            f"社会验证因子: {validation_result.social_validation_factor:.2f}x",
            f"原始置信度校准后: {validation_result.calibrated_confidence:.2%}",
            "",
            "## 验证结论",
            "-" * 40,
            validation_result.conclusion,
            "",
        ]

        # 添加验证详情
        details = validation_result.validation_details
        if details:
            lines.extend([
                "## 维度评分",
                "-" * 40,
                f"- 方向一致性: {details.get('direction_score', 0):.2%}",
                f"- 时间一致性: {details.get('timing_score', 0):.2%}",
                f"- 强度一致性: {details.get('intensity_score', 0):.2%}",
                "",
                "## 社会模拟参考",
                "-" * 40,
                f"- 共识度: {details.get('consensus_level', 0):.2%}",
                f"- 情感趋势: {details.get('sentiment_trend', '未知')}",
            ])

            emergence_insights = details.get("emergence_insights", [])
            if emergence_insights:
                lines.extend([
                    "",
                    "## 群体涌现洞察",
                    "-" * 40,
                ])
                for insight in emergence_insights:
                    lines.append(f"- {insight}")

        # 添加矛盾点
        contradictions = validation_result.contradictions
        if contradictions:
            lines.extend([
                "",
                "## 检测到的矛盾",
                "-" * 40,
            ])
            for c in contradictions:
                lines.extend([
                    f"[{c.type.upper()}] 严重度: {c.severity:.2%}",
                    f"  命理主张: {c.metaphysics_claim}",
                    f"  社会主张: {c.social_claim}",
                ])
                if c.resolution:
                    lines.append(f"  建议: {c.resolution}")
                lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    # ============ 辅助方法 ============

    def _get_social_validation_factor(self, consensus_score: float) -> float:
        """根据共识度确定社会验证因子"""
        if consensus_score > 0.85:
            return SOCIAL_VALIDATION_FACTOR["高度共识"]
        elif consensus_score > 0.6:
            return SOCIAL_VALIDATION_FACTOR["中度共识"]
        elif consensus_score > 0.4:
            return SOCIAL_VALIDATION_FACTOR["低度共识"]
        elif consensus_score > 0.2:
            return SOCIAL_VALIDATION_FACTOR["存在分歧"]
        else:
            return SOCIAL_VALIDATION_FACTOR["严重矛盾"]

    def _direction_to_sentiment(self, direction: str) -> str:
        """将命理方向转换为社会情感趋势"""
        direction_map = {
            "上升": "上升",
            "大吉": "上升",
            "吉": "上升",
            "下降": "下降",
            "大凶": "下降",
            "凶": "下降",
            "平稳": "平稳",
            "平": "平稳",
            "波动": "平稳",  # 波动对应社会中的相对平稳
            "震荡": "平稳",
        }
        return direction_map.get(direction, "平稳")

    def _intensity_to_sentiment(self, intensity: float, direction: str) -> float:
        """将强度转换为预期情感值"""
        base = 0.0
        if direction in ["上升", "大吉", "吉"]:
            base = 0.3 + intensity * 0.5  # 0.3-0.8
        elif direction in ["下降", "大凶", "凶"]:
            base = -0.3 - intensity * 0.5  # -0.3 to -0.8
        else:
            base = 0.0
        return max(-1.0, min(1.0, base))

    def _topics_related(self, palace_topic: str, social_topic: str) -> bool:
        """判断命理话题与社会话题是否相关"""
        palace_cats = set()
        social_cats = set()

        for meta, cat in TOPIC_CATEGORY_MAP.items():
            if meta in palace_topic:
                palace_cats.add(cat)
            if meta in social_topic:
                social_cats.add(cat)

        return bool(palace_cats & social_cats)

    def _suggest_resolution(
        self, direction: str, social_trend: str, contradiction_type: str
    ) -> str:
        """建议矛盾解决方式"""
        if contradiction_type == "direction":
            if direction in ["上升", "大吉"] and social_trend == "下降":
                return "命理显示有利趋势，但社会环境尚未反映，建议等待时机"
            elif direction in ["下降", "大凶"] and social_trend == "上升":
                return "命理显示挑战，但社会环境积极，可能存在时间偏差"
            else:
                return "建议结合双方信息综合判断"

        elif contradiction_type == "intensity":
            return "可能存在预测强度估计过高的情况，建议适度调低预期"

        elif contradiction_type == "timing":
            return "时间节点可能存在偏差，建议密切关注后续发展"

        return "建议进一步验证预测可靠性"

    def _generate_conclusion(
        self,
        consistency_score: float,
        contradictions: List[Contradiction],
    ) -> str:
        """生成验证结论"""
        high_severity_count = sum(1 for c in contradictions if c.severity > 0.7)

        if consistency_score >= 0.85 and len(contradictions) == 0:
            return "高度一致 - 命理预测与社会模拟完美吻合"
        elif consistency_score >= 0.7 and high_severity_count == 0:
            return "基本一致 - 预测具有较高可信度"
        elif consistency_score >= 0.5:
            return "存在分歧 - 建议参考多方信息综合判断"
        elif consistency_score >= 0.3:
            return "显著分歧 - 需谨慎解读预测结果"
        else:
            return "严重矛盾 - 预测存在重大不确定性，建议重新验证"

    def get_validation_history(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取验证历史

        Args:
            limit: 返回数量限制

        Returns:
            验证历史字典列表
        """
        history = self.validation_history
        if limit:
            history = history[-limit:]
        return [r.to_dict() for r in history]

    def get_average_consistency(self) -> float:
        """获取平均一致性评分"""
        if not self.validation_history:
            return 0.0
        return sum(r.consistency_score for r in self.validation_history) / len(
            self.validation_history
        )
