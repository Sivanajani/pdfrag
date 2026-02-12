import logging
import uuid
import shutil
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, Form
from fastapi.responses import JSONResponse

from app.utils.paths import TMP_DIR, MAX_UPLOAD_SIZE_BYTES, validate_doc_id
from app.services.pdf_service import read_pdf_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["uploads"])


def _is_pdf(file: UploadFile) -> bool:
    # 1) Content-Type check
    if file.content_type == "application/pdf":
        return True
    # 2) Magic header check
    head = file.file.read(5)
    file.file.seek(0)
    return head == b"%PDF-"


async def _check_file_size(file: UploadFile) -> None:
    """Read file size and reject if over limit."""
    file.file.seek(0, 2)  # seek to end
    size = file.file.tell()
    file.file.seek(0)  # reset
    if size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Datei zu gross. Maximum: {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
        )


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Nimmt eine einzelne PDF entgegen, speichert sie in tmp/, gibt eine ID zurueck."""
    if not _is_pdf(file):
        raise HTTPException(status_code=400, detail="Bitte eine PDF-Datei hochladen.")
    await _check_file_size(file)

    uid = uuid.uuid4().hex
    dest = TMP_DIR / f"{uid}.pdf"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"id": uid, "filename": file.filename},
    )


@router.post("/upload/batch")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    results, errors = [], []
    for file in files:
        if not _is_pdf(file):
            errors.append({"filename": file.filename, "error": "Nur PDFs erlaubt"})
            continue
        try:
            await _check_file_size(file)
        except HTTPException:
            errors.append({"filename": file.filename, "error": "Datei zu gross"})
            continue
        uid = uuid.uuid4().hex
        dest = TMP_DIR / f"{uid}.pdf"
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        results.append({"id": uid, "filename": file.filename})

    status_code = status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
    return JSONResponse(status_code=status_code, content={"count": len(results), "items": results, "errors": errors})


@router.get("/upload/{doc_id}/text")
async def extract_text_by_id(
    doc_id: str,
    pages: Optional[str] = Query(None, description="Kommagetrennte 0-basierte Seiten, z. B. '0,1,2'"),
    max_chars: int = Query(20000, ge=1000, le=1_000_000, description="Maximale Anzahl Zeichen")
):
    pdf_path = validate_doc_id(doc_id)

    page_list = None
    if pages:
        try:
            page_list = [int(p.strip()) for p in pages.split(",") if p.strip() != ""]
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungueltiger pages-Parameter.")

    text = read_pdf_text(pdf_path, pages=page_list, max_chars=max_chars)
    return {"id": doc_id, "pages": page_list, "length": len(text), "text": text}


@router.post("/extract-text")
async def extract_text_direct(
    file: UploadFile = File(...),
    pages: Optional[str] = Query(None, description="Kommagetrennte 0-basierte Seiten, z. B. '0,1,2'"),
    max_chars: int = Query(20000, ge=1000, le=1_000_000)
):
    if not _is_pdf(file):
        raise HTTPException(status_code=400, detail="Bitte eine PDF-Datei hochladen.")
    await _check_file_size(file)

    uid = uuid.uuid4().hex
    dest = TMP_DIR / f"{uid}.pdf"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    page_list = None
    if pages:
        try:
            page_list = [int(p.strip()) for p in pages.split(",") if p.strip() != ""]
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungueltiger pages-Parameter.")

    text = read_pdf_text(dest, pages=page_list, max_chars=max_chars)

    try:
        dest.unlink(missing_ok=True)
    except Exception:
        pass

    return {"filename": file.filename, "pages": page_list, "length": len(text), "text": text}


@router.post("/upload-with-text")
async def upload_pdf_with_text(
    file: UploadFile = File(...),
    doc_type: str = Form("unknown"),
    extract: bool = Query(True, description="Wenn true, wird der Text sofort extrahiert."),
):
    """Nimmt eine PDF entgegen, speichert sie und gibt optional direkt den Text zurueck."""
    if not _is_pdf(file):
        raise HTTPException(status_code=400, detail="Bitte eine PDF-Datei hochladen.")
    await _check_file_size(file)

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
        except Exception:
            logger.exception("Textextraktion fehlgeschlagen fuer %s", uid)
            raise HTTPException(status_code=500, detail="Fehler bei Textextraktion.")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
