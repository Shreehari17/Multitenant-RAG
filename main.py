import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ingestion.pdf_extractor import extract_text_from_pdf
from ingestion.ingestor import ingest_document
from retrieval.retriever import retrieve_chunks
from generation.generator import generate_answer

app = FastAPI(
    title="Multitenant RAG API",
    description="Upload PDFs and query them with AI",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    tenant_id: str
    query: str
    top_k: int = 5

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG API is running"}

@app.post("/ingest")
async def ingest_pdf(
    tenant_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        text = extract_text_from_pdf(tmp_path)
        os.unlink(tmp_path)
        
        if not text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from PDF"
            )
        
        count = ingest_document(
            tenant_id=tenant_id,
            doc_id=file.filename,
            raw_text=text
        )
        
        return JSONResponse(content={
            "message": "PDF ingested successfully",
            "tenant_id": tenant_id,
            "doc_id": file.filename,
            "chunks_stored": count
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query(request: QueryRequest):
    try:
        chunks = retrieve_chunks(
            tenant_id=request.tenant_id,
            query=request.query,
            top_k=request.top_k
        )
        
        result = generate_answer(
            query=request.query,
            chunks=chunks
        )
        
        return JSONResponse(content={
            "query": result["query"],
            "answer": result["answer"],
            "sources": result["sources"],
            "chunks_used": result["chunks_used"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))