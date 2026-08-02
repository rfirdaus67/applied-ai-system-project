"""Demo for the AI Music DJ.

Runs a few example user profiles and their preferences through the Gemini API
agent and prints the results to the terminal

"""
from gemini import generate
from ranking import build_rag_payload

# Each example mirrors what app.py collects: a genre, a mood, a target energy,
# and a priority ranking (the order the user clicked the features in, where the
# first item is the #1 priority and gets the most weight).
EXAMPLES = [
    {
        "label": "Example 1 — Energy-first workout playlist",
        "genre": "pop",
        "mood": "Energetic",
        "energy": 0.95,
        # Energy matters most, then genre, then mood.
        "rank_order": ["Energy", "Genre", "Mood"],
    },
    {
        "label": "Example 2 — Mood-first mellow evening",
        "genre": "acoustic",
        "mood": "Chill",
        "energy": 0.3,
        # Mood matters most, then energy, then genre.
        "rank_order": ["Mood", "Energy", "Genre"],
    },
]


def run_example(example):
    payload = build_rag_payload(
        example["genre"], example["mood"], example["energy"], example["rank_order"]
    )

    print("=" * 78)
    print(example["label"])
    print("-" * 78)
    print(f"  Genre:      {example['genre']}")
    print(f"  Mood:       {example['mood']}")
    print(f"  Energy:     {example['energy']}")
    print(f"  Priority:   {' > '.join(example['rank_order'])}  (1st = most weight)")
    print(f"  Weights:    {payload['dynamic_weights']}")
    print("-" * 78)
    print("AI recommendations:\n")
    print(generate(payload))
    print()


def main():
    for example in EXAMPLES:
        run_example(example)


if __name__ == "__main__":
    main()
