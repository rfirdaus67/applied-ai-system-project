"""Turns the songs to be recommended into chunks --> sent to Gemini.

Sends the scoring/ranking results + info about the songs as a few small chunks of tokens
instead of uploading the whole dataset to the model.

Kept free of Streamlit and the Gemini client so it can be tested separately."""

import csv
import io
from typing import List

import pandas as pd

# The fields sent to Gemini for each recommended song: the attributes are their own columns
# plus the score computed in ranking.py.
CSV_FIELDS = ["rank", "artists", "track_name", "energy", "track_genre", "mood", "score"]


def rows_to_lines(top: pd.DataFrame) -> List[str]:
    """Render the recommended songs as CSV rows, one line per song.

    Written with csv.writer because track names and songs with multiple artists have strings with
    commas. The song id is left out intentionally."""

    lines = []
    for rank, row in enumerate(top.itertuples(index=False), start=1):
        buffer = io.StringIO()
        csv.writer(buffer, lineterminator="").writerow([
            rank,
            row.artists,
            row.track_name,
            f"{row.energy:.3f}",
            row.track_genre,
            row.mood,
            f"{row.final_score:.3f}",
        ])
        lines.append(buffer.getvalue())
    return lines


def chunk_lines(lines: List[str], chunk_size: int = 2) -> List[str]:
    """Group the CSV rows into blocks of chunk_size rows.

    Each block is sent to Gemini as its own part, so the model reads the
    recommendations as a few small chunks of tokens."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    return [
        "\n".join(lines[start:start + chunk_size])
        for start in range(0, len(lines), chunk_size)
    ]


def build_csv_chunks(top: pd.DataFrame, chunk_size: int = 2) -> List[str]:
    """The whole payload for the recommendations: header row, then chunked rows."""
    return [",".join(CSV_FIELDS)] + chunk_lines(rows_to_lines(top), chunk_size)


def format_recommendations(top: pd.DataFrame, explanations: List[str]) -> str:
    """Lay the recommendations out as markdown: title, then score, then reason.

    The title and score come from the DataFrame and only the sentences come from
    Gemini, so the layout is identical every run. Blank lines between the parts
    are what makes Streamlit put them on separate lines."""
    blocks = []
    for position, row in enumerate(top.itertuples(index=False)):
        explanation = (
            explanations[position].strip()
            if position < len(explanations) else ""
        )
        blocks.append(
            f"**{position + 1}. {row.track_name} - {row.artists}**\n\n"
            f"**Score:** {row.final_score:.3f}\n\n"
            f"{explanation}"
        )
    return "\n\n---\n\n".join(blocks)
