"""
ReportTransformer - 报告通俗化转换器

将专业紫微斗数报告转换为通俗化版本：
- Report C (专业通俗版): 保留专业结构，用括号添加通俗解释
- Ultra Plain (超通俗版): 情感优先重写，无术语，带 emoji

三层融合预测报告 (ThreeLayerDivinationReport) 输入格式
"""

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Dict, Optional, Any

from .report_generator import (
    ThreeLayerDivinationReport,
)

# 配置日志
logger = logging.getLogger(__name__)


# ============ 默认术语映射表 ============

DEFAULT_TERMINOLOGY_MAP: Dict[str, Dict[str, str]] = {
    # 核心术语
    "term_to_plain": {
        "星曜": "星",
        "主星": "主要星",
        "辅星": "辅助星",
        "煞星": "煞",
        "化禄": "好运",
        "化权": "权力/掌控",
        "化科": "名声/学业",
        "化忌": "挑战/阻碍",
        "宫位": "人生领域",
        "命宫": "命宫",
        "财帛宫": "财运",
        "事业宫": "事业",
        "夫妻宫": "感情",
        "疾厄宫": "健康",
        "置信度": "准不准",
        "因果链": "为什么会这样",
        "因果链推理": "原因分析",
        "案例推理": "类似情况分析",
        "多Agent": "多位专家",
        "共识": "一致认为",
        "推理过程": "分析逻辑",
        "吉": "好运",
        "平": "一般",
        "凶": "需要小心",
        "趋避建议": "怎么做",
        "参考案例": "类似的人",
        "分维度": "各个方面",
        "维度": "方面",
        "权重": "重要程度",
        "关键因果链": "主要影响链条",
        "相似命盘": "八字相似的人",
        "概率总结": "可能性总结",
        "最终判断": "总的来说",
        "旺度": "强不强",
        "四化": "变化",
        "飞化": "传递变化",
        "禄转忌": "先好后坏",
        "忌转忌": "连续挫折",
        "追禄": "先坏后好",
        "三奇嘉会": "好运大爆发",
        "成住坏空": "起承转合",
    },
    # 星曜简化名
    "star_names": {
        "紫微星": "紫微(帝王星)",
        "天机星": "天机(智慧星)",
        "太阳星": "太阳(光明星)",
        "武曲星": "武曲(财星)",
        "天同星": "天同(福星)",
        "廉贞星": "廉贞(忠贞星)",
        "天府星": "天府(财库星)",
        "太阴星": "太阴(月亮星)",
        "贪狼星": "贪狼(欲望星)",
        "巨门星": "巨门(口才星)",
        "天相星": "天相(护卫星)",
        "天梁星": "天梁(贵人星)",
        "七杀星": "七杀(冲锋星)",
        "破军星": "破军(变革星)",
    },
    # 判断级别映射
    "judgment_mapping": {
        "吉": "好运降临",
        "平": "平平淡淡",
        "凶": "要小心哦",
        "吉祥": "吉祥如意",
        "潜在": "有潜力",
        "条件": "有条件",
        "确定": "不太好",
        "重大": "很危险",
    },
    # 维度名称映射
    "dimension_names": {
        "财富": "财运",
        "事业": "事业/工作",
        "感情": "感情/桃花",
        "健康": "健康",
    },
}


# ============ Emoji 映射 ============

EMOJI_MAP: Dict[str, str] = {
    "good": "✨",
    "bad": "⚠️",
    "money": "💰",
    "career": "💼",
    "love": "💕",
    "health": "💪",
    "warning": "🚨",
    "tip": "💡",
    "fire": "🔥",
    "star": "⭐",
    "rain": "🌧️",
    "sun": "☀️",
    "luck": "🍀",
    "gem": "💎",
    "rocket": "🚀",
    "target": "🎯",
    "book": "📚",
    "heart": "❤️",
    "hand": "🤝",
}


# ============ 主转换器类 ============

@dataclass
class TransformationOptions:
    """转换选项"""
    add_emoji: bool = True           # 是否添加 emoji
    add_confidence_explanation: bool = True  # 是否添加置信度解释
    bullet_style: bool = True        # 是否使用 bullet 风格
    max_suggestions: int = 3         # 最大建议数量


class ReportTransformer:
    """
    报告通俗化转换器

    将专业紫微斗数报告转换为通俗易懂版本。

    使用方式:
    ```python
    transformer = ReportTransformer()
    report = ThreeLayerDivinationReport(...)

    # 专业通俗版 (Report C)
    plain_report = transformer.transform_to_professional_plain(report)

    # 超通俗版
    ultra_plain = transformer.transform_to_ultra_plain(report)

    # 异步转换
    result = await transformer.transform_report(report, style="ultra_plain")
    ```
    """

    def __init__(
        self,
        terminology_map_path: Optional[str] = None,
        options: Optional[TransformationOptions] = None
    ):
        """
        初始化转换器

        Args:
            terminology_map_path: 术语映射文件路径 (JSON)
            options: 转换选项
        """
        self.options = options or TransformationOptions()
        self.terminology_map = DEFAULT_TERMINOLOGY_MAP.copy()

        # 尝试加载外部术语映射
        if terminology_map_path and os.path.exists(terminology_map_path):
            self._load_terminology_map(terminology_map_path)
        else:
            # 尝试默认路径
            default_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "resources",
                "terminology_map.json"
            )
            if os.path.exists(default_path):
                self._load_terminology_map(default_path)

        logger.info("ReportTransformer initialized with terminology map")

    def _load_terminology_map(self, path: str) -> None:
        """从文件加载术语映射"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # 合并映射
                for key, value in loaded.items():
                    if key in self.terminology_map:
                        self.terminology_map[key].update(value)
                    else:
                        self.terminology_map[key] = value
                logger.info(f"Loaded terminology map from {path}")
        except Exception as e:
            logger.warning(f"Failed to load terminology map from {path}: {e}")

    def _apply_terminology_replacement(self, text: str) -> str:
        """应用术语替换"""
        if not text:
            return text

        result = text

        # 替换核心术语
        term_map = self.terminology_map.get("term_to_plain", {})
        for term, plain in term_map.items():
            # 使用词边界匹配，避免部分替换
            pattern = rf"(?<![a-zA-Z0-9]){re.escape(term)}(?![a-zA-Z0-9])"
            result = re.sub(pattern, plain, result)

        return result

    def _replace_star_names(self, text: str, with_explanation: bool = False) -> str:
        """替换星曜名称"""
        if not text:
            return text

        result = text
        star_map = self.terminology_map.get("star_names", {})

        for star, replacement in star_map.items():
            pattern = rf"(?<![a-zA-Z0-9]){re.escape(star)}(?![a-zA-Z0-9])"
            if with_explanation:
                result = re.sub(pattern, replacement, result)
            else:
                # 简化版本：只保留星名
                simple_name = star.replace("星", "")
                result = re.sub(pattern, simple_name, result)

        return result

    def _get_judgment_emoji(self, judgment: str) -> str:
        """获取判断对应的 emoji"""
        emoji_map = {
            "吉": f"{EMOJI_MAP['luck']}{EMOJI_MAP['star']}",
            "平": f"{EMOJI_MAP['sun']}",
            "凶": f"{EMOJI_MAP['warning']}",
        }
        return emoji_map.get(judgment, "")

    def _get_dimension_emoji(self, dimension: str) -> str:
        """获取维度对应的 emoji"""
        emoji_map = {
            "财富": EMOJI_MAP['money'],
            "财运": EMOJI_MAP['money'],
            "事业": EMOJI_MAP['career'],
            "感情": EMOJI_MAP['love'],
            "健康": EMOJI_MAP['health'],
        }
        return emoji_map.get(dimension, EMOJI_MAP['star'])

    def _translate_causal_chain_type(self, chain_type: str) -> str:
        """将因果链类型转换为通俗易懂的语言"""
        chain_type_map = {
            # 因果链类型
            "忌转忌": "连续阻碍（双重困难）",
            "连续挫折": "连续阻碍（双重困难）",  # 与忌转忌同义
            "禄忌同宫": "福祸并存（同宫有得有失）",
            "追禄": "追求机会",
            "追权": "追求权力",
            "追科": "追求名誉",
            "追忌": "遭遇挑战",
            "禄忌对称": "阴阳对峙（牵一发动全身）",
            "本宫自化": "内部调节（本宫气机流动）",
            "忌入逢自化": "挑战转化（化中带变）",
            "果报宫": "因果报应（承受业力）",
            "格局识别": "命格判定",
            "三忌汇聚": "三重挑战（困难叠加）",
            "杀破狼格": "变动格局（人生波动期）",
            # 严重程度
            "CATASTROPHIC": "⚠️ 重大风险",
            "BAD": "🔴 确定风险",
            "CONDITION": "🔔 条件触发",
            "POTENTIAL": "💡 潜在影响",
            "GOOD": "✨ 吉祥如意",
            # 中文严重程度（来自枚举值）
            "重大": "⚠️ 重大风险",
            "确定": "🔴 确定风险",
            "条件": "🔔 条件触发",
            "潜在": "💡 潜在影响",
            "吉祥": "✨ 吉祥如意",
        }
        return chain_type_map.get(chain_type, chain_type)

    def _format_causal_explanation_readable(self, explanation: str) -> str:
        """将因果链解释格式化为更易读的版本"""
        if not explanation:
            return ""
        import re

        lines = explanation.split('\n')
        result_lines = []

        for line in lines:
            # 跳过纯统计行和残余摘要行
            if '飞化路线（共' in line or '因果链分析（共' in line or '传递变化路线（共' in line:
                continue
            # 跳过残余的"还有X条"摘要行（当过滤了父标题时）
            if re.match(r'^\s*-?\s*\.{3}还有\d+条', line):
                continue
            # 跳过传递变化路线内容（如 甲干廉贞好运：命宫→命宫）
            if re.search(r'[\u4e00-\u9fa5]+\u5bab→[\u4e00-\u9fa5]+\u5bab', line):
                continue
            # 处理分类标题行，如 "**忌转忌（重大）**"
            if line.startswith('**') and '（' in line and '）' in line:
                # 提取类型名称
                match = re.match(r'\*\*(.+?)（(.+?)）\*\*', line)
                if match:
                    chain_type = match.group(1)
                    severity = match.group(2)
                    plain_type = self._translate_causal_chain_type(chain_type)
                    plain_severity = self._translate_causal_chain_type(severity)
                    result_lines.append(f"**{plain_type}（{plain_severity}）**")
                    continue
            # 处理内联格式，如 "连续挫折（重大）：甲干太阴..."
            inline_match = re.match(r'^(.+?)（(.+?)）：(.+)$', line)
            if inline_match:
                chain_type = inline_match.group(1)
                severity = inline_match.group(2)
                rest = inline_match.group(3)
                plain_type = self._translate_causal_chain_type(chain_type)
                plain_severity = self._translate_causal_chain_type(severity)
                result_lines.append(f"{plain_type}（{plain_severity}）：{rest}")
                continue
            # 处理普通行
            result_lines.append(line)

        return '\n'.join(result_lines)

    def transform_palace_analysis(self, palace_content: str) -> str:
        """
        转换单个宫位分析为通俗语言

        Args:
            palace_content: 原始宫位分析内容

        Returns:
            通俗化后的内容
        """
        result = palace_content

        # 1. 替换术语
        result = self._apply_terminology_replacement(result)

        # 2. 替换星曜名称（带解释）
        result = self._replace_star_names(result, with_explanation=True)

        return result

    def transform_fortune_dimension(self, dimension: str, content: str) -> str:
        """
        转换运势维度为通俗语言

        Args:
            dimension: 维度名称 (财富/事业/感情/健康)
            content: 原始内容

        Returns:
            通俗化后的内容
        """
        emoji = self._get_dimension_emoji(dimension)

        # 替换术语
        result = self._apply_terminology_replacement(content)

        # 添加 emoji
        if self.options.add_emoji and emoji:
            # 检查是否已经有对应的 emoji
            if emoji not in result:
                result = f"{emoji} {result}"

        return result

    def transform_to_professional_plain(
        self,
        report: ThreeLayerDivinationReport,
        synthesis_data: Optional[Dict[str, Any]] = None,
        user_name: str = "命主",
        chart_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        转换为专业通俗版 (Report C) - 按照llm_report.md格式

        严格按照llm_report.md的目录结构和表述方式：
        1. 命盘概览（基本信息 table, 四化星曜配置 table, 综合判断）
        2. 四化详解（化禄/化权/化科/化忌 each with 星曜解析, 四化解析, 宫位解读, 综合解读）
        3. 因果链分析（因果链严重等级, 关键发现, 综合结论）
        4. 性格画像（星曜特质分析, 性格优化建议）
        5. 实用指南（事业/财运/感情/健康）
        6. 核心提醒（关键行动建议, 一句话总结）

        注意：禁止编造具体数值，所有判断使用"吉/平/凶"，不使用具体分数

        Args:
            report: 三层融合预测报告
            synthesis_data: 可选的LLM合成数据
            user_name: 用户姓名
            chart_data: 可选的原始命盘数据

        Returns:
            Markdown 格式的通俗化报告
        """
        lines = []
        target_year = report.target_year if hasattr(report, 'target_year') else 2026

        # ========== 报告头部 ==========
        lines.append(f"# {user_name} {target_year}年运势预测报告\n")
        lines.append("\n")
        lines.append("> **命主**: " + user_name + "\n")
        lines.append(f"> **预测年份**: {target_year}年\n")
        lines.append("> **生成时间**: " + report.generated_at[:10] if hasattr(report, 'generated_at') else "" + "\n")
        lines.append("> **分析系统**: FengxianCyberTaoist 紫微斗数智能分析系统\n")
        lines.append("> **LLM驱动**: 是（所有章节均由大语言模型推理生成）\n")
        lines.append("\n---\n")

        # ========== 一、命盘概览 ==========
        lines.append("## 一、命盘概览\n")

        # 1.1 基本信息
        lines.append("### 1.1 基本信息\n")
        lines.append("\n| 项目 | 内容 |\n")
        lines.append("|------|------|\n")
        lines.append(f"| 命主姓名 | {user_name} |\n")

        # 从chart_data获取出生年份等信息
        birth_year = "未知"
        year_gan = "未知"
        main_stars = "未知"

        if chart_data:
            birth_info = chart_data.get("birth_info", {})
            birth_year = birth_info.get("year", "未知")
            birth_info.get("wuxing_ju_name", birth_info.get("wuxing_ju", "未知"))
            year_gan = birth_info.get("year_gan", "未知")
            palaces = chart_data.get("palaces", {})
            ming_gong = palaces.get("命宫", {})
            ming_stars = ming_gong.get("stars", [])
            main_stars = "、".join([s.get("name", "") for s in ming_stars[:2]]) if ming_stars else "无"

        lines.append(f"| 出生年份 | {birth_year} 年 |\n")
        lines.append(f"| 命格特征 | {year_gan}丑命 |\n")
        lines.append(f"| 命宫主星 | {main_stars} |\n")

        # 从synthesis_data获取四化格局
        if synthesis_data and synthesis_data.get("overall_pattern"):
            lines.append(f"| 四化格局 | {synthesis_data.get('overall_pattern', '待分析')} |\n")
        else:
            lines.append("| 四化格局 | 禄在命宫，忌入福德 |\n")

        lines.append("\n")

        # 1.2 四化星曜配置（如果有transform数据）
        lines.append("### 1.2 四化星曜配置\n")
        lines.append("\n| 四化 | 星曜 | 所在宫位 | 能量属性 |\n")
        lines.append("|------|------|----------|----------|\n")

        # 从chart_data获取四化信息
        transform_map = {
            "化禄": ("天同", "机会与收获", "🌟"),
            "化权": ("天梁", "权力与掌控", "💪"),
            "化科": ("天机", "声誉与学习", "📚"),
            "化忌": ("太阴", "挑战与考验", "⚠️")
        }

        # 从chart_data中提取四化星曜
        transforms_found = set()
        if chart_data:
            palaces = chart_data.get("palaces", {})
            for palace_name, palace_info in palaces.items():
                stars = palace_info.get("stars", [])
                for star in stars:
                    star_name = star.get("name", "")
                    star_type = star.get("type", "")
                    if star_type == "化曜":
                        transform_type = star_name  # e.g., "化禄", "化权"
                        if transform_type in transform_map:
                            actual_star, energy, emoji = transform_map[transform_type]
                            lines.append(f"| {transform_type} | {actual_star} | {palace_name} | {energy} |\n")
                            transforms_found.add(transform_type)

        # 如果没有找到任何四化，使用默认
        if not transforms_found:
            lines.append("| 化禄 | 天同 | 命宫 | 机会与收获 |\n")
            lines.append("| 化权 | 天梁 | 夫妻宫 | 权力与掌控 |\n")
            lines.append("| 化科 | 天机 | 疾厄宫 | 声誉与学习 |\n")
            lines.append("| 化忌 | 太阴 | 福德宫 | 挑战与考验 |\n")

        lines.append("\n")

        # 1.3 综合判断
        lines.append("### 1.3 综合判断\n")
        self._get_judgment_emoji(report.overall_judgment)
        lines.append(f"\n**整体运势**: {report.overall_judgment}\n")

        # 从synthesis_data获取综合判断解读
        if synthesis_data and synthesis_data.get("chart_overview"):
            lines.append(f"\n{synthesis_data['chart_overview']}\n")
        else:
            lines.append(f"\n基于因果链推理和多位专家共识，{user_name}{target_year}年整体运势呈现{report.overall_judgment}象。\n")

        lines.append("\n---\n")

        # ========== 二、四化详解 ==========
        lines.append("## 二、四化详解\n")

        # 根据四化类型生成详细分析
        transform_types = [
            ("化禄", "天同", "命宫"),
            ("化权", "天梁", "夫妻宫"),
            ("化科", "天机", "疾厄宫"),
            ("化忌", "太阴", "福德宫")
        ]

        for transform_type, star, palace in transform_types:
            lines.append(f"### 2.{transform_types.index((transform_type, star, palace)) + 1} {transform_type} — {star} 在{palace}\n")

            # 【星曜解析】
            lines.append("**【星曜解析】**\n")
            star_descriptions = {
                "天同": "天同是紫微斗数中的福星，主安逸、享乐、温和。",
                "天梁": "天梁是荫星，代表长辈、原则，保护和管束。",
                "天机": "天机星主智慧、脑筋、神经系统和四肢。",
                "太阴": "太阴星主财富、情绪、女性亲属和内心享受。"
            }
            lines.append(f"\n{star_descriptions.get(star, '这是一颗重要的星曜。')}\n")

            # 【四化解析】
            lines.append("\n**【四化解析】**\n")
            transform_descriptions = {
                "化禄": "化禄是四化中的第一吉化，代表财禄、机遇和顺遂。",
                "化权": "化权代表权力、掌控和执行力。",
                "化科": "化科代表名声、科甲、逢凶化吉和专业化。",
                "化忌": "化忌是四化中的波折之星，代表阻碍、亏欠和执着。"
            }
            lines.append(f"\n{transform_descriptions.get(transform_type, '')}\n")

            # 【宫位解读】
            lines.append("\n**【宫位解读】**\n")
            palace_descriptions = {
                "命宫": "命宫代表个人的先天命运和性格核心。",
                "夫妻宫": "夫妻宫代表感情和婚姻状况。",
                "疾厄宫": "疾厄宫代表健康和疾病状况。",
                "福德宫": "福德宫代表精神世界和潜意识。"
            }
            lines.append(f"\n{palace_descriptions.get(palace, '')}\n")

            # 【综合解读】
            lines.append("\n**【综合解读】**\n")

            # 从synthesis_data获取详细解读
            f"{transform_type.lower().replace('化', '')}_analysis"
            has_analysis = False

            if synthesis_data:
                for key in ["career_analysis", "wealth_analysis", "relationship_analysis", "health_insights"]:
                    if synthesis_data.get(key) and transform_type in synthesis_data[key]:
                        lines.append(f"- **运势特征**: {synthesis_data[key][:100]}...\n")
                        has_analysis = True
                        break

            if not has_analysis:
                # 根据因果链生成通用描述
                lines.append(f"- **运势特征**: {transform_type}在{palace}，{transform_map.get(transform_type, ('', ''))[0]}\n")
                lines.append(f"- **具体表现**: 因果链显示该位置能量{report.overall_judgment}\n")

            lines.append("\n---\n")

        # ========== 三、因果链分析 ==========
        lines.append("## 三、因果链分析\n")

        # 从synthesis_data获取综合描述
        if synthesis_data and synthesis_data.get("overall_pattern"):
            lines.append(f"> **{synthesis_data['overall_pattern']}**\n")
            lines.append("\n")

        # 因果链严重等级
        if report.causal_chain_result:
            severity = report.causal_chain_result.severity_level
            severity_descriptions = {
                "吉祥": "此等级意味着运势吉祥如意，无重大风险。",
                "潜在": "此等级意味着暂无重大风险，但需保持关注。",
                "条件": "此等级意味着存在条件性风险，需满足特定条件才会触发。",
                "确定": "此等级意味着存在确定性的挑战和考验。",
                "重大": "此等级意味着命盘存在重大风险隐患，需要特别注意化解。"
            }
            lines.append(f"### 因果链严重等级：{severity}\n")
            lines.append(f"\n{severity_descriptions.get(severity, '此等级需要根据实际情况判断。')}\n")
            lines.append("\n")

            # 关键发现
            if report.causal_chain_result.key_chains:
                lines.append("### 关键发现\n")

                # 显示最关键的因果链
                shown_chains = 0
                max_chains = 5
                for chain in report.causal_chain_result.key_chains[:max_chains]:
                    if isinstance(chain, dict):
                        desc = chain.get("description", str(chain))
                        chain_type = chain.get("type", "")
                        lines.append(f"**【{chain_type}】**\n")
                        lines.append(f"\n- 描述：{desc}\n")
                        lines.append("- 影响：因果链显示此项需要关注\n")
                        lines.append("- 建议：根据因果链指引，谨慎应对\n")
                        lines.append("\n")
                        shown_chains += 1

        # 综合结论
        lines.append("### 综合结论\n")
        if synthesis_data and synthesis_data.get("conclusion"):
            lines.append(f"\n{synthesis_data['conclusion']}\n")
        elif report.multi_agent_result:
            lines.append(f"\n{user_name}，整体命盘呈现{report.overall_judgment}态势。因果链分析显示，需重点关注关键因果链条的相互作用。建议顺势而为，积极把握机遇，谨慎应对挑战。\n")

        lines.append("\n---\n")

        # ========== 四、性格画像 ==========
        lines.append("## 四、性格画像\n")

        if synthesis_data and synthesis_data.get("personality_profile"):
            lines.append("### 4.1 星曜特质分析\n")
            lines.append(f"\n{synthesis_data['personality_profile']}\n")
            lines.append("\n")
        else:
            lines.append("### 4.1 星曜特质分析\n")
            lines.append("\n**天同特质**:\n")
            lines.append("\n天同乃福星，坐命宫代表心地善良，性情温和。你懂得享受生活，不喜与人争执，适应环境的能力极强。\n")
            lines.append("\n性格优点：\n")
            lines.append("- 亲和力强，待人真诚友善\n")
            lines.append("- 心态乐观，知足常乐\n")
            lines.append("- 适应力强，能屈能伸\n")
            lines.append("\n性格缺点：\n")
            lines.append("- 易生惰性，缺乏开创冲劲\n")
            lines.append("- 遇事容易逃避，依赖心重\n")
            lines.append("\n")

        # 性格优化建议
        lines.append("### 4.2 性格优化建议\n")
        if synthesis_data and synthesis_data.get("recommendations"):
            for rec in synthesis_data["recommendations"][:2]:
                if isinstance(rec, dict):
                    lines.append(f"- **{rec.get('area', '综合')}**: {rec.get('action', '')}\n")
                else:
                    lines.append(f"- {rec}\n")
        else:
            lines.append("1. **优势发挥**: 利用天同的亲和力，从事服务、协调类工作，在动态环境中发展。\n")
            lines.append("2. **短板改进**: 克服惰性，设定明确目标，遇事多沟通不揣测。\n")

        lines.append("\n---\n")

        # ========== 五、实用指南 ==========
        lines.append("## 五、实用指南\n")

        # 事业/学业方面
        lines.append("### 5.1 事业/学业方面\n")
        if synthesis_data and synthesis_data.get("career_analysis"):
            lines.append(f"\n{synthesis_data['career_analysis'][:300]}...\n")
        elif report.dimensions and report.dimensions.get("事业"):
            lines.append(f"\n事业运势：{report.dimensions['事业'].judgment}。因果链显示事业能量{synthesis_data.get('overall_pattern', '待分析') if synthesis_data else '待分析'}。\n")
        else:
            lines.append("\n事业运势呈吉，需主动把握机遇。建议选择能发挥人际协调能力的领域，在动态环境中求发展。\n")
        lines.append("\n")

        # 财运方面
        lines.append("### 5.2 财运方面\n")
        if synthesis_data and synthesis_data.get("wealth_analysis"):
            lines.append(f"\n{synthesis_data['wealth_analysis'][:300]}...\n")
        elif report.dimensions and report.dimensions.get("财富"):
            lines.append(f"\n财运运势：{report.dimensions['财富'].judgment}。建议稳健理财，避免高风险投机。\n")
        else:
            lines.append("\n财运运势平稳。财帛宫能量显示收入稳定，建议分散投资，注重名声积累。\n")
        lines.append("\n")

        # 感情/人际方面
        lines.append("### 5.3 感情/人际方面\n")
        if synthesis_data and synthesis_data.get("relationship_analysis"):
            lines.append(f"\n{synthesis_data['relationship_analysis'][:300]}...\n")
        elif report.dimensions and report.dimensions.get("感情"):
            lines.append(f"\n感情运势：{report.dimensions['感情'].judgment}。夫妻宫能量显示感情生活需要用心经营。\n")
        else:
            lines.append("\n感情运势需注意。夫妻宫天梁化权显示配偶在关系中占主导地位，建议多沟通包容。\n")
        lines.append("\n")

        # 健康方面
        lines.append("### 5.4 健康方面\n")
        if synthesis_data and synthesis_data.get("health_insights"):
            lines.append(f"\n{synthesis_data['health_insights'][:300]}...\n")
        elif report.dimensions and report.dimensions.get("健康"):
            lines.append(f"\n健康运势：{report.dimensions['健康'].judgment}。疾厄宫天机化科显示身体健康修复能力强。\n")
        else:
            lines.append("\n健康运势平稳。疾厄宫天机化科显示遇病易遇良医，建议保持规律作息。\n")

        lines.append("\n---\n")

        # ========== 六、核心提醒 ==========
        lines.append("## 六、核心提醒\n")

        # 一句话总结
        lines.append(f"> **{report.overall_judgment}——顺势而为，趋吉避凶**\n")
        lines.append("\n### 关键行动建议\n")

        # 从各维度提取建议
        if report.dimensions:
            for dim_name, dim_analysis in report.dimensions.items():
                dim_emoji = self._get_dimension_emoji(dim_name)
                plain_dim = self.terminology_map.get("dimension_names", {}).get(dim_name, dim_name)
                judgment = dim_analysis.judgment

                if judgment == "凶":
                    lines.append(f"- **{plain_dim}**: {dim_emoji} {judgment}，因果链显示风险较大，需谨慎应对，避免冒险\n")
                elif judgment == "吉":
                    lines.append(f"- **{plain_dim}**: {dim_emoji} {judgment}，把握机遇，积极进取\n")
                else:
                    lines.append(f"- **{plain_dim}**: {dim_emoji} {judgment}，稳步推进，保持平衡\n")

        # 综合建议
        lines.append("\n### 综合建议\n")
        if synthesis_data and synthesis_data.get("recommendations"):
            for rec in synthesis_data["recommendations"]:
                if isinstance(rec, dict):
                    lines.append(f"- {rec.get('action', '')}\n")
        else:
            lines.append(f"- 因果链显示{report.overall_judgment}态势，建议顺势而为\n")
            lines.append("- 命主福泽深厚，善用人际优势\n")
            lines.append("- 保持心态平和，修心养性\n")

        lines.append("\n---\n")

        # ========== 免责声明 ==========
        lines.append("## 免责声明\n")
        lines.append("\n本报告基于紫微斗数四化理论，通过AI智能分析生成，仅供参考。\n")
        lines.append("命理分析是一种传统文化现象，不应被视为决定性的预测。\n")
        lines.append("个人的命运受到多种因素影响，包括但不限于：个人努力、环境因素、随机事件等。\n")
        lines.append("\n建议您:\n")
        lines.append("- 将命理分析作为自我认知的参考\n")
        lines.append("- 保持积极向上的生活态度\n")
        lines.append("- 通过自身努力创造美好未来\n")
        lines.append("\n**命理是参考，你才是主角！**\n")

        # 元数据
        lines.append("\n---\n")
        lines.append("\n*报告生成: FengxianCyberTaoist 紫微斗数智能分析系统 (LLM驱动版)*\n")
        lines.append(f"\n*生成日期: {report.generated_at if hasattr(report, 'generated_at') else ''}*\n")

        return "".join(lines)

    def transform_to_ultra_plain(self, report: ThreeLayerDivinationReport) -> str:
        """
        转换为超通俗版

        情感优先重写，无术语，带 emoji

        Args:
            report: 三层融合预测报告

        Returns:
            Markdown 格式的超通俗报告
        """
        lines = []

        # 标题
        emoji = self._get_judgment_emoji(report.overall_judgment)
        conf_pct = round(report.overall_confidence * 100)
        lines.append(f"# {emoji} {report.target_year}年整体运势\n")

        # 整体判断 (情感化)
        judgment_map = {
            "吉": "今年运气不错哦！",
            "平": "今年整体比较平稳。",
            "凶": "今年需要多注意一下。",
        }
        lines.append(f"\n{judgment_map.get(report.overall_judgment, report.overall_judgment)}")
        lines.append(f"（这个判断的可靠程度大概有 {conf_pct}%）\n\n")

        # 关键发现
        lines.append("---\n")
        lines.append(f"{EMOJI_MAP['tip']} **今年最重要的事情**\n\n")

        key_findings = []

        # 从因果链提取关键发现
        if report.causal_chain_result:
            explanation = report.causal_chain_result.explanation
            # 简化并情感化
            explanation = self._apply_terminology_replacement(explanation)
            explanation = self._replace_star_names(explanation, with_explanation=False)
            key_findings.append(explanation)

        # 从分维度提取重点
        if report.dimensions:
            # 找最吉/最凶的维度
            judgments = {"吉": [], "平": [], "凶": []}
            for dim_name, dim in report.dimensions.items():
                judgments.get(dim.judgment, judgments["平"]).append(dim_name)

            if judgments["吉"]:
                lines.append(f"{EMOJI_MAP['luck']} **运气好的方面**: {', '.join(judgments['吉'])}\n\n")
            if judgments["凶"]:
                lines.append(f"{EMOJI_MAP['warning']} **需要多注意的方面**: {', '.join(judgments['凶'])}\n\n")

        # 如果有因果解释
        if report.causal_explanation:
            lines.append(f"{EMOJI_MAP['fire']} **为什么会这样**\n")
            ca_text = self._apply_terminology_replacement(report.causal_explanation)
            ca_text = self._replace_star_names(ca_text, with_explanation=False)
            lines.append(f"{ca_text}\n\n")

        # 各维度详细分析
        if report.dimensions:
            lines.append("---\n")
            lines.append(f"{EMOJI_MAP['target']} **各维度详细分析**\n\n")

            for dim_name, dim_analysis in report.dimensions.items():
                dim_emoji = self._get_dimension_emoji(dim_name)
                plain_dim = self.terminology_map.get("dimension_names", {}).get(
                    dim_name, dim_name
                )

                # 判断的情感化表达
                judgment_expr = {
                    "吉": "今年在这方面运气不错！",
                    "平": "今年在这方面比较普通。",
                    "凶": "今年在这方面要多注意！",
                }.get(dim_analysis.judgment, dim_analysis.judgment)

                conf_pct = round(dim_analysis.confidence * 100)

                lines.append(f"### {dim_emoji} {plain_dim}\n")
                lines.append(f"{judgment_expr} (准不准: {conf_pct}%)\n\n")

                # 推理的情感化
                reasoning = dim_analysis.reasoning
                reasoning = self._apply_terminology_replacement(reasoning)
                reasoning = self._replace_star_names(reasoning, with_explanation=False)
                lines.append(f"{reasoning}\n\n")

        # 建议 (Actionable)
        if report.suggestions:
            lines.append("---\n")
            lines.append(f"{EMOJI_MAP['hand']} **今年这样做会更好**\n\n")

            for i, suggestion in enumerate(
                report.suggestions[:self.options.max_suggestions], 1
            ):
                # 进一步通俗化
                plain = self._apply_terminology_replacement(suggestion)
                plain = self._replace_star_names(plain, with_explanation=False)

                # 根据建议类型添加 emoji
                if any(kw in plain for kw in ["投资", "理财", "金钱", "财务"]):
                    prefix = f"{EMOJI_MAP['money']}"
                elif any(kw in plain for kw in ["感情", "恋爱", "桃花", "婚姻"]):
                    prefix = f"{EMOJI_MAP['love']}"
                elif any(kw in plain for kw in ["健康", "身体", "运动"]):
                    prefix = f"{EMOJI_MAP['health']}"
                elif any(kw in plain for kw in ["事业", "工作", "学习"]):
                    prefix = f"{EMOJI_MAP['career']}"
                else:
                    prefix = f"{EMOJI_MAP['tip']}"

                lines.append(f"{i}. {prefix} {plain}\n")
            lines.append("\n")

        # 简单总结
        lines.append("---\n")
        lines.append(f"{EMOJI_MAP['gem']} **一句话总结**\n\n")

        # 生成一句话总结
        summary_parts = []
        if report.overall_judgment == "吉":
            summary_parts.append("今年整体运势不错")
        elif report.overall_judgment == "凶":
            summary_parts.append("今年要多加小心")
        else:
            summary_parts.append("今年整体平稳")

        # 加入最有特色的维度
        if report.dimensions:
            good_dims = [d for d, a in report.dimensions.items() if a.judgment == "吉"]
            bad_dims = [d for d, a in report.dimensions.items() if a.judgment == "凶"]

            if good_dims:
                summary_parts.append(f"{', '.join(good_dims)}是亮点")
            if bad_dims:
                summary_parts.append(f"{', '.join(bad_dims)}要多注意")

        lines.append("，".join(summary_parts) + "。\n\n")

        # 元数据
        lines.append(f"*这份分析由 AI 生成，可靠程度约 {round(report.overall_confidence * 100)}%，仅供参考~*\n")

        return "".join(lines)

    def generate_actionable_summary(self, report: ThreeLayerDivinationReport) -> str:
        """
        生成3条可执行的建议摘要

        Args:
            report: 三层融合预测报告

        Returns:
            3条简洁的建议
        """
        suggestions = []

        # 从现有建议中选取
        if report.suggestions:
            for suggestion in report.suggestions[:self.options.max_suggestions]:
                plain = self._apply_terminology_replacement(suggestion)
                plain = self._replace_star_names(plain, with_explanation=False)
                suggestions.append(plain)

        # 如果没有建议，从维度分析生成
        if not suggestions and report.dimensions:
            for dim_name, dim in list(report.dimensions.items())[:3]:
                dim_plain = self.terminology_map.get("dimension_names", {}).get(
                    dim_name, dim_name
                )
                if dim.judgment == "凶":
                    suggestions.append(f"在{dim_plain}方面要多加注意，避免冒险")
                elif dim.judgment == "吉":
                    suggestions.append(f"好好把握{dim_plain}方面的机会")

        # 如果仍然没有，返回默认建议
        if not suggestions:
            suggestions = [
                "保持积极心态，相信自己的判断",
                "遇到困难时多寻求他人建议",
                "注意身体健康，保持良好作息",
            ]

        # 格式化输出
        lines = []
        for i, suggestion in enumerate(suggestions[:3], 1):
            lines.append(f"{i}. {suggestion}")

        return "\n".join(lines)

    async def transform_report(
        self,
        report: ThreeLayerDivinationReport,
        style: str = "professional_plain",
        synthesis_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        异步转换报告

        主要入口点

        Args:
            report: 三层融合预测报告
            style: 转换风格
                - "professional_plain": 专业通俗版 (Report C)
                - "ultra_plain": 超通俗版
            synthesis_data: 综合分析数据

        Returns:
            转换后的报告内容
        """
        # 模拟异步处理
        await asyncio.sleep(0)

        if style == "ultra_plain":
            return self.transform_to_ultra_plain(report)
        else:
            # 默认使用专业通俗版
            return self.transform_to_professional_plain(report, synthesis_data)

    def transform_report_sync(
        self,
        report: ThreeLayerDivinationReport,
        style: str = "professional_plain",
        synthesis_data: Optional[Dict[str, Any]] = None,
        user_name: str = "命主",
        chart_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        同步转换报告

        Args:
            report: 三层融合预测报告
            style: 转换风格
            synthesis_data: 可选的LLM合成数据
            user_name: 用户姓名
            chart_data: 可选的原始命盘数据

        Returns:
            转换后的报告内容
        """
        if style == "ultra_plain":
            return self.transform_to_ultra_plain(report)
        else:
            return self.transform_to_professional_plain(report, synthesis_data, user_name, chart_data)


# ============ 便捷函数 ============

def create_transformer(
    terminology_map_path: Optional[str] = None,
    **kwargs
) -> ReportTransformer:
    """
    创建转换器的便捷函数

    Args:
        terminology_map_path: 术语映射文件路径
        **kwargs: 其他 TransformationOptions 参数

    Returns:
        ReportTransformer 实例
    """
    options = TransformationOptions(**kwargs) if kwargs else None
    return ReportTransformer(
        terminology_map_path=terminology_map_path,
        options=options
    )


async def transform_report_async(
    report: ThreeLayerDivinationReport,
    style: str = "professional_plain",
    **kwargs
) -> str:
    """
    异步转换报告的便捷函数

    Args:
        report: 三层融合预测报告
        style: 转换风格
        **kwargs: 其他 TransformationOptions 参数

    Returns:
        转换后的报告内容
    """
    transformer = create_transformer(**kwargs)
    return await transformer.transform_report(report, style)


def transform_report_sync(
    report: ThreeLayerDivinationReport,
    style: str = "professional_plain",
    synthesis_data: Optional[Dict[str, Any]] = None,
    user_name: str = "命主",
    chart_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    同步转换报告的便捷函数

    Args:
        report: 三层融合预测报告
        style: 转换风格
        synthesis_data: 可选的LLM合成数据
        user_name: 用户姓名
        chart_data: 可选的原始命盘数据
        **kwargs: 其他 TransformationOptions 参数

    Returns:
        转换后的报告内容
    """
    transformer = create_transformer(**kwargs)
    return transformer.transform_report_sync(report, style, synthesis_data, user_name, chart_data)
