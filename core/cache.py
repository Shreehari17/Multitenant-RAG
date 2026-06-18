import os
import json
import numpy as np
import redis
from typing import Optional, Dict, List
from dotenv import load_dotenv
from ingestion.embedder import embed_query

load_dotenv()

SIMILARITY_THRESHOLD = 0.95
CACHE_TTL = 3600  # 1 hour in seconds

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_cached_answer(query: str) -> Optional[Dict]:
    """
    Check if a semantically similar query was answered before.
    
    Steps:
    1. Embed the incoming query
    2. Scan all cached query embeddings in Redis
    3. If any cached embedding has similarity > threshold, return cached answer
    
    Args:
        query: the user's question
    
    Returns:
        cached result dict if found, None otherwise
    """
    try:
        query_vector = embed_query(query)

        # Get all cached query keys
        cache_keys = redis_client.keys("query:*")

        if not cache_keys:
            return None

        best_similarity = 0.0
        best_key = None

        for key in cache_keys:
            cached_data = redis_client.get(key)
            if not cached_data:
                continue

            cached = json.loads(cached_data)
            cached_vector = cached.get("embedding")

            if not cached_vector:
                continue

            similarity = _cosine_similarity(query_vector, cached_vector)

            if similarity > best_similarity:
                best_similarity = similarity
                best_key = key

        if best_similarity >= SIMILARITY_THRESHOLD:
            cached_data = redis_client.get(best_key)
            cached = json.loads(cached_data)
            print(f"[cache] HIT — similarity: {best_similarity:.4f}")
            return {
                "query": query,
                "answer": cached["answer"],
                "sources": cached["sources"],
                "chunks_used": cached["chunks_used"],
                "cache_hit": True,
                "similarity": round(best_similarity, 4)
            }

        print(f"[cache] MISS — best similarity: {best_similarity:.4f}")
        return None

    except Exception as e:
        print(f"[cache] Error checking cache: {e}")
        return None


def store_cached_answer(query: str, result: Dict) -> bool:
    """
    Store a query-answer pair in Redis with the query embedding.
    
    Args:
        query: the user's question
        result: the full result dict from generate_answer
    
    Returns:
        True if stored successfully, False otherwise
    """
    try:
        query_vector = embed_query(query)

        cache_key = f"query:{hash(query)}"

        cache_data = {
            "query": query,
            "embedding": query_vector,
            "answer": result["answer"],
            "sources": result["sources"],
            "chunks_used": result["chunks_used"]
        }

        redis_client.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(cache_data)
        )

        print(f"[cache] Stored answer for: {query[:50]}...")
        return True

    except Exception as e:
        print(f"[cache] Error storing cache: {e}")
        return False


def clear_cache() -> int:
    """Clear all cached queries. Returns number of keys deleted."""
    try:
        keys = redis_client.keys("query:*")
        if keys:
            redis_client.delete(*keys)
        return len(keys)
    except Exception as e:
        print(f"[cache] Error clearing cache: {e}")
        return 0