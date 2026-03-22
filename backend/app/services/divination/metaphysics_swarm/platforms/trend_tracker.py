"""
TrendTracker - 趋势追踪器

追踪社交媒体上的话题趋势、情感变化和群体共识。

依赖:
- platforms/social_media.py: Post
- social_interaction.py: SocialEvent
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import statistics
import uuid

from app.services.divination.metaphysics_swarm.platforms.social_media import Post
from app.services.divination.metaphysics_swarm.social_interaction import SocialEvent


# ============ 话题分类 ============

TOPIC_CATEGORIES = {
    "事业发展方向": "事业",
    "财务投资策略": "财运",
    "人际关系处理": "感情",
    "健康生活方式": "健康",
    "学业进修计划": "学业",
    "家庭责任分担": "感情",
    "退休养老安排": "财运",
    "创业创新机遇": "事业",
    "社会责任担当": "事业",
    "心理健康维护": "健康",
}


# ============ 数据模型 ============

@dataclass
class Topic:
    """话题数据模型"""
    name: str
    category: str  # 事业/财运/感情/健康/学业
    mention_count: int = 0
    sentiment_avg: float = 0.0
    trending_score: float = 0.0
    first_mentioned: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    related_palaces: List[str] = field(default_factory=list)

    def update_from_posts(self, posts: List[Post]) -> None:
        """从帖子列表更新话题数据"""
        related_posts = [p for p in posts if p.topic == self.name]
        if not related_posts:
            return

        self.mention_count = len(related_posts)
        self.sentiment_avg = sum(p.sentiment for p in related_posts) / len(related_posts)
        self.related_palaces = list(set(p.author_palace for p in related_posts))
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "category": self.category,
            "mention_count": self.mention_count,
            "sentiment_avg": round(self.sentiment_avg, 3),
            "trending_score": round(self.trending_score, 3),
            "first_mentioned": self.first_mentioned.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "related_palaces": self.related_palaces,
        }


@dataclass
class SentimentDataPoint:
    """情感数据点"""
    timestamp: datetime
    round_num: int
    overall_sentiment: float
    topic_sentiments: Dict[str, float]  # {topic: sentiment}
    palace_sentiments: Dict[str, float]  # {palace: sentiment}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "round_num": self.round_num,
            "overall_sentiment": round(self.overall_sentiment, 3),
            "topic_sentiments": {k: round(v, 3) for k, v in self.topic_sentiments.items()},
            "palace_sentiments": {k: round(v, 3) for k, v in self.palace_sentiments.items()},
        }


@dataclass
class OpinionCluster:
    """观点聚类"""
    cluster_id: str
    dominant_topic: str
    dominant_sentiment: float
    participating_palaces: List[str]
    strength: float  # 0-1
    evolution: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "cluster_id": self.cluster_id,
            "dominant_topic": self.dominant_topic,
            "dominant_sentiment": round(self.dominant_sentiment, 3),
            "participating_palaces": self.participating_palaces,
            "strength": round(self.strength, 3),
            "evolution": self.evolution,
        }


@dataclass
class SentimentShift:
    """情感变化"""
    direction: str  # "positive" / "negative"
    magnitude: float
    topic: str
    before_avg: float = 0.0
    after_avg: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "direction": self.direction,
            "magnitude": round(self.magnitude, 3),
            "topic": self.topic,
            "before_avg": round(self.before_avg, 3),
            "after_avg": round(self.after_avg, 3),
        }


@dataclass
class TrendSnapshot:
    """趋势快照"""
    snapshot_id: str
    timestamp: datetime
    round_num: int
    top_topics: List[str]
    overall_sentiment: float
    consensus_level: float
    active_palaces: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "round_num": self.round_num,
            "top_topics": self.top_topics,
            "overall_sentiment": round(self.overall_sentiment, 3),
            "consensus_level": round(self.consensus_level, 3),
            "active_palaces": self.active_palaces,
        }


@dataclass
class EmergenceResult:
    """群体涌现结果"""
    overall_sentiment: float
    sentiment_trend: str  # "上升" / "下降" / "平稳"
    consensus_level: float  # 群体共识度 0-1
    emerging_topics: List[str]
    declining_topics: List[str]
    conflict_zones: List[str]  # 高冲突区域
    key_insights: List[str]
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "overall_sentiment": round(self.overall_sentiment, 3),
            "sentiment_trend": self.sentiment_trend,
            "consensus_level": round(self.consensus_level, 3),
            "emerging_topics": self.emerging_topics,
            "declining_topics": self.declining_topics,
            "conflict_zones": self.conflict_zones,
            "key_insights": self.key_insights,
            "confidence": round(self.confidence, 3),
        }


# ============ 涌现模式定义 ============

EMERGENCE_PATTERNS = {
    "sudden_consensus": {
        "condition": "consensus > 0.8 and velocity > 0.5",
        "insight": "群体快速达成共识",
    },
    "growing_conflict": {
        "condition": "conflict_count > 5 and increasing",
        "insight": "观点冲突加剧",
    },
    "topic_shift": {
        "condition": "top_topic changed in 3 consecutive rounds",
        "insight": "关注话题发生转移",
    },
    "sentiment_polarization": {
        "condition": "sentiment_std > 0.6",
        "insight": "情感两极分化",
    },
}


# ============ 计算工具函数 ============

def calculate_trending_score(
    mention_count: int,
    sentiment: float,
    velocity: float,  # 增长速度
    recency: float,  # 时效性 0-1
) -> float:
    """
    计算话题热门分数

    Args:
        mention_count: 提及次数
        sentiment: 平均情感值 (-1 to 1)
        velocity: 增长速度指标
        recency: 时效性权重

    Returns:
        热门分数
    """
    return (
        mention_count * 0.3 +
        (sentiment + 1) * 0.2 +  # 归一化到0-1
        velocity * 0.3 +
        recency * 0.2
    )


def calculate_velocity(
    current_count: int,
    previous_count: int,
    time_delta: float,
) -> float:
    """
    计算话题增长速率

    Args:
        current_count: 当前提及数
        previous_count: 之前提及数
        time_delta: 时间间隔（轮次）

    Returns:
        速度值
    """
    if time_delta <= 0:
        return 0.0
    return (current_count - previous_count) / time_delta


def calculate_consensus(opinions: List[float]) -> float:
    """
    基于方差计算共识度

    Args:
        opinions: 观点分数列表

    Returns:
        共识度 0-1（方差越小，共识度越高）
    """
    if len(opinions) < 2:
        return 1.0
    variance = statistics.variance(opinions)
    return max(0.0, 1.0 - variance)


def detect_sentiment_shift_impl(
    before: List[float],
    after: List[float],
    topic: str,
    threshold: float = 0.2,
) -> Optional[SentimentShift]:
    """
    检测情感变化

    Args:
        before: 变化前的情感值列表
        after: 变化后的情感值列表
        topic: 话题名称
        threshold: 变化阈值

    Returns:
        SentimentShift 或 None
    """
    if not before or not after:
        return None

    before_avg = sum(before) / len(before)
    after_avg = sum(after) / len(after)
    delta = after_avg - before_avg

    if abs(delta) > threshold:
        return SentimentShift(
            direction="positive" if delta > 0 else "negative",
            magnitude=abs(delta),
            topic=topic,
            before_avg=before_avg,
            after_avg=after_avg,
        )
    return None


# ============ 核心追踪器 ============

class TrendTracker:
    """
    社交趋势追踪器

    追踪热门话题、情感变化、观点聚类和群体涌现。
    """

    def __init__(self):
        """初始化趋势追踪器"""
        # 热门话题
        self.trending_topics: List[Topic] = []
        self.topic_map: Dict[str, Topic] = {}

        # 情感时间线
        self.sentiment_timeline: List[SentimentDataPoint] = []

        # 观点聚类
        self.opinion_clusters: List[OpinionCluster] = []

        # 历史快照
        self.historical_data: List[TrendSnapshot] = []

        # 内部状态
        self._previous_mention_counts: Dict[str, int] = {}
        self._previous_top_topic: Optional[str] = None
        self._topic_change_streak: int = 0
        self._sentiment_history: Dict[str, List[float]] = defaultdict(list)
        self._conflict_history: List[int] = []  # 每轮冲突数历史

        # 初始化话题
        self._initialize_topics()

    def _initialize_topics(self) -> None:
        """初始化所有话题"""
        for topic_name, category in TOPIC_CATEGORIES.items():
            topic = Topic(name=topic_name, category=category)
            self.topic_map[topic_name] = topic
            self.trending_topics.append(topic)

    def update(
        self,
        posts: List[Post],
        events: List[SocialEvent],
        round_num: int,
    ) -> None:
        """
        更新趋势数据

        Args:
            posts: 本轮新帖子
            events: 本轮社交事件
            round_num: 当前轮次
        """
        # 1. 更新热门话题
        self._update_trending_topics(posts)

        # 2. 记录情感变化
        self._record_sentiment_timeline(posts, events, round_num)

        # 3. 聚类观点
        self._update_opinion_clusters(posts, events)

        # 4. 保存快照
        self._save_snapshot(posts, events, round_num)

    def _update_trending_topics(self, posts: List[Post]) -> None:
        """更新热门话题"""
        # 更新每个话题的提及数和情感
        for topic in self.trending_topics:
            topic.update_from_posts(posts)

            # 计算热门分数
            current_count = topic.mention_count
            previous_count = self._previous_mention_counts.get(topic.name, 0)
            velocity = calculate_velocity(current_count, previous_count, 1.0)

            # 计算时效性（基于最后更新时间）
            time_since_update = (datetime.now() - topic.last_updated).total_seconds()
            recency = max(0.0, 1.0 - (time_since_update / 3600))  # 1小时衰减

            topic.trending_score = calculate_trending_score(
                mention_count=current_count,
                sentiment=topic.sentiment_avg,
                velocity=max(0.0, velocity),
                recency=recency,
            )

            # 更新历史记录
            self._previous_mention_counts[topic.name] = current_count

        # 排序热门话题
        self.trending_topics.sort(key=lambda t: t.trending_score, reverse=True)

    def _record_sentiment_timeline(
        self,
        posts: List[Post],
        events: List[SocialEvent],
        round_num: int,
    ) -> None:
        """记录情感时间线"""
        # 计算各话题情感
        topic_sentiments: Dict[str, float] = {}
        for topic_name in self.topic_map:
            topic_posts = [p for p in posts if p.topic == topic_name]
            if topic_posts:
                topic_sentiments[topic_name] = sum(p.sentiment for p in topic_posts) / len(topic_posts)

        # 计算各宫位情感
        palace_sentiments: Dict[str, float] = defaultdict(list)
        for post in posts:
            palace_sentiments[post.author_palace].append(post.sentiment)

        palace_avg: Dict[str, float] = {
            palace: sum(sentiments) / len(sentiments)
            for palace, sentiments in palace_sentiments.items()
        }

        # 计算整体情感
        all_sentiments = [p.sentiment for p in posts]
        overall = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0.0

        # 创建数据点
        data_point = SentimentDataPoint(
            timestamp=datetime.now(),
            round_num=round_num,
            overall_sentiment=overall,
            topic_sentiments=topic_sentiments,
            palace_sentiments=palace_avg,
        )

        self.sentiment_timeline.append(data_point)

        # 更新情感历史用于变化检测
        for topic, sentiment in topic_sentiments.items():
            self._sentiment_history[topic].append(sentiment)

    def _update_opinion_clusters(
        self,
        posts: List[Post],
        events: List[SocialEvent],
    ) -> None:
        """更新观点聚类"""
        # 基于帖子情感和宫位进行简单聚类
        palace_sentiments: Dict[str, List[float]] = defaultdict(list)

        for post in posts:
            palace_sentiments[post.author_palace].append(post.sentiment)

        # 对每个话题计算聚类
        topic_clusters: Dict[str, List[str]] = defaultdict(list)

        for topic_name in self.topic_map:
            topic_posts = [p for p in posts if p.topic == topic_name]
            if len(topic_posts) < 2:
                continue

            sentiments = [p.sentiment for p in topic_posts]

            # 简单聚类：正面/负面/中性
            avg_sentiment = sum(sentiments) / len(sentiments)

            if avg_sentiment > 0.3:
                cluster_type = "positive"
            elif avg_sentiment < -0.3:
                cluster_type = "negative"
            else:
                cluster_type = "neutral"

            topic_clusters[topic_name].append(cluster_type)

        # 更新现有聚类或创建新聚类
        existing_topics = {c.dominant_topic for c in self.opinion_clusters}

        for topic_name, cluster_types in topic_clusters.items():
            if topic_name not in existing_topics and cluster_types:
                cluster = OpinionCluster(
                    cluster_id=str(uuid.uuid4())[:8],
                    dominant_topic=topic_name,
                    dominant_sentiment=sum(cluster_types.count(t) for t in ["positive", "negative", "neutral"]) / 3,
                    participating_palaces=list(set(p.author_palace for p in posts if p.topic == topic_name)),
                    strength=0.5,
                    evolution=[],
                )
                self.opinion_clusters.append(cluster)

    def _save_snapshot(
        self,
        posts: List[Post],
        events: List[SocialEvent],
        round_num: int,
    ) -> None:
        """保存趋势快照"""
        # 获取当前热门话题
        top_topics = [t.name for t in self.get_trending_topics(limit=3)]

        # 检查话题变化
        if self._previous_top_topic and top_topics:
            if top_topics[0] != self._previous_top_topic:
                self._topic_change_streak += 1
            else:
                self._topic_change_streak = 0
        self._previous_top_topic = top_topics[0] if top_topics else None

        # 计算共识度
        all_sentiments = [p.sentiment for p in posts]
        consensus = calculate_consensus(all_sentiments)

        # 活跃宫位
        active_palaces = list(set(p.author_palace for p in posts))

        # 整体情感
        overall_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0.0

        # 记录冲突数
        conflict_count = sum(1 for e in events if e.event_type.value == "冲突")
        self._conflict_history.append(conflict_count)

        snapshot = TrendSnapshot(
            snapshot_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            round_num=round_num,
            top_topics=top_topics,
            overall_sentiment=overall_sentiment,
            consensus_level=consensus,
            active_palaces=active_palaces,
        )

        self.historical_data.append(snapshot)

        # 限制历史数据大小
        if len(self.historical_data) > 100:
            self.historical_data = self.historical_data[-100:]

    def get_trending_topics(
        self,
        limit: int = 5,
        time_window: int = 10,
    ) -> List[Topic]:
        """
        获取热门话题

        Args:
            limit: 返回数量限制
            time_window: 时间窗口（轮次）

        Returns:
            热门话题列表
        """
        # 基于时间窗口过滤
        cutoff_time = datetime.now()
        recent_topics = [
            t for t in self.trending_topics
            if t.mention_count > 0
        ]

        return recent_topics[:limit]

    def calculate_group_emergence(self) -> EmergenceResult:
        """
        计算群体涌现结果

        Returns:
            涌现分析结果
        """
        insights: List[str] = []
        emerging_topics: List[str] = []
        declining_topics: List[str] = []
        conflict_zones: List[str] = []

        # 计算整体情感和趋势
        overall_sentiment = 0.0
        if self.sentiment_timeline:
            latest = self.sentiment_timeline[-1]
            overall_sentiment = latest.overall_sentiment

        # 计算情感趋势
        sentiment_trend = "平稳"
        if len(self.sentiment_timeline) >= 2:
            recent_avg = sum(
                dp.overall_sentiment for dp in self.sentiment_timeline[-3:]
            ) / min(3, len(self.sentiment_timeline))
            earlier_avg = sum(
                dp.overall_sentiment for dp in self.sentiment_timeline[:-3]
            ) / max(1, len(self.sentiment_timeline) - 3)

            if recent_avg - earlier_avg > 0.1:
                sentiment_trend = "上升"
            elif earlier_avg - recent_avg > 0.1:
                sentiment_trend = "下降"

        # 计算共识度
        consensus_level = 0.0
        if self.sentiment_timeline:
            latest = self.sentiment_timeline[-1]
            palace_sentiments = list(latest.palace_sentiments.values())
            consensus_level = calculate_consensus(palace_sentiments)

        # 检测涌现模式
        # 1. 突然共识
        if consensus_level > 0.8 and self._topic_change_streak > 0:
            insights.append(EMERGENCE_PATTERNS["sudden_consensus"]["insight"])

        # 2. 冲突加剧
        if len(self._conflict_history) >= 3:
            recent_conflicts = self._conflict_history[-3:]
            if all(recent_conflicts[i] <= recent_conflicts[i+1] for i in range(len(recent_conflicts)-1)):
                if recent_conflicts[-1] > 5:
                    insights.append(EMERGENCE_PATTERNS["growing_conflict"]["insight"])
                    conflict_zones.append("多宫位观点分歧")

        # 3. 话题转移
        if self._topic_change_streak >= 3:
            insights.append(EMERGENCE_PATTERNS["topic_shift"]["insight"])

        # 4. 情感两极分化
        if self.sentiment_timeline and len(self.sentiment_timeline) >= 2:
            latest = self.sentiment_timeline[-1]
            if latest.palace_sentiments:
                sentiments = list(latest.palace_sentiments.values())
                if len(sentiments) >= 2:
                    sentiment_std = statistics.stdev(sentiments)
                    if sentiment_std > 0.6:
                        insights.append(EMERGENCE_PATTERNS["sentiment_polarization"]["insight"])

        # 识别新兴和衰退话题
        if len(self.trending_topics) >= 2:
            if self.trending_topics[0].trending_score > self.trending_topics[1].trending_score * 1.5:
                emerging_topics.append(self.trending_topics[0].name)

            if len(self.trending_topics) > 3:
                if self.trending_topics[-1].trending_score < 1.0:
                    declining_topics.append(self.trending_topics[-1].name)

        # 计算置信度
        confidence = min(1.0, len(self.sentiment_timeline) * 0.1 + 0.3)

        return EmergenceResult(
            overall_sentiment=overall_sentiment,
            sentiment_trend=sentiment_trend,
            consensus_level=consensus_level,
            emerging_topics=emerging_topics,
            declining_topics=declining_topics,
            conflict_zones=conflict_zones,
            key_insights=insights,
            confidence=confidence,
        )

    def detect_sentiment_shift(self, topic: str) -> Optional[SentimentShift]:
        """
        检测情感变化

        Args:
            topic: 话题名称

        Returns:
            情感变化信息或 None
        """
        history = self._sentiment_history.get(topic, [])

        if len(history) < 4:
            return None

        # 比较前半段和后半段的情感
        mid = len(history) // 2
        before = history[:mid]
        after = history[mid:]

        return detect_sentiment_shift_impl(before, after, topic)

    def get_opinion_distribution(self) -> Dict[str, float]:
        """
        获取观点分布

        Returns:
            {情感类型: 比例} 字典
        """
        distribution = {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 0.0,
        }

        if not self.sentiment_timeline:
            return distribution

        latest = self.sentiment_timeline[-1]
        sentiments = list(latest.palace_sentiments.values())

        if not sentiments:
            return distribution

        total = len(sentiments)
        distribution["positive"] = sum(1 for s in sentiments if s > 0.3) / total
        distribution["negative"] = sum(1 for s in sentiments if s < -0.3) / total
        distribution["neutral"] = sum(1 for s in sentiments if -0.3 <= s <= 0.3) / total

        return distribution

    def generate_insights(self) -> List[str]:
        """
        生成趋势洞察

        Returns:
            洞察列表
        """
        insights: List[str] = []

        if not self.sentiment_timeline:
            return ["暂无足够数据生成洞察"]

        # 1. 基于热门话题
        top_topics = self.get_trending_topics(limit=3)
        if top_topics:
            topic_names = ", ".join([t.name for t in top_topics[:2]])
            insights.append(f"当前热门话题: {topic_names}")

        # 2. 基于情感趋势
        emergence = self.calculate_group_emergence()
        if emergence.sentiment_trend != "平稳":
            trend_desc = "改善" if emergence.sentiment_trend == "上升" else "恶化"
            insights.append(f"整体情感趋势{trend_desc}")

        # 3. 基于共识度
        if emergence.consensus_level > 0.8:
            insights.append("群体达成高度共识")
        elif emergence.consensus_level < 0.3:
            insights.append("群体观点分歧明显")

        # 4. 基于涌现模式
        insights.extend(emergence.key_insights)

        # 5. 基于新兴/衰退话题
        if emergence.emerging_topics:
            insights.append(f"新兴关注: {', '.join(emergence.emerging_topics)}")
        if emergence.declining_topics:
            insights.append(f"关注度下降: {', '.join(emergence.declining_topics)}")

        # 6. 基于情感变化检测
        for topic_name in list(self._sentiment_history.keys())[:3]:
            shift = self.detect_sentiment_shift(topic_name)
            if shift:
                direction = "转向正面" if shift.direction == "positive" else "转向负面"
                insights.append(f"{topic_name}情感{direction}")

        # 7. 基于冲突区域
        if emergence.conflict_zones:
            insights.append(f"高冲突区域: {', '.join(emergence.conflict_zones)}")

        # 8. 观点分布
        distribution = self.get_opinion_distribution()
        positive_pct = int(distribution["positive"] * 100)
        negative_pct = int(distribution["negative"] * 100)
        insights.append(f"观点分布: {positive_pct}%正面, {negative_pct}%负面")

        return insights if insights else ["数据不足，无法生成有效洞察"]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "trending_topics": [t.to_dict() for t in self.trending_topics[:10]],
            "sentiment_timeline": [dp.to_dict() for dp in self.sentiment_timeline[-20:]],
            "opinion_clusters": [c.to_dict() for c in self.opinion_clusters],
            "historical_data": [s.to_dict() for s in self.historical_data[-20:]],
            "emergence_result": self.calculate_group_emergence().to_dict(),
            "insights": self.generate_insights(),
        }
