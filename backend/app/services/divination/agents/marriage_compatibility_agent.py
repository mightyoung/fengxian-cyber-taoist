"""
姻缘配对分析智能体 - MarriageCompatibilityAgent

分析两个人的姻缘配对度，输出配对指数+分维度评分+建议。

职责：
1. 分析性格契合度（命宫对比）
2. 分析财运互补（财帛宫对比）
3. 分析事业助力（官禄宫对比）
4. 分析感情甜蜜度（夫妻宫对比）
5. 分析健康同步（疾厄宫对比）
6. 检查有害组合
7. 分析大运同步性
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

# 导入共用类型
from ..service_types import FortuneLevel, fortune_level_from_score, normalize_score

# 五行相生相克关系
WUXING_SHENG = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木",
}

WUXING_KENG = {
    "木": "金",
    "火": "水",
    "土": "木",
    "金": "火",
    "水": "土",
}

# 主星五行属性
STAR_WUXING = {
    # 甲级星
    "紫微": "土",
    "天机": "木",
    "太阳": "火",
    "武曲": "金",
    "天同": "水",
    "廉贞": "火",
    "天府": "土",
    "太阴": "水",
    "贪狼": "木",
    "巨门": "水",
    "天相": "水",
    "天梁": "土",
    "七杀": "金",
    "破军": "水",
    # 乙级星
    "文昌": "金",
    "文曲": "水",
    "左辅": "土",
    "右弼": "水",
    "天魁": "火",
    "天钺": "火",
    "火星": "火",
    "铃星": "火",
    "擎羊": "金",
    "陀罗": "火",
    "地空": "火",
    "地劫": "火",
    "化禄": "水",
    "化权": "火",
    "化科": "木",
    "化忌": "水",
}

# 吉星列表
LUCKY_STARS = [
    "紫微", "天府", "天相", "天魁", "天钺",
    "左辅", "右弼", "文昌", "文曲",
    "化禄", "化科",
]

# 桃花星列表
PEACH_BLOSSOM_STARS = [
    "贪狼", "廉贞", "太阴", "天喜", "红鸾",
    "咸池", "天姚", "沐浴",
]

# 煞星列表
MALIFIC_STARS = [
    "火星", "铃星", "擎羊", "陀罗", "地空", "地劫",
    "化忌",
]


class CompatibilityLevel(Enum):
    """配对等级"""
    PERFECT = "完美姻缘"      # 90-100
    EXCELLENT = "天作之合"     # 80-89
    GOOD = "良缘佳配"         # 70-79
    AVERAGE = "中规中矩"      # 50-69
    FAIR = "需要努力"         # 30-49
    CHALLENGING = "磨合期"     # 0-29


@dataclass
class CompatibilityDimension:
    """配对维度"""
    dimension: str              # "性格契合" / "财运互补" / "事业助力" / "感情甜蜜" / "健康同步"
    score: float               # 维度分数 0-100
    level: str                 # 等级
    analysis: str              # 分析理由
    positive_factors: List[str] = field(default_factory=list)
    negative_factors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dimension": self.dimension,
            "score": self.score,
            "level": self.level,
            "analysis": self.analysis,
            "positive_factors": self.positive_factors,
            "negative_factors": self.negative_factors,
        }


@dataclass
class CompatibilityResult:
    """姻缘配对结果"""
    service_type: str = "marriage_compatibility"
    person_a_name: str = "甲方"
    person_b_name: str = "乙方"
    overall_score: float = 0.0                    # 综合配对指数 0-100
    overall_level: str = ""                      # 等级
    dimensions: List[CompatibilityDimension] = field(default_factory=list)
    compatibility_highlights: List[str] = field(default_factory=list)  # 亮点
    compatibility_warnings: List[str] = field(default_factory=list)     # 警示
    best_timing: str = ""                        # 最佳时机
    suggestions: List[str] = field(default_factory=list)
    overall_analysis: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "service_type": self.service_type,
            "person_a_name": self.person_a_name,
            "person_b_name": self.person_b_name,
            "overall_score": self.overall_score,
            "overall_level": self.overall_level,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "compatibility_highlights": self.compatibility_highlights,
            "compatibility_warnings": self.compatibility_warnings,
            "best_timing": self.best_timing,
            "suggestions": self.suggestions,
            "overall_analysis": self.overall_analysis,
            "confidence": self.confidence,
        }


class MarriageCompatibilityAgent:
    """姻缘配对分析智能体"""

    def __init__(
        self,
        chart_a: Dict[str, Any],    # 甲方命盘
        chart_b: Dict[str, Any],    # 乙方命盘
        name_a: str = "甲方",
        name_b: str = "乙方",
    ):
        """
        初始化姻缘配对

        Args:
            chart_a: 甲方命盘数据
            chart_b: 乙方命盘数据
            name_a: 甲方名称
            name_b: 乙方名称
        """
        self.chart_a = chart_a
        self.chart_b = chart_b
        self.name_a = name_a
        self.name_b = name_b
        self.palaces_a = chart_a.get("palaces", {})
        self.palaces_b = chart_b.get("palaces", {})
        self.transforms_a = chart_a.get("transforms", [])
        self.transforms_b = chart_b.get("transforms", [])

    def _get_main_star(self, palace_name: str) -> Optional[str]:
        """获取宫位主星"""
        palace_a = self.palaces_a.get(palace_name, {})
        palace_b = self.palaces_b.get(palace_name, {})
        return palace_a.get("main_star") or palace_b.get("main_star")

    def _get_palace_stars(self, palace_name: str, which: str = "a") -> List[str]:
        """获取宫位所有星曜"""
        if which == "a":
            palace = self.palaces_a.get(palace_name, {})
        else:
            palace = self.palaces_b.get(palace_name, {})
        stars = palace.get("stars", [])
        # Handle both string and dict formats for stars
        result = []
        for star in stars:
            if isinstance(star, str):
                result.append(star)
            elif isinstance(star, dict) and "name" in star:
                result.append(star["name"])
        return result

    def _get_wuxing(self, star: str) -> Optional[str]:
        """获取星曜五行属性"""
        return STAR_WUXING.get(star)

    def _check_wuxing_relation(self, star_a: Optional[str], star_b: Optional[str]) -> tuple[str, int]:
        """检查两星曜五行关系"""
        if not star_a or not star_b:
            return "无法判断", 0

        wx_a = self._get_wuxing(star_a)
        wx_b = self._get_wuxing(star_b)

        if not wx_a or not wx_b:
            return "无法判断", 0

        # 同五行
        if wx_a == wx_b:
            return "同五行", 20

        # 相生
        if WUXING_SHENG.get(wx_a) == wx_b:
            return "相生", 15
        if WUXING_SHENG.get(wx_b) == wx_a:
            return "相生", 15

        # 相克
        if WUXING_KENG.get(wx_a) == wx_b:
            return "相克", -15
        if WUXING_KENG.get(wx_b) == wx_a:
            return "相克", -15

        return "平和", 5

    def _count_lucky_stars(self, stars: List[str]) -> int:
        """统计吉星数量"""
        return sum(1 for s in stars if s in LUCKY_STARS)

    def _count_malefic_stars(self, stars: List[str]) -> int:
        """统计煞星数量"""
        return sum(1 for s in stars if s in MALIFIC_STARS)

    def _count_peach_blossom(self, stars: List[str]) -> int:
        """统计桃花星数量"""
        return sum(1 for s in stars if s in PEACH_BLOSSOM_STARS)

    def _check_transform_conflict(self, palace_a: str, palace_b: str) -> tuple[bool, List[str]]:
        """检查化忌冲克"""
        conflicts = []

        # 检查甲方化忌是否冲乙方宫位
        for t in self.transforms_a:
            if t.get("type") == "化忌":
                to_palace = t.get("to_palace", "")
                # 如果化忌入乙方命宫或夫妻宫
                if to_palace == palace_b:
                    conflicts.append(f"甲方化忌入{palace_b}")

        # 检查乙方化忌是否冲甲方宫位
        for t in self.transforms_b:
            if t.get("type") == "化忌":
                to_palace = t.get("to_palace", "")
                if to_palace == palace_a:
                    conflicts.append(f"乙方化忌入{palace_a}")

        return len(conflicts) > 0, conflicts

    def _analyze_personality_fit(self) -> CompatibilityDimension:
        """
        分析性格契合度 (25%)

        评估：
        - 命宫主星五行关系
        - 命宫三方四正吉星对比
        - 福德宫对比
        """
        main_star_a = self._get_palace_stars("命宫", "a")
        main_star_b = self._get_palace_stars("命宫", "b")
        fu_de_a = self._get_palace_stars("福德宫", "a")
        fu_de_b = self._get_palace_stars("福德宫", "b")

        score = 50  # 基础分
        positive_factors = []
        negative_factors = []

        # 命宫主星分析
        if main_star_a and main_star_b:
            relation, delta = self._check_wuxing_relation(
                main_star_a[0] if main_star_a else None,
                main_star_b[0] if main_star_b else None
            )

            if relation == "同五行":
                score += 20
                positive_factors.append(f"命宫主星同属{self._get_wuxing(main_star_a[0])}行，志同道合")
            elif relation == "相生":
                score += 15
                positive_factors.append("命宫主星五行相生，性格互补互助")
            elif relation == "相克":
                score += delta
                negative_factors.append("命宫主星五行相克，性格有摩擦")

        # 命宫吉星对比
        lucky_a = self._count_lucky_stars(main_star_a)
        lucky_b = self._count_lucky_stars(main_star_b)
        if lucky_a > 0 and lucky_b > 0:
            common_lucky = min(lucky_a, lucky_b)
            score += common_lucky * 5
            positive_factors.append(f"双方命宫共有{common_lucky}颗吉星")

        # 命宫煞星冲突
        malefic_a = self._count_malefic_stars(main_star_a)
        malefic_b = self._count_malefic_stars(main_star_b)
        if malefic_a > 0 and malefic_b > 0:
            score -= 10
            negative_factors.append("双方命宫皆有煞星，需注意磨合")

        # 福德宫对比
        fu_relation, fu_delta = self._check_wuxing_relation(
            fu_de_a[0] if fu_de_a else None,
            fu_de_b[0] if fu_de_b else None
        )
        if fu_relation in ["同五行", "相生"]:
            score += 10
            positive_factors.append("福德宫精神追求契合")

        # 化忌冲命宫检查
        has_conflict, conflicts = self._check_transform_conflict("命宫", "命宫")
        if has_conflict:
            score -= 20
            negative_factors.extend(conflicts)

        score = normalize_score(score)

        analysis_parts = [
            f"{self.name_a}命宫主星{','.join(main_star_a[:2]) or '空宫'}，"
            f"{self.name_b}命宫主星{','.join(main_star_b[:2]) or '空宫'}。"
        ]
        if positive_factors:
            analysis_parts.append("优势：" + "；".join(positive_factors))
        if negative_factors:
            analysis_parts.append("注意：" + "；".join(negative_factors))

        return CompatibilityDimension(
            dimension="性格契合",
            score=score,
            level=fortune_level_from_score(score),
            analysis="".join(analysis_parts),
            positive_factors=positive_factors,
            negative_factors=negative_factors,
        )

    def _analyze_wealth_complement(self) -> CompatibilityDimension:
        """
        分析财运互补 (20%)

        评估：
        - 财帛宫主星对比
        - 一方财帛宫强 + 另一方官禄宫强 = 互补
        """
        wealth_a = self._get_palace_stars("财帛宫", "a")
        wealth_b = self._get_palace_stars("财帛宫", "b")
        career_a = self._get_palace_stars("官禄宫", "a")
        career_b = self._get_palace_stars("官禄宫", "b")

        score = 50  # 基础分
        positive_factors = []
        negative_factors = []

        # 计算宫位强弱
        def palace_strength(stars: List[str]) -> int:
            return sum(10 for s in stars if s in LUCKY_STARS) - \
                   sum(8 for s in stars if s in MALIFIC_STARS)

        strength_wealth_a = palace_strength(wealth_a)
        strength_wealth_b = palace_strength(wealth_b)
        strength_career_a = palace_strength(career_a)
        strength_career_b = palace_strength(career_b)

        # 财帛宫互补分析
        if strength_wealth_a >= 10 and strength_career_b >= 10:
            score += 25
            positive_factors.append(f"{self.name_a}财帛宫旺+{self.name_b}官禄宫旺，财运事业双丰收")
        if strength_wealth_b >= 10 and strength_career_a >= 10:
            score += 25
            positive_factors.append(f"{self.name_b}财帛宫旺+{self.name_a}官禄宫旺，财运事业双丰收")

        # 双方财帛宫都强
        if strength_wealth_a >= 10 and strength_wealth_b >= 10:
            score += 10
            positive_factors.append("双方财帛宫皆旺，财运基础扎实")

        # 双方财帛宫都弱
        if strength_wealth_a < 0 and strength_wealth_b < 0:
            score -= 10
            negative_factors.append("双方财帛宫皆弱，需注意理财")

        # 财帛宫五行关系
        wealth_relation, _ = self._check_wuxing_relation(
            wealth_a[0] if wealth_a else None,
            wealth_b[0] if wealth_b else None
        )
        if wealth_relation in ["同五行", "相生"]:
            score += 10
            positive_factors.append("财帛宫五行和谐，财运理念相近")

        score = normalize_score(score)

        analysis_parts = [
            f"{self.name_a}财帛宫{','.join(wealth_a[:2]) or '空宫'}，"
            f"{self.name_b}财帛宫{','.join(wealth_b[:2]) or '空宫'}。"
        ]
        if positive_factors:
            analysis_parts.append("优势：" + "；".join(positive_factors))
        if negative_factors:
            analysis_parts.append("注意：" + "；".join(negative_factors))

        return CompatibilityDimension(
            dimension="财运互补",
            score=score,
            level=fortune_level_from_score(score),
            analysis="".join(analysis_parts),
            positive_factors=positive_factors,
            negative_factors=negative_factors,
        )

    def _analyze_career_boost(self) -> CompatibilityDimension:
        """
        分析事业助力 (20%)

        评估：
        - 官禄宫主星对比
        - 迁移宫对比（外地/海外机遇）
        """
        career_a = self._get_palace_stars("官禄宫", "a")
        career_b = self._get_palace_stars("官禄宫", "b")
        migrate_a = self._get_palace_stars("迁移宫", "a")
        migrate_b = self._get_palace_stars("迁移宫", "b")

        score = 50  # 基础分
        positive_factors = []
        negative_factors = []

        # 官禄宫主星分析
        career_relation, delta = self._check_wuxing_relation(
            career_a[0] if career_a else None,
            career_b[0] if career_b else None
        )

        if career_relation == "同五行":
            score += 15
            positive_factors.append("官禄宫主星同五行，事业心志同道合")
        elif career_relation == "相生":
            score += 15
            positive_factors.append("官禄宫主星相生，事业上能互相支持")
        elif career_relation == "相克":
            score += delta
            negative_factors.append("官禄宫主星相克，事业方向有分歧")

        # 事业与财富互补
        wealth_a = self._get_palace_stars("财帛宫", "a")
        wealth_b = self._get_palace_stars("财帛宫", "b")
        lucky_career_a = self._count_lucky_stars(career_a)
        lucky_wealth_b = self._count_lucky_stars(wealth_b)
        if lucky_career_a >= 2 and lucky_wealth_b >= 2:
            score += 20
            positive_factors.append("一方事业强+一方财运旺，完美互补")

        lucky_career_b = self._count_lucky_stars(career_b)
        lucky_wealth_a = self._count_lucky_stars(wealth_a)
        if lucky_career_b >= 2 and lucky_wealth_a >= 2:
            score += 20
            positive_factors.append("一方事业强+一方财运旺，完美互补")

        # 迁移宫对比（外地/海外机遇）
        migrate_relation, _ = self._check_wuxing_relation(
            migrate_a[0] if migrate_a else None,
            migrate_b[0] if migrate_b else None
        )
        if migrate_relation in ["同五行", "相生"]:
            score += 10
            positive_factors.append("迁移宫和谐，外地/海外发展机遇同步")

        # 煞星冲突
        malefic_career_a = self._count_malefic_stars(career_a)
        malefic_career_b = self._count_malefic_stars(career_b)
        if malefic_career_a > 0 and malefic_career_b > 0:
            score -= 10
            negative_factors.append("双方官禄宫皆有煞星，事业竞争压力较大")

        score = normalize_score(score)

        analysis_parts = [
            f"{self.name_a}官禄宫{','.join(career_a[:2]) or '空宫'}，"
            f"{self.name_b}官禄宫{','.join(career_b[:2]) or '空宫'}。"
        ]
        if positive_factors:
            analysis_parts.append("优势：" + "；".join(positive_factors))
        if negative_factors:
            analysis_parts.append("注意：" + "；".join(negative_factors))

        return CompatibilityDimension(
            dimension="事业助力",
            score=score,
            level=fortune_level_from_score(score),
            analysis="".join(analysis_parts),
            positive_factors=positive_factors,
            negative_factors=negative_factors,
        )

    def _analyze_emotional_connection(self) -> CompatibilityDimension:
        """
        分析感情甜蜜度 (25%)

        评估：
        - 夫妻宫星曜对比
        - 桃花星配置
        - 化忌冲夫妻宫
        """
        spouse_a = self._get_palace_stars("夫妻宫", "a")
        spouse_b = self._get_palace_stars("夫妻宫", "b")
        migrate_a = self._get_palace_stars("迁移宫", "a")
        migrate_b = self._get_palace_stars("迁移宫", "b")

        score = 50  # 基础分
        positive_factors = []
        negative_factors = []

        # 夫妻宫主星关系
        spouse_relation, delta = self._check_wuxing_relation(
            spouse_a[0] if spouse_a else None,
            spouse_b[0] if spouse_b else None
        )

        if spouse_relation == "同五行":
            score += 20
            positive_factors.append("夫妻宫主星同五行，感情价值观一致")
        elif spouse_relation == "相生":
            score += 15
            positive_factors.append("夫妻宫主星相生，感情甜蜜互助")
        elif spouse_relation == "相克":
            score += delta
            negative_factors.append("夫妻宫主星相克，感情需多包容")

        # 桃花星配置
        peach_a = self._count_peach_blossom(spouse_a)
        peach_migrate_a = self._count_peach_blossom(migrate_a)
        peach_b = self._count_peach_blossom(spouse_b)
        peach_migrate_b = self._count_peach_blossom(migrate_b)

        if peach_a > 0 and peach_migrate_b > 0:
            score += 15
            positive_factors.append(f"{self.name_a}桃花在夫妻宫，{self.name_b}桃花在迁移宫，异地桃花缘分")
        if peach_b > 0 and peach_migrate_a > 0:
            score += 15
            positive_factors.append(f"{self.name_b}桃花在夫妻宫，{self.name_a}桃花在迁移宫，异地桃花缘分")

        # 夫妻宫桃花都旺
        if peach_a > 0 and peach_b > 0:
            score += 10
            positive_factors.append("双方夫妻宫皆有桃花，感情生活丰富")

        # 化忌冲夫妻宫（严重警告）
        has_conflict, conflicts = self._check_transform_conflict("夫妻宫", "夫妻宫")
        if has_conflict:
            score -= 30
            negative_factors.append("化忌冲夫妻宫，感情需特别注意！")

        # 迁移宫对迁移宫和谐
        migrate_relation, _ = self._check_wuxing_relation(
            migrate_a[0] if migrate_a else None,
            migrate_b[0] if migrate_b else None
        )
        if migrate_relation in ["同五行", "相生"]:
            score += 10
            positive_factors.append("迁移宫对迁移宫和谐，外地/旅行相处愉快")

        # 煞星检查
        malefic_spouse_a = self._count_malefic_stars(spouse_a)
        malefic_spouse_b = self._count_malefic_stars(spouse_b)
        if malefic_spouse_a > 1:
            score -= 10
            negative_factors.append(f"{self.name_a}夫妻宫煞星较多，感情有波折")
        if malefic_spouse_b > 1:
            score -= 10
            negative_factors.append(f"{self.name_b}夫妻宫煞星较多，感情有波折")

        score = normalize_score(score)

        analysis_parts = [
            f"{self.name_a}夫妻宫{','.join(spouse_a[:2]) or '空宫'}，"
            f"{self.name_b}夫妻宫{','.join(spouse_b[:2]) or '空宫'}。"
        ]
        if positive_factors:
            analysis_parts.append("优势：" + "；".join(positive_factors))
        if negative_factors:
            analysis_parts.append("注意：" + "；".join(negative_factors))

        return CompatibilityDimension(
            dimension="感情甜蜜",
            score=score,
            level=fortune_level_from_score(score),
            analysis="".join(analysis_parts),
            positive_factors=positive_factors,
            negative_factors=negative_factors,
        )

    def _analyze_health_sync(self) -> CompatibilityDimension:
        """
        分析健康同步 (10%)

        评估：
        - 疾厄宫主星对比
        - 煞星分布对比
        """
        health_a = self._get_palace_stars("疾厄宫", "a")
        health_b = self._get_palace_stars("疾厄宫", "b")

        score = 50  # 基础分
        positive_factors = []
        negative_factors = []

        # 疾厄宫主星关系
        health_relation, delta = self._check_wuxing_relation(
            health_a[0] if health_a else None,
            health_b[0] if health_b else None
        )

        if health_relation in ["同五行", "相生"]:
            score += 10
            positive_factors.append("疾厄宫五行和谐，健康理念一致")

        # 煞星分布
        malefic_health_a = self._count_malefic_stars(health_a)
        malefic_health_b = self._count_malefic_stars(health_b)

        # 无共同煞星
        stars_a = set(health_a)
        stars_b = set(health_b)
        common_malefic = stars_a & stars_b & set(MALIFIC_STARS)

        if not common_malefic:
            score += 5
            positive_factors.append("疾厄宫无共同煞星，健康风险分散")
        else:
            score -= 10
            negative_factors.append(f"疾厄宫共有煞星：{','.join(common_malefic)}")

        # 疾厄宫过弱
        if malefic_health_a >= 3:
            score -= 10
            negative_factors.append(f"{self.name_a}疾厄宫煞星较多，需注意健康")
        if malefic_health_b >= 3:
            score -= 10
            negative_factors.append(f"{self.name_b}疾厄宫煞星较多，需注意健康")

        score = normalize_score(score)

        analysis_parts = [
            f"{self.name_a}疾厄宫{','.join(health_a[:2]) or '空宫'}，"
            f"{self.name_b}疾厄宫{','.join(health_b[:2]) or '空宫'}。"
        ]
        if positive_factors:
            analysis_parts.append("优势：" + "；".join(positive_factors))
        if negative_factors:
            analysis_parts.append("注意：" + "；".join(negative_factors))

        return CompatibilityDimension(
            dimension="健康同步",
            score=score,
            level=fortune_level_from_score(score),
            analysis="".join(analysis_parts),
            positive_factors=positive_factors,
            negative_factors=negative_factors,
        )

    def _check_harmful_combinations(self) -> List[str]:
        """
        检查有害组合

        检测：
        - 命宫冲克
        - 忌星互冲
        - 凶格对冲
        """
        warnings = []

        # 命宫冲克检查
        mings_a = self._get_palace_stars("命宫", "a")
        mings_b = self._get_palace_stars("命宫", "b")

        # 煞星互冲
        malefic_a = [s for s in mings_a if s in MALIFIC_STARS]
        malefic_b = [s for s in mings_b if s in MALIFIC_STARS]

        if len(malefic_a) >= 2 and len(malefic_b) >= 2:
            warnings.append("双方命宫煞星均较多，性格冲突风险较高")

        # 化忌互冲检查
        ji_in_a_b = False
        ji_in_b_a = False

        for t in self.transforms_a:
            if t.get("type") == "化忌" and t.get("to_palace") == "命宫":
                ji_in_a_b = True
        for t in self.transforms_b:
            if t.get("type") == "化忌" and t.get("to_palace") == "命宫":
                ji_in_b_a = True

        if ji_in_a_b and ji_in_b_a:
            warnings.append("化忌互冲命宫，需特别注意沟通方式")

        # 夫妻宫双忌检查
        spouse_ji_a = any(
            t.get("type") == "化忌" and t.get("to_palace") == "夫妻宫"
            for t in self.transforms_a
        )
        spouse_ji_b = any(
            t.get("type") == "化忌" and t.get("to_palace") == "夫妻宫"
            for t in self.transforms_b
        )

        if spouse_ji_a and spouse_ji_b:
            warnings.append("化忌互冲夫妻宫，婚姻需用心经营")

        # 财帛宫双忌
        wealth_ji_a = any(
            t.get("type") == "化忌" and t.get("to_palace") == "财帛宫"
            for t in self.transforms_a
        )
        wealth_ji_b = any(
            t.get("type") == "化忌" and t.get("to_palace") == "财帛宫"
            for t in self.transforms_b
        )

        if wealth_ji_a and wealth_ji_b:
            warnings.append("化忌互冲财帛宫，财务需分开管理")

        return warnings

    def _analyze_fate_sync(self) -> tuple[str, List[str]]:
        """
        分析大运同步性

        分析两人大运起落是否同步，返回最佳时机和建议
        """
        suggestions = []

        # 获取大运信息（如果有）
        dayun_a = self.chart_a.get("dayun", [])
        dayun_b = self.chart_b.get("dayun", [])

        best_timing = "两人大运各有优劣，建议相互扶持"

        if dayun_a and dayun_b:
            # 简单的同步性检查
            try:
                # 假设大运有 start_year 和运气等级
                luck_a = dayun_a[0].get("luck_level", "average") if dayun_a else "average"
                luck_b = dayun_b[0].get("luck_level", "average") if dayun_b else "average"

                if luck_a == luck_b:
                    best_timing = "当前大运同步，可考虑订婚或结婚"
                    suggestions.append("当前大运同步，是感情升华的好时机")
                else:
                    best_timing = "大运错位，待同步时再考虑结婚"
                    suggestions.append("建议等待大运同步后再考虑结婚大事")
            except (IndexError, KeyError):
                pass

        # 基于五行分析建议
        ming_a = self._get_palace_stars("命宫", "a")
        ming_b = self._get_palace_stars("命宫", "b")

        if ming_a and ming_b:
            wx_a = self._get_wuxing(ming_a[0])
            wx_b = self._get_wuxing(ming_b[0])

            if wx_a and wx_b:
                if wx_a == wx_b:
                    suggestions.append("命格相同，相处默契，但需注意保持独立空间")
                elif WUXING_SHENG.get(wx_a) == wx_b:
                    suggestions.append(f"{wx_a}命格生助{wx_b}命格，一方需多付出")
                elif WUXING_SHENG.get(wx_b) == wx_a:
                    suggestions.append(f"{wx_b}命格生助{wx_a}命格，另一方需多付出")

        return best_timing, suggestions

    def _calculate_overall_score(
        self,
        dimensions: List[CompatibilityDimension]
    ) -> float:
        """
        计算综合分数

        权重配置：
        - 性格契合: 25%
        - 财运互补: 20%
        - 事业助力: 20%
        - 感情甜蜜: 25%
        - 健康同步: 10%
        """
        weights = {
            "性格契合": 0.25,
            "财运互补": 0.2,
            "事业助力": 0.2,
            "感情甜蜜": 0.25,
            "健康同步": 0.1,
        }

        weighted_sum = sum(
            d.score * weights.get(d.dimension, 0.2)
            for d in dimensions
        )

        return min(100.0, max(0.0, weighted_sum))

    def _generate_highlights(
        self,
        dimensions: List[CompatibilityDimension]
    ) -> List[str]:
        """生成配对亮点"""
        highlights = []

        for d in dimensions:
            if d.score >= 80:
                highlights.append(f"{d.dimension}极佳：{d.analysis[:50]}...")

        return highlights[:3]  # 最多3个亮点

    def _generate_suggestions(
        self,
        dimensions: List[CompatibilityDimension],
        warnings: List[str]
    ) -> List[str]:
        """生成建议"""
        suggestions = []

        # 基于维度分数的建议
        for d in dimensions:
            if d.score < 50:
                if d.dimension == "性格契合":
                    suggestions.append("性格差异较大，建议多沟通、互相包容")
                elif d.dimension == "财运互补":
                    suggestions.append("财运配置不同，建议财务分开管理，共同投资需谨慎")
                elif d.dimension == "事业助力":
                    suggestions.append("事业方向不同，建议尊重对方职业选择")
                elif d.dimension == "感情甜蜜":
                    suggestions.append("感情基础需加强，建议多创造二人空间")
                elif d.dimension == "健康同步":
                    suggestions.append("健康关注点不同，建议互相提醒定期体检")

        # 基于警告的建议
        for w in warnings:
            if "化忌冲" in w:
                suggestions.append("存在化忌冲宫，需特别注意该宫位相关事务的沟通")
            if "煞星" in w:
                suggestions.append("煞星较多，需注意该方面风险防范")

        # 通用建议
        suggestions.append("无论配对结果如何，相互尊重和沟通是感情的基础")

        return list(dict.fromkeys(suggestions))  # 去重保持顺序

    def analyze(self) -> CompatibilityResult:
        """
        执行完整分析

        Returns:
            CompatibilityResult: 包含所有分析结果的完整报告
        """
        # 1. 分析各维度
        dimension_personality = self._analyze_personality_fit()
        dimension_wealth = self._analyze_wealth_complement()
        dimension_career = self._analyze_career_boost()
        dimension_emotional = self._analyze_emotional_connection()
        dimension_health = self._analyze_health_sync()

        dimensions = [
            dimension_personality,
            dimension_wealth,
            dimension_career,
            dimension_emotional,
            dimension_health,
        ]

        # 2. 计算综合分数
        overall_score = self._calculate_overall_score(dimensions)

        # 3. 确定综合等级
        if overall_score >= 90:
            overall_level = CompatibilityLevel.PERFECT.value
        elif overall_score >= 80:
            overall_level = CompatibilityLevel.EXCELLENT.value
        elif overall_score >= 70:
            overall_level = CompatibilityLevel.GOOD.value
        elif overall_score >= 50:
            overall_level = CompatibilityLevel.AVERAGE.value
        elif overall_score >= 30:
            overall_level = CompatibilityLevel.FAIR.value
        else:
            overall_level = CompatibilityLevel.CHALLENGING.value

        # 4. 检查有害组合
        warnings = self._check_harmful_combinations()

        # 5. 分析大运同步性
        best_timing, timing_suggestions = self._analyze_fate_sync()

        # 6. 生成亮点和警告
        highlights = self._generate_highlights(dimensions)
        warnings.extend(self._check_harmful_combinations())

        # 7. 生成建议
        suggestions = self._generate_suggestions(dimensions, warnings)
        suggestions.extend(timing_suggestions)

        # 8. 生成综合分析
        overall_analysis = (
            f"{self.name_a}与{self.name_b}的姻缘配对分析完成。"
            f"综合配对指数{overall_score:.1f}分，等级{overall_level}。"
            f"性格契合度{dimension_personality.score:.1f}分，"
            f"财运互补{dimension_wealth.score:.1f}分，"
            f"事业助力{dimension_career.score:.1f}分，"
            f"感情甜蜜度{dimension_emotional.score:.1f}分，"
            f"健康同步性{dimension_health.score:.1f}分。"
        )

        # 9. 计算置信度
        # 基于数据完整度
        confidence = 0.5  # 基础置信度

        # 命盘数据完整
        if len(self.palaces_a) >= 10 and len(self.palaces_b) >= 10:
            confidence += 0.2

        # 有四化数据
        if self.transforms_a and self.transforms_b:
            confidence += 0.15

        # 数据完整度高
        if len(self.palaces_a) >= 12 and len(self.palaces_b) >= 12:
            confidence += 0.15

        return CompatibilityResult(
            service_type="marriage_compatibility",
            person_a_name=self.name_a,
            person_b_name=self.name_b,
            overall_score=overall_score,
            overall_level=overall_level,
            dimensions=dimensions,
            compatibility_highlights=highlights,
            compatibility_warnings=warnings,
            best_timing=best_timing,
            suggestions=suggestions,
            overall_analysis=overall_analysis,
            confidence=min(1.0, confidence),
        )


def analyze_marriage_compatibility_sync(
    chart_a: Dict[str, Any],
    chart_b: Dict[str, Any],
    name_a: str = "甲方",
    name_b: str = "乙方",
) -> CompatibilityResult:
    """
    同步便捷函数 - 分析姻缘配对

    Args:
        chart_a: 甲方命盘数据
        chart_b: 乙方命盘数据
        name_a: 甲方名称
        name_b: 乙方名称

    Returns:
        CompatibilityResult: 配对分析结果

    Example:
        >>> chart_a = {"palaces": {...}, "transforms": [...]}
        >>> chart_b = {"palaces": {...}, "transforms": [...]}
        >>> result = analyze_marriage_compatibility_sync(chart_a, chart_b, "张三", "李四")
        >>> print(result.overall_score)
    """
    agent = MarriageCompatibilityAgent(
        chart_a=chart_a,
        chart_b=chart_b,
        name_a=name_a,
        name_b=name_b,
    )
    return agent.analyze()


# ============ LLM增强姻缘配对分析 ============

class LLMMarriageCompatibilityAnalyzer:
    """LLM姻缘配对增强器"""

    def __init__(self, chart_a: Dict[str, Any], chart_b: Dict[str, Any],
                 name_a: str = "甲方", name_b: str = "乙方"):
        """
        初始化LLM姻缘配对增强器

        Args:
            chart_a: 甲方命盘数据
            chart_b: 乙方命盘数据
            name_a: 甲方名称
            name_b: 乙方名称
        """
        self.chart_a = chart_a
        self.chart_b = chart_b
        self.name_a = name_a
        self.name_b = name_b
        self.base_analyzer = MarriageCompatibilityAgent(
            chart_a=chart_a,
            chart_b=chart_b,
            name_a=name_a,
            name_b=name_b,
        )

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度姻缘配对分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            LLM分析结果
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import build_marriage_compat_user_prompt, MARRIAGE_COMPAT_SYSTEM_PROMPT

        # 先获取基础分析
        base_result = self.base_analyzer.analyze()

        # 构建提示词
        user_prompt = build_marriage_compat_user_prompt(
            chart_a=self.chart_a,
            chart_b=self.chart_b,
            compatibility_result=base_result.to_dict(),
            name_a=self.name_a,
            name_b=self.name_b,
            question=question,
        )

        messages = [
            {"role": "system", "content": MARRIAGE_COMPAT_SYSTEM_PROMPT},
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


async def llm_analyze_marriage_compatibility(
    chart_a: Dict[str, Any],
    chart_b: Dict[str, Any],
    name_a: str = "甲方",
    name_b: str = "乙方",
    question: Optional[str] = None,
) -> Dict[str, Any]:
    """
    异步LLM姻缘配对分析

    Args:
        chart_a: 甲方命盘数据
        chart_b: 乙方命盘数据
        name_a: 甲方名称
        name_b: 乙方名称
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLMMarriageCompatibilityAnalyzer(
        chart_a=chart_a,
        chart_b=chart_b,
        name_a=name_a,
        name_b=name_b,
    )
    return await analyzer.analyze_with_llm(question)


def llm_analyze_marriage_compatibility_sync(
    chart_a: Dict[str, Any],
    chart_b: Dict[str, Any],
    name_a: str = "甲方",
    name_b: str = "乙方",
    question: Optional[str] = None,
) -> Dict[str, Any]:
    """
    同步LLM姻缘配对分析

    Args:
        chart_a: 甲方命盘数据
        chart_b: 乙方命盘数据
        name_a: 甲方名称
        name_b: 乙方名称
        question: 可选的特定问题

    Returns:
        LLM分析结果

    Example:
        >>> chart_a = {"palaces": {...}, "transforms": [...]}
        >>> chart_b = {"palaces": {...}, "transforms": [...]}
        >>> result = llm_analyze_marriage_compatibility_sync(
        ...     chart_a, chart_b, "张三", "李四",
        ...     question="我们适合结婚吗？"
        ... )
        >>> print(result.get("overall_assessment"))
    """
    import asyncio
    return asyncio.run(llm_analyze_marriage_compatibility(
        chart_a=chart_a,
        chart_b=chart_b,
        name_a=name_a,
        name_b=name_b,
        question=question,
    ))
