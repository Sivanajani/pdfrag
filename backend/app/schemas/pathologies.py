from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class BiopsyType(str, Enum):
    incisional_biopsy = "Incisional biopsy"
    excisional_biopsy = "Excisional biopsy"
    core_needle_biopsy = "Core needle biopsy"
    fine_needle_aspiration = "Fine needle aspiration (FNA)"
    punch_biopsy = "Punch biopsy"
    resection_specimen = "Resection specimen"
    other = "Other"


class BiopsiedLesionType(str, Enum):
    primary_tumor = "Primary tumor"
    recurrent_tumor = "Recurrent tumor"
    metastasis = "Metastasis"
    lymph_node = "Lymph node"
    other = "Other"


class PriorTreatment(str, Enum):
    none = "None"
    chemotherapy = "Chemotherapy"
    radiotherapy = "Radiotherapy"
    surgery = "Surgery"
    combined = "Combined treatment"
    other = "Other"


class DiagnosticGrading(str, Enum):
    g1 = "G1 (well differentiated)"
    g2 = "G2 (moderately differentiated)"
    g3 = "G3 (poorly differentiated)"
    gx = "GX (cannot be assessed)"


class SurgicalMarginJudgment(str, Enum):
    r0 = "R0 (complete resection, negative margins)"
    r1 = "R1 (microscopic residual tumor)"
    r2 = "R2 (macroscopic residual tumor)"
    unknown = "Unknown"
    not_applicable = "Not applicable (biopsy only)"


class BiologicalBarrier(str, Enum):
    none = "None"
    fascia = "Fascia"
    periosteum = "Periosteum"
    adventitia = "Adventitia"
    capsule = "Capsule"
    other = "Other"


class TestPerformedStatus(str, Enum):
    not_performed = "Not performed"
    performed = "Performed"
    pending = "Pending"
    not_applicable = "Not applicable"


class EORTCResponseGrade(str, Enum):
    """
    EORTC Response Grade für Sarkom-Response nach neoadjuvanter Therapie.
    """
    grade_1 = "Grade 1 (no therapy effect)"
    grade_2 = "Grade 2 (< 50% necrosis)"
    grade_3 = "Grade 3 (50-90% necrosis)"
    grade_4 = "Grade 4 (> 90% necrosis)"
    not_applicable = "Not applicable"


class PathologyEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_pathologies Tabelle.
    Pathologie-Befund nach Biopsie oder Resektion.
    """

    institution_id: Optional[int] = Field(default=None, ge=0, description="Institution ID")
    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")
    responsible_pathologist_id: Optional[int] = Field(default=None, ge=0, description="Verantwortlicher Pathologe")

    # Biopsie/Resektions-Details
    biopsy_type: Optional[BiopsyType] = None
    biopsied_lesion_type: Optional[BiopsiedLesionType] = None
    biopsy_resection_date: Optional[date] = None

    # Befund-Daten
    registrate_date: Optional[date] = Field(default=None, description="Registrierungsdatum")
    first_report_date: Optional[date] = Field(default=None, description="Datum Erstbefund")
    final_report_date: Optional[date] = Field(default=None, description="Datum Endbefund")
    report_date: Optional[date] = Field(default=None, description="Befunddatum (allgemein)")

    # Vorbehandlung
    prior_treatment: Optional[PriorTreatment] = None

    # Diagnose nach WHO-Klassifikation
    who_diagnosis: Optional[str] = Field(
        default=None,
        max_length=500,
        description="WHO-Diagnose (z.B. 'High-grade myxofibrosarcoma')"
    )

    # Grading
    diagnostic_grading: Optional[DiagnosticGrading] = None

    # Chirurgischer Rand
    judgment_of_surgical_margin: Optional[SurgicalMarginJudgment] = None
    closest_distance_to_margin_mm: Optional[int] = Field(
        default=None,
        ge=0,
        description="Abstand zum nächsten Resektionsrand in mm"
    )
    biological_barrier_to_closest_margin: Optional[BiologicalBarrier] = None
    biological_barrier_to_closest_margin_comment: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    # Tumor-Charakteristika
    proliferation_index: Optional[str] = Field(
        default=None,
        max_length=50,
        description="z.B. 'Ki-67: 40%'"
    )
    mitoses_per_10hpf: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Mitosen pro 10 High-Power-Fields"
    )
    extent_of_necrosis: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Nekroseanteil (z.B. '<10%' oder '50-90%')"
    )

    # Response nach neoadjuvanter Therapie
    eortc_response_grade: Optional[EORTCResponseGrade] = None

    # Molekularpathologie
    ihc_performed_status: Optional[TestPerformedStatus] = Field(
        default=None,
        description="Immunhistochemie durchgeführt?"
    )
    ihc_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="IHC-Ergebnis"
    )

    fish_performed_status: Optional[TestPerformedStatus] = Field(
        default=None,
        description="FISH durchgeführt?"
    )
    fish_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="FISH-Ergebnis (z.B. MDM2-Amplifikation)"
    )

    rna_performed_status: Optional[TestPerformedStatus] = Field(
        default=None,
        description="RNA-Sequenzierung durchgeführt?"
    )
    rna_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="RNA-Sequenzierungs-Ergebnis (z.B. Fusionsgene)"
    )

    dna_performed_status: Optional[TestPerformedStatus] = Field(
        default=None,
        description="DNA-Sequenzierung durchgeführt?"
    )
    dna_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="DNA-Sequenzierungs-Ergebnis (z.B. Mutationen)"
    )

    # Vollständiger Befundtext
    report: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Vollständiger Pathologie-Befund"
    )

    @field_validator(
        "biopsy_resection_date",
        "registrate_date",
        "first_report_date",
        "final_report_date",
        "report_date",
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
            s = s.split(' ')[0]  # Entfernt Textanhänge
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        return None  # Unbekanntes Format → leer lassen statt Fehler


class PathologyEvents(BaseModel):
    """
    Wrapper für mehrere Pathologie-Events, extrahiert aus einem Bericht.
    """
    events: List[PathologyEvent]
