"""
Platforms Module - 社交媒体平台模拟

提供 Twitter/Reddit 风格社交媒体平台模拟能力。
"""

from .social_media import (
    PlatformType,
    PlatformSimulator,
    Post,
    EngagementMetrics,
    Topic,
    RoundResult,
    TWITTER_CONTENT_RULES,
    REDDIT_CONTENT_RULES,
)

from .trend_tracker import (
    TrendTracker,
    Topic,
    SentimentDataPoint,
    OpinionCluster,
    SentimentShift,
    TrendSnapshot,
    EmergenceResult,
    TOPIC_CATEGORIES,
    calculate_trending_score,
    calculate_consensus,
    detect_sentiment_shift_impl,
)

from .content_generator import (
    ContentGenerator,
    ContentItem,
    STAR_CONTENT_STYLES,
    SCENARIO_TOPICS,
    PLATFORM_LIMITS,
    GLOBAL_TOPICS,
    create_content_generator,
)

__all__ = [
    # social_media exports
    "PlatformType",
    "PlatformSimulator",
    "Post",
    "EngagementMetrics",
    "Topic",
    "RoundResult",
    "TWITTER_CONTENT_RULES",
    "REDDIT_CONTENT_RULES",
    # trend_tracker exports
    "TrendTracker",
    "SentimentDataPoint",
    "OpinionCluster",
    "SentimentShift",
    "TrendSnapshot",
    "EmergenceResult",
    "TOPIC_CATEGORIES",
    "calculate_trending_score",
    "calculate_consensus",
    "detect_sentiment_shift_impl",
    # content_generator exports
    "ContentGenerator",
    "ContentItem",
    "STAR_CONTENT_STYLES",
    "SCENARIO_TOPICS",
    "PLATFORM_LIMITS",
    "GLOBAL_TOPICS",
    "create_content_generator",
]
