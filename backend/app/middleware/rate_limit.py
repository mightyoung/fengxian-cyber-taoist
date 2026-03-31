"""
Rate Limiting Middleware - 限流中间件

基于用户等级的API限流。
"""

import os
import json
from datetime import datetime
from functools import wraps
from typing import Dict, Tuple
from flask import jsonify, g


class RateLimiter:
    """限流器"""

    # 存储路径
    QUOTAS_DIR = os.path.join(
        os.path.dirname(__file__), '../../uploads/rate_limits'
    )

    # 各等级配额
    QUOTAS = {
        "free": {
            "charts_per_month": 5,
            "reports_per_month": 5,
            "api_calls_per_day": 100,
        },
        "pro": {
            "charts_per_month": 50,
            "reports_per_month": 50,
            "api_calls_per_day": 1000,
        },
        "premium": {
            "charts_per_month": -1,  # 无限制
            "reports_per_month": -1,
            "api_calls_per_day": -1,
        },
    }

    @classmethod
    def _ensure_dirs(cls):
        """确保目录存在"""
        os.makedirs(cls.QUOTAS_DIR, exist_ok=True)

    @classmethod
    def _get_quota_file(cls, user_id: str, month: str) -> str:
        """获取配额文件路径"""
        return os.path.join(cls.QUOTAS_DIR, f"{user_id}_{month}.json")

    @classmethod
    def get_current_usage(cls, user_id: str, tier: str) -> Dict:
        """获取当前使用量"""
        month = datetime.now().strftime('%Y-%m')
        quota_file = cls._get_quota_file(user_id, month)
        cls._ensure_dirs()

        if os.path.exists(quota_file):
            with open(quota_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "user_id": user_id,
            "month": month,
            "charts_generated": 0,
            "reports_generated": 0,
            "api_calls": 0,
            "last_api_call": None,
        }

    @classmethod
    def increment_usage(cls, user_id: str, resource: str) -> Tuple[bool, Dict]:
        """
        增加使用量

        Returns:
            (is_allowed, current_usage)
        """
        month = datetime.now().strftime('%Y-%m')
        quota_file = cls._get_quota_file(user_id, month)
        cls._ensure_dirs()

        # 获取当前使用量
        usage = cls.get_current_usage(user_id, "")

        # 读取用户等级
        from app.models.user import UserManager
        subscription = UserManager.get_subscription(user_id)
        tier = subscription.tier
        quotas = cls.QUOTAS.get(tier, cls.QUOTAS["free"])

        # 检查配额
        if resource == "chart":
            limit = quotas["charts_per_month"]
            if limit > 0 and usage.get("charts_generated", 0) >= limit:
                return False, usage
            usage["charts_generated"] = usage.get("charts_generated", 0) + 1

        elif resource == "report":
            limit = quotas["reports_per_month"]
            if limit > 0 and usage.get("reports_generated", 0) >= limit:
                return False, usage
            usage["reports_generated"] = usage.get("reports_generated", 0) + 1

        elif resource == "api_call":
            # API调用按天限制，检查是否需要重置
            today = datetime.now().strftime('%Y-%m-%d')
            last_call = usage.get("last_api_call", "")
            if last_call and not last_call.startswith(today):
                usage["api_calls_today"] = 0

            limit = quotas["api_calls_per_day"]
            if limit > 0 and usage.get("api_calls_today", 0) >= limit:
                return False, usage
            usage["api_calls_today"] = usage.get("api_calls_today", 0) + 1

        usage["last_api_call"] = datetime.now().isoformat()

        # 保存
        with open(quota_file, 'w', encoding='utf-8') as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)

        return True, usage

    @classmethod
    def get_remaining_quota(cls, user_id: str, tier: str, resource: str) -> Dict:
        """获取剩余配额"""
        quotas = cls.QUOTAS.get(tier, cls.QUOTAS["free"])
        usage = cls.get_current_usage(user_id, tier)

        if resource == "chart":
            limit = quotas["charts_per_month"]
            used = usage.get("charts_generated", 0)
        elif resource == "report":
            limit = quotas["reports_per_month"]
            used = usage.get("reports_generated", 0)
        else:
            limit = quotas["api_calls_per_day"]
            used = usage.get("api_calls_today", 0)

        if limit < 0:
            return {"remaining": -1, "limit": "unlimited", "used": used}

        return {
            "remaining": max(0, limit - used),
            "limit": limit,
            "used": used,
        }


def rate_limit(resource: str):
    """
    限流装饰器

    Usage:
        @rate_limit("chart")
        def generate_chart():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # 检查是否已登录
            user_id = getattr(g, 'current_user_id', None)
            if not user_id:
                # 未登录用户不允许访问需要限流的资源
                return jsonify({
                    "success": False,
                    "error": "此操作需要登录",
                    "code": "AUTH_REQUIRED",
                }), 401

            # 检查配额
            is_allowed, usage = RateLimiter.increment_usage(user_id, resource)
            if not is_allowed:
                tier = getattr(g, 'current_tier', 'free')
                remaining = RateLimiter.get_remaining_quota(user_id, tier, resource)

                return jsonify({
                    "success": False,
                    "error": f"本月{resource}配额已用完，请升级到更高等级",
                    "code": "QUOTA_EXCEEDED",
                    "quota": remaining,
                }), 429

            return f(*args, **kwargs)
        return decorated
    return decorator


def check_quota(resource: str):
    """
    检查配额装饰器（不消耗配额）

    Usage:
        @check_quota("chart")
        def get_chart_quote():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_id = getattr(g, 'current_user_id', None)
            tier = getattr(g, 'current_tier', 'free')

            if not user_id:
                tier = 'free'

            remaining = RateLimiter.get_remaining_quota(user_id or 'anonymous', tier, resource)

            # 将配额信息注入响应
            result = f(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2:
                response, status_code = result
                if hasattr(response, 'json'):
                    response.json['quota'] = remaining
            return result
        return decorated
    return decorator
