# pdfrag (RAG MVP)

Proof of Concept für ein Retrieval-Augmented-Generation-System zur Verarbeitung medizinischer PDF-Dokumente.

## Ziel

Das Projekt extrahiert strukturierte Informationen aus medizinischen Berichten (z. B. Radiology, Pathology, Surgery) und stellt die Ergebnisse über eine Weboberfläche sowie API-Endpunkte bereit.

## Features

- PDF-Upload (einzeln und batch)
- PDF-Text-Extraktion
- Dokumenttyp-Klassifikation via LLM
- Strukturierte Extraktion für medizinische Domänen
- Export/Weiterverarbeitung der Ergebnisse im Frontend
- Temporäre Dateispeicherung mit Cleanup im Backend

## Architektur

- `frontend/`: React + TypeScript + Vite + MUI
- `backend/`: FastAPI + Pydantic + pypdf + Google Gemini
- `db/`: Schema/Artefakte
- `terraform/`: Infrastruktur auf GCP
- `docker-compose.local.yml`: Lokaler Betrieb
- `docker-compose.prod.yml`: Produktionsnahes Docker-Setup

## Voraussetzungen

- Docker + Docker Compose (empfohlen)
- alternativ lokal:
  - Python 3.11+
  - Node.js 20+
  - npm
- Google Gemini API-Key (`GOOGLE_API_KEY`)

## Schnellstart (lokal mit Docker)

1. Backend-Env anlegen:

```bash
cp backend/.env backend/.env.local  # optionales Backup
# backend/.env mit GOOGLE_API_KEY befüllen
```

2. Services starten:

```bash
docker compose -f docker-compose.local.yml up --build
```

3. Aufrufen:

- Frontend: `http://localhost`
- Backend Health: `http://localhost/api/health`
- API Docs (Swagger): `http://localhost/api/docs`

## Lokale Entwicklung ohne Docker

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
export GOOGLE_API_KEY="<dein_key>"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Hinweis: Frontend nutzt `VITE_API_URL` (Standard im Compose-Build: `/api`).

## Wichtige Environment-Variablen (Backend)

- `GOOGLE_API_KEY` (Pflicht)
- `ALLOWED_ORIGINS` (CSV, Default: `http://localhost:8080`)
- `LLM_RATE_LIMIT` (Requests/Minute für `/api/llm/*`, Default: `30`)
- `HOST` (Default: `0.0.0.0`)
- `PORT` (Default: `8080`)

## API-Überblick

Basis: `/api`

- `POST /upload` - einzelne PDF hochladen
- `POST /upload/batch` - mehrere PDFs hochladen
- `GET /upload/{doc_id}/text` - Text aus gespeicherter PDF extrahieren
- `POST /extract-text` - direkte Text-Extraktion aus Upload
- `POST /upload-with-text` - Upload + optionale Sofort-Extraktion
- `POST /llm/classify-doc-type` - Dokumenttyp klassifizieren
- `POST /llm/extract` - generische Extraktion
- `POST /llm/extract-radiology`
- `POST /llm/extract-radiotherapy`
- `POST /llm/extract-pathology`
- `POST /llm/extract-surgery`
- `POST /llm/extract-sarcoma-board`
- `POST /llm/extract-systemic-therapy`

Live-Spezifikation: `http://localhost/api/docs`

## Tests

### Backend

```bash
python -m unittest discover -s backend/tests -v
```

### Frontend

```bash
cd frontend
npm test
```

## Produktion

Produktionsnahes Compose-Setup:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Enthält:

- `nginx-proxy` als Reverse Proxy
- `frontend` als statische Nginx-App
- `backend` als FastAPI-Service

## Terraform / GCP

Infrastrukturdefinitionen liegen unter `terraform/`.
Details zu Rollen, APIs und manuellen Vorbedingungen stehen in:

- `terraform/README.md`

## Sicherheitshinweise

- Keine Secrets ins Repository committen.
- API-Keys nur über Env-Variablen setzen.
- Uploads liegen temporär unter `backend/tmp` und werden periodisch bereinigt.

## Projektstatus

MVP / PoC-Stand mit Fokus auf funktionsfähigem End-to-End-Flow (Upload -> Extraktion -> strukturierte Ausgabe).
