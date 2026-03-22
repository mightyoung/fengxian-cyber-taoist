"""
四化确定模块
根据出生年干确定四化星曜分布
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TransformType(Enum):
    """四化类型"""
    HUA_LU = "化禄"      # 化禄
    HUA_QUAN = "化权"    # 化权
    HUA_KE = "化科"      # 化科
    HUA_JI = "化忌"      # 化忌


@dataclass
class TransformStar:
    """四化星曜"""
    transform_type: TransformType
    star_name: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "type": self.transform_type.value,
            "star": self.star_name
        }


@dataclass
class TransformResult:
    """四化结果"""
    year_stem: str
    transforms: List[TransformStar]

    def to_dict(self) -> Dict[str, any]:
        return {
            "year_stem": self.year_stem,
            "transforms": [t.to_dict() for t in self.transforms]
        }


# 生年干四化映射表 (根据紫微斗数典籍《紫微斗数全书》《飞星紫微斗数》)
# 一星不可化两曜，化禄和化忌可以同星
# 甲: 廉贞化禄、破军化权、太阳化科、太阴化忌
# 乙: 廉贞化禄、破军化权、武曲化科、太阳化忌
# 丙: 天同化禄、天梁化权、太阳化科、天同化忌
# 丁: 天同化禄、天梁化权、天机化科、太阴化忌
# 戊: 贪狼化禄、太阴化权、右弼化科、天机化忌
# 己: 武曲化禄、贪狼化权、太阴化科、武曲化忌
# 庚: 太阳化禄、武曲化权、天府化科、太阳化忌
# 辛: 巨门化禄、太阳化权、天府化科、巨门化忌
# 壬: 天梁化禄、天机化权、紫微化科、天梁化忌
# 癸: 天机化禄、巨门化权、紫微化科、天机化忌
YEAR_STEM_TRANSFORMS: Dict[str, Dict[TransformType, str]] = {
    "甲": {
        TransformType.HUA_LU: "廉贞",
        TransformType.HUA_QUAN: "破军",
        TransformType.HUA_KE: "太阳",
        TransformType.HUA_JI: "太阴",
    },
    "乙": {
        TransformType.HUA_LU: "廉贞",
        TransformType.HUA_QUAN: "破军",
        TransformType.HUA_KE: "武曲",
        TransformType.HUA_JI: "太阳",
    },
    "丙": {
        TransformType.HUA_LU: "天同",
        TransformType.HUA_QUAN: "天梁",
        TransformType.HUA_KE: "太阳",
        TransformType.HUA_JI: "天同",
    },
    "丁": {
        TransformType.HUA_LU: "天同",
        TransformType.HUA_QUAN: "天梁",
        TransformType.HUA_KE: "天机",
        TransformType.HUA_JI: "太阴",
    },
    "戊": {
        TransformType.HUA_LU: "贪狼",
        TransformType.HUA_QUAN: "太阴",
        TransformType.HUA_KE: "右弼",
        TransformType.HUA_JI: "天机",
    },
    "己": {
        TransformType.HUA_LU: "武曲",
        TransformType.HUA_QUAN: "贪狼",
        TransformType.HUA_KE: "太阴",
        TransformType.HUA_JI: "武曲",
    },
    "庚": {
        TransformType.HUA_LU: "太阳",
        TransformType.HUA_QUAN: "武曲",
        TransformType.HUA_KE: "天府",
        TransformType.HUA_JI: "太阳",
    },
    "辛": {
        TransformType.HUA_LU: "巨门",
        TransformType.HUA_QUAN: "太阳",
        TransformType.HUA_KE: "天府",
        TransformType.HUA_JI: "巨门",
    },
    "壬": {
        TransformType.HUA_LU: "天梁",
        TransformType.HUA_QUAN: "天机",
        TransformType.HUA_KE: "紫微",
        TransformType.HUA_JI: "天梁",
    },
    "癸": {
        TransformType.HUA_LU: "天机",
        TransformType.HUA_QUAN: "巨门",
        TransformType.HUA_KE: "紫微",
        TransformType.HUA_JI: "天机",
    },
}

# 天干列表（用于验证）
VALID_YEAR_STEMS = list(YEAR_STEM_TRANSFORMS.keys())


class TransformDecider:
    """
    四化确定器
    根据出生年干确定四化星曜分布
    """

    @staticmethod
    def get_transform(year_stem: str) -> TransformResult:
        """
        获取指定年干的四化星曜

        Args:
            year_stem: 出生年干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）

        Returns:
            TransformResult: 四化结果

        Raises:
            ValueError: 当年干无效时
        """
        if year_stem not in YEAR_STEM_TRANSFORMS:
            raise ValueError(
                f"无效的年干: {year_stem}。有效值为: {', '.join(VALID_YEAR_STEMS)}"
            )

        transform_map = YEAR_STEM_TRANSFORMS[year_stem]
        transforms = [
            TransformStar(transform_type, star)
            for transform_type, star in transform_map.items()
        ]

        return TransformResult(year_stem=year_stem, transforms=transforms)

    @staticmethod
    def get_transform_dict(year_stem: str) -> Dict[str, any]:
        """
        获取四化结果的字典形式

        Args:
            year_stem: 出生年干

        Returns:
            Dict: 四化结果的字典表示
        """
        result = TransformDecider.get_transform(year_stem)
        return result.to_dict()

    @staticmethod
    def is_valid_year_stem(year_stem: str) -> bool:
        """
        检查是否为有效的年干

        Args:
            year_stem: 待检查的年干

        Returns:
            bool: 是否有效
        """
        return year_stem in YEAR_STEM_TRANSFORMS

    @staticmethod
    def get_all_transforms() -> Dict[str, Dict[str, str]]:
        """
        获取所有年干的四化映射（用于调试或展示）

        Returns:
            Dict: 所有年干的四化映射
        """
        result = {}
        for year_stem in VALID_YEAR_STEMS:
            transform_map = YEAR_STEM_TRANSFORMS[year_stem]
            result[year_stem] = {
                t_type.value: star for t_type, star in transform_map.items()
            }
        return result
