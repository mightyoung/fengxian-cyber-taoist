"""
RelationshipAgent - 姻缘感情分析智能体

负责分析命盘中的姻缘感情运势，包括：
- 婚姻早晚
- 配偶特征
- 婚姻质量
- 桃花运势
- 感情建议
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class MarriageTiming(Enum):
    """婚姻时间"""
    EARLY = "early"      # 早婚 (25岁前)
    NORMAL = "normal"    # 正常 (25-32岁)
    LATE = "late"        # 晚婚 (32-40岁)
    VERY_LATE = "very_late"  # 晚婚 (40岁后)


class MarriageQuality(Enum):
    """婚姻质量"""
    EXCELLENT = "excellent"  # 美满
    GOOD = "good"          # 良好
    FAIR = "fair"          # 一般
    CHALLENGING = "challenging"  # 有挑战
    DIFFICULT = "difficult" # 困难


class PeachBlossomLevel(Enum):
    """桃花等级"""
    STRONG = "strong"      # 旺
    MODERATE = "moderate"  # 中
    WEAK = "weak"         # 弱
    NONE = "none"         # 无


@dataclass
class SpouseFeatures:
    """配偶特征"""
    star_influence: str  # 主星影响
    appearance: str     # 外貌特征
    personality: str     # 性格特点
    career: str         # 事业倾向
    age_difference: str  # 年龄差


@dataclass
class RelationshipAnalysis:
    """姻缘分析结果"""
    marriage_timing: MarriageTiming
    marriage_age_hint: int  # 建议婚龄
    marriage_quality: MarriageQuality
    spouse_features: SpouseFeatures
    peach_blossom: PeachBlossomLevel
    peach_blossom_ages: List[int]  # 桃花旺的年龄
    relationship_risks: List[str]  # 感情风险
    marriage_advice: List[str]  # 婚姻建议

    def to_dict(self) -> Dict[str, Any]:
        return {
            "marriage_timing": self.marriage_timing.value,
            "marriage_age_hint": self.marriage_age_hint,
            "marriage_quality": self.marriage_quality.value,
            "spouse_features": self.spouse_features.__dict__,
            "peach_blossom": self.peach_blossom.value,
            "peach_blossom_ages": self.peach_blossom_ages,
            "relationship_risks": self.relationship_risks,
            "marriage_advice": self.marriage_advice
        }


# 夫妻宫星曜与配偶特征
SPOUSE_STAR_EFFECTS = {
    "紫微": {"appearance": "端庄威严", "personality": "自尊心强、有领导力", "career": "管理或公职"},
    "天机": {"appearance": "清秀机敏", "personality": "聪明善变、适应力强", "career": "技术或策划"},
    "太阳": {"appearance": "开朗外向", "personality": "热情慷慨、正直无私", "career": "政治或教育"},
    "武曲": {"appearance": "刚毅果断", "personality": "独立坚强、实际务实", "career": "金融或财务"},
    "天府": {"appearance": "稳重成熟", "personality": "大方有魄力、享受生活", "career": "商业或企业"},
    "天相": {"appearance": "温和儒雅", "personality": "稳重有礼、善于协调", "career": "公务或秘书"},
    "贪狼": {"appearance": "美艳风流", "personality": "活泼外向、善于交际", "career": "销售或娱乐"},
    "巨门": {"appearance": "清瘦严肃", "personality": "固执直接、口才出众", "career": "法律或教育"},
    "天同": {"appearance": "圆润温和", "personality": "温和懒散、享受悠闲", "career": "服务或艺术"},
    "天梁": {"appearance": "成熟稳重", "personality": "老成持重、慈悲为怀", "career": "监察或慈善"},
    "七杀": {"appearance": "刚强威猛", "personality": "冲动果断、勇於拼搏", "career": "创业或武职"},
    "廉贞": {"appearance": "清丽脱俗", "personality": "感情丰富、任性执着", "career": "创意或演艺"},
}

# 桃花星曜
PEACH_BLOSSOM_STARS = ["贪狼", "廉贞", "天姚", "红鸾", "天喜", "咸池"]

# 煞星对感情影响
RELATIONSHIP_SHA_EFFECTS = {
    "擎羊": "感情竞争激烈，易有第三者",
    "陀罗": "感情拖延，单身者难脱单",
    "火星": "感情冲动，易有争吵或冲动行为",
    "铃星": "感情持续困扰，易有隐瞒",
    "地空": "感情空虚，难有稳定关系",
    "地劫": "感情起伏大，难有结果",
}


class RelationshipAgent:
    """姻缘感情分析智能体"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data
        self.palaces = chart_data.get("palaces", {})
        self.birth = chart_data.get("birth_info", {})

    def analyze_relationship(
        self,
        timing_transforms: Optional[Dict[str, Any]] = None
    ) -> RelationshipAnalysis:
        """
        分析命盘姻缘感情运势

        Args:
            timing_transforms: 运势四化信息（可选）

        Returns:
            RelationshipAnalysis 姻缘分析结果
        """
        # 分析夫妻宫
        spouse_palace = self._analyze_spouse_palace()

        # 分析桃花
        peach = self._analyze_peach_blossom()

        # 确定婚姻时间
        timing = self._determine_marriage_timing(spouse_palace, peach)

        # 确定婚姻质量
        quality = self._determine_marriage_quality(spouse_palace, timing_transforms)

        # 识别感情风险
        risks = self._identify_relationship_risks(timing_transforms)

        # 生成建议
        advice = self._generate_marriage_advice(timing, quality, peach, risks)

        return RelationshipAnalysis(
            marriage_timing=timing,
            marriage_age_hint=self._calculate_marriage_age(spouse_palace),
            marriage_quality=quality,
            spouse_features=spouse_palace,
            peach_blossom=peach.get("level"),
            peach_blossom_ages=peach.get("ages", []),
            relationship_risks=risks,
            marriage_advice=advice
        )

    def _analyze_spouse_palace(self) -> SpouseFeatures:
        """分析夫妻宫获取配偶特征"""
        palace_data = self.palaces.get("夫妻宫", {})
        stars = palace_data.get("stars", [])
        star_names = [s.get("name", "") for s in stars]

        # 获取主星
        main_star = None
        for star in star_names:
            if star in SPOUSE_STAR_EFFECTS:
                main_star = star
                break

        if main_star and main_star in SPOUSE_STAR_EFFECTS:
            effects = SPOUSE_STAR_EFFECTS[main_star]
            return SpouseFeatures(
                star_influence=main_star,
                appearance=effects["appearance"],
                personality=effects["personality"],
                career=effects["career"],
                age_difference="差1-3岁" if main_star in ["天同", "天府"] else "差3-5岁"
            )

        return SpouseFeatures(
            star_influence="无明显主星",
            appearance="中等",
            personality="温和",
            career="稳定职业",
            age_difference="相近"
        )

    def _analyze_peach_blossom(self) -> Dict[str, Any]:
        """分析桃花运势"""
        # 检查各宫位桃花星
        peach_stars_found = []
        peach_locations = []

        for palace_name, palace_data in self.palaces.items():
            stars = palace_data.get("stars", [])
            for star in stars:
                if star.get("name", "") in PEACH_BLOSSOM_STARS:
                    peach_stars_found.append(star.get("name"))
                    peach_locations.append(palace_name)

        # 判断桃花等级
        if len(peach_stars_found) >= 3:
            level = PeachBlossomLevel.STRONG
        elif len(peach_stars_found) >= 1:
            level = PeachBlossomLevel.MODERATE
        elif len(peach_stars_found) == 0:
            level = PeachBlossomLevel.WEAK
        else:
            level = PeachBlossomLevel.NONE

        # 计算桃花旺的年龄
        birth_year = self.birth.get("year", 1990)
        current_year = datetime.now().year
        peach_ages = []

        # 桃花旺的年龄规律（简化版）
        if level in [PeachBlossomLevel.STRONG, PeachBlossomLevel.MODERATE]:
            for i in range(20, 40):
                if i % 7 in [2, 3, 5]:  # 简化规律
                    peach_ages.append(current_year - birth_year + i)

        return {
            "level": level,
            "stars": list(set(peach_stars_found)),
            "locations": peach_locations,
            "ages": sorted(list(set(peach_ages)))[:5]
        }

    def _determine_marriage_timing(
        self,
        spouse: SpouseFeatures,
        peach: Dict[str, Any]
    ) -> MarriageTiming:
        """确定婚姻时间"""

        # 基于星曜判断
        if spouse.star_influence in ["贪狼", "廉贞", "七杀"]:
            # 桃花星或杀气星可能早婚也可能晚婚
            if peach.get("level") == PeachBlossomLevel.STRONG:
                return MarriageTiming.EARLY
            return MarriageTiming.LATE
        elif spouse.star_influence in ["天府", "天同", "天相"]:
            # 温和星曜倾向于正常或晚婚
            return MarriageTiming.NORMAL

        return MarriageTiming.NORMAL

    def _calculate_marriage_age(self, spouse: SpouseFeatures) -> int:
        """计算建议婚龄"""
        if spouse.star_influence in ["贪狼", "七杀"]:
            return 26
        elif spouse.star_influence in ["天府", "天同"]:
            return 30
        elif spouse.star_influence in ["紫微", "太阳"]:
            return 28
        return 28

    def _determine_marriage_quality(
        self,
        spouse: SpouseFeatures,
        timing: Optional[Dict[str, Any]]
    ) -> MarriageQuality:
        """确定婚姻质量"""
        score = 70  # 基础分

        # 主星影响
        good_stars = ["紫微", "天府", "天相", "天同"]
        bad_stars = ["贪狼", "七杀", "廉贞"]

        if spouse.star_influence in good_stars:
            score += 15
        elif spouse.star_influence in bad_stars:
            score -= 10

        # 煞星影响
        palace_data = self.palaces.get("夫妻宫", {})
        stars = palace_data.get("stars", [])
        for star in stars:
            if star.get("name", "") in RELATIONSHIP_SHA_EFFECTS:
                score -= 15

        # 四化影响
        if timing:
            for t in timing.get("transforms", []):
                if t.get("palace") == "夫妻宫":
                    if t.get("type") == "化忌":
                        score -= 20
                    elif t.get("type") == "化禄":
                        score += 10

        if score >= 85:
            return MarriageQuality.EXCELLENT
        elif score >= 70:
            return MarriageQuality.GOOD
        elif score >= 55:
            return MarriageQuality.FAIR
        elif score >= 40:
            return MarriageQuality.CHALLENGING
        else:
            return MarriageQuality.DIFFICULT

    def _identify_relationship_risks(self, timing: Optional[Dict[str, Any]]) -> List[str]:
        """识别感情风险"""
        risks = []

        palace_data = self.palaces.get("夫妻宫", {})
        stars = palace_data.get("stars", [])

        for star in stars:
            star_name = star.get("name", "")
            if star_name in RELATIONSHIP_SHA_EFFECTS:
                risks.append(RELATIONSHIP_SHA_EFFECTS[star_name])

        if timing:
            for t in timing.get("transforms", []):
                if t.get("palace") == "夫妻宫" and t.get("type") == "化忌":
                    risks.append(f"流年{t.get('star')}化忌冲夫妻宫，感情需谨慎")

        return list(set(risks))[:5]

    def _generate_marriage_advice(
        self,
        timing: MarriageTiming,
        quality: MarriageQuality,
        peach: Dict[str, Any],
        risks: List[str]
    ) -> List[str]:
        """生成婚姻建议"""
        advice = []

        # 婚姻时间建议
        timing_advice = {
            MarriageTiming.EARLY: "早婚者宜珍惜缘分，相互包容",
            MarriageTiming.NORMAL: "正常婚龄，宜把握28-32岁黄金期",
            MarriageTiming.LATE: "晚婚者宜充实自我，缘分自会到来",
            MarriageTiming.VERY_LATE: "不急婚配，先立业后成家亦可"
        }
        advice.append(timing_advice.get(timing, ""))

        # 婚姻质量建议
        quality_advice = {
            MarriageQuality.EXCELLENT: "婚姻美满，珍惜眼前幸福",
            MarriageQuality.GOOD: "婚姻良好，用心经营更幸福",
            MarriageQuality.FAIR: "婚姻平稳，用心沟通化解矛盾",
            MarriageQuality.CHALLENGING: "婚姻有挑战，多包容多理解",
            MarriageQuality.DIFFICULT: "婚姻需谨慎，可考虑晚婚或求助于专业"
        }
        advice.append(quality_advice.get(quality, ""))

        # 桃花建议
        if peach.get("level") == PeachBlossomLevel.STRONG:
            advice.append("桃花旺盛，注意把握分寸，避免烂桃花")
        elif peach.get("level") == PeachBlossomLevel.WEAK:
            advice.append("桃花较弱，专心事业，缘分天定")

        # 针对风险
        for risk in risks[:2]:
            if "第三者" in risk:
                advice.append("注意与异性保持适当距离")
            elif "争吵" in risk:
                advice.append("控制情绪，多沟通少争执")

        return [a for a in advice if a][:5]


# ============ 便捷函数 ============

def analyze_relationship_async(
    chart_data: Dict[str, Any],
    timing_transforms: Optional[Dict[str, Any]] = None
) -> RelationshipAnalysis:
    """异步姻缘分析"""
    agent = RelationshipAgent(chart_data)
    return agent.analyze_relationship(timing_transforms)


def analyze_relationship_sync(
    chart_data: Dict[str, Any],
    timing_transforms: Optional[Dict[str, Any]] = None
) -> RelationshipAnalysis:
    """同步姻缘分析"""
    return analyze_relationship_async(chart_data, timing_transforms)
