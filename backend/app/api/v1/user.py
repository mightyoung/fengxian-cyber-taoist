"""
User API - 用户功德与资料接口
"""

from flask import Blueprint, jsonify, g
from ...models.user import UserManager
from ...services.auth import require_auth as token_required

user_bp = Blueprint('user_profile', __name__)

@user_bp.route('/merit', methods=['GET'])
@token_required
def get_merit_status(current_user):
    """获取当前功德状态"""
    return jsonify({
        "success": True,
        "data": {
            "merit_balance": current_user.merit_balance,
            "merit_total_earned": current_user.merit_total_earned
        }
    })

@user_bp.route('/merit/daily', methods=['POST'])
@token_required
def daily_practice(current_user):
    """每日修行（签到领功德）"""
    # 简单逻辑：每天加10点
    # TODO: 增加日期判断，防止重复领取
    new_balance = UserManager.add_merit(current_user.id, 10, "每日修行")
    return jsonify({
        "success": True,
        "data": {
            "reward": 10,
            "new_balance": new_balance,
            "message": "功德+10，愿道友福慧双增。"
        }
    })
