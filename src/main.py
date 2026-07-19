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
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print()
    print("=" * 48)
    print(f"  Top {len(recommendations)} recommendations")
    print(f"  for {user_prefs['mood']} / {user_prefs['genre']} "
          f"@ energy {user_prefs['energy']}")
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
