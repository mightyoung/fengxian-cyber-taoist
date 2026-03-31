"""
ScenarioGenerator - 场景生成器

根据四化特征生成交互场景:
- 化禄入宫 -> 机遇事件
- 化忌入宫 -> 挑战事件
- 化权入宫 -> 竞争事件
- 化科入宫 -> 学业/名誉事件
- 禄忌对称 -> 关键决策点
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random


class ScenarioType(str, Enum):
    """场景类型"""
    OPPORTUNITY = "机遇"      # 化禄带来的机会
    CHALLENGE = "挑战"       # 化忌带来的挑战
    COMPETITION = "竞争"      # 化权带来的竞争
    REPUTATION = "名誉"       # 化科带来的名誉事件
    DECISION = "决策"         # 禄忌对称的决策点
    INTERACTION = "互动"      # Agent间互动
    CHANGE = "转变"           # 大运/流年转变


@dataclass
class TransformScenario:
    """四化场景"""
    scenario_type: ScenarioType
    trigger_transforms: List[str]   # 触发的四化
    involved_palaces: List[str]     # 涉及的宫位
    description: str                 # 场景描述
    keywords: List[str] = field(default_factory=list)


@dataclass
class InteractionEvent:
    """交互事件"""
    id: str
    scenario_type: ScenarioType
    round_number: int
    timestamp: datetime = field(default_factory=datetime.now)

    # 事件内容
    trigger_agent_id: Optional[str] = None
    target_agent_id: Optional[str] = None
    event_type: str = ""                    # 事件类型
    content: str = ""                      # 事件描述

    # 预期影响
    expected_impact: Dict[str, float] = field(default_factory=dict)

    # 实际影响（执行后更新）
    actual_impact: Dict[str, float] = field(default_factory=dict)

    # 参与Agent的响应
    responses: Dict[str, str] = field(default_factory=dict)


@dataclass
class Scenario:
    """场景"""
    type: ScenarioType
    name: str
    description: str

    # 触发条件
    triggers: List[str] = field(default_factory=list)  # 触发关键词

    # 事件序列
    events: List[InteractionEvent] = field(default_factory=list)

    # 预期结果
    expected_outcome: Dict[str, Any] = field(default_factory=dict)


# ============ Scenario Templates ============

# 四化场景模板
TRANSFORM_SCENARIOS: Dict[str, TransformScenario] = {
    "化禄-机遇": TransformScenario(
        scenario_type=ScenarioType.OPPORTUNITY,
        trigger_transforms=["化禄"],
        involved_palaces=["命宫", "财帛宫", "官禄宫"],
        description="化禄星曜入驻，带来事业或财运的机遇",
        keywords=["机遇", "晋升", "投资收益", "贵人相助", "新机会"],
    ),
    "化忌-挑战": TransformScenario(
        scenario_type=ScenarioType.CHALLENGE,
        trigger_transforms=["化忌"],
        involved_palaces=["命宫", "夫妻宫", "子女宫"],
        description="化忌星曜入驻，面临挑战和阻碍",
        keywords=["困难", "阻碍", "损失", "压力", "健康问题"],
    ),
    "化权-竞争": TransformScenario(
        scenario_type=ScenarioType.COMPETITION,
        trigger_transforms=["化权"],
        involved_palaces=["官禄宫", "财帛宫"],
        description="化权星曜入驻，面临竞争和争夺",
        keywords=["竞争", "权力", "争夺", "控制", "话语权"],
    ),
    "化科-名誉": TransformScenario(
        scenario_type=ScenarioType.REPUTATION,
        trigger_transforms=["化科"],
        involved_palaces=["官禄宫", "迁移宫"],
        description="化科星曜入驻，学业或名誉相关事件",
        keywords=["考试", "荣誉", "学业", "名声", "表扬"],
    ),
    "禄忌对称": TransformScenario(
        scenario_type=ScenarioType.DECISION,
        trigger_transforms=["化禄", "化忌"],
        involved_palaces=["命宫", "财帛宫"],
        description="禄忌同宫或对宫，面临关键决策",
        keywords=["抉择", "转折", "关键决策", "取舍"],
    ),
}


# 场景内容库
SCENARIO_CONTENT = {
    ScenarioType.OPPORTUNITY: [
        "突然收到一个重要的工作邀请，待遇优厚",
        "投资理财获得意外收益",
        "遇到久未联系的贵人愿意帮助",
        "发现一个新的商业机会",
        "领导赏识，有晋升机会",
    ],
    ScenarioType.CHALLENGE: [
        "工作遇到重大挫折，需要重新规划",
        "财务出现意外损失",
        "健康出现问题需要调养",
        "感情出现危机或争执",
        "人际关系紧张，遭遇小人",
    ],
    ScenarioType.COMPETITION: [
        "项目竞争中遇到强劲对手",
        "职位晋升面临多人争夺",
        "商业谈判陷入僵局",
        "市场份额被竞争对手抢占",
        "评优评先遇到有力竞争",
    ],
    ScenarioType.REPUTATION: [
        "参加重要考试或评审",
        "作品或方案获得好评",
        "获得行业荣誉或奖项",
        "学术论文发表或获奖",
        "在公开场合获得表扬",
    ],
    ScenarioType.DECISION: [
        "面临职业选择的关键时刻",
        "需要决定是否接受新机会",
        "投资方向需要重新评估",
        "感情关系需要做出承诺",
        "人生规划需要重大调整",
    ],
    ScenarioType.INTERACTION: [
        "与合作伙伴进行重要洽谈",
        "与家人进行深度沟通",
        "与朋友发生误会需要解释",
        "与领导进行绩效沟通",
        "与配偶讨论未来规划",
    ],
    ScenarioType.CHANGE: [
        "大运开始，进入新阶段",
        "流年变化，运势转折",
        "工作或生活环境改变",
        "重要人际关系发生变化",
        "心态或观念发生转变",
    ],
}


# ============ Scenario Generator ============

class ScenarioGenerator:
    """场景生成器"""

    def __init__(
        self,
        transforms: Dict[str, str],
        palaces: Dict[str, List[str]],
        year: int = 2026,
    ):
        """
        初始化场景生成器

        Args:
            transforms: 四化映射 {化禄星, 化权星, 化科星, 化忌星}
            palaces: 宫位星曜映射
            year: 目标年份
        """
        self.transforms = transforms
        self.palaces = palaces
        self.year = year
        self.event_counter = 0

    def generate_scenarios(self, count: int = 5) -> List[Scenario]:
        """
        生成多个场景

        Args:
            count: 场景数量

        Returns:
            场景列表
        """
        scenarios = []

        # 根据四化生成场景
        if self.transforms.get("化禄星"):
            scenarios.append(self._create_opportunity_scenario())

        if self.transforms.get("化忌星"):
            scenarios.append(self._create_challenge_scenario())

        if self.transforms.get("化权星"):
            scenarios.append(self._create_competition_scenario())

        if self.transforms.get("化科星"):
            scenarios.append(self._create_reputation_scenario())

        # 检查禄忌对称
        if self.transforms.get("化禄星") and self.transforms.get("化忌星"):
            scenarios.append(self._create_decision_scenario())

        # 补充随机场景
        while len(scenarios) < count:
            scenarios.append(self._create_random_scenario())

        return scenarios[:count]

    def _create_opportunity_scenario(self) -> Scenario:
        """创建机遇场景"""
        lu_star = self.transforms.get("化禄星", "")
        return Scenario(
            type=ScenarioType.OPPORTUNITY,
            name=f"化禄{lu_star}机遇",
            description=f"流年有{lu_star}化禄，带来事业发展或财运提升的机遇",
            triggers=["化禄", "机遇", "发展"],
            events=[],
            expected_outcome={"wealth_boost": 0.2, "career_boost": 0.1},
        )

    def _create_challenge_scenario(self) -> Scenario:
        """创建挑战场景"""
        ji_star = self.transforms.get("化忌星", "")
        return Scenario(
            type=ScenarioType.CHALLENGE,
            name=f"化忌{ji_star}挑战",
            description=f"流年有{ji_star}化忌，面临挑战和阻碍",
            triggers=["化忌", "困难", "阻碍"],
            events=[],
            expected_outcome={"stress": 0.3, "relationship_drain": 0.1},
        )

    def _create_competition_scenario(self) -> Scenario:
        """创建竞争场景"""
        quan_star = self.transforms.get("化权星", "")
        return Scenario(
            type=ScenarioType.COMPETITION,
            name=f"化权{quan_star}竞争",
            description=f"流年有{quan_star}化权，面临竞争和争夺",
            triggers=["化权", "竞争", "争夺"],
            events=[],
            expected_outcome={"career_stress": 0.2, "opportunity_cost": 0.1},
        )

    def _create_reputation_scenario(self) -> Scenario:
        """创建名誉场景"""
        ke_star = self.transforms.get("化科星", "")
        return Scenario(
            type=ScenarioType.REPUTATION,
            name=f"化科{ke_star}名誉",
            description=f"流年有{ke_star}化科，学业或名誉相关事件",
            triggers=["化科", "考试", "荣誉"],
            events=[],
            expected_outcome={"reputation_boost": 0.2, "learning_boost": 0.1},
        )

    def _create_decision_scenario(self) -> Scenario:
        """创建决策场景"""
        lu_star = self.transforms.get("化禄星", "")
        ji_star = self.transforms.get("化忌星", "")
        return Scenario(
            type=ScenarioType.DECISION,
            name=f"禄忌{lu_star}-{ji_star}决策",
            description="禄忌同现，面临关键决策",
            triggers=["决策", "抉择", "转折"],
            events=[],
            expected_outcome={"growth_potential": 0.3, "risk_level": 0.2},
        )

    def _create_random_scenario(self) -> Scenario:
        """创建随机场景"""
        types = [
            ScenarioType.INTERACTION,
            ScenarioType.CHANGE,
            ScenarioType.OPPORTUNITY,
        ]
        scenario_type = random.choice(types)
        content = random.choice(SCENARIO_CONTENT[scenario_type])

        return Scenario(
            type=scenario_type,
            name=f"{scenario_type.value}场景",
            description=content,
            triggers=[],
            events=[],
            expected_outcome={},
        )

    def generate_event(
        self,
        scenario: Scenario,
        agent_id: str,
        target_id: Optional[str] = None,
    ) -> InteractionEvent:
        """
        为场景生成具体事件

        Args:
            scenario: 场景
            agent_id: 触发Agent ID
            target_id: 目标Agent ID

        Returns:
            交互事件
        """
        self.event_counter += 1
        event_id = f"event_{self.year}_{self.event_counter}"

        # 根据场景类型生成内容
        content = random.choice(SCENARIO_CONTENT[scenario.type])

        # 计算预期影响
        expected_impact = self._calculate_impact(scenario.type)

        return InteractionEvent(
            id=event_id,
            scenario_type=scenario.type,
            round_number=0,
            trigger_agent_id=agent_id,
            target_agent_id=target_id,
            event_type=scenario.type.value,
            content=content,
            expected_impact=expected_impact,
        )

    def _calculate_impact(self, scenario_type: ScenarioType) -> Dict[str, float]:
        """计算场景影响"""
        impacts = {
            ScenarioType.OPPORTUNITY: {
                "wealth": 0.15,
                "career": 0.1,
                "mood": 0.1,
                "energy": 0.1,
            },
            ScenarioType.CHALLENGE: {
                "wealth": -0.1,
                "career": -0.1,
                "mood": -0.15,
                "energy": -0.1,
            },
            ScenarioType.COMPETITION: {
                "career": 0.05,
                "stress": 0.15,
                "energy": -0.1,
            },
            ScenarioType.REPUTATION: {
                "social": 0.15,
                "mood": 0.1,
            },
            ScenarioType.DECISION: {
                "stress": 0.1,
                "growth": 0.2,
            },
            ScenarioType.INTERACTION: {
                "relationship": 0.1,
                "social": 0.05,
            },
            ScenarioType.CHANGE: {
                "energy": -0.1,
                "growth": 0.1,
            },
        }
        return impacts.get(scenario_type, {})


# ============ Helper Functions ============

def parse_transforms_from_chart(chart_data: Dict[str, Any]) -> Dict[str, str]:
    """
    从命盘数据解析四化信息

    Args:
        chart_data: 命盘数据

    Returns:
        四化映射 {化禄星, 化权星, 化科星, 化忌星}
    """
    transforms = {
        "化禄星": "",
        "化权星": "",
        "化科星": "",
        "化忌星": "",
    }

    # 从transforms字段获取
    if "transforms" in chart_data:
        for t in chart_data["transforms"]:
            transform_type = t.get("type", "")
            star = t.get("star", "")

            if transform_type == "化禄":
                transforms["化禄星"] = star
            elif transform_type == "化权":
                transforms["化权星"] = star
            elif transform_type == "化科":
                transforms["化科星"] = star
            elif transform_type == "化忌":
                transforms["化忌星"] = star

    return transforms


def parse_palaces_from_chart(chart_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    从命盘数据解析宫位信息

    Args:
        chart_data: 命盘数据

    Returns:
        宫位星曜映射
    """
    palaces = {}

    if "palaces" in chart_data:
        for palace in chart_data["palaces"]:
            palace_name = palace.get("name", "")
            stars = [s.get("name", "") for s in palace.get("stars", [])]
            palaces[palace_name] = stars

    return palaces


# ============ Aliases for type hints ============

# MetaphysicsScenario 是 Scenario 的别名，用于内容生成器等模块的类型提示
MetaphysicsScenario = Scenario
"""命理场景别名（兼容 P3-5 ContentGenerator）"""
