"""
SynthesisAgent - 综合分析代理

负责汇总所有分析结果，生成完整的命盘解读报告
- 聚合各agent的分析结果
- 解决冲突观点
- 生成综合建议
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


# ============ Data Models ============

class AnalysisPriority(str, Enum):
    """分析优先级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class AgentResult:
    """各agent的分析结果"""
    agent_name: str          # agent名称
    content: str            # 分析内容
    priority: AnalysisPriority = AnalysisPriority.MEDIUM
    confidence: float = 0.8  # 置信度 0-1
    conflicts_with: List[str] = field(default_factory=list)  # 与哪些agent有冲突


@dataclass
class StarAnalysis:
    """星曜分析结果"""
    main_stars: List[str]           # 主星
    assistant_stars: List[str]       # 辅星
    marginal_stars: List[str]        # 杂曜
    transforming_stars: List[str]   # 四化星
    key_observations: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class PalaceAnalysis:
    """宫位分析结果"""
    palace_strengths: Dict[str, float] = field(default_factory=dict)  # 宫位强弱
    key_palaces: Dict[str, str] = field(default_factory=dict)  # 关键宫位
    observations: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class PatternAnalysis:
    """格局分析结果"""
    major_patterns: List[str] = field(default_factory=list)
    minor_patterns: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class TransformAnalysis:
    """四化分析结果"""
    original_transforms: Dict[str, str] = field(default_factory=dict)  # 原局四化
    current_transforms: Dict[str, str] = field(default_factory=dict)  # 运限四化
    observations: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class TimingAnalysis:
    """时机分析结果(简化版)"""
    current_period: str = ""
    year_fate: str = ""
    key_timing: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class SynthesisReport:
    """综合报告"""
    # 基础信息
    chart_overview: str = ""
    birth_info: Dict[str, Any] = field(default_factory=dict)

    # 各维度分析
    star_analysis: StarAnalysis = field(default_factory=lambda: StarAnalysis([], [], [], []))
    palace_analysis: PalaceAnalysis = field(default_factory=lambda: PalaceAnalysis("", "", ""))
    pattern_analysis: PatternAnalysis = field(default_factory=lambda: PatternAnalysis("", []))
    transform_analysis: TransformAnalysis = field(default_factory=lambda: TransformAnalysis([]))
    timing_analysis: TimingAnalysis = field(default_factory=lambda: TimingAnalysis([]))

    # 综合结论
    overall_assessment: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # 冲突解决
    conflict_resolutions: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chart_overview": self.chart_overview,
            "birth_info": self.birth_info,
            "star_analysis": {
                "main_stars": self.star_analysis.main_stars,
                "assistant_stars": self.star_analysis.assistant_stars,
                "marginal_stars": self.star_analysis.marginal_stars,
                "transforming_stars": self.star_analysis.transforming_stars,
                "key_observations": self.star_analysis.key_observations,
                "summary": self.star_analysis.summary
            },
            "palace_analysis": {
                "palace_strengths": self.palace_analysis.palace_strengths,
                "key_palaces": self.palace_analysis.key_palaces,
                "observations": self.palace_analysis.observations,
                "summary": self.palace_analysis.summary
            },
            "pattern_analysis": {
                "major_patterns": self.pattern_analysis.major_patterns,
                "minor_patterns": self.pattern_analysis.minor_patterns,
                "observations": self.pattern_analysis.observations,
                "summary": self.pattern_analysis.summary
            },
            "transform_analysis": {
                "original_transforms": self.transform_analysis.original_transforms,
                "current_transforms": self.transform_analysis.current_transforms,
                "observations": self.transform_analysis.observations,
                "summary": self.transform_analysis.summary
            },
            "timing_analysis": {
                "current_period": self.timing_analysis.current_period,
                "year_fate": self.timing_analysis.year_fate,
                "key_timing": self.timing_analysis.key_timing,
                "observations": self.timing_analysis.observations,
                "summary": self.timing_analysis.summary
            },
            "overall_assessment": self.overall_assessment,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "conflict_resolutions": self.conflict_resolutions
        }


# ============ Conflict Resolution Rules ============

class ConflictType(Enum):
    """冲突类型枚举"""
    REAL_CONFLICT = "real_conflict"           # 真正的冲突（性质相反且影响同一事务）
    TRANSFORMABLE = "transformable"            # 可转化类型（某些凶格在特定条件下可解）
    FALSE_POSITIVE = "false_positive"         # 误判（看起来冲突但实际不冲突）
    COMPLEMENTARY = "complementary"           # 互补关系（一方描述细节另一方描述全局）
    NO_CONFLICT = "no_conflict"               # 无冲突


class ConflictResolver:
    """冲突解决器 - 增强版

    增强的冲突检测逻辑：
    1. 考虑宫位特性（如财帛宫和官禄宫的关系）
    2. 考虑星曜组合（如桃花星+煞星=特定含义）
    3. 考虑四化影响（化禄/化权/化科/化忌的相互作用）
    4. 考虑主星与辅星的优先级
    5. 识别"可转化"类型的冲突
    """

    # 优先级规则：主星 > 辅星 > 杂曜
    # 时机：运限 > 原局
    # 四化：化忌 > 化禄/化权/化科

    PRIORITY_RULES = {
        "星曜级别": {
            "正曜": 3,
            "副曜": 2,
            "杂曜": 1
        },
        "四化级别": {
            "化忌": 4,
            "化权": 3,
            "化科": 2,
            "化禄": 2
        },
        "时机": {
            "运限": 2,
            "原局": 1
        }
    }

    # 宫位关系图：哪些宫位相互影响
    PALACE_RELATIONS = {
        "财帛宫": {"related": ["命宫", "官禄宫", "福德宫"], "opposes": ["田宅宫"]},
        "官禄宫": {"related": ["命宫", "财帛宫", "迁移宫"], "opposes": ["兄弟宫"]},
        "命宫": {"related": ["财帛宫", "官禄宫", "迁移宫"], "opposes": ["福德宫"]},
        "夫妻宫": {"related": ["官禄宫", "迁移宫", "福德宫"], "opposes": ["田宅宫"]},
        "迁移宫": {"related": ["命宫", "官禄宫", "仆役宫"], "opposes": ["命宫"]},
        "福德宫": {"related": ["命宫", "夫妻宫", "田宅宫"], "opposes": ["命宫"]},
    }

    # 星曜分类：决定优先级
    STAR_CATEGORIES = {
        "main_stars": ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"],
        "assistant_stars": ["左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马"],
        "transforming_stars": ["化禄", "化权", "化科", "化忌"],
        "flower_stars": ["红鸾", "天喜", "咸池", "海棠"],
        "sha_stars": ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"],
    }

    # 四化相互作用的规则
    TRANSFORM_INTERACTIONS = {
        ("化禄", "化忌"): "相悖",    # 化禄增加vs化忌减少
        ("化权", "化忌"): "相悖",    # 强势vs阻碍
        ("化科", "化忌"): "相悖",    # 名声vs阻碍
        ("化禄", "化权"): "相助",    # 财权双美
        ("化禄", "化科"): "相助",    # 财名双美
        ("化权", "化科"): "相助",    # 权名双美
    }

    # 可转化凶格规则
    TRANSFORMABLE_PATTERNS = [
        # (凶格特征, 转化条件, 转化结果)
        ("桃花星.*煞星", "有化禄或化权", "桃花煞变桃花贵"),
        ("煞星.*桃花星", "有化科或左辅右弼", "煞星被制化"),
        ("化忌.*破军", "有化禄或禄存", "破财可解"),
        ("空亡.*星曜", "有天乙贵人或天马", "凶中带吉"),
        ("陀罗.*火星", "有天梁或天寿", "擎羊夹忌可解"),
    ]

    @classmethod
    def resolve(cls, results: List[AgentResult]) -> str:
        """
        解决多个agent结果之间的冲突

        Args:
            results: 各agent的分析结果

        Returns:
            解决后的结论
        """
        if len(results) <= 1:
            return results[0].content if results else ""

        # 按优先级排序
        sorted_results = sorted(results, key=lambda r: (
            cls._get_priority_score(r),
            r.confidence
        ), reverse=True)

        # 最高优先级的结论
        primary = sorted_results[0]

        # 检查是否有冲突
        conflicts = []
        for r in sorted_results[1:]:
            conflict_info = cls._analyze_conflict_detailed(primary.content, r.content)
            if conflict_info["has_conflict"]:
                conflicts.append({
                    "agent1": primary.agent_name,
                    "agent2": r.agent_name,
                    "conflict_type": conflict_info["type"].value,
                    "resolution": cls._resolve_conflict_detailed(primary, r, conflict_info)
                })

        return primary.content

    @classmethod
    def _get_priority_score(cls, result: AgentResult) -> float:
        """计算结果优先级分数"""
        priority_scores = {
            AnalysisPriority.HIGH: 3.0,
            AnalysisPriority.MEDIUM: 2.0,
            AnalysisPriority.LOW: 1.0
        }
        return priority_scores.get(result.priority, 2.0) * result.confidence

    @classmethod
    def _analyze_sentiment(cls, content: str) -> Dict[str, Any]:
        """
        深度情感分析，考虑语境

        Returns:
            {
                "has_positive": bool,
                "has_negative": bool,
                "positive_score": float,  # 0-1
                "negative_score": float,   # 0-1
                "sentiment_phrases": [("吉", True), ...],  # 发现的具体词语及极性
                "modifiers": ["总体", "但", "有小凶"],  # 修饰词
                "certainty": "高/中/低",  # 确定程度
                "integrated_score": float,  # 综合评分
                "context_pattern": str,  # 语境模式
            }
        """
        import re

        # ============ 紫微斗数专业词汇 ============
        # 吉兆词（确定性高）
        strong_positive = [
            "大吉", "特吉", "富贵", "荣华", "兴旺发达", "飞黄腾达",
            "旺", "爆发", "飞升", "发达", "大发", "贵", "福", "禄",
            "天厨", "天魁", "天钺", "左辅", "右弼", "文昌", "文曲",
            "紫微", "天府", "太阴", "太阳", "禄存", "天马"
        ]
        # 弱正面词（可能被修饰）
        weak_positive = [
            "吉", "好", "利", "顺", "发", "旺", "喜", "庆",
            "得", "有", "助", "帮"
        ]
        # 凶兆词（确定性高）
        strong_negative = [
            "大凶", "特凶", "衰败", "破败", "大败", "血光", "死亡",
            "离散", "孤独", "夭折", "绝", "亡", "煞", "凶",
            "劫", "灾", "难", "祸", "伤", "杀", "七杀", "破军"
        ]
        # 弱负面词
        weak_negative = [
            "凶", "坏", "衰", "不利", "不顺", "败", "差", "难",
            "阻", "滞", "困", "危", "忧", "患"
        ]
        # 中性词
        neutral_words = ["平常", "中等", "普通", "一般", "平", "稳", "安"]

        # ============ 修饰词权重 ============
        modifier_weights = {
            # 转折类（改变情感方向）
            "但": -0.3,
            "不过": -0.2,
            "却": -0.3,
            "然而": -0.25,
            "可惜": -0.25,
            # 让步类
            "虽然": -0.15,
            "尽管": -0.15,
            "虽然说": -0.15,
            # 弱化类
            "略有": -0.1,
            "稍有": -0.1,
            "基本": -0.1,
            "略微": -0.1,
            # 强化类
            "总体": +0.15,
            "整体": +0.15,
            "总的来说": +0.2,
            "整体来看": +0.2,
            "总体而言": +0.2,
            # 否定反转类
            "并非": -0.2,
            "不是": -0.1,
        }

        # ============ 语境模式识别 ============
        # 转折模式
        transition_patterns = [
            (r"先吉后凶", "negative"),  # 先好后坏
            (r"先凶后吉", "positive"),  # 先坏后好
            (r"先好后坏", "negative"),
            (r"先坏后好", "positive"),
            (r"由吉转凶", "negative"),
            (r"由凶转吉", "positive"),
        ]
        # 转化模式
        transform_patterns = [
            (r"假凶真吉", "positive"),  # 表面凶实际吉
            (r"假吉真凶", "negative"),  # 表面吉实际凶
            (r"凶中有吉", "positive"),   # 凶中有好的成分
            (r"吉中有凶", "negative"),   # 吉中有坏的成分
            (r"忌中有禄", "positive"),   # 忌中带禄
            (r"禄中有忌", "negative"),   # 禄中带忌
            (r"逢凶化吉", "positive"),   # 凶转吉
            (r"化险为夷", "positive"),   # 危险转安全
        ]

        result = {
            "has_positive": False,
            "has_negative": False,
            "positive_score": 0.0,
            "negative_score": 0.0,
            "sentiment_phrases": [],
            "modifiers": [],
            "certainty": "高",
            "integrated_score": 0.0,
            "context_pattern": "normal",
        }

        # ============ 1. 语境模式检测（优先级最高） ============
        detected_context = []
        for pattern, sentiment in transition_patterns + transform_patterns:
            if re.search(pattern, content):
                detected_context.append((pattern, sentiment))
                result["context_pattern"] = pattern

        # ============ 2. 修饰词检测与权重计算 ============
        found_modifiers = {}
        for modifier, weight in modifier_weights.items():
            if modifier in content:
                found_modifiers[modifier] = weight

        result["modifiers"] = list(found_modifiers.keys())

        # 确定性判断
        if any(w < 0 for w in found_modifiers.values()):
            result["certainty"] = "中"
        if any(abs(w) >= 0.3 for w in found_modifiers.values()):
            result["certainty"] = "高"

        # ============ 3. 词汇匹配与评分 ============
        for word in strong_positive:
            if word in content:
                result["sentiment_phrases"].append((word, True))
                result["positive_score"] += 0.4
                result["has_positive"] = True

        for word in weak_positive:
            if word in content:
                result["sentiment_phrases"].append((word, True))
                result["positive_score"] += 0.2
                result["has_positive"] = True

        for word in strong_negative:
            if word in content:
                result["sentiment_phrases"].append((word, False))
                result["negative_score"] += 0.4
                result["has_negative"] = True

        for word in weak_negative:
            if word in content:
                result["sentiment_phrases"].append((word, False))
                result["negative_score"] += 0.2
                result["has_negative"] = True

        for word in neutral_words:
            if word in content:
                result["sentiment_phrases"].append((word, None))  # None表示中性
                # 中性词不影响分数，但表明内容描述平淡

        # ============ 4. 语境模式影响评分 ============
        context_multiplier = 1.0
        if detected_context:
            for _, sentiment in detected_context:
                if sentiment == "positive":
                    context_multiplier *= 1.2  # 正面转化增强
                else:
                    context_multiplier *= 0.8  # 负面转化减弱

        # ============ 5. 修饰词权重影响评分 ============
        modifier_sum = sum(found_modifiers.values())

        # ============ 6. 归一化 ============
        result["positive_score"] = min(1.0, result["positive_score"])
        result["negative_score"] = min(1.0, result["negative_score"])

        # ============ 7. 计算综合评分 ============
        base_score = result["positive_score"] - result["negative_score"]
        certainty_factor = {"高": 1.0, "中": 0.8, "低": 0.6}.get(result["certainty"], 1.0)

        result["integrated_score"] = cls._calculate_integrated_score(
            base_score=base_score,
            context_multiplier=context_multiplier,
            certainty_factor=certainty_factor,
            modifier_sum=modifier_sum,
        )

        return result

    @classmethod
    def _calculate_integrated_score(
        cls,
        base_score: float,
        context_multiplier: float,
        certainty_factor: float,
        modifier_sum: float,
    ) -> float:
        """
        综合评分计算

        综合评分 = 基础分 * 语境系数 * 确定性系数 + 修饰词调整

        Args:
            base_score: 基础分 (-1 到 1)
            context_multiplier: 语境系数 (通常 0.8-1.2)
            certainty_factor: 确定性系数 (0.6-1.0)
            modifier_sum: 修饰词权重和

        Returns:
            综合评分 (-1 到 1)
        """
        # 基础分 * 语境系数 * 确定性系数
        score = base_score * context_multiplier * certainty_factor
        # 加上修饰词调整
        score += modifier_sum
        # 限制在 [-1, 1] 范围内
        return max(-1.0, min(1.0, score))

    @classmethod
    def _analyze_conflict_detailed(cls, content1: str, content2: str) -> Dict[str, Any]:
        """
        详细分析两段内容之间的冲突关系

        Returns:
            {
                "has_conflict": bool,
                "type": ConflictType,
                "confidence": float,  # 判断置信度
                "reason": str,  # 判断理由
                "details": {}  # 详细分析数据
            }
        """
        import re

        sentiment1 = cls._analyze_sentiment(content1)
        sentiment2 = cls._analyze_sentiment(content2)

        # 1. 检查误判情况（一方描述全局，一方描述细节）
        # 例如："总体吉利但有小凶" vs "有小凶"
        if sentiment1["certainty"] == "中" and sentiment2["certainty"] == "高":
            # content1可能是全面描述，content2是单一焦点
            if sentiment1["has_positive"] and sentiment1["has_negative"]:
                # content1有混合情感，可能是全面评价
                if sentiment2["has_negative"] and not sentiment2["has_positive"]:
                    return {
                        "has_conflict": False,
                        "type": ConflictType.COMPLEMENTARY,
                        "confidence": 0.8,
                        "reason": "content1是整体评价(含优缺点的全面描述)，content2是单一焦点分析",
                        "details": {"sentiment1": sentiment1, "sentiment2": sentiment2}
                    }

        # 2. 检查"可转化"模式
        # 某些凶格在特定条件下可以转化
        transformable_match = cls._check_transformable_pattern(content1, content2)
        if transformable_match:
            return transformable_match

        # 3. 检查真正的冲突
        # 真正冲突条件：
        # - content1全正(高确定性) vs content2全负(高确定性)
        # - 或者两者的情感极性截然相反
        if sentiment1["certainty"] == "高" and sentiment2["certainty"] == "高":
            # 双重检查：不仅看有没有正负，还要看强度
            pos1, neg1 = sentiment1["positive_score"], sentiment1["negative_score"]
            pos2, neg2 = sentiment2["positive_score"], sentiment2["negative_score"]

            # 计算情感方向
            direction1 = pos1 - neg1  # 正数偏正，负数偏负
            direction2 = pos2 - neg2

            # 方向相反且强度都较高
            if direction1 > 0.3 and direction2 < -0.3:
                # 检查是否是同一事务的影响
                if cls._is_same_domain_conflict(content1, content2):
                    return {
                        "has_conflict": True,
                        "type": ConflictType.REAL_CONFLICT,
                        "confidence": 0.9,
                        "reason": "两个分析对同一事务给出截然相反的判断，且确定性都高",
                        "details": {"sentiment1": sentiment1, "sentiment2": sentiment2, "direction1": direction1, "direction2": direction2}
                    }
            elif direction1 < -0.3 and direction2 > 0.3:
                if cls._is_same_domain_conflict(content1, content2):
                    return {
                        "has_conflict": True,
                        "type": ConflictType.REAL_CONFLICT,
                        "confidence": 0.9,
                        "reason": "两个分析对同一事务给出截然相反的判断，且确定性都高",
                        "details": {"sentiment1": sentiment1, "sentiment2": sentiment2, "direction1": direction1, "direction2": direction2}
                    }

        # 4. 检查是否有修饰词导致的"假冲突"
        # "总体吉利" + "有小凶" 不是冲突
        if sentiment1["has_positive"] and sentiment1["has_negative"]:
            if sentiment2["has_negative"]:
                return {
                    "has_conflict": False,
                    "type": ConflictType.FALSE_POSITIVE,
                    "confidence": 0.85,
                    "reason": "content1已包含正负两方面评价，content2的负面观点已被涵盖",
                    "details": {"sentiment1": sentiment1, "sentiment2": sentiment2}
                }

        if sentiment2["has_positive"] and sentiment2["has_negative"]:
            if sentiment1["has_negative"]:
                return {
                    "has_conflict": False,
                    "type": ConflictType.FALSE_POSITIVE,
                    "confidence": 0.85,
                    "reason": "content2已包含正负两方面评价，content1的负面观点已被涵盖",
                    "details": {"sentiment1": sentiment1, "sentiment2": sentiment2}
                }

        return {
            "has_conflict": False,
            "type": ConflictType.NO_CONFLICT,
            "confidence": 0.7,
            "reason": "未检测到明显的冲突关系",
            "details": {"sentiment1": sentiment1, "sentiment2": sentiment2}
        }

    @classmethod
    def _check_transformable_pattern(cls, content1: str, content2: str) -> Optional[Dict[str, Any]]:
        """
        检查是否符合可转化的凶格模式

        Returns:
            如果匹配到可转化模式，返回详细分析；否则返回None
        """
        import re

        # 检查content1中是否有凶格，content2中是否有转化条件
        for pattern, condition, result in cls.TRANSFORMABLE_PATTERNS:
            # 检查凶格模式
            has_malefice = re.search(pattern, content1) or re.search(pattern, content2)
            # 检查转化条件
            has_transform_condition = condition in content1 or condition in content2

            if has_malefice and has_transform_condition:
                return {
                    "has_conflict": False,
                    "type": ConflictType.TRANSFORMABLE,
                    "confidence": 0.75,
                    "reason": f"检测到凶格但存在转化条件({condition})，可转化为{result}",
                    "details": {"malefice_pattern": pattern, "transform_condition": condition, "transform_result": result}
                }

        return None

    @classmethod
    def _is_same_domain_conflict(cls, content1: str, content2: str) -> bool:
        """
        判断两个内容是否针对同一领域/事务的冲突
        """
        # 提取关键领域词
        domains = {
            "事业": ["事业", "工作", "官禄", "职业", "创业", "升迁"],
            "财运": ["财运", "财富", "金钱", "财帛", "投资", "理财", "破财", "发财"],
            "感情": ["感情", "婚姻", "夫妻", "桃花", "恋爱", "配偶"],
            "健康": ["健康", "疾病", "身体", "体检", "寿命"],
            "迁移": ["迁移", "外出", "旅行", "搬迁", "远行"],
        }

        def extract_domains(content: str) -> set:
            found = set()
            for domain, keywords in domains.items():
                if any(kw in content for kw in keywords):
                    found.add(domain)
            return found

        domains1 = extract_domains(content1)
        domains2 = extract_domains(content2)

        # 如果有共同领域，可能是同一事务的冲突
        if domains1 & domains2:
            return True

        # 如果都没有提取到领域关键词，保守假设可能是同一事务
        if not domains1 and not domains2:
            return True

        return False

    @classmethod
    def _has_conflict(cls, content1: str, content2: str) -> bool:
        """检查两段内容是否有冲突（简化的兼容性接口）"""
        result = cls._analyze_conflict_detailed(content1, content2)
        return result["has_conflict"]

    @classmethod
    def _resolve_conflict_detailed(cls, result1: AgentResult, result2: AgentResult, conflict_info: Dict[str, Any]) -> str:
        """
        根据冲突类型和详细信息解决冲突

        Args:
            result1: 高优先级结果
            result2: 低优先级结果
            conflict_info: 详细冲突分析信息

        Returns:
            冲突解决说明
        """
        conflict_type = conflict_info["type"]

        if conflict_type == ConflictType.TRANSFORMABLE:
            # 可转化类型：两者都需要保留，但说明转化条件
            details = conflict_info.get("details", {})
            transform_result = details.get("transform_result", "可调整")
            return f"综合{result1.agent_name}和{result2.agent_name}的分析，注意{transform_result}的条件"

        if conflict_type == ConflictType.COMPLEMENTARY:
            # 互补类型：两者都需要保留
            return f"综合{result1.agent_name}和{result2.agent_name}的分析，{result1.agent_name}提供整体视角，{result2.agent_name}提供细节分析"

        if conflict_type == ConflictType.FALSE_POSITIVE:
            # 误判类型：保留全面评价
            return f"以{result1.agent_name}的分析为准（{result2.agent_name}的观点已被包含在整体评价中）"

        # ConflictType.REAL_CONFLICT 或 ConflictType.NO_CONFLICT
        # 使用原有的优先级规则
        return cls._resolve_conflict(result1, result2)

    @classmethod
    def _resolve_conflict(cls, result1: AgentResult, result2: AgentResult) -> str:
        """解决两个结果之间的冲突（基于优先级规则）"""
        # 1. 高优先级agent的结论优先
        if result1.priority == AnalysisPriority.HIGH:
            return f"以{result1.agent_name}的分析为准"

        # 2. 高置信度的结论优先
        if result1.confidence > result2.confidence + 0.2:
            return f"以{result1.agent_name}的分析为准(置信度更高)"

        # 3. 运限优先于原局
        if "运限" in result1.content and "原局" in result2.content:
            return f"以{result1.agent_name}的分析为准(运限优先)"

        # 4. 化忌优先
        if "化忌" in result1.content and "化忌" not in result2.content:
            return f"以{result1.agent_name}的分析为准(化忌优先)"

        # 5. 主星分析优先于辅星分析
        if cls._contains_main_star_analysis(result1.content) and not cls._contains_main_star_analysis(result2.content):
            return f"以{result1.agent_name}的分析为准(主星分析优先)"

        # 默认：综合两者，取折中
        return f"综合{result1.agent_name}和{result2.agent_name}的分析"

    @classmethod
    def _contains_main_star_analysis(cls, content: str) -> bool:
        """检查内容是否包含主星分析"""
        main_star_keywords = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]
        return any(star in content for star in main_star_keywords)


# ============ Synthesis Agent ============

class SynthesisAgent:
    """
    综合分析代理

    负责:
    1. 聚合各agent的分析结果
    2. 解决冲突观点
    3. 生成完整的命盘解读报告
    """

    def __init__(self, chart_data: Any):
        """
        初始化综合分析代理

        Args:
            chart_data: 命盘数据
        """
        self.chart = chart_data
        self.conflict_resolver = ConflictResolver()

    async def synthesize(
        self,
        star_analysis: Optional[StarAnalysis] = None,
        palace_analysis: Optional[PalaceAnalysis] = None,
        pattern_analysis: Optional[PatternAnalysis] = None,
        transform_analysis: Optional[TransformAnalysis] = None,
        timing_analysis: Optional[TimingAnalysis] = None
    ) -> SynthesisReport:
        """
        汇总所有分析结果，生成综合报告

        Args:
            star_analysis: 星曜分析结果
            palace_analysis: 宫位分析结果
            pattern_analysis: 格局分析结果
            transform_analysis: 四化分析结果
            timing_analysis: 时机分析结果

        Returns:
            综合报告
        """
        # 创建报告对象
        report = SynthesisReport()

        # 1. 命盘概览
        report.chart_overview = self._generate_chart_overview()

        # 2. 出生信息
        report.birth_info = self._extract_birth_info()

        # 3. 聚合各维度分析
        if star_analysis:
            report.star_analysis = star_analysis
        if palace_analysis:
            report.palace_analysis = palace_analysis
        if pattern_analysis:
            report.pattern_analysis = pattern_analysis
        if transform_analysis:
            report.transform_analysis = transform_analysis
        if timing_analysis:
            report.timing_analysis = timing_analysis

        # 4. 生成综合评估
        report.overall_assessment = self._generate_overall_assessment(report)

        # 5. 分析优劣势
        report.strengths = self._analyze_strengths(report)
        report.weaknesses = self._analyze_weaknesses(report)

        # 6. 生成建议
        report.recommendations = self._generate_recommendations(report)

        # 7. 解决冲突
        if star_analysis or palace_analysis or pattern_analysis:
            report.conflict_resolutions = self._resolve_all_conflicts(
                star_analysis, palace_analysis, pattern_analysis
            )

        return report

    def _generate_chart_overview(self) -> str:
        """生成命盘概览"""
        try:
            # 从命盘数据中提取基本信息
            overview_parts = []

            if hasattr(self.chart, 'birth_year'):
                overview_parts.append(f"出生年份: {self.chart.birth_year}")

            if hasattr(self.chart, 'birth_month'):
                overview_parts.append(f"出生月份: {self.chart.birth_month}")

            if hasattr(self.chart, 'birth_day'):
                overview_parts.append(f"出生日期: {self.chart.birth_day}")

            if hasattr(self.chart, 'birth_hour'):
                overview_parts.append(f"出生时辰: {self.chart.birth_hour}")

            if hasattr(self.chart, 'gender'):
                overview_parts.append(f"性别: {self.chart.gender}")

            if hasattr(self.chart, 'solar_term'):
                overview_parts.append(f"节气: {self.chart.solar_term}")

            return " | ".join(overview_parts) if overview_parts else "命盘基本信息"
        except Exception:
            return "命盘基本信息"

    def _extract_birth_info(self) -> Dict[str, Any]:
        """提取出生信息"""
        info = {}
        try:
            if hasattr(self.chart, 'birth_year'):
                info['year'] = self.chart.birth_year
            if hasattr(self.chart, 'birth_month'):
                info['month'] = self.chart.birth_month
            if hasattr(self.chart, 'birth_day'):
                info['day'] = self.chart.birth_day
            if hasattr(self.chart, 'birth_hour'):
                info['hour'] = self.chart.birth_hour
            if hasattr(self.chart, 'gender'):
                info['gender'] = self.chart.gender
        except Exception:
            pass
        return info

    def _generate_overall_assessment(self, report: SynthesisReport) -> str:
        """生成综合评估"""
        assessments = []

        # 基于星曜分析 - 处理 star_agent 的 StarAnalysis 类型
        if hasattr(report.star_analysis, 'main_stars') and report.star_analysis.main_stars:
            main_star_count = len(report.star_analysis.main_stars)
            aux_star_count = len(getattr(report.star_analysis, 'auxiliary_stars', []))
            sha_count = len(getattr(report.star_analysis, 'sha_stars', []))
            # 尝试获取 summary 属性，如果没有则生成
            if hasattr(report.star_analysis, 'summary') and report.star_analysis.summary:
                assessments.append(f"星曜: {report.star_analysis.summary}")
            else:
                assessments.append(f"星曜: 含{main_star_count}颗主星、{aux_star_count}颗辅星、{sha_count}颗煞星")

        # 基于宫位分析
        if hasattr(report.palace_analysis, 'summary') and report.palace_analysis.summary:
            assessments.append(f"宫位: {report.palace_analysis.summary}")
        elif hasattr(report.palace_analysis, 'palace_results'):
            palace_count = len(report.palace_analysis.palace_results)
            assessments.append(f"宫位: 共{palace_count}个宫位")

        # 基于格局分析
        if hasattr(report.pattern_analysis, 'major_patterns') and report.pattern_analysis.major_patterns:
            patterns = "、".join(report.pattern_analysis.major_patterns)
            assessments.append(f"格局: {patterns}")
        elif hasattr(report.pattern_analysis, 'patterns'):
            pattern_count = len(report.pattern_analysis.patterns)
            assessments.append(f"格局: 共{pattern_count}个格局")

        # 基于四化分析
        if hasattr(report.transform_analysis, 'summary') and report.transform_analysis.summary:
            assessments.append(f"四化: {report.transform_analysis.summary}")
        elif hasattr(report.transform_analysis, 'transforms'):
            transform_count = len(report.transform_analysis.transforms)
            assessments.append(f"四化: 共{transform_count}个四化")

        # 基于时机分析
        if hasattr(report.timing_analysis, 'summary') and report.timing_analysis.summary:
            assessments.append(f"运势: {report.timing_analysis.summary}")

        return "；".join(assessments) if assessments else "综合分析进行中"

    def _analyze_strengths(self, report: SynthesisReport) -> List[str]:
        """分析优势"""
        strengths = []

        # 从星曜分析提取优势
        if report.star_analysis.main_stars:
            strengths.append(f"主星入驻: {', '.join(report.star_analysis.main_stars[:3])}")

        # 从格局分析提取优势
        if report.pattern_analysis.major_patterns:
            strengths.append(f"主要格局: {', '.join(report.pattern_analysis.major_patterns)}")

        # 从宫位分析提取优势
        strong_palaces = [
            palace for palace, strength in report.palace_analysis.palace_strengths.items()
            if strength >= 70
        ]
        if strong_palaces:
            strengths.append(f"强宫: {', '.join(strong_palaces[:3])}")

        # 从四化分析提取优势
        if report.transform_analysis.original_transforms:
            lu_stars = [k for k, v in report.transform_analysis.original_transforms.items() if v == "化禄"]
            if lu_stars:
                strengths.append(f"化禄: {', '.join(lu_stars)}")

        return strengths if strengths else ["需要进一步分析"]

    def _analyze_weaknesses(self, report: SynthesisReport) -> List[str]:
        """分析劣势"""
        weaknesses = []

        # 从宫位分析提取劣势
        weak_palaces = [
            palace for palace, strength in report.palace_analysis.palace_strengths.items()
            if strength < 40
        ]
        if weak_palaces:
            weaknesses.append(f"弱宫: {', '.join(weak_palaces[:3])}")

        # 从四化分析提取劣势
        if report.transform_analysis.original_transforms:
            ji_stars = [k for k, v in report.transform_analysis.original_transforms.items() if v == "化忌"]
            if ji_stars:
                weaknesses.append(f"化忌: {', '.join(ji_stars)}")

        # 从时机分析提取注意事项
        if report.timing_analysis.key_timing:
            warnings = [t for t in report.timing_analysis.key_timing if "注意" in t or "防" in t]
            if warnings:
                weaknesses.append(f"注意事项: {', '.join(warnings[:2])}")

        return weaknesses if weaknesses else ["无明显劣势"]

    def _generate_recommendations(self, report: SynthesisReport) -> List[str]:
        """生成趋吉避凶建议"""
        recommendations = []

        # 基于优势的建议
        if report.strengths:
            recommendations.append(f"发挥优势: 把握{'、'.join(report.strengths[:2])}")

        # 基于劣势的建议
        if report.weaknesses:
            recommendations.append(f"规避风险: 注意{'、'.join(report.weaknesses[:2])}")

        # 基于时机分析的建议
        if report.timing_analysis.key_timing:
            for timing in report.timing_analysis.key_timing[:3]:
                if "宜" in timing or "利" in timing:
                    recommendations.append(f"把握时机: {timing}")
                elif "忌" in timing or "不宜" in timing:
                    recommendations.append(f"注意规避: {timing}")

        # 基于四化的建议
        if report.transform_analysis.current_transforms:
            for star, transform in report.transform_analysis.current_transforms.items():
                if transform == "化忌":
                    recommendations.append(f"化忌化解: {star}年注意化解")
                elif transform == "化禄":
                    recommendations.append(f"化禄把握: {star}年把握机遇")

        # 通用建议
        recommendations.extend([
            "保持积极心态，顺势而为",
            "关注健康，定期体检",
            "理性投资，避免冲动决策"
        ])

        return recommendations[:8]  # 最多8条建议

    def _resolve_all_conflicts(
        self,
        star_analysis: Optional[Any],
        palace_analysis: Optional[Any],
        pattern_analysis: Optional[Any]
    ) -> Dict[str, str]:
        """解决所有分析之间的冲突"""
        resolutions = {}

        # 构建agent结果列表
        results = []

        if star_analysis:
            # 获取summary或生成内容摘要
            if hasattr(star_analysis, 'summary') and star_analysis.summary:
                content = star_analysis.summary
            else:
                # 从分析结果生成摘要
                main_stars = getattr(star_analysis, 'main_stars', [])
                main_star_names = [s.name if hasattr(s, 'name') else str(s) for s in main_stars[:5]]
                content = f"星曜分析: {len(main_stars)}颗主星" if main_stars else "星曜分析完成"
            results.append(AgentResult(
                agent_name="StarAgent",
                content=content,
                priority=AnalysisPriority.HIGH,
                confidence=0.9
            ))

        if palace_analysis:
            if hasattr(palace_analysis, 'summary') and palace_analysis.summary:
                content = palace_analysis.summary
            else:
                palace_results = getattr(palace_analysis, 'palace_results', [])
                content = f"宫位分析: {len(palace_results)}个宫位" if palace_results else "宫位分析完成"
            results.append(AgentResult(
                agent_name="PalaceAgent",
                content=content,
                priority=AnalysisPriority.HIGH,
                confidence=0.85
            ))

        if pattern_analysis:
            if hasattr(pattern_analysis, 'summary') and pattern_analysis.summary:
                content = pattern_analysis.summary
            else:
                patterns = getattr(pattern_analysis, 'patterns', [])
                content = f"格局分析: {len(patterns)}个格局" if patterns else "格局分析完成"
            results.append(AgentResult(
                agent_name="PatternAgent",
                content=content,
                priority=AnalysisPriority.MEDIUM,
                confidence=0.8
            ))

        # 解决冲突
        if len(results) > 1:
            resolutions["整体"] = self.conflict_resolver.resolve(results)

        return resolutions

    def resolve_conflicts(self, agent_results: List[AgentResult]) -> str:
        """
        解决冲突的公开接口

        Args:
            agent_results: 各agent的结果列表

        Returns:
            解决后的结论
        """
        return self.conflict_resolver.resolve(agent_results)

    def generate_fortune_report(self, report: SynthesisReport) -> Dict[str, Any]:
        """
        生成完整的运势报告

        Args:
            report: 综合报告

        Returns:
            格式化报告
        """
        return {
            "报告标题": "紫微斗数命盘综合分析报告",
            "命盘概览": {
                "出生信息": report.birth_info,
                "基本盘面": report.chart_overview
            },
            "一、命盘概览": {
                "内容": report.chart_overview
            },
            "二、星曜分析": {
                "主星": report.star_analysis.main_stars,
                "辅星": report.star_analysis.assistant_stars,
                "杂曜": report.star_analysis.marginal_stars,
                "四化星": report.star_analysis.transforming_stars,
                "关键观察": report.star_analysis.key_observations,
                "小结": report.star_analysis.summary
            },
            "三、宫位强弱": {
                "强弱评分": report.palace_analysis.palace_strengths,
                "关键宫位": report.palace_analysis.key_palaces,
                "观察": report.palace_analysis.observations,
                "小结": report.palace_analysis.summary
            },
            "四、格局判定": {
                "主格": report.pattern_analysis.major_patterns,
                "副格": report.pattern_analysis.minor_patterns,
                "观察": report.pattern_analysis.observations,
                "小结": report.pattern_analysis.summary
            },
            "五、四化解读": {
                "原局四化": report.transform_analysis.original_transforms,
                "运限四化": report.transform_analysis.current_transforms,
                "观察": report.transform_analysis.observations,
                "小结": report.transform_analysis.summary
            },
            "六、运势预测": {
                "当前阶段": report.timing_analysis.current_period,
                "流年运势": report.timing_analysis.year_fate,
                "关键时机": report.timing_analysis.key_timing,
                "观察": report.timing_analysis.observations,
                "小结": report.timing_analysis.summary
            },
            "七、趋吉避凶建议": {
                "优势": report.strengths,
                "劣势": report.weaknesses,
                "建议": report.recommendations
            },
            "综合评估": report.overall_assessment,
            "冲突解决": report.conflict_resolutions
        }


# ============ LLM增强综合分析 ============

class LLMSynthesisAnalyzer:
    """综合分析LLM增强器"""

    def __init__(self, chart_data: Any, enable_semantic_search: bool = True):
        self.chart = chart_data
        self.enable_semantic_search = enable_semantic_search
        self._semantic_search = None

    @property
    def semantic_search(self):
        """延迟加载语义搜索模块"""
        if self._semantic_search is None:
            try:
                from ..semantic_search import get_semantic_search
                self._semantic_search = get_semantic_search()
            except ImportError:
                self._semantic_search = None
        return self._semantic_search

    def _build_search_context(self, query: str, top_k: int = 3) -> str:
        """
        构建语义搜索上下文

        Args:
            query: 查询文本
            top_k: 返回结果数

        Returns:
            格式化的知识上下文
        """
        if not self.enable_semantic_search:
            return ""

        search = self.semantic_search
        if search is None:
            return ""

        try:
            return search.get_knowledge_context(query, top_k=top_k)
        except Exception as e:
            print(f"[LLMSynthesisAnalyzer] 语义搜索失败: {e}")
            return ""

    def _extract_search_keywords(self) -> List[str]:
        """从命盘数据中提取搜索关键词"""
        keywords = []

        # 提取主星
        stars = self.chart.get("stars", {})
        main_stars = stars.get("main_stars", [])
        for star in main_stars:
            name = star.get("name", "")
            if name:
                keywords.append(name)

        # 提取四化
        transforms = self.chart.get("transforms", [])
        for t in transforms:
            star = t.get("star", "")
            transform_type = t.get("type", "")
            if star and transform_type:
                keywords.append(f"{star}化{transform_type}")

        # 提取关键宫位
        palaces = self.chart.get("palaces", {})
        key_palaces = ["命宫", "官禄宫", "财帛宫", "夫妻宫", "迁移宫"]
        for palace in key_palaces:
            if palace in palaces:
                keywords.append(palace)

        return keywords[:10]  # 限制关键词数量

    async def synthesize_with_llm(
        self,
        star_analysis: Optional[Dict[str, Any]] = None,
        palace_analysis: Optional[Dict[str, Any]] = None,
        pattern_analysis: Optional[Dict[str, Any]] = None,
        transform_analysis: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度综合分析（带语义搜索增强）

        Args:
            star_analysis: 星曜分析结果（可选）
            palace_analysis: 宫位分析结果（可选）
            pattern_analysis: 格局分析结果（可选）
            transform_analysis: 四化分析结果（可选）
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON综合分析报告
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import (
            SYNTHESIS_SYSTEM_PROMPT,
            build_synthesis_user_prompt,
            format_analysis_as_text
        )

        # 构建提示词
        user_prompt = build_synthesis_user_prompt(
            self.chart,
            star_analysis,
            palace_analysis,
            pattern_analysis,
            transform_analysis,
            question
        )

        # 添加语义搜索上下文
        if self.enable_semantic_search:
            # 从问题或命盘提取关键词进行搜索
            search_queries = []

            if question:
                search_queries.append(question)

            # 添加命盘相关的搜索查询
            keywords = self._extract_search_keywords()
            search_queries.extend(keywords[:5])

            # 执行多角度搜索并合并上下文
            search_contexts = []
            for query in search_queries[:3]:  # 限制搜索次数
                context = self._build_search_context(query, top_k=2)
                if context and context not in search_contexts:
                    search_contexts.append(context)

            if search_contexts:
                user_prompt += "\n\n" + "\n---\n".join(search_contexts)

        messages = [
            {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature, cache=False)

        return result

    def synthesize_with_llm_sync(
        self,
        star_analysis: Optional[Dict[str, Any]] = None,
        palace_analysis: Optional[Dict[str, Any]] = None,
        pattern_analysis: Optional[Dict[str, Any]] = None,
        transform_analysis: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """同步版本的LLM综合分析"""
        import asyncio
        return asyncio.run(
            self.synthesize_with_llm(
                star_analysis,
                palace_analysis,
                pattern_analysis,
                transform_analysis,
                question,
                temperature
            )
        )

    async def generate_text_report(
        self,
        star_analysis: Optional[Dict[str, Any]] = None,
        palace_analysis: Optional[Dict[str, Any]] = None,
        pattern_analysis: Optional[Dict[str, Any]] = None,
        transform_analysis: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """生成文本格式的LLM综合分析报告"""
        from .llm_prompts import format_analysis_as_text

        result = await self.synthesize_with_llm(
            star_analysis,
            palace_analysis,
            pattern_analysis,
            transform_analysis,
            question,
            temperature
        )
        return format_analysis_as_text(result)


async def llm_synthesize_report(
    chart_data: Any,
    star_analysis: Optional[Dict[str, Any]] = None,
    palace_analysis: Optional[Dict[str, Any]] = None,
    pattern_analysis: Optional[Dict[str, Any]] = None,
    transform_analysis: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None,
    enable_semantic_search: bool = True
) -> Dict[str, Any]:
    """
    使用LLM生成综合分析报告（带语义搜索增强）

    Args:
        chart_data: 命盘数据
        star_analysis: 星曜分析结果（可选）
        palace_analysis: 宫位分析结果（可选）
        pattern_analysis: 格局分析结果（可选）
        transform_analysis: 四化分析结果（可选）
        question: 可选的特定问题
        enable_semantic_search: 是否启用语义搜索增强（默认True）

    Returns:
        LLM综合分析报告
    """
    analyzer = LLMSynthesisAnalyzer(chart_data, enable_semantic_search=enable_semantic_search)
    return await analyzer.synthesize_with_llm(
        star_analysis,
        palace_analysis,
        pattern_analysis,
        transform_analysis,
        question
    )


def llm_synthesize_report_sync(
    chart_data: Any,
    star_analysis: Optional[Dict[str, Any]] = None,
    palace_analysis: Optional[Dict[str, Any]] = None,
    pattern_analysis: Optional[Dict[str, Any]] = None,
    transform_analysis: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None,
    enable_semantic_search: bool = True
) -> Dict[str, Any]:
    """同步版本的LLM综合分析（带语义搜索增强）"""
    import asyncio
    return asyncio.run(
        llm_synthesize_report(
            chart_data,
            star_analysis,
            palace_analysis,
            pattern_analysis,
            transform_analysis,
            question,
            enable_semantic_search
        )
    )


# ============ Standard LLM Pattern Functions ============

class LLMSynthesisAnalyzerStandard:
    """
    综合分析LLM增强器 - 标准模式

    遵循 star_agent.py 的 LLMStarAnalyzer 模式
    """

    def __init__(self, chart_data: Any, analysis_data: Optional[Dict[str, Any]] = None):
        """
        初始化综合分析LLM增强器

        Args:
            chart_data: 命盘数据
            analysis_data: 分析数据（可选），包含 star_analysis, palace_analysis 等
        """
        self.chart = chart_data
        self.analysis = analysis_data or {}

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度综合分析（标准模式）

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON综合分析报告
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import SYNTHESIS_SYSTEM_PROMPT, build_synthesis_user_prompt

        # 获取各维度的分析结果
        star_analysis = self.analysis.get("star_analysis")
        palace_analysis = self.analysis.get("palace_analysis")
        pattern_analysis = self.analysis.get("pattern_analysis")
        transform_analysis = self.analysis.get("transform_analysis")
        timing_analysis = self.analysis.get("timing_analysis")

        # 构建用户提示词
        user_prompt = build_synthesis_user_prompt(
            self.chart,
            star_analysis,
            palace_analysis,
            pattern_analysis,
            transform_analysis,
            question
        )

        messages = [
            {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature, cache=False)

        return result

    def analyze_with_llm_sync(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        同步版本的LLM综合分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON综合分析报告
        """
        import asyncio
        return asyncio.run(self.analyze_with_llm(question, temperature))

    async def generate_text_report(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """
        生成文本格式的LLM综合分析报告

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            格式化的文本报告
        """
        from .llm_prompts import format_analysis_as_text

        result = await self.analyze_with_llm(question, temperature)
        return format_analysis_as_text(result)


async def llm_analyze_synthesis(
    chart_data: Any,
    analysis_data: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用LLM进行综合分析（标准模式）

    Args:
        chart_data: 命盘数据
        analysis_data: 分析数据（可选），包含各agent的分析结果
        question: 可选的特定问题

    Returns:
        LLM综合分析报告
    """
    analyzer = LLMSynthesisAnalyzerStandard(chart_data, analysis_data)
    return await analyzer.analyze_with_llm(question)


def llm_analyze_synthesis_sync(
    chart_data: Any,
    analysis_data: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    同步版本的LLM综合分析（标准模式）

    Args:
        chart_data: 命盘数据
        analysis_data: 分析数据（可选），包含各agent的分析结果
        question: 可选的特定问题

    Returns:
        LLM综合分析报告
    """
    import asyncio
    return asyncio.run(llm_analyze_synthesis(chart_data, analysis_data, question))


# ============ Utility Functions ============

def create_synthesis_agent(chart_data: Any) -> SynthesisAgent:
    """创建综合分析代理的工厂函数"""
    return SynthesisAgent(chart_data)
