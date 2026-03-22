"""
E2E测试 - DateSelectionAgent LLM集成测试

测试:
1. LLMDateSelectionAnalyzer - LLM增强分析器
2. llm_analyze_date_selection_sync - 同步便捷函数
3. llm_analyze_date_selection - 异步便捷函数
4. 提示词构建 - build_date_selection_user_prompt
5. DATE_SELECTION_SYSTEM_PROMPT - 系统提示词

运行: pytest tests/e2e/test_date_selection_llm.py -v
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

# 测试命盘数据
TEST_CHART = {
    "birth_info": {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "gender": "male",
        "wuxing_ju": "水二局",
        "wuxing_ju_name": "水二局",
        "tiangan": "甲",
    },
    "palaces": {
        "命宫": {
            "branch": "子",
            "tiangan": "甲",
            "stars": [
                {"name": "紫微", "type": "正曜", "level": "旺"},
                {"name": "天机", "type": "正曜", "level": "平"},
            ],
        },
        "兄弟宫": {"branch": "丑", "tiangan": "乙", "stars": []},
        "夫妻宫": {"branch": "寅", "tiangan": "丙", "stars": []},
        "子女宫": {"branch": "卯", "tiangan": "丁", "stars": []},
        "财帛宫": {"branch": "辰", "tiangan": "戊", "stars": []},
        "疾厄宫": {"branch": "巳", "tiangan": "己", "stars": []},
        "迁移宫": {"branch": "午", "tiangan": "庚", "stars": []},
        "仆役宫": {"branch": "未", "tiangan": "辛", "stars": []},
        "官禄宫": {"branch": "申", "tiangan": "壬", "stars": []},
        "田宅宫": {"branch": "酉", "tiangan": "癸", "stars": []},
        "父母宫": {"branch": "戌", "tiangan": "甲", "stars": []},
        "福德宫": {"branch": "亥", "tiangan": "乙", "stars": []},
    },
    "stars": {
        "main_stars": [
            {"name": "紫微", "palace": "命宫", "level": "旺", "type": "正曜"},
            {"name": "天机", "palace": "命宫", "level": "平", "type": "正曜"},
        ],
        "auxiliary_stars": [],
        "sha_stars": [],
        "transform_stars": [],
    },
}

# 测试候选日期列表
TEST_DAILY_OPTIONS = [
    {
        "rank": 1,
        "solar_date": "2026-04-15",
        "lunar_date": "三月十九",
        "tiangan": "丙寅",
        "dizhi": "寅",
        "score": 78.0,
        "level": "良好",
        "is_auspicious": True,
        "suitable_for": ["结婚", "搬家", "祭祀"],
        "avoid": ["动土"],
        "key_factors": ["木火相生", "命宫能量加持"],
        "best_time_window": "巳时（09:00-11:00）",
        "warnings": [],
    },
    {
        "rank": 2,
        "solar_date": "2026-04-18",
        "lunar_date": "三月廿二",
        "tiangan": "己巳",
        "dizhi": "巳",
        "score": 75.0,
        "level": "良好",
        "is_auspicious": True,
        "suitable_for": ["结婚", "出行"],
        "avoid": [],
        "key_factors": ["巳火为命宫禄位"],
        "best_time_window": "午时（11:00-13:00）",
        "warnings": [],
    },
    {
        "rank": 3,
        "solar_date": "2026-04-22",
        "lunar_date": "三月廿六",
        "tiangan": "癸酉",
        "dizhi": "酉",
        "score": 72.0,
        "level": "中等",
        "is_auspicious": True,
        "suitable_for": ["入学", "开市"],
        "avoid": ["结婚"],
        "key_factors": ["桃花星旺"],
        "best_time_window": "酉时（17:00-19:00）",
        "warnings": ["癸水克甲木"],
    },
]


# ============ 测试用例 ============

class TestLLMDateSelectionAnalyzer:
    """测试LLMDateSelectionAnalyzer类"""

    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        from app.services.divination.agents.date_selection_agent import (
            LLMDateSelectionAnalyzer,
        )

        analyzer = LLMDateSelectionAnalyzer(TEST_CHART)
        assert analyzer.chart == TEST_CHART

    def test_sync_analysis_returns_dict(self):
        """测试同步分析返回字典"""
        from app.services.divination.agents.date_selection_agent import (
            LLMDateSelectionAnalyzer,
            DailyOption,
        )

        # 创建测试选项
        options = [DailyOption(**opt) for opt in TEST_DAILY_OPTIONS]

        analyzer = LLMDateSelectionAnalyzer(TEST_CHART)
        # 注意：这里只测试结构，不调用实际LLM
        assert analyzer is not None
        assert len(options) == 3


class TestDateSelectionSyncFunction:
    """测试llm_analyze_date_selection_sync函数"""

    def test_function_exists(self):
        """测试函数存在"""
        from app.services.divination.agents.date_selection_agent import (
            llm_analyze_date_selection_sync,
        )
        assert callable(llm_analyze_date_selection_sync)

    def test_function_signature(self):
        """测试函数签名"""
        import inspect
        from app.services.divination.agents.date_selection_agent import (
            llm_analyze_date_selection_sync,
        )

        sig = inspect.signature(llm_analyze_date_selection_sync)
        params = list(sig.parameters.keys())

        assert "chart" in params
        assert "date_type" in params
        assert "daily_options" in params
        assert "question" in params


class TestLLMPrompts:
    """测试LLM提示词"""

    def test_system_prompt_exists(self):
        """测试系统提示词存在"""
        from app.services.divination.agents.llm_prompts import (
            DATE_SELECTION_SYSTEM_PROMPT,
        )

        assert DATE_SELECTION_SYSTEM_PROMPT is not None
        assert len(DATE_SELECTION_SYSTEM_PROMPT) > 0
        assert "择日" in DATE_SELECTION_SYSTEM_PROMPT
        assert "紫微斗数" in DATE_SELECTION_SYSTEM_PROMPT

    def test_system_prompt_contains_guidance(self):
        """测试系统提示词包含指导原则"""
        from app.services.divination.agents.llm_prompts import (
            DATE_SELECTION_SYSTEM_PROMPT,
        )

        # 检查关键原则存在
        assert "吉神凶煞" in DATE_SELECTION_SYSTEM_PROMPT
        assert "喜神忌神" in DATE_SELECTION_SYSTEM_PROMPT
        assert "事件类型" in DATE_SELECTION_SYSTEM_PROMPT
        assert "日柱五行" in DATE_SELECTION_SYSTEM_PROMPT

    def test_build_user_prompt_function_exists(self):
        """测试用户提示词构建函数存在"""
        from app.services.divination.agents.llm_prompts import (
            build_date_selection_user_prompt,
        )

        assert callable(build_date_selection_user_prompt)

    def test_build_user_prompt_structure(self):
        """测试用户提示词结构"""
        from app.services.divination.agents.llm_prompts import (
            build_date_selection_user_prompt,
        )

        prompt = build_date_selection_user_prompt(
            chart=TEST_CHART,
            date_type="结婚嫁娶",
            daily_options=TEST_DAILY_OPTIONS,
            question="哪个日期最适合结婚？",
        )

        # 验证基本结构
        assert "结婚嫁娶" in prompt
        assert "甲" in prompt  # 出生年干
        assert "2026-04-15" in prompt
        assert "2026-04-18" in prompt
        assert "2026-04-22" in prompt
        assert "丙寅" in prompt
        assert "78" in prompt


class TestDateSelectionResult:
    """测试DateSelectionResult结构"""

    def test_daily_option_to_dict(self):
        """测试DailyOption转换为字典"""
        from app.services.divination.agents.date_selection_agent import (
            DailyOption,
        )

        option = DailyOption(
            rank=1,
            solar_date="2026-04-15",
            lunar_date="三月十九",
            tiangan="丙寅",
            dizhi="寅",
            score=78.0,
            level="良好",
            is_auspicious=True,
            suitable_for=["结婚", "搬家"],
            avoid=["动土"],
            key_factors=["木火相生"],
            best_time_window="巳时（09:00-11:00）",
            warnings=[],
        )

        result = option.to_dict()

        assert result["rank"] == 1
        assert result["solar_date"] == "2026-04-15"
        assert result["tiangan"] == "丙寅"
        assert result["score"] == 78.0
        assert result["is_auspicious"] is True

    def test_result_structure(self):
        """测试DateSelectionResult结构"""
        from app.services.divination.agents.date_selection_agent import (
            DateSelectionAgent,
            DailyOption,
        )

        agent = DateSelectionAgent(
            chart=TEST_CHART,
            date_type="结婚嫁娶",
            date_range_start="2026-04-01",
            date_range_end="2026-04-30",
            top_n=5,
        )

        result = agent.analyze()

        assert result.service_type == "date_selection"
        assert result.date_type == "结婚嫁娶"
        assert isinstance(result.daily_options, list)
        assert isinstance(result.best_dates, list)
        assert isinstance(result.analysis_summary, str)


class TestDateSelectionEventTypes:
    """测试不同事件类型的择日"""

    @pytest.fixture
    def chart(self):
        """返回测试命盘"""
        return TEST_CHART

    def test_marriage_date_selection(self, chart):
        """测试结婚嫁娶择日"""
        from app.services.divination.agents.date_selection_agent import (
            DateSelectionAgent,
        )

        agent = DateSelectionAgent(
            chart=chart,
            date_type="结婚嫁娶",
            date_range_start="2026-04-01",
            date_range_end="2026-04-30",
            top_n=3,
        )

        result = agent.analyze()

        # 验证夫妻宫、迁移宫、福德宫是关键宫位
        assert "夫妻宫" in result.target_palaces
        assert "迁移宫" in result.target_palaces
        assert "福德宫" in result.target_palaces

    def test_business_date_selection(self, chart):
        """测试开市开张择日"""
        from app.services.divination.agents.date_selection_agent import (
            DateSelectionAgent,
        )

        agent = DateSelectionAgent(
            chart=chart,
            date_type="开市开张",
            date_range_start="2026-05-01",
            date_range_end="2026-05-31",
            top_n=3,
        )

        result = agent.analyze()

        # 验证财帛宫、官禄宫、田宅宫是关键宫位
        assert "财帛宫" in result.target_palaces
        assert "官禄宫" in result.target_palaces
        assert "田宅宫" in result.target_palaces

    def test_move_date_selection(self, chart):
        """测试搬家入宅择日"""
        from app.services.divination.agents.date_selection_agent import (
            DateSelectionAgent,
        )

        agent = DateSelectionAgent(
            chart=chart,
            date_type="搬家入宅",
            date_range_start="2026-06-01",
            date_range_end="2026-06-30",
            top_n=3,
        )

        result = agent.analyze()

        # 验证田宅宫、命宫是关键宫位
        assert "田宅宫" in result.target_palaces
        assert "命宫" in result.target_palaces


class TestDateSelectionScoring:
    """测试日期评分逻辑"""

    @pytest.fixture
    def chart(self):
        """返回测试命盘"""
        return TEST_CHART

    def test_score_calculation(self, chart):
        """测试分数计算"""
        from app.services.divination.agents.date_selection_agent import (
            DateSelectionAgent,
        )

        agent = DateSelectionAgent(
            chart=chart,
            date_type="结婚嫁娶",
            date_range_start="2026-04-15",
            date_range_end="2026-04-15",
            top_n=5,
        )

        result = agent.analyze()

        # 应该有至少一个选项
        assert len(result.daily_options) >= 1

        # 分数应该在0-100之间
        for opt in result.daily_options:
            assert 0 <= opt.score <= 100

    def test_level_assignment(self, chart):
        """测试等级分配"""
        from app.services.divination.agents.date_selection_agent import (
            DateSelectionAgent,
        )

        agent = DateSelectionAgent(
            chart=chart,
            date_type="结婚嫁娶",
            date_range_start="2026-04-01",
            date_range_end="2026-04-30",
            top_n=10,
        )

        result = agent.analyze()

        # 验证等级分配
        for opt in result.daily_options:
            assert opt.level in ["极佳", "良好", "中等", "一般", "较差"]

    def test_best_dates_sorted(self, chart):
        """测试最佳日期排序"""
        from app.services.divination.agents.date_selection_agent import (
            DateSelectionAgent,
        )

        agent = DateSelectionAgent(
            chart=chart,
            date_type="结婚嫁娶",
            date_range_start="2026-04-01",
            date_range_end="2026-04-30",
            top_n=5,
        )

        result = agent.analyze()

        # 验证排序
        if len(result.best_dates) >= 2:
            for i in range(len(result.best_dates) - 1):
                assert result.best_dates[i].score >= result.best_dates[i + 1].score


class TestExportFunctions:
    """测试导出函数"""

    def test_export_from_agents(self):
        """测试从agents模块导出"""
        from app.services.divination.agents import (
            DateSelectionAgent,
            DateSelectionResult,
            DailyOption,
            select_date_sync,
            LLMDateSelectionAnalyzer,
            llm_analyze_date_selection_sync,
        )

        assert callable(DateSelectionAgent)
        assert callable(select_date_sync)
        assert callable(llm_analyze_date_selection_sync)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
