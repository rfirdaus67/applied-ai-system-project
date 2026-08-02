"""Pure, testable helpers for the priority-ranking -> weight logic.

Kept free of Streamlit and the Gemini client so it can be tested separately.
"""
from typing import Dict, List

FEATURES = ["Genre", "Mood", "Energy"]

# Weight applied to the 1st / 2nd / 3rd ranked feature.
# The top weight (6) exceeds #2 + #3 combined (3 + 1 = 4), so the user's #1
# priority always dominates the score while the others still break near-ties.
RANK_WEIGHTS = [6.0, 3.0, 1.0]

# Used until the user has ranked all three features.
DEFAULT_WEIGHTS = {"genre": 0.33, "mood": 0.33, "energy": 0.34}


def compute_weights(rank_order: List[str]) -> Dict[str, float]:
    """Map a click-ordered list of features to per-feature weights.

    ``rank_order[0]`` is the top priority and receives the largest weight.
    Until all three features are ranked, the neutral default weights are
    returned so no single feature is favored.
    """
    if len(rank_order) != len(FEATURES):
        return dict(DEFAULT_WEIGHTS)
    return {
        feat.lower(): RANK_WEIGHTS[rank_order.index(feat)]
        for feat in FEATURES
    }


def build_rag_payload(genre: str, mood: str, energy: float,
                      rank_order: List[str]) -> Dict:
    """Bundle user preferences + computed weights into the RAG payload."""
    return {
        "user_preferences": {"genre": genre, "mood": mood, "energy": energy},
        "dynamic_weights": compute_weights(rank_order),
    }


def build_prompt(rag_payload: Dict) -> str:
    """Build the Gemini prompt text from a RAG payload.

    The weights are surfaced in the prompt so the model prioritizes the
    highest-weighted feature first.
    """
    prefs = rag_payload["user_preferences"]
    weights = rag_payload["dynamic_weights"]
    # The feature with the largest weight is the user's top priority.
    top_feature = max(weights, key=weights.get)
    return (
        "You are an AI music DJ. Using the user's preferences, find the top 5 songs "
        "from the attached CSV dataset that best match their interests. "
        f"The user's preferences are: genre={prefs['genre']}, "
        f"mood={prefs['mood']}, energy={prefs['energy']}. "
        "The user ranked how much each feature matters, expressed as these weights "
        "where a HIGHER weight means MORE important: "
        f"genre={weights['genre']}, mood={weights['mood']}, energy={weights['energy']}. "
        f"The single most important feature is {top_feature} (highest weight), so it must "
        "dominate the ranking. "
        "Score each song and recommend the 5 highest, ordered best match first. "
        "Do not include the song ID or the raw calculation. "
        "Scoring: "
        f"if the song's genre matches or is similar, score += {weights['genre']}; "
        f"if the song's mood matches or is similar, score += {weights['mood']}; "
        "for energy, energy_closeness = 1 - abs(song_energy - "
        f"{prefs['energy']}), then score += {weights['energy']} * energy_closeness. "
        "For each recommended song shown in the [artist(s)] - [song name] format\n, include the final score\n, a brief explanation of why "
        "it received that score (e.g. same/similar genre)\n, and show the song's energy "
        "vs the user's preferred energy."
    )