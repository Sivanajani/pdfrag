from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from pathlib import Path
import uuid, shutil

from app.utils.paths import TMP_DIR
from app.services.pdf_service import read_pdf_text

router = APIRouter(tags=["uploads"])

def _is_pdf(file: UploadFile) -> bool:
    # 1) Content-Type check
    if file.content_type == "application/pdf":
        return True
    # 2) Magic header check (non-seekable stream, daher kurz anlesen)
    head = file.file.read(5)
    file.file.seek(0)
    return head == b"%PDF-"


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Nimmt eine einzelne PDF entgegen, speichert sie in tmp/, gibt eine ID zurück."""
    if not _is_pdf(file):
        raise HTTPException(status_code=400, detail="Bitte eine PDF-Datei hochladen.")

    uid = uuid.uuid4().hex
    dest = TMP_DIR / f"{uid}.pdf"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"id": uid, "filename": file.filename, "path": f"/tmp/{uid}.pdf"},
    )


@router.post("/upload/batch")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    results, errors = [], []
    for file in files:
        if not _is_pdf(file):
            errors.append({"filename": file.filename, "error": "Nur PDFs erlaubt"})
            continue
        uid = uuid.uuid4().hex
        dest = TMP_DIR / f"{uid}.pdf"
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        results.append({"id": uid, "filename": file.filename, "path": f"/tmp/{uid}.pdf"})

    status_code = status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
    return JSONResponse(status_code=status_code, content={"count": len(results), "items": results, "errors": errors})

# --- NEU: Text aus bereits hochgeladener Datei (per ID) ---
@router.get("/upload/{doc_id}/text")
async def extract_text_by_id(
    doc_id: str,
    pages: Optional[str] = Query(None, description="Kommagetrennte 0-basierte Seiten, z. B. '0,1,2'"),
    max_chars: int = Query(20000, ge=1000, le=1_000_000, description="Maximale Anzahl Zeichen")
):
    pdf_path = TMP_DIR / f"{doc_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF nicht gefunden (ID unbekannt).")

    page_list = None
    if pages:
        try:
            page_list = [int(p.strip()) for p in pages.split(",") if p.strip() != ""]
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungültiger pages-Parameter.")

    text = read_pdf_text(pdf_path, pages=page_list, max_chars=max_chars)
    return {"id": doc_id, "pages": page_list, "length": len(text), "text": text}

# --- NEU: Ad-hoc-Extraktion ohne Speichern ---
@router.post("/extract-text")
async def extract_text_direct(
    file: UploadFile = File(...),
    pages: Optional[str] = Query(None, description="Kommagetrennte 0-basierte Seiten, z. B. '0,1,2'"),
    max_chars: int = Query(20000, ge=1000, le=1_000_000)
):
    if not _is_pdf(file):
        raise HTTPException(status_code=400, detail="Bitte eine PDF-Datei hochladen.")

    # Temporär in TMP schreiben, dann lesen (pypdf braucht Pfad/seekbare Quelle)
    uid = uuid.uuid4().hex
    dest = TMP_DIR / f"{uid}.pdf"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    page_list = None
    if pages:
        try:
            page_list = [int(p.strip()) for p in pages.split(",") if p.strip() != ""]
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungültiger pages-Parameter.")

    text = read_pdf_text(dest, pages=page_list, max_chars=max_chars)

    # Optional: temporäre Datei direkt wieder löschen
    try:
        dest.unlink(missing_ok=True)
    except Exception:
        pass

    return {"filename": file.filename, "pages": page_list, "length": len(text), "text": text}

@router.post("/upload-with-text")
async def upload_pdf_with_text(
    file: UploadFile = File(...),
    doc_type: str = Form(...),  # <-- NEU
    extract: bool = Query(True, description="Wenn true, wird der Text sofort extrahiert."),
):
    """Nimmt eine PDF entgegen, speichert sie und gibt optional direkt den Text zurück."""
    if not _is_pdf(file):
        raise HTTPException(status_code=400, detail="Bitte eine PDF-Datei hochladen.")

    uid = uuid.uuid4().hex
    dest = TMP_DIR / f"{uid}.pdf"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    result = {"id": uid, "filename": file.filename, "doc_type": doc_type}  

    if extract:
        try:
            text = read_pdf_text(dest, max_chars=None)
            result["text"] = text
            result["length"] = len(text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler bei Textextraktion: {e}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

