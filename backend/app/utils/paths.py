from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)