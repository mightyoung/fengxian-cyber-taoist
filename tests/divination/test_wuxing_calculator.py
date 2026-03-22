"""Tests for WuXingCalculator module."""
import pytest
import sys
import importlib.util

# Direct import to avoid backend.app.services __init__.py dependencies
spec = importlib.util.spec_from_file_location(
    "wuxing_calculator",
    "backend/app/services/divination/wuxing_calculator.py"
)
wuxing_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wuxing_module)

WuXingCalculator = wuxing_module.WuXingCalculator
WuXingJuType = wuxing_module.WuXingJuType


class TestWuXingCalculator:
    """Test cases for WuXingCalculator."""

    def test_water_two_years(self):
        """Test water two (水二局) years - 壬年, 癸年"""
        calc = WuXingCalculator()
        # 壬年 (壬子, 壬寅...) -> 水二局
        for year in [1972, 1982, 1992, 2002, 2012]:
            result = calc.calculate_by_year(year)
            assert result.wuxing_ju == WuXingJuType.WATER_TWO, f"Year {year} should be WATER_TWO"

    def test_wood_three_years(self):
        """Test wood three (木三局) years - 甲年, 乙年"""
        calc = WuXingCalculator()
        # 甲年 -> 木三局
        for year in [1974, 1984, 1994, 2004, 2024]:
            result = calc.calculate_by_year(year)
            assert result.wuxing_ju == WuXingJuType.WOOD_THREE, f"Year {year} should be WOOD_THREE"

    def test_gold_four_years(self):
        """Test gold four (金四局) years - 庚年, 辛年"""
        calc = WuXingCalculator()
        # 庚年 -> 金四局
        for year in [1970, 1980, 1990, 2000, 2010]:
            result = calc.calculate_by_year(year)
            assert result.wuxing_ju == WuXingJuType.GOLD_FOUR, f"Year {year} should be GOLD_FOUR"

    def test_earth_five_years(self):
        """Test earth five (土五局) years - 戊年, 己年"""
        calc = WuXingCalculator()
        # 戊年 -> 土五局
        for year in [1979, 1989, 1999, 2009, 2019]:
            result = calc.calculate_by_year(year)
            assert result.wuxing_ju == WuXingJuType.EARTH_FIVE, f"Year {year} should be EARTH_FIVE"

    def test_fire_six_years(self):
        """Test fire six (火六局) years - 丙年, 丁年"""
        calc = WuXingCalculator()
        # 丙年 -> 火六局
        for year in [1976, 1986, 1996, 2006, 2016]:
            result = calc.calculate_by_year(year)
            assert result.wuxing_ju == WuXingJuType.FIRE_SIX, f"Year {year} should be FIRE_SIX"

    def test_year_gan(self):
        """Test getting year gan (年干) from year."""
        calc = WuXingCalculator()
        # 甲年 (2024)
        assert calc.get_year_gan(2024) == "甲"
        # 乙年 (2025)
        assert calc.get_year_gan(2025) == "乙"
        # 癸年 (2023)
        assert calc.get_year_gan(2023) == "癸"
        # 丙年 (1986)
        assert calc.get_year_gan(1986) == "丙"
        # 庚年 (2010)
        assert calc.get_year_gan(2010) == "庚"

    def test_ganzhi_year(self):
        """Test getting ganzhi (干支) from year."""
        calc = WuXingCalculator()
        # 甲子年
        assert calc.get_ganzhi_year(1984) == "甲子"
        # 乙丑年
        assert calc.get_ganzhi_year(1985) == "乙丑"

    def test_calculate_by_gan(self):
        """Test calculating wuxing_ju by gan (年干)."""
        calc = WuXingCalculator()
        # 甲 -> 木三局
        result = calc.calculate_by_gan("甲")
        assert result.wuxing_ju == WuXingJuType.WOOD_THREE
        assert result.year_gan == "甲"

        # 乙 -> 木三局
        result = calc.calculate_by_gan("乙")
        assert result.wuxing_ju == WuXingJuType.WOOD_THREE

        # 丙 -> 火六局
        result = calc.calculate_by_gan("丙")
        assert result.wuxing_ju == WuXingJuType.FIRE_SIX

        # 丁 -> 火六局
        result = calc.calculate_by_gan("丁")
        assert result.wuxing_ju == WuXingJuType.FIRE_SIX

        # 戊 -> 土五局
        result = calc.calculate_by_gan("戊")
        assert result.wuxing_ju == WuXingJuType.EARTH_FIVE

    def test_calculate_by_ganzhi(self):
        """Test calculating wuxing_ju by ganzhi (年干支)."""
        calc = WuXingCalculator()
        # 甲子 -> 金四局
        result = calc.calculate_by_ganzhi("甲子")
        assert result.year_gan == "甲"

    def test_invalid_gan(self):
        """Test invalid gan raises ValueError."""
        calc = WuXingCalculator()
        with pytest.raises(ValueError):
            calc.calculate_by_gan("invalid")

    def test_get_daxian_ranges(self):
        """Test getting daxian (大限) age ranges."""
        # 水二局 -> 2岁起运
        ranges = WuXingCalculator.get_daxian_ranges(2)
        assert ranges[0] == (2, 11)

        # 木三局 -> 3岁起运
        ranges = WuXingCalculator.get_daxian_ranges(3)
        assert ranges[0] == (3, 12)

        # 金四局 -> 4岁起运
        ranges = WuXingCalculator.get_daxian_ranges(4)
        assert ranges[0] == (4, 13)
