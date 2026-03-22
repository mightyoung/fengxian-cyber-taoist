"""
pytest配置文件 - 测试夹具和Mock支持

提供常用的测试fixtures和Mock配置。
"""

import pytest
import sys
import os
from typing import Dict, Any

# 确保backend目录在Python路径中
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


# ============ Mock LLM Fixtures ============


@pytest.fixture
def mock_llm_responses():
    """预定义的LLM响应映射"""
    return {
        "排盘": '{"palaces": {"命宫": {"stars": []}}, "birth_info": {}}',
        "格局": '{"matched_patterns": [], "interpretation": "test"}',
        "因果链": '{"chains": [], "忌数": 0}',
    }


@pytest.fixture
def mock_llm_client(mock_llm_responses):
    """Mock LLM客户端"""
    from tests.mocks.mock_llm_client import MockLLMClient

    return MockLLMClient(
        responses=mock_llm_responses,
        default_response='{"content": "default mock response"}',
    )


@pytest.fixture
def async_mock_llm_client(mock_llm_responses):
    """异步Mock LLM客户端"""
    from tests.mocks.mock_llm_client import AsyncMockLLMClient

    return AsyncMockLLMClient(
        responses=mock_llm_responses,
        default_response='{"content": "default mock response"}',
    )


# ============ Mock Agent Fixtures ============


@pytest.fixture
def mock_chart_agent():
    """Mock ChartAgent"""
    from tests.mocks.mock_agents import MockChartAgent

    return MockChartAgent()


@pytest.fixture
def mock_pattern_agent():
    """Mock PatternAgent"""
    from tests.mocks.mock_agents import MockPatternAgent

    return MockPatternAgent()


@pytest.fixture
def mock_causal_chain_predictor():
    """Mock CausalChainPredictor"""
    from tests.mocks.mock_agents import MockCausalChainPredictor

    return MockCausalChainPredictor()


# ============ Sample Data Fixtures ============


@pytest.fixture
def sample_birth_info():
    """示例出生信息"""
    return {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "minute": 30,
        "gender": "male",
        "birthplace": "北京",
    }


@pytest.fixture
def sample_chart_data() -> Dict[str, Any]:
    """
    完整示例命盘数据

    包含标准格式的命盘，用于测试各Agent。
    """
    return {
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
        ],
    }


@pytest.fixture
def minimal_chart_data() -> Dict[str, Any]:
    """最小命盘数据"""
    return {
        "birth_info": {
            "year": 2000,
            "month": 1,
            "day": 1,
            "hour": 0,
            "gender": "male",
        },
        "palaces": {
            "命宫": {"stars": []},
            "兄弟宫": {"stars": []},
            "夫妻宫": {"stars": []},
            "子女宫": {"stars": []},
            "财帛宫": {"stars": []},
            "疾厄宫": {"stars": []},
            "迁移宫": {"stars": []},
            "仆役宫": {"stars": []},
            "官禄宫": {"stars": []},
            "田宅宫": {"stars": []},
            "福德宫": {"stars": []},
            "父母宫": {"stars": []},
        },
    }


# ============ Utility Fixtures ============


@pytest.fixture
def palace_stars_dict(sample_chart_data: Dict[str, Any]) -> Dict[str, list]:
    """从命盘数据提取宫位星曜字典"""
    result = {}
    for palace_name, palace_data in sample_chart_data.get("palaces", {}).items():
        stars = [s.get("name", "") for s in palace_data.get("stars", [])]
        result[palace_name] = stars
    return result


@pytest.fixture
def mock_llm_client_with_chart(mock_llm_client):
    """带有命盘相关响应的Mock LLM客户端"""
    import json

    mock_llm_client.responses["命宫"] = json.dumps({
        "palaces": {
            "命宫": {"stars": [{"name": "紫微"}]},
        },
        "birth_info": {"year": 1990}
    })
    return mock_llm_client


# ============ Patch Fixtures ============


@pytest.fixture
def patch_llm_client(mock_llm_client):
    """自动patch LLMClient的fixture"""
    import unittest.mock as mock

    with mock.patch("app.utils.llm_client.LLMClient") as MockLLM:
        instance = mock_llm_client
        MockLLM.return_value = instance
        yield MockLLM


@pytest.fixture
def patch_llm_chat(patch_llm_client):
    """自动patch LLMClient.chat方法的fixture"""
    import unittest.mock as mock

    mock_instance = patch_llm_client.return_value
    mock_instance.chat = mock.MagicMock(side_effect=patch_llm_client.return_value.chat)
    return mock_instance
