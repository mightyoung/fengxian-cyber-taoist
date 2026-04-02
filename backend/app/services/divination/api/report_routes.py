"""
Report Routes - 报告相关路由

提供预测报告生成和格式转换的API接口。
"""

from typing import Dict, Any

from flask import Blueprint, request, jsonify

from app.services.divination.api.common import _to_dict
from app.models.divination import DivinationManager

# Create blueprint for report routes
report_bp = Blueprint('report', __name__, url_prefix='/report')


def _transform_to_professional_plain(markdown_content: str) -> str:
    """使用术语表将专业报告转换为通俗易懂版本"""
    try:
        import os
        import json
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

    from app.services.divination.agents.star_agent import llm_analyze_stars_sync
    from app.services.divination.agents.palace_agent import llm_analyze_palaces_sync
    from app.services.divination.agents.transform_agent import llm_analyze_transforms_sync
    from app.services.divination.agents.pattern_agent import llm_analyze_patterns_sync
    from app.services.divination.agents.timing_agent import llm_analyze_timing_sync

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
    生成预测报告

    支持两种报告类型：
    - professional_plain: 专业通俗版（默认），使用LLM生成详细报告
    - xiaohongshu: 小红书版

    Request Body:
        {
            "chart_id": "uuid",       // optional
            "chart": { ... },          // optional
            "user_name": "杨宏辉",    // optional
            "year": 2026,             // 预测年份
            "report_type": "professional_plain"  // professional_plain | xiaohongshu
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
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({"success": False, "error": f"未找到ID为 {chart_id} 的命盘"}), 404
            chart_data = chart.chart_data
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
        _to_dict(analyses.get("star_analysis"))
        _to_dict(analyses.get("palace_analysis"))
        _to_dict(analyses.get("pattern_analysis"))
        transform_dict = _to_dict(analyses.get("transform_analysis"))
        _to_dict(analyses.get("timing_analysis"))

        # 生成三层融合预测报告
        from app.services.divination.agents.report_generator import (
            generate_prediction_report_sync,
        )
        prediction_report = generate_prediction_report_sync(
            chart=chart_data,
            target_year=year,
            question=f"请对{user_name}{year}年运势进行全面预测分析",
        )

        # 根据报告类型生成不同格式（DivinationManager统一存储，无需手动写文件）
        # 只保留 professional_plain (详细LLM版) 和 xiaohongshu
        if report_type == "xiaohongshu":
            # 小红书版 - 先生成专业报告，再转换为小红书格式
            from app.utils.unified_report_generator import generate_markdown_report
            analysis_result = {
                "overall_judgment": prediction_report.overall_judgment if hasattr(prediction_report, 'overall_judgment') else "平",
                "dimensions": {k: {"judgment": v.judgment, "reasoning": getattr(v, 'reasoning', '')} for k, v in getattr(prediction_report, 'dimensions', {}).items()},
                "causal_chain_result": {
                    "severity_level": prediction_report.causal_chain_result.severity_level if hasattr(prediction_report, 'causal_chain_result') and hasattr(prediction_report.causal_chain_result, 'severity_level') else "潜在",
                    "key_chains": prediction_report.causal_chain_result.key_chains if hasattr(prediction_report, 'causal_chain_result') else []
                } if hasattr(prediction_report, 'causal_chain_result') else {},
                "transforms": transform_dict,
            }
            full_markdown = generate_markdown_report(
                chart=chart_data,
                analysis_result=analysis_result,
                target_year=year,
                use_llm=True
            )
            from app.services.divination.agents.xiaohongshu_agent import generate_xhs_report_sync
            xhs_result = generate_xhs_report_sync(
                report=full_markdown,
                user_name=user_name,
                user_type="运势预测"
            )
            markdown = xhs_result.get("markdown", xhs_result.get("content", full_markdown))
        else:
            # professional_plain - 专业通俗版（默认，使用LLM生成详细报告）
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

        # DivinationManager统一存储报告（包含完整markdown_content）
        saved_report = DivinationManager.create_report(
            chart_id=chart_id or "inline",
            user_name=user_name,
            target_year=year,
            report_type=report_type,
            markdown_content=markdown,
            metadata={
                "user_name": user_name,
                "year": year,
                "report_type": report_type,
            },
        )

        return jsonify({
            "success": True,
            "data": {
                "report_id": saved_report.report_id,
                "chart_id": chart_id or "inline",
                "markdown": markdown,
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
def get_reports_by_chart(chart_id):
    """
    获取指定命盘的所有报告

    Returns:
        {
            "success": true,
            "data": {
                "reports": [...]
            }
        }
    """
    chart = DivinationManager.get_chart(chart_id)
    if not chart:
        return jsonify({"success": False, "error": f"未找到ID为 {chart_id} 的命盘"}), 404

    reports = DivinationManager.get_reports_by_chart(chart_id)
    return jsonify({
        "success": True,
        "data": {
            "reports": [r.to_dict() for r in reports]
        }
    })


@report_bp.route('/id/<report_id>', methods=['GET'])
def get_report_by_id(report_id):
    """
    根据报告ID获取单个报告

    Returns:
        {
            "success": true,
            "data": {
                "report": {...}
            }
        }
    """
    report = DivinationManager.get_report(report_id)
    if not report:
        return jsonify({"success": False, "error": f"未找到ID为 {report_id} 的报告"}), 404

    return jsonify({
        "success": True,
        "data": {
            "report": report.to_dict()
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
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if chart:
                chart_data = chart.chart_data

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
                import traceback
                traceback.print_exc()
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
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"报告转换时出错: {str(e)}"}), 500
