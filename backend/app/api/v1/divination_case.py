"""
Case API - 命理案例库管理接口
"""

import json
from flask import Blueprint, request, jsonify
from ...services.divination.agents.case_based_predictor import CaseBasedPredictor
from ...services.auth import require_auth as token_required

case_bp = Blueprint('divination_case', __name__)

@case_bp.route('/upload', methods=['POST'])
@token_required
def upload_personal_case(current_user):
    """
    用户上传个人历史案例，以校准预测模型
    
    请求（JSON）:
        {
            "case_name": "我的2022年大变动",
            "chart": { ... },
            "trajectory": {
                "birth_year": 1990,
                "events": [
                    { "age": 32, "event_type": "事业", "description": "辞职创业", "significance": 0.8 }
                ]
            }
        }
    """
    try:
        data = request.get_json() or {}
        chart = data.get('chart')
        trajectory_data = data.get('trajectory')
        
        if not chart or not trajectory_data:
            return jsonify({"success": False, "error": "缺少命盘或轨迹数据"}), 400
            
        # TODO: 将案例持久化到用户专属目录
        # 这里先演示添加到当前运行时的 Predictor 中
        predictor = CaseBasedPredictor()
        
        # 简单转换 trajectory_data -> LifeTrajectory (如果是为了演示)
        # 实际生产中应保存为文件，后续 auto_load 加载
        
        return jsonify({
            "success": True,
            "message": "案例已上传，功德+100（演示）",
            "reward": 100
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
