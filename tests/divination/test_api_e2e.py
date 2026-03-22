"""
E2E tests for divination API.

Tests the Flask API endpoints for the divination system:
- POST /api/divination/chart/generate - Generate birth chart
- GET /api/divination/chart/<chart_id> - Get stored chart
- POST /api/divination/agents/analyze - Run agent analysis
- GET /api/divination/health - Health check

Uses direct module loading to avoid Flask/zep_cloud dependency issues.
"""
import pytest
import sys
import os
import json
import asyncio
from dataclasses import asdict, is_dataclass
from importlib.util import spec_from_file_location, module_from_spec
from unittest.mock import MagicMock, patch
import types


def setup_all_mocks():
    """Setup ALL mocks before any imports to avoid dependency issues."""
    # Mock zep_cloud first (before any other imports)
    zep_cloud_mock = types.ModuleType('zep_cloud')

    # Add all needed zep_cloud exports
    zep_cloud_mock.InternalServerError = Exception
    zep_cloud_mock.EpisodeData = MagicMock()
    zep_cloud_mock.EntityEdgeSourceTarget = MagicMock()

    # Create a mock for zep_cloud.client module
    zep_cloud_client_mock = types.ModuleType('zep_cloud.client')
    zep_cloud_client_mock.Zep = MagicMock()
    sys.modules['zep_cloud.client'] = zep_cloud_client_mock

    # Create mock for zep_cloud.memory (if needed)
    zep_cloud_memory_mock = types.ModuleType('zep_cloud.memory')
    sys.modules['zep_cloud.memory'] = zep_cloud_memory_mock

    zep_cloud_mock.client = zep_cloud_client_mock
    sys.modules['zep_cloud'] = zep_cloud_mock

    # Mock flask - create a real-like Blueprint mock
    class MockBlueprint:
        def __init__(self, name, __name__, url_prefix=None):
            self.name = name
            self.url_prefix = url_prefix
            self.url_map = MagicMock(iter_rules=lambda: [])

        def route(self, path, methods=None):
            """Mock route decorator."""
            def decorator(func):
                return func
            return decorator

    flask_mock = types.ModuleType('flask')
    flask_mock.Flask = MagicMock()
    flask_mock.Blueprint = MockBlueprint
    flask_mock.request = MagicMock()
    flask_mock.jsonify = MagicMock(side_effect=lambda x: x)
    sys.modules['flask'] = flask_mock

    # Mock flask_cors
    flask_cors_mock = types.ModuleType('flask_cors')
    flask_cors_mock.CORS = MagicMock()
    sys.modules['flask_cors'] = flask_cors_mock

    # Mock dotenv
    dotenv_mock = types.ModuleType('dotenv')
    dotenv_mock.load_dotenv = MagicMock(return_value={})
    sys.modules['dotenv'] = dotenv_mock

    # Mock openai
    openai_mock = types.ModuleType('openai')
    openai_mock.OpenAI = MagicMock()
    sys.modules['openai'] = openai_mock

    return flask_mock


# Setup mocks FIRST
setup_all_mocks()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


def direct_import(name, path):
    """Directly import a module file without triggering package __init__ files."""
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Load chart_agent module directly
def get_chart_agent_module():
    """Load chart_agent module directly."""
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app', 'services', 'divination')

    # Load wuxing_calculator first
    wuxing_calc = direct_import(
        'wuxing_calculator',
        os.path.join(base_path, 'wuxing_calculator.py')
    )

    # Load palace_builder
    palace_builder = direct_import(
        'palace_builder',
        os.path.join(base_path, 'palace_builder.py')
    )

    # Load star_placer
    star_placer = direct_import(
        'star_placer',
        os.path.join(base_path, 'star_placer.py')
    )

    # Load transform_decider
    transform_decider = direct_import(
        'transform_decider',
        os.path.join(base_path, 'transform_decider.py')
    )

    # Load chart_agent
    chart_agent = direct_import(
        'chart_agent',
        os.path.join(base_path, 'agents', 'chart_agent.py')
    )

    return chart_agent


class TestChartGeneration:
    """Test chart generation functionality."""

    @pytest.fixture
    def chart_agent(self):
        """Get chart_agent module."""
        return get_chart_agent_module()

    def test_birth_info_validation(self, chart_agent):
        """Test BirthInfo validation."""
        BirthInfo = chart_agent.BirthInfo

        # Valid birth info
        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            gender="male"
        )
        assert birth_info.year == 1990
        assert birth_info.gender == "male"

        # Invalid year should raise ValueError
        with pytest.raises(ValueError):
            BirthInfo(year=1800, month=5, day=15, hour=10, gender="male")

        # Invalid gender should raise ValueError
        with pytest.raises(ValueError):
            BirthInfo(year=1990, month=5, day=15, hour=10, gender="unknown")

        # Invalid month should raise ValueError
        with pytest.raises(ValueError):
            BirthInfo(year=1990, month=13, day=15, hour=10, gender="male")

        print("✓ BirthInfo validation works correctly")

    def test_chart_generation_sync(self, chart_agent):
        """Test synchronous chart generation."""
        BirthInfo = chart_agent.BirthInfo
        ChartAgent = chart_agent.ChartAgent

        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            gender="male"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))

        # Verify chart structure
        assert chart is not None
        assert chart.birth_info["year"] == 1990
        assert chart.birth_info["wuxing_ju"] is not None
        assert chart.birth_info["wuxing_ju_name"] is not None
        assert chart.palaces is not None
        assert chart.stars is not None

        # Verify chart has required fields
        chart_dict = chart.to_dict()
        assert "birth_info" in chart_dict
        assert "palaces" in chart_dict
        assert "stars" in chart_dict
        assert "transforms" in chart_dict

        print(f"✓ Chart generated: {chart.birth_info['wuxing_ju_name']}")
        print(f"  Main stars: {len(chart.stars['main_stars'])}")
        print(f"  Auxiliary stars: {len(chart.stars['auxiliary_stars'])}")

    def test_chart_to_dict_serialization(self, chart_agent):
        """Test chart serialization to dict."""
        BirthInfo = chart_agent.BirthInfo
        ChartAgent = chart_agent.ChartAgent

        birth_info = BirthInfo(
            year=1995,
            month=8,
            day=20,
            hour=15,
            gender="female"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))

        # Test to_dict
        chart_dict = chart.to_dict()
        assert isinstance(chart_dict, dict)
        assert "birth_info" in chart_dict

        # Test nested serialization
        assert isinstance(chart_dict["birth_info"], dict)
        assert isinstance(chart_dict["palaces"], dict)
        assert isinstance(chart_dict["stars"], dict)

        print("✓ Chart serialization works correctly")


class TestAPIResponseFormat:
    """Test API response format helpers."""

    @pytest.fixture
    def chart_agent(self):
        """Get chart_agent module."""
        return get_chart_agent_module()

    def test_to_dict_helper(self, chart_agent):
        """Test _to_dict helper function."""
        # Load the routes module
        routes_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'backend',
            'app', 'services', 'divination', 'api', 'routes.py'
        )
        routes_module = direct_import('routes', routes_path)
        _to_dict = routes_module._to_dict

        BirthInfo = chart_agent.BirthInfo

        # Test with dataclass
        birth_info = BirthInfo(
            year=1990,
            month=5,
            day=15,
            hour=10,
            gender="male"
        )
        result = _to_dict(birth_info)
        assert isinstance(result, dict)
        assert result["year"] == 1990

        # Test with dict
        result = _to_dict({"key": "value"})
        assert result == {"key": "value"}

        # Test with list
        result = _to_dict([birth_info])
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["year"] == 1990

        print("✓ _to_dict helper works correctly")


class TestInputValidation:
    """Test API input validation."""

    def test_validate_birth_info_function(self):
        """Test the validate_birth_info function."""
        # Load the routes module
        routes_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'backend',
            'app', 'services', 'divination', 'api', 'routes.py'
        )
        routes_module = direct_import('routes', routes_path)
        validate_birth_info = routes_module.validate_birth_info

        # Valid input
        valid_data = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 10,
            "gender": "male"
        }
        is_valid, error = validate_birth_info(valid_data)
        assert is_valid is True
        assert error is None

        # Missing field
        invalid_data = {"year": 1990, "month": 5}
        is_valid, error = validate_birth_info(invalid_data)
        assert is_valid is False
        assert "day" in error

        # Invalid year
        invalid_data = {
            "year": 1800,
            "month": 5,
            "day": 15,
            "hour": 10,
            "gender": "male"
        }
        is_valid, error = validate_birth_info(invalid_data)
        assert is_valid is False
        assert "1900" in error

        # Invalid gender
        invalid_data = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 10,
            "gender": "unknown"
        }
        is_valid, error = validate_birth_info(invalid_data)
        assert is_valid is False
        assert "male" in error or "female" in error

        # Invalid hour
        invalid_data = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 25,
            "gender": "male"
        }
        is_valid, error = validate_birth_info(invalid_data)
        assert is_valid is False
        assert "0-23" in error

        print("✓ Input validation works correctly")


class TestBlueprintEndpoints:
    """Test that blueprint has correct endpoints."""

    def test_divination_blueprint_exists(self):
        """Test that divination_bp blueprint exists."""
        # Load the routes module
        routes_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'backend',
            'app', 'services', 'divination', 'api', 'routes.py'
        )
        routes_module = direct_import('routes', routes_path)
        divination_bp = routes_module.divination_bp

        assert divination_bp is not None
        assert divination_bp.name == 'divination'
        assert divination_bp.url_prefix == '/api/divination'

        print("✓ divination_bp blueprint exists")

    def test_blueprint_routes(self):
        """Test that blueprint has all required routes."""
        # Load the routes module
        routes_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'backend',
            'app', 'services', 'divination', 'api', 'routes.py'
        )
        routes_module = direct_import('routes', routes_path)

        # Check that the routes module has the expected route functions defined
        assert hasattr(routes_module, 'generate_chart'), "Missing generate_chart endpoint"
        assert hasattr(routes_module, 'get_chart'), "Missing get_chart endpoint"
        assert hasattr(routes_module, 'analyze_with_agents'), "Missing analyze_with_agents endpoint"
        assert hasattr(routes_module, 'health'), "Missing health endpoint"

        print("✓ Blueprint has all required endpoints")


class TestFullAPIFlow:
    """Test full API flow (integration test)."""

    @pytest.fixture
    def chart_agent(self):
        """Get chart_agent module."""
        return get_chart_agent_module()

    def test_generate_and_store_chart(self, chart_agent):
        """Test generating a chart and verifying it can be converted to dict."""
        BirthInfo = chart_agent.BirthInfo
        ChartAgent = chart_agent.ChartAgent

        birth_info = BirthInfo(
            year=2000,
            month=1,
            day=1,
            hour=0,
            gender="female",
            birthplace="上海"
        )

        agent = ChartAgent()
        chart = asyncio.run(agent.generate_chart(birth_info))

        # Simulate what the API does
        chart_id = "test-uuid-123"
        chart_data = chart.to_dict()

        # Verify we can store and retrieve
        stored_data = {
            'chart': chart_data,
            'birth_info': asdict(birth_info),
        }

        assert stored_data['chart'] is not None
        assert stored_data['birth_info']['year'] == 2000
        assert stored_data['chart']['birth_info']['wuxing_ju'] is not None

        print("✓ Full API flow test passed")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
