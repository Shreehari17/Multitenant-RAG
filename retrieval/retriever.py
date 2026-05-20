from typing import List,Dict
from ingestion.embedder import embed_query
from core.db import get_connection, release_connection

def retrieve_chunks(tenant_id:str,query:str,top_k:int=5)->List[Dict]:
    """
    Retrieve the most relevant chunks for a query.
    
    Args:
        tenant_id: which organisation is querying
        query: the user's question
        top_k: how many chunks to return
    
    Returns:
        list of dicts with chunk_text, doc_id, similarity score
    """
    print(f"[retriever]: Embedding query....")
    query_vector=embed_query(query)
    #print(query_vector)
    vector_str="["+",".join(str(x)for x in query_vector)+"]"
    print(f"[retriever]: Searching database for tenant: {tenant_id}")
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        select 
                id,
                doc_id,
                chunk_text,
                1-(embedding <=> %s::vector) AS similarity
        from chunks
        WHERE tenant_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (vector_str, tenant_id, vector_str, top_k))
    rows=cursor.fetchall()
    cursor.close()
    release_connection(conn)
    results=[]
    for row in rows:
        results.append({
            "id":row[0],
            "doc_id":row[1],
            "chunk_text":row[2],
            "similarity":round(float(row[3]),4)
        })
    print(f"[retriever] Found {len(results)} chunks")
    return results
           

    
