"""
MetaphysicsSwarmEngine - 命理群体预测引擎

核心功能:
1. 根据命盘特征创建Agent
2. 根据四化创建交互场景
3. 运行多轮群体模拟
4. 计算涌现结果
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.services.divination.metaphysics_swarm.agents import (
    MetaphysicsAgent,
    AgentRole,
    AgentAction,
    create_agent_from_chart,
)
from app.services.divination.metaphysics_swarm.scenarios import (
    ScenarioGenerator,
    Scenario,
    ScenarioType,
    InteractionEvent,
    parse_transforms_from_chart,
    parse_palaces_from_chart,
)


class SwarmStatus(str, Enum):
    """Swarm状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SwarmConfig:
    """Swarm配置"""
    rounds: int = 10                    # 模拟轮数
    max_concurrent: int = 3             # 最大并发Agent数
    enable_emergence: bool = True        # 启用涌现计算
    emergence_threshold: float = 0.3      # 涌现阈值
    event_density: float = 0.5           # 事件密度 0-1
    agent_response_timeout: int = 30     # Agent响应超时(秒)

    # 可选的LLM回调
    llm_callback: Optional[Callable] = None


@dataclass
class SimulationRound:
    """模拟轮次"""
    round_number: int
    timestamp: datetime

    # 触发的场景
    scenarios: List[Scenario] = field(default_factory=list)

    # 发生的交互事件
    events: List[InteractionEvent] = field(default_factory=list)

    # Agent状态变化
    state_changes: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # 本轮涌现结果
    emergence: Optional["EmergenceResult"] = None


@dataclass
class EmergenceResult:
    """涌现结果"""
    timestamp: datetime = field(default_factory=datetime.now)

    # 整体评估
    overall_score: float = 0.0           # 整体得分 0-1
    overall_trend: str = "平稳"           # 趋势：上升/下降/平稳

    # 维度评估
    dimension_scores: Dict[str, float] = field(default_factory=dict)

    # 关键事件
    key_events: List[str] = field(default_factory=list)

    # 涌现模式
    emergence_patterns: List[str] = field(default_factory=list)

    # 建议
    suggestions: List[str] = field(default_factory=list)

    # 置信度
    confidence: float = 0.5


class MetaphysicsSwarmEngine:
    """
    命理群体预测引擎

    将命理分析转化为多Agent模拟，通过涌现机制生成预测结果。
    """

    def __init__(
        self,
        chart_data: Dict[str, Any],
        target_year: int = 2026,
        config: Optional[SwarmConfig] = None,
    ):
        """
        初始化引擎

        Args:
            chart_data: 命盘数据
            target_year: 目标年份
            config: 配置
        """
        self.chart_data = chart_data
        self.target_year = target_year
        self.config = config or SwarmConfig()

        # 解析命盘信息
        self._parse_chart()

        # 初始化组件
        self.agents: Dict[str, MetaphysicsAgent] = {}
        self.scenario_generator: Optional[ScenarioGenerator] = None

        # 模拟状态
        self.status = SwarmStatus.IDLE
        self.current_round = 0
        self.rounds: List[SimulationRound] = []

    def _parse_chart(self) -> None:
        """解析命盘数据"""
        # 提取四化信息
        self.transforms = parse_transforms_from_chart(self.chart_data)

        # 提取宫位信息
        self.palaces = parse_palaces_from_chart(self.chart_data)

        # 提取主星（命宫）
        self.ming_gong_stars = self.palaces.get("命宫", [])

        # 提取事业宫主星
        self.guanlu_stars = self.palaces.get("官禄宫", [])

        # 提取财帛宫主星
        self.caibo_stars = self.palaces.get("财帛宫", [])

        # 提取夫妻宫主星
        self.fuq_gong_stars = self.palaces.get("夫妻宫", [])

    async def initialize(self) -> None:
        """初始化Agent和场景"""
        # 创建Agent
        self._create_agents()

        # 创建场景生成器
        self.scenario_generator = ScenarioGenerator(
            transforms=self.transforms,
            palaces=self.palaces,
            year=self.target_year,
        )

        # 预生成场景
        self.scenarios = self.scenario_generator.generate_scenarios(
            count=self.config.rounds
        )

    def _create_agents(self) -> None:
        """创建Agent群体"""
        # 命主Agent
        self.agents["命主"] = create_agent_from_chart(
            agent_id="mingzhu",
            role=AgentRole.MING_ZHU,
            stars=self.ming_gong_stars,
            transforms=self.transforms,
            palace_name="命宫",
            palace_stars=self.palaces.get("命宫", []),
        )

        # 事业Agent
        if self.guanlu_stars:
            self.agents["事业"] = create_agent_from_chart(
                agent_id="shiye",
                role=AgentRole.SHI_YE,
                stars=self.guanlu_stars,
                transforms=self.transforms,
                palace_name="官禄宫",
                palace_stars=self.palaces.get("官禄宫", []),
            )

        # 财运Agent
        if self.caibo_stars:
            self.agents["财运"] = create_agent_from_chart(
                agent_id="caiyun",
                role=AgentRole.CAI_YUN,
                stars=self.caibo_stars,
                transforms=self.transforms,
                palace_name="财帛宫",
                palace_stars=self.palaces.get("财帛宫", []),
            )

        # 感情Agent
        if self.fuq_gong_stars:
            self.agents["感情"] = create_agent_from_chart(
                agent_id="ganqing",
                role=AgentRole.GAN_QING,
                stars=self.fuq_gong_stars,
                transforms=self.transforms,
                palace_name="夫妻宫",
                palace_stars=self.palaces.get("夫妻宫", []),
            )

    async def run(self) -> EmergenceResult:
        """
        运行群体模拟

        Returns:
            涌现结果
        """
        if self.status == SwarmStatus.RUNNING:
            raise RuntimeError("Simulation already running")

        self.status = SwarmStatus.RUNNING

        try:
            # 确保已初始化
            if not self.agents:
                await self.initialize()

            # 运行每轮模拟
            for round_num in range(1, self.config.rounds + 1):
                self.current_round = round_num
                round_result = await self._run_round(round_num)
                self.rounds.append(round_result)

                # 检查是否暂停
                if self.status == SwarmStatus.PAUSED:
                    break

            # 计算最终涌现结果
            final_emergence = self._compute_emergence()

            self.status = SwarmStatus.COMPLETED
            return final_emergence

        except Exception:
            self.status = SwarmStatus.ERROR
            raise

    async def _run_round(self, round_num: int) -> SimulationRound:
        """运行单轮模拟"""
        round_result = SimulationRound(
            round_number=round_num,
            timestamp=datetime.now(),
        )

        # 获取本轮场景
        scenario_idx = min(round_num - 1, len(self.scenarios) - 1)
        scenario = self.scenarios[scenario_idx]
        round_result.scenarios.append(scenario)

        # 根据事件密度决定事件数量
        event_count = max(1, int(len(self.agents) * self.config.event_density))

        # 为每个事件创建交互
        agent_ids = list(self.agents.keys())
        for i in range(event_count):
            # 选择触发Agent
            trigger_id = agent_ids[i % len(agent_ids)]

            # 选择目标Agent（随机）
            target_ids = [a for a in agent_ids if a != trigger_id]
            target_id = target_ids[i % len(target_ids)] if target_ids else None

            # 生成事件
            event = self.scenario_generator.generate_event(
                scenario=scenario,
                agent_id=trigger_id,
                target_id=target_id,
            )
            event.round_number = round_num

            # 执行事件
            await self._execute_event(event)
            round_result.events.append(event)

            # 记录状态变化
            round_result.state_changes[trigger_id] = event.actual_impact

        # 计算本轮涌现
        if self.config.enable_emergence:
            round_result.emergence = self._compute_round_emergence(round_result)

        return round_result

    async def _execute_event(self, event: InteractionEvent) -> None:
        """执行交互事件"""
        # 更新触发Agent
        if event.trigger_agent_id and event.trigger_agent_id in self.agents:
            trigger_agent = self.agents[event.trigger_agent_id]

            # 创建行动
            action = AgentAction(
                agent_id=event.trigger_agent_id,
                action_type=event.event_type,
                target_id=event.target_agent_id,
                content=event.content,
                emotion=self._infer_emotion(event.scenario_type),
                impact=event.expected_impact,
            )

            # 记录记忆
            trigger_agent.add_memory(action)

            # 更新状态
            trigger_agent.update_state(event.expected_impact)

        # 更新目标Agent
        if event.target_agent_id and event.target_agent_id in self.agents:
            target_agent = self.agents[event.target_agent_id]

            # 计算反向影响
            reverse_impact = {
                k: -v * 0.5 for k, v in event.expected_impact.items()
            }

            target_agent.update_state(reverse_impact)

        # 记录实际影响
        event.actual_impact = event.expected_impact.copy()

    def _infer_emotion(self, scenario_type: ScenarioType) -> str:
        """推断情绪"""
        emotions = {
            ScenarioType.OPPORTUNITY: "兴奋",
            ScenarioType.CHALLENGE: "担忧",
            ScenarioType.COMPETITION: "紧张",
            ScenarioType.REPUTATION: "自豪",
            ScenarioType.DECISION: "纠结",
            ScenarioType.INTERACTION: "期待",
            ScenarioType.CHANGE: "期待",
        }
        return emotions.get(scenario_type, "平静")

    def _compute_round_emergence(self, round_result: SimulationRound) -> EmergenceResult:
        """计算单轮涌现"""
        if not round_result.events:
            return EmergenceResult()

        # 收集所有状态变化
        all_impacts: Dict[str, float] = {}
        for impacts in round_result.state_changes.values():
            for key, value in impacts.items():
                all_impacts[key] = all_impacts.get(key, 0) + value

        # 计算维度得分
        dimension_scores = {}
        for key, value in all_impacts.items():
            # 归一化到0-1
            score = max(0.0, min(1.0, 0.5 + value))
            dimension_scores[key] = score

        # 计算整体得分
        if dimension_scores:
            overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        else:
            overall_score = 0.5

        # 确定趋势
        if len(self.rounds) > 0:
            prev_score = self.rounds[-1].emergence.overall_score if self.rounds[-1].emergence else 0.5
            diff = overall_score - prev_score
            if diff > 0.1:
                overall_trend = "上升"
            elif diff < -0.1:
                overall_trend = "下降"
            else:
                overall_trend = "平稳"
        else:
            overall_trend = "平稳"

        # 收集关键事件
        key_events = [e.content for e in round_result.events[:3]]

        return EmergenceResult(
            overall_score=overall_score,
            overall_trend=overall_trend,
            dimension_scores=dimension_scores,
            key_events=key_events,
            confidence=0.6,
        )

    def _compute_emergence(self) -> EmergenceResult:
        """计算最终涌现结果"""
        if not self.rounds:
            return EmergenceResult()

        # 汇总所有轮次
        all_dimension_scores: Dict[str, List[float]] = {}
        all_key_events: List[str] = []

        for round_result in self.rounds:
            if round_result.emergence:
                for key, value in round_result.emergence.dimension_scores.items():
                    if key not in all_dimension_scores:
                        all_dimension_scores[key] = []
                    all_dimension_scores[key].append(value)

                all_key_events.extend(round_result.emergence.key_events)

        # 计算平均维度得分
        dimension_scores = {}
        for key, values in all_dimension_scores.items():
            dimension_scores[key] = sum(values) / len(values)

        # 计算整体得分（加权平均）
        if dimension_scores:
            weights = {
                "wealth": 0.25,
                "career": 0.25,
                "relationship": 0.2,
                "mood": 0.15,
                "health": 0.15,
            }
            overall_score = sum(
                dimension_scores.get(k, 0.5) * w
                for k, w in weights.items()
            )
        else:
            overall_score = 0.5

        # 确定整体趋势
        trends = [r.emergence.overall_trend for r in self.rounds if r.emergence]
        if trends.count("上升") > trends.count("下降"):
            overall_trend = "上升"
        elif trends.count("下降") > trends.count("上升"):
            overall_trend = "下降"
        else:
            overall_trend = "平稳"

        # 识别涌现模式
        emergence_patterns = self._identify_emergence_patterns(dimension_scores)

        # 生成建议
        suggestions = self._generate_suggestions(dimension_scores, overall_trend)

        return EmergenceResult(
            overall_score=overall_score,
            overall_trend=overall_trend,
            dimension_scores=dimension_scores,
            key_events=all_key_events[:5],
            emergence_patterns=emergence_patterns,
            suggestions=suggestions,
            confidence=0.7,
        )

    def _identify_emergence_patterns(
        self,
        dimension_scores: Dict[str, float],
    ) -> List[str]:
        """识别涌现模式"""
        patterns = []

        # 财富模式
        wealth = dimension_scores.get("wealth", 0.5)
        if wealth > 0.7:
            patterns.append("财运亨通期")
        elif wealth < 0.3:
            patterns.append("财运需谨慎")

        # 事业模式
        career = dimension_scores.get("career", 0.5)
        if career > 0.7:
            patterns.append("事业上升期")
        elif career < 0.3:
            patterns.append("事业调整期")

        # 感情模式
        relationship = dimension_scores.get("relationship", 0.5)
        if relationship > 0.7:
            patterns.append("感情甜蜜期")
        elif relationship < 0.3:
            patterns.append("感情考验期")

        # 综合模式
        values = list(dimension_scores.values())
        if values:
            std = self._standard_deviation(values)
            if std > 0.2:
                patterns.append("分化明显")
            else:
                patterns.append("均衡发展")

        return patterns

    def _standard_deviation(self, values: List[float]) -> float:
        """计算标准差"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _generate_suggestions(
        self,
        dimension_scores: Dict[str, float],
        trend: str,
    ) -> List[str]:
        """生成建议"""
        suggestions = []

        # 基于趋势
        if trend == "上升":
            suggestions.append("运势上升期，适合积极进取")
        elif trend == "下降":
            suggestions.append("运势调整期，宜静不宜动")

        # 基于维度得分
        if dimension_scores.get("wealth", 0.5) < 0.4:
            suggestions.append("财运方面需谨慎投资，避免冲动决策")

        if dimension_scores.get("career", 0.5) < 0.4:
            suggestions.append("事业上保持低调养精蓄锐")

        if dimension_scores.get("relationship", 0.5) < 0.4:
            suggestions.append("感情需要多沟通和包容")

        if dimension_scores.get("health", 0.5) < 0.4:
            suggestions.append("注意身体健康，适当运动休息")

        # 补充建议
        if not suggestions:
            suggestions.append("整体运势平稳，保持平常心")

        return suggestions

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "status": self.status.value,
            "current_round": self.current_round,
            "total_rounds": self.config.rounds,
            "agent_count": len(self.agents),
            "event_count": sum(len(r.events) for r in self.rounds),
        }

    def get_agents_summary(self) -> List[Dict[str, Any]]:
        """获取Agent摘要"""
        return [agent.to_dict() for agent in self.agents.values()]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chart_data": self.chart_data,
            "target_year": self.target_year,
            "status": self.status.value,
            "current_round": self.current_round,
            "config": {
                "rounds": self.config.rounds,
                "event_density": self.config.event_density,
            },
            "transforms": self.transforms,
            "agents": self.get_agents_summary(),
            "rounds": [
                {
                    "round_number": r.round_number,
                    "event_count": len(r.events),
                    "emergence": r.emergence.to_dict() if r.emergence else None,
                }
                for r in self.rounds
            ],
        }


# ============ Convenience Functions ============

async def run_metaphysics_swarm(
    chart_data: Dict[str, Any],
    target_year: int = 2026,
    rounds: int = 10,
) -> EmergenceResult:
    """
    运行命理群体预测

    Args:
        chart_data: 命盘数据
        target_year: 目标年份
        rounds: 模拟轮数

    Returns:
        涌现结果
    """
    config = SwarmConfig(rounds=rounds)
    engine = MetaphysicsSwarmEngine(
        chart_data=chart_data,
        target_year=target_year,
        config=config,
    )
    await engine.initialize()
    return await engine.run()


# 添加EmergenceResult的to_dict方法
EmergenceResult.to_dict = lambda self: {
    "timestamp": self.timestamp.isoformat(),
    "overall_score": self.overall_score,
    "overall_trend": self.overall_trend,
    "dimension_scores": self.dimension_scores,
    "key_events": self.key_events,
    "emergence_patterns": self.emergence_patterns,
    "suggestions": self.suggestions,
    "confidence": self.confidence,
}
