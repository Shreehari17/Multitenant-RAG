import sys
import os
import time
import requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.ingestor import ingest_document

# Direct Wikipedia page titles — exact matches, no search needed
ORG_A_TOPICS = [
    ("A* search algorithm", "A*_search_algorithm"),
    ("Machine learning", "Machine_learning"),
    ("Artificial intelligence", "Artificial_intelligence"),
    ("PostgreSQL", "PostgreSQL"),
    ("Artificial neural network", "Artificial_neural_network")
]

ORG_B_TOPICS = [
    ("Human resource management", "Human_resource_management"),
    ("Employment contract", "Employment_contract"),
    ("Nonprofit organization", "Nonprofit_organization"),
    ("Volunteering", "Volunteering"),
    ("Corporate governance", "Corporate_governance")
]

def fetch_wikipedia_text(title: str, page_slug: str) -> str:
    """
    Fetch Wikipedia article text using REST API directly.
    More reliable than the wikipedia Python library.
    """
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,
        "exsectionformat": "plain"
    }
    headers = {
        "User-Agent": "MultitentantRAG/1.0 (educational project)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id == "-1":
                print(f"  Page not found: {title}")
                return None
            text = page.get("extract", "")
            if len(text) > 500:
                print(f"  Fetched: {page.get('title')} ({len(text)} chars)")
                return text
            else:
                print(f"  Too short: {title}")
                return None

    except Exception as e:
        print(f"  Request failed for {title}: {e}")
        return None


def seed_tenant(tenant_id: str, topics: list):
    print(f"\n{'='*50}")
    print(f"Seeding tenant: {tenant_id}")
    print(f"{'='*50}")

    total_chunks = 0

    for title, slug in topics:
        print(f"\nFetching: {title}...")

        text = fetch_wikipedia_text(title, slug)

        if not text:
            print(f"  FAILED — skipping {title}")
            time.sleep(2)
            continue

        doc_id = f"{slug}.wiki"

        count = ingest_document(
            tenant_id=tenant_id,
            doc_id=doc_id,
            raw_text=text
        )

        total_chunks += count
        print(f"  Stored {count} chunks")
        time.sleep(1)

    print(f"\nTotal chunks for {tenant_id}: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    print("Starting Wikipedia seeding...")

    a_chunks = seed_tenant("org_a", ORG_A_TOPICS)

    print("\nWaiting 3 seconds before seeding org_b...")
    time.sleep(3)

    b_chunks = seed_tenant("org_b", ORG_B_TOPICS)

    print(f"\n{'='*50}")
    print(f"SEEDING COMPLETE")
    print(f"org_a total chunks: {a_chunks}")
    print(f"org_b total chunks: {b_chunks}")
    print(f"{'='*50}")