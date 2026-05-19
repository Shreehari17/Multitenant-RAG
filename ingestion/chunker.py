from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks using LangChain's
    RecursiveCharacterTextSplitter.
    
    Args:
        text: raw text to split
        chunk_size: target size of each chunk in characters
        overlap: number of characters to overlap between chunks
    
    Returns:
        list of text chunks
    """
    if not text or not text.strip():
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_text(text)
    
    print(f"[chunker] Created {len(chunks)} chunks from {len(text)} characters")
    return chunks