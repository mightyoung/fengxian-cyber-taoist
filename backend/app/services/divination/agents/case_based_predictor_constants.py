"""
CaseBasedPredictor Constants - 案例推理预测器常量定义

包含：
- CHROMADB_AVAILABLE: ChromaDB可用性标志
- DEFAULT_DALIAN_START_AGE: 默认大限起始年龄
- DEFAULT_DALIAN_YEARS: 每个大限的年数
- MIN_CONFIDENCE: 最小置信度
- DEFAULT_EVENT_TYPES: 默认事件类型列表
- EVENT_DESCRIPTIONS: 事件描述映射

注意：Dataclasses 请使用 case_based_predictor_types 模块
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# 尝试导入ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available, using in-memory fallback")

# 大限参数（默认值）
DEFAULT_DALIAN_START_AGE = 15  # 默认大限起始年龄
DEFAULT_DALIAN_YEARS = 10      # 每个大限的年数

# 置信度计算
MIN_CONFIDENCE = 0.3  # 最小置信度（信息不完整时的基础不确定性）

# 默认事件类型
DEFAULT_EVENT_TYPES: List[str] = ["财运", "事业", "感情", "健康"]

# 事件描述映射
EVENT_DESCRIPTIONS: Dict[str, str] = {
    "财运": "有财运机遇",
    "事业": "事业有发展",
    "感情": "感情有变化",
    "健康": "健康需注意"
}

# 概率等级阈值
PROBABILITY_HIGH = 0.7
PROBABILITY_MEDIUM = 0.5
PROBABILITY_LOW = 0.3

# 概率等级描述
PROBABILITY_LEVELS: Dict[str, str] = {
    "high": "大概率",
    "medium": "较可能",
    "low": "可能",
    "very_low": "小概率"
}

# 种子数据路径
SEED_DATA_PATHS: List[str] = [
    "data_source/cases/seed",
    "data_source/cases",
]

# 向量相似度阈值
SIMILARITY_THRESHOLD = 0.7
TOP_K_CASES = 10

# 大限容差（支持±1大限容差，即±10年）
DALIAN_TOLERANCE = 1
DALIAN_DISTANCE_PENALTY = 0.2

# 轨迹相似度计算
TRAJECTORY_AGE_RANGE = (20, 60)

# 预测置信度因子
CONFIDENCE_COUNT_FACTOR_MAX = 0.4
CONFIDENCE_SIMILARITY_FACTOR_MAX = 0.6

# 基础概率计算
BASE_PROB_FACTOR = 0.6
SIGNIFICANCE_FACTOR = 0.4
MAX_EVENTS_FOR_BASE_PROB = 10.0
