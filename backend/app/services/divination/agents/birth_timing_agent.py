"""
BirthTimingAgent - 剖腹产良辰吉日分析引擎

分析并推荐最佳剖腹产时间，遍历日期范围内的所有可能时辰，
生成虚拟命盘并评分排序。

职责：
1. 生成指定日期范围内所有时辰的虚拟命盘
2. 对命盘进行多维度评分
3. 分析命盘优劣势
4. 排序并输出最佳时辰推荐
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from app.services.divination.agents.chart_agent import generate_chart_sync
from app.services.divination.fortune_calculator import (
    DIMENSION_PALACE_MAPPING,
    MAIN_STAR_BASE_SCORE,
    AUXILIARY_STAR_JUDGMENT,
)
from app.services.divination.service_types import fortune_level_from_score

logger = logging.getLogger(__name__)


from .birth_timing_constants import (
    SHICHEN_HOURS,
    SHICHEN_DISPLAY,
    IMPORTANT_STARS,
    SHA_STARS,
    STAR_TEMPLE_SCORES,
)
from .birth_timing_types import BirthTimingOption, BirthTimingResult


# ============ 核心类 ============

class BirthTimingAgent:
    """
    剖腹产良辰吉日分析引擎

    分析并推荐最佳剖腹产时间，综合考虑：
    - 命宫主星强弱
    - 各宫位星曜配置
    - 四化飞星影响
    - 格局吉凶
    """

    def __init__(
        self,
        mother_birth_info: Dict[str, Any],
        father_birth_info: Optional[Dict[str, Any]] = None,
        date_range_start: Optional[str] = None,
        date_range_end: Optional[str] = None,
        top_n: int = 10,
    ):
        """
        初始化剖腹产分析

        Args:
            mother_birth_info: 母亲出生信息
                {
                    "year": 1990,
                    "month": 5,
                    "day": 15,
                    "hour": 10,
                    "gender": "female",
                    "birthplace": "北京",
                    "is_lunar": False
                }
            father_birth_info: 父亲出生信息（可选）
            date_range_start: 日期范围开始 "YYYY-MM-DD"
            date_range_end: 日期范围结束 "YYYY-MM-DD"
            top_n: 返回最优数量
        """
        self.mother_info = mother_birth_info
        self.father_info = father_birth_info
        self.top_n = top_n

        # 设置默认日期范围（当前日期+30天到+180天）
        today = datetime.now()
        if date_range_start:
            self.date_range_start = datetime.strptime(date_range_start, "%Y-%m-%d")
        else:
            self.date_range_start = today + timedelta(days=30)

        if date_range_end:
            self.date_range_end = datetime.strptime(date_range_end, "%Y-%m-%d")
        else:
            self.date_range_end = today + timedelta(days=180)

        # 确保开始日期不早于今天
        if self.date_range_start < today:
            self.date_range_start = today

        logger.info(
            f"初始化剖腹产分析: 日期范围 {self.date_range_start.date()} 至 {self.date_range_end.date()}, "
            f"Top-{top_n}"
        )

    def generate_timing_options(self) -> List[BirthTimingOption]:
        """
        生成所有时辰选项并评分

        Returns:
            按分数排序的时辰选项列表
        """
        options: List[BirthTimingOption] = []
        current_date = self.date_range_start

        while current_date <= self.date_range_end:
            date_str = current_date.strftime("%Y-%m-%d")

            # 生成农历日期（简化版本，实际应该用 lunarcalendar 库）
            lunar_date = self._get_lunar_date(current_date)

            # 遍历十二时辰
            for i, (shichen_name, start_hour, end_hour) in enumerate(SHICHEN_HOURS):
                try:
                    # 生成虚拟命盘
                    chart = self._generate_virtual_chart(
                        birth_year=current_date.year,
                        birth_month=current_date.month,
                        birth_day=current_date.day,
                        birth_hour=start_hour,
                        gender="male",  # 假设剖腹产为男孩，可根据需要调整
                    )

                    # 评分
                    score, strengths, weaknesses = self._score_chart(chart)

                    # 获取等级
                    level = fortune_level_from_score(score)

                    # 生成命盘摘要
                    chart_summary = self._extract_chart_summary(chart)

                    # 生成推荐理由和注意事项
                    reasons = self._generate_reasons(chart, score, strengths)
                    warnings = self._generate_warnings(chart, weaknesses)

                    option = BirthTimingOption(
                        rank=0,  # 稍后排序时设置
                        date=date_str,
                        lunar_date=lunar_date,
                        hour=f"{shichen_name} ({SHICHEN_DISPLAY[i]})",
                        chart_summary=chart_summary,
                        score=score,
                        level=level,
                        strengths=strengths,
                        weaknesses=weaknesses,
                        reasons=reasons,
                        warnings=warnings,
                    )
                    options.append(option)

                except Exception as e:
                    logger.warning(f"生成时辰 {date_str} {shichen_name} 命盘失败: {e}")
                    continue

            current_date += timedelta(days=1)

        # 按分数排序
        options.sort(key=lambda x: x.score, reverse=True)

        # 设置排名
        for i, option in enumerate(options[:self.top_n]):
            option.rank = i + 1

        logger.info(f"生成 {len(options)} 个时辰选项，前 {self.top_n} 名已排序")

        return options[:self.top_n]

    def _generate_virtual_chart(
        self,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        birth_hour: int,
        gender: str,
    ) -> Dict[str, Any]:
        """
        生成虚拟命盘

        Args:
            birth_year: 出生年份
            birth_month: 出生月份
            birth_day: 出生日期
            birth_hour: 出生小时 (0-23)
            gender: 性别 ("male" 或 "female")

        Returns:
            命盘数据字典
        """
        return generate_chart_sync(
            year=birth_year,
            month=birth_month,
            day=birth_day,
            hour=birth_hour,
            gender=gender,
            minute=0,
            birthplace="",
            is_lunar=False,
        )

    def _score_chart(self, chart: Dict[str, Any]) -> tuple[float, List[str], List[str]]:
        """
        计算命盘分数，返回 (分数, 优势, 劣势)

        综合分 = (
            命宫主星分数 × 0.25 +          # 主星强弱
            官禄宫分数 × 0.2 +             # 事业发展
            财帛宫分数 × 0.2 +             # 财运
            迁移宫分数 × 0.15 +            # 外出运势
            疾厄宫分数 × 0.1 +             # 健康
            夫妻宫分数 × 0.1               # 感情/婚姻
        ) + 格局加成 + 四化加分 - 煞星扣分

        Args:
            chart: 命盘数据

        Returns:
            (综合分数, 优势列表, 劣势列表)
        """
        palaces = chart.get("palaces", {})
        stars = chart.get("stars", {})
        transforms = chart.get("transforms", [])

        strengths: List[str] = []
        weaknesses: List[str] = []

        # ===== 1. 命宫主星分数 =====
        ming_gong = palaces.get("命宫", {})
        ming_gong_stars = ming_gong.get("stars", [])

        # 提取主星
        main_stars = stars.get("main_stars", [])
        main_star_names = [s.get("name", "") for s in main_stars]

        # 命宫主星基础分
        ming_gong_score = 50.0  # 默认基础分

        if main_star_names:
            # 最重要的主星（第一个）作为命宫主星
            main_star = main_star_names[0] if main_star_names else ""
            if main_star in MAIN_STAR_BASE_SCORE:
                ming_gong_score = MAIN_STAR_BASE_SCORE[main_star] * 100

            # 检查是否是紫微或天府
            if main_star in ["紫微", "天府"]:
                strengths.append(f"命宫{main_star}坐守，格局尊贵")
                ming_gong_score += 10

        # ===== 2. 各宫位分数计算 =====
        palace_scores = {}
        for dimension, palace_name in DIMENSION_PALACE_MAPPING.items():
            palace_data = palaces.get(palace_name, {})
            palace_stars = palace_data.get("stars", [])

            # 计算宫位分数
            palace_score = self._calculate_palace_score(palace_stars, main_stars)
            palace_scores[dimension] = palace_score

        # ===== 3. 四化飞星加分/减分 =====
        transform_bonus = 0

        # 提取四化信息
        transform_dict = {}
        for t in transforms:
            transform_type = t.get("type", "")
            transform_star = t.get("star", "")
            transform_target = t.get("target_palace", "")
            transform_dict[transform_star] = {
                "type": transform_type,
                "target": transform_target,
            }

        # 化禄入命宫
        for star, info in transform_dict.items():
            if info["type"] == "化禄" and info["target"] == "命宫":
                transform_bonus += 15
                strengths.append("化禄入命宫，财运亨通")

            # 化忌入命宫
            if info["type"] == "化忌" and info["target"] == "命宫":
                transform_bonus -= 10
                weaknesses.append("化忌入命宫，需注意是非")

            # 禄忌同宫
            if info["type"] == "化禄" or info["type"] == "化忌":
                for other_star, other_info in transform_dict.items():
                    if other_star != star:
                        if info["target"] == other_info["target"]:
                            if (info["type"] == "化禄" and other_info["type"] == "化忌") or \
                               (info["type"] == "化忌" and other_info["type"] == "化禄"):
                                transform_bonus += 5
                                strengths.append(f"禄忌同宫{info['target']}，吉凶参半但以吉论")

        # ===== 4. 煞星扣分 =====
        sha_penalty = 0
        sha_stars = stars.get("sha_stars", [])
        for sha in sha_stars:
            sha_name = sha.get("name", "")
            sha_palace = sha.get("palace", "")

            if sha_name in SHA_STARS:
                sha_penalty += 15
                weaknesses.append(f"{sha_name}在{sha_palace}，带来挑战")

        # ===== 5. 格局加成 =====
        pattern_bonus = 0
        for star in main_star_names:
            if star in ["紫微", "天府"]:
                pattern_bonus += 10
            if star == "七杀" or star == "破军" or star == "贪狼":
                pattern_bonus += 8
                strengths.append(f"具有{star}，杀破狼格局")

        # ===== 6. 计算综合分数 =====
        base_score = (
            ming_gong_score * 0.25 +
            palace_scores.get("career", 50) * 0.20 +
            palace_scores.get("wealth", 50) * 0.20 +
            palace_scores.get("relationship", 50) * 0.10 +
            palace_scores.get("health", 50) * 0.15 +
            palace_scores.get("social", 50) * 0.10
        )

        # 确保分数在0-100范围内
        final_score = base_score + transform_bonus + pattern_bonus - sha_penalty
        final_score = max(0.0, min(100.0, final_score))

        # 添加剩余的优势和劣势
        if final_score >= 85:
            strengths.append("综合格局极佳，大富大贵之命")
        elif final_score >= 70:
            strengths.append("命格良好，一生顺遂")
        elif final_score < 30:
            weaknesses.append("命格较弱，需要后天努力")

        return final_score, strengths, weaknesses

    def _calculate_palace_score(
        self,
        palace_stars: List[Dict[str, Any]],
        main_stars: List[Dict[str, Any]]
    ) -> float:
        """
        计算宫位分数

        Args:
            palace_stars: 宫位内的星曜列表
            main_stars: 所有主星列表

        Returns:
            宫位分数 (0-100)
        """
        if not palace_stars:
            return 50.0  # 默认中等

        score = 50.0
        main_star_names = [s.get("name", "") for s in main_stars]

        for star in palace_stars:
            star_name = star.get("name", "")
            temple = star.get("temple", "平")  # 庙旺等级

            temple_score = STAR_TEMPLE_SCORES.get(temple, 0.5)

            if star_name in main_star_names:
                # 主星
                if star_name in MAIN_STAR_BASE_SCORE:
                    score += MAIN_STAR_BASE_SCORE[star_name] * temple_score * 10
            elif star_name in AUXILIARY_STAR_JUDGMENT:
                # 辅星
                score += AUXILIARY_STAR_JUDGMENT[star_name] * temple_score * 5
            elif star_name in SHA_STARS:
                # 煞星
                score -= 10

        return max(0.0, min(100.0, score))

    def _analyze_chart_strengths_weaknesses(
        self, chart: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """
        分析命盘优劣势

        Args:
            chart: 命盘数据

        Returns:
            (优势列表, 劣势列表)
        """
        strengths: List[str] = []
        weaknesses: List[str] = []

        palaces = chart.get("palaces", {})
        stars = chart.get("stars", {})
        transforms = chart.get("transforms", [])

        # 主星分析
        main_stars = stars.get("main_stars", [])
        main_star_names = [s.get("name", "") for s in main_stars]

        # 重要星曜分析
        for star_name in IMPORTANT_STARS:
            if star_name in main_star_names:
                if star_name in ["紫微", "天府"]:
                    strengths.append(f"{star_name}星入命，格局尊贵")
                elif star_name in ["贪狼", "七杀", "破军"]:
                    strengths.append(f"{star_name}星入命，敢于拼搏")

        # 煞星分析
        sha_stars = stars.get("sha_stars", [])
        if len(sha_stars) >= 3:
            weaknesses.append(f"煞星较多({len(sha_stars)}颗)，需注意运势波动")
        elif len(sha_stars) == 0:
            strengths.append("无煞星冲破，格局较为稳定")

        # 四化分析
        transform_dict = {t.get("star", ""): t.get("type", "") for t in transforms}

        if "化禄" in transform_dict.values():
            strengths.append("命中有化禄，财运较好")
        if "化忌" in transform_dict.values():
            weaknesses.append("命中有化忌，需注意是非困扰")

        # 命宫分析
        ming_gong = palaces.get("命宫", {})
        ming_gong_stars = ming_gong.get("stars", [])

        if len(ming_gong_stars) >= 5:
            strengths.append("命宫星曜聚集，格局厚重")
        elif len(ming_gong_stars) == 0:
            weaknesses.append("命宫空荡，格局较轻")

        return strengths, weaknesses

    def _extract_chart_summary(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取命盘摘要

        Args:
            chart: 命盘数据

        Returns:
            命盘摘要字典
        """
        birth_info = chart.get("birth_info", {})
        palaces = chart.get("palaces", {})
        stars = chart.get("stars", {})
        transforms = chart.get("transforms", [])

        # 命宫主星
        ming_gong = palaces.get("命宫", {})
        ming_gong_stars = ming_gong.get("stars", [])
        main_star_names = [s.get("name", "") for s in ming_gong_stars if s.get("level") == "major"]

        # 命宫主星（第一个主要星曜）
        main_star = main_star_names[0] if main_star_names else "无主星"

        # 四化
        transform_list = [f"{t.get('star', '')}{t.get('type', '')}" for t in transforms]

        # 五行局
        wuxing_ju = birth_info.get("wuxing_ju_name", "")

        return {
            "wuxing_ju": wuxing_ju,
            "main_star": main_star,
            "transforms": transform_list,
            "main_star_count": len(stars.get("main_stars", [])),
            "auxiliary_star_count": len(stars.get("auxiliary_stars", [])),
            "sha_star_count": len(stars.get("sha_stars", [])),
        }

    def _generate_reasons(
        self,
        chart: Dict[str, Any],
        score: float,
        strengths: List[str],
    ) -> List[str]:
        """
        生成推荐理由

        Args:
            chart: 命盘数据
            score: 综合分数
            strengths: 优势列表

        Returns:
            推荐理由列表
        """
        reasons: List[str] = []

        if score >= 85:
            reasons.append("综合格局极佳，为大富大贵之命")
        elif score >= 70:
            reasons.append("命格优良，一生运势顺遂")
        elif score >= 50:
            reasons.append("命格中等，需后天努力")

        # 基于优势生成理由
        for strength in strengths[:3]:  # 最多取3个
            if "主星" in strength or "格局" in strength:
                reasons.append(strength)

        # 基于命盘摘要
        chart_summary = self._extract_chart_summary(chart)
        main_star = chart_summary.get("main_star", "")

        if main_star in ["紫微", "天府"]:
            reasons.append(f"命宫{main_star}星，尊贵之格")
        elif main_star in ["贪狼", "七杀", "破军"]:
            reasons.append(f"命宫{main_star}星，敢于创业")

        return reasons if reasons else ["命格尚可，适合剖腹产"]

    def _generate_warnings(
        self,
        chart: Dict[str, Any],
        weaknesses: List[str],
    ) -> List[str]:
        """
        生成注意事项

        Args:
            chart: 命盘数据
            weaknesses: 劣势列表

        Returns:
            注意事项列表
        """
        warnings: List[str] = []

        # 基于劣势生成警告
        for weakness in weaknesses[:3]:  # 最多取3个
            if "煞星" in weakness or "化忌" in weakness:
                warnings.append(weakness)

        # 基于命盘摘要
        chart_summary = self._extract_chart_summary(chart)
        sha_count = chart_summary.get("sha_star_count", 0)

        if sha_count >= 3:
            warnings.append("煞星较多，建议后天注意化解")
        if sha_count == 0:
            warnings.append("无煞星冲破，格局稳定")

        return warnings if warnings else ["命格平和，无特殊注意事项"]

    def _get_lunar_date(self, solar_date: datetime) -> str:
        """
        获取农历日期（简化版本）

        注意：实际应该使用 lunarcalendar 或类似库进行转换
        这里返回简化格式

        Args:
            solar_date: 阳历日期

        Returns:
            农历日期字符串
        """
        # 简化处理：直接返回"农历"+月份+日
        # 实际项目中应该使用专业的农历转换库
        month = solar_date.month
        day = solar_date.day

        month_names = [
            "", "正", "二", "三", "四", "五", "六",
            "七", "八", "九", "十", "冬", "腊"
        ]

        month_name = month_names[month] if 1 <= month <= 12 else str(month)
        return f"农历{month_name}月{day}日"

    def analyze(self) -> BirthTimingResult:
        """
        执行完整分析

        Returns:
            剖腹产分析结果
        """
        logger.info("开始剖腹产良辰吉日分析...")

        # 生成母亲命盘（如果提供）
        mother_chart = {}
        if self.mother_info:
            try:
                mother_chart = generate_chart_sync(
                    year=self.mother_info.get("year", 1990),
                    month=self.mother_info.get("month", 1),
                    day=self.mother_info.get("day", 1),
                    hour=self.mother_info.get("hour", 12),
                    gender=self.mother_info.get("gender", "female"),
                    minute=self.mother_info.get("minute", 0),
                    birthplace=self.mother_info.get("birthplace", ""),
                    is_lunar=self.mother_info.get("is_lunar", False),
                )
            except Exception as e:
                logger.warning(f"生成母亲命盘失败: {e}")

        # 生成父亲命盘（如果提供）
        father_chart = {}
        if self.father_info:
            try:
                father_chart = generate_chart_sync(
                    year=self.father_info.get("year", 1990),
                    month=self.father_info.get("month", 1),
                    day=self.father_info.get("day", 1),
                    hour=self.father_info.get("hour", 12),
                    gender=self.father_info.get("gender", "male"),
                    minute=self.father_info.get("minute", 0),
                    birthplace=self.father_info.get("birthplace", ""),
                    is_lunar=self.father_info.get("is_lunar", False),
                )
            except Exception as e:
                logger.warning(f"生成父亲命盘失败: {e}")

        # 生成时辰选项
        options = self.generate_timing_options()

        # 确定最佳选项
        best_option = options[0] if options else None

        # 生成分析摘要
        analysis_summary = self._generate_analysis_summary(options)

        # 计算置信度
        confidence = self._calculate_confidence(options)

        result = BirthTimingResult(
            service_type="birth_timing",
            mother_chart=mother_chart,
            father_chart=father_chart,
            options=options,
            best_option=best_option,
            analysis_summary=analysis_summary,
            confidence=confidence,
        )

        logger.info(f"剖腹产分析完成，生成 {len(options)} 个时辰选项，最优: {best_option.date if best_option else '无'}")

        return result

    def _generate_analysis_summary(self, options: List[BirthTimingOption]) -> str:
        """
        生成分析摘要

        Args:
            options: 时辰选项列表

        Returns:
            分析摘要字符串
        """
        if not options:
            return "在指定日期范围内未找到合适的剖腹产时间"

        best = options[0]
        avg_score = sum(opt.score for opt in options) / len(options)

        summary = f"分析了 {len(options)} 个时辰选项，"
        summary += f"最优时间为 {best.date} {best.hour}，"
        summary += f"综合评分 {best.score:.1f} 分（{best.level}）。"

        if avg_score >= 70:
            summary += "整体命格优良，多个时段适合剖腹产。"
        elif avg_score >= 50:
            summary += "命格中等，建议优先选择评分较高的时段。"
        else:
            summary += "命格整体偏弱，建议与命理师进一步咨询。"

        return summary

    def _calculate_confidence(self, options: List[BirthTimingOption]) -> float:
        """
        计算置信度

        Args:
            options: 时辰选项列表

        Returns:
            置信度 (0-1)
        """
        if not options:
            return 0.0

        # 基于选项数量和分数差异计算置信度
        score_variance = self._calculate_variance([opt.score for opt in options])

        # 选项数量置信度
        count_confidence = min(len(options) / 10, 1.0)  # 10个选项时满分

        # 分数集中度置信度
        variance_confidence = max(0, 1 - score_variance / 1000)

        # 综合置信度
        confidence = (count_confidence * 0.4 + variance_confidence * 0.6)

        return min(1.0, max(0.0, confidence))

    def _calculate_variance(self, scores: List[float]) -> float:
        """
        计算方差

        Args:
            scores: 分数列表

        Returns:
            方差
        """
        if not scores:
            return 0.0

        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        return variance


# ============ LLM增强分析 ============

class LLMBirthTimingAnalyzer:
    """
    剖腹产良辰吉日LLM增强器

    使用LLM对规则引擎生成的时辰选项进行深度分析和优化，
    综合考虑父母命盘、孩子命盘质量、五行平衡等因素。
    """

    def __init__(
        self,
        birth_timing_result: BirthTimingResult,
        mother_chart: Optional[Dict[str, Any]] = None,
        father_chart: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化LLM增强器

        Args:
            birth_timing_result: 规则引擎生成的时辰分析结果
            mother_chart: 母亲命盘数据
            father_chart: 父亲命盘数据
        """
        self.birth_timing_result = birth_timing_result
        self.mother_chart = mother_chart
        self.father_chart = father_chart

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度时辰分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import BIRTH_TIMING_SYSTEM_PROMPT, build_birth_timing_user_prompt

        # 构建提示词
        user_prompt = build_birth_timing_user_prompt(
            birth_timing_result=self.birth_timing_result.to_dict(),
            mother_chart=self.mother_chart,
            father_chart=self.father_chart,
            question=question
        )

        messages = [
            {"role": "system", "content": BIRTH_TIMING_SYSTEM_PROMPT},
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
        """
        同步版本的LLM分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        import asyncio
        return asyncio.run(self.analyze_with_llm(question, temperature))

    async def generate_text_report(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """
        生成文本格式的LLM分析报告

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            格式化的文本报告
        """
        from .llm_prompts import format_analysis_as_text
        result = await self.analyze_with_llm(question, temperature)
        return format_analysis_as_text(result)

    async def enhance_result(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> BirthTimingResult:
        """
        使用LLM增强分析结果

        在原有规则引擎分析的基础上，调用LLM进行深度分析，
        并将LLM的分析结果整合到返回的BirthTimingResult中。

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            增强后的剖腹产分析结果
        """
        llm_analysis = await self.analyze_with_llm(question, temperature)

        # 如果LLM返回了推荐，更新best_option
        recommended_rank = llm_analysis.get("recommended_option", 1)
        if recommended_rank and 1 <= recommended_rank <= len(self.birth_timing_result.options):
            self.birth_timing_result.best_option = self.birth_timing_result.options[recommended_rank - 1]

        # 更新置信度
        llm_confidence = llm_analysis.get("confidence", 0)
        if llm_confidence:
            # 综合规则引擎置信度和LLM置信度
            original_confidence = self.birth_timing_result.confidence
            self.birth_timing_result.confidence = (original_confidence * 0.3 + llm_confidence * 0.7)

        # 添加LLM分析摘要
        if "final_recommendation" in llm_analysis:
            self.birth_timing_result.analysis_summary = llm_analysis["final_recommendation"]

        return self.birth_timing_result


async def llm_analyze_birth_timing(
    birth_timing_result: BirthTimingResult,
    mother_chart: Optional[Dict[str, Any]] = None,
    father_chart: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用LLM分析剖腹产时辰

    Args:
        birth_timing_result: 规则引擎生成的时辰分析结果
        mother_chart: 母亲命盘数据
        father_chart: 父亲命盘数据
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLMBirthTimingAnalyzer(
        birth_timing_result=birth_timing_result,
        mother_chart=mother_chart,
        father_chart=father_chart
    )
    return await analyzer.analyze_with_llm(question)


def llm_analyze_birth_timing_sync(
    birth_timing_result: BirthTimingResult,
    mother_chart: Optional[Dict[str, Any]] = None,
    father_chart: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    同步版本的LLM剖腹产时辰分析

    Args:
        birth_timing_result: 规则引擎生成的时辰分析结果
        mother_chart: 母亲命盘数据
        father_chart: 父亲命盘数据
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    import asyncio
    return asyncio.run(llm_analyze_birth_timing(
        birth_timing_result=birth_timing_result,
        mother_chart=mother_chart,
        father_chart=father_chart,
        question=question
    ))


def llm_analyze_birth_timing_enhanced(
    mother_birth_info: Dict[str, Any],
    father_birth_info: Optional[Dict[str, Any]] = None,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None,
    top_n: int = 10,
    question: Optional[str] = None
) -> tuple[BirthTimingResult, Dict[str, Any]]:
    """
    完整的LLM增强型剖腹产分析

    先运行规则引擎生成候选时辰，再使用LLM进行深度分析优化。

    Args:
        mother_birth_info: 母亲出生信息
        father_birth_info: 父亲出生信息（可选）
        date_range_start: 日期范围开始 "YYYY-MM-DD"
        date_range_end: 日期范围结束 "YYYY-MM-DD"
        top_n: 返回最优数量
        question: 可选的特定问题

    Returns:
        (BirthTimingResult, LLM分析结果) 元组
    """
    # 先运行规则引擎分析
    birth_timing_result = analyze_birth_timing_sync(
        mother_birth_info=mother_birth_info,
        father_birth_info=father_birth_info,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        top_n=top_n
    )

    # 获取父母命盘
    mother_chart = birth_timing_result.mother_chart if birth_timing_result.mother_chart else None
    father_chart = birth_timing_result.father_chart if birth_timing_result.father_chart else None

    # 调用LLM分析
    llm_result = llm_analyze_birth_timing_sync(
        birth_timing_result=birth_timing_result,
        mother_chart=mother_chart,
        father_chart=father_chart,
        question=question
    )

    # 增强结果
    analyzer = LLMBirthTimingAnalyzer(
        birth_timing_result=birth_timing_result,
        mother_chart=mother_chart,
        father_chart=father_chart
    )

    import asyncio
    enhanced_result = asyncio.run(analyzer.enhance_result(question))

    return enhanced_result, llm_result


# ============ 便捷函数 ============

def analyze_birth_timing_sync(
    mother_birth_info: Dict[str, Any],
    father_birth_info: Optional[Dict[str, Any]] = None,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None,
    top_n: int = 10,
) -> BirthTimingResult:
    """
    同步便捷函数：剖腹产良辰吉日分析

    Args:
        mother_birth_info: 母亲出生信息
        father_birth_info: 父亲出生信息（可选）
        date_range_start: 日期范围开始 "YYYY-MM-DD"
        date_range_end: 日期范围结束 "YYYY-MM-DD"
        top_n: 返回最优数量

    Returns:
        剖腹产分析结果

    Example:
        >>> result = analyze_birth_timing_sync(
        ...     mother_birth_info={"year": 1990, "month": 5, "day": 15, "hour": 10, "gender": "female"},
        ...     date_range_start="2026-09-01",
        ...     date_range_end="2026-09-30",
        ...     top_n=5,
        ... )
        >>> print(result.best_option.date, result.best_option.hour)
    """
    agent = BirthTimingAgent(
        mother_birth_info=mother_birth_info,
        father_birth_info=father_birth_info,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        top_n=top_n,
    )
    return agent.analyze()


# ============ 测试代码 ============

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    print("=== 测试：剖腹产良辰吉日分析 ===")

    # 测试参数
    mother_info = {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "gender": "female",
        "birthplace": "北京",
    }

    # 执行分析（使用较短的范围以加快测试）
    result = analyze_birth_timing_sync(
        mother_birth_info=mother_info,
        father_birth_info=None,
        date_range_start="2026-04-01",
        date_range_end="2026-04-03",  # 只分析3天
        top_n=5,
    )

    print(f"\n分析摘要: {result.analysis_summary}")
    print(f"置信度: {result.confidence:.2f}")

    if result.best_option:
        print(f"\n最佳剖腹产时间:")
        print(f"  日期: {result.best_option.date}")
        print(f"  农历: {result.best_option.lunar_date}")
        print(f"  时辰: {result.best_option.hour}")
        print(f"  评分: {result.best_option.score} ({result.best_option.level})")
        print(f"  优势: {', '.join(result.best_option.strengths[:3])}")
        print(f"  劣势: {', '.join(result.best_option.weaknesses[:2])}")

    print(f"\n共生成 {len(result.options)} 个时辰选项")
