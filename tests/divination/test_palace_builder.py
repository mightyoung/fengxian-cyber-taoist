"""Tests for PalaceBuilder module."""
import pytest
import sys
import importlib.util

# Direct import to avoid backend.app.services __init__.py dependencies
spec = importlib.util.spec_from_file_location(
    "palace_builder",
    "backend/app/services/divination/palace_builder.py"
)
palace_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(palace_module)

PalaceBuilder = palace_module.PalaceBuilder
PALACE_NAMES = palace_module.PALACE_NAMES


class TestPalaceBuilder:
    """Test cases for PalaceBuilder."""

    def test_yang_male_clockwise(self):
        """Test yang male (阳男) clockwise direction."""
        builder = PalaceBuilder()
        # 甲年出生男性：阳男 -> 顺时针
        result = builder.build(gender="male", year_stem="甲")
        assert result.direction == "顺时针"
        assert result.yin_yang == "yang"

    def test_yin_male_counter_clockwise(self):
        """Test yin male (阴男) counter-clockwise direction."""
        builder = PalaceBuilder()
        # 乙年出生男性：阴男 -> 逆时针
        result = builder.build(gender="male", year_stem="乙")
        assert result.direction == "逆时针"
        assert result.yin_yang == "yin"

    def test_yang_female_counter_clockwise(self):
        """Test yang female (阳女) counter-clockwise direction."""
        builder = PalaceBuilder()
        # 甲年出生女性：阳女 -> 逆时针
        result = builder.build(gender="female", year_stem="甲")
        assert result.direction == "逆时针"
        assert result.yin_yang == "yang"

    def test_yin_female_clockwise(self):
        """Test yin female (阴女) clockwise direction."""
        builder = PalaceBuilder()
        # 乙年出生女性：阴女 -> 顺时针
        result = builder.build(gender="female", year_stem="乙")
        assert result.direction == "顺时针"
        assert result.yin_yang == "yin"

    def test_all_12_palaces_present(self):
        """Test that all 12 palaces are present."""
        builder = PalaceBuilder()
        result = builder.build(gender="male", year_stem="甲")
        palace_names = [p.name for p in result.palaces]
        assert len(palace_names) == 12
        assert "命宫" in palace_names
        assert "父母宫" in palace_names
        assert "兄弟宫" in palace_names
        assert "夫妻宫" in palace_names

    def test_ming_gong_branch(self):
        """Test that ming gong (命宫) has the correct branch."""
        builder = PalaceBuilder()
        result = builder.build(gender="male", year_stem="甲")
        # 命宫应该是寅
        ming_gong = result.get_palace("命宫")
        assert ming_gong.branch == "寅"

    def test_clockwise_sequence(self):
        """Test clockwise sequence for yang male."""
        builder = PalaceBuilder()
        result = builder.build(gender="male", year_stem="甲")
        branches = [p.branch for p in result.palaces]
        # 顺时针从寅开始: 寅, 卯, 辰, ...
        assert branches[0] == "寅"
        assert branches[1] == "卯"
        assert branches[2] == "辰"

    def test_counter_clockwise_sequence(self):
        """Test counter-clockwise sequence for yin male."""
        builder = PalaceBuilder()
        result = builder.build(gender="male", year_stem="乙")
        branches = [p.branch for p in result.palaces]
        # 逆时针从寅开始: 寅, 丑, 子, ...
        assert branches[0] == "寅"
        assert branches[1] == "丑"
        assert branches[2] == "子"

    def test_invalid_gender(self):
        """Test invalid gender raises ValueError."""
        builder = PalaceBuilder()
        with pytest.raises(ValueError):
            builder.build(gender="invalid", year_stem="甲")

    def test_invalid_year_stem(self):
        """Test invalid year stem raises ValueError."""
        builder = PalaceBuilder()
        with pytest.raises(ValueError):
            builder.build(gender="male", year_stem="invalid")

    def test_build_with_year_ganzhi(self):
        """Test building palaces with year ganzhi."""
        builder = PalaceBuilder()
        # 甲子年
        result = builder.build_with_year_ganzhi(gender="male", year_ganzhi="甲子")
        assert result.year_stem == "甲"

    def test_year_stem_propagation(self):
        """Test that year_stem is propagated correctly."""
        builder = PalaceBuilder()
        result = builder.build(gender="male", year_stem="甲")
        assert result.year_stem == "甲"

    def test_gender_propagation(self):
        """Test that gender is propagated correctly."""
        builder = PalaceBuilder()
        result = builder.build(gender="female", year_stem="甲")
        assert result.gender == "female"

    def test_yin_yang_propagation(self):
        """Test that yin_yang is propagated correctly."""
        builder = PalaceBuilder()
        # 甲 -> 阳
        result = builder.build(gender="male", year_stem="甲")
        assert result.yin_yang == "yang"
        # 乙 -> 阴
        result = builder.build(gender="male", year_stem="乙")
        assert result.yin_yang == "yin"

    def test_get_palace_by_name(self):
        """Test getting palace by name."""
        builder = PalaceBuilder()
        result = builder.build(gender="male", year_stem="甲")
        palace = result.get_palace("命宫")
        assert palace is not None
        assert palace.name == "命宫"

    def test_to_dict(self):
        """Test converting result to dictionary."""
        builder = PalaceBuilder()
        result = builder.build(gender="male", year_stem="甲")
        result_dict = result.to_dict()
        assert "palaces" in result_dict
        assert len(result_dict["palaces"]) == 12
        assert result_dict["direction"] == "顺时针"
