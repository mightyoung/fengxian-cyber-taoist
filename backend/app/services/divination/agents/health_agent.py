"""
HealthAgent - 健康分析智能体

负责分析命盘中的健康信息，包括：
- 疾厄宫星曜配置
- 体质强弱判断
- 潜在健康风险
- 养生建议
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
import os


class HealthLevel(Enum):
    """健康等级"""
    EXCELLENT = "excellent"      # 非常健康
    GOOD = "good"               # 健康
    FAIR = "fair"               # 亚健康
    WEAK = "weak"               # 体弱
    VERY_WEAK = "very_weak"     # 多病


class HealthRisk(Enum):
    """健康风险类型"""
    INHERENT = "inherent"        # 先天体质
    ACQUIRED = "acquired"       # 后天养成
    SEASONAL = "seasonal"       # 季节性
    EMOTIONAL = "emotional"      # 情绪相关


@dataclass
class HealthStar:
    """健康相关星曜"""
    star: str
    is_harmful: bool  # 是否为煞星
    impact: str  # 影响描述


@dataclass
class PalaceHealth:
    """宫位健康分析"""
    palace: str
    health_score: int  # 1-100
    level: HealthLevel
    stars: List[HealthStar]
    risks: List[str]
    warnings: List[str]


@dataclass
class HealthAnalysis:
    """健康分析结果"""
    inherent_strength: int  # 先天体质 1-100
    current_health: int    # 当前健康状况 1-100
    health_level: HealthLevel
    disease_palace_analysis: PalaceHealth
    weak_body_parts: List[str]      # 虚弱部位
    risk_factors: List[str]         # 风险因素
    seasonal_risks: List[str]       # 季节性风险
    recommendations: List[str]       # 养生建议

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inherent_strength": self.inherent_strength,
            "current_health": self.current_health,
            "health_level": self.health_level.value,
            "disease_palace": self.disease_palace_analysis.__dict__,
            "weak_body_parts": self.weak_body_parts,
            "risk_factors": self.risk_factors,
            "seasonal_risks": self.seasonal_risks,
            "recommendations": self.recommendations
        }


# 健康相关星曜映射
HEALTH_STAR_EFFECTS = {
    # 紫微系 - 影响头部、脑部
    "紫微": {"body": "头部", "type": "功能性问题", "is_harmful": False},
    "天机": {"body": "神经系统", "type": "过度思考", "is_harmful": False},
    "太阳": {"body": "眼部", "type": "火气过旺", "is_harmful": False},

    # 煞星 - 一般对健康不利
    "擎羊": {"body": "手术", "type": "血光之灾", "is_harmful": True},
    "陀罗": {"body": "慢性病", "type": "拖延问题", "is_harmful": True},
    "火星": {"body": "急症", "type": "突发意外", "is_harmful": True},
    "铃星": {"body": "突发事件", "type": "心理冲击", "is_harmful": True},

    # 其他
    "文昌": {"body": "文学相关", "type": "神经系统", "is_harmful": False},
    "文曲": {"body": "艺术相关", "type": "情绪波动", "is_harmful": False},
    "左辅": {"body": "辅助", "type": "增强体质", "is_harmful": False},
    "右弼": {"body": "辅助", "type": "增强体质", "is_harmful": False},
}

# 五行与健康
WUXING_HEALTH_MAP = {
    "木": {"organ": "肝胆", "weak": "筋骨", "excess": "头部"},
    "火": {"organ": "心脏", "weak": "血液循环", "excess": "眼部"},
    "土": {"organ": "脾胃", "weak": "消化系统", "excess": "肿胀"},
    "金": {"organ": "肺肠", "weak": "呼吸系统", "excess": "骨骼"},
    "水": {"organ": "肾膀胱", "weak": "泌尿系统", "excess": "耳部"},
}


class HealthAgent:
    """健康分析智能体"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data
        self._load_health_rules()

    def _load_health_rules(self):
        """加载健康规则"""
        # 可以从JSON文件加载，此处使用内置规则
        self._health_rules = {}

    def analyze_health(self, timing_transforms: Optional[Dict[str, Any]] = None) -> HealthAnalysis:
        """
        分析命盘健康状况

        Args:
            timing_transforms: 运势四化信息（可选）

        Returns:
            HealthAnalysis 健康分析结果
        """
        # 获取疾厄宫信息
        disease_palace = self._get_disease_palace()

        # 分析先天体质
        inherent = self._analyze_inherent_strength()

        # 分析当前健康
        current = self._analyze_current_health(disease_palace, timing_transforms)

        # 确定健康等级
        health_level = self._determine_health_level(current)

        # 识别风险因素
        risks = self._identify_risk_factors(disease_palace, timing_transforms)

        # 生成建议
        recommendations = self._generate_recommendations(health_level, risks)

        return HealthAnalysis(
            inherent_strength=inherent,
            current_health=current,
            health_level=health_level,
            disease_palace_analysis=disease_palace,
            weak_body_parts=self._identify_weak_parts(disease_palace),
            risk_factors=risks.get("factors", []),
            seasonal_risks=risks.get("seasonal", []),
            recommendations=recommendations
        )

    def _get_disease_palace(self) -> PalaceHealth:
        """获取疾厄宫健康分析"""
        palaces = self.chart.get("palaces", {})
        disease_palace_data = palaces.get("疾厄宫", {})
        stars = disease_palace_data.get("stars", [])

        health_score = 70  # 默认基础分
        health_stars = []
        warnings = []
        risks = []

        for star in stars:
            star_name = star.get("name", "")
            if star_name in HEALTH_STAR_EFFECTS:
                effect = HEALTH_STAR_EFFECTS[star_name]
                health_stars.append(HealthStar(
                    star=star_name,
                    is_harmful=effect["is_harmful"],
                    impact=effect["type"]
                ))

                if effect["is_harmful"]:
                    health_score -= 15
                    warnings.append(f"{star_name}在疾厄宫: {effect['type']}")
                    risks.append(effect["type"])
                else:
                    health_score += 5

        # 计算健康等级
        if health_score >= 80:
            level = HealthLevel.EXCELLENT
        elif health_score >= 60:
            level = HealthLevel.GOOD
        elif health_score >= 40:
            level = HealthLevel.FAIR
        elif health_score >= 20:
            level = HealthLevel.WEAK
        else:
            level = HealthLevel.VERY_WEAK

        return PalaceHealth(
            palace="疾厄宫",
            health_score=health_score,
            level=level,
            stars=health_stars,
            risks=risks,
            warnings=warnings
        )

    def _analyze_inherent_strength(self) -> int:
        """分析先天体质（1-100）"""
        score = 60  # 基础分

        palaces = self.chart.get("palaces", {})

        # 命宫强则体质强
        ming_gong = palaces.get("命宫", {})
        ming_stars = ming_gong.get("stars", [])

        # 有紫微、天府等主星加分的
        beneficial_stars = ["紫微", "天府", "天相", "天同", "太阴", "天机"]
        for star in ming_stars:
            if star.get("name") in beneficial_stars:
                score += 8

        # 煞星冲命宫减分
        harmful_stars = ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]
        for star in ming_stars:
            if star.get("name") in harmful_stars:
                score -= 10

        return max(0, min(100, score))

    def _analyze_current_health(self, disease_palace: PalaceHealth,
                                 timing_transforms: Optional[Dict[str, Any]]) -> int:
        """分析当前健康状况"""
        score = disease_palace.health_score

        if timing_transforms:
            # 流年化忌对健康影响大
            yearly_transforms = timing_transforms.get("transforms", [])
            for t in yearly_transforms:
                if t.get("type") == "化忌" and t.get("palace") in ["疾厄宫", "命宫"]:
                    score -= 20

        return max(0, min(100, score))

    def _determine_health_level(self, score: int) -> HealthLevel:
        """根据分数确定健康等级"""
        if score >= 80:
            return HealthLevel.EXCELLENT
        elif score >= 60:
            return HealthLevel.GOOD
        elif score >= 40:
            return HealthLevel.FAIR
        elif score >= 20:
            return HealthLevel.WEAK
        else:
            return HealthLevel.VERY_WEAK

    def _identify_risk_factors(self, disease_palace: PalaceHealth,
                                timing_transforms: Optional[Dict[str, Any]]) -> Dict[str, List[str]]:
        """识别风险因素"""
        factors = []
        seasonal = []

        # 从疾厄宫星曜识别
        for star in disease_palace.stars:
            if star.is_harmful:
                factors.append(f"{star.star}星: {star.impact}")

        # 流年风险
        if timing_transforms:
            yearly_transforms = timing_transforms.get("transforms", [])
            for t in yearly_transforms:
                if t.get("type") == "化忌" and t.get("palace") in ["疾厄宫", "命宫"]:
                    factors.append(f"流年{t.get('star')}{t.get('type')}冲疾厄宫")

        # 季节性风险（根据生日）
        birth = self.chart.get("birth_info", {})
        month = birth.get("month", 6)
        if month in [12, 1, 2]:
            seasonal.append("冬季: 注意呼吸系统疾病")
        elif month in [6, 7, 8]:
            seasonal.append("夏季: 注意心脑血管疾病")

        return {"factors": factors, "seasonal": seasonal}

    def _identify_weak_parts(self, disease_palace: PalaceHealth) -> List[str]:
        """识别虚弱部位"""
        parts = []
        for star in disease_palace.stars:
            if star.star in HEALTH_STAR_EFFECTS:
                body = HEALTH_STAR_EFFECTS[star.star]["body"]
                if star.is_harmful:
                    parts.append(body)
        return list(set(parts))

    def _generate_recommendations(self, level: HealthLevel,
                                   risks: Dict[str, List[str]]) -> List[str]:
        """生成健康建议"""
        recommendations = []

        level_recs = {
            HealthLevel.EXCELLENT: ["保持良好生活习惯", "适度运动"],
            HealthLevel.GOOD: ["注意作息规律", "定期体检"],
            HealthLevel.FAIR: ["加强锻炼", "注意饮食", "充足睡眠"],
            HealthLevel.WEAK: ["重点关注健康", "建议咨询医师", "中医调理"],
            HealthLevel.VERY_WEAK: ["必须就医检查", "长期调养计划", "避免过劳"]
        }
        recommendations.extend(level_recs.get(level, []))

        # 针对具体风险
        for factor in risks.get("factors", []):
            if "血光" in factor:
                recommendations.append("注意意外伤害，农历月份注意出行安全")
            if "肺部" in factor or "呼吸" in factor:
                recommendations.append("戒烟限酒，注意肺部保养")

        return recommendations[:5]  # 最多5条


# ============ 便捷函数 ============

def analyze_health_async(chart_data: Dict[str, Any],
                         timing_transforms: Optional[Dict[str, Any]] = None) -> HealthAnalysis:
    """异步健康分析"""
    agent = HealthAgent(chart_data)
    return agent.analyze_health(timing_transforms)


def analyze_health_sync(chart_data: Dict[str, Any],
                        timing_transforms: Optional[Dict[str, Any]] = None) -> HealthAnalysis:
    """同步健康分析"""
    return analyze_health_async(chart_data, timing_transforms)
