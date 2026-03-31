"""
报告图表生成辅助模块

从分析结果自动生成各种图表：
- 五维运势雷达图
- 月度运势柱状图
- 置信度仪表盘
- 年度热力图
- 月度宜忌建议

使用方法:
    from app.utils.report_chart_helper import generate_report_charts

    chart_data = generate_report_charts(analysis_result)
    # 返回 {
    #     "charts": {"radar": bytes, "bar": bytes, "gauge": bytes},
    #     "heatmap": bytes,
    #     "monthly_advice": [...]
    # }
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# 尝试导入图表生成器
try:
    from .chart_generator import (
        generate_radar_chart,
        generate_bar_chart,
        generate_confidence_gauge,
        generate_monthly_heatmap,
    )
    CHART_GENERATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chart generator not available: {e}")
    CHART_GENERATOR_AVAILABLE = False


def generate_report_charts(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    从分析结果生成所有报告图表

    Args:
        analysis_result: 分析结果字典，包含：
            - dimensions: 分维度分析结果
            - overall_judgment: 综合判断
            - overall_confidence: 置信度
            - monthly_data: 月度数据（可选）

    Returns:
        {
            "charts": {
                "radar": bytes,      # 五维雷达图
                "bar": bytes,        # 月度柱状图
                "gauge": bytes       # 置信度仪表盘
            },
            "heatmap": bytes,          # 年度热力图
            "monthly_advice": [...]    # 月度宜忌建议
        }
    """
    if not CHART_GENERATOR_AVAILABLE:
        logger.warning("Chart generator not available, returning empty charts")
        return {"charts": None, "heatmap": None, "monthly_advice": []}

    result = {
        "charts": {},
        "heatmap": None,
        "monthly_advice": []
    }

    try:
        # 1. 生成五维雷达图
        dimensions_data = analysis_result.get("dimensions", {})
        if dimensions_data:
            dims, scores = _extract_dimension_data(dimensions_data)
            if dims and scores:
                radar_img = generate_radar_chart(
                    dimensions=dims,
                    scores=scores,
                    title="五维运势雷达图"
                )
                if radar_img:
                    result["charts"]["radar"] = radar_img

        # 2. 生成月度柱状图
        monthly_data = analysis_result.get("monthly_data", [])
        if monthly_data:
            months = [m.get("month", f"{i+1}月") for i, m in enumerate(monthly_data)]
            values = [m.get("score", 3.5) * 20 for m in monthly_data]  # 转换为百分制

            bar_img = generate_bar_chart(
                labels=months,
                values=values,
                title="月度运势评分"
            )
            if bar_img:
                result["charts"]["bar"] = bar_img

        # 3. 生成置信度仪表盘
        confidence = analysis_result.get("overall_confidence", 0.5)
        analysis_result.get("overall_judgment", "平")
        gauge_img = generate_confidence_gauge(
            value=int(confidence * 100),
            label="综合运势评分"
        )
        if gauge_img:
            result["charts"]["gauge"] = gauge_img

        # 4. 生成年度热力图
        if monthly_data:
            heatmap_data = [
                {
                    "month": m.get("month", f"{i+1}月"),
                    "fortune": m.get("score", 3.5),
                    "label": _score_to_label(m.get("score", 3.5))
                }
                for i, m in enumerate(monthly_data)
            ]
            heatmap_img = generate_monthly_heatmap(
                monthly_data=heatmap_data,
                title="2026年每月运势热力图"
            )
            if heatmap_img:
                result["heatmap"] = heatmap_img

        # 5. 提取月度宜忌建议
        result["monthly_advice"] = _extract_monthly_advice(analysis_result)

        logger.info(f"图表生成完成: {len(result['charts'])} 个图表")
        return result

    except Exception as e:
        logger.error(f"图表生成失败: {e}")
        return {"charts": None, "heatmap": None, "monthly_advice": []}


def _extract_dimension_data(dimensions: Dict[str, Any]) -> tuple:
    """
    从分维度数据提取雷达图所需的数据

    Args:
        dimensions: 维度字典 {"事业": {"judgment": "吉", "confidence": 0.6}, ...}

    Returns:
        (维度列表, 得分列表)
    """
    # 维度名称映射（英文->中文）
    DIMENSION_NAMES = {
        "career": "事业",
        "wealth": "财运",
        "finance": "财运",
        "money": "财运",
        "relationship": "感情",
        "love": "感情",
        "marriage": "感情",
        "health": "健康",
        "personality": "人际关系",
        "social": "人际关系",
        "人际": "人际关系"
    }

    dims = []
    scores = []

    # 维度显示顺序
    ORDER = ["事业", "财运", "感情", "健康", "人际关系"]

    for dim_key in ORDER:
        if dim_key in dimensions:
            dim_data = dimensions[dim_key]
            dims.append(dim_key)
            # 根据判断类型计算得分
            judgment = dim_data.get("judgment", "平")
            confidence = dim_data.get("confidence", 0.5)

            if judgment == "吉":
                score = 4.0 + confidence * 1.0  # 4.0-5.0
            elif judgment == "凶":
                score = 1.0 + confidence * 1.0  # 1.0-2.0
            else:  # 平
                score = 2.5 + confidence * 1.0  # 2.5-3.5

            scores.append(min(5.0, max(1.0, score)))

    # 如果没有标准维度，尝试从原始数据提取
    if not dims:
        for key, value in dimensions.items():
            if isinstance(value, dict) and "judgment" in value:
                # 尝试转换英文名称
                display_name = DIMENSION_NAMES.get(key, key)
                dims.append(display_name)

                judgment = value.get("judgment", "平")
                confidence = value.get("confidence", 0.5)

                if judgment == "吉":
                    score = 4.0 + confidence * 1.0
                elif judgment == "凶":
                    score = 1.0 + confidence * 1.0
                else:
                    score = 2.5 + confidence * 1.0

                scores.append(min(5.0, max(1.0, score)))

    return dims, scores


def _score_to_label(score: float) -> str:
    """将得分转换为运势标签"""
    if score >= 4.5:
        return "高峰"
    elif score >= 4.0:
        return "上升"
    elif score >= 3.0:
        return "平稳"
    elif score >= 2.0:
        return "波动"
    else:
        return "低沉"


def _extract_monthly_advice(analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从分析结果中提取月度宜忌建议"""
    monthly_advice = []

    # 尝试从monthly_data提取
    monthly_data = analysis_result.get("monthly_data", [])

    # 尝试从suggestions中提取
    analysis_result.get("suggestions", [])

    if monthly_data:
        for i, month_data in enumerate(monthly_data):
            advice = {
                "month": month_data.get("month", f"{i+1}"),
                "fortune_score": month_data.get("score", 3.5),
                "fortune_label": _score_to_label(month_data.get("score", 3.5)),
                "yi": month_data.get("yi", _default_yi_list(i)),
                "ji": month_data.get("ji", _default_ji_list(i)),
                "finance": month_data.get("finance", ""),
                "health": month_data.get("health", "")
            }
            monthly_advice.append(advice)
    else:
        # 生成12个月的默认建议
        for i in range(12):
            advice = {
                "month": f"{i+1}",
                "fortune_score": 3.5,
                "fortune_label": "平稳",
                "yi": _default_yi_list(i),
                "ji": _default_ji_list(i),
                "finance": "",
                "health": ""
            }
            monthly_advice.append(advice)

    return monthly_advice


def _default_yi_list(month: int) -> List[str]:
    """根据月份返回默认宜做事项"""
    base_yi = [
        ["制定计划", "学习新知", "结交朋友"],
        ["稳扎稳打", "维护关系", "储备能量"],
        ["抓住机遇", "积极行动", "拓展人脉"],
        ["保持现状", "积累经验", "观察形势"],
        ["全力以赴", "勇攀高峰", "把握机会"],
        ["乘胜追击", "巩固成果", "人际拓展"],
        ["休养调整", "学习提升", "反思总结"],
        ["贵人相助", "团队合作", "财运回升"],
        ["再创佳绩", "收获成果", "人际活跃"],
        ["盘点收获", "感恩回报", "规划未来"],
        ["总结经验", "调整心态", "为年末冲刺"],
        ["年末冲刺", "关系维护", "积极总结"]
    ]
    return base_yi[month % 12]


def _default_ji_list(month: int) -> List[str]:
    """根据月份返回默认忌做事项"""
    base_ji = [
        ["盲目投资", "过度焦虑", "冲动决策"],
        ["急功近利", "消极懈怠", "过度消费"],
        ["犹豫不决", "错失良机", "固步自封"],
        ["盲目扩张", "轻举妄动", "消极等待"],
        ["犹豫不决", "畏缩不前", "骄傲自满"],
        ["得意忘形", "过度劳累", "放松警惕"],
        ["勉强行事", "透支体力", "盲目冒进"],
        ["独断专行", "小人作祟", "财务冒险"],
        ["骄傲自满", "错失机会", "人际冲突"],
        ["贪得无厌", "消极抱怨", "过度消费"],
        ["急躁冒进", "人际摩擦", "财务风险"],
        ["虎头蛇尾", "忽视健康", "人际冷淡"]
    ]
    return base_ji[month % 12]


def generate_simple_charts(analysis_result: Dict[str, Any]) -> Optional[Dict[str, bytes]]:
    """
    生成简单图表（不包含热力图和月度建议）

    适用于只需要图表，不需要完整信息的场景

    Returns:
        {"radar": bytes, "bar": bytes, "gauge": bytes} 或 None
    """
    if not CHART_GENERATOR_AVAILABLE:
        return None

    try:
        charts = {}

        # 雷达图
        dimensions_data = analysis_result.get("dimensions", {})
        if dimensions_data:
            dims, scores = _extract_dimension_data(dimensions_data)
            if dims and scores:
                radar_img = generate_radar_chart(
                    dimensions=dims,
                    scores=scores,
                    title="五维运势雷达图"
                )
                if radar_img:
                    charts["radar"] = radar_img

        # 仪表盘
        confidence = analysis_result.get("overall_confidence", 0.5)
        gauge_img = generate_confidence_gauge(
            value=int(confidence * 100),
            label="综合运势评分"
        )
        if gauge_img:
            charts["gauge"] = gauge_img

        return charts if charts else None

    except Exception as e:
        logger.error(f"简单图表生成失败: {e}")
        return None
