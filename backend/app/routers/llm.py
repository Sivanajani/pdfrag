from typing import Optional, List, Any, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.utils.paths import TMP_DIR
from app.services.pdf_service import read_pdf_text
from app.services.gemini_client import (
    extract_structured_data_from_text,
    extract_radiology_events_from_text,
    extract_radiotherapy_events_from_text,
    extract_pathology_events_from_text,
    extract_surgery_events_from_text,
    extract_sarcoma_board_events_from_text,
    extract_systemic_therapy_events_from_text,
    classify_document_type,
)

from app.schemas.radiology import RadiologyEvent
from app.schemas.radioTherapy import RadiotherapyEvent
from app.schemas.pathologies import PathologyEvent
from app.schemas.surgeries import SurgeryEvent
from app.schemas.sarcoma_boards import SarcomaBoardEvent
from app.schemas.systemic_therapies import SystemicTherapyEvent



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


class ClassifyDocTypeRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 5000  # Für Classification reichen 5000 Zeichen


class ClassifyDocTypeResponse(BaseModel):
    doc_type: str  # "radiology" | "radiotherapy" | "pathology" | "surgery" | "sarcoma_board" | "systemic_therapy"


@router.post("/llm/classify-doc-type", response_model=ClassifyDocTypeResponse)
async def classify_doc_type(payload: ClassifyDocTypeRequest):
    """
    Klassifiziert einen Dokumententext automatisch in einen der 6 Dokumenttypen.

    Nimmt entweder:
    - doc_id: PDF wurde bereits hochgeladen (tmp/<doc_id>.pdf)
    - text: bereits extrahierter Text

    Gibt zurück: "radiology" | "radiotherapy" | "pathology" | "surgery" | "sarcoma_board" | "systemic_therapy"
    """
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

    # 2) Gemini Classification
    try:
        doc_type = classify_document_type(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Dokumenten-Klassifikation: {e}")

    return ClassifyDocTypeResponse(doc_type=doc_type)


# ============================================================================
# RADIOTHERAPY EXTRACTION
# ============================================================================

class RadiotherapyExtractRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000


class RadiotherapyExtractResponse(BaseModel):
    events: List[RadiotherapyEvent]


@router.post("/llm/extract-radiotherapy", response_model=RadiotherapyExtractResponse)
async def llm_extract_radiotherapy(payload: RadiotherapyExtractRequest):
    """
    Extrahiert Radiotherapie-Daten aus einem Strahlentherapie-Bericht.
    """
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
        raw_list = extract_radiotherapy_events_from_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Radiotherapy-Extraktion: {e}")

    # 3) Pydantic: jedes Element validieren
    try:
        events = [RadiotherapyEvent(**r) for r in raw_list]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"RadiotherapyEvent Validation failed: {e}")

    return RadiotherapyExtractResponse(events=events)


# ============================================================================
# PATHOLOGY EXTRACTION
# ============================================================================

class PathologyExtractRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000


class PathologyExtractResponse(BaseModel):
    events: List[PathologyEvent]


@router.post("/llm/extract-pathology", response_model=PathologyExtractResponse)
async def llm_extract_pathology(payload: PathologyExtractRequest):
    """
    Extrahiert Pathologie-Daten aus einem Pathologie-Befund.
    """
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
        raw_list = extract_pathology_events_from_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Pathology-Extraktion: {e}")

    # 3) Pydantic: jedes Element validieren
    try:
        events = [PathologyEvent(**r) for r in raw_list]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PathologyEvent Validation failed: {e}")

    return PathologyExtractResponse(events=events)


# ============================================================================
# SURGERY EXTRACTION
# ============================================================================

class SurgeryExtractRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000


class SurgeryExtractResponse(BaseModel):
    events: List[SurgeryEvent]


@router.post("/llm/extract-surgery", response_model=SurgeryExtractResponse)
async def llm_extract_surgery(payload: SurgeryExtractRequest):
    """
    Extrahiert Chirurgie-Daten aus einem Operations-Bericht.
    """
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
        raw_list = extract_surgery_events_from_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Surgery-Extraktion: {e}")

    # 3) Pydantic: jedes Element validieren
    try:
        events = [SurgeryEvent(**r) for r in raw_list]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"SurgeryEvent Validation failed: {e}")

    return SurgeryExtractResponse(events=events)


# ============================================================================
# SARCOMA BOARD EXTRACTION
# ============================================================================

class SarcomaBoardExtractRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000


class SarcomaBoardExtractResponse(BaseModel):
    events: List[SarcomaBoardEvent]


@router.post("/llm/extract-sarcoma-board", response_model=SarcomaBoardExtractResponse)
async def llm_extract_sarcoma_board(payload: SarcomaBoardExtractRequest):
    """
    Extrahiert Sarkom-Board-Daten aus einem Tumorboard-Protokoll.
    """
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
        raw_list = extract_sarcoma_board_events_from_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Sarcoma Board-Extraktion: {e}")

    # 3) Pydantic: jedes Element validieren
    try:
        events = [SarcomaBoardEvent(**r) for r in raw_list]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"SarcomaBoardEvent Validation failed: {e}")

    return SarcomaBoardExtractResponse(events=events)


# ============================================================================
# SYSTEMIC THERAPY EXTRACTION
# ============================================================================

class SystemicTherapyExtractRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000


class SystemicTherapyExtractResponse(BaseModel):
    events: List[SystemicTherapyEvent]


@router.post("/llm/extract-systemic-therapy", response_model=SystemicTherapyExtractResponse)
async def llm_extract_systemic_therapy(payload: SystemicTherapyExtractRequest):
    """
    Extrahiert Systemische-Therapie-Daten aus einem Chemotherapie/Immuntherapie-Bericht.
    """
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
        raw_list = extract_systemic_therapy_events_from_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Systemic Therapy-Extraktion: {e}")

    # 3) Pydantic: jedes Element validieren
    try:
        events = [SystemicTherapyEvent(**r) for r in raw_list]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"SystemicTherapyEvent Validation failed: {e}")

    return SystemicTherapyExtractResponse(events=events)
