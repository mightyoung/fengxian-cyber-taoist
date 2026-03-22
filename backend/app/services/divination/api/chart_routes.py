"""
Chart Routes - 命盘相关路由

提供命盘生成和获取的API接口。
"""

import asyncio
import uuid
from typing import Dict, Any

from flask import Blueprint, request, jsonify

from app.services.divination.api import (
    _charts_storage,
    _to_dict,
    validate_birth_info,
    ChartAgent,
    BirthInfo,
)

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

        # 生成chart_id并存储
        chart_id = str(uuid.uuid4())
        chart_data = chart.to_dict()

        _charts_storage[chart_id] = {
            'chart': chart_data,
            'birth_info': data,
        }

        return jsonify({
            "success": True,
            "data": {
                "chart_id": chart_id,
                "chart": chart_data
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
        if chart_id not in _charts_storage:
            return jsonify({
                "success": False,
                "error": f"未找到ID为 {chart_id} 的命盘"
            }), 404

        stored_data = _charts_storage[chart_id]

        return jsonify({
            "success": True,
            "data": {
                "chart_id": chart_id,
                "chart": stored_data['chart'],
                "birth_info": stored_data['birth_info']
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取命盘时出错: {str(e)}"
        }), 500
