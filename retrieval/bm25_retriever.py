from typing import List, Dict
from rank_bm25 import BM25Okapi
from core.db import get_connection, release_connection

def get_all_chunks_for_tenant(tenant_id: str) -> List[Dict]:
    """
    Fetch all chunks for a tenant from the database.
    BM25 needs all documents loaded in memory to build its index.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, doc_id, chunk_text
        FROM chunks
        WHERE tenant_id = %s
    """, (tenant_id,))

    rows = cursor.fetchall()
    cursor.close()
    release_connection(conn)

    return [
        {"id": row[0], "doc_id": row[1], "chunk_text": row[2]}
        for row in rows
    ]

def tokenize(text: str) -> List[str]:
    """
    Simple tokenizer — lowercase and split by whitespace.
    BM25 works on token lists, not raw strings.
    """
    return text.lower().split()

def bm25_search(tenant_id: str, query: str, top_k: int = 10) -> List[Dict]:
    """
    BM25 keyword search over all chunks for a tenant.

    Args:
        tenant_id: which organisation to search
        query: the user's question
        top_k: how many results to return

    Returns:
        list of dicts with chunk info and bm25_score
    """
    # Load all chunks for this tenant
    chunks = get_all_chunks_for_tenant(tenant_id)

    if not chunks:
        return []

    # Build BM25 index from tokenized chunk texts
    tokenized_corpus = [tokenize(chunk["chunk_text"]) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    # Score the query against all chunks
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    # Pair each chunk with its score and sort
    scored_chunks = [
        {
            "id": chunks[i]["id"],
            "doc_id": chunks[i]["doc_id"],
            "chunk_text": chunks[i]["chunk_text"],
            "bm25_score": float(scores[i])
        }
        for i in range(len(chunks))
    ]

    # Sort by score descending, return top_k
    scored_chunks.sort(key=lambda x: x["bm25_score"], reverse=True)
    return scored_chunks[:top_k]