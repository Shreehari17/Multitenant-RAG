import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from ingestion.pdf_extractor import extract_text_from_pdf
from ingestion.ingestor import ingest_document
from retrieval.hybrid_retriever import hybrid_retrieve
from generation.generator import generate_answer
from core.cache import get_cached_answer, store_cached_answer

app = FastAPI(
    title="Multitenant RAG API",
    description="Upload PDFs and query them with AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    tenant_id: str
    query: str
    top_k: int = 5

    @field_validator('tenant_id')
    @classmethod
    def tenant_id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('tenant_id cannot be empty')
        return v.strip()

    @field_validator('query')
    @classmethod
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('query cannot be empty')
        if len(v.strip()) < 3:
            raise ValueError('query must be at least 3 characters')
        return v.strip()

    @field_validator('top_k')
    @classmethod
    def top_k_must_be_valid(cls, v):
        if v < 1 or v > 20:
            raise ValueError('top_k must be between 1 and 20')
        return v


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG API is running"}


@app.post("/ingest")
async def ingest_pdf(
    tenant_id: str = Form(...),
    file: UploadFile = File(...)
):
    # Validate tenant_id
    if not tenant_id or not tenant_id.strip():
        raise HTTPException(
            status_code=400,
            detail="tenant_id cannot be empty"
        )

    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files supported. Got: {file.filename}"
        )

    # Validate file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB"
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    try:
        # Write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # Extract text
        text = extract_text_from_pdf(tmp_path)
        os.unlink(tmp_path)

        if not text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from PDF. File may be scanned or image-only."
            )

        if len(text.strip()) < 50:
            raise HTTPException(
                status_code=422,
                detail="PDF contains too little text to be useful"
            )

        # Ingest
        count = ingest_document(
            tenant_id=tenant_id.strip(),
            doc_id=file.filename,
            raw_text=text
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "PDF ingested successfully",
                "tenant_id": tenant_id.strip(),
                "doc_id": file.filename,
                "chunks_stored": count
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


@app.post("/query")
def query(request: QueryRequest):
    try:
        # Check semantic cache first
        cached = get_cached_answer(request.query)
        if cached:
            return JSONResponse(status_code=200, content=cached)

        # Cache miss — run full pipeline
        chunks = hybrid_retrieve(
            tenant_id=request.tenant_id,
            query=request.query,
            top_k=request.top_k
        )

        result = generate_answer(
            query=request.query,
            chunks=chunks
        )

        response = {
            "query": result["query"],
            "answer": result["answer"],
            "sources": result["sources"],
            "chunks_used": result["chunks_used"],
            "cache_hit": False
        }

        # Store in cache for future similar queries
        store_cached_answer(request.query, result)

        return JSONResponse(status_code=200, content=response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")