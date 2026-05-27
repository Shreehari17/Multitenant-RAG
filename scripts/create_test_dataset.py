"""
RAGAS Test Dataset
Write questions based on actual documents in your database.
ground_truth = what the correct answer should be (your judgment)
"""

test_dataset = [
    {
        "question": "What is the A star search algorithm?",
        "ground_truth": "A* search is a pathfinding algorithm that finds the shortest path between two nodes in a weighted graph using a priority queue and a heuristic function to guide the search."
    },
    {
        "question": "What data structure does A star use to store nodes?",
        "ground_truth": "A* uses a priority queue implemented with Python's heapq module to store nodes ordered by their f-cost (actual cost plus heuristic estimate)."
    },
    {
        "question": "What is the heuristic function in A star?",
        "ground_truth": "The heuristic function estimates the cost from the current node to the goal node. It guides the search towards the goal efficiently without exploring all possible paths."
    },
    {
        "question": "What does the minimax algorithm do?",
        "ground_truth": "Minimax is a decision-making algorithm used in game trees. It maximizes the score for the current player while minimizing the opponent's score by recursively evaluating all possible moves."
    },
    {
        "question": "What is the liability cap mentioned in the contract?",
        "ground_truth": "The liability clause states that damages are capped at $10,000."
    },
    {
        "question": "What is Youth for Seva?",
        "ground_truth": "Youth for Seva is a non-profit organization focused on volunteering and social service initiatives that engages youth in community activities."
    },
    {
        "question": "What activities were done at the walkathon?",
        "ground_truth": "At the walkathon, volunteers engaged with the flow of the crowd, reported medical or logistical issues, and helped with distribution of food, water, and materials."
    },
    {
        "question": "How does the priority queue work in A star search?",
        "ground_truth": "The priority queue stores tuples of f-cost, total cost, current node, and path. heapq.heappop removes the node with lowest f-cost and heapq.heappush adds new nodes."
    },
    {
        "question": "What visited set is used for in A star?",
        "ground_truth": "The visited set tracks already explored nodes to prevent revisiting them and avoid infinite loops during the search."
    },
    {
        "question": "What skills were developed through Youth for Seva activities?",
        "ground_truth": "Management and organizational skills were developed through coordinating volunteers and activities in Youth for Seva events."
    }
]

if __name__ == "__main__":
    print(f"Test dataset created with {len(test_dataset)} questions")
    for i, item in enumerate(test_dataset, 1):
        print(f"\n{i}. Q: {item['question']}")
        print(f"   A: {item['ground_truth'][:80]}...")