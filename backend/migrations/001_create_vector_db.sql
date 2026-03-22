-- Create dedicated database for vector storage
-- Run: psql $DATABASE_URL -f migrations/001_create_vector_db.sql

-- Connect to postgres first
\c postgres

-- Create new database
DROP DATABASE IF EXISTS fengxian_cyber_taoist_vectors;
CREATE DATABASE fengxian_cyber_taoist_vectors;
\c fengxian_cyber_taoist_vectors

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create chart cases table
CREATE TABLE chart_cases (
    id SERIAL PRIMARY KEY,
    chart_id VARCHAR(64) UNIQUE NOT NULL,
    birth_info JSONB NOT NULL,
    chart_data JSONB NOT NULL,
    embedding vector(55) NOT NULL,
    labels TEXT[],  -- e.g., ['财运好', '婚姻稳定']
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for vector search
CREATE INDEX ON chart_cases USING hnsw (embedding vector_cosine_ops);

-- Create similarity search function
CREATE OR REPLACE FUNCTION find_similar_charts(
    query_embedding vector(55),
    match_count int DEFAULT 5,
    similarity_threshold float DEFAULT 0.7
) RETURNS TABLE (
    chart_id VARCHAR(64),
    birth_info JSONB,
    chart_data JSONB,
    labels TEXT[],
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cc.chart_id,
        cc.birth_info,
        cc.chart_data,
        cc.labels,
        1 - (cc.embedding <=> query_embedding) AS similarity
    FROM chart_cases cc
    WHERE 1 - (cc.embedding <=> query_embedding) >= similarity_threshold
    ORDER BY cc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;