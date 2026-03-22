"""
紫微斗数十二宫排布服务
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Gender(Enum):
    """性别"""
    MALE = "male"
    FEMALE = "female"


class YinYang(Enum):
    """阴阳"""
    YANG = "yang"
    YIN = "yin"


# 十二地支（按顺时针顺序）
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 十二宫名称（按固定顺序）
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "奴仆宫",
    "官禄宫", "田宅宫", "福德宫", "父母宫"
]

# 天干阴阳属性
HEAVENLY_STEMS_YINYANG = {
    "甲": YinYang.YANG,  # 阳木
    "乙": YinYang.YIN,   # 阴木
    "丙": YinYang.YANG,  # 阳火
    "丁": YinYang.YIN,   # 阴火
    "戊": YinYang.YANG,  # 阳土
    "己": YinYang.YIN,   # 阴土
    "庚": YinYang.YANG,  # 阳金
    "辛": YinYang.YIN,   # 阴金
    "壬": YinYang.YANG,  # 阳水
    "癸": YinYang.YIN,   # 阴水
}


@dataclass
class Palace:
    """宫位"""
    name: str                           # 宫名
    branch: str                         # 地支
    main_stars: List[str] = field(default_factory=list)  # 主星
    transformed_stars: Dict[str, str] = field(default_factory=dict)  # 四化星

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "branch": self.branch,
            "main_stars": self.main_stars,
            "transformed_stars": self.transformed_stars,
        }


@dataclass
class TwelvePalaces:
    """十二宫排布结果"""
    ming_gong_branch: str               # 命宫所在的地支
    gender: str                          # 性别
    year_stem: str                      # 年干
    yin_yang: str                       # 阴阳
    direction: str                      # 排布方向 (顺时针/逆时针)
    palaces: List[Palace] = field(default_factory=list)

    def get_palace(self, name: str) -> Optional[Palace]:
        """获取指定宫位"""
        for palace in self.palaces:
            if palace.name == name:
                return palace
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ming_gong_branch": self.ming_gong_branch,
            "gender": self.gender,
            "year_stem": self.year_stem,
            "yin_yang": self.yin_yang,
            "direction": self.direction,
            "palaces": [p.to_dict() for p in self.palaces],
        }


class PalaceBuilder:
    """
    十二宫排布器

    排布规则：
    1. 命宫起例：
       - 阳男阴女：顺时针数（从寅开始）
       - 阴男阳女：逆时针数（从寅开始）
    2. 其他宫位顺时针排列
    """

    def __init__(self):
        # 寅在地支数组中的索引
        self.yin_index = EARTHLY_BRANCHES.index("寅")

    def get_yin_yang(self, year_stem: str) -> YinYang:
        """根据年干获取阴阳属性"""
        return HEAVENLY_STEMS_YINYANG.get(year_stem, YinYang.YANG)

    def _calculate_direction(self, gender: Gender, yin_yang: YinYang) -> str:
        """
        计算排布方向

        Args:
            gender: 性别
            yin_yang: 年干阴阳

        Returns:
            "顺时针" 或 "逆时针"
        """
        # 阳男阴女：顺时针
        # 阴男阳女：逆时针
        if (gender == Gender.MALE and yin_yang == YinYang.YANG) or \
           (gender == Gender.FEMALE and yin_yang == YinYang.YIN):
            return "顺时针"
        else:
            return "逆时针"

    def _get_branches_sequence(self, direction: str) -> List[str]:
        """
        获取地支序列

        Args:
            direction: 排布方向

        Returns:
            从寅开始的地支序列
        """
        if direction == "顺时针":
            # 顺时针：从寅开始，依次向后
            return EARTHLY_BRANCHES[self.yin_index:] + EARTHLY_BRANCHES[:self.yin_index]
        else:
            # 逆时针：从寅开始，依次向前
            branches = []
            for i in range(12):
                idx = (self.yin_index - i) % 12
                branches.append(EARTHLY_BRANCHES[idx])
            return branches

    def build(
        self,
        gender: str,
        year_stem: str
    ) -> TwelvePalaces:
        """
        构建十二宫排布

        Args:
            gender: 性别 ("male" 或 "female")
            year_stem: 年干 ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")

        Returns:
            十二宫排布结果

        Raises:
            ValueError: 参数无效
        """
        # 验证参数
        if gender not in ["male", "female"]:
            raise ValueError(f"无效的性别: {gender}")

        if year_stem not in HEAVENLY_STEMS_YINYANG:
            raise ValueError(f"无效的年干: {year_stem}")

        # 转换为枚举
        gender_enum = Gender.MALE if gender == "male" else Gender.FEMALE
        yin_yang = self.get_yin_yang(year_stem)

        # 计算方向
        direction = self._calculate_direction(gender_enum, yin_yang)

        # 获取地支序列
        branches_sequence = self._get_branches_sequence(direction)

        # 构建宫位
        palaces = []
        for i, palace_name in enumerate(PALACE_NAMES):
            palace = Palace(
                name=palace_name,
                branch=branches_sequence[i],
                main_stars=[],  # 主星待后续填充
                transformed_stars={}  # 四化待后续填充
            )
            palaces.append(palace)

        return TwelvePalaces(
            ming_gong_branch=branches_sequence[0],  # 命宫就是寅
            gender=gender,
            year_stem=year_stem,
            yin_yang=yin_yang.value,
            direction=direction,
            palaces=palaces
        )

    def build_with_year_ganzhi(self, gender: str, year_ganzhi: str) -> TwelvePalaces:
        """
        根据年干支构建十二宫排布

        Args:
            gender: 性别 ("male" 或 "female")
            year_ganzhi: 年干支（如 "甲子", "乙丑" 等）

        Returns:
            十二宫排布结果
        """
        if len(year_ganzhi) < 2:
            raise ValueError(f"无效的年干支: {year_ganzhi}")

        year_stem = year_ganzhi[0]
        return self.build(gender, year_stem)


def build_twelve_palaces(
    gender: str,
    year_stem: str
) -> Dict[str, Any]:
    """
    快速构建十二宫排布（便捷函数）

    Args:
        gender: 性别 ("male" 或 "female")
        year_stem: 年干 ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")

    Returns:
        十二宫排布结果的字典
    """
    builder = PalaceBuilder()
    result = builder.build(gender, year_stem)
    return result.to_dict()


if __name__ == "__main__":
    # 测试示例
    print("=== 测试：阳男（甲年出生男性）===")
    result1 = build_twelve_palaces("male", "甲")
    print(f"方向: {result1['direction']}")
    print("宫位:")
    for p in result1['palaces']:
        print(f"  {p['name']}: {p['branch']}")

    print("\n=== 测试：阴男（乙年出生男性）===")
    result2 = build_twelve_palaces("male", "乙")
    print(f"方向: {result2['direction']}")
    print("宫位:")
    for p in result2['palaces']:
        print(f"  {p['name']}: {p['branch']}")

    print("\n=== 测试：阳女（甲年出生女性）===")
    result3 = build_twelve_palaces("female", "甲")
    print(f"方向: {result3['direction']}")
    print("宫位:")
    for p in result3['palaces']:
        print(f"  {p['name']}: {p['branch']}")

    print("\n=== 测试：阴女（乙年出生女性）===")
    result4 = build_twelve_palaces("female", "乙")
    print(f"方向: {result4['direction']}")
    print("宫位:")
    for p in result4['palaces']:
        print(f"  {p['name']}: {p['branch']}")
