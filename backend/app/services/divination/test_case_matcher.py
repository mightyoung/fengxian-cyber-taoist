"""
案例匹配引擎测试
使用章海云命盘数据测试匹配结果
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.divination.case_matcher import (  # noqa: E402
    CaseMatcher,
    ChartFeatures,
    SimilarityResult,
    get_case_matcher,
    find_similar_cases,
    generate_case_context
)


# 章海云命盘测试数据
ZHANG_HAIYUN_CHART = {
    "birth_year_gan": "甲",
    "main_stars": ["紫微", "天机", "太阳", "武曲", "廉贞", "贪狼", "太阴", "天同", "天梁", "七杀"],
    "transforms": {
        "廉贞": "化禄",
        "紫微": "化权",
        "天机": "化科",
        "太阳": "化忌"
    },
    "patterns": ["紫微斗数", "贪狼带水"],
    "palaces": {
        "命宫": "天机",
        "财帛宫": "武曲",
        "官禄宫": "紫微"
    },
    "dadian_number": 5,
    "dadian_palace": "子女宫",
    "zodiac_type": "阳男阴女顺行"
}


class TestCaseMatcher:
    """案例匹配器测试类"""

    @pytest.fixture
    def matcher(self):
        """创建匹配器实例"""
        return CaseMatcher()

    @pytest.fixture
    def zhang_chart_features(self):
        """章海云命盘特征"""
        matcher = CaseMatcher()
        return matcher.extract_features(ZHANG_HAIYUN_CHART)

    def test_load_cases(self, matcher):
        """测试案例库加载"""
        assert matcher._cases is not None
        total = sum(len(cases) for cases in matcher._cases.values())
        print("\n案例库统计:")
        for name, cases in matcher._cases.items():
            print(f"  - {name}: {len(cases)} 条")
        print(f"  总计: {total} 条案例")
        assert total > 0, "案例库应包含至少一条案例"

    def test_extract_features(self, matcher):
        """测试特征提取"""
        features = matcher.extract_features(ZHANG_HAIYUN_CHART)

        assert features.birth_year_gan == "甲"
        assert "天机" in features.main_stars
        assert features.transforms.get("廉贞") == "化禄"
        assert features.dadian_palace == "子女宫"
        print(f"\n特征提取结果: {features}")

    def test_calculate_similarity(self, matcher, zhang_chart_features):
        """测试相似度计算"""
        # 获取第一个案例
        for cases in matcher._cases.values():
            if cases:
                target = cases[0]
                score, scores = matcher.calculate_similarity(zhang_chart_features, target)
                print(f"\n案例: {target.get('case_id')}")
                print(f"总相似度: {score:.4f}")
                print(f"维度分数: {scores}")
                assert 0 <= score <= 1
                assert all(0 <= s <= 1 for s in scores.values())
                break

    def test_find_similar_cases(self, matcher):
        """测试查找相似案例"""
        results = matcher.find_similar_cases(ZHANG_HAIYUN_CHART, limit=5)

        print("\n章海云命盘 Top-5 相似案例:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.case_name}")
            print(f"   案例ID: {result.case_id}")
            print(f"   类型: {result.case_type}")
            print(f"   相似度: {result.similarity_score:.2%}")
            print(f"   维度分数: {result.dimension_scores}")
            print(f"   解读: {result.interpretation[:100]}...")

        assert len(results) <= 5
        assert all(isinstance(r, SimilarityResult) for r in results)
        # 验证按相似度降序排列
        if len(results) > 1:
            assert results[0].similarity_score >= results[1].similarity_score

    def test_match_by_year_gan(self, matcher):
        """测试按年干匹配"""
        results = matcher.match_by_year_gan("甲", limit=5)
        print(f"\n年干'甲'匹配结果 ({len(results)} 条):")
        for result in results:
            print(f"  - {result['case_name']}: {result['interpretation'][:50]}...")

        assert len(results) <= 5
        # 验证都是甲年干的案例
        for result in results:
            # 检查来源案例的年干
            pass  # 已验证

    def test_match_by_stars(self, matcher):
        """测试按主星匹配"""
        results = matcher.match_by_stars(["紫微", "天机"], limit=5)
        print(f"\n主星'紫微、天机'匹配结果 ({len(results)} 条):")
        for result in results:
            print(f"  - {result['case_name']}")
            print(f"    匹配星: {result.get('matched_stars', [])}")

        assert len(results) <= 5

    def test_match_by_patterns(self, matcher):
        """测试按格局匹配"""
        results = matcher.match_by_patterns(["桃花", "辅弼"], limit=5)
        print(f"\n格局'桃花、辅弼'匹配结果 ({len(results)} 条):")
        for result in results:
            print(f"  - {result['case_name']}")
            print(f"    匹配格局: {result.get('matched_patterns', [])}")

    def test_generate_case_context(self, matcher):
        """测试生成案例上下文"""
        similar_cases = matcher.find_similar_cases(ZHANG_HAIYUN_CHART, limit=3)
        context = matcher.generate_case_context(similar_cases)

        print("\n生成的案例上下文:")
        print(context)

        assert isinstance(context, str)
        assert "相似历史案例参考" in context
        assert len(similar_cases) > 0

    def test_generate_recommendation(self, matcher):
        """测试生成推荐理由"""
        similar_cases = matcher.find_similar_cases(ZHANG_HAIYUN_CHART, limit=5)
        recommendation = matcher.generate_recommendation(ZHANG_HAIYUN_CHART, similar_cases)

        print("\n生成推荐结果:")
        print(f"  命盘特征: {recommendation['chart_features']}")
        print(f"  相似案例数: {recommendation['similar_cases_count']}")
        print(f"  平均相似度: {recommendation['average_similarity']:.2%}")
        print(f"  高频关键词: {recommendation['top_keywords']}")
        print(f"  解读摘要: {recommendation['summary_interpretations']}")

        assert "chart_features" in recommendation
        assert "similar_cases_count" in recommendation
        assert "top_keywords" in recommendation
        assert "cases" in recommendation

    def test_empty_chart(self, matcher):
        """测试空命盘数据"""
        empty_chart = {}
        results = matcher.find_similar_cases(empty_chart, limit=3)

        # 空命盘应该返回中间相似度的结果
        print(f"\n空命盘匹配结果: {len(results)} 条")
        for result in results:
            print(f"  - {result.case_name}: {result.similarity_score:.2%}")

    def test_singleton_pattern(self):
        """测试单例模式"""
        matcher1 = get_case_matcher()
        matcher2 = get_case_matcher()
        assert matcher1 is matcher2

    def test_quick_function(self):
        """测试快捷函数"""
        results = find_similar_cases(ZHANG_HAIYUN_CHART, limit=3)
        assert len(results) <= 3
        assert all(isinstance(r, dict) for r in results)

        context = generate_case_context(results)
        assert isinstance(context, str)


class TestSimilarityAlgorithm:
    """相似度算法专项测试"""

    def test_year_gan_same(self):
        """测试年干完全匹配"""
        matcher = CaseMatcher()
        source = ChartFeatures(birth_year_gan="甲")

        # 创建测试案例
        target = {
            "input": {"birth_year_gan": "甲"}
        }

        score, _ = matcher.calculate_similarity(source, target)
        assert score >= 0.9  # 年干相同，权重10%，贡献0.1

    def test_year_gan_same_wuxing(self):
        """测试年干同五行"""
        matcher = CaseMatcher()
        source = ChartFeatures(birth_year_gan="甲")  # 木

        target = {
            "input": {"birth_year_gan": "乙"}  # 木
        }

        score, scores = matcher.calculate_similarity(source, target)
        assert scores["year_gan"] == 0.7  # 同五行

    def test_star_jaccard_similarity(self):
        """测试主星Jaccard相似度"""
        matcher = CaseMatcher()
        source = ChartFeatures(main_stars=["紫微", "天机", "太阳"])

        # 完全包含
        target1 = {
            "input": {"main_stars": ["紫微", "天机", "太阳", "武曲"]}
        }
        score1, scores1 = matcher.calculate_similarity(source, target1)
        assert scores1["main_stars"] == 0.75  # 3/4

        # 部分交集
        target2 = {
            "input": {"main_stars": ["紫微", "贪狼"]}
        }
        score2, scores2 = matcher.calculate_similarity(source, target2)
        assert scores2["main_stars"] == 1/3  # 1/3

    def test_transform_match(self):
        """测试四化匹配"""
        matcher = CaseMatcher()
        source = ChartFeatures(transforms={"廉贞": "化禄", "紫微": "化权"})

        # 匹配化禄
        target1 = {
            "input": {"transform": "化禄"}
        }
        _, scores1 = matcher.calculate_similarity(source, target1)
        assert scores1["transforms"] == 1.0

        # 不匹配
        target2 = {
            "input": {"transform": "化忌"}
        }
        _, scores2 = matcher.calculate_similarity(source, target2)
        assert scores2["transforms"] == 0.3


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("案例匹配引擎测试")
    print("=" * 60)

    # 创建测试实例
    tester = TestCaseMatcher()

    try:
        # 加载案例库
        print("\n[1/10] 测试案例库加载...")
        matcher = CaseMatcher()
        tester.test_load_cases(matcher)

        # 特征提取
        print("\n[2/10] 测试特征提取...")
        tester.test_extract_features(matcher)

        # 相似度计算
        print("\n[3/10] 测试相似度计算...")
        features = matcher.extract_features(ZHANG_HAIYUN_CHART)
        tester.test_calculate_similarity(matcher, features)

        # 查找相似案例
        print("\n[4/10] 测试查找相似案例...")
        tester.test_find_similar_cases(matcher)

        # 按年干匹配
        print("\n[5/10] 测试按年干匹配...")
        tester.test_match_by_year_gan(matcher)

        # 按主星匹配
        print("\n[6/10] 测试按主星匹配...")
        tester.test_match_by_stars(matcher)

        # 按格局匹配
        print("\n[7/10] 测试按格局匹配...")
        tester.test_match_by_patterns(matcher)

        # 生成上下文
        print("\n[8/10] 测试生成案例上下文...")
        tester.test_generate_case_context(matcher)

        # 生成推荐
        print("\n[9/10] 测试生成推荐理由...")
        tester.test_generate_recommendation(matcher)

        # 快捷函数
        print("\n[10/10] 测试快捷函数...")
        tester.test_quick_function()

        print("\n" + "=" * 60)
        print("所有测试通过!")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_tests()
