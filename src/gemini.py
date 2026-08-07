"""Gemini call: inputs CSV data of recommended songs and writes up explanations"""
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai.types import GenerateContentConfig

import json

from ranking import build_explanation_prompt, score_songs, top_songs
from scoring import build_csv_chunks, format_recommendations

MODEL = "gemini-3.6-flash"

# How many songs to recommend, and how many CSV rows to put in each chunk.
TOP_K = 5
CHUNK_SIZE = 2

# One explanation per song, in the order the songs were sent and forces same explanation format everytime
explanation = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "rank": {"type": "integer"},
            "explanation": {"type": "string"},
        },
        "required": ["rank", "explanation"],
    },
}

# genai.Client() automatically reads GEMINI_API_KEY from the environment
client = genai.Client()


def parse_explanations(response_text):
    """Uses JSON ouput to get the explanation per song, in rank order.

    Falls back to the raw text as a single explanation if the response somehow
    is not the JSON needed. """
    try:
        items = json.loads(response_text)
        items.sort(key=lambda item: item.get("rank", 0))
        return [str(item.get("explanation", "")) for item in items]
    except (json.JSONDecodeError, AttributeError, TypeError):
        return [response_text]


def generate(prefs_payload, weights_payload):
    """Ranks the catalog, then ask Gemini output the ordered songs + explanations.

    Returns (explanation_text, top_songs_dataframe, prompt_token_count).
    """
    prefs = prefs_payload["user_preferences"]
    weights = weights_payload["weights"]

    scored = score_songs(prefs["genre"], prefs["mood"], prefs["energy"], weights)
    top = top_songs(scored, k=TOP_K)

    # The recommendations go in as chunks of CSV rows
    contents = [build_explanation_prompt(prefs_payload, weights_payload, len(top))]
    contents.extend(build_csv_chunks(top, chunk_size=CHUNK_SIZE))

    token_count = client.models.count_tokens(
        model=MODEL, contents=contents
    ).total_tokens

    # Using JSON to get wanted layout:
    # Returns the sentences, and format_recommendations() builds the
    # title / score / explanation block the same way every time.
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=explanation,
        ),
    )

    return format_recommendations(top, parse_explanations(response.text)), top, token_count
