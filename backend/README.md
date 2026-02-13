# Backend README

## Zweck
Dieses Backend stellt Upload-, Textextraktions- und LLM-Extraktions-APIs für medizinische PDF-Berichte bereit.

## Tech-Stack
- FastAPI
- Pydantic
- pypdf
- Google Gemini (`google-generativeai`)

## Projektstruktur
- `app/main.py`: App-Setup, CORS, Rate-Limit, Startup-Cleanup
- `app/routers/uploads.py`: Upload und PDF-Text-Endpunkte
- `app/routers/llm.py`: Klassifikation und strukturierte Extraktion
- `app/services/gemini_client.py`: LLM-Prompts und Parsing
- `app/utils/paths.py`: Upload-Pfade, Validierung, Cleanup
- `tests/`: Unit-Tests

## Sicherheit und Datenhaltung
- Uploads werden nach `backend/tmp` geschrieben.
- `cleanup_tmp()` löscht alte Dateien periodisch.
- Aktuell: `TMP_MAX_AGE_SECONDS = 3600` (1 Stunde) in `app/utils/paths.py`.
- `validate_doc_id()` erlaubt nur 32-stellige Hex-IDs und blockiert ungültige Pfade.

## Voraussetzungen
- Python 3.11+ (lokal wurde auch mit 3.14 getestet)
- `pip`
- `GOOGLE_API_KEY` als Environment Variable

## Installation
```bash
cd backend
python -m pip install -r requirements.txt
```

## Starten (lokal)
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Relevante Environment-Variablen
- `GOOGLE_API_KEY`: Pflicht für LLM-Aufrufe
- `ALLOWED_ORIGINS`: CORS-Liste (CSV), Default `http://localhost:8080`
- `LLM_RATE_LIMIT`: Requests/Minute für `/api/llm/*`, Default `30`

## Testfälle
Die Tests liegen in `backend/tests`.

### Aktuelle Unit-Tests
1. `tests/test_llm_parser.py`
- Parser verliert keine Rohdaten bei Mapping/Enum-Fehlern.
- Nicht-Objekt-Events werden als Parse-Issue markiert.

2. `tests/test_befund_section.py`
- `extract_befund_section()` extrahiert korrekt bis zur nächsten Überschrift.
- Fallback auf Volltext, wenn kein `Befund`-Abschnitt gefunden wird.

3. `tests/test_paths_security.py`
- Cleanup löscht nur Dateien, die älter als `max_age_seconds` sind.
- Cleanup löscht keine neuen Dateien.
- Path Traversal via `../` in `doc_id` wird verhindert (HTTP 400).

## Tests ausführen
```bash
python -m unittest discover -s backend/tests -v
```

## Erwartetes Ergebnis
- Alle Tests sollten mit `OK` enden.
- Hinweis: Es kann ein `FutureWarning` zu `google.generativeai` erscheinen; das beeinflusst diese Unit-Tests nicht.

## Docker
Build:
```bash
cd backend
docker build -t rag-backend .
```

Run:
```bash
docker run --rm -p 8080:8080 -e GOOGLE_API_KEY=... rag-backend
```
