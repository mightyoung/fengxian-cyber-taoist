"""
TimingAgent - 运限时间节点分析

负责分析大限、流年、流月、流日、流时各级时间预测
- 大限(10年)枢纽宫分析
- 流年太岁宫位系统
- 流曜系统(博士十二神、将前十神、岁前十二神)
- 应期/克应规则

模块化结构：
- timing_constants.py: 常量定义（干支、宫位、四化映射表、流曜序列）
- timing_types.py: 类型定义（enums、dataclasses）
- timing_core.py: 核心计算函数（四化计算、成住坏空阶段）
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import from modular components
from .timing_constants import (
    CYCLE_STAGE_PALACE_MAP,
)
from .timing_types import (
    MajorFate,
    YearFate,
    TimingAnalysis,
)
from .cache_decorator import cached_chart_analysis
from .timing_core import (
    get_yearly_transforms,
    get_birth_transforms,
    get_cycle_stage_for_palace,
    get_transform_cycle_impact,
)

# Try to import from parent module, fallback to any
try:
    from ..star_placer import ChartResult
    from ..palace_builder import TwelvePalaces, EARTHLY_BRANCHES
except ImportError:
    ChartResult = Any
    TwelvePalaces = Any
    EARTHLY_BRANCHES = []


# ============ Timing Rules Loader ============

def load_timing_rules() -> Dict[str, Any]:
    """加载流曜和大运规则"""
    base_path = Path(__file__).parent.parent.parent.parent / "data_source" / "mlx" / "data" / "knowledge" / "timing"

    rules = {
        "fate_period": {},
        "liu_yao": {},
        "tai_sui": {},
        "ying_qi": {},
        "ke_ying": {}
    }

    # Load fate period rules
    fate_file = base_path / "fate-period-timing.json"
    if fate_file.exists():
        with open(fate_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            rules["fate_period"] = data.get("fate_period_rules", {})
            rules["liu_yao"] = data.get("liu_yao_system", {})

    # Load liu yao system
    liu_yao_file = base_path / "liu-yao-system.json"
    if liu_yao_file.exists():
        with open(liu_yao_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            rules["liu_yao"].update(data)

    # Load tai sui system
    tai_sui_file = base_path / "tai-sui-system.json"
    if tai_sui_file.exists():
        with open(tai_sui_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            rules["tai_sui"] = data

    # Load ying qi timing
    ying_qi_file = base_path / "ying-qi-timing.json"
    if ying_qi_file.exists():
        with open(ying_qi_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            rules["ying_qi"] = data

    # Load ke ying rules
    ke_ying_file = base_path / "ke-ying-rules.json"
    if ke_ying_file.exists():
        with open(ke_ying_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            rules["ke_ying"] = data

    return rules


# ============ Timing Agent ============

class TimingAgent:
    """
    时间分析代理

    负责分析命盘的各级运限:
    - 大限分析(10年周期)
    - 流年分析(1年周期)
    - 流月/流日/流时分析
    - 太岁宫位系统
    - 流曜系统分析
    """

    def __init__(self, chart_data: ChartResult):
        """
        初始化时间分析代理

        Args:
            chart_data: 命盘数据
        """
        self.chart = chart_data
        self.timing_rules = load_timing_rules()

        # 地支对应宫位映射
        self.zhi_to_palace = {
            "子": "命宫", "丑": "兄弟宫", "寅": "夫妻宫", "卯": "子女宫",
            "辰": "财帛宫", "巳": "疾厄宫", "午": "迁移宫", "未": "交友宫",
            "申": "官禄宫", "酉": "田宅宫", "戌": "福德宫", "亥": "父母宫"
        }

        # 命宫地支(根据出生年份)
        self.life_palace_zhi = self._get_life_palace_zhi()

    def _get_life_palace_zhi(self) -> str:
        """获取命宫地支（根据出生月时计算）"""
        try:
            birth_month = getattr(self.chart, 'birth_month', None)
            birth_hour = getattr(self.chart, 'birth_hour', None)
            if birth_month and birth_hour:
                return self._calculate_life_palace_zhi(birth_month, birth_hour)
            # Fallback: use birth year only
            if hasattr(self.chart, 'birth_year') and self.chart.birth_year:
                return self._year_to_zhi(self.chart.birth_year)
        except Exception:
            pass
        return "子"  # Default

    def _year_to_zhi(self, year: int) -> str:
        """将年份转换为地支"""
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        return zhi_list[(year - 4) % 12]

    def _get_gan_zhi(self, year: int) -> str:
        """获取年份的干支"""
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        gan = gan_list[(year - 4) % 10]
        zhi = zhi_list[(year - 4) % 12]
        return f"{gan}{zhi}"

    def _zhi_to_index(self, zhi: str) -> int:
        """地支转索引"""
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        return zhi_list.index(zhi) if zhi in zhi_list else 0

    def _index_to_zhi(self, idx: int) -> str:
        """索引转地支"""
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        return zhi_list[idx % 12]

    def _calculate_life_palace_zhi(self, birth_month: int, birth_hour: int) -> str:
        """
        根据出生月时计算命宫地支（中州派公式）

        命宫 = (月支 + 时支) 逆数
        即：先计算月支和时支之和对应的地支位置，再逆数一位

        Args:
            birth_month: 出生月份(1-12)
            birth_hour: 出生时辰(1-12对应子-亥)

        Returns:
            命宫地支
        """
        # 地支顺序：子丑寅卯辰巳午未申酉戌亥
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

        # 时支计算：时辰对应地支
        # 子时(23-1点)=0, 丑时(1-3点)=1, 寅时(3-5点)=2, ...
        # 简化：时辰序号(1-12)对应子-亥
        hour_zhi_idx = (birth_hour - 1) % 12

        # 月支计算：月份对应地支
        # 正月=寅, 二月=卯, 三月=辰, 四月=巳, 五月=午, 六月=未
        # 七月=申, 八月=酉, 九月=戌, 十月=亥, 十一月=子, 十二月=丑
        month_zhi_base = 2  # 正月=寅的索引
        month_zhi_idx = (birth_month + month_zhi_base - 2) % 12

        # 中州派公式: (月支 + 时支) 逆数
        # 先计算两者之和
        combined_idx = (month_zhi_idx + hour_zhi_idx) % 12

        # 逆数：combined_idx 位置逆时针的第一个地支
        life_zhi_idx = (combined_idx - 1) % 12

        return zhi_list[life_zhi_idx]

    def _get_year_life_palace(self, year: int) -> str:
        """
        获取流年命宫

        流年命宫 = 流年太岁逆数3宫

        Args:
            year: 流年年份

        Returns:
            流年命宫名称
        """
        palace_names = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                       "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]

        # 流年地支
        year_zhi = self._year_to_zhi(year)

        # 流年太岁所在宫位
        tai_sui_palace = self.zhi_to_palace.get(year_zhi, "命宫")
        tai_sui_idx = palace_names.index(tai_sui_palace)

        # 流年命宫 = 太岁逆数3宫
        year_life_palace_idx = (tai_sui_idx - 3) % 12

        return palace_names[year_life_palace_idx]

    def _get_tai_sui_palace(self, year: int) -> str:
        """
        获取流年太岁落宫

        太岁与流年地支相同：
        - 子年太岁在子（命宫）
        - 丑年太岁在丑（兄弟宫）
        - 寅年太岁在寅（夫妻宫）
        - 卯年太岁在卯（子女宫）
        - 辰年太岁在辰（财帛宫）
        - 巳年太岁在巳（疾厄宫）
        - 午年太岁在午（迁移宫）
        - 未年太岁在未（交友宫）
        - 申年太岁在申（官禄宫）
        - 酉年太岁在酉（田宅宫）
        - 戌年太岁在戌（福德宫）
        - 亥年太岁在亥（父母宫）

        Args:
            year: 流年年份

        Returns:
            太岁落宫名称
        """
        # 流年地支即为太岁所在宫位
        zhi = self._year_to_zhi(year)
        return self.zhi_to_palace.get(zhi, "命宫")

    def _get_tai_sui_palace_for_year(self, year: int, life_palace_zhi: str) -> str:
        """
        根据命宫地支计算太岁落宫（完整版）

        当需要考虑命宫位置时使用此方法。
        太岁按地支顺序流转，与命宫位置形成特定关系。

        Args:
            year: 流年年份
            life_palace_zhi: 命宫地支

        Returns:
            太岁落宫名称
        """
        # 年份地支
        year_zhi = self._year_to_zhi(year)

        # 地支对应宫位（命宫固定在子）
        zhi_to_palace = {
            "子": "命宫", "丑": "兄弟宫", "寅": "夫妻宫", "卯": "子女宫",
            "辰": "财帛宫", "巳": "疾厄宫", "午": "迁移宫", "未": "交友宫",
            "申": "官禄宫", "酉": "田宅宫", "戌": "福德宫", "亥": "父母宫"
        }

        return zhi_to_palace.get(year_zhi, "命宫")

    def _get_tai_sui_relationship(self, tai_sui_palace: str) -> str:
        """获取太岁与命宫的关系"""
        life_palace = "命宫"
        palace_names = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                       "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]

        try:
            tai_idx = palace_names.index(tai_sui_palace)
            life_idx = palace_names.index(life_palace)

            # 对宫关系(相隔6宫)
            if abs(tai_idx - life_idx) == 6:
                return "冲本宫"
            # 三合关系(相隔4或8宫)
            elif abs(tai_idx - life_idx) in [4, 8]:
                return "三合"
            # 本宫
            elif tai_idx == life_idx:
                return "入本宫"
            # 相邻宫位(拱照)
            elif abs(tai_idx - life_idx) in [1, 11]:
                return "拱照"
            else:
                return "其他"
        except Exception:
            return "入本宫"

    def calculate_major_fate(self, birth_year: int, gender: str = "男") -> List[MajorFate]:
        """
        计算大限（逆数法）

        紫微斗数大限计算规则（基于中州派典籍）：
        1. 先根据出生月份和时辰确定命宫实际位置
        2. 阳男阴女从命宫起逆数，阴男阳女从夫妻宫起逆数
        3. 大限按逆时针方向依次排列（逆数）
        4. 每个大限10年

        Args:
            birth_year: 出生年份
            gender: 性别

        Returns:
            大限列表
        """
        major_fates = []

        # 阳男阴女判断
        # 年干阴阳：甲丙戊庚壬为阳，乙丁己辛癸为阴
        yang_stems = ["甲", "丙", "戊", "庚", "壬"]

        # 通过出生年获取年干
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        year_gan = gan_list[(birth_year - 4) % 10]
        is_yang_stem = year_gan in yang_stems

        palace_names = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                       "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]

        # 根据出生月时计算命宫地支
        birth_month = getattr(self.chart, 'birth_month', 1)
        birth_hour = getattr(self.chart, 'birth_hour', 1)
        life_palace_zhi = self._calculate_life_palace_zhi(birth_month, birth_hour)

        # 命宫地支对应的宫位索引
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        life_palace_zhi_idx = zhi_list.index(life_palace_zhi)
        life_palace_idx = palace_names.index(self.zhi_to_palace.get(life_palace_zhi, "命宫"))

        # 起大限宫位判断
        # 阳男阴女从命宫起逆数，阴男阳女从夫妻宫起逆数
        if (is_yang_stem and gender == "男") or (not is_yang_stem and gender == "女"):
            start_palace_idx = life_palace_idx  # 从命宫起
        else:
            start_palace_idx = 2  # 从夫妻宫起

        # 获取命宫星曜用于判断主星系统
        ming_gong_stars = self._get_palace_stars("命宫")
        star_system, hub_star = self._identify_star_system(ming_gong_stars)

        # 计算每个大限（逆时针方向：index减小）
        for i in range(12):
            # 逆数：start_palace_idx - i（而不是+i）
            # 这样第一个大限在命宫，第二个大限在父母宫（逆时针方向）
            palace_idx = (start_palace_idx - i) % 12
            start_age = i * 10 + 1
            end_age = (i + 1) * 10

            # 获取枢纽宫位(根据中州派理论)
            hub_palace = self._get_hub_palace(i)

            # 获取大限内的星曜
            stars = self._get_major_fate_stars(palace_names[palace_idx])

            # 获取该大限的四化信息（基于生年四化）
            transformation = self._get_major_fate_transformation_info(birth_year, i)

            major_fates.append(MajorFate(
                index=i + 1,
                start_age=start_age,
                end_age=end_age,
                palace=palace_names[palace_idx],
                hub_palace=hub_palace,
                star_system=star_system,
                hub_star=hub_star,
                stars=stars,
                transformation=transformation["main_transform"],
                description=f"第{i+1}大限({start_age}-{end_age}岁)，{palace_names[palace_idx]}{transformation['description']}"
            ))

        return major_fates

    def _get_hub_palace(self, major_fate_index: int) -> str:
        """
        根据中州派理论获取大限枢纽宫位

        中州派枢纽宫判断规则：
        1. 命宫主星为紫微星系（紫微独坐或紫微为主）：以紫微所在宫为枢纽
        2. 命宫主星为天府星系（天府独坐或天府为主）：以天府所在宫为枢纽
        3. 命宫主星为杀破狼星系（七杀、破军、贪狼）：以七杀所在宫为枢纽
        4. 若命宫无主要主星，以大限所在宫本身为枢纽

        Args:
            major_fate_index: 大限序号(0-11)

        Returns:
            枢纽宫位名称
        """
        palace_names = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                       "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]

        # 首先获取命宫星曜，判断主星类型
        ming_gong_stars = self._get_palace_stars("命宫")

        # 根据主星类型确定枢纽宫
        hub_palace = self._determine_hub_by_star_system(ming_gong_stars)
        if hub_palace:
            return hub_palace

        # 默认：枢纽宫为大限所在宫
        return palace_names[major_fate_index]

    def _get_palace_stars(self, palace_name: str) -> List[str]:
        """获取指定宫位的星曜列表"""
        try:
            if hasattr(self.chart, 'palaces') and self.chart.palaces:
                # chart.palaces can be dict or list
                if isinstance(self.chart.palaces, dict):
                    palace = self.chart.palaces.get(palace_name)
                    if palace:
                        if hasattr(palace, 'stars'):
                            return [s.name if hasattr(s, 'name') else str(s) for s in palace.stars]
                        elif isinstance(palace, dict) and 'stars' in palace:
                            return [s.get('name', str(s)) if isinstance(s, dict) else str(s) for s in palace.get('stars', [])]
                elif isinstance(self.chart.palaces, list):
                    for p in self.chart.palaces:
                        if p.get("name") == palace_name:
                            return p.get("stars", [])
        except Exception as e:
            pass
        return []

    def _find_star_palace(self, star_name: str) -> Optional[str]:
        """查找星曜所在的宫位"""
        palace_names = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                       "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]

        for palace_name in palace_names:
            stars = self._get_palace_stars(palace_name)
            if star_name in stars:
                return palace_name
        return None

    def _determine_hub_by_star_system(self, ming_gong_stars: List[str]) -> Optional[str]:
        """
        根据命宫主星类型确定枢纽宫

        Args:
            ming_gong_stars: 命宫星曜列表

        Returns:
            枢纽宫位，若无法确定则返回None
        """
        if not ming_gong_stars:
            return None

        # 中州派星系分类
        ZIWEI_STARS = ["紫微"]  # 紫微星系
        TIANFU_STARS = ["天府"]  # 天府星系
        SHA_PO_LANG_STARS = ["七杀", "破军", "贪狼"]  # 杀破狼星系

        # 判断主星类型
        has_ziwei = any(star in ZIWEI_STARS for star in ming_gong_stars)
        has_tianfu = any(star in TIANFU_STARS for star in ming_gong_stars)
        has_sha = any(star in SHA_PO_LANG_STARS for star in ming_gong_stars)

        # 优先级判断：紫微 > 天府 > 杀破狼
        if has_ziwei:
            # 紫微星系：以紫微所在宫为枢纽
            return self._find_star_palace("紫微")

        if has_tianfu:
            # 天府星系：以天府所在宫为枢纽
            return self._find_star_palace("天府")

        if has_sha:
            # 杀破狼星系：以七杀所在宫为枢纽
            return self._find_star_palace("七杀")

        return None

    def _identify_star_system(self, ming_gong_stars: List[str]) -> tuple:
        """
        识别命宫主星系统

        Args:
            ming_gong_stars: 命宫星曜列表

        Returns:
            (star_system, hub_star) - 主星系统名称和枢纽星名称
        """
        if not ming_gong_stars:
            return ("未识别", "")

        ZIWEI_STARS = ["紫微"]
        TIANFU_STARS = ["天府"]
        SHA_PO_LANG_STARS = ["七杀", "破军", "贪狼"]

        has_ziwei = any(star in ZIWEI_STARS for star in ming_gong_stars)
        has_tianfu = any(star in TIANFU_STARS for star in ming_gong_stars)
        has_sha = any(star in SHA_PO_LANG_STARS for star in ming_gong_stars)

        if has_ziwei:
            return ("紫微星系", "紫微")
        if has_tianfu:
            return ("天府星系", "天府")
        if has_sha:
            # 杀破狼中以七杀为主
            if "七杀" in ming_gong_stars:
                return ("杀破狼星系", "七杀")
            elif "破军" in ming_gong_stars:
                return ("杀破狼星系", "破军")
            else:
                return ("杀破狼星系", "贪狼")

        return ("一般星系", "")

    def _get_major_fate_stars(self, palace: str) -> List[str]:
        """获取大限宫内的星曜"""
        # 简化：从命盘中获取该宫的星曜
        try:
            if hasattr(self.chart, 'palaces') and self.chart.palaces:
                for p in self.chart.palaces:
                    if p.get("name") == palace:
                        return p.get("stars", [])
        except Exception:
            pass
        return []

    def _get_major_fate_transformation_info(self, birth_year: int, major_fate_index: int) -> Dict[str, str]:
        """
        获取大限四化详细信息

        大限四化采用生年四化飞入规则：
        - 生年化禄所在之星，在大限期间继续化禄
        - 生年化权所在之星，在大限期间继续化权
        - 生年化科所在之星，在大限期间继续化科
        - 生年化忌所在之星，在大限期间继续化忌

        Args:
            birth_year: 出生年份
            major_fate_index: 大限序号(0-11)

        Returns:
            包含主四化和描述的字典
        """
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        year_gan = gan_list[(birth_year - 4) % 10]

        birth_transforms = get_birth_transforms(year_gan)

        if not birth_transforms:
            trans = ["", "化禄", "化权", "化科", "化忌"]
            return {
                "main_transform": trans[major_fate_index % 4] if major_fate_index % 4 else "无化",
                "transforms": {},
                "description": ""
            }

        transforms = []
        for transform_type, star in birth_transforms.items():
            transforms.append(f"{star}{transform_type}")

        # 确定该大限的主导四化
        # 大限1-3年：禄权科忌循环
        # 大限4-6年：权科忌禄循环
        # 大限7-9年：科忌禄权循环
        # 大限10年：忌禄权科循环
        transform_order = ["禄", "权", "科", "忌"]
        fate_period = major_fate_index // 3  # 0-3
        main_idx = (fate_period + major_fate_index) % 4
        main_transform = transform_order[main_idx]

        # 获取主导四化对应的星曜
        main_star = birth_transforms.get(main_transform, "")

        description = ""
        if main_star:
            description = f"，{main_star}化{main_transform}"

        return {
            "main_transform": f"{main_star}{main_transform}" if main_star else main_transform,
            "transforms": birth_transforms,
            "description": description
        }

    def calculate_year_fate(self, year: int, birth_year: int) -> YearFate:
        """
        计算流年

        Args:
            year: 流年年份
            birth_year: 出生年份

        Returns:
            流年信息
        """
        tai_sui_palace = self._get_tai_sui_palace(year)
        tai_sui_relationship = self._get_tai_sui_relationship(tai_sui_palace)
        gan_zhi = self._get_gan_zhi(year)
        zodiac = self._year_to_zhi(year)

        # 获取流年星曜
        year_stars = self._get_year_stars(year, tai_sui_palace)

        # 获取流曜
        liu_yao = self._get_liu_yao(year)

        return YearFate(
            year=year,
            zodiac=zodiac,
            gan_zhi=gan_zhi,
            tai_sui_palace=tai_sui_palace,
            tai_sui_relationship=tai_sui_relationship,
            stars=year_stars,
            liu_yao=liu_yao,
            description=f"{gan_zhi}年，太岁在{tai_sui_palace}，{tai_sui_relationship}"
        )

    def _get_year_stars(self, year: int, tai_sui_palace: str) -> List[str]:
        """
        获取流年星曜（流年四化及飞入规则）

        流年四化规则：
        - 流年四化：根据流年天干决定，每年变化
        - 生年四化：根据出生年天干决定，一生不变
        - 四化星曜会"飞入"特定宫位，产生影响力

        流年四化飞入规则（基于中州派典籍）：
        - 化禄：多飞入财帛宫、官禄宫
        - 化权：多飞入官禄宫、迁移宫
        - 化科：多飞入官禄宫、名望宫
        - 化忌：多飞入疾厄宫、迁移宫

        Args:
            year: 流年年份
            tai_sui_palace: 流年太岁落宫

        Returns:
            流年四化星列表，例如：["廉贞化禄", "破军化权", "太阳化科", "太阴化忌"]
        """
        stars = []

        # 天干列表（用于索引）
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

        # 根据年份计算流年天干
        year_gan_index = (year - 4) % 10
        year_gan = gan_list[year_gan_index]

        # 使用流年四化函数获取四化信息
        transforms = get_yearly_transforms(year_gan)
        for transform_type, star_name in transforms.items():
            stars.append(f"{star_name}化{transform_type}")

        return stars

    def _get_transform_flying_palaces(self, year: int, birth_year: int) -> Dict[str, List[Dict]]:
        """
        获取流年四化飞入宫位（中州派飞星规则）

        基于《飞星紫微斗数》典籍，实现完整的中州派流年四化飞化规则：

        1. 基于星曜性质的飞化规则：
           - 不同星曜化禄/化忌后飞入的宫位不同
           - 星曜本身有木火土金水五行属性，影响飞化方向

        2. 结合飞星派核心规则：
           - 禄转忌：禄出而转忌，挾禄以入第二宫
           - 忌转忌：忌出而再转忌，深入因果
           - 追禄、追权、追忌的因缘串联

        3. 三合关系：化曜会飞入有本宫三方四正关系的宫位

        Args:
            year: 流年年份
            birth_year: 出生年份

        Returns:
            四化飞入宫位字典，格式：
            {
                "化禄": [{"star": "廉贞", "palaces": ["财帛宫", "官禄宫"], "interpretation": "..."}],
                "化权": [...],
                "化科": [...],
                "化忌": [...]
            }
        """
        # 天干列表
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        year_gan = gan_list[(year - 4) % 10]

        # 获取流年四化
        transforms = get_yearly_transforms(year_gan)

        # 基于星曜性质的飞化规则（中州派核心规则）
        # 格式：{星曜: {化类型: {palaces: [], interpretation: ""}}}
        STAR_FLYING_RULES: Dict[str, Dict[str, Dict]] = {
            # 甲年四化
            "廉贞": {
                "禄": {
                    "palaces": ["财帛宫", "官禄宫", "迁移宫"],
                    "interpretation": "廉贞化禄主财禄双美，有桃花性质但为艺术桃花"
                },
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "疾厄宫"],
                    "interpretation": "廉贞化忌主官非小人，须防口舌是非"
                }
            },
            "天机": {
                "禄": {
                    "palaces": ["官禄宫", "迁移宫", "财帛宫"],
                    "interpretation": "天机化禄主智慧生财，有谋略善策划"
                },
                "权": {
                    "palaces": ["官禄宫", "迁移宫"],
                    "interpretation": "天机化权主竞争创新，宜主动出击"
                },
                "科": {
                    "palaces": ["官禄宫", "福德宫"],
                    "interpretation": "天机化科主谋略名声，宜学术研究"
                },
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "疾厄宫"],
                    "interpretation": "天机化忌主思虑过度，变动不安"
                }
            },
            "太阳": {
                "禄": {
                    "palaces": ["官禄宫", "财帛宫", "迁移宫"],
                    "interpretation": "太阳化禄主事业发达，光明磊落"
                },
                "权": {
                    "palaces": ["官禄宫", "迁移宫"],
                    "interpretation": "太阳化权主权威显现，宜争夺功名"
                },
                "科": {
                    "palaces": ["官禄宫", "迁移宫"],
                    "interpretation": "太阳化科主声名远播，贵人多助"
                },
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "田宅宫"],
                    "interpretation": "太阳化忌主小人是非，眼光偏高"
                }
            },
            "太阴": {
                "禄": {
                    "palaces": ["财帛宫", "田宅宫", "福德宫"],
                    "interpretation": "太阴化禄主财库充盈，房产田宅积聚"
                },
                "权": {
                    "palaces": ["官禄宫", "田宅宫"],
                    "interpretation": "太阴化权主女权主导，理财持家"
                },
                "科": {
                    "palaces": ["福德宫", "田宅宫"],
                    "interpretation": "太阴化科主财库名声，储蓄有方"
                },
                "忌": {
                    "palaces": ["疾厄宫", "迁移宫", "田宅宫"],
                    "interpretation": "太阴化忌主家宅不宁，财库有损"
                }
            },
            # 乙年四化
            "天梁": {
                "权": {
                    "palaces": ["官禄宫", "迁移宫", "福德宫"],
                    "interpretation": "天梁化权主清高独立，宜监管仲裁"
                }
            },
            "武曲": {
                "科": {
                    "palaces": ["财帛宫", "官禄宫"],
                    "interpretation": "武曲化科主财运名声，正财有利"
                }
            },
            "巨门": {
                "禄": {
                    "palaces": ["财帛宫", "迁移宫", "官禄宫"],
                    "interpretation": "巨门化禄主口财生财，宜销售外交"
                },
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "疾厄宫"],
                    "interpretation": "巨门化忌主是非口舌，须防小人"
                }
            },
            # 丙年四化
            "天同": {
                "禄": {
                    "palaces": ["财帛宫", "福德宫", "田宅宫"],
                    "interpretation": "天同化禄主福泽深厚，温和得财"
                },
                "权": {
                    "palaces": ["官禄宫", "迁移宫"],
                    "interpretation": "天同化权主平稳保守，宜守成"
                },
                "忌": {
                    "palaces": ["疾厄宫", "迁移宫", "田宅宫"],
                    "interpretation": "天同化忌主小人是非，健康有损"
                }
            },
            # 丁年四化
            "太阳": {
                "权": {
                    "palaces": ["官禄宫", "迁移宫", "财帛宫"],
                    "interpretation": "太阳化权主事业心重，宜争取功名"
                }
            },
            # 戊年四化
            "贪狼": {
                "禄": {
                    "palaces": ["财帛宫", "田宅宫", "迁移宫"],
                    "interpretation": "贪狼化禄主财源广进，桃花财机会多"
                },
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "疾厄宫"],
                    "interpretation": "贪狼化忌主酒色财气，宜防贪念"
                }
            },
            # 己年四化
            "天府": {
                "科": {
                    "palaces": ["官禄宫", "田宅宫", "财帛宫"],
                    "interpretation": "天府化科主才能出众，理财有方"
                }
            },
            "文曲": {
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "疾厄宫"],
                    "interpretation": "文曲化忌主文书失误，名声有损"
                }
            },
            # 庚年四化
            "文昌": {
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "疾厄宫"],
                    "interpretation": "文昌化忌主文书失误，考运不佳"
                }
            },
            # 辛年四化
            "文曲": {
                "科": {
                    "palaces": ["官禄宫", "财帛宫", "迁移宫"],
                    "interpretation": "文曲化科主文采风流，名声远播"
                }
            },
            # 壬年四化
            "紫微": {
                "权": {
                    "palaces": ["官禄宫", "田宅宫", "财帛宫"],
                    "interpretation": "紫微化权主独尊权威，宜领导管理"
                }
            },
            "贪狼": {
                "科": {
                    "palaces": ["官禄宫", "财帛宫", "迁移宫"],
                    "interpretation": "贪狼化科主才艺生财，有桃花性质"
                }
            },
            # 癸年四化
            "文昌": {
                "忌": {
                    "palaces": ["官禄宫", "迁移宫", "疾厄宫"],
                    "interpretation": "文昌化忌主文书失误，学业受阻"
                }
            }
        }

        # 通用飞化宫位规则（当星曜没有特定规则时使用）
        # 基于飞星派三合关系
        GENERIC_FLYING_RULES: Dict[str, List[str]] = {
            "禄": ["财帛宫", "官禄宫", "迁移宫"],  # 禄出三合方
            "权": ["官禄宫", "迁移宫", "命宫"],     # 权争三合方
            "科": ["官禄宫", "福德宫", "迁移宫"],  # 科名三合方
            "忌": ["疾厄宫", "迁移宫", "官禄宫"]   # 忌冲三合方
        }

        # 构建返回结果
        flying_palaces: Dict[str, List[Dict]] = {
            "化禄": [],
            "化权": [],
            "化科": [],
            "化忌": []
        }

        for transform_type, star_name in transforms.items():
            transform_key = "禄" if transform_type == "禄" else transform_type
            result_item = {
                "star": star_name,
                "palaces": [],
                "interpretation": ""
            }

            # 首先查找星曜特定规则
            if star_name in STAR_FLYING_RULES:
                star_rules = STAR_FLYING_RULES[star_name]
                if transform_key in star_rules:
                    rule = star_rules[transform_key]
                    result_item["palaces"] = rule["palaces"]
                    result_item["interpretation"] = rule["interpretation"]
                else:
                    # 星曜有记录但该化类型无特定规则，使用通用规则
                    result_item["palaces"] = GENERIC_FLYING_RULES.get(transform_type, [])
                    result_item["interpretation"] = f"{star_name}化{transform_type}按通用规则飞化"
            else:
                # 星曜无特定规则，使用通用规则
                result_item["palaces"] = GENERIC_FLYING_RULES.get(transform_type, [])
                result_item["interpretation"] = f"{star_name}化{transform_type}按通用规则飞化"

            flying_palaces[f"化{transform_type}"].append(result_item)

        # 飞星派核心规则补充说明
        flying_palaces["_meta"] = {
            "year_gan": year_gan,
            "transforms": transforms,
            "rules_source": "中州派飞星紫微斗数",
            "core_rules": [
                "禄转忌：禄出而转忌，挾禄以入第二宫",
                "忌转忌：忌出而再转忌，深入因果追根究底",
                "忌冲对宫：消散、放弃、虎头蛇尾、少坚持象"
            ]
        }

        return flying_palaces

    def _get_liu_yao(self, year: int) -> Dict[str, List[str]]:
        """
        获取流曜（博士十二神、将前十神、岁前十二神）

        流曜系统说明（基于紫微斗数典籍）：

        1. 博士十二神（按流年地支起）：
           子年：博士→力士→青龙→小耗→将军→奏书→蜚廉→喜神→病符→大耗→伏兵→官府
           丑年：力士→青龙→...→博士（逆时针）
           ...

        2. 将前十神（按流年地支起）：
           子年：将星→攀鞍→岁驿→息神→华盖→劫煞→灾煞→天煞→指背→咸池→月煞→亡神
           丑年：攀鞍→岁驿→...→将星（逆时针）
           ...

        3. 岁前十二神（按流年地支起）：
           子年：岁建→晦气→丧门→贯索→官符→小耗→大耗→龙德→白虎→天德→吊客→病符
           丑年：晦气→丧门→...→岁建（逆时针）
           ...

        Args:
            year: 流年年份

        Returns:
            流曜字典
        """
        # 流年地支决定起始位置
        year_zhi = self._year_to_zhi(year)
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        year_zhi_idx = zhi_list.index(year_zhi)

        # 博士十二神(按流年地支逆时针排列)
        boshis = ["博士", "力士", "青龙", "小耗", "将军", "奏书",
                  "蜚廉", "喜神", "病符", "大耗", "伏兵", "官府"]

        # 将前十神(按流年地支逆时针排列)
        jiangs = ["将星", "攀鞍", "岁驿", "息神", "华盖", "劫煞",
                  "灾煞", "天煞", "指背", "咸池", "月煞", "亡神"]

        # 岁前十二神(按流年地支逆时针排列)
        suis = ["岁建", "晦气", "丧门", "贯索", "官符", "小耗",
                "大耗", "龙德", "白虎", "天德", "吊客", "病符"]

        return {
            "博士十二神": [boshis[year_zhi_idx]],
            "将前十神": [jiangs[year_zhi_idx]],
            "岁前十二神": [suis[year_zhi_idx]]
        }

    def _get_liu_yao_full(self, year: int) -> Dict[str, List[str]]:
        """
        获取完整流曜（包含所有十二神）

        与_get_liu_yao不同，此方法返回完整的流曜序列而非仅当年值。

        Args:
            year: 流年年份

        Returns:
            完整的流曜序列
        """
        year_zhi = self._year_to_zhi(year)
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        year_zhi_idx = zhi_list.index(year_zhi)

        # 博士十二神完整序列
        boshis = ["博士", "力士", "青龙", "小耗", "将军", "奏书",
                  "蜚廉", "喜神", "病符", "大耗", "伏兵", "官府"]

        # 将前十神完整序列
        jiangs = ["将星", "攀鞍", "岁驿", "息神", "华盖", "劫煞",
                  "灾煞", "天煞", "指背", "咸池", "月煞", "亡神"]

        # 岁前十二神完整序列
        suis = ["岁建", "晦气", "丧门", "贯索", "官符", "小耗",
                "大耗", "龙德", "白虎", "天德", "吊客", "病符"]

        # 逆时针排列：从流年地支开始，逆时针依次排列
        def rotate_anticlockwise(lst: List, start_idx: int) -> List:
            return lst[start_idx:] + lst[:start_idx]

        return {
            "博士十二神": rotate_anticlockwise(boshis, year_zhi_idx),
            "将前十神": rotate_anticlockwise(jiangs, year_zhi_idx),
            "岁前十二神": rotate_anticlockwise(suis, year_zhi_idx)
        }

    def analyze_timing(self, target_year: int, birth_year: int, gender: str = "男",
                       years_ahead: int = 10) -> TimingAnalysis:
        """
        分析指定年份的时间运势

        Args:
            target_year: 目标年份
            birth_year: 出生年份
            gender: 性别
            years_ahead: 预测年数（默认10年）

        Returns:
            时间分析结果
        """
        # 计算大限
        major_fates = self.calculate_major_fate(birth_year, gender)

        # 找到当前大限
        current_major = None
        age = target_year - birth_year
        for mf in major_fates:
            if mf.start_age <= age <= mf.end_age:
                current_major = mf
                break

        # 计算流年（多年）
        year_fates = []
        for i in range(years_ahead):
            year = target_year + i
            year_fates.append(self.calculate_year_fate(year, birth_year))

        # 当前流年
        year_fate = year_fates[0] if year_fates else None

        # 获取时机触发因素
        timing_triggers = self._analyze_timing_triggers(year_fate, current_major)

        # 枢纽宫分析
        hub_analysis = self._analyze_hub_palace(current_major, year_fate)

        # 建议
        recommendations = self._generate_recommendations(year_fate, current_major)

        # 构建大限表格
        major_fate_table = self._build_major_fate_table(major_fates, birth_year)

        # 构建流年预测列表
        year_predictions = self._build_year_predictions(year_fates, birth_year)

        # 时间锚点分析
        time_anchors = self._analyze_time_anchors(year_fates, major_fates, birth_year)

        return TimingAnalysis(
            major_fates=major_fates,
            current_major_fate=current_major,
            year_fates=year_fates,
            current_year_fate=year_fate,
            timing_triggers=timing_triggers,
            hub_palace_analysis=hub_analysis,
            recommendations=recommendations,
            major_fate_table=major_fate_table,
            year_predictions=year_predictions,
            time_anchors=time_anchors
        )

    def _analyze_timing_triggers(self, year_fate: YearFate, major_fate: Optional[MajorFate]) -> List[Dict[str, Any]]:
        """分析时机触发因素"""
        triggers = []

        # 太岁关系触发
        if year_fate.tai_sui_relationship == "冲本宫":
            triggers.append({
                "type": "太岁冲宫",
                "description": "流年太岁冲命宫，变动较大",
                "advice": "宜守不宜攻，谨慎决策"
            })
        elif year_fate.tai_sui_relationship == "三合":
            triggers.append({
                "type": "太岁三合",
                "description": "流年太岁与命宫三合，运势顺畅",
                "advice": "把握机遇，主动出击"
            })
        elif year_fate.tai_sui_relationship == "入本宫":
            triggers.append({
                "type": "太岁入宫",
                "description": "流年太岁入命宫，气势旺盛",
                "advice": "把握机会，展示能力"
            })

        # 流曜触发
        for category, stars in year_fate.liu_yao.items():
            for star in stars:
                if star in ["大耗", "丧门", "白虎", "病符", "官符"]:
                    triggers.append({
                        "type": f"流曜-{star}",
                        "description": f"流年遇到{star}，需注意",
                        "advice": "低调行事，避免冲突"
                    })
                elif star in ["龙德", "天德", "将星", "岁驿"]:
                    triggers.append({
                        "type": f"流曜-{star}",
                        "description": f"流年遇到{star}，有利发展",
                        "advice": "抓住机会，积极进取"
                    })

        # 四化触发
        for star in year_fate.stars:
            if "化忌" in star:
                triggers.append({
                    "type": "化忌触发",
                    "description": f"流年遇到{star}，需防阻碍",
                    "advice": "注意化解，稳健行事"
                })
            elif "化禄" in star or "化权" in star or "化科" in star:
                triggers.append({
                    "type": "吉化触发",
                    "description": f"流年遇到{star}，有利于发展",
                    "advice": "抓住机遇，乘势而上"
                })

        return triggers

    def _analyze_hub_palace(self, major_fate: Optional[MajorFate], year_fate: YearFate) -> Dict[str, Any]:
        """
        分析枢纽宫 - 基于中州派理论

        中州派枢纽宫分析要点：
        1. 枢纽宫是大限中最重要的宫位，代表该大限的核心运势
        2. 流年太岁与枢纽宫的关系决定该年运势的激烈程度
        3. 枢纽星(如紫微、天府、七杀)的强弱影响整个大限
        """
        if not major_fate:
            return {}

        result = {
            "is_hub_year": False,
            "hub_palace": major_fate.hub_palace,
            "hub_star": major_fate.hub_star,
            "star_system": major_fate.star_system,
            "description": "",
            "significance": "一般",
            "analysis": ""
        }

        # 检查流年太岁是否在大限枢纽宫
        if year_fate.tai_sui_palace == major_fate.hub_palace:
            result["is_hub_year"] = True
            result["significance"] = "重要"
            result["description"] = f"流年太岁在大限枢纽宫{major_fate.hub_palace}，为命运转折之年"
            result["analysis"] = self._generate_hub_year_analysis(major_fate, year_fate)
        else:
            # 检查太岁与枢纽宫的关系
            palace_names = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                           "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]
            try:
                hub_idx = palace_names.index(major_fate.hub_palace)
                tai_idx = palace_names.index(year_fate.tai_sui_palace)
                diff = abs(hub_idx - tai_idx)

                if diff == 6:
                    result["description"] = f"流年太岁与枢纽宫{major_fate.hub_palace}相冲，运势波动较大"
                elif diff in [4, 8]:
                    result["description"] = f"流年太岁与枢纽宫三合，运势顺畅"
                elif diff in [1, 11]:
                    result["description"] = f"流年太岁拱照枢纽宫{major_fate.hub_palace}，有暗中助力"
                else:
                    result["description"] = f"流年太岁不在枢纽宫{major_fate.hub_palace}"
            except ValueError:
                result["description"] = f"流年太岁不在枢纽宫"

        return result

    def _generate_hub_year_analysis(self, major_fate: MajorFate, year_fate: YearFate) -> str:
        """生成枢纽年的详细分析"""
        analysis_parts = []

        # 基于主星系统给出分析
        if major_fate.star_system == "紫微星系":
            analysis_parts.append("紫微星为枢纽，该年紫微星耀，权力和地位有提升机会。")
        elif major_fate.star_system == "天府星系":
            analysis_parts.append("天府星为枢纽，该年天府星旺，财运和事业稳定发展。")
        elif major_fate.star_system == "杀破狼星系":
            analysis_parts.append("七杀星为枢纽，该年变动较大，需积极把握机遇。")

        # 基于四化给出分析
        for star in year_fate.stars:
            if "化禄" in star:
                analysis_parts.append(f"流年{star}，有利于财运和事业发展。")
            elif "化权" in star:
                analysis_parts.append(f"流年{star}，权力和竞争运势增强。")
            elif "化科" in star:
                analysis_parts.append(f"流年{star}，功名和学业运势上升。")
            elif "化忌" in star:
                analysis_parts.append(f"流年{star}，注意化解，注意人际关系和财务。")

        return " ".join(analysis_parts) if analysis_parts else "该年为命运转折点，需谨慎把握。"

    def _generate_recommendations(self, year_fate: YearFate, major_fate: Optional[MajorFate]) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于太岁关系
        if year_fate.tai_sui_relationship == "冲本宫":
            recommendations.append("太岁冲宫，宜静不宜动，避免激进决策")
        elif year_fate.tai_sui_relationship == "三合":
            recommendations.append("太岁三合，运势顺畅，可把握机遇")
        elif year_fate.tai_sui_relationship == "入本宫":
            recommendations.append("太岁入宫，可展示能力，把握机会")

        # 基于流年四化
        for star in year_fate.stars:
            if "化忌" in star:
                recommendations.append(f"{star}年份，注意化解忌星之力，稳健行事")
            elif "化禄" in star:
                recommendations.append(f"{star}年份，适合发展事业，把握财富机会")

        # 基于流曜
        liu_yao = year_fate.liu_yao
        if "博士十二神" in liu_yao:
            boshi = liu_yao["博士十二神"][0]
            if boshi in ["大耗", "小耗", "病符"]:
                recommendations.append(f"博士十二神为{boshi}，注意财务和健康")
            elif boshi in ["青龙", "将军", "喜神"]:
                recommendations.append(f"博士十二神为{boshi}，运势较佳")

        return recommendations

    def _build_major_fate_table(self, major_fates: List[MajorFate], birth_year: int) -> List[Dict[str, Any]]:
        """构建大限分析表格"""
        table = []
        for mf in major_fates:
            # 评估该大限的运势等级
            rating = self._evaluate_major_fate_rating(mf)
            table.append({
                "index": mf.index,
                "name": f"第{mf.index}大限",
                "age_range": f"{mf.start_age}-{mf.end_age}岁",
                "years": f"{birth_year + mf.start_age - 1}-{birth_year + mf.end_age - 1}",
                "palace": mf.palace,
                "hub_palace": mf.hub_palace,
                "star_system": mf.star_system,
                "hub_star": mf.hub_star,
                "stars": mf.stars[:5] if mf.stars else [],  # 限制显示星曜数量
                "transformation": mf.transformation,
                "rating": rating["level"],
                "rating_description": rating["description"],
                "summary": mf.description
            })
        return table

    def _evaluate_major_fate_rating(self, major_fate: MajorFate) -> Dict[str, str]:
        """评估大限运势等级"""
        score = 50  # 基础分

        # 考虑星曜
        if major_fate.stars:
            star_names = "".join(major_fate.stars)
            if any(s in star_names for s in ["紫微", "天府", "太阳", "武曲", "天同"]):
                score += 15
            if any(s in star_names for s in ["贪狼", "巨门", "天相", "天梁"]):
                score += 10
            if any(s in star_names for s in ["七杀", "破军", "廉贞"]):
                score += 5
            if any(s in star_names for s in ["擎羊", "陀罗", "火星", "铃星"]):
                score -= 15
            if any(s in star_names for s in ["化禄", "化权", "化科"]):
                score += 10
            if "化忌" in star_names:
                score -= 10

        # 考虑四化
        if major_fate.transformation in ["化禄", "化权", "化科"]:
            score += 10
        elif major_fate.transformation == "化忌":
            score -= 10

        # 评级
        if score >= 80:
            return {"level": "A+", "description": "大吉，大限运势极佳，诸事顺遂"}
        elif score >= 70:
            return {"level": "A", "description": "吉，大限运势较好，把握机遇"}
        elif score >= 60:
            return {"level": "B+", "description": "中吉，大限运势中等，稳中求进"}
        elif score >= 50:
            return {"level": "B", "description": "平，大限运势一般，谨慎行事"}
        elif score >= 40:
            return {"level": "C+", "description": "小凶，大限运势较弱，注意调整"}
        else:
            return {"level": "C", "description": "凶，大限运势低迷，静待时机"}

    def _build_year_predictions(self, year_fates: List[YearFate], birth_year: int) -> List[Dict[str, Any]]:
        """构建流年预测列表"""
        predictions = []
        for yf in year_fates:
            age = yf.year - birth_year
            # 简化的运势评估
            rating = self._evaluate_year_rating(yf)
            predictions.append({
                "year": yf.year,
                "gan_zhi": yf.gan_zhi,
                "zodiac": yf.zodiac,
                "age": age,
                "tai_sui_palace": yf.tai_sui_palace,
                "tai_sui_relationship": yf.tai_sui_relationship,
                "stars": yf.stars,
                "liu_yao": yf.liu_yao,
                "rating": rating["level"],
                "rating_description": rating["description"],
                "key_highlights": rating["highlights"],
                "summary": yf.description
            })
        return predictions

    def _evaluate_year_rating(self, year_fate: YearFate) -> Dict[str, Any]:
        """评估流年运势"""
        score = 50
        highlights = []

        # 太岁关系
        if year_fate.tai_sui_relationship == "冲本宫":
            score -= 10
            highlights.append("太岁冲命，变动之年")
        elif year_fate.tai_sui_relationship == "三合":
            score += 15
            highlights.append("太岁三合，运势顺畅")
        elif year_fate.tai_sui_relationship == "入本宫":
            score += 10
            highlights.append("太岁入命，气势旺盛")

        # 流年四化星
        for star in year_fate.stars:
            if "化忌" in star:
                score -= 15
                highlights.append(f"{star}，注意阻碍")
            elif "化禄" in star:
                score += 15
                highlights.append(f"{star}，财禄机遇")
            elif "化权" in star:
                score += 10
                highlights.append(f"{star}，权力提升")
            elif "化科" in star:
                score += 10
                highlights.append(f"{star}，功名有望")

        # 流曜影响
        for category, stars in year_fate.liu_yao.items():
            for star in stars:
                if star in ["大耗", "丧门", "白虎", "病符"]:
                    score -= 10
                    highlights.append(f"{star}，注意化解")
                elif star in ["龙德", "天德", "将星", "岁驿", "喜神"]:
                    score += 10
                    highlights.append(f"{star}，有利发展")

        # 评级
        if score >= 80:
            level = "A+"
            description = "流年大吉，诸事顺遂"
        elif score >= 70:
            level = "A"
            description = "流年吉利，把握机遇"
        elif score >= 60:
            level = "B+"
            description = "流年平顺，稳中求进"
        elif score >= 50:
            level = "B"
            description = "流年平常，谨慎行事"
        elif score >= 40:
            level = "C+"
            description = "流年小凶，注意调整"
        else:
            level = "C"
            description = "流年不利，静待时机"

        return {
            "level": level,
            "description": description,
            "highlights": highlights[:3]  # 限制高亮数量
        }

    def _analyze_time_anchors(self, year_fates: List[YearFate],
                              major_fates: List[MajorFate],
                              birth_year: int) -> List[Dict[str, Any]]:
        """分析时间锚点：重大机遇和挑战的年份"""
        anchors = []

        # 找出流年运势最好的年份
        sorted_years = sorted(year_fates, key=lambda y: self._get_year_score(y), reverse=True)

        # 前3个最好的年份作为机遇年
        for i, yf in enumerate(sorted_years[:3]):
            age = yf.year - birth_year
            anchors.append({
                "type": "机遇",
                "year": yf.year,
                "age": age,
                "gan_zhi": yf.gan_zhi,
                "description": f"{age}岁（{yf.year}年）{yf.tai_sui_relationship}，运势较佳",
                "advice": self._get_opportunity_advice(yf),
                "suitable": self._get_suitable_activities(yf)
            })

        # 找出流年运势较差的年份作为挑战年
        for yf in sorted_years[-2:]:
            age = yf.year - birth_year
            anchors.append({
                "type": "挑战",
                "year": yf.year,
                "age": age,
                "gan_zhi": yf.gan_zhi,
                "description": f"{age}岁（{yf.year}年）{yf.tai_sui_relationship}，运势较弱",
                "advice": self._get_challenge_advice(yf),
                "caution": self._get_caution_points(yf)
            })

        # 排序：按年份
        anchors.sort(key=lambda x: x["year"])

        return anchors

    def _get_year_score(self, year_fate: YearFate) -> int:
        """获取流年评分"""
        score = 50

        if year_fate.tai_sui_relationship == "三合":
            score += 20
        elif year_fate.tai_sui_relationship == "入本宫":
            score += 15
        elif year_fate.tai_sui_relationship == "冲本宫":
            score -= 15

        for star in year_fate.stars:
            if "化忌" in star:
                score -= 15
            elif "化禄" in star:
                score += 15

        return score

    def _get_opportunity_advice(self, year_fate: YearFate) -> str:
        """获取机遇年建议"""
        advices = []
        if year_fate.tai_sui_relationship == "三合":
            advices.append("太岁三合，宜主动出击")
        if any("化禄" in s for s in year_fate.stars):
            advices.append("流年化禄，宜把握财禄机会")
        if any(s in str(year_fate.liu_yao) for s in ["龙德", "天德", "将星"]):
            advices.append("吉曜高照，宜开展新事业")
        if not advices:
            advices.append("运势较好，宜积极进取")
        return "; ".join(advices)

    def _get_suitable_activities(self, year_fate: YearFate) -> List[str]:
        """获取适合的活动"""
        activities = []
        if any("化禄" in s or "武曲" in s for s in year_fate.stars):
            activities.append("投资理财")
        if any(s in str(year_fate.liu_yao) for s in ["龙德", "天德"]):
            activities.append("考试升迁")
        if any(s in ["将星", "岁驿"] for s in str(year_fate.liu_yao).split()):
            activities.append("外出远行")
        if any(s in ["喜神", "青龙"] for s in str(year_fate.liu_yao).split()):
            activities.append("社交姻缘")
        if not activities:
            activities = ["稳健发展", "把握机遇"]
        return activities[:3]

    def _get_challenge_advice(self, year_fate: YearFate) -> str:
        """获取挑战年建议"""
        advices = []
        if year_fate.tai_sui_relationship == "冲本宫":
            advices.append("太岁冲命，宜静不宜动")
        if any("化忌" in s for s in year_fate.stars):
            advices.append("流年化忌，谨慎决策")
        if any(s in ["大耗", "白虎", "丧门"] for s in str(year_fate.liu_yao).split()):
            advices.append("凶曜临命，注意化解")
        if not advices:
            advices.append("运势较弱，保守行事")
        return "; ".join(advices)

    def _get_caution_points(self, year_fate: YearFate) -> List[str]:
        """获取注意事项"""
        cautions = []
        if any("化忌" in s for s in year_fate.stars):
            cautions.append("避免激进投资")
        if any(s in ["大耗", "官符"] for s in str(year_fate.liu_yao).split()):
            cautions.append("注意财务纠纷")
        if any(s in ["白虎", "丧门"] for s in str(year_fate.liu_yao).split()):
            cautions.append("注意健康安全")
        if not cautions:
            cautions = ["谨慎行事", "避免冒险"]
        return cautions[:3]

    def analyze_cycle_stage(self, palace: str, age: int, major_fate_year: int,
                           transform_type: Optional[str] = None) -> Dict[str, Any]:
        """
        分析宫位在当前大限的成住坏空阶段

        Args:
            palace: 宫位名称
            age: 当前年龄
            major_fate_year: 大限第几年 (1-10)
            transform_type: 可选的化禄/化权/化科/化忌

        Returns:
            {
                "palace": 宫位,
                "stage": 成/住/坏/空,
                "description": 阶段描述,
                "transform_impact": 四化影响,
                "advice": 建议
            }
        """
        stage = get_cycle_stage_for_palace(palace, age, major_fate_year)
        palace_data = CYCLE_STAGE_PALACE_MAP.get(palace, {})
        description = palace_data.get(stage, "")

        result = {
            "palace": palace,
            "stage": stage,
            "description": description,
            "stage_meaning": f"{palace}正处于{description}阶段",
            "advice": self._get_cycle_advice(palace, stage)
        }

        # 如果有四化信息，添加四化影响
        if transform_type:
            transform_impact = get_transform_cycle_impact(transform_type, palace)
            if transform_impact:
                result["transform_impact"] = {
                    "transform_type": transform_type,
                    "impact": transform_impact.get(stage, ""),
                    "full_impacts": transform_impact
                }

        return result

    def _get_cycle_advice(self, palace: str, stage: str) -> str:
        """获取成住坏空阶段的建议"""
        advice_map = {
            "成": f"{palace}正在形成期，适合规划、布局、奠定基础。",
            "住": f"{palace}处于稳定期，适合巩固、发展、积累成果。",
            "坏": f"{palace}进入衰败期，需要警惕问题、调整策略、化解矛盾。",
            "空": f"{palace}处于空亡期，宜静不宜动，避免重大决策。"
        }
        return advice_map.get(stage, "")

    def get_cycle_analysis_for_major_fate(self, major_fate: MajorFate,
                                        birth_year: int) -> Dict[str, Any]:
        """
        获取大限的成住坏空全面分析

        Args:
            major_fate: 大限信息
            birth_year: 出生年份

        Returns:
            包含所有宫位成住坏空分析的结果
        """
        import datetime
        current_year = datetime.datetime.now().year
        current_age = current_year - birth_year

        # 计算当前在大限中的第几年
        if major_fate.start_age <= current_age <= major_fate.end_age:
            major_fate_year = current_age - major_fate.start_age + 1
        else:
            major_fate_year = 1

        # 宫位列表
        palace_names = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                       "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]

        cycle_analysis = {
            "major_fate_index": major_fate.index,
            "major_fate_palace": major_fate.palace,
            "current_age": current_age,
            "major_fate_year": major_fate_year,
            "overall_stage": get_cycle_stage_for_palace(major_fate.palace, current_age, major_fate_year),
            "palace_cycles": [],
            "summary": {}
        }

        # 分析每个宫位的成住坏空
        for palace in palace_names:
            palace_cycle = self.analyze_cycle_stage(palace, current_age, major_fate_year)
            cycle_analysis["palace_cycles"].append(palace_cycle)

        # 找出当前最需要关注的宫位（处于坏和空阶段的）
        critical_palaces = [
            p for p in cycle_analysis["palace_cycles"]
            if p["stage"] in ["坏", "空"]
        ]
        cycle_analysis["summary"]["critical_palaces"] = critical_palaces

        # 找出最有利的宫位（处于成和住阶段的）
        favorable_palaces = [
            p for p in cycle_analysis["palace_cycles"]
            if p["stage"] in ["成", "住"]
        ]
        cycle_analysis["summary"]["favorable_palaces"] = favorable_palaces

        return cycle_analysis

    def get_year_predictions(self, birth_year: int, gender: str = "男",
                           start_year: int = None, years: int = 10) -> List[YearFate]:
        """
        获取多年流年预测

        Args:
            birth_year: 出生年份
            gender: 性别
            start_year: 起始年份(默认为当前年)
            years: 预测年数

        Returns:
            流年列表
        """
        if start_year is None:
            import datetime
            start_year = datetime.datetime.now().year

        year_fates = []
        for i in range(years):
            year = start_year + i
            year_fates.append(self.calculate_year_fate(year, birth_year))

        return year_fates


# ============ Utility Functions ============

def create_timing_agent(chart_data: ChartResult) -> TimingAgent:
    """创建时间分析代理的工厂函数"""
    return TimingAgent(chart_data)


# ============ LLM增强分析 ============

class LLMTimingAnalyzer:
    """运限分析LLM增强器"""

    def __init__(self, chart_data: Any = None):
        self.chart = chart_data

    async def analyze_with_llm(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用LLM进行深度运限分析

        Args:
            question: 可选的特定问题
            temperature: LLM温度参数

        Returns:
            解析后的JSON分析结果
        """
        from ....utils.llm_client import LLMClient
        from .llm_prompts import TIMING_SYSTEM_PROMPT, build_timing_user_prompt

        # 构建提示词
        user_prompt = build_timing_user_prompt(self.chart, question)

        messages = [
            {"role": "system", "content": TIMING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 调用LLM
        llm_client = LLMClient()
        result = llm_client.chat_json(messages, temperature=temperature)

        return result

    def analyze_with_llm_sync(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """同步版本的LLM分析"""
        import asyncio
        return asyncio.run(self.analyze_with_llm(question, temperature))

    async def generate_text_report(
        self,
        question: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """生成文本格式的LLM分析报告"""
        from .llm_prompts import format_analysis_as_text
        result = await self.analyze_with_llm(question, temperature)
        return format_analysis_as_text(result)


async def llm_analyze_timing(
    chart_data: Any,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用LLM分析命盘运限

    Args:
        chart_data: 命盘数据
        question: 可选的特定问题

    Returns:
        LLM分析结果
    """
    analyzer = LLMTimingAnalyzer(chart_data)
    return await analyzer.analyze_with_llm(question)


@cached_chart_analysis("timing", ttl=3600)
def llm_analyze_timing_sync(
    chart_data: Any,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """同步版本的LLM运限分析"""
    import asyncio
    return asyncio.run(llm_analyze_timing(chart_data, question))
