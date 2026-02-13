from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class SystemicTherapyReason(str, Enum):
    neoadjuvant = "Neoadjuvant"
    adjuvant = "Adjuvant"
    palliative_first_line = "Palliative (first line)"
    palliative_further_line = "Palliative (further line)"
    curative = "Curative"
    maintenance = "Maintenance"
    other = "Other"


class TreatmentLine(int, Enum):
    first_line = 1
    second_line = 2
    third_line = 3
    fourth_line = 4
    fifth_line_or_more = 5


class BoneProtocol(str, Enum):
    map = "MAP (Methotrexate, Adriamycin, Cisplatin)"
    mapie = "MAPIE (MAP + Ifosfamide, Etoposide)"
    euramos = "EURAMOS"
    ie = "IE (Ifosfamide, Etoposide)"
    vai = "VAI (Vincristine, Adriamycin, Ifosfamide)"
    other = "Other"
    none = "None"


class SoftTissueProtocol(str, Enum):
    ai = "AI (Adriamycin, Ifosfamide)"
    maid = "MAID (Mesna, Adriamycin, Ifosfamide, Dacarbazine)"
    gemcitabine_docetaxel = "Gemcitabine/Docetaxel"
    trabectedin = "Trabectedin"
    pazopanib = "Pazopanib"
    eribulin = "Eribulin"
    ifosfamide_monotherapy = "Ifosfamide monotherapy"
    doxorubicin_monotherapy = "Doxorubicin monotherapy"
    other = "Other"
    none = "None"


class DiscontinuationReason(str, Enum):
    completion_of_planned_therapy = "Completion of planned therapy"
    progressive_disease = "Progressive disease"
    toxicity = "Toxicity"
    patient_refusal = "Patient refusal"
    death = "Death"
    surgery_planned = "Surgery planned"
    other = "Other"


class ClinicalTrialInclusion(str, Enum):
    yes = "Yes"
    no = "No"
    unknown = "Unknown"


class HyperthermiaStatus(str, Enum):
    none = "None"
    planned = "Planned"
    ongoing = "Ongoing"
    completed = "Completed"


class PatientType(str, Enum):
    pediatric = "Pediatric"
    adolescent_young_adult = "Adolescent/Young adult (AYA)"
    adult = "Adult"


class DrugType(str, Enum):
    # Chemotherapie
    adriamycin = "Adriamycin (Doxorubicin)"
    cisplatin = "Cisplatin"
    carboplatin = "Carboplatin"
    ifosfamide = "Ifosfamide"
    etoposide = "Etoposide"
    methotrexate = "Methotrexate"
    vincristine = "Vincristine"
    cyclophosphamide = "Cyclophosphamide"
    dacarbazine = "Dacarbazine"
    gemcitabine = "Gemcitabine"
    docetaxel = "Docetaxel"

    # Targeted Therapy
    pazopanib = "Pazopanib"
    trabectedin = "Trabectedin"
    eribulin = "Eribulin"
    imatinib = "Imatinib"

    # Supportive
    mesna = "Mesna"
    granulocyte_colony_stimulating_factor = "G-CSF"

    other = "Other"


class RouteOfAdministration(str, Enum):
    intravenous = "Intravenous (IV)"
    oral = "Oral (PO)"
    intramuscular = "Intramuscular (IM)"
    subcutaneous = "Subcutaneous (SC)"
    intrathecal = "Intrathecal (IT)"
    other = "Other"


class Drug(BaseModel):
    """
    Einzelnes Medikament innerhalb einer systemischen Therapie.
    Entspricht der croms_drugs Tabelle.
    """
    drug_type: Optional[DrugType] = None
    dose: Optional[float] = Field(default=None, ge=0, description="Dosis")
    dose_unit: Optional[str] = Field(default=None, max_length=50, description="z.B. mg, mg/m², mg/kg")
    frequency: Optional[float] = Field(default=None, ge=0, description="Häufigkeit")
    frequency_unit: Optional[str] = Field(default=None, max_length=50, description="z.B. daily, weekly, q3w")
    frequency_unit_comment: Optional[str] = Field(default=None, max_length=500)
    route: Optional[RouteOfAdministration] = None
    administration_day: Optional[str] = Field(default=None, max_length=50, description="z.B. Day 1, Day 1-5")


class AdverseEvent(BaseModel):
    """
    Unerwünschtes Ereignis während systemischer Therapie.
    Entspricht der croms_adverse_events Tabelle.
    """
    medical_area: Optional[str] = Field(default=None, max_length=200, description="Medizinischer Bereich (z.B. Hämatologie)")
    event_type: Optional[str] = Field(default=None, max_length=200, description="Art des Ereignisses (z.B. Neutropenie)")
    grade: Optional[str] = Field(default=None, max_length=10, description="CTCAE Grade (1-5)")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    comment: Optional[str] = Field(default=None, max_length=1000)


class SystemicTherapyEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_systemic_therapies Tabelle.
    Systemische Therapie = Chemotherapie, Targeted Therapy, Immuntherapie.
    """

    institution_id: Optional[int] = Field(default=None, ge=0, description="Institution ID")
    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")
    responsible_oncologist_id: Optional[int] = Field(default=None, ge=0, description="Verantwortlicher Onkologe")

    # Therapie-Grund und Linie
    reason: Optional[SystemicTherapyReason] = None
    reason_comment: Optional[str] = Field(default=None, max_length=1000)
    treatment_line: Optional[TreatmentLine] = None

    # Protokolle
    bone_protocol: Optional[BoneProtocol] = None
    bone_protocol_comment: Optional[str] = Field(default=None, max_length=1000)
    softtissue_protocol: Optional[SoftTissueProtocol] = None
    softtissue_protocol_comment: Optional[str] = Field(default=None, max_length=1000)

    # Zeitraum
    cycle_start_date: Optional[date] = None
    cycle_end_date: Optional[date] = None
    cycles_executed: Optional[str] = Field(default=None, max_length=50, description="z.B. '6/6' oder '4/6'")

    # Begleitende Therapie
    was_rct_concomittant: bool = Field(
        default=False,
        description="Gleichzeitige Radiochemotherapie"
    )
    hyperthermia_status: Optional[HyperthermiaStatus] = None

    # Studienteilnahme
    clinical_trial_inclusion: Optional[ClinicalTrialInclusion] = None

    # Abbruch
    discontinuation_reason: Optional[DiscontinuationReason] = None

    # Patient-Typ
    patient_type: Optional[PatientType] = None

    # Assessment
    assessment_date: Optional[date] = Field(
        default=None,
        description="Datum des Response-Assessments"
    )

    # Kommentare
    comments: Optional[str] = Field(default=None, max_length=2000)

    # Verknüpfte Daten
    drugs: List[Drug] = Field(
        default_factory=list,
        description="Liste der verwendeten Medikamente"
    )
    adverse_events: List[AdverseEvent] = Field(
        default_factory=list,
        description="Unerwünschte Ereignisse"
    )

    @field_validator("cycle_start_date", "cycle_end_date", "assessment_date", mode="before")
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
            s = s.split(' ')[0]  # Entfernt Textanhänge
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        return None  # Unbekanntes Format → leer lassen statt Fehler


class SystemicTherapyEvents(BaseModel):
    """
    Wrapper für mehrere systemische Therapie-Events, extrahiert aus einem Bericht.
    """
    events: List[SystemicTherapyEvent]
