"""
CareerRecommendationAgent - 职业推荐引擎

根据命盘分析最适合的职业类型，输出：
- Top-N 职业推荐
- 行业方向
- 财运类型
- 学业建议
- 发展路线图
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# ============ 主星 → 职业类型映射 ============

STAR_CAREER_MAPPING = {
    # 北斗
    "紫微": ["管理", "政治", "领导", "策划", "咨询"],
    "天机": ["技术", "策划", "智囊", "顾问", "研发"],
    "太阳": ["外交", "教育", "法律", "政治", "传播"],
    "武曲": ["金融", "财务", "军警", "工程", "体育"],
    "天同": ["服务", "餐饮", "旅游", "艺术", "娱乐"],
    "廉贞": ["商业", "销售", "外交", "演艺", "法律"],
    # 南斗
    "天府": ["管理", "财务", "银行", "稳定职业", "教育"],
    "太阴": ["艺术", "设计", "财务", "医疗", "服务"],
    "贪狼": ["商业", "销售", "演艺", "社交", "投资"],
    "巨门": ["法律", "口才", "教育", "咨询", "翻译"],
    "天相": ["服务", "稳定职业", "管理", "财务", "技术"],
    "天梁": ["慈善", "教育", "医疗", "稳定职业", "公正"],
    # 中天
    "七杀": ["军警", "工程", "体育", "冒险", "销售"],
    "破军": ["冒险", "创新", "科技", "创业", "演艺"],
}

# 宫位 → 职业倾向
PALACE_CAREER_TENDENCY = {
    "命宫": "个性特质主导，适合发挥个人特长的职业",
    "官禄宫": "事业心强，适合管理或专业技术",
    "财帛宫": "财运好，适合金融、财务、投资",
    "迁移宫": "外地发展，适合外交、销售、传媒",
    "田宅宫": "房产相关，适合建筑、装修、房地产",
    "交友宫": "人脉广泛，适合销售、公关、人力资源",
    "疾厄宫": "身体素质好，适合军警、体育、工程",
    "福德宫": "精神追求高，适合学术、艺术、教育",
    "父母宫": "文书相关，适合教育、法律、出版",
    "子女宫": "创新创业，适合新兴行业、自由职业",
}

# 职业类型 → 职业名称映射
CAREER_NAME_MAPPING = {
    "管理": [
        ("企业高管", "高层管理"),
        ("项目经理", "中层管理"),
        ("行政主管", "行政管理"),
    ],
    "政治": [
        ("公务员", "政府机构"),
        ("政策分析师", "政策研究"),
        ("公共关系主管", "公关媒体"),
    ],
    "技术": [
        ("软件工程师", "IT互联网"),
        ("数据分析师", "数据分析"),
        ("技术支持工程师", "技术服务"),
    ],
    "策划": [
        ("品牌策划", "市场营销"),
        ("活动策划", "公关会展"),
        ("商业策划", "咨询顾问"),
    ],
    "金融": [
        ("投资顾问", "金融服务"),
        ("财务经理", "企业管理"),
        ("风险管理师", "金融风控"),
    ],
    "销售": [
        ("销售经理", "业务拓展"),
        ("大客户经理", "企业服务"),
        ("商务拓展", "市场营销"),
    ],
    "艺术": [
        ("设计师", "创意设计"),
        ("插画师", "数字创意"),
        ("艺术指导", "广告传媒"),
    ],
    "教育": [
        ("教师/讲师", "教育培训"),
        ("课程设计师", "教育科技"),
        ("培训师", "企业管理培训"),
    ],
    "法律": [
        ("律师", "法律服务"),
        ("法务顾问", "企业法务"),
        ("合规专员", "风险管理"),
    ],
    "咨询": [
        ("管理咨询师", "咨询服务"),
        ("心理咨询师", "心理健康"),
        ("职业顾问", "人力资源"),
    ],
    "工程": [
        ("土木工程师", "建筑地产"),
        ("机械工程师", "制造业"),
        ("电气工程师", "能源电力"),
    ],
    "医疗": [
        ("医生", "医疗健康"),
        ("健康管理师", "健康产业"),
        ("医疗器械", "医药行业"),
    ],
    "创业": [
        ("创业者", "创新商业"),
        ("自由职业者", "个人品牌"),
        ("投资人", "风险投资"),
    ],
}

# 职业等级定义
CAREER_LEVELS = {
    "基层": ["初级专员", "助理", "实习生", "基层员工"],
    "中层": ["项目经理", "主管", "高级专员", "team leader"],
    "高层": ["总监", "总经理", "VP", "CXO"],
    "专家": ["首席专家", "院士", "资深顾问", "行业领袖"],
}

# 财运类型判定
WEALTH_TYPE_STARS = {
    "正财型": ["天府", "天同", "天梁", "天相"],
    "横财型": ["贪狼", "破军", "七杀", "廉贞"],
    "技术财型": ["武曲", "天机", "太阳"],
    "艺术财型": ["太阴", "天同"],
}

# ============ 数据结构 ============


@dataclass
class CareerOption:
    """职业选项"""
    rank: int
    career_type: str            # 职业类型: "管理类"
    career_name: str            # 职业名称: "企业高管"
    match_score: float         # 匹配度 0-100
    level: str                  # 等级
    match_reasons: List[str]    # 匹配理由
    strengths_utilized: List[str] = field(default_factory=list)  # 发挥的优势
    growth_potential: str = ""  # 发展潜力描述
    best_industry: str = ""      # 最佳行业

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "career_type": self.career_type,
            "career_name": self.career_name,
            "match_score": self.match_score,
            "level": self.level,
            "match_reasons": self.match_reasons,
            "strengths_utilized": self.strengths_utilized,
            "growth_potential": self.growth_potential,
            "best_industry": self.best_industry,
        }


@dataclass
class EducationAdvice:
    """教育建议"""
    direction: str              # 学业方向
    suitable_degrees: List[str]  # 适合的学历层次
    recommended_majors: List[str]  # 推荐专业
    exam_luck: str = ""        # 考试运势
    study_environment: str = ""  # 学习环境偏好

    def to_dict(self) -> Dict[str, Any]:
        return {
            "direction": self.direction,
            "suitable_degrees": self.suitable_degrees,
            "recommended_majors": self.recommended_majors,
            "exam_luck": self.exam_luck,
            "study_environment": self.study_environment,
        }


@dataclass
class CareerRecommendationResult:
    """职业推荐结果"""
    service_type: str = "career_recommendation"
    strongest_palace: str = ""       # 最强宫位
    career_potential_score: float = 0.0  # 职业潜力综合分
    career_options: List[CareerOption] = field(default_factory=list)
    wealth_type: str = ""            # 财运类型: "正财型" / "横财型" / "技术财型"
    education_advice: Optional[EducationAdvice] = None
    key_strengths: List[str] = field(default_factory=list)  # 核心优势
    development_roadmap: List[str] = field(default_factory=list)  # 发展路线图
    warnings: List[str] = field(default_factory=list)      # 职业警示
    overall_analysis: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_type": self.service_type,
            "strongest_palace": self.strongest_palace,
            "career_potential_score": self.career_potential_score,
            "career_options": [opt.to_dict() for opt in self.career_options],
            "wealth_type": self.wealth_type,
            "education_advice": self.education_advice.to_dict() if self.education_advice else None,
            "key_strengths": self.key_strengths,
            "development_roadmap": self.development_roadmap,
            "warnings": self.warnings,
            "overall_analysis": self.overall_analysis,
            "confidence": self.confidence,
        }


# ============ 职业推荐引擎 ============


class CareerRecommendationAgent:
    """职业推荐引擎"""

    def __init__(
        self,
        chart: Dict[str, Any],
        age: Optional[int] = None,
        current_career: Optional[str] = None,
        education_level: Optional[str] = None,
        top_n: int = 5,
    ):
        """
        初始化职业推荐

        Args:
            chart: 命盘数据
            age: 年龄
            current_career: 当前职业
            education_level: 学历
            top_n: 推荐数量
        """
        self.chart = chart
        self.palaces = chart.get("palaces", {})
        self.transforms = chart.get("transforms", [])
        self.age = age or 25
        self.current_career = current_career
        self.education_level = education_level
        self.top_n = top_n

        # 三方四正映射 (复用 palace_agent 的逻辑)
        self.sanfang_map = {
            "命宫": ["财帛宫", "官禄宫", "迁移宫"],
            "官禄宫": ["命宫", "夫妻宫", "迁移宫"],
            "财帛宫": ["命宫", "子女宫", "疾厄宫"],
            "迁移宫": ["命宫", "官禄宫", "仆役宫"],
        }

    def _get_palace_stars(self, palace_name: str) -> List[str]:
        """获取宫位主星"""
        palace = self.palaces.get(palace_name, {})
        major_stars = palace.get("major_stars", [])
        minor_stars = palace.get("minor_stars", [])
        return major_stars + minor_stars

    def _get_palace_score(self, palace_name: str) -> float:
        """计算宫位强弱分数"""
        palace = self.palaces.get(palace_name, {})
        score = palace.get("score", 50)
        return float(score)

    def _get_transforms_for_palace(self, palace_name: str) -> List[str]:
        """获取宫位的四化信息"""
        palace_transforms = []
        for t in self.transforms:
            if t.get("palace") == palace_name:
                transform_type = t.get("transform", "")
                star = t.get("star", "")
                palace_transforms.append(f"{transform_type}{star}")
        return palace_transforms

    def _analyze_career_palace(self) -> tuple[str, float, List[str], List[str]]:
        """
        分析官禄宫，返回 (宫位描述, 分数, 优势, 劣势)
        """
        palace_name = "官禄宫"
        stars = self._get_palace_stars(palace_name)
        score = self._get_palace_score(palace_name)
        transforms = self._get_transforms_for_palace(palace_name)

        # 分析优势
        advantages = []
        if stars:
            for star in stars:
                if star in STAR_CAREER_MAPPING:
                    advantages.extend(STAR_CAREER_MAPPING[star])

        # 检查四化
        for t in transforms:
            if "化禄" in t:
                advantages.append("有财运加持")
            elif "化权" in t:
                advantages.append("有权力运势")
            elif "化科" in t:
                advantages.append("学术/名声运势佳")

        # 分析劣势
        disadvantages = []
        # 空的官禄宫
        if not stars:
            disadvantages.append("官禄宫无主星，事业发展需更多努力")
        # 动荡星曜
        动荡星 = ["破军", "七杀", "廉贞", "贪狼"]
        for star in stars:
            if star in 动荡星:
                disadvantages.append(f"{star}在官禄宫，可能导致事业变动较多")

        description = PALACE_CAREER_TENDENCY.get(palace_name, "")
        return description, score, list(set(advantages)), disadvantages

    def _analyze_wealth_type(self) -> str:
        """
        分析财运类型

        Returns:
            财运类型: "正财型" / "横财型" / "技术财型"
        """
        wealth_palace = "财帛宫"
        stars = self._get_palace_stars(wealth_palace)

        if not stars:
            return "未定型"

        # 匹配财运类型
        type_scores = {
            "正财型": 0,
            "横财型": 0,
            "技术财型": 0,
            "艺术财型": 0,
        }

        for star in stars:
            for wealth_type, type_stars in WEALTH_TYPE_STARS.items():
                if star in type_stars:
                    type_scores[wealth_type] += 1

        # 返回得分最高的类型
        if max(type_scores.values()) == 0:
            return "未定型"

        return max(type_scores, key=type_scores.get)

    def _analyze_strengths(self) -> List[str]:
        """
        分析核心优势

        综合命宫、官禄宫、三方四正分析最强特质
        """
        strengths = []

        # 命宫分析
        life_stars = self._get_palace_stars("命宫")
        for star in life_stars:
            if star in STAR_CAREER_MAPPING:
                strengths.extend(STAR_CAREER_MAPPING[star][:2])

        # 官禄宫分析
        career_stars = self._get_palace_stars("官禄宫")
        for star in career_stars:
            if star in STAR_CAREER_MAPPING:
                strengths.extend(STAR_CAREER_MAPPING[star][:2])

        # 迁移宫分析 (社交能力)
        migration_stars = self._get_palace_stars("迁移宫")
        for star in migration_stars:
            if star in ["太阳", "贪狼", "廉贞"]:
                strengths.append("社交能力强")

        # 去重并返回前5个
        unique_strengths = list(dict.fromkeys(strengths))
        return unique_strengths[:5]

    def _calculate_career_type_score(self, career_type: str) -> float:
        """
        计算某种职业类型的匹配度

        匹配度 = (
            官禄宫主星匹配 × 0.35 +
            官禄宫配置分 × 0.25 +
            三方四正配合 × 0.2 +
            四化加分 × 0.15 +
            格局加成 × 0.05
        )
        """
        score = 0.0

        # 1. 官禄宫主星匹配 (35%)
        career_stars = self._get_palace_stars("官禄宫")
        star_match = 0.0
        for star in career_stars:
            if star in STAR_CAREER_MAPPING:
                if career_type in STAR_CAREER_MAPPING[star]:
                    star_match += 33.0  # 每颗星最高33分
        score += min(star_match, 35.0)

        # 2. 官禄宫配置分 (25%)
        palace_score = self._get_palace_score("官禄宫")
        score += (palace_score / 100.0) * 25.0

        # 3. 三方四正配合 (20%)
        sanfang_palaces = ["命宫", "财帛宫", "迁移宫"]
        sanfang_match = 0.0
        for palace in sanfang_palaces:
            palace_stars = self._get_palace_stars(palace)
            for star in palace_stars:
                if star in STAR_CAREER_MAPPING:
                    if career_type in STAR_CAREER_MAPPING[star]:
                        sanfang_match += 6.0  # 每个宫位最高6分
        score += min(sanfang_match, 20.0)

        # 4. 四化加分 (15%)
        transform_bonus = 0.0
        transforms = self._get_transforms_for_palace("官禄宫")
        transforms += self._get_transforms_for_palace("财帛宫")
        for t in transforms:
            if "化禄" in t and career_type in ["金融", "投资", "销售"]:
                transform_bonus += 5.0
            elif "化权" in t and career_type in ["管理", "技术"]:
                transform_bonus += 5.0
            elif "化科" in t and career_type in ["教育", "技术", "咨询"]:
                transform_bonus += 5.0
        score += min(transform_bonus, 15.0)

        # 5. 格局加成 (5%) - 简化处理
        if career_stars:
            if len(career_stars) >= 3:
                score += 5.0  # 多星汇聚

        return min(score, 100.0)

    def _rank_career_options(self) -> List[CareerOption]:
        """
        评分排序职业选项
        """
        # 收集所有职业类型及其得分
        career_scores = {}

        for career_type, career_list in CAREER_NAME_MAPPING.items():
            score = self._calculate_career_type_score(career_type)
            if score > 0:
                career_scores[career_type] = score

        # 排序
        sorted_careers = sorted(
            career_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_n]

        # 生成职业选项
        options = []
        for rank, (career_type, score) in enumerate(sorted_careers, 1):
            career_list = CAREER_NAME_MAPPING.get(career_type, [])
            if career_list:
                career_name, best_industry = career_list[0]

                # 生成匹配理由
                reasons = []
                career_stars = self._get_palace_stars("官禄宫")
                for star in career_stars:
                    if star in STAR_CAREER_MAPPING:
                        if career_type in STAR_CAREER_MAPPING[star]:
                            reasons.append(f"{star}星适合从事{career_type}")

                # 确定等级
                level = "中层" if score >= 70 else "基层" if score >= 50 else "基层"

                # 发展潜力
                potential = "发展潜力高，适合长期深耕" if score >= 70 else "建议从基层积累经验"

                option = CareerOption(
                    rank=rank,
                    career_type=career_type,
                    career_name=career_name,
                    match_score=round(score, 1),
                    level=level,
                    match_reasons=reasons if reasons else [f"命盘配置适合{career_type}方向"],
                    strengths_utilized=self._analyze_strengths()[:3],
                    growth_potential=potential,
                    best_industry=best_industry,
                )
                options.append(option)

        return options

    def _generate_education_advice(self) -> EducationAdvice:
        """
        生成教育建议
        """
        # 分析教育相关宫位
        life_stars = self._get_palace_stars("命宫")
        migration_stars = self._get_palace_stars("迁移宫")

        direction = "未定"
        majors = []
        exam_luck = "一般"

        # 检查学业运势
        has_academic = False
        for star in life_stars + migration_stars:
            if star in ["天机", "天梁", "文昌", "文曲", "化科"]:
                has_academic = True
                break

        if has_academic:
            direction = "学术研究型"
            majors = ["理论研究", "数据分析", "教育学", "法律"]
            exam_luck = "考试运势良好"
        else:
            direction = "实践应用型"
            majors = ["技术技能", "艺术设计", "商业管理", "实务操作"]

        # 学历建议
        education = self.education_level or ""
        if "本科" in education or "硕士" in education:
            suitable_degrees = ["研究生", "博士", "专业认证"]
        elif "高中" in education or "中专" in education:
            suitable_degrees = ["大专", "本科", "职业培训"]
        else:
            suitable_degrees = ["本科", "研究生", "专业技能证书"]

        # 学习环境
        study_env = "适合在稳定的环境中学习" if "天府" in life_stars else "适合在变化中学习实战经验"

        return EducationAdvice(
            direction=direction,
            suitable_degrees=suitable_degrees,
            recommended_majors=majors,
            exam_luck=exam_luck,
            study_environment=study_env,
        )

    def _create_development_roadmap(
        self,
        strongest_palace: str
    ) -> List[str]:
        """
        创建发展路线图
        """
        roadmap = []

        # 基础路线
        roadmap.append(f"短期(1-2年): 在{self.current_career or '当前领域'}积累基础经验")

        if self.current_career:
            roadmap.append(f"中期(3-5年): 向{self._get_palace_stars('官禄宫')[0] if self._get_palace_stars('官禄宫') else '管理'}方向发展")
        else:
            roadmap.append("中期(3-5年): 确定职业方向，深耕细分领域")

        roadmap.append("长期(5-10年): 建立个人品牌，实现职业价值")

        # 根据财运类型调整
        wealth_type = self._analyze_wealth_type()
        if wealth_type == "横财型":
            roadmap.append("注意: 投资需谨慎，避免高风险投资")
        elif wealth_type == "技术财型":
            roadmap.append("建议: 持续提升专业技能，保持竞争力")

        return roadmap

    def _generate_warnings(self) -> List[str]:
        """
        生成职业警示
        """
        warnings = []

        career_stars = self._get_palace_stars("官禄宫")

        # 检查事业风险
        if not career_stars:
            warnings.append("官禄宫无主星，建议谨慎规划职业发展")

        # 检查动荡
        动荡星 = ["破军", "七杀"]
        for star in career_stars:
            if star in 动荡星:
                warnings.append(f"{star}在官禄宫，职业生涯可能有较大变动，需做好规划")

        # 检查四化
        transforms = self._get_transforms_for_palace("官禄宫")
        for t in transforms:
            if "化忌" in t:
                warnings.append("事业宫有化忌，职场人际关系需注意")

        return warnings

    def _calculate_potential_score(self) -> float:
        """
        计算职业潜力综合分
        """
        score = 0.0

        # 官禄宫分数
        career_score = self._get_palace_score("官禄宫")
        score += career_score * 0.4

        # 财帛宫分数
        wealth_score = self._get_palace_score("财帛宫")
        score += wealth_score * 0.2

        # 命宫分数
        life_score = self._get_palace_score("命宫")
        score += life_score * 0.2

        # 迁移宫分数
        migration_score = self._get_palace_score("迁移宫")
        score += migration_score * 0.2

        return round(score / 100.0 * 100, 1)

    def recommend(self) -> CareerRecommendationResult:
        """
        执行职业推荐

        Returns:
            CareerRecommendationResult: 职业推荐结果
        """
        # 分析官禄宫
        palace_desc, palace_score, advantages, disadvantages = self._analyze_career_palace()

        # 确定最强宫位
        strongest_palace = "官禄宫"
        strongest_score = palace_score

        for palace_name in ["命宫", "财帛宫", "迁移宫"]:
            score = self._get_palace_score(palace_name)
            if score > strongest_score:
                strongest_score = score
                strongest_palace = palace_name

        # 生成职业选项
        career_options = self._rank_career_options()

        # 分析财运类型
        wealth_type = self._analyze_wealth_type()

        # 生成教育建议
        education_advice = self._generate_education_advice()

        # 分析核心优势
        key_strengths = self._analyze_strengths()

        # 生成发展路线图
        development_roadmap = self._create_development_roadmap(strongest_palace)

        # 生成警示
        warnings = self._generate_warnings()

        # 计算综合分
        career_potential_score = self._calculate_potential_score()

        # 生成总体分析
        overall_analysis = f"根据命盘分析，{strongest_palace}配置良好，{wealth_type}财运，"
        if career_options:
            top_career = career_options[0]
            overall_analysis += f"最适合从事{top_career.career_type}相关职业。"
        if advantages:
            overall_analysis += f"核心优势: {', '.join(advantages[:3])}。"

        # 计算置信度
        confidence = 0.7 if career_options else 0.5

        return CareerRecommendationResult(
            service_type="career_recommendation",
            strongest_palace=strongest_palace,
            career_potential_score=career_potential_score,
            career_options=career_options,
            wealth_type=wealth_type,
            education_advice=education_advice,
            key_strengths=key_strengths,
            development_roadmap=development_roadmap,
            warnings=warnings,
            overall_analysis=overall_analysis,
            confidence=confidence,
        )


# ============ 便捷函数 ============


def recommend_career_sync(
    chart: Dict[str, Any],
    age: Optional[int] = None,
    current_career: Optional[str] = None,
    education_level: Optional[str] = None,
    top_n: int = 5,
) -> CareerRecommendationResult:
    """
    同步便捷函数 - 执行职业推荐

    Args:
        chart: 命盘数据
        age: 年龄
        current_career: 当前职业
        education_level: 学历
        top_n: 推荐数量

    Returns:
        CareerRecommendationResult: 职业推荐结果
    """
    agent = CareerRecommendationAgent(
        chart=chart,
        age=age,
        current_career=current_career,
        education_level=education_level,
        top_n=top_n,
    )
    return agent.recommend()
