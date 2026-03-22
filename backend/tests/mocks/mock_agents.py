"""
Mock Agents - 用于测试的模拟智能体

提供可控的Agent行为，用于单元测试。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


# 预定义的测试命盘数据
# 注意：此数据仅用于测试，不是真实命盘数据
SAMPLE_CHART_DATA = {
    "_is_mock_data": True,  # 明确标识为Mock数据
    "_version": "1.0.0",
    "_generated_at": "2024-01-01",
    "_description": "仅用于单元测试，不是真实命盘数据",
    "birth_info": {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "minute": 30,
        "gender": "male",
        "birthplace": "北京",
        "wuxing_ju": "火六局",
        "year_gan": "庚",
    },
    "palaces": {
        "命宫": {
            "name": "命宫",
            "branch": "寅",
            "tiangan": "甲",
            "stars": [
                {"name": "紫微", "type": "主星", "level": "A"},
                {"name": "天机", "type": "主星", "level": "B"},
            ],
        },
        "兄弟宫": {
            "name": "兄弟宫",
            "branch": "卯",
            "tiangan": "乙",
            "stars": [{"name": "左辅", "type": "辅星", "level": "C"}],
        },
        "夫妻宫": {
            "name": "夫妻宫",
            "branch": "辰",
            "tiangan": "丙",
            "stars": [{"name": "天同", "type": "主星", "level": "B"}],
        },
        "子女宫": {
            "name": "子女宫",
            "branch": "巳",
            "tiangan": "丁",
            "stars": [],
        },
        "财帛宫": {
            "name": "财帛宫",
            "branch": "午",
            "tiangan": "戊",
            "stars": [{"name": "贪狼", "type": "主星", "level": "A"}],
        },
        "疾厄宫": {
            "name": "疾厄宫",
            "branch": "未",
            "tiangan": "己",
            "stars": [{"name": "天相", "type": "主星", "level": "B"}],
        },
        "迁移宫": {
            "name": "迁移宫",
            "branch": "申",
            "tiangan": "庚",
            "stars": [],
        },
        "仆役宫": {
            "name": "仆役宫",
            "branch": "酉",
            "tiangan": "辛",
            "stars": [],
        },
        "官禄宫": {
            "name": "官禄宫",
            "branch": "戌",
            "tiangan": "壬",
            "stars": [{"name": "武曲", "type": "主星", "level": "A"}],
        },
        "田宅宫": {
            "name": "田宅宫",
            "branch": "亥",
            "tiangan": "癸",
            "stars": [],
        },
        "福德宫": {
            "name": "福德宫",
            "branch": "子",
            "tiangan": "甲",
            "stars": [],
        },
        "父母宫": {
            "name": "父母宫",
            "branch": "丑",
            "tiangan": "乙",
            "stars": [{"name": "太阳", "type": "主星", "level": "B"}],
        },
    },
    "stars": {
        "main_stars": [
            {"name": "紫微", "palace": "命宫", "level": "A"},
            {"name": "天机", "palace": "命宫", "level": "B"},
            {"name": "天同", "palace": "夫妻宫", "level": "B"},
            {"name": "贪狼", "palace": "财帛宫", "level": "A"},
            {"name": "天相", "palace": "疾厄宫", "level": "B"},
            {"name": "武曲", "palace": "官禄宫", "level": "A"},
            {"name": "太阳", "palace": "父母宫", "level": "B"},
        ],
        "auxiliary_stars": [
            {"name": "左辅", "palace": "兄弟宫", "level": "C"},
        ],
        "sha_stars": [],
        "transform_stars": [],
    },
    "transforms": [
        {"type": "化禄", "star": "贪狼", "palace": "财帛宫"},
        {"type": "化权", "star": "武曲", "palace": "官禄宫"},
        {"type": "化科", "star": "天同", "palace": "夫妻宫"},
        {"type": "化忌", "star": "太阳", "palace": "父母宫"},
    ],
    "chart_timestamp": "2024-01-01T00:00:00Z",
}


class MockChartAgent:
    """
    Mock ChartAgent - 返回预定义的命盘数据

    用于测试，不依赖真实的排盘逻辑。
    """

    def __init__(self, chart_data: Optional[Dict[str, Any]] = None):
        """
        初始化Mock ChartAgent

        Args:
            chart_data: 预定义的命盘数据，如果为None则使用默认数据
        """
        self.chart_data = chart_data or SAMPLE_CHART_DATA
        self.generate_chart_called = False

    async def generate_chart(self, birth_info: Any) -> Dict[str, Any]:
        """
        生成命盘（Mock实现）

        Args:
            birth_info: 出生信息

        Returns:
            预定义的命盘数据
        """
        self.generate_chart_called = True

        # 返回预定义数据，确保包含birth_info
        result = self.chart_data.copy()
        if "birth_info" in result and hasattr(birth_info, "__dict__"):
            # 用传入的birth_info覆盖
            result["birth_info"] = {
                "year": birth_info.year,
                "month": birth_info.month,
                "day": birth_info.day,
                "hour": birth_info.hour,
                "minute": birth_info.minute,
                "gender": birth_info.gender,
                "birthplace": birth_info.birthplace,
            }

        return result

    async def receive(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """接收消息"""
        try:
            birth_info = message.get("birth_info")
            if not birth_info:
                return {"status": "error", "message": "缺少birth_info"}

            chart = await self.generate_chart(birth_info)
            return {"status": "success", "data": chart}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def respond(self, context: Dict[str, Any]) -> str:
        """响应消息"""
        return "Mock chart generated successfully"


class MockPatternAgent:
    """
    Mock PatternAgent - 返回预定义的格局匹配结果

    用于测试，不依赖真实的格局规则匹配。
    """

    def __init__(
        self,
        matched_patterns: Optional[List[Dict[str, Any]]] = None,
        chart_data: Any = None,
    ):
        """
        初始化Mock PatternAgent

        Args:
            matched_patterns: 预定义的匹配格局列表
            chart_data: 命盘数据
        """
        self.chart = chart_data
        self.matched_patterns = matched_patterns or [
            {
                "id": "p001",
                "name": "紫府同宫格",
                "name_en": "Zi Fu Tong Gong",
                "category": "吉格",
                "quality": "A",
                "description": "紫微天府同宫于命宫，主富贵",
                "source": "紫微斗数全书",
                "matched": True,
                "match_details": "紫微天府在命宫",
                "effects": {"事业": "吉", "财运": "吉"},
            },
            {
                "id": "p002",
                "name": "贪狼会照格",
                "name_en": "Tang Lang Hui Zhao",
                "category": "中性格",
                "quality": "B",
                "description": "贪狼与吉星同宫",
                "source": "紫微斗数全书",
                "matched": True,
                "match_details": "贪狼在财帛宫",
                "effects": {"财运": "吉"},
            },
        ]
        self.analyze_patterns_called = False

    def identify_patterns(
        self,
        palace_stars: Dict[str, List[str]],
        year_stem: str = ""
    ) -> List[Dict[str, Any]]:
        """识别格局"""
        self.analyze_patterns_called = True
        return self.matched_patterns

    def analyze_patterns(
        self,
        palace_stars: Dict[str, List[str]],
        year_stem: str = ""
    ) -> Dict[str, Any]:
        """
        分析格局（Mock实现）

        Returns:
            预定义的格局分析结果
        """
        self.analyze_patterns_called = True

        return {
            "year_stem": year_stem,
            "matched_patterns": self.matched_patterns,
            "auspicious_count": len([p for p in self.matched_patterns if p.get("category") == "吉格"]),
            "inauspicious_count": len([p for p in self.matched_patterns if p.get("category") == "凶格"]),
            "neutral_count": len([p for p in self.matched_patterns if p.get("category") == "中性格"]),
            "interpretation": "命中紫府同宫格，主富贵。贪狼会照，财运亨通。",
        }

    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """获取所有格局"""
        return self.matched_patterns


class MockCausalChainPredictor:
    """
    Mock CausalChainPredictor - 返回预定义的因果链分析结果

    用于测试，不依赖真实的因果链推理逻辑。
    """

    def __init__(
        self,
        causal_chains: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        初始化Mock CausalChainPredictor

        Args:
            causal_chains: 预定义的因果链列表
        """
        self.causal_chains = causal_chains or [
            {
                "cause": {
                    "palace": "财帛宫",
                    "transform": "化禄",
                    "star": "贪狼",
                },
                "effect": {
                    "palace": "迁移宫",
                    "transform": "化忌",
                    "star": "太阳",
                },
                "interpretation": "财帛宫化禄，得财机会；忌在迁移宫，出行耗财",
                "type": "禄转忌",
            },
            {
                "cause": {
                    "palace": "官禄宫",
                    "transform": "化权",
                    "star": "武曲",
                },
                "effect": {
                    "palace": "夫妻宫",
                    "transform": "化科",
                    "star": "天同",
                },
                "interpretation": "事业有权，夫妻关系和谐",
                "type": "禄转忌",
            },
        ]
        self.analyze_called = False
        self.total_ji_count = 2  # 总忌数

    def analyze(
        self,
        palace_stars: Dict[str, List[str]],
        transforms: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        分析因果链（Mock实现）

        Args:
            palace_stars: 宫位星曜数据
            transforms: 四化数据

        Returns:
            预定义的因果链分析结果
        """
        self.analyze_called = True

        return {
            "chains": self.causal_chains,
            "忌数": self.total_ji_count,
            "interpretation": f"因果链分析完成，共有{len(self.causal_chains)}条链，总忌数为{self.total_ji_count}",
            "summary": {
                "财帛相关": 1,
                "事业相关": 1,
                "感情相关": 0,
            },
        }

    def get_chains(self) -> List[Dict[str, Any]]:
        """获取因果链"""
        return self.causal_chains


class MockAgentFactory:
    """Mock Agent工厂类"""

    @staticmethod
    def create_chart_agent(chart_data: Optional[Dict[str, Any]] = None) -> MockChartAgent:
        """创建Mock ChartAgent"""
        return MockChartAgent(chart_data)

    @staticmethod
    def create_pattern_agent(
        matched_patterns: Optional[List[Dict[str, Any]]] = None
    ) -> MockPatternAgent:
        """创建Mock PatternAgent"""
        return MockPatternAgent(matched_patterns)

    @staticmethod
    def create_causal_chain_predictor(
        causal_chains: Optional[List[Dict[str, Any]]] = None
    ) -> MockCausalChainPredictor:
        """创建Mock CausalChainPredictor"""
        return MockCausalChainPredictor(causal_chains)
