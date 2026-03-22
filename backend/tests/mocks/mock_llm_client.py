"""
Mock LLM Client - 用于测试的模拟LLM客户端

提供可控的响应，用于单元测试，避免依赖真实LLM API。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class MockLLMResponse:
    """模拟LLM响应"""
    content: str
    usage: Dict[str, int] = field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0})
    model: str = "mock-model"
    finish_reason: str = "stop"


class MockLLMClient:
    """
    Mock LLM客户端，用于测试

    支持:
    - 预定义响应映射
    - 调用计数
    - 响应模板
    """

    def __init__(
        self,
        responses: Optional[Dict[str, str]] = None,
        default_response: str = "Mock response",
        raise_on_call: bool = False,
    ):
        """
        初始化Mock LLM客户端

        Args:
            responses: 预定义的响应映射 {prompt_key: response}
            default_response: 默认响应（当没有匹配到预定义响应时）
            raise_on_call: 是否在调用时抛出异常（用于测试错误处理）
        """
        self.responses = responses or {}
        self.default_response = default_response
        self.raise_on_call = raise_on_call
        self.call_count = 0
        self.call_history: List[Dict[str, Any]] = []

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs
    ) -> MockLLMResponse:
        """
        模拟chat调用

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            MockLLMResponse: 模拟的响应
        """
        self.call_count += 1

        if self.raise_on_call:
            raise RuntimeError("Mock LLM error for testing")

        # 提取最后一条用户消息
        prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                prompt = msg.get("content", "")
                break

        # 记录调用历史
        self.call_history.append({
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "kwargs": kwargs,
        })

        # 查找预定义的响应
        response_content = self.default_response
        for key, response in self.responses.items():
            if key in prompt:
                response_content = response
                break

        return MockLLMResponse(
            content=response_content,
            usage={"prompt_tokens": len(prompt) // 4, "completion_tokens": len(response_content) // 4},
        )

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        模拟chat_json调用，返回解析后的JSON

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            解析后的JSON对象
        """
        response = self.chat(messages, temperature, max_tokens, **kwargs)

        # 尝试解析JSON
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # 如果不是有效JSON，返回包装的对象
            return {"content": response.content, "parsed": False}

    def reset(self):
        """重置调用计数和历史"""
        self.call_count = 0
        self.call_history.clear()


class AsyncMockLLMClient:
    """
    异步Mock LLM客户端

    与MockLLMClient接口相同，但返回协程。
    """

    def __init__(
        self,
        responses: Optional[Dict[str, str]] = None,
        default_response: str = "Mock response",
        raise_on_call: bool = False,
    ):
        self._sync_client = MockLLMClient(responses, default_response, raise_on_call)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs
    ) -> MockLLMResponse:
        """异步chat调用"""
        return self._sync_client.chat(messages, temperature, max_tokens, **kwargs)

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """异步chat_json调用"""
        return self._sync_client.chat_json(messages, temperature, max_tokens, **kwargs)

    @property
    def call_count(self) -> int:
        return self._sync_client.call_count

    @property
    def call_history(self) -> List[Dict[str, Any]]:
        return self._sync_client.call_history

    def reset(self):
        self._sync_client.reset()


# 预定义的测试响应模板
# 注意：以下数据仅用于单元测试，不是真实API响应
CHART_RESPONSE_TEMPLATE = json.dumps({
    "palaces": {
        "命宫": {"stars": [{"name": "紫微", "type": "主星"}], "branch": "寅", "tiangan": "甲"},
        "兄弟宫": {"stars": [], "branch": "卯", "tiangan": "乙"},
        "夫妻宫": {"stars": [{"name": "天同"}], "branch": "辰", "tiangan": "丙"},
    },
    "birth_info": {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "gender": "male",
    }
})

PATTERN_RESPONSE_TEMPLATE = json.dumps({
    "matched_patterns": [
        {
            "name": "紫府同宫格",
            "category": "吉格",
            "quality": "A",
            "description": "紫微天府同宫于命宫",
        }
    ],
    "interpretation": "格局良好，主富贵"
})

CAUSAL_CHAIN_RESPONSE_TEMPLATE = json.dumps({
    "chains": [
        {
            "cause": "化禄在财帛宫",
            "effect": "忌在迁移宫",
            "interpretation": "得而复失"
        }
    ],
    "忌数": 2
})
