"""
五行局计算模块

五行局是紫微斗数排盘的核心要素之一，根据出生年的天干确定纳音五行，
进而确定五行局。五行局决定大限起运年龄，是排盘系统的关键模块。

五行局类型：
- 水二局：纳音五行为水
- 木三局：纳音五行为木
- 金四局：纳音五行为金
- 土五局：纳音五行为土
- 火六局：纳音五行为火
"""

from enum import Enum
from dataclasses import dataclass


class WuXingJuType(str, Enum):
    """五行局类型"""
    WATER_TWO = "水二局"   # 水二局
    WOOD_THREE = "木三局"  # 木三局
    GOLD_FOUR = "金四局"   # 金四局
    EARTH_FIVE = "土五局"  # 土五局
    FIRE_SIX = "火六局"    # 火六局


# 天干与五行局的对应关系
# 根据年干确定纳音五行，再映射到五行局
TIANGAN_WUXING_JU_MAP = {
    # 壬、癸 → 水
    "壬": WuXingJuType.WATER_TWO,
    "癸": WuXingJuType.WATER_TWO,
    # 甲、乙 → 木
    "甲": WuXingJuType.WOOD_THREE,
    "乙": WuXingJuType.WOOD_THREE,
    # 庚、辛 → 金
    "庚": WuXingJuType.GOLD_FOUR,
    "辛": WuXingJuType.GOLD_FOUR,
    # 戊、己 → 土
    "戊": WuXingJuType.EARTH_FIVE,
    "己": WuXingJuType.EARTH_FIVE,
    # 丙、丁 → 火
    "丙": WuXingJuType.FIRE_SIX,
    "丁": WuXingJuType.FIRE_SIX,
}


# 六十花甲纳音五行表
# 格式: {干支: 纳音五行}
NAYIN_WUXING_MAP = {
    # 甲子、乙丑 - 金
    "甲子": "金", "乙丑": "金",
    # 丙寅、丁卯 - 火
    "丙寅": "火", "丁卯": "火",
    # 戊辰、己巳 - 木
    "戊辰": "木", "己巳": "木",
    # 庚午、辛未 - 土
    "庚午": "土", "辛未": "土",
    # 壬申、癸酉 - 金
    "壬申": "金", "癸酉": "金",
    # 甲戌、乙亥 - 火
    "甲戌": "火", "乙亥": "火",
    # 丙子、丁丑 - 水
    "丙子": "水", "丁丑": "水",
    # 戊寅、己卯 - 土
    "戊寅": "土", "己卯": "土",
    # 庚辰、辛巳 - 金
    "庚辰": "金", "辛巳": "金",
    # 壬午、癸未 - 木
    "壬午": "木", "癸未": "木",
    # 甲申、乙酉 - 水
    "甲申": "水", "乙酉": "水",
    # 丙戌、丁亥 - 土
    "丙戌": "土", "丁亥": "土",
    # 戊子、己丑 - 火
    "戊子": "火", "己丑": "火",
    # 庚寅、辛卯 - 木
    "庚寅": "木", "辛卯": "木",
    # 壬辰、癸巳 - 水
    "壬辰": "水", "癸巳": "水",
    # 甲午、乙未 - 金
    "甲午": "金", "乙未": "金",
    # 丙申、丁酉 - 火
    "丙申": "火", "丁酉": "火",
    # 戊戌、己亥 - 木
    "戊戌": "木", "己亥": "木",
    # 庚子、辛丑 - 土
    "庚子": "土", "辛丑": "土",
    # 壬寅、癸卯 - 金
    "壬寅": "金", "癸卯": "金",
    # 甲辰、乙巳 - 火
    "甲辰": "火", "乙巳": "火",
    # 丙午、丁未 - 水
    "丙午": "水", "丁未": "水",
    # 戊申、己酉 - 土
    "戊申": "土", "己酉": "土",
    # 庚戌、辛亥 - 金
    "庚戌": "金", "辛亥": "金",
    # 壬子、癸丑 - 木
    "壬子": "木", "癸丑": "木",
    # 甲寅、乙卯 - 水
    "甲寅": "水", "乙卯": "水",
    # 丙辰、丁巳 - 土
    "丙辰": "土", "丁巳": "土",
    # 戊午、己未 - 火
    "戊午": "火", "己未": "火",
    # 庚申、辛酉 - 木
    "庚申": "木", "辛酉": "木",
    # 壬戌、癸亥 - 水
    "壬戌": "水", "癸亥": "水",
}


# 纳音五行到五行局的映射
NAYIN_TO_WUXING_JU = {
    "水": WuXingJuType.WATER_TWO,
    "木": WuXingJuType.WOOD_THREE,
    "金": WuXingJuType.GOLD_FOUR,
    "土": WuXingJuType.EARTH_FIVE,
    "火": WuXingJuType.FIRE_SIX,
}


# 五行局对应的起运年龄
# 第一大限的开始年龄
WUXING_JU_START_AGE = {
    WuXingJuType.WATER_TWO: 2,
    WuXingJuType.WOOD_THREE: 3,
    WuXingJuType.GOLD_FOUR: 4,
    WuXingJuType.EARTH_FIVE: 5,
    WuXingJuType.FIRE_SIX: 9,
}


# 天干列表
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支列表
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


@dataclass
class WuXingJuResult:
    """五行局计算结果"""
    wuxing_ju: WuXingJuType  # 五行局类型
    naiyin_wuxing: str        # 纳音五行
    start_age: int             # 起运年龄
    year_gan: str              # 年干


class WuXingCalculator:
    """五行局计算器"""

    @staticmethod
    def get_ganzhi_year(year: int) -> str:
        """
        根据公历年获取农历年干支

        Args:
            year: 公历年（如2024）

        Returns:
            农历年干支（如"甲辰"）
        """
        # 公元年份到干支的转换
        # 公式: (year - 4) % 60 得到甲子年的偏移
        # 甲子年对应公元4年
        offset = (year - 4) % 60
        gan_index = offset % 10
        zhi_index = offset % 12
        return TIANGAN[gan_index] + DIZHI[zhi_index]

    @staticmethod
    def get_year_gan(year: int) -> str:
        """
        获取年干

        Args:
            year: 公历年

        Returns:
            年干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）
        """
        ganzhi = WuXingCalculator.get_ganzhi_year(year)
        return ganzhi[0]

    @staticmethod
    def get_naiyin_wuxing(year_gan: str, year_zhi: str = None) -> str:
        """
        根据年干获取纳音五行

        Args:
            year_gan: 年干
            year_zhi: 年支（可选，如果提供则使用六十花甲表精确查找）

        Returns:
            纳音五行（金、木、水、火、土）
        """
        if year_zhi:
            ganzhi = year_gan + year_zhi
            if ganzhi in NAYIN_WUXING_MAP:
                return NAYIN_WUXING_MAP[ganzhi]

        # 简化版本：根据年干确定纳音五行
        # 这是因为同一年干的纳音五行是固定的
        year_gan_to_naiyin = {
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水",
        }
        return year_gan_to_naiyin.get(year_gan, "土")

    @classmethod
    def calculate_by_gan(cls, year_gan: str) -> WuXingJuResult:
        """
        根据年干计算五行局

        Args:
            year_gan: 年干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）

        Returns:
            五行局计算结果

        Raises:
            ValueError: 无效的年干
        """
        if year_gan not in TIANGAN_WUXING_JU_MAP:
            raise ValueError(f"无效的年干: {year_gan}")

        wuxing_ju = TIANGAN_WUXING_JU_MAP[year_gan]
        naiyin = cls.get_naiyin_wuxing(year_gan)
        start_age = WUXING_JU_START_AGE[wuxing_ju]

        return WuXingJuResult(
            wuxing_ju=wuxing_ju,
            naiyin_wuxing=naiyin,
            start_age=start_age,
            year_gan=year_gan
        )

    @classmethod
    def calculate_by_year(cls, year: int, month: int = 1, day: int = 1,
                          hour: int = 0, is_lunar: bool = False) -> WuXingJuResult:
        """
        根据出生年份计算五行局

        Args:
            year: 出生年份
            month: 出生月份（公历）
            day: 出生日期（公历）
            hour: 出生时辰（0-23）
            is_lunar: 是否为农历输入

        Returns:
            五行局计算结果
        """
        if is_lunar:
            # 农历转公历的逻辑需要额外的日历库
            # 这里简化处理，假设输入为公历
            pass

        year_gan = cls.get_year_gan(year)
        return cls.calculate_by_gan(year_gan)

    @classmethod
    def calculate_by_ganzhi(cls, ganzhi: str) -> WuXingJuResult:
        """
        根据年干支计算五行局

        Args:
            ganzhi: 年干支（如"甲辰"）

        Returns:
            五行局计算结果
        """
        if len(ganzhi) != 2:
            raise ValueError(f"无效的干支: {ganzhi}")

        year_gan = ganzhi[0]
        year_zhi = ganzhi[1]

        if year_zhi in NAYIN_WUXING_MAP:
            naiyin = NAYIN_WUXING_MAP[year_zhi]
            wuxing_ju = NAYIN_TO_WUXING_JU[naiyin]
            start_age = WUXING_JU_START_AGE[wuxing_ju]

            return WuXingJuResult(
                wuxing_ju=wuxing_ju,
                naiyin_wuxing=naiyin,
                start_age=start_age,
                year_gan=year_gan
            )

        return cls.calculate_by_gan(year_gan)

    @staticmethod
    def get_daxian_ranges(start_age: int, total_years: int = 80) -> list:
        """
        根据起运年龄计算各大限的年龄范围

        Args:
            start_age: 起运年龄
            total_years: 总年数（默认80年）

        Returns:
            大限年龄范围列表，如 [(2, 11), (12, 21), ...]
        """
        ranges = []
        current_age = start_age

        while current_age < total_years:
            end_age = min(current_age + 9, total_years)
            ranges.append((current_age, end_age))
            current_age = end_age + 1

        return ranges


def calculate_wuxing_ju(birth_year: int) -> dict:
    """
    便捷函数：根据出生年份计算五行局

    Args:
        birth_year: 出生年份

    Returns:
        五行局信息字典
    """
    result = WuXingCalculator.calculate_by_year(birth_year)
    return {
        "wuxing_ju": result.wuxing_ju.value,
        "naiyin_wuxing": result.naiyin_wuxing,
        "start_age": result.start_age,
        "year_gan": result.year_gan,
        "daxian_ranges": WuXingCalculator.get_daxian_ranges(result.start_age)
    }
