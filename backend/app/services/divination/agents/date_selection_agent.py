"""
DateSelectionAgent - 择日分析智能体

负责分析并推荐最佳择日（结婚/开市/动土/出行），遍历日期范围内的每日并评分排序。

功能：
1. 根据事件类型确定关键宫位
2. 计算每日日柱天干地支
3. 评估每日与命盘的配合度
4. 筛选吉日并排序
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from .date_selection_constants import (
    TIANGAN_DIZHI,
    DATE_EVENT_PALACE_MAPPING,
    AUSPICIOUS_TIANGAN,
    INOMINOUS_TIANGAN,
    TIANGAN_YINYANG,
    TIANGAN_WUXING,
    DIZHI_WUXING,
    WUXING_SHENG,
    WUXING_KENG,
)
from .date_selection_types import DailyOption, DateSelectionResult


class DateSelectionAgent:
    """
    择日分析智能体

    分析并推荐最佳择日，根据事件类型和命盘配合度对日期进行评分排序。
    """

    def __init__(
        self,
        chart: Dict[str, Any],              # 用户命盘
        date_type: str,                     # 吉日类型: "结婚嫁娶"
        date_range_start: str,              # "YYYY-MM-DD"
        date_range_end: str,                # "YYYY-MM-DD"
        top_n: int = 10,
    ):
        """
        初始化择日分析

        Args:
            chart: 用户命盘数据字典
            date_type: 吉日类型
            date_range_start: 日期范围开始
            date_range_end: 日期范围结束
            top_n: 返回最佳日期数量
        """
        self.chart = chart
        self.date_type = date_type
        self.date_range_start = date_range_start
        self.date_range_end = date_range_end
        self.top_n = top_n

        # 从命盘获取生年天干和命宫天干
        self.birth_year_gan = self._get_birth_year_gan()
        self.minggong_gan = self._get_minggong_tiangan()

        # 获取事件对应的关键宫位
        self.target_palaces = DATE_EVENT_PALACE_MAPPING.get(
            date_type, ["命宫", "财帛宫", "官禄宫"]
        )

    def _get_birth_year_gan(self) -> str:
        """获取生年天干"""
        try:
            birth_info = self.chart.get("birth_info", {})
            tiangan = birth_info.get("tiangan", "甲")
            return tiangan[0] if tiangan else "甲"
        except Exception:
            return "甲"

    def _get_minggong_tiangan(self) -> str:
        """获取命宫天干"""
        try:
            palaces = self.chart.get("palaces", {})
            minggong = palaces.get("命宫", {})
            tiangan = minggong.get("tiangan", "甲")
            return tiangan[0] if tiangan else "甲"
        except Exception:
            return "甲"

    def _get_daily_stem_branch(self, solar_date: datetime) -> Tuple[str, str]:
        """
        根据阳历日期计算日柱天干地支

        使用简单的算法计算日柱：
        - 1900年1月1日是庚子日（index 36 in TIANGAN_DIZHI）

        Args:
            solar_date: 阳历日期

        Returns:
            (天干, 地支) 元组
        """
        # 基准日期：1900年1月1日（庚子日，index 36）
        base_date = datetime(1900, 1, 1)
        base_index = 36  # 庚子在60甲子中的位置

        # 计算天数差
        days_diff = (solar_date - base_date).days

        # 计算当前日期在60甲子中的位置
        current_index = (base_index + days_diff) % 60

        # 获取天干地支
        stem_branch = TIANGAN_DIZHI[current_index]
        tiangan = stem_branch[0]
        dizhi = stem_branch[1]

        return tiangan, dizhi

    def _get_lunar_date_approximate(self, solar_date: datetime) -> str:
        """
        近似计算农历日期

        使用简化算法，实际生产环境应使用 lunardate 库

        Args:
            solar_date: 阳历日期

        Returns:
            农历日期字符串，如 "八月初五"
        """
        try:
            from lunardate import LunarDate
            # 转换为农历
            lunar = LunarDate.fromSolarDate(
                solar_date.year, solar_date.month, solar_date.day
            )
            # 农历月份和日期
            month_names = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
            day_names = [
                "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
            ]
            month_name = month_names[lunar.month - 1]
            day_name = day_names[lunar.day - 1]
            return f"{month_name}月{day_name}"
        except ImportError:
            # 简化算法作为fallback
            month = (solar_date.month + 1) % 12
            day = solar_date.day
            month_names = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
            day_names = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                         "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                         "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
            return f"{month_names[month-1]}月{day_names[min(day-1, 29)]}"

    def _calculate_stem_branch_score(
        self,
        tiangan: str,
        dizhi: str,
    ) -> Tuple[float, List[str], List[str]]:
        """
        计算天干地支的配合分数

        Args:
            tiangan: 日柱天干
            dizhi: 日柱地支

        Returns:
            (分数, 优势列表, 劣势列表)
        """
        score = 50.0  # 基础分
        advantages = []
        disadvantages = []

        # 获取天干地支的阴阳五行
        tiangan_yy = TIANGAN_YINYANG.get(tiangan, "阳")
        tiangan_wx = TIANGAN_WUXING.get(tiangan, "土")
        dizhi_wx = DIZHI_WUXING.get(dizhi, "土")

        birth_yy = TIANGAN_YINYANG.get(self.birth_year_gan, "阳")
        birth_wx = TIANGAN_WUXING.get(self.birth_year_gan, "土")
        minggong_yy = TIANGAN_YINYANG.get(self.minggong_gan, "阳")
        minggong_wx = TIANGAN_WUXING.get(self.minggong_gan, "土")

        # 1. 与生年天干同阴阳: +15分
        if tiangan_yy == birth_yy:
            score += 15
            advantages.append(f"日柱天干{tiangan}与生年天干同{tiangan_yy}性")

        # 2. 日柱天干生助生年天干: +20分
        if WUXING_SHENG.get(tiangan_wx, "") == birth_wx:
            score += 20
            advantages.append(f"日柱天干{tiangan}之五行生助生年天干")
        elif WUXING_SHENG.get(birth_wx, "") == tiangan_wx:
            score += 10
            advantages.append(f"日柱天干{tiangan}受生年天干之生助")

        # 3. 日柱天干克泄生年天干: -10分
        if WUXING_KENG.get(tiangan_wx, "") == birth_wx:
            score -= 10
            disadvantages.append(f"日柱天干{tiangan}克生年天干")
        elif tiangan_wx in WUXING_KENG.get(birth_wx, "").split():
            score -= 5
            disadvantages.append(f"日柱天干{tiangan}被生年天干所泄")

        # 4. 日柱天干与命宫天干相生: +10分
        if WUXING_SHENG.get(tiangan_wx, "") == minggong_wx:
            score += 10
            advantages.append(f"日柱天干{tiangan}生助命宫天干")
        elif WUXING_SHENG.get(minggong_wx, "") == tiangan_wx:
            score += 5
            advantages.append(f"命宫天干生助日柱天干")

        # 5. 地支与命宫地支相合: +10分
        # 子丑合化土, 寅亥合化木, 卯戌合化火, 辰酉合化金, 巳申合化水, 午未合化火
        he_groups = [
            ("子", "丑"), ("丑", "子"), ("寅", "亥"), ("亥", "寅"),
            ("卯", "戌"), ("戌", "卯"), ("辰", "酉"), ("酉", "辰"),
            ("巳", "申"), ("申", "巳"), ("午", "未"), ("未", "午"),
        ]
        minggong_branch = self._get_minggong_branch()
        if minggong_branch and (dizhi, minggong_branch) in he_groups:
            score += 10
            advantages.append(f"日柱地支{dizhi}与命宫地支{minggong_branch}相合")

        # 归一化到0-100
        score = max(0.0, min(100.0, score))
        return score, advantages, disadvantages

    def _get_minggong_branch(self) -> str:
        """获取命宫地支"""
        try:
            palaces = self.chart.get("palaces", {})
            minggong = palaces.get("命宫", {})
            branch = minggong.get("branch", "子")
            return branch
        except Exception:
            return "子"

    def _calculate_auspicious_score(
        self,
        tiangan: str,
        stem_branch: str,
    ) -> Tuple[float, List[str], List[str]]:
        """
        计算吉凶神煞分数

        Args:
            tiangan: 日柱天干
            stem_branch: 完整日柱（如"甲子"）

        Returns:
            (分数, 吉神列表, 凶煞列表)
        """
        score = 50.0  # 基础分
        good_signs = []
        bad_signs = []

        # 1. 检查是否为吉日天干
        if stem_branch in AUSPICIOUS_TIANGAN:
            score += 20
            activities = AUSPICIOUS_TIANGAN[stem_branch]
            good_signs.append(f"吉日宜: {','.join(activities)}")

        # 2. 检查是否为凶日天干
        if stem_branch in INOMINOUS_TIANGAN:
            score -= 20
            avoid_activities = INOMINOUS_TIANGAN[stem_branch]
            bad_signs.append(f"凶日忌: {','.join(avoid_activities)}")

        # 3. 检查日柱地支是否为四旺（子午卯酉）
        si_wang = ["子", "午", "卯", "酉"]
        dizhi = stem_branch[1] if len(stem_branch) > 1 else ""
        if dizhi in si_wang:
            score += 15
            good_signs.append("四旺日（地支为子午卯酉之一）")

        # 4. 检查是否为岁破/月破（地支与当年太岁相冲）
        # 简化处理：申子辰破寅，亥卯未破申，寅午戌破亥，巳酉丑破寅
        today = datetime.now()
        year_zhi = self._get_year_zhi(today.year)
        if year_zhi:
            chong_zhi = self._get_opposite_zhi(year_zhi)
            if dizhi == chong_zhi:
                score -= 25
                bad_signs.append("月破日（地支与太岁相冲）")

        # 5. 检查是否杨公忌日（正三四六十月 忌初一，二五七八十一月 忌初九，十二月 忌腊月二十七）
        # 简化处理

        # 6. 检查是否四离日（立春、立夏、立秋、立冬前一天）
        # 简化处理

        # 归一化到0-100
        score = max(0.0, min(100.0, score))
        return score, good_signs, bad_signs

    def _get_year_zhi(self, year: int) -> Optional[str]:
        """获取指定年份的地支"""
        # 简化计算：2024年是甲辰年（辰）
        year_zhi_map = {
            2024: "辰", 2025: "巳", 2026: "午", 2027: "未",
            2028: "申", 2029: "酉", 2030: "戌", 2031: "亥",
            2032: "子", 2033: "丑", 2034: "寅", 2035: "卯",
        }
        return year_zhi_map.get(year, None)

    def _get_opposite_zhi(self, zhi: str) -> str:
        """获取相冲的地支"""
        opposites = {
            "子": "午", "丑": "未", "寅": "申", "卯": "酉",
            "辰": "戌", "巳": "亥", "午": "子", "未": "丑",
            "申": "寅", "酉": "卯", "戌": "辰", "亥": "巳",
        }
        return opposites.get(zhi, "")

    def _calculate_palace_strength(
        self,
        palace_name: str,
        tiangan: str,
    ) -> float:
        """
        计算当日某宫位的强弱

        简化版：根据日柱天干与宫位地支的关系计算

        Args:
            palace_name: 宫位名称
            tiangan: 日柱天干

        Returns:
            强弱分数 0-100
        """
        score = 50.0

        # 获取宫位地支
        palace_zhi = self._get_palace_branch(palace_name)
        if not palace_zhi:
            return score

        # 日柱天干生助宫位地支: +10
        tiangan_wx = TIANGAN_WUXING.get(tiangan, "土")
        palace_zhi_wx = DIZHI_WUXING.get(palace_zhi, "土")

        if WUXING_SHENG.get(tiangan_wx, "") == palace_zhi_wx:
            score += 15
        elif WUXING_KENG.get(tiangan_wx, "") == palace_zhi_wx:
            score -= 10

        return max(0.0, min(100.0, score))

    def _get_palace_branch(self, palace_name: str) -> Optional[str]:
        """获取宫位地支"""
        try:
            palaces = self.chart.get("palaces", {})
            palace = palaces.get(palace_name, {})
            return palace.get("branch", None)
        except Exception:
            return None

    def _score_daily(
        self,
        tiangan: str,
        dizhi: str,
        stem_branch: str,
    ) -> Tuple[float, List[str], List[str], List[str], List[str]]:
        """
        计算每日综合分数

        综合分 = 关键宫位分数 × 0.6 + 天干配合分 × 0.2 + 吉凶神煞分 × 0.2

        Args:
            tiangan: 日柱天干
            dizhi: 日柱地支
            stem_branch: 完整日柱

        Returns:
            (总分, 优势列表, 劣势列表, 吉神列表, 凶煞列表)
        """
        # 1. 计算关键宫位分数
        palace_score = 50.0
        palace_details = []
        for palace in self.target_palaces:
            p_score = self._calculate_palace_strength(palace, tiangan)
            palace_score += (p_score - 50) / len(self.target_palaces)
            if p_score > 55:
                palace_details.append(f"{palace}强")
            elif p_score < 45:
                palace_details.append(f"{palace}弱")
        palace_score = max(0.0, min(100.0, palace_score))

        # 2. 计算天干配合分
        stem_score, stem_advantages, stem_disadvantages = self._calculate_stem_branch_score(
            tiangan, dizhi
        )

        # 3. 计算吉凶神煞分
        auspicious_score, good_signs, bad_signs = self._calculate_auspicious_score(
            tiangan, stem_branch
        )

        # 综合分数计算
        # 权重：关键宫位 60%, 天干配合 20%, 吉凶神煞 20%
        total_score = (
            palace_score * 0.6 +
            stem_score * 0.2 +
            auspicious_score * 0.2
        )

        # 合并所有因素
        advantages = stem_advantages + palace_details
        disadvantages = stem_disadvantages
        warnings = bad_signs

        return total_score, advantages, disadvantages, good_signs, warnings

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

    def _get_best_time_window(self, tiangan: str, dizhi: str) -> str:
        """
        获取最佳时段

        Args:
            tiangan: 日柱天干
            dizhi: 日柱地支

        Returns:
            最佳时段描述
        """
        # 根据日柱地支确定最佳时辰
        time_windows = {
            "子": "23:00-01:00",
            "丑": "01:00-03:00",
            "寅": "03:00-05:00",
            "卯": "05:00-07:00",
            "辰": "07:00-09:00",
            "巳": "09:00-11:00",
            "午": "11:00-13:00",
            "未": "13:00-15:00",
            "申": "15:00-17:00",
            "酉": "17:00-19:00",
            "戌": "19:00-21:00",
            "亥": "21:00-23:00",
        }

        # 时辰对应的最佳小时（方便阅读的表述）
        hour_map = {
            "子": "子时（23:00-01:00）",
            "丑": "丑时（01:00-03:00）",
            "寅": "寅时（03:00-05:00）",
            "卯": "卯时（05:00-07:00）",
            "辰": "辰时（07:00-09:00）",
            "巳": "巳时（09:00-11:00）",
            "午": "午时（11:00-13:00）",
            "未": "未时（13:00-15:00）",
            "申": "申时（15:00-17:00）",
            "酉": "酉时（17:00-19:00）",
            "戌": "戌时（19:00-21:00）",
            "亥": "亥时（21:00-23:00）",
        }

        return hour_map.get(dizhi, "巳时（09:00-11:00）")

    def _generate_daily_options(self) -> List[DailyOption]:
        """生成所有日期选项并评分"""
        options = []

        # 解析日期范围
        start_date = datetime.strptime(self.date_range_start, "%Y-%m-%d")
        end_date = datetime.strptime(self.date_range_end, "%Y-%m-%d")

        current_date = start_date
        rank = 1

        while current_date <= end_date:
            # 计算日柱
            tiangan, dizhi = self._get_daily_stem_branch(current_date)
            stem_branch = tiangan + dizhi

            # 计算农历日期
            lunar_date = self._get_lunar_date_approximate(current_date)

            # 计算分数
            score, advantages, disadvantages, good_signs, warnings = self._score_daily(
                tiangan, dizhi, stem_branch
            )

            # 检查是否为吉日（分数>=50）
            is_auspicious = score >= 50

            # 获取适合做的事
            suitable = AUSPICIOUS_TIANGAN.get(stem_branch, [])
            # 只保留与当前事件类型相关的
            if self.date_type == "结婚嫁娶":
                suitable = [s for s in suitable if s in ["结婚", "搬家"]]
            elif self.date_type == "开市开张":
                suitable = [s for s in suitable if s in ["开市", "交易", "立券"]]
            elif self.date_type == "动土破土":
                suitable = [s for s in suitable if s == "动土"]
            elif self.date_type == "出行远行":
                suitable = [s for s in suitable if s == "出行"]

            # 获取应避免的事
            avoid = INOMINOUS_TIANGAN.get(stem_branch, [])

            # 构建关键因素
            key_factors = []
            if advantages:
                key_factors.extend(advantages[:2])
            if good_signs:
                key_factors.extend(good_signs[:2])

            # 获取最佳时段
            best_time = self._get_best_time_window(tiangan, dizhi)

            # 创建每日选项
            option = DailyOption(
                rank=rank,
                solar_date=current_date.strftime("%Y-%m-%d"),
                lunar_date=lunar_date,
                tiangan=stem_branch,
                dizhi=dizhi,
                score=score,
                level=self._get_level_from_score(score),
                is_auspicious=is_auspicious,
                suitable_for=suitable if suitable else ["一般事宜"],
                avoid=avoid if avoid else [],
                key_factors=key_factors if key_factors else ["无特殊"],
                best_time_window=best_time,
                warnings=warnings if warnings else [],
            )

            options.append(option)
            rank += 1
            current_date += timedelta(days=1)

        return options

    def _sort_and_rank_options(self, options: List[DailyOption]) -> List[DailyOption]:
        """对选项排序并重新编号"""
        # 按分数降序排序
        sorted_options = sorted(options, key=lambda x: x.score, reverse=True)

        # 重新编号
        for i, opt in enumerate(sorted_options):
            opt.rank = i + 1

        return sorted_options

    def _generate_summary(
        self,
        best_dates: List[DailyOption],
        date_type: str,
    ) -> str:
        """生成分析摘要"""
        if not best_dates:
            return f"在{self.date_range_start}至{self.date_range_end}期间，未找到合适的{date_type}吉日。"

        best = best_dates[0]
        summary = (
            f"根据命盘分析，在{self.date_range_start}至{self.date_range_end}期间，"
            f"最适合{date_type}的日子是{best.solar_date}（{best.lunar_date}，{best.tiangan}日）。"
            f"该日综合评分{best.score:.1f}分，等级{best.level}。"
        )

        if best.key_factors:
            summary += f"主要优势：{'；'.join(best.key_factors[:2])}。"
        if best.suitable_for:
            summary += f"该日宜：{'、'.join(best.suitable_for[:3])}。"
        if best.avoid:
            summary += f"忌：{'、'.join(best.avoid[:2])}。"

        return summary

    def analyze(self) -> DateSelectionResult:
        """
        执行完整分析

        Returns:
            DateSelectionResult: 择日分析结果
        """
        # 生成所有日期选项
        daily_options = self._generate_daily_options()

        # 过滤吉日并排序
        auspicious_options = [opt for opt in daily_options if opt.is_auspicious]
        sorted_options = self._sort_and_rank_options(auspicious_options)

        # 取前N个最佳日期
        best_dates = sorted_options[:self.top_n]

        # 生成分析摘要
        summary = self._generate_summary(best_dates, self.date_type)

        # 计算置信度（基于选项数量和分数差异）
        confidence = min(0.95, 0.6 + 0.05 * len(sorted_options))
        if sorted_options and len(sorted_options) > 1:
            score_diff = sorted_options[0].score - sorted_options[1].score
            if score_diff > 20:
                confidence += 0.1

        # 构建结果
        result = DateSelectionResult(
            service_type="date_selection",
            date_type=self.date_type,
            target_palaces=self.target_palaces,
            daily_options=sorted_options,
            best_dates=best_dates,
            analysis_summary=summary,
            confidence=confidence,
            date_range=(self.date_range_start, self.date_range_end),
        )

        return result


def select_date_sync(
    chart: Dict[str, Any],
    date_type: str,
    date_range_start: str,
    date_range_end: str,
    top_n: int = 10,
) -> DateSelectionResult:
    """
    同步便捷函数

    Args:
        chart: 用户命盘
        date_type: 吉日类型
        date_range_start: 日期范围开始
        date_range_end: 日期范围结束
        top_n: 返回最佳日期数量

    Returns:
        DateSelectionResult: 择日分析结果
    """
    agent = DateSelectionAgent(
        chart=chart,
        date_type=date_type,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        top_n=top_n,
    )
    return agent.analyze()


async def select_date_async(
    chart: Dict[str, Any],
    date_type: str,
    date_range_start: str,
    date_range_end: str,
    top_n: int = 10,
) -> DateSelectionResult:
    """
    异步便捷函数

    Args:
        chart: 用户命盘
        date_type: 吉日类型
        date_range_start: 日期范围开始
        date_range_end: 日期范围结束
        top_n: 返回最佳日期数量

    Returns:
        DateSelectionResult: 择日分析结果
    """
    agent = DateSelectionAgent(
        chart=chart,
        date_type=date_type,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        top_n=top_n,
    )
    return agent.analyze()


# ============ LLM增强分析 ============

from typing import Optional
from .llm_prompts import (
    DATE_SELECTION_SYSTEM_PROMPT,
    build_date_selection_user_prompt,
)


class LLMDateSelectionAnalyzer:
    """择日分析LLM增强器"""

    def __init__(self, chart: Dict[str, Any]):
        self.chart = chart

    async def analyze_with_llm(
        self,
        date_type: str,
        daily_options: List[DailyOption],
        question: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度择日分析

        Args:
            date_type: 事件类型
            daily_options: 候选日期列表
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        from ....utils.llm_client import LLMClient

        # 将DailyOption转换为字典
        options_dicts = [opt.to_dict() for opt in daily_options]

        # 构建提示词
        user_prompt = build_date_selection_user_prompt(
            self.chart, date_type, options_dicts, question
        )

        messages = [
            {"role": "system", "content": DATE_SELECTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature)

        return result

    def analyze_with_llm_sync(
        self,
        date_type: str,
        daily_options: List[DailyOption],
        question: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """同步版本的LLM分析"""
        import asyncio
        return asyncio.run(
            self.analyze_with_llm(date_type, daily_options, question, temperature)
        )


async def llm_analyze_date_selection(
    chart: Dict[str, Any],
    date_type: str,
    daily_options: List[DailyOption],
    question: Optional[str] = None,
) -> Dict[str, Any]:
    """
    使用LLM分析择日候选

    Args:
        chart: 命盘数据
        date_type: 事件类型
        daily_options: 候选日期列表
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLMDateSelectionAnalyzer(chart)
    return await analyzer.analyze_with_llm(date_type, daily_options, question)


def llm_analyze_date_selection_sync(
    chart: Dict[str, Any],
    date_type: str,
    daily_options: List[DailyOption],
    question: Optional[str] = None,
) -> Dict[str, Any]:
    """
    同步版本的LLM择日分析

    Args:
        chart: 命盘数据
        date_type: 事件类型
        daily_options: 候选日期列表
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    import asyncio
    return asyncio.run(
        llm_analyze_date_selection(chart, date_type, daily_options, question)
    )


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("DateSelectionAgent 测试")
    print("=" * 60)

    # 模拟命盘数据
    test_chart = {
        "birth_info": {
            "tiangan": "甲",
            "gender": "male",
        },
        "palaces": {
            "命宫": {"branch": "子", "tiangan": "甲"},
            "夫妻宫": {"branch": "午", "tiangan": "庚"},
            "财帛宫": {"branch": "丑", "tiangan": "乙"},
            "官禄宫": {"branch": "寅", "tiangan": "丙"},
            "田宅宫": {"branch": "卯", "tiangan": "丁"},
            "迁移宫": {"branch": "辰", "tiangan": "戊"},
            "福德宫": {"branch": "巳", "tiangan": "己"},
            "疾厄宫": {"branch": "午", "tiangan": "庚"},
            "父母宫": {"branch": "未", "tiangan": "辛"},
        },
    }

    # 测试择日分析
    result = select_date_sync(
        chart=test_chart,
        date_type="结婚嫁娶",
        date_range_start="2026-03-22",
        date_range_end="2026-04-22",
        top_n=5,
    )

    print(f"\n分析类型: {result.date_type}")
    print(f"关键宫位: {result.target_palaces}")
    print(f"日期范围: {result.date_range[0]} 至 {result.date_range[1]}")
    print(f"置信度: {result.confidence:.2f}")
    print(f"\n分析摘要:\n{result.analysis_summary}")

    print(f"\n{'='*60}")
    print(f"最佳日期 TOP {len(result.best_dates)}:")
    print(f"{'='*60}")

    for opt in result.best_dates:
        print(f"\n排名 {opt.rank}: {opt.solar_date} ({opt.lunar_date})")
        print(f"  日柱: {opt.tiangan}")
        print(f"  分数: {opt.score:.1f} ({opt.level})")
        print(f"  宜: {', '.join(opt.suitable_for)}")
        print(f"  忌: {', '.join(opt.avoid) if opt.avoid else '无'}")
        print(f"  最佳时段: {opt.best_time_window}")
        if opt.key_factors:
            print(f"  关键因素: {', '.join(opt.key_factors)}")
        if opt.warnings:
            print(f"  警示: {', '.join(opt.warnings)}")

    print(f"\n{'='*60}")
    print("DateSelectionAgent implemented")
    print(f"{'='*60}")
