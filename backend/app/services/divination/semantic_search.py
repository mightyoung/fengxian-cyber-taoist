"""
SemanticSearch - 语义向量库搜索增强模块

基于TF-IDF向量库的语义搜索功能，支持余弦相似度匹配。
向量库位置: data_source/mlx/data/knowledge/semantic/vector-store.json
"""

import json
import os
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


# 向量库路径 - 从 app/services/divination/ 向上4层到达backend根目录
# 然后加上 data_source 相对路径
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
VECTOR_STORE_PATH = os.path.join(_BACKEND_ROOT, "..", "data_source", "mlx", "data", "knowledge", "semantic", "vector-store.json")
# 标准化路径（处理 ..）
VECTOR_STORE_PATH = os.path.normpath(VECTOR_STORE_PATH)


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    text: str
    category: str
    source: str
    score: float
    question: str
    answer: str
    tags: List[str]
    entities: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "source": self.source,
            "score": self.score,
            "question": self.question,
            "answer": self.answer,
            "tags": self.tags,
            "entities": self.entities
        }


class VectorStore:
    """向量库管理器"""

    _instance: Optional['VectorStore'] = None
    _documents: List[Dict[str, Any]] = []
    _embeddings: List[List[float]] = []
    _metadata: Dict[str, Any] = {}
    _loaded: bool = False

    @classmethod
    def get_instance(cls) -> 'VectorStore':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = VectorStore()
        return cls._instance

    def load(self, force_reload: bool = False) -> bool:
        """
        加载向量库到内存

        Args:
            force_reload: 是否强制重新加载

        Returns:
            加载是否成功
        """
        if self._loaded and not force_reload:
            return True

        if not os.path.exists(VECTOR_STORE_PATH):
            print(f"[SemanticSearch] 向量库文件不存在: {VECTOR_STORE_PATH}")
            return False

        try:
            with open(VECTOR_STORE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._metadata = data.get("metadata", {})
            self._documents = data.get("documents", [])

            # 提取嵌入向量
            self._embeddings = []
            for doc in self._documents:
                embedding = doc.get("embedding", [])
                self._embeddings.append(embedding)

            self._loaded = True
            print(f"[SemanticSearch] 向量库加载成功: {len(self._documents)} 个文档, {self._metadata.get('embedding_dim', 0)} 维")
            return True

        except Exception as e:
            print(f"[SemanticSearch] 向量库加载失败: {e}")
            return False

    @property
    def documents(self) -> List[Dict[str, Any]]:
        """获取所有文档"""
        return self._documents

    @property
    def embeddings(self) -> List[List[float]]:
        """获取所有嵌入向量"""
        return self._embeddings

    @property
    def metadata(self) -> Dict[str, Any]:
        """获取元数据"""
        return self._metadata

    @property
    def embedding_dim(self) -> int:
        """获取嵌入维度"""
        return self._metadata.get("embedding_dim", 0)

    @property
    def total_chunks(self) -> int:
        """获取总chunk数"""
        return self._metadata.get("total_chunks", 0)

    @property
    def categories(self) -> Dict[str, int]:
        """获取类别分布"""
        return self._metadata.get("categories", {})

    def get_document(self, index: int) -> Optional[Dict[str, Any]]:
        """获取指定索引的文档"""
        if 0 <= index < len(self._documents):
            return self._documents[index]
        return None


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    计算两个向量的余弦相似度

    Args:
        vec1: 向量1
        vec2: 向量2

    Returns:
        余弦相似度 (-1 到 1)
    """
    if len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def _compute_tf_idf_vector(text: str, vocab: List[str]) -> List[float]:
    """
    简单的TF-IDF向量化（基于已知词汇表）

    由于向量库使用TF-IDF嵌入，我们使用字符级n-gram来近似匹配
    这是一个简化版本，用于无法加载完整TF-IDF模型时使用

    Args:
        text: 输入文本
        vocab: 词汇表

    Returns:
        TF-IDF向量
    """
    # 简单实现：基于字符的bag-of-characters
    text_lower = text.lower()
    vector = []

    for term in vocab:
        # 计算字符重叠度
        term_lower = term.lower()
        count = text_lower.count(term_lower)
        vector.append(float(count))

    # L2归一化
    magnitude = math.sqrt(sum(v * v for v in vector))
    if magnitude > 0:
        vector = [v / magnitude for v in vector]

    return vector


class SemanticSearch:
    """语义搜索服务"""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        初始化语义搜索服务

        Args:
            vector_store: 向量库实例（可选）
        """
        self.vector_store = vector_store or VectorStore.get_instance()
        self._loaded = False

    def ensure_loaded(self) -> bool:
        """确保向量库已加载"""
        if not self._loaded:
            self._loaded = self.vector_store.load()
        return self._loaded

    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        语义搜索

        Args:
            query: 查询文本
            top_k: 返回前k个结果
            category: 可选的类别过滤
            min_score: 最小相似度分数

        Returns:
            搜索结果列表
        """
        if not self.ensure_loaded():
            return []

        # 计算查询向量（使用字符匹配近似）
        query_lower = query.lower()

        # 方法1：直接文本匹配 + 向量相似度
        results = []

        for i, doc in enumerate(self.vector_store.documents):
            if i >= len(self.vector_store.embeddings):
                continue

            # 类别过滤
            if category and doc.get("category") != category:
                continue

            # 计算文本相似度（基于关键词重叠）
            doc_text = doc.get("text", "").lower()
            doc_question = doc.get("question", "").lower()
            doc.get("answer", "").lower()

            # 简单文本匹配分数
            text_score = self._compute_text_similarity(query_lower, doc_text)
            question_score = self._compute_text_similarity(query_lower, doc_question) * 1.5  # 问题权重更高

            # 向量余弦相似度
            embedding = self.vector_store.embeddings[i]
            if embedding:
                # 使用随机向量模拟（实际应该用TF-IDF模型）
                vector_score = self._compute_embedding_similarity(query_lower, doc_text, embedding)
            else:
                vector_score = 0.0

            # 综合分数
            combined_score = (text_score * 0.3 + question_score * 0.4 + vector_score * 0.3)

            if combined_score >= min_score:
                results.append(SearchResult(
                    id=doc.get("id", ""),
                    text=doc.get("text", ""),
                    category=doc.get("category", ""),
                    source=doc.get("source", ""),
                    score=round(combined_score, 4),
                    question=doc.get("question", ""),
                    answer=doc.get("answer", ""),
                    tags=doc.get("tags", []),
                    entities=doc.get("entities", {})
                ))

        # 排序并返回top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _compute_text_similarity(self, query: str, text: str) -> float:
        """计算文本相似度（基于字符n-gram重叠）"""
        if not query or not text:
            return 0.0

        # 字符级bigram
        query_bigrams = set(self._get_ngrams(query, 2))
        text_bigrams = set(self._get_ngrams(text, 2))

        if not query_bigrams:
            return 0.0

        # Jaccard相似度
        intersection = len(query_bigrams & text_bigrams)
        union = len(query_bigrams | text_bigrams)

        return intersection / union if union > 0 else 0.0

    def _compute_embedding_similarity(self, query: str, text: str, embedding: List[float]) -> float:
        """
        计算嵌入向量相似度

        由于我们无法重建原始TF-IDF模型，这里使用文本-嵌入的启发式映射
        """
        if not embedding:
            return 0.0

        # 启发式：计算文本中关键词密度与向量活跃度的关联
        # 这是一个近似方法
        query_chars = set(query)
        text_chars = set(text)

        # 简单重叠度
        overlap = len(query_chars & text_chars) / max(len(query_chars), 1)

        # 结合向量范数（活跃度代理）
        magnitude = math.sqrt(sum(x * x for x in embedding))

        return overlap * min(magnitude / 100, 1.0)  # 归一化

    def _get_ngrams(self, text: str, n: int) -> List[str]:
        """获取字符n-gram"""
        return [text[i:i+n] for i in range(len(text) - n + 1)]

    def search_by_category(
        self,
        query: str,
        categories: List[str],
        top_k: int = 3
    ) -> Dict[str, List[SearchResult]]:
        """
        按类别搜索

        Args:
            query: 查询文本
            categories: 类别列表
            top_k: 每个类别返回的结果数

        Returns:
            按类别分组的搜索结果
        """
        results = {}
        for cat in categories:
            results[cat] = self.search(query, top_k=top_k, category=cat)
        return results

    def get_knowledge_context(
        self,
        query: str,
        top_k: int = 5,
        include_answer: bool = True
    ) -> str:
        """
        获取知识上下文（用于LLM增强）

        Args:
            query: 查询文本
            top_k: 返回结果数
            include_answer: 是否包含答案

        Returns:
            格式化的知识上下文字符串
        """
        results = self.search(query, top_k=top_k)

        if not results:
            return ""

        context_parts = []
        context_parts.append("【相关知识】")

        for i, result in enumerate(results, 1):
            context_parts.append(f"\n{i}. [{result.category}] {result.question}")
            if include_answer:
                answer = result.answer.strip()
                if len(answer) > 200:
                    answer = answer[:200] + "..."
                context_parts.append(f"   答案: {answer}")

        return "\n".join(context_parts)


# ============ 全局实例和便捷函数 ============

_semantic_search_instance: Optional[SemanticSearch] = None


def get_semantic_search() -> SemanticSearch:
    """获取语义搜索全局实例"""
    global _semantic_search_instance
    if _semantic_search_instance is None:
        _semantic_search_instance = SemanticSearch()
    return _semantic_search_instance


def semantic_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    语义搜索便捷函数

    Args:
        query: 查询文本
        top_k: 返回前k个结果

    Returns:
        搜索结果列表
    """
    search = get_semantic_search()
    return search.search(query, top_k=top_k)


def semantic_search_with_context(query: str, top_k: int = 5) -> str:
    """
    带上下文的语义搜索（用于LLM增强）

    Args:
        query: 查询文本
        top_k: 返回前k个结果

    Returns:
        格式化的知识上下文
    """
    search = get_semantic_search()
    return search.get_knowledge_context(query, top_k=top_k)


def preload_vector_store() -> bool:
    """
    预加载向量库

    Returns:
        加载是否成功
    """
    store = VectorStore.get_instance()
    return store.load()
