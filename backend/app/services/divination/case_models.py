"""
大限案例数据模型
用于定义大限案例库的数据结构和验证
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class CaseType(str, Enum):
    """案例类型枚举"""
    DA_XIAN_STAGE = "大限阶段"           # 大限阶段（命宫流转）
    DA_XIAN_TRANSFORM = "大限四化"       # 大限四化（化禄/化权/化科/化忌）
    WUXING_BUREAU = "五行局"              # 五行局（水二局/木三局等）
    FATE_MOVER = "运限综合"              # 运限综合（格局组合）


class ZodiacType(str, Enum):
    """八字类型"""
    MALE_POSITIVE = "阳男阴女顺行"
    FEMALE_POSITIVE = "阴男阳女逆行"


class TransformType(str, Enum):
    """四化类型"""
    HUA_LU = "化禄"   # 化禄
    HUA_QUAN = "化权"  # 化权
    HUA_KE = "化科"   # 化科
    HUA_JI = "化忌"   # 化忌


@dataclass
class DaxianStageInput:
    """大限阶段输入"""
    dadian_number: int
    age_range: str
    palace: str
    zodiac_type: str


@dataclass
class DaxianTransformInput:
    """大限四化输入"""
    dadian_number: int
    age_range: str
    transform: str
    palace: str


@dataclass
class WuxingBureauInput:
    """五行局输入"""
    wuxing_bureau: str
    main_stars: List[str]
    palace: str


@dataclass
class FateMoverInput:
    """运限综合输入"""
    stars: Optional[List[str]] = None
    transform_1: Optional[str] = None
    transform_2: Optional[str] = None
    palace: Optional[str] = None


@dataclass
class CaseInput:
    """通用案例输入（兼容所有类型）"""
    # 年干
    birth_year_gan: Optional[str] = None

    # 大限阶段字段
    dadian_number: Optional[int] = None
    age_range: Optional[str] = None
    palace: Optional[str] = None
    zodiac_type: Optional[str] = None

    # 大限四化字段
    transform: Optional[str] = None

    # 五行局字段
    wuxing_bureau: Optional[str] = None
    main_stars: Optional[List[str]] = None

    # 运限综合字段
    stars: Optional[List[str]] = None
    transform_1: Optional[str] = None
    transform_2: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaseInput":
        """从字典创建"""
        return cls(
            birth_year_gan=data.get("birth_year_gan"),
            dadian_number=data.get("dadian_number"),
            age_range=data.get("age_range"),
            palace=data.get("palace"),
            zodiac_type=data.get("zodiac_type"),
            transform=data.get("transform"),
            wuxing_bureau=data.get("wuxing_bureau"),
            main_stars=data.get("main_stars"),
            stars=data.get("stars"),
            transform_1=data.get("transform_1"),
            transform_2=data.get("transform_2"),
        )


@dataclass
class CaseOutput:
    """案例输出"""
    interpretation: str
    keywords: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaseOutput":
        """从字典创建"""
        return cls(
            interpretation=data.get("interpretation", ""),
            keywords=data.get("keywords", [])
        )


@dataclass
class DaxianCase:
    """大限案例"""
    case_id: str
    agent: str
    type: str
    name: str
    input: CaseInput
    output: CaseOutput
    source: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DaxianCase":
        """从字典创建"""
        return cls(
            case_id=data["case_id"],
            agent=data.get("agent", "TimingAgent"),
            type=data.get("type", ""),
            name=data.get("name", ""),
            input=CaseInput.from_dict(data.get("input", {})),
            output=CaseOutput.from_dict(data.get("output", {})),
            source=data.get("source", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "case_id": self.case_id,
            "agent": self.agent,
            "type": self.type,
            "name": self.name,
            "input": {
                k: v for k, v in {
                    "birth_year_gan": self.input.birth_year_gan,
                    "dadian_number": self.input.dadian_number,
                    "age_range": self.input.age_range,
                    "palace": self.input.palace,
                    "zodiac_type": self.input.zodiac_type,
                    "transform": self.input.transform,
                    "wuxing_bureau": self.input.wuxing_bureau,
                    "main_stars": self.input.main_stars,
                    "stars": self.input.stars,
                    "transform_1": self.input.transform_1,
                    "transform_2": self.input.transform_2,
                }.items() if v is not None
            },
            "output": {
                "interpretation": self.output.interpretation,
                "keywords": self.output.keywords
            },
            "source": self.source
        }


@dataclass
class DaxianCaseMetadata:
    """案例库元数据"""
    source: str
    total_cases: int
    extracted_date: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DaxianCaseMetadata":
        """从字典创建"""
        return cls(
            source=data.get("source", ""),
            total_cases=data.get("total_cases", 0),
            extracted_date=data.get("extracted_date", "")
        )


@dataclass
class DaxianCaseDatabase:
    """完整案例库"""
    metadata: DaxianCaseMetadata
    cases: List[DaxianCase] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DaxianCaseDatabase":
        """从字典创建"""
        metadata = DaxianCaseMetadata.from_dict(data.get("metadata", {}))
        cases = [DaxianCase.from_dict(c) for c in data.get("cases", [])]
        return cls(metadata=metadata, cases=cases)

    def get_total(self) -> int:
        """获取案例总数"""
        return len(self.cases)

    def get_cases_by_type(self, case_type: str) -> List[DaxianCase]:
        """按类型筛选案例"""
        return [c for c in self.cases if c.type == case_type]

    def get_cases_by_palace(self, palace: str) -> List[DaxianCase]:
        """按宫位筛选案例"""
        return [c for c in self.cases if c.input.palace == palace]

    def search_by_keyword(self, keyword: str) -> List[DaxianCase]:
        """按关键词搜索"""
        keyword_lower = keyword.lower()
        return [
            c for c in self.cases
            if any(keyword_lower in k.lower() for k in c.output.keywords)
        ]
