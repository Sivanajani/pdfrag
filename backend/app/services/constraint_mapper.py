"""
Batch-Normalisierung für LLM-Ausgaben, die nicht von den statischen
Schema-Dicts erkannt wurden.

Flow:
  raw_list (LLM output)
      │
      ▼  normalize_raw_events(raw_list, topic)
  Felder ohne gültigen DB-Code gesammelt
      │
      ├─ falls keine → raw_list unverändert (0 Token)
      │
      └─ falls vorhanden → EIN Gemini-Aufruf (~300 Token)
              → Korrekturen auf raw_list anwenden
              → korrigierte raw_list zurückgeben

Danach läuft _parse_events_tolerant() / Pydantic-Validierung.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai

from app.services.locale_loader import load_constraint_codes

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constraint-Feld-Definitionen pro Topic
# Tupel: (constraint_topic, constraint_field)
# Nur Top-Level-Felder; verschachtelte Felder (drugs[], adverse_events[])
# werden über _NESTED_SPECS separat definiert.
# ---------------------------------------------------------------------------

_TOP_LEVEL_SPECS: Dict[str, Dict[str, Tuple[str, str]]] = {
    "systemic_therapy": {
        "reason":                   ("systemic_therapy", "reason"),
        "bone_protocol":            ("systemic_therapy", "bone_protocol"),
        "softtissue_protocol":      ("systemic_therapy", "softtissue_protocol"),
        "cycles_executed":          ("systemic_therapy", "cycles_executed"),
        "hyperthermia_status":      ("systemic_therapy", "hyperthermia_status"),
        "clinical_trial_inclusion": ("systemic_therapy", "clinical_trial_inclusion"),
        "discontinuation_reason":   ("systemic_therapy", "discontinuation_reason"),
        "patient_type":             ("systemic_therapy", "patient_type"),
    },
    "radiology_exam": {
        "exam_type":            ("radiology_exam", "exam_type"),
        "imaging_timing":       ("radiology_exam", "imaging_timing"),
        "imaging_type":         ("radiology_exam", "imaging_type"),
        "location_of_lesion":   ("radiology_exam", "location_of_lesion"),
        "recist_response":      ("radiology_exam", "recist_response"),
        "choi_response":        ("radiology_exam", "choi_response"),
        "irecist_response":     ("radiology_exam", "irecist_response"),
        "local_disease_status": ("radiology_exam", "local_disease_status"),
        "metastasis":           ("radiology_exam", "metastasis"),
    },
    "radio_therapy": {
        "hyperthermia_status": ("radio_therapy", "hyperthermia_status"),
    },
    "pathology": {
        "biopsy_type":          ("pathology", "biopsy_type"),
        "biopsied_lesion_type": ("pathology", "biopsied_lesion_type"),
        "eortc_response_grade": ("pathology", "eortc_response_grade"),
        "diagnostic_grading":   ("pathology", "diagnostic_grading"),
        "prior_treatment":      ("pathology", "prior_treatment"),
        "proliferation_index":  ("pathology", "proliferation_index"),
        "extent_of_necrosis":   ("pathology", "extent_of_necrosis"),
    },
    "surgery": {
        "indication":   ("surgery", "indication"),
        "surgery_side": ("surgery", "surgery_side"),
    },
    "sarcoma_board": {
        "reason_for_presentation":   ("sarcoma_board", "reason_for_presentation"),
        "follow_up_reason":          ("sarcoma_board", "follow_up_reason"),
        "decision_surgery":          ("sarcoma_board", "decision_surgery"),
        "last_execution":            ("sarcoma_board", "last_execution"),
        "status_before_follow_up":   ("sarcoma_board", "status_before_follow_up"),
        "status_after_follow_up":    ("sarcoma_board", "status_after_follow_up"),
        "treatment_before_follow_up":("sarcoma_board", "treatment_before_follow_up"),
    },
}

# Nested array specs: topic → (array_field, sub_field → (c_topic, c_field))
_NESTED_SPECS: Dict[str, Dict[str, Dict[str, Tuple[str, str]]]] = {
    "systemic_therapy": {
        "drugs": {
            "drug_type":        ("drug", "drug_type"),
            "dose_unit":        ("drug", "dose_unit"),
            "frequency_unit":   ("drug", "frequency_unit"),
            "route":            ("drug", "route"),
            "administration_day": ("drug", "administration_day"),
        },
        "adverse_events": {
            "medical_area": ("adverse_event", "ctcae"),
            "grade":        ("adverse_event", "grade"),
        },
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_valid_code(value: Any, allowed: List[str]) -> bool:
    """Return True if value already is an allowed DB code (case-insensitive)."""
    if value is None:
        return True  # null is always valid
    v = str(value).strip().lower()
    if not v:
        return True
    allowed_lower = {c.lower() for c in allowed}
    return v in allowed_lower


def _collect_mismatches(
    raw_list: List[Dict[str, Any]],
    topic: str,
) -> List[Dict[str, Any]]:
    """Collect all field values that are not valid DB codes and need LLM remapping.

    Returns list of mismatch dicts:
      {"event_idx": int, "path": str, "field": str, "value": str, "allowed": List[str]}
    """
    mismatches = []
    top_specs = _TOP_LEVEL_SPECS.get(topic, {})
    nested_specs = _NESTED_SPECS.get(topic, {})

    for event_idx, event in enumerate(raw_list):
        if not isinstance(event, dict):
            continue

        # Top-level fields
        for field, (c_topic, c_field) in top_specs.items():
            value = event.get(field)
            if value is None:
                continue
            allowed = load_constraint_codes(c_topic, c_field)
            if not allowed:
                continue
            if not _is_valid_code(value, allowed):
                mismatches.append({
                    "event_idx": event_idx,
                    "path": field,
                    "field": field,
                    "value": str(value),
                    "allowed": allowed,
                })

        # Nested array fields
        for array_field, sub_specs in nested_specs.items():
            items = event.get(array_field) or []
            if not isinstance(items, list):
                continue
            for item_idx, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                for sub_field, (c_topic, c_field) in sub_specs.items():
                    value = item.get(sub_field)
                    if value is None:
                        continue
                    allowed = load_constraint_codes(c_topic, c_field)
                    if not allowed:
                        continue
                    if not _is_valid_code(value, allowed):
                        mismatches.append({
                            "event_idx": event_idx,
                            "path": f"{array_field}[{item_idx}].{sub_field}",
                            "array_field": array_field,
                            "item_idx": item_idx,
                            "field": sub_field,
                            "value": str(value),
                            "allowed": allowed,
                        })

    return mismatches


def _batch_llm_map(mismatches: List[Dict[str, Any]]) -> Dict[str, str]:
    """Send ONE LLM call to map all mismatched values to DB codes.

    Returns {path: corrected_code} or empty dict on failure.
    """
    lines = []
    for m in mismatches:
        # Limit displayed codes to keep prompt short (max 20 per field)
        codes_preview = m["allowed"][:20]
        codes_str = " | ".join(f'"{c}"' for c in codes_preview)
        if len(m["allowed"]) > 20:
            codes_str += " | ..."
        lines.append(
            f'- path "{m["path"]}", value "{m["value"]}" → allowed: [{codes_str}]'
        )

    prompt = (
        "You are a medical data normalization expert.\n"
        "Map each value to the closest allowed DB code. "
        "If no code fits, return null.\n"
        "Return ONLY valid JSON, no explanation.\n\n"
        + "\n".join(lines)
        + '\n\nReturn: {"path/to/field": "best_matching_code_or_null", ...}'
    )

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt)
        raw = (response.text or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json", "", 1).strip()
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Batch-Normalisierung fehlgeschlagen: %s", exc)
        return {}


def _apply_corrections(
    raw_list: List[Dict[str, Any]],
    mismatches: List[Dict[str, Any]],
    corrections: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Apply LLM corrections back to the raw event list."""
    for m in mismatches:
        corrected = corrections.get(m["path"])
        if corrected is None or corrected == "null":
            continue
        event = raw_list[m["event_idx"]]
        if "array_field" in m:
            items = event.get(m["array_field"]) or []
            if m["item_idx"] < len(items) and isinstance(items[m["item_idx"]], dict):
                items[m["item_idx"]][m["field"]] = corrected
        else:
            event[m["field"]] = corrected
    return raw_list


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize_raw_events(
    raw_list: List[Dict[str, Any]],
    topic: str,
) -> List[Dict[str, Any]]:
    """Pre-normalize raw LLM output before Pydantic schema validation.

    For values that are not valid DB codes (and not null), sends a single
    batch LLM call to map them.  Returns the (possibly corrected) raw_list.

    This runs BEFORE the schema model_validators, so both layers complement
    each other:
      - This layer catches truly unknown synonyms via LLM semantics
      - Schema model_validators catch the most common static synonyms (0 tokens)
    """
    mismatches = _collect_mismatches(raw_list, topic)
    if not mismatches:
        return raw_list

    logger.info(
        "Batch-Normalisierung: %d Felder aus %d Events für topic '%s'",
        len(mismatches), len(raw_list), topic,
    )
    corrections = _batch_llm_map(mismatches)
    if corrections:
        raw_list = _apply_corrections(raw_list, mismatches, corrections)

    return raw_list
