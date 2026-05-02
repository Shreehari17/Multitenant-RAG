from retrieval.retriever import retrieve_chunks
from generation.generator import generate_answer

if __name__ == "__main__":
    
    test_cases = [
        {
            "tenant_id": "org_a",
            "query": "What is artificial intelligence?"
        },
        {
            "tenant_id": "org_a", 
            "query": "What is the liability cap in the contract?"
        },
        {
            "tenant_id": "org_a",
            "query": "What is the weather like today?"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Query: {test['query']}")
        print(f"{'='*60}")
        
        chunks = retrieve_chunks(
            tenant_id=test['tenant_id'],
            query=test['query'],
            top_k=3
        )
        
        result = generate_answer(
            query=test['query'],
            chunks=chunks
        )
        
        print(f"\nAnswer: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print(f"Chunks used: {result['chunks_used']}")