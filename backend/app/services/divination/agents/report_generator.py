"""
ReportGenerator - Markdown报告生成器

生成主报告+分报告格式的紫微斗数分析报告
- 并行生成各分报告
- 汇总生成主报告

三层融合预测报告：
- 因果链推理 (40%)
- 案例涌现推理 (35%)
- 多Agent共识验证 (25%)
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .report_generator_types import (
    DimensionAnalysis,
    CausalChainAnalysis,
    CaseBasedAnalysis,
    MultiAgentAnalysis,
    ThreeLayerPredictionReport,
    ReportBundle,
)
from .report_generator_constants import (
    CAUSAL_WEIGHT,
    CASE_BASED_WEIGHT,
    MULTI_AGENT_WEIGHT,
    CORE_DIMENSIONS,
)

# 配置日志
logger = logging.getLogger(__name__)


# ============ Markdown格式化工具 ============

def _format_star_section(data: Any) -> str:
    """格式化星曜分析分报告

    支持传入 dict 或 dataclass 对象。
    - dict: 使用 get() 方法访问
    - dataclass: 使用属性访问
    """
    lines = ["## 星曜分析\n"]

    # 统一数据访问方式 - 兼容 dict 和 dataclass
    def get_value(obj: Any, key: str, default: Any = None) -> Any:
        """从 dict 或 dataclass 获取值"""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def get_list(obj: Any, key: str, default: list = None) -> list:
        """获取列表类型属性"""
        if default is None:
            default = []
        val = get_value(obj, key, default)
        return val if isinstance(val, list) else default

    # 主星解读
    main_stars = get_list(data, "main_stars", [])
    if main_stars:
        lines.append("### 主星解读\n")
        for item in main_stars:
            if isinstance(item, dict):
                lines.append(f"- **{item.get('star_name', item.get('star', '未知'))}**: {item.get('interpretation', '')}")
            elif hasattr(item, 'star_name'):
                lines.append(f"- **{item.star_name}**: {item.interpretation}")
            elif isinstance(item, str):
                lines.append(f"- {item}")
        lines.append("")

    # 辅星解读
    aux_stars = get_list(data, "auxiliary_stars", [])
    if aux_stars:
        lines.append("### 辅星解读\n")
        for item in aux_stars:
            if isinstance(item, dict):
                lines.append(f"- **{item.get('star_name', item.get('star', '未知'))}**: {item.get('interpretation', '')}")
            elif hasattr(item, 'star_name'):
                lines.append(f"- **{item.star_name}**: {item.interpretation}")
            elif isinstance(item, str):
                lines.append(f"- {item}")
        lines.append("")

    # 煞星影响
    sha_stars = get_list(data, "sha_stars", [])
    if sha_stars:
        lines.append("### 煞星影响\n")
        for item in sha_stars:
            if isinstance(item, dict):
                lines.append(f"- **{item.get('star_name', item.get('star', '未知'))}**: {item.get('interpretation', '')}")
            elif hasattr(item, 'star_name'):
                lines.append(f"- **{item.star_name}**: {item.interpretation}")
            elif isinstance(item, str):
                lines.append(f"- {item}")
        lines.append("")

    # 四化星
    transform_stars = get_list(data, "transform_stars", [])
    if transform_stars:
        lines.append("### 四化星\n")
        for item in transform_stars:
            if isinstance(item, dict):
                lines.append(f"- **{item.get('star_name', item.get('star', '未知'))}**: {item.get('interpretation', '')}")
            elif hasattr(item, 'star_name'):
                lines.append(f"- **{item.star_name}**: {item.interpretation}")
            elif isinstance(item, str):
                lines.append(f"- {item}")
        lines.append("")

    # 性格总结 - 尝试多个可能的属性名
    personality = (
        get_value(data, "personality_summary") or
        get_value(data, "summary") or
        get_value(data, "character_summary", "")
    )
    if personality:
        lines.append("### 性格总结\n")
        lines.append(f"{personality}\n")

    # 宫位星曜概览
    palace_star_summary = get_value(data, "palace_star_summary", {})
    if palace_star_summary:
        lines.append("### 宫位星曜概览\n")
        for palace, stars in palace_star_summary.items():
            if isinstance(stars, list):
                stars_str = ", ".join(stars)
            else:
                stars_str = str(stars)
            lines.append(f"- **{palace}**: {stars_str}")
        lines.append("")

    return "\n".join(lines)


def _format_palace_section(data: Any) -> str:
    """格式化宫位分析分报告

    支持传入 dict 或 dataclass 对象。
    """
    lines = ["## 宫位分析\n"]

    # 统一数据访问方式
    def get_value(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # 宫位强弱 - 尝试从 palace_results 构建
    palace_results = get_value(data, "palace_results", [])
    if palace_results and isinstance(palace_results, list):
        lines.append("### 宫位强弱\n")
        for result in palace_results:
            if isinstance(result, dict):
                palace = result.get("palace_name", result.get("name", "未知"))
                score = result.get("score", {})
                if isinstance(score, dict):
                    score_val = score.get("total_score", 50)
                else:
                    score_val = 50
            elif hasattr(result, 'palace_name') and hasattr(result, 'score'):
                palace = result.palace_name
                score_val = result.score.total_score if hasattr(result.score, 'total_score') else 50
            else:
                palace = str(result)
                score_val = 50
            level = "🟢强" if score_val >= 70 else "🟡中" if score_val >= 40 else "🔴弱"
            lines.append(f"- **{palace}**: {level} ({score_val}分)")
        lines.append("")

    # 最强/最弱宫位
    strongest = get_value(data, "strongest_palaces", [])
    if not strongest:
        strongest = get_value(data, "strongest_palace", "")
        if strongest:
            strongest = [strongest]
    weakest = get_value(data, "weakest_palaces", [])
    if not weakest:
        weakest = get_value(data, "weakest_palace", "")
        if weakest:
            weakest = [weakest]

    if strongest:
        lines.append(f"**最强宫位**: {', '.join(strongest)}\n")
    if weakest:
        lines.append(f"**最弱宫位**: {', '.join(weakest)}\n")
    lines.append("")

    # 关键宫位
    key_palaces = get_value(data, "key_palaces", [])
    if key_palaces:
        lines.append("### 关键宫位\n")
        for palace in key_palaces:
            lines.append(f"- {palace}")
        lines.append("")

    # 人生重心
    life_focus = get_value(data, "life_focus", "")
    if life_focus:
        lines.append("### 人生重心\n")
        lines.append(f"{life_focus}\n")

    return "\n".join(lines)


def _format_pattern_section(data: Any) -> str:
    """格式化格局分析分报告

    支持传入 dict 或 dataclass 对象。
    """
    lines = ["## 格局分析\n"]

    # 统一数据访问方式
    def get_value(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def get_list(obj: Any, key: str, default: list = None) -> list:
        if default is None:
            default = []
        val = get_value(obj, key, default)
        return val if isinstance(val, list) else default

    # 匹配格局 - 优先使用 patterns (dataclass) 或 matched_patterns (dict)
    patterns = get_list(data, "patterns", [])
    matched = get_list(data, "matched_patterns", [])

    if matched or patterns:
        lines.append("### 匹配格局\n")
        items = matched if matched else patterns
        for pattern in items:
            if isinstance(pattern, dict):
                name = pattern.get("name", "未知")
                quality = pattern.get("quality", "未知")
                desc = pattern.get("description", "")
            elif hasattr(pattern, 'name'):
                name = pattern.name
                quality = pattern.quality if hasattr(pattern, 'quality') else "未知"
                desc = pattern.description if hasattr(pattern, 'description') else ""
            else:
                name = str(pattern)
                quality = "未知"
                desc = ""
            lines.append(f"- **{name}** ({quality})")
            if desc:
                lines.append(f"  - {desc}")
        lines.append("")

    # 吉祥格局
    auspicious = get_list(data, "auspicious_patterns", [])
    if auspicious:
        lines.append("### 吉祥格局\n")
        for p in auspicious:
            if isinstance(p, dict):
                lines.append(f"- {p.get('name', str(p))}")
            elif hasattr(p, 'name'):
                lines.append(f"- {p.name}")
            else:
                lines.append(f"- {p}")
        lines.append("")

    # 不利格局
    inauspicious = get_list(data, "inauspicious_patterns", [])
    if inauspicious:
        lines.append("### 需要注意的格局\n")
        for p in inauspicious:
            if isinstance(p, dict):
                lines.append(f"- {p.get('name', str(p))}")
            elif hasattr(p, 'name'):
                lines.append(f"- {p.name}")
            else:
                lines.append(f"- {p}")
        lines.append("")

    # 格局总结 - 尝试多个可能的属性名
    summary = (
        get_value(data, "pattern_summary") or
        get_value(data, "interpretation") or
        get_value(data, "summary", "")
    )
    if summary:
        lines.append(f"**总结**: {summary}\n")

    return "\n".join(lines)


def _format_transform_section(data: Any) -> str:
    """格式化四化分析分报告

    支持传入 dict 或 dataclass 对象。
    """
    lines = ["## 四化分析\n"]

    # 统一数据访问方式
    def get_value(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def get_list(obj: Any, key: str, default: list = None) -> list:
        if default is None:
            default = []
        val = get_value(obj, key, default)
        return val if isinstance(val, list) else default

    # 四化分布 - 尝试多个可能的属性名
    distribution = get_value(data, "transform_distribution", {})
    if not distribution:
        # 从 transforms 构建分布
        transforms = get_list(data, "transforms", [])
        if transforms:
            distribution = {}
            for t in transforms:
                if isinstance(t, dict):
                    transform_type = t.get("transform_type", t.get("transform", ""))
                elif hasattr(t, 'transform_type'):
                    transform_type = t.transform_type
                else:
                    transform_type = str(t)
                if transform_type not in distribution:
                    distribution[transform_type] = []
                if isinstance(t, dict):
                    distribution[transform_type].append(t.get("star", ""))
                elif hasattr(t, 'star'):
                    distribution[transform_type].append(t.star)
    if distribution:
        lines.append("### 四化分布\n")
        for transform, palaces in distribution.items():
            if isinstance(palaces, str):
                lines.append(f"- **{transform}**: {palaces}")
            else:
                lines.append(f"- **{transform}**: {', '.join(str(p) for p in palaces)}")
        lines.append("")

    # 关键四化
    key_transforms = get_list(data, "key_transforms", [])
    if key_transforms:
        lines.append("### 关键四化\n")
        for t in key_transforms:
            if isinstance(t, dict):
                lines.append(f"- **{t.get('star', '')}** {t.get('transform', '')}: {t.get('impact', '')}")
            elif hasattr(t, 'star'):
                transform_type = getattr(t, 'transform_type', getattr(t, 'transform', ''))
                impact = getattr(t, 'impact', '')
                lines.append(f"- **{t.star}** {transform_type}: {impact}")
            else:
                lines.append(f"- {t}")
        lines.append("")

    # 四化相互作用
    interactions = get_value(data, "transform_interactions", "")
    if not interactions:
        interactions = get_value(data, "interactions", "")
    if interactions:
        lines.append("### 四化相互作用\n")
        lines.append(f"{interactions}\n")

    # 宫位影响
    palace_impact = get_value(data, "palace_impact", "")
    if palace_impact:
        lines.append("### 宫位影响\n")
        lines.append(f"{palace_impact}\n")

    # 总评
    assessment = get_value(data, "overall_assessment", "")
    if not assessment:
        assessment = get_value(data, "interpretation", "")
    if assessment:
        lines.append(f"**总评**: {assessment}\n")

    return "\n".join(lines)


def _format_timing_section(data: Any) -> str:
    """格式化运势分析分报告

    支持传入 dict 或 dataclass 对象。
    """
    lines = ["## 运势分析\n"]

    # 统一数据访问方式
    def get_value(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def get_list(obj: Any, key: str, default: list = None) -> list:
        if default is None:
            default = []
        val = get_value(obj, key, default)
        return val if isinstance(val, list) else default

    # 当前大限
    current = get_value(data, "current_major_fate", {})
    if current:
        lines.append("### 当前大限\n")
        if isinstance(current, dict):
            lines.append(f"- **年龄**: {current.get('age_range', '未知')}")
            lines.append(f"- **宫位**: {current.get('palace', '未知')}")
            lines.append(f"- **四化**: {current.get('transformation', '无')}")
            lines.append(f"- **评价**: {current.get('rating', '未知')}")
            desc = current.get('description', '')
        elif hasattr(current, 'age_range'):
            lines.append(f"- **年龄**: {current.age_range}")
            lines.append(f"- **宫位**: {getattr(current, 'palace', '未知')}")
            lines.append(f"- **四化**: {getattr(current, 'transformation', '无')}")
            lines.append(f"- **评价**: {getattr(current, 'rating', '未知')}")
            desc = getattr(current, 'description', '')
        else:
            desc = str(current)
        if desc:
            lines.append(f"\n**描述**: {desc}\n")
        lines.append("")

    # 大限表
    major_table = get_list(data, "major_fate_table", [])
    if major_table:
        lines.append("\n### 大限一览\n")
        lines.append("| 大限 | 年龄 | 宫位 | 四化 | 评价 |")
        lines.append("|------|------|------|------|------|")
        for fate in major_table:
            if isinstance(fate, dict):
                lines.append(f"| {fate.get('name', '')} | {fate.get('age_range', '')} | {fate.get('palace', '')} | {fate.get('transformation', '')} | {fate.get('rating', '')} |")
            elif hasattr(fate, 'name'):
                lines.append(f"| {fate.name} | {getattr(fate, 'age_range', '')} | {getattr(fate, 'palace', '')} | {getattr(fate, 'transformation', '')} | {getattr(fate, 'rating', '')} |")
        lines.append("")

    return "\n".join(lines)


def _build_main_report(
    chart_data: Dict[str, Any],
    analyses: Dict[str, Any],
    question: str
) -> str:
    """构建主报告"""

    # 统一数据访问方式
    def get_value(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def get_list(obj: Any, key: str, default: list = None) -> list:
        if default is None:
            default = []
        val = get_value(obj, key, default)
        return val if isinstance(val, list) else default

    birth = chart_data.get("birth_info", {})
    palaces = chart_data.get("palaces", {})

    # 从命宫提取主星
    ming_gong_stars = []
    if isinstance(palaces, dict) and "命宫" in palaces:
        ming_data = palaces["命宫"]
        if isinstance(ming_data, dict):
            stars = ming_data.get("stars", [])
            if isinstance(stars, list):
                ming_gong_stars = [s.get("name", "") if isinstance(s, dict) else str(s) for s in stars[:5]]

    # 从身宫提取主星
    shen_gong_stars = []
    if isinstance(palaces, dict) and "身宫" in palaces:
        shen_data = palaces["身宫"]
        if isinstance(shen_data, dict):
            stars = shen_data.get("stars", [])
            if isinstance(stars, list):
                shen_gong_stars = [s.get("name", "") if isinstance(s, dict) else str(s) for s in stars[:5]]

    lines = [
        "# 紫微斗数命盘综合分析报告\n",
        f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        f"**分析问题**: {question}\n",
        "---\n",
        "## 命盘概览\n",
        f"- **出生**: {birth.get('year', '')}年{birth.get('month', '')}月{birth.get('day', '')}日{birth.get('hour', '')}时",
        f"- **性别**: {'男' if birth.get('gender') == 'male' else '女'}",
        f"- **五行局**: {birth.get('wuxing_ju_name', '未知')}",
        f"- **命宫**: {', '.join(ming_gong_stars) if ming_gong_stars else '未知'}",
        f"- **身宫**: {', '.join(shen_gong_stars) if shen_gong_stars else '未知'}",
        "---\n",
        "## 核心结论\n",
    ]

    # 从各分析中提取核心结论
    star_data = analyses.get("star_analysis", {})
    palace_data = analyses.get("palace_analysis", {})
    pattern_data = analyses.get("pattern_analysis", {})
    timing_data = analyses.get("timing_analysis", {})
    transform_data = analyses.get("transform_analysis", {})

    # 性格一句话 - 尝试多个可能的属性名
    personality = (
        get_value(star_data, "personality_summary") or
        get_value(star_data, "summary") or
        get_value(star_data, "character_summary", "")
    )
    if personality:
        lines.append(f"**性格特点**: {str(personality)[:200]}...\n")

    # 格局结论 - 尝试多个可能的属性名
    patterns = get_list(pattern_data, "matched_patterns", [])
    if not patterns:
        patterns = get_list(pattern_data, "patterns", [])
    if patterns:
        pattern_names = []
        for p in patterns[:3]:
            if isinstance(p, dict):
                pattern_names.append(p.get("name", ""))
            elif hasattr(p, 'name'):
                pattern_names.append(p.name)
            else:
                pattern_names.append(str(p))
        lines.append(f"**命格格局**: {', '.join(pattern_names)}\n")

    # 当前运势
    current = get_value(timing_data, "current_major_fate", {})
    if current:
        age_range = get_value(current, "age_range", '')
        palace = get_value(current, "palace", '')
        rating = get_value(current, "rating", '')
        lines.append(f"**当前大限**: {age_range} ({palace}宫)")
        lines.append(f"**大限评价**: {rating}\n")

    # 四化总览
    dist = get_value(transform_data, "transform_distribution", {})
    if dist:
        items = []
        for k, v in dist.items():
            if isinstance(v, list):
                items.append(f"{k}({', '.join(str(x) for x in v)})")
            else:
                items.append(f"{k}({v})")
        lines.append("**四化总览**: " + ", ".join(items) + "\n")

    lines.append("---\n")

    # 重点关注
    lines.append("## 重点关注\n")

    # 优势
    strongest = get_list(palace_data, "strongest_palaces", [])
    if not strongest:
        sp = get_value(palace_data, "strongest_palace", "")
        if sp:
            strongest = [sp]
    if strongest:
        lines.append("### 🎯 优势领域")
        for palace in strongest[:3]:
            lines.append(f"- {palace}")
        lines.append("")

    # 注意事项
    weakest = get_list(palace_data, "weakest_palaces", [])
    if not weakest:
        wp = get_value(palace_data, "weakest_palace", "")
        if wp:
            weakest = [wp]
    if weakest:
        lines.append("### ⚠️ 需要注意\n")
        for palace in weakest[:3]:
            lines.append(f"- {palace}需要多加关注")
        lines.append("")

    # 流年建议
    focus_areas = get_list(current, "focus_areas", [])
    if focus_areas:
        lines.append("### 📌 当前大限重点")
        for area in focus_areas:
            lines.append(f"- {area}")
        lines.append("")

    warnings = get_list(current, "warnings", [])
    if warnings:
        lines.append("### ⚡ 风险预警")
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append("---\n")

    # 行动建议
    lines.append("## 行动建议\n")

    # 事业建议
    career = get_value(star_data, "career_recommendations", "")
    if career:
        lines.append("### 💼 事业发展")
        lines.append(f"{str(career)[:300]}...\n")

    # 财运建议
    wealth = get_value(star_data, "wealth_insights", "")
    if wealth:
        lines.append("### 💰 财务管理")
        lines.append(f"{str(wealth)[:300]}...\n")

    # 综合建议
    recommendations = get_list(palace_data, "recommendations", [])
    if recommendations:
        lines.append("### 📋 综合建议")
        for rec in recommendations[:5]:
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("\n---\n")
    lines.append("*详细分析请参阅各分报告*\n")

    return "\n".join(lines)


# ============ 主报告生成器 ============

class ReportGenerator:
    """Markdown报告生成器"""

    def __init__(self, chart_data: Dict[str, Any]):
        self.chart = chart_data

    def generate_bundle(
        self,
        star_analysis: Optional[Dict[str, Any]] = None,
        palace_analysis: Optional[Dict[str, Any]] = None,
        pattern_analysis: Optional[Dict[str, Any]] = None,
        transform_analysis: Optional[Dict[str, Any]] = None,
        timing_analysis: Optional[Dict[str, Any]] = None,
        question: str = ""
    ) -> ReportBundle:
        """生成完整报告集（同步版本）"""
        import asyncio
        return asyncio.run(self.generate_bundle_async(
            star_analysis, palace_analysis, pattern_analysis,
            transform_analysis, timing_analysis, question
        ))

    async def generate_bundle_async(
        self,
        star_analysis: Optional[Dict[str, Any]] = None,
        palace_analysis: Optional[Dict[str, Any]] = None,
        pattern_analysis: Optional[Dict[str, Any]] = None,
        transform_analysis: Optional[Dict[str, Any]] = None,
        timing_analysis: Optional[Dict[str, Any]] = None,
        question: str = ""
    ) -> ReportBundle:
        """生成完整报告集（异步并行版本）"""

        # 并行格式化所有分报告

        async def format_star():
            if star_analysis:
                return ("star", _format_star_section(star_analysis))
            return ("star", "")

        async def format_palace():
            if palace_analysis:
                return ("palace", _format_palace_section(palace_analysis))
            return ("palace", "")

        async def format_pattern():
            if pattern_analysis:
                return ("pattern", _format_pattern_section(pattern_analysis))
            return ("pattern", "")

        async def format_transform():
            if transform_analysis:
                return ("transform", _format_transform_section(transform_analysis))
            return ("transform", "")

        async def format_timing():
            if timing_analysis:
                return ("timing", _format_timing_section(timing_analysis))
            return ("timing", "")

        # 并行执行所有格式化任务
        format_results = await asyncio.gather(
            format_star(),
            format_palace(),
            format_pattern(),
            format_transform(),
            format_timing(),
        )

        # 构建分报告字典
        sub_reports = {}
        for key, content in format_results:
            if content:
                sub_reports[key] = content

        # 汇总分析数据
        analyses = {
            "star_analysis": star_analysis or {},
            "palace_analysis": palace_analysis or {},
            "pattern_analysis": pattern_analysis or {},
            "transform_analysis": transform_analysis or {},
            "timing_analysis": timing_analysis or {},
        }

        # 构建主报告
        main_report = _build_main_report(self.chart, analyses, question)

        return ReportBundle(
            main_report=main_report,
            sub_reports=sub_reports,
            metadata={
                "chart_id": self.chart.get("chart_id", ""),
                "birth_year": self.chart.get("birth_info", {}).get("year"),
                "wuxing_ju": self.chart.get("birth_info", {}).get("wuxing_ju_name"),
                "question": question,
            },
            generated_at=datetime.now().isoformat()
        )


async def generate_markdown_report(
    chart_data: Dict[str, Any],
    star_analysis: Optional[Dict[str, Any]] = None,
    palace_analysis: Optional[Dict[str, Any]] = None,
    pattern_analysis: Optional[Dict[str, Any]] = None,
    transform_analysis: Optional[Dict[str, Any]] = None,
    timing_analysis: Optional[Dict[str, Any]] = None,
    question: str = ""
) -> ReportBundle:
    """生成Markdown报告的便捷函数"""
    generator = ReportGenerator(chart_data)
    return await generator.generate_bundle_async(
        star_analysis, palace_analysis, pattern_analysis,
        transform_analysis, timing_analysis, question
    )


def generate_markdown_report_sync(
    chart_data: Dict[str, Any],
    star_analysis: Optional[Dict[str, Any]] = None,
    palace_analysis: Optional[Dict[str, Any]] = None,
    pattern_analysis: Optional[Dict[str, Any]] = None,
    transform_analysis: Optional[Dict[str, Any]] = None,
    timing_analysis: Optional[Dict[str, Any]] = None,
    question: str = ""
) -> ReportBundle:
    """生成Markdown报告的便捷函数（同步版本）"""
    generator = ReportGenerator(chart_data)
    return generator.generate_bundle(
        star_analysis, palace_analysis, pattern_analysis,
        transform_analysis, timing_analysis, question
    )


# ============ 三层融合预测报告生成函数 ============

async def generate_prediction_report(
    chart: Dict[str, Any],
    target_year: int,
    question: str = ""
) -> "ThreeLayerPredictionReport":
    """
    生成三层融合预测报告

    Args:
        chart: 命盘数据
        target_year: 目标年份
        question: 分析问题

    Returns:
        ThreeLayerPredictionReport: 三层融合预测报告
    """
    chart_id = chart.get("chart_id", f"chart_{id(chart)}")

    # 1. 因果链推理分析
    causal_result = await _analyze_causal_chain(chart, target_year)

    # 2. 案例涌现推理分析
    case_based_result = await _analyze_case_based(chart, target_year)

    # 3. 多Agent共识验证分析
    multi_agent_result = await _analyze_multi_agent(chart, question)

    # 计算综合置信度
    overall_confidence = _calculate_overall_confidence(
        causal_result,
        case_based_result,
        multi_agent_result
    )

    # 生成综合判断
    overall_judgment = _generate_overall_judgment(
        causal_result,
        case_based_result,
        multi_agent_result
    )

    # 生成分维度分析
    dimensions = _generate_dimensions(
        causal_result,
        case_based_result,
        multi_agent_result
    )

    # 生成因果链解释
    causal_explanation = _generate_causal_explanation(causal_result)

    # 提取参考案例
    reference_cases = _extract_reference_cases(case_based_result)

    # 生成趋避建议
    suggestions = _generate_suggestions(
        overall_judgment,
        causal_result,
        case_based_result,
        multi_agent_result,
        dimensions
    )

    return ThreeLayerPredictionReport(
        overall_judgment=overall_judgment,
        overall_confidence=overall_confidence,
        causal_chain_result=causal_result,
        case_based_result=case_based_result,
        multi_agent_result=multi_agent_result,
        dimensions=dimensions,
        causal_explanation=causal_explanation,
        reference_cases=reference_cases,
        suggestions=suggestions,
        target_year=target_year,
        chart_id=chart_id,
        generated_at=datetime.now().isoformat()
    )


def generate_prediction_report_sync(
    chart: Dict[str, Any],
    target_year: int,
    question: str = ""
) -> "ThreeLayerPredictionReport":
    """同步版本的三层融合预测报告生成"""
    return asyncio.run(generate_prediction_report(chart, target_year, question))


async def _analyze_causal_chain(
    chart: Dict[str, Any],
    target_year: int
) -> Optional["CausalChainAnalysis"]:
    """执行因果链推理分析"""
    try:
        from .causal_chain_predictor import CausalChainPredictor

        predictor = CausalChainPredictor()
        analysis = predictor.predict(chart, target_year)

        # 提取关键因果链
        key_chains = []
        if hasattr(analysis, 'causal_chains') and analysis.causal_chains:
            for chain in analysis.causal_chains[:5]:
                chain_type = getattr(chain, 'chain_type', 'UNKNOWN')
                severity = getattr(chain, 'severity', '潜在')
                # 处理枚举类型
                if hasattr(chain_type, 'value'):
                    chain_type = chain_type.value
                if hasattr(severity, 'value'):
                    severity = severity.value
                key_chains.append({
                    "type": chain_type,
                    "severity": severity,
                    "description": getattr(chain, 'description', str(chain))
                })
        elif isinstance(analysis, dict):
            key_chains = analysis.get("causal_chains", [])

        # 确定严重程度
        severity_level = "潜在"
        if hasattr(analysis, 'severity'):
            severity_level = analysis.severity.value  # 使用中文值
        elif isinstance(analysis, dict):
            severity_level = analysis.get("severity", "潜在")

        # 确定因果链类型
        chain_type = "复合因果链"
        if hasattr(analysis, 'chain_type'):
            chain_type = analysis.chain_type
            if hasattr(chain_type, 'value'):
                chain_type = chain_type.value
        elif isinstance(analysis, dict):
            chain_type = analysis.get("chain_type", "复合因果链")

        # 生成解释
        explanation = _build_causal_explanation(analysis)

        # 计算置信度
        confidence = _extract_causal_confidence(analysis)

        return CausalChainAnalysis(
            severity_level=severity_level,
            chain_type=chain_type,
            key_chains=key_chains,
            explanation=explanation,
            confidence=confidence
        )
    except ImportError:
        # 如果因果链分析器不可用，返回默认值
        return CausalChainAnalysis(
            severity_level="潜在",
            chain_type="因果链分析",
            key_chains=[],
            explanation="因果链分析暂时不可用",
            confidence=0.35
        )
    except Exception as e:
        return CausalChainAnalysis(
            severity_level="潜在",
            chain_type="因果链分析",
            key_chains=[],
            explanation=f"分析出错: {str(e)}",
            confidence=0.25
        )


async def _analyze_case_based(
    chart: Dict[str, Any],
    target_year: int
) -> Optional["CaseBasedAnalysis"]:
    """执行案例涌现推理分析"""
    try:
        from .case_based_predictor import predict_from_chart

        # 使用案例推理预测器
        report = await predict_from_chart(
            chart,
            target_year,
            event_types=CORE_DIMENSIONS
        )

        # 提取相似案例
        similar_cases = []
        if hasattr(report, 'results') and report.results:
            for result in report.results[:3]:
                if hasattr(result, 'similar_cases'):
                    for case in result.similar_cases[:2]:
                        similar_cases.append(case)

        # 提取各维度预测
        predictions = {}
        if hasattr(report, 'results') and report.results:
            for result in report.results:
                event_type = getattr(result, 'event_type', '未知')
                predictions[event_type] = {
                    "prediction": getattr(result, 'prediction', ''),
                    "probability": round(getattr(result, 'probability', 0.5), 3),
                    "confidence": round(getattr(result, 'confidence', 0.5), 3)
                }

        # 概率总结
        probability_summary = getattr(report, 'summary', '缺乏足够案例进行预测')

        # 计算置信度
        # 根据业务审查建议：案例库置信度应在50-60%区间，取中值55%
        # 优先使用 report.metadata 中的置信度（当没有相似案例时为0.3）
        base_confidence = 0.55  # 案例库基准置信度
        confidence = report.metadata.get("confidence", base_confidence)
        if predictions:
            # 当有预测结果时，使用各维度置信度的平均值，并施加上限60%
            confidences = [p.get("confidence", base_confidence) for p in predictions.values()]
            avg_confidence = sum(confidences) / len(confidences) if confidences else base_confidence
            confidence = min(avg_confidence, 0.60)  # 案例库置信度不超过60%

        return CaseBasedAnalysis(
            similar_cases=similar_cases[:10],
            predictions=predictions,
            probability_summary=probability_summary,
            confidence=confidence
        )
    except ImportError:
        return CaseBasedAnalysis(
            similar_cases=[],
            predictions={},
            probability_summary="案例推理暂时不可用",
            confidence=0.55
        )
    except Exception as e:
        return CaseBasedAnalysis(
            similar_cases=[],
            predictions={},
            probability_summary=f"分析出错: {str(e)}",
            confidence=0.40
        )


async def _analyze_multi_agent(
    chart: Dict[str, Any],
    question: str
) -> Optional["MultiAgentAnalysis"]:
    """执行多Agent共识验证分析"""
    try:
        from .multi_agent_validator import MultiAgentValidator

        # 对每个维度进行多Agent验证
        all_agent_views = []
        consensus_result = None

        for dimension in CORE_DIMENSIONS:
            validator = MultiAgentValidator()
            result = await validator.validate(chart, question, dimension)

            # 收集Agent观点
            if hasattr(result, 'agent_views') and result.agent_views:
                for view in result.agent_views:
                    all_agent_views.append({
                        "agent_name": view.agent_name,
                        "dimension": dimension,
                        "judgment": view.judgment.value if hasattr(view.judgment, 'value') else str(view.judgment),
                        "confidence": view.confidence,
                        "reasoning": view.reasoning
                    })

            # 收集共识结果（使用第一个维度的共识）
            if not consensus_result and hasattr(result, 'consensus_result') and result.consensus_result:
                consensus_result = {
                    "has_consensus": result.consensus_result.has_consensus,
                    "agreed_judgment": result.consensus_result.agreed_judgment.value
                        if hasattr(result.consensus_result.agreed_judgment, 'value')
                        else str(result.consensus_result.agreed_judgment),
                    "agreeing_agents": result.consensus_result.agreeing_agents,
                    "reasoning": result.consensus_result.reasoning
                }

        # 确定最终判断
        final_judgment = "平"
        if consensus_result and consensus_result.get("has_consensus"):
            final_judgment = consensus_result["agreed_judgment"]
        elif all_agent_views:
            # 统计多数判断
            judgments = [v["judgment"] for v in all_agent_views]
            from collections import Counter
            most_common = Counter(judgments).most_common(1)
            if most_common:
                final_judgment = most_common[0][0]

        # 计算置信度
        # 根据业务审查建议：多Agent置信度应在40-50%区间，取中值45%
        base_confidence = 0.45
        confidence = base_confidence
        if all_agent_views:
            confidences = [v["confidence"] for v in all_agent_views]
            avg_confidence = sum(confidences) / len(confidences) if confidences else base_confidence
            confidence = min(avg_confidence, 0.50)  # 多Agent置信度不超过50%

        return MultiAgentAnalysis(
            agent_views=all_agent_views,
            consensus=consensus_result,
            final_judgment=final_judgment,
            confidence=confidence
        )
    except ImportError:
        return MultiAgentAnalysis(
            agent_views=[],
            consensus=None,
            final_judgment="平",
            confidence=0.45
        )
    except Exception:
        return MultiAgentAnalysis(
            agent_views=[],
            consensus=None,
            final_judgment="平",
            confidence=0.35
        )


def _calculate_overall_confidence(
    causal: Optional["CausalChainAnalysis"],
    case_based: Optional["CaseBasedAnalysis"],
    multi_agent: Optional["MultiAgentAnalysis"]
) -> float:
    """计算综合置信度 - 引入信息完整度权重因子动态调整

    根据业务审查建议：
    - 因果链置信度：30-40% (取35%)
    - 案例库置信度：50-60% (取55%)
    - 多Agent置信度：40-50% (取45%)
    - 综合置信度应在35-45%范围内
    """
    # 1. 提取各层置信度，若无数据则标记为None
    causal_conf = getattr(causal, 'confidence', None) if causal else None
    case_conf = getattr(case_based, 'confidence', None) if case_based else None
    agent_conf = getattr(multi_agent, 'confidence', None) if multi_agent else None

    # 2. 定义基础权重
    weights = {
        "causal": CAUSAL_WEIGHT,
        "case": CASE_BASED_WEIGHT,
        "agent": MULTI_AGENT_WEIGHT
    }

    # 3. 收集有效数据层
    valid_layers = []
    if causal_conf is not None:
        valid_layers.append(("causal", causal_conf, weights["causal"]))
    if case_conf is not None:
        valid_layers.append(("case", case_conf, weights["case"]))
    if agent_conf is not None:
        valid_layers.append(("agent", agent_conf, weights["agent"]))

    # 4. 若无有效数据，返回低置信度表示缺乏信息
    if not valid_layers:
        return 0.30

    # 5. 动态权重归一化
    total_weight = sum(w for _, _, w in valid_layers)
    normalized_weights = [w / total_weight for _, _, w in valid_layers]

    # 6. 加权计算
    overall = sum(conf * nw for (_, conf, _), nw in zip(valid_layers, normalized_weights))

    # 7. 根据有效层数应用折扣
    layer_count = len(valid_layers)
    if layer_count == 1:
        overall *= 0.7  # 单层数据打7折
    elif layer_count == 2:
        overall *= 0.9  # 两层数据打9折
    # 3层数据不打折扣

    # 8. 根据业务审查建议，增加综合置信度上限约束（不超过45%）
    MAX_OVERALL_CONFIDENCE = 0.45
    overall = min(overall, MAX_OVERALL_CONFIDENCE)

    return min(max(overall, 0.0), 1.0)


def _generate_overall_judgment(
    causal: Optional["CausalChainAnalysis"],
    case_based: Optional["CaseBasedAnalysis"],
    multi_agent: Optional["MultiAgentAnalysis"]
) -> str:
    """生成综合判断"""
    # 从各层提取判断分数
    scores = []

    # 因果链判断
    if causal:
        severity = causal.severity_level
        if severity in ["吉祥", "潜在"]:
            scores.append(0.6)  # 潜在问题，偏吉
        elif severity in ["条件"]:
            scores.append(0.5)  # 有条件，中性
        elif severity in ["确定"]:
            scores.append(0.4)  # 确定问题，偏凶
        elif severity in ["重大"]:
            scores.append(0.38)  # 重大问题，调整分数以平衡多Agent权重
        else:
            scores.append(0.5)
    else:
        scores.append(0.5)

    # 案例推理判断
    if case_based and case_based.predictions:
        pred_scores = []
        for pred in case_based.predictions.values():
            prob = pred.get("probability", 0.5)
            if prob >= 0.7:
                pred_scores.append(0.7)
            elif prob >= 0.5:
                pred_scores.append(0.5)
            elif prob >= 0.3:
                pred_scores.append(0.4)
            else:
                pred_scores.append(0.3)
        if pred_scores:
            scores.append(sum(pred_scores) / len(pred_scores))
        else:
            scores.append(0.5)
    else:
        scores.append(0.5)

    # 多Agent判断
    if multi_agent:
        judgment = multi_agent.final_judgment
        if judgment == "吉":
            scores.append(0.7)
        elif judgment == "凶":
            scores.append(0.3)
        else:
            scores.append(0.5)
    else:
        scores.append(0.5)

    # 加权平均
    weighted_score = (
        scores[0] * CAUSAL_WEIGHT +
        scores[1] * CASE_BASED_WEIGHT +
        scores[2] * MULTI_AGENT_WEIGHT
    )

    # ========== 重大 因果链否决规则 ==========
    # 根据 metaphysics expert (梁若瑜派系) 建议：
    # 因果链是"因"，案例和共识是"缘"
    # 重大代表"因已种下"，但权重应该与多Agent共识平衡
    if causal and causal.severity_level == "重大":
        if weighted_score >= 0.50:  # 调整阈值
            return "平"  # 原为"吉"，降为"平"
        elif weighted_score > 0.30:  # 调整阈值，避免过度惩罚
            return "凶"  # 原为"平"，降为"凶"

    # 转换为判断
    if weighted_score >= 0.55:  # 调整阈值以匹配
        return "吉"
    elif weighted_score <= 0.30:  # 调整阈值
        return "凶"
    else:
        return "平"


def _generate_dimensions(
    causal: Optional["CausalChainAnalysis"],
    case_based: Optional["CaseBasedAnalysis"],
    multi_agent: Optional["MultiAgentAnalysis"]
) -> Dict[str, "DimensionAnalysis"]:
    """生成分维度分析"""
    dimensions = {}

    # 因果链风险因子：只有当因果链严重程度为重大时才应用小幅惩罚
    # 惩罚力度降低，避免覆盖多Agent共识的独立判断
    causal_risk_penalty = 0.0
    causal_risk_reason = ""
    if causal and causal.severity_level in ["确定", "重大"]:
        if causal.severity_level == "重大":
            causal_risk_penalty = 0.05  # 降低惩罚力度，从0.15改为0.05
            causal_risk_reason = f"因果链{causal.severity_level}级风险"
        elif causal.severity_level == "确定":
            causal_risk_penalty = 0.03  # 降低惩罚力度，从0.10改为0.03
            causal_risk_reason = f"因果链{causal.severity_level}级风险"

    for dim in CORE_DIMENSIONS:
        # 尝试从各层获取该维度的分析
        reasoning_parts = []
        # 分维度置信度基准值
        base_dim_confidence = 0.45
        confidence = base_dim_confidence

        # 从多Agent结果获取
        if multi_agent and multi_agent.agent_views:
            dim_views = [v for v in multi_agent.agent_views if v.get("dimension") == dim]
            if dim_views:
                judgments = [v["judgment"] for v in dim_views]
                confidences = [v["confidence"] for v in dim_views]
                reasoning_parts.append(f"多Agent共识: {', '.join(set(judgments))}")
                avg_conf = sum(confidences) / len(confidences) if confidences else base_dim_confidence
                confidence = min(avg_conf, 0.65)  # 多Agent维度置信度上限调整为65%

        # 从案例推理获取
        if case_based and case_based.predictions.get(dim):
            pred = case_based.predictions[dim]
            reasoning_parts.append(f"概率预测: {pred.get('prediction', '')}")
            case_conf = pred.get("confidence", 0.55)
            confidence = (confidence + case_conf) / 2 if confidence != base_dim_confidence else case_conf
            confidence = min(confidence, 0.60)  # 案例库维度置信度不超过60%

        # 应用因果链风险惩罚
        if causal_risk_penalty > 0:
            confidence = max(0.1, confidence - causal_risk_penalty)
            if causal_risk_reason and "因果链" not in "".join(reasoning_parts):
                reasoning_parts.append(causal_risk_reason)

        # 确定判断
        judgment = "平"
        if confidence >= 0.55:  # 调整阈值，给"平"更多空间
            judgment = "吉"
        elif confidence <= 0.35:  # 调整阈值，避免过于宽松的"凶"
            judgment = "凶"

        dimensions[dim] = DimensionAnalysis(
            judgment=judgment,
            confidence=confidence,
            reasoning="; ".join(reasoning_parts) if reasoning_parts else "缺乏足够分析数据"
        )

    return dimensions


def _build_causal_explanation(analysis: Any) -> str:
    """构建因果链解释"""
    if not analysis:
        return "因果链分析暂时不可用"

    if hasattr(analysis, 'summary'):
        return analysis.summary

    if hasattr(analysis, 'analysis'):
        return analysis.analysis

    if isinstance(analysis, dict):
        return analysis.get("explanation", analysis.get("summary", ""))

    return str(analysis)


def _extract_causal_confidence(analysis: Any) -> float:
    """提取因果链置信度

    根据业务审查建议：
    - 因果链底层因果链65%错误率，置信度应在30-40%区间
    - 取中值35%作为基准
    """
    if not analysis:
        return 0.35  # 降低默认置信度

    if hasattr(analysis, 'confidence'):
        conf = analysis.confidence
        # 对因果链置信度施加上限约束，不应超过40%
        return min(conf, 0.40)

    if isinstance(analysis, dict):
        conf = analysis.get("confidence", 0.35)
        return min(conf, 0.40)

    return 0.35


def _generate_causal_explanation(causal: Optional["CausalChainAnalysis"]) -> str:
    """生成因果链解释"""
    if not causal:
        return "因果链分析暂时不可用"

    parts = []

    # 添加严重程度说明
    severity_map = {
        "吉祥": "运势吉祥如意",
        "潜在": "当前处于潜在阶段，需要关注",
        "条件": "存在条件性阻碍，需注意",
        "确定": "问题已较确定，需要化解",
        "重大": "存在重大风险，需要特别注意"
    }
    severity_text = severity_map.get(causal.severity_level, causal.severity_level)
    parts.append(f"【因果链分析】{severity_text}")

    # 添加解释（移除字符截断限制，确保完整输出）
    if causal.explanation:
        parts.append(causal.explanation)

    # 添加关键因果链
    if causal.key_chains:
        chain_descriptions = []
        for chain in causal.key_chains[:3]:
            desc = chain.get("description", "") or str(chain)
            if desc and len(desc) < 50:
                chain_descriptions.append(desc)
        if chain_descriptions:
            parts.append("关键因素: " + ", ".join(chain_descriptions))

    return "\n".join(parts) if parts else "分析完成"


def _extract_reference_cases(
    case_based: Optional["CaseBasedAnalysis"]
) -> List[Dict[str, Any]]:
    """提取参考案例"""
    if not case_based:
        return []

    cases = case_based.similar_cases if case_based else []

    # 简化案例信息
    simplified = []
    for case in cases[:5]:
        if isinstance(case, dict):
            simplified.append({
                "case_id": case.get("case_id", ""),
                "chart_id": case.get("chart_id", ""),
                "similarity": round(case.get("similarity", 0), 3)
            })
        elif hasattr(case, 'case_id'):
            simplified.append({
                "case_id": case.case_id,
                "chart_id": getattr(case, 'chart_id', ''),
                "similarity": 0.8
            })

    return simplified


# 宫位与维度的映射关系
DIMENSION_PALACE_MAP = {
    "财富": ["财帛宫", "福德宫"],
    "事业": ["官禄宫", "迁移宫"],
    "感情": ["夫妻宫", "子女宫"],
    "健康": ["疾厄宫"]
}

# 维度专属建议关键词映射
DIMENSION_KEYWORDS = {
    "财富": ["财帛", "福德", "理财", "投资", "收入", "金钱", "财运"],
    "事业": ["官禄", "迁移", "事业", "工作", "职位", "升迁", "创业"],
    "感情": ["夫妻", "子女", "婚姻", "感情", "桃花", "恋爱"],
    "健康": ["疾厄", "健康", "身体", "疾病", "医疗"]
}


def _generate_suggestions(
    overall_judgment: str,
    causal: Optional["CausalChainAnalysis"],
    case_based: Optional["CaseBasedAnalysis"],
    multi_agent: Optional["MultiAgentAnalysis"],
    dimensions: Dict[str, "DimensionAnalysis"]
) -> List[str]:
    """生成趋避建议

    根据三层分析结果生成针对性建议：
    - 因果链分析：识别潜在风险和触发条件
    - 案例推理：基于相似命盘的经验
    - 多Agent共识：群体智慧验证
    """
    suggestions = []
    conflict_explanations = []  # 存储维度冲突说明

    # ========== 1. 分析维度冲突 ==========
    ji_dims = [dim for dim, a in dimensions.items() if a.judgment == "吉"]
    xiong_dims = [dim for dim, a in dimensions.items() if a.judgment == "凶"]
    [dim for dim, a in dimensions.items() if a.judgment == "平"]

    # 处理冲突情况：吉多平少但综合判断不是"吉"
    if len(ji_dims) >= 2 and len(xiong_dims) == 0 and overall_judgment != "吉":
        # 检查是否存在隐性风险
        causal_risk = False
        if causal and causal.severity_level in ["条件", "确定", "重大"]:
            causal_risk = True

        if causal_risk:
            conflict_explanations.append(
                f"虽然【{'/'.join(ji_dims)}】运势较好，但因果链分析显示存在潜在风险因素，"
                f"综合判断为{overall_judgment}，建议保持谨慎"
            )

    # 处理凶兆但有化解因素
    if len(xiong_dims) >= 1 and len(ji_dims) >= 1 and overall_judgment == "平":
        conflict_explanations.append(
            f"【{'/'.join(xiong_dims)}】存在压力，但【{'/'.join(ji_dims)}】有化解之力，"
            f"综合判断为{overall_judgment}，需趋吉避凶"
        )

    # ========== 2. 根据整体判断生成基础建议 ==========
    if overall_judgment == "吉":
        suggestions.append("运势较佳，宜把握机遇，积极进取")
    elif overall_judgment == "凶":
        suggestions.append("运势较弱，宜静心养性，谨慎行事")
    else:
        suggestions.append("运势平稳，宜守成待机，稳健发展")

    # ========== 3. 根据因果链分析生成针对性建议 ==========
    if causal:
        # 分析关键因果链，生成针对性建议
        if causal.key_chains:
            for chain in causal.key_chains[:2]:  # 取最重要的两条因果链
                chain_desc = chain.get("description", "")
                chain.get("type", "")

                # 根据因果链类型生成对应建议
                if "财富" in chain_desc or "财帛" in chain_desc:
                    if causal.severity_level in ["确定", "重大"]:
                        suggestions.append(
                            "【财富风险】因果链显示财务领域存在重大隐患，"
                            "建议提前做好资产保全，谨慎大额投资"
                        )
                    elif causal.severity_level == "条件":
                        suggestions.append(
                            "【财富注意】财务运势有条件触发风险，"
                            "留意下半年时间节点，避免冲动决策"
                        )

                elif "事业" in chain_desc or "官禄" in chain_desc:
                    if causal.severity_level in ["确定", "重大"]:
                        suggestions.append(
                            "【事业风险】工作事业面临重大挑战，"
                            "建议寻求贵人相助，备好Plan B"
                        )
                    elif causal.severity_level == "条件":
                        suggestions.append(
                            "【事业注意】事业运势存在变动可能，"
                            "保持职业竞争力，关注内部机会"
                        )

                elif "感情" in chain_desc or "夫妻" in chain_desc:
                    if causal.severity_level in ["确定", "重大"]:
                        suggestions.append(
                            "【感情警示】感情关系可能出现重大转折，"
                            "建议加强沟通，避免冷处理"
                        )
                    elif causal.severity_level == "条件":
                        suggestions.append(
                            "【感情注意】感情运势有潜在波动，"
                            "多关注伴侣情绪变化"
                        )

                elif "健康" in chain_desc or "疾厄" in chain_desc:
                    if causal.severity_level in ["确定", "重大"]:
                        suggestions.append(
                            "【健康警示】健康运势较弱，建议提前进行全面体检，"
                            "调整作息和饮食习惯"
                        )
                    elif causal.severity_level == "条件":
                        suggestions.append(
                            "【健康注意】健康有条件触发风险，"
                            "换季时注意保养，预防为主"
                        )
        else:
            # key_chains为空但严重程度不是潜在时，基于各维度判断生成建议
            if causal.severity_level in ["确定", "重大"]:
                # 根据各维度判断生成针对性建议
                for dim, analysis in dimensions.items():
                    if analysis.judgment == "凶":
                        if dim == "财富":
                            suggestions.append(
                                "【财富风险】因果链分析显示财务领域存在风险，"
                                "建议做好资产保全，谨慎大额支出"
                            )
                        elif dim == "事业":
                            suggestions.append(
                                "【事业风险】事业运面临挑战，建议寻求贵人相助，"
                                "保持职业竞争力"
                            )
                        elif dim == "感情":
                            suggestions.append(
                                "【感情警示】感情关系需注意沟通，"
                                "避免误解和冷暴力"
                            )
                        elif dim == "健康":
                            suggestions.append(
                                "【健康警示】健康需要注意，建议体检，"
                                "调整作息和饮食习惯"
                            )
            elif causal.severity_level == "条件":
                suggestions.append("存在条件触发因素，注意规避风险")

        # 根据严重程度生成通用建议
        severity = causal.severity_level
        if severity in ["确定", "重大"]:
            suggestions.append("因实证较强，建议寻求专业化解指导")
        elif severity == "条件":
            suggestions.append("存在条件触发因素，注意规避风险")

    # ========== 4. 根据案例推理生成针对性建议 ==========
    if case_based and case_based.similar_cases:
        # 分析相似案例的成功/失败经验
        successful_outcomes = 0
        caution_cases = 0

        for case in case_based.similar_cases[:3]:
            # 尝试从多个字段获取outcome信息
            outcome = case.get("outcome", "")
            if not outcome:
                # 从event字段中提取description
                event = case.get("event", {})
                if isinstance(event, dict):
                    outcome = event.get("description", "")

            if "吉" in outcome or "顺利" in outcome or "成功" in outcome or "亨通" in outcome:
                successful_outcomes += 1
            elif "凶" in outcome or "失败" in outcome or "注意" in outcome or "波折" in outcome:
                caution_cases += 1

        if successful_outcomes >= 1:
            # 找到成功案例的关键因素
            suggestions.append(
                f"参考案例：{successful_outcomes}个相似命盘呈现吉兆，"
                "可借鉴其成功经验顺势而为"
            )

        if caution_cases >= 1:
            suggestions.append(
                f"参考案例：{caution_cases}个相似命盘有警示记录，"
                "建议避开类似风险因素"
            )

        # 根据案例推理的各维度预测生成建议
        if case_based.predictions:
            for dim, pred in case_based.predictions.items():
                prediction = pred.get("prediction", "")
                pred.get("probability", 0.5)

                if dim in dimensions:
                    dim_judgment = dimensions[dim].judgment

                    # 案例与维度判断一致时的建议
                    if "吉" in prediction or "发展" in prediction or "好转" in prediction:
                        if dim_judgment == "吉":
                            suggestions.append(
                                f"【{dim}】案例验证支持吉兆，宜顺势进取，把握时机"
                            )
                    elif "凶" in prediction or "风险" in prediction or "注意" in prediction:
                        if dim_judgment == "凶":
                            suggestions.append(
                                f"【{dim}】案例显示风险较高，宜提前防范，保守应对"
                            )

    # ========== 5. 根据多Agent共识生成针对性建议 ==========
    if multi_agent and multi_agent.agent_views:
        # 分析各Agent的观点分布
        agent_judgments = {}
        for view in multi_agent.agent_views:
            dim = view.get("dimension", "整体")
            judgment = view.get("judgment", "平")
            if dim not in agent_judgments:
                agent_judgments[dim] = []
            agent_judgments[dim].append(judgment)

        # 分析共识情况
        has_disagreement = False
        for dim, judgments in agent_judgments.items():
            ji_count = judgments.count("吉")
            xiong_count = judgments.count("凶")
            total = len(judgments)

            if total >= 2:
                # 多数共识
                if ji_count >= total * 0.6:
                    agent_name = next((v.get("agent_name", "Agent") for v in multi_agent.agent_views
                                     if v.get("dimension") == dim and v.get("judgment") == "吉"), "Agent")
                    suggestions.append(
                        f"【{dim}】多Agent共识偏向吉兆({ji_count}/{total})，"
                        f"{agent_name}等认为可适度进取"
                    )
                elif xiong_count >= total * 0.6:
                    agent_name = next((v.get("agent_name", "Agent") for v in multi_agent.agent_views
                                     if v.get("dimension") == dim and v.get("judgment") == "凶"), "Agent")
                    suggestions.append(
                        f"【{dim}】多Agent共识偏向谨慎({xiong_count}/{total})，"
                        f"{agent_name}等建议防守为主"
                    )
                else:
                    # 分歧情况（1:1）
                    has_disagreement = True

        # 如果存在分歧，添加综合建议
        if has_disagreement:
            suggestions.append(
                "多Agent观点存在分歧，建议综合多方意见，灵活应对为佳"
            )

        # 共识验证结果
        if multi_agent.consensus and multi_agent.consensus.get("has_consensus"):
            consensus_reasoning = multi_agent.consensus.get("reasoning", "")
            if "分歧" in consensus_reasoning or "不一致" in consensus_reasoning:
                suggestions.append(
                    "多Agent存在分歧，建议综合多方观点，灵活应对"
                )

    # ========== 6. 根据分维度分析生成补充建议 ==========
    for dim, analysis in dimensions.items():
        # 只对还未生成建议的维度进行补充
        dim_covered = any(dim in s for s in suggestions)
        if not dim_covered:
            if analysis.judgment == "凶":
                # 针对具体维度生成更详细的建议
                if dim == "财富":
                    suggestions.append(
                        f"【{dim}】运势较弱，建议稳健理财，控制支出，"
                        f"避免高风险投资，关注{DIMENSION_PALACE_MAP.get(dim, ['财帛宫'])[0]}"
                    )
                elif dim == "事业":
                    suggestions.append(
                        f"【{dim}】事业有阻，宜静心提升专业能力，"
                        f"谨慎跳槽或创业，关注{DIMENSION_PALACE_MAP.get(dim, ['官禄宫'])[0]}"
                    )
                elif dim == "感情":
                    suggestions.append(
                        f"【{dim}】感情需用心经营，多沟通理解，"
                        f"避免冲动决定，关注{DIMENSION_PALACE_MAP.get(dim, ['夫妻宫'])[0]}"
                    )
                elif dim == "健康":
                    suggestions.append(
                        f"【{dim}】健康需注意，合理作息，适量运动，"
                        f"定期体检，关注{DIMENSION_PALACE_MAP.get(dim, ['疾厄宫'])[0]}"
                    )
            elif analysis.judgment == "吉":
                if dim == "财富":
                    suggestions.append(
                        f"【{dim}】财运较好，可把握投资机会，"
                        f"但需分散风险，关注{DIMENSION_PALACE_MAP.get(dim, ['财帛宫'])[0]}"
                    )
                elif dim == "事业":
                    suggestions.append(
                        f"【{dim}】事业上升期，宜主动争取机会，"
                        f"展现能力，关注{DIMENSION_PALACE_MAP.get(dim, ['官禄宫'])[0]}"
                    )
                elif dim == "感情":
                    suggestions.append(
                        f"【{dim}】感情运势佳，宜增进关系，"
                        f"适合表达心意，关注{DIMENSION_PALACE_MAP.get(dim, ['夫妻宫'])[0]}"
                    )
                elif dim == "健康":
                    suggestions.append(
                        f"【{dim}】健康状况良好，宜保持良好生活习惯，"
                        f"适度运动养生，关注{DIMENSION_PALACE_MAP.get(dim, ['疾厄宫'])[0]}"
                    )

    # ========== 7. 添加维度冲突说明 ==========
    if conflict_explanations:
        # 将冲突说明作为特殊建议插入
        for exp in conflict_explanations:
            suggestions.insert(0, f"[解读] {exp}")

    # 限制建议数量，优先保留针对性建议
    return suggestions[:8]


# ============ Markdown格式化扩展 ============

def format_prediction_report_markdown(
    report: "ThreeLayerPredictionReport"
) -> str:
    """将三层融合预测报告格式化为Markdown"""

    lines = [
        "# 三层融合预测报告\n",
        f"**生成时间**: {report.generated_at[:19] if report.generated_at else '未知'}\n",
        f"**目标年份**: {report.target_year}\n",
        f"**命盘ID**: {report.chart_id}\n",
        "---\n",
        "## 综合判断\n",
        f"- **整体运势**: {report.overall_judgment}\n",
        f"- **置信度**: {report.overall_confidence:.1%}\n",
        "---\n"
    ]

    # 三层分析结果
    lines.append("## 三层分析\n")

    # 因果链分析
    lines.append("### 因果链推理 (权重40%)\n")
    if report.causal_chain_result:
        cr = report.causal_chain_result
        lines.append(f"- **严重程度**: {cr.severity_level}\n")
        lines.append(f"- **因果链类型**: {cr.chain_type}\n")
        lines.append(f"- **置信度**: {cr.confidence:.1%}\n")
        if cr.key_chains:
            lines.append("- **关键因果链**:\n")
            for chain in cr.key_chains[:3]:
                desc = chain.get("description", "") or str(chain)
                lines.append(f"  - {desc}\n")
    lines.append("\n")

    # 案例推理
    lines.append("### 案例涌现推理 (权重35%)\n")
    if report.case_based_result:
        cb = report.case_based_result
        lines.append(f"- **置信度**: {cb.confidence:.1%}\n")
        lines.append(f"- **概率总结**: {cb.probability_summary}\n")
        if cb.predictions:
            lines.append("- **各维度预测**:\n")
            for dim, pred in cb.predictions.items():
                lines.append(f"  - {dim}: {pred.get('prediction', '')} (概率{prob_to_percent(pred.get('probability', 0.5))})\n")
    lines.append("\n")

    # 多Agent共识
    lines.append("### 多Agent共识验证 (权重25%)\n")
    if report.multi_agent_result:
        ma = report.multi_agent_result
        lines.append(f"- **最终判断**: {ma.final_judgment}\n")
        lines.append(f"- **置信度**: {ma.confidence:.1%}\n")
        if ma.agent_views:
            agent_names = list(set(v["agent_name"] for v in ma.agent_views))
            lines.append(f"- **参与Agent**: {', '.join(agent_names)}\n")
        if ma.consensus and ma.consensus.get("has_consensus"):
            lines.append(f"- **共识达成**: {ma.consensus.get('reasoning', '')}\n")
    lines.append("\n")

    # 分维度分析
    lines.append("## 分维度分析\n")
    if report.dimensions:
        lines.append("| 维度 | 判断 | 置信度 | 简析 |\n")
        lines.append("|------|------|--------|------|\n")
        for dim, analysis in report.dimensions.items():
            brief_reason = analysis.reasoning[:30] + "..." if len(analysis.reasoning) > 30 else analysis.reasoning
            lines.append(f"| {dim} | {analysis.judgment} | {analysis.confidence:.1%} | {brief_reason} |\n")
    lines.append("\n")

    # 因果链解释 - 智能摘要
    if report.causal_explanation:
        lines.append("## 因果链解释\n")
        summary = _summarize_causal_chains(report.causal_explanation)
        lines.append(f"{summary}\n\n")

    # 参考案例
    if report.reference_cases:
        lines.append("## 参考案例\n")
        lines.append("以下为相似命盘案例供参考：\n")
        for case in report.reference_cases[:5]:
            lines.append(f"- **{case.get('chart_id', case.get('case_id', '未知'))}**: 相似度 {case.get('similarity', 0):.1%}\n")
        lines.append("\n")

    # 趋避建议
    if report.suggestions:
        lines.append("## 趋避建议\n")
        for i, suggestion in enumerate(report.suggestions, 1):
            lines.append(f"{i}. {suggestion}\n")

    return "".join(lines)


def _summarize_causal_chains(explanation: str) -> str:
    """
    智能摘要因果链解释
    - 按类型分组（忌转忌重大、禄忌同宫等）
    - 每类最多保留3条
    - 添加类型解读
    """
    if not explanation:
        return "因果链分析暂时不可用"
    lines = explanation.strip().split("\n")
    if not lines:
        return explanation

    # 首行是标题/说明，保留
    result = [lines[0] + "\n"]

    # 解析因果链条目
    chain_lines = []
    summary_lines = []
    total_chains = 0

    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        # 解析因果链条目格式：- 类型（级别）：内容
        m = re.match(r"^- (.+?)（(.+?)）：(.+)$", stripped)
        if m:
            chain_type = m.group(1).strip()
            severity = m.group(2).strip()
            content = m.group(3).strip()
            chain_lines.append((chain_type, severity, content))
            total_chains += 1
        else:
            summary_lines.append(stripped)

    if not chain_lines:
        return explanation  # 无法解析，直接返回原文

    # 按类型分组，每类最多3条
    from collections import OrderedDict
    grouped = OrderedDict()
    for chain_type, severity, content in chain_lines:
        key = f"{chain_type}（{severity}）"
        if key not in grouped:
            grouped[key] = []
        if len(grouped[key]) < 3:
            grouped[key].append(content)

    # 构建摘要
    result.append(f"共检测到 {total_chains} 条因果链，归纳为 {len(grouped)} 种类型：\n\n")

    severity_labels = {
        "重大": "⚠️ 高风险",
        "条件": "🔔 条件触发",
        "潜在": "💡 潜在影响",
        "确定": "🔴 已确定",
    }

    type_descriptions = {
        "忌转忌": "双重忌力叠加，主大凶或大吉之变",
        "禄忌同宫": "得失参半，同宫内机遇与挑战并存",
        "禄忌对称": "阴阳对峙，牵一发而动全身",
        "本宫自化": "本宫气机流动，内部自动调节",
        "忌入逢星": "忌入有星之宫，化中带变需谨慎",
        "果报宫": "因果报应宫位，该宫承受业力",
        "追权": "权力追逐与巩固",
        "追禄": "财运追逐与积累",
        "格局识别": "命格格局识别",
    }

    for key, contents in grouped.items():
        chain_type = key.split("（")[0].strip()
        severity = key.split("（")[1].rstrip("）").strip()
        label = severity_labels.get(severity, severity)
        desc = type_descriptions.get(chain_type, "")
        result.append(f"**{key}** {label}\n")
        if desc:
            result.append(f"*{desc}*\n")
        for content in contents:
            result.append(f"- {content}\n")
        result.append("\n")

    # 添加原始总结（如有）
    if summary_lines:
        result.append("---\n")
        for sl in summary_lines:
            if sl and not re.match(r"^-", sl):
                result.append(f"{sl}\n")

    return "".join(result)


def prob_to_percent(prob: float) -> str:
    """概率转百分比字符串"""
    return f"{prob * 100:.0f}%"


# ============ 完整三层融合预测报告生成 ============

def generate_full_prediction_markdown_report(
    chart: Dict[str, Any],
    target_year: int,
    question: str = ""
) -> "ReportBundle":
    """
    生成完整的三层融合预测 Markdown 报告

    这是主要的入口函数，整合了：
    1. 三层融合预测报告生成 (generate_prediction_report)
    2. Markdown 格式化 (format_prediction_report_markdown)

    Args:
        chart: 命盘数据
        target_year: 目标年份
        question: 分析问题

    Returns:
        ReportBundle: 包含完整 Markdown 报告的报告集
    """
    # 1. 生成三层融合预测报告
    prediction_report = generate_prediction_report_sync(chart, target_year, question)

    # 2. 格式化为 Markdown
    format_prediction_report_markdown(prediction_report)

    # 3. 构建命盘概览
    birth = chart.get("birth_info", {})
    chart.get("year_stem", birth.get("year_stem", ""))


def _validate_and_fix_transforms(year_stem: str, wuxing_transforms: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """
    校验并修复四化映射中的科忌同星问题

    校验规则：
    - 一星不可化两曜：同一星不能同时化科和化忌
    - 化禄和化忌可以同星（如太阳禄忌同宫）

    Args:
        year_stem: 年干（甲乙丙丁戊己庚辛壬癸）
        wuxing_transforms: 四化映射表

    Returns:
        校验并修复后的四化信息
    """
    transforms = wuxing_transforms.get(year_stem, {})

    if not transforms:
        logger.warning(f"未找到年干 {year_stem} 的四化映射")
        return transforms

    # 提取化科和化忌的星曜
    ke_star = transforms.get("科", "")
    ji_star = transforms.get("忌", "")

    # 检查科忌是否同星（一星不可化两曜）
    if ke_star and ji_star and ke_star == ji_star:
        error_msg = (
            f"【科忌同星错误】{year_stem}年：化科星曜 '{ke_star}' 与化忌星曜 '{ji_star}' 相同！"
            f"一星不可化两曜，化科和化忌不能是同一颗星。"
        )
        logger.error(error_msg)

        # 尝试修复：根据年干查找正确的四化
        # 已知正确映射：
        # - 戊: 天机化忌，右弼化科（天机只化忌不化科）
        fixed_transforms = _get_correct_transforms(year_stem)
        if fixed_transforms:
            logger.info(f"已自动修复 {year_stem}年 四化映射: {transforms} -> {fixed_transforms}")
            return fixed_transforms

        # 无法自动修复，返回原值但标记错误
        logger.warning(f"无法自动修复 {year_stem}年 四化映射，请手动检查")
        return transforms

    # 检查化禄和化忌是否同星（这是允许的）
    lu_star = transforms.get("禄", "")
    if lu_star and ji_star and lu_star == ji_star:
        logger.info(f"【化禄忌同星】{year_stem}年：{lu_star} 化禄忌同宫（这是允许的）")

    # 检查是否有其他异常（排除禄忌同星的情况）
    # 科和权不能与禄或忌同星（除了禄忌同星是允许的）
    ke_star = transforms.get("科", "")
    quan_star = transforms.get("权", "")

    # 检查科是否与其他三化同星（不允许）
    if ke_star:
        if ke_star == lu_star:
            logger.warning(f"【四化错误】{year_stem}年：化科'{ke_star}'与化禄同星（不允许）")
        if ke_star == ji_star:
            logger.warning(f"【四化错误】{year_stem}年：化科'{ke_star}'与化忌同星（不允许，一星不可化两曜）")
        if ke_star == quan_star:
            logger.warning(f"【四化错误】{year_stem}年：化科'{ke_star}'与化权同星（不允许）")

    # 检查权是否与忌同星（不允许）
    if quan_star and ji_star and quan_star == ji_star:
        logger.warning(f"【四化错误】{year_stem}年：化权'{quan_star}'与化忌同星（不允许）")

    return transforms


def _get_correct_transforms(year_stem: str) -> Optional[Dict[str, str]]:
    """
    获取正确的四化映射（用于修复错误的映射）

    正确四化表（根据紫微斗数典籍《紫微斗数全书》《飞星紫微斗数》）：
    一星不可化两曜，化禄和化忌可以同星
    - 甲: 廉贞禄、破军权、太阳科、太阴忌
    - 乙: 廉贞禄、破军权、武曲科、太阳忌
    - 丙: 天同禄、天梁权、太阳科、天同忌
    - 丁: 天同禄、天梁权、天机科、太阴忌
    - 戊: 贪狼禄、太阴权、右弼科、天机忌
    - 己: 武曲禄、贪狼权、太阴科、武曲忌
    - 庚: 太阳禄、武曲权、天府科、太阳忌（禄忌同宫）
    - 辛: 巨门禄、太阳权、天府科、巨门忌（禄忌同宫）
    - 壬: 天梁禄、天机权、紫微科、天梁忌（禄忌同宫）
    - 癸: 天机禄、巨门权、紫微科、天机忌（禄忌同宫）
    """
    correct_transforms = {
        "甲": {"禄": "廉贞", "权": "破军", "科": "太阳", "忌": "太阴"},
        "乙": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
        "丙": {"禄": "天同", "权": "天梁", "科": "太阳", "忌": "天同"},
        "丁": {"禄": "天同", "权": "天梁", "科": "天机", "忌": "太阴"},
        "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
        "己": {"禄": "武曲", "权": "贪狼", "科": "太阴", "忌": "武曲"},
        "庚": {"禄": "太阳", "权": "武曲", "科": "天府", "忌": "太阳"},
        "辛": {"禄": "巨门", "权": "太阳", "科": "天府", "忌": "巨门"},
        "壬": {"禄": "天梁", "权": "天机", "科": "紫微", "忌": "天梁"},
        "癸": {"禄": "天机", "权": "巨门", "科": "紫微", "忌": "天机"},
    }
    return correct_transforms.get(year_stem)


# ============ 报告生成函数 ============


def _build_chart_overview(
    chart: Dict[str, Any],
    target_year: str,
    prediction_report: Any,
    markdown_content: str = "",
    question: str = ""
) -> Tuple[str, Dict[str, str]]:
    """
    构建命盘概览和四化信息

    Args:
        chart: 命盘数据
        target_year: 目标年份
        prediction_report: 预测报告

    Returns:
        (概览markdown, 四化信息字典)
    """
    birth = chart.get("birth_info", {})
    year_stem = chart.get("year_stem", birth.get("year_stem", ""))

    # 年干四化映射（根据紫微斗数典籍《紫微斗数全书》《飞星紫微斗数》）
    # 规则说明：
    # - 一星不可化两曜：同一星不能同时化科和化忌
    # - 化禄和化忌可以同星（如庚太阳、辛巨门、壬天梁、癸天机禄忌同宫）
    # 甲: 廉贞化禄、破军化权、太阳化科、太阴化忌
    # 乙: 廉贞化禄、破军化权、武曲化科、太阳化忌
    # 丙: 天同化禄、天梁化权、太阳化科、天同化忌
    # 丁: 天同化禄、天梁化权、天机化科、太阴化忌
    # 戊: 贪狼化禄、太阴化权、右弼化科、天机化忌
    # 己: 武曲化禄、贪狼化权、太阴化科、武曲化忌
    # 庚: 太阳化禄、武曲化权、天府化科、太阳化忌
    # 辛: 巨门化禄、太阳化权、天府化科、巨门化忌
    # 壬: 天梁化禄、天机化权、紫微化科、天梁化忌
    # 癸: 天机化禄、巨门化权、紫微化科、天机化忌
    wuxing_transforms = {
        "甲": {"禄": "廉贞", "权": "破军", "科": "太阳", "忌": "太阴"},
        "乙": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
        "丙": {"禄": "天同", "权": "天梁", "科": "太阳", "忌": "天同"},
        "丁": {"禄": "天同", "权": "天梁", "科": "天机", "忌": "太阴"},
        "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
        "己": {"禄": "武曲", "权": "贪狼", "科": "太阴", "忌": "武曲"},
        "庚": {"禄": "太阳", "权": "武曲", "科": "天府", "忌": "太阳"},
        "辛": {"禄": "巨门", "权": "太阳", "科": "天府", "忌": "巨门"},
        "壬": {"禄": "天梁", "权": "天机", "科": "紫微", "忌": "天梁"},
        "癸": {"禄": "天机", "权": "巨门", "科": "紫微", "忌": "天机"},
    }

    # 科忌同星校验
    transforms_info = _validate_and_fix_transforms(year_stem, wuxing_transforms)

    # 命宫主星
    ming_gong_stars = []
    palaces = chart.get("palaces", {})
    if isinstance(palaces, dict) and "命宫" in palaces:
        ming_data = palaces["命宫"]
        if isinstance(ming_data, dict):
            stars = ming_data.get("stars", [])
            if isinstance(stars, list):
                ming_gong_stars = [s.get("name", "") if isinstance(s, dict) else str(s) for s in stars[:5]]
            elif isinstance(stars, str):
                ming_gong_stars = stars.split(",")[:5]

    # 构建命盘概览 Markdown
    overview_lines = [
        "## 命盘概览\n",
        f"- **命盘ID**: {chart.get('chart_id', '未知')}\n",
        f"- **出生日期**: {birth.get('birth_date', birth.get('year', ''))} {birth.get('birth_time', '')}\n",
        f"- **性别**: {'男' if birth.get('gender') in ['male', '男'] else '女'}\n",
        f"- **年干**: {year_stem}\n",
        f"- **命宫主星**: {', '.join(ming_gong_stars) if ming_gong_stars else '未知'}\n",
    ]

    # 添加四化信息
    if transforms_info:
        overview_lines.append(f"\n### 年干四化 ({year_stem}年)\n")
        overview_lines.append(f"- **化禄**: {transforms_info.get('禄', '无')}\n")
        overview_lines.append(f"- **化权**: {transforms_info.get('权', '无')}\n")
        overview_lines.append(f"- **化科**: {transforms_info.get('科', '无')}\n")
        overview_lines.append(f"- **化忌**: {transforms_info.get('忌', '无')}\n")

    overview_markdown = "".join(overview_lines)

    # 组合完整报告
    full_report = f"""# 紫微斗数三层融合预测报告

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

**预测年份**: {target_year}

**命盘ID**: {chart.get('chart_id', '未知')}

---

{overview_markdown}

---

{prediction_report.causal_explanation if hasattr(prediction_report, 'causal_explanation') and prediction_report.causal_explanation else ''}

---

{markdown_content}

---

*本报告由三层融合预测系统生成*
*因果链推理 (40%) + 案例涌现推理 (35%) + 多Agent共识验证 (25%)*
"""

    # 返回 ReportBundle
    return ReportBundle(
        main_report=full_report,
        sub_reports={
            "prediction": markdown_content,
            "overview": overview_markdown
        },
        metadata={
            "chart_id": chart.get("chart_id", ""),
            "target_year": target_year,
            "question": question,
            "overall_judgment": prediction_report.overall_judgment if hasattr(prediction_report, 'overall_judgment') else "未知",
            "overall_confidence": prediction_report.overall_confidence if hasattr(prediction_report, 'overall_confidence') else 0,
        },
        generated_at=datetime.now().isoformat()
    )


def generate_full_prediction_markdown_report_sync(
    chart: Dict[str, Any],
    target_year: int,
    question: str = ""
) -> "ReportBundle":
    """
    同步版本 - 生成完整的三层融合预测 Markdown 报告

    Args:
        chart: 命盘数据
        target_year: 目标年份
        question: 分析问题

    Returns:
        ReportBundle: 包含完整 Markdown 报告的报告集
    """
    return generate_full_prediction_markdown_report(chart, target_year, question)
