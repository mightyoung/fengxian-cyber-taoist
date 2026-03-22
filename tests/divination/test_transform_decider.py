"""Tests for TransformDecider module."""
import pytest
import sys
import importlib.util

# Direct import to avoid backend.app.services __init__.py dependencies
spec = importlib.util.spec_from_file_location(
    "transform_decider",
    "backend/app/services/divination/transform_decider.py"
)
transform_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transform_module)

TransformDecider = transform_module.TransformDecider
TransformType = transform_module.TransformType


class TestTransformDecider:
    """Test cases for TransformDecider."""

    def test_jia_hua(self):
        """Test 甲 year transformation - 化禄廉贞、化权破军、化科太阳、化忌太阴"""
        decider = TransformDecider()
        result = decider.get_transform("甲")
        assert len(result.transforms) == 4
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "廉贞"
        assert transform_dict.get(TransformType.HUA_QUAN) == "破军"
        assert transform_dict.get(TransformType.HUA_KE) == "太阳"
        assert transform_dict.get(TransformType.HUA_JI) == "太阴"

    def test_yi_hua(self):
        """Test 乙 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("乙")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "天机"
        assert transform_dict.get(TransformType.HUA_QUAN) == "天梁"
        assert transform_dict.get(TransformType.HUA_KE) == "文昌"
        assert transform_dict.get(TransformType.HUA_JI) == "贪狼"

    def test_bing_hua(self):
        """Test 丙 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("丙")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "天同"
        assert transform_dict.get(TransformType.HUA_QUAN) == "天机"
        assert transform_dict.get(TransformType.HUA_KE) == "天机"
        assert transform_dict.get(TransformType.HUA_JI) == "天同"

    def test_ding_hua(self):
        """Test 丁 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("丁")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "巨门"
        assert transform_dict.get(TransformType.HUA_QUAN) == "太阳"
        assert transform_dict.get(TransformType.HUA_KE) == "文曲"
        assert transform_dict.get(TransformType.HUA_JI) == "天机"

    def test_wu_hua(self):
        """Test 戊 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("戊")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "贪狼"
        assert transform_dict.get(TransformType.HUA_QUAN) == "武曲"
        assert transform_dict.get(TransformType.HUA_KE) == "天梁"
        assert transform_dict.get(TransformType.HUA_JI) == "廉贞"

    def test_ji_hua(self):
        """Test 己 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("己")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "太阴"
        assert transform_dict.get(TransformType.HUA_QUAN) == "巨门"
        assert transform_dict.get(TransformType.HUA_KE) == "天机"
        assert transform_dict.get(TransformType.HUA_JI) == "文昌"

    def test_geng_hua(self):
        """Test 庚 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("庚")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "天梁"
        assert transform_dict.get(TransformType.HUA_QUAN) == "紫微"
        assert transform_dict.get(TransformType.HUA_KE) == "天府"
        assert transform_dict.get(TransformType.HUA_JI) == "天同"

    def test_xin_hua(self):
        """Test 辛 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("辛")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "文昌"
        assert transform_dict.get(TransformType.HUA_QUAN) == "文曲"
        assert transform_dict.get(TransformType.HUA_KE) == "天同"
        assert transform_dict.get(TransformType.HUA_JI) == "天梁"

    def test_ren_hua(self):
        """Test 壬 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("壬")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "天同"
        assert transform_dict.get(TransformType.HUA_QUAN) == "天机"
        assert transform_dict.get(TransformType.HUA_KE) == "天机"
        assert transform_dict.get(TransformType.HUA_JI) == "天同"

    def test_gui_hua(self):
        """Test 癸 year transformation."""
        decider = TransformDecider()
        result = decider.get_transform("癸")
        transform_dict = {t.transform_type: t.star_name for t in result.transforms}
        assert transform_dict.get(TransformType.HUA_LU) == "天机"
        assert transform_dict.get(TransformType.HUA_QUAN) == "文曲"
        assert transform_dict.get(TransformType.HUA_KE) == "天同"
        assert transform_dict.get(TransformType.HUA_JI) == "天机"

    def test_year_stem_propagation(self):
        """Test that year_stem is propagated correctly."""
        decider = TransformDecider()
        result = decider.get_transform("甲")
        assert result.year_stem == "甲"

    def test_invalid_year_stem(self):
        """Test invalid year stem raises ValueError."""
        decider = TransformDecider()
        with pytest.raises(ValueError):
            decider.get_transform("invalid")

    def test_is_valid_year_stem(self):
        """Test is_valid_year_stem method."""
        decider = TransformDecider()
        assert decider.is_valid_year_stem("甲") is True
        assert decider.is_valid_year_stem("乙") is True
        assert decider.is_valid_year_stem("invalid") is False

    def test_get_transform_dict(self):
        """Test get_transform_dict method."""
        decider = TransformDecider()
        result = decider.get_transform_dict("甲")
        assert "year_stem" in result
        assert "transforms" in result

    def test_to_dict(self):
        """Test to_dict method of TransformResult."""
        decider = TransformDecider()
        result = decider.get_transform("甲")
        result_dict = result.to_dict()
        assert result_dict["year_stem"] == "甲"
        assert len(result_dict["transforms"]) == 4

    def test_transform_star_to_dict(self):
        """Test to_dict method of TransformStar."""
        decider = TransformDecider()
        result = decider.get_transform("甲")
        first_transform = result.transforms[0]
        transform_dict = first_transform.to_dict()
        assert "type" in transform_dict
        assert "star" in transform_dict

    def test_get_all_transforms(self):
        """Test get_all_transforms method."""
        decider = TransformDecider()
        all_transforms = decider.get_all_transforms()
        # Should have 10 year stems
        assert len(all_transforms) == 10
        # Each should have 4 transforms
        for stem, transforms in all_transforms.items():
            assert len(transforms) == 4

    def test_transform_count(self):
        """Test that each year has exactly 4 transforms."""
        decider = TransformDecider()
        year_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        for stem in year_stems:
            result = decider.get_transform(stem)
            assert len(result.transforms) == 4

    def test_transform_types_coverage(self):
        """Test that all 4 transform types are present for each year."""
        decider = TransformDecider()
        result = decider.get_transform("甲")
        transform_types = [t.transform_type for t in result.transforms]
        assert TransformType.HUA_LU in transform_types
        assert TransformType.HUA_QUAN in transform_types
        assert TransformType.HUA_KE in transform_types
        assert TransformType.HUA_JI in transform_types

    def test_transform_types_enum(self):
        """Test TransformType enum values."""
        assert TransformType.HUA_LU.value == "化禄"
        assert TransformType.HUA_QUAN.value == "化权"
        assert TransformType.HUA_KE.value == "化科"
        assert TransformType.HUA_JI.value == "化忌"
