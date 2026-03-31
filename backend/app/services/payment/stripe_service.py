"""
Stripe Payment Service - Stripe支付服务

提供Stripe支付和订阅集成功能。
"""

import os
import stripe
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class PriceInfo:
    """价格信息"""
    price_id: str
    name: str
    amount: int  # cents
    currency: str
    interval: str  # 'month' or 'year'


# 订阅价格配置
SUBSCRIPTION_PRICES = {
    "pro_monthly": PriceInfo(
        price_id="price_pro_monthly",  # 替换为真实的Stripe Price ID
        name="Pro月度订阅",
        amount=9900,  # 99元
        currency="cny",
        interval="month",
    ),
    "pro_yearly": PriceInfo(
        price_id="price_pro_yearly",
        name="Pro年度订阅",
        amount=99000,  # 990元
        currency="cny",
        interval="year",
    ),
    "premium_monthly": PriceInfo(
        price_id="price_premium_monthly",
        name="Premium月度订阅",
        amount=29900,  # 299元
        currency="cny",
        interval="month",
    ),
    "premium_yearly": PriceInfo(
        price_id="price_premium_yearly",
        name="Premium年度订阅",
        amount=299000,  # 2990元
        currency="cny",
        interval="year",
    ),
}


class StripeService:
    """Stripe支付服务"""

    # 配置
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    STRIPE_API_VERSION = '2023-10-16'

    # 模式
    _test_mode = True

    @classmethod
    def _get_stripe(cls) -> stripe:
        """获取Stripe客户端"""
        if not cls.STRIPE_SECRET_KEY:
            raise ValueError("STRIPE_SECRET_KEY 环境变量未设置")
        return stripe

    @classmethod
    def _configure(cls):
        """配置Stripe"""
        stripe.api_key = cls.STRIPE_SECRET_KEY
        stripe.api_version = cls.STRIPE_API_VERSION

    # ==================== 客户管理 ====================

    @classmethod
    def create_customer(
        cls,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        创建Stripe客户

        Returns:
            customer_id
        """
        cls._configure()
        customer = stripe.Customer.create(
            email=email,
            name=name or "",
            metadata=metadata or {},
        )
        return customer.id

    @classmethod
    def get_customer(cls, customer_id: str) -> Optional[Dict[str, Any]]:
        """获取Stripe客户信息"""
        cls._configure()
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except stripe.error.NotFound:
            return None

    @classmethod
    def delete_customer(cls, customer_id: str) -> bool:
        """删除Stripe客户"""
        cls._configure()
        try:
            stripe.Customer.delete(customer_id)
            return True
        except stripe.error.NotFound:
            return False

    # ==================== Checkout Session ====================

    @classmethod
    def create_checkout_session(
        cls,
        customer_id: str,
        price_key: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str]:
        """
        创建Checkout Session

        Returns:
            (session_id, url)
        """
        cls._configure()

        price_info = SUBSCRIPTION_PRICES.get(price_key)
        if not price_info:
            raise ValueError(f"Unknown price_key: {price_key}")

        # 构建metadata
        session_metadata = metadata or {}
        session_metadata["price_key"] = price_key

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': price_info.currency,
                    'product_data': {
                        'name': price_info.name,
                    },
                    'unit_amount': price_info.amount,
                    'recurring': {
                        'interval': price_info.interval,
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=session_metadata,
            allow_promotion_codes=True,
        )

        return session.id, session.url

    # ==================== Subscription Management ====================

    @classmethod
    def get_subscription(cls, subscription_id: str) -> Optional[Dict[str, Any]]:
        """获取订阅信息"""
        cls._configure()
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.NotFound:
            return None

    @classmethod
    def cancel_subscription(cls, subscription_id: str, at_period_end: bool = True) -> bool:
        """
        取消订阅

        Args:
            subscription_id: Stripe订阅ID
            at_period_end: 是否在当前周期结束时取消（True）还是立即取消（False）
        """
        cls._configure()
        try:
            if at_period_end:
                # 在周期结束时取消
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                # 立即取消
                stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.NotFound:
            return False

    @classmethod
    def reactivate_subscription(cls, subscription_id: str) -> bool:
        """重新激活订阅（取消取消）"""
        cls._configure()
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False,
            )
            return True
        except stripe.error.NotFound:
            return False

    @classmethod
    def update_subscription_tier(
        cls,
        subscription_id: str,
        new_price_key: str,
    ) -> Optional[str]:
        """
        更新订阅等级

        Returns:
            new_subscription_id
        """
        cls._configure()

        price_info = SUBSCRIPTION_PRICES.get(new_price_key)
        if not price_info:
            raise ValueError(f"Unknown price_key: {new_price_key}")

        # 获取当前订阅
        subscription = stripe.Subscription.retrieve(subscription_id)

        # 更新订阅
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': price_info.price_id,
            }],
            proration_behavior='create_prorations',
        )

        return subscription_id

    # ==================== Webhook Handling ====================

    @classmethod
    def construct_webhook_event(
        cls,
        payload: bytes,
        signature: str,
    ) -> Optional[Dict[str, Any]]:
        """
        验证并解析Webhook事件

        Args:
            payload: 请求体
            signature: Stripe-Signature 头

        Returns:
            event dict or None
        """
        cls._configure()

        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                cls.STRIPE_WEBHOOK_SECRET,
            )
            return event
        except ValueError:
            # Invalid payload
            return None
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return None

    @classmethod
    def handle_webhook_event(cls, event: Dict[str, Any]) -> Optional[str]:
        """
        处理Webhook事件

        Returns:
            event_type or None
        """
        event_type = event.get('type')

        if event_type == 'checkout.session.completed':
            # Checkout完成
            session = event['data']['object']
            return cls._handle_checkout_completed(session)

        elif event_type == 'customer.subscription.updated':
            # 订阅更新
            subscription = event['data']['object']
            return cls._handle_subscription_updated(subscription)

        elif event_type == 'customer.subscription.deleted':
            # 订阅取消
            subscription = event['data']['object']
            return cls._handle_subscription_deleted(subscription)

        elif event_type == 'invoice.payment_succeeded':
            # 支付成功
            invoice = event['data']['object']
            return cls._handle_invoice_paid(invoice)

        elif event_type == 'invoice.payment_failed':
            # 支付失败
            invoice = event['data']['object']
            return cls._handle_invoice_failed(invoice)

        return event_type

    @classmethod
    def _handle_checkout_completed(cls, session: Dict[str, Any]) -> str:
        """处理Checkout完成"""
        # 获取session中的信息
        # metadata = session.get('metadata', {})

        # 根据metadata更新用户订阅状态
        # TODO: 实现完整的订阅更新逻辑

        return 'checkout.session.completed'

    @classmethod
    def _handle_subscription_updated(cls, subscription: Dict[str, Any]) -> str:
        """处理订阅更新"""
        return 'customer.subscription.updated'

    @classmethod
    def _handle_subscription_deleted(cls, subscription: Dict[str, Any]) -> str:
        """处理订阅取消"""
        return 'customer.subscription.deleted'

    @classmethod
    def _handle_invoice_paid(cls, invoice: Dict[str, Any]) -> str:
        """处理支付成功"""
        return 'invoice.payment_succeeded'

    @classmethod
    def _handle_invoice_failed(cls, invoice: Dict[str, Any]) -> str:
        """处理支付失败"""
        return 'invoice.payment_failed'

    # ==================== Payment Intent ====================

    @classmethod
    def create_payment_intent(
        cls,
        amount: int,
        currency: str,
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str]:
        """
        创建Payment Intent（用于一次性支付）

        Returns:
            (payment_intent_id, client_secret)
        """
        cls._configure()

        intent_params = {
            'amount': amount,
            'currency': currency,
            'metadata': metadata or {},
        }

        if customer_id:
            intent_params['customer'] = customer_id

        intent = stripe.PaymentIntent.create(**intent_params)

        return intent.id, intent.client_secret

    @classmethod
    def get_payment_intent(cls, payment_intent_id: str) -> Optional[Dict[str, Any]]:
        """获取Payment Intent"""
        cls._configure()
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.NotFound:
            return None
