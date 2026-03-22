"""
Redis缓存层E2E测试
"""

import pytest
import json
import hashlib
from unittest.mock import MagicMock, patch


class TestRedisCache:
    """Redis缓存测试"""

    def test_make_llm_cache_key(self):
        """测试LLM缓存键生成"""
        from backend.app.utils.redis_cache import RedisCache

        key1 = RedisCache.make_llm_cache_key(
            prompt="Hello world",
            model="gpt-4",
            temperature=0.3
        )
        key2 = RedisCache.make_llm_cache_key(
            prompt="Hello world",
            model="gpt-4",
            temperature=0.3
        )
        key3 = RedisCache.make_llm_cache_key(
            prompt="Hello world",
            model="gpt-4",
            temperature=0.5
        )

        # 相同参数应生成相同的键
        assert key1 == key2
        # 不同参数应生成不同的键
        assert key1 != key3
        # 键应以"llm:response:"为前缀
        assert key1.startswith("llm:response:")

    def test_cache_key_deterministic(self):
        """测试缓存键的确定性"""
        from backend.app.utils.redis_cache import RedisCache

        prompt = "Test prompt with unicode: 中文测试"
        model = "test-model"
        temperature = 0.7

        # 多次调用应生成相同的键
        for _ in range(3):
            key = RedisCache.make_llm_cache_key(prompt, model, temperature)
            assert key.startswith("llm:response:")
            assert len(key) == len("llm:response:") + 64  # SHA256 hex = 64 chars


class TestRedisCacheWithMock:
    """使用Mock的Redis缓存测试"""

    def test_get_set_basic(self):
        """测试基本的get/set操作"""
        with patch('redis.Redis') as mock_redis:
            with patch('redis.ConnectionPool'):
                mock_client = MagicMock()
                mock_redis.return_value = mock_client
                mock_client.ping.return_value = True

                from backend.app.utils.redis_cache import RedisCache
                # 重置单例
                RedisCache._instance = None

                cache = RedisCache()
                cache._client = mock_client
                cache._available = True

                # 测试set
                mock_client.setex.return_value = True
                result = cache.set("test_key", "test_value", ttl=3600)
                assert result is True
                mock_client.setex.assert_called_once_with("test_key", 3600, "test_value")

                # 测试get
                mock_client.get.return_value = "test_value"
                result = cache.get("test_key")
                assert result == "test_value"
                mock_client.get.assert_called_once_with("test_key")

    def test_delete(self):
        """测试delete操作"""
        with patch('redis.Redis') as mock_redis:
            with patch('redis.ConnectionPool'):
                mock_client = MagicMock()
                mock_redis.return_value = mock_client
                mock_client.ping.return_value = True

                from backend.app.utils.redis_cache import RedisCache
                RedisCache._instance = None

                cache = RedisCache()
                cache._client = mock_client
                cache._available = True

                mock_client.delete.return_value = 1
                result = cache.delete("test_key")
                assert result is True
                mock_client.delete.assert_called_once_with("test_key")

    def test_llm_response_caching(self):
        """测试LLM响应缓存"""
        with patch('redis.Redis') as mock_redis:
            with patch('redis.ConnectionPool'):
                mock_client = MagicMock()
                mock_redis.return_value = mock_client
                mock_client.ping.return_value = True

                from backend.app.utils.redis_cache import RedisCache
                RedisCache._instance = None

                cache = RedisCache()
                cache._client = mock_client
                cache._available = True

                prompt = "What is AI?"
                model = "gpt-4"
                response = "AI is artificial intelligence."

                # 测试设置缓存
                mock_client.setex.return_value = True
                result = cache.set_llm_response(prompt, response, model, ttl=86400)
                assert result is True

                # 验证setex被调用，键包含llm:response:前缀
                call_args = mock_client.setex.call_args
                assert call_args[0][0].startswith("llm:response:")

    def test_cache_miss_returns_none(self):
        """测试缓存未命中时返回None"""
        with patch('redis.Redis') as mock_redis:
            with patch('redis.ConnectionPool'):
                mock_client = MagicMock()
                mock_redis.return_value = mock_client
                mock_client.ping.return_value = True

                from backend.app.utils.redis_cache import RedisCache
                RedisCache._instance = None

                cache = RedisCache()
                cache._client = mock_client
                cache._available = True

                mock_client.get.return_value = None
                result = cache.get_llm_response("unknown prompt", "gpt-4")
                assert result is None


class TestRedisFallback:
    """Redis降级测试"""

    def test_graceful_fallback_when_redis_unavailable(self):
        """测试Redis不可用时的优雅降级"""
        with patch('redis.Redis') as mock_redis:
            with patch('redis.ConnectionPool'):
                import redis as real_redis
                mock_redis.return_value.ping.side_effect = real_redis.ConnectionError("Connection refused")

                from backend.app.utils.redis_cache import RedisCache
                RedisCache._instance = None

                cache = RedisCache()

                # 缓存应不可用
                assert cache.is_available is False

                # 所有操作应返回默认值，不抛异常
                assert cache.get("any_key") is None
                assert cache.set("any_key", "any_value") is False
                assert cache.delete("any_key") is False
                assert cache.get_llm_response("prompt", "model") is None
                assert cache.set_llm_response("prompt", "response", "model") is False

    def test_fallback_on_connection_error(self):
        """测试连接错误时的降级"""
        with patch('redis.Redis') as mock_redis:
            with patch('redis.ConnectionPool'):
                mock_client = MagicMock()
                mock_redis.return_value = mock_client
                mock_client.ping.return_value = True
                mock_client.get.side_effect = Exception("Unexpected error")

                from backend.app.utils.redis_cache import RedisCache
                RedisCache._instance = None

                cache = RedisCache()
                cache._client = mock_client
                cache._available = True

                # 发生异常时应捕获并返回None
                result = cache.get("test_key")
                assert result is None


class TestRedisCacheSingleton:
    """单例模式测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        with patch('redis.Redis') as mock_redis:
            with patch('redis.ConnectionPool'):
                mock_client = MagicMock()
                mock_redis.return_value = mock_client
                mock_client.ping.return_value = True

                from backend.app.utils.redis_cache import RedisCache
                RedisCache._instance = None

                cache1 = RedisCache()
                cache2 = RedisCache()

                assert cache1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
