"""
命盘数据访问工具模块

提供统一的数据访问接口，处理星曜数据在 dict 和 string 数组之间的转换
"""

from typing import Any, Dict, List, Union, Optional


class ChartDataHelper:
    """命盘数据访问辅助类

    提供统一的方法来访问和处理命盘中的星曜数据。
    统一处理星曜数据可能是 dict 对象数组或字符串数组的情况。
    """

    @staticmethod
    def extract_star_names(stars_data: Union[List[Dict[str, Any]], List[str], Any]) -> List[str]:
        """从星曜数据中提取名称列表

        处理两种数据格式:
        - dict 数组: [{"name": "天同", ...}, {"name": "天相", ...}]
        - 字符串数组: ["天同", "天相"]

        Args:
            stars_data: 星曜数据，可以是 dict 数组、字符串数组或其他

        Returns:
            星曜名称字符串列表
        """
        if not stars_data:
            return []

        result = []
        for star in stars_data:
            if isinstance(star, dict):
                name = star.get('name', '')
                if name:
                    result.append(name)
            elif isinstance(star, str) and star:
                result.append(star)

        return result

    @staticmethod
    def get_palace_stars(
        palace_data: Union[Dict[str, Any], List, None],
        as_names: bool = True
    ) -> Union[List[str], List[Dict[str, Any]]]:
        """获取宫位星曜数据

        Args:
            palace_data: 宫位数据，可以是包含 'stars' 键的 dict 或星曜列表
            as_names: 是否只返回星曜名称列表，False 时返回原始星曜数据

        Returns:
            星曜名称列表（as_names=True）或原始星曜数据列表（as_names=False）
        """
        if palace_data is None:
            return [] if as_names else []

        # 如果是列表，直接处理
        if isinstance(palace_data, list):
            if as_names:
                return ChartDataHelper.extract_star_names(palace_data)
            return palace_data

        # 如果是 dict，尝试获取 stars 字段
        if isinstance(palace_data, dict):
            stars = palace_data.get('stars', [])
            if as_names:
                return ChartDataHelper.extract_star_names(stars)
            return stars

        return [] if as_names else []

    @staticmethod
    def build_palace_stars_dict(
        chart_palaces: Optional[Dict[str, Any]],
        as_names: bool = True
    ) -> Dict[str, List[str]]:
        """从命盘构建宫位星曜字典

        统一处理命盘中所有宫位的星曜数据提取。

        Args:
            chart_palaces: 命盘宫位数据，格式如 {"命宫": {"stars": [...]}, "兄弟宫": {...}, ...}
            as_names: 是否只返回星曜名称列表

        Returns:
            宫位名称到星曜列表的字典，格式如 {"命宫": ["天同", "天相"], "兄弟宫": [...]}
        """
        if not chart_palaces:
            return {}

        result = {}
        for palace_name, palace_data in chart_palaces.items():
            if isinstance(palace_data, dict):
                result[palace_name] = ChartDataHelper.get_palace_stars(palace_data, as_names)
            elif isinstance(palace_data, list):
                # 直接是星曜列表的情况
                if as_names:
                    result[palace_name] = ChartDataHelper.extract_star_names(palace_data)
                else:
                    result[palace_name] = palace_data
            else:
                result[palace_name] = [] if as_names else []

        return result

    @staticmethod
    def get_palace_star_names(palace_data: Union[Dict[str, Any], List, None]) -> List[str]:
        """获取宫位星曜名称的便捷方法

        Args:
            palace_data: 宫位数据

        Returns:
            星曜名称列表
        """
        return ChartDataHelper.get_palace_stars(palace_data, as_names=True)

    @staticmethod
    def has_star(palace_data: Union[Dict[str, Any], List, None], star_name: str) -> bool:
        """检查宫位是否包含指定星曜

        Args:
            palace_data: 宫位数据
            star_name: 要检查的星曜名称

        Returns:
            是否包含该星曜
        """
        star_names = ChartDataHelper.get_palace_star_names(palace_data)
        return star_name in star_names

    @staticmethod
    def find_star_palace(
        chart_palaces: Optional[Dict[str, Any]],
        star_name: str
    ) -> Optional[str]:
        """查找指定星曜所在的宫位

        Args:
            chart_palaces: 命盘宫位数据
            star_name: 要查找的星曜名称

        Returns:
            星曜所在的宫位名称，如果未找到返回 None
        """
        if not chart_palaces:
            return None

        palace_stars = ChartDataHelper.build_palace_stars_dict(chart_palaces, as_names=True)

        for palace_name, stars in palace_stars.items():
            if star_name in stars:
                return palace_name

        return None
