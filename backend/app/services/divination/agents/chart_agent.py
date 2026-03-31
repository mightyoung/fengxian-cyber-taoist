"""
ChartAgent - 紫微斗数排盘智能体

负责解析出生信息并协调各模块完成完整的紫微斗数排盘。

职责：
1. 解析出生信息（年/月/日/时/分、性别、出生地）
2. 协调各模块完成排盘：
   - wuxing_calculator.py - 计算五行局
   - palace_builder.py - 构建十二宫
   - star_placer.py - 安放星曜
   - transform_decider.py - 确定四化
3. 输出完整的命盘数据
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any
from enum import Enum

# 导入现有模块（使用相对导入）
from app.services.divination.wuxing_calculator import (
    WuXingCalculator,
    WuXingJuType,
    TIANGAN,
)
from app.services.divination.palace_builder import (
    PalaceBuilder,
)
from app.services.divination.star_placer import (
    StarPlacer,
    FiveElementType,
    StarType,
    PALACE_ORDER,
)
from app.services.divination.transform_decider import (
    TransformDecider,
)


class GenderType(str, Enum):
    """性别类型"""
    MALE = "male"
    FEMALE = "female"


@dataclass
class BirthInfo:
    """出生信息"""
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    gender: str = "male"
    birthplace: str = ""
    is_lunar: bool = False  # 是否农历

    def __post_init__(self):
        """验证出生信息"""
        if not (1900 <= self.year <= 2100):
            raise ValueError(f"无效的年份: {self.year}，应在1900-2100之间")
        if not (1 <= self.month <= 12):
            raise ValueError(f"无效的月份: {self.month}")
        if not (1 <= self.day <= 31):
            raise ValueError(f"无效的日期: {self.day}")
        if not (0 <= self.hour <= 23):
            raise ValueError(f"无效的小时: {self.hour}，应在0-23之间")
        if self.gender not in ["male", "female"]:
            raise ValueError(f"无效的性别: {self.gender}，应为'male'或'female'")


@dataclass
class PalaceData:
    """宫位数据"""
    name: str
    branch: str
    tiangan: str
    stars: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "branch": self.branch,
            "tiangan": self.tiangan,
            "stars": self.stars,
        }


@dataclass
class StarData:
    """星曜数据"""
    name: str
    palace: str
    level: str
    star_type: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "palace": self.palace,
            "level": self.level,
            "type": self.star_type,
            "description": self.description,
        }


@dataclass
class Chart:
    """完整命盘"""
    birth_info: Dict[str, Any]
    palaces: Dict[str, Any]
    stars: Dict[str, List[Dict[str, Any]]]
    transforms: List[Dict[str, Any]]
    chart_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "birth_info": self.birth_info,
            "palaces": self.palaces,
            "stars": self.stars,
            "transforms": self.transforms,
            "chart_timestamp": self.chart_timestamp,
        }


class ChartAgent:
    """
    排盘智能体

    协调各模块完成紫微斗数排盘，输出完整的命盘数据。
    """

    def __init__(self):
        """初始化排盘智能体"""
        self._wuxing_calc = WuXingCalculator()
        self._palace_builder = PalaceBuilder()
        self._transform_decider = TransformDecider()

    async def generate_chart(self, birth_info: BirthInfo) -> Chart:
        """
        生成完整命盘

        Args:
            birth_info: 出生信息

        Returns:
            Chart: 完整命盘数据

        Raises:
            ValueError: 当出生信息无效时
        """
        # 验证输入
        if not isinstance(birth_info, BirthInfo):
            raise ValueError("birth_info必须是BirthInfo类型")

        # 步骤1: 计算五行局
        wuxing_result = self._calculate_wuxing_ju(birth_info)

        # 步骤2: 计算年干
        year_gan = self._wuxing_calc.get_year_gan(birth_info.year)

        # 步骤3: 构建十二宫
        palaces_data = self._build_palaces(birth_info, year_gan)

        # 步骤4: 安放星曜
        stars_data = self._place_stars(birth_info, wuxing_result, palaces_data)

        # 步骤5: 确定四化
        transforms_data = self._determine_transforms(year_gan, palaces_data, stars_data)

        # 构建出生信息输出
        birth_info_dict = {
            "year": birth_info.year,
            "month": birth_info.month,
            "day": birth_info.day,
            "hour": birth_info.hour,
            "minute": birth_info.minute,
            "gender": birth_info.gender,
            "wuxing_ju": wuxing_result.wuxing_ju.value,
            "wuxing_ju_name": wuxing_result.wuxing_ju.value,
            "year_gan": year_gan,
            "birthplace": birth_info.birthplace,
        }

        # 构建完整命盘
        chart = Chart(
            birth_info=birth_info_dict,
            palaces=palaces_data,
            stars=stars_data,
            transforms=transforms_data,
            chart_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )

        return chart

    def _calculate_wuxing_ju(self, birth_info: BirthInfo) -> Any:
        """计算五行局"""
        result = self._wuxing_calc.calculate_by_year(birth_info.year)
        return result

    def _build_palaces(self, birth_info: BirthInfo, year_gan: str) -> Dict[str, Any]:
        """构建十二宫"""
        # 使用palace_builder构建宫位
        palace_result = self._palace_builder.build(birth_info.gender, year_gan)

        # 转换为字典格式
        palaces_dict = {}
        for palace in palace_result.palaces:
            palaces_dict[palace.name] = {
                "name": palace.name,
                "branch": palace.branch,
                "tiangan": "",  # 宫干稍后计算
                "stars": [],
            }

        # 计算各宫宫干
        palace_tiangan = self._calculate_palace_tiangan(birth_info.year)
        for palace_name, tiangan in palace_tiangan.items():
            if palace_name in palaces_dict:
                palaces_dict[palace_name]["tiangan"] = tiangan

        return palaces_dict

    def _calculate_palace_tiangan(self, year: int) -> Dict[str, str]:
        """计算各宫宫干"""
        year_gan_index = (year - 1900) % 10
        result = {}

        for i, palace in enumerate(PALACE_ORDER):
            gan_index = (year_gan_index + i) % 10
            result[palace] = TIANGAN[gan_index]

        return result

    def _place_stars(self, birth_info: BirthInfo, wuxing_result: Any, palaces_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """安放星曜"""
        # 转换五行局类型
        wuxing_ju_map = {
            WuXingJuType.WATER_TWO: FiveElementType.SHUI_ER,
            WuXingJuType.WOOD_THREE: FiveElementType.MU_SAN,
            WuXingJuType.GOLD_FOUR: FiveElementType.JIN_SI,
            WuXingJuType.EARTH_FIVE: FiveElementType.TU_WU,
            WuXingJuType.FIRE_SIX: FiveElementType.HUO_LIU,
        }

        wuxing_ju = wuxing_ju_map.get(wuxing_result.wuxing_ju, FiveElementType.SHUI_ER)

        # 使用star_placer安放星曜
        gender_display = "男" if birth_info.gender == "male" else "女"
        star_placer = StarPlacer(
            year=birth_info.year,
            month=birth_info.month,
            day=birth_info.day,
            hour=birth_info.hour,
            minute=birth_info.minute,
            wuxing_ju=wuxing_ju,
            gender=gender_display,
            is_yinli=birth_info.is_lunar,
        )

        # 获取排盘结果
        chart_result = star_placer.get_result()

        # 分类星曜
        main_stars = []
        auxiliary_stars = []
        sha_stars = []
        transform_stars = []

        # 遍历所有宫位，收集星曜
        for palace_name, palace_stars in chart_result.palaces.items():
            for star in palace_stars.stars:
                star_data = StarData(
                    name=star.name,
                    palace=palace_name,
                    level=star.level.value,
                    star_type=star.star_type.value,
                ).to_dict()

                if star.star_type == StarType.ZHENGYAO:
                    main_stars.append(star_data)
                elif star.star_type == StarType.FUXING:
                    auxiliary_stars.append(star_data)
                elif star.star_type == StarType.SAXING:
                    sha_stars.append(star_data)
                elif star.star_type == StarType.HUA_YAO:
                    transform_stars.append(star_data)

        # 同时更新palaces中的stars字段
        for palace_name, palace_stars in chart_result.palaces.items():
            if palace_name in palaces_data:
                palaces_data[palace_name]["stars"] = []
                for star in palace_stars.stars:
                    star_dict = {
                        "name": star.name,
                        "type": star.star_type.value,
                        "level": star.level.value,
                    }
                    palaces_data[palace_name]["stars"].append(star_dict)

        return {
            "main_stars": main_stars,
            "auxiliary_stars": auxiliary_stars,
            "sha_stars": sha_stars,
            "transform_stars": transform_stars,
        }

    def _determine_transforms(
        self,
        year_gan: str,
        palaces_data: Dict[str, Any],
        stars_data: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """确定四化"""
        transform_result = self._transform_decider.get_transform(year_gan)

        # 获取四化星所在的宫位
        transforms = []
        for transform in transform_result.transforms:
            star_name = transform.star_name

            # 查找星曜所在的宫位
            palace_name = None
            for category in ["main_stars", "auxiliary_stars"]:
                for star in stars_data.get(category, []):
                    if star["name"] == star_name:
                        palace_name = star["palace"]
                        break
                if palace_name:
                    break

            transforms.append({
                "type": transform.transform_type.value,
                "star": star_name,
                "palace": palace_name or "",
            })

        return transforms

    async def receive(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        接收消息（Agent通信协议）

        Args:
            message: 消息字典，应包含birth_info字段

        Returns:
            处理结果
        """
        try:
            birth_info_data = message.get("birth_info")
            if not birth_info_data:
                return {
                    "status": "error",
                    "message": "缺少birth_info字段",
                }

            birth_info = BirthInfo(**birth_info_data)
            chart = await self.generate_chart(birth_info)

            return {
                "status": "success",
                "data": chart.to_dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    async def respond(self, context: Dict[str, Any]) -> str:
        """
        响应消息（Agent通信协议）

        Args:
            context: 上下文信息

        Returns:
            响应文本
        """
        try:
            birth_info_data = context.get("birth_info")
            if not birth_info_data:
                return "请提供出生信息，包括年份、月份、日期、小时、性别。"

            birth_info = BirthInfo(**birth_info_data)
            chart = await self.generate_chart(birth_info)

            # 生成响应文本
            response = f"命盘已生成。\n"
            response += f"出生年份: {chart.birth_info['year']}年\n"
            response += f"五行局: {chart.birth_info['wuxing_ju_name']}\n"
            response += f"命宫主星: {', '.join([s['name'] for s in chart.stars['main_stars'] if s['palace'] == '命宫'])}\n"
            response += f"四化: {', '.join([t['type'] + t['star'] for t in chart.transforms])}"

            return response
        except Exception as e:
            return f"生成命盘时出错: {str(e)}"


# 便捷函数
async def generate_birth_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str,
    minute: int = 0,
    birthplace: str = "",
    is_lunar: bool = False,
) -> Dict[str, Any]:
    """
    生成紫微斗数命盘

    Args:
        year: 出生年份
        month: 出生月份
        day: 出生日期
        hour: 出生小时 (0-23)
        gender: 性别 ("male" 或 "female")
        minute: 出生分钟 (默认0)
        birthplace: 出生地 (可选)
        is_lunar: 是否农历 (默认False)

    Returns:
        命盘数据字典
    """
    birth_info = BirthInfo(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        gender=gender,
        birthplace=birthplace,
        is_lunar=is_lunar,
    )

    agent = ChartAgent()
    chart = await agent.generate_chart(birth_info)

    return chart.to_dict()


# 同步版本（兼容旧代码）
def generate_chart_sync(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str,
    minute: int = 0,
    birthplace: str = "",
    is_lunar: bool = False,
) -> Dict[str, Any]:
    """
    同步版本的命盘生成函数

    Args:
        year: 出生年份
        month: 出生月份
        day: 出生日期
        hour: 出生小时 (0-23)
        gender: 性别 ("male" 或 "female")
        minute: 出生分钟 (默认0)
        birthplace: 出生地 (可选)
        is_lunar: 是否农历 (默认False)

    Returns:
        命盘数据字典
    """
    return asyncio.run(generate_birth_chart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        gender=gender,
        minute=minute,
        birthplace=birthplace,
        is_lunar=is_lunar,
    ))


if __name__ == "__main__":
    # 测试示例
    async def main():
        print("=== 测试：生成命盘 ===")

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=30,
            gender="male",
            birthplace="北京",
        )

        agent = ChartAgent()
        chart = await agent.generate_chart(birth_info)

        print(f"出生信息: {chart.birth_info}")
        print(f"命宫: {chart.palaces.get('命宫', {})}")
        print(f"主星数量: {len(chart.stars['main_stars'])}")
        print(f"辅星数量: {len(chart.stars['auxiliary_stars'])}")
        print(f"煞星数量: {len(chart.stars['sha_stars'])}")
        print(f"化曜数量: {len(chart.stars['transform_stars'])}")
        print(f"四化: {chart.transforms}")

        # 测试便捷函数
        print("\n=== 测试：便捷函数 ===")
        chart2 = await generate_birth_chart(
            year=1995,
            month=8,
            day=20,
            hour=15,
            gender="female",
        )
        print(f"五行局: {chart2['birth_info']['wuxing_ju_name']}")

    asyncio.run(main())
