"""
ContentGenerator - 内容生成器

根据命盘特征和星曜生成社交媒体内容:
- 基于星曜特性生成风格化内容
- 适配不同平台的内容长度规则
- 支持批量内容生成

依赖:
- agents.py: MetaphysicsAgent
- scenarios.py: MetaphysicsScenario (alias for Scenario)
- social_media.py: PlatformType
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
import random
import uuid

# 避免循环导入
if TYPE_CHECKING:
    from ..agents import MetaphysicsAgent
    from ..scenarios import Scenario

from .social_media import PlatformType


# ============ 数据模型 ============

@dataclass
class ContentItem:
    """内容项数据模型"""
    content_id: str
    agent_palace: str
    platform: PlatformType
    content: str
    topic: str
    sentiment: float  # -1.0 ~ 1.0
    style_tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content_id": self.content_id,
            "agent_palace": self.agent_palace,
            "platform": self.platform.value,
            "content": self.content,
            "topic": self.topic,
            "sentiment": round(self.sentiment, 3),
            "style_tags": self.style_tags,
            "metadata": self.metadata,
        }


# ============ 星曜→内容风格映射 ============

STAR_CONTENT_STYLES: Dict[str, Dict[str, Any]] = {
    "紫微": {
        "twitter": "【领导力视角】{topic}",
        "reddit": "作为团队管理者，关于{topic}的深度思考",
        "tone": "权威",
        "topics": ["战略决策", "团队管理", "资源整合"],
        "emoji": "\U0001F3AF",  # 🎯
    },
    "天府": {
        "twitter": "稳健分析 | {topic}",
        "reddit": "长期价值投资者视角：{topic}",
        "tone": "稳健",
        "topics": ["风险控制", "资产配置", "长期规划"],
        "emoji": "\U0001F4B0",  # 💰
    },
    "贪狼": {
        "twitter": "🔥 {topic} | 机遇与挑战",
        "reddit": "激进派视角：{topic}，我的不同解读",
        "tone": "激进",
        "topics": ["创业机会", "竞争策略", "突破点"],
        "emoji": "\U0001F525",  # 🔥
    },
    "太阴": {
        "twitter": "💫 从心出发 | {topic}",
        "reddit": "情感与生活：{topic}的深层意义",
        "tone": "细腻",
        "topics": ["人际关系", "家庭生活", "情感沟通"],
        "emoji": "\U0001F4AB",  # 💫
    },
    "天机": {
        "twitter": "💡 智慧解析 | {topic}",
        "reddit": "深度分析：{topic}的底层逻辑",
        "tone": "智慧",
        "topics": ["学习方法", "思维模式", "创新思路"],
        "emoji": "\U0001F4A1",  # 💡
    },
    "武曲": {
        "twitter": "💰 财商视角 | {topic}",
        "reddit": "投资者日记：{topic}的实际考量",
        "tone": "务实",
        "topics": ["投资理财", "商业决策", "价值评估"],
        "emoji": "\U0001F4B8",  # 💸
    },
    "太阳": {
        "twitter": "☀️ 公共视野 | {topic}",
        "reddit": "社会责任角度：{topic}的群体影响",
        "tone": "热情",
        "topics": ["社会热点", "公众议题", "影响力"],
        "emoji": "\U00002600",  # ☀️
    },
    "巨门": {
        "twitter": "🔍 深度挖掘 | {topic}",
        "reddit": "争议话题：{topic}的多面性分析",
        "tone": "批判",
        "topics": ["舆论分析", "真相挖掘", "深度报道"],
        "emoji": "\U0001F50D",  # 🔍
    },
    "天同": {
        "twitter": "🌊 平和观点 | {topic}",
        "reddit": "生活化视角：{topic}的日常意义",
        "tone": "平和",
        "topics": ["生活方式", "工作生活平衡", "幸福感"],
        "emoji": "\U0001F30A",  # 🌊
    },
    "天梁": {
        "twitter": "🛡️ 风险提示 | {topic}",
        "reddit": "风控专家：{topic}中需要注意的问题",
        "tone": "稳健",
        "topics": ["风险评估", "问题预防", "长期安全"],
        "emoji": "\U0001F6E1",  # 🛡️
    },
    "廉贞": {
        "twitter": "⚡ 直击要害 | {topic}",
        "reddit": "道德探讨：{topic}的边界与底线",
        "tone": "尖锐",
        "topics": ["伦理讨论", "争议焦点", "规则边界"],
        "emoji": "\U000026A1",  # ⚡
    },
    "破军": {
        "twitter": "💥 破局时刻 | {topic}",
        "reddit": "变革者视角：{topic}的重新定义",
        "tone": "激进",
        "topics": ["创新突破", "变革管理", "风险管理"],
        "emoji": "\U0001F4A5",  # 💥
    },
    "七杀": {
        "twitter": "⚔️ 竞争格局 | {topic}",
        "reddit": "强者思维：{topic}的制胜策略",
        "tone": "强势",
        "topics": ["竞争分析", "战略部署", "实力证明"],
        "emoji": "\u2694\uFE0F",  # ⚔️
    },
    "文昌": {
        "twitter": "📚 学以致用 | {topic}",
        "reddit": "学业进阶：{topic}的深度研究",
        "tone": "严谨",
        "topics": ["考试技巧", "学习方法", "知识积累"],
        "emoji": "\U0001F4DA",  # 📚
    },
    "文曲": {
        "twitter": "🎨 文艺视角 | {topic}",
        "reddit": "文化解读：{topic}的艺术表达",
        "tone": "文雅",
        "topics": ["文化创意", "艺术审美", "情感表达"],
        "emoji": "\U0001F3A8",  # 🎨
    },
}

# 默认星曜风格（用于未定义的星曜）
DEFAULT_STAR_STYLE = {
    "twitter": "{topic}",
    "reddit": "分享关于{topic}的看法",
    "tone": "中性",
    "topics": ["综合讨论"],
    "emoji": "\U0001F4AD",  # 💭
}


# ============ 话题模板 ============

SCENARIO_TOPICS: Dict[str, List[str]] = {
    "事业": ["职业发展", "创业机会", "团队协作", "领导力"],
    "财运": ["投资机会", "财务规划", "财富增长", "风险控制"],
    "感情": ["人际关系", "情感沟通", "家庭和睦", "单身脱单"],
    "健康": ["健康管理", "压力调适", "运动健身", "心理健康"],
    "学业": ["学习进步", "考试运", "教育资源", "技能提升"],
}

# 全局话题列表
GLOBAL_TOPICS = [
    "战略决策",
    "团队管理",
    "资源整合",
    "风险控制",
    "资产配置",
    "长期规划",
    "创业机会",
    "竞争策略",
    "突破点",
    "人际关系",
    "家庭生活",
    "情感沟通",
    "学习方法",
    "思维模式",
    "创新思路",
    "投资理财",
    "商业决策",
    "价值评估",
    "社会热点",
    "公众议题",
    "影响力",
    "舆论分析",
    "真相挖掘",
    "深度报道",
    "生活方式",
    "工作生活平衡",
    "幸福感",
    "风险评估",
    "问题预防",
    "长期安全",
]


# ============ 平台内容长度规则 ============

PLATFORM_LIMITS: Dict[PlatformType, Dict[str, Any]] = {
    PlatformType.TWITTER: {
        "min_length": 20,
        "max_length": 280,
        "hashtag_limit": 3,
        "emoji_limit": 2,
    },
    PlatformType.REDDIT: {
        "min_length": 200,
        "max_length": 40000,
        "section_required": True,
        "paragraph_limit": 10,
    },
}


# ============ 内容模板 ============

TWITTER_CONTENT_TEMPLATES: Dict[str, List[str]] = {
    "权威": [
        "从战略高度来看，{topic}是决定成败的关键。",
        "我们必须在{topic}上建立明确的标准和规范。",
        "领导力视角：{topic}需要系统性思维。",
    ],
    "稳健": [
        "对于{topic}，建议采取循序渐进的策略。",
        "稳健推进{topic}的发展才是长久之计。",
        "审慎评估{topic}的每个环节。",
    ],
    "务实": [
        "关注{topic}的实际效益比空谈更重要。",
        "数据告诉我们，{topic}需要务实的方法。",
        "从实际出发，{topic}的落地执行。",
    ],
    "激进": [
        "机会稍纵即逝，在{topic}上必须果断行动！",
        "市场竞争激烈，{topic}需要突破性思维。",
        "错过{topic}，就是错过时代红利。",
    ],
    "细腻": [
        "在{topic}的讨论中，我们应该更多关注细节。",
        "每个人的感受都值得被重视，尤其是在{topic}上。",
        "用心感受{topic}中的温度。",
    ],
    "智慧": [
        "换个角度看{topic}，或许会有新发现。",
        "创新的思路往往能打开{topic}的新局面。",
        "{topic}需要智慧的洞察力。",
    ],
    "热情": [
        "让更多人了解{topic}的重要性！",
        "积极传播{topic}的正能量！",
        "用热情点燃{topic}的讨论！",
    ],
    "批判": [
        "真相只有一个，关于{topic}我们需要更深入的思考。",
        "揭开{topic}背后的真实逻辑。",
        "理性分析{topic}的每个层面。",
    ],
    "平和": [
        "{topic}需要我们保持平和的心态。",
        "在{topic}上，不必太过焦虑。",
        "享受{topic}带来的每一个小确幸。",
    ],
    "强势": [
        "强者恒强，{topic}就是证明实力的战场。",
        "在{topic}上，没有退路。",
        "用实力说话，{topic}的竞争法则。",
    ],
    "尖锐": [
        "必须直面{topic}中的问题！",
        "对{topic}的虚伪说不。",
        "{topic}的灰色地带需要被照亮。",
    ],
    "文雅": [
        "品味{topic}中的文化内涵。",
        "从文化角度解读{topic}的意义。",
        "{topic}中的艺术之美。",
    ],
    "严谨": [
        "系统分析{topic}的每个环节。",
        "用科学方法研究{topic}的规律。",
        "严谨态度对待{topic}。",
    ],
    "中性": [
        "分享一个关于{topic}的观点。",
        "客观看待{topic}的不同面向。",
        "关于{topic}，欢迎讨论。",
    ],
}

REDDIT_CONTENT_TEMPLATES: Dict[str, List[str]] = {
    "权威": """作为一个长期关注战略管理领域的人，我想分享关于{topic}的深度分析：

{intro}

从我的经验来看，{topic}的关键在于：
1. 建立清晰的战略框架
2. 整合核心资源
3. 持续评估和调整

欢迎大家分享你们的看法。""",

    "稳健": """关于{topic}，作为一个稳健型投资者，我有一些思考想和大家分享：

【背景分析】
{intro}

【风险评估】
{topic}需要我们关注以下几个风险点：
- 市场波动风险
- 流动性风险
- 执行风险

【建议】
建议采取渐进式策略，不要急于求成。

你的看法是什么？""",

    "激进": """关于{topic}，我的观点可能和主流不太一样——

{intro}

我认为传统的思路已经过时了！理由如下：

1. 时代变了，环境变了
2. 新机会窗口正在打开
3. 观望者将被淘汰

挑战传统观点，欢迎来辩。""",

    "细腻": """在讨论{topic}时，我想从情感和人性的角度切入：

{intro}

很多人忽略了{topic}背后的情感因素：

- 人们对变化的恐惧
- 对未知的焦虑
- 对安全感的渴望

{topic}不仅仅是一个理性话题，更是一个关乎人心的话题。

你怎么看？""",

    "智慧": """深度分析：{topic}的底层逻辑

{intro}

【核心洞察】
{topic}的本质是什么？我认为：

第一性原理分析显示，{topic}涉及多个维度的交互作用。

【思维框架】
建议采用系统思维来理解{topic}。

【实践建议】
如何在日常生活中应用这些洞察？

期待看到更多元的观点。""",

    "热情": """关于{topic}，我真的很想大声疾呼——

{intro}

{topic}不应该被忽视！原因：

1. 影响数百万人的生活
2. 关乎社会长远发展
3. 每个人都应该参与讨论

让我们一起推动{topic}的积极发展！

你的热情在哪里？""",

    "批判": """揭开{topic}的真相（可能是你不愿面对的）

{intro}

经过深入调查，我发现{topic}存在以下问题：

【被忽视的真相】
...

【利益相关方】
...

【系统性风险】
...

这篇文章可能让人不舒服，但真相需要被说出来。

你怎么看？""",

    "平和": """聊聊{topic}这个话题（不争不吵，peace & love）

{intro}

最近在思考{topic}，心态平和了很多：

{topic}不是非黑即白的问题
每个观点都有其合理性
重要的是找到适合自己的平衡点

生活已经够累了，何必在{topic}上争个你死我活？

你的{topic}生活哲学是什么？""",

    "中性": """客观分析：{topic}的多面性

{intro}

【支持观点】
...

【反对观点】
...

【中立看法】
...

{topic}是一个复杂话题，需要多角度审视。

欢迎理性讨论！""",
}


# ============ 核心生成器 ============

class ContentGenerator:
    """
    基于命盘特征的内容生成器

    根据星曜特性、宫位角色和场景上下文生成社交媒体内容。
    支持 Twitter 和 Reddit 两大平台的内容适配。
    """

    def __init__(self, agents: List["MetaphysicsAgent"]):
        """
        初始化内容生成器

        Args:
            agents: MetaphysicsAgent 列表
        """
        self.agents = {agent.id: agent for agent in agents}
        self.agents_by_palace: Dict[str, MetaphysicsAgent] = {
            agent.persona.palace_name: agent for agent in agents
        }
        self.generated_content: List[ContentItem] = []
        self.content_counter = 0

    def _get_agent_primary_star(self, agent: "MetaphysicsAgent") -> str:
        """获取 Agent 的主星"""
        if agent.persona.stars:
            return agent.persona.stars[0]
        return "天同"

    def _get_star_style(self, star: str) -> Dict[str, Any]:
        """获取星曜风格配置"""
        return STAR_CONTENT_STYLES.get(star, DEFAULT_STAR_STYLE)

    def _select_topic_for_agent(
        self,
        agent: "MetaphysicsAgent",
        scenario: Optional["Scenario"] = None,
    ) -> str:
        """为 Agent 选择合适的话题"""
        primary_star = self._get_agent_primary_star(agent)
        star_style = self._get_star_style(primary_star)
        preferred_topics = star_style.get("topics", [])

        # 优先从星曜擅长的话题中选择
        if preferred_topics and random.random() < 0.7:
            return random.choice(preferred_topics)

        # 否则从全局话题中选择
        if random.random() < 0.3 and scenario:
            # 尝试从场景类型推断话题类别
            from ..scenarios import ScenarioType
            if hasattr(scenario, 'type'):
                if scenario.type == ScenarioType.OPPORTUNITY:
                    return random.choice(SCENARIO_TOPICS["财运"] + SCENARIO_TOPICS["事业"])
                elif scenario.type == ScenarioType.CHALLENGE:
                    return random.choice(SCENARIO_TOPICS["健康"] + SCENARIO_TOPICS["感情"])
                elif scenario.type == ScenarioType.COMPETITION:
                    return random.choice(SCENARIO_TOPICS["事业"])
                elif scenario.type == ScenarioType.REPUTATION:
                    return random.choice(SCENARIO_TOPICS["学业"])

        return random.choice(GLOBAL_TOPICS)

    def _calculate_sentiment(
        self,
        agent: "MetaphysicsAgent",
        topic: str,
    ) -> float:
        """计算内容情感值"""
        base_sentiment = 0.0

        # 基于四化计算基础情感
        transforms = agent.persona.transforms
        for transform in transforms:
            if transform == "化禄":
                base_sentiment += 0.3
            elif transform == "化权":
                base_sentiment += 0.1
            elif transform == "化科":
                base_sentiment += 0.05
            elif transform == "化忌":
                base_sentiment -= 0.2

        # 基于主星调整
        primary_star = self._get_agent_primary_star(agent)
        star_style = self._get_star_style(primary_star)
        tone = star_style.get("tone", "中性")

        tone_sentiment_adjustments = {
            "权威": 0.1,
            "稳健": 0.05,
            "务实": -0.05,
            "激进": 0.0,
            "细腻": 0.15,
            "智慧": 0.0,
            "热情": 0.1,
            "批判": -0.15,
            "平和": 0.2,
            "强势": -0.1,
            "尖锐": -0.1,
            "文雅": 0.1,
            "严谨": 0.05,
            "中性": 0.0,
        }
        base_sentiment += tone_sentiment_adjustments.get(tone, 0.0)

        # 添加随机波动
        sentiment = base_sentiment + random.uniform(-0.1, 0.1)
        return max(-1.0, min(1.0, sentiment))

    def _generate_twitter_content(
        self,
        agent: "MetaphysicsAgent",
        topic: str,
        sentiment: float,
    ) -> str:
        """生成 Twitter 风格内容"""
        primary_star = self._get_agent_primary_star(agent)
        star_style = self._get_star_style(primary_star)
        tone = star_style.get("tone", "中性")

        # 获取模板
        templates = TWITTER_CONTENT_TEMPLATES.get(tone, TWITTER_CONTENT_TEMPLATES["中性"])
        template = random.choice(templates)

        # 生成内容
        content = template.format(topic=topic)

        # 添加话题标签
        hashtag = f"#{topic.replace(' ', '')}"
        if random.random() < 0.5:
            content = f"{content} {hashtag}"

        # 根据情感调整
        if sentiment < 0:
            negative_replacements = {
                "机遇": "挑战",
                "机会": "风险",
                "成功": "困难",
                "发展": "停滞",
                "突破": "瓶颈",
            }
            for old, new in negative_replacements.items():
                if old in content:
                    content = content.replace(old, new)
                    break

        # 截断到限制长度
        limits = PLATFORM_LIMITS[PlatformType.TWITTER]
        if len(content) > limits["max_length"]:
            content = content[:limits["max_length"] - 3] + "..."

        return content

    def _generate_reddit_content(
        self,
        agent: "MetaphysicsAgent",
        topic: str,
        sentiment: float,
    ) -> str:
        """生成 Reddit 风格内容"""
        primary_star = self._get_agent_primary_star(agent)
        star_style = self._get_star_style(primary_star)
        tone = star_style.get("tone", "中性")

        # 获取模板
        template = REDDIT_CONTENT_TEMPLATES.get(tone, REDDIT_CONTENT_TEMPLATES["中性"])

        # 生成引言
        intros = [
            f"最近在思考关于{topic}的问题，有了一些新的认识。",
            f"{topic}一直是大家关心的话题，我也想分享一些看法。",
            f"关于{topic}，我的观点可能有些独特，欢迎指正。",
            f"深度探讨{topic}，希望能引发有价值的讨论。",
        ]
        intro = random.choice(intros)

        # 填充模板
        content = template.format(topic=topic, intro=intro)

        # 根据情感调整语气
        if sentiment < 0:
            content = content.replace("积极", "审慎").replace("乐观", "保守")

        return content

    def generate_for_agent(
        self,
        agent: "MetaphysicsAgent",
        scenario: Optional["Scenario"],
        topic: str,
        platform: PlatformType,
    ) -> ContentItem:
        """
        为指定 Agent 生成内容

        Args:
            agent: 目标 Agent
            scenario: 场景上下文（可选）
            topic: 指定话题（可选，将根据 Agent 自动选择）
            platform: 目标平台

        Returns:
            生成的 ContentItem
        """
        self.content_counter += 1

        # 选择话题
        if not topic:
            topic = self._select_topic_for_agent(agent, scenario)

        # 计算情感
        sentiment = self._calculate_sentiment(agent, topic)

        # 生成内容
        if platform == PlatformType.TWITTER:
            content = self._generate_twitter_content(agent, topic, sentiment)
        else:
            content = self._generate_reddit_content(agent, topic, sentiment)

        # 获取星曜风格标签
        primary_star = self._get_agent_primary_star(agent)
        star_style = self._get_star_style(primary_star)
        style_tags = [star_style.get("tone", "中性"), primary_star]

        # 创建内容项
        content_item = ContentItem(
            content_id=f"content_{uuid.uuid4().hex[:8]}",
            agent_palace=agent.persona.palace_name,
            platform=platform,
            content=content,
            topic=topic,
            sentiment=sentiment,
            style_tags=style_tags,
            metadata={
                "primary_star": primary_star,
                "agent_id": agent.id,
                "scenario_type": scenario.type.value if scenario and hasattr(scenario, 'type') else None,
                "transforms": agent.persona.transforms,
                "generated_at": datetime.now().isoformat(),
            },
        )

        self.generated_content.append(content_item)
        return content_item

    def generate_batch(
        self,
        agents: List["MetaphysicsAgent"],
        scenario: Optional["Scenario"],
        platform: PlatformType,
    ) -> List[ContentItem]:
        """
        批量生成内容

        Args:
            agents: Agent 列表
            scenario: 场景上下文（可选）
            platform: 目标平台

        Returns:
            生成的内容项列表
        """
        content_items = []

        # 每个 Agent 生成一个内容
        for agent in agents:
            content_item = self.generate_for_agent(
                agent=agent,
                scenario=scenario,
                topic="",  # 自动选择话题
                platform=platform,
            )
            content_items.append(content_item)

        return content_items

    def apply_styling(
        self,
        content: str,
        star: str,
        platform: PlatformType,
    ) -> str:
        """
        应用星曜特定的风格到内容

        Args:
            content: 原始内容
            star: 星曜名称
            platform: 目标平台

        Returns:
            样式化后的内容
        """
        star_style = self._get_star_style(star)
        emoji = star_style.get("emoji", "")

        if platform == PlatformType.TWITTER:
            # Twitter: 添加星曜前缀
            star_style.get("twitter", "{topic}")
            if "{topic}" not in content:
                content = f"{emoji} {content}" if emoji else content

        else:
            # Reddit: 添加星曜标签
            reddit_label = star_style.get("reddit", "")
            if reddit_label and "[星曜]" in reddit_label:
                content = f"[{star}星曜视角]\n\n{content}"

        return content

    def get_generated_content(
        self,
        agent_palace: Optional[str] = None,
        platform: Optional[PlatformType] = None,
        topic: Optional[str] = None,
    ) -> List[ContentItem]:
        """
        获取已生成的内容

        Args:
            agent_palace: 按宫位过滤（可选）
            platform: 按平台过滤（可选）
            topic: 按话题过滤（可选）

        Returns:
            过滤后的内容列表
        """
        results = self.generated_content

        if agent_palace:
            results = [c for c in results if c.agent_palace == agent_palace]

        if platform:
            results = [c for c in results if c.platform == platform]

        if topic:
            results = [c for c in results if topic in c.topic]

        return results

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_generated": len(self.generated_content),
            "agents_count": len(self.agents),
            "content_by_platform": {
                "twitter": len([c for c in self.generated_content if c.platform == PlatformType.TWITTER]),
                "reddit": len([c for c in self.generated_content if c.platform == PlatformType.REDDIT]),
            },
            "content_by_palace": {
                palace: len([c for c in self.generated_content if c.agent_palace == palace])
                for palace in set(c.agent_palace for c in self.generated_content)
            },
            "sample_content": [
                c.to_dict() for c in self.generated_content[:3]
            ],
        }


# ============ 便捷函数 ============

def create_content_generator(agents: List["MetaphysicsAgent"]) -> ContentGenerator:
    """
    创建内容生成器

    Args:
        agents: MetaphysicsAgent 列表

    Returns:
        ContentGenerator 实例
    """
    return ContentGenerator(agents=agents)
