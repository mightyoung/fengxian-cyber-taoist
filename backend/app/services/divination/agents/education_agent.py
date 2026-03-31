"""
EducationAgent - 教育学业分析智能体

负责分析命盘中的学业运势，包括：
- 学习能力评估
- 学历层次预测
- 学业运势波动
- 学业风险预警
- 学业建议
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class EducationLevel(Enum):
    """学历层次"""
    DOCTOR = "doctor"           # 博士及以上
    MASTER = "master"          # 硕士
    BACHELOR = "bachelor"      # 本科
    ASSOCIATE = "associate"     # 大专
    HIGH_SCHOOL = "high_school"  # 高中及以下


class LearningAbility(Enum):
    """学习能力"""
    EXCELLENT = "excellent"    # 聪颖过人
    GOOD = "good"             # 聪明伶俐
    FAIR = "fair"             # 中等平平
    WEAK = "weak"             # 学习吃力
    VERY_WEAK = "very_weak"   # 难以学习


@dataclass
class EducationAnalysis:
    """学业分析结果"""
    learning_ability: LearningAbility
    learning_score: int  # 学习能力评分 1-100
    education_level_hint: EducationLevel  # 学历层次预测
    best_study_ages: List[int]  # 最佳学习年龄
    weak_subjects: List[str]  # 薄弱学科提醒
    academic_risks: List[str]  # 学业风险
    study_tips: List[str]  # 学习建议

    def to_dict(self) -> Dict[str, Any]:
        return {
            "learning_ability": self.learning_ability.value,
            "learning_score": self.learning_score,
            "education_level_hint": self.education_level_hint.value,
            "best_study_ages": self.best_study_ages,
            "weak_subjects": self.weak_subjects,
            "academic_risks": self.academic_risks,
            "study_tips": self.study_tips
        }


# 文昌文曲影响
LITERARY_STAR_EFFECTS = {
    "文昌": {"subjects": "文科学术", "bonus": 15, "description": "学术成就，正规学历"},
    "文曲": {"subjects": "文学艺术", "bonus": 12, "description": "文艺才华，表达能力强"},
}

# 主星与学习能力
LEARNING_STAR_EFFECTS = {
    "紫微": {"ability": LearningAbility.EXCELLENT, "description": "悟性极高，理解力强"},
    "天机": {"ability": LearningAbility.EXCELLENT, "description": "聪明机敏，学习快速"},
    "太阳": {"ability": LearningAbility.GOOD, "description": "视野开阔，学习认真"},
    "武曲": {"ability": LearningAbility.FAIR, "description": "独立学习，需要督促"},
    "天府": {"ability": LearningAbility.GOOD, "description": "稳扎稳打，有后劲"},
    "天相": {"ability": LearningAbility.GOOD, "description": "配合度高，适合团队学习"},
    "贪狼": {"ability": LearningAbility.FAIR, "description": "兴趣驱动，需要找到动力"},
    "巨门": {"ability": LearningAbility.FAIR, "description": "深度思考，需避免分心"},
    "天同": {"ability": LearningAbility.WEAK, "description": "懒散享乐，需要压力"},
    "天梁": {"ability": LearningAbility.GOOD, "description": "老成学习法，适合持久战"},
    "七杀": {"ability": LearningAbility.FAIR, "description": "实践型学习，边做边学"},
    "廉贞": {"ability": LearningAbility.FAIR, "description": "专注时效率高，易分心"},
}

# 科名星
SCIENCE_STARS = ["文昌", "文曲", "化科", "天魁", "天钺"]


class EducationAgent:
    """教育学业分析智能体"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data
        self.palaces = chart_data.get("palaces", {})
        self.birth = chart_data.get("birth_info", {})

    def analyze_education(
        self,
        timing_transforms: Optional[Dict[str, Any]] = None
    ) -> EducationAnalysis:
        """
        分析命盘学业运势

        Args:
            timing_transforms: 运势四化信息（可选）

        Returns:
            EducationAnalysis 学业分析结果
        """
        # 分析学习能力
        ability = self._analyze_learning_ability()

        # 确定学历层次
        edu_level = self._determine_education_level(ability)

        # 计算最佳学习年龄
        best_ages = self._calculate_best_study_ages()

        # 识别薄弱学科
        weak_subjects = self._identify_weak_subjects()

        # 识别学业风险
        risks = self._identify_academic_risks(timing_transforms)

        # 生成学习建议
        tips = self._generate_study_tips(ability, edu_level, risks)

        return EducationAnalysis(
            learning_ability=ability,
            learning_score=self._calculate_learning_score(ability),
            education_level_hint=edu_level,
            best_study_ages=best_ages,
            weak_subjects=weak_subjects,
            academic_risks=risks,
            study_tips=tips
        )

    def _analyze_learning_ability(self) -> LearningAbility:
        """分析学习能力"""
        # 检查命宫
        life_palace = self.palaces.get("命宫", {})
        life_stars = [s.get("name", "") for s in life_palace.get("stars", [])]

        # 检查父母宫（学业宫）
        parents_palace = self.palaces.get("父母宫", {})
        parents_stars = [s.get("name", "") for s in parents_palace.get("stars", [])]

        all_stars = life_stars + parents_stars

        # 查找主星学习能力
        for star in all_stars:
            if star in LEARNING_STAR_EFFECTS:
                return LEARNING_STAR_EFFECTS[star]["ability"]

        return LearningAbility.FAIR

    def _calculate_learning_score(self, ability: LearningAbility) -> int:
        """计算学习能力评分"""
        scores = {
            LearningAbility.EXCELLENT: 90,
            LearningAbility.GOOD: 75,
            LearningAbility.FAIR: 60,
            LearningAbility.WEAK: 45,
            LearningAbility.VERY_WEAK: 30
        }

        base_score = scores.get(ability, 60)

        # 文昌文曲加分
        parents_palace = self.palaces.get("父母宫", {})
        stars = parents_palace.get("stars", [])
        for star in stars:
            star_name = star.get("name", "")
            if star_name in LITERARY_STAR_EFFECTS:
                base_score += LITERARY_STAR_EFFECTS[star_name]["bonus"]

        return max(0, min(100, base_score))

    def _determine_education_level(self, ability: LearningAbility) -> EducationLevel:
        """确定学历层次"""
        parents_palace = self.palaces.get("父母宫", {})
        stars = parents_palace.get("stars", [])
        star_names = [s.get("name", "") for s in stars]

        # 科名星数量
        science_count = sum(1 for s in star_names if s in SCIENCE_STARS)

        # 主星影响
        ability_score = {
            LearningAbility.EXCELLENT: 4,
            LearningAbility.GOOD: 3,
            LearningAbility.FAIR: 2,
            LearningAbility.WEAK: 1,
            LearningAbility.VERY_WEAK: 0
        }.get(ability, 2)

        total = ability_score + science_count

        if total >= 5:
            return EducationLevel.DOCTOR
        elif total >= 4:
            return EducationLevel.MASTER
        elif total >= 3:
            return EducationLevel.BACHELOR
        elif total >= 2:
            return EducationLevel.ASSOCIATE
        else:
            return EducationLevel.HIGH_SCHOOL

    def _calculate_best_study_ages(self) -> List[int]:
        """计算最佳学习年龄"""
        birth_year = self.birth.get("year", 1990)
        current_year = datetime.now().year
        current_age = current_year - birth_year

        # 基础学习高峰期
        # 少年期(12-18)、青年期(20-28)
        best_ages = []

        if current_age < 20:
            # 还有学习阶段
            for age in [14, 15, 16, 17, 18, 22, 23, 24]:
                if age > current_age:
                    best_ages.append(age)
        elif current_age < 35:
            # 继续深造
            for age in [28, 29, 30, 31]:
                best_ages.append(age)
        else:
            # 终身学习
            best_ages = [40, 45]  # 可能的学习转型期

        return best_ages[:5]

    def _identify_weak_subjects(self) -> List[str]:
        """识别薄弱学科"""
        weak = []

        parents_palace = self.palaces.get("父母宫", {})
        stars = [s.get("name", "") for s in parents_palace.get("stars", [])]

        # 无文昌文曲，语文可能弱
        if "文昌" not in stars and "文曲" not in stars:
            weak.append("语文理解表达")

        # 无数学星
        if "天机" not in stars and "武曲" not in stars:
            weak.append("数学逻辑")

        # 贪狼过重
        if stars.count("贪狼") > 0:
            weak.append("专注力")

        return weak[:3]

    def _identify_academic_risks(self, timing: Optional[Dict[str, Any]]) -> List[str]:
        """识别学业风险"""
        risks = []

        parents_palace = self.palaces.get("父母宫", {})
        stars = parents_palace.get("stars", [])

        for star in stars:
            star_name = star.get("name", "")
            if star_name in ["擎羊", "陀罗", "火星", "铃星"]:
                if star_name == "擎羊":
                    risks.append("学业竞争压力大")
                elif star_name == "陀罗":
                    risks.append("学习拖延症")
                elif star_name == "火星":
                    risks.append("学习易冲动急躁")
                elif star_name == "铃星":
                    risks.append("学习持续焦虑")

        if timing:
            for t in timing.get("transforms", []):
                if t.get("palace") == "父母宫":
                    if t.get("type") == "化忌":
                        risks.append("学业运势受阻，需要加倍努力")
                    elif t.get("type") == "化科":
                        risks.append("学业有进步，名声渐显")

        return list(set(risks))[:5]

    def _generate_study_tips(
        self,
        ability: LearningAbility,
        level: EducationLevel,
        risks: List[str]
    ) -> List[str]:
        """生成学习建议"""
        tips = []

        # 能力建议
        ability_tips = {
            LearningAbility.EXCELLENT: [
                "天赋极高，可挑战更高学历",
                "尝试深入研究，做学问型"
            ],
            LearningAbility.GOOD: [
                "稳扎稳打，可以取得好成绩",
                "注重基础，厚积薄发"
            ],
            LearningAbility.FAIR: [
                "学习方法很重要，找对路子",
                "勤能补拙，多花时间"
            ],
            LearningAbility.WEAK: [
                "扬长避短，发掘特长",
                "考虑技术类或实践型方向"
            ],
            LearningAbility.VERY_WEAK: [
                "寻找感兴趣领域，兴趣是最好的老师",
                "考虑创业或其他发展路径"
            ]
        }
        tips.extend(ability_tips.get(ability, []))

        # 学历建议
        level_tips = {
            EducationLevel.DOCTOR: "适合学术研究，可考虑考研读博",
            EducationLevel.MASTER: "适合专业深化，建议考研",
            EducationLevel.BACHELOR: "打好基础，可考虑考研或出国",
            EducationLevel.ASSOCIATE: "注重技能培养，积累经验",
            EducationLevel.HIGH_SCHOOL: "选择感兴趣的方向持续学习"
        }
        tips.append(level_tips.get(level, ""))

        # 风险建议
        for risk in risks[:2]:
            if "拖延" in risk:
                tips.append("使用时间管理方法，如番茄工作法")
            elif "焦虑" in risk:
                tips.append("适当放松，保持平常心")

        return [t for t in tips if t][:5]


# ============ 便捷函数 ============

def analyze_education_async(
    chart_data: Dict[str, Any],
    timing_transforms: Optional[Dict[str, Any]] = None
) -> EducationAnalysis:
    """异步学业分析"""
    agent = EducationAgent(chart_data)
    return agent.analyze_education(timing_transforms)


def analyze_education_sync(
    chart_data: Dict[str, Any],
    timing_transforms: Optional[Dict[str, Any]] = None
) -> EducationAnalysis:
    """同步学业分析"""
    return analyze_education_async(chart_data, timing_transforms)
