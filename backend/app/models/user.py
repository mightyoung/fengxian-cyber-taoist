"""
User Model - 用户模型

提供用户注册、登录、密码哈希等基本功能。
存储方案: 通过 StorageAdapter 接口（当前为 JSON 文件）。
如需切换数据库，实现 StorageAdapter 接口即可。
"""

import uuid
import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


class SubscriptionTier(str):
    """订阅等级枚举"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionStatus(str):
    """订阅状态枚举"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class User:
    """用户数据模型"""
    id: str
    email: str
    password_hash: str
    phone: Optional[str] = None
    wechat_openid: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""
    last_login_at: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含密码哈希）"""
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "wechat_openid": self.wechat_openid,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login_at": self.last_login_at,
        }

    def to_dict_with_password(self) -> Dict[str, Any]:
        """转换为字典（包含密码哈希，仅内部使用）"""
        data = self.to_dict()
        data["password_hash"] = self.password_hash
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """从字典创建"""
        return cls(
            id=data["id"],
            email=data["email"],
            password_hash=data["password_hash"],
            phone=data.get("phone"),
            wechat_openid=data.get("wechat_openid"),
            nickname=data.get("nickname"),
            avatar_url=data.get("avatar_url"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            last_login_at=data.get("last_login_at"),
        )


@dataclass
class Subscription:
    """订阅数据模型"""
    id: str
    user_id: str
    tier: str
    status: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    wechat_prepay_id: Optional[str] = None
    starts_at: str = ""
    expires_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.starts_at:
            self.starts_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tier": self.tier,
            "status": self.status,
            "stripe_customer_id": self.stripe_customer_id,
            "stripe_subscription_id": self.stripe_subscription_id,
            "wechat_prepay_id": self.wechat_prepay_id,
            "starts_at": self.starts_at,
            "expires_at": self.expires_at,
            "cancelled_at": self.cancelled_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subscription":
        """从字典创建"""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            tier=data.get("tier", SubscriptionTier.FREE),
            status=data.get("status", SubscriptionStatus.ACTIVE),
            stripe_customer_id=data.get("stripe_customer_id"),
            stripe_subscription_id=data.get("stripe_subscription_id"),
            wechat_prepay_id=data.get("wechat_prepay_id"),
            starts_at=data.get("starts_at", ""),
            expires_at=data.get("expires_at"),
            cancelled_at=data.get("cancelled_at"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


class UserManager:
    """用户管理器"""

    @classmethod
    def _get_storage(cls):
        """获取用户存储适配器"""
        from app.storage.adapter import get_user_storage
        return get_user_storage()

    @classmethod
    def _get_user_file(cls, user_id: str) -> str:
        """获取用户文件键"""
        return f"{user_id}.json"

    @classmethod
    def _get_user_by_email_file(cls, email: str) -> Optional[str]:
        """根据邮箱查找用户ID"""
        storage = cls._get_storage()
        email_lower = email.lower()
        keys = storage.list_keys()

        for key in keys:
            if key.endswith('_subscription.json'):
                continue
            data = storage.load(key)
            if data and data.get('email', '').lower() == email_lower:
                # 从键中提取 user_id: "uuid.json" -> "uuid"
                return key.replace('.json', '')
        return None

    # ==================== 用户管理 ====================

    @classmethod
    def create_user(
        cls,
        email: str,
        password: str,
        phone: Optional[str] = None,
        nickname: Optional[str] = None,
    ) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        existing_id = cls._get_user_by_email_file(email)
        if existing_id:
            raise ValueError(f"邮箱 {email} 已被注册")

        user_id = str(uuid.uuid4())
        password_hash = cls.hash_password(password)

        user = User(
            id=user_id,
            email=email.lower(),
            password_hash=password_hash,
            phone=phone,
            nickname=nickname or email.split('@')[0],
        )

        cls.save_user(user)
        return user

    @classmethod
    def save_user(cls, user: User) -> None:
        """保存用户"""
        storage = cls._get_storage()
        user.updated_at = datetime.now().isoformat()
        storage.save(cls._get_user_file(user.id), user.to_dict_with_password())

    @classmethod
    def get_user(cls, user_id: str) -> Optional[User]:
        """获取用户"""
        storage = cls._get_storage()
        data = storage.load(cls._get_user_file(user_id))
        if data is None:
            return None
        return User.from_dict(data)

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        user_id = cls._get_user_by_email_file(email)
        if user_id:
            return cls.get_user(user_id)
        return None

    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional[User]:
        """验证用户登录"""
        user = cls.get_user_by_email(email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not cls.verify_password(password, user.password_hash):
            return None

        # 更新最后登录时间
        user.last_login_at = datetime.now().isoformat()
        cls.save_user(user)
        return user

    @classmethod
    def update_user(cls, user_id: str, **kwargs) -> Optional[User]:
        """更新用户信息"""
        user = cls.get_user(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ('id', 'password_hash'):
                setattr(user, key, value)

        cls.save_user(user)
        return user

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        """删除用户"""
        storage = cls._get_storage()
        deleted = storage.delete(user_id)
        # 同时删除订阅文件
        subscription_key = f"{user_id}_subscription.json"
        storage.delete(subscription_key)
        return deleted

    # ==================== 密码管理 ====================

    @classmethod
    def hash_password(cls, password: str) -> str:
        """哈希密码"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False

    @classmethod
    def change_password(cls, user_id: str, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = cls.get_user(user_id)
        if not user:
            return False
        if not cls.verify_password(old_password, user.password_hash):
            return False

        user.password_hash = cls.hash_password(new_password)
        cls.save_user(user)
        return True

    # ==================== 订阅管理 ====================

    @classmethod
    def get_subscription(cls, user_id: str) -> Subscription:
        """获取用户订阅信息"""
        storage = cls._get_storage()
        sub_key = f"{user_id}_subscription.json"
        data = storage.load(sub_key)
        if data is not None:
            return Subscription.from_dict(data)

        # 返回默认免费订阅
        return Subscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            tier=SubscriptionTier.FREE,
            status=SubscriptionStatus.ACTIVE,
        )

    @classmethod
    def save_subscription(cls, subscription: Subscription) -> None:
        """保存订阅信息"""
        storage = cls._get_storage()
        subscription.updated_at = datetime.now().isoformat()
        sub_key = f"{subscription.user_id}_subscription.json"
        storage.save(sub_key, subscription.to_dict())

    @classmethod
    def upgrade_subscription(
        cls,
        user_id: str,
        tier: str,
        payment_method: str = "stripe",
        payment_id: Optional[str] = None,
    ) -> Subscription:
        """升级订阅"""
        subscription = cls.get_subscription(user_id)
        subscription.tier = tier
        subscription.status = SubscriptionStatus.ACTIVE

        if payment_method == "stripe":
            subscription.stripe_subscription_id = payment_id
        elif payment_method == "wechat":
            subscription.wechat_prepay_id = payment_id

        cls.save_subscription(subscription)
        return subscription
