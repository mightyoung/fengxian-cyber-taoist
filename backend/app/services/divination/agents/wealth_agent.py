"""
财运分析智能体 - WealthAgent

负责深度财运分析,包括:
- 财帛宫分析: 正财运势、赚钱能力
- 田宅宫分析: 不动产运势、储物能力
- 福德宫分析: 理财观念、福德运势
- 流年财运: 年度财富预测
- 财富格局识别: 富贵命格分析
- 投资建议: 基于命盘的理财建议
"""

import os
from typing import Dict, List, Optional, Any

from .wealth_constants import WEALTH_STARS, PALACE_WEIGHTS
from .wealth_types import (
    WealthLevel,
    PalaceWealthAnalysis,
    WealthPattern,
    YearlyWealthForecast,
    WealthReport,
)


class WealthAgent:
    """
    财运分析智能体

    负责深度财运分析,包括:
    1. 财帛宫分析 - 正财运势、赚钱能力
    2. 田宅宫分析 - 不动产运势、储物能力
    3. 福德宫分析 - 理财观念、福德运势
    4. 流年财运 - 年度财富预测
    5. 财富格局识别 - 富贵命格分析
    6. 投资建议 - 基于命盘的理财建议
    """

    def __init__(self, chart_data: Dict[str, Any]):
        """
        初始化财运分析智能体

        Args:
            chart_data: 命盘数据
        """
        self.chart = chart_data
        self.palaces_data = chart_data.get("palaces", {})

    def _get_palace_stars(self, palace_name: str) -> List[Dict[str, Any]]:
        """获取宫位内的所有星曜"""
        palace_data = self.palaces_data.get(palace_name, {})
        return palace_data.get("stars", [])

    def _classify_stars(self, palace_name: str) -> Dict[str, List[str]]:
        """分类宫位内的星曜"""
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

            if "正曜" in star_type or star_name in WEALTH_STARS.get("主星", []):
                result["main_stars"].append(star_name)
            elif "辅星" in star_type or star_name in WEALTH_STARS.get("辅星", []):
                result["auxiliary_stars"].append(star_name)
            elif "煞星" in star_type or star_name in WEALTH_STARS.get("煞星", []):
                result["sha_stars"].append(star_name)
            elif "化曜" in star_type or star_name in WEALTH_STARS.get("化曜", []):
                result["transform_stars"].append(star_name)

        return result

    def _get_palace_score(self, palace_name: str) -> int:
        """获取宫位评分"""
        palace_data = self.palaces_data.get(palace_name, {})
        return palace_data.get("score", {}).get("total", 50)

    def _analyze_caibi_palace(self) -> PalaceWealthAnalysis:
        """
        分析财帛宫

        财帛宫代表:
        - 正财运势 (收入能力)
        - 赚钱方式
        - 理财能力
        - 物质生活
        """
        palace_name = "财帛宫"
        stars_classified = self._classify_stars(palace_name)
        score = self._get_palace_score(palace_name)

        # 财富指示星
        wealth_indicators = []
        risk_factors = []
        opportunity_factors = []

        main_stars = stars_classified["main_stars"]
        transform_stars = stars_classified["transform_stars"]
        sha_stars = stars_classified["sha_stars"]

        # 主星分析
        if "武曲" in main_stars:
            wealth_indicators.append("武曲星 - 正财之星，适合技术或财务相关工作")
        if "太阳" in main_stars:
            wealth_indicators.append("太阳星 - 财禄旺盛，宜公开事业")
        if "太阴" in main_stars:
            wealth_indicators.append("太阴星 - 理财之星，宜财务规划")
        if "贪狼" in main_stars:
            wealth_indicators.append("贪狼星 - 野心大，财运佳但需注意理财")
        if "天府" in main_stars:
            wealth_indicators.append("天府星 - 财库充盈，宜积累财富")
        if "紫微" in main_stars:
            wealth_indicators.append("紫微星 - 领导型财运，宜创业或管理")

        # 四化分析
        if "化禄" in transform_stars:
            opportunity_factors.append("化禄入财帛宫 - 财运亨通，财源广进")
            wealth_indicators.append("化禄 - 财富自来，财运亨通")
        if "化权" in transform_stars:
            opportunity_factors.append("化权入财帛宫 - 赚钱能力强，宜积极进取")
        if "化科" in transform_stars:
            opportunity_factors.append("化科入财帛宫 - 财运平稳，宜知识变现")
        if "化忌" in transform_stars:
            risk_factors.append("化忌入财帛宫 - 赚钱辛苦，需靠技术或固定收入")
            wealth_indicators.append("化忌 - 财来财去，需靠技术吃饭")

        # 煞星分析
        if len(sha_stars) >= 2:
            risk_factors.append(f"多煞星同宫 - 需注意破财风险 ({', '.join(sha_stars)})")
        if "地空" in sha_stars or "地劫" in sha_stars:
            risk_factors.append("空劫同宫 - 财运不稳，宜保守理财")

        # 辅星分析
        if "禄存" in stars_classified["auxiliary_stars"]:
            opportunity_factors.append("禄存星同宫 - 有储蓄能力，财运稳定")
        if "天马" in stars_classified["auxiliary_stars"]:
            opportunity_factors.append("天马星同宫 - 走动生财，宜异地发展")

        # 生成解读
        interpretation_parts = [f"【财帛宫】综合评分: {score}分"]
        if wealth_indicators:
            interpretation_parts.append("财富特征: " + "；".join(wealth_indicators[:3]))
        if opportunity_factors:
            interpretation_parts.append("有利因素: " + "；".join(opportunity_factors[:2]))
        if risk_factors:
            interpretation_parts.append("风险因素: " + "；".join(risk_factors[:2]))

        return PalaceWealthAnalysis(
            palace_name=palace_name,
            score=score,
            strength_level=self._get_strength_level(score),
            main_stars=main_stars,
            auxiliary_stars=stars_classified["auxiliary_stars"],
            sha_stars=sha_stars,
            transform_stars=transform_stars,
            interpretation="\n".join(interpretation_parts),
            wealth_indicator="; ".join(wealth_indicators[:2]) if wealth_indicators else "无明显财富特征",
            risk_factors=risk_factors,
            opportunity_factors=opportunity_factors
        )

    def _analyze_tianzhai_palace(self) -> PalaceWealthAnalysis:
        """
        分析田宅宫

        田宅宫代表:
        - 不动产运势
        - 储物能力
        - 家庭财务
        - 祖业运势
        """
        palace_name = "田宅宫"
        stars_classified = self._classify_stars(palace_name)
        score = self._get_palace_score(palace_name)

        wealth_indicators = []
        risk_factors = []
        opportunity_factors = []

        main_stars = stars_classified["main_stars"]
        transform_stars = stars_classified["transform_stars"]
        sha_stars = stars_classified["sha_stars"]

        # 主星分析
        if "天府" in main_stars:
            wealth_indicators.append("天府星 - 不动产之星，宜置产保值")
        if "武曲" in main_stars:
            wealth_indicators.append("武曲星 - 财务之星，宜投资理财")
        if "紫微" in main_stars:
            wealth_indicators.append("紫微星 - 贵气之星，宜高端物业")
        if "太阴" in main_stars:
            wealth_indicators.append("太阴星 - 储物之星，宜收藏投资")
        if "贪狼" in main_stars:
            wealth_indicators.append("贪狼星 - 欲望之星，需注意理财")
        if "破军" in main_stars:
            risk_factors.append("破军星 - 变动之星，不动产易有变动")

        # 四化分析
        if "化禄" in transform_stars:
            opportunity_factors.append("化禄入田宅宫 - 不动产运势佳，宜置产")
        if "化忌" in transform_stars:
            risk_factors.append("化忌入田宅宫 - 田宅运势较弱，不宜强求")

        # 煞星分析
        if "地空" in sha_stars or "地劫" in sha_stars:
            risk_factors.append("空劫同宫 - 不动产运势较弱，宜谨慎")
        if "火星" in sha_stars or "铃星" in sha_stars:
            risk_factors.append("火铃同宫 - 房产易有是非，宜注意法律问题")

        # 辅星分析
        if "禄存" in stars_classified["auxiliary_stars"]:
            opportunity_factors.append("禄存星同宫 - 有储蓄和置产能力")

        interpretation_parts = [f"【田宅宫】综合评分: {score}分"]
        if wealth_indicators:
            interpretation_parts.append("财富特征: " + "；".join(wealth_indicators[:3]))
        if opportunity_factors:
            interpretation_parts.append("有利因素: " + "；".join(opportunity_factors[:2]))
        if risk_factors:
            interpretation_parts.append("风险因素: " + "；".join(risk_factors[:2]))

        return PalaceWealthAnalysis(
            palace_name=palace_name,
            score=score,
            strength_level=self._get_strength_level(score),
            main_stars=main_stars,
            auxiliary_stars=stars_classified["auxiliary_stars"],
            sha_stars=sha_stars,
            transform_stars=transform_stars,
            interpretation="\n".join(interpretation_parts),
            wealth_indicator="; ".join(wealth_indicators[:2]) if wealth_indicators else "无明显田宅特征",
            risk_factors=risk_factors,
            opportunity_factors=opportunity_factors
        )

    def _analyze_fude_palace(self) -> PalaceWealthAnalysis:
        """
        分析福德宫

        福德宫代表:
        - 理财观念
        - 福德运势
        - 精神财富
        - 物质享受
        """
        palace_name = "福德宫"
        stars_classified = self._classify_stars(palace_name)
        score = self._get_palace_score(palace_name)

        wealth_indicators = []
        risk_factors = []
        opportunity_factors = []

        main_stars = stars_classified["main_stars"]
        transform_stars = stars_classified["transform_stars"]
        sha_stars = stars_classified["sha_stars"]

        # 主星分析
        if "紫微" in main_stars:
            wealth_indicators.append("紫微星 - 福德深厚，精神富足")
        if "天梁" in main_stars:
            wealth_indicators.append("天梁星 - 理财高手，善于规划")
        if "天同" in main_stars:
            wealth_indicators.append("天同星 - 享受型理财，宜稳健投资")
        if "太阴" in main_stars:
            wealth_indicators.append("太阴星 - 细腻理财，宜长期规划")
        if "廉贞" in main_stars:
            risk_factors.append("廉贞星 - 情绪化理财，需理性对待")

        # 四化分析
        if "化禄" in transform_stars:
            opportunity_factors.append("化禄入福德宫 - 福德运势佳，理财顺利")
        if "化忌" in transform_stars:
            risk_factors.append("化忌入福德宫 - 理财观念需调整，宜保守")

        # 煞星分析
        if len(sha_stars) >= 2:
            risk_factors.append(f"多煞星同宫 - 理财观念受影响 ({', '.join(sha_stars)})")

        interpretation_parts = [f"【福德宫】综合评分: {score}分"]
        if wealth_indicators:
            interpretation_parts.append("财富特征: " + "；".join(wealth_indicators[:3]))
        if opportunity_factors:
            interpretation_parts.append("有利因素: " + "；".join(opportunity_factors[:2]))
        if risk_factors:
            interpretation_parts.append("风险因素: " + "；".join(risk_factors[:2]))

        return PalaceWealthAnalysis(
            palace_name=palace_name,
            score=score,
            strength_level=self._get_strength_level(score),
            main_stars=main_stars,
            auxiliary_stars=stars_classified["auxiliary_stars"],
            sha_stars=sha_stars,
            transform_stars=transform_stars,
            interpretation="\n".join(interpretation_parts),
            wealth_indicator="; ".join(wealth_indicators[:2]) if wealth_indicators else "无明显福德特征",
            risk_factors=risk_factors,
            opportunity_factors=opportunity_factors
        )

    def _analyze_guanlu_palace(self) -> PalaceWealthAnalysis:
        """
        分析官禄宫

        官禄宫代表:
        - 事业财运
        - 职业发展
        - 收入来源
        - 社会地位
        """
        palace_name = "官禄宫"
        stars_classified = self._classify_stars(palace_name)
        score = self._get_palace_score(palace_name)

        wealth_indicators = []
        risk_factors = []
        opportunity_factors = []

        main_stars = stars_classified["main_stars"]
        transform_stars = stars_classified["transform_stars"]
        sha_stars = stars_classified["sha_stars"]

        # 主星分析
        if "太阳" in main_stars:
            wealth_indicators.append("太阳星 - 事业心强，宜公职或领导")
        if "武曲" in main_stars:
            wealth_indicators.append("武曲星 - 事业财运佳，宜技术或财务")
        if "紫微" in main_stars:
            wealth_indicators.append("紫微星 - 领导型事业，宜创业或管理")
        if "天府" in main_stars:
            wealth_indicators.append("天府星 - 稳定事业，宜积累型发展")
        if "贪狼" in main_stars:
            wealth_indicators.append("贪狼星 - 野心大，宜挑战性工作")

        # 四化分析
        if "化禄" in transform_stars:
            opportunity_factors.append("化禄入官禄宫 - 事业财运亨通")
        if "化权" in transform_stars:
            opportunity_factors.append("化权入官禄宫 - 事业心强，宜积极进取")
        if "化忌" in transform_stars:
            risk_factors.append("化忌入官禄宫 - 事业需稳扎稳打，不宜冒险")

        interpretation_parts = [f"【官禄宫】综合评分: {score}分"]
        if wealth_indicators:
            interpretation_parts.append("财富特征: " + "；".join(wealth_indicators[:3]))
        if opportunity_factors:
            interpretation_parts.append("有利因素: " + "；".join(opportunity_factors[:2]))
        if risk_factors:
            interpretation_parts.append("风险因素: " + "；".join(risk_factors[:2]))

        return PalaceWealthAnalysis(
            palace_name=palace_name,
            score=score,
            strength_level=self._get_strength_level(score),
            main_stars=main_stars,
            auxiliary_stars=stars_classified["auxiliary_stars"],
            sha_stars=sha_stars,
            transform_stars=transform_stars,
            interpretation="\n".join(interpretation_parts),
            wealth_indicator="; ".join(wealth_indicators[:2]) if wealth_indicators else "无明显官禄特征",
            risk_factors=risk_factors,
            opportunity_factors=opportunity_factors
        )

    def _identify_wealth_patterns(self) -> List[WealthPattern]:
        """识别财富格局"""
        patterns = []

        caibi_stars = self._classify_stars("财帛宫")
        tianzhai_stars = self._classify_stars("田宅宫")
        fude_stars = self._classify_stars("福德宫")
        guanlu_stars = self._classify_stars("官禄宫")

        all_stars = {
            "财帛宫": caibi_stars,
            "田宅宫": tianzhai_stars,
            "福德宫": fude_stars,
            "官禄宫": guanlu_stars
        }

        # 武曲天府同会 - 大富之命
        has_wuqu = any("武曲" in stars["main_stars"] for stars in all_stars.values())
        has_tianfu = any("天府" in stars["main_stars"] for stars in all_stars.values())
        if has_wuqu and has_tianfu:
            patterns.append(WealthPattern(
                pattern_name="武曲天府同会格",
                description="财运亨通，有大富之命，善于积累财富",
                score_bonus=15,
                characteristics=["财务稳定", "积累能力强", "不动产运势佳"]
            ))

        # 禄存星多宫 - 财运稳定
        lucun_count = sum(1 for stars in all_stars.values() if "禄存" in stars["auxiliary_stars"])
        if lucun_count >= 2:
            patterns.append(WealthPattern(
                pattern_name="禄存多宫格",
                description="财运稳定，有储蓄能力，财务状况良好",
                score_bonus=10,
                characteristics=["财运稳定", "储蓄能力强", "财务规划佳"]
            ))

        # 化禄星多宫 - 财运亨通
        hualu_count = sum(1 for stars in all_stars.values() if "化禄" in stars["transform_stars"])
        if hualu_count >= 2:
            patterns.append(WealthPattern(
                pattern_name="化禄叠会格",
                description="财运亨通，财源广进，财富快速增长",
                score_bonus=12,
                characteristics=["财源广进", "财运亨通", "创富能力强"]
            ))

        # 太阳太阴同宫 - 财禄旺盛
        has_taiyang = any("太阳" in stars["main_stars"] for stars in all_stars.values())
        has_taiyin = any("太阴" in stars["main_stars"] for stars in all_stars.values())
        if has_taiyang and has_taiyin:
            patterns.append(WealthPattern(
                pattern_name="日月同照格",
                description="财禄旺盛，日主外财，月主内财，财运全面",
                score_bonus=10,
                characteristics=["外财旺盛", "内财充裕", "财运全面"]
            ))

        # 贪狼星入财帛宫 - 野心财运
        if "贪狼" in caibi_stars["main_stars"]:
            patterns.append(WealthPattern(
                pattern_name="贪狼入财格",
                description="野心与财运并存，敢于冒险，财富波动大",
                score_bonus=5,
                characteristics=["敢于冒险", "野心大", "财运波动"]
            ))

        # 紫微天府双星 - 富贵命
        has_ziwei = any("紫微" in stars["main_stars"] for stars in all_stars.values())
        if has_ziwei and has_tianfu:
            patterns.append(WealthPattern(
                pattern_name="紫微天府双贵格",
                description="富贵命格，有领导财运和社会地位",
                score_bonus=15,
                characteristics=["领导才能", "社会地位高", "财运亨通"]
            ))

        return patterns

    def _get_strength_level(self, score: int) -> str:
        """根据得分确定强弱等级"""
        if score >= 70:
            return "强"
        elif score >= 40:
            return "中"
        else:
            return "弱"

    def _get_wealth_level(self, score: int) -> str:
        """根据得分确定财富等级"""
        if score >= 90:
            return WealthLevel.TOP_RICH.value
        elif score >= 75:
            return WealthLevel.VERY_RICH.value
        elif score >= 60:
            return WealthLevel.MEDIUM_RICH.value
        elif score >= 45:
            return WealthLevel.SMALL_RICH.value
        elif score >= 30:
            return WealthLevel.NORMAL.value
        else:
            return WealthLevel.POOR.value

    def _calculate_total_score(self) -> int:
        """计算总财富得分"""
        total = 0
        for palace, weight in PALACE_WEIGHTS.items():
            score = self._get_palace_score(palace)
            total += score * weight
        return int(total)

    def _identify_advantages(self) -> List[str]:
        """识别财富优势"""
        advantages = []

        caibi = self._analyze_caibi_palace()
        tianzhai = self._analyze_tianzhai_palace()
        fude = self._analyze_fude_palace()

        if caibi.score >= 70:
            advantages.append("财帛宫强旺，正财运势佳，赚钱能力强")
        if tianzhai.score >= 70:
            advantages.append("田宅宫强旺，不动产运势佳，有置产能力")
        if fude.score >= 70:
            advantages.append("福德宫强旺，理财观念佳，善于规划财务")

        patterns = self._identify_wealth_patterns()
        for pattern in patterns:
            if pattern.score_bonus >= 10:
                advantages.append(f"形成{pattern.pattern_name}，{pattern.description}")

        # 检查化禄
        for palace_name in ["财帛宫", "田宅宫", "福德宫", "官禄宫"]:
            stars = self._classify_stars(palace_name)
            if "化禄" in stars["transform_stars"]:
                advantages.append(f"{palace_name}有化禄，财运亨通")

        return advantages if advantages else ["各宫位运势平衡"]

    def _identify_weaknesses(self) -> List[str]:
        """识别财富劣势"""
        weaknesses = []

        caibi = self._analyze_caibi_palace()
        tianzhai = self._analyze_tianzhai_palace()
        fude = self._analyze_fude_palace()

        if caibi.score < 40:
            weaknesses.append("财帛宫较弱，财运需加强，赚钱较辛苦")
        if tianzhai.score < 40:
            weaknesses.append("田宅宫较弱，不动产运势一般，不宜强求")
        if fude.score < 40:
            weaknesses.append("福德宫较弱，理财观念需调整")

        # 检查化忌
        for palace_name in ["财帛宫", "田宅宫", "福德宫", "官禄宫"]:
            stars = self._classify_stars(palace_name)
            if "化忌" in stars["transform_stars"]:
                weaknesses.append(f"{palace_name}有化忌，运势受阻，需注意化解")

        # 检查煞星
        for palace_name in ["财帛宫", "田宅宫"]:
            stars = self._classify_stars(palace_name)
            if len(stars["sha_stars"]) >= 2:
                weaknesses.append(f"{palace_name}多煞同宫，财运易有波动")

        return weaknesses if weaknesses else ["无明显劣势"]

    def _generate_recommendations(self, yearly_forecast: List[Dict]) -> List[str]:
        """生成财富建议"""
        recommendations = []

        caibi = self._analyze_caibi_palace()
        tianzhai = self._analyze_tianzhai_palace()
        fude = self._analyze_fude_palace()

        # 基于宫位分析的建议
        if caibi.score >= 70:
            recommendations.append("发挥财帛宫优势，积极进取，敢于把握财富机会")
        elif caibi.score < 40:
            recommendations.append("财帛宫较弱，宜稳扎稳打，通过技术或专业能力积累财富")

        if tianzhai.score >= 70:
            recommendations.append("田宅宫强旺，宜配置不动产，如房产、实体资产")
        elif tianzhai.score < 40:
            recommendations.append("田宅宫较弱，不宜过度投资房产，宜现金流管理为主")

        if fude.score >= 70:
            recommendations.append("福德宫强旺，宜做长期理财规划，如养老金、教育金")
        elif fude.score < 40:
            recommendations.append("福德宫较弱，投资需谨慎，避免高风险理财产品")

        # 基于流年预测的建议
        if yearly_forecast:
            current_year = yearly_forecast[0]
            year_wealth = current_year.wealth_score

            if year_wealth < 40:
                recommendations.append(f"流年{current_year.year}财运较弱，控制支出，谨慎投资")
            elif year_wealth >= 75:
                recommendations.append(f"流年{current_year.year}财运旺盛，可积极把握机会")

        # 通用建议
        recommendations.append("建议每月做好收支记录，养成理财习惯")
        recommendations.append("注意分散投资风险，不要把所有资金放在一个篮子里")

        return recommendations[:6]

    def _generate_investment_advice(self) -> Dict[str, str]:
        """生成投资建议"""
        advice = {}

        caibi_stars = self._classify_stars("财帛宫")
        tianzhai_stars = self._classify_stars("田宅宫")
        fude_stars = self._classify_stars("福德宫")

        # 低风险投资
        if "化忌" in caibi_stars["transform_stars"] or "地空" in caibi_stars["sha_stars"]:
            advice["低风险"] = "保守型理财，如定期存款、国债、货币基金"
        else:
            advice["低风险"] = "稳健型理财，如债券基金、混合基金"

        # 中风险投资
        if "天府" in tianzhai_stars["main_stars"] or "武曲" in caibi_stars["main_stars"]:
            advice["中风险"] = "进取型理财，如股票、基金、房产投资"
        else:
            advice["中风险"] = "平衡型理财，如指数基金、定投"

        # 高风险投资
        if "贪狼" in caibi_stars["main_stars"] and "化禄" in caibi_stars["transform_stars"]:
            advice["高风险"] = "激进型理财，如股票、期货、外汇，但需控制比例"
        else:
            advice["高风险"] = "适度参与高风险理财，不宜超过总资产的20%"

        # 不动产投资建议
        if tianzhai_stars["main_stars"] and "地空" not in tianzhai_stars["sha_stars"]:
            advice["不动产"] = "不动产运势佳，可考虑配置房产、写字楼等"
        else:
            advice["不动产"] = "不动产运势一般，建议谨慎，或选择核心地段"

        # 理财期限建议
        if "太阴" in fude_stars["main_stars"] or "天同" in fude_stars["main_stars"]:
            advice["理财期限"] = "适合长期理财规划，如5年以上的定投或保险"
        else:
            advice["理财期限"] = "中短期理财为主，3-5年周期较合适"

        return advice

    def _assess_risk(self) -> Dict[str, Any]:
        """风险评估"""
        risk_assessment = {
            "overall_risk_level": "中等",
            "risk_factors": [],
            "protective_factors": []
        }

        caibi_stars = self._classify_stars("财帛宫")
        tianzhai_stars = self._classify_stars("田宅宫")
        fude_stars = self._classify_stars("福德宫")

        # 风险因素
        if len(caibi_stars["sha_stars"]) >= 2:
            risk_assessment["risk_factors"].append("财帛宫多煞星，财务波动风险高")
        if "化忌" in caibi_stars["transform_stars"]:
            risk_assessment["risk_factors"].append("财帛宫化忌，财运易受阻")
        if "地空" in caibi_stars["sha_stars"] or "地劫" in caibi_stars["sha_stars"]:
            risk_assessment["risk_factors"].append("空劫同宫，财务易有空缺")

        # 保护因素
        if "禄存" in caibi_stars["auxiliary_stars"]:
            risk_assessment["protective_factors"].append("禄存星入财帛宫，有储蓄保障")
        if "天府" in tianzhai_stars["main_stars"]:
            risk_assessment["protective_factors"].append("天府星入田宅宫，有资产保护")
        if "化禄" in fude_stars["transform_stars"]:
            risk_assessment["protective_factors"].append("福德宫化禄，理财观念佳，风险意识强")

        # 综合风险等级
        risk_score = len(risk_assessment["risk_factors"]) - len(risk_assessment["protective_factors"])
        if risk_score <= -2:
            risk_assessment["overall_risk_level"] = "较低"
        elif risk_score >= 2:
            risk_assessment["overall_risk_level"] = "较高"
        else:
            risk_assessment["overall_risk_level"] = "中等"

        return risk_assessment

    async def analyze_wealth(self, years: int = 5) -> WealthReport:
        """
        完整财运分析

        Args:
            years: 预测年数

        Returns:
            WealthReport: 完整财富报告
        """
        # 分析各宫位
        caibi_palace = self._analyze_caibi_palace()
        tianzhai_palace = self._analyze_tianzhai_palace()
        fude_palace = self._analyze_fude_palace()
        guanlu_palace = self._analyze_guanlu_palace()

        # 计算总得分
        total_score = self._calculate_total_score()

        # 识别格局
        patterns = self._identify_wealth_patterns()

        # 格局加分
        pattern_bonus = sum(p.score_bonus for p in patterns)
        final_score = min(100, total_score + pattern_bonus)

        # 获取优势劣势
        advantages = self._identify_advantages()
        weaknesses = self._identify_weaknesses()

        # 获取流年预测
        from datetime import datetime
        from app.services.divination.agents.timing_agent import TimingAgent

        birth_info = self.chart.get("birth_info", {})
        current_year = datetime.now().year
        yearly_forecast = []

        try:
            timing_agent = TimingAgent(self.chart)

            for i in range(years):
                year = current_year + i
                year_fate = timing_agent.calculate_year_fate(year, birth_info.get("year", 1990))

                wealth_score = 50

                # 太岁关系影响
                if year_fate.tai_sui_relationship == "三合":
                    wealth_score += 10
                elif year_fate.tai_sui_relationship == "入本宫":
                    wealth_score += 15
                elif year_fate.tai_sui_relationship == "冲本宫":
                    wealth_score -= 10

                # 星曜影响
                for star in year_fate.stars:
                    if "化禄" in star:
                        wealth_score += 15
                    elif "化权" in star:
                        wealth_score += 10
                    elif "化科" in star:
                        wealth_score += 5
                    elif "化忌" in star:
                        wealth_score -= 10

                # 流曜影响
                liu_yao = year_fate.liu_yao
                for category, stars_list in liu_yao.items():
                    for star in stars_list:
                        if star in ["大耗", "小耗", "丧门"]:
                            wealth_score -= 8
                        elif star in ["青龙", "龙德", "天德"]:
                            wealth_score += 8

                wealth_score = max(0, min(100, wealth_score))

                # 生成建议
                if wealth_score >= 75:
                    advice = "财运旺盛，把握机遇，可主动出击"
                elif wealth_score >= 50:
                    advice = "财运平稳，宜守成，稳健投资"
                elif wealth_score >= 30:
                    advice = "财运较弱，注意节约，谨慎投资"
                else:
                    advice = "财运低迷，静待时机，避免风险"

                yearly_forecast.append(YearlyWealthForecast(
                    year=year,
                    wealth_score=wealth_score,
                    gan_zhi=year_fate.gan_zhi,
                    tai_sui_palace=year_fate.tai_sui_palace,
                    advice=advice,
                    opportunity_periods=[f"{year}年{year_fate.tai_sui_palace}"],
                    risk_periods=[],
                    recommended_actions=[advice]
                ))

        except Exception:
            # 回退方案
            for i in range(years):
                yearly_forecast.append(YearlyWealthForecast(
                    year=current_year + i,
                    wealth_score=60,
                    gan_zhi="",
                    tai_sui_palace="",
                    advice="财运平稳，顺势而为",
                    opportunity_periods=[],
                    risk_periods=[],
                    recommended_actions=["保持稳健理财"]
                ))

        # 生成建议
        recommendations = self._generate_recommendations(yearly_forecast)

        # 生成投资建议
        investment_advice = self._generate_investment_advice()

        # 风险评估
        risk_assessment = self._assess_risk()

        return WealthReport(
            total_wealth_score=final_score,
            wealth_level=self._get_wealth_level(final_score),
            caibi_palace=caibi_palace,
            tianzhai_palace=tianzhai_palace,
            fude_palace=fude_palace,
            guanlu_palace=guanlu_palace,
            wealth_patterns=patterns,
            advantages=advantages,
            weaknesses=weaknesses,
            yearly_forecast=yearly_forecast,
            recommendations=recommendations,
            investment_advice=investment_advice,
            risk_assessment=risk_assessment
        )

    def analyze_wealth_sync(self, years: int = 5) -> WealthReport:
        """同步版本的财运分析"""
        import asyncio
        return asyncio.run(self.analyze_wealth(years))

    def to_dict(self, report: WealthReport) -> Dict[str, Any]:
        """将报告转换为字典"""
        return {
            "wealth_score": report.total_wealth_score,
            "wealth_level": report.wealth_level,
            "caibi_palace": {
                "palace_name": report.caibi_palace.palace_name,
                "score": report.caibi_palace.score,
                "strength_level": report.caibi_palace.strength_level,
                "main_stars": report.caibi_palace.main_stars,
                "auxiliary_stars": report.caibi_palace.auxiliary_stars,
                "sha_stars": report.caibi_palace.sha_stars,
                "transform_stars": report.caibi_palace.transform_stars,
                "interpretation": report.caibi_palace.interpretation,
                "wealth_indicator": report.caibi_palace.wealth_indicator,
                "risk_factors": report.caibi_palace.risk_factors,
                "opportunity_factors": report.caibi_palace.opportunity_factors
            },
            "tianzhai_palace": {
                "palace_name": report.tianzhai_palace.palace_name,
                "score": report.tianzhai_palace.score,
                "strength_level": report.tianzhai_palace.strength_level,
                "main_stars": report.tianzhai_palace.main_stars,
                "auxiliary_stars": report.tianzhai_palace.auxiliary_stars,
                "sha_stars": report.tianzhai_palace.sha_stars,
                "transform_stars": report.tianzhai_palace.transform_stars,
                "interpretation": report.tianzhai_palace.interpretation,
                "wealth_indicator": report.tianzhai_palace.wealth_indicator,
                "risk_factors": report.tianzhai_palace.risk_factors,
                "opportunity_factors": report.tianzhai_palace.opportunity_factors
            },
            "fude_palace": {
                "palace_name": report.fude_palace.palace_name,
                "score": report.fude_palace.score,
                "strength_level": report.fude_palace.strength_level,
                "main_stars": report.fude_palace.main_stars,
                "auxiliary_stars": report.fude_palace.auxiliary_stars,
                "sha_stars": report.fude_palace.sha_stars,
                "transform_stars": report.fude_palace.transform_stars,
                "interpretation": report.fude_palace.interpretation,
                "wealth_indicator": report.fude_palace.wealth_indicator,
                "risk_factors": report.fude_palace.risk_factors,
                "opportunity_factors": report.fude_palace.opportunity_factors
            },
            "guanlu_palace": {
                "palace_name": report.guanlu_palace.palace_name,
                "score": report.guanlu_palace.score,
                "strength_level": report.guanlu_palace.strength_level,
                "main_stars": report.guanlu_palace.main_stars,
                "auxiliary_stars": report.guanlu_palace.auxiliary_stars,
                "sha_stars": report.guanlu_palace.sha_stars,
                "transform_stars": report.guanlu_palace.transform_stars,
                "interpretation": report.guanlu_palace.interpretation,
                "wealth_indicator": report.guanlu_palace.wealth_indicator,
                "risk_factors": report.guanlu_palace.risk_factors,
                "opportunity_factors": report.guanlu_palace.opportunity_factors
            },
            "wealth_patterns": [
                {
                    "pattern_name": p.pattern_name,
                    "description": p.description,
                    "score_bonus": p.score_bonus,
                    "characteristics": p.characteristics
                }
                for p in report.wealth_patterns
            ],
            "wealth_advantages": report.advantages,
            "wealth_weaknesses": report.weaknesses,
            "yearly_forecast": [
                {
                    "year": f.year,
                    "wealth": f.wealth_score,
                    "gan_zhi": f.gan_zhi,
                    "tai_sui_palace": f.tai_sui_palace,
                    "advice": f.advice,
                    "opportunity_periods": f.opportunity_periods,
                    "risk_periods": f.risk_periods,
                    "recommended_actions": f.recommended_actions
                }
                for f in report.yearly_forecast
            ],
            "recommendations": report.recommendations,
            "investment_advice": report.investment_advice,
            "risk_assessment": report.risk_assessment
        }


# ============ LLM增强分析 ============

class LLMWealthAnalyzer:
    """LLM财富分析增强器"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data
        self.base_analyzer = WealthAgent(chart_data)

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度财富分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            LLM分析结果
        """
        from ....utils.llm_client import LLMClient

        # 先获取基础分析
        base_report = await self.base_analyzer.analyze_wealth()

        # 构建提示词
        user_prompt = self._build_llm_prompt(base_report, question)

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature)

        return result

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是紫微斗数财运分析专家。你的任务是：

1. 基于命盘数据分析财运
2. 解读各宫位星曜组合
3. 识别财富格局和运势
4. 提供个性化理财建议

请用JSON格式返回分析结果，包括：
- 财运特征描述
- 星曜组合解读
- 财富格局分析
- 具体理财建议
- 注意事项

注意：
- 结合传统紫微斗数和现代理财观念
- 建议要具体可操作
- 风险提示要明确"""

    def _build_llm_prompt(
        self,
        base_report: WealthReport,
        question: Optional[str]
    ) -> str:
        """构建LLM提示词"""
        prompt_parts = ["# 命盘财运分析请求\n"]

        # 基础信息
        prompt_parts.append(f"## 基础信息")
        prompt_parts.append(f"- 总财富得分: {base_report.total_wealth_score}")
        prompt_parts.append(f"- 财富等级: {base_report.wealth_level}")
        prompt_parts.append("")

        # 各宫位分析
        for palace in [base_report.caibi_palace, base_report.tianzhai_palace,
                       base_report.fude_palace, base_report.guanlu_palace]:
            prompt_parts.append(f"## {palace.palace_name} (得分: {palace.score})")
            prompt_parts.append(f"- 主星: {', '.join(palace.main_stars) if palace.main_stars else '无'}")
            prompt_parts.append(f"- 辅星: {', '.join(palace.auxiliary_stars) if palace.auxiliary_stars else '无'}")
            prompt_parts.append(f"- 煞星: {', '.join(palace.sha_stars) if palace.sha_stars else '无'}")
            prompt_parts.append(f"- 化曜: {', '.join(palace.transform_stars) if palace.transform_stars else '无'}")
            prompt_parts.append(f"- 财富指示: {palace.wealth_indicator}")
            if palace.opportunity_factors:
                prompt_parts.append(f"- 有利因素: {'; '.join(palace.opportunity_factors)}")
            if palace.risk_factors:
                prompt_parts.append(f"- 风险因素: {'; '.join(palace.risk_factors)}")
            prompt_parts.append("")

        # 财富格局
        if base_report.wealth_patterns:
            prompt_parts.append("## 财富格局")
            for pattern in base_report.wealth_patterns:
                prompt_parts.append(f"- {pattern.pattern_name}: {pattern.description}")
            prompt_parts.append("")

        # 流年预测
        if base_report.yearly_forecast:
            prompt_parts.append("## 流年财运预测")
            for forecast in base_report.yearly_forecast[:3]:
                prompt_parts.append(f"- {forecast.year}年: {forecast.advice}")
            prompt_parts.append("")

        # 投资建议
        if base_report.investment_advice:
            prompt_parts.append("## 投资建议")
            for category, advice in base_report.investment_advice.items():
                prompt_parts.append(f"- {category}: {advice}")
            prompt_parts.append("")

        # 特定问题
        if question:
            prompt_parts.append(f"## 特定问题\n{question}")

        return "\n".join(prompt_parts)

    def analyze_with_llm_sync(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """同步版本"""
        import asyncio
        return asyncio.run(self.analyze_with_llm(question, temperature))


async def analyze_wealth_async(
    chart_data: Dict[str, Any],
    years: int = 5
) -> Dict[str, Any]:
    """
    异步财运分析

    Args:
        chart_data: 命盘数据
        years: 预测年数

    Returns:
        财富分析结果字典
    """
    agent = WealthAgent(chart_data)
    report = await agent.analyze_wealth(years)
    return agent.to_dict(report)


def analyze_wealth_sync(
    chart_data: Dict[str, Any],
    years: int = 5
) -> Dict[str, Any]:
    """同步财运分析"""
    import asyncio
    return asyncio.run(analyze_wealth_async(chart_data, years))


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
                    {"name": "紫微", "type": "正曜", "level": "旺"}
                ]},
                "财帛宫": {"branch": "辰", "tiangan": "戊", "score": {"total": 75}, "stars": [
                    {"name": "武曲", "type": "正曜", "level": "旺"},
                    {"name": "天府", "type": "正曜", "level": "旺"},
                    {"name": "化禄", "type": "化曜", "level": "庙"}
                ]},
                "田宅宫": {"branch": "酉", "tiangan": "癸", "score": {"total": 70}, "stars": [
                    {"name": "天府", "type": "正曜", "level": "旺"},
                    {"name": "禄存", "type": "辅星", "level": "旺"}
                ]},
                "福德宫": {"branch": "亥", "tiangan": "乙", "score": {"total": 65}, "stars": [
                    {"name": "天梁", "type": "正曜", "level": "旺"},
                    {"name": "太阴", "type": "正曜", "level": "庙"}
                ]},
                "官禄宫": {"branch": "申", "tiangan": "壬", "score": {"total": 72}, "stars": [
                    {"name": "太阳", "type": "正曜", "level": "旺"},
                    {"name": "化权", "type": "化曜", "level": "旺"}
                ]}
            }
        }

        agent = WealthAgent(test_chart)
        report = await agent.analyze_wealth(years=5)

        print("=" * 60)
        print("财运分析报告")
        print("=" * 60)
        print(f"总财富得分: {report.total_wealth_score}")
        print(f"财富等级: {report.wealth_level}")
        print()
        print("财帛宫分析:")
        print(f"  得分: {report.caibi_palace.score}")
        print(f"  主星: {', '.join(report.caibi_palace.main_stars)}")
        print(f"  财富指示: {report.caibi_palace.wealth_indicator}")
        print()
        print("田宅宫分析:")
        print(f"  得分: {report.tianzhai_palace.score}")
        print(f"  主星: {', '.join(report.tianzhai_palace.main_stars)}")
        print()
        print("财富格局:")
        for pattern in report.wealth_patterns:
            print(f"  {pattern.pattern_name}: {pattern.description}")
        print()
        print("财富优势:")
        for adv in report.advantages:
            print(f"  - {adv}")
        print()
        print("财富劣势:")
        for weak in report.weaknesses:
            print(f"  - {weak}")
        print()
        print("投资建议:")
        for category, advice in report.investment_advice.items():
            print(f"  {category}: {advice}")
        print()
        print("流年预测:")
        for forecast in report.yearly_forecast:
            print(f"  {forecast.year}年: {forecast.advice}")
        print()
        print("风险评估:")
        print(f"  总体风险等级: {report.risk_assessment['overall_risk_level']}")
        print(f"  风险因素: {report.risk_assessment['risk_factors']}")
        print(f"  保护因素: {report.risk_assessment['protective_factors']}")

    asyncio.run(main())
