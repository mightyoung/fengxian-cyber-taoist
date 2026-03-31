"""
Common utilities for divination API routes - 共享工具函数
"""

import os
from enum import Enum
from typing import Any


# 数据文件路径常量
DATA_BASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
    '..',
    'data_source', 'mlx', 'data'
)


def _to_dict(obj: Any) -> Any:
    """Convert object to dict for JSON serialization"""
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


def validate_birth_info(data):
    """验证出生信息"""
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
