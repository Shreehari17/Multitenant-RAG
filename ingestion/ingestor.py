from core.db import get_connection, release_connection
from ingestion.chunker import chunk_text
from ingestion.embedder import embed_chunks


def ingest_document(tenant_id:int, doc_id: int,raw_text:str)->int:
    print(f"ingestor: starting ingestion for {doc_id} of(tenant:{tenant_id}) ")
    #chunking
    chunks=chunk_text(raw_text)
    print(f"ingestor: Created {len(chunks)} chunks")
    #embedding
    embeddings=embed_chunks(chunks)
    print(f"ingestor: generated {len(embeddings)} embeddings ")
    #store 
    conn=get_connection()
    cursor=conn.cursor()
    #cursor.execute("""DELETE FROM chunks WHERE tenant_id = %s AND doc_id = %s""", (tenant_id, doc_id))

    print("ingestor: cleared old chunks")
    for chunk_text_value,embedding in zip(chunks,embeddings):
        vector_str="["+",".join(str(x)for x in embedding)+"]"
        cursor.execute("""
             INSERT into chunks(tenant_id,doc_id,chunk_text,embedding) 
            values(%s,%s,%s,%s::vector)""",(tenant_id,doc_id,chunk_text_value,vector_str))
        

    conn.commit()
    cursor.close()
    release_connection(conn)
    print(f"[ingestor] Stored {len(chunks)} chunks in database")
    return len(chunks)