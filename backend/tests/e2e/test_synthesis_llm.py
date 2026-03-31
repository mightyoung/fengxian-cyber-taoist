"""
E2E测试 - SynthesisAgent LLM综合分析测试

测试 LLMSynthesisAnalyzer 和 llm_analyze_synthesis_sync 函数

运行方式:
    pytest tests/e2e/test_synthesis_llm.py -v
"""

import pytest
import os
import sys

# 添加 backend 目录到 path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)


# ============ 测试数据 ============

SAMPLE_CHART_DATA = {
    "birth_info": {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "gender": "male",
        "wuxing_ju": "水二局"
    },
    "palaces": {
        "命宫": {
            "branch": "子",
            "stars": [
                {"name": "紫微", "type": "正曜", "level": "旺"},
                {"name": "天机", "type": "正曜", "level": "平"},
                {"name": "左辅", "type": "辅星", "level": "旺"}
            ]
        },
        "兄弟宫": {"branch": "丑", "stars": []},
        "夫妻宫": {
            "branch": "寅",
            "stars": [
                {"name": "贪狼", "type": "正曜", "level": "庙"}
            ]
        },
        "子女宫": {"branch": "卯", "stars": []},
        "财帛宫": {
            "branch": "辰",
            "stars": [
                {"name": "太阳", "type": "正曜", "level": "旺"}
            ]
        },
        "疾厄宫": {"branch": "巳", "stars": []},
        "迁移宫": {"branch": "午", "stars": []},
        "仆役宫": {"branch": "未", "stars": []},
        "官禄宫": {
            "branch": "申",
            "stars": [
                {"name": "天府", "type": "正曜", "level": "旺"}
            ]
        },
        "田宅宫": {"branch": "酉", "stars": []},
        "父母宫": {"branch": "戌", "stars": []},
        "福德宫": {"branch": "亥", "stars": []}
    },
    "stars": {
        "main_stars": [
            {"name": "紫微", "palace": "命宫", "level": "旺"},
            {"name": "天机", "palace": "命宫", "level": "平"},
            {"name": "太阳", "palace": "财帛宫", "level": "旺"},
            {"name": "天府", "palace": "官禄宫", "level": "旺"},
            {"name": "贪狼", "palace": "夫妻宫", "level": "庙"}
        ],
        "auxiliary_stars": [
            {"name": "左辅", "palace": "命宫", "level": "旺"}
        ],
        "sha_stars": [],
        "transform_stars": []
    },
    "transforms": [
        {"type": "禄", "star": "廉贞", "palace": "财帛宫"},
        {"type": "权", "star": "紫微", "palace": "官禄宫"},
        {"type": "忌", "star": "廉贞", "palace": "福德宫"}
    ]
}

SAMPLE_ANALYSIS_DATA = {
    "star_analysis": {
        "summary": "命宫紫微天机会照，具备领导才能和智慧。贪狼在夫妻宫旺位，感情方面有活力。"
    },
    "palace_analysis": {
        "summary": "命宫、财帛宫、官禄宫皆为强宫，事业财运有基础。"
    },
    "pattern_analysis": {
        "summary": "紫微天府坐命，代表领导才能和财运基础。"
    },
    "transform_analysis": {
        "summary": "廉贞化禄在财帛宫，财运转佳；紫微化权在官禄宫，事业发展有权力。"
    }
}


# ============ Test Class ============

class TestLLMSynthesisAnalyzer:
    """LLMSynthesisAnalyzerStandard 测试"""

    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        from app.services.divination.agents.synthesis_agent import LLMSynthesisAnalyzerStandard

        # 无分析数据初始化
        analyzer = LLMSynthesisAnalyzerStandard(SAMPLE_CHART_DATA)
        assert analyzer.chart == SAMPLE_CHART_DATA
        assert analyzer.analysis == {}

        # 带分析数据初始化
        analyzer_with_data = LLMSynthesisAnalyzerStandard(SAMPLE_CHART_DATA, SAMPLE_ANALYSIS_DATA)
        assert analyzer_with_data.analysis == SAMPLE_ANALYSIS_DATA

    def test_analyzer_has_analyze_method(self):
        """测试分析器具有标准方法"""
        from app.services.divination.agents.synthesis_agent import LLMSynthesisAnalyzerStandard

        analyzer = LLMSynthesisAnalyzerStandard(SAMPLE_CHART_DATA)

        # 检查是否有标准方法
        assert hasattr(analyzer, 'analyze_with_llm')
        assert hasattr(analyzer, 'analyze_with_llm_sync')
        assert callable(analyzer.analyze_with_llm)
        assert callable(analyzer.analyze_with_llm_sync)

    @pytest.mark.asyncio
    async def test_analyze_with_llm_returns_dict(self):
        """测试异步分析返回字典结构"""
        from app.services.divination.agents.synthesis_agent import LLMSynthesisAnalyzerStandard

        analyzer = LLMSynthesisAnalyzerStandard(SAMPLE_CHART_DATA, SAMPLE_ANALYSIS_DATA)

        # 由于需要 LLM API，这里只测试方法签名和返回类型
        # 实际测试需要 mock LLMClient
        result = await analyzer.analyze_with_llm(temperature=0.3)

        # 验证返回的是字典
        assert isinstance(result, dict)

        # 验证包含分析类型
        assert "analysis_type" in result or "chart_overview" in result or "overall_pattern" in result

    def test_analyze_with_llm_sync_returns_dict(self):
        """测试同步分析返回字典结构"""
        from app.services.divination.agents.synthesis_agent import LLMSynthesisAnalyzerStandard

        analyzer = LLMSynthesisAnalyzerStandard(SAMPLE_CHART_DATA, SAMPLE_ANALYSIS_DATA)

        # 由于需要 LLM API，这里只测试方法签名
        result = analyzer.analyze_with_llm_sync(temperature=0.3)

        # 验证返回的是字典
        assert isinstance(result, dict)

    def test_analyze_with_question_parameter(self):
        """测试带问题的分析"""
        from app.services.divination.agents.synthesis_agent import LLMSynthesisAnalyzerStandard

        analyzer = LLMSynthesisAnalyzerStandard(SAMPLE_CHART_DATA, SAMPLE_ANALYSIS_DATA)

        question = "事业运程如何？"
        result = analyzer.analyze_with_llm_sync(question=question)

        assert isinstance(result, dict)


class TestLLMSynthesisFunctions:
    """LLM综合分析函数测试"""

    def test_llm_analyze_synthesis_sync_function_exists(self):
        """测试 llm_analyze_synthesis_sync 函数存在"""
        from app.services.divination.agents import llm_analyze_synthesis_sync

        assert callable(llm_analyze_synthesis_sync)

    def test_llm_analyze_synthesis_function_exists(self):
        """测试 llm_analyze_synthesis 函数存在"""
        from app.services.divination.agents import LLMSynthesisAnalyzer

        # 检查函数是否存在（通过类方法）
        assert hasattr(LLMSynthesisAnalyzer, 'analyze_with_llm')

    def test_llm_analyze_synthesis_sync_returns_dict(self):
        """测试 llm_analyze_synthesis_sync 返回字典"""
        from app.services.divination.agents import llm_analyze_synthesis_sync

        # 由于需要 LLM API，这里只测试方法签名
        result = llm_analyze_synthesis_sync(SAMPLE_CHART_DATA, SAMPLE_ANALYSIS_DATA)

        assert isinstance(result, dict)

    def test_llm_analyze_synthesis_sync_with_question(self):
        """测试带问题的综合分析"""
        from app.services.divination.agents import llm_analyze_synthesis_sync

        question = "我的财运如何？"
        result = llm_analyze_synthesis_sync(
            SAMPLE_CHART_DATA,
            SAMPLE_ANALYSIS_DATA,
            question=question
        )

        assert isinstance(result, dict)

    def test_llm_analyze_synthesis_sync_with_minimal_data(self):
        """测试最小数据输入"""
        from app.services.divination.agents import llm_analyze_synthesis_sync

        minimal_chart = {
            "birth_info": {"year": 1990, "month": 1, "day": 1, "gender": "male"},
            "palaces": {},
            "stars": {}
        }

        result = llm_analyze_synthesis_sync(minimal_chart)

        assert isinstance(result, dict)


class TestSynthesisAnalyzerIntegration:
    """综合分析器集成测试"""

    def test_analyzer_with_full_analysis_data(self):
        """测试带完整分析数据的分析器"""
        from app.services.divination.agents.synthesis_agent import LLMSynthesisAnalyzerStandard

        full_analysis = {
            "star_analysis": {
                "main_stars": ["紫微", "天府"],
                "summary": "紫微天府坐命"
            },
            "palace_analysis": {
                "palace_strengths": {"命宫": 85, "财帛宫": 80},
                "summary": "命宫强旺"
            },
            "pattern_analysis": {
                "major_patterns": ["紫府同宫格"],
                "summary": "格局佳"
            },
            "transform_analysis": {
                "original_transforms": {"廉贞": "化禄"},
                "summary": "财运转佳"
            },
            "timing_analysis": {
                "current_period": "30-40岁",
                "summary": "事业黄金期"
            }
        }

        analyzer = LLMSynthesisAnalyzerStandard(SAMPLE_CHART_DATA, full_analysis)

        result = analyzer.analyze_with_llm_sync()

        assert isinstance(result, dict)
        # 验证分析器能正确处理完整数据
        assert analyzer.analysis == full_analysis

    def test_export_from_init(self):
        """测试从 __init__ 导出"""
        # 测试可以从模块直接导入
        from app.services.divination.agents import (
            LLMSynthesisAnalyzer,
            llm_analyze_synthesis,
            llm_analyze_synthesis_sync,
            llm_synthesize_report,
            llm_synthesize_report_sync
        )

        assert LLMSynthesisAnalyzer is not None
        assert callable(llm_analyze_synthesis_sync)


# ============ 运行测试 ============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
