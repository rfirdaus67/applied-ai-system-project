"""The recommender's algorithm: ranking -> weights -> cosine similarity scores.

Whatever user ranks #1 gets 6.0, #2 gets 3.0, #3 gets 1.0.

Kept free of Streamlit and the Gemini client so it can be tested separately.
"""
import os
from typing import Dict, List

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# features user can rank, applied to each song
FEATURES = ["Genre", "Mood", "Energy"]

# weight applied to the ranked features, in order of ranking
RANK_WEIGHTS = [6.0, 3.0, 1.0]

# if the user doesn't rank all three features
DEFAULT_WEIGHTS = {"genre": 0.33, "mood": 0.33, "energy": 0.34}

# relative to this file, so the app works no matter where it is launched from.
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "spotify_songs.csv")

# vectorizers are built once the dataset is loaded
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=["track_genre", "mood", "energy"]).reset_index(drop=True)

# Fit each vectorizer on the dataset to learn its vocabulary. CountVectorizer
# splits on words, so "alt-rock" becomes {alt, rock} and shares the
# word "rock" with plain "rock" and words can earn partial credit instead of perfect matches

mood_vectorizer = CountVectorizer()
mood_matrix = mood_vectorizer.fit_transform(df["mood"])

genre_vectorizer = CountVectorizer()
genre_matrix = genre_vectorizer.fit_transform(df["track_genre"])


def compute_weights(rank_order: List[str]) -> Dict[str, float]:
    """Map a click based list of attributes to their according weights."""
    if len(rank_order) != len(FEATURES):
        return dict(DEFAULT_WEIGHTS)
    return {
        feature.lower(): RANK_WEIGHTS[position]
        for position, feature in enumerate(rank_order)
    }


def build_prefs(genre: str, mood: str, energy: float) -> Dict:
    """Build user preferences into the RAG payload."""
    return {
        "user_preferences": {"genre": genre, "mood": mood, "energy": energy},
    }


def build_weights(rank_order: List[str]) -> Dict:
    """Build user weights into the RAG payload based on rank order."""
    return {
        "weights": compute_weights(rank_order)
    }


def score_songs(genre: str, mood: str, energy: float,
                weights: Dict[str, float]) -> pd.DataFrame:
    """Score every song against the user's preferences.

    Takes the preferences and weights as arguments"""
    scored = df.copy()

    # --- ATTRIBUTE 1: MOOD SIMILARITY ---
    # transform() takes a list of documents; a bare string would be read one
    # character at a time.
    user_mood_vector = mood_vectorizer.transform([str(mood)])
    # Compute similarity between the user vector and all songs
    scored["mood_score"] = cosine_similarity(user_mood_vector, mood_matrix).flatten()

    # --- ATTRIBUTE 2: GENRE SIMILARITY ---
    user_genre_vector = genre_vectorizer.transform([str(genre)])
    scored["genre_score"] = cosine_similarity(user_genre_vector, genre_matrix).flatten()

    # --- ATTRIBUTE 3: ENERGY CLOSENESS ---
    # Using absolute distance formula: 1 means perfect match, 0 means total opposite
    scored["energy_score"] = 1 - np.abs(scored["energy"] - float(energy))

    # Dividing by the total weight puts the score on a 0.00-1.00 scale. It has to
    # be the actual sum, not a hardcoded 10: ranked weights add up to 6+3+1=10,
    # but DEFAULT_WEIGHTS only adds up to 1.0.
    total_weight = sum(weights.values())
    scored["final_score"] = (
        (scored["mood_score"] * weights["mood"])
        + (scored["genre_score"] * weights["genre"])
        + (scored["energy_score"] * weights["energy"])
    ) / total_weight

    return scored


def top_songs(scored: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    """The 5 highest scoring songs, highest score is to be recommended first
    
    songs with equal scores keep their order and
    the same preferences always produce the same list."""

    ranked = scored.sort_values(by="final_score", ascending=False, kind="mergesort")
    return ranked.head(k).reset_index(drop=True)


def build_explanation_prompt(prefs_payload: Dict, weights_payload: Dict,
                             ranked_count: int) -> str:
    """returns the Gemini prompt for explaining a song thats being recommended.

    Scoring and ordering happen by cosine similarity. The model's
    job is to return one explanation per song as JSON with the
    title / score / explanation layout assembled in Python.
    
    so the output is always formatted the same."""
    
    prefs = prefs_payload["user_preferences"]
    weights = weights_payload["weights"]
    # The feature with the largest weight is the user's top priority.
    top_feature = max(weights, key=weights.get)
    return (
        "You are an AI music DJ. The recommendations have ALREADY been chosen and "
        "ranked by a cosine-similarity scoring engine. Your only job is to explain "
        f"them to the user. You will receive {ranked_count} songs, best match first, "
        "as rows of CSV data in one or more chunks. "
        f"The user's preferences are: genre={prefs['genre']}, "
        f"mood={prefs['mood']}, energy={prefs['energy']}. "
        "The user ranked how much each feature matters, expressed as these weights "
        "where a HIGHER weight means MORE important: "
        f"genre={weights['genre']}, mood={weights['mood']}, energy={weights['energy']}. "
        f"The single most important feature is {top_feature} (highest weight), so it "
        "dominated the ranking and your explanations should reflect that. "
        "The score is already the cosine similarity to the user's weighted "
        "preferences, from 0.00 to 1.00, where 1.00 is a perfect match. "
        "Rules: do NOT reorder the songs, do NOT add or drop songs, and do NOT "
        "recompute or second-guess any score. Keep the given order and the given "
        "numbers exactly.\n\n"
        f"Return a JSON array of exactly {ranked_count} objects, in the same order "
        "as the songs you were given, each shaped like this:\n"
        '{"rank": 1, "explanation": "..."}\n\n'
        "The explanation is one or two plain sentences saying why the song earned "
        "its score: which of genre, mood, or energy it gained the most from, and "
        "how the song's energy compares to the user's preferred energy. "
        "Do not repeat the song title, the artist, or the score inside the "
        "explanation, and do not mention the song ID -- those are added around "
        "your text. No markdown, no bullet points, no line breaks."
    )
