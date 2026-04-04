"""
业务服务模块

Note: For testing purposes, this module uses lazy imports to avoid
dependency chain issues with zep_cloud and other external services.
Import from specific submodules directly when testing.
"""

# Lazy import for weasyprint-dependent modules (macOS may not have libgobject)
# NOTE: ReportService was removed - simulation reports now use ReportManager (report_agent.py)
# Lazy import for zep_cloud-dependent modules (only needed at runtime, not for tests)
try:
    from .graph_builder import GraphBuilderService
except ImportError:
    GraphBuilderService = None

try:
    from .zep_entity_reader import ZepEntityReader, EntityNode, FilteredEntities
except ImportError:
    ZepEntityReader = None
    EntityNode = None
    FilteredEntities = None

try:
    from .zep_graph_memory_updater import (
        ZepGraphMemoryUpdater,
        ZepGraphMemoryManager,
        AgentActivity
    )
except ImportError:
    ZepGraphMemoryUpdater = None
    ZepGraphMemoryManager = None
    AgentActivity = None

try:
    from .oasis_profile_generator import OasisProfileGenerator, OasisAgentProfile
except ImportError:
    OasisProfileGenerator = None
    OasisAgentProfile = None

# Non-lazy imports for modules without external dependencies
from .ontology_generator import OntologyGenerator
from .text_processor import TextProcessor

# Lazy import for simulation modules (depend on zep_cloud indirectly)
try:
    from .simulation_manager import SimulationManager, SimulationState, SimulationStatus
except ImportError:
    SimulationManager = None
    SimulationState = None
    SimulationStatus = None

try:
    from .simulation_config_generator import (
        SimulationConfigGenerator,
        SimulationParameters,
        AgentActivityConfig,
        TimeSimulationConfig,
        EventConfig,
        PlatformConfig
    )
except ImportError:
    SimulationConfigGenerator = None
    SimulationParameters = None
    AgentActivityConfig = None
    TimeSimulationConfig = None
    EventConfig = None
    PlatformConfig = None

try:
    from .simulation_runner import (
        SimulationRunner,
        SimulationRunState,
        RunnerStatus,
        AgentAction,
        RoundSummary
    )
except ImportError:
    SimulationRunner = None
    SimulationRunState = None
    RunnerStatus = None
    AgentAction = None
    RoundSummary = None

from .simulation_ipc import (
    SimulationIPCClient,
    SimulationIPCServer,
    IPCCommand,
    IPCResponse,
    CommandType,
    CommandStatus
)

__all__ = [
    # 'ReportService', 'get_report_service', 'ReportFormat', 'ReportType', 'ReportStatus', 'Report'
    # (lazy-loaded, may be None if weasyprint unavailable)
    'OntologyGenerator',
    'GraphBuilderService',  # May be None if zep_cloud unavailable
    'TextProcessor',
    'ZepEntityReader',  # May be None if zep_cloud unavailable
    'EntityNode',  # May be None if zep_cloud unavailable
    'FilteredEntities',  # May be None if zep_cloud unavailable
    'OasisProfileGenerator',  # May be None if zep_cloud unavailable
    'OasisAgentProfile',  # May be None if zep_cloud unavailable
    'SimulationManager',  # May be None if zep_cloud unavailable
    'SimulationState',  # May be None if zep_cloud unavailable
    'SimulationStatus',  # May be None if zep_cloud unavailable
    'SimulationConfigGenerator',  # May be None if zep_cloud unavailable
    'SimulationParameters',  # May be None if zep_cloud unavailable
    'AgentActivityConfig',  # May be None if zep_cloud unavailable
    'TimeSimulationConfig',  # May be None if zep_cloud unavailable
    'EventConfig',  # May be None if zep_cloud unavailable
    'PlatformConfig',  # May be None if zep_cloud unavailable
    'SimulationRunner',  # May be None if zep_cloud unavailable
    'SimulationRunState',  # May be None if zep_cloud unavailable
    'RunnerStatus',  # May be None if zep_cloud unavailable
    'AgentAction',  # May be None if zep_cloud unavailable
    'RoundSummary',  # May be None if zep_cloud unavailable
    'ZepGraphMemoryUpdater',  # May be None if zep_cloud unavailable
    'ZepGraphMemoryManager',  # May be None if zep_cloud unavailable
    'AgentActivity',  # May be None if zep_cloud unavailable
    'SimulationIPCClient',
    'SimulationIPCServer',
    'IPCCommand',
    'IPCResponse',
    'CommandType',
    'CommandStatus',
]

