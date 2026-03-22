"""
E2E Tests for EventPredictorAgent with LLM Integration

这些测试验证事件预测智能体的完整功能，包括规则基础分析和LLM增强分析。
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# 导入测试模块
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.divination.agents.event_predictor_agent import (
    EventPredictorAgent,
    EventPredictionResult,
    EventRiskFactor,
    predict_event_sync,
    LLMEventPredictorAnalyzer,
    llm_analyze_event_predict_sync,
)


# ============ 测试数据 ============

@pytest.fixture
def sample_chart_data() -> Dict[str, Any]:
    """示例命盘数据"""
    return {
        "birth_info": {
            "year": 1990,
            "month": 5,
            "day": 15,
            "birth_hour": 10,
            "gender": "male",
            "wuxing_ju": "水二局"
        },
        "palaces": {
            "命宫": {
                "branch": "子",
                "tiangan": "甲",
                "score": {"total": 75},
                "stars": [
                    {"name": "紫微", "type": "正曜", "level": "旺"},
                    {"name": "天机", "type": "正曜", "level": "平"},
                    {"name": "左辅", "type": "辅星", "level": "旺"},
                    {"name": "右弼", "type": "辅星", "level": "平"}
                ],
                "patterns": []
            },
            "官禄宫": {
                "branch": "寅",
                "tiangan": "丙",
                "score": {"total": 80},
                "stars": [
                    {"name": "太阳", "type": "正曜", "level": "旺"},
                    {"name": "文昌", "type": "辅星", "level": "平"},
                    {"name": "天魁", "type": "辅星", "level": "旺"}
                ],
                "patterns": [{"type": "吉", "name": "日月照殿格"}]
            },
            "财帛宫": {
                "branch": "辰",
                "tiangan": "戊",
                "score": {"total": 70},
                "stars": [
                    {"name": "武曲", "type": "正曜", "level": "旺"},
                    {"name": "化禄", "type": "化曜", "level": "庙"},
                    {"name": "地空", "type": "煞星", "level": "陷"}
                ],
                "patterns": []
            },
            "夫妻宫": {
                "branch": "卯",
                "tiangan": "丁",
                "score": {"total": 60},
                "stars": [
                    {"name": "贪狼", "type": "正曜", "level": "平"},
                    {"name": "陀罗", "type": "煞星", "level": "陷"}
                ],
                "patterns": []
            },
            "迁移宫": {
                "branch": "午",
                "tiangan": "庚",
                "score": {"total": 65},
                "stars": [
                    {"name": "天相", "type": "正曜", "level": "旺"},
                    {"name": "擎羊", "type": "煞星", "level": "陷"}
                ],
                "patterns": []
            },
            "田宅宫": {
                "branch": "酉",
                "tiangan": "癸",
                "score": {"total": 55},
                "stars": [
                    {"name": "天府", "type": "正曜", "level": "平"}
                ],
                "patterns": []
            },
            "福德宫": {
                "branch": "亥",
                "tiangan": "乙",
                "score": {"total": 58},
                "stars": [
                    {"name": "太阴", "type": "正曜", "level": "平"},
                    {"name": "化忌", "type": "化曜", "level": "陷"}
                ],
                "patterns": []
            },
            "兄弟宫": {
                "branch": "丑",
                "tiangan": "乙",
                "score": {"total": 50},
                "stars": [],
                "patterns": []
            },
            "子女宫": {
                "branch": "卯",
                "tiangan": "丁",
                "score": {"total": 50},
                "stars": [],
                "patterns": []
            },
            "疾厄宫": {
                "branch": "巳",
                "tiangan": "己",
                "score": {"total": 50},
                "stars": [],
                "patterns": []
            },
            "仆役宫": {
                "branch": "未",
                "tiangan": "辛",
                "score": {"total": 50},
                "stars": [],
                "patterns": []
            },
            "父母宫": {
                "branch": "戌",
                "tiangan": "甲",
                "score": {"total": 50},
                "stars": [],
                "patterns": []
            }
        },
        "flowing_year": {
            "year": 2025,
            "score": 72,
            "stars": ["太阳", "太阴", "天机"]
        },
        "flowing_month": {
            "month": 3,
            "score": 68
        }
    }


@pytest.fixture
def weak_chart_data() -> Dict[str, Any]:
    """弱势命盘数据（煞星多、空宫多）"""
    return {
        "birth_info": {
            "year": 1985,
            "month": 8,
            "day": 20,
            "birth_hour": 3,
            "gender": "female",
            "wuxing_ju": "火六局"
        },
        "palaces": {
            "命宫": {
                "branch": "子",
                "tiangan": "甲",
                "score": {"total": 40},
                "stars": [
                    {"name": "擎羊", "type": "煞星", "level": "陷"},
                    {"name": "陀罗", "type": "煞星", "level": "陷"},
                    {"name": "火星", "type": "煞星", "level": "陷"}
                ],
                "patterns": [{"type": "凶", "name": "羊陀夹忌格"}]
            },
            "官禄宫": {
                "branch": "寅",
                "tiangan": "丙",
                "score": {"total": 45},
                "stars": [
                    {"name": "地空", "type": "煞星", "level": "陷"},
                    {"name": "地劫", "type": "煞星", "level": "陷"}
                ],
                "patterns": []
            },
            "财帛宫": {
                "branch": "辰",
                "tiangan": "戊",
                "score": {"total": 35},
                "stars": [
                    {"name": "化忌", "type": "化曜", "level": "陷"}
                ],
                "patterns": []
            },
            "夫妻宫": {
                "branch": "卯",
                "tiangan": "丁",
                "score": {"total": 50},
                "stars": [],
                "patterns": []
            },
            "迁移宫": {
                "branch": "午",
                "tiangan": "庚",
                "score": {"total": 48},
                "stars": [],
                "patterns": []
            },
            "田宅宫": {
                "branch": "酉",
                "tiangan": "癸",
                "score": {"total": 42},
                "stars": [],
                "patterns": []
            },
            "福德宫": {
                "branch": "亥",
                "tiangan": "乙",
                "score": {"total": 38},
                "stars": [
                    {"name": "铃星", "type": "煞星", "level": "陷"}
                ],
                "patterns": []
            },
            "兄弟宫": {"branch": "丑", "tiangan": "乙", "score": {"total": 50}, "stars": [], "patterns": []},
            "子女宫": {"branch": "卯", "tiangan": "丁", "score": {"total": 50}, "stars": [], "patterns": []},
            "疾厄宫": {"branch": "巳", "tiangan": "己", "score": {"total": 50}, "stars": [], "patterns": []},
            "仆役宫": {"branch": "未", "tiangan": "辛", "score": {"total": 50}, "stars": [], "patterns": []},
            "父母宫": {"branch": "戌", "tiangan": "甲", "score": {"total": 50}, "stars": [], "patterns": []}
        },
        "flowing_year": {
            "year": 2025,
            "score": 42
        }
    }


@pytest.fixture
def strong_chart_data() -> Dict[str, Any]:
    """强势命盘数据（吉星多、格局好）"""
    return {
        "birth_info": {
            "year": 1995,
            "month": 3,
            "day": 8,
            "birth_hour": 14,
            "gender": "male",
            "wuxing_ju": "金四局"
        },
        "palaces": {
            "命宫": {
                "branch": "寅",
                "tiangan": "丙",
                "score": {"total": 90},
                "stars": [
                    {"name": "紫微", "type": "正曜", "level": "庙"},
                    {"name": "天府", "type": "正曜", "level": "庙"},
                    {"name": "左辅", "type": "辅星", "level": "旺"},
                    {"name": "右弼", "type": "辅星", "level": "旺"},
                    {"name": "天魁", "type": "辅星", "level": "旺"},
                    {"name": "天钺", "type": "辅星", "level": "旺"},
                    {"name": "禄存", "type": "辅星", "level": "旺"},
                    {"name": "天马", "type": "辅星", "level": "旺"}
                ],
                "patterns": [
                    {"type": "吉", "name": "紫府同宫格"},
                    {"type": "吉", "name": "府相朝垣格"}
                ]
            },
            "官禄宫": {
                "branch": "申",
                "tiangan": "壬",
                "score": {"total": 88},
                "stars": [
                    {"name": "太阳", "type": "正曜", "level": "旺"},
                    {"name": "太阴", "type": "正曜", "level": "旺"},
                    {"name": "化禄", "type": "化曜", "level": "庙"},
                    {"name": "化权", "type": "化曜", "level": "旺"},
                    {"name": "化科", "type": "化曜", "level": "旺"}
                ],
                "patterns": [{"type": "吉", "name": "日月照殿格"}]
            },
            "财帛宫": {
                "branch": "辰",
                "tiangan": "戊",
                "score": {"total": 85},
                "stars": [
                    {"name": "武曲", "type": "正曜", "level": "庙"},
                    {"name": "贪狼", "type": "正曜", "level": "旺"},
                    {"name": "文昌", "type": "辅星", "level": "旺"},
                    {"name": "文曲", "type": "辅星", "level": "旺"}
                ],
                "patterns": [{"type": "吉", "name": "贪狼武曲格"}]
            },
            "夫妻宫": {
                "branch": "卯",
                "tiangan": "丁",
                "score": {"total": 80},
                "stars": [
                    {"name": "天同", "type": "正曜", "level": "旺"},
                    {"name": "天梁", "type": "正曜", "level": "旺"},
                    {"name": "天机", "type": "正曜", "level": "平"}
                ],
                "patterns": [{"type": "吉", "name": "机月同梁格"}]
            },
            "迁移宫": {
                "branch": "午",
                "tiangan": "庚",
                "score": {"total": 82},
                "stars": [
                    {"name": "七杀", "type": "正曜", "level": "旺"},
                    {"name": "破军", "type": "正曜", "level": "旺"},
                    {"name": "天相", "type": "正曜", "level": "旺"}
                ],
                "patterns": [{"type": "吉", "name": "杀破狼格"}]
            },
            "田宅宫": {"branch": "酉", "tiangan": "癸", "score": {"total": 80}, "stars": [], "patterns": []},
            "福德宫": {"branch": "亥", "tiangan": "乙", "score": {"total": 78}, "stars": [], "patterns": []},
            "兄弟宫": {"branch": "丑", "tiangan": "乙", "score": {"total": 75}, "stars": [], "patterns": []},
            "子女宫": {"branch": "卯", "tiangan": "丁", "score": {"total": 75}, "stars": [], "patterns": []},
            "疾厄宫": {"branch": "巳", "tiangan": "己", "score": {"total": 70}, "stars": [], "patterns": []},
            "仆役宫": {"branch": "未", "tiangan": "辛", "score": {"total": 72}, "stars": [], "patterns": []},
            "父母宫": {"branch": "戌", "tiangan": "甲", "score": {"total": 75}, "stars": [], "patterns": []}
        },
        "flowing_year": {
            "year": 2025,
            "score": 85
        },
        "flowing_month": {
            "month": 5,
            "score": 80
        }
    }


# ============ Test Cases ============

class TestEventPredictorAgent:
    """事件预测智能体基础功能测试"""

    def test_predict_job_change_success(self, sample_chart_data):
        """测试跳槽预测 - 成功率较高"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="跳槽",
            target_year=2025,
            target_month=3
        )

        assert isinstance(result, EventPredictionResult)
        assert result.event_type == "跳槽"
        assert result.target_palace == "官禄宫"
        assert 0 <= result.success_rate <= 100
        assert 0 <= result.timing_score <= 100
        assert 0 <= result.confidence <= 1
        assert result.level in ["极佳", "良好", "中等", "一般", "较差"]

    def test_predict_career_promotion(self, sample_chart_data):
        """测试晋升预测"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="晋升"
        )

        assert result.target_palace == "官禄宫"
        assert isinstance(result.risk_factors, list)
        assert isinstance(result.opportunity_factors, list)

    def test_predict_investment_wealth(self, sample_chart_data):
        """测试投资理财预测"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="投资理财"
        )

        assert result.target_palace == "财帛宫"
        # 检查化禄因素的影响
        assert len(result.opportunity_factors) >= 0

    def test_predict_marriage_relationship(self, sample_chart_data):
        """测试结婚嫁娶预测"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="结婚嫁娶"
        )

        assert result.target_palace == "夫妻宫"

    def test_predict_weak_chart_career(self, weak_chart_data):
        """测试弱势命盘的事业预测 - 成功率较低"""
        result = predict_event_sync(
            chart=weak_chart_data,
            event_type="求职面试",
            target_year=2025
        )

        assert result.target_palace == "官禄宫"
        # 弱势命盘应该有风险因素
        assert len(result.risk_factors) >= 1
        # 成功率应该相对较低
        assert result.success_rate < 70

    def test_predict_strong_chart_career(self, strong_chart_data):
        """测试强势命盘的事业预测 - 成功率高"""
        result = predict_event_sync(
            chart=strong_chart_data,
            event_type="创业",
            target_year=2025
        )

        assert result.target_palace == "官禄宫"
        # 强势命盘应该有机遇因素
        assert len(result.opportunity_factors) >= 1
        # 成功率应该较高
        assert result.success_rate >= 70

    def test_predict_travel_exam(self, sample_chart_data):
        """测试考试升学预测"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="考试升学"
        )

        assert result.target_palace == "迁移宫"

    def test_predict_house_moving(self, sample_chart_data):
        """测试搬家乔迁预测"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="搬家乔迁"
        )

        assert result.target_palace == "田宅宫"

    def test_result_to_dict(self, sample_chart_data):
        """测试结果序列化"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="跳槽"
        )

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "service_type" in result_dict
        assert result_dict["service_type"] == "event_prediction"
        assert "event_type" in result_dict
        assert "success_rate" in result_dict

    def test_risk_factor_structure(self, sample_chart_data):
        """测试风险因素数据结构"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="跳槽"
        )

        for risk in result.risk_factors:
            assert isinstance(risk, EventRiskFactor)
            assert risk.factor_type in ["risk", "opportunity"]
            assert risk.palace
            assert risk.description
            assert isinstance(risk.impact_score, (int, float))


class TestEventPredictorAgentEdgeCases:
    """边界情况测试"""

    def test_unknown_event_type_uses_minggong(self):
        """未知事件类型默认使用命宫"""
        chart = {
            "birth_info": {},
            "palaces": {
                "命宫": {"score": {"total": 50}, "stars": []},
            },
            "flowing_year": {"score": 50}
        }
        result = predict_event_sync(
            chart=chart,
            event_type="未知事件"
        )
        assert result.target_palace == "命宫"

    def test_empty_flowing_year(self):
        """空流年数据"""
        chart = {
            "birth_info": {},
            "palaces": {
                "官禄宫": {"score": {"total": 50}, "stars": []},
            }
        }
        result = predict_event_sync(
            chart=chart,
            event_type="晋升"
        )
        assert result.timing_score > 0

    def test_empty_palace_stars(self):
        """空宫位星曜"""
        chart = {
            "birth_info": {},
            "palaces": {
                "官禄宫": {"score": {"total": 50}, "stars": []},
            },
            "flowing_year": {"score": 60}
        }
        result = predict_event_sync(
            chart=chart,
            event_type="晋升"
        )
        assert result.success_rate > 0

    def test_multiple_sha_stars(self):
        """多煞星同宫风险"""
        chart = {
            "birth_info": {},
            "palaces": {
                "官禄宫": {
                    "score": {"total": 40},
                    "stars": [
                        {"name": "擎羊", "type": "煞星", "level": "陷"},
                        {"name": "陀罗", "type": "煞星", "level": "陷"},
                        {"name": "火星", "type": "煞星", "level": "陷"}
                    ]
                },
            },
            "flowing_year": {"score": 50}
        }
        result = predict_event_sync(
            chart=chart,
            event_type="晋升"
        )
        # 应该识别出多煞星同宫风险
        has_multi_sha_risk = any(
            "多煞星" in r.description for r in result.risk_factors
        )
        assert has_multi_sha_risk


class TestLLMEventPredictorAnalyzer:
    """LLM增强分析测试（使用Mock）"""

    @patch('app.utils.llm_client.LLMClient')
    def test_llm_analyze_with_mock(self, mock_llm_class, sample_chart_data):
        """测试LLM分析（Mock模式）"""
        # Mock LLM响应
        mock_response = {
            "analysis_type": "event_prediction",
            "event_type": "跳槽",
            "target_palace": "官禄宫",
            "success_probability": {
                "base_probability": 75,
                "adjusted_probability": 78,
                "confidence": 0.85,
                "best_case": 90,
                "worst_case": 60
            },
            "timing_analysis": {
                "year_timing": "良好",
                "month_timing": "3月、9月",
                "optimal_window": "2025年下半年"
            },
            "favorable_factors": [
                {"factor": "太阳星旺", "palace": "官禄宫", "impact": 20}
            ],
            "risk_factors": [],
            "overall_reasoning": "命盘显示事业运势良好"
        }

        mock_llm_instance = MagicMock()
        mock_llm_instance.chat_json.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance

        # 执行分析
        analyzer = LLMEventPredictorAnalyzer(sample_chart_data)
        result = analyzer.analyze_with_llm_sync(
            event_type="跳槽",
            target_year=2025
        )

        assert result["analysis_type"] == "event_prediction"
        assert result["event_type"] == "跳槽"
        assert "rule_based_analysis" in result
        assert result["rule_based_analysis"]["success_rate"] > 0

    @patch('app.utils.llm_client.LLMClient')
    def test_llm_analyze_weak_chart(self, mock_llm_class, weak_chart_data):
        """测试LLM分析弱势命盘"""
        mock_response = {
            "analysis_type": "event_prediction",
            "event_type": "晋升",
            "target_palace": "官禄宫",
            "success_probability": {
                "base_probability": 35,
                "adjusted_probability": 30,
                "confidence": 0.8,
                "best_case": 50,
                "worst_case": 15
            },
            "timing_analysis": {
                "year_timing": "一般",
                "month_timing": "避开年初"
            },
            "favorable_factors": [],
            "risk_factors": [
                {"factor": "煞星汇聚", "palace": "命宫", "impact": -30}
            ],
            "actionable_advice": [
                {"advice": "提升专业能力", "timing": "全年", "priority": "high"}
            ],
            "overall_reasoning": "命盘显示晋升难度较大"
        }

        mock_llm_instance = MagicMock()
        mock_llm_instance.chat_json.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance

        analyzer = LLMEventPredictorAnalyzer(weak_chart_data)
        result = analyzer.analyze_with_llm_sync(
            event_type="晋升",
            target_year=2025
        )

        assert result["success_probability"]["adjusted_probability"] < 50

    @patch('app.utils.llm_client.LLMClient')
    def test_llm_analyze_strong_chart(self, mock_llm_class, strong_chart_data):
        """测试LLM分析强势命盘"""
        mock_response = {
            "analysis_type": "event_prediction",
            "event_type": "创业",
            "target_palace": "官禄宫",
            "success_probability": {
                "base_probability": 85,
                "adjusted_probability": 92,
                "confidence": 0.95,
                "best_case": 98,
                "worst_case": 75
            },
            "timing_analysis": {
                "year_timing": "极佳",
                "month_timing": "5月-10月"
            },
            "favorable_factors": [
                {"factor": "紫府同宫", "palace": "命宫", "impact": 30}
            ],
            "risk_factors": [],
            "actionable_advice": [
                {"advice": "把握时机，大胆推进", "timing": "下半年", "priority": "high"}
            ],
            "overall_reasoning": "命盘显示创业运势极佳"
        }

        mock_llm_instance = MagicMock()
        mock_llm_instance.chat_json.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance

        analyzer = LLMEventPredictorAnalyzer(strong_chart_data)
        result = analyzer.analyze_with_llm_sync(
            event_type="创业",
            target_year=2025
        )

        assert result["success_probability"]["adjusted_probability"] >= 80


class TestEventPredictionIntegration:
    """集成测试"""

    def test_event_type_mapping_completeness(self, sample_chart_data):
        """测试所有事件类型都能正确映射"""
        event_types = [
            "跳槽", "晋升", "创业", "求职面试",
            "官司诉讼", "考试升学", "出行远行", "求学申请",
            "商务签约", "投资理财", "结婚嫁娶", "搬家乔迁"
        ]

        for event_type in event_types:
            result = predict_event_sync(
                chart=sample_chart_data,
                event_type=event_type
            )
            assert result.event_type == event_type
            assert result.target_palace is not None

    def test_timing_score_range(self, sample_chart_data):
        """测试时机评分范围"""
        # 测试不同流年数据
        chart_high = {
            **sample_chart_data,
            "flowing_year": {"score": 95}
        }
        chart_low = {
            **sample_chart_data,
            "flowing_year": {"score": 20}
        }

        result_high = predict_event_sync(chart_high, "跳槽")
        result_low = predict_event_sync(chart_low, "跳槽")

        assert result_high.timing_score > result_low.timing_score

    def test_suggestions_generation(self, sample_chart_data):
        """测试建议生成"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="跳槽"
        )

        assert isinstance(result.suggestions, list)
        assert len(result.suggestions) <= 5

    def test_confidence_calculation(self, sample_chart_data):
        """测试置信度计算"""
        result = predict_event_sync(
            chart=sample_chart_data,
            event_type="跳槽"
        )

        assert 0.3 <= result.confidence <= 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
