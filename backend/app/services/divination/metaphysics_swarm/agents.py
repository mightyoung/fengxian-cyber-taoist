"""
MetaphysicsAgent - 命理智能体定义

基于紫微斗数命盘特征创建Agent:
- 根据命宫主星确定Agent性格
- 根据四化确定Agent行为动机
- 根据宫位确定Agent角色分工
- 社交网络扩展（P3-3 AgentSocialProfile）
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# 避免循环导入
if TYPE_CHECKING:
    from .social_network import SocialNetwork


class AgentRole(str, Enum):
    """Agent角色类型"""
    MING_ZHU = "命主"       # 命宫，代表本人
    SHI_YE = "事业"         # 官禄宫，代表事业
    CAI_YUN = "财运"        # 财帛宫，代表财运
    GAN_QING = "感情"       # 夫妻宫，代表感情
    FU_QI = "配偶"          # 夫妻宫，代表配偶
    JIA_REN = "家人"        # 父母宫，代表家人
    PENG_YOU = "朋友"        # 迁移宫/奴仆宫，代表朋友
    ZI_NU = "子女"          # 子女宫，代表子女


class AgentPersonality(str, Enum):
    """Agent性格类型（基于主星）"""
    # 紫微星系
    ZI_WEI = "紫微"         # 尊贵、领导欲强
    TIAN_JI = "天机"        # 聪明、善变
    TAI_YANG = "太阳"       # 热情、爱面子
    WU_QU = "武曲"          # 刚毅、理财
    TIAN_TONG = "天同"      # 享乐、保守
    LIAN_ZHEN = "廉贞"      # 邪正、复杂

    # 天府星系
    TIAN_FU = "天府"        # 稳重、保守
    TAI_YIN = "太阴"        # 温柔、敏感
    JU_MEN = "巨门"         # 、口才好
    TAN_LANG = "贪狼"       # 贪心、欲望
    PO_JUN = "破军"         # 破坏、创新
    ZUO_BI = "左辅"         # 辅助、忠诚
    YOU_BI = "右弼"         # 辅助、聪慧
    WEN_QU = "文曲"         # 文采、才华
    WEN_SHAO = "文昌"       # 文昌、考运
    JIAO_SHENG = "教驿"     # 动态、奔波

    # 辅助星曜
    QI_SHA = "七杀"         # 刚烈、果断
    SUI_YUE = "岁建"        # 变动、机遇
    BAI_FEN = "百非"        # 灾祸、化解
    TIAN_KU = "天哭"        # 悲伤、压力
    TIAN_XU = "天虚"        # 虚弱、虚耗
    LONG_CHI = "龙池"       # 功名、进取
    FENG_HE = "凤阁"        # 功名、贵气


# ============ Social Profile Enums & Classes (P3-3) ============

class SocialRole(str, Enum):
    """社交角色类型"""
    OPINION_LEADER = "意见领袖"    # 高影响力，主动传播
    FOLLOWER = "跟随者"            # 低影响力，响应他人
    CONTROVERSIAL = "争议人物"    # 高冲突性
    NEUTRAL = "中立者"            # 低参与度


class NetworkPosition(str, Enum):
    """网络位置类型"""
    CENTRAL = "中心节点"          # 高连接度
    BRIDGE = "桥接节点"           # 连接不同群体
    PERIPHERAL = "边缘节点"       # 低连接度


@dataclass
class SocialEvent:
    """社交事件"""
    event_id: str
    agent_id: str
    event_type: str              # "opinion", "response", "attack", "support"
    topic: str                   # 话题
    content: str                 # 内容
    sentiment: float = 0.0      # 情感倾向 -1.0 ~ 1.0
    target_id: Optional[str] = None  # 目标Agent（如果有）
    impact_score: float = 0.0   # 影响分数
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentSocialProfile:
    """Agent社交画像"""
    agent_id: str
    social_role: SocialRole = SocialRole.NEUTRAL
    influence_score: float = 0.5  # 0.0-1.0
    network_position: NetworkPosition = NetworkPosition.PERIPHERAL
    interaction_count: int = 0
    consensus_reached: int = 0
    conflicts_engaged: int = 0
    opinion_clusters: Dict[str, float] = field(default_factory=dict)  # {话题: 倾向值}
    interaction_history: List[Dict] = field(default_factory=list)

    def update_from_network(self, centrality: float, degree: int) -> None:
        """根据网络指标更新社交位置"""
        # 中心性 > 0.6 → CENTRAL
        if centrality > 0.6:
            self.network_position = NetworkPosition.CENTRAL
        # degree 高但 centrality 低 → BRIDGE
        elif degree > 4 and centrality < 0.4:
            self.network_position = NetworkPosition.BRIDGE
        # 其他 → PERIPHERAL
        else:
            self.network_position = NetworkPosition.PERIPHERAL

    def update_role(self) -> None:
        """根据交互历史更新社交角色"""
        # 计算冲突率
        total_interactions = max(1, self.interaction_count)
        conflict_rate = self.conflicts_engaged / total_interactions

        # 高影响力 + 高互动 → OPINION_LEADER
        if self.influence_score > 0.7 and self.interaction_count > 10:
            self.social_role = SocialRole.OPINION_LEADER
        # 高冲突 → CONTROVERSIAL
        elif conflict_rate > 0.3:
            self.social_role = SocialRole.CONTROVERSIAL
        # 低参与 → FOLLOWER
        elif self.interaction_count < 3:
            self.social_role = SocialRole.FOLLOWER
        else:
            self.social_role = SocialRole.NEUTRAL

    def record_interaction(
        self,
        interaction_type: str,
        topic: str,
        sentiment: float,
        target_id: Optional[str] = None,
        impact: float = 0.0
    ) -> None:
        """记录交互"""
        self.interaction_count += 1
        if interaction_type == "conflict":
            self.conflicts_engaged += 1
        elif interaction_type == "consensus":
            self.consensus_reached += 1

        # 更新话题倾向
        if topic not in self.opinion_clusters:
            self.opinion_clusters[topic] = sentiment
        else:
            # 移动平均更新倾向
            self.opinion_clusters[topic] = 0.7 * self.opinion_clusters[topic] + 0.3 * sentiment

        # 添加历史记录
        self.interaction_history.append({
            "type": interaction_type,
            "topic": topic,
            "sentiment": sentiment,
            "target_id": target_id,
            "impact": impact,
            "timestamp": datetime.now().isoformat(),
        })

        # 限制历史长度
        if len(self.interaction_history) > 50:
            self.interaction_history = self.interaction_history[-50:]

    def get_opinion(self, topic: str) -> Optional[float]:
        """获取对某话题的倾向"""
        return self.opinion_clusters.get(topic)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "social_role": self.social_role.value,
            "influence_score": round(self.influence_score, 3),
            "network_position": self.network_position.value,
            "interaction_count": self.interaction_count,
            "consensus_reached": self.consensus_reached,
            "conflicts_engaged": self.conflicts_engaged,
            "opinion_clusters": {k: round(v, 3) for k, v in self.opinion_clusters.items()},
            "recent_interactions": self.interaction_history[-5:],
        }


# 星曜社交风格映射
STAR_SOCIAL_STYLE: Dict[str, Dict[str, Any]] = {
    # 紫微系 → 领导力、战略话题
    "紫微": {"topics": ["领导力", "战略规划", "团队管理"], "style": "权威", "sentiment_bias": 0.1},
    "天府": {"topics": ["理财", "稳健发展", "资源管理"], "style": "稳健", "sentiment_bias": 0.05},
    # 武曲系 → 商业、投资话题
    "武曲": {"topics": ["商业决策", "投资", "创业"], "style": "务实", "sentiment_bias": -0.05},
    # 贪狼系 → 创业、竞争话题
    "贪狼": {"topics": ["机遇", "竞争", "创新"], "style": "激进", "sentiment_bias": 0.0},
    # 太阴系 → 情感、家庭话题
    "太阴": {"topics": ["情感关系", "家庭", "生活方式"], "style": "细腻", "sentiment_bias": 0.15},
    # 天机系 → 智慧、创新话题
    "天机": {"topics": ["科技", "创新思维", "学习方法"], "style": "灵活", "sentiment_bias": 0.0},
    # 太阳系 → 名声、社会话题
    "太阳": {"topics": ["社会责任", "公众形象", "慈善公益"], "style": "热情", "sentiment_bias": 0.1},
    # 天同系 → 享乐、生活话题
    "天同": {"topics": ["生活品质", "休闲娱乐", "身心健康"], "style": "平和", "sentiment_bias": 0.2},
    # 廉贞系 → 复杂、争议话题
    "廉贞": {"topics": ["人际关系", "道德伦理", "法律问题"], "style": "尖锐", "sentiment_bias": -0.1},
    # 破军系 → 变革、突破话题
    "破军": {"topics": ["变革", "突破", "风险", "创业"], "style": "激进", "sentiment_bias": -0.05},
    # 巨门系 → 传播、辩论话题
    "巨门": {"topics": ["舆论", "传播", "真相", "辩论"], "style": "犀利", "sentiment_bias": -0.15},
    # 七杀系 → 挑战、竞争话题
    "七杀": {"topics": ["竞争", "挑战", "权力"], "style": "强势", "sentiment_bias": -0.1},
    # 辅助星曜
    "左辅": {"topics": ["团队协作", "支持", "辅助"], "style": "温和", "sentiment_bias": 0.1},
    "右弼": {"topics": ["协调", "沟通", "和解"], "style": "圆融", "sentiment_bias": 0.15},
    "文曲": {"topics": ["文化", "艺术", "教育"], "style": "文雅", "sentiment_bias": 0.1},
    "文昌": {"topics": ["学业", "考试", "晋升"], "style": "严谨", "sentiment_bias": 0.05},
    "天梁": {"topics": ["公益", "监督", "公正"], "style": "正直", "sentiment_bias": 0.1},
}


@dataclass
class AgentPersona:
    """Agent人设"""
    role: AgentRole
    personality: AgentPersonality
    stars: List[str]              # 主星列表
    transforms: List[str]          # 四化列表
    palace_name: str               # 所属宫位
    strengths: List[str] = field(default_factory=list)    # 优势
    weaknesses: List[str] = field(default_factory=list)   # 劣势
    motivations: List[str] = field(default_factory=list)  # 行为动机


@dataclass
class AgentState:
    """Agent状态"""
    energy: float = 0.5           # 能量值 0-1
    mood: float = 0.5             # 情绪值 0-1
    wealth: float = 0.5           # 财运值 0-1
    career: float = 0.5           # 事业值 0-1
    relationship: float = 0.5      # 感情值 0-1
    health: float = 0.5           # 健康值 0-1
    social: float = 0.5           # 人际关系 0-1
    resources: Dict[str, float] = field(default_factory=dict)  # 其他资源


@dataclass
class AgentAction:
    """Agent行动"""
    agent_id: str
    action_type: str              # 行动类型
    target_id: Optional[str]      # 目标Agent
    content: str                  # 行动内容
    emotion: str                  # 情绪表达
    impact: Dict[str, float] = field(default_factory=dict)  # 影响
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetaphysicsAgent:
    """命理智能体"""
    id: str
    persona: AgentPersona
    state: AgentState
    memory: List[AgentAction] = field(default_factory=list)  # 记忆
    social_profile: Optional[AgentSocialProfile] = None  # 社交画像 (P3-3)

    def init_social_profile(self, network: "SocialNetwork") -> AgentSocialProfile:
        """
        基于宫位和网络初始化社交画像

        Args:
            network: 社交网络实例

        Returns:
            初始化后的AgentSocialProfile
        """
        palace = self.persona.palace_name

        # 1. 根据主星确定基础影响力
        primary_star = self.persona.stars[0] if self.persona.stars else "天同"
        base_influence = 0.5

        # 根据主星调整影响力
        high_influence_stars = {"紫微", "太阳", "贪狼", "天府", "天机"}
        low_influence_stars = {"巨门", "七杀", "破军", "廉贞"}

        if primary_star in high_influence_stars:
            base_influence = 0.7
        elif primary_star in low_influence_stars:
            base_influence = 0.4

        # 根据四化加成
        transforms = self.persona.transforms
        if "化禄" in transforms or "化权" in transforms:
            base_influence = min(1.0, base_influence + 0.1)
        if "化忌" in transforms:
            base_influence = max(0.2, base_influence - 0.1)

        # 2. 获取网络指标
        centrality = network.calculate_centrality(palace)
        degree = len(network.nodes.get(palace, None).connections) if palace in network.nodes else 0

        # 3. 确定网络位置
        if centrality > 0.6:
            network_position = NetworkPosition.CENTRAL
        elif degree > 4 and centrality < 0.4:
            network_position = NetworkPosition.BRIDGE
        else:
            network_position = NetworkPosition.PERIPHERAL

        # 4. 生成社交角色
        if base_influence > 0.6 and centrality > 0.5:
            social_role = SocialRole.OPINION_LEADER
        elif "化忌" in transforms or "七杀" in self.persona.stars or "破军" in self.persona.stars:
            social_role = SocialRole.CONTROVERSIAL
        elif centrality < 0.3:
            social_role = SocialRole.FOLLOWER
        else:
            social_role = SocialRole.NEUTRAL

        # 创建社交画像
        self.social_profile = AgentSocialProfile(
            agent_id=self.id,
            social_role=social_role,
            influence_score=base_influence,
            network_position=network_position,
            interaction_count=0,
            consensus_reached=0,
            conflicts_engaged=0,
            opinion_clusters={},
            interaction_history=[],
        )

        # 根据网络指标更新位置
        self.social_profile.update_from_network(centrality, degree)

        return self.social_profile

    def generate_social_content(self, scenario: Dict[str, Any], topic: str) -> str:
        """
        生成社交内容（基于命盘特征）

        Args:
            scenario: 场景上下文
            topic: 话题

        Returns:
            生成的社交内容
        """
        if not self.social_profile:
            return self._generate_default_content(topic)

        primary_star = self.persona.stars[0] if self.persona.stars else "天同"
        star_style = STAR_SOCIAL_STYLE.get(primary_star, STAR_SOCIAL_STYLE["天同"])

        # 获取该星曜擅长的话题
        relevant_topics = star_style.get("topics", [])
        style = star_style.get("style", "中性")
        star_style.get("sentiment_bias", 0.0)

        # 根据角色调整风格
        if self.social_profile.social_role == SocialRole.OPINION_LEADER:
            prefix = "作为行业领袖，我认为"
        elif self.social_profile.social_role == SocialRole.CONTROVERSIAL:
            prefix = "我必须指出"
        elif self.social_profile.social_role == SocialRole.FOLLOWER:
            prefix = "看了大家的讨论，我觉得"
        else:
            prefix = "分享一个观点"

        # 根据话题选择内容模板
        if topic in relevant_topics or any(t in topic for t in relevant_topics):
            content = self._generate_topic_content(topic, style, scenario)
        else:
            content = self._generate_general_content(topic, style, scenario)

        return f"{prefix}：{content}"

    def _generate_topic_content(self, topic: str, style: str, scenario: Dict[str, Any]) -> str:
        """根据话题和风格生成内容"""
        templates = {
            "权威": [
                "从战略高度来看，{topic}是决定成败的关键因素。",
                "我们必须在{topic}上建立明确的标准和规范。",
            ],
            "稳健": [
                "对于{topic}，建议采取循序渐进的策略。",
                "稳健推进{topic}的发展才是长久之计。",
            ],
            "务实": [
                "关注{topic}的实际效益比空谈更重要。",
                "数据告诉我们，{topic}需要务实的方法。",
            ],
            "激进": [
                "机会稍纵即逝，在{topic}上必须果断行动！",
                "市场竞争激烈，{topic}需要突破性思维。",
            ],
            "细腻": [
                "在{topic}的讨论中，我们应该更多关注细节。",
                "每个人的感受都值得被重视，尤其是在{topic}上。",
            ],
            "灵活": [
                "换个角度看{topic}，或许会有新发现。",
                "创新的思路往往能打开{topic}的新局面。",
            ],
            "热情": [
                "让更多人了解{topic}的重要性！",
                "积极传播{topic}的正能量！",
            ],
            "平和": [
                "{topic}需要我们保持平和的心态。",
                "在{topic}上，不必太过焦虑。",
            ],
            "尖锐": [
                "必须直面{topic}中的问题！",
                "对{topic}的虚伪说不。",
            ],
            "激进": [
                "破旧立新，{topic}需要彻底变革！",
                "风险与机遇并存，{topic}需要勇气。",
            ],
            "犀利": [
                "真相是：{topic}需要更多理性思考。",
                "揭开{topic}背后的真实逻辑。",
            ],
            "强势": [
                "强者恒强，{topic}就是证明实力的战场。",
                "在{topic}上，没有退路。",
            ],
            "温和": [
                "让我们一起探讨{topic}的解决方案。",
                "支持{topic}的发展需要大家共同努力。",
            ],
            "圆融": [
                "{topic}需要多方协调，寻求共识。",
                "在{topic}上，中庸之道往往更有效。",
            ],
            "文雅": [
                "品味{topic}中的文化内涵。",
                "从文化角度解读{topic}的意义。",
            ],
            "严谨": [
                "系统分析{topic}的每个环节。",
                "用科学方法研究{topic}的规律。",
            ],
            "正直": [
                "公正地看待{topic}的问题。",
                "在{topic}上坚持正直的原则。",
            ],
            "中性": [
                "关于{topic}，我有一些思考。",
                "分享对{topic}的看法。",
            ],
        }

        style_templates = templates.get(style, templates["中性"])
        template = style_templates[hash(topic) % len(style_templates)]
        return template.format(topic=topic)

    def _generate_default_content(self, topic: str) -> str:
        """生成默认内容"""
        return f"分享关于'{topic}'的思考：命盘中显示我对此类话题有独特的见解。"

    def _generate_general_content(self, topic: str, style: str, scenario: Dict[str, Any]) -> str:
        """生成通用话题内容"""
        primary_star = self.persona.stars[0] if self.persona.stars else "天同"
        return f"作为{primary_star}星曜持有者，我认为{topic}需要结合多方面因素来考虑。"

    def express_opinion(self, topic: str, sentiment: float) -> SocialEvent:
        """
        表达观点

        Args:
            topic: 话题
            sentiment: 情感倾向 -1.0 ~ 1.0

        Returns:
            生成的社交事件
        """
        if not self.social_profile:
            raise ValueError("Social profile not initialized. Call init_social_profile first.")

        # 生成事件ID
        event_id = f"{self.id}_event_{datetime.now().timestamp()}"

        # 计算影响分数
        impact_score = abs(sentiment) * self.social_profile.influence_score * 10

        # 根据角色调整情感
        role = self.social_profile.social_role
        if role == SocialRole.CONTROVERSIAL:
            sentiment = -0.5 if sentiment > 0 else 0.5  # 总是与主流唱反调
        elif role == SocialRole.FOLLOWER:
            sentiment = sentiment * 0.5  # 跟随者倾向温和

        # 创建社交事件
        event = SocialEvent(
            event_id=event_id,
            agent_id=self.id,
            event_type="opinion",
            topic=topic,
            content=self.generate_social_content({"topic": topic}, topic),
            sentiment=sentiment,
            target_id=None,
            impact_score=impact_score,
        )

        # 记录交互
        self.social_profile.record_interaction(
            interaction_type="opinion",
            topic=topic,
            sentiment=sentiment,
            target_id=None,
            impact=impact_score,
        )

        return event

    def respond_to_opinion(self, event: SocialEvent) -> Optional[SocialEvent]:
        """
        响应他人观点

        Args:
            event: 被响应的事件

        Returns:
            响应事件（如果需要响应），None表示不响应
        """
        if not self.social_profile:
            raise ValueError("Social profile not initialized. Call init_social_profile first.")

        # 跟随者不主动响应
        if self.social_profile.social_role == SocialRole.FOLLOWER:
            # 但可能有小概率支持
            import random
            if random.random() < 0.1:  # 10%概率响应
                return self._create_support_response(event)
            return None

        # 计算响应概率
        response_prob = self._calculate_response_probability(event)
        import random
        if random.random() > response_prob:
            return None

        # 判断响应类型
        sentiment = event.sentiment
        my_opinion = self.social_profile.get_opinion(event.topic)

        if my_opinion is not None:
            opinion_diff = abs(my_opinion - sentiment)
        else:
            opinion_diff = 0.5

        # 观点差异大 → 冲突
        if opinion_diff > 0.6:
            return self._create_conflict_response(event)
        # 观点相近 → 支持
        elif opinion_diff < 0.3:
            return self._create_support_response(event)
        # 中立 → 补充
        else:
            return self._create_neutral_response(event)

    def _calculate_response_probability(self, event: SocialEvent) -> float:
        """计算响应概率"""
        base_prob = 0.3

        # 根据角色调整
        if self.social_profile.social_role == SocialRole.OPINION_LEADER:
            base_prob = 0.6  # 意见领袖更可能响应
        elif self.social_profile.social_role == SocialRole.CONTROVERSIAL:
            base_prob = 0.7  # 争议人物总是想发言

        # 根据影响力调整
        influence_factor = self.social_profile.influence_score

        # 根据话题相关性调整
        topic_relevant = 0.0
        for star in self.persona.stars:
            if star in STAR_SOCIAL_STYLE:
                topics = STAR_SOCIAL_STYLE[star].get("topics", [])
                if event.topic in topics or any(t in event.topic for t in topics):
                    topic_relevant = 0.2
                    break

        return min(1.0, base_prob * influence_factor + topic_relevant)

    def _create_support_response(self, event: SocialEvent) -> SocialEvent:
        """创建支持响应"""
        event_id = f"{self.id}_response_{datetime.now().timestamp()}"

        response = SocialEvent(
            event_id=event_id,
            agent_id=self.id,
            event_type="support",
            topic=event.topic,
            content=f"我赞同这个观点，补充一点：{self._generate_topic_content(event.topic, '温和', {})}",
            sentiment=event.sentiment * 0.8,
            target_id=event.agent_id,
            impact_score=event.impact_score * 0.5,
        )

        self.social_profile.record_interaction(
            interaction_type="consensus",
            topic=event.topic,
            sentiment=response.sentiment,
            target_id=event.agent_id,
            impact=response.impact_score,
        )

        return response

    def _create_conflict_response(self, event: SocialEvent) -> SocialEvent:
        """创建冲突响应"""
        event_id = f"{self.id}_conflict_{datetime.now().timestamp()}"

        response = SocialEvent(
            event_id=event_id,
            agent_id=self.id,
            event_type="attack",
            topic=event.topic,
            content=f"这个观点值得商榷，我的看法是：{self._generate_topic_content(event.topic, '犀利', {})}",
            sentiment=-event.sentiment * 0.7,
            target_id=event.agent_id,
            impact_score=event.impact_score * 0.8,
        )

        self.social_profile.record_interaction(
            interaction_type="conflict",
            topic=event.topic,
            sentiment=response.sentiment,
            target_id=event.agent_id,
            impact=response.impact_score,
        )

        return response

    def _create_neutral_response(self, event: SocialEvent) -> SocialEvent:
        """创建中立响应"""
        event_id = f"{self.id}_neutral_{datetime.now().timestamp()}"

        response = SocialEvent(
            event_id=event_id,
            agent_id=self.id,
            event_type="response",
            topic=event.topic,
            content=f"从另一个角度看：{self._generate_topic_content(event.topic, '中性', {})}",
            sentiment=event.sentiment * 0.3,
            target_id=event.agent_id,
            impact_score=event.impact_score * 0.3,
        )

        self.social_profile.record_interaction(
            interaction_type="neutral",
            topic=event.topic,
            sentiment=response.sentiment,
            target_id=event.agent_id,
            impact=response.impact_score,
        )

        return response

    def calculate_influence(self, network: "SocialNetwork") -> float:
        """
        计算在社交网络中的影响力

        Args:
            network: 社交网络

        Returns:
            综合影响力分数 (0.0-1.0)
        """
        if not self.social_profile:
            return 0.5

        palace = self.persona.palace_name

        # 获取网络中心性
        centrality = network.calculate_centrality(palace)

        # 综合影响力 = 基础影响力 * 0.4 + 网络中心性 * 0.6
        combined_influence = (
            self.social_profile.influence_score * 0.4 +
            centrality * 0.6
        )

        # 更新社交画像中的影响力
        self.social_profile.influence_score = combined_influence

        # 可能触发角色更新
        self.social_profile.update_role()

        return combined_influence

    def add_memory(self, action: AgentAction) -> None:
        """添加记忆"""
        self.memory.append(action)
        # 限制记忆长度
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]

    def update_state(self, impact: Dict[str, float]) -> None:
        """更新状态"""
        for key, value in impact.items():
            if hasattr(self.state, key):
                current = getattr(self.state, key)
                new_value = max(0.0, min(1.0, current + value))
                setattr(self.state, key, new_value)

    def get_context(self) -> Dict[str, Any]:
        """获取Agent上下文"""
        context = {
            "id": self.id,
            "role": self.persona.role.value,
            "personality": self.persona.personality.value,
            "stars": self.persona.stars,
            "transforms": self.persona.transforms,
            "palace": self.persona.palace_name,
            "state": {
                "energy": self.state.energy,
                "mood": self.state.mood,
                "wealth": self.state.wealth,
                "career": self.state.career,
                "relationship": self.state.relationship,
                "health": self.state.health,
                "social": self.state.social,
            },
            "recent_actions": [
                {
                    "type": a.action_type,
                    "content": a.content,
                    "emotion": a.emotion,
                }
                for a in self.memory[-5:]
            ],
        }

        # 添加社交画像信息 (P3-3)
        if self.social_profile:
            context["social_profile"] = self.social_profile.to_dict()

        return context

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": self.id,
            "persona": {
                "role": self.persona.role.value,
                "personality": self.persona.personality.value,
                "stars": self.persona.stars,
                "transforms": self.persona.transforms,
                "palace": self.persona.palace_name,
                "strengths": self.persona.strengths,
                "weaknesses": self.persona.weaknesses,
                "motivations": self.persona.motivations,
            },
            "state": {
                "energy": self.state.energy,
                "mood": self.state.mood,
                "wealth": self.state.wealth,
                "career": self.state.career,
                "relationship": self.state.relationship,
                "health": self.state.health,
                "social": self.state.social,
            },
            "memory_count": len(self.memory),
        }

        # 添加社交画像信息 (P3-3)
        if self.social_profile:
            result["social_profile"] = self.social_profile.to_dict()

        return result


# ============ Agent Factory ============

def create_agent_from_chart(
    agent_id: str,
    role: AgentRole,
    stars: List[str],
    transforms: Dict[str, str],
    palace_name: str,
    palace_stars: List[str],
) -> MetaphysicsAgent:
    """
    根据命盘特征创建Agent

    Args:
        agent_id: Agent ID
        role: Agent角色
        stars: 主星列表
        transforms: 四化映射 {化禄星, 化权星, 化科星, 化忌星}
        palace_name: 宫位名称
        palace_stars: 宫位内星曜列表

    Returns:
        MetaphysicsAgent实例
    """
    # 确定性格（取第一个主星）
    personality_str = stars[0] if stars else "天同"
    try:
        personality = AgentPersonality(personality_str)
    except ValueError:
        personality = AgentPersonality.TIAN_TONG  # 默认

    # 构建四化列表
    transform_list = [t for t in transforms.values() if t]

    # 根据性格和四化确定动机
    motivations = _derive_motivations(personality_str, transform_list, palace_name)

    # 根据性格确定优劣势
    strengths, weaknesses = _derive_strengths_weaknesses(personality_str, transform_list)

    persona = AgentPersona(
        role=role,
        personality=personality,
        stars=stars,
        transforms=transform_list,
        palace_name=palace_name,
        strengths=strengths,
        weaknesses=weaknesses,
        motivations=motivations,
    )

    # 初始化状态
    initial_energy = 0.5 + (0.1 if "紫微" in stars else 0.0)
    state = AgentState(energy=initial_energy)

    return MetaphysicsAgent(
        id=agent_id,
        persona=persona,
        state=state,
    )


def _derive_motivations(
    personality: str,
    transforms: List[str],
    palace: str,
) -> List[str]:
    """派生动机"""
    motivations = []

    # 基于性格
    if "紫微" in personality:
        motivations.append("追求领导地位和尊贵感")
    elif "天机" in personality:
        motivations.append("寻求智慧和创新机会")
    elif "太阳" in personality:
        motivations.append("追求名声和社会认可")
    elif "武曲" in personality:
        motivations.append("追求财富和事业成就")
    elif "天同" in personality:
        motivations.append("追求生活舒适和享乐")
    elif "贪狼" in personality:
        motivations.append("追求欲望满足和社交")

    # 基于四化
    if "化禄" in transforms:
        motivations.append("抓住机遇发展")
    if "化权" in transforms:
        motivations.append("争取控制权和话语权")
    if "化科" in transforms:
        motivations.append("追求名誉和学业")
    if "化忌" in transforms:
        motivations.append("克服困难和阻碍")

    # 基于宫位
    if "事业" in palace or "官禄" in palace:
        motivations.append("追求职业发展")
    elif "财帛" in palace:
        motivations.append("追求财务自由")
    elif "夫妻" in palace:
        motivations.append("追求感情和谐")

    return motivations


def _derive_strengths_weaknesses(
    personality: str,
    transforms: List[str],
) -> tuple[List[str], List[str]]:
    """派生优劣势"""
    strengths = []
    weaknesses = []

    # 基于性格
    if "紫微" in personality:
        strengths.append("领导能力强")
        weaknesses.append("过于自尊")
    elif "天机" in personality:
        strengths.append("思维敏捷")
        weaknesses.append("善变不稳定")
    elif "太阳" in personality:
        strengths.append("热情开朗")
        weaknesses.append("爱面子")
    elif "武曲" in personality:
        strengths.append("执行力强")
        weaknesses.append("过于刚硬")
    elif "天同" in personality:
        strengths.append("心态平和")
        weaknesses.append("缺乏斗志")
    elif "贪狼" in personality:
        strengths.append("社交能力强")
        weaknesses.append("贪心欲望强")
    elif "破军" in personality:
        strengths.append("创新突破")
        weaknesses.append("破坏性大")
    elif "天府" in personality:
        strengths.append("稳重可靠")
        weaknesses.append("保守谨慎")

    # 基于四化
    if "化禄" in transforms:
        strengths.append("有贵人相助")
    if "化权" in transforms:
        strengths.append("有竞争力")
    if "化科" in transforms:
        strengths.append("有学业运势")
    if "化忌" in transforms:
        weaknesses.append("有阻碍需克服")

    return strengths, weaknesses
