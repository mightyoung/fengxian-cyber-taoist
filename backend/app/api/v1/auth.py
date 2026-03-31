"""
Auth Routes - 认证API路由

提供用户注册、登录、令牌刷新等认证接口。
"""

from flask import Blueprint, request, jsonify, g
from app.models.user import UserManager
from app.services.auth import JWTAuth, require_auth

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册

    Request Body:
        {
            "email": "user@example.com",
            "password": "password123",
            "phone": "13800138000",  // optional
            "nickname": "用户名"  // optional
        }

    Returns:
        {
            "success": true,
            "data": {
                "user_id": "...",
                "email": "...",
                "access_token": "...",
                "refresh_token": "..."
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '')
        phone = data.get('phone')
        nickname = data.get('nickname')

        # 验证必填字段
        if not email:
            return jsonify({"success": False, "error": "邮箱不能为空"}), 400
        if not password:
            return jsonify({"success": False, "error": "密码不能为空"}), 400
        if len(password) < 6:
            return jsonify({"success": False, "error": "密码长度至少6位"}), 400

        # 验证邮箱格式
        if '@' not in email:
            return jsonify({"success": False, "error": "邮箱格式不正确"}), 400

        # 创建用户
        try:
            user = UserManager.create_user(
                email=email,
                password=password,
                phone=phone,
                nickname=nickname,
            )
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

        # 生成令牌
        subscription = UserManager.get_subscription(user.id)
        access_token, refresh_token = JWTAuth.generate_token_pair(
            user_id=user.id,
            email=user.email,
            tier=subscription.tier,
        )

        return jsonify({
            "success": True,
            "data": {
                "user_id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "subscription_tier": subscription.tier,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"注册失败: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录

    Request Body:
        {
            "email": "user@example.com",
            "password": "password123"
        }

    Returns:
        {
            "success": true,
            "data": {
                "user_id": "...",
                "email": "...",
                "access_token": "...",
                "refresh_token": "..."
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({"success": False, "error": "邮箱和密码不能为空"}), 400

        # 验证登录
        user = UserManager.authenticate(email, password)
        if not user:
            return jsonify({"success": False, "error": "邮箱或密码错误"}), 401

        # 生成令牌
        subscription = UserManager.get_subscription(user.id)
        access_token, refresh_token = JWTAuth.generate_token_pair(
            user_id=user.id,
            email=user.email,
            tier=subscription.tier,
        )

        return jsonify({
            "success": True,
            "data": {
                "user_id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "subscription_tier": subscription.tier,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"登录失败: {str(e)}"}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    刷新令牌

    Request Body:
        {
            "refresh_token": "..."
        }

    Returns:
        {
            "success": true,
            "data": {
                "access_token": "...",
                "refresh_token": "..."
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        refresh_token = data.get('refresh_token', '')
        if not refresh_token:
            return jsonify({"success": False, "error": "refresh_token不能为空"}), 400

        # 刷新令牌
        tokens = JWTAuth.refresh_access_token(refresh_token)
        if not tokens:
            return jsonify({"success": False, "error": "refresh_token无效或已过期"}), 401

        access_token, new_refresh_token = tokens

        return jsonify({
            "success": True,
            "data": {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"刷新令牌失败: {str(e)}"}), 500


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    获取当前用户信息

    Requires: Authorization: Bearer <access_token>

    Returns:
        {
            "success": true,
            "data": {
                "user_id": "...",
                "email": "...",
                "subscription_tier": "free|pro|premium",
                ...
            }
        }
    """
    try:
        user = UserManager.get_user(g.current_user_id)
        if not user:
            return jsonify({"success": False, "error": "用户不存在"}), 404

        subscription = UserManager.get_subscription(user.id)

        return jsonify({
            "success": True,
            "data": {
                "user_id": user.id,
                "email": user.email,
                "phone": user.phone,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at,
                "subscription_tier": subscription.tier,
                "subscription_status": subscription.status,
                "subscription_expires_at": subscription.expires_at,
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"获取用户信息失败: {str(e)}"}), 500


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """
    修改密码

    Request Body:
        {
            "old_password": "...",
            "new_password": "..."
        }

    Returns:
        {
            "success": true,
            "data": {
                "message": "密码修改成功"
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')

        if not old_password or not new_password:
            return jsonify({"success": False, "error": "旧密码和新密码不能为空"}), 400

        if len(new_password) < 6:
            return jsonify({"success": False, "error": "新密码长度至少6位"}), 400

        success = UserManager.change_password(g.current_user_id, old_password, new_password)
        if not success:
            return jsonify({"success": False, "error": "旧密码不正确"}), 400

        return jsonify({
            "success": True,
            "data": {
                "message": "密码修改成功"
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"修改密码失败: {str(e)}"}), 500


@auth_bp.route('/subscription', methods=['GET'])
@require_auth
def get_subscription():
    """
    获取当前订阅信息

    Returns:
        {
            "success": true,
            "data": {
                "tier": "free|pro|premium",
                "status": "active|cancelled|expired",
                "expires_at": "...",
                ...
            }
        }
    """
    try:
        subscription = UserManager.get_subscription(g.current_user_id)

        return jsonify({
            "success": True,
            "data": subscription.to_dict()
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"获取订阅信息失败: {str(e)}"}), 500
