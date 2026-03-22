"""
pytest configuration to handle Flask import issues.
"""
import sys
import os
import types
from importlib.util import spec_from_file_location, module_from_spec
from unittest.mock import MagicMock

# Create mock modules before any imports
# This prevents Flask and other heavy dependencies from being loaded
flask_mock = types.ModuleType('flask')
flask_mock.Flask = MagicMock()
flask_mock.request = MagicMock()
sys.modules['flask'] = flask_mock

flask_cors_mock = types.ModuleType('flask_cors')
flask_cors_mock.CORS = MagicMock()
sys.modules['flask_cors'] = flask_cors_mock

dotenv_mock = types.ModuleType('dotenv')
dotenv_mock.load_dotenv = MagicMock(return_value={})
sys.modules['dotenv'] = dotenv_mock

openai_mock = types.ModuleType('openai')
openai_mock.OpenAI = MagicMock()
sys.modules['openai'] = openai_mock

# Mock redis module
redis_mock = types.ModuleType('redis')
redis_mock.Redis = MagicMock()
redis_mock.ConnectionPool = MagicMock()
redis_mock.ConnectionError = Exception
redis_mock.RedisError = Exception
sys.modules['redis'] = redis_mock

# Mock zep_cloud module - need to add more classes
zep_cloud_mock = types.ModuleType('zep_cloud')
zep_client_mock = types.ModuleType('zep_cloud.client')
zep_client_mock.Zep = MagicMock()

# Add external_clients mock
zep_external_mock = types.ModuleType('zep_cloud.external_clients')
zep_ontology_mock = types.ModuleType('zep_cloud.external_clients.ontology')
zep_ontology_mock.EntityModel = MagicMock()
zep_ontology_mock.EntityText = MagicMock()
zep_ontology_mock.EdgeModel = MagicMock()
zep_external_mock.ontology = zep_ontology_mock

# Add the missing classes as mocks
zep_cloud_mock.EpisodeData = MagicMock()
zep_cloud_mock.EntityEdgeSourceTarget = MagicMock()
zep_cloud_mock.client = zep_client_mock
zep_cloud_mock.external_clients = zep_external_mock

sys.modules['zep_cloud'] = zep_cloud_mock
sys.modules['zep_cloud.client'] = zep_client_mock
sys.modules['zep_cloud.external_clients'] = zep_external_mock
sys.modules['zep_cloud.external_clients.ontology'] = zep_ontology_mock


def direct_import(module_name, module_path):
    """Directly import a module file without triggering package __init__ files."""
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def setup_divination_modules():
    """Load divination modules directly to avoid Flask imports."""
    base_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'services', 'divination')

    # Load modules in dependency order
    modules = {}

    # 1. wuxing_calculator
    wuxing_calc = direct_import(
        'wuxing_calculator',
        os.path.join(base_path, 'wuxing_calculator.py')
    )
    modules['WuXingCalculator'] = wuxing_calc.WuXingCalculator
    modules['WuXingJuType'] = wuxing_calc.WuXingJuType

    # 2. palace_builder
    palace_builder = direct_import(
        'palace_builder',
        os.path.join(base_path, 'palace_builder.py')
    )
    modules['PalaceBuilder'] = palace_builder.PalaceBuilder
    modules['Gender'] = palace_builder.Gender
    modules['YinYang'] = palace_builder.YinYang
    modules['PALACE_NAMES'] = palace_builder.PALACE_NAMES

    # 3. star_placer
    star_placer = direct_import(
        'star_placer',
        os.path.join(base_path, 'star_placer.py')
    )
    modules['StarPlacer'] = star_placer.StarPlacer
    modules['FiveElementType'] = star_placer.FiveElementType
    modules['StarType'] = star_placer.StarType
    modules['StarLevel'] = star_placer.StarLevel
    modules['PALACE_ORDER'] = star_placer.PALACE_ORDER

    # 4. transform_decider
    transform_decider = direct_import(
        'transform_decider',
        os.path.join(base_path, 'transform_decider.py')
    )
    modules['TransformDecider'] = transform_decider.TransformDecider
    modules['TransformType'] = transform_decider.TransformType

    # Note: chart_agent requires zep_cloud - skip loading it here
    # It can be imported in tests using pytest.importorskip

    return modules


# Pre-load modules before tests run
DIVINATION_MODULES = setup_divination_modules()
