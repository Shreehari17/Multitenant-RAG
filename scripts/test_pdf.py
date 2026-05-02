from ingestion.pdf_extractor import extract_text_from_pdf
from ingestion.ingestor import ingest_document

PDF_PATH = "scripts/sample.pdf"  
TENANT_ID = "org_a"
DOC_ID = "sample.pdf"

if __name__ == "__main__":
    print("Step 1: Extracting text from PDF...")
    text = extract_text_from_pdf(PDF_PATH)
    
    if not text:
        print("Failed to extract text. Check the PDF path.")
        exit(1)
    
    print(f"\nFirst 300 characters of extracted text:")
    print(text[:300])
    
    print(f"\nStep 2: Ingesting into database...")
    count = ingest_document(
        tenant_id=TENANT_ID,
        doc_id=DOC_ID,
        raw_text=text
    )
    
    print(f"\nDone. {count} chunks stored from real PDF.")