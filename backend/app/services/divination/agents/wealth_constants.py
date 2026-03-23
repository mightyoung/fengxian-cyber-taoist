"""
Wealth Constants - 财运分析常量定义

包含：
- WEALTH_STARS: 财富相关星曜
- PALACE_WEIGHTS: 财富宫位权重

注意：Enums 和 Dataclasses 请使用 wealth_types 模块
"""

from typing import Dict, List


# 财富相关星曜
WEALTH_STARS: Dict[str, List[str]] = {
    "主星": ["紫微", "天府", "武曲", "太阳", "太阴", "贪狼", "巨门", "天梁", "天同", "廉贞"],
    "辅星": ["左辅", "右弼", "天魁", "天钺", "文昌", "文曲", "禄存", "天马"],
    "煞星": ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"],
    "化曜": ["化禄", "化权", "化科", "化忌"]
}

# 财富宫位权重
PALACE_WEIGHTS: Dict[str, float] = {
    "财帛宫": 0.40,
    "田宅宫": 0.25,
    "福德宫": 0.15,
    "官禄宫": 0.20
}
