# ShapeRAG – Produktbeschreibung

**Version:** 0.1.0
**Domain:** shaperag.com
**Hersteller:** SwissNTech
**Kontakt:** sivanajani@swissntech.ch

---

## 1. Produktübersicht

ShapeRAG ist eine webbasierte Plattform zur automatisierten Extraktion strukturierter klinischer Daten aus medizinischen PDF-Berichten. Das System richtet sich an onkologische Zentren, Kliniken und Forschungseinrichtungen, die grosse Mengen an Arztbriefen, Befundberichten und Tumorboard-Protokollen digital aufbereiten und auswerten möchten.

Die Applikation kombiniert **PDF-Texterkennung**, **KI-gestützte Informationsextraktion** (Google Gemini) und ein **interaktives Frontend** zur Visualisierung, Bearbeitung und Export der Ergebnisse.

---

## 2. Kernfunktionen

### 2.1 Dokumenten-Upload
- Upload von **einem oder mehreren PDF-Dateien** gleichzeitig (Drag & Drop oder Dateiauswahl)
- Unterstützte Dateiformate: **PDF**
- Maximale Dateigröße: **50 MB pro Datei**
- Fortschrittsanzeige bei Mehrfach-Upload: "Verarbeite 2 / 5: befund_patient2.pdf"

### 2.2 Automatische Dokumenttyp-Erkennung (Auto-Detect)
- Optional: Der Dokumenttyp wird automatisch per KI klassifiziert
- Manuelle Auswahl alternativ möglich (6 Dokumenttypen)
- Bei Mehrfach-Upload wird jede Datei einzeln klassifiziert

### 2.3 Strukturierte Datenextraktion aus 6 Dokumenttypen

Das System erkennt und extrahiert Daten aus folgenden medizinischen Dokumenttypen:

| Dokumenttyp | Beschreibung | Felder |
|---|---|---|
| **Radiology** | Bildgebende Befunde (MRT, CT, PET, Röntgen, Sonographie) | 37+ Felder |
| **Radiotherapy** | Strahlentherapie-Protokolle | 13 Felder |
| **Pathology** | Histologische Befunde & Biopsien | 21 Felder |
| **Surgery** | Operationsberichte | 14 Felder |
| **Sarcoma Board** | Tumorboard-Protokolle | 24 Felder |
| **Systemic Therapy** | Chemo-/Immuntherapie-Berichte | 16 Felder |

#### Ausgewählte extrahierte Felder (Beispiel Radiology):
- Untersuchungsdatum, Bildgebungstyp, Timing
- Läsionsgrösse (grösste/mittlere/kleinste), Lokalisation
- RECIST-Response, Choi-Response, iRECIST, PET-Response
- Lokale Erkrankung: Status, Messbarkeit, MRT-Response, Radiologensicherheit
- Metastasen: Präsenz, Lokalisation, Anzahl (Lunge, Pleura, Knochen, Leber, Weichteile, Lymphknoten, Gehirn)
- Radiologiebefund (Freitext), Berichtsdatum

#### Wichtig – Befund-fokussierte Extraktion:
Die KI extrahiert ausschließlich aus dem Abschnitt "Befund" des Berichts (nicht aus der gesamten Dokumententext). Falls kein Befund-Abschnitt gefunden wird oder dieser weniger als 50 Zeichen enthält, wird automatisch der gesamte Text verwendet (Fallback).

### 2.4 Mehrfach-Upload & Akkumulation
- Mehrere Berichte desselben oder verschiedener Patienten können gleichzeitig hochgeladen werden
- Ergebnisse aller Berichte werden in **einer gemeinsamen Tabelle akkumuliert** (jeder Bericht = eine neue Zeile)
- Beispiel: 3 Radiologie-PDFs → 3 Zeilen in der Radiology-Tabelle, kombinierter CSV/XLSX/JSON-Export

### 2.5 Interaktive Ergebnistabelle
- Alle extrahierten Felder werden in einer **farbcodierten Tabelle** angezeigt:
  - Blau: Datum / Basisinformation
  - Orange: Kategorisierung / Diagnose
  - Grün: Behandlung / Resektion
  - Hellblau: Details / Charakteristika
  - Rot: Kritische Werte / Molekularpathologie
  - Lila: Zusammenfassungen / Berichte
- **Patient ID** ist als sticky-Spalte immer sichtbar (links fixiert)
- Leere Felder werden immer angezeigt (kein Ausblenden bei fehlenden Werten)
- Horizontales Scrollen für alle Felder

### 2.6 Inline-Bearbeitung
- Jede Zelle ist **direkt im Browser bearbeitbar** (Klick auf Zelle → Textfeld erscheint)
- Bestätigen mit Enter, Abbrechen mit Escape
- Korrekturen der KI-Extraktion möglich, ohne Neustart

### 2.7 Datenexport
Jede Tabelle bietet drei Exportformate:
- **JSON** – vollständig strukturiert, maschinenlesbar
- **CSV** – alle Spalten immer enthalten (leere Felder = leere Zellen)
- **XLSX** – Excel-kompatibel mit korrekter Spaltenstruktur

### 2.8 Mehrsprachigkeit
- Interface verfügbar auf **Deutsch** und **Englisch** (i18n)
- Umschaltbar zur Laufzeit

### 2.9 Dark / Light Mode
- Vollständig unterstützter Dark-Mode
- Umschaltbar über den Header

---

## 3. Technischer Ablauf (Workflow)

```
Nutzer lädt PDF hoch
       │
       ▼
[Backend] PDF-Validierung (Magic Bytes, Dateigröße, Dateityp)
       │
       ▼
[Backend] Texterkennung aus PDF (pypdf)
       │
       ▼
[Optional] Auto-Detect: Gemini klassifiziert Dokumenttyp
       │
       ▼
[Backend] Befund-Abschnitt extrahieren (Regex, Fallback auf Volltext)
       │
       ▼
[Backend] Gemini-Extraktion → strukturiertes JSON
       │
       ▼
[Backend] Pydantic-Validierung (fehlertolerante Bereinigung)
       │
       ▼
[Frontend] Anzeige in farbcodierter Tabelle
       │
       ▼
Nutzer bearbeitet / exportiert (CSV, XLSX, JSON)
```

**API-Calls pro Dokument:**
- Auto-Detect **an**: 1× `classify-doc-type` + 1× `extract-{doctype}` = **2 Calls**
- Auto-Detect **aus**: 1× `extract-{doctype}` = **1 Call**

---

## 4. Sicherheit (Security Layers)

### 4.1 Upload-Validierung
| Prüfung | Details |
|---|---|
| Dateityp (MIME) | Nur `application/pdf` oder `.pdf`-Endung |
| Magic Bytes | Inhalt muss mit `%PDF-` beginnen (echter PDF-Header) |
| Dateigröße | Maximum **50 MB** pro Datei (HTTP 413 bei Überschreitung) |

### 4.2 Path Traversal Protection
- Alle Dokument-IDs werden gegen das Regex-Muster `^[a-f0-9]{32}$` (32-stellige Hex-UUID) validiert
- Pfad-Resolution wird geprüft: Dateizugriff nur innerhalb des dedizierten `/tmp`-Verzeichnisses
- Ungültige IDs → HTTP 400; nicht gefundene Dateien → HTTP 404

### 4.3 Rate Limiting
- Alle `/api/llm/*`-Endpunkte sind rate-limitiert
- Standard: **30 Anfragen pro Minute pro IP-Adresse**
- Konfigurierbar über Umgebungsvariable `LLM_RATE_LIMIT`
- Sliding-Window-Algorithmus im Arbeitsspeicher
- Überschreitung → HTTP 429

### 4.4 CORS
- Erlaubte Origins über Umgebungsvariable `ALLOWED_ORIGINS` konfiguriert
- Nur definierte Herkunftsdomains können die API aufrufen
- Credentials-Unterstützung aktiviert

### 4.5 Temporäre Dateiverarbeitung
- Hochgeladene PDFs werden mit **UUID-Dateinamen** gespeichert (keine erratbaren Dateinamen)
- Automatische Löschung aller Dateien nach **1 Stunde** (Startup-Cleanup + stündlicher Cleanup-Job)
- Kein persistenter Datenspeicher – keine Datenbank, kein langfristiger Speicher

### 4.6 Fehlertolerante Pydantic-Validierung
- Bei Validierungsfehlern aus der KI-Antwort werden fehlerhafte Felder auf `null` gesetzt (statt Abbruch)
- Parse-Fehler werden geloggt und im Response zurückgegeben (`parse_issues`)
- Kein Datenverlust durch einzelne Feldvalidierungsfehler

### 4.7 TLS/SSL (Produktion)
- Nginx-Reverse-Proxy mit automatischem Let's Encrypt-Zertifikatsmanagement
- HTTPS auf Port 443 in der Produktionsumgebung
- HTTP (Port 80) für lokale Entwicklung

---

## 5. Tech-Stack

### 5.1 Frontend

| Technologie | Version | Zweck |
|---|---|---|
| **React** | 19.1.1 | UI-Framework |
| **TypeScript** | 5.9.3 | Typsicherheit |
| **Vite** | 7.1.7 | Build-Tool & Dev-Server |
| **Material UI (MUI)** | 7.x | UI-Komponenten, Tabellen, Icons |
| **Emotion** | 11.x | CSS-in-JS Styling |
| **i18next / react-i18next** | 25.x / 16.x | Internationalisierung (DE/EN) |
| **xlsx** | 0.18.5 | Excel-Export (XLSX) |
| **Framer Motion** | 12.x | Animationen |
| **Vitest** | 3.x | Unit-Tests |
| **ESLint** | 9.x | Code-Qualität |

### 5.2 Backend

| Technologie | Version | Zweck |
|---|---|---|
| **Python** | 3.11+ | Laufzeitumgebung |
| **FastAPI** | aktuell | REST-API-Framework |
| **Uvicorn** | aktuell | ASGI-Server |
| **Pydantic** | v2 | Datenvalidierung & Schemas |
| **pypdf** | aktuell | PDF-Textextraktion |
| **google-generativeai** | ≥0.8.0 | Gemini-KI-Integration |
| **python-multipart** | aktuell | Datei-Upload-Handling |

### 5.3 KI / LLM

| Komponente | Details |
|---|---|
| **Modell** | Google Gemini Flash (gemini-flash-latest) |
| **Anbieter** | Google AI (API-Key via Umgebungsvariable) |
| **Aufgaben** | Dokumentklassifikation, strukturierte Informationsextraktion |
| **Prompt-Sprache** | Deutsch (medizinische Fachterminologie) |
| **Output-Format** | JSON (strukturiert nach Pydantic-Schemas) |
| **Befund-Fokus** | Regex-basierte Abschnittserkennung vor LLM-Übergabe |

### 5.4 Infrastruktur & Deployment

| Komponente | Details |
|---|---|
| **Containerisierung** | Docker + Docker Compose |
| **Reverse Proxy** | nginx-proxy (nginxproxy/nginx-proxy:2678-alpine) |
| **SSL** | Let's Encrypt (automatisch via ACME Companion) |
| **Umgebungen** | Lokal (`docker-compose.local.yml`) & Produktion (`docker-compose.prod.yml`) |
| **Produktionsdomain** | shaperag.com / www.shaperag.com |
| **Backend-Port** | 8080 (intern) |
| **Frontend-Port** | 80/443 (extern via Proxy) |

---

## 6. API-Endpunkte (Übersicht)

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `POST` | `/api/upload-with-text` | PDF hochladen + Text extrahieren |
| `POST` | `/api/llm/classify-doc-type` | Dokumenttyp automatisch erkennen |
| `POST` | `/api/llm/extract-radiology` | Radiology-Daten extrahieren |
| `POST` | `/api/llm/extract-radiotherapy` | Radiotherapy-Daten extrahieren |
| `POST` | `/api/llm/extract-pathology` | Pathologie-Daten extrahieren |
| `POST` | `/api/llm/extract-surgery` | Operations-Daten extrahieren |
| `POST` | `/api/llm/extract-sarcoma-board` | Tumorboard-Daten extrahieren |
| `POST` | `/api/llm/extract-systemic-therapy` | Systemtherapie-Daten extrahieren |
| `POST` | `/api/llm/classify-and-extract` | Klassifikation + Extraktion in einem Call |
| `GET` | `/api/health` | Health Check |
| `GET` | `/api/docs` | Swagger UI (Interaktive API-Doku) |

---

## 7. Systemvoraussetzungen

### Betrieb (Server)
- Docker & Docker Compose installiert
- Google AI API-Key (`GOOGLE_API_KEY`)
- Konfigurierbare Umgebungsvariablen:
  - `GOOGLE_API_KEY` – Google Gemini API-Schlüssel
  - `ALLOWED_ORIGINS` – Erlaubte Frontend-Origins (z.B. `https://shaperag.com`)
  - `LLM_RATE_LIMIT` – Max. Anfragen/Minute pro IP (Standard: 30)

### Client (Browser)
- Moderner Webbrowser (Chrome, Firefox, Edge, Safari)
- Keine lokale Installation notwendig

---

## 8. Einschränkungen & Hinweise

- **Keine Datenbank**: Alle extrahierten Daten existieren nur im Browser-Speicher der aktuellen Sitzung. Beim Neuladen der Seite gehen nicht exportierte Daten verloren.
- **Temporäre PDFs**: Hochgeladene PDFs werden nach 1 Stunde automatisch gelöscht.
- **KI-Fehlerrate**: Die Genauigkeit der Extraktion hängt von der Qualität und Struktur des PDF-Textes ab. Handschriftliche oder gescannte PDFs ohne OCR werden nicht unterstützt.
- **Befund-Abschnitt**: Das System extrahiert primär aus dem Abschnitt "Befund". Bei abweichender Dokumentstruktur greift der Fallback auf den Volltext.
- **Sprache**: Die KI-Prompts und das Extraktionsverhalten sind auf **deutsche medizinische Berichte** optimiert.

---

## 9. Roadmap / Offene Punkte

- [ ] Persistente Datenspeicherung (Datenbank-Anbindung)
- [ ] Benutzer-Authentifizierung & Rollenverwaltung
- [ ] Mapping von `institution_id` und `patient_id` zu echten Stammdaten
- [ ] Unterstützung für OCR-gescannte PDFs
- [ ] Batch-Export über mehrere Sitzungen hinweg
- [ ] Audit-Log für alle Extraktionen

---

*Dokument erstellt: Februar 2026 | ShapeRAG v0.1.0 | SwissNTech Sivakumar*
