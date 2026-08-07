"""Tests for the CSV chunks handed to Gemini.

Only the recommended songs are sent, as chunks of CSV rows, so these check that
the rows carry the right fields, that commas in track names cannot break the
format, and that the chunking splits where it should.
"""
import pandas as pd
import pytest

from src.scoring import (
    CSV_FIELDS,
    build_csv_chunks,
    chunk_lines,
    format_recommendations,
    rows_to_lines,
)

# Row 2 has commas and a semicolon in exactly the places that would corrupt a
# naive f-string join.
TOP_SONGS = pd.DataFrame([
    {
        "id": 7, "artists": "Ghost", "track_name": "Mary On A Cross",
        "energy": 0.9, "track_genre": "hard-rock", "mood": "Intense",
        "final_score": 0.913,
    },
    {
        "id": 12, "artists": "Stephen Sanchez;Em Beihold",
        "track_name": "Until I Found You, Em Beihold Version",
        "energy": 0.55, "track_genre": "singer-songwriter", "mood": "Mellow",
        "final_score": 0.4,
    },
    {
        "id": 3, "artists": "Gen Hoshino", "track_name": "Comedy",
        "energy": 0.461, "track_genre": "acoustic", "mood": "Chill",
        "final_score": 0.222,
    },
])


def test_each_song_becomes_one_ranked_row():
    lines = rows_to_lines(TOP_SONGS)
    assert len(lines) == 3
    assert lines[0].startswith("1,Ghost,Mary On A Cross,0.900,hard-rock,Intense,0.91")
    assert lines[2].startswith("3,")


def test_commas_in_track_names_are_quoted_not_split():
    line = rows_to_lines(TOP_SONGS)[1]
    assert '"Until I Found You, Em Beihold Version"' in line
    # Quoted correctly, the row still parses back into exactly seven fields.
    import csv, io
    assert len(next(csv.reader(io.StringIO(line)))) == len(CSV_FIELDS)


def test_the_song_id_is_never_sent():
    for line in rows_to_lines(TOP_SONGS):
        assert not line.startswith("7,")
        assert "id" not in line


def test_scores_are_rounded_for_the_prompt():
    lines = rows_to_lines(TOP_SONGS)
    assert lines[0].endswith("0.913")
    assert lines[1].endswith("0.400")


def test_chunk_lines_groups_rows_into_blocks():
    lines = [f"line {n}" for n in range(5)]
    chunks = chunk_lines(lines, chunk_size=2)
    assert len(chunks) == 3
    assert chunks[0] == "line 0\nline 1"
    assert chunks[-1] == "line 4"


def test_chunk_lines_rejects_a_zero_chunk_size():
    with pytest.raises(ValueError):
        chunk_lines(["a"], chunk_size=0)


def test_payload_starts_with_the_header_then_chunks_the_rows():
    chunks = build_csv_chunks(TOP_SONGS, chunk_size=2)
    assert chunks[0] == ",".join(CSV_FIELDS)
    # 3 songs at 2 per chunk -> a header part plus two row parts.
    assert len(chunks) == 3
    assert chunks[1].count("\n") == 1
    assert "\n" not in chunks[2]


def test_every_recommended_song_survives_the_chunking():
    joined = "\n".join(build_csv_chunks(TOP_SONGS, chunk_size=2))
    for track in TOP_SONGS["track_name"]:
        assert track in joined


# ---------------------------------------------------------------------------
# Output layout: built in Python so it cannot vary between runs
# ---------------------------------------------------------------------------

EXPLANATIONS = ["Because it rocks.", "Because it is mellow.", "Because it is calm."]


def test_title_score_and_explanation_are_on_separate_lines():
    block = format_recommendations(TOP_SONGS.head(1), EXPLANATIONS)
    # Blank lines between the three parts are what Streamlit renders as breaks.
    assert block == (
        "**1. Mary On A Cross - Ghost**\n"
        "\n"
        "**Score:** 0.913\n"
        "\n"
        "Because it rocks."
    )


def test_songs_are_numbered_in_rank_order_and_separated():
    output = format_recommendations(TOP_SONGS, EXPLANATIONS)
    assert output.index("**1.") < output.index("**2.") < output.index("**3.")
    assert output.count("\n\n---\n\n") == len(TOP_SONGS) - 1


def test_the_score_comes_from_the_dataframe_not_the_model():
    # Even if the model says something wrong, the printed score is ours.
    output = format_recommendations(TOP_SONGS, ["the score is 1.00", "", ""])
    assert "**Score:** 0.91" in output


def test_missing_explanations_leave_the_layout_intact():
    # A short or truncated response must not crash or drop a song.
    output = format_recommendations(TOP_SONGS, ["only one"])
    assert "**3. Comedy - Gen Hoshino**" in output
    assert "**Score:** 0.22" in output
