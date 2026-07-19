"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs_pop = {"genre": "pop", "mood": "happy", "energy": 0.75}
    user_prefs_rock = {"genre": "rock", "mood": "intense", "energy": 0.9}
    user_prefs_lofi = {"genre": "lofi", "mood": "chill", "energy": 0.3}

    # edge-case profiles

    # lofi songs are all chill and low-energy, but this asks for intense + max
    # energy. The genre bonus fights a big energy penalty, and no lofi song is
    # "intense" so the heaviest weight (mood) never fires.
    user_prefs_edge_lofi_intense = {"genre": "lofi", "mood": "intense", "energy": 1.0}

    # ambient songs sit around 0.28 energy; asking for happy at max energy means
    # the one genre match loses heavily on energy while no ambient song is happy.
    user_prefs_edge_ambient_hype = {"genre": "ambient", "mood": "happy", "energy": 1.0}

    # rock is intense/high-energy (~0.91); asking for chill at zero energy inverts
    # it. The genuine rock song matches genre but gets crushed on energy and mood.
    user_prefs_edge_rock_mellow = {"genre": "rock", "mood": "chill", "energy": 0.0}

    # No pop song is "chill", so the mood weight (the heaviest) never fires and
    # the ranking silently collapses onto energy proximity — a hidden conflict.
    user_prefs_edge_pop_chill = {"genre": "pop", "mood": "chill", "energy": 0.85}

    # "intense" mood exists only in high-energy songs, but energy is pinned low.
    # Tests whether a mood match can outweigh a large energy penalty.
    user_prefs_edge_mood_vs_energy = {"genre": "jazz", "mood": "intense", "energy": 0.1}

    recommendations = recommend_songs(user_prefs_pop, songs, k=5)

    print()
    print("=" * 48)
    print(f"  Top {len(recommendations)} recommendations")
    print(f"  for {user_prefs_pop['mood']} / {user_prefs_pop['genre']} "
          f"@ energy {user_prefs_pop['energy']}")
    print("=" * 48)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} — {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Reasons:")
        for reason in explanation.split("; "):
            print(f"     • {reason}")

    print()


if __name__ == "__main__":
    main()
