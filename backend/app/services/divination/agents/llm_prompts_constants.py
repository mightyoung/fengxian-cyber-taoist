"""
LLM Prompts Constants - LLM提示词模块常量定义

包含：
- 案例库文件映射
- 案例库目录路径函数
- 知识库目录路径函数
- 案例加载函数

注意：Dataclasses 请使用 llm_prompts_types 模块
"""

import os
import json
from typing import Dict, Any, List

# 案例库文件映射
CASE_FILES: Dict[str, str] = {
    "transform": "transform_cases.json",
    "pattern": "pattern_cases.json",
    "palace": "palace_cases.json",
    "star": "star_cases.json",
    "daxian": "daxian_cases.json",
    "six_relation": "six_relation_cases.json",
}


def _get_cases_dir() -> str:
    """获取案例库目录路径"""
    return os.path.join(
        os.path.dirname(__file__),
        "..", "resources", "cases"
    )


def _get_knowledge_base_dir() -> str:
    """获取知识库目录路径"""
    return os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "data_source", "knowledge_base", "divination"
    )


def _load_case_file(filename: str) -> Dict[str, Any]:
    """加载案例文件"""
    cases_path = os.path.join(_get_cases_dir(), filename)
    if os.path.exists(cases_path):
        try:
            with open(cases_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"cases": []}


def load_transform_cases() -> List[Dict[str, Any]]:
    """加载四化案例库"""
    data = _load_case_file(CASE_FILES.get("transform", "transform_cases.json"))
    return data.get("cases", [])


def load_pattern_cases() -> List[Dict[str, Any]]:
    """加载格局案例库"""
    data = _load_case_file(CASE_FILES.get("pattern", "pattern_cases.json"))
    return data.get("cases", [])


def load_palace_cases() -> List[Dict[str, Any]]:
    """加载宫位案例库"""
    data = _load_case_file(CASE_FILES.get("palace", "palace_cases.json"))
    return data.get("cases", [])


def load_star_cases() -> List[Dict[str, Any]]:
    """加载星曜案例库"""
    data = _load_case_file(CASE_FILES.get("star", "star_cases.json"))
    return data.get("cases", [])


def load_daxian_cases() -> List[Dict[str, Any]]:
    """加载大限案例库"""
    data = _load_case_file(CASE_FILES.get("daxian", "daxian_cases.json"))
    return data.get("cases", [])


def load_six_relation_cases() -> List[Dict[str, Any]]:
    """加载六亲论断案例库"""
    data = _load_case_file(CASE_FILES.get("six_relation", "six_relation_cases.json"))
    return data.get("cases", [])


def load_flying_star_rules() -> Dict[str, Any]:
    """加载飞星四化核心规则库"""
    rules_path = os.path.join(_get_knowledge_base_dir(), "flying_star_transforms.json")
    if os.path.exists(rules_path):
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"rules": {}}
