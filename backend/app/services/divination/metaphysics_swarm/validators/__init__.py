"""
Validators - 验证器模块

命理-社会交叉验证器，用于对比命理预测与社会模拟结果。
"""

from app.services.divination.metaphysics_swarm.validators.metaphysics_validator import (
    MetaphysicsValidator,
    MetaphysicsPrediction,
    SocialSimulationResult,
    ValidationResult,
    Contradiction,
    PalaceAnalysis,
    Prediction,
    PlatformMetrics,
)

__all__ = [
    "MetaphysicsValidator",
    "MetaphysicsPrediction",
    "SocialSimulationResult",
    "ValidationResult",
    "Contradiction",
    "PalaceAnalysis",
    "Prediction",
    "PlatformMetrics",
]
