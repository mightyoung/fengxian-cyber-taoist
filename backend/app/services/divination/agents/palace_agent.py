"""
宫位分析智能体 - PalaceAgent

负责分析命盘中的宫位强弱,生成宫位解读。

职责：
1. 加载宫位属性数据
2. 加载宫位强弱评估规则
3. 计算宫位强弱评分
4. 评估宫位重点
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

# 宫位顺序
PALACE_ORDER = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "仆役宫",
    "官禄宫", "田宅宫", "父母宫", "福德宫"
]

# 三方宫位映射 (根据紫微斗数典籍的三方四正规则)
# 三方：指本宫+两个三方宫（隔三位宫）
# 四正：指对宫（隔六位宫）
# 正确逻辑：命宫三方是财帛宫、官禄宫、迁移宫
SANFANG_MAP = {
    "命宫": ["财帛宫", "官禄宫", "迁移宫"],
    "兄弟宫": ["夫妻宫", "子女宫", "疾厄宫"],
    "夫妻宫": ["财帛宫", "迁移宫", "福德宫"],
    "子女宫": ["财帛宫", "官禄宫", "迁移宫"],
    "财帛宫": ["命宫", "子女宫", "疾厄宫"],
    "疾厄宫": ["命宫", "兄弟宫", "子女宫"],
    "迁移宫": ["命宫", "官禄宫", "仆役宫"],
    "仆役宫": ["命宫", "迁移宫", "田宅宫"],
    "官禄宫": ["命宫", "夫妻宫", "子女宫"],
    "田宅宫": ["兄弟宫", "仆役宫", "福德宫"],
    "父母宫": ["子女宫", "疾厄宫", "福德宫"],
    "福德宫": ["夫妻宫", "财帛宫", "田宅宫"]
}

# 对宫映射（已修正）
# 规律：相差6位的宫位互为对宫
# 简记：命↔迁、兄↔仆、夫↔官、子↔田、财↔福、疾↔父
DUIGONG_MAP = {
    "命宫": "迁移宫",
    "兄弟宫": "仆役宫",
    "夫妻宫": "官禄宫",
    "子女宫": "田宅宫",
    "财帛宫": "福德宫",
    "疾厄宫": "父母宫",
    "迁移宫": "命宫",
    "仆役宫": "兄弟宫",
    "官禄宫": "夫妻宫",
    "田宅宫": "子女宫",
    "父母宫": "疾厄宫",
    "福德宫": "财帛宫",
    # 兼容旧名称
    "交友宫": "兄弟宫",  # 仆役宫=交友宫
}

# 多宫位串联主题规则 (中州派核心论命方法)
TOPIC_PALACE_CONNECTIONS = {
    "婚姻": ["夫妻宫", "子女宫", "田宅宫"],
    "事业": ["官禄宫", "财帛宫", "迁移宫"],
    "财运": ["财帛宫", "田宅宫", "福德宫"],
    "健康": ["疾厄宫", "命宫", "父母宫"],
    "人际关系": ["仆役宫", "兄弟宫", "迁移宫"],
    "父母": ["父母宫", "命宫", "福德宫"],
    "子女": ["子女宫", "田宅宫", "夫妻宫"],
    "房产": ["田宅宫", "夫妻宫", "子女宫"],
    "学业": ["父母宫", "官禄宫", "命宫"],
}


class PalaceStrengthLevel(str, Enum):
    """宫位强弱等级"""
    STRONG = "强"    # 70-100分
    MEDIUM = "中"    # 40-69分
    WEAK = "弱"      # 0-39分


@dataclass
class PalaceScore:
    """宫位评分详情"""
    palace_name: str
    total_score: int
    strength_level: str

    # 各维度得分
    master_star_score: int = 0
    auxiliary_star_score: int = 0
    sha_star_deduction: int = 0
    transform_bonus_score: int = 0
    palace_environment_score: int = 0

    # 加权调整
    weighted_score: int = 0


@dataclass
class PalaceAnalysisResult:
    """单个宫位分析结果"""
    palace_name: str
    branch: str
    tiangan: str
    score: PalaceScore
    stars_in_palace: List[Dict[str, Any]]
    focal_point: str
    interpretation: str


@dataclass
class PalaceAnalysis:
    """宫位分析结果"""
    palace_results: List[PalaceAnalysisResult] = field(default_factory=list)
    strongest_palace: str = ""
    weakest_palace: str = ""
    key_palaces: List[str] = field(default_factory=list)


@dataclass
class PalaceConnectionResult:
    """多宫位串联分析结果"""
    topic: str
    connected_palaces: List[str]
    palace_scores: Dict[str, int]
    strongest_in_chain: str
    weakest_in_chain: str
    overall_score: int
    connection_analysis: str
    detailed_interpretation: str


@dataclass
class MultiPalaceConnectionAnalysis:
    """多宫位串联分析汇总"""
    topic: str
    connection_result: PalaceConnectionResult
    chain_summary: str
    recommendations: List[str]


@dataclass
class EmptyPalaceAnalysis:
    """空宫分析结果"""
    palace_name: str
    is_empty: bool
    opposite_palace: str
    opposite_stars: List[Dict[str, Any]]
    projection_strength: str  # 强/中/弱
    projection_analysis: str
    influence_description: str


class PalaceAgent:
    """
    宫位分析智能体

    分析命盘中的宫位强弱,生成详细的宫位解读。
    """

    def __init__(self, chart_data: Dict[str, Any]):
        """
        初始化宫位分析智能体

        Args:
            chart_data: 命盘数据字典
        """
        self.chart = chart_data
        self.palace_attributes = self._load_palace_attributes()
        self.strength_rules = self._load_strength_rules()

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        full_path = os.path.join(project_root, file_path)

        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_palace_attributes(self) -> Dict[str, Any]:
        """加载宫位属性数据"""
        try:
            return self._load_json("data_source/mlx/data/knowledge/palaces/palaces-attributes.json")
        except FileNotFoundError:
            return {"palaces": {}}

    def _load_strength_rules(self) -> Dict[str, Any]:
        """加载宫位强弱评估规则"""
        try:
            return self._load_json("data_source/mlx/data/knowledge/fate/palace-strength-assessment.json")
        except FileNotFoundError:
            return {"scoring_dimensions": {}, "thresholds": {}, "palace_specific": {}}

    def _get_palace_branch(self, palace_name: str) -> str:
        """获取宫位地支"""
        palaces = self.palace_attributes.get("palaces", {})
        return palaces.get(palace_name, {}).get("branch", "")

    def _get_palace_tiangan(self, palace_name: str) -> str:
        """获取宫位天干"""
        palaces_data = self.chart.get("palaces", {})
        return palaces_data.get(palace_name, {}).get("tiangan", "")

    def _get_palace_stars(self, palace_name: str) -> List[Dict[str, Any]]:
        """获取宫位内的所有星曜"""
        palaces_data = self.chart.get("palaces", {})
        palace_data = palaces_data.get(palace_name, {})
        return palace_data.get("stars", [])

    def _get_stars_by_category(
        self,
        palace_name: str
    ) -> Dict[str, List[str]]:
        """获取宫位内按类别分类的星曜"""
        stars = self._get_palace_stars(palace_name)
        result = {
            "main_stars": [],
            "auxiliary_stars": [],
            "sha_stars": [],
            "transform_stars": []
        }

        for star in stars:
            star_type = star.get("type", "")
            star_name = star.get("name", "")

            if star_type == "正曜":
                result["main_stars"].append(star_name)
            elif star_type == "辅星":
                result["auxiliary_stars"].append(star_name)
            elif star_type == "煞星":
                result["sha_stars"].append(star_name)
            elif star_type == "化曜":
                result["transform_stars"].append(star_name)

        return result

    def _calculate_master_star_score(self, palace_name: str) -> int:
        """计算主星强度得分"""
        scoring_rules = self.strength_rules.get("scoring_dimensions", {})
        master_star_rules = scoring_rules.get("master_stars", {}).get("rules", {})

        stars_by_category = self._get_stars_by_category(palace_name)
        main_stars = stars_by_category["main_stars"]

        score = 0
        for star in main_stars:
            star_score = master_star_rules.get(star, {}).get("base_score", 0)
            score += star_score

        # 主星强度最高40分
        return min(score, 40)

    def _calculate_auxiliary_star_score(self, palace_name: str) -> int:
        """计算辅星加分"""
        scoring_rules = self.strength_rules.get("scoring_dimensions", {})
        auxiliary_rules = scoring_rules.get("auxiliary_stars", {}).get("rules", {})

        stars_by_category = self._get_stars_by_category(palace_name)
        auxiliary_stars = stars_by_category["auxiliary_stars"]

        score = 0
        for star in auxiliary_stars:
            star_score = auxiliary_rules.get(star, 1)
            score += star_score

        # 辅星加分最高20分
        return min(score, 20)

    def _calculate_sha_star_deduction(self, palace_name: str) -> int:
        """计算煞星扣分"""
        scoring_rules = self.strength_rules.get("scoring_dimensions", {})
        sha_rules = scoring_rules.get("sha_stars", {}).get("rules", {})

        stars_by_category = self._get_stars_by_category(palace_name)
        sha_stars = stars_by_category["sha_stars"]

        deduction = 0
        for star in sha_stars:
            star_deduction = sha_rules.get(star, -2)
            deduction += star_deduction

        # 煞星扣分最低-20分
        return max(deduction, -20)

    def _calculate_transform_bonus(self, palace_name: str) -> int:
        """计算化曜加成"""
        scoring_rules = self.strength_rules.get("scoring_dimensions", {})
        transform_rules = scoring_rules.get("transform_bonus", {}).get("rules", {})

        stars_by_category = self._get_stars_by_category(palace_name)
        transform_stars = stars_by_category["transform_stars"]

        score = 0
        for star in transform_stars:
            star_score = transform_rules.get(star, 0)
            score += star_score

        # 化曜加成最高20分
        return max(min(score, 20), -20)

    def _calculate_palace_environment_score(self, palace_name: str) -> int:
        """计算宫位环境得分"""
        scoring_rules = self.strength_rules.get("scoring_dimensions", {})
        env_rules = scoring_rules.get("palace_environment", {}).get("rules", {})

        score = 0

        # 检查本宫是否有禄存
        stars_in_palace = self._get_palace_stars(palace_name)
        star_names = [s.get("name", "") for s in stars_in_palace]
        if "禄存" in star_names:
            score += env_rules.get("本宫有禄存", 3)

        # 检查三方是否有主星
        sanfang = SANFANG_MAP.get(palace_name, [])
        has_main_star = False
        for sf_palace in sanfang:
            sf_stars = self._get_stars_by_category(sf_palace)
            if sf_stars["main_stars"]:
                has_main_star = True
                break
        if has_main_star:
            score += env_rules.get("三合有主星", 2)

        # 检查对宫是否有辅星
        duigong = DUIGONG_MAP.get(palace_name, "")
        if duigong:
            dg_stars = self._get_stars_by_category(duigong)
            if dg_stars["auxiliary_stars"]:
                score += env_rules.get("对宫有辅星", 2)

        # 检查三方是否有煞星
        has_sha = False
        for sf_palace in sanfang:
            sf_stars = self._get_stars_by_category(sf_palace)
            if sf_stars["sha_stars"]:
                has_sha = True
                break
        if not has_sha:
            score += env_rules.get("三方无煞", 3)

        # 检查是否为空宫(无主星)
        if not stars_in_palace:
            score += env_rules.get("空宫", -3)
        elif not star_names:  # 无主星
            # 检查是否真的无主星
            has_main = any(
                s.get("type", "") == "正曜"
                for s in stars_in_palace
            )
            if not has_main:
                score += env_rules.get("空宫", -3)

        # 检查本宫是否有忌
        if "化忌" in star_names:
            score += env_rules.get("本宫有忌", -2)

        # 检查三方是否有忌
        has_ji = False
        for sf_palace in sanfang:
            sf_stars = self._get_stars_by_category(sf_palace)
            if "化忌" in sf_stars["transform_stars"]:
                has_ji = True
                break
        if has_ji:
            score += env_rules.get("三方有忌", -1)

        # 宫位环境最高20分
        return max(min(score, 20), -10)

    def calculate_palace_strength(self, palace_name: str) -> PalaceScore:
        """
        计算宫位强弱评分

        使用100分制评分系统：
        - 主星强度: 40分
        - 辅星加分: 20分
        - 煞星扣分: -20分
        - 化曜加成: 20分
        - 宫位环境: 20分

        Args:
            palace_name: 宫位名称

        Returns:
            PalaceScore: 宫位评分详情
        """
        # 获取宫位特定权重调整
        palace_specific = self.strength_rules.get("palace_specific", {})
        palace_tip = palace_specific.get(palace_name, {}).get("scoring_tip", "")

        # 计算各维度得分
        master_score = self._calculate_master_star_score(palace_name)
        auxiliary_score = self._calculate_auxiliary_star_score(palace_name)
        sha_deduction = self._calculate_sha_star_deduction(palace_name)
        transform_score = self._calculate_transform_bonus(palace_name)
        env_score = self._calculate_palace_environment_score(palace_name)

        # 计算总分
        total_score = (
            master_score +
            auxiliary_score +
            sha_deduction +
            transform_score +
            env_score
        )

        # 确保分数在0-100范围内
        total_score = max(0, min(100, total_score))

        # 确定强弱等级
        thresholds = self.strength_rules.get("thresholds", {})
        if total_score >= thresholds.get("strong", {}).get("min", 70):
            level = PalaceStrengthLevel.STRONG.value
        elif total_score >= thresholds.get("medium", {}).get("min", 40):
            level = PalaceStrengthLevel.MEDIUM.value
        else:
            level = PalaceStrengthLevel.WEAK.value

        return PalaceScore(
            palace_name=palace_name,
            total_score=total_score,
            strength_level=level,
            master_star_score=master_score,
            auxiliary_star_score=auxiliary_score,
            sha_star_deduction=sha_deduction,
            transform_bonus_score=transform_score,
            palace_environment_score=env_score
        )

    def _assess_palace_focal_point(self, palace_name: str, score: PalaceScore) -> str:
        """评估宫位重点"""
        palace_specific = self.strength_rules.get("palace_specific", {})
        palace_info = palace_specific.get(palace_name, {})
        default_focus = palace_info.get("focus", "综合分析")

        # 根据得分和结构判断重点
        stars_by_category = self._get_stars_by_category(palace_name)

        # 有化忌需要特别注意
        if "化忌" in stars_by_category["transform_stars"]:
            return f"{default_focus} - 化忌在此宫,需特别注意"

        # 强宫
        if score.strength_level == PalaceStrengthLevel.STRONG.value:
            return f"{default_focus} - 宫位强盛,运势旺盛"

        # 弱宫
        if score.strength_level == PalaceStrengthLevel.WEAK.value:
            return f"{default_focus} - 宫位较弱,需补强"

        # 中等
        return f"{default_focus} - 宫位中等,平稳发展"

    def _generate_palace_interpretation(
        self,
        palace_name: str,
        score: PalaceScore,
        stars_by_category: Dict[str, List[str]]
    ) -> str:
        """生成宫位解读"""
        palace_data = self.palace_attributes.get("palaces", {}).get(palace_name, {})
        nature = palace_data.get("nature", "")
        focus = palace_data.get("focus", "")

        parts = []

        # 基础信息
        parts.append(f"【{palace_name}】({nature})")
        parts.append(f"重点: {focus}")

        # 得分信息
        parts.append(f"\n综合评分: {score.total_score}分 ({score.strength_level})")
        parts.append(f"  主星强度: {score.master_star_score}分")
        parts.append(f"  辅星加分: {score.auxiliary_star_score}分")
        parts.append(f"  煞星扣分: {score.sha_star_deduction}分")
        parts.append(f"  化曜加成: {score.transform_bonus_score}分")
        parts.append(f"  宫位环境: {score.palace_environment_score}分")

        # 星曜情况
        if stars_by_category["main_stars"]:
            parts.append(f"\n主星: {', '.join(stars_by_category['main_stars'])}")
        if stars_by_category["auxiliary_stars"]:
            parts.append(f"辅星: {', '.join(stars_by_category['auxiliary_stars'])}")
        if stars_by_category["sha_stars"]:
            parts.append(f"煞星: {', '.join(stars_by_category['sha_stars'])}")
        if stars_by_category["transform_stars"]:
            parts.append(f"化曜: {', '.join(stars_by_category['transform_stars'])}")

        # 空宫特殊分析
        empty_analysis = self.analyze_empty_palace(palace_name)
        if empty_analysis.is_empty:
            parts.append(f"\n【空宫特殊分析】")
            parts.append(f"对宫: {empty_analysis.opposite_palace}")
            parts.append(f"对宫星曜: {', '.join([s.get('name', '') for s in empty_analysis.opposite_stars]) if empty_analysis.opposite_stars else '无主星'}")
            parts.append(f"投影强度: {empty_analysis.projection_strength}宫")
            parts.append(f"投影分析: {empty_analysis.projection_analysis}")

        # 判断建议
        if empty_analysis.is_empty and empty_analysis.projection_strength == "强":
            advice = "此宫为空宫，但对宫星曜投影力量充沛，实际上不可视为弱宫。"
        elif empty_analysis.is_empty and empty_analysis.projection_strength == "中":
            advice = "此宫为空宫，对宫投影中等，本宫有一定依托但不算强盛。"
        elif empty_analysis.is_empty and empty_analysis.projection_strength == "弱":
            advice = "此宫为空宫且对宫投影较弱，本宫力量不足，行事需谨慎。"
        elif empty_analysis.is_empty:
            advice = "此宫为空宫且对宫无力，为命盘弱点所在，逢大运流年需特别注意。"
        elif score.strength_level == PalaceStrengthLevel.STRONG.value:
            advice = "此宫强盛,运势旺盛,可积极进取。"
        elif score.strength_level == PalaceStrengthLevel.WEAK.value:
            advice = "此宫较弱,需积蓄能量,避免冒险。"
        else:
            advice = "此宫中等,平稳发展,注意把握机遇。"

        parts.append(f"\n建议: {advice}")

        return "\n".join(parts)

    async def analyze_palaces(self) -> PalaceAnalysis:
        """
        分析所有宫位

        Returns:
            PalaceAnalysis: 宫位分析结果
        """
        result = PalaceAnalysis()

        palace_scores = []

        for palace_name in PALACE_ORDER:
            # 计算得分
            score = self.calculate_palace_strength(palace_name)
            palace_scores.append((palace_name, score))

            # 获取星曜
            stars_in_palace = self._get_palace_stars(palace_name)
            stars_by_category = self._get_stars_by_category(palace_name)

            # 获取宫位信息
            branch = self._get_palace_branch(palace_name)
            tiangan = self._get_palace_tiangan(palace_name)

            # 评估重点
            focal_point = self._assess_palace_focal_point(palace_name, score)

            # 生成解读
            interpretation = self._generate_palace_interpretation(
                palace_name, score, stars_by_category
            )

            palace_result = PalaceAnalysisResult(
                palace_name=palace_name,
                branch=branch,
                tiangan=tiangan,
                score=score,
                stars_in_palace=stars_in_palace,
                focal_point=focal_point,
                interpretation=interpretation
            )

            result.palace_results.append(palace_result)

        # 找出最强和最弱宫位
        if palace_scores:
            sorted_scores = sorted(palace_scores, key=lambda x: x[1].total_score, reverse=True)
            result.strongest_palace = sorted_scores[0][0]
            result.weakest_palace = sorted_scores[-1][0]

            # 找出关键宫位(强宫)
            result.key_palaces = [
                name for name, score in sorted_scores
                if score.strength_level == PalaceStrengthLevel.STRONG.value
            ]

        return result

    def get_palace_detail(self, palace_name: str) -> Dict[str, Any]:
        """获取指定宫位的详细分析"""
        score = self.calculate_palace_strength(palace_name)
        stars_in_palace = self._get_palace_stars(palace_name)
        stars_by_category = self._get_stars_by_category(palace_name)
        branch = self._get_palace_branch(palace_name)
        tiangan = self._get_palace_tiangan(palace_name)
        focal_point = self._assess_palace_focal_point(palace_name, score)
        interpretation = self._generate_palace_interpretation(
            palace_name, score, stars_by_category
        )

        return {
            "palace": palace_name,
            "branch": branch,
            "tiangan": tiangan,
            "score": {
                "total": score.total_score,
                "level": score.strength_level,
                "master_star": score.master_star_score,
                "auxiliary_star": score.auxiliary_star_score,
                "sha_star": score.sha_star_deduction,
                "transform": score.transform_bonus_score,
                "environment": score.palace_environment_score
            },
            "stars": stars_by_category,
            "focal_point": focal_point,
            "interpretation": interpretation
        }

    def analyze_multi_palace_connection(self, topic: str) -> PalaceConnectionResult:
        """
        多宫位串联释象分析 (中州派核心论命方法)

        根据梁若瑜《飞星紫微斗数》理论，通过联动多个相关宫位来分析具体事务。

        Args:
            topic: 分析主题
                   支持: 婚姻、事业、财运、健康、人际关系、父母、子女、房产、学业

        Returns:
            PalaceConnectionResult: 多宫位串联分析结果
        """
        # 获取主题对应的宫位串联
        connected_palaces = TOPIC_PALACE_CONNECTIONS.get(topic, [])
        if not connected_palaces:
            # 如果主题不匹配，返回默认分析
            connected_palaces = [topic, "命宫", "福德宫"]

        # 计算串联宫位的得分
        palace_scores: Dict[str, int] = {}
        palace_details: Dict[str, Dict[str, Any]] = {}

        for palace in connected_palaces:
            score = self.calculate_palace_strength(palace)
            palace_scores[palace] = score.total_score
            palace_details[palace] = {
                "score": score,
                "stars": self._get_stars_by_category(palace),
                "stars_in_palace": self._get_palace_stars(palace)
            }

        # 找出串联中最强和最弱宫位
        strongest = max(palace_scores.items(), key=lambda x: x[1])
        weakest = min(palace_scores.items(), key=lambda x: x[1])

        # 计算整体得分 (加权平均，强宫权重更高)
        total_weight = sum(range(1, len(connected_palaces) + 1))
        weighted_sum = sum(
            score * (idx + 1)
            for idx, score in enumerate(palace_scores.values())
        )
        overall_score = round(weighted_sum / total_weight)

        # 生成联动分析
        connection_analysis = self._generate_connection_analysis(
            topic, connected_palaces, palace_scores, palace_details
        )

        # 生成详细解读
        detailed_interpretation = self._generate_connection_interpretation(
            topic, connected_palaces, palace_scores, palace_details,
            strongest[0], weakest[0], overall_score
        )

        return PalaceConnectionResult(
            topic=topic,
            connected_palaces=connected_palaces,
            palace_scores=palace_scores,
            strongest_in_chain=strongest[0],
            weakest_in_chain=weakest[0],
            overall_score=overall_score,
            connection_analysis=connection_analysis,
            detailed_interpretation=detailed_interpretation
        )

    def _generate_connection_analysis(
        self,
        topic: str,
        connected_palaces: List[str],
        palace_scores: Dict[str, int],
        palace_details: Dict[str, Dict[str, Any]]
    ) -> str:
        """生成宫位联动分析"""
        lines = []

        # 分析各宫位之间的关联
        for i, palace in enumerate(connected_palaces):
            duigong = DUIGONG_MAP.get(palace, "")
            sanfang = SANFANG_MAP.get(palace, [])

            palace_info = palace_details[palace]
            score = palace_info["score"]
            stars = palace_info["stars"]

            lines.append(f"\n【{palace}】({score.strength_level}宫, {score.total_score}分)")

            # 分析本宫星曜
            main_stars = stars["main_stars"]
            aux_stars = stars["auxiliary_stars"]
            sha_stars = stars["sha_stars"]
            trans_stars = stars["transform_stars"]

            if main_stars:
                lines.append(f"  主星: {', '.join(main_stars)}")
            if aux_stars:
                lines.append(f"  辅星: {', '.join(aux_stars)}")
            if sha_stars:
                lines.append(f"  煞星: {', '.join(sha_stars)}")
            if trans_stars:
                lines.append(f"  化曜: {', '.join(trans_stars)}")

            # 分析对宫影响
            if duigong and duigong in connected_palaces:
                duigong_score = palace_scores.get(duigong, 0)
                if duigong_score > score.total_score:
                    lines.append(f"  → 对宫{duigong}较强({duigong_score}分)，有投影增强效果")
                elif duigong_score < score.total_score:
                    lines.append(f"  → 对宫{duigong}较弱({duigong_score}分)，投影力量不足")

            # 分析三方影响
            sanfang_strong = [sf for sf in sanfang if palace_scores.get(sf, 0) >= 60]
            if sanfang_strong:
                lines.append(f"  → 三方强宫: {', '.join(sanfang_strong)}")

        return "\n".join(lines)

    def _generate_connection_interpretation(
        self,
        topic: str,
        connected_palaces: List[str],
        palace_scores: Dict[str, int],
        palace_details: Dict[str, Dict[str, Any]],
        strongest: str,
        weakest: str,
        overall_score: int
    ) -> str:
        """生成多宫位串联详细解读"""
        lines = []

        # 主题概述
        lines.append(f"{'=' * 50}")
        lines.append(f"【{topic}】多宫位串联释象分析")
        lines.append(f"{'=' * 50}")

        # 整体评估
        lines.append(f"\n整体评估: {overall_score}分")
        if overall_score >= 70:
            lines.append("综合评价: 串联宫位整体强盛，此项运势旺盛，布局良好。")
        elif overall_score >= 40:
            lines.append("综合评价: 串联宫位中等，运势平稳，需把握机遇。")
        else:
            lines.append("综合评价: 串联宫位较弱，需补强调理，注意风险。")

        # 强弱宫位
        lines.append(f"\n最强宫位: {strongest}({palace_scores[strongest]}分)")
        lines.append(f"最弱宫位: {weakest}({palace_scores[weakest]}分)")

        # 主题分析
        topic_intros = {
            "婚姻": "婚姻宫位串联分析：夫妻宫为核心，联动子女宫(子女缘分)与田宅宫(家庭环境)。",
            "事业": "事业宫位串联分析：官禄宫为核心，联动财帛宫(财运)与迁移宫(外发展)。",
            "财运": "财运宫位串联分析：财帛宫为核心，联动田宅宫(固定资产)与福德宫(福报享受)。",
            "健康": "健康宫位串联分析：疾厄宫为核心，联动命宫(本体)与父母宫(先天体质)。",
            "人际关系": "人际关系宫位串联分析：仆役宫为核心，联动兄弟宫(兄弟姐妹)与迁移宫(外人)。",
            "父母": "父母宫位串联分析：父母宫为核心，联动命宫(自我)与福德宫(福荫)。",
            "子女": "子女宫位串联分析：子女宫为核心，联动田宅宫(家宅)与夫妻宫(婚姻)。",
            "房产": "房产宫位串联分析：田宅宫为核心，联动夫妻宫(配偶)与子女宫(后代)。",
            "学业": "学业宫位串联分析：父母宫(文书宫)为核心，联动官禄宫(事业)与命宫(自我)。",
        }

        lines.append(f"\n{topic_intros.get(topic, '')}")

        # 详细分析各宫
        lines.append(f"\n各宫详细分析:")
        for palace in connected_palaces:
            palace_info = palace_details[palace]
            score = palace_info["score"]
            stars = palace_info["stars"]
            stars_list = palace_info["stars_in_palace"]

            lines.append(f"\n  {palace}:")
            lines.append(f"    得分: {score.total_score}分 ({score.strength_level})")

            # 星曜组合分析
            main = stars["main_stars"]
            aux = stars["auxiliary_stars"]
            sha = stars["sha_stars"]
            trans = stars["transform_stars"]

            if main:
                lines.append(f"    主星: {', '.join(main)}")

            # 格局判断
            if main and len(main) >= 2:
                lines.append(f"    格局: 双星同宫，力量较强")
            elif main and aux:
                lines.append(f"    格局: 主星得辅星拱照，格局良好")
            elif sha and len(sha) >= 2:
                lines.append(f"    格局: 多煞汇聚，需谨慎")

            # 化曜影响
            if trans:
                trans_names = [t for t in trans if t.startswith("化")]
                if trans_names:
                    lines.append(f"    化曜: {', '.join(trans_names)}")
                    for t in trans_names:
                        if t == "化禄":
                            lines.append(f"      → 化禄增强财运/吉庆")
                        elif t == "化权":
                            lines.append(f"      → 化权增强事业/竞争力")
                        elif t == "化科":
                            lines.append(f"      → 化科增强学业/名声")
                        elif t == "化忌":
                            lines.append(f"      → 化忌需特别注意阻碍")

        # 综合建议
        lines.append(f"\n综合建议:")

        # 根据最弱宫位给出建议
        weakest_score = palace_scores[weakest]
        if weakest_score < 40:
            weak_palace_advice = {
                "命宫": "命宫较弱，自我能量不足，需提升核心竞争力。",
                "兄弟宫": "兄弟宫较弱，人际合伙需谨慎，避免合伙纠纷。",
                "夫妻宫": "夫妻宫较弱，婚姻感情需用心经营，避免第三者介入。",
                "子女宫": "子女宫较弱，子女缘分淡薄或需关注子女教育。",
                "财帛宫": "财帛宫较弱，理财需保守，避免投机冒险。",
                "疾厄宫": "疾厄宫较弱，健康需注意，定期体检保养。",
                "迁移宫": "迁移宫较弱，外出发展受限，扎根本地较宜。",
                "仆役宫": "仆役宫较弱，朋友助力不足，谨防小人。",
                "官禄宫": "官禄宫较弱，事业进展缓慢，需加倍努力。",
                "田宅宫": "田宅宫较弱，房产运势不佳，不宜重大投资。",
                "父母宫": "父母宫较弱，与父母缘分浅或文书事由不顺。",
                "福德宫": "福德宫较弱，福报不足，享受较少，宜积德行善。"
            }
            advice = weak_palace_advice.get(weakest, "此宫较弱，需针对性调理。")
            lines.append(f"  1. {advice}")

        # 根据最强宫位给出建议
        strongest_score = palace_scores[strongest]
        if strongest_score >= 70:
            strong_palace_advice = {
                "命宫": "命宫强盛，自我能量充沛，可积极进取。",
                "兄弟宫": "兄弟宫强盛，人脉广泛，合伙运势佳。",
                "夫妻宫": "夫妻宫强盛，婚姻美满，感情顺利。",
                "子女宫": "子女宫强盛，子女缘分深厚，桃李满天下。",
                "财帛宫": "财帛宫强盛，财运亨通，正财偏财皆旺。",
                "疾厄宫": "疾厄宫强盛，身体健康，抵抗能力强。",
                "迁移宫": "迁移宫强盛，出外得贵，远行发展有利。",
                "仆役宫": "仆役宫强盛，友人相助，下属得力。",
                "官禄宫": "官禄宫强盛，事业发达，仕途顺遂。",
                "田宅宫": "田宅宫强盛，房产运佳，置产有利。",
                "父母宫": "父母宫强盛，父母安康，文书运势佳。",
                "福德宫": "福德宫强盛，福泽深厚，享受充足。"
            }
            advice = strong_palace_advice.get(strongest, "此宫强盛，可善加利用。")
            lines.append(f"  2. {advice}")

        # 串联关系建议
        lines.append(f"  3. 宫位串联关系:")
        if connected_palaces == ["夫妻宫", "子女宫", "田宅宫"]:
            lines.append("     婚姻线：家庭-子女-婚姻三位一体，相互影响。")
            lines.append("     建议：家庭和睦有利于婚姻，子女教育需共同关注。")
        elif connected_palaces == ["官禄宫", "财帛宫", "迁移宫"]:
            lines.append("     事业线：官禄-财帛-迁移三方位联动。")
            lines.append("     建议：事业发展带动财运，外出机遇需把握。")
        elif connected_palaces == ["财帛宫", "田宅宫", "福德宫"]:
            lines.append("     财运线：现金-固定资产-福报三位一看。")
            lines.append("     建议：开源节流并重，房产投资需时机。")

        return "\n".join(lines)

    def analyze_multi_palace_sync(self, topic: str) -> PalaceConnectionResult:
        """同步版本的多宫位串联分析"""
        return self.analyze_multi_palace_connection(topic)

    def _is_empty_palace(self, palace_name: str) -> bool:
        """判断宫位是否为空宫（无十四正曜）"""
        stars_in_palace = self._get_palace_stars(palace_name)
        if not stars_in_palace:
            return True
        # 检查是否有正曜
        has_main_star = any(
            star.get("type", "") == "正曜"
            for star in stars_in_palace
        )
        return not has_main_star

    def _get_opposite_palace_stars(self, palace_name: str) -> List[Dict[str, Any]]:
        """获取对宫星曜"""
        duigong = DUIGONG_MAP.get(palace_name, "")
        if not duigong:
            return []
        return self._get_palace_stars(duigong)

    def _assess_projection_strength(
        self,
        opposite_stars: List[Dict[str, Any]],
        duigong_name: str
    ) -> str:
        """
        评估对宫星曜投影强度

        投影强度判断规则：
        1. 对宫有主星且庙旺 → 投影强
        2. 对宫有主星但平和 → 投影中
        3. 对宫有主星但失陷 → 投影弱
        4. 对宫无主星但有辅星 → 投影中
        5. 对宫无星 → 投影极弱/无
        """
        if not opposite_stars:
            return "极弱"

        has_main_star = any(star.get("type", "") == "正曜" for star in opposite_stars)
        if not has_main_star:
            # 无主星，检查辅星
            has_aux = any(star.get("type", "") == "辅星" for star in opposite_stars)
            if has_aux:
                return "中"
            return "极弱"

        # 有主星，判断庙旺平陷
        star_levels = [star.get("level", "") for star in opposite_stars]
        if any(level in ["庙", "旺"] for level in star_levels):
            return "强"
        elif any(level in ["平", "得"] for level in star_levels):
            return "中"
        elif any(level in ["陷", "不得"] for level in star_levels):
            return "弱"
        return "中"

    def _analyze_projection_influence(
        self,
        palace_name: str,
        opposite_palace: str,
        opposite_stars: List[Dict[str, Any]],
        projection_strength: str
    ) -> str:
        """分析对宫投影的具体影响"""
        if not opposite_stars:
            return f"空宫无主星，对宫{opposite_palace}亦无星曜，故此宫本身力量极弱，仅靠自身环境勉强维持。"

        parts = []
        main_stars = [s for s in opposite_stars if s.get("type") == "正曜"]
        aux_stars = [s for s in opposite_stars if s.get("type") == "辅星"]
        sha_stars = [s for s in opposite_stars if s.get("type") == "煞星"]
        trans_stars = [s for s in opposite_stars if s.get("type") == "化曜"]

        # 主星投影
        if main_stars:
            star_names = [s.get("name", "") for s in main_stars]
            star_levels = [s.get("level", "") for s in main_stars]
            parts.append(f"对宫{opposite_palace}有主星{','.join(star_names)}")

            # 判断庙旺
            miao_count = sum(1 for l in star_levels if l in ["庙", "旺"])
            ping_count = sum(1 for l in star_levels if l in ["平", "得"])
            xian_count = sum(1 for l in star_levels if l in ["陷", "不得"])

            if miao_count > 0:
                parts.append("，星曜庙旺，投影力量较强")
            elif ping_count > 0:
                parts.append("，星曜平和，投影力量中等")
            elif xian_count > 0:
                parts.append("，星曜失陷，投影力量较弱")
            else:
                parts.append("，投影力量中等")

        # 辅星增强
        if aux_stars:
            aux_names = [s.get("name", "") for s in aux_stars]
            parts.append(f"；对宫辅星{','.join(aux_names)}可增强对宫力量")

        # 煞星影响
        if sha_stars:
            sha_names = [s.get("name", "") for s in sha_stars]
            parts.append(f"；但对宫煞星{','.join(sha_names)}会削弱投影效果")

        # 化曜影响
        if trans_stars:
            trans_names = [s.get("name", "") for s in trans_stars]
            parts.append(f"；对宫化曜{','.join(trans_names)}产生特殊影响")

        # 综合投影评估
        strength_desc = {
            "强": "投影力量充沛，可有效补强本宫",
            "中": "投影力量一般，本宫有一定依托",
            "弱": "投影力量不足，本宫偏弱",
            "极弱": "几近无投影，本宫力量薄弱"
        }.get(projection_strength, "")

        parts.append(f"。整体而言，{strength_desc}。")

        return "".join(parts)

    def analyze_empty_palace(self, palace_name: str) -> EmptyPalaceAnalysis:
        """
        分析空宫的特殊情况

        空宫指无十四正曜落入的宫位。空宫并非真的"无星"，
        而是需要看对宫星曜的投影影响。

        Args:
            palace_name: 宫位名称

        Returns:
            EmptyPalaceAnalysis: 空宫分析结果
        """
        # 判断是否为空宫
        is_empty = self._is_empty_palace(palace_name)

        # 获取对宫
        opposite_palace = DUIGONG_MAP.get(palace_name, "")

        # 获取对宫星曜
        opposite_stars = self._get_opposite_palace_stars(palace_name)

        # 评估投影强度
        projection_strength = self._assess_projection_strength(
            opposite_stars, opposite_palace
        )

        # 分析投影影响
        projection_analysis = self._analyze_projection_influence(
            palace_name, opposite_palace, opposite_stars, projection_strength
        )

        # 生成空宫影响描述
        if is_empty:
            influence_parts = [
                f"【{palace_name}为空宫】",
                f"对宫{opposite_palace}星曜投影分析："
            ]

            if opposite_stars:
                star_names = [s.get("name", "") for s in opposite_stars]
                star_types = list(set([s.get("type", "") for s in opposite_stars]))
                influence_parts.append(
                    f"对宫有{','.join(star_types)}：{','.join(star_names)}"
                )
            else:
                influence_parts.append(f"对宫{opposite_palace}亦无星曜，力量最弱")

            influence_parts.append(f"\n投影强度：{projection_strength}宫")
            influence_parts.append(f"具体分析：{projection_analysis}")

            # 特殊建议
            if projection_strength == "强":
                influence_parts.append(
                    "\n空宫得力：此空宫虽有主星缺失，但对宫星曜庙旺得势，"
                    "投影力量充沛，实际上相当于有主星坐守，不可视为弱宫。"
                )
            elif projection_strength == "中":
                influence_parts.append(
                    "\n空宫中等：此空宫对宫星曜力量平和，投影效果一般，"
                    "本宫有一定依托但不算强盛，需结合三方综合判断。"
                )
            elif projection_strength == "弱":
                influence_parts.append(
                    "\n空宫偏弱：此空宫对宫星曜失陷，投影力量不足，"
                    "本宫较弱，宜静不宜动，需谨慎行事。"
                )
            else:
                influence_parts.append(
                    "\n空宫无力：此空宫对宫亦无星曜，力量极为薄弱，"
                    "为命盘中的弱点所在，逢大运流年需特别注意补强。"
                )

            influence_description = "\n".join(influence_parts)
        else:
            influence_description = f"【{palace_name}非空宫】本宫有主星坐守，不需考虑对宫投影影响。"

        return EmptyPalaceAnalysis(
            palace_name=palace_name,
            is_empty=is_empty,
            opposite_palace=opposite_palace,
            opposite_stars=opposite_stars,
            projection_strength=projection_strength,
            projection_analysis=projection_analysis,
            influence_description=influence_description
        )

    def generate_multi_palace_report(self, topic: str) -> str:
        """生成多宫位串联分析报告"""
        result = self.analyze_multi_palace_connection(topic)
        return result.detailed_interpretation

    def generate_palace_report(self) -> str:
        """生成宫位分析报告文本"""
        import asyncio

        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 没有运行中的事件循环，可以安全使用asyncio.run()
            return asyncio.run(self._generate_palace_report_async())
        else:
            # 在事件循环中运行，需要创建一个任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, self._generate_palace_report_async())
                return future.result()

    async def _generate_palace_report_async(self) -> str:
        """异步生成宫位分析报告"""
        analysis = await self.analyze_palaces()

        lines = ["=" * 60]
        lines.append("宫位强弱分析报告")
        lines.append("=" * 60)

        # 强弱宫位汇总
        lines.append(f"\n最强宫位: {analysis.strongest_palace}")
        lines.append(f"最弱宫位: {analysis.weakest_palace}")
        lines.append(f"强宫: {', '.join(analysis.key_palaces) if analysis.key_palaces else '无'}")

        # 各宫位详细分析
        lines.append("\n" + "=" * 60)
        lines.append("各宫位详细分析")
        lines.append("=" * 60)

        for palace_result in analysis.palace_results:
            lines.append(f"\n{palace_result.interpretation}")
            lines.append("-" * 40)

        lines.append("\n" + "=" * 60)
        lines.append(f"分析宫位数: {len(analysis.palace_results)}")
        lines.append("=" * 60)

        return "\n".join(lines)


# ============ LLM增强分析 ============

class LLVMPalaceAnalyzer:
    """宫位分析LLM增强器"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度宫位分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import (
            PALACE_SYSTEM_PROMPT,
            build_palace_user_prompt,
            format_analysis_as_text,
            load_palace_cases,
            load_six_relation_cases,
            get_relevant_cases,
            format_cases_as_context
        )

        # 构建提示词
        user_prompt = build_palace_user_prompt(self.chart, question)

        # 确保宫位案例被添加到prompt中
        # get_relevant_cases 对宫位案例的匹配可能不完善,当返回空时直接获取案例补充
        palace_cases = load_palace_cases()
        relevant_cases = get_relevant_cases(palace_cases, self.chart, limit=6)
        # 如果相关案例为空但存在全局案例,则使用前6个作为参考
        if not relevant_cases and palace_cases:
            relevant_cases = palace_cases[:6]
        if relevant_cases:
            user_prompt += format_cases_as_context(relevant_cases, "宫位")

        # 添加六亲论断案例
        six_relation_cases = load_six_relation_cases()
        relevant_six_cases = get_relevant_cases(six_relation_cases, self.chart, limit=6)
        if relevant_six_cases:
            user_prompt += format_cases_as_context(relevant_six_cases, "六亲")

        messages = [
            {"role": "system", "content": PALACE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature)

        return result

    def analyze_with_llm_sync(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """同步版本的LLM分析"""
        import asyncio
        return asyncio.run(self.analyze_with_llm(question, temperature))

    async def generate_text_report(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """生成文本格式的LLM分析报告"""
        from .llm_prompts import format_analysis_as_text

        result = await self.analyze_with_llm(question, temperature)
        return format_analysis_as_text(result)


async def llm_analyze_palaces(
    chart_data: Dict[str, Any],
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用LLM分析命盘宫位

    Args:
        chart_data: 命盘数据
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLVMPalaceAnalyzer(chart_data)
    return await analyzer.analyze_with_llm(question)


def llm_analyze_palaces_sync(
    chart_data: Dict[str, Any],
    question: Optional[str] = None
) -> Dict[str, Any]:
    """同步版本的LLM宫位分析"""
    import asyncio
    return asyncio.run(llm_analyze_palaces(chart_data, question))


# ============ 便捷函数 ============

async def analyze_chart_palaces(chart_data: Dict[str, Any]) -> PalaceAnalysis:
    """
    分析命盘宫位

    Args:
        chart_data: 命盘数据

    Returns:
        PalaceAnalysis: 宫位分析结果
    """
    agent = PalaceAgent(chart_data)
    return await agent.analyze_palaces()


def analyze_palaces_sync(chart_data: Dict[str, Any]) -> PalaceAnalysis:
    """同步版本的宫位分析"""
    import asyncio
    return asyncio.run(analyze_chart_palaces(chart_data))


# ============ 多宫位串联分析便捷函数 ============

def analyze_multi_palace_connection(
    chart_data: Dict[str, Any],
    topic: str
) -> PalaceConnectionResult:
    """
    多宫位串联释象分析 (中州派核心论命方法)

    Args:
        chart_data: 命盘数据
        topic: 分析主题 (婚姻/事业/财运/健康/人际关系/父母/子女/房产/学业)

    Returns:
        PalaceConnectionResult: 多宫位串联分析结果
    """
    agent = PalaceAgent(chart_data)
    return agent.analyze_multi_palace_connection(topic)


def generate_multi_palace_report(
    chart_data: Dict[str, Any],
    topic: str
) -> str:
    """
    生成多宫位串联分析报告文本

    Args:
        chart_data: 命盘数据
        topic: 分析主题

    Returns:
        str: 格式化的分析报告
    """
    agent = PalaceAgent(chart_data)
    return agent.generate_multi_palace_report(topic)


# ============ 空宫分析便捷函数 ============

def analyze_empty_palace(
    chart_data: Dict[str, Any],
    palace_name: str
) -> EmptyPalaceAnalysis:
    """
    分析空宫的特殊情况

    空宫指无十四正曜落入的宫位。空宫并非真的"无星"，
    而是需要看对宫星曜的投影影响。

    Args:
        chart_data: 命盘数据
        palace_name: 宫位名称

    Returns:
        EmptyPalaceAnalysis: 空宫分析结果，包含对宫星曜投影分析
    """
    agent = PalaceAgent(chart_data)
    return agent.analyze_empty_palace(palace_name)


def get_all_empty_palaces(chart_data: Dict[str, Any]) -> List[EmptyPalaceAnalysis]:
    """
    获取所有空宫及其分析

    Args:
        chart_data: 命盘数据

    Returns:
        List[EmptyPalaceAnalysis]: 所有空宫的分析结果列表
    """
    agent = PalaceAgent(chart_data)
    empty_palaces = []

    for palace_name in PALACE_ORDER:
        if agent._is_empty_palace(palace_name):
            empty_palaces.append(agent.analyze_empty_palace(palace_name))

    return empty_palaces


def analyze_empty_palace_sync(
    chart_data: Dict[str, Any],
    palace_name: str
) -> EmptyPalaceAnalysis:
    """同步版本的空宫分析"""
    return analyze_empty_palace(chart_data, palace_name)


# ============ 测试 ============

if __name__ == "__main__":
    # 测试示例
    import asyncio

    async def main():
        # 模拟命盘数据
        test_chart = {
            "birth_info": {
                "year": 1990,
                "month": 5,
                "day": 15,
                "gender": "male",
                "wuxing_ju": "水二局"
            },
            "palaces": {
                "命宫": {"branch": "子", "tiangan": "甲", "stars": [
                    {"name": "紫微", "type": "正曜", "level": "旺"},
                    {"name": "天机", "type": "正曜", "level": "平"},
                    {"name": "左辅", "type": "辅星", "level": "旺"}
                ]},
                "兄弟宫": {"branch": "丑", "tiangan": "乙", "stars": [
                    {"name": "太阴", "type": "正曜", "level": "旺"}
                ]},
                "夫妻宫": {"branch": "寅", "tiangan": "丙", "stars": [
                    {"name": "贪狼", "type": "正曜", "level": "庙"},
                    {"name": "天钺", "type": "辅星", "level": "旺"}
                ]},
                "子女宫": {"branch": "卯", "tiangan": "丁", "stars": [
                    {"name": "天梁", "type": "正曜", "level": "旺"}
                ]},
                "财帛宫": {"branch": "辰", "tiangan": "戊", "stars": [
                    {"name": "太阳", "type": "正曜", "level": "旺"},
                    {"name": "化禄", "type": "化曜", "level": "庙"}
                ]},
                "疾厄宫": {"branch": "巳", "tiangan": "己", "stars": [
                    {"name": "天相", "type": "正曜", "level": "庙"},
                    {"name": "陀罗", "type": "煞星", "level": "陷"}
                ]},
                "迁移宫": {"branch": "午", "tiangan": "庚", "stars": [
                    {"name": "巨门", "type": "正曜", "level": "旺"},
                    {"name": "天魁", "type": "辅星", "level": "旺"},
                    {"name": "擎羊", "type": "煞星", "level": "陷"}
                ]},
                "仆役宫": {"branch": "未", "tiangan": "辛", "stars": [
                    {"name": "七杀", "type": "正曜", "level": "旺"}
                ]},
                "官禄宫": {"branch": "申", "tiangan": "壬", "stars": [
                    {"name": "天同", "type": "正曜", "level": "庙"},
                    {"name": "文昌", "type": "辅星", "level": "平"},
                    {"name": "化权", "type": "化曜", "level": "旺"}
                ]},
                "田宅宫": {"branch": "酉", "tiangan": "癸", "stars": [
                    {"name": "武曲", "type": "正曜", "level": "旺"},
                    {"name": "破军", "type": "正曜", "level": "旺"},
                    {"name": "火星", "type": "煞星", "level": "陷"}
                ]},
                "父母宫": {"branch": "戌", "tiangan": "甲", "stars": [
                    {"name": "天府", "type": "正曜", "level": "旺"},
                    {"name": "地空", "type": "煞星", "level": "陷"}
                ]},
                "福德宫": {"branch": "亥", "tiangan": "乙", "stars": [
                    {"name": "廉贞", "type": "正曜", "level": "旺"},
                    {"name": "右弼", "type": "辅星", "level": "旺"},
                    {"name": "化忌", "type": "化曜", "level": "陷"}
                ]}
            },
            "stars": {
                "main_stars": [
                    {"name": "紫微", "palace": "命宫", "level": "旺", "type": "正曜"},
                    {"name": "天机", "palace": "命宫", "level": "平", "type": "正曜"}
                ],
                "auxiliary_stars": [
                    {"name": "左辅", "palace": "命宫", "level": "旺", "type": "辅星"}
                ],
                "sha_stars": [],
                "transform_stars": []
            },
            "transforms": []
        }

        agent = PalaceAgent(test_chart)

        # 测试宫位评分
        print("=== 宫位分析测试 ===\n")

        # 测试命宫评分
        ming_score = agent.calculate_palace_strength("命宫")
        print(f"命宫评分: {ming_score.total_score}分 ({ming_score.strength_level})")
        print(f"  主星强度: {ming_score.master_star_score}")
        print(f"  辅星加分: {ming_score.auxiliary_star_score}")
        print(f"  煞星扣分: {ming_score.sha_star_deduction}")
        print(f"  化曜加成: {ming_score.transform_bonus_score}")
        print(f"  宫位环境: {ming_score.palace_environment_score}")

        # 测试福德宫评分
        fude_score = agent.calculate_palace_strength("福德宫")
        print(f"\n福德宫评分: {fude_score.total_score}分 ({fude_score.strength_level})")
        print(f"  主星强度: {fude_score.master_star_score}")
        print(f"  辅星加分: {fude_score.auxiliary_star_score}")
        print(f"  煞星扣分: {fude_score.sha_star_deduction}")
        print(f"  化曜加成: {fude_score.transform_bonus_score}")
        print(f"  宫位环境: {fude_score.palace_environment_score}")

        # 测试完整分析
        analysis = await agent.analyze_palaces()
        print(f"\n最强宫位: {analysis.strongest_palace}")
        print(f"最弱宫位: {analysis.weakest_palace}")
        print(f"强宫列表: {analysis.key_palaces}")

        # 测试详细分析
        print("\n=== 命宫详细分析 ===")
        detail = agent.get_palace_detail("命宫")
        print(detail["interpretation"])

        # 测试报告生成
        print("\n" + "=" * 60)
        print(agent.generate_palace_report())

    asyncio.run(main())
