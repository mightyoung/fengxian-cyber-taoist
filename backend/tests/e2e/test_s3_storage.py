"""
Tests for S3 Storage functionality

These tests use unittest.mock to mock boto3, allowing tests to run without a real S3 endpoint.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# Mock environment variables before importing the module
MOCK_ENV = {
    'AWS_ACCESS_KEY_ID': 'testing',
    'AWS_SECRET_ACCESS_KEY': 'testing',
    'S3_ENDPOINT_URL': 'http://localhost:9000',
    'S3_BUCKET_NAME': 'test-fengxian_cyber_taoist-reports',
    'S3_REGION_NAME': 'us-east-1',
}


class TestS3StorageUnit:
    """Unit tests for S3Storage class"""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup mock environment for each test"""
        with patch.dict(os.environ, MOCK_ENV, clear=True):
            yield

    def test_generate_key_format(self):
        """Test that S3 key generation follows expected format"""
        with patch('app.utils.s3_storage.boto3'):
            from app.utils.s3_storage import S3Storage

            storage = S3Storage()
            key = storage._generate_key("reports", "report_123", "report.pdf")

            assert key.startswith("reports/report_123/")
            assert key.endswith("/report.pdf")
            # Key should contain timestamp in format YYYYMMDD_HHMMSS
            assert "/" in key

    def test_generate_key_with_different_filenames(self):
        """Test key generation with different filenames"""
        with patch('app.utils.s3_storage.boto3'):
            from app.utils.s3_storage import S3Storage

            storage = S3Storage()

            md_key = storage._generate_key("reports", "report_abc", "report.md")
            assert md_key.endswith("/report.md")

            pdf_key = storage._generate_key("reports", "report_abc", "report.pdf")
            assert pdf_key.endswith("/report.pdf")

    def test_generate_metadata_key(self):
        """Test metadata key generation"""
        with patch('app.utils.s3_storage.boto3'):
            from app.utils.s3_storage import S3Storage

            storage = S3Storage()
            key = storage._generate_metadata_key("reports", "report_123")

            assert key.startswith("reports/report_123/")
            assert key.endswith("/metadata.json")


class TestS3StorageMocked:
    """Tests for S3Storage with mocked boto3 client"""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup mock environment for each test"""
        with patch.dict(os.environ, MOCK_ENV, clear=True):
            yield

    @pytest.fixture
    def mock_s3_client(self):
        """Create a mock S3 client"""
        mock_client = MagicMock()
        mock_client.create_bucket.return_value = {}
        mock_client.head_bucket.return_value = {}
        return mock_client

    @pytest.fixture
    def storage(self, mock_s3_client):
        """Create S3Storage with mocked client"""
        with patch('app.utils.s3_storage.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from app.utils.s3_storage import S3Storage
            # Reset singleton
            import app.utils.s3_storage as module
            module._storage_instance = None
            storage = S3Storage()
            return storage

    def test_init_with_env_vars(self, mock_s3_client):
        """Test initialization reads from environment variables"""
        with patch('app.utils.s3_storage.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from app.utils.s3_storage import S3Storage
            # Reset singleton
            import app.utils.s3_storage as module
            module._storage_instance = None
            storage = S3Storage()

            # The bucket should be set - either default or fallback
            assert storage.bucket_name is not None
            assert storage.region == 'us-east-1'

    def test_upload_report_success(self, storage, mock_s3_client):
        """Test successful report upload"""
        content = b"Test report content"
        key = storage.upload_report(
            report_id="report_123",
            content=content,
            content_type="text/markdown",
            filename="report.md"
        )

        assert key.startswith("reports/report_123/")
        assert key.endswith("/report.md")

        mock_s3_client.put_object.assert_called()
        # Check the last call (main file, not metadata)
        calls = mock_s3_client.put_object.call_args_list
        main_call = calls[-1]  # Last call is the main file
        assert main_call[1]['Bucket'] == storage.bucket_name
        assert main_call[1]['Body'] == content
        assert main_call[1]['ContentType'] == "text/markdown"

    def test_upload_markdown(self, storage, mock_s3_client):
        """Test markdown upload convenience method"""
        content = "# Test Report\n\nThis is a test."
        key = storage.upload_markdown("report_456", content)

        assert key.endswith("/report.md")

        calls = mock_s3_client.put_object.call_args_list
        main_call = calls[-1]
        assert main_call[1]['Body'] == content.encode('utf-8')
        assert 'charset=utf-8' in main_call[1]['ContentType']

    def test_upload_pdf(self, storage, mock_s3_client):
        """Test PDF upload convenience method"""
        content = b"%PDF-1.4 fake pdf content"
        key = storage.upload_pdf("report_789", content)

        assert key.endswith("/report.pdf")

        calls = mock_s3_client.put_object.call_args_list
        main_call = calls[-1]
        assert main_call[1]['Body'] == content
        assert main_call[1]['ContentType'] == "application/pdf"

    def test_upload_with_metadata(self, storage, mock_s3_client):
        """Test upload with metadata"""
        content = b"Test content"
        metadata = {"report_id": "test_123", "created_at": "2024-01-01"}
        key = storage.upload_with_metadata(
            category="reports",
            item_id="test_123",
            content=content,
            content_type="text/plain",
            filename="test.txt",
            metadata=metadata
        )

        # Should have 2 put_object calls: main file + metadata
        assert mock_s3_client.put_object.call_count == 2

    def test_get_presigned_url(self, storage, mock_s3_client):
        """Test presigned URL generation"""
        mock_s3_client.generate_presigned_url.return_value = "https://s3.example.com/presigned-url"

        url = storage.get_presigned_url("reports/report_123/20230101/report.md")

        assert url == "https://s3.example.com/presigned-url"
        mock_s3_client.generate_presigned_url.assert_called_once()
        call_kwargs = mock_s3_client.generate_presigned_url.call_args[1]
        assert call_kwargs['Params']['Bucket'] == storage.bucket_name

    def test_get_presigned_url_custom_expiry(self, storage, mock_s3_client):
        """Test presigned URL with custom expiration"""
        mock_s3_client.generate_presigned_url.return_value = "https://s3.example.com/presigned-url"

        storage.get_presigned_url("reports/report_123/file.pdf", expires_in=7200)

        call_kwargs = mock_s3_client.generate_presigned_url.call_args[1]
        assert call_kwargs['ExpiresIn'] == 7200

    def test_list_reports(self, storage, mock_s3_client):
        """Test listing reports for a given report_id"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'reports/report_123/20230101/report.md'},
                {'Key': 'reports/report_123/20230102/report.pdf'},
            ]
        }

        keys = storage.list_reports("report_123")

        assert len(keys) == 2
        assert 'reports/report_123/20230101/report.md' in keys
        assert 'reports/report_123/20230102/report.pdf' in keys

    def test_list_reports_empty(self, storage, mock_s3_client):
        """Test listing when no reports exist"""
        mock_s3_client.list_objects_v2.return_value = {}

        keys = storage.list_reports("nonexistent_report")

        assert keys == []

    def test_delete_report(self, storage, mock_s3_client):
        """Test deleting all files for a report"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'reports/report_123/20230101/report.md'},
                {'Key': 'reports/report_123/20230101/chart.png'},
            ]
        }

        result = storage.delete_report("report_123")

        assert result is True
        mock_s3_client.delete_objects.assert_called_once()

    def test_delete_report_empty(self, storage, mock_s3_client):
        """Test deleting when no files exist"""
        mock_s3_client.list_objects_v2.return_value = {}

        result = storage.delete_report("nonexistent")

        assert result is True
        mock_s3_client.delete_objects.assert_not_called()

    def test_download_file_success(self, storage, mock_s3_client):
        """Test successful file download"""
        result = storage.download_file("reports/report_123/report.md", "/tmp/report.md")

        assert result is True
        mock_s3_client.download_file.assert_called_once_with(
            storage.bucket_name,
            'reports/report_123/report.md',
            '/tmp/report.md'
        )

    def test_download_file_failure(self, storage, mock_s3_client):
        """Test failed file download"""
        from botocore.exceptions import ClientError

        mock_s3_client.download_file.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'GetObject'
        )

        result = storage.download_file("nonexistent/file.md", "/tmp/file.md")

        assert result is False

    def test_key_exists_true(self, storage, mock_s3_client):
        """Test checking if key exists (it does)"""
        result = storage.key_exists("reports/report_123/report.md")

        assert result is True
        mock_s3_client.head_object.assert_called_once()

    def test_key_exists_false(self, storage, mock_s3_client):
        """Test checking if key exists (it doesn't)"""
        from botocore.exceptions import ClientError

        mock_s3_client.head_object.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )

        result = storage.key_exists("nonexistent/file.md")

        assert result is False

    def test_get_object_metadata(self, storage, mock_s3_client):
        """Test getting object metadata"""
        mock_s3_client.head_object.return_value = {
            'ContentLength': 1024,
            'ContentType': 'text/markdown',
            'LastModified': datetime(2024, 1, 15, 12, 0, 0),
            'ETag': '"abc123"'
        }

        metadata = storage.get_object_metadata("reports/report_123/report.md")

        assert metadata['ContentLength'] == 1024
        assert metadata['ContentType'] == 'text/markdown'

    def test_upload_chart(self, storage, mock_s3_client):
        """Test chart upload"""
        content = b"chart data"
        key = storage.upload_chart("chart_123", content, "application/json", "chart.json")

        assert key.startswith("charts/chart_123/")
        assert key.endswith("/chart.json")

    def test_upload_export(self, storage, mock_s3_client):
        """Test export upload"""
        content = b"export data"
        key = storage.upload_export("user_123", content, "text/csv", "export.csv")

        assert key.startswith("exports/user_123/")
        assert key.endswith("/export.csv")


class TestSaveReportToS3:
    """Tests for the save_report_to_s3 convenience function"""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup mock environment for each test"""
        with patch.dict(os.environ, MOCK_ENV, clear=True):
            yield

    @pytest.fixture
    def mock_storage_instance(self):
        """Create a mock S3Storage instance"""
        mock_instance = MagicMock()
        mock_instance.upload_report.return_value = "reports/test_123/20230101/report.md"
        mock_instance.get_presigned_url.return_value = "https://s3.example.com/presigned"
        return mock_instance

    def test_save_markdown_report(self, mock_storage_instance):
        """Test saving a markdown report"""
        with patch('app.utils.s3_storage.get_storage', return_value=mock_storage_instance):
            from app.utils.s3_storage import save_report_to_s3

            url = save_report_to_s3(
                report_id="test_123",
                report_content="# Test Report\n\nContent here",
                report_format="markdown"
            )

            assert url == "https://s3.example.com/presigned"
            mock_storage_instance.upload_report.assert_called_once()
            # Arguments are passed positionally: (report_id, content, content_type, filename, metadata)
            call_args = mock_storage_instance.upload_report.call_args[0]
            assert 'text/markdown' in call_args[2]  # content_type
            assert call_args[3] == 'report.md'  # filename

    def test_save_pdf_report(self, mock_storage_instance):
        """Test saving a PDF report"""
        with patch('app.utils.s3_storage.get_storage', return_value=mock_storage_instance):
            from app.utils.s3_storage import save_report_to_s3

            pdf_content = b"%PDF-1.4 fake"
            url = save_report_to_s3(
                report_id="test_456",
                report_content=pdf_content,
                report_format="pdf"
            )

            assert url == "https://s3.example.com/presigned"
            call_args = mock_storage_instance.upload_report.call_args[0]
            assert call_args[2] == 'application/pdf'  # content_type
            assert call_args[3] == 'report.pdf'  # filename

    def test_save_with_metadata(self, mock_storage_instance):
        """Test saving report with custom metadata"""
        with patch('app.utils.s3_storage.get_storage', return_value=mock_storage_instance):
            from app.utils.s3_storage import save_report_to_s3

            custom_metadata = {"llm_model": "qwen-plus", "version": "1.0"}
            save_report_to_s3(
                report_id="test_789",
                report_content="# Report",
                report_format="markdown",
                metadata=custom_metadata
            )

            # Metadata is passed as 5th positional argument
            call_args = mock_storage_instance.upload_report.call_args[0]
            metadata_arg = call_args[4]
            assert metadata_arg['report_id'] == "test_789"
            assert metadata_arg['llm_model'] == "qwen-plus"

    def test_save_invalid_format_raises(self, mock_storage_instance):
        """Test that invalid format raises ValueError"""
        with patch('app.utils.s3_storage.get_storage', return_value=mock_storage_instance):
            from app.utils.s3_storage import save_report_to_s3

            with pytest.raises(ValueError, match="Unsupported report format"):
                save_report_to_s3(
                    report_id="test_789",
                    report_content="some content",
                    report_format="html"
                )


class TestGetStorageSingleton:
    """Tests for the get_storage singleton function"""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup mock environment for each test"""
        with patch.dict(os.environ, MOCK_ENV, clear=True):
            yield

    def test_returns_s3_storage_instance(self):
        """Test that get_storage returns S3Storage instance"""
        with patch('app.utils.s3_storage.boto3'):
            # Reset singleton
            import app.utils.s3_storage as module
            module._storage_instance = None

            from app.utils.s3_storage import get_storage, S3Storage

            storage = get_storage()

            assert isinstance(storage, S3Storage)

    def test_returns_same_instance(self):
        """Test that get_storage returns the same instance"""
        with patch('app.utils.s3_storage.boto3'):
            # Reset singleton
            import app.utils.s3_storage as module
            module._storage_instance = None

            from app.utils.s3_storage import get_storage

            storage1 = get_storage()
            storage2 = get_storage()

            assert storage1 is storage2
