"""
紫微斗数排盘服务模块
"""

from .data_utils import ChartDataHelper

from .star_placer import (
    StarPlacer,
    Star,
    PalaceStars,
    ChartResult,
    StarType,
    StarLevel,
    FiveElementType,
    place_stars,
)

from .palace_builder import (
    PalaceBuilder,
    TwelvePalaces,
    Palace,
    build_twelve_palaces,
    Gender,
    YinYang,
    PALACE_NAMES,
    EARTHLY_BRANCHES,
)

from .transform_decider import TransformDecider, TransformResult, TransformStar, TransformType

from .wuxing_calculator import (
    WuXingCalculator,
    WuXingJuType,
    WuXingJuResult,
    calculate_wuxing_ju,
)

# 命理群体预测模块
from .metaphysics_swarm import (
    MetaphysicsSwarmEngine,
    SwarmConfig,
    EmergenceResult,
    SimulationRound,
    run_metaphysics_swarm,
    MetaphysicsAgent,
    AgentRole,
    AgentPersonality,
    AgentAction,
    AgentState,
    ScenarioGenerator,
    Scenario,
    ScenarioType,
    TransformScenario,
    InteractionEvent,
)

__all__ = [
    # data_utils
    "ChartDataHelper",
    # star_placer
    "StarPlacer",
    "Star",
    "PalaceStars",
    "ChartResult",
    "StarType",
    "StarLevel",
    "FiveElementType",
    "place_stars",
    # palace_builder
    "PalaceBuilder",
    "TwelvePalaces",
    "Palace",
    "build_twelve_palaces",
    "Gender",
    "YinYang",
    "PALACE_NAMES",
    "EARTHLY_BRANCHES",
    # transform_decider
    "TransformDecider",
    "TransformResult",
    "TransformStar",
    "TransformType",
    # wuxing_calculator
    "WuXingCalculator",
    "WuXingJuType",
    "WuXingJuResult",
    "calculate_wuxing_ju",
    # metaphysics_swarm
    "MetaphysicsSwarmEngine",
    "SwarmConfig",
    "EmergenceResult",
    "SimulationRound",
    "run_metaphysics_swarm",
    "MetaphysicsAgent",
    "AgentRole",
    "AgentPersonality",
    "AgentAction",
    "AgentState",
    "ScenarioGenerator",
    "Scenario",
    "ScenarioType",
    "TransformScenario",
    "InteractionEvent",
]
