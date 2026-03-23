"""
LLM Prompts Types - LLM提示词模块数据类型

包含：
- LLMResponse: LLM响应封装

注意：常量定义请使用 llm_prompts_constants 模块
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class LLMResponse:
    """LLM响应封装"""
    content: str
    parsed_json: Optional[Dict[str, Any]] = None
    raw_response: Optional[str] = None
