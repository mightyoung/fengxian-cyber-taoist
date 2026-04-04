"""
System API - 系统信息与状态
"""

from flask import Blueprint, jsonify
from ...utils.capability_manager import CapabilityManager

system_bp = Blueprint('system', __name__)

@system_bp.route('/fortune', methods=['GET'])
def get_global_fortune():
    """获取全服运势气象预报"""
    from ...models.divination import DivinationManager
    stats = DivinationManager.get_global_stats()
    return jsonify({
        "success": True,
        "data": stats
    })

@system_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """获取系统能力报告"""
    capabilities = CapabilityManager.get_capabilities()
    return jsonify({
        "success": True,
        "data": capabilities
    })

@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "success": True,
        "status": "ok",
        "service": "FengxianCyberTaoist Backend"
    })
