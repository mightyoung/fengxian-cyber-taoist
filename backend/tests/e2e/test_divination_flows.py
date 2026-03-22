"""
E2E测试 - 紫微斗数完整流程测试

测试完整的用户流程:
1. 命盘生成
2. 星曜分析
3. 宫位分析
4. 格局分析
5. 四化分析
6. 运势分析
7. 综合报告生成

运行方式:
    pytest tests/e2e/test_divination_flows.py -v
"""

import pytest
import asyncio
import os
import sys

# 添加 backend 目录到 path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)


# ============ 测试数据 ============

SAMPLE_BIRTH_INFO = {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 10,
    "minute": 30,
    "gender": "male",
    "birthplace": "北京",
    "is_lunar": False
}


# ============ E2E 测试夹具 (Fixtures) ============

@pytest.fixture
def sample_birth_info():
    """标准出生信息"""
    return SAMPLE_BIRTH_INFO.copy()


@pytest.fixture
def birth_info_with_timezone():
    """带时区的出生信息"""
    return {
        **SAMPLE_BIRTH_INFO,
        "timezone": "Asia/Shanghai"
    }


# ============ 命盘生成测试 ============

class TestChartGeneration:
    """命盘生成流程测试"""

    def test_generate_chart_with_all_fields(self, sample_birth_info):
        """测试使用完整字段生成命盘"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=sample_birth_info["year"],
            month=sample_birth_info["month"],
            day=sample_birth_info["day"],
            hour=sample_birth_info["hour"],
            minute=sample_birth_info["minute"],
            gender=sample_birth_info["gender"],
            birthplace=sample_birth_info.get("birthplace", ""),
            is_lunar=sample_birth_info.get("is_lunar", False)
        )

        # 生成命盘
        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))

        # 验证命盘结构
        assert chart is not None
        assert chart.birth_info is not None
        assert chart.birth_info["year"] == 1990
        assert chart.birth_info["month"] == 5
        assert chart.birth_info["day"] == 15

    def test_generate_chart_minimal_fields(self):
        """测试使用最小字段生成命盘"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))

        assert chart is not None
        assert chart.birth_info is not None

    def test_chart_has_required_palaces(self):
        """测试命盘包含所有必需的宫位"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))

        # 验证十二宫位
        assert len(chart.palaces) == 12

        # 验证关键宫位存在
        required_palaces = [
            "命宫", "兄弟宫", "夫妻宫", "子女宫",
            "财帛宫", "疾厄宫", "迁移宫", "交友宫",
            "官禄宫", "田宅宫", "福德宫", "父母宫"
        ]

        for palace in required_palaces:
            assert palace in chart.palaces, f"Missing palace: {palace}"


# ============ 星曜分析测试 ============

class TestStarAnalysis:
    """星曜分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_stars_returns_structure(self, chart_data):
        """测试星曜分析返回正确结构"""
        from app.services.divination.agents import analyze_stars_sync

        result = analyze_stars_sync(chart_data)

        assert result is not None
        assert hasattr(result, "main_stars")
        assert hasattr(result, "auxiliary_stars")
        assert hasattr(result, "sha_stars")
        assert hasattr(result, "transform_stars")

    def test_analyze_stars_counts(self, chart_data):
        """测试星曜计数"""
        from app.services.divination.agents import analyze_stars_sync

        result = analyze_stars_sync(chart_data)

        assert result.total_stars_count > 0


# ============ 宫位分析测试 ============

class TestPalaceAnalysis:
    """宫位分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_palaces_returns_structure(self, chart_data):
        """测试宫位分析返回正确结构"""
        from app.services.divination.agents import analyze_palaces_sync

        result = analyze_palaces_sync(chart_data)

        assert result is not None
        assert hasattr(result, "palace_results")
        assert hasattr(result, "strongest_palace")
        assert hasattr(result, "weakest_palace")

    def test_palace_results_count(self, chart_data):
        """测试宫位结果数量"""
        from app.services.divination.agents import analyze_palaces_sync

        result = analyze_palaces_sync(chart_data)

        assert len(result.palace_results) == 12


# ============ 四化分析测试 ============

class TestTransformAnalysis:
    """四化分析测试"""

    def test_get_transform_for_甲(self):
        """测试甲年四化"""
        from app.services.divination.agents import get_transform

        result = get_transform("甲")

        assert result is not None
        assert result.year_stem == "甲"
        assert len(result.transforms) == 4
        # 甲年: 破军化禄, 廉贞化权, 太阳化科, 太阴化忌
        transform_types = {t.transform_type.value for t in result.transforms}
        assert "化禄" in transform_types
        assert "化权" in transform_types
        assert "化科" in transform_types
        assert "化忌" in transform_types

    def test_get_transform_for_乙(self):
        """测试乙年四化"""
        from app.services.divination.agents import get_transform

        result = get_transform("乙")

        assert result is not None
        assert result.year_stem == "乙"
        assert len(result.transforms) == 4

    def test_get_transform_all_stems(self):
        """测试所有年干的四化"""
        from app.services.divination.agents import get_transform

        stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

        for stem in stems:
            result = get_transform(stem)
            assert result is not None, f"Failed for stem: {stem}"
            assert result.year_stem == stem
            assert len(result.transforms) == 4


# ============ 格局分析测试 ============

class TestPatternAnalysis:
    """格局分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_patterns_returns_structure(self, chart_data):
        """测试格局分析返回正确结构"""
        from app.services.divination.agents import analyze_patterns

        palace_stars = {
            k: [s.get("name", "") for s in v.get("stars", [])]
            for k, v in chart_data.get("palaces", {}).items()
        }

        result = analyze_patterns(chart_data, palace_stars)

        assert result is not None
        assert hasattr(result, "patterns")
        assert hasattr(result, "auspicious_patterns")
        assert hasattr(result, "inauspicious_patterns")
        assert hasattr(result, "neutral_patterns")


# ============ 运势分析测试 ============

class TestTimingAnalysis:
    """运势分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_timing_agent_initialization(self, chart_data):
        """测试TimingAgent初始化"""
        from app.services.divination.agents import TimingAgent

        agent = TimingAgent(chart_data)

        assert agent is not None
        # TimingAgent doesn't store chart_data as attribute, just verify it can be created

    def test_calculate_major_fate(self, chart_data):
        """测试大限计算"""
        from app.services.divination.agents import TimingAgent

        agent = TimingAgent(chart_data)
        major_fate_list = agent.calculate_major_fate(30, 1990)  # 30岁, 2020年

        assert major_fate_list is not None
        assert isinstance(major_fate_list, list)
        assert len(major_fate_list) > 0
        # Each major_fate has description, palace, start_age, end_age
        first_fate = major_fate_list[0]
        assert hasattr(first_fate, "description")
        assert hasattr(first_fate, "palace")
        assert hasattr(first_fate, "start_age")
        assert hasattr(first_fate, "end_age")

    def test_calculate_year_fate(self, chart_data):
        """测试流年计算"""
        from app.services.divination.agents import TimingAgent

        agent = TimingAgent(chart_data)
        year_fate = agent.calculate_year_fate(2025, 1990)

        assert year_fate is not None
        assert hasattr(year_fate, "gan_zhi")
        assert hasattr(year_fate, "tai_sui_palace")


# ============ 综合报告测试 ============

class TestSynthesisReport:
    """综合报告生成测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    @pytest.fixture
    def analyses(self, chart_data):
        """生成所有分析结果"""
        from app.services.divination.agents import (
            analyze_stars_sync,
            analyze_palaces_sync,
            analyze_patterns,
            llm_analyze_transforms_sync,
            llm_analyze_timing_sync
        )

        palace_stars = {
            k: [s.get("name", "") for s in v.get("stars", [])]
            for k, v in chart_data.get("palaces", {}).items()
        }

        star_analysis = analyze_stars_sync(chart_data)
        palace_analysis = analyze_palaces_sync(chart_data)
        pattern_analysis = analyze_patterns(chart_data, palace_stars)
        transform_analysis = llm_analyze_transforms_sync(chart_data)
        timing_analysis = llm_analyze_timing_sync(chart_data)

        return {
            "star_analysis": star_analysis,
            "palace_analysis": palace_analysis,
            "pattern_analysis": pattern_analysis,
            "transform_analysis": transform_analysis,
            "timing_analysis": timing_analysis
        }

    def test_generate_markdown_report(self, chart_data, analyses):
        """测试生成Markdown报告"""
        from app.services.divination.agents import generate_markdown_report_sync

        report_bundle = generate_markdown_report_sync(
            chart_data=chart_data,
            star_analysis=analyses["star_analysis"],
            palace_analysis=analyses["palace_analysis"],
            pattern_analysis=analyses["pattern_analysis"],
            transform_analysis=analyses["transform_analysis"],
            timing_analysis=analyses["timing_analysis"],
            question="请分析我的命格"
        )

        assert report_bundle is not None
        assert hasattr(report_bundle, "main_report")
        assert hasattr(report_bundle, "sub_reports")
        assert len(report_bundle.main_report) > 0


# ============ 六十星系测试 ============

class TestSiyinLoader:
    """六十星系加载器测试"""

    def test_load_siyin_systems(self):
        """测试加载六十星系"""
        from app.services.divination.agents.siyin_loader import SiyinLoader

        loader = SiyinLoader()
        systems = loader.get_all_systems()

        assert systems is not None
        assert len(systems) > 0

    def test_get_system_by_id(self):
        """测试按ID获取星系统一"""
        from app.services.divination.agents.siyin_loader import SiyinLoader

        loader = SiyinLoader()

        # 获取第一个系统
        systems = loader.get_all_systems()
        if systems:
            first_system = systems[0]
            system_id = first_system.get("id")

            if system_id:
                result = loader.get_system_by_id(system_id)
                assert result is not None

    def test_find_systems_by_main_star(self):
        """测试按主星查找星系统一"""
        from app.services.divination.agents.siyin_loader import SiyinLoader

        loader = SiyinLoader()
        systems = loader.find_systems_by_main_star("紫微")

        # 紫微星可能存在或不存在，取决于数据
        assert isinstance(systems, list)

    def test_get_siyin_interpretation(self):
        """测试获取星曜组合解读"""
        from app.services.divination.agents.siyin_loader import SiyinLoader

        loader = SiyinLoader()
        result = loader.get_siyin_interpretation("紫微", ["贪狼"], "卯")

        assert result is not None
        assert "matched" in result
        assert isinstance(result["matched"], bool)


# ============ 健康分析测试 ============

class TestHealthAnalysis:
    """健康分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_health_returns_structure(self, chart_data):
        """测试健康分析返回正确结构"""
        from app.services.divination.agents import analyze_health_sync

        result = analyze_health_sync(chart_data)

        assert result is not None
        assert hasattr(result, "disease_palace_analysis")
        assert hasattr(result, "weak_body_parts")
        assert hasattr(result, "risk_factors")
        assert hasattr(result, "inherent_strength")
        assert hasattr(result, "current_health")


# ============ 财富分析测试 ============

class TestWealthAnalysis:
    """财富分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_wealth_returns_structure(self, chart_data):
        """测试财富分析返回正确结构"""
        from app.services.divination.agents import analyze_wealth_sync

        result = analyze_wealth_sync(chart_data, years=5)

        assert result is not None
        assert "wealth_level" in result or "wealth_score" in result


# ============ 事业分析测试 ============

class TestCareerAnalysis:
    """事业分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_career_returns_structure(self, chart_data):
        """测试事业分析返回正确结构"""
        from app.services.divination.agents import analyze_career_sync

        result = analyze_career_sync(chart_data)

        assert result is not None
        assert hasattr(result, "career_level") or hasattr(result, "career_score")


# ============ 姻缘分析测试 ============

class TestRelationshipAnalysis:
    """姻缘分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_relationship_returns_structure(self, chart_data):
        """测试姻缘分析返回正确结构"""
        from app.services.divination.agents import analyze_relationship_sync

        result = analyze_relationship_sync(chart_data)

        assert result is not None
        assert hasattr(result, "marriage_timing") or hasattr(result, "marriage_quality")


# ============ 学业分析测试 ============

class TestEducationAnalysis:
    """学业分析测试"""

    @pytest.fixture
    def chart_data(self):
        """生成命盘数据用于分析"""
        from app.services.divination.agents import ChartAgent, BirthInfo

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))
        return chart.to_dict()

    def test_analyze_education_returns_structure(self, chart_data):
        """测试学业分析返回正确结构"""
        from app.services.divination.agents import analyze_education_sync

        result = analyze_education_sync(chart_data)

        assert result is not None
        assert hasattr(result, "learning_ability") or hasattr(result, "learning_score")


# ============ 缓存装饰器测试 ============

class TestCacheDecorator:
    """缓存装饰器测试"""

    def test_cache_key_generation(self):
        """测试缓存键生成"""
        from app.services.divination.agents.cache_decorator import generate_cache_key

        key1 = generate_cache_key("chart123", "stars", {"param": "value"})
        key2 = generate_cache_key("chart123", "stars", {"param": "value"})
        key3 = generate_cache_key("chart123", "palaces", {"param": "value"})

        assert key1 == key2  # 相同参数应生成相同键
        assert key1 != key3  # 不同分析类型应生成不同键

    def test_cache_get_set(self):
        """测试缓存存取"""
        from app.services.divination.agents.cache_decorator import AnalysisCache

        cache = AnalysisCache(default_ttl=60)

        cache.set("test_key", {"data": "test_value"})
        result = cache.get("test_key")

        assert result is not None
        assert result["data"] == "test_value"

    def test_cache_expiration(self):
        """测试缓存过期"""
        from app.services.divination.agents.cache_decorator import AnalysisCache
        import time

        cache = AnalysisCache(default_ttl=1)  # 1秒过期

        cache.set("test_key", {"data": "test_value"})
        result1 = cache.get("test_key")
        assert result1 is not None

        time.sleep(1.5)  # 等待过期

        result2 = cache.get("test_key")
        assert result2 is None  # 应该已过期

    def test_cache_clear(self):
        """测试缓存清空"""
        from app.services.divination.agents.cache_decorator import AnalysisCache

        cache = AnalysisCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_invalidate_chart_cache(self):
        """测试命盘缓存失效"""
        from app.services.divination.agents.cache_decorator import (
            get_cache,
            generate_cache_key,
            invalidate_chart_cache
        )

        cache = get_cache()

        # 设置一些缓存
        cache.set(generate_cache_key("chart1", "stars", None), "value1")
        cache.set(generate_cache_key("chart1", "palaces", None), "value2")
        cache.set(generate_cache_key("chart2", "stars", None), "value3")

        # 只失效 chart1 的缓存
        deleted = invalidate_chart_cache("chart1")

        # chart1 的缓存应该被删除
        assert cache.get(generate_cache_key("chart1", "stars", None)) is None
        assert cache.get(generate_cache_key("chart1", "palaces", None)) is None

        # chart2 的缓存应该还在
        assert cache.get(generate_cache_key("chart2", "stars", None)) is not None


# ============ 运行入口 ============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
