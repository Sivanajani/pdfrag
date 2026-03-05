import os
import json
from typing import List, Dict, Any

import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY ist nicht gesetzt. Bitte als Environment-Variable konfigurieren."
    )

genai.configure(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-flash-latest"


def extract_befund_section(text: str) -> str:
    """
    Extrahiert den 'Befund'-Abschnitt aus einem medizinischen Bericht.

    Sucht nach typischen Überschriften wie:
    - "Befund:", "BEFUND:", "Befund :"
    - "Makroskopischer Befund:", "Mikroskopischer Befund:"
    - "Histologischer Befund:"

    Endet bei der nächsten Überschrift wie:
    - "Beurteilung:", "Diagnose:", "Zusammenfassung:", "Kommentar:", etc.

    Falls kein Befund-Abschnitt gefunden wird, wird der gesamte Text zurückgegeben.
    """
    import re

    if not text or text.strip() == "":
        return text

    # Muster für den Beginn des Befund-Abschnitts
    befund_start_patterns = [
        r'(?i)(?:^|\n)\s*(?:makroskopischer\s+)?(?:mikroskopischer\s+)?(?:histologischer\s+)?befund\s*[:\-]?\s*\n',
        r'(?i)(?:^|\n)\s*BEFUND\s*[:\-]?\s*\n',
        r'(?i)(?:^|\n)\s*Befund\s*[:\-]\s*',
    ]

    # Muster für das Ende des Befund-Abschnitts (nächste Überschrift)
    end_patterns = [
        r'(?i)(?:^|\n)\s*(?:Beurteilung|Zusammenfassung|Diagnose|Kommentar|Empfehlung|Procedere|Bewertung|Schlussfolgerung|Interpretation|Stellungnahme)\s*[:\-]',
    ]

    # Versuche Befund-Abschnitt zu finden
    befund_start = None
    for pattern in befund_start_patterns:
        match = re.search(pattern, text)
        if match:
            befund_start = match.end()
            break

    if befund_start is None:
        # Kein Befund-Abschnitt gefunden → ganzen Text zurückgeben
        return text

    # Suche nach dem Ende des Befund-Abschnitts
    remaining_text = text[befund_start:]
    befund_end = len(remaining_text)

    for pattern in end_patterns:
        match = re.search(pattern, remaining_text)
        if match:
            befund_end = min(befund_end, match.start())

    befund_text = remaining_text[:befund_end].strip()

    # Falls extrahierter Befund sehr kurz ist (< 50 Zeichen), verwende gesamten Text
    if len(befund_text) < 50:
        return text

    return befund_text


def extract_structured_data_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Ruft Gemini auf und bittet um strukturierte Extraktion.
    Rückgabe: Liste von Dicts, z.B.
    [
      {
        "source_type": "measurement",
        "body_part": "Oberarm",
        "concept": "tumor_size",
        "value": 50,
        "unit": "mm",
        "note": "… ggf. Zusatzkontext …"
      },
      ...
    ]
    """
    if not text or text.strip() == "":
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    system_instructions = (
        "Du bist ein medizinischer Extraktions-Assistent. "
        "Du bekommst den Text eines medizinischen Berichts (z.B. PDF-Text). "
        "Extrahiere alle relevanten Messwerte und Befunde wie Tumorgrößen, "
        "Längenangaben, Volumen, etc. "
        "Gib das Ergebnis NUR als gültiges JSON mit einer Liste von Objekten zurück. "
        "Kein zusätzlicher Text, keine Erklärungen, nur JSON."
    )
    
    json_spec = """
    Antworte als JSON-Array von Objekten wie:
    [
      {
        "source_type": "measurement" | "description" | "other",
        "body_part": "Oberarm",
        "concept": "tumor_size",
        "value": 50,
        "unit": "mm",
        "note": "optionaler Textkontext oder Kommentar"
      }
    ]

    Regeln:
    - value ist eine Zahl, falls vorhanden (z.B. 50)
    - unit sind Einheiten wie "mm", "cm", "%", "ml" etc., falls vorhanden
    - body_part ist eine anatomische Region, falls erkennbar (z.B. 'Oberarm')
    - concept ist ein kurzer, englischer Identifier wie 'tumor_size', 'length', 'weight'
    - Wenn du nichts Sinnvolles extrahieren kannst, gib ein leeres Array [] zurück.
    """

    prompt = f"{system_instructions}\n\nJSON-Spezifikation:\n{json_spec}\n\nBerichtstext:\n```{text}```"

    response = model.generate_content(prompt)

    raw = response.text or ""

    
    raw = raw.strip()
    
    if raw.startswith("```"):
    
        raw = raw.strip("`")
    
        raw = raw.replace("json", "", 1).replace("JSON", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "source_type": item.get("source_type"),
                "body_part": item.get("body_part"),
                "concept": item.get("concept"),
                "value": item.get("value"),
                "unit": item.get("unit"),
                "note": item.get("note"),
            }
        )

    return normalized


def extract_radiology_events_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrahiert VOLLSTÄNDIGE RadiologyEvent-Daten aus einem Radiology-Bericht.
    Verwendet BEFUND + BEURTEILUNG Abschnitte.
    Unterstützt alle 45+ Felder aus dem RadiologyEvent-Schema.
    Kann mehrere Events pro Bericht zurückgeben (bei mehreren Läsionen/Regionen).
    """
    if not text or text.strip() == "":
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    # Nur den Befund-Abschnitt extrahieren
    text = extract_befund_section(text)

    system_instructions = """Du bist ein spezialisierter medizinischer Extraktions-Assistent für RADIOLOGIE-Befunde.

WICHTIG:
1. Du bekommst NUR den BEFUND-Abschnitt eines Radiologie-Berichts.
   Extrahiere ALLE relevanten Informationen aus diesem Abschnitt.

2. Klinische Angaben, Fragestellung und andere Abschnitte wurden bereits entfernt.
   Fokussiere dich auf die objektiven Beschreibungen: Größen, Lokalisationen, Befundtext.

3. Multi-Event Logik:
   - EINE Läsion in EINER Region → EIN Event
   - MEHRERE Läsionen in VERSCHIEDENEN Regionen → MEHRERE Events
   - Beispiel: Primärtumor Oberschenkel + Lungenmetastasen → 2 Events

4. Gib NUR valides JSON zurück, kein Markdown, keine Erklärungen."""

    json_spec = """
Gib ein JSON-ARRAY zurück. Jedes Element ist ein vollständiges RadiologyEvent:

[
  {
    // IDs (optional für LLM-Extraktion)
    "patient_id": number | null,

    // PFLICHTFELD
    "exam_date": "YYYY-MM-DD" (aus dem Bericht extrahieren, z.B. "2024-01-15"),

    // Grundlegende Untersuchungs-Informationen
    "exam_type": "conventional_x_ray" | "mri" | "ct_scan" | "ultrasound" | "pet_ct" | "pet_mri" | "scintigraphy" | "other" | null,
    "exam_type_comment": string | null,
    "imaging_timing": "initial_imaging" | "post_neoadjuvant_pre_op" | "immediate_post_op_baseline_6_12_weeks" | "surveillance" | "at_suspicion_of_local_recurrence" | "at_suspicion_of_systemic_recurrence" | null,
    "imaging_type": "local_imaging" | "systemic_imaging" | null,

    // Läsions-Informationen (location_of_lesion = Tiefenlage des Tumors, NICHT anatomische Region!)
    "location_of_lesion": "epifascial" | "subfascial" | "bone" | null,
    "largest_lesion_size_in_mm": number | null,
    "medium_lesion_size_in_mm": number | null,
    "smallest_lesion_size_in_mm": number | null,

    // Response-Kriterien (falls im Bericht erwähnt)
    "recist_response": "not_applicable" | "complete_remission_cr" | "partial_remission_pr" | "stable_disease_sd" | "progressive_disease_pd" | null,
    "choi_response": "not_applicable" | "complete_response_cr" | "partial_response_pr" | "stable_disease_sd" | "progressive_disease_pd" | null,
    "irecist_response": "not_applicable" | "complete_response_icr" | "partial_response_ipr" | "stable_disease_isd" | "unconfirmed_progressive_iupd" | "confirmed_progression_icpd" | null,
    "pet_response": "not_applicable" | "complete_metabolic_response_mcr" | "partial_metabolic_response_pmr" | "stable_metabolic_disease_smd" | "progressive_metabolic_disease_pmd" | null,

    // Lokale Erkrankung
    "local_disease_status": "no_evidence_of_local_disease" | "residual_viable_local_tumor_suspected" | "indeterminate_post_treatment_change" | "local_recurrence_suspected" | "local_recurrence_confirmed" | null,
    "local_disease_measurable": "yes" | "no" | "unknown" | null,
    "local_disease_report_largest_diameter": number | null,  // in mm
    "local_disease_qualitative_mri_response": "likely_viable" | "indeterminate" | "likely_treatment_effect" | null,
    "local_disease_radiologist_confidence": number | null,  // 1-5
    "local_disease_pet_metabolic_response": "cmr" | "pmr" | "smd" | "pmd" | null,

    // Metastasen - Allgemein
    "metastasis_presence": boolean | null,  // deprecated, aber noch unterstützt
    "metastasis": "no" | "yes" | "indeterminate" | null,
    "anatomic_location_of_metastasis": ["lung", "pleura", "bone", "liver", "soft_tissue", "lymph_node", "brain", "other"] | [],  // Array!

    // Metastasen - Anzahl pro Lokalisation
    "metastasis_location_lung_count": "one" | "two_to_five" | "more_than_five" | null,
    "metastasis_location_pleura_count": "one" | "two_to_five" | "more_than_five" | null,
    "metastasis_location_bone_count": "one" | "two_to_five" | "more_than_five" | null,
    "metastasis_location_liver_count": "one" | "two_to_five" | "more_than_five" | null,
    "metastasis_location_soft_tissue_count": "one" | "two_to_five" | "more_than_five" | null,
    "metastasis_location_lymph_node_count": "one" | "two_to_five" | "more_than_five" | null,
    "metastasis_location_brain_count": "one" | "two_to_five" | "more_than_five" | null,
    "metastasis_location_other_count": "one" | "two_to_five" | "more_than_five" | null,

    // Metastasen - Messungen
    "metastasis_target_lesion_count": number | null,
    "metastasis_longest_diameter_mm": number | null,
    "metastasis_indeterminate_category": "ipn_low" | "ipn_indeterminate" | "ipn_high" | "unclear" | null,

    // Vollständiger Befundtext
    "radiology_report": string | null,  // Der komplette Text aus BEFUND + BEURTEILUNG
    "report_date": "YYYY-MM-DD" | null  // Befunddatum (kann von exam_date abweichen)
  }
]

WICHTIGE REGELN:

1. **Datum-Extraktion**:
   - Wenn Datum im Format "15.01.2024" → konvertiere zu "2024-01-15"
   - Wenn mehrere Daten: exam_date ist das Untersuchungsdatum

2. **Läsions-Größen**:
   - Alle Größen in mm angeben
   - "5 cm" → 50 mm
   - "2,5 cm" → 25 mm

3. **Metastasen**:
   - "anatomic_location_of_metastasis" ist ein ARRAY (Liste)
   - Wenn "pulmonale Metastasen" → ["lung"]
   - Wenn "ossäre und hepatische Metastasen" → ["bone", "liver"]
   - Count-Felder: Wenn "eine Lungenmetastase" → "one", "2-3 Metastasen" → "two_to_five", "multiple" → "more_than_five"

4. **Response-Kriterien**:
   - Nur füllen wenn EXPLIZIT im Bericht genannt
   - "komplette Remission" → "complete_remission_cr"
   - "partielle Remission" → "partial_remission_pr"
   - "stabile Erkrankung" → "stable_disease_sd"
   - "Progress" → "progressive_disease_pd"

5. **Befundtext**:
   - "radiology_report": Kopiere BEFUND + BEURTEILUNG hierhin
   - Maximal 10.000 Zeichen
   - Format: "Befund: ... Beurteilung: ..."

6. **Fehlende Werte**:
   - Wenn Information nicht im Bericht: null verwenden
   - Niemals raten oder erfinden!

7. **Multi-Event Entscheidung**:
   - EINE Region, EINE Läsion → 1 Event (z.B. Knoten im Ellbogen)
   - MEHRERE Regionen → MEHRERE Events (z.B. Primärtumor Oberschenkel + Lungenmetastasen)
   - Bei Unsicherheit: Lieber EINE Zeile mit allen Infos

BEISPIELE für deutsche Ausdrücke:
- "MRT Oberschenkel" → exam_type: "mri"
- "CT Thorax" → exam_type: "ct_scan"
- "Erstuntersuchung" → imaging_timing: "initial_imaging"
- "Verlaufskontrolle" → imaging_timing: "surveillance"
- "nach neoadjuvanter Therapie" → imaging_timing: "post_neoadjuvant_pre_op"
- "Verdacht Lokalrezidiv" → imaging_timing: "at_suspicion_of_local_recurrence"
- "Lokalbildgebung" → imaging_type: "local_imaging"
- "epifasziales Weichteilsarkom" → location_of_lesion: "epifascial"
- "subfasziales Sarkom" → location_of_lesion: "subfascial"
- "keine Metastasen" → metastasis: "no"
- "Lungenmetastasen vorhanden" → metastasis: "yes", anatomic_location_of_metastasis: ["lung"]
- "unklare Leberläsion" → metastasis: "indeterminate", metastasis_indeterminate_category: "ipn_indeterminate"
- "wahrscheinlich benigne" → metastasis_indeterminate_category: "ipn_low"
- "kein Lokalbefund" → local_disease_status: "no_evidence_of_local_disease"
- "Resttumor" → local_disease_status: "residual_viable_local_tumor_suspected"
- "komplette Remission" → recist_response: "complete_remission_cr"
- "partielle Remission" → recist_response: "partial_remission_pr"
- "stabile Erkrankung" → recist_response: "stable_disease_sd"
- "Progress" → recist_response: "progressive_disease_pd"

BEISPIELE für Multi-Event:
- Bericht: "Knoten im Oberschenkel 3,5 cm. Beurteilung: Verdacht auf Sarkom" → 1 Event
- Bericht: "Primärtumor Oberschenkel 8 cm. Multiple Lungenmetastasen." → 2 Events
  Event 1: largest_lesion_size_in_mm=80, location_of_lesion="subfascial"
  Event 2: metastasis="yes", anatomic_location_of_metastasis=["lung"], metastasis_location_lung_count="more_than_five"
"""

    prompt = f"{system_instructions}\n\nJSON-Spezifikation:\n{json_spec}\n\nRadiologie-Berichtstext:\n{text}"

    response = model.generate_content(prompt)
    raw = (response.text or "").strip()

    # Bereinige Markdown-Wrapper
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).replace("JSON", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    # Normalisiere zu Liste
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    # Keine Key-Filterung mehr! Alle Felder durchlassen
    # Die Validierung übernimmt RadiologyEvent in llm.py
    return data


def classify_document_type(text: str) -> str:
    """
    Klassifiziert einen medizinischen Berichtstext automatisch in einen der 6 Dokumenttypen.

    Returns:
        "radiology" | "radiotherapy" | "pathology" | "surgery" | "sarcoma_board" | "systemic_therapy"
    """
    if not text or text.strip() == "":
        return "radiology"  # Default fallback

    model = genai.GenerativeModel(MODEL_NAME)

    prompt = """Du bist ein medizinischer Dokumenten-Klassifikations-Assistent.

AUFGABE: Klassifiziere den folgenden Berichtstext in GENAU EINEN der folgenden Dokumenttypen:

1. **radiology** - Radiologie-Befunde (MRT, CT, Röntgen, PET, Ultraschall)
   Erkennungsmerkmale: "Befund", "Beurteilung", "MRT", "CT", "Röntgen", "Bildgebung", "Untersuchung vom"

2. **radiotherapy** - Strahlentherapie-Berichte
   Erkennungsmerkmale: "Bestrahlungsplan", "Gy", "Gray", "Fraktionen", "Strahlentherapie", "Radiotherapie", "Zielvolumen"

3. **pathology** - Pathologie-Befunde (Histologie, Biopsie)
   Erkennungsmerkmale: "Histologie", "Biopsie", "mikroskopisch", "Färbung", "Immunhistochemie", "Gewebe", "Schnitt"

4. **surgery** - Operations-Berichte
   Erkennungsmerkmale: "Operation", "OP-Bericht", "Eingriff", "Resektion", "Operateur", "Anästhesie", "Schnittführung"

5. **sarcoma_board** - Tumorboard-Protokolle
   Erkennungsmerkmale: "Tumorboard", "Tumorkonferenz", "Board", "Empfehlung", "Diskussion", "Konsensus"

6. **systemic_therapy** - Systemische Therapie (Chemotherapie, Immuntherapie)
   Erkennungsmerkmale: "Chemotherapie", "Immuntherapie", "Zyklus", "Infusion", "mg/m²", "Medikamente", "Therapieplan"

WICHTIG:
- Antworte NUR mit dem Typ-Namen (z.B. "radiology")
- KEIN JSON, KEINE Erklärung, NUR der Typ-Name
- Bei Unsicherheit: Wähle den wahrscheinlichsten Typ

Berichtstext:
{text}

Klassifikation:""".format(text=text[:5000])  # Nur erste 5000 Zeichen für schnellere Classification

    try:
        response = model.generate_content(prompt)
        classification = (response.text or "").strip().lower()

        # Validiere gegen erlaubte Typen
        valid_types = {"radiology", "radiotherapy", "pathology", "surgery", "sarcoma_board", "systemic_therapy"}
        if classification in valid_types:
            return classification

        # Fuzzy matching falls LLM leichte Variationen zurückgibt
        if "radio" in classification and "therapy" in classification:
            return "radiotherapy"
        if "patholog" in classification:
            return "pathology"
        if "surg" in classification or "operation" in classification:
            return "surgery"
        if "board" in classification or "tumor" in classification:
            return "sarcoma_board"
        if "system" in classification or "chemo" in classification or "immun" in classification:
            return "systemic_therapy"

        # Default fallback
        return "radiology"

    except Exception:
        # Bei Fehler: Default zu radiology
        return "radiology"


def extract_radiotherapy_events_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrahiert Radiotherapie-Event-Daten aus einem Strahlentherapie-Bericht.
    Unterstützt ~17 Felder inkl. Arrays (indications, therapy_types).
    """
    if not text or text.strip() == "":
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    # Nur den Befund-Abschnitt extrahieren
    text = extract_befund_section(text)

    system_instructions = """Du bist ein spezialisierter medizinischer Extraktions-Assistent für STRAHLENTHERAPIE-Berichte.

WICHTIG:
1. Du bekommst NUR den BEFUND-Abschnitt eines Strahlentherapie-Berichts.
   Extrahiere ALLE relevanten Informationen aus diesem Abschnitt:
   - Indikation (präoperativ, postoperativ, definitiv, palliativ)
   - Therapietyp (IMRT, VMAT, stereotaktisch, Protonentherapie, etc.)
   - Dosierung (Gesamtdosis in Gy, Anzahl Fraktionen)
   - Volumina (PTV, GTV in cm³)
   - Termine (Überweisung, Erstkontakt, Therapiebeginn, Therapieende)
   - Hyperthermie-Status

2. Klinische Angaben und andere Abschnitte wurden bereits entfernt.

3. Gib NUR valides JSON zurück, kein Markdown, keine Erklärungen."""

    json_spec = """
Gib ein JSON-ARRAY zurück. Jedes Element ist ein RadiotherapyEvent:

[
  {
    // IDs (optional für LLM-Extraktion)
    "institution_id": number | null,
    "patient_id": number | null,
    "responsible_oncologist_id": number | null,

    // Termine (alle optional)
    "referral_date": "YYYY-MM-DD" | null,
    "first_contact_date": "YYYY-MM-DD" | null,
    "therapy_start_date": "YYYY-MM-DD" | null,
    "therapy_end_date": "YYYY-MM-DD" | null,

    // Indikationen - ARRAY! (Erlaubte DB-Codes)
    "indications": ["preoperative" | "postoperative" | "definitive" | "palliative" | "curative"],

    // Therapietypen - ARRAY! (Erlaubte DB-Codes)
    "therapy_types": [
      "intensity_modulated_radiotherapy_imrt" |
      "lattice_lrt" |
      "volumetric_arc_vmat" |
      "conventional_3d" |
      "stereotactic_radiotherapy" |
      "proton_therapy" |
      "intraoperative_linac" |
      "intraoperative_brachytherapy" |
      "brachytherapy" |
      "sequential_boost" |
      "simultaneous_integrated_boost"
    ],

    // Dosierung
    "total_dose_in_gy": number | null,  // Gesamtdosis in Gray
    "given_fractions": number | null,    // Anzahl Fraktionen

    // Volumina
    "ptv_volume_in_cm3": number | null,  // Planned Target Volume
    "gtv_volume_in_cm3": number | null,  // Gross Tumor Volume

    // Tumor-Lokalisation
    "was_tumor_located_in_radiated_area": boolean | null,
    "was_tumor_located_with_pre_existing_lymph_edema": boolean | null,

    // Hyperthermie (Erlaubte DB-Codes)
    "hyperthermia_status": "no" | "yes_radiation_hyperthermia" | null,

    // Kommentare
    "comments": string | null  // Max 2000 Zeichen
  }
]

WICHTIGE REGELN:

1. **Datum-Extraktion**:
   - Deutsche Formate "15.01.2024" → "2024-01-15"
   - referral_date = Überweisungsdatum
   - first_contact_date = Erstkontakt
   - therapy_start_date = Therapiebeginn
   - therapy_end_date = Therapieende

2. **Dosierung**:
   - "50 Gy" → total_dose_in_gy: 50
   - "25 Fraktionen" → given_fractions: 25
   - "5 x 5 Gy" → total_dose_in_gy: 25, given_fractions: 5

3. **Indikationen** (ARRAY! Erlaubte DB-Codes):
   - "präoperativ" / "neoadjuvant" → ["preoperative"]
   - "postoperativ" / "adjuvant" → ["postoperative"]
   - "definitiv" → ["definitive"]
   - "palliativ" → ["palliative"]
   - "kurativ" → ["curative"]
   - Mehrere möglich: ["preoperative", "postoperative"]

4. **Therapietypen** (ARRAY! Erlaubte DB-Codes):
   - "IMRT" / "intensitätsmoduliert" → ["intensity_modulated_radiotherapy_imrt"]
   - "VMAT" / "volumetric arc" → ["volumetric_arc_vmat"]
   - "Lattice" / "LRT" → ["lattice_lrt"]
   - "konventionell 3D" → ["conventional_3d"]
   - "stereotaktisch" / "SBRT" / "SRS" → ["stereotactic_radiotherapy"]
   - "Protonentherapie" → ["proton_therapy"]
   - "intraoperativ Linac" → ["intraoperative_linac"]
   - "intraoperative Brachytherapie" → ["intraoperative_brachytherapy"]
   - "Brachytherapie" → ["brachytherapy"]
   - "sequenzieller Boost" → ["sequential_boost"]
   - "simultaner integrierter Boost" / "SIB" → ["simultaneous_integrated_boost"]
   - Mehrere möglich: ["intensity_modulated_radiotherapy_imrt", "sequential_boost"]

5. **Hyperthermie** (Erlaubte DB-Codes):
   - Keine / nicht durchgeführt → "no"
   - Durchgeführt / geplant / ja → "yes_radiation_hyperthermia"

6. **Volumina**:
   - "PTV 500 cm³" → ptv_volume_in_cm3: 500
   - "GTV 120 cm³" → gtv_volume_in_cm3: 120

7. **Fehlende Werte**:
   - Wenn Information nicht im Bericht: null oder leeres Array []
   - Niemals raten oder erfinden!

BEISPIELE für deutsche Ausdrücke:
- "neoadjuvante Radiochemotherapie" → indications: ["preoperative"]
- "50 Gy in 25 Fraktionen" → total_dose_in_gy: 50, given_fractions: 25
- "IMRT-Plan" → therapy_types: ["intensity_modulated_radiotherapy_imrt"]
- "Therapiebeginn 15.01.2024" → therapy_start_date: "2024-01-15"
- "Hyperthermie: durchgeführt" → hyperthermia_status: "yes_radiation_hyperthermia"
"""

    prompt = f"{system_instructions}\n\nJSON-Spezifikation:\n{json_spec}\n\nStrahlentherapie-Berichtstext:\n{text}"

    response = model.generate_content(prompt)
    raw = (response.text or "").strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).replace("JSON", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    return data


def extract_pathology_events_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrahiert Pathologie-Event-Daten aus einem Pathologie-Befund.
    Unterstützt ~30 Felder inkl. Molekularpathologie (IHC, FISH, RNA, DNA).
    """
    if not text or text.strip() == "":
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    # Nur den Befund-Abschnitt extrahieren
    text = extract_befund_section(text)

    system_instructions = """Du bist ein spezialisierter medizinischer Extraktions-Assistent für PATHOLOGIE-Befunde.

WICHTIG:
1. Du bekommst NUR den BEFUND-Abschnitt eines Pathologie-Berichts.
   Extrahiere ALLE relevanten Informationen aus diesem Abschnitt:
   - Biopsie-/Resektionstyp und Datum
   - WHO-Diagnose und Grading
   - Chirurgische Ränder (R0/R1/R2) und Abstände
   - Tumor-Charakteristika (Ki-67, Mitosen, Nekrose)
   - Molekularpathologie (IHC, FISH, RNA, DNA)
   - EORTC Response Grade (bei neoadjuvanter Therapie)

2. Klinische Angaben und andere Abschnitte wurden bereits entfernt.

3. Gib NUR valides JSON zurück, kein Markdown, keine Erklärungen."""

    json_spec = """
Gib ein JSON-ARRAY zurück. Jedes Element ist ein PathologyEvent:

[
  {
    // IDs
    "institution_id": number,
    "patient_id": number,
    "responsible_pathologist_id": number | null,

    // Biopsie/Resektion
    "biopsy_type": "fine_needle" | "core_biopsy" | "open_incisional_with_suspicion_of_sarcoma" | "open_incisional_without_suspicion_of_sarcoma" | "excisional_with_suspicion_of_sarcoma" | "excisional_without_supsicion_of_sarcoma_whoops" | null,
    "biopsied_lesion_type": "biopsy_of_the_primary_tumor" | "biopsy_of_local_recurrence" | "biopsy_of_metastases" | "resection_of_the_primary_tumor" | "resection_of_local_recurrence" | "resection_of_metastases" | null,
    "biopsy_resection_date": "YYYY-MM-DD" | null,

    // Befund-Daten
    "registrate_date": "YYYY-MM-DD" | null,
    "first_report_date": "YYYY-MM-DD" | null,
    "final_report_date": "YYYY-MM-DD" | null,
    "report_date": "YYYY-MM-DD" | null,

    // Vorbehandlung
    "prior_treatment": "no" | "radiotherapy" | "chemotherapy" | "radiotherapy_and_chemotherapy" | "unknown",

    // Diagnose
    "who_diagnosis": string | null,  // DB-Code bevorzugt (z.B. "1_3_2_myxoid_liposarcoma"), sonst exakter WHO-Name aus dem Bericht

    // Grading
    "diagnostic_grading": "not_a_sarcoma" | "g1" | "g2" | "g3" | "benign" | "suspicious_of_malignancy" | "non_diagnostic" | "not_applicable" | "intermediate" | null,

    // Chirurgischer Rand
    "judgment_of_surgical_margin": "ro_wide_margin" | "r1a_marginal_margin_planned_close_ultimative_positive" | "r1b_marginal_margin_positive_after_tumor_bed_re_exicision" | "r1c_marginal_margin_inadvertent_positive_margin" | "r2_intralesional_margin" | "curettage" | "not_applicable_because_no_sarcoma" | null,
    "closest_distance_to_margin_mm": number | null,
    "biological_barrier_to_closest_margin": "none" | "fascia" | "adventitia" | "perineurium" | "periosteum" | "growth_plate" | "other" | "non_applicable" | null,
    "biological_barrier_to_closest_margin_comment": string | null,

    // Tumor-Charakteristika
    "proliferation_index": "less_than_10_percent" | "11_to_20_percent" | "21_to_30_percent" | "31_to_40_percent" | "41_to_50_percent" | "51_to_60_percent" | "61_to_70_percent" | "71_to_80_percent" | "81_to_90_percent" | "more_than_90_percent" | "not_applicable_because_of_therapy_before_biopsy_or_necrosis" | null,  // Ki-67-Wert als Bereich: z.B. Ki-67 40% → "31_to_40_percent"
    "mitoses_per_10hpf": "less_than_10_mitoses_per_10hpf" | "10_to_19_mitoses_per_10hpf" | "more_than_19_mitoses_per_10hpf" | "not_applicable_in_cases_with_neoadjuvant_therapy_necrosis" | null,
    "extent_of_necrosis": "less_than_10_percent" | "11_to_20_percent" | "21_to_30_percent" | "31_to_40_percent" | "41_to_50_percent" | "51_to_60_percent" | "61_to_70_percent" | "71_to_80_percent" | "81_to_90_percent" | "more_than_90_percent" | null,

    // Response nach neoadjuvanter Therapie
    "eortc_response_grade": "grade_a" | "grade_b" | "grade_c" | "grade_d" | "grade_e" | null,

    // Molekularpathologie - IHC
    "ihc_performed_status": "yes" | "no" | "not_yet_but_planned" | null,
    "ihc_result": "positive" | "negative" | "not_interpretable" | "in_progress" | null,

    // FISH
    "fish_performed_status": "yes" | "no" | "not_yet_but_planned" | null,
    "fish_result": "positive" | "negative" | "not_interpretable" | "in_progress" | null,

    // RNA-Sequenzierung
    "rna_performed_status": "yes" | "no" | "not_yet_but_planned" | null,
    "rna_result": "positive" | "negative" | "not_interpretable" | "in_progress" | null,

    // DNA-Sequenzierung
    "dna_performed_status": "yes" | "no" | "not_yet_but_planned" | null,
    "dna_result": "positive" | "negative" | "not_interpretable" | "in_progress" | null,

    // Vollständiger Befund
    "report": string | null  // Max 10000 Zeichen
  }
]

WICHTIGE REGELN:

1. **WHO-Diagnose** (who_diagnosis):
   - Bevorzugt: exakter DB-Code im Format "X_Y_Z_diagnosename" (z.B. "1_3_2_myxoid_liposarcoma")
   - Fallback: exakter WHO-Diagnosename aus dem Bericht (z.B. "Myxoid liposarcoma")
   - Code-Format: Ziffern_Untergruppe_Kurzname
     - Soft Tissue Tumoren: Präfix 1–12 (z.B. "4_2_1_synovial_sarcoma")
     - Knochen-Tumoren: Präfix 13–22 (z.B. "13_3_1_conventional_chondrosarcoma", "13_9_1_osteosarcoma_nos")
     - Sonstige: gs_ (genetische Syndrome), m_ (Metastasen), b_ (hämatopoietisch), ot_ (andere)
   - Beispiele:
     - Myxoid liposarcoma           → "1_3_2_myxoid_liposarcoma"
     - Synovial sarcoma             → "4_2_1_synovial_sarcoma"
     - Conventional chondrosarcoma  → "13_3_1_conventional_chondrosarcoma"
     - Osteosarcoma NOS             → "13_9_1_osteosarcoma_nos"
   - Wenn kein klarer Wert erkennbar → null

2. **Grading** (erlaubte Werte aus db/constraints/pathology/diagnostic_grading.yml):
   - "G1" / "gut differenziert" / "well differentiated" → "g1"
   - "G2" / "mäßig differenziert" / "moderately differentiated" → "g2"
   - "G3" / "schlecht differenziert" / "poorly differentiated" / "high grade" → "g3"
   - "GX" / "cannot be assessed" → "not_applicable"
   - "benign" / "gutartig" → "benign"
   - "kein Sarkom" / "not a sarcoma" → "not_a_sarcoma"
   - "suspekt" / "Verdacht auf Malignität" → "suspicious_of_malignancy"
   - "nicht diagnostisch" / "nicht verwertbar" / "inadequate" → "non_diagnostic"
   - "nicht zutreffend" / "not applicable" → "not_applicable"
   - "intermediär" / "intermediate" → "intermediate"
   - Wenn kein klarer Wert erkennbar und kein sinnvoller Text vorhanden → null
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

3. **Ränder**:
   - Erlaubte Werte für judgment_of_surgical_margin:
     - "ro_wide_margin"
     - "r1a_marginal_margin_planned_close_ultimative_positive"
     - "r1b_marginal_margin_positive_after_tumor_bed_re_exicision"
     - "r1c_marginal_margin_inadvertent_positive_margin"
     - "r2_intralesional_margin"
     - "curettage"
     - "not_applicable_because_no_sarcoma"
   - Mapping:
     - "R0" / "in sano" / "wide margin" → "ro_wide_margin"
     - "R1a" / "planned close margin" → "r1a_marginal_margin_planned_close_ultimative_positive"
     - "R1b" / "positive after tumor bed re-excision" → "r1b_marginal_margin_positive_after_tumor_bed_re_exicision"
     - "R1c" / "inadvertent positive margin" → "r1c_marginal_margin_inadvertent_positive_margin"
     - "R2" / "intralesional" → "r2_intralesional_margin"
     - "curettage" → "curettage"
     - "not applicable / no sarcoma" → "not_applicable_because_no_sarcoma"
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen
   - Abstand: "3 mm zum Rand" → closest_distance_to_margin_mm: 3
   - biological_barrier_to_closest_margin:
     - Erlaubte Werte: "none", "fascia", "adventitia", "perineurium", "periosteum", "growth_plate", "other", "non_applicable"
     - Synonyme (DE/EN) auf erlaubte Werte mappen (z.B. "Faszie" -> "fascia", "Wachstumsfuge" -> "growth_plate")
     - Wenn KEIN passendes Wort im Text steht -> "none"
     - Wenn Text vorhanden ist, aber kein valides Mapping möglich: biological_barrier_to_closest_margin = null
       und den Originaltext in biological_barrier_to_closest_margin_comment als raw_text speichern

4. **biopsied_lesion_type**:
   - Erlaubte Werte (nur diese 6):
     - "biopsy_of_the_primary_tumor"
     - "biopsy_of_local_recurrence"
     - "biopsy_of_metastases"
     - "resection_of_the_primary_tumor"
     - "resection_of_local_recurrence"
     - "resection_of_metastases"
   - Synonyme entsprechend mappen:
     - Biopsie Primärtumor -> biopsy_of_the_primary_tumor
     - Biopsie Lokalrezidiv -> biopsy_of_local_recurrence
     - Biopsie Metastase(n) -> biopsy_of_metastases
     - Resektion Primärtumor -> resection_of_the_primary_tumor
     - Resektion Lokalrezidiv -> resection_of_local_recurrence
     - Resektion Metastase(n) -> resection_of_metastases
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

5. **biopsy_type**:
   - Erlaubte Werte (nur diese 6):
     - "fine_needle"
     - "core_biopsy"
     - "open_incisional_with_suspicion_of_sarcoma"
     - "open_incisional_without_suspicion_of_sarcoma"
     - "excisional_with_suspicion_of_sarcoma"
     - "excisional_without_supsicion_of_sarcoma_whoops"
   - Synonyme entsprechend mappen:
     - Fine needle / FNA -> fine_needle
     - Core biopsy / Stanzbiopsie -> core_biopsy
     - Open incisional (mit Sarkomverdacht) -> open_incisional_with_suspicion_of_sarcoma
     - Open incisional (ohne Sarkomverdacht) -> open_incisional_without_suspicion_of_sarcoma
     - Excisional (mit Sarkomverdacht) -> excisional_with_suspicion_of_sarcoma
     - Excisional (ohne Sarkomverdacht / whoops) -> excisional_without_supsicion_of_sarcoma_whoops
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

6. **prior_treatment**:
   - Erlaubte Werte: "no", "radiotherapy", "chemotherapy", "radiotherapy_and_chemotherapy", "unknown"
   - Synonyme:
     - kein/keine/ohne Vorbehandlung -> no
     - Bestrahlung / Radiotherapie -> radiotherapy
     - Chemotherapie / Chemo -> chemotherapy
     - Radio + Chemo zusammen -> radiotherapy_and_chemotherapy
     - unklar / unknown -> unknown
   - Wenn keine Information im Bericht vorhanden ist -> unknown
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

7. **eortc_response_grade**:
   - Erlaubte Werte: "grade_a", "grade_b", "grade_c", "grade_d", "grade_e"
   - Mapping:
     - Grade 1 / no therapy effect -> grade_a
     - Grade 2 / <50% necrosis -> grade_b
     - Grade 3 / 50-90% necrosis -> grade_c
     - Grade 4 / >90% necrosis -> grade_d
     - Grade 5 / complete response / no viable tumor -> grade_e
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

8. **extent_of_necrosis**:
   - Erlaubte Werte: "less_than_10_percent", "11_to_20_percent", "21_to_30_percent", "31_to_40_percent", "41_to_50_percent", "51_to_60_percent", "61_to_70_percent", "71_to_80_percent", "81_to_90_percent", "more_than_90_percent"
   - Mapping:
     - <10% -> less_than_10_percent
     - 11-20% -> 11_to_20_percent
     - 21-30% -> 21_to_30_percent
     - 31-40% -> 31_to_40_percent
     - 41-50% -> 41_to_50_percent
     - 51-60% -> 51_to_60_percent
     - 61-70% -> 61_to_70_percent
     - 71-80% -> 71_to_80_percent
     - 81-90% -> 81_to_90_percent
     - >90% -> more_than_90_percent
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

9. **Molekularpathologie** (_result und _performed_status Felder):
   - Erlaubte Werte für ihc_result, fish_result, rna_result, dna_result: "positive", "negative", "not_interpretable", "in_progress"
   - Erlaubte Werte für ihc_performed_status, fish_performed_status, rna_performed_status, dna_performed_status: "yes", "no", "not_yet_but_planned"
   - Mapping der Status-Felder:
     - "durchgeführt" / "performed" / "done" -> "yes"
     - "nicht durchgeführt" / "not performed" / "none" / "n/a" -> "no"
     - "geplant" / "ausstehend" / "pending" / "not yet" -> "not_yet_but_planned"
   - Mapping der Ergebnisse:
     - "positiv" / "detected" / "nachgewiesen" / "amplifiziert" → "positive"
     - "negativ" / "not detected" / "nicht nachgewiesen" / "wildtyp" → "negative"
     - "nicht interpretierbar" / "nicht auswertbar" / "inadequate" → "not_interpretable"
     - "ausstehend" / "pending" / "in Bearbeitung" → "in_progress"
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen
   - Wenn kein sinnvoller Text vorhanden: null

10. **proliferation_index** (Ki-67 / Proliferationsindex):
   - Erlaubte Werte: "less_than_10_percent", "11_to_20_percent", "21_to_30_percent", "31_to_40_percent", "41_to_50_percent", "51_to_60_percent", "61_to_70_percent", "71_to_80_percent", "81_to_90_percent", "more_than_90_percent", "not_applicable_because_of_therapy_before_biopsy_or_necrosis"
   - Mapping: Prozentzahl nach dem Doppelpunkt extrahieren und Bereich zuordnen:
     - Ki-67 <10% → "less_than_10_percent"
     - Ki-67 11-20% → "11_to_20_percent"
     - Ki-67 21-30% → "21_to_30_percent"
     - Ki-67 31-40% → "31_to_40_percent"
     - Ki-67 41-50% → "41_to_50_percent"
     - Ki-67 51-60% → "51_to_60_percent"
     - Ki-67 61-70% → "61_to_70_percent"
     - Ki-67 71-80% → "71_to_80_percent"
     - Ki-67 81-90% → "81_to_90_percent"
     - Ki-67 >90% → "more_than_90_percent"
     - Neoadjuvante Therapie / Nekrose → "not_applicable_because_of_therapy_before_biopsy_or_necrosis"
   - Wenn kein klarer Wert erkennbar und kein sinnvoller Text vorhanden → null
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

11. **mitoses_per_10hpf**:
   - Erlaubte Werte: "less_than_10_mitoses_per_10hpf", "10_to_19_mitoses_per_10hpf", "more_than_19_mitoses_per_10hpf", "not_applicable_in_cases_with_neoadjuvant_therapy_necrosis"
   - Mapping:
     - <10 Mitosen/10 HPF -> less_than_10_mitoses_per_10hpf
     - 10-19 Mitosen/10 HPF -> 10_to_19_mitoses_per_10hpf
     - >19 Mitosen/10 HPF -> more_than_19_mitoses_per_10hpf
     - Neoadjuvante Therapie/Nekrose -> not_applicable_in_cases_with_neoadjuvant_therapy_necrosis
   - Wenn Text vorhanden ist, aber kein valides Mapping möglich: originalen Text unverändert übernehmen

12. **Fehlende Werte**:
   - Standard: null verwenden
   - Ausnahme prior_treatment: unknown
   - Ausnahme biological_barrier_to_closest_margin: none

BEISPIELE:
- "Ki-67: 40%" → proliferation_index: "31_to_40_percent"
- "Ki-67: 5%" → proliferation_index: "less_than_10_percent"
- "MIB1: 65%" → proliferation_index: "61_to_70_percent"
- "5 Mitosen/10 HPF" → mitoses_per_10hpf: "less_than_10_mitoses_per_10hpf"
- "15 Mitosen/10 HPF" → mitoses_per_10hpf: "10_to_19_mitoses_per_10hpf"
- "25 Mitosen/10 HPF" → mitoses_per_10hpf: "more_than_19_mitoses_per_10hpf"
- Neoadjuvante Therapie / Nekrose → mitoses_per_10hpf: "not_applicable_in_cases_with_neoadjuvant_therapy_necrosis"
- "Nekrose <10%" → extent_of_necrosis: "less_than_10_percent"
"""

    prompt = f"{system_instructions}\n\nJSON-Spezifikation:\n{json_spec}\n\nPathologie-Berichtstext:\n{text}"

    response = model.generate_content(prompt)
    raw = (response.text or "").strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).replace("JSON", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    return data


def extract_surgery_events_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrahiert Chirurgie-Event-Daten aus einem Operations-Bericht.
    Unterstützt ~25 Felder inkl. Arrays (resection, participated_disciplines).
    """
    if not text or text.strip() == "":
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    # Nur den Befund-Abschnitt extrahieren
    text = extract_befund_section(text)

    system_instructions = """Du bist ein spezialisierter medizinischer Extraktions-Assistent für OPERATIONS-Berichte.

WICHTIG:
1. Du bekommst NUR den BEFUND-Abschnitt eines Operations-Berichts.
   Extrahiere ALLE relevanten chirurgischen Details aus diesem Abschnitt:
   - Indikation und Datum der Operation
   - Anatomische Region und Seite
   - Tumorgröße und Resektionstyp
   - Resektionsrand (R0/R1/R2)
   - Rekonstruktionstyp
   - Amputation (falls zutreffend)
   - Beteiligte Disziplinen

2. Klinische Angaben und andere Abschnitte wurden bereits entfernt.

3. Gib NUR valides JSON zurück, kein Markdown, keine Erklärungen."""

    json_spec = """
Gib ein JSON-ARRAY zurück. Jedes Element ist ein SurgeryEvent:

[
  {
    // IDs
    "institution_id": number,
    "patient_id": number,
    "responsible_surgeon_id": number,

    // PFLICHTFELD
    "surgery_date": "YYYY-MM-DD",

    // Operations-Details
    "indication": "Preoperative biopsy" | "Definitive surgery" | "Curative resection" | "Palliative surgery" | "Revision surgery" | "Debulking" | "Metastasectomy" | "Other" | null,
    "indication_comment": string | null,

    "surgery_side": "Left" | "Right" | "Bilateral" | "Midline" | "Not applicable" | null,
    "anatomic_region": "Head and neck" | "Trunk" | "Chest wall" | "Abdomen" | "Pelvis" | "Upper extremity" | "Lower extremity" | "Retroperitoneum" | "Other" | null,

    // Tumor
    "greatest_surgical_tumor_dimension_in_mm": number | null,
    "had_tumor_spillage": boolean | null,

    // Resektion - ARRAY!
    "resection": [
      "Wide excision" | "Marginal excision" | "Intralesional excision" |
      "Compartmental resection" | "En-bloc resection" | "Limb-sparing surgery"
    ],

    "resected_tumor_margin": "R0 (complete resection, negative margins)" | "R1 (microscopic residual tumor)" | "R2 (macroscopic residual tumor)" | "Unknown" | null,

    // Rekonstruktion
    "reconstruction": "None" | "Primary closure" | "Skin graft" | "Local flap" | "Free flap" | "Mesh" | "Prosthesis" | "Bone graft" | "Endoprosthesis" | "Other" | null,

    // Amputation
    "amputation": "None" | "Above-knee amputation" | "Below-knee amputation" | "Above-elbow amputation" | "Below-elbow amputation" | "Hip disarticulation" | "Shoulder disarticulation" | "Hemipelvectomy" | "Other" | null,

    "hemipelvectomy": string[] | [],  // Array für Details

    // Revisionen
    "first_revision_details": string | null,
    "second_revision_details": string | null,

    // Beteiligte Disziplinen - ARRAY!
    "participated_disciplines": [
      "Orthopedic surgery" | "General surgery" | "Plastic surgery" |
      "Vascular surgery" | "Thoracic surgery" | "Neurosurgery" |
      "Gynecology" | "Urology" | "Other"
    ],
    "participated_disciplines_comment": string | null
  }
]

WICHTIGE REGELN:

1. **Datum**: surgery_date ist PFLICHTFELD!
   - "OP am 15.01.2024" → surgery_date: "2024-01-15"

2. **Indikation**:
   - "Whoops-Exzision" oder "unbeabsichtigt" → "Preoperative biopsy"
   - "kurative Resektion" → "Curative resection"
   - "palliativ" → "Palliative surgery"

3. **Anatomische Region**:
   - "Oberschenkel" → "Lower extremity"
   - "Unterarm" → "Upper extremity"
   - "Becken" → "Pelvis"

4. **Resektionstyp** (ARRAY!):
   - "weite Exzision" → ["Wide excision"]
   - "kompartmentelle Resektion" → ["Compartmental resection"]
   - Mehrere möglich: ["Wide excision", "Compartmental resection"]

5. **Resektionsrand**:
   - "R0" → "R0 (complete resection, negative margins)"
   - "R1" → "R1 (microscopic residual tumor)"
   - "R2" → "R2 (macroscopic residual tumor)"

6. **Rekonstruktion**:
   - "primärer Wundverschluss" → "Primary closure"
   - "Hauttransplantat" → "Skin graft"
   - "freier Lappen" → "Free flap"
   - "Mesh" → "Mesh"

7. **Beteiligte Disziplinen** (ARRAY!):
   - "Plastische Chirurgie" → ["Plastic surgery"]
   - "Gefäßchirurgie" → ["Vascular surgery"]
   - Mehrere: ["Orthopedic surgery", "Plastic surgery"]

BEISPIELE:
- "Tumorgröße 8 cm" → greatest_surgical_tumor_dimension_in_mm: 80
- "linker Oberschenkel" → surgery_side: "Left", anatomic_region: "Lower extremity"
"""

    prompt = f"{system_instructions}\n\nJSON-Spezifikation:\n{json_spec}\n\nOperations-Berichtstext:\n{text}"

    response = model.generate_content(prompt)
    raw = (response.text or "").strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).replace("JSON", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    return data


def extract_sarcoma_board_events_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrahiert Sarkom-Board-Event-Daten aus einem Tumorboard-Protokoll.
    Unterstützt ~30 Felder inkl. Board-Entscheidungen und Zusammenfassungen.
    """
    if not text or text.strip() == "":
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    # Nur den Befund-Abschnitt extrahieren
    text = extract_befund_section(text)

    system_instructions = """Du bist ein spezialisierter medizinischer Extraktions-Assistent für TUMORBOARD-Protokolle.

WICHTIG:
1. Du bekommst NUR den BEFUND-Abschnitt eines Tumorboard-Protokolls.
   Extrahiere ALLE relevanten Informationen aus diesem Abschnitt:
   - Präsentationsdatum und Grund
   - Patient-Status vorher/nachher
   - Behandlungsverlauf
   - Fragestellung an das Board
   - Board-Entscheidungen (Chirurgie, Radiotherapie, Systemtherapie, etc.)
   - Zusammenfassungen (Radiologie, Pathologie, etc.)

2. Klinische Angaben und andere Abschnitte wurden bereits entfernt.

3. Gib NUR valides JSON zurück, kein Markdown, keine Erklärungen."""

    json_spec = """
Gib ein JSON-ARRAY zurück. Jedes Element ist ein SarcomaBoardEvent:

[
  {
    // IDs
    "institution_id": number,
    "patient_id": number,

    // PFLICHTFELD
    "presentation_date": "YYYY-MM-DD",

    // Grund und Status
    "reason_for_presentation": "first_time" | "unplanned_excision" | "follow_up" | null,
    "status_before_follow_up": "no_previous_therapy" | "locally_advanced_tumor" | "exophytic_growth" | null,
    "status_after_follow_up": "partial_therapy_for_primary_tumor" | "completed_therapy_for_primary_tumor" | "other" | null,
    "status_after_follow_up_comment": string | null,

    // Behandlungsverlauf
    "treatment_before_follow_up": "none" | "surgery" | "radiotherapy" | "systemic_therapy" | "surgery_radiotherapy" | "surgery_chemotherapy" | "radiotherapy_chemotherapy" | "surgery_chemotherapy_radiotherapy" | null,
    "follow_up_reason": "in_context_of_primary_treatment" | "first_local_recurrence" | "in_context_of_treatment_for_first_local_recurrence" | "first_systemic_recurrence" | "in_context_of_first_systemic_recurrence" | "second_or_more_local_systemic_recurrences" | "important_follow_up_information_of_general_interest" | null,
    "last_execution": "patient_related_factors" | "physician_healthcare_provider_related_factors" | "logistical_administrative_factors" | "no_re_presentation_at_sarcomaboard" | "systemic_institutional_factors" | "disease_course" | "research_trial_related_factors" | "no_categorization_possible" | null,
    "unplanned_excision_date": "YYYY-MM-DD" | null,

    // Fragestellung
    "question": string | null,  // Max 2000 Zeichen
    "proposed_procedure": string | null,  // Max 2000 Zeichen

    // ECOG
    "current_ecog": number | null,  // 0-5

    // Board-Entscheidungen (jeweils mit Kommentar)
    "decision_surgery": "yes" | "yes_interventional_radiology" | "no" | "undecided" | null,
    "decision_surgery_comment": string | null,

    "decision_radio_therapy": "yes" | "yes_interventional_radiology" | "no" | "undecided" | null,
    "decision_radio_therapy_comment": string | null,

    "decision_systemic_surgery": "yes" | "yes_interventional_radiology" | "no" | "undecided" | null,  // systemische Therapie-Entscheidung
    "decision_systemic_surgery_comment": string | null,

    "decision_follow_up": "yes" | "yes_interventional_radiology" | "no" | "undecided" | null,
    "decision_follow_up_comment": string | null,

    "decision_diagnostics": "yes" | "yes_interventional_radiology" | "no" | "undecided" | null,
    "decision_diagnostics_comment": string | null,

    "decision_palliative_care": "yes" | "yes_interventional_radiology" | "no" | "undecided" | null,
    "decision_palliative_care_comment": string | null,

    // Zusammenfassungen
    "summary": string | null,  // Max 5000 Zeichen
    "patient_history": string | null,
    "summary_patient_information": string | null,
    "summary_radiology": string | null,
    "summary_pathology": string | null,
    "further_details": string | null,

    // Zusätzlich
    "fast_track": boolean,  // Default: false
    "whoops_surgery_institution_id": number | null,
    "presenting_physician_id": number | null
  }
]

WICHTIGE REGELN:

1. **Präsentationsdatum**: presentation_date ist PFLICHTFELD!
   - "Board vom 15.01.2024" → "2024-01-15"

2. **Board-Entscheidungen**:
   - "Chirurgie empfohlen" → decision_surgery: "yes"
   - "Radiotherapie nicht indiziert" → decision_radio_therapy: "no"
   - "Systemtherapie wird diskutiert" → decision_systemic_surgery: "undecided"
   - "Interventionelle Radiologie" → decision_surgery: "yes_interventional_radiology"
   - Kommentare: Zusätzliche Details zur Entscheidung

3b. **Präsentationsgrund**:
   - "Erstvorstellung" → reason_for_presentation: "first_time"
   - "Whoops-OP" → reason_for_presentation: "unplanned_excision"
   - "Verlaufskontrolle" → reason_for_presentation: "follow_up"

3c. **Behandlungshistorie**:
   - "nach Chirurgie und Radiotherapie" → treatment_before_follow_up: "surgery_radiotherapy"
   - "nach Chemotherapie" → treatment_before_follow_up: "systemic_therapy"

3. **ECOG**:
   - "ECOG 0" → current_ecog: 0
   - "ECOG 2" → current_ecog: 2

4. **Zusammenfassungen**:
   - summary: Gesamtzusammenfassung der Board-Sitzung
   - summary_radiology: Radiologische Zusammenfassung
   - summary_pathology: Pathologische Zusammenfassung

5. **Fehlende Werte**: null verwenden

BEISPIELE:
- "Empfehlung: Weite Exzision mit anschließender Radiotherapie"
  → decision_surgery: "yes", decision_radio_therapy: "yes"
- "Follow-up in 3 Monaten"
  → decision_follow_up: "yes", decision_follow_up_comment: "in 3 Monaten"
- "Erstpräsentation, keine Vorbehandlung"
  → reason_for_presentation: "first_time", treatment_before_follow_up: "none"
- "Verlauf nach OP und Radiotherapie, Lokalrezidiv"
  → reason_for_presentation: "follow_up", treatment_before_follow_up: "surgery_radiotherapy", follow_up_reason: "first_local_recurrence"
"""

    prompt = f"{system_instructions}\n\nJSON-Spezifikation:\n{json_spec}\n\nTumorboard-Protokoll:\n{text}"

    response = model.generate_content(prompt)
    raw = (response.text or "").strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).replace("JSON", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    return data


def extract_systemic_therapy_events_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrahiert Systemische-Therapie-Event-Daten aus einem Chemotherapie/Immuntherapie-Bericht.
    Unterstützt ~20 Hauptfelder + nested Arrays (drugs, adverse_events).
    """
    if not text or text.strip() == "":
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    # Nur den Befund-Abschnitt extrahieren
    text = extract_befund_section(text)

    system_instructions = """Du bist ein spezialisierter medizinischer Extraktions-Assistent für SYSTEMISCHE THERAPIE-Berichte (Chemotherapie, Immuntherapie, Targeted Therapy).

WICHTIG:
1. Du bekommst NUR den BEFUND-Abschnitt eines Systemtherapie-Berichts.
   Extrahiere ALLE relevanten Informationen aus diesem Abschnitt:
   - Therapiegrund (neoadjuvant, adjuvant, palliativ) und Linie
   - Protokoll (MAP, MAID, AI, Gemcitabine/Docetaxel, etc.)
   - Medikamente mit Dosierungen
   - Zyklen und Zeitraum
   - Unerwünschte Ereignisse (Adverse Events)
   - Hyperthermie, Studienteilnahme

2. Klinische Angaben und andere Abschnitte wurden bereits entfernt.

3. Gib NUR valides JSON zurück, kein Markdown, keine Erklärungen."""

    json_spec = """
Gib ein JSON-ARRAY zurück. Jedes Element ist ein SystemicTherapyEvent:

[
  {
    // IDs
    "institution_id": number,
    "patient_id": number,
    "responsible_oncologist_id": number | null,

    // Therapiegrund
    "reason": "Neoadjuvant" | "Adjuvant" | "Palliative (first line)" | "Palliative (further line)" | "Curative" | "Maintenance" | "Other" | null,
    "reason_comment": string | null,
    "treatment_line": 1 | 2 | 3 | 4 | 5 | null,  // 1=first line, 5=fifth or more

    // Protokolle
    "bone_protocol": "MAP (Methotrexate, Adriamycin, Cisplatin)" | "MAPIE (MAP + Ifosfamide, Etoposide)" | "EURAMOS" | "IE (Ifosfamide, Etoposide)" | "VAI (Vincristine, Adriamycin, Ifosfamide)" | "Other" | "None" | null,
    "bone_protocol_comment": string | null,

    "softtissue_protocol": "AI (Adriamycin, Ifosfamide)" | "MAID (Mesna, Adriamycin, Ifosfamide, Dacarbazine)" | "Gemcitabine/Docetaxel" | "Trabectedin" | "Pazopanib" | "Eribulin" | "Ifosfamide monotherapy" | "Doxorubicin monotherapy" | "Other" | "None" | null,
    "softtissue_protocol_comment": string | null,

    // Zeitraum
    "cycle_start_date": "YYYY-MM-DD" | null,
    "cycle_end_date": "YYYY-MM-DD" | null,
    "cycles_executed": string | null,  // z.B. "6/6" oder "4/6"

    // Begleittherapie
    "was_rct_concomittant": boolean,  // Gleichzeitige Radiochemotherapie
    "hyperthermia_status": "None" | "Planned" | "Ongoing" | "Completed" | null,

    // Studienteilnahme
    "clinical_trial_inclusion": "Yes" | "No" | "Unknown" | null,

    // Abbruch
    "discontinuation_reason": "Completion of planned therapy" | "Progressive disease" | "Toxicity" | "Patient refusal" | "Death" | "Surgery planned" | "Other" | null,

    // Patient-Typ
    "patient_type": "Pediatric" | "Adolescent/Young adult (AYA)" | "Adult" | null,

    // Assessment
    "assessment_date": "YYYY-MM-DD" | null,

    // Kommentare
    "comments": string | null,

    // NESTED: Medikamente (ARRAY!)
    "drugs": [
      {
        "drug_type": "Adriamycin (Doxorubicin)" | "Cisplatin" | "Carboplatin" | "Ifosfamide" | "Etoposide" | "Methotrexate" | "Vincristine" | "Cyclophosphamide" | "Dacarbazine" | "Gemcitabine" | "Docetaxel" | "Pazopanib" | "Trabectedin" | "Eribulin" | "Imatinib" | "Mesna" | "G-CSF" | "Other",
        "dose": number | null,
        "dose_unit": string | null,  // z.B. "mg", "mg/m²", "mg/kg"
        "frequency": number | null,
        "frequency_unit": string | null,  // z.B. "daily", "weekly", "q3w"
        "frequency_unit_comment": string | null,
        "route": "Intravenous (IV)" | "Oral (PO)" | "Intramuscular (IM)" | "Subcutaneous (SC)" | "Intrathecal (IT)" | "Other" | null,
        "administration_day": string | null  // z.B. "Day 1", "Day 1-5"
      }
    ],

    // NESTED: Unerwünschte Ereignisse (ARRAY!)
    "adverse_events": [
      {
        "medical_area": string,  // z.B. "Hematology"
        "event_type": string,    // z.B. "Neutropenia"
        "grade": string,         // CTCAE Grade "1", "2", "3", "4", "5"
        "start_date": "YYYY-MM-DD" | null,
        "end_date": "YYYY-MM-DD" | null,
        "comment": string | null
      }
    ]
  }
]

WICHTIGE REGELN:

1. **Therapiegrund und Linie**:
   - "neoadjuvant" → reason: "Neoadjuvant"
   - "adjuvant" → reason: "Adjuvant"
   - "palliativ Erstlinie" → reason: "Palliative (first line)", treatment_line: 1
   - "Zweitlinientherapie" → treatment_line: 2

2. **Protokolle**:
   - "MAP-Schema" → bone_protocol: "MAP (Methotrexate, Adriamycin, Cisplatin)"
   - "AI-Schema" → softtissue_protocol: "AI (Adriamycin, Ifosfamide)"
   - "Gem/Doce" → softtissue_protocol: "Gemcitabine/Docetaxel"

3. **Medikamente** (ARRAY!):
   - Für jedes Medikament ein eigenes Objekt
   - "Doxorubicin 75 mg/m² i.v. Tag 1" →
     {
       drug_type: "Adriamycin (Doxorubicin)",
       dose: 75,
       dose_unit: "mg/m²",
       route: "Intravenous (IV)",
       administration_day: "Day 1"
     }

4. **Unerwünschte Ereignisse** (ARRAY!):
   - "Neutropenie Grad 3" →
     {
       medical_area: "Hematology",
       event_type: "Neutropenia",
       grade: "3"
     }

5. **Zyklen**:
   - "6 Zyklen geplant, 4 verabreicht" → cycles_executed: "4/6"
   - "Zyklus 1-6 abgeschlossen" → cycles_executed: "6/6"

6. **Fehlende Werte**: null oder leere Arrays []

BEISPIELE:
- "AI-Schema: Adriamycin 75 mg/m² + Ifosfamide 9 g/m²"
  → drugs: [
      {drug_type: "Adriamycin (Doxorubicin)", dose: 75, dose_unit: "mg/m²"},
      {drug_type: "Ifosfamide", dose: 9, dose_unit: "mg/m²"}
    ]
"""

    prompt = f"{system_instructions}\n\nJSON-Spezifikation:\n{json_spec}\n\nSystemtherapie-Berichtstext:\n{text}"

    response = model.generate_content(prompt)
    raw = (response.text or "").strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).replace("JSON", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    return data


def classify_and_extract_from_text(text: str) -> Dict[str, Any]:
    """
    Kombiniert Klassifikation und Extraktion in einem Backend-Call.
    Intern: 1 schneller classify-Call + 1 extract-Call basierend auf Ergebnis.
    Spart dem Frontend einen separaten HTTP-Roundtrip.

    Returns:
        {"doc_type": str, "events": List[Dict]}
    """
    doc_type = classify_document_type(text)

    extractor_map = {
        "radiology": extract_radiology_events_from_text,
        "radiotherapy": extract_radiotherapy_events_from_text,
        "pathology": extract_pathology_events_from_text,
        "surgery": extract_surgery_events_from_text,
        "sarcoma_board": extract_sarcoma_board_events_from_text,
        "systemic_therapy": extract_systemic_therapy_events_from_text,
    }

    extractor = extractor_map.get(doc_type, extract_radiology_events_from_text)
    events = extractor(text)

    return {"doc_type": doc_type, "events": events}
