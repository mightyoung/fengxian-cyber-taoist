"""
CareerAgent - 事业发展分析智能体

负责分析命盘中的事业运势，包括：
- 事业发展方向
- 职业类型适配
- 事业高峰期
- 事业风险预警
- 事业建议
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class CareerLevel(Enum):
    """事业等级"""
    EXCELLENT = "excellent"      # 事业辉煌
    GOOD = "good"              # 事业顺利
    FAIR = "fair"              # 事业平稳
    CHALLENGING = "challenging" # 事业挑战
    WEAK = "weak"             # 事业薄弱


class CareerDirection(Enum):
    """事业方向"""
    OFFICIAL = "official"      # 公务/管理
    BUSINESS = "business"      # 商业/贸易
    CREATIVE = "creative"      # 创意/艺术
    TECHNICAL = "technical"    # 技术/专业
    SERVICE = "service"        # 服务/教育
    FINANCIAL = "financial"    # 金融/投资


@dataclass
class PalaceCareer:
    """宫位事业分析"""
    palace: str
    career_score: int  # 1-100
    stars: List[str]
    characteristics: str


@dataclass
class CareerAnalysis:
    """事业分析结果"""
    career_level: CareerLevel
    career_score: int  # 综合评分 1-100
    career_direction: List[CareerDirection]  # 适合的事业方向
    best_palace: str   # 最强事业宫位
    career_peak_ages: List[int]  # 事业高峰期年龄
    potential_risks: List[str]  # 潜在风险
    recommendations: List[str]  # 事业建议

    def to_dict(self) -> Dict[str, Any]:
        return {
            "career_level": self.career_level.value,
            "career_score": self.career_score,
            "career_direction": [d.value for d in self.career_direction],
            "best_palace": self.best_palace,
            "career_peak_ages": self.career_peak_ages,
            "potential_risks": self.potential_risks,
            "recommendations": self.recommendations
        }


# 事业宫星曜映射
CAREER_STAR_EFFECTS = {
    # 紫微系 - 适合管理
    "紫微": {"direction": CareerDirection.OFFICIAL, "description": "适合管理岗位，有领导能力"},
    "天机": {"direction": CareerDirection.TECHNICAL, "description": "适合技术、策划、咨询"},
    "太阳": {"direction": CareerDirection.OFFICIAL, "description": "适合政治、外交、教育"},

    # 武曲系 - 适合金融
    "武曲": {"direction": CareerDirection.FINANCIAL, "description": "适合金融、投资、财务"},
    "破军": {"direction": CareerDirection.BUSINESS, "description": "适合创业、冒险、变革"},

    # 天府系 - 适合稳定
    "天府": {"direction": CareerDirection.BUSINESS, "description": "适合商业、企业、管理"},
    "天相": {"direction": CareerDirection.OFFICIAL, "description": "适合公务、秘书、行政"},

    # 其他主星
    "贪狼": {"direction": CareerDirection.CREATIVE, "description": "适合创意、公关、销售"},
    "巨门": {"direction": CareerDirection.SERVICE, "description": "适合法律、教育、口才"},
    "天同": {"direction": CareerDirection.SERVICE, "description": "适合服务、艺术、悠闲"},
    "天梁": {"direction": CareerDirection.OFFICIAL, "description": "适合监察、慈善、管理"},
    "七杀": {"direction": CareerDirection.BUSINESS, "description": "适合创业、武职、司法"},
    "廉贞": {"direction": CareerDirection.CREATIVE, "description": "适合创意、行政、娱乐"},
}

# 煞星对事业影响
CAREER_SHA_EFFECTS = {
    "擎羊": "事业竞争激烈，易有小人",
    "陀罗": "事业拖延阻碍，需要耐心",
    "火星": "事业突发变化，注意冲动",
    "铃星": "事业持续压力，需坚韧",
    "地空": "事业不稳定，宜求稳",
    "地劫": "事业风险高，忌冒险投资",
}


class CareerAgent:
    """事业分析智能体"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data
        self.palaces = chart_data.get("palaces", {})
        self.birth = chart_data.get("birth_info", {})

    def analyze_career(
        self,
        timing_transforms: Optional[Dict[str, Any]] = None
    ) -> CareerAnalysis:
        """
        分析命盘事业运势

        Args:
            timing_transforms: 运势四化信息（可选）

        Returns:
            CareerAnalysis 事业分析结果
        """
        # 分析事业宫
        career_palace = self._analyze_career_palace()

        # 分析财帛宫
        wealth_palace = self._analyze_wealth_palace()

        # 分析命宫
        life_palace = self._analyze_life_palace()

        # 确定事业等级
        career_score = self._calculate_career_score(
            career_palace, wealth_palace, life_palace, timing_transforms
        )
        career_level = self._determine_career_level(career_score)

        # 确定事业方向
        career_direction = self._determine_career_direction(career_palace, life_palace)

        # 识别风险
        risks = self._identify_career_risks(timing_transforms)

        # 生成建议
        recommendations = self._generate_recommendations(
            career_level, career_direction, risks
        )

        # 计算事业高峰期
        peak_ages = self._calculate_peak_ages()

        return CareerAnalysis(
            career_level=career_level,
            career_score=career_score,
            career_direction=career_direction,
            best_palace=career_palace.palace,
            career_peak_ages=peak_ages,
            potential_risks=risks,
            recommendations=recommendations
        )

    def _analyze_career_palace(self) -> PalaceCareer:
        """分析事业宫（官禄宫）"""
        palace_data = self.palaces.get("事业宫", {})
        if not palace_data:
            palace_data = self.palaces.get("官禄宫", {})

        stars = palace_data.get("stars", [])
        star_names = [s.get("name", "") for s in stars]

        score = 60  # 基础分
        characteristics = []

        for star in star_names:
            if star in CAREER_STAR_EFFECTS:
                score += 5
                characteristics.append(CAREER_STAR_EFFECTS[star]["description"])
            elif star in CAREER_SHA_EFFECTS:
                score -= 10
                characteristics.append(CAREER_SHA_EFFECTS[star])

        return PalaceCareer(
            palace="事业宫",
            career_score=max(0, min(100, score)),
            stars=star_names,
            characteristics="; ".join(characteristics[:3])
        )

    def _analyze_wealth_palace(self) -> PalaceCareer:
        """分析财帛宫"""
        palace_data = self.palaces.get("财帛宫", {})
        stars = palace_data.get("stars", [])
        star_names = [s.get("name", "") for s in stars]

        score = 60

        for star in star_names:
            if star in ["武曲", "天府", "太阴", "贪狼"]:
                score += 8
            elif star in CAREER_SHA_EFFECTS:
                score -= 10

        return PalaceCareer(
            palace="财帛宫",
            career_score=max(0, min(100, score)),
            stars=star_names,
            characteristics=""
        )

    def _analyze_life_palace(self) -> PalaceCareer:
        """分析命宫"""
        palace_data = self.palaces.get("命宫", {})
        stars = palace_data.get("stars", [])
        star_names = [s.get("name", "") for s in stars]

        score = 50

        for star in star_names:
            if star in ["紫微", "天府", "天相"]:
                score += 10
            elif star in CAREER_SHA_EFFECTS:
                score -= 8

        return PalaceCareer(
            palace="命宫",
            career_score=max(0, min(100, score)),
            stars=star_names,
            characteristics=""
        )

    def _calculate_career_score(
        self,
        career: PalaceCareer,
        wealth: PalaceCareer,
        life: PalaceCareer,
        timing: Optional[Dict[str, Any]]
    ) -> int:
        """计算综合事业评分"""
        score = (career.career_score * 0.5 +
                 wealth.career_score * 0.3 +
                 life.career_score * 0.2)

        # 流年调整
        if timing:
            yearly_transforms = timing.get("transforms", [])
            for t in yearly_transforms:
                if t.get("palace") in ["事业宫", "财帛宫"] and t.get("type") == "化忌":
                    score -= 15
                elif t.get("palace") in ["事业宫", "财帛宫"] and t.get("type") == "化禄":
                    score += 10

        return max(0, min(100, int(score)))

    def _determine_career_level(self, score: int) -> CareerLevel:
        """确定事业等级"""
        if score >= 85:
            return CareerLevel.EXCELLENT
        elif score >= 70:
            return CareerLevel.GOOD
        elif score >= 55:
            return CareerLevel.FAIR
        elif score >= 40:
            return CareerLevel.CHALLENGING
        else:
            return CareerLevel.WEAK

    def _determine_career_direction(
        self,
        career: PalaceCareer,
        life: PalaceCareer
    ) -> List[CareerDirection]:
        """确定事业方向"""
        directions = []
        all_stars = career.stars + life.stars

        found_directions = set()
        for star in all_stars:
            if star in CAREER_STAR_EFFECTS:
                direction = CAREER_STAR_EFFECTS[star]["direction"]
                if direction not in found_directions:
                    directions.append(direction)
                    found_directions.add(direction)

        if not directions:
            directions = [CareerDirection.SERVICE]

        return directions[:3]  # 最多3个方向

    def _identify_career_risks(self, timing: Optional[Dict[str, Any]]) -> List[str]:
        """识别事业风险"""
        risks = []

        career_palace = self.palaces.get("事业宫", {})
        stars = career_palace.get("stars", [])
        star_names = [s.get("name", "") for s in stars]

        for star in star_names:
            if star in CAREER_SHA_EFFECTS:
                risks.append(CAREER_SHA_EFFECTS[star])

        if timing:
            for t in timing.get("transforms", []):
                if t.get("palace") == "事业宫" and t.get("type") == "化忌":
                    risks.append(f"流年{t.get('star')}化忌冲事业宫，需防事业变动")

        return list(set(risks))[:5]

    def _calculate_peak_ages(self) -> List[int]:
        """计算事业高峰期年龄"""
        birth_year = self.birth.get("year", 1990)
        current_year = datetime.now().year

        # 大致的事业高峰期（根据命盘结构）
        # 30-35岁第一个高峰，45-50岁第二个高峰
        return [32, 35, 45, 48]

    def _generate_recommendations(
        self,
        level: CareerLevel,
        directions: List[CareerDirection],
        risks: List[str]
    ) -> List[str]:
        """生成事业建议"""
        recommendations = []

        level_recs = {
            CareerLevel.EXCELLENT: [
                "把握机遇，勇于担当更重要职位",
                "善用领导才能，可考虑创业",
                "注意人际协调，避免孤傲"
            ],
            CareerLevel.GOOD: [
                "稳扎稳打，把握现有机会",
                "持续学习提升，增强竞争力",
                "建立人脉，为长远发展铺路"
            ],
            CareerLevel.FAIR: [
                "专注本职，积累经验",
                "选择稳定行业，避免频繁跳槽",
                "提升专业技能，增加不可替代性"
            ],
            CareerLevel.CHALLENGING: [
                "调整心态，化挑战为机遇",
                "考虑转型或进修",
                "注意与上司同事关系"
            ],
            CareerLevel.WEAK: [
                "先生存后发展，求稳为主",
                "考虑合伙而非单打独斗",
                "注重身心健康，厚积薄发"
            ]
        }
        recommendations.extend(level_recs.get(level, []))

        # 针对风险的建议
        for risk in risks[:2]:
            if "小人" in risk:
                recommendations.append("注意办公室政治，与小人保持距离")
            elif "冲动" in risk:
                recommendations.append("重大决策前冷静三天，避免冲动")

        return recommendations[:5]


# ============ 便捷函数 ============

def analyze_career_async(
    chart_data: Dict[str, Any],
    timing_transforms: Optional[Dict[str, Any]] = None
) -> CareerAnalysis:
    """异步事业分析"""
    agent = CareerAgent(chart_data)
    return agent.analyze_career(timing_transforms)


def analyze_career_sync(
    chart_data: Dict[str, Any],
    timing_transforms: Optional[Dict[str, Any]] = None
) -> CareerAnalysis:
    """同步事业分析"""
    return analyze_career_async(chart_data, timing_transforms)
