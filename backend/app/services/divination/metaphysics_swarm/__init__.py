"""
MetaphysicsSwarmEngine - 命理群体预测模块

基于紫微斗数命盘特征，创建多Agent模拟群体交互，
通过涌现机制生成预测结果。

核心类:
- MetaphysicsSwarmEngine: 主引擎
- MetaphysicsAgent: 命理智能体
- ScenarioGenerator: 场景生成器
- EmergenceCalculator: 涌现计算器
"""

from app.services.divination.metaphysics_swarm.engine import (
    MetaphysicsSwarmEngine,
    SwarmConfig,
    EmergenceResult,
    SimulationRound,
    run_metaphysics_swarm,
)

from app.services.divination.metaphysics_swarm.agents import (
    MetaphysicsAgent,
    AgentRole,
    AgentPersonality,
    AgentAction,
    AgentState,
)

from app.services.divination.metaphysics_swarm.scenarios import (
    ScenarioGenerator,
    Scenario,
    ScenarioType,
    TransformScenario,
    InteractionEvent,
)

from app.services.divination.metaphysics_swarm.social_network import (
    SocialNetworkSimulator,
    SocialNetwork,
    SocialNode,
    SocialEdge,
    RelationType,
    PalaceType,
    create_social_network,
    get_palace_influence,
    simulate_event_propagation,
)

from app.services.divination.metaphysics_swarm.social_interaction import (
    SocialInteractionEngine,
    SocialEvent,
    EventType,
    RoundResult,
    Opinion,
    InteractionMetrics,
    TransformBehavior,
    TRANSFORMATION_TO_SOCIAL,
    OPINION_TOPICS,
)

__all__ = [
    # engine
    "MetaphysicsSwarmEngine",
    "SwarmConfig",
    "EmergenceResult",
    "SimulationRound",
    "run_metaphysics_swarm",
    # agents
    "MetaphysicsAgent",
    "AgentRole",
    "AgentPersonality",
    "AgentAction",
    "AgentState",
    # scenarios
    "ScenarioGenerator",
    "Scenario",
    "ScenarioType",
    "TransformScenario",
    "InteractionEvent",
    # social_network
    "SocialNetworkSimulator",
    "SocialNetwork",
    "SocialNode",
    "SocialEdge",
    "RelationType",
    "PalaceType",
    "create_social_network",
    "get_palace_influence",
    "simulate_event_propagation",
    # social_interaction
    "SocialInteractionEngine",
    "SocialEvent",
    "EventType",
    "RoundResult",
    "Opinion",
    "InteractionMetrics",
    "TransformBehavior",
    "TRANSFORMATION_TO_SOCIAL",
    "OPINION_TOPICS",
]
