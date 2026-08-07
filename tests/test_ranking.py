"""Tests that the priorities a user assigns are reflected in the recommendations,
the cosine-similarity scores, and the prompt being fed to Gemini.


Whatever the user clicks/ranks #1 gets the most weight (6.0),
#2 the next (3.0), and #3 the least (1.0). These tests test this ranking
across the happy cases and the edge cases.
"""
import pytest

from src.ranking import (
   compute_weights,
   build_prefs,
   build_weights,
   build_explanation_prompt,
   score_songs,
   top_songs,
   RANK_WEIGHTS,
   DEFAULT_WEIGHTS,
)

GENRE_FIRST = compute_weights(["Genre", "Mood", "Energy"])
ENERGY_FIRST = compute_weights(["Energy", "Mood", "Genre"])

# ---------------------------------------------------------------------------
# Happy cases: Ranking of all three features
# ---------------------------------------------------------------------------


def test_first_ranked_feature_gets_the_most_weight():
   weights = compute_weights(["Mood", "Energy", "Genre"])
   # Mood was clicked first -> must be the single highest weight.
   assert weights["mood"] == 6.0
   assert weights["mood"] == max(weights.values())




def test_weights_strictly_decrease_with_rank():
   # Rank order: Genre (1st), Mood (2nd), Energy (3rd)
   weights = compute_weights(["Genre", "Mood", "Energy"])
   assert weights["genre"] > weights["mood"] > weights["energy"]
   assert [weights["genre"], weights["mood"], weights["energy"]] == [6.0, 3.0, 1.0]




def test_second_rank_considered_after_first():
   weights = compute_weights(["Energy", "Genre", "Mood"])
   # Energy #1, Genre #2, Mood #3
   assert weights["energy"] == 6.0
   assert weights["genre"] == 3.0
   assert weights["mood"] == 1.0




def test_every_permutation_maps_rank_position_to_weight():
   import itertools
   for order in itertools.permutations(["Genre", "Mood", "Energy"]):
       weights = compute_weights(list(order))
       for position, feat in enumerate(order):
           assert weights[feat.lower()] == RANK_WEIGHTS[position], (
               f"{feat} ranked #{position + 1} should weigh {RANK_WEIGHTS[position]}"
           )




def test_weight_values_are_exactly_the_expected_set():
   weights = compute_weights(["Mood", "Genre", "Energy"])
   assert sorted(weights.values()) == [1.0, 3.0, 6.0]




# ---------------------------------------------------------------------------
# Edge cases: incomplete or unusual rankings
# ---------------------------------------------------------------------------


def test_no_ranking_falls_back_to_neutral_defaults():
   assert compute_weights([]) == DEFAULT_WEIGHTS




def test_partial_ranking_one_feature_is_neutral():
   # Only one feature clicked -> not enough to lock in weights.
   assert compute_weights(["Mood"]) == DEFAULT_WEIGHTS




def test_partial_ranking_two_features_is_neutral():
   assert compute_weights(["Mood", "Energy"]) == DEFAULT_WEIGHTS




def test_default_weights_are_roughly_equal():
   w = compute_weights([])
   # No feature should dominate before the user has ranked.
   assert max(w.values()) - min(w.values()) <= 0.02




def test_compute_weights_does_not_mutate_default_constant():
   w = compute_weights([])
   w["genre"] = 99.0
   # Mutating a returned copy must not corrupt the shared default.
   assert DEFAULT_WEIGHTS["genre"] == 0.33




# ---------------------------------------------------------------------------
# Cosine similarity scoring: the weights must change what gets recommended
# ---------------------------------------------------------------------------


def test_every_song_gets_a_score_between_zero_and_one():
   scored = score_songs("rock", "Energetic", 0.9, GENRE_FIRST)
   assert len(scored) > 0
   assert scored["final_score"].min() >= 0.0
   assert scored["final_score"].max() <= 1.0




def test_exact_genre_match_beats_an_unrelated_genre():
   scored = score_songs("rock", "Energetic", 0.9, GENRE_FIRST).set_index("track_genre")
   # Genre is ranked #1, so a rock song must outscore a classical one.
   assert scored.loc["rock", "final_score"].max() > scored.loc["classical", "final_score"].max()




def test_similar_genre_earns_partial_credit():
   # "alt-rock" shares the word "rock", so it must land between an exact match
   # and something with no words in common at all.
   scored = score_songs("rock", "Energetic", 0.9, GENRE_FIRST).set_index("track_genre")
   exact = scored.loc["rock", "genre_score"].max()
   similar = scored.loc["alt-rock", "genre_score"].max()
   unrelated = scored.loc["classical", "genre_score"].max()
   assert unrelated < similar < exact




def test_energy_score_is_highest_for_the_closest_energy():
   scored = score_songs("rock", "Energetic", 0.5, GENRE_FIRST)
   closest = scored.loc[(scored["energy"] - 0.5).abs().idxmin()]
   assert closest["energy_score"] == scored["energy_score"].max()




def test_energy_score_uses_absolute_distance():
   scored = score_songs("rock", "Energetic", 0.9, GENRE_FIRST)
   row = scored.iloc[0]
   assert row["energy_score"] == pytest.approx(1 - abs(row["energy"] - 0.9))




def test_the_top_priority_decides_the_recommendations():
   # Same preferences, opposite priority: rock at very low energy, which the rock
   # songs in the catalog do not have. Genre-first must still pick a rock song;
   # energy-first must give up the genre for a song closer to the target energy.
   genre_led = top_songs(score_songs("rock", "Energetic", 0.15, GENRE_FIRST), k=1)
   energy_led = top_songs(score_songs("rock", "Energetic", 0.15, ENERGY_FIRST), k=1)

   assert "rock" in genre_led.loc[0, "track_genre"]
   assert genre_led.loc[0, "track_name"] != energy_led.loc[0, "track_name"]
   assert energy_led.loc[0, "energy_score"] > genre_led.loc[0, "energy_score"]




def test_unmatched_preferences_still_produce_recommendations():
   # Blank inputs must not crash: genre and mood simply score 0 and energy decides.
   scored = score_songs("", "", 0.5, GENRE_FIRST)
   assert scored["genre_score"].max() == 0.0
   assert scored["mood_score"].max() == 0.0
   assert len(top_songs(scored)) == 5




def test_top_songs_returns_five_in_descending_order():
   ranked = top_songs(score_songs("pop", "Happy", 0.8, GENRE_FIRST))
   assert len(ranked) == 5
   assert list(ranked["final_score"]) == sorted(ranked["final_score"], reverse=True)




def test_the_same_preferences_always_give_the_same_recommendations():
   # The whole point of scoring in Python: no run-to-run drift.
   first = top_songs(score_songs("pop", "Happy", 0.8, GENRE_FIRST))
   second = top_songs(score_songs("pop", "Happy", 0.8, GENRE_FIRST))
   assert list(first["track_name"]) == list(second["track_name"])




# ---------------------------------------------------------------------------
# Payload + prompt: the weighting must survive into what Gemini receives
# ---------------------------------------------------------------------------


def test_payload_carries_preferences_and_computed_weights():
   prefs = build_prefs("pop", "Happy", 0.85)
   weights = build_weights(["Mood", "Energy", "Genre"])
   assert prefs["user_preferences"] == {
       "genre": "pop", "mood": "Happy", "energy": 0.85,
   }
   assert weights["weights"]["mood"] == 6.0




def test_prompt_reflects_the_highest_priority_weight():
   prompt = build_explanation_prompt(
       build_prefs("pop", "Happy", 0.85), build_weights(["Mood", "Energy", "Genre"]), 5
   )
   # The top-ranked feature's weight must appear alongside its name in the prompt.
   assert "mood=6.0" in prompt
   assert "energy=3.0" in prompt
   assert "genre=1.0" in prompt




def test_prompt_includes_user_preferences():
   prompt = build_explanation_prompt(
       build_prefs("jazz", "Chill", 0.3), build_weights(["Genre", "Mood", "Energy"]), 5
   )
   assert "genre=jazz" in prompt
   assert "mood=Chill" in prompt
   assert "energy=0.3" in prompt




def test_prompt_names_top_priority_as_dominant():
   # Energy ranked #1 -> the prompt must tell the model energy dominated.
   prompt = build_explanation_prompt(
       build_prefs("pop", "Happy", 0.9), build_weights(["Energy", "Genre", "Mood"]), 5
   )
   assert "most important feature is energy" in prompt.lower()
   assert "higher weight means more important" in prompt.lower()




def test_prompt_states_higher_weight_is_more_important():
   # Regression guard: the legend must not claim "1 = most important".
   prompt = build_explanation_prompt(
       build_prefs("pop", "Happy", 0.9), build_weights(["Energy", "Genre", "Mood"]), 5
   )
   assert "1 = most important" not in prompt




def test_prompt_interpolates_real_weight_numbers():
   # Regression guard: the weights must be actual numbers, not literal
   # placeholder text like weights['energy'].
   prompt = build_explanation_prompt(
       build_prefs("pop", "Happy", 0.9), build_weights(["Energy", "Genre", "Mood"]), 5
   )
   assert "weights[" not in prompt
   assert "energy=6.0" in prompt




def test_prompt_forbids_reordering_or_rescoring():
   # The ranking is already decided by cosine similarity, so the model must not
   # touch it -- this is what stops the AI from doing the judging again.
   prompt = build_explanation_prompt(
       build_prefs("pop", "Happy", 0.9), build_weights(["Energy", "Genre", "Mood"]), 5
   ).lower()
   assert "do not reorder" in prompt
   assert "already been chosen" in prompt
   assert "second-guess any score" in prompt




def test_prompt_states_how_many_songs_it_will_receive():
   prefs = build_prefs("pop", "Happy", 0.9)
   weights = build_weights(["Energy", "Genre", "Mood"])
   assert "3 songs" in build_explanation_prompt(prefs, weights, 3)
   assert "5 songs" in build_explanation_prompt(prefs, weights, 5)
