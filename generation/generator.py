import os
from groq import Groq
from dotenv import load_dotenv
from typing import List,Dict
load_dotenv()

client=Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(query:str,chunks:List[Dict])->str:
    """
    Build a grounded prompt from the query and retrieved chunks.
    """
    context=""
    for i,chunk in enumerate(chunks,1):
        context += f"\n--- Chunk {i} (from {chunk['doc_id']}) ---\n"
        context += chunk['chunk_text']
        context += "\n"
    prompt = f"""You are a helpful assistant. Answer the question using ONLY the context provided below.
If the answer is not found in the context, say "I don't have enough information to answer this."
Do not make up information. Be concise and direct.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    return prompt

def generate_answer(query:str,chunks:List[Dict])->Dict:
     """
    Generate a grounded answer from retrieved chunks using Groq LLM.
    
    Args:
        query: the user's original question
        chunks: list of retrieved chunks from retriever
    
    Returns:
        dict with answer and sources
    """
     if not chunks:
         return {
             "answer":"I do not have enough information to answer this",
             "sources":[],
             "query":query
         }
     prompt=build_prompt(query,chunks)
     response=client.chat.completions.create(
         model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=512
     )
     answer=response.choices[0].message.content.strip()
     sources=list(set([chunk['doc_id']for chunk in chunks]))
     return {
         "query":query,
         "answer":answer,
         "sources":sources,
         "chunks_used":len(chunks)
     }

         
    
    

    