"""
System API - 系统信息与状态
"""

from flask import Blueprint, jsonify
from ...utils.capability_manager import CapabilityManager

system_bp = Blueprint('system', __name__)

@system_bp.route('/poster', methods=['POST'])
def generate_vibe_poster():
    """生成每日气场海报元数据与SVG灵符"""
    try:
        data = request.get_json() or {}
        chart_id = data.get('chart_id')
        
        # 模拟生成逻辑
        vibe_score = 88
        core_char = "禄" if vibe_score > 70 else "泰"
        
        # 构建一个简单的赛博灵符 SVG
        svg_content = f"""<svg width="400" height="600" viewBox="0 0 400 600" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#0F172A"/>
            <path d="M50 50 L350 50 L350 550 L50 550 Z" stroke="#D4AF37" stroke-width="4" fill="none"/>
            <text x="200" y="150" font-family="serif" font-size="80" fill="#D4AF37" text-anchor="middle">{core_char}</text>
            <text x="200" y="300" font-family="serif" font-size="20" fill="#D4AF37" text-anchor="middle">赛博气场志 · 凤仙郡</text>
            <line x1="100" y1="350" x2="300" y2="350" stroke="#D4AF37" stroke-width="1"/>
            <text x="200" y="400" font-family="sans-serif" font-size="14" fill="#94A3B8" text-anchor="middle">气场指数: {vibe_score}</text>
            <text x="200" y="430" font-family="sans-serif" font-size="14" fill="#94A3B8" text-anchor="middle">因果自在，顺势而为</text>
        </svg>"""
        
        return jsonify({
            "success": True,
            "data": {
                "title": "赛博气场志",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "vibe_score": vibe_score,
                "svg": svg_content,
                "motto": "顺势而为，因果自在。"
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
