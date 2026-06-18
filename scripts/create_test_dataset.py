"""
RAGAS Test Dataset
Write questions based on actual documents in your database.
ground_truth = what the correct answer should be (your judgment)
"""

test_dataset = [
    {
        "question": "What is the A star search algorithm?",
        "ground_truth": "A* is a graph traversal and pathfinding algorithm that finds the shortest path between nodes using a heuristic function. It is complete, optimal, and optimally efficient."
    },
    {
        "question": "What heuristic does A star use?",
        "ground_truth": "A* uses an admissible heuristic function h(n) that estimates the cost from the current node to the goal. Common heuristics include Manhattan distance and Euclidean distance."
    },
    {
        "question": "What is the difference between A star and Dijkstra?",
        "ground_truth": "A* uses a heuristic to guide search towards the goal making it faster than Dijkstra which explores all directions equally without a heuristic."
    },
    {
        "question": "What does f score mean in A star?",
        "ground_truth": "The f score in A* is f(n) = g(n) + h(n) where g(n) is the actual cost from start to current node and h(n) is the heuristic estimate to the goal."
    },
    {
        "question": "What is the liability cap in the contract?",
        "ground_truth": "The liability clause states that damages are capped at $10,000."
    },
    {
        "question": "What is the notice period for termination?",
        "ground_truth": "The notice period for termination is 30 days. Either party may terminate with written notice."
    },
    {
        "question": "What is Youth for Seva?",
        "ground_truth": "Youth for Seva is a non-profit organization focused on volunteering and social service that engages youth in community activities."
    },
    {
        "question": "What activities were done at the Walk2HEAL walkathon event?",
        "ground_truth": "At the Walk2HEAL walkathon volunteers sorted participant T-shirts, managed registration desks, facilitated onboarding and used digital payment QR codes for registrations."
    },
    {
        "question": "What is human resource management according to the Wikipedia article?",
        "ground_truth": "Human resource management is the strategic approach to managing people in an organization covering recruitment, training, performance management and employee relations."
    },
    {
        "question": "What is volunteering?",
        "ground_truth": "Volunteering is the practice of people working on behalf of others or a cause without payment, typically through a nonprofit organization or community group."
    }
]

if __name__ == "__main__":
    print(f"Test dataset created with {len(test_dataset)} questions")
    for i, item in enumerate(test_dataset, 1):
        print(f"\n{i}. Q: {item['question']}")
        print(f"   A: {item['ground_truth'][:80]}...")