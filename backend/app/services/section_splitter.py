"""
section_splitter.py – Teilt medizinische Dokumente in benannte Abschnitte auf
und ordnet jeden Abschnitt per Keyword-Matching einer Domain zu.

Wird von /llm/extract-multi genutzt damit jeder Extraktor nur die
für ihn relevanten Textabschnitte bekommt (token-effizient).
"""
import re
from typing import Dict, List, Optional

# Erkennt Anhang-/Anlage-Überschriften am Zeilenanfang
_APPENDIX_PATTERN = re.compile(
    r"(?im)^\s*(?:anhang|anh\.|anhänge|anlage(?:n)?|beilage(?:n)?)\s*(?:[:\d.\n]|$)"
)


def strip_appendix(text: str) -> str:
    """
    Schneidet alles ab dem ersten Anhang-/Anlage-Header ab.
    Gibt den unveränderten Text zurück wenn kein Anhang gefunden.
    """
    match = _APPENDIX_PATTERN.search(text)
    if match:
        return text[: match.start()].rstrip()
    return text


# Regex-Muster für Abschnittsüberschriften (case-insensitive, start of line)
_HEADER_PATTERN = re.compile(
    r"(?im)^"
    r"(?:"
    r"pathologi(?:e|sch)?|histologi(?:e|sch)?|biopsie"
    r"|radiologi(?:e|sch)?|bildgebung|kernspintomographie|magnetresonanztomographie"
    r"|(?:mrt|ct|pet)(?:-|\s|:)|röntgen"
    r"|strahlentherapie|radiotherapie|bestrahlungsplan|strahlenbehandlung"
    r"|tumorboard|sarkom.?board|tumorkonferenz|interdisziplinäre konferenz"
    r"|(?:operationsbericht|op-bericht|op bericht)|chirurgie|eingriff|resektion"
    r"|systemische\s+therapie|chemotherapie|immuntherapie|antikörpertherapie"
    r"|befund|beurteilung|zusammenfassung|anamnese|diagnose|therapie(?:verlauf|empfehlung)?"
    r")"
    r"[^\n]{0,80}$",
    re.IGNORECASE | re.MULTILINE,
)

# Keyword-Sets für Domain-Zuordnung je Abschnitt
_DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "radiology": [
        "mrt", "ct", "pet", "röntgen", "ultraschall", "sonographie",
        "bildgebung", "radiologi", "kernspintomographie", "magnetresonanztomographie",
        "befund", "beurteilung", "metastasen", "tumorausdehnung", "läsion",
    ],
    "radiotherapy": [
        "strahlentherapie", "radiotherapie", "bestrahlungsplan", "gy", "gray",
        "fraktion", "zielvolumen", "ptv", "gtv", "imrt", "vmat", "stereotaktisch",
        "strahlenbehandlung", "dosierung",
    ],
    "pathology": [
        "pathologi", "histologi", "biopsie", "mikroskopisch", "immunhistochemie",
        "ihc", "who-diagnose", "resektionsrand", "nekrose", "ki-67", "mitose",
        "färbung", "gewebe", "schnitt", "ngs", "fish", "rna",
    ],
    "surgery": [
        "operation", "op-bericht", "operationsbericht", "resektion", "eingriff",
        "operateur", "anästhesie", "schnittführung", "tumorprothese", "amputation",
        "chirurgie", "transartikulär", "axilla",
    ],
    "sarcoma_board": [
        "tumorboard", "sarkom-board", "sarkomboard", "tumorkonferenz",
        "board", "empfehlung", "diskussion", "konsensus", "interdisziplinär",
        "erstvorstellung", "wiedervorstellung",
    ],
    "systemic_therapy": [
        "chemotherapie", "immuntherapie", "systemische therapie", "therapielinie",
        "zyklus", "infusion", "mg/m", "protokoll", "euramos", "maid", "map",
        "antikörper", "pembrolizumab", "atezolizumab", "cabozantinib",
        "ifosfamid", "carboplatin", "etoposid", "lenvatinib",
    ],
}

ALL_DOMAINS = list(_DOMAIN_KEYWORDS.keys())


def _score_domain(text_lower: str, domain: str) -> int:
    """Zählt wie viele Keywords einer Domain im Text vorkommen."""
    return sum(1 for kw in _DOMAIN_KEYWORDS[domain] if kw in text_lower)


def _tag_section(content: str) -> Optional[str]:
    """Ordnet einen Textabschnitt der Domain mit dem höchsten Keyword-Score zu."""
    text_lower = content.lower()
    scores = {domain: _score_domain(text_lower, domain) for domain in ALL_DOMAINS}
    best_domain = max(scores, key=lambda d: scores[d])
    return best_domain if scores[best_domain] > 0 else None


def split_into_sections(text: str, max_chunk_chars: int = 10_000) -> List[Dict]:
    """
    Teilt Text an medizinischen Überschriften auf.
    Jeder Abschnitt erhält ein Keyword-basiertes Domain-Tag.

    Returns:
        [{"header": str, "content": str, "domain": str | None}, ...]
    Falls keine Überschriften erkannt: ein Abschnitt mit gesamtem Text.
    """
    matches = list(_HEADER_PATTERN.finditer(text))

    if not matches:
        content = text[:max_chunk_chars]
        return [{"header": "full_document", "content": content, "domain": _tag_section(content)}]

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end][:max_chunk_chars]
        sections.append({
            "header": match.group().strip(),
            "content": content,
            "domain": _tag_section(content),
        })
    return sections


def get_text_for_domain(sections: List[Dict], domain: str) -> str:
    """
    Gibt den vollständigen Text aller Abschnitte zurück.
    Domain-Kontext wird über [DOKUMENTTYP: <domain>] im Chunk-Prompt übermittelt,
    Keyword-Filtering ist daher redundant und würde relevanten Inhalt verwerfen.
    """
    return "\n\n".join(s["content"] for s in sections if s.get("content"))


def split_domain_text_into_chunks(text: str, chunk_size: int = 3500, overlap: int = 300) -> List[str]:
    """
    Teilt einen langen Domänentext in überlappende Chunks für separate LLM-Calls.

    Schneidet an Zeilenenden um Sätze nicht mittendrin zu trennen.
    Gibt [text] zurück wenn text <= chunk_size (kein Chunking nötig).
    """
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # An Zeilenende snappen statt mitten im Satz schneiden
            newline_pos = text.rfind("\n", start, end)
            if newline_pos > start + overlap:
                end = newline_pos + 1
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap  # Überlappung zurücksetzen
    return chunks
