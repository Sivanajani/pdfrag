from pathlib import Path
from typing import Optional, Iterable
from pypdf import PdfReader

def read_pdf_text(pdf_path: Path, pages: Optional[Iterable[int]] = None, max_chars: Optional[int] = None) -> str:
    """
    Sehr einfache Extraktion für digitale PDFs.
    - pages: z.B. [0,1,2] (0-basiert). None = alle Seiten.
    - max_chars: hartes Limit für Rückgabetext (Performance/Netzwerk).
    """
    r = PdfReader(str(pdf_path))
    page_indexes = pages if pages is not None else range(len(r.pages))
    chunks = []
    for i in page_indexes:
        if i < 0 or i >= len(r.pages):
            continue
        txt = r.pages[i].extract_text() or ""
        chunks.append(txt)

        if max_chars is not None and sum(len(c) for c in chunks) >= max_chars:
            break

    out = "\n".join(chunks)
    if max_chars is not None and len(out) > max_chars:
        out = out[:max_chars]
    return out
