# SangeetShaathi 2.0 — Premium AI Music Discovery

Streamlit app using a multilingual Transformer emotion classifier, multilingual sentence embeddings, hybrid ranking, mood shortcuts, catalog filters, SQLite feedback and favorites.

## Windows / VS Code setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python download_models.py
streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

## Offline behavior
Models are downloaded once with `python download_models.py` and loaded from local `models/` folders. Model inference works offline after a successful download. External search/streaming links and remote images may require internet.

## Current starter catalog
The included CSV is a small illustrative starter dataset. It does **not** yet contain 1,000 verified records. The UI reports the actual catalog count and does not fabricate songs to meet the target.

## Build a 1,000+ record catalog
1. Review the dataset license and attribution requirements before use.
2. Download a CSV from a source you are permitted to use.
3. Inspect its column names and sample rows.
4. Run the normalization script, e.g.:

```powershell
python prepare_dataset.py "C:\path\to\source_songs.csv" --source-name "Dataset name" --license "MIT"
```

To merge a second compatible CSV into the existing catalog:

```powershell
python prepare_dataset.py "C:\path\to\second_source.csv" --source-name "Second source" --license "MIT" --append
```

The script maps common title/artist/album/year columns, removes duplicate title/artist pairs, adds provenance fields, and reports the number of usable records. It does not create fake songs or fabricate mood labels. Inspect the output before submission.

Potential metadata source to evaluate: https://github.com/MrAsacker/bollywood-songs-metadata (repository describes 57,005 songs and an MIT license; check the current repo's files, schema, and license before importing). MoodWave is research-use-only according to its dataset card, so do not use it unless its terms fit your project: https://huggingface.co/datasets/anujpaude1/moodwave-music-tagging

## Required CSV schema
`song_id,title,artist,album,year,language,genre,mood_tags,energy,valence,description,source,license,link,artwork_url`

Mood tags are pipe-separated, for example `joy|hope|uplifting`.

## Project features
- Predefined mood shortcuts: Happy, Sad, Emotional, Angry, Calm, Energetic, Motivational, Romantic, Sleep/Relax, Party, Focus/Study, Nostalgic, Lonely, Spiritual and Hopeful.
- Natural-language AI search in Hindi/English/Hinglish (quality depends on model and input).
- Local Transformer emotion predictions.
- Sentence Transformer embeddings and cosine similarity.
- Ranking that combines semantic relevance, mood metadata and feedback.
- Catalog search/filter/sort/pagination.
- SQLite favorites and likes/dislikes.
- Model information and dataset count in the UI.

## Evaluation
The project does not claim an invented accuracy score. For an advanced submission, create a labelled holdout set and measure emotion precision/recall/macro-F1. Collect relevance judgments or user ratings to evaluate Precision@5, Recall@5 and NDCG@5. Distinguish classifier metrics from recommendation metrics.

## Known limitations
- The initial catalog has illustrative sample metadata; expand it before final submission.
- Some tags and descriptions in public song datasets may be missing or inconsistent.
- The emotion classifier can misread sarcasm, slang, and code-mixed text.
- A recommendation match score is a ranking signal, not a calibrated probability.
- The app links to external song searches; it does not host copyrighted audio.
