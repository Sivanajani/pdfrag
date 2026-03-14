import io
import logging
import tempfile
from pathlib import Path
from typing import Optional, Iterable

from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

# Seiten mit weniger Zeichen als dieser Schwellenwert gelten als gescannt
_OCR_THRESHOLD_PER_PAGE = 50


def _ocr_single_page(reader: PdfReader, page_index: int) -> str:
    """Schreibt eine einzelne PDF-Seite in eine Temp-Datei und OCRt sie via Gemini."""
    from app.services.gemini_client import ocr_pdf_with_gemini

    writer = PdfWriter()
    writer.add_page(reader.pages[page_index])

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        writer.write(tmp)

    try:
        return ocr_pdf_with_gemini(tmp_path)
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass


def read_pdf_text(pdf_path: Path, pages: Optional[Iterable[int]] = None, max_chars: Optional[int] = None) -> str:
    """
    Extrahiert Text aus PDFs seitenweise.

    Pro Seite:
      - pypdf extrahiert den Text
      - Liefert die Seite weniger als _OCR_THRESHOLD_PER_PAGE Zeichen →
        Gemini OCR nur für diese Seite

    - pages: z.B. [0,1,2] (0-basiert). None = alle Seiten.
    - max_chars: hartes Limit für Rückgabetext.
    """
    r = PdfReader(str(pdf_path))
    page_indexes = list(pages if pages is not None else range(len(r.pages)))
    page_texts = []

    for i in page_indexes:
        if i < 0 or i >= len(r.pages):
            continue

        txt = (r.pages[i].extract_text() or "").strip()

        if len(txt) < _OCR_THRESHOLD_PER_PAGE:
            logger.debug("Seite %d: nur %d Zeichen via pypdf – OCR wird verwendet", i + 1, len(txt))
            try:
                txt = _ocr_single_page(r, i)
            except Exception:
                logger.exception("OCR fehlgeschlagen für Seite %d – Seite wird übersprungen", i + 1)
                txt = ""

        page_texts.append(txt)

        if max_chars is not None and sum(len(t) for t in page_texts) >= max_chars:
            break

    out = "\n\n".join(t for t in page_texts if t)
    if max_chars is not None and len(out) > max_chars:
        out = out[:max_chars]

    return out
