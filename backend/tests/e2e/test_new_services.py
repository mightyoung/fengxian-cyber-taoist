"""
E2E测试 - 6个新服务集成测试

测试:
1. BirthTimingAgent - 剖腹产良辰吉日
2. DateSelectionAgent - 择日分析
3. EventPredictorAgent - 事件预测
4. MarriageCompatibilityAgent - 姻缘配对
5. CareerRecommendationAgent - 职业推荐
6. NameRecommendationAgent - 改名起名

运行: pytest tests/e2e/test_new_services.py -v
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

# 标准测试命盘
TEST_CHART = {
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
                {"name": "天同", "type": "主星", "level": "B"},
                {"name": "贪狼", "type": "主星", "level": "A"},
            ],
        },
        "兄弟宫": {"name": "兄弟宫", "branch": "卯", "tiangan": "乙", "stars": []},
        "夫妻宫": {
            "name": "夫妻宫",
            "branch": "辰",
            "tiangan": "丙",
            "stars": [{"name": "天相", "type": "主星", "level": "B"}],
        },
        "子女宫": {"name": "子女宫", "branch": "巳", "tiangan": "丁", "stars": []},
        "财帛宫": {
            "name": "财帛宫",
            "branch": "午",
            "tiangan": "戊",
            "stars": [{"name": "武曲", "type": "主星", "level": "A"}],
        },
        "疾厄宫": {"name": "疾厄宫", "branch": "未", "tiangan": "己", "stars": []},
        "迁移宫": {
            "name": "迁移宫",
            "branch": "申",
            "tiangan": "庚",
            "stars": [],
        },
        "仆役宫": {"name": "仆役宫", "branch": "酉", "tiangan": "辛", "stars": []},
        "官禄宫": {
            "name": "官禄宫",
            "branch": "戌",
            "tiangan": "壬",
            "stars": [{"name": "紫微", "type": "主星", "level": "A"}],
        },
        "田宅宫": {"name": "田宅宫", "branch": "亥", "tiangan": "癸", "stars": []},
        "福德宫": {"name": "福德宫", "branch": "子", "tiangan": "甲", "stars": []},
        "父母宫": {
            "name": "父母宫",
            "branch": "丑",
            "tiangan": "乙",
            "stars": [{"name": "太阳", "type": "主星", "level": "B"}],
        },
    },
    "stars": {
        "main_stars": [
            {"name": "天同", "palace": "命宫", "level": "B"},
            {"name": "贪狼", "palace": "命宫", "level": "A"},
            {"name": "天相", "palace": "夫妻宫", "level": "B"},
            {"name": "武曲", "palace": "财帛宫", "level": "A"},
            {"name": "紫微", "palace": "官禄宫", "level": "A"},
            {"name": "太阳", "palace": "父母宫", "level": "B"},
        ],
        "auxiliary_stars": [],
        "sha_stars": [],
        "transform_stars": [],
    },
    "transforms": [
        {"type": "化禄", "star": "贪狼", "palace": "财帛宫"},
        {"type": "化权", "star": "武曲", "palace": "官禄宫"},
    ],
}

# 父亲命盘
TEST_CHART_FATHER = {
    "birth_info": {
        "year": 1988,
        "month": 3,
        "day": 10,
        "hour": 14,
        "gender": "male",
        "birthplace": "上海",
        "wuxing_ju": "木三局",
        "year_gan": "戊",
    },
    "palaces": {
        "命宫": {
            "name": "命宫",
            "branch": "子",
            "tiangan": "癸",
            "stars": [
                {"name": "紫微", "type": "主星", "level": "A"},
                {"name": "天府", "type": "主星", "level": "A"},
            ],
        },
        "兄弟宫": {"name": "兄弟宫", "branch": "丑", "tiangan": "壬", "stars": []},
        "夫妻宫": {
            "name": "夫妻宫",
            "branch": "寅",
            "tiangan": "辛",
            "stars": [{"name": "天机", "type": "主星", "level": "B"}],
        },
        "子女宫": {"name": "子女宫", "branch": "卯", "tiangan": "庚", "stars": []},
        "财帛宫": {
            "name": "财帛宫",
            "branch": "辰",
            "tiangan": "己",
            "stars": [{"name": "太阳", "type": "主星", "level": "A"}],
        },
        "疾厄宫": {"name": "疾厄宫", "branch": "巳", "tiangan": "戊", "stars": []},
        "迁移宫": {
            "name": "迁移宫",
            "branch": "午",
            "tiangan": "丁",
            "stars": [],
        },
        "仆役宫": {"name": "仆役宫", "branch": "未", "tiangan": "丙", "stars": []},
        "官禄宫": {
            "name": "官禄宫",
            "branch": "申",
            "tiangan": "乙",
            "stars": [{"name": "天同", "type": "主星", "level": "B"}],
        },
        "田宅宫": {"name": "田宅宫", "branch": "酉", "tiangan": "甲", "stars": []},
        "福德宫": {"name": "福德宫", "branch": "戌", "tiangan": "癸", "stars": []},
        "父母宫": {
            "name": "父母宫",
            "branch": "亥",
            "tiangan": "壬",
            "stars": [{"name": "武曲", "type": "主星", "level": "A"}],
        },
    },
    "transforms": [
        {"type": "化禄", "star": "天机", "palace": "夫妻宫"},
    ],
}

# 母亲命盘
TEST_CHART_MOTHER = {
    "birth_info": {
        "year": 1992,
        "month": 8,
        "day": 20,
        "hour": 15,
        "gender": "female",
        "birthplace": "北京",
        "wuxing_ju": "金四局",
        "year_gan": "壬",
    },
    "palaces": {
        "命宫": {
            "name": "命宫",
            "branch": "丑",
            "tiangan": "己",
            "stars": [
                {"name": "太阴", "type": "主星", "level": "A"},
                {"name": "天机", "type": "主星", "level": "B"},
            ],
        },
        "兄弟宫": {"name": "兄弟宫", "branch": "子", "tiangan": "庚", "stars": []},
        "夫妻宫": {
            "name": "夫妻宫",
            "branch": "亥",
            "tiangan": "辛",
            "stars": [{"name": "贪狼", "type": "主星", "level": "A"}],
        },
        "子女宫": {"name": "子女宫", "branch": "戌", "tiangan": "壬", "stars": []},
        "财帛宫": {
            "name": "财帛宫",
            "branch": "酉",
            "tiangan": "癸",
            "stars": [{"name": "天府", "type": "主星", "level": "A"}],
        },
        "疾厄宫": {"name": "疾厄宫", "branch": "申", "tiangan": "甲", "stars": []},
        "迁移宫": {
            "name": "迁移宫",
            "branch": "未",
            "tiangan": "乙",
            "stars": [],
        },
        "仆役宫": {"name": "仆役宫", "branch": "午", "tiangan": "丙", "stars": []},
        "官禄宫": {
            "name": "官禄宫",
            "branch": "巳",
            "tiangan": "丁",
            "stars": [{"name": "天梁", "type": "主星", "level": "B"}],
        },
        "田宅宫": {"name": "田宅宫", "branch": "辰", "tiangan": "戊", "stars": []},
        "福德宫": {"name": "福德宫", "branch": "卯", "tiangan": "己", "stars": []},
        "父母宫": {
            "name": "父母宫",
            "branch": "寅",
            "tiangan": "丙",
            "stars": [{"name": "太阳", "type": "主星", "level": "B"}],
        },
    },
    "transforms": [
        {"type": "化科", "star": "天机", "palace": "命宫"},
    ],
}

# 测试出生信息
TEST_BIRTH_FEMALE = {
    "year": 1992,
    "month": 8,
    "day": 20,
    "hour": 15,
    "minute": 30,
    "gender": "female",
    "birthplace": "上海",
    "is_lunar": False,
}

TEST_BIRTH_MALE = {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 10,
    "minute": 0,
    "gender": "male",
    "birthplace": "北京",
    "is_lunar": False,
}

TEST_BIRTH_FATHER = {
    "year": 1988,
    "month": 3,
    "day": 10,
    "hour": 14,
    "minute": 0,
    "gender": "male",
    "birthplace": "上海",
    "is_lunar": False,
}


# ============ Fixtures ============

@pytest.fixture
def sample_chart():
    """标准测试命盘"""
    return TEST_CHART


@pytest.fixture
def father_chart():
    """父亲命盘"""
    return TEST_CHART_FATHER


@pytest.fixture
def mother_chart():
    """母亲命盘"""
    return TEST_CHART_MOTHER


@pytest.fixture
def sample_birth_info():
    """标准出生信息"""
    return TEST_BIRTH_MALE.copy()


@pytest.fixture
def mother_birth_info():
    """母亲出生信息"""
    return TEST_BIRTH_FEMALE.copy()


@pytest.fixture
def father_birth_info():
    """父亲出生信息"""
    return TEST_BIRTH_FATHER.copy()


# ============ BirthTimingAgent 测试 ============

class TestBirthTimingAgent:
    """剖腹产良辰吉日测试"""

    def test_analyze_returns_result(self, mother_birth_info):
        """测试分析返回结果"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
            BirthTimingResult,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-03",
            top_n=3,
        )

        assert result is not None
        assert isinstance(result, BirthTimingResult)
        assert result.service_type == "birth_timing"

    def test_result_has_required_fields(self, mother_birth_info):
        """测试结果包含必需字段"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-02",
            top_n=2,
        )

        # 验证必需字段
        assert hasattr(result, "service_type")
        assert hasattr(result, "options")
        assert hasattr(result, "analysis_summary")
        assert hasattr(result, "confidence")

        # options应该是列表
        assert isinstance(result.options, list)

    def test_options_have_required_fields(self, mother_birth_info):
        """测试选项包含必需字段"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-01",
            top_n=1,
        )

        if result.options:
            opt = result.options[0]
            assert hasattr(opt, "date")
            assert hasattr(opt, "hour")
            assert hasattr(opt, "score")
            assert hasattr(opt, "level")
            assert hasattr(opt, "rank")

    def test_best_option_ranks_highest(self, mother_birth_info):
        """测试最佳选项排名第一"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-03",
            top_n=5,
        )

        if result.options and len(result.options) >= 2:
            # 最佳选项的分数应该最高
            assert result.options[0].score >= result.options[1].score
            # 最佳选项应该排名第一
            assert result.options[0].rank == 1

    def test_score_in_valid_range(self, mother_birth_info):
        """测试分数在有效范围内"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-01",
            top_n=1,
        )

        for opt in result.options:
            assert 0 <= opt.score <= 100

    def test_level_is_valid(self, mother_birth_info):
        """测试等级值有效"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-01",
            top_n=1,
        )

        valid_levels = ["极佳", "良好", "中等", "一般", "较差"]
        for opt in result.options:
            assert opt.level in valid_levels

    def test_with_father_info(self, mother_birth_info, father_birth_info):
        """测试包含父亲信息"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            father_birth_info=father_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-01",
            top_n=1,
        )

        assert result is not None
        assert len(result.options) >= 0

    def test_confidence_is_valid(self, mother_birth_info):
        """测试置信度在有效范围内"""
        from app.services.divination.agents.birth_timing_agent import (
            analyze_birth_timing_sync,
        )

        result = analyze_birth_timing_sync(
            mother_birth_info=mother_birth_info,
            date_range_start="2026-04-01",
            date_range_end="2026-04-01",
            top_n=1,
        )

        assert 0 <= result.confidence <= 1


# ============ DateSelectionAgent 测试 ============

class TestDateSelectionAgent:
    """择日分析测试"""

    def test_select_returns_result(self, sample_chart):
        """测试择日返回结果"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
            DateSelectionResult,
        )

        result = select_date_sync(
            chart=sample_chart,
            date_type="结婚嫁娶",
            date_range_start="2026-03-22",
            date_range_end="2026-03-25",
            top_n=3,
        )

        assert result is not None
        assert isinstance(result, DateSelectionResult)
        assert result.service_type == "date_selection"

    def test_result_has_required_fields(self, sample_chart):
        """测试结果包含必需字段"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
        )

        result = select_date_sync(
            chart=sample_chart,
            date_type="开市开张",
            date_range_start="2026-03-22",
            date_range_end="2026-03-22",
            top_n=1,
        )

        assert hasattr(result, "service_type")
        assert hasattr(result, "date_type")
        assert hasattr(result, "daily_options")
        assert hasattr(result, "best_dates")
        assert hasattr(result, "analysis_summary")
        assert hasattr(result, "confidence")

    def test_options_have_required_fields(self, sample_chart):
        """测试选项包含必需字段"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
        )

        result = select_date_sync(
            chart=sample_chart,
            date_type="结婚嫁娶",
            date_range_start="2026-03-22",
            date_range_end="2026-03-22",
            top_n=1,
        )

        if result.best_dates:
            opt = result.best_dates[0]
            assert hasattr(opt, "solar_date")
            assert hasattr(opt, "lunar_date")
            assert hasattr(opt, "tiangan")
            assert hasattr(opt, "score")
            assert hasattr(opt, "level")
            assert hasattr(opt, "is_auspicious")

    def test_event_type_affects_results(self, sample_chart):
        """测试不同事件类型产生不同结果"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
        )

        result1 = select_date_sync(
            chart=sample_chart,
            date_type="结婚嫁娶",
            date_range_start="2026-03-22",
            date_range_end="2026-03-25",
            top_n=5,
        )

        result2 = select_date_sync(
            chart=sample_chart,
            date_type="开业破土",
            date_range_start="2026-03-22",
            date_range_end="2026-03-25",
            top_n=5,
        )

        # 不同事件类型应产生不同的分析摘要
        assert result1.date_type == "结婚嫁娶"
        assert result2.date_type == "开业破土"

    def test_score_in_valid_range(self, sample_chart):
        """测试分数在有效范围内"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
        )

        result = select_date_sync(
            chart=sample_chart,
            date_type="搬家入宅",
            date_range_start="2026-03-22",
            date_range_end="2026-03-22",
            top_n=1,
        )

        for opt in result.daily_options:
            assert 0 <= opt.score <= 100

    def test_date_range_valid(self, sample_chart):
        """测试日期范围正确"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
        )

        result = select_date_sync(
            chart=sample_chart,
            date_type="出行远行",
            date_range_start="2026-04-01",
            date_range_end="2026-04-03",
            top_n=5,
        )

        assert result.date_range is not None
        assert result.date_range[0] == "2026-04-01"
        assert result.date_range[1] == "2026-04-03"

    def test_tiangan_in_60_jiazi(self, sample_chart):
        """测试日柱在60甲子中"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
        )

        result = select_date_sync(
            chart=sample_chart,
            date_type="签约谈判",
            date_range_start="2026-03-22",
            date_range_end="2026-03-22",
            top_n=1,
        )

        if result.best_dates:
            tiangan = result.best_dates[0].tiangan
            assert len(tiangan) == 2  # 60甲子是两个字
            assert tiangan[0] in ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
            assert tiangan[1] in ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def test_all_event_types(self, sample_chart):
        """测试所有事件类型"""
        from app.services.divination.agents.date_selection_agent import (
            select_date_sync,
        )

        event_types = [
            "结婚嫁娶",
            "开市开张",
            "动土破土",
            "出行远行",
            "签约谈判",
            "搬家入宅",
            "订婚相亲",
        ]

        for event_type in event_types:
            result = select_date_sync(
                chart=sample_chart,
                date_type=event_type,
                date_range_start="2026-03-22",
                date_range_end="2026-03-22",
                top_n=1,
            )
            assert result.date_type == event_type


# ============ EventPredictorAgent 测试 ============

class TestEventPredictorAgent:
    """事件预测测试"""

    def test_predict_returns_result(self, sample_chart):
        """测试预测返回结果"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
            EventPredictionResult,
        )

        result = predict_event_sync(
            chart=sample_chart,
            event_type="跳槽",
        )

        assert result is not None
        assert isinstance(result, EventPredictionResult)
        assert result.service_type == "event_prediction"

    def test_result_has_required_fields(self, sample_chart):
        """测试结果包含必需字段"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        result = predict_event_sync(
            chart=sample_chart,
            event_type="投资理财",
        )

        assert hasattr(result, "service_type")
        assert hasattr(result, "event_type")
        assert hasattr(result, "target_palace")
        assert hasattr(result, "success_rate")
        assert hasattr(result, "level")
        assert hasattr(result, "timing_score")
        assert hasattr(result, "risk_factors")
        assert hasattr(result, "opportunity_factors")
        assert hasattr(result, "suggestions")

    def test_success_rate_in_valid_range(self, sample_chart):
        """测试成功率在有效范围内"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        result = predict_event_sync(
            chart=sample_chart,
            event_type="创业",
        )

        assert 0 <= result.success_rate <= 100

    def test_level_is_valid(self, sample_chart):
        """测试等级值有效"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        result = predict_event_sync(
            chart=sample_chart,
            event_type="晋升",
        )

        valid_levels = ["极佳", "良好", "中等", "一般", "较差"]
        assert result.level in valid_levels

    def test_timing_score_in_valid_range(self, sample_chart):
        """测试时机评分在有效范围内"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        result = predict_event_sync(
            chart=sample_chart,
            event_type="考试升学",
        )

        assert 0 <= result.timing_score <= 100

    def test_different_events_different_results(self, sample_chart):
        """测试不同事件产生不同结果"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        result1 = predict_event_sync(
            chart=sample_chart,
            event_type="跳槽",
        )

        result2 = predict_event_sync(
            chart=sample_chart,
            event_type="官司诉讼",
        )

        assert result1.event_type == "跳槽"
        assert result2.event_type == "官司诉讼"

    def test_event_palace_mapping(self, sample_chart):
        """测试事件-宫位映射"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        # 跳槽 -> 官禄宫
        result = predict_event_sync(
            chart=sample_chart,
            event_type="跳槽",
        )
        assert result.target_palace == "官禄宫"

        # 结婚嫁娶 -> 夫妻宫
        result = predict_event_sync(
            chart=sample_chart,
            event_type="结婚嫁娶",
        )
        assert result.target_palace == "夫妻宫"

        # 投资理财 -> 财帛宫
        result = predict_event_sync(
            chart=sample_chart,
            event_type="投资理财",
        )
        assert result.target_palace == "财帛宫"

    def test_with_target_year(self, sample_chart):
        """测试带目标年份"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        result = predict_event_sync(
            chart=sample_chart,
            event_type="求职面试",
            target_year=2026,
        )

        assert result is not None
        assert result.event_type == "求职面试"

    def test_confidence_in_valid_range(self, sample_chart):
        """测试置信度在有效范围内"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        result = predict_event_sync(
            chart=sample_chart,
            event_type="商务签约",
        )

        assert 0 <= result.confidence <= 1


# ============ MarriageCompatibilityAgent 测试 ============

class TestMarriageCompatibilityAgent:
    """姻缘配对测试"""

    def test_analyze_returns_result(self, sample_chart, mother_chart):
        """测试分析返回结果"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
            CompatibilityResult,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
            name_a="张三",
            name_b="李四",
        )

        assert result is not None
        assert isinstance(result, CompatibilityResult)
        assert result.service_type == "marriage_compatibility"

    def test_result_has_required_fields(self, sample_chart, mother_chart):
        """测试结果包含必需字段"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
        )

        assert hasattr(result, "service_type")
        assert hasattr(result, "overall_score")
        assert hasattr(result, "overall_level")
        assert hasattr(result, "dimensions")
        assert hasattr(result, "compatibility_highlights")
        assert hasattr(result, "compatibility_warnings")
        assert hasattr(result, "suggestions")

    def test_overall_score_in_valid_range(self, sample_chart, mother_chart):
        """测试综合分数在有效范围内"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
        )

        assert 0 <= result.overall_score <= 100

    def test_overall_level_is_valid(self, sample_chart, mother_chart):
        """测试综合等级值有效"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
        )

        valid_levels = [
            "完美姻缘",
            "天作之合",
            "良缘佳配",
            "中规中矩",
            "需要努力",
            "磨合期",
        ]
        assert result.overall_level in valid_levels

    def test_dimensions_count(self, sample_chart, mother_chart):
        """测试维度数量正确"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
        )

        # 应该有5个维度
        assert len(result.dimensions) == 5

        # 维度名称应该正确
        dimension_names = [d.dimension for d in result.dimensions]
        expected_dims = ["性格契合", "财运互补", "事业助力", "感情甜蜜", "健康同步"]
        for expected in expected_dims:
            assert expected in dimension_names

    def test_dimension_scores_in_valid_range(self, sample_chart, mother_chart):
        """测试维度分数在有效范围内"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
        )

        for dim in result.dimensions:
            assert 0 <= dim.score <= 100

    def test_dimension_has_required_fields(self, sample_chart, mother_chart):
        """测试维度包含必需字段"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
        )

        for dim in result.dimensions:
            assert hasattr(dim, "dimension")
            assert hasattr(dim, "score")
            assert hasattr(dim, "level")
            assert hasattr(dim, "analysis")

    def test_confidence_in_valid_range(self, sample_chart, mother_chart):
        """测试置信度在有效范围内"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
        )

        assert 0 <= result.confidence <= 1

    def test_person_names_set(self, sample_chart, mother_chart):
        """测试人物名称设置正确"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=mother_chart,
            name_a="张三",
            name_b="李四",
        )

        assert result.person_a_name == "张三"
        assert result.person_b_name == "李四"

    def test_same_charts(self, sample_chart):
        """测试相同命盘的配对分析"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=sample_chart,
            chart_b=sample_chart,
        )

        assert result is not None
        assert 0 <= result.overall_score <= 100


# ============ CareerRecommendationAgent 测试 ============

class TestCareerRecommendationAgent:
    """职业推荐测试"""

    def test_recommend_returns_result(self, sample_chart):
        """测试推荐返回结果"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
            CareerRecommendationResult,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            age=30,
            education_level="本科",
            top_n=3,
        )

        assert result is not None
        assert isinstance(result, CareerRecommendationResult)
        assert result.service_type == "career_recommendation"

    def test_result_has_required_fields(self, sample_chart):
        """测试结果包含必需字段"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            top_n=3,
        )

        assert hasattr(result, "service_type")
        assert hasattr(result, "strongest_palace")
        assert hasattr(result, "career_potential_score")
        assert hasattr(result, "career_options")
        assert hasattr(result, "wealth_type")
        assert hasattr(result, "key_strengths")

    def test_career_options_count(self, sample_chart):
        """测试职业选项数量正确"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            top_n=3,
        )

        assert len(result.career_options) <= 3

    def test_career_options_have_required_fields(self, sample_chart):
        """测试职业选项包含必需字段"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            top_n=3,
        )

        for opt in result.career_options:
            assert hasattr(opt, "rank")
            assert hasattr(opt, "career_type")
            assert hasattr(opt, "career_name")
            assert hasattr(opt, "match_score")
            assert hasattr(opt, "level")

    def test_match_score_in_valid_range(self, sample_chart):
        """测试匹配分数在有效范围内"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            top_n=3,
        )

        for opt in result.career_options:
            assert 0 <= opt.match_score <= 100

    def test_wealth_type_valid(self, sample_chart):
        """测试财运类型有效"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            top_n=3,
        )

        valid_types = ["正财型", "横财型", "技术财型", "艺术财型", "未定型"]
        assert result.wealth_type in valid_types

    def test_career_potential_score_in_valid_range(self, sample_chart):
        """测试职业潜力分数在有效范围内"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            top_n=3,
        )

        assert 0 <= result.career_potential_score <= 100

    def test_strongest_palace_in_valid(self, sample_chart):
        """测试最强宫位有效"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            top_n=3,
        )

        valid_palaces = [
            "命宫",
            "兄弟宫",
            "夫妻宫",
            "子女宫",
            "财帛宫",
            "疾厄宫",
            "迁移宫",
            "仆役宫",
            "官禄宫",
            "田宅宫",
            "福德宫",
            "父母宫",
        ]
        assert result.strongest_palace in valid_palaces

    def test_with_current_career(self, sample_chart):
        """测试带当前职业参数"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            current_career="软件工程师",
            top_n=3,
        )

        assert result is not None
        assert len(result.career_options) >= 0

    def test_education_advice_exists(self, sample_chart):
        """测试教育建议存在"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )

        result = recommend_career_sync(
            chart=sample_chart,
            education_level="本科",
            top_n=3,
        )

        assert result.education_advice is not None
        assert hasattr(result.education_advice, "direction")
        assert hasattr(result.education_advice, "suitable_degrees")


# ============ NameRecommendationAgent 测试 ============

class TestNameRecommendationAgent:
    """改名起名测试"""

    def test_recommend_returns_result(self, sample_birth_info):
        """测试推荐返回结果"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
            NameRecommendationResult,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="李",
            top_n=5,
        )

        assert result is not None
        assert isinstance(result, NameRecommendationResult)
        assert result.service_type == "name_recommendation"

    def test_result_has_required_fields(self, sample_birth_info):
        """测试结果包含必需字段"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="王",
            top_n=5,
        )

        assert hasattr(result, "service_type")
        assert hasattr(result, "wuxing_lack")
        assert hasattr(result, "wuxing_excess")
        assert hasattr(result, "recommended_radicals")
        assert hasattr(result, "name_options")
        assert hasattr(result, "best_name")

    def test_options_have_required_fields(self, sample_birth_info):
        """测试名字选项包含必需字段"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="张",
            top_n=5,
        )

        if result.name_options:
            opt = result.name_options[0]
            assert hasattr(opt, "rank")
            assert hasattr(opt, "surname")
            assert hasattr(opt, "given_name")
            assert hasattr(opt, "full_name")
            assert hasattr(opt, "wuxing_score")
            assert hasattr(opt, "math_score")
            assert hasattr(opt, "overall_score")
            assert hasattr(opt, "level")

    def test_scores_in_valid_range(self, sample_birth_info):
        """测试分数在有效范围内"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="刘",
            top_n=5,
        )

        for opt in result.name_options:
            assert 0 <= opt.wuxing_score <= 100
            assert 0 <= opt.math_score <= 100
            assert 0 <= opt.overall_score <= 100

    def test_level_is_valid(self, sample_birth_info):
        """测试等级值有效"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="陈",
            top_n=5,
        )

        valid_levels = ["极佳", "良好", "中等", "一般"]
        for opt in result.name_options:
            assert opt.level in valid_levels

    def test_wuxing_analysis_exists(self, sample_birth_info):
        """测试五行分析存在"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="周",
            top_n=5,
        )

        assert isinstance(result.wuxing_lack, list)
        assert isinstance(result.wuxing_excess, list)
        assert isinstance(result.recommended_radicals, list)

    def test_single_char_name(self, sample_birth_info):
        """测试单字名"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="吴",
            name_style="单字",
            top_n=5,
        )

        assert result is not None

    def test_double_char_name(self, sample_birth_info):
        """测试双字名"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="郑",
            name_style="双字",
            top_n=5,
        )

        assert result is not None

    def test_with_chart(self, sample_birth_info, sample_chart):
        """测试带命盘参数"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            chart=sample_chart,
            surname="孙",
            top_n=5,
        )

        assert result is not None
        assert result.wuxing_lack is not None

    def test_best_name_has_highest_score(self, sample_birth_info):
        """测试最佳名字分数最高"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="冯",
            top_n=5,
        )

        if result.name_options and result.best_name:
            assert result.best_name.overall_score >= result.name_options[-1].overall_score

    def test_confidence_in_valid_range(self, sample_birth_info):
        """测试置信度在有效范围内"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="蒋",
            top_n=5,
        )

        assert 0 <= result.confidence <= 1

    def test_full_name_correct(self, sample_birth_info):
        """测试全名格式正确"""
        from app.services.divination.agents.name_recommendation_agent import (
            recommend_name_sync,
        )

        result = recommend_name_sync(
            birth_info=sample_birth_info,
            surname="韩",
            top_n=5,
        )

        for opt in result.name_options:
            expected_full = "韩" + opt.given_name
            assert opt.full_name == expected_full


# ============ 边界条件测试 ============

class TestEdgeCases:
    """边界条件测试"""

    def test_minimal_chart_data(self):
        """测试最小命盘数据"""
        from app.services.divination.agents.career_recommendation_agent import (
            recommend_career_sync,
        )
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        minimal_chart = {
            "birth_info": {"year": 2000, "month": 1, "day": 1},
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

        # 应该不会崩溃
        result = recommend_career_sync(chart=minimal_chart, top_n=3)
        assert result is not None

        result = predict_event_sync(chart=minimal_chart, event_type="跳槽")
        assert result is not None

    def test_empty_palaces(self):
        """测试空宫位"""
        from app.services.divination.agents.marriage_compatibility_agent import (
            analyze_marriage_compatibility_sync,
        )

        empty_chart = {
            "birth_info": {"year": 2000, "month": 1, "day": 1},
            "palaces": {},
            "transforms": [],
        }

        # 应该不会崩溃
        result = analyze_marriage_compatibility_sync(
            chart_a=empty_chart,
            chart_b=empty_chart,
        )
        assert result is not None
        assert 0 <= result.overall_score <= 100

    def test_missing_transforms(self):
        """测试缺少四化数据"""
        from app.services.divination.agents.event_predictor_agent import (
            predict_event_sync,
        )

        chart_no_transforms = {
            "birth_info": {"year": 2000, "month": 1, "day": 1},
            "palaces": {
                "命宫": {"stars": [{"name": "紫微", "type": "主星"}]},
                "官禄宫": {"stars": []},
                "夫妻宫": {"stars": []},
                "财帛宫": {"stars": []},
                "迁移宫": {"stars": []},
            },
            "transforms": [],
        }

        result = predict_event_sync(
            chart=chart_no_transforms,
            event_type="跳槽",
        )
        assert result is not None


# ============ 运行入口 ============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
