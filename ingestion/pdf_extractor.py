import pypdf
from typing import Optional

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract raw text from a PDF file.
    
    Args:
        pdf_path: path to the PDF file
    
    Returns:
        extracted text as string, or None if extraction fails
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        
        if len(reader.pages) == 0:
            print(f"[pdf_extractor] PDF has no pages: {pdf_path}")
            return None
        
        full_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
            print(f"[pdf_extractor] Extracted page {i+1}/{len(reader.pages)}")
        
        if not full_text.strip():
            print(f"[pdf_extractor] No text extracted from: {pdf_path}")
            return None
            
        print(f"[pdf_extractor] Total characters extracted: {len(full_text)}")
        return full_text
        
    except Exception as e:
        print(f"[pdf_extractor] Error reading PDF: {e}")
        return None