"""
Divination Agents - 紫微斗数智能体模块

包含：
- ChartAgent: 排盘智能体，负责生成完整命盘
- StarAgent: 星曜分析智能体
- PalaceAgent: 宫位分析智能体
- TransformAgent: 四化分析智能体
- PatternAgent: 格局分析智能体
- TimingAgent: 时间运势分析智能体
- SynthesisAgent: 综合分析汇总智能体
- ResolutionAgent: 化解智能体，提供化解建议
"""

from app.services.divination.agents.chart_agent import (
    ChartAgent,
    BirthInfo,
    Chart,
    generate_birth_chart,
    generate_chart_sync,
)

from app.services.divination.agents.star_agent import (
    StarAgent,
    StarAnalysis,
    StarAnalysisResult,
    analyze_chart_stars,
    analyze_stars_sync,
    llm_analyze_stars_sync,
)

from app.services.divination.agents.palace_agent import (
    PalaceAgent,
    PalaceAnalysis,
    PalaceAnalysisResult,
    analyze_chart_palaces,
    analyze_palaces_sync,
    llm_analyze_palaces_sync,
)

from app.services.divination.agents.transform_agent import (
    TransformAgent,
    TransformAnalysis,
    TransformStar,
    TransformType,
    get_transform,
    LLMTransformAnalyzer,
    llm_analyze_transforms,
    llm_analyze_transforms_sync,
)

from app.services.divination.agents.pattern_agent import (
    PatternAgent,
    PatternAnalysis,
    Pattern,
    PatternCategory,
    PatternQuality,
    analyze_patterns,
    LLMPatternAnalyzer,
    llm_analyze_patterns,
    llm_analyze_patterns_sync,
)

from app.services.divination.agents.timing_agent import (
    TimingAgent,
    TimingAnalysis,
    MajorFate,
    YearFate,
    FateLevel,
    create_timing_agent,
    LLMTimingAnalyzer,
    llm_analyze_timing,
    llm_analyze_timing_sync,
)

from app.services.divination.agents.synthesis_agent import (
    SynthesisAgent,
    SynthesisReport,
    StarAnalysis as SynthesisStarAnalysis,
    PalaceAnalysis as SynthesisPalaceAnalysis,
    PatternAnalysis as SynthesisPatternAnalysis,
    TransformAnalysis as SynthesisTransformAnalysis,
    AgentResult,
    AnalysisPriority,
    ConflictResolver,
    create_synthesis_agent,
    # LLM synthesis functions (standard pattern)
    LLMSynthesisAnalyzer,
    llm_synthesize_report,
    llm_synthesize_report_sync,
    llm_analyze_synthesis,
    llm_analyze_synthesis_sync,
)

from app.services.divination.agents.report_generator import (
    ReportBundle,
    ReportGenerator,
    generate_markdown_report,
    generate_markdown_report_sync,
    # 三层融合预测报告
    ThreeLayerPredictionReport,
    CausalChainAnalysis,
    CaseBasedAnalysis,
    MultiAgentAnalysis,
    DimensionAnalysis,
    generate_prediction_report,
    generate_prediction_report_sync,
    format_prediction_report_markdown,
)

from app.services.divination.agents.wealth_agent import (
    WealthAgent,
    WealthReport,
    WealthLevel,
    PalaceWealthAnalysis,
    WealthPattern,
    YearlyWealthForecast,
    analyze_wealth_async,
    analyze_wealth_sync,
    LLMWealthAnalyzer,
)

from app.services.divination.agents.health_agent import (
    HealthAgent,
    HealthAnalysis,
    HealthLevel,
    HealthRisk,
    HealthStar,
    PalaceHealth,
    analyze_health_async,
    analyze_health_sync,
)

from app.services.divination.agents.resolution_agent import (
    ResolutionAgent,
    ResolutionAnalysis,
    IdentifiedIssue,
    Resolution,
    Severity,
    IssueType,
    analyze_chart_resolutions,
)

from app.services.divination.agents.career_agent import (
    CareerAgent,
    CareerAnalysis,
    CareerLevel,
    CareerDirection,
    PalaceCareer,
    analyze_career_async,
    analyze_career_sync,
)

from app.services.divination.agents.relationship_agent import (
    RelationshipAgent,
    RelationshipAnalysis,
    MarriageTiming,
    MarriageQuality,
    PeachBlossomLevel,
    SpouseFeatures,
    analyze_relationship_async,
    analyze_relationship_sync,
)

from app.services.divination.agents.education_agent import (
    EducationAgent,
    EducationAnalysis,
    EducationLevel,
    LearningAbility,
    analyze_education_async,
    analyze_education_sync,
)

from app.services.divination.agents.xiaohongshu_agent import (
    XiaohongshuAgent,
    XHSReport,
    XHSSection,
    generate_xhs_report_sync,
    generate_xhs_report_async,
)

from app.services.divination.agents.chart_vectorizer import (
    ChartVectorizer,
    ChartFeatures,
    ChartFeatureQuality,
    LifeEvent,
    LifeTrajectory,
    ChartCase,
    extract_chart_features,
    compute_chart_similarity,
)

from app.services.divination.agents.case_based_predictor import (
    CaseBasedPredictor,
    VectorStore,
    TrajectoryMatcher,
    ProbabilisticResult,
    PredictionReport,
    InMemoryVectorStore,
    predict_from_chart,
    create_predictor,
)

from app.services.divination.agents.xiaohongshu_agent import (
    XiaohongshuAgent,
    XHSReport,
    XHSSection,
    generate_xhs_report_sync,
    generate_xhs_report_async,
)

from app.services.divination.agents.report_transformer import (
    ReportTransformer,
    TransformationOptions,
    transform_report_async,
    transform_report_sync,
)

from app.services.divination.agents.birth_timing_agent import (
    BirthTimingAgent,
    BirthTimingOption,
    BirthTimingResult,
    analyze_birth_timing_sync,
    LLMBirthTimingAnalyzer,
    llm_analyze_birth_timing,
    llm_analyze_birth_timing_sync,
    llm_analyze_birth_timing_enhanced,
)

from app.services.divination.agents.marriage_compatibility_agent import (
    MarriageCompatibilityAgent,
    CompatibilityResult,
    CompatibilityDimension,
    analyze_marriage_compatibility_sync,
    LLMMarriageCompatibilityAnalyzer,
    llm_analyze_marriage_compatibility,
    llm_analyze_marriage_compatibility_sync,
)

from app.services.divination.agents.career_recommendation_agent import (
    CareerRecommendationAgent,
    CareerRecommendationResult,
    EducationAdvice,
    recommend_career_sync,
)

from app.services.divination.agents.event_predictor_agent import (
    EventPredictorAgent,
    EventPredictionResult,
    EventRiskFactor,
    predict_event_sync,
    LLMEventPredictorAnalyzer,
    llm_analyze_event_predict,
    llm_analyze_event_predict_sync,
)

from app.services.divination.agents.name_recommendation_agent import (
    NameRecommendationAgent,
    NameRecommendationResult,
    NameOption,
    recommend_name_sync,
)

from app.services.divination.agents.date_selection_agent import (
    DateSelectionAgent,
    DateSelectionResult,
    DailyOption,
    select_date_sync,
    LLMDateSelectionAnalyzer,
    llm_analyze_date_selection,
    llm_analyze_date_selection_sync,
)

__all__ = [
    # chart_agent
    "ChartAgent",
    "BirthInfo",
    "Chart",
    "generate_birth_chart",
    "generate_chart_sync",
    # star_agent
    "StarAgent",
    "StarAnalysis",
    "StarAnalysisResult",
    "analyze_chart_stars",
    "analyze_stars_sync",
    "llm_analyze_stars_sync",
    # palace_agent
    "PalaceAgent",
    "PalaceAnalysis",
    "PalaceAnalysisResult",
    "analyze_chart_palaces",
    "analyze_palaces_sync",
    "llm_analyze_palaces_sync",
    # transform_agent
    "TransformAgent",
    "TransformAnalysis",
    "TransformStar",
    "TransformType",
    "get_transform",
    "LLMTransformAnalyzer",
    "llm_analyze_transforms",
    "llm_analyze_transforms_sync",
    # pattern_agent
    "PatternAgent",
    "PatternAnalysis",
    "Pattern",
    "PatternCategory",
    "PatternQuality",
    "analyze_patterns",
    "LLMPatternAnalyzer",
    "llm_analyze_patterns",
    "llm_analyze_patterns_sync",
    # timing_agent
    "TimingAgent",
    "TimingAnalysis",
    "MajorFate",
    "YearFate",
    "FateLevel",
    "create_timing_agent",
    "LLMTimingAnalyzer",
    "llm_analyze_timing",
    "llm_analyze_timing_sync",
    # synthesis_agent
    "SynthesisAgent",
    "SynthesisReport",
    "StarAnalysis",
    "PalaceAnalysis",
    "SynthesisPatternAnalysis",
    "SynthesisTransformAnalysis",
    "AgentResult",
    "AnalysisPriority",
    "ConflictResolver",
    "create_synthesis_agent",
    # LLM synthesis functions
    "LLMSynthesisAnalyzer",
    "llm_synthesize_report",
    "llm_synthesize_report_sync",
    "llm_analyze_synthesis",
    "llm_analyze_synthesis_sync",
    # report_generator
    "ReportBundle",
    "ReportGenerator",
    "generate_markdown_report",
    "generate_markdown_report_sync",
    # wealth_agent
    "WealthAgent",
    "WealthReport",
    "WealthLevel",
    "PalaceWealthAnalysis",
    "WealthPattern",
    "YearlyWealthForecast",
    "analyze_wealth_async",
    "analyze_wealth_sync",
    "LLMWealthAnalyzer",
    # health_agent
    "HealthAgent",
    "HealthAnalysis",
    "HealthLevel",
    "HealthRisk",
    "HealthStar",
    "PalaceHealth",
    "analyze_health_async",
    "analyze_health_sync",
    # resolution_agent
    "ResolutionAgent",
    "ResolutionAnalysis",
    "IdentifiedIssue",
    "Resolution",
    "Severity",
    "IssueType",
    "analyze_chart_resolutions",
    # career_agent
    "CareerAgent",
    "CareerAnalysis",
    "CareerLevel",
    "CareerDirection",
    "PalaceCareer",
    "analyze_career_async",
    "analyze_career_sync",
    # relationship_agent
    "RelationshipAgent",
    "RelationshipAnalysis",
    "MarriageTiming",
    "MarriageQuality",
    "PeachBlossomLevel",
    "SpouseFeatures",
    "analyze_relationship_async",
    "analyze_relationship_sync",
    # education_agent
    "EducationAgent",
    "EducationAnalysis",
    "EducationLevel",
    "LearningAbility",
    "analyze_education_async",
    "analyze_education_sync",
    # chart_vectorizer
    "ChartVectorizer",
    "ChartFeatures",
    "ChartFeatureQuality",
    "LifeEvent",
    "LifeTrajectory",
    "ChartCase",
    "extract_chart_features",
    "compute_chart_similarity",
    # case_based_predictor
    "CaseBasedPredictor",
    "VectorStore",
    "TrajectoryMatcher",
    "ProbabilisticResult",
    "PredictionReport",
    "InMemoryVectorStore",
    "predict_from_chart",
    "create_predictor",
    # xiaohongshu_agent
    "XiaohongshuAgent",
    "XHSReport",
    "XHSSection",
    "generate_xhs_report_sync",
    "generate_xhs_report_async",
    # report_transformer
    "ReportTransformer",
    "TransformationOptions",
    "transform_report_async",
    "transform_report_sync",
    # birth_timing_agent
    "BirthTimingAgent",
    "BirthTimingOption",
    "BirthTimingResult",
    "analyze_birth_timing_sync",
    "LLMBirthTimingAnalyzer",
    "llm_analyze_birth_timing",
    "llm_analyze_birth_timing_sync",
    "llm_analyze_birth_timing_enhanced",
    # marriage_compatibility_agent
    "MarriageCompatibilityAgent",
    "CompatibilityResult",
    "CompatibilityDimension",
    "analyze_marriage_compatibility_sync",
    "LLMMarriageCompatibilityAnalyzer",
    "llm_analyze_marriage_compatibility",
    "llm_analyze_marriage_compatibility_sync",
    # career_recommendation_agent
    "CareerRecommendationAgent",
    "CareerRecommendationResult",
    "EducationAdvice",
    "recommend_career_sync",
    # event_predictor_agent
    "EventPredictorAgent",
    "EventPredictionResult",
    "EventRiskFactor",
    "predict_event_sync",
    "LLMEventPredictorAnalyzer",
    "llm_analyze_event_predict",
    "llm_analyze_event_predict_sync",
    # name_recommendation_agent
    "NameRecommendationAgent",
    "NameRecommendationResult",
    "NameOption",
    "recommend_name_sync",
    # date_selection_agent
    "DateSelectionAgent",
    "DateSelectionResult",
    "DailyOption",
    "select_date_sync",
    "LLMDateSelectionAnalyzer",
    "llm_analyze_date_selection",
    "llm_analyze_date_selection_sync",
]
