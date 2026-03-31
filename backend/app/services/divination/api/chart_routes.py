"""
Chart Routes - 命盘相关路由

提供命盘生成和获取的API接口。
"""

import asyncio

from flask import Blueprint, request, jsonify

from app.services.divination.api.common import validate_birth_info
from app.services.divination.agents.chart_agent import ChartAgent, BirthInfo
from app.models.divination import DivinationManager

# Create blueprint for chart routes
chart_bp = Blueprint('chart', __name__, url_prefix='/chart')


@chart_bp.route('/generate', methods=['POST'])
def generate_chart():
    """
    生成命盘

    Request Body:
        {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 10,
            "minute": 30,  // optional, default 0
            "gender": "male",
            "birthplace": "北京",  // optional
            "is_lunar": false  // optional, default false
        }

    Returns:
        {
            "success": true,
            "data": {
                "chart_id": "uuid",
                "chart": { ... }
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

        # 验证出生信息
        is_valid, error_msg = validate_birth_info(data)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": error_msg
            }), 400

        # 创建BirthInfo对象
        birth_info = BirthInfo(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=data['hour'],
            minute=data.get('minute', 0),
            gender=data['gender'],
            birthplace=data.get('birthplace', ''),
            is_lunar=data.get('is_lunar', False),
        )

        # 生成命盘
        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))

        # 使用DivinationManager持久化存储
        birth_info_dict = {
            'year': data['year'],
            'month': data['month'],
            'day': data['day'],
            'hour': data['hour'],
            'minute': data.get('minute', 0),
            'gender': data['gender'],
            'birthplace': data.get('birthplace', ''),
            'is_lunar': data.get('is_lunar', False),
        }
        saved_chart = DivinationManager.create_chart(
            birth_info=birth_info_dict,
            chart_data=chart.to_dict(),
        )

        return jsonify({
            "success": True,
            "data": {
                "chart_id": saved_chart.chart_id,
                "chart": saved_chart.chart_data
            }
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"生成命盘时出错: {str(e)}"
        }), 500


@chart_bp.route('/<chart_id>', methods=['GET'])
def get_chart(chart_id: str):
    """
    根据ID获取命盘

    URL Parameters:
        chart_id: 命盘ID

    Returns:
        {
            "success": true,
            "data": {
                "chart_id": "uuid",
                "chart": { ... }
            }
        }
    """
    try:
        chart = DivinationManager.get_chart(chart_id)
        if not chart:
            return jsonify({
                "success": False,
                "error": f"未找到ID为 {chart_id} 的命盘"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "chart_id": chart.chart_id,
                "chart": chart.chart_data,
                "birth_info": chart.birth_info
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取命盘时出错: {str(e)}"
        }), 500
