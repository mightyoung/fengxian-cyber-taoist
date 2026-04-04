"""
NarrativeGenerator - 模拟叙事生成器
将原始Agent动作转化为文学化的叙事总结
"""

import json
from typing import List, Dict, Any, Optional
from ..utils.llm_client import LLMClient
from .simulation_runner import AgentAction, RoundSummary

class SimulationNarrativeGenerator:
    """叙事生成器类"""

    def __init__(self):
        self.llm = LLMClient()

    def generate_round_narrative(self, round_data: RoundSummary) -> str:
        """为单轮模拟生成叙事总结"""
        actions = [a.to_dict() for a in round_data.actions]
        
        # 精简动作信息，节省Token
        simplified_actions = []
        for a in actions:
            # 只保留核心信息
            simplified_actions.append(f"{a['agent_name']} ({a['platform']}): {a['action_type']} {a['action_args'].get('content', '')[:100]}")

        prompt = f"""请将以下社交媒体模拟的原始动作记录，转化为一段流畅、深刻的叙事文学总结。
你要像一位历史学家或社会观察家一样，点破这一轮中发生的核心矛盾、共识或反转。

### 原始动作记录:
{json.dumps(simplified_actions, ensure_ascii=False, indent=2)}

### 要求:
1. 不要罗列动作，要写成连贯的文字。
2. 字数控制在200-400字之间。
3. 语气要带有“赛博”和“因果”感。
4. 明确指出本轮的“关键变量”或“转折点”。
"""
        
        try:
            return self.llm.chat([{"role": "user", "content": prompt}], temperature=0.7)
        except Exception:
            return "气机紊乱，无法生成本轮叙事。"

    def generate_full_story(self, rounds: List[RoundSummary]) -> str:
        """为整个模拟生成完整故事"""
        # 取前中后三段关键轮次
        if not rounds:
            return "模拟尚未开始，尚无故事可说。"
            
        key_rounds = [rounds[0]]
        if len(rounds) > 2:
            key_rounds.append(rounds[len(rounds)//2])
            key_rounds.append(rounds[-1])
            
        round_summaries = []
        for r in key_rounds:
            round_summaries.append(f"第{r.round_num}轮: {len(r.actions)}个动作")

        prompt = f"""请为这次模拟实验撰写一份“赛博郡历史志”。
总共经历了{len(rounds)}轮演化。

### 关键阶段概览:
{chr(10).join(round_summaries)}

### 要求:
1. 宏观总结整个事件的演变逻辑（起因、发酵、高潮、终局）。
2. 评价模拟中展现出的群体心理特质。
3. 给这份历史志起一个具有“赛博道家”风格的标题。
"""
        
        try:
            return self.llm.chat([{"role": "user", "content": prompt}], temperature=0.8)
        except Exception:
            return "史官失职，无法编纂完整志书。"
