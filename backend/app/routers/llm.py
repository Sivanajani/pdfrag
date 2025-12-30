from typing import Optional, List, Any, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.utils.paths import TMP_DIR
from app.services.pdf_service import read_pdf_text
from app.services.gemini_client import extract_structured_data_from_text

from app.schemas.radiology import RadiologyEvent
from app.services.gemini_client import extract_radiology_events_from_text



router = APIRouter(tags=["llm"])

class LLMExtractRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000

class ExtractedItem(BaseModel):
    source_type: Optional[str] = None
    body_part: Optional[str] = None
    concept: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    note: Optional[str] = None

class LLMExtractResponse(BaseModel):
    items: List[ExtractedItem]

class RadiologyExtractRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000

class RadiologyExtractResponse(BaseModel):
    events: List[RadiologyEvent]


@router.post("/llm/extract", response_model=LLMExtractResponse)
async def llm_extract(payload: LLMExtractRequest):
    """
    Nimmt entweder:
    - doc_id: PDF wurde bereits hochgeladen (tmp/<doc_id>.pdf)
    - text: bereits extrahierter Text (direkt vom Frontend oder anderem Endpoint)

    Gibt strukturierte Items aus dem Bericht zurück, extrahiert via Gemini.
    """
    if not payload.doc_id and not payload.text:
        raise HTTPException(
            status_code=400,
            detail="Bitte entweder 'doc_id' oder 'text' angeben."
        )

    if payload.doc_id and payload.text:
        raise HTTPException(
            status_code=400,
            detail="Bitte entweder 'doc_id' ODER 'text' angeben, nicht beides."
        )

    # 1) Text besorgen
    if payload.doc_id:
        pdf_path = TMP_DIR / f"{payload.doc_id}.pdf"
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF nicht gefunden (ID unbekannt).")

        raw_text = read_pdf_text(pdf_path, max_chars=payload.max_chars)
    else:
        raw_text = payload.text[: payload.max_chars]

    if not raw_text:
        raise HTTPException(status_code=400, detail="Kein Text gefunden oder leer.")

    # 2) LLM aufrufen
    try:
        items_raw: List[Dict[str, Any]] = extract_structured_data_from_text(raw_text)
    except Exception as e:
        # In der Praxis: Logging hinzufügen
        raise HTTPException(status_code=500, detail=f"Fehler bei LLM-Extraktion: {e}")

    items = [ExtractedItem(**item) for item in items_raw]

    return LLMExtractResponse(items=items)

@router.post("/llm/extract-radiology", response_model=RadiologyExtractResponse)
async def llm_extract_radiology(payload: RadiologyExtractRequest):
    if not payload.doc_id and not payload.text:
        raise HTTPException(status_code=400, detail="Bitte entweder 'doc_id' oder 'text' angeben.")
    if payload.doc_id and payload.text:
        raise HTTPException(status_code=400, detail="Bitte entweder 'doc_id' ODER 'text' angeben, nicht beides.")

    # 1) Text besorgen
    if payload.doc_id:
        pdf_path = TMP_DIR / f"{payload.doc_id}.pdf"
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF nicht gefunden (ID unbekannt).")
        raw_text = read_pdf_text(pdf_path, max_chars=payload.max_chars)
    else:
        raw_text = payload.text[: payload.max_chars]

    if not raw_text:
        raise HTTPException(status_code=400, detail="Kein Text gefunden oder leer.")

    # 2) Gemini → LISTE von dicts
    try:
        raw_list = extract_radiology_events_from_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Radiology-Extraktion: {e}")

    # 3) Pydantic: jedes Element validieren
    try:
        events = [RadiologyEvent(**r) for r in raw_list]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"RadiologyEvent Validation failed: {e}")

    return RadiologyExtractResponse(events=events)
