from typing import List, Dict
from retrieval.retriever import retrieve_chunks
from retrieval.bm25_retriever import bm25_search

def reciprocal_rank_fusion(
    semantic_results: List[Dict],
    bm25_results: List[Dict],
    k: int = 60
) -> List[Dict]:
    """
    Merge two ranked lists using Reciprocal Rank Fusion.

    RRF score = 1/(rank_in_semantic + k) + 1/(rank_in_bm25 + k)

    Chunks appearing high in both lists get the highest combined score.
    k=60 is standard — prevents top ranks from completely dominating.

    Args:
        semantic_results: ranked list from vector similarity search
        bm25_results: ranked list from BM25 keyword search
        k: RRF constant (default 60)

    Returns:
        merged and re-ranked list of chunks
    """
    rrf_scores = {}
    chunk_data = {}

    # Score from semantic search ranking
    for rank, chunk in enumerate(semantic_results, 1):
        chunk_id = chunk["id"]
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (rank + k)
        chunk_data[chunk_id] = chunk

    # Score from BM25 ranking
    for rank, chunk in enumerate(bm25_results, 1):
        chunk_id = chunk["id"]
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (rank + k)
        if chunk_id not in chunk_data:
            chunk_data[chunk_id] = chunk

    # Sort by combined RRF score
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

    results = []
    for chunk_id in sorted_ids:
        chunk = chunk_data[chunk_id].copy()
        chunk["rrf_score"] = round(rrf_scores[chunk_id], 6)
        results.append(chunk)

    return results


def hybrid_retrieve(tenant_id: str, query: str, top_k: int = 5) -> List[Dict]:
    """
    Hybrid retrieval combining semantic search and BM25 via RRF.

    Args:
        tenant_id: which organisation is querying
        query: the user's question
        top_k: final number of chunks to return

    Returns:
        list of top_k chunks ranked by RRF score
    """
    print(f"[hybrid_retriever] Running semantic search...")
    semantic_results = retrieve_chunks(
        tenant_id=tenant_id,
        query=query,
        top_k=10
    )

    print(f"[hybrid_retriever] Running BM25 search...")
    bm25_results = bm25_search(
        tenant_id=tenant_id,
        query=query,
        top_k=10
    )

    print(f"[hybrid_retriever] Semantic: {len(semantic_results)} chunks, "
          f"BM25: {len(bm25_results)} chunks")

    # Merge with RRF
    merged = reciprocal_rank_fusion(semantic_results, bm25_results)

    print(f"[hybrid_retriever] After RRF fusion: returning top {top_k}")
    return merged[:top_k]