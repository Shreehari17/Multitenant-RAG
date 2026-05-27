import os
import sys
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.retriever import retrieve_chunks
from generation.generator import generate_answer
from scripts.create_test_dataset import test_dataset

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_llm(prompt: str) -> str:
    """Call Groq LLM and return response text."""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"    LLM call failed: {e}")
        return ""

def score_faithfulness(answer: str, contexts: list) -> float:
    """
    Faithfulness: does the answer stick to what the context says?
    We break the answer into statements and check each one against context.
    Score = faithful statements / total statements
    """
    context_text = "\n".join(contexts)
    prompt = f"""Given the following context and answer, list each factual statement 
in the answer and label it FAITHFUL or UNFAITHFUL based on whether it can be 
supported by the context.

Context:
{context_text}

Answer:
{answer}

Respond in JSON format like this:
{{"statements": [{{"statement": "...", "label": "FAITHFUL"}}]}}

Only respond with JSON, nothing else."""

    result = ask_llm(prompt)
    try:
        data = json.loads(result)
        statements = data.get("statements", [])
        if not statements:
            return 0.0
        faithful = sum(1 for s in statements if s.get("label") == "FAITHFUL")
        return round(faithful / len(statements), 4)
    except:
        return 0.5

def score_answer_relevancy(question: str, answer: str) -> float:
    """
    Answer Relevancy: does the answer address the question?
    Score 0-10 from LLM, normalized to 0-1.
    """
    prompt = f"""Rate how well this answer addresses the question on a scale of 0-10.
0 = completely irrelevant or refuses to answer
10 = directly and completely answers the question

Question: {question}
Answer: {answer}

Respond with only a number between 0 and 10."""

    result = ask_llm(prompt)
    try:
        score = float(result.strip().split()[0])
        return round(min(max(score, 0), 10) / 10, 4)
    except:
        return 0.5

def score_context_precision(question: str, contexts: list) -> float:
    """
    Context Precision: are the retrieved chunks actually relevant?
    Score = relevant chunks / total chunks retrieved
    """
    if not contexts:
        return 0.0

    relevant = 0
    for ctx in contexts:
        prompt = f"""Is this context chunk relevant and useful for answering the question?
Answer only YES or NO.

Question: {question}
Context chunk: {ctx[:300]}"""

        result = ask_llm(prompt)
        if "YES" in result.upper():
            relevant += 1
        time.sleep(0.3)

    return round(relevant / len(contexts), 4)

def score_context_recall(ground_truth: str, contexts: list) -> float:
    """
    Context Recall: does the retrieved context contain the information
    needed to produce the ground truth answer?
    Score 0-10 from LLM, normalized to 0-1.
    """
    context_text = "\n".join(contexts)
    prompt = f"""Rate how much of the information needed to produce the ground truth 
answer is present in the retrieved context. Scale 0-10.
0 = none of the needed information is in context
10 = all information needed is in context

Ground truth answer: {ground_truth}
Retrieved context: {context_text[:600]}

Respond with only a number between 0 and 10."""

    result = ask_llm(prompt)
    try:
        score = float(result.strip().split()[0])
        return round(min(max(score, 0), 10) / 10, 4)
    except:
        return 0.5

def get_tenant(question: str) -> str:
    org_b_keywords = ["youth for seva", "walkathon", "volunteering",
                      "ngo", "activities", "skills were developed"]
    for keyword in org_b_keywords:
        if keyword in question.lower():
            return "org_b"
    return "org_a"

def run_evaluation():
    print("="*55)
    print("CUSTOM RAG EVALUATION")
    print("="*55)

    all_scores = {
        "faithfulness": [],
        "answer_relevancy": [],
        "context_precision": [],
        "context_recall": []
    }

    for i, item in enumerate(test_dataset, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]
        tenant = get_tenant(question)

        print(f"\n[{i}/{len(test_dataset)}] {question[:55]}...")

        # Get RAG pipeline output
        chunks = retrieve_chunks(tenant_id=tenant, query=question, top_k=3)
        result = generate_answer(query=question, chunks=chunks)
        answer = result["answer"]
        contexts = [c["chunk_text"] for c in chunks]

        print(f"  Answer: {answer[:70]}...")

        # Score each metric
        f_score = score_faithfulness(answer, contexts)
        time.sleep(0.5)

        ar_score = score_answer_relevancy(question, answer)
        time.sleep(0.5)

        cp_score = score_context_precision(question, contexts)
        time.sleep(0.5)

        cr_score = score_context_recall(ground_truth, contexts)
        time.sleep(0.5)

        all_scores["faithfulness"].append(f_score)
        all_scores["answer_relevancy"].append(ar_score)
        all_scores["context_precision"].append(cp_score)
        all_scores["context_recall"].append(cr_score)

        print(f"  Faithfulness:     {f_score}")
        print(f"  Answer Relevancy: {ar_score}")
        print(f"  Context Precision:{cp_score}")
        print(f"  Context Recall:   {cr_score}")

    # Average scores
    avg = {k: round(sum(v)/len(v), 4) for k, v in all_scores.items()}

    print("\n" + "="*55)
    print("BASELINE SCORES")
    print("="*55)
    print(f"Faithfulness:      {avg['faithfulness']}")
    print(f"Answer Relevancy:  {avg['answer_relevancy']}")
    print(f"Context Precision: {avg['context_precision']}")
    print(f"Context Recall:    {avg['context_recall']}")
    print("="*55)

    # Save results
    with open("ragas_baseline_scores.txt", "w") as f:
        f.write("RAG EVALUATION BASELINE SCORES\n")
        f.write("="*55 + "\n")
        f.write(f"Faithfulness:      {avg['faithfulness']}\n")
        f.write(f"Answer Relevancy:  {avg['answer_relevancy']}\n")
        f.write(f"Context Precision: {avg['context_precision']}\n")
        f.write(f"Context Recall:    {avg['context_recall']}\n")
        f.write("="*55 + "\n")
        f.write(f"Model: llama-3.1-8b-instant\n")
        f.write(f"Embedding: all-mpnet-base-v2\n")
        f.write(f"Chunker: RecursiveCharacterTextSplitter 500/50\n")
        f.write(f"Questions evaluated: {len(test_dataset)}\n")
        f.write("Evaluator: custom LLM-as-judge using Groq\n")

    print("\nSaved to ragas_baseline_scores.txt")
    return avg

if __name__ == "__main__":
    run_evaluation()