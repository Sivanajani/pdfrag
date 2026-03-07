import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Any, Dict, Type, TypeVar

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError, Field

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
    classify_document_types_multi,
)
from app.services.constraint_mapper import normalize_raw_events
from app.services.section_splitter import split_into_sections, get_text_for_domain

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


# --- Multi-Domain Extraction ---

# Mapping: domain → (constraint_topic, extractor_fn, pydantic_model)
_DOMAIN_CONFIG: Dict[str, tuple] = {
    "radiology":        ("radiology_exam",   extract_radiology_events_from_text,        RadiologyEvent),
    "radiotherapy":     ("radio_therapy",    extract_radiotherapy_events_from_text,     RadiotherapyEvent),
    "pathology":        ("pathology",        extract_pathology_events_from_text,        PathologyEvent),
    "surgery":          ("surgery",          extract_surgery_events_from_text,          SurgeryEvent),
    "sarcoma_board":    ("sarcoma_board",    extract_sarcoma_board_events_from_text,    SarcomaBoardEvent),
    "systemic_therapy": ("systemic_therapy", extract_systemic_therapy_events_from_text, SystemicTherapyEvent),
}


class DomainResult(BaseModel):
    events: List[Dict[str, Any]] = Field(default_factory=list)
    raw_events: List[Dict[str, Any]] = Field(default_factory=list)
    parse_issues: List[ParseIssue] = Field(default_factory=list)


class DomainMeta(BaseModel):
    input_chars: int = 0
    used_section_text: bool = False
    duration_ms: int = 0
    events_count: int = 0
    raw_events_count: int = 0
    parse_issues_count: int = 0
    error: Optional[str] = None


class MultiExtractMeta(BaseModel):
    classify_ms: int = 0
    split_ms: int = 0
    extract_ms: int = 0
    total_ms: int = 0
    domain_meta: Dict[str, DomainMeta] = Field(default_factory=dict)


class MultiExtractResponse(BaseModel):
    detected_types: List[str] = Field(default_factory=list)
    radiology: DomainResult = Field(default_factory=DomainResult)
    radiotherapy: DomainResult = Field(default_factory=DomainResult)
    pathology: DomainResult = Field(default_factory=DomainResult)
    surgery: DomainResult = Field(default_factory=DomainResult)
    sarcoma_board: DomainResult = Field(default_factory=DomainResult)
    systemic_therapy: DomainResult = Field(default_factory=DomainResult)
    meta: MultiExtractMeta = Field(default_factory=MultiExtractMeta)


def _extract_multi_domain_result(domain: str, raw_text: str, sections: List[Dict[str, Any]]) -> tuple[str, DomainResult, DomainMeta]:
    started = time.perf_counter()
    topic, extractor_fn, model_cls = _DOMAIN_CONFIG[domain]

    # Prefer domain sections; fallback to capped fulltext to reduce tokens for mixed/long reports.
    section_text = get_text_for_domain(sections, domain)
    used_section_text = bool(section_text)
    domain_text = section_text or raw_text[:12_000]

    try:
        raw_list = extractor_fn(domain_text)
        raw_list = normalize_raw_events(raw_list, topic)
        events, raw_events, parse_issues = _parse_events_tolerant(raw_list, model_cls)
        result = DomainResult(
            events=[e.model_dump() for e in events],
            raw_events=raw_events,
            parse_issues=parse_issues,
        )
        err = None
    except Exception as exc:
        logger.exception("Extraktion fehlgeschlagen für Domain '%s'", domain)
        result = DomainResult()
        err = str(exc)

    duration_ms = int((time.perf_counter() - started) * 1000)
    meta = DomainMeta(
        input_chars=len(domain_text),
        used_section_text=used_section_text,
        duration_ms=duration_ms,
        events_count=len(result.events),
        raw_events_count=len(result.raw_events),
        parse_issues_count=len(result.parse_issues),
        error=err,
    )
    return domain, result, meta


@router.post("/llm/extract-multi", response_model=MultiExtractResponse)
async def llm_extract_multi(payload: _DocOrTextRequest):
    """
    Erkennt automatisch welche Domains in einem Dokument vorkommen und extrahiert
    nur diese (token-effizient). Unterstützt Mischberichte mit mehreren Domains.

    Flow:
    1. Multi-Label-Klassifikation des Gesamttexts → detected_types (max 3)
    2. Dokument per Überschriften in Abschnitte teilen + Keyword-Tagging
    3. Pro erkannter Domain: nur zugehörige Abschnitte extrahieren
       (Fallback auf Volltext wenn keine passenden Abschnitte)
    4. Normalisierung + Pydantic-Validierung wie bei Einzel-Endpoints
    """
    total_started = time.perf_counter()
    raw_text = _resolve_text(payload)

    # 1. Multi-Label-Klassifikation (1 LLM-Call, max 3 Typen)
    classify_started = time.perf_counter()
    try:
        detected_types = classify_document_types_multi(raw_text, max_types=3)
    except Exception:
        logger.exception("Multi-Klassifikation fehlgeschlagen")
        detected_types = []
    classify_ms = int((time.perf_counter() - classify_started) * 1000)

    # Sicherheitsnetz: nur bekannte Domains, Fallback auf radiology
    detected_types = [d for d in detected_types if d in _DOMAIN_CONFIG]
    if not detected_types:
        logger.warning("Keine Domain erkannt – Fallback auf radiology")
        detected_types = ["radiology"]

    # 2. Dokument in Abschnitte splitten (Keyword-basiert, kein LLM)
    split_started = time.perf_counter()
    sections = split_into_sections(raw_text)
    split_ms = int((time.perf_counter() - split_started) * 1000)

    # 3. Pro erkannter Domain parallel extrahieren
    extract_started = time.perf_counter()
    domain_results: Dict[str, DomainResult] = {}
    domain_meta: Dict[str, DomainMeta] = {}
    max_workers = max(1, min(3, len(detected_types)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_extract_multi_domain_result, domain, raw_text, sections)
            for domain in detected_types
        ]
        for future in as_completed(futures):
            try:
                domain, result, meta = future.result()
            except Exception:
                logger.exception("Unerwarteter Fehler in Parallel-Extraktion")
                continue
            domain_results[domain] = result
            domain_meta[domain] = meta
    extract_ms = int((time.perf_counter() - extract_started) * 1000)
    total_ms = int((time.perf_counter() - total_started) * 1000)

    return MultiExtractResponse(
        detected_types=detected_types,
        meta=MultiExtractMeta(
            classify_ms=classify_ms,
            split_ms=split_ms,
            extract_ms=extract_ms,
            total_ms=total_ms,
            domain_meta=domain_meta,
        ),
        **domain_results,
    )
