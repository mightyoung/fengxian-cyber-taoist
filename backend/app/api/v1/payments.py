"""
Payment Routes - 支付API路由

提供Stripe和微信支付的订阅、支付接口。
"""

import time
from flask import Blueprint, request, jsonify, g
from app.services.auth import require_auth
from app.services.payment import StripeService, WeChatPayService, SUBSCRIPTION_PRICES

# Create blueprint
payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


@payments_bp.route('/checkout', methods=['POST'])
@require_auth
def create_checkout():
    """
    创建Stripe Checkout Session

    Request Body:
        {
            "price_key": "pro_monthly",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/pricing"
        }

    Returns:
        {
            "success": true,
            "data": {
                "checkout_url": "..."
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        price_key = data.get('price_key')
        success_url = data.get('success_url', 'https://example.com/success?session_id={CHECKOUT_SESSION_ID}')
        cancel_url = data.get('cancel_url', 'https://example.com/pricing')

        if price_key not in SUBSCRIPTION_PRICES:
            return jsonify({"success": False, "error": f"未知的价格方案: {price_key}"}), 400

        # 获取用户信息
        from app.models.user import UserManager
        user = UserManager.get_user(g.current_user_id)
        if not user:
            return jsonify({"success": False, "error": "用户不存在"}), 404

        # 获取或创建Stripe客户
        subscription = UserManager.get_subscription(g.current_user_id)
        if subscription.stripe_customer_id:
            customer_id = subscription.stripe_customer_id
        else:
            # 创建Stripe客户
            customer_id = StripeService.create_customer(
                email=user.email,
                name=user.nickname or user.email,
                metadata={"user_id": user.id},
            )
            # 保存客户ID
            subscription.stripe_customer_id = customer_id
            UserManager.save_subscription(subscription)

        # 创建Checkout Session
        session_id, checkout_url = StripeService.create_checkout_session(
            customer_id=customer_id,
            price_key=price_key,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "user_email": user.email,
                "price_key": price_key,
            },
        )

        return jsonify({
            "success": True,
            "data": {
                "session_id": session_id,
                "checkout_url": checkout_url,
            }
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"创建Checkout失败: {str(e)}"}), 500


@payments_bp.route('/wechat/qr', methods=['POST'])
@require_auth
def create_wechat_qr():
    """
    创建微信支付二维码

    Request Body:
        {
            "price_key": "pro_monthly",
            "description": "Pro月度订阅"
        }

    Returns:
        {
            "success": true,
            "data": {
                "qr_code_url": "weixin://wxpay/bizpayurl?..."
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        price_key = data.get('price_key')
        description = data.get('description', '订阅服务')

        price_info = SUBSCRIPTION_PRICES.get(price_key)
        if not price_info:
            return jsonify({"success": False, "error": f"未知的价格方案: {price_key}"}), 400

        # 获取用户信息
        from app.models.user import UserManager
        user = UserManager.get_user(g.current_user_id)
        if not user:
            return jsonify({"success": False, "error": "用户不存在"}), 404

        # 创建微信订单
        order_result = WeChatPayService.create_native_order(
            description=description,
            amount=price_info.amount,
            out_trade_no=f"wx_{user.id}_{int(time.time())}",
            metadata={
                "user_id": user.id,
                "price_key": price_key,
            },
        )

        return jsonify({
            "success": True,
            "data": {
                "prepay_id": order_result.prepay_id,
                "order_id": order_result.order_id,
                "qr_code_url": order_result.qr_code_url,
            }
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"创建微信订单失败: {str(e)}"}), 500


@payments_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Stripe Webhook回调

    注意：生产环境需要验证签名
    """
    try:
        payload = request.data
        signature = request.headers.get('Stripe-Signature', '')

        event = StripeService.construct_webhook_event(payload, signature)
        if not event:
            return jsonify({"success": False, "error": "Invalid webhook"}), 400

        # 处理事件
        event_type = StripeService.handle_webhook_event(event)

        return jsonify({
            "success": True,
            "data": {"event_type": event_type}
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@payments_bp.route('/webhook/wechat', methods=['POST'])
def wechat_webhook():
    """
    微信支付回调

    微信支付完成后会调用此接口通知
    """
    try:
        payload = request.data.decode('utf-8')

        # 解析回调数据
        result = WeChatPayService.parse_notify_response(payload)

        if result.get('return_code') == 'SUCCESS':
            # 获取附加数据
            attach = result.get('attach', '')
            metadata = {}
            if attach:
                for item in attach.split('&'):
                    if '=' in item:
                        k, v = item.split('=', 1)
                        metadata[k] = v

            # 处理支付成功逻辑
            user_id = metadata.get('user_id')
            price_key = metadata.get('price_key')

            if user_id and price_key:
                from app.models.user import UserManager
                UserManager.upgrade_subscription(
                    user_id=user_id,
                    tier=price_key_to_tier(price_key),
                    payment_method="wechat",
                    payment_id=result.get('transaction_id'),
                )

            return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
        else:
            return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[FAIL]]></return_msg></xml>'

    except Exception as e:
        return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[{}]]></return_msg></xml>'.format(str(e))


@payments_bp.route('/history', methods=['GET'])
@require_auth
def get_payment_history():
    """
    获取支付历史

    Returns:
        {
            "success": true,
            "data": {
                "payments": [...]
            }
        }
    """
    try:
        # TODO: 实现支付历史查询
        # 目前返回空列表
        payments = []

        return jsonify({
            "success": True,
            "data": {
                "payments": payments
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"获取支付历史失败: {str(e)}"}), 500


@payments_bp.route('/cancel', methods=['POST'])
@require_auth
def cancel_subscription():
    """
    取消订阅

    Request Body:
        {
            "cancel_at_period_end": true  // 是否在周期结束时取消
        }

    Returns:
        {
            "success": true,
            "data": {
                "message": "订阅已取消"
            }
        }
    """
    try:
        data = request.get_json() or {}
        cancel_at_period_end = data.get('cancel_at_period_end', True)

        from app.models.user import UserManager
        subscription = UserManager.get_subscription(g.current_user_id)

        if subscription.stripe_subscription_id:
            success = StripeService.cancel_subscription(
                subscription.stripe_subscription_id,
                at_period_end=cancel_at_period_end,
            )
            if not success:
                return jsonify({"success": False, "error": "取消订阅失败"}), 500
        elif subscription.wechat_prepay_id:
            # 微信订阅暂时不支持主动取消
            return jsonify({"success": False, "error": "微信订阅请联系客服取消"}), 400
        else:
            # 免费用户直接降级
            subscription.tier = "free"
            UserManager.save_subscription(subscription)

        return jsonify({
            "success": True,
            "data": {
                "message": "订阅已取消" if cancel_at_period_end else "订阅已立即取消"
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"取消订阅失败: {str(e)}"}), 500


@payments_bp.route('/upgrade', methods=['POST'])
@require_auth
def upgrade_subscription():
    """
    升级/变更订阅

    Request Body:
        {
            "price_key": "pro_monthly"
        }

    Returns:
        {
            "success": true,
            "data": {
                "message": "订阅已更新"
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体必须是JSON格式"}), 400

        price_key = data.get('price_key')
        if price_key not in SUBSCRIPTION_PRICES:
            return jsonify({"success": False, "error": f"未知的价格方案: {price_key}"}), 400

        from app.models.user import UserManager
        subscription = UserManager.get_subscription(g.current_user_id)

        if subscription.stripe_subscription_id:
            # Stripe订阅变更
            new_subscription_id = StripeService.update_subscription_tier(
                subscription.stripe_subscription_id,
                price_key,
            )
            if new_subscription_id:
                subscription.stripe_subscription_id = new_subscription_id
                UserManager.save_subscription(subscription)
        else:
            # 直接升级
            tier = price_key_to_tier(price_key)
            subscription.tier = tier
            UserManager.save_subscription(subscription)

        return jsonify({
            "success": True,
            "data": {
                "message": "订阅已更新",
                "tier": price_key_to_tier(price_key),
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"升级订阅失败: {str(e)}"}), 500


def price_key_to_tier(price_key: str) -> str:
    """将price_key转换为tier"""
    if 'premium' in price_key:
        return 'premium'
    elif 'pro' in price_key:
        return 'pro'
    return 'free'
