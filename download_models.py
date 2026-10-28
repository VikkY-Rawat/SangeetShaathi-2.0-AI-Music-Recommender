from pathlib import Path
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

# Multilingual (includes Hindi) multi-label emotion model.
EMOTION_REPO = "tabularisai/multilingual-emotion-classification"
# Multilingual sentence embeddings; supports Hindi and many other languages.
EMBEDDING_REPO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def main():
    print("Downloading emotion model. This can take several minutes...")
    snapshot_download(repo_id=EMOTION_REPO, local_dir=MODELS / "emotion")
    print("Downloading multilingual sentence-embedding model...")
    snapshot_download(repo_id=EMBEDDING_REPO, local_dir=MODELS / "embeddings")
    print("\nModels saved in the project's models/ folder.")
    print("You can now run the app with internet disconnected (assuming downloads completed).")

if __name__ == "__main__":
    main()
