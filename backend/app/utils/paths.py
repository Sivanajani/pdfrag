import re
import time
import logging
from pathlib import Path

from fastapi import HTTPException

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# --- Security constants ---
MAX_UPLOAD_SIZE_BYTES = 1024 * 1024 * 1024  # 1 GB
TMP_MAX_AGE_SECONDS = 3600  # 1 hour

_DOC_ID_RE = re.compile(r"^[a-f0-9]{32}$")


def validate_doc_id(doc_id: str) -> Path:
    """Validate doc_id as hex UUID and return the resolved PDF path.

    Raises HTTPException 400 if doc_id format is invalid,
    or 404 if the file does not exist.
    """
    if not _DOC_ID_RE.match(doc_id):
        raise HTTPException(status_code=400, detail="Ungueltige Dokument-ID.")

    pdf_path = TMP_DIR / f"{doc_id}.pdf"

    # Extra safeguard: ensure resolved path stays inside TMP_DIR
    try:
        pdf_path.resolve().relative_to(TMP_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungueltige Dokument-ID.")

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF nicht gefunden (ID unbekannt).")

    return pdf_path


def cleanup_tmp(max_age_seconds: int = TMP_MAX_AGE_SECONDS) -> int:
    """Delete files in TMP_DIR older than max_age_seconds. Returns count of deleted files."""
    now = time.time()
    deleted = 0
    for f in TMP_DIR.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > max_age_seconds:
            try:
                f.unlink()
                deleted += 1
            except OSError:
                pass
    if deleted:
        logger.info("tmp cleanup: %d file(s) deleted", deleted)
    return deleted
