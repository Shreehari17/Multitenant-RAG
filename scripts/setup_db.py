from core.db import get_connection, release_connection

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Setting up database...")
    
    # Enable pgvector
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("✓ pgvector extension enabled")
    
    # Create chunks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id BIGSERIAL PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding vector(768)
        );
    """)
    print("✓ chunks table created")
    
    # Create IVFFlat index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx 
        ON chunks 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)
    print("✓ IVFFlat index created")
    
    conn.commit()
    cursor.close()
    release_connection(conn)
    print("\nDatabase setup complete.")

if __name__ == "__main__":
    setup_database()