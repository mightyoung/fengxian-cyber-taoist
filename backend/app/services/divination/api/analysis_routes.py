"""
Analysis Routes - 分析相关路由

提供多智能体分析和领域分析（财富、健康、事业、学业、姻缘）的API接口。
"""

import asyncio
from functools import partial
from typing import Dict, Any

from flask import Blueprint, request, jsonify

from app.services.divination.api.common import _to_dict
from app.services.divination.agents.star_agent import llm_analyze_stars_sync, analyze_stars_sync
from app.services.divination.agents.palace_agent import llm_analyze_palaces_sync, analyze_palaces_sync
from app.services.divination.agents.transform_agent import llm_analyze_transforms_sync, get_transform
from app.services.divination.agents.pattern_agent import llm_analyze_patterns_sync
from app.services.divination.agents.timing_agent import llm_analyze_timing_sync
from app.services.divination.agents.wealth_agent import analyze_wealth_async
from app.services.divination.agents.health_agent import analyze_health_sync
from app.services.divination.agents.career_agent import analyze_career_sync
from app.services.divination.agents.relationship_agent import analyze_relationship_sync
from app.services.divination.agents.education_agent import analyze_education_sync
from app.models.divination import DivinationManager

# Create blueprint for analysis routes
analysis_bp = Blueprint('analysis', __name__, url_prefix='')

# Wealth related constants
WEALTH_PALACES = {
    "caibi": "财帛宫",
    "tianzhai": "田宅宫",
    "fude": "福德宫",
    "guanlu": "官禄宫"
}

WEALTH_STARS = {
    "主星": ["紫微", "天府", "武曲", "太阳", "太阴", "贪狼", "巨门", "天梁", "天同", "廉贞"],
    "辅星": ["左辅", "右弼", "天魁", "天钺", "文昌", "文曲", "禄存", "天马"],
    "煞星": ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"],
    "化曜": ["化禄", "化权", "化科", "化忌"]
}


async def _run_parallel_analysis(chart_data: Dict[str, Any]):
    """
    并行运行5个独立分析任务
    """
    loop = asyncio.get_event_loop()

    # 准备数据
    palace_stars = {k: [s.get('name', '') for s in v.get('stars', [])] for k, v in chart_data.get('palaces', {}).items()}

    # 并行执行5个独立分析任务 (LLM增强版本)
    star_task = loop.run_in_executor(None, partial(llm_analyze_stars_sync, chart_data))
    palace_task = loop.run_in_executor(None, partial(llm_analyze_palaces_sync, chart_data))
    transform_task = loop.run_in_executor(None, partial(llm_analyze_transforms_sync, chart_data))
    pattern_task = loop.run_in_executor(None, partial(llm_analyze_patterns_sync, chart_data, palace_stars))
    timing_task = loop.run_in_executor(None, partial(llm_analyze_timing_sync, chart_data))

    # 等待所有任务完成
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


def _format_analysis_response(analyses: Dict[str, Any]):
    """格式化分析结果为JSON响应格式"""
    return {
        "star_analysis": _to_dict(analyses.get("star_analysis")),
        "palace_analysis": _to_dict(analyses.get("palace_analysis")),
        "transform_analysis": _to_dict(analyses.get("transform_analysis")),
        "pattern_analysis": _to_dict(analyses.get("pattern_analysis")),
        "timing_analysis": _to_dict(analyses.get("timing_analysis")),
        "synthesis_report": _to_dict(analyses.get("synthesis_report"))
    }


# ==================== Agent Analysis Routes ====================

@analysis_bp.route('/agents/analyze', methods=['POST'])
def analyze_with_agents():
    """
    运行完整智能体分析（并行执行版本）

    Request Body:
        {
            "chart_id": "uuid",  // optional, if provided uses stored chart
            "chart": { ... }  // optional, if provided uses this chart directly
        }

    Returns:
        {
            "success": true,
            "data": {
                "star_analysis": { ... },
                "palace_analysis": { ... },
                "transform_analysis": { ... },
                "pattern_analysis": { ... },
                "timing_analysis": { ... },
                "synthesis_report": { ... }
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        chart_data = None

        # 优先使用chart_id获取命盘
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            # 使用请求中直接提供的chart
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 并行执行前5个分析任务
        analyses = asyncio.run(_run_parallel_analysis(chart_data))

        # 使用LLM进行综合分析
        from app.services.divination.agents.synthesis_agent import LLMSynthesisAnalyzer
        llm_analyzer = LLMSynthesisAnalyzer(chart_data)

        # 将分析结果转换为字典
        star_analysis_dict = _to_dict(analyses.get("star_analysis"))
        palace_analysis_dict = _to_dict(analyses.get("palace_analysis"))
        pattern_analysis_dict = _to_dict(analyses.get("pattern_analysis"))
        transform_analysis_dict = _to_dict(analyses.get("transform_analysis"))
        _to_dict(analyses.get("timing_analysis"))

        # 调用LLM综合分析
        synthesis_report = llm_analyzer.synthesize_with_llm_sync(
            star_analysis=star_analysis_dict,
            palace_analysis=palace_analysis_dict,
            pattern_analysis=pattern_analysis_dict,
            transform_analysis=transform_analysis_dict
        )
        analyses["synthesis_report"] = synthesis_report

        # 格式化响应
        response_data = _format_analysis_response(analyses)

        return jsonify({
            "success": True,
            "data": response_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"分析时出错: {str(e)}"
        }), 500


@analysis_bp.route('/agents/analyze/markdown', methods=['POST'])
def analyze_with_agents_markdown():
    """
    运行完整智能体分析并生成Markdown报告（主报告+分报告格式）

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "question": "..."      // optional, 用户问题
        }

    Returns:
        {
            "success": true,
            "data": {
                "main_report": "# 紫微斗数命盘综合分析报告\n...",
                "sub_reports": {
                    "star": "## 星曜分析\n...",
                    "palace": "## 宫位分析\n...",
                    "pattern": "## 格局分析\n...",
                    "transform": "## 四化分析\n...",
                    "timing": "## 运势分析\n..."
                },
                "metadata": { ... },
                "generated_at": "2026-03-19T..."
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        chart_data = None

        # 优先使用chart_id获取命盘
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        question = data.get('question', '请对我的命格进行全方位解读')

        # 并行执行5个分析任务
        analyses = asyncio.run(_run_parallel_analysis(chart_data))

        # 将分析结果转换为字典
        star_analysis_dict = _to_dict(analyses.get("star_analysis"))
        palace_analysis_dict = _to_dict(analyses.get("palace_analysis"))
        pattern_analysis_dict = _to_dict(analyses.get("pattern_analysis"))
        transform_analysis_dict = _to_dict(analyses.get("transform_analysis"))
        timing_analysis_dict = _to_dict(analyses.get("timing_analysis"))

        # 生成Markdown报告
        from app.services.divination.agents.report_generator import generate_markdown_report_sync
        report_bundle = generate_markdown_report_sync(
            chart_data=chart_data,
            star_analysis=star_analysis_dict,
            palace_analysis=palace_analysis_dict,
            pattern_analysis=pattern_analysis_dict,
            transform_analysis=transform_analysis_dict,
            timing_analysis=timing_analysis_dict,
            question=question
        )

        return jsonify({
            "success": True,
            "data": report_bundle.to_dict()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Markdown报告生成时出错: {str(e)}"
        }), 500


@analysis_bp.route('/stars/analyze', methods=['POST'])
def analyze_stars():
    """
    分析命盘星曜

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... }  // optional
        }

    Returns:
        {
            "success": true,
            "data": { ... }
        }
    """
    try:
        data = request.get_json() or {}
        chart_data = None

        # 获取命盘数据
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 分析星曜
        result = analyze_stars_sync(chart_data)

        return jsonify({
            "success": True,
            "data": {
                "main_stars": [s.to_dict() for s in result.main_stars],
                "auxiliary_stars": [s.to_dict() for s in result.auxiliary_stars],
                "sha_stars": [s.to_dict() for s in result.sha_stars],
                "transform_stars": [s.to_dict() for s in result.transform_stars],
                "palace_star_summary": result.palace_star_summary,
                "total_stars_count": result.total_stars_count
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"星曜分析时出错: {str(e)}"
        }), 500


@analysis_bp.route('/palaces/analyze', methods=['POST'])
def analyze_palaces():
    """
    分析宫位强弱

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... }  // optional
        }

    Returns:
        {
            "success": true,
            "data": { ... }
        }
    """
    try:
        data = request.get_json() or {}
        chart_data = None

        # 获取命盘数据
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 分析宫位
        result = analyze_palaces_sync(chart_data)

        return jsonify({
            "success": True,
            "data": {
                "palace_results": [
                    {
                        "palace_name": p.palace_name,
                        "branch": p.branch,
                        "tiangan": p.tiangan,
                        "score": {
                            "total": p.score.total_score,
                            "level": p.score.strength_level,
                            "master_star_score": p.score.master_star_score,
                            "auxiliary_star_score": p.score.auxiliary_star_score,
                            "sha_star_deduction": p.score.sha_star_deduction,
                            "transform_bonus_score": p.score.transform_bonus_score,
                            "palace_environment_score": p.score.palace_environment_score
                        },
                        "stars_in_palace": p.stars_in_palace,
                        "focal_point": p.focal_point,
                        "interpretation": p.interpretation
                    }
                    for p in result.palace_results
                ],
                "strongest_palace": result.strongest_palace,
                "weakest_palace": result.weakest_palace,
                "key_palaces": result.key_palaces
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"宫位分析时出错: {str(e)}"
        }), 500


@analysis_bp.route('/transforms/analyze', methods=['POST'])
def analyze_transforms():
    """
    分析四化

    Request Body:
        {
            "year_stem": "甲",  // required
            "chart_id": "uuid",  // optional
            "chart": { ... }  // optional
        }

    Returns:
        {
            "success": true,
            "data": { ... }
        }
    """
    try:
        data = request.get_json() or {}

        year_stem = data.get('year_stem')
        if not year_stem:
            return jsonify({
                "success": False,
                "error": "必须提供 year_stem (年干)"
            }), 400

        chart_data = data.get('chart')

        if chart_data:
            {
                k: [s.get('name', '') for s in v.get('stars', [])]
                for k, v in chart_data.get('palaces', {}).items()
            }

        # 分析四化
        result = get_transform(year_stem)

        return jsonify({
            "success": True,
            "data": result.to_dict()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"四化分析时出错: {str(e)}"
        }), 500


@analysis_bp.route('/health', methods=['GET'])
def health():
    """健康检查"""
    from app.services.divination.agents.case_based_predictor_constants import CHROMADB_AVAILABLE

    charts = DivinationManager.list_charts(limit=1000)
    return jsonify({
        "success": True,
        "data": {
            "status": "ok",
            "service": "divination-api",
            "stored_charts": len(charts),
            "capabilities": {
                "chroma": CHROMADB_AVAILABLE,
            }
        }
    })


# ==================== Wealth Analysis Route ====================

@analysis_bp.route('/wealth/analyze', methods=['POST'])
def analyze_wealth():
    """
    财运分析

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... }     // optional
        }

    Returns:
        {
            "success": true,
            "data": {
                "wealth_score": 75,
                "wealth_level": "中富",
                "caibi_palace": { ... },
                "tianzhai_palace": { ... },
                "fude_palace": { ... },
                "guanlu_palace": { ... },
                "wealth_patterns": [ ... ],
                "wealth_advantages": [ ... ],
                "wealth_weaknesses": [ ... ],
                "yearly_forecast": [ ... ],
                "recommendations": [ ... ],
                "investment_advice": { ... },
                "risk_assessment": { ... }
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        chart_data = None

        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 使用新的 WealthAgent 进行深度分析
        result = asyncio.run(analyze_wealth_async(chart_data, years=5))

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"财运分析时出错: {str(e)}"
        }), 500


# ==================== Health Analysis Route ====================

@analysis_bp.route('/health/analyze', methods=['POST'])
def analyze_health():
    """
    健康分析

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... }     // optional
        }

    Returns:
        {
            "success": true,
            "data": {
                "ji_e_palace_analysis": "疾厄宫分析",
                "health_risks": ["风险1", "风险2"],
                "protective_factors": ["保护因素"],
                "health_advice": "健康建议",
                "total_health_score": 75,
                "health_level": "健康良好",
                "ji_e_palace": { ... },
                "fu_de_palace": { ... },
                "disease_risks": [ ... ],
                "cancer_warnings": [ ... ],
                "health_advantages": [ ... ],
                "health_weaknesses": [ ... ]
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        chart_data = None

        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 使用 HealthAgent 进行健康分析
        result = analyze_health_sync(chart_data)

        # 转换为可序列化格式
        health_data = {
            "ji_e_palace_analysis": result.ji_e_palace_analysis,
            "health_risks": result.health_weaknesses,
            "protective_factors": result.health_advantages,
            "health_advice": result.health_advice,
            "total_health_score": result.total_health_score,
            "health_level": result.health_level,
            "ji_e_palace": {
                "palace_name": result.ji_e_palace.palace_name,
                "score": result.ji_e_palace.score,
                "strength_level": result.ji_e_palace.strength_level,
                "main_stars": result.ji_e_palace.main_stars,
                "auxiliary_stars": result.ji_e_palace.auxiliary_stars,
                "sha_stars": result.ji_e_palace.sha_stars,
                "transform_stars": result.ji_e_palace.transform_stars,
                "interpretation": result.ji_e_palace.interpretation,
                "health_indicators": result.ji_e_palace.health_indicators,
                "risk_factors": result.ji_e_palace.risk_factors,
                "protective_factors": result.ji_e_palace.protective_factors
            },
            "fu_de_palace": {
                "palace_name": result.fu_de_palace.palace_name,
                "score": result.fu_de_palace.score,
                "strength_level": result.fu_de_palace.strength_level,
                "main_stars": result.fu_de_palace.main_stars,
                "interpretation": result.fu_de_palace.interpretation
            },
            "disease_risks": [
                {
                    "disease_name": r.disease_name,
                    "star_combination": r.star_combination,
                    "risk_level": r.risk_level,
                    "category": r.category,
                    "notes": r.notes
                }
                for r in result.disease_risks
            ],
            "cancer_warnings": result.cancer_warnings,
            "health_advantages": result.health_advantages,
            "health_weaknesses": result.health_weaknesses
        }

        return jsonify({
            "success": True,
            "data": health_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"健康分析时出错: {str(e)}"
        }), 500


# ==================== Career Analysis Route ====================

@analysis_bp.route('/career/analyze', methods=['POST'])
def analyze_career():
    """
    事业分析

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "timing_transforms": { ... }  // optional, 流年四化信息
        }

    Returns:
        {
            "success": true,
            "data": {
                "career_level": "good",
                "career_score": 75,
                "career_direction": ["official", "business"],
                "best_palace": "官禄宫",
                "career_peak_ages": [32, 35, 45, 48],
                "potential_risks": ["事业竞争激烈，易有小人"],
                "recommendations": ["把握机遇，勇于担当更重要职位"]
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        chart_data = None

        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 获取流年四化（可选）
        timing_transforms = data.get('timing_transforms')

        # 使用 CareerAgent 进行事业分析
        result = analyze_career_sync(chart_data, timing_transforms)

        # 转换为可序列化格式
        career_data = result.to_dict()

        return jsonify({
            "success": True,
            "data": career_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"事业分析时出错: {str(e)}"
        }), 500


# ==================== Education Analysis Route ====================

@analysis_bp.route('/education/analyze', methods=['POST'])
def analyze_education():
    """
    学业分析

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "timing_transforms": { ... }  // optional, 流年四化信息
        }

    Returns:
        {
            "success": true,
            "data": {
                "learning_ability": "excellent",
                "learning_score": 90,
                "education_level_hint": "master",
                "best_study_ages": [14, 15, 16, 17, 18],
                "weak_subjects": ["语文理解表达", "数学逻辑"],
                "academic_risks": ["学业竞争压力大"],
                "study_tips": ["天赋极高，可挑战更高学历", "尝试深入研究，做学问型"]
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        chart_data = None

        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 获取流年四化（可选）
        timing_transforms = data.get('timing_transforms')

        # 使用 EducationAgent 进行学业分析
        result = analyze_education_sync(chart_data, timing_transforms)

        # 转换为可序列化格式
        education_data = result.to_dict()

        return jsonify({
            "success": True,
            "data": education_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"学业分析时出错: {str(e)}"
        }), 500


# ==================== Relationship Analysis Route ====================

@analysis_bp.route('/relationship/analyze', methods=['POST'])
def analyze_relationship():
    """
    姻缘感情分析

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "timing_transforms": { ... }  // optional, 流年四化信息
        }

    Returns:
        {
            "success": true,
            "data": {
                "marriage_timing": "normal",
                "marriage_age_hint": 28,
                "marriage_quality": "good",
                "spouse_features": {
                    "star_influence": "紫微",
                    "appearance": "端庄威严",
                    "personality": "自尊心强、有领导力",
                    "career": "管理或公职",
                    "age_difference": "差3-5岁"
                },
                "peach_blossom": "moderate",
                "peach_blossom_ages": [25, 27, 30],
                "relationship_risks": ["感情竞争激烈，易有第三者"],
                "marriage_advice": ["正常婚龄，宜把握28-32岁黄金期", "婚姻良好，用心经营更幸福"]
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        chart_data = None

        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if not chart:
                return jsonify({
                    "success": False,
                    "error": f"未找到ID为 {chart_id} 的命盘"
                }), 404
            chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')
            if not chart_data:
                return jsonify({
                    "success": False,
                    "error": "必须提供 chart_id 或 chart 数据"
                }), 400

        # 获取流年四化（可选）
        timing_transforms = data.get('timing_transforms')

        # 使用 RelationshipAgent 进行姻缘分析
        result = analyze_relationship_sync(chart_data, timing_transforms)

        # 转换为可序列化格式
        relationship_data = {
            "marriage_timing": result.marriage_timing.value,
            "marriage_age_hint": result.marriage_age_hint,
            "marriage_quality": result.marriage_quality.value,
            "spouse_features": {
                "star_influence": result.spouse_features.star_influence,
                "appearance": result.spouse_features.appearance,
                "personality": result.spouse_features.personality,
                "career": result.spouse_features.career,
                "age_difference": result.spouse_features.age_difference
            },
            "peach_blossom": result.peach_blossom.value,
            "peach_blossom_ages": result.peach_blossom_ages,
            "relationship_risks": result.relationship_risks,
            "marriage_advice": result.marriage_advice
        }

        return jsonify({
            "success": True,
            "data": relationship_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"姻缘分析时出错: {str(e)}"
        }), 500
