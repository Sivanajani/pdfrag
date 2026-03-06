"""
Locale- und Constraint-Loader für die Prompt-Anreicherung.

Lädt croms.enums.en.yml (Lesbare Labels pro Code) und die Constraint-YAMLs
(erlaubte DB-Codes pro Feld) und stellt daraus fertig formatierte Prompt-Zeilen
bereit — z.B. für build_enum_prompt_line("systemic_therapy", "reason"):

    "curative_intent_neoadjuvant" (Curative Intent: Neoadjuvant)
  | "curative_intent_adjuvant" (Curative Intent: Adjuvant)
  | ...
  | null
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import yaml

def _find_db_dir() -> Optional[Path]:
    """Search upward from this file for a db/ dir containing locales/ and constraints/."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "db"
        if candidate.is_dir() and (candidate / "locales").is_dir():
            return candidate
    return None


_DB_DIR = _find_db_dir()
_LOCALE_DIR = _DB_DIR / "locales" if _DB_DIR else None
_CONSTRAINT_DIR = _DB_DIR / "constraints" if _DB_DIR else None


# ---------------------------------------------------------------------------
# Locale label loader
# ---------------------------------------------------------------------------

def _flatten_yaml(node, result: Dict[str, str]) -> None:
    """Recursively walk a YAML dict and collect all leaf {str_key: str_value} pairs."""
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str):
                result[str(key)] = value
            else:
                _flatten_yaml(value, result)
    elif isinstance(node, list):
        for item in node:
            _flatten_yaml(item, result)


@lru_cache(maxsize=1)
def load_enum_labels() -> Dict[str, str]:
    """Return a flat {code: label} dict from croms.enums.en.yml."""
    if _LOCALE_DIR is None:
        return {}
    path = _LOCALE_DIR / "croms.enums.en.yml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    result: Dict[str, str] = {}
    _flatten_yaml(data, result)
    # Filter out label_* group-header keys (they're not DB codes)
    return {k: v for k, v in result.items() if not k.startswith("label_")}


# ---------------------------------------------------------------------------
# Constraint code loader
# ---------------------------------------------------------------------------

def _extract_codes(node) -> List[str]:
    """Extract leaf string codes from any constraint YAML format.

    Handles three formats:
      Format 1 — flat list:       ["code1", "code2", ...]
      Format 2 — label/children:  [{label: "...", children: ["code1", ...]}, ...]
      Format 3 — dict:            {category: ["code1", "code2"], ...}
    """
    codes: List[str] = []
    if isinstance(node, list):
        for item in node:
            if isinstance(item, str):
                codes.append(item)
            elif isinstance(item, dict):
                # Format 2: {label: ..., children: [...]}
                children = item.get("children") or []
                codes.extend(_extract_codes(children))
    elif isinstance(node, dict):
        # Format 3
        for value in node.values():
            codes.extend(_extract_codes(value))
    return codes


def _load_yaml_codes(path: Path) -> List[str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return _extract_codes(data)
    except Exception:
        return []


@lru_cache(maxsize=None)
def load_constraint_codes(topic: str, field: str) -> List[str]:
    """Return allowed DB codes for a field, searching constraint dirs in priority order.

    Priority:
      1. db/constraints/<topic>/<field>.yml
      2. db/constraints/<topic>/<field_stem_without_last_word>.yml
      3. db/constraints/<field>.yml
      4. db/constraints/<field_stem_without_last_word>.yml
    """
    # Derive stem (e.g. "drug_type" → "drug")
    parts = field.rsplit("_", 1)
    field_stem = parts[0] if len(parts) > 1 else field

    candidates = [
        _CONSTRAINT_DIR / topic / f"{field}.yml",
        _CONSTRAINT_DIR / topic / f"{field_stem}.yml",
        _CONSTRAINT_DIR / f"{field}.yml",
        _CONSTRAINT_DIR / f"{field_stem}.yml",
    ]
    for path in candidates:
        if path.exists():
            codes = _load_yaml_codes(path)
            if codes:
                return codes
    return []


# ---------------------------------------------------------------------------
# Prompt line builder
# ---------------------------------------------------------------------------

def build_enum_prompt_line(
    topic: str,
    field: str,
    *,
    max_codes: Optional[int] = None,
    include_null: bool = True,
) -> str:
    """Build a formatted 'code (label) | ...' string for embedding in LLM prompts.

    Args:
        topic:        Constraint sub-directory, e.g. "systemic_therapy", "drug", "adverse_event"
        field:        Field name, e.g. "reason", "drug_type"
        max_codes:    Optionally truncate to the N most important codes (use for very long lists)
        include_null: Append '| null' at the end (default True)

    Returns empty string if no codes found.
    """
    codes = load_constraint_codes(topic, field)
    if not codes:
        return ""

    labels = load_enum_labels()
    if max_codes:
        codes = codes[:max_codes]

    parts = []
    for code in codes:
        label = labels.get(code)
        if label and label.strip() and label.strip() != code:
            parts.append(f'"{code}" ({label})')
        else:
            parts.append(f'"{code}"')

    separator = "\n      | "
    result = separator.join(parts)
    if include_null:
        result += "\n      | null"
    return result


def build_constraint_guide(specs: List[tuple]) -> str:
    """Build a labelled constraint-guide block to prepend to LLM extraction prompts.

    Args:
        specs: list of (display_label, topic, field) tuples, e.g.:
               [("reason", "systemic_therapy", "reason"), ...]

    Returns a formatted string like::

        CONSTRAINT-GUIDE
        ────────────────
        reason:
          "curative_intent_neoadjuvant" (Curative Intent: Neoadjuvant)
          | "palliative" (Palliative)
          | null

        discontinuation_reason:
          ...

    Returns an empty string if no constraints are found.
    """
    sections: List[str] = []
    for label, topic, field in specs:
        line = build_enum_prompt_line(topic, field)
        if line:
            sections.append(f"{label}:\n  {line}")
    if not sections:
        return ""
    body = "\n\n".join(sections)
    return (
        "CONSTRAINT-GUIDE — erlaubte DB-Codes mit Bedeutungen "
        "(gilt für alle Sprachen: immer den DB-Code zurückgeben):\n"
        "────────────────────────────────────────────────────────\n"
        + body
        + "\n────────────────────────────────────────────────────────"
    )
    if _CONSTRAINT_DIR is None:
        return []
