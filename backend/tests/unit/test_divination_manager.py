"""
Unit Tests - DivinationManager Persistence Layer

Tests for BirthChart and DivinationReport persistence.

Run with:
    pytest tests/unit/test_divination_manager.py -v
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime

# Ensure backend is in path
import sys
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)


class TestDivinationManagerPersistence:
    """Test DivinationManager storage operations"""

    @pytest.fixture
    def temp_storage_root(self, tmp_path):
        """Create a temporary storage directory"""
        storage_root = tmp_path / "divination_test"
        storage_root.mkdir()
        return storage_root

    @pytest.fixture
    def sample_birth_info(self):
        """Sample birth info for testing"""
        return {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 10,
            "minute": 30,
            "gender": "male",
            "birthplace": "北京",
            "is_lunar": False
        }

    @pytest.fixture
    def sample_chart_data(self):
        """Sample chart data for testing"""
        return {
            "palaces": {
                "命宫": {"stars": [], "branch": "寅"},
                "兄弟宫": {"stars": [], "branch": "卯"}
            },
            "stars": [],
            "transforms": []
        }

    def test_divination_manager_import(self):
        """Test that DivinationManager can be imported"""
        from app.models.divination import DivinationManager
        assert DivinationManager is not None

    def test_birth_chart_dataclass(self):
        """Test BirthChart dataclass creation and serialization"""
        from app.models.divination import BirthChart, DivinationStatus

        chart = BirthChart(
            chart_id="test-chart-123",
            birth_info={"year": 1990, "month": 1, "day": 1, "hour": 0, "gender": "male"},
            chart_data={"palaces": {}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            status=DivinationStatus.CHART_GENERATED
        )

        assert chart.chart_id == "test-chart-123"
        assert chart.status == DivinationStatus.CHART_GENERATED

        # Test to_dict
        chart_dict = chart.to_dict()
        assert chart_dict["chart_id"] == "test-chart-123"
        assert chart_dict["status"] == DivinationStatus.CHART_GENERATED

        # Test from_dict
        from app.models.divination import BirthChart
        restored = BirthChart.from_dict(chart_dict)
        assert restored.chart_id == chart.chart_id
        assert restored.status == chart.status

    def test_prediction_report_dataclass(self):
        """Test DivinationReport dataclass creation and serialization"""
        from app.models.divination import DivinationReport, DivinationStatus

        report = DivinationReport(
            report_id="test-report-456",
            chart_id="test-chart-123",
            user_name="测试用户",
            target_year=2026,
            report_type="professional_plain",
            markdown_content="# 测试报告\n\n内容",
            created_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            status=DivinationStatus.REPORT_COMPLETED,
            metadata={"author": "test"}
        )

        assert report.report_id == "test-report-456"
        assert report.user_name == "测试用户"
        assert report.status == DivinationStatus.REPORT_COMPLETED

        # Test to_dict
        report_dict = report.to_dict()
        assert report_dict["report_id"] == "test-report-456"
        assert report_dict["user_name"] == "测试用户"

        # Test from_dict
        from app.models.divination import DivinationReport
        restored = DivinationReport.from_dict(report_dict)
        assert restored.report_id == report.report_id
        assert restored.user_name == report.user_name

    def test_divination_status_constants(self):
        """Test DivinationStatus string constants"""
        from app.models.divination import DivinationStatus

        assert DivinationStatus.CHART_GENERATED == "chart_generated"
        assert DivinationStatus.CHART_ANALYZED == "chart_analyzed"
        assert DivinationStatus.REPORT_GENERATING == "report_generating"
        assert DivinationStatus.REPORT_COMPLETED == "report_completed"
        assert DivinationStatus.REPORT_FAILED == "report_failed"


class TestDivinationManagerWithStorage:
    """Test DivinationManager with actual file storage"""

    @pytest.fixture
    def mock_storage_paths(self, monkeypatch, tmp_path):
        """Mock the storage paths to use temp directory"""
        from app.storage import adapter

        # Create temp directories
        charts_dir = tmp_path / "divination" / "charts"
        reports_dir = tmp_path / "divination" / "reports"
        charts_dir.mkdir(parents=True)
        reports_dir.mkdir(parents=True)

        # Mock the storage adapter base paths
        original_chart_init = adapter.DivinationChartStorageAdapter.__init__
        original_report_init = adapter.DivinationReportStorageAdapter.__init__

        def mock_chart_init(self):
            original_chart_init(self)
            self._base_path = str(charts_dir)

        def mock_report_init(self):
            original_report_init(self)
            self._base_path = str(reports_dir)

        monkeypatch.setattr(adapter.DivinationChartStorageAdapter, '__init__', mock_chart_init)
        monkeypatch.setattr(adapter.DivinationReportStorageAdapter, '__init__', mock_report_init)

        # Reset the singletons so they use the new paths
        adapter._chart_storage = None
        adapter._report_storage = None

        return {
            "charts_dir": charts_dir,
            "reports_dir": reports_dir
        }

    def test_create_and_get_chart(self, mock_storage_paths, sample_birth_info, sample_chart_data):
        """Test creating and retrieving a chart"""
        from app.models.divination import DivinationManager, BirthChart

        # Create chart
        chart = DivinationManager.create_chart(
            birth_info=sample_birth_info,
            chart_data=sample_chart_data
        )

        assert chart.chart_id is not None
        assert chart.birth_info["year"] == sample_birth_info["year"]

        # Retrieve chart
        retrieved = DivinationManager.get_chart(chart.chart_id)
        assert retrieved is not None
        assert retrieved.chart_id == chart.chart_id
        assert retrieved.birth_info["gender"] == sample_birth_info["gender"]

    def test_create_and_get_report(self, mock_storage_paths):
        """Test creating and retrieving a report"""
        from app.models.divination import DivinationManager

        # Create a chart first
        chart = DivinationManager.create_chart(
            birth_info={"year": 1990, "month": 1, "day": 1, "hour": 0, "gender": "male"},
            chart_data={"palaces": {}}
        )

        # Create report
        report = DivinationManager.create_report(
            chart_id=chart.chart_id,
            user_name="测试用户",
            target_year=2026,
            report_type="professional_plain",
            markdown_content="# 测试报告",
            metadata={"test": True}
        )

        assert report.report_id is not None
        assert report.chart_id == chart.chart_id
        assert report.user_name == "测试用户"

        # Retrieve report
        retrieved = DivinationManager.get_report(report.report_id)
        assert retrieved is not None
        assert retrieved.report_id == report.report_id

    def test_list_charts(self, mock_storage_paths, sample_birth_info, sample_chart_data):
        """Test listing charts"""
        from app.models.divination import DivinationManager

        # Create multiple charts
        for i in range(3):
            DivinationManager.create_chart(
                birth_info={**sample_birth_info, "year": 1990 + i},
                chart_data=sample_chart_data
            )

        # List charts
        charts = DivinationManager.list_charts(limit=10)
        assert len(charts) == 3

    def test_delete_chart(self, mock_storage_paths, sample_birth_info, sample_chart_data):
        """Test deleting a chart"""
        from app.models.divination import DivinationManager

        # Create chart
        chart = DivinationManager.create_chart(
            birth_info=sample_birth_info,
            chart_data=sample_chart_data
        )

        chart_id = chart.chart_id

        # Delete chart
        result = DivinationManager.delete_chart(chart_id)
        assert result is True

        # Verify deleted
        retrieved = DivinationManager.get_chart(chart_id)
        assert retrieved is None
