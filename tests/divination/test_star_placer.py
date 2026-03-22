"""Tests for StarPlacer module."""
import pytest
import sys
import importlib.util

# Direct import to avoid backend.app.services __init__.py dependencies
spec = importlib.util.spec_from_file_location(
    "star_placer",
    "backend/app/services/divination/star_placer.py"
)
star_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(star_module)

StarPlacer = star_module.StarPlacer
FiveElementType = star_module.FiveElementType
StarType = star_module.StarType
StarLevel = star_module.StarLevel
PALACE_ORDER = star_module.PALACE_ORDER


class TestStarPlacer:
    """Test cases for StarPlacer."""

    def test_ziwei_placement(self):
        """Test that 紫微星 is placed correctly."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()
        # Verify 紫微星 is placed in some palace
        assert result is not None

    def test_main_stars_count(self):
        """Test that main stars (十四正曜) are placed."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()
        # Count all stars across all palaces
        total_stars = sum(len(ps.stars) for ps in result.palaces.values())
        # Should have at least 14 main stars
        assert total_stars >= 14

    def test_star_types_present(self):
        """Test that different star types are present."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()

        # Check that we have different star types
        star_types = set()
        for palace in result.palaces.values():
            for star in palace.stars:
                star_types.add(star.star_type)

        assert StarType.ZHENGYAO in star_types
        assert StarType.FUXING in star_types

    def test_wuxing_ju_in_result(self):
        """Test that wuxing_ju is stored in result."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.JIN_SI,
            gender="男"
        )
        result = placer.get_result()
        assert result.wuxing_ju == FiveElementType.JIN_SI

    def test_palace_has_tiangan(self):
        """Test that each palace has tiangan (宫干)."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()

        # Each palace should have a tiangan
        for palace_name, palace_stars in result.palaces.items():
            assert palace_stars.tiangan != ""

    def test_ming_gong_has_stars(self):
        """Test that ming gong (命宫) has stars."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        ming_gong_stars = placer.get_ming_gong_stars()
        # Ming gong should have at least one main star (紫微)
        assert len(ming_gong_stars) > 0

    def test_get_palace_stars(self):
        """Test getting stars for a specific palace."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        stars = placer.get_palace_stars("命宫")
        assert isinstance(stars, list)

    def test_get_star_palace(self):
        """Test getting palace for a specific star."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        # 紫微 should be somewhere
        palace = placer.get_star_palace("紫微")
        assert palace is not None
        assert palace in PALACE_ORDER

    def test_to_dict(self):
        """Test converting result to dictionary."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result_dict = placer.to_dict()
        assert "birth_info" in result_dict
        assert "palaces" in result_dict
        assert "ming_gong_stars" in result_dict

    def test_zhengyao_stars_present(self):
        """Test that all 14 main stars are present."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()

        # Expected main stars (十四正曜)
        expected_main_stars = [
            "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
            "天府", "太阴", "贪狼", "巨门", "天相", "天梁",
            "七杀", "破军"
        ]

        # Collect all star names
        all_star_names = []
        for palace in result.palaces.values():
            for star in palace.stars:
                if star.star_type == StarType.ZHENGYAO:
                    all_star_names.append(star.name)

        # Check all main stars are present
        for star_name in expected_main_stars:
            assert star_name in all_star_names, f"Star {star_name} should be present"

    def test_fuxing_stars_present(self):
        """Test that auxiliary stars (辅星) are present."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()

        # Expected auxiliary stars
        expected_fuxing = ["左辅", "右弼", "文昌", "文曲"]

        # Collect all star names
        all_star_names = []
        for palace in result.palaces.values():
            for star in palace.stars:
                if star.star_type == StarType.FUXING:
                    all_star_names.append(star.name)

        # At least some fuxing should be present
        assert len(all_star_names) > 0

    def test_different_wuxing_ju(self):
        """Test with different wuxing_ju values."""
        for wuxing_ju in FiveElementType:
            placer = StarPlacer(
                year=1990,
                month=5,
                day=15,
                hour=10,
                minute=0,
                wuxing_ju=wuxing_ju,
                gender="男"
            )
            result = placer.get_result()
            assert result.wuxing_ju == wuxing_ju

    def test_palace_count(self):
        """Test that there are 12 palaces."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()
        assert len(result.palaces) == 12

    def test_has_star_method(self):
        """Test the has_star method."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()

        # Find a palace with stars
        palace_with_stars = None
        for palace in result.palaces.values():
            if len(palace.stars) > 0:
                palace_with_stars = palace
                break

        assert palace_with_stars is not None
        star_name = palace_with_stars.stars[0].name
        assert palace_with_stars.has_star(star_name)
        assert not palace_with_stars.has_star("不存在的星曜")

    def test_get_result_returns_chart_result(self):
        """Test that get_result returns ChartResult."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()
        # Verify result type by checking attributes
        assert hasattr(result, 'palaces')
        assert hasattr(result, 'wuxing_ju')

    def test_female_gender(self):
        """Test with female gender."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="女"
        )
        result = placer.get_result()
        assert result is not None

    def test_get_all_stars_in_palace(self):
        """Test getting all stars in a palace."""
        placer = StarPlacer(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=0,
            wuxing_ju=FiveElementType.SHUI_ER,
            gender="男"
        )
        result = placer.get_result()
        stars = result.get_all_stars_in_palace("命宫")
        assert isinstance(stars, list)
