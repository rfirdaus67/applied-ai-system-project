import csv
from os import read
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    # Columns that must be numeric for scoring later.
    float_fields = ("energy", "valence", "danceability", "acousticness")
    int_fields = ("tempo_bpm",)
    with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for field in float_fields:
                if row.get(field) not in (None, ""):
                    row[field] = float(row[field])
            for field in int_fields:
                if row.get(field) not in (None, ""):
                    row[field] = int(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's prefs, returning (score, reasons)."""
    # Weights from the Algorithm Recipe: mood matters most, then energy, then genre.
    MOOD_WEIGHT = 2.5
    ENERGY_WEIGHT = 2.0
    GENRE_WEIGHT = 1.0

    score = 0.0
    reasons: List[str] = []

    # Mood: string, so only an exact match earns points.
    if user_prefs["mood"] == song["mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood matches ({song['mood']})")

    # Energy: numeric, so score by how close it is. 1 - |diff| is 1 when
    # identical and drops toward 0 as the energies get further apart.
    energy_closeness = 1 - abs(song["energy"] - user_prefs["energy"])
    energy_points = ENERGY_WEIGHT * energy_closeness
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs preferred {user_prefs['energy']:.2f} "
        f"(+{energy_points:.2f})"
    )

    # Genre: string, so only an exact match earns points.
    if user_prefs["genre"] == song["genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre matches ({song['genre']})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top k (song, score, explanation) tuples, highest score first."""
    # Score every song, then return the top k sorted highest-to-lowest.
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
