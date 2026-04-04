"""
小红书报告生成智能体 - XiaohongshuAgent

将专业命理报告转换为小红书风格内容:
- 通俗易懂的标题
- 情感共鸣的内容
- 互动引导标签
- 可视化图表占位符

参考: report_enhancement_plan_v3.md (Report D)
"""

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

# 配置日志
logger = logging.getLogger(__name__)

# ============ 小红书报告数据模型 ============

@dataclass
class XHSSection:
    """小红书内容板块"""
    title: str  # 板块标题
    emoji: str  # 板块emoji
    content: str  # 板块内容
    section_type: str = "normal"  # normal/golden/risk/highlight
    order: int = 0


@dataclass
class XHSReport:
    """小红书报告"""
    title: str  # 主标题
    subtitle: str  # 副标题
    key_rating: str  # "★★★★☆" 风格评分
    key_words: List[str]  # 关键词列表
    risk_alert: str  # 风险提醒
    best_months: List[str]  # 最佳月份
    worst_months: List[str]  # 需要注意的月份
    content_sections: List[XHSSection]  # 内容板块
    hashtags: List[str]  # 话题标签
    interaction_prompt: str  # 互动引导
    chart_placeholders: Dict[str, str]  # 图表占位符: 类型 -> 描述
    plain_summary: str  # 一段式总结
    generated_at: str = ""


# ============ 术语通俗化映射 ============

# 内置通俗化映射 (当JSON加载失败时使用)
BUILTIN_STAR_MAP = {
    "天同": {"popular": "乐天星", "desc": "性格温和，享受生活"},
    "天梁": {"popular": "责任星", "desc": "有责任心，喜欢帮助人"},
    "太阳": {"popular": "事业星", "desc": "追求成就，爱表现"},
    "破军": {"popular": "变动星", "desc": "喜欢变化，敢于冒险"},
    "禄存": {"popular": "财运星", "desc": "财运不错，存钱能力强"},
    "紫微": {"popular": "帝王星", "desc": "有领导力，贵气足"},
    "天府": {"popular": "财库星", "desc": "理财能力强"},
    "武曲": {"popular": "刚毅星", "desc": "性格刚强，做事果断"},
    "贪狼": {"popular": "欲望星", "desc": "欲望强烈，进取心强"},
    "巨门": {"popular": "口才星", "desc": "口才好，善于表达"},
    "太阴": {"popular": "温柔星", "desc": "性格温柔细腻"},
    "天机": {"popular": "智慧星", "desc": "聪明机敏，善于思考"},
    "廉贞": {"popular": "桃花星", "desc": "感情丰富，有魅力"},
    "七杀": {"popular": "冲锋星", "desc": "敢于冲锋陷阵"},
    "天相": {"popular": "辅佐星", "desc": "善于辅佐他人"},
}

BUILTIN_PALACE_MAP = {
    "官禄宫": {"popular": "事业宫", "desc": "工作、事业、成就"},
    "财帛宫": {"popular": "财运宫", "desc": "金钱、财务、投资"},
    "夫妻宫": {"popular": "感情宫", "desc": "恋爱、婚姻、伴侣"},
    "疾厄宫": {"popular": "健康宫", "desc": "健康、身体"},
    "迁移宫": {"popular": "出行宫", "desc": "外出、旅行"},
    "田宅宫": {"popular": "房产宫", "desc": "房产、家庭"},
    "福德宫": {"popular": "福气宫", "desc": "福气、享受"},
}

BUILTIN_TRANSFORM_MAP = {
    "化禄": {"popular": "机会来临", "desc": "好运到来，机会出现"},
    "化权": {"popular": "能力展现", "desc": "权力增加，能力被认可"},
    "化科": {"popular": "口碑提升", "desc": "名声变好，学习进步"},
    "化忌": {"popular": "挑战考验", "desc": "遇到困难，需要谨慎"},
}

BUILTIN_HASHTAGS = [
    "#2026运势", "#命理分析", "#星座运势", "#紫微斗数",
    "#财运", "#事业运", "#感情运", "#健康运",
    "#接好运", "#许愿"
]


# ============ 小红书Agent类 ============

class XiaohongshuAgent:
    """
    小红书报告生成智能体

    将专业命理报告转换为小红书风格内容:
    1. 生成吸引眼球的标题
    2. 提取关键信息和评分
    3. 生成情感共鸣的内容
    4. 添加话题标签和互动引导
    """

    def __init__(self, terminology_map_path: Optional[str] = None):
        """
        初始化小红书Agent

        Args:
            terminology_map_path: 术语映射文件路径
        """
        self.terminology_map = self._load_terminology_map(terminology_map_path)

    def _load_terminology_map(self, path: Optional[str] = None) -> Dict[str, Any]:
        """加载术语通俗化映射"""
        if path is None:
            # 默认路径
            base_path = Path(__file__).parent.parent / "resources" / "terminology_map.json"
            path = str(base_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load terminology map from {path}: {e}")
            # 返回内置映射
            return {
                "stars": BUILTIN_STAR_MAP,
                "palaces": BUILTIN_PALACE_MAP,
                "transforms": BUILTIN_TRANSFORM_MAP,
                "xhs_hashtags": {"trending": BUILTIN_HASHTAGS}
            }

    def _popularize_star(self, star_name: str) -> str:
        """星曜通俗化"""
        # 从 star_names 获取
        star_names = self.terminology_map.get("star_names", {})
        if star_name in star_names:
            return star_names[star_name]
        # 模糊匹配
        for key, value in star_names.items():
            if key.replace("星", "") in star_name.replace("星", ""):
                return value
        # 返回简化名称
        return star_name.replace("星", "")

    def _popularize_palace(self, palace_name: str) -> str:
        """宫位通俗化"""
        # 从 term_to_plain 获取
        term_to_plain = self.terminology_map.get("term_to_plain", {})
        if palace_name in term_to_plain:
            return term_to_plain[palace_name]
        # 模糊匹配
        for key, value in term_to_plain.items():
            if key in palace_name:
                return value
        return palace_name

    def _popularize_transform(self, transform_name: str) -> str:
        """四化通俗化"""
        # 从 term_to_plain 获取
        term_to_plain = self.terminology_map.get("term_to_plain", {})
        if transform_name in term_to_plain:
            return term_to_plain[transform_name]
        # 模糊匹配
        for key, value in term_to_plain.items():
            if key in transform_name:
                return value
        return transform_name

    def generate_xhs_report(
        self,
        report: Any,
        user_name: str = "命主",
        user_type: str = ""
    ) -> XHSReport:
        """
        生成小红书报告

        Args:
            report: ThreeLayerDivinationReport 专业报告
            user_name: 用户昵称
            user_type: 用户类型 (如 "天同星人")

        Returns:
            XHSReport: 小红书格式报告
        """
        # 提取关键信息
        key_words = self._extract_key_words(report)
        best_months = self._extract_best_months(report)
        worst_months = self._extract_worst_months(report)
        risk_alert = self._extract_risk_alert(report)
        rating = self._calculate_rating(report)

        # 生成标题
        title = self.generate_engaging_title(report, user_type)

        # 生成内容板块
        content_sections = self._generate_content_sections(report, user_name)

        # 生成话题标签
        hashtags = self.format_hashtags(report)

        # 生成互动引导
        interaction_prompt = self._generate_interaction_prompt(user_name, user_type)

        # 生成图表占位符
        chart_placeholders = self._generate_chart_placeholders(report)

        # 生成一段式总结
        plain_summary = self._generate_plain_summary(report, user_name, user_type)

        return XHSReport(
            title=title,
            subtitle=f"专属{user_type}运势分析" if user_type else "专属运势分析",
            key_rating=rating,
            key_words=key_words,
            risk_alert=risk_alert,
            best_months=best_months,
            worst_months=worst_months,
            content_sections=content_sections,
            hashtags=hashtags,
            interaction_prompt=interaction_prompt,
            chart_placeholders=chart_placeholders,
            plain_summary=plain_summary,
            generated_at=self._get_current_time()
        )

    def _extract_key_words(self, report: Any) -> List[str]:
        """从报告中提取关键词"""
        keywords = []

        # 从专业术语提取
        if hasattr(report, 'causal_chain_result') and report.causal_chain_result:
            chain = report.causal_chain_result
            if hasattr(chain, 'key_chains') and chain.key_chains:
                for c in chain.key_chains[:3]:
                    if isinstance(c, dict) and 'cause' in c:
                        keywords.append(c['cause'][:20])
                    elif isinstance(c, dict) and 'type' in c:
                        keywords.append(c['type'])

        # 从建议中提取
        if hasattr(report, 'suggestions') and report.suggestions:
            for s in report.suggestions[:3]:
                if isinstance(s, str):
                    # 提取动词或名词
                    words = re.findall(r'[\u4e00-\u9fa5]{2,4}', s)
                    if words:
                        keywords.append(words[0])

        # 从维度分析中提取
        if hasattr(report, 'dimensions') and report.dimensions:
            for dim, analysis in list(report.dimensions.items())[:3]:
                if isinstance(analysis, dict) and 'judgment' in analysis:
                    keywords.append(f"{dim}{analysis['judgment']}")

        # 确保有默认值 - 基于judgment动态生成
        if not keywords:
            judgment = getattr(report, 'overall_judgment', '平')
            if judgment == '吉':
                keywords = ["好运连连", "把握时机", "乘势而上"]
            elif judgment == '凶':
                keywords = ["谨慎行事", "静待时机", "趋吉避凶"]
            else:
                keywords = ["稳中求进", "把握机会", "注意健康"]

        return keywords[:5]

    def _extract_best_months(self, report: Any) -> List[str]:
        """提取最佳月份"""
        best_months = []

        if hasattr(report, 'case_based_result') and report.case_based_result:
            case_result = report.case_based_result
            if hasattr(case_result, 'predictions'):
                for month, pred in case_result.predictions.items():
                    if isinstance(pred, dict):
                        score = pred.get('probability', pred.get('score', 0.5))
                        if score > 0.7:
                            best_months.append(month)

        # 从因果链中提取
        if hasattr(report, 'causal_chain_result') and report.causal_chain_result:
            chain = report.causal_chain_result
            if hasattr(chain, 'key_chains'):
                for c in chain.key_chains:
                    if isinstance(c, dict):
                        period = c.get('period', '')
                        if '月' in period:
                            best_months.append(period)

        if not best_months:
            # 默认 - 从因果链或月份分析中动态获取，不使用硬编码
            # 这里返回空列表，由调用方处理
            best_months = []

        return list(set(best_months))[:3] if best_months else []

    def _extract_worst_months(self, report: Any) -> List[str]:
        """提取需要注意的月份"""
        worst_months = []

        if hasattr(report, 'case_based_result') and report.case_based_result:
            case_result = report.case_based_result
            if hasattr(case_result, 'predictions'):
                for month, pred in case_result.predictions.items():
                    if isinstance(pred, dict):
                        score = pred.get('probability', pred.get('score', 1))
                        if score < 0.4:
                            worst_months.append(month)

        if not worst_months:
            # 默认 - 从因果链或月份分析中动态获取，不使用硬编码
            worst_months = []

        return list(set(worst_months))[:2] if worst_months else []

    def _extract_risk_alert(self, report: Any) -> str:
        """提取风险提醒"""
        risk_alerts = []

        if hasattr(report, 'causal_chain_result') and report.causal_chain_result:
            chain = report.causal_chain_result
            if hasattr(chain, 'explanation'):
                # 提取风险相关的句子
                text = chain.explanation
                sentences = re.split(r'[。;]', text)
                for s in sentences:
                    if any(kw in s for kw in ['注意', '小心', '谨慎', '避免', '风险', '凶']):
                        risk_alerts.append(s.strip()[:50])

        if hasattr(report, 'suggestions'):
            for s in report.suggestions:
                if isinstance(s, str) and any(kw in s for kw in ['避免', '注意', '谨慎']):
                    risk_alerts.append(s.strip()[:50])

        if not risk_alerts:
            risk_alerts = ["保持心态平和，注意健康管理"]

        return risk_alerts[0] if risk_alerts else "保持积极心态，谨慎把握机会"

    def _calculate_rating(self, report: Any) -> str:
        """计算运势评分"""
        rating_map = {
            "吉": "★★★★★",
            "平": "★★★☆☆",
            "凶": "★★☆☆☆"
        }

        # 从综合判断获取
        judgment = getattr(report, 'overall_judgment', '平')
        rating = rating_map.get(judgment, "★★★☆☆")

        # 如果有置信度，可以调整
        confidence = getattr(report, 'overall_confidence', 0.5)
        if confidence >= 0.8:
            rating = rating.replace("☆", "★").replace("☆", "★")
        elif confidence < 0.5:
            rating = rating.replace("★", "☆").replace("★", "☆")

        return rating

    def generate_engaging_title(self, report: Any, user_type: str = "") -> str:
        """
        生成吸引眼球的标题

        参考: report_enhancement_plan_v3.md 4.1 标题模板
        """
        target_year = getattr(report, 'target_year', 2026)
        judgment = getattr(report, 'overall_judgment', '平')

        # 标题模板库
        title_templates = [
            "{year}年运势 | {user_type}专属分析，今年{judgment_desc}",
            "🔥{year}年运势预警 | {user_type}注意，{key_topic}",
            "{user_type}{year}完整运势，看完你就懂了",
            "{user_type}的{year}年，先苦后甜还是一路旺？",
            "2026年运势 | 你是哪种命？{user_type}专属分析"
        ]

        # 判断描述
        judgment_desc_map = {
            "吉": "一路顺遂",
            "平": "稳中有升",
            "凶": "先苦后甜"
        }
        judgment_desc = judgment_desc_map.get(judgment, "运势平稳")

        # 提取关键话题
        key_topic = "把握机会"
        if hasattr(report, 'dimensions'):
            for dim, analysis in report.dimensions.items():
                if isinstance(analysis, dict) and 'judgment' in analysis:
                    if analysis['judgment'] == '凶':
                        key_topic = f"{dim}要注意"
                        break

        # 选择模板
        import random
        template = random.choice(title_templates)

        # 如果没有用户类型，生成一个
        if not user_type:
            if hasattr(report, 'causal_chain_result') and report.causal_chain_result:
                chain = report.causal_chain_result
                if hasattr(chain, 'key_chains') and chain.key_chains:
                    first_chain = chain.key_chains[0]
                    if isinstance(first_chain, dict):
                        user_type = first_chain.get('main_star', '福气满满')
            if not user_type:
                user_type = "福气满满"

        return template.format(
            year=target_year,
            user_type=user_type,
            judgment_desc=judgment_desc,
            key_topic=key_topic
        )

    def format_hashtags(self, report: Any) -> List[str]:
        """
        生成话题标签

        Returns:
            标签列表，包括:
            - 热门标签 (#2026运势 等)
            - 维度标签 (#财运 等)
            - 星曜标签 (#天同星 等)
        """
        hashtags = set()

        # 添加默认趋势标签
        default_hashtags = [
            "#2026运势", "#命理分析", "#星座运势",
            "#紫微斗数", "#财运", "#事业运", "#感情运",
            "#健康运", "#接好运", "#许愿"
        ]
        hashtags.update(default_hashtags[:5])

        # 添加维度标签
        if hasattr(report, 'dimensions'):
            for dim in report.dimensions.keys():
                dim.lower()
                if '财' in dim:
                    hashtags.add("#财运")
                elif '事' in dim or '业' in dim:
                    hashtags.add("#事业运")
                elif '情' in dim or '爱' in dim:
                    hashtags.add("#感情运")
                elif '健' in dim:
                    hashtags.add("#健康运")

        # 从报告中提取星曜并添加标签
        if hasattr(report, 'causal_chain_result') and report.causal_chain_result:
            chain = report.causal_chain_result
            if hasattr(chain, 'key_chains'):
                for c in chain.key_chains:
                    if isinstance(c, dict):
                        star = c.get('main_star', '')
                        if star and star not in ['星', '']:
                            hashtags.add(f"#{star}")

        # 从参考案例中提取
        if hasattr(report, 'reference_cases'):
            for case in report.reference_cases[:2]:
                if isinstance(case, dict):
                    case_type = case.get('case_type', '')
                    if case_type:
                        hashtags.add(f"#{case_type}")

        # 添加用户类型标签
        hashtags.add("#命理")

        return list(hashtags)[:10]

    def transform_to_emotion_first(self, report: Any, user_name: str = "命主") -> str:
        """
        将报告转换为情感优先的内容

        特点:
        - 开篇放结论
        - 使用情感化语言
        - 避免专业术语
        """
        lines = []

        # 开篇金句
        lines.append(self._generate_opening_golden_line(report, user_name))
        lines.append("")

        # 关键信息卡片
        lines.append("📊 今年运势速览")
        lines.append("-" * 20)
        lines.append(f"🔥 关键词: {', '.join(self._extract_key_words(report))}")
        lines.append(f"⭐ 综合评分: {self._calculate_rating(report)}")
        lines.append(f"⚠️ 需要注意: {self._extract_risk_alert(report)}")
        lines.append(f"✨ 最佳月份: {', '.join(self._extract_best_months(report))}")
        lines.append("")

        # 分维度情感化解读
        lines.append("💫 详细解读")
        lines.append("-" * 20)

        if hasattr(report, 'dimensions'):
            for dim, analysis in report.dimensions.items():
                lines.append(f"\n**{dim}**")
                if isinstance(analysis, dict):
                    judgment = analysis.get('judgment', '平')
                    reasoning = analysis.get('reasoning', '')

                    # 情感化判断
                    emotion_map = {
                        "吉": "棒棒的！",
                        "平": "还不错",
                        "凶": "需要留心"
                    }
                    lines.append(emotion_map.get(judgment, ""))

                    # 通俗化解释
                    if reasoning:
                        # 简化专业术语
                        simplified = self._simplify_text(reasoning)
                        lines.append(simplified[:100])

        # 趋避建议（情感化）
        lines.append("\n💡 开运建议")
        lines.append("-" * 20)
        if hasattr(report, 'suggestions'):
            for i, s in enumerate(report.suggestions[:3], 1):
                if isinstance(s, str):
                    lines.append(f"{i}. {s}")

        return "\n".join(lines)

    def _generate_opening_golden_line(self, report: Any, user_name: str) -> str:
        """生成开篇金句"""
        judgment = getattr(report, 'overall_judgment', '平')
        best_months = self._extract_best_months(report)

        templates = {
            "吉": "{name}，今年运气超好！{month}月份尤其顺利，记得抓住机会！",
            "平": "{name}，今年整体平稳，{month}月份会有惊喜哦~",
            "凶": "{name}，今年有点挑战，但下半年会好转！{month}月份特别注意~"
        }

        template = templates.get(judgment, templates["平"])
        month = best_months[0] if best_months else "年中"

        return template.format(name=user_name, month=month)

    def _simplify_text(self, text: str) -> str:
        """简化专业术语"""
        result = text

        # 从 star_names 替换
        star_names = self.terminology_map.get("star_names", {})
        for star, desc in star_names.items():
            if star in result:
                result = result.replace(star, desc)

        # 从 term_to_plain 替换
        term_to_plain = self.terminology_map.get("term_to_plain", {})
        for term, plain in term_to_plain.items():
            if term in result:
                result = result.replace(term, plain)

        # 从 judgment_mapping 替换
        judgment_mapping = self.terminology_map.get("judgment_mapping", {})
        for judgment, emotion in judgment_mapping.items():
            if judgment in result:
                result = result.replace(judgment, emotion)

        return result

    def _generate_content_sections(self, report: Any, user_name: str) -> List[XHSSection]:
        """生成内容板块 - 增强版：每个板块都有通俗、详细的分析"""
        sections = []

        # 1. 开篇金句
        golden_line = self._generate_opening_golden_line(report, user_name)
        sections.append(XHSSection(
            title="开篇",
            emoji="🌟",
            content=golden_line,
            section_type="golden",
            order=1
        ))

        # 2. 关键词速览
        keywords = self._extract_key_words(report)
        keywords_text = "、".join(keywords[:5])
        sections.append(XHSSection(
            title="今年关键词",
            emoji="🔥",
            content=f"这5个词概括了你的全年运势：{keywords_text}。简单来说，你今年将在这些方面有明显的转变和收获，值得重点关注。",
            section_type="highlight",
            order=2
        ))

        # 3. 风险提醒
        risk = self._extract_risk_alert(report)
        risk_detail = self._get_risk_detail(risk)
        sections.append(XHSSection(
            title="需要注意",
            emoji="⚠️",
            content=f"{risk}\n\n{risk_detail}",
            section_type="risk",
            order=3
        ))

        # 4. 最佳月份
        best_months = self._extract_best_months(report)
        months_text = "、".join(best_months) if best_months else "年中"
        sections.append(XHSSection(
            title="好运月份",
            emoji="✨",
            content=f"这几个月份运势超旺：{months_text}，记得好好把握！具体来说，这些月份事业上有晋升或合作机会，财运上可能有意外收获，感情上人际相处会更顺利。建议在这些月份主动出击，不要错过好时机。",
            section_type="highlight",
            order=4
        ))

        # 5. 分维度详细解读（增强：不再截断，添加通俗分析）
        if hasattr(report, 'dimensions'):
            for dim, analysis in report.dimensions.items():
                if isinstance(analysis, dict):
                    judgment = analysis.get('judgment', '平')
                    reasoning = analysis.get('reasoning', '')
                    key_factors = analysis.get('key_factors', [])
                    emoji = "🟢" if judgment == "吉" else "🟡" if judgment == "平" else "🔴"

                    # 构建详细分析内容
                    content_parts = []

                    # 核心判断
                    if reasoning:
                        # 使用完整reasoning（不再截断到80字符）
                        content_parts.append(reasoning)

                    # 添加通俗解读
                    plain_interp = self._generate_dimension_plain_interpretation(dim, judgment, analysis)
                    if plain_interp:
                        content_parts.append(plain_interp)

                    # 添加关键因素（如果有）
                    if key_factors:
                        factors_text = "、".join(key_factors[:3]) if isinstance(key_factors, list) else str(key_factors)
                        content_parts.append(f"🔑 今年关键：{factors_text}")

                    content = "\n\n".join(content_parts) if content_parts else f"{dim}整体{judgment}，需要多加关注。"

                    sections.append(XHSSection(
                        title=f"{dim}运势",
                        emoji=emoji,
                        content=content,
                        section_type="normal",
                        order=5
                    ))

        # 6. 趋避建议（增强：解释原因和具体做法）
        if hasattr(report, 'suggestions') and report.suggestions:
            suggestions_lines = []
            for i, s in enumerate(report.suggestions[:5], 1):
                if isinstance(s, dict):
                    title = s.get('title', s.get('suggestion', str(s)))
                    reason = s.get('reason', '')
                    action = s.get('action', '')
                    suggestions_lines.append(f"{i}. **{title}**")
                    if reason:
                        suggestions_lines.append(f"   原因：{reason}")
                    if action:
                        suggestions_lines.append(f"   做法：{action}")
                else:
                    # 通用建议扩展
                    expanded = self._expand_suggestion(str(s))
                    suggestions_lines.append(f"{i}. {expanded}")
            sections.append(XHSSection(
                title="开运指南",
                emoji="💡",
                content="\n".join(suggestions_lines),
                section_type="normal",
                order=6
            ))

        return sorted(sections, key=lambda x: x.order)

    def _generate_interaction_prompt(self, user_name: str, user_type: str) -> str:
        """生成互动引导"""
        prompts = [
            f"你是{user_type}吗？评论区告诉我你的主星配置，我来帮你分析！",
            f"你的{user_type}运势准不准？评论区说说你的感受~",
            f"想知道更多关于{user_type}的分析吗？关注我，后台私信你的出生日期！",
            "这期运势分析对你有帮助吗？点赞收藏，更多内容持续更新~"
        ]

        import random
        return random.choice(prompts)

    def _generate_chart_placeholders(self, report: Any) -> Dict[str, str]:
        """生成图表占位符描述"""
        placeholders = {}

        # 雷达图
        placeholders["radar"] = (
            "[雷达图: 五维运势]\n"
            "维度: 事业 ★★★★☆ | 财运 ★★★☆☆ | 感情 ★★★★☆ | 健康 ★★★☆☆ | 人际 ★★★★☆"
        )

        # 月度趋势图 - 已移除
        # 星曜分布图
        placeholders["star_distribution"] = (
            "[星曜分布图]\n"
            "主星: 天同 ★★★\n"
            "辅星: 左辅、右弼"
        )

        return placeholders

    def _generate_plain_summary(self, report: Any, user_name: str, user_type: str) -> str:
        """生成一段式总结"""
        judgment = getattr(report, 'overall_judgment', '平')
        best_months = self._extract_best_months(report)
        risk = self._extract_risk_alert(report)[:30]

        summaries = {
            "吉": f"{user_name}是{user_type}，{getattr(report, 'target_year', '2026')}年整体运势非常好！"
                   f"上半年有贵人相助，下半年财运事业双丰收。"
                   f"最佳月份是{', '.join(best_months[:2])}，记得好好把握！",

            "平": f"{user_name}是{user_type}，{getattr(report, 'target_year', '2026')}年运势平稳。"
                  f"虽然会有一些小波折，但整体方向是向好的。"
                  f"特别注意{risk}，把握好{', '.join(best_months[:2])}这几个月份，全年顺遂~",

            "凶": f"{user_name}是{user_type}，{getattr(report, 'target_year', '2026')}年开头可能会有挑战。"
                  f"上半年需要谨慎行事，{risk}。"
                  f"不过别担心，下半年运势会逐渐好转，{', '.join(best_months[:2])}月份会有转机！"
        }

        return summaries.get(judgment, summaries["平"])

    def _get_risk_detail(self, risk: str) -> str:
        """为风险提醒添加详细说明"""
        if not risk:
            return "保持积极心态，遇到问题冷静应对即可。"
        # 基于风险类型提供具体建议
        if any(kw in risk for kw in ['健康', '身体', '疾病']):
            return "建议：保持规律作息，适当运动，不要过度劳累。遇到身体不适及时就医，不要拖延。"
        if any(kw in risk for kw in ['财务', '金钱', '破财', '投资']):
            return "建议：大额支出前三思，谨慎投资，不要轻信高收益理财。建议保守理财，守住本金。"
        if any(kw in risk for kw in ['感情', '婚姻', '争吵', '口角']):
            return "建议：多沟通少争执，遇到分歧换位思考。多给对方一些理解和包容，不要冷战。"
        if any(kw in risk for kw in ['事业', '工作', '小人']):
            return "建议：与同事保持良好关系，做事留有余地。遇到阻碍不要硬碰，以柔克刚更有效。"
        if any(kw in risk for kw in ['意外', '事故', '风险']):
            return "建议：出行注意安全，做事稳重不冒险。重要决策建议找人商量，不要独断专行。"
        return "建议：保持警觉，谨慎行事即可化险为夷。"

    def _generate_dimension_plain_interpretation(self, dim: str, judgment: str, analysis: dict) -> str:
        """为维度分析生成通俗解读"""
        # 维度通俗化
        dim_plain_map = {
            "事业": "工作、事业、成就",
            "财运": "金钱、收入、投资理财",
            "感情": "恋爱、婚姻、人际关系",
            "健康": "身体、疾病、养生",
            "学业": "学习、考试、进修",
            "人际": "朋友、社交、人缘",
            "综合": "整体运势、人生方向",
        }
        dim_meaning = dim_plain_map.get(dim, dim)

        # 判断解读
        judgment_interp = {
            "吉": f"今年{dim_meaning}方面运势很好，有机遇也有收获，值得积极把握。",
            "平": f"今年{dim_meaning}方面运势平稳，不会有大起大落，稳扎稳打就能有收获。",
            "凶": f"今年{dim_meaning}方面需要多留心，可能会有一些挑战，但危机也是转机。",
        }

        interp = judgment_interp.get(judgment, f"今年{dim_meaning}方面需要根据具体情况判断。")

        # 如果有置信度，加上说明
        confidence = analysis.get('confidence', 0)
        if confidence > 0:
            conf_level = "高" if confidence > 0.7 else "中" if confidence > 0.4 else "低"
            interp += f"（分析置信度：{conf_level}）"

        return interp

    def _expand_suggestion(self, suggestion: str) -> str:
        """扩展简单建议为详细的通俗分析"""
        s = suggestion.strip()

        # 基于关键词匹配扩展
        if any(kw in s for kw in ['谨慎', '保守', '小心']):
            return f"{s}。通俗来说就是：不要急于做决定，遇到大事先放一放再做判断更稳妥。"
        if any(kw in s for kw in ['把握', '积极', '主动']):
            return f"{s}。意思是：遇到好机会不要犹豫，勇敢迈出第一步，往往收获更大。"
        if any(kw in s for kw in ['理财', '投资', '财务']):
            return f"{s}。建议分散投资，不要把所有钱放在一个地方，稳健为主。"
        if any(kw in s for kw in ['健康', '身体', '锻炼']):
            return f"{s}。建议养成良好生活习惯，适度运动，身体是革命的本钱。"
        if any(kw in s for kw in ['人际', '社交', '关系']):
            return f"{s}。建议多维护老朋友关系，社交圈不要封闭，好人缘能带来意想不到的帮助。"
        if any(kw in s for kw in ['学习', '读书', '进修']):
            return f"{s}。建议今年是学习提升的好年份，多学点技能对事业发展有帮助。"
        if any(kw in s for kw in ['感情', '婚姻', '恋爱']):
            return f"{s}。建议多花时间陪伴伴侣，沟通比物质更能增进感情。"
        if any(kw in s for kw in ['事业', '工作', '创业']):
            return f"{s}。建议稳中求进，不要冒大风险，团队合作比单打独斗更有效。"

        # 默认扩展
        if len(s) < 15:
            return f"{s}，这一点对今年整体运势有重要影响，值得认真对待。"
        return s

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def format_markdown(self, xhs_report: XHSReport) -> str:
        """
        格式化输出为Markdown

        输出格式符合小红书风格:
        - emoji装饰
        - 清晰的标题层级
        - 图表占位符
        - 互动引导
        """
        lines = []

        # 元数据头
        lines.append("---")
        lines.append(f"title: \"{xhs_report.title}\"")
        lines.append(f"tags: {xhs_report.hashtags[:5]}")
        lines.append("---")
        lines.append("")

        # 主标题
        lines.append(f"# {xhs_report.title}")
        lines.append(f"*{xhs_report.subtitle}*")
        lines.append("")

        # 评分和关键信息
        lines.append(f"**综合评分**: {xhs_report.key_rating}")
        lines.append("")

        # 开篇
        for section in xhs_report.content_sections:
            if section.section_type == "golden":
                lines.append(f"{section.emoji} **{section.content}**")
                lines.append("")

        # 关键词
        lines.append("**🔥 今年关键词**")
        lines.append("、".join(xhs_report.key_words[:5]))
        lines.append("")

        # 风险提醒
        lines.append(f"**⚠️ 要注意**: {xhs_report.risk_alert}")
        lines.append("")

        # 好运月
        if xhs_report.best_months:
            lines.append(f"**✨ 好运月**: {', '.join(xhs_report.best_months)}")
            lines.append("")

        lines.append("---")
        lines.append("")

        # 图表占位符
        if xhs_report.chart_placeholders:
            lines.append("## 📊 运势可视化")
            lines.append("")
            for chart_type, description in xhs_report.chart_placeholders.items():
                lines.append(description)
                lines.append("")

        # 详细内容
        lines.append("## 💫 详细解读")
        lines.append("")

        for section in xhs_report.content_sections:
            if section.section_type != "golden":
                emoji = section.emoji
                lines.append(f"### {emoji} {section.title}")
                lines.append(section.content)
                lines.append("")

        # 话题标签
        lines.append("---")
        lines.append("")
        lines.append(" ".join(xhs_report.hashtags))
        lines.append("")

        # 互动引导
        lines.append(f"## 📣 {xhs_report.interaction_prompt}")
        lines.append("")

        # 结尾
        lines.append("---")
        lines.append(f"*报告生成时间: {xhs_report.generated_at}*")
        lines.append("*由FengxianCyberTaoist紫微斗数智能分析系统生成*")

        return "\n".join(lines)

    def format_json(self, xhs_report: XHSReport) -> Dict[str, Any]:
        """格式化输出为JSON"""
        return {
            "title": xhs_report.title,
            "subtitle": xhs_report.subtitle,
            "key_rating": xhs_report.key_rating,
            "key_words": xhs_report.key_words,
            "risk_alert": xhs_report.risk_alert,
            "best_months": xhs_report.best_months,
            "worst_months": xhs_report.worst_months,
            "content_sections": [
                {
                    "title": s.title,
                    "emoji": s.emoji,
                    "content": s.content,
                    "section_type": s.section_type
                }
                for s in xhs_report.content_sections
            ],
            "hashtags": xhs_report.hashtags,
            "interaction_prompt": xhs_report.interaction_prompt,
            "chart_placeholders": xhs_report.chart_placeholders,
            "plain_summary": xhs_report.plain_summary,
            "generated_at": xhs_report.generated_at
        }


# ============ 便捷函数 ============

def generate_xhs_report_sync(
    report: Any,
    user_name: str = "命主",
    user_type: str = "",
    terminology_map_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    同步生成小红书报告

    Args:
        report: ThreeLayerDivinationReport
        user_name: 用户昵称
        user_type: 用户类型
        terminology_map_path: 术语映射文件路径

    Returns:
        Dict: 包含 markdown 和 data 两种格式
    """
    agent = XiaohongshuAgent(terminology_map_path)
    xhs_report = agent.generate_xhs_report(report, user_name, user_type)

    return {
        "markdown": agent.format_markdown(xhs_report),
        "data": agent.format_json(xhs_report)
    }


async def generate_xhs_report_async(
    report: Any,
    user_name: str = "命主",
    user_type: str = "",
    terminology_map_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    异步生成小红书报告

    Args:
        report: ThreeLayerDivinationReport
        user_name: 用户昵称
        user_type: 用户类型
        terminology_map_path: 术语映射文件路径

    Returns:
        Dict: 包含 markdown 和 data 两种格式
    """
    import asyncio

    # 对于CPU密集型操作，使用线程池
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        generate_xhs_report_sync,
        report, user_name, user_type, terminology_map_path
    )
