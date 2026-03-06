import logging
from typing import Optional, List, Any, Dict, Type, TypeVar, Callable

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
    classify_and_extract_from_text,
    extract_befund_section,
    build_classification_text,
)
from app.services.constraint_mapper import normalize_raw_events, normalize_raw_events_with_meta

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
    max_chars: Optional[int] = None


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


class ParseIssue(BaseModel):
    event_index: int
    field: Optional[str] = None
    raw_value: Any = None
    error: str


def _parse_events_tolerant(
    raw_list: List[Dict[str, Any]], model_cls: Type[T]
) -> tuple[List[T], List[Dict[str, Any]], List[ParseIssue]]:
    """Parse events while preserving original payload and parse errors.

    Returns:
    - parsed events (schema-conform)
    - raw events (original dicts, unchanged)
    - parse issues (which values could not be mapped/validated)
    """
    events: List[T] = []
    raw_events: List[Dict[str, Any]] = []
    issues: List[ParseIssue] = []

    for idx, raw in enumerate(raw_list):
        if not isinstance(raw, dict):
            issues.append(
                ParseIssue(
                    event_index=idx,
                    field=None,
                    raw_value=raw,
                    error="Event ist kein JSON-Objekt und wurde ignoriert.",
                )
            )
            continue

        raw_events.append(dict(raw))

        try:
            events.append(model_cls(**raw))
            continue
        except ValidationError as exc:
            cleaned = dict(raw)
            for err in exc.errors():
                field = err["loc"][0] if err.get("loc") else None
                if isinstance(field, str) and field in cleaned:
                    issues.append(
                        ParseIssue(
                            event_index=idx,
                            field=field,
                            raw_value=raw.get(field),
                            error=err.get("msg", "Validierungsfehler"),
                        )
                    )
                    cleaned[field] = None
            try:
                events.append(model_cls(**cleaned))
            except Exception as second_exc:
                issues.append(
                    ParseIssue(
                        event_index=idx,
                        field=None,
                        raw_value=raw,
                        error=f"Event trotz Bereinigung ungueltig: {second_exc}",
                    )
                )
                logger.warning("Event komplett uebersprungen: %s", second_exc)
        except Exception as exc:
            issues.append(
                ParseIssue(
                    event_index=idx,
                    field=None,
                    raw_value=raw,
                    error=f"Unerwarteter Parse-Fehler: {exc}",
                )
            )
            logger.warning("Unerwarteter Parse-Fehler: %s", exc)

    return events, raw_events, issues


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
    raw_events: List[Dict[str, Any]] = []
    parse_issues: List[ParseIssue] = []


@router.post("/llm/extract-radiology", response_model=RadiologyExtractResponse)
async def llm_extract_radiology(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_radiology_events_from_text(raw_text)
    except Exception:
        logger.exception("Radiology-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Radiology-Extraktion.")

    raw_list = normalize_raw_events(raw_list, "radiology_exam")
    events, raw_events, parse_issues = _parse_events_tolerant(raw_list, RadiologyEvent)
    return RadiologyExtractResponse(events=events, raw_events=raw_events, parse_issues=parse_issues)


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
    raw_events: List[Dict[str, Any]] = []
    parse_issues: List[ParseIssue] = []


@router.post("/llm/extract-radiotherapy", response_model=RadiotherapyExtractResponse)
async def llm_extract_radiotherapy(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_radiotherapy_events_from_text(raw_text)
    except Exception:
        logger.exception("Radiotherapy-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Radiotherapy-Extraktion.")

    raw_list = normalize_raw_events(raw_list, "radio_therapy")
    events, raw_events, parse_issues = _parse_events_tolerant(raw_list, RadiotherapyEvent)
    return RadiotherapyExtractResponse(events=events, raw_events=raw_events, parse_issues=parse_issues)


# --- Pathology ---

class PathologyExtractResponse(BaseModel):
    events: List[PathologyEvent]
    raw_events: List[Dict[str, Any]] = []
    parse_issues: List[ParseIssue] = []


@router.post("/llm/extract-pathology", response_model=PathologyExtractResponse)
async def llm_extract_pathology(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_pathology_events_from_text(raw_text)
    except Exception:
        logger.exception("Pathology-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Pathology-Extraktion.")

    raw_list = normalize_raw_events(raw_list, "pathology")
    events, raw_events, parse_issues = _parse_events_tolerant(raw_list, PathologyEvent)
    return PathologyExtractResponse(events=events, raw_events=raw_events, parse_issues=parse_issues)


# --- Surgery ---

class SurgeryExtractResponse(BaseModel):
    events: List[SurgeryEvent]
    raw_events: List[Dict[str, Any]] = []
    parse_issues: List[ParseIssue] = []


@router.post("/llm/extract-surgery", response_model=SurgeryExtractResponse)
async def llm_extract_surgery(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_surgery_events_from_text(raw_text)
    except Exception:
        logger.exception("Surgery-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Surgery-Extraktion.")

    raw_list = normalize_raw_events(raw_list, "surgery")
    events, raw_events, parse_issues = _parse_events_tolerant(raw_list, SurgeryEvent)
    return SurgeryExtractResponse(events=events, raw_events=raw_events, parse_issues=parse_issues)


# --- Sarcoma Board ---

class SarcomaBoardExtractResponse(BaseModel):
    events: List[SarcomaBoardEvent]
    raw_events: List[Dict[str, Any]] = []
    parse_issues: List[ParseIssue] = []


@router.post("/llm/extract-sarcoma-board", response_model=SarcomaBoardExtractResponse)
async def llm_extract_sarcoma_board(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_sarcoma_board_events_from_text(raw_text)
    except Exception:
        logger.exception("Sarcoma Board-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Sarcoma Board-Extraktion.")

    raw_list = normalize_raw_events(raw_list, "sarcoma_board")
    events, raw_events, parse_issues = _parse_events_tolerant(raw_list, SarcomaBoardEvent)
    return SarcomaBoardExtractResponse(events=events, raw_events=raw_events, parse_issues=parse_issues)


# --- Systemic Therapy ---

class SystemicTherapyExtractResponse(BaseModel):
    events: List[SystemicTherapyEvent]
    raw_events: List[Dict[str, Any]] = []
    parse_issues: List[ParseIssue] = []


@router.post("/llm/extract-systemic-therapy", response_model=SystemicTherapyExtractResponse)
async def llm_extract_systemic_therapy(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        raw_list = extract_systemic_therapy_events_from_text(raw_text)
    except Exception:
        logger.exception("Systemic Therapy-Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Systemic Therapy-Extraktion.")

    raw_list = normalize_raw_events(raw_list, "systemic_therapy")
    events, raw_events, parse_issues = _parse_events_tolerant(raw_list, SystemicTherapyEvent)
    return SystemicTherapyExtractResponse(events=events, raw_events=raw_events, parse_issues=parse_issues)


# --- Combined Classify + Extract ---

class ClassifyAndExtractResponse(BaseModel):
    doc_type: str
    events: List[Dict[str, Any]]
    raw_events: List[Dict[str, Any]] = []
    parse_issues: List[ParseIssue] = []


def _topic_and_model_for_doc_type(doc_type: str) -> tuple[Optional[str], Optional[Type[BaseModel]]]:
    mapping: Dict[str, tuple[str, Type[BaseModel]]] = {
        "radiology": ("radiology_exam", RadiologyEvent),
        "radiotherapy": ("radio_therapy", RadiotherapyEvent),
        "pathology": ("pathology", PathologyEvent),
        "surgery": ("surgery", SurgeryEvent),
        "sarcoma_board": ("sarcoma_board", SarcomaBoardEvent),
        "systemic_therapy": ("systemic_therapy", SystemicTherapyEvent),
    }
    return mapping.get(doc_type, (None, None))


def _extractor_for_doc_type(doc_type: str) -> Callable[[str], List[Dict[str, Any]]]:
    extractor_map: Dict[str, Callable[[str], List[Dict[str, Any]]]] = {
        "radiology": extract_radiology_events_from_text,
        "radiotherapy": extract_radiotherapy_events_from_text,
        "pathology": extract_pathology_events_from_text,
        "surgery": extract_surgery_events_from_text,
        "sarcoma_board": extract_sarcoma_board_events_from_text,
        "systemic_therapy": extract_systemic_therapy_events_from_text,
    }
    return extractor_map.get(doc_type, extract_radiology_events_from_text)


def _event_score(items: List[Dict[str, Any]]) -> int:
    score = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        score += sum(1 for v in it.values() if v not in (None, "", [], {}))
    return score


@router.post("/llm/classify-and-extract", response_model=ClassifyAndExtractResponse)
async def llm_classify_and_extract(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)

    try:
        result = classify_and_extract_from_text(raw_text)
    except Exception:
        logger.exception("Classify-and-Extract fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Classify-and-Extract.")

    doc_type = result["doc_type"]
    raw_list = result["events"] if isinstance(result.get("events"), list) else []

    topic, model_cls = _topic_and_model_for_doc_type(doc_type)
    if topic and model_cls:
        raw_list = normalize_raw_events(raw_list, topic)
        parsed_events, raw_events, parse_issues = _parse_events_tolerant(raw_list, model_cls)
        events_payload = [evt.model_dump() for evt in parsed_events]
        return ClassifyAndExtractResponse(
            doc_type=doc_type,
            events=events_payload,
            raw_events=raw_events,
            parse_issues=parse_issues,
        )

    # Unknown doc_type fallback: keep extractor output as-is.
    return ClassifyAndExtractResponse(doc_type=doc_type, events=raw_list, raw_events=raw_list, parse_issues=[])


class ClassifyAndExtractDebugResponse(BaseModel):
    doc_type_initial: str
    doc_type_final: str
    raw_text: str
    classify_input_text: str
    extract_input_text: str
    llm_raw_events_initial: List[Dict[str, Any]]
    llm_raw_events_final: List[Dict[str, Any]]
    normalized_events: List[Dict[str, Any]]
    mapped_events: List[Dict[str, Any]]
    parse_issues: List[ParseIssue]
    mapping_debug: Dict[str, Any]
    fallback_debug: Dict[str, Any]


@router.post("/llm/classify-and-extract-debug", response_model=ClassifyAndExtractDebugResponse)
async def llm_classify_and_extract_debug(payload: _DocOrTextRequest):
    raw_text = _resolve_text(payload)
    classify_input_text = build_classification_text(raw_text)
    extract_input_text = extract_befund_section(raw_text)

    try:
        doc_type_initial = classify_document_type(raw_text)
    except Exception:
        logger.exception("Debug: Dokumenten-Klassifikation fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei Dokumenten-Klassifikation.")

    # Run classified extractor first, then fallback exactly as in classify_and_extract_from_text.
    extractor = _extractor_for_doc_type(doc_type_initial)
    try:
        initial_events = extractor(raw_text)
    except Exception:
        logger.exception("Debug: Initiale Extraktion fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei initialer Extraktion.")

    doc_type_final = doc_type_initial
    final_events = initial_events
    fallback_candidates: Dict[str, Dict[str, Any]] = {}

    if not final_events:
        best_type = doc_type_initial
        best_events = final_events
        best_score = _event_score(final_events)

        for t in ("radiology", "radiotherapy", "pathology", "surgery", "sarcoma_board", "systemic_therapy"):
            if t == doc_type_initial:
                continue
            try:
                candidate = _extractor_for_doc_type(t)(raw_text)
            except Exception as exc:
                fallback_candidates[t] = {"error": str(exc), "score": 0, "events_count": 0}
                continue
            candidate_score = _event_score(candidate)
            fallback_candidates[t] = {
                "score": candidate_score,
                "events_count": len(candidate),
            }
            if candidate_score > best_score:
                best_type = t
                best_events = candidate
                best_score = candidate_score

        doc_type_final = best_type
        final_events = best_events

    topic, model_cls = _topic_and_model_for_doc_type(doc_type_final)
    if topic and model_cls:
        normalized_events, mapping_meta = normalize_raw_events_with_meta(final_events, topic)
        parsed_events, raw_events, parse_issues = _parse_events_tolerant(normalized_events, model_cls)
        mapped_events = [evt.model_dump() for evt in parsed_events]
    else:
        normalized_events = final_events
        mapping_meta = {"topic": None, "mismatches": [], "corrections": {}, "before": final_events, "after": final_events}
        raw_events = final_events
        parse_issues = []
        mapped_events = final_events

    return ClassifyAndExtractDebugResponse(
        doc_type_initial=doc_type_initial,
        doc_type_final=doc_type_final,
        raw_text=raw_text,
        classify_input_text=classify_input_text,
        extract_input_text=extract_input_text,
        llm_raw_events_initial=initial_events,
        llm_raw_events_final=final_events,
        normalized_events=normalized_events,
        mapped_events=mapped_events,
        parse_issues=parse_issues,
        mapping_debug=mapping_meta,
        fallback_debug={
            "used_fallback": doc_type_final != doc_type_initial,
            "candidates": fallback_candidates,
        },
    )
