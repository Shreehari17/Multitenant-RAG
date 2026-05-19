-- Run this once after docker compose up to set up the database

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768)
);

-- Create IVFFlat index for fast similarity search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx 
ON chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);