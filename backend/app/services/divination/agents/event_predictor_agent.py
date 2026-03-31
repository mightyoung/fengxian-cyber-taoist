"""
事件成功率分析智能体 - EventPredictorAgent

负责预测某件具体事情的成功率，输出：
- 成功率百分比
- 风险点清单
- 提升建议
- 时机建议
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


# ============ 常量配置 ============

# 事件类型 -> 宫位映射表
EVENT_PALACE_MAPPING = {
    "跳槽": "官禄宫",
    "晋升": "官禄宫",
    "创业": "官禄宫",
    "求职面试": "官禄宫",
    "官司诉讼": "迁移宫",
    "考试升学": "迁移宫",
    "出行远行": "迁移宫",
    "求学申请": "迁移宫",
    "商务签约": "财帛宫",
    "投资理财": "财帛宫",
    "结婚嫁娶": "夫妻宫",
    "搬家乔迁": "田宅宫",
}

# 宫位 -> 五行对应
PALACE_ELEMENT_MAPPING = {
    "命宫": "木",
    "兄弟宫": "金",
    "夫妻宫": "土",
    "子女宫": "木",
    "财帛宫": "金",
    "疾厄宫": "土",
    "迁移宫": "火",
    "交友宫": "金",
    "官禄宫": "火",
    "田宅宫": "水",
    "福德宫": "火",
    "父母宫": "金",
}

# 星曜等级分数
STAR_LEVEL_SCORES = {
    "庙": 100,
    "旺": 80,
    "平": 50,
    "陷": 20,
}

# 四化分数调整
TRANSFORM_SCORES = {
    "化禄": 20,
    "化权": 15,
    "化科": 10,
    "化忌": -20,
}

# 煞星扣分
MALEFIC_PENALTY = -15

# 吉利辅星加分
LUCKY_STAR_BONUS = 8

# 吉格加分
PATTERN_BONUS = 10


# ============ 数据结构 ============

@dataclass
class EventRiskFactor:
    """事件风险因素"""
    factor_type: str  # "risk" 或 "opportunity"
    palace: str  # 相关宫位
    description: str  # 描述
    impact_score: float  # 影响分数（正数有利，负数不利）
    mitigation: Optional[str] = None  # 化解建议

    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor_type": self.factor_type,
            "palace": self.palace,
            "description": self.description,
            "impact_score": self.impact_score,
            "mitigation": self.mitigation,
        }


@dataclass
class EventPredictionResult:
    """事件预测结果"""
    event_type: str  # 事件类型
    target_palace: str  # 关联的宫位
    success_rate: float  # 成功率 0-100
    level: str  # 等级: 极佳/良好/中等/一般/较差
    timing_score: float  # 时机评分 0-100
    service_type: str = "event_prediction"
    risk_factors: List[EventRiskFactor] = field(default_factory=list)
    opportunity_factors: List[EventRiskFactor] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    timing_advice: str = ""  # 时机建议
    overall_reasoning: str = ""  # 整体分析理由
    confidence: float = 0.0  # 置信度 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_type": self.service_type,
            "event_type": self.event_type,
            "target_palace": self.target_palace,
            "success_rate": self.success_rate,
            "level": self.level,
            "timing_score": self.timing_score,
            "risk_factors": [f.to_dict() for f in self.risk_factors],
            "opportunity_factors": [f.to_dict() for f in self.opportunity_factors],
            "suggestions": self.suggestions,
            "timing_advice": self.timing_advice,
            "overall_reasoning": self.overall_reasoning,
            "confidence": self.confidence,
        }


# ============ 核心类 ============

class EventPredictorAgent:
    """
    事件成功率分析智能体

    预测某件具体事情的成功率，输出：
    - 成功率百分比
    - 风险点清单
    - 提升建议
    - 时机建议
    """

    def __init__(
        self,
        chart: Dict[str, Any],  # 用户命盘
        event_type: str,  # 事件类型（如"跳槽"）
        target_year: Optional[int] = None,
        target_month: Optional[int] = None,
    ):
        """
        初始化事件预测

        Args:
            chart: 命盘数据，包含 palaces 等信息
            event_type: 事件类型（如"跳槽"、"投资"等）
            target_year: 目标年份（可选，用于流年分析）
            target_month: 目标月份（可选，用于流月分析）
        """
        self.chart = chart
        self.palaces_data = chart.get("palaces", {})
        self.event_type = event_type
        self.target_year = target_year
        self.target_month = target_month

        # 获取目标宫位
        self.target_palace = EVENT_PALACE_MAPPING.get(
            event_type,
            "命宫"  # 默认命宫
        )

        # 流年流月数据
        self.flowing_year_data = chart.get("flowing_year", {})
        self.flowing_month_data = chart.get("flowing_month", {})

    def _get_palace_stars(self, palace_name: str) -> List[Dict[str, Any]]:
        """获取宫位内的所有星曜"""
        palace_data = self.palaces_data.get(palace_name, {})
        return palace_data.get("stars", [])

    def _get_palace_score(self, palace_name: str) -> float:
        """获取宫位基础评分"""
        palace_data = self.palaces_data.get(palace_name, {})
        return palace_data.get("score", {}).get("total", 50)

    def _classify_stars(self, palace_name: str) -> Dict[str, List[str]]:
        """分类宫位内的星曜"""
        stars = self._get_palace_stars(palace_name)
        result = {
            "main_stars": [],
            "auxiliary_stars": [],
            "malefic_stars": [],
            "transform_stars": [],
        }

        for star in stars:
            star_type = star.get("type", "")
            star_name = star.get("name", "")

            if "正曜" in star_type or star_name in [
                "紫微", "天府", "天机", "太阳", "武曲", "天同", "廉贞",
                "贪狼", "巨门", "天相", "天梁", "七杀", "破军"
            ]:
                result["main_stars"].append(star_name)
            elif "辅星" in star_type or star_name in [
                "左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马"
            ]:
                result["auxiliary_stars"].append(star_name)
            elif "煞星" in star_type or star_name in [
                "擎羊", "陀罗", "火星", "铃星", "地空", "地劫"
            ]:
                result["malefic_stars"].append(star_name)
            elif "化曜" in star_type or star_name in [
                "化禄", "化权", "化科", "化忌"
            ]:
                result["transform_stars"].append(star_name)

        return result

    def _calculate_palace_score(self, palace_name: str) -> float:
        """
        计算宫位分数

        评分规则：
        - 主星庙旺：庙=100, 旺=80, 平=50, 陷=20
        - 化禄入宫：+20分
        - 化权入宫：+15分
        - 化忌入宫：-20分（命宫忌→-25）
        - 化科入宫：+10分
        - 煞星入宫：-15分/颗
        - 吉利辅星入宫：+8分/颗
        """
        base_score = self._get_palace_score(palace_name)
        stars_classified = self._classify_stars(palace_name)

        # 计算星曜调整
        score_adjustment = 0.0

        # 四化星调整
        transform_stars = stars_classified["transform_stars"]
        for transform in transform_stars:
            score_adjustment += TRANSFORM_SCORES.get(transform, 0)
            # 命宫化忌额外扣分
            if transform == "化忌" and palace_name == "命宫":
                score_adjustment -= 5

        # 煞星扣分
        malefic_count = len(stars_classified["malefic_stars"])
        score_adjustment += malefic_count * MALEFIC_PENALTY

        # 吉利辅星加分
        lucky_count = len(stars_classified["auxiliary_stars"])
        score_adjustment += lucky_count * LUCKY_STAR_BONUS

        # 计算最终分数（归一化到0-100）
        final_score = base_score + score_adjustment
        return max(0.0, min(100.0, final_score))

    def _get_star_level(self, palace_name: str, star_name: str) -> str:
        """获取星曜在宫位的庙旺陷等级"""
        palace_data = self.palaces_data.get(palace_name, {})
        stars = palace_data.get("stars", [])

        for star in stars:
            if star.get("name") == star_name:
                return star.get("level", "平")

        return "平"

    def _analyze_risk_factors(self, palace_name: str) -> List[EventRiskFactor]:
        """分析风险因素"""
        risk_factors = []
        stars_classified = self._classify_stars(palace_name)

        transform_stars = stars_classified["transform_stars"]
        malefic_stars = stars_classified["malefic_stars"]
        main_stars = stars_classified["main_stars"]

        # 化忌风险
        if "化忌" in transform_stars:
            risk_factors.append(EventRiskFactor(
                factor_type="risk",
                palace=palace_name,
                description=f"化忌入{palace_name} - 主变化、阻碍，需防波折",
                impact_score=-20,
                mitigation="提前做好准备，循序渐进，避免冲动决策"
            ))

        # 煞星风险
        for star in malefic_stars:
            mitigation_map = {
                "擎羊": "注意人际关系，避免冲突",
                "陀罗": "保持耐心，不要急于求成",
                "火星": "控制情绪，避免冲动",
                "铃星": "谨言慎行，注意口舌是非",
                "地空": "务实规划，避免空想",
                "地劫": "保守理财，避免大额投资"
            }
            risk_factors.append(EventRiskFactor(
                factor_type="risk",
                palace=palace_name,
                description=f"{star}入{palace_name} - 增加变数和风险",
                impact_score=MALEFIC_PENALTY,
                mitigation=mitigation_map.get(star, "谨慎行事")
            ))

        # 多煞星同宫风险
        if len(malefic_stars) >= 2:
            risk_factors.append(EventRiskFactor(
                factor_type="risk",
                palace=palace_name,
                description=f"多煞星同宫（{', '.join(malefic_stars)}） - 运势受阻较多",
                impact_score=-15,
                mitigation="稳扎稳打，不宜冒进，考虑延后行动"
            ))

        # 命宫空宫风险（无正曜）
        if palace_name == "命宫" and not main_stars:
            risk_factors.append(EventRiskFactor(
                factor_type="risk",
                palace="命宫",
                description="命宫空宫 - 运势起伏较大，需借后天努力补足",
                impact_score=-10,
                mitigation="加强自我提升，借助专业指导"
            ))

        # 凶星格局风险
        patterns = self.palaces_data.get(palace_name, {}).get("patterns", [])
        for pattern in patterns:
            if "凶" in pattern.get("type", ""):
                risk_factors.append(EventRiskFactor(
                    factor_type="risk",
                    palace=palace_name,
                    description=f"凶格：{pattern.get('name', '未知格局')}",
                    impact_score=-12,
                    mitigation="尽量避免触发该格局的条件"
                ))

        return risk_factors

    def _analyze_opportunity_factors(self, palace_name: str) -> List[EventRiskFactor]:
        """分析机遇因素"""
        opportunity_factors = []
        stars_classified = self._classify_stars(palace_name)

        transform_stars = stars_classified["transform_stars"]
        auxiliary_stars = stars_classified["auxiliary_stars"]
        main_stars = stars_classified["main_stars"]

        # 化禄机遇
        if "化禄" in transform_stars:
            opportunity_factors.append(EventRiskFactor(
                factor_type="opportunity",
                palace=palace_name,
                description=f"化禄入{palace_name} - 财运佳，机会众多",
                impact_score=20,
                mitigation=None
            ))

        # 化权机遇
        if "化权" in transform_stars:
            opportunity_factors.append(EventRiskFactor(
                factor_type="opportunity",
                palace=palace_name,
                description=f"化权入{palace_name} - 权力增强，执行力提升",
                impact_score=15,
                mitigation=None
            ))

        # 化科机遇
        if "化科" in transform_stars:
            opportunity_factors.append(EventRiskFactor(
                factor_type="opportunity",
                palace=palace_name,
                description=f"化科入{palace_name} - 考运佳，名声声誉提升",
                impact_score=10,
                mitigation=None
            ))

        # 吉利辅星机遇
        for star in auxiliary_stars:
            desc_map = {
                "左辅": "左辅星 - 有贵人相助",
                "右弼": "右弼星 - 人际和谐",
                "文昌": "文昌星 - 学业考运佳",
                "文曲": "文曲星 - 才华表现",
                "天魁": "天魁星 - 考运极佳",
                "天钺": "天钺星 - 机缘深厚",
                "禄存": "禄存星 - 财运稳定",
                "天马": "天马星 - 走动生财"
            }
            opportunity_factors.append(EventRiskFactor(
                factor_type="opportunity",
                palace=palace_name,
                description=f"{desc_map.get(star, star)}入{palace_name}",
                impact_score=LUCKY_STAR_BONUS,
                mitigation=None
            ))

        # 主星庙旺机遇
        for star in main_stars:
            level = self._get_star_level(palace_name, star)
            if level in ["庙", "旺"]:
                level_desc = "庙旺" if level == "庙" else "旺"
                opportunity_factors.append(EventRiskFactor(
                    factor_type="opportunity",
                    palace=palace_name,
                    description=f"{star}星{level_desc} - {star}星能量充沛",
                    impact_score=STAR_LEVEL_SCORES.get(level, 50),
                    mitigation=None
                ))

        # 吉格机遇
        patterns = self.palaces_data.get(palace_name, {}).get("patterns", [])
        for pattern in patterns:
            if "吉" in pattern.get("type", ""):
                opportunity_factors.append(EventRiskFactor(
                    factor_type="opportunity",
                    palace=palace_name,
                    description=f"吉格：{pattern.get('name', '未知格局')}",
                    impact_score=PATTERN_BONUS,
                    mitigation=None
                ))

        return opportunity_factors

    def _calculate_timing_score(self) -> float:
        """计算时机评分"""

        # 流年运势分
        flowing_year_score = self.flowing_year_data.get("score", 50)
        year_score = (flowing_year_score - 50) * 0.5 + 50  # 归一化到40-60范围

        # 流月运势分（如果有）
        if self.target_month and self.flowing_month_data:
            flowing_month_score = self.flowing_month_data.get("score", 50)
            month_score = (flowing_month_score - 50) * 0.3 + 50
        else:
            month_score = 50

        # 综合时机分
        timing_score = (year_score * 0.7 + month_score * 0.3)
        return max(0.0, min(100.0, timing_score))

    def _calculate_success_rate(
        self,
        palace_name: str,
        risk_factors: List[EventRiskFactor],
        opportunity_factors: List[EventRiskFactor]
    ) -> float:
        """
        计算成功率

        成功率 = min(95, max(5, 基础分 + 时机分×0.2 + 机遇加分 - 风险扣分))

        公式说明：
        - 基础分 = 50
        - 时机分 = min(100, max(0, 流年运势分))
        - 机遇加分 = Σ(机遇因素 × 0.15)
        - 风险扣分 = Σ(风险因素 × 0.12)
        """
        base_score = 50.0

        # 时机分
        timing_score = self._calculate_timing_score()

        # 机遇加分
        opportunity_bonus = sum(f.impact_score * 0.15 for f in opportunity_factors)

        # 风险扣分
        risk_penalty = sum(f.impact_score * 0.12 for f in risk_factors)

        # 计算最终成功率
        success_rate = (
            base_score
            + timing_score * 0.2
            + opportunity_bonus
            + risk_penalty
        )

        # 限制范围
        return max(5.0, min(95.0, success_rate))

    def _get_level_from_score(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 85:
            return "极佳"
        elif score >= 70:
            return "良好"
        elif score >= 50:
            return "中等"
        elif score >= 30:
            return "一般"
        else:
            return "较差"

    def _generate_suggestions(
        self,
        event_type: str,
        risk_factors: List[EventRiskFactor],
        opportunity_factors: List[EventRiskFactor]
    ) -> List[str]:
        """生成建议"""
        suggestions = []

        # 基于风险因素的建议
        for risk in risk_factors:
            if risk.mitigation:
                suggestions.append(f"针对{risk.palace}{risk.description.split(' - ')[0]}：{risk.mitigation}")

        # 基于机遇因素的建议
        for opp in opportunity_factors:
            suggestions.append(f"把握{opp.palace}{opp.description.split(' - ')[0]}的机遇")

        # 通用建议
        if not opportunity_factors:
            suggestions.append("当前运势较为平淡，建议观望等待更好的时机")

        if len(risk_factors) >= 3:
            suggestions.append("风险因素较多，建议延后行动或寻求专业人士指导")

        if not risk_factors and opportunity_factors:
            suggestions.append("运势上佳，是推进此事的好时机")

        return suggestions[:5]  # 最多5条建议

    def _generate_timing_advice(self, timing_score: float) -> str:
        """生成时机建议"""
        if timing_score >= 80:
            return "时机极佳，把握当前运势，大胆推进"
        elif timing_score >= 60:
            return "时机良好，可按计划推进，适度把握机遇"
        elif timing_score >= 40:
            return "时机一般，建议稳扎稳打，不宜冒进"
        else:
            return "时机欠佳，建议暂缓，等待更好的时机"

    def _calculate_confidence(
        self,
        palace_name: str,
        risk_factors: List[EventRiskFactor],
        opportunity_factors: List[EventRiskFactor]
    ) -> float:
        """计算置信度"""
        base_confidence = 0.5

        # 宫位星曜信息完整度
        palace_data = self.palaces_data.get(palace_name, {})
        stars_count = len(palace_data.get("stars", []))
        if stars_count >= 5:
            base_confidence += 0.15
        elif stars_count >= 3:
            base_confidence += 0.1

        # 流年信息完整度
        if self.flowing_year_data:
            base_confidence += 0.15

        # 因素明确度
        total_factors = len(risk_factors) + len(opportunity_factors)
        if total_factors >= 3:
            base_confidence += 0.1

        return min(0.95, max(0.3, base_confidence))

    def predict(self) -> EventPredictionResult:
        """执行预测"""
        palace_name = self.target_palace

        # 分析风险因素
        risk_factors = self._analyze_risk_factors(palace_name)

        # 分析机遇因素
        opportunity_factors = self._analyze_opportunity_factors(palace_name)

        # 计算成功率
        success_rate = self._calculate_success_rate(
            palace_name,
            risk_factors,
            opportunity_factors
        )

        # 获取等级
        level = self._get_level_from_score(success_rate)

        # 计算时机分
        timing_score = self._calculate_timing_score()

        # 生成建议
        suggestions = self._generate_suggestions(
            self.event_type,
            risk_factors,
            opportunity_factors
        )

        # 时机建议
        timing_advice = self._generate_timing_advice(timing_score)

        # 整体分析理由
        overall_reasoning = self._generate_reasoning(
            palace_name,
            success_rate,
            risk_factors,
            opportunity_factors
        )

        # 置信度
        confidence = self._calculate_confidence(
            palace_name,
            risk_factors,
            opportunity_factors
        )

        return EventPredictionResult(
            service_type="event_prediction",
            event_type=self.event_type,
            target_palace=palace_name,
            success_rate=round(success_rate, 1),
            level=level,
            timing_score=round(timing_score, 1),
            risk_factors=risk_factors,
            opportunity_factors=opportunity_factors,
            suggestions=suggestions,
            timing_advice=timing_advice,
            overall_reasoning=overall_reasoning,
            confidence=round(confidence, 2)
        )

    def _generate_reasoning(
        self,
        palace_name: str,
        success_rate: float,
        risk_factors: List[EventRiskFactor],
        opportunity_factors: List[EventRiskFactor]
    ) -> str:
        """生成整体分析理由"""
        reasoning_parts = []

        # 基础描述
        reasoning_parts.append(f"针对【{self.event_type}】，重点分析{palace_name}的运势状况。")

        # 星曜情况
        stars_classified = self._classify_stars(palace_name)
        if stars_classified["main_stars"]:
            reasoning_parts.append(f"主星配置：{', '.join(stars_classified['main_stars'])}")
        if stars_classified["transform_stars"]:
            reasoning_parts.append(f"四化状况：{', '.join(stars_classified['transform_stars'])}")

        # 机遇描述
        if opportunity_factors:
            opp_descs = [f.description.split(' - ')[0] for f in opportunity_factors[:3]]
            reasoning_parts.append(f"有利因素：{'；'.join(opp_descs)}")

        # 风险描述
        if risk_factors:
            risk_descs = [f.description.split(' - ')[0] for f in risk_factors[:3]]
            reasoning_parts.append(f"风险因素：{'；'.join(risk_descs)}")

        # 结论
        reasoning_parts.append(f"综合评分：{success_rate:.1f}分（{self._get_level_from_score(success_rate)}）")

        return " ".join(reasoning_parts)


# ============ LLM增强分析 ============

class LLMEventPredictorAnalyzer:
    """事件预测LLM增强器"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data

    async def analyze_with_llm(
        self,
        event_type: str,
        target_year: Optional[int] = None,
        target_month: Optional[int] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度事件预测

        Args:
            event_type: 事件类型
            target_year: 目标年份
            target_month: 目标月份
            temperature: LLM温度参数

        Returns:
            LLM分析结果
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import EVENT_PREDICT_SYSTEM_PROMPT, build_event_predict_user_prompt

        # 首先执行规则基础分析
        rule_result = predict_event_sync(
            chart=self.chart,
            event_type=event_type,
            target_year=target_year,
            target_month=target_month,
        )
        rule_result_dict = rule_result.to_dict() if hasattr(rule_result, 'to_dict') else {
            "success_rate": rule_result.success_rate,
            "timing_score": rule_result.timing_score,
            "confidence": rule_result.confidence,
            "risk_factors": [f.to_dict() for f in rule_result.risk_factors],
            "opportunity_factors": [f.to_dict() for f in rule_result.opportunity_factors],
        }

        # 构建提示词
        user_prompt = build_event_predict_user_prompt(
            self.chart,
            event_type,
            target_year,
            target_month,
            rule_result_dict
        )

        messages = [
            {"role": "system", "content": EVENT_PREDICT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature)

        # 合并规则基础结果和LLM增强结果
        result["rule_based_analysis"] = rule_result_dict

        return result

    def analyze_with_llm_sync(
        self,
        event_type: str,
        target_year: Optional[int] = None,
        target_month: Optional[int] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """同步版本的LLM分析"""
        import asyncio
        return asyncio.run(
            self.analyze_with_llm(event_type, target_year, target_month, temperature)
        )

    async def generate_text_report(
        self,
        event_type: str,
        target_year: Optional[int] = None,
        target_month: Optional[int] = None,
        temperature: float = 0.3
    ) -> str:
        """
        生成文本格式的事件预测报告

        Args:
            event_type: 事件类型
            target_year: 目标年份
            target_month: 目标月份
            temperature: LLM温度参数

        Returns:
            格式化的文本报告
        """
        from .llm_prompts import format_analysis_as_text

        result = await self.analyze_with_llm(event_type, target_year, target_month, temperature)
        return format_analysis_as_text(result)


# ============ 便捷函数 ============

def predict_event_sync(
    chart: Dict[str, Any],
    event_type: str,
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
) -> EventPredictionResult:
    """
    同步便捷函数

    Args:
        chart: 命盘数据
        event_type: 事件类型
        target_year: 目标年份（可选）
        target_month: 目标月份（可选）

    Returns:
        EventPredictionResult: 事件预测结果
    """
    agent = EventPredictorAgent(
        chart=chart,
        event_type=event_type,
        target_year=target_year,
        target_month=target_month,
    )
    return agent.predict()


async def llm_analyze_event_predict(
    chart: Dict[str, Any],
    event_type: str,
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
) -> Dict[str, Any]:
    """
    使用LLM分析事件预测

    Args:
        chart: 命盘数据
        event_type: 事件类型
        target_year: 目标年份
        target_month: 目标月份

    Returns:
        LLM分析结果
    """
    analyzer = LLMEventPredictorAnalyzer(chart)
    return await analyzer.analyze_with_llm(event_type, target_year, target_month)


def llm_analyze_event_predict_sync(
    chart: Dict[str, Any],
    event_type: str,
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
) -> Dict[str, Any]:
    """同步版本的LLM事件预测分析"""
    import asyncio
    return asyncio.run(
        llm_analyze_event_predict(chart, event_type, target_year, target_month)
    )
