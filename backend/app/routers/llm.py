import logging
from typing import Optional, List, Any, Dict, Type, TypeVar

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from app.utils.paths import validate_doc_id
from app.services.pdf_service import read_pdf_text

T = TypeVar("T", bound=BaseModel)
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

logger = logging.getLogger(__name__)

router = APIRouter(tags=["llm"])


# --- Shared helpers ---

class _DocOrTextRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 20000


def _resolve_text(payload: _DocOrTextRequest) -> str:
    """Resolve text from doc_id or direct text field. Raises HTTPException on invalid input."""
    if not payload.doc_id and not payload.text:
        raise HTTPException(status_code=400, detail="Bitte entweder 'doc_id' oder 'text' angeben.")
    if payload.doc_id and payload.text:
        raise HTTPException(status_code=400, detail="Bitte entweder 'doc_id' ODER 'text' angeben, nicht beides.")

    if payload.doc_id:
        pdf_path = validate_doc_id(payload.doc_id)
        raw_text = read_pdf_text(pdf_path, max_chars=payload.max_chars)
    else:
        raw_text = payload.text[: payload.max_chars]

    if not raw_text:
        raise HTTPException(status_code=400, detail="Kein Text gefunden oder leer.")

    return raw_text


def _parse_events_tolerant(raw_list: List[Dict[str, Any]], model_cls: Type[T]) -> List[T]:
    """Parse a list of dicts into Pydantic models, tolerating invalid fields.

    For each dict: try strict parse first. If it fails, set every invalid
    field to None and retry. If that still fails, skip the event entirely.
    This ensures partial data is always returned instead of a 422 error.
    """
    events: List[T] = []
    for raw in raw_list:
        if not isinstance(raw, dict):
            continue
        try:
            events.append(model_cls(**raw))
        except (ValidationError, Exception) as exc:
            # Identify invalid fields from Pydantic error and null them out
            cleaned = dict(raw)
            if isinstance(exc, ValidationError):
                for err in exc.errors():
                    field = err["loc"][0] if err["loc"] else None
                    if field and field in cleaned:
                        cleaned[field] = None
            try:
                events.append(model_cls(**cleaned))
            except Exception:
                logger.warning("Event komplett uebersprungen: %s", exc)
    return events


# --- Generic extraction ---

class ExtractedItem(BaseModel):
    source_type: Optional[str] = None
    body_part: Optional[str] = None
    concept: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    note: Optional[str] = None


class LLMExtractResponse(BaseModel):
    items: List[ExtractedItem]


@router.post("/llm/extract", response_model=LLMExtractResponse)
async def llm_extract(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        items_raw: List[Dict[str, Any]] = extract_structured_data_from_text(raw_text)
    except Exception:
        logger.exception("LLM-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei LLM-Extraktion.")

    items = [ExtractedItem(**item) for item in items_raw]
    return LLMExtractResponse(items=items)


# --- Radiology ---

class RadiologyExtractResponse(BaseModel):
    events: List[RadiologyEvent]


@router.post("/llm/extract-radiology", response_model=RadiologyExtractResponse)
async def llm_extract_radiology(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_radiology_events_from_text(raw_text)
    except Exception:
        logger.exception("Radiology-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Radiology-Extraktion.")

    events = _parse_events_tolerant(raw_list, RadiologyEvent)
    return RadiologyExtractResponse(events=events)


# --- Classify doc type ---

class ClassifyDocTypeRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    max_chars: int = 5000


class ClassifyDocTypeResponse(BaseModel):
    doc_type: str


@router.post("/llm/classify-doc-type", response_model=ClassifyDocTypeResponse)
async def classify_doc_type(payload: ClassifyDocTypeRequest):
    # Reuse _resolve_text with a temporary _DocOrTextRequest
    req = _DocOrTextRequest(doc_id=payload.doc_id, text=payload.text, max_chars=payload.max_chars)
    raw_text = _resolve_text(req)

    try:
        doc_type = classify_document_type(raw_text)
    except Exception:
        logger.exception("Dokumenten-Klassifikation fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Dokumenten-Klassifikation.")

    return ClassifyDocTypeResponse(doc_type=doc_type)


# --- Radiotherapy ---

class RadiotherapyExtractResponse(BaseModel):
    events: List[RadiotherapyEvent]


@router.post("/llm/extract-radiotherapy", response_model=RadiotherapyExtractResponse)
async def llm_extract_radiotherapy(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_radiotherapy_events_from_text(raw_text)
    except Exception:
        logger.exception("Radiotherapy-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Radiotherapy-Extraktion.")

    events = _parse_events_tolerant(raw_list, RadiotherapyEvent)
    return RadiotherapyExtractResponse(events=events)


# --- Pathology ---

class PathologyExtractResponse(BaseModel):
    events: List[PathologyEvent]


@router.post("/llm/extract-pathology", response_model=PathologyExtractResponse)
async def llm_extract_pathology(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_pathology_events_from_text(raw_text)
    except Exception:
        logger.exception("Pathology-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Pathology-Extraktion.")

    events = _parse_events_tolerant(raw_list, PathologyEvent)
    return PathologyExtractResponse(events=events)


# --- Surgery ---

class SurgeryExtractResponse(BaseModel):
    events: List[SurgeryEvent]


@router.post("/llm/extract-surgery", response_model=SurgeryExtractResponse)
async def llm_extract_surgery(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_surgery_events_from_text(raw_text)
    except Exception:
        logger.exception("Surgery-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Surgery-Extraktion.")

    events = _parse_events_tolerant(raw_list, SurgeryEvent)
    return SurgeryExtractResponse(events=events)


# --- Sarcoma Board ---

class SarcomaBoardExtractResponse(BaseModel):
    events: List[SarcomaBoardEvent]


@router.post("/llm/extract-sarcoma-board", response_model=SarcomaBoardExtractResponse)
async def llm_extract_sarcoma_board(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_sarcoma_board_events_from_text(raw_text)
    except Exception:
        logger.exception("Sarcoma Board-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Sarcoma Board-Extraktion.")

    events = _parse_events_tolerant(raw_list, SarcomaBoardEvent)
    return SarcomaBoardExtractResponse(events=events)


# --- Systemic Therapy ---

class SystemicTherapyExtractResponse(BaseModel):
    events: List[SystemicTherapyEvent]


@router.post("/llm/extract-systemic-therapy", response_model=SystemicTherapyExtractResponse)
async def llm_extract_systemic_therapy(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_systemic_therapy_events_from_text(raw_text)
    except Exception:
        logger.exception("Systemic Therapy-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Systemic Therapy-Extraktion.")

    events = _parse_events_tolerant(raw_list, SystemicTherapyEvent)
    return SystemicTherapyExtractResponse(events=events)
