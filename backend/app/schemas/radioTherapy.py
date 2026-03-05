from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List
import re

from pydantic import BaseModel, Field, field_validator, model_validator


class RadiotherapyIndication(str, Enum):
    preoperative = "preoperative"
    postoperative = "postoperative"
    definitive = "definitive"
    palliative = "palliative"
    curative = "curative"


class RadiotherapyType(str, Enum):
    intensity_modulated_radiotherapy_imrt = "intensity_modulated_radiotherapy_imrt"
    lattice_lrt = "lattice_lrt"
    volumetric_arc_vmat = "volumetric_arc_vmat"
    conventional_3d = "conventional_3d"
    stereotactic_radiotherapy = "stereotactic_radiotherapy"
    proton_therapy = "proton_therapy"
    intraoperative_linac = "intraoperative_linac"
    intraoperative_brachytherapy = "intraoperative_brachytherapy"
    brachytherapy = "brachytherapy"
    sequential_boost = "sequential_boost"
    simultaneous_integrated_boost = "simultaneous_integrated_boost"


class HyperthermiaStatus(str, Enum):
    """
    WICHTIG: In der DB ist hyperthermia_status ein STRING!
    Constraint-Werte laut db/constraints/radio_therapy/hyperthermia_status.yml
    """
    no = "no"
    yes_radiation_hyperthermia = "yes_radiation_hyperthermia"


class RadiotherapyEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_radio_therapies Tabelle.
    WICHTIG: indications und therapy_types sind Arrays in der DB!
    """

    # IDs (in DB nicht nullable, aber hier optional für LLM-Extraktion)
    institution_id: Optional[int] = Field(default=None, ge=0, description="Institution ID")
    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")
    responsible_oncologist_id: Optional[int] = Field(
        default=None,
        ge=0,
        description="Verantwortlicher Radio-Onkologe"
    )

    # Termine (DB hat mehrere Datum-Felder!)
    referral_date: Optional[date] = Field(default=None, description="Überweisungsdatum")
    first_contact_date: Optional[date] = Field(default=None, description="Erstkontakt-Datum")
    therapy_start_date: Optional[date] = Field(default=None, description="Therapiebeginn")
    therapy_end_date: Optional[date] = Field(default=None, description="Therapieende")

    # Indikationen - ARRAY! (in DB: indications ARRAY)
    indications: List[str] = Field(
        default_factory=list,
        description="Indikationen (mehrere möglich, z.B. preoperative + postoperative)"
    )

    # Therapietypen - ARRAY! (in DB: therapy_types ARRAY, NOT NULL!)
    therapy_types: List[str] = Field(
        default_factory=list,
        description="Therapietypen (mehrere möglich, z.B. imrt + stereotactic)"
    )

    # Dosierung (DB-Feldnamen: total_dose_in_gy, given_fractions)
    total_dose_in_gy: Optional[float] = Field(
        default=None,
        ge=0,
        description="Gesamtdosis in Gray"
    )
    given_fractions: Optional[int] = Field(
        default=None,
        ge=0,
        description="Anzahl verabreichter Fraktionen"
    )

    # Volumina (DB-Feldnamen: ptv_volume_in_cm3, gtv_volume_in_cm3)
    ptv_volume_in_cm3: Optional[float] = Field(
        default=None,
        ge=0,
        description="Planned Target Volume in cm³"
    )
    gtv_volume_in_cm3: Optional[float] = Field(
        default=None,
        ge=0,
        description="Gross Tumor Volume in cm³"
    )

    # Tumor-Lokalisation (wichtig für Sarkom-Dokumentation!)
    was_tumor_located_in_radiated_area: Optional[bool] = Field(
        default=None,
        description="War der Tumor im bestrahlten Bereich lokalisiert?"
    )
    was_tumor_located_with_pre_existing_lymph_edema: Optional[bool] = Field(
        default=None,
        description="War der Tumor mit vorbestehendem Lymphödem assoziiert?"
    )

    # Hyperthermie
    hyperthermia_status: Optional[str] = None

    # Kommentare (DB-Feldname: comments, nicht remarks!)
    comments: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Kommentare zur Radiotherapie"
    )

    @staticmethod
    def _normalize_indication(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radio_therapy/indications.yml:
        preoperative, postoperative, definitive, palliative, curative
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None

        raw = value.strip()
        if not raw:
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"preoperative", "postoperative", "definitive", "palliative", "curative"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Old enum format: "[1] preoperative" → strip number prefix
        if "preoperative" in lower or "präoperativ" in lower or "neoadjuvant" in lower:
            return "preoperative"
        if "postoperative" in lower or "postoperativ" in lower or "adjuvant" in lower:
            return "postoperative"
        if "definitive" in lower or "definitiv" in lower:
            return "definitive"
        if "palliative" in lower or "palliativ" in lower:
            return "palliative"
        if "curative" in lower or "kurativ" in lower:
            return "curative"

        # No mapping → preserve raw text
        return raw

    @staticmethod
    def _normalize_therapy_type(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radio_therapy/therapy_types.yml:
        intensity_modulated_radiotherapy_imrt, lattice_lrt, volumetric_arc_vmat,
        conventional_3d, stereotactic_radiotherapy, proton_therapy,
        intraoperative_linac, intraoperative_brachytherapy, brachytherapy,
        sequential_boost, simultaneous_integrated_boost
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None

        raw = value.strip()
        if not raw:
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-/\.()]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {
            "intensity_modulated_radiotherapy_imrt", "lattice_lrt", "volumetric_arc_vmat",
            "conventional_3d", "stereotactic_radiotherapy", "proton_therapy",
            "intraoperative_linac", "intraoperative_brachytherapy", "brachytherapy",
            "sequential_boost", "simultaneous_integrated_boost",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Synonym-Mapping (old enum format + DE/EN free text)
        if "imrt" in lower or "intensity modulated" in lower or "intensitätsmoduliert" in lower:
            return "intensity_modulated_radiotherapy_imrt"
        if "lattice" in lower or "lrt" == lower.strip():
            return "lattice_lrt"
        if "vmat" in lower or "volumetric arc" in lower:
            return "volumetric_arc_vmat"
        if "intraoperative" in lower and ("linac" in lower or "linear" in lower):
            return "intraoperative_linac"
        if "intraoperative" in lower and "brachy" in lower:
            return "intraoperative_brachytherapy"
        if "brachy" in lower:
            return "brachytherapy"
        if "sequential" in lower or "sequenziell" in lower or "sequential boost" in lower:
            return "sequential_boost"
        if "simultaneous integrated" in lower or "simultane" in lower or "sib" in lower:
            return "simultaneous_integrated_boost"
        if "stereotactic" in lower or "stereotaktisch" in lower or "sbrt" in lower or "srs" in lower:
            return "stereotactic_radiotherapy"
        if "proton" in lower:
            return "proton_therapy"
        if "conventional" in lower or "konventionell" in lower or "3d" in lower:
            return "conventional_3d"

        # No mapping → preserve raw text
        return raw

    @staticmethod
    def _normalize_hyperthermia_status(value) -> Optional[str]:
        """
        Normalisiert Hyperthermie-Status auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radio_therapy/hyperthermia_status.yml:
        no, yes_radiation_hyperthermia
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None

        raw = value.strip()
        if not raw:
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"no", "yes_radiation_hyperthermia"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Old enum values + free text (DE/EN)
        if any(token in lower for token in ["yes_radiation", "yes radiation"]):
            return "yes_radiation_hyperthermia"
        if any(token in lower for token in ["hypertherm", "yes", "ja", "planned", "geplant", "ongoing", "completed", "durchgeführt"]):
            return "yes_radiation_hyperthermia"
        if any(token in lower for token in ["no", "none", "nein", "nicht", "kein"]):
            return "no"

        # No mapping → preserve raw text
        return raw

    @model_validator(mode="before")
    @classmethod
    def normalize_radiotherapy_fields(cls, data):
        if not isinstance(data, dict):
            return data

        # indications list → normalize each element
        raw_indications = data.get("indications") or []
        if isinstance(raw_indications, list):
            normalized = []
            for v in raw_indications:
                n = cls._normalize_indication(v)
                if n is not None:
                    normalized.append(n)
            data["indications"] = normalized

        # therapy_types list → normalize each element
        raw_types = data.get("therapy_types") or []
        if isinstance(raw_types, list):
            normalized = []
            for v in raw_types:
                n = cls._normalize_therapy_type(v)
                if n is not None:
                    normalized.append(n)
            data["therapy_types"] = normalized

        # hyperthermia_status
        hyp_raw = data.get("hyperthermia_status")
        hyp_normalized = cls._normalize_hyperthermia_status(hyp_raw)
        if hyp_normalized is not None:
            data["hyperthermia_status"] = hyp_normalized
        elif hyp_raw is None or (isinstance(hyp_raw, str) and not hyp_raw.strip()):
            data["hyperthermia_status"] = None

        return data

    @field_validator(
        "referral_date",
        "first_contact_date",
        "therapy_start_date",
        "therapy_end_date",
        mode="before"
    )
    @classmethod
    def parse_dates(cls, v):
        """
        Parst flexible Datumsformate (DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD)
        """
        if v is None or (isinstance(v, str) and not v.strip()):
            return None

        if isinstance(v, date):
            return v

        if isinstance(v, str):
            s = v.strip()
            # Entfernt Textanhänge wie " preoperative" aus dem Datumsstring
            s = s.split(' ')[0]
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        return None  # Unbekanntes Format → leer lassen statt Fehler


class RadiotherapyEvents(BaseModel):
    """
    Wrapper für mehrere Radiotherapie-Events, extrahiert aus einem Bericht.
    """
    events: List[RadiotherapyEvent]
