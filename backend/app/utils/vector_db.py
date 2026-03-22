"""
VectorDB - pgvector-based vector database for chart similarity search

This module provides a VectorDB class that uses pgvector for storing and
searching chart embeddings with high-dimensional vector similarity.
"""

import os
import logging
from typing import Optional

import psycopg2
from psycopg2.extras import Json
import numpy as np

logger = logging.getLogger(__name__)


class VectorDB:
    """pgvector-based vector database for chart similarity search"""

    def __init__(self, connection_url: Optional[str] = None):
        """
        Initialize VectorDB connection.

        Args:
            connection_url: PostgreSQL connection URL. If not provided,
                           reads from VECTOR_DB_URL or constructs from DATABASE_URL.
        """
        if connection_url is None:
            # Construct from DATABASE_URL: replace db name with fengxian_cyber_taoist_vectors
            base_url = os.environ.get('DATABASE_URL', '')
            if base_url:
                # Replace database name to point to vector DB
                if '/bs_generator_db' in base_url:
                    connection_url = base_url.replace('/bs_generator_db', '/fengxian_cyber_taoist_vectors')
                elif '/intelligence_db' in base_url:
                    connection_url = base_url.replace('/intelligence_db', '/fengxian_cyber_taoist_vectors')
                else:
                    connection_url = base_url
            else:
                connection_url = os.environ.get('VECTOR_DB_URL', '')

        if not connection_url:
            raise ValueError(
                "No database URL provided. Set VECTOR_DB_URL or DATABASE_URL environment variable."
            )

        self._connection_url = connection_url
        self.conn = psycopg2.connect(connection_url)
        self.conn.autocommit = True
        logger.info("VectorDB connected to pgvector database")

    def insert_chart(
        self,
        chart_id: str,
        birth_info: dict,
        chart_data: dict,
        embedding: list[float],
        labels: Optional[list[str]] = None
    ) -> bool:
        """
        Insert a chart with its embedding.

        Args:
            chart_id: Unique chart identifier
            birth_info: Birth information dict
            chart_data: Full chart data dict
            embedding: 55-dimensional feature vector
            labels: Optional list of labels (e.g., ['财运好', '婚姻稳定'])

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cur = self.conn.cursor()
            # Convert numpy arrays to lists if needed
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()

            cur.execute("""
                INSERT INTO chart_cases (chart_id, birth_info, chart_data, embedding, labels)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (chart_id) DO UPDATE SET
                    chart_data = EXCLUDED.chart_data,
                    embedding = EXCLUDED.embedding,
                    labels = EXCLUDED.labels,
                    updated_at = NOW()
            """, (chart_id, Json(birth_info), Json(chart_data), embedding, labels or []))
            cur.close()
            logger.debug(f"Inserted chart {chart_id} into vector database")
            return True
        except Exception as e:
            logger.error(f"Failed to insert chart {chart_id}: {e}")
            return False

    def search_similar(
        self,
        embedding: list[float],
        top_k: int = 5,
        threshold: float = 0.7
    ) -> list[dict]:
        """
        Search for similar charts using vector similarity.

        Args:
            embedding: Query embedding vector
            top_k: Maximum number of results to return
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of dicts containing chart_id, birth_info, chart_data, labels, similarity
        """
        try:
            cur = self.conn.cursor()
            # Convert numpy arrays to lists if needed
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()

            cur.execute("""
                SELECT chart_id, birth_info, chart_data, labels,
                       1 - (embedding <=> %s) as similarity
                FROM chart_cases
                WHERE 1 - (embedding <=> %s) >= %s
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (embedding, embedding, threshold, embedding, top_k))

            results = []
            for row in cur.fetchall():
                results.append({
                    'chart_id': row[0],
                    'birth_info': row[1],
                    'chart_data': row[2],
                    'labels': row[3] or [],
                    'similarity': float(row[4])
                })
            cur.close()
            return results
        except Exception as e:
            logger.error(f"Failed to search similar charts: {e}")
            return []

    def search_similar_charts(
        self,
        embedding: list[float],
        match_count: int = 5,
        similarity_threshold: float = 0.7
    ) -> list[dict]:
        """
        Search for similar charts using the stored function.

        Args:
            embedding: Query embedding vector
            match_count: Maximum number of results
            similarity_threshold: Minimum similarity threshold (0-1)

        Returns:
            List of similar charts with similarity scores
        """
        try:
            cur = self.conn.cursor()
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()

            cur.execute("""
                SELECT * FROM find_similar_charts(%s, %s, %s)
            """, (embedding, match_count, similarity_threshold))

            results = []
            for row in cur.fetchall():
                results.append({
                    'chart_id': row[0],
                    'birth_info': row[1],
                    'chart_data': row[2],
                    'labels': row[3] or [],
                    'similarity': float(row[4])
                })
            cur.close()
            return results
        except Exception as e:
            logger.error(f"Failed to search similar charts: {e}")
            return []

    def delete_chart(self, chart_id: str) -> bool:
        """
        Delete a chart from the database.

        Args:
            chart_id: Chart identifier to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM chart_cases WHERE chart_id = %s", (chart_id,))
            cur.close()
            logger.debug(f"Deleted chart {chart_id} from vector database")
            return True
        except Exception as e:
            logger.error(f"Failed to delete chart {chart_id}: {e}")
            return False

    def count(self) -> int:
        """
        Get the total number of charts in the database.

        Returns:
            int: Number of stored charts
        """
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM chart_cases")
            count = cur.fetchone()[0]
            cur.close()
            return count
        except Exception as e:
            logger.error(f"Failed to count charts: {e}")
            return 0

    def health_check(self) -> bool:
        """
        Check if the database connection is healthy.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            return True
        except Exception as e:
            logger.error(f"VectorDB health check failed: {e}")
            return False

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("VectorDB connection closed")


def get_vector_db() -> VectorDB:
    """
    Get a VectorDB instance using environment configuration.

    Returns:
        VectorDB: Configured vector database instance

    Raises:
        ValueError: If no database URL is configured
    """
    return VectorDB()
