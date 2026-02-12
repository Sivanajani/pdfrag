from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class RadiotherapyIndication(str, Enum):
    preoperative = "[1] preoperative"
    postoperative = "[2] postoperative"
    definitive = "[3] definitive"
    palliative = "[4] palliative"
    other_unknown = "[8] other/ unknown"


class RadiotherapyType(str, Enum):
    imrt = "[1] Intensity modulated radiotherapy (IMRT)"
    vmat = "[2] volumetric arc VMAT"
    conv_3d = "[3] conventional 3D"
    stereotactic = "[4] stereotactic radiotherapy"
    proton = "[5] proton therapy"
    linac = "[6] intraoperative (Linac)"
    brachytherapy = "[7] intraoperative brachytherapy"
    other = "[8] other"


class HyperthermiaStatus(str, Enum):
    """
    WICHTIG: In der DB ist hyperthermia_status ein STRING, nicht INT!
    """
    none = "None"
    planned = "Planned"
    ongoing = "Ongoing"
    completed = "Completed"
    no = "No"
    yes = "Yes"


class RadiotherapyEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_radio_therapies Tabelle.
    WICHTIG: Viele Felder sind Arrays in der DB!
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
    indications: List[RadiotherapyIndication] = Field(
        default_factory=list,
        description="Indikationen (mehrere möglich, z.B. preoperative + postoperative)"
    )

    # Therapietypen - ARRAY! (in DB: therapy_types ARRAY, NOT NULL!)
    therapy_types: List[RadiotherapyType] = Field(
        default_factory=list,
        description="Therapietypen (mehrere möglich, z.B. IMRT + stereotactic)"
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
    hyperthermia_status: Optional[HyperthermiaStatus] = None

    # Kommentare (DB-Feldname: comments, nicht remarks!)
    comments: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Kommentare zur Radiotherapie"
    )

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

        raise ValueError(f"Invalid date format: {v}")


class RadiotherapyEvents(BaseModel):
    """
    Wrapper für mehrere Radiotherapie-Events, extrahiert aus einem Bericht.
    """
    events: List[RadiotherapyEvent]
