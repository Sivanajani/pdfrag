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
