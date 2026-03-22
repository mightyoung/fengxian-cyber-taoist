"""
Report Routes - 报告相关路由

提供预测报告生成和格式转换的API接口。
"""

import os
from datetime import datetime
from typing import Dict, Any

from flask import Blueprint, request, jsonify

from app.services.divination.api import (
    _charts_storage,
    _to_dict,
    _format_transform_explanation,
    _format_palace_overview,
)

# Create blueprint for report routes
report_bp = Blueprint('report', __name__, url_prefix='/report')


def _transform_to_professional_plain(markdown_content: str) -> str:
    """使用术语表将专业报告转换为通俗易懂版本"""
    try:
        import os, json
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        term_map_path = os.path.join(base_dir, "services", "divination", "resources", "terminology_map.json")

        if os.path.exists(term_map_path):
            with open(term_map_path, encoding="utf-8") as f:
                term_map = json.load(f)
        else:
            return markdown_content

        content = markdown_content
        replaced = 0
        for category in term_map.get("categories", []):
            for term in category.get("terms", []):
                key = term.get("term", "")
                plain = term.get("plain", "")
                explanation = term.get("explanation", "")
                if key and plain and explanation:
                    # 用 "术语【通俗名】解释" 格式替换
                    if key in content:
                        content = content.replace(
                            key,
                            f"{key}（{plain}）"
                        )
                        replaced += 1

        if replaced > 0:
            return content
        return markdown_content

    except Exception:
        return markdown_content


async def _run_parallel_analysis_for_report(chart_data: Dict[str, Any]):
    """
    并行运行5个独立分析任务（报告专用）
    """
    import asyncio
    from functools import partial

    from app.services.divination.api import (
        llm_analyze_stars_sync,
        llm_analyze_palaces_sync,
        llm_analyze_transforms_sync,
        llm_analyze_patterns_sync,
        llm_analyze_timing_sync,
    )

    loop = asyncio.get_event_loop()

    palace_stars = {k: [s.get('name', '') for s in v.get('stars', [])] for k, v in chart_data.get('palaces', {}).items()}

    star_task = loop.run_in_executor(None, partial(llm_analyze_stars_sync, chart_data))
    palace_task = loop.run_in_executor(None, partial(llm_analyze_palaces_sync, chart_data))
    transform_task = loop.run_in_executor(None, partial(llm_analyze_transforms_sync, chart_data))
    pattern_task = loop.run_in_executor(None, partial(llm_analyze_patterns_sync, chart_data, palace_stars))
    timing_task = loop.run_in_executor(None, partial(llm_analyze_timing_sync, chart_data))

    star_analysis, palace_analysis, transform_analysis, pattern_analysis, timing_analysis = \
        await asyncio.gather(
            star_task,
            palace_task,
            transform_task,
            pattern_task,
            timing_task
        )

    return {
        "star_analysis": star_analysis,
        "palace_analysis": palace_analysis,
        "transform_analysis": transform_analysis,
        "pattern_analysis": pattern_analysis,
        "timing_analysis": timing_analysis
    }


@report_bp.route('/generate', methods=['POST'])
def generate_prediction_report():
    """
    生成三层融合预测报告（综合报告 B）

    Request Body:
        {
            "chart_id": "uuid",       // optional
            "chart": { ... },          // optional
            "user_name": "杨宏辉",    // optional
            "year": 2026               // 预测年份
        }

    Returns:
        {
            "success": true,
            "data": {
                "chart_id": "...",
                "markdown": "# 预测报告\n...",
                "metadata": { ... }
            }
        }
    """
    try:
        import asyncio

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        chart_data = None
        chart_id = data.get("chart_id")
        if chart_id:
            if chart_id not in _charts_storage:
                return jsonify({"success": False, "error": f"未找到ID为 {chart_id} 的命盘"}), 404
            chart_data = _charts_storage[chart_id]["chart"]
        else:
            chart_data = data.get("chart")
            if not chart_data:
                return jsonify({"success": False, "error": "必须提供 chart_id 或 chart 数据"}), 400

        year = data.get("year", 2026)
        user_name = data.get("user_name", "命主")
        report_type = data.get("report_type", "full")  # 支持: prediction, enhanced, professional_plain, full

        # 并行执行分析
        analyses = asyncio.run(_run_parallel_analysis_for_report(chart_data))

        # 转换为字典
        star_dict = _to_dict(analyses.get("star_analysis"))
        palace_dict = _to_dict(analyses.get("palace_analysis"))
        pattern_dict = _to_dict(analyses.get("pattern_analysis"))
        transform_dict = _to_dict(analyses.get("transform_analysis"))
        timing_dict = _to_dict(analyses.get("timing_analysis"))

        # 生成三层融合预测报告
        from app.services.divination.agents.report_generator import (
            generate_prediction_report_sync,
            format_prediction_report_markdown,
        )
        prediction_report = generate_prediction_report_sync(
            chart=chart_data,
            target_year=year,
            question=f"请对{user_name}{year}年运势进行全面预测分析",
        )

        # 确定返回的markdown和文件名
        reports_base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 'reports')
        user_folder = os.path.join(reports_base, f"{user_name}_{year}")
        os.makedirs(user_folder, exist_ok=True)
        report_id_str = chart_id or f"inline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 根据报告类型生成不同格式
        if report_type == "prediction":
            # 基础三层融合报告
            markdown = format_prediction_report_markdown(prediction_report)
            saved_filename = f"{report_id_str}_prediction.md"
        elif report_type == "enhanced":
            # 增强版 - 包含详细四化解读的完整报告
            from app.services.divination.agents.report_transformer import ReportTransformer
            transformer = ReportTransformer()
            # 获取四化详细解读（从parallel analysis的结果）
            transform_content = _format_transform_explanation(chart_data, transform_dict)
            palace_content = _format_palace_overview(chart_data, palace_dict)
            # 基础预测报告
            prediction_markdown = format_prediction_report_markdown(prediction_report)
            # 合并为增强版
            markdown = f"""# {user_name} {year}年运势预测报告（增强版）

> **命主**: {user_name}
> **预测年份**: {year}年
> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **分析系统**: FengxianCyberTaoist 紫微斗数智能分析系统

---

## 一、命盘概览

{palace_content}

---

## 二、四化详解

{transform_content}

---

## 三、年度运势分析

{prediction_markdown}
"""
            saved_filename = f"{report_id_str}_enhanced.md"
        elif report_type == "professional_plain":
            # 专业通俗版 - 使用unified_report_generator生成详细LLM内容
            from app.utils.unified_report_generator import generate_markdown_report
            # 构建analysis_result（从并行分析结果）
            analysis_result = {
                "overall_judgment": prediction_report.overall_judgment if hasattr(prediction_report, 'overall_judgment') else "平",
                "dimensions": {k: {"judgment": v.judgment, "reasoning": getattr(v, 'reasoning', '')} for k, v in getattr(prediction_report, 'dimensions', {}).items()},
                "causal_chain_result": {
                    "severity_level": prediction_report.causal_chain_result.severity_level if hasattr(prediction_report, 'causal_chain_result') and hasattr(prediction_report.causal_chain_result, 'severity_level') else "潜在",
                    "key_chains": prediction_report.causal_chain_result.key_chains if hasattr(prediction_report, 'causal_chain_result') else []
                } if hasattr(prediction_report, 'causal_chain_result') else {},
                "transforms": transform_dict,
            }
            markdown = generate_markdown_report(
                chart=chart_data,
                analysis_result=analysis_result,
                target_year=year,
                use_llm=True
            )
            # 添加命主名称到标题（如果chart中没有）
            markdown = markdown.replace("# 命主 ", f"# {user_name} ")
            saved_filename = f"{report_id_str}_professional_plain.md"
        else:  # "full" - 综合版，合并所有报告
            # 生成完整综合报告
            from app.services.divination.agents.report_transformer import ReportTransformer
            transformer = ReportTransformer()
            plain_markdown = transformer.transform_report_sync(prediction_report, style="professional_plain", user_name=user_name, chart_data=chart_data)
            prediction_markdown = format_prediction_report_markdown(prediction_report)

            # 合并报告: 专业通俗 + 三层分析 + 因果链
            markdown = f"""# {user_name} {year}年运势预测报告

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **命盘ID**: {report_id_str}
> **报告类型**: 综合完整版

---

## 一、命盘概览与通俗解读

{plain_markdown}

---

## 二、三层融合专业分析

{prediction_markdown}

---

## 三、趋避建议

1. 因实证较强，建议寻求专业化解指导
2. 把握机会，谨慎行事
"""

            saved_filename = f"{report_id_str}_full.md"

        # 保存报告
        report_path = os.path.join(user_folder, saved_filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return jsonify({
            "success": True,
            "data": {
                "chart_id": chart_id or "inline",
                "markdown": markdown,
                "report_path": report_path,
                "metadata": {
                    "user_name": user_name,
                    "year": year,
                    "report_type": report_type,
                },
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"报告生成时出错: {str(e)}"}), 500


@report_bp.route('/<chart_id>', methods=['GET'])
def get_report(chart_id):
    """
    获取已存储的报告

    Returns:
        {
            "success": true,
            "data": {
                "prediction_report": "# 报告\n...",
                "xiaohongshu": "# 小红书版\n...",
                "professional_plain": "# 通俗版\n..."
            }
        }
    """
    if chart_id not in _charts_storage:
        return jsonify({"success": False, "error": f"未找到ID为 {chart_id} 的命盘"}), 404

    stored = _charts_storage[chart_id]
    return jsonify({
        "success": True,
        "data": {
            "prediction_report": stored.get("prediction_report", ""),
            "xiaohongshu": stored.get("xiaohongshu", ""),
            "professional_plain": stored.get("professional_plain", ""),
        }
    })


@report_bp.route('/transform', methods=['POST'])
def transform_report():
    """
    将报告转换为不同风格

    Request Body:
        {
            "chart_id": "uuid",              // optional
            "chart": { ... },                 // optional
            "report_content": "...",          // 原始报告markdown内容
            "style": "professional_plain"     // professional_plain | xiaohongshu
        }

    Returns:
        {
            "success": true,
            "data": {
                "content": "# 转换后内容\n...",
                "style": "..."
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        report_content = data.get("report_content", "")
        style = data.get("style", "professional_plain")

        chart_data = None
        chart_id = data.get("chart_id")
        if chart_id and chart_id in _charts_storage:
            chart_data = _charts_storage[chart_id]["chart"]

        user_name = data.get("user_name", "命主")

        if style == "xiaohongshu":
            # 小红书版转换
            chart = chart_data or {}
            try:
                from app.services.divination.agents.xiaohongshu_agent import generate_xhs_report_sync
                xhs_result = generate_xhs_report_sync(
                    report=report_content,
                    user_name=user_name,
                    user_type="财运预测",
                )
                content = xhs_result.get("markdown", xhs_result.get("content", report_content))
            except Exception as e:
                import traceback; traceback.print_exc()
                return jsonify({
                    "success": False,
                    "error": f"小红书版生成失败: {str(e)}"
                }), 500
        else:
            # 通俗版转换 - 使用术语表替换
            content = _transform_to_professional_plain(report_content)

        return jsonify({
            "success": True,
            "data": {
                "content": content,
                "style": style,
            }
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "error": f"报告转换时出错: {str(e)}"}), 500
