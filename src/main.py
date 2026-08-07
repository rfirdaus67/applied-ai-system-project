"""Demo for the AI Music DJ.

Runs a few example user profiles & prints the results to the terminal.
"""
from gemini import generate
from ranking import build_prefs, build_weights

# Each example mirrors what app.py collects: a genre, a mood, a target energy,
# and the ranking order

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
    prefs_payload = build_prefs(
        example["genre"], example["mood"], example["energy"]
    )
    weights_payload = build_weights(example["rank_order"])

    print("=" * 78)
    print(example["label"])
    print("-" * 78)
    print(f"  Genre:      {example['genre']}")
    print(f"  Mood:       {example['mood']}")
    print(f"  Energy:     {example['energy']}")
    print(f"  Priority:   {' > '.join(example['rank_order'])}  (1st = most weight)")
    print(f"  Weights:    {weights_payload['weights']}")
    print("-" * 78)

    explanation, recommended, token_count = generate(prefs_payload, weights_payload)

    print("Cosine similarity ranking:\n")
    print(
        recommended[[
            "artists", "track_name", "track_genre", "mood", "energy", "final_score"
        ]].to_string(index=False)
    )
    print(f"\nAI explanations ({token_count} prompt tokens):\n")
    print(explanation)
    print()


def main():
    for example in EXAMPLES:
        run_example(example)


if __name__ == "__main__":
    main()
