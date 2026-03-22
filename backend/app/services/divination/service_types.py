"""
service_types.py - 紫微斗数扩展服务共用类型定义
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, unique


# ============ 基础枚举 ============

@unique
class FortuneLevel(str, Enum):
    """运势等级枚举"""
    EXCELLENT = "极佳"     # 85-100
    GOOD = "良好"          # 70-84
    AVERAGE = "中等"       # 50-69
    FAIR = "一般"          # 30-49
    POOR = "较差"          # 0-29


@unique
class ServiceType(str, Enum):
    """服务类型枚举"""
    FORTUNE = "fortune"                    # 年度运势（已有）
    BIRTH_TIMING = "birth_timing"          # 剖腹产良辰
    EVENT_PREDICTION = "event_prediction"  # 事件成功率
    DATE_SELECTION = "date_selection"      # 择日分析
    MARRIAGE_COMPATIBILITY = "marriage_compatibility"  # 姻缘配对
    NAME_RECOMMENDATION = "name_recommendation"        # 改名起名
    CAREER_RECOMMENDATION = "career_recommendation"    # 职业推荐


@unique
class ScoreCategory(str, Enum):
    """评分类别枚举"""
    OVERALL = "overall"                    # 综合
    TIMING = "timing"                      # 时机
    COMPATIBILITY = "compatibility"        # 适配度
    RISK = "risk"                          # 风险
    POTENTIAL = "potential"                # 潜力
    HARMONY = "harmony"                    # 和谐度


# ============ 事件类型枚举 ============

@unique
class EventType(str, Enum):
    """事件类型枚举（用于 EVENT_PREDICTION）"""
    CAREER_CHANGE = "career_change"        # 跳槽
    LAWSUIT = "lawsuit"                    # 官司诉讼
    BUSINESS_SIGNING = "business_signing"  # 商务签约
    INVESTMENT = "investment"             # 投资理财
    EXAM = "exam"                          # 考试升学
    MARRIAGE = "marriage"                  # 结婚嫁娶
    RELOCATION = "relocation"             # 搬家乔迁
    TRAVEL = "travel"                      # 出行远行


# ============ 吉日类型枚举 ============

@unique
class AuspiciousDateType(str, Enum):
    """吉日类型枚举（用于 DATE_SELECTION）"""
    WEDDING = "wedding"                    # 结婚吉日
    BUSINESS_OPENING = "business_opening"  # 开市吉日
    GROUND_BREAKING = "ground_breaking"    # 动土吉日
    TRAVEL = "travel"                      # 出行吉日
    SIGNING = "signing"                    # 签约吉日


# ============ 职业类型枚举 ============

@unique
class CareerType(str, Enum):
    """职业类型枚举"""
    MANAGEMENT = "management"             # 管理类
    TECHNICAL = "technical"                # 技术类
    CREATIVE = "creative"                  # 创意艺术类
    SALES = "sales"                        # 销售商务类
    FINANCE = "finance"                    # 金融投资类
    ACADEMIC = "academic"                  # 学术教育类
    MEDICAL = "medical"                    # 医疗健康类
    LEGAL = "legal"                        # 法律咨询类
    MEDIA = "media"                        # 媒体传播类
    GOVERNMENT = "government"              # 政府公共类


# ============ 数据结构 ============

@dataclass(frozen=True)
class EvaluationResult:
    """
    通用的评估结果数据结构

    用于返回单一评估场景的结果，如事件成功率分析、姻缘配对等。
    """
    service_type: str
    overall_score: float                   # 综合分数 0-100
    overall_level: str                     # 综合等级（极佳/良好/中等/一般/较差）
    dimension_scores: Dict[str, float]     # 分维度分数
    dimension_levels: Dict[str, str]       # 分维度等级
    reasoning: str                         # 分析理由
    confidence: float                     # 置信度 0-1
    recommendations: List[str]             # 建议列表
    metadata: Dict[str, Any] = field(default_factory=dict)  # 附加元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为纯字典（不含 dataclass 内部机制）"""
        return {
            "service_type": self.service_type,
            "overall_score": self.overall_score,
            "overall_level": self.overall_level,
            "dimension_scores": self.dimension_scores,
            "dimension_levels": self.dimension_levels,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class RankedOption:
    """
    带排名的选项数据结构

    用于返回多个选项的场景，如吉日推荐、名字推荐、职业推荐等。
    """
    rank: int                              # 排名 1-indexed
    option: str                             # 选项内容（如日期+时辰或名字）
    score: float                           # 分数 0-100
    level: str                             # 等级
    reasons: List[str]                    # 入选理由
    suitability_notes: str = ""            # 注意事项

    def to_dict(self) -> Dict[str, Any]:
        """转换为纯字典（不含 dataclass 内部机制）"""
        return {
            "rank": self.rank,
            "option": self.option,
            "score": self.score,
            "level": self.level,
            "reasons": self.reasons,
            "suitability_notes": self.suitability_notes,
        }


@dataclass(frozen=True)
class ServiceResponse:
    """
    统一的服务响应格式

    所有服务统一返回此格式，便于前端处理。
    """
    success: bool                          # 是否成功
    service_type: str                      # 服务类型
    result: Optional[EvaluationResult] = None  # 评估结果（单一场景）
    ranked_options: List[RankedOption] = field(default_factory=list)  # 排名选项（多选项场景）
    error: Optional[str] = None           # 错误信息

    def to_dict(self) -> Dict[str, Any]:
        """转换为纯字典（不含 dataclass 内部机制）"""
        return {
            "success": self.success,
            "service_type": self.service_type,
            "result": self.result.to_dict() if self.result else None,
            "ranked_options": [opt.to_dict() for opt in self.ranked_options],
            "error": self.error,
        }


# ============ 便捷函数 ============

def fortune_level_from_score(score: float) -> str:
    """
    根据分数返回等级字符串

    Args:
        score: 分数 0-100

    Returns:
        等级字符串（极佳/良好/中等/一般/较差）
    """
    if score >= 85:
        return FortuneLevel.EXCELLENT.value
    elif score >= 70:
        return FortuneLevel.GOOD.value
    elif score >= 50:
        return FortuneLevel.AVERAGE.value
    elif score >= 30:
        return FortuneLevel.FAIR.value
    else:
        return FortuneLevel.POOR.value


def normalize_score(score: float) -> float:
    """
    将分数归一化到 0-100 范围

    Args:
        score: 原始分数

    Returns:
        归一化后的分数，范围 [0, 100]
    """
    return max(0.0, min(100.0, float(score)))
