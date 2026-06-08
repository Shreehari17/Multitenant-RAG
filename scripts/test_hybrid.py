from retrieval.hybrid_retriever import hybrid_retrieve
from generation.generator import generate_answer

if __name__ == "__main__":

    test_cases = [
        {
            "tenant_id": "org_a",
            "query": "What does heapq.heappop do in A star?"
        },
        {
            "tenant_id": "org_a",
            "query": "What is the heuristic function?"
        },
        {
            "tenant_id": "org_b",
            "query": "What activities were done at the walkathon?"
        }
    ]

    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Query: {test['query']}")
        print(f"{'='*60}")

        chunks = hybrid_retrieve(
            tenant_id=test["tenant_id"],
            query=test["query"],
            top_k=3
        )

        print(f"\nTop chunks after RRF fusion:")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n  Rank {i} (rrf_score: {chunk['rrf_score']})")
            print(f"  Doc: {chunk['doc_id']}")
            print(f"  Preview: {chunk['chunk_text'][:80]}...")

        result = generate_answer(query=test["query"], chunks=chunks)
        print(f"\nAnswer: {result['answer']}")
        print(f"Sources: {result['sources']}")