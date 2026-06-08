import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.ingestor import ingest_document

with open("scripts/sample_contract.txt", "r") as f:
    text = f.read()

count = ingest_document(
    tenant_id="org_a",
    doc_id="contract.pdf",
    raw_text=text
)

print(f"Ingested {count} chunks from contract")