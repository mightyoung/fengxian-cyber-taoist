#!/usr/bin/env python3
"""
统一报告生成脚本 - LLM驱动的紫微斗数运势报告生成

重构目标：全部部分的推理都要让LLM参与进来
- 真实规则的计算作为提供给他的素材
- 编写提示词、提供给他fewshot辅助他生成
- 每个章节都通过LLM独立推理生成

使用方法:
    python -m app.utils.unified_report_generator --name "张三" --birth 1997 --year 2026

    或直接在Python中调用:
    from app.utils.unified_report_generator import generate_complete_report
    result = generate_complete_report(chart_data, analysis_result)
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# 添加backend路径
_BACKEND_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_BACKEND_ROOT))

from app.utils.logger import get_logger  # noqa: E402

logger = get_logger('fengxian_cyber_taoist.unified_report')

# 尝试导入LLM客户端
try:
    from app.utils.llm_client import LLMClient
    from app.services.divination.agents.report_prompts import (
        build_overview_prompt,
        build_transform_detail_prompt,
        build_yearly_fortune_prompt,
        build_personality_prompt,
        build_practical_guide_prompt,
        build_monthly_advice_prompt,
        build_key_reminder_prompt,
        build_causal_chain_prompt,
        get_llm_temperature,
        get_llm_max_tokens,
    )
    from app.services.divination.agents.report_examples import (
        SIHUA_EXAMPLES,
        PERSONALITY_EXAMPLES,
        GUIDE_EXAMPLES,
        REMINDER_EXAMPLES,
    )
    LLM_AND_PROMPTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LLM/Prompts module not available: {e}")
    LLM_AND_PROMPTS_AVAILABLE = False

# 尝试导入图表生成器
try:
    from app.utils.chart_generator import (
        generate_radar_chart,
        generate_bar_chart,
        generate_confidence_gauge,
        generate_monthly_heatmap
    )
    from app.utils.markdown_to_pdf import markdown_to_pdf
    CHART_AND_PDF_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chart/PDF module not available: {e}")
    CHART_AND_PDF_AVAILABLE = False


class LLMReportGenerator:
    """LLM驱动的报告生成器"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """初始化LLM报告生成器"""
        if not LLM_AND_PROMPTS_AVAILABLE:
            raise ImportError("LLM客户端和提示词模块不可用")

        self.llm = llm_client or LLMClient()

    def _add_fewshot_examples(self, messages: List[Dict[str, str]], section: str) -> List[Dict[str, str]]:
        """
        为消息列表添加few-shot示例

        Args:
            messages: 消息列表
            section: 章节类型

        Returns:
            添加了示例的消息列表
        """
        if not messages:
            return messages

        user_message = messages[-1]["content"]

        # 根据章节类型添加对应的few-shot示例
        fewshot_map = {
            "overview": "",
            "transform_detail": self._build_fewshot_section("sihua"),
            "yearly_fortune": self._build_fewshot_section("monthly"),
            "personality": self._build_fewshot_section("personality"),
            "practical_guide": self._build_fewshot_section("guide"),
            "monthly_advice": self._build_fewshot_section("monthly"),
            "key_reminder": self._build_fewshot_section("reminder"),
            "causal_chain": "",
        }

        examples = fewshot_map.get(section, "")
        if examples:
            user_message += f"\n\n## Few-Shot参考示例\n\n{examples}"

        messages[-1]["content"] = user_message
        return messages

    def _build_fewshot_section(self, example_type: str) -> str:
        """构建few-shot示例文本"""
        if example_type == "sihua":
            # 四化详解示例
            SIHUA_EXAMPLES[0] if SIHUA_EXAMPLES else {}
            return """**示例：禄忌同宫双化**

用户命盘：化禄[星曜A]在[宫位X]，[星曜A]同时化忌
LLM生成结果：
```json
{
  "title": "2.1 化禄 — [星曜A] 在[宫位X]",
  "xingyao_analysis": "[星曜A]是紫微斗数中的[星曜分类]，代表[性格特点]。[星曜A]坐命的人，通常[性格描述]。",
  "sihua_analysis": "化禄代表星的能量往好的方向发展，带来机会和收获。对于[星曜A]来说，化禄增强了其[特质]，让命主更容易获得[好运描述]。",
  "palace_context": "[星曜A]化禄落入[宫位X]，这是[吉凶描述]的配置。[宫位X]代表[含义]，[宫位X]有化禄意味着[运势描述]。",
  "synthesis": {
    "fortune_feature": "[运势特征概括]",
    "specific_manifestations": [
      "[具体表现1]",
      "[具体表现2]",
      "[具体表现3]"
    ],
    "advice": "[行动建议]"
  }
}
```"""

        elif example_type == "personality":
            PERSONALITY_EXAMPLES[0] if PERSONALITY_EXAMPLES else {}
            return """**示例：命宫双星组合**

用户命盘：[星曜A]、[星曜B]坐命宫，有[辅助星曜]等
LLM生成结果：
```json
{
  "section_title": "四、性格画像",
  "star_traits": [
    {
      "star_name": "[星曜A]",
      "traits_analysis": "[星曜A]是[星曜分类]，代表[性格特点]。你是一个[性格描述]的人。",
      "positive_traits": ["[优点1]", "[优点2]", "[优点3]"],
      "negative_traits": ["[缺点1]", "[缺点2]"]
    },
    {
      "star_name": "[星曜B]",
      "traits_analysis": "[星曜B]是[星曜分类]，代表[性格特点]。[星曜B]坐命的人通常[性格描述]。",
      "positive_traits": ["[优点1]", "[优点2]", "[优点3]"],
      "negative_traits": ["[缺点1]", "[缺点2]"]
    }
  ],
  "personality_summary": "你是一个性格[特征描述]的人。兼具[星曜A]的[特质]和[星曜B]的[特质]，在人际交往中往往能发挥积极作用。...",
  "optimization_suggestions": [
    {"aspect": "优势发挥", "suggestion": "利用[星曜A]的[特质]和[星曜B]的[协调能力]，在人际交往中发挥积极作用"},
    {"aspect": "短板改进", "suggestion": "克服[缺点描述]，学会果断决策"}
  ]
}
```"""

        elif example_type == "guide":
            GUIDE_EXAMPLES[0] if GUIDE_EXAMPLES else {}
            return """**示例：禄忌并存实用指南**

用户命盘：化禄[星曜A]、[星曜A]化忌同宫
LLM生成结果：
```json
{{
  "section_title": "五、实用指南",
  "career_guide": {{
    "title": "5.1 事业/学业方面",
    "suggestions": [
      {{"title": "[建议标题]", "content": "[具体建议内容，要结合用户的实际四化配置]"}}
    ]
  }},
  "wealth_guide": {{"title": "5.2 财运方面", "suggestions": [...]}},
  "relationship_guide": {{"title": "5.3 感情/人际方面", "suggestions": [...]}},
  "health_guide": {{"title": "5.4 健康方面", "suggestions": [...]}}
}}
```"""

        elif example_type == "reminder":
            REMINDER_EXAMPLES[0] if REMINDER_EXAMPLES else {}
            return """**示例：平运势核心提醒**

用户命盘：整体运势"平"，因果链为CONDITION级别
LLM生成结果：
```json
{{
  "section_title": "七、核心提醒",
  "overall_theme": "平——关键在于把握好度",
  "key_action_suggestions": [
    {{"category": "事业", "suggestion": "运势平稳，宜守成待机，稳健发展"}},
    {{"category": "财富", "suggestion": "案例验证支持吉兆，可适度进取"}}
  ],
  "special_reminders": {{
    "advantage_months": {{"months": ["高峰月1", "高峰月2"], "description": "全力出击，收获成果"}},
    "challenge_months": {{"months": ["挑战月"], "description": "休养生息，避免冒进"}},
    "balance_months": {{"description": "稳扎稳打，积累能量"}}
  }}
}}
```"""

        return ""

    def _generate_section_markdown(
        self,
        section: str,
        chart_data: Dict[str, Any],
        analysis_result: Dict[str, Any],
        target_year: Optional[int] = None
    ) -> str:
        """
        使用LLM生成单个章节的Markdown内容

        Args:
            section: 章节类型
            chart_data: 命盘数据
            analysis_result: 分析结果
            target_year: 目标年份

        Returns:
            章节的Markdown内容
        """
        # 构建提示词
        if section == "overview":
            messages = build_overview_prompt(chart_data, analysis_result)
        elif section == "transform_detail":
            messages = build_transform_detail_prompt(chart_data, analysis_result)
        elif section == "yearly_fortune":
            messages = build_yearly_fortune_prompt(chart_data, analysis_result)
        elif section == "personality":
            messages = build_personality_prompt(chart_data, analysis_result)
        elif section == "practical_guide":
            messages = build_practical_guide_prompt(chart_data, analysis_result)
        elif section == "monthly_advice":
            messages = build_monthly_advice_prompt(chart_data, analysis_result, target_year or 2026)
        elif section == "key_reminder":
            messages = build_key_reminder_prompt(chart_data, analysis_result)
        elif section == "causal_chain":
            messages = build_causal_chain_prompt(chart_data, analysis_result, target_year or 2026)
        else:
            return ""

        # 添加few-shot示例
        messages = self._add_fewshot_examples(messages, section)

        # 获取LLM参数
        temperature = get_llm_temperature(section)
        max_tokens = get_llm_max_tokens(section)

        # 调用LLM
        try:
            response = self.llm.chat_json(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=False
            )

            # 转换为Markdown
            markdown = self._json_to_markdown(response, section)
            return markdown

        except Exception as e:
            logger.error(f"LLM生成章节失败 [{section}]: {e}")
            return f"<!-- LLM生成失败: {section} -->\n\n**内容生成中...**\n"

    def _json_to_markdown(self, json_data: Dict[str, Any], section: str) -> str:
        """
        将JSON数据转换为Markdown格式

        Args:
            json_data: LLM返回的JSON数据
            section: 章节类型

        Returns:
            Markdown格式的文本
        """
        if not json_data:
            return ""

        markdown_parts = []

        if section == "overview":
            # 命盘概览
            section_title = json_data.get("section_title", "一、命盘概览")
            markdown_parts.append(f"## {section_title}\n")

            basic_info = json_data.get("basic_info", {})
            markdown_parts.append("### 1.1 基本信息\n")
            markdown_parts.append("| 项目 | 内容 |")
            markdown_parts.append("|------|------|")
            for key, value in basic_info.items():
                display_key = {"name": "命主姓名", "birth_year": "出生年份", "ming_ge": "命格特征",
                              "ming_gong_star": "命宫主星", "sihua_pattern": "四化格局"}.get(key, key)
                markdown_parts.append(f"| {display_key} | {value} |")

            sihua_config = json_data.get("sihua_config", [])
            if sihua_config:
                markdown_parts.append("\n### 1.2 四化星曜配置\n")
                markdown_parts.append("| 四化 | 星曜 | 所在宫位 | 能量属性 |")
                markdown_parts.append("|------|------|----------|----------|")
                energy_map = {"化禄": "机会与收获", "化权": "权力与掌控", "化科": "声誉与学习", "化忌": "挑战与考验"}
                for item in sihua_config:
                    energy = energy_map.get(item.get("sihua", ""), "")
                    markdown_parts.append(f"| {item.get('sihua', '')} | {item.get('star', '')} | {item.get('palace', '')} | {energy} |")

            judgment = json_data.get("overall_judgment", "")
            judgment_desc = json_data.get("judgment_description", "")
            if judgment:
                markdown_parts.append("\n### 1.3 综合判断\n")
                markdown_parts.append(f"**整体运势**: {judgment}\n")
                if judgment_desc:
                    markdown_parts.append(f"{judgment_desc}\n")

        elif section == "transform_detail":
            # 四化详解
            section_title = json_data.get("section_title", "二、四化详解")
            markdown_parts.append(f"## {section_title}\n")

            transforms = json_data.get("transforms", [])
            for i, t in enumerate(transforms, 1):
                title = t.get("title", f"2.{i} 四化")
                markdown_parts.append(f"### {title}\n")
                markdown_parts.append("**【星曜解析】**\n")
                markdown_parts.append(f"{t.get('xingyao_analysis', '')}\n")
                markdown_parts.append("\n**【四化解析】**\n")
                markdown_parts.append(f"{t.get('sihua_analysis', '')}\n")

                palace_context = t.get("palace_context", "")
                if palace_context:
                    markdown_parts.append("\n**【宫位解读】**\n")
                    markdown_parts.append(f"{palace_context}\n")

                synthesis = t.get("synthesis", {})
                if synthesis:
                    markdown_parts.append("\n**【综合解读】**\n")
                    markdown_parts.append(f"- **运势特征**: {synthesis.get('fortune_feature', '')}\n")
                    manifestations = synthesis.get("specific_manifestations", [])
                    if manifestations:
                        markdown_parts.append("- **具体表现**: \n")
                        for m in manifestations:
                            markdown_parts.append(f"  - {m}\n")
                    advice = synthesis.get("advice", "")
                    if advice:
                        markdown_parts.append(f"- **把握建议**: {advice}\n")

                markdown_parts.append("\n---\n")

        elif section == "yearly_fortune":
            # 年度运势分析
            section_title = json_data.get("section_title", "三、年度运势分析")
            markdown_parts.append(f"## {section_title}\n")

            markdown_parts.append("### 3.1 五维运势评分\n")
            markdown_parts.append("| 维度 | 评分 | 运势解读 |")
            markdown_parts.append("|------|------|----------|")

            scores = json_data.get("five_dimension_scores", [])
            for score in scores:
                dim = score.get("dimension", "")
                score_val = score.get("score", "")
                interpretation = score.get("interpretation", "")
                judgment = score.get("judgment", "")
                markdown_parts.append(f"| {dim} | {score_val}/100 | {interpretation} |")

            monthly_trends = json_data.get("monthly_trends", [])
            if monthly_trends:
                markdown_parts.append("\n### 3.2 月度运势走势\n")
                markdown_parts.append("| 月份 | 运势 | 提示 |")
                markdown_parts.append("|------|------|------|")
                for m in monthly_trends:
                    month = m.get("month", "")
                    fortune = m.get("fortune", "")
                    tip = m.get("tip", "")
                    markdown_parts.append(f"| {month} | {fortune} | {tip} |")

            key_months = json_data.get("key_months", {})
            if key_months:
                markdown_parts.append("\n### 3.3 关键月份分析\n")
                peak_months = key_months.get("peak_months", [])
                if peak_months:
                    month_str = "、".join(peak_months)
                    markdown_parts.append(f"**{month_str}是全年运势高峰期**\n")
                    markdown_parts.append(f"{key_months.get('peak_description', '')}\n")

        elif section == "personality":
            # 性格画像
            section_title = json_data.get("section_title", "四、性格画像")
            markdown_parts.append(f"## {section_title}\n")

            markdown_parts.append("### 4.1 星曜特质分析\n")
            star_traits = json_data.get("star_traits", [])
            for star in star_traits:
                star_name = star.get("star_name", "")
                traits = star.get("traits_analysis", "")
                markdown_parts.append(f"**{star_name}特质**:\n")
                markdown_parts.append(f"{traits}\n")
                markdown_parts.append("\n性格优点：\n")
                for t in star.get("positive_traits", []):
                    markdown_parts.append(f"- {t}\n")
                markdown_parts.append("\n性格缺点：\n")
                for t in star.get("negative_traits", []):
                    markdown_parts.append(f"- {t}\n")
                markdown_parts.append("")

            summary = json_data.get("personality_summary", "")
            if summary:
                markdown_parts.append(f"**综合性格描述**: {summary}\n")

            markdown_parts.append("\n### 4.2 性格优化建议\n")
            suggestions = json_data.get("optimization_suggestions", [])
            for i, s in enumerate(suggestions, 1):
                aspect = s.get("aspect", "")
                suggestion = s.get("suggestion", "")
                markdown_parts.append(f"{i}. **{aspect}**: {suggestion}\n")

        elif section == "practical_guide":
            # 实用指南
            section_title = json_data.get("section_title", "五、实用指南")
            markdown_parts.append(f"## {section_title}\n")

            guides = [
                ("career_guide", "5.1 事业/学业方面"),
                ("wealth_guide", "5.2 财运方面"),
                ("relationship_guide", "5.3 感情/人际方面"),
                ("health_guide", "5.4 健康方面"),
            ]

            for key, title in guides:
                guide = json_data.get(key, {})
                if guide:
                    markdown_parts.append(f"### {title}\n")
                    for s in guide.get("suggestions", []):
                        s_title = s.get("title", "")
                        s_content = s.get("content", "")
                        markdown_parts.append(f"- **{s_title}**: {s_content}\n")
                    markdown_parts.append("")

        elif section == "monthly_advice":
            # 每月宜忌
            section_title = json_data.get("section_title", "六、每月宜忌")
            markdown_parts.append(f"## {section_title}\n")

            months = json_data.get("months", [])
            for m in months:
                month_title = m.get("month", "")
                fortune = m.get("fortune_level", "")
                yi_list = m.get("yi", [])
                ji_list = m.get("ji", [])
                analysis = m.get("analysis", "")

                markdown_parts.append(f"### {month_title}\n")
                if fortune:
                    markdown_parts.append(f"**运势**: {fortune}\n")
                markdown_parts.append("\n**宜**:\n")
                for yi in yi_list:
                    markdown_parts.append(f"- {yi}\n")
                markdown_parts.append("\n**忌**:\n")
                for ji in ji_list:
                    markdown_parts.append(f"- {ji}\n")
                if analysis:
                    markdown_parts.append(f"\n**分析**: {analysis}\n")
                markdown_parts.append("")

        elif section == "key_reminder":
            # 核心提醒
            section_title = json_data.get("section_title", "七、核心提醒")
            markdown_parts.append(f"## {section_title}\n")

            theme = json_data.get("overall_theme", "")
            if theme:
                markdown_parts.append(f"> **{theme}**\n\n")

            markdown_parts.append("### 7.1 关键行动建议\n")
            for s in json_data.get("key_action_suggestions", []):
                category = s.get("category", "")
                suggestion = s.get("suggestion", "")
                markdown_parts.append(f"- **{category}**: {suggestion}\n")
            markdown_parts.append("")

            special = json_data.get("special_reminders", {})
            if special:
                markdown_parts.append("### 7.2 特别提醒\n")
                advantage = special.get("advantage_months", {})
                if advantage:
                    months = "、".join(advantage.get("months", []))
                    markdown_parts.append(f"**优势月** ({months}): {advantage.get('description', '')}\n")

                challenge = special.get("challenge_months", {})
                if challenge:
                    months = "、".join(challenge.get("months", []))
                    markdown_parts.append(f"**挑战月** ({months}): {challenge.get('description', '')}\n")

                balance = special.get("balance_months", {})
                if balance:
                    markdown_parts.append(f"**平衡月**: {balance.get('description', '')}\n")

        elif section == "causal_chain":
            # 因果链分析
            section_title = json_data.get("section_title", "三、因果链分析")
            markdown_parts.append(f"## {section_title}\n")

            summary = json_data.get("analysis_summary", "")
            if summary:
                markdown_parts.append(f"> **{summary}**\n\n")

            severity = json_data.get("severity_level", "未知")
            severity_exp = json_data.get("severity_explanation", "")
            markdown_parts.append(f"### 因果链严重等级：{severity}\n")
            if severity_exp:
                markdown_parts.append(f"{severity_exp}\n\n")

            markdown_parts.append("### 关键发现\n")
            for finding in json_data.get("key_findings", []):
                chain_type = finding.get("chain_type", "")
                description = finding.get("description", "")
                impact = finding.get("impact", "")
                suggestion = finding.get("suggestion", "")
                markdown_parts.append(f"**【{chain_type}】**\n")
                markdown_parts.append(f"- 描述：{description}\n")
                if impact:
                    markdown_parts.append(f"- 影响：{impact}\n")
                if suggestion:
                    markdown_parts.append(f"- 建议：{suggestion}\n")
                markdown_parts.append("")

            conclusion = json_data.get("overall_conclusion", "")
            if conclusion:
                markdown_parts.append("### 综合结论\n")
                markdown_parts.append(f"{conclusion}\n")

        return "\n".join(markdown_parts)

    def generate_full_report(
        self,
        chart_data: Dict[str, Any],
        analysis_result: Dict[str, Any],
        target_year: int = 2026
    ) -> str:
        """
        使用LLM生成完整报告

        Args:
            chart_data: 命盘数据
            analysis_result: 分析结果
            target_year: 目标年份

        Returns:
            完整报告的Markdown文本
        """
        # 获取用户信息
        birth_info = chart_data.get("birth_info", {})
        name = birth_info.get("name", "命主")

        # 标题和元信息
        lines = []
        lines.append(f"# {name} {target_year}年运势预测报告\n")
        lines.append(f"> **命主**: {name}")
        lines.append(f"> **预测年份**: {target_year}年")
        lines.append(f"> **生成时间**: {datetime.now().strftime('%Y年%m月')}")
        lines.append("> **分析系统**: FengxianCyberTaoist 紫微斗数智能分析系统")
        lines.append("> **LLM驱动**: 是（所有章节均由大语言模型推理生成）\n")
        lines.append("---\n")

        # 生成各章节
        sections = [
            ("overview", "命盘概览"),
            ("transform_detail", "四化详解"),
            ("causal_chain", "因果链分析"),
            ("yearly_fortune", "年度运势分析"),
            ("personality", "性格画像"),
            ("practical_guide", "实用指南"),
            ("key_reminder", "核心提醒"),
        ]

        for section_key, section_name in sections:
            logger.info(f"正在生成章节: {section_name}")
            try:
                section_content = self._generate_section_markdown(
                    section=section_key,
                    chart_data=chart_data,
                    analysis_result=analysis_result,
                    target_year=target_year
                )
                lines.append(section_content)
                lines.append("---\n")
            except Exception as e:
                logger.error(f"生成章节失败 [{section_key}]: {e}")
                lines.append(f"## {section_name}\n")
                lines.append(f"<!-- 生成失败: {e} -->\n")
                lines.append("---\n")

        # 添加免责声明
        lines.append("## 八、免责声明\n")
        lines.append("本报告基于紫微斗数四化理论，通过AI智能分析生成，仅供参考。\n")
        lines.append("命理分析是一种传统文化现象，不应被视为决定性的预测。\n")
        lines.append("个人的命运受到多种因素影响，包括但不限于：个人努力、环境因素、随机事件等。\n")
        lines.append("\n建议您:\n")
        lines.append("- 将命理分析作为自我认知的参考\n")
        lines.append("- 保持积极向上的生活态度\n")
        lines.append("- 通过自身努力创造美好未来\n")
        lines.append("\n**命理是参考，你才是主角！**\n")
        lines.append("\n---\n\n*报告生成: FengxianCyberTaoist 紫微斗数智能分析系统 (LLM驱动版)*\n")
        lines.append(f"*生成日期: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}*")

        return "\n".join(lines)


# ============ 兼容旧版本的函数 ============

def _get_judgment_description(judgment: str, transforms: Dict[str, Any]) -> str:
    """根据判断结果和四化配置生成描述（备用）"""
    has_lu = "hua_lu" in transforms
    has_ji = "hua_ji" in transforms

    if judgment == "吉":
        return "收获满满的年份"
    elif judgment == "凶":
        return "需要谨慎应对的年份"
    elif has_lu and has_ji:
        return "既有机遇也有挑战的年份。命盘中同时存在福气之星(化禄)和考验之星(化忌)，预示着这一年将在收获与挑战中前行"
    elif has_lu:
        return "充满机遇和收获的年份"
    elif has_ji:
        return "需要谨慎应对挑战的年份"
    else:
        return "机遇与挑战并存的年份"


def _get_star_description(star_name: str) -> str:
    """获取星曜的基本描述（备用）"""
    star_descriptions = {
        "天同": "天同是紫微斗数中最具福气的星曜，被称为「福星」。它代表温和、享乐、知足常乐的性格特点。",
        "天梁": "天梁是「荫星」和「寿星」，代表庇护、慈善、长寿，责任感和清贵的品格。",
        "天机": "天机是「智慧星」，代表智慧、思考、变动、机敏和创新。",
        "太阳": "太阳是「光明之星」，代表热情、积极、智慧和权贵。",
        "紫微": "紫微是「帝王星」，代表尊贵、权威、领导和才能。",
        "天府": "天府是「福星」和「库星」，代表福气、保守、稳重和储藏。",
    }
    return star_descriptions.get(star_name, f"{star_name}是紫微斗数中的一颗重要星曜，对命运有着独特的影响。")


def generate_report_charts(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """从分析结果生成所有图表"""
    if not CHART_AND_PDF_AVAILABLE:
        return {"charts": None, "heatmap": None, "monthly_data": []}

    charts = {}
    heatmap = None
    monthly_data = []

    try:
        # 1. 五维雷达图
        dimensions = analysis_result.get("dimensions", {})
        if dimensions:
            dims = []
            scores = []
            ORDER = ["事业", "财运", "感情", "健康", "人际关系"]

            for dim_key in ORDER:
                if dim_key in dimensions:
                    dim_data = dimensions[dim_key]
                    dims.append(dim_key)
                    judgment = dim_data.get("judgment", "平")
                    confidence = dim_data.get("confidence", 0.5)

                    if judgment == "吉":
                        score = 4.0 + confidence
                    elif judgment == "凶":
                        score = 1.0 + confidence
                    else:
                        score = 2.5 + confidence

                    scores.append(min(5.0, max(1.0, score)))

            if dims and scores:
                radar = generate_radar_chart(dims, scores, "五维运势雷达图")
                if radar:
                    charts["radar"] = radar

        # 2. 月度运势数据
        monthly = analysis_result.get("monthly_data", [])
        if monthly:
            months = [m.get("month", f"{i+1}月") for i, m in enumerate(monthly)]
            values = [m.get("score", 3.5) * 20 for m in monthly]

            bar = generate_bar_chart(months, values, "月度运势评分")
            if bar:
                charts["bar"] = bar

            # 热力图
            heatmap_data = []
            for i, m in enumerate(monthly):
                score = m.get("score", 3.5)
                if score >= 4.5:
                    label = "高峰"
                elif score >= 4.0:
                    label = "上升"
                elif score >= 3.0:
                    label = "平稳"
                elif score >= 2.0:
                    label = "波动"
                else:
                    label = "低沉"

                heatmap_data.append({
                    "month": m.get("month", f"{i+1}月"),
                    "fortune": score,
                    "label": label
                })

            heatmap = generate_monthly_heatmap(heatmap_data, "2026年每月运势热力图")
            monthly_data = monthly

        # 3. 置信度仪表盘
        confidence = analysis_result.get("overall_confidence", 0.5)
        gauge = generate_confidence_gauge(int(confidence * 100), "综合运势评分")
        if gauge:
            charts["gauge"] = gauge

        logger.info(f"图表生成完成: {len(charts)} 个图表")
        return {"charts": charts, "heatmap": heatmap, "monthly_data": monthly_data}

    except Exception as e:
        logger.error(f"图表生成失败: {e}")
        return {"charts": None, "heatmap": None, "monthly_data": []}


def generate_markdown_report(
    chart: Dict[str, Any],
    analysis_result: Dict[str, Any],
    target_year: int = 2026,
    use_llm: bool = True
) -> str:
    """
    生成Markdown格式的运势预测报告

    Args:
        chart: 命盘数据
        analysis_result: 分析结果
        target_year: 目标年份
        use_llm: 是否使用LLM生成（默认True）

    Returns:
        Markdown格式的报告内容
    """
    if use_llm and LLM_AND_PROMPTS_AVAILABLE:
        try:
            generator = LLMReportGenerator()
            return generator.generate_full_report(chart, analysis_result, target_year)
        except Exception as e:
            logger.warning(f"LLM生成失败，回退到模板模式: {e}")
            return _generate_template_report(chart, analysis_result, target_year)
    else:
        return _generate_template_report(chart, analysis_result, target_year)


def _generate_template_report(
    chart: Dict[str, Any],
    analysis_result: Dict[str, Any],
    target_year: int = 2026
) -> str:
    """生成模板化报告（备用）"""
    lines = []

    # 标题和元信息
    birth_info = chart.get("birth_info", {})
    name = birth_info.get("name", "命主")
    year_gan = birth_info.get("year_gan", "丙")
    year_zhi = birth_info.get("year_zhi", "子")
    overall_judgment = analysis_result.get("overall_judgment", "平")

    lines.append(f"# {name} {target_year}年运势预测报告\n")
    lines.append(f"> **命主**: {name}")
    lines.append(f"> **预测年份**: {target_year}年")
    lines.append(f"> **生成时间**: {datetime.now().strftime('%Y年%m月')}")
    lines.append("> **分析系统**: FengxianCyberTaoist 紫微斗数智能分析系统\n")
    lines.append("---\n")

    # ========== 一、命盘概览 ==========
    lines.append("## 一、命盘概览\n")
    lines.append("### 1.1 基本信息\n")
    lines.append("| 项目 | 内容 |")
    lines.append("|------|------|")
    lines.append(f"| 命主姓名 | {name} |")
    lines.append(f"| 出生年份 | {birth_info.get('year', '未知')}年 |")
    lines.append(f"| 命格特征 | {year_gan}{year_zhi}命 |")

    ming_gong = analysis_result.get("ming_gong", {})
    if ming_gong:
        lines.append(f"| 命宫主星 | {ming_gong.get('main_star', '天同')} |")

    transforms = analysis_result.get("transforms", {})
    if transforms:
        has_transforms = any([
            transforms.get("hua_lu"),
            transforms.get("hua_quan"),
            transforms.get("hua_ke"),
            transforms.get("hua_ji")
        ])
        if has_transforms:
            lines.append("| 四化格局 | 禄权科忌全配置 |")

    lines.append("")
    lines.append("### 1.2 四化星曜配置\n")
    lines.append("| 四化 | 星曜 | 所在宫位 | 能量属性 |")
    lines.append("|------|------|----------|----------|")

    transform_map = {
        "hua_lu": ("化禄", "机会与收获"),
        "hua_quan": ("化权", "权力与掌控"),
        "hua_ke": ("化科", "声誉与学习"),
        "hua_ji": ("化忌", "挑战与考验")
    }

    has_transform_data = False
    for key, (name_cn, attr) in transform_map.items():
        if key in transforms:
            has_transform_data = True
            t = transforms[key]
            star = t.get("star", "未知")
            palace = t.get("palace", "未知")
            lines.append(f"| {name_cn} | {star} | {palace} | {attr} |")

    if not has_transform_data:
        lines.append("| 化禄 | - | - | 待分析 |")
        lines.append("| 化权 | - | - | 待分析 |")
        lines.append("| 化科 | - | - | 待分析 |")
        lines.append("| 化忌 | - | - | 待分析 |")
    lines.append("")

    lines.append("### 1.3 综合判断\n")
    lines.append(f"**整体运势**: {overall_judgment}\n")
    judgment_desc = _get_judgment_description(overall_judgment, transforms)
    lines.append(f"{name}而言是{judgment_desc}。关键在于把握机遇的时机，以及应对挑战的智慧。\n")
    lines.append("---\n")

    # 其他章节使用简化模板...
    lines.append("## 二、四化详解\n")
    lines.append("*(详细内容请使用LLM模式生成)*\n")
    lines.append("---\n")

    lines.append("## 三、因果链分析\n")
    lines.append("*(详细内容请使用LLM模式生成)*\n")
    lines.append("---\n")

    lines.append("## 四、年度运势分析\n")
    lines.append("*(详细内容请使用LLM模式生成)*\n")
    lines.append("---\n")

    lines.append("## 五、性格画像\n")
    lines.append("*(详细内容请使用LLM模式生成)*\n")
    lines.append("---\n")

    lines.append("## 六、实用指南\n")
    lines.append("*(详细内容请使用LLM模式生成)*\n")
    lines.append("---\n")

    lines.append("## 七、核心提醒\n")
    lines.append("*(详细内容请使用LLM模式生成)*\n")
    lines.append("---\n")

    # 免责声明
    lines.append("## 八、免责声明\n")
    lines.append("本报告基于紫微斗数四化理论，通过AI智能分析生成，仅供参考。\n")
    lines.append("**命理是参考，你才是主角！**\n")
    lines.append(f"\n---\n\n*报告生成: FengxianCyberTaoist 紫微斗数智能分析系统*\n*生成日期: {datetime.now().strftime('%Y年%m月')}*")

    return "\n".join(lines)


def generate_complete_report(
    chart: Dict[str, Any],
    analysis_result: Dict[str, Any],
    output_dir: Optional[str] = None,
    target_year: int = 2026,
    generate_pdf: bool = True,
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    生成完整的运势预测报告

    Args:
        chart: 命盘数据
        analysis_result: 分析结果
        output_dir: 输出目录
        target_year: 预测年份
        generate_pdf: 是否生成PDF
        use_llm: 是否使用LLM生成（默认True）

    Returns:
        {
            "success": bool,
            "report_id": str,
            "markdown_path": str,
            "pdf_path": str,
            "charts_generated": int,
            "llm_generated": bool
        }
    """
    # 生成报告ID
    import uuid
    report_id = f"report_{uuid.uuid4().hex[:12]}"

    logger.info(f"开始生成报告: {report_id} (LLM模式: {use_llm})")

    # 1. 生成图表
    chart_data = generate_report_charts(analysis_result)
    charts = chart_data.get("charts")
    heatmap = chart_data.get("heatmap")
    charts_count = len(charts) if charts else 0

    # 2. 生成Markdown报告
    markdown_content = generate_markdown_report(
        chart, analysis_result, target_year, use_llm=use_llm
    )

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        md_path = output_dir / f"{report_id}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"Markdown报告已保存: {md_path}")
    else:
        md_path = None
        logger.info("未提供 output_dir，跳过文件保存")

    # 3. 生成PDF（如果启用）
    pdf_path = None
    if generate_pdf and CHART_AND_PDF_AVAILABLE:
        try:
            birth_info = chart.get("birth_info", {})
            name = birth_info.get("name", "命主")
            user_info = {
                "name": name,
                "year": str(target_year),
                "birth": f"{birth_info.get('year', '')}年",
                "judgment": analysis_result.get("overall_judgment", "运势平稳")
            }

            pdf_path = output_dir / f"{report_id}.pdf"

            markdown_to_pdf(
                markdown_text=markdown_content,
                title=f"{name} {target_year}年运势预测报告",
                output_path=str(pdf_path),
                charts=charts,
                user_info=user_info,
                heatmap=heatmap
            )

            logger.info(f"PDF报告已保存: {pdf_path}")
        except Exception as e:
            logger.error(f"PDF生成失败: {e}")
            pdf_path = None

    # 4. 保存元数据
    metadata = {
        "report_id": report_id,
        "chart_id": chart.get("chart_id"),
        "target_year": target_year,
        "analysis_result": analysis_result,
        "generated_at": datetime.now().isoformat(),
        "llm_generated": use_llm and LLM_AND_PROMPTS_AVAILABLE,
        "files": {
            "markdown": str(md_path),
            "pdf": str(pdf_path) if pdf_path else None
        }
    }

    if output_dir:
        meta_path = output_dir / f"{report_id}_metadata.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    result = {
        "success": True,
        "report_id": report_id,
        "output_dir": str(output_dir) if output_dir else None,
        "markdown_path": str(md_path) if md_path else None,
        "markdown_content": markdown_content,
        "pdf_path": str(pdf_path) if pdf_path else None,
        "charts_generated": charts_count,
        "llm_generated": use_llm and LLM_AND_PROMPTS_AVAILABLE
    }

    logger.info(f"报告生成完成: {report_id} (LLM: {result['llm_generated']})")
    return result


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="生成完整的运势预测报告")
    parser.add_argument("--name", "-n", default="命主", help="姓名")
    parser.add_argument("--birth", "-b", type=int, default=1997, help="出生年份")
    parser.add_argument("--year", "-y", type=int, default=2026, help="预测年份")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--no-pdf", action="store_true", help="不生成PDF")
    parser.add_argument("--no-llm", action="store_true", help="不使用LLM生成（模板模式）")

    args = parser.parse_args()

    # 构建示例命盘数据
    chart = {
        "chart_id": f"chart_{args.birth}",
        "birth_info": {
            "name": args.name,
            "year": args.birth,
            "year_gan": "丙",
            "year_zhi": "子"
        }
    }

    # 构建示例分析结果
    analysis_result = {
        "overall_judgment": "平",
        "overall_confidence": 0.55,
        "dimensions": {
            "事业": {"judgment": "吉", "confidence": 0.6, "reasoning": "贵人运强"},
            "财运": {"judgment": "平", "confidence": 0.5},
            "感情": {"judgment": "平", "confidence": 0.5},
            "健康": {"judgment": "吉", "confidence": 0.55},
            "人际关系": {"judgment": "吉", "confidence": 0.6}
        },
        "monthly_data": [
            {"month": "1月", "score": 3.8, "tip": "新年开好头"},
            {"month": "2月", "score": 3.5, "tip": "稳扎稳打"},
            {"month": "3月", "score": 4.0, "tip": "贵人出现"},
            {"month": "4月", "score": 3.6, "tip": "保持现状"},
            {"month": "5月", "score": 4.5, "tip": "全力以赴"},
            {"month": "6月", "score": 4.2, "tip": "乘胜追击"},
            {"month": "7月", "score": 3.4, "tip": "休养调整"},
            {"month": "8月", "score": 4.0, "tip": "贵人相助"},
            {"month": "9月", "score": 4.6, "tip": "再创佳绩"},
            {"month": "10月", "score": 3.7, "tip": "盘点收获"},
            {"month": "11月", "score": 3.5, "tip": "总结经验"},
            {"month": "12月", "score": 4.0, "tip": "年末冲刺"}
        ],
        "suggestions": [
            "把握两个高峰期（5月和9月）",
            "保持稳健心态",
            "善用贵人运",
            "注重学习提升",
            "保持身心健康"
        ]
    }

    # 生成报告
    result = generate_complete_report(
        chart=chart,
        analysis_result=analysis_result,
        output_dir=args.output,
        target_year=args.year,
        generate_pdf=not args.no_pdf,
        use_llm=not args.no_llm
    )

    print("\n" + "=" * 60)
    print("报告生成结果")
    print("=" * 60)
    print(f"报告ID: {result['report_id']}")
    print(f"输出目录: {result['output_dir']}")
    print(f"Markdown: {result['markdown_path']}")
    if result['pdf_path']:
        print(f"PDF: {result['pdf_path']}")
    else:
        print("PDF: 未生成")
    print(f"图表数量: {result['charts_generated']}")
    print(f"LLM生成: {'是' if result.get('llm_generated') else '否'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
