from dotenv import load_dotenv
load_dotenv()

import os
from google import genai
from google.genai.types import GenerateContentConfig

from ranking import build_prompt

# genai.Client() automatically reads GEMINI_API_KEY from the environment
client = genai.Client()

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "spotify_songs.csv")

# The dataset is small (100 songs), so we can hand the whole thing to the model.
csv_file = client.files.upload(file=CSV_PATH)


def generate(rag_payload):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            csv_file,
            build_prompt(rag_payload),
        ],
        config=GenerateContentConfig(response_modalities=["TEXT"]),
    )
    return response.text

