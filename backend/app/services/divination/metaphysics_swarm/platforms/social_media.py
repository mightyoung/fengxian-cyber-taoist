"""
Social Media Platform Simulator - 社交媒体平台模拟器

模拟 Twitter/Reddit 风格的社交媒体平台：
- Twitter: 短观点、高转发率、热点话题易爆发、互动即时
- Reddit: 长帖、投票机制、子社区分化、评论树结构

依赖:
- social_interaction.py: SocialInteractionEngine
- social_network.py: SocialNetwork
- agents.py: MetaphysicsAgent
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random
import math
import uuid

# 避免循环导入
from app.services.divination.metaphysics_swarm.social_interaction import SocialInteractionEngine
from app.services.divination.metaphysics_swarm.agents import MetaphysicsAgent


# ============ 平台类型定义 ============

class PlatformType(str, Enum):
    """平台类型"""
    TWITTER = "twitter"    # 短观点、点赞、转发、评论
    REDDIT = "reddit"      # 长帖、投票、子社区


# ============ 数据模型 ============

@dataclass
class Post:
    """帖子数据模型"""
    post_id: str
    author_palace: str
    content: str
    topic: str
    sentiment: float  # -1.0 to 1.0
    likes: int = 0
    retweets: int = 0
    comments: int = 0
    engagement_score: float = 0.0
    viral_reach: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None  # 用于 Reddit 评论树
    upvotes: int = 0   # Reddit 专用
    downvotes: int = 0  # Reddit 专用

    def calculate_engagement(self) -> float:
        """计算互动分数"""
        if self.likes + self.retweets + self.comments == 0:
            return 0.0
        # Twitter: 转发权重更高
        engagement = self.likes * 1.0 + self.retweets * 3.0 + self.comments * 2.0
        return engagement

    def calculate_viral_reach(self) -> int:
        """计算病毒传播范围"""
        if self.retweets == 0:
            return self.likes + self.comments
        # 病毒传播模型
        base_reach = self.likes + self.comments
        viral_multiplier = 1 + (self.retweets * 0.5) + (self.retweets ** 0.8)
        return int(base_reach * viral_multiplier)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "post_id": self.post_id,
            "author_palace": self.author_palace,
            "content": self.content,
            "topic": self.topic,
            "sentiment": round(self.sentiment, 3),
            "likes": self.likes,
            "retweets": self.retweets,
            "comments": self.comments,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "engagement_score": round(self.engagement_score, 3),
            "viral_reach": self.viral_reach,
            "timestamp": self.timestamp.isoformat(),
            "parent_id": self.parent_id,
        }


@dataclass
class EngagementMetrics:
    """用户参与度指标"""
    user_id: str
    posts_count: int = 0
    likes_given: int = 0
    likes_received: int = 0
    retweets_given: int = 0
    retweets_received: int = 0
    comments_given: int = 0
    comments_received: int = 0
    upvotes_given: int = 0  # Reddit
    upvotes_received: int = 0  # Reddit
    total_engagement_score: float = 0.0

    def calculate_influence(self) -> float:
        """计算用户影响力"""
        received_score = (
            self.likes_received * 1.0 +
            self.retweets_received * 3.0 +
            self.comments_received * 2.0 +
            self.upvotes_received * 2.0
        )
        return min(1.0, received_score / 1000.0)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "posts_count": self.posts_count,
            "likes_given": self.likes_given,
            "likes_received": self.likes_received,
            "retweets_given": self.retweets_given,
            "retweets_received": self.retweets_received,
            "comments_given": self.comments_given,
            "comments_received": self.comments_received,
            "upvotes_given": self.upvotes_given,
            "upvotes_received": self.upvotes_received,
            "total_engagement_score": round(self.total_engagement_score, 3),
            "influence_score": round(self.calculate_influence(), 3),
        }


@dataclass
class Topic:
    """话题数据模型"""
    name: str
    post_count: int = 0
    total_sentiment: float = 0.0
    trending_score: float = 0.0
    participant_palaces: List[str] = field(default_factory=list)

    def get_average_sentiment(self) -> float:
        """获取平均情感"""
        if self.post_count == 0:
            return 0.0
        return self.total_sentiment / self.post_count

    def update_trending_score(self, posts: List[Post]) -> None:
        """更新热门分数"""
        # 基于帖子数量、互动量、情感强度计算
        recent_posts = [p for p in posts if p.topic == self.name]
        if not recent_posts:
            return

        post_score = len(recent_posts) * 10
        engagement_score = sum(p.engagement_score for p in recent_posts)
        sentiment_score = sum(abs(p.sentiment) for p in recent_posts) * 5

        self.trending_score = post_score + engagement_score + sentiment_score
        self.post_count = len(recent_posts)
        self.total_sentiment = sum(p.sentiment for p in recent_posts)
        self.participant_palaces = list(set(p.author_palace for p in recent_posts))


@dataclass
class Comment:
    """评论数据模型"""
    comment_id: str
    post_id: str
    author_palace: str
    content: str
    sentiment: float
    likes: int = 0
    parent_comment_id: Optional[str] = None  # 用于嵌套评论
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "comment_id": self.comment_id,
            "post_id": self.post_id,
            "author_palace": self.author_palace,
            "content": self.content,
            "sentiment": round(self.sentiment, 3),
            "likes": self.likes,
            "parent_comment_id": self.parent_comment_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class RoundResult:
    """一轮模拟结果"""
    round_num: int
    new_posts: List[Post]
    new_comments: List[Comment]
    engagement_events: List[Dict[str, Any]]
    trending_topics: List[Topic]
    platform_metrics: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "round_num": self.round_num,
            "new_posts_count": len(self.new_posts),
            "new_comments_count": len(self.new_comments),
            "engagement_events_count": len(self.engagement_events),
            "trending_topics": [t.name for t in self.trending_topics],
            "platform_metrics": self.platform_metrics,
            "timestamp": self.timestamp.isoformat(),
        }


# ============ 平台特定内容生成规则 ============

TWITTER_CONTENT_RULES: Dict[str, Dict[str, str]] = {
    "紫微": {
        "prefix": "【战略视角】",
        "style": "权威、领导力导向",
        "sentiment_modifier": 0.1,
        "example_templates": [
            "【战略视角】{topic}的深层逻辑在于把握核心资源。",
            "【战略视角】关于{topic}，领导力决定成败。",
            "【战略视角】{topic}需要系统性的顶层设计。",
        ],
    },
    "天府": {
        "prefix": "稳健分析：",
        "style": "稳健、风险控制导向",
        "sentiment_modifier": 0.05,
        "example_templates": [
            "稳健分析：{topic}的风险与机遇并存。",
            "稳健分析：关于{topic}，建议审慎评估。",
            "稳健分析：{topic}需要长期观察。",
        ],
    },
    "贪狼": {
        "prefix": "🔥",
        "style": "激进、机遇导向",
        "sentiment_modifier": 0.15,
        "example_templates": [
            "🔥 {topic} 机遇解读，抓住先机！",
            "🔥 {topic} 的窗口期就在当下！",
            "🔥 挑战{topic}，共赢未来！",
        ],
    },
    "太阴": {
        "prefix": "💫",
        "style": "细腻、情感导向",
        "sentiment_modifier": 0.15,
        "example_templates": [
            "💫 从情感角度看{topic}...",
            "💫 {topic}中的人情冷暖。",
            "💫 关注{topic}背后的情感需求。",
        ],
    },
    "天机": {
        "prefix": "💡",
        "style": "灵活、创新导向",
        "sentiment_modifier": 0.0,
        "example_templates": [
            "💡 {topic}的创新思维...",
            "💡 换个角度看{topic}...",
            "💡 {topic}中的智慧启示。",
        ],
    },
    "太阳": {
        "prefix": "☀️",
        "style": "热情、社会导向",
        "sentiment_modifier": 0.1,
        "example_templates": [
            "☀️ {topic}的正能量传递！",
            "☀️ 关于{topic}，光明磊落。",
            "☀️ {topic}照亮前行之路。",
        ],
    },
    "天同": {
        "prefix": "🌟",
        "style": "平和、享乐导向",
        "sentiment_modifier": 0.2,
        "example_templates": [
            "🌟 {topic}中的小确幸...",
            "🌟 享受{topic}的美好时光。",
            "🌟 {topic}带来的幸福感。",
        ],
    },
    "武曲": {
        "prefix": "💰",
        "style": "务实、财务导向",
        "sentiment_modifier": -0.05,
        "example_templates": [
            "💰 {topic}的实际收益分析。",
            "💰 务实看待{topic}。",
            "💰 {topic}的性价比考量。",
        ],
    },
    "廉贞": {
        "prefix": "⚡",
        "style": "尖锐、争议导向",
        "sentiment_modifier": -0.1,
        "example_templates": [
            "⚡ 必须直面{topic}的问题！",
            "⚡ {topic}中的灰色地带。",
            "⚡ 揭开{topic}的真相。",
        ],
    },
    "破军": {
        "prefix": "💥",
        "style": "激进、变革导向",
        "sentiment_modifier": -0.05,
        "example_templates": [
            "💥 {topic}需要破旧立新！",
            "💥 风险与机遇并存的{topic}。",
            "💥 突破{topic}的常规思维。",
        ],
    },
    "巨门": {
        "prefix": "🔍",
        "style": "犀利、传播导向",
        "sentiment_modifier": -0.15,
        "example_templates": [
            "🔍 深度剖析{topic}...",
            "🔍 {topic}背后的逻辑。",
            "🔍 真相只有一个：{topic}。",
        ],
    },
    "七杀": {
        "prefix": "⚔️",
        "style": "强势、竞争导向",
        "sentiment_modifier": -0.1,
        "example_templates": [
            "⚔️ {topic}的竞争格局。",
            "⚔️ 强者生存：{topic}。",
            "⚔️ {topic}中的挑战与应对。",
        ],
    },
}

REDDIT_CONTENT_RULES: Dict[str, Dict[str, str]] = {
    "紫微": {
        "prefix": "作为一个领导力研究者",
        "style": "权威分析、学术性",
        "sentiment_modifier": 0.1,
        "example_templates": [
            "作为一个领导力研究者，关于{topic}的深度分析...",
            "从战略管理角度，我如何看待{topic}...",
            "领导力视角下的{topic}探讨。",
        ],
    },
    "天府": {
        "prefix": "长期投资者视角：",
        "style": "稳健分析、数据导向",
        "sentiment_modifier": 0.05,
        "example_templates": [
            "长期投资者视角：{topic}的持久价值...",
            "作为稳健型投资者，关于{topic}的一些思考...",
            "从资产配置角度看{topic}。",
        ],
    },
    "贪狼": {
        "prefix": "争议观点：",
        "style": "激进、挑战常规",
        "sentiment_modifier": 0.15,
        "example_templates": [
            "关于{topic}的争议：我的不同看法...",
            "挑战传统观点：{topic}应该如何重新定义...",
            "我的{topic}研究可能会让你意外...",
        ],
    },
    "太阴": {
        "prefix": "情感专家角度：",
        "style": "细腻、人文关怀",
        "sentiment_modifier": 0.15,
        "example_templates": [
            "情感专家角度：{topic}如何影响人际关系...",
            "从心理学角度看{topic}...",
            "在{topic}中寻找情感共鸣。",
        ],
    },
    "天机": {
        "prefix": "创新思维：",
        "style": "灵活、多元视角",
        "sentiment_modifier": 0.0,
        "example_templates": [
            "天机星的独特视角：{topic}的创新解法...",
            "打破常规：{topic}的新思路...",
            "科技与人文的交叉点：{topic}。",
        ],
    },
    "太阳": {
        "prefix": "公益倡导者：",
        "style": "热情、社会责任",
        "sentiment_modifier": 0.1,
        "example_templates": [
            "公益倡导者：{topic}的社会意义...",
            "让世界更美好：关于{topic}的倡议...",
            "社会责任视角下的{topic}探讨。",
        ],
    },
    "天同": {
        "prefix": "生活美学：",
        "style": "平和、生活品质",
        "sentiment_modifier": 0.2,
        "example_templates": [
            "生活美学：{topic}中的幸福感...",
            "享受生活：{topic}的小确幸...",
            "从生活品质角度看{topic}。",
        ],
    },
    "武曲": {
        "prefix": "商业分析：",
        "style": "务实、商业逻辑",
        "sentiment_modifier": -0.05,
        "example_templates": [
            "商业分析：{topic}的经济效益...",
            "ROI视角：{topic}的投入产出...",
            "务实商业决策：{topic}评估。",
        ],
    },
    "廉贞": {
        "prefix": "道德伦理讨论：",
        "style": "尖锐、批判性",
        "sentiment_modifier": -0.1,
        "example_templates": [
            "道德伦理讨论：{topic}的正确与否...",
            "争议话题：关于{topic}的不同声音...",
            "直面{topic}的阴暗面。",
        ],
    },
    "破军": {
        "prefix": "变革先锋：",
        "style": "激进、突破性",
        "sentiment_modifier": -0.05,
        "example_templates": [
            "变革先锋：{topic}的破局之道...",
            "创新还是破坏？{topic}的双面性...",
            "突破常规：{topic}的未来展望。",
        ],
    },
    "巨门": {
        "prefix": "深度调查：",
        "style": "犀利、信息挖掘",
        "sentiment_modifier": -0.15,
        "example_templates": [
            "深度调查：揭开{topic}的真相...",
            "信息分析：{topic}的完整图景...",
            "逻辑推理：{topic}背后的规律。",
        ],
    },
    "七杀": {
        "prefix": "竞争策略：",
        "style": "强势、战略思维",
        "sentiment_modifier": -0.1,
        "example_templates": [
            "竞争策略：{topic}中的制胜之道...",
            "强者思维：如何在{topic}中胜出...",
            "战略分析：{topic}的竞争格局。",
        ],
    },
}

# 平台话题
PLATFORM_TOPICS = [
    "事业发展方向",
    "财务投资策略",
    "人际关系处理",
    "健康生活方式",
    "家庭责任分担",
    "学业进修计划",
    "退休养老安排",
    "创业创新机遇",
    "社会责任担当",
    "心理健康维护",
]


# ============ 核心模拟器 ============

class PlatformSimulator:
    """
    社交媒体平台模拟器

    模拟 Twitter/Reddit 风格的社交媒体平台互动。
    支持内容生成、互动模拟、话题追踪等功能。
    """

    def __init__(
        self,
        platform_type: PlatformType,
        agents: List[MetaphysicsAgent],
        interaction_engine: SocialInteractionEngine,
    ):
        """
        初始化平台模拟器

        Args:
            platform_type: 平台类型（Twitter/Reddit）
            agents: Agent 列表
            interaction_engine: 社交互动引擎
        """
        self.platform_type = platform_type
        self.agents = {agent.id: agent for agent in agents}
        self.agents_by_palace: Dict[str, MetaphysicsAgent] = {
            agent.persona.palace_name: agent for agent in agents
        }
        self.interaction_engine = interaction_engine

        # 帖子和评论
        self.posts: List[Post] = []
        self.comments: List[Comment] = []

        # 用户参与度
        self.user_engagement: Dict[str, EngagementMetrics] = {
            agent.persona.palace_name: EngagementMetrics(user_id=agent.persona.palace_name)
            for agent in agents
        }

        # 话题追踪
        self.topics: Dict[str, Topic] = {
            topic: Topic(name=topic) for topic in PLATFORM_TOPICS
        }

        # 平台特定参数
        self._init_platform_params()

    def _init_platform_params(self) -> None:
        """初始化平台特定参数"""
        if self.platform_type == PlatformType.TWITTER:
            self.max_content_length = 280
            self.viral_threshold = 50  # 转发数阈值
            self.retweet_weight = 3.0
            self.like_weight = 1.0
            self.comment_weight = 2.0
            self.content_rules = TWITTER_CONTENT_RULES
            self.interaction_delay = 0.1  # 低延迟，即时互动
        else:  # REDDIT
            self.max_content_length = 10000  # Reddit 长帖
            self.viral_threshold = 20  # upvote 阈值
            self.upvote_weight = 2.0
            self.downvote_weight = 1.0
            self.comment_weight = 3.0
            self.content_rules = REDDIT_CONTENT_RULES
            self.interaction_delay = 0.3  # Reddit 讨论延迟更高

    def _get_agent_primary_star(self, palace: str) -> str:
        """获取 Agent 的主星"""
        agent = self.agents_by_palace.get(palace)
        if not agent or not agent.persona.stars:
            return "天同"
        return agent.persona.stars[0]

    def _generate_content(
        self,
        palace: str,
        topic: str,
        sentiment: float,
    ) -> str:
        """生成平台特定内容"""
        primary_star = self._get_agent_primary_star(palace)
        rules = self.content_rules.get(primary_star, self.content_rules["天同"])

        templates = rules.get("example_templates", [])
        if not templates:
            return f"关于{topic}的观点：命盘显示相关机遇。"

        template = random.choice(templates)
        content = template.format(topic=topic)

        # 根据情感调整
        if sentiment < 0:
            content = content.replace("机遇", "挑战").replace("美好", "困难")

        # 平台特定截断
        if len(content) > self.max_content_length:
            content = content[:self.max_content_length - 3] + "..."

        return content

    async def simulate_round(self, round_num: int) -> RoundResult:
        """
        模拟一轮平台互动

        Args:
            round_num: 轮次编号

        Returns:
            轮次模拟结果
        """
        new_posts: List[Post] = []
        new_comments: List[Comment] = []
        engagement_events: List[Dict[str, Any]] = []

        # 1. Agent 生成内容
        posts = await self._generate_agent_posts(round_num)
        new_posts.extend(posts)

        # 2. 发布到平台
        self.posts.extend(new_posts)

        # 3. 其他 Agent 互动（点赞、转发/投票、评论）
        for post in new_posts:
            interactions = await self._simulate_post_interactions(post, round_num)
            engagement_events.extend(interactions)

        # 4. 计算传播和更新指标
        self._update_platform_metrics()

        # 5. 更新热门话题
        self._update_trending_topics()

        # 6. 获取结果
        trending = self.get_trending_topics()

        return RoundResult(
            round_num=round_num,
            new_posts=new_posts,
            new_comments=new_comments,
            engagement_events=engagement_events,
            trending_topics=trending,
            platform_metrics=self.get_platform_metrics(),
        )

    async def _generate_agent_posts(self, round_num: int) -> List[Post]:
        """生成 Agent 发布的帖子"""
        posts: List[Post] = []

        # 选择 1-3 个 Agent 发帖
        palaces = list(self.agents_by_palace.keys())
        num_posters = min(len(palaces), random.randint(1, 3))
        selected_palaces = random.sample(palaces, num_posters)

        for palace in selected_palaces:
            agent = self.agents_by_palace.get(palace)
            if not agent:
                continue

            # 选择话题（基于 Agent 擅长的话题）
            topic = self._select_topic_for_agent(agent)

            # 计算情感
            sentiment = self._calculate_post_sentiment(agent, topic)

            # 生成内容
            content = self._generate_content(palace, topic, sentiment)

            # 创建帖子
            post = Post(
                post_id=f"post_{uuid.uuid4().hex[:8]}",
                author_palace=palace,
                content=content,
                topic=topic,
                sentiment=sentiment,
                timestamp=datetime.now(),
            )

            posts.append(post)

            # 更新用户指标
            if palace in self.user_engagement:
                self.user_engagement[palace].posts_count += 1

        return posts

    def _select_topic_for_agent(self, agent: MetaphysicsAgent) -> str:
        """为 Agent 选择话题"""
        primary_star = agent.persona.stars[0] if agent.persona.stars else "天同"

        # 星曜擅长的话题
        star_topics: Dict[str, List[str]] = {
            "紫微": ["事业发展方向", "社会责任担当"],
            "天府": ["财务投资策略", "退休养老安排"],
            "贪狼": ["创业创新机遇", "人际关系处理"],
            "太阴": ["家庭责任分担", "心理健康维护"],
            "天机": ["学业进修计划", "创业创新机遇"],
            "太阳": ["社会责任担当", "事业发展方向"],
            "天同": ["健康生活方式", "家庭责任分担"],
            "武曲": ["财务投资策略", "退休养老安排"],
            "廉贞": ["人际关系处理", "心理健康维护"],
            "破军": ["创业创新机遇", "事业发展方向"],
            "巨门": ["人际关系处理", "学业进修计划"],
            "七杀": ["创业创新机遇", "事业发展方向"],
        }

        preferred_topics = star_topics.get(primary_star, [])

        # 优先选择擅长的话题
        if preferred_topics and random.random() < 0.7:
            return random.choice(preferred_topics)

        return random.choice(PLATFORM_TOPICS)

    def _calculate_post_sentiment(self, agent: MetaphysicsAgent, topic: str) -> float:
        """计算帖子情感"""
        # 基于四化计算基础情感
        transforms = agent.persona.transforms
        base_sentiment = 0.0

        for transform in transforms:
            if transform == "化禄":
                base_sentiment += 0.3
            elif transform == "化权":
                base_sentiment += 0.1
            elif transform == "化科":
                base_sentiment += 0.05
            elif transform == "化忌":
                base_sentiment -= 0.2

        # 添加随机波动
        sentiment = base_sentiment + random.uniform(-0.1, 0.1)
        return max(-1.0, min(1.0, sentiment))

    async def _simulate_post_interactions(
        self,
        post: Post,
        round_num: int,
    ) -> List[Dict[str, Any]]:
        """模拟帖子的互动（点赞、转发、评论）"""
        events: List[Dict[str, Any]] = []

        # 其他 Agent 互动
        other_palaces = [
            p for p in self.agents_by_palace.keys()
            if p != post.author_palace
        ]

        if not other_palaces:
            return events

        # 随机选择互动者
        num_interactors = random.randint(1, min(3, len(other_palaces)))
        interactors = random.sample(other_palaces, num_interactors)

        for palace in interactors:
            agent = self.agents_by_palace.get(palace)
            if not agent:
                continue

            # 计算互动概率
            interaction_prob = self._calculate_interaction_probability(
                agent=agent,
                post=post,
            )

            if random.random() > interaction_prob:
                continue

            # 决定互动类型
            if self.platform_type == PlatformType.TWITTER:
                event = await self._simulate_twitter_interaction(
                    agent=agent,
                    post=post,
                    palace=palace,
                    round_num=round_num,
                )
            else:
                event = await self._simulate_reddit_interaction(
                    agent=agent,
                    post=post,
                    palace=palace,
                    round_num=round_num,
                )

            if event:
                events.append(event)

        return events

    def _calculate_interaction_probability(
        self,
        agent: MetaphysicsAgent,
        post: Post,
    ) -> float:
        """计算互动概率"""
        # 基础概率
        base_prob = 0.3

        # 根据情感差异调整（差异越大，可能越想评论）
        post_sentiment = post.sentiment
        agent_opinion = self._get_agent_opinion(agent, post.topic)

        if agent_opinion is not None:
            sentiment_diff = abs(agent_opinion - post_sentiment)
            if sentiment_diff > 0.5:
                base_prob += 0.2  # 观点差异大，更可能互动

        # 根据 Agent 社交分数调整
        social_score = agent.state.social if hasattr(agent.state, 'social') else 0.5
        base_prob *= (0.5 + social_score)

        # Reddit 互动概率稍低（更倾向于深思熟虑）
        if self.platform_type == PlatformType.REDDIT:
            base_prob *= 0.7

        return min(0.9, max(0.1, base_prob))

    def _get_agent_opinion(self, agent: MetaphysicsAgent, topic: str) -> Optional[float]:
        """获取 Agent 对某话题的观点"""
        palace = agent.persona.palace_name
        opinions = self.interaction_engine.get_opinions_state()
        return opinions.get(palace, {}).get(topic)

    async def _simulate_twitter_interaction(
        self,
        agent: MetaphysicsAgent,
        post: Post,
        palace: str,
        round_num: int,
    ) -> Optional[Dict[str, Any]]:
        """模拟 Twitter 互动"""
        event: Dict[str, Any] = {
            "round_num": round_num,
            "post_id": post.post_id,
            "interactor_palace": palace,
        }

        # 决定互动类型
        roll = random.random()
        abs(agent.state.mood - 0.5) if hasattr(agent.state, 'mood') else 0

        if roll < 0.5:
            # 点赞 (50%)
            post.likes += 1
            self.user_engagement[palace].likes_given += 1
            self.user_engagement[post.author_palace].likes_received += 1
            event["type"] = "like"
            event["sentiment"] = post.sentiment

        elif roll < 0.8:
            # 转发 (30%)
            post.retweets += 1
            self.user_engagement[palace].retweets_given += 1
            self.user_engagement[post.author_palace].retweets_received += 1
            event["type"] = "retweet"
            event["sentiment"] = post.sentiment

            # 转发可能增加情感放大
            if post.sentiment > 0:
                post.viral_reach += random.randint(10, 50)
            else:
                post.viral_reach += random.randint(5, 20)

        else:
            # 评论 (20%)
            comment = self._generate_twitter_comment(agent, post)
            post.comments += 1
            self.comments.append(comment)

            self.user_engagement[palace].comments_given += 1
            self.user_engagement[post.author_palace].comments_received += 1

            event["type"] = "comment"
            event["comment"] = comment.to_dict()
            event["sentiment"] = comment.sentiment

        # 更新帖子指标
        post.engagement_score = post.calculate_engagement()
        post.viral_reach = post.calculate_viral_reach()

        return event

    async def _simulate_reddit_interaction(
        self,
        agent: MetaphysicsAgent,
        post: Post,
        palace: str,
        round_num: int,
    ) -> Optional[Dict[str, Any]]:
        """模拟 Reddit 互动"""
        event: Dict[str, Any] = {
            "round_num": round_num,
            "post_id": post.post_id,
            "interactor_palace": palace,
        }

        # Reddit 更多是评论和投票
        roll = random.random()

        if roll < 0.3:
            # Upvote (30%)
            post.upvotes += 1
            self.user_engagement[palace].upvotes_given += 1
            self.user_engagement[post.author_palace].upvotes_received += 1
            event["type"] = "upvote"
            event["sentiment"] = 1.0

        elif roll < 0.4:
            # Downvote (10%)
            post.downvotes += 1
            event["type"] = "downvote"
            event["sentiment"] = -1.0

        else:
            # 评论 (60%) - Reddit 更注重讨论
            comment = self._generate_reddit_comment(agent, post)
            post.comments += 1
            self.comments.append(comment)

            self.user_engagement[palace].comments_given += 1
            self.user_engagement[post.author_palace].comments_received += 1

            event["type"] = "comment"
            event["comment"] = comment.to_dict()
            event["sentiment"] = comment.sentiment

        # 更新帖子指标
        post.engagement_score = post.upvotes + post.comments * 2 - post.downvotes

        return event

    def _generate_twitter_comment(self, agent: MetaphysicsAgent, post: Post) -> Comment:
        """生成 Twitter 评论"""
        primary_star = agent.persona.stars[0] if agent.persona.stars else "天同"

        templates = [
            "有道理，支持！",
            "值得深思...",
            "这观点我不太认同",
            "分析得很到位",
            "补充一点看法...",
        ]

        comment_templates = {
            "紫微": "从领导力角度看...",
            "天府": "稳健考虑很重要",
            "贪狼": "机会稍纵即逝！",
            "太阴": "情感层面需要关注",
            "化忌": "这个担忧很有道理",
        }

        prefix = comment_templates.get(primary_star, "")
        base_comment = random.choice(templates)
        content = f"{prefix} {base_comment}" if prefix else base_comment

        return Comment(
            comment_id=f"cmt_{uuid.uuid4().hex[:8]}",
            post_id=post.post_id,
            author_palace=agent.persona.palace_name,
            content=content,
            sentiment=-post.sentiment * 0.5 if random.random() < 0.3 else post.sentiment * 0.8,
        )

    def _generate_reddit_comment(self, agent: MetaphysicsAgent, post: Post) -> Comment:
        """生成 Reddit 评论（更长、更详细）"""
        agent.persona.stars[0] if agent.persona.stars else "天同"

        templates = [
            "作为一个长期关注这个话题的人，我想分享一些看法...",
            "深入分析一下这个问题：",
            "我认为这个观点需要更多证据支持...",
            "从多个角度来看，这确实是一个复杂的话题...",
            "根据我的经验，这个问题需要分情况讨论...",
        ]

        topic_templates = {
            "事业发展方向": "关于职业发展，我建议从长期规划的角度思考...",
            "财务投资策略": "分散投资是降低风险的关键...",
            "人际关系处理": "沟通是建立信任的基础...",
            "健康生活方式": "保持良好的作息对身心健康都很重要...",
        }

        topic_prefix = topic_templates.get(post.topic, "")
        base_comment = random.choice(templates)
        content = f"{topic_prefix} {base_comment}" if topic_prefix else base_comment

        return Comment(
            comment_id=f"cmt_{uuid.uuid4().hex[:8]}",
            post_id=post.post_id,
            author_palace=agent.persona.palace_name,
            content=content,
            sentiment=-post.sentiment * 0.3 if random.random() < 0.2 else post.sentiment * 0.7,
        )

    def _update_platform_metrics(self) -> None:
        """更新平台指标"""
        for palace, metrics in self.user_engagement.items():
            metrics.total_engagement_score = (
                metrics.likes_received * 1.0 +
                metrics.retweets_received * 3.0 +
                metrics.comments_received * 2.0 +
                metrics.upvotes_received * 2.0
            )

    def _update_trending_topics(self) -> None:
        """更新热门话题"""
        for topic in self.topics.values():
            topic.update_trending_score(self.posts)

    def get_trending_topics(self, limit: int = 5) -> List[Topic]:
        """
        获取热门话题

        Args:
            limit: 返回数量限制

        Returns:
            热门话题列表（按 trending_score 降序）
        """
        trending = sorted(
            self.topics.values(),
            key=lambda t: t.trending_score,
            reverse=True,
        )
        return trending[:limit]

    def calculate_viral_score(self, post: Post) -> float:
        """
        计算帖子病毒传播分数

        Args:
            post: 帖子对象

        Returns:
            病毒传播分数
        """
        if self.platform_type == PlatformType.TWITTER:
            # Twitter: 转发权重高
            base_score = (
                post.likes * 1.0 +
                post.retweets * 5.0 +
                post.comments * 2.0
            )
            # 情感强度加成
            sentiment_boost = abs(post.sentiment) * 1.5
            return base_score * (1 + sentiment_boost)

        else:
            # Reddit: upvote 权重高
            net_votes = post.upvotes - post.downvotes
            base_score = net_votes * 2.0 + post.comments * 3.0
            # Reddit 算法
            score = math.log10(max(1, abs(net_votes))) * (1 if net_votes > 0 else -1)
            return base_score + score * 10

    def get_agent_feed(
        self,
        agent: MetaphysicsAgent,
        limit: int = 20,
    ) -> List[Post]:
        """
        获取 Agent 的信息流

        Args:
            agent: Agent 对象
            limit: 返回数量限制

        Returns:
            信息流帖子列表
        """
        palace = agent.persona.palace_name

        # 获取相关话题的帖子
        relevant_topics = self._get_relevant_topics_for_agent(agent)

        # 过滤和排序
        feed_posts = [
            p for p in self.posts
            if p.topic in relevant_topics and p.author_palace != palace
        ]

        # 按互动分数和新鲜度排序
        feed_posts.sort(
            key=lambda p: (p.engagement_score + p.calculate_viral_reach() * 0.1),
            reverse=True,
        )

        return feed_posts[:limit]

    def _get_relevant_topics_for_agent(self, agent: MetaphysicsAgent) -> Set[str]:
        """获取 Agent 相关的话题集合"""
        primary_star = agent.persona.stars[0] if agent.persona.stars else "天同"

        star_topics: Dict[str, List[str]] = {
            "紫微": ["事业发展方向", "社会责任担当", "人际关系处理"],
            "天府": ["财务投资策略", "退休养老安排", "健康生活方式"],
            "贪狼": ["创业创新机遇", "人际关系处理", "事业发展方向"],
            "太阴": ["家庭责任分担", "心理健康维护", "人际关系处理"],
            "天机": ["学业进修计划", "创业创新机遇", "健康生活方式"],
            "太阳": ["社会责任担当", "事业发展方向", "人际关系处理"],
            "天同": ["健康生活方式", "家庭责任分担", "心理健康维护"],
            "武曲": ["财务投资策略", "退休养老安排", "创业创新机遇"],
            "廉贞": ["人际关系处理", "心理健康维护", "社会责任担当"],
            "破军": ["创业创新机遇", "事业发展方向", "财务投资策略"],
            "巨门": ["人际关系处理", "学业进修计划", "社会责任担当"],
            "七杀": ["创业创新机遇", "事业发展方向", "人际关系处理"],
        }

        return set(star_topics.get(primary_star, PLATFORM_TOPICS[:3]))

    def get_platform_metrics(self) -> Dict[str, Any]:
        """获取平台指标"""
        total_posts = len(self.posts)
        total_comments = len(self.comments)

        if self.platform_type == PlatformType.TWITTER:
            total_likes = sum(p.likes for p in self.posts)
            total_retweets = sum(p.retweets for p in self.posts)
            engagement_rate = (
                (total_likes + total_retweets + total_comments) / max(1, total_posts)
            )
        else:
            total_upvotes = sum(p.upvotes for p in self.posts)
            sum(p.downvotes for p in self.posts)
            engagement_rate = (
                (total_upvotes + total_comments) / max(1, total_posts)
            )

        return {
            "platform_type": self.platform_type.value,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_engagement_rate": round(engagement_rate, 3),
            "active_users": len([m for m in self.user_engagement.values() if m.posts_count > 0]),
            "trending_score": sum(t.trending_score for t in self.topics.values()),
        }

    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        """根据 ID 获取帖子"""
        for post in self.posts:
            if post.post_id == post_id:
                return post
        return None

    def get_comments_for_post(self, post_id: str) -> List[Comment]:
        """获取帖子的所有评论"""
        return [c for c in self.comments if c.post_id == post_id]

    def get_user_engagement(self, palace: str) -> Optional[EngagementMetrics]:
        """获取用户参与度指标"""
        return self.user_engagement.get(palace)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "platform_type": self.platform_type.value,
            "total_posts": len(self.posts),
            "total_comments": len(self.comments),
            "metrics": self.get_platform_metrics(),
            "trending_topics": [
                {"name": t.name, "score": round(t.trending_score, 2)}
                for t in self.get_trending_topics()
            ],
            "user_engagements": {
                palace: metrics.to_dict()
                for palace, metrics in self.user_engagement.items()
            },
        }


# ============ 便捷函数 ============

def create_platform_simulator(
    platform_type: PlatformType,
    agents: List[MetaphysicsAgent],
    interaction_engine: SocialInteractionEngine,
) -> PlatformSimulator:
    """
    创建平台模拟器

    Args:
        platform_type: 平台类型
        agents: Agent 列表
        interaction_engine: 社交互动引擎

    Returns:
        PlatformSimulator 实例
    """
    return PlatformSimulator(
        platform_type=platform_type,
        agents=agents,
        interaction_engine=interaction_engine,
    )


def create_dual_platform_simulation(
    agents: List[MetaphysicsAgent],
    interaction_engine: SocialInteractionEngine,
) -> Dict[str, PlatformSimulator]:
    """
    创建双平台模拟（Twitter + Reddit）

    Args:
        agents: Agent 列表
        interaction_engine: 社交互动引擎

    Returns:
        {平台类型: 模拟器} 字典
    """
    return {
        "twitter": PlatformSimulator(
            platform_type=PlatformType.TWITTER,
            agents=agents,
            interaction_engine=interaction_engine,
        ),
        "reddit": PlatformSimulator(
            platform_type=PlatformType.REDDIT,
            agents=agents,
            interaction_engine=interaction_engine,
        ),
    }
