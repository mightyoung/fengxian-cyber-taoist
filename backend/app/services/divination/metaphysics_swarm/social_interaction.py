"""
SocialInteractionEngine - 社交互动引擎

基于四化（化禄/化权/化科/化忌）生成交互事件：
- 观点生成与传播
- 冲突检测与共识计算
- Agent间影响力追踪
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random
import math

from app.services.divination.metaphysics_swarm.social_network import SocialNetwork, SocialNode, SocialEdge
from app.services.divination.metaphysics_swarm.agents import MetaphysicsAgent
from app.services.divination.metaphysics_swarm.scenarios import Scenario, ScenarioType


# ============ 事件类型定义 ============

class EventType(str, Enum):
    """社交事件类型"""
    OPINION_POST = "观点发表"     # Agent发表观点
    COMMENT = "评论"              # Agent评论他人观点
    RETWEET = "转发"              # 转发传播
    CONFLICT = "冲突"             # 观点冲突
    CONSENSUS = "共识"            # 达成共识


# ============ 四化→社交行为映射 ============

@dataclass
class TransformBehavior:
    """四化对应的社交行为"""
    behavior: str          # 行为类型
    tendency: str          # 倾向描述
    conflict_prob: float   # 冲突概率

TRANSFORMATION_TO_SOCIAL: Dict[str, TransformBehavior] = {
    "化禄": TransformBehavior("分享", "合作", 0.3),
    "化权": TransformBehavior("主导", "说服", 0.5),
    "化科": TransformBehavior("讨论", "建议", 0.2),
    "化忌": TransformBehavior("质疑", "反对", 0.7),
}

# 四化对观点影响力的调整系数
TRANSFORM_INFLUENCE_MODIFIER: Dict[str, float] = {
    "化禄": 1.2,   # 正面放大
    "化权": 1.1,   # 略增
    "化科": 1.0,   # 中性
    "化忌": 0.8,   # 负面影响
}


# ============ 数据模型 ============

@dataclass
class SocialEvent:
    """社交事件"""
    round_num: int
    event_type: EventType
    source_palace: str
    target_palace: Optional[str]
    content: str
    topic: str
    sentiment: float  # -1.0 to 1.0
    influence: float  # 传播影响力
    timestamp: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "round_num": self.round_num,
            "event_type": self.event_type.value,
            "source_palace": self.source_palace,
            "target_palace": self.target_palace,
            "content": self.content,
            "topic": self.topic,
            "sentiment": self.sentiment,
            "influence": self.influence,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
        }


@dataclass
class Opinion:
    """观点"""
    palace: str
    topic: str
    score: float          # 观点倾向分数 -1.0 to 1.0
    confidence: float     # 置信度 0.0 to 1.0
    round_created: int
    source_event_id: Optional[str] = None


@dataclass
class RoundResult:
    """轮次模拟结果"""
    round_num: int
    events: List[SocialEvent]
    opinion_changes: Dict[str, Dict[str, float]]  # {palace: {topic: change}}
    new_consensus: Optional[float]
    new_conflicts: List[Tuple[str, str]]
    sentiment_trend: float  # 本轮情感趋势
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class InteractionMetrics:
    """互动指标"""
    total_events: int = 0
    opinion_posts: int = 0
    comments: int = 0
    retweets: int = 0
    conflicts: int = 0
    consensus_reached: int = 0
    average_sentiment: float = 0.0
    consensus_score: float = 0.0


# ============ 观点主题模板 ============

OPINION_TOPICS = [
    "事业发展方向",
    "财务投资策略",
    "人际关系处理",
    "健康生活方式",
    "家庭责任分担",
    "学业进修计划",
    "退休养老安排",
]


# ============ 核心引擎 ============

class SocialInteractionEngine:
    """
    社交互动引擎

    基于四化特征生成Agent间的交互事件，追踪观点传播，计算群体共识度。
    """

    def __init__(
        self,
        network: SocialNetwork,
        agents: List[MetaphysicsAgent],
    ):
        """
        初始化社交互动引擎

        Args:
            network: 社交网络
            agents: Agent列表
        """
        self.network = network
        self.agents = {agent.id: agent for agent in agents}
        self.agent_by_palace: Dict[str, MetaphysicsAgent] = {
            agent.persona.palace_name: agent for agent in agents
        }

        # 事件历史
        self.events: List[SocialEvent] = []

        # 观点追踪: {palace: {topic: Opinion}}
        self.opinions: Dict[str, Dict[str, Opinion]] = {}

        # 影响力传播记录: {source_palace: {affected_palace: influence_value}}
        self.influence_map: Dict[str, Dict[str, float]] = {}

        # 冲突记录: [(palace1, palace2)]
        self.conflicts: List[Tuple[str, str]] = []

        # 指标
        self.metrics = InteractionMetrics()

        # 初始化观点
        self._initialize_opinions()

    def _initialize_opinions(self) -> None:
        """初始化各宫位的观点"""
        for palace in self.network.nodes.keys():
            self.opinions[palace] = {}
            self.influence_map[palace] = {}

            # 初始化基于四化的初始观点
            agent = self.agent_by_palace.get(palace)
            if agent:
                transforms = agent.persona.transforms
                for topic in OPINION_TOPICS:
                    # 根据四化确定初始倾向
                    base_score = self._get_transform_opinion_score(transforms, topic)
                    self.opinions[palace][topic] = Opinion(
                        palace=palace,
                        topic=topic,
                        score=base_score,
                        confidence=0.3,
                        round_created=0,
                    )

    def _get_transform_opinion_score(self, transforms: List[str], topic: str) -> float:
        """根据四化获取初始观点分数"""
        if not transforms:
            return 0.0

        total = 0.0
        count = 0

        for transform in transforms:
            if transform in TRANSFORMATION_TO_SOCIAL:
                behavior = TRANSFORMATION_TO_SOCIAL[transform]
                if behavior.behavior in ["分享", "讨论", "建议"]:
                    total += 0.3  # 正面
                elif behavior.behavior in ["主导", "说服"]:
                    total += 0.1  # 略正面
                elif behavior.behavior in ["质疑", "反对"]:
                    total -= 0.4  # 负面
                count += 1

        if count > 0:
            return max(-1.0, min(1.0, total / count))
        return 0.0

    async def simulate_round(
        self,
        round_num: int,
        scenario: Optional[Scenario] = None,
    ) -> RoundResult:
        """
        模拟一轮社交互动

        Args:
            round_num: 轮次编号
            scenario: 场景上下文

        Returns:
            轮次模拟结果
        """
        round_events: List[SocialEvent] = []
        opinion_changes: Dict[str, Dict[str, float]] = {palace: {} for palace in self.network.nodes}
        new_conflicts: List[Tuple[str, str]] = []

        # 1. 生成观点事件
        post_events = await self._generate_opinion_events(round_num)
        round_events.extend(post_events)

        # 2. 传播观点
        propagation_events = await self._propagate_opinions(round_num)
        round_events.extend(propagation_events)

        # 3. 计算互动（评论）
        comment_events = await self._generate_comments(round_num)
        round_events.extend(comment_events)

        # 4. 检测冲突
        new_conflicts = self._detect_conflicts(round_num)
        round_events.extend(self._create_conflict_events(round_num, new_conflicts))

        # 5. 检测共识
        current_consensus = self.calculate_consensus()
        consensus_event = self._check_consensus(round_num, current_consensus)
        if consensus_event:
            round_events.append(consensus_event)

        # 6. 更新观点
        for palace in self.network.nodes:
            for topic, opinion in self.opinions[palace].items():
                old_score = opinion.score
                # 应用事件影响
                for event in round_events:
                    if event.source_palace == palace and event.topic == topic:
                        # 根据事件类型调整影响力
                        if event.event_type == EventType.OPINION_POST:
                            influence = event.influence * 0.15
                        elif event.event_type == EventType.COMMENT:
                            influence = event.sentiment * event.influence * 0.1
                        elif event.event_type == EventType.RETWEET:
                            influence = event.influence * 0.08
                        else:
                            influence = 0.0

                        opinion.score = max(-1.0, min(1.0, opinion.score + influence))
                        opinion.confidence = min(1.0, opinion.confidence + 0.05)

                change = opinion.score - old_score
                if abs(change) > 0.01:
                    opinion_changes[palace][topic] = change

        # 7. 更新指标
        self._update_metrics(round_events, new_conflicts, current_consensus)

        # 添加事件到历史
        self.events.extend(round_events)

        # 计算情感趋势
        sentiment_trend = self._calculate_sentiment_trend(round_events)

        return RoundResult(
            round_num=round_num,
            events=round_events,
            opinion_changes=opinion_changes,
            new_consensus=current_consensus,
            new_conflicts=new_conflicts,
            sentiment_trend=sentiment_trend,
        )

    async def _generate_opinion_events(self, round_num: int) -> List[SocialEvent]:
        """生成观点发表事件"""
        events: List[SocialEvent] = []

        # 随机选择发言的宫位（根据社交分数加权）
        palaces = list(self.network.nodes.keys())
        weights = [
            self.network.nodes[p].get_centrality_score()
            for p in palaces
        ]
        total_weight = sum(weights) or 1.0
        probabilities = [w / total_weight for w in weights]

        # 选择2-4个宫位发言
        num_posters = min(len(palaces), random.randint(2, 4))
        selected_palaces = random.choices(
            palaces,
            weights=probabilities,
            k=num_posters,
        )

        for palace in selected_palaces:
            agent = self.agent_by_palace.get(palace)
            if not agent:
                continue

            # 选择主题
            topic = random.choice(OPINION_TOPICS)

            # 根据四化生成观点
            transform = self._get_dominant_transform(agent.persona.transforms)
            behavior = TRANSFORMATION_TO_SOCIAL.get(transform, TRANSFORMATION_TO_SOCIAL["化科"])

            # 生成观点内容
            content = self._generate_opinion_content(
                palace=palace,
                topic=topic,
                transform=transform,
                agent=agent,
            )

            # 计算情感和影响力
            sentiment = self._calculate_sentiment(transform, topic)
            influence = self._calculate_influence(agent, transform)

            event = SocialEvent(
                round_num=round_num,
                event_type=EventType.OPINION_POST,
                source_palace=palace,
                target_palace=None,
                content=content,
                topic=topic,
                sentiment=sentiment,
                influence=influence,
                agent_id=agent.id,
            )

            events.append(event)

            # 更新观点
            if palace in self.opinions and topic in self.opinions[palace]:
                self.opinions[palace][topic].score = sentiment
                self.opinions[palace][topic].round_created = round_num

        return events

    async def _propagate_opinions(self, round_num: int) -> List[SocialEvent]:
        """传播观点（转发）"""
        events: List[SocialEvent] = []

        if not self.events:
            return events

        # 获取本轮新发表的观点
        recent_opinions = [
            e for e in self.events[-10:]
            if e.event_type == EventType.OPINION_POST
        ]

        for opinion_event in recent_opinions:
            source_palace = opinion_event.source_palace

            # 获取源宫位的连接
            neighbors = self.network.adjacency.get(source_palace, [])

            # 随机选择1-2个邻居进行转发
            num_recipients = min(len(neighbors), random.randint(1, 2))
            recipients = random.sample(neighbors, num_recipients) if neighbors else []

            for target_palace in recipients:
                # 获取边权重
                edge_weight = self._get_edge_weight(source_palace, target_palace)

                # 计算传播影响力
                propagation_influence = opinion_event.influence * edge_weight * 0.6

                # 更新影响力映射
                if target_palace not in self.influence_map[source_palace]:
                    self.influence_map[source_palace][target_palace] = 0.0
                self.influence_map[source_palace][target_palace] += propagation_influence

                event = SocialEvent(
                    round_num=round_num,
                    event_type=EventType.RETWEET,
                    source_palace=source_palace,
                    target_palace=target_palace,
                    content=f"转发: {opinion_event.content[:30]}...",
                    topic=opinion_event.topic,
                    sentiment=opinion_event.sentiment,
                    influence=propagation_influence,
                    agent_id=self.agent_by_palace.get(target_palace).id
                              if target_palace in self.agent_by_palace else None,
                )
                events.append(event)

                # 更新目标观点
                if target_palace in self.opinions and opinion_event.topic in self.opinions[target_palace]:
                    target_opinion = self.opinions[target_palace][opinion_event.topic]
                    # 观点趋同
                    target_opinion.score = (
                        target_opinion.score * 0.7 +
                        opinion_event.sentiment * 0.3
                    )
                    target_opinion.confidence = min(1.0, target_opinion.confidence + 0.1)

        return events

    async def _generate_comments(self, round_num: int) -> List[SocialEvent]:
        """生成评论事件"""
        events: List[SocialEvent] = []

        if not self.events:
            return events

        # 获取最近的观点和转发
        recent_posts = [
            e for e in self.events[-15:]
            if e.event_type in [EventType.OPINION_POST, EventType.RETWEET]
        ]

        # 随机生成评论
        for _ in range(random.randint(0, 3)):
            if not recent_posts:
                break

            post = random.choice(recent_posts)
            commenter_palace = random.choice(list(self.network.nodes.keys()))

            # 不评论自己的帖子
            if commenter_palace == post.source_palace:
                continue

            commenter = self.agent_by_palace.get(commenter_palace)
            if not commenter:
                continue

            # 根据评论者的四化确定立场
            transform = self._get_dominant_transform(commenter.persona.transforms)
            behavior = TRANSFORMATION_TO_SOCIAL.get(transform, TRANSFORMATION_TO_SOCIAL["化科"])

            # 计算评论情感（与原观点的关系）
            if behavior.conflict_prob > 0.5:
                comment_sentiment = -post.sentiment * random.uniform(0.5, 1.0)
            else:
                comment_sentiment = post.sentiment * random.uniform(0.3, 0.8)

            content = self._generate_comment_content(
                commenter=commenter,
                original_post=post,
                transform=transform,
            )

            event = SocialEvent(
                round_num=round_num,
                event_type=EventType.COMMENT,
                source_palace=commenter_palace,
                target_palace=post.source_palace,
                content=content,
                topic=post.topic,
                sentiment=comment_sentiment,
                influence=0.3,
                agent_id=commenter.id,
            )
            events.append(event)

        return events

    def _detect_conflicts(self, round_num: int) -> List[Tuple[str, str]]:
        """检测观点冲突的宫位对"""
        new_conflicts: List[Tuple[str, str]] = []

        palaces = list(self.network.nodes.keys())

        for i, p1 in enumerate(palaces):
            for p2 in palaces[i+1:]:
                # 检查是否相邻
                if p2 not in self.network.adjacency.get(p1, []):
                    continue

                # 计算观点分歧
                conflict_score = self._calculate_palace_conflict(p1, p2)

                if conflict_score > 0.6:
                    conflict_pair = tuple(sorted([p1, p2]))
                    if conflict_pair not in self.conflicts:
                        new_conflicts.append(conflict_pair)
                        self.conflicts.append(conflict_pair)

        return new_conflicts

    def _calculate_palace_conflict(self, p1: str, p2: str) -> float:
        """计算两个宫位间的冲突程度"""
        if p1 not in self.opinions or p2 not in self.opinions:
            return 0.0

        total_diff = 0.0
        topics_compared = 0

        common_topics = set(self.opinions[p1].keys()) & set(self.opinions[p2].keys())
        for topic in common_topics:
            diff = abs(
                self.opinions[p1][topic].score -
                self.opinions[p2][topic].score
            )
            # 加入化忌的冲突放大
            agent1 = self.agent_by_palace.get(p1)
            agent2 = self.agent_by_palace.get(p2)

            if agent1 and "化忌" in agent1.persona.transforms:
                diff *= 1.2
            if agent2 and "化忌" in agent2.persona.transforms:
                diff *= 1.2

            total_diff += diff
            topics_compared += 1

        if topics_compared == 0:
            return 0.0

        return total_diff / topics_compared

    def _create_conflict_events(
        self,
        round_num: int,
        conflicts: List[Tuple[str, str]],
    ) -> List[SocialEvent]:
        """创建冲突事件"""
        events: List[SocialEvent] = []

        for p1, p2 in conflicts:
            agent1 = self.agent_by_palace.get(p1)
            agent2 = self.agent_by_palace.get(p2)

            event = SocialEvent(
                round_num=round_num,
                event_type=EventType.CONFLICT,
                source_palace=p1,
                target_palace=p2,
                content=f"观点冲突: {p1}与{p2}在多个话题上存在分歧",
                topic="综合",
                sentiment=-0.3,
                influence=0.5,
                agent_id=agent1.id if agent1 else None,
            )
            events.append(event)

        return events

    def _check_consensus(
        self,
        round_num: int,
        current_consensus: float,
    ) -> Optional[SocialEvent]:
        """检查是否达成共识"""
        # 简单策略：共识度超过0.7且本轮没有新冲突
        if current_consensus > 0.7 and not any(
            e.event_type == EventType.CONFLICT
            for e in self.events[-5:]
        ):
            return SocialEvent(
                round_num=round_num,
                event_type=EventType.CONSENSUS,
                source_palace="群体",
                target_palace=None,
                content=f"群体达成共识，共识度: {current_consensus:.2f}",
                topic="综合",
                sentiment=0.5,
                influence=0.0,
            )
        return None

    def calculate_consensus(self) -> float:
        """
        计算群体共识度

        Returns:
            共识度分数 0.0-1.0
        """
        if not self.opinions:
            return 0.0

        total_variance = 0.0
        topic_count = 0

        # 对每个话题计算方差
        for topic in OPINION_TOPICS:
            topic_scores = []
            for palace in self.network.nodes:
                if palace in self.opinions and topic in self.opinions[palace]:
                    topic_scores.append(self.opinions[palace][topic].score)

            if len(topic_scores) >= 2:
                # 计算方差
                mean = sum(topic_scores) / len(topic_scores)
                variance = sum((s - mean) ** 2 for s in topic_scores) / len(topic_scores)
                total_variance += variance
                topic_count += 1

        if topic_count == 0:
            return 0.0

        # 平均方差转共识度（方差越小共识越高）
        avg_variance = total_variance / topic_count
        consensus = max(0.0, min(1.0, 1.0 - math.sqrt(avg_variance)))

        return consensus

    def get_influence_propagation(self, source_palace: str) -> Dict[str, float]:
        """
        获取从某个宫位传播出去的影响

        Args:
            source_palace: 源宫位

        Returns:
            {目标宫位: 影响值}
        """
        return self.influence_map.get(source_palace, {}).copy()

    def get_conflict_zones(self) -> List[Tuple[str, str]]:
        """
        识别观点冲突的宫位对

        Returns:
            冲突宫位对列表
        """
        return self.conflicts.copy()

    def _get_dominant_transform(self, transforms: List[str]) -> str:
        """获取主导四化"""
        priority_order = ["化忌", "化权", "化禄", "化科"]

        for t in priority_order:
            if t in transforms:
                return t

        return "化科"

    def _generate_opinion_content(
        self,
        palace: str,
        topic: str,
        transform: str,
        agent: MetaphysicsAgent,
    ) -> str:
        """生成观点内容"""
        templates = {
            "化禄": [
                f"{palace}认为{topic}应该积极把握机会",
                f"{palace}分享了关于{topic}的乐观看法",
                f"对{topic}，{palace}主张主动出击",
            ],
            "化权": [
                f"{palace}坚持在{topic}上要掌控主导权",
                f"{palace}认为{topic}需要强势推进",
                f"关于{topic}，{palace}主张不能退让",
            ],
            "化科": [
                f"{palace}建议理性分析{topic}",
                f"关于{topic}，{palace}认为需要深入研究",
                f"{palace}提出了对{topic}的学术性观点",
            ],
            "化忌": [
                f"{palace}对{topic}表示担忧",
                f"关于{topic}，{palace}认为需要谨慎应对",
                f"{palace}提醒大家注意{topic}的风险",
            ],
        }

        return random.choice(templates.get(transform, templates["化科"]))

    def _generate_comment_content(
        self,
        commenter: MetaphysicsAgent,
        original_post: SocialEvent,
        transform: str,
    ) -> str:
        """生成评论内容"""
        commenter_palace = commenter.persona.palace_name

        if transform == "化忌":
            return f"@{original_post.source_palace} 这个观点我有些担忧..."
        elif transform == "化权":
            return f"@{original_post.source_palace} 我有不同的看法，应该这样做..."
        elif transform == "化禄":
            return f"@{original_post.source_palace} 有道理！支持你的观点"
        else:
            return f"@{original_post.source_palace} 值得思考，但还需要更多分析"

    def _calculate_sentiment(self, transform: str, topic: str) -> float:
        """计算情感值"""
        base_sentiment = {
            "化禄": 0.6,
            "化权": 0.2,
            "化科": 0.1,
            "化忌": -0.4,
        }
        base = base_sentiment.get(transform, 0.0)
        return max(-1.0, min(1.0, base + random.uniform(-0.1, 0.1)))

    def _calculate_influence(self, agent: MetaphysicsAgent, transform: str) -> float:
        """计算影响力"""
        # 基础影响力 = 社交分数 / 100
        base = agent.state.social

        # 根据四化调整
        modifier = TRANSFORM_INFLUENCE_MODIFIER.get(transform, 1.0)

        # 根据宫位中心性调整
        palace = agent.persona.palace_name
        node = self.network.nodes.get(palace)
        centrality = node.get_centrality_score() / 100.0 if node else 0.5

        influence = base * modifier * (0.7 + centrality * 0.6)
        return max(0.1, min(1.0, influence))

    def _get_edge_weight(self, source: str, target: str) -> float:
        """获取边权重"""
        for edge in self.network.edges:
            if edge.source == source and edge.target == target:
                return edge.weight
            if edge.source == target and edge.target == source:
                return edge.weight
        return 0.5

    def _calculate_sentiment_trend(self, events: List[SocialEvent]) -> float:
        """计算情感趋势"""
        if not events:
            return 0.0

        sentiments = [e.sentiment for e in events]
        return sum(sentiments) / len(sentiments)

    def _update_metrics(
        self,
        events: List[SocialEvent],
        new_conflicts: List[Tuple[str, str]],
        consensus: float,
    ) -> None:
        """更新指标"""
        self.metrics.total_events += len(events)
        self.metrics.opinion_posts += sum(
            1 for e in events if e.event_type == EventType.OPINION_POST
        )
        self.metrics.comments += sum(
            1 for e in events if e.event_type == EventType.COMMENT
        )
        self.metrics.retweets += sum(
            1 for e in events if e.event_type == EventType.RETWEET
        )
        self.metrics.conflicts += len(new_conflicts)
        self.metrics.consensus_score = consensus

        # 更新平均情感
        if events:
            total_sentiment = sum(e.sentiment for e in events)
            n = len(self.events)
            old_avg = self.metrics.average_sentiment * (n - len(events))
            self.metrics.average_sentiment = (old_avg + total_sentiment) / n if n > 0 else 0.0

    def get_metrics(self) -> InteractionMetrics:
        """获取互动指标"""
        return self.metrics

    def get_events_summary(self) -> Dict[str, Any]:
        """获取事件摘要"""
        return {
            "total_events": len(self.events),
            "by_type": {
                etype.value: sum(1 for e in self.events if e.event_type == etype)
                for etype in EventType
            },
            "by_palace": {
                palace: sum(1 for e in self.events if e.source_palace == palace)
                for palace in self.network.nodes
            },
        }

    def get_opinions_state(self) -> Dict[str, Dict[str, float]]:
        """获取当前观点状态"""
        return {
            palace: {
                topic: opinion.score
                for topic, opinion in topics.items()
            }
            for palace, topics in self.opinions.items()
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "events_count": len(self.events),
            "conflicts_count": len(self.conflicts),
            "consensus_score": self.calculate_consensus(),
            "metrics": {
                "total_events": self.metrics.total_events,
                "opinion_posts": self.metrics.opinion_posts,
                "comments": self.metrics.comments,
                "retweets": self.metrics.retweets,
                "conflicts": self.metrics.conflicts,
                "consensus_reached": self.metrics.consensus_reached,
                "average_sentiment": self.metrics.average_sentiment,
            },
        }
