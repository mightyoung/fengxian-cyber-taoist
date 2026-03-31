"""
NameRecommendationAgent - 改名起名推荐引擎

根据命盘五行属性，推荐最佳姓名，分析姓名学笔画数理并评分。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import logging

# 配置日志
logger = logging.getLogger(__name__)


# ============ 五行偏旁部首表 ============

WU_XING_RADICALS = {
    "木": ["木", "艹", "宀", "林", "森", "东", "桂", "桐", "松", "柏", "楠", "榆", "槐", "樱", "柳", "梅", "竹", "芝", "芸", "芬", "花", "苗", "英", "荣", "苹"],
    "火": ["火", "灬", "光", "炎", "焱", "灿", "焕", "辉", "耀", "熙", "彤", "丹", "红", "纪", "紫", "赤", "哲", "日", "昌", "明", "昊", "晖", "旭", "晨", "昭"],
    "土": ["土", "艸", "山", "石", "玉", "王", "珏", "琳", "琅", "琪", "瑛", "璐", "壁", "瑾", "瑟", "瑞", "圭", "培", "墨", "坤", "城", "坚", "基"],
    "金": ["金", "钅", "刂", "戈", "玉", "佩", "钦", "钧", "铭", "锋", "锐", "锦", "锡", "镖", "镔", "鉴", "鑫", "铖", "钰", "钲", "钱", "镛"],
    "水": ["水", "氵", "冫", "雨", "雪", "云", "风", "冰", "泉", "溪", "渊", "润", "泽", "洁", "漾", "涛", "澜", "波", "瀚", "海", "洋", "津"],
}

# 姓名学笔画数理（81数理）
# 只定义关键的吉数和凶数
LUCKY_NUMBERS = [1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65, 67, 68, 81]
UNLUCKY_NUMBERS = [2, 4, 9, 10, 12, 14, 19, 20, 22, 27, 28, 30, 34, 36, 42, 43, 44, 46, 50, 51, 53, 54, 55, 56, 58, 59, 60, 62, 64, 66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80]

# 五行偏旁 → 五行
RADICAL_TO_WUXING = {
    "木": "木", "艹": "木", "宀": "木", "林": "木", "森": "木",
    "火": "火", "灬": "火", "光": "火", "炎": "火",
    "土": "土", "艸": "土", "山": "土", "石": "土",
    "金": "金", "钅": "金", "刂": "金", "戈": "金",
    "水": "水", "氵": "水", "冫": "水", "雨": "水",
}

# 姓名数据库（50+常见好名字）
NAME_DATABASE = [
    # 木属性名字
    {"name": "林", "pinyin": "lin", "wuxing": "木", "meaning": "森林"},
    {"name": "松", "pinyin": "song", "wuxing": "木", "meaning": "松树"},
    {"name": "柏", "pinyin": "bai", "wuxing": "木", "meaning": "柏树"},
    {"name": "楠", "pinyin": "nan", "wuxing": "木", "meaning": "楠木"},
    {"name": "桐", "pinyin": "tong", "wuxing": "木", "meaning": "梧桐"},
    {"name": "桂", "pinyin": "gui", "wuxing": "木", "meaning": "桂花"},
    {"name": "樱", "pinyin": "ying", "wuxing": "木", "meaning": "樱花"},
    {"name": "柳", "pinyin": "liu", "wuxing": "木", "meaning": "杨柳"},
    {"name": "梅", "pinyin": "mei", "wuxing": "木", "meaning": "梅花"},
    {"name": "竹", "pinyin": "zhu", "wuxing": "木", "meaning": "竹子"},
    {"name": "芸", "pinyin": "yun", "wuxing": "木", "meaning": "芸香"},
    {"name": "芬", "pinyin": "fen", "wuxing": "木", "meaning": "芬芳"},
    {"name": "芳", "pinyin": "fang", "wuxing": "木", "meaning": "芳香"},
    {"name": "英", "pinyin": "ying", "wuxing": "木", "meaning": "英华"},
    # 火属性名字
    {"name": "灿", "pinyin": "can", "wuxing": "火", "meaning": "灿烂"},
    {"name": "焕", "pinyin": "huan", "wuxing": "火", "meaning": "焕发"},
    {"name": "辉", "pinyin": "hui", "wuxing": "火", "meaning": "光辉"},
    {"name": "耀", "pinyin": "yao", "wuxing": "火", "meaning": "照耀"},
    {"name": "熙", "pinyin": "xi", "wuxing": "火", "meaning": "康熙"},
    {"name": "彤", "pinyin": "tong", "wuxing": "火", "meaning": "红彤"},
    {"name": "丹", "pinyin": "dan", "wuxing": "火", "meaning": "丹心"},
    {"name": "炎", "pinyin": "yan", "wuxing": "火", "meaning": "炎热"},
    {"name": "昌", "pinyin": "chang", "wuxing": "火", "meaning": "昌盛"},
    {"name": "明", "pinyin": "ming", "wuxing": "火", "meaning": "光明"},
    {"name": "昊", "pinyin": "hao", "wuxing": "火", "meaning": "昊天"},
    {"name": "旭", "pinyin": "xu", "wuxing": "火", "meaning": "旭日"},
    {"name": "晨", "pinyin": "chen", "wuxing": "火", "meaning": "晨曦"},
    # 土属性名字
    {"name": "墨", "pinyin": "mo", "wuxing": "土", "meaning": "墨水"},
    {"name": "坤", "pinyin": "kun", "wuxing": "土", "meaning": "乾坤"},
    {"name": "培", "pinyin": "pei", "wuxing": "土", "meaning": "培养"},
    {"name": "壁", "pinyin": "bi", "wuxing": "土", "meaning": "墙壁"},
    {"name": "城", "pinyin": "cheng", "wuxing": "土", "meaning": "城池"},
    {"name": "基", "pinyin": "ji", "wuxing": "土", "meaning": "基础"},
    {"name": "坚", "pinyin": "jian", "wuxing": "土", "meaning": "坚强"},
    {"name": "岳", "pinyin": "yue", "wuxing": "土", "meaning": "山岳"},
    {"name": "均", "pinyin": "jun", "wuxing": "土", "meaning": "均匀"},
    {"name": "轩", "pinyin": "xuan", "wuxing": "土", "meaning": "轩辕"},
    {"name": "玮", "pinyin": "wei", "wuxing": "土", "meaning": "美玉"},
    {"name": "容", "pinyin": "rong", "wuxing": "土", "meaning": "容貌"},
    # 金属性名字
    {"name": "铭", "pinyin": "ming", "wuxing": "金", "meaning": "铭刻"},
    {"name": "钧", "pinyin": "jun", "wuxing": "金", "meaning": "千钧"},
    {"name": "锦", "pinyin": "jin", "wuxing": "金", "meaning": "锦绣"},
    {"name": "锐", "pinyin": "rui", "wuxing": "金", "meaning": "锐利"},
    {"name": "锋", "pinyin": "feng", "wuxing": "金", "meaning": "锋芒"},
    {"name": "钟", "pinyin": "zhong", "wuxing": "金", "meaning": "钟声"},
    {"name": "钲", "pinyin": "zheng", "wuxing": "金", "meaning": "钲声"},
    {"name": "钱", "pinyin": "qian", "wuxing": "金", "meaning": "钱财"},
    {"name": "钦", "pinyin": "qin", "wuxing": "金", "meaning": "钦佩"},
    {"name": "钰", "pinyin": "yu", "wuxing": "金", "meaning": "珍宝"},
    {"name": "鑫", "pinyin": "xin", "wuxing": "金", "meaning": "财富兴盛"},
    {"name": "铎", "pinyin": "duo", "wuxing": "金", "meaning": "大铃"},
    # 水属性名字
    {"name": "润", "pinyin": "run", "wuxing": "水", "meaning": "润泽"},
    {"name": "泽", "pinyin": "ze", "wuxing": "水", "meaning": "恩泽"},
    {"name": "洁", "pinyin": "jie", "wuxing": "水", "meaning": "洁净"},
    {"name": "澜", "pinyin": "lan", "wuxing": "水", "meaning": "波澜"},
    {"name": "涛", "pinyin": "tao", "wuxing": "水", "meaning": "波涛"},
    {"name": "瀚", "pinyin": "han", "wuxing": "水", "meaning": "浩瀚"},
    {"name": "洋", "pinyin": "yang", "wuxing": "水", "meaning": "海洋"},
    {"name": "泉", "pinyin": "quan", "wuxing": "水", "meaning": "源泉"},
    {"name": "溪", "pinyin": "xi", "wuxing": "水", "meaning": "小溪"},
    {"name": "津", "pinyin": "jin", "wuxing": "水", "meaning": "津津"},
    {"name": "涵", "pinyin": "han", "wuxing": "水", "meaning": "包含"},
    {"name": "渊", "pinyin": "yuan", "wuxing": "水", "meaning": "深渊"},
    {"name": "洁", "pinyin": "jie", "wuxing": "水", "meaning": "清洁"},
    {"name": "漾", "pinyin": "yang", "wuxing": "水", "meaning": "水波荡漾"},
]

# 常用姓氏笔画表（简化版）
SURNAME_STROKES = {
    "王": 4, "李": 7, "张": 11, "刘": 6, "陈": 7, "杨": 7, "赵": 9, "黄": 11,
    "周": 8, "吴": 7, "徐": 10, "孙": 6, "胡": 9, "朱": 6, "高": 10, "林": 8,
    "何": 7, "郭": 10, "马": 3, "罗": 8, "梁": 11, "宋": 7, "郑": 8, "谢": 12,
    "韩": 12, "唐": 10, "冯": 12, "于": 3, "董": 12, "萧": 11, "程": 12, "曹": 7,
    "袁": 10, "邓": 12, "许": 11, "傅": 12, "沈": 7, "曾": 12, "彭": 12, "吕": 6,
    "苏": 7, "卢": 7, "蒋": 15, "蔡": 13, "贾": 10, "丁": 2, "魏": 12, "薛": 16,
    "叶": 5, "阎": 11, "余": 7, "潘": 12, "杜": 7, "戴": 13, "夏": 10, "钟": 9,
    "汪": 7, "田": 5, "任": 6, "姜": 9, "范": 8, "方": 4, "石": 5, "姚": 9,
    "谭": 19, "廖": 14, "邹": 7, "熊": 14, "金": 8, "陆": 11, "郝": 10, "孔": 4,
    "白": 5, "崔": 11, "康": 11, "毛": 4, "邱": 12, "秦": 10, "江": 6, "史": 5,
}

# 汉字笔画数表（简化版，包含常用字）
CHAR_STROKE_MAP = {
    # 木属性
    "林": 8, "松": 8, "柏": 9, "楠": 13, "桐": 10, "桂": 10, "樱": 15, "柳": 9,
    "梅": 11, "竹": 6, "芸": 7, "芬": 7, "芳": 7, "英": 8, "芝": 6, "荣": 9,
    "桃": 10, "桦": 10, "榆": 13, "槐": 14, "橙": 16, "桔": 10,
    "材": 7, "村": 7, "杏": 7, "枚": 8, "果": 8, "枣": 8, "枫": 8, "标": 9,
    # 火属性
    "灿": 7, "焕": 11, "辉": 12, "耀": 20, "熙": 14, "彤": 7, "丹": 4, "炎": 8,
    "昌": 8, "明": 8, "昊": 8, "旭": 6, "晨": 11, "昭": 9, "日": 4, "晶": 12,
    "晓": 10, "晔": 11, "晟": 10, "晧": 11, "晖": 11, "暄": 13, "晴": 12, "智": 12,
    "焱": 12, "煜": 13, "熠": 15, "燊": 16, "耿": 10, "炉": 8, "炖": 8, "炒": 8,
    # 土属性
    "墨": 15, "坤": 8, "培": 11, "壁": 16, "城": 10, "基": 11, "坚": 11, "岳": 8,
    "均": 7, "轩": 7, "玮": 8, "容": 10, "岩": 8, "峰": 10, "岭": 8, "巍": 20,
    "崔": 11, "崇": 11, "密": 11, "富": 12, "宪": 9, "定": 8, "宝": 8, "宫": 9,
    "室": 9, "宇": 6, "安": 6, "宁": 5, "宛": 8, "宜": 8, "实": 8, "审": 8,
    # 金属性
    "铭": 14, "钧": 9, "锦": 16, "锐": 15, "锋": 12, "钟": 9, "钲": 11, "钱": 10,
    "钦": 9, "钰": 10, "鑫": 24, "铎": 17, "镜": 19, "镛": 20, "铛": 12,
    "锡": 14, "镖": 16, "镔": 16, "鉴": 22, "铜": 11, "银": 14, "铁": 10, "钻": 10,
    "钮": 9, "钗": 10, "钏": 8, "钐": 8, "钜": 12, "镐": 15, "镇": 16,
    # 水属性
    "润": 12, "泽": 8, "洁": 10, "澜": 21, "涛": 10, "瀚": 20, "洋": 9, "泉": 9,
    "溪": 14, "津": 9, "涵": 11, "渊": 11, "漾": 14, "波": 8, "浪": 10,
    "海": 10, "洲": 9, "洪": 9, "治": 8, "泳": 8, "泪": 8, "涟": 11,
    "湛": 13, "滕": 15, "沂": 7, "淳": 11, "滨": 13, "潭": 15,
}


# ============ 数据结构 ============

@dataclass
class NameOption:
    """名字选项"""
    rank: int                                  # 排名
    surname: str                               # 姓
    given_name: str                            # 名（单字或双字）
    full_name: str                             # 全名
    wuxing_score: float                        # 五行补救分 0-100
    math_score: float                          # 姓名学数理分 0-100
    overall_score: float                       # 综合分 0-100
    level: str                                 # 等级
    wuxing_analysis: str                       # 五行分析
    math_analysis: str                         # 数理分析
    resonance_notes: List[str] = field(default_factory=list)  # 与命盘的共振说明

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rank": self.rank,
            "surname": self.surname,
            "given_name": self.given_name,
            "full_name": self.full_name,
            "wuxing_score": round(self.wuxing_score, 2),
            "math_score": round(self.math_score, 2),
            "overall_score": round(self.overall_score, 2),
            "level": self.level,
            "wuxing_analysis": self.wuxing_analysis,
            "math_analysis": self.math_analysis,
            "resonance_notes": self.resonance_notes,
        }


@dataclass
class NameRecommendationResult:
    """起名推荐结果"""
    service_type: str = "name_recommendation"
    birth_info: Dict[str, Any] = field(default_factory=dict)
    wuxing_lack: List[str] = field(default_factory=list)       # 缺什么五行
    wuxing_excess: List[str] = field(default_factory=list)     # 什么五行过盛
    recommended_radicals: List[str] = field(default_factory=list)  # 推荐偏旁
    avoided_radicals: List[str] = field(default_factory=list)   # 禁忌偏旁
    name_options: List[NameOption] = field(default_factory=list)
    best_name: Optional[NameOption] = None
    overall_analysis: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "service_type": self.service_type,
            "birth_info": self.birth_info,
            "wuxing_lack": self.wuxing_lack,
            "wuxing_excess": self.wuxing_excess,
            "recommended_radicals": self.recommended_radicals,
            "avoided_radicals": self.avoided_radicals,
            "name_options": [opt.to_dict() for opt in self.name_options],
            "best_name": self.best_name.to_dict() if self.best_name else None,
            "overall_analysis": self.overall_analysis,
            "confidence": round(self.confidence, 3),
        }


# ============ NameRecommendationAgent ============

class NameRecommendationAgent:
    """
    改名起名推荐引擎

    根据命盘五行属性，推荐最佳姓名，分析姓名学笔画数理并评分。

    Features:
    - 五行需求分析（缺什么、补什么）
    - 姓名学数理计算（天格、地格、人格、外格、总格）
    - 五行补救评分
    - 名字推荐排序
    """

    def __init__(
        self,
        birth_info: Dict[str, Any],              # {year, month, day, hour, gender, name, is_lunar}
        chart: Optional[Dict[str, Any]] = None,   # 命盘（可选）
        surname: str = "",                        # 姓氏
        name_style: str = "单字",                 # "单字" 或 "双字"
        top_n: int = 10,
    ):
        """
        初始化起名推荐

        Args:
            birth_info: 出生信息
            chart: 命盘数据（可选）
            surname: 姓氏
            name_style: 名字风格（单字/双字）
            top_n: 返回推荐数量
        """
        self.birth_info = birth_info
        self.chart = chart
        self.surname = surname or self._get_surname_from_birth_info()
        self.name_style = name_style
        self.top_n = top_n

        # 分析五行需求
        self.wuxing_lack: List[str] = []
        self.wuxing_excess: List[str] = []
        self.recommended_radicals: List[str] = []
        self.avoided_radicals: List[str] = []

        # 五行局（如果有命盘）
        self.wuxing_ju: Optional[str] = None
        if chart:
            self.wuxing_ju = chart.get("wuxing_ju") or chart.get("nayin")

        logger.info(f"NameRecommendationAgent initialized: surname={self.surname}, style={self.name_style}")

    def _get_surname_from_birth_info(self) -> str:
        """从出生信息中提取姓氏"""
        if self.birth_info.get("name"):
            # 尝试提取姓（假设全名格式为 姓+名）
            name = self.birth_info["name"]
            if len(name) >= 2:
                return name[0]
        return ""

    def _analyze_wuxing_needs(self) -> Tuple[List[str], List[str], List[str], List[str]]:
        """
        分析五行需求，返回 (缺五行, 过盛五行, 推荐偏旁, 禁忌偏旁)

        分析逻辑：
        1. 如果有命盘，使用命盘中的五行信息
        2. 否则根据五行局推断
        3. 结合四化信息调整
        """
        wuxing_counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

        # 从命盘分析五行分布
        if self.chart:
            # 分析命宫主星五行
            ming_gong = self.chart.get("ming_gong", {}) or {}
            main_stars = ming_gong.get("main_stars", []) or []
            for star in main_stars:
                star_wuxing = self._get_star_wuxing(star)
                if star_wuxing:
                    wuxing_counts[star_wuxing] += 2  # 主星权重更高

            # 分析身宫五行
            shen_gong = self.chart.get("shen_gong", {}) or {}
            shen_stars = shen_gong.get("main_stars", []) or []
            for star in shen_stars:
                star_wuxing = self._get_star_wuxing(star)
                if star_wuxing:
                    wuxing_counts[star_wuxing] += 1

            # 分析四化影响
            sibiaos = self.chart.get("sibiao", {}) or {}
            for transformation in sibiaos.values():
                if transformation:
                    # 化禄、化权、化科、化忌 对五行的影响
                    trans_wuxing = self._get_sibiao_wuxing(transformation)
                    if trans_wuxing:
                        if transformation in ["化禄", "化权", "化科"]:
                            wuxing_counts[trans_wuxing] += 1
                        else:  # 化忌
                            wuxing_counts[trans_wuxing] -= 1
        else:
            # 根据五行局推断
            if self.wuxing_ju:
                if "水" in self.wuxing_ju:
                    wuxing_counts["木"] = 2  # 水生木
                elif "木" in self.wuxing_ju:
                    wuxing_counts["火"] = 2  # 木生火
                elif "金" in self.wuxing_ju:
                    wuxing_counts["土"] = 2  # 金生土
                elif "土" in self.wuxing_ju:
                    wuxing_counts["金"] = 2  # 土生金
                elif "火" in self.wuxing_ju:
                    wuxing_counts["土"] = 2  # 火生土（特殊情况）

        # 计算缺什么和过盛
        lack = []
        excess = []
        for wuxing, count in wuxing_counts.items():
            if count <= 0:
                lack.append(wuxing)
            elif count >= 5:
                excess.append(wuxing)

        # 生成推荐和禁忌偏旁
        recommended = []
        avoided = []

        for w in lack:
            recommended.extend(WU_XING_RADICALS.get(w, [])[:5])

        for w in excess:
            avoided.extend(WU_XING_RADICALS.get(w, [])[:3])

        # 确保推荐和禁忌不重复
        recommended = list(set(recommended) - set(avoided))[:10]

        self.wuxing_lack = lack
        self.wuxing_excess = excess
        self.recommended_radicals = recommended
        self.avoided_radicals = avoided

        return lack, excess, recommended, avoided

    def _get_star_wuxing(self, star: str) -> Optional[str]:
        """获取星曜的五行属性"""
        # 简化版星曜五行表
        star_wuxing = {
            # 紫微星系
            "紫微": "土", "天机": "木", "太阳": "火",
            "武曲": "金", "天同": "水", "廉贞": "火",
            "天府": "土", "太阴": "水", "贪狼": "木",
            "巨门": "土", "天相": "水", "天梁": "土",
            "七杀": "金", "破军": "水",
            # 辅助星
            "文昌": "金", "文曲": "水", "左辅": "土", "右弼": "水",
            "科权禄": "木", "忌": "水",
        }
        return star_wuxing.get(star)

    def _get_sibiao_wuxing(self, sibiao: str) -> Optional[str]:
        """获取四化的五行"""
        sibiao_wuxing = {
            "化禄": "木",  # 化禄主木
            "化权": "火",  # 化权主火
            "化科": "金",  # 化科主金
            "化忌": "水",  # 化忌主水
        }
        return sibiao_wuxing.get(sibiao)

    def _get_radical_wuxing(self, char: str) -> Optional[str]:
        """
        获取汉字的五行属性（通过偏旁）

        Args:
            char: 单个汉字

        Returns:
            五行属性字符串（木/火/土/金/水）或 None
        """
        # 首先检查是否是五行直接对应
        if char in ["木", "火", "土", "金", "水"]:
            return char

        # 查找偏旁对应的五行
        for wuxing, radicals in WU_XING_RADICALS.items():
            if char in radicals:
                return wuxing

        return None

    def _calculate_wuxing_score(self, name: str, lack: List[str]) -> float:
        """
        计算名字的五行补救分

        Args:
            name: 名字（不含姓）
            lack: 缺的五行列表

        Returns:
            五行补救分 0-100
        """
        if not name or not lack:
            return 50.0  # 无分析条件返回中等分

        score = 50.0
        name_wuxings = []

        # 分析名字每个字的五行
        for char in name:
            wuxing = self._get_radical_wuxing(char)
            if wuxing:
                name_wuxings.append(wuxing)

        # 计算补救分
        matched_lack = sum(1 for w in name_wuxings if w in lack)

        if matched_lack > 0:
            # 有补救，每补一个+15分
            score += matched_lack * 15

        # 检查是否有禁忌五行
        has_excess = any(w in self.wuxing_excess for w in name_wuxings)
        if has_excess:
            score -= 20

        # 确保分数在有效范围内
        return max(0.0, min(100.0, score))

    def _calculate_math_score(self, surname: str, given_name: str) -> Tuple[float, str]:
        """
        计算姓名学数理分

        三才五格计算：
        - 天格：姓笔画数 + 1（复姓为姓笔画之和）
        - 地格：名笔画数 + 1（单名加1）
        - 人格：姓笔画首 + 名笔画首
        - 外格：天格尾 + 地格尾
        - 总格：所有笔画之和

        Args:
            surname: 姓
            given_name: 名

        Returns:
            (分数, 分析说明)
        """
        if not surname:
            return 50.0, "姓氏不详，无法计算"

        # 获取姓笔画数
        surname_strokes = SURNAME_STROKES.get(surname, 0) or len(surname) * 3
        if surname_strokes == 0:
            surname_strokes = len(surname) * 3  # 估算

        # 计算名的笔画数
        given_strokes = 0
        for char in given_name:
            strokes = CHAR_STROKE_MAP.get(char, 0) or len(char) * 3
            given_strokes += strokes

        # 计算五格
        tian_ge = surname_strokes + 1  # 天格
        di_ge = given_strokes + (1 if len(given_name) == 1 else 0)  # 地格（单名+1）
        ren_ge = surname_strokes + (CHAR_STROKE_MAP.get(given_name[0], 0) if given_name else 0)  # 人格
        wai_ge = (tian_ge % 10) + (di_ge % 10)  # 外格
        zong_ge = surname_strokes + given_strokes  # 总格

        # 确保数值在1-81范围内
        tian_ge = max(1, min(81, tian_ge))
        di_ge = max(1, min(81, di_ge))
        ren_ge = max(1, min(81, ren_ge))
        wai_ge = max(1, min(81, wai_ge))
        zong_ge = max(1, min(81, zong_ge))

        # 评估各格
        scores = []
        analyses = []

        for name, num in [("天格", tian_ge), ("人格", ren_ge), ("地格", di_ge), ("总格", zong_ge)]:
            if num in LUCKY_NUMBERS:
                scores.append(100)
                analyses.append(f"{name}{num}为吉数")
            elif num in UNLUCKY_NUMBERS:
                scores.append(40)
                analyses.append(f"{name}{num}为凶数")
            else:
                scores.append(70)
                analyses.append(f"{name}{num}为半吉")

        # 计算总分
        avg_score = sum(scores) / len(scores)

        # 综合分析
        analysis = f"天格{tian_ge}、人格{ren_ge}、地格{di_ge}、总格{zong_ge}。" + "；".join(analyses)

        return avg_score, analysis

    def _generate_candidates(self) -> List[Tuple[str, str]]:
        """
        生成候选名字

        Returns:
            [(given_name, wuxing), ...]
        """
        candidates = []

        # 根据五行需求过滤名字库
        if self.wuxing_lack:
            # 优先选择能补救的名字
            for entry in NAME_DATABASE:
                if entry["wuxing"] in self.wuxing_lack:
                    candidates.append((entry["name"], entry["wuxing"]))
        else:
            # 无特定需求，选择所有名字
            for entry in NAME_DATABASE:
                candidates.append((entry["name"], entry["wuxing"]))

        # 如果是双字名，组合生成
        if self.name_style == "双字" and self.recommended_radicals:
            # 使用推荐偏旁生成双字组合
            for radical in self.recommended_radicals[:5]:
                for entry in NAME_DATABASE[:10]:
                    # 简单组合，实际应更智能
                    pass  # 简化处理

        # 去重
        seen = set()
        unique_candidates = []
        for name, wuxing in candidates:
            if name not in seen:
                seen.add(name)
                unique_candidates.append((name, wuxing))

        return unique_candidates

    def _score_and_rank(self, candidates: List[Tuple[str, str]]) -> List[NameOption]:
        """
        评分并排序

        Args:
            candidates: 候选名字列表 [(name, wuxing), ...]

        Returns:
            排序后的名字选项列表
        """
        options = []

        for given_name, wuxing in candidates:
            if self.surname:
                full_name = self.surname + given_name
            else:
                full_name = given_name

            # 计算五行分
            wuxing_score = self._calculate_wuxing_score(given_name, self.wuxing_lack)

            # 计算数理分
            math_score, math_analysis = self._calculate_math_score(self.surname, given_name)

            # 综合分（五行60%，数理40%）
            overall_score = wuxing_score * 0.6 + math_score * 0.4

            # 生成五行分析
            wuxing_analysis = f"名字属{wuxing}行"
            if wuxing in self.wuxing_lack:
                wuxing_analysis += f"，可补救命局缺{wuxing}的不足"
            if wuxing in self.wuxing_excess:
                wuxing_analysis += f"，但需注意命局{self.wuxing_excess}已较旺"

            # 共振说明
            resonance = []
            if self.wuxing_ju:
                resonance.append(f"五行局：{self.wuxing_ju}")
            resonance.append(f"名字属性：{wuxing}行")

            # 确定等级
            if overall_score >= 85:
                level = "极佳"
            elif overall_score >= 70:
                level = "良好"
            elif overall_score >= 50:
                level = "中等"
            else:
                level = "一般"

            option = NameOption(
                rank=0,  # 待填充
                surname=self.surname,
                given_name=given_name,
                full_name=full_name,
                wuxing_score=wuxing_score,
                math_score=math_score,
                overall_score=overall_score,
                level=level,
                wuxing_analysis=wuxing_analysis,
                math_analysis=math_analysis,
                resonance_notes=resonance,
            )
            options.append(option)

        # 按综合分排序
        options.sort(key=lambda x: x.overall_score, reverse=True)

        # 填充排名
        for i, opt in enumerate(options[:self.top_n]):
            opt.rank = i + 1

        return options[:self.top_n]

    def recommend(self) -> NameRecommendationResult:
        """
        执行推荐

        Returns:
            NameRecommendationResult
        """
        logger.info("Starting name recommendation...")

        # 1. 分析五行需求
        lack, excess, recommended, avoided = self._analyze_wuxing_needs()

        # 2. 生成候选
        candidates = self._generate_candidates()

        # 3. 评分排序
        name_options = self._score_and_rank(candidates)

        # 4. 生成总体分析
        overall_analysis = self._generate_overall_analysis(lack, excess, name_options)

        # 5. 构建结果
        result = NameRecommendationResult(
            birth_info=self.birth_info,
            wuxing_lack=lack,
            wuxing_excess=excess,
            recommended_radicals=recommended,
            avoided_radicals=avoided,
            name_options=name_options,
            best_name=name_options[0] if name_options else None,
            overall_analysis=overall_analysis,
            confidence=0.85 if name_options else 0.5,
        )

        logger.info(f"Name recommendation completed: {len(name_options)} options generated")

        return result

    def _generate_overall_analysis(
        self,
        lack: List[str],
        excess: List[str],
        options: List[NameOption]
    ) -> str:
        """生成总体分析"""
        lines = []

        # 五行分析
        if lack:
            lines.append(f"命局五行缺{''.join(lack)}，宜用属{''.join(lack)}行的字补救")
        if excess:
            lines.append(f"命局五行{''.join(excess)}较旺，用字时需注意避免加重")

        # 推荐偏旁
        if self.recommended_radicals:
            radicals_str = "、".join(self.recommended_radicals[:5])
            lines.append(f"推荐偏旁部首：{radicals_str}等")

        # 最佳选择
        if options:
            best = options[0]
            lines.append(f"综合评分最高：{best.full_name}（{best.overall_score:.1f}分），{best.level}")

        return "；".join(lines)


# ============ 便捷函数 ============

def recommend_name_sync(
    birth_info: Dict[str, Any],
    chart: Optional[Dict[str, Any]] = None,
    surname: str = "",
    name_style: str = "单字",
    top_n: int = 10,
) -> NameRecommendationResult:
    """
    同步便捷函数

    Args:
        birth_info: 出生信息
        chart: 命盘数据
        surname: 姓氏
        name_style: 名字风格
        top_n: 推荐数量

    Returns:
        NameRecommendationResult
    """
    agent = NameRecommendationAgent(
        birth_info=birth_info,
        chart=chart,
        surname=surname,
        name_style=name_style,
        top_n=top_n,
    )
    return agent.recommend()


# ============ 导出 ============

__all__ = [
    "NameRecommendationAgent",
    "NameRecommendationResult",
    "NameOption",
    "recommend_name_sync",
]
