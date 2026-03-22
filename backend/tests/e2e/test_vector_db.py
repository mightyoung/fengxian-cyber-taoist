"""
End-to-end tests for VectorDB (pgvector)

These tests require a running PostgreSQL database with pgvector extension.
Set VECTOR_DB_URL environment variable to run these tests.

Note: These tests are marked with `integration` marker and are skipped by default.
Run with: pytest tests/e2e/test_vector_db.py -v -m integration
"""

import os
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestVectorDB:
    """Tests for VectorDB class"""

    @pytest.fixture
    def mock_pgconnection(self):
        """Mock psycopg2 connection"""
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.autocommit = True
            mock_connect.return_value = mock_conn
            yield mock_conn, mock_cursor

    @pytest.fixture
    def sample_embedding(self):
        """Generate a sample 55-dimensional embedding"""
        return np.random.rand(55).tolist()

    @pytest.fixture
    def sample_chart_data(self):
        """Sample chart data for testing"""
        return {
            'birth_info': {
                'year': 1990,
                'month': 4,
                'day': 18,
                'hour': 14,
                'minute': 30
            },
            'palaces': {
                '命宫': {'stars': [{'name': '紫微'}]},
                '兄弟宫': {'stars': [{'name': '天机'}]},
            },
            'stars': {},
            'transforms': []
        }

    def test_vector_db_initialization(self, mock_pgconnection):
        """Test VectorDB initialization with mock"""
        mock_conn, mock_cursor = mock_pgconnection

        from app.utils.vector_db import VectorDB

        # Test with explicit URL
        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        assert vdb.conn is not None
        mock_conn.cursor.assert_called_once()

    def test_insert_chart(self, mock_pgconnection, sample_embedding, sample_chart_data):
        """Test inserting a chart into the database"""
        mock_conn, mock_cursor = mock_pgconnection

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        result = vdb.insert_chart(
            chart_id='test_chart_001',
            birth_info=sample_chart_data['birth_info'],
            chart_data=sample_chart_data,
            embedding=sample_embedding,
            labels=['财运好', '事业旺']
        )

        assert result is True
        mock_cursor.execute.assert_called_once()

    def test_insert_chart_with_numpy_array(self, mock_pgconnection, sample_chart_data):
        """Test inserting a chart with numpy array embedding"""
        mock_conn, mock_cursor = mock_pgconnection

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        # Test with numpy array
        embedding = np.random.rand(55)

        result = vdb.insert_chart(
            chart_id='test_chart_002',
            birth_info=sample_chart_data['birth_info'],
            chart_data=sample_chart_data,
            embedding=embedding,
            labels=['婚姻稳定']
        )

        assert result is True

    def test_search_similar(self, mock_pgconnection, sample_embedding):
        """Test searching for similar charts"""
        mock_conn, mock_cursor = mock_pgconnection

        # Setup mock cursor fetchall
        mock_cursor.fetchall.return_value = [
            ('chart_001', {'year': 1990}, {'palaces': {}}, ['财运好'], 0.85),
            ('chart_002', {'year': 1985}, {'palaces': {}}, ['事业旺'], 0.78),
        ]

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        results = vdb.search_similar(
            embedding=sample_embedding,
            top_k=5,
            threshold=0.7
        )

        assert len(results) == 2
        assert results[0]['chart_id'] == 'chart_001'
        assert results[0]['similarity'] == 0.85
        assert results[1]['chart_id'] == 'chart_002'
        assert results[1]['similarity'] == 0.78

    def test_search_similar_charts_function(self, mock_pgconnection, sample_embedding):
        """Test searching using the stored function"""
        mock_conn, mock_cursor = mock_pgconnection

        mock_cursor.fetchall.return_value = [
            ('chart_001', {'year': 1990}, {'palaces': {}}, ['财运好'], 0.82),
        ]

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        results = vdb.search_similar_charts(
            embedding=sample_embedding,
            match_count=5,
            similarity_threshold=0.7
        )

        assert len(results) == 1
        assert results[0]['chart_id'] == 'chart_001'

    def test_delete_chart(self, mock_pgconnection):
        """Test deleting a chart from the database"""
        mock_conn, mock_cursor = mock_pgconnection

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        result = vdb.delete_chart('test_chart_001')

        assert result is True
        mock_cursor.execute.assert_called()

    def test_count(self, mock_pgconnection):
        """Test getting the count of charts"""
        mock_conn, mock_cursor = mock_pgconnection
        mock_cursor.fetchone.return_value = (42,)

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        count = vdb.count()

        assert count == 42

    def test_health_check(self, mock_pgconnection):
        """Test health check"""
        mock_conn, mock_cursor = mock_pgconnection
        mock_cursor.fetchone.return_value = (1,)

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        assert vdb.health_check() is True

    def test_health_check_failure(self, mock_pgconnection):
        """Test health check failure"""
        mock_conn, mock_cursor = mock_pgconnection
        mock_cursor.execute.side_effect = Exception("Connection failed")

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')

        assert vdb.health_check() is False

    def test_close(self, mock_pgconnection):
        """Test closing the connection"""
        mock_conn, mock_cursor = mock_pgconnection

        from app.utils.vector_db import VectorDB

        vdb = VectorDB(connection_url='postgresql://test:test@localhost:5432/fengxian_cyber_taoist_vectors')
        vdb.close()

        mock_conn.close.assert_called_once()

    def test_connection_url_construction(self, sample_embedding):
        """Test that VECTOR_DB_URL is correctly constructed from DATABASE_URL"""
        # Set DATABASE_URL
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/test_db'

        with patch('psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            from app.utils.vector_db import VectorDB

            vdb = VectorDB()

            # Verify connection URL was constructed correctly
            call_args = mock_connect.call_args[0][0]
            assert '/fengxian_cyber_taoist_vectors' in call_args
            assert '/bs_generator_db' not in call_args

        # Cleanup
        del os.environ['DATABASE_URL']


class TestVectorDBIntegration:
    """Integration tests for VectorDB (requires actual database)"""

    @pytest.fixture
    def vector_db_url(self):
        """Get VectorDB URL from environment"""
        return os.environ.get('VECTOR_DB_URL')

    @pytest.mark.skipif(
        not os.environ.get('VECTOR_DB_URL'),
        reason="VECTOR_DB_URL not set - skipping integration test"
    )
    def test_integration_insert_and_search(self, vector_db_url):
        """Integration test: insert a chart and search for similar charts"""
        from app.utils.vector_db import VectorDB

        vdb = VectorDB(vector_db_url)

        # Clean up first
        vdb.delete_chart('test_integration_chart')

        # Generate a random 55-dim embedding
        embedding = np.random.rand(55).tolist()

        # Insert a chart
        birth_info = {'year': 1990, 'month': 4, 'day': 18}
        chart_data = {'palaces': {'命宫': {'stars': [{'name': '紫微'}]}}}

        result = vdb.insert_chart(
            chart_id='test_integration_chart',
            birth_info=birth_info,
            chart_data=chart_data,
            embedding=embedding,
            labels=['财运好']
        )
        assert result is True

        # Search for similar charts
        results = vdb.search_similar(embedding=embedding, top_k=5, threshold=0.5)

        assert len(results) >= 1
        assert any(r['chart_id'] == 'test_integration_chart' for r in results)

        # Clean up
        vdb.delete_chart('test_integration_chart')
        vdb.close()

    @pytest.mark.skipif(
        not os.environ.get('VECTOR_DB_URL'),
        reason="VECTOR_DB_URL not set - skipping integration test"
    )
    def test_integration_upsert(self, vector_db_url):
        """Integration test: upsert updates existing chart"""
        from app.utils.vector_db import VectorDB

        vdb = VectorDB(vector_db_url)

        # Clean up first
        vdb.delete_chart('test_upsert_chart')

        # Insert a chart
        embedding = np.random.rand(55).tolist()
        vdb.insert_chart(
            chart_id='test_upsert_chart',
            birth_info={'year': 1990},
            chart_data={'palaces': {}},
            embedding=embedding,
            labels=['财运好']
        )

        # Update with new labels
        new_embedding = (np.array(embedding) + 0.1).tolist()
        vdb.insert_chart(
            chart_id='test_upsert_chart',
            birth_info={'year': 1990},
            chart_data={'palaces': {}},
            embedding=new_embedding,
            labels=['事业旺', '财运好']  # New labels
        )

        # Search and verify
        results = vdb.search_similar(embedding=new_embedding, top_k=1, threshold=0.0)
        assert len(results) >= 1

        # Clean up
        vdb.delete_chart('test_upsert_chart')
        vdb.close()


class TestVectorStoreWithPgvector:
    """Tests for VectorStore integration with pgvector"""

    @pytest.fixture
    def mock_vector_db(self):
        """Mock VectorDB"""
        mock_vdb = MagicMock()
        mock_vdb.insert_chart.return_value = True
        mock_vdb.search_similar.return_value = [
            {
                'chart_id': 'chart_001',
                'birth_info': {'year': 1990},
                'chart_data': {'palaces': {}},
                'labels': ['财运好'],
                'similarity': 0.85
            }
        ]
        mock_vdb.count.return_value = 1
        return mock_vdb

    def test_vector_store_uses_pgvector(self, mock_vector_db):
        """Test that VectorStore falls back to pgvector"""
        with patch.dict('sys.modules', {'chromadb': None}):
            with patch('app.utils.vector_db.VectorDB', return_value=mock_vector_db):
                # Re-import to pick up the mock
                import importlib
                import app.services.divination.agents.case_based_predictor as cbp

                # Create VectorStore with pgvector
                vs = cbp.VectorStore(collection_name="test_cases")

                # Verify pgvector was attempted
                assert vs._use_pgvector is True

    def test_vector_store_add_case_pgvector(self, mock_vector_db):
        """Test adding a case to pgvector"""
        with patch.dict('sys.modules', {'chromadb': None}):
            with patch('app.utils.vector_db.VectorDB', return_value=mock_vector_db):
                import app.services.divination.agents.case_based_predictor as cbp
                importlib.reload(cbp)

                vs = cbp.VectorStore(collection_name="test_cases")

                # Create a mock ChartCase
                from app.services.divination.agents.chart_vectorizer import ChartCase, ChartFeatures

                mock_features = MagicMock(spec=ChartFeatures)
                mock_features.to_vector.return_value = [0.1] * 55

                case = ChartCase(
                    case_id='test_case_001',
                    chart_id='test_chart_001',
                    features=mock_features,
                    trajectory=None,
                    metadata={
                        'birth_info': {'year': 1990},
                        'chart_data': {'palaces': {}},
                        'labels': ['财运好']
                    }
                )

                result = vs.add_case(case)
                assert result is True
                mock_vector_db.insert_chart.assert_called_once()

    def test_vector_store_search_pgvector(self, mock_vector_db):
        """Test searching for similar cases in pgvector"""
        with patch.dict('sys.modules', {'chromadb': None}):
            with patch('app.utils.vector_db.VectorDB', return_value=mock_vector_db):
                import app.services.divination.agents.case_based_predictor as cbp
                importlib.reload(cbp)

                vs = cbp.VectorStore(collection_name="test_cases")

                from app.services.divination.agents.chart_vectorizer import ChartFeatures

                mock_features = MagicMock(spec=ChartFeatures)
                mock_features.to_vector.return_value = [0.1] * 55

                results = vs.search_similar(mock_features, top_k=5)

                assert len(results) == 1
                assert results[0][0].chart_id == 'chart_001'
                assert results[0][1] == 0.85
