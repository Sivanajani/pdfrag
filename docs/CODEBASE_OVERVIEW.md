# PDFrag Codebase-Dokumentation

## 1) Was das Projekt macht

`pdfrag` ist ein RAG-orientiertes MVP (PoC) zur Verarbeitung medizinischer PDF-Berichte.
Der End-to-End-Flow ist:

1. PDF(s) hochladen
2. PDF-Text extrahieren
3. Berichtstyp per LLM klassifizieren
4. Strukturierte Events pro Domäne extrahieren
5. Ergebnisse im Frontend prüfen, manuell korrigieren und exportieren (JSON/CSV/XLSX)

Ziel ist die strukturierte Aufbereitung von Berichten für Sarcoma-/Onkologie-nahe Prozesse (Radiology, Radiotherapy, Pathology, Surgery, Sarcoma Board, Systemic Therapy).

## 2) High-Level-Architektur

```text
[Browser / React]
   |
   | HTTP (VITE_API_URL, meist /api)
   v
[FastAPI Backend]
   |- Upload-Router: PDF validieren + temporär speichern + Text extrahieren
   |- LLM-Router: Klassifikation + domänenspezifische Extraktion
   |- Pydantic-Schemas: strikte Validierung/Normalisierung
   |- Rate Limit: /api/llm/* (in-memory, pro IP)
   v
[Google Gemini API]

Temporäre Dateien: backend/tmp (Cleanup auf Startup + periodisch)
```

Wichtig: Es gibt in diesem Repo **keine aktive Persistenz der extrahierten Daten in eine Datenbank**. Die Verarbeitung läuft API-basiert und in-memory im UI; `db/` liefert das Ziel-Datenmodell/Constraints als Referenz.

## 3) Repository-Struktur (wo was ist)

- `backend/`
- `frontend/`
- `db/`
- `terraform/`
- `docker-compose.local.yml`
- `docker-compose.prod.yml`

### Backend (`backend/`)

- `backend/app/main.py`
  - FastAPI-App, CORS, Health-Endpunkte
  - in-memory Rate Limit für `/api/llm/*`
  - Router-Mounting
  - Startup-Cleanup + periodischer Cleanup von `tmp/`
- `backend/app/routers/uploads.py`
  - Upload- und PDF-Text-Endpoints
- `backend/app/routers/llm.py`
  - Klassifikation + Extraktion pro Dokumenttyp
  - tolerantes Event-Parsing inkl. `raw_events` und `parse_issues`
- `backend/app/services/pdf_service.py`
  - Text-Extraktion aus PDF via `pypdf`
- `backend/app/services/gemini_client.py`
  - Gemini-Aufrufe + Prompting + JSON-Parsing
  - pro Domäne eigene Extraktionsfunktion
  - `classify_and_extract_from_text()` als Kombi-Call
- `backend/app/schemas/*.py`
  - Pydantic-Modelle/Enums pro Domäne, inkl. Datums-Validatoren
- `backend/app/utils/paths.py`
  - sichere Pfadlogik (`validate_doc_id`), Upload-Limit, tmp-Cleanup
- `backend/tests/`
  - Tests für Parser-Robustheit, Befund-Section-Logik, Pfad-Sicherheit

### Frontend (`frontend/`)

- `frontend/src/App.tsx`
  - App-Layout, Theme, Ergebnis-State, Übergabe an Panel
- `frontend/src/components/UploadWizard.tsx`
  - Kern-Workflow in 5 Phasen:
    - `upload`
    - `wizard` (pro Dokument Textvorschau + Patient-ID)
    - `summary`
    - `processing` (Klassifikation + Extraktion für alle Docs)
    - `done` (Typ-Korrektur + Re-Extraktion)
- `frontend/src/components/ExtractedDataPanel.tsx`
  - Tabellenansicht je Domäne
  - Inline-Editing einzelner Zellen
  - Export als JSON/CSV/XLSX
- `frontend/src/api.ts`
  - komplette API-Client-Schicht (Upload + alle LLM-Endpunkte)
  - zentrale TS-Typen der Event-Strukturen
- `frontend/src/i18n.ts` + `frontend/src/i18n/resources.ts`
  - Internationalisierung (`de`/`en`)
- `frontend/src/theme.ts`, `frontend/src/hooks/useColorScheme.ts`
  - Theme/Light-Dark-Umschaltung

### Datenmodell/Constraints (`db/`)

- `db/schema.rb`
  - Ziel-Datenbankschema (CROMS-Tabellen)
- `db/constraints/**`
  - Feldwerte/Enumerationen als YAML pro Domäne (z. B. `radiology_exam`, `surgery`, `systemic_therapy`)

Hinweis: Die Constraints dienen als Referenz der Domänenlogik und spiegeln sich in den Pydantic-Enums wider.

### Infrastruktur (`terraform/`)

- `terraform/env/dev` und `terraform/env/prod`
  - Umgebungs-spezifische Terraform-Konfiguration
- `terraform/modules/*`
  - VM, Firewall, Policy, Billing etc.
- `terraform/README.md`
  - manuelle Vorbedingungen (State Bucket, Static IP, Artifact Registry, Rollen)

## 4) Backend API (Endpunkte)

Basis-Prefix: `/api`

### Health

- `GET /api/health`
- `GET /healthz`

### Upload / PDF

- `POST /api/upload`
  - 1 PDF hochladen, temporär speichern, `id` zurückgeben
- `POST /api/upload/batch`
  - mehrere PDFs hochladen
- `GET /api/upload/{doc_id}/text`
  - Text aus zuvor gespeicherter PDF extrahieren
  - Query: `pages`, `max_chars`
- `POST /api/extract-text`
  - direkte Text-Extraktion aus hochgeladener PDF (ohne persistenten doc_id-Flow)
- `POST /api/upload-with-text`
  - Upload + optional sofortige Textextraktion (`extract=true`)

### LLM

- `POST /api/llm/classify-doc-type`
- `POST /api/llm/extract`
- `POST /api/llm/extract-radiology`
- `POST /api/llm/extract-radiotherapy`
- `POST /api/llm/extract-pathology`
- `POST /api/llm/extract-surgery`
- `POST /api/llm/extract-sarcoma-board`
- `POST /api/llm/extract-systemic-therapy`
- `POST /api/llm/classify-and-extract`

API-Dokumentation:
- Swagger: `/api/docs`
- OpenAPI JSON: `/api/openapi.json`

## 5) Request-/Response-Prinzip im LLM-Layer

Viele LLM-Endpunkte akzeptieren:

```json
{
  "doc_id": "...",
  "text": "...",
  "max_chars": 20000
}
```

Regeln:
- Entweder `doc_id` **oder** `text` (nicht beides)
- Bei `doc_id` wird PDF-Text serverseitig geladen
- Ergebnis wird über Pydantic gegen Domänenmodelle validiert
- Bei Feld-Fehlern versucht der Parser tolerant zu reparieren (`null`-Setzung), sammelt Fehler in `parse_issues`

## 6) Frontend-Datenfluss

1. Benutzer lädt bis zu 10 PDFs in den Wizard.
2. Für jedes Dokument: `upload-with-text` -> Textvorschau.
3. Benutzer vergibt `patient_id` pro Dokument.
4. In der Verarbeitung: pro Dokument `classify-and-extract`.
5. Ergebnisse werden nach `doc_type` aufgeteilt und im `ExtractedDataPanel` dargestellt.
6. Bei Fehlklassifikation kann der Typ manuell überschrieben und per domänenspezifischem Endpoint neu extrahiert werden.
7. Export pro Tabelle als JSON/CSV/XLSX.

## 7) Domänen / Schemas

Unterstützte Dokumenttypen:

- `radiology`
- `radiotherapy`
- `pathology`
- `surgery`
- `sarcoma_board`
- `systemic_therapy`

Jede Domäne hat:
- eigenes Pydantic-Schema in `backend/app/schemas/`
- eigene Gemini-Extraktionsfunktion in `backend/app/services/gemini_client.py`
- eigenen API-Endpoint unter `/api/llm/extract-...`
- eigene TS-Typen in `frontend/src/api.ts`

## 8) Sicherheit und technische Leitplanken

- Upload-Limit: `50 MB` pro Datei (`MAX_UPLOAD_SIZE_BYTES`)
- `doc_id`-Validierung gegen 32-char hex + Pfadschutz gegen Traversal
- Temp-Dateien nur in `backend/tmp`
- Cleanup alter Temp-Dateien (Default 1 Stunde)
- CORS über `ALLOWED_ORIGINS`
- Rate Limit für `/api/llm/*` (Default `30` Requests/Minute/IP, in-memory)
- PDF-Validierung über MIME + `%PDF-` Header

## 9) Konfiguration und Betrieb

### Relevante ENV-Variablen (Backend)

- `GOOGLE_API_KEY` (Pflicht)
- `ALLOWED_ORIGINS`
- `LLM_RATE_LIMIT`
- `HOST`
- `PORT`

### Docker

- Lokal: `docker-compose.local.yml`
  - `nginx-proxy`, `backend`, `frontend`
  - Frontend spricht über `VITE_API_URL=/api`
- Prod-nah: `docker-compose.prod.yml`
  - Reverse-Proxy + optionales Let's Encrypt Setup

## 10) Tests

Backend-Tests (`backend/tests`):
- `test_llm_parser.py`
- `test_befund_section.py`
- `test_paths_security.py`

Frontend:
- `vitest`-Setup, z. B. `frontend/src/utils/csv.test.ts`

## 11) Aktuelle Grenzen des MVP

- Keine persistente Speicherung extrahierter Events im Backend
- Rate Limiting ist pro Prozess in-memory (nicht shared/distributed)
- LLM-Extraktion hängt vollständig von externem Gemini-Service und Prompt-Qualität ab
- Teils starke Domänenabhängigkeit der Prompts (Deutsch/medizinische Berichtslogik)

## 12) Schnellorientierung für neue Entwickler

Wenn du neu im Projekt bist, starte hier:

1. `README.md` (Start/Run)
2. `backend/app/main.py` (App-Setup)
3. `backend/app/routers/uploads.py` und `backend/app/routers/llm.py` (API)
4. `frontend/src/components/UploadWizard.tsx` (Haupt-Workflow)
5. `frontend/src/components/ExtractedDataPanel.tsx` (Resultatdarstellung/Export)
6. `backend/app/schemas/` + `db/constraints/` (Domänenregeln)
