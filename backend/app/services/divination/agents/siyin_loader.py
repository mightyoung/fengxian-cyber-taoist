"""
六十星系加载器 - SiyinLoader

负责加载和管理六十星系数据，提供星系统一查询和分析功能。

六十星系是中州派紫微斗数的核心理论体系，将十四正曜按照同宫、共星、会照等关系
组合成60种特定的星曜配置，每种配置都有其独特的性格特征和运势倾向。
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


# 资源文件路径
RESOURCE_PATH = "app/services/divination/resources/siyin_system.json"


@dataclass
class SiyinStar:
    """单颗星曜信息"""
    id: str
    name: str
    main_star: str
    secondary_stars: List[str] = field(default_factory=list)
    palace_requirements: str = ""
    characteristics: str = ""
    positive_aspects: List[str] = field(default_factory=list)
    negative_aspects: List[str] = field(default_factory=list)


@dataclass
class SiyinSystem:
    """六十星系系统"""
    star_systems: List[SiyinStar] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SiyinLoader:
    """
    六十星系加载器

    提供六十星系数据的加载、查询和匹配功能。
    """

    _instance: Optional['SiyinLoader'] = None
    _data: Optional[Dict[str, Any]] = None

    def __new__(cls) -> 'SiyinLoader':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化加载器"""
        if self._data is None:
            self._load_data()

    def _get_resource_path(self) -> str:
        """获取资源文件路径

        使用 Path.resolve() 和 parent 属性来可靠地计算资源文件路径。
        文件位置: app/services/divination/agents/siyin_loader.py
        - parents[0] = agents/
        - parents[1] = divination/
        - parents[2] = services/
        - parents[3] = app/
        - parents[4] = backend/  (项目根目录)
        """
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parents[4]
        return str(backend_dir / RESOURCE_PATH)

    def _load_data(self) -> None:
        """加载六十星系数据"""
        try:
            resource_path = self._get_resource_path()
            with open(resource_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except FileNotFoundError:
            # 如果文件不存在，返回空数据
            self._data = {"sixty_star_systems": [], "metadata": {}}

    def get_all_systems(self) -> List[Dict[str, Any]]:
        """获取所有六十星系"""
        return self._data.get("sixty_star_systems", [])

    def get_system_by_id(self, system_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取星系统一"""
        systems = self.get_all_systems()
        for system in systems:
            if system.get("id") == system_id:
                return system
        return None

    def get_system_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取星系统一"""
        systems = self.get_all_systems()
        for system in systems:
            if system.get("name") == name:
                return system
        return None

    def find_systems_by_main_star(self, main_star: str) -> List[Dict[str, Any]]:
        """根据主星查找所有包含该星的星系统一"""
        systems = self.get_all_systems()
        return [
            s for s in systems
            if s.get("main_star") == main_star
        ]

    def find_systems_by_palace(self, palace: str) -> List[Dict[str, Any]]:
        """根据宫位查找星系统一"""
        systems = self.get_all_systems()
        matching = []
        for system in systems:
            requirements = system.get("palace_requirements", "")
            if palace in requirements:
                matching.append(system)
        return matching

    def find_system_by_stars_palace(
        self,
        main_star: str,
        secondary_stars: List[str],
        palace: str
    ) -> Optional[Dict[str, Any]]:
        """
        根据星曜组合和宫位查找匹配的星系统一

        Args:
            main_star: 主星名称
            secondary_stars: 副星列表
            palace: 宫位

        Returns:
            匹配的星系统一，如果没有匹配则返回None
        """
        systems = self.get_all_systems()

        for system in systems:
            # 检查主星
            if system.get("main_star") != main_star:
                continue

            # 检查副星
            system_secondary = system.get("secondary_stars", [])
            if set(system_secondary) != set(secondary_stars):
                continue

            # 检查宫位
            requirements = system.get("palace_requirements", "")
            if palace not in requirements:
                continue

            return system

        return None

    def get_siyin_interpretation(
        self,
        main_star: str,
        secondary_stars: List[str],
        palace: str
    ) -> Dict[str, Any]:
        """
        获取星曜组合的六十星系解读

        Args:
            main_star: 主星名称
            secondary_stars: 副星列表
            palace: 宫位

        Returns:
            包含解读结果的字典
        """
        system = self.find_system_by_stars_palace(main_star, secondary_stars, palace)

        if system:
            return {
                "matched": True,
                "system_id": system.get("id"),
                "system_name": system.get("name"),
                "characteristics": system.get("characteristics", ""),
                "positive_aspects": system.get("positive_aspects", []),
                "negative_aspects": system.get("negative_aspects", []),
                "interpretation": self._generate_interpretation(system)
            }

        # 如果没有精确匹配，尝试查找同主星的系统
        similar_systems = self.find_systems_by_main_star(main_star)
        if similar_systems:
            return {
                "matched": False,
                "system_id": None,
                "system_name": None,
                "characteristics": "",
                "positive_aspects": [],
                "negative_aspects": [],
                "interpretation": f"{main_star}星在{palace}宫的组合分析",
                "similar_systems": [
                    {
                        "id": s.get("id"),
                        "name": s.get("name"),
                        "palace_requirements": s.get("palace_requirements")
                    }
                    for s in similar_systems[:3]
                ]
            }

        return {
            "matched": False,
            "system_id": None,
            "system_name": None,
            "characteristics": "",
            "positive_aspects": [],
            "negative_aspects": [],
            "interpretation": f"{main_star}星在{palace}宫的组合分析"
        }

    def _generate_interpretation(self, system: Dict[str, Any]) -> str:
        """生成六十星系解读文本"""
        parts = []

        characteristics = system.get("characteristics", "")
        if characteristics:
            parts.append(characteristics)

        positive = system.get("positive_aspects", [])
        if positive:
            parts.append(f"优点: {', '.join(positive)}")

        negative = system.get("negative_aspects", [])
        if negative:
            parts.append(f"缺点: {', '.join(negative)}")

        return "。".join(parts)

    def get_metadata(self) -> Dict[str, Any]:
        """获取元数据"""
        return self._data.get("metadata", {})

    def get_grouped_systems(self) -> Dict[str, List[str]]:
        """获取按组分类的星系统一"""
        metadata = self.get_metadata()
        return metadata.get("grouping", {})

    def get_key_concepts(self) -> Dict[str, str]:
        """获取关键概念"""
        metadata = self.get_metadata()
        return metadata.get("key_concepts", {})

    def format_siyin_summary(self) -> str:
        """格式化六十星系概要"""
        lines = ["六十星系概要"]

        grouping = self.get_grouped_systems()
        for group_name, systems in grouping.items():
            lines.append(f"\n【{group_name}】")
            lines.append(f"  包含: {', '.join(systems)}")

        concepts = self.get_key_concepts()
        if concepts:
            lines.append("\n【关键概念】")
            for concept, description in concepts.items():
                lines.append(f"  {concept}: {description}")

        return "\n".join(lines)


# ============ 便捷函数 ============

def load_siyin_system() -> SiyinLoader:
    """
    加载六十星系数据

    Returns:
        SiyinLoader实例
    """
    return SiyinLoader()


def get_siyin_interpretation(
    main_star: str,
    secondary_stars: List[str],
    palace: str
) -> Dict[str, Any]:
    """
    获取星曜组合的六十星系解读

    Args:
        main_star: 主星名称
        secondary_stars: 副星列表
        palace: 宫位

    Returns:
        包含解读结果的字典
    """
    loader = load_siyin_system()
    return loader.get_siyin_interpretation(main_star, secondary_stars, palace)


def format_all_systems_brief() -> str:
    """格式化所有星系统一的简要列表"""
    loader = load_siyin_system()
    systems = loader.get_all_systems()

    lines = ["六十星系统一列表:"]
    for system in systems:
        lines.append(
            f"  {system.get('id')}: {system.get('name')} "
            f"({system.get('main_star')}, {system.get('palace_requirements')})"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试示例
    loader = SiyinLoader()

    print("=== 六十星系加载器测试 ===\n")

    # 测试加载
    all_systems = loader.get_all_systems()
    print(f"共加载 {len(all_systems)} 个星系统一\n")

    # 测试按ID查找
    system = loader.get_system_by_id("ZS_001")
    if system:
        print(f"ZS_001: {system.get('name')}")
        print(f"  主星: {system.get('main_star')}")
        print(f"  宫位要求: {system.get('palace_requirements')}")
        print(f"  特点: {system.get('characteristics')[:50]}...")

    # 测试按主星查找
    print("\n--- 紫微星相关的星系统一 ---")
    ziwei_systems = loader.find_systems_by_main_star("紫微")
    for s in ziwei_systems[:5]:
        print(f"  {s.get('id')}: {s.get('name')} ({s.get('palace_requirements')})")

    # 测试星曜组合匹配
    print("\n--- 测试星曜组合匹配 ---")
    result = loader.get_siyin_interpretation("紫微", ["贪狼"], "卯")
    print(f"紫微贪狼在卯宫: 匹配={result['matched']}")
    if result.get('system_name'):
        print(f"  星系统一: {result['system_name']}")
        print(f"  解读: {result['characteristics'][:80]}...")

    # 测试元数据
    print("\n--- 关键概念 ---")
    concepts = loader.get_key_concepts()
    for concept, desc in list(concepts.items())[:3]:
        print(f"  {concept}: {desc[:40]}...")
