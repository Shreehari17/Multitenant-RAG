from ingestion.ingestor import ingest_document
from core.db import get_connection, release_connection

sample_text = """
Artificial intelligence is transforming industries across the world. 
Machine learning algorithms can now detect diseases earlier than human doctors.
Natural language processing enables computers to understand human speech.
Computer vision systems can identify objects in images with superhuman accuracy.
Reinforcement learning has beaten world champions in chess and Go.
Neural networks are inspired by the structure of the human brain.
Deep learning requires large amounts of data and computational power.
Transfer learning allows models trained on one task to be applied to another.
Generative AI can create realistic images, text, and audio from scratch.
Large language models are trained on vast amounts of internet text data.
""" * 5

if __name__ == "__main__":
    print("Testing full ingestion pipeline...\n")
    
    count = ingest_document(
        tenant_id="org_a",
        doc_id="ai_overview.txt",
        raw_text=sample_text
    )
    
    print(f"\nIngestion complete. {count} chunks stored.")
    
    # Verify in database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, doc_id, LEFT(chunk_text, 50) as preview
        FROM chunks
        WHERE tenant_id = 'org_a'
        AND doc_id = 'ai_overview.txt'
        ORDER BY id
    """)
    rows = cursor.fetchall()
    print(f"\nVerification - rows in database:")
    for row in rows:
        print(f"  id={row[0]} | doc={row[1]} | preview: {row[2]}...")
    cursor.close()
    release_connection(conn)