"""
星曜安放模块 - 紫微斗数排盘引擎

实现十四正曜、辅星、煞星、化曜的安放规则
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from copy import deepcopy


class PalaceType(Enum):
    """十二宫类型"""
    ZIWEI = "子午"      # 紫微宫
    TIANJI = "天机宫"
    TAIYANG = "太阳宫"
    WUQU = "武曲宫"
    TIANGTONG = "天同宫"
    LIANZHEN = "廉贞宫"
    TIANFU = "天府宫"
    TAIYIN = "太阴宫"
    TANLANG = "贪狼宫"
    JUMEN = "巨门宫"
    TIANXIANG = "天相宫"
    TIANLIANG = "天梁宫"
    QUSHA = "七杀宫"
    POJUN = "破军宫"

    # 辅助宫位
    MING = "命宫"
    FO = "父母宫"
    ZIFU = "子宫"
    TIANZHAI = "田宅宫"
    QIANTIAN = "乾天宫"  # 乾卦宫位
    KUNTIAN = "坤天宫"  # 坤卦宫位
    GUAITAN = "官禄宫"
    POCHA = "仆役宫"
    QICHANG = "七强宫"


class StarType(Enum):
    """星曜类型"""
    ZHENGYAO = "正曜"      # 十四正曜
    FUXING = "辅星"        # 辅曜
    SAXING = "煞星"        # 煞星
    HUA_YAO = "化曜"       # 化曜


class StarLevel(Enum):
    """星曜等级（庙旺陷）"""
    MIAO = "庙"   # 庙旺 - 最吉
    WANG = "旺"   # 旺 - 次吉
    PING = "平"   # 平 - 中等
    XIAN = "陷"   # 陷 - 凶


class FiveElementType(Enum):
    """五行局"""
    SHUI_ER = "水二局"
    MU_SAN = "木三局"
    JIN_SI = "金四局"
    TU_WU = "土五局"
    HUO_LIU = "火六局"


# 十二宫序号（顺时针）- 与 palace_builder.py 保持一致
PALACE_ORDER = [
    "命宫",       # 0
    "兄弟宫",     # 1
    "夫妻宫",     # 2
    "子女宫",     # 3
    "财帛宫",     # 4
    "疾厄宫",     # 5
    "迁移宫",     # 6
    "交友宫",     # 7 (与 palace_builder 保持一致)
    "官禄宫",     # 8
    "田宅宫",     # 9
    "福德宫",     # 10 (与 palace_builder 保持一致)
    "父母宫",     # 11 (与 palace_builder 保持一致)
]


# 宫干对应表（简化版）- 实际需要根据出生年份计算
PALACE_TIANGAN = {
    "命宫": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
    "兄弟宫": ["乙", "甲", "丁", "丙", "己", "戊", "辛", "庚", "癸", "壬"],
    "夫妻宫": ["丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙"],
    "子女宫": ["丁", "丙", "己", "戊", "辛", "庚", "癸", "壬", "乙", "甲"],
    "财帛宫": ["戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁"],
    "疾厄宫": ["己", "戊", "辛", "庚", "癸", "壬", "乙", "甲", "丁", "丙"],
    "迁移宫": ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"],
    "仆役宫": ["辛", "庚", "癸", "壬", "乙", "甲", "丁", "丙", "己", "戊"],
    "官禄宫": ["壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛"],
    "田宅宫": ["癸", "壬", "乙", "甲", "丁", "丙", "己", "戊", "庚", "辛"],
    "父母宫": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
    "福德宫": ["乙", "甲", "丁", "丙", "己", "戊", "辛", "庚", "癸", "壬"],
}


@dataclass
class Star:
    """星曜"""
    name: str
    star_type: StarType
    level: StarLevel = StarLevel.PING
    is_jiucang: bool = False  # 是否为九仓


@dataclass
class PalaceStars:
    """宫位星曜"""
    palace_name: str
    palace_index: int
    stars: List[Star] = field(default_factory=list)
    tiangan: str = ""  # 宫干

    def add_star(self, star: Star):
        """添加星曜"""
        self.stars.append(star)

    def has_star(self, star_name: str) -> bool:
        """检查是否包含某星曜"""
        return any(s.name == star_name for s in self.stars)


@dataclass
class ChartResult:
    """排盘结果"""
    palaces: Dict[str, PalaceStars] = field(default_factory=dict)
    wuxing_ju: FiveElementType = FiveElementType.SHUI_ER

    def get_palace(self, name: str) -> Optional[PalaceStars]:
        return self.palaces.get(name)

    def get_all_stars_in_palace(self, palace_name: str) -> List[str]:
        """获取宫位所有星曜名称"""
        palace = self.palaces.get(palace_name)
        if palace:
            return [s.name for s in palace.stars]
        return []


class StarPlacer:
    """星曜安放器"""

    # 十四正曜定义
    ZHENGYAO_BEIDOU = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞"]
    ZHENGYAO_NANDOU = ["天府", "太阴", "贪狼", "巨门", "天相", "天梁"]
    ZHENGYAO_ZHONGTIAN = ["七杀", "破军"]

    # 辅星定义
    FUXING = [
        "左辅", "右弼", "文昌", "文曲",
        "天魁", "天钺", "禄存", "天马",
        "火星", "铃星", "地空", "地劫"
    ]

    # 煞星定义
    SAXING = ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]

    # 化曜定义
    HUA_YAO = ["化禄", "化权", "化科", "化忌"]

    # 地支索引映射
    ZHI_INDEX = {
        "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
        "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11
    }

    # 时支索引（按顺时针顺序，从子时开始）
    SHI_ZHI_INDEX = {
        "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
        "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11
    }

    # 天干索引
    GAN_INDEX = {
        "甲": 0, "乙": 1, "丙": 2, "丁": 3, "戊": 4,
        "己": 5, "庚": 6, "辛": 7, "壬": 8, "癸": 9
    }

    # 年干阴阳
    YEAR_GAN_YINYANG = {
        "甲": True,  # 阳木
        "乙": False, # 阴木
        "丙": True,  # 阳火
        "丁": False, # 阴火
        "戊": True,  # 阳土
        "己": False, # 阴土
        "庚": True,  # 阳金
        "辛": False, # 阴金
        "壬": True,  # 阳水
        "癸": False, # 阴水
    }

    def __init__(self, year: int, month: int, day: int,
                 hour: int, minute: int,
                 wuxing_ju: FiveElementType = FiveElementType.SHUI_ER,
                 gender: str = "男",
                 is_yinli: bool = False):
        """
        初始化星曜安放器

        Args:
            year: 出生年
            month: 出生月
            day: 出生日
            hour: 出生时
            minute: 出生分
            wuxing_ju: 五行局
            gender: 性别（男/女）
            is_yinli: 是否阴历
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.wuxing_ju = wuxing_ju
        self.gender = gender
        self.is_yinli = is_yinli

        # 计算年干
        self.year_gan = self._get_year_gan()

        # 计算命宫位置
        self.ming_gong_index = self._calculate_ming_gong()

        # 计算宫干
        self.palace_tiangan = self._calculate_palace_tiangan()

        # 安放星曜
        self.result = self._place_all_stars()

    def _get_year_gan(self) -> str:
        """获取年干"""
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        gan_index = (self.year - 4) % 10
        return gan_list[gan_index]

    def _get_hour_zhi(self) -> int:
        """
        获取出生时辰的地支索引

        时支计算：子时(23-1点)=0, 丑时(1-3点)=1, ...
        """
        # 将小时转换为时辰索引
        # 子时: 23-1点, 丑时: 1-3点, 寅时: 3-5点, ...
        if self.hour >= 23 or self.hour < 1:
            return 0  # 子时
        elif 1 <= self.hour < 3:
            return 1  # 丑时
        elif 3 <= self.hour < 5:
            return 2  # 寅时
        elif 5 <= self.hour < 7:
            return 3  # 卯时
        elif 7 <= self.hour < 9:
            return 4  # 辰时
        elif 9 <= self.hour < 11:
            return 5  # 巳时
        elif 11 <= self.hour < 13:
            return 6  # 午时
        elif 13 <= self.hour < 15:
            return 7  # 未时
        elif 15 <= self.hour < 17:
            return 8  # 申时
        elif 17 <= self.hour < 19:
            return 9  # 酉时
        elif 19 <= self.hour < 21:
            return 10 # 戌时
        elif 21 <= self.hour < 23:
            return 11 # 亥时
        return 0

    def _calculate_ming_gong(self) -> int:
        """
        计算命宫位置

        中州派公式：命宫 = (月支 + 时支) % 12
        - 阳男阴女：顺时针（从寅开始）
        - 阴男阳女：逆时针（从寅开始）

        月支：寅=2, 卯=3, 辰=4, 巳=5, 午=6, 未=7, 申=8, 酉=9, 戌=10, 亥=11, 子=0, 丑=1
        """
        # 月支索引（寅为2，子为0）
        month_zhi_index = (self.month + 1) % 12 if self.month >= 1 else 0

        # 时支索引
        hour_zhi_index = self._get_hour_zhi()

        # 判断阴阳
        is_yang = self.YEAR_GAN_YINYANG.get(self.year_gan, True)

        # 判断顺逆
        # 阳男阴女：顺时针（+）
        # 阴男阳女：逆时针（-）
        is_clockwise = (self.gender == "男" and is_yang) or (self.gender == "女" and not is_yang)

        # 中州派公式：(月支 + 时支) % 12
        base_index = (month_zhi_index + hour_zhi_index) % 12

        # 从寅(索引2)开始计算
        yin_index = 2  # 寅的索引

        if is_clockwise:
            # 顺时针：从寅开始向后数
            ming_gong_index = (yin_index + base_index) % 12
        else:
            # 逆时针：从寅开始向前数
            ming_gong_index = (yin_index - base_index) % 12

        return ming_gong_index

    def _calculate_palace_tiangan(self) -> Dict[str, str]:
        """计算各宫宫干"""
        # 根据出生年份天干计算
        year_gan_index = (self.year - 1900) % 10

        result = {}
        for i, palace in enumerate(PALACE_ORDER):
            gan_index = (year_gan_index + i) % 10
            result[palace] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"][gan_index]

        return result

    def _get_zhengyao_position(self, star_name: str) -> int:
        """
        获取十四正曜的基础位置

        根据紫微斗数经典规则：
        - 紫微/天府在子午宫
        - 天机/太阴在丑未宫
        - 太阳/贪狼在寅申宫
        - 武曲/巨门在卯酉宫
        - 天同/天相在辰戌宫
        - 天梁/廉贞在巳亥宫
        - 七杀在子午宫
        - 破军在丑未宫
        """
        position_map = {
            # 北斗
            "紫微": 0,    # 子午宫
            "天机": 1,    # 丑未宫
            "太阳": 2,    # 寅申宫
            "武曲": 3,    # 卯酉宫
            "天同": 4,    # 辰戌宫
            "廉贞": 5,    # 巳亥宫
            # 南斗
            "天府": 0,    # 子午宫
            "太阴": 1,    # 丑未宫
            "贪狼": 2,    # 寅申宫
            "巨门": 3,    # 卯酉宫
            "天相": 4,    # 辰戌宫
            "天梁": 5,    # 巳亥宫
            # 中天
            "七杀": 0,    # 子午宫
            "破军": 1,    # 丑未宫
        }
        return position_map.get(star_name, 0)

    def _adjust_position_by_wuxing(self, base_pos: int, star_name: str) -> int:
        """
        根据五行局调整星曜位置

        五行局对星曜分布的影响：
        - 水二局：星曜多化水
        - 木三局：星曜多化木
        - 金四局：星曜多化金
        - 土五局：星曜多化土
        - 火六局：星曜多化火

        五行局调整规则（根据典籍）：
        - 水二局：星曜在水局宫位更强
        - 木三局：星曜在木局宫位更强
        - 金四局：星曜在金局宫位更强
        - 土五局：星曜在土局宫位更强
        - 火六局：星曜在火局宫位更强
        """
        # 五行局对应的宫位偏移
        wuxing_offset = {
            FiveElementType.SHUI_ER: 0,
            FiveElementType.MU_SAN: 1,
            FiveElementType.JIN_SI: 2,
            FiveElementType.TU_WU: 3,
            FiveElementType.HUO_LIU: 4,
        }

        offset = wuxing_offset.get(self.wuxing_ju, 0)

        # 根据星曜五行属性调整
        star_wuxing = self._get_star_wuxing(star_name)
        ju_wuxing = self._get_ju_wuxing(self.wuxing_ju)

        # 五行同类或相生关系，更吉利（得地），位置优化
        # 五行相克关系，不利（失地），位置调整
        if star_wuxing == ju_wuxing or self._is_xiangsheng(star_wuxing, ju_wuxing):
            # 得地或利地：星曜在适合的五行局，位置不变或微调
            return (base_pos + offset) % 12
        elif self._is_xiangke(star_wuxing, ju_wuxing):
            # 失地或陷地：星曜被五行局克制，位置调整
            return (base_pos - offset) % 12

        # 平地：位置正常偏移
        return (base_pos + offset) % 12

    def _get_star_wuxing(self, star_name: str) -> str:
        """获取星曜五行属性"""
        wuxing_map = {
            # 北斗
            "紫微": "土",
            "天机": "木",
            "太阳": "火",
            "武曲": "金",
            "天同": "水",
            "廉贞": "火",
            # 南斗
            "天府": "土",
            "太阴": "水",
            "贪狼": "木",
            "巨门": "土",
            "天相": "水",
            "天梁": "土",
            # 中天
            "七杀": "金",
            "破军": "水",
            # 辅星
            "左辅": "土",
            "右弼": "水",
            "文昌": "金",
            "文曲": "水",
            "禄存": "土",
            "天马": "火",
            "火星": "火",
            "铃星": "火",
            "地空": "火",
            "地劫": "金",
            # 煞星
            "擎羊": "金",
            "陀罗": "土",
        }
        return wuxing_map.get(star_name, "土")

    def _get_ju_wuxing(self, ju: FiveElementType) -> str:
        """获取五行局对应的五行"""
        wuxing_map = {
            FiveElementType.SHUI_ER: "水",
            FiveElementType.MU_SAN: "木",
            FiveElementType.JIN_SI: "金",
            FiveElementType.TU_WU: "土",
            FiveElementType.HUO_LIU: "火",
        }
        return wuxing_map.get(ju, "水")

    def _is_xiangsheng(self, wuxing1: str, wuxing2: str) -> bool:
        """判断是否相生"""
        xiangsheng_map = {
            "木": ["火"],
            "火": ["土"],
            "土": ["金"],
            "金": ["水"],
            "水": ["木"],
        }
        return wuxing2 in xiangsheng_map.get(wuxing1, [])

    def _is_xiangke(self, wuxing1: str, wuxing2: str) -> bool:
        """判断是否相克"""
        xiangke_map = {
            "木": ["土"],
            "土": ["水"],
            "水": ["火"],
            "火": ["金"],
            "金": ["木"],
        }
        return wuxing2 in xiangke_map.get(wuxing1, [])

    def _calculate_star_level(self, star_name: str, palace_index: int) -> StarLevel:
        """
        计算星曜的庙旺陷

        庙旺陷的判定规则：
        1. 星曜落入其旺相的宫位为"庙"
        2. 星曜落入其次旺的宫位为"旺"
        3. 星曜落入其平位的宫位为"平"
        4. 星曜落入其失陷的宫位为"陷"
        """
        # 定义各星曜的庙旺宫位
        miao_positions = {
            "紫微": [0, 6],    # 子、午宫庙
            "天机": [1, 7],    # 丑、未宫庙
            "太阳": [2, 8],    # 寅、申宫庙
            "武曲": [],        # 武曲无庙位，根据《飞星紫微斗数》卯酉为陷
            "天同": [4, 10],   # 辰、戌宫庙
            "廉贞": [5, 11],   # 巳、亥宫庙
            "天府": [6],       # 午宫庙（子为陷）
            "太阴": [1, 7],    # 丑、未宫庙
            "贪狼": [2, 8],    # 寅、申宫庙
            "巨门": [3, 9],    # 卯、酉宫庙
            "天相": [4, 10],   # 辰、戌宫庙
            "天梁": [5, 11],   # 巳、亥宫庙
            "七杀": [0, 6, 3, 9],  # 子午卯酉庙
            "破军": [1, 7, 4, 10],  # 丑未辰戌庙
        }

        # 旺位（次旺）
        wang_positions = {
            # 紫微: 去掉辰(4)戌(10)未(7)，保留丑寅卯等
            "紫微": [1, 2, 3, 5, 8, 9, 11],
            # 天机: 去掉子(0)午(6)亥(11)
            "天机": [2, 3, 4, 5, 8, 9, 10],
            # 太阳庙旺在寅申，其他为平
            "太阳": [0, 1, 3, 4, 5, 6, 7, 9, 10, 11],
        }

        # 陷位（失陷）- 根据《紫微斗数全书》《飞星紫微斗数》等典籍
        # 宫位索引: 子=0, 丑=1, 寅=2, 卯=3, 辰=4, 巳=5, 午=6, 未=7, 申=8, 酉=9, 戌=10, 亥=11
        xian_positions = {
            "紫微": [4, 7, 10],   # 未宫、辰戌宫陷
            "天机": [0, 6, 11],   # 亥宫、子午宫陷
            "武曲": [1, 3, 7, 9], # 卯酉宫、丑未宫陷
            "天同": [9],          # 酉宫陷
            "天府": [0, 1, 11],   # 亥子丑陷
            "太阴": [8, 9, 10, 11], # 申酉戌、亥宫陷
            "贪狼": [1, 4, 7, 10], # 辰戌丑未陷
        }

        positions = miao_positions.get(star_name, [])
        if palace_index in positions:
            return StarLevel.MIAO

        wang_pos = wang_positions.get(star_name, [])
        if palace_index in wang_pos:
            return StarLevel.WANG

        xian_pos = xian_positions.get(star_name, [])
        if palace_index in xian_pos:
            return StarLevel.XIAN

        return StarLevel.PING

    def _place_zhengyao(self) -> Dict[str, PalaceStars]:
        """安放十四正曜"""
        palaces = {}

        # 初始化所有宫位
        for i, palace_name in enumerate(PALACE_ORDER):
            palaces[palace_name] = PalaceStars(
                palace_name=palace_name,
                palace_index=i,
                tiangan=self.palace_tiangan.get(palace_name, "")
            )

        # 安放北斗六星
        for star_name in self.ZHENGYAO_BEIDOU:
            base_pos = self._get_zhengyao_position(star_name)
            adjusted_pos = self._adjust_position_by_wuxing(base_pos, star_name)
            palace = PALACE_ORDER[adjusted_pos]

            level = self._calculate_star_level(star_name, adjusted_pos)
            star = Star(name=star_name, star_type=StarType.ZHENGYAO, level=level)
            palaces[palace].add_star(star)

        # 安放南斗六星
        for star_name in self.ZHENGYAO_NANDOU:
            base_pos = self._get_zhengyao_position(star_name)
            # 南斗在命宫对面宫位
            adjusted_pos = (self.ming_gong_index + base_pos + 6) % 12
            palace = PALACE_ORDER[adjusted_pos]

            level = self._calculate_star_level(star_name, adjusted_pos)
            star = Star(name=star_name, star_type=StarType.ZHENGYAO, level=level)
            palaces[palace].add_star(star)

        # 安放中天二星
        for star_name in self.ZHENGYAO_ZHONGTIAN:
            base_pos = self._get_zhengyao_position(star_name)
            adjusted_pos = (self.ming_gong_index + base_pos) % 12
            palace = PALACE_ORDER[adjusted_pos]

            level = self._calculate_star_level(star_name, adjusted_pos)
            star = Star(name=star_name, star_type=StarType.ZHENGYAO, level=level)
            palaces[palace].add_star(star)

        return palaces

    def _place_fuxing(self, palaces: Dict[str, PalaceStars]) -> None:
        """安放辅星"""
        # 左辅右弼 - 随正曜
        zuofu_pos = (self.ming_gong_index + 1) % 12
        youbi_pos = (self.ming_gong_index + 11) % 12

        palaces[PALACE_ORDER[zuofu_pos]].add_star(
            Star("左辅", StarType.FUXING, StarLevel.WANG)
        )
        palaces[PALACE_ORDER[youbi_pos]].add_star(
            Star("右弼", StarType.FUXING, StarLevel.WANG)
        )

        # 文昌文曲
        wenchang_pos = (self.ming_gong_index + 4) % 12
        wenqu_pos = (self.ming_gong_index + 8) % 12

        palaces[PALACE_ORDER[wenchang_pos]].add_star(
            Star("文昌", StarType.FUXING, StarLevel.PING)
        )
        palaces[PALACE_ORDER[wenqu_pos]].add_star(
            Star("文曲", StarType.FUXING, StarLevel.PING)
        )

        # 天魁天钺
        tiankui_pos = (self.ming_gong_index + 3) % 12
        tianyue_pos = (self.ming_gong_index + 9) % 12

        palaces[PALACE_ORDER[tiankui_pos]].add_star(
            Star("天魁", StarType.FUXING, StarLevel.WANG)
        )
        palaces[PALACE_ORDER[tianyue_pos]].add_star(
            Star("天钺", StarType.FUXING, StarLevel.WANG)
        )

        # 禄存 - 根据宫干
        for i, palace_name in enumerate(PALACE_ORDER):
            tiangan = self.palace_tiangan.get(palace_name, "")
            if tiangan in ["甲", "丙", "戊", "庚", "壬"]:
                palaces[palace_name].add_star(
                    Star("禄存", StarType.FUXING, StarLevel.MIAO)
                )

        # 天马 - 驿马位
        tianma_pos = self._get_tianma_position()
        if tianma_pos is not None:
            palaces[PALACE_ORDER[tianma_pos]].add_star(
                Star("天马", StarType.FUXING, StarLevel.WANG)
            )

    def _place_saxing(self, palaces: Dict[str, PalaceStars]) -> None:
        """安放煞星"""
        # 擎羊陀罗 - 对宫
        qingyang_pos = (self.ming_gong_index + 1) % 12
        tuoluo_pos = (self.ming_gong_index + 11) % 12

        palaces[PALACE_ORDER[qingyang_pos]].add_star(
            Star("擎羊", StarType.SAXING, StarLevel.XIAN)
        )
        palaces[PALACE_ORDER[tuoluo_pos]].add_star(
            Star("陀罗", StarType.SAXING, StarLevel.XIAN)
        )

        # 火星铃星
        huoxing_pos = (self.ming_gong_index + 6) % 12
        lingxing_pos = (self.ming_gong_index + 2) % 12

        palaces[PALACE_ORDER[huoxing_pos]].add_star(
            Star("火星", StarType.SAXING, StarLevel.XIAN)
        )
        palaces[PALACE_ORDER[lingxing_pos]].add_star(
            Star("铃星", StarType.SAXING, StarLevel.XIAN)
        )

        # 地空地劫
        dikong_pos = (self.ming_gong_index + 4) % 12
        dijie_pos = (self.ming_gong_index + 10) % 12

        palaces[PALACE_ORDER[dikong_pos]].add_star(
            Star("地空", StarType.SAXING, StarLevel.XIAN)
        )
        palaces[PALACE_ORDER[dijie_pos]].add_star(
            Star("地劫", StarType.SAXING, StarLevel.XIAN)
        )

    def _place_hua_yao(self, palaces: Dict[str, PalaceStars]) -> None:
        """
        安放化曜

        根据年干四化飞星规则（根据紫微斗数典籍）：
        - 甲年：廉贞化禄、武曲化权、太阳化科、太阴化忌
        - 乙年：天机化禄、天梁化权、紫微化科、天机化忌
        - 丙年：天同化禄、天机化权、廉贞化科、天同化忌
        - 丁年：紫微化禄、天同化权、天机化科、紫微化忌
        - 戊年：贪狼化禄、太阴化权、右弼化科、天机化忌
        - 己年：武曲化禄、贪狼化权、太阴化科、武曲化忌
        - 庚年：太阳化禄、武曲化权、天府化科、太阳化忌
        - 辛年：巨门化禄、太阳化权、天府化科、巨门化忌
        - 壬年：天梁化禄、天机化权、紫微化科、天梁化忌
        - 癸年：天机化禄、巨门化权、紫微化科、天机化忌
        """
        # 年干四化映射表（根据紫微斗数典籍）
        # 一星不可化两曜，化禄和化忌可以同星
        year_stem_transforms = {
            "甲": {"化禄": "廉贞", "化权": "破军", "化科": "太阳", "化忌": "太阴"},
            "乙": {"化禄": "廉贞", "化权": "破军", "化科": "武曲", "化忌": "太阳"},
            "丙": {"化禄": "天同", "化权": "天梁", "化科": "太阳", "化忌": "天同"},
            "丁": {"化禄": "天同", "化权": "天梁", "化科": "天机", "化忌": "太阴"},
            "戊": {"化禄": "贪狼", "化权": "太阴", "化科": "右弼", "化忌": "天机"},
            "己": {"化禄": "武曲", "化权": "贪狼", "化科": "太阴", "化忌": "武曲"},
            "庚": {"化禄": "太阳", "化权": "武曲", "化科": "天府", "化忌": "太阳"},
            "辛": {"化禄": "巨门", "化权": "太阳", "化科": "天府", "化忌": "巨门"},
            "壬": {"化禄": "天梁", "化权": "天机", "化科": "紫微", "化忌": "天梁"},
            "癸": {"化禄": "天机", "化权": "巨门", "化科": "紫微", "化忌": "天机"},
        }

        # 获取该年干的四化
        transforms = year_stem_transforms.get(self.year_gan, {})

        # 为每个化曜找到其主星所在的宫位，并添加化曜
        for hua_type, star_name in transforms.items():
            for palace_name, palace_stars in palaces.items():
                if palace_stars.has_star(star_name):
                    # 根据化曜类型设置等级
                    if hua_type == "化禄":
                        level = StarLevel.MIAO
                    elif hua_type == "化权":
                        level = StarLevel.WANG
                    elif hua_type == "化科":
                        level = StarLevel.PING
                    else:  # 化忌
                        level = StarLevel.XIAN

                    palaces[palace_name].add_star(
                        Star(hua_type, StarType.HUA_YAO, level)
                    )
                    break

    def _get_tianma_position(self) -> Optional[int]:
        """
        计算天马位置

        天马驿马位计算规则（根据典籍）：
        - 申子辰马在寅（出生在申月、子月、辰月，天马在寅宫）
        - 巳酉丑马在亥
        - 寅午戌马在申
        - 亥卯未马在巳

        结合日期调整：
        - 上半月出生的，天马在前一个宫位
        - 下半月出生的，天马在后一个宫位
        """
        # 获取年月计算基础天马位置
        # 申子辰马在寅(2)
        if self.month in [3, 6, 9]:
            base_pos = 2
        # 巳酉丑马在亥(11)
        elif self.month in [4, 8, 12]:
            base_pos = 11
        # 寅午戌马在申(8)
        elif self.month in [1, 5, 7]:
            base_pos = 8
        # 亥卯未马在巳(5)
        elif self.month in [2, 10, 11]:
            base_pos = 5
        else:
            return None

        # 结合日期调整
        # 一个月约30天，上半月(1-15)偏前，下半月(16-31)偏后
        if 1 <= self.day <= 15:
            # 上半月，天马在前
            adjusted_pos = (base_pos - 1) % 12
        else:
            # 下半月，天马在后
            adjusted_pos = (base_pos + 1) % 12

        return adjusted_pos

    def _place_all_stars(self) -> ChartResult:
        """安放所有星曜"""
        # 初始化结果
        result = ChartResult(wuxing_ju=self.wuxing_ju)

        # 安放十四正曜
        result.palaces = self._place_zhengyao()

        # 安放辅星
        self._place_fuxing(result.palaces)

        # 安放煞星
        self._place_saxing(result.palaces)

        # 安放化曜
        self._place_hua_yao(result.palaces)

        return result

    def get_result(self) -> ChartResult:
        """获取排盘结果"""
        return self.result

    def get_ming_gong_stars(self) -> List[str]:
        """获取命宫星曜"""
        return self.result.get_all_stars_in_palace("命宫")

    def get_palace_stars(self, palace_name: str) -> List[str]:
        """获取指定宫位星曜"""
        return self.result.get_all_stars_in_palace(palace_name)

    def get_star_palace(self, star_name: str) -> Optional[str]:
        """获取指定星曜所在的宫位"""
        for palace_name, palace in self.result.palaces.items():
            if palace.has_star(star_name):
                return palace_name
        return None

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {
            "birth_info": {
                "year": self.year,
                "month": self.month,
                "day": self.day,
                "hour": self.hour,
                "minute": self.minute,
                "wuxing_ju": self.wuxing_ju.value,
                "gender": self.gender,
            },
            "palaces": {},
            "ming_gong_stars": self.get_ming_gong_stars(),
        }

        for palace_name, palace in self.result.palaces.items():
            result["palaces"][palace_name] = {
                "tiangan": palace.tiangan,
                "stars": [
                    {
                        "name": s.name,
                        "type": s.star_type.value,
                        "level": s.level.value,
                    }
                    for s in palace.stars
                ],
            }

        return result


def place_stars(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    wuxing_ju: str = "水二局",
    gender: str = "男",
    is_yinli: bool = False
) -> dict:
    """
    星曜安放入口函数

    Args:
        year: 出生年
        month: 出生月
        day: 出生日
        hour: 出生时
        minute: 出生分
        wuxing_ju: 五行局 (水二局/木三局/金四局/土五局/火六局)
        gender: 性别 (男/女)
        is_yinli: 是否阴历

    Returns:
        排盘结果字典
    """
    # 转换五行局
    wuxing_ju_map = {
        "水二局": FiveElementType.SHUI_ER,
        "木三局": FiveElementType.MU_SAN,
        "金四局": FiveElementType.JIN_SI,
        "土五局": FiveElementType.TU_WU,
        "火六局": FiveElementType.HUO_LIU,
    }

    ju = wuxing_ju_map.get(wuxing_ju, FiveElementType.SHUI_ER)

    placer = StarPlacer(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        wuxing_ju=ju,
        gender=gender,
        is_yinli=is_yinli
    )

    return placer.to_dict()
