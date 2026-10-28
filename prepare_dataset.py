
"""Normalize a song metadata CSV into data/songs.csv.

Usage:
  python prepare_dataset.py path/to/source.csv --source-name "Dataset title" --license "MIT"
"""
import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "songs.csv"

ALIASES = {
    "song_id": [
        "song_id", "id", "song_uuid", "uuid", "track_id",
        "music_id", "track_uuid"
    ],
    "title": [
        "title", "song_title", "song_name", "music_name",
        "track_name", "name"
    ],
    "artist": [
        "artist", "artists", "singer", "singers",
        "song_singers", "artist_name", "vocalist"
    ],
    "album": [
        "album", "album_name", "album_title", "movie",
        "film", "album_uuid"
    ],
    "year": [
        "year", "release", "release_year", "album_year"
    ],
    "language": ["language", "lang"],
    "genre": ["genre", "genres", "music_genre"],
    "mood_tags": [
        "mood_tags", "mood", "emotion", "tags", "labels"
    ],
    "energy": ["energy", "danceability"],
    "valence": ["valence", "positivity"],
    "description": [
        "description", "summary", "lyrics", "overview"
    ],
    "link": [
        "link", "url", "youtube_url", "spotify_url", "track_url"
    ],
    "artwork_url": [
        "artwork_url", "thumbnail", "image", "image_url", "cover_url"
    ],
}


def norm_name(value):
    return re.sub(
        r"[^a-z0-9]+", "_", str(value).strip().lower()
    ).strip("_")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Path to source CSV")
    parser.add_argument(
        "--source-name",
        default="User-supplied dataset"
    )
    parser.add_argument(
        "--license",
        default="Verify source license before redistribution"
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Merge with existing catalog before deduplication"
    )
    args = parser.parse_args()

    source = Path(args.input_csv)
    if not source.is_file():
        raise SystemExit(f"Input CSV not found: {source}")

    raw = pd.read_csv(source, low_memory=False).fillna("")
    original_cols = {norm_name(c): c for c in raw.columns}

    out = pd.DataFrame(index=raw.index)

    for target, choices in ALIASES.items():
        match = next(
            (original_cols[c] for c in choices if c in original_cols),
            None
        )
        out[target] = raw[match] if match else ""

    # Clean and validate essential fields.
    out["title"] = out["title"].astype(str).str.strip()
    out["artist"] = out["artist"].astype(str).str.strip()

    valid = (
        out["title"].ne("")
        & out["artist"].ne("")
        & out["title"].str.lower().ne("nan")
        & out["artist"].str.lower().ne("nan")
    )
    out = out.loc[valid].copy()

    # Normalize optional fields.
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["year"] = out["year"].apply(
        lambda x: int(x) if pd.notna(x) and 1800 <= x <= 2100 else ""
    )

    out["language"] = out["language"].replace("", "Hindi")
    out["genre"] = out["genre"].replace("", "Bollywood / Unknown")
    out["mood_tags"] = (
        out["mood_tags"]
        .astype(str)
        .str.replace(",", "|", regex=False)
        .str.lower()
    )
    out["energy"] = pd.to_numeric(out["energy"], errors="coerce")
    out["valence"] = pd.to_numeric(out["valence"], errors="coerce")

    out["source"] = args.source_name
    out["license"] = args.license

    # Remove duplicate title/artist combinations.
    def make_key(frame):
        title = (
            frame["title"].astype(str).str.lower()
            .str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip()
        )
        artist = (
            frame["artist"].astype(str).str.lower()
            .str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip()
        )
        return title + "::" + artist

    out["_key"] = make_key(out)
    out = out.drop_duplicates("_key").drop(columns="_key")

    if args.append and OUT.exists():
        current = pd.read_csv(OUT).fillna("")
        out = pd.concat(
            [current, out], ignore_index=True, sort=False
        ).fillna("")

        out["_key"] = make_key(out)
        out = out.drop_duplicates("_key", keep="first").drop(
            columns="_key"
        )

    out = out.reset_index(drop=True)
    out["song_id"] = range(1, len(out) + 1)

    columns = [
        "song_id", "title", "artist", "album", "year",
        "language", "genre", "mood_tags", "energy", "valence",
        "description", "source", "license", "link", "artwork_url"
    ]

    for column in columns:
        if column not in out.columns:
            out[column] = ""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out[columns].to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"Input rows: {len(raw):,}")
    print(f"Valid unique title/artist pairs: {len(out):,}")
    print(f"Output: {OUT}")

    if len(out) < 1000:
        print(
            f"WARNING: catalog is below the 1,000-song target "
            f"by {1000 - len(out):,} records."
        )


if __name__ == "__main__":
    main()

