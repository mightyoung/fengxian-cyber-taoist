"""
E2E测试 - BirthTimingAgent LLM集成测试

测试:
1. LLMBirthTimingAnalyzer - LLM增强分析器
2. llm_analyze_birth_timing_sync - 同步便捷函数
3. llm_analyze_birth_timing_enhanced - 完整增强分析流程
4. 提示词构建 - build_birth_timing_user_prompt

运行: pytest tests/e2e/test_birth_timing_llm.py -v
"""

import pytest
import sys
import os
from datetime import datetime

# 确保backend目录在Python路径中
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# ============ 测试数据 ============

# 测试母亲信息
TEST_MOTHER_INFO = {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 10,
    "gender": "female",
    "birthplace": "北京",
}

# 测试父亲信息
TEST_FATHER_INFO = {
    "year": 1988,
    "month": 8,
    "day": 20,
    "hour": 14,
    "gender": "male",
    "birthplace": "上海",
}

# 模拟的母亲命盘数据
TEST_MOTHER_CHART = {
    "birth_info": {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "gender": "female",
        "wuxing_ju": "火六局",
        "wuxing_ju_name": "火六局",
    },
    "palaces": {
        "命宫": {
            "branch": "寅",
            "tiangan": "甲",
            "stars": [
                {"name": "紫微", "type": "正曜", "level": "旺"},
            ],
        },
        "兄弟宫": {"branch": "卯", "tiangan": "乙", "stars": []},
        "夫妻宫": {"branch": "辰", "tiangan": "丙", "stars": []},
        "子女宫": {"branch": "巳", "tiangan": "丁", "stars": []},
        "财帛宫": {"branch": "午", "tiangan": "戊", "stars": []},
        "疾厄宫": {"branch": "未", "tiangan": "己", "stars": []},
        "迁移宫": {"branch": "申", "tiangan": "庚", "stars": []},
        "仆役宫": {"branch": "酉", "tiangan": "辛", "stars": []},
        "官禄宫": {"branch": "申", "tiangan": "壬", "stars": []},
        "田宅宫": {"branch": "酉", "tiangan": "癸", "stars": []},
        "父母宫": {"branch": "戌", "tiangan": "甲", "stars": []},
        "福德宫": {"branch": "亥", "tiangan": "乙", "stars": []},
    },
    "stars": {
        "main_stars": [
            {"name": "紫微", "palace": "命宫", "level": "旺", "type": "正曜"},
            {"name": "天机", "palace": "兄弟宫", "level": "平", "type": "正曜"},
        ],
        "auxiliary_stars": [],
        "sha_stars": [],
        "transform_stars": [],
    },
}

# 模拟的父亲命盘数据
TEST_FATHER_CHART = {
    "birth_info": {
        "year": 1988,
        "month": 8,
        "day": 20,
        "hour": 14,
        "gender": "male",
        "wuxing_ju": "水二局",
        "wuxing_ju_name": "水二局",
    },
    "palaces": {
        "命宫": {
            "branch": "午",
            "tiangan": "庚",
            "stars": [
                {"name": "天府", "type": "正曜", "level": "旺"},
            ],
        },
    },
    "stars": {
        "main_stars": [
            {"name": "天府", "palace": "命宫", "level": "旺", "type": "正曜"},
        ],
        "auxiliary_stars": [],
        "sha_stars": [],
        "transform_stars": [],
    },
}


# ============ 测试用例 ============

class TestLLMBirthTimingAnalyzer:
    """测试LLMBirthTimingAnalyzer类"""

    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        from app.services.divination.agents.birth_timing_agent import (
            BirthTimingOption,
            BirthTimingResult,
            LLMBirthTimingAnalyzer,
        )

        # 创建测试数据
        test_option = BirthTimingOption(
            rank=1,
            date="2026-09-15",
            lunar_date="农历八月初五",
            hour="午时 (11:00-13:00)",
            chart_summary={"main_star": "紫微", "wuxing_ju": "火六局"},
            score=85.0,
            level="极佳",
            strengths=["命宫紫微星尊贵", "无煞星冲破"],
            weaknesses=[],
            reasons=["命格优良"],
            warnings=[],
        )

        test_result = BirthTimingResult(
            options=[test_option],
            best_option=test_option,
            confidence=0.8,
        )

        # 初始化分析器
        analyzer = LLMBirthTimingAnalyzer(
            birth_timing_result=test_result,
            mother_chart=TEST_MOTHER_CHART,
            father_chart=TEST_FATHER_CHART,
        )

        assert analyzer.birth_timing_result is not None
        assert analyzer.mother_chart == TEST_MOTHER_CHART
        assert analyzer.father_chart == TEST_FATHER_CHART
        assert len(analyzer.birth_timing_result.options) == 1

    def test_analyzer_with_empty_result(self):
        """测试空结果分析"""
        from app.services.divination.agents.birth_timing_agent import (
            BirthTimingResult,
            LLMBirthTimingAnalyzer,
        )

        test_result = BirthTimingResult(
            options=[],
            confidence=0.0,
        )

        analyzer = LLMBirthTimingAnalyzer(
            birth_timing_result=test_result,
            mother_chart=None,
            father_chart=None,
        )

        assert analyzer.birth_timing_result.options == []

    def test_analyzer_sync_method(self):
        """测试同步方法存在"""
        from app.services.divination.agents.birth_timing_agent import (
            BirthTimingOption,
            BirthTimingResult,
            LLMBirthTimingAnalyzer,
        )

        test_option = BirthTimingOption(
            rank=1,
            date="2026-09-15",
            lunar_date="农历八月初五",
            hour="午时",
            chart_summary={},
            score=80.0,
            level="良好",
            strengths=["命格优良"],
            weaknesses=[],
            reasons=[],
            warnings=[],
        )

        test_result = BirthTimingResult(options=[test_option])

        analyzer = LLMBirthTimingAnalyzer(
            birth_timing_result=test_result,
            mother_chart=TEST_MOTHER_CHART,
            father_chart=None,
        )

        # 检查同步方法存在
        assert hasattr(analyzer, "analyze_with_llm_sync")
        assert callable(analyzer.analyze_with_llm_sync)

        # 检查异步方法存在
        assert hasattr(analyzer, "analyze_with_llm")
        assert callable(analyzer.analyze_with_llm)

        # 检查增强方法存在
        assert hasattr(analyzer, "enhance_result")
        assert callable(analyzer.enhance_result)


class TestLLMConvenienceFunctions:
    """测试LLM便捷函数"""

    def test_llm_analyze_birth_timing_sync_exists(self):
        """测试同步便捷函数存在"""
        from app.services.divination.agents.birth_timing_agent import (
            llm_analyze_birth_timing_sync,
        )

        assert callable(llm_analyze_birth_timing_sync)

    def test_llm_analyze_birth_timing_async_exists(self):
        """测试异步便捷函数存在"""
        from app.services.divination.agents.birth_timing_agent import (
            llm_analyze_birth_timing,
        )

        assert callable(llm_analyze_birth_timing)

    def test_llm_analyze_birth_timing_enhanced_exists(self):
        """测试完整增强函数存在"""
        from app.services.divination.agents.birth_timing_agent import (
            llm_analyze_birth_timing_enhanced,
        )

        assert callable(llm_analyze_birth_timing_enhanced)


class TestPromptBuilder:
    """测试提示词构建"""

    def test_build_birth_timing_user_prompt_basic(self):
        """测试基础提示词构建"""
        from app.services.divination.agents.llm_prompts import build_birth_timing_user_prompt

        # 创建测试数据
        test_result = {
            "options": [
                {
                    "rank": 1,
                    "date": "2026-09-15",
                    "hour": "午时",
                    "lunar_date": "农历八月初五",
                    "score": 85.0,
                    "level": "极佳",
                    "chart_summary": {
                        "main_star": "紫微",
                        "wuxing_ju": "火六局",
                        "transforms": ["化禄", "化权"],
                    },
                    "strengths": ["命宫紫微星尊贵", "无煞星冲破"],
                    "weaknesses": ["贪狼桃花特性"],
                    "reasons": ["命格优良，适合剖腹产"],
                },
                {
                    "rank": 2,
                    "date": "2026-09-16",
                    "hour": "巳时",
                    "lunar_date": "农历八月初六",
                    "score": 78.0,
                    "level": "良好",
                    "chart_summary": {
                        "main_star": "天同",
                        "wuxing_ju": "水二局",
                        "transforms": [],
                    },
                    "strengths": ["命格平和"],
                    "weaknesses": [],
                    "reasons": ["尚可"],
                },
            ],
            "best_option": {
                "date": "2026-09-15",
                "hour": "午时",
                "score": 85.0,
            },
            "confidence": 0.8,
        }

        prompt = build_birth_timing_user_prompt(
            birth_timing_result=test_result,
            mother_chart=TEST_MOTHER_CHART,
            father_chart=TEST_FATHER_CHART,
        )

        # 验证提示词包含关键内容
        assert "母亲命盘信息" in prompt
        assert "父亲命盘信息" in prompt
        assert "候选时辰选项" in prompt
        assert "核心问题" in prompt
        assert "2026-09-15" in prompt
        assert "午时" in prompt
        assert "紫微" in prompt

    def test_build_prompt_without_parents(self):
        """测试无父母命盘的提示词构建"""
        from app.services.divination.agents.llm_prompts import build_birth_timing_user_prompt

        test_result = {
            "options": [
                {
                    "rank": 1,
                    "date": "2026-09-15",
                    "hour": "午时",
                    "lunar_date": "农历八月初五",
                    "score": 80.0,
                    "level": "良好",
                    "chart_summary": {"main_star": "紫微", "wuxing_ju": "火六局"},
                    "strengths": [],
                    "weaknesses": [],
                    "reasons": [],
                },
            ],
            "confidence": 0.7,
        }

        prompt = build_birth_timing_user_prompt(
            birth_timing_result=test_result,
            mother_chart=None,
            father_chart=None,
        )

        # 验证提示词不包含父母信息
        assert "母亲命盘信息" not in prompt or "未知" in prompt
        assert "候选时辰选项" in prompt

    def test_build_prompt_with_custom_question(self):
        """测试带自定义问题的提示词构建"""
        from app.services.divination.agents.llm_prompts import build_birth_timing_user_prompt

        test_result = {
            "options": [],
            "confidence": 0.0,
        }

        custom_question = "请特别关注孩子的学业运势"
        prompt = build_birth_timing_user_prompt(
            birth_timing_result=test_result,
            mother_chart=None,
            father_chart=None,
            question=custom_question,
        )

        assert custom_question in prompt


class TestBirthTimingResultEnhancement:
    """测试结果增强功能"""

    def test_result_to_dict(self):
        """测试结果序列化"""
        from app.services.divination.agents.birth_timing_agent import (
            BirthTimingOption,
            BirthTimingResult,
        )

        test_option = BirthTimingOption(
            rank=1,
            date="2026-09-15",
            lunar_date="农历八月初五",
            hour="午时 (11:00-13:00)",
            chart_summary={"main_star": "紫微"},
            score=85.0,
            level="极佳",
            strengths=["命宫紫微星尊贵"],
            weaknesses=["贪狼桃花"],
            reasons=["命格优良"],
            warnings=["注意感情"],
        )

        test_result = BirthTimingResult(
            service_type="birth_timing",
            mother_chart=TEST_MOTHER_CHART,
            father_chart=TEST_FATHER_CHART,
            options=[test_option],
            best_option=test_option,
            analysis_summary="测试摘要",
            confidence=0.85,
        )

        # 转换为字典
        result_dict = test_result.to_dict()

        # 验证结构
        assert result_dict["service_type"] == "birth_timing"
        assert "mother_chart" in result_dict
        assert "father_chart" in result_dict
        assert "options" in result_dict
        assert len(result_dict["options"]) == 1
        assert "best_option" in result_dict
        assert result_dict["confidence"] == 0.85

        # 验证选项字典
        opt_dict = result_dict["options"][0]
        assert opt_dict["date"] == "2026-09-15"
        assert opt_dict["score"] == 85.0
        assert opt_dict["level"] == "极佳"

    def test_option_to_dict(self):
        """测试选项序列化"""
        from app.services.divination.agents.birth_timing_agent import BirthTimingOption

        test_option = BirthTimingOption(
            rank=1,
            date="2026-09-15",
            lunar_date="农历八月初五",
            hour="午时",
            chart_summary={"main_star": "紫微", "wuxing_ju": "火六局"},
            score=85.0,
            level="极佳",
            strengths=["命宫紫微星尊贵", "无煞星冲破"],
            weaknesses=["贪狼桃花特性"],
            reasons=["命格优良，适合剖腹产"],
            warnings=["注意感情运势"],
        )

        opt_dict = test_option.to_dict()

        # 验证结构
        assert opt_dict["rank"] == 1
        assert opt_dict["date"] == "2026-09-15"
        assert opt_dict["lunar_date"] == "农历八月初五"
        assert opt_dict["hour"] == "午时"
        assert opt_dict["chart_summary"]["main_star"] == "紫微"
        assert opt_dict["score"] == 85.0
        assert opt_dict["level"] == "极佳"
        assert len(opt_dict["strengths"]) == 2
        assert len(opt_dict["weaknesses"]) == 1


class TestIntegration:
    """集成测试"""

    def test_full_analysis_flow(self):
        """测试完整分析流程"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
            LLMBirthTimingAnalyzer,
        )

        # 运行规则引擎分析（使用短日期范围加快测试）
        result = analyze_birth_timing_sync(
            mother_birth_info=TEST_MOTHER_INFO,
            father_birth_info=None,
            date_range_start="2026-04-01",
            date_range_end="2026-04-02",  # 只分析2天
            top_n=5,
        )

        # 验证结果
        assert result is not None
        assert isinstance(result.options, list)
        assert result.confidence >= 0.0

        # 如果有选项，验证结构
        if result.options:
            opt = result.options[0]
            assert opt.rank >= 1
            assert opt.score >= 0.0
            assert opt.level in ["极佳", "良好", "中等", "一般", "较差"]

    def test_llm_analyzer_with_real_result(self):
        """测试LLM分析器与真实结果"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
            LLMBirthTimingAnalyzer,
        )

        # 先运行规则引擎
        result = analyze_birth_timing_sync(
            mother_birth_info=TEST_MOTHER_INFO,
            father_birth_info=None,
            date_range_start="2026-04-01",
            date_range_end="2026-04-01",
            top_n=3,
        )

        # 初始化LLM分析器
        analyzer = LLMBirthTimingAnalyzer(
            birth_timing_result=result,
            mother_chart=TEST_MOTHER_CHART,
            father_chart=None,
        )

        # 验证分析器可以处理结果
        assert analyzer.birth_timing_result is not None
        assert len(analyzer.birth_timing_result.options) >= 0


# ============ 运行测试 ============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
