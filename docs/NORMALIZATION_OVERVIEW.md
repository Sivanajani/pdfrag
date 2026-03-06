# Normalization Overview

Vollständige Dokumentation des Normalisierungs-Stacks für die PDF-Extraction-Pipeline.

---

## Architektur: 3-Lagen-Normalisierung

```
PDF-Text
    │
    ▼  Layer 0: Enriched Extraction Prompt (immer aktiv, +150-300 Token)
Gemini Flash  →  gibt DB-Codes direkt aus, weil Prompt "code (Label)" zeigt
    │
    ▼  Layer 1: Pydantic static dicts (immer aktiv, 0 Token)
model_validator in Schemas  →  fängt bekannte Synonyme / Varianten ab
    │
    ▼  Layer 2: Batch Normalization LLM call (nur bei Mismatches, +300 Token)
normalize_raw_events()  →  mappt restliche unbekannte Werte via Gemini
    │
    ▼
Saubere DB-Codes → Pydantic-Validierung → Response
```

**Token-Kosten:**
- Layer 0: +200 Token × jeder Request (Flash-Preise → irrelevant)
- Layer 2: +400 Token × ~15% der Requests (~60 Token amortisiert)
- **Gesamt: ~260 Token/Request zusätzlich**

---

## Layer 0: Enriched Extraction Prompts

### Datei: `backend/app/services/locale_loader.py` (NEU)

Lädt Constraint-YAMLs und Locale-Labels und baut daraus fertig formatierte Prompt-Zeilen.

**Kernfunktionen:**

```python
@lru_cache(maxsize=1)
def load_enum_labels() -> Dict[str, str]:
    """Flattens croms.enums.en.yml → {code: label}. Filtered label_* keys."""
    ...

@lru_cache(maxsize=None)
def load_constraint_codes(topic: str, field: str) -> List[str]:
    """Loads allowed codes. 4-level priority fallback:
      1. db/constraints/<topic>/<field>.yml
      2. db/constraints/<topic>/<field_stem>.yml
      3. db/constraints/<field>.yml
      4. db/constraints/<field_stem>.yml
    """
    ...

def build_constraint_guide(specs: List[tuple]) -> str:
    """Builds a CONSTRAINT-GUIDE block to prepend to LLM prompts.

    specs = [("display_label", "topic", "field"), ...]

    Output example:
        CONSTRAINT-GUIDE — erlaubte DB-Codes mit Bedeutungen
        ────────────────────────────────────────────────────
        reason:
          "curative_intent_neoadjuvant" (Curative Intent: Neoadjuvant)
          | "curative_intent_adjuvant" (Curative Intent: Adjuvant)
          | "palliative" (Palliative)
          | null
        ...
    """
```

**Path-Suche (Docker-kompatibel):**
```python
def _find_db_dir() -> Path:
    """Sucht von der Datei aufwärts nach db/-Dir. Funktioniert auf Host und in Docker."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "db"
        if candidate.is_dir() and (candidate / "locales").is_dir():
            return candidate
    raise RuntimeError("db/ directory not found — add ./db:/app/db:ro volume mount")
```

**Docker-Setup:** `docker-compose.local.yml` hat `volumes: - ./db:/app/db:ro` (ro = read-only).

### Constraint-YAML-Formate (alle 3 werden unterstützt)

```yaml
# Format 1 — flat list
- curative_intent_neoadjuvant
- curative_intent_adjuvant
- palliative

# Format 2 — label/children
- label: "Bone Protocols"
  children:
    - map
    - mapie
    - vai

# Format 3 — dict
some_category:
  - code_a
  - code_b
```

### Integration in gemini_client.py

Alle 6 Extraction-Funktionen bauen einen `constraint_guide` und hängen ihn vor den Prompt:

```python
# Beispiel: Systemic Therapy
constraint_guide = build_constraint_guide([
    ("reason",                   "systemic_therapy", "reason"),
    ("bone_protocol",            "systemic_therapy", "bone_protocol"),
    ("softtissue_protocol",      "systemic_therapy", "softtissue_protocol"),
    ("drug_type",                "drug",             "drug_type"),
    ("dose_unit",                "drug",             "dose_unit"),
    ("route",                    "drug",             "route"),
    ("medical_area (CTCAE)",     "adverse_event",    "ctcae"),
    # ...
])
prompt = f"{system_instructions}\n\n{constraint_guide}\n\nJSON-Spezifikation:\n{json_spec}\n\n{text}"
```

| Domain | Felder im Constraint-Guide |
|--------|---------------------------|
| systemic_therapy | reason, bone/softtissue_protocol, cycles_executed, hyperthermia_status, clinical_trial_inclusion, discontinuation_reason, patient_type, drug_type, dose_unit, frequency_unit, route, administration_day, medical_area, grade |
| radiology_exam | exam_type, imaging_timing, recist_response, choi_response, irecist_response, local_disease_status, metastasis |
| radio_therapy | indication_type, therapy_type, hyperthermia_status |
| pathology | biopsy_type, biopsied_lesion_type, eortc_response_grade, diagnostic_grading |
| surgery | indication, surgery_side, resection, reconstruction, amputation, hemipelvectomy |
| sarcoma_board | reason_for_presentation, decision_surgery, follow_up_reason |

---

## Layer 1: Pydantic Static Normalizer

### Refactoring systemic_therapies.py (1054 → ~540 Zeilen)

**Vorher:** 16 Inline-Dicts, inkonsistente `replace()`-Ketten, gleicher `model_validator`-Boilerplate 3×.

**Nachher:** Einheitliche Architektur mit Basisklasse:

**`_lookup()` Funktion:**
```python
def _lookup(mapping: Dict[str, str], value) -> Optional[str]:
    """Erst raw lowercase, dann compact (spaces/hyphens → _)."""
    if not isinstance(value, str) or not value.strip():
        return None
    s = value.strip().lower()
    return mapping.get(s) or mapping.get(s.replace(" ", "_").replace("-", "_"))
```

**`_NormalizingModel` Basisklasse:**
```python
class _NormalizingModel(BaseModel):
    _NORMALIZERS: ClassVar[Dict[str, Dict[str, str]]] = {}

    @model_validator(mode="before")
    @classmethod
    def _normalize_fields(cls, data):
        if not isinstance(data, dict):
            return data
        for field, mapping in cls._NORMALIZERS.items():
            raw = data.get(field)
            normalized = _lookup(mapping, raw)
            if normalized is not None:
                data[field] = normalized
            elif raw is None or (isinstance(raw, str) and not raw.strip()):
                data[field] = None
            # else: raw bleibt erhalten — kein Datenverlust
        return data
```

**Klassen deklarieren nur noch `_NORMALIZERS`:**
```python
class Drug(_NormalizingModel):
    _NORMALIZERS = {
        "drug_type":        _DRUG_TYPE,
        "dose_unit":        _DOSE_UNIT,
        "frequency_unit":   _FREQUENCY_UNIT,
        "route":            _ROUTE,
        "administration_day": _ADMINISTRATION_DAY,
    }

class AdverseEvent(_NormalizingModel):
    _NORMALIZERS = {"medical_area": _MEDICAL_AREA, "event_type": _EVENT_TYPE, "grade": _GRADE}

class SystemicTherapyEvent(_NormalizingModel):
    _NORMALIZERS = {"reason": _REASON, "bone_protocol": _BONE_PROTOCOL, ...}
```

### CTCAE-Event-Codes: dynamisches Laden

`event_type` nutzt eine hybrid aufgebaute Lookup-Table (selbst-aktualisierend):

```python
@lru_cache(maxsize=1)
def _load_ctcae_event_codes() -> List[str]:
    """Lädt alle CTCAE-Leaf-Codes aus db/constraints/adverse_event/ctcae.yml."""
    ...

def _build_event_type_lookup() -> Dict[str, str]:
    for code in _load_ctcae_event_codes():
        mapping[code] = code                          # pass-through
        mapping[code.replace("_", " ")] = code       # space-Variante
        mapping[code.replace("_", "-")] = code       # hyphen-Variante
    mapping.update(_EVENT_TYPE_EXTRA)                 # manuelle DE/EN Aliases
    return mapping
```

Vorteil: Neue Codes in `ctcae.yml` → automatisch gültig ohne Code-Änderung.

### Normalisierungslogik (gilt für alle Domains)

```
LLM-Output (raw string)
        │
        ▼ _lookup(mapping, value)
        │
        ├─ Exakter Code-Match (lower/compact)  → DB-Code
        ├─ Synonym-Mapping (DE/EN, alte Formate) → DB-Code
        └─ Kein Match → raw (Originalwert, kein Datenverlust)
        │
        ▼
model_validator (pro Feld):
  if normalized → data[field] = normalized   (DB-Code)
  elif raw leer → data[field] = None
  else          → data[field] = raw          (raw_text Fallback)
```

### Domain-spezifische Besonderheiten

**surgery:**
- `indication`: komplett andere Codes (`first_surgery_for_this_reason` statt `definitive_surgery`)
- `surgery_side`: nur `right`, `left`, `midline` (kein `bilateral` im Constraint)
- `resection` + `participated_disciplines` + `hemipelvectomy`: Listen → per-item Normalizer
- `amputation`: Bug gefixt — `above-knee` → `resh_170`, `hemipelvectomy` → `resg_080`
- `hemipelvectomy`: LLM-Prompt enthält vollständige Code→Beschreibung-Tabelle; Normalizer akzeptiert alle Codes mit `e_`-Prefix direkt durch

**sarcoma_board:**
- `last_execution`: speichert Grund für **nicht** erneute Board-Vorstellung (nicht letzte Behandlung)
- `current_ecog`: parst Strings wie `"ECOG 2"`, `"PS 1"` → `int 0–5`
- Feldname: `decision_systemic_surgery` (nicht `decision_systemic_therapy`)

**systemic_therapy:**
- `patient_type`: `outpatient`/`inpatient` (nicht Altersgruppe wie alte Enums)
- `softtissue_protocol`: nur 4 Codes (cws, pazoqol, napage, other); MAP/AI/MAID → `other`
- `bone_protocol`: EURAMOS/EuroBOSS/Ewing → direkte Codes; MAP/MAPIE/VAI → `other`
- `cycles_executed`: DB-Codes sind Zahlwörter (one–nine, until_progression); Brüche → raw_text
- `hyperthermia_status`: nur 2 Codes (no, yes_chemotherapy_hyperthermia)
- `discontinuation_reason`: kein `other`-Code — unbekannte Werte → raw_text

---

## Layer 2: Batch Normalization

### Datei: `backend/app/services/constraint_mapper.py` (NEU)

Sitzt **zwischen** LLM-Extraction und Pydantic-Validierung. Sendet bei Mismatches einen einzelnen Gemini-Call für alle unbekannten Werte.

**Flow:**
```python
def normalize_raw_events(raw_list: List[Dict], topic: str) -> List[Dict]:
    mismatches = _collect_mismatches(raw_list, topic)   # Welche Felder stimmen nicht?
    if not mismatches:
        return raw_list                                  # 0 Token, keine Änderung

    corrections = _batch_llm_map(mismatches)             # EIN Gemini-Call
    if corrections:
        raw_list = _apply_corrections(raw_list, mismatches, corrections)
    return raw_list
```

**Mismatch-Sammlung:**
- Top-Level-Felder: prüft jeden Event gegen `_TOP_LEVEL_SPECS[topic]`
- Nested Arrays: prüft `drugs[]` und `adverse_events[]` via `_NESTED_SPECS`
- `_is_valid_code()`: case-insensitiver Vergleich gegen erlaubte Codes

**Batch-LLM-Prompt (~300 Token):**
```
You are a medical data normalization expert.
Map each value to the closest allowed DB code. If no code fits, return null.
Return ONLY valid JSON, no explanation.

- path "reason", value "palliativ" → allowed: ["palliative" | "curative_intent_neoadjuvant" | ...]
- path "drugs[0].drug_type", value "Taxol" → allowed: ["paclitaxel" | "docetaxel" | ...]

Return: {"path/to/field": "best_matching_code_or_null", ...}
```

**Correction-Anwendung:**
- Top-Level: `event[field] = corrected`
- Nested: `event[array_field][item_idx][field] = corrected`
- `null`-Korrekturen werden ignoriert (raw_text-Fallback bleibt)

**Feld-Definitionen per Topic:**

| Topic | Top-Level-Felder | Nested |
|-------|-----------------|--------|
| systemic_therapy | reason, bone/softtissue_protocol, cycles_executed, hyperthermia_status, clinical_trial_inclusion, discontinuation_reason, patient_type | drugs[].drug_type/dose_unit/frequency_unit/route/administration_day, adverse_events[].medical_area/grade |
| radiology_exam | exam_type, imaging_timing, imaging_type, location_of_lesion, recist/choi/irecist_response, local_disease_status, metastasis | — |
| radio_therapy | hyperthermia_status | — |
| pathology | biopsy_type, biopsied_lesion_type, eortc_response_grade, diagnostic_grading, prior_treatment, proliferation_index, extent_of_necrosis | — |
| surgery | indication, surgery_side | — |
| sarcoma_board | reason_for_presentation, follow_up_reason, decision_surgery, last_execution, status_before/after_follow_up, treatment_before_follow_up | — |

### Integration in llm.py

Alle 6 Extraction-Endpunkte rufen `normalize_raw_events()` vor `_parse_events_tolerant()` auf:

```python
from app.services.constraint_mapper import normalize_raw_events

# Radiology
raw_list = extract_radiology_exam_events_from_text(raw_text)
raw_list = normalize_raw_events(raw_list, "radiology_exam")
events, raw_events, parse_issues = _parse_events_tolerant(raw_list, RadiologyExamEvent)

# Radiotherapy
raw_list = extract_radiotherapy_events_from_text(raw_text)
raw_list = normalize_raw_events(raw_list, "radio_therapy")
events, raw_events, parse_issues = _parse_events_tolerant(raw_list, RadioTherapyEvent)

# Pathology
raw_list = extract_pathology_events_from_text(raw_text)
raw_list = normalize_raw_events(raw_list, "pathology")
events, raw_events, parse_issues = _parse_events_tolerant(raw_list, PathologyEvent)

# Surgery
raw_list = extract_surgery_events_from_text(raw_text)
raw_list = normalize_raw_events(raw_list, "surgery")
events, raw_events, parse_issues = _parse_events_tolerant(raw_list, SurgeryEvent)

# Sarcoma Board
raw_list = extract_sarcoma_board_events_from_text(raw_text)
raw_list = normalize_raw_events(raw_list, "sarcoma_board")
events, raw_events, parse_issues = _parse_events_tolerant(raw_list, SarcomaBoardEvent)

# Systemic Therapy
raw_list = extract_systemic_therapy_events_from_text(raw_text)
raw_list = normalize_raw_events(raw_list, "systemic_therapy")
events, raw_events, parse_issues = _parse_events_tolerant(raw_list, SystemicTherapyEvent)
```

---

## Gesamtübersicht geänderte Dateien

| Datei | Änderung | Status |
|-------|----------|--------|
| `backend/app/services/locale_loader.py` | NEU: lru_cache Loader + build_constraint_guide() | ✅ |
| `backend/app/services/constraint_mapper.py` | NEU: normalize_raw_events() (Layer 2) | ✅ |
| `backend/app/services/gemini_client.py` | Alle 6 Extraction-Prompts mit Constraint-Guide angereichert | ✅ |
| `backend/app/routers/llm.py` | normalize_raw_events() in alle 6 Endpunkte integriert | ✅ |
| `backend/app/schemas/systemic_therapies.py` | Refactoring 1054→540 Zeilen, _NormalizingModel Basisklasse | ✅ |
| `backend/app/schemas/surgeries.py` | DB-Constraint-Codes, Normalizer, per-item List-Normalizer | ✅ |
| `backend/app/schemas/systemic_therapies.py` | DB-Constraint-Codes, _NormalizingModel, CTCAE-Loader | ✅ |
| `backend/app/schemas/sarcoma_boards.py` | DB-Constraint-Codes, ECOG-Parser | ✅ |
| `backend/app/schemas/radioTherapy.py` | DB-Constraint-Codes, Normalizer | ✅ |
| `backend/app/schemas/radiology.py` | DB-Constraint-Codes, Normalizer | ✅ |
| `backend/app/schemas/pathologies.py` | DB-Constraint-Codes, Normalizer (Basis) | ✅ |
| `docker-compose.local.yml` | `./db:/app/db:ro` Volume-Mount hinzugefügt | ✅ |

---

## Constraint-Dateien

Quelle der Wahrheit für erlaubte Werte:

```
db/constraints/
├── pathology/          (biopsy_type, who_diagnosis, eortc_response_grade, ...)
├── radio_therapy/      (indications, therapy_types, hyperthermia_status)
├── radiology_exam/     (exam_type, imaging_timing, recist_response, metastasis, ...)
├── sarcoma_board/      (reason_for_presentation, decision_surgery, follow_up_reason, ...)
├── surgery/            (indication, surgery_side, resection, reconstruction, amputation,
│                        hemipelvectomy, participated_disciplines)
├── systemic_therapy/   (reason, bone_protocol, softtissue_protocol, ...)
├── drug/               (drug_type, dose_unit, frequency_unit, route, administration_day)
├── adverse_event/      (ctcae.yml — CTCAE-Kategorien und Leaf-Codes, grade.yml)
└── ecog.yml            (0–5, shared across domains)

db/locales/
└── croms.enums.en.yml  ({code: label} für alle Domains)
```

---

## Verifikation / Tests

```bash
# Layer 0 testen: Constraint-Guide Output
docker compose -f docker-compose.local.yml run --rm backend python -c "
from app.services.locale_loader import build_constraint_guide
print(build_constraint_guide([
    ('reason', 'systemic_therapy', 'reason'),
    ('drug_type', 'drug', 'drug_type'),
]))
"

# Layer 2 testen: Batch-Normalisierung
docker compose -f docker-compose.local.yml run --rm backend python -c "
from app.services.constraint_mapper import normalize_raw_events
result = normalize_raw_events([
    {'reason': 'palliativ', 'drugs': [{'drug_type': 'Taxol'}]}
], topic='systemic_therapy')
print(result)
# Erwartung: reason → 'palliative', drug_type → 'paclitaxel'
"

# End-to-end: POST /llm/extract-systemic-therapy mit realem Bericht
# Erwartung: parse_issues leer oder stark reduziert
```
