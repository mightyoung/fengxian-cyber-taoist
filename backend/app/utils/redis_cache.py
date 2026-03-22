"""
Redis缓存层
提供LLM响应缓存功能，支持优雅降级
"""

import json
import hashlib
import logging
from typing import Optional, Any

import redis

from ..config import Config

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis缓存类（单例模式）"""

    _instance: Optional['RedisCache'] = None
    _pool: Optional[redis.ConnectionPool] = None

    def __new__(cls) -> 'RedisCache':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._host = Config.REDIS_HOST
        self._port = Config.REDIS_PORT
        self._db = Config.REDIS_DB
        self._password = Config.REDIS_PASSWORD
        self._available = False
        self._client: Optional[redis.Redis] = None

        self._init_connection()
        self._initialized = True

    def _init_connection(self) -> None:
        """初始化Redis连接池"""
        try:
            self._pool = redis.ConnectionPool(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=True,
                max_connections=10,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            self._client = redis.Redis(connection_pool=self._pool)
            # Test connection
            self._client.ping()
            self._available = True
            logger.info(f"Redis连接成功: {self._host}:{self._port}/{self._db}")
        except redis.ConnectionError as e:
            logger.warning(f"Redis连接失败，降级到无缓存模式: {e}")
            self._available = False
            self._client = None
        except Exception as e:
            logger.warning(f"Redis初始化异常，降级到无缓存模式: {e}")
            self._available = False
            self._client = None

    def _ensure_connection(self) -> bool:
        """确保Redis连接可用"""
        if not self._available or self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except redis.ConnectionError:
            logger.warning("Redis连接已断开，尝试重连")
            self._init_connection()
            return self._available
        except Exception:
            return False

    @property
    def is_available(self) -> bool:
        """检查缓存是否可用"""
        return self._ensure_connection()

    def get(self, key: str) -> Optional[str]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或Redis不可用则返回None
        """
        if not self._ensure_connection():
            return None

        try:
            return self._client.get(key)
        except redis.RedisError as e:
            logger.warning(f"Redis GET失败: {e}")
            return None
        except Exception as e:
            logger.warning(f"缓存获取异常: {e}")
            return None

    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认1小时

        Returns:
            是否设置成功
        """
        if not self._ensure_connection():
            return False

        try:
            self._client.setex(key, ttl, value)
            return True
        except redis.RedisError as e:
            logger.warning(f"Redis SET失败: {e}")
            return False
        except Exception as e:
            logger.warning(f"缓存设置异常: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        if not self._ensure_connection():
            return False

        try:
            self._client.delete(key)
            return True
        except redis.RedisError as e:
            logger.warning(f"Redis DELETE失败: {e}")
            return False
        except Exception as e:
            logger.warning(f"缓存删除异常: {e}")
            return False

    @staticmethod
    def make_llm_cache_key(prompt: str, model: str, temperature: float = 0.3) -> str:
        """
        生成LLM响应的缓存键

        Args:
            prompt: 提示文本
            model: 模型名称
            temperature: 温度参数

        Returns:
            缓存键字符串
        """
        data = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature
        }
        hash_value = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        return f"llm:response:{hash_value}"

    def get_llm_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        获取LLM响应缓存

        Args:
            prompt: 提示文本
            model: 模型名称
            temperature: 温度参数

        Returns:
            缓存的响应，如果不存在则返回None
        """
        key = self.make_llm_cache_key(prompt, model, temperature)
        return self.get(key)

    def set_llm_response(
        self,
        prompt: str,
        response: str,
        model: str,
        temperature: float = 0.3,
        ttl: int = 86400
    ) -> bool:
        """
        缓存LLM响应

        Args:
            prompt: 提示文本
            response: LLM响应
            model: 模型名称
            temperature: 温度参数
            ttl: 过期时间（秒），默认24小时

        Returns:
            是否设置成功
        """
        key = self.make_llm_cache_key(prompt, model, temperature)
        return self.set(key, response, ttl)


# 全局缓存实例
_cache: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """获取缓存单例实例"""
    global _cache
    if _cache is None:
        _cache = RedisCache()
    return _cache
