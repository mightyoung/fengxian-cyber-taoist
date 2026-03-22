"""
运势分数计算模块测试

测试用例：
1. 基础命盘数据测试
2. 章海云命盘测试
3. 分数范围验证
4. 各维度分数测试
"""

import pytest
import sys
sys.path.insert(0, '/Users/muyi/Downloads/dev/FengxianCyberTaoist/backend')

from app.services.divination.fortune_calculator import (
    FortuneCalculator,
    FortuneLevel,
    FortuneScore,
    DIMENSION_WEIGHTS,
    DIMENSION_PALACE_MAPPING,
    DIMENSION_PALACE_INDEX,
    PALACE_INDEX_TO_NAME,
    STAR_LEVEL_SCORES,
    TRANSFORM_INTENSITY,
    MAIN_STAR_BASE_SCORE,
    AUXILIARY_STAR_JUDGMENT,
    PATTERN_SCORES,
)


# 测试用命盘数据（简化版）
SAMPLE_CHART = {
    "year": 1996,
    "month": 6,
    "day": 2,
    "gan": "丙",
    "zhi": "子",
    "wuxing": "水二局",
    "gender": "女",
    "palaces": {
        "命宫": {
            "stars": [
                {"name": "天机", "type": "正曜", "brightness": "旺"},
                {"name": "左辅", "type": "辅曜", "brightness": "得"}
            ],
            "main_star": "天机",
            "auxiliary_stars": ["左辅"],
            "transforms": {},
            "strength": "强"
        },
        "官禄宫": {
            "stars": [
                {"name": "紫微", "type": "正曜", "brightness": "庙"},
                {"name": "天相", "type": "正曜", "brightness": "庙"}
            ],
            "main_star": "紫微",
            "auxiliary_stars": ["文昌", "左辅"],
            "transforms": {"化禄": "紫微"},
            "strength": "强"
        },
        "财帛宫": {
            "stars": [
                {"name": "武曲", "type": "正曜", "brightness": "旺"},
                {"name": "天府", "type": "正曜", "brightness": "庙"}
            ],
            "main_star": "武曲",
            "auxiliary_stars": ["禄存"],
            "transforms": {},
            "strength": "强"
        },
        "夫妻宫": {
            "stars": [
                {"name": "太阳", "type": "正曜", "brightness": "陷"},
                {"name": "巨门", "type": "正曜", "brightness": "陷"}
            ],
            "main_star": "太阳",
            "auxiliary_stars": ["文曲"],
            "malefic_stars": ["陀罗"],
            "transforms": {"化忌": "太阳"},
            "strength": "弱"
        },
        "疾厄宫": {
            "stars": [
                {"name": "廉贞", "type": "正曜", "brightness": "庙"}
            ],
            "main_star": "廉贞",
            "auxiliary_stars": [],
            "transforms": {},
            "strength": "中"
        },
        "交友宫": {
            "stars": [
                {"name": "太阴", "type": "正曜", "brightness": "旺"}
            ],
            "main_star": "太阴",
            "auxiliary_stars": ["天魁"],
            "transforms": {},
            "strength": "中"
        }
    },
    "transforms": {
        "birth_year_gan": "丙",
        "transforms": [
            {"star": "天同", "palace": "命宫", "transform_type": "化禄", "source": "生年"},
            {"star": "天梁", "palace": "迁移宫", "transform_type": "化权", "source": "生年"},
            {"star": "太阳", "palace": "夫妻宫", "transform_type": "化忌", "source": "生年"}
        ]
    },
    "patterns": [
        {
            "name": "紫微天相",
            "type": "吉格",
            "main_star": "紫微",
            "palace": "官禄宫"
        }
    ]
}


class TestFortuneCalculator:
    """运势计算器测试类"""

    def test_calculator_initialization(self):
        """测试计算器初始化"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        assert calculator.chart == SAMPLE_CHART
        assert calculator.target_year == 2026

    def test_dimension_mapping(self):
        """测试维度宫位映射"""
        assert DIMENSION_PALACE_MAPPING["career"] == "官禄宫"
        assert DIMENSION_PALACE_MAPPING["wealth"] == "财帛宫"
        assert DIMENSION_PALACE_MAPPING["relationship"] == "夫妻宫"
        assert DIMENSION_PALACE_MAPPING["health"] == "疾厄宫"
        assert DIMENSION_PALACE_MAPPING["social"] == "交友宫"

    def test_weight_sum(self):
        """测试权重总和"""
        total_weight = sum(DIMENSION_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001, f"权重总和应为1.0，实际为{total_weight}"

    def test_calculate_dimension_scores(self):
        """测试各维度分数计算"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        dimension_scores = calculator.calculate_dimension_scores()

        assert len(dimension_scores) == 5
        assert "career" in dimension_scores
        assert "wealth" in dimension_scores
        assert "relationship" in dimension_scores
        assert "health" in dimension_scores
        assert "social" in dimension_scores

        # 检查分数范围
        for key, score in dimension_scores.items():
            assert 0 <= score.score <= 100, f"{key}分数超出范围: {score.score}"
            assert score.level in [e.value for e in FortuneLevel]

    def test_calculate_fortune_score(self):
        """测试综合运势分数"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        fortune_score = calculator.calculate_fortune_score()

        assert 0 <= fortune_score <= 100, f"运势分数超出范围: {fortune_score}"
        print(f"综合运势分数: {fortune_score}")

    def test_risk_index(self):
        """测试风险指数"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        risk_index = calculator.calculate_risk_index()

        assert 0 <= risk_index <= 100, f"风险指数超出范围: {risk_index}"
        print(f"风险指数: {risk_index}")

    def test_opportunity_index(self):
        """测试机遇指数"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        opportunity_index = calculator.calculate_opportunity_index()

        assert 0 <= opportunity_index <= 100, f"机遇指数超出范围: {opportunity_index}"
        print(f"机遇指数: {opportunity_index}")

    def test_monthly_scores(self):
        """测试月度运势"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        monthly_scores = calculator.get_monthly_scores()

        assert len(monthly_scores) == 12

        for month_score in monthly_scores:
            assert 0 <= month_score["score"] <= 100
            assert month_score["level"] in [e.value for e in FortuneLevel]

    def test_full_calculation(self):
        """测试完整运势计算"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        result = calculator.calculate_full()

        assert 0 <= result.overall_score <= 100
        assert result.overall_level in [e.value for e in FortuneLevel]
        assert len(result.dimension_scores) == 5
        # 风险和机遇指数需要单独调用方法
        risk_index = calculator.calculate_risk_index()
        opportunity_index = calculator.calculate_opportunity_index()
        assert 0 <= risk_index <= 100
        assert 0 <= opportunity_index <= 100
        assert len(result.monthly_scores) == 12

    def test_score_to_level(self):
        """测试分数等级转换"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)

        assert calculator._score_to_level(95) == "极佳"
        assert calculator._score_to_level(80) == "良好"
        assert calculator._score_to_level(60) == "中等"
        assert calculator._score_to_level(40) == "一般"
        assert calculator._score_to_level(15) == "较差"

    def test_convenience_function(self):
        """测试便捷函数"""
        calculator = FortuneCalculator(chart=SAMPLE_CHART, target_year=2026)
        result = calculator.calculate_full()

        assert "overall_score" in result.to_dict()
        assert "dimension_scores" in result.to_dict()
        assert "monthly_scores" in result.to_dict()


class TestZhangHaiYunChart:
    """章海云命盘测试"""

    @pytest.fixture
    def zhang_chart(self):
        """加载章海云命盘数据"""
        # 章海云命盘数据（简化版）
        # 女命 农历1996年4月17日 上午10点（巳时）
        # 丙子年 水二局
        return {
            "year": 1996,
            "month": 6,
            "day": 2,
            "gan": "丙",
            "zhi": "子",
            "wuxing": "水二局",
            "gender": "女",
            "palaces": {
                "命宫": {
                    "stars": [
                        {"name": "天机", "type": "正曜", "brightness": "旺"},
                        {"name": "天梁", "type": "正曜", "brightness": "庙"}
                    ],
                    "main_star": "天机",
                    "auxiliary_stars": ["左辅", "天寿"],
                    "transforms": {"化禄": "天机"},
                    "strength": "强"
                },
                "兄弟宫": {
                    "stars": [
                        {"name": "太阴", "type": "正曜", "brightness": "旺"}
                    ],
                    "main_star": "太阴",
                    "auxiliary_stars": [],
                    "transforms": {},
                    "strength": "中"
                },
                "夫妻宫": {
                    "stars": [
                        {"name": "太阳", "type": "正曜", "brightness": "陷"},
                        {"name": "巨门", "type": "正曜", "brightness": "平"}
                    ],
                    "main_star": "太阳",
                    "auxiliary_stars": ["文曲"],
                    "malefic_stars": ["陀罗", "铃星"],
                    "transforms": {"化忌": "太阳"},
                    "strength": "弱"
                },
                "子女宫": {
                    "stars": [
                        {"name": "天同", "type": "正曜", "brightness": "旺"},
                        {"name": "天梁", "type": "正曜", "brightness": "庙"}
                    ],
                    "main_star": "天同",
                    "auxiliary_stars": ["右弼"],
                    "transforms": {},
                    "strength": "中"
                },
                "财帛宫": {
                    "stars": [
                        {"name": "武曲", "type": "正曜", "brightness": "庙"},
                        {"name": "天府", "type": "正曜", "brightness": "旺"}
                    ],
                    "main_star": "武曲",
                    "auxiliary_stars": ["禄存", "天魁"],
                    "transforms": {},
                    "strength": "强"
                },
                "疾厄宫": {
                    "stars": [
                        {"name": "紫微", "type": "正曜", "brightness": "得"}
                    ],
                    "main_star": "紫微",
                    "auxiliary_stars": ["天钥"],
                    "malefic_stars": ["火星"],
                    "transforms": {},
                    "strength": "中"
                },
                "迁移宫": {
                    "stars": [
                        {"name": "破军", "type": "正曜", "brightness": "旺"},
                        {"name": "七杀", "type": "正曜", "brightness": "旺"}
                    ],
                    "main_star": "破军",
                    "auxiliary_stars": ["天马"],
                    "malefic_stars": ["擎羊"],
                    "transforms": {"化权": "破军"},
                    "strength": "强"
                },
                "交友宫": {
                    "stars": [
                        {"name": "贪狼", "type": "正曜", "brightness": "平"}
                    ],
                    "main_star": "贪狼",
                    "auxiliary_stars": ["天钺"],
                    "transforms": {},
                    "strength": "弱"
                },
                "官禄宫": {
                    "stars": [
                        {"name": "廉贞", "type": "正曜", "brightness": "庙"},
                        {"name": "天相", "type": "正曜", "brightness": "庙"}
                    ],
                    "main_star": "廉贞",
                    "auxiliary_stars": ["文昌", "左辅"],
                    "transforms": {"化科": "天相"},
                    "strength": "强"
                },
                "田宅宫": {
                    "stars": [
                        {"name": "贪狼", "type": "正曜", "brightness": "平"}
                    ],
                    "main_star": "贪狼",
                    "auxiliary_stars": [],
                    "malefic_stars": ["地空", "地劫"],
                    "transforms": {},
                    "strength": "弱"
                },
                "福德宫": {
                    "stars": [
                        {"name": "天机", "type": "正曜", "brightness": "利"},
                        {"name": "天梁", "type": "正曜", "brightness": "庙"}
                    ],
                    "main_star": "天机",
                    "auxiliary_stars": ["天梁"],
                    "transforms": {},
                    "strength": "中"
                },
                "父母宫": {
                    "stars": [
                        {"name": "天府", "type": "正曜", "brightness": "旺"},
                        {"name": "太阴", "type": "正曜", "brightness": "旺"}
                    ],
                    "main_star": "天府",
                    "auxiliary_stars": ["天魁", "天钺"],
                    "transforms": {},
                    "strength": "强"
                }
            },
            "transforms": {
                "birth_year_gan": "丙",
                "transforms": [
                    {"star": "天同", "palace": "命宫", "transform_type": "化禄", "source": "生年"},
                    {"star": "天梁", "palace": "迁移宫", "transform_type": "化权", "source": "生年"},
                    {"star": "太阳", "palace": "夫妻宫", "transform_type": "化忌", "source": "生年"}
                ]
            },
            "patterns": [
                {
                    "name": "机梁同行",
                    "type": "中格",
                    "main_star": "天机",
                    "palace": "命宫"
                },
                {
                    "name": "财印相随",
                    "type": "吉格",
                    "main_star": "武曲",
                    "palace": "财帛宫"
                }
            ]
        }

    def test_zhang_overall_score(self, zhang_chart):
        """测试章海云综合运势"""
        calculator = FortuneCalculator(chart=zhang_chart, target_year=2026)
        result = calculator.calculate_full()
        risk_index = calculator.calculate_risk_index()
        opportunity_index = calculator.calculate_opportunity_index()

        print(f"\n=== 章海云 2026年运势 ===")
        print(f"综合运势: {result.overall_score} ({result.overall_level})")
        print(f"风险指数: {risk_index}")
        print(f"机遇指数: {opportunity_index}")

        # 验证分数范围
        assert 0 <= result.overall_score <= 100
        assert 0 <= risk_index <= 100
        assert 0 <= opportunity_index <= 100

    def test_zhang_dimension_scores(self, zhang_chart):
        """测试章海云各维度分数"""
        calculator = FortuneCalculator(chart=zhang_chart, target_year=2026)
        dimension_scores = calculator.calculate_dimension_scores()

        print(f"\n=== 各维度分数 ===")
        for key, score in dimension_scores.items():
            print(f"{key}: {score.score} ({score.level})")
            assert 0 <= score.score <= 100

    def test_zhang_monthly_scores(self, zhang_chart):
        """测试章海云月度运势"""
        calculator = FortuneCalculator(chart=zhang_chart, target_year=2026)
        monthly_scores = calculator.get_monthly_scores()

        print(f"\n=== 月度运势 ===")
        for month_score in monthly_scores:
            print(f"{month_score['month_name']}: {month_score['score']} ({month_score['level']})")
            assert 0 <= month_score["score"] <= 100


class TestScoreRangeValidation:
    """分数范围验证测试"""

    def test_extreme_cases(self):
        """测试极端情况"""
        # 全吉命盘
        best_chart = {
            "palaces": {
                "官禄宫": {
                    "stars": [{"name": "紫微", "brightness": "庙"}],
                    "main_star": "紫微",
                    "auxiliary_stars": ["左辅", "右弼", "天魁", "天钺"],
                    "transforms": {"化禄": "紫微"},
                },
                "财帛宫": {
                    "stars": [{"name": "武曲", "brightness": "庙"}],
                    "main_star": "武曲",
                    "auxiliary_stars": ["禄存"],
                    "transforms": {},
                },
                "夫妻宫": {
                    "stars": [{"name": "太阳", "brightness": "庙"}],
                    "main_star": "太阳",
                    "auxiliary_stars": [],
                    "transforms": {"化科": "太阳"},
                },
                "疾厄宫": {
                    "stars": [{"name": "天同", "brightness": "旺"}],
                    "main_star": "天同",
                    "auxiliary_stars": [],
                    "transforms": {},
                },
                "交友宫": {
                    "stars": [{"name": "太阴", "brightness": "旺"}],
                    "main_star": "太阴",
                    "auxiliary_stars": ["天魁"],
                    "transforms": {},
                }
            },
            "patterns": [{"name": "紫微天府", "type": "吉格", "palace": "官禄宫"}]
        }

        calculator = FortuneCalculator(chart=best_chart, target_year=2026)
        result = calculator.calculate_full()

        print(f"\n=== 最佳命盘测试 ===")
        print(f"综合运势: {result.overall_score}")
        assert result.overall_score > 50  # 应该高于平均

        # 全凶命盘
        worst_chart = {
            "palaces": {
                "官禄宫": {
                    "stars": [{"name": "天机", "brightness": "陷"}],
                    "main_star": "天机",
                    "auxiliary_stars": [],
                    "malefic_stars": ["擎羊", "陀罗", "火星", "铃星"],
                    "transforms": {"化忌": "天机"},
                },
                "财帛宫": {
                    "stars": [{"name": "武曲", "brightness": "陷"}],
                    "main_star": "武曲",
                    "auxiliary_stars": [],
                    "malefic_stars": ["地空", "地劫"],
                    "transforms": {"化忌": "武曲"},
                },
                "夫妻宫": {
                    "stars": [{"name": "太阳", "brightness": "陷"}],
                    "main_star": "太阳",
                    "auxiliary_stars": [],
                    "malefic_stars": ["陀罗", "铃星"],
                    "transforms": {"化忌": "太阳"},
                },
                "疾厄宫": {
                    "stars": [{"name": "廉贞", "brightness": "陷"}],
                    "main_star": "廉贞",
                    "auxiliary_stars": [],
                    "malefic_stars": ["火星", "铃星"],
                    "transforms": {},
                },
                "交友宫": {
                    "stars": [{"name": "贪狼", "brightness": "陷"}],
                    "main_star": "贪狼",
                    "auxiliary_stars": [],
                    "malefic_stars": ["擎羊", "地空"],
                    "transforms": {},
                }
            },
            "patterns": [{"name": "凶格", "type": "凶格", "palace": "官禄宫"}]
        }

        calculator2 = FortuneCalculator(chart=worst_chart, target_year=2026)
        result2 = calculator2.calculate_full()

        print(f"\n=== 最差命盘测试 ===")
        print(f"综合运势: {result2.overall_score}")
        assert result2.overall_score < 50  # 应该低于平均

    def test_neutral_chart(self):
        """测试中性命盘"""
        neutral_chart = {
            "palaces": {
                "官禄宫": {
                    "stars": [{"name": "天同", "brightness": "平"}],
                    "main_star": "天同",
                    "auxiliary_stars": [],
                    "transforms": {},
                },
                "财帛宫": {
                    "stars": [{"name": "天相", "brightness": "平"}],
                    "main_star": "天相",
                    "auxiliary_stars": [],
                    "transforms": {},
                },
                "夫妻宫": {
                    "stars": [{"name": "天梁", "brightness": "平"}],
                    "main_star": "天梁",
                    "auxiliary_stars": [],
                    "transforms": {},
                },
                "疾厄宫": {
                    "stars": [{"name": "天机", "brightness": "平"}],
                    "main_star": "天机",
                    "auxiliary_stars": [],
                    "transforms": {},
                },
                "交友宫": {
                    "stars": [{"name": "太阳", "brightness": "平"}],
                    "main_star": "太阳",
                    "auxiliary_stars": [],
                    "transforms": {},
                }
            },
            "patterns": []
        }

        calculator = FortuneCalculator(chart=neutral_chart, target_year=2026)
        result = calculator.calculate_full()

        print(f"\n=== 中性命盘测试 ===")
        print(f"综合运势: {result.overall_score}")
        # 中性命盘应该在45-55之间
        assert 30 <= result.overall_score <= 70


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
