# Pathology Field Normalization – Progress

## Übersicht

Jedes Pathologie-Feld wird systematisch normalisiert:
**LLM-Output → `_normalize_*()` in `PathologyEvent` → DB-Constraint-Code**

Fallback-Logik (einheitlich für alle Felder):
- Wert vorhanden + mappbar → **gemappter Code** (Priorität)
- Wert vorhanden + nicht mappbar → **raw_text erhalten** (kein Datenverlust)
- Kein Wert / leer → **None** (Feld bleibt leer)

---

## Status je Feld

### ✅ Erledigt

| Feld | Constraint-Datei | Python-Klasse | Normalize-Methode | Gemini-Spec |
|---|---|---|---|---|
| `biopsy_type` | `biopsy_type.yml` (6 Werte) | `BiopsyType` enum | `_normalize_biopsy_type()` | ✅ |
| `biopsied_lesion_type` | `biopsied_lesion_type.yml` (6 Werte) | `BiopsiedLesionType` enum | `_normalize_biopsied_lesion_type()` | ✅ |
| `diagnostic_grading` | `diagnostic_grading.yml` (9 Werte) | `DiagnosticGrading` enum | `_normalize_diagnostic_grading()` | ✅ |
| `prior_treatment` | `prior_treatment.yml` (5 Werte) | `PriorTreatment` enum | `_normalize_prior_treatment()` | ✅ |
| `eortc_response_grade` | `eortc_response_grade.yml` (5 Werte) | `EORTCResponseGrade` enum | `_normalize_eortc_response_grade()` | ✅ |
| `mitoses_per_10hpf` | `mitoses_per_10hpf.yml` (4 Werte) | `MitosesPerHPF` enum | `_normalize_mitoses_per_10hpf()` | ✅ |
| `extent_of_necrosis` | `extent_of_necrosis.yml` (10 Werte) | `ExtentOfNecrosis` enum | `_normalize_extent_of_necrosis()` | ✅ |
| `biological_barrier_to_closest_margin` | `biological_barrier_to_closest_margin.yml` (8 Werte) | `BiologicalBarrier` enum | `_normalize_biological_barrier()` | ✅ |
| `proliferation_index` | `proliferation_index.yml` (11 Werte) | `ProliferationIndex` enum | `_normalize_proliferation_index()` | ✅ |
| `ihc_result` | `report_result.yml` (4 Werte) | `ReportResult` enum | `_normalize_report_result()` | ✅ |
| `fish_result` | `report_result.yml` (4 Werte) | `ReportResult` enum | `_normalize_report_result()` | ✅ |
| `rna_result` | `report_result.yml` (4 Werte) | `ReportResult` enum | `_normalize_report_result()` | ✅ |
| `dna_result` | `report_result.yml` (4 Werte) | `ReportResult` enum | `_normalize_report_result()` | ✅ |
| `who_diagnosis` | `who_diagnosis.yml` (~200 Werte, nested) | kein Enum (zu viele) | `_normalize_who_diagnosis()` | ✅ |

### ❌ Noch offen

| Feld | Constraint-Datei | Werte | Bemerkung |
|---|---|---|---|
| `report_status` (?) | `report_status.yml` | `yes`, `no`, `not_yet_but_planned` | Feld existiert noch nicht im Schema |

---

## Änderungen pro Datei

### `backend/app/schemas/pathologies.py`

**Neue Enums (diese Session):**
- `ProliferationIndex` — 11 Werte inkl. `not_applicable_because_of_therapy_before_biopsy_or_necrosis`
- `ReportResult` — 4 Werte: `positive`, `negative`, `not_interpretable`, `in_progress`

**Neue Normalize-Methoden (diese Session):**
- `_normalize_proliferation_index()` — extrahiert Prozentzahl aus "Ki-67: 40%"-Format, mappt auf Range
- `_normalize_report_result()` — mappt positiv/negativ/nicht interpretierbar auf 4 Codes (DE + EN Synonyme)
- `_normalize_who_diagnosis()` — YAML-basiert: exakter Code → compact → Locale-Label → raw_text

**Neuer Modul-Level-Loader:**
- `_load_who_diagnosis_data()` — `@lru_cache`, lädt `who_diagnosis.yml` + `croms.enums.en.yml` einmalig

**Neue Imports:**
- `functools`, `pathlib`, `yaml`

**Feld-Anpassungen:**
- `proliferation_index.max_length`: 50 → 200 (längster Code = 60 Zeichen)

**Hooks in `normalize_pathology_fields`:**
- `proliferation_index` ✅
- `ihc_result`, `fish_result`, `rna_result`, `dna_result` (Loop) ✅
- `who_diagnosis` ✅

---

### `backend/app/services/gemini_client.py`

**Pathology JSON-Spec — aktualisierte Felder:**

| Feld | Vorher | Nachher |
|---|---|---|
| `proliferation_index` | `string \| null` | 11 erlaubte Werte + `null` |
| `who_diagnosis` | `string \| null` (freier Text) | DB-Code bevorzugt, Fallback Diagnosename |
| `ihc_result` | `string \| null` | 4 erlaubte Werte (`positive`/`negative`/…) |
| `fish_result` | `string \| null` | 4 erlaubte Werte |
| `rna_result` | `string \| null` | 4 erlaubte Werte |
| `dna_result` | `string \| null` | 4 erlaubte Werte |

**Neue / aktualisierte Regeln:**
- Regel 1 (WHO-Diagnose): Code-Format dokumentiert mit Beispielen für Soft Tissue / Knochen / Sonstige
- Regel 9 (Molekularpathologie): Mapping-Tabelle für `_result`-Felder ergänzt
- Regel 10 (proliferation_index): Vollständige Range-Tabelle mit DE/EN-Mappings
- Regel 11 (Fehlende Werte): auf Nummer 11 verschoben

---

### `backend/requirements.txt`

- `PyYAML` hinzugefügt (fehlte, wird für YAML-Loading in `who_diagnosis` benötigt)

---

## Architektur-Notizen

### Zwei Normalisierungs-Ansätze

**Ansatz A — Enum-basiert** (einfache Felder, ≤ ~15 Werte):
```
Schema-Enum → static _normalize_*() → hardcoded Synonym-Maps
```
Beispiel: `biopsy_type`, `diagnostic_grading`, `proliferation_index`

**Ansatz B — YAML-basiert** (komplexe Felder, viele Werte):
```
_load_*_data() [lru_cache] → frozenset(codes) + label_to_code dict → _normalize_*()
```
Beispiel: `who_diagnosis` (~200 Codes aus who_diagnosis.yml + croms.enums.en.yml)

### Fallback-Kette (einheitlich)
```
1. Exakter Code-Match (lower)
2. Compact-Form (re.sub spaces/dashes → underscore)
3. Synonym-Map / Locale-Label-Lookup
4. Partieller Match (nur bei Ansatz B, eindeutig)
5. raw_text erhalten (kein null!)
6. None (nur bei leerem/null Input)
```

### Special Cases
- `biological_barrier_to_closest_margin`: Unmappbarer Text → `comment`-Feld, Hauptfeld → `None`
- `who_diagnosis`: YAML-Loader mit `parents[3]` Pfad-Auflösung relativ zum Schema-File
- `proliferation_index`: Regex sucht Prozentzeichen (`\d+%`) um Ki-67-Marker-Nummer zu vermeiden
