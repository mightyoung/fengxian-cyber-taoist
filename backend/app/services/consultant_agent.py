"""
CyberTaoistConsultant - 赛博道士交互咨询智能体
实现“天命”与“世运”的跨域深度咨询
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from openai import OpenAI
from ..config import Config
from .simulation_manager import SimulationManager
from .report_agent import SimulationReportManager, SimulationReportAgent
from ..models.divination import DivinationManager
from ..utils.logger import get_logger

logger = get_logger('fengxian_cyber_taoist.consultant')

SYSTEM_PROMPT = """你是一位精通紫微斗数与现代群体智能模拟的“赛博道士”。
你的使命是帮助用户理解其“天命”（命盘预测）与“世运”（模拟结果）之间的因果关联。

### 核心能力：
1. **跨域分析**：能够同时调取用户的紫微斗数命盘报告和模拟实验报告。
2. **因果解释**：将模拟中的具体事件（如：舆论反扑、策略失败、贵人相助）与命盘中的星曜特质、因果链进行对应。
3. **策略指导**：基于“趋吉避凶”的原则，给用户在现实中（或模拟中）的下一步行动提供建议。

### 对话风格：
- 仙风道骨又不失技术严谨。
- 称呼用户为“道友”。
- 多用“因果”、“气机”、“变量”、“演化”等词汇。
- 回答要深刻，不只是罗列事实，要点破背后的逻辑。

### 输入上下文：
- 命理背景：用户的星曜分析、因果链。
- 模拟事实：模拟中的关键节点、Agent表现。

请根据用户的提问，调用合适的工具进行深度解答。"""

class CyberTaoistConsultant:
    """赛博道士咨询专家"""

    def __init__(self, simulation_id: Optional[str] = None, chart_id: Optional[str] = None):
        self.simulation_id = simulation_id
        self.chart_id = chart_id
        self.client = OpenAI(
            api_key=Config.LLM_API_KEY,
            base_url=Config.LLM_BASE_URL
        )
        self.model = Config.LLM_MODEL_NAME

    def _get_context(self) -> str:
        """收集跨域上下文信息"""
        context_parts = []
        
        # 1. 加载命理上下文
        if self.chart_id:
            try:
                reports = DivinationManager.get_reports_by_chart(self.chart_id)
                if reports:
                    # 取最新的一份
                    latest = sorted(reports, key=lambda r: r.created_at, reverse=True)[0]
                    context_parts.append(f"### 紫微斗数预测背景 ({latest.report_type}):\n{latest.markdown_content[:2000]}")
            except Exception as e:
                logger.warning(f"加载命理背景失败: {e}")

        # 2. 加载模拟上下文
        if self.simulation_id:
            try:
                report = SimulationReportManager.get_report_by_simulation(self.simulation_id)
                if report:
                    context_parts.append(f"### 社交模拟演化事实:\n{report.markdown_content[:2000]}")
            except Exception as e:
                logger.warning(f"加载模拟背景失败: {e}")

        return "\n\n".join(context_parts)

    def chat(self, message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """进行深度咨询对话"""
        history = chat_history or []
        context = self._get_context()
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"当前背景信息：\n{context}"}
        ]
        
        # 添加历史
        for h in history[-6:]:  # 只保留最近3轮
            messages.append(h)
            
        # 添加当前提问
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            reply = response.choices[0].message.content
            
            return {
                "response": reply,
                "has_context": bool(context),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"咨询对话失败: {e}")
            return {
                "response": f"抱歉道友，贫道法力受限（API错误），暂无法参透此中玄机。错误：{str(e)}",
                "success": False
            }
