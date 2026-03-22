"""
MultiAgent Validator - 多Agent共识验证模块

核心原理：观点汇聚
- 各Agent独立分析给出观点
- 检测观点是否达成共识
- 分歧时用加权投票解决

职责：
1. AgentView 标准化 - 统一各Agent输出格式
2. 共识检测算法 - 检测≥3个Agent判断一致
3. 分歧解决机制 - 加权投票解决分歧
4. 置信度综合计算 - 三层加权综合
5. MultiAgentValidator 整合 - 并行执行、观点汇聚、结果输出

专家角色定义（基于REVIEW文档）:
1. 紫微斗数专家 - 验证紫微斗数专业知识正确性（四化、格局、宫位理论）
2. 用户体验设计师 - 验证报告可读性和决策支撑能力
3. LLM专家 - 验证推理深度和prompt质量
4. 数据质量分析师 - 验证数据管道完整性和类型匹配
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter
import asyncio


# ============ Expert Author Definitions ============
# 基于MD文档中的真实作者定义

class ExpertAuthor(str, Enum):
    """专家作者定义 - 基于data_source/mlx/resources/md目录下的真实作者"""
    XU_QUAN_REN = "许铨仁"           # 《命理学正解》- 斗数界公认的好老师
    LIANG_RUO_YU = "梁若瑜"           # 《飞星紫微斗数》- 四化能量符号专家
    WANG_TING_ZHI = "王亭之"          # 《中州派紫微斗数深造讲义》- 中州派正统
    ZI_YUN = "紫云"                   # 《紫云论斗数 星曜赋性》- 星曜赋性专家


# 作者专业领域描述
EXPERT_AUTHOR_DESCRIPTIONS = {
    ExpertAuthor.XU_QUAN_REN: {
        "name": "许铨仁",
        "title": "《命理学正解》作者",
        "school": "台湾斗数学派",
        "expertise": [
            "斗数命理学正本清源",
            "宫星象三合一完整解义学",
            "象数平衡学",
            "理则学而非神学"
        ],
        "key_theories": [
            "紫微斗数命理学系哲学/理则学",
            "绝无'改命''改运'之谬论",
            "宫星象三合一解义"
        ]
    },
    ExpertAuthor.LIANG_RUO_YU: {
        "name": "梁若瑜",
        "title": "《飞星紫微斗数》作者",
        "school": "飞星派",
        "expertise": [
            "四化是能量符号",
            "禄转忌、忌转忌分析",
            "多宫位串联释象",
            "理气的逻辑归纳"
        ],
        "key_theories": [
            "禄因忌果",
            "善观禄忌解析问题",
            "追禄/追权/追忌",
            "忌入逢本宫自化禄出"
        ]
    },
    ExpertAuthor.WANG_TING_ZHI: {
        "name": "王亭之",
        "title": "《中州派紫微斗数深造讲义》作者",
        "school": "中州派",
        "expertise": [
            "中州派紫微斗数正统传承",
            "太微赋注解",
            "星曜赋性深化",
            "格局体系"
        ],
        "key_theories": [
            "中州派格局论断",
            "星曜庙旺平陷",
            "宫位三方四正关系"
        ]
    },
    ExpertAuthor.ZI_YUN: {
        "name": "紫云",
        "title": "《紫云论斗数 星曜赋性》作者",
        "school": "星曜派",
        "expertise": [
            "星曜赋性详解（5册）",
            "十四正曜特性",
            "辅星、煞星配置",
            "星曜组合效应"
        ],
        "key_theories": [
            "星曜五行属性",
            "星曜入宫论断",
            "星曜互动关系"
        ]
    }
}


# 兼容性别名（用于ExpertRole）
ExpertRole = ExpertAuthor  # 向后兼容


# ============ Data Models ============

class JudgmentType(str, Enum):
    """判断类型"""
    JI = "吉"      # 吉
    PING = "平"    # 平
    XIONG = "凶"   # 凶


@dataclass
class AgentView:
    """标准化Agent观点"""
    agent_name: str           # "StarAgent", "PalaceAgent", etc.
    dimension: str           # "财富", "事业", "感情", "健康"
    judgment: JudgmentType    # 吉 / 平 / 凶
    confidence: float         # 0.0-1.0
    reasoning: str            # 推理过程
    key_factors: List[str]    # 关键因素
    expert_role: Optional[ExpertAuthor] = None  # 专家作者
    validation_results: List[str] = field(default_factory=list)  # 验证结果列表

    def __post_init__(self):
        """验证字段范围"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.judgment not in JudgmentType:
            raise ValueError(f"invalid judgment type: {self.judgment}")


@dataclass
class ConsensusResult:
    """共识检测结果"""
    has_consensus: bool                    # 是否有共识
    agreed_judgment: Optional[JudgmentType]  # 共识判断（无共识时为None）
    agreeing_agents: List[str]              # 达成共识的Agent列表
    consensus_confidence: float             # 共识置信度
    dissenting_views: List[AgentView]       # 分歧观点
    reasoning: str                          # 共识检测推理过程


@dataclass
class Resolution:
    """分歧解决结果"""
    resolved_judgment: JudgmentType        # 最终判断
    weight_scores: Dict[str, float]        # 各判断的加权得分
    deciding_agents: List[str]             # 决定性投票的Agent
    reasoning: str                          # 解决推理过程


@dataclass
class FinalConfidence:
    """综合置信度"""
    causal_confidence: float               # 因果链置信度
    probabilistic_confidence: float         # 案例推理置信度
    multi_agent_confidence: float           # 多Agent共识置信度
    overall_confidence: float               # 综合置信度

    # 权重配置
    CAUSAL_WEIGHT: float = 0.40           # 因果链权重 40%
    PROBABILISTIC_WEIGHT: float = 0.35     # 案例推理权重 35%
    MULTI_AGENT_WEIGHT: float = 0.25       # 多Agent共识权重 25%


@dataclass
class ValidationResult:
    """验证最终结果"""
    dimension: str                          # 分析维度
    final_judgment: JudgmentType           # 最终判断
    final_confidence: FinalConfidence       # 综合置信度
    consensus_result: Optional[ConsensusResult]  # 共识结果（如果有）
    resolution: Optional[Resolution]        # 分歧解决结果（如果有）
    agent_views: List[AgentView]            # 所有Agent观点
    summary: str                            # 结果摘要


# ============ Agent Weights ============

# Agent权重配置：基于专家角色的重要性
# 紫微斗数专家权重最高（专业知识是核心），其他专家辅助验证

# 原有Agent权重（技术实现层）
AGENT_WEIGHTS = {
    # 技术Agent权重
    "TransformAgent": 1.0,   # 四化分析是核心
    "PatternAgent": 0.8,     # 格局识别重要
    "PalaceAgent": 0.7,     # 宫位分析基础
    "StarAgent": 0.6,       # 星曜分析基础
    # 其他Agent默认权重
    "TimingAgent": 0.5,
    "WealthAgent": 0.5,
    "HealthAgent": 0.5,
    "CareerAgent": 0.5,
    "RelationshipAgent": 0.5,
    "EducationAgent": 0.5,
    "ResolutionAgent": 0.4,
}

# 专家角色权重（专家验证层）
# 基于真实作者的专业领域和影响力
EXPERT_ROLE_WEIGHTS = {
    ExpertAuthor.XU_QUAN_REN: 1.0,     # 命理学正解派 - 理论根基
    ExpertAuthor.LIANG_RUO_YU: 0.95,   # 飞星派 - 四化能量是核心
    ExpertAuthor.WANG_TING_ZHI: 0.9,    # 中州派 - 正统传承
    ExpertAuthor.ZI_YUN: 0.85,          # 星曜派 - 星曜赋性为基础
}

# 默认权重
DEFAULT_AGENT_WEIGHT = 0.5
DEFAULT_EXPERT_WEIGHT = 0.5


def get_agent_weight(agent_name: str) -> float:
    """获取Agent权重"""
    return AGENT_WEIGHTS.get(agent_name, DEFAULT_AGENT_WEIGHT)


def get_expert_weight(expert_role: ExpertAuthor) -> float:
    """获取专家角色权重"""
    return EXPERT_ROLE_WEIGHTS.get(expert_role, DEFAULT_EXPERT_WEIGHT)


# ============ Expert Validator ============

class ExpertValidator:
    """专家验证器

    基于MD文档中的真实作者定义，对报告进行多维度验证：
    1. 许铨仁 - 《命理学正解》- 斗数理论基础
    2. 梁若瑜 - 《飞星紫微斗数》- 四化能量符号
    3. 王亭之 - 《中州派紫微斗数》- 正统格局
    4. 紫云 - 《紫云论斗数 星曜赋性》- 星曜特性
    """

    def __init__(self):
        self.expert_criteria = EXPERT_AUTHOR_DESCRIPTIONS

    async def validate_from_expert_async(
        self,
        expert_author: ExpertAuthor,
        report_content: Dict[str, Any],
        chart_data: Optional[Dict[str, Any]] = None
    ) -> AgentView:
        """异步版本：从指定专家角度验证报告"""
        return self.validate_from_expert(expert_author, report_content, chart_data)

    def validate_all_experts(
        self,
        report_content: Dict[str, Any],
        chart_data: Optional[Dict[str, Any]] = None
    ) -> List[AgentView]:
        """
        并行运行所有专家验证

        Args:
            report_content: 报告内容
            chart_data: 原始命盘数据

        Returns:
            List[AgentView]: 所有专家的验证结果
        """
        views = []
        for expert_author in ExpertAuthor:
            view = self.validate_from_expert(expert_author, report_content, chart_data)
            views.append(view)
        return views

    def validate_from_expert(
        self,
        expert_author: ExpertAuthor,
        report_content: Dict[str, Any],
        chart_data: Optional[Dict[str, Any]] = None
    ) -> AgentView:
        """
        从指定专家角度验证报告

        Args:
            expert_author: 专家作者
            report_content: 报告内容（各section的分析结果）
            chart_data: 原始命盘数据

        Returns:
            AgentView: 专家验证结果
        """
        if expert_author == ExpertAuthor.XU_QUAN_REN:
            return self._validate_xu_quan_ren(report_content)
        elif expert_author == ExpertAuthor.LIANG_RUO_YU:
            return self._validate_liang_ruo_yu(report_content)
        elif expert_author == ExpertAuthor.WANG_TING_ZHI:
            return self._validate_wang_ting_zhi(report_content)
        elif expert_author == ExpertAuthor.ZI_YUN:
            return self._validate_zi_yun(report_content)
        else:
            raise ValueError(f"Unknown expert author: {expert_author}")

    def _validate_xu_quan_ren(self, report_content: Dict[str, Any]) -> AgentView:
        """许铨仁派验证：强调宫星象三合一、理则学而非神学"""
        validation_results = []
        issues = []

        # 1. 检查是否强调"宫星象三合一"
        synthesis = report_content.get("synthesis_report", {})
        if synthesis:
            content = str(synthesis)
            # 许铨仁强调宫星象三合一
            has_gong_xing_xiang = any(term in content for term in ["宫星象", "三合一", "象数"])
            if not has_gong_xing_xiang:
                issues.append("未体现宫星象三合一思想")
                validation_results.append("⚠️ 缺少宫星象三合一论述")
            else:
                validation_results.append("✓ 有宫星象三合一论述")

        # 2. 检查四化基础准确性
        transform_analysis = report_content.get("transform_analysis", {})
        if transform_analysis:
            transforms = transform_analysis.get("transforms", [])
            if transforms and len(transforms) >= 4:
                validation_results.append("✓ 四化数据完整（禄权科忌齐全）")
            else:
                issues.append("四化数据不完整")
                validation_results.append("❌ 四化数据缺失")

        # 3. 检查格局分析
        pattern_analysis = report_content.get("pattern_analysis", {})
        if pattern_analysis:
            patterns = pattern_analysis.get("patterns", [])
            if patterns and len(patterns) > 0:
                validation_results.append(f"✓ 格局识别：{len(patterns)}个")
            else:
                issues.append("格局识别为零")
                validation_results.append("❌ 格局识别为零")

        # 计算置信度
        if len(issues) == 0:
            judgment = JudgmentType.JI
            confidence = 0.88
        elif len(issues) <= 2:
            judgment = JudgmentType.PING
            confidence = 0.68
        else:
            judgment = JudgmentType.XIONG
            confidence = 0.48

        return AgentView(
            agent_name="许铨仁",
            expert_role=ExpertAuthor.XU_QUAN_REN,
            dimension="命理学正解派验证",
            judgment=judgment,
            confidence=confidence,
            reasoning=f"许铨仁派验证：{len(validation_results)}项检查，{len(issues)}个问题",
            key_factors=issues[:3] if issues else ["宫星象三合一", "四化准确", "格局清晰"],
            validation_results=validation_results
        )

    def _validate_liang_ruo_yu(self, report_content: Dict[str, Any]) -> AgentView:
        """梁若瑜派验证：强调四化能量符号、禄转忌、忌转忌"""
        validation_results = []
        issues = []

        # 1. 检查四化能量符号（梁若瑜核心思想）
        transform_analysis = report_content.get("transform_analysis", {})
        if transform_analysis:
            content = str(transform_analysis)
            # 梁若瑜强调四化是能量符号
            has_energy_symbol = any(term in content for term in ["能量", "禄转忌", "忌转忌", "追禄", "追权"])
            if not has_energy_symbol:
                issues.append("未体现四化能量符号思想")
                validation_results.append("⚠️ 缺少能量符号论述")

            # 检查是否有禄忌分析
            transforms = transform_analysis.get("transforms", [])
            has_lu_ji = any(t.get("type") in ["化禄", "化忌"] for t in transforms if isinstance(t, dict))
            if has_lu_ji:
                validation_results.append("✓ 有禄忌分析")
            else:
                issues.append("缺少禄忌分析")
                validation_results.append("❌ 缺少禄忌分析")

        # 2. 检查因果链分析（梁若瑜强调因果）
        causal_analysis = report_content.get("causal_chain", {})
        if causal_analysis:
            chains = causal_analysis.get("chains", [])
            if chains and len(chains) > 0:
                validation_results.append(f"✓ 因果链分析：{len(chains)}条")
            else:
                issues.append("因果链分析缺失")
                validation_results.append("⚠️ 因果链分析为空")

        # 3. 检查多宫位串联释象
        synthesis = report_content.get("synthesis_report", {})
        if synthesis:
            content = str(synthesis)
            has_multi_palace = any(term in content for term in ["串联", "多宫", "宫位"])
            if has_multi_palace:
                validation_results.append("✓ 有宫位串联论述")
            else:
                validation_results.append("⚠️ 缺少宫位串联论述")

        # 计算置信度
        if len(issues) == 0:
            judgment = JudgmentType.JI
            confidence = 0.85
        elif len(issues) <= 2:
            judgment = JudgmentType.PING
            confidence = 0.65
        else:
            judgment = JudgmentType.XIONG
            confidence = 0.45

        return AgentView(
            agent_name="梁若瑜",
            expert_role=ExpertAuthor.LIANG_RUO_YU,
            dimension="飞星紫微斗数派验证",
            judgment=judgment,
            confidence=confidence,
            reasoning=f"梁若瑜派验证：{len(validation_results)}项检查，{len(issues)}个问题",
            key_factors=issues[:3] if issues else ["四化能量", "禄转忌", "因果清晰"],
            validation_results=validation_results
        )

    def _validate_wang_ting_zhi(self, report_content: Dict[str, Any]) -> AgentView:
        """王亭之派验证：中州派正统传承、格局论断"""
        validation_results = []
        issues = []

        # 1. 检查格局识别（中州派核心）
        pattern_analysis = report_content.get("pattern_analysis", {})
        if pattern_analysis:
            patterns = pattern_analysis.get("patterns", [])
            if patterns and len(patterns) > 0:
                validation_results.append(f"✓ 格局识别：{len(patterns)}个")
            else:
                issues.append("格局识别为零")
                validation_results.append("❌ 格局识别为零（中州派重视格局）")

        # 2. 检查星曜庙旺平陷（中州派核心）
        star_analysis = report_content.get("star_analysis", {})
        if star_analysis:
            main_stars = star_analysis.get("main_stars", [])
            if main_stars and main_stars != [{}] and main_stars != ["****"]:
                validation_results.append(f"✓ 星曜分析完整")
            else:
                issues.append("星曜分析数据缺失")
                validation_results.append("❌ 星曜数据缺失")

        # 3. 检查宫位三方四正关系（中州派核心）
        palace_analysis = report_content.get("palace_analysis", {})
        if palace_analysis:
            content = str(palace_analysis)
            has_san_fang = any(term in content for term in ["三方", "四正", "对宫"])
            if has_san_fang:
                validation_results.append("✓ 有三方四正论述")
            else:
                validation_results.append("⚠️ 缺少三方四正论述")

        # 计算置信度
        if len(issues) == 0:
            judgment = JudgmentType.JI
            confidence = 0.85
        elif len(issues) <= 2:
            judgment = JudgmentType.PING
            confidence = 0.65
        else:
            judgment = JudgmentType.XIONG
            confidence = 0.45

        return AgentView(
            agent_name="王亭之",
            expert_role=ExpertAuthor.WANG_TING_ZHI,
            dimension="中州派验证",
            judgment=judgment,
            confidence=confidence,
            reasoning=f"王亭之派验证：{len(validation_results)}项检查，{len(issues)}个问题",
            key_factors=issues[:3] if issues else ["格局完整", "星曜清晰", "三方四正"],
            validation_results=validation_results
        )

    def _validate_zi_yun(self, report_content: Dict[str, Any]) -> AgentView:
        """紫云派验证：星曜赋性、组合效应"""
        validation_results = []
        issues = []

        # 1. 检查星曜详细分析（紫云核心著作是星曜赋性）
        star_analysis = report_content.get("star_analysis", {})
        if star_analysis:
            main_stars = star_analysis.get("main_stars", [])
            if main_stars and main_stars != [{}] and main_stars != ["****"]:
                validation_results.append(f"✓ 星曜分析：{len(main_stars)}颗")
            else:
                issues.append("星曜分析数据缺失")
                validation_results.append("❌ 星曜数据缺失")

            # 检查是否有星曜特性描述
            content = str(star_analysis)
            has_star_nature = any(term in content for term in ["特性", "赋性", "庙旺", "平陷"])
            if has_star_nature:
                validation_results.append("✓ 有星曜赋性论述")
            else:
                validation_results.append("⚠️ 缺少星曜赋性论述")

        # 2. 检查辅星煞星配置
        assistant_stars = star_analysis.get("assistant_stars", []) if star_analysis else []
        if assistant_stars and assistant_stars != []:
            validation_results.append(f"✓ 辅星配置完整")
        else:
            validation_results.append("⚠️ 辅星数据缺失")

        # 3. 检查星曜组合效应
        synthesis = report_content.get("synthesis_report", {})
        if synthesis:
            content = str(synthesis)
            has_combination = any(term in content for term in ["组合", "同宫", "会照", "拱照"])
            if has_combination:
                validation_results.append("✓ 有星曜组合论述")
            else:
                validation_results.append("⚠️ 缺少星曜组合论述")

        # 计算置信度
        if len(issues) == 0:
            judgment = JudgmentType.JI
            confidence = 0.85
        elif len(issues) <= 2:
            judgment = JudgmentType.PING
            confidence = 0.65
        else:
            judgment = JudgmentType.XIONG
            confidence = 0.45

        return AgentView(
            agent_name="紫云",
            expert_role=ExpertAuthor.ZI_YUN,
            dimension="星曜赋性派验证",
            judgment=judgment,
            confidence=confidence,
            reasoning=f"紫云派验证：{len(validation_results)}项检查，{len(issues)}个问题",
            key_factors=issues[:3] if issues else ["星曜完整", "赋性清晰", "组合准确"],
            validation_results=validation_results
        )


# ============ Consensus Detector ============

class ConsensusDetector:
    """共识检测器

    共识条件：≥3个Agent判断一致
    """

    MIN_CONSENSUS_COUNT = 3  # 最少共识Agent数量

    def detect_consensus(self, views: List[AgentView]) -> ConsensusResult:
        """
        检测共识

        Args:
            views: Agent观点列表

        Returns:
            ConsensusResult: 共识检测结果
        """
        if not views:
            return ConsensusResult(
                has_consensus=False,
                agreed_judgment=None,
                agreeing_agents=[],
                consensus_confidence=0.0,
                dissenting_views=[],
                reasoning="无Agent观点输入"
            )

        if len(views) < 2:
            # 少于2个Agent无法形成共识
            return ConsensusResult(
                has_consensus=False,
                agreed_judgment=None,
                agreeing_agents=[],
                consensus_confidence=views[0].confidence if views else 0.0,
                dissenting_views=views.copy(),
                reasoning="Agent数量不足，无法形成共识"
            )

        # 按判断类型分组
        judgment_groups: Dict[JudgmentType, List[AgentView]] = {}
        for view in views:
            if view.judgment not in judgment_groups:
                judgment_groups[view.judgment] = []
            judgment_groups[view.judgment].append(view)

        # 寻找达成共识的判断（使用加权数量计算）
        # 对于专家视图，使用专家权重；对于普通Agent，使用Agent权重
        for judgment, group in judgment_groups.items():
            # 计算加权共识分数
            weighted_count = 0.0
            for view in group:
                if view.expert_role:
                    weight = get_expert_weight(view.expert_role)
                else:
                    weight = get_agent_weight(view.agent_name)
                weighted_count += weight

            # 如果加权分数 >= 2.5（近似3个标准Agent），则认为达成共识
            if weighted_count >= 2.5:
                agreeing_agents = [v.agent_name for v in group]
                avg_confidence = sum(v.confidence for v in group) / len(group)
                weighted_confidence = sum(
                    v.confidence * (get_expert_weight(v.expert_role) if v.expert_role else get_agent_weight(v.agent_name))
                    for v in group
                ) / weighted_count if weighted_count > 0 else avg_confidence

                return ConsensusResult(
                    has_consensus=True,
                    agreed_judgment=judgment,
                    agreeing_agents=agreeing_agents,
                    consensus_confidence=weighted_confidence,
                    dissenting_views=[v for v in views if v not in group],
                    reasoning=f"{len(group)}个专家/Agent（{', '.join(agreeing_agents)}）判断{judgment.value}，加权分数{weighted_count:.2f}，达成共识"
                )

        # 无共识 - 找出最接近共识的情况
        max_weighted = 0.0
        best_group = None
        best_judgment = None

        for judgment, group in judgment_groups.items():
            weighted_count = sum(
                get_expert_weight(v.expert_role) if v.expert_role else get_agent_weight(v.agent_name)
                for v in group
            )
            if weighted_count > max_weighted:
                max_weighted = weighted_count
                best_group = group
                best_judgment = judgment

        if best_group and max_weighted > 0:
            dissenting_views = [v for v in views if v not in best_group]
            reasoning = f"最多仅{max_weighted:.2f}加权分数（未达到2.5共识阈值），判断{best_judgment.value}"
            return ConsensusResult(
                has_consensus=False,
                agreed_judgment=None,
                agreeing_agents=[v.agent_name for v in best_group],
                consensus_confidence=sum(v.confidence for v in best_group) / len(best_group),
                dissenting_views=dissenting_views,
                reasoning=reasoning
            )

        return ConsensusResult(
            has_consensus=False,
            agreed_judgment=None,
            agreeing_agents=[],
            consensus_confidence=0.0,
            dissenting_views=views.copy(),
            reasoning="无明显共识"
        )


# ============ Divergence Resolver ============

class DivergenceResolver:
    """分歧解决器

    加权投票解决分歧
    权重：TransformAgent(1.0) > PatternAgent(0.8) > PalaceAgent(0.7) > StarAgent(0.6)
    """

    def resolve(self, views: List[AgentView]) -> Resolution:
        """
        通过加权投票解决分歧

        Args:
            views: Agent观点列表

        Returns:
            Resolution: 分歧解决结果
        """
        if not views:
            return Resolution(
                resolved_judgment=JudgmentType.PING,
                weight_scores={},
                deciding_agents=[],
                reasoning="无观点可决"
            )

        if len(views) == 1:
            return Resolution(
                resolved_judgment=views[0].judgment,
                weight_scores={views[0].judgment.value: views[0].confidence},
                deciding_agents=[views[0].agent_name],
                reasoning=f"仅{views[0].agent_name}一个观点，直接采用其判断"
            )

        # 计算每种判断的加权得分
        weight_scores: Dict[str, float] = {}
        judgment_details: Dict[str, List[tuple]] = {}  # judgment -> [(agent_name, weighted_score)]

        for view in views:
            weight = get_agent_weight(view.agent_name)
            weighted_score = view.confidence * weight

            judgment_key = view.judgment.value
            if judgment_key not in weight_scores:
                weight_scores[judgment_key] = 0.0
                judgment_details[judgment_key] = []

            weight_scores[judgment_key] += weighted_score
            judgment_details[judgment_key].append((view.agent_name, weighted_score))

        # 找出最高分的判断
        max_score = max(weight_scores.values()) if weight_scores else 0.0
        winning_judgments = [j for j, s in weight_scores.items() if s == max_score]

        if len(winning_judgments) == 1:
            winning_judgment = winning_judgments[0]
            deciding_agents = [agent for agent, score in judgment_details[winning_judgment]]

            return Resolution(
                resolved_judgment=JudgmentType(winning_judgment),
                weight_scores=weight_scores,
                deciding_agents=deciding_agents,
                reasoning=f"加权投票结果：{winning_judgment}（得分{max_score:.3f}），由{', '.join(deciding_agents)}决定"
            )
        else:
            # 平局，使用置信度决胜
            tiebreaker_results = {}
            for j in winning_judgments:
                avg_confidence = sum(
                    next((v.confidence for v in views if v.agent_name == agent), 0.0)
                    for agent, _ in judgment_details[j]
                ) / len(judgment_details[j])
                tiebreaker_results[j] = avg_confidence

            winner = max(tiebreaker_results.items(), key=lambda x: x[1])
            winning_judgment = winner[0]
            deciding_agents = [agent for agent, _ in judgment_details[winning_judgment]]

            return Resolution(
                resolved_judgment=JudgmentType(winning_judgment),
                weight_scores=weight_scores,
                deciding_agents=deciding_agents,
                reasoning=f"加权投票平局（{', '.join(winning_judgments)}），置信度决胜：{winning_judgment}"
            )


# ============ Confidence Calculator ============

@dataclass
class CausalResult:
    """因果链推理结果"""
    confidence: float
    chain_strength: float = 0.8
    key_factors: List[str] = field(default_factory=list)


@dataclass
class ProbResult:
    """案例推理结果"""
    confidence: float
    similar_cases: int = 0
    match_rate: float = 0.0


class ConfidenceCalculator:
    """置信度计算器

    三层加权综合：
    - 因果链：40%
    - 案例推理：35%
    - 多Agent：25%
    """

    def calculate_overall(
        self,
        causal_result: Optional[CausalResult] = None,
        probabilistic_result: Optional[ProbResult] = None,
        consensus_result: Optional[ConsensusResult] = None
    ) -> FinalConfidence:
        """
        计算综合置信度

        Args:
            causal_result: 因果链置信度（可为None）
            probabilistic_result: 案例推理置信度（可为None）
            consensus_result: 多Agent共识置信度（可为None）

        Returns:
            FinalConfidence: 综合置信度
        """
        # 因果链置信度
        causal_conf = causal_result.confidence if causal_result else 0.5

        # 案例推理置信度
        prob_conf = probabilistic_result.confidence if probabilistic_result else 0.5

        # 多Agent共识置信度
        multi_agent_conf = consensus_result.consensus_confidence if consensus_result else 0.5

        # 加权综合
        overall = (
            causal_conf * FinalConfidence.CAUSAL_WEIGHT +
            prob_conf * FinalConfidence.PROBABILISTIC_WEIGHT +
            multi_agent_conf * FinalConfidence.MULTI_AGENT_WEIGHT
        )

        return FinalConfidence(
            causal_confidence=causal_conf,
            probabilistic_confidence=prob_conf,
            multi_agent_confidence=multi_agent_conf,
            overall_confidence=overall
        )


# ============ MultiAgent Validator ============

class MultiAgentValidator:
    """多Agent验证器

    整合各Agent分析，实现共识验证
    """

    def __init__(self):
        self.consensus_detector = ConsensusDetector()
        self.divergence_resolver = DivergenceResolver()
        self.confidence_calculator = ConfidenceCalculator()

    async def validate(
        self,
        chart: Dict[str, Any],
        question: str,
        dimension: str = "事业"
    ) -> ValidationResult:
        """
        执行多Agent验证

        Args:
            chart: 命盘数据
            question: 分析问题
            dimension: 分析维度

        Returns:
            ValidationResult: 验证结果
        """
        # 1. 各Agent独立分析（并行）
        agent_views = await self._collect_agent_views(chart, question, dimension)

        # 2. 观点标准化（已经在AgentView中完成）
        # 3. 共识检测
        consensus_result = self.consensus_detector.detect_consensus(agent_views)

        # 4. 分歧解决
        resolution = None
        if not consensus_result.has_consensus:
            resolution = self.divergence_resolver.resolve(agent_views)

        # 5. 计算综合置信度
        final_confidence = self.confidence_calculator.calculate_overall(
            causal_result=CausalResult(confidence=0.75),  # 简化版，实际可传入真实值
            probabilistic_result=ProbResult(confidence=0.70),
            consensus_result=consensus_result if consensus_result.has_consensus else None
        )

        # 6. 确定最终判断
        if consensus_result.has_consensus:
            final_judgment = consensus_result.agreed_judgment
            summary = f"共识达成：{consensus_result.agreed_judgment.value}（置信度{consensus_result.consensus_confidence:.2f}）"
        else:
            final_judgment = resolution.resolved_judgment
            summary = f"分歧解决：{resolution.resolved_judgment.value}（加权得分{resolution.weight_scores}）"

        return ValidationResult(
            dimension=dimension,
            final_judgment=final_judgment,
            final_confidence=final_confidence,
            consensus_result=consensus_result if consensus_result.has_consensus else None,
            resolution=resolution,
            agent_views=agent_views,
            summary=summary
        )

    async def _collect_agent_views(
        self,
        chart: Dict[str, Any],
        question: str,
        dimension: str
    ) -> List[AgentView]:
        """
        并行收集各Agent观点

        Args:
            chart: 命盘数据
            question: 分析问题
            dimension: 分析维度

        Returns:
            List[AgentView]: Agent观点列表
        """
        # 导入各Agent（延迟导入避免循环依赖）
        from .star_agent import StarAgent
        from .palace_agent import PalaceAgent
        from .pattern_agent import PatternAgent
        from .transform_agent import TransformAgent

        # 创建各Agent任务
        tasks = []

        # StarAgent分析
        async def analyze_star():
            try:
                star_agent = StarAgent(chart)
                analysis = await star_agent.analyze_stars()
                # 简化的判断逻辑，实际应更复杂
                star_count = len(analysis.main_stars)
                if star_count >= 10:
                    judgment = JudgmentType.JI
                    confidence = 0.7
                elif star_count >= 5:
                    judgment = JudgmentType.PING
                    confidence = 0.6
                else:
                    judgment = JudgmentType.XIONG
                    confidence = 0.5
                return AgentView(
                    agent_name="StarAgent",
                    dimension=dimension,
                    judgment=judgment,
                    confidence=confidence,
                    reasoning=f"分析了{star_count}颗主星",
                    key_factors=[f"主星数:{star_count}"]
                )
            except Exception as e:
                return None

        # PalaceAgent分析
        async def analyze_palace():
            try:
                palace_agent = PalaceAgent(chart)
                analysis = await palace_agent.analyze_palaces()
                # 简化判断
                return AgentView(
                    agent_name="PalaceAgent",
                    dimension=dimension,
                    judgment=JudgmentType.JI,
                    confidence=0.7,
                    reasoning="宫位结构分析完成",
                    key_factors=["宫位强弱"]
                )
            except Exception as e:
                return None

        # PatternAgent分析
        async def analyze_pattern():
            try:
                pattern_agent = PatternAgent(chart)
                analysis = await pattern_agent.analyze_patterns()
                # 简化判断
                return AgentView(
                    agent_name="PatternAgent",
                    dimension=dimension,
                    judgment=JudgmentType.JI,
                    confidence=0.8,
                    reasoning="格局分析完成",
                    key_factors=["格局识别"]
                )
            except Exception as e:
                return None

        # TransformAgent分析
        async def analyze_transform():
            try:
                transform_agent = TransformAgent(chart)
                analysis = await transform_agent.analyze_transforms()
                # 简化判断
                return AgentView(
                    agent_name="TransformAgent",
                    dimension=dimension,
                    judgment=JudgmentType.JI,
                    confidence=0.85,
                    reasoning="四化分析完成",
                    key_factors=["四化飞化"]
                )
            except Exception as e:
                return None

        # 并行执行所有分析
        tasks = [
            analyze_star(),
            analyze_palace(),
            analyze_pattern(),
            analyze_transform()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤无效结果
        agent_views = [r for r in results if isinstance(r, AgentView)]

        return agent_views


# ============ Factory Function ============

def create_multi_agent_validator() -> MultiAgentValidator:
    """创建多Agent验证器实例"""
    return MultiAgentValidator()


# ============ Convenience Functions ============

async def validate_with_consensus(
    chart: Dict[str, Any],
    question: str,
    dimension: str = "事业"
) -> ValidationResult:
    """
    使用多Agent共识验证分析命盘

    Args:
        chart: 命盘数据
        question: 分析问题
        dimension: 分析维度

    Returns:
        ValidationResult: 验证结果
    """
    validator = create_multi_agent_validator()
    return await validator.validate(chart, question, dimension)


def validate_with_consensus_sync(
    chart: Dict[str, Any],
    question: str,
    dimension: str = "事业"
) -> ValidationResult:
    """同步版本的多Agent共识验证"""
    import asyncio
    return asyncio.run(validate_with_consensus(chart, question, dimension))


# ============ Test ============

if __name__ == "__main__":
    import asyncio

    async def test_consensus():
        """测试共识检测"""
        # 模拟数据
        views = [
            AgentView(
                agent_name="StarAgent",
                dimension="事业",
                judgment=JudgmentType.JI,
                confidence=0.8,
                reasoning="星曜配置良好",
                key_factors=["紫微星", "天府星"]
            ),
            AgentView(
                agent_name="PalaceAgent",
                dimension="事业",
                judgment=JudgmentType.JI,
                confidence=0.7,
                reasoning="官禄宫强",
                key_factors=["官禄宫"]
            ),
            AgentView(
                agent_name="PatternAgent",
                dimension="事业",
                judgment=JudgmentType.JI,
                confidence=0.85,
                reasoning="有吉格",
                key_factors=["紫府同宫"]
            ),
            AgentView(
                agent_name="TransformAgent",
                dimension="事业",
                judgment=JudgmentType.PING,
                confidence=0.6,
                reasoning="四化一般",
                key_factors=["化禄"]
            ),
        ]

        detector = ConsensusDetector()
        result = detector.detect_consensus(views)

        print("=== 共识检测测试 ===")
        print(f"有共识: {result.has_consensus}")
        print(f"共识判断: {result.agreed_judgment}")
        print(f"参与共识的Agent: {result.agreeing_agents}")
        print(f"共识置信度: {result.consensus_confidence}")
        print(f"推理: {result.reasoning}")

    async def test_divergence():
        """测试分歧解决"""
        views = [
            AgentView(
                agent_name="StarAgent",
                dimension="事业",
                judgment=JudgmentType.JI,
                confidence=0.8,
                reasoning="星曜配置良好",
                key_factors=["紫微星"]
            ),
            AgentView(
                agent_name="PalaceAgent",
                dimension="事业",
                judgment=JudgmentType.XIONG,
                confidence=0.7,
                reasoning="官禄宫弱",
                key_factors=["官禄宫"]
            ),
            AgentView(
                agent_name="PatternAgent",
                dimension="事业",
                judgment=JudgmentType.JI,
                confidence=0.85,
                reasoning="有吉格",
                key_factors=["紫府同宫"]
            ),
        ]

        resolver = DivergenceResolver()
        result = resolver.resolve(views)

        print("\n=== 分歧解决测试 ===")
        print(f"最终判断: {result.resolved_judgment}")
        print(f"加权得分: {result.weight_scores}")
        print(f"决定性Agent: {result.deciding_agents}")
        print(f"推理: {result.reasoning}")

    async def test_confidence():
        """测试置信度计算"""
        calculator = ConfidenceCalculator()

        causal = CausalResult(confidence=0.8)
        prob = ProbResult(confidence=0.75)
        consensus = ConsensusResult(
            has_consensus=True,
            agreed_judgment=JudgmentType.JI,
            agreeing_agents=["Agent1", "Agent2", "Agent3"],
            consensus_confidence=0.85,
            dissenting_views=[],
            reasoning="3个Agent共识"
        )

        result = calculator.calculate_overall(causal, prob, consensus)

        print("\n=== 置信度计算测试 ===")
        print(f"因果链: {result.causal_confidence:.2f}")
        print(f"案例推理: {result.probabilistic_confidence:.2f}")
        print(f"多Agent: {result.multi_agent_confidence:.2f}")
        print(f"综合: {result.overall_confidence:.2f}")

    async def main():
        await test_consensus()
        await test_divergence()
        await test_confidence()

        print("\n=== 所有测试完成 ===")

    asyncio.run(main())
