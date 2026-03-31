"""
Cache Decorator - 分析结果缓存装饰器

提供TTL-based缓存机制，用于缓存昂贵的LLM分析结果。
"""

import hashlib
import json
import time
from functools import wraps
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass
from threading import Lock


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    timestamp: float
    ttl: int  # seconds


class AnalysisCache:
    """
    线程安全的分析结果缓存

    使用TTL机制自动过期，支持基于参数哈希的缓存键。
    """

    def __init__(self, default_ttl: int = 3600):  # 默认1小时
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            # 检查是否过期
            if time.time() - entry.timestamp > entry.ttl:
                del self._cache[key]
                return None

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl if ttl is not None else self._default_ttl
            )

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> int:
        """清理过期条目，返回清理数量"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time - entry.timestamp > entry.ttl
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            current_time = time.time()
            total = len(self._cache)
            expired = sum(
                1 for entry in self._cache.values()
                if current_time - entry.timestamp > entry.ttl
            )
            return {
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired
            }


# 全局缓存实例
_global_cache = AnalysisCache(default_ttl=3600)  # 1小时


def get_cache() -> AnalysisCache:
    """获取全局缓存实例"""
    return _global_cache


def generate_cache_key(
    chart_id: str,
    analysis_type: str,
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成缓存键

    Args:
        chart_id: 命盘ID
        analysis_type: 分析类型 (stars, palaces, patterns, etc.)
        params: 其他参数

    Returns:
        缓存键字符串
    """
    key_parts = [chart_id, analysis_type]

    if params:
        # 将参数字典排序后序列化为JSON，确保相同参数产生相同键
        sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
        params_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
        key_parts.append(params_hash)

    return "|".join(key_parts)


def generate_chart_data_cache_key(
    chart_data: Dict[str, Any],
    analysis_type: str,
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    从 chart_data 生成缓存键（不依赖 chart_id）

    Args:
        chart_data: 命盘数据字典
        analysis_type: 分析类型
        params: 其他参数

    Returns:
        缓存键字符串
    """
    # 从 chart_data 中提取关键信息生成稳定的哈希
    birth_info = chart_data.get("birth_info", {})
    key_parts = [
        str(birth_info.get("year", "")),
        str(birth_info.get("month", "")),
        str(birth_info.get("day", "")),
        str(birth_info.get("hour", "")),
        birth_info.get("gender", ""),
        birth_info.get("wuxing_ju", ""),
        analysis_type
    ]

    if params:
        key_parts.append(json.dumps(params, sort_keys=True, ensure_ascii=False))

    # 生成稳定的哈希
    key_string = "|".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
    return f"chart_data|{key_hash}"


def cache_analysis_result(
    ttl: int = 3600,
    key_prefix: str = ""
) -> Callable:
    """
    缓存分析结果的装饰器

    Args:
        ttl: 缓存过期时间（秒），默认3600（1小时）
        key_prefix: 缓存键前缀

    Usage:
        @cache_analysis_result(ttl=1800, key_prefix="stars")
        def analyze_stars(chart_id: str, params: Dict) -> Dict:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 尝试从参数中提取chart_id
            chart_id = kwargs.get('chart_id') or (args[0] if args else 'unknown')
            analysis_type = key_prefix or func.__name__

            # 生成缓存键
            cache_key = generate_cache_key(
                chart_id=chart_id,
                analysis_type=analysis_type,
                params=kwargs if kwargs else None
            )

            # 尝试从缓存获取
            cache = get_cache()
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            # 执行原函数
            result = func(*args, **kwargs)

            # 存入缓存
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result

        # 添加清理方法
        wrapper.clear_cache = get_cache().clear
        wrapper.get_cache_stats = get_cache().get_stats

        return wrapper

    return decorator


def cached_chart_analysis(
    analysis_type: str,
    ttl: int = 1800  # 30分钟，LLM分析结果变化较少
) -> Callable:
    """
    基于 chart_data 的缓存装饰器（不需要 chart_id）

    Args:
        analysis_type: 分析类型 (stars, palaces, patterns, etc.)
        ttl: 缓存过期时间（秒），默认1800（30分钟）

    Usage:
        @cached_chart_analysis("stars", ttl=3600)
        def llm_analyze_stars_sync(chart_data: Dict, question: Optional[str] = None) -> Dict:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 从参数中提取 chart_data（可能在 args[0] 或 kwargs['chart_data']）
            chart_data = kwargs.get('chart_data')
            if chart_data is None and args:
                chart_data = args[0]

            if chart_data is None:
                # 无法提取 chart_data，直接执行
                return func(*args, **kwargs)

            # 生成缓存键
            question = kwargs.get('question')
            params = {"question": question} if question else None
            cache_key = generate_chart_data_cache_key(
                chart_data=chart_data,
                analysis_type=analysis_type,
                params=params
            )

            # 尝试从缓存获取
            cache = get_cache()
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            # 执行原函数
            result = func(*args, **kwargs)

            # 存入缓存
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result

        # 添加清理方法
        wrapper.clear_cache = get_cache().clear
        wrapper.get_cache_stats = get_cache().get_stats
        wrapper.cache_key_prefix = f"chart_data|{analysis_type}"

        return wrapper

    return decorator


def invalidate_chart_cache(chart_id: str) -> int:
    """
    使特定命盘的所有缓存失效

    Args:
        chart_id: 命盘ID

    Returns:
        删除的缓存数量
    """
    cache = get_cache()
    deleted = 0

    # 查找所有与该命盘相关的缓存键
    keys_to_delete = []
    for key in cache._cache.keys():
        if key.startswith(f"{chart_id}|"):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        if cache.delete(key):
            deleted += 1

    return deleted


def cached_llm_analysis(
    analysis_type: str,
    ttl: int = 1800  # 30分钟，LLM分析结果变化较少
) -> Callable:
    """
    LLM分析结果专用的缓存装饰器

    Args:
        analysis_type: 分析类型
        ttl: 缓存过期时间（秒），默认1800（30分钟）

    Usage:
        @cached_llm_analysis("stars", ttl=3600)
        async def analyze_stars(chart_id: str, chart_data: Dict) -> Dict:
            ...
    """
    return cache_analysis_result(ttl=ttl, key_prefix=analysis_type)


# 便捷函数
def clear_all_cache() -> None:
    """清空所有缓存"""
    get_cache().clear()


def get_cache_statistics() -> Dict[str, Any]:
    """获取缓存统计"""
    return get_cache().get_stats()
