"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
import logging
from typing import Optional, Dict, Any, List

from openai import OpenAI

from ..config import Config

# 获取logger
logger = logging.getLogger(__name__)

# 延迟导入redis_cache避免循环依赖
_redis_cache = None


def _get_cache():
    """延迟获取缓存实例"""
    global _redis_cache
    if _redis_cache is None:
        try:
            from ..utils.redis_cache import get_cache as _get_cache_instance
            _redis_cache = _get_cache_instance()
        except Exception:
            _redis_cache = None
    return _redis_cache


class LLMClient:
    """LLM客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME

        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        cache: bool = True
    ) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（支持 {"type": "json_object"}）
            cache: 是否使用缓存（默认True）

        Returns:
            LLM生成的文本内容
        """
        # 尝试从缓存获取响应
        if cache:
            cache_instance = _get_cache()
            if cache_instance and cache_instance.is_available:
                # 将messages转换为字符串用于缓存键生成
                prompt_text = json.dumps(messages, ensure_ascii=False)
                cached_response = cache_instance.get_llm_response(
                    prompt=prompt_text,
                    model=self.model,
                    temperature=temperature
                )
                if cached_response is not None:
                    return cached_response

        # 构建请求参数
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        # 发送请求
        try:
            response = self.client.chat.completions.create(**kwargs)
        except Exception as e:
            logger.error(f"LLM API调用失败: {e}")
            raise

        # 提取响应内容
        if not response.choices:
            logger.error(f"LLM返回空choices: {response}")
            raise ValueError("LLM返回空响应")

        content = response.choices[0].message.content
        if content is None:
            content = ""
            logger.warning(f"LLM返回None content, choices: {response.choices}")

        # 如果内容为空，记录警告
        if not content.strip():
            logger.warning(f"LLM返回空内容，model={self.model}")

        # 缓存响应
        if cache:
            cache_instance = _get_cache()
            if cache_instance and cache_instance.is_available:
                prompt_text = json.dumps(messages, ensure_ascii=False)
                cache_instance.set_llm_response(
                    prompt=prompt_text,
                    response=content,
                    model=self.model,
                    temperature=temperature
                )

        # 清理thinking tags
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        cache: bool = True
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            cache: 是否使用缓存（默认True）

        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            cache=cache
        )
        # 清理markdown代码块标记
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            # 尝试修复截断的JSON
            fixed_response = self._fix_truncated_json(cleaned_response)
            if fixed_response:
                try:
                    return json.loads(fixed_response)
                except json.JSONDecodeError:
                    pass
            # 提供更详细的错误信息
            error_detail = cleaned_response[:500] if cleaned_response else "(空响应)"
            raise ValueError(f"LLM返回的JSON格式无效: {error_detail}")

    def _fix_truncated_json(self, s: str) -> Optional[str]:
        """
        尝试修复截断的JSON字符串

        使用渐进式修复策略:
        1. 移除尾部逗号
        2. 补全未闭合的括号
        3. 从后向前移除不完整的部分直到JSON有效
        """
        if not s:
            return None

        original = s

        # 策略1: 基本清理 - 移除尾部逗号
        s = re.sub(r',\s*([}\]])', r'\1', s)

        # 策略2: 补全未闭合的括号
        open_braces = s.count('{') - s.count('}')
        open_brackets = s.count('[') - s.count(']')
        s += '}' * max(0, open_braces)
        s += ']' * max(0, open_brackets)

        # 策略3: 渐进式截断直到JSON有效
        # 从后向前逐步移除不完整的部分
        truncate_pos = len(s)

        for i in range(len(s) - 1, -1, -1):
            # 检查当前位置是否可以作为截断点
            prefix = s[:i + 1].strip()
            if not prefix:
                continue

            # 尝试补全括号并解析
            test_s = prefix
            open_b = test_s.count('{') - test_s.count('}')
            open_k = test_s.count('[') - test_s.count(']')
            test_s += '}' * max(0, open_b)
            test_s += ']' * max(0, open_k)

            # 移除尾部逗号
            test_s = re.sub(r',\s*([}\]])', r'\1', test_s)

            try:
                json.loads(test_s)
                # 如果能解析成功，记录这个位置
                truncate_pos = i + 1
                break
            except json.JSONDecodeError:
                continue

        s = s[:truncate_pos].strip()

        # 最终补全括号
        open_braces = s.count('{') - s.count('}')
        open_brackets = s.count('[') - s.count(']')
        s += '}' * max(0, open_braces)
        s += ']' * max(0, open_brackets)

        # 最终清理
        s = re.sub(r',\s*([}\]])', r'\1', s)

        # 如果修复后为空或差异太大，返回None
        if not s or len(s) < len(original) * 0.3:
            return None

        # 验证修复后的JSON
        try:
            json.loads(s)
            return s if s != original else None
        except json.JSONDecodeError:
            return None
