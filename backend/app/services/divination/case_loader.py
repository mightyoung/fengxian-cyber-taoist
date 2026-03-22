"""
大限案例加载器
用于加载和管理大限案例库
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from functools import lru_cache

from .case_models import (
    DaxianCase,
    DaxianCaseDatabase,
    DaxianCaseMetadata,
    CaseType,
    TransformType,
)


# 案例库文件路径
CASES_FILE_PATH = Path(__file__).parent / "resources" / "cases" / "daxian_cases.json"


class DaxianCaseLoader:
    """大限案例加载器"""

    _instance: Optional["DaxianCaseLoader"] = None
    _database: Optional[DaxianCaseDatabase] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化"""
        if self._database is None:
            self._load_database()

    def _load_database(self) -> None:
        """加载案例库"""
        if not CASES_FILE_PATH.exists():
            raise FileNotFoundError(f"案例库文件不存在: {CASES_FILE_PATH}")

        with open(CASES_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._database = DaxianCaseDatabase.from_dict(data)

    def reload(self) -> None:
        """重新加载案例库"""
        self._database = None
        self._load_database()

    @property
    def database(self) -> DaxianCaseDatabase:
        """获取案例库"""
        if self._database is None:
            self._load_database()
        return self._database

    @property
    def total_cases(self) -> int:
        """获取案例总数"""
        return self.database.get_total()

    @property
    def metadata(self) -> DaxianCaseMetadata:
        """获取元数据"""
        return self.database.metadata

    def get_all_cases(self) -> List[DaxianCase]:
        """获取所有案例"""
        return self.database.cases

    def get_case_by_id(self, case_id: str) -> Optional[DaxianCase]:
        """
        根据ID获取案例

        Args:
            case_id: 案例ID (如 "DX_001")

        Returns:
            案例对象，如果不存在返回None
        """
        for case in self.database.cases:
            if case.case_id == case_id:
                return case
        return None

    def get_cases_by_type(self, case_type: str) -> List[DaxianCase]:
        """
        根据类型获取案例

        Args:
            case_type: 案例类型 (如 "大限阶段", "大限四化")

        Returns:
            符合条件的案例列表
        """
        return self.database.get_cases_by_type(case_type)

    def get_cases_by_palace(self, palace: str) -> List[DaxianCase]:
        """
        根据宫位获取案例

        Args:
            palace: 宫位名称 (如 "命宫", "财帛宫")

        Returns:
            符合条件的案例列表
        """
        return self.database.get_cases_by_palace(palace)

    def get_daxian_stage_cases(self) -> List[DaxianCase]:
        """获取大限阶段案例"""
        return self.get_cases_by_type(CaseType.DA_XIAN_STAGE.value)

    def get_daxian_transform_cases(self) -> List[DaxianCase]:
        """获取大限四化案例"""
        return self.get_cases_by_type(CaseType.DA_XIAN_TRANSFORM.value)

    def get_wuxing_bureau_cases(self) -> List[DaxianCase]:
        """获取五行局案例"""
        return self.get_cases_by_type(CaseType.WUXING_BUREAU.value)

    def get_fate_mover_cases(self) -> List[DaxianCase]:
        """获取运限综合案例"""
        return self.get_cases_by_type(CaseType.FATE_MOVER.value)

    def get_transform_cases(self, transform_type: str) -> List[DaxianCase]:
        """
        获取特定四化类型的案例

        Args:
            transform_type: 四化类型 (如 "化禄", "化忌")

        Returns:
            符合条件的案例列表
        """
        return [
            case for case in self.get_daxian_transform_cases()
            if case.input.transform == transform_type
        ]

    def get_cases_by_dadian_number(self, dadian_number: int) -> List[DaxianCase]:
        """
        根据大限序号获取案例

        Args:
            dadian_number: 大限序号 (1-10)

        Returns:
            符合条件的案例列表
        """
        return [
            case for case in self.database.cases
            if case.input.dadian_number == dadian_number
        ]

    def search_cases(
        self,
        keyword: Optional[str] = None,
        case_type: Optional[str] = None,
        palace: Optional[str] = None,
        transform: Optional[str] = None,
        filter_func: Optional[Callable[[DaxianCase], bool]] = None
    ) -> List[DaxianCase]:
        """
        搜索案例

        Args:
            keyword: 关键词（搜索keywords和interpretation）
            case_type: 案例类型
            palace: 宫位
            transform: 四化类型
            filter_func: 自定义过滤函数

        Returns:
            符合条件的案例列表
        """
        results = self.database.cases

        # 按关键词过滤
        if keyword:
            keyword_lower = keyword.lower()
            results = [
                case for case in results
                if keyword_lower in case.output.interpretation.lower()
                or any(keyword_lower in k.lower() for k in case.output.keywords)
                or keyword_lower in case.name.lower()
            ]

        # 按类型过滤
        if case_type:
            results = [c for c in results if c.type == case_type]

        # 按宫位过滤
        if palace:
            results = [c for c in results if c.input.palace == palace]

        # 按四化类型过滤
        if transform:
            results = [c for c in results if c.input.transform == transform]

        # 自定义过滤
        if filter_func:
            results = [c for c in results if filter_func(c)]

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取案例库统计信息

        Returns:
            统计信息字典
        """
        cases = self.database.cases

        # 按类型统计
        type_counts: Dict[str, int] = {}
        for case in cases:
            type_counts[case.type] = type_counts.get(case.type, 0) + 1

        # 按宫位统计
        palace_counts: Dict[str, int] = {}
        for case in cases:
            if case.input.palace:
                palace_counts[case.input.palace] = palace_counts.get(case.input.palace, 0) + 1

        # 按四化统计
        transform_counts: Dict[str, int] = {}
        for case in cases:
            if case.input.transform:
                transform_counts[case.input.transform] = transform_counts.get(case.input.transform, 0) + 1

        return {
            "total_cases": len(cases),
            "metadata": {
                "source": self.metadata.source,
                "total_expected": self.metadata.total_cases,
                "extracted_date": self.metadata.extracted_date,
            },
            "by_type": type_counts,
            "by_palace": palace_counts,
            "by_transform": transform_counts,
        }


# 全局加载器实例
_loader: Optional[DaxianCaseLoader] = None


def get_case_loader() -> DaxianCaseLoader:
    """获取案例加载器实例"""
    global _loader
    if _loader is None:
        _loader = DaxianCaseLoader()
    return _loader


def load_daxian_cases() -> List[DaxianCase]:
    """
    加载所有大限案例

    Returns:
        案例列表
    """
    return get_case_loader().get_all_cases()


def get_case_by_id(case_id: str) -> Optional[DaxianCase]:
    """
    根据ID获取案例

    Args:
        case_id: 案例ID

    Returns:
        案例对象
    """
    return get_case_loader().get_case_by_id(case_id)


def search_daxian_cases(
    keyword: Optional[str] = None,
    case_type: Optional[str] = None,
    palace: Optional[str] = None,
) -> List[DaxianCase]:
    """
    搜索大限案例

    Args:
        keyword: 关键词
        case_type: 案例类型
        palace: 宫位

    Returns:
        符合条件的案例列表
    """
    return get_case_loader().search_cases(
        keyword=keyword,
        case_type=case_type,
        palace=palace,
    )


def get_daxian_statistics() -> Dict[str, Any]:
    """
    获取大限案例库统计

    Returns:
        统计信息
    """
    return get_case_loader().get_statistics()
