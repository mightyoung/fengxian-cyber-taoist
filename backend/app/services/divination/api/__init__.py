"""
Divination API Module - 紫微斗数API模块

提供命盘生成和分析的REST API接口。
"""

import os
from typing import Dict, Any, Optional
from flask import Blueprint

# 数据文件路径常量
DATA_BASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    '..',
    'data_source', 'mlx', 'data'
)

# Create blueprints
divination_bp = Blueprint('divination', __name__, url_prefix='/api/divination')
knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/divination/knowledge')


def _to_dict(obj: Any) -> Any:
    """Convert object to dict for JSON serialization"""
    from enum import Enum
    if isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_to_dict(item) for item in obj]
    elif isinstance(obj, object) and hasattr(obj, '__dataclass_fields__'):
        from dataclasses import asdict
        result = {}
        for k, v in asdict(obj).items():
            result[k] = _to_dict(v)
        return result
    else:
        return obj


def _format_transform_explanation(chart_data: Dict, transform_dict: Dict) -> str:
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


def _format_palace_overview(chart_data: Dict, palace_dict: Dict) -> str:
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


def validate_birth_info(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    验证出生信息

    Returns:
        (is_valid, error_message)
    """
    required_fields = ['year', 'month', 'day', 'hour', 'gender']

    for field in required_fields:
        if field not in data:
            return False, f"缺少必需字段: {field}"

    year = data.get('year')
    if not isinstance(year, int) or not (1900 <= year <= 2100):
        return False, "年份必须在1900-2100之间"

    month = data.get('month')
    if not isinstance(month, int) or not (1 <= month <= 12):
        return False, "月份必须在1-12之间"

    day = data.get('day')
    if not isinstance(day, int) or not (1 <= day <= 31):
        return False, "日期必须在1-31之间"

    hour = data.get('hour')
    if not isinstance(hour, int) or not (0 <= hour <= 23):
        return False, "小时必须在0-23之间"

    gender = data.get('gender')
    if gender not in ['male', 'female']:
        return False, "性别必须是 'male' 或 'female'"

    minute = data.get('minute', 0)
    if not isinstance(minute, int) or not (0 <= minute <= 59):
        return False, "分钟必须在0-59之间"

    return True, None


# Import route modules to register blueprints
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

__all__ = ['divination_bp', 'knowledge_bp']
