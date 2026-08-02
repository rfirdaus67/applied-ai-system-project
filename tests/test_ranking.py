"""Tests that the priorities a user assigns are reflected in the recommendations and prompt being fed to Gemini.


Whatever the user clicks/ranks #1 gets the most weight (6.0),
#2 the next (3.0), and #3 the least (1.0). These tests test this ranking
across the happy cases and the edge cases.
"""
from src.ranking import (
   compute_weights,
   build_rag_payload,
   build_prompt,
   RANK_WEIGHTS,
   DEFAULT_WEIGHTS,
)

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
# Payload + prompt: the weighting must survive into what Gemini receives
# ---------------------------------------------------------------------------


def test_payload_carries_computed_weights():
   payload = build_rag_payload("pop", "Happy", 0.85, ["Mood", "Energy", "Genre"])
   assert payload["user_preferences"] == {
       "genre": "pop", "mood": "Happy", "energy": 0.85,
   }
   assert payload["dynamic_weights"]["mood"] == 6.0




def test_prompt_reflects_the_highest_priority_weight():
   payload = build_rag_payload("pop", "Happy", 0.85, ["Mood", "Energy", "Genre"])
   prompt = build_prompt(payload)
   # The top-ranked feature's weight must appear alongside its name in the prompt.
   assert "mood=6.0" in prompt
   assert "energy=3.0" in prompt
   assert "genre=1.0" in prompt




def test_prompt_includes_user_preferences():
   payload = build_rag_payload("jazz", "Chill", 0.3, ["Genre", "Mood", "Energy"])
   prompt = build_prompt(payload)
   assert "genre=jazz" in prompt
   assert "mood=Chill" in prompt
   assert "energy=0.3" in prompt




def test_prompt_names_top_priority_as_dominant():
   # Energy ranked #1 -> the prompt must tell the model energy dominates.
   payload = build_rag_payload("pop", "Happy", 0.9, ["Energy", "Genre", "Mood"])
   prompt = build_prompt(payload)
   assert "most important feature is energy" in prompt.lower()
   assert "higher weight means more important" in prompt.lower()




def test_prompt_states_higher_weight_is_more_important():
   # Regression guard: the legend must not claim "1 = most important".
   payload = build_rag_payload("pop", "Happy", 0.9, ["Energy", "Genre", "Mood"])
   prompt = build_prompt(payload)
   assert "1 = most important" not in prompt




def test_prompt_interpolates_real_weight_numbers_in_scoring():
   # Regression guard: scoring must contain actual numbers, not literal
   # placeholder text like weights['energy'].
   payload = build_rag_payload("pop", "Happy", 0.9, ["Energy", "Genre", "Mood"])
   prompt = build_prompt(payload)
   assert "weights[" not in prompt
   # Energy #1 -> its 6.0 weight appears in the energy scoring term.
   assert "6.0 * energy_closeness" in prompt
