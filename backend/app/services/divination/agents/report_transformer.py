"""
ReportTransformer - 报告通俗化转换器

将专业紫微斗数报告转换为通俗化版本：
- Report C (专业通俗版): 保留专业结构，用括号添加通俗解释
- Ultra Plain (超通俗版): 情感优先重写，无术语，带 emoji

三层融合预测报告 (ThreeLayerPredictionReport) 输入格式
"""

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set

from .report_generator import (
    ThreeLayerPredictionReport,
    DimensionAnalysis,
    CausalChainAnalysis,
    CaseBasedAnalysis,
    MultiAgentAnalysis,
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
        "POTENTIAL": "有潜力",
        "CONDITION": "有条件",
        "BAD": "不太好",
        "CATASTROPHIC": "很危险",
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
    report = ThreeLayerPredictionReport(...)

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

    def transform_to_professional_plain(self, report: ThreeLayerPredictionReport) -> str:
        """
        转换为专业通俗版 (Report C)

        保持专业结构，但用括号添加通俗解释

        Args:
            report: 三层融合预测报告

        Returns:
            Markdown 格式的通俗化报告
        """
        lines = []

        # 标题
        lines.append("# 专业通俗版命盘分析\n")
        lines.append(f"**分析年份**: {report.target_year}年\n")
        lines.append(f"**命盘ID**: {report.chart_id}\n")
        lines.append("---\n")

        # 整体判断
        emoji = self._get_judgment_emoji(report.overall_judgment)
        conf_pct = round(report.overall_confidence * 100)
        lines.append(f"## {emoji} 整体运势\n")
        lines.append(f"**综合判断**: {report.overall_judgment}")
        lines.append(f" (置信度: {conf_pct}%)")
        lines.append("\n\n")

        # 三层分析结果
        lines.append("## 三层分析\n")

        # 因果链推理
        if report.causal_chain_result:
            lines.append("### 1. 原因分析\n")
            causal = report.causal_chain_result
            lines.append(f"**严重程度**: {causal.severity_level}\n")
            lines.append(f"**因果类型**: {causal.chain_type}\n")
            if self.options.add_confidence_explanation:
                lines.append(f"**准不准**: {round(causal.confidence * 100)}%\n")

            # 显示详细的因果链分类分析（来自CausalResult.analysis）
            # 限制显示条数，只显示最严重的因果链，避免信息过载
            MAX_EXPLANATION_LINES = 15  # 最多显示15条
            if causal.explanation:
                lines.append("\n")
                explanation = self._apply_terminology_replacement(causal.explanation)
                # 格式化为更易读的版本
                readable_explanation = self._format_causal_explanation_readable(explanation)
                # 限制行数
                exp_lines = readable_explanation.strip().split('\n')
                if len(exp_lines) > MAX_EXPLANATION_LINES:
                    # 保留前几行和最后一行的整体评估
                    lines.append('\n'.join(exp_lines[:MAX_EXPLANATION_LINES]))
                    lines.append(f"\n*...还有{len(exp_lines) - MAX_EXPLANATION_LINES}条因果链*\n")
                    lines.append(f"\n{exp_lines[-1]}\n")
                else:
                    lines.append(f"{readable_explanation}\n")
                lines.append("\n")
            # 同时显示关键链条摘要（按严重程度分组，最多显示10条）
            if causal.key_chains:
                lines.append("\n**🔍 因果链速览**:\n")
                # 按严重程度分组 - 支持枚举名和中文值两种格式
                by_severity = {
                    "CATASTROPHIC": [], "重大": [],
                    "BAD": [], "确定": [],
                    "CONDITION": [], "条件": [],
                    "POTENTIAL": [], "潜在": []
                }
                for chain in causal.key_chains:
                    if isinstance(chain, dict):
                        sev = chain.get("severity", "POTENTIAL")
                    else:
                        sev = "POTENTIAL"
                    # 直接匹配或归入潜在
                    if sev in by_severity:
                        by_severity[sev].append(chain)
                    else:
                        by_severity["POTENTIAL"].append(chain)

                severity_labels = {
                    "CATASTROPHIC": "⚠️ 重大风险",
                    "重大": "⚠️ 重大风险",
                    "BAD": "🔴 确定风险",
                    "确定": "🔴 确定风险",
                    "CONDITION": "🔔 条件触发",
                    "条件": "🔔 条件触发",
                    "POTENTIAL": "💡 潜在影响",
                    "潜在": "💡 潜在影响"
                }
                # 优先级顺序
                severity_priority = ["CATASTROPHIC", "重大", "BAD", "确定", "CONDITION", "条件", "POTENTIAL", "潜在"]

                count = 0
                shown_labels = set()  # 避免重复显示同一标签
                for sev in severity_priority:
                    chains = by_severity.get(sev, [])
                    if chains and count < 10:
                        label = severity_labels.get(sev, severity_labels.get(sev.split("_")[0] if "_" in sev else sev, "未知"))
                        if label not in shown_labels:
                            lines.append(f"**{label}**\n")
                            shown_labels.add(label)
                        for chain in chains[:2]:  # 每组最多2条
                            if isinstance(chain, dict):
                                desc = chain.get("description", str(chain))
                                # 翻译因果链类型
                                plain_desc = self._translate_causal_chain_type(desc)
                                lines.append(f"- {self._apply_terminology_replacement(plain_desc)}\n")
                            else:
                                lines.append(f"- {chain}\n")
                            count += 1
                            if count >= 10:
                                break
                    if count >= 10:
                        break
                if count < len(causal.key_chains):
                    lines.append(f"- ...还有{len(causal.key_chains) - count}条因果链\n")
                lines.append("\n")
            # 如果没有详细分析，则显示关键链条
            elif causal.key_chains:
                lines.append("\n**主要影响链条**:\n")
                for chain in causal.key_chains[:5]:  # 最多显示5条
                    if isinstance(chain, dict):
                        chain_desc = chain.get("description", str(chain))
                        lines.append(f"- {self._apply_terminology_replacement(chain_desc)}\n")
                    else:
                        lines.append(f"- {chain}\n")
                lines.append("\n")

        # 案例推理
        if report.case_based_result:
            lines.append("### 2. 类似情况分析\n")
            case_result = report.case_based_result
            if self.options.add_confidence_explanation:
                lines.append(f"**准不准**: {round(case_result.confidence * 100)}%\n")
            lines.append(f"\n{self._apply_terminology_replacement(case_result.probability_summary)}\n")
            lines.append("\n")

        # 多Agent共识
        if report.multi_agent_result:
            lines.append("### 3. 多位专家共识\n")
            multi = report.multi_agent_result
            if self.options.add_confidence_explanation:
                lines.append(f"**准不准**: {round(multi.confidence * 100)}%\n")
            lines.append(f"\n**一致认为**: {self._apply_terminology_replacement(multi.final_judgment)}\n")
            lines.append("\n")

        # 分维度分析
        if report.dimensions:
            lines.append("---\n")
            lines.append("## 各个方面\n")

            for dim_name, dim_analysis in report.dimensions.items():
                dim_emoji = self._get_dimension_emoji(dim_name)
                plain_dim = self.terminology_map.get("dimension_names", {}).get(dim_name, dim_name)

                lines.append(f"### {dim_emoji} {plain_dim}\n")

                # 判断
                lines.append(f"**运势**: {dim_analysis.judgment}")
                conf_pct = round(dim_analysis.confidence * 100)
                lines.append(f" (准不准: {conf_pct}%)\n")

                # 推理
                reasoning = self._apply_terminology_replacement(dim_analysis.reasoning)
                lines.append(f"\n**分析逻辑**: {reasoning}\n")
                lines.append("\n")

            # 术语解释
            lines.append("---\n")
            lines.append("## 术语解释\n")
            lines.append("| 术语 | 含义 |\n")
            lines.append("|------|------|\n")
            lines.append("| **化禄** | 好运降临，代表机会与收获 |\n")
            lines.append("| **化权** | 权力增强，代表掌控与进取 |\n")
            lines.append("| **化科** | 名声提升，代表学业与声誉 |\n")
            lines.append("| **化忌** | 挑战显现，代表阻碍与考验 |\n")
            lines.append("| **命宫** | 体现性格与先天命运 |\n")
            lines.append("| **财帛宫** | 代表财运与金钱状况 |\n")
            lines.append("| **事业宫** | 代表事业与工作发展 |\n")
            lines.append("| **夫妻宫** | 代表感情与婚姻状况 |\n")
            lines.append("| **福德宫** | 代表精神与福气积累 |\n")
            lines.append("| **疾厄宫** | 代表健康与疾病状况 |\n")
            lines.append("| **因果链** | 导致运势好坏的深层原因 |\n")
            lines.append("| **置信度** | 分析结果的可靠程度（越高越准） |\n")
            lines.append("\n")

        # 趋避建议
        if report.suggestions:
            lines.append("---\n")
            lines.append("## 怎么做\n")
            for i, suggestion in enumerate(report.suggestions[:self.options.max_suggestions], 1):
                plain_suggestion = self._apply_terminology_replacement(suggestion)
                lines.append(f"{i}. {plain_suggestion}\n")
            lines.append("\n")

        # 参考案例
        if report.reference_cases:
            lines.append("---\n")
            lines.append("## 类似的人\n")
            for case in report.reference_cases[:3]:
                if isinstance(case, dict):
                    desc = case.get("description", case.get("summary", ""))
                    if desc:
                        lines.append(f"- {self._apply_terminology_replacement(desc)}\n")
            lines.append("\n")

        # 元数据
        lines.append("---\n")
        lines.append(f"*报告生成时间: {report.generated_at}*\n")

        return "".join(lines)

    def transform_to_ultra_plain(self, report: ThreeLayerPredictionReport) -> str:
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

    def generate_actionable_summary(self, report: ThreeLayerPredictionReport) -> str:
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
        report: ThreeLayerPredictionReport,
        style: str = "professional_plain"
    ) -> str:
        """
        异步转换报告

        主要入口点

        Args:
            report: 三层融合预测报告
            style: 转换风格
                - "professional_plain": 专业通俗版 (Report C)
                - "ultra_plain": 超通俗版

        Returns:
            转换后的报告内容
        """
        # 模拟异步处理
        await asyncio.sleep(0)

        if style == "ultra_plain":
            return self.transform_to_ultra_plain(report)
        else:
            # 默认使用专业通俗版
            return self.transform_to_professional_plain(report)

    def transform_report_sync(
        self,
        report: ThreeLayerPredictionReport,
        style: str = "professional_plain"
    ) -> str:
        """
        同步转换报告

        Args:
            report: 三层融合预测报告
            style: 转换风格

        Returns:
            转换后的报告内容
        """
        if style == "ultra_plain":
            return self.transform_to_ultra_plain(report)
        else:
            return self.transform_to_professional_plain(report)


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
    report: ThreeLayerPredictionReport,
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
    report: ThreeLayerPredictionReport,
    style: str = "professional_plain",
    **kwargs
) -> str:
    """
    同步转换报告的便捷函数

    Args:
        report: 三层融合预测报告
        style: 转换风格
        **kwargs: 其他 TransformationOptions 参数

    Returns:
        转换后的报告内容
    """
    transformer = create_transformer(**kwargs)
    return transformer.transform_report_sync(report, style)
