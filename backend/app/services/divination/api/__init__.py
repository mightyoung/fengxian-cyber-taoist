"""
Divination API Module - 紫微斗数API模块

提供命盘生成和分析的REST API接口。
"""

from flask import Blueprint

# 数据文件路径常量 - 从 common 导入
from app.services.divination.api.common import DATA_BASE_PATH

# 工具函数 - 从 common 导入
from app.services.divination.api.common import _to_dict, validate_birth_info

# Create blueprints
divination_bp = Blueprint('divination', __name__, url_prefix='/api/divination')
knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/divination/knowledge')


def _format_transform_explanation(chart_data, transform_dict):
    """Format transform analysis into readable markdown"""
    lines = []
    transforms = transform_dict.get("transforms", []) if isinstance(transform_dict, dict) else []

    transform_meanings = {
        "化禄": ("机会与收获", "🌟"),
        "化权": ("权力与掌控", "💪"),
        "化科": ("声誉与学习", "📚"),
        "化忌": ("挑战与考验", "⚠️"),
    }

    if transforms:
        for t in transforms:
            t_type = t.get("type", "")
            star = t.get("star", "")
            palace = t.get("palace", "")
            meaning, emoji = transform_meanings.get(t_type, ("未知", "❓"))
            lines.append(f"### {emoji} {t_type} — {star} 在{palace}\n")
            lines.append(f"**能量属性**: {meaning}\n")
            lines.append(f"- 化星: {star}\n")
            lines.append(f"- 所在宫位: {palace}\n\n")
    else:
        lines.append("*四化信息暂无详细解读*\n")

    return "".join(lines) if lines else "*四化信息暂无*\n"


def _format_palace_overview(chart_data, palace_dict):
    """Format palace overview into readable markdown"""
    lines = []
    birth_info = chart_data.get("birth_info", {})
    palaces = chart_data.get("palaces", {})

    lines.append("### 基本信息\n\n")
    lines.append("| 项目 | 内容 |\n")
    lines.append("|------|------|\n")
    lines.append(f"| 出生年份 | {birth_info.get('year', '未知')}年 |\n")
    lines.append(f"| 五行局 | {birth_info.get('wuxing_ju', '未知')} |\n")
    lines.append(f"| 年干 | {birth_info.get('year_gan', '未知')} |\n\n")

    ming_gong = palaces.get("命宫", {})
    ming_stars = ming_gong.get("stars", [])
    main_star = ming_stars[0].get("name", "未知") if ming_stars else "未知"

    lines.append("### 命宫信息\n\n")
    lines.append(f"- **命宫主星**: {main_star}\n")
    lines.append(f"- **命宫星曜**: {', '.join([s.get('name', '') for s in ming_stars]) if ming_stars else '无主星'}\n\n")

    return "".join(lines)


# Import route modules AFTER defining all shared utilities (avoids circular import)
from app.services.divination.api import chart_routes
from app.services.divination.api import analysis_routes
from app.services.divination.api import knowledge_routes
from app.services.divination.api import report_routes
from app.services.divination.api import specialized_routes

# Register sub-module blueprints
divination_bp.register_blueprint(chart_routes.chart_bp)
divination_bp.register_blueprint(analysis_routes.analysis_bp)
divination_bp.register_blueprint(report_routes.report_bp)
divination_bp.register_blueprint(specialized_routes.specialized_bp)
knowledge_bp.register_blueprint(knowledge_routes.knowledge_routes_bp)

__all__ = ['divination_bp', 'knowledge_bp', '_to_dict', 'validate_birth_info', 'DATA_BASE_PATH']
