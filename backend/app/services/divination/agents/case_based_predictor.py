"""
CaseBasedPredictor - 案例涌现推理引擎

基于案例的预测系统，实现"数字孪生精神"：
1. 找到历史上相似的命盘案例
2. 将命运轨迹时序对齐
3. 统计推断预测概率

核心组件：
- VectorStore: 向量存储（ChromaDB或内存后备）
- TrajectoryMatcher: 轨迹匹配器
- CaseBasedPredictor: 案例推理预测器
"""

import math
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import Counter
from datetime import datetime
import asyncio

from .chart_vectorizer import (
    ChartVectorizer,
    ChartFeatures,
    ChartFeatureQuality,
    LifeEvent,
    LifeTrajectory,
    ChartCase,
    ZHENGYAO_STARS,
    PALACE_NAMES,
    TRANSFORM_TYPES,
)

logger = logging.getLogger(__name__)

# 尝试导入ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available, using in-memory fallback")


@dataclass
class ProbabilisticResult:
    """
    概率推断结果

    包含预测结果和置信度
    """
    event_type: str                          # 事件类型
    prediction: str                           # 预测描述
    probability: float                       # 概率 (0-1)
    confidence: float                        # 置信度 (0-1)
    similar_cases: List[Dict[str, Any]]      # 相似案例
    reasoning: str                           # 推理过程
    year: int                                # 预测年份

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "prediction": self.prediction,
            "probability": round(self.probability, 3),
            "confidence": round(self.confidence, 3),
            "similar_cases": self.similar_cases,
            "reasoning": self.reasoning,
            "year": self.year
        }


@dataclass
class PredictionReport:
    """
    预测报告

    包含多个概率推断结果的汇总
    """
    chart_id: str
    target_year: int
    results: List[ProbabilisticResult]
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "target_year": self.target_year,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
            "metadata": self.metadata
        }


class InMemoryVectorStore:
    """
    内存向量存储（ChromaDB后备方案）

    使用简单的余弦相似度进行向量检索
    """

    def __init__(self, collection_name: str = "chart_cases"):
        self.collection_name = collection_name
        self.cases: Dict[str, ChartCase] = {}
        self._initialized = True

    def add_case(self, case: ChartCase) -> bool:
        """
        添加案例

        Args:
            case: 命盘案例

        Returns:
            bool: 是否成功
        """
        try:
            self.cases[case.case_id] = case
            return True
        except Exception as e:
            logger.error(f"Failed to add case: {e}")
            return False

    def search_similar(
        self,
        query_features: ChartFeatures,
        top_k: int = 10
    ) -> List[Tuple[ChartCase, float]]:
        """
        检索相似案例

        Args:
            query_features: 查询特征
            top_k: 返回数量

        Returns:
            List of (case, similarity_score) tuples
        """
        if not self.cases:
            return []

        query_vector = query_features.to_vector()
        results = []

        for case in self.cases.values():
            case_vector = case.features.to_vector()
            similarity = self._cosine_similarity(query_vector, case_vector)
            results.append((case, similarity))

        # 排序并返回top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def count(self) -> int:
        """返回案例数量"""
        return len(self.cases)

    def clear(self) -> None:
        """清空所有案例"""
        self.cases.clear()


class VectorStore:
    """
    向量存储（ChromaDB或pgvector封装）

    支持ChromaDB、pgvector和内存后备方案
    """

    def __init__(
        self,
        collection_name: str = "chart_cases",
        persist_directory: Optional[str] = None
    ):
        """
        初始化向量存储

        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录（可选）
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._vectorizer = ChartVectorizer()
        self._use_chroma = False
        self._use_pgvector = False

        if CHROMADB_AVAILABLE and persist_directory:
            self._init_chromadb(persist_directory)
        else:
            # Try pgvector as fallback
            if self._init_pgvector():
                logger.info("Using pgvector for vector storage")
            else:
                logger.info("Using in-memory vector store")
                self._store = InMemoryVectorStore(collection_name)

    def _init_pgvector(self) -> bool:
        """Initialize pgvector (VectorDB)"""
        try:
            from app.utils.vector_db import VectorDB
            self._vector_db = VectorDB()
            self._use_pgvector = True
            logger.info("pgvector (VectorDB) initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"pgvector init failed: {e}")
            self._use_pgvector = False
            return False

    def _init_chromadb(self, persist_directory: str) -> None:
        """初始化ChromaDB"""
        try:
            self._client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._use_chroma = True
            logger.info(f"ChromaDB initialized: {persist_directory}")
        except Exception as e:
            logger.warning(f"ChromaDB init failed: {e}, trying pgvector")
            self._use_chroma = False
            if not self._init_pgvector():
                logger.warning("pgvector also failed, using in-memory")
                self._store = InMemoryVectorStore(self.collection_name)

    def add_case(self, case: ChartCase) -> bool:
        """
        添加案例

        Args:
            case: 命盘案例

        Returns:
            bool: 是否成功
        """
        if self._use_chroma:
            return self._add_to_chroma(case)
        elif self._use_pgvector:
            return self._add_to_pgvector(case)
        else:
            return self._store.add_case(case)

    def _add_to_pgvector(self, case: ChartCase) -> bool:
        """添加到pgvector"""
        try:
            vector = case.features.to_vector()
            birth_info = case.metadata.get('birth_info', {})
            chart_data = case.metadata.get('chart_data', {})
            labels = case.metadata.get('labels', [])

            return self._vector_db.insert_chart(
                chart_id=case.chart_id,
                birth_info=birth_info,
                chart_data=chart_data,
                embedding=vector,
                labels=labels
            )
        except Exception as e:
            logger.error(f"Failed to add to pgvector: {e}")
            return False

    def _add_to_chroma(self, case: ChartCase) -> bool:
        """添加到ChromaDB"""
        try:
            vector = case.features.to_vector()
            self._collection.add(
                ids=[case.case_id],
                embeddings=[vector],
                metadatas=[{
                    "chart_id": case.chart_id,
                    "quality": case.features.quality.value,
                    **case.metadata
                }],
                documents=[json.dumps(case.trajectory.to_dict() if case.trajectory else {})]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add to ChromaDB: {e}")
            return False

    def search_similar(
        self,
        query: ChartFeatures,
        top_k: int = 10
    ) -> List[Tuple[ChartCase, float]]:
        """
        检索相似案例

        Args:
            query: 查询特征
            top_k: 返回数量

        Returns:
            List of (case, similarity_score) tuples
        """
        if self._use_chroma:
            return self._search_chroma(query, top_k)
        elif self._use_pgvector:
            return self._search_pgvector(query, top_k)
        else:
            return self._store.search_similar(query, top_k)

    def _search_pgvector(
        self,
        query: ChartFeatures,
        top_k: int
    ) -> List[Tuple[ChartCase, float]]:
        """在pgvector中搜索"""
        try:
            vector = query.to_vector()
            results = self._vector_db.search_similar(
                embedding=vector,
                top_k=top_k,
                threshold=0.7
            )

            cases = []
            for row in results:
                # Reconstruct ChartCase from stored data
                case = ChartCase(
                    case_id=row['chart_id'],
                    chart_id=row['chart_id'],
                    features=query,  # Use query features as approximation
                    trajectory=None,
                    metadata={
                        'birth_info': row.get('birth_info', {}),
                        'chart_data': row.get('chart_data', {}),
                        'labels': row.get('labels', [])
                    }
                )
                cases.append((case, row['similarity']))

            return cases
        except Exception as e:
            logger.error(f"pgvector search failed: {e}")
            return self._store.search_similar(query, top_k)

    def _search_chroma(
        self,
        query: ChartFeatures,
        top_k: int
    ) -> List[Tuple[ChartCase, float]]:
        """在ChromaDB中搜索"""
        try:
            results = self._collection.query(
                query_embeddings=[query.to_vector()],
                n_results=top_k
            )

            cases = []
            for i, case_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                similarity = 1.0 - distance  # 转换距离为相似度

                # 获取案例数据
                metadata = results["metadatas"][0][i]
                chart_id = metadata.get("chart_id", case_id)

                # 重建ChartCase（简化版）
                case = ChartCase(
                    case_id=case_id,
                    chart_id=chart_id,
                    features=query,  # 使用查询特征作为近似
                    trajectory=None,
                    metadata=metadata
                )
                cases.append((case, similarity))

            return cases
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return self._store.search_similar(query, top_k)

    def count(self) -> int:
        """返回案例数量"""
        if self._use_chroma:
            return self._collection.count()
        elif self._use_pgvector:
            return self._vector_db.count()
        else:
            return self._store.count()

    def clear(self) -> None:
        """清空所有案例"""
        if self._use_chroma:
            try:
                self._client.delete_collection(self.collection_name)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                logger.error(f"Failed to clear ChromaDB: {e}")
        elif self._use_pgvector:
            try:
                # pgvector doesn't support truncate, so we delete all records
                cur = self._vector_db.conn.cursor()
                cur.execute("DELETE FROM chart_cases")
                cur.close()
                logger.info("Cleared all charts from pgvector")
            except Exception as e:
                logger.error(f"Failed to clear pgvector: {e}")
        else:
            self._store.clear()


class TrajectoryMatcher:
    """
    轨迹匹配器

    将目标命盘与案例命盘的命运轨迹按大限对齐
    """

    # 大限参数（默认值，可被chart中的五行局覆盖）
    DEFAULT_DALIAN_START_AGE = 15  # 默认大限起始年龄
    DEFAULT_DALIAN_YEARS = 10      # 每个大限的年数

    def __init__(self):
        self._vectorizer = ChartVectorizer()

    def calculate_dalian_index(
        self,
        age: int,
        start_age: int = None
    ) -> int:
        """
        计算年龄对应的大限索引

        Args:
            age: 年龄
            start_age: 大限起始年龄（默认15）

        Returns:
            int: 大限索引（0开始）
        """
        if start_age is None:
            start_age = self.DEFAULT_DALIAN_START_AGE

        if age < start_age:
            return -1  # 尚未进入大限

        return (age - start_age) // self.DEFAULT_DALIAN_YEARS

    def align_by_dalian_index(
        self,
        case: ChartCase,
        target_birth_year: int,
        target_features: ChartFeatures,
        dalian_start_age: int = None
    ) -> Dict[int, List[LifeEvent]]:
        """
        按大限索引对齐命运阶段

        这是正确的时序对齐方式：将线性年龄转换为大限索引后对齐。
        大限索引 = (年龄 - 大限起始年龄) / 大限年限

        Args:
            case: 案例命盘
            target_birth_year: 目标出生年份
            target_features: 目标命盘特征
            dalian_start_age: 大限起始年龄（默认15）

        Returns:
            Dict: {大限索引: [LifeEvent列表]}
        """
        if not case.trajectory:
            return {}

        if dalian_start_age is None:
            dalian_start_age = self.DEFAULT_DALIAN_START_AGE

        aligned_events: Dict[int, List[LifeEvent]] = {}

        # 对齐每个事件：将案例事件的年龄转换为大限索引
        # 案例事件的大限索引 = (事件年龄 - 大限起始年龄) // 10
        for event in case.trajectory.events:
            event_dalian_index = self.calculate_dalian_index(event.age, dalian_start_age)
            if event_dalian_index < 0:
                continue  # 跳过尚未进入大限的事件

            if event_dalian_index not in aligned_events:
                aligned_events[event_dalian_index] = []
            aligned_events[event_dalian_index].append(event)

        return aligned_events

    def align_by_age(
        self,
        case: ChartCase,
        target_birth_year: int,
        target_features: ChartFeatures
    ) -> Dict[int, List[LifeEvent]]:
        """
        按年龄对齐命运阶段（已废弃，请使用 align_by_dalian_index）

        Args:
            case: 案例命盘
            target_birth_year: 目标出生年份
            target_features: 目标命盘特征

        Returns:
            Dict: {年龄: [LifeEvent列表]}
        """
        # 兼容旧代码，实际调用大限对齐
        return self.align_by_dalian_index(case, target_birth_year, target_features)

    def compute_trajectory_similarity(
        self,
        trajectory1: LifeTrajectory,
        trajectory2: LifeTrajectory,
        age_range: Tuple[int, int] = (20, 60)
    ) -> float:
        """
        计算两条轨迹的相似度

        Args:
            trajectory1: 第一条轨迹
            trajectory2: 第二条轨迹
            age_range: 比较的年龄范围

        Returns:
            float: 相似度 (0-1)
        """
        start_age, end_age = age_range

        # 统计事件类型分布
        events1 = [e for e in trajectory1.events if start_age <= e.age <= end_age]
        events2 = [e for e in trajectory2.events if start_age <= e.age <= end_age]

        if not events1 or not events2:
            return 0.0

        types1 = Counter(e.event_type for e in events1)
        types2 = Counter(e.event_type for e in events2)

        # 计算Jaccard相似度
        all_types = set(types1.keys()) | set(types2.keys())
        if not all_types:
            return 0.0

        intersection = sum(min(types1.get(t, 0), types2.get(t, 0)) for t in all_types)
        union = sum(max(types1.get(t, 0), types2.get(t, 0)) for t in all_types)

        return intersection / union if union > 0 else 0.0


class CaseBasedPredictor:
    """
    案例推理预测器

    基于相似命盘案例进行概率推断预测
    """

    def __init__(
        self,
        collection_name: str = "chart_cases",
        persist_directory: Optional[str] = None
    ):
        """
        初始化预测器

        Args:
            collection_name: 案例集合名称
            persist_directory: 向量存储持久化目录
        """
        self._vectorizer = ChartVectorizer()
        self._vector_store = VectorStore(collection_name, persist_directory)
        self._trajectory_matcher = TrajectoryMatcher()

    def load_from_json_file(self, file_path: str) -> int:
        """
        从JSON文件加载命盘案例

        Args:
            file_path: JSON文件路径

        Returns:
            int: 加载的案例数量
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            cases = data.get('cases', []) if isinstance(data, dict) else data
            count = 0

            for case_data in cases:
                case = self._parse_case_from_dict(case_data)
                if case:
                    self._vector_store.add_case(case)
                    count += 1

            logger.info(f"从 {file_path} 加载了 {count} 个案例")
            return count
        except Exception as e:
            logger.error(f"加载案例失败: {e}")
            return 0

    def load_from_directory(self, directory: str, pattern: str = "*.json") -> int:
        """
        从目录加载所有命盘案例

        Args:
            directory: 目录路径
            pattern: 文件匹配模式

        Returns:
            int: 加载的案例总数
        """
        total = 0
        path = Path(directory)

        if not path.exists():
            logger.warning(f"案例目录不存在: {directory}")
            return 0

        for json_file in path.glob(pattern):
            count = self.load_from_json_file(str(json_file))
            total += count

        logger.info(f"从目录 {directory} 共加载了 {total} 个案例")
        return total

    def auto_load_seed_cases(self) -> int:
        """
        自动从默认种子数据目录加载案例

        Returns:
            int: 加载的案例数量
        """
        # 尝试多个可能的种子数据路径
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "data_source" / "cases" / "seed",
            Path(__file__).parent.parent.parent.parent / "data_source" / "cases",
            Path("data_source/cases/seed"),
        ]

        for seed_path in possible_paths:
            if seed_path.exists():
                return self.load_from_directory(str(seed_path))

        logger.warning("未找到种子数据目录，案例库为空")
        return 0

    def _parse_case_from_dict(self, case_data: Dict[str, Any]) -> Optional[ChartCase]:
        """
        从字典数据解析为ChartCase对象

        Args:
            case_data: 案例数据字典

        Returns:
            Optional[ChartCase]: 解析后的案例对象，解析失败返回None
        """
        try:
            case_id = case_data.get('case_id', f"case_{datetime.utcnow().timestamp()}")

            # 提取chart数据
            chart = case_data.get('chart', case_data.get('natal_chart', {}))
            if not chart:
                # 尝试从palaces构建chart
                palaces = case_data.get('palaces', {})
                chart = {'palaces': palaces, 'stars': {}}

            # 提取特征向量
            features = self._vectorizer.extract(chart)

            # 提取命运轨迹
            trajectory_data = case_data.get('life_trajectory', case_data.get('fate_trajectory', []))
            trajectory = None
            if trajectory_data:
                events = []
                # 获取出生年份用于计算event.year
                birth_year = chart.get('birth_info', {}).get('year', 1990) if isinstance(chart, dict) else 1990

                for event_data in trajectory_data:
                    if isinstance(event_data, dict):
                        # 处理 outcome -> significance 的映射
                        outcome = event_data.get('outcome', '平')
                        significance = 0.5
                        if outcome in ['吉', '大吉', '顺利', '发展', '发达']:
                            significance = 0.8
                        elif outcome in ['凶', '大凶', '挫折', '失败']:
                            significance = 0.2
                        else:
                            significance = 0.5

                        # 处理 age 字段（可能是字符串如"幼年(1-15岁)"或整数）
                        age_value = event_data.get('age', 0)
                        if isinstance(age_value, str):
                            # 尝试从字符串中提取数字
                            import re
                            numbers = re.findall(r'\d+', age_value)
                            if numbers:
                                age_value = int(numbers[0])
                            else:
                                # 尝试解析中文年龄描述
                                if '幼年' in age_value or '童年' in age_value:
                                    age_value = 10
                                elif '少年' in age_value:
                                    age_value = 17
                                elif '青年' in age_value:
                                    age_value = 25
                                elif '中年' in age_value:
                                    age_value = 40
                                elif '老年' in age_value:
                                    age_value = 60
                                else:
                                    age_value = 30
                        else:
                            age_value = int(age_value) if age_value else 0

                        # 计算 year: birth_year + age
                        year_value = event_data.get('year', 0)
                        if not year_value or year_value == 0:
                            year_value = birth_year + age_value

                        # 处理 event_type: 优先使用 type/event_type，否则使用 period
                        event_type = event_data.get('type', event_data.get('event_type', None))
                        if not event_type:
                            period = event_data.get('period', '')
                            # 从period推断事件类型
                            if any(k in period for k in ['学业', '求学', '学习']):
                                event_type = '学业'
                            elif any(k in period for k in ['事业', '工作', '创业', '职业']):
                                event_type = '事业'
                            elif any(k in period for k in ['财运', '财富', '金钱', '投资']):
                                event_type = '财运'
                            elif any(k in period for k in ['感情', '婚姻', '恋爱', '家庭', '子女']):
                                event_type = '感情'
                            elif any(k in period for k in ['健康', '身体', '疾病']):
                                event_type = '健康'
                            else:
                                event_type = '其他'

                        # 处理 description: 优先使用 description/desc，否则使用 event
                        description = event_data.get('description', event_data.get('desc', event_data.get('event', '')))

                        event = LifeEvent(
                            age=age_value,
                            year=year_value,
                            event_type=event_type,
                            description=description,
                            significance=significance,
                            palace=event_data.get('palace', '')
                        )
                        events.append(event)

                if events:
                    trajectory = LifeTrajectory(
                        chart_id=case_id,
                        birth_year=birth_year,
                        events=events
                    )

            return ChartCase(
                case_id=case_id,
                chart_id=case_id,  # 使用case_id作为chart_id
                features=features,
                trajectory=trajectory,
                metadata=case_data.get('metadata', {
                    'source': case_data.get('source', 'unknown'),
                    'type': case_data.get('type', 'unknown')
                })
            )
        except Exception as e:
            logger.error(f"解析案例失败: {e}")
            return None

    async def predict(
        self,
        chart: Dict[str, Any],
        target_year: int,
        event_types: Optional[List[str]] = None
    ) -> PredictionReport:
        """
        预测指定年份的事件

        Args:
            chart: 目标命盘
            target_year: 目标年份
            event_types: 要预测的事件类型列表（默认：财运、事业、感情、健康）

        Returns:
            PredictionReport: 预测报告
        """
        if event_types is None:
            event_types = ["财运", "事业", "感情", "健康"]

        chart_id = str(chart.get("birth_info", {}).get("year", "")) + "_" + str(id(chart))

        # 1. 提取特征
        features = self._vectorizer.extract(chart)

        # 2. 检索相似命盘
        similar_cases = self._vector_store.search_similar(features, top_k=10)

        if not similar_cases:
            return self._create_empty_report(chart_id, target_year, "暂无相似案例")

        # 3. 时序对齐并推断
        # 提取出生年份（支持多种格式）
        birth_info = chart.get("birth_info", {})
        birth_year = birth_info.get("year")
        if not birth_year and "birth_date" in birth_info:
            # 从 birth_date 提取年份，如 "1988-04-18" -> 1988
            try:
                birth_year = int(birth_info["birth_date"].split("-")[0])
            except (ValueError, IndexError):
                birth_year = 1990
        if not birth_year:
            birth_year = 1990
        target_age = target_year - birth_year

        results = []
        for event_type in event_types:
            result = await self._predict_event_type(
                event_type,
                target_age,
                target_year,
                similar_cases,
                birth_year,
                features
            )
            if result:
                results.append(result)

        # 4. 生成汇总
        summary = self._generate_summary(results, len(similar_cases))

        # 计算目标的大限索引
        dalian_start_age = TrajectoryMatcher.DEFAULT_DALIAN_START_AGE
        target_dalian_index = (target_age - dalian_start_age) // TrajectoryMatcher.DEFAULT_DALIAN_YEARS if target_age >= dalian_start_age else -1
        dalian_age_range = f"第{target_dalian_index + 1}大限" if target_dalian_index >= 0 else "未入大限"

        return PredictionReport(
            chart_id=chart_id,
            target_year=target_year,
            results=results,
            summary=summary,
            metadata={
                "case_count": self._vector_store.count(),
                "similar_case_count": len(similar_cases),
                "target_age": target_age,
                "target_dalian_index": target_dalian_index,
                "target_dalian_label": dalian_age_range
            }
        )

    async def _predict_event_type(
        self,
        event_type: str,
        target_age: int,
        target_year: int,
        similar_cases: List[Tuple[ChartCase, float]],
        birth_year: int,
        target_features: ChartFeatures,
        dalian_start_age: int = None
    ) -> Optional[ProbabilisticResult]:
        """
        预测特定类型的事件

        Args:
            event_type: 事件类型
            target_age: 目标年龄
            target_year: 目标年份
            similar_cases: 相似案例列表
            birth_year: 出生年份
            target_features: 目标命盘特征
            dalian_start_age: 大限起始年龄（默认15）

        Returns:
            ProbabilisticResult or None
        """
        # 使用大限索引（默认15岁起）
        if dalian_start_age is None:
            dalian_start_age = TrajectoryMatcher.DEFAULT_DALIAN_START_AGE

        # 计算目标的大限索引
        target_dalian_index = self._trajectory_matcher.calculate_dalian_index(
            target_age, dalian_start_age
        )

        aligned_events: List[Tuple[LifeEvent, float]] = []

        for case, similarity in similar_cases:
            if not case.trajectory:
                continue

            # 对齐轨迹（按大限索引）
            aligned = self._trajectory_matcher.align_by_dalian_index(
                case, birth_year, target_features, dalian_start_age
            )

            # 收集目标大限索引的事件（支持±1大限容差，即±10年）
            dalian_tolerance = 1
            for dalian_offset in range(-dalian_tolerance, dalian_tolerance + 1):
                check_dalian_index = target_dalian_index + dalian_offset
                if check_dalian_index < 0:
                    continue
                events_at_dalian = aligned.get(check_dalian_index, [])
                for event in events_at_dalian:
                    if event.event_type == event_type or event_type in event.description:
                        # 添加大限差距作为衰减因子（±1大限内衰减较小）
                        distance_penalty = 1.0 - (abs(dalian_offset) * 0.2)
                        adjusted_similarity = similarity * distance_penalty
                        aligned_events.append((event, adjusted_similarity))

        if not aligned_events:
            return None

        # 计算概率
        probability, reasoning = self._calculate_probability(
            aligned_events, event_type
        )

        # 计算置信度
        confidence = self._calculate_confidence(
            len(aligned_events),
            sum(s for _, s in aligned_events) / len(aligned_events)
        )

        # 相似案例信息
        similar_case_info = [
            {
                "case_id": case.case_id,
                "chart_id": case.chart_id,
                "similarity": round(sim, 3),
                "event": event.to_dict()
            }
            for (event, sim), (case, _) in zip(aligned_events[:5], similar_cases[:5])
        ]

        # 生成预测描述
        prediction = self._generate_prediction(event_type, probability, reasoning)

        return ProbabilisticResult(
            event_type=event_type,
            prediction=prediction,
            probability=probability,
            confidence=confidence,
            similar_cases=similar_case_info,
            reasoning=reasoning,
            year=target_year
        )

    def _calculate_probability(
        self,
        events: List[Tuple[LifeEvent, float]],
        event_type: str
    ) -> Tuple[float, str]:
        """
        计算事件发生的概率

        Args:
            events: 事件列表（事件，加权相似度）
            event_type: 事件类型

        Returns:
            Tuple[概率, 推理描述]
        """
        if not events:
            return 0.0, "No data"

        # 统计事件的显著性分布
        significance_sum = sum(e.significance * sim for e, sim in events)
        avg_significance = significance_sum / len(events)

        # 基础概率
        base_prob = min(len(events) / 10.0, 1.0) * 0.6

        # 加权调整
        weighted_prob = base_prob + avg_significance * 0.4

        # 限制在0-1范围
        probability = max(0.0, min(1.0, weighted_prob))

        # 推理描述
        reasoning = (
            f"Based on {len(events)} similar cases with average significance "
            f"{avg_significance:.2f}, the probability is calculated using "
            f"weighted statistical inference."
        )

        return probability, reasoning

    def _calculate_confidence(
        self,
        event_count: int,
        avg_similarity: float
    ) -> float:
        """
        计算置信度

        Args:
            event_count: 事件数量
            avg_similarity: 平均相似度

        Returns:
            float: 置信度 (0-1)
        """
        # 最小置信度（信息不完整时的基础不确定性）
        MIN_CONFIDENCE = 0.3

        # 无案例情况：返回0.3，反映缺乏案例信息
        if event_count == 0:
            return MIN_CONFIDENCE

        # 样本数量因子 (0-0.4)
        count_factor = min(event_count / 5.0, 1.0) * 0.4

        # 相似度因子 (0-0.6)
        similarity_factor = avg_similarity * 0.6

        # 有案例但相似度低：0.3 + 低相似度调整
        if avg_similarity < 0.5:
            # 低相似度时降低置信度，但仍不低于0.3
            adjusted_confidence = MIN_CONFIDENCE + similarity_factor * 0.4
            return max(MIN_CONFIDENCE, adjusted_confidence)

        # 有案例且相似度高：正常计算
        confidence = count_factor + similarity_factor
        return max(MIN_CONFIDENCE, min(confidence, 1.0))

    def _generate_prediction(
        self,
        event_type: str,
        probability: float,
        reasoning: str
    ) -> str:
        """
        生成预测描述

        Args:
            event_type: 事件类型
            probability: 概率
            reasoning: 推理过程

        Returns:
            str: 预测描述
        """
        level = ""
        if probability >= 0.7:
            level = "大概率"
        elif probability >= 0.5:
            level = "较可能"
        elif probability >= 0.3:
            level = "可能"
        else:
            level = "小概率"

        event_descriptions = {
            "财运": "有财运机遇",
            "事业": "事业有发展",
            "感情": "感情有变化",
            "健康": "健康需注意"
        }

        desc = event_descriptions.get(event_type, event_type)
        return f"{level}{desc}"

    def _generate_summary(
        self,
        results: List[ProbabilisticResult],
        total_cases: int
    ) -> str:
        """
        生成预测汇总

        Args:
            results: 预测结果列表
            total_cases: 相似案例总数

        Returns:
            str: 汇总描述
        """
        if not results:
            return "缺乏相似案例，无法做出有效预测"

        high_prob = [r for r in results if r.probability >= 0.6]
        medium_prob = [r for r in results if 0.4 <= r.probability < 0.6]

        summary_parts = []

        if high_prob:
            events = ", ".join(r.event_type for r in high_prob)
            summary_parts.append(f"重点关注：{events}")

        if medium_prob:
            events = ", ".join(r.event_type for r in medium_prob)
            summary_parts.append(f"需要留意：{events}")

        summary_parts.append(f"参考案例数：{total_cases}")

        return "；".join(summary_parts)

    def _create_empty_report(
        self,
        chart_id: str,
        target_year: int,
        reason: str
    ) -> PredictionReport:
        """创建空报告（优雅降级）"""
        return PredictionReport(
            chart_id=chart_id,
            target_year=target_year,
            results=[],
            summary=f"无法预测：{reason}",
            metadata={
                "error": True,
                "confidence": 0.3,  # 无案例时使用0.3，反映信息不完整
                "reason": reason
            }
        )

    def add_case(
        self,
        chart: Dict[str, Any],
        trajectory: Optional[LifeTrajectory] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加案例到知识库

        Args:
            chart: 命盘数据
            trajectory: 命运轨迹（可选）
            metadata: 额外元数据（可选）

        Returns:
            bool: 是否成功
        """
        try:
            features = self._vectorizer.extract(chart)
            case_id = f"case_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

            case = ChartCase(
                case_id=case_id,
                chart_id=chart.get("birth_info", {}).get("year", ""),
                features=features,
                trajectory=trajectory,
                metadata=metadata or {}
            )

            return self._vector_store.add_case(case)
        except Exception as e:
            logger.error(f"Failed to add case: {e}")
            return False

    def load_cases_from_directory(
        self,
        directory: str
    ) -> int:
        """
        从目录加载案例

        Args:
            directory: 案例目录路径

        Returns:
            int: 加载的案例数量
        """
        loaded = 0
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.warning(f"Case directory not found: {directory}")
            return 0

        for file_path in dir_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 解析案例数据
                if "cases" in data:
                    for case_data in data["cases"]:
                        self._load_single_case(case_data)
                        loaded += 1
                elif "chart" in data:
                    self._load_single_case(data)
                    loaded += 1

            except Exception as e:
                logger.error(f"Failed to load case from {file_path}: {e}")

        return loaded

    def _load_single_case(self, case_data: Dict[str, Any]) -> bool:
        """加载单个案例"""
        try:
            chart = case_data.get("chart", {})
            trajectory_data = case_data.get("trajectory")
            metadata = case_data.get("metadata", {})

            features = self._vectorizer.extract(chart)

            trajectory = None
            if trajectory_data:
                events = []
                for event_data in trajectory_data.get("events", []):
                    event = LifeEvent(
                        age=event_data.get("age", 0),
                        year=event_data.get("year", 0),
                        event_type=event_data.get("event_type", ""),
                        description=event_data.get("description", ""),
                        significance=event_data.get("significance", 0.5),
                        palace=event_data.get("palace", "")
                    )
                    events.append(event)

                trajectory = LifeTrajectory(
                    chart_id=case_data.get("case_id", ""),
                    birth_year=trajectory_data.get("birth_year", 1990),
                    events=events
                )

            case = ChartCase(
                case_id=case_data.get("case_id", f"case_{id(case_data)}"),
                chart_id=case_data.get("chart_id", ""),
                features=features,
                trajectory=trajectory,
                metadata=metadata
            )

            return self._vector_store.add_case(case)
        except Exception as e:
            logger.error(f"Failed to load single case: {e}")
            return False


# 便捷函数
async def predict_from_chart(
    chart: Dict[str, Any],
    target_year: int,
    event_types: Optional[List[str]] = None,
    collection_name: str = "chart_cases"
) -> PredictionReport:
    """
    从命盘数据进行预测

    Args:
        chart: 命盘数据
        target_year: 目标年份
        event_types: 事件类型列表
        collection_name: 案例集合名称

    Returns:
        PredictionReport: 预测报告
    """
    predictor = CaseBasedPredictor(collection_name)
    # 加载种子案例库
    predictor.auto_load_seed_cases()
    return await predictor.predict(chart, target_year, event_types)


def create_predictor(
    collection_name: str = "chart_cases",
    persist_directory: Optional[str] = None
) -> CaseBasedPredictor:
    """
    创建预测器实例

    Args:
        collection_name: 案例集合名称
        persist_directory: 持久化目录

    Returns:
        CaseBasedPredictor: 预测器实例
    """
    return CaseBasedPredictor(collection_name, persist_directory)
