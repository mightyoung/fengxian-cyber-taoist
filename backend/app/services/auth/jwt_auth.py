"""
JWT Authentication Service - JWT认证服务

提供基于JWT的令牌生成和验证功能。
"""

import os
import jwt
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class TokenPayload:
    """JWT载荷"""
    user_id: str
    email: str
    tier: str  # subscription tier
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp

    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.fromtimestamp(self.exp) < datetime.now()


class JWTAuth:
    """JWT认证服务"""

    # 配置
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    @classmethod
    def generate_access_token(
        cls,
        user_id: str,
        email: str,
        tier: str = "free",
    ) -> str:
        """生成访问令牌"""
        now = datetime.now()
        payload = {
            "user_id": user_id,
            "email": email,
            "tier": tier,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def generate_refresh_token(cls, user_id: str) -> str:
        """生成刷新令牌"""
        now = datetime.now()
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def generate_token_pair(
        cls,
        user_id: str,
        email: str,
        tier: str = "free",
    ) -> Tuple[str, str]:
        """生成令牌对（access + refresh）"""
        access_token = cls.generate_access_token(user_id, email, tier)
        refresh_token = cls.generate_refresh_token(user_id)
        return access_token, refresh_token

    @classmethod
    def verify_token(cls, token: str, token_type: str = "access") -> Optional[TokenPayload]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

            # 检查令牌类型
            if payload.get("type") != token_type:
                return None

            # 检查是否过期（jwt.decode会自动检查，但我们要构造payload对象）
            exp = payload.get("exp", 0)
            if datetime.fromtimestamp(exp) < datetime.now():
                return None

            return TokenPayload(
                user_id=payload["user_id"],
                email=payload.get("email", ""),
                tier=payload.get("tier", "free"),
                exp=exp,
                iat=payload.get("iat", 0),
            )

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Optional[Tuple[str, str]]:
        """使用刷新令牌获取新的访问令牌"""
        payload = cls.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return None

        # 生成新的令牌对
        return cls.generate_token_pair(payload.user_id, payload.email, payload.tier)

    @classmethod
    def decode_token_unsafe(cls, token: str) -> Optional[Dict[str, Any]]:
        """解码令牌（不验证，用于调试）"""
        try:
            return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM], options={"verify_signature": False})
        except Exception:
            return None


def get_token_from_header() -> Optional[str]:
    """从请求头获取令牌"""
    from flask import request
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def require_auth(f):
    """认证装饰器"""
    from functools import wraps
    from flask import jsonify

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({"success": False, "error": "未提供认证令牌"}), 401

        payload = JWTAuth.verify_token(token)
        if not payload:
            return jsonify({"success": False, "error": "令牌无效或已过期"}), 401

        # 将用户信息注入请求上下文
        from flask import g
        g.current_user_id = payload.user_id
        g.current_email = payload.email
        g.current_tier = payload.tier

        return f(*args, **kwargs)

    return decorated


def require_tier(required_tier: str):
    """等级要求装饰器"""
    from functools import wraps
    from flask import jsonify, g

    # tier hierarchy: free < pro < premium
    TIER_HIERARCHY = {
        "free": 0,
        "pro": 1,
        "premium": 2,
    }

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_tier = getattr(g, 'current_tier', 'free')
            user_level = TIER_HIERARCHY.get(user_tier, 0)
            required_level = TIER_HIERARCHY.get(required_tier, 99)

            if user_level < required_level:
                return jsonify({
                    "success": False,
                    "error": f"此功能需要 {required_tier} 会员或更高等级",
                    "required_tier": required_tier,
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
