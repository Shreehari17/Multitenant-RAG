# Multitenant RAG System

A production-grade Retrieval-Augmented Generation (RAG) system built from scratch — no LangChain, no LlamaIndex — with multi-tenant data isolation, hybrid search, cross-encoder reranking, and semantic caching.

## What This Does

Multiple organisations upload PDFs. Each organisation's data is completely isolated. When they ask questions, the system retrieves relevant chunks from only their documents and generates grounded answers using an LLM.

Most RAG tutorials stop at "embed → retrieve → answer." This system goes further: it measures retrieval and generation quality with a custom RAGAS-style evaluator, combines semantic and keyword search, reranks for precision, and caches semantically similar queries for near-instant responses.

## Results

Measured on a 10-question evaluation set using a custom LLM-as-judge evaluator, tracked across each engineering improvement:

| Metric | Baseline | +Hybrid Search | +Reranker | Final |
|---|---|---|---|---|
| Faithfulness | 0.59 | 0.75 | 0.70 | **0.80** |
| Answer Relevancy | 0.77 | 0.75 | 0.81 | **0.88** |
| Context Precision | 0.73 | 0.83 | 0.80 | **0.70** |
| Context Recall | 0.56 | 0.73 | 0.67 | **0.77** |

Context Recall improved 38% and Answer Relevancy improved 14% from baseline to final, driven by hybrid retrieval and better-grounded prompting.

## Architecture

```
INGESTION PHASE (one time)

  [PDF] → [PyMuPDF Extractor] → [LangChain Chunker] → [all-mpnet Embedder] → [PostgreSQL + pgvector]
           text extraction       500 chars, 50 overlap   768 dimensions        IVFFlat index


QUERY PHASE (cached or fresh)

  [Question] → [Embed Query] → ┌─[Semantic Search (pgvector <=>)]─┐
                                │                                   ├→ [RRF Fusion] → [Reranker] → [Groq LLM] → [Answer]
                                └─[BM25 Keyword Search]────────────┘
                                              ↑
                                       [Redis Cache]
                                  similarity > 0.95 → ~10ms


TENANT ISOLATION

  WHERE tenant_id = %s enforced at every layer:
  vector search · keyword search · retrieval · generation
```

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| PDF extraction | PyMuPDF | Preserves reading order in multi-column layouts |
| Chunking | LangChain `RecursiveCharacterTextSplitter` | Splits at paragraph → sentence → word boundaries |
| Embeddings | `sentence-transformers/all-mpnet-base-v2` | 768-dim vectors, trained on billions of sentence pairs |
| Vector store | PostgreSQL + pgvector | One system for SQL, vectors, and tenant filtering |
| Vector index | IVFFlat (`lists = 100`) | Approximate nearest-neighbour search, faster than full scan at scale |
| Keyword search | `rank-bm25` | Catches exact terms that embeddings can miss |
| Fusion | Reciprocal Rank Fusion | Merges semantic + keyword rankings, `1/(rank + 60)` |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Scores query + chunk together for precise relevance |
| Caching | Redis | Semantic cache — embed query, compare, return in ~10ms on a hit |
| LLM | Groq `llama-3.1-8b-instant` | Fast, free tier, `temperature=0.1` for grounded output |
| API | FastAPI + Pydantic | Typed request validation, clean error handling |
| Deployment | Docker Compose | Postgres + Redis + API, reproducible on any machine |

## Project Structure

```
multitenant-rag/
├── core/
│   ├── db.py                    # Postgres connection pool
│   └── cache.py                 # Redis semantic caching layer
├── generation/
│   └── generator.py             # Groq LLM + grounded prompt
├── ingestion/
│   ├── pdf_extractor.py         # PyMuPDF text extraction
│   ├── chunker.py               # LangChain text splitting
│   ├── embedder.py              # sentence-transformers embedding
│   └── ingestor.py              # orchestrates the ingestion pipeline
├── retrieval/
│   ├── retriever.py             # pgvector semantic search
│   ├── bm25_retriever.py        # BM25 keyword search
│   ├── hybrid_retriever.py      # RRF fusion + reranker
│   └── reranker.py              # cross-encoder reranking
├── scripts/
│   ├── setup_db.py              # creates chunks table + IVFFlat index
│   ├── init_db.sql              # raw SQL schema (used by setup_db.py)
│   ├── seed_data.py             # loads sample Wikipedia data
│   ├── ingest_contract.py       # ingests the sample contract into org_b
│   ├── sample_contract.txt      # sample document used for evaluation
│   ├── create_test_dataset.py   # 10 Q&A pairs for evaluation
│   ├── run_ragas.py             # custom LLM-as-judge evaluator
│   ├── test_chunker.py
│   ├── test_db.py
│   ├── test_embedder.py
│   ├── test_generator.py
│   ├── test_hybrid.py
│   ├── test_ingestor.py
│   ├── test_pdf.py
│   ├── test_reranker.py
│   └── test_retriever.py
├── main.py                      # FastAPI server
├── Dockerfile
├── docker-compose.yml           # Postgres + Redis + API
├── railway.toml                 # Railway deployment config
├── ragas_baseline_scores.txt    # recorded evaluation runs
├── requirements.txt
└── README.md
```

Component-level unit tests live in `scripts/` alongside the pipeline scripts (`test_chunker.py`, `test_embedder.py`, `test_retriever.py`, `test_reranker.py`, `test_hybrid.py`, `test_generator.py`, `test_db.py`, `test_pdf.py`, `test_ingestor.py`), each exercising one module in isolation before it's wired into the full pipeline.

## Running Locally

### Prerequisites
- Docker Desktop
- Python 3.9+
- A free [Groq API key](https://console.groq.com)

### Setup

```bash
git clone https://github.com/Shreehari17/Multitenant-RAG.git
cd Multitenant-RAG

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ragdb
POSTGRES_USER=raguser
POSTGRES_PASSWORD=ragpass
REDIS_HOST=localhost
REDIS_PORT=6379
GROQ_API_KEY=your_groq_key_here
```

Start the services:

```bash
docker compose up -d
docker ps        # should show rag_postgres and rag_redis
```

Initialise the database and (optionally) load sample data:

```bash
python scripts/setup_db.py
python scripts/seed_data.py
```

Start the API:

```bash
python -m uvicorn main:app --reload
```

The API is now running at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## API Usage

**Health check**
```bash
curl http://localhost:8000/health
```

**Ingest a document**
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@sample.pdf" \
  -F "tenant_id=org_a"
```

**Query**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "org_a", "query": "What is the A* search algorithm?", "top_k": 3}'
```

Example response:
```json
{
  "query": "What is the A* search algorithm?",
  "answer": "A* is a graph traversal and pathfinding algorithm that finds the shortest path between nodes using a heuristic function...",
  "sources": ["A*_search_algorithm.wiki"],
  "chunks_used": 3,
  "cache_hit": false
}
```

Asking the same question again (or a semantically similar one) returns `"cache_hit": true` in roughly 10ms, with no retrieval or LLM call.

## How It Works

**Embedding** — Text is converted into a 768-number vector by a model trained on billions of sentence pairs. Similar meanings produce vectors that point in similar directions, which is what makes semantic search possible.

**Hybrid search** — Semantic search understands meaning but can miss exact keywords; BM25 catches exact keywords but misses synonyms. Running both and merging the results with Reciprocal Rank Fusion covers each one's blind spots.

**Reranking** — Semantic search embeds the query and each chunk separately, which is fast but imprecise. A cross-encoder reads the query and a candidate chunk together and produces a much more accurate relevance score, at the cost of extra latency — so it's only applied to the top candidates after fusion.

**Semantic caching** — If a new query's embedding is more than 95% similar to a previously cached query, the stored answer is returned directly. Same meaning, different wording, no repeated LLM call.

**Tenant isolation** — Every retrieval query, at every stage (semantic search, keyword search, final results), is filtered with `WHERE tenant_id = %s`. There is no cross-tenant fallback: a query from one tenant simply cannot see another tenant's chunks.

## Evaluation Methodology

A custom LLM-as-judge evaluator (built instead of using the `ragas` library, due to a Python 3.9 dependency conflict) scores four metrics using Groq:

1. **Faithfulness** — is the answer grounded in the retrieved context? (binary YES/NO)
2. **Answer Relevancy** — does the answer actually address the question? (LLM score 0–10, normalized)
3. **Context Precision** — what fraction of retrieved chunks are relevant?
4. **Context Recall** — does the retrieved context contain what's needed to answer correctly? (LLM score 0–10, normalized)

The evaluation set is 10 hand-written Q&A pairs spanning the A* search algorithm, a sample contract, and a nonprofit-organisation document.

Run it yourself:
```bash
python scripts/run_ragas.py
```

## Known Limitations

- Scanned (image-only) PDFs aren't supported — OCR isn't implemented.
- The evaluator is custom-built and simpler than the full RAGAS library (e.g. faithfulness is binary rather than statement-level).
- No authentication on the API — in production this would need JWT auth and rate limiting.
- IVFFlat is an approximate index, so it can occasionally miss a relevant chunk; the reranker helps offset this.
- The knowledge base (~2,000 chunks) is small compared to production-scale deployments.

## Author

Built as a portfolio project by [Shreehari17](https://github.com/Shreehari17).
