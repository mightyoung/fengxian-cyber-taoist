"""
SocialNetworkSimulator - 命盘社交网络模拟

基于紫微斗数宫位关系构建Agent社交网络：
- 三方四正关系映射为社交连接
- 计算宫位间影响权重
- 模拟影响力传播路径
"""

from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class RelationType(str, Enum):
    """关系类型"""
    BEN_GONG = "本宫"      # 自身
    SAN_FANG = "三方"      # 三方四正
    DUI_GONG = "对宫"      # 对宫关系
    XING_XIANG = "星曜"    # 星曜关联
    CHA_GONG = "差宫"      # 其他弱关联


class PalaceType(str, Enum):
    """宫位类型"""
    NEI_GONG = "内宫"      # 内宫（命、财帛、疾厄、官禄、田宅、福德）
    WAI_GONG = "外宫"      # 外宫（兄弟、夫妻、子女、迁移、仆役、父母）


@dataclass
class SocialEdge:
    """社交网络边"""
    source: str           # 源宫位 (e.g., "命宫")
    target: str           # 目标宫位 (e.g., "官禄宫")
    weight: float         # 影响权重 (0.0-1.0)
    relation: RelationType # 关系类型
    direction: str        # 影响方向: "单向" | "双向"
    decay_rate: float = 0.15  # 传播衰减率

    def __post_init__(self):
        """验证数据"""
        if not 0.0 <= self.weight <= 1.0:
            self.weight = max(0.0, min(1.0, self.weight))


@dataclass
class SocialNode:
    """社交网络节点"""
    palace: str                       # 宫位名称
    palace_type: PalaceType           # 宫位类型
    stars: List[str]                  # 主星列表
    social_score: float = 50.0        # 社交影响力 (0-100)
    connections: List[str] = field(default_factory=list)  # 直接连接的其他宫位
    in_degree: int = 0                # 入度
    out_degree: int = 0               # 出度

    def add_connection(self, other_palace: str) -> None:
        """添加连接"""
        if other_palace not in self.connections:
            self.connections.append(other_palace)

    def get_centrality_score(self) -> float:
        """计算基础中心性分数"""
        return self.social_score * (len(self.connections) / 11.0)


@dataclass
class SocialNetwork:
    """社交网络"""
    nodes: Dict[str, SocialNode]
    edges: List[SocialEdge]
    adjacency: Dict[str, List[str]] = field(default_factory=dict)  # 邻接表: {宫位: [相连宫位列表]}

    # 基础权重常量
    WEIGHT_SAN_FANG: float = 0.8     # 三方关系权重
    WEIGHT_DUI_GONG: float = 0.5     # 对宫关系权重
    WEIGHT_BEN_GONG: float = 1.0     # 本宫关系权重
    WEIGHT_CHA_GONG: float = 0.2     # 差宫关系权重
    WEIGHT_WAI_GONG_BONUS: float = 0.05  # 外宫加成
    WEIGHT_WAI_GONG_BONUS: float = 0.1   # 内宫加成

    def __post_init(self):
        """初始化邻接表"""
        if not self.adjacency:
            self._build_adjacency()

    def _build_adjacency(self) -> None:
        """构建邻接表（处理双向边）"""
        self.adjacency = {palace: [] for palace in self.nodes}
        for edge in self.edges:
            # 添加正向边
            if edge.source not in self.adjacency:
                self.adjacency[edge.source] = []
            if edge.target not in self.adjacency[edge.source]:
                self.adjacency[edge.source].append(edge.target)

            # 双向边：也添加反向边
            if edge.direction == "双向":
                if edge.target not in self.adjacency:
                    self.adjacency[edge.target] = []
                if edge.source not in self.adjacency[edge.target]:
                    self.adjacency[edge.target].append(edge.source)

    def get_influence_chain(self, from_palace: str, to_palace: str) -> List[str]:
        """
        获取从from宫到to宫的影响链（BFS最短路径）

        Args:
            from_palace: 起点宫位
            to_palace: 终点宫位

        Returns:
            影响链路径列表，若无路径则返回空列表
        """
        if from_palace not in self.adjacency or to_palace not in self.adjacency:
            return []

        if from_palace == to_palace:
            return [from_palace]

        # BFS 寻找最短路径
        visited: Set[str] = {from_palace}
        queue: deque[Tuple[str, List[str]]] = deque()
        queue.append((from_palace, [from_palace]))

        while queue:
            current, path = queue.popleft()

            for neighbor in self.adjacency.get(current, []):
                if neighbor == to_palace:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []

    def calculate_degree_centrality(self, palace: str) -> float:
        """
        计算度中心性（归一化）

        Args:
            palace: 宫位名称

        Returns:
            度中心性分数 (0-1)
        """
        if palace not in self.nodes:
            return 0.0

        node = self.nodes[palace]
        total_degree = len(self.nodes) - 1  # 最大可能的连接数
        if total_degree <= 0:
            return 0.0

        return len(node.connections) / total_degree

    def calculate_closeness_centrality(self, palace: str) -> float:
        """
        计算接近中心性

        Args:
            palace: 宫位名称

        Returns:
            接近中心性分数 (0-1)
        """
        if palace not in self.adjacency:
            return 0.0

        # BFS计算到所有其他节点的距离
        distances: Dict[str, int] = {palace: 0}
        queue: deque[str] = deque([palace])

        while queue:
            current = queue.popleft()
            current_dist = distances[current]

            for neighbor in self.adjacency.get(current, []):
                if neighbor not in distances:
                    distances[neighbor] = current_dist + 1
                    queue.append(neighbor)

        # 计算平均距离
        if len(distances) <= 1:
            return 0.0

        total_distance = sum(distances.values())
        avg_distance = total_distance / (len(distances) - 1)

        # 接近中心性 = n-1 / 平均距离
        n = len(self.nodes)
        return (n - 1) / (avg_distance * (n - 1)) if avg_distance > 0 else 0.0

    def calculate_betweenness_centrality(self, palace: str) -> float:
        """
        计算中介中心性

        Args:
            palace: 宫位名称

        Returns:
            中介中心性分数 (0-1)
        """
        if palace not in self.nodes:
            return 0.0

        n = len(self.nodes)
        if n <= 2:
            return 0.0

        # 计算经过该节点的最短路径数量
        betweenness = 0.0
        nodes_list = list(self.nodes.keys())

        for source in nodes_list:
            if source == palace:
                continue

            for target in nodes_list:
                if target == palace or target == source:
                    continue

                # 获取source到target的最短路径
                path = self.get_influence_chain(source, target)
                if len(path) > 1 and palace in path:
                    # 计算该路径占总路径的比例
                    betweenness += 1.0 / len(path)

        # 归一化
        max_betweenness = (n - 1) * (n - 2) / 2
        return betweenness / max_betweenness if max_betweenness > 0 else 0.0

    def calculate_centrality(self, palace: str) -> float:
        """
        计算综合中心性（度中心性 + 接近中心性 + 中介中心性的加权平均）

        Args:
            palace: 宫位名称

        Returns:
            综合中心性分数 (0-1)
        """
        degree = self.calculate_degree_centrality(palace)
        closeness = self.calculate_closeness_centrality(palace)
        betweenness = self.calculate_betweenness_centrality(palace)

        # 加权综合
        return 0.4 * degree + 0.3 * closeness + 0.3 * betweenness

    def get_edge_weight(self, source: str, target: str) -> float:
        """
        获取两个宫位之间的边权重

        对于三方和对宫关系，即使边只在一个方向定义，也返回其权重。
        这因为这些关系在物理上是双向的。

        Args:
            source: 源宫位
            target: 目标宫位

        Returns:
            边权重，若不存在则返回0
        """
        # 优先查找正向边
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                return edge.weight

        # 对于三方和对宫关系，查找反向边
        for edge in self.edges:
            if edge.source == target and edge.target == source:
                if edge.relation in (RelationType.SAN_FANG, RelationType.DUI_GONG):
                    return edge.weight

        return 0.0

    def get_all_centralities(self) -> Dict[str, float]:
        """
        获取所有宫位的综合中心性

        Returns:
            {宫位名: 中心性分数} 字典，按分数降序排列
        """
        centralities = {
            palace: self.calculate_centrality(palace)
            for palace in self.nodes
        }
        return dict(sorted(centralities.items(), key=lambda x: x[1], reverse=True))

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "nodes": {
                name: {
                    "palace": node.palace,
                    "palace_type": node.palace_type.value,
                    "stars": node.stars,
                    "social_score": node.social_score,
                    "connections": node.connections,
                    "centrality": self.calculate_centrality(name),
                }
                for name, node in self.nodes.items()
            },
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "weight": edge.weight,
                    "relation": edge.relation.value,
                    "direction": edge.direction,
                }
                for edge in self.edges
            ],
            "centralities": self.get_all_centralities(),
        }


class SocialNetworkSimulator:
    """
    社交网络模拟器

    基于命盘宫位关系构建社交网络，模拟Agent之间的影响力传播。
    """

    # 12个宫位名称
    PALACE_NAMES: List[str] = [
        "命宫", "兄弟宫", "夫妻宫", "子女宫",
        "财帛宫", "疾厄宫", "迁移宫", "仆役宫",
        "官禄宫", "田宅宫", "福德宫", "父母宫"
    ]

    # 内宫列表
    NEI_GONGS: Set[str] = {"命宫", "财帛宫", "疾厄宫", "官禄宫", "田宅宫", "福德宫"}

    # 三方关系映射 {本宫: [三方宫位]}
    SAN_FANG_MAP: Dict[str, List[str]] = {
        "命宫": ["官禄宫", "财帛宫", "迁移宫"],
        "兄弟宫": ["田宅宫", "仆役宫", "福德宫"],
        "夫妻宫": ["官禄宫", "迁移宫", "福德宫"],
        "子女宫": ["官禄宫", "迁移宫", "父母宫"],
        "财帛宫": ["命宫", "官禄宫", "迁移宫"],
        "疾厄宫": ["田宅宫", "父母宫", "兄弟宫"],
        "迁移宫": ["命宫", "官禄宫", "财帛宫"],
        "仆役宫": ["田宅宫", "兄弟宫", "福德宫"],
        "官禄宫": ["命宫", "财帛宫", "迁移宫"],
        "田宅宫": ["兄弟宫", "仆役宫", "福德宫"],
        "福德宫": ["命宫", "兄弟宫", "夫妻宫"],
        "父母宫": ["疾厄宫", "子女宫", "官禄宫"],
    }

    # 对宫关系映射 {本宫: 对宫}
    DUI_GONG_MAP: Dict[str, str] = {
        "命宫": "福德宫",
        "兄弟宫": "官禄宫",
        "夫妻宫": "田宅宫",
        "子女宫": "仆役宫",
        "财帛宫": "迁移宫",
        "疾厄宫": "父母宫",
        "迁移宫": "财帛宫",
        "仆役宫": "子女宫",
        "官禄宫": "兄弟宫",
        "田宅宫": "夫妻宫",
        "福德宫": "命宫",
        "父母宫": "疾厄宫",
    }

    def __init__(self, chart_data: Dict[str, Any]):
        """
        初始化社交网络模拟器

        Args:
            chart_data: 命盘数据，包含各宫位的星曜信息
        """
        self.chart = chart_data
        self.network = self._build_network()

    def _get_palace_type(self, palace: str) -> PalaceType:
        """获取宫位类型"""
        if palace in self.NEI_GONGS:
            return PalaceType.NEI_GONG
        return PalaceType.WAI_GONG

    def _get_palace_stars(self, palace: str) -> List[str]:
        """从命盘数据获取宫位星曜"""
        # 尝试多种数据格式
        palaces_data = self.chart.get("palaces", self.chart)

        if isinstance(palaces_data, dict):
            palace_info = palaces_data.get(palace, {})
            if isinstance(palace_info, dict):
                return palace_info.get("stars", palace_info.get("主星", []))
            elif isinstance(palace_info, list):
                return palace_info
        elif isinstance(palaces_data, list):
            for p in palaces_data:
                if isinstance(p, dict) and p.get("name") == palace:
                    return p.get("stars", p.get("主星", []))
                elif isinstance(p, str) and p == palace:
                    return []

        return []

    def _calculate_edge_weight(
        self,
        source: str,
        target: str,
        relation: RelationType
    ) -> float:
        """
        计算边权重

        Args:
            source: 源宫位
            target: 目标宫位
            relation: 关系类型

        Returns:
            权重值 (0-1)
        """
        # 基础权重
        base_weight = {
            RelationType.BEN_GONG: SocialNetwork.WEIGHT_BEN_GONG,
            RelationType.SAN_FANG: SocialNetwork.WEIGHT_SAN_FANG,
            RelationType.DUI_GONG: SocialNetwork.WEIGHT_DUI_GONG,
            RelationType.CHA_GONG: SocialNetwork.WEIGHT_CHA_GONG,
        }.get(relation, SocialNetwork.WEIGHT_CHA_GONG)

        # 内宫加成
        source_type = self._get_palace_type(source)
        target_type = self._get_palace_type(target)

        bonus = 0.0
        if source_type == PalaceType.NEI_GONG:
            bonus += 0.1
        if target_type == PalaceType.NEI_GONG:
            bonus += 0.1

        return min(1.0, base_weight + bonus)

    def _build_network(self) -> SocialNetwork:
        """
        根据命盘构建社交网络

        Returns:
            构建好的社交网络
        """
        nodes: Dict[str, SocialNode] = {}
        edges: List[SocialEdge] = []

        # 1. 创建12个宫位节点
        for palace in self.PALACE_NAMES:
            palace_type = self._get_palace_type(palace)
            stars = self._get_palace_stars(palace)

            # 根据星曜计算社交影响力
            social_score = self._calculate_social_score(stars, palace)

            nodes[palace] = SocialNode(
                palace=palace,
                palace_type=palace_type,
                stars=stars,
                social_score=social_score,
            )

        # 2. 创建边

        # 2.1 创建三方关系边
        for source, targets in self.SAN_FANG_MAP.items():
            if source not in nodes:
                continue

            for target in targets:
                if target not in nodes:
                    continue

                weight = self._calculate_edge_weight(source, target, RelationType.SAN_FANG)

                edge = SocialEdge(
                    source=source,
                    target=target,
                    weight=weight,
                    relation=RelationType.SAN_FANG,
                    direction="双向",
                )
                edges.append(edge)

                # 更新节点连接
                nodes[source].add_connection(target)
                nodes[target].add_connection(source)
                nodes[source].out_degree += 1
                nodes[target].in_degree += 1

        # 2.2 创建对宫关系边（对宫是重要的关联，使用双向边）
        for source, target in self.DUI_GONG_MAP.items():
            if source not in nodes or target not in nodes:
                continue

            # 检查是否已存在边
            exists = any(
                (e.source == source and e.target == target) or
                (e.source == target and e.target == source)
                for e in edges
            )

            if not exists:
                weight = self._calculate_edge_weight(source, target, RelationType.DUI_GONG)

                edge = SocialEdge(
                    source=source,
                    target=target,
                    weight=weight,
                    relation=RelationType.DUI_GONG,
                    direction="双向",
                )
                edges.append(edge)

                # 更新节点连接
                nodes[source].add_connection(target)
                nodes[target].add_connection(source)
                nodes[source].out_degree += 1
                nodes[target].in_degree += 1

        # 2.3 创建本宫自环（可选，用于强调自身）
        # 本实现暂不添加自环

        # 3. 构建邻接表
        adjacency: Dict[str, List[str]] = {palace: [] for palace in nodes}
        for edge in edges:
            # 添加正向边
            if edge.target not in adjacency[edge.source]:
                adjacency[edge.source].append(edge.target)
            # 双向边：也添加反向边
            if edge.direction == "双向":
                if edge.source not in adjacency[edge.target]:
                    adjacency[edge.target].append(edge.source)

        return SocialNetwork(
            nodes=nodes,
            edges=edges,
            adjacency=adjacency,
        )

    def _calculate_social_score(self, stars: List[str], palace: str) -> float:
        """
        根据星曜计算社交影响力分数

        Args:
            stars: 星曜列表
            palace: 宫位名称

        Returns:
            社交影响力分数 (0-100)
        """
        base_score = 50.0

        # 社交影响力强的星曜
        social_stars = {
            "贪狼": 15, "太阳": 12, "紫微": 12,
            "天同": 8, "天机": 8, "天府": 8,
            "左辅": 6, "右弼": 6, "文曲": 5,
            "文昌": 4, "天梁": 4,
        }

        # 社交影响力弱的星曜
        anti_social_stars = {
            "巨门": -8, "七杀": -5, "破军": -5,
            "廉贞": -3, "武曲": -2,
        }

        for star in stars:
            base_score += social_stars.get(star, 0)
            base_score += anti_social_stars.get(star, 0)

        # 宫位加成
        if palace in ["命宫", "迁移宫"]:
            base_score += 5  # 命宫和迁移宫天然有更多社交机会
        elif palace in ["仆役宫", "福德宫"]:
            base_score += 3

        return max(0.0, min(100.0, base_score))

    def get_agent_social_position(self, palace: str) -> Dict[str, Any]:
        """
        获取某宫位在社交网络中的位置

        Args:
            palace: 宫位名称

        Returns:
            社交位置信息字典
        """
        if palace not in self.network.nodes:
            return {"error": f"宫位 {palace} 不存在"}

        node = self.network.nodes[palace]

        # 获取所有中心性指标
        degree_cent = self.network.calculate_degree_centrality(palace)
        closeness_cent = self.network.calculate_closeness_centrality(palace)
        betweenness_cent = self.network.calculate_betweenness_centrality(palace)
        overall_cent = self.network.calculate_centrality(palace)

        # 获取相邻宫位及其权重
        neighbors = []
        for target in node.connections:
            weight = self.network.get_edge_weight(palace, target)
            neighbors.append({
                "palace": target,
                "weight": weight,
                "relation": self._get_relation_type(palace, target),
            })

        # 排序邻居（按权重）
        neighbors.sort(key=lambda x: x["weight"], reverse=True)

        # 计算网络排名
        all_centralities = self.network.get_all_centralities()
        rank = list(all_centralities.keys()).index(palace) + 1

        return {
            "palace": palace,
            "palace_type": node.palace_type.value,
            "stars": node.stars,
            "social_score": node.social_score,
            "centrality": {
                "degree": round(degree_cent, 4),
                "closeness": round(closeness_cent, 4),
                "betweenness": round(betweenness_cent, 4),
                "overall": round(overall_cent, 4),
            },
            "rank": rank,
            "total_palaces": len(self.network.nodes),
            "connections": {
                "count": len(node.connections),
                "list": neighbors,
            },
            "influence_range": self._calculate_influence_range(palace),
        }

    def _get_relation_type(self, source: str, target: str) -> str:
        """获取两个宫位之间的关系类型"""
        if target in self.SAN_FANG_MAP.get(source, []):
            return "三方"
        if self.DUI_GONG_MAP.get(source) == target:
            return "对宫"
        return "其他"

    def _calculate_influence_range(self, palace: str, max_hops: int = 3) -> Dict[str, Any]:
        """
        计算影响力范围

        Args:
            palace: 宫位名称
            max_hops: 最大跳数

        Returns:
            影响力范围信息
        """
        reachable: Dict[int, List[str]] = {}
        visited: Set[str] = {palace}
        queue: deque[Tuple[str, int]] = deque()

        # BFS初始化
        for neighbor in self.network.adjacency.get(palace, []):
            queue.append((neighbor, 1))
            if 1 not in reachable:
                reachable[1] = []
            if neighbor not in reachable[1]:
                reachable[1].append(neighbor)

        # BFS扩展
        while queue:
            current, hops = queue.popleft()

            if hops >= max_hops:
                continue

            for neighbor in self.network.adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_hops = hops + 1
                    if next_hops not in reachable:
                        reachable[next_hops] = []
                    if neighbor not in reachable[next_hops]:
                        reachable[next_hops].append(neighbor)
                    queue.append((neighbor, next_hops))

        return {
            "total_reachable": len(visited) - 1,
            "by_hops": {k: len(v) for k, v in reachable.items()},
            "palaces_by_hops": reachable,
        }

    def simulate_influence_propagation(
        self,
        source: str,
        magnitude: float,
        max_hops: int = 3,
        decay_rate: float = 0.15
    ) -> Dict[str, float]:
        """
        模拟影响力传播（BFS扩散）

        Args:
            source: 源头宫位
            magnitude: 初始影响力强度 (0-100)
            max_hops: 最大传播跳数
            decay_rate: 每跳衰减率

        Returns:
            {宫位: 接收到的影响力} 字典
        """
        if source not in self.network.nodes:
            return {"error": f"宫位 {source} 不存在"}

        # 影响力记录
        influence: Dict[str, float] = {source: magnitude}

        # BFS扩散
        visited: Set[str] = {source}
        queue: deque[Tuple[str, float, int]] = deque()

        # 初始化队列（一跳邻居）
        for neighbor in self.network.adjacency.get(source, []):
            edge_weight = self.network.get_edge_weight(source, neighbor)
            received = magnitude * edge_weight * (1 - decay_rate)
            queue.append((neighbor, received, 1))
            influence[neighbor] = max(influence.get(neighbor, 0), received)

        # BFS扩散
        while queue:
            current, current_influence, hops = queue.popleft()

            if hops >= max_hops:
                continue

            next_influence = current_influence * (1 - decay_rate)

            for neighbor in self.network.adjacency.get(current, []):
                if neighbor in visited:
                    continue

                visited.add(neighbor)

                # 计算边的综合影响值
                edge_weight = self.network.get_edge_weight(current, neighbor)
                received = next_influence * edge_weight

                # 更新影响力
                influence[neighbor] = max(influence.get(neighbor, 0), received)

                # 加入队列继续扩散
                queue.append((neighbor, received, hops + 1))

        return influence

    def get_influence_path(self, from_palace: str, to_palace: str) -> Dict[str, Any]:
        """
        获取从from宫到to宫的影响路径详情

        Args:
            from_palace: 起点宫位
            to_palace: 终点宫位

        Returns:
            影响路径详情
        """
        path = self.network.get_influence_chain(from_palace, to_palace)

        if not path:
            return {
                "has_path": False,
                "message": f"从 {from_palace} 到 {to_palace} 无影响路径",
            }

        # 计算路径上每段的权重和累积影响
        segments = []
        cumulative_influence = 1.0

        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            weight = self.network.get_edge_weight(source, target)

            cumulative_influence *= weight

            segments.append({
                "from": source,
                "to": target,
                "weight": round(weight, 4),
                "relation": self._get_relation_type(source, target),
                "cumulative_influence": round(cumulative_influence, 4),
            })

        return {
            "has_path": True,
            "path": path,
            "hop_count": len(path) - 1,
            "segments": segments,
            "total_influence": round(cumulative_influence, 4),
            "influence_at_target": round(cumulative_influence * 100, 2),
        }

    def get_social_network_summary(self) -> Dict[str, Any]:
        """
        获取社交网络摘要

        Returns:
            网络摘要信息
        """
        centralities = self.network.get_all_centralities()

        # 找出最有影响力的宫位
        top_palaces = list(centralities.items())[:3]

        # 统计各种关系数量
        relation_counts = {
            "san_fang": len([e for e in self.network.edges if e.relation == RelationType.SAN_FANG]),
            "dui_gong": len([e for e in self.network.edges if e.relation == RelationType.DUI_GONG]),
        }

        # 计算平均连接度
        total_connections = sum(len(n.connections) for n in self.network.nodes.values())
        avg_connections = total_connections / len(self.network.nodes) if self.network.nodes else 0

        return {
            "total_nodes": len(self.network.nodes),
            "total_edges": len(self.network.edges),
            "avg_connections": round(avg_connections, 2),
            "relation_counts": relation_counts,
            "top_influential_palaces": [
                {"palace": p, "centrality": round(c, 4)}
                for p, c in top_palaces
            ],
            "inner_palaces": [p for p in self.PALACE_NAMES if p in self.NEI_GONGS],
            "outer_palaces": [p for p in self.PALACE_NAMES if p not in self.NEI_GONGS],
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "network": self.network.to_dict(),
            "summary": self.get_social_network_summary(),
            "chart_stars": {
                palace: self._get_palace_stars(palace)
                for palace in self.PALACE_NAMES
            },
        }


# ============ Convenience Functions ============

def create_social_network(chart_data: Dict[str, Any]) -> SocialNetworkSimulator:
    """
    创建社交网络模拟器

    Args:
        chart_data: 命盘数据

    Returns:
        SocialNetworkSimulator实例
    """
    return SocialNetworkSimulator(chart_data)


def get_palace_influence(
    chart_data: Dict[str, Any],
    palace: str
) -> Dict[str, Any]:
    """
    获取宫位影响力分析

    Args:
        chart_data: 命盘数据
        palace: 宫位名称

    Returns:
        影响力分析结果
    """
    simulator = SocialNetworkSimulator(chart_data)
    return simulator.get_agent_social_position(palace)


def simulate_event_propagation(
    chart_data: Dict[str, Any],
    source_palace: str,
    event_magnitude: float = 80.0
) -> Dict[str, Any]:
    """
    模拟事件从某宫位传播的影响

    Args:
        chart_data: 命盘数据
        source_palace: 事件源宫位
        event_magnitude: 事件影响力强度

    Returns:
        传播结果
    """
    simulator = SocialNetworkSimulator(chart_data)

    influence_map = simulator.simulate_influence_propagation(
        source=source_palace,
        magnitude=event_magnitude,
    )

    # 按影响力排序
    sorted_influence = sorted(
        influence_map.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "source": source_palace,
        "initial_magnitude": event_magnitude,
        "affected_palaces": len(influence_map),
        "influence_map": influence_map,
        "influence_ranking": [
            {"palace": p, "influence": round(i, 2)}
            for p, i in sorted_influence
        ],
    }


# ============ Exports ============

__all__ = [
    # Data Classes
    "SocialEdge",
    "SocialNode",
    "SocialNetwork",
    # Enums
    "RelationType",
    "PalaceType",
    # Main Class
    "SocialNetworkSimulator",
    # Convenience Functions
    "create_social_network",
    "get_palace_influence",
    "simulate_event_propagation",
]
