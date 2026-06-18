from sentence_transformers import CrossEncoder
from typing import List,Dict
MODEL_NAME="cross-encoder/ms-marco-MiniLM-L-6-v2"
print(f"[reranker] Loading cross-encoder model:{MODEL_NAME}")
reranker_model=CrossEncoder(MODEL_NAME)
print(f"[reranker] Model loaded successfully")

def rerank(query:str,chunks:List[Dict],top_k:int=5)->List[Dict]:
    """
    Re-score retrieved chunks using a cross-encoder model.
    
    Unlike bi-encoders which embed query and chunk separately,
    cross-encoders read both together — much more accurate relevance scoring.
    
    Args:
        query: the user's original question
        chunks: list of chunks from hybrid retrieval
        top_k: how many to return after reranking
    
    Returns:
        reranked list of chunks with cross_encoder_score added
    """
    if not chunks:
        return []
    pairs=[(query,chunk['chunk_text']) for chunk in chunks]
    scores=reranker_model.predict(pairs)
    for i,chunk in enumerate(chunks):
        chunk["cross_encoder_score"]=round(float(scores[i]),4)
    reranked=sorted(chunks,key=lambda x: x["cross_encoder_score"],reverse=True)
    print(f"[rereanker] Reranked {len(chunks)} chunks -> returning top {top_k}")
    return reranked[:top_k]